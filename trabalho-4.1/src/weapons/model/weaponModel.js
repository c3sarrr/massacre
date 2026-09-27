// Gerador das armas de massinha (Fase 4.1; desenho em docs/phases/phase-4.md, seção 4.1, "Gerador"): a receita vira
// uma malha por grupo animável (SdfMesher: nos Workers e com o cache do IndexedDB), cada malha num Object3D posto no
// pivô do grupo, as âncoras como Object3D vazios e os materiais de massinha com o acento da facção.
// Dois níveis de detalhe: `perto` (viewmodel e bancada) e `mundo` (arma no chão e na mão dos outros, Fases 5, 8 e 9).

import * as THREE from 'three';
import { ClayMaterial } from '../../clay/ClayMaterial.js';
import { bounds } from '../../clay/sdf/nodes.js';
import { WEAPON_MODEL } from '../../data/weaponPalette.js';
import { recipeTrees, resolveClay, validateRecipe, weaponFaction } from './recipe.js';

export const WEAPON_LODS = Object.freeze(Object.keys(WEAPON_MODEL.lods));

const now = () => (globalThis.performance?.now ? globalThis.performance.now() : Date.now());

/**
 * Opções do SdfMesher para a árvore de um grupo num nível: a resolução sai da célula do nível na maior dimensão da
 * caixa (a mesma célula em todas as armas, então a massa tem o mesmo grão na Glock e na AWP).
 * @returns {{resolution:number, maxCells:number, touchRadius:number}}
 */
export function meshOptions(tree, lod) {
  const def = WEAPON_MODEL.lods[lod];
  if (!def) throw new Error(`nível de detalhe desconhecido: ${lod} (use ${WEAPON_LODS.join(', ')})`);
  const b = bounds(tree);
  const extent = Math.max(b.max[0] - b.min[0], b.max[1] - b.min[1], b.max[2] - b.min[2]);
  return {
    resolution: Math.max(8, Math.min(1024, Math.ceil(extent / def.cell))),
    maxCells: def.maxCells,
    touchRadius: WEAPON_MODEL.touchRadius,
  };
}

/**
 * Gera as geometrias de uma receita num nível: uma por grupo, no referencial do pivô do grupo. Quem recebe é dono
 * das geometrias (a biblioteca as marca como compartilhadas).
 * @param {object} recipe receita (src/data/armas/)
 * @param {import('../../clay/sdf/sdfMesher.js').SdfMesher} sdf
 * @param {string} [lod]
 * @returns {Promise<{id:string, lod:string, materials:string[], radius:number, triangles:number, ms:number,
 *   groups:Object<string, {geometry:THREE.BufferGeometry, pivot:number[], axis:number[]|null}>}>}
 */
export async function buildWeaponMeshes(recipe, sdf, lod = 'perto') {
  validateRecipe(recipe);
  const t0 = now();
  const { materials, groups } = recipeTrees(recipe);
  const names = Object.keys(groups);
  const geometries = await Promise.all(names.map((g) => sdf.build(groups[g].tree, meshOptions(groups[g].tree, lod))));
  const out = {};
  const box = new THREE.Box3();
  const part = new THREE.Box3();
  let triangles = 0;
  names.forEach((g, i) => {
    const geometry = geometries[i];
    geometry.name = `arma:${recipe.id}:${g}:${lod}`;
    triangles += geometry.index.count / 3;
    const { pivot, axis } = groups[g];
    box.union(part.copy(geometry.boundingBox).translate(new THREE.Vector3(...pivot)));
    out[g] = { geometry, pivot: [...pivot], axis: axis ? [...axis] : null };
  });
  const size = box.getSize(new THREE.Vector3());
  return { id: recipe.id, lod, materials, radius: size.length() / 2, triangles, ms: now() - t0, groups: out };
}

/**
 * Materiais de massinha de uma arma, um por massa na ordem do `mat` das malhas, com o acento da facção e o boil na
 * medida da arma (`setObjectSize` pelo raio: a AWP ferve em calombos maiores que a Glock, como massa de verdade).
 * @param {object} recipe
 * @param {string[]} slots massas na ordem do `mat` (buildWeaponMeshes().materials)
 * @param {{faction?:'tr'|'ct'|'ambos', radius?:number}} [options]
 * @returns {ClayMaterial[]}
 */
export function createWeaponMaterials(recipe, slots, { faction = weaponFaction(recipe.id), radius = 12 } = {}) {
  return slots.map((slot) => {
    const clay = resolveClay(recipe, slot, faction);
    const material = new ClayMaterial({
      color: clay.color,
      roughness: clay.roughness,
      wetness: clay.wetness,
      skin: clay.skin ?? 'liso',
      colorB: clay.colorB ?? null,
      colorC: clay.colorC ?? null,
      touched: true, // arma é peça de mão: as digitais crescem nas bordas e nos pontos de pega
      seed: `${recipe.id}:${slot}:${faction}`,
    });
    material.name = `arma:${recipe.id}:${slot}:${faction}`;
    material.setObjectSize(radius);
    return material;
  });
}

/**
 * Monta uma instância da arma com geometrias e materiais dados (a instância não é dona deles).
 * `userData.weapon` = {id, lod, faction, radius, parts: {grupo: Object3D no pivô}, anchors: {nome: Object3D}}; cada
 * âncora de mão traz a pose em `userData.pose`, e cada grupo o eixo de giro/deslize em `userData.axis`.
 * @returns {THREE.Group}
 */
export function assembleWeapon(recipe, built, materials, faction = weaponFaction(recipe.id)) {
  const root = new THREE.Group();
  root.name = `arma:${recipe.id}`;
  const parts = {};
  for (const [name, def] of Object.entries(built.groups)) {
    const holder = new THREE.Object3D();
    holder.name = `grupo:${name}`;
    holder.position.fromArray(def.pivot);
    holder.userData.axis = def.axis;
    holder.userData.rest = def.pivot;
    const mesh = new THREE.Mesh(def.geometry, materials);
    mesh.name = `massa:${recipe.id}:${name}`;
    mesh.castShadow = true;
    mesh.receiveShadow = true;
    holder.add(mesh);
    root.add(holder);
    parts[name] = holder;
  }
  const anchors = {};
  for (const [name, def] of Object.entries(recipe.anchors)) {
    const anchor = new THREE.Object3D();
    anchor.name = `ancora:${name}`;
    anchor.position.fromArray(def.pos);
    if (def.rot) anchor.rotation.fromArray(def.rot);
    if (def.pose) anchor.userData.pose = def.pose;
    root.add(anchor);
    anchors[name] = anchor;
  }
  root.userData.weapon = { id: recipe.id, lod: built.lod, faction, radius: built.radius, parts, anchors };
  return root;
}
