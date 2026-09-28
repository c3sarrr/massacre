// Testes da sensação da câmera (subfase 3.5): balanço preso ao relógio de passos (o ponto mais baixo no tick do passo,
// média zero numa passada, lado do pé), peso zero no ar, no slide e parado; inclinação de lado pela velocidade e o
// sinal; slide; chute do wall-jump (pico de 5,7° em ~77 ms, para longe da parede); picos do mergulho (4,4 u no pulo e
// 12 u na queda de 420 u a 100%) e o nível Médio; escalas; molas exatas (o mesmo resultado em ticks de qualquer tamanho
// que somem o mesmo tempo). O movimento é o de verdade (playerMove sobre um chão).
import { test } from 'node:test';
import assert from 'node:assert/strict';
import * as THREE from 'three';
import { CAMERA_FEEL, CAMERA_FEEL_DEFAULT, CAMERA_FEEL_LEVELS } from '../src/data/cameraFeel.js';
import { FALL } from '../src/data/movement.js';
import { FEEL_SPRINGS, createCameraFeel, landFactor, resetCameraFeel, updateCameraFeel } from '../src/player/cameraFeel.js';
import { BTN } from '../src/player/moveCmd.js';
import { createMoveState } from '../src/player/movement.js';
import { floor, worldOf } from './worldTestUtils.js';
import { DT, forward, makePlayer, run } from './playerTestUtils.js';

const DEG = Math.PI / 180;
const FULL = Object.freeze({ bob: 1, tilt: 1, dip: 1 });
const BOB = Object.freeze({ bob: 1, tilt: 0, dip: 0 });
const ground = () => worldOf((b) => floor(b));

/** Joga `ticks` ticks do jogador `p` com a sensação `f`; `drive(cmd, i)` monta o comando. Amostras por tick. */
function play(p, f, ticks, drive, scales = FULL) {
  const out = [];
  for (let i = 0; i < ticks; i++) {
    const events = run(p, 1, (c) => drive(c, i));
    updateCameraFeel(f, p.state, events, p.cmd.yaw, scales, DT);
    out.push({ i, y: f.y, side: f.side, roll: f.roll, weight: f.weight, events: events.map((e) => ({ ...e })) });
  }
  return out;
}

/** Estado parado no chão (sem o playerMove): para alimentar eventos soltos. */
function still() {
  const s = createMoveState();
  s.onGround = true;
  return s;
}

/** Aplica um evento no tick 0 e anda `ticks` ticks parado; devolve as saídas por tick. */
function afterEvent(event, ticks, scales = FULL, yaw = 0) {
  const f = createCameraFeel();
  const s = still();
  const out = [];
  for (let i = 0; i < ticks; i++) {
    updateCameraFeel(f, s, i === 0 ? [event] : [], yaw, scales, DT);
    out.push({ y: f.y, roll: f.roll });
  }
  return out;
}

test('dados: o nível Médio é o padrão; os valores de 100% vêm da referência na escala do CS', () => {
  assert.deepEqual(CAMERA_FEEL_DEFAULT, CAMERA_FEEL_LEVELS.medio);
  assert.deepEqual({ ...CAMERA_FEEL_LEVELS.medio }, { bob: 60, tilt: 70, dip: 65 });
  assert.ok(Math.abs(0.03 * 1.4 * 40 - CAMERA_FEEL.bob.vertical) < 0.05);
  assert.ok(Math.abs(0.018 * 1.4 * 40 - CAMERA_FEEL.bob.lateral) < 0.01);
  assert.ok(Math.abs(0.0056 / DEG - CAMERA_FEEL.bob.rollDeg) < 0.01);
  assert.ok(Math.abs(0.022 / DEG - CAMERA_FEEL.tilt.strafeDeg) < 0.05);
  assert.ok(Math.abs(0.08 / DEG - CAMERA_FEEL.tilt.slideDeg) < 0.05);
  assert.ok(Math.abs(0.1 / DEG - CAMERA_FEEL.kick.peakDeg) < 0.05);
  assert.ok(Math.abs(FEEL_SPRINGS.dipPeakTime - 0.09) < 0.002, `pico do mergulho em ${FEEL_SPRINGS.dipPeakTime}`);
  assert.ok(Math.abs(FEEL_SPRINGS.dipOvershoot - 0.11) < 0.005, `passa ${FEEL_SPRINGS.dipOvershoot} na volta`);
  assert.ok(Math.abs(FEEL_SPRINGS.kickPeakTime - 0.0767) < 0.001);
});

