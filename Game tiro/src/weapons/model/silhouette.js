// Silhueta lateral de uma arma de massinha e a conferência com a planta de referência (Fase 4.1; docs/phases/phase-4.md,
// seção 4.1, "Plantas de referência"). A silhueta é o SDF visto de +Z com o máximo em Z: um ponto (x, y) é massa se
// algum z ali está dentro. A planta (tools/blender/refs/<id>.json) tem a boca do cano em x = 0 e o eixo em y = 0; aqui
// ela é posta na âncora `boca` da receita. Puro (sem three.js): a suíte do Node e a bancada `arsenal` usam o mesmo.

import { bounds, compile } from '../../clay/sdf/nodes.js';
import { recipeWholeTree } from './recipe.js';

/**
 * Grade no plano XY: células de lado `cell` a partir de (x0, y0), `nx` × `ny`; o valor de cada célula é o do centro.
 * @typedef {{x0:number, y0:number, nx:number, ny:number, cell:number}} Grid
 */

/** Grade que cobre uma caixa XY com folga de uma célula. */
export function gridFor(minX, minY, maxX, maxY, cell) {
  const x0 = minX - cell;
  const y0 = minY - cell;
  return { x0, y0, nx: Math.ceil((maxX - x0) / cell) + 1, ny: Math.ceil((maxY - y0) / cell) + 1, cell };
}

/**
 * Máscara da silhueta lateral de uma árvore SDF: raio em Z por célula, avançando pela distância (a árvore é
 * 1-Lipschitz; o fator 0,9 cobre os calombos do `displace`).
 * @param {object} tree
 * @param {Grid} grid
 * @returns {Uint8Array} nx × ny (linha a linha, y crescente)
 */
export function sideMask(tree, grid) {
  const b = bounds(tree);
  const { distance } = compile(tree);
  const { x0, y0, nx, ny, cell } = grid;
  const mask = new Uint8Array(nx * ny);
  for (let j = 0; j < ny; j++) {
    const y = y0 + (j + 0.5) * cell;
    if (y < b.min[1] - cell || y > b.max[1] + cell) continue;
    for (let i = 0; i < nx; i++) {
      const x = x0 + (i + 0.5) * cell;
      if (x < b.min[0] - cell || x > b.max[0] + cell) continue;
      if (hitAlongZ(distance, x, y, b, cell)) mask[j * nx + i] = 1;
    }
  }
  return mask;
}

/** Algum z em (x, y) está dentro da massa? Avança pela distância (o fator 0,9 cobre os calombos do `displace`). */
function hitAlongZ(distance, x, y, b, cell) {
  const minStep = cell * 0.25;
  const z1 = b.max[2] + cell;
  let z = b.min[2] - cell;
  while (z <= z1) {
    const d = distance(x, y, z);
    if (d < 0) return true;
    z += Math.max(d * 0.9, minStep);
  }
  return false;
}

/**
 * Máscara de um polígono com buracos (par/ímpar: o contorno e os buracos juntos), por varredura de linhas.
 * @param {number[][]} outline pontos [x, y]
 * @param {number[][][]} holes
 * @param {Grid} grid
 * @returns {Uint8Array}
 */
export function polygonMask(outline, holes, grid) {
  const { x0, y0, nx, ny, cell } = grid;
  const mask = new Uint8Array(nx * ny);
  const rings = [outline, ...(holes ?? [])];
  const xs = [];
  for (let j = 0; j < ny; j++) {
    const y = y0 + (j + 0.5) * cell;
    xs.length = 0;
    for (const ring of rings) {
      for (let k = 0, n = ring.length; k < n; k++) {
        const [ax, ay] = ring[k];
        const [bx, by] = ring[(k + 1) % n];
        if ((ay > y) !== (by > y)) xs.push(ax + ((y - ay) / (by - ay)) * (bx - ax));
      }
    }
    xs.sort((a, b) => a - b);
    for (let k = 0; k + 1 < xs.length; k += 2) {
      const i0 = Math.max(0, Math.ceil((xs[k] - x0) / cell - 0.5));
      const i1 = Math.min(nx - 1, Math.floor((xs[k + 1] - x0) / cell - 0.5));
      for (let i = i0; i <= i1; i++) mask[j * nx + i] = 1;
    }
  }
  return mask;
}

