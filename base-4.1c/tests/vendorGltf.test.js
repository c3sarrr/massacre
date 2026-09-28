// O vendor tem o GLTFLoader e o DRACOLoader do three fixado, o que eles importam e o decodificador Draco (Fase 4.1a;
// desenho, seções 4.5 e 5.2) — de loaders/, fora os dois, só o que outro arquivo do vendor importa; o servidor de
// desenvolvimento serve .glb, .gltf, .bin e .webp com o tipo certo.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { existsSync, readFileSync, readdirSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const JSM = new URL('../vendor/three/examples/jsm/', import.meta.url);
const IMPORT = /from\s*['"](\.{1,2}\/[^'"]+)['"]/g;

const CARREGADORES = ['GLTFLoader.js', 'DRACOLoader.js'];
const DECODIFICADOR = ['draco_decoder.js', 'draco_decoder.wasm', 'draco_wasm_wrapper.js'];

test('vendor: GLTFLoader, DRACOLoader e o decodificador iguais aos do node_modules; o resto de loaders/ só por import', () => {
  for (const nome of CARREGADORES) {
    const arquivo = new URL(`loaders/${nome}`, JSM);
    assert.ok(existsSync(arquivo), `vendor/three/examples/jsm/loaders/${nome}`);
    const texto = readFileSync(arquivo, 'utf8');
    assert.equal(texto, readFileSync(new URL(`../node_modules/three/examples/jsm/loaders/${nome}`, import.meta.url), 'utf8'));
    for (const m of texto.matchAll(IMPORT)) assert.ok(existsSync(new URL(m[1], arquivo)), `${nome}: import ${m[1]}`);
  }
  for (const nome of DECODIFICADOR) {
    const arquivo = new URL(`libs/draco/gltf/${nome}`, JSM);
    assert.ok(existsSync(arquivo), `vendor/three/examples/jsm/libs/draco/gltf/${nome}`);
    assert.ok(readFileSync(arquivo).equals(readFileSync(new URL(`../node_modules/three/examples/jsm/libs/draco/gltf/${nome}`, import.meta.url))), nome);
  }
  // O fechamento de imports do vendor.mjs já trazia o FontLoader (TextGeometry) e o MD2Loader (MD2Character): fora os
  // dois de propósito, todo arquivo de loaders/ tem quem o importe — nenhum carregador solto.
  const pasta = fileURLToPath(JSM);
  const importados = new Set();
  for (const f of readdirSync(pasta, { recursive: true }).filter((x) => x.endsWith('.js'))) {
    const caminho = join(pasta, f);
    for (const m of readFileSync(caminho, 'utf8').matchAll(IMPORT)) importados.add(resolve(dirname(caminho), m[1]));
  }
  for (const nome of readdirSync(new URL('loaders/', JSM))) {
    if (!CARREGADORES.includes(nome)) assert.ok(importados.has(join(pasta, 'loaders', nome)), `loaders/${nome} sem quem o importe`);
  }
});

test('servidor de desenvolvimento: .glb, .gltf, .bin e .webp com o tipo MIME', () => {
  const texto = readFileSync(new URL('../tools/dev-server.mjs', import.meta.url), 'utf8');
  assert.match(texto, /'\.glb': 'model\/gltf-binary'/);
  assert.match(texto, /'\.gltf': 'model\/gltf\+json'/);
  assert.match(texto, /'\.bin': 'application\/octet-stream'/);
  assert.match(texto, /'\.webp': 'image\/webp'/);
});
