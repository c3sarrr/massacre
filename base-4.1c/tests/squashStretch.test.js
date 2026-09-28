// Testes do corpo (subfase 3.5): volume constante; sequência do pulo e do wall-jump (−10% → +14%); estica caindo; o
// pouso achata na hora pelo fator (11%, 17%, 30%, 42%) e passa do normal na volta; limites; morte (−62%) e a volta;
// agachar (72 → 54 u como a cápsula); mola exata; o boneco de referência com botas (72 u, pivô no tornozelo, sola das
// pegadas) e o corpo no mundo (a forma só muda na troca de pose; visível em terceira pessoa e no noclip).
import { test } from 'node:test';
import assert from 'node:assert/strict';
import * as THREE from 'three';
import { FALL, HULL } from '../src/data/movement.js';
import { REFERENCE_DOLL } from '../src/data/referenceDoll.js';
import { SOLE } from '../src/data/footprints.js';
import {
  ANKLE, DUCK_DROP, JUMP_KICK, bodyShape, createSquash, resetSquash, updateSquash,
} from '../src/characters/squashStretch.js';
import { PlayerBody } from '../src/characters/playerBody.js';
import { clayBoot, cleatBars, soleOutline } from '../src/clay/kit/boots.js';
import { referenceDoll } from '../src/clay/kit/scaleMarker.js';
import { SOLE_EXTENT, soleDistance } from '../src/clay/prints/sole.js';
import { PlayerPawn } from '../src/player/playerPawn.js';
import { createMoveState } from '../src/player/movement.js';
import { createSvVars } from '../src/player/movementVars.js';
import { floor, worldOf } from './worldTestUtils.js';

const DT = 1 / 64;
const Q = REFERENCE_DOLL.squash;

/** Estado de movimento no chão ou no ar com a velocidade vertical dada. */
function moveState({ onGround = true, vy = 0 } = {}) {
  const s = createMoveState();
  s.onGround = onGround;
  s.velocity.y = vy;
  return s;
}

/** Roda a mola `ticks` ticks no estado `s`; eventos só no primeiro. Devolve os valores de x por tick. */
function springRun(sq, s, ticks, events = [], alive = true) {
  const xs = [];
  for (let i = 0; i < ticks; i++) {
    updateSquash(sq, s, i === 0 ? events : [], alive, DT);
    xs.push(sq.x);
  }
  return xs;
}

test('volume constante: altura × (1 + x), largura × 1/√(1 + x); botas alargam até 16%', () => {
  for (const x of [-0.45, -0.3, -0.1, 0, 0.12, 0.35]) {
    for (const duck of [0, 0.5, 1]) {
      const sh = bodyShape({ x, v: 0 }, duck);
      assert.ok(Math.abs(sh.sy * sh.sxz * sh.sxz - 1) < 1e-12, `x ${x}, agachar ${duck}`);
    }
  }
  assert.equal(bodyShape({ x: 0, v: 0 }, 0).widen, 0);
  assert.ok(Math.abs(bodyShape({ x: -0.3, v: 0 }, 0).widen - 0.105) < 1e-12);
  assert.equal(bodyShape({ x: -0.62, v: 0 }, 0).widen, REFERENCE_DOLL.bootWiden.max);
  assert.equal(bodyShape({ x: 0.2, v: 0 }, 0).widen, 0);
});

test('agachar: a altura acima do tornozelo cai junto com a cápsula (72 → 54 u)', () => {
  assert.ok(Math.abs(ANKLE - 72 * 0.06) < 1e-9);
  const top = (duck) => ANKLE + (HULL.standHeight - ANKLE) * bodyShape({ x: 0, v: 0 }, duck).sy;
  assert.ok(Math.abs(top(0) - HULL.standHeight) < 1e-9);
  assert.ok(Math.abs(top(1) - HULL.duckHeight) < 1e-9);
  assert.ok(DUCK_DROP > 0.26 && DUCK_DROP < 0.27, `queda por agachar ${DUCK_DROP}`);
});

test('pulo e wall-jump: o tick do evento mostra −10% e a mola estica até +14%', () => {
  for (const type of ['jump', 'walljump']) {
    const sq = createSquash();
    const xs = springRun(sq, moveState({ onGround: false, vy: 280 }), 40, [{ type }]);
    assert.equal(xs[0], Q.jumpStart, type);
    const peak = Math.max(...xs);
    assert.ok(peak > 0.138 && peak <= Q.jumpPeak + 1e-9, `${type}: pico ${peak}`);
    assert.ok(xs.indexOf(peak) >= 3 && xs.indexOf(peak) <= 8, `pico no tick ${xs.indexOf(peak)}`);
  }
  assert.ok(JUMP_KICK > 0);
});

