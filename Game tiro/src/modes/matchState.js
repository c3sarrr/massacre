// Estado "partida". Até os modos de jogo (Fase 8) roda o modo "livre" no mapa escolhido: em mapa com colisão o jogador
// anda com a cápsula (PlayerPawn, Fase 3) e o inventário local; sem colisão (vitrine) voa com a câmera livre.
// Responsável por: montar/desmontar o mapa (sem vazar GPU), jogador e câmera, contexto de entrada, pointer lock, pausa,
// a vida no HUD de teste, a morte e a volta em 2 s (subfase 3.4: no ponto de volta — o último teleporte do console que
// se sustentou, senão o spawn —; cair do set mata, com god volta ao spawn), sensibilidade da luneta, trincos do andar,
// ferramentas de debug da física e do movimento (medidores de counter-strafe e de salto e queda), o teleporte das
// estações (`estacao`, pista de testes), as escalas da sensação da câmera (subfase 3.5, seção "Conforto"), o corpo do
// jogador (o boneco de referência com squash & stretch, visível em terceira pessoa e no noclip), as pegadas nas peças
// de massinha que o mapa declara (`printSurfaces`), o monitor do movimento do aceite da Fase 3 (cl_monitor), a arma na
// mão em primeira pessoa (viewmodel, Fase 4.1; o "Segurar" da bancada de armas estaciona a câmera livre) e o resumo que
// vai para a tela de resultado.

import { EV, Subscriptions } from '../core/events.js';
import { SANDBOX } from '../data/sandbox.js';
import { VITALS } from '../data/vitals.js';
import { getMapDef } from '../maps/index.js';
import { ReturnPoint } from './returnPoint.js';
import { createFpsCamera } from '../render/camera.js';
import { disposeObject3D } from '../render/dispose.js';
import { capturarReflexo, pontoDoReflexo } from '../render/setReflection.js';
import { REFLEXO } from '../data/armasReais.js';
import { FreeCamera } from '../player/freeCamera.js';
import { PlayerPawn } from '../player/playerPawn.js';
import { PlayerBody } from '../characters/playerBody.js';
import { PrintSystem } from '../clay/prints/printSystem.js';
import { Viewmodel } from '../weapons/viewmodel/viewmodel.js';
import { viewmodelVisible } from '../weapons/viewmodel/placement.js';
import { itemName, zoomLevels } from '../player/hands.js';
import { readyToRespawn } from '../player/vitals.js';
import { PhysicsDebugView } from '../debug/physicsDebug.js';
import { ShowPosPanel } from '../debug/showPos.js';
import { StrafeMeter } from '../debug/strafeMeter.js';
import { JumpMeter } from '../debug/jumpMeter.js';
import { MoveMonitor } from '../debug/moveMonitor.js';
import { CONTEXT } from '../input/inputManager.js';
import { createSandboxHud } from '../ui/sandboxHud.js';
import { createPauseMenu } from '../ui/pauseMenu.js';
import { openSettings } from '../ui/settingsScreen.js';
import { h } from '../ui/dom.js';

export class MatchState {
  constructor(services) {
    this.s = services;
    this.subs = null;
    this.map = null;
    this.camera = null;
    this.player = null;
    this.body = null; // corpo do jogador (subfase 3.5)
    this.prints = null; // pegadas na massinha (subfase 3.5), nos mapas com `printSurfaces`
    this.viewmodel = null; // arma na mão em primeira pessoa (Fase 4.1)
    this.reflection = null; // reflexo do set das armas realistas (Fase 4.1a): o render target do PMREM
    this.hold = null; // "Segurar" da bancada de armas: {id, faction, lod} (câmera livre estacionada)
    this._vm = { item: null, visible: false, faction: null, lod: 'perto', gloves: null }; // pedido do viewmodel neste quadro
    this.physicsDebug = null;
    this.showPos = null;
    this.strafe = null; // medidor de counter-strafe (cl_showpos)
    this.jump = null; // medidor de salto e queda (cl_showpos)
    this.monitor = null; // monitor do movimento (cl_monitor, aceite da Fase 3)
    this.hud = null;
    this.pause = null;
    this.paused = false;
    this.params = null;
    this.devices = new Set();
    this.startedAt = 0;
    this.pausedMs = 0;
    this.pauseStart = 0;
    this.returnPoint = new ReturnPoint(); // ponto de volta: o último teleporte do console neste mapa (senão o spawn)
    this._feel = { bob: 0, tilt: 0, dip: 0 }; // escalas da sensação da câmera do tick (0–1)
  }

