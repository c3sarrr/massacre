// Mãos e antebraços de massinha do boneco (Fase 4.1; desenho em docs/phases/phase-4.md, seção 4.1, "Mãos de 4
// dedos"): três dedos e o polegar, grossos e arredondados como os humanos da Aardman (decisão do usuário, 2026-09-25;
// CMH3, CMH14, CMH16, CMH19 — poses de mão em massa; CMH15, CMH18 — mãos simples de massa). O viewmodel usa agora; a
// Fase 5 herda o modelo e o rig nos personagens. Unidades: u (polegada na escala do boneco).
// Referencial da mão direita (osso `mao`): origem no pulso, +X para as pontas dos dedos, +Y para as costas da mão,
// −Z para o lado do polegar (palma para baixo). A esquerda é a direita espelhada em Z.

const F = Object.freeze;

export const HAND = F({
  palm: F({ center: [1.72, 0, 0], half: [1.52, 0.72, 1.62], round: 0.62 }), // 3,0 × 1,4 × 3,2 u
  // Dedos (o primeiro é o do gatilho, do lado do polegar): base no nó do dedo, falanges ao longo de +X.
  fingers: F([
    F({ id: 'dedo1', base: [3.12, 0.08, -1.06], radius: 0.6, phalanges: F([1.2, 1.0, 0.86]) }),
    F({ id: 'dedo2', base: [3.2, 0.1, 0], radius: 0.63, phalanges: F([1.28, 1.06, 0.9]) }),
    F({ id: 'dedo3', base: [3.08, 0.08, 1.06], radius: 0.6, phalanges: F([1.14, 0.96, 0.82]) }),
  ]),
  // Polegar: sai da palma perto do pulso, do lado −Z, apontando para a frente e para fora.
  thumb: F({ id: 'polegar', base: [0.95, -0.22, -1.38], dir: [0.74, -0.14, -0.66], radius: 0.68, phalanges: F([1.25, 1.02, 0.86]) }),
  // Antebraço (osso `antebraco`: origem no cotovelo, +X para o pulso): cone arredondado.
  forearm: F({ length: 11, elbowRadius: 1.65, wristRadius: 1.25 }),
  // Nós dos dedos: vinco da costura onde o dedo sai da palma (a massa apertada no lugar).
  soft: 0.35,
  crease: F({ depth: 0.06, width: 0.14 }),
  knuckleSoft: 0.22,
  lumps: F({ amp: 0.025, freq: 0.5, octaves: 2 }),
  // Pesos do skinning: queda suave pela distância ao segmento do osso; os 4 maiores, normalizados.
  skin: F({ falloff: 0.55, influences: 4 }),
  mesh: F({ cell: 0.11, maxCells: 1400000, touchRadius: 0.5 }),
  // Massa do braço: a cor é a do boneco (terracota no boneco de referência; o criador da Fase 5 troca); o boil segue o
  // tamanho da mão (`objectSize`, u).
  clay: F({ roughness: 0.7, wetness: 0.36, objectSize: 9 }),
});

/**
 * Braçadeira do time no antebraço (seção 0.12): faixa de massa a 55% do antebraço, visível só com time. A cor é a do
 * time que mais se destaca da massa do braço: a primeira de `colors` (TEAM_COLORS) com diferença ΔE ≥ `minDelta` para a
 * massa, senão a mais distante — terracota não some no braço terracota do boneco de referência (vira o laranja).
 */
export const ARMBAND = F({
  at: 0.55, width: 1.7, thickness: 0.34, round: 0.3,
  colors: F(['primary', 'secondary', 'accent']),
  minDelta: 30,
  clay: F({ roughness: 0.66, wetness: 0.4, objectSize: 4 }),
  mesh: F({ cell: 0.06, maxCells: 600000, touchRadius: 0.3 }),
});

/**
 * Poses de mão (radianos). Cada dedo: [flexão da base, do meio, da ponta] — positivo dobra para a palma; `spread`
 * abre para os lados na base. Polegar: [giro na base em torno de +Y, flexão 1, flexão 2]. Pulso: [flexão, desvio].
 * A pose muda só na troca de pose (12/s, "em dois").
 */
export const HAND_POSES = F({
  aberta: F({ fingers: F([F([0.18, 0.22, 0.12]), F([0.2, 0.25, 0.14]), F([0.24, 0.28, 0.16])]), spread: F([-0.08, 0, 0.1]), thumb: F([0.15, 0.2, 0.12]), wrist: F([0, 0]) }),
  // Empunhadura da arma: o primeiro dedo esticado até o gatilho, os outros dois fechados em volta da empunhadura.
  empunhadura: F({ fingers: F([F([0.5, 0.95, 0.42]), F([1.38, 1.52, 0.86]), F([1.42, 1.5, 0.84])]), spread: F([-0.06, 0, 0.05]), thumb: F([0.62, 0.62, 0.38]), wrist: F([0, 0]) }),
  // Mão de apoio em concha por baixo da empunhadura (pistolas).
  apoio: F({ fingers: F([F([1.1, 1.2, 0.7]), F([1.16, 1.24, 0.72]), F([1.2, 1.28, 0.74])]), spread: F([0, 0, 0.04]), thumb: F([0.3, 0.16, 0.08]), wrist: F([0.12, 0]) }),
  // Mão em volta do guarda-mão (fuzis, SMGs, a frente da AWP).
  guardaMao: F({ fingers: F([F([1.02, 1.1, 0.66]), F([1.08, 1.16, 0.7]), F([1.12, 1.2, 0.72])]), spread: F([-0.04, 0, 0.06]), thumb: F([0.72, 0.42, 0.22]), wrist: F([0.08, 0]) }),
  // Mão na bomba da escopeta: fechada mais apertado.
  bomba: F({ fingers: F([F([1.22, 1.34, 0.8]), F([1.26, 1.38, 0.82]), F([1.3, 1.4, 0.84])]), spread: F([0, 0, 0.04]), thumb: F([0.86, 0.56, 0.3]), wrist: F([0.1, 0]) }),
  // Punho fechado no cabo da faca.
  faca: F({ fingers: F([F([1.44, 1.62, 1.0]), F([1.48, 1.64, 1.02]), F([1.5, 1.66, 1.04])]), spread: F([0, 0, 0]), thumb: F([1.0, 0.72, 0.42]), wrist: F([0, 0]) }),
});

/** Limites das juntas (radianos): flexão dos dedos, abertura, giro e flexão do polegar, pulso. */
export const HAND_LIMITS = F({
  flex: F([-0.3, 1.7]),
  spread: F([-0.35, 0.35]),
  thumbYaw: F([-0.4, 1.3]),
  thumbFlex: F([-0.3, 1.3]),
  wrist: F([-0.9, 0.9]),
});
