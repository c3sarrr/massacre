// Skins das armas realistas (Fase 4.1a; desenho, seção 6): as tabelas dos acabamentos, das cores e das skins nomeadas,
// o registro das armas realistas (zonas, soquetes, peças, orçamentos, pintura de fábrica) e as contas puras de
// src/weapons/skins/ (acabamento → material, skins de fábrica e nomeadas, os argumentos do comando `skin`).
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { ACABAMENTOS, PADROES } from '../src/data/acabamentos.js';
import { CORES_SKIN } from '../src/data/coresSkin.js';
import { SKINS_ARMA } from '../src/data/skinsArma.js';
import {
  ARMAS_REAIS, CLASSE_DA_CATEGORIA, LODS_REAIS, ORCAMENTOS, PECAS_MOVEIS, ZONAS, orcamentoDaArma, soquetesDaArma,
} from '../src/data/armasReais.js';
import { VIEWMODEL } from '../src/data/viewmodel.js';
import {
  acabamentoParaMaterial, hexParaLinear, normalizarNome, resolverAcabamento, resolverCor, srgbParaLinear,
} from '../src/weapons/skins/acabamento.js';
import {
  FABRICA, aplicarZonas, chaveDaSkin, descreverSkin, lerArgumentosSkin, skinDeFabrica, skinPorNome, validarSkin,
} from '../src/weapons/skins/skin.js';

const HEX = /^#[0-9A-F]{6}$/;

// Os 15 da seção 6.1 do desenho das armas mais os 2 das luvas (4.1b: couro e tecido); a borracha passou a ser a borracha
// moldada (TPR) semifosca das luvas e das armas (0,9 → 0,68, desenho da 4.1b, seção 7.2).
test('acabamentos: os 15 da seção 6.1 e os 2 das luvas com metal e aspereza da tabela', () => {
  const tabela = {
    oxidado: [1, 0.34], fosfatizado: [1, 0.55], fosco: [0, 0.85], acetinado: [0, 0.5], brilhante: [0, 0.25],
    metalico: [0.6, 0.35], perolado: [0.2, 0.3], anodizado: [1, 0.25], escovado: [1, 0.3], cromado: [1, 0.05],
    cerakote: [0, 0.7], carbono: [0, 0.35], madeira: [0, 0.45], polimero: [0, 0.65], borracha: [0, 0.68],
    couro: [0, 0.56], tecido: [0, 0.88],
  };
  assert.deepEqual(Object.keys(ACABAMENTOS).sort(), Object.keys(tabela).sort());
  for (const [id, [metal, aspereza]] of Object.entries(tabela)) {
    const a = ACABAMENTOS[id];
    assert.equal(a.metal, metal, `${id}.metal`);
    assert.equal(a.aspereza, aspereza, `${id}.aspereza`);
    assert.ok(PADROES.includes(a.padrao), `${id}.padrao`);
    assert.match(a.gasto.cor, HEX, `${id}.gasto.cor`);
    assert.ok(a.varAspereza >= 0 && a.varAspereza <= 0.3 && a.varCor >= 0 && a.varCor <= 0.3, `${id}: variações`);
    if (a.duasCores) assert.ok(a.cor2Fator > 0, `${id}.cor2Fator`);
  }
  assert.equal(ACABAMENTOS.brilhante.verniz, 1);
  assert.equal(ACABAMENTOS.brilhante.asperezaVerniz, 0.05);
  assert.equal(ACABAMENTOS.metalico.verniz, 0.8);
  assert.equal(ACABAMENTOS.perolado.iridescencia, 0.8);
  assert.equal(ACABAMENTOS.perolado.iorIridescencia, 1.3);
  assert.deepEqual(ACABAMENTOS.perolado.filme, [250, 600]);
  assert.equal(ACABAMENTOS.anodizado.iridescencia, 0.2);
  assert.equal(ACABAMENTOS.escovado.anisotropia, 0.8);
  assert.equal(ACABAMENTOS.madeira.verniz, 0.6);
  assert.equal(ACABAMENTOS.carbono.padrao, 'carbono');
  assert.equal(ACABAMENTOS.madeira.padrao, 'veio');
  assert.equal(ACABAMENTOS.polimero.padrao, 'pontilhado');
});

