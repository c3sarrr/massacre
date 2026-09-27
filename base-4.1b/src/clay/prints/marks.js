// Marcas das pegadas (subfase 3.5; números em src/data/footprints.js; referências no item 12 do moodboard): o que cada
// evento do movimento deixa na massinha — o pé do passo, o par do pouso, o par da saída do pulo, os sulcos do slide e o
// montinho do fim —, a passagem para o referencial de uma peça de chão e o valor de cada texel do mapa de pegadas (R
// fundo, G lábio, B massa fresca) em inteiros de 8 bits, com o esmaecimento. É a mesma conta que a GPU faz ao carimbar
// (src/clay/prints/stampPass.js); no navegador as duas são comparadas texel a texel. Puro (sem WebGL). Referencial de
// uma marca de pé: `a` ao longo do pé (para o bico) e `b` para a direita do pé; a sola usa bi = b × inner (o lado de
// dentro positivo: +1 no pé esquerdo, −1 no direito).

import { FOOTPRINTS, SOLE } from '../../data/footprints.js';
import { smoothstep, soleCleats, soleDistance } from './sole.js';

const FP = FOOTPRINTS;
const LR = FP.lipRing;
const DEG = Math.PI / 180;

export const MARK = Object.freeze({ FOOT: 0, GROOVE: 1, MOUND: 2 });

/** Alcance do lábio (u além da borda): a gaussiana vale ~0 a partir daqui. */
export const LIP_REACH = LR.offset + 3 * LR.width;

const clamp01 = (v) => (v < 0 ? 0 : v > 1 ? 1 : v);

/** Valor de 0–1 no inteiro de 8 bits do mapa (o arredondamento da GPU ao gravar no alvo RGBA8). */
export const q8 = (v) => Math.round(clamp01(v) * 255);

/** Gaussiana do lábio a `d` u fora da borda. */
function lipRing(d) {
  const t = (d - LR.offset) / LR.width;
  return Math.exp(-t * t);
}

/**
 * Marca de um pé no mundo: pés do jogador em (x, y, z), olhar `yaw`, `foot` (0 esquerdo, 1 direito) e a especificação
 * (FOOTPRINTS.marks.step/land/jump): o pé a ±offset do centro no eixo direito do olhar, virado para a frente do olhar
 * com o bico `toeOutDeg` para fora; `heel`/`front` (pulo): o fundo cresce do calcanhar ao bico.
 */
export function footMark(x, y, z, yaw, foot, { offset, toeOutDeg, strength, heel = 1, front = 1 }) {
  const fx = -Math.sin(yaw);
  const fz = -Math.cos(yaw);
  const rx = Math.cos(yaw);
  const rz = -Math.sin(yaw);
  const side = foot === 0 ? -1 : 1;
  const turn = side * toeOutDeg * DEG; // esquerdo gira para a esquerda, direito para a direita
  const c = Math.cos(turn);
  const s = Math.sin(turn);
  return {
    kind: MARK.FOOT, x: x + rx * side * offset, y, z: z + rz * side * offset,
    dx: fx * c + rx * s, dz: fz * c + rz * s, inner: foot === 0 ? 1 : -1, strength, heel, front,
  };
}

/** O par de pés lado a lado (pouso, saída do pulo). */
export function footPair(x, y, z, yaw, spec) {
  return [footMark(x, y, z, yaw, 0, spec), footMark(x, y, z, yaw, 1, spec)];
}

/**
 * Sulcos de calcanhar do slide de (x0, z0) a (x1, z1): dois segmentos a ±offset da trajetória, com a meia largura e a
 * força do slide. Sem deslocamento, nenhum.
 */
