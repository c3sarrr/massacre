// Bancada de armas do mapa `arsenal` (Fase 4.1; docs/phases/phase-4.md, seção 4.1, "Bancada de armas"; Fase 4.1a:
// docs/superpowers/specs/2026-09-26-armas-realistas-design.md): a mesa do animador com o quadro de hardboard perfurado
// no fundo (ferramentas de modelar penduradas e a planta a lápis de cada arma presa com fita), as armas deitadas no
// tapete em fileiras com a etiqueta de fita de cada uma e, na frente, a roda de modelar com a arma escolhida no suporte
// de arame. Referências no item 13 do moodboard (QGW, QPB, QTT, QWS, QBP). Serve as duas origens da biblioteca de
// armas: tudo o que depende da arma sai do `info(id)` (a caixa, as âncoras, a planta, o comprimento); a skin da arma
// realista é a do serviço (weaponModels.setSkin: a roda, a fileira e a mão trocam juntas), a da de massinha é a skin de
// massa da 4.1 (clone dos materiais, só na roda).

import * as THREE from 'three';
import { ARSENAL } from '../../data/arsenal.js';
import { WEAPONS } from '../../data/weapons.js';
import { RNG } from '../../core/rng.js';
import { buildAnimatorDesk } from '../animatorDesk.js';
import { sculptTool, tapeStrip, wireGeometry } from '../../clay/set/propGeometry.js';
import { bakeLabelAtlas } from '../../clay/set/labelAtlas.js';
import { tapeLabelMaterial } from '../../clay/set/paperMaterials.js';
import { weaponFaction } from '../../weapons/model/recipe.js';
import { placeReference, silhouetteIoU } from '../../weapons/model/silhouette.js';
import { FABRICA, skinPorNome } from '../../weapons/skins/skin.js';
import { buildBandingWheel, buildWireStand } from './turntable.js';
import { drawPlanSheet, planSheetMaterial } from './planSheets.js';

const DEG = Math.PI / 180;
const labelLength = (aspect, L) => Math.max(L.tapeWidth * 2.2, aspect * L.textHeight + L.margin * 2);

export class ArsenalBench {
  /**
   * @param {{set:import('../../clay/set/index.js').SetLibrary, weapons:import('../../weapons/model/weaponLibrary.js').WeaponLibrary,
   *          anisotropy?:number, log?:object, precompile?:((obj:THREE.Object3D)=>Promise<unknown>)|null}} deps
   *   `precompile` compila as variantes de shader de uma instância antes de ela entrar na cena (renderer.compileAsync)
   */
  constructor({ set, weapons, anisotropy = 8, log = null, precompile = null }) {
    this.set = set;
    this.weapons = weapons;
    this.anisotropy = anisotropy;
    this.log = log;
    this.precompile = precompile;
    this.root = new THREE.Group();
    this.root.name = 'arsenal';
    this.matTop = ARSENAL.desk.mat.thickness;
    this.displays = new Map(); // id → instância deitada na fileira
    this.textures = [];
    this.labelAtlas = null;
    this.wheel = null;
    this.stand = null;
    this.weapon = null; // instância na roda
    // `skin`: a skin de massa da de massinha (a da realista é a do serviço); `faction`: null na realista.
    this.state = { id: null, faction: null, lod: 'perto', skin: null, explode: 0, anchors: false, plan: false, spin: true };
    this.skinMaterials = [];
    this.overlay = null;
    this.onChange = null; // o painel escuta (troca de arma, carga pronta, skin)
    this.selecting = Promise.resolve();
  }

  /** Ids com modelo, na ordem das fileiras. */
  get ids() {
    return ARSENAL.rows.flatMap((r) => r.ids).filter((id) => this.weapons.has(id));
  }

  async build(scene) {
    const t0 = performance.now();
    scene.add(this.root);
    this.root.add(buildAnimatorDesk(this.set, ARSENAL.desk));
    const ids = this.ids;
    // O `info` de cada arma: a caixa, as âncoras, a planta e o comprimento (na realista, o .glb, a ficha e o relatório).
    await Promise.all(ids.map((id) => this.weapons.describe(id)));
    this.#buildPegboard();
    this.#buildPlans(ids);
    await this.#buildRows();
    const t = ARSENAL.turntable;
    this.wheel = buildBandingWheel(this.set, t);
    this.wheel.root.position.set(t.x, this.matTop, t.z);
    this.root.add(this.wheel.root);
    await this.select(ids[0] ?? null);
    this.log?.info(`bancada de armas montada: ${ids.length} armas em ${(performance.now() - t0).toFixed(0)} ms`);
    return this;
  }

