// Arquivos de cada tarefa do plano executado da 4.1c. Diferente da 4.1b (cada arquivo numa tarefa só, na versão
// final), um arquivo que mudou em várias tarefas entra pedaço por pedaço: os blocos do diff base → trabalho
// (blocos-diff.mjs) vão cada um para a tarefa da mudança dele, e o plano dá a cada tarefa os pares da versão anterior até
// a dela. Assim cada tarefa tem o código e os testes dela, os testes falhando antes e passando depois.
//
// A ordem respeita os imports e a construção no Blender, que roda uma vez, depois da Tarefa 11: os scripts das armas,
// a biblioteca e o solver são Python sem teste do Node e só se exercitam no `construir` (a prova das peças roda na
// Tarefa 4), então entram inteiros, cada um na tarefa da mudança principal dele; tudo o que lê os .glb novos (os testes
// das três armas, a pega com a palma que cede, as armas do registro que viram realistas no jogo) entra com a construção
// (Tarefa 11). O `pega.js`, o `saidaPega.mjs` e o `luvas.js` entram inteiros na 11: a pega de uma mão (Tarefa 8), a
// regra da faca (9) e as duas mãos da pistola com a palma (11) estão entrelaçadas nas mesmas funções, e a leitura da
// pega passou a exigir a palma, que só as construções novas trazem.
//
// ARQUIVOS: caminho → tarefa (o arquivo inteiro ou todos os pares) ou { resto: tarefa, [tarefa]: [índices dos blocos] }.