export function grooveMarks(x0, z0, x1, z1, y, spec = FP.marks.slide) {
  const len = Math.hypot(x1 - x0, z1 - z0);
  if (len < 1e-6) return [];
  const dx = (x1 - x0) / len;
  const dz = (z1 - z0) / len;
  return [-1, 1].map((side) => ({
    kind: MARK.GROOVE, x: x0 - dz * side * spec.offset, y, z: z0 + dx * side * spec.offset, dx, dz, length: len,
    halfWidth: spec.halfWidth, strength: spec.strength,
  }));
}

/** Montinho de massa empurrada à frente dos pés no fim do slide (direção unitária dx, dz), da força dos sulcos. */
export function moundMark(x, y, z, dx, dz, spec = FP.marks.slide) {
  return {
    kind: MARK.MOUND, x: x + dx * spec.moundAhead, y, z: z + dz * spec.moundAhead, dx, dz, radius: spec.moundRadius,
    strength: spec.strength,
  };
}

/**
 * A marca no referencial de uma peça: `inv` = elementos (coluna a coluna) da inversa da matriz de mundo dela. Posição
 * (inclusive o y dos pés, para comparar com o topo da peça) e direção no XZ do objeto; o resto copiado. Escreve em
 * `out`.
 */
export function toLocal(m, inv, out = {}) {
  Object.assign(out, m);
  out.x = inv[0] * m.x + inv[4] * m.y + inv[8] * m.z + inv[12];
  out.y = inv[1] * m.x + inv[5] * m.y + inv[9] * m.z + inv[13];
  out.z = inv[2] * m.x + inv[6] * m.y + inv[10] * m.z + inv[14];
  const dx = inv[0] * m.dx + inv[8] * m.dz;
  const dz = inv[2] * m.dx + inv[10] * m.dz;
  const n = Math.hypot(dx, dz) || 1;
  out.dx = dx / n;
  out.dz = dz / n;
  return out;
}

/** Retângulo da marca no plano dela [x0, z0, x1, z1] (quanto o carimbo cobre). */
export function markBounds(m, out = [0, 0, 0, 0]) {
  let r;
  if (m.kind === MARK.FOOT) r = FP.footReach;
  else if (m.kind === MARK.MOUND) r = m.radius;
  else r = m.halfWidth + Math.max(LIP_REACH, FP.freshReach);
  const x1 = m.kind === MARK.GROOVE ? m.x + m.dx * m.length : m.x;
  const z1 = m.kind === MARK.GROOVE ? m.z + m.dz * m.length : m.z;
  out[0] = Math.min(m.x, x1) - r;
  out[1] = Math.min(m.z, z1) - r;
  out[2] = Math.max(m.x, x1) + r;
  out[3] = Math.max(m.z, z1) + r;
  return out;
}

/** Fundo máximo da marca (0–1): o lábio nunca passa dele. */
export function markPeak(m) {
  return clamp01(m.kind === MARK.FOOT ? m.strength * Math.max(m.heel, m.front) : m.strength);
}

/** Poses até a marca sumir inteira: o fundo máximo (e o lábio, que não passa dele) e o brilho, cada um no seu ritmo. */
export function markLife(m) {
  const f = FP.fade;
  const peak = q8(markPeak(m));
  return Math.max(Math.ceil(peak / f.depth), Math.ceil(peak / f.lip), Math.ceil(255 / f.fresh));
}

/**
 * Valor do mapa (R, G, B em 0–255) que a marca `m` (no plano dela) carimba no ponto (x, z), já com `fades` poses de
 * esmaecimento. A GPU faz a mesma conta (stampPass.js).
 */
