// Serviço `weaponModels` (Fase 4.1; docs/phases/phase-4.md, seção 4.1, "Gerador"): guarda as malhas de cada arma por
// (arma, nível) e os materiais por (arma, facção), e entrega instâncias que só apontam para eles — a geometria e os
// materiais são compartilhados (marcados `userData.shared`, o dispose das cenas não os toca) e saem só no dispose do
// serviço ou na recarga da receita. Pré-carrega as armas do jogador ao entrar no mapa, para a troca não esperar.
// Os materiais são por arma (e não só por massa) porque o boil de cada um segue o tamanho da arma.

import { EV } from '../../core/events.js';
import { ARMAS } from '../../data/armas/index.js';
import { validateRecipe, weaponFaction } from './recipe.js';
import { WEAPON_LODS, assembleWeapon, buildWeaponMeshes, createWeaponMaterials } from './weaponModel.js';

export class WeaponLibrary {
  #sdf;
  #log;
  #events;
  #recipes = new Map(Object.entries(ARMAS));
  #meshes = new Map(); // `${id}:${lod}` → Promise<built>
  #built = new Map(); // `${id}:${lod}` → built (pronto)
  #materials = new Map(); // `${id}:${facção}` → ClayMaterial[]
  #disposed = false;

  /**
   * @param {{sdf:import('../../clay/sdf/sdfMesher.js').SdfMesher, log?:object|null,
   *          events?:import('../../core/events.js').EventBus|null}} deps
   */
  constructor({ sdf, log = null, events = null }) {
    this.#sdf = sdf;
    this.#log = log;
    this.#events = events;
  }

  /** Armas com receita (a ordem do registro src/data/armas/index.js). */
  get ids() {
    return [...this.#recipes.keys()];
  }

  has(id) {
    return this.#recipes.has(id);
  }

  recipe(id) {
    return this.#recipes.get(id) ?? null;
  }

  /**
   * Malhas de uma arma num nível (gera na primeira vez; pedidos iguais dividem a mesma promessa).
   * @returns {Promise<object>} ver buildWeaponMeshes
   */
  meshes(id, lod = 'perto') {
    if (this.#disposed) return Promise.reject(new Error('WeaponLibrary: já foi descartada'));
    const recipe = this.recipe(id);
    if (!recipe) return Promise.reject(new Error(`arma sem receita: ${id}`));
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

  /** Materiais de uma arma para uma facção (um por massa, na ordem do `mat`). */
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
   * Instância nova da arma (THREE.Group; ver assembleWeapon). Pode ser posta em qualquer cena; tirar da cena basta.
   * @param {string} id
   * @param {{lod?:string, faction?:'tr'|'ct'|'ambos'}} [options] facção padrão: a da arma
   */
  async instance(id, { lod = 'perto', faction = weaponFaction(id) } = {}) {
    const built = await this.meshes(id, lod);
    const recipe = this.recipe(id);
    return assembleWeapon(recipe, built, this.#materialsFor(recipe, built, faction), faction);
  }

  /** Pré-carrega as malhas (sem esperar): as armas do jogador ao entrar no mapa. */
  preload(ids, lod = 'perto') {
    return Promise.allSettled(ids.filter((id) => this.has(id)).map((id) => this.meshes(id, lod)));
  }

  /** Relatório do console (`armas`): uma linha por (arma, nível) gerado. */
  report() {
    const rows = [];
    for (const id of this.ids) {
      for (const lod of WEAPON_LODS) {
        const built = this.#built.get(`${id}:${lod}`);
        const pending = this.#meshes.has(`${id}:${lod}`);
        rows.push({
          id, lod,
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
   * Relê a receita do disco (depois de exportar do Blender) sem recarregar a página: importa o módulo de novo, valida,
   * troca, descarta as malhas e os materiais antigos e gera o nível pedido. Emite EV.WEAPON_MODEL duas vezes: `relendo`
   * logo antes de descartar (quem tem instância na cena tira agora: uma malha descartada que continua sendo desenhada
   * volta para a GPU e ninguém a libera depois) e `pronta` com a malha nova gerada.
   */
  async reload(id, lod = 'perto') {
    if (!this.has(id)) throw new Error(`arma sem receita: ${id}`);
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
    return recipe;
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
  }

  dispose() {
    for (const id of this.ids) this.#forget(id);
    this.#disposed = true;
  }
}
