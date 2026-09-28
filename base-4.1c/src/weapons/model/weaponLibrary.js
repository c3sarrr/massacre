// Serviço `weaponModels` (Fase 4.1: docs/phases/phase-4.md, seção 4.1, "Gerador"; Fase 4.1a:
// docs/superpowers/specs/2026-09-26-armas-realistas-design.md, seção 5.2): guarda e empresta as armas do jogo, de duas
// origens até o fim da 4.1d —
//  - `glb`: as realistas feitas no Blender (src/data/armasReais.js), pela GlbSource: o .glb, as texturas, os materiais
//    de zona com a skin atual e o reflexo do set;
//  - `massinha`: as receitas da 4.1 (src/data/armas/), pelo gerador SDF: malhas por (arma, nível), materiais por (arma,
//    facção), a planta de referência para a bancada.
// A interface é a mesma para as duas: `ids`, `has`, `source`, `lods`, `describe`/`info` (no lugar da `recipe` da 4.1),
// `meshes`/`preload`, `instance`, `report`, `reload` (depois de exportar do Blender) e `dispose`; as skins de acabamento
// (`skinOf`/`setSkin`) e o ambiente (`setEnvironment`) valem para as realistas. Geometrias, materiais e texturas são
// compartilhados (userData.shared: o dispose das cenas não os toca) e saem só aqui.

import * as THREE from 'three';
import { EV } from '../../core/events.js';
import { ARMAS } from '../../data/armas/index.js';
import { ARMAS_REAIS } from '../../data/armasReais.js';
import { VIEWMODEL } from '../../data/viewmodel.js';
import { bounds } from '../../clay/sdf/nodes.js';
import { plantaDoArquivo } from './ficha.js';
import { GlbSource, carregadoresDoNavegador } from './glbSource.js';
import { recipeWholeTree, validateRecipe, weaponFaction } from './recipe.js';
import { silhouetteLength } from './silhouette.js';
import { WEAPON_LODS, assembleWeapon, buildWeaponMeshes, createWeaponMaterials } from './weaponModel.js';

const RAIZ = new URL('../../../', import.meta.url);

export class WeaponLibrary {
  #sdf;
  #log;
  #events;
  #carregar;
  #glb;
  // A arma realista vale sobre a receita de massinha do mesmo id (a da AK fica no disco até sair, na Tarefa 16).
  #recipes = new Map(Object.entries(ARMAS).filter(([id]) => !ARMAS_REAIS[id]));
  #meshes = new Map(); // `${id}:${lod}` → Promise<built> (massinha)
  #built = new Map(); // `${id}:${lod}` → built (pronto)
  #materials = new Map(); // `${id}:${facção}` → ClayMaterial[]
  #plans = new Map(); // id → planta (massinha)
  #infos = new Map(); // id → info (massinha)
  #disposed = false;

  /**
   * @param {{sdf:import('../../clay/sdf/sdfMesher.js').SdfMesher|null, log?:object|null,
   *          events?:import('../../core/events.js').EventBus|null, anisotropy?:number,
   *          carregadores?:object|null}} deps `carregadores` substitui o GLTFLoader/TextureLoader/fetch (testes)
   */
  constructor({ sdf, log = null, events = null, anisotropy = 8, carregadores = null }) {
    this.#sdf = sdf;
    this.#log = log;
    this.#events = events;
    this.#carregar = carregadores ?? carregadoresDoNavegador();
    this.#glb = new GlbSource({ carregadores: this.#carregar, log, anisotropia: anisotropy });
  }

