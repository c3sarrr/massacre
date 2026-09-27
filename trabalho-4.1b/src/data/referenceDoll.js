// Boneco de referência (subfase 3.5; desenho em docs/phases/phase-3.md, seção 3.5; referências no item 12 do
// moodboard): o boneco de escala da sala de testes e da vitrine e o corpo do jogador até a Fase 5 trazer os personagens
// (os bots da Fase 7 e os outros jogadores da Fase 9 também). Corpo em cápsula e cabeça de massinha sobre botas com
// cravos — a sola das pegadas (src/data/footprints.js). A mola do squash & stretch (src/characters/squashStretch.js)
// roda a 64 Hz e o corpo mostra o valor da pose (12 poses/s, "em dois"). Medidas para o boneco de 72 u (outras alturas
// escalam).

const F = Object.freeze;

export const REFERENCE_DOLL = F({
  height: 72,
  bodyScale: 0.94, // corpo e cabeça 6% menores, sobre as botas: a altura total continua 72 u
  boots: F({
    offset: 5.6, // u do centro do boneco ao centro de cada bota (PFT4: pés de massa de sola chata sob o boneco)
    toeOutDeg: 6, // bico para fora (CST16/CST19: bolotas com pezinhos; SFP1/SFP5: a trilha com o bico para fora)
    height: 4.5, // u: a subida da bota, dos cravos à borda de cima
    round: 1.2, // u: raio das bordas arredondadas (de cima e da sola)
    cleatHeight: 0.6, // u: os cravos em relevo embaixo
    cleatInset: 0.5, // u: os cravos param antes da borda da sola
    outline: 56, // pontos do contorno
    color: '#3B312B', // massa marrom-escura
  }),
  // Mola do corpo: passa ~25% e assenta em ~0,6 s (solução exata, por tick).
  spring: F({ stiffness: 260, damping: 13 }),
  // Squash & stretch com volume constante (SQS12, SQS17, SQS30): altura × (1 + x), largura × 1/√(1 + x).
  squash: F({
    jumpStart: -0.1, // saída do pulo e do wall-jump: começa achatado (SQS7, SQS11, SQS14, SQS19: antecipação)...
    jumpPeak: 0.14, // ...com o impulso que leva ao pico de esticada
    fall: 0.12, // caindo: estica até 12% × mín(1, queda ÷ fallSpeed) (SQS4, SQS24, BBR33)
    fallSpeed: 800,
    // Pouso: achata na hora 30% × o fator da queda da câmera (BBR7, BBR8, BBR22: a pose de contato é a mais achatada).
    land: 0.3,
    min: -0.45,
    max: 0.35,
    dead: -0.62, // morto: achata e alarga como massa caindo na mesa (a morte da seção 0.12)
  }),
  bootWiden: F({ gain: 0.35, max: 0.16 }), // as botas alargam 0,35 × o achatado, até 16%
  // Sombra de contato (BBR32: a sombra embaixo diz a altura): disco de borda macia no chão embaixo do boneco.
  shadow: F({
    diameter: 30, opacity: 0.4, // no chão
    fadeHeight: 300, minScale: 0.55, minOpacity: 0.35, // a 300 u de altura: 55% do tamanho e 35% da opacidade
    lift: 0.25, // u acima do chão
    probe: 2000, // u de busca do chão para baixo
    texture: 64, // px da textura do disco
  }),
});
