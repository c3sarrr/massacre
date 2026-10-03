// A pega das luvas no .glb das armas (Fase 4.1b; desenho, seção 6.4; plano, Tarefa 7 e D1): `lerPega` (os nós `pega`,
// `pega_mao_d` e `pega_mao_e`, o clipe `empunhadura` com as rotações dos 34 ossos de dedo, a marca do rig e as sondas
// nos extras, e o afundamento da palma — a palma que cede, 4.1c), a validação da seção `empunhadura` do relatório e a
// AK de verdade depois do construir, com a marca igual à do luvas.glb.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { existsSync, readFileSync } from 'node:fs';
import { join } from 'node:path';
import { LIMITES_DA_PEGA, OSSOS_DE_DEDO, ossosDoLado } from '../src/data/luvas.js';
import { lerPega } from '../src/characters/hands/pega.js';
import { lerGlb, validarSaida } from '../tools/blender/saida.mjs';
import { validarPega } from '../tools/blender/saidaPega.mjs';

const ROOT = join(import.meta.dirname, '..');
const MARCA = { d: 'a'.repeat(64), e: 'b'.repeat(64) };
const SONDAS = {
  d: { palma: { vertice: 12, mm: 0.03 }, indicador_gatilho: { vertice: 400, mm: 0.02 }, polegar: { vertice: 900, mm: 0.04 } },
  e: { palma: { vertice: 15, mm: 0.04 }, polegar: { vertice: 901, mm: 0.05 } },
};
// o afundamento da palma de cada mão (mm, no referencial do braço com o osso mao em repouso, no do Blender)
const PALMA = {
  d: { vertices: [12, 13, 40], vetores: [[0, 0, 2.5], [0, 0.3, 1.9], [0.1, 0, 0.6]] },
  e: { vertices: [15, 16], vetores: [[0, 0, 1.2], [0, 0, 0.4]] },
};
// a capacidade de cada braço nas luvas (os extras do luvas.glb)
const CAPACIDADE = { d: { vertices: [12, 13, 40, 41], mm: [4.9, 3.1, 2.2, 1] }, e: { vertices: [15, 16], mm: [3, 3] } };

/** O glTF da pega: a raiz da arma, o nó `pega` com os extras, as duas mãos e a armadura com os 40 ossos; o clipe gira os
 *  ossos de `giram` (por padrão os 34 de dedo) e, como o exportador com amostragem, move todos. */
function gltfPega({ extras = { luvas: JSON.stringify({ marca: MARCA, sondas: SONDAS, palma: PALMA }) }, maos = ['d', 'e'],
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
  assert.deepEqual(p.palma, PALMA);
});

test('lerPega aceita os extras já como objeto', () => {
  const p = lerPega(gltfPega({ extras: { luvas: { marca: MARCA, sondas: SONDAS, palma: PALMA } } }));
  assert.deepEqual(p.marca, MARCA);
});

test('lerPega recusa a pega sem o afundamento da palma de uma mão (a palma que cede)', () => {
  const semPalma = { marca: MARCA, sondas: SONDAS, palma: { d: PALMA.d } };
  assert.throws(() => lerPega(gltfPega({ extras: { luvas: semPalma } })), /palma e/);
  const torta = { marca: MARCA, sondas: SONDAS, palma: { d: PALMA.d, e: { vertices: [15, 16], vetores: [[0, 0, 1]] } } };
  assert.throws(() => lerPega(gltfPega({ extras: { luvas: torta } })), /palma e/);
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
  assert.throws(() => lerPega(gltfPega({ extras: { luvas: { sondas: SONDAS, palma: PALMA } } })), /marca/);
});

