// Bota de massinha com cravos (subfase 3.5; números em src/data/referenceDoll.js; referências no item 12 do moodboard:
// PFT4 pés de massa de sola chata, AAC1/AAC6 botas escuras de bico redondo, FIM22 sola de cravos). O contorno é a sola
// das pegadas (src/clay/prints/sole.js): a bota pisa na massa e deixa a marca da própria sola. Extrusão do contorno com
// as bordas de cima e da sola arredondadas, cravos em relevo embaixo (barras transversais na frente, ao comprido no
// calcanhar, arco liso) e o acabamento do kit (calombos, aTouch, aSeam para a costura com o corpo). Referencial da
// peça: +Z para o bico, Y para cima (sola dos cravos em y = 0), X para o lado — o lado de dentro é −X no pé esquerdo
// (que fica em +X no boneco) e +X no direito.

import * as THREE from 'three';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';
import { SOLE } from '../../data/footprints.js';
import { REFERENCE_DOLL } from '../../data/referenceDoll.js';
import { SOLE_EXTENT, smoothstep, soleDistance } from '../prints/sole.js';
import { finalizeClayGeometry, sculpt, weld } from './sculpt.js';

const B = REFERENCE_DOLL.boots;
const C = SOLE.cleats;

/** Ponto (a, bi) do raio que sai de (ca, cb) na direção (da, db) onde a distância à sola vale −inset (bisseção). */
function isoPoint(ca, cb, da, db, inset) {
  let lo = 0;
  let hi = SOLE_EXTENT.length;
  for (let i = 0; i < 48; i++) {
    const t = (lo + hi) / 2;
    if (soleDistance(ca + da * t, cb + db * t) + inset < 0) lo = t;
    else hi = t;
  }
  const t = (lo + hi) / 2;
  return [ca + da * t, cb + db * t];
}

/**
 * Contorno da sola recuado `inset` u, com `n` pontos igualmente espaçados ao longo dele, em (a, bi), no sentido de a
 * para bi (anti-horário no plano a × bi). O contorno é estrelado a partir do meio do pé: raios dali o cruzam uma vez.
 */
export function soleOutline(inset = 0, n = B.outline) {
  const ca = (SOLE.heel.a + SOLE.toe.a) / 2;
  const cb = SOLE.inward / 2;
  const m = n * 8;
  const dense = [];
  for (let i = 0; i < m; i++) {
    const th = (i / m) * Math.PI * 2;
    dense.push(isoPoint(ca, cb, Math.cos(th), Math.sin(th), inset));
  }
  const cum = [0];
  for (let i = 1; i <= m; i++) {
    const p = dense[i % m];
    const q = dense[i - 1];
    cum.push(cum[i - 1] + Math.hypot(p[0] - q[0], p[1] - q[1]));
  }
  const out = [];
  let j = 0;
  for (let k = 0; k < n; k++) {
    const s = (k / n) * cum[m];
    while (cum[j + 1] < s) j++;
    const t = (s - cum[j]) / (cum[j + 1] - cum[j]);
    const p = dense[j];
    const q = dense[(j + 1) % m];
    out.push([p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t]);
  }
  return out;
}

/** Trecho [lo, hi] de uma reta dentro da sola recuada `inset`: `at(t)` → (a, bi); bisseção a partir de `mid`. */
function span(at, mid, reach, inset) {
  const inside = (t) => {
    const [a, bi] = at(t);
    return soleDistance(a, bi) + inset < 0;
  };
  if (!inside(mid)) return null;
  const edge = (dir) => {
    let lo = 0;
    let hi = reach;
    for (let i = 0; i < 40; i++) {
      const t = (lo + hi) / 2;
      if (inside(mid + dir * t)) lo = t;
      else hi = t;
    }
    return mid + dir * lo;
  };
  return [edge(-1), edge(1)];
}

/**
 * Barras dos cravos em (a, bi): retângulos {a0, a1, b0, b1} dentro da sola recuada `inset` — na frente, faixas de a
 * (de `front.from` ao corte) com a largura da sola; no calcanhar, faixas de bi (até `heel.to`). Os mesmos intervalos do
 * fundo das pegadas (soleCleats).
 */