test('fator da queda: nada abaixo de 150 u/s, 0,368 no pouso do pulo, 1 no limite seguro e 1,4 no fatal', () => {
  assert.equal(landFactor(149), 0);
  assert.ok(Math.abs(landFactor(301.993377) - 0.3684) < 1e-3);
  assert.equal(landFactor(FALL.safeSpeed), 1);
  assert.ok(Math.abs(landFactor(FALL.fatalSpeed) - 1.4) < 1e-12);
  assert.ok(Math.abs(landFactor(5000) - 1.4) < 1e-12, 'acima do fatal não cresce');
  const mid = landFactor((FALL.safeSpeed + FALL.fatalSpeed) / 2);
  assert.ok(Math.abs(mid - 1.2) < 1e-12);
});

test('balanço: o ponto mais baixo no tick do passo, o mais alto no meio da passada e média zero numa passada', () => {
  const p = makePlayer(ground(), [0, 0, 0]);
  const f = createCameraFeel();
  const out = play(p, f, 64 * 3, (c) => forward(c), BOB);
  const steps = out.filter((o) => o.events.some((e) => e.type === 'step') && o.i > 64);
  assert.ok(steps.length >= 4, `passos: ${steps.length}`);
  const [a, b] = steps;
  const stride = out.slice(a.i, b.i);
  assert.equal(stride.length, 19, 'faca: um passo a cada 19 ticks');
  const w = a.weight;
  assert.ok(w > 0.99, `peso na corrida (250 u/s): ${w}`);
  const low = Math.min(...stride.map((o) => o.y));
  assert.equal(a.y, low, 'o mais baixo é o tick do passo');
  assert.ok(Math.abs(a.y + CAMERA_FEEL.bob.vertical * (2 / Math.PI) * w) < 1e-9);
  const high = Math.max(...stride.map((o) => o.y));
  assert.ok(Math.abs(high - CAMERA_FEEL.bob.vertical * (1 - 2 / Math.PI)) < 0.02, `mais alto: ${high}`);
  const mean = stride.reduce((m, o) => m + o.y, 0) / stride.length;
  assert.ok(Math.abs(mean) < 0.06, `média numa passada ${mean}`);
});

test('balanço: lateral e rolagem para o lado do pé do último passo', () => {
  const p = makePlayer(ground(), [0, 0, 0]);
  const f = createCameraFeel();
  const out = play(p, f, 64 * 3, (c) => forward(c), BOB);
  const steps = out.filter((o) => o.i > 64 && o.events.some((e) => e.type === 'step'));
  for (let k = 0; k + 1 < steps.length; k++) {
    const foot = steps[k].events.find((e) => e.type === 'step').foot;
    const mid = out[steps[k].i + 9];
    const sign = foot === 0 ? -1 : 1; // esquerdo: para a esquerda (lateral negativo) e cabeça para a esquerda (+)
    assert.ok(Math.sign(mid.side) === sign, `pé ${foot}: lateral ${mid.side}`);
    assert.ok(Math.sign(mid.roll) === -sign, `pé ${foot}: rolagem ${mid.roll}`);
    assert.ok(Math.abs(Math.abs(mid.side) - CAMERA_FEEL.bob.lateral) < 0.02, `lateral ${mid.side}`);
    assert.ok(Math.abs(Math.abs(mid.roll) - CAMERA_FEEL.bob.rollDeg * DEG) < 0.02 * DEG);
  }
});

test('peso do balanço: zero parado, no ar e no slide; segue a velocidade (andar a 130 u/s dá 0,52)', () => {
  const idleOut = play(makePlayer(ground(), [0, 0, 0]), createCameraFeel(), 64, (c) => { c.forward = 0; c.buttons = 0; }, BOB);
  assert.ok(idleOut.every((o) => o.weight === 0 && o.y === 0 && o.side === 0));
  const walk = play(makePlayer(ground(), [0, 0, 0]), createCameraFeel(), 64 * 2, (c) => {
    forward(c);
    c.buttons = BTN.WALK;
  }, BOB);
  assert.ok(Math.abs(walk.at(-1).weight - 130 / 250) < 0.01, `andando: ${walk.at(-1).weight}`);
  // Correndo e pulando: no ar o peso cai para zero.
  const p = makePlayer(ground(), [0, 0, 0]);
  const f = createCameraFeel();
  play(p, f, 64, (c) => forward(c), BOB);
  const air = play(p, f, 30, (c, i) => {
    forward(c);
    c.buttons = i === 0 ? BTN.JUMP : 0;
  }, BOB);
  assert.ok(air.at(-1).weight < 0.05, `no ar: ${air.at(-1).weight}`);
  // Slide: o peso cai para zero enquanto desliza.
  const q = makePlayer(ground(), [0, 0, 0]);
  const g = createCameraFeel();
  play(q, g, 64, (c) => forward(c), BOB);
  const slide = play(q, g, 30, (c) => {
    forward(c);
    c.buttons = BTN.DUCK;
  }, BOB);
  assert.ok(slide.some((o) => o.events.some((e) => e.type === 'slide' && e.phase === 'start')));
  assert.ok(slide[25].weight < 0.05, `no slide: ${slide[25].weight}`);
});

