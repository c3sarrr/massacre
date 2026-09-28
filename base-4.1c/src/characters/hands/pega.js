// A pega das luvas numa arma realista (Fase 4.1b; desenho em docs/superpowers/specs/2026-09-26-4.1b-luvas-e-
// empunhadura-design.md, seção 6.4; plano, D1): o que o solver de empunhadura do Blender grava no .glb da arma e o jogo
// lê pelo bloco JSON do glTF (o `parser.json` do GLTFLoader, ou o JSON cru nos testes e no validador da saída).
//  - o nó `pega` (debaixo da raiz da arma), com `extras.luvas` = {marca: {d, e}, sondas: {lado: {contato: {vertice, mm}}}}
//    (a marca do rig de cada braço, D4 — o jogo só aplica a pega a luvas com a mesma marca — e o vértice de cada contato
//    da regra com a distância que o Blender mediu, que o `luvas_contato` refaz com o skinning do three); o exportador
//    grava os extras como texto JSON ou como objeto, e os dois servem;
//  - os nós `pega_mao_d` e `pega_mao_e`, filhos de `pega`: o referencial do osso `mao` de cada braço na pose, no da arma
//    (u); o braço põe o pulso ali;
//  - a animação `empunhadura`: um quadro com a rotação dos 17 ossos de dedo de cada mão (OSSOS_DE_DEDO) nos nós da
//    armadura `pega_luvas`, com os nomes do luvas.glb; o exportador com amostragem grava também a posição e a escala, e
//    o jogo usa só as rotações. Trilha em nó de nome que não é osso das luvas é erro (o esqueleto errado).
// No jogo, `pegaDoGltf` junta as três coisas para os braços (a marca, os dedos do clipe carregado e o referencial do osso
// `mao` de cada lado no da raiz da arma).
import * as THREE from 'three';
import { OSSOS_DE_DEDO, ossosDoLado } from '../../data/luvas.js';

const LADOS = ['d', 'e'];
const MARCA = /^[0-9a-f]{64}$/;

function extrasDasLuvas(no) {
  const bruto = no.extras?.luvas;
  if (bruto === undefined) throw new Error('pega: o nó pega sem os extras das luvas (marca e sondas)');
  let luvas;
  try {
    luvas = typeof bruto === 'string' ? JSON.parse(bruto) : bruto;
  } catch (e) {
    throw new Error(`pega: os extras das luvas não são JSON (${e.message})`);
  }
  for (const lado of LADOS) {
    if (!MARCA.test(luvas?.marca?.[lado] ?? '')) throw new Error(`pega: sem a marca do rig ${lado} nos extras`);
  }
  return luvas;
}

/**
 * Lê a pega do glTF de uma arma. Devolve {pega: índice do nó, maos: {d|e: {no, posicao, rotacao}}, trilhas: {osso_lado:
 * índice do nó}, marca: {d, e}, sondas: {d, e}}; lança com a explicação se falta alguma parte.
 */
export function lerPega(json) {
  const nos = json.nodes ?? [];
  const iPega = nos.findIndex((n) => n.name === 'pega');
  if (iPega < 0) throw new Error('pega: o .glb não tem o nó pega');
  const pega = nos[iPega];
  const luvas = extrasDasLuvas(pega);
  const filhos = pega.children ?? [];
  const maos = {};
  for (const lado of LADOS) {
    const i = filhos.find((k) => nos[k]?.name === `pega_mao_${lado}`);
    if (i === undefined) throw new Error(`pega: falta o nó pega_mao_${lado} dentro de pega`);
    maos[lado] = { no: i, posicao: nos[i].translation ?? [0, 0, 0], rotacao: nos[i].rotation ?? [0, 0, 0, 1] };
  }
  const clipe = (json.animations ?? []).find((a) => a.name === 'empunhadura');
  if (!clipe) throw new Error('pega: o .glb não tem a animação empunhadura');
  const ossos = new Set([...ossosDoLado('d'), ...ossosDoLado('e')]);
  const trilhas = {};
  for (const canal of clipe.channels ?? []) {
    const nome = nos[canal.target?.node]?.name;
    if (!ossos.has(nome)) throw new Error(`pega: trilha no nó desconhecido ${nome} (não é osso das luvas)`);
    if (canal.target.path === 'rotation') trilhas[nome] = canal.target.node;
  }
  for (const lado of LADOS) {
    for (const osso of OSSOS_DE_DEDO) {
      if (trilhas[`${osso}_${lado}`] === undefined) throw new Error(`pega: o clipe sem a rotação de ${osso}_${lado}`);
    }
  }
  for (const nome of Object.keys(trilhas)) {
    if (!OSSOS_DE_DEDO.includes(nome.slice(0, -2))) delete trilhas[nome];
  }
  return { pega: iPega, maos, trilhas, marca: luvas.marca, sondas: luvas.sondas ?? {} };
}

