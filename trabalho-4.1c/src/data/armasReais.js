// Armas realistas feitas no Blender (Fase 4.1a; desenho em docs/superpowers/specs/2026-09-26-armas-realistas-design.md,
// seções 4 e 5): o que o serviço weaponModels carrega pelo .glb (src/weapons/model/glbSource.js), o que o lançador do
// Blender constrói (tools/blender.mjs, tools/blender/armas/) e o que o validador da saída confere
// (tools/blender/saida.mjs). As outras armas continuam na receita de massinha (src/data/armas/) até serem refeitas
// (4.1c, 4.1d, 4.4).
//  - Zonas: grupos de material, a base das skins (o nome do material de cada primitiva do .glb).
//  - Soquetes: nós vazios com posição e orientação (os da base mais os da categoria).
//  - Peças móveis: nós próprios com o pivô no eixo real; `base` é o resto da arma.
//  - Classes (Fase 4.1c; plano da 4.1c, D3): fuzil, pistola e faca, cada uma com as zonas, os soquetes da base, as
//    medidas-chave da ficha (tools/blender/refs/<id>.json, `medidas`) e o orçamento (seção 5.1: triângulos por nível,
//    lado das texturas e o total dos arquivos). A faca não tem carregador, ferrolho nem miras.
//  - `fabrica`: a pintura de fábrica, com as cores da ficha (tools/blender/refs/<id>.json, `cores.*.fabrica`).

import { CATEGORIAS_COM_PEGA } from './luvas.js';

const F = Object.freeze;

export const ZONAS = F(['corpo', 'guarnicao', 'carregador', 'detalhes', 'interno']);
export const LODS_REAIS = F(['perto', 'mundo', 'longe']);
// Conjunto de texturas de cada nível: o `perto` (viewmodel e bancada) usa o de 2048/1024; o `mundo` e o `longe`, o de 512/256.
export const TEXTURAS_DO_LOD = F({ perto: 'perto', mundo: 'mundo', longe: 'mundo' });
// A alavanca de manejo e a tampa da janela de ejeção entram com a M4 (4.1c).
export const PECAS_MOVEIS = F(['ferrolho', 'carregador', 'gatilho', 'cao', 'seletor', 'alavanca', 'tampa']);
export const SOQUETES_BASE = F(['boca', 'ejecao', 'carregador', 'mira_tras', 'mira_frente', 'mao_d', 'mao_e']);
export const SOQUETES_CATEGORIA = F({ sniper: F(['luneta']), escopeta: F(['bomba']) });
// Soquete → âncora da 4.1 (o viewmodel e a bancada continuam falando em âncoras até a 4.1d).
export const ANCORA_DO_SOQUETE = F({ mao_d: 'maoDireita', mao_e: 'maoEsquerda' });
// As medidas-chave das armas de fogo (desenho geral, seção 3.4): comprimento, cano, raio de mira e as duas alturas.
export const MEDIDAS_DE_FOGO = F(['comprimento', 'cano', 'raioDeMira', 'alturaSemCarregador', 'alturaComCarregador']);

export const ORCAMENTOS = F({
  fuzil: F({ triangulos: F({ perto: 40000, mundo: 6000, longe: 1500 }), textura: 2048, texturaMundo: 512, arquivosMB: 6 }),
  pistola: F({ triangulos: F({ perto: 20000, mundo: 3000, longe: 800 }), textura: 1024, texturaMundo: 256, arquivosMB: 3 }),
  faca: F({ triangulos: F({ perto: 8000, mundo: 1500, longe: 400 }), textura: 1024, texturaMundo: 256, arquivosMB: 2 }),
});
// As classes (plano da 4.1c, D3). A faca: a lâmina (`corpo`), o cabo (`guarnicao`) e a guarda, a argola e o pomo
// (`detalhes`); os soquetes da mão e da ponta da lâmina (o golpe da 4.6); as medidas da ficha — comprimento, lâmina (da
// frente da guarda à ponta) e a espessura da lâmina.
export const CLASSES = F({
  fuzil: F({ zonas: ZONAS, soquetes: SOQUETES_BASE, medidas: MEDIDAS_DE_FOGO, orcamento: ORCAMENTOS.fuzil }),
  pistola: F({ zonas: ZONAS, soquetes: SOQUETES_BASE, medidas: MEDIDAS_DE_FOGO, orcamento: ORCAMENTOS.pistola }),
  faca: F({
    zonas: F(['corpo', 'guarnicao', 'detalhes']),
    soquetes: F(['mao_d', 'ponta']),
    medidas: F(['comprimento', 'lamina', 'espessuraLamina']),
    orcamento: ORCAMENTOS.faca,
  }),
});
// Classe de orçamento pela categoria do viewmodel (src/data/viewmodel.js).
export const CLASSE_DA_CATEGORIA = F({
  rifle: 'fuzil', sniper: 'fuzil', escopeta: 'fuzil', smgBullpup: 'fuzil', pistola: 'pistola', faca: 'faca',
});

// Reflexo do set (seção 5.4): lado de cada face da câmera cúbica, os planos de corte (u) e a intensidade no material
// (1 = a luz que o set tem de verdade; a conferência da Tarefa 18 compara a arma com a massinha em volta).
export const REFLEXO = F({ tamanho: 256, perto: 1, longe: 20000, intensidade: 1 });

