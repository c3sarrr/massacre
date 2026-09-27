// O viewmodel com as luvas (Fase 4.1b; plano, Tarefa 10), sem GPU: a AK de verdade (o .glb pela biblioteca de armas,
// com o GLTFLoader do vendor e o Draco sem Workers) e as luvas de verdade (LuvasSource), a Glock de massinha falsa.
// `handSides` dá os dois lados para a AK com pega e nenhum para a realista sem pega; `info.pega` vem do .glb; o
// viewmodel segura a AK com as luvas e a Glock com os braços de massinha; a facção vem do time (`cl_bracadeira`) e,
// sem time, da do boneco; a braçadeira só com time; a facção troca os materiais sem recriar a malha; `status()` diz
// os braços; a esfera da sombra própria cobre as duas mãos de luva; e os cotovelos do `rifle` deixam o pulso dos dois
// lados dentro dos limites da AAOS nas três posições prontas do CS.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import * as THREE from 'three';
import { Config } from '../src/core/config.js';
import { EventBus } from '../src/core/events.js';
import { ARMAS } from '../src/data/armas/index.js';
import { CONFIG_SCHEMA } from '../src/data/configSchema.js';
import { LUVAS } from '../src/data/luvas.js';
import { VIEWMODEL } from '../src/data/viewmodel.js';
import { LuvasSource } from '../src/characters/hands/luvasSource.js';
import { WeaponLibrary } from '../src/weapons/model/weaponLibrary.js';
import {
  applyViewmodelPreset, categoryPlacement, gloveFaction, gloveTarget, handSides, viewmodelVerticalFov,
} from '../src/weapons/viewmodel/placement.js';
import { Viewmodel } from '../src/weapons/viewmodel/viewmodel.js';
import { RAIZ, carregarGlbNoNode, decodificadorDraco, sdfDeTeste } from './luvasTestUtils.js';

const MM = 25.4;
let draco = null;

const json = (arquivo) => JSON.parse(readFileSync(join(RAIZ, arquivo), 'utf8'));

function carregadores() {
  return {
    async glb(url) {
      const caminho = decodeURIComponent(new URL(url).pathname).replace(/^\/([A-Za-z]:)/, '$1');
      return carregarGlbNoNode(caminho.split('?')[0], draco);
    },
    async textura() {
      return new THREE.Texture();
    },
    async json(url) {
      const caminho = decodeURIComponent(new URL(url).pathname).replace(/^\/([A-Za-z]:)/, '$1').split('?')[0];
      return JSON.parse(readFileSync(caminho, 'utf8'));
    },
  };
}

/** As armas: a AK pela biblioteca de verdade (origem glb); a Glock de massinha falsa (a receita, uma caixa). */
function armas() {
  const lib = new WeaponLibrary({ sdf: null, carregadores: carregadores() });
  const glockInfo = { id: 'glock', source: 'massinha', category: 'pistola', hands: true, anchors: ARMAS.glock.anchors, radius: 5 };
  return {
    lib,
    has: (id) => id === 'ak47' || id === 'glock',
    source: (id) => (id === 'ak47' ? 'glb' : 'massinha'),
    describe: (id) => (id === 'ak47' ? lib.describe(id) : Promise.resolve(glockInfo)),
    info: (id) => (id === 'ak47' ? lib.info(id) : glockInfo),
    instance: async (id, o) => {
      if (id === 'ak47') return lib.instance(id, o);
      const g = new THREE.Mesh(new THREE.BoxGeometry(6, 3, 1), new THREE.MeshBasicMaterial());
      g.userData.weapon = { id: 'glock', radius: 5 };
      return g;
    },
  };
}

function maosDeMassinha() {
  const criadas = [];
  return {
    criadas,
    async createArm(side) {
      const mesh = new THREE.Object3D();
      mesh.name = `braco-${side}`;
      const arm = { side, mesh, poses: [], faixa: undefined, setPose(p) { this.poses.push(p); }, setArmband(c) { this.faixa = c; }, place() {}, dispose() {} };
      criadas.push(arm);
      return arm;
    },
  };
}

async function montar() {
  draco ??= await decodificadorDraco();
  const events = new EventBus();
  const config = new Config(CONFIG_SCHEMA, { events });
  const render = {
    renderer: { compileAsync: async () => {}, shadowMap: { enabled: false, needsUpdate: false } },
    pipeline: { addLayer: () => () => {} }, shadowLevel: 0,
  };
  const luvas = new LuvasSource({ carregadores: carregadores(), sdf: sdfDeTeste(24) });
  const weapons = armas();
  const vm = new Viewmodel({ render, weapons, hands: maosDeMassinha(), luvas, config, events });
  const camera = new THREE.PerspectiveCamera(74, 16 / 9, 0.5, 400);
  return { vm, config, luvas, weapons, camera };
}

