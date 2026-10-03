// O viewmodel com as luvas (Fase 4.1b; plano, Tarefa 10; 4.1c, Tarefa 12), sem GPU: a AK, a M4A4 e a Glock de verdade
// (o .glb pela biblioteca de armas, com o GLTFLoader do vendor e o Draco sem Workers) e as luvas de verdade
// (LuvasSource), e uma arma de massinha falsa (a primeira receita que sobrou: a AWP até a 4.1d). `handSides` dá os dois
// lados para a AK com pega e nenhum para a realista sem pega; `info.pega` vem do .glb; o viewmodel segura a AK com as
// luvas e a de massinha com os braços de massinha; a facção vem do time (`cl_bracadeira`) e, sem time, da do boneco; a
// braçadeira só com time; a facção troca os materiais sem recriar a malha; `status()` diz os braços; a esfera da sombra
// própria cobre as duas mãos de luva; e os cotovelos de luva do `rifle` (a AK e a M4A4 com o ajuste fino dela) e da
// `pistola` (a Glock) deixam o pulso dos dois lados dentro dos limites da AAOS nas três posições prontas do CS.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import * as THREE from 'three';
import { Config } from '../src/core/config.js';
import { EventBus } from '../src/core/events.js';
import { ARMAS } from '../src/data/armas/index.js';
import { ARMAS_REAIS } from '../src/data/armasReais.js';
import { CONFIG_SCHEMA } from '../src/data/configSchema.js';
import { LUVAS } from '../src/data/luvas.js';
import { VIEWMODEL } from '../src/data/viewmodel.js';
import { LuvasSource } from '../src/characters/hands/luvasSource.js';
import { WeaponLibrary } from '../src/weapons/model/weaponLibrary.js';
import {
  applyViewmodelPreset, categoryPlacement, gloveFaction, gloveTarget, handSides, viewCategory, viewmodelVerticalFov,
} from '../src/weapons/viewmodel/placement.js';
import { Viewmodel } from '../src/weapons/viewmodel/viewmodel.js';
import { RAIZ, carregadoresDoDisco, decodificadorDraco, sdfDeTeste } from './luvasTestUtils.js';

const MM = 25.4;
let draco = null;
// A arma de massinha do teste: a primeira receita que ainda não virou realista (a AWP até a 4.1d).
const MASSINHA = Object.keys(ARMAS).find((id) => !ARMAS_REAIS[id]);
// As realistas que o teste segura pela biblioteca de verdade.
const REAIS = ['ak47', 'm4a4', 'glock'];

const json = (arquivo) => JSON.parse(readFileSync(join(RAIZ, arquivo), 'utf8'));

