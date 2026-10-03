// Utilitários dos testes das luvas de verdade (Fase 4.1b): o decodificador Draco do vendor carregado no Node, os
// atributos e os índices de uma primitiva comprimida, e o modelo das dobras de um braço montado do luvas.glb (as
// primitivas por zona, o esqueleto pelas matrizes de ligação inversas e as correções dos extras), como o jogo monta; e o
// GLTFLoader do vendor lendo um .glb do disco com o Draco sem Workers.
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import vm from 'node:vm';
import * as THREE from 'three';
import { bounds, compile } from '../src/clay/sdf/nodes.js';
import { polygonize } from '../src/clay/sdf/marchingCubes.js';
import { ModeloDobras, dadosDasPrimitivas } from '../src/characters/hands/modeloDobras.js';

export const RAIZ = join(dirname(fileURLToPath(import.meta.url)), '..');

/** O módulo do decodificador Draco do vendor (Emscripten, CommonJS) carregado no Node. */
export async function decodificadorDraco() {
  const arquivo = join(RAIZ, 'vendor', 'three', 'examples', 'jsm', 'libs', 'draco', 'gltf', 'draco_decoder.js');
  const modulo = { exports: {} };
  vm.runInThisContext(`(function (module, exports, require, __filename, __dirname) {${readFileSync(arquivo, 'utf8')}\n})`)(
    modulo, modulo.exports, createRequire(arquivo), arquivo, dirname(arquivo));
  return modulo.exports();
}

/** Os atributos pedidos ({nome glTF: valores}) e os índices dos triângulos de uma primitiva comprimida pelo Draco. */
export function primitivaDraco(draco, json, bin, primitiva, nomes) {
  const ext = primitiva.extensions.KHR_draco_mesh_compression;
  const vista = json.bufferViews[ext.bufferView];
  const bytes = new Int8Array(bin.buffer, bin.byteOffset + (vista.byteOffset ?? 0), vista.byteLength);
  const decodificador = new draco.Decoder();
  const buffer = new draco.DecoderBuffer();
  buffer.Init(bytes, bytes.length);
  const malha = new draco.Mesh();
  try {
    const estado = decodificador.DecodeBufferToMesh(buffer, malha);
    assert.ok(estado.ok(), `o Draco não decodificou: ${estado.error_msg()}`);
    const saida = {};
    for (const nome of nomes) {
      const atributo = decodificador.GetAttributeByUniqueId(malha, ext.attributes[nome]);
      const n = malha.num_points() * atributo.num_components();
      const arr = new draco.DracoFloat32Array();
      decodificador.GetAttributeFloatForAllPoints(malha, atributo, arr);
      const valores = new Float32Array(n);
      for (let i = 0; i < n; i++) valores[i] = arr.GetValue(i);
      draco.destroy(arr);
      saida[nome] = valores;
    }
    const indices = new Uint32Array(malha.num_faces() * 3);
    const face = new draco.DracoInt32Array();
    for (let f = 0; f < malha.num_faces(); f++) {
      decodificador.GetFaceFromMesh(malha, f, face);
      for (let k = 0; k < 3; k++) indices[f * 3 + k] = face.GetValue(k);
    }
    draco.destroy(face);
    saida.indices = indices;
    return saida;
  } finally {
    draco.destroy(malha);
    draco.destroy(buffer);
    draco.destroy(decodificador);
  }
}

/** Um acessor comum (não comprimido) como Float32Array. */
function acessor(json, bin, i) {
  const a = json.accessors[i];
  const vista = json.bufferViews[a.bufferView];
  const comp = { SCALAR: 1, VEC2: 2, VEC3: 3, VEC4: 4, MAT4: 16 }[a.type];
  assert.equal(a.componentType, 5126, 'o acessor não é float');
  return new Float32Array(bin.buffer.slice(bin.byteOffset + (vista.byteOffset ?? 0) + (a.byteOffset ?? 0),
    bin.byteOffset + (vista.byteOffset ?? 0) + (a.byteOffset ?? 0) + a.count * comp * 4));
}

