// Bancada de armas — mapa `arsenal` (Fase 4.1; docs/phases/phase-4.md, seção 4.1, "Bancada de armas"): a mesa do
// animador da vitrine virada em bancada de armeiro. Referências no item 13 do moodboard: bancadas de armeiro com o
// quadro de ferramentas atrás (QGW1, QGW6, QGW8, QGW14), quadro de hardboard perfurado (QPB8, QPB13, QPB19), a roda de
// modelar de metal (QTT11) e a giratória de produto (QTT9), suportes de arame em garfo (QWS9, QWS12, QWS14) e as
// plantas a lápis com cotas (QBP3, QBP13, QBP15). Unidades: u (1 u = 1 mm no estúdio; as armas têm 7 a 48 u).

import { SHOWCASE_SET } from './showcase.js';

const F = Object.freeze;

export const ARSENAL = F({
  rig: 'vitrine', // a mesma montagem de luz da vitrine (key de tungstênio, fill frio, rim e a luminária)
  desk: SHOWCASE_SET, // mesa, tapete A1 e chão do estúdio da vitrine
  // Câmera de bancada: baixa e perto da roda, as armas de 3 cm pedem olhar de joalheiro.
  spawn: F({ x: 0, y: 70, z: 262, yawDeg: 0, pitchDeg: -18 }),
  bounds: SHOWCASE_SET.bounds,
  speedScale: 0.28,
  // "Segurar" do painel (o viewmodel com a câmera parada): o boneco de pé no tapete, o olho na altura do dele
  // (HULL.standEye acima do tapete), de frente para a roda — a arma na mão fica no feixe da key.
  hold: F({ x: 0, z: 236, yawDeg: 0, pitchDeg: -8 }),
  // Roda de modelar (QTT11): pé de metal pesado, coluna e prato torneado com anéis de centragem; gira devagar.
  turntable: F({
    x: 0, z: 185,
    foot: F({ radius: 30, height: 5 }),
    column: F({ radius: 7.5, height: 24 }),
    plate: F({ radius: 42, height: 4.2, rings: 5, ringDepth: 0.35 }),
    spin: 0.35, // rad/s
  }),
  // Suporte de arame (QWS9, QWS12): placa de compensado no prato e dois garfos de arame; a arma deita de lado neles.
  stand: F({ wire: 0.75, lift: 17, forkWidth: 2.2, forkDepth: 1.6, base: F({ width: 58, depth: 14, thickness: 1.8 }) }),
  // Fileiras no tapete, deitadas com o lado direito para cima (QGW14); a fileira começa em `x0` e as armas ficam a
  // `gap` uma da outra; a etiqueta de fita de cada arma fica `labelForward` à frente dela.
  rows: F([
    F({ label: 'Pistolas · SMG · Escopeta', z: 78, ids: F(['glock', 'p90', 'nova']) }),
    F({ label: 'Fuzis', z: 6, ids: F(['ak47', 'm4a4']) }),
    F({ label: 'Precisão · Corpo a corpo', z: -66, ids: F(['awp', 'knife']) }),
  ]),
  rowX0: -250,
  rowGap: 26,
  rowLabelX: -445,
  labelForward: 17,
  // Quadro de ferramentas de hardboard perfurado (QPB8, QPB13, QPB19) em pé no fundo do tapete, preso por dois pés.
  pegboard: F({
    z: -250, width: 760, height: 390, thickness: 4.8, pitch: 25.4, hole: 3.3,
    color: '#8E6B49', fiber: '#6E4F33', holeColor: '#1B130D', foot: F({ depth: 70, height: 40 }),
  }),
  // Plantas a lápis (QBP3, QBP13): papel creme preso com duas tiras de fita, contorno da referência em grafite, cota do
  // comprimento e o nome escrito à caneta (a planta vem de tools/blender/refs/<id>.json; a faca é desenhada de cabeça).
  plans: F({
    width: 160, height: 92, cols: 3, gapX: 22, gapY: 20, top: 330, tapeLength: 34,
    texture: F({ width: 768, height: 441 }),
    paper: '#F1E8D4', graphite: '#50535A', ink: '#1C2238', grid: '#D9CFB8',
  }),
  // Ferramentas penduradas no quadro (propGeometry.sculptTool): tipo, comprimento, posição no quadro (u, a partir do
  // canto de baixo à esquerda) e giro em graus.
  tools: F([
    F({ kind: 'espatula', length: 150, at: F([52, 118]), rotDeg: 90 }),
    F({ kind: 'laco', length: 140, at: F([86, 112]), rotDeg: 92 }),
    F({ kind: 'bolinha', length: 140, at: F([674, 116]), rotDeg: 88 }),
    F({ kind: 'agulha', length: 130, at: F([708, 124]), rotDeg: 90 }),
  ]),
  label: SHOWCASE_SET.label,
  // "Explodir" do painel: cada grupo se afasta do corpo nessa direção (u por unidade da régua).
  explode: F({
    max: 8,
    dirs: F({
      carregador: F([0, -1, 0]), ferrolho: F([0, 0, 1]), slide: F([0, 1, 0]), gatilho: F([0, -0.8, 0.6]),
      bomba: F([1, -0.2, 0]), alavanca: F([0, 0.3, 1]), silenciador: F([1, 0, 0]),
    }),
  }),
  anchorSize: 2.4, // eixos das âncoras
  planOverlay: F({ color: '#F28F3B', lift: 0.05 }), // contorno da planta por cima da arma na roda
});
