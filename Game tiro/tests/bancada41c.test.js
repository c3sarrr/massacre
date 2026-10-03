// A bancada `arsenal` com as armas da 4.1c (plano da 4.1c, Tarefa 13), sem GPU: a Glock-18, a M4A4 e a baioneta M9 nas
// fileiras e na roda com a AK (os ids da bancada, na ordem das fileiras); a planta a lápis de cada realista saindo da
// ficha, posta no referencial da arma pela origem da ficha (o `origemMM` do relatório: a boca nas armas de fogo, a ponta
// na faca, que não tem boca), a mesma conta do contorno sobreposto à arma na roda; a "Explodir" com cada peça móvel
// saindo da arma pelo lado dela (o carregador da Glock pelo eixo do punho); a skin de fábrica e as nomeadas nos
// materiais das três (a faca só com as zonas dela); e o "Segurar" com as luvas nas três, na facção escolhida no painel.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import * as THREE from 'three';
import { Config } from '../src/core/config.js';
import { EventBus } from '../src/core/events.js';
import { ARSENAL } from '../src/data/arsenal.js';
import { ARMAS_REAIS, zonasDaArma } from '../src/data/armasReais.js';
import { CONFIG_SCHEMA } from '../src/data/configSchema.js';
import { FACCOES_DAS_LUVAS } from '../src/data/luvas.js';
import { SKINS_ARMA } from '../src/data/skinsArma.js';
import { LuvasSource } from '../src/characters/hands/luvasSource.js';
import { ArsenalBench, explodeDir } from '../src/maps/arsenal/bench.js';
import { planSheetLayout } from '../src/maps/arsenal/planSheets.js';
import { MM_POR_U, fotoDoContorno, origemDaFicha } from '../src/weapons/model/ficha.js';
import { placeReference } from '../src/weapons/model/silhouette.js';
import { WeaponLibrary } from '../src/weapons/model/weaponLibrary.js';
import { skinDeFabrica, skinPorNome } from '../src/weapons/skins/skin.js';
import { handSides } from '../src/weapons/viewmodel/placement.js';
import { Viewmodel } from '../src/weapons/viewmodel/viewmodel.js';
import { RAIZ, carregadoresDoDisco, decodificadorDraco, sdfDeTeste } from './luvasTestUtils.js';

const DA_41C = ['glock', 'm4a4', 'knife'];
const REAIS = Object.keys(ARMAS_REAIS);
let draco = null;

const json = (arquivo) => JSON.parse(readFileSync(join(RAIZ, arquivo), 'utf8'));
const near = (a, b, eps, msg) => assert.ok(Math.abs(a - b) <= eps, `${msg}: ${a} ≠ ${b} (±${eps})`);

async function biblioteca() {
  draco ??= await decodificadorDraco();
  return new WeaponLibrary({ sdf: null, carregadores: carregadoresDoDisco(draco) });
}

/** A caixa (x0, x1, y0, y1) de um anel de pontos. */
function caixa(anel) {
  const xs = anel.map((p) => p[0]);
  const ys = anel.map((p) => p[1]);
  return { x0: Math.min(...xs), x1: Math.max(...xs), y0: Math.min(...ys), y1: Math.max(...ys) };
}

test('bancada: as realistas nas fileiras, uma vez cada, e a roda com toda arma que tem modelo, na ordem das fileiras', async () => {
  const nasFileiras = ARSENAL.rows.flatMap((r) => r.ids);
  assert.equal(new Set(nasFileiras).size, nasFileiras.length, 'nenhuma arma repetida nas fileiras');
  for (const id of REAIS) assert.equal(nasFileiras.filter((x) => x === id).length, 1, `${id} numa fileira`);
  const lib = await biblioteca();
  try {
    const bancada = new ArsenalBench({ set: null, weapons: lib });
    assert.deepEqual(bancada.ids, nasFileiras.filter((id) => lib.has(id)), 'a roda na ordem das fileiras');
    assert.deepEqual([...bancada.ids].sort(), [...lib.ids].sort(), 'toda arma com modelo está na bancada');
    for (const id of DA_41C) assert.equal(lib.source(id), 'glb', `${id}: a do Blender na bancada`);
  } finally {
    lib.dispose();
  }
});

