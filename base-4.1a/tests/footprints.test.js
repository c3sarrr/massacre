// Testes das pegadas (subfase 3.5): a forma da marca (contorno da sola com o bico cortado e o lado de dentro, cravos,
// lábio que não passa do fundo, brilho); a posição e o rumo dos pés (passo, par do pouso, pulo, sulcos e montinho do
// slide) e o referencial de uma placa girada; a escolha da placa (a que a marca encosta e está na altura dos pés;
// nenhuma fora da massinha); a fila na ordem do jogo e a pausa; o esmaecimento em inteiros de 8 bits (o pouso em 255
// poses, o passo em 191) e a passada única por peça igual a aplicar a fila item a item; o tamanho dos alvos e o teto de
// 1024; e o sistema (uma chamada de render por peça com marca nova ou viva, limpeza, GPU reiniciada, liberação).
import { test } from 'node:test';
import assert from 'node:assert/strict';
import * as THREE from 'three';
import { EV, EventBus } from '../src/core/events.js';
import { FOOTPRINTS, SOLE } from '../src/data/footprints.js';
import { ClayMaterial } from '../src/clay/ClayMaterial.js';
import {
  MARK, createPrintTrack, fadeTexel, footMark, footPair, grooveMarks, markLife, markTexel, moundMark, tickMarks,
} from '../src/clay/prints/marks.js';
import { PrintQueue, createPlan, surfaceLife } from '../src/clay/prints/printQueue.js';
import { PrintSurface, placeMark, surfaceSize } from '../src/clay/prints/surface.js';
import { PrintSystem } from '../src/clay/prints/printSystem.js';
import { createMoveState, MOVETYPE } from '../src/player/movement.js';

const M = FOOTPRINTS.marks;
const DEG = Math.PI / 180;
const DT = 1 / 64;

/** Placa de massinha da pista: 180 × 5 × 130, em pé sobre o kraft (0,3 u) em (x, z), girada `heading` graus. */
function plate(x, z, heading, id = 'placa') {
  const mesh = new THREE.Mesh(new THREE.BoxGeometry(180, 5, 130), new ClayMaterial({ seed: id }));
  mesh.matrixAutoUpdate = false;
  mesh.matrix.makeRotationY(-heading * DEG).setPosition(x, 0.3 + 2.5, z);
  return { id, mesh, material: mesh.material, width: 180, depth: 130, top: 2.5 };
}

/** Superfície pura (sem alvo) para a escolha da placa. */
function frame(decl) {
  decl.mesh.updateWorldMatrix(true, false, true);
  return { ...decl, inverse: decl.mesh.matrixWorld.clone().invert().elements.slice() };
}

/** Valor do texel da marca no ponto do referencial do pé (a ao longo, bi para dentro). */
function soleTexel(m, a, bi, fades = 0) {
  const rx = -m.dz;
  const rz = m.dx;
  const b = bi * m.inner;
  return markTexel(m, m.x + m.dx * a + rx * b, m.z + m.dz * a + rz * b, fades);
}