  async enter(params = {}) {
    const s = this.s;
    this.params = { map: 'testroom', mode: 'livre', ...params };
    const def = getMapDef(this.params.map);
    if (!def) throw new Error(`mapa desconhecido: ${this.params.map}`);
    this.subs = new Subscriptions();

    const loading = h('div.loading', { role: 'status' }, h('span.tape-label', null, `Montando o set: ${def.label}…`));
    s.uiRoot.append(loading);
    try {
      this.map = await def.build({ render: s.render, config: s.config, rng: s.rng, services: s });
    } finally {
      loading.remove();
    }
    this.cursorMode = false;

    this.camera = createFpsCamera({ hfov: s.config.get('graphics.fov'), aspect: s.render.cssWidth / s.render.cssHeight });
    const sp = this.map.spawn;
    if (this.map.collision) {
      this.player = new PlayerPawn({
        world: this.map.collision, sv: s.sv, loadout: s.localLoadout, events: s.events,
        position: sp.position, yaw: sp.yaw, pitch: sp.pitch,
      });
      this.body = new PlayerBody({ scene: this.map.scene, world: this.map.collision });
      this.body.onPose(this.player);
      if (this.map.printSurfaces?.length) {
        this.prints = new PrintSystem({ render: s.render, events: s.events, surfaces: this.map.printSurfaces });
      }
      this.physicsDebug = new PhysicsDebugView({ scene: this.map.scene, world: this.map.collision });
      this.showPos = new ShowPosPanel(s.debugRoot);
      this.strafe = new StrafeMeter(s.loop.stepDt);
      this.jump = new JumpMeter(s.loop.stepDt);
      this.monitor = new MoveMonitor({
        root: s.debugRoot, world: this.map.collision, floorY: this.map.bounds.min.y, lots: this.map.lots,
        stations: this.map.stations,
      });
      this.#applyDebugView();
      this.subs.add(s.config.watch('debug.', () => this.#applyDebugView()));
    } else {
      this.player = new FreeCamera({
        position: sp.position, yaw: sp.yaw, pitch: sp.pitch, bounds: this.map.bounds, speedScale: this.map.move?.speedScale ?? 1,
      });
    }
    this.player.updateCamera(this.camera, 1);
    s.render.setView(this.map.scene, this.camera, { staticShadows: this.map.staticShadows ?? false });
    // Reflexo do set das armas realistas: fotografado com o mapa pronto e as sombras como no jogo.
    this.#captureReflection();
    // Arma na mão: camada própria com as luzes do mapa copiadas; o mundo de colisão tapa a luz. As mãos e as armas do
    // inventário começam a ser geradas já (a troca não espera).
    this.viewmodel = new Viewmodel({
      render: s.render, weapons: s.weaponModels, hands: s.handModels, luvas: s.luvasModels, config: s.config, events: s.events, log: s.log,
    });
    this.viewmodel.attach(this.map.scene, this.map.collision ?? null);
    // GPU reiniciada: o reflexo se perdeu com ela (o mapa reassa o ambiente dele antes: inscreveu-se na montagem).
    this.subs.on(s.events, EV.RENDER_CONTEXT, ({ lost }) => {
      if (!lost) this.#captureReflection();
    });
    s.handModels.geometries().catch((err) => s.log?.error('mãos de massinha:', err));
    s.luvasModels?.carregar().catch(() => {}); // o erro de carga das luvas já vai ao log pela fonte
    this.#preloadWeapons();
    // Contexto do pós (jogo, vitrine...) e exposição da montagem de luz do mapa.
    s.render.post?.configure(this.map.post ?? { context: 'jogo', exposure: 1 });

    if (!s.roster.humans.some((p) => p.local)) s.roster.addHuman({ name: 'Você', local: true });

    this.hud = createSandboxHud(s, {
      title: def.label, mode: this.map.collision ? 'andar' : 'voo', stations: Boolean(this.map.stations?.length),
    });
    this.pause = createPauseMenu(s, {
      onResume: () => this.resume(),
      onSettings: () => openSettings(s),
      onEnd: () => s.states.go('result', { summary: this.summary() }),
      onQuit: () => s.states.go('menu'),
    });
    // Agachar (Ctrl) + andar (W) = Ctrl+W, que fecha a aba. Durante a partida o navegador pergunta antes
    // de sair; em tela cheia no Chromium o Keyboard Lock (botão "Tela cheia" da pausa) evita até a pergunta.
    this.subs.listen(window, 'beforeunload', (e) => {
      e.preventDefault();
      e.returnValue = '';
    });
    this.subs.listen(this.hud.prompt, 'click', () => this.#lock());
    this.subs.listen(s.render.canvas, 'click', () => {
      if (this.cursorMode) {
        this.setCursorMode(false);
        return;
      }
      if (!this.paused && s.input.device === 'kbm' && !s.input.pointerLocked) this.#lock();
    });
    this.subs.on(s.events, EV.INPUT_POINTER_LOCK, ({ locked }) => {
      this.hud.setPromptVisible(!locked && !this.paused && !this.cursorMode && s.input.device === 'kbm');
      if (!locked && !this.paused && !this.cursorMode && s.input.device === 'kbm') this.openPause();
    });
    this.subs.on(s.events, EV.INPUT_ACTION, ({ action, phase }) => {
      if (action === 'pause' && phase === 'press' && !this.paused && s.focusNav.empty) this.openPause();
      // Mapas com painel interativo (vitrine): Tab solta o mouse para usar o painel, sem pausar.
      if (action === 'scoreboard' && phase === 'press' && this.map?.panel && !this.paused) this.setCursorMode(true);
    });
    this.subs.on(s.events, EV.INPUT_DEVICE, ({ device }) => {
      this.devices.add(device);
      this.hud.setPromptVisible(device === 'kbm' && !s.input.pointerLocked && !this.paused);
    });
    if (this.player instanceof PlayerPawn) {
      // Arma recebida (give, loja): troca automática se for melhor que a da mão.
      this.subs.on(s.events, EV.LOADOUT, ({ owner, received }) => {
        if (owner !== 'local') return;
        this.player?.onLoadout(received);
        this.#preloadWeapons();
      });
      // Corpo: forma, virada e botas mudam só na troca de pose (12/s), como a massinha animada "em dois"; as pegadas da
      // fila vão para a GPU no mesmo ritmo (junto com o boil).
      this.subs.on(s.events, EV.POSE, () => {
        this.body?.onPose(this.player);
        this.prints?.onPose();
      });
      this.subs.on(s.events, EV.PLAYER_WEAPON, () => this.#syncHeld());
      this.subs.on(s.events, EV.PLAYER_ZOOM, () => this.#syncHeld());
      this.#syncHeld();
      // Vida no HUD de teste: dano (pisca e mostra quanto saiu), morte (etiqueta com a causa) e volta.
      this.subs.on(s.events, EV.LOADOUT, () => this.#syncVitals());
      this.subs.on(s.events, EV.PLAYER_HURT, ({ damage }) => {
        this.#syncVitals();
        this.hud.flashDamage(damage);
      });
      this.subs.on(s.events, EV.PLAYER_DEATH, ({ cause }) => {
        this.returnPoint.failed(cause);
        this.#syncVitals();
      });
      this.subs.on(s.events, EV.PLAYER_SPAWN, () => {
        this.#syncVitals();
        this.hud.setDeath(null);
      });
      this.#syncVitals();
    }

    this.devices = new Set([s.input.device]);
    this.startedAt = performance.now();
    this.pausedMs = 0;
    this.paused = false;
    s.input.resetToggles();
    s.input.setContext(CONTEXT.GAME);
    s.events.emit(EV.MAP_LOADED, { id: this.map.id });
    if (s.input.device === 'kbm') {
      // O clique que abriu a partida ainda vale como gesto do usuário na maioria dos navegadores.
      const ok = await s.input.requestPointerLock();
      this.hud.setPromptVisible(!ok);
    }
  }

  /** r_colisao, cl_showpos, cl_monitor e terceira pessoa seguem as chaves de debug da config. */
  #applyDebugView() {
    const cfg = this.s.config;
    this.physicsDebug?.setVisible(cfg.get('debug.collision'));
    this.showPos?.setVisible(cfg.get('debug.showPos'));
    this.monitor?.setVisible(cfg.get('debug.monitor'));
    if (this.player instanceof PlayerPawn) this.player.thirdPerson = cfg.get('debug.thirdPerson');
  }

  /**
   * Fotografa o set para o reflexo das armas realistas (seção 5.4 do desenho) e entrega ao serviço de armas; o corpo do
   * jogador (visível em terceira pessoa e no noclip) fica fora da foto.
   */
  #captureReflection() {
    const s = this.s;
    const body = this.body;
    const was = body ? [body.root.visible, body.shadow.visible] : null;
    if (body) body.root.visible = body.shadow.visible = false;
    try {
      this.reflection?.dispose();
      this.reflection = capturarReflexo(s.render.renderer, this.map.scene, pontoDoReflexo(this.map));
      s.weaponModels.setEnvironment(this.reflection.texture, REFLEXO.intensidade);
      s.luvasModels?.setAmbiente(this.reflection.texture, REFLEXO.intensidade);
    } finally {
      if (body) [body.root.visible, body.shadow.visible] = was;
    }
  }

  /** Gera (sem esperar) as malhas "perto" das armas do inventário local que têm modelo. */
  #preloadWeapons() {
    const l = this.s.localLoadout;
    this.s.weaponModels.preload([l.primary, l.secondary, l.melee].filter(Boolean), 'perto');
  }

  /**
   * "Segurar" da bancada de armas (mapas sem colisão): a câmera livre para no ponto dado (o olhar continua) e o
   * viewmodel mostra a arma escolhida, com o acento, o nível e a facção das luvas da bancada; null solta. Devolve se está
   * segurando.
   * @param {{id:string, faction?:string|null, lod?:string, gloves?:string|null,
   *   camera?:{position:import('three').Vector3, yaw:number, pitch:number}}|null} spec
   */
  setHold(spec) {
    const p = this.player;
    if (!(p instanceof FreeCamera)) return false;
    const was = this.hold;
    this.hold = spec ? { id: spec.id, faction: spec.faction ?? null, lod: spec.lod ?? 'perto', gloves: spec.gloves ?? null } : null;
    p.parked = Boolean(this.hold);
    if (spec?.camera && !was) p.teleport(spec.camera.position, spec.camera.yaw, spec.camera.pitch);
    return Boolean(this.hold);
  }

  /** O que o viewmodel mostra neste quadro (placement.js decide quando aparece). */
  #viewmodelState() {
    const s = this.s;
    const vm = this._vm;
    const enabled = s.config.get('debug.viewmodel');
    const p = this.player;
    if (p instanceof PlayerPawn) {
      vm.item = p.hands.item;
      vm.faction = null;
      vm.lod = 'perto';
      vm.gloves = null;
      vm.visible = viewmodelVisible({
        enabled, firstPerson: !p.thirdPerson, alive: p.vitals.alive, noclip: s.cheats.noclip, zoomed: p.hands.zoom !== 0,
        item: vm.item, hasModel: (id) => s.weaponModels.has(id),
      });
    } else {
      vm.item = this.hold?.id ?? null;
      vm.faction = this.hold?.faction ?? null;
      vm.lod = this.hold?.lod ?? 'perto';
      vm.gloves = this.hold?.gloves ?? null;
      vm.visible = Boolean(enabled && this.hold);
    }
    return vm;
  }

  /** Etiqueta "na mão" do HUD de teste: item, velocidade no modo atual e nível da luneta. */
  #syncHeld() {
    const p = this.player;
    if (!(p instanceof PlayerPawn)) return;
    const levels = zoomLevels(p.hands.item);
    const zoom = levels ? ` · luneta ${p.hands.zoom}/${levels}` : '';
    this.hud.setHeld(`na mão: ${itemName(p.hands.item)} · ${p.held.speed} u/s${zoom}`);
  }

  /** Etiqueta de vida do HUD de teste: vida do jogador e colete do inventário. */
  #syncVitals() {
    const p = this.player;
    if (!(p instanceof PlayerPawn)) return;
    this.hud.setVitals(p.vitals.health, p.loadout.armor);
  }

