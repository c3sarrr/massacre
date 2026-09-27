// Contas do viewmodel parado (Fase 4.1; docs/phases/phase-4.md, seção 4.1, "Viewmodel parado"), sem cena: o FOV no
// referencial do CS, a pose da arma na câmera por categoria (com os offsets), a pose de cada âncora na câmera (onde vai
// cada pulso), os cotovelos, a facção do acento e quando o viewmodel aparece. O Viewmodel (viewmodel.js) aplica; os
// testes do Node conferem.
// Referencial da câmera: +X direita, +Y cima, −Z frente. Referencial da arma: +X boca, +Y cima, +Z lado direito.

import * as THREE from 'three';
import { VIEWMODEL } from '../../data/viewmodel.js';
import { weaponFaction } from '../model/recipe.js';

const DEG = Math.PI / 180;

/** Giro de base: a boca (+X da arma) para a frente (−Z), o lado direito (+Z) para a direita (+X), o topo para cima. */
export const WEAPON_TO_VIEW = Object.freeze(new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0, 1, 0), Math.PI / 2));

/** FOV vertical (graus) do viewmodel_fov do CS (horizontal num quadro 4:3; fica fixo em qualquer tela, Hor+). */
export function viewmodelVerticalFov(fov) {
  return (2 * Math.atan(Math.tan((fov * DEG) / 2) / VIEWMODEL.fov.aspect)) / DEG;
}

/** Categoria de posição de uma arma com receita (null: não tem). */
export function viewCategory(id) {
  return VIEWMODEL.weapons[id]?.category ?? null;
}

/** Ajuste fino da arma somado à posição da categoria (u, referencial da câmera), ou null. */
export function weaponNudge(id) {
  return VIEWMODEL.weapons[id]?.nudge ?? null;
}

/**
 * Posição de uma categoria com um ajuste por cima (o `viewmodel_ajuste` do console afina os dados ao vivo).
 * @param {string} category
 * @param {{pos?:number[], angles?:number[], elbows?:{direita?:number[], esquerda?:number[]}}|null} [tune]
 */
export function categoryPlacement(category, tune = null) {
  const base = VIEWMODEL.categories[category];
  if (!base) throw new Error(`categoria de viewmodel desconhecida: ${category}`);
  return {
    pos: tune?.pos ?? base.pos,
    angles: tune?.angles ?? base.angles,
    elbows: { direita: tune?.elbows?.direita ?? base.elbows.direita, esquerda: tune?.elbows?.esquerda ?? base.elbows.esquerda },
  };
}

const _e = new THREE.Euler();
const _q = new THREE.Quaternion();

/**
 * Pose da arma no referencial da câmera: a posição da categoria + o ajuste fino da arma + offsets (x direita, y frente,
 * z cima, como no CS) e o giro da categoria (arfagem, guinada, rolagem na ordem da câmera, 'YXZ') sobre o giro de base.
 * @param {string} category
 * @param {{offset?:{x:number,y:number,z:number}, tune?:object|null, nudge?:number[]|null}} [options]
 * @param {{position:THREE.Vector3, quaternion:THREE.Quaternion}} [out]
 */
export function viewPlacement(category, { offset = { x: 0, y: 0, z: 0 }, tune = null, nudge = null } = {}, out = { position: new THREE.Vector3(), quaternion: new THREE.Quaternion() }) {
  const p = categoryPlacement(category, tune);
  const n = nudge ?? [0, 0, 0];
  out.position.set(p.pos[0] + n[0] + offset.x, p.pos[1] + n[1] + offset.z, p.pos[2] + n[2] - offset.y);
  const [pitch, yaw, roll] = p.angles;
  _e.set(pitch * DEG, yaw * DEG, roll * DEG, 'YXZ');
  out.quaternion.setFromEuler(_e).multiply(WEAPON_TO_VIEW);
  return out;
}