export const ARQUIVOS = {
  // Tarefa 1: as referências e o moodboard (a seção 16, com as buscas das correções da P1 e a linha da luva preta da 13)
  'tools/moodboard.mjs': 1,
  'docs/art/moodboard.md': 1,

  // Tarefa 2: classes, ficha e validação por classe
  'tests/armasClasses.test.js': 2,
  'src/data/armasReais.js': { resto: 2, 11: [5] },
  'src/weapons/model/ficha.js': { resto: 2, 13: [11] },
  'src/weapons/model/glbSource.js': { resto: 2, 13: [2, 5] },
  'tools/blender/saida.mjs': { resto: 2, 7: [2, 3, 4], 11: [7] },
  'tools/blender/armas/validar.py': 2,

  // Tarefa 3: as três fichas e a régua
  'tests/fichas41c.test.js': 3,
  'tools/blender/refs/knife.json': 3,
  'tools/blender/refs/glock.json': 3,
  'tools/blender/refs/m4a4.json': 3,
  'tools/regua.html': 3,

  // Tarefa 4: as peças novas da biblioteca, a prova delas e o lançador (`provar pecas`)
  'tools/blender/armas/pecas_superficie.py': 4,
  'tools/blender/armas/provas_pecas.py': 4,
  'tools/blender/armas/pecas.py': 4,
  'tools/blender/armas/canonica.py': 4,
  'tools/blender/armas/contornos.py': 4,
  'tools/blender.mjs': { resto: 4, 2: [4, 6, 8], 7: [5, 7, 9], 8: [10], 9: [11], 11: [2, 3, 12, 13] },

  // Tarefas 5 a 7: os scripts das três armas; na 7, as correções da P1 (o relevo moldado, as texturas CC0, o polímero,
  // o anodizado, a madeira da AK, a conferência)
  'tools/blender/armas/glock.py': 5,
  'tools/blender/armas/m4a4.py': 6,
  'tools/blender/armas/m4a4_frente.py': 6,
  'tools/blender/armas/soquetes.py': 6,
  'tools/blender/armas/knife.py': 7,
  'tools/blender/armas/relevo.py': 7,
  'tools/blender/armas/texturas.py': 7,
  'tools/blender/texturas/fontes.json': 7,
  'tools/blender/armas/materiais.py': 7,
  'tools/blender/armas/assar.py': 7,
  'tools/blender/armas/ak47.py': 7,
  'tools/blender/armas/conferir.py': 7,
  'tools/blender/armas/estudio.py': 7,
  'src/weapons/model/relevoMoldado.js': 7,
  'src/weapons/model/glsl/acabamentos.js': 7,
  'src/weapons/model/materialArma.js': 7,
  'src/data/acabamentos.js': { resto: 7, 13: [0, 8, 9] },
  'src/weapons/viewmodel/placement.js': { resto: 12, 7: [6] },
  'tests/relevoMoldado.test.js': 7,
  'tests/texturasCC0.test.js': 7,
  'tests/skinsArma.test.js': { resto: 13, 2: [6], 7: [2, 3, 4, 5] },

  // Tarefas 8 a 10: o solver (Python)
  'tools/blender/armas/empunhadura_pega.py': 8,
  'tools/blender/armas/empunhadura_regras.py': 9,
  'tools/blender/armas/empunhadura_polegar.py': 9,
  'tools/blender/armas/empunhadura_arma.py': 10,

  // Tarefa 11: a regra da pistola, a palma que cede e a construção de tudo
  'tools/blender/armas/empunhadura.py': 11,
  'tools/blender/armas/empunhadura_dedo.py': 11,
  'tools/blender/armas/empunhadura_palma.py': 11,
  'tools/blender/armas/empunhadura_polegar_deitado.py': 11,
  'tools/blender/armas/empunhadura_validacao.py': 11,
  'tools/blender/armas/maos_palma.py': 11,
  'tools/blender/armas/maos_correcoes.py': 11,
  'tools/blender/armas/validar_maos.py': 11,
  'tools/blender/armas/luvas.py': 11,
  'tools/blender/armas/gravar.py': 11,
  'tools/blender/armas/exportar.py': 11,
  'tools/blender/armas/principal.py': 11,
  'tools/blender/refs/luvas.json': 11,
  'tools/blender/saidaPega.mjs': 11,
  'src/characters/hands/pega.js': 11,
  'src/characters/hands/fichaLuvas.js': 11,
  'src/characters/hands/modeloDobras.js': 11,
  'src/characters/hands/bracoLuva.js': 11,
  'src/data/luvas.js': 11,
  'tests/pegaUmaMao.test.js': 11,
  'tests/pegaPistola.test.js': 11,
  'tests/pegaGlb.test.js': 11,
  'tests/fichaLuvas.test.js': 11,
  'tests/modeloDobras.test.js': 11,
  'tests/bracoLuva.test.js': 11,
  'tests/luvasTestUtils.js': 11,
  'tests/armaAk47.test.js': 11,
  'tests/armaGlock.test.js': 11,
  'tests/armaM4a4.test.js': 11,
  'tests/armaKnife.test.js': 11,
  'tests/weaponLibraryGlb.test.js': { resto: 11, 13: [0, 5] },

  // Tarefa 12: no jogo — as três pelo .glb, as luvas nas categorias novas e as receitas de massinha delas fora
  'src/data/viewmodel.js': 12,
  'src/weapons/viewmodel/viewmodel.js': 12,
  'src/weapons/viewmodel/bracosLuva.js': { resto: 12, 13: [3, 4] },
  'src/data/armas/index.js': 12,
  'src/debug/luvasCommands.js': 12,
  'tools/cotovelos.mjs': 12,
  'tests/armasDoGlb.test.js': 12,
  'tests/viewmodelFaca.test.js': 12,
  'tests/viewmodel.test.js': 12,
  'tests/viewmodelLuvas.test.js': 12,
  'tests/blenderPrevia.test.js': 12,
  'tests/weaponRecipes.test.js': { resto: 12, 3: [4] },
  'tests/luvasCommand.test.js': 12,

  // Tarefa 13: a bancada, as plantas e as skins
  'src/data/arsenal.js': 13,
  'src/maps/arsenal/bench.js': 13,
  'src/maps/arsenal/planSheets.js': 13,
  'src/weapons/model/silhouette.js': 13,
  'src/weapons/model/weaponLibrary.js': 13,
  'src/weapons/skins/acabamento.js': 13,
  'src/weapons/skins/skin.js': 13,
  'src/debug/console.js': 13,
  'src/debug/weaponCommands.js': 13,
  'tests/bancada41c.test.js': 13,
  'tests/bracosUmaMao.test.js': 13,
  'tests/skinCommand.test.js': 13,
  'tests/materialLuva.test.js': 13,

  // Tarefa 14: os documentos (as regras, os desenhos, a pesquisa e o desenho das miras pedidos na P1)
  'CLAUDE.md': 14,
  'CLAUDE.md.md': 14,
  'docs/superpowers/specs/2026-09-26-armas-realistas-design.md': 14,
  'docs/superpowers/specs/2026-09-26-4.1b-luvas-e-empunhadura-design.md': 14,
  'docs/superpowers/specs/2026-09-28-4.1c-glock-m4a4-m9-design.md': 14,
  'docs/superpowers/specs/2026-10-01-miras-acessorios-e-skins-design.md': 14,
  'docs/research/miras-acessorios-skins.md': 14,
  'docs/research/miras-acessorios-skins/acabamentos_reais.md': 14,
  'docs/research/miras-acessorios-skins/miras_nos_jogos.md': 14,
  'docs/research/miras-acessorios-skins/miras_reais.md': 14,
  'docs/research/miras-acessorios-skins/pinterest.md': 14,
  'docs/research/miras-acessorios-skins/skins_nos_jogos.md': 14,
  'docs/research/miras-acessorios-skins/tecnica_das_miras.md': 14,

  // Tarefa 16: o relatório, o estado da fase e o plano de desenho com as notas da execução
  'docs/PROGRESS.md': 16,
  'docs/phases/phase-4.md': 16,
  'docs/superpowers/plans/2026-09-28-4.1c-glock-m4a4-m9.md': 16,
};

