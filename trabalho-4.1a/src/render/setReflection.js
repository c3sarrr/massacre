// Reflexo do set das armas realistas (Fase 4.1a; desenho em docs/superpowers/specs/2026-09-26-armas-realistas-design.md,
// seção 5.4; plano da 4.1a, D9): uma câmera cúbica (256² por face) fotografa o set de um ponto na altura do olho do
// boneco — o `reflection` do mapa montado (o centro da área jogável, dos dados dele) ou, sem ele, o spawn — e o PMREM
// filtra a foto no mapa de ambiente dos materiais das armas realistas (weaponModels.setEnvironment): o metal reflete o
// set de verdade. O `scene.environment` de cada mapa continua o do estúdio para o resto. O MatchState fotografa ao
// montar o mapa e de novo quando a GPU volta (EV.RENDER_CONTEXT), com o corpo do jogador fora da foto.

import * as THREE from 'three';
import { REFLEXO } from '../data/armasReais.js';
import { HULL } from '../data/movement.js';

/**
 * Ponto do reflexo de um mapa montado (mundo): o `reflection` dele; sem ele, o spawn — que é o pé nos mapas de andar
 * (soma a altura do olho) e já é o olho na câmera livre.
 * @param {{reflection?:THREE.Vector3, spawn:{position:THREE.Vector3}, collision?:object|null}} map
 * @returns {THREE.Vector3} uma cópia
 */
export function pontoDoReflexo(map) {
  if (map.reflection) return map.reflection.clone();
  const p = map.spawn.position.clone();
  if (map.collision) p.y += HULL.standEye;
  return p;
}

/**
 * Fotografa o set e devolve o render target do PMREM (a textura em `.texture`); quem chama descarta com `dispose()`.
 * @param {THREE.WebGLRenderer} renderer
 * @param {THREE.Scene} scene
 * @param {THREE.Vector3} position
 * @returns {THREE.WebGLRenderTarget}
 */
export function capturarReflexo(renderer, scene, position) {
  const pmrem = new THREE.PMREMGenerator(renderer);
  try {
    return pmrem.fromScene(scene, 0, REFLEXO.perto, REFLEXO.longe, { size: REFLEXO.tamanho, position });
  } finally {
    pmrem.dispose();
  }
}
