// Pegadas na massinha (subfase 3.5; desenho em docs/phases/phase-3.md, seção 3.5; referências no item 12 do moodboard):
// a sola da bota com cravos (a mesma dos pés do boneco de referência, src/clay/kit/boots.js), a forma da marca (fundo
// pelos cravos, parede, lábio de massa empurrada, brilho de massa fresca), as marcas de cada evento do movimento, o
// mapa de pegadas de cada peça de chão de massinha e o esmaecimento. Unidades do jogo (u). A sola é descrita no
// referencial do pé: `a` ao longo do pé (positivo para o bico) e `bi` para o lado de dentro (o do dedão): pé esquerdo e
// direito são espelhos. Canais do mapa: R = fundo (0–1 × `depth`), G = lábio (0–1 × `lip`), B = massa fresca (0/1).

const F = Object.freeze;

/**
 * Sola da bota com cravos (FIM22: sola de cravos na lama; SFP20: o contorno do sapato transferido): calcanhar e bico
 * circulares ligados por tangentes, o bico cortado reto e desviado para dentro. 16,4 × 7,8 u de calcanhar a bico
 * (15,8 u com o bico cortado).
 */
export const SOLE = F({
  heel: F({ a: -5.0, radius: 3.2 }),
  toe: F({ a: 4.3, radius: 3.9 }),
  cut: 7.6, // bico cortado reto em a = +7,6
  inward: 0.3, // o bico desvia 0,3 u para o lado de dentro
  // Cravos (fundo relativo da marca: 1 nas barras): na frente, barras transversais em 55% de cada 1,8 u; no calcanhar,
  // barras ao comprido em metade de cada 1,6 u; o arco liso. `phase` (u) põe a borda das barras em (n · passo − phase).
  cleats: F({
    front: F({ from: -1, pitch: 1.8, duty: 0.55, gap: 0.74 }),
    heel: F({ to: -2.6, pitch: 1.6, duty: 0.5, gap: 0.78 }),
    arch: 0.58,
    phase: 20,
  }),
});

/** Forma da marca, mapa por peça, marcas dos eventos e esmaecimento. */
export const FOOTPRINTS = F({
  depth: 4, // u de fundo no R = 1 (o par do pouso)
  lip: 0.8, // u de lábio no G = 1
  wall: 1.1, // u: a parede da marca, da borda ao fundo (FIM10/FIM21: parede íngreme e borda nítida)
  // Lábio de massa empurrada fora da borda: gaussiana a `offset` u da borda com largura `width`, 60% mais alta na
  // frente (de a = 0 a a = 6, SFP6/FIM25: o impulso empurra a massa para a frente), na proporção da força da marca e
  // nunca acima do fundo máximo dela (a marca some inteira junto com a parte mais funda).
  lipRing: F({ offset: 0.9, width: 0.85, front: 0.6, frontFrom: 0, frontTo: 6, gain: 1 / 1.2 }),
  freshReach: 2.4, // u além da borda com brilho de massa fresca (FIM6/FIM7: o fundo molhado brilha mais)
  footReach: 13, // u: meia largura do retângulo de uma marca de pé (sola, lábio e brilho)
  // Mapa de pegadas por peça (o XZ do objeto, centrado): texels por u e o teto por lado (peça maior perde densidade).
  texelsPerUnit: 4,
  maxTexels: 1024,
  topTolerance: 4, // u: a peça recebe a marca se o topo dela está a até isto dos pés
  marks: F({
    // Passo: o pé do evento a ±offset do centro, virado para onde o jogador olha, bico para fora (SFP1/SFP5).
    step: F({ offset: 5.6, toeOutDeg: 6, strength: 0.75 }),
    // Pouso: o par lado a lado (FIM13/FIM24/FIM29); abaixo de `minFall` u/s de queda (descer meio degrau) não marca,
    // como a câmera e o corpo não reagem (src/data/cameraFeel.js, dip.minFall).
    land: F({ offset: 6.2, toeOutDeg: 8, strength: 1, minFall: 150 }),
    // Saída do pulo: o par com a frente mais funda e o calcanhar raso (o impulso), do calcanhar ao bico.
    jump: F({ offset: 6.2, toeOutDeg: 8, strength: 0.83, heel: 0.5, front: 1.3 }),
    // Slide: dois sulcos de calcanhar a ±offset da trajetória (um segmento por tick) e, no fim, um montinho de massa
    // empurrada `moundAhead` u à frente dos pés (só lábio, da força dos sulcos: some junto com eles).
    slide: F({ offset: 5.6, halfWidth: 1.5, strength: 0.5, moundRadius: 4, moundAhead: 8 }),
  }),
  // Esmaecimento: `rate` passos por segundo de simulação (um a cada 1/12 s, o ritmo das poses; a pausa congela); cada
  // passo tira 1/255 do fundo e do lábio e 3/255 do brilho (SFP17: as marcas somem com o tempo; SFP30: sobram as partes
  // mais fundas). O par do pouso some em 21,25 s, o passo em ~16 s, o sulco do slide em ~11 s e o brilho em 7,1 s.
  fade: F({ rate: 12, depth: 1, lip: 1, fresh: 3 }),
});
