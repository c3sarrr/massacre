// Classes das armas realistas (Fase 4.1c; plano em docs/superpowers/plans/2026-09-28-4.1c-glock-m4a4-m9.md, D2 e D3): as
// zonas, os soquetes da base e as medidas-chave de cada classe (fuzil, pistola, faca) no registro, e a ficha no formato 2
// validada pelas medidas da classe, com a foto do contorno de qualquer lado.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import {
  ARMAS_REAIS, CLASSES, PECAS_MOVEIS, ZONAS, classeDaArma, medidasDaArma, orcamentoDaArma, soquetesDaArma, zonasDaArma,
} from '../src/data/armasReais.js';
import { fotoDoContorno, problemasDaFicha } from '../src/weapons/model/ficha.js';

const ak = JSON.parse(readFileSync(new URL('../tools/blender/refs/ak47.json', import.meta.url), 'utf8'));
const FOGO = ['comprimento', 'cano', 'raioDeMira', 'alturaSemCarregador', 'alturaComCarregador'];
const SOQUETES_FOGO = ['boca', 'ejecao', 'carregador', 'mira_tras', 'mira_frente', 'mao_d', 'mao_e'];

test('classes: fuzil e pistola com as cinco zonas, os sete soquetes e as cinco medidas; a faca com as dela', () => {
  assert.deepEqual(Object.keys(CLASSES).sort(), ['faca', 'fuzil', 'pistola']);
  for (const c of ['fuzil', 'pistola']) {
    assert.deepEqual([...CLASSES[c].zonas], [...ZONAS]);
    assert.deepEqual([...CLASSES[c].soquetes], SOQUETES_FOGO);
    assert.deepEqual([...CLASSES[c].medidas], FOGO);
  }
  assert.deepEqual([...CLASSES.faca.zonas], ['corpo', 'guarnicao', 'detalhes']);
  assert.deepEqual([...CLASSES.faca.soquetes], ['mao_d', 'ponta']);
  assert.deepEqual([...CLASSES.faca.medidas], ['comprimento', 'lamina', 'espessuraLamina']);
  for (const c of Object.values(CLASSES)) {
    assert.ok(Object.isFrozen(c) && Object.isFrozen(c.zonas) && Object.isFrozen(c.soquetes) && Object.isFrozen(c.medidas));
    assert.ok(c.orcamento.triangulos.perto > c.orcamento.triangulos.mundo, 'orçamento da classe');
  }
});

test('classes: a AK continua com o mesmo registro (zonas, soquetes, medidas e orçamento de fuzil)', () => {
  assert.equal(classeDaArma('ak47'), 'fuzil');
  assert.deepEqual([...zonasDaArma('ak47')], [...ZONAS]);
  assert.deepEqual(soquetesDaArma('ak47'), SOQUETES_FOGO);
  assert.deepEqual([...medidasDaArma('ak47')], FOGO);
  assert.deepEqual(orcamentoDaArma('ak47'), { triangulos: { perto: 40000, mundo: 6000, longe: 1500 }, textura: 2048, texturaMundo: 512, arquivosMB: 6 });
  assert.throws(() => classeDaArma('espatula'), /arma realista desconhecida: espatula/);
});

test('classes: peças móveis da M4 (alavanca de manejo e tampa da janela) e cada arma do registro dentro da classe', () => {
  for (const p of ['ferrolho', 'carregador', 'gatilho', 'cao', 'seletor', 'alavanca', 'tampa']) assert.ok(PECAS_MOVEIS.includes(p), p);
  for (const [id, a] of Object.entries(ARMAS_REAIS)) {
    for (const p of a.pecas) assert.ok(PECAS_MOVEIS.includes(p), `${id}: peça ${p}`);
    assert.deepEqual([...a.zonas], [...zonasDaArma(id)], `${id}: as zonas da classe`);
    for (const z of Object.keys(a.fabrica.zonas)) assert.ok(zonasDaArma(id).includes(z), `${id}: pintura na zona ${z}`);
  }
});

