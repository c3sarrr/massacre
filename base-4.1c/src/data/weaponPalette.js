// Massas e números do gerador das armas de massinha (Fase 4.1; desenho em docs/phases/phase-4.md, seção 4.1;
// referências no item 13 do moodboard). Decisão do usuário (2026-09-25): cor real traduzida em massinha + acento da
// facção nos detalhes pequenos (massa de mira, gatilho, base do carregador, seletor).
// Massinha nunca é preta: o "preto" das armas reais vira grafite (QPG1, QPL1 — a pistola preta fosca de massa).

const F = Object.freeze;

/**
 * Massas da paleta das armas. `skin` é um id de src/data/claySkins.js; `colorB`/`colorC` são as cores extras da skin.
 * roughness e wetness seguem o ClayMaterial (0 = massa seca e fosca, 1 = fresca e úmida).
 */
export const WEAPON_CLAYS = F({
  grafite: F({ color: '#33383F', roughness: 0.68, wetness: 0.28 }), // metal preto (QPG5, QPL6)
  grafiteClaro: F({ color: '#79818A', roughness: 0.62, wetness: 0.34 }), // ferrolho, slide, peças soltas
  madeira: F({ color: '#8C5A3C', roughness: 0.7, wetness: 0.25, skin: 'veio', colorB: '#4A2C19', colorC: '#A5764D' }), // QPG2, QPL4
  madeiraEscura: F({ color: '#5A3825', roughness: 0.64, wetness: 0.3 }), // baquelite da empunhadura do AK (QPG2)
  verdeOliva: F({ color: '#48533A', roughness: 0.7, wetness: 0.26 }), // polímero verde (AWP, AUG, Scout)
  areia: F({ color: '#B79C6E', roughness: 0.72, wetness: 0.24 }), // polímero cor de areia (SCAR-20, 4.4)
  prata: F({ color: '#A8AEB5', roughness: 0.5, wetness: 0.55 }), // Deagle, Five-SeveN (4.4)
  aco: F({ color: '#9CA6B1', roughness: 0.42, wetness: 0.72 }), // lâmina da espátula (CTL6, CTL16): massa prata úmida
});

/** Acento da facção: `acento` na massa de mira, base do carregador e bola da alavanca; `acento2` no seletor/gatilho. */
export const FACTION_ACCENTS = F({
  tr: F({ acento: '#C8553D', acento2: '#F28F3B' }), // Massa Crua: terracota e laranja
  ct: F({ acento: '#2F6DB5', acento2: '#3FB8AF' }), // Tropa do Estúdio: azul e verde-água
  ambos: F({ acento: '#FFD23F', acento2: '#F4EDE1' }), // armas dos dois lados: amarelo-massinha e branco-massa
});

/** Rugosidade/umidade das massas de acento (massinha colorida nova, um pouco mais úmida que o corpo). */
export const ACCENT_CLAY = F({ roughness: 0.6, wetness: 0.4 });

/** Números do gerador (receita → árvore SDF → malha). Unidades: u (polegada na escala do boneco). */
export const WEAPON_MODEL = F({
  soft: 0.25, // k da união suave entre peças do mesmo grupo (a massa apertada uma na outra)
  crease: F({ depth: 0.08, width: 0.18 }), // vinco da costura onde duas massas se encostam
  seamWidth: 0.25, // faixa de costura entre massas de cores diferentes
  cutSoft: 0.12, // k da subtração suave dos cortes (borda do corte de estilete, não quina viva)
  lumps: F({ amp: 0.03, freq: 0.35, octaves: 2 }), // calombos da massa inteira (nenhuma peça é perfeita)
  minThickness: 1.2, // espessura mínima de massa ("fiel e gordinha")
  minBlade: 0.5, // exceção: a lâmina da espátula
  touchRadius: 0.6, // raio do "toque" (onde o dedo mais encosta: digitais) na escala das armas
  lods: F({
    perto: F({ cell: 0.14, maxCells: 1600000 }), // viewmodel e bancada
    mundo: F({ cell: 0.35, maxCells: 300000 }), // no chão e na mão dos outros
  }),
  silhouetteIoU: 0.8, // silhueta lateral do SDF × planta de referência (aceite da 4.1)
});