test('cores: as 20 da paleta da seção 6.2', () => {
  const tabela = {
    preto: '#1B1B1D', brancoTitanio: '#EDEDE8', cinzaGrafite: '#4A4E54', carmesim: '#9E1B32', vermelho: '#D1362F',
    laranja: '#F28F3B', acafrao: '#E9A13B', amarelo: '#FFD23F', lima: '#9BD13B', verdeFloresta: '#2F5D3A',
    verdeAgua: '#3FB8AF', azulCobalto: '#2F4FB5', azulCeleste: '#5DADE2', roxo: '#6C3FB5', rosa: '#E86FA3',
    marromSiena: '#8C5A3C', areia: '#C2A878', verdeOliva: '#5B5F3A', terracota: '#C8553D', azulTropa: '#2F6DB5',
  };
  assert.deepEqual(Object.fromEntries(Object.entries(CORES_SKIN).map(([k, c]) => [k, c.hex])), tabela);
  for (const c of Object.values(CORES_SKIN)) assert.ok(c.nome.length > 2);
  assert.equal(CORES_SKIN.brancoTitanio.nome, 'Branco Titânio');
  assert.equal(CORES_SKIN.verdeAgua.nome, 'Verde-água');
});

test('skins nomeadas: as três de exemplo, com zonas, acabamentos e cores que existem', () => {
  assert.deepEqual(Object.values(SKINS_ARMA).map((s) => s.nome), ['Anodizado Terracota', 'Cromo e Carbono', 'Madeira Clara e Aço Escovado']);
  for (const [id, s] of Object.entries(SKINS_ARMA)) {
    for (const [zona, z] of Object.entries(s.zonas)) {
      assert.ok(ZONAS.includes(zona), `${id}.${zona}`);
      assert.ok(ACABAMENTOS[z.acabamento], `${id}.${zona}.acabamento`);
      for (const c of [z.cor, z.cor2].filter(Boolean)) assert.ok(CORES_SKIN[c] || HEX.test(c), `${id}.${zona}: cor ${c}`);
      assert.ok(z.desgaste >= 0 && z.desgaste <= 1, `${id}.${zona}.desgaste`);
      if (zona === 'interno') assert.equal(ACABAMENTOS[z.acabamento].metal, 1, `${id}: interno só metal`);
    }
  }
});

test('registro das armas realistas: a AK-47 com zonas, peças, soquetes, orçamento e pintura de fábrica', () => {
  assert.deepEqual(ZONAS, ['corpo', 'guarnicao', 'carregador', 'detalhes', 'interno']);
  assert.deepEqual(LODS_REAIS, ['perto', 'mundo', 'longe']);
  assert.deepEqual(PECAS_MOVEIS, ['ferrolho', 'carregador', 'gatilho', 'cao', 'seletor']);
  const ak = ARMAS_REAIS.ak47;
  assert.equal(ak.categoria, VIEWMODEL.weapons.ak47.category);
  assert.equal(ak.pasta, 'assets/armas/ak47/');
  assert.deepEqual(ak.zonas, ZONAS);
  assert.deepEqual(ak.pecas, ['ferrolho', 'carregador', 'gatilho', 'cao', 'seletor']);
  assert.deepEqual(soquetesDaArma('ak47'), ['boca', 'ejecao', 'carregador', 'mira_tras', 'mira_frente', 'mao_d', 'mao_e']);
  const o = orcamentoDaArma('ak47');
  assert.equal(o, ORCAMENTOS[CLASSE_DA_CATEGORIA.rifle]);
  assert.deepEqual(o.triangulos, { perto: 40000, mundo: 6000, longe: 1500 });
  assert.equal(o.textura, 2048);
  assert.equal(o.texturaMundo, 512);
  assert.equal(o.arquivosMB, 6);
  assert.deepEqual(Object.keys(ak.fabrica.zonas), ZONAS);
  for (const z of Object.values(ak.fabrica.zonas)) {
    assert.ok(ACABAMENTOS[z.acabamento]);
    assert.match(z.cor, HEX);
  }
  assert.equal(ak.fabrica.zonas.interno.acabamento, 'escovado');
  for (const id of Object.keys(ARMAS_REAIS)) assert.ok(VIEWMODEL.weapons[id], `${id} tem categoria no viewmodel`);
});

test('registro × ficha: a pintura de fábrica usa as cores de fábrica da ficha da AK', () => {
  const ficha = JSON.parse(readFileSync(new URL('../tools/blender/refs/ak47.json', import.meta.url), 'utf8'));
  const z = ARMAS_REAIS.ak47.fabrica.zonas;
  assert.equal(ficha.cores.aco.fabrica, z.corpo.cor);
  assert.equal(ficha.cores.aco.fabrica, z.detalhes.cor);
  assert.equal(ficha.cores.madeira.fabrica, z.guarnicao.cor);
  assert.equal(ficha.cores.madeira.fabricaEscura, z.guarnicao.cor2);
  assert.equal(ficha.cores.carregador.fabrica, z.carregador.cor);
  assert.equal(ficha.cores.acoPolido.fabrica, z.interno.cor);
});