export function markTexel(m, x, z, fades = 0, out = [0, 0, 0]) {
  let r = 0;
  let g = 0;
  let b = 0;
  const peak = markPeak(m);
  const px = x - m.x;
  const pz = z - m.z;
  if (m.kind === MARK.FOOT) {
    const a = px * m.dx + pz * m.dz;
    const bi = (pz * m.dx - px * m.dz) * m.inner;
    const d = soleDistance(a, bi);
    const push = m.heel + (m.front - m.heel) * smoothstep(SOLE.heel.a, SOLE.toe.a, a);
    r = smoothstep(0, FP.wall, -d) * soleCleats(a, bi) * m.strength * push;
    if (d > 0) {
      const front = 1 + LR.front * smoothstep(LR.frontFrom, LR.frontTo, a);
      g = Math.min(peak, lipRing(d) * front * m.strength * LR.gain);
    }
    b = d < FP.freshReach ? 1 : 0;
  } else if (m.kind === MARK.GROOVE) {
    const t = Math.min(m.length, Math.max(0, px * m.dx + pz * m.dz));
    const d = Math.hypot(px - m.dx * t, pz - m.dz * t) - m.halfWidth;
    r = smoothstep(0, FP.wall, -d) * m.strength;
    if (d > 0) g = Math.min(peak, lipRing(d) * m.strength * LR.gain);
    b = d < FP.freshReach ? 1 : 0;
  } else {
    const k = 1 - (px * px + pz * pz) / (m.radius * m.radius);
    if (k > 0) {
      g = m.strength * k * k;
      b = 1;
    }
  }
  const f = FP.fade;
  out[0] = Math.max(0, q8(r) - fades * f.depth);
  out[1] = Math.max(0, q8(g) - fades * f.lip);
  out[2] = Math.max(0, q8(b) - fades * f.fresh);
  return out;
}

/** Um texel já no mapa depois de `fades` poses de esmaecimento (a subtração reversa da GPU, em 8 bits). */
export function fadeTexel(rgb, fades, out = [0, 0, 0]) {
  const f = FP.fade;
  out[0] = Math.max(0, rgb[0] - fades * f.depth);
  out[1] = Math.max(0, rgb[1] - fades * f.lip);
  out[2] = Math.max(0, rgb[2] - fades * f.fresh);
  return out;
}

/** Rastro entre ticks: o slide no chão do tick anterior (os pés no fim do último sulco e a direção dele). */
export function createPrintTrack() {
  return { sliding: false, x: 0, y: 0, z: 0, dx: 0, dz: 0 };
}

export function resetPrintTrack(t) {
  t.sliding = false;
  return t;
}

/**
 * Marcas do tick no mundo (em `out`), de quem está vivo e fora do noclip: `s` = estado de movimento depois do
 * playerMove, `from` = a origem no começo do tick (a do pulo e o começo do sulco), `events` = os do tick, `yaw` = o
 * olhar. Passo: o pé do evento, onde ele estava; pouso (acima de `minFall`): o par onde parou; pulo: o par de onde
 * saiu; slide no chão: os dois sulcos do tick; fim do slide depois de um tick no chão: o montinho à frente.
 */
export function tickMarks(t, s, from, events, yaw, out = []) {
  const M = FP.marks;
  out.length = 0;
  const o = s.origin;
  for (let i = 0; i < events.length; i++) {
    const e = events[i];
    if (e.type === 'step') out.push(footMark(e.x, e.y, e.z, yaw, e.foot, M.step));
    else if (e.type === 'land' && e.speed >= M.land.minFall) out.push(...footPair(o.x, o.y, o.z, yaw, M.land));
    else if (e.type === 'jump') out.push(...footPair(from.x, from.y, from.z, yaw, M.jump));
    else if (e.type === 'slide' && e.phase === 'end' && t.sliding) out.push(moundMark(t.x, t.y, t.z, t.dx, t.dz));
  }
  if (s.sliding && s.onGround) {
    const grooves = grooveMarks(from.x, from.z, o.x, o.z, o.y);
    if (grooves.length) {
      out.push(...grooves);
      t.dx = grooves[0].dx;
      t.dz = grooves[0].dz;
    }
    t.sliding = t.sliding || grooves.length > 0;
    t.x = o.x;
    t.y = o.y;
    t.z = o.z;
  } else t.sliding = false;
  return out;
}
