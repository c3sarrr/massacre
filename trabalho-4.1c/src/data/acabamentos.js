// Acabamentos das skins das armas realistas (Fase 4.1a; desenho em docs/superpowers/specs/2026-09-26-armas-realistas-
// design.md, seção 6.1; referências QCK2/5/7/10/13 e QRL2/5/8/11 no item 14 do moodboard): cada um com os parâmetros do
// material físico (MeshPhysicalMaterial) e o padrão procedural que o trecho de shader das armas desenha por cima
// (src/weapons/model/glsl/acabamentos.js). `gasto` é o que o desgaste mostra por baixo, pelo canal de borda (_m.b): o
// metal nu nas pinturas, o aço claro nos metais, a madeira lixada, o plástico raspado. `varAspereza` e `varCor` dosam o
// quanto a variação assada (_m.g e _m.a, em torno de 0,5) mexe na aspereza e na cor. `verniz` liga a camada de verniz
// (clearcoat), `iridescencia` o filme fino, `anisotropia` o escovado ao longo do X da arma, `brilhoTecido` o brilho de
// tecido (o sheen do material físico: a intensidade, a aspereza e a cor dele — `superficie` + `ganho` × a cor do fio) —
// só quando o acabamento pede, para limitar as variantes de shader. `cor2Fator` faz a segunda cor (veio, trama, o fundo do grão)
// quando a skin não traz uma. Os das luvas (Fase 4.1b; desenho da 4.1b, seção 7.2): o couro sintético da palma e das
// pontas, com o grão fino; o tecido elástico das costas, com a trama e o brilho de tecido; a borracha moldada (TPR) do
// protetor dos nós, das almofadas e da tira, pontilhada. O grão, a trama e o pontilhado são finos demais para o assar
// (viravam moiré na _n; plano da 4.1b, Tarefa 6) e saem do shader.

const F = Object.freeze;

// Padrões procedurais do shader, na ordem do define ARMA_PADRAO. O `molde` (correções da P1 da 4.1c) é o grão do
// polímero moldado, só na aspereza: a textura de verdade das regiões texturizadas vem do relevo moldado (abaixo).
export const PADROES = F(['nenhum', 'fino', 'granulado', 'flocos', 'carbono', 'veio', 'pontilhado', 'ceramica', 'grao', 'trama', 'molde']);

// Relevos moldados (correções da P1 da 4.1c; plano da 4.1c, P1.1 e P1.2): as texturas do molde nas peças — o
// pontilhado do punho da Glock de 3ª geração (os grãos espalhados), o quadriculado das costas e da frente dela (os
// quadradinhos de topo chato), o losango do punho A2 da M4 e o recartilhado do cabo da M9 (fotos do Commons: Glock 18C,
// Glock 35, M4A1 da NSWC, "US Military M9 Bajonett COMPO"). O script da arma no Blender declara onde cada um vai
// (`relevos(ficha)`, tools/blender/armas/relevo.py) e o assar grava o tipo no alfa do `_n` (255 = liso, 255 − 32·id,
// src/weapons/model/relevoMoldado.js); o shader desenha o relevo pelo tipo em qualquer acabamento — a skin pinta por
// cima do molde. Medidas em mm: `passo` (a célula), `altura`, `raio` do grão (maior que meia célula: os grãos se
// encostam e o pontilhado lê como o granulado do molde, não como bolinhas soltas), `angulo` das linhas (graus) e `plato`
// (fração achatada do topo da pirâmide). Projeção `plano`: no plano da face (lado, frente ou cima, pela normal);
// `cilindrica`: em volta do eixo X da arma (o cabo torneado da faca), com um número fixo de `voltas` (os losangos numa
// volta, inteiro: sem emenda), o do `raioNominal` (mm) da peça; fora dele o losango estica ou encolhe na volta, como
// no recartilhado de verdade numa peça de diâmetro variável. Tirado do raio de cada ponto, o número pulava entre o
// meio e a quina das facetas do torno e o padrão rasgava ao longo do cabo.
export const RELEVOS_MOLDADOS = F({
  pontilhado: F({ id: 1, nome: 'Pontilhado', forma: 'graos', passo: 0.8, raio: 0.5, altura: 0.1, projecao: 'plano' }),
  quadriculado: F({ id: 2, nome: 'Quadriculado', forma: 'piramides', passo: 1.5, altura: 0.32, angulo: 0, plato: 0.45, projecao: 'plano' }),
  losango: F({ id: 3, nome: 'Losango', forma: 'piramides', passo: 1.3, altura: 0.36, angulo: 45, plato: 0.12, projecao: 'plano' }),
  // o cabo da M9: os segmentos com 13,8 a 13,9 mm de raio (a ficha, tornos.cabo)
  recartilhado: F({
    id: 4, nome: 'Recartilhado', forma: 'piramides', passo: 1.05, altura: 0.26, angulo: 45, plato: 0.05, projecao: 'cilindrica',
    raioNominal: 13.9, voltas: 59,
  }),
});

