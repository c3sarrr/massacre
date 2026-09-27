// Forma `tronco` das árvores SDF (Fase 4.1b; desenho em docs/superpowers/specs/2026-09-26-4.1b-luvas-e-empunhadura-
// design.md, seção 5): um tronco ao longo do eixo X local cuja seção é um retângulo arredondado que muda de tamanho de
// uma seção para a outra — o antebraço de massinha que entra no punho da luva (achatado no pulso na largura da ficha,
// mais largo e mais redondo no cotovelo) e a braçadeira em volta dele. Cada seção é [x, largura (ao longo de Z),
// espessura (ao longo de Y), raio do canto]; entre duas seções os quatro números variam em linha reta, e fora das
// pontas vale a seção da ponta. As pontas são arredondadas com `round`, como o perfil extrudado (opExtrusion
// arredondado de iq). A distância ao retângulo arredondado é a exata de iq (sdRoundBox 2D); como a seção muda com x, a
// distância é dividida pelo pior fator de Lipschitz dos trechos (√(1 + g²), g = a soma das inclinações das meias
// medidas e do raio), e a forma continua 1-Lipschitz para a poda e os intervalos do SdfMesher — a superfície (o zero) é
// a mesma.
// Puro: a leitura valida o nó e devolve a distância no espaço local; shapes.js aplica a transformação e o material, e
// bounds.js usa o suporte.

import { MAX_POINTS, MIN_EDGE, fail, readNonNegative } from './params.js';

/**
 * Lê e valida um nó `tronco`.
 * @returns {{secoes:number[][], x0:number, x1:number, rd:number, lipschitz:number, alcance:number,
 *   d:(x:number, y:number, z:number)=>number}} `d` = a distância no espaço local (já 1-Lipschitz); `alcance` = a maior
 *   meia diagonal das seções
 */
export function lerTronco(node, path) {
  const v = node.secoes;
  if (!Array.isArray(v) || v.length < 2 || v.length > MAX_POINTS) fail(path, `'secoes' precisa ser uma lista de 2 a ${MAX_POINTS} seções`);
  const secoes = v.map((s, i) => {
    if (!Array.isArray(s) || s.length !== 4) fail(path, `'secoes[${i}]' precisa ser [x, largura, espessura, raio]`);
    const q = s.map(Number);
    if (!q.every(Number.isFinite)) fail(path, `'secoes[${i}]' tem número não finito (${JSON.stringify(s)})`);
    const [, l, e, r] = q;
    if (!(l > 0 && e > 0)) fail(path, `'secoes[${i}]' precisa de largura e espessura positivas`);
    if (!(r >= 0 && r <= Math.min(l, e) / 2)) fail(path, `'secoes[${i}]' tem o raio fora de 0 a metade do menor lado`);
    if (i > 0 && q[0] - v[i - 1][0] < MIN_EDGE) fail(path, `'secoes[${i}]' precisa vir depois da anterior em x`);
    return q;
  });
  const x0 = secoes[0][0];
  const x1 = secoes[secoes.length - 1][0];
  let menor = Infinity;
  let alcance = 0;
  let g = 0;
  for (let i = 0; i < secoes.length; i++) {
    const [x, l, e, r] = secoes[i];
    menor = Math.min(menor, l / 2, e / 2);
    alcance = Math.max(alcance, Math.hypot(l / 2, e / 2));
    if (i === 0) continue;
    const [xa, la, ea, ra] = secoes[i - 1];
    const dx = x - xa;
    g = Math.max(g, (Math.abs(l - la) / 2 + Math.abs(e - ea) / 2 + Math.abs(r - ra)) / dx);
  }
  const rd = readNonNegative(node, 'round', path, 0);
  if (rd > menor || rd > (x1 - x0) / 2) fail(path, `'round' (${rd}) maior que a meia medida da seção ou que a metade do comprimento`);
  const lipschitz = Math.sqrt(1 + g * g);
  const inv = 1 / lipschitz;
  const n = secoes.length;
  const xs = Float64Array.from(secoes, (s) => s[0]);
  const meiaL = Float64Array.from(secoes, (s) => s[1] / 2);
  const meiaE = Float64Array.from(secoes, (s) => s[2] / 2);
  const raio = Float64Array.from(secoes, (s) => s[3]);
  const xc = (x0 + x1) / 2;
  const eh = (x1 - x0) / 2 - rd;
  const d = (x, y, z) => {
    // a seção em x (a das pontas fora delas), pelo trecho da busca binária
    let a;
    let b;
    let r;
    if (x <= x0) {
      a = meiaL[0];
      b = meiaE[0];
      r = raio[0];
    } else if (x >= x1) {
      a = meiaL[n - 1];
      b = meiaE[n - 1];
      r = raio[n - 1];
    } else {
      let lo = 0;
      let hi = n - 1;
      while (hi - lo > 1) {
        const m = (lo + hi) >> 1;
        if (xs[m] <= x) lo = m;
        else hi = m;
      }
      const t = (x - xs[lo]) / (xs[hi] - xs[lo]);
      a = meiaL[lo] + (meiaL[hi] - meiaL[lo]) * t;
      b = meiaE[lo] + (meiaE[hi] - meiaE[lo]) * t;
      r = raio[lo] + (raio[hi] - raio[lo]) * t;
    }
    // o retângulo arredondado (meias medidas a em Z e b em Y, canto r), encolhido de rd para o arredondamento da ponta
    const qz = Math.abs(z) - a + r;
    const qy = Math.abs(y) - b + r;
    const mz = qz > 0 ? qz : 0;
    const my = qy > 0 ? qy : 0;
    const dentro = qz > qy ? qz : qy;
    const wx = Math.sqrt(mz * mz + my * my) + (dentro < 0 ? dentro : 0) - r + rd;
    const wy = Math.abs(x - xc) - eh;
    const ox = wx > 0 ? wx : 0;
    const oy = wy > 0 ? wy : 0;
    const w = wx > wy ? wx : wy;
    return ((w < 0 ? w : 0) + Math.sqrt(ox * ox + oy * oy) - rd) * inv;
  };
  return { secoes, x0, x1, rd, lipschitz, alcance, d };
}

/** Função suporte da casca convexa das seções (os retângulos sem o arredondamento, que só encolhe): h(u). */
export function suporteDoTronco(node, path) {
  const { secoes } = lerTronco(node, path);
  return (ux, uy, uz) => {
    let m = -Infinity;
    for (const [x, l, e] of secoes) m = Math.max(m, ux * x + Math.abs(uy) * (e / 2) + Math.abs(uz) * (l / 2));
    return m;
  };
}