const REL_OK = {
  empunhadura: {
    d: {
      penetracaoMM: 0.05, contatosMM: { palma: 0.03, indicador_gatilho: 0.02, polegar: 0.04 },
      lados: { polegarMM: 14.2, dedosMM: { medio: -12.5, anelar: -13.1, minimo: -11.8 } },
      juntosMM: { 'medio-anelar': [2.45, 0.98], 'anelar-minimo': [3.34, 4.55] },
      palma: { afundaMM: 2.5, vertices: 3, encostam: 2, alemMM: 0 },
    },
    e: {
      penetracaoMM: 0.04, contatosMM: { palma: 0.04, polegar: 0.05 },
      lados: { polegarMM: 19.6, dedosMM: { indicador: -18.4, medio: -19.9, anelar: -18.7, minimo: -17.2 } },
      polegar: { curvaGraus: 0, trechosMM: [6.48, 5.23, 4.01, 2.36, 0.2, 0.09] },
      juntosMM: { 'indicador-medio': [3.98, 9.71], 'medio-anelar': [2.64, 3.72], 'anelar-minimo': [6.77, 15.68] },
      palma: { afundaMM: 1.2, vertices: 2, encostam: 1, alemMM: 0.12 },
    },
    frente: 'e',
    marca: MARCA,
  },
};

test('validarPega aprova o relatório e o .glb certos', () => {
  assert.deepEqual(validarPega(REL_OK, lerPega(gltfPega()), MARCA), []);
  assert.deepEqual(validarPega(REL_OK, lerPega(gltfPega()), MARCA, 'rifle', CAPACIDADE), []);
});

