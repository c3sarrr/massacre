// Arquivos de cada tarefa do plano da 4.1 (um arquivo muda numa tarefa só: sem estados intermediários).
export const TAREFAS = {
  1: {
    testes: ['tests/sdfProfile.test.js'],
    novos: ['src/clay/sdf/polygon.js'],
    pares: ['src/clay/sdf/params.js', 'src/clay/sdf/bounds.js', 'src/clay/sdf/shapes.js'],
  },
  2: {
    testes: ['tests/clayHands.test.js'],
    novos: [
      'src/data/hands.js', 'src/characters/hands/handShape.js', 'src/characters/hands/handSkin.js',
      'src/characters/hands/armband.js', 'src/characters/hands/handRig.js', 'src/characters/hands/handLibrary.js',
    ],
    pares: [],
  },
  3: {
    testes: ['tests/weaponRecipes.test.js'],
    novos: [
      'src/data/weaponPalette.js', 'src/data/viewmodel.js', 'src/weapons/model/recipe.js', 'src/weapons/model/weaponModel.js',
      'src/weapons/model/silhouette.js', 'src/weapons/model/weaponLibrary.js',
      'src/data/armas/glock.js', 'src/data/armas/ak47.js', 'src/data/armas/m4a4.js', 'src/data/armas/awp.js',
      'src/data/armas/nova.js', 'src/data/armas/p90.js', 'src/data/armas/knife.js', 'src/data/armas/index.js',
      'tools/blender/refs/glock.json', 'tools/blender/refs/ak47.json', 'tools/blender/refs/m4a4.json',
      'tools/blender/refs/awp.json', 'tools/blender/refs/nova.json', 'tools/blender/refs/p90.json', 'tools/silhueta.html',
    ],
    pares: ['src/data/claySkins.js', 'src/clay/glsl/skins.js', 'src/core/events.js'],
  },
  4: {
    testes: ['tests/viewmodel.test.js'],
    novos: ['src/weapons/viewmodel/placement.js', 'src/weapons/viewmodel/viewmodelLights.js', 'src/weapons/viewmodel/viewmodel.js'],
    pares: ['src/render/postPipeline.js', 'src/data/configSchema.js', 'src/ui/settingControls.js', 'src/ui/settingsScreen.js'],
  },
  5: {
    testes: [],
    novos: [
      'src/maps/animatorDesk.js', 'src/clay/set/pegboardMaterial.js', 'src/data/arsenal.js', 'src/maps/arsenal/turntable.js',
      'src/maps/arsenal/planSheets.js', 'src/maps/arsenal/bench.js', 'src/debug/panelControls.js', 'src/maps/arsenal/panel.js',
      'src/maps/arsenal/index.js', 'src/debug/weaponCommands.js',
    ],
    pares: [
      'src/clay/set/index.js', 'src/debug/showcase.js', 'src/debug/showcasePanel.js', 'src/maps/index.js', 'src/render/dispose.js',
      'src/player/freeCamera.js', 'src/debug/commands.js', 'src/modes/matchState.js', 'src/main.js',
    ],
  },
  6: {
    testes: ['tests/blenderPrevia.test.js'],
    novos: [
      'tools/blender/previa.mjs', 'tools/blender.mjs', 'tools/blender/massacre/__init__.py', 'tools/blender/massacre/receita.py',
      'tools/blender/massacre/eixos.py', 'tools/blender/massacre/importar.py', 'tools/blender/massacre/exportar.py',
      'tools/blender/massacre/previa.py', 'tools/blender/massacre/conferir.py', 'tools/blender/massacre_armas.py',
    ],
    pares: ['package.json', '.gitignore'],
  },
};
