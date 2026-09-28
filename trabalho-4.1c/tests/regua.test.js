// Contas puras da régua (Fase 4.1a): Chaikin, área e caixa de polígono, rasterização com buracos, dilatação, IoU bruto
// e com a tolerância de raio r, perfis de cima e de baixo. Os números são conferíveis à mão.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { areaPoligono, caixaDoPoligono, chaikin, dilatar, iou, perfis, rasterizar } from '../tools/regua/geometria.js';

const QUADRADO = [[0, 0], [10, 0], [10, 10], [0, 10]];

test('régua: área com sinal, caixa e Chaikin (um corte tira 1/8 da área do quadrado)', () => {
  assert.equal(areaPoligono(QUADRADO), 100);
  assert.equal(areaPoligono([...QUADRADO].reverse()), -100);
  assert.deepEqual(caixaDoPoligono(QUADRADO), { x0: 0, y0: 0, x1: 10, y1: 10 });
  const suave = chaikin(QUADRADO, 1);
  assert.equal(suave.length, 8);
  assert.ok(Math.abs(areaPoligono(suave) - 87.5) < 1e-9);
  assert.equal(chaikin(QUADRADO, 2).length, 16);
});

test('régua: rasterização pelo centro da célula, com buraco', () => {
  const grade = { x0: 0, y1: 10, passo: 1, largura: 10, altura: 10 };
  const cheio = rasterizar([QUADRADO], grade);
  assert.equal(cheio.reduce((a, b) => a + b, 0), 100);
  const buraco = [[2, 2], [5, 2], [5, 5], [2, 5]];
  const vazado = rasterizar([QUADRADO, buraco], grade);
  assert.equal(vazado.reduce((a, b) => a + b, 0), 91);
  // Linha 0 é a de cima (y entre 9 e 10); a célula (3, 6) cobre x 3..4, y 3..4 → dentro do buraco.
  assert.equal(vazado[6 * 10 + 3], 0);
  assert.equal(vazado[0], 1);
});

test('régua: dilatação por disco e IoU com tolerância', () => {
  const L = 20;
  const a = new Uint8Array(L * L);
  const b = new Uint8Array(L * L);
  for (let j = 0; j < 10; j++) {
    for (let i = 0; i < 10; i++) a[j * L + i] = 1;
    for (let i = 1; i < 11; i++) b[j * L + i] = 1;
  }
  const d = dilatar(a, L, L, 1);
  assert.equal(d[0 * L + 10], 1, 'um pixel para a direita');
  assert.equal(d[10 * L + 10], 0, 'a diagonal fica fora do disco de raio 1');
  const r0 = iou(a, b, L, L, 0);
  assert.equal(r0.inter, 90);
  assert.ok(Math.abs(r0.bruto - 90 / 110) < 1e-12);
  assert.equal(r0.tolerancia, r0.bruto, 'sem tolerância as duas contas coincidem');
  const r1 = iou(a, b, L, L, 1);
  assert.equal(r1.tolerancia, 1, 'a diferença de 1 px some com r = 1');
  const longe = new Uint8Array(L * L);
  for (let j = 0; j < 10; j++) for (let i = 3; i < 13; i++) longe[j * L + i] = 1;
  assert.ok(iou(a, longe, L, L, 1).tolerancia < 1, 'deslocamento de 3 px ainda conta com r = 1');
});

test('régua: perfis de cima e de baixo por coluna', () => {
  const L = 4;
  const m = new Uint8Array([0, 1, 0, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0]);
  assert.deepEqual(perfis(m, L, L), { cima: [-1, 0, 1, -1], baixo: [-1, 2, 2, -1] });
});