/**
 * Pose de uma âncora da receita ({pos, rot}) no referencial da câmera, dada a pose da arma.
 * @param {{position:THREE.Vector3, quaternion:THREE.Quaternion}} placement
 * @param {{pos:number[], rot?:number[]}} anchor
 * @param {{position:THREE.Vector3, quaternion:THREE.Quaternion}} [out]
 */
export function anchorPose(placement, anchor, out = { position: new THREE.Vector3(), quaternion: new THREE.Quaternion() }) {
  out.position.fromArray(anchor.pos).applyQuaternion(placement.quaternion).add(placement.position);
  const r = anchor.rot ?? [0, 0, 0];
  _e.set(r[0], r[1], r[2], 'XYZ');
  out.quaternion.copy(placement.quaternion).multiply(_q.setFromEuler(_e));
  return out;
}

/** Cotovelo (para onde o antebraço aponta) de um lado, no referencial da câmera. */
export function elbowTarget(category, side, tune = null, out = new THREE.Vector3()) {
  return out.fromArray(categoryPlacement(category, tune).elbows[side]);
}

/** Mãos que a arma usa: as âncoras `maoDireita`/`maoEsquerda` da receita (a faca só tem a direita). */
export function handSides(recipe) {
  const sides = [];
  if (recipe?.anchors?.maoDireita) sides.push('direita');
  if (recipe?.anchors?.maoEsquerda) sides.push('esquerda');
  return sides;
}

/** Âncora da mão de cada lado. */
export const HAND_ANCHOR = Object.freeze({ direita: 'maoDireita', esquerda: 'maoEsquerda' });

/**
 * Facção do acento da arma na mão: as de um lado só (Glock, AK, M4A4...) ficam com o seu; as dos dois lados pegam o
 * time de quem segura (ou o amarelo/branco sem time).
 * @param {string} id @param {'tr'|'ct'|null} team
 */
export function viewFaction(id, team) {
  const own = weaponFaction(id);
  if (own !== 'ambos') return own;
  return team === 'tr' || team === 'ct' ? team : 'ambos';
}

/**
 * O viewmodel aparece? Em primeira pessoa com o PlayerPawn, vivo, fora do noclip, sem a luneta aberta (a visão pela
 * luneta é da 4.5; no CS a arma some com o zoom), com `r_viewmodel 1` e com receita para o item na mão (as outras 18
 * armas até a 4.4, granadas até a 4.7, a bomba até a Fase 8). A bancada `arsenal` força com "Segurar".
 * @param {{enabled:boolean, firstPerson:boolean, alive:boolean, noclip:boolean, zoomed:boolean, item:string|null,
 *          hasRecipe:(id:string)=>boolean}} s
 */
export function viewmodelVisible(s) {
  return Boolean(s.enabled && s.firstPerson && s.alive && !s.noclip && !s.zoomed && s.item && s.hasRecipe(s.item));
}

/** Chaves da config de cada campo das posições prontas (viewmodel_presetpos). */
const PRESET_KEYS = Object.freeze({ fov: 'viewmodel.fov', x: 'viewmodel.offsetX', y: 'viewmodel.offsetY', z: 'viewmodel.offsetZ' });

/** Aplica uma posição pronta do CS (1 Mesa, 2 Sofá, 3 Clássica) na config. */
export function applyViewmodelPreset(config, id) {
  const p = VIEWMODEL.presets[id];
  if (!p) throw new Error(`posição desconhecida: ${id} (use ${Object.keys(VIEWMODEL.presets).join(', ')})`);
  for (const [field, key] of Object.entries(PRESET_KEYS)) config.set(key, p[field]);
  return p;
}

/** A posição pronta que a config tem agora (ou null se foi ajustada à mão). */
export function currentViewmodelPreset(config) {
  for (const [id, p] of Object.entries(VIEWMODEL.presets)) {
    if (Object.entries(PRESET_KEYS).every(([field, key]) => Math.abs(config.get(key) - p[field]) < 1e-6)) return id;
  }
  return null;
}
