// A pega de uma mão e o formato por categoria (Fase 4.1c; desenho, seção 4.3 e 4.4; plano, Tarefa 8): o nó `pega` diz
// quais mãos a regra tem (`extras.luvas.maos`; sem o campo, as duas — as armas da 4.1b), e `lerPega`, `dedosDoClipe` e
// `validarPega` aceitam uma mão só na categoria de uma mão (a faca, só a direita); a mão da frente (o polegar de um lado
// e os quatro dedos do outro) é só do fuzil.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { CATEGORIAS_COM_PEGA, FRENTE_DA_CATEGORIA, MAOS_DA_CATEGORIA, OSSOS_DE_DEDO, ossosDoLado } from '../src/data/luvas.js';
import { dedosDoClipe, lerPega } from '../src/characters/hands/pega.js';
import { validarPega } from '../tools/blender/saidaPega.mjs';

const MARCA = { d: 'a'.repeat(64), e: 'b'.repeat(64) };

/** O glTF da pega com as mãos `maos` (os nós e as trilhas dos dedos delas) e os extras `luvas`. */
function gltfPega({ maos = ['d'], luvas = { marca: { d: MARCA.d }, sondas: { d: {} }, maos: ['d'] }, trilhasDe = maos } = {}) {
  const nodes = [{ name: 'knife', children: [1] }, { name: 'pega', extras: { luvas: JSON.stringify(luvas) }, children: [] }];
  for (const lado of maos) {
    nodes.push({ name: `pega_mao_${lado}`, translation: [1, 2, 3], rotation: [0, 0, 0, 1] });
    nodes[1].children.push(nodes.length - 1);
  }
  nodes.push({ name: 'pega_luvas', children: [] });
  const arm = nodes.length - 1;
  nodes[1].children.push(arm);
  const channels = [];
  for (const lado of trilhasDe) {
    for (const nome of ossosDoLado(lado)) {
      nodes.push({ name: nome, rotation: [0, 0, 0, 1] });
      nodes[arm].children.push(nodes.length - 1);
      if (OSSOS_DE_DEDO.includes(nome.slice(0, -2))) channels.push({ sampler: 0, target: { node: nodes.length - 1, path: 'rotation' } });
    }
  }
  return { scene: 0, scenes: [{ nodes: [0] }], nodes, animations: [{ name: 'empunhadura', channels, samplers: [{ input: 0, output: 1 }] }] };
}

test('categorias: as mãos de cada uma (a faca só com a direita) e a mão da frente só no fuzil', () => {
  assert.deepEqual(MAOS_DA_CATEGORIA, { rifle: ['d', 'e'], pistola: ['d', 'e'], faca: ['d'] });
  assert.deepEqual(FRENTE_DA_CATEGORIA, { rifle: 'e' });
  // cada categoria entra em CATEGORIAS_COM_PEGA com a regra dela no Blender (a faca na Tarefa 9, a pistola na 11)
  for (const c of CATEGORIAS_COM_PEGA) assert.ok(MAOS_DA_CATEGORIA[c], `${c} sem as mãos`);
});

test('lerPega de uma mão: só a direita, os 17 ossos de dedo dela, a marca e as sondas dela', () => {
  const p = lerPega(gltfPega());
  assert.deepEqual(p.lados, ['d']);
  assert.deepEqual(Object.keys(p.maos), ['d']);
  assert.equal(Object.keys(p.trilhas).length, 17);
  assert.ok(Object.keys(p.trilhas).every((n) => n.endsWith('_d')));
  assert.deepEqual(p.marca, { d: MARCA.d });
});

test('lerPega sem o campo `maos`: as duas mãos (as armas da 4.1b)', () => {
  const p = lerPega(gltfPega({ maos: ['d', 'e'], luvas: { marca: MARCA, sondas: { d: {}, e: {} } } }));
  assert.deepEqual(p.lados, ['d', 'e']);
  assert.deepEqual(Object.keys(p.maos).sort(), ['d', 'e']);
  assert.equal(Object.keys(p.trilhas).length, 34);
});

test('lerPega recusa as mãos que não batem com os nós, as trilhas, a marca ou o formato', () => {
  // diz as duas, mas só tem o nó da direita
  assert.throws(() => lerPega(gltfPega({ luvas: { marca: MARCA, sondas: {}, maos: ['d', 'e'] } })), /pega_mao_e/);
  // diz a direita, mas o clipe só gira a esquerda
  assert.throws(() => lerPega(gltfPega({ trilhasDe: ['e'] })), /_d/);
  // sem a marca da mão que tem
  assert.throws(() => lerPega(gltfPega({ luvas: { marca: { e: MARCA.e }, sondas: {}, maos: ['d'] } })), /marca/);
  // a lista das mãos fora do formato
  for (const maos of [[], ['x'], ['e', 'd'], ['d', 'd'], 'd']) {
    assert.throws(() => lerPega(gltfPega({ luvas: { marca: MARCA, sondas: {}, maos } })), /maos/, JSON.stringify(maos));
  }
});

test('dedosDoClipe pede só as mãos da pega', () => {
  const track = (nome) => ({ name: `${nome}.quaternion`, values: new Float32Array([0, 0, 0, 1]) });
  const clip = { tracks: OSSOS_DE_DEDO.map((o) => track(`${o}_d`)) };
  const dedos = dedosDoClipe(clip, ['d']);
  assert.deepEqual(Object.keys(dedos), ['d']);
  assert.equal(Object.keys(dedos.d).length, 17);
  assert.throws(() => dedosDoClipe(clip), /_e/); // sem as mãos, as duas (como antes)
});

const BRACO = { penetracaoMM: 0.1, contatosMM: { palma: 0.2, indicador: 0.3 }, juntosMM: { 'medio-anelar': [2.5, 3] } };

test('validarPega numa categoria de uma mão: só a direita, sem a mão da frente', () => {
  const p = lerPega(gltfPega());
  const rel = { empunhadura: { maos: ['d'], d: BRACO, marca: { d: MARCA.d } } };
  assert.deepEqual(validarPega(rel, p, { d: MARCA.d, e: MARCA.e }, 'faca'), []);
  // o relatório com as mãos diferentes das do .glb, ou das da categoria
  assert.match(validarPega({ empunhadura: { ...rel.empunhadura, maos: ['d', 'e'] } }, p, null, 'faca').join('\n'), /mãos/);
  assert.match(validarPega(rel, p, null, 'rifle').join('\n'), /mãos/);
  // a penetração e os contatos continuam valendo
  const fundo = { empunhadura: { ...rel.empunhadura, d: { ...BRACO, penetracaoMM: 0.5 } } };
  assert.match(validarPega(fundo, p, null, 'faca').join('\n'), /entra 0,50 mm/);
});