/** Quadros até o item pedido estar na mão (as cargas são promessas). */
async function segurar(vm, camera, item) {
  for (let i = 0; i < 400; i++) {
    vm.frame(camera, 1 / 60, { item, visible: true });
    if (vm.status().item === item && vm.layer.visible) return;
    await new Promise((r) => setTimeout(r, 5));
  }
  throw new Error(`o viewmodel não segurou ${item}`);
}

test('placement: o alvo do osso mao pela pega e a facção das luvas pelo time', () => {
  const pl = { position: new THREE.Vector3(1, -2, -9), quaternion: new THREE.Quaternion().setFromEuler(new THREE.Euler(0.1, 1.5, -0.05)) };
  const mao = { posicao: new THREE.Vector3(-4, -3, 2), quaternion: new THREE.Quaternion().setFromEuler(new THREE.Euler(-1, 0.4, 2)) };
  const a = gloveTarget(pl, mao);
  const m = new THREE.Matrix4().compose(pl.position, pl.quaternion, new THREE.Vector3(1, 1, 1));
  assert.ok(a.position.distanceTo(mao.posicao.clone().applyMatrix4(m)) < 1e-12);
  assert.ok(1 - Math.abs(a.quaternion.dot(pl.quaternion.clone().multiply(mao.quaternion))) < 1e-12);
  assert.equal(gloveFaction('tr'), 'massaCrua');
  assert.equal(gloveFaction('ct'), 'tropa');
  assert.equal(gloveFaction(null), 'massaCrua', 'sem time, a do boneco de referência');
  assert.equal(gloveFaction(null, 'tropa'), 'tropa');
});

test('viewmodel: a AK com pega nos dois lados, a info.pega do .glb; a realista sem pega sem mãos', async () => {
  const { weapons } = await montar();
  const info = await weapons.describe('ak47');
  assert.equal(info.hands, true);
  assert.deepEqual(handSides(info), ['direita', 'esquerda']);
  const rel = json('assets/armas/ak47/ak47.relatorio.json');
  assert.equal(info.pega.marca.d, json(`${LUVAS.pasta}luvas.relatorio.json`).marca.d, 'a marca do rig da AK é a das luvas');
  assert.ok(info.pega.dedos.d.indicador_1 && info.pega.dedos.e.minimo_3);
  assert.ok(info.pega.maos.d.posicao.isVector3 && info.pega.maos.e.quaternion.isQuaternion);
  assert.ok(rel.empunhadura?.d, 'o relatório com a empunhadura');
  assert.deepEqual(handSides({ ...info, hands: false, pega: null }), []);
});

test('viewmodel: luvas na AK, massinha na Glock, e o status diz os braços', async () => {
  const { vm, camera } = await montar();
  await segurar(vm, camera, 'ak47');
  let s = vm.status();
  assert.equal(s.bracos, 'luvas');
  assert.deepEqual(s.arms, ['direita', 'esquerda']);
  assert.equal(s.faccao, 'massaCrua');
  assert.ok(vm.gloves.bracos.direita.grupo.parent === vm.root, 'os braços de luva no referencial da câmera');
  await segurar(vm, camera, 'glock');
  s = vm.status();
  assert.equal(s.bracos, 'massinha');
  assert.deepEqual(vm.gloves.visiveis(), [], 'as luvas somem com a Glock');
  vm.frame(camera, 1 / 60, { item: 'glock', visible: true });
  assert.deepEqual(vm.status().arms, ['direita', 'esquerda']);
  await segurar(vm, camera, 'ak47');
  assert.equal(vm.status().bracos, 'luvas');
  vm.dispose();
});

test('viewmodel: a facção das luvas pelo time (e a do boneco sem time), a braçadeira só com time, as malhas ficam', async () => {
  const { vm, camera, config } = await montar();
  await segurar(vm, camera, 'ak47');
  const d = vm.gloves.bracos.direita;
  const malhas = d.malhas.slice();
  const nomes = () => d.malhas.map((m) => m.material.name).sort();
  assert.deepEqual(nomes(), ['luvas:massaCrua:couro', 'luvas:massaCrua:reforco', 'luvas:massaCrua:tecido']);
  assert.equal(d.bracadeira.visible, false, 'sem time, sem braçadeira');
  config.set('debug.armband', 'ct');
  await vm.gloves.setFaccao(vm.gloves.faccao); // espera os materiais da facção nova
  assert.equal(vm.status().faccao, 'tropa');
  assert.deepEqual(nomes(), ['luvas:tropa:couro', 'luvas:tropa:reforco', 'luvas:tropa:tecido']);
  assert.deepEqual(d.malhas, malhas, 'as malhas são as mesmas');
  assert.equal(d.bracadeira.visible, true);
  config.set('debug.armband', 'tr');
  await vm.gloves.setFaccao(vm.gloves.faccao);
  assert.equal(vm.status().faccao, 'massaCrua');
  assert.equal(vm.gloves.bracos.esquerda.bracadeira.visible, true);
  config.set('debug.armband', 'off');
  await vm.gloves.setFaccao(vm.gloves.faccao);
  assert.equal(vm.status().faccao, 'massaCrua');
  assert.equal(d.bracadeira.visible, false);
  vm.dispose();
});

