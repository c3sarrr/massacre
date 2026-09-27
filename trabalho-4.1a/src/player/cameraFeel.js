// Sensação da câmera em primeira pessoa (subfase 3.5; números em src/data/cameraFeel.js): módulo puro, por tick (64
// Hz), sobre o estado de movimento e os eventos do tick. As molas andam pela solução exata (o mesmo resultado em
// qualquer tamanho de tick) e as suavizações por 1 − e^(−taxa·dt); a saída do tick anterior e a do atual são
// interpoladas no quadro como o resto da câmera (PlayerPawn.updateCamera). Saídas: deslocamento vertical e lateral (u,
// no eixo direito da câmera) e rolagem (rad, em volta do eixo da vista: a mira não sai do lugar). Sem giro de pitch — o
// "view punch" do CS tiraria a mira do lugar. Só visual.
//  - Balanço: ψ = π · (1 − stepTimer ÷ stepSpan), o ritmo do relógio de passos do CS; o ponto mais baixo no passo, o
//    mais alto no meio da passada, média zero numa passada; lateral e rolagem para o lado do pé do último passo. O peso
//    segue a velocidade no plano no chão, fora do slide e acima da velocidade mínima de passo.
//  - Inclinação: a cabeça pende para o lado do movimento; no slide, para a direita. Wall-jump: chute numa mola crítica
//    para longe da parede.
//  - Mergulho: mola sub-amortecida com impulso no pouso (pelo fator da queda, o mesmo do achatamento do corpo), na
//    saída do pulo, no começo do slide e no wall-jump.

import { CAMERA_FEEL } from '../data/cameraFeel.js';
import { FALL } from '../data/movement.js';

const DEG = Math.PI / 180;
const C = CAMERA_FEEL;
const TWO_OVER_PI = 2 / Math.PI;

const clamp = (v, lo, hi) => (v < lo ? lo : v > hi ? hi : v);

/** Mola sub-amortecida x'' = −k·x − d·x' (ζ < 1): constantes da solução exata e o pico por unidade de velocidade. */
function damped(k, d) {
  const w0 = Math.sqrt(k);
  const a = d / 2; // ζ·ω0
  const wd = Math.sqrt(k - a * a);
  const tPeak = Math.atan2(wd, a) / wd;
  return { k, a, wd, tPeak, peak: (Math.exp(-a * tPeak) * Math.sin(wd * tPeak)) / wd, w0 };
}

const DIP = damped(C.dip.stiffness, C.dip.damping);
const KICK_W = Math.sqrt(C.kick.stiffness);
/** Pico da mola crítica por unidade de velocidade: x(t) = v·t·e^(−ωt), máximo em t = 1/ω. */
const KICK_PEAK = 1 / (KICK_W * Math.E);

/** Constantes das molas (os testes conferem os tempos do desenho). */
export const FEEL_SPRINGS = Object.freeze({
  dipPeakTime: DIP.tPeak, // s até o pico do mergulho (~90 ms)
  dipOvershoot: Math.exp((-DIP.a * Math.PI) / DIP.wd), // fração que passa na volta (~11%)
  kickPeakTime: 1 / KICK_W, // s até o pico do chute do wall-jump (~77 ms)
});

/**
 * Fator da queda no pouso (o mergulho da câmera e o achatamento do corpo): 0 abaixo de 150 u/s; queda ÷ limite seguro
 * até ele (0,368 no pouso do pulo, 1 na queda de 420 u); acima, mais até 40% na queda fatal.
 */
export function landFactor(fall) {
  if (!(fall >= C.dip.minFall)) return 0;
  if (fall <= FALL.safeSpeed) return fall / FALL.safeSpeed;
  return 1 + C.dip.fatalExtra * Math.min(1, (fall - FALL.safeSpeed) / (FALL.fatalSpeed - FALL.safeSpeed));
}

/** Estado da sensação de um jogador (dados simples). */
export function createCameraFeel() {
  return {
    weight: 0, // peso do balanço (0–1)
    tilt: 0, // inclinação suavizada (rad)
    kick: 0, // rolagem do chute do wall-jump (rad) e a velocidade da mola
    kickV: 0,
    dip: 0, // mergulho (u, negativo = para baixo) e a velocidade da mola
    dipV: 0,
    y: 0, // saída do tick: deslocamento vertical (u)
    side: 0, // deslocamento lateral no eixo direito da câmera (u)
    roll: 0, // rolagem (rad; positivo = cabeça para a esquerda, a rolagem do three.js)
  };
}

