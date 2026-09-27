// Testes do monitor do movimento (subfase 3.5, aceite da Fase 3): a checagem por tick (penetração com a profundidade,
// preso, abaixo do chão do estúdio; nada no noclip), os problemas guardados com o tick e o lugar, o tempo por estação
// (o lote sob os pés), a estatística de FPS (média, 1% low e a janela do painel), a memória (primeira, última, mínimo e
// máximo) e o relatório em texto.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import * as THREE from 'three';
import { HULL } from '../src/data/movement.js';
import { MONITOR } from '../src/data/sandbox.js';
import { MonitorLog, formatMonitorReport, memorySample } from '../src/debug/moveMonitor.js';
import { createMoveState, MOVETYPE } from '../src/player/movement.js';
import { floor, worldOf } from './worldTestUtils.js';

const DT = 1 / 64;
const world = worldOf((b) => floor(b));
const LOTS = [
  { number: 1, label: 'Counter-strafe', x: [0, 400], z: [0, 400] },
  { number: 2, label: 'Escadas', x: [500, 900], z: [0, 400] },
];

function at(x, y, z) {
  const s = createMoveState({ position: new THREE.Vector3(x, y, z) });
  s.onGround = true;
  return s;
}

test('checagem por tick: cabe no chão; penetração com a profundidade; preso; abaixo do chão; nada no noclip', () => {
  const log = new MonitorLog({ world, floorY: -100, lots: LOTS }); // o chão do estúdio bem abaixo do tapete
  for (let i = 0; i < 64; i++) log.tick(at(100, 0, 100), DT);
  assert.ok(log.ok && log.checked === 64 && log.penetrations === 0);
  log.tick(at(100, -3, 100), DT);
  assert.equal(log.penetrations, 1);
  assert.ok(Math.abs(log.maxDepth - 3) < 1e-6, `3 u dentro do chão: ${log.maxDepth}`);
  // Encostado no chão (dentro da folga de 0,05 u): não conta.
  log.tick(at(100, -MONITOR.tolerance / 2, 100), DT);
  assert.equal(log.penetrations, 1);
  const stuck = at(100, 0, 100);
  stuck.stuck = true;
  log.tick(stuck, DT);
  assert.equal(log.stuck, 1);
  // Abaixo do chão do estúdio (o fundo do mapa): no ar, sem penetrar nada.
  const low = new MonitorLog({ world, floorY: 200 });
  low.tick(at(100, 150, 100), DT);
  assert.equal(low.below, 1);
  assert.equal(low.penetrations, 0);
  // Noclip atravessa tudo de propósito: não confere (mas o tempo e o lote contam).
  const ghost = at(100, -40, 100);
  ghost.moveType = MOVETYPE.NOCLIP;
  const before = log.checked;
  log.tick(ghost, DT);
  assert.equal(log.checked, before);
  assert.equal(log.penetrations, 1);
  assert.equal(log.ok, false);
  assert.deepEqual(log.problems.map((p) => p.kind), ['penetração', 'preso']);
  assert.equal(log.problems[0].tick, 65);
  assert.deepEqual(log.problems[0].at, [100, -3, 100]);
  // Problemas guardados até o limite; a contagem continua.
  for (let i = 0; i < 40; i++) log.tick(at(100, -3, 100), DT);
  assert.equal(log.problems.length, MONITOR.keepProblems);
  assert.equal(log.penetrations, 41);
  log.reset();
  assert.ok(log.ok && log.ticks === 0 && log.problems.length === 0 && log.lotTime.size === 0);
});

test('tempo por estação: o lote sob os pés; fora deles, "fora dos lotes"', () => {
  const log = new MonitorLog({ world, floorY: 0, lots: LOTS });
  for (let i = 0; i < 128; i++) log.tick(at(200, 0, 200), DT);
  for (let i = 0; i < 64; i++) log.tick(at(700, 0, 100), DT);
  for (let i = 0; i < 32; i++) log.tick(at(-300, 0, 0), DT);
  assert.equal(log.lotAt(400, 400), 1, 'a borda conta');
  assert.equal(log.lotAt(450, 0), 0);
  const r = log.report();
  assert.deepEqual(r.lots.map((l) => [l.number, l.label, l.seconds]), [
    [1, 'Counter-strafe', 2], [2, 'Escadas', 1], [0, 'fora dos lotes', 0.5],
  ]);
  assert.ok(Math.abs(r.minutes - 3.5 / 60) < 1e-12);
});

test('FPS da sessão e da janela (média e 1% low) e memória (primeira, última, mínimo, máximo)', () => {
  const log = new MonitorLog({ world });
  for (let i = 0; i < 99; i++) log.frame(10);
  log.frame(50);
  log.frame(0); // quadro sem tempo não entra
  const all = log.fps();
  assert.equal(all.frames, 100);
  assert.ok(Math.abs(all.fps - 100000 / 1040) < 1e-9);
  assert.ok(Math.abs(all.low1Fps - 20) < 1e-9, '1% low = o quadro de 50 ms');
  assert.ok(Math.abs(log.sessionFps() - all.fps) < 1e-9, 'a média da sessão pela soma, sem ordenar');
  const recent = log.fps(0.055);
  assert.equal(recent.frames, 2, 'a janela junta quadros do fim até cobrir o tempo');
  log.sample({ geometries: 120, textures: 40, programs: 30, heapMB: 80 });
  log.tick(at(0, 0, 0), DT);
  log.sample({ geometries: 126, textures: 40, programs: 31, heapMB: 95 });
  log.sample({ geometries: 120, textures: 40, programs: 31, heapMB: 82 });
  const m = log.report().memory;
  assert.equal(m.samples, 3);
  assert.deepEqual(m.geometries, { first: 120, last: 120, min: 120, max: 126 });
  assert.deepEqual(m.heapMB, { first: 80, last: 82, min: 80, max: 95 });
  assert.equal(log.memory[1].time, DT, 'amostra no tempo de jogo');
  const sample = memorySample({ stats: () => ({ geometries: 7, textures: 3, programs: 2 }) });
  assert.equal(sample.geometries, 7);
  assert.ok(sample.heapMB === null || sample.heapMB > 0);
});

test('relatório em texto: resultado, problemas, FPS, memória e estações', () => {
  const log = new MonitorLog({ world, floorY: 0, lots: LOTS });
  for (let i = 0; i < 64; i++) log.tick(at(10, 0, 10), DT);
  let text = formatMonitorReport(log.report());
  assert.match(text, /→ OK/);
  assert.match(text, / 1 Counter-strafe\s+1 s/);
  assert.match(text, /FPS n\/d/);
  log.tick(at(10, -2, 10), DT);
  text = formatMonitorReport(log.report());
  assert.match(text, /penetração 1 \(máx\. 2\.000 u\)/);
  assert.match(text, /FALHOU/);
  assert.match(text, /tick 65: penetração em 10\.0 -2\.0 10\.0 \(2\.000 u\)/);
  assert.ok(HULL.radius > 2);
});