export function cleatBars(inset = B.cleatInset) {
  const bars = [];
  const minLength = 0.6;
  const fp = C.front.pitch;
  for (let n = Math.floor((C.front.from + C.phase) / fp); n * fp - C.phase < SOLE.cut; n++) {
    const a0 = Math.max(n * fp - C.phase, C.front.from);
    const a1 = Math.min(n * fp - C.phase + C.front.duty * fp, SOLE.cut - inset);
    if (a1 - a0 < 0.3) continue;
    const am = (a0 + a1) / 2;
    const centre = SOLE.inward * smoothstep(SOLE.heel.a, SOLE.toe.a, am);
    const s = span((t) => [am, t], centre, SOLE_EXTENT.half + 1, inset);
    if (s && s[1] - s[0] >= minLength) bars.push({ a0, a1, b0: s[0], b1: s[1] });
  }
  const hp = C.heel.pitch;
  for (let n = Math.floor((-SOLE_EXTENT.half + C.phase) / hp); n * hp - C.phase < SOLE_EXTENT.half; n++) {
    const b0 = n * hp - C.phase;
    const b1 = b0 + C.heel.duty * hp;
    const bm = (b0 + b1) / 2;
    const s = span((t) => [t, bm], SOLE.heel.a, SOLE_EXTENT.length, inset);
    if (!s) continue;
    const a1 = Math.min(s[1], C.heel.to);
    if (a1 - s[0] >= minLength) bars.push({ a0: s[0], a1, b0, b1 });
  }
  return bars;
}

/**
 * Bota de massinha. `foot`: 'left' ou 'right'; `scale`: altura do boneco ÷ 72. Devolve { geometry, radius, distance }
 * como as primitivas do kit (distance: SDF aproximado no espaço da peça, para a costura com o corpo).
 */
export function clayBoot({ foot = 'left', scale = 1, seed = 17 } = {}) {
  const side = foot === 'left' ? -1 : 1; // x = side × bi
  const round = B.round;
  const shell = B.height - B.cleatHeight;
  // Casco: o contorno recuado do raio das bordas, extrudado com bisel redondo (o bisel devolve o contorno inteiro).
  const shape = new THREE.Shape(soleOutline(round).map(([a, bi]) => new THREE.Vector2(side * bi, -a)));
  const hull = new THREE.ExtrudeGeometry(shape, {
    depth: Math.max(0.1, shell - 2 * round), steps: 2, bevelEnabled: true, bevelThickness: round, bevelSize: round,
    bevelSegments: 3, curveSegments: 1,
  });
  hull.rotateX(-Math.PI / 2); // (x, −a, z) → (x, z, a): extrusão para cima, bico em +Z
  hull.translate(0, B.cleatHeight + round, 0);
  const parts = [hull]; // a extrusão e as barras saem sem índice (mergeGeometries pede o mesmo formato)
  // Cravos: barras de canto arredondado embaixo da sola, entrando um pouco no casco.
  const h = B.cleatHeight + 0.15;
  for (const bar of cleatBars()) {
    const w = bar.b1 - bar.b0;
    const l = bar.a1 - bar.a0;
    const g = new RoundedBoxGeometry(w, h, l, 2, Math.min(0.2, w / 2 - 0.01, l / 2 - 0.01));
    g.translate(side * (bar.b0 + bar.b1) / 2, h / 2, (bar.a0 + bar.a1) / 2);
    parts.push(g);
  }
  const merged = mergeGeometries(parts, false);
  for (const p of parts) p.dispose();
  if (!merged) throw new Error('não foi possível fundir a bota');
  if (scale !== 1) merged.scale(scale, scale, scale);
  const radius = Math.hypot(SOLE_EXTENT.length / 2 + 0.4, B.height) * scale;
  const geometry = finalizeClayGeometry(sculpt(weld(merged), {
    seed, radius, lumpiness: 0.012, lumpFreq: 1.1, dents: 1, dentDepth: 0.02, dentRadius: 0.25,
  }));
  const H = B.height * scale;
  return {
    geometry,
    radius,
    // Extrusão da sola (o contorno no plano, de y = 0 a y = H).
    distance: (p) => {
      const d2 = soleDistance(p.z / scale, (side * p.x) / scale) * scale;
      const dy = Math.max(-p.y, p.y - H);
      return Math.hypot(Math.max(d2, 0), Math.max(dy, 0)) + Math.min(Math.max(d2, dy), 0);
    },
  };
}
