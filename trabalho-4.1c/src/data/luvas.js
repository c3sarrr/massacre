// Registro das luvas táticas (Fase 4.1b; desenho em docs/superpowers/specs/2026-09-26-4.1b-luvas-e-empunhadura-design.md,
// seção 7.1; plano da 4.1b, D2 e D6): o que o Blender constrói (tools/blender/armas/luvas.py, pela ficha
// tools/blender/refs/luvas.json), o que o validador da saída confere e o que o jogo carrega.
//  - Zonas: os grupos de material das duas malhas (`couro` na palma, nas pontas e entre o polegar e o indicador;
//    `tecido` nas costas e nos lados; `reforco` no protetor dos nós, nas almofadas e na tira do punho).
//  - Ossos: 20 por braço, com o sufixo do lado (`_d`, `_e`); os dedos em três falanges, o anelar e o mínimo com o
//    metacarpo próprio (a borda da palma fecha em concha).
//  - Orçamento: os dois braços juntos (D6).
//  - Pinturas: acabamento, cor e desgaste por zona, no formato das skins das armas; Massa Crua em coiote e Tropa do
//    Estúdio em preto (seção 7.1). O coiote de partida (#8B6B4A) saía na pista, sob a luz quente, no mesmo laranja da
//    madeira de fábrica da AK e da mesa (P2, 2026-09-27: rgb 180/117/75 contra 188/129/97, 1,2× de luminância): ficou
//    mais escuro e puxado para o oliva (o matiz ~40°, longe dos ~23° da madeira), e o couro gasta menos (o gasto do
//    couro clareia).

const F = Object.freeze;

export const ZONAS_DAS_LUVAS = F(['couro', 'tecido', 'reforco']);
export const OSSOS_DO_BRACO = F([
  'antebraco', 'torcao', 'mao',
  'polegar_1', 'polegar_2', 'polegar_3',
  'indicador_1', 'indicador_2', 'indicador_3',
  'medio_1', 'medio_2', 'medio_3',
  'anelar_0', 'anelar_1', 'anelar_2', 'anelar_3',
  'minimo_0', 'minimo_1', 'minimo_2', 'minimo_3',
]);
export const FACCOES_DAS_LUVAS = F(['massaCrua', 'tropa']);
// A pega das armas (seção 6.4 do desenho; plano, D1): os 17 ossos de dedo de cada mão que o clipe `empunhadura` do
// .glb da arma gira, e os limites da validação da seção 6.3 (o relatório do Blender e o `luvas_contato` do jogo).
export const OSSOS_DE_DEDO = F([
  'polegar_1', 'polegar_2', 'polegar_3',
  'indicador_1', 'indicador_2', 'indicador_3',
  'medio_1', 'medio_2', 'medio_3',
  'anelar_0', 'anelar_1', 'anelar_2', 'anelar_3',
  'minimo_0', 'minimo_1', 'minimo_2', 'minimo_3',
]);
// `ladoMM` (regra do usuário de 2026-09-27, para toda arma com mão da frente): na mão da frente só o polegar fica de um
// lado da arma e os quatro dedos do outro, como a pega da AK no CS:GO — a polpa de cada um a pelo menos esta distância
// do plano do meio da arma, do lado certo (a mão do gatilho, quando a regra dela diz os lados, passa pela mesma conta).
// `polegarCurvaGraus` e `polegarFolgaMM` (o usuário, 2026-09-27: "o dedo tem que estar colado com a arma", sem curva):
// o polegar da mão da frente reto e deitado na face do lado dele — a MCP mais a IP até 20° (a versão recusada fazia um
// arco de 52°), a falange distal encostando (o trecho dela mais perto até `contatoMM`) e nenhum trecho a mais de 8 mm (a
// cunha da base, que sai da quina de baixo do guarda-mão).
// `dedosJuntosMM` (a revisão crítica da 4.1b, 2026-09-27): os dedos que abraçam a arma lado a lado, sem leque — a falange
// média de cada um a no máximo esta distância da do vizinho, menos da metade da largura dela (17 a 19 mm na ficha).
// Fechando cada dedo sozinho, os da mão da frente da AK saíam em leque (até 8,53 mm, a ponta a 17 mm); a ponta não
// conta, porque o dedo que dobra mais sai da ponta do vizinho.
export const LIMITES_DA_PEGA = F({
  penetracaoMM: 0.3, contatoMM: 1, contatoJogoMM: 0.05, ladoMM: 5, polegarCurvaGraus: 20, polegarFolgaMM: 8,
  dedosJuntosMM: 8,
});
export const DEDOS_DA_FRENTE = F(['indicador', 'medio', 'anelar', 'minimo']);
// As categorias do viewmodel com regra de pega no Blender (tools/blender/armas/empunhadura_regras.py): a arma realista
// delas sai com a pega no .glb; as outras entram com as armas delas, cada uma junto com a regra dela (4.1c: a faca na
// Tarefa 9, a pistola na 11; 4.1d).
export const CATEGORIAS_COM_PEGA = F(['rifle', 'faca']);
// As mãos da regra de cada categoria (4.1c; desenho da 4.1c, seção 4.4): o fuzil e a pistola com as duas, a faca só com
// a direita — o nó `pega` do .glb diz as dele (`extras.luvas.maos`) e o validador confere as duas listas; e a mão da
// frente (o polegar de um lado, os quatro dedos do outro: a regra do usuário de 2026-09-27), só no fuzil.
export const MAOS_DA_CATEGORIA = F({ rifle: F(['d', 'e']), pistola: F(['d', 'e']), faca: F(['d']) });
export const FRENTE_DA_CATEGORIA = F({ rifle: 'e' });
// O polegar dobrado por cima dos dedos (a empunhadura de martelo da faca, Tarefa 9): a polpa nas falanges deles, até
// `contatoMM`, e não na arma.
export const POLEGAR_SOBRE_DA_CATEGORIA = F({ faca: F(['indicador']) });

