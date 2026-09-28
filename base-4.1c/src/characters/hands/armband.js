// Cor da braçadeira do time (Fase 4.1; docs/phases/phase-4.md, seção 4.1, "Mãos de 4 dedos", e seção 0.12): a cor do
// time que mais se destaca da massa do braço, pela diferença de cor ΔE (CIE76, em L*a*b* D65). Puro: o viewmodel usa
// agora, os bonecos da Fase 5 (com a cor do criador) depois, e os testes do Node conferem.

import { ARMBAND } from '../../data/hands.js';
import { TEAM_COLORS } from '../../data/palette.js';

const srgbToLinear = (c) => (c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4);
const labF = (t) => (t > 216 / 24389 ? Math.cbrt(t) : (t * 24389) / 27 / 116 + 16 / 116);

/** '#RRGGBB' → [L, a, b] (D65). */
export function hexToLab(hex) {
  const m = /^#?([0-9a-f]{6})$/i.exec(hex);
  if (!m) throw new Error(`cor inválida: ${hex}`);
  const n = parseInt(m[1], 16);
  const r = srgbToLinear(((n >> 16) & 255) / 255);
  const g = srgbToLinear(((n >> 8) & 255) / 255);
  const b = srgbToLinear((n & 255) / 255);
  const x = (0.4124564 * r + 0.3575761 * g + 0.1804375 * b) / 0.95047;
  const y = 0.2126729 * r + 0.7151522 * g + 0.072175 * b;
  const z = (0.0193339 * r + 0.119192 * g + 0.9503041 * b) / 1.08883;
  const fx = labF(x);
  const fy = labF(y);
  const fz = labF(z);
  return [116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz)];
}

/** Diferença de cor ΔE (CIE76) entre duas cores '#RRGGBB'. */
export function deltaE(hexA, hexB) {
  const [l1, a1, b1] = hexToLab(hexA);
  const [l2, a2, b2] = hexToLab(hexB);
  return Math.hypot(l1 - l2, a1 - a2, b1 - b2);
}

/**
 * Cor da braçadeira de um time sobre um braço de massa `armColor`, ou null sem time.
 * @param {'tr'|'ct'|null} team
 * @param {string} armColor '#RRGGBB'
 * @returns {string|null}
 */
export function armbandColor(team, armColor) {
  const colors = team ? TEAM_COLORS[team] : null;
  if (!colors) return null;
  let best = null;
  let bestDelta = -1;
  for (const key of ARMBAND.colors) {
    const c = colors[key];
    const d = deltaE(c, armColor);
    if (d >= ARMBAND.minDelta) return c;
    if (d > bestDelta) {
      best = c;
      bestDelta = d;
    }
  }
  return best;
}
