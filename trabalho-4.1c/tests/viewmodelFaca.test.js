// A faca no viewmodel com a luva (Fase 4.1c; plano, P1.4 e Tarefa 9), sem GPU: a M9 de verdade (o .glb com a pega de
// martelo, pela biblioteca de armas) e as luvas de verdade, como o viewmodelLuvas. Só o braço direito aparece; a pose da
// categoria `faca` é a da M9 do CS2 parada (a miniatura de vitrine do plano, P1.4) — a lâmina subindo para o centro da
// tela com a face para a câmera, os dentes do dorso embaixo e o gume em cima, a luva embaixo à direita; a nossa saía
// com os dentes para cima, o "de ponta-cabeça" do usuário na P1 —, e o cotovelo de luva da categoria deixa o pulso nos
// limites da AAOS, com folga, nas três posições prontas do CS, com o cotovelo fora da tela e abaixo do pulso.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import * as THREE from 'three';
import { Config } from '../src/core/config.js';
import { EventBus } from '../src/core/events.js';
import { CONFIG_SCHEMA } from '../src/data/configSchema.js';
import { VIEWMODEL } from '../src/data/viewmodel.js';
import { LuvasSource } from '../src/characters/hands/luvasSource.js';
import { WeaponLibrary } from '../src/weapons/model/weaponLibrary.js';
import { applyViewmodelPreset, handSides, viewmodelVerticalFov } from '../src/weapons/viewmodel/placement.js';
import { Viewmodel } from '../src/weapons/viewmodel/viewmodel.js';
import { carregarGlbNoNode, decodificadorDraco, sdfDeTeste } from './luvasTestUtils.js';

let draco = null;
const caminho = (url) => decodeURIComponent(new URL(url).pathname).replace(/^\/([A-Za-z]:)/, '$1').split('?')[0];

async function montar() {
  draco ??= await decodificadorDraco();
  const carregadores = {
    glb: async (url) => carregarGlbNoNode(caminho(url), draco),
    textura: async () => new THREE.Texture(),
    json: async (url) => JSON.parse(readFileSync(caminho(url), 'utf8')),
  };
  const lib = new WeaponLibrary({ sdf: null, carregadores });
  const weapons = {
    has: (id) => id === 'knife', source: () => 'glb', describe: (id) => lib.describe(id), info: (id) => lib.info(id),
    instance: (id, o) => lib.instance(id, o),
  };
  const hands = { async createArm(side) { return { side, mesh: new THREE.Object3D(), setPose() {}, setArmband() {}, place() {}, dispose() {} }; } };
  const events = new EventBus();
  const config = new Config(CONFIG_SCHEMA, { events });
  const render = {
    renderer: { compileAsync: async () => {}, shadowMap: { enabled: false, needsUpdate: false } },
    pipeline: { addLayer: () => () => {} }, shadowLevel: 0,
  };
  const luvas = new LuvasSource({ carregadores, sdf: sdfDeTeste(24) });
  const vm = new Viewmodel({ render, weapons, hands, luvas, config, events });
  const camera = new THREE.PerspectiveCamera(74, 16 / 9, 0.5, 400);
  for (let i = 0; i < 400; i++) {
    vm.frame(camera, 1 / 60, { item: 'knife', visible: true });
    if (vm.status().item === 'knife' && vm.layer.visible) return { vm, config, camera, info: weapons.info('knife') };
    await new Promise((r) => setTimeout(r, 5));
  }
  throw new Error('o viewmodel não segurou a faca');
}

/** O ponto (referencial da câmera) na tela: x e y de −1 a 1 dentro do quadro. */
function naTela(p, fovV, aspect) {
  const t = Math.tan((fovV * Math.PI) / 360);
  return { x: p.x / (-p.z * t * aspect), y: p.y / (-p.z * t), frente: p.z < -VIEWMODEL.near };
}

test('viewmodel da faca: só o braço direito, na pega de martelo do .glb', async () => {
  const { vm, info } = await montar();
  assert.deepEqual(handSides(info), ['direita']);
  assert.deepEqual(info.pega.lados, ['d']);
  assert.deepEqual(vm.status().arms, ['direita']);
  assert.equal(vm.status().bracos, 'luvas');
  vm.dispose();
});