  /** Armas com modelo: as realistas, depois as de massinha (a ordem dos registros). */
  get ids() {
    return [...this.#glb.ids, ...this.#recipes.keys()];
  }

  has(id) {
    return this.#glb.has(id) || this.#recipes.has(id);
  }

  /** 'glb', 'massinha' ou null. */
  source(id) {
    if (this.#glb.has(id)) return 'glb';
    return this.#recipes.has(id) ? 'massinha' : null;
  }

  /** Níveis de detalhe da arma. */
  lods(id) {
    return this.#glb.has(id) ? this.#glb.lods() : WEAPON_LODS;
  }

  /** Carrega o que falta para o `info` (o .glb, o relatório e a ficha; a planta das de massinha) e devolve o info. */
  async describe(id) {
    if (this.#disposed) throw new Error('WeaponLibrary: já foi descartada');
    if (this.#glb.has(id)) return (await this.#glb.carregar(id)).info;
    if (!this.#recipes.has(id)) throw new Error(`arma sem modelo: ${id}`);
    if (!this.#plans.has(id)) {
      // A planta vem do arquivo que a receita aponta (`refs.planta`); a faca não tem (é desenhada de cabeça): sem busca.
      const arquivo = this.#recipes.get(id).refs?.planta;
      const plan = arquivo ? plantaDoArquivo(await this.#carregar.json(new URL(arquivo, RAIZ).href)) : null;
      this.#plans.set(id, plan);
      this.#infos.delete(id);
    }
    return this.info(id);
  }

  /** Info da arma no formato comum (ver o plano da 4.1a, Tarefa 11); null antes de carregar (glb) ou sem modelo. */
  info(id) {
    if (this.#glb.has(id)) return this.#glb.info(id);
    const recipe = this.#recipes.get(id);
    if (!recipe) return null;
    let info = this.#infos.get(id);
    if (!info) {
      const b = bounds(recipeWholeTree(recipe));
      const plan = this.#plans.get(id) ?? null;
      const size = new THREE.Vector3(b.max[0] - b.min[0], b.max[1] - b.min[1], b.max[2] - b.min[2]);
      info = {
        id, source: 'massinha', category: VIEWMODEL.weapons[id]?.category ?? null,
        bounds: { min: [...b.min], max: [...b.max] }, radius: size.length() / 2,
        anchors: recipe.anchors, sockets: null, hands: true,
        plan, lengthU: plan?.lengthU ?? silhouetteLength(recipe),
        parts: [...new Set(recipe.parts.map((p) => p.group))], zones: null, lods: [...WEAPON_LODS],
        report: null, ficha: null, iou: null, recipe,
      };
      this.#infos.set(id, info);
    }
    return info;
  }

  /**
   * Malhas de uma arma num nível (massinha: gera na primeira vez; glb: carrega o .glb). Pedidos iguais dividem a mesma
   * promessa.
   */
  meshes(id, lod = 'perto') {
    if (this.#disposed) return Promise.reject(new Error('WeaponLibrary: já foi descartada'));
    if (this.#glb.has(id)) {
      if (!this.#glb.lods().includes(lod)) return Promise.reject(new Error(`nível de detalhe desconhecido: ${lod}`));
      return this.#glb.carregar(id).then((p) => ({
        id, lod, source: 'glb', triangles: p.resumo.lods[lod].triangulos, ms: p.ms, groups: p.resumo.lods[lod].pecas,
      }));
    }
    const recipe = this.#recipes.get(id);
    if (!recipe) return Promise.reject(new Error(`arma sem modelo: ${id}`));
    if (!WEAPON_LODS.includes(lod)) return Promise.reject(new Error(`nível de detalhe desconhecido: ${lod}`));
    const key = `${id}:${lod}`;
    let pending = this.#meshes.get(key);
    if (!pending) {
      pending = buildWeaponMeshes(recipe, this.#sdf, lod).then((built) => {
        if (this.#disposed || this.#meshes.get(key) !== pending) {
          for (const g of Object.values(built.groups)) g.geometry.dispose();
          throw new Error(`arma ${id} descartada durante a geração`);
        }
        for (const g of Object.values(built.groups)) g.geometry.userData.shared = true;
        this.#built.set(key, built);
        this.#log?.debug(`arma ${id} (${lod}): ${Math.round(built.triangles)} triângulos em ${built.ms.toFixed(0)} ms`);
        return built;
      });
      pending.catch(() => {
        if (this.#meshes.get(key) === pending) this.#meshes.delete(key);
      });
      this.#meshes.set(key, pending);
    }
    return pending;
  }

  /** Materiais de massinha de uma arma para uma facção (um por massa, na ordem do `mat`). */
  #materialsFor(recipe, built, faction) {
    const key = `${recipe.id}:${faction}`;
    let list = this.#materials.get(key);
    if (!list) {
      list = createWeaponMaterials(recipe, built.materials, { faction, radius: built.radius });
      for (const m of list) m.userData.shared = true;
      this.#materials.set(key, list);
    }
    return list;
  }

  /**
   * Instância nova da arma (THREE.Group com userData.weapon). Pode ser posta em qualquer cena; tirar da cena basta.
   * @param {string} id
   * @param {{lod?:string, faction?:'tr'|'ct'|'ambos'}} [options] a facção só vale para as de massinha (o acento)
   */
  async instance(id, { lod = 'perto', faction = weaponFaction(id) } = {}) {
    if (this.#disposed) throw new Error('WeaponLibrary: já foi descartada');
    if (this.#glb.has(id)) return this.#glb.instancia(id, { lod });
    const built = await this.meshes(id, lod);
    const recipe = this.#recipes.get(id);
    return assembleWeapon(recipe, built, this.#materialsFor(recipe, built, faction), faction);
  }

  /** Pré-carrega (sem esperar): as armas do jogador ao entrar no mapa. */
  preload(ids, lod = 'perto') {
    return Promise.allSettled(ids.filter((id) => this.has(id)).map((id) =>
      (this.#glb.has(id) ? this.#glb.instancia(id, { lod: this.#glb.lods().includes(lod) ? lod : 'perto' }) : this.meshes(id, lod))));
  }

  /** Skin atual de uma arma realista. */
  skinOf(id) {
    if (!this.#glb.has(id)) throw new Error(`${id} não é uma arma realista (skins de acabamento só nas armas realistas)`);
    return this.#glb.skinOf(id);
  }

  /** Troca a skin de uma arma realista; quem tem instância na cena pede outra (EV.WEAPON_MODEL, phase 'skin'). */
  setSkin(id, skin) {
    if (!this.#glb.has(id)) throw new Error(`${id} não é uma arma realista (skins de acabamento só nas armas realistas)`);
    this.#glb.setSkin(id, skin);
    this.#events?.emit(EV.WEAPON_MODEL, { id, phase: 'skin' });
    return skin;
  }

  /** Reflexo do set (PMREM do mapa carregado) nos materiais das armas realistas; null volta ao ambiente da cena. */
  setEnvironment(texture, intensity = 1) {
    this.#glb.setAmbiente(texture, intensity);
  }

  /** Anisotropia das texturas das armas realistas (graphics.anisotropy). */
  setAnisotropy(n) {
    this.#glb.setAnisotropia(n);
  }

  /** Relatório do console (`armas`): uma linha por (arma, nível), das duas origens. */
  report() {
    const rows = this.#glb.relatorio();
    for (const id of this.#recipes.keys()) {
      for (const lod of WEAPON_LODS) {
        const built = this.#built.get(`${id}:${lod}`);
        const pending = this.#meshes.has(`${id}:${lod}`);
        rows.push({
          id, lod, source: 'massinha',
          state: built ? 'pronta' : pending ? 'gerando' : '—',
          triangles: built ? Math.round(built.triangles) : 0,
          ms: built ? Math.round(built.ms) : 0,
          groups: built ? Object.keys(built.groups).length : 0,
        });
      }
    }
    return rows;
  }

  /**
   * Relê a arma do disco (depois de exportar do Blender) sem recarregar a página. Emite EV.WEAPON_MODEL duas vezes:
   * `relendo` logo antes de descartar (quem tem instância na cena tira agora: uma malha descartada que continua sendo
   * desenhada volta para a GPU e ninguém a libera depois) e `pronta` com a arma nova carregada (glb) ou gerada no nível
   * pedido (massinha).
   */
  async reload(id, lod = 'perto') {
    if (this.#glb.has(id)) {
      this.#events?.emit(EV.WEAPON_MODEL, { id, phase: 'relendo' });
      await this.#glb.recarregar(id);
      await this.#glb.instancia(id, { lod: this.#glb.lods().includes(lod) ? lod : 'perto' });
      this.#events?.emit(EV.WEAPON_MODEL, { id, phase: 'pronta' });
      return this.#glb.info(id);
    }
    if (!this.#recipes.has(id)) throw new Error(`arma sem modelo: ${id}`);
    const url = new URL(`../../data/armas/${id}.js`, import.meta.url);
    url.searchParams.set('v', String(Date.now()));
    const mod = await import(url.href);
    const recipe = validateRecipe(mod.default);
    if (recipe.id !== id) throw new Error(`a receita de ${id} diz ser ${recipe.id}`);
    this.#events?.emit(EV.WEAPON_MODEL, { id, phase: 'relendo' });
    this.#forget(id);
    this.#recipes.set(id, recipe);
    await this.meshes(id, lod);
    this.#events?.emit(EV.WEAPON_MODEL, { id, phase: 'pronta' });
    return this.info(id);
  }

  #forget(id) {
    for (const lod of WEAPON_LODS) {
      const key = `${id}:${lod}`;
      const built = this.#built.get(key);
      if (built) for (const g of Object.values(built.groups)) g.geometry.dispose();
      this.#built.delete(key);
      this.#meshes.delete(key);
    }
    for (const [key, list] of this.#materials) {
      if (!key.startsWith(`${id}:`)) continue;
      for (const m of list) m.dispose();
      this.#materials.delete(key);
    }
    this.#infos.delete(id);
  }

  dispose() {
    for (const id of this.#recipes.keys()) this.#forget(id);
    this.#glb.dispose();
    this.#disposed = true;
  }
}