/**
 * Os quaternions dos 17 ossos de dedo de cada mão no clipe `empunhadura` carregado pelo GLTFLoader (um
 * THREE.AnimationClip com as trilhas `<osso>_<lado>.quaternion`): {d: {osso: [x, y, z, w]}, e: {...}}, o primeiro
 * quadro de cada trilha. As outras trilhas do clipe (posição e escala da amostragem, os ossos do braço) ficam de fora.
 */
export function dedosDoClipe(clip) {
  const dedos = { d: {}, e: {} };
  for (const t of clip?.tracks ?? []) {
    const m = /^(.+)_([de])\.quaternion$/.exec(t.name);
    if (!m || !OSSOS_DE_DEDO.includes(m[1])) continue;
    if (t.values.length < 4) throw new Error(`pega: a trilha ${t.name} sem quadro`);
    dedos[m[2]][m[1]] = Array.from(t.values.slice(0, 4));
  }
  for (const lado of LADOS) {
    for (const osso of OSSOS_DE_DEDO) if (!dedos[lado][osso]) throw new Error(`pega: o clipe sem a rotação de ${osso}_${lado}`);
  }
  return dedos;
}

// O exportador do glTF leva os objetos para o Y para cima conjugando (C·R·C⁻¹) e os ossos só pela esquerda (C·R: o osso
// fica com os eixos locais do Blender), com C = Rx(−90°): o osso `mao` na pose, que o Blender gravou no nó `pega_mao_*`,
// tem no jogo a rotação do nó vezes C.
const C = Object.freeze(new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(1, 0, 0), -Math.PI / 2));

/**
 * A pega de uma arma carregada pelo GLTFLoader, pronta para os braços de luva: `lerPega` confere as partes no JSON cru
 * (`gltf.parser.json`), `dedosDoClipe` tira os dedos do clipe carregado, e o referencial do osso `mao` de cada lado sai
 * do nó `pega_mao_*` no referencial da raiz da arma (u).
 * @param {{scene:THREE.Object3D, animations:THREE.AnimationClip[], parser:{json:object}}} gltf
 * @param {string} id o nome da raiz da arma no .glb
 * @returns {{marca:{d:string, e:string}, sondas:object, dedos:{d:object, e:object},
 *   maos:{d:{posicao:THREE.Vector3, quaternion:THREE.Quaternion}, e:{posicao:THREE.Vector3, quaternion:THREE.Quaternion}}}}
 */
export function pegaDoGltf(gltf, id) {
  const lida = lerPega(gltf.parser.json);
  const dedos = dedosDoClipe((gltf.animations ?? []).find((a) => a.name === 'empunhadura'));
  const raiz = gltf.scene.getObjectByName(id);
  if (!raiz) throw new Error(`pega: o .glb não tem a raiz ${id}`);
  gltf.scene.updateMatrixWorld(true);
  const inv = new THREE.Matrix4().copy(raiz.matrixWorld).invert();
  const maos = {};
  for (const lado of LADOS) {
    const no = gltf.scene.getObjectByName(`pega_mao_${lado}`);
    const posicao = new THREE.Vector3();
    const quaternion = new THREE.Quaternion();
    new THREE.Matrix4().multiplyMatrices(inv, no.matrixWorld).decompose(posicao, quaternion, new THREE.Vector3());
    maos[lado] = { posicao, quaternion: quaternion.multiply(C) };
  }
  return { marca: lida.marca, sondas: lida.sondas, dedos, maos };
}