test('nomes: sem acento, sem espaço, cor pela chave, pelo nome ou em hex; acabamento pelo nome da tabela', () => {
  assert.equal(normalizarNome('Branco Titânio'), 'brancotitanio');
  assert.equal(normalizarNome('verde-água'), 'verdeagua');
  assert.equal(resolverCor('Branco Titânio'), '#EDEDE8');
  assert.equal(resolverCor('branco-titanio'), '#EDEDE8');
  assert.equal(resolverCor('brancoTitanio'), '#EDEDE8');
  assert.equal(resolverCor('#abcdef'), '#ABCDEF');
  assert.equal(resolverCor('abcdef'), '#ABCDEF');
  assert.equal(resolverCor('ciano'), null);
  assert.equal(resolverAcabamento('Aço escovado'), 'escovado');
  assert.equal(resolverAcabamento('fibra de carbono'), 'carbono');
  assert.equal(resolverAcabamento('verniz'), null);
});

test('cor: sRGB → linear (IEC 61966-2-1)', () => {
  assert.equal(srgbParaLinear(0), 0);
  assert.equal(srgbParaLinear(1), 1);
  assert.ok(Math.abs(srgbParaLinear(0.04045) - 0.04045 / 12.92) < 1e-12);
  assert.ok(Math.abs(hexParaLinear('#808080')[0] - 0.2158605) < 1e-6);
  assert.deepEqual(hexParaLinear('#FFFFFF'), [1, 1, 1]);
});

test('acabamento → material: números da tabela, recursos só quando o acabamento pede, segunda cor e desgaste', () => {
  const ox = acabamentoParaMaterial({ acabamento: 'oxidado', cor: '#303135', desgaste: 0.22 });
  assert.equal(ox.acabamento, 'oxidado');
  assert.equal(ox.metalness, 1);
  assert.equal(ox.roughness, 0.34);
  assert.deepEqual(ox.recursos, []);
  assert.equal(ox.clearcoat, 0);
  assert.equal(ox.padrao, 'fino');
  assert.equal(ox.padraoId, 1);
  assert.equal(ox.color2, null);
  assert.equal(ox.desgaste, 0.22);
  assert.deepEqual(ox.gasto.color, hexParaLinear('#A7ABB0'));
  const br = acabamentoParaMaterial({ acabamento: 'brilhante', cor: 'vermelho' });
  assert.deepEqual(br.recursos, ['verniz']);
  assert.equal(br.clearcoat, 1);
  assert.equal(br.clearcoatRoughness, 0.05);
  const pe = acabamentoParaMaterial({ acabamento: 'Perolado', cor: 'rosa' });
  assert.deepEqual(pe.recursos, ['verniz', 'iridescencia']);
  assert.equal(pe.iridescence, 0.8);
  assert.equal(pe.iridescenceIOR, 1.3);
  assert.deepEqual(pe.iridescenceThicknessRange, [250, 600]);
  const es = acabamentoParaMaterial({ acabamento: 'escovado', cor: '#ADADAF' });
  assert.deepEqual(es.recursos, ['anisotropia']);
  assert.equal(es.anisotropy, 0.8);
  const md = acabamentoParaMaterial({ acabamento: 'madeira', cor: '#A4673F' });
  assert.deepEqual(md.color2, md.color.map((c) => c * 0.45), 'sem cor2, o veio sai da cor pelo fator');
  const md2 = acabamentoParaMaterial({ acabamento: 'madeira', cor: '#A4673F', cor2: '#794224' });
  assert.deepEqual(md2.color2, hexParaLinear('#794224'));
  const cb = acabamentoParaMaterial({ acabamento: 'carbono', cor: 'preto' });
  assert.ok(cb.color2.every((c, i) => c > cb.color[i]), 'a trama clara sai mais clara que o preto');
  assert.equal(acabamentoParaMaterial({ acabamento: 'fosco', cor: 'preto', desgaste: 7 }).desgaste, 1);
  assert.equal(acabamentoParaMaterial({ acabamento: 'fosco', cor: 'preto', desgaste: -1 }).desgaste, 0);
  assert.throws(() => acabamentoParaMaterial({ acabamento: 'verniz', cor: 'preto' }), /acabamento desconhecido/);
  assert.throws(() => acabamentoParaMaterial({ acabamento: 'fosco', cor: 'ciano' }), /cor desconhecida/);
});

