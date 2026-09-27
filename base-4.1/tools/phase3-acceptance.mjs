// Varredura de aceite da Fase 3 (subfase 3.5; `npm run aceite:fase3`): 5 seeds × 10 min simulados na colisão da pista
// de testes (50 min) com a entrada aleatória da suíte (tests/pistaSim.js: andar, agachar, pulos, slides, wall-jumps,
// troca do item e empurrões de até 1500 u/s, partindo de cada estação) e as checagens do monitor do movimento
// (src/debug/moveMonitor.js): nenhuma penetração além da folga, nunca preso, nunca abaixo do chão do estúdio. Cada seed
// roda duas vezes e o estado final tem de sair igual, bit a bit. Imprime o relatório (pulos, slides, wall-jumps,
// empurrões, altura máxima e o tempo em cada estação) e sai com código 1 se algo falhou.
// Uso: node tools/phase3-acceptance.mjs [seed1 seed2 ...]

import { TEN_MINUTES, describeProblems, simulatePista, snapshotState } from '../tests/pistaSim.js';

const seeds = process.argv.slice(2);
if (!seeds.length) seeds.push('aceite-3-a', 'aceite-3-b', 'aceite-3-c', 'aceite-3-d', 'aceite-3-e');

const pad = (v, n) => String(v).padStart(n);
const totals = { jumps: 0, slides: 0, wallJumps: 0, kicks: 0, ticks: 0 };
const lotSeconds = new Map();
const lotLabels = new Map();
let failed = 0;

console.log(`Aceite da Fase 3 — ${seeds.length} seeds × 10 min na colisão da pista\n`);
console.log(`${'seed'.padEnd(12)} ${'pulos'.padStart(6)} ${'slides'.padStart(7)} ${'wall-j.'.padStart(8)} `
  + `${'empurr.'.padStart(8)} ${'alt. máx.'.padStart(10)} ${'checagem'.padStart(10)} ${'repete'.padStart(7)}  tempo`);
for (const seed of seeds) {
  const t0 = performance.now();
  const { state, stats, log } = simulatePista(seed, TEN_MINUTES, { check: true });
  const again = simulatePista(seed, TEN_MINUTES, { check: false }).state;
  const same = snapshotState(state) === snapshotState(again);
  const ok = log.ok && same;
  if (!ok) failed++;
  totals.jumps += stats.jumps;
  totals.slides += stats.slides;
  totals.wallJumps += stats.wallJumps;
  totals.kicks += stats.kicks;
  totals.ticks += log.checked;
  for (const l of log.report().lots) {
    lotSeconds.set(l.number, (lotSeconds.get(l.number) ?? 0) + l.seconds);
    lotLabels.set(l.number, l.label);
  }
  const check = log.ok ? 'ok' : `${log.penetrations + log.stuck + log.below} falhas`;
  console.log(`${seed.padEnd(12)} ${pad(stats.jumps, 6)} ${pad(stats.slides, 7)} ${pad(stats.wallJumps, 8)} `
    + `${pad(stats.kicks, 8)} ${pad(stats.maxY.toFixed(0), 10)} ${check.padStart(10)} `
    + `${(same ? 'sim' : 'NÃO').padStart(7)}  ${((performance.now() - t0) / 1000).toFixed(1)} s`);
  if (!log.ok) console.log(`  ${describeProblems(log)}`);
}

const minutes = totals.ticks / 64 / 60;
console.log(`\nTotal: ${minutes.toFixed(0)} min simulados · ${totals.ticks} ticks conferidos · ${totals.jumps} pulos · `
  + `${totals.slides} slides · ${totals.wallJumps} wall-jumps · ${totals.kicks} empurrões`);
console.log('Tempo em cada estação (todas as seeds):');
const width = Math.max(...[...lotLabels.values()].map((l) => String(l).length));
for (const [number, seconds] of [...lotSeconds.entries()].sort((a, b) => (a[0] || 99) - (b[0] || 99))) {
  const label = String(lotLabels.get(number)).padEnd(width);
  console.log(`  ${number ? pad(number, 2) : ' —'} ${label} ${pad((seconds / 60).toFixed(1), 5)} min`);
}
const verdict = failed ? `FALHOU em ${failed} de ${seeds.length} seeds.`
  : 'OK: nenhuma penetração, nunca preso, nunca abaixo do chão do estúdio; repetível bit a bit.';
console.log(`\n${verdict}`);
process.exitCode = failed ? 1 : 0;
