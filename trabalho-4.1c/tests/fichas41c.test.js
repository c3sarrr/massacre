// As fichas da 4.1c no formato 2 (plano em docs/superpowers/plans/2026-09-28-4.1c-glock-m4a4-m9.md, Tarefa 3): cada
// uma válida pela classe dela, com as medidas oficiais e a fonte primária, a foto do contorno marcada (com a escala), as
// fotos dos dois lados quando há peça de um lado só, o contorno no comprimento oficial, as peças dentro dele e as cores
// de fábrica com a correção.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { fotoDoContorno, problemasDaFicha } from '../src/weapons/model/ficha.js';
import { caixaDoPoligono } from '../tools/regua/geometria.js';

const ler = (id) => JSON.parse(readFileSync(new URL(`../tools/blender/refs/${id}.json`, import.meta.url), 'utf8'));

/** O contorno no comprimento oficial (±0,5 %), a boca em x = 0 e as peças dentro da caixa dele (1 mm de folga). */
function conferirContorno(f) {
  const c = caixaDoPoligono(f.contorno);
  assert.ok(Math.abs(c.x1) <= 0.5, `${f.arma}: a boca em x = 0`);
  const alvo = f.medidas.comprimento.mm;
  assert.ok(Math.abs((c.x1 - c.x0) - alvo) <= alvo * 0.005, `${f.arma}: comprimento ${c.x1 - c.x0}`);
  for (const [nome, anel] of Object.entries(f.pecas)) {
    const p = caixaDoPoligono(anel);
    assert.ok(p.x0 >= c.x0 - 1 && p.x1 <= c.x1 + 1 && p.y0 >= c.y0 - 1 && p.y1 <= c.y1 + 1, `${f.arma}: peça ${nome} fora do contorno`);
  }
  return c;
}

test('ficha da Glock-18: 3ª geração, válida como pistola, medidas da Glock com a fonte', () => {
  const f = ler('glock');
  assert.deepEqual(problemasDaFicha(f, 'pistola'), []);
  assert.match(f.variante, /Glock 18 de 3ª geração/);
  assert.equal(f.medidas.comprimento.mm, 204);
  assert.equal(f.medidas.cano.mm, 114);
  assert.equal(f.medidas.raioDeMira.mm, 165);
  for (const m of ['comprimento', 'cano', 'raioDeMira']) assert.match(f.medidas[m].fonte, /Glock/);
  assert.ok(Math.abs(f.medidas.raioDeMira.foto - 165) / 165 <= 0.01, 'o raio de mira da foto a ±1 %');
  assert.ok(Math.abs(f.medidas.ferrolho.foto - 186) / 186 <= 0.01, 'o ferrolho da foto a ±1 % dos 186 mm');
});

test('ficha da Glock-18: a foto do contorno (MOD, lado esquerdo espelhada) e as dos dois lados', () => {
  const f = ler('glock');
  const foto = fotoDoContorno(f);
  assert.equal(foto.arquivo, 'File:GLOCK 17 Gen 4 Pistol MOD 45160305.jpg');
  assert.equal(foto.lado, 'esquerdo');
  assert.equal(foto.espelhada, true);
  assert.ok(foto.mmPorPixel > 0.1 && foto.mmPorPixel < 0.2);
  assert.ok(f.fotos.some((p) => p.lado === 'direito' && p.usos.includes('janela de ejeção')), 'a janela vem do lado direito');
  assert.ok(f.fotos.some((p) => p.lado === 'esquerdo' && p.usos.includes('seletor')), 'o seletor vem do lado esquerdo');
});

