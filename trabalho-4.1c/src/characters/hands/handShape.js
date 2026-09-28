// Mão de 4 dedos de massinha com o antebraço (Fase 4.1; docs/phases/phase-4.md, seção 4.1, "Mãos de 4 dedos"): a árvore
// SDF na pose de repouso (dedos esticados) e o esqueleto de 14 ossos — antebraço, mão, 3 × 3 falanges e o polegar em 3.
// Puro (sem three.js): o rig (handRig.js), os pesos (handSkin.js) e os testes do Node usam o mesmo desenho.
// Referencial do modelo = o do antebraço: origem no cotovelo, +X para o pulso, +Y para as costas da mão, −Z para o lado
// do polegar (mão direita). A mão (osso `mao`) começa no pulso, em x = comprimento do antebraço.

import { HAND } from '../../data/hands.js';

const add = (a, b) => [a[0] + b[0], a[1] + b[1], a[2] + b[2]];
const scale = (a, s) => [a[0] * s, a[1] * s, a[2] * s];
const norm = (a) => {
  const l = Math.hypot(a[0], a[1], a[2]) || 1;
  return [a[0] / l, a[1] / l, a[2] / l];
};
const cross = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
const dot = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];

/** Posição do pulso no referencial do modelo. */
export const WRIST = Object.freeze([HAND.forearm.length, 0, 0]);

/** Raio do antebraço num x do modelo (cone arredondado do cotovelo ao pulso). */
export function forearmRadius(x) {
  const t = Math.max(0, Math.min(1, x / HAND.forearm.length));
  return HAND.forearm.elbowRadius + (HAND.forearm.wristRadius - HAND.forearm.elbowRadius) * t;
}

/**
 * Base ortonormal de repouso de um osso cujo +X é `dir`, com o +Y o mais perto possível das costas da mão (+Y).
 * @returns {{x:number[], y:number[], z:number[]}}
 */
export function boneBasis(dir) {
  const x = norm(dir);
  let y = [0, 1, 0];
  y = norm(add(y, scale(x, -dot(y, x))));
  return { x, y, z: cross(x, y) };
}

/**
 * Os 14 ossos em ordem (pai antes do filho): nome, pai, cabeça e ponta no referencial do modelo (repouso), raio da massa
 * em volta e a cadeia (braco, dedo1, dedo2, dedo3, polegar).
 * @returns {Array<{name:string, parent:string|null, head:number[], tail:number[], radius:number, chain:string, dir:number[]}>}
 */
export function handBones() {
  const bones = [];
  const push = (name, parent, head, tail, radius, chain) => {
    bones.push({ name, parent, head, tail, radius, chain, dir: norm([tail[0] - head[0], tail[1] - head[1], tail[2] - head[2]]) });
  };
  const L = HAND.forearm.length;
  push('antebraco', null, [0, 0, 0], [...WRIST], (HAND.forearm.elbowRadius + HAND.forearm.wristRadius) / 2, 'braco');
  const palmFront = add(WRIST, [HAND.palm.center[0] + HAND.palm.half[0], 0, 0]);
  push('mao', 'antebraco', [...WRIST], palmFront, HAND.palm.half[1] + 0.2, 'braco');
  for (const f of HAND.fingers) {
    let head = add(WRIST, f.base);
    let parent = 'mao';
    f.phalanges.forEach((len, i) => {
      const tail = add(head, [len, 0, 0]);
      const name = `${f.id}_${i + 1}`;
      push(name, parent, head, tail, f.radius * (1 - 0.04 * i), f.id);
      parent = name;
      head = tail;
    });
  }
  const t = HAND.thumb;
  const dir = norm(t.dir);
  let head = add(WRIST, t.base);
  let parent = 'mao';
  t.phalanges.forEach((len, i) => {
    const tail = add(head, scale(dir, len));
    const name = `${t.id}_${i + 1}`;
    push(name, parent, head, tail, t.radius * (1 - 0.05 * i), 'polegar');
    parent = name;
    head = tail;
  });
  if (bones.length !== 14) throw new Error(`mão com ${bones.length} ossos (esperado 14)`);
  if (bones[0].tail[0] !== L) throw new Error('antebraço fora do lugar');
  return bones;
}

/**
 * Árvore SDF da mão e do antebraço na pose de repouso (um material só: a massa do boneco). As costuras ficam nos nós
 * dos dedos e no pulso (união suave com vinco); calombos da massa inteira por cima.
 * @returns {object}
 */
export function handTree() {
  const L = HAND.forearm.length;
  const P = HAND.palm;
  const forearm = {
    type: 'roundCone', mat: 0, a: [0, 0, 0], b: [L - 0.35, 0, 0], ra: HAND.forearm.elbowRadius, rb: HAND.forearm.wristRadius,
  };
  const palm = { type: 'roundBox', mat: 0, pos: add(WRIST, P.center), size: [...P.half], r: P.round };
  // Almofada do polegar (tenar): liga a raiz do polegar à palma, como a massa apertada ali.
  const thenar = { type: 'ellipsoid', mat: 0, pos: add(WRIST, [1.25, -0.28, -1.0]), radii: [1.15, 0.66, 0.78] };
  const digits = [...HAND.fingers, HAND.thumb].map((f) => {
    const dir = f.dir ? norm(f.dir) : [1, 0, 0];
    const pts = [add(WRIST, f.base)];
    for (const len of f.phalanges) pts.push(add(pts[pts.length - 1], scale(dir, len)));
    return { type: 'tube', mat: 0, points: pts, radii: pts.map((_, i) => f.radius * (1 - 0.045 * i)) };
  });
  const body = { type: 'smoothUnion', k: HAND.soft, children: [forearm, palm, thenar] };
  const tree = {
    type: 'smoothUnionCrease', k: HAND.knuckleSoft, depth: HAND.crease.depth, width: HAND.crease.width, children: [body, ...digits],
  };
  const { amp, freq, octaves } = HAND.lumps;
  return { type: 'displace', amp, freq, octaves, seed: 'mao-de-massinha', child: tree };
}