/** As armas: as realistas pela biblioteca de verdade (origem glb); a de massinha falsa (a receita, uma caixa). */
function armas() {
  const lib = new WeaponLibrary({ sdf: null, carregadores: carregadoresDoDisco(draco) });
  const real = (id) => REAIS.includes(id);
  const massinha = { id: MASSINHA, source: 'massinha', category: viewCategory(MASSINHA), hands: true, anchors: ARMAS[MASSINHA].anchors, radius: 5 };
  return {
    lib,
    has: (id) => real(id) || id === MASSINHA,
    source: (id) => (real(id) ? 'glb' : 'massinha'),
    describe: (id) => (real(id) ? lib.describe(id) : Promise.resolve(massinha)),
    info: (id) => (real(id) ? lib.info(id) : massinha),
    instance: async (id, o) => {
      if (real(id)) return lib.instance(id, o);
      const g = new THREE.Mesh(new THREE.BoxGeometry(6, 3, 1), new THREE.MeshBasicMaterial());
      g.userData.weapon = { id: MASSINHA, radius: 5 };
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
  const luvas = new LuvasSource({ carregadores: carregadoresDoDisco(draco), sdf: sdfDeTeste(24) });
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

test('viewmodel: luvas na AK, massinha na que ainda é de massinha, e o status diz os braços', async () => {
  const { vm, camera } = await montar();
  await segurar(vm, camera, 'ak47');
  let s = vm.status();
  assert.equal(s.bracos, 'luvas');
  assert.deepEqual(s.arms, ['direita', 'esquerda']);
  assert.equal(s.faccao, 'massaCrua');
  assert.ok(vm.gloves.bracos.direita.grupo.parent === vm.root, 'os braços de luva no referencial da câmera');
  await segurar(vm, camera, MASSINHA);
  s = vm.status();
  assert.equal(s.bracos, 'massinha');
  assert.deepEqual(vm.gloves.visiveis(), [], `as luvas somem com a ${MASSINHA}`);
  vm.frame(camera, 1 / 60, { item: MASSINHA, visible: true });
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

/**
 * Os cotovelos de luva da categoria da arma, nas três posições prontas do CS: nenhum aviso dos limites da AAOS, nenhum
 * ângulo do pulso ou do antebraço a mais de 93 % do limite, o cotovelo de verdade (o osso `antebraco`) abaixo do pulso
 * e fora da tela em 16:9 e 21:9 e cada antebraço para o seu lado do pulso (a pega isósceles da pistola; o triângulo do
 * fuzil, com o apoio debaixo do guarda-mão).
 */
async function conferirCotovelos(item) {
  const { vm, camera, config } = await montar();
  await segurar(vm, camera, item);
  for (const id of Object.keys(VIEWMODEL.presets)) {
    applyViewmodelPreset(config, id);
    vm.frame(camera, 1 / 60, { item, visible: true });
    const { avisos } = vm.status();
    assert.deepEqual(avisos, { direita: [], esquerda: [] }, `${item}, posição ${id}: ${JSON.stringify(avisos)}`);
    // e com folga: nenhum ângulo a mais de 93 % do limite (na P2 da 4.1b a supinação da esquerda da AK ficava a 97 %)
    for (const lado of ['direita', 'esquerda']) {
      const { angulos: a, limites: l } = vm.gloves.bracos[lado];
      const razoes = {
        flexao: a.flexao >= 0 ? a.flexao / l.pulso.flexao : -a.flexao / l.pulso.extensao,
        desvio: a.desvio >= 0 ? a.desvio / l.pulso.radial : -a.desvio / l.pulso.ulnar,
        pronacao: a.pronacao >= 0 ? a.pronacao / l.antebraco.pronacao : -a.pronacao / l.antebraco.supinacao,
      };
      for (const [k, r] of Object.entries(razoes)) assert.ok(r <= 0.93, `${item}, posição ${id}, ${lado}: ${k} a ${(100 * r).toFixed(0)} % do limite`);
    }
    // o cotovelo de verdade (o osso antebraco) fora da tela em 16:9 e 21:9, abaixo do pulso e do lado dele
    const fovV = viewmodelVerticalFov(VIEWMODEL.presets[id].fov);
    const t = Math.tan((fovV * Math.PI) / 360);
    for (const lado of ['direita', 'esquerda']) {
      const b = vm.gloves.bracos[lado];
      b.grupo.updateMatrixWorld(true);
      const inv = vm.root.matrixWorld.clone().invert();
      const cotovelo = b.ossos.antebraco.getWorldPosition(new THREE.Vector3()).applyMatrix4(inv);
      const pulso = b.ossos.mao.getWorldPosition(new THREE.Vector3()).applyMatrix4(inv);
      assert.ok(cotovelo.y < pulso.y, `${item}, posição ${id}, ${lado}: o cotovelo acima do pulso`);
      const sinal = lado === 'direita' ? 1 : -1;
      assert.ok(sinal * (cotovelo.x - pulso.x) >= -1e-9, `${item}, posição ${id}, ${lado}: o antebraço cruza para o outro lado`);
      for (const aspect of [16 / 9, 21 / 9]) {
        const naTela = cotovelo.z < -VIEWMODEL.near && Math.abs(cotovelo.x / (-cotovelo.z * t * aspect)) < 1 && Math.abs(cotovelo.y / (-cotovelo.z * t)) < 1;
        assert.ok(!naTela, `${item}, posição ${id}, ${lado}: o cotovelo aparece em ${aspect.toFixed(2)}`);
      }
    }
  }
  vm.dispose();
}

test('viewmodel: os cotovelos do rifle deixam os dois pulsos da AK nos limites da AAOS nas três posições prontas do CS', async () => {
  await conferirCotovelos('ak47');
});

test('viewmodel: a M4A4 com o ajuste fino dela, a pega dela e os cotovelos dela nos limites, cada antebraço do seu lado', async () => {
  await conferirCotovelos('m4a4');
});

test('viewmodel: os cotovelos da pistola deixam os dois pulsos da Glock nos limites, cada antebraço do seu lado', async () => {
  await conferirCotovelos('glock');
});

test('viewmodel: os cotovelos de luva das categorias (as sem cotovelos de luva usam os de massinha)', () => {
  assert.deepEqual(categoryPlacement('sniper').gloveElbows, categoryPlacement('sniper').elbows);
  assert.deepEqual(categoryPlacement('rifle').gloveElbows, { direita: [13.1, -8.2, 13.9], esquerda: [-9.9, -52.4, -9.7] });
  // a AK fica com os do rifle; a M4A4, com os dela (com os do rifle, o apoio a 96 % do limite e o cotovelo do gatilho
  // na altura do pulso)
  assert.deepEqual(categoryPlacement('rifle', null, 'ak47').gloveElbows, categoryPlacement('rifle').gloveElbows);
  const m4 = VIEWMODEL.weapons.m4a4.gloveElbows;
  assert.deepEqual(categoryPlacement('rifle', null, 'm4a4').gloveElbows, { direita: [...m4.direita], esquerda: [...m4.esquerda] });
  const p = VIEWMODEL.categories.pistola.gloveElbows;
  assert.deepEqual(categoryPlacement('pistola').gloveElbows, { direita: [...p.direita], esquerda: [...p.esquerda] });
  assert.notDeepEqual(categoryPlacement('pistola').gloveElbows, categoryPlacement('pistola').elbows, 'a pistola com os dela');
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
