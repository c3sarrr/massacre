// Sola da bota com cravos (subfase 3.5; números em src/data/footprints.js): a distância assinada ao contorno da sola e
// o fundo relativo dos cravos, em JS e em GLSL gerado dos mesmos números (o mapa de pegadas é desenhado na GPU e
// conferido texel a texel com o JS). Referencial do pé: `a` ao longo do pé (positivo para o bico) e `bi` para o lado de
// dentro (o do dedão) — pé esquerdo e direito são espelhos. As botas do boneco de referência (src/clay/kit/boots.js)
// são moldadas no mesmo contorno. Contorno: "cápsula desigual" entre o círculo do calcanhar e o do bico (tangentes
// externas; a do bico desvia para dentro ao longo do pé), cortada reta na ponta.

import { SOLE } from '../../data/footprints.js';

const H = SOLE.heel;
const T = SOLE.toe;
const LEN = T.a - H.a;
const K0 = (H.radius - T.radius) / LEN;
const K1 = Math.sqrt(1 - K0 * K0);
const C = SOLE.cleats;

const clamp01 = (v) => (v < 0 ? 0 : v > 1 ? 1 : v);

/** smoothstep do GLSL (e0 < e1). */
export function smoothstep(e0, e1, x) {
  const t = clamp01((x - e0) / (e1 - e0));
  return t * t * (3 - 2 * t);
}

const fract = (v) => v - Math.floor(v);

/** Distância assinada (u) de (a, bi) ao contorno da sola: negativa dentro. */
export function soleDistance(a, bi) {
  const px = Math.abs(bi - SOLE.inward * smoothstep(H.a, T.a, a));
  const py = a - H.a;
  const k = -K0 * px + K1 * py;
  let d;
  if (k < 0) d = Math.hypot(px, py) - H.radius;
  else if (k > K1 * LEN) d = Math.hypot(px, py - LEN) - T.radius;
  else d = K1 * px + K0 * py - H.radius;
  return Math.max(d, a - SOLE.cut);
}

/** Fundo relativo da marca pelos cravos em (a, bi): 1 nas barras, `gap` entre elas, `arch` no arco. */
export function soleCleats(a, bi) {
  if (a > C.front.from) return fract((a + C.phase) / C.front.pitch) < C.front.duty ? 1 : C.front.gap;
  if (a < C.heel.to) return fract((bi + C.phase) / C.heel.pitch) < C.heel.duty ? 1 : C.heel.gap;
  return C.arch;
}

/** Limites da sola no referencial do pé: calcanhar, ponta (o corte) e meia largura (o bico). */
export const SOLE_EXTENT = Object.freeze({
  back: H.a - H.radius,
  front: SOLE.cut,
  half: Math.max(H.radius, T.radius) + SOLE.inward,
  length: SOLE.cut - (H.a - H.radius),
  width: 2 * Math.max(H.radius, T.radius),
  nominalLength: T.a + T.radius - (H.a - H.radius),
});

/** Número JS como literal float do GLSL (os shaders das pegadas saem dos mesmos números do JS). */
export function glslFloat(v) {
  const s = String(v);
  return s.includes('.') || s.includes('e') ? s : `${s}.0`;
}

const f = glslFloat;

/** GLSL das mesmas funções: `float soleDistance(vec2 p)` e `float soleCleats(vec2 p)` com p = (a, bi). */
export const SOLE_GLSL = /* glsl */ `
float soleDistance(vec2 p) {
  float px = abs(p.y - ${f(SOLE.inward)} * smoothstep(${f(H.a)}, ${f(T.a)}, p.x));
  float py = p.x - (${f(H.a)});
  float k = ${f(-K0)} * px + ${f(K1)} * py;
  float d;
  if (k < 0.0) d = length(vec2(px, py)) - ${f(H.radius)};
  else if (k > ${f(K1 * LEN)}) d = length(vec2(px, py - ${f(LEN)})) - ${f(T.radius)};
  else d = ${f(K1)} * px + ${f(K0)} * py - ${f(H.radius)};
  return max(d, p.x - ${f(SOLE.cut)});
}
float soleCleats(vec2 p) {
  if (p.x > ${f(C.front.from)}) {
    return fract((p.x + ${f(C.phase)}) / ${f(C.front.pitch)}) < ${f(C.front.duty)} ? 1.0 : ${f(C.front.gap)};
  }
  if (p.x < ${f(C.heel.to)}) {
    return fract((p.y + ${f(C.phase)}) / ${f(C.heel.pitch)}) < ${f(C.heel.duty)} ? 1.0 : ${f(C.heel.gap)};
  }
  return ${f(C.arch)};
}
`;