/** Zera tudo na hora (morto, noclip, teleporte, volta ao jogo). */
export function resetCameraFeel(f) {
  f.weight = 0;
  f.tilt = 0;
  f.kick = 0;
  f.kickV = 0;
  f.dip = 0;
  f.dipV = 0;
  f.y = 0;
  f.side = 0;
  f.roll = 0;
  return f;
}

/** Um passo exato da mola sub-amortecida do mergulho (dt qualquer). */
function stepDip(f, dt) {
  const e = Math.exp(-DIP.a * dt);
  const c = Math.cos(DIP.wd * dt);
  const s = Math.sin(DIP.wd * dt);
  const x = f.dip;
  const v = f.dipV;
  f.dip = e * (x * c + ((v + DIP.a * x) / DIP.wd) * s);
  f.dipV = e * (v * c - ((DIP.a * v + DIP.k * x) / DIP.wd) * s);
}

/** Um passo exato da mola crítica do chute (dt qualquer). */
function stepKick(f, dt) {
  const e = Math.exp(-KICK_W * dt);
  const x = f.kick;
  const v = f.kickV;
  const b = v + KICK_W * x;
  f.kick = (x + b * dt) * e;
  f.kickV = (v - KICK_W * b * dt) * e;
}

/**
 * Um tick. `s`: estado de movimento depois do playerMove; `events`: os eventos do tick (land {speed}, jump,
 * slide {phase}, walljump {nx, nz}); `yaw`: o olhar do tick; `scales`: {bob, tilt, dip} de 0 a 1 (a seção "Conforto").
 */
export function updateCameraFeel(f, s, events, yaw, scales, dt) {
  const kb = scales.bob;
  const kt = scales.tilt;
  const kd = scales.dip;
  const dipUnit = (C.dip.max * kd) / DIP.peak;
  const rightX = Math.cos(yaw);
  const rightZ = -Math.sin(yaw);
  for (let i = 0; i < events.length; i++) {
    const e = events[i];
    switch (e.type) {
      case 'land':
        f.dipV -= dipUnit * landFactor(e.speed);
        break;
      case 'jump':
        f.dipV -= dipUnit * C.dip.jump;
        break;
      case 'slide':
        if (e.phase === 'start') f.dipV -= dipUnit * C.dip.slide;
        break;
      case 'walljump': {
        f.dipV -= dipUnit * C.dip.wallJump;
        // Normal da parede (para o jogador) no eixo direito do olhar: parede à direita → normal para a esquerda → a
        // cabeça tomba para a esquerda, para longe da parede.
        const lateral = e.nx * rightX + e.nz * rightZ;
        f.kickV -= (lateral * C.kick.peakDeg * DEG * kt) / KICK_PEAK;
        break;
      }
      default:
        break;
    }
  }
  const v = s.velocity;
  const speed = Math.hypot(v.x, v.z);
  const minSpeed = s.duckFlag ? C.bob.minSpeedDuck : C.bob.minSpeed;
  const weightTarget = s.onGround && !s.sliding && speed >= minSpeed ? Math.min(1, speed / C.referenceSpeed) : 0;
  f.weight += (weightTarget - f.weight) * (1 - Math.exp(-C.bob.weightRate * dt));
  const lateralSpeed = clamp((v.x * rightX + v.z * rightZ) / C.referenceSpeed, -1, 1);
  const tiltTarget = -C.tilt.strafeDeg * DEG * kt * lateralSpeed - (s.sliding ? C.tilt.slideDeg * DEG * kt : 0);
  f.tilt += (tiltTarget - f.tilt) * (1 - Math.exp(-C.tilt.rate * dt));
  stepDip(f, dt);
  stepKick(f, dt);
  const span = s.stepSpan > 0 ? s.stepSpan : 1;
  const psi = Math.PI * clamp(1 - s.stepTimer / span, 0, 1);
  const sn = Math.sin(psi);
  const w = f.weight * kb;
  // Pé do último passo: o relógio já trocou para o próximo (stepFoot), então é o outro. Esquerdo (0) → lado −1.
  const side = s.stepFoot === 1 ? -1 : 1;
  f.y = f.dip + C.bob.vertical * w * (sn - TWO_OVER_PI);
  f.side = side * C.bob.lateral * w * sn;
  f.roll = f.tilt + f.kick - side * C.bob.rollDeg * DEG * w * sn;
  return f;
}
