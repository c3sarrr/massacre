// Plantas a lápis da bancada `arsenal` (Fase 4.1; QBP3, QBP13, QBP15 no item 13 do moodboard): uma folha de papel
// creme quadriculado por arma, com o contorno da planta de referência (o `info(id).plan` da biblioteca de armas: a
// planta de tools/blender/refs/<id>.json, ou a ficha da arma realista convertida) em grafite, a linha do eixo em
// traço-ponto (o do cano; na faca, o do cabo), a cota do comprimento com as setas, o nome escrito à caneta e o crédito
// da foto de origem em letra miúda. A planta fica no referencial da arma pela origem dela (`placeReference`: a boca da
// de massinha, a origem da ficha da realista — na faca, a ponta; Fase 4.1c, Tarefa 13), a mesma conta do contorno
// sobreposto à arma na roda. A de massinha sem planta (sem `refs.planta`; nenhuma hoje — a faca de massinha era a única
// e virou a M9 realista na 4.1c) tem na folha a silhueta lateral da própria receita, sombreada a lápis ("desenhada de
// cabeça").

import * as THREE from 'three';
import { RNG } from '../../core/rng.js';
import { drawHandwriting } from '../../clay/set/labelAtlas.js';
import { createSetMaterial } from '../../clay/set/setShader.js';
import { gridFor, placeReference, sideMask } from '../../weapons/model/silhouette.js';
import { recipeWholeTree } from '../../weapons/model/recipe.js';

function sketchPath(g, ring, map, rng, jitter) {
  g.beginPath();
  ring.forEach(([x, y], i) => {
    const [px, py] = map(x, y);
    const jx = rng.float(-jitter, jitter);
    const jy = rng.float(-jitter, jitter);
    if (i === 0) g.moveTo(px + jx, py + jy);
    else g.lineTo(px + jx, py + jy);
  });
  g.closePath();
}

function arrowHead(g, x, y, dir, size) {
  g.beginPath();
  g.moveTo(x, y);
  g.lineTo(x - dir * size, y - size * 0.45);
  g.moveTo(x, y);
  g.lineTo(x - dir * size, y + size * 0.45);
  g.stroke();
}

/**
 * O que a folha desenha, sem o canvas: os anéis da planta no referencial da arma (o contorno e os buracos, pela origem
 * da planta), a área do desenho (a caixa da arma e a da planta juntas, em u) e o crédito da foto.
 * @param {{id:string, info:object, plan:object|null}} item
 * @returns {{rings:number[][][]|null, x0:number, x1:number, y0:number, y1:number, credit:string}}
 */
export function planSheetLayout(item) {
  const box = item.info.bounds;
  let rings = null;
  if (item.plan) {
    const { outline, holes } = placeReference(item.info, item.plan);
    rings = [outline, ...holes];
  }
  let x0 = box.min[0];
  let x1 = box.max[0];
  let y0 = box.min[1];
  let y1 = box.max[1];
  if (rings) {
    for (const [x, y] of rings[0]) {
      x0 = Math.min(x0, x);
      x1 = Math.max(x1, x);
      y0 = Math.min(y0, y);
      y1 = Math.max(y1, y);
    }
  }
  const credit = item.plan
    ? `planta: ${item.plan.source.file.replace(/^File:/, '')} · ${item.plan.source.license} · ${item.plan.source.artist}`
    : 'desenhada de cabeça (sem foto de referência)';
  return { rings, x0, x1, y0, y1, credit };
}

/**
 * Desenha a folha de uma arma num canvas.
 * @param {{id:string, name:string, info:object, plan:object|null, lengthU:number}} item `info` = weaponModels.info(id)
 * @param {object} def ARSENAL.plans
 * @param {string} font fonte da etiqueta (com "{px}")
 * @returns {HTMLCanvasElement}
 */