test('planta a lápis: a de cada realista sai da ficha, posta pela origem da ficha (a boca; na faca, a ponta)', async () => {
  const lib = await biblioteca();
  try {
    for (const id of REAIS) {
      const info = await lib.describe(id);
      const ficha = json(`tools/blender/refs/${id}.json`);
      assert.deepEqual(info.plan.points, ficha.contorno.map(([x, y]) => [x / MM_POR_U, y / MM_POR_U]), `${id}: o contorno da ficha`);
      assert.deepEqual(info.planOrigin, origemDaFicha(info.report.origemMM), `${id}: a origem pelo relatório`);
      // nas armas de fogo, a origem da ficha é a boca do cano (o soquete do .glb, em float32)
      if (info.anchors.boca) {
        near(info.planOrigin[0], info.anchors.boca.pos[0], 1e-5, `${id}: x da boca`);
        near(info.planOrigin[1], info.anchors.boca.pos[1], 1e-5, `${id}: y da boca`);
      }
      const folha = planSheetLayout({ id, info, plan: info.plan });
      // a folha e o contorno sobreposto à arma na roda: a mesma conta
      const { outline, holes } = placeReference(info, info.plan);
      assert.deepEqual(folha.rings, [outline, ...holes], `${id}: a folha e a sobreposição`);
      // a planta posta cobre a arma: cada lado da caixa a no máximo 1 % do comprimento do da arma
      const c = caixa(folha.rings[0]);
      const tol = info.lengthU * 0.01;
      near(c.x0, info.bounds.min[0], tol, `${id}: a traseira`);
      near(c.x1, info.bounds.max[0], tol, `${id}: a frente`);
      near(c.y0, info.bounds.min[1], tol, `${id}: o pé`);
      near(c.y1, info.bounds.max[1], tol, `${id}: o alto`);
      assert.ok(folha.credit.includes(fotoDoContorno(ficha).arquivo.replace(/^File:/, '').slice(0, 40)), `${id}: o crédito da foto`);
    }
    // a faca não tem boca: a origem da ficha é a ponta da lâmina (a âncora `ponta` e a frente da caixa)
    const faca = lib.info('knife');
    assert.equal(faca.anchors.boca, undefined);
    near(faca.planOrigin[0], faca.anchors.ponta.pos[0], 1e-5, 'a faca: a origem na ponta');
    // a ponta da malha, arredondada no Blender, fica a 0,06 mm da ponta da ficha
    near(faca.planOrigin[0], faca.bounds.max[0], 0.004, 'a faca: a ponta na frente da caixa');
    assert.throws(() => placeReference({ id: 'teste', planOrigin: null, anchors: {} }, faca.plan), /teste: a planta sem origem/);
    assert.throws(() => origemDaFicha(undefined, 'teste'), /teste: o relatório sem a origemMM/);
  } finally {
    lib.dispose();
  }
});

test('explodir: cada peça móvel das realistas sai da arma — com direção, pelo lado dela, o carregador pelo eixo', async () => {
  const lib = await biblioteca();
  try {
    for (const id of REAIS) {
      const inst = await lib.instance(id, { lod: 'perto' });
      inst.updateMatrixWorld(true);
      const parts = inst.userData.weapon.parts;
      assert.deepEqual(Object.keys(parts).sort(), [...ARMAS_REAIS[id].pecas].sort(), `${id}: as peças móveis`);
      for (const [nome, peca] of Object.entries(parts)) {
        const d = explodeDir(id, nome, peca);
        assert.ok(Math.hypot(...d) > 0.5, `${id}.${nome}: sem direção na "Explodir"`);
        // a peça inteira de um lado do plano do cano sai por esse lado (nunca atravessando a arma para o outro)
        const b = new THREE.Box3().setFromObject(peca);
        if (b.min.z > 0) assert.ok(d[2] >= 0, `${id}.${nome}: do lado direito, saindo para a esquerda`);
        if (b.max.z < 0) assert.ok(d[2] <= 0, `${id}.${nome}: do lado esquerdo, saindo para a direita`);
        if (nome === 'carregador' && peca.userData.axis) assert.deepEqual(d, peca.userData.axis, `${id}: o carregador pelo eixo`);
      }
    }
    // a corrediça da Glock sobe da armação; o carregador dela desce pelo eixo do punho, para trás
    const glock = (await lib.instance('glock')).userData.weapon.parts;
    assert.deepEqual(explodeDir('glock', 'ferrolho', glock.ferrolho), [0, 1, 0]);
    const eixo = explodeDir('glock', 'carregador', glock.carregador);
    assert.ok(eixo[0] < -0.3 && eixo[1] < -0.9, `o carregador da Glock em ${eixo}`);
  } finally {
    lib.dispose();
  }
});