test('forma da marca: contorno da sola (16,4 u com o bico cortado em 7,6), lado de dentro, cravos, lábio e brilho', () => {
  const m = footMark(0, 0, 0, 0, 0, M.land);
  const depth = (a, bi) => soleTexel(m, a, bi)[0];
  // Comprimento: do calcanhar (−8,2) ao corte do bico (+7,6); largura no bico ±3,9 (desviado para dentro).
  assert.ok(depth(-7.5, 0) > 0 && depth(-8.4, 0) === 0, 'calcanhar');
  assert.ok(depth(7.4, 0) > 0 && depth(7.7, 0) === 0, 'bico cortado reto');
  assert.ok(depth(4.3, 3.8) > 0 && depth(4.3, -3.8) === 0, 'o bico desvia para o lado de dentro');
  // Cravos (longe da parede): barra 1, vão da frente 0,74, arco 0,58, vão do calcanhar 0,78.
  assert.equal(depth(2.0, 0), 255, 'barra da frente (de 1,6 a 2,59)');
  assert.equal(depth(1.2, 0), Math.round(SOLE.cleats.front.gap * 255), 'vão da frente (de 0,79 a 1,6)');
  assert.equal(depth(-1.8, 0), Math.round(SOLE.cleats.arch * 255), 'arco liso');
  assert.equal(depth(-5, 1.2), 255, 'barra do calcanhar (de 0,8 a 1,6)');
  assert.equal(depth(-5, 0.4), Math.round(SOLE.cleats.heel.gap * 255), 'vão do calcanhar (de 0 a 0,8)');
  // Lábio fora da borda (0 dentro), mais alto na frente, nunca acima do fundo máximo; brilho até 2,4 u da borda.
  const lip = (a, bi) => soleTexel(m, a, bi)[1];
  assert.equal(lip(0, 0), 0);
  const side = Math.max(...[3.6, 3.9, 4.2, 4.5, 4.8].map((b) => lip(-2, b)));
  const front = Math.max(...[8.2, 8.5, 8.8, 9.1].map((a) => lip(a, 0.3)));
  assert.ok(side > 150 && front === 255 && front > side, `lábio: lado ${side}, frente ${front}`);
  const step = footMark(0, 0, 0, 0, 0, M.step);
  const stepFront = Math.max(...[8.2, 8.5, 8.8, 9.1].map((a) => soleTexel(step, a, 0.3)[1]));
  assert.equal(stepFront, 191, 'o lábio do passo para no fundo dele (0,75)');
  assert.equal(soleTexel(m, 9.9, 0.3)[2], 255, 'brilho a 2,3 u do bico');
  assert.equal(soleTexel(m, 10.1, 0.3)[2], 0, 'sem brilho a 2,5 u');
});

test('pés: passo a ±5,6 u com o bico 6° para fora; pares do pouso e do pulo; sulcos e montinho do slide', () => {
  // Olhando para −Z (yaw 0): a direita do olhar é +X.
  const left = footMark(100, 5, 200, 0, 0, M.step);
  const right = footMark(100, 5, 200, 0, 1, M.step);
  assert.ok(Math.abs(left.x - 94.4) < 1e-9 && Math.abs(right.x - 105.6) < 1e-9 && left.z === 200 && left.y === 5);
  assert.ok(Math.abs(Math.atan2(-left.dx, -left.dz) - 6 * DEG) < 1e-9, 'esquerdo gira para a esquerda');
  assert.ok(Math.abs(Math.atan2(-right.dx, -right.dz) + 6 * DEG) < 1e-9, 'direito gira para a direita');
  assert.equal(left.inner, 1);
  assert.equal(right.inner, -1);
  // Andando de lado o pé continua de frente para o olhar: o rumo sai do yaw, não da velocidade.
  const turned = footMark(0, 0, 0, 90 * DEG, 1, M.step);
  assert.ok(Math.abs(Math.atan2(-turned.dx, -turned.dz) - 84 * DEG) < 1e-9);
  const [l, r] = footPair(0, 0, 0, 0, M.land);
  assert.ok(Math.abs(l.x + 6.2) < 1e-9 && Math.abs(r.x - 6.2) < 1e-9 && l.strength === 1);
  assert.ok(Math.abs(Math.atan2(-l.dx, -l.dz) - 8 * DEG) < 1e-9);
  // Pulo: nas barras, a frente 30% mais funda (satura em 1) e o calcanhar pela metade (o impulso).
  const [jl] = footPair(0, 0, 0, 0, M.jump);
  assert.equal(soleTexel(jl, 5.5, 0)[0], 255, 'frente funda');
  assert.equal(soleTexel(jl, -5, 1.2)[0], Math.round(M.jump.strength * M.jump.heel * 255), 'calcanhar raso');
  // Slide: dois sulcos a ±5,6 u da trajetória, com o comprimento do deslocamento.
  const grooves = grooveMarks(0, 0, 0, -10, 0);
  assert.equal(grooves.length, 2);
  assert.deepEqual(grooves.map((g) => g.x).sort((a, b) => a - b), [-5.6, 5.6]);
  assert.ok(grooves.every((g) => g.kind === MARK.GROOVE && g.length === 10 && g.dz === -1));
  assert.equal(markTexel(grooves[0], grooves[0].x, -5)[0], 128, 'fundo do sulco (0,5)');
  assert.deepEqual(grooveMarks(1, 1, 1, 1, 0), [], 'sem deslocamento, nada');
  const mound = moundMark(0, 0, 0, 0, -1);
  assert.equal(mound.z, -M.slide.moundAhead);
  assert.deepEqual(markTexel(mound, 0, -8), [0, 128, 255], 'montinho: só lábio, da força dos sulcos');
});

