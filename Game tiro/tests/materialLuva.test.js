// Os acabamentos das luvas (Fase 4.1b; desenho em docs/superpowers/specs/2026-09-26-4.1b-luvas-e-empunhadura-design.md,
// seção 7.2; plano, Tarefa 8): couro, tecido (com o brilho de tecido, o `sheen` do material físico) e borracha — os
// números da função pura, o material de zona com o brilho e o padrão pela pose de repouso (a malha das luvas se deforma
// na CPU: o padrão lê os atributos de repouso), e as pinturas das duas facções pela validação das skins.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import * as THREE from 'three';
import { PADROES } from '../src/data/acabamentos.js';
import { LUVAS, ZONAS_DAS_LUVAS } from '../src/data/luvas.js';
import { acabamentoParaMaterial } from '../src/weapons/skins/acabamento.js';
import { validarPintura } from '../src/weapons/skins/skin.js';
import { criarMaterialZona } from '../src/weapons/model/materialArma.js';

const FAIXAS = { couro: [0.45, 0.65], tecido: [0.8, 0.95], borracha: [0.55, 0.75] };
const PADRAO = { couro: 'grao', tecido: 'trama', borracha: 'pontilhado' };

test('couro, tecido e borracha: sem metal, a aspereza na faixa e o padrão procedural deles', () => {
  for (const [acabamento, [a, b]] of Object.entries(FAIXAS)) {
    const p = acabamentoParaMaterial({ acabamento, cor: '#8B6B4A' });
    assert.equal(p.metalness, 0, acabamento);
    assert.ok(p.roughness >= a && p.roughness <= b, `${acabamento}: aspereza ${p.roughness} fora de ${a}–${b}`);
    assert.equal(p.padrao, PADRAO[acabamento]);
    assert.equal(p.padraoId, PADROES.indexOf(PADRAO[acabamento]));
    assert.ok(p.padraoId > 0);
  }
});

test('só o tecido liga o brilho de tecido, com a cor e a aspereza dele', () => {
  const t = acabamentoParaMaterial({ acabamento: 'tecido', cor: '#6B5038' });
  assert.ok(t.sheen > 0);
  assert.ok(t.sheenRoughness > 0 && t.sheenRoughness < 1);
  assert.equal(t.sheenColor.length, 3);
  assert.ok(t.sheenColor[0] > t.color[0], 'o brilho mais claro que o fio');
  assert.ok(t.recursos.includes('tecido'));
  for (const acabamento of ['couro', 'borracha', 'oxidado', 'madeira']) {
    const p = acabamentoParaMaterial({ acabamento, cor: '#303135' });
    assert.equal(p.sheen, 0, acabamento);
    assert.ok(!p.recursos.includes('tecido'), acabamento);
  }
});

test('o brilho de tecido sai tingido pelo fio: a luva preta da Tropa lê preta, o coiote fica como na 4.1b', () => {
  // Medido na pista (4.1c, Tarefa 13): com o brilho clareando o fio 35 % rumo ao branco, o tecido preto da Tropa ganhava
  // um brilho cinza de 0,36 e saía rgb(86, 51, 29) sob a luminária (sem o brilho, 24, 9, 3) — a luva preta lia
  // cinza-parda e as duas facções quase iguais. Nas fotos (Commons: "US Navy 091208-N-4440L-097…", a luva preta sob o
  // sol do deserto; a Mechanix preta sobre o tapete), o tecido preto continua preto, com reflexos fracos só nas quinas.
  const lum = (c) => 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2];
  const sat = (c) => (Math.max(...c) - Math.min(...c)) / Math.max(...c);
  const tecido = (f) => acabamentoParaMaterial({ acabamento: 'tecido', cor: LUVAS.pinturas[f].zonas.tecido.cor });
  const coiote = tecido('massaCrua');
  const preto = tecido('tropa');
  // o brilho do coiote com a luminância de antes (0,389, a aprovada na 4.1b), agora na cor do fio (não cinza)
  assert.ok(Math.abs(lum(coiote.sheenColor) - 0.3886) < 0.002, `o brilho do coiote: ${lum(coiote.sheenColor).toFixed(4)}`);
  assert.ok(sat(coiote.sheenColor) > 0.4, `o brilho do coiote tingido: saturação ${sat(coiote.sheenColor).toFixed(2)}`);
  // o do preto: escuro (a 15 % no máximo; antes, 0,36) e menos de 40 % do brilho do coiote
  assert.ok(lum(preto.sheenColor) <= 0.15, `o brilho do tecido preto: ${lum(preto.sheenColor).toFixed(4)}`);
  assert.ok(lum(preto.sheenColor) < 0.4 * lum(coiote.sheenColor), 'as duas facções separadas pelo brilho');
  // sem passar de 1 no fio claro
  for (const c of acabamentoParaMaterial({ acabamento: 'tecido', cor: '#F4EDE1' }).sheenColor) assert.ok(c <= 1);
});