/** Os 20 nomes de osso de um braço (`d` ou `e`). */
export function ossosDoLado(lado) {
  if (lado !== 'd' && lado !== 'e') throw new Error(`lado das luvas: 'd' ou 'e' (veio ${lado})`);
  return OSSOS_DO_BRACO.map((o) => `${o}_${lado}`);
}

export const LUVAS = F({
  pasta: 'assets/maos/',
  orcamento: F({ triangulos: 14000, textura: 2048, arquivosMB: 6 }),
  pinturas: F({
    massaCrua: F({
      nome: 'Massa Crua (coiote)',
      zonas: F({
        couro: F({ acabamento: 'couro', cor: '#5C5139', desgaste: 0.15 }),
        tecido: F({ acabamento: 'tecido', cor: '#4D4432', desgaste: 0.12 }),
        reforco: F({ acabamento: 'borracha', cor: '#342E24', desgaste: 0.15 }),
      }),
    }),
    tropa: F({
      nome: 'Tropa do Estúdio (preta)',
      zonas: F({
        couro: F({ acabamento: 'couro', cor: '#1D1D1F', desgaste: 0.25 }),
        tecido: F({ acabamento: 'tecido', cor: '#232326', desgaste: 0.15 }),
        reforco: F({ acabamento: 'borracha', cor: '#2C2D30', desgaste: 0.2 }),
      }),
    }),
  }),
});

// O antebraço de massinha que entra no punho da luva e a braçadeira do time (seção 5 do desenho; plano, Tarefa 9). A
// seção vem da ficha (o retângulo arredondado do pulso crescendo até a circunferência do cotovelo, `perfilDoAntebraco`
// — o mesmo modelo que o Blender usou para vestir o punho da luva); aqui fica só o que é do jogo, em mm (a árvore SDF sai
// em u):
//  - o tronco vai de `dentroDoPunhoMM` antes do pulso (dentro do punho, que tem 45 mm: a ponta não fura a luva quando o
//    pulso dobra, e a boca do punho nunca mostra o fim da massa) até `alemDoCotoveloMM` depois do cotovelo, fora da
//    tela; `secoes` amostram a curva t^1,3;
//  - a irregularidade de massa moldada à mão (o `displace` do SDF, como a mão de massinha da 4.1) fica abaixo da folga
//    do forro do punho (1,6 mm na borda de dentro; medida com a luva de verdade, a menor folga sai 1,2 mm);
//  - a célula da malha: o antebraço tem curvatura baixa (cantos de 18 a 31 mm), e com 4 mm a silhueta erra ~0,1 mm
//    (h²/8r) — 12 mil triângulos, contra 35 mil do braço de massinha da 4.1; a braçadeira, com a borda arredondada de
//    2,5 mm, pede 2,3 mm;
//  - a torção passa do osso `antebraco` ao `torcao` em rampa linear do cotovelo à boca do punho (100 % `torcao`, como o
//    punho da luva): meia torção do pulso repartida ao longo do antebraço;
//  - a massa: a do boneco, com as digitais, a translucidez e o brilho de massinha, sem boil (seção 0.7);
//  - a braçadeira: uma faixa de massa em volta do antebraço, a `doPulsoMM` do pulso (depois da boca do punho, onde a
//    câmera do viewmodel pega), só com time.
export const BRACO_DE_MASSA = F({
  dentroDoPunhoMM: 20,
  alemDoCotoveloMM: 60,
  secoes: 24,
  irregularidade: F({ ampMM: 0.4, freqPorU: 0.5, oitavas: 2 }),
  malha: F({ celulaU: 0.16, maxCells: 1400000, touchRadius: 0.5 }),
  massa: F({ roughness: 0.7, wetness: 0.36, objectSize: 5 }),
  bracadeira: F({
    doPulsoMM: 110, larguraMM: 40, espessuraMM: 5, arredondaMM: 2.5, dentroMM: 1.5,
    irregularidade: F({ ampMM: 0.25, freqPorU: 0.9, oitavas: 2 }),
    massa: F({ roughness: 0.66, wetness: 0.4, objectSize: 3 }),
    malha: F({ celulaU: 0.09, maxCells: 800000, touchRadius: 0.3 }),
  }),
});