test('inclinação: a cabeça pende para o lado do movimento (1,3° a 250 u/s) e o sinal segue o lado', () => {
  const right = play(makePlayer(ground(), [0, 0, 0]), createCameraFeel(), 64 * 2, (c) => {
    c.forward = 0;
    c.side = 1;
    c.buttons = 0;
  }, { bob: 0, tilt: 1, dip: 0 });
  assert.ok(Math.abs(right.at(-1).roll + CAMERA_FEEL.tilt.strafeDeg * DEG) < 0.02 * DEG, `direita: ${right.at(-1).roll / DEG}°`);
  const left = play(makePlayer(ground(), [0, 0, 0]), createCameraFeel(), 64 * 2, (c) => {
    c.forward = 0;
    c.side = -1;
    c.buttons = 0;
  }, { bob: 0, tilt: 0.7, dip: 0 });
  assert.ok(Math.abs(left.at(-1).roll - 0.7 * CAMERA_FEEL.tilt.strafeDeg * DEG) < 0.02 * DEG, `esquerda (70%): ${left.at(-1).roll / DEG}°`);
  // Correndo para a frente: sem inclinação de lado.
  const fwd = play(makePlayer(ground(), [0, 0, 0]), createCameraFeel(), 64, (c) => forward(c), { bob: 0, tilt: 1, dip: 0 });
  assert.ok(Math.abs(fwd.at(-1).roll) < 1e-9);
});

test('slide: a cabeça pende para a direita (4,6°) enquanto desliza e volta depois', () => {
  const p = makePlayer(ground(), [0, 0, 0]);
  const f = createCameraFeel();
  play(p, f, 64, (c) => forward(c), { bob: 0, tilt: 1, dip: 0 });
  const out = play(p, f, 90, (c, i) => {
    forward(c);
    c.buttons = i < 38 ? BTN.DUCK : 0;
  }, { bob: 0, tilt: 1, dip: 0 });
  const minRoll = Math.min(...out.map((o) => o.roll));
  assert.ok(minRoll < -3.9 * DEG && minRoll > -4.61 * DEG, `no slide: ${minRoll / DEG}°`);
  assert.ok(Math.abs(out.at(-1).roll) < 0.4 * DEG, `depois: ${out.at(-1).roll / DEG}°`);
});

test('wall-jump: chute de 5,7° em ~77 ms para longe da parede (parede à direita → cabeça para a esquerda)', () => {
  // Olhando para −Z (yaw 0) o eixo direito é +X: parede à direita tem a normal −X (para o jogador).
  const out = afterEvent({ type: 'walljump', nx: -1, nz: 0 }, 40, { bob: 0, tilt: 1, dip: 0 });
  const peak = Math.max(...out.map((o) => o.roll));
  const at = out.findIndex((o) => o.roll === peak) + 1;
  assert.ok(Math.abs(peak - CAMERA_FEEL.kick.peakDeg * DEG) < 0.03 * DEG, `pico ${peak / DEG}°`);
  assert.equal(at, 5, 'no 5º tick (78 ms)');
  const fade = out[Math.round(0.4 * 64) - 1].roll / peak;
  assert.ok(fade > 0.05 && fade < 0.1, `~8% em 0,4 s: ${fade}`);
  const mirrored = afterEvent({ type: 'walljump', nx: 1, nz: 0 }, 10, { bob: 0, tilt: 1, dip: 0 });
  assert.ok(Math.abs(Math.min(...mirrored.map((o) => o.roll)) + peak) < 1e-12, 'parede à esquerda: o espelho');
  const ahead = afterEvent({ type: 'walljump', nx: 0, nz: 1 }, 10, { bob: 0, tilt: 1, dip: 0 });
  assert.ok(ahead.every((o) => Math.abs(o.roll) < 1e-12), 'parede à frente: sem chute de lado');
});