test('skins: fábrica, nomeadas por cima da fábrica, chave estável e validação', () => {
  const fab = skinDeFabrica('ak47');
  assert.equal(fab.chave, FABRICA);
  assert.equal(fab.nome, 'De fábrica');
  assert.deepEqual(Object.keys(fab.zonas), ZONAS);
  assert.equal(fab.zonas.guarnicao.cor2, '#794224');
  const cc = skinPorNome('ak47', 'Cromo e Carbono');
  assert.equal(cc.chave, 'cromoECarbono');
  assert.equal(cc.zonas.corpo.acabamento, 'cromado');
  assert.equal(cc.zonas.guarnicao.cor2, '#4A4E54');
  assert.deepEqual(skinPorNome('ak47', 'fabrica'), fab);
  assert.equal(skinPorNome('ak47', 'madeira clara e aco escovado').chave, 'madeiraClaraEAcoEscovado');
  assert.throws(() => skinPorNome('ak47', 'Dourada'), /skin desconhecida/);
  assert.equal(chaveDaSkin(fab), 'fabrica');
  const p1 = aplicarZonas('ak47', fab, { zonas: { corpo: { acabamento: 'fosco', cor: 'preto' } }, desgaste: null });
  const p2 = aplicarZonas('ak47', fab, { zonas: { corpo: { acabamento: 'fosco', cor: 'preto' } }, desgaste: null });
  assert.equal(p1.chave, 'personalizada');
  assert.equal(chaveDaSkin(p1), chaveDaSkin(p2), 'a mesma skin personalizada dá a mesma chave');
  assert.notEqual(chaveDaSkin(p1), chaveDaSkin(fab));
  assert.throws(() => validarSkin('ak47', { ...fab, zonas: { ...fab.zonas, interno: { acabamento: 'fosco', cor: '#FFFFFF', desgaste: 0 } } }),
    /interno só aceita acabamento de metal/);
  const linhas = descreverSkin(fab);
  assert.equal(linhas.length, ZONAS.length);
  assert.match(linhas[0], /^corpo: Oxidado de fábrica #303135 · desgaste 0,22$/);
});

test('comando skin: leitura dos argumentos', () => {
  assert.deepEqual(lerArgumentosSkin([]), { tipo: 'mostrar' });
  assert.deepEqual(lerArgumentosSkin(['fabrica']), { tipo: 'nome', nome: FABRICA });
  assert.deepEqual(lerArgumentosSkin(['Fábrica']), { tipo: 'nome', nome: FABRICA });
  assert.deepEqual(lerArgumentosSkin(['Anodizado', 'Terracota']), { tipo: 'nome', nome: 'anodizadoTerracota' });
  assert.deepEqual(lerArgumentosSkin(['corpo=anodizado:terracota', 'guarnição=madeira:areia,marrom-siena', 'desgaste=0,3']), {
    tipo: 'zonas',
    zonas: {
      corpo: { acabamento: 'anodizado', cor: '#C8553D', cor2: null },
      guarnicao: { acabamento: 'madeira', cor: '#C2A878', cor2: '#8C5A3C' },
    },
    desgaste: 0.3,
  });
  assert.deepEqual(lerArgumentosSkin(['desgaste=1']), { tipo: 'zonas', zonas: {}, desgaste: 1 });
  assert.throws(() => lerArgumentosSkin(['Dourada']), /skin desconhecida: Dourada/);
  assert.throws(() => lerArgumentosSkin(['cano=fosco:preto']), /zona desconhecida: cano/);
  assert.throws(() => lerArgumentosSkin(['corpo=verniz:preto']), /acabamento desconhecido: verniz/);
  assert.throws(() => lerArgumentosSkin(['corpo=fosco:ciano']), /cor desconhecida: ciano/);
  assert.throws(() => lerArgumentosSkin(['corpo=fosco']), /use <zona>=<acabamento>:<cor>/);
  assert.throws(() => lerArgumentosSkin(['desgaste=2']), /desgaste entre 0 e 1/);
});

test('comando skin: aplicar zonas na skin atual (desgaste nas zonas citadas, ou em todas sem zona)', () => {
  const fab = skinDeFabrica('ak47');
  const a = aplicarZonas('ak47', fab, lerArgumentosSkin(['corpo=anodizado:terracota', 'desgaste=0.4']));
  assert.equal(a.zonas.corpo.acabamento, 'anodizado');
  assert.equal(a.zonas.corpo.cor, '#C8553D');
  assert.equal(a.zonas.corpo.desgaste, 0.4);
  assert.equal(a.zonas.guarnicao.desgaste, fab.zonas.guarnicao.desgaste, 'as outras zonas ficam');
  const b = aplicarZonas('ak47', fab, lerArgumentosSkin(['desgaste=0']));
  for (const z of ZONAS) assert.equal(b.zonas[z].desgaste, 0);
  assert.throws(() => aplicarZonas('ak47', fab, lerArgumentosSkin(['interno=fosco:preto'])), /interno só aceita acabamento de metal/);
});
