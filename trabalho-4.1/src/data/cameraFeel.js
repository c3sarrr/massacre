// Sensação da câmera em primeira pessoa (subfase 3.5; desenho em docs/phases/phase-3.md, seção 3.5): balanço preso ao
// relógio dos passos, inclinação ao andar de lado e no slide, chute de rolagem no wall-jump e mergulho com mola no
// pouso, na saída do pulo, no começo do slide e no wall-jump. Os valores de 100% são os do Doodle District
// (src/player.js da referência, em metros) na escala do CS: 40 u por metro (olho de 64 u ÷ 1,6 m) e a corrida da
// referência (10,6 m/s) na faca (250 u/s). Os três controles da seção "Conforto" (0–100%) multiplicam os valores de
// 100%; "Reduzir movimento" zera os três. Só visual: tiro, precisão, rede, replay e medidores usam o olho de verdade
// (PlayerPawn.eyeOffset).
// Ficam de fora, de propósito: o chute de FOV da referência (o FOV fixo preserva a leitura da mira e da luneta) e a
// tremida aleatória dos pousos duros (determinismo e conforto).

const F = Object.freeze;

export const CAMERA_FEEL = F({
  referenceSpeed: 250, // u/s: a corrida da referência na escala do CS (a faca)
  bob: F({
    // Referência: vertical |sen| × 0,03 m, lateral 0,018 m e rolagem 0,004 rad, com o peso de 1,4 na corrida.
    vertical: 1.7, // u: o ponto mais baixo no passo, o mais alto no meio da passada (o corpo sobre o pé de apoio)
    lateral: 1.0, // u: para o lado do pé do último passo
    rollDeg: 0.32, // °: para o mesmo lado
    weightRate: 8, // 1/s: o peso segue o alvo (velocidade no plano ÷ referência) com 1 − e^(−8·dt) por tick
    minSpeed: 90, // u/s: abaixo disso não há passo (STEPS.walkSpeed) nem balanço
    minSpeedDuck: 60, // o mesmo agachado (STEPS.duckWalkSpeed)
  }),
  tilt: F({
    strafeDeg: 1.3, // ° na velocidade de referência para o lado (0,022 rad): a cabeça pende para o lado do movimento
    slideDeg: 4.6, // ° no slide (0,08 rad), sempre para a direita, como na referência
    rate: 9, // 1/s: suavização da inclinação (1 − e^(−9·dt) por tick)
  }),
  kick: F({
    // Wall-jump: rolagem para longe da parede (0,1 rad da referência) numa mola crítica — pico em 1/ω = 77 ms e ~8% do
    // pico em 0,4 s.
    peakDeg: 5.7,
    stiffness: 170, // ω = √170 = 13,04/s
  }),
  dip: F({
    // Mergulho do olho (u, para baixo) numa mola sub-amortecida: pico em 90 ms, passa ~11% na volta. O impulso vai na
    // velocidade da mola, calculado para o pico dar `max` × o fator.
    max: 12, // u no fator 1: o pouso da queda do limite seguro (420 u, FALL.safeSpeed)
    stiffness: 170,
    damping: 15,
    minFall: 150, // u/s: pouso mais lento não mergulha
    fatalExtra: 0.4, // acima do limite seguro, mais até 40% na queda fatal (FALL.fatalSpeed)
    jump: 0.12, // fração do máximo na saída do pulo
    slide: 0.15, // no começo do slide (a queda de 18 u do olho continua sendo a suavização da 3.4)
    wallJump: 0.12, // no wall-jump
  }),
});

/** Níveis mostrados no desenho: % de balanço, inclinação e mergulho. O padrão do jogo é o Médio. */
export const CAMERA_FEEL_LEVELS = F({
  desligado: F({ bob: 0, tilt: 0, dip: 0 }),
  tatico: F({ bob: 0, tilt: 30, dip: 35 }),
  medio: F({ bob: 60, tilt: 70, dip: 65 }),
  forte: F({ bob: 100, tilt: 100, dip: 100 }),
});

export const CAMERA_FEEL_DEFAULT = CAMERA_FEEL_LEVELS.medio;
