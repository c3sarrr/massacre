// Viewmodel parado (Fase 4.1; docs/phases/phase-4.md, seção 4.1, "Viewmodel parado"): a arma na mão em primeira pessoa
// numa camada própria do pipeline (postPipeline.addLayer) — cena com a arma e os dois braços de massinha, câmera que
// copia a do jogador com o FOV do viewmodel (viewmodel_fov) e a luz do mapa copiada (viewmodelLights.js). A arma fica na
// posição da categoria (src/data/viewmodel.js) mais os offsets; cada mão vai para a âncora da receita com a pose da
// âncora e o antebraço aponta para um cotovelo fixo fora da tela. Na 4.1 não anima: segura parado, com o boil "em
// dois" da massinha. Quem decide o que segurar e quando aparece é o MatchState (placement.js: viewmodelVisible).

import * as THREE from 'three';
import { EV, Subscriptions } from '../../core/events.js';
import { VIEWMODEL } from '../../data/viewmodel.js';
import { PALETTE } from '../../data/palette.js';
import { HAND } from '../../data/hands.js';
import { armbandColor } from '../../characters/hands/armband.js';
import { ViewmodelLights } from './viewmodelLights.js';
import {
  HAND_ANCHOR, anchorPose, categoryPlacement, elbowTarget, viewCategory, viewFaction, viewPlacement, viewmodelVerticalFov,
  weaponNudge,
} from './placement.js';

const SIDES = Object.freeze(['direita', 'esquerda']);
// Alcance da mão a partir do pulso (palma + dedos esticados): a esfera da sombra própria cobre a mão inteira.
const HAND_REACH = HAND.palm.center[0] + HAND.palm.half[0] + HAND.fingers[1].phalanges.reduce((a, b) => a + b, 0);

export class Viewmodel {
  /**
   * @param {object} deps
   * @param {import('../../render/renderSystem.js').RenderSystem} deps.render
   * @param {import('../model/weaponLibrary.js').WeaponLibrary} deps.weapons
   * @param {import('../../characters/hands/handLibrary.js').HandLibrary} deps.hands
   * @param {import('../../core/config.js').Config} deps.config
   * @param {import('../../core/events.js').EventBus} deps.events
   * @param {object|null} [deps.log]
   * @param {string} [deps.armColor] massa dos braços (a do boneco; terracota no de referência)
   */
  constructor({ render, weapons, hands, config, events, log = null, armColor = PALETTE.terracotta }) {
    this.render = render;
    this.weapons = weapons;
    this.hands = hands;
    this.config = config;
    this.log = log;
    this.armColor = armColor;
    this.scene = new THREE.Scene();
    this.scene.name = 'viewmodel';
    this.camera = new THREE.PerspectiveCamera(viewmodelVerticalFov(VIEWMODEL.fov.default), 16 / 9, VIEWMODEL.near, VIEWMODEL.far);
    this.camera.name = 'viewmodel';
    // `root` segue a câmera do jogador (o referencial da câmera); `holder` é a arma na posição da categoria.
    this.root = new THREE.Group();
    this.root.name = 'viewmodel:camera';
    this.holder = new THREE.Group();
    this.holder.name = 'viewmodel:arma';
    this.root.add(this.holder);
    this.scene.add(this.root);
    this.lights = new ViewmodelLights(this.scene);
    this.layer = {
      scene: this.scene, camera: this.camera, visible: false,
      beforeRender: (r) => this.#beforeRender(r), afterRender: (r) => this.#afterRender(r),
    };
    this.removeLayer = render.pipeline.addLayer(this.layer);
    this._shadowForced = false;
    this._shadowPending = false;

    this.arms = { direita: null, esquerda: null };
    this.armsReady = null;
    this.weapon = null; // instância na mão
    this.recipe = null;
    this.itemKey = null; // `${id}:${lod}:${facção}` pedido
    this.loadedKey = null; // o que está na mão
    this.request = { id: null, lod: null, faction: null, fresh: false }; // o último pedido (evita refazer a chave por quadro)
    this.token = 0;
    this.category = null;
    this.center = new THREE.Vector3(); // centro da arma no referencial dela
    this.radius = 10;
    this.dirty = true;
    this.tune = {}; // ajustes ao vivo por categoria (viewmodel_ajuste)
    this.anchorTune = {}; // ajustes ao vivo das âncoras das mãos por arma: {id: {maoDireita: {pos, rot}}}
    this.team = null;
    this.placement = { position: new THREE.Vector3(), quaternion: new THREE.Quaternion() };
    this._pose = { position: new THREE.Vector3(), quaternion: new THREE.Quaternion() };
    this._elbow = new THREE.Vector3();
    this.localPoints = []; // pontos da oclusão no referencial da câmera
    this.worldPoints = [];
    this.localSphere = new THREE.Sphere();
    this.worldSphere = new THREE.Sphere();

    this.subs = new Subscriptions();
    this.subs.add(config.watch('viewmodel.', () => {
      this.dirty = true;
    }));
    this.subs.add(config.watch('debug.armband', () => this.#applyTeam()));
    // Receita relida do disco (Blender): a instância antiga sai agora, antes de a biblioteca descartar as malhas.
    this.subs.on(events, EV.WEAPON_MODEL, ({ id, phase }) => {
      if (phase === 'relendo' && this.recipe?.id === id) this.#drop();
      if (id === this.itemKey?.split(':')[0]) this.#invalidate();
    });
    this.#applyTeam();
  }

  /** Liga à cena do mapa (as luzes copiadas) e ao mundo de colisão (o que tapa a luz; null na bancada). */
  attach(mapScene, world = null) {
    this.lights.attach(mapScene, world);
  }

  /** Time da braçadeira (cl_bracadeira; nas partidas de time, o do jogador): cor da faixa e acento das armas dos dois lados. */
  #applyTeam() {
    const v = this.config.get('debug.armband');
    this.team = v === 'tr' || v === 'ct' ? v : null;
    const color = armbandColor(this.team, this.armColor);
    for (const side of SIDES) this.arms[side]?.setArmband(color);
    this.#invalidate(); // o acento das armas dos dois lados muda com o time
  }

  /** Esquece o pedido: o próximo quadro pede a arma de novo (receita relida, time trocado). */
  #invalidate() {
    this.itemKey = null;
    this.request.fresh = false;
  }