export function drawPlanSheet(item, def, font) {
  const { width: W, height: H } = def.texture;
  const canvas = document.createElement('canvas');
  canvas.width = W;
  canvas.height = H;
  const g = canvas.getContext('2d');
  const rng = new RNG(`planta:${item.id}`);
  g.fillStyle = def.paper;
  g.fillRect(0, 0, W, H);
  // Papel quadriculado de 5 mm (a folha tem 160 u de largura).
  const cell = (W / 160) * 5;
  g.strokeStyle = def.grid;
  g.lineWidth = 1;
  for (let x = cell; x < W; x += cell) {
    g.beginPath();
    g.moveTo(x, 0);
    g.lineTo(x, H);
    g.stroke();
  }
  for (let y = cell; y < H; y += cell) {
    g.beginPath();
    g.moveTo(0, y);
    g.lineTo(W, y);
    g.stroke();
  }
  // Área do desenho: a arma inteira com margem, escala única nos dois eixos.
  const { rings, x0, x1, y0, y1, credit } = planSheetLayout(item);
  const area = { x: W * 0.07, y: H * 0.2, w: W * 0.86, h: H * 0.56 };
  const s = Math.min(area.w / (x1 - x0), area.h / (y1 - y0));
  const ox = area.x + (area.w - (x1 - x0) * s) / 2;
  const oy = area.y + (area.h + (y1 - y0) * s) / 2;
  const map = (x, y) => [ox + (x - x0) * s, oy - (y - y0) * s];
  g.lineJoin = 'round';
  g.lineCap = 'round';
  g.strokeStyle = def.graphite;
  if (rings) {
    // Grafite: um traço firme e dois de rascunho por cima, com tremor de mão.
    for (const [alpha, widthPx, jitter] of [[0.85, 2.2, 0.4], [0.3, 1.2, 1.6], [0.22, 1, 2.2]]) {
      g.globalAlpha = alpha;
      g.lineWidth = widthPx;
      for (const r of rings) {
        sketchPath(g, r, map, rng, jitter);
        g.stroke();
      }
    }
  } else {
    // Sem planta (a de massinha sem `refs.planta`): a silhueta da receita, sombreada a lápis (tom leve por baixo e
    // hachuras a 45°).
    if (!item.info.recipe) throw new Error(`${item.id}: arma sem planta e sem receita para desenhar a silhueta`);
    const grid = gridFor(x0, y0, x1, y1, Math.max(0.03, (x1 - x0) / 260));
    const mask = sideMask(recipeWholeTree(item.info.recipe), grid);
    const inside = (i, j) => i >= 0 && j >= 0 && i < grid.nx && j < grid.ny && mask[j * grid.nx + i] === 1;
    const cellPx = grid.cell * s;
    g.fillStyle = def.graphite;
    g.globalAlpha = 0.16;
    for (let j = 0; j < grid.ny; j++) {
      for (let i = 0; i < grid.nx; i++) {
        if (!inside(i, j)) continue;
        const [px, py] = map(grid.x0 + i * grid.cell, grid.y0 + (j + 1) * grid.cell);
        g.fillRect(px, py, cellPx + 0.5, cellPx + 0.5);
      }
    }
    g.globalAlpha = 0.45;
    g.lineWidth = 1.2;
    for (let j = 0; j < grid.ny; j++) {
      for (let i = 0; i < grid.nx; i++) {
        if (!inside(i, j) || (i + j) % 4 !== 0) continue;
        const [px, py] = map(grid.x0 + (i + 0.5) * grid.cell, grid.y0 + (j + 0.5) * grid.cell);
        g.beginPath();
        g.moveTo(px - cellPx * 1.6, py + cellPx * 1.6);
        g.lineTo(px + cellPx * 1.6, py - cellPx * 1.6);
        g.stroke();
      }
    }
    // Contorno: as bordas das células de massa que encostam no vazio, com o tremor do lápis.
    g.globalAlpha = 0.85;
    g.lineWidth = 1.8;
    g.beginPath();
    for (let j = 0; j < grid.ny; j++) {
      for (let i = 0; i < grid.nx; i++) {
        if (!inside(i, j)) continue;
        const xa = grid.x0 + i * grid.cell;
        const ya = grid.y0 + j * grid.cell;
        const edges = [[!inside(i, j - 1), [xa, ya], [xa + grid.cell, ya]], [!inside(i, j + 1), [xa, ya + grid.cell], [xa + grid.cell, ya + grid.cell]],
          [!inside(i - 1, j), [xa, ya], [xa, ya + grid.cell]], [!inside(i + 1, j), [xa + grid.cell, ya], [xa + grid.cell, ya + grid.cell]]];
        for (const [open, a, b] of edges) {
          if (!open) continue;
          const [ax, ay] = map(a[0], a[1]);
          const [bx, by] = map(b[0], b[1]);
          g.moveTo(ax + rng.float(-0.3, 0.3), ay + rng.float(-0.3, 0.3));
          g.lineTo(bx, by);
        }
      }
    }
    g.stroke();
  }
  // O eixo em traço-ponto, passando das pontas: o do cano (y = 0 é o eixo do cano no referencial da arma) e, na faca,
  // o do cabo (a origem dela fica no eixo do cabo).
  g.globalAlpha = 0.5;
  g.lineWidth = 1;
  g.setLineDash([14, 5, 3, 5]);
  const [ax0, ay] = map(x0 - 1, 0);
  const [ax1] = map(x1 + 1.5, 0);
  g.beginPath();
  g.moveTo(ax0, ay);
  g.lineTo(ax1, ay);
  g.stroke();
  g.setLineDash([]);
  // Cota do comprimento embaixo.
  const [dx0, dyBase] = map(x0, y0);
  const [dx1] = map(x1, y0);
  const dy = dyBase + H * 0.07;
  g.globalAlpha = 0.75;
  g.lineWidth = 1.3;
  for (const x of [dx0, dx1]) {
    g.beginPath();
    g.moveTo(x, dyBase + 6);
    g.lineTo(x, dy + 8);
    g.stroke();
  }
  g.beginPath();
  g.moveTo(dx0, dy);
  g.lineTo(dx1, dy);
  g.stroke();
  arrowHead(g, dx0, dy, -1, 12);
  arrowHead(g, dx1, dy, 1, 12);
  g.globalAlpha = 1;
  g.fillStyle = def.graphite;
  g.strokeStyle = def.graphite;
  const lengthText = `${item.lengthU.toFixed(1).replace('.', ',')} u`;
  const lx = (dx0 + dx1) / 2 - lengthText.length * H * 0.018;
  drawHandwriting(g, lengthText, { x: lx, baseline: dy - 6, size: H * 0.06, font, rng, stroke: 0.02, wobble: 0.6 });
  // Nome à caneta no alto e o crédito da foto embaixo.
  g.fillStyle = def.ink;
  g.strokeStyle = def.ink;
  drawHandwriting(g, item.name, { x: W * 0.17, baseline: H * 0.155, size: H * 0.11, font, rng });
  g.font = `${Math.round(H * 0.032)}px ui-monospace, "Cascadia Mono", Consolas, monospace`;
  g.fillStyle = def.graphite;
  g.globalAlpha = 0.8;
  g.fillText(credit.length > 96 ? `${credit.slice(0, 93)}…` : credit, W * 0.05, H * 0.95);
  g.globalAlpha = 1;
  return canvas;
}