test('o couro e o tecido escurecem o fundo do padrão (a segunda cor sai da primeira)', () => {
  for (const acabamento of ['couro', 'tecido']) {
    const p = acabamentoParaMaterial({ acabamento, cor: '#8B6B4A' });
    assert.ok(p.color2 && p.color2[0] < p.color[0], acabamento);
  }
});

test('material de zona das luvas: o brilho de tecido, a chave do programa e o padrão pela pose de repouso', () => {
  const texturas = { n: new THREE.Texture(), m: new THREE.Texture() };
  const t = criarMaterialZona({ zona: 'tecido', def: { acabamento: 'tecido', cor: '#6B5038', desgaste: 0.15 }, texturas, repouso: true });
  assert.equal(t.sheen, 1);
  assert.ok(t.sheenRoughness > 0);
  assert.ok(t.sheenColor.r > t.color.r);
  assert.equal(t.customProgramCacheKey(), 'arma:trama:tecido:repouso');
  assert.equal(t.defines.ARMA_REPOUSO, '');
  const shader = { uniforms: {}, vertexShader: THREE.ShaderLib.physical.vertexShader, fragmentShader: THREE.ShaderLib.physical.fragmentShader };
  t.onBeforeCompile(shader);
  assert.match(shader.vertexShader, /attribute vec3 repouso;\nattribute vec3 normalRepouso;/);
  assert.match(shader.vertexShader, /#ifdef ARMA_REPOUSO\nvPosArma = repouso;\nvNormalArma = normalRepouso;/);
  const c = criarMaterialZona({ zona: 'couro', def: { acabamento: 'couro', cor: '#8B6B4A' }, texturas });
  assert.equal(c.sheen, 0);
  assert.equal(c.defines.ARMA_REPOUSO, undefined, 'as armas leem a posição da malha');
  assert.equal(c.customProgramCacheKey(), 'arma:grao:');
  assert.equal(c.defines.ARMA_PADRAO, PADROES.indexOf('grao'));
});

test('as pinturas de Massa Crua e da Tropa do Estúdio passam pela validação das skins', () => {
  for (const [faccao, pintura] of Object.entries(LUVAS.pinturas)) {
    const v = validarPintura(ZONAS_DAS_LUVAS, pintura);
    assert.deepEqual(Object.keys(v.zonas).sort(), [...ZONAS_DAS_LUVAS].sort(), faccao);
    assert.equal(v.zonas.couro.acabamento, 'couro');
    assert.equal(v.zonas.tecido.acabamento, 'tecido');
    assert.equal(v.zonas.reforco.acabamento, 'borracha');
  }
  assert.throws(() => validarPintura(ZONAS_DAS_LUVAS, { zonas: { couro: LUVAS.pinturas.tropa.zonas.couro } }), /tecido/);
  assert.throws(() => validarPintura(ZONAS_DAS_LUVAS, { zonas: { ...LUVAS.pinturas.tropa.zonas, tecido: { acabamento: 'linho', cor: '#000000' } } }), /linho/);
});
