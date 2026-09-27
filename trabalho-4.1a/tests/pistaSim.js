// Simulação aleatória na colisão da pista de testes (subfases 3.3 e 3.4; módulo próprio na 3.5): entrada com andar,
// spam de agachar, pulos, slides, wall-jumps e troca do item na mão, partindo de cada estação (a mesma fatia de tempo em
// cada uma, do primeiro ponto de teleporte), com empurrões de até 1500 u/s a cada 400 ticks. As checagens são as do
// monitor do movimento (src/debug/moveMonitor.js: nenhuma penetração além da folga, nunca preso, nunca abaixo do chão
// do estúdio), que também soma o tempo em cada lote. Usada pelo teste de 10 min (tests/pistaFuzz.test.js) e pela
// varredura de aceite da Fase 3 (tools/phase3-acceptance.mjs, 5 seeds × 10 min).

import { RNG } from '../src/core/rng.js';
import { PISTA } from '../src/data/pista.js';
import { buildPistaLayout } from '../src/maps/pista/layout.js';
import { buildPistaColliders } from '../src/maps/pista/colliders.js';
import { CollisionWorld } from '../src/physics/collisionWorld.js';
import { resolveStations } from '../src/maps/stations.js';
import { MonitorLog } from '../src/debug/moveMonitor.js';
import { BTN } from '../src/player/moveCmd.js';
import { playerMove } from '../src/player/movement.js';
import { DT, itemEnv, makePlayer } from './playerTestUtils.js';

export const layout = buildPistaLayout();
export const world = CollisionWorld.fromBuilder(buildPistaColliders(layout), 'pista');
export const stations = resolveStations(layout.stations, world);
export const TEN_MINUTES = 10 * 60 * 64;
export const FLOOR = -PISTA.base.thickness; // chão do estúdio
const ITEMS = [['knife', 0], ['ak47', 0], ['awp', 1], ['negev', 0], ['c4', 0]];
const LOTS = PISTA.lots.map((l) => ({
  number: l.number, x: l.x, z: l.z, label: stations.find((s) => s.number === l.number)?.label,
}));

/**
 * `ticks` ticks com a seed `seed`. Devolve o estado final, as contagens (pulos, agachadas, empurrões, altura máxima,
 * estações, slides e wall-jumps) e, com `check`, o registro do monitor (`log.ok`, os problemas e o tempo por lote).
 */
export function simulatePista(seed, ticks, { check = true } = {}) {
  const rng = new RNG(seed);
  const per = Math.ceil(ticks / stations.length);
  const stats = { jumps: 0, ducks: 0, kicks: 0, maxY: -Infinity, stations: 0, slides: 0, wallJumps: 0 };
  const log = check ? new MonitorLog({ world, floorY: FLOOR, lots: LOTS }) : null;
  let p = null;
  let phase = 0;
  let turn = 0;
  let rates = { jump: 0, duck: 0, walk: 0 };
  for (let i = 0; i < ticks; i++) {
    if (i % per === 0) {
      const st = stations[Math.floor(i / per)];
      const s = st.spots[0].position;
      p = makePlayer(world, [s.x, s.y, s.z], { yaw: st.spots[0].yaw });
      stats.stations++;
    }
    if (phase-- <= 0) {
      phase = rng.int(16, 64);
      let f = rng.bool(0.3) ? rng.float(-1, 1) : rng.pick([-1, 0, 1]);
      let sd = rng.bool(0.3) ? rng.float(-1, 1) : rng.pick([-1, 0, 1]);
      const len = Math.hypot(f, sd);
      if (len > 1) {
        f /= len;
        sd /= len;
      }
      p.cmd.forward = f;
      p.cmd.side = sd;
      turn = rng.float(-5, 5);
      rates = { jump: rng.pick([0, 0.05, 0.3]), duck: rng.pick([0, 0, 0.5, 1]), walk: rng.pick([0, 0, 1]) };
      const [item, zoom] = rng.pick(ITEMS);
      p.env.item = itemEnv(item, zoom);
    }
    p.cmd.yaw += turn * DT;
    p.cmd.buttons = (rng.bool(rates.jump) ? BTN.JUMP : 0) | (rng.bool(rates.duck) ? BTN.DUCK : 0) | (rng.bool(rates.walk) ? BTN.WALK : 0);
    if (i % 400 === 399) {
      const dir = rng.onUnitSphere();
      const v = rng.float(300, 1500);
      p.state.velocity.set(dir.x * v, Math.abs(dir.y) * v, dir.z * v);
      p.state.onGround = false;
      stats.kicks++;
    }
    p.cmd.tick = i;
    playerMove(p.state, p.cmd, p.env);
    const s = p.state;
    for (const e of p.env.events) {
      if (e.type === 'jump') stats.jumps++;
      if (e.type === 'duck') stats.ducks++;
      if (e.type === 'slide' && e.phase === 'start') stats.slides++;
      if (e.type === 'walljump') stats.wallJumps++;
    }
    stats.maxY = Math.max(stats.maxY, s.origin.y);
    log?.tick(s, DT);
  }
  return { state: p.state, stats, log };
}

/** Estado inteiro como texto: números com a representação exata do double (igual ⇔ bit a bit). */
export function snapshotState(s) {
  return JSON.stringify({
    ...s, origin: s.origin.toArray(), velocity: s.velocity.toArray(), groundNormal: s.groundNormal.toArray(),
  });
}

/** Os problemas do registro em texto (mensagem das falhas). */
export function describeProblems(log) {
  return log.problems.map((p) => `tick ${p.tick}: ${p.kind} em ${p.at.map((v) => v.toFixed(2)).join(' ')}`).join('; ');
}
