// Testes da prévia do jogo para o Blender (Fase 4.1; docs/phases/phase-4.md, seção 4.1, "Blender"): o formato que o
// tools/blender/massacre/previa.py lê — blocos alinhados a 4 bytes dentro do binário, contagens coerentes (3 números por
// vértice, 3 índices por triângulo, uma massa por triângulo), índices dentro dos vértices, massas dentro da lista —, um
// grupo por grupo da receita no pivô dele, um braço por âncora de mão com o pulso na âncora e a câmera do viewmodel
// olhando para a arma. Sem o Blender (o caminho dentro dele é o `npm run blender -- ida-volta|conferir`).
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, readFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import * as THREE from 'three';
import { ARMAS } from '../src/data/armas/index.js';
import { VIEWMODEL } from '../src/data/viewmodel.js';
import { HAND_ANCHOR, handSides, viewmodelVerticalFov } from '../src/weapons/viewmodel/placement.js';
import { gerarPrevia } from '../tools/blender/previa.mjs';

function malha(bin, m, comMassas, nMateriais) {
  const bloco = (b, Type) => {
    assert.equal(b.offset % 4, 0, 'bloco alinhado a 4 bytes');
    assert.ok(b.offset + b.count * Type.BYTES_PER_ELEMENT <= bin.byteLength, 'bloco dentro do binário');
    return new Type(bin, b.offset, b.count);
  };
  const pos = bloco(m.positions, Float32Array);
  const nor = bloco(m.normals, Float32Array);
  const idx = bloco(m.indices, Uint32Array);
  assert.equal(pos.length % 3, 0);
  assert.equal(nor.length, pos.length);
  assert.equal(idx.length % 3, 0);
  assert.ok(idx.length > 0);
  const nv = pos.length / 3;
  assert.ok(idx.every((i) => i < nv), 'índices dentro dos vértices');
  assert.ok(pos.every(Number.isFinite), 'posições finitas');
  for (let i = 0; i < nv; i += 97) {
    const l = Math.hypot(nor[i * 3], nor[i * 3 + 1], nor[i * 3 + 2]);
    assert.ok(Math.abs(l - 1) < 0.02, `normal unitária (${l})`);
  }
  if (comMassas) {
    const massas = bloco(m.massas, Uint8Array);
    assert.equal(massas.length, idx.length / 3, 'uma massa por triângulo');
    assert.ok(massas.every((k) => k < nMateriais), 'massas dentro da lista');
  }
  return { pos, nv };
}

for (const id of ['knife', 'glock']) {
  test(`prévia do jogo (${id}): blocos, contagens, grupos, braços nas âncoras e a câmera do viewmodel`, async () => {
    const recipe = ARMAS[id];
    const dir = mkdtempSync(join(tmpdir(), 'massacre-previa-'));
    try {
      const { json, triangulos } = await gerarPrevia(recipe, join(dir, id));
      const cab = JSON.parse(readFileSync(json, 'utf8'));
      const arquivo = readFileSync(join(dir, cab.bin));
      const bin = arquivo.buffer.slice(arquivo.byteOffset, arquivo.byteOffset + arquivo.byteLength);
      assert.equal(cab.id, id);
      assert.equal(cab.versao, 1);
      assert.ok(cab.materiais.length > 0);
      assert.deepEqual(cab.grupos.map((g) => g.nome), Object.keys(recipe.groups));
      let soma = 0;
      for (const g of cab.grupos) {
        assert.deepEqual(g.pivo, recipe.groups[g.nome].pivot ?? [0, 0, 0]);
        malha(bin, g, true, cab.materiais.length);
        soma += g.indices.count / 3;
      }
      // Um braço por âncora de mão, na pose dela, com o pulso na âncora (algum vértice a menos de um raio de dedo).
      assert.deepEqual(cab.maos.map((m) => m.lado), handSides(recipe));
      for (const m of cab.maos) {
        const anchor = recipe.anchors[HAND_ANCHOR[m.lado]];
        assert.equal(m.pose, anchor.pose);
        const { pos, nv } = malha(bin, m, false, 1);
        let perto = Infinity;
        for (let i = 0; i < nv; i++) {
          perto = Math.min(perto, Math.hypot(pos[i * 3] - anchor.pos[0], pos[i * 3 + 1] - anchor.pos[1], pos[i * 3 + 2] - anchor.pos[2]));
        }
        assert.ok(perto < 1.5, `a massa do braço passa pelo pulso (${perto.toFixed(2)} u)`);
        soma += m.indices.count / 3;
      }
      assert.equal(soma, triangulos);
      // A câmera do viewmodel: o FOV vertical do viewmodel_fov padrão e a arma na frente dela (−Z), perto.
      const c = cab.camera;
      assert.ok(Math.abs(c.fovY - viewmodelVerticalFov(VIEWMODEL.fov.default)) < 1e-9);
      assert.equal(c.near, VIEWMODEL.near);
      const q = new THREE.Quaternion(...c.quat);
      assert.ok(Math.abs(q.length() - 1) < 1e-6);
      const origem = new THREE.Vector3().sub(new THREE.Vector3(...c.pos)).applyQuaternion(q.clone().invert());
      assert.ok(origem.z < -5 && origem.z > -30, `a arma na frente da câmera (${origem.z.toFixed(2)} u)`);
    } finally {
      rmSync(dir, { recursive: true, force: true });
    }
  });
}