test('referencial de uma placa girada: posição (com o y dos pés) e rumo no XZ do objeto', () => {
  const p = frame(plate(600, 1580, 4));
  const yaw = 30 * DEG;
  const m = footMark(610, 5.3, 1560, yaw, 0, M.step);
  const local = placeMark(p, m);
  assert.ok(local, 'cai na placa');
  const want = new THREE.Vector3(m.x, m.y, m.z).applyMatrix4(p.mesh.matrixWorld.clone().invert());
  assert.ok(Math.abs(local.x - want.x) < 1e-9 && Math.abs(local.z - want.z) < 1e-9);
  assert.ok(Math.abs(local.y - 2.5) < 1e-9, 'os pés no topo da placa');
  // O rumo gira junto: o yaw do pé no objeto = o do mundo + o giro da placa.
  const worldYaw = Math.atan2(-m.dx, -m.dz);
  assert.ok(Math.abs(Math.atan2(-local.dx, -local.dz) - (worldYaw + 4 * DEG)) < 1e-9);
  assert.ok(Math.abs(Math.hypot(local.dx, local.dz) - 1) < 1e-12);
  assert.equal(local.inner, m.inner, 'o resto da marca vem junto');
});

test('escolha da placa: a que a marca encosta e está na altura dos pés; nenhuma fora da massinha', () => {
  const a = frame(plate(600, 1580, 3, 'P'));
  const b = frame(plate(400, 1580, -2, 'E'));
  const on = (x, z, y = 5.3) => [a, b].filter((p) => placeMark(p, footMark(x, y, z, 0, 1, M.step))).map((p) => p.id);
  assert.deepEqual(on(600, 1580), ['P'], 'no meio da placa');
  assert.deepEqual(on(400, 1600), ['E']);
  assert.deepEqual(on(600 + 90 - 5.6 + 8, 1580), ['P'], 'passando da borda: cortada, mas na placa');
  assert.deepEqual(on(600, 1580, 0.3), [], 'no kraft (5 u abaixo do topo): fora da massinha');
  assert.deepEqual(on(0, 1580), [], 'longe de qualquer placa');
  assert.deepEqual(on(600, 1580 + 65 + 20), [], 'além da borda com folga');
  // O limite da altura: 4 u.
  assert.deepEqual(on(600, 1580, 5.3 + 3.9), ['P']);
  assert.deepEqual(on(600, 1580, 5.3 + 4.1), []);
});

test('marcas do tick: passo onde o pé estava, pouso acima de 150 u/s, pulo de onde saiu, sulcos e montinho', () => {
  const t = createPrintTrack();
  const s = createMoveState({ position: new THREE.Vector3(10, 0, 0) });
  s.onGround = true;
  const from = new THREE.Vector3(10, 0, 4);
  const out = [];
  tickMarks(t, s, from, [{ type: 'step', foot: 1, x: 3, y: 0, z: 7 }], 0, out);
  assert.equal(out.length, 1);
  assert.ok(Math.abs(out[0].x - (3 + M.step.offset)) < 1e-9 && out[0].z === 7, 'o pé do evento');
  tickMarks(t, s, from, [{ type: 'land', speed: 100 }], 0, out);
  assert.equal(out.length, 0, 'pouso lento não marca');
  tickMarks(t, s, from, [{ type: 'land', speed: 420 }], 0, out);
  assert.equal(out.length, 2);
  assert.ok(out.every((m) => m.strength === M.land.strength && m.z === 0), 'o par onde parou');
  tickMarks(t, s, from, [{ type: 'jump' }], 0, out);
  assert.ok(out.length === 2 && out.every((m) => m.z === 4 && m.front === M.jump.front), 'o par de onde saiu');
  tickMarks(t, s, from, [{ type: 'walljump', nx: 1, nz: 0 }], 0, out);
  assert.equal(out.length, 0, 'wall-jump não marca o chão');
  // Slide no chão: dois sulcos por tick; o fim depois de um tick no chão deixa o montinho à frente.
  s.sliding = true;
  s.origin.set(10, 0, -6);
  tickMarks(t, s, new THREE.Vector3(10, 0, 0), [{ type: 'slide', phase: 'start' }], 0, out);
  assert.ok(out.length === 2 && out.every((m) => m.kind === MARK.GROOVE && m.length === 6));
  s.sliding = false;
  tickMarks(t, s, new THREE.Vector3(10, 0, -6), [{ type: 'slide', phase: 'end' }], 0, out);
  assert.equal(out.length, 1);
  assert.ok(out[0].kind === MARK.MOUND && out[0].x === 10 && out[0].z === -6 - M.slide.moundAhead);
  // Slide que sai do chão (e acaba no ar): sem montinho.
  s.sliding = true;
  s.onGround = false;
  tickMarks(t, s, new THREE.Vector3(10, 0, -6), [], 0, out);
  assert.equal(out.length, 0);
  s.sliding = false;
  tickMarks(t, s, new THREE.Vector3(10, 0, -6), [{ type: 'slide', phase: 'end' }], 0, out);
  assert.equal(out.length, 0);
});

