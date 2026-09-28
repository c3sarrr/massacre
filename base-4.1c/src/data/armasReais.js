// Armas realistas feitas no Blender (Fase 4.1a; desenho em docs/superpowers/specs/2026-09-26-armas-realistas-design.md,
// seções 4 e 5): o que o serviço weaponModels carrega pelo .glb (src/weapons/model/glbSource.js), o que o lançador do
// Blender constrói (tools/blender.mjs, tools/blender/armas/) e o que o validador da saída confere
// (tools/blender/saida.mjs). As outras armas continuam na receita de massinha (src/data/armas/) até serem refeitas
// (4.1c, 4.1d, 4.4).
//  - Zonas: grupos de material, a base das skins (o nome do material de cada primitiva do .glb).
//  - Soquetes: nós vazios com posição e orientação (os da base mais os da categoria).
//  - Peças móveis: nós próprios com o pivô no eixo real; `base` é o resto da arma.
//  - Orçamentos por classe (seção 5.1): triângulos por nível, lado das texturas e o total dos arquivos.
//  - `fabrica`: a pintura de fábrica, com as cores da ficha (tools/blender/refs/<id>.json, `cores.*.fabrica`).

const F = Object.freeze;

export const ZONAS = F(['corpo', 'guarnicao', 'carregador', 'detalhes', 'interno']);
export const LODS_REAIS = F(['perto', 'mundo', 'longe']);
// Conjunto de texturas de cada nível: o `perto` (viewmodel e bancada) usa o de 2048/1024; o `mundo` e o `longe`, o de 512/256.
export const TEXTURAS_DO_LOD = F({ perto: 'perto', mundo: 'mundo', longe: 'mundo' });
export const PECAS_MOVEIS = F(['ferrolho', 'carregador', 'gatilho', 'cao', 'seletor']);
export const SOQUETES_BASE = F(['boca', 'ejecao', 'carregador', 'mira_tras', 'mira_frente', 'mao_d', 'mao_e']);
export const SOQUETES_CATEGORIA = F({ sniper: F(['luneta']), escopeta: F(['bomba']) });
// Soquete → âncora da 4.1 (o viewmodel e a bancada continuam falando em âncoras até a 4.1d).
export const ANCORA_DO_SOQUETE = F({ mao_d: 'maoDireita', mao_e: 'maoEsquerda' });

export const ORCAMENTOS = F({
  fuzil: F({ triangulos: F({ perto: 40000, mundo: 6000, longe: 1500 }), textura: 2048, texturaMundo: 512, arquivosMB: 6 }),
  pistola: F({ triangulos: F({ perto: 20000, mundo: 3000, longe: 800 }), textura: 1024, texturaMundo: 256, arquivosMB: 3 }),
  faca: F({ triangulos: F({ perto: 8000, mundo: 1500, longe: 400 }), textura: 1024, texturaMundo: 256, arquivosMB: 2 }),
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
});

/** Soquetes que a arma precisa ter: os da base mais os da categoria. */
export function soquetesDaArma(id) {
  const a = ARMAS_REAIS[id];
  if (!a) throw new Error(`arma realista desconhecida: ${id}`);
  return [...SOQUETES_BASE, ...(SOQUETES_CATEGORIA[a.categoria] ?? [])];
}

/** Orçamento da classe da arma. */
export function orcamentoDaArma(id) {
  const a = ARMAS_REAIS[id];
  if (!a) throw new Error(`arma realista desconhecida: ${id}`);
  return ORCAMENTOS[CLASSE_DA_CATEGORIA[a.categoria]];
}
