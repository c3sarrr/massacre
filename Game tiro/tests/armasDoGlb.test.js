// As armas da 4.1c no jogo pelo .glb (plano da 4.1c, Tarefa 12, Passo 1), sem GPU: o serviço `weaponModels` (a
// WeaponLibrary com os carregadores do disco) serve a Glock-18, a M4A4 e a baioneta M9 pelo .glb do Blender, com a pega
// das luvas (`info(id).pega`): as mãos da categoria (as duas na pistola e no fuzil, só a direita na faca), a marca do rig
// igual à do luvas.glb, os dedos e a palma afundada de cada mão; a receita de massinha delas saiu do registro e as mãos
// que o viewmodel usa (`handSides`) são as da pega.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import { ARMAS } from '../src/data/armas/index.js';
import { ARMAS_REAIS, armaComPega } from '../src/data/armasReais.js';
import { LUVAS, MAOS_DA_CATEGORIA, OSSOS_DE_DEDO } from '../src/data/luvas.js';
import { WeaponLibrary } from '../src/weapons/model/weaponLibrary.js';
import { handSides, viewCategory } from '../src/weapons/viewmodel/placement.js';
import { RAIZ, carregadoresDoDisco, decodificadorDraco } from './luvasTestUtils.js';

const DA_41C = ['glock', 'm4a4', 'knife'];
const LADO = { d: 'direita', e: 'esquerda' };

test('a Glock, a M4A4 e a faca saíram das receitas de massinha e estão nas realistas, com a pega', () => {
  for (const id of DA_41C) {
    assert.equal(ARMAS[id], undefined, `${id}: a receita de massinha saiu`);
    assert.ok(ARMAS_REAIS[id], `${id}: realista`);
    assert.equal(armaComPega(id), true, `${id}: com a pega das luvas`);
  }
});

test('weaponModels serve a Glock, a M4A4 e a faca pelo .glb, com a pega das luvas no info', async () => {
  const lib = new WeaponLibrary({ sdf: null, carregadores: carregadoresDoDisco(await decodificadorDraco()) });
  const marcaLuvas = JSON.parse(readFileSync(join(RAIZ, `${LUVAS.pasta}luvas.relatorio.json`), 'utf8')).marca;
  try {
    for (const id of DA_41C) {
      assert.equal(lib.has(id), true, id);
      assert.equal(lib.source(id), 'glb', `${id}: origem`);
      const info = await lib.describe(id);
      assert.equal(info, lib.info(id), `${id}: o info guardado`);
      assert.equal(info.hands, true, `${id}: com as mãos`);
      const lados = MAOS_DA_CATEGORIA[viewCategory(id)];
      assert.deepEqual(info.pega.lados, lados, `${id}: as mãos da categoria`);
      assert.deepEqual(handSides(info), lados.map((l) => LADO[l]), `${id}: as mãos do viewmodel`);
      for (const l of lados) {
        assert.equal(info.pega.marca[l], marcaLuvas[l], `${id}: a marca do rig ${l} é a das luvas`);
        assert.deepEqual(Object.keys(info.pega.dedos[l]).sort(), [...OSSOS_DE_DEDO].sort(), `${id}: os dedos ${l}`);
        assert.ok(info.pega.maos[l].posicao.isVector3 && info.pega.maos[l].quaternion.isQuaternion, `${id}: o pulso ${l}`);
        // o afundamento da palma de cada mão (a palma que cede): só a pistola chega afundando (`aperto`), as outras
        // podem não ter vértice nenhum que cede
        const palma = info.pega.palma[l];
        assert.equal(palma.vertices.length, palma.vetores.length, `${id}: a palma ${l}`);
        if (viewCategory(id) === 'pistola') assert.ok(palma.vertices.length > 0, `${id}: a palma ${l} afundada`);
      }
      for (const l of ['d', 'e'].filter((x) => !lados.includes(x))) assert.equal(info.pega.maos[l], undefined, `${id}: sem a mão ${l}`);
      const inst = await lib.instance(id, { lod: 'perto' });
      assert.equal(inst.userData.weapon.id, id);
    }
  } finally {
    lib.dispose();
  }
});
