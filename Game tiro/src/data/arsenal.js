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
  // Reflexo das armas realistas (Fase 4.1a, src/render/setReflection.js): o olho do "Segurar", de pé no tapete de frente
  // para a roda — de onde a arma na mão vê a bancada (a arma da roda entra só como parte do set, a 51 u).
  reflexo: F({ x: 0, z: 236 }),
  // Rebatedor (Fase 4.1b; desenho da 4.1b, seção 7.6): uma placa de isopor branco de 20 mm num C-stand, atrás de quem
  // olha a bancada e virada para ela — o lado do receptor das armas realistas refletia o estúdio escuro atrás do olho e
  // saía quase preto. Quem acende a placa é o `luz` da montagem (o rim: alto, do outro lado do set e apontando para cá,
  // é a única luz que chega pela frente ali; a key e o fill ficam atrás dela), e ela olha para a bissetriz entre essa luz
  // e o olho do reflexo, no plano horizontal, e deita `inclinacao` graus para trás (o cartão rebatedor de mesa do
  // estúdio de verdade, que devolve a contraluz para a frente). O lado do receptor virado para quem olha a roda
  // reflete, a partir do olho, a direção +Z um pouco para baixo (elevação −0,29): o tampo logo atrás dele. Medido na
  // bancada (a luminância do receptor): em pé na beira da mesa, a placa começava acima desse reflexo e clareava menos o
  // aço que alta e girada; deitada, a borda de baixo fica perto e rente ao tampo (cobre o centro do reflexo), a de
  // cima longe e alta — quase de frente para o rim — e abaixo dos raios da key que vão ao tapete (sem sombra na
  // bancada). `centro` = x e z do centro da placa; a altura sai da inclinação: a aresta de baixo de trás assenta no
  // tampo, na madeira atrás do tapete (girada para o rim, ela cruzaria a beira de trás do tapete em diagonal; o canto
  // mais perto fica 11 mm atrás dela, e a aresta de baixo da frente passa 6 mm acima do tapete). `braco` = do encaixe atrás da placa até a coluna do tripé (a coluna desce fora da
  // mesa); `conta` = o diâmetro das contas de isopor fundidas (mm).
  rebatedor: F({
    luz: 'rim',
    centro: F([0, 400]),
    largura: 700, altura: 220, espessura: 20, inclinacao: 25,
    braco: 150,
    conta: 4, cor: '#F2F1EC',
  }),
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
  // "Explodir" do painel: cada grupo (massinha) ou peça móvel (realista) se afasta do corpo nessa direção (u por unidade
  // da régua; referencial da arma: +X a boca, +Y em cima, +Z o lado direito). Pela tabela do nome (as peças da AK e os
  // grupos das de massinha): o cão da AK sai por cima e para a direita; o ferrolho e o seletor, para a direita, o lado
  // deles. O carregador que desliza sai pelo eixo dele (o `eixo` do .glb: o da Glock pelo eixo do punho, para baixo e
  // para trás, sem atravessar a frente do punho). `byWeapon` vale sobre os dois quando a peça da arma está noutro lugar
  // (4.1c, Tarefa 13): o ferrolho da Glock (a corrediça por cima da armação) sobe; o seletor da Glock e o da M4 (a
  // alavanca do lado esquerdo) saem pela esquerda, pelo eixo de giro; a alavanca de manejo da M4 sai para trás pelo
  // trilho dela e sobe acima da coronha; a tampa da janela da M4 (no lado direito, sem direção na tabela) sai para a
  // direita.
  explode: F({
    max: 8,
    dirs: F({
      carregador: F([0, -1, 0]), ferrolho: F([0, 0, 1]), slide: F([0, 1, 0]), gatilho: F([0, -0.8, 0.6]),
      bomba: F([1, -0.2, 0]), alavanca: F([0, 0.3, 1]), silenciador: F([1, 0, 0]), cao: F([0, 0.5, 1]), seletor: F([0, 0, 1]),
    }),
    byWeapon: F({
      glock: F({ ferrolho: F([0, 1, 0]), seletor: F([0, 0, -1]) }),
      m4a4: F({ alavanca: F([-0.8, 0.6, 0]), seletor: F([0, 0, -1]), tampa: F([0, 0, 1]) }),
    }),
  }),
  anchorSize: 2.4, // eixos das âncoras
  planOverlay: F({ color: '#F28F3B', lift: 0.05 }), // contorno da planta por cima da arma na roda
});
