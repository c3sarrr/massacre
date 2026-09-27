// A saída de verdade das luvas (Fase 4.1b; plano, Tarefa 6, Passo 7), depois de `npm run blender -- construir luvas`:
// o validador da saída sem problemas (os 20 ossos de cada braço com os nomes da D2, as três zonas nas duas malhas, os
// triângulos dos dois braços ≤ 14 000, as duas texturas de 2048 sem perdas, os arquivos ≤ 6 MB, a marca do rig igual no
// relatório e no .glb) e o `_VERTICE` decodificado do Draco (o decodificador do vendor, em JS): em cada braço, depois de
// arredondado, um índice inteiro de vértice do Blender por vértice do glTF, cobrindo todos os vértices da luva — o que o
// jogo usa para casar o modelo das dobras e as amarras das peças com a malha do glTF.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import vm from 'node:vm';
import { LUVAS } from '../src/data/luvas.js';
import { lerGlb } from '../tools/blender/saida.mjs';
import { validarSaidaLuvas } from '../tools/blender/saidaLuvas.mjs';

const RAIZ = join(dirname(fileURLToPath(import.meta.url)), '..');
const PASTA = join(RAIZ, LUVAS.pasta);

/** O módulo do decodificador Draco do vendor (Emscripten, CommonJS) carregado no Node. */
async function decodificadorDraco() {
  const arquivo = join(RAIZ, 'vendor', 'three', 'examples', 'jsm', 'libs', 'draco', 'gltf', 'draco_decoder.js');
  const modulo = { exports: {} };
  vm.runInThisContext(`(function (module, exports, require, __filename, __dirname) {${readFileSync(arquivo, 'utf8')}\n})`)(
    modulo, modulo.exports, createRequire(arquivo), arquivo, dirname(arquivo));
  return modulo.exports();
}

/** Os valores de um atributo (pelo id único da extensão Draco) de uma primitiva comprimida. */
function atributoDraco(draco, json, bin, primitiva, nome) {
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
    const atributo = decodificador.GetAttributeByUniqueId(malha, ext.attributes[nome]);
    const n = malha.num_points() * atributo.num_components();
    const arr = new draco.DracoFloat32Array();
    decodificador.GetAttributeFloatForAllPoints(malha, atributo, arr);
    const valores = new Float32Array(n);
    for (let i = 0; i < n; i++) valores[i] = arr.GetValue(i);
    draco.destroy(arr);
    return valores;
  } finally {
    draco.destroy(malha);
    draco.destroy(buffer);
    draco.destroy(decodificador);
  }
}

test('luvas.glb de verdade: o validador da saída sem problemas', () => {
  const { problemas, resumo, relatorio, bytes } = validarSaidaLuvas(RAIZ);
  assert.deepEqual(problemas, []);
  assert.equal(resumo.malhas.luva_d.ossos.length, 20);
  assert.equal(resumo.malhas.luva_e.ossos.length, 20);
  assert.ok(resumo.malhas.luva_d.triangulos + resumo.malhas.luva_e.triangulos <= LUVAS.orcamento.triangulos);
  assert.ok(bytes <= LUVAS.orcamento.arquivosMB * 1024 * 1024);
  assert.equal(relatorio.aprovado, true);
  assert.equal(relatorio.uv.sobreposicao, 0);
});

test('luvas.glb de verdade: o _VERTICE do Draco cobre os vértices do Blender, um inteiro por vértice do glTF', async () => {
  const { json, bin } = lerGlb(readFileSync(join(PASTA, 'luvas.glb')));
  const relatorio = JSON.parse(readFileSync(join(PASTA, 'luvas.relatorio.json'), 'utf8'));
  const draco = await decodificadorDraco();
  for (const nome of ['luva_d', 'luva_e']) {
    const no = json.nodes.find((n) => n.name === nome);
    const vistos = new Set();
    let pior = 0;
    for (const p of json.meshes[no.mesh].primitives) {
      for (const v of atributoDraco(draco, json, bin, p, '_VERTICE')) {
        const i = Math.round(v);
        pior = Math.max(pior, Math.abs(v - i));
        vistos.add(i);
      }
    }
    assert.ok(pior < 0.1, `${nome}: o _VERTICE a ${pior} de um inteiro (a quantização do Draco)`);
    assert.equal(vistos.size, relatorio.vertices, `${nome}: ${vistos.size} índices, ${relatorio.vertices} vértices no Blender`);
    assert.equal(Math.min(...vistos), 0);
    assert.equal(Math.max(...vistos), relatorio.vertices - 1);
  }
});