  async #lock() {
    const ok = await this.s.input.requestPointerLock();
    if (ok) this.hud.setPromptVisible(false);
    return ok;
  }

  /**
   * Modo cursor (só em mapas com `panel`): o mouse fica livre para o painel do mapa e o jogo não pausa.
   * Sai com Esc/B (navegação por foco), pelo botão do painel ou clicando na cena.
   */
  setCursorMode(on) {
    const s = this.s;
    const panel = this.map?.panel;
    if (!panel || on === this.cursorMode || this.paused) return;
    this.cursorMode = on;
    if (on) {
      s.input.exitPointerLock();
      s.input.setContext(CONTEXT.UI);
      this.hud.setPromptVisible(false);
      panel.open();
      this._popCursorNav = s.focusNav.push(panel.root, { onBack: () => this.setCursorMode(false) });
    } else {
      this._popCursorNav?.();
      this._popCursorNav = null;
      panel.close();
      s.input.setContext(CONTEXT.GAME);
      if (s.input.device === 'kbm') this.#lock();
    }
  }

  openPause() {
    if (this.paused) return;
    this.paused = true;
    this.pauseStart = performance.now();
    // Pausa aberta pelo controle, pelo toque ou pelo Esc com Keyboard Lock: o cursor precisa voltar.
    this.s.input.exitPointerLock();
    this.s.input.setContext(CONTEXT.UI);
    this.hud.setPromptVisible(false);
    this.pause.show();
  }

  async resume() {
    if (!this.paused) return;
    const s = this.s;
    if (s.input.device === 'kbm') {
      // Sem pointer lock não há como mirar no PC: continua pausado até o navegador aceitar.
      const ok = await s.input.requestPointerLock();
      if (!ok) {
        s.toasts.show('Clique em "Continuar" de novo para capturar o mouse');
        return;
      }
    }
    this.paused = false;
    this.pausedMs += performance.now() - this.pauseStart;
    this.pause.hide();
    s.input.setContext(CONTEXT.GAME);
  }

  tick(dt, tickIndex) {
    if (this.paused || !this.player) return;
    // O olhar acumulado no quadro entra antes do tick: o comando do tick usa o yaw mais recente.
    this.player.applyLook(this.s.input.consumeLook());
    this.player.tick(dt, this.s.input, {
      noclip: this.s.cheats.noclip, tick: tickIndex, god: this.s.cheats.god,
      reduceMotion: this.s.config.get('accessibility.reduceMotion'), feel: this.#feelScales(),
    });
    if (this.player instanceof PlayerPawn) {
      this.body.tick(this.player, dt);
      this.prints?.tick(this.player, dt);
      this.monitor.tick(this.player, dt);
      this.returnPoint.update(this.player.vitals.alive, this.player.state.onGround);
      this.strafe.updateFrom(this.player.telemetry);
      this.jump.update(this.player.state, this.player.env.events);
      // Luneta: a sensibilidade do olhar do próximo quadro segue o nível de zoom deste tick.
      this.s.input.lookScale = this.player.lookScale(this.s.config.get('controls.zoomSensitivity'));
    }
    this.#checkFellOut();
    if (this.player instanceof PlayerPawn && readyToRespawn(this.player.vitals)) this.#respawn();
    this.map.tick?.(dt);
  }

  /** Escalas da sensação da câmera (0–1) pela seção "Conforto"; "Reduzir movimento" zera as três. */
  #feelScales() {
    const cfg = this.s.config;
    const off = cfg.get('accessibility.reduceMotion');
    const f = this._feel;
    f.bob = off ? 0 : cfg.get('accessibility.cameraBob') / 100;
    f.tilt = off ? 0 : cfg.get('accessibility.cameraTilt') / 100;
    f.dip = off ? 0 : cfg.get('accessibility.cameraDip') / 100;
    return f;
  }

  /**
   * Fora do set (noclip desligado lá fora, ou um buraco): bem abaixo do mapa o jogador morre ("Caiu do set"); com god,
   * volta ao spawn com o aviso. Nos dois casos, um ponto de volta em que ele ainda não tinha pisado sai (ReturnPoint).
   */
  #checkFellOut() {
    const p = this.player;
    if (!(p instanceof PlayerPawn) || p.state.origin.y > this.map.bounds.min.y - SANDBOX.fallOutDepth) return;
    if (!p.vitals.alive) return;
    if (!this.s.cheats.god) {
      p.kill('fora');
      return;
    }
    this.returnPoint.failed('fora');
    const sp = this.map.spawn;
    this.#place(sp.position, sp.yaw, sp.pitch);
    this.s.toasts.show('Caiu para fora do set: de volta ao spawn');
  }

  /** Volta ao jogo no ponto de volta (o último teleporte do console neste mapa que se sustentou, senão o spawn). */
  #respawn() {
    const point = this.returnPoint.pick(this.map.spawn);
    this.player.respawn(point.position, point.yaw, point.pitch);
    this.body?.reset();
    this.prints?.reset();
    this.returnPoint.placed();
    this.jump?.interrupt();
  }

  frame(alpha, dt) {
    if (!this.player) return;
    const look = this.s.input.consumeLook();
    if (!this.paused) this.player.applyLook(look);
    const a = this.paused ? 1 : alpha;
    this.player.updateCamera(this.camera, a);
    this.viewmodel?.frame(this.camera, dt, this.#viewmodelState());
    this.body?.update(this.player, a);
    this.physicsDebug?.update(this.player, a);
    this.showPos?.update(this.player, { strafe: this.strafe, jump: this.jump });
    if (!this.paused) this.monitor?.frame(dt, this.s.render, this.player);
    if (this.player instanceof PlayerPawn) {
      const v = this.player.vitals;
      this.hud.setWalking(v.alive && !this.s.cheats.noclip && this.s.input.isDown('walk'));
      this.hud.setDeath(v.alive ? null : v.cause, Math.max(0, VITALS.respawnDelay - v.deadTime));
    }
    this.map.frame?.(dt, this.camera);
  }

  summary() {
    const now = performance.now();
    const pausedNow = this.paused ? now - this.pauseStart : 0;
    return {
      map: this.params.map,
      mode: this.params.mode,
      durationS: (now - this.startedAt - this.pausedMs - pausedNow) / 1000,
      distance: this.player?.stats.distance ?? 0,
      topSpeed: this.player?.stats.topSpeed ?? 0,
      ticks: this.player?.stats.ticks ?? 0,
      devices: [...this.devices],
    };
  }

  async exit() {
    const s = this.s;
    s.input.exitPointerLock();
    s.input.setContext(CONTEXT.UI);
    s.input.resetToggles();
    s.input.lookScale = 1;
    this._popCursorNav?.();
    this._popCursorNav = null;
    this.cursorMode = false;
    this.subs?.dispose();
    this.pause?.dispose();
    this.hud?.dispose();
    this.body?.dispose();
    this.prints?.dispose();
    this.viewmodel?.dispose();
    s.weaponModels.setEnvironment(null);
    s.luvasModels?.setAmbiente(null);
    this.reflection?.dispose();
    this.reflection = null;
    this.physicsDebug?.dispose();
    this.showPos?.dispose();
    this.monitor?.dispose();
    s.render.clearView();
    s.render.post?.configure({ context: 'jogo', exposure: 1 });
    if (this.map) {
      const id = this.map.id;
      this.map.dispose?.();
      this.map.collision?.dispose();
      disposeObject3D(this.map.scene);
      // Materiais do set em cache eram deste mapa (a GPU já foi liberada acima): o próximo mapa cria os seus.
      s.set?.releaseMaterials();
      s.events.emit(EV.MAP_UNLOADED, { id });
    }
    this.map = null;
    this.player = null;
    this.body = null;
    this.prints = null;
    this.viewmodel = null;
    this.hold = null;
    this.physicsDebug = null;
    this.showPos = null;
    this.strafe = null;
    this.jump = null;
    this.monitor = null;
    this.camera = null;
    this.pause = null;
    this.hud = null;
    this.paused = false;
    this.returnPoint.clear();
  }

  /**
   * Teleporte do console (setpos, estacao): vira o ponto de volta depois de morrer neste mapa (morrer da prancha de
   * 1310 devolve à prancha); um ponto em que o mundo mata o jogador antes de ele pisar no chão (o vazio, o alto) sai
   * (ReturnPoint).
   */
  teleport(position, yaw = this.player?.yaw ?? 0, pitch = this.player?.pitch ?? 0) {
    this.returnPoint.set(position, yaw, pitch);
    this.#place(position, yaw, pitch);
  }

  /** Leva o jogador ao ponto: o voo em andamento não conta no medidor de salto. */
  #place(position, yaw, pitch) {
    this.player?.teleport(position, yaw, pitch);
    this.prints?.reset();
    this.jump?.interrupt();
  }
}
