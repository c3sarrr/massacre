// Testes do viewmodel parado (Fase 4.1; docs/phases/phase-4.md, seção 4.1, "Viewmodel parado" e "Testes"): o FOV no
// referencial do CS, a posição por categoria com os offsets e o ajuste fino da arma, o giro de base (boca para a
// frente, lado direito para a direita), as mãos nas âncoras, os cotovelos fora da tela e a arma dentro dela (em 16:9,
// com os valores padrão), quando aparece e some, a facção do acento na mão e as posições prontas do CS.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import * as THREE from 'three';
import { ARMAS } from '../src/data/armas/index.js';
import { ARMAS_REAIS } from '../src/data/armasReais.js';
import { HAND } from '../src/data/hands.js';
import { VIEWMODEL } from '../src/data/viewmodel.js';
import {
  HAND_ANCHOR, WEAPON_TO_VIEW, anchorPose, applyViewmodelPreset, categoryPlacement, currentViewmodelPreset, elbowTarget,
  handSides, viewCategory, viewFaction, viewPlacement, viewmodelVerticalFov, viewmodelVisible, weaponNudge,
} from '../src/weapons/viewmodel/placement.js';

const near = (a, b, eps = 1e-9, msg = '') => assert.ok(Math.abs(a - b) <= eps, `${msg} esperado ${b}, veio ${a}`);
const DEFAULT_OFFSET = { x: VIEWMODEL.offset.x.default, y: VIEWMODEL.offset.y.default, z: VIEWMODEL.offset.z.default };

/** Projeção de um ponto do referencial da câmera na tela (NDC), com o FOV padrão do viewmodel em 16:9. */
function ndc(p, aspect = 16 / 9) {
  const t = Math.tan((viewmodelVerticalFov(VIEWMODEL.fov.default) * Math.PI) / 360);
  return { x: p.x / (-p.z * t * aspect), y: p.y / (-p.z * t), front: p.z < -VIEWMODEL.near };
}

test('viewmodel: FOV como no CS (horizontal em 4:3 → vertical fixo)', () => {
  near(viewmodelVerticalFov(90), 73.7397952917, 1e-6, '90 do CS');
  near(viewmodelVerticalFov(60), 46.8264489, 1e-6, '60 do CS');
  assert.ok(viewmodelVerticalFov(VIEWMODEL.fov.max) > viewmodelVerticalFov(VIEWMODEL.fov.min));
});

test('viewmodel: giro de base leva a boca para a frente e o lado direito para a direita', () => {
  const muzzle = new THREE.Vector3(1, 0, 0).applyQuaternion(WEAPON_TO_VIEW);
  const right = new THREE.Vector3(0, 0, 1).applyQuaternion(WEAPON_TO_VIEW);
  const up = new THREE.Vector3(0, 1, 0).applyQuaternion(WEAPON_TO_VIEW);
  assert.ok(muzzle.distanceTo(new THREE.Vector3(0, 0, -1)) < 1e-9);
  assert.ok(right.distanceTo(new THREE.Vector3(1, 0, 0)) < 1e-9);
  assert.ok(up.distanceTo(new THREE.Vector3(0, 1, 0)) < 1e-9);
});

test('viewmodel: posição da categoria + offsets do CS (x direita, y frente, z cima) + ajuste fino da arma', () => {
  for (const cat of Object.keys(VIEWMODEL.categories)) {
    const base = VIEWMODEL.categories[cat];
    const zero = viewPlacement(cat, { offset: { x: 0, y: 0, z: 0 } });
    assert.deepEqual(zero.position.toArray(), [...base.pos], cat);
    const moved = viewPlacement(cat, { offset: { x: 1, y: 2, z: -0.5 } });
    assert.deepEqual(moved.position.toArray().map((v, i) => +(v - base.pos[i]).toFixed(9)), [1, -0.5, -2], `${cat}: offsets`);
    assert.ok(Math.abs(zero.quaternion.lengthSq() - 1) < 1e-9);
  }
  const nudge = weaponNudge('m4a4');
  assert.ok(nudge, 'a M4 tem ajuste fino');
  const m4 = viewPlacement('rifle', { offset: { x: 0, y: 0, z: 0 }, nudge });
  assert.deepEqual(m4.position.toArray().map((v, i) => +(v - VIEWMODEL.categories.rifle.pos[i]).toFixed(9)), [...nudge]);
  assert.equal(weaponNudge('ak47'), null);
});