test('caindo estica pela velocidade de queda (até 12% a 800 u/s); subindo não', () => {
  const settle = (vy) => springRun(createSquash(), moveState({ onGround: false, vy }), 128).at(-1);
  assert.ok(Math.abs(settle(-800) - Q.fall) < 1e-3, `a 800: ${settle(-800)}`);
  assert.ok(Math.abs(settle(-1600) - Q.fall) < 1e-3, 'acima de 800 não passa de 12%');
  assert.ok(Math.abs(settle(-400) - Q.fall / 2) < 1e-3, `a 400: ${settle(-400)}`);
  assert.ok(Math.abs(settle(300)) < 1e-3, 'subindo: normal');
});

test('pouso: achata na hora 30% × o fator da queda (11%, 17%, 30%, 42%) e volta passando do normal', () => {
  const cases = [[301.993377, 0.1105], [Math.sqrt(2 * 800 * 128), 0.1657], [FALL.safeSpeed, 0.3], [FALL.fatalSpeed, 0.42]];
  for (const [speed, want] of cases) {
    const sq = createSquash();
    const xs = springRun(sq, moveState(), 64, [{ type: 'land', speed }]);
    assert.ok(Math.abs(xs[0] + want) < 1e-3, `queda a ${speed}: ${xs[0]}`);
    assert.equal(Math.min(...xs), xs[0], 'a pose de contato é a mais achatada');
    const over = Math.max(...xs);
    assert.ok(over > want * 0.2 && over < want * 0.3, `passa do normal: ${over}`);
    assert.ok(Math.abs(xs.at(-1)) < want * 0.05, 'assenta em ~1 s');
  }
  // Pouso lento (abaixo de 150 u/s): nada muda na hora.
  const soft = createSquash();
  soft.x = 0.05;
  springRun(soft, moveState(), 1, [{ type: 'land', speed: 100 }]);
  assert.ok(soft.x > 0.04, 'pouso lento não achata');
});

test('limites (−45% e +35%), morte (−62%) e a volta ao jogo', () => {
  const sq = createSquash();
  sq.v = 100;
  updateSquash(sq, moveState(), [], true, DT);
  assert.equal(sq.x, Q.max);
  sq.x = 0;
  sq.v = -100;
  updateSquash(sq, moveState(), [], true, DT);
  assert.equal(sq.x, Q.min);
  const dead = createSquash();
  const xs = springRun(dead, moveState(), 128, [], false);
  assert.ok(Math.min(...xs) >= Q.dead - 1e-12, 'nunca abaixo do limite da morte');
  assert.ok(Math.abs(xs.at(-1) - Q.dead) < 1e-3, `morto: ${xs.at(-1)}`);
  const ignored = createSquash();
  springRun(ignored, moveState(), 1, [{ type: 'jump' }], false);
  assert.notEqual(ignored.x, Q.jumpStart, 'morto não pula');
  resetSquash(dead);
  assert.deepEqual(dead, createSquash());
});

test('mola exata: dois ticks de 1/64 s dão o mesmo que um de 1/32 s', () => {
  const a = createSquash();
  const b = createSquash();
  const s = moveState();
  updateSquash(a, s, [{ type: 'land', speed: 900 }], true, 0);
  updateSquash(b, s, [{ type: 'land', speed: 900 }], true, 0);
  for (let i = 0; i < 20; i++) {
    updateSquash(a, s, [], true, DT);
    updateSquash(a, s, [], true, DT);
    updateSquash(b, s, [], true, 2 * DT);
  }
  assert.ok(Math.abs(a.x - b.x) < 1e-9 && Math.abs(a.v - b.v) < 1e-9);
});