test('viewmodel da faca: a pose da M9 do CS2 e o pulso nos limites da AAOS nas três posições prontas', async () => {
  const { vm, config, camera, info } = await montar();
  for (const id of Object.keys(VIEWMODEL.presets)) {
    applyViewmodelPreset(config, id);
    vm.frame(camera, 1 / 60, { item: 'knife', visible: true });
    const fovV = viewmodelVerticalFov(VIEWMODEL.presets[id].fov);
    const pl = vm.placement;
    // o dorso (os dentes) para baixo e o gume para cima, a face da lâmina para a câmera e a lâmina para a esquerda
    const dorso = new THREE.Vector3(0, 1, 0).applyQuaternion(pl.quaternion);
    const face = new THREE.Vector3(0, 0, 1).applyQuaternion(pl.quaternion);
    const lamina = new THREE.Vector3(1, 0, 0).applyQuaternion(pl.quaternion);
    assert.ok(dorso.y < -0.6, `posição ${id}: o dorso em ${dorso.toArray().map((v) => v.toFixed(2))}`);
    assert.ok(face.z > 0.6, `posição ${id}: a face da lâmina a ${face.z.toFixed(2)} da câmera`);
    assert.ok(lamina.x < -0.4 && lamina.y > 0, `posição ${id}: a lâmina em ${lamina.toArray().map((v) => v.toFixed(2))}`);
    // a ponta perto do centro da tela e a mão (o punho fechado no meio do cabo) embaixo à direita, dentro do quadro; o
    // pulso, abaixo do punho, fica fora da tela embaixo
    const naArma = (a) => naTela(new THREE.Vector3(...a).applyQuaternion(pl.quaternion).add(pl.position), fovV, 16 / 9);
    const ponta = naArma(info.anchors.ponta.pos);
    assert.ok(ponta.frente && Math.abs(ponta.x) < 0.4 && Math.abs(ponta.y) < 0.4, `posição ${id}: a ponta em ${ponta.x.toFixed(2)}, ${ponta.y.toFixed(2)}`);
    const mao = naArma(info.anchors.maoDireita.pos);
    assert.ok(mao.frente && mao.x > 0.15 && mao.x < 1 && mao.y < -0.3 && mao.y > -1, `posição ${id}: a mão em ${mao.x.toFixed(2)}, ${mao.y.toFixed(2)}`);
    const b = vm.gloves.bracos.direita;
    b.grupo.updateMatrixWorld(true);
    const inv = vm.root.matrixWorld.clone().invert();
    const pulso = b.ossos.mao.getWorldPosition(new THREE.Vector3()).applyMatrix4(inv);
    assert.ok(naTela(pulso, fovV, 16 / 9).frente, `posição ${id}: o pulso atrás da câmera`);
    // o pulso e o antebraço sem aviso e a no máximo 93 % de cada limite
    assert.deepEqual(vm.status().avisos, { direita: [], esquerda: [] }, `posição ${id}`);
    const { angulos: a, limites: l } = b;
    const razoes = {
      flexao: a.flexao >= 0 ? a.flexao / l.pulso.flexao : -a.flexao / l.pulso.extensao,
      desvio: a.desvio >= 0 ? a.desvio / l.pulso.radial : -a.desvio / l.pulso.ulnar,
      pronacao: a.pronacao >= 0 ? a.pronacao / l.antebraco.pronacao : -a.pronacao / l.antebraco.supinacao,
    };
    for (const [k, r] of Object.entries(razoes)) assert.ok(r <= 0.93, `posição ${id}: ${k} a ${(100 * r).toFixed(0)} % do limite`);
    // o cotovelo de verdade (o osso antebraco) fora da tela em 16:9 e 21:9 e abaixo do pulso
    const cotovelo = b.ossos.antebraco.getWorldPosition(new THREE.Vector3()).applyMatrix4(inv);
    assert.ok(cotovelo.y < pulso.y, `posição ${id}: o cotovelo acima do pulso`);
    for (const aspect of [16 / 9, 21 / 9]) {
      const c = naTela(cotovelo, fovV, aspect);
      assert.ok(!(c.frente && Math.abs(c.x) < 1 && Math.abs(c.y) < 1), `posição ${id}: o cotovelo aparece em ${aspect.toFixed(2)}`);
    }
  }
  vm.dispose();
});