test('validarPega confere a palma afundada: o .glb e o relatório batendo, nada além do que cede', () => {
  const semPalma = structuredClone(REL_OK);
  delete semPalma.empunhadura.e.palma;
  assert.match(validarPega(semPalma, lerPega(gltfPega()), MARCA).join('\n'), /empunhadura e: o relatório sem o afundamento/);
  const outroMaior = structuredClone(REL_OK);
  outroMaior.empunhadura.d.palma.afundaMM = 3.1;
  assert.match(validarPega(outroMaior, lerPega(gltfPega()), MARCA).join('\n'), /empunhadura d: o afundamento da palma do \.glb/);
  const outraConta = structuredClone(REL_OK);
  outraConta.empunhadura.e.palma.vertices = 5;
  assert.match(validarPega(outraConta, lerPega(gltfPega()), MARCA).join('\n'), /empunhadura e: o afundamento/);
  // o que ainda entra na arma além do que a palma cede é colisão
  const alem = structuredClone(REL_OK);
  alem.empunhadura.d.palma.alemMM = 0.4;
  assert.match(validarPega(alem, lerPega(gltfPega()), MARCA).join('\n'), /palma entra 0,40 mm na arma além do que cede/);
  // com as luvas construídas, cada vértice afunda até o que ele cede nelas
  const pouco = structuredClone(CAPACIDADE);
  pouco.d.mm[1] = 1.5;
  assert.match(validarPega(REL_OK, lerPega(gltfPega()), MARCA, 'rifle', pouco).join('\n'), /1 vértices da palma afundam além.*13/);
  const outraLuva = structuredClone(CAPACIDADE);
  outraLuva.e.vertices = [99, 100];
  assert.match(validarPega(REL_OK, lerPega(gltfPega()), MARCA, 'rifle', outraLuva).join('\n'), /empunhadura e: 2 vértices/);
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

test('validarPega exige na mão da frente só o polegar de um lado e os quatro dedos do outro', () => {
  const semLados = structuredClone(REL_OK);
  delete semLados.empunhadura.e.lados;
  assert.match(validarPega(semLados, lerPega(gltfPega()), MARCA).join('\n'), /mão da frente.*lados/);
  const semFrente = structuredClone(REL_OK);
  delete semFrente.empunhadura.frente;
  assert.match(validarPega(semFrente, lerPega(gltfPega()), MARCA).join('\n'), /mão da frente/);
  const faltaDedo = structuredClone(REL_OK);
  delete faltaDedo.empunhadura.e.lados.dedosMM.minimo;
  assert.match(validarPega(faltaDedo, lerPega(gltfPega()), MARCA).join('\n'), /minimo/);
  const indicadorTrocado = structuredClone(REL_OK);
  indicadorTrocado.empunhadura.e.lados.dedosMM.indicador = 6.1;
  assert.match(validarPega(indicadorTrocado, lerPega(gltfPega()), MARCA).join('\n'), /indicador.*lado do polegar/);
  // perto demais do meio da arma (dentro da margem) também reprova: o dedo não chegou ao outro lado
  const noMeio = structuredClone(REL_OK);
  noMeio.empunhadura.e.lados.dedosMM.anelar = -(LIMITES_DA_PEGA.ladoMM - 0.5);
  assert.match(validarPega(noMeio, lerPega(gltfPega()), MARCA).join('\n'), /anelar/);
  const polegarTrocado = structuredClone(REL_OK);
  polegarTrocado.empunhadura.e.lados.polegarMM = -15;
  assert.match(validarPega(polegarTrocado, lerPega(gltfPega()), MARCA).join('\n'), /polegar.*lado dos dedos/);
  // a mão do gatilho, quando traz os lados, passa pela mesma conta
  const gatilho = structuredClone(REL_OK);
  gatilho.empunhadura.d.lados.dedosMM.medio = 3;
  assert.match(validarPega(gatilho, lerPega(gltfPega()), MARCA).join('\n'), /empunhadura d.*medio/);
});

test('validarPega exige na mão da frente o polegar reto e deitado na arma (sem a curva)', () => {
  const semPolegar = structuredClone(REL_OK);
  delete semPolegar.empunhadura.e.polegar;
  assert.match(validarPega(semPolegar, lerPega(gltfPega()), MARCA).join('\n'), /polegar.*deitado/);
  // a versão que o usuário recusou: o polegar em arco (MCP 35°, IP 17°), só com a ponta encostada
  const curvo = structuredClone(REL_OK);
  curvo.empunhadura.e.polegar.curvaGraus = 52;
  assert.match(validarPega(curvo, lerPega(gltfPega()), MARCA).join('\n'), /curva/);
  const pontaNoAr = structuredClone(REL_OK);
  for (const i of [3, 4, 5]) pontaNoAr.empunhadura.e.polegar.trechosMM[i] = LIMITES_DA_PEGA.contatoMM + 0.5;
  assert.match(validarPega(pontaNoAr, lerPega(gltfPega()), MARCA).join('\n'), /distal/);
  const baseLonge = structuredClone(REL_OK);
  baseLonge.empunhadura.e.polegar.trechosMM[0] = LIMITES_DA_PEGA.polegarFolgaMM + 1;
  assert.match(validarPega(baseLonge, lerPega(gltfPega()), MARCA).join('\n'), /proximal/);
});

test('validarPega exige os dedos que abraçam a arma lado a lado, sem leque', () => {
  const semJuntos = structuredClone(REL_OK);
  delete semJuntos.empunhadura.e.juntosMM;
  assert.match(validarPega(semJuntos, lerPega(gltfPega()), MARCA).join('\n'), /mão da frente.*lado a lado/);
  const faltaPar = structuredClone(REL_OK);
  delete faltaPar.empunhadura.e.juntosMM['indicador-medio'];
  assert.match(validarPega(faltaPar, lerPega(gltfPega()), MARCA).join('\n'), /indicador-medio/);
  // o leque da primeira pega da mão da frente da AK: a falange média do mínimo a 8,53 mm da do anelar
  const leque = structuredClone(REL_OK);
  leque.empunhadura.e.juntosMM['anelar-minimo'][0] = 8.53;
  assert.match(validarPega(leque, lerPega(gltfPega()), MARCA).join('\n'), /anelar-minimo.*leque/);
  // só a falange média conta: a ponta do dedo que dobra mais pode sair da do vizinho
  const pontas = structuredClone(REL_OK);
  pontas.empunhadura.e.juntosMM['indicador-medio'][1] = 20;
  assert.deepEqual(validarPega(pontas, lerPega(gltfPega()), MARCA), []);
  // a mão do gatilho passa pela mesma conta nos dedos que abraçam o punho
  const gatilho = structuredClone(REL_OK);
  gatilho.empunhadura.d.juntosMM['medio-anelar'][0] = LIMITES_DA_PEGA.dedosJuntosMM + 1;
  assert.match(validarPega(gatilho, lerPega(gltfPega()), MARCA).join('\n'), /empunhadura d.*medio-anelar/);
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