/** Arquivos que existem na base mas entram inteiros (o conteúdo foi trocado: as fichas no formato 2 no lugar das
 *  plantas da 4.1). */
export const INTEIROS = new Set(['tools/blender/refs/glock.json', 'tools/blender/refs/m4a4.json']);

/** Arquivos removidos, por tarefa (as receitas de massinha das três). */
export const REMOVER = { 12: ['src/data/armas/glock.js', 'src/data/armas/m4a4.js', 'src/data/armas/knife.js'] };

/** JSON de uma linha que ganha chaves no fim (o objeto do JSON.stringify): o plano traz só as chaves novas. */
export const JSON_CHAVES = { 1: ['docs/art/pinterest-boards.json'] };

/** Arquivos gerados por um comando do projeto na tarefa (o plano manda rodar; o aplicador roda). */
export const GERAR = { 1: [{ comando: 'node tools/moodboard.mjs', arquivo: 'docs/art/moodboard.html' }] };

/** Binários de entrada (não saem do construir): o plano diz de onde baixar (a página, o arquivo e o md5 do registro
 *  tools/blender/texturas/fontes.json, que o texturas.py confere); o validador copia da cópia de trabalho. */
export const BINARIOS = {
  7: [{
    arquivo: 'tools/blender/texturas/cherry_veneer/cherry_veneer_diff_2k.jpg',
    pagina: 'https://polyhaven.com/a/cherry_veneer',
    descricao: 'o difuso em JPG de 2K (2048 × 2048)',
    md5: '6d5c8b7fe2d3c262bf9d0e0178a86b20',
  }],
};

/** A prova das peças (Blender), depois da tarefa. */
export const PROVAR = { 4: ['pecas'] };

/** As tarefas que constroem no Blender depois de aplicadas (o validador roda o `construir`). */
export const CONSTRUIR = { 11: ['todas'] };

/** Os binários que o `construir` da tarefa escreve (copiados da construção aceita com --sem-blender). */
export const SAIDAS = { 11: ['assets/maos', 'assets/armas/ak47', 'assets/armas/glock', 'assets/armas/m4a4', 'assets/armas/knife'] };