test('fila na ordem do jogo: 12 passos do esmaecimento por segundo de tick; a pausa congela', () => {
  const q = new PrintQueue();
  const plan = createPlan(2);
  for (let i = 0; i < 64; i++) q.advance(DT);
  assert.equal(q.drain(plan).fades, 12, 'um segundo de tick, 12 passos (conta exata)');
  assert.equal(q.acc, 0);
  const a = { id: 'a' };
  const b = { id: 'b' };
  const c = { id: 'c' };
  q.push(0, a);
  for (let i = 0; i < 16; i++) q.advance(DT); // 3 passos
  q.push(1, b);
  q.push(0, c);
  for (let i = 0; i < 6; i++) q.advance(DT); // mais 1 (1,125)
  q.drain(plan);
  assert.equal(plan.fades, 4);
  assert.deepEqual(plan.stamps[0], [a, c], 'na ordem do jogo');
  assert.deepEqual(plan.stamps[1], [b]);
  assert.deepEqual([a.fades, b.fades, c.fades], [4, 1, 1], 'passos depois de cada marca');
  // Pausa: o MatchState não anda o tick; poses seguidas não esmaecem nada.
  q.push(0, { id: 'd' });
  assert.equal(q.drain(plan).fades, 0);
  assert.equal(q.drain(plan).stamps[0].length, 0, 'a fila esvaziou');
});

test('esmaecimento em 8 bits: o pouso some em 255 poses (21,25 s), o passo em 191, o sulco em 128, o brilho em 85', () => {
  const [land] = footPair(0, 0, 0, 0, M.land);
  const step = footMark(0, 0, 0, 0, 0, M.step);
  const [groove] = grooveMarks(0, 0, 0, -10, 0);
  assert.equal(markLife(land), 255);
  assert.equal(markLife(step), 191);
  assert.equal(markLife(groove), 128);
  assert.equal(markLife(moundMark(0, 0, 0, 0, -1)), 128);
  assert.equal(255 / FOOTPRINTS.fade.rate, 21.25);
  assert.equal(soleTexel(land, 2, 0, 254)[0], 1, 'a barra mais funda ainda está lá na pose 254');
  assert.equal(soleTexel(land, 2, 0, 255)[0], 0);
  assert.equal(soleTexel(step, 2, 0, 190)[0], 1);
  assert.equal(soleTexel(step, 2, 0, 191)[0], 0);
  assert.equal(soleTexel(land, 0, 0, 84)[2], 3);
  assert.equal(soleTexel(land, 0, 0, 85)[2], 0, 'brilho em 85 poses (7,1 s)');
  // Esmaecer o texel carimbado = carimbar já esmaecido (a GPU faz dos dois jeitos).
  for (const [a, bi] of [[2, 0], [8.6, 0.3], [-3, 4.1], [9.9, 0]]) {
    for (const k of [0, 3, 90, 200]) assert.deepEqual(soleTexel(land, a, bi, k), fadeTexel(soleTexel(land, a, bi), k));
  }
  // Toda marca some por inteiro na vida dela.
  for (const m of [land, step, groove]) {
    for (let x = -14; x <= 14; x += 0.5) {
      for (let z = -14; z <= 14; z += 0.5) {
        assert.deepEqual(markTexel(m, m.x + x, m.z + z, markLife(m)), [0, 0, 0]);
      }
    }
  }
});