/**
 * A planta no referencial da arma: o (0, 0) da planta (a boca do cano; na faca, a ponta) vai para a origem da planta do
 * `info` (`planOrigin`: a âncora `boca` da de massinha, a origem da ficha da realista) ou, numa receita, para a âncora
 * `boca` dela. Sem nenhuma das duas, erro (a planta não tem onde ficar).
 * @param {{planOrigin?:number[]|null, anchors?:object, id?:string}} owner o `info` da arma, ou a receita
 */
export function placeReference(owner, ref) {
  const origem = owner.planOrigin ?? owner.anchors?.boca?.pos;
  if (!origem) throw new Error(`${owner.id ?? ref.weapon ?? 'arma'}: a planta sem origem (nem planOrigin nem a âncora boca)`);
  const shift = (p) => [p[0] + origem[0], p[1] + origem[1]];
  return { outline: ref.points.map(shift), holes: (ref.holes ?? []).map((h) => h.map(shift)) };
}

/**
 * IoU da silhueta lateral da receita com a planta (aceite da 4.1: ≥ 0,8), e as áreas em u².
 * @param {object} recipe
 * @param {object} ref planta (tools/blender/refs/<id>.json)
 * @param {{cell?:number}} [options]
 * @returns {{iou:number, sdfArea:number, refArea:number, interArea:number, grid:Grid, sdf:Uint8Array, plan:Uint8Array}}
 */
export function silhouetteIoU(recipe, ref, { cell = 0.1 } = {}) {
  const tree = recipeWholeTree(recipe);
  const b = bounds(tree);
  const { outline, holes } = placeReference(recipe, ref);
  let minX = b.min[0];
  let minY = b.min[1];
  let maxX = b.max[0];
  let maxY = b.max[1];
  for (const [x, y] of outline) {
    minX = Math.min(minX, x);
    minY = Math.min(minY, y);
    maxX = Math.max(maxX, x);
    maxY = Math.max(maxY, y);
  }
  const grid = gridFor(minX, minY, maxX, maxY, cell);
  const sdf = sideMask(tree, grid);
  const plan = polygonMask(outline, holes, grid);
  let a = 0;
  let r = 0;
  let both = 0;
  for (let k = 0; k < sdf.length; k++) {
    a += sdf[k];
    r += plan[k];
    both += sdf[k] & plan[k];
  }
  const union = a + r - both;
  const c2 = cell * cell;
  return { iou: union > 0 ? both / union : 0, sdfArea: a * c2, refArea: r * c2, interArea: both * c2, grid, sdf, plan };
}

/**
 * Comprimento real da arma (u): a extensão em X da silhueta lateral, sem a folga da caixa envolvente (calombos e
 * arredondados). É o número da tabela de escala (docs/phases/phase-4.md, "Unidades e escala"). Só as colunas das pontas
 * são varridas, de fora para dentro, até a primeira com massa (a mesma grade da silhueta inteira, bem mais rápido).
 */
export function silhouetteLength(recipe, { cell = 0.05 } = {}) {
  const tree = recipeWholeTree(recipe);
  const b = bounds(tree);
  const { distance } = compile(tree);
  const grid = gridFor(b.min[0], b.min[1], b.max[0], b.max[1], cell);
  const column = (i) => {
    const x = grid.x0 + (i + 0.5) * cell;
    if (x < b.min[0] - cell || x > b.max[0] + cell) return false;
    for (let j = 0; j < grid.ny; j++) {
      const y = grid.y0 + (j + 0.5) * cell;
      if (y < b.min[1] - cell || y > b.max[1] + cell) continue;
      if (hitAlongZ(distance, x, y, b, cell)) return true;
    }
    return false;
  };
  let i0 = 0;
  while (i0 < grid.nx && !column(i0)) i0++;
  if (i0 === grid.nx) return 0;
  let i1 = grid.nx - 1;
  while (i1 > i0 && !column(i1)) i1--;
  return (i1 - i0 + 1) * cell;
}