test('ficha da Glock-18: contorno, peças, alturas e o que só se vê de cima', () => {
  const f = ler('glock');
  const c = conferirContorno(f);
  assert.ok(Math.abs((c.y1 - c.y0) - f.medidas.alturaComCarregador.mm) <= 0.5, 'a altura com o carregador é a do contorno');
  for (const p of ['ferrolho', 'armacao', 'gatilho', 'carregador', 'miraTras', 'miraFrente']) assert.ok(f.pecas[p], p);
  assert.ok(f.buracos.length >= 2, 'o vão do guarda-mato na frente e atrás do gatilho');
  const L = f.vistaDeCima.larguras;
  assert.equal(L.ferrolho.mm, 25.5);
  assert.equal(L.punho.mm, 30);
  assert.equal(L.seletor.sai, 4);
  const d = f.vistaDeCima.detalhes;
  assert.equal(d.serrilha.sulcos.length, 7);
  assert.ok(d.serrilha.esquerdaDa18[0] > d.serrilha.x[0], 'no lado esquerdo da 18 a serrilha fica à frente do seletor');
  assert.ok(f.pontos.janela.x0 < f.pontos.janela.x1 && f.pontos.janela.y1 > f.pontos.janela.y0);
  for (const [nome, cor] of Object.entries(f.cores)) assert.match(cor.fabrica, /^#[0-9A-F]{6}$/, nome);
});

test('ficha da M4A4: a M4A1 de 14,5 pol., válida como fuzil, com as medidas do TM e o contorno composto', () => {
  const f = ler('m4a4');
  assert.deepEqual(problemasDaFicha(f, 'fuzil'), []);
  assert.match(f.variante, /M4A1/);
  assert.equal(f.medidas.comprimento.mm, 838.2);
  assert.equal(f.medidas.cano.mm, 368.3);
  for (const m of ['comprimento', 'cano']) assert.match(f.medidas[m].fonte, /TM 9-1005-319-23&P/);
  assert.equal(f.medidas.fechada.mm, 755.7, 'a coronha fechada dá a escala');
  const foto = fotoDoContorno(f);
  assert.equal(foto.arquivo, 'File:PEO M4 Carbine RAS noBG.png');
  assert.ok(f.fotos.some((p) => p.arquivo === 'File:M4A1 Carbine.jpg' && p.usos.some((u) => /alça/.test(u))), 'a alça da foto da planta da 4.1');
  assert.ok(f.fotos.some((p) => p.lado === 'esquerdo' && p.usos.includes('seletor')), 'o seletor vem do lado esquerdo');
  const c = conferirContorno(f);
  assert.ok(Math.abs((c.y1 - c.y0) - f.medidas.alturaComCarregador.mm) <= 0.5);
  for (const p of ['coronha', 'receptorInferior', 'receptorSuperior', 'alca', 'guardaMao', 'torre', 'quebraChamas', 'carregador', 'gatilho']) {
    assert.ok(f.pecas[p], p);
  }
  // as fendas dos trilhos no passo da foto: o do receptor a 1,5 % da norma (10,008 mm); o do guarda-mão da foto fica
  // 2,4 % abaixo dela (a posição das fendas vem da foto, a largura e o fundo da norma)
  const passo = (xs) => (xs[xs.length - 1] - xs[0]) / (xs.length - 1);
  assert.ok(Math.abs(passo(f.pontos.trilho.fendas) - 10.008) / 10.008 < 0.015);
  assert.ok(Math.abs(passo(f.pontos.trilhoGuardaMao.fendas) - 10.008) / 10.008 < 0.035);
  assert.equal(f.vistaDeCima.larguras.trilho.mm, 21.2);
  assert.ok(Math.abs(f.pontos.massaDeMira[0] - f.pontos.miraTras[0] - f.medidas.raioDeMira.mm) < 0.5, 'o raio de mira pelos pontos');
});

test('ficha da faca: a baioneta M9, válida como faca, com a lâmina, a espessura e o furo do corta-arame', () => {
  const f = ler('knife');
  assert.deepEqual(problemasDaFicha(f, 'faca'), []);
  assert.match(f.variante, /M9/);
  assert.equal(f.medidas.comprimento.mm, 311.2);
  assert.match(f.medidas.comprimento.fonte, /NMAH/);
  assert.ok(Math.abs(f.medidas.lamina.foto - f.medidas.lamina.mm) / f.medidas.lamina.mm <= 0.01, 'a lâmina da foto a ±1 %');
  assert.equal(f.medidas.espessuraLamina.mm, 5.84);
  const c = conferirContorno(f);
  assert.ok(Math.abs((c.y1 - c.y0) - f.medidas.alturaGuarda.mm) / f.medidas.alturaGuarda.mm <= 0.02, 'a guarda com a argola');
  assert.equal(f.buracos.length, 1, 'o furo do corta-arame');
  const s = f.pontos.serrilha;
  assert.ok(Math.abs((s.x[1] - s.x[0]) - 76.2) < 5, 'uns três polegadas de dentes (a patente)');
  for (const p of ['lamina', 'guarda', 'cabo', 'pomo']) assert.ok(f.pecas[p], p);
});
