// Boneco de referência de massinha com a altura do jogador (72 u = a medida do mundo): corpo em cápsula, cabeça e olhos
// de massinha com pupila sobre botas com cravos (subfase 3.5: a sola das pegadas; corpo e cabeça 6% menores, sobre as
// botas, para a altura total continuar a mesma). Usado na sala de testes e na vitrine para conferir a escala de tudo em
// volta (PLA2/PLA14: a mesa e os objetos do dia a dia provam o tamanho do boneco) e como o corpo do jogador até a
// Fase 5 (src/characters/playerBody.js). Números em src/data/referenceDoll.js; referências no item 12 do moodboard
// (PFT4 pés de massa sob o boneco, CST16/CST19 bolotas com pezinhos).

import { PALETTE } from '../../data/palette.js';
import { REFERENCE_DOLL } from '../../data/referenceDoll.js';
import { ClayMaterial } from '../ClayMaterial.js';
import { ClayAssembly } from './assembly.js';
import { clayBoot } from './boots.js';
import { clayBall, clayCapsule } from './shapes.js';

const DEG = Math.PI / 180;

/**
 * O boneco com as partes separadas, para quem anima (o corpo do jogador): `group` pronto para a cena (uma malha por cor
 * de massa, costuradas onde se encostam), `boots` (a malha das duas botas), `upper` (as malhas do corpo, da cabeça e
 * dos olhos) e `ankle` (a altura onde o corpo encosta nas botas: o pivô do squash & stretch).
 * @param {number} height altura total (u)
 * @param {{color?:string, seed?:string}} [opts]
 */
export function referenceDoll(height, { color = PALETTE.terracotta, seed = 'marcador' } = {}) {
  const D = REFERENCE_DOLL;
  const body = new ClayMaterial({ color, touched: true, wetness: 0.3, seed: `${seed}-corpo` });
  const white = new ClayMaterial({ color: PALETTE.clayWhite, touched: true, wetness: 0.45, seed: `${seed}-olho` });
  const black = new ClayMaterial({ color: '#1E1A18', touched: true, wetness: 0.6, roughness: 0.55, seed: `${seed}-pupila` });
  const bootClay = new ClayMaterial({
    color: D.boots.color, touched: true, wetness: 0.25, roughness: 0.66, seed: `${seed}-botas`,
  });
  const scale = height / D.height;
  const ankle = height * (1 - D.bodyScale);
  const up = height * D.bodyScale; // corpo e cabeça
  const headR = up * 0.14;
  const bodyR = up * 0.21;
  const bodyTop = up - headR * 1.6;
  const bodyLen = Math.max(4, bodyTop - bodyR * 2);
  const headY = ankle + up - headR;
  const eyeR = headR * 0.26;
  const eyeZ = headR * 0.84;
  const asm = new ClayAssembly(`${seed}-escala-${height}u`);
  asm.add(clayCapsule({ radius: bodyR, length: bodyLen, seed: 11 }), {
    material: body, position: [0, ankle + bodyR + bodyLen / 2, 0],
  });
  asm.add(clayBall({ radius: headR, squash: [1, 0.94, 1], seed: 12 }), { material: body, position: [0, headY, 0] });
  for (const side of [-1, 1]) {
    asm.add(clayBall({ radius: eyeR, segments: 8, lumpiness: 0.03, dents: 1, seed: 13 + side }), {
      material: white, position: [side * headR * 0.36, headY + headR * 0.08, eyeZ],
    });
    asm.add(clayBall({ radius: eyeR * 0.45, segments: 6, lumpiness: 0.02, dents: 0, seed: 15 + side }), {
      material: black, position: [side * headR * 0.34, headY + headR * 0.1, eyeZ + eyeR * 0.72], seams: false,
    });
  }
  // Botas: o boneco olha para +Z; o pé esquerdo fica em +X, com o bico virado para fora.
  for (const foot of ['left', 'right']) {
    const side = foot === 'left' ? 1 : -1;
    asm.add(clayBoot({ foot, scale, seed: 18 + side }), {
      material: bootClay, position: [side * D.boots.offset * scale, 0, 0],
      rotation: [0, side * D.boots.toeOutDeg * DEG, 0], name: `bota-${foot}`,
    });
  }
  const group = asm.build();
  const boots = group.children.find((m) => m.material === bootClay);
  const upper = group.children.filter((m) => m !== boots);
  return { group, boots, upper, ankle };
}

/**
 * Boneco de escala (sala de testes, vitrine).
 * @param {number} height altura total (u)
 * @param {{color?:string, seed?:string}} [opts]
 * @returns {import('three').Group}
 */
export function scaleMarker(height, opts = {}) {
  return referenceDoll(height, opts).group;
}