  /** Cria os dois braços uma vez (a malha da mão sai da HandLibrary, gerada uma vez por sessão). */
  #ensureArms() {
    if (!this.armsReady) {
      this.armsReady = Promise.all(SIDES.map((side) => this.hands.createArm(side, { color: this.armColor }))).then((arms) => {
        if (this.disposed) {
          for (const a of arms) a.dispose();
          throw new Error('viewmodel descartado');
        }
        const color = armbandColor(this.team, this.armColor);
        SIDES.forEach((side, i) => {
          const arm = arms[i];
          arm.mesh.visible = false;
          arm.setArmband(color);
          this.root.add(arm.mesh);
          this.arms[side] = arm;
        });
        this.dirty = true;
      });
      this.armsReady.catch((err) => {
        if (!this.disposed) this.log?.error('viewmodel: braços', err);
      });
    }
    return this.armsReady;
  }

  /**
   * Pede o item na mão (id de arma com receita, ou null). `faction` força o acento (a bancada); sem ela, as armas dos
   * dois lados pegam o time da braçadeira.
   * @param {string|null} id @param {{lod?:string, faction?:string|null}} [options]
   */
  #want(id, { lod = 'perto', faction = null } = {}) {
    const r = this.request;
    if (r.fresh && r.id === id && r.lod === lod && r.faction === faction) return;
    r.id = id;
    r.lod = lod;
    r.faction = faction;
    r.fresh = true;
    const has = id && this.weapons.has(id) && viewCategory(id);
    const key = has ? `${id}:${lod}:${faction ?? viewFaction(id, this.team)}` : null;
    if (key === this.itemKey) return;
    this.itemKey = key;
    const token = ++this.token;
    if (!key) {
      this.#drop();
      return;
    }
    const [wid, wlod, wfaction] = key.split(':');
    Promise.all([this.weapons.instance(wid, { lod: wlod, faction: wfaction }), this.#ensureArms()]).then(([instance]) => {
      if (this.disposed || token !== this.token) return;
      this.#swap(instance, key);
    }).catch((err) => {
      if (!this.disposed && token === this.token) this.log?.error(`viewmodel: ${wid}`, err);
    });
  }

  /** Troca a arma da mão pela instância nova: centro e raio, poses das mãos pela âncora, posição a refazer. */
  #swap(instance, key) {
    this.#drop();
    const info = instance.userData.weapon;
    this.weapon = instance;
    this.recipe = this.weapons.recipe(info.id);
    this.loadedKey = key;
    this.category = viewCategory(info.id);
    instance.updateMatrixWorld(true);
    new THREE.Box3().setFromObject(instance).getCenter(this.center);
    this.radius = info.radius;
    this.holder.add(instance);
    for (const side of SIDES) {
      const anchor = this.#anchor(HAND_ANCHOR[side]);
      if (anchor) this.arms[side]?.setPose(anchor.pose ?? 'aberta');
    }
    this.dirty = true;
  }

  /** Âncora da receita na mão, com o ajuste ao vivo por cima (viewmodel_ajuste mao). */
  #anchor(name) {
    const base = this.recipe?.anchors[name];
    const tuned = this.anchorTune[this.recipe?.id]?.[name];
    return base && tuned ? { ...base, ...tuned } : base;
  }

  /** Tira a arma da mão (a instância só aponta para malhas e materiais da biblioteca: basta sair da cena). */
  #drop() {
    this.weapon?.removeFromParent();
    this.weapon = null;
    this.recipe = null;
    this.loadedKey = null;
    this.category = null;
    for (const side of SIDES) if (this.arms[side]) this.arms[side].mesh.visible = false;
  }

  /** Arma e mãos no referencial da câmera: a posição da categoria + offsets, os pulsos nas âncoras, os cotovelos. */
  #place() {
    const cat = this.category;
    const cfg = this.config;
    const offset = { x: cfg.get('viewmodel.offsetX'), y: cfg.get('viewmodel.offsetY'), z: cfg.get('viewmodel.offsetZ') };
    const pl = viewPlacement(cat, { offset, tune: this.tune[cat] ?? null, nudge: weaponNudge(this.recipe.id) }, this.placement);
    this.holder.position.copy(pl.position);
    this.holder.quaternion.copy(pl.quaternion);
    // Pontos da oclusão (centro, boca, pulsos) e a esfera da sombra própria, no referencial da câmera.
    const pts = [];
    const center = this.center.clone().applyQuaternion(pl.quaternion).add(pl.position);
    let radius = this.radius;
    for (const name of VIEWMODEL.light.occlusion.points) {
      if (name === 'centro') {
        pts.push(center.clone());
        continue;
      }
      const anchor = this.#anchor(name);
      if (anchor) pts.push(anchorPose(pl, anchor, this._pose).position.clone());
    }
    for (const side of SIDES) {
      const arm = this.arms[side];
      const anchor = this.#anchor(HAND_ANCHOR[side]);
      if (!arm) continue;
      arm.mesh.visible = Boolean(anchor);
      if (!anchor) continue;
      const pose = anchorPose(pl, anchor, this._pose);
      arm.place(pose.position, pose.quaternion, elbowTarget(cat, side, this.tune[cat] ?? null, this._elbow));
      radius = Math.max(radius, pose.position.distanceTo(center) + HAND_REACH);
    }
    this.localPoints = pts;
    while (this.worldPoints.length < pts.length) this.worldPoints.push(new THREE.Vector3());
    this.worldPoints.length = pts.length;
    this.localSphere.set(center, radius + VIEWMODEL.light.selfShadow.padding);
    this.dirty = false;
  }

  /**
   * Um quadro. `item`: o que a mão segura (id, ou null); `visible`: a regra de quando aparece (placement.js) já
   * avaliada por quem chama; `faction`/`lod` forçam o acento e o nível (a bancada).
   * @param {THREE.PerspectiveCamera} camera câmera do jogador (já posta neste quadro)
   * @param {number} dt
   * @param {{item:string|null, visible:boolean, faction?:string|null, lod?:string}} state
   */
  frame(camera, dt, { item, visible, faction = null, lod = 'perto' }) {
    this.#want(item, { lod, faction });
    const show = Boolean(visible && this.weapon && this.arms.direita && this.loadedKey === this.itemKey);
    this.layer.visible = show;
    if (!show) return;
    // Câmera e raiz: a do jogador (posição, olhar e rolagem), com o FOV do viewmodel.
    camera.updateMatrixWorld();
    const cam = this.camera;
    camera.matrixWorld.decompose(cam.position, cam.quaternion, cam.scale);
    const fov = viewmodelVerticalFov(this.config.get('viewmodel.fov'));
    if (cam.fov !== fov || cam.aspect !== camera.aspect) {
      cam.fov = fov;
      cam.aspect = camera.aspect;
      cam.updateProjectionMatrix();
    }
    this.root.position.copy(cam.position);
    this.root.quaternion.copy(cam.quaternion);
    if (this.dirty) this.#place();
    this.root.updateMatrixWorld(true);
    const m = this.root.matrixWorld;
    for (let i = 0; i < this.localPoints.length; i++) this.worldPoints[i].copy(this.localPoints[i]).applyMatrix4(m);
    this.worldSphere.copy(this.localSphere).applyMatrix4(m);
    const renderer = this.render.renderer;
    this.lights.update({
      points: this.worldPoints, sphere: this.worldSphere, level: this.render.shadowLevel, shadows: renderer.shadowMap.enabled, dt,
    });
  }

  // Sombra própria com o mapa em sombras estáticas (shadowMap.autoUpdate desligado): a camada pede o passe de sombra só
  // para ela e devolve o pedido pendente do mapa como estava.
  #beforeRender(r) {
    if (!this.lights.casting) return;
    this._shadowPending = r.shadowMap.needsUpdate;
    r.shadowMap.needsUpdate = true;
    this._shadowForced = true;
  }

  #afterRender(r) {
    if (!this._shadowForced) return;
    r.shadowMap.needsUpdate = this._shadowPending;
    this._shadowForced = false;
  }

  /** Ajuste ao vivo da posição de uma categoria (viewmodel_ajuste): `pos`, `angles` ou `elbows.{lado}`. */
  setTune(category, patch) {
    if (!VIEWMODEL.categories[category]) throw new Error(`categoria desconhecida: ${category}`);
    const cur = this.tune[category] ?? {};
    this.tune[category] = { ...cur, ...patch, elbows: { ...(cur.elbows ?? {}), ...(patch.elbows ?? {}) } };
    this.dirty = true;
  }

  clearTune(category = null) {
    if (category) delete this.tune[category];
    else this.tune = {};
    this.anchorTune = {};
    this.dirty = true;
  }

  /** Ajuste ao vivo da âncora de uma mão da arma na mão ({pos, rot}); devolve a linha para a receita. */
  setAnchorTune(side, patch) {
    if (!this.recipe) throw new Error('nenhuma arma na mão');
    const name = HAND_ANCHOR[side];
    if (!this.recipe.anchors[name]) throw new Error(`${this.recipe.id} não tem ${name}`);
    const byWeapon = (this.anchorTune[this.recipe.id] ??= {});
    byWeapon[name] = { ...(byWeapon[name] ?? {}), ...patch };
    this.dirty = true;
    return this.anchorLine(side);
  }

  /** A linha da âncora de uma mão no formato da receita (src/data/armas/<id>.js). */
  anchorLine(side) {
    const name = HAND_ANCHOR[side];
    const a = this.#anchor(name);
    if (!a) return `${this.recipe?.id ?? '—'}: sem ${name}`;
    const r = (v) => Number(v.toFixed(4));
    return `"${name}": { "pos": [${a.pos.map(r).join(', ')}], "rot": [${(a.rot ?? [0, 0, 0]).map(r).join(', ')}], "pose": "${a.pose}" },`;
  }

  /** A linha de src/data/viewmodel.js com o ajuste atual de uma categoria (para colar nos dados). */
  tuneLine(category) {
    const p = categoryPlacement(category, this.tune[category] ?? null);
    const f = (a) => `F([${a.map((v) => Number(v.toFixed(2))).join(', ')}])`;
    return `${category}: F({ pos: ${f(p.pos)}, angles: ${f(p.angles)}, elbows: F({ direita: ${f(p.elbows.direita)}, esquerda: ${f(p.elbows.esquerda)} }) }),`;
  }

  /** Estado para o console e os testes. */
  status() {
    return {
      item: this.loadedKey?.split(':')[0] ?? null, wanted: this.itemKey, category: this.category, visible: this.layer.visible,
      team: this.team, arms: SIDES.filter((s) => this.arms[s]?.mesh.visible),
    };
  }

  dispose() {
    this.disposed = true;
    this.token++;
    this.subs.dispose();
    this.removeLayer();
    this.#drop();
    for (const side of SIDES) {
      this.arms[side]?.dispose();
      this.arms[side] = null;
    }
    this.lights.dispose();
    this.scene.clear();
  }
}