export const ARMAS_REAIS = F({
  ak47: F({
    categoria: 'rifle',
    pasta: 'assets/armas/ak47/',
    zonas: ZONAS,
    pecas: F(['ferrolho', 'carregador', 'gatilho', 'cao', 'seletor']),
    fabrica: F({
      nome: 'De fábrica',
      zonas: F({
        corpo: F({ acabamento: 'oxidado', cor: '#303135', desgaste: 0.22 }),
        guarnicao: F({ acabamento: 'madeira', cor: '#A4673F', cor2: '#794224', desgaste: 0.18 }),
        carregador: F({ acabamento: 'oxidado', cor: '#4D5054', desgaste: 0.3 }),
        detalhes: F({ acabamento: 'oxidado', cor: '#303135', desgaste: 0.3 }),
        interno: F({ acabamento: 'escovado', cor: '#ADADAF', desgaste: 0 }),
      }),
    }),
  }),
  // Glock-18 de 3ª geração (Fase 4.1c; ficha em tools/blender/refs/glock.json): o ferrolho de aço com o acabamento
  // nitretado preto-acinzentado (fosfatizado no jogo), a armação e o carregador de polímero, os pinos, as alavancas e
  // as miras de aço preto acetinado e o cano, o extrator e a face da culatra de aço claro, vistos pela janela.
  glock: F({
    categoria: 'pistola',
    pasta: 'assets/armas/glock/',
    zonas: ZONAS,
    pecas: F(['ferrolho', 'carregador', 'gatilho', 'seletor']),
    fabrica: F({
      nome: 'De fábrica',
      zonas: F({
        corpo: F({ acabamento: 'fosfatizado', cor: '#34353A', desgaste: 0.12 }),
        guarnicao: F({ acabamento: 'polimero', cor: '#1F1F22', desgaste: 0.08 }),
        carregador: F({ acabamento: 'polimero', cor: '#1C1B1E', desgaste: 0.1 }),
        detalhes: F({ acabamento: 'acetinado', cor: '#19191B', desgaste: 0.15 }),
        interno: F({ acabamento: 'escovado', cor: '#9A9CA0', desgaste: 0 }),
      }),
    }),
  }),
  // M4A4 do jogo = a carabina M4A1 (Fase 4.1c; ficha em tools/blender/refs/m4a4.json): os receptores e a alça de alumínio
  // anodizado, o guarda-mão de trilhos, o punho e a coronha pretos, o carregador de alumínio com o revestimento seco, o
  // cano, a torre e os comandos de aço fosfatizado e o transportador do ferrolho de aço claro, visto pela janela.
  m4a4: F({
    categoria: 'rifle',
    // a regra rifle da pega é a da AK (o indicador cruza o gatilho da M4): a da M4A4 entra na Tarefa 10 do plano da 4.1c
    pega: false,
    pasta: 'assets/armas/m4a4/',
    zonas: ZONAS,
    pecas: F(['ferrolho', 'alavanca', 'tampa', 'carregador', 'gatilho', 'seletor']),
    fabrica: F({
      nome: 'De fábrica',
      zonas: F({
        corpo: F({ acabamento: 'anodizado', cor: '#2B2C2E', desgaste: 0.16 }),
        guarnicao: F({ acabamento: 'polimero', cor: '#1F2022', desgaste: 0.1 }),
        carregador: F({ acabamento: 'fosco', cor: '#4A4B4C', desgaste: 0.2 }),
        detalhes: F({ acabamento: 'fosfatizado', cor: '#3A3937', desgaste: 0.14 }),
        interno: F({ acabamento: 'escovado', cor: '#8E9094', desgaste: 0 }),
      }),
    }),
  }),
  // A faca: a baioneta M9 (EUA, 1986) de lâmina fixa (Fase 4.1c; ficha em tools/blender/refs/knife.json): a lâmina de
  // aço com o revestimento preto, o cabo de polímero marrom-oliva e a guarda e o pomo de aço pintados na cor dele.
  knife: F({
    categoria: 'faca',
    pasta: 'assets/armas/knife/',
    zonas: CLASSES.faca.zonas,
    pecas: F([]),
    fabrica: F({
      nome: 'De fábrica',
      zonas: F({
        corpo: F({ acabamento: 'fosfatizado', cor: '#2E2F31', desgaste: 0.12 }),
        guarnicao: F({ acabamento: 'polimero', cor: '#4A4234', desgaste: 0.1 }),
        detalhes: F({ acabamento: 'cerakote', cor: '#3F382C', desgaste: 0.14 }),
      }),
    }),
  }),
});

function arma(id) {
  const a = ARMAS_REAIS[id];
  if (!a) throw new Error(`arma realista desconhecida: ${id}`);
  return a;
}

/** A classe da arma (fuzil, pistola ou faca), pela categoria do viewmodel. */
export function classeDaArma(id) {
  return CLASSE_DA_CATEGORIA[arma(id).categoria];
}

/** Zonas de material da classe da arma. */
export function zonasDaArma(id) {
  return CLASSES[classeDaArma(id)].zonas;
}

/** Soquetes que a arma precisa ter: os da classe mais os da categoria. */
export function soquetesDaArma(id) {
  return [...CLASSES[classeDaArma(id)].soquetes, ...(SOQUETES_CATEGORIA[arma(id).categoria] ?? [])];
}

/** Medidas-chave da ficha que o construir confere a ±1 % (as da classe). */
export function medidasDaArma(id) {
  return CLASSES[classeDaArma(id)].medidas;
}

/** Se a arma sai com a pega das luvas no .glb: a categoria tem a regra no Blender (CATEGORIAS_COM_PEGA) e a arma não
 * espera a regra dela (`pega: false`). */
export function armaComPega(id) {
  const a = arma(id);
  return CATEGORIAS_COM_PEGA.includes(a.categoria) && a.pega !== false;
}

/** Orçamento da classe da arma. */
export function orcamentoDaArma(id) {
  return CLASSES[classeDaArma(id)].orcamento;
}
