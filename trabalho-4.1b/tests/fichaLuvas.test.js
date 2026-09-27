// Ficha das luvas (Fase 4.1b; desenho em docs/superpowers/specs/2026-09-26-4.1b-luvas-e-empunhadura-design.md,
// seção 2): tools/blender/refs/luvas.json com as medidas da mão e de cada osso, as larguras nas juntas, os limites das
// juntas e a luva, cada grupo com a fonte. O Blender constrói a luva só com o que está aqui; o Node confere antes.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import {
  DEDOS, OSSOS_DO_DEDO, escalasDaFicha, perimetroRetanguloArredondado, problemasDaFichaLuvas, validarFichaLuvas,
} from '../src/characters/hands/fichaLuvas.js';

const ler = () => JSON.parse(readFileSync(new URL('../tools/blender/refs/luvas.json', import.meta.url), 'utf8'));

test('ficha das luvas: formato 1, válida, congelada, com as seis fontes', () => {
  const f = validarFichaLuvas(ler());
  assert.equal(f.formato, 1);
  assert.equal(f.id, 'luvas');
  assert.ok(Object.isFrozen(f) && Object.isFrozen(f.ossos.medio) && Object.isFrozen(f.juntas.medio.pip));
  for (const fonte of ['ansur2', 'ansur2Explorador', 'buryanov', 'greiner', 'aaos', 'referencias']) {
    assert.ok(f.fontes[fonte].titulo.length > 10 && /^https:\/\//.test(f.fontes[fonte].url), fonte);
  }
  assert.deepEqual(DEDOS, ['polegar', 'indicador', 'medio', 'anelar', 'minimo']);
});

test('ficha das luvas: os números das fontes, como publicados', () => {
  const f = ler();
  assert.equal(f.mao.comprimento.mm, 189.3);
  assert.equal(f.mao.largura.mm, 85);
  assert.equal(f.mao.palma.mm, 113.9);
  assert.equal(f.mao.circunferencia.mm, 203.9);
  assert.equal(f.mao.pulso.mm, 169);
  // ANSUR II no Data Explorer do OPEN Design Lab: medianas dos dois sexos.
  assert.deepEqual([f.antebraco.circunferenciaFlexionado.mm, f.antebraco.pulso.mm], [285, 165]);
  // Buryanov & Kotiuk (2010), tabela I.
  const b = f.ossos;
  assert.deepEqual([b.polegar.metacarpo, b.polegar.proximal, b.polegar.distal, b.polegar.polpa], [46.22, 31.57, 21.67, 5.67]);
  assert.deepEqual([b.indicador.metacarpo, b.indicador.proximal, b.indicador.media, b.indicador.distal, b.indicador.polpa], [68.12, 39.78, 22.38, 15.82, 3.84]);
  assert.deepEqual([b.medio.metacarpo, b.medio.proximal, b.medio.media, b.medio.distal, b.medio.polpa], [64.6, 44.63, 26.33, 17.4, 3.95]);
  assert.deepEqual([b.anelar.metacarpo, b.anelar.proximal, b.anelar.media, b.anelar.distal, b.anelar.polpa], [58, 41.37, 25.65, 17.3, 3.95]);
  assert.deepEqual([b.minimo.metacarpo, b.minimo.proximal, b.minimo.media, b.minimo.distal, b.minimo.polpa], [53.69, 32.74, 18.11, 15.96, 3.73]);
  // Greiner (1991), médias dos homens.
  const j = f.juntas;
  assert.deepEqual([j.polegar.ip.largura, j.polegar.ip.circunferencia], [24, 72.3]);
  assert.deepEqual(['indicador', 'medio', 'anelar', 'minimo'].map((d) => j[d].pip.largura), [23, 22.5, 21.4, 19.2]);
  assert.deepEqual(['indicador', 'medio', 'anelar', 'minimo'].map((d) => j[d].pip.circunferencia), [68.4, 69.6, 64.9, 57.8]);
  assert.deepEqual(['medio', 'anelar', 'minimo'].map((d) => j[d].dip.largura), [19.8, 18.5, 17.4]);
  assert.deepEqual(['indicador', 'medio', 'anelar', 'minimo'].map((d) => j[d].dip.circunferencia), [57.4, 57.8, 53.8, 49.2]);
  assert.deepEqual([j.pulso.largura, j.pulso.circunferencia], [65.8, 174.3]);
  assert.deepEqual(DEDOS.map((d) => j.pontaAoPulso[d]), [137.9, 185.2, 194.5, 185, 159.9]);
  assert.equal(j.larguraDaMao, 90.4);
  assert.deepEqual([j.dobras.polegarIndicador, j.dobras.indicadorMedio, j.dobras.medioAnelar, j.dobras.anelarMinimo], [69.1, 110.4, 109.9, 96.6]);
  assert.equal(j.cotoveloAoPulso, 290);
  // AAOS.
  const l = f.limites;
  assert.deepEqual([l.mcp, l.pip, l.dip, l.abertura], [[0, 90], [0, 100], [0, 90], [-20, 20]]);
  assert.deepEqual([l.polegar.cmcAbducao, l.polegar.cmcFlexao, l.polegar.mcp, l.polegar.ip], [[0, 70], [-20, 15], [0, 50], [0, 80]]);
  assert.deepEqual(l.pulso, { flexao: 80, extensao: 70, radial: 20, ulnar: 30 });
  assert.deepEqual(l.antebraco, { pronacao: 80, supinacao: 80 });
  // Cooney (1981): a rotação axial da CMC do polegar.
  assert.deepEqual(f.rotacaoDoPolegar.cmc, [0, 17]);
  assert.equal(f.rotacaoDoPolegar.fonte, 'cooney');
});

test('ficha das luvas: as escalas das médias dos homens para a mão da ficha', () => {
  const e = escalasDaFicha(ler());
  assert.ok(Math.abs(e.comprimento - 189.3 / 194.5) < 1e-12, 'comprimento pela ponta do médio ao pulso');
  assert.ok(Math.abs(e.largura - 85 / 90.4) < 1e-12, 'largura pela largura da mão');
});

test('ficha das luvas: cada dedo cabe entre o pulso e a ponta, o médio é o mais longo e o mínimo o mais curto', () => {
  const f = ler();
  const e = escalasDaFicha(f);
  const comprimento = (d) => OSSOS_DO_DEDO[d].filter((o) => o !== 'metacarpo').reduce((s, o) => s + f.ossos[d][o], 0);
  for (const d of DEDOS.slice(1)) {
    const mcp = f.juntas.pontaAoPulso[d] * e.comprimento - comprimento(d);
    const cmc = mcp - f.ossos[d].metacarpo;
    assert.ok(cmc > 20 && cmc < 45, `${d}: a base do metacarpo a ${cmc.toFixed(1)} mm do pulso`);
  }
  const pontas = DEDOS.slice(1).map((d) => f.juntas.pontaAoPulso[d]);
  assert.equal(Math.max(...pontas), f.juntas.pontaAoPulso.medio);
  assert.equal(Math.min(...pontas), f.juntas.pontaAoPulso.minimo);
  assert.ok(Math.abs(f.juntas.pontaAoPulso.medio * e.comprimento - f.mao.comprimento.mm) < 0.05, 'a ponta do médio é o comprimento da mão');
});

test('ficha das luvas: a luva, o repouso e as deduções com o porquê', () => {
  const f = ler();
  for (const k of ['tecido', 'couro', 'almofada', 'protetor', 'tira', 'punho', 'folgaPunho']) assert.ok(f.luva[k] > 0, `luva.${k}`);
  assert.ok(f.luva.nota.length > 20);
  for (const k of ['mcp', 'pip', 'dip', 'abertura', 'polegarAbducao', 'polegarMcp', 'polegarIp']) assert.ok(Number.isFinite(f.repouso[k]), `repouso.${k}`);
  for (const [nome, d] of Object.entries(f.deducoes)) assert.ok(typeof d.porque === 'string' && d.porque.length > 20, `deducoes.${nome}.porque`);
  assert.ok(f.deducoes.polegar.cmc.length === 3 && Number.isFinite(f.deducoes.polegar.anguloNaPalma));
  assert.ok(f.deducoes.pulso.espessura > 30 && f.deducoes.antebraco.divisao > 0 && f.deducoes.antebraco.divisao < 1);
  assert.ok(f.deducoes.leque.fator > 0 && f.deducoes.leque.fator < 1);
  assert.deepEqual(Object.keys(f.deducoes.arco.mm), ['indicador', 'medio', 'anelar', 'minimo']);
  assert.deepEqual(Object.keys(f.deducoes.convergencia.graus), ['indicador', 'medio', 'anelar', 'minimo']);
  assert.ok(f.deducoes.espessuraDaMao.mm > 20 && f.deducoes.espessuraDaMao.mm < 40);
});

test('ficha das luvas: as seções de retângulo arredondado batem com as circunferências', () => {
  const f = ler();
  const e = escalasDaFicha(f);
  const d = f.deducoes;
  // O pulso: a largura de Greiner na escala da ficha e a espessura e o raio deduzidos dão a circunferência do ANSUR II.
  const pulso = perimetroRetanguloArredondado(f.juntas.pulso.largura * e.largura, d.pulso.espessura, d.pulso.raio);
  assert.ok(Math.abs(pulso - f.mao.pulso.mm) < 1, `pulso: ${pulso.toFixed(1)} mm`);
  // A mão nos nós: a largura e a espessura com o raio deduzido ficam a ±2 % da circunferência do ANSUR II.
  const nos = perimetroRetanguloArredondado(f.mao.largura.mm, d.espessuraDaMao.mm, d.espessuraDaMao.raio);
  assert.ok(Math.abs(nos / f.mao.circunferencia.mm - 1) < 0.02, `nós: ${nos.toFixed(1)} mm`);
  // O antebraço: a razão das medianas aplicada ao pulso da ficha; o expoente deixa o terço do pulso quase reto.
  const p = d.perfilDoAntebraco;
  assert.ok(Math.abs(p.circunferenciaNoCotovelo - f.mao.pulso.mm * f.antebraco.circunferenciaFlexionado.mm / f.antebraco.pulso.mm) < 0.05);
  assert.ok(p.expoente > 1 && p.expoente < 2);
  const comprimento = f.juntas.cotoveloAoPulso * e.comprimento;
  const naBoca = f.mao.pulso.mm + (p.circunferenciaNoCotovelo - f.mao.pulso.mm) * (f.luva.punho / comprimento) ** p.expoente;
  assert.ok(naBoca / f.mao.pulso.mm > 1.04 && naBoca / f.mao.pulso.mm < 1.1, `na boca do punho: ${naBoca.toFixed(1)} mm`);
});

test('ficha das luvas: cada problema aparece com o campo', () => {
  const ruim = ler();
  delete ruim.fontes.greiner;
  delete ruim.ossos.anelar;
  ruim.ossos.medio.proximal = 0;
  delete ruim.juntas.fonte;
  delete ruim.juntas.dobras.anelarMinimo;
  delete ruim.deducoes.arco;
  delete ruim.antebraco.circunferenciaFlexionado;
  ruim.deducoes.pulso.raio = -1;
  delete ruim.deducoes.perfilDoAntebraco.expoente;
  ruim.limites.pip = [0];
  delete ruim.limites.antebraco.supinacao;
  ruim.rotacaoDoPolegar.cmc = [17];
  const p = problemasDaFichaLuvas(ruim);
  assert.ok(p.some((m) => m.includes('fontes.greiner')), p.join(' | '));
  assert.ok(p.some((m) => m.includes('ossos.anelar')), p.join(' | '));
  assert.ok(p.some((m) => m.includes('ossos.medio.proximal')), p.join(' | '));
  assert.ok(p.some((m) => m.includes('juntas.fonte')), p.join(' | '));
  assert.ok(p.some((m) => m.includes('limites.pip')), p.join(' | '));
  assert.ok(p.some((m) => m.includes('limites.antebraco.supinacao')), p.join(' | '));
  assert.ok(p.some((m) => m.includes('rotacaoDoPolegar.cmc')), p.join(' | '));
  assert.ok(p.some((m) => m.includes('juntas.dobras.anelarMinimo')), p.join(' | '));
  assert.ok(p.some((m) => m.includes('deducoes.arco')), p.join(' | '));
  assert.ok(p.some((m) => m.includes('antebraco.circunferenciaFlexionado')), p.join(' | '));
  assert.ok(p.some((m) => m.includes('deducoes.pulso.raio')), p.join(' | '));
  assert.ok(p.some((m) => m.includes('deducoes.perfilDoAntebraco.expoente')), p.join(' | '));
  assert.throws(() => validarFichaLuvas(ruim), /ficha das luvas/);
});