test('skins nas três: a de fábrica e as nomeadas nos materiais de cada zona (a faca só com as zonas dela)', async () => {
  const lib = await biblioteca();
  try {
    for (const id of DA_41C) {
      for (const skin of [skinDeFabrica(id), ...Object.keys(SKINS_ARMA).map((k) => skinPorNome(id, k))]) {
        lib.setSkin(id, skin);
        const inst = await lib.instance(id, { lod: 'perto' });
        const zonas = new Set();
        inst.traverse((o) => {
          if (!o.isMesh) return;
          zonas.add(o.userData.zona);
          assert.equal(o.material.userData.acabamento, skin.zonas[o.userData.zona].acabamento, `${id} · ${skin.nome} · ${o.userData.zona}`);
        });
        assert.deepEqual([...zonas].sort(), [...zonasDaArma(id)].sort(), `${id}: as zonas do .glb`);
      }
    }
    assert.deepEqual(Object.keys(lib.skinOf('knife').zonas), ['corpo', 'guarnicao', 'detalhes'], 'a faca sem carregador nem interno');
  } finally {
    lib.dispose();
  }
});

test('"Segurar" da bancada: as três nas luvas, na facção escolhida no painel, com as mãos de cada categoria', async () => {
  draco ??= await decodificadorDraco();
  const lib = await biblioteca();
  const weapons = {
    has: (id) => DA_41C.includes(id), source: () => 'glb', describe: (id) => lib.describe(id), info: (id) => lib.info(id),
    instance: (id, o) => lib.instance(id, o),
  };
  const hands = { async createArm(side) { return { side, mesh: new THREE.Object3D(), setPose() {}, setArmband() {}, place() {}, dispose() {} }; } };
  const events = new EventBus();
  const config = new Config(CONFIG_SCHEMA, { events });
  const render = {
    renderer: { compileAsync: async () => {}, shadowMap: { enabled: false, needsUpdate: false } },
    pipeline: { addLayer: () => () => {} }, shadowLevel: 0,
  };
  const luvas = new LuvasSource({ carregadores: carregadoresDoDisco(draco), sdf: sdfDeTeste(24) });
  const vm = new Viewmodel({ render, weapons, hands, luvas, config, events });
  const camera = new THREE.PerspectiveCamera(74, 16 / 9, 0.5, 400);
  try {
    for (const id of DA_41C) {
      for (const gloves of FACCOES_DAS_LUVAS) {
        // o estado do viewmodel que o MatchState monta no "Segurar" (hold: a arma da roda, o nível e a facção das luvas)
        const estado = { item: id, visible: true, faction: null, lod: 'perto', gloves };
        let ok = false;
        for (let i = 0; i < 400 && !ok; i++) {
          vm.frame(camera, 1 / 60, estado);
          const s = vm.status();
          ok = s.item === id && vm.layer.visible && s.bracos === 'luvas' && s.faccao === gloves;
          if (!ok) await new Promise((r) => setTimeout(r, 5));
        }
        assert.ok(ok, `${id}: o viewmodel não segurou com as luvas ${gloves}`);
        const s = vm.status();
        assert.deepEqual(s.arms, handSides(lib.info(id)), `${id} · ${gloves}: as mãos da categoria`);
        // o pulso de cada braço nos limites da AAOS (e o braço escondido da faca sem os avisos da arma anterior)
        assert.deepEqual(s.avisos, { direita: [], esquerda: [] }, `${id} · ${gloves}: os avisos do pulso`);
      }
    }
  } finally {
    vm.dispose();
    lib.dispose();
  }
});