test('viewmodel: ângulos (guinada + boca para a esquerda, arfagem + boca para cima, rolagem + topo para a esquerda)', () => {
  const dir = (angles) => new THREE.Vector3(1, 0, 0).applyQuaternion(viewPlacement('rifle', { tune: { angles } }).quaternion);
  const top = (angles) => new THREE.Vector3(0, 1, 0).applyQuaternion(viewPlacement('rifle', { tune: { angles } }).quaternion);
  assert.ok(dir([0, 10, 0]).x < -0.1, 'guinada');
  assert.ok(dir([10, 0, 0]).y > 0.1, 'arfagem');
  assert.ok(top([0, 0, 10]).x < -0.1, 'rolagem');
  assert.ok(dir([0, 0, 0]).distanceTo(new THREE.Vector3(0, 0, -1)) < 1e-9, 'sem giro: boca para a frente');
  // O ajuste ao vivo por cima dos dados, sem mexer nos dados.
  const tuned = categoryPlacement('rifle', { pos: [1, 2, 3], elbows: { direita: [9, 9, 9] } });
  assert.deepEqual(tuned.pos, [1, 2, 3]);
  assert.deepEqual(tuned.elbows.direita, [9, 9, 9]);
  assert.deepEqual(tuned.elbows.esquerda, [...VIEWMODEL.categories.rifle.elbows.esquerda]);
  assert.throws(() => categoryPlacement('bazuca'), /categoria/);
});

test('viewmodel: cada mão na âncora da receita, no referencial da câmera', () => {
  for (const id of Object.keys(ARMAS)) {
    const r = ARMAS[id];
    const pl = viewPlacement(viewCategory(id), { offset: DEFAULT_OFFSET, nudge: weaponNudge(id) });
    const m = new THREE.Matrix4().compose(pl.position, pl.quaternion, new THREE.Vector3(1, 1, 1));
    for (const side of handSides(r)) {
      const a = r.anchors[HAND_ANCHOR[side]];
      const pose = anchorPose(pl, a);
      const expected = new THREE.Vector3(...a.pos).applyMatrix4(m);
      assert.ok(pose.position.distanceTo(expected) < 1e-9, `${id}.${side}: pulso`);
      const q = pl.quaternion.clone().multiply(new THREE.Quaternion().setFromEuler(new THREE.Euler(...a.rot, 'XYZ')));
      assert.ok(Math.abs(Math.abs(pose.quaternion.dot(q)) - 1) < 1e-9, `${id}.${side}: giro`);
    }
    assert.deepEqual(handSides(r), id === 'knife' ? ['direita'] : ['direita', 'esquerda'], id);
  }
  // A arma realista sem as luvas (4.1a): as âncoras das mãos existem (os soquetes), mas nenhuma mão aparece.
  assert.deepEqual(handSides({ hands: false, anchors: ARMAS.glock.anchors }), []);
});