test('mergulho: pico de 4,4 u no pouso do pulo e de 12 u na queda de 420 u a 100%; 2,9 u e 7,8 u no Médio', () => {
  const dipOf = (speed, k) => -Math.min(...afterEvent({ type: 'land', speed }, 40, { bob: 0, tilt: 0, dip: k }).map((o) => o.y));
  assert.ok(Math.abs(dipOf(301.993377, 1) - 4.42) < 0.03, `pulo ${dipOf(301.993377, 1)}`);
  assert.ok(Math.abs(dipOf(FALL.safeSpeed, 1) - 12) < 0.05, `420 u ${dipOf(FALL.safeSpeed, 1)}`);
  assert.ok(Math.abs(dipOf(FALL.fatalSpeed, 1) - 16.8) < 0.07, `fatal ${dipOf(FALL.fatalSpeed, 1)}`);
  assert.ok(Math.abs(dipOf(301.993377, 0.65) - 2.87) < 0.03, `Médio, pulo ${dipOf(301.993377, 0.65)}`);
  assert.ok(Math.abs(dipOf(FALL.safeSpeed, 0.65) - 7.8) < 0.04, `Médio, 420 u ${dipOf(FALL.safeSpeed, 0.65)}`);
  assert.ok(dipOf(140, 1) === 0, 'pouso lento não mergulha');
  const land = afterEvent({ type: 'land', speed: FALL.safeSpeed }, 64);
  const low = Math.min(...land.map((o) => o.y));
  assert.equal(land.findIndex((o) => o.y === low) + 1, 6, 'pico em ~90 ms (6º tick)');
  const over = Math.max(...land.map((o) => o.y));
  assert.ok(over > 0.1 * 12 && over < 0.12 * 12, `passa ~11% na volta: ${over}`);
  // Pulo, começo do slide e wall-jump: 12%, 15% e 12% do máximo.
  const peakOf = (e) => -Math.min(...afterEvent(e, 20, { bob: 0, tilt: 0, dip: 1 }).map((o) => o.y));
  assert.ok(Math.abs(peakOf({ type: 'jump' }) - 1.44) < 0.02);
  assert.ok(Math.abs(peakOf({ type: 'slide', phase: 'start' }) - 1.8) < 0.02);
  assert.ok(peakOf({ type: 'slide', phase: 'end' }) === 0, 'o fim do slide não mergulha');
  assert.ok(Math.abs(peakOf({ type: 'walljump', nx: 0, nz: 1 }) - 1.44) < 0.02);
});

test('escalas: zero em tudo não mexe a câmera; cada controle só mexe o seu efeito', () => {
  const zero = { bob: 0, tilt: 0, dip: 0 };
  const p = makePlayer(ground(), [0, 0, 0]);
  const f = createCameraFeel();
  const out = play(p, f, 64 * 3, (c, i) => {
    c.forward = 1;
    c.side = i % 60 < 30 ? 1 : -1;
    c.buttons = i % 50 === 0 ? BTN.JUMP : 0;
  }, zero);
  assert.ok(out.every((o) => o.y === 0 && o.side === 0 && o.roll === 0));
  const onlyDip = afterEvent({ type: 'walljump', nx: -1, nz: 0 }, 20, { bob: 0, tilt: 0, dip: 1 });
  assert.ok(onlyDip.every((o) => o.roll === 0) && onlyDip.some((o) => o.y < 0));
  const onlyTilt = afterEvent({ type: 'land', speed: FALL.safeSpeed }, 20, { bob: 0, tilt: 1, dip: 0 });
  assert.ok(onlyTilt.every((o) => o.y === 0));
});

test('molas exatas: dois ticks de 1/64 s dão o mesmo que um de 1/32 s; reset zera tudo', () => {
  const s = still();
  const a = createCameraFeel();
  const b = createCameraFeel();
  const events = [{ type: 'land', speed: 900 }, { type: 'walljump', nx: -0.6, nz: 0.8 }];
  updateCameraFeel(a, s, events, 0.3, FULL, 0);
  updateCameraFeel(b, s, events, 0.3, FULL, 0);
  for (let i = 0; i < 20; i++) {
    updateCameraFeel(a, s, [], 0.3, FULL, DT);
    updateCameraFeel(a, s, [], 0.3, FULL, DT);
    updateCameraFeel(b, s, [], 0.3, FULL, 2 * DT);
  }
  for (const k of ['dip', 'dipV', 'kick', 'kickV', 'y', 'roll', 'tilt', 'weight']) {
    assert.ok(Math.abs(a[k] - b[k]) < 1e-9, `${k}: ${a[k]} × ${b[k]}`);
  }
  resetCameraFeel(a);
  assert.deepEqual(a, createCameraFeel());
  // A velocidade do tick só entra pela velocidade do estado: o mesmo estado em yaw oposto espelha a inclinação.
  const t1 = createCameraFeel();
  const t2 = createCameraFeel();
  const moving = still();
  moving.velocity.copy(new THREE.Vector3(200, 0, 0));
  updateCameraFeel(t1, moving, [], 0, { bob: 0, tilt: 1, dip: 0 }, DT);
  updateCameraFeel(t2, moving, [], Math.PI, { bob: 0, tilt: 1, dip: 0 }, DT);
  assert.ok(Math.abs(t1.roll + t2.roll) < 1e-12 && t1.roll < 0);
});
