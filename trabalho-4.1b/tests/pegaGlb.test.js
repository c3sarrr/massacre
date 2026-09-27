// A pega das luvas no .glb das armas (Fase 4.1b; desenho, seção 6.4; plano, Tarefa 7 e D1): `lerPega` (os nós `pega`,
// `pega_mao_d` e `pega_mao_e`, o clipe `empunhadura` com as rotações dos 34 ossos de dedo, a marca do rig e as sondas
// nos extras), a validação da seção `empunhadura` do relatório e a AK de verdade depois do construir, com a marca igual
// à do luvas.glb.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { existsSync, readFileSync } from 'node:fs';
import { join } from 'node:path';
import { OSSOS_DE_DEDO, ossosDoLado } from '../src/data/luvas.js';
import { lerPega } from '../src/characters/hands/pega.js';
import { lerGlb, validarSaida } from '../tools/blender/saida.mjs';
import { validarPega } from '../tools/blender/saidaPega.mjs';

const ROOT = join(import.meta.dirname, '..');
const MARCA = { d: 'a'.repeat(64), e: 'b'.repeat(64) };
const SONDAS = {
  d: { palma: { vertice: 12, mm: 0.03 }, indicador_gatilho: { vertice: 400, mm: 0.02 }, polegar: { vertice: 900, mm: 0.04 } },
  e: { palma: { vertice: 15, mm: 0.04 }, polegar: { vertice: 901, mm: 0.05 } },
};

/** O glTF da pega: a raiz da arma, o nó `pega` com os extras, as duas mãos e a armadura com os 40 ossos; o clipe gira os
 *  ossos de `giram` (por padrão os 34 de dedo) e, como o exportador com amostragem, move todos. */
function gltfPega({ extras = { luvas: JSON.stringify({ marca: MARCA, sondas: SONDAS }) }, maos = ['d', 'e'],
  giram = [...OSSOS_DE_DEDO.map((o) => `${o}_d`), ...OSSOS_DE_DEDO.map((o) => `${o}_e`)], comClipe = true } = {}) {
  const nodes = [{ name: 'ak47', children: [1] }, { name: 'pega', extras, children: [] }];
  for (const lado of maos) {
    nodes.push({ name: `pega_mao_${lado}`, translation: [1, 2, 3], rotation: [0, 0, 0, 1] });
    nodes[1].children.push(nodes.length - 1);
  }
  nodes.push({ name: 'pega_luvas', children: [] });
  const arm = nodes.length - 1;
  nodes[1].children.push(arm);
  const indice = {};
  for (const nome of new Set([...ossosDoLado('d'), ...ossosDoLado('e'), ...giram])) {
    nodes.push({ name: nome, rotation: [0, 0, 0, 1] });
    indice[nome] = nodes.length - 1;
    nodes[arm].children.push(nodes.length - 1);
  }
  const channels = [];
  for (const nome of giram) channels.push({ sampler: 0, target: { node: indice[nome], path: 'rotation' } });
  for (const nome of ossosDoLado('d')) channels.push({ sampler: 1, target: { node: indice[nome], path: 'translation' } });
  const animations = comClipe ? [{ name: 'empunhadura', channels, samplers: [{ input: 0, output: 1 }, { input: 0, output: 2 }] }] : [];
  return { scene: 0, scenes: [{ nodes: [0] }], nodes, animations };
}

test('lerPega acha as duas mãos, as 34 trilhas de dedo, a marca e as sondas', () => {
  const p = lerPega(gltfPega());
  assert.deepEqual(Object.keys(p.maos).sort(), ['d', 'e']);
  assert.deepEqual(p.maos.d.posicao, [1, 2, 3]);
  assert.deepEqual(p.maos.d.rotacao, [0, 0, 0, 1]);
  assert.equal(Object.keys(p.trilhas).length, 34);
  assert.ok(p.trilhas.indicador_1_d >= 0 && p.trilhas.minimo_0_e >= 0);
  assert.deepEqual(p.marca, MARCA);
  assert.equal(p.sondas.d.indicador_gatilho.vertice, 400);
});

