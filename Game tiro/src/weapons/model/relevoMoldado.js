// Relevo moldado das armas realistas (correções da P1 da 4.1c; plano da 4.1c, P1.1 e P1.2): o tipo de textura do molde
// de cada texel (src/data/acabamentos.js, RELEVOS_MOLDADOS) vai no alfa do `_n` — 255 no liso, 255 − 32·id nos
// relevos —, assado pelo Blender (tools/blender/armas/relevo.py) e lido pelo shader (glsl/acabamentos.js). Aqui as
// contas puras, as mesmas dos dois lados: o alfa de um tipo e o tipo de um alfa, com o peso que some na borda da região
// (o filtro da textura mistura o liso com o tipo, e o meio da mistura não pode virar um terceiro tipo com força).

import { RELEVOS_MOLDADOS } from '../../data/acabamentos.js';

export const RELEVO_DEGRAU = 32;

const POR_ID = new Map(Object.values(RELEVOS_MOLDADOS).map((r) => [r.id, r]));
const MAIOR_ID = Math.max(...POR_ID.keys());

/** A definição do tipo (null no liso, id 0). */
export function relevoPorId(id) {
  return POR_ID.get(id) ?? null;
}

/** O alfa do `_n` (0 a 1) de um tipo: 1 no liso, (255 − 32·id)/255 nos outros. */
export function alfaDoRelevo(id) {
  if (id !== 0 && !POR_ID.has(id)) throw new Error(`relevo moldado desconhecido: ${id}`);
  return (255 - RELEVO_DEGRAU * id) / 255;
}

/**
 * O tipo de um alfa lido da textura (0 a 1) e o peso: 1 até 0,1 degrau do valor do tipo, caindo a 0 no meio do
 * caminho para o vizinho (a borda filtrada de uma região).
 * @returns {{id:number, peso:number}}
 */
export function relevoDoAlfa(alfa) {
  const k = ((1 - alfa) * 255) / RELEVO_DEGRAU;
  const id = Math.round(k);
  if (id <= 0 || id > MAIOR_ID) return { id: 0, peso: 0 };
  return { id, peso: Math.min(1, Math.max(0, (0.5 - Math.abs(k - id)) / 0.4)) };
}
