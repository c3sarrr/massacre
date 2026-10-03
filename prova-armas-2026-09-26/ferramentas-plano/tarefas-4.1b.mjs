// Arquivos de cada tarefa do plano executado da 4.1b (um arquivo entra numa tarefa só, na versão verificada — sem
// estados intermediários). A ordem respeita os imports: o `principal.py` chama o solver da pega, e o `luvas.py` fecha as
// poses de teste até o contato com o núcleo do solver, então o solver inteiro entra com a construção das luvas (Tarefa
// 6) e a Tarefa 7 fica com a construção da AK e a conferência; o `src/data/luvas.js`, que quase tudo importa, entra com
// a ficha (Tarefa 2). Os documentos que mudaram em várias tarefas entram na 13 (regras, desenhos, fase, moodboard) e na
// 15 (o PROGRESS e o plano de desenho com as notas da execução).
export const TAREFAS = {
  2: {
    testes: ['tests/fichaLuvas.test.js', 'tests/luvasDados.test.js'],
    novos: ['tools/blender/refs/luvas.json', 'src/characters/hands/fichaLuvas.js', 'src/data/luvas.js'],
    pares: [],
  },
  3: {
    testes: [],
    novos: [
      'tools/blender/armas/maos.py', 'tools/blender/armas/maos_medidas.py', 'tools/blender/armas/maos_limite.py',
      'tools/blender/armas/maos_gaiola.py', 'tools/blender/armas/maos_capsulas.py',
    ],
    pares: [],
  },
  4: {
    testes: [],
    novos: ['tools/blender/armas/maos_detalhes.py', 'tools/blender/armas/maos_alto.py'],
    pares: ['tools/blender/armas/materiais.py'],
  },
  5: {
    testes: [],
    novos: [
      'tools/blender/armas/maos_rig.py', 'tools/blender/armas/maos_contato.py', 'tools/blender/armas/maos_correcoes.py',
      'tools/blender/armas/validar_maos.py', 'tools/blender/armas/empunhadura.py',
      'tools/blender/armas/empunhadura_polegar.py', 'tools/blender/armas/maos_poses.py',
    ],
    pares: [],
  },
  6: {
    testes: [
      'tests/luvasSaida.test.js', 'tests/luvasGlb.test.js', 'tests/modeloDobras.test.js', 'tests/luvasTestUtils.js',
      'tests/pegaGlb.test.js',
    ],
    novos: [
      'tools/blender/armas/luvas.py', 'tools/blender/armas/empunhadura_regras.py',
      'tools/blender/armas/empunhadura_arma.py', 'tools/blender/armas/empunhadura_pega.py',
      'tools/blender/saidaLuvas.mjs', 'tools/blender/saidaPega.mjs', 'src/characters/hands/pega.js',
      'src/characters/hands/modeloDobras.js',
    ],
    pares: [
      'tools/blender/armas/assar.py', 'tools/blender/armas/exportar.py', 'tools/blender/armas/conferir.py',
      'tools/blender/armas/principal.py', 'tools/blender.mjs', 'tools/blender/saida.mjs',
    ],
  },
  7: { testes: [], novos: [], pares: [] },
  8: {
    testes: ['tests/materialLuva.test.js', 'tests/materialArma.test.js', 'tests/skinsArma.test.js'],
    novos: [],
    pares: [
      'src/data/acabamentos.js', 'src/weapons/skins/acabamento.js', 'src/weapons/skins/skin.js',
      'src/weapons/model/materialArma.js', 'src/weapons/model/glsl/acabamentos.js',
    ],
  },
  9: {
    testes: [
      'tests/sdfTronco.test.js', 'tests/antebracoMassa.test.js', 'tests/bracoLuva.test.js', 'tests/luvasSource.test.js',
    ],
    novos: [
      'src/clay/sdf/tronco.js', 'src/characters/hands/antebracoMassa.js', 'src/characters/hands/moldeLuva.js',
      'src/characters/hands/bracoLuva.js', 'src/characters/hands/luvasSource.js',
    ],
    pares: ['src/clay/sdf/params.js', 'src/clay/sdf/bounds.js', 'src/clay/sdf/shapes.js', 'src/main.js'],
  },
  10: {
    testes: ['tests/viewmodelLuvas.test.js', 'tests/weaponLibraryGlb.test.js'],
    novos: ['src/weapons/viewmodel/bracosLuva.js'],
    pares: [
      'src/data/viewmodel.js', 'src/weapons/viewmodel/placement.js', 'src/weapons/viewmodel/viewmodel.js',
      'src/weapons/model/glbSource.js', 'src/modes/matchState.js',
    ],
  },
  11: {
    testes: ['tests/luvasCommand.test.js'],
    novos: ['src/characters/hands/luvasContato.js', 'src/debug/luvasCommands.js'],
    pares: ['src/debug/weaponCommands.js', 'src/maps/arsenal/bench.js', 'src/maps/arsenal/panel.js'],
  },
  12: {
    testes: ['tests/rebatedor.test.js'],
    novos: ['src/maps/arsenal/rebatedor.js'],
    pares: [
      'src/clay/set/surfaceMaterials.js', 'src/clay/set/index.js', 'src/render/studio/fixtures.js',
      'src/data/arsenal.js', 'src/maps/arsenal/index.js',
    ],
  },
  13: {
    testes: [],
    novos: [],
    pares: [
      'CLAUDE.md', 'CLAUDE.md.md', 'docs/superpowers/specs/2026-09-26-armas-realistas-design.md',
      'docs/superpowers/specs/2026-09-26-4.1b-luvas-e-empunhadura-design.md', 'docs/phases/phase-4.md',
      'docs/art/moodboard.md',
    ],
  },
  14: { testes: [], novos: [], pares: [] },
  15: {
    testes: [],
    novos: [],
    pares: ['docs/PROGRESS.md', 'docs/superpowers/plans/2026-09-26-4.1b-luvas-e-empunhadura.md'],
  },
};

/** As tarefas que constroem no Blender depois de aplicadas (o validador roda o `construir`). */
export const CONSTRUIR = { 6: ['luvas', 'ak47 --forcar'] };