test('lerPega aceita os extras já como objeto', () => {
  const p = lerPega(gltfPega({ extras: { luvas: { marca: MARCA, sondas: SONDAS } } }));
  assert.deepEqual(p.marca, MARCA);
});

test('lerPega recusa a pega sem uma das mãos', () => {
  assert.throws(() => lerPega(gltfPega({ maos: ['d'] })), /pega_mao_e/);
});

test('lerPega recusa o clipe sem um osso de dedo', () => {
  const giram = [...OSSOS_DE_DEDO.map((o) => `${o}_d`), ...OSSOS_DE_DEDO.map((o) => `${o}_e`)].filter((n) => n !== 'minimo_3_e');
  assert.throws(() => lerPega(gltfPega({ giram })), /minimo_3_e/);
});

test('lerPega recusa trilha em osso de nome desconhecido', () => {
  const giram = [...OSSOS_DE_DEDO.map((o) => `${o}_d`), ...OSSOS_DE_DEDO.map((o) => `${o}_e`), 'mindinho_1_d'];
  assert.throws(() => lerPega(gltfPega({ giram })), /desconhecid/);
});

test('lerPega recusa sem o clipe, sem o nó pega ou sem a marca', () => {
  assert.throws(() => lerPega(gltfPega({ comClipe: false })), /empunhadura/);
  const semPega = gltfPega();
  semPega.nodes[1].name = 'outro';
  assert.throws(() => lerPega(semPega), /pega/);
  assert.throws(() => lerPega(gltfPega({ extras: { luvas: { sondas: SONDAS } } })), /marca/);
});

const REL_OK = {
  empunhadura: {
    d: { penetracaoMM: 0.05, contatosMM: { palma: 0.03, indicador_gatilho: 0.02, polegar: 0.04 } },
    e: { penetracaoMM: 0.04, contatosMM: { palma: 0.04, polegar: 0.05 } },
    marca: MARCA,
  },
};

test('validarPega aprova o relatório e o .glb certos', () => {
  assert.deepEqual(validarPega(REL_OK, lerPega(gltfPega()), MARCA), []);
});

test('validarPega aponta o relatório sem a empunhadura, a penetração, o contato e a marca', () => {
  assert.match(validarPega({}, lerPega(gltfPega()), MARCA).join('\n'), /empunhadura/);
  const fundo = structuredClone(REL_OK);
  fundo.empunhadura.d.penetracaoMM = 0.35;
  assert.match(validarPega(fundo, lerPega(gltfPega()), MARCA).join('\n'), /0,35|0\.35/);
  const longe = structuredClone(REL_OK);
  longe.empunhadura.e.contatosMM.polegar = 1.2;
  assert.match(validarPega(longe, lerPega(gltfPega()), MARCA).join('\n'), /polegar/);
  assert.match(validarPega(REL_OK, lerPega(gltfPega()), { d: 'c'.repeat(64), e: MARCA.e }).join('\n'), /marca/);
});

test('a AK de verdade: a pega no .glb, a marca igual à do luvas.glb e a saída aprovada', () => {
  const ak = join(ROOT, 'assets', 'armas', 'ak47', 'ak47.glb');
  const luvas = join(ROOT, 'assets', 'maos', 'luvas.glb');
  assert.ok(existsSync(ak) && existsSync(luvas), 'rode npm run blender -- construir todas');
  const p = lerPega(lerGlb(readFileSync(ak)).json);
  const marcaLuvas = lerGlb(readFileSync(luvas)).json.nodes.find((n) => n.name === 'luvas').extras.marca;
  assert.deepEqual(p.marca, marcaLuvas);
  assert.deepEqual(validarSaida('ak47', ROOT).problemas, []);
});
