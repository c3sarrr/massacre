// Registro das luvas (Fase 4.1b; desenho em docs/superpowers/specs/2026-09-26-4.1b-luvas-e-empunhadura-design.md,
// seção 7.1; plano, D2 e D6): a pasta, as zonas, os 20 ossos por braço, o orçamento e a pintura de cada facção.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { FACCOES_DAS_LUVAS, LUVAS, OSSOS_DO_BRACO, ZONAS_DAS_LUVAS, ossosDoLado } from '../src/data/luvas.js';

test('luvas: a pasta, as três zonas e o orçamento da D6', () => {
  assert.equal(LUVAS.pasta, 'assets/maos/');
  assert.deepEqual(ZONAS_DAS_LUVAS, ['couro', 'tecido', 'reforco']);
  assert.deepEqual(LUVAS.orcamento, { triangulos: 14000, textura: 2048, arquivosMB: 6 });
  assert.ok(Object.isFrozen(LUVAS) && Object.isFrozen(LUVAS.pinturas.massaCrua.zonas.couro));
});

test('luvas: os 20 ossos por braço com os nomes da D2 e o sufixo do lado', () => {
  assert.equal(OSSOS_DO_BRACO.length, 20);
  assert.deepEqual(OSSOS_DO_BRACO.slice(0, 3), ['antebraco', 'torcao', 'mao']);
  for (const d of ['polegar', 'indicador', 'medio']) {
    assert.deepEqual(OSSOS_DO_BRACO.filter((o) => o.startsWith(`${d}_`)), [1, 2, 3].map((i) => `${d}_${i}`));
  }
  for (const d of ['anelar', 'minimo']) {
    assert.deepEqual(OSSOS_DO_BRACO.filter((o) => o.startsWith(`${d}_`)), [0, 1, 2, 3].map((i) => `${d}_${i}`));
  }
  assert.equal(ossosDoLado('d')[2], 'mao_d');
  assert.equal(ossosDoLado('e').at(-1), 'minimo_3_e');
  assert.throws(() => ossosDoLado('x'), /lado/);
});

test('luvas: a pintura de cada facção, zona a zona, com as cores do desenho', () => {
  assert.deepEqual(FACCOES_DAS_LUVAS, ['massaCrua', 'tropa']);
  const cores = (f) => ZONAS_DAS_LUVAS.map((z) => LUVAS.pinturas[f].zonas[z].cor);
  assert.deepEqual(cores('massaCrua'), ['#8B6B4A', '#6B5038', '#4A3A2C']);
  assert.deepEqual(cores('tropa'), ['#1D1D1F', '#232326', '#2C2D30']);
  for (const f of FACCOES_DAS_LUVAS) {
    const z = LUVAS.pinturas[f].zonas;
    assert.deepEqual([z.couro.acabamento, z.tecido.acabamento, z.reforco.acabamento], ['couro', 'tecido', 'borracha']);
    for (const zona of ZONAS_DAS_LUVAS) assert.ok(z[zona].desgaste >= 0 && z[zona].desgaste <= 1, `${f}.${zona}`);
    assert.ok(LUVAS.pinturas[f].nome.length > 3);
  }
});
