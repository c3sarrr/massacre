// Pesos do skinning e poses da mão de massinha (Fase 4.1; docs/phases/phase-4.md, seção 4.1, "Mãos de 4 dedos"). Puro:
// os testes do Node conferem os pesos (normalizados, cada vértice do dedo puxado pelo seu osso) e as poses (dentro dos
// limites das juntas); o rig (handRig.js) aplica.
// Pesos: distância de cada vértice à cápsula de cada osso (segmento + raio), queda suave 1/(d + queda)⁴, os 4 maiores,
// normalizados. Cada vértice só ouve os ossos da sua cadeia (o dedo mais perto, com a mão), então um dedo que dobra
// não arrasta o vizinho.

import { HAND, HAND_LIMITS, HAND_POSES } from '../../data/hands.js';

function segmentDistance(px, py, pz, h, t) {
  const dx = t[0] - h[0];
  const dy = t[1] - h[1];
  const dz = t[2] - h[2];
  const l2 = dx * dx + dy * dy + dz * dz || 1e-12;
  const s = Math.max(0, Math.min(1, ((px - h[0]) * dx + (py - h[1]) * dy + (pz - h[2]) * dz) / l2));
  return Math.hypot(px - h[0] - s * dx, py - h[1] - s * dy, pz - h[2] - s * dz);
}

/**
 * Índices e pesos de skinning (4 influências por vértice).
 * @param {Float32Array|number[]} positions xyz no referencial do modelo (repouso)
 * @param {Array} bones handBones()
 * @param {{falloff?:number, influences?:number}} [opts]
 * @returns {{skinIndex:Uint16Array, skinWeight:Float32Array}}
 */
export function computeSkinWeights(positions, bones, { falloff = HAND.skin.falloff, influences = HAND.skin.influences } = {}) {
  const n = positions.length / 3;
  const k = influences;
  const skinIndex = new Uint16Array(n * k);
  const skinWeight = new Float32Array(n * k);
  const chains = [...new Set(bones.map((b) => b.chain))];
  const chainBones = Object.fromEntries(chains.map((c) => [c, bones.map((b, i) => (b.chain === c ? i : -1)).filter((i) => i >= 0)]));
  const handIndex = bones.findIndex((b) => b.name === 'mao');
  const surf = new Float64Array(bones.length);
  const idx = new Array(bones.length);
  for (let v = 0; v < n; v++) {
    const px = positions[v * 3];
    const py = positions[v * 3 + 1];
    const pz = positions[v * 3 + 2];
    let bestChain = 'braco';
    let best = Infinity;
    for (let b = 0; b < bones.length; b++) {
      const d = Math.max(0, segmentDistance(px, py, pz, bones[b].head, bones[b].tail) - bones[b].radius);
      surf[b] = d;
      if (d < best) {
        best = d;
        bestChain = bones[b].chain;
      }
    }
    const allowed = bestChain === 'braco' ? chainBones.braco : [handIndex, ...chainBones[bestChain]];
    let count = 0;
    for (const b of allowed) idx[count++] = b;
    const ws = allowed.map((b) => 1 / (surf[b] + falloff) ** 4);
    const order = ws.map((w, i) => i).sort((a, b) => ws[b] - ws[a]).slice(0, k);
    let sum = 0;
    for (const i of order) sum += ws[i];
    for (let j = 0; j < k; j++) {
      const i = order[j];
      skinIndex[v * k + j] = i === undefined ? 0 : idx[i];
      skinWeight[v * k + j] = i === undefined ? 0 : ws[i] / sum;
    }
  }
  return { skinIndex, skinWeight };
}

const clamp = (v, [lo, hi]) => Math.max(lo, Math.min(hi, v));

/**
 * Rotações locais de cada osso para uma pose (Euler 'YZX' do three: [x, y, z]); a flexão dobra para a palma (−Y), então é
 * giro negativo em Z. Tudo preso aos limites das juntas. O antebraço não gira aqui (quem posiciona o braço é o viewmodel).
 * @param {string|object} pose nome em HAND_POSES ou a pose
 * @returns {Object<string, number[]>}
 */
export function poseRotations(pose) {
  const p = typeof pose === 'string' ? HAND_POSES[pose] : pose;
  if (!p) throw new Error(`pose de mão desconhecida: ${pose}`);
  const L = HAND_LIMITS;
  const out = { antebraco: [0, 0, 0], mao: [0, clamp(p.wrist[1], L.wrist), -clamp(p.wrist[0], L.wrist)] };
  HAND.fingers.forEach((f, i) => {
    const [a, b, c] = p.fingers[i];
    out[`${f.id}_1`] = [0, clamp(p.spread[i], L.spread), -clamp(a, L.flex)];
    out[`${f.id}_2`] = [0, 0, -clamp(b, L.flex)];
    out[`${f.id}_3`] = [0, 0, -clamp(c, L.flex)];
  });
  const [yaw, f1, f2] = p.thumb;
  out[`${HAND.thumb.id}_1`] = [0, -clamp(yaw, L.thumbYaw), -clamp(f1, L.thumbFlex) * 0.6];
  out[`${HAND.thumb.id}_2`] = [0, 0, -clamp(f1, L.thumbFlex) * 0.4 - clamp(f2, L.thumbFlex) * 0.3];
  out[`${HAND.thumb.id}_3`] = [0, 0, -clamp(f2, L.thumbFlex) * 0.7];
  return out;
}

/** A mesma pose na mão esquerda (a direita espelhada em Z): giros em X e Y trocam de sinal, em Z ficam. */
export function mirrorRotations(rot) {
  return Object.fromEntries(Object.entries(rot).map(([k, [x, y, z]]) => [k, [-x, -y, z]]));
}