/** A translação da inversa de uma matriz afim 4×4 (glTF, por colunas; a parte linear pode ter escala): −A⁻¹·t. */
function translacaoDaInversa(m) {
  const a = [[m[0], m[4], m[8]], [m[1], m[5], m[9]], [m[2], m[6], m[10]]];
  const t = [m[12], m[13], m[14]];
  const det = a[0][0] * (a[1][1] * a[2][2] - a[1][2] * a[2][1]) - a[0][1] * (a[1][0] * a[2][2] - a[1][2] * a[2][0])
    + a[0][2] * (a[1][0] * a[2][1] - a[1][1] * a[2][0]);
  const inv = [
    [(a[1][1] * a[2][2] - a[1][2] * a[2][1]) / det, (a[0][2] * a[2][1] - a[0][1] * a[2][2]) / det, (a[0][1] * a[1][2] - a[0][2] * a[1][1]) / det],
    [(a[1][2] * a[2][0] - a[1][0] * a[2][2]) / det, (a[0][0] * a[2][2] - a[0][2] * a[2][0]) / det, (a[0][2] * a[1][0] - a[0][0] * a[1][2]) / det],
    [(a[1][0] * a[2][1] - a[1][1] * a[2][0]) / det, (a[0][1] * a[2][0] - a[0][0] * a[2][1]) / det, (a[0][0] * a[1][1] - a[0][1] * a[1][0]) / det],
  ];
  return [0, 1, 2].map((r) => -(inv[r][0] * t[0] + inv[r][1] * t[1] + inv[r][2] * t[2]));
}

/** O modelo das dobras de um braço (`luva_d` ou `luva_e`) montado do luvas.glb, como o jogo faz. */
export function modeloDoGlb(draco, json, bin, nomeDaMalha) {
  const no = json.nodes.find((n) => n.name === nomeDaMalha);
  const lado = nomeDaMalha.slice(-1);
  const materiais = json.materials ?? [];
  const primitivas = json.meshes[no.mesh].primitives.map((p) => {
    const d = primitivaDraco(draco, json, bin, p, ['POSITION', 'JOINTS_0', 'WEIGHTS_0', '_VERTICE']);
    return { posicoes: d.POSITION, juntas: d.JOINTS_0, pesos: d.WEIGHTS_0, vertice: d._VERTICE, indices: d.indices, zona: materiais[p.material]?.name };
  });
  const malha = dadosDasPrimitivas(primitivas);
  const skin = json.skins[no.skin];
  const ossos = skin.joints.map((j) => json.nodes[j].name);
  const pais = skin.joints.map((j) => skin.joints.findIndex((k) => (json.nodes[k].children ?? []).includes(j)));
  const ibm = acessor(json, bin, skin.inverseBindMatrices);
  const cabecas = [];
  // as cabeças de repouso no referencial da malha (u; a inversa da matriz de ligação inversa), em mm
  for (let i = 0; i < ossos.length; i++) cabecas.push(...translacaoDaInversa(ibm.subarray(i * 16, i * 16 + 16)).map((v) => v * 25.4));
  const parametros = typeof no.extras.correcoes === 'string' ? JSON.parse(no.extras.correcoes) : no.extras.correcoes;
  return new ModeloDobras({ malha, ossos, pais, cabecas, parametros, lado });
}

/**
 * O DRACOLoader do three sem Workers (o Node não tem Worker de navegador): a mesma decodificação do worker dele
 * (atributos pelo id único, com o tipo que o GLTFLoader pede, e os índices), síncrona, para o GLTFLoader do vendor ler
 * o .glb de verdade nos testes.
 */
