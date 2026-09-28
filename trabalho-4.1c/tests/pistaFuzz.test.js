// 10 minutos simulados na colisão da pista de testes (subfases 3.3 e 3.4; a parte automática do aceite da Fase 3, na
// suíte com uma seed — a varredura de 5 seeds é o tools/phase3-acceptance.mjs): entrada aleatória com andar, spam de
// agachar, pulos, slides, wall-jumps e troca do item na mão, partindo de cada estação (50 s em cada uma, do primeiro
// ponto de teleporte), com empurrões de até 1500 u/s — pelas checagens do monitor do movimento, nenhuma penetração além
// da folga, nunca preso, nunca abaixo do chão do estúdio. Depois, a mesma seed repetida dá o mesmo estado inteiro, bit
// a bit. A simulação fica em tests/pistaSim.js.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { TEN_MINUTES, describeProblems, simulatePista, snapshotState } from './pistaSim.js';

test('10 min simulados na pista, partindo de cada estação: nenhuma penetração, nunca preso', () => {
  const { stats, log } = simulatePista('pista-dez-minutos', TEN_MINUTES, { check: true });
  assert.ok(log.ok, describeProblems(log));
  assert.equal(log.checked, TEN_MINUTES);
  assert.equal(stats.stations, 12);
  assert.ok(stats.jumps > 100, `pulos ${stats.jumps}`);
  assert.ok(stats.ducks > 100, `agachadas ${stats.ducks}`);
  assert.equal(stats.kicks, TEN_MINUTES / 400);
  assert.ok(stats.maxY > 200, `subiu em alguma coisa (${stats.maxY})`);
  assert.ok(stats.slides > 20, `slides ${stats.slides}`);
  assert.ok(stats.wallJumps > 20, `wall-jumps ${stats.wallJumps}`);
  // Cada fatia começa numa estação: os 12 lotes recebem tempo (os empurrões levam o jogador para a praça e os caminhos).
  const report = log.report();
  const lots = report.lots.filter((l) => l.number);
  assert.equal(lots.length, 12, lots.map((l) => `${l.number}: ${l.seconds.toFixed(0)} s`).join(', '));
  assert.ok(Math.abs(report.lots.reduce((sum, l) => sum + l.seconds, 0) - 600) < 1e-6, '10 min no total');
});

test('a mesma seed dá o mesmo estado inteiro na pista, bit a bit (2 min)', () => {
  const a = simulatePista('pista-repetivel', 2 * 60 * 64, { check: false }).state;
  const b = simulatePista('pista-repetivel', 2 * 60 * 64, { check: false }).state;
  assert.equal(snapshotState(a), snapshotState(b));
});
