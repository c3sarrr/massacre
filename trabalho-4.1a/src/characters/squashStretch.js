// Squash & stretch do corpo (subfase 3.5; números em src/data/referenceDoll.js; referências no item 12 do moodboard):
// uma mola de um escalar x (0 = normal; negativo achata, positivo estica), pura, por tick, pela solução exata. O corpo
// mostra o valor da pose (12 poses/s, src/characters/playerBody.js), com volume constante: altura × (1 + x) e largura ×
// 1/√(1 + x) (SQS12, SQS17, SQS30). Agachar e slide baixam a altura junto com a cápsula (72 → 54 u).
//  - Saída do pulo e do wall-jump: começa achatado (antecipação) com o impulso que leva ao pico de esticada (SQS7,
//    SQS11, SQS14, SQS19).
//  - No ar, caindo: estica pela velocidade de queda (SQS4, SQS24, BBR33).
//  - Pouso: achata na hora pelo fator da queda da câmera (a pose de contato é a mais achatada: BBR7, BBR8, BBR22) e
//    volta passando do normal (SQS7).
//  - Morto: achata e alarga como massa caindo na mesa; a volta ao jogo zera. A Fase 5 reaproveita a mola nas mortes dos
//    personagens.

import { HULL } from '../data/movement.js';
import { REFERENCE_DOLL } from '../data/referenceDoll.js';
import { landFactor } from '../player/cameraFeel.js';

const D = REFERENCE_DOLL;
const Q = D.squash;
const K = D.spring.stiffness;
const A = D.spring.damping / 2;
const WD = Math.sqrt(K - A * A);

/** Um passo exato da mola rumo a `target` (dt qualquer). */
function stepSpring(sq, target, dt) {
  const e = Math.exp(-A * dt);
  const c = Math.cos(WD * dt);
  const s = Math.sin(WD * dt);
  const x = sq.x - target;
  const v = sq.v;
  sq.x = target + e * (x * c + ((v + A * x) / WD) * s);
  sq.v = e * (v * c - ((A * v + K * x) / WD) * s);
}

/** Primeiro máximo de x(t) (a mola livre rumo a 0) partindo de x0 < 0 com velocidade v0 > 0. */
function firstPeak(x0, v0) {
  // Velocidade zero quando tan(ωt) = v0·ω / (A·v0 + K·x0); o primeiro instante positivo.
  const t = Math.atan2(v0 * WD, A * v0 + K * x0) / WD;
  return Math.exp(-A * t) * (x0 * Math.cos(WD * t) + ((v0 + A * x0) / WD) * Math.sin(WD * t));
}

/** Impulso da saída do pulo: a velocidade que leva de `jumpStart` ao pico `jumpPeak` (bisseção sobre o pico exato). */
function jumpKick() {
  let lo = 0;
  let hi = 100;
  for (let i = 0; i < 80; i++) {
    const v = (lo + hi) / 2;
    if (firstPeak(Q.jumpStart, v) > Q.jumpPeak) hi = v;
    else lo = v;
  }
  return (lo + hi) / 2;
}

export const JUMP_KICK = jumpKick();

/** Altura do pivô (tornozelo) e quanto a altura cai por unidade de agachar: 72 → 54 u acima do chão, como a cápsula. */
export const ANKLE = D.height * (1 - D.bodyScale);
export const DUCK_DROP = 1 - (HULL.duckHeight - ANKLE) / (HULL.standHeight - ANKLE);

/** Estado da mola (dados simples). */
export function createSquash() {
  return { x: 0, v: 0 };
}

export function resetSquash(sq) {
  sq.x = 0;
  sq.v = 0;
  return sq;
}

/**
 * Um tick. `s`: estado de movimento depois do playerMove; `events`: os do tick (jump, walljump, land {speed});
 * `alive`: morto, a mola vai para o achatado da morte. A mola anda primeiro e os eventos marcam o tick deles: o tick do
 * pulo mostra o achatado de partida e o do pouso, o achatado inteiro.
 */
export function updateSquash(sq, s, events, alive, dt) {
  let target = 0;
  if (!alive) target = Q.dead;
  else if (!s.onGround && s.velocity.y < 0) target = Q.fall * Math.min(1, -s.velocity.y / Q.fallSpeed);
  stepSpring(sq, target, dt);
  if (alive) {
    for (let i = 0; i < events.length; i++) {
      const e = events[i];
      if (e.type === 'jump' || e.type === 'walljump') {
        sq.x = Q.jumpStart;
        sq.v = JUMP_KICK;
      } else if (e.type === 'land') {
        const k = landFactor(e.speed);
        if (k > 0) {
          sq.x = Math.min(sq.x, -Q.land * k);
          sq.v = 0;
        }
      }
    }
  }
  const lo = alive ? Q.min : Q.dead;
  if (sq.x < lo) {
    sq.x = lo;
    if (sq.v < 0) sq.v = 0;
  } else if (sq.x > Q.max) {
    sq.x = Q.max;
    if (sq.v > 0) sq.v = 0;
  }
  return sq;
}

/**
 * Forma do corpo para a mola `sq` e o quanto agachou (0–1): `sy` (altura, acima do tornozelo), `sxz` (largura, volume
 * constante) e `widen` (as botas alargam no achatado).
 */
export function bodyShape(sq, duckAmount, out = { sy: 1, sxz: 1, widen: 0 }) {
  const sy = (1 + sq.x) * (1 - DUCK_DROP * duckAmount);
  out.sy = sy;
  out.sxz = 1 / Math.sqrt(sy);
  out.widen = Math.min(D.bootWiden.max, Math.max(0, -sq.x) * D.bootWiden.gain);
  return out;
}