export function dracoSincrono(draco) {
  const tipos = {
    Float32Array: draco.DT_FLOAT32, Int8Array: draco.DT_INT8, Int16Array: draco.DT_INT16, Int32Array: draco.DT_INT32,
    Uint8Array: draco.DT_UINT8, Uint16Array: draco.DT_UINT16, Uint32Array: draco.DT_UINT32,
  };
  return {
    decodeDracoFile(buffer, callback, attributeIDs, attributeTypes, _cor, onError = () => {}) {
      const decodificador = new draco.Decoder();
      const malha = new draco.Mesh();
      try {
        const bytes = new Int8Array(buffer);
        const estado = decodificador.DecodeArrayToMesh(bytes, bytes.byteLength, malha);
        if (!estado.ok() || malha.ptr === 0) throw new Error(`Draco: ${estado.error_msg()}`);
        const g = new THREE.BufferGeometry();
        for (const [nome, id] of Object.entries(attributeIDs)) {
          const Tipo = globalThis[attributeTypes[nome]];
          const atributo = decodificador.GetAttributeByUniqueId(malha, id);
          const n = malha.num_points() * atributo.num_components();
          const ptr = draco._malloc(n * Tipo.BYTES_PER_ELEMENT);
          decodificador.GetAttributeDataArrayForAllPoints(malha, atributo, tipos[attributeTypes[nome]], n * Tipo.BYTES_PER_ELEMENT, ptr);
          const valores = new Tipo(draco.HEAPF32.buffer, ptr, n).slice();
          draco._free(ptr);
          g.setAttribute(nome, new THREE.BufferAttribute(valores, atributo.num_components()));
        }
        const ni = malha.num_faces() * 3;
        const ptr = draco._malloc(ni * 4);
        decodificador.GetTrianglesUInt32Array(malha, ni * 4, ptr);
        g.setIndex(new THREE.BufferAttribute(new Uint32Array(draco.HEAPF32.buffer, ptr, ni).slice(), 1));
        draco._free(ptr);
        callback(g);
      } catch (e) {
        onError(e);
      } finally {
        draco.destroy(malha);
        draco.destroy(decodificador);
      }
      return Promise.resolve();
    },
    preload() {
      return this;
    },
    dispose() {},
  };
}

/** Um .glb do disco pelo GLTFLoader do vendor (o mesmo código do jogo), com o Draco síncrono. */
export async function carregarGlbNoNode(arquivo, draco) {
  const { GLTFLoader } = await import('three/addons/loaders/GLTFLoader.js');
  const loader = new GLTFLoader().setDRACOLoader(dracoSincrono(draco));
  const b = readFileSync(arquivo);
  return loader.parseAsync(b.buffer.slice(b.byteOffset, b.byteOffset + b.byteLength), '');
}

/** O arquivo do disco de uma URL file:// (sem a busca `?v=`), no Windows sem a barra antes da letra do disco. */
export function arquivoDaUrl(url) {
  return decodeURIComponent(new URL(url).pathname).replace(/^\/([A-Za-z]:)/, '$1').split('?')[0];
}

/**
 * Os carregadores da biblioteca de armas e da LuvasSource lendo do disco, no Node: o .glb pelo GLTFLoader do vendor (o
 * Draco síncrono), as texturas vazias (sem GPU) e o JSON do arquivo.
 */
export function carregadoresDoDisco(draco) {
  return {
    glb: async (url) => carregarGlbNoNode(arquivoDaUrl(url), draco),
    textura: async () => new THREE.Texture(),
    json: async (url) => JSON.parse(readFileSync(arquivoDaUrl(url), 'utf8')),
  };
}

/** SdfMesher de teste: a mesma árvore pelo marching cubes, numa grade grossa, e o registro dos pedidos. */
export function sdfDeTeste(resolucao = 48) {
  const pedidos = [];
  return {
    pedidos,
    async build(tree, opts) {
      pedidos.push({ tree, opts });
      const m = polygonize(compile(tree), bounds(tree), { resolution: Math.min(resolucao, opts.resolution), maxCells: 600000 });
      const g = new THREE.BufferGeometry();
      g.setAttribute('position', new THREE.BufferAttribute(Float32Array.from(m.positions), 3));
      g.setAttribute('normal', new THREE.BufferAttribute(Float32Array.from(m.normals), 3));
      g.setIndex(new THREE.BufferAttribute(Uint32Array.from(m.indices), 1));
      return g;
    },
  };
}