test('ficha por classe: a faca pede lâmina e espessura, e não raio de mira nem alturas', () => {
  const faca = structuredClone(ak);
  faca.arma = 'knife';
  const p = problemasDaFicha(faca, 'faca');
  assert.ok(p.some((m) => m.startsWith('medidas.lamina.mm')));
  assert.ok(p.some((m) => m.startsWith('medidas.espessuraLamina.mm')));
  faca.medidas = {
    comprimento: ak.medidas.comprimento,
    lamina: { mm: 178, fonte: 'teste' },
    espessuraLamina: { mm: 6, fonte: 'teste' },
  };
  assert.deepEqual(problemasDaFicha(faca, 'faca'), []);
  assert.ok(problemasDaFicha(faca, 'pistola').some((m) => m.startsWith('medidas.raioDeMira')));
  assert.throws(() => problemasDaFicha(faca, 'lança'), /classe desconhecida: lança/);
});

test('ficha por classe: sem a classe, vale a do registro (a AK, fuzil) e, fora dele, a de fuzil', () => {
  assert.deepEqual(problemasDaFicha(ak), []);
  const outra = structuredClone(ak);
  outra.arma = 'semregistro';
  assert.deepEqual(problemasDaFicha(outra), []);
});

test('foto do contorno: a marcada, de qualquer lado (espelhada na régua); sem marca, a do lado direito', () => {
  assert.equal(fotoDoContorno(ak).arquivo, 'File:AK-47 assault rifle.jpg', 'a ficha da AK não marca: vale a do lado direito');
  const f = structuredClone(ak);
  f.fotos = [
    { ...ak.fotos[0], lado: 'direito', usos: ['janela de ejeção'] },
    { ...ak.fotos[1], lado: 'esquerdo', espelhada: true, contorno: true, usos: ['contorno', 'seletor'] },
  ];
  assert.deepEqual(problemasDaFicha(f), []);
  assert.equal(fotoDoContorno(f).arquivo, ak.fotos[1].arquivo);
  f.fotos[0].contorno = true;
  assert.ok(problemasDaFicha(f).some((m) => m.includes('uma foto só com contorno: true')));
  f.fotos[0].contorno = false;
  f.fotos[1].lado = 'de cima';
  assert.ok(problemasDaFicha(f).some((m) => m.startsWith('fotos[1].lado')));
  f.fotos[1].lado = 'esquerdo';
  f.fotos[1].espelhada = 'sim';
  assert.ok(problemasDaFicha(f).some((m) => m.startsWith('fotos[1].espelhada')));
  f.fotos[1].espelhada = true;
  f.fotos[1].usos = 'contorno';
  assert.ok(problemasDaFicha(f).some((m) => m.startsWith('fotos[1].usos')));
});

test('saída: o relatório traz as medidas da classe, cada uma a ±1 % do alvo, e nenhuma a mais', async () => {
  const { problemasDasMedidas } = await import('../tools/blender/saida.mjs');
  const med = (mm, alvo) => ({ mm, alvo, erro: (mm - alvo) / alvo });
  const faca = { medidas: { comprimento: med(305.5, 305), lamina: med(178, 178), espessuraLamina: med(6.02, 6) } };
  assert.deepEqual(problemasDasMedidas(faca, CLASSES.faca.medidas), []);
  const p = problemasDasMedidas({ medidas: { comprimento: med(310, 305), cano: med(1, 1) } }, CLASSES.faca.medidas);
  assert.ok(p.some((m) => m.includes('comprimento') && m.includes('+1.64 %')), p.join('; '));
  assert.ok(p.some((m) => m === 'o relatório não tem a medida lamina'));
  assert.ok(p.some((m) => m === 'o relatório não tem a medida espessuraLamina'));
  assert.ok(p.some((m) => m === 'medida cano fora das da classe'));
});