test('uma passada por peça (esmaecer a pose, depois as marcas já esmaecidas) = aplicar a fila item a item', () => {
  const W = 48;
  const texel = (grid, m, fades) => {
    for (let j = 0; j < W; j++) {
      for (let i = 0; i < W; i++) {
        const v = markTexel(m, i - W / 2 + 0.5, j - W / 2 + 0.5, fades);
        for (let c = 0; c < 3; c++) grid[(j * W + i) * 3 + c] = Math.max(grid[(j * W + i) * 3 + c], v[c]);
      }
    }
  };
  const fade = (grid, n) => {
    for (let k = 0; k < grid.length; k++) grid[k] = Math.max(0, grid[k] - n * [1, 1, 3][k % 3]);
  };
  const marks = [
    ...footPair(0, 0, 4, 0.3, M.land), footMark(-3, 0, -6, 0.3, 0, M.step), ...grooveMarks(-10, 10, 8, -12, 0),
    moundMark(8, 0, -12, 0.6, -0.8),
  ];
  const q = new PrintQueue();
  const seq = new Uint8Array(W * W * 3);
  const old = new Uint8Array(W * W * 3);
  texel(seq, footMark(2, 0, 2, 1, 1, M.step), 0);
  texel(old, footMark(2, 0, 2, 1, 1, M.step), 0);
  marks.forEach((m, n) => {
    q.push(0, { ...m });
    texel(seq, m, 0);
    for (let k = 0; k < (n % 3) * 16 + 5; k++) {
      const before = q.size;
      q.advance(DT);
      if (q.size > before) fade(seq, q.size - before);
    }
  });
  const plan = q.drain(createPlan(1));
  assert.ok(plan.fades > 3);
  fade(old, plan.fades);
  for (const m of plan.stamps[0]) texel(old, m, m.fades);
  assert.deepEqual(old, seq);
  assert.equal(surfaceLife(0, plan.fades, plan.stamps[0]), Math.max(...plan.stamps[0].map((m) => markLife(m) - m.fades)));
  assert.equal(surfaceLife(100, 4, []), 96);
  assert.equal(surfaceLife(3, 4, []), 0);
});

test('alvos: 4 texels/u (720 × 520 na placa da pista), teto de 1024 por lado com a mesma densidade nos dois eixos', () => {
  assert.deepEqual(surfaceSize(180, 130), { width: 720, height: 520, texelsPerUnit: 4 });
  const wide = surfaceSize(300, 100);
  assert.equal(wide.width, 1024);
  assert.equal(wide.height, Math.round((100 * 1024) / 300));
  const huge = surfaceSize(4000, 4000);
  assert.deepEqual([huge.width, huge.height], [1024, 1024]);
  assert.equal(surfaceSize(2, 2).width, 8);
});

/** Renderer que só anota as chamadas (a GPU é conferida no navegador). */
function fakeRender() {
  const draws = [];
  const renderer = {
    autoClear: true,
    target: null,
    compiled: 0,
    compile() {
      this.compiled++;
    },
    getRenderTarget() {
      return this.target;
    },
    setRenderTarget(t) {
      this.target = t;
    },
    render(scene) {
      const [fadeMesh, stamps] = scene.children;
      draws.push({
        target: this.target, autoClear: this.autoClear, fade: fadeMesh.visible ? fadeMesh.material.uniforms.uFade.value.x * 255 : 0,
        stamps: stamps.visible ? stamps.geometry.instanceCount : 0,
      });
    },
  };
  return { contextLost: false, renderer, draws };
}

/** Jogador de mentira: estado de movimento, origem do começo do tick, eventos, olhar e vida. */
function fakePawn(x, y, z) {
  const state = createMoveState({ position: new THREE.Vector3(x, y, z) });
  state.onGround = true;
  return { state, prevOrigin: state.origin.clone(), env: { events: [] }, yaw: 0, vitals: { alive: true } };
}