const NU = F({ cor: '#8F959C', metal: 1, aspereza: 0.32 }); // aço nu debaixo da tinta

export const ACABAMENTOS = F({
  // oxidado (o aço azulado da AK, o carregador de chapa dela): por igual, como nas fotos do board QAK — com ±0,16 de
  // aspereza o receptor e o carregador saíam manchados de cinza no reflexo, como chapa galvanizada (correções da P1 da
  // 4.1c); fosfatizado e nitretado modernos (o ferrolho da Glock, as peças de aço da M4) idem: com ±0,14 o ferrolho saía
  // manchado de nuvens
  oxidado: F({ nome: 'Oxidado de fábrica', metal: 1, aspereza: 0.34, padrao: 'fino', varAspereza: 0.06, varCor: 0.03, gasto: F({ cor: '#A7ABB0', metal: 1, aspereza: 0.2 }) }),
  fosfatizado: F({ nome: 'Fosfatizado', metal: 1, aspereza: 0.55, padrao: 'granulado', varAspereza: 0.07, varCor: 0.03, gasto: F({ cor: '#9CA0A6', metal: 1, aspereza: 0.26 }) }),
  fosco: F({ nome: 'Fosco', metal: 0, aspereza: 0.85, padrao: 'nenhum', varAspereza: 0.06, varCor: 0.04, gasto: NU }),
  acetinado: F({ nome: 'Acetinado', metal: 0, aspereza: 0.5, padrao: 'nenhum', varAspereza: 0.06, varCor: 0.04, gasto: NU }),
  brilhante: F({ nome: 'Brilhante', metal: 0, aspereza: 0.25, verniz: 1, asperezaVerniz: 0.05, padrao: 'nenhum', varAspereza: 0.04, varCor: 0.03, gasto: NU }),
  metalico: F({ nome: 'Metálico', metal: 0.6, aspereza: 0.35, verniz: 0.8, asperezaVerniz: 0.08, padrao: 'flocos', varAspereza: 0.05, varCor: 0.03, gasto: NU }),
  perolado: F({
    nome: 'Perolado', metal: 0.2, aspereza: 0.3, verniz: 1, asperezaVerniz: 0.06, iridescencia: 0.8, iorIridescencia: 1.3,
    filme: F([250, 600]), padrao: 'nenhum', varAspereza: 0.04, varCor: 0.03, gasto: NU,
  }),
  // Anodizado (correções da P1 da 4.1c): o alumínio jateado e anodizado das armas — o receptor da M4 nas fotos, as
  // peças coloridas das skins — é acetinado (a mesma aspereza do modelo alto no Blender, ASPEREZA_DE_FABRICA) e a cor
  // vem do corante nos poros da camada de óxido, grossa demais para o arco-íris de filme fino (esse é o do titânio
  // anodizado): a iridescência de 0,2 e a aspereza de 0,25 deixavam o receptor manchado de verde-azulado no reflexo.
  anodizado: F({
    nome: 'Anodizado', metal: 1, aspereza: 0.42, padrao: 'fino', varAspereza: 0.05, varCor: 0.04,
    gasto: F({ cor: '#C9CCD0', metal: 1, aspereza: 0.2 }),
  }),
  escovado: F({ nome: 'Aço escovado', metal: 1, aspereza: 0.3, anisotropia: 0.8, padrao: 'nenhum', varAspereza: 0.06, varCor: 0.03, gasto: F({ cor: '#B8BBBF', metal: 1, aspereza: 0.18 }) }),
  cromado: F({ nome: 'Cromado', metal: 1, aspereza: 0.05, padrao: 'nenhum', varAspereza: 0.03, varCor: 0.02, gasto: NU }),
  cerakote: F({ nome: 'Cerakote', metal: 0, aspereza: 0.7, padrao: 'ceramica', varAspereza: 0.08, varCor: 0.04, gasto: NU }),
  carbono: F({
    nome: 'Fibra de carbono', metal: 0, aspereza: 0.35, verniz: 1, asperezaVerniz: 0.05, padrao: 'carbono', duasCores: true, cor2Fator: 2.2,
    varAspereza: 0.04, varCor: 0.03, gasto: F({ cor: '#3A3C40', metal: 0, aspereza: 0.6 }),
  }),
  // Madeira (revisão crítica da P1 da 4.1c): o veio é o de uma madeira de verdade — a lâmina de cerejeira CC0 do
  // Blender (tools/blender/texturas/fontes.json), normalizada no canal A da _m (0,5 na média) — e `veio` é a conta que o
  // jogo e o modelo alto fazem com ele: a mistura para a segunda cor sobe de 0 (canal em `claro`) até `peso` (canal em
  // `escuro`), em curva suave; o brilho acompanha o canal pela `varCor`.
  madeira: F({
    nome: 'Madeira', metal: 0, aspereza: 0.45, verniz: 0.6, asperezaVerniz: 0.18, padrao: 'veio', duasCores: true, cor2Fator: 0.45,
    varAspereza: 0.1, varCor: 0.3, veio: F({ claro: 0.62, escuro: 0.22, peso: 0.8 }), gasto: F({ cor: '#C49A6C', metal: 0, aspereza: 0.62 }),
  }),
  // Polímero moldado (correções da P1 da 4.1c): acetinado nas faces lisas, como o da Glock e o da coronha e do punho da
  // M4 nas fotos; a textura das regiões do punho é o relevo moldado. Gasto, fica mais liso e um pouco mais claro (o
  // brilho que a mão dá), e não mais áspero.
  polimero: F({ nome: 'Polímero texturizado', metal: 0, aspereza: 0.45, padrao: 'molde', varAspereza: 0.06, varCor: 0.03, gasto: F({ cor: '#3A3C40', metal: 0, aspereza: 0.3 }) }),
  // Borracha moldada (TPR): semifosca, com o pontilhado do molde; gasta, fica mais lisa e um pouco mais clara.
  borracha: F({ nome: 'Borracha', metal: 0, aspereza: 0.68, padrao: 'pontilhado', varAspereza: 0.06, varCor: 0.04, gasto: F({ cor: '#55575B', metal: 0, aspereza: 0.5 }) }),
  // Couro sintético: brilho leve, o grão pequeno com o fundo das dobrinhas mais escuro; gasto, alisa e clareia.
  couro: F({ nome: 'Couro', metal: 0, aspereza: 0.56, padrao: 'grao', cor2Fator: 0.8, varAspereza: 0.08, varCor: 0.06, gasto: F({ cor: '#9C8468', metal: 0, aspereza: 0.4 }) }),
  // Tecido elástico: bem fosco, a trama com o fundo mais escuro e o brilho de tecido rente à superfície. A cor do brilho
  // tem duas partes (4.1c, Tarefa 13): o reflexo sem cor da superfície do fio, um dielétrico (o poliéster e o náilon,
  // n ≈ 1,55: F0 ≈ 4,5 %), e a luz que entra no fio e volta tingida por ele — o tecido escuro brilha escuro. Antes o
  // brilho clareava o fio 35 % rumo ao branco, e o preto da Tropa ganhava um brilho cinza de 0,36 que, na pista, o
  // levava de rgb(24, 9, 3) a (86, 51, 29): a luva preta lia cinza-parda (nas fotos, a luva preta continua preta). O
  // ganho deixa o brilho do coiote com a luminância de antes (0,389, a aprovada na 4.1b), agora na cor do fio; o do
  // preto cai para 0,14.
  tecido: F({
    nome: 'Tecido', metal: 0, aspereza: 0.88, padrao: 'trama', cor2Fator: 0.72,
    brilhoTecido: F({ intensidade: 1, aspereza: 0.5, superficie: 0.045, ganho: 5.78 }),
    varAspereza: 0.04, varCor: 0.05, gasto: F({ cor: '#8A7F74', metal: 0, aspereza: 0.95 }),
  }),
});