test('viewmodel: com os valores padrão em 16:9, a arma aparece e os cotovelos ficam fora da tela', () => {
  for (const id of Object.keys(ARMAS)) {
    const r = ARMAS[id];
    const cat = viewCategory(id);
    const pl = viewPlacement(cat, { offset: DEFAULT_OFFSET, nudge: weaponNudge(id) });
    // A arma na tela: a boca (ou, na faca, a ponta da lâmina) cai dentro do quadro, na metade de baixo à direita.
    const tipLocal = r.anchors.boca?.pos ?? [3.6, 0, 0];
    const tip = new THREE.Vector3(...tipLocal).applyQuaternion(pl.quaternion).add(pl.position);
    const t = ndc(tip);
    assert.ok(t.front && Math.abs(t.x) < 1 && Math.abs(t.y) < 1, `${id}: a boca fora da tela (${t.x.toFixed(2)}, ${t.y.toFixed(2)})`);
    assert.ok(t.x > -0.2 && t.y < 0.1, `${id}: a arma fica embaixo à direita (${t.x.toFixed(2)}, ${t.y.toFixed(2)})`);
    for (const side of handSides(r)) {
      const wrist = anchorPose(pl, r.anchors[HAND_ANCHOR[side]]).position;
      assert.ok(wrist.z < -VIEWMODEL.near, `${id}.${side}: o pulso na frente da câmera`);
      const target = elbowTarget(cat, side);
      const dir = target.clone().sub(wrist).normalize();
      const elbow = wrist.clone().addScaledVector(dir, HAND.forearm.length);
      const e = ndc(elbow);
      assert.ok(!e.front || Math.abs(e.x) > 1 || Math.abs(e.y) > 1, `${id}.${side}: o cotovelo aparece (${e.x.toFixed(2)}, ${e.y.toFixed(2)})`);
      // O antebraço vai para baixo (o cotovelo abaixo do pulso).
      assert.ok(elbow.y < wrist.y, `${id}.${side}: o cotovelo acima do pulso`);
    }
  }
});

test('viewmodel: quando aparece e quando some', () => {
  const base = {
    enabled: true, firstPerson: true, alive: true, noclip: false, zoomed: false, item: 'ak47',
    hasModel: (id) => Boolean(ARMAS[id] || ARMAS_REAIS[id]),
  };
  assert.equal(viewmodelVisible(base), true);
  assert.equal(viewmodelVisible({ ...base, firstPerson: false }), false, 'terceira pessoa');
  assert.equal(viewmodelVisible({ ...base, noclip: true }), false, 'noclip');
  assert.equal(viewmodelVisible({ ...base, alive: false }), false, 'morto');
  assert.equal(viewmodelVisible({ ...base, zoomed: true }), false, 'luneta aberta');
  assert.equal(viewmodelVisible({ ...base, enabled: false }), false, 'r_viewmodel 0');
  assert.equal(viewmodelVisible({ ...base, item: 'usps' }), false, 'arma sem modelo (4.4)');
  assert.equal(viewmodelVisible({ ...base, item: 'he' }), false, 'granada (4.7)');
  assert.equal(viewmodelVisible({ ...base, item: 'c4' }), false, 'bomba (Fase 8)');
  assert.equal(viewmodelVisible({ ...base, item: null }), false, 'mão vazia');
  assert.equal(viewCategory('usps'), null);
});

test('viewmodel: o acento da arma na mão', () => {
  assert.equal(viewFaction('glock', 'ct'), 'tr', 'arma de um lado fica com o seu');
  assert.equal(viewFaction('m4a4', 'tr'), 'ct');
  assert.equal(viewFaction('awp', 'ct'), 'ct', 'arma dos dois lados pega o time de quem segura');
  assert.equal(viewFaction('awp', 'tr'), 'tr');
  assert.equal(viewFaction('awp', null), 'ambos', 'sem time: amarelo e branco');
  assert.equal(viewFaction('knife', 'off'), 'ambos');
});

test('viewmodel: posições prontas do CS (viewmodel_presetpos)', () => {
  const store = new Map();
  const config = { set: (k, v) => store.set(k, v), get: (k) => store.get(k) };
  for (const [id, p] of Object.entries(VIEWMODEL.presets)) {
    applyViewmodelPreset(config, id);
    assert.equal(store.get('viewmodel.fov'), p.fov);
    assert.equal(currentViewmodelPreset(config), id);
  }
  config.set('viewmodel.offsetX', 0.3);
  assert.equal(currentViewmodelPreset(config), null, 'ajustada à mão');
  assert.throws(() => applyViewmodelPreset(config, '7'), /posição desconhecida/);
  // O "Mesa" é o padrão da config.
  const d = VIEWMODEL.presets[1];
  assert.deepEqual([d.fov, d.x, d.y, d.z], [VIEWMODEL.fov.default, DEFAULT_OFFSET.x, DEFAULT_OFFSET.y, DEFAULT_OFFSET.z]);
});