  #buildPegboard() {
    const P = ARSENAL.pegboard;
    const nx = Math.floor(P.width / P.pitch);
    const ny = Math.floor(P.height / P.pitch);
    const material = this.set.pegboard({
      color: P.color, fiber: P.fiber, holeColor: P.holeColor, pitch: P.pitch, hole: P.hole,
      origin: [-(nx - 1) * P.pitch / 2, -(ny - 1) * P.pitch / 2],
    });
    const board = new THREE.Mesh(new THREE.BoxGeometry(P.width, P.height, P.thickness), material);
    board.name = 'quadro-de-ferramentas';
    board.position.set(0, this.matTop + P.height / 2 + 6, P.z);
    board.castShadow = true;
    board.receiveShadow = true;
    this.root.add(board);
    this.board = board;
    // Dois pés de ripa atrás segurando o quadro em pé.
    const foot = new THREE.BoxGeometry(22, P.foot.height, P.foot.depth);
    for (const sx of [-1, 1]) {
      const f = new THREE.Mesh(foot, this.set.balsa());
      f.position.set(sx * (P.width / 2 - 60), this.matTop + P.foot.height / 2, P.z - P.thickness / 2 - P.foot.depth / 2);
      f.castShadow = true;
      f.receiveShadow = true;
      f.name = 'pe-do-quadro';
      this.root.add(f);
    }
    // Ferramentas de modelar penduradas, cada uma num gancho de arame.
    const wood = this.set.benchWood();
    const face = P.z + P.thickness / 2;
    for (const tdef of ARSENAL.tools) {
      const tool = sculptTool(tdef.kind, { length: tdef.length });
      const g = new THREE.Group();
      g.name = `ferramenta-${tdef.kind}`;
      g.add(new THREE.Mesh(tool.handle, wood), new THREE.Mesh(tool.metal, this.set.toolMetal({ length: tdef.length })));
      g.rotation.z = -tdef.rotDeg * DEG;
      const x = -P.width / 2 + tdef.at[0];
      const y = this.matTop + 6 + tdef.at[1];
      g.position.set(x, y + tdef.length / 2 - 18, face + 5);
      const hook = new THREE.CatmullRomCurve3([
        new THREE.Vector3(x, y + tdef.length / 2 - 4, face - 1), new THREE.Vector3(x, y + tdef.length / 2 - 4, face + 8),
        new THREE.Vector3(x, y + tdef.length / 2 + 2, face + 11),
      ]);
      const hookMesh = new THREE.Mesh(wireGeometry(hook, 0.9), this.set.wire());
      hookMesh.name = 'gancho';
      for (const m of [...g.children, hookMesh]) {
        m.castShadow = true;
        m.receiveShadow = true;
      }
      this.root.add(g, hookMesh);
    }
  }

  #buildPlans(ids) {
    const D = ARSENAL.plans;
    const P = ARSENAL.pegboard;
    const face = P.z + P.thickness / 2 + 0.35;
    const tape = this.set.tape({ width: 19 });
    const rng = new RNG('plantas-arsenal');
    ids.forEach((id, i) => {
      const info = this.weapons.info(id);
      const col = i % D.cols;
      const row = Math.floor(i / D.cols);
      const inRow = Math.min(D.cols, ids.length - row * D.cols);
      const canvas = drawPlanSheet({
        id, info, name: WEAPONS[id]?.name ?? id, plan: info.plan, lengthU: info.lengthU,
      }, D, ARSENAL.label.font);
      const texture = new THREE.CanvasTexture(canvas);
      texture.colorSpace = THREE.SRGBColorSpace;
      texture.anisotropy = this.anisotropy;
      this.textures.push(texture);
      const material = this.set.adopt(`planta-${id}`, planSheetMaterial(this.set.textures, texture, `planta-${id}`));
      const sheet = new THREE.Mesh(new THREE.PlaneGeometry(D.width, D.height), material);
      sheet.name = `planta-${id}`;
      const x = (col - (inRow - 1) / 2) * (D.width + D.gapX);
      const y = this.matTop + 6 + D.top - row * (D.height + D.gapY);
      sheet.position.set(x, y, face);
      sheet.rotation.z = rng.float(-1.6, 1.6) * DEG;
      sheet.receiveShadow = true;
      this.root.add(sheet);
      // Duas tiras de fita nos cantos de cima, tortas.
      for (const sx of [-1, 1]) {
        const strip = new THREE.Mesh(tapeStrip(D.tapeLength, 19, { seed: `planta-${id}-${sx}` }), tape);
        strip.rotation.set(0, 0, (sx * 38 + rng.float(-8, 8)) * DEG);
        strip.position.set(sx * (D.width / 2 - 6), D.height / 2 - 6, 0.25);
        strip.receiveShadow = true;
        sheet.add(strip);
      }
    });
  }

  async #buildRows() {
    const L = ARSENAL.label;
    const texts = [];
    for (const row of ARSENAL.rows) {
      texts.push(row.label);
      for (const id of row.ids) if (this.weapons.has(id)) texts.push(WEAPONS[id]?.name ?? id);
    }
    this.labelAtlas = bakeLabelAtlas(texts, {
      width: L.atlas.width, cellHeight: L.atlas.cellHeight, columns: L.atlas.columns, font: L.font, seed: 'etiquetas-arsenal', anisotropy: this.anisotropy,
    });
    const rng = new RNG('fileiras-arsenal');
    let k = 0;
    const strip = (text, x, z, tilt) => {
      const info = this.labelAtlas.labels[k++];
      const length = labelLength(info.aspect, L);
      const material = this.set.adopt(`etiqueta-arsenal-${text}`, tapeLabelMaterial(this.set.textures, {
        atlas: this.labelAtlas.texture, rect: info.rect, length, width: L.tapeWidth, margin: L.margin, textHeight: L.textHeight,
        ink: L.ink, name: `etiqueta-arsenal-${text}`,
      }));
      const mesh = new THREE.Mesh(tapeStrip(length, L.tapeWidth, { seed: `arsenal-${text}` }), material);
      mesh.rotation.set(-Math.PI / 2, 0, tilt * DEG);
      mesh.position.set(x + length / 2, this.matTop + L.lift, z);
      mesh.receiveShadow = true;
      mesh.name = `etiqueta-${text}`;
      this.root.add(mesh);
    };
    for (const row of ARSENAL.rows) {
      strip(row.label, ARSENAL.rowLabelX, row.z + 4, rng.float(-3, 3));
      let x = ARSENAL.rowX0;
      for (const id of row.ids) {
        if (!this.weapons.has(id)) continue;
        const inst = await this.weapons.instance(id, { lod: 'perto' });
        await this.precompile?.(inst);
        const b = this.weapons.info(id).bounds;
        // Deitada com o lado direito para cima: +Z da arma vira +Y do mundo (o topo aponta para o fundo).
        inst.rotation.set(-Math.PI / 2, 0, rng.float(-2, 2) * DEG);
        inst.position.set(x - b.min[0], this.matTop - b.min[2] + 0.15, row.z);
        inst.name = `fileira-${id}`;
        this.root.add(inst);
        this.displays.set(id, inst);
        strip(WEAPONS[id]?.name ?? id, x, row.z - b.min[1] + ARSENAL.labelForward, rng.float(-4, 4));
        x += b.max[0] - b.min[0] + ARSENAL.rowGap;
      }
    }
  }

  /** Troca a arma da roda (fila: pedidos seguidos esperam o anterior). */
  select(id) {
    this.selecting = this.selecting.then(() => this.#place(id, { faction: null })).catch((err) => this.log?.error('bancada:', err));
    return this.selecting;
  }

  /** Remonta a arma da roda com o estado atual (facção, nível). */
  refresh() {
    this.selecting = this.selecting.then(() => this.#place(this.state.id, { faction: this.state.faction })).catch((err) => this.log?.error('bancada:', err));
    return this.selecting;
  }

  async #place(id, { faction }) {
    this.#clearWheel();
    if (!id || !this.weapons.has(id)) {
      this.state.id = null;
      this.onChange?.();
      return;
    }
    this.state.id = id;
    const glb = this.weapons.source(id) === 'glb';
    // A realista não tem acento de facção (a identidade do time fica nas luvas, 4.1b); a de massinha pega a pedida ou a dela.
    this.state.faction = glb ? null : faction ?? weaponFaction(id);
    if (!this.weapons.lods(id).includes(this.state.lod)) this.state.lod = 'perto';
    const weapon = await this.weapons.instance(id, glb ? { lod: this.state.lod } : { lod: this.state.lod, faction: this.state.faction });
    await this.precompile?.(weapon);
    if (this.state.id !== id) return;
    const stand = buildWireStand(this.set, ARSENAL.stand, weapon);
    stand.group.add(weapon);
    weapon.position.copy(stand.weaponOffset);
    this.stand = stand.group;
    this.weapon = weapon;
    this.wheel.spinner.add(stand.group);
    this.#applySkin();
    this.#applyExplode();
    this.#applyAnchors();
    this.#applyOverlay();
    this.onChange?.();
  }

  #clearWheel() {
    if (this.stand) {
      this.stand.removeFromParent();
      this.stand.traverse((o) => {
        if (o.geometry && !o.geometry.userData?.shared) o.geometry.dispose();
      });
    }
    this.#disposeSkin();
    this.overlay?.geometry.dispose();
    this.overlay?.material.dispose();
    this.overlay = null;
    this.stand = null;
    this.weapon = null;
  }

  setFaction(faction) {
    this.state.faction = faction;
    return this.refresh();
  }

  setLod(lod) {
    this.state.lod = lod;
    return this.refresh();
  }

  /**
   * Skin da arma da roda. Na realista, `value` é "fabrica" ou a chave de uma skin nomeada e a troca é no serviço (o
   * evento `skin` volta por onSkin e remonta a roda e a fileira; a mão troca sozinha); na de massinha, a chave de uma
   * skin de massa (ou "" para a massa da receita), só na roda.
   */
  setSkin(value) {
    const id = this.state.id;
    if (id && this.weapons.source(id) === 'glb') {
      this.weapons.setSkin(id, skinPorNome(id, value || FABRICA));
      return;
    }
    this.state.skin = value || null;
    this.#applySkin();
  }

  /** Skin trocada no serviço (o painel ou o console `skin`): a arma da fileira e, se estiver nela, a da roda voltam novas. */
  onSkin(id) {
    if (this.weapons.source(id) !== 'glb') return this.selecting;
    this.selecting = this.selecting.then(async () => {
      await this.#renewDisplay(id);
      if (this.state.id === id) await this.#place(id, { faction: null });
      else this.onChange?.();
    }).catch((err) => this.log?.error('bancada:', err));
    return this.selecting;
  }

  /** Troca a instância da fileira por uma nova (skin nova), no mesmo lugar. */
  async #renewDisplay(id) {
    const old = this.displays.get(id);
    if (!old) return;
    const fresh = await this.weapons.instance(id, { lod: 'perto' });
    await this.precompile?.(fresh);
    fresh.position.copy(old.position);
    fresh.rotation.copy(old.rotation);
    fresh.name = old.name;
    old.parent.add(fresh);
    old.removeFromParent();
    this.displays.set(id, fresh);
  }

  #disposeSkin() {
    for (const m of this.skinMaterials) m.dispose();
    this.skinMaterials = [];
  }

  #applySkin() {
    if (!this.weapon) return;
    this.#disposeSkin();
    // A realista já vem com os materiais da skin atual do serviço.
    if (this.weapon.userData.weapon.source === 'glb') return;
    const skin = this.state.skin;
    let clones = null;
    this.weapon.traverse((o) => {
      if (!o.isMesh) return;
      if (!o.userData.sharedMaterials) o.userData.sharedMaterials = o.material;
      if (!skin) {
        o.material = o.userData.sharedMaterials;
        return;
      }
      // A skin vale para a arma inteira: um clone de cada massa (os materiais compartilhados não mudam).
      if (!clones) {
        clones = o.userData.sharedMaterials.map((m) => {
          const c = m.clone().setSkin(skin);
          c.userData.shared = false;
          return c;
        });
        this.skinMaterials = clones;
      }
      o.material = clones;
    });
  }

  setExplode(v) {
    this.state.explode = v;
    this.#applyExplode();
  }

  #applyExplode() {
    const parts = this.weapon?.userData.weapon.parts;
    if (!parts) return;
    for (const [name, holder] of Object.entries(parts)) {
      const dir = ARSENAL.explode.dirs[name] ?? [0, 0, 0];
      const k = this.state.explode * ARSENAL.explode.max;
      holder.position.set(holder.userData.rest[0] + dir[0] * k, holder.userData.rest[1] + dir[1] * k, holder.userData.rest[2] + dir[2] * k);
    }
  }

  setAnchors(on) {
    this.state.anchors = on;
    this.#applyAnchors();
  }

  #applyAnchors() {
    const anchors = this.weapon?.userData.weapon.anchors;
    if (!anchors) return;
    for (const a of Object.values(anchors)) {
      const helper = a.getObjectByName('eixos-ancora');
      if (this.state.anchors && !helper) {
        const axes = new THREE.AxesHelper(ARSENAL.anchorSize);
        axes.name = 'eixos-ancora';
        axes.material.depthTest = false;
        axes.renderOrder = 10;
        a.add(axes);
      } else if (!this.state.anchors && helper) {
        helper.removeFromParent();
        helper.geometry.dispose();
        helper.material.dispose();
      }
    }
  }

  setPlanOverlay(on) {
    this.state.plan = on;
    this.#applyOverlay();
  }

  #applyOverlay() {
    this.overlay?.removeFromParent();
    this.overlay?.geometry.dispose();
    this.overlay?.material.dispose();
    this.overlay = null;
    const info = this.state.id ? this.weapons.info(this.state.id) : null;
    if (!this.state.plan || !info?.plan || !this.weapon) return;
    const { outline, holes } = placeReference(info, info.plan);
    const z = info.bounds.max[2] + ARSENAL.planOverlay.lift;
    const segs = [];
    for (const ring of [outline, ...holes]) {
      for (let i = 0; i < ring.length; i++) {
        const a = ring[i];
        const b = ring[(i + 1) % ring.length];
        segs.push(a[0], a[1], z, b[0], b[1], z);
      }
    }
    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.Float32BufferAttribute(segs, 3));
    const mat = new THREE.LineBasicMaterial({ color: ARSENAL.planOverlay.color, depthTest: false, transparent: true, opacity: 0.9 });
    this.overlay = new THREE.LineSegments(geo, mat);
    this.overlay.name = 'planta-sobreposta';
    this.overlay.renderOrder = 11;
    this.weapon.add(this.overlay);
  }

  setSpin(on) {
    this.state.spin = on;
  }

  /**
   * Silhueta lateral da arma da roda contra a planta: a de massinha mede aqui (IoU do SDF; aceite ≥ 0,8); a realista
   * traz a do Blender (relatório: com a tolerância de 1 px da foto, aceite ≥ 0,98). null sem planta.
   * @returns {{iou:number, bruto:number|null, origem:'glb'|'massinha'}|null}
   */
  measure() {
    const info = this.state.id ? this.weapons.info(this.state.id) : null;
    if (!info?.plan) return null;
    if (info.source === 'glb') return { iou: info.report.silhueta.iouTolerancia, bruto: info.report.silhueta.iouBruto, origem: 'glb' };
    return { iou: silhouetteIoU(info.recipe, info.plan, { cell: 0.1 }).iou, bruto: null, origem: 'massinha' };
  }

  /**
   * Relê do disco a arma da roda (depois de exportar do Blender) e remonta a roda e a fileira. As instâncias dessa arma
   * saem da cena antes de a biblioteca descartar as malhas (WeaponLibrary.reload) e voltam novas no fim, mesmo se a
   * releitura falhar (aí com o modelo que continuou valendo).
   */
  async reload() {
    const id = this.state.id;
    if (!id) return;
    this.#clearWheel();
    const old = this.displays.get(id);
    const slot = old ? { parent: old.parent, position: old.position.clone(), rotation: old.rotation.clone(), name: old.name } : null;
    old?.removeFromParent();
    this.displays.delete(id);
    try {
      await this.weapons.reload(id, this.state.lod);
    } finally {
      if (slot) {
        try {
          const fresh = await this.weapons.instance(id, { lod: 'perto' });
          await this.precompile?.(fresh);
          fresh.position.copy(slot.position);
          fresh.rotation.copy(slot.rotation);
          fresh.name = slot.name;
          slot.parent.add(fresh);
          this.displays.set(id, fresh);
        } catch (err) {
          this.log?.error(`bancada: a fileira ficou sem ${id}:`, err);
        }
      }
      await this.refresh();
    }
  }

  frame(dt) {
    if (this.state.spin && this.wheel) this.wheel.spinner.rotation.y += ARSENAL.turntable.spin * dt;
  }

  dispose() {
    this.#clearWheel();
    this.labelAtlas?.dispose();
    this.labelAtlas = null;
    for (const t of this.textures) t.dispose();
    this.textures = [];
    this.displays.clear();
    this.onChange = null;
  }
}