test('sola e botas: contorno de 15,8 × 7,8 u (16,4 sem o corte), bico desviado para dentro, cravos por baixo', () => {
  assert.ok(Math.abs(SOLE_EXTENT.nominalLength - 16.4) < 1e-9);
  assert.ok(Math.abs(SOLE_EXTENT.length - 15.8) < 1e-9);
  assert.equal(SOLE_EXTENT.width, 7.8);
  assert.ok(soleDistance(0, 0) < 0 && soleDistance(SOLE.cut + 0.01, 0) > 0 && soleDistance(-8.19, 0) < 0);
  // Bico para dentro: no bico, o lado de dentro (bi > 0) vai mais longe que o de fora.
  assert.ok(soleDistance(4.3, 4.1) < 0 && soleDistance(4.3, -4.1) > 0);
  const outline = soleOutline(0);
  const as = outline.map(([a]) => a);
  assert.ok(Math.abs(Math.min(...as) - SOLE_EXTENT.back) < 0.01 && Math.abs(Math.max(...as) - SOLE_EXTENT.front) < 0.01);
  assert.ok(outline.every(([a, bi]) => Math.abs(soleDistance(a, bi)) < 0.01), 'no contorno (cordas de ~0,1 u)');
  const bars = cleatBars();
  assert.equal(bars.filter((b) => b.a0 > -1.01).length, 4, 'quatro barras transversais na frente');
  assert.equal(bars.filter((b) => b.a1 <= -2.6 + 1e-9).length, 3, 'três barras ao comprido no calcanhar');
  for (const b of bars) assert.ok(soleDistance((b.a0 + b.a1) / 2, (b.b0 + b.b1) / 2) < 0);
  const left = clayBoot({ foot: 'left' });
  const right = clayBoot({ foot: 'right' });
  left.geometry.computeBoundingBox();
  right.geometry.computeBoundingBox();
  const L = left.geometry.boundingBox;
  const R = right.geometry.boundingBox;
  assert.ok(Math.abs(L.max.y - REFERENCE_DOLL.boots.height) < 0.1 && L.min.y > -0.1, `altura ${L.min.y}..${L.max.y}`);
  assert.ok(Math.abs(L.min.x + R.max.x) < 0.1 && Math.abs(L.max.x + R.min.x) < 0.1, 'pé esquerdo e direito espelhados');
  assert.ok(-L.min.x > L.max.x, 'lado de dentro do pé esquerdo em −X');
  assert.ok(left.distance(new THREE.Vector3(0, 2, 0)) < 0 && left.distance(new THREE.Vector3(0, 7, 0)) > 0);
  assert.ok(left.geometry.attributes.aTouch && left.geometry.attributes.aSeam);
});

test('boneco de referência: 72 u com as botas, corpo 6% menor sobre elas, uma malha por cor de massa', () => {
  const doll = referenceDoll(72, { seed: 'teste-boneco' });
  const box = new THREE.Box3().setFromObject(doll.group);
  assert.ok(box.max.y > 71 && box.max.y <= 72.2, `altura ${box.max.y}`);
  assert.ok(Math.abs(doll.ankle - 72 * (1 - REFERENCE_DOLL.bodyScale)) < 1e-9);
  assert.equal(doll.group.children.length, 4, 'corpo, olhos, pupilas e botas');
  assert.equal(doll.upper.length, 3);
  const boots = new THREE.Box3().setFromObject(doll.boots);
  assert.ok(boots.max.y < 5 && boots.min.x < -8 && boots.max.x > 8, 'as duas botas nos lados, até ~4,5 u');
  // Costura: o corpo ganhou sulco onde encosta nas botas.
  const body = doll.upper.find((m) => m.material.clay.color === REFERENCE_DOLL.boots.color) ?? doll.upper[0];
  const seam = body.geometry.attributes.aSeam.array;
  assert.ok(seam.some((v) => v > 0.2), 'costura no corpo');
});

test('corpo no mundo: a forma só muda na troca de pose; pés interpolados; visível em terceira pessoa e no noclip', () => {
  const scene = new THREE.Scene();
  const world = worldOf((b) => floor(b));
  const pawn = new PlayerPawn({ world, sv: createSvVars(), position: new THREE.Vector3(0, 0, 0) });
  const body = new PlayerBody({ scene, world, seed: 'teste-corpo' });
  const input = { move: { x: 0, y: 0 }, isDown: (a) => a === 'jump', pressed: () => false };
  body.onPose(pawn);
  const before = body.pivot.scale.toArray();
  pawn.tick(DT, input, { tick: 1 });
  body.tick(pawn, DT);
  assert.equal(body.squash.x, Q.jumpStart, 'a mola anda no tick');
  assert.deepEqual(body.pivot.scale.toArray(), before, 'sem pose, a forma não muda');
  body.onPose(pawn);
  assert.ok(body.pivot.scale.y < before[1] && body.pivot.scale.x > before[0], 'na pose, achata e alarga');
  assert.ok(Math.abs(body.pivot.scale.y * body.pivot.scale.x ** 2 - 1) < 1e-9);
  body.update(pawn, 0.5);
  assert.equal(body.root.visible, false, 'primeira pessoa: escondido');
  pawn.thirdPerson = true;
  body.update(pawn, 0.5);
  assert.ok(body.root.visible && body.shadow.visible);
  const mid = pawn.prevOrigin.clone().lerp(pawn.state.origin, 0.5);
  assert.ok(body.root.position.distanceTo(mid) < 1e-9);
  assert.ok(Math.abs(body.shadow.material.opacity - REFERENCE_DOLL.shadow.opacity) < 0.01, 'no chão: sombra cheia');
  assert.ok(Math.abs(body.root.rotation.y - (pawn.yaw + Math.PI)) < 1e-12);
  body.reset();
  assert.deepEqual(body.squash, createSquash());
  body.dispose();
  assert.equal(scene.children.length, 0);
});
