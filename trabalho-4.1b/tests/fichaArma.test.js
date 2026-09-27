// Ficha de fidelidade no formato 2 (Fase 4.1a; desenho, seção 3.1): a da AK-47 tipo 3 é válida, o contorno bate com as
// medidas, as peças cabem no contorno e a conversão para a planta da 4.1 (u, relativo à boca) — que a bancada desenha —
// é exata. A cor de fábrica × a pintura de fábrica do registro fica em tests/skinsArma.test.js (Tarefa 2).
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { MEDIDAS_CHAVE, MM_POR_U, fichaParaPlanta, plantaDoArquivo, problemasDaFicha, validarFicha } from '../src/weapons/model/ficha.js';
import { areaPoligono, caixaDoPoligono } from '../tools/regua/geometria.js';

const ficha = JSON.parse(readFileSync(new URL('../tools/blender/refs/ak47.json', import.meta.url), 'utf8'));

test('ficha da AK-47 tipo 3: formato 2, válida, cinco medidas-chave com fonte e a foto do lado direito', () => {
  assert.deepEqual(problemasDaFicha(ficha), []);
  assert.equal(ficha.arma, 'ak47');
  assert.match(ficha.variante, /tipo 3/);
  for (const m of MEDIDAS_CHAVE) assert.ok(ficha.medidas[m].mm > 0 && ficha.medidas[m].fonte.length > 3, m);
  assert.equal(ficha.medidas.comprimento.mm, 870);
  assert.equal(ficha.medidas.cano.mm, 415);
  const foto = ficha.fotos.find((f) => f.lado === 'direito');
  assert.equal(foto.arquivo, 'File:AK-47 assault rifle.jpg');
  assert.equal(foto.licenca, 'Domínio público');
  assert.equal(foto.mmPorPixel, 1.018);
});

test('ficha da AK: contorno com a boca em x = 0, comprimento e altura das medidas, buracos e peças dentro', () => {
  const c = caixaDoPoligono(ficha.contorno);
  assert.ok(Math.abs(c.x1) <= 0.5, 'boca em x = 0');
  assert.ok(Math.abs((c.x1 - c.x0) - 870) <= 870 * 0.005, `comprimento ${c.x1 - c.x0}`);
  assert.ok(Math.abs((c.y1 - c.y0) - ficha.medidas.alturaComCarregador.mm) <= 1, 'altura com o carregador');
  assert.ok(Math.abs(areaPoligono(ficha.contorno)) > 40000, 'área de um fuzil de lado (mm²)');
  for (const b of ficha.buracos) {
    const cb = caixaDoPoligono(b);
    assert.ok(cb.x0 >= c.x0 && cb.x1 <= c.x1 && cb.y0 >= c.y0 && cb.y1 <= c.y1);
  }
  for (const [nome, anel] of Object.entries(ficha.pecas)) {
    const cp = caixaDoPoligono(anel);
    assert.ok(cp.x0 >= c.x0 - 1 && cp.x1 <= c.x1 + 1 && cp.y0 >= c.y0 - 1 && cp.y1 <= c.y1 + 1, nome);
  }
  for (const nome of ['coronha', 'soleira', 'receptor', 'tampa', 'punho', 'carregador', 'guardaMaoSuperior', 'guardaMaoInferior', 'torreMassa']) {
    assert.ok(ficha.pecas[nome], `peça ${nome}`);
  }
});

test('ficha → planta: pontos em u relativos à boca, comprimento em u e a fonte', () => {
  const p = fichaParaPlanta(ficha);
  assert.equal(p.weapon, 'ak47');
  assert.ok(Math.abs(p.lengthU - 870 / MM_POR_U) < 1e-12);
  assert.equal(p.points.length, ficha.contorno.length);
  assert.deepEqual(p.points[0], [ficha.contorno[0][0] / MM_POR_U, ficha.contorno[0][1] / MM_POR_U]);
  assert.equal(p.holes.length, ficha.buracos.length);
  assert.equal(p.source.license, 'Domínio público');
  assert.deepEqual(plantaDoArquivo(ficha), p);
  const antiga = { weapon: 'glock', points: [[0, 0], [1, 0], [1, 1]], holes: [], lengthU: 7.3 };
  assert.equal(plantaDoArquivo(antiga), antiga, 'a planta da 4.1 (formato 1) passa como está');
});

test('ficha: cada problema aparece com o campo', () => {
  const ruim = structuredClone(ficha);
  ruim.formato = 1;
  delete ruim.medidas.cano.fonte;
  ruim.fotos = ruim.fotos.map((f) => ({ ...f, lado: 'esquerdo' }));
  ruim.contorno = ruim.contorno.map(([x, y]) => [x - 20, y]);
  const p = problemasDaFicha(ruim);
  assert.ok(p.some((m) => m.startsWith('formato')));
  assert.ok(p.some((m) => m.startsWith('medidas.cano.fonte')));
  assert.ok(p.some((m) => m.includes('lado direito')));
  assert.ok(p.some((m) => m.includes('x = 0')));
  assert.throws(() => validarFicha(ruim), /ficha de ak47 inválida/);
});