test('viewmodel: a esfera da sombra própria cobre as duas mãos de luva inteiras', async () => {
  const { vm, camera } = await montar();
  await segurar(vm, camera, 'ak47');
  vm.frame(camera, 1 / 60, { item: 'ak47', visible: true });
  for (const lado of ['direita', 'esquerda']) {
    const b = vm.gloves.bracos[lado];
    b.grupo.updateMatrix();
    const pts = b.posicoesMM;
    let fora = 0;
    for (let v = 0; v < pts.length / 3; v++) {
      if (pts[v * 3] < -45) continue; // o antebraço e o punho saem da tela: a esfera é das mãos
      const p = new THREE.Vector3(pts[v * 3] / MM, pts[v * 3 + 1] / MM, pts[v * 3 + 2] / MM).applyMatrix4(b.grupo.matrix);
      if (!vm.localSphere.containsPoint(p)) fora++;
    }
    assert.equal(fora, 0, `${lado}: ${fora} vértices da mão fora da esfera da sombra própria`);
  }
  vm.dispose();
});

test('viewmodel: os cotovelos do rifle deixam os dois pulsos nos limites da AAOS nas três posições prontas do CS', async () => {
  const { vm, camera, config } = await montar();
  await segurar(vm, camera, 'ak47');
  for (const id of Object.keys(VIEWMODEL.presets)) {
    applyViewmodelPreset(config, id);
    vm.frame(camera, 1 / 60, { item: 'ak47', visible: true });
    const { avisos } = vm.status();
    assert.deepEqual(avisos, { direita: [], esquerda: [] }, `posição ${id}: ${JSON.stringify(avisos)}`);
    // o cotovelo de verdade (o osso antebraco) fora da tela em 16:9 e 21:9 e abaixo do pulso
    const fovV = viewmodelVerticalFov(VIEWMODEL.presets[id].fov);
    const t = Math.tan((fovV * Math.PI) / 360);
    for (const lado of ['direita', 'esquerda']) {
      const b = vm.gloves.bracos[lado];
      b.grupo.updateMatrixWorld(true);
      const inv = vm.root.matrixWorld.clone().invert();
      const cotovelo = b.ossos.antebraco.getWorldPosition(new THREE.Vector3()).applyMatrix4(inv);
      const pulso = b.ossos.mao.getWorldPosition(new THREE.Vector3()).applyMatrix4(inv);
      assert.ok(cotovelo.y < pulso.y, `posição ${id}, ${lado}: o cotovelo acima do pulso`);
      for (const aspect of [16 / 9, 21 / 9]) {
        const naTela = cotovelo.z < -VIEWMODEL.near && Math.abs(cotovelo.x / (-cotovelo.z * t * aspect)) < 1 && Math.abs(cotovelo.y / (-cotovelo.z * t)) < 1;
        assert.ok(!naTela, `posição ${id}, ${lado}: o cotovelo aparece em ${aspect.toFixed(2)}`);
      }
    }
  }
  // as categorias sem cotovelos de luva usam os de massinha
  assert.deepEqual(categoryPlacement('pistola').gloveElbows, categoryPlacement('pistola').elbows);
  assert.deepEqual(categoryPlacement('rifle').gloveElbows, { direita: [13.1, -8.2, 13.9], esquerda: [-3.9, -24.4, -15.7] });
  vm.dispose();
});

test('viewmodel: a facção das luvas forçada pela bancada vale sobre a do time e sai quando solta', async () => {
  const { vm, camera, config } = await montar();
  await segurar(vm, camera, 'ak47');
  config.set('debug.armband', 'tr');
  vm.frame(camera, 1 / 60, { item: 'ak47', visible: true, gloves: 'tropa' });
  await vm.gloves.setFaccao(vm.gloves.faccao);
  assert.equal(vm.status().faccao, 'tropa', 'a bancada escolheu a Tropa com o time TR');
  assert.ok(vm.gloves.bracos.direita.malhas.every((m) => m.material.name.startsWith('luvas:tropa:')));
  vm.frame(camera, 1 / 60, { item: 'ak47', visible: true, gloves: null });
  await vm.gloves.setFaccao(vm.gloves.faccao);
  assert.equal(vm.status().faccao, 'massaCrua', 'solta: a do time');
  vm.dispose();
});