/** Papel da folha com o desenho: fibras do papel do set por cima da cor, grafite um pouco brilhante contra a luz. */
export function planSheetMaterial(tex, map, name) {
  return createSetMaterial({
    name,
    params: { color: 0xffffff, roughness: 0.88, metalness: 0, side: THREE.DoubleSide },
    uniforms: { uPlan: { value: map }, uPaperTex: { value: tex.paper } },
    light: { wrap: 0.35, lift: 0.08, translucency: 0.25 },
    fragPars: 'uniform sampler2D uPlan;\nuniform sampler2D uPaperTex;',
    surface: /* glsl */ `
vec3 art = texture(uPlan, setUv).rgb;
vec4 pt = texture(uPaperTex, setUv * vec2(3.2, 1.84));
float lum = dot(art, vec3(0.299, 0.587, 0.114));
float graphite = 1.0 - smoothstep(0.35, 0.75, lum);
vec3 col = art * (0.95 + 0.1 * (pt.b - 0.5));
diffuseColor.rgb = col;
setMetal += graphite * 0.25;
setRough += (pt.a - 0.5) * 0.06 - graphite * 0.3;
mat3 tbn = setCotangentFrame(setN, setP, setUv * vec2(3.2, 1.84));
setObjN = normalize(tbn * vec3((pt.rg * 2.0 - 1.0) * 0.25, 1.0));
`,
  });
}