test('sistema: uma chamada por peça com marca nova ou viva, esmaecimento no tempo do jogo, limpeza e liberação', () => {
  const render = fakeRender();
  const events = new EventBus();
  const decls = [plate(600, 1580, 3, 'P'), plate(400, 1580, -2, 'E')];
  const sys = new PrintSystem({ render, events, surfaces: decls });
  assert.equal(render.renderer.compiled, 1, 'programas compilados na montagem');
  assert.equal(render.draws.length, 2, 'montagem: cada mapa zerado (e os mipmaps)');
  assert.ok(render.draws.every((d) => d.fade === 255 && d.stamps === 0 && d.autoClear === false));
  assert.equal(render.renderer.autoClear, true, 'o autoClear volta');
  assert.ok(decls.every((d) => d.material.clayPrints && d.material.clayUniforms.uClayPrints.value.isRenderTargetTexture));
  render.draws.length = 0;
  const pawn = fakePawn(600, 5.3, 1580);
  pawn.env.events = [{ type: 'land', speed: 420 }];
  sys.tick(pawn, DT);
  pawn.env.events = [];
  for (let i = 0; i < 5; i++) sys.tick(pawn, DT);
  sys.onPose();
  assert.equal(render.draws.length, 1, 'só a placa P desenha');
  assert.equal(render.draws[0].target, sys.surfaces[0].target);
  assert.deepEqual([render.draws[0].fade, render.draws[0].stamps], [0, 2], 'mapa limpo: sem esmaecer; o par do pouso');
  assert.equal(sys.surfaces[0].life, 255 - 1, 'um passo do esmaecimento veio depois do pouso');
  // Poses sem marca nova: a placa viva só esmaece; a limpa não desenha.
  render.draws.length = 0;
  for (let i = 0; i < 6; i++) sys.tick(pawn, DT);
  sys.onPose();
  assert.equal(render.draws.length, 1);
  assert.deepEqual([render.draws[0].fade, render.draws[0].stamps], [1, 0]);
  // Até sumir: depois, nenhuma chamada.
  for (let i = 0; i < 64 * 22; i++) sys.tick(pawn, DT);
  sys.onPose();
  assert.equal(sys.surfaces[0].life, 0);
  render.draws.length = 0;
  for (let i = 0; i < 16; i++) sys.tick(pawn, DT);
  sys.onPose();
  assert.equal(render.draws.length, 0, 'placa sem marca viva não recebe desenho');
  // Morto ou no noclip: nada marca.
  pawn.env.events = [{ type: 'step', foot: 0, x: 600, y: 5.3, z: 1580 }];
  pawn.vitals.alive = false;
  sys.tick(pawn, DT);
  pawn.vitals.alive = true;
  pawn.state.moveType = MOVETYPE.NOCLIP;
  sys.tick(pawn, DT);
  assert.equal(sys.queue.items.filter((it) => it.mark).length, 0);
  pawn.state.moveType = MOVETYPE.WALK;
  sys.tick(pawn, DT);
  assert.equal(sys.info().queue > 0, true);
  assert.equal(sys.info().surfaces, 2);
  // Limpar: a fila sai e os dois mapas zeram; GPU reiniciada faz o mesmo; perdida, nada desenha.
  render.draws.length = 0;
  sys.clear();
  assert.equal(sys.queue.size, 0);
  assert.equal(render.draws.length, 2);
  render.contextLost = true;
  sys.tick(pawn, DT);
  sys.onPose();
  assert.equal(render.draws.length, 2, 'contexto perdido: sem desenho');
  render.contextLost = false;
  events.emit(EV.RENDER_CONTEXT, { lost: false });
  assert.equal(render.draws.length, 4, 'recuperado: mapas zerados de novo');
  let disposed = 0;
  for (const s of sys.surfaces) s.target.addEventListener('dispose', () => disposed++);
  sys.dispose();
  assert.equal(disposed, 2, 'alvos liberados');
  assert.ok(decls.every((d) => !d.material.clayPrints), 'materiais sem o mapa');
  events.emit(EV.RENDER_CONTEXT, { lost: false });
  assert.equal(render.draws.length, 4, 'depois de liberado não ouve mais a GPU');
});

test('superfície: o mapa cobre a peça inteira (centrada) no ClayMaterial, com a chave do programa', () => {
  const decl = plate(0, 0, 0, 'S');
  const key = decl.material.customProgramCacheKey();
  const s = new PrintSurface(decl);
  assert.deepEqual([s.target.width, s.target.height], [720, 520]);
  assert.equal(s.target.texture.generateMipmaps, true);
  assert.equal(s.target.depthBuffer, false);
  const u = decl.material.clayUniforms;
  assert.deepEqual(u.uClayPrintsRect.value.toArray(), [-90, -65, 180, 130]);
  assert.deepEqual(u.uClayPrintsDepth.value.toArray(), [FOOTPRINTS.depth, FOOTPRINTS.lip]);
  assert.notEqual(decl.material.customProgramCacheKey(), key, 'a camada entra na chave do programa');
  s.dispose();
  assert.equal(decl.material.customProgramCacheKey(), key);
});
