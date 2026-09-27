// Registro das luvas táticas (Fase 4.1b; desenho em docs/superpowers/specs/2026-09-26-4.1b-luvas-e-empunhadura-design.md,
// seção 7.1; plano da 4.1b, D2 e D6): o que o Blender constrói (tools/blender/armas/luvas.py, pela ficha
// tools/blender/refs/luvas.json), o que o validador da saída confere e o que o jogo carrega.
//  - Zonas: os grupos de material das duas malhas (`couro` na palma, nas pontas e entre o polegar e o indicador;
//    `tecido` nas costas e nos lados; `reforco` no protetor dos nós, nas almofadas e na tira do punho).
//  - Ossos: 20 por braço, com o sufixo do lado (`_d`, `_e`); os dedos em três falanges, o anelar e o mínimo com o
//    metacarpo próprio (a borda da palma fecha em concha).
//  - Orçamento: os dois braços juntos (D6).
//  - Pinturas: acabamento, cor e desgaste por zona, no formato das skins das armas; Massa Crua em coiote e Tropa do
//    Estúdio em preto (seção 7.1).

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
export const LIMITES_DA_PEGA = F({ penetracaoMM: 0.3, contatoMM: 1, contatoJogoMM: 0.05 });
// As categorias do viewmodel com regra de pega no Blender (tools/blender/armas/empunhadura_regras.py): a arma realista
// delas sai com a pega no .glb; as outras entram com as armas delas (4.1c, 4.1d).
export const CATEGORIAS_COM_PEGA = F(['rifle']);

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
        couro: F({ acabamento: 'couro', cor: '#8B6B4A', desgaste: 0.25 }),
        tecido: F({ acabamento: 'tecido', cor: '#6B5038', desgaste: 0.15 }),
        reforco: F({ acabamento: 'borracha', cor: '#4A3A2C', desgaste: 0.2 }),
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
