# Subfase 4.1 — Oficina de armas: plano de implementação

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** o caminho de modelagem inteiro e a fatia vertical das armas de massinha — três formas novas do SDF (perfil recortado, torno e tubo), a receita de cada arma em `src/data/armas/`, o gerador receita → malha de massinha por grupo animável (dois níveis de detalhe, com a biblioteca que guarda e empresta as malhas), as plantas de referência (a silhueta das armas reais), as mãos de 4 dedos gordinhos com rig, o viewmodel parado segurando a arma em primeira pessoa (FOV e offsets como no CS, luz do set com sombra própria e oclusão), a bancada `arsenal`, o Blender como editor da receita (importar, exportar, conferir com a malha do jogo, ida e volta) e as sete primeiras peças: Glock-18, AK-47, M4A4, AWP, Nova, P90 e a faca.

**Architecture:** a receita é dado puro (JSON num módulo por arma) e tudo o que é conta fica puro e testado no Node: as formas novas entram no kit SDF (`src/clay/sdf/polygon.js` + `shapes.js`, `bounds.js`, `params.js`); `src/weapons/model/recipe.js` valida a receita e monta uma árvore SDF por grupo (união suave com vinco de costura, cortes em subtração suave, calombos), `weaponModel.js` gera as malhas pelo `SdfMesher` (Workers e cache do IndexedDB) e `weaponLibrary.js` (serviço `weaponModels`) guarda e empresta malhas e materiais marcados como compartilhados; `silhouette.js` mede a silhueta lateral contra a planta. As mãos são uma árvore SDF (`handShape.js`) com pesos pela distância aos ossos (`handSkin.js`) numa `SkinnedMesh` de 14 ossos (`handRig.js`), geradas uma vez pelo serviço `handModels` (`handLibrary.js`). O viewmodel (`src/weapons/viewmodel/`) é uma camada própria do pipeline de pós: as contas de posição e visibilidade são puras (`placement.js`), a luz copia a do mapa com sombra própria e oclusão (`viewmodelLights.js`) e o `Viewmodel` monta arma e braços presos às âncoras. A bancada é um mapa (`src/maps/arsenal/`). O Blender roda scripts Python (`tools/blender/`) chamados pelo `tools/blender.mjs`, que prepara no Node o que só o jogo sabe calcular (a paleta, a mão em cada pose, a prévia do jogo). Números em `src/data/weaponPalette.js`, `hands.js`, `viewmodel.js`, `arsenal.js` e nas receitas.

**Tech Stack:** JavaScript ES Modules, three 0.186.1 (`SkinnedMesh`, camadas no pipeline de pós, sombras com câmera própria), three-mesh-bvh 0.9.15 (raios de oclusão), `node --test`; Blender 5.2 (Python `bpy`, Workbench) para o editor de receitas.

**Especificação:** `docs/phases/phase-4.md` (seção 4.1, com os ajustes feitos na implementação e as medições); decisões do usuário de 2026-09-25 (o Blender gera a receita, o estilo "fiel e gordinha", as mãos de 4 dedos gordinhos, a cor real com o acento da facção); referências visuais no item 13 do moodboard. Regras: `CLAUDE.md` (sem placeholder, < 600 linhas por arquivo, números em `src/data/`, tudo procedural — o Blender edita a receita, o jogo gera a malha).

**Como executar os blocos de código:** cada bloco ` ```js file=<caminho> ` (ou `json`, `html`, `python`) é o conteúdo completo do arquivo e é gravado com o extrator da Tarefa 0, sem redigitar — num arquivo que já existe, substitui o arquivo inteiro. Alterações em arquivos existentes vêm como pares "Em `arquivo`, trocar: … por: …", aplicados na ordem em que aparecem com a ferramenta de edição (cada trecho "trocar" é único no arquivo no momento em que é aplicado). Nenhum arquivo passa por estado intermediário: cada um é criado ou alterado numa tarefa só. O checkout tem arquivos com CRLF (`core.autocrlf`): os pares casam em LF e gravam LF.

**Estado de partida:** a árvore da 3.5 (sem commit, sobre o commit `953425b` da branch `fase-3.1`) com o desenho da Fase 4 registrado em `docs/phases/phase-4.md`; `npm test` com 294 testes passando. A 4.1 entra na mesma árvore.

**Commits:** os passos "Commit" só rodam quando o usuário pedir (decisão da 3.3: nada de commit até o pedido). Toda mensagem termina com a linha `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.

**Números conferidos pelos testes:** polígono com distância 2D exata (igual à força bruta nos dois sentidos de volta), filete de raio pedido tangente aos dois lados e limitado pelos lados, perfil com as arestas arredondadas exato em pontos conhecidos, torno igual ao cilindro da biblioteca girado para o X, tubo de um trecho igual à cápsula e ao cone arredondado, caixa envolvente e intervalo garantidos, malha fechada e bem orientada; as sete receitas validam com os grupos, as âncoras e as massas da tabela do primeiro lote, espessura mínima de 1,2 u (a lâmina da faca, 0,5 u), acento pela facção (TR terracota/laranja, CT azul/verde-água, as dos dois lados amarelo-massinha/branco-massa), silhueta lateral × planta com IoU ≥ 0,8 nas seis com planta (Glock 0,873, AK 0,931, M4A4 0,937, AWP 0,945, Nova 0,894, P90 0,947), comprimento real da tabela de escala (7,3 · 34,6 · 33,1 · 48,4 · 39,2 · 19,7 · 7,9 u, ±0,15 u, igual ao da planta), árvores determinísticas; mão com 14 ossos, malha fechada do tamanho do desenho, pesos normalizados em no máximo 4 ossos com cada dedo puxado pelos seus, poses dentro dos limites das juntas, esquerda = direita espelhada, braço na âncora (pulso no lugar, antebraço para o cotovelo), braçadeira pela cor do time mais distante da massa do braço (ΔE ≥ 30); viewmodel com o FOV do CS (60 horizontal em 4:3 = 46,83° vertical), giro de base, posição da categoria + offsets do CS + ajuste fino, ângulos, mãos nas âncoras no referencial da câmera, arma na tela e cotovelos fora dela em 16:9, visibilidade, acento, `viewmodel_presetpos`; a prévia do Blender com blocos alinhados, contagens coerentes, braços passando pelas âncoras e a câmera olhando para a arma.

**Números medidos** (a implementação verificada no navegador, RTX 2070 a 144 Hz, e no Blender 5.2.2): camada do viewmodel de ~1,3–1,6 ms por quadro (0,07 ms com a camada vazia); triângulos no nível `perto` de 4 360 (faca) a 72 540 (AWP) e a mão com 34 880; reler uma receita na bancada deixa as geometrias como estavam; 3 ciclos menu ↔ arsenal ↔ pista com a memória igual nas três voltas (menu 27/35/35, arsenal 76/43/51, pista 68/92/59 em geometrias/texturas/programas) e sem erros no console; `npm run blender -- ida-volta todas` idêntica byte a byte nas sete em 11,7 s, `conferir todas` em 48,7 s (seis vistas × sete armas); a massa de mira da AK escalada ×1,6 no Blender e exportada chega à bancada (topo de 2,017 u → 2,46 u) e volta ao original.

**Validação do próprio plano:** antes de ser gravado, o plano foi aplicado tarefa por tarefa numa cópia limpa do projeto (a árvore da 3.5) com o extrator e os pares: em cada tarefa os testes novos falham antes da implementação (as falhas esperadas estão em cada passo) e passam depois, a suíte inteira passa ao fim de cada tarefa (294 → 302 → 309 → 317 → 326 → 326 → 328), o Blender faz a ida e volta idêntica das sete na cópia e, no fim, cada arquivo criado ou alterado ficou idêntico ao da implementação verificada no navegador e no Blender.

---

## Mapa de arquivos

| Arquivo | Responsabilidade |
|---|---|
| `src/clay/sdf/polygon.js` | **novo** — polígono 2D: filete dos cantos (arcos tangentes, raio limitado pelos lados), distância exata com sinal, caixa |
| `src/clay/sdf/params.js`, `bounds.js`, `shapes.js` | leitores e limites de `profile`, `lathe` e `tube`; a função suporte de cada um; as distâncias exatas |
| `src/data/hands.js` | **novo** — medidas da mão de 4 dedos, braçadeira, poses (radianos) e limites das juntas |
| `src/characters/hands/handShape.js` | **novo** — ossos (cabeça, ponta, raio, pai) e a árvore SDF da mão direita com as costuras nos nós |
| `src/characters/hands/handSkin.js` | **novo** — pesos pela distância aos ossos (4 maiores, normalizados), giros das poses, espelho |
| `src/characters/hands/armband.js` | **novo** — cor da braçadeira pelo ΔE (CIE76) entre as cores do time e a massa do braço |
| `src/characters/hands/handRig.js` | **novo** — `ClayArm`: `SkinnedMesh` de 14 ossos, pose, âncora com cotovelo, braçadeira, lado esquerdo espelhado |
| `src/characters/hands/handLibrary.js` | **novo** — serviço `handModels`: a malha da mão e a braçadeira geradas uma vez, os braços dividindo |
| `src/data/weaponPalette.js` | **novo** — massas das armas, acento de cada facção e os números do gerador (`WEAPON_MODEL`) |
| `src/data/claySkins.js`, `src/clay/glsl/skins.js` | skin de base `veio` (madeira riscada a palito), fora das skins de jogador |
| `src/data/viewmodel.js` | **novo** — FOV, offsets e presets do CS, posição e cotovelos por categoria, categoria de cada arma, luz da camada |
| `src/weapons/model/recipe.js` | **novo** — validação da receita, espessura por forma, facção do acento, árvore SDF por grupo, massas |
| `src/weapons/model/weaponModel.js` | **novo** — malhas por grupo em dois níveis, materiais de massinha com o acento, montagem da instância |
| `src/weapons/model/silhouette.js` | **novo** — silhueta lateral do SDF (máximo em Z), IoU contra a planta, comprimento |
| `src/weapons/model/weaponLibrary.js` | **novo** — serviço `weaponModels`: malhas por (arma, nível), materiais por (arma, facção), pré-carga, recarga |
| `src/core/events.js` | `EV.WEAPON_MODEL` (`relendo` / `pronta`) |
| `src/data/armas/*.js` | **novos** — as sete receitas e o registro `index.js` |
| `tools/blender/refs/*.json`, `tools/silhueta.html` | **novos** — plantas de referência e a página que tira o contorno das fotos do Commons |
| `src/weapons/viewmodel/placement.js` | **novo** — contas puras: FOV do CS, pose da arma e das âncoras na câmera, cotovelos, facção, visibilidade, presets |
| `src/weapons/viewmodel/viewmodelLights.js` | **novo** — cópias das luzes do mapa, sombra própria focada e oclusão pelo set |
| `src/weapons/viewmodel/viewmodel.js` | **novo** — a camada: arma e braços, pose "em dois", braçadeira, luz, `status` e ajuste ao vivo |
| `src/render/postPipeline.js` | `beforeRender`/`afterRender` nas camadas |
| `src/data/configSchema.js`, `src/ui/settingControls.js`, `src/ui/settingsScreen.js` | `viewmodel.fov/offsetX/Y/Z`, `debug.viewmodel`, `debug.armband`; a seção "Arma na mão" com os presets |
| `src/maps/animatorDesk.js` | **novo** — a mesa do animador (tampo, pernas, tapete, chão), dividida entre a vitrine e a bancada |
| `src/clay/set/pegboardMaterial.js`, `src/clay/set/index.js` | **novo** — material do quadro de hardboard perfurado; registro no kit do set |
| `src/data/arsenal.js` | **novo** — números da bancada: fileiras, roda de modelar, suporte, quadro, plantas, ferramentas, "segurar" |
| `src/maps/arsenal/turntable.js`, `planSheets.js`, `bench.js`, `panel.js`, `index.js` | **novos** — roda e suporte, plantas a lápis, a bancada, o painel (Tab) e o mapa |
| `src/debug/panelControls.js`, `showcase.js`, `showcasePanel.js` | **novo** — controles de painel divididos entre a vitrine e a bancada; a mesa do animador vinda de `animatorDesk.js` |
| `src/maps/index.js`, `src/render/dispose.js`, `src/player/freeCamera.js` | o mapa `arsenal` no registro; recursos compartilhados fora do dispose das cenas; câmera estacionada |
| `src/debug/weaponCommands.js`, `src/debug/commands.js` | **novo** — `viewmodel_*`, `r_viewmodel`, `cl_bracadeira`, `arsenal`/`bancada`, `arma`, `armas` |
| `src/modes/matchState.js`, `src/main.js` | o viewmodel na partida, pré-carga das armas, "segurar"; os serviços `weaponModels` e `handModels` |
| `tools/blender/previa.mjs` | **novo** — a prévia do jogo para o Blender: malhas do jogo, braços skinned nas âncoras, câmera do viewmodel |
| `tools/blender.mjs`, `package.json`, `.gitignore` | **novo** — `npm run blender -- abrir|conferir|ida-volta|validar|previa`; o executável e o contexto |
| `tools/blender/massacre/*.py`, `tools/blender/massacre_armas.py` | **novos** — receita, eixos, importar, exportar, prévia e conferir no Blender; o painel "MASSACRE" |
| testes novos | `sdfProfile`, `clayHands`, `weaponRecipes`, `viewmodel`, `blenderPrevia` |

---

### Tarefa 0: Extrator dos blocos do plano

**Files:**
- Create: `<scratchpad>/extract-plan.mjs` (fora do projeto)

- [ ] **Passo 1: Criar o extrator** — o mesmo da 3.1 à 3.5: lê o plano e grava cada bloco ` ```<linguagem> file=... ` no caminho indicado, só para os arquivos pedidos na linha de comando.

```js
// Uso: node extract-plan.mjs <plano.md> <raiz do projeto> <arquivo> [arquivo...]
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { dirname, join } from 'node:path';

const [plan, root, ...wanted] = process.argv.slice(2);
const text = readFileSync(plan, 'utf8');
const re = /^```[a-z]+ file=(\S+)\n([\s\S]*?)^```$/gm;
const blocks = new Map();
for (const m of text.matchAll(re)) blocks.set(m[1], m[2]);
for (const file of wanted) {
  if (!blocks.has(file)) throw new Error(`bloco não encontrado no plano: ${file}`);
  const out = join(root, file);
  mkdirSync(dirname(out), { recursive: true });
  writeFileSync(out, blocks.get(file));
  console.log(`gravado ${file} (${blocks.get(file).split('\n').length - 1} linhas)`);
}
```

- [ ] **Passo 2: Conferir** — `node extract-plan.mjs docs/phases/phase-4.1-plan.md . src/clay/sdf/polygon.js` grava o arquivo pedido (apagar o arquivo de novo: a Tarefa 1 o cria no passo certo).

---

### Tarefa 1: Formas novas do SDF — perfil recortado, torno e tubo

**Files:**
- Create: `src/clay/sdf/polygon.js`, `tests/sdfProfile.test.js`
- Modify: `src/clay/sdf/params.js`, `src/clay/sdf/bounds.js`, `src/clay/sdf/shapes.js`

As peças das armas são massa cortada à mão (QPG2, QPL4): um contorno recortado e extrudado, um sólido torneado e uma cobrinha. `profile` é um polígono em XY (`points`) extrudado com meia-espessura `h` em Z, com `corner` (filete 2D nos cantos convexos e côncavos — a massa preenche os cantos de dentro) e `round` (as arestas da extrusão arredondadas); o filete é feito uma vez na compilação (arcos tangentes aos dois lados, raio limitado pelos lados, 6 segmentos por arco) e o `corner` fica ≥ `round`, o que torna exata a distância do contorno encolhido de `round` usada no "opExtrusion" arredondado de iq. A distância 2D é exata (distância aos segmentos com o sinal pelo número de cruzamentos), então a forma é 1-Lipschitz e entra no intervalo garantido d ± R do marching cubes. `lathe` é o mesmo polígono no semiplano (x, ρ ≥ 0) girado em volta do X (distância exata = a 2D em (x, √(y² + z²))), com `closed` para anéis. `tube` é uma polilinha 3D com raio por ponto (cones arredondados encadeados; a distância é o mínimo entre os trechos). `params.js` lê e limita (polígono de 3 a 256 pontos, sem lado de comprimento zero, raios positivos) e explica o problema quando a forma é inválida; `bounds.js` dá a função suporte de cada uma (o polígono e a revolução do polígono; no tubo, a casca das esferas das pontas).

- [ ] **Passo 1: Escrever os testes** — distância contra a força bruta, o filete, o perfil, o torno contra o cilindro, o tubo contra a cápsula e o cone arredondado, caixa e intervalo, malha fechada e as formas inválidas.

```js file=tests/sdfProfile.test.js
// Testes das formas por contorno do SDF (Fase 4.1): filete dos cantos, distância exata ao polígono, perfil
// recortado e extrudado, torno e tubo — distâncias contra força bruta e contra as formas antigas equivalentes,
// caixa envolvente, intervalo garantido, malha fechada e árvores inválidas.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { bounds, compile, createRange, evaluate, isEmptyBounds } from '../src/clay/sdf/nodes.js';
import { filletPolygon, latheOutline, polygonDistance, signedArea } from '../src/clay/sdf/polygon.js';
import { polygonize } from '../src/clay/sdf/marchingCubes.js';
import { RNG } from '../src/core/rng.js';
import { meshReport } from './sdfTestUtils.js';

const near = (actual, expected, eps = 1e-9, msg = '') => assert.ok(Math.abs(actual - expected) <= eps, `${msg} esperado ${expected}, veio ${actual}`);

// Ponto dentro de polígono por cruzamentos (independente do de iq) e distância aos lados.
function inside(poly, x, y) {
  let c = false;
  for (let i = 0, j = poly.length - 1; i < poly.length; j = i++) {
    const [xi, yi] = poly[i];
    const [xj, yj] = poly[j];
    if ((yi > y) !== (yj > y) && x < ((xj - xi) * (y - yi)) / (yj - yi) + xi) c = !c;
  }
  return c;
}
function segDist(px, py, a, b) {
  const ex = b[0] - a[0];
  const ey = b[1] - a[1];
  const t = Math.max(0, Math.min(1, ((px - a[0]) * ex + (py - a[1]) * ey) / (ex * ex + ey * ey)));
  return Math.hypot(px - a[0] - ex * t, py - a[1] - ey * t);
}
function bruteDistance(poly, x, y) {
  let d = Infinity;
  for (let i = 0; i < poly.length; i++) d = Math.min(d, segDist(x, y, poly[i], poly[(i + 1) % poly.length]));
  return inside(poly, x, y) ? -d : d;
}

// Estrela irregular (cantos convexos e côncavos) — um contorno de peça recortada.
const STAR = Array.from({ length: 14 }, (_, i) => {
  const a = (i / 14) * Math.PI * 2;
  const r = i % 2 ? 3.2 : 6 + (i % 4) * 0.7;
  return [Math.cos(a) * r, Math.sin(a) * r * 0.7];
});

test('polígono: distância exata igual à força bruta, dos dois sentidos de volta', () => {
  const rng = new RNG('poligono');
  for (const poly of [STAR, [...STAR].reverse()]) {
    const d = polygonDistance(poly);
    for (let i = 0; i < 3000; i++) {
      const x = rng.float(-9, 9);
      const y = rng.float(-7, 7);
      near(d(x, y), bruteDistance(poly, x, y), 1e-9, `(${x}, ${y})`);
    }
  }
});

test('filete: arcos tangentes de raio pedido, cantos côncavos cheios, raio limitado pelos lados', () => {
  const square = [[-5, -5], [5, -5], [5, 5], [-5, 5]];
  const f = filletPolygon(square, 1);
  // Cada ponto do contorno fica na borda do quadrado arredondado de raio 1 (distância ao quadrado encolhido = 1).
  const shrunk = polygonDistance([[-4, -4], [4, -4], [4, 4], [-4, 4]]);
  for (const [x, y] of f) near(shrunk(x, y), 1, 1e-9, 'ponto do filete');
  near(Math.abs(signedArea(f)), 100 - (4 - Math.PI), 0.05, 'área do quadrado arredondado');
  // L: o canto côncavo (em (0, 0)) ganha massa; os convexos perdem.
  const L = [[-4, -4], [4, -4], [4, 0], [0, 0], [0, 4], [-4, 4]];
  const fl = polygonDistance(filletPolygon(L, 1));
  assert.ok(fl(0.2, 0.2) < 0, 'canto côncavo cheio pelo filete');
  assert.ok(fl(3.9, -3.9) > 0, 'ponta convexa arredondada');
  near(fl(0.5, -2), polygonDistance(L)(0.5, -2), 1e-9, 'longe dos cantos nada muda');
  // Lado curto: o raio do canto cai para caber em metade dos lados (os arcos vizinhos não se cruzam).
  const thin = filletPolygon([[0, 0], [10, 0], [10, 0.4], [0, 0.4]], 1);
  for (const [, y] of thin) assert.ok(y >= -1e-12 && y <= 0.4 + 1e-12, 'filete limitado não sai da tira');
});

test('perfil: extrusão com as arestas arredondadas e os cantos em filete, exata em pontos conhecidos', () => {
  const p = { type: 'profile', points: [[-5, -2], [5, -2], [5, 2], [-5, 2]], h: 1, round: 0.25, corner: 0.5 };
  near(evaluate(p, 0, 0, 1), 0, 1e-9, 'face de cima (z = h)');
  near(evaluate(p, 0, 0, 0), -1, 1e-9, 'meio');
  near(evaluate(p, 5, 0, 0), 0, 1e-9, 'lado');
  near(evaluate(p, 6, 0, 0), 1, 1e-9, 'fora do lado');
  near(evaluate(p, 0, 0, 2), 1, 1e-9, 'acima da face');
  near(evaluate(p, 5.5, 0, 1.5), Math.hypot(0.75, 0.75) - 0.25, 1e-9, 'aresta arredondada');
  near(evaluate(p, 6, 3, 0), Math.hypot(1.5, 1.5) - 0.5, 1e-9, 'canto em filete');
  // Contra força bruta 3D do sólido arredondado: prisma do contorno encolhido engordado de `round`.
  const rng = new RNG('perfil');
  const shape = { type: 'profile', points: STAR, h: 0.9, round: 0.3, corner: 0.6 };
  const outline = polygonDistance(filletPolygon(STAR, 0.6));
  for (let i = 0; i < 2000; i++) {
    const x = rng.float(-8, 8);
    const y = rng.float(-6, 6);
    const z = rng.float(-2, 2);
    const wx = outline(x, y) + 0.3;
    const wy = Math.abs(z) - 0.6;
    const expect = Math.min(Math.max(wx, wy), 0) + Math.hypot(Math.max(wx, 0), Math.max(wy, 0)) - 0.3;
    near(evaluate(shape, x, y, z), expect, 1e-9);
  }
});

test('torno: igual ao cilindro da biblioteca girado para o eixo X; anel fechado; ponta com filete', () => {
  const lathe = { type: 'lathe', points: [[-5, 0], [-5, 2], [5, 2], [5, 0]] };
  const cyl = { type: 'cylinder', h: 5, r: 2, rot: [0, 0, Math.PI / 2] };
  const rng = new RNG('torno');
  for (let i = 0; i < 2000; i++) {
    const p = [rng.float(-8, 8), rng.float(-4, 4), rng.float(-4, 4)];
    near(evaluate(lathe, ...p), evaluate(cyl, ...p), 1e-9, `(${p})`);
  }
  const ring = { type: 'lathe', closed: true, points: [[-1, 3], [1, 3], [1, 4], [-1, 4]] };
  near(evaluate(ring, 0, 3.5, 0), -0.5);
  near(evaluate(ring, 0, 0, 3.5), -0.5, 1e-9, 'anel gira em volta de X');
  near(evaluate(ring, 0, 0, 0), 3, 1e-9, 'furo do anel');
  const tip = { type: 'lathe', corner: 0.8, points: [[0, 0], [0, 2], [6, 2], [6, 0]] };
  assert.ok(evaluate(tip, 6, 1.7, 0) > 0, 'quina da ponta arredondada');
  near(evaluate(tip, 3, 0, 2), 0, 1e-9, 'meio da lateral intacto');
  assert.deepEqual(latheOutline([[0, 0], [1, 2], [3, 0]], false), [[0, 0], [1, 2], [3, 0], [1, -2]]);
});

test('tubo: um trecho igual à cápsula e ao cone arredondado; vários trechos pegam o mais perto', () => {
  const rng = new RNG('tubo');
  const tube = { type: 'tube', points: [[0, 0, 0], [0, 10, 0]], r: 2 };
  const cap = { type: 'capsule', a: [0, 0, 0], b: [0, 10, 0], r: 2 };
  const cone = { type: 'tube', points: [[0, 0, 0], [0, 10, 0]], radii: [3, 1] };
  const rc = { type: 'roundCone', a: [0, 0, 0], b: [0, 10, 0], ra: 3, rb: 1 };
  const bent = { type: 'tube', points: [[0, 0, 0], [6, 0, 0], [6, 6, 2]], radii: [1, 1.5, 0.8] };
  for (let i = 0; i < 1500; i++) {
    const p = [rng.float(-6, 12), rng.float(-6, 14), rng.float(-6, 6)];
    near(evaluate(tube, ...p), evaluate(cap, ...p), 1e-9);
    near(evaluate(cone, ...p), evaluate(rc, ...p), 1e-9);
    const expect = Math.min(
      evaluate({ type: 'roundCone', a: [0, 0, 0], b: [6, 0, 0], ra: 1, rb: 1.5 }, ...p),
      evaluate({ type: 'roundCone', a: [6, 0, 0], b: [6, 6, 2], ra: 1.5, rb: 0.8 }, ...p),
    );
    near(evaluate(bent, ...p), expect, 1e-9);
  }
});

const TREES = {
  perfil: { type: 'profile', points: STAR, h: 0.8, round: 0.25, corner: 0.5, pos: [1, 2, -1], rot: [0.3, -0.7, 0.2] },
  torno: { type: 'lathe', corner: 0.3, points: [[-4, 0], [-4, 1.5], [-1, 1], [2, 2.2], [4, 1.2], [4, 0]], rot: [0, 0.6, 0.4] },
  anel: { type: 'lathe', closed: true, points: [[-1, 2], [1, 2], [1, 3], [-1, 3]], pos: [0, 1, 0] },
  tubo: { type: 'tube', points: [[0, 0, 0], [5, 1, 0], [6, 5, 3]], radii: [0.8, 1.4, 0.6], rot: [0.2, 0.2, 0.2] },
  uniao: {
    type: 'smoothUnion', k: 0.5, children: [
      { type: 'profile', points: [[0, 0], [8, 0], [8, 2], [0, 2]], h: 1, round: 0.3, corner: 0.4 },
      { type: 'lathe', points: [[7, 0], [7, 0.7], [14, 0.7], [14, 0]], pos: [0, 1, 0], mat: 1 },
    ],
  },
};

test('formas por contorno: a caixa envolvente contém a massa e o intervalo é garantido', () => {
  const rng = new RNG('caixas-contorno');
  const q = createRange();
  for (const [name, tree] of Object.entries(TREES)) {
    const b = bounds(tree);
    assert.ok(!isEmptyBounds(b), name);
    const ext = b.max.map((v, i) => v - b.min[i]);
    let massa = 0;
    for (let i = 0; i < 5000; i++) {
      const p = [0, 1, 2].map((a) => b.min[a] - ext[a] * 0.5 + rng.next() * ext[a] * 2);
      if (evaluate(tree, ...p) > 0) continue;
      massa++;
      for (let a = 0; a < 3; a++) assert.ok(p[a] >= b.min[a] - 1e-9 && p[a] <= b.max[a] + 1e-9, `${name}: massa fora da caixa`);
    }
    assert.ok(massa > 30, `${name}: amostrou a massa`);
    const sdf = compile(tree);
    const plain = compile(tree, { cull: false });
    for (let i = 0; i < 300; i++) {
      const c = [0, 1, 2].map((a) => b.min[a] - 2 + rng.next() * (ext[a] + 4));
      const R = rng.float(0.05, 3);
      sdf.range(...c, R, q);
      for (let j = 0; j < 8; j++) {
        const dir = rng.onUnitSphere();
        const t = R * Math.cbrt(rng.next());
        const p = [c[0] + dir.x * t, c[1] + dir.y * t, c[2] + dir.z * t];
        const d = sdf.distance(...p);
        assert.ok(d >= q.lo - 1e-9 && d <= q.hi + 1e-9, `${name}: fora do intervalo`);
        assert.equal(d, plain.distance(...p), `${name}: a poda mudou a distância`);
      }
    }
  }
});

test('formas por contorno viram malha fechada e bem orientada', () => {
  for (const name of ['perfil', 'torno', 'tubo', 'uniao']) {
    const tree = TREES[name];
    const mesh = polygonize(compile(tree), bounds(tree), { resolution: 56, maxCells: 400000 });
    const r = meshReport(mesh);
    assert.ok(mesh.indices.length > 300, `${name}: gerou triângulos`);
    assert.equal(r.open, 0, `${name}: arestas abertas`);
    assert.equal(r.badWinding, 0, `${name}: triângulos virados`);
  }
});

test('formas por contorno inválidas explicam o problema', () => {
  const bad = [
    [{ type: 'profile', points: [[0, 0], [1, 0]], h: 1 }, /3 a 256 pontos/],
    [{ type: 'profile', points: [[0, 0], [1, 0], [1, 0], [0, 1]], h: 1 }, /repete o ponto anterior/],
    [{ type: 'profile', points: [[0, 0], [1, 0], [0, 1], [0, 0]], h: 1 }, /fecha repetindo o primeiro ponto/],
    [{ type: 'profile', points: [[0, 0], [1, 0], [0, 1]] }, /'h' é obrigatório/],
    [{ type: 'lathe', points: [[0, 1], [2, 1], [2, 0]] }, /começa e termina no eixo/],
    [{ type: 'lathe', points: [[0, 0], [1, -1], [2, 0]] }, /ρ negativo/],
    [{ type: 'lathe', closed: true, points: [[0, 0], [1, 1], [2, 1]] }, /não pode tocar o eixo/],
    [{ type: 'tube', points: [[0, 0, 0], [1, 0, 0]], radii: [1] }, /um raio por ponto/],
    [{ type: 'tube', points: [[0, 0, 0], [1, 0]], r: 1 }, /3 coordenadas/],
  ];
  for (const [tree, re] of bad) assert.throws(() => compile(tree), re, JSON.stringify(tree));
});
```

- [ ] **Passo 2: Rodar e ver falhar**

Run: `node --test tests/sdfProfile.test.js`
Expected: FAIL — o teste não carrega (`ERR_MODULE_NOT_FOUND`: `src/clay/sdf/polygon.js`).

- [ ] **Passo 3: O polígono 2D** — filete dos cantos, distância com sinal e caixa.

```js file=src/clay/sdf/polygon.js
// Contornos 2D das formas por perfil (Fase 4.1): o filete dos cantos e a distância exata a um polígono.
//  - filletPolygon: troca cada canto por um arco tangente aos dois lados (convexo tira a ponta; côncavo enche o canto,
//    como a massa que o dedo alisa por dentro — QPG2, QPL4), com o raio limitado para os arcos vizinhos não se
//    cruzarem (cada arco usa no máximo metade de cada lado).
//  - polygonDistance: distância assinada exata (negativa dentro) de iq ("sdPolygon", iquilezles.org/articles/
//    distfunctions2d): o mínimo das distâncias aos lados e o sinal pelo número de cruzamentos. 1-Lipschitz.
//  - latheOutline: o meridiano do torno (polilinha de eixo a eixo) espelhado no eixo, fechando o polígono cujo
//    lado sobre o eixo some — a distância ao sólido de revolução é a distância 2D em (x, ρ).
// Tudo em Float64Array e closures sem alocar por amostra (o marching cubes chama milhões de vezes).

/** Segmentos de cada arco de filete. */
export const FILLET_SEGMENTS = 6;

/**
 * Polígono fechado com os cantos arredondados.
 * @param {number[][]} points [[x, y], ...] sem repetir o primeiro no fim (horário ou anti-horário)
 * @param {number} radius raio pedido (cada canto usa o menor entre ele e o que cabe nos dois lados)
 * @param {number} [segments]
 * @returns {number[][]} novo contorno
 */
export function filletPolygon(points, radius, segments = FILLET_SEGMENTS) {
  const n = points.length;
  if (!(radius > 0) || n < 3) return points.map((p) => [p[0], p[1]]);
  const out = [];
  for (let i = 0; i < n; i++) {
    const p0 = points[(i + n - 1) % n];
    const p1 = points[i];
    const p2 = points[(i + 1) % n];
    let ax = p0[0] - p1[0];
    let ay = p0[1] - p1[1];
    const la = Math.hypot(ax, ay);
    let bx = p2[0] - p1[0];
    let by = p2[1] - p1[1];
    const lb = Math.hypot(bx, by);
    ax /= la;
    ay /= la;
    bx /= lb;
    by /= lb;
    const cos = Math.max(-1, Math.min(1, ax * bx + ay * by));
    const theta = Math.acos(cos); // ângulo entre os dois lados, no vértice
    if (theta > Math.PI - 1e-6 || theta < 1e-6) {
      out.push([p1[0], p1[1]]); // alinhado (sem canto) ou ponta degenerada
      continue;
    }
    const tanHalf = Math.tan(theta / 2);
    const r = Math.min(radius, 0.5 * Math.min(la, lb) * tanHalf);
    if (r <= 1e-9) {
      out.push([p1[0], p1[1]]);
      continue;
    }
    const tl = r / tanHalf; // distância do vértice aos pontos de tangência
    const t0x = p1[0] + ax * tl;
    const t0y = p1[1] + ay * tl;
    const t1x = p1[0] + bx * tl;
    const t1y = p1[1] + by * tl;
    // Centro na bissetriz, dentro da cunha entre os dois lados.
    let hx = ax + bx;
    let hy = ay + by;
    const lh = Math.hypot(hx, hy);
    hx /= lh;
    hy /= lh;
    const dc = r / Math.sin(theta / 2);
    const cx = p1[0] + hx * dc;
    const cy = p1[1] + hy * dc;
    const a0 = Math.atan2(t0y - cy, t0x - cx);
    let da = Math.atan2(t1y - cy, t1x - cx) - a0;
    while (da > Math.PI) da -= 2 * Math.PI;
    while (da < -Math.PI) da += 2 * Math.PI;
    for (let k = 0; k <= segments; k++) {
      const a = a0 + (da * k) / segments;
      out.push([cx + r * Math.cos(a), cy + r * Math.sin(a)]);
    }
  }
  return out;
}

/** Área com sinal (positiva = anti-horário). */
export function signedArea(points) {
  let a = 0;
  for (let i = 0, j = points.length - 1; i < points.length; j = i++) {
    a += points[j][0] * points[i][1] - points[i][0] * points[j][1];
  }
  return a / 2;
}

/**
 * Distância assinada exata a um polígono fechado (negativa dentro).
 * @param {number[][]} points [[x, y], ...]
 * @returns {(x:number, y:number) => number}
 */
export function polygonDistance(points) {
  const n = points.length;
  const vx = new Float64Array(n);
  const vy = new Float64Array(n);
  const ex = new Float64Array(n);
  const ey = new Float64Array(n);
  const inv = new Float64Array(n);
  for (let i = 0; i < n; i++) {
    vx[i] = points[i][0];
    vy[i] = points[i][1];
  }
  for (let i = 0, j = n - 1; i < n; j = i++) {
    ex[i] = vx[j] - vx[i];
    ey[i] = vy[j] - vy[i];
    const l2 = ex[i] * ex[i] + ey[i] * ey[i];
    inv[i] = l2 > 0 ? 1 / l2 : 0;
  }
  return (px, py) => {
    let d = Infinity;
    let s = 1;
    for (let i = 0, j = n - 1; i < n; j = i++) {
      const wx = px - vx[i];
      const wy = py - vy[i];
      let h = (wx * ex[i] + wy * ey[i]) * inv[i];
      h = h < 0 ? 0 : h > 1 ? 1 : h;
      const bx = wx - ex[i] * h;
      const by = wy - ey[i] * h;
      const b2 = bx * bx + by * by;
      if (b2 < d) d = b2;
      // Cruzamento da semirreta horizontal pelo ponto (a regra par/ímpar de iq).
      const c1 = py >= vy[i];
      const c2 = py < vy[j];
      const c3 = ex[i] * wy > ey[i] * wx;
      if ((c1 && c2 && c3) || (!c1 && !c2 && !c3)) s = -s;
    }
    return s * Math.sqrt(d);
  };
}

/**
 * Polígono do meridiano de um torno: a polilinha (x, ρ) vai de um ponto no eixo (ρ = 0) a outro e é espelhada em
 * ρ → −ρ (sem repetir os pontos do eixo); com `closed`, é um anel que não toca o eixo e fica como está.
 * @param {number[][]} points [[x, ρ], ...]
 * @param {boolean} closed
 * @returns {number[][]}
 */
export function latheOutline(points, closed) {
  if (closed) return points.map((p) => [p[0], p[1]]);
  const out = points.map((p) => [p[0], p[1]]);
  for (let i = points.length - 2; i >= 1; i--) out.push([points[i][0], -points[i][1]]);
  return out;
}
```

- [ ] **Passo 4: Leitores e limites das formas novas**

Em `src/clay/sdf/params.js`, trocar:

```
  'sphere', 'ellipsoid', 'capsule', 'roundCone', 'roundBox', 'cylinder', 'torus', 'cone', 'spiral',
]);

/** Operações sobre filhos. */
```

por:

```
  'sphere', 'ellipsoid', 'capsule', 'roundCone', 'roundBox', 'cylinder', 'torus', 'cone', 'spiral',
  'profile', 'lathe', 'tube',
]);

/** Limites de pontos das formas por contorno (perfil e torno) e por polilinha (tubo). */
export const MAX_POINTS = 256;

/** Menor lado aceito num contorno ou polilinha (unidades locais): lado mais curto é ponto repetido. */
export const MIN_EDGE = 1e-4;

/** Operações sobre filhos. */
```

Em `src/clay/sdf/params.js`, trocar:

```

/** Filho único obrigatório (objeto de nó). */
```

por:

```

/**
 * Lista de pontos com `dim` coordenadas finitas ([[x, y], ...] ou [[x, y, z], ...]), entre `min` e MAX_POINTS pontos,
 * sem dois pontos seguidos a menos de MIN_EDGE (e, se `closed`, sem o último colado no primeiro).
 * @returns {number[][]} cópia
 */
export function readPoints(node, key, path, dim, min, closed) {
  const v = node[key];
  if (!Array.isArray(v) || v.length < min || v.length > MAX_POINTS) {
    fail(path, `'${key}' precisa ser uma lista de ${min} a ${MAX_POINTS} pontos`);
  }
  const out = v.map((p, i) => {
    if (!(Array.isArray(p) || ArrayBuffer.isView(p)) || p.length !== dim) fail(path, `'${key}[${i}]' precisa ter ${dim} coordenadas`);
    const q = Array.from(p, Number);
    if (!q.every(Number.isFinite)) fail(path, `'${key}[${i}]' tem coordenada não finita (${JSON.stringify(Array.from(p))})`);
    return q;
  });
  const gap = (a, b) => Math.hypot(...a.map((c, k) => c - b[k]));
  for (let i = 1; i < out.length; i++) {
    if (gap(out[i], out[i - 1]) < MIN_EDGE) fail(path, `'${key}[${i}]' repete o ponto anterior`);
  }
  if (closed && gap(out[0], out[out.length - 1]) < MIN_EDGE) fail(path, `'${key}' fecha repetindo o primeiro ponto (deixe o último de fora)`);
  return out;
}

/** Filho único obrigatório (objeto de nó). */
```

- [ ] **Passo 5: A função suporte de cada uma**

Em `src/clay/sdf/bounds.js`, trocar:

```
import {
  MAX_DEPTH, fail, readChild, readChildren, readNonNegative, readNumber, readPositive, readPositiveVec3,
  readTransform, readType, readVec3,
```

por:

```
import {
  MAX_DEPTH, fail, readChild, readChildren, readNonNegative, readNumber, readPoints, readPositive, readPositiveVec3,
  readTransform, readType, readVec3,
```

Em `src/clay/sdf/bounds.js`, trocar:

```
    }
    default:
```

por:

```
    }
    case 'profile': {
      // O filete fica dentro do fecho dos pontos originais (tira a ponta dos convexos e enche os côncavos entre os
      // pontos de tangência, que estão sobre os lados): o suporte dos pontos é conservador.
      const pts = readPoints(node, 'points', path, 2, 3, true);
      const h = readPositive(node, 'h', path);
      return (ux, uy, uz) => {
        let m = -Infinity;
        for (const p of pts) m = Math.max(m, ux * p[0] + uy * p[1]);
        return m + Math.abs(uz) * h;
      };
    }
    case 'lathe': {
      // Revolução em volta de X: cada ponto (x, ρ) varre um círculo; o suporte é x·ux + ρ·|(uy, uz)|.
      const pts = readPoints(node, 'points', path, 2, node.closed === true ? 3 : 2, node.closed === true);
      return (ux, uy, uz) => {
        const q = Math.hypot(uy, uz);
        let m = -Infinity;
        for (const p of pts) m = Math.max(m, ux * p[0] + q * Math.abs(p[1]));
        return m;
      };
    }
    case 'tube': {
      // Casca convexa das esferas das pontas de cada trecho.
      const pts = readPoints(node, 'points', path, 3, 2, false);
      const radii = Array.isArray(node.radii) ? node.radii.map(Number) : pts.map(() => readPositive(node, 'r', path));
      return (ux, uy, uz) => {
        let m = -Infinity;
        pts.forEach((p, i) => {
          m = Math.max(m, ux * p[0] + uy * p[1] + uz * p[2] + radii[i]);
        });
        return m;
      };
    }
    default:
```

- [ ] **Passo 6: As distâncias** — `profile`, `lathe` e `tube` no compilador de formas.

Em `src/clay/sdf/shapes.js`, trocar:

```
// engrossada e extrudada com o "opExtrusion" arredondado de iq.
// Todas aceitam pos/rot/scale (rígida + escala uniforme, então o SDF continua exato) e mat.
```

por:

```
// engrossada e extrudada com o "opExtrusion" arredondado de iq.
// Fase 4.1 (armas): o perfil recortado e extrudado (polígono em XY com os cantos em filete, "opExtrusion"
// arredondado de iq), o torno (polígono do meridiano girado em volta de X) e o tubo (cones arredondados encadeados
// por uma polilinha) — formas de peça de massa cortada à mão (QPG2, QPL4); contornos em src/clay/sdf/polygon.js.
// Todas aceitam pos/rot/scale (rígida + escala uniforme, então o SDF continua exato) e mat.
```

Em `src/clay/sdf/shapes.js`, trocar:

```
import {
  fail, readInteger, readMaterial, readNonNegative, readPositive, readPositiveVec3, readTransform, readVec3,
} from './params.js';

```

por:

```
import {
  fail, readInteger, readMaterial, readNonNegative, readPoints, readPositive, readPositiveVec3, readTransform, readVec3,
} from './params.js';
import { filletPolygon, latheOutline, polygonDistance } from './polygon.js';

```

Em `src/clay/sdf/shapes.js`, trocar:

```
}

/**
 * Compila uma forma básica.
```

por:

```
}

/**
 * Perfil recortado: polígono em XY (`points`) com os cantos em filete de raio `corner`, extrudado em Z com
 * meia-espessura `h` e as arestas da extrusão arredondadas com raio `round`. O contorno encolhido de `round` usa
 * d2 + round, que é a distância exata a ele porque os cantos convexos ficam com raio ≥ round (o filete é forçado a
 * pelo menos `round`); depois tudo engorda de `round` — a silhueta lateral é o polígono com os cantos em filete.
 */
function profileShape(node, t, mat, path) {
  const points = readPoints(node, 'points', path, 2, 3, true);
  const h = readPositive(node, 'h', path);
  const rd = Math.min(readNonNegative(node, 'round', path, 0), h);
  const corner = Math.max(readNonNegative(node, 'corner', path, 0), rd);
  const outline = filletPolygon(points, corner);
  const d2 = polygonDistance(outline);
  const eh = h - rd;
  let cx = 0;
  let cy = 0;
  for (const p of points) {
    cx += p[0];
    cy += p[1];
  }
  cx /= points.length;
  cy /= points.length;
  let reach = 0;
  for (const p of points) reach = Math.max(reach, Math.hypot(p[0] - cx, p[1] - cy));
  return exactShape((x, y, z) => {
    toLocal(t, x, y, z);
    const wx = d2(LP[0], LP[1]) + rd;
    const wy = Math.abs(LP[2]) - eh;
    const mx = wx > 0 ? wx : 0;
    const my = wy > 0 ? wy : 0;
    const inner = wx > wy ? wx : wy;
    return t.s * ((inner < 0 ? inner : 0) + Math.sqrt(mx * mx + my * my) - rd);
  }, mat, sphereBound(t, cx, cy, 0, Math.hypot(reach, h), 1));
}

/**
 * Torno: meridiano (x, ρ) girado em volta do eixo X local. `points` vai de um ponto no eixo (ρ = 0) a outro e é
 * espelhado no eixo; com `closed: true` é um anel fechado que não toca o eixo. Cantos em filete de raio `corner`.
 * Distância exata = distância 2D ao meridiano em (x, √(y² + z²)).
 */
function latheShape(node, t, mat, path) {
  const closed = node.closed === true;
  const points = readPoints(node, 'points', path, 2, closed ? 3 : 2, closed);
  for (let i = 0; i < points.length; i++) {
    if (points[i][1] < 0) fail(path, `'points[${i}]' tem ρ negativo (o meridiano fica em ρ ≥ 0)`);
  }
  if (closed) {
    if (points.some((p) => p[1] === 0)) fail(path, "anel 'closed' não pode tocar o eixo (ρ = 0)");
  } else if (points[0][1] !== 0 || points[points.length - 1][1] !== 0) {
    fail(path, "'points' do torno aberto começa e termina no eixo (ρ = 0)");
  }
  const outline = filletPolygon(latheOutline(points, closed), readNonNegative(node, 'corner', path, 0));
  const d2 = polygonDistance(outline);
  let x0 = Infinity;
  let x1 = -Infinity;
  let rmax = 0;
  for (const p of points) {
    x0 = Math.min(x0, p[0]);
    x1 = Math.max(x1, p[0]);
    rmax = Math.max(rmax, p[1]);
  }
  return exactShape((x, y, z) => {
    toLocal(t, x, y, z);
    const ly = LP[1];
    const lz = LP[2];
    return t.s * d2(LP[0], Math.sqrt(ly * ly + lz * lz));
  }, mat, sphereBound(t, (x0 + x1) / 2, 0, 0, Math.hypot((x1 - x0) / 2, rmax), 1));
}

/**
 * Tubo: polilinha 3D (`points`) com raio `r` ou um raio por ponto (`radii`); cada trecho é um cone arredondado
 * exato (casca das duas esferas das pontas) e a distância é o menor dos trechos — cobrinha de massa, guarda-mato,
 * alavancas.
 */
function tubeShape(node, t, mat, path) {
  const points = readPoints(node, 'points', path, 3, 2, false);
  let radii;
  if (node.radii !== undefined) {
    if (!Array.isArray(node.radii) || node.radii.length !== points.length) {
      fail(path, "'radii' precisa ter um raio por ponto");
    }
    radii = node.radii.map((r, i) => readPositive({ r }, 'r', `${path}.radii[${i}]`));
  } else {
    const r = readPositive(node, 'r', path);
    radii = points.map(() => r);
  }
  const segs = [];
  for (let i = 0; i < points.length - 1; i++) {
    const a = points[i];
    const b = points[i + 1];
    const ra = radii[i];
    const rb = radii[i + 1];
    const bax = b[0] - a[0];
    const bay = b[1] - a[1];
    const baz = b[2] - a[2];
    const l2 = bax * bax + bay * bay + baz * baz;
    const rr = ra - rb;
    const a2 = l2 - rr * rr;
    // Uma esfera engole a outra: o trecho é só a esfera maior.
    if (a2 <= 1e-9 * Math.max(l2, ra * ra, rb * rb)) {
      segs.push(ra >= rb ? { sphere: true, x: a[0], y: a[1], z: a[2], r: ra } : { sphere: true, x: b[0], y: b[1], z: b[2], r: rb });
      continue;
    }
    segs.push({
      sphere: false, ax: a[0], ay: a[1], az: a[2], bax, bay, baz, l2, il2: 1 / l2, rr, a2, ra, rb,
      krr: Math.sign(rr) * rr * rr,
    });
  }
  const n = segs.length;
  const dist = (lx, ly, lz) => {
    let best = Infinity;
    for (let i = 0; i < n; i++) {
      const g = segs[i];
      let v;
      if (g.sphere) {
        const dx = lx - g.x;
        const dy = ly - g.y;
        const dz = lz - g.z;
        v = Math.sqrt(dx * dx + dy * dy + dz * dz) - g.r;
      } else {
        const pax = lx - g.ax;
        const pay = ly - g.ay;
        const paz = lz - g.az;
        const yy = pax * g.bax + pay * g.bay + paz * g.baz;
        const zz = yy - g.l2;
        const wx = pax * g.l2 - g.bax * yy;
        const wy = pay * g.l2 - g.bay * yy;
        const wz = paz * g.l2 - g.baz * yy;
        const x2 = wx * wx + wy * wy + wz * wz;
        const y2 = yy * yy * g.l2;
        const z2 = zz * zz * g.l2;
        const kk = g.krr * x2;
        if (Math.sign(zz) * g.a2 * z2 > kk) v = Math.sqrt(x2 + z2) * g.il2 - g.rb;
        else if (Math.sign(yy) * g.a2 * y2 < kk) v = Math.sqrt(x2 + y2) * g.il2 - g.ra;
        else v = (Math.sqrt(x2 * g.a2 * g.il2) + yy * g.rr) * g.il2 - g.ra;
      }
      if (v < best) best = v;
    }
    return best;
  };
  const min = [Infinity, Infinity, Infinity];
  const max = [-Infinity, -Infinity, -Infinity];
  points.forEach((p, i) => {
    for (let k = 0; k < 3; k++) {
      min[k] = Math.min(min[k], p[k] - radii[i]);
      max[k] = Math.max(max[k], p[k] + radii[i]);
    }
  });
  const c = min.map((v, k) => (v + max[k]) / 2);
  return exactShape((x, y, z) => {
    toLocal(t, x, y, z);
    return t.s * dist(LP[0], LP[1], LP[2]);
  }, mat, sphereBound(t, c[0], c[1], c[2], Math.hypot((max[0] - min[0]) / 2, (max[1] - min[1]) / 2, (max[2] - min[2]) / 2), 1));
}

/**
 * Compila uma forma básica.
```

Em `src/clay/sdf/shapes.js`, trocar:

```
    }
    default:
```

por:

```
    }
    case 'profile':
      return profileShape(node, t, mat, path);
    case 'lathe':
      return latheShape(node, t, mat, path);
    case 'tube':
      return tubeShape(node, t, mat, path);
    default:
```

- [ ] **Passo 7: Rodar e ver passar**

Run: `node --test tests/sdfProfile.test.js`
Expected: PASS
Run: `npm test`
Expected: PASS — 302 testes passando.

- [ ] **Passo final: Commit** (só com o pedido do usuário)

```bash
git add src/clay/sdf tests/sdfProfile.test.js
git commit -m "MASSACRE 4.1: formas novas do SDF (perfil recortado, torno e tubo)" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Tarefa 2: Mãos de 4 dedos com rig

**Files:**
- Create: `src/data/hands.js`, `src/characters/hands/handShape.js`, `src/characters/hands/handSkin.js`, `src/characters/hands/armband.js`, `src/characters/hands/handRig.js`, `src/characters/hands/handLibrary.js`, `tests/clayHands.test.js`

Decisão do usuário: três dedos grossos e o polegar, como os humanos da Aardman (CMH3, CMH14, CMH16, CMH19; mãos simples CMH15, CMH18). A mão direita é uma árvore SDF (palma de caixa arredondada de 3,0 × 1,4 × 3,2 u, dedos de raio ~0,6 u com três falanges, polegar de 0,68 u saindo perto do pulso, antebraço em cone arredondado de 1,25 u no pulso a 1,65 u no cotovelo e 11 u de comprimento), com o vinco da costura onde cada dedo sai da palma. O rig tem 14 ossos (antebraço, mão, 3 × 3 falanges, polegar em 3) com pesos pela distância de cada vértice ao segmento de cada osso (queda suave, os 4 maiores, normalizados) numa `SkinnedMesh`; o boil do `ClayMaterial` age na pose de repouso (antes do skinning) e as digitais ficam no espaço do objeto em repouso, então a massa dobra com o dedo e as marcas vão junto. As poses (`empunhadura`, `apoio`, `guardaMao`, `bomba`, `faca`, `aberta`) são ângulos em dados, dentro dos limites das juntas. A esquerda é a direita espelhada em Z (malha, ossos e giros). `ClayArm.place` põe o pulso na âncora e aponta o antebraço para o cotovelo. A braçadeira do time é uma faixa torneada a 55% do antebraço; a cor é a primeira do time (primária, secundária, acento) com ΔE ≥ 30 para a massa do braço — no braço terracota do boneco de referência, a do TR vira o laranja. O serviço `handModels` (`HandLibrary`) gera a malha da mão e a da braçadeira uma vez (SDF, cache) e os braços dividem as geometrias de cada lado.

- [ ] **Passo 1: Escrever os testes** — ossos e cadeias, malha fechada do tamanho do desenho, pesos, limites das poses, espelho, braço na âncora e a cor da braçadeira.

```js file=tests/clayHands.test.js
// Testes das mãos de massinha de 4 dedos (Fase 4.1; docs/phases/phase-4.md, seção 4.1, "Mãos de 4 dedos" e "Testes"):
// o esqueleto de 14 ossos, os pesos do skinning (normalizados, no máximo 4, cada vértice dos dedos puxado pelo seu
// osso e nenhum dedo arrastando o vizinho), as poses dentro dos limites das juntas, o espelho da esquerda (malha,
// pesos e giros), o braço posto numa âncora (pulso no lugar, antebraço apontando para o cotovelo) e a cor da braçadeira.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import * as THREE from 'three';
import { bounds, compile } from '../src/clay/sdf/nodes.js';
import { polygonize } from '../src/clay/sdf/marchingCubes.js';
import { meshToGeometry } from '../src/clay/sdf/sdfMesher.js';
import { ARMBAND, HAND, HAND_LIMITS, HAND_POSES } from '../src/data/hands.js';
import { PALETTE, TEAM_COLORS } from '../src/data/palette.js';
import { handBones, handTree, WRIST } from '../src/characters/hands/handShape.js';
import { computeSkinWeights, mirrorRotations, poseRotations } from '../src/characters/hands/handSkin.js';
import { ClayArm, mirrorGeometry, prepareArmGeometry } from '../src/characters/hands/handRig.js';
import { armbandColor, deltaE, hexToLab } from '../src/characters/hands/armband.js';
import { meshReport } from './sdfTestUtils.js';

// Malha da mão numa grade mais grossa que a do jogo (os pesos não dependem da resolução; o teste fica rápido).
const tree = handTree();
const data = polygonize(compile(tree), bounds(tree), { resolution: 90 });
const source = meshToGeometry(data, 'mao-teste');

function segmentT(p, h, t) {
  const d = [t[0] - h[0], t[1] - h[1], t[2] - h[2]];
  const l2 = d[0] ** 2 + d[1] ** 2 + d[2] ** 2;
  return ((p[0] - h[0]) * d[0] + (p[1] - h[1]) * d[1] + (p[2] - h[2]) * d[2]) / l2;
}
function segmentDist(p, h, t) {
  const s = Math.max(0, Math.min(1, segmentT(p, h, t)));
  return Math.hypot(p[0] - h[0] - s * (t[0] - h[0]), p[1] - h[1] - s * (t[1] - h[1]), p[2] - h[2] - s * (t[2] - h[2]));
}

test('mãos: 14 ossos em ordem, cadeias certas e falanges emendadas', () => {
  const bones = handBones();
  assert.equal(bones.length, 14);
  const seen = new Set();
  for (const b of bones) {
    if (b.parent) assert.ok(seen.has(b.parent), `${b.name}: o pai ${b.parent} vem antes`);
    seen.add(b.name);
  }
  assert.deepEqual([...new Set(bones.map((b) => b.chain))].sort(), ['braco', 'dedo1', 'dedo2', 'dedo3', 'polegar']);
  assert.deepEqual(bones[0].tail, [...WRIST], 'o antebraço termina no pulso');
  for (const b of bones) {
    const parent = bones.find((x) => x.name === b.parent);
    if (parent && parent.chain === b.chain && b.chain !== 'braco') assert.deepEqual(b.head, parent.tail, `${b.name} emenda no pai`);
  }
  // A mão fica com ~7 u do pulso à ponta do dedo do meio (a medida da empunhadura da Glock).
  const tip = bones.find((b) => b.name === 'dedo2_3').tail;
  assert.ok(Math.abs(tip[0] - WRIST[0] - 7) < 0.8, `mão de ${(tip[0] - WRIST[0]).toFixed(2)} u`);
});

test('mãos: a malha da mão é fechada e tem o tamanho do desenho', () => {
  const rep = meshReport(data);
  assert.equal(rep.open, 0, 'estanque');
  assert.equal(rep.badWinding, 0, 'enrolamento de fora');
  const box = new THREE.Box3().setFromBufferAttribute(source.attributes.position);
  assert.ok(box.min.x < 0.5 - HAND.forearm.elbowRadius + 0.3, 'começa no cotovelo');
  assert.ok(box.max.x > WRIST[0] + 6, 'vai até a ponta dos dedos');
});

test('mãos: pesos normalizados, no máximo 4 ossos, cada dedo puxado pelos seus ossos', () => {
  const bones = handBones();
  const P = source.attributes.position.array;
  const { skinIndex, skinWeight } = computeSkinWeights(P, bones);
  const n = P.length / 3;
  let fingerChecked = 0;
  for (let v = 0; v < n; v++) {
    let sum = 0;
    for (let k = 0; k < 4; k++) {
      const w = skinWeight[v * 4 + k];
      assert.ok(w >= 0 && w <= 1 + 1e-6);
      assert.ok(skinIndex[v * 4 + k] < bones.length);
      sum += w;
    }
    assert.ok(Math.abs(sum - 1) < 1e-5, `vértice ${v}: soma ${sum}`);
    // Vértices no meio de uma falange (bem longe das outras cadeias): o maior peso é dessa falange, e nenhum osso de
    // outro dedo puxa o vértice.
    const p = [P[v * 3], P[v * 3 + 1], P[v * 3 + 2]];
    for (const b of bones) {
      if (b.chain === 'braco' || !/_[23]$/.test(b.name)) continue;
      const t = segmentT(p, b.head, b.tail);
      if (t < 0.3 || t > 0.7 || segmentDist(p, b.head, b.tail) > b.radius + 0.12) continue;
      const others = bones.filter((o) => o.chain !== b.chain && o.chain !== 'braco');
      if (others.some((o) => segmentDist(p, o.head, o.tail) < o.radius + 0.4)) continue;
      let best = -1;
      let bw = -1;
      for (let k = 0; k < 4; k++) {
        if (skinWeight[v * 4 + k] > bw) {
          bw = skinWeight[v * 4 + k];
          best = skinIndex[v * 4 + k];
        }
        const chain = bones[skinIndex[v * 4 + k]].chain;
        if (skinWeight[v * 4 + k] > 0) assert.ok(chain === b.chain || chain === 'braco', `vértice ${v}: ${b.chain} puxado por ${chain}`);
      }
      assert.equal(bones[best].name, b.name, `vértice ${v} no meio de ${b.name}`);
      fingerChecked++;
    }
  }
  assert.ok(fingerChecked > 50, `vértices de falange conferidos: ${fingerChecked}`);
});

test('mãos: as poses ficam dentro dos limites das juntas', () => {
  const inRange = (v, [lo, hi], what) => assert.ok(v >= lo - 1e-9 && v <= hi + 1e-9, `${what}: ${v} fora de [${lo}, ${hi}]`);
  for (const [name, pose] of Object.entries(HAND_POSES)) {
    const r = poseRotations(name);
    assert.equal(Object.keys(r).length, 14, name);
    for (const f of HAND.fingers) {
      for (let i = 1; i <= 3; i++) inRange(-r[`${f.id}_${i}`][2], HAND_LIMITS.flex, `${name}.${f.id}_${i}`);
      inRange(r[`${f.id}_1`][1], HAND_LIMITS.spread, `${name}.${f.id} abertura`);
    }
    inRange(-r.polegar_1[1], HAND_LIMITS.thumbYaw, `${name}.polegar giro`);
    inRange(r.mao[1], HAND_LIMITS.wrist, `${name}.pulso desvio`);
    inRange(-r.mao[2], HAND_LIMITS.wrist, `${name}.pulso flexão`);
    // A pose fechada dobra mais que a aberta (empunhadura e faca fecham os dedos).
    if (name === 'faca') assert.ok(pose.fingers.every((f) => f[0] > HAND_POSES.aberta.fingers[0][0]));
  }
  // Fora do limite é preso ao limite.
  const wild = { ...HAND_POSES.aberta, fingers: [[9, 9, 9], [9, 9, 9], [9, 9, 9]] };
  assert.equal(poseRotations(wild).dedo1_1[2], -HAND_LIMITS.flex[1]);
  assert.throws(() => poseRotations('pose-que-nao-existe'), /pose de mão desconhecida/);
});

test('mãos: a esquerda é a direita espelhada (malha, pesos e giros)', () => {
  const right = prepareArmGeometry(source, 'direita');
  const left = prepareArmGeometry(source, 'esquerda');
  const pr = right.attributes.position;
  const pl = left.attributes.position;
  assert.equal(pr.count, pl.count);
  for (let i = 0; i < pr.count; i += 7) {
    assert.equal(pl.getX(i), pr.getX(i));
    assert.equal(pl.getY(i), pr.getY(i));
    assert.equal(pl.getZ(i), -pr.getZ(i));
    assert.equal(left.attributes.normal.getZ(i), -right.attributes.normal.getZ(i));
  }
  // Os pesos acompanham o espelho: o mesmo vértice, o mesmo osso.
  for (let i = 0; i < pr.count * 4; i += 13) {
    assert.equal(left.attributes.skinIndex.array[i], right.attributes.skinIndex.array[i]);
    assert.ok(Math.abs(left.attributes.skinWeight.array[i] - right.attributes.skinWeight.array[i]) < 1e-6);
  }
  // O espelho inverte o enrolamento (a malha continua virada para fora).
  const mirrored = { positions: mirrorGeometry(source).attributes.position.array, normals: mirrorGeometry(source).attributes.normal.array, indices: mirrorGeometry(source).index.array };
  assert.equal(meshReport(mirrored).badWinding, 0);
  const rot = poseRotations('empunhadura');
  const m = mirrorRotations(rot);
  for (const k of Object.keys(rot)) assert.deepEqual(m[k], [-rot[k][0], -rot[k][1], rot[k][2]]);
});

test('mãos: o braço vai para a âncora — pulso no lugar, antebraço apontando para o cotovelo, dedos fechando', () => {
  const geometry = prepareArmGeometry(source, 'direita');
  const arm = new ClayArm({ geometry, side: 'direita', color: PALETTE.terracotta });
  const tip = () => {
    arm.mesh.updateMatrixWorld(true);
    return new THREE.Vector3(HAND.fingers[1].phalanges[2], 0, 0).applyMatrix4(arm.bones.dedo2_3.matrixWorld);
  };
  const middleKnuckle = () => {
    arm.mesh.updateMatrixWorld(true);
    return new THREE.Vector3().setFromMatrixPosition(arm.bones.dedo2_2.matrixWorld);
  };
  arm.setPose('aberta');
  const wrist = new THREE.Vector3(5, -4, -12);
  const handQuat = new THREE.Quaternion().setFromEuler(new THREE.Euler(0.4, -0.3, 0.2));
  const elbow = new THREE.Vector3(15, -18, 6);
  arm.place(wrist, handQuat, elbow);
  arm.mesh.updateMatrixWorld(true);
  const w = new THREE.Vector3();
  const e = new THREE.Vector3();
  arm.joints(w, e);
  assert.ok(w.distanceTo(wrist) < 1e-9, 'pulso na âncora');
  assert.ok(Math.abs(w.distanceTo(e) - HAND.forearm.length) < 1e-9, 'antebraço com o comprimento');
  const toElbow = elbow.clone().sub(wrist).normalize();
  assert.ok(e.clone().sub(w).normalize().dot(toElbow) > 1 - 1e-9, 'antebraço na direção do cotovelo');
  const handWorld = new THREE.Vector3().setFromMatrixPosition(arm.bones.mao.matrixWorld);
  assert.ok(handWorld.distanceTo(wrist) < 1e-9, 'o osso da mão começa no pulso');
  // A mão fica na rotação da âncora (com a pose de pulso "aberta", que é neutra).
  const q = new THREE.Quaternion().setFromRotationMatrix(arm.bones.mao.matrixWorld);
  assert.ok(Math.abs(Math.abs(q.dot(handQuat)) - 1) < 1e-9, 'rotação da âncora');
  // Fechar a mão: o nó do meio desce para o lado da palma (−Y da mão), a ponta volta para perto do pulso e fica do
  // lado da palma.
  const open = tip();
  const openKnuckle = middleKnuckle();
  arm.setPose('faca');
  arm.place(wrist, handQuat, elbow);
  const fist = tip();
  const palmDown = new THREE.Vector3(0, -1, 0).applyQuaternion(handQuat);
  assert.ok(middleKnuckle().sub(openKnuckle).dot(palmDown) > 0.8, 'o nó do meio desce para a palma');
  assert.ok(fist.distanceTo(wrist) < open.distanceTo(wrist) - 3, 'a ponta volta para perto do pulso');
  assert.ok(fist.clone().sub(wrist).dot(palmDown) > 0, 'e fica do lado da palma');
  arm.setArmband(null);
  arm.dispose();
  geometry.dispose();
});

test('braçadeira: a cor do time que mais se destaca da massa do braço', () => {
  assert.equal(deltaE('#C8553D', '#C8553D'), 0);
  assert.ok(Math.abs(deltaE('#C8553D', '#2F6DB5') - deltaE('#2F6DB5', '#C8553D')) < 1e-12);
  const [L] = hexToLab('#FFFFFF');
  assert.ok(Math.abs(L - 100) < 1e-3, 'branco tem L* 100');
  // Braço terracota (o boneco de referência): a braçadeira TR não pode ser terracota; a CT é o azul.
  assert.equal(armbandColor('tr', PALETTE.terracotta), TEAM_COLORS.tr.secondary);
  assert.equal(armbandColor('ct', PALETTE.terracotta), TEAM_COLORS.ct.primary);
  // Braço azul (um boneco da Tropa do Estúdio): a CT troca para a segunda cor.
  assert.equal(armbandColor('ct', PALETTE.blue), TEAM_COLORS.ct.secondary);
  assert.equal(armbandColor(null, PALETTE.terracotta), null);
  for (const team of ['tr', 'ct']) {
    for (const arm of [PALETTE.terracotta, PALETTE.blue, PALETTE.clayWhite, '#6B4F3A']) {
      assert.ok(deltaE(armbandColor(team, arm), arm) >= ARMBAND.minDelta, `${team} em ${arm}`);
    }
  }
});
```

- [ ] **Passo 2: Rodar e ver falhar**

Run: `node --test tests/clayHands.test.js`
Expected: FAIL — o teste não carrega (`ERR_MODULE_NOT_FOUND`: `src/data/hands.js`).

- [ ] **Passo 3: Números da mão, da braçadeira e das poses**

```js file=src/data/hands.js
// Mãos e antebraços de massinha do boneco (Fase 4.1; desenho em docs/phases/phase-4.md, seção 4.1, "Mãos de 4
// dedos"): três dedos e o polegar, grossos e arredondados como os humanos da Aardman (decisão do usuário, 2026-09-25;
// CMH3, CMH14, CMH16, CMH19 — poses de mão em massa; CMH15, CMH18 — mãos simples de massa). O viewmodel usa agora; a
// Fase 5 herda o modelo e o rig nos personagens. Unidades: u (polegada na escala do boneco).
// Referencial da mão direita (osso `mao`): origem no pulso, +X para as pontas dos dedos, +Y para as costas da mão,
// −Z para o lado do polegar (palma para baixo). A esquerda é a direita espelhada em Z.

const F = Object.freeze;

export const HAND = F({
  palm: F({ center: [1.72, 0, 0], half: [1.52, 0.72, 1.62], round: 0.62 }), // 3,0 × 1,4 × 3,2 u
  // Dedos (o primeiro é o do gatilho, do lado do polegar): base no nó do dedo, falanges ao longo de +X.
  fingers: F([
    F({ id: 'dedo1', base: [3.12, 0.08, -1.06], radius: 0.6, phalanges: F([1.2, 1.0, 0.86]) }),
    F({ id: 'dedo2', base: [3.2, 0.1, 0], radius: 0.63, phalanges: F([1.28, 1.06, 0.9]) }),
    F({ id: 'dedo3', base: [3.08, 0.08, 1.06], radius: 0.6, phalanges: F([1.14, 0.96, 0.82]) }),
  ]),
  // Polegar: sai da palma perto do pulso, do lado −Z, apontando para a frente e para fora.
  thumb: F({ id: 'polegar', base: [0.95, -0.22, -1.38], dir: [0.74, -0.14, -0.66], radius: 0.68, phalanges: F([1.25, 1.02, 0.86]) }),
  // Antebraço (osso `antebraco`: origem no cotovelo, +X para o pulso): cone arredondado.
  forearm: F({ length: 11, elbowRadius: 1.65, wristRadius: 1.25 }),
  // Nós dos dedos: vinco da costura onde o dedo sai da palma (a massa apertada no lugar).
  soft: 0.35,
  crease: F({ depth: 0.06, width: 0.14 }),
  knuckleSoft: 0.22,
  lumps: F({ amp: 0.025, freq: 0.5, octaves: 2 }),
  // Pesos do skinning: queda suave pela distância ao segmento do osso; os 4 maiores, normalizados.
  skin: F({ falloff: 0.55, influences: 4 }),
  mesh: F({ cell: 0.11, maxCells: 1400000, touchRadius: 0.5 }),
  // Massa do braço: a cor é a do boneco (terracota no boneco de referência; o criador da Fase 5 troca); o boil segue o
  // tamanho da mão (`objectSize`, u).
  clay: F({ roughness: 0.7, wetness: 0.36, objectSize: 9 }),
});

/**
 * Braçadeira do time no antebraço (seção 0.12): faixa de massa a 55% do antebraço, visível só com time. A cor é a do
 * time que mais se destaca da massa do braço: a primeira de `colors` (TEAM_COLORS) com diferença ΔE ≥ `minDelta` para a
 * massa, senão a mais distante — terracota não some no braço terracota do boneco de referência (vira o laranja).
 */
export const ARMBAND = F({
  at: 0.55, width: 1.7, thickness: 0.34, round: 0.3,
  colors: F(['primary', 'secondary', 'accent']),
  minDelta: 30,
  clay: F({ roughness: 0.66, wetness: 0.4, objectSize: 4 }),
  mesh: F({ cell: 0.06, maxCells: 600000, touchRadius: 0.3 }),
});

/**
 * Poses de mão (radianos). Cada dedo: [flexão da base, do meio, da ponta] — positivo dobra para a palma; `spread`
 * abre para os lados na base. Polegar: [giro na base em torno de +Y, flexão 1, flexão 2]. Pulso: [flexão, desvio].
 * A pose muda só na troca de pose (12/s, "em dois").
 */
export const HAND_POSES = F({
  aberta: F({ fingers: F([F([0.18, 0.22, 0.12]), F([0.2, 0.25, 0.14]), F([0.24, 0.28, 0.16])]), spread: F([-0.08, 0, 0.1]), thumb: F([0.15, 0.2, 0.12]), wrist: F([0, 0]) }),
  // Empunhadura da arma: o primeiro dedo esticado até o gatilho, os outros dois fechados em volta da empunhadura.
  empunhadura: F({ fingers: F([F([0.5, 0.95, 0.42]), F([1.38, 1.52, 0.86]), F([1.42, 1.5, 0.84])]), spread: F([-0.06, 0, 0.05]), thumb: F([0.62, 0.62, 0.38]), wrist: F([0, 0]) }),
  // Mão de apoio em concha por baixo da empunhadura (pistolas).
  apoio: F({ fingers: F([F([1.1, 1.2, 0.7]), F([1.16, 1.24, 0.72]), F([1.2, 1.28, 0.74])]), spread: F([0, 0, 0.04]), thumb: F([0.3, 0.16, 0.08]), wrist: F([0.12, 0]) }),
  // Mão em volta do guarda-mão (fuzis, SMGs, a frente da AWP).
  guardaMao: F({ fingers: F([F([1.02, 1.1, 0.66]), F([1.08, 1.16, 0.7]), F([1.12, 1.2, 0.72])]), spread: F([-0.04, 0, 0.06]), thumb: F([0.72, 0.42, 0.22]), wrist: F([0.08, 0]) }),
  // Mão na bomba da escopeta: fechada mais apertado.
  bomba: F({ fingers: F([F([1.22, 1.34, 0.8]), F([1.26, 1.38, 0.82]), F([1.3, 1.4, 0.84])]), spread: F([0, 0, 0.04]), thumb: F([0.86, 0.56, 0.3]), wrist: F([0.1, 0]) }),
  // Punho fechado no cabo da faca.
  faca: F({ fingers: F([F([1.44, 1.62, 1.0]), F([1.48, 1.64, 1.02]), F([1.5, 1.66, 1.04])]), spread: F([0, 0, 0]), thumb: F([1.0, 0.72, 0.42]), wrist: F([0, 0]) }),
});

/** Limites das juntas (radianos): flexão dos dedos, abertura, giro e flexão do polegar, pulso. */
export const HAND_LIMITS = F({
  flex: F([-0.3, 1.7]),
  spread: F([-0.35, 0.35]),
  thumbYaw: F([-0.4, 1.3]),
  thumbFlex: F([-0.3, 1.3]),
  wrist: F([-0.9, 0.9]),
});
```

- [ ] **Passo 4: Ossos e a árvore SDF da mão**

```js file=src/characters/hands/handShape.js
// Mão de 4 dedos de massinha com o antebraço (Fase 4.1; docs/phases/phase-4.md, seção 4.1, "Mãos de 4 dedos"): a árvore
// SDF na pose de repouso (dedos esticados) e o esqueleto de 14 ossos — antebraço, mão, 3 × 3 falanges e o polegar em 3.
// Puro (sem three.js): o rig (handRig.js), os pesos (handSkin.js) e os testes do Node usam o mesmo desenho.
// Referencial do modelo = o do antebraço: origem no cotovelo, +X para o pulso, +Y para as costas da mão, −Z para o lado
// do polegar (mão direita). A mão (osso `mao`) começa no pulso, em x = comprimento do antebraço.

import { HAND } from '../../data/hands.js';

const add = (a, b) => [a[0] + b[0], a[1] + b[1], a[2] + b[2]];
const scale = (a, s) => [a[0] * s, a[1] * s, a[2] * s];
const norm = (a) => {
  const l = Math.hypot(a[0], a[1], a[2]) || 1;
  return [a[0] / l, a[1] / l, a[2] / l];
};
const cross = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
const dot = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];

/** Posição do pulso no referencial do modelo. */
export const WRIST = Object.freeze([HAND.forearm.length, 0, 0]);

/** Raio do antebraço num x do modelo (cone arredondado do cotovelo ao pulso). */
export function forearmRadius(x) {
  const t = Math.max(0, Math.min(1, x / HAND.forearm.length));
  return HAND.forearm.elbowRadius + (HAND.forearm.wristRadius - HAND.forearm.elbowRadius) * t;
}

/**
 * Base ortonormal de repouso de um osso cujo +X é `dir`, com o +Y o mais perto possível das costas da mão (+Y).
 * @returns {{x:number[], y:number[], z:number[]}}
 */
export function boneBasis(dir) {
  const x = norm(dir);
  let y = [0, 1, 0];
  y = norm(add(y, scale(x, -dot(y, x))));
  return { x, y, z: cross(x, y) };
}

/**
 * Os 14 ossos em ordem (pai antes do filho): nome, pai, cabeça e ponta no referencial do modelo (repouso), raio da massa
 * em volta e a cadeia (braco, dedo1, dedo2, dedo3, polegar).
 * @returns {Array<{name:string, parent:string|null, head:number[], tail:number[], radius:number, chain:string, dir:number[]}>}
 */
export function handBones() {
  const bones = [];
  const push = (name, parent, head, tail, radius, chain) => {
    bones.push({ name, parent, head, tail, radius, chain, dir: norm([tail[0] - head[0], tail[1] - head[1], tail[2] - head[2]]) });
  };
  const L = HAND.forearm.length;
  push('antebraco', null, [0, 0, 0], [...WRIST], (HAND.forearm.elbowRadius + HAND.forearm.wristRadius) / 2, 'braco');
  const palmFront = add(WRIST, [HAND.palm.center[0] + HAND.palm.half[0], 0, 0]);
  push('mao', 'antebraco', [...WRIST], palmFront, HAND.palm.half[1] + 0.2, 'braco');
  for (const f of HAND.fingers) {
    let head = add(WRIST, f.base);
    let parent = 'mao';
    f.phalanges.forEach((len, i) => {
      const tail = add(head, [len, 0, 0]);
      const name = `${f.id}_${i + 1}`;
      push(name, parent, head, tail, f.radius * (1 - 0.04 * i), f.id);
      parent = name;
      head = tail;
    });
  }
  const t = HAND.thumb;
  const dir = norm(t.dir);
  let head = add(WRIST, t.base);
  let parent = 'mao';
  t.phalanges.forEach((len, i) => {
    const tail = add(head, scale(dir, len));
    const name = `${t.id}_${i + 1}`;
    push(name, parent, head, tail, t.radius * (1 - 0.05 * i), 'polegar');
    parent = name;
    head = tail;
  });
  if (bones.length !== 14) throw new Error(`mão com ${bones.length} ossos (esperado 14)`);
  if (bones[0].tail[0] !== L) throw new Error('antebraço fora do lugar');
  return bones;
}

/**
 * Árvore SDF da mão e do antebraço na pose de repouso (um material só: a massa do boneco). As costuras ficam nos nós
 * dos dedos e no pulso (união suave com vinco); calombos da massa inteira por cima.
 * @returns {object}
 */
export function handTree() {
  const L = HAND.forearm.length;
  const P = HAND.palm;
  const forearm = {
    type: 'roundCone', mat: 0, a: [0, 0, 0], b: [L - 0.35, 0, 0], ra: HAND.forearm.elbowRadius, rb: HAND.forearm.wristRadius,
  };
  const palm = { type: 'roundBox', mat: 0, pos: add(WRIST, P.center), size: [...P.half], r: P.round };
  // Almofada do polegar (tenar): liga a raiz do polegar à palma, como a massa apertada ali.
  const thenar = { type: 'ellipsoid', mat: 0, pos: add(WRIST, [1.25, -0.28, -1.0]), radii: [1.15, 0.66, 0.78] };
  const digits = [...HAND.fingers, HAND.thumb].map((f) => {
    const dir = f.dir ? norm(f.dir) : [1, 0, 0];
    const pts = [add(WRIST, f.base)];
    for (const len of f.phalanges) pts.push(add(pts[pts.length - 1], scale(dir, len)));
    return { type: 'tube', mat: 0, points: pts, radii: pts.map((_, i) => f.radius * (1 - 0.045 * i)) };
  });
  const body = { type: 'smoothUnion', k: HAND.soft, children: [forearm, palm, thenar] };
  const tree = {
    type: 'smoothUnionCrease', k: HAND.knuckleSoft, depth: HAND.crease.depth, width: HAND.crease.width, children: [body, ...digits],
  };
  const { amp, freq, octaves } = HAND.lumps;
  return { type: 'displace', amp, freq, octaves, seed: 'mao-de-massinha', child: tree };
}
```

- [ ] **Passo 5: Pesos, giros das poses e espelho**

```js file=src/characters/hands/handSkin.js
// Pesos do skinning e poses da mão de massinha (Fase 4.1; docs/phases/phase-4.md, seção 4.1, "Mãos de 4 dedos"). Puro:
// os testes do Node conferem os pesos (normalizados, cada vértice do dedo puxado pelo seu osso) e as poses (dentro dos
// limites das juntas); o rig (handRig.js) aplica.
// Pesos: distância de cada vértice à cápsula de cada osso (segmento + raio), queda suave 1/(d + queda)⁴, os 4 maiores,
// normalizados. Cada vértice só ouve os ossos da sua cadeia (o dedo mais perto, com a mão), então um dedo que dobra
// não arrasta o vizinho.

import { HAND, HAND_LIMITS, HAND_POSES } from '../../data/hands.js';

function segmentDistance(px, py, pz, h, t) {
  const dx = t[0] - h[0];
  const dy = t[1] - h[1];
  const dz = t[2] - h[2];
  const l2 = dx * dx + dy * dy + dz * dz || 1e-12;
  const s = Math.max(0, Math.min(1, ((px - h[0]) * dx + (py - h[1]) * dy + (pz - h[2]) * dz) / l2));
  return Math.hypot(px - h[0] - s * dx, py - h[1] - s * dy, pz - h[2] - s * dz);
}

/**
 * Índices e pesos de skinning (4 influências por vértice).
 * @param {Float32Array|number[]} positions xyz no referencial do modelo (repouso)
 * @param {Array} bones handBones()
 * @param {{falloff?:number, influences?:number}} [opts]
 * @returns {{skinIndex:Uint16Array, skinWeight:Float32Array}}
 */
export function computeSkinWeights(positions, bones, { falloff = HAND.skin.falloff, influences = HAND.skin.influences } = {}) {
  const n = positions.length / 3;
  const k = influences;
  const skinIndex = new Uint16Array(n * k);
  const skinWeight = new Float32Array(n * k);
  const chains = [...new Set(bones.map((b) => b.chain))];
  const chainBones = Object.fromEntries(chains.map((c) => [c, bones.map((b, i) => (b.chain === c ? i : -1)).filter((i) => i >= 0)]));
  const handIndex = bones.findIndex((b) => b.name === 'mao');
  const surf = new Float64Array(bones.length);
  const idx = new Array(bones.length);
  for (let v = 0; v < n; v++) {
    const px = positions[v * 3];
    const py = positions[v * 3 + 1];
    const pz = positions[v * 3 + 2];
    let bestChain = 'braco';
    let best = Infinity;
    for (let b = 0; b < bones.length; b++) {
      const d = Math.max(0, segmentDistance(px, py, pz, bones[b].head, bones[b].tail) - bones[b].radius);
      surf[b] = d;
      if (d < best) {
        best = d;
        bestChain = bones[b].chain;
      }
    }
    const allowed = bestChain === 'braco' ? chainBones.braco : [handIndex, ...chainBones[bestChain]];
    let count = 0;
    for (const b of allowed) idx[count++] = b;
    const ws = allowed.map((b) => 1 / (surf[b] + falloff) ** 4);
    const order = ws.map((w, i) => i).sort((a, b) => ws[b] - ws[a]).slice(0, k);
    let sum = 0;
    for (const i of order) sum += ws[i];
    for (let j = 0; j < k; j++) {
      const i = order[j];
      skinIndex[v * k + j] = i === undefined ? 0 : idx[i];
      skinWeight[v * k + j] = i === undefined ? 0 : ws[i] / sum;
    }
  }
  return { skinIndex, skinWeight };
}

const clamp = (v, [lo, hi]) => Math.max(lo, Math.min(hi, v));

/**
 * Rotações locais de cada osso para uma pose (Euler 'YZX' do three: [x, y, z]); a flexão dobra para a palma (−Y), então é
 * giro negativo em Z. Tudo preso aos limites das juntas. O antebraço não gira aqui (quem posiciona o braço é o viewmodel).
 * @param {string|object} pose nome em HAND_POSES ou a pose
 * @returns {Object<string, number[]>}
 */
export function poseRotations(pose) {
  const p = typeof pose === 'string' ? HAND_POSES[pose] : pose;
  if (!p) throw new Error(`pose de mão desconhecida: ${pose}`);
  const L = HAND_LIMITS;
  const out = { antebraco: [0, 0, 0], mao: [0, clamp(p.wrist[1], L.wrist), -clamp(p.wrist[0], L.wrist)] };
  HAND.fingers.forEach((f, i) => {
    const [a, b, c] = p.fingers[i];
    out[`${f.id}_1`] = [0, clamp(p.spread[i], L.spread), -clamp(a, L.flex)];
    out[`${f.id}_2`] = [0, 0, -clamp(b, L.flex)];
    out[`${f.id}_3`] = [0, 0, -clamp(c, L.flex)];
  });
  const [yaw, f1, f2] = p.thumb;
  out[`${HAND.thumb.id}_1`] = [0, -clamp(yaw, L.thumbYaw), -clamp(f1, L.thumbFlex) * 0.6];
  out[`${HAND.thumb.id}_2`] = [0, 0, -clamp(f1, L.thumbFlex) * 0.4 - clamp(f2, L.thumbFlex) * 0.3];
  out[`${HAND.thumb.id}_3`] = [0, 0, -clamp(f2, L.thumbFlex) * 0.7];
  return out;
}

/** A mesma pose na mão esquerda (a direita espelhada em Z): giros em X e Y trocam de sinal, em Z ficam. */
export function mirrorRotations(rot) {
  return Object.fromEntries(Object.entries(rot).map(([k, [x, y, z]]) => [k, [-x, -y, z]]));
}
```

- [ ] **Passo 6: Cor da braçadeira**

```js file=src/characters/hands/armband.js
// Cor da braçadeira do time (Fase 4.1; docs/phases/phase-4.md, seção 4.1, "Mãos de 4 dedos", e seção 0.12): a cor do
// time que mais se destaca da massa do braço, pela diferença de cor ΔE (CIE76, em L*a*b* D65). Puro: o viewmodel usa
// agora, os bonecos da Fase 5 (com a cor do criador) depois, e os testes do Node conferem.

import { ARMBAND } from '../../data/hands.js';
import { TEAM_COLORS } from '../../data/palette.js';

const srgbToLinear = (c) => (c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4);
const labF = (t) => (t > 216 / 24389 ? Math.cbrt(t) : (t * 24389) / 27 / 116 + 16 / 116);

/** '#RRGGBB' → [L, a, b] (D65). */
export function hexToLab(hex) {
  const m = /^#?([0-9a-f]{6})$/i.exec(hex);
  if (!m) throw new Error(`cor inválida: ${hex}`);
  const n = parseInt(m[1], 16);
  const r = srgbToLinear(((n >> 16) & 255) / 255);
  const g = srgbToLinear(((n >> 8) & 255) / 255);
  const b = srgbToLinear((n & 255) / 255);
  const x = (0.4124564 * r + 0.3575761 * g + 0.1804375 * b) / 0.95047;
  const y = 0.2126729 * r + 0.7151522 * g + 0.072175 * b;
  const z = (0.0193339 * r + 0.119192 * g + 0.9503041 * b) / 1.08883;
  const fx = labF(x);
  const fy = labF(y);
  const fz = labF(z);
  return [116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz)];
}

/** Diferença de cor ΔE (CIE76) entre duas cores '#RRGGBB'. */
export function deltaE(hexA, hexB) {
  const [l1, a1, b1] = hexToLab(hexA);
  const [l2, a2, b2] = hexToLab(hexB);
  return Math.hypot(l1 - l2, a1 - a2, b1 - b2);
}

/**
 * Cor da braçadeira de um time sobre um braço de massa `armColor`, ou null sem time.
 * @param {'tr'|'ct'|null} team
 * @param {string} armColor '#RRGGBB'
 * @returns {string|null}
 */
export function armbandColor(team, armColor) {
  const colors = team ? TEAM_COLORS[team] : null;
  if (!colors) return null;
  let best = null;
  let bestDelta = -1;
  for (const key of ARMBAND.colors) {
    const c = colors[key];
    const d = deltaE(c, armColor);
    if (d >= ARMBAND.minDelta) return c;
    if (d > bestDelta) {
      best = c;
      bestDelta = d;
    }
  }
  return best;
}
```

- [ ] **Passo 7: O braço (`ClayArm`)**

```js file=src/characters/hands/handRig.js
// Braço de massinha com a mão de 4 dedos e o rig (Fase 4.1; docs/phases/phase-4.md, seção 4.1, "Mãos de 4 dedos"):
// a malha SDF da mão direita em repouso (src/characters/hands/handShape.js) vira uma SkinnedMesh de 14 ossos com os pesos
// de handSkin.js; a esquerda é a direita espelhada em Z (malha, ossos e giros). O boil do ClayMaterial age na pose de
// repouso (antes do skinning) e as digitais ficam no espaço do objeto em repouso: a massa dobra com o dedo e as marcas
// vão junto. A braçadeira do time é uma faixa de massa presa ao osso do antebraço (seção 0.12).
// As geometrias (com os pesos) são preparadas uma vez por lado e divididas entre os braços (HandLibrary); cada braço tem
// o seu esqueleto e os seus materiais. A pose muda só na troca de pose (12/s, "em dois"); quem chama decide quando.

import * as THREE from 'three';
import { ClayMaterial } from '../../clay/ClayMaterial.js';
import { ARMBAND, HAND } from '../../data/hands.js';
import { WRIST, boneBasis, forearmRadius, handBones, handTree } from './handShape.js';
import { computeSkinWeights, mirrorRotations, poseRotations } from './handSkin.js';

const MIRROR = new THREE.Matrix4().makeScale(1, 1, -1);

/** Malha da mão direita em repouso (Workers e cache do SdfMesher). Quem recebe é dono. */
export function buildArmGeometry(sdf) {
  const tree = handTree();
  const extent = HAND.forearm.length + HAND.palm.half[0] * 2 + 4.5;
  return sdf.build(tree, {
    resolution: Math.min(1024, Math.ceil(extent / HAND.mesh.cell)), maxCells: HAND.mesh.maxCells, touchRadius: HAND.mesh.touchRadius,
  });
}

/** Faixa da braçadeira em volta do antebraço (anel torneado), no referencial do modelo. */
export function armbandTree() {
  const L = HAND.forearm.length;
  const x0 = ARMBAND.at * L - ARMBAND.width / 2;
  const x1 = x0 + ARMBAND.width;
  const r0 = forearmRadius(x0) - 0.12;
  const r1 = forearmRadius(x1) - 0.12;
  return {
    type: 'lathe', mat: 0, closed: true, corner: ARMBAND.round,
    points: [[x0, r0], [x1, r1], [x1, r1 + ARMBAND.thickness + 0.12], [x0, r0 + ARMBAND.thickness + 0.12]],
  };
}

/** Malha da braçadeira (Workers e cache do SdfMesher), no referencial do antebraço. Quem recebe é dono. */
export function buildArmbandGeometry(sdf) {
  const extent = 2 * (HAND.forearm.elbowRadius + ARMBAND.thickness + 0.5);
  return sdf.build(armbandTree(), {
    resolution: Math.min(512, Math.ceil(extent / ARMBAND.mesh.cell)), maxCells: ARMBAND.mesh.maxCells,
    touchRadius: ARMBAND.mesh.touchRadius,
  });
}

/** Cópia espelhada em Z (esquerda): posições e normais trocam o sinal de z e os triângulos invertem o sentido. */
export function mirrorGeometry(source) {
  const g = source.clone();
  for (const name of ['position', 'normal']) {
    const a = g.attributes[name];
    for (let i = 0; i < a.count; i++) a.setZ(i, -a.getZ(i));
    a.needsUpdate = true;
  }
  const idx = g.index;
  for (let i = 0; i < idx.count; i += 3) {
    const b = idx.getX(i + 1);
    idx.setX(i + 1, idx.getX(i + 2));
    idx.setX(i + 2, b);
  }
  idx.needsUpdate = true;
  g.computeBoundingBox();
  g.computeBoundingSphere();
  return g;
}

function mirrorBone(b) {
  const m = (p) => [p[0], p[1], -p[2]];
  return { ...b, head: m(b.head), tail: m(b.tail), dir: m(b.dir) };
}

/** Ossos de um lado (a esquerda é a direita espelhada em Z). */
export function sideBones(side) {
  const defs = handBones();
  return side === 'esquerda' ? defs.map(mirrorBone) : defs;
}

/**
 * Geometria de um lado pronta para o skinning: a direita copiada, a esquerda espelhada, com `skinIndex`/`skinWeight`.
 * A fonte continua de quem a deu; quem recebe é dono da nova.
 * @param {THREE.BufferGeometry} source a mão direita em repouso (buildArmGeometry)
 * @param {'direita'|'esquerda'} side
 */
export function prepareArmGeometry(source, side) {
  const geo = side === 'esquerda' ? mirrorGeometry(source) : source.clone();
  const { skinIndex, skinWeight } = computeSkinWeights(geo.attributes.position.array, sideBones(side));
  geo.setAttribute('skinIndex', new THREE.Uint16BufferAttribute(skinIndex, 4));
  geo.setAttribute('skinWeight', new THREE.Float32BufferAttribute(skinWeight, 4));
  geo.name = `braco:${side}`;
  return geo;
}

/** A braçadeira de um lado (a esquerda espelhada). Quem recebe é dono. */
export function prepareArmbandGeometry(source, side) {
  const geo = side === 'esquerda' ? mirrorGeometry(source) : source.clone();
  geo.name = `bracadeira:${side}`;
  return geo;
}

function restMatrix(bone, left) {
  const { x, y, z } = boneBasis(bone.dir);
  const m = new THREE.Matrix4().makeBasis(new THREE.Vector3(...x), new THREE.Vector3(...y), new THREE.Vector3(...z));
  m.setPosition(bone.head[0], bone.head[1], bone.head[2]);
  return left ? MIRROR.clone().multiply(m).multiply(MIRROR) : m;
}

const _q = new THREE.Quaternion();
const _e = new THREE.Euler(0, 0, 0, 'YZX');
const _m = new THREE.Matrix4();
const _v = new THREE.Vector3();
const _x = new THREE.Vector3();
const _y = new THREE.Vector3();
const _z = new THREE.Vector3();

export class ClayArm {
  /**
   * @param {{geometry:THREE.BufferGeometry, armband?:THREE.BufferGeometry|null, side:'direita'|'esquerda', color:string}} opts
   *   `geometry`: a do lado já preparada (prepareArmGeometry); `armband`: a braçadeira do lado. As duas continuam de
   *   quem as deu (a HandLibrary divide entre os braços); o braço é dono só do esqueleto e dos materiais.
   */
  constructor({ geometry, armband = null, side, color }) {
    if (!geometry.attributes.skinIndex) throw new Error('ClayArm: a geometria precisa dos pesos (prepareArmGeometry)');
    this.side = side;
    const left = side === 'esquerda';
    this.left = left;
    const C = HAND.clay;
    this.material = new ClayMaterial({ color, roughness: C.roughness, wetness: C.wetness, touched: true, seed: `mao-${side}` });
    this.material.setObjectSize(C.objectSize);
    // Ossos: matriz de repouso de cada um no referencial do modelo; a local é a do pai invertida vezes a sua.
    this.bones = {};
    this.rest = {};
    const worlds = {};
    const list = [];
    for (const def of handBones()) {
      const bone = new THREE.Bone();
      bone.name = def.name;
      const world = restMatrix(def, left);
      worlds[def.name] = world;
      const local = def.parent ? _m.copy(worlds[def.parent]).invert().multiply(world) : world.clone();
      local.decompose(bone.position, bone.quaternion, bone.scale);
      this.rest[def.name] = bone.quaternion.clone();
      if (def.parent) this.bones[def.parent].add(bone);
      this.bones[def.name] = bone;
      list.push(bone);
    }
    this.mesh = new THREE.SkinnedMesh(geometry, this.material);
    this.mesh.name = `braco-${side}`;
    this.mesh.frustumCulled = false; // os ossos saem de perto da caixa de repouso
    this.mesh.castShadow = true;
    this.mesh.receiveShadow = true;
    this.mesh.add(this.bones.antebraco);
    this.mesh.updateMatrixWorld(true);
    this.skeleton = new THREE.Skeleton(list);
    this.mesh.bind(this.skeleton);
    // Braçadeira: presa ao osso do antebraço (rígida), escondida sem time.
    this.armbandMaterial = null;
    this.armband = null;
    if (armband) {
      const B = ARMBAND.clay;
      this.armbandMaterial = new ClayMaterial({ color, roughness: B.roughness, wetness: B.wetness, touched: true, seed: `bracadeira-${side}` });
      this.armbandMaterial.setObjectSize(B.objectSize);
      this.armband = new THREE.Mesh(armband, this.armbandMaterial);
      this.armband.name = `bracadeira-${side}`;
      this.armband.visible = false;
      this.armband.castShadow = true;
      this.armband.receiveShadow = true;
      this.bones.antebraco.add(this.armband);
    }
    this.pose = null;
    this.wristPose = null;
  }

  /** Aplica uma pose de mão (nome em HAND_POSES ou objeto): giro de repouso × giro da pose em cada osso. */
  setPose(pose) {
    const rot = poseRotations(pose);
    const r = this.left ? mirrorRotations(rot) : rot;
    for (const [name, [x, y, z]] of Object.entries(r)) {
      if (name === 'antebraco') continue;
      _e.set(x, y, z, 'YZX');
      this.bones[name].quaternion.copy(this.rest[name]).multiply(_q.setFromEuler(_e));
    }
    this.pose = pose;
    this.wristPose = r.mao;
  }

  /** Cor da massa do braço (a do boneco). */
  setColor(color) {
    this.material.color.set(color);
  }

  /** Braçadeira do time: cor (hex) ou null para esconder. */
  setArmband(color) {
    if (!this.armband) return;
    this.armband.visible = Boolean(color);
    if (color) this.armbandMaterial.color.set(color);
  }

  /**
   * Põe a mão numa âncora: o pulso na posição e na rotação dadas (no espaço do pai da malha) e o antebraço apontando para
   * o cotovelo, com o comprimento do antebraço (o cotovelo real fica no alinhamento, a `forearm.length` do pulso). O giro
   * do antebraço acompanha o da mão (o +Y do antebraço é o +Y da mão, sem a componente ao longo do braço).
   * @param {THREE.Vector3} wrist @param {THREE.Quaternion} handQuat @param {THREE.Vector3} elbowTarget
   */
  place(wrist, handQuat, elbowTarget) {
    const L = HAND.forearm.length;
    _x.subVectors(wrist, elbowTarget).normalize();
    _y.set(0, 1, 0).applyQuaternion(handQuat);
    _y.addScaledVector(_x, -_y.dot(_x));
    if (_y.lengthSq() < 1e-6) _y.set(0, 1, 0).addScaledVector(_x, -_x.y);
    _y.normalize();
    _z.crossVectors(_x, _y);
    _m.makeBasis(_x, _y, _z);
    const forearm = this.bones.antebraco;
    forearm.quaternion.setFromRotationMatrix(_m);
    forearm.position.copy(_v.copy(wrist).addScaledVector(_x, -L));
    // A mão: rotação da âncora no referencial do antebraço, com o pulso da pose por cima.
    const hand = this.bones.mao;
    hand.quaternion.copy(forearm.quaternion).invert().multiply(handQuat);
    if (this.wristPose) {
      const [x, y, z] = this.wristPose;
      hand.quaternion.multiply(_q.setFromEuler(_e.set(x, y, z, 'YZX')));
    }
    hand.position.set(L, 0, 0);
  }

  /** Posição do pulso e do cotovelo (espaço do pai da malha), para os testes e o painel. */
  joints(outWrist, outElbow) {
    const f = this.bones.antebraco;
    outElbow.copy(f.position);
    outWrist.set(HAND.forearm.length, 0, 0).applyQuaternion(f.quaternion).add(f.position);
  }

  dispose() {
    this.mesh.removeFromParent();
    this.material.dispose();
    this.armbandMaterial?.dispose();
    this.skeleton.dispose();
  }
}

/** Pulso no referencial do modelo (para quem precisa do comprimento do antebraço). */
export const ARM_WRIST = WRIST;
```

- [ ] **Passo 8: O serviço `handModels`**

```js file=src/characters/hands/handLibrary.js
// Serviço `handModels` (Fase 4.1; docs/phases/phase-4.md, seção 4.1, "Mãos de 4 dedos"): gera uma vez por sessão a malha
// da mão de massinha e a da braçadeira (SdfMesher: Workers e cache do IndexedDB), prepara os dois lados com os pesos do
// skinning e entrega braços (ClayArm) que só apontam para elas — as geometrias são compartilhadas (marcadas
// `userData.shared`, o dispose das cenas não as toca) e saem só no dispose do serviço. O viewmodel usa agora; os
// bonecos da Fase 5 herdam.

import { ClayArm, buildArmGeometry, buildArmbandGeometry, prepareArmGeometry, prepareArmbandGeometry } from './handRig.js';

const now = () => (globalThis.performance?.now ? globalThis.performance.now() : Date.now());
const SIDES = Object.freeze(['direita', 'esquerda']);

export class HandLibrary {
  #sdf;
  #log;
  #pending = null;
  #built = null;
  #disposed = false;

  /** @param {{sdf:import('../../clay/sdf/sdfMesher.js').SdfMesher, log?:object|null}} deps */
  constructor({ sdf, log = null }) {
    this.#sdf = sdf;
    this.#log = log;
  }

  /**
   * Geometrias prontas dos dois lados (gera na primeira vez; pedidos juntos dividem a mesma promessa).
   * @returns {Promise<{direita:{arm, armband}, esquerda:{arm, armband}, triangles:number, ms:number}>}
   */
  geometries() {
    if (this.#disposed) return Promise.reject(new Error('HandLibrary: já foi descartada'));
    if (!this.#pending) {
      const pending = this.#build();
      pending.catch(() => {
        if (this.#pending === pending) this.#pending = null;
      });
      this.#pending = pending;
    }
    return this.#pending;
  }

  async #build() {
    const t0 = now();
    const [arm, band] = await Promise.all([buildArmGeometry(this.#sdf), buildArmbandGeometry(this.#sdf)]);
    if (this.#disposed) {
      arm.dispose();
      band.dispose();
      throw new Error('HandLibrary: descartada durante a geração');
    }
    const out = { triangles: 0, ms: 0 };
    for (const side of SIDES) {
      const g = { arm: prepareArmGeometry(arm, side), armband: prepareArmbandGeometry(band, side) };
      g.arm.userData.shared = true;
      g.armband.userData.shared = true;
      out[side] = g;
      out.triangles += g.arm.index.count / 3;
    }
    arm.dispose();
    band.dispose();
    out.ms = now() - t0;
    this.#built = out;
    this.#log?.debug(`mãos de massinha: ${Math.round(out.triangles / 2)} triângulos por braço em ${out.ms.toFixed(0)} ms`);
    return out;
  }

  /** Relatório do console (`armas`): estado, triângulos por braço e tempo. */
  report() {
    const b = this.#built;
    return { state: b ? 'pronta' : this.#pending ? 'gerando' : '—', triangles: b ? Math.round(b.triangles / 2) : 0, ms: b ? Math.round(b.ms) : 0 };
  }

  /**
   * Braço novo de um lado, com a massa `color` (a do boneco). O braço é dono só do esqueleto e dos materiais.
   * @param {'direita'|'esquerda'} side
   * @param {{color:string}} options
   */
  async createArm(side, { color }) {
    const g = (await this.geometries())[side];
    if (!g) throw new Error(`lado desconhecido: ${side}`);
    return new ClayArm({ geometry: g.arm, armband: g.armband, side, color });
  }

  dispose() {
    this.#disposed = true;
    const b = this.#built;
    if (b) {
      for (const side of SIDES) {
        b[side].arm.dispose();
        b[side].armband.dispose();
      }
    }
    this.#built = null;
    this.#pending = null;
  }
}
```

- [ ] **Passo 9: Rodar e ver passar**

Run: `node --test tests/clayHands.test.js`
Expected: PASS
Run: `npm test`
Expected: PASS — 309 testes passando.

- [ ] **Passo final: Commit** (só com o pedido do usuário)

```bash
git add src/data/hands.js src/characters/hands tests/clayHands.test.js
git commit -m "MASSACRE 4.1: mãos de massinha de 4 dedos com rig e braçadeira" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Tarefa 3: Massas, receitas, gerador, plantas e a biblioteca das armas

**Files:**
- Create: `src/data/weaponPalette.js`, `src/data/viewmodel.js`, `src/weapons/model/recipe.js`, `src/weapons/model/weaponModel.js`, `src/weapons/model/silhouette.js`, `src/weapons/model/weaponLibrary.js`, `src/data/armas/glock.js`, `ak47.js`, `m4a4.js`, `awp.js`, `nova.js`, `p90.js`, `knife.js`, `index.js`, `tools/blender/refs/glock.json`, `ak47.json`, `m4a4.json`, `awp.json`, `nova.json`, `p90.json`, `tools/silhueta.html`, `tests/weaponRecipes.test.js`
- Modify: `src/data/claySkins.js`, `src/clay/glsl/skins.js`, `src/core/events.js`

Decisões do usuário: estilo "fiel e gordinha" (a silhueta da arma real com massa mínima de 1,2 u; a lâmina da espátula, 0,5 u — o revólver do pinguim de *The Wrong Trousers*, QCG1) e a cor real traduzida em massinha com o acento da facção nos detalhes pequenos (massa de mira, base do carregador, gatilho, seletor). A paleta: `grafite` (o "preto" das armas vira grafite fosco; massinha nunca é preta), `grafiteClaro`, `madeira` com a skin de base nova `veio` (riscada a palito ao longo da peça, fora das skins de jogador), `madeiraEscura`, `verdeOliva`, `areia`, `prata` e `aco` (a lâmina da espátula, massa prata úmida); o acento TR é terracota/laranja, o CT azul/verde-água e o das armas dos dois lados amarelo-massinha/branco-massa. A receita (um módulo por arma, `export default` + JSON puro) tem `id`, `version`, `refs`, `materials` (slot → massa), `soft` opcional, `groups` (as partes que se mexem, com pivô e eixo), `anchors` (mãos com a pose, boca, ejeção, mira) e `parts` (forma, parâmetros, `pos`/`rot` em Euler XYZ, `op: 'subtract'` nos cortes). `recipe.js` valida e monta uma árvore SDF por grupo — as peças numa união suave com vinco (k 0,25 u, faixa de costura de 0,25 u entre massas), os cortes numa subtração suave (k 0,12 u) e os calombos —; `weaponModel.js` gera uma malha por grupo no pivô, em dois níveis (`perto` 0,14 u, viewmodel e bancada; `mundo` 0,35 u, Fases 5, 8 e 9), e os materiais com o acento e o boil na medida da arma; `silhouette.js` tira a silhueta lateral do SDF (máximo em Z) para o IoU contra a planta e para o comprimento. As plantas vêm de fotos laterais do Wikimedia Commons (Glock 17, AK-47 tipo II, carabina M4A1 com a alça de transporte, AI Arctic Warfare PSG 90, Benelli M3 Super 90, FN P90): a página `tools/silhueta.html` (servida pelo servidor de desenvolvimento) carrega a imagem pelo CORS num canvas, separa a arma do fundo, segue o contorno, simplifica e escala pelo comprimento real — nenhuma imagem vai para o disco, só o contorno e a ficha da fonte. As âncoras das mãos saem da geometria da empunhadura (a mão direita com os dedos perpendiculares ao eixo inclinado da empunhadura e os nós logo à frente da borda; a esquerda por baixo do guarda-mão) e os guarda-matos ficam alargados em relação à planta, para o dedo de massa caber. `src/data/viewmodel.js` entra aqui porque o teste das receitas confere a categoria de cada uma no viewmodel (a Tarefa 4 usa o resto). O serviço `weaponModels` guarda as malhas por (arma, nível) e os materiais por (arma, facção) — o boil de cada material segue o tamanho da arma —, marca tudo como compartilhado (`userData.shared`), pré-carrega e relê a receita do disco em duas fases (`EV.WEAPON_MODEL` com `relendo` antes do descarte e `pronta` depois).

- [ ] **Passo 1: Escrever os testes** — registro e validação, a tabela do primeiro lote, espessura mínima, acento pela facção, IoU ≥ 0,8, comprimento, árvores determinísticas e categoria no viewmodel.

```js file=tests/weaponRecipes.test.js
// Testes das receitas das armas de massinha (Fase 4.1; docs/phases/phase-4.md, seção 4.1, "Testes"): as sete validam;
// grupos, âncoras e massas por arma (a tabela do primeiro lote); a espessura mínima (e a receita que a quebra é
// recusada); o acento pela facção; a silhueta lateral × a planta de referência com IoU ≥ 0,8; o comprimento real da
// tabela de escala; árvores determinísticas (a mesma chave de cache); e a categoria de cada uma no viewmodel.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { ARMAS } from '../src/data/armas/index.js';
import { FACTION_ACCENTS, WEAPON_CLAYS, WEAPON_MODEL } from '../src/data/weaponPalette.js';
import { HAND_POSES } from '../src/data/hands.js';
import { VIEWMODEL } from '../src/data/viewmodel.js';
import { WEAPONS } from '../src/data/weapons.js';
import {
  materialSlots, partThickness, recipeTrees, recipeWholeTree, resolveClay, validateRecipe, weaponFaction,
} from '../src/weapons/model/recipe.js';
import { meshOptions } from '../src/weapons/model/weaponModel.js';
import { silhouetteIoU, silhouetteLength } from '../src/weapons/model/silhouette.js';
import { hashNode } from '../src/clay/sdf/nodes.js';

const IDS = ['glock', 'ak47', 'm4a4', 'awp', 'nova', 'p90', 'knife'];

// A tabela do primeiro lote (phase-4.md): facção do acento, massas, grupos e o comprimento real (u).
const TABLE = {
  glock: { faction: 'tr', clays: ['grafite', 'grafiteClaro'], groups: ['corpo', 'slide', 'carregador', 'gatilho'], length: 7.3 },
  ak47: { faction: 'tr', clays: ['grafite', 'madeira', 'madeiraEscura'], groups: ['corpo', 'carregador', 'ferrolho', 'gatilho'], length: 34.6 },
  m4a4: { faction: 'ct', clays: ['grafite', 'grafiteClaro'], groups: ['corpo', 'carregador', 'ferrolho', 'gatilho'], length: 33.1 },
  awp: { faction: 'ambos', clays: ['verdeOliva', 'grafite'], groups: ['corpo', 'carregador', 'alavanca', 'gatilho'], length: 48.4 },
  nova: { faction: 'ambos', clays: ['grafite', 'grafiteClaro'], groups: ['corpo', 'bomba', 'gatilho'], length: 39.2 },
  p90: { faction: 'ambos', clays: ['grafite', 'grafiteClaro'], groups: ['corpo', 'carregador', 'gatilho'], length: 19.7 },
  knife: { faction: 'ambos', clays: ['aco', 'madeira'], groups: ['corpo'], length: 7.9 },
};

const plan = (id) => JSON.parse(readFileSync(new URL(`../tools/blender/refs/${id}.json`, import.meta.url), 'utf8'));

test('receitas: as sete estão no registro, validam e são das armas da tabela', () => {
  assert.deepEqual(Object.keys(ARMAS).sort(), [...IDS].sort());
  for (const id of IDS) {
    const r = ARMAS[id];
    assert.equal(r.id, id);
    assert.ok(WEAPONS[id], `${id} existe em src/data/weapons.js`);
    assert.doesNotThrow(() => validateRecipe(r), id);
  }
});

test('receitas: grupos, âncoras e massas por arma (a tabela do primeiro lote)', () => {
  for (const id of IDS) {
    const r = ARMAS[id];
    const t = TABLE[id];
    assert.deepEqual(Object.keys(r.groups).sort(), [...t.groups].sort(), `${id}: grupos`);
    const clays = new Set(Object.values(r.materials));
    for (const c of t.clays) assert.ok(clays.has(c), `${id}: falta a massa ${c}`);
    for (const c of clays) assert.ok(WEAPON_CLAYS[c] || c === 'acento' || c === 'acento2', `${id}: massa ${c}`);
    const melee = WEAPONS[id].slot === 'melee';
    const expected = melee ? ['maoDireita'] : ['boca', 'ejecao', 'maoDireita', 'maoEsquerda'];
    for (const a of expected) assert.ok(r.anchors[a], `${id}: falta a âncora ${a}`);
    if (melee) assert.equal(r.anchors.maoEsquerda, undefined, 'a faca é de uma mão só');
    for (const side of ['maoDireita', 'maoEsquerda']) {
      const a = r.anchors[side];
      if (a) assert.ok(HAND_POSES[a.pose], `${id}.${side}: pose ${a.pose}`);
    }
    // Toda massa declarada é usada por alguma peça de massa (a lista de materiais das malhas sai daí).
    const used = materialSlots(r);
    assert.ok(used.length >= 2, `${id}: massas usadas ${used}`);
    for (const slot of used) assert.ok(r.materials[slot], `${id}: ${slot}`);
  }
});

test('receitas: nenhuma peça de massa fica mais fina que o mínimo (a lâmina da faca é a exceção)', () => {
  for (const id of IDS) {
    for (const p of ARMAS[id].parts) {
      if (p.op === 'subtract') continue;
      const min = p.thin ? WEAPON_MODEL.minBlade : WEAPON_MODEL.minThickness;
      assert.ok(partThickness(p) >= min - 1e-9, `${id}.${p.name}: ${partThickness(p)} < ${min}`);
    }
  }
  assert.ok(ARMAS.knife.parts.some((p) => p.thin && Math.abs(partThickness(p) - WEAPON_MODEL.minBlade) < 1e-9), 'a lâmina tem 0,5 u');
  // Uma receita com uma peça fina demais é recusada, com o nome da peça no erro.
  const bad = structuredClone(ARMAS.glock);
  const part = bad.parts.find((p) => p.shape === 'profile' && p.op !== 'subtract');
  part.h = 0.4;
  assert.throws(() => validateRecipe(bad), new RegExp(part.name));
});

test('receitas: acento pela facção (as de um lado ficam com o seu; as dos dois lados trocam)', () => {
  for (const id of IDS) {
    assert.equal(weaponFaction(id), TABLE[id].faction, id);
    const r = ARMAS[id];
    const accentSlot = Object.keys(r.materials).find((k) => r.materials[k] === 'acento');
    for (const f of ['tr', 'ct', 'ambos']) {
      assert.equal(resolveClay(r, accentSlot, f).color, FACTION_ACCENTS[f].acento, `${id}/${f}`);
    }
    // Sem facção pedida, o acento é o da própria arma.
    assert.equal(resolveClay(r, accentSlot).color, FACTION_ACCENTS[TABLE[id].faction].acento, `${id}: padrão`);
  }
});

test('receitas: silhueta lateral × planta de referência com IoU ≥ 0,8 (as seis com planta)', () => {
  for (const id of IDS.filter((x) => x !== 'knife')) {
    const { iou, sdfArea, refArea } = silhouetteIoU(ARMAS[id], plan(id), { cell: 0.1 });
    assert.ok(iou >= WEAPON_MODEL.silhouetteIoU, `${id}: IoU ${iou.toFixed(3)} (massa ${sdfArea.toFixed(1)} u², planta ${refArea.toFixed(1)} u²)`);
  }
});

test('receitas: o comprimento real é o da tabela de escala (e o da planta)', () => {
  for (const id of IDS) {
    const len = silhouetteLength(ARMAS[id], { cell: 0.05 });
    assert.ok(Math.abs(len - TABLE[id].length) <= 0.15, `${id}: ${len.toFixed(2)} u (tabela ${TABLE[id].length})`);
    if (id !== 'knife') assert.equal(plan(id).lengthU, TABLE[id].length, `${id}: planta`);
  }
});

test('receitas: árvores determinísticas (a mesma chave de cache do SdfMesher)', () => {
  for (const id of IDS) {
    const a = recipeTrees(ARMAS[id]);
    const b = recipeTrees(structuredClone(ARMAS[id]));
    assert.deepEqual(a.materials, b.materials, id);
    for (const g of Object.keys(a.groups)) {
      for (const lod of Object.keys(WEAPON_MODEL.lods)) {
        const oa = meshOptions(a.groups[g].tree, lod);
        const ob = meshOptions(b.groups[g].tree, lod);
        assert.deepEqual(oa, ob);
        assert.equal(hashNode(a.groups[g].tree, oa), hashNode(b.groups[g].tree, ob), `${id}.${g}.${lod}`);
      }
    }
    assert.equal(hashNode(recipeWholeTree(ARMAS[id])), hashNode(recipeWholeTree(structuredClone(ARMAS[id]))));
  }
});

test('receitas: cada uma tem categoria no viewmodel', () => {
  for (const id of IDS) {
    const w = VIEWMODEL.weapons[id];
    assert.ok(w && VIEWMODEL.categories[w.category], `${id}: categoria ${w?.category}`);
  }
  for (const id of Object.keys(VIEWMODEL.weapons)) assert.ok(ARMAS[id], `${id}: categoria sem receita`);
});
```

- [ ] **Passo 2: Rodar e ver falhar**

Run: `node --test tests/weaponRecipes.test.js`
Expected: FAIL — o teste não carrega (`ERR_MODULE_NOT_FOUND`: `src/data/armas/index.js`).

- [ ] **Passo 3: As massas das armas e a skin de base `veio`**

```js file=src/data/weaponPalette.js
// Massas e números do gerador das armas de massinha (Fase 4.1; desenho em docs/phases/phase-4.md, seção 4.1;
// referências no item 13 do moodboard). Decisão do usuário (2026-09-25): cor real traduzida em massinha + acento da
// facção nos detalhes pequenos (massa de mira, gatilho, base do carregador, seletor).
// Massinha nunca é preta: o "preto" das armas reais vira grafite (QPG1, QPL1 — a pistola preta fosca de massa).

const F = Object.freeze;

/**
 * Massas da paleta das armas. `skin` é um id de src/data/claySkins.js; `colorB`/`colorC` são as cores extras da skin.
 * roughness e wetness seguem o ClayMaterial (0 = massa seca e fosca, 1 = fresca e úmida).
 */
export const WEAPON_CLAYS = F({
  grafite: F({ color: '#33383F', roughness: 0.68, wetness: 0.28 }), // metal preto (QPG5, QPL6)
  grafiteClaro: F({ color: '#79818A', roughness: 0.62, wetness: 0.34 }), // ferrolho, slide, peças soltas
  madeira: F({ color: '#8C5A3C', roughness: 0.7, wetness: 0.25, skin: 'veio', colorB: '#4A2C19', colorC: '#A5764D' }), // QPG2, QPL4
  madeiraEscura: F({ color: '#5A3825', roughness: 0.64, wetness: 0.3 }), // baquelite da empunhadura do AK (QPG2)
  verdeOliva: F({ color: '#48533A', roughness: 0.7, wetness: 0.26 }), // polímero verde (AWP, AUG, Scout)
  areia: F({ color: '#B79C6E', roughness: 0.72, wetness: 0.24 }), // polímero cor de areia (SCAR-20, 4.4)
  prata: F({ color: '#A8AEB5', roughness: 0.5, wetness: 0.55 }), // Deagle, Five-SeveN (4.4)
  aco: F({ color: '#9CA6B1', roughness: 0.42, wetness: 0.72 }), // lâmina da espátula (CTL6, CTL16): massa prata úmida
});

/** Acento da facção: `acento` na massa de mira, base do carregador e bola da alavanca; `acento2` no seletor/gatilho. */
export const FACTION_ACCENTS = F({
  tr: F({ acento: '#C8553D', acento2: '#F28F3B' }), // Massa Crua: terracota e laranja
  ct: F({ acento: '#2F6DB5', acento2: '#3FB8AF' }), // Tropa do Estúdio: azul e verde-água
  ambos: F({ acento: '#FFD23F', acento2: '#F4EDE1' }), // armas dos dois lados: amarelo-massinha e branco-massa
});

/** Rugosidade/umidade das massas de acento (massinha colorida nova, um pouco mais úmida que o corpo). */
export const ACCENT_CLAY = F({ roughness: 0.6, wetness: 0.4 });

/** Números do gerador (receita → árvore SDF → malha). Unidades: u (polegada na escala do boneco). */
export const WEAPON_MODEL = F({
  soft: 0.25, // k da união suave entre peças do mesmo grupo (a massa apertada uma na outra)
  crease: F({ depth: 0.08, width: 0.18 }), // vinco da costura onde duas massas se encostam
  seamWidth: 0.25, // faixa de costura entre massas de cores diferentes
  cutSoft: 0.12, // k da subtração suave dos cortes (borda do corte de estilete, não quina viva)
  lumps: F({ amp: 0.03, freq: 0.35, octaves: 2 }), // calombos da massa inteira (nenhuma peça é perfeita)
  minThickness: 1.2, // espessura mínima de massa ("fiel e gordinha")
  minBlade: 0.5, // exceção: a lâmina da espátula
  touchRadius: 0.6, // raio do "toque" (onde o dedo mais encosta: digitais) na escala das armas
  lods: F({
    perto: F({ cell: 0.14, maxCells: 1600000 }), // viewmodel e bancada
    mundo: F({ cell: 0.35, maxCells: 300000 }), // no chão e na mão dos outros
  }),
  silhouetteIoU: 0.8, // silhueta lateral do SDF × planta de referência (aceite da 4.1)
});
```

Em `src/data/claySkins.js`, trocar:

```
  ouro: Object.freeze({ id: 8, label: 'Ouro (Gun Game)', params: [1, 0.32, 0, 0], metalness: 1, roughness: 0.34, color: '#E2B53E' }),
});

export const CLAY_SKIN_IDS = Object.freeze(Object.keys(CLAY_SKINS));

```

por:

```
  ouro: Object.freeze({ id: 8, label: 'Ouro (Gun Game)', params: [1, 0.32, 0, 0], metalness: 1, roughness: 0.34, color: '#E2B53E' }),
  // Base (não é skin de jogador): a madeira das armas (Fase 4.1), riscada a palito ao longo do comprimento da peça
  // (QPG2, QPL4, QPG8). Cores B (risco) e C (faixa clara) vêm da massa em src/data/weaponPalette.js.
  veio: Object.freeze({
    id: 9, label: 'Madeira riscada a palito', base: true, colorB: '#4A2C19', colorC: '#A5764D',
    params: [1, 0.16, 0.85, 0], // escala (1 → ~0,45 u entre riscos), largura do risco, força do risco, —
  }),
});

/** Skins de jogador (a Fase 11 desbloqueia): todas menos as de base das peças. */
export const CLAY_SKIN_IDS = Object.freeze(Object.keys(CLAY_SKINS).filter((id) => !CLAY_SKINS[id].base));

```

Em `src/clay/glsl/skins.js`, trocar:

```
    return a;
  #else
```

por:

```
    return a;
  #elif CLAY_SKIN == 9
    // Madeira riscada a palito (base das armas — QPG2, QPL4, QPG8): riscos finos e compridos ao longo de X (o
    // comprimento da coronha e do guarda-mão), um pouco ondulados, que começam e acabam, sobre faixas largas de tom.
    // k.x = escala (1 → ~0,45 u entre riscos), k.y = largura do risco, k.z = força do risco. De longe (risco menor
    // que o pixel) sobra a média, sem chiado.
    vec3 q = p * k.x;
    float wave = clayFbm3(vec3(q.x * 0.12, q.y * 0.55, q.z * 0.55), 2) * 1.4;
    float phase = (q.y + q.z * 0.83) / 0.45 + wave;
    float aa = fwidth(phase) + 1e-4;
    float line = abs(fract(phase) - 0.5) * 2.0;
    float groove = 1.0 - smoothstep(k.y, k.y + aa * 1.5, line);
    float gate = smoothstep(0.1, 0.35, clayNoise3(vec3(q.x * 0.35, floor(phase) * 1.618, 3.7)) * 0.5 + 0.5);
    float far = 1.0 - smoothstep(0.35, 0.7, aa);
    float band = clayFbm3(vec3(q.x * 0.06, q.y * 0.8, q.z * 0.8), 2) * 0.5 + 0.5;
    vec3 col = mix(a, c, band * 0.5);
    return mix(col, b, groove * gate * far * k.z);
  #else
```

- [ ] **Passo 4: Números do viewmodel** (a categoria de cada arma; FOV, offsets, presets, cotovelos e luz da camada para a Tarefa 4)

```js file=src/data/viewmodel.js
// Viewmodel parado (Fase 4.1; desenho em docs/phases/phase-4.md, seção 4.1, "Viewmodel parado"): a arma na mão em
// primeira pessoa, numa camada própria do pipeline, com os dois braços de massinha presos às âncoras da arma. Na 4.1
// não anima (a 4.3 traz as poses-chave do Blender): segura parado, com o boil "em dois".
// Referencial da câmera (o do three): +X direita, +Y cima, −Z frente. Unidades: u (polegada na escala do boneco).
// FOV e offsets como no CS:GO: `viewmodel_fov` é horizontal em 4:3 (o Source mede assim; o vertical fica fixo e telas
// mais largas ganham lado, Hor+), 60 por padrão, 54–68; `viewmodel_offset_x/y/z` (direita, frente, cima) somam por
// cima da posição da categoria, com o padrão do CS (1, 1, −1 — o "Desktop" do viewmodel_presetpos).

const F = Object.freeze;

export const VIEWMODEL = F({
  fov: F({ default: 60, min: 54, max: 68, aspect: 4 / 3 }),
  offset: F({
    x: F({ default: 1, min: -2, max: 2.5 }), // direita (+) / esquerda (−)
    y: F({ default: 1, min: -2, max: 2 }), // frente (+) / trás (−)
    z: F({ default: -1, min: -2, max: 2 }), // cima (+) / baixo (−)
  }),
  // viewmodel_presetpos do CS:GO: 1 Mesa ("Desktop"), 2 Sofá ("Couch"), 3 Clássica ("Classic").
  presets: F({
    1: F({ label: 'Mesa', fov: 60, x: 1, y: 1, z: -1 }),
    2: F({ label: 'Sofá', fov: 54, x: 0, y: 0, z: 0 }),
    3: F({ label: 'Clássica', fov: 68, x: 2.5, y: 0, z: -1.5 }),
  }),
  // Câmera própria da camada: o antebraço passa rente ao olho, então o plano de perto é bem mais curto que o do mundo.
  near: 0.5,
  far: 400,
  /**
   * Posição por categoria: `pos` = a origem da arma (o eixo do cano acima do gatilho) no referencial da câmera, antes
   * dos offsets; `angles` = [arfagem, guinada, rolagem] em graus (guinada + vira a boca para o centro da tela, arfagem +
   * levanta a boca, rolagem + tomba o topo para a esquerda); `elbows` = para onde cada antebraço aponta, fora da tela
   * (o cotovelo real fica no alinhamento, a um antebraço do pulso).
   */
  categories: F({
    pistola: F({ pos: F([1.8, -0.9, -13.5]), angles: F([3, 4, -2]), elbows: F({ direita: F([12, -20, 2]), esquerda: F([-10, -20, 0]) }) }),
    rifle: F({ pos: F([4.5, -3.1, -9]), angles: F([4, 1, -2]), elbows: F({ direita: F([15, -18, 6]), esquerda: F([-18, -16, -4]) }) }),
    sniper: F({ pos: F([5, -4.1, -9.6]), angles: F([3.5, 1, -1.5]), elbows: F({ direita: F([15, -18, 6]), esquerda: F([-18, -17, -8]) }) }),
    escopeta: F({ pos: F([4.5, -3.2, -9.2]), angles: F([4, 1, -2]), elbows: F({ direita: F([15, -18, 6]), esquerda: F([-18, -17, -6]) }) }),
    smgBullpup: F({ pos: F([4.9, -4, -14.5]), angles: F([4, 2, -2]), elbows: F({ direita: F([14, -19, 4]), esquerda: F([-14, -19, -2]) }) }),
    faca: F({ pos: F([3.4, -2.4, -10.5]), angles: F([10, 18, -30]), elbows: F({ direita: F([16, -16, 4]), esquerda: F([-9, -20, 4]) }) }),
  }),
  // Categoria de cada arma com receita (as da 4.4 entram aqui junto com a receita) e, quando a silhueta pede, um ajuste
  // fino somado à posição da categoria (`nudge`, u no referencial da câmera): a alça de transporte da M4A4 fica mais
  // alta que a tampa da AK, então a M4 desce um pouco para não tapar o lado direito da tela.
  weapons: F({
    glock: F({ category: 'pistola' }),
    ak47: F({ category: 'rifle' }),
    m4a4: F({ category: 'rifle', nudge: F([0.3, -0.6, -0.4]) }),
    awp: F({ category: 'sniper' }),
    nova: F({ category: 'escopeta' }),
    p90: F({ category: 'smgBullpup' }),
    knife: F({ category: 'faca' }),
  }),
  // Luz da camada: cópias das luzes do mapa (mesmas posições, cores e intensidades, lidas a cada quadro), a hemisférica
  // e o ambiente assado.
  light: F({
    // Sombra própria (a mão na arma, a arma nos dedos): cada luz que faz sombra no mapa ganha, na cópia, uma câmera de
    // sombra apertada numa esfera em volta da arma e dos pulsos (+ `padding` u). Lado do mapa = o do nível de sombra ×
    // `mapScale`, entre `minSize` e `maxSize`; some com as sombras desligadas. `softness` multiplica o raio do filtro.
    selfShadow: F({ mapScale: 0.5, minSize: 512, maxSize: 1024, padding: 2, bias: -0.0006, normalBias: 0.04, softness: 1.2 }),
    // O set tapa a luz: do centro da arma, da boca e dos pulsos, um raio até cada luz que faz sombra no mapa (no mundo
    // de colisão); a fração livre multiplica a cópia. Suaviza (constantes de tempo em s, subindo e descendo) para não
    // piscar ao passar rente a uma quina.
    occlusion: F({ points: F(['centro', 'boca', 'maoDireita', 'maoEsquerda']), rise: 0.08, fall: 0.14 }),
    // s entre as varreduras da cena do mapa atrás de luzes que entraram (uma que saiu aparece na hora).
    rescan: 1,
  }),
});
```

- [ ] **Passo 5: A receita — validação e árvores por grupo**

```js file=src/weapons/model/recipe.js
// Receita de arma de massinha (Fase 4.1; formato em docs/phases/phase-4.md, seção 4.1, "Receita"): validação e as
// árvores SDF de cada grupo animável. Puro (sem three.js): o gerador (weaponModel.js), os testes do Node e o
// exportador do Blender (pela mesma validação, via tools/blender.mjs) usam o mesmo código.
// Referencial da arma: +X para a boca do cano, +Y para cima, +Z para o lado direito; origem no eixo do cano sobre o
// gatilho. Unidades: u (polegada na escala do boneco).

import { WEAPONS } from '../../data/weapons.js';
import { ACCENT_CLAY, FACTION_ACCENTS, WEAPON_CLAYS, WEAPON_MODEL } from '../../data/weaponPalette.js';
import { HAND_POSES } from '../../data/hands.js';

export const RECIPE_VERSION = 1;

/** Formas aceitas numa peça (as do SDF, src/clay/sdf/shapes.js) e os parâmetros de cada uma. */
export const RECIPE_SHAPES = Object.freeze({
  roundBox: Object.freeze(['size', 'r']),
  cylinder: Object.freeze(['h', 'r', 'round']),
  capsule: Object.freeze(['a', 'b', 'r']),
  sphere: Object.freeze(['r']),
  ellipsoid: Object.freeze(['radii']),
  roundCone: Object.freeze(['a', 'b', 'ra', 'rb']),
  torus: Object.freeze(['R', 'r']),
  cone: Object.freeze(['h', 'r1', 'r2']),
  profile: Object.freeze(['points', 'h', 'round', 'corner']),
  lathe: Object.freeze(['points', 'corner', 'closed']),
  tube: Object.freeze(['points', 'r', 'radii']),
});

/** Grupos que se mexem (cada um vira malha própria); `corpo` é obrigatório. */
export const RECIPE_GROUPS = Object.freeze(['corpo', 'carregador', 'ferrolho', 'slide', 'gatilho', 'bomba', 'alavanca', 'silenciador']);

/** Âncoras: as de mão levam a pose; `boca` e `ejecao` apontam pelo +X da própria rotação. */
export const RECIPE_ANCHORS = Object.freeze(['maoDireita', 'maoEsquerda', 'boca', 'ejecao', 'mira']);
const HAND_ANCHORS = Object.freeze(['maoDireita', 'maoEsquerda']);

/** Massas especiais resolvidas pela facção. */
export const ACCENT_SLOTS = Object.freeze(['acento', 'acento2']);

const fail = (id, where, msg) => {
  throw new Error(`receita de arma ${id ?? '?'} inválida em ${where}: ${msg}`);
};

const isVec = (v, n) => Array.isArray(v) && v.length === n && v.every((c) => typeof c === 'number' && Number.isFinite(c));

/** Facção do acento de uma arma: 'tr', 'ct' ou 'ambos' (as dos dois lados, a faca). */
export function weaponFaction(id) {
  const team = WEAPONS[id]?.team;
  return team === 'tr' || team === 'ct' ? team : 'ambos';
}

/** Menor espessura de uma peça (u), pela forma. */
export function partThickness(part) {
  switch (part.shape) {
    case 'profile':
      return 2 * part.h;
    case 'lathe':
      return 2 * Math.max(...part.points.map((p) => p[1]));
    case 'tube':
      return 2 * (part.radii ? Math.min(...part.radii) : part.r);
    case 'cylinder':
      return 2 * Math.min(part.r, part.h);
    case 'capsule':
    case 'sphere':
    case 'torus':
      return 2 * part.r;
    case 'ellipsoid':
      return 2 * Math.min(...part.radii);
    case 'roundBox':
      return 2 * Math.min(...part.size);
    case 'roundCone':
      return 2 * Math.min(part.ra, part.rb);
    case 'cone':
      return 2 * Math.max(part.r1, part.r2);
    default:
      return 0;
  }
}

/**
 * Valida uma receita e devolve a mesma receita (congelada em profundidade não; só conferida). Lança Error dizendo
 * a arma, o lugar e o problema.
 */
export function validateRecipe(recipe) {
  const id = recipe?.id;
  if (!recipe || typeof recipe !== 'object') fail(id, 'raiz', 'a receita precisa ser um objeto');
  if (typeof id !== 'string' || !WEAPONS[id]) fail(id, 'id', `arma desconhecida ${JSON.stringify(id)}`);
  if (recipe.version !== RECIPE_VERSION) fail(id, 'version', `formato ${recipe.version} (esperado ${RECIPE_VERSION})`);
  const mats = recipe.materials;
  if (!mats || typeof mats !== 'object') fail(id, 'materials', 'faltam as massas');
  for (const [slot, clay] of Object.entries(mats)) {
    if (!(ACCENT_SLOTS.includes(clay) || WEAPON_CLAYS[clay])) fail(id, `materials.${slot}`, `massa desconhecida ${JSON.stringify(clay)}`);
  }
  const groups = recipe.groups;
  if (!groups || typeof groups !== 'object' || !groups.corpo) fail(id, 'groups', "falta o grupo 'corpo'");
  for (const [g, def] of Object.entries(groups)) {
    if (!RECIPE_GROUPS.includes(g)) fail(id, `groups.${g}`, `grupo desconhecido (use ${RECIPE_GROUPS.join(', ')})`);
    if (def.pivot !== undefined && !isVec(def.pivot, 3)) fail(id, `groups.${g}.pivot`, 'precisa ser [x, y, z]');
    if (def.axis !== undefined && !isVec(def.axis, 3)) fail(id, `groups.${g}.axis`, 'precisa ser [x, y, z]');
  }
  const anchors = recipe.anchors ?? {};
  for (const [a, def] of Object.entries(anchors)) {
    if (!RECIPE_ANCHORS.includes(a)) fail(id, `anchors.${a}`, `âncora desconhecida (use ${RECIPE_ANCHORS.join(', ')})`);
    if (!isVec(def.pos, 3)) fail(id, `anchors.${a}.pos`, 'precisa ser [x, y, z]');
    if (def.rot !== undefined && !isVec(def.rot, 3)) fail(id, `anchors.${a}.rot`, 'precisa ser [x, y, z] (Euler XYZ, rad)');
    if (HAND_ANCHORS.includes(a) && !HAND_POSES[def.pose]) fail(id, `anchors.${a}.pose`, `pose de mão desconhecida ${JSON.stringify(def.pose)}`);
  }
  if (!anchors.maoDireita) fail(id, 'anchors', "falta a âncora 'maoDireita'");
  const melee = WEAPONS[id].slot === 'melee';
  if (!melee) for (const a of ['boca', 'ejecao', 'maoEsquerda']) if (!anchors[a]) fail(id, 'anchors', `falta a âncora '${a}'`);
  const parts = recipe.parts;
  if (!Array.isArray(parts) || parts.length === 0) fail(id, 'parts', 'a arma não tem peças');
  const names = new Set();
  const minimum = recipe.minThickness ?? WEAPON_MODEL.minThickness;
  for (let i = 0; i < parts.length; i++) {
    const p = parts[i];
    const where = `parts[${i}] (${p?.name ?? 'sem nome'})`;
    if (typeof p?.name !== 'string' || !p.name) fail(id, where, 'peça sem nome');
    if (names.has(p.name)) fail(id, where, 'nome repetido');
    names.add(p.name);
    if (!groups[p.group]) fail(id, where, `grupo ${JSON.stringify(p.group)} não existe em 'groups'`);
    if (!mats[p.mat]) fail(id, where, `massa ${JSON.stringify(p.mat)} não existe em 'materials'`);
    if (!RECIPE_SHAPES[p.shape]) fail(id, where, `forma desconhecida ${JSON.stringify(p.shape)}`);
    if (p.pos !== undefined && !isVec(p.pos, 3)) fail(id, where, "'pos' precisa ser [x, y, z]");
    if (p.rot !== undefined && !isVec(p.rot, 3)) fail(id, where, "'rot' precisa ser [x, y, z]");
    if (p.op !== undefined && p.op !== 'subtract') fail(id, where, `op ${JSON.stringify(p.op)} (só 'subtract')`);
    if (p.k !== undefined && !(p.k >= 0)) fail(id, where, "'k' precisa ser ≥ 0");
    if (p.op !== 'subtract') {
      const min = p.thin ? WEAPON_MODEL.minBlade : minimum;
      const t = partThickness(p);
      if (!(t >= min - 1e-9)) fail(id, where, `mais fina que a massa mínima (${t.toFixed(3)} u < ${min} u)`);
    }
  }
  for (const g of Object.keys(groups)) {
    if (!parts.some((p) => p.group === g && p.op !== 'subtract')) fail(id, `groups.${g}`, 'grupo sem nenhuma peça de massa');
  }
  return recipe;
}

/** Massas usadas pelas peças, na ordem em que aparecem: o índice é o `mat` da árvore e do array de materiais. */
export function materialSlots(recipe) {
  const out = [];
  for (const p of recipe.parts) if (p.op !== 'subtract' && !out.includes(p.mat)) out.push(p.mat);
  return out;
}

/**
 * Massa de um slot já com a facção: {color, roughness, wetness, skin?, colorB?, colorC?}.
 * @param {object} recipe
 * @param {string} slot
 * @param {'tr'|'ct'|'ambos'} [faction] padrão: a facção da arma
 */
export function resolveClay(recipe, slot, faction = weaponFaction(recipe.id)) {
  const clay = recipe.materials[slot];
  if (ACCENT_SLOTS.includes(clay)) {
    const accents = FACTION_ACCENTS[faction] ?? FACTION_ACCENTS.ambos;
    return { color: accents[clay], roughness: ACCENT_CLAY.roughness, wetness: ACCENT_CLAY.wetness };
  }
  return { ...WEAPON_CLAYS[clay] };
}

// Nó SDF de uma peça no referencial da arma (os parâmetros da forma passam direto).
function partNode(p, matIndex) {
  const node = { type: p.shape, mat: matIndex };
  for (const key of RECIPE_SHAPES[p.shape]) if (p[key] !== undefined) node[key] = p[key];
  if (p.pos) node.pos = p.pos;
  if (p.rot) node.rot = p.rot;
  return node;
}

/**
 * Árvore SDF de cada grupo, no referencial do pivô do grupo (a malha gira em volta dele).
 * Peças somadas numa união suave com vinco por suavidade (peças com `k`/`crease` próprios num grupo à parte),
 * calombos por cima, e os cortes numa subtração suave.
 * @returns {{materials:string[], groups:Object<string, {tree:object, pivot:number[], axis:number[]|null}>}}
 */
export function recipeTrees(recipe) {
  // `soft` opcional na receita: {k, crease: {depth, width}, lumps: {amp, freq, octaves}} por cima do padrão.
  const k0 = recipe.soft?.k ?? WEAPON_MODEL.soft;
  const crease = { ...WEAPON_MODEL.crease, ...(recipe.soft?.crease ?? {}) };
  const lumps = { ...WEAPON_MODEL.lumps, ...(recipe.soft?.lumps ?? {}) };
  const seamWidth = WEAPON_MODEL.seamWidth;
  const slots = materialSlots(recipe);
  const groups = {};
  for (const [name, def] of Object.entries(recipe.groups)) {
    const pivot = def.pivot ?? [0, 0, 0];
    const mine = recipe.parts.filter((p) => p.group === name);
    // Baldes por suavidade: n-ário (raso) em vez de uma cadeia binária de dezenas de níveis.
    const buckets = new Map();
    for (const p of mine) {
      if (p.op === 'subtract') continue;
      const k = p.k ?? k0;
      const c = { ...crease, ...(p.crease ?? {}) };
      const key = `${k}|${c.depth}|${c.width}`;
      if (!buckets.has(key)) buckets.set(key, { k, crease: c, nodes: [] });
      buckets.get(key).nodes.push(partNode(p, slots.indexOf(p.mat)));
    }
    const unions = [...buckets.values()].map((b) => ({
      type: 'smoothUnionCrease', k: b.k, depth: b.crease.depth, width: b.crease.width, seamWidth, children: b.nodes,
    }));
    let tree = unions.length === 1 ? unions[0] : {
      type: 'smoothUnionCrease', k: k0, depth: crease.depth, width: crease.width, seamWidth, children: unions,
    };
    if (lumps.amp > 0) {
      tree = { type: 'displace', amp: lumps.amp, freq: lumps.freq, octaves: lumps.octaves, seed: `${recipe.id}:${name}`, child: tree };
    }
    const cuts = mine.filter((p) => p.op === 'subtract').map((p) => partNode(p, 0));
    if (cuts.length) {
      tree = { type: 'smoothSubtract', k: WEAPON_MODEL.cutSoft, a: tree, b: cuts.length === 1 ? cuts[0] : { type: 'union', children: cuts } };
    }
    if (pivot.some((c) => c !== 0)) tree = { type: 'transform', pos: pivot.map((c) => -c), child: tree };
    groups[name] = { tree, pivot, axis: def.axis ?? null };
  }
  return { materials: slots, groups };
}

/** Árvore da arma inteira no referencial da arma (todos os grupos na posição de repouso): silhueta e testes. */
export function recipeWholeTree(recipe) {
  const { groups } = recipeTrees(recipe);
  const children = Object.values(groups).map((g) => (g.pivot.some((c) => c !== 0) ? { type: 'transform', pos: g.pivot, child: g.tree } : g.tree));
  return children.length === 1 ? children[0] : { type: 'union', children };
}
```

- [ ] **Passo 6: Malhas, materiais e a instância**

```js file=src/weapons/model/weaponModel.js
// Gerador das armas de massinha (Fase 4.1; desenho em docs/phases/phase-4.md, seção 4.1, "Gerador"): a receita vira
// uma malha por grupo animável (SdfMesher: nos Workers e com o cache do IndexedDB), cada malha num Object3D posto no
// pivô do grupo, as âncoras como Object3D vazios e os materiais de massinha com o acento da facção.
// Dois níveis de detalhe: `perto` (viewmodel e bancada) e `mundo` (arma no chão e na mão dos outros, Fases 5, 8 e 9).

import * as THREE from 'three';
import { ClayMaterial } from '../../clay/ClayMaterial.js';
import { bounds } from '../../clay/sdf/nodes.js';
import { WEAPON_MODEL } from '../../data/weaponPalette.js';
import { recipeTrees, resolveClay, validateRecipe, weaponFaction } from './recipe.js';

export const WEAPON_LODS = Object.freeze(Object.keys(WEAPON_MODEL.lods));

const now = () => (globalThis.performance?.now ? globalThis.performance.now() : Date.now());

/**
 * Opções do SdfMesher para a árvore de um grupo num nível: a resolução sai da célula do nível na maior dimensão da
 * caixa (a mesma célula em todas as armas, então a massa tem o mesmo grão na Glock e na AWP).
 * @returns {{resolution:number, maxCells:number, touchRadius:number}}
 */
export function meshOptions(tree, lod) {
  const def = WEAPON_MODEL.lods[lod];
  if (!def) throw new Error(`nível de detalhe desconhecido: ${lod} (use ${WEAPON_LODS.join(', ')})`);
  const b = bounds(tree);
  const extent = Math.max(b.max[0] - b.min[0], b.max[1] - b.min[1], b.max[2] - b.min[2]);
  return {
    resolution: Math.max(8, Math.min(1024, Math.ceil(extent / def.cell))),
    maxCells: def.maxCells,
    touchRadius: WEAPON_MODEL.touchRadius,
  };
}

/**
 * Gera as geometrias de uma receita num nível: uma por grupo, no referencial do pivô do grupo. Quem recebe é dono
 * das geometrias (a biblioteca as marca como compartilhadas).
 * @param {object} recipe receita (src/data/armas/)
 * @param {import('../../clay/sdf/sdfMesher.js').SdfMesher} sdf
 * @param {string} [lod]
 * @returns {Promise<{id:string, lod:string, materials:string[], radius:number, triangles:number, ms:number,
 *   groups:Object<string, {geometry:THREE.BufferGeometry, pivot:number[], axis:number[]|null}>}>}
 */
export async function buildWeaponMeshes(recipe, sdf, lod = 'perto') {
  validateRecipe(recipe);
  const t0 = now();
  const { materials, groups } = recipeTrees(recipe);
  const names = Object.keys(groups);
  const geometries = await Promise.all(names.map((g) => sdf.build(groups[g].tree, meshOptions(groups[g].tree, lod))));
  const out = {};
  const box = new THREE.Box3();
  const part = new THREE.Box3();
  let triangles = 0;
  names.forEach((g, i) => {
    const geometry = geometries[i];
    geometry.name = `arma:${recipe.id}:${g}:${lod}`;
    triangles += geometry.index.count / 3;
    const { pivot, axis } = groups[g];
    box.union(part.copy(geometry.boundingBox).translate(new THREE.Vector3(...pivot)));
    out[g] = { geometry, pivot: [...pivot], axis: axis ? [...axis] : null };
  });
  const size = box.getSize(new THREE.Vector3());
  return { id: recipe.id, lod, materials, radius: size.length() / 2, triangles, ms: now() - t0, groups: out };
}

/**
 * Materiais de massinha de uma arma, um por massa na ordem do `mat` das malhas, com o acento da facção e o boil na
 * medida da arma (`setObjectSize` pelo raio: a AWP ferve em calombos maiores que a Glock, como massa de verdade).
 * @param {object} recipe
 * @param {string[]} slots massas na ordem do `mat` (buildWeaponMeshes().materials)
 * @param {{faction?:'tr'|'ct'|'ambos', radius?:number}} [options]
 * @returns {ClayMaterial[]}
 */
export function createWeaponMaterials(recipe, slots, { faction = weaponFaction(recipe.id), radius = 12 } = {}) {
  return slots.map((slot) => {
    const clay = resolveClay(recipe, slot, faction);
    const material = new ClayMaterial({
      color: clay.color,
      roughness: clay.roughness,
      wetness: clay.wetness,
      skin: clay.skin ?? 'liso',
      colorB: clay.colorB ?? null,
      colorC: clay.colorC ?? null,
      touched: true, // arma é peça de mão: as digitais crescem nas bordas e nos pontos de pega
      seed: `${recipe.id}:${slot}:${faction}`,
    });
    material.name = `arma:${recipe.id}:${slot}:${faction}`;
    material.setObjectSize(radius);
    return material;
  });
}

/**
 * Monta uma instância da arma com geometrias e materiais dados (a instância não é dona deles).
 * `userData.weapon` = {id, lod, faction, radius, parts: {grupo: Object3D no pivô}, anchors: {nome: Object3D}}; cada
 * âncora de mão traz a pose em `userData.pose`, e cada grupo o eixo de giro/deslize em `userData.axis`.
 * @returns {THREE.Group}
 */
export function assembleWeapon(recipe, built, materials, faction = weaponFaction(recipe.id)) {
  const root = new THREE.Group();
  root.name = `arma:${recipe.id}`;
  const parts = {};
  for (const [name, def] of Object.entries(built.groups)) {
    const holder = new THREE.Object3D();
    holder.name = `grupo:${name}`;
    holder.position.fromArray(def.pivot);
    holder.userData.axis = def.axis;
    holder.userData.rest = def.pivot;
    const mesh = new THREE.Mesh(def.geometry, materials);
    mesh.name = `massa:${recipe.id}:${name}`;
    mesh.castShadow = true;
    mesh.receiveShadow = true;
    holder.add(mesh);
    root.add(holder);
    parts[name] = holder;
  }
  const anchors = {};
  for (const [name, def] of Object.entries(recipe.anchors)) {
    const anchor = new THREE.Object3D();
    anchor.name = `ancora:${name}`;
    anchor.position.fromArray(def.pos);
    if (def.rot) anchor.rotation.fromArray(def.rot);
    if (def.pose) anchor.userData.pose = def.pose;
    root.add(anchor);
    anchors[name] = anchor;
  }
  root.userData.weapon = { id: recipe.id, lod: built.lod, faction, radius: built.radius, parts, anchors };
  return root;
}
```

- [ ] **Passo 7: Silhueta lateral e comprimento**

```js file=src/weapons/model/silhouette.js
// Silhueta lateral de uma arma de massinha e a conferência com a planta de referência (Fase 4.1; docs/phases/phase-4.md,
// seção 4.1, "Plantas de referência"). A silhueta é o SDF visto de +Z com o máximo em Z: um ponto (x, y) é massa se
// algum z ali está dentro. A planta (tools/blender/refs/<id>.json) tem a boca do cano em x = 0 e o eixo em y = 0; aqui
// ela é posta na âncora `boca` da receita. Puro (sem three.js): a suíte do Node e a bancada `arsenal` usam o mesmo.

import { bounds, compile } from '../../clay/sdf/nodes.js';
import { recipeWholeTree } from './recipe.js';

/**
 * Grade no plano XY: células de lado `cell` a partir de (x0, y0), `nx` × `ny`; o valor de cada célula é o do centro.
 * @typedef {{x0:number, y0:number, nx:number, ny:number, cell:number}} Grid
 */

/** Grade que cobre uma caixa XY com folga de uma célula. */
export function gridFor(minX, minY, maxX, maxY, cell) {
  const x0 = minX - cell;
  const y0 = minY - cell;
  return { x0, y0, nx: Math.ceil((maxX - x0) / cell) + 1, ny: Math.ceil((maxY - y0) / cell) + 1, cell };
}

/**
 * Máscara da silhueta lateral de uma árvore SDF: raio em Z por célula, avançando pela distância (a árvore é
 * 1-Lipschitz; o fator 0,9 cobre os calombos do `displace`).
 * @param {object} tree
 * @param {Grid} grid
 * @returns {Uint8Array} nx × ny (linha a linha, y crescente)
 */
export function sideMask(tree, grid) {
  const b = bounds(tree);
  const { distance } = compile(tree);
  const { x0, y0, nx, ny, cell } = grid;
  const mask = new Uint8Array(nx * ny);
  for (let j = 0; j < ny; j++) {
    const y = y0 + (j + 0.5) * cell;
    if (y < b.min[1] - cell || y > b.max[1] + cell) continue;
    for (let i = 0; i < nx; i++) {
      const x = x0 + (i + 0.5) * cell;
      if (x < b.min[0] - cell || x > b.max[0] + cell) continue;
      if (hitAlongZ(distance, x, y, b, cell)) mask[j * nx + i] = 1;
    }
  }
  return mask;
}

/** Algum z em (x, y) está dentro da massa? Avança pela distância (o fator 0,9 cobre os calombos do `displace`). */
function hitAlongZ(distance, x, y, b, cell) {
  const minStep = cell * 0.25;
  const z1 = b.max[2] + cell;
  let z = b.min[2] - cell;
  while (z <= z1) {
    const d = distance(x, y, z);
    if (d < 0) return true;
    z += Math.max(d * 0.9, minStep);
  }
  return false;
}

/**
 * Máscara de um polígono com buracos (par/ímpar: o contorno e os buracos juntos), por varredura de linhas.
 * @param {number[][]} outline pontos [x, y]
 * @param {number[][][]} holes
 * @param {Grid} grid
 * @returns {Uint8Array}
 */
export function polygonMask(outline, holes, grid) {
  const { x0, y0, nx, ny, cell } = grid;
  const mask = new Uint8Array(nx * ny);
  const rings = [outline, ...(holes ?? [])];
  const xs = [];
  for (let j = 0; j < ny; j++) {
    const y = y0 + (j + 0.5) * cell;
    xs.length = 0;
    for (const ring of rings) {
      for (let k = 0, n = ring.length; k < n; k++) {
        const [ax, ay] = ring[k];
        const [bx, by] = ring[(k + 1) % n];
        if ((ay > y) !== (by > y)) xs.push(ax + ((y - ay) / (by - ay)) * (bx - ax));
      }
    }
    xs.sort((a, b) => a - b);
    for (let k = 0; k + 1 < xs.length; k += 2) {
      const i0 = Math.max(0, Math.ceil((xs[k] - x0) / cell - 0.5));
      const i1 = Math.min(nx - 1, Math.floor((xs[k + 1] - x0) / cell - 0.5));
      for (let i = i0; i <= i1; i++) mask[j * nx + i] = 1;
    }
  }
  return mask;
}

/** A planta no referencial da arma: a boca do cano da planta vai para a âncora `boca` da receita. */
export function placeReference(recipe, ref) {
  const boca = recipe.anchors?.boca?.pos ?? [0, 0, 0];
  const shift = (p) => [p[0] + boca[0], p[1] + boca[1]];
  return { outline: ref.points.map(shift), holes: (ref.holes ?? []).map((h) => h.map(shift)) };
}

/**
 * IoU da silhueta lateral da receita com a planta (aceite da 4.1: ≥ 0,8), e as áreas em u².
 * @param {object} recipe
 * @param {object} ref planta (tools/blender/refs/<id>.json)
 * @param {{cell?:number}} [options]
 * @returns {{iou:number, sdfArea:number, refArea:number, interArea:number, grid:Grid, sdf:Uint8Array, plan:Uint8Array}}
 */
export function silhouetteIoU(recipe, ref, { cell = 0.1 } = {}) {
  const tree = recipeWholeTree(recipe);
  const b = bounds(tree);
  const { outline, holes } = placeReference(recipe, ref);
  let minX = b.min[0];
  let minY = b.min[1];
  let maxX = b.max[0];
  let maxY = b.max[1];
  for (const [x, y] of outline) {
    minX = Math.min(minX, x);
    minY = Math.min(minY, y);
    maxX = Math.max(maxX, x);
    maxY = Math.max(maxY, y);
  }
  const grid = gridFor(minX, minY, maxX, maxY, cell);
  const sdf = sideMask(tree, grid);
  const plan = polygonMask(outline, holes, grid);
  let a = 0;
  let r = 0;
  let both = 0;
  for (let k = 0; k < sdf.length; k++) {
    a += sdf[k];
    r += plan[k];
    both += sdf[k] & plan[k];
  }
  const union = a + r - both;
  const c2 = cell * cell;
  return { iou: union > 0 ? both / union : 0, sdfArea: a * c2, refArea: r * c2, interArea: both * c2, grid, sdf, plan };
}

/**
 * Comprimento real da arma (u): a extensão em X da silhueta lateral, sem a folga da caixa envolvente (calombos e
 * arredondados). É o número da tabela de escala (docs/phases/phase-4.md, "Unidades e escala"). Só as colunas das pontas
 * são varridas, de fora para dentro, até a primeira com massa (a mesma grade da silhueta inteira, bem mais rápido).
 */
export function silhouetteLength(recipe, { cell = 0.05 } = {}) {
  const tree = recipeWholeTree(recipe);
  const b = bounds(tree);
  const { distance } = compile(tree);
  const grid = gridFor(b.min[0], b.min[1], b.max[0], b.max[1], cell);
  const column = (i) => {
    const x = grid.x0 + (i + 0.5) * cell;
    if (x < b.min[0] - cell || x > b.max[0] + cell) return false;
    for (let j = 0; j < grid.ny; j++) {
      const y = grid.y0 + (j + 0.5) * cell;
      if (y < b.min[1] - cell || y > b.max[1] + cell) continue;
      if (hitAlongZ(distance, x, y, b, cell)) return true;
    }
    return false;
  };
  let i0 = 0;
  while (i0 < grid.nx && !column(i0)) i0++;
  if (i0 === grid.nx) return 0;
  let i1 = grid.nx - 1;
  while (i1 > i0 && !column(i1)) i1--;
  return (i1 - i0 + 1) * cell;
}
```

- [ ] **Passo 8: As plantas de referência e a página que tira o contorno**

```json file=tools/blender/refs/glock.json
{
  "weapon": "glock",
  "note": "Glock 17 (4ª geração, com trilho e as ondas dos dedos): a Glock 18 do jogo é a mesma arma com o seletor no ferrolho. O eixo do cano fica a 38% da face do ferrolho, de cima para baixo (a haste da mola ocupa a parte de baixo); foto espelhada para a boca ficar à direita.",
  "source": {"file":"File:Glock 17 (transparent background).jpg","page":"https://commons.wikimedia.org/wiki/File:Glock_17_(transparent_background).jpg","license":"Public domain","artist":"U.S. Bureau of Alcohol, Tobacco, Firearms and Explosives","credit":"ATF.gov, an official site of the U.S. Department of Justice"},
  "extracted": {"imageWidth":1920,"imageHeight":960,"mirrored":true,"mask":"cor da borda rgb(255, 255, 255), limiar 48","epsilonPx":1.2,"holeMin":0.004,"axis":0.38},
  "lengthU": 7.3,
  "frame": "boca do cano em x = 0, eixo do cano em y = 0, +X para a boca, +Y para cima (u)",
  "points": [
    [-6.3792, 0.6475], [-6.4124, 0.631], [-6.4622, 0.5563], [-6.4622, 0.5314], [-6.4953, 0.4982], [-6.7027, 0.4982], [-6.7442, 0.4816], [-6.794, 0.4153],
    [-6.8106, 0.324], [-6.8106, -0.3064], [-6.8438, -0.3396], [-6.8603, -0.4143], [-6.8438, -0.5221], [-6.794, -0.5802], [-6.5451, -0.6134], [-6.4041, -0.688],
    [-6.288, -0.8373], [-6.2465, -0.9701], [-6.2382, -1.1028], [-6.2631, -1.2355], [-6.3128, -1.3683], [-6.3211, -1.4512], [-6.3377, -1.4927], [-6.3543, -1.4927],
    [-6.3543, -1.5508], [-6.3792, -1.5756], [-6.3958, -1.6835], [-6.429, -1.7084], [-6.429, -1.7664], [-6.4622, -1.7913], [-6.4622, -1.8494], [-6.4787, -1.8494],
    [-6.487, -1.9158], [-6.5119, -1.924], [-6.5119, -1.9738], [-6.5451, -2.007], [-6.5534, -2.0651], [-6.5783, -2.0734], [-6.5783, -2.1231], [-6.6115, -2.1563],
    [-6.6115, -2.1978], [-6.6447, -2.2144], [-6.653, -2.2725], [-6.6778, -2.2808], [-6.6861, -2.3388], [-6.7193, -2.3554], [-6.7276, -2.4052], [-6.7525, -2.4135],
    [-6.7608, -2.4633], [-6.8023, -2.5047], [-6.8023, -2.5379], [-6.8355, -2.5545], [-6.8438, -2.6043], [-6.8769, -2.6209], [-6.8852, -2.6706], [-6.9101, -2.6789],
    [-6.9184, -2.7287], [-6.9516, -2.7536], [-6.9599, -2.8034], [-6.9848, -2.8117], [-7.0014, -2.878], [-7.0263, -2.8863], [-7.0345, -2.9361], [-7.0594, -2.9527],
    [-7.0677, -2.9942], [-7.1009, -3.0356], [-7.1009, -3.0771], [-7.1341, -3.102], [-7.1341, -3.1435], [-7.1839, -3.2347], [-7.1922, -3.3011], [-7.2087, -3.3094],
    [-7.2087, -3.3675], [-7.2336, -3.4006], [-7.2336, -3.4504], [-7.2502, -3.4504], [-7.2585, -3.4753], [-7.3, -3.7408], [-7.3, -3.8652], [-7.2751, -3.8901],
    [-7.2751, -3.915], [-7.1839, -4.0145], [-7.1424, -4.0228], [-7.1009, -4.0809], [-7.018, -4.1058], [-6.9267, -4.1058], [-6.9018, -4.1223], [-6.9267, -4.1638],
    [-6.9516, -4.1638], [-7.0014, -4.2136], [-7.0014, -4.2551], [-7.018, -4.2717], [-7.0097, -4.3878], [-5.8151, -4.4127], [-5.757, -4.4127], [-5.7156, -4.3878],
    [-5.6077, -4.3878], [-5.4667, -4.2385], [-5.4667, -4.0809], [-5.3755, -3.9979], [-5.3589, -3.9979], [-5.3091, -3.9398], [-5.2925, -3.9398], [-5.2344, -3.8735],
    [-5.251, -3.6163], [-5.2261, -3.5168], [-5.1266, -3.3011], [-5.1017, -3.2762], [-5.1017, -3.2513], [-5.0519, -3.2015], [-4.9939, -3.185], [-4.9607, -3.1518],
    [-4.9773, -2.9444], [-4.9607, -2.8117], [-4.9192, -2.7204], [-4.8445, -2.6209], [-4.7865, -2.5794], [-4.745, -2.5711], [-4.7118, -2.5379], [-4.7201, -2.3222],
    [-4.6952, -2.2144], [-4.6123, -2.0153], [-4.5127, -1.8909], [-4.4215, -1.8577], [-4.3468, -1.8577], [-4.2722, -1.8743], [-4.1311, -1.9572], [-4.0482, -1.9738],
    [-3.1937, -1.9738], [-2.5799, -1.9406], [-2.555, -1.924], [-2.555, -1.8826], [-2.6214, -1.7001], [-2.6297, -1.2272], [-2.6214, -1.1692], [-2.5716, -1.053],
    [-2.4803, -0.9701], [-2.3476, -0.9203], [-1.0203, -0.8954], [-0.9789, -0.8456], [-0.9623, -0.8456], [-0.9291, -0.8954], [-0.2323, -0.8622], [-0.1244, -0.7876],
    [-0.1078, -0.7378], [-0.0498, -0.688], [-0.0249, -0.6134], [-0.0249, -0.3645], [-0.0415, -0.3562], [-0.0415, -0.3064], [-0.0332, -0.1986], [0, -0.1571],
    [-0.0083, 0.3489], [-0.0249, 0.3489], [-0.0249, 0.3738], [-0.0415, 0.3738], [-0.0498, 0.4153], [-0.083, 0.4485], [-0.1161, 0.465], [-0.2323, 0.465],
    [-0.3235, 0.5646], [-0.4397, 0.5563], [-0.4728, 0.4733], [-6.1137, 0.4982], [-6.1635, 0.5563], [-6.2382, 0.5729], [-6.2382, 0.6061], [-6.2962, 0.6475]
  ],
  "holes": [
    [
      [-3.1689, -0.9203], [-3.0776, -0.9286], [-2.9781, -0.9784], [-2.8868, -1.0613], [-2.8287, -1.1775], [-2.8287, -1.5425], [-2.8951, -1.6669], [-2.9698, -1.7333],
      [-3.0942, -1.783], [-3.8989, -1.7913], [-4.0482, -1.7581], [-4.1145, -1.725], [-4.2556, -1.6005], [-4.2887, -1.501], [-4.2887, -1.3848], [-4.2473, -1.3765],
      [-4.1892, -1.5093], [-4.156, -1.5425], [-4.1477, -1.5839], [-4.1145, -1.6088], [-4.1063, -1.642], [-3.9818, -1.7415], [-3.9155, -1.7498], [-3.874, -1.7167],
      [-3.874, -1.6586], [-3.9486, -1.418], [-3.9486, -1.3102], [-3.9072, -1.1692], [-3.8242, -1.053], [-3.7412, -1.0115], [-3.2601, -0.9452]
    ]
  ]
}
```

```json file=tools/blender/refs/ak47.json
{
  "weapon": "ak47",
  "note": "AK-47 tipo II (receptor fresado) com coronha fixa, guarda-mãos e empunhadura de madeira; foto espelhada para a boca ficar à direita.",
  "source": {"file":"File:AK-47 type II noBG.png","page":"https://commons.wikimedia.org/wiki/File:AK-47_type_II_noBG.png","license":"CC BY-SA 4.0","artist":"User:Nemo5576","credit":"File:AK-47_type_II_Part_DM-ST-89-01131.jpg"},
  "extracted": {"imageWidth":1920,"imageHeight":744,"mirrored":true,"mask":"alfa","epsilonPx":1.2,"holeMin":0.004,"axis":null},
  "lengthU": 34.6,
  "frame": "boca do cano em x = 0, eixo do cano em y = 0, +X para a boca, +Y para cima (u)",
  "points": [
    [-1.0211, 2.003], [-1.1978, 1.944], [-1.3157, 1.8262], [-1.3157, 1.6299], [-1.2371, 1.5513], [-1.7673, 0.5302], [-1.7673, 0.2946], [-2.2582, 0.2553],
    [-4.0452, 0.2553], [-4.1041, 0.3338], [-4.4183, 0.4124], [-4.595, 0.5106], [-4.811, 0.7266], [-4.9681, 1.0604], [-5.2037, 1.3157], [-7.8154, 1.3157],
    [-7.8743, 1.3746], [-8.3653, 1.3746], [-8.3849, 1.4531], [-8.4635, 1.5317], [-8.7187, 1.5709], [-11.7232, 1.6495], [-12.7246, 1.6299], [-12.7835, 1.5906],
    [-12.8032, 1.4335], [-12.8817, 1.4335], [-12.921, 1.6495], [-13.0388, 1.7673], [-13.2941, 1.7673], [-13.353, 1.728], [-13.3726, 1.7869], [-13.5297, 1.7869],
    [-13.6279, 1.8459], [-13.7457, 1.8459], [-13.785, 1.7869], [-13.9421, 1.7869], [-13.9814, 1.8262], [-14.1188, 1.8459], [-14.217, 1.7673], [-14.9043, 1.7673],
    [-14.9632, 1.8655], [-15.1203, 1.8655], [-15.2381, 1.7673], [-15.2381, 1.728], [-15.4541, 1.728], [-15.4738, 1.8459], [-15.5327, 1.9048], [-15.6505, 1.9048],
    [-15.6701, 1.8066], [-15.6112, 1.6299], [-15.2774, 1.6299], [-15.2185, 1.5513], [-15.5523, 1.512], [-15.5916, 1.3942], [-23.6623, 1.3549], [-23.898, 1.296],
    [-23.9372, 1.2175], [-24.0943, 1.1193], [-24.2514, 0.9426], [-24.3692, 0.7266], [-24.5656, 0.7069], [-24.8209, 0.5106], [-24.8012, 0.4516], [-24.7031, 0.4516],
    [-24.7031, 0.3927], [-24.8602, 0.216], [-24.8798, 0.0785], [-24.8209, 0.0196], [-24.8798, 0], [-25.0762, 0.0589], [-25.6064, -0.0196], [-26.7846, -0.2749],
    [-27.9235, -0.4516], [-28.2573, -0.432], [-28.6304, -0.2356], [-28.8268, -0.1767], [-29.1606, -0.1964], [-34.4822, -1.1193], [-34.6, -1.296], [-34.6, -1.512],
    [-34.5215, -1.6691], [-34.2858, -3.0044], [-34.1287, -3.6328], [-33.9323, -5.1841], [-33.8145, -5.3608], [-33.6574, -5.4198], [-33.4807, -5.4001], [-33.2843, -5.3216],
    [-31.1832, -4.2612], [-31.1243, -4.2023], [-28.8661, -3.2204], [-27.786, -2.6902], [-25.9991, -1.9833], [-25.7242, -1.9048], [-25.4885, -1.8066], [-25.4689, -1.7673],
    [-24.8012, -1.6495], [-24.6638, -1.5709], [-24.5852, -1.5709], [-24.5852, -1.6102], [-24.5067, -1.6495], [-24.5263, -1.8459], [-24.4478, -2.16], [-24.3692, -2.3171],
    [-24.33, -2.6117], [-24.5263, -3.2401], [-24.8405, -4.0255], [-25.0369, -4.4183], [-25.1351, -4.7717], [-25.1351, -4.9288], [-24.978, -5.2627], [-24.762, -5.4983],
    [-24.4281, -5.6554], [-24.0551, -5.6947], [-23.6034, -5.6358], [-23.4463, -5.4983], [-23.3678, -4.9877], [-23.1321, -4.3397], [-22.5234, -2.9455], [-22.1896, -2.4939],
    [-22.1306, -2.5135], [-22.0325, -2.6902], [-21.8361, -2.8277], [-21.247, -2.8473], [-20.5008, -2.8081], [-20.1277, -2.7491], [-19.951, -2.6313], [-19.9117, -2.5135],
    [-19.8135, -2.5135], [-19.7546, -2.435], [-19.6564, -2.435], [-19.5779, -2.4546], [-19.6171, -2.9062], [-19.5975, -2.9455], [-19.5386, -2.9455], [-19.4797, -2.8473],
    [-19.4011, -2.4546], [-19.3422, -2.435], [-19.2244, -2.2779], [-19.2244, -1.512], [-19.1066, -1.4924], [-19.0477, -1.8459], [-19.0084, -1.9048], [-18.9495, -1.9048],
    [-18.6942, -2.8473], [-18.3211, -3.8292], [-17.9284, -4.6146], [-17.3589, -5.5179], [-16.9465, -6.0089], [-16.9465, -6.0481], [-16.8484, -6.1267], [-16.8484, -6.1659],
    [-16.7305, -6.2641], [-16.7305, -6.3034], [-15.9451, -7.0889], [-15.9058, -7.0889], [-15.8272, -7.1871], [-15.788, -7.1871], [-15.788, -7.2263], [-15.7487, -7.2263],
    [-15.6898, -7.3049], [-15.2185, -7.6583], [-14.8258, -7.894], [-14.7079, -8.0314], [-14.5509, -8.0511], [-14.5116, -7.9529], [-14.4134, -7.9136], [-13.6083, -6.6765],
    [-13.6279, -6.5587], [-13.4708, -6.3427], [-13.3334, -6.0678], [-13.785, -5.7928], [-13.9225, -5.6554], [-14.1974, -5.4787], [-14.3152, -5.3412], [-14.3545, -5.3412],
    [-14.8847, -4.8306], [-14.8847, -4.7914], [-15.14, -4.5361], [-15.14, -4.4968], [-15.4541, -4.1237], [-15.8665, -3.4953], [-16.3967, -2.3171], [-16.6127, -1.4728],
    [-16.6127, -1.3942], [-16.5538, -1.3746], [-16.5538, -1.2371], [-14.924, -1.1782], [-14.6098, -1.1389], [-14.5901, -1.0997], [-14.5705, -1.1389], [-14.3545, -1.1389],
    [-14.3152, -1.2764], [-14.217, -1.3746], [-13.8636, -1.3942], [-13.0388, -1.1389], [-11.5464, -1.0997], [-9.1115, -0.9033], [-8.6009, -0.8051], [-8.4242, -0.8444],
    [-8.326, -0.7658], [-8.3064, -0.6873], [-5.3805, -0.648], [-5.3805, -0.7069], [-5.3412, -0.7266], [-5.0467, -0.7266], [-4.9681, -0.6284], [-0.7266, -0.648],
    [-0.6284, -0.5302], [-0.6284, -0.3142], [-0.3731, -0.3338], [-0.3338, -0.2749], [-0.0589, -0.2749], [0, -0.0589], [0, 0.0982], [-0.0982, 0.3142],
    [-0.2553, 0.3142], [-0.2946, 0.2553], [-0.3927, 0.2553], [-0.3927, 0.3731], [-0.4516, 0.4124], [-0.5498, 0.4124], [-0.5891, 1.2371], [-0.5891, 1.5906],
    [-0.5498, 1.6495], [-0.5695, 1.8851], [-0.7266, 1.9833]
  ],
  "holes": [
    [
      [-20.3437, -1.4728], [-20.1081, -1.4728], [-20.0688, -1.4924], [-20.0491, -1.5906], [-20.0295, -2.4939], [-20.1277, -2.6117], [-20.2652, -2.6706], [-20.5401, -2.6902],
      [-21.7575, -2.7099], [-21.8361, -2.6706], [-22.0325, -2.4546], [-22.0521, -2.3957], [-21.9736, -2.2779], [-21.9736, -2.1993], [-21.9932, -2.0619], [-22.0717, -1.9833],
      [-22.0717, -1.5317], [-21.895, -1.6888], [-21.679, -1.7673], [-21.5808, -2.0619], [-21.3844, -2.3368], [-21.1292, -2.4939], [-20.9917, -2.4939], [-20.9721, -2.3957],
      [-21.1488, -2.3368], [-21.3844, -2.0619], [-21.4041, -1.7869], [-21.3452, -1.6495], [-21.1292, -1.4924]
    ],
    [
      [-5.891, 0.5891], [-5.5965, 0.5695], [-5.5965, 0.2946], [-7.7369, 0.2946], [-7.7565, 0.432], [-7.7958, 0.4713], [-8.2867, 0.4909], [-7.8154, 0.5106],
      [-7.8154, 0.5498], [-7.5405, 0.5695]
    ]
  ]
}
```

```json file=tools/blender/refs/m4a4.json
{
  "weapon": "m4a4",
  "note": "Carabina M4A1 (Colt) com guarda-mão de trilhos, torre da massa de mira A2, alça de transporte com a mira traseira no receptor plano (sem luneta) e coronha aberta; a M4A4 do jogo usa a mesma silhueta.",
  "source": {"file":"File:M4A1 Carbine.jpg","page":"https://commons.wikimedia.org/wiki/File:M4A1_Carbine.jpg","license":"Public domain","artist":"Jeff Johnson, Naval Surface Warfare Center","credit":"http://www.dtic.mil/ndia/2003smallarms/john.ppt"},
  "extracted": {"imageWidth":1177,"imageHeight":520,"mirrored":false,"mask":"cor da borda rgb(255, 255, 255), limiar 48","epsilonPx":1.2,"holeMin":0.004,"axis":null},
  "lengthU": 33.1,
  "frame": "boca do cano em x = 0, eixo do cano em y = 0, +X para a boca, +Y para cima (u)",
  "points": [
    [-22.3192, 3.6276], [-22.5523, 3.511], [-22.7563, 3.3071], [-22.7563, 2.6369], [-22.9019, 2.6661], [-23.0476, 2.5787], [-23.3973, 1.6463], [-23.6012, 1.7337],
    [-24.0383, 1.7045], [-24.1257, 1.2966], [-24.0674, 1.0052], [-24.2131, 1.0344], [-24.3879, 0.9761], [-24.4171, 0.9178], [-24.9124, 0.9178], [-24.9707, 0.8013],
    [-25.1164, 0.9761], [-25.2038, 0.9761], [-25.2329, 0.9178], [-30.5068, 0.9178], [-30.5651, 1.1509], [-30.769, 1.3257], [-32.7212, 1.3257], [-32.8086, 1.2383],
    [-32.9252, 0.9178], [-33.0417, -0.1311], [-33.0417, -1.4714], [-33.1, -1.5588], [-33.0417, -1.6171], [-33.0417, -3.3071], [-32.9543, -3.8024], [-32.8669, -3.919],
    [-32.7212, -3.9481], [-32.3133, -3.6276], [-31.7305, -3.4236], [-31.6431, -3.3362], [-31.5557, -3.3362], [-30.5942, -2.87], [-30.5359, -2.87], [-30.5359, -3.5693],
    [-30.3028, -3.6567], [-29.1373, -2.7826], [-28.9625, -2.7243], [-28.7877, -2.5495], [-28.6129, -2.4912], [-28.3215, -2.4912], [-28.3215, -2.8118], [-27.8844, -2.87],
    [-27.7387, -2.8409], [-27.7096, -2.4912], [-26.8063, -2.4912], [-26.7772, -2.2581], [-26.6898, -2.229], [-26.6898, -1.2675], [-25.0581, -1.2675], [-24.9998, -1.1509],
    [-24.9998, -0.6847], [-24.9415, -0.6847], [-24.9124, -0.8013], [-24.621, -0.8013], [-24.621, -1.4132], [-24.5628, -1.6463], [-23.9217, -1.7337], [-23.5138, -2.025],
    [-23.3973, -2.2873], [-23.4264, -2.6661], [-23.5721, -3.074], [-23.6595, -3.1323], [-23.7761, -3.3654], [-23.9509, -3.5402], [-24.5336, -4.4143], [-24.6502, -4.5017],
    [-24.6793, -4.6183], [-25.3786, -5.5215], [-25.4077, -5.6381], [-25.5826, -5.8129], [-25.6991, -6.046], [-25.9322, -6.2791], [-26.0196, -6.4248], [-26.0196, -6.5705],
    [-25.9322, -6.6579], [-25.6117, -6.7744], [-25.3495, -6.8036], [-23.8052, -7.2406], [-23.3681, -7.2698], [-23.1933, -7.1241], [-23.1933, -6.9493], [-23.3099, -6.7744],
    [-23.2224, -6.5122], [-23.135, -6.4539], [-22.8145, -5.9003], [-22.7563, -5.9003], [-22.7563, -5.8129], [-22.6688, -5.7838], [-22.6106, -5.6089], [-22.494, -5.5215],
    [-22.494, -5.4341], [-22.4357, -5.4341], [-22.3775, -5.2884], [-22.2901, -5.201], [-21.9695, -5.1719], [-21.9404, -5.0262], [-22.057, -4.8222], [-21.853, -4.5309],
    [-21.9695, -4.356], [-21.7364, -4.0064], [-20.8915, -4.0064], [-20.804, -3.919], [-18.9975, -3.919], [-18.9101, -4.0064], [-18.6188, -4.0064], [-18.5022, -5.405],
    [-18.24, -6.7453], [-17.5989, -9.018], [-17.395, -9.1928], [-17.1327, -9.1637], [-16.8705, -9.0471], [-16.7248, -9.1054], [-16.55, -9.018], [-16.4043, -9.018],
    [-16.2586, -8.8723], [-14.9766, -8.4935], [-14.8309, -8.5518], [-14.3647, -8.3187], [-15.0931, -5.7546], [-15.268, -4.8222], [-15.3845, -3.511], [-15.3554, -3.4528],
    [-15.1805, -3.4236], [-15.0931, -3.2197], [-15.0931, -3.074], [-15.2388, -2.9283], [-15.2388, -1.7045], [-15.0349, -1.4714], [-14.7435, -1.3257], [-14.6269, -1.0344],
    [-14.6561, -0.8304], [-14.5687, -0.8304], [-14.5978, -1.1509], [-14.5395, -1.1509], [-14.5104, -1.2675], [-13.8402, -1.2092], [-13.6654, -1.0926], [-13.6071, -1.1509],
    [-13.6363, -1.4714], [-13.578, -1.6171], [-13.1118, -1.5297], [-12.9952, -1.5297], [-12.937, -1.6171], [-12.7913, -1.6171], [-12.733, -1.5297], [-12.3542, -1.5297],
    [-12.296, -1.6171], [-12.1794, -1.6171], [-12.1211, -1.5297], [-11.7132, -1.5297], [-11.6841, -1.6171], [-11.5675, -1.6171], [-11.4801, -1.5297], [-11.1305, -1.5297],
    [-11.043, -1.6171], [-10.9265, -1.6171], [-10.8682, -1.5297], [-10.4894, -1.5297], [-10.4312, -1.6171], [-10.3146, -1.6171], [-10.2272, -1.5297], [-9.8776, -1.5297],
    [-9.8193, -1.6171], [-9.6445, -1.6171], [-9.6153, -1.5588], [-9.2074, -1.5588], [-9.12, -1.6463], [-8.9743, -1.5588], [-8.5955, -1.5588], [-8.5664, -1.6171],
    [-7.9836, -1.5588], [-7.8671, -1.6463], [-7.6923, -1.5588], [-7.3426, -1.5588], [-7.2843, -1.6463], [-7.1678, -1.6463], [-7.0512, -1.5588], [-6.7307, -1.5588],
    [-6.6433, -1.6463], [-5.8566, -1.6463], [-5.7401, -1.5297], [-5.7109, -1.3549], [-5.6526, -1.3257], [-5.6526, -1.0344], [-5.4778, -1.0052], [-5.3904, -1.0926],
    [-5.1282, -1.0926], [-4.9242, -0.8596], [-4.8951, -0.4808], [-4.7785, -0.4516], [-3.9044, -0.4516], [-3.8461, -0.5682], [-3.7296, -0.6265], [-3.7004, -1.1801],
    [-3.2925, -1.2092], [-3.2051, -1.1509], [-3.176, -1.0344], [-2.9137, -1.0635], [-2.7098, -0.8887], [-2.7389, -0.5682], [-2.972, -0.5099], [-3.0011, -0.4516],
    [-2.6806, -0.4516], [-2.4475, -0.539], [-2.0688, -0.539], [-2.0396, -0.4808], [-1.9522, -0.539], [-0.2622, -0.539], [-0.0874, -0.4516], [-0.0583, -0.2477],
    [0, -0.2185], [0, 0.2768], [-0.0583, 0.3059], [-0.0583, 0.4225], [-0.1457, 0.539], [-1.6608, 0.5682], [-1.9813, 0.539], [-2.0105, 0.4808],
    [-2.0979, 0.5682], [-2.3893, 0.5682], [-2.5932, 0.4808], [-3.1177, 0.4808], [-3.2342, 2.8118], [-3.3508, 3.1614], [-3.4673, 3.2779], [-3.7004, 3.3362],
    [-4.021, 3.2197], [-4.2249, 2.9283], [-4.3706, 2.8409], [-4.5454, 2.5204], [-4.7202, 2.3456], [-4.7494, 2.229], [-4.8659, 2.1416], [-4.9825, 1.9085],
    [-5.6235, 1.0635], [-5.6818, 1.1509], [-5.7983, 1.1801], [-5.7983, 1.2966], [-5.7401, 1.2966], [-5.7401, 1.7337], [-5.8275, 1.7919], [-6.6724, 1.7919],
    [-6.7307, 1.7337], [-7.3135, 1.7919], [-7.3426, 1.7337], [-7.6923, 1.7337], [-7.7505, 1.8211], [-7.8962, 1.8211], [-7.9836, 1.7337], [-8.3041, 1.7337],
    [-8.3333, 1.7919], [-8.5372, 1.8211], [-8.5955, 1.7337], [-8.9452, 1.7337], [-9.0326, 1.8211], [-9.1783, 1.8211], [-9.2365, 1.7337], [-9.557, 1.7337],
    [-9.6445, 1.8211], [-9.7901, 1.8211], [-9.8776, 1.7337], [-10.1689, 1.7337], [-10.2563, 1.8211], [-10.4312, 1.8211], [-10.4894, 1.7337], [-10.6351, 1.7337],
    [-11.0722, 1.8211], [-11.1596, 1.7337], [-11.4801, 1.7628], [-11.5092, 1.8211], [-11.6258, 1.8502], [-11.7132, 1.8211], [-11.7132, 1.7628], [-12.092, 1.7628],
    [-12.1503, 1.8502], [-12.296, 1.8502], [-12.3542, 1.7628], [-12.7039, 1.7628], [-12.7913, 1.8502], [-12.9661, 1.8502], [-13.0244, 1.7628], [-13.3449, 1.7919],
    [-13.4032, 1.8794], [-13.5489, 1.8794], [-13.6071, 1.7919], [-13.6363, 1.2092], [-13.7237, 1.2675], [-14.5104, 1.384], [-14.5104, 1.1801], [-14.5978, 1.0926],
    [-14.6852, 1.1218], [-14.6852, 2.5495], [-14.7435, 2.6078], [-14.7435, 2.7243], [-14.9183, 2.8992], [-15.1223, 2.9866], [-20.6292, 3.4528], [-21.008, 3.5402],
    [-21.3285, 3.5402], [-21.4159, 3.5985]
  ],
  "holes": [
    [
      [-18.2691, 2.6078], [-15.5302, 2.5787], [-15.3262, 2.4912], [-15.268, 2.4038], [-15.2388, 1.9959], [-15.7924, 1.9376], [-15.909, 1.9085], [-15.9381, 1.8502],
      [-19.9299, 1.8502], [-20.5127, 1.9376], [-20.6292, 1.9959], [-20.6001, 2.4038], [-20.3961, 2.5787]
    ],
    [
      [-20.1922, -2.4621], [-19.318, -2.4621], [-19.1141, -2.5204], [-18.9393, -2.6661], [-18.8518, -2.8409], [-18.8227, -3.074], [-18.8518, -3.2488], [-18.9393, -3.4528],
      [-19.0558, -3.5402], [-19.0849, -3.6859], [-20.6584, -3.7441], [-20.8623, -3.715], [-20.9497, -3.5985], [-21.0954, -3.5402], [-21.0954, -3.4236], [-21.212, -3.2488],
      [-21.1828, -2.8118], [-20.9497, -2.5495], [-20.6875, -2.4912], [-20.7749, -2.7535], [-20.7166, -3.2488], [-20.4544, -3.6567], [-20.2504, -3.6567], [-20.4544, -3.3654],
      [-20.4835, -2.9574], [-20.4253, -2.7535]
    ],
    [
      [-4.3123, 2.3164], [-4.0501, 2.3164], [-3.9918, 2.229], [-3.9627, 1.7919], [-3.7004, 1.7337], [-3.6422, 1.6463], [-3.6422, 1.0635], [-3.7879, 0.9761],
      [-5.0408, 1.0052], [-5.0699, 1.2383], [-4.9825, 1.2966], [-4.8077, 1.6171], [-4.7202, 1.6463], [-4.6328, 1.8502], [-4.4871, 1.9668], [-4.4871, 2.0542],
      [-4.3415, 2.1999]
    ]
  ]
}
```

```json file=tools/blender/refs/awp.json
{
  "weapon": "awp",
  "note": "Accuracy International Arctic Warfare (PSG 90 sueco) com coronha verde de buraco do polegar, luneta e sem bipé, escalada para o comprimento da AWM .338 (48,4 u): a mesma família e o mesmo desenho da AWP do jogo.",
  "source": {"file":"File:Accuracy International Arctic Warfare - Psg 90 G24.png","page":"https://commons.wikimedia.org/wiki/File:Accuracy_International_Arctic_Warfare_-_Psg_90_G24.png","license":"CC BY-SA 4.0","artist":"Mr Bullitt","credit":"File:Accuracy_International_Arctic_Warfare_-_Psg_90.jpg"},
  "extracted": {"imageWidth":650,"imageHeight":180,"mirrored":false,"mask":"alfa","epsilonPx":1.2,"holeMin":0.004,"axis":null},
  "lengthU": 48.4,
  "frame": "boca do cano em x = 0, eixo do cano em y = 0, +X para a boca, +Y para cima (u)",
  "points": [
    [-30.3103, 3.6983], [-30.3907, 3.4571], [-30.2299, 2.8944], [-30.4711, 2.8944], [-30.4711, 2.7336], [-32.9635, 2.7336], [-33.1243, 2.9748], [-36.6618, 3.0551],
    [-36.6618, 1.3668], [-36.2598, 1.3668], [-36.099, 1.1256], [-32.4007, 1.206], [-32.4007, 0.8844], [-34.089, 0.8844], [-34.2498, 0.7236], [-35.295, 0.804],
    [-35.5362, -0.402], [-40.6013, -0.4824], [-40.7621, -0.2412], [-41.3249, -0.2412], [-42.0485, 0.0804], [-48.1588, 0.0804], [-48.4, -5.3063], [-47.8372, -5.2259],
    [-47.7568, -5.4671], [-44.2997, -5.3063], [-43.9781, -4.1807], [-43.6565, -4.0199], [-41.7269, -3.9395], [-41.0837, -4.2611], [-40.6013, -4.8239], [-39.8777, -5.2259],
    [-38.2698, -5.4671], [-37.3854, -5.8691], [-36.501, -5.9495], [-36.099, -5.6279], [-36.0186, -4.5827], [-35.7774, -3.8591], [-35.4558, -3.5375], [-35.2146, -3.3767],
    [-33.285, -3.4571], [-32.8831, -2.8944], [-32.7223, -2.8944], [-32.6419, -3.3767], [-32.4007, -3.2963], [-32.2399, -3.6179], [-31.9183, -3.6179], [-31.6771, -3.8591],
    [-31.0339, -3.8591], [-29.3455, -3.6179], [-29.1043, -3.1355], [-28.7023, -2.814], [-24.602, -2.0904], [-23.7176, -2.1708], [-23.6372, -2.8944], [-22.994, -3.4571],
    [-22.6724, -3.4571], [-22.2704, -3.1355], [-20.0193, -3.1355], [-19.6173, -3.0551], [-19.3761, -2.7336], [-18.8937, -2.7336], [-18.8133, -2.8944], [-18.4917, -2.8944],
    [-18.4113, -2.7336], [-17.7681, -2.7336], [-17.6877, -2.9748], [-17.4465, -2.9748], [-17.2857, -3.2159], [-16.3209, -3.2963], [-15.4365, -3.1355], [-15.3561, -2.6532],
    [-15.4365, -2.01], [-15.7581, -1.608], [-15.7581, -0.804], [-16.6425, -0.7236], [-16.6425, -0.5628], [-16.4013, -0.4824], [-2.8944, -0.4824], [-2.3316, -0.804],
    [-2.01, -0.804], [-1.6884, -0.6432], [-0.2412, -0.6432], [0, -0.3216], [-0.0804, 0.6432], [-2.0904, 0.6432], [-2.1708, 0.804], [-3.0551, 0.804],
    [-3.1355, 0.5628], [-23.9588, 0.6432], [-23.9588, 0.8844], [-22.7528, 0.804], [-22.592, 0.9648], [-22.592, 2.3316], [-22.7528, 3.2159], [-23.2352, 3.2159],
    [-23.3156, 3.0551], [-25.4864, 3.0551], [-26.612, 2.7336], [-28.7023, 2.7336], [-28.9435, 2.8944], [-29.0239, 3.6983]
  ],
  "holes": [
    [
      [-38.1894, -2.0904], [-37.2246, -2.0904], [-37.0638, -2.3316], [-37.1442, -2.9748], [-37.9482, -3.6179], [-39.0738, -3.5375], [-39.2346, -3.2963], [-39.1542, -2.7336],
      [-38.7522, -2.3316]
    ],
    [
      [-33.9282, -2.3316], [-33.2047, -2.3316], [-33.1243, -2.8944], [-33.3654, -3.2159], [-34.6518, -3.2963], [-35.0538, -3.1355], [-35.1342, -2.814], [-34.893, -2.4924],
      [-34.6518, -2.4924], [-34.2498, -3.1355], [-34.089, -3.1355], [-34.4106, -2.6532], [-34.4106, -2.412]
    ]
  ]
}
```

```json file=tools/blender/refs/nova.json
{
  "weapon": "nova",
  "note": "Benelli M3 Super 90 de coronha sintética preta: a mesma família e o mesmo arranjo da Benelli Nova do jogo (coronha, receptor, bomba, tubo do carregador e cano de 18,5\"), escalada para o comprimento da Nova (39,2 u). Nenhuma foto lateral da Nova sobre fundo limpo no Commons.",
  "source": {"file":"File:Benelli M3.png","page":"https://commons.wikimedia.org/wiki/File:Benelli_M3.png","license":"CC BY-SA 4.0","artist":"Blocatul","credit":"Own work"},
  "extracted": {"imageWidth":1920,"imageHeight":921,"mirrored":false,"mask":"alfa","epsilonPx":1.2,"holeMin":0.004,"axis":null},
  "lengthU": 39.2,
  "frame": "boca do cano em x = 0, eixo do cano em y = 0, +X para a boca, +Y para cima (u)",
  "points": [
    [-24.4309, 1.4703], [-24.5415, 1.4261], [-24.8289, 1.1165], [-24.9173, 0.8733], [-24.9394, 0.6522], [-25.6027, 0.5859], [-26.3544, 0.3869], [-26.8408, 0.1658],
    [-26.9293, 0.1658], [-27.1283, 0.0111], [-27.88, -0.3648], [-28.6538, -0.6743], [-29.6929, -1.006], [-30.2015, -1.006], [-30.3783, -0.8512], [-30.4668, -0.6522],
    [-30.71, -0.6522], [-32.6556, -0.8733], [-38.2714, -1.3818], [-38.9568, -1.4703], [-39.1116, -1.5366], [-39.2, -1.6472], [-39.2, -2.1336], [-39.0673, -4.0792],
    [-39.0231, -5.5605], [-38.9789, -6.069], [-38.9126, -6.1575], [-38.6694, -6.1133], [-38.1387, -5.8922], [-37.6081, -5.7374], [-37.3207, -5.6047], [-34.8002, -4.7425],
    [-33.3852, -4.2118], [-31.0416, -3.438], [-30.8205, -3.438], [-30.7542, -3.4822], [-30.7321, -3.6149], [-30.6437, -3.7033], [-30.2899, -3.8139], [-29.4497, -3.836],
    [-29.0076, -3.7475], [-28.9191, -3.6149], [-28.9191, -3.3496], [-28.8307, -2.9737], [-28.5212, -2.421], [-28.2116, -2.1114], [-27.8579, -1.8682], [-27.5483, -1.7356],
    [-27.2609, -1.6693], [-26.7966, -1.6693], [-26.3323, -1.7577], [-26.1776, -1.9125], [-25.9122, -2.4873], [-25.7575, -2.62], [-25.5364, -2.7084], [-24.9836, -2.7084],
    [-24.2983, -2.5979], [-24.0993, -2.4873], [-23.9003, -2.2883], [-23.834, -2.1557], [-23.5465, -1.9125], [-23.3033, -1.8019], [-22.9275, -1.7356], [-15.5429, -1.7798],
    [-15.4987, -1.9788], [-14.0395, -2.1557], [-10.4799, -2.1557], [-9.8829, -2.1114], [-8.7111, -2.1114], [-8.4237, -2.0893], [-8.3353, -1.9567], [-8.1363, -1.9788],
    [-8.0478, -1.9125], [-8.0257, -2.4431], [-8.0036, -2.5536], [-7.9152, -2.5757], [-7.871, -2.3989], [-7.7825, -2.2883], [-7.8046, -1.824], [-7.1856, -1.824],
    [-7.0971, -1.5808], [-5.4168, -1.5808], [-5.3505, -1.6472], [-4.7977, -1.6472], [-4.7535, -1.5808], [-1.2381, -1.5366], [-1.1718, -1.3597], [-1.1718, -0.807],
    [-1.2823, -0.6301], [-4.6872, -0.6522], [-4.7314, -0.5638], [-4.7093, -0.3869], [-0.0884, -0.3869], [-0.0221, -0.3206], [0, -0.1879], [0, 0.1658],
    [-0.0663, 0.3869], [-0.6191, 0.3869], [-0.6854, 0.5417], [-0.8623, 0.6301], [-1.017, 0.8512], [-1.1055, 0.8512], [-1.1055, 0.9618], [-1.1718, 1.0502],
    [-1.614, 1.205], [-1.813, 1.1829], [-1.9898, 0.7849], [-2.0783, 0.6964], [-2.0783, 0.608], [-2.1888, 0.4975], [-2.2331, 0.3869], [-4.7756, 0.3869],
    [-4.7977, 0.4311], [-5.3947, 0.3869], [-7.1192, 0.3648], [-13.4204, 0.3869], [-17.8644, 0.4754], [-18.5498, 0.5417], [-18.594, 0.6743], [-22.9275, 0.6743],
    [-22.9275, 0.8733], [-23.0159, 1.0723], [-23.7013, 1.1165], [-23.9445, 1.2271], [-24.2319, 1.4703]
  ],
  "holes": [
    [
      [-24.6741, -1.7356], [-24.3646, -1.7577], [-24.2098, -1.9788], [-24.2319, -2.1999], [-24.4088, -2.421], [-24.5636, -2.4873], [-24.8731, -2.5315], [-25.4922, -2.5315],
      [-25.4922, -2.4652], [-25.6027, -2.2883], [-25.6027, -2.0672], [-25.5364, -1.8904], [-25.4258, -1.7577]
    ],
    [
      [-6.8981, -0.3869], [-5.461, -0.3869], [-5.4389, -0.6301], [-7.0971, -0.6522], [-7.1635, -0.409]
    ]
  ]
}
```

```json file=tools/blender/refs/p90.json
{
  "weapon": "p90",
  "note": "FN P90 padrão (foto oficial da FN Herstal) com a mira de anel no alojamento de cima e o carregador translúcido por cima; foto espelhada para a boca ficar à direita.",
  "source": {"file":"File:P90 Official No Bg.png","page":"https://commons.wikimedia.org/wiki/File:P90_Official_No_Bg.png","license":"CC BY 2.5","artist":"FN HERSTAL","credit":"https://www.flickr.com/photos/15725582@N08/2769180422/in/photostream/"},
  "extracted": {"imageWidth":1920,"imageHeight":938,"mirrored":true,"mask":"alfa","epsilonPx":1.2,"holeMin":0.004,"axis":null},
  "lengthU": 19.7,
  "frame": "boca do cano em x = 0, eixo do cano em y = 0, +X para a boca, +Y para cima (u)",
  "points": [
    [-6.2267, 3.825], [-6.2504, 3.7657], [-6.2623, 3.398], [-6.3097, 3.315], [-6.4402, 3.2201], [-6.5113, 3.2082], [-6.535, 3.2319], [-6.7841, 3.2319],
    [-6.8078, 3.2082], [-6.8315, 3.2319], [-7.0569, 3.2319], [-7.0806, 3.2082], [-7.3415, 3.2082], [-7.3534, 3.1371], [-7.6974, 3.1252], [-7.9701, 2.544],
    [-7.9701, 2.5085], [-7.9939, 2.4966], [-8.065, 2.3424], [-8.065, 2.3068], [-8.1006, 2.2713], [-8.1243, 2.1645], [-8.1599, 2.1289], [-8.1599, 2.0933],
    [-8.4564, 1.4885], [-13.7224, 1.5003], [-13.7817, 1.5241], [-15.0745, 1.5122], [-16.2605, 1.5359], [-17.5296, 1.5241], [-18.7986, 1.5478], [-19.2374, 1.5359],
    [-19.2374, 1.5596], [-19.617, 1.5241], [-19.6763, 1.4529], [-19.6763, 1.2513], [-19.5933, 0.5041], [-19.5695, 0.0059], [-19.5577, -1.2513], [-19.5814, -1.3936],
    [-19.5814, -1.7968], [-19.617, -2.3306], [-19.7, -2.9236], [-19.7, -3.0303], [-19.6763, -3.0778], [-19.617, -3.1133], [-19.3798, -3.1252], [-19.2612, -3.1252],
    [-19.2374, -3.1015], [-14.7187, -3.1252], [-14.6712, -3.0778], [-14.6475, -2.9592], [-14.268, -2.9473], [-12.2873, -3.5996], [-11.9789, -3.6826], [-11.9196, -3.8012],
    [-11.8247, -3.9198], [-10.3185, -3.9317], [-9.9983, -3.908], [-9.6424, -3.8487], [-9.0969, -3.6826], [-8.6699, -3.481], [-8.3141, -3.2557], [-8.065, -3.0422],
    [-8.0413, -3.0422], [-7.9346, -2.9236], [-7.9108, -2.9236], [-7.5906, -2.5915], [-7.389, -2.5203], [-6.8553, -2.5203], [-6.7011, -2.5559], [-6.6062, -2.6152],
    [-6.535, -2.6982], [-6.4876, -2.8287], [-6.4876, -3.0066], [-6.7129, -3.7775], [-6.7011, -3.8843], [-6.6062, -3.9554], [-5.4439, -3.9673], [-5.0881, -3.9198],
    [-4.7323, -3.8012], [-4.5069, -3.6826], [-4.2934, -3.5284], [-4.0325, -3.2675], [-3.819, -2.9592], [-3.6648, -2.5796], [-3.6055, -2.3068], [-3.5818, -1.8324],
    [-3.5225, -1.7257], [-3.3683, -1.6071], [-3.2972, -1.5834], [-2.6686, -1.5834], [-2.5262, -1.6427], [-2.4076, -1.7613], [-2.3602, -1.868], [-2.3483, -2.4017],
    [-2.2653, -2.4492], [-1.8977, -2.4492], [-1.8384, -2.034], [-1.8384, -1.868], [-1.8146, -1.8087], [-1.7435, -0.8717], [-1.8384, -0.765], [-1.8502, -0.7175],
    [-1.8858, -0.6938], [-2.0637, -0.421], [-1.4114, -0.4092], [-1.3995, -0.3617], [-1.3284, -0.3617], [-1.3165, -0.4092], [-1.186, -0.4092], [-1.1742, -0.3024],
    [-1.0674, -0.3024], [-1.0437, -0.3262], [-1.0437, -0.4092], [-0.9607, -0.421], [-0.8065, -0.421], [-0.676, -0.3499], [-0.5337, -0.3736], [-0.4744, -0.421],
    [-0.0237, -0.421], [0, -0.3024], [-0.1542, 0.4092], [-0.4863, 0.421], [-0.5812, 0.3617], [-0.676, 0.3617], [-0.7709, 0.421], [-0.8421, 0.421],
    [-0.8539, 0.338], [-1.1742, 0.3143], [-1.186, 0.421], [-1.3165, 0.421], [-1.3165, 0.3736], [-1.4114, 0.3736], [-1.4232, 0.4329], [-1.6604, 0.4329],
    [-1.6842, 0.4092], [-1.6842, 0.3143], [-1.779, 0.3143], [-1.779, 1.2631], [-1.8028, 1.6782], [-1.957, 2.6626], [-2.0518, 3.054], [-2.0874, 3.1133],
    [-2.7753, 3.1133], [-2.7872, 3.0896], [-2.8228, 3.0896], [-2.8465, 3.1608], [-2.8465, 3.8131]
  ],
  "holes": [
    [
      [-11.0064, -0.7294], [-9.678, -0.7413], [-9.4171, -0.8243], [-9.2273, -0.9903], [-9.1206, -1.2038], [-9.0969, -1.4529], [-9.168, -1.6901], [-9.2392, -1.7968],
      [-9.4171, -1.951], [-10.6269, -2.4966], [-10.7929, -2.5322], [-11.0064, -2.5322], [-11.1724, -2.4966], [-11.3741, -2.4017], [-11.5994, -2.212], [-11.7536, -1.951],
      [-11.8129, -1.6664], [-11.7892, -1.4054], [-11.6824, -1.1445], [-11.5282, -0.9548], [-11.2673, -0.7887]
    ],
    [
      [-5.8827, -0.8243], [-5.6218, -0.8243], [-5.4439, -0.8836], [-5.266, -1.0141], [-5.183, -1.1564], [-4.9813, -1.2631], [-4.839, -1.4292], [-4.756, -1.6782],
      [-4.7679, -1.868], [-4.839, -2.0578], [-5.0288, -2.2594], [-5.1474, -2.3187], [-5.2897, -2.3543], [-5.5506, -2.3306], [-5.7641, -2.2238], [-5.8827, -2.1052],
      [-5.9302, -2.0222], [-5.9302, -1.9747], [-6.0606, -1.9866], [-6.0843, -1.9392], [-6.3216, -1.9273], [-6.369, -1.6071], [-6.369, -1.3224], [-6.3334, -1.192],
      [-6.2623, -1.0615], [-6.1674, -0.9548], [-6.0132, -0.8599]
    ],
    [
      [-6.7248, 2.0222], [-6.3453, 1.9866], [-5.3253, 1.7968], [-4.839, 1.7257], [-4.6611, 1.7257], [-4.5425, 1.6901], [-3.8783, 1.5952], [-3.7834, 1.5596],
      [-3.653, 1.441], [-3.8902, 1.4292], [-3.9376, 1.4648], [-6.9739, 1.4766], [-6.8078, 1.7968], [-6.7604, 1.9747]
    ]
  ]
}
```

```html file=tools/silhueta.html
<!doctype html>
<html lang="pt-BR">
<meta charset="utf-8">
<title>MASSACRE — silhueta de referência (ferramenta)</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
  body { margin: 0; background: #2A2320; color: #F6F0E4; font: 14px system-ui, sans-serif; }
  header { padding: 10px 14px; }
  h1 { margin: 0 0 4px; font-size: 18px; }
  code { color: #FFD23F; }
  #view { display: block; max-width: 100%; background: repeating-conic-gradient(#3a322e 0 25%, #2f2825 0 50%) 0 0 / 24px 24px; }
  #out { width: calc(100% - 28px); height: 120px; margin: 8px 14px; background: #1c1715; color: #E8D9A8; font: 12px monospace; }
  #info { padding: 0 14px 12px; color: #E8D9A8; }
</style>
<header>
  <h1>Silhueta de referência de arma (planta)</h1>
  <div>Parâmetros na URL: <code>arquivo</code> (título no Commons, ex. <code>File:AK-47 type II noBG.png</code>),
    <code>comprimento</code> (u), <code>espelhar=1</code> (boca do cano para a esquerda na foto), <code>limiar</code>
    (diferença de cor do fundo, 0–255), <code>buraco</code> (área mínima de um buraco, fração), <code>eixo</code>
    (altura do eixo do cano na boca, fração de cima para baixo; sem ele, o meio da boca), <code>simplifica</code>
    (px), <code>largura</code> (px da imagem usada). A imagem só é lida no canvas; nada vai para o disco.</div>
</header>
<canvas id="view"></canvas>
<textarea id="out" spellcheck="false"></textarea>
<div id="info"></div>
<script type="module">
// Extrai o contorno lateral de uma arma de uma foto de licença livre do Wikimedia Commons (Fase 4.1): fundo por
// transparência ou pela cor da borda (enchimento a partir da borda, então reflexos claros dentro da arma continuam
// arma), maior componente, buracos grandes (guarda-mato, buraco do polegar), contorno pelas arestas dos pixels,
// Douglas-Peucker e o referencial da arma: boca do cano em x = 0, eixo do cano em y = 0, +X para a boca, +Y para cima,
// u pelo comprimento real. O resultado vai para tools/blender/refs/<arma>.json (com a ficha da fonte).
const P = new URLSearchParams(location.search);
const FILE = P.get('arquivo');
const LENGTH = Number(P.get('comprimento') || 0);
const MIRROR = P.get('espelhar') === '1';
const THRESHOLD = Number(P.get('limiar') || 48);
const HOLE_MIN = Number(P.get('buraco') || 0.004);
const AXIS = P.has('eixo') ? Number(P.get('eixo')) : null;
const EPS = Number(P.get('simplifica') || 1.2);
const WIDTH = Number(P.get('largura') || 1600);
const info = document.getElementById('info');
const out = document.getElementById('out');

async function sourceInfo(title) {
  const u = 'https://commons.wikimedia.org/w/api.php?action=query&format=json&origin=*&prop=imageinfo'
    + `&iiprop=url|size|mime|extmetadata&iiurlwidth=${WIDTH}&titles=${encodeURIComponent(title)}`;
  const j = await (await fetch(u)).json();
  const page = Object.values(j.query.pages)[0];
  const ii = page.imageinfo?.[0];
  if (!ii) throw new Error(`arquivo não encontrado no Commons: ${title}`);
  const m = ii.extmetadata || {};
  const strip = (s) => (s || '').replace(/<[^>]+>/g, '').replace(/\s+/g, ' ').trim();
  return {
    file: page.title, page: ii.descriptionurl, url: ii.thumburl || ii.url, width: ii.width, height: ii.height,
    license: strip(m.LicenseShortName?.value), artist: strip(m.Artist?.value), credit: strip(m.Credit?.value).slice(0, 200),
  };
}

function loadImage(url) {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.crossOrigin = 'anonymous';
    img.onload = () => resolve(img);
    img.onerror = () => reject(new Error(`não carregou a imagem: ${url}`));
    img.src = url;
  });
}

// Máscara da arma: 1 = arma. Fundo = transparência, ou pixels parecidos com a cor da borda ligados à borda.
function weaponMask(data, W, H) {
  const n = W * H;
  const px = data.data;
  let transparent = 0;
  for (let i = 0; i < n; i += 97) if (px[i * 4 + 3] < 128) transparent++;
  const mask = new Uint8Array(n);
  if (transparent > (n / 97) * 0.05) {
    for (let i = 0; i < n; i++) mask[i] = px[i * 4 + 3] >= 128 ? 1 : 0;
    return { mask, mode: 'alfa' };
  }
  // Cor do fundo: mediana dos pixels da borda.
  const border = [];
  for (let x = 0; x < W; x++) border.push(x, (H - 1) * W + x);
  for (let y = 0; y < H; y++) border.push(y * W, y * W + W - 1);
  const med = [0, 1, 2].map((c) => {
    const v = border.map((i) => px[i * 4 + c]).sort((a, b) => a - b);
    return v[v.length >> 1];
  });
  const near = (i) => Math.abs(px[i * 4] - med[0]) + Math.abs(px[i * 4 + 1] - med[1]) + Math.abs(px[i * 4 + 2] - med[2]) <= THRESHOLD * 1.5;
  const bg = new Uint8Array(n);
  const stack = [];
  for (const i of border) if (!bg[i] && near(i)) {
    bg[i] = 1;
    stack.push(i);
  }
  while (stack.length) {
    const i = stack.pop();
    const x = i % W;
    const y = (i / W) | 0;
    const nb = [x > 0 ? i - 1 : -1, x < W - 1 ? i + 1 : -1, y > 0 ? i - W : -1, y < H - 1 ? i + W : -1];
    for (const j of nb) if (j >= 0 && !bg[j] && near(j)) {
      bg[j] = 1;
      stack.push(j);
    }
  }
  for (let i = 0; i < n; i++) mask[i] = bg[i] ? 0 : 1;
  // Buracos: regiões com a cor do fundo, fechadas pela arma e grandes (o resto são reflexos na arma).
  const seen = new Uint8Array(n);
  for (let s = 0; s < n; s++) {
    if (seen[s] || !mask[s] || !near(s)) continue;
    const comp = [s];
    seen[s] = 1;
    for (let k = 0; k < comp.length; k++) {
      const i = comp[k];
      const x = i % W;
      const y = (i / W) | 0;
      const nb = [x > 0 ? i - 1 : -1, x < W - 1 ? i + 1 : -1, y > 0 ? i - W : -1, y < H - 1 ? i + W : -1];
      for (const j of nb) if (j >= 0 && !seen[j] && mask[j] && near(j)) {
        seen[j] = 1;
        comp.push(j);
      }
    }
    if (comp.length > n * HOLE_MIN * 0.1) for (const i of comp) mask[i] = 0;
  }
  return { mask, mode: `cor da borda rgb(${med.join(', ')}), limiar ${THRESHOLD}` };
}

// Maior componente de 4-vizinhança.
function largestComponent(mask, W, H) {
  const n = W * H;
  const label = new Int32Array(n);
  let best = 0;
  let bestSize = 0;
  let next = 1;
  for (let s = 0; s < n; s++) {
    if (!mask[s] || label[s]) continue;
    const comp = [s];
    label[s] = next;
    for (let k = 0; k < comp.length; k++) {
      const i = comp[k];
      const x = i % W;
      const y = (i / W) | 0;
      const nb = [x > 0 ? i - 1 : -1, x < W - 1 ? i + 1 : -1, y > 0 ? i - W : -1, y < H - 1 ? i + W : -1];
      for (const j of nb) if (j >= 0 && mask[j] && !label[j]) {
        label[j] = next;
        comp.push(j);
      }
    }
    if (comp.length > bestSize) {
      bestSize = comp.length;
      best = next;
    }
    next++;
  }
  const out = new Uint8Array(n);
  for (let i = 0; i < n; i++) out[i] = label[i] === best ? 1 : 0;
  return out;
}

// Laços do contorno pelas arestas dos pixels (arma à esquerda de cada aresta), com a regra de virar à direita nos
// cantos em sela (dois pixels só na diagonal ficam separados).
function traceLoops(mask, W, H) {
  const at = (x, y) => (x >= 0 && y >= 0 && x < W && y < H ? mask[y * W + x] : 0);
  const key = (x, y) => y * (W + 1) + x;
  const out = new Map();
  const add = (x0, y0, x1, y1) => {
    const k = key(x0, y0);
    if (!out.has(k)) out.set(k, []);
    out.get(k).push([x1, y1]);
  };
  for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
    if (!mask[y * W + x]) continue;
    if (!at(x, y - 1)) add(x + 1, y, x, y);
    if (!at(x - 1, y)) add(x, y, x, y + 1);
    if (!at(x, y + 1)) add(x, y + 1, x + 1, y + 1);
    if (!at(x + 1, y)) add(x + 1, y + 1, x + 1, y);
  }
  const loops = [];
  for (const [k0, list0] of out) {
    while (list0.length) {
      const sx = k0 % (W + 1);
      const sy = (k0 / (W + 1)) | 0;
      const loop = [[sx, sy]];
      let [cx, cy] = list0.shift();
      let dx = cx - sx;
      let dy = cy - sy;
      for (let guard = 0; guard < 4 * W * H; guard++) {
        if (cx === sx && cy === sy) break;
        loop.push([cx, cy]);
        const list = out.get(key(cx, cy));
        let pick = 0;
        if (list.length > 1) {
          // Sela: vira à direita (em coordenadas da imagem, y para baixo).
          const right = [-dy, dx];
          const i = list.findIndex(([nx, ny]) => nx - cx === right[0] && ny - cy === right[1]);
          pick = i >= 0 ? i : 0;
        }
        const [nx, ny] = list.splice(pick, 1)[0];
        dx = nx - cx;
        dy = ny - cy;
        cx = nx;
        cy = ny;
      }
      loops.push(loop);
    }
  }
  return loops;
}

function area(poly) {
  let a = 0;
  for (let i = 0, j = poly.length - 1; i < poly.length; j = i++) a += poly[j][0] * poly[i][1] - poly[i][0] * poly[j][1];
  return a / 2;
}

// Douglas-Peucker num laço fechado (divide no ponto mais longe do primeiro).
function simplify(loop, eps) {
  const dp = (pts) => {
    if (pts.length < 3) return pts;
    const [ax, ay] = pts[0];
    const [bx, by] = pts[pts.length - 1];
    const ex = bx - ax;
    const ey = by - ay;
    const l = Math.hypot(ex, ey) || 1;
    let far = 0;
    let fi = 0;
    for (let i = 1; i < pts.length - 1; i++) {
      const d = Math.abs((pts[i][0] - ax) * ey - (pts[i][1] - ay) * ex) / l;
      if (d > far) {
        far = d;
        fi = i;
      }
    }
    if (far <= eps) return [pts[0], pts[pts.length - 1]];
    const a = dp(pts.slice(0, fi + 1));
    const b = dp(pts.slice(fi));
    return [...a.slice(0, -1), ...b];
  };
  let fi = 0;
  let far = 0;
  for (let i = 1; i < loop.length; i++) {
    const d = Math.hypot(loop[i][0] - loop[0][0], loop[i][1] - loop[0][1]);
    if (d > far) {
      far = d;
      fi = i;
    }
  }
  const a = dp(loop.slice(0, fi + 1));
  const b = dp([...loop.slice(fi), loop[0]]);
  return [...a.slice(0, -1), ...b.slice(0, -1)];
}

async function run() {
  if (!FILE || !(LENGTH > 0)) {
    info.textContent = 'Passe ?arquivo=File:...&comprimento=<u> na URL.';
    return;
  }
  const src = await sourceInfo(FILE);
  const img = await loadImage(src.url);
  const W = img.naturalWidth;
  const H = img.naturalHeight;
  const canvas = document.getElementById('view');
  canvas.width = W;
  canvas.height = H;
  const g = canvas.getContext('2d', { willReadFrequently: true });
  if (MIRROR) {
    g.translate(W, 0);
    g.scale(-1, 1);
  }
  g.drawImage(img, 0, 0);
  g.setTransform(1, 0, 0, 1, 0, 0);
  const { mask: raw, mode } = weaponMask(g.getImageData(0, 0, W, H), W, H);
  const mask = largestComponent(raw, W, H);
  const loops = traceLoops(mask, W, H).map((l) => ({ l, a: area(l) }));
  loops.sort((p, q) => Math.abs(q.a) - Math.abs(p.a));
  const outer = loops[0];
  const total = Math.abs(outer.a);
  const holes = loops.slice(1).filter((h) => Math.abs(h.a) > total * HOLE_MIN && Math.sign(h.a) !== Math.sign(outer.a));
  let minX = Infinity;
  let maxX = -Infinity;
  for (const [x] of outer.l) {
    minX = Math.min(minX, x);
    maxX = Math.max(maxX, x);
  }
  const s = LENGTH / (maxX - minX);
  // Eixo do cano: o meio da boca (1% final do comprimento), ou a fração pedida.
  let top = Infinity;
  let bottom = -Infinity;
  const band = (maxX - minX) * 0.01;
  for (const [x, y] of outer.l) if (x >= maxX - band) {
    top = Math.min(top, y);
    bottom = Math.max(bottom, y);
  }
  const axisY = AXIS === null ? (top + bottom) / 2 : top + (bottom - top) * AXIS;
  const toU = (pts) => {
    const q = simplify(pts, EPS).map(([x, y]) => [+(((x - maxX) * s).toFixed(4)), +((-(y - axisY) * s).toFixed(4))]);
    return area(q) < 0 ? q.reverse() : q; // anti-horário no referencial da arma (y para cima)
  };
  const result = {
    source: { file: src.file, page: src.page, license: src.license, artist: src.artist, credit: src.credit },
    extracted: { imageWidth: W, imageHeight: H, mirrored: MIRROR, mask: mode, epsilonPx: EPS, holeMin: HOLE_MIN, axis: AXIS },
    lengthU: LENGTH,
    frame: 'boca do cano em x = 0, eixo do cano em y = 0, +X para a boca, +Y para cima (u)',
    points: toU(outer.l),
    holes: holes.map((h) => toU(h.l).reverse()),
  };
  // Desenho de conferência: contorno em vermelho, buracos em laranja, eixo em amarelo.
  g.lineWidth = Math.max(2, W / 600);
  const draw = (pts, color) => {
    g.strokeStyle = color;
    g.beginPath();
    pts.forEach(([x, y], i) => {
      const X = maxX + x / s;
      const Y = axisY - y / s;
      if (i) g.lineTo(X, Y);
      else g.moveTo(X, Y);
    });
    g.closePath();
    g.stroke();
  };
  draw(result.points, '#ff2d2d');
  for (const h of result.holes) draw(h, '#ffa53a');
  g.strokeStyle = '#FFD23F';
  g.setLineDash([12, 8]);
  g.beginPath();
  g.moveTo(0, axisY);
  g.lineTo(W, axisY);
  g.stroke();
  out.value = JSON.stringify(result);
  info.textContent = `${src.file} · ${src.license} · ${src.artist} · ${W}×${H} px · ${mode} · ${result.points.length} pontos, `
    + `${result.holes.length} buraco(s) · 1 px = ${s.toFixed(4)} u · altura ${(((bottom - top) * s)).toFixed(2)} u na boca`;
  window.__silhueta = result;
}

run().catch((err) => {
  info.textContent = `erro: ${err.message}`;
  window.__silhueta = { error: err.message };
});
</script>
</html>
```

- [ ] **Passo 9: As sete receitas e o registro**

```js file=src/data/armas/glock.js
// Receita da Glock-18 de massinha (Fase 4.1): armação e empunhadura com as ondas dos dedos em grafite, ferrolho em grafite
// claro com as serrilhas em cortes de estilete e o cano marcado na boca, a massa de mira da frente, o seletor de rajada, o
// gatilho e a base do carregador na cor da facção. Referencial: +X para a boca, +Y para cima, +Z para a direita, origem no
// eixo do cano sobre o gatilho (u). Formato em docs/phases/phase-4.md, seção 4.1, "Receita"; o corpo é JSON puro.
export default {
  "id": "glock",
  "version": 1,
  "refs": { "planta": "tools/blender/refs/glock.json", "pins": ["QPG1", "QPG5", "QPL6", "QCG1"] },
  "materials": { "corpo": "grafite", "claro": "grafiteClaro", "acento": "acento", "acento2": "acento2" },
  "groups": {
    "corpo": { "pivot": [0, 0, 0] },
    "slide": { "pivot": [0.65, 0.08, 0], "axis": [-1, 0, 0] },
    "carregador": { "pivot": [-2.2, -4.15, 0], "axis": [-0.252, -0.968, 0] },
    "gatilho": { "pivot": [-0.05, -0.95, 0], "axis": [0, 0, 1] }
  },
  "anchors": {
    "maoDireita": { "pos": [-3.21, -1.64, 1.45], "rot": [1.5708, -0.32, 0], "pose": "empunhadura" },
    "maoEsquerda": { "pos": [-2.64, -2.14, -1.45], "rot": [-1.5708, 0.32, 0], "pose": "apoio" },
    "boca": { "pos": [4.05, 0, 0], "rot": [0, 0, 0] },
    "ejecao": { "pos": [1.1, 0.6, 0.45], "rot": [0, -1.768, 0.532] }
  },
  "parts": [
    { "name": "armacao", "group": "corpo", "mat": "corpo", "shape": "profile", "h": 0.62, "round": 0.26, "corner": 0.2, "points": [[-2.81, -0.414], [-2.744, -0.58], [-2.354, -0.688], [-2.195, -1], [1.537, -1], [1.702, -0.92], [3.818, -0.862], [4.025, -0.613], [4.009, -0.3], [-2.761, -0.3]] },
    { "name": "empunhadura", "group": "corpo", "mat": "corpo", "shape": "profile", "h": 0.7, "round": 0.34, "corner": 0.3, "points": [[-3.25, -3.741], [-3.25, -3.865], [-3.134, -4.014], [-2.852, -4.122], [-2.951, -4.214], [-2.962, -4.36], [-1.531, -4.36], [-1.417, -4.238], [-1.417, -4.081], [-1.184, -3.873], [-1.201, -3.616], [-1.077, -3.301], [-0.911, -3.152], [-0.911, -2.812], [-0.795, -2.621], [-0.662, -2.538], [-0.645, -2.214], [-0.562, -2.015], [-0.4, -1.868], [-0.4, -0.3], [-2.794, -0.34], [-2.744, -0.58], [-2.354, -0.688], [-2.238, -0.837], [-2.188, -1.103], [-2.562, -2.198], [-3.084, -3.102]] },
    { "name": "guardaMato", "group": "corpo", "mat": "corpo", "shape": "profile", "h": 0.6, "round": 0.24, "corner": 0.22, "points": [[1.7, -0.85], [1.7, -2.25], [1.3, -2.65], [-0.4, -2.65], [-0.8, -2.2], [-0.75, -1.9], [-0.35, -1.9], [-0.35, -2.1], [1.3, -2.1], [1.3, -0.85]] },
    { "name": "guardaVao", "group": "corpo", "mat": "corpo", "shape": "profile", "op": "subtract", "h": 1.4, "round": 0, "corner": 0.24, "points": [[-0.35, -2.1], [1.3, -2.1], [1.3, -0.95], [-0.35, -0.95]] },
    { "name": "ferrolho", "group": "slide", "mat": "claro", "shape": "profile", "h": 0.62, "round": 0.28, "corner": 0.2, "points": [[-2.798, -0.36], [4.016, -0.36], [4.04, 0.349], [3.967, 0.449], [3.767, 0.52], [3.596, 0.52], [3.577, 0.473], [-2.653, 0.498], [-2.761, 0.324]] },
    { "name": "serrilhaDireita", "group": "slide", "mat": "claro", "shape": "profile", "op": "subtract", "pos": [0, 0, 0.66], "h": 0.14, "round": 0, "corner": 0.03, "points": [[-1.15, 1.15], [-2.15, 1.15], [-2.095, 0.95], [-2.095, -0.22], [-2.005, -0.22], [-2.005, 0.95], [-1.895, 0.95], [-1.895, -0.22], [-1.805, -0.22], [-1.805, 0.95], [-1.695, 0.95], [-1.695, -0.22], [-1.605, -0.22], [-1.605, 0.95], [-1.495, 0.95], [-1.495, -0.22], [-1.405, -0.22], [-1.405, 0.95], [-1.295, 0.95], [-1.295, -0.22], [-1.205, -0.22], [-1.205, 0.95]] },
    { "name": "serrilhaEsquerda", "group": "slide", "mat": "claro", "shape": "profile", "op": "subtract", "pos": [0, 0, -0.66], "h": 0.14, "round": 0, "corner": 0.03, "points": [[-1.15, 1.15], [-2.15, 1.15], [-2.095, 0.95], [-2.095, -0.22], [-2.005, -0.22], [-2.005, 0.95], [-1.895, 0.95], [-1.895, -0.22], [-1.805, -0.22], [-1.805, 0.95], [-1.695, 0.95], [-1.695, -0.22], [-1.605, -0.22], [-1.605, 0.95], [-1.495, 0.95], [-1.495, -0.22], [-1.405, -0.22], [-1.405, 0.95], [-1.295, 0.95], [-1.295, -0.22], [-1.205, -0.22], [-1.205, 0.95]] },
    { "name": "janelaEjecao", "group": "slide", "mat": "claro", "shape": "roundBox", "op": "subtract", "pos": [1.1, 0.55, 0.36], "size": [0.75, 0.2, 0.3], "r": 0.08 },
    { "name": "alma", "group": "slide", "mat": "claro", "shape": "cylinder", "op": "subtract", "pos": [3.95, 0, 0], "rot": [0, 0, 1.5708], "r": 0.22, "h": 0.3, "round": 0.04 },
    { "name": "bordaCano", "group": "slide", "mat": "claro", "shape": "torus", "op": "subtract", "pos": [4.07, 0, 0], "rot": [0, 0, 1.5708], "r": 0.05, "R": 0.38 },
    { "name": "miraTras", "group": "slide", "mat": "claro", "shape": "profile", "h": 0.6, "round": 0.12, "corner": 0.08, "points": [[-2.5, 0.42], [-2.05, 0.42], [-2.07, 0.7], [-2.47, 0.72]] },
    { "name": "miraTrasEntalhe", "group": "slide", "mat": "claro", "shape": "roundBox", "op": "subtract", "pos": [-2.28, 0.78, 0], "size": [0.4, 0.14, 0.12], "r": 0.04 },
    { "name": "miraFrente", "group": "slide", "mat": "acento", "shape": "profile", "h": 0.6, "round": 0.12, "corner": 0.08, "points": [[3.59, 0.42], [3.85, 0.42], [3.83, 0.66], [3.61, 0.67]] },
    { "name": "seletor", "group": "slide", "mat": "acento2", "shape": "profile", "pos": [0, 0, -0.5], "h": 0.6, "round": 0.2, "corner": 0.14, "points": [[-2.35, 0.08], [-1.57, 0.1], [-1.5, 0.3], [-2.3, 0.36]] },
    { "name": "gatilho", "group": "gatilho", "mat": "acento2", "shape": "profile", "h": 0.6, "round": 0.2, "corner": 0.14, "points": [[0.1, -0.95], [0.05, -1.4], [-0.1, -1.75], [-0.3, -1.9], [-0.37, -1.7], [-0.23, -1.5], [-0.2, -1.15], [-0.2, -0.95]] },
    { "name": "pente", "group": "carregador", "mat": "corpo", "shape": "profile", "h": 0.6, "round": 0.26, "corner": 0.2, "points": [[-2.9, -4.15], [-1.55, -4.15], [-0.85, -1.35], [-2.1, -1.2]] },
    { "name": "penteBase", "group": "carregador", "mat": "acento", "shape": "profile", "h": 0.74, "round": 0.24, "corner": 0.2, "points": [[-3.1, -4.021], [-2.852, -4.122], [-2.951, -4.214], [-2.96, -4.388], [-1.707, -4.413], [-1.558, -4.388], [-1.417, -4.238], [-1.417, -4.081], [-1.35, -4.02]] }
  ]
};
```

```js file=src/data/armas/ak47.js
// Receita da AK-47 de massinha (Fase 4.1): receptor e tampa em grafite, coronha e guarda-mãos de madeira riscada a palito,
// empunhadura de baquelite, carregador curvo com a base na cor da facção. Referencial: +X para a boca, +Y para cima,
// +Z para a direita, origem no eixo do cano sobre o gatilho (u). Formato em docs/phases/phase-4.md, seção 4.1, "Receita";
// o corpo é JSON puro (o exportador do Blender, tools/blender/massacre_armas.py, grava; o importador lê).
export default {
  "id": "ak47",
  "version": 1,
  "refs": { "planta": "tools/blender/refs/ak47.json", "pins": ["QPG2", "QPL4", "QRF1", "QCG1"] },
  "materials": { "corpo": "grafite", "madeira": "madeira", "empunhadura": "madeiraEscura", "ferrolho": "grafiteClaro", "acento": "acento", "acento2": "acento2" },
  "groups": {
    "corpo": { "pivot": [0, 0, 0] },
    "carregador": { "pivot": [4.65, -1.3, 0], "axis": [0, 0, 1] },
    "ferrolho": { "pivot": [4.7, 0.3, 0.78], "axis": [-1, 0, 0] },
    "gatilho": { "pivot": [-0.28, -1.42, 0], "axis": [0, 0, 1] }
  },
  "anchors": {
    "maoDireita": { "pos": [-4.2, -2.95, 1.4], "rot": [1.5708, -0.18, 0], "pose": "empunhadura" },
    "maoEsquerda": { "pos": [8.81, -0.88, -2.22], "rot": [-2.608, 1.28, 0], "pose": "guardaMao" },
    "boca": { "pos": [21.2, 0, 0], "rot": [0, 0, 0] },
    "ejecao": { "pos": [2.65, 0.3, 1], "rot": [0, -1.816, 0.327] }
  },
  "parts": [
    { "name": "coronha", "group": "corpo", "mat": "madeira", "shape": "profile", "h": 0.8, "round": 0.42, "corner": 0.6, "points": [[-13.4, -1.296], [-12.732, -5.184], [-12.615, -5.361], [-12.281, -5.4], [-6.586, -2.69], [-4.269, -1.767], [-3.387, -1.571], [-3.1, -0.637], [-3.1, 0.853], [-3.621, 0.511], [-3.503, 0.393], [-3.66, 0.216], [-3.68, 0], [-4.406, -0.02], [-6.724, -0.452], [-7.057, -0.432], [-7.627, -0.177], [-7.961, -0.196], [-13.282, -1.119]] },
    { "name": "soleira", "group": "corpo", "mat": "corpo", "shape": "profile", "h": 0.86, "round": 0.4, "corner": 0.4, "points": [[-13.4, -1.296], [-12.929, -3.633], [-12.732, -5.184], [-12.615, -5.361], [-12.281, -5.4], [-12.25, -0.94], [-13.282, -1.119]] },
    { "name": "empunhadura", "group": "corpo", "mat": "empunhadura", "shape": "profile", "h": 0.64, "round": 0.45, "corner": 0.55, "points": [[-3.935, -4.772], [-3.778, -5.263], [-3.562, -5.498], [-3.228, -5.655], [-2.403, -5.636], [-2.246, -5.498], [-1.932, -4.34], [-1.323, -2.945], [-1.1, -2.643], [-1.1, -1.2], [-3.273, -1.2], [-3.385, -1.61], [-3.307, -1.649], [-3.13, -2.612]] },
    { "name": "receptor", "group": "corpo", "mat": "corpo", "shape": "profile", "h": 0.78, "round": 0.3, "corner": 0.3, "points": [[-3.25, -1.52], [4.599, -1.52], [4.646, -1.237], [5.5, -1.206], [5.5, 0.62], [-3.25, 0.62]] },
    { "name": "tampa", "group": "corpo", "mat": "corpo", "shape": "profile", "h": 0.72, "round": 0.55, "corner": 0.45, "points": [[-3, 1], [-3, 0.3], [5.4, 0.3], [5.4, 1.393], [-2.462, 1.355], [-2.698, 1.296]] },
    { "name": "alcaMira", "group": "corpo", "mat": "corpo", "shape": "profile", "h": 0.68, "round": 0.3, "corner": 0.22, "points": [[5.05, 1.391], [5.05, 0.35], [6.35, 0.35], [6.35, 1.767], [6.237, 1.866], [5.746, 1.728], [5.55, 1.905], [5.589, 1.63], [5.981, 1.551], [5.648, 1.512], [5.608, 1.394]] },
    { "name": "guardaMaoCima", "group": "corpo", "mat": "madeira", "shape": "profile", "h": 0.62, "round": 0.5, "corner": 0.45, "points": [[6.25, 1.843], [6.25, 0.42], [12.85, 0.42], [12.85, 1.375], [12.737, 1.532], [8.475, 1.63], [8.318, 1.434], [8.161, 1.767], [7.847, 1.728], [7.572, 1.846], [6.296, 1.767]] },
    { "name": "guardaMaoBaixo", "group": "corpo", "mat": "madeira", "shape": "profile", "h": 0.84, "round": 0.5, "corner": 0.5, "points": [[5.45, 0.46], [5.45, -1.208], [6.61, -1.1], [6.845, -1.139], [6.983, -1.375], [7.336, -1.394], [8.161, -1.139], [9.654, -1.1], [12.85, -0.785], [12.85, 0.46]] },
    { "name": "anelFrente", "group": "corpo", "mat": "corpo", "shape": "roundBox", "pos": [13, -0.2, 0], "size": [0.6, 0.74, 0.9], "r": 0.34 },
    { "name": "blocoGas", "group": "corpo", "mat": "corpo", "shape": "profile", "h": 0.66, "round": 0.36, "corner": 0.35, "points": [[12.8, 1.468], [12.8, 0.18], [17, 0.18], [17, 0.358], [16.605, 0.511], [15.996, 1.316], [13.385, 1.316], [12.835, 1.375]] },
    { "name": "cano", "group": "corpo", "mat": "corpo", "shape": "lathe", "corner": 0.1, "points": [[5.6, 0], [5.6, 0.62], [16.7, 0.62], [20.58, 0.6], [20.58, 0]] },
    { "name": "baseMira", "group": "corpo", "mat": "corpo", "shape": "profile", "h": 0.64, "round": 0.34, "corner": 0.3, "points": [[19.35, 0.288], [19.35, -0.643], [20.473, -0.648], [20.62, -0.318], [20.611, 1.25], [19.806, 1.25], [19.433, 0.53], [19.433, 0.295]] },
    { "name": "massaMira", "group": "corpo", "mat": "acento", "shape": "capsule", "r": 0.6, "a": [20.08, 1.15, 0], "b": [20.08, 1.42, 0] },
    { "name": "freio", "group": "corpo", "mat": "corpo", "shape": "lathe", "corner": 0.14, "points": [[20.3, 0], [20.3, 0.63], [21.2, 0.61], [21.2, 0]] },
    { "name": "freioInclinado", "group": "corpo", "mat": "corpo", "shape": "roundBox", "op": "subtract", "pos": [21.48, 0.62, 0], "rot": [0, 0, -0.62], "size": [0.45, 0.62, 1.2], "r": 0.08 },
    { "name": "alma", "group": "corpo", "mat": "corpo", "shape": "cylinder", "op": "subtract", "pos": [21, 0, 0], "rot": [0, 0, 1.5708], "r": 0.25, "h": 0.62, "round": 0.06 },
    { "name": "guardaMato", "group": "corpo", "mat": "corpo", "shape": "profile", "h": 0.6, "round": 0.28, "corner": 0.26, "points": [[2, -1.3], [1.95, -3.05], [1.5, -3.5], [-1.15, -3.5], [-1.85, -3.05], [-1.9, -2.35], [-1.2, -2.5], [-1.1, -2.88], [1.1, -2.88], [1.38, -2.6], [1.4, -1.3]] },
    { "name": "seletor", "group": "corpo", "mat": "acento2", "shape": "profile", "pos": [0, 0, 0.7], "h": 0.6, "round": 0.26, "corner": 0.2, "points": [[-3.15, 0.35], [-3, 0.74], [-2.6, 0.82], [0.2, 0.52], [0.65, 0.3], [0.7, -0.45], [0.25, -0.52], [0.1, 0], [-2.4, -0.06], [-3, 0]] },
    { "name": "janelaEjecao", "group": "corpo", "mat": "corpo", "shape": "roundBox", "op": "subtract", "pos": [2.65, 0.3, 0.98], "size": [1.75, 0.34, 0.38], "r": 0.1 },
    { "name": "ferrolhoCorpo", "group": "ferrolho", "mat": "ferrolho", "shape": "roundBox", "pos": [2.65, 0.3, 0.1], "size": [1.6, 0.6, 0.6], "r": 0.24 },
    { "name": "alavanca", "group": "ferrolho", "mat": "ferrolho", "shape": "tube", "r": 0.6, "points": [[4.65, 0.3, 0.55], [4.75, 0.36, 1.2]] },
    { "name": "alavancaBola", "group": "ferrolho", "mat": "ferrolho", "shape": "sphere", "pos": [4.78, 0.38, 1.45], "r": 0.66 },
    { "name": "gatilho", "group": "gatilho", "mat": "acento2", "shape": "profile", "h": 0.6, "round": 0.22, "corner": 0.16, "points": [[-0.05, -1.3], [-0.1, -1.95], [-0.4, -2.4], [-0.85, -2.62], [-1, -2.35], [-0.7, -2.05], [-0.52, -1.6], [-0.52, -1.3]] },
    { "name": "pente", "group": "carregador", "mat": "corpo", "shape": "profile", "h": 0.62, "round": 0.3, "corner": 0.35, "points": [[2.18, -1.28], [2.18, -1.887], [2.879, -3.829], [3.272, -4.615], [4.47, -6.303], [5.412, -7.226], [6.217, -7.8], [7.443, -5.81], [6.315, -4.831], [5.333, -3.495], [4.803, -2.317], [4.587, -1.394], [4.646, -1.28], [6.888, -1.28], [7.336, -1.394], [7.705, -1.28]] },
    { "name": "penteBase", "group": "carregador", "mat": "acento", "shape": "profile", "h": 0.68, "round": 0.3, "corner": 0.3, "points": [[6.028, -7.686], [6.492, -8.031], [6.649, -8.051], [7.592, -6.676], [7.572, -6.559], [7.867, -6.068], [7.279, -5.657]] },
    { "name": "penteFriso1D", "group": "carregador", "mat": "corpo", "shape": "tube", "op": "subtract", "r": 0.18, "points": [[2.95, -2.4, 0.66], [3.85, -4.4, 0.66], [5.35, -6.35, 0.66]] },
    { "name": "penteFriso2D", "group": "carregador", "mat": "corpo", "shape": "tube", "op": "subtract", "r": 0.18, "points": [[4.05, -2.2, 0.66], [4.9, -4.05, 0.66], [6.3, -5.9, 0.66]] },
    { "name": "penteFriso1E", "group": "carregador", "mat": "corpo", "shape": "tube", "op": "subtract", "r": 0.18, "points": [[2.95, -2.4, -0.66], [3.85, -4.4, -0.66], [5.35, -6.35, -0.66]] },
    { "name": "penteFriso2E", "group": "carregador", "mat": "corpo", "shape": "tube", "op": "subtract", "r": 0.18, "points": [[4.05, -2.2, -0.66], [4.9, -4.05, -0.66], [6.3, -5.9, -0.66]] }
  ]
};
```

```js file=src/data/armas/m4a4.js
// Receita da M4A4 de massinha (Fase 4.1): receptores, coronha retrátil e guarda-mão de trilhos em grafite, receptor de cima,
// alça de transporte, cano e abafador em grafite claro, os dentes do trilho em cortes de estilete e a massa de mira, o seletor
// e a base do carregador na cor da facção. Referencial: +X para a boca, +Y para cima, +Z para a direita, origem no eixo do
// cano sobre o gatilho (u). Formato em docs/phases/phase-4.md, seção 4.1, "Receita"; o corpo é JSON puro.
export default {
  "id": "m4a4",
  "version": 1,
  "refs": { "planta": "tools/blender/refs/m4a4.json", "pins": ["QPG5", "QPL6", "QCG1", "QRF4"] },
  "materials": { "corpo": "grafite", "claro": "grafiteClaro", "acento": "acento", "acento2": "acento2" },
  "groups": {
    "corpo": { "pivot": [0, 0, 0] },
    "carregador": { "pivot": [5.2, -3.3, 0], "axis": [0, -1, 0] },
    "ferrolho": { "pivot": [-3.8, 1.6, 0], "axis": [-1, 0, 0] },
    "gatilho": { "pivot": [0.02, -2.45, 0], "axis": [0, 0, 1] }
  },
  "anchors": {
    "maoDireita": { "pos": [-3.8, -3.35, 1.41], "rot": [1.5708, -0.5, 0], "pose": "empunhadura" },
    "maoEsquerda": { "pos": [10.51, -1.33, -2.75], "rot": [-2.608, 1.28, 0], "pose": "guardaMao" },
    "boca": { "pos": [20.4, 0, 0], "rot": [0, 0, 0] },
    "ejecao": { "pos": [1, 0.95, 1.05], "rot": [0, -1.326, 0.283] }
  },
  "parts": [
    { "name": "coronha", "group": "corpo", "mat": "corpo", "shape": "profile", "h": 0.92, "round": 0.42, "corner": 0.35, "points": [[-12.7, -1.559], [-12.642, -3.307], [-12.554, -3.802], [-12.321, -3.948], [-11.913, -3.628], [-10.194, -2.87], [-10.136, -3.569], [-9.903, -3.657], [-8.213, -2.491], [-7.922, -2.491], [-7.922, -2.812], [-7.484, -2.87], [-7.339, -2.841], [-7.31, -2.491], [-6.406, -2.491], [-6.377, -2.258], [-6.29, -2.229], [-6.25, 0.918], [-10.107, 0.918], [-10.165, 1.151], [-10.369, 1.326], [-12.321, 1.326], [-12.525, 0.918]] },
    { "name": "tuboCoronha", "group": "corpo", "mat": "corpo", "shape": "profile", "h": 0.66, "round": 0.5, "corner": 0.3, "points": [[-6.4, 0.918], [-6.4, -1.35], [-6.29, -1.35], [-6.29, -1.267], [-4.658, -1.267], [-4.6, -0.685], [-4.512, -0.801], [-4.221, -0.801], [-4.221, -1.35], [-3.95, -1.35], [-3.95, 0.98], [-4.017, 0.918], [-4.512, 0.918], [-4.571, 0.801], [-4.716, 0.976], [-4.833, 0.918]] },
    { "name": "receptorBaixo", "group": "corpo", "mat": "corpo", "shape": "profile", "h": 0.82, "round": 0.28, "corner": 0.25, "points": [[-4.35, -0.801], [-4.221, -0.801], [-4.163, -1.646], [-3.522, -1.734], [-3.114, -2.025], [-2.997, -2.287], [-3.014, -2.5], [5.161, -2.5], [5.161, -1.704], [5.365, -1.471], [5.656, -1.326], [5.773, -1.034], [5.744, -0.83], [5.831, -0.83], [5.85, -1.151], [5.85, 0.42], [-4.35, 0.42]] },
    { "name": "pocoCarregador", "group": "corpo", "mat": "corpo", "shape": "profile", "h": 0.84, "round": 0.3, "corner": 0.25, "points": [[1.45, -3.967], [1.781, -4.006], [1.787, -4.08], [5.066, -4.08], [5.015, -3.511], [5.219, -3.424], [5.307, -3.22], [5.307, -3.074], [5.161, -2.928], [5.161, -2.3], [1.45, -2.3]] },
    { "name": "empunhadura", "group": "corpo", "mat": "corpo", "shape": "profile", "h": 0.66, "round": 0.45, "corner": 0.5, "points": [[-6.1, -1.35], [-4.221, -1.35], [-4.163, -1.646], [-3.522, -1.734], [-3.114, -2.025], [-2.997, -2.287], [-3.172, -3.074], [-5.532, -6.279], [-5.62, -6.57], [-5.212, -6.774], [-3.405, -7.241], [-2.968, -7.27], [-2.793, -7.124], [-2.91, -6.774], [-2.822, -6.512], [-2.356, -5.813], [-1.89, -5.201], [-1.57, -5.172], [-1.657, -4.822], [-1.55, -4.669], [-1.55, -1.35]] },
    { "name": "guardaMato", "group": "corpo", "mat": "corpo", "shape": "profile", "h": 0.6, "round": 0.26, "corner": 0.24, "points": [[1.5, -2.4], [1.5, -3.95], [1.05, -4.4], [-1, -4.4], [-1.65, -3.9], [-1.7, -3.1], [-0.85, -3.1], [-0.85, -3.8], [1, -3.8], [1, -2.4]] },
    { "name": "seletor", "group": "corpo", "mat": "acento", "shape": "profile", "pos": [0, 0, -0.78], "h": 0.6, "round": 0.26, "corner": 0.2, "points": [[-2.75, -0.3], [-2.1, -0.28], [-1.15, -0.55], [-1.15, -0.98], [-2.1, -1.06], [-2.75, -0.9]] },
    { "name": "receptorCima", "group": "corpo", "mat": "claro", "shape": "profile", "h": 0.8, "round": 0.3, "corner": 0.25, "points": [[-3.8, 1.032], [-3.8, 0.3], [5.9, 0.3], [5.9, 1.382], [5.89, 1.18], [5.802, 1.093], [5.715, 1.122], [5.715, 1.82], [-2.932, 1.82], [-2.997, 1.646], [-3.201, 1.734], [-3.638, 1.705], [-3.726, 1.297], [-3.667, 1.005]] },
    { "name": "alca", "group": "corpo", "mat": "claro", "shape": "profile", "h": 0.62, "round": 0.34, "corner": 0.3, "points": [[-2.85, 2.039], [-2.85, 1.6], [5.3, 1.6], [5.3, 2.977], [-1.919, 3.628], [-2.356, 3.307], [-2.356, 2.637], [-2.648, 2.579]] },
    { "name": "alcaVao", "group": "corpo", "mat": "claro", "shape": "profile", "op": "subtract", "h": 1.4, "round": 0, "corner": 0.2, "points": [[2.131, 2.6078], [4.87, 2.5787], [5.074, 2.4912], [5.132, 2.4038], [5.161, 1.9959], [4.608, 1.9376], [4.491, 1.9085], [4.462, 1.8502], [0.47, 1.8502], [-0.113, 1.9376], [-0.229, 1.9959], [-0.2, 2.4038], [0.004, 2.5787]] },
    { "name": "assistente", "group": "corpo", "mat": "claro", "shape": "capsule", "r": 0.6, "a": [-1.8, 0.95, 0.7], "b": [-2.95, 0.95, 1.08] },
    { "name": "janelaEjecao", "group": "corpo", "mat": "claro", "shape": "roundBox", "op": "subtract", "pos": [1, 0.95, 1], "size": [1.35, 0.34, 0.32], "r": 0.1 },
    { "name": "guardaMao", "group": "corpo", "mat": "corpo", "shape": "profile", "h": 0.96, "round": 0.5, "corner": 0.35, "points": [[5.65, -1.329], [5.831, -0.83], [5.89, -1.267], [6.735, -1.093], [6.822, -1.617], [14.543, -1.646], [14.55, 1.792], [6.851, 1.879], [6.764, 1.209], [5.89, 1.384], [5.802, 1.093], [5.65, 1.95]] },
    { "name": "trilhoCima", "group": "corpo", "mat": "corpo", "shape": "profile", "op": "subtract", "h": 1.3, "round": 0, "corner": 0.05, "points": [[14.2, 2.72], [14.11, 2.22], [14.11, 1.5], [13.85, 1.5], [13.85, 2.22], [13.47, 2.22], [13.47, 1.5], [13.21, 1.5], [13.21, 2.22], [12.83, 2.22], [12.83, 1.5], [12.57, 1.5], [12.57, 2.22], [12.19, 2.22], [12.19, 1.5], [11.93, 1.5], [11.93, 2.22], [11.55, 2.22], [11.55, 1.5], [11.29, 1.5], [11.29, 2.22], [10.91, 2.22], [10.91, 1.5], [10.65, 1.5], [10.65, 2.22], [10.27, 2.22], [10.27, 1.5], [10.01, 1.5], [10.01, 2.22], [9.63, 2.22], [9.63, 1.5], [9.37, 1.5], [9.37, 2.22], [8.99, 2.22], [8.99, 1.5], [8.73, 1.5], [8.73, 2.22], [8.35, 2.22], [8.35, 1.5], [8.09, 1.5], [8.09, 2.22], [7.71, 2.22], [7.71, 1.5], [7.45, 1.5], [7.45, 2.22], [7.07, 2.22], [7.07, 1.5], [6.81, 1.5], [6.81, 2.22], [6.43, 2.22], [6.43, 1.5], [6.17, 1.5], [6.17, 2.22], [6.1, 2.72]] },
    { "name": "trilhoBaixo", "group": "corpo", "mat": "corpo", "shape": "profile", "op": "subtract", "h": 1.3, "round": 0, "corner": 0.05, "points": [[6.1, -2.5], [6.17, -2], [6.17, -1.28], [6.43, -1.28], [6.43, -2], [6.81, -2], [6.81, -1.28], [7.07, -1.28], [7.07, -2], [7.45, -2], [7.45, -1.28], [7.71, -1.28], [7.71, -2], [8.09, -2], [8.09, -1.28], [8.35, -1.28], [8.35, -2], [8.73, -2], [8.73, -1.28], [8.99, -1.28], [8.99, -2], [9.37, -2], [9.37, -1.28], [9.63, -1.28], [9.63, -2], [10.01, -2], [10.01, -1.28], [10.27, -1.28], [10.27, -2], [10.65, -2], [10.65, -1.28], [10.91, -1.28], [10.91, -2], [11.29, -2], [11.29, -1.28], [11.55, -1.28], [11.55, -2], [11.93, -2], [11.93, -1.28], [12.19, -1.28], [12.19, -2], [12.57, -2], [12.57, -1.28], [12.83, -1.28], [12.83, -2], [13.21, -2], [13.21, -1.28], [13.47, -1.28], [13.47, -2], [13.85, -2], [13.85, -1.28], [14.11, -1.28], [14.11, -2], [14.2, -2.5]] },
    { "name": "trilhoDireito", "group": "corpo", "mat": "corpo", "shape": "profile", "op": "subtract", "pos": [0, 0.12, 0], "rot": [1.5708, 0, 0], "h": 0.38, "round": 0, "corner": 0.05, "points": [[14.2, 1.96], [14.11, 1.46], [14.11, 0.76], [13.85, 0.76], [13.85, 1.46], [13.47, 1.46], [13.47, 0.76], [13.21, 0.76], [13.21, 1.46], [12.83, 1.46], [12.83, 0.76], [12.57, 0.76], [12.57, 1.46], [12.19, 1.46], [12.19, 0.76], [11.93, 0.76], [11.93, 1.46], [11.55, 1.46], [11.55, 0.76], [11.29, 0.76], [11.29, 1.46], [10.91, 1.46], [10.91, 0.76], [10.65, 0.76], [10.65, 1.46], [10.27, 1.46], [10.27, 0.76], [10.01, 0.76], [10.01, 1.46], [9.63, 1.46], [9.63, 0.76], [9.37, 0.76], [9.37, 1.46], [8.99, 1.46], [8.99, 0.76], [8.73, 0.76], [8.73, 1.46], [8.35, 1.46], [8.35, 0.76], [8.09, 0.76], [8.09, 1.46], [7.71, 1.46], [7.71, 0.76], [7.45, 0.76], [7.45, 1.46], [7.07, 1.46], [7.07, 0.76], [6.81, 0.76], [6.81, 1.46], [6.43, 1.46], [6.43, 0.76], [6.17, 0.76], [6.17, 1.46], [6.1, 1.96]] },
    { "name": "trilhoEsquerdo", "group": "corpo", "mat": "corpo", "shape": "profile", "op": "subtract", "pos": [0, 0.12, 0], "rot": [1.5708, 0, 0], "h": 0.38, "round": 0, "corner": 0.05, "points": [[6.1, -1.96], [6.17, -1.46], [6.17, -0.76], [6.43, -0.76], [6.43, -1.46], [6.81, -1.46], [6.81, -0.76], [7.07, -0.76], [7.07, -1.46], [7.45, -1.46], [7.45, -0.76], [7.71, -0.76], [7.71, -1.46], [8.09, -1.46], [8.09, -0.76], [8.35, -0.76], [8.35, -1.46], [8.73, -1.46], [8.73, -0.76], [8.99, -0.76], [8.99, -1.46], [9.37, -1.46], [9.37, -0.76], [9.63, -0.76], [9.63, -1.46], [10.01, -1.46], [10.01, -0.76], [10.27, -0.76], [10.27, -1.46], [10.65, -1.46], [10.65, -0.76], [10.91, -0.76], [10.91, -1.46], [11.29, -1.46], [11.29, -0.76], [11.55, -0.76], [11.55, -1.46], [11.93, -1.46], [11.93, -0.76], [12.19, -0.76], [12.19, -1.46], [12.57, -1.46], [12.57, -0.76], [12.83, -0.76], [12.83, -1.46], [13.21, -1.46], [13.21, -0.76], [13.47, -0.76], [13.47, -1.46], [13.85, -1.46], [13.85, -0.76], [14.11, -0.76], [14.11, -1.46], [14.2, -1.96]] },
    { "name": "torreMira", "group": "corpo", "mat": "corpo", "shape": "profile", "h": 0.62, "round": 0.28, "corner": 0.2, "points": [[14.5, -1.25], [14.747, -1.25], [14.747, -1.034], [15.272, -1.093], [15.476, -0.86], [15.505, -0.481], [15.621, -0.452], [16.496, -0.452], [16.67, -0.626], [16.7, -1.18], [17.15, -1.181], [17.15, 2.859], [16.933, 3.278], [16.7, 3.336], [16.379, 3.22], [16.029, 2.841], [14.776, 1.064], [14.602, 1.18], [14.66, 1.734], [14.5, 1.792]] },
    { "name": "torreVao", "group": "corpo", "mat": "corpo", "shape": "profile", "op": "subtract", "h": 1.4, "round": 0, "corner": 0.18, "points": [[16.088, 2.3164], [16.35, 2.3164], [16.408, 2.229], [16.437, 1.7919], [16.7, 1.7337], [16.758, 1.6463], [16.758, 1.0635], [16.612, 0.9761], [15.359, 1.0052], [15.33, 1.2383], [15.417, 1.2966], [15.592, 1.6171], [15.68, 1.6463], [15.767, 1.8502], [15.913, 1.9668], [15.913, 2.0542], [16.058, 2.1999]] },
    { "name": "massaMira", "group": "corpo", "mat": "acento", "shape": "capsule", "r": 0.6, "a": [16.1, 1.3, 0], "b": [16.1, 1.72, 0] },
    { "name": "cano", "group": "corpo", "mat": "claro", "shape": "lathe", "corner": 0.1, "points": [[5.7, 0], [5.7, 0.62], [17.85, 0.62], [17.85, 0]] },
    { "name": "abafador", "group": "corpo", "mat": "claro", "shape": "lathe", "corner": 0.14, "points": [[17.7, 0], [17.7, 0.68], [20.2, 0.64], [20.4, 0.52], [20.4, 0]] },
    { "name": "abafadorFenda1", "group": "corpo", "mat": "claro", "shape": "capsule", "op": "subtract", "r": 0.17, "a": [18.35, 0, 0.66], "b": [19.8, 0, 0.66] },
    { "name": "abafadorFenda2", "group": "corpo", "mat": "claro", "shape": "capsule", "op": "subtract", "r": 0.17, "a": [18.35, -0.5716, -0.33], "b": [19.8, -0.5716, -0.33] },
    { "name": "abafadorFenda3", "group": "corpo", "mat": "claro", "shape": "capsule", "op": "subtract", "r": 0.17, "a": [18.35, 0.5716, -0.33], "b": [19.8, 0.5716, -0.33] },
    { "name": "alma", "group": "corpo", "mat": "claro", "shape": "cylinder", "op": "subtract", "pos": [20.2, 0, 0], "rot": [0, 0, 1.5708], "r": 0.26, "h": 0.62, "round": 0.06 },
    { "name": "alavancaHaste", "group": "ferrolho", "mat": "claro", "shape": "roundBox", "pos": [-3.65, 1.6, 0], "size": [0.62, 0.6, 0.6], "r": 0.26 },
    { "name": "alavancaT", "group": "ferrolho", "mat": "claro", "shape": "roundBox", "pos": [-4.15, 1.6, 0], "size": [0.6, 0.6, 1.28], "r": 0.28 },
    { "name": "gatilho", "group": "gatilho", "mat": "acento2", "shape": "profile", "h": 0.6, "round": 0.22, "corner": 0.16, "points": [[0.2, -2.4], [0.15, -2.95], [-0.1, -3.35], [-0.5, -3.52], [-0.6, -3.3], [-0.32, -3.05], [-0.16, -2.7], [-0.16, -2.4]] },
    { "name": "pente", "group": "carregador", "mat": "claro", "shape": "profile", "h": 0.62, "round": 0.3, "corner": 0.3, "points": [[1.45, -3.3], [1.45, -3.967], [1.781, -4.006], [1.898, -5.405], [2.16, -6.745], [2.699, -8.655], [5.899, -7.84], [5.307, -5.755], [5.132, -4.822], [5.015, -3.511], [5.219, -3.424], [5.272, -3.3]] },
    { "name": "penteBase", "group": "carregador", "mat": "acento", "shape": "profile", "h": 0.68, "round": 0.3, "corner": 0.3, "points": [[2.639, -8.443], [2.801, -9.018], [3.005, -9.193], [3.529, -9.047], [3.675, -9.105], [3.996, -9.018], [4.141, -8.872], [5.423, -8.493], [5.569, -8.552], [6.035, -8.319], [5.839, -7.628]] }
  ]
};
```

```js file=src/data/armas/awp.js
// Receita da AWP de massinha (Fase 4.1): chassi de coronha verde-oliva com o buraco do polegar, ação redonda, luneta com as
// torres, cano pesado e freio de boca em grafite, a bola da alavanca do ferrolho e a base do carregador na cor de acento dos
// dois lados. Referencial: +X para a boca, +Y para cima, +Z para a direita, origem no eixo do cano sobre o gatilho (u).
// Formato em docs/phases/phase-4.md, seção 4.1, "Receita"; o corpo é JSON puro.
export default {
  "id": "awp",
  "version": 1,
  "refs": { "planta": "tools/blender/refs/awp.json", "pins": ["QPG8", "QRF4", "QCG1", "NFS1"] },
  "materials": { "corpo": "verdeOliva", "metal": "grafite", "claro": "grafiteClaro", "acento": "acento", "acento2": "acento2" },
  "groups": {
    "corpo": { "pivot": [0, 0, 0] },
    "carregador": { "pivot": [11.2, -2.2, 0], "axis": [0, -1, 0] },
    "alavanca": { "pivot": [-1, 0.26, 0], "axis": [1, 0, 0] },
    "gatilho": { "pivot": [-0.5, -2.35, 0], "axis": [0, 0, 1] }
  },
  "anchors": {
    "maoDireita": { "pos": [-3.48, -2.25, 1.61], "rot": [1.5708, -0.3, 0], "pose": "empunhadura" },
    "maoEsquerda": { "pos": [14.51, -2.64, -2.59], "rot": [-2.608, 1.28, 0], "pose": "guardaMao" },
    "boca": { "pos": [34.2, 0, 0], "rot": [0, 0, 0] },
    "ejecao": { "pos": [3, 0.45, 0.8], "rot": [0, -1.67, 0.335] },
    "mira": { "pos": [-2.52, 2.05, 0], "rot": [0, 0, 0] }
  },
  "parts": [
    { "name": "coronha", "group": "corpo", "mat": "corpo", "shape": "profile", "h": 0.86, "round": 0.45, "corner": 0.5, "points": [[-13.9, 0.08], [-13.9, -5.263], [-13.637, -5.226], [-13.557, -5.467], [-10.1, -5.306], [-9.778, -4.181], [-9.456, -4.02], [-7.527, -3.939], [-6.884, -4.261], [-6.401, -4.824], [-5.678, -5.226], [-4.07, -5.467], [-3.185, -5.869], [-2.301, -5.949], [-1.899, -5.628], [-1.819, -4.583], [-1.577, -3.859], [-1.015, -3.377], [0.915, -3.457], [1.317, -2.894], [1.478, -2.894], [1.558, -3.377], [1.799, -3.296], [1.96, -3.618], [2.282, -3.618], [2.523, -3.859], [3.166, -3.859], [4.855, -3.618], [5.096, -3.135], [5.498, -2.814], [9.598, -2.09], [10.45, -2.168], [10.45, 0.2], [-1.216, 0.2], [-1.336, -0.402], [-6.401, -0.482], [-6.562, -0.241], [-7.125, -0.241], [-7.848, 0.08]] },
    { "name": "pocoCarregador", "group": "corpo", "mat": "corpo", "shape": "profile", "h": 0.8, "round": 0.4, "corner": 0.3, "points": [[10.4, -2.163], [12, -2.2], [12, 0.2], [10.4, 0.2]] },
    { "name": "guardaMaoFrente", "group": "corpo", "mat": "corpo", "shape": "profile", "h": 0.8, "round": 0.42, "corner": 0.45, "points": [[11.95, -3.135], [14.181, -3.135], [14.583, -3.055], [14.824, -2.734], [15.306, -2.734], [15.387, -2.894], [15.708, -2.894], [15.789, -2.734], [16.432, -2.734], [16.512, -2.975], [16.754, -2.975], [16.914, -3.216], [17.879, -3.296], [18.764, -3.135], [18.844, -2.653], [18.764, -2.01], [18.442, -1.608], [18.442, -0.804], [17.558, -0.724], [17.558, -0.563], [17.799, -0.482], [18.9, -0.482], [18.9, 0.2], [11.95, 0.2]] },
    { "name": "buracoPolegar", "group": "corpo", "mat": "corpo", "shape": "profile", "op": "subtract", "h": 1.6, "round": 0, "corner": 0.3, "points": [[-3.989, -2.0904], [-3.025, -2.0904], [-2.864, -2.3316], [-2.944, -2.9748], [-3.748, -3.6179], [-4.874, -3.5375], [-5.035, -3.2963], [-4.954, -2.7336], [-4.552, -2.3316]] },
    { "name": "guardaMato", "group": "corpo", "mat": "corpo", "shape": "profile", "h": 0.62, "round": 0.28, "corner": 0.26, "points": [[1.45, -2.5], [1.45, -3.6], [1, -4.1], [-1.1, -4.1], [-1.65, -3.7], [-1.7, -3], [-1.05, -3], [-1.05, -3.5], [0.9, -3.5], [0.9, -2.5]] },
    { "name": "guardaVao", "group": "corpo", "mat": "corpo", "shape": "profile", "op": "subtract", "h": 1.6, "round": 0, "corner": 0.28, "points": [[-1.05, -3.5], [0.9, -3.5], [0.9, -2.25], [-1.05, -2.25]] },
    { "name": "soleira", "group": "corpo", "mat": "metal", "shape": "profile", "h": 0.9, "round": 0.4, "corner": 0.35, "points": [[-14.2, -5.306], [-13.637, -5.226], [-13.557, -5.467], [-13.45, -5.462], [-13.45, 0.08], [-13.959, 0.08]] },
    { "name": "acao", "group": "corpo", "mat": "metal", "shape": "lathe", "pos": [0, 0.26, 0], "corner": 0.16, "points": [[-1.25, 0], [-1.25, 0.62], [11.7, 0.62], [11.7, 0]] },
    { "name": "trilho", "group": "corpo", "mat": "metal", "shape": "roundBox", "pos": [5.3, 0.85, 0], "size": [5, 0.6, 0.6], "r": 0.2 },
    { "name": "anelTras", "group": "corpo", "mat": "metal", "shape": "roundBox", "pos": [0.8, 1.45, 0], "size": [0.62, 0.62, 0.86], "r": 0.3 },
    { "name": "anelFrente", "group": "corpo", "mat": "metal", "shape": "roundBox", "pos": [9.8, 1.45, 0], "size": [0.62, 0.62, 0.86], "r": 0.3 },
    { "name": "luneta", "group": "corpo", "mat": "metal", "shape": "lathe", "pos": [0, 2.05, 0], "corner": 0.16, "points": [[-2.52, 0], [-2.52, 0.8], [-2.3, 0.9], [-1.25, 0.9], [-0.85, 0.76], [8, 0.76], [8.95, 1.12], [11.6, 1.14], [11.6, 0]] },
    { "name": "ocular", "group": "corpo", "mat": "metal", "shape": "cylinder", "op": "subtract", "pos": [-2.7, 2.05, 0], "rot": [0, 0, 1.5708], "r": 0.52, "h": 0.4, "round": 0.08 },
    { "name": "objetiva", "group": "corpo", "mat": "metal", "shape": "cylinder", "op": "subtract", "pos": [11.8, 2.05, 0], "rot": [0, 0, 1.5708], "r": 0.82, "h": 0.4, "round": 0.08 },
    { "name": "torreCima", "group": "corpo", "mat": "metal", "shape": "cylinder", "pos": [4.5, 3.12, 0], "r": 0.66, "h": 0.6, "round": 0.22 },
    { "name": "torreLado", "group": "corpo", "mat": "metal", "shape": "cylinder", "pos": [4.5, 2.05, 1.12], "rot": [1.5708, 0, 0], "r": 0.62, "h": 0.6, "round": 0.22 },
    { "name": "cano", "group": "corpo", "mat": "metal", "shape": "lathe", "corner": 0.1, "points": [[11.6, 0], [11.6, 0.66], [18.2, 0.64], [31.25, 0.6], [31.25, 0]] },
    { "name": "freio", "group": "corpo", "mat": "metal", "shape": "lathe", "corner": 0.16, "points": [[31.25, 0], [31.25, 0.8], [31.95, 0.8], [32.45, 0.68], [34.2, 0.66], [34.2, 0]] },
    { "name": "freioJanelaD", "group": "corpo", "mat": "metal", "shape": "roundBox", "op": "subtract", "pos": [33.2, 0, 0.72], "size": [0.42, 0.34, 0.3], "r": 0.1 },
    { "name": "freioJanelaE", "group": "corpo", "mat": "metal", "shape": "roundBox", "op": "subtract", "pos": [33.2, 0, -0.72], "size": [0.42, 0.34, 0.3], "r": 0.1 },
    { "name": "alma", "group": "corpo", "mat": "metal", "shape": "cylinder", "op": "subtract", "pos": [34, 0, 0], "rot": [0, 0, 1.5708], "r": 0.26, "h": 0.62, "round": 0.06 },
    { "name": "janelaEjecao", "group": "corpo", "mat": "metal", "shape": "roundBox", "op": "subtract", "pos": [3, 0.45, 0.72], "size": [1.3, 0.3, 0.3], "r": 0.1 },
    { "name": "ferrolho", "group": "alavanca", "mat": "claro", "shape": "lathe", "pos": [0, 0.26, 0], "corner": 0.14, "points": [[-1.95, 0], [-1.95, 0.6], [-1, 0.6], [-1, 0]] },
    { "name": "alavancaHaste", "group": "alavanca", "mat": "claro", "shape": "tube", "r": 0.6, "points": [[-1.35, 0.4, 0.4], [-1.55, 0.05, 1.2]] },
    { "name": "alavancaBola", "group": "alavanca", "mat": "acento", "shape": "sphere", "pos": [-1.65, -0.15, 1.55], "r": 0.74 },
    { "name": "gatilho", "group": "gatilho", "mat": "acento2", "shape": "profile", "h": 0.6, "round": 0.22, "corner": 0.16, "points": [[-0.35, -2.3], [-0.4, -2.85], [-0.6, -3.18], [-0.9, -3.36], [-1, -3.15], [-0.78, -2.9], [-0.66, -2.55], [-0.66, -2.3]] },
    { "name": "pente", "group": "carregador", "mat": "metal", "shape": "profile", "h": 0.62, "round": 0.3, "corner": 0.25, "points": [[10.48, -2.171], [10.563, -2.894], [10.684, -3], [11.92, -3], [11.92, -1.6], [10.48, -1.6]] },
    { "name": "penteBase", "group": "carregador", "mat": "acento", "shape": "profile", "h": 0.68, "round": 0.3, "corner": 0.28, "points": [[10.42, -2.95], [10.626, -2.95], [11.206, -3.457], [11.528, -3.457], [11.98, -3.135], [11.98, -2.95]] }
  ]
};
```

```js file=src/data/armas/nova.js
// Receita da Nova de massinha (Fase 4.1): coronha e receptor moldados numa peça só em grafite, cano e tubo do carregador em
// grafite claro, bomba com os sulcos, a massa de mira em bolinha e o gatilho na cor de acento dos dois lados. Referencial:
// +X para a boca, +Y para cima, +Z para a direita, origem no eixo do cano sobre o gatilho (u). Formato em
// docs/phases/phase-4.md, seção 4.1, "Receita"; o corpo é JSON puro.
export default {
  "id": "nova",
  "version": 1,
  "refs": { "planta": "tools/blender/refs/nova.json", "pins": ["QPG3", "QCG1", "QPL5"] },
  "materials": { "corpo": "grafite", "claro": "grafiteClaro", "acento": "acento", "acento2": "acento2" },
  "groups": {
    "corpo": { "pivot": [0, 0, 0] },
    "bomba": { "pivot": [13.3, -1.2, 0], "axis": [-1, 0, 0] },
    "gatilho": { "pivot": [-0.4, -1.7, 0], "axis": [0, 0, 1] }
  },
  "anchors": {
    "maoDireita": { "pos": [-5.84, -0.99, 1.61], "rot": [1.5708, -0.6, 0], "pose": "empunhadura" },
    "maoEsquerda": { "pos": [12.5, -1.93, -2.35], "rot": [-2.608, 1.28, 0], "pose": "bomba" },
    "boca": { "pos": [24.9, 0, 0], "rot": [0, 0, 0] },
    "ejecao": { "pos": [4.3, -0.35, 0.95], "rot": [0, -1.471, 0.244] }
  },
  "parts": [
    { "name": "coronha", "group": "corpo", "mat": "corpo", "shape": "profile", "h": 0.86, "round": 0.45, "corner": 0.5, "points": [[-14.3, -1.647], [-14.123, -5.56], [-14.013, -6.157], [-6.142, -3.438], [-5.921, -3.438], [-5.744, -3.703], [-5.39, -3.814], [-4.55, -3.836], [-4.108, -3.747], [-3.931, -2.974], [-3.621, -2.421], [-3.312, -2.111], [-2.648, -1.736], [-2.361, -1.669], [-1.65, -1.716], [-1.65, 0.298], [-2.98, -0.365], [-4.793, -1.006], [-5.302, -1.006], [-5.567, -0.652], [-5.81, -0.652], [-13.371, -1.382], [-14.057, -1.47]] },
    { "name": "receptor", "group": "corpo", "mat": "corpo", "shape": "profile", "h": 0.74, "round": 0.4, "corner": 0.35, "points": [[-2.1, 0.111], [-2.1, -1.669], [-1.39, -1.8], [1.607, -1.8], [1.973, -1.736], [9.5, -1.8], [9.5, 0.426], [7.036, 0.475], [6.35, 0.542], [6.306, 0.674], [1.973, 0.674], [1.884, 1.072], [1.199, 1.117], [0.668, 1.47], [0.469, 1.47], [0.071, 1.117], [-0.039, 0.652], [-0.703, 0.586], [-1.454, 0.387]] },
    { "name": "guardaMato", "group": "corpo", "mat": "corpo", "shape": "profile", "h": 0.6, "round": 0.26, "corner": 0.24, "points": [[1.8, -1.7], [1.8, -3.1], [1.35, -3.7], [-1.05, -3.7], [-1.65, -3.3], [-1.7, -1.7], [-1.1, -1.7], [-1.1, -3.1], [1.25, -3.1], [1.25, -1.7]] },
    { "name": "guardaVao", "group": "corpo", "mat": "corpo", "shape": "profile", "op": "subtract", "h": 1.6, "round": 0, "corner": 0.26, "points": [[-1.1, -3.1], [1.25, -3.1], [1.25, -1.62], [-1.1, -1.62]] },
    { "name": "janelaEjecao", "group": "corpo", "mat": "corpo", "shape": "roundBox", "op": "subtract", "pos": [4.3, -0.35, 0.92], "size": [1.5, 0.38, 0.3], "r": 0.12 },
    { "name": "cano", "group": "corpo", "mat": "claro", "shape": "lathe", "corner": 0.1, "points": [[2.9, 0], [2.9, 0.62], [24.88, 0.6], [24.88, 0]] },
    { "name": "tuboCarregador", "group": "corpo", "mat": "claro", "shape": "lathe", "pos": [0, -1.1, 0], "corner": 0.3, "points": [[8.9, 0], [8.9, 0.6], [23.3, 0.6], [23.75, 0.5], [23.8, 0]] },
    { "name": "massaMira", "group": "corpo", "mat": "acento", "shape": "sphere", "pos": [23.45, 0.72, 0], "r": 0.62 },
    { "name": "alma", "group": "corpo", "mat": "claro", "shape": "cylinder", "op": "subtract", "pos": [24.7, 0, 0], "rot": [0, 0, 1.5708], "r": 0.3, "h": 0.6, "round": 0.06 },
    { "name": "bomba", "group": "bomba", "mat": "corpo", "shape": "profile", "h": 0.92, "round": 0.52, "corner": 0.45, "points": [[9.45, -1.985], [10.86, -2.156], [14.42, -2.156], [16.476, -2.089], [16.565, -1.957], [16.852, -1.912], [16.874, -2.443], [16.985, -2.576], [17.118, -2.288], [17.15, -0.28], [9.45, -0.28]] },
    { "name": "bombaSulco1D", "group": "bomba", "mat": "corpo", "shape": "capsule", "op": "subtract", "r": 0.13, "a": [10.3, -0.85, 0.96], "b": [16.3, -0.85, 0.96] },
    { "name": "bombaSulco2D", "group": "bomba", "mat": "corpo", "shape": "capsule", "op": "subtract", "r": 0.13, "a": [10.3, -1.3, 0.96], "b": [16.3, -1.3, 0.96] },
    { "name": "bombaSulco3D", "group": "bomba", "mat": "corpo", "shape": "capsule", "op": "subtract", "r": 0.13, "a": [10.3, -1.75, 0.96], "b": [16.3, -1.75, 0.96] },
    { "name": "bombaSulco1E", "group": "bomba", "mat": "corpo", "shape": "capsule", "op": "subtract", "r": 0.13, "a": [10.3, -0.85, -0.96], "b": [16.3, -0.85, -0.96] },
    { "name": "bombaSulco2E", "group": "bomba", "mat": "corpo", "shape": "capsule", "op": "subtract", "r": 0.13, "a": [10.3, -1.3, -0.96], "b": [16.3, -1.3, -0.96] },
    { "name": "bombaSulco3E", "group": "bomba", "mat": "corpo", "shape": "capsule", "op": "subtract", "r": 0.13, "a": [10.3, -1.75, -0.96], "b": [16.3, -1.75, -0.96] },
    { "name": "gatilho", "group": "gatilho", "mat": "acento2", "shape": "profile", "h": 0.6, "round": 0.22, "corner": 0.16, "points": [[-0.2, -1.65], [-0.25, -2.2], [-0.5, -2.6], [-0.85, -2.78], [-0.95, -2.55], [-0.69, -2.3], [-0.55, -1.95], [-0.55, -1.65]] }
  ]
};
```

```js file=src/data/armas/p90.js
// Receita da P90 de massinha (Fase 4.1): corpo bullpup em grafite com o buraco da empunhadura e a janela do gatilho, alojamento
// da mira, carregador por cima em grafite claro, a mira de anel, o seletor, o gatilho e a ponta do carregador na cor de acento
// dos dois lados. Referencial: +X para a boca, +Y para cima, +Z para a direita, origem no eixo do cano sobre o gatilho (u).
// Formato em docs/phases/phase-4.md, seção 4.1, "Receita"; o corpo é JSON puro.
export default {
  "id": "p90",
  "version": 1,
  "refs": { "planta": "tools/blender/refs/p90.json", "pins": ["QSG2", "QCG1", "QPL1"] },
  "materials": { "corpo": "grafite", "claro": "grafiteClaro", "acento": "acento", "acento2": "acento2" },
  "groups": {
    "corpo": { "pivot": [0, 0, 0] },
    "carregador": { "pivot": [-7.9, 1, 0], "axis": [0, 1, 0] },
    "gatilho": { "pivot": [-0.45, -0.8, 0], "axis": [0, 0, 1] }
  },
  "anchors": {
    "maoDireita": { "pos": [-3.41, -1.28, 1.77], "rot": [1.5708, -0.1, 0], "pose": "empunhadura" },
    "maoEsquerda": { "pos": [1.91, -2.98, -2.39], "rot": [-2.608, 1.28, 0], "pose": "guardaMao" },
    "boca": { "pos": [5.6, 0, 0], "rot": [0, 0, 0] },
    "ejecao": { "pos": [-4.2, -3.9, 0], "rot": [0, -0.588, -1.392] },
    "mira": { "pos": [-0.75, 2.72, 0], "rot": [0, 0, 0] }
  },
  "parts": [
    { "name": "corpo", "group": "corpo", "mat": "corpo", "shape": "profile", "h": 1.05, "round": 0.56, "corner": 0.5, "points": [[-14.1, -2.924], [-14.076, -3.078], [-13.78, -3.125], [-9.119, -3.125], [-9.048, -2.959], [-8.668, -2.947], [-6.379, -3.683], [-6.225, -3.92], [-4.719, -3.932], [-3.497, -3.683], [-2.714, -3.256], [-1.991, -2.591], [-1.255, -2.52], [-1.006, -2.615], [-0.888, -2.829], [-1.101, -3.884], [-1.006, -3.955], [0.512, -3.92], [1.093, -3.683], [1.568, -3.267], [1.935, -2.58], [2.018, -1.832], [2.232, -1.607], [3.074, -1.643], [3.24, -1.868], [3.252, -2.402], [3.702, -2.449], [3.85, -0.864], [3.536, -0.421], [3.85, -0.415], [3.814, 1.38], [-14.076, 1.38], [-13.958, -1.251]] },
    { "name": "buracoEmpunhadura", "group": "corpo", "mat": "corpo", "shape": "profile", "op": "subtract", "h": 1.8, "round": 0, "corner": 0.35, "points": [[-5.406, -0.7294], [-4.078, -0.7413], [-3.817, -0.8243], [-3.627, -0.9903], [-3.521, -1.2038], [-3.497, -1.4529], [-3.568, -1.6901], [-3.639, -1.7968], [-3.817, -1.951], [-5.027, -2.4966], [-5.193, -2.5322], [-5.406, -2.5322], [-5.572, -2.4966], [-5.774, -2.4017], [-5.999, -2.212], [-6.154, -1.951], [-6.213, -1.6664], [-6.189, -1.4054], [-6.082, -1.1445], [-5.928, -0.9548], [-5.667, -0.7887]] },
    { "name": "janelaGatilho", "group": "corpo", "mat": "corpo", "shape": "profile", "op": "subtract", "h": 1.8, "round": 0, "corner": 0.42, "points": [[-0.85, -2.45], [1.05, -2.45], [1.05, -0.8], [-0.85, -0.8]] },
    { "name": "manejo", "group": "corpo", "mat": "corpo", "shape": "capsule", "r": 0.6, "a": [2.2, 0.45, -1.55], "b": [2.2, 0.45, 1.55] },
    { "name": "seletor", "group": "corpo", "mat": "acento", "shape": "cylinder", "pos": [0.1, -4.12, 0], "r": 0.72, "h": 0.6, "round": 0.24 },
    { "name": "alojamentoMira", "group": "corpo", "mat": "corpo", "shape": "profile", "h": 0.82, "round": 0.45, "corner": 0.35, "points": [[-2.65, 1.91], [-2.65, 1.3], [3.55, 1.3], [3.55, 3.047], [3.513, 3.113], [2.777, 3.09], [2.754, 3.813], [-0.627, 3.825], [-0.662, 3.398], [-0.84, 3.22], [-2.097, 3.125]] },
    { "name": "alojamentoVao", "group": "corpo", "mat": "corpo", "shape": "profile", "op": "subtract", "h": 1.4, "round": 0, "corner": 0.2, "points": [[-1.125, 2.0222], [-0.745, 1.9866], [0.275, 1.7968], [0.761, 1.7257], [0.939, 1.7257], [1.057, 1.6901], [1.722, 1.5952], [1.817, 1.5596], [1.947, 1.441], [1.71, 1.4292], [1.662, 1.4648], [-1.374, 1.4766], [-1.208, 1.7968], [-1.16, 1.9747]] },
    { "name": "miraAnel", "group": "corpo", "mat": "acento", "shape": "torus", "pos": [-0.75, 2.72, 0], "rot": [0, 0, 1.5708], "r": 0.6, "R": 0.78 },
    { "name": "miraFuro", "group": "corpo", "mat": "acento", "shape": "cylinder", "op": "subtract", "pos": [-0.75, 2.72, 0], "rot": [0, 0, 1.5708], "r": 0.3, "h": 1.2, "round": 0.05 },
    { "name": "cano", "group": "corpo", "mat": "claro", "shape": "lathe", "corner": 0.14, "points": [[3.2, 0], [3.2, 0.62], [5.3, 0.6], [5.6, 0.5], [5.6, 0]] },
    { "name": "quebraChamaD", "group": "corpo", "mat": "claro", "shape": "capsule", "op": "subtract", "r": 0.16, "a": [4.15, 0, 0.62], "b": [5.15, 0, 0.62] },
    { "name": "quebraChamaE", "group": "corpo", "mat": "claro", "shape": "capsule", "op": "subtract", "r": 0.16, "a": [4.15, 0, -0.62], "b": [5.15, 0, -0.62] },
    { "name": "alma", "group": "corpo", "mat": "claro", "shape": "cylinder", "op": "subtract", "pos": [5.4, 0, 0], "rot": [0, 0, 1.5708], "r": 0.24, "h": 0.6, "round": 0.06 },
    { "name": "gatilho", "group": "gatilho", "mat": "acento2", "shape": "profile", "h": 0.6, "round": 0.22, "corner": 0.16, "points": [[-0.3, -0.75], [-0.35, -1.3], [-0.55, -1.75], [-0.82, -2], [-0.9, -1.78], [-0.7, -1.5], [-0.64, -1.1], [-0.64, -0.75]] },
    { "name": "pente", "group": "carregador", "mat": "claro", "shape": "profile", "h": 0.9, "round": 0.42, "corner": 0.35, "points": [[-13.2, 1.548], [-13.2, 0.35], [-2.75, 0.35], [-2.75, 1.62], [-2.856, 1.489]] },
    { "name": "penteBase", "group": "carregador", "mat": "acento", "shape": "profile", "h": 0.96, "round": 0.4, "corner": 0.3, "points": [[-13.8, 1.544], [-13.8, 0.3], [-13.1, 0.3], [-13.1, 1.546]] }
  ]
};
```

```js file=src/data/armas/knife.js
// Receita da faca de massinha (Fase 4.1): a espátula de modelar de aço com cabo torneado de madeira (CTL6, CTL7, CTL16),
// lâmina de 0,5 u com a borda arredondada, virola de aço e o anel de acento no pé do cabo. Referencial: +X para a ponta da
// lâmina, +Y para cima (o fio para baixo), +Z para a direita, origem na virola (u). Formato em docs/phases/phase-4.md,
// seção 4.1, "Receita"; o corpo é JSON puro.
export default {
  "id": "knife",
  "version": 1,
  "refs": { "pins": ["CTL6", "CTL7", "CTL16", "CTL12"] },
  "materials": { "aco": "aco", "madeira": "madeira", "acento": "acento" },
  "groups": {
    "corpo": { "pivot": [0, 0, 0] }
  },
  "anchors": {
    "maoDireita": { "pos": [-2.2, -1.3, 3], "rot": [3.1416, -1.5708, 0], "pose": "faca" }
  },
  "parts": [
    { "name": "cabo", "group": "corpo", "mat": "madeira", "shape": "lathe", "corner": 0.12, "points": [[-4.25, 0], [-4.25, 0.44], [-4.05, 0.62], [-3.4, 0.7], [-2, 0.74], [-1, 0.68], [-0.5, 0.6], [-0.3, 0.57], [-0.3, 0]] },
    { "name": "anel", "group": "corpo", "mat": "acento", "shape": "lathe", "corner": 0.06, "closed": true, "points": [[-3.98, 0.6], [-3.66, 0.6], [-3.66, 0.8], [-3.98, 0.8]] },
    { "name": "virola", "group": "corpo", "mat": "aco", "shape": "lathe", "corner": 0.1, "points": [[-0.38, 0], [-0.38, 0.64], [0.1, 0.62], [0.28, 0.46], [0.34, 0]] },
    { "name": "lamina", "group": "corpo", "mat": "aco", "shape": "profile", "thin": true, "h": 0.25, "round": 0.2, "corner": 0.16, "points": [[0.15, -0.2], [0.9, -0.4], [2, -0.5], [3, -0.36], [3.6, -0.06], [3.65, 0], [3.55, 0.12], [2.8, 0.43], [1.8, 0.52], [0.9, 0.38], [0.15, 0.2]] },
    { "name": "laminaFioD", "group": "corpo", "mat": "aco", "shape": "capsule", "op": "subtract", "r": 0.1, "a": [0.9, -0.05, 0.29], "b": [3.1, -0.12, 0.29] },
    { "name": "laminaFioE", "group": "corpo", "mat": "aco", "shape": "capsule", "op": "subtract", "r": 0.1, "a": [0.9, -0.05, -0.29], "b": [3.1, -0.12, -0.29] }
  ]
};
```

```js file=src/data/armas/index.js
// Registro das receitas das armas de massinha (Fase 4.1; formato em docs/phases/phase-4.md, seção 4.1, "Receita").
// Cada arquivo desta pasta é gravado pelo exportador do Blender (tools/blender/massacre_armas.py) e lido pelo
// gerador (src/weapons/model/); a ordem aqui é a da bancada `arsenal` e do comando `armas`.
// As outras 18 armas de fogo e a faca de ouro entram na 4.4; as granadas na 4.7.

import glock from './glock.js';
import ak47 from './ak47.js';
import m4a4 from './m4a4.js';
import awp from './awp.js';
import nova from './nova.js';
import p90 from './p90.js';
import knife from './knife.js';

export const ARMAS = Object.freeze({ glock, ak47, m4a4, awp, nova, p90, knife });
```

- [ ] **Passo 10: O evento da recarga e o serviço `weaponModels`**

Em `src/core/events.js`, trocar:

```
  PLAYER_SPAWN: 'player:spawn', // {position} — volta ao jogo
});
```

por:

```
  PLAYER_SPAWN: 'player:spawn', // {position} — volta ao jogo
  WEAPON_MODEL: 'weapon:model', // {id, phase: 'relendo'|'pronta'} — a receita da arma foi relida: tire a instância antiga / a nova está pronta
});
```

```js file=src/weapons/model/weaponLibrary.js
// Serviço `weaponModels` (Fase 4.1; docs/phases/phase-4.md, seção 4.1, "Gerador"): guarda as malhas de cada arma por
// (arma, nível) e os materiais por (arma, facção), e entrega instâncias que só apontam para eles — a geometria e os
// materiais são compartilhados (marcados `userData.shared`, o dispose das cenas não os toca) e saem só no dispose do
// serviço ou na recarga da receita. Pré-carrega as armas do jogador ao entrar no mapa, para a troca não esperar.
// Os materiais são por arma (e não só por massa) porque o boil de cada um segue o tamanho da arma.

import { EV } from '../../core/events.js';
import { ARMAS } from '../../data/armas/index.js';
import { validateRecipe, weaponFaction } from './recipe.js';
import { WEAPON_LODS, assembleWeapon, buildWeaponMeshes, createWeaponMaterials } from './weaponModel.js';

export class WeaponLibrary {
  #sdf;
  #log;
  #events;
  #recipes = new Map(Object.entries(ARMAS));
  #meshes = new Map(); // `${id}:${lod}` → Promise<built>
  #built = new Map(); // `${id}:${lod}` → built (pronto)
  #materials = new Map(); // `${id}:${facção}` → ClayMaterial[]
  #disposed = false;

  /**
   * @param {{sdf:import('../../clay/sdf/sdfMesher.js').SdfMesher, log?:object|null,
   *          events?:import('../../core/events.js').EventBus|null}} deps
   */
  constructor({ sdf, log = null, events = null }) {
    this.#sdf = sdf;
    this.#log = log;
    this.#events = events;
  }

  /** Armas com receita (a ordem do registro src/data/armas/index.js). */
  get ids() {
    return [...this.#recipes.keys()];
  }

  has(id) {
    return this.#recipes.has(id);
  }

  recipe(id) {
    return this.#recipes.get(id) ?? null;
  }

  /**
   * Malhas de uma arma num nível (gera na primeira vez; pedidos iguais dividem a mesma promessa).
   * @returns {Promise<object>} ver buildWeaponMeshes
   */
  meshes(id, lod = 'perto') {
    if (this.#disposed) return Promise.reject(new Error('WeaponLibrary: já foi descartada'));
    const recipe = this.recipe(id);
    if (!recipe) return Promise.reject(new Error(`arma sem receita: ${id}`));
    if (!WEAPON_LODS.includes(lod)) return Promise.reject(new Error(`nível de detalhe desconhecido: ${lod}`));
    const key = `${id}:${lod}`;
    let pending = this.#meshes.get(key);
    if (!pending) {
      pending = buildWeaponMeshes(recipe, this.#sdf, lod).then((built) => {
        if (this.#disposed || this.#meshes.get(key) !== pending) {
          for (const g of Object.values(built.groups)) g.geometry.dispose();
          throw new Error(`arma ${id} descartada durante a geração`);
        }
        for (const g of Object.values(built.groups)) g.geometry.userData.shared = true;
        this.#built.set(key, built);
        this.#log?.debug(`arma ${id} (${lod}): ${Math.round(built.triangles)} triângulos em ${built.ms.toFixed(0)} ms`);
        return built;
      });
      pending.catch(() => {
        if (this.#meshes.get(key) === pending) this.#meshes.delete(key);
      });
      this.#meshes.set(key, pending);
    }
    return pending;
  }

  /** Materiais de uma arma para uma facção (um por massa, na ordem do `mat`). */
  #materialsFor(recipe, built, faction) {
    const key = `${recipe.id}:${faction}`;
    let list = this.#materials.get(key);
    if (!list) {
      list = createWeaponMaterials(recipe, built.materials, { faction, radius: built.radius });
      for (const m of list) m.userData.shared = true;
      this.#materials.set(key, list);
    }
    return list;
  }

  /**
   * Instância nova da arma (THREE.Group; ver assembleWeapon). Pode ser posta em qualquer cena; tirar da cena basta.
   * @param {string} id
   * @param {{lod?:string, faction?:'tr'|'ct'|'ambos'}} [options] facção padrão: a da arma
   */
  async instance(id, { lod = 'perto', faction = weaponFaction(id) } = {}) {
    const built = await this.meshes(id, lod);
    const recipe = this.recipe(id);
    return assembleWeapon(recipe, built, this.#materialsFor(recipe, built, faction), faction);
  }

  /** Pré-carrega as malhas (sem esperar): as armas do jogador ao entrar no mapa. */
  preload(ids, lod = 'perto') {
    return Promise.allSettled(ids.filter((id) => this.has(id)).map((id) => this.meshes(id, lod)));
  }

  /** Relatório do console (`armas`): uma linha por (arma, nível) gerado. */
  report() {
    const rows = [];
    for (const id of this.ids) {
      for (const lod of WEAPON_LODS) {
        const built = this.#built.get(`${id}:${lod}`);
        const pending = this.#meshes.has(`${id}:${lod}`);
        rows.push({
          id, lod,
          state: built ? 'pronta' : pending ? 'gerando' : '—',
          triangles: built ? Math.round(built.triangles) : 0,
          ms: built ? Math.round(built.ms) : 0,
          groups: built ? Object.keys(built.groups).length : 0,
        });
      }
    }
    return rows;
  }

  /**
   * Relê a receita do disco (depois de exportar do Blender) sem recarregar a página: importa o módulo de novo, valida,
   * troca, descarta as malhas e os materiais antigos e gera o nível pedido. Emite EV.WEAPON_MODEL duas vezes: `relendo`
   * logo antes de descartar (quem tem instância na cena tira agora: uma malha descartada que continua sendo desenhada
   * volta para a GPU e ninguém a libera depois) e `pronta` com a malha nova gerada.
   */
  async reload(id, lod = 'perto') {
    if (!this.has(id)) throw new Error(`arma sem receita: ${id}`);
    const url = new URL(`../../data/armas/${id}.js`, import.meta.url);
    url.searchParams.set('v', String(Date.now()));
    const mod = await import(url.href);
    const recipe = validateRecipe(mod.default);
    if (recipe.id !== id) throw new Error(`a receita de ${id} diz ser ${recipe.id}`);
    this.#events?.emit(EV.WEAPON_MODEL, { id, phase: 'relendo' });
    this.#forget(id);
    this.#recipes.set(id, recipe);
    await this.meshes(id, lod);
    this.#events?.emit(EV.WEAPON_MODEL, { id, phase: 'pronta' });
    return recipe;
  }

  #forget(id) {
    for (const lod of WEAPON_LODS) {
      const key = `${id}:${lod}`;
      const built = this.#built.get(key);
      if (built) for (const g of Object.values(built.groups)) g.geometry.dispose();
      this.#built.delete(key);
      this.#meshes.delete(key);
    }
    for (const [key, list] of this.#materials) {
      if (!key.startsWith(`${id}:`)) continue;
      for (const m of list) m.dispose();
      this.#materials.delete(key);
    }
  }

  dispose() {
    for (const id of this.ids) this.#forget(id);
    this.#disposed = true;
  }
}
```

- [ ] **Passo 11: Rodar e ver passar**

Run: `node --test tests/weaponRecipes.test.js`
Expected: PASS
Run: `npm test`
Expected: PASS — 317 testes passando.

- [ ] **Passo final: Commit** (só com o pedido do usuário)

```bash
git add src/data/weaponPalette.js src/data/claySkins.js src/clay/glsl/skins.js src/data/viewmodel.js src/weapons/model src/data/armas tools/blender/refs tools/silhueta.html src/core/events.js tests/weaponRecipes.test.js
git commit -m "MASSACRE 4.1: receitas das sete primeiras armas, gerador, plantas e a biblioteca de malhas" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Tarefa 4: Viewmodel parado — a arma na mão em primeira pessoa

**Files:**
- Create: `src/weapons/viewmodel/placement.js`, `src/weapons/viewmodel/viewmodelLights.js`, `src/weapons/viewmodel/viewmodel.js`, `tests/viewmodel.test.js`
- Modify: `src/render/postPipeline.js`, `src/data/configSchema.js`, `src/ui/settingControls.js`, `src/ui/settingsScreen.js`

O viewmodel é uma camada própria do pipeline de pós (`postPipeline.addLayer`, desenhada depois das passadas da cena e antes do bloom e do tone mapping), com a cena da arma e dos dois braços e uma câmera que copia a do jogador. Convenções do CS (a referência do "sentir" das armas): `viewmodel_fov` é horizontal num quadro 4:3 (o Source mede assim), então o vertical fica fixo e telas mais largas ganham lado (Hor+) — 60 por padrão (46,83° na vertical), de 54 a 68; `viewmodel_offset_x/y/z` (direita, frente, cima; padrão 1, 1, −1) somam por cima da posição da categoria (pistola, rifle, sniper, escopeta, SMG bullpup, faca: a origem da arma na câmera e os ângulos de arfagem, guinada e rolagem) e do ajuste fino da arma (`nudge`, a M4A4 desce por causa da alça); os três `viewmodel_presetpos` (1 Mesa, 2 Sofá, 3 Clássica) e a seção "Arma na mão" das configurações. As contas são puras (`placement.js`): o giro de base leva a boca (+X da arma) para a frente (−Z da câmera), cada âncora de mão vira a pose do pulso na câmera e cada antebraço aponta para um cotovelo fixo fora da tela. A luz da camada (`viewmodelLights.js`) copia as luzes do mapa a cada quadro (mesmas posições, cores e intensidades — o painel da vitrine e o console `luz` valem na hora) e acrescenta o que a cópia sozinha não faz: a sombra própria (cada spot/direcional que faz sombra no mapa projeta na camada com a câmera de sombra apertada numa esfera em volta da arma e dos pulsos, mapa de 512 a 1024) e a oclusão pelo set (raios no mundo de colisão do centro da arma, da boca e dos pulsos até cada luz; a fração livre multiplica a cópia, suavizada em 0,08 s subindo e 0,14 s descendo). As camadas ganham `beforeRender`/`afterRender` (a sombra própria força o mapa de sombra quando as sombras do mapa são estáticas). O `Viewmodel` pede a arma à biblioteca e os braços ao `handModels`, põe as mãos nas âncoras com a pose de cada uma, troca a pose só na troca de pose (12/s, "em dois"), mostra a braçadeira do time e some em terceira pessoa, no noclip, morto, com a luneta, com `r_viewmodel 0` e quando o item na mão não tem receita.

- [ ] **Passo 1: Escrever os testes** — FOV, giro de base, posição e offsets, ângulos, mãos nas âncoras, a arma na tela e os cotovelos fora dela, visibilidade, acento e os presets.

```js file=tests/viewmodel.test.js
// Testes do viewmodel parado (Fase 4.1; docs/phases/phase-4.md, seção 4.1, "Viewmodel parado" e "Testes"): o FOV no
// referencial do CS, a posição por categoria com os offsets e o ajuste fino da arma, o giro de base (boca para a
// frente, lado direito para a direita), as mãos nas âncoras, os cotovelos fora da tela e a arma dentro dela (em 16:9,
// com os valores padrão), quando aparece e some, a facção do acento na mão e as posições prontas do CS.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import * as THREE from 'three';
import { ARMAS } from '../src/data/armas/index.js';
import { HAND } from '../src/data/hands.js';
import { VIEWMODEL } from '../src/data/viewmodel.js';
import {
  HAND_ANCHOR, WEAPON_TO_VIEW, anchorPose, applyViewmodelPreset, categoryPlacement, currentViewmodelPreset, elbowTarget,
  handSides, viewCategory, viewFaction, viewPlacement, viewmodelVerticalFov, viewmodelVisible, weaponNudge,
} from '../src/weapons/viewmodel/placement.js';

const near = (a, b, eps = 1e-9, msg = '') => assert.ok(Math.abs(a - b) <= eps, `${msg} esperado ${b}, veio ${a}`);
const DEFAULT_OFFSET = { x: VIEWMODEL.offset.x.default, y: VIEWMODEL.offset.y.default, z: VIEWMODEL.offset.z.default };

/** Projeção de um ponto do referencial da câmera na tela (NDC), com o FOV padrão do viewmodel em 16:9. */
function ndc(p, aspect = 16 / 9) {
  const t = Math.tan((viewmodelVerticalFov(VIEWMODEL.fov.default) * Math.PI) / 360);
  return { x: p.x / (-p.z * t * aspect), y: p.y / (-p.z * t), front: p.z < -VIEWMODEL.near };
}

test('viewmodel: FOV como no CS (horizontal em 4:3 → vertical fixo)', () => {
  near(viewmodelVerticalFov(90), 73.7397952917, 1e-6, '90 do CS');
  near(viewmodelVerticalFov(60), 46.8264489, 1e-6, '60 do CS');
  assert.ok(viewmodelVerticalFov(VIEWMODEL.fov.max) > viewmodelVerticalFov(VIEWMODEL.fov.min));
});

test('viewmodel: giro de base leva a boca para a frente e o lado direito para a direita', () => {
  const muzzle = new THREE.Vector3(1, 0, 0).applyQuaternion(WEAPON_TO_VIEW);
  const right = new THREE.Vector3(0, 0, 1).applyQuaternion(WEAPON_TO_VIEW);
  const up = new THREE.Vector3(0, 1, 0).applyQuaternion(WEAPON_TO_VIEW);
  assert.ok(muzzle.distanceTo(new THREE.Vector3(0, 0, -1)) < 1e-9);
  assert.ok(right.distanceTo(new THREE.Vector3(1, 0, 0)) < 1e-9);
  assert.ok(up.distanceTo(new THREE.Vector3(0, 1, 0)) < 1e-9);
});

test('viewmodel: posição da categoria + offsets do CS (x direita, y frente, z cima) + ajuste fino da arma', () => {
  for (const cat of Object.keys(VIEWMODEL.categories)) {
    const base = VIEWMODEL.categories[cat];
    const zero = viewPlacement(cat, { offset: { x: 0, y: 0, z: 0 } });
    assert.deepEqual(zero.position.toArray(), [...base.pos], cat);
    const moved = viewPlacement(cat, { offset: { x: 1, y: 2, z: -0.5 } });
    assert.deepEqual(moved.position.toArray().map((v, i) => +(v - base.pos[i]).toFixed(9)), [1, -0.5, -2], `${cat}: offsets`);
    assert.ok(Math.abs(zero.quaternion.lengthSq() - 1) < 1e-9);
  }
  const nudge = weaponNudge('m4a4');
  assert.ok(nudge, 'a M4 tem ajuste fino');
  const m4 = viewPlacement('rifle', { offset: { x: 0, y: 0, z: 0 }, nudge });
  assert.deepEqual(m4.position.toArray().map((v, i) => +(v - VIEWMODEL.categories.rifle.pos[i]).toFixed(9)), [...nudge]);
  assert.equal(weaponNudge('ak47'), null);
});

test('viewmodel: ângulos (guinada + boca para a esquerda, arfagem + boca para cima, rolagem + topo para a esquerda)', () => {
  const dir = (angles) => new THREE.Vector3(1, 0, 0).applyQuaternion(viewPlacement('rifle', { tune: { angles } }).quaternion);
  const top = (angles) => new THREE.Vector3(0, 1, 0).applyQuaternion(viewPlacement('rifle', { tune: { angles } }).quaternion);
  assert.ok(dir([0, 10, 0]).x < -0.1, 'guinada');
  assert.ok(dir([10, 0, 0]).y > 0.1, 'arfagem');
  assert.ok(top([0, 0, 10]).x < -0.1, 'rolagem');
  assert.ok(dir([0, 0, 0]).distanceTo(new THREE.Vector3(0, 0, -1)) < 1e-9, 'sem giro: boca para a frente');
  // O ajuste ao vivo por cima dos dados, sem mexer nos dados.
  const tuned = categoryPlacement('rifle', { pos: [1, 2, 3], elbows: { direita: [9, 9, 9] } });
  assert.deepEqual(tuned.pos, [1, 2, 3]);
  assert.deepEqual(tuned.elbows.direita, [9, 9, 9]);
  assert.deepEqual(tuned.elbows.esquerda, [...VIEWMODEL.categories.rifle.elbows.esquerda]);
  assert.throws(() => categoryPlacement('bazuca'), /categoria/);
});

test('viewmodel: cada mão na âncora da receita, no referencial da câmera', () => {
  for (const id of Object.keys(ARMAS)) {
    const r = ARMAS[id];
    const pl = viewPlacement(viewCategory(id), { offset: DEFAULT_OFFSET, nudge: weaponNudge(id) });
    const m = new THREE.Matrix4().compose(pl.position, pl.quaternion, new THREE.Vector3(1, 1, 1));
    for (const side of handSides(r)) {
      const a = r.anchors[HAND_ANCHOR[side]];
      const pose = anchorPose(pl, a);
      const expected = new THREE.Vector3(...a.pos).applyMatrix4(m);
      assert.ok(pose.position.distanceTo(expected) < 1e-9, `${id}.${side}: pulso`);
      const q = pl.quaternion.clone().multiply(new THREE.Quaternion().setFromEuler(new THREE.Euler(...a.rot, 'XYZ')));
      assert.ok(Math.abs(Math.abs(pose.quaternion.dot(q)) - 1) < 1e-9, `${id}.${side}: giro`);
    }
    assert.deepEqual(handSides(r), id === 'knife' ? ['direita'] : ['direita', 'esquerda'], id);
  }
});

test('viewmodel: com os valores padrão em 16:9, a arma aparece e os cotovelos ficam fora da tela', () => {
  for (const id of Object.keys(ARMAS)) {
    const r = ARMAS[id];
    const cat = viewCategory(id);
    const pl = viewPlacement(cat, { offset: DEFAULT_OFFSET, nudge: weaponNudge(id) });
    // A arma na tela: a boca (ou, na faca, a ponta da lâmina) cai dentro do quadro, na metade de baixo à direita.
    const tipLocal = r.anchors.boca?.pos ?? [3.6, 0, 0];
    const tip = new THREE.Vector3(...tipLocal).applyQuaternion(pl.quaternion).add(pl.position);
    const t = ndc(tip);
    assert.ok(t.front && Math.abs(t.x) < 1 && Math.abs(t.y) < 1, `${id}: a boca fora da tela (${t.x.toFixed(2)}, ${t.y.toFixed(2)})`);
    assert.ok(t.x > -0.2 && t.y < 0.1, `${id}: a arma fica embaixo à direita (${t.x.toFixed(2)}, ${t.y.toFixed(2)})`);
    for (const side of handSides(r)) {
      const wrist = anchorPose(pl, r.anchors[HAND_ANCHOR[side]]).position;
      assert.ok(wrist.z < -VIEWMODEL.near, `${id}.${side}: o pulso na frente da câmera`);
      const target = elbowTarget(cat, side);
      const dir = target.clone().sub(wrist).normalize();
      const elbow = wrist.clone().addScaledVector(dir, HAND.forearm.length);
      const e = ndc(elbow);
      assert.ok(!e.front || Math.abs(e.x) > 1 || Math.abs(e.y) > 1, `${id}.${side}: o cotovelo aparece (${e.x.toFixed(2)}, ${e.y.toFixed(2)})`);
      // O antebraço vai para baixo (o cotovelo abaixo do pulso).
      assert.ok(elbow.y < wrist.y, `${id}.${side}: o cotovelo acima do pulso`);
    }
  }
});

test('viewmodel: quando aparece e quando some', () => {
  const base = {
    enabled: true, firstPerson: true, alive: true, noclip: false, zoomed: false, item: 'ak47', hasRecipe: (id) => Boolean(ARMAS[id]),
  };
  assert.equal(viewmodelVisible(base), true);
  assert.equal(viewmodelVisible({ ...base, firstPerson: false }), false, 'terceira pessoa');
  assert.equal(viewmodelVisible({ ...base, noclip: true }), false, 'noclip');
  assert.equal(viewmodelVisible({ ...base, alive: false }), false, 'morto');
  assert.equal(viewmodelVisible({ ...base, zoomed: true }), false, 'luneta aberta');
  assert.equal(viewmodelVisible({ ...base, enabled: false }), false, 'r_viewmodel 0');
  assert.equal(viewmodelVisible({ ...base, item: 'usps' }), false, 'arma sem receita (4.4)');
  assert.equal(viewmodelVisible({ ...base, item: 'he' }), false, 'granada (4.7)');
  assert.equal(viewmodelVisible({ ...base, item: 'c4' }), false, 'bomba (Fase 8)');
  assert.equal(viewmodelVisible({ ...base, item: null }), false, 'mão vazia');
  assert.equal(viewCategory('usps'), null);
});

test('viewmodel: o acento da arma na mão', () => {
  assert.equal(viewFaction('glock', 'ct'), 'tr', 'arma de um lado fica com o seu');
  assert.equal(viewFaction('m4a4', 'tr'), 'ct');
  assert.equal(viewFaction('awp', 'ct'), 'ct', 'arma dos dois lados pega o time de quem segura');
  assert.equal(viewFaction('awp', 'tr'), 'tr');
  assert.equal(viewFaction('awp', null), 'ambos', 'sem time: amarelo e branco');
  assert.equal(viewFaction('knife', 'off'), 'ambos');
});

test('viewmodel: posições prontas do CS (viewmodel_presetpos)', () => {
  const store = new Map();
  const config = { set: (k, v) => store.set(k, v), get: (k) => store.get(k) };
  for (const [id, p] of Object.entries(VIEWMODEL.presets)) {
    applyViewmodelPreset(config, id);
    assert.equal(store.get('viewmodel.fov'), p.fov);
    assert.equal(currentViewmodelPreset(config), id);
  }
  config.set('viewmodel.offsetX', 0.3);
  assert.equal(currentViewmodelPreset(config), null, 'ajustada à mão');
  assert.throws(() => applyViewmodelPreset(config, '7'), /posição desconhecida/);
  // O "Mesa" é o padrão da config.
  const d = VIEWMODEL.presets[1];
  assert.deepEqual([d.fov, d.x, d.y, d.z], [VIEWMODEL.fov.default, DEFAULT_OFFSET.x, DEFAULT_OFFSET.y, DEFAULT_OFFSET.z]);
});
```

- [ ] **Passo 2: Rodar e ver falhar**

Run: `node --test tests/viewmodel.test.js`
Expected: FAIL — o teste não carrega (`ERR_MODULE_NOT_FOUND`: `src/weapons/viewmodel/placement.js`).

- [ ] **Passo 3: As contas do viewmodel**

```js file=src/weapons/viewmodel/placement.js
// Contas do viewmodel parado (Fase 4.1; docs/phases/phase-4.md, seção 4.1, "Viewmodel parado"), sem cena: o FOV no
// referencial do CS, a pose da arma na câmera por categoria (com os offsets), a pose de cada âncora na câmera (onde vai
// cada pulso), os cotovelos, a facção do acento e quando o viewmodel aparece. O Viewmodel (viewmodel.js) aplica; os
// testes do Node conferem.
// Referencial da câmera: +X direita, +Y cima, −Z frente. Referencial da arma: +X boca, +Y cima, +Z lado direito.

import * as THREE from 'three';
import { VIEWMODEL } from '../../data/viewmodel.js';
import { weaponFaction } from '../model/recipe.js';

const DEG = Math.PI / 180;

/** Giro de base: a boca (+X da arma) para a frente (−Z), o lado direito (+Z) para a direita (+X), o topo para cima. */
export const WEAPON_TO_VIEW = Object.freeze(new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0, 1, 0), Math.PI / 2));

/** FOV vertical (graus) do viewmodel_fov do CS (horizontal num quadro 4:3; fica fixo em qualquer tela, Hor+). */
export function viewmodelVerticalFov(fov) {
  return (2 * Math.atan(Math.tan((fov * DEG) / 2) / VIEWMODEL.fov.aspect)) / DEG;
}

/** Categoria de posição de uma arma com receita (null: não tem). */
export function viewCategory(id) {
  return VIEWMODEL.weapons[id]?.category ?? null;
}

/** Ajuste fino da arma somado à posição da categoria (u, referencial da câmera), ou null. */
export function weaponNudge(id) {
  return VIEWMODEL.weapons[id]?.nudge ?? null;
}

/**
 * Posição de uma categoria com um ajuste por cima (o `viewmodel_ajuste` do console afina os dados ao vivo).
 * @param {string} category
 * @param {{pos?:number[], angles?:number[], elbows?:{direita?:number[], esquerda?:number[]}}|null} [tune]
 */
export function categoryPlacement(category, tune = null) {
  const base = VIEWMODEL.categories[category];
  if (!base) throw new Error(`categoria de viewmodel desconhecida: ${category}`);
  return {
    pos: tune?.pos ?? base.pos,
    angles: tune?.angles ?? base.angles,
    elbows: { direita: tune?.elbows?.direita ?? base.elbows.direita, esquerda: tune?.elbows?.esquerda ?? base.elbows.esquerda },
  };
}

const _e = new THREE.Euler();
const _q = new THREE.Quaternion();

/**
 * Pose da arma no referencial da câmera: a posição da categoria + o ajuste fino da arma + offsets (x direita, y frente,
 * z cima, como no CS) e o giro da categoria (arfagem, guinada, rolagem na ordem da câmera, 'YXZ') sobre o giro de base.
 * @param {string} category
 * @param {{offset?:{x:number,y:number,z:number}, tune?:object|null, nudge?:number[]|null}} [options]
 * @param {{position:THREE.Vector3, quaternion:THREE.Quaternion}} [out]
 */
export function viewPlacement(category, { offset = { x: 0, y: 0, z: 0 }, tune = null, nudge = null } = {}, out = { position: new THREE.Vector3(), quaternion: new THREE.Quaternion() }) {
  const p = categoryPlacement(category, tune);
  const n = nudge ?? [0, 0, 0];
  out.position.set(p.pos[0] + n[0] + offset.x, p.pos[1] + n[1] + offset.z, p.pos[2] + n[2] - offset.y);
  const [pitch, yaw, roll] = p.angles;
  _e.set(pitch * DEG, yaw * DEG, roll * DEG, 'YXZ');
  out.quaternion.setFromEuler(_e).multiply(WEAPON_TO_VIEW);
  return out;
}

/**
 * Pose de uma âncora da receita ({pos, rot}) no referencial da câmera, dada a pose da arma.
 * @param {{position:THREE.Vector3, quaternion:THREE.Quaternion}} placement
 * @param {{pos:number[], rot?:number[]}} anchor
 * @param {{position:THREE.Vector3, quaternion:THREE.Quaternion}} [out]
 */
export function anchorPose(placement, anchor, out = { position: new THREE.Vector3(), quaternion: new THREE.Quaternion() }) {
  out.position.fromArray(anchor.pos).applyQuaternion(placement.quaternion).add(placement.position);
  const r = anchor.rot ?? [0, 0, 0];
  _e.set(r[0], r[1], r[2], 'XYZ');
  out.quaternion.copy(placement.quaternion).multiply(_q.setFromEuler(_e));
  return out;
}

/** Cotovelo (para onde o antebraço aponta) de um lado, no referencial da câmera. */
export function elbowTarget(category, side, tune = null, out = new THREE.Vector3()) {
  return out.fromArray(categoryPlacement(category, tune).elbows[side]);
}

/** Mãos que a arma usa: as âncoras `maoDireita`/`maoEsquerda` da receita (a faca só tem a direita). */
export function handSides(recipe) {
  const sides = [];
  if (recipe?.anchors?.maoDireita) sides.push('direita');
  if (recipe?.anchors?.maoEsquerda) sides.push('esquerda');
  return sides;
}

/** Âncora da mão de cada lado. */
export const HAND_ANCHOR = Object.freeze({ direita: 'maoDireita', esquerda: 'maoEsquerda' });

/**
 * Facção do acento da arma na mão: as de um lado só (Glock, AK, M4A4...) ficam com o seu; as dos dois lados pegam o
 * time de quem segura (ou o amarelo/branco sem time).
 * @param {string} id @param {'tr'|'ct'|null} team
 */
export function viewFaction(id, team) {
  const own = weaponFaction(id);
  if (own !== 'ambos') return own;
  return team === 'tr' || team === 'ct' ? team : 'ambos';
}

/**
 * O viewmodel aparece? Em primeira pessoa com o PlayerPawn, vivo, fora do noclip, sem a luneta aberta (a visão pela
 * luneta é da 4.5; no CS a arma some com o zoom), com `r_viewmodel 1` e com receita para o item na mão (as outras 18
 * armas até a 4.4, granadas até a 4.7, a bomba até a Fase 8). A bancada `arsenal` força com "Segurar".
 * @param {{enabled:boolean, firstPerson:boolean, alive:boolean, noclip:boolean, zoomed:boolean, item:string|null,
 *          hasRecipe:(id:string)=>boolean}} s
 */
export function viewmodelVisible(s) {
  return Boolean(s.enabled && s.firstPerson && s.alive && !s.noclip && !s.zoomed && s.item && s.hasRecipe(s.item));
}

/** Chaves da config de cada campo das posições prontas (viewmodel_presetpos). */
const PRESET_KEYS = Object.freeze({ fov: 'viewmodel.fov', x: 'viewmodel.offsetX', y: 'viewmodel.offsetY', z: 'viewmodel.offsetZ' });

/** Aplica uma posição pronta do CS (1 Mesa, 2 Sofá, 3 Clássica) na config. */
export function applyViewmodelPreset(config, id) {
  const p = VIEWMODEL.presets[id];
  if (!p) throw new Error(`posição desconhecida: ${id} (use ${Object.keys(VIEWMODEL.presets).join(', ')})`);
  for (const [field, key] of Object.entries(PRESET_KEYS)) config.set(key, p[field]);
  return p;
}

/** A posição pronta que a config tem agora (ou null se foi ajustada à mão). */
export function currentViewmodelPreset(config) {
  for (const [id, p] of Object.entries(VIEWMODEL.presets)) {
    if (Object.entries(PRESET_KEYS).every(([field, key]) => Math.abs(config.get(key) - p[field]) < 1e-6)) return id;
  }
  return null;
}
```

- [ ] **Passo 4: Rodar os testes do viewmodel**

Run: `node --test tests/viewmodel.test.js`
Expected: PASS

- [ ] **Passo 5: `beforeRender`/`afterRender` nas camadas do pipeline**

Em `src/render/postPipeline.js`, trocar:

```

  addLayer(layer) {
```

por:

```

  /**
   * Camada por cima da cena (o viewmodel): `{scene, camera, visible?, beforeRender?(renderer), afterRender?(renderer)}`,
   * desenhada com a profundidade própria depois dos passes da cena e antes do bloom e do tone mapping. Devolve quem a tira.
   */
  addLayer(layer) {
```

Em `src/render/postPipeline.js`, trocar:

```
        r.clearDepth();
        r.render(layer.scene, layer.camera);
      }
```

por:

```
        r.clearDepth();
        layer.beforeRender?.(r);
        try {
          r.render(layer.scene, layer.camera);
        } finally {
          layer.afterRender?.(r);
        }
      }
```

- [ ] **Passo 6: A luz da camada**

```js file=src/weapons/viewmodel/viewmodelLights.js
// Luz da camada do viewmodel (Fase 4.1; docs/phases/phase-4.md, seção 4.1, "Viewmodel parado"): cópias das luzes do mapa
// (spot, pontual, direcional, hemisférica e ambiente — mesmas posições, cores e intensidades, lidas a cada quadro, então
// o painel da vitrine e o console `luz` valem na hora) e o ambiente assado. Assim a arma escurece fora do feixe da key,
// como o resto do set. Duas coisas que a cópia sozinha não faz:
//  - o set tapar a luz: de alguns pontos da arma (centro, boca, pulsos), um raio no mundo de colisão até cada luz que
//    faz sombra no mapa; a fração livre multiplica a cópia (suavizada);
//  - a sombra própria (a mão na arma, a arma nos dedos): a cópia de cada spot/direcional que faz sombra no mapa projeta
//    sombra na camada, com a câmera de sombra apertada numa esfera em volta da arma e dos pulsos (mais texels no que
//    importa; o cone e a direção da luz continuam os do mapa).

import * as THREE from 'three';
import { VIEWMODEL } from '../../data/viewmodel.js';
import { createRayHit } from '../../physics/collisionWorld.js';

const L = VIEWMODEL.light;
const _p = new THREE.Vector3();
const _t = new THREE.Vector3();
const _d = new THREE.Vector3();

/**
 * A câmera de sombra de uma luz vista de onde ela está, apertada numa esfera (centro e raio no mundo). Usa a conta do
 * three (LightShadow.updateMatrices) com uma luz de mentira que "mira" o centro da esfera: a iluminação continua com o
 * cone e a direção da luz de verdade.
 */
function focusShadow(shadow) {
  shadow.sphere = new THREE.Sphere(new THREE.Vector3(), 10);
  const proxy = { matrixWorld: new THREE.Matrix4(), target: { matrixWorld: new THREE.Matrix4() } };
  const base = THREE.LightShadow.prototype.updateMatrices;
  shadow.updateMatrices = function updateMatrices(light) {
    const cam = this.camera;
    const { center, radius } = this.sphere;
    if (cam.isPerspectiveCamera) {
      _p.setFromMatrixPosition(light.matrixWorld);
      const d = Math.max(_p.distanceTo(center), radius * 1.05);
      const fov = (2 * Math.asin(Math.min(0.999, radius / d)) * 180) / Math.PI;
      const near = Math.max(0.05, d - radius);
      const far = d + radius;
      if (cam.fov !== fov || cam.near !== near || cam.far !== far || cam.aspect !== 1) {
        cam.fov = fov;
        cam.near = near;
        cam.far = far;
        cam.aspect = 1;
        cam.updateProjectionMatrix();
      }
      proxy.matrixWorld.copy(light.matrixWorld);
    } else {
      // Direcional: a câmera ortográfica sai de trás da esfera, na direção da luz.
      _p.setFromMatrixPosition(light.matrixWorld);
      _t.setFromMatrixPosition(light.target.matrixWorld);
      _d.subVectors(_p, _t).normalize();
      const back = radius * 3;
      proxy.matrixWorld.makeTranslation(center.x + _d.x * back, center.y + _d.y * back, center.z + _d.z * back);
      if (cam.right !== radius || cam.near !== back - radius || cam.far !== back + radius) {
        cam.left = cam.bottom = -radius;
        cam.right = cam.top = radius;
        cam.near = back - radius;
        cam.far = back + radius;
        cam.updateProjectionMatrix();
      }
    }
    proxy.target.matrixWorld.makeTranslation(center.x, center.y, center.z);
    base.call(this, proxy);
  };
  return shadow;
}

/** A luz visível de fato (ela e todos os pais visíveis, como o renderer do three decide). */
function effectivelyVisible(obj) {
  for (let o = obj; o; o = o.parent) if (!o.visible) return false;
  return true;
}

function makeCopy(src) {
  let copy;
  if (src.isSpotLight) copy = new THREE.SpotLight();
  else if (src.isPointLight) copy = new THREE.PointLight();
  else if (src.isDirectionalLight) copy = new THREE.DirectionalLight();
  else if (src.isHemisphereLight) copy = new THREE.HemisphereLight();
  else if (src.isAmbientLight) copy = new THREE.AmbientLight();
  else return null;
  copy.name = `vm:${src.name || src.type}`;
  // A matriz de cada quadro é a do mundo da luz do mapa (o grupo das cópias fica na origem).
  copy.matrixAutoUpdate = false;
  if (copy.target) copy.target.matrixAutoUpdate = false;
  // Só as que fazem sombra no mapa podem fazer a sombra própria (e só spot e direcional: a pontual gastaria 6 faces).
  const selfShadow = src.castShadow && (src.isSpotLight || src.isDirectionalLight);
  if (selfShadow) {
    focusShadow(copy.shadow);
    copy.shadow.bias = L.selfShadow.bias;
    copy.shadow.normalBias = L.selfShadow.normalBias;
  }
  return { src, copy, selfShadow, occludes: Boolean(src.castShadow) && !src.isHemisphereLight && !src.isAmbientLight, visibility: 1 };
}

export class ViewmodelLights {
  /** @param {THREE.Scene} scene a cena da camada (as cópias entram nela) */
  constructor(scene) {
    this.scene = scene;
    this.group = new THREE.Group();
    this.group.name = 'viewmodel:luzes';
    scene.add(this.group);
    this.entries = [];
    this.source = null;
    this.world = null;
    this.hit = createRayHit();
    this.shadowSize = 0;
    this.shadowRadius = 0;
    this.shadowOn = false;
    this.scanClock = 0;
  }

  /**
   * Liga ao mapa: lê as luzes da cena dele (as cópias saem de novo quando a lista muda) e o mundo de colisão (null =
   * nada tapa a luz, como na bancada).
   */
  attach(sourceScene, world = null) {
    this.source = sourceScene;
    this.world = world;
    this.#rebuild();
  }

  #collect() {
    const list = [];
    this.source?.traverse((o) => {
      if (o.isLight) list.push(o);
    });
    return list;
  }

  #rebuild() {
    this.#clear();
    for (const src of this.#collect()) {
      const e = makeCopy(src);
      if (!e) continue;
      this.group.add(e.copy);
      if (e.copy.target) this.group.add(e.copy.target);
      this.entries.push(e);
    }
    this.shadowSize = 0;
  }

  #clear() {
    for (const e of this.entries) {
      e.copy.shadow?.map?.dispose();
      e.copy.dispose?.();
      e.copy.removeFromParent();
      e.copy.target?.removeFromParent();
    }
    this.entries = [];
  }

  /**
   * As luzes do mapa mudaram de lista? Uma que saiu da cena aparece na hora (sem pai); uma que entrou, na varredura da
   * cena a cada `light.rescan` s (a lista quase nunca muda: o painel mexe nas propriedades, não na lista).
   */
  #changed(dt) {
    for (const e of this.entries) if (!e.src.parent) return true;
    this.scanClock += dt;
    if (this.scanClock < L.rescan) return false;
    this.scanClock = 0;
    return this.#stale();
  }

  /** Confere a lista inteira pelos objetos, sem alocar. */
  #stale() {
    let n = 0;
    let stale = false;
    this.source?.traverse((o) => {
      if (!o.isLight || stale) return;
      if (this.entries[n]?.src !== o) stale = true;
      n++;
    });
    return stale || n !== this.entries.length;
  }

  /**
   * Nível da sombra própria: lado do mapa pelo nível de sombra do jogo (× mapScale), filtro pelo raio do nível.
   * @param {{mapSize:number, radius:number}} level SHADOW_LEVELS do render
   * @param {boolean} enabled sombras ligadas no renderer
   */
  #applyShadowLevel(level, enabled) {
    const S = L.selfShadow;
    const on = enabled && level.mapSize > 0;
    const size = on ? Math.min(S.maxSize, Math.max(S.minSize, Math.round(level.mapSize * S.mapScale))) : 0;
    const radius = level.radius * S.softness;
    if (size === this.shadowSize && radius === this.shadowRadius && on === this.shadowOn) return;
    this.shadowSize = size;
    this.shadowRadius = radius;
    this.shadowOn = on;
    for (const e of this.entries) {
      if (!e.selfShadow) continue;
      e.copy.castShadow = on;
      if (!on) continue;
      if (e.copy.shadow.mapSize.x !== size) {
        e.copy.shadow.mapSize.set(size, size);
        e.copy.shadow.map?.dispose();
        e.copy.shadow.map = null;
      }
      e.copy.shadow.radius = radius;
    }
  }

  /** Há sombra própria neste quadro (a camada força o mapa de sombra quando o mapa usa sombras estáticas)? */
  get casting() {
    return this.shadowOn && this.entries.some((e) => e.selfShadow && e.copy.visible && e.copy.intensity > 0);
  }

  /**
   * Um quadro: copia as luzes (posição, alvo, cor, intensidade, cone), atualiza o quanto o set tapa cada uma e a esfera
   * da sombra própria.
   * @param {object} o
   * @param {THREE.Vector3[]} o.points pontos da arma no mundo (centro, boca, pulsos) para a oclusão
   * @param {THREE.Sphere} o.sphere esfera da arma e dos pulsos no mundo
   * @param {{mapSize:number, radius:number}} o.level nível de sombra do jogo
   * @param {boolean} o.shadows sombras ligadas no renderer
   * @param {number} o.dt segundos desde o quadro anterior
   */
  update({ points, sphere, level, shadows, dt }) {
    if (!this.source) return;
    if (this.#changed(dt)) this.#rebuild();
    this.#applyShadowLevel(level, shadows);
    const scene = this.scene;
    scene.environment = this.source.environment;
    scene.environmentIntensity = this.source.environmentIntensity ?? 1;
    scene.environmentRotation.copy(this.source.environmentRotation);
    const O = L.occlusion;
    for (const e of this.entries) {
      const { src, copy } = e;
      copy.visible = effectivelyVisible(src);
      copy.color.copy(src.color);
      if (src.isHemisphereLight) copy.groundColor.copy(src.groundColor);
      copy.matrix.copy(src.matrixWorld);
      copy.matrixWorld.copy(src.matrixWorld);
      if (copy.target) {
        copy.target.matrix.copy(src.target.matrixWorld);
        copy.target.matrixWorld.copy(src.target.matrixWorld);
      }
      if (src.isSpotLight || src.isPointLight) {
        copy.distance = src.distance;
        copy.decay = src.decay;
      }
      if (src.isSpotLight) {
        copy.angle = src.angle;
        copy.penumbra = src.penumbra;
      }
      if (e.occludes && copy.visible && this.world && points.length) {
        const target = this.#visibility(src, points);
        const tau = target > e.visibility ? O.rise : O.fall;
        e.visibility += (target - e.visibility) * (1 - Math.exp(-Math.max(0, dt) / tau));
      } else {
        e.visibility = 1;
      }
      copy.intensity = src.intensity * e.visibility;
      if (e.selfShadow && copy.castShadow) copy.shadow.sphere.copy(sphere);
    }
  }

  /** Fração dos pontos que enxergam a luz (raios no mundo de colisão). */
  #visibility(src, points) {
    _p.setFromMatrixPosition(src.matrixWorld);
    let free = 0;
    for (const pt of points) {
      let max;
      if (src.isDirectionalLight) {
        _t.setFromMatrixPosition(src.target.matrixWorld);
        _d.subVectors(_p, _t).normalize();
        max = 1e5;
      } else {
        _d.subVectors(_p, pt);
        max = _d.length() - 1;
        if (max <= 0) {
          free++;
          continue;
        }
        _d.normalize();
      }
      if (!this.world.raycast(pt.x, pt.y, pt.z, _d.x, _d.y, _d.z, max, this.hit)) free++;
    }
    return free / points.length;
  }

  dispose() {
    this.#clear();
    this.group.removeFromParent();
    this.scene.environment = null;
    this.source = null;
    this.world = null;
  }
}
```

- [ ] **Passo 7: O viewmodel**

```js file=src/weapons/viewmodel/viewmodel.js
// Viewmodel parado (Fase 4.1; docs/phases/phase-4.md, seção 4.1, "Viewmodel parado"): a arma na mão em primeira pessoa
// numa camada própria do pipeline (postPipeline.addLayer) — cena com a arma e os dois braços de massinha, câmera que
// copia a do jogador com o FOV do viewmodel (viewmodel_fov) e a luz do mapa copiada (viewmodelLights.js). A arma fica na
// posição da categoria (src/data/viewmodel.js) mais os offsets; cada mão vai para a âncora da receita com a pose da
// âncora e o antebraço aponta para um cotovelo fixo fora da tela. Na 4.1 não anima: segura parado, com o boil "em
// dois" da massinha. Quem decide o que segurar e quando aparece é o MatchState (placement.js: viewmodelVisible).

import * as THREE from 'three';
import { EV, Subscriptions } from '../../core/events.js';
import { VIEWMODEL } from '../../data/viewmodel.js';
import { PALETTE } from '../../data/palette.js';
import { HAND } from '../../data/hands.js';
import { armbandColor } from '../../characters/hands/armband.js';
import { ViewmodelLights } from './viewmodelLights.js';
import {
  HAND_ANCHOR, anchorPose, categoryPlacement, elbowTarget, viewCategory, viewFaction, viewPlacement, viewmodelVerticalFov,
  weaponNudge,
} from './placement.js';

const SIDES = Object.freeze(['direita', 'esquerda']);
// Alcance da mão a partir do pulso (palma + dedos esticados): a esfera da sombra própria cobre a mão inteira.
const HAND_REACH = HAND.palm.center[0] + HAND.palm.half[0] + HAND.fingers[1].phalanges.reduce((a, b) => a + b, 0);

export class Viewmodel {
  /**
   * @param {object} deps
   * @param {import('../../render/renderSystem.js').RenderSystem} deps.render
   * @param {import('../model/weaponLibrary.js').WeaponLibrary} deps.weapons
   * @param {import('../../characters/hands/handLibrary.js').HandLibrary} deps.hands
   * @param {import('../../core/config.js').Config} deps.config
   * @param {import('../../core/events.js').EventBus} deps.events
   * @param {object|null} [deps.log]
   * @param {string} [deps.armColor] massa dos braços (a do boneco; terracota no de referência)
   */
  constructor({ render, weapons, hands, config, events, log = null, armColor = PALETTE.terracotta }) {
    this.render = render;
    this.weapons = weapons;
    this.hands = hands;
    this.config = config;
    this.log = log;
    this.armColor = armColor;
    this.scene = new THREE.Scene();
    this.scene.name = 'viewmodel';
    this.camera = new THREE.PerspectiveCamera(viewmodelVerticalFov(VIEWMODEL.fov.default), 16 / 9, VIEWMODEL.near, VIEWMODEL.far);
    this.camera.name = 'viewmodel';
    // `root` segue a câmera do jogador (o referencial da câmera); `holder` é a arma na posição da categoria.
    this.root = new THREE.Group();
    this.root.name = 'viewmodel:camera';
    this.holder = new THREE.Group();
    this.holder.name = 'viewmodel:arma';
    this.root.add(this.holder);
    this.scene.add(this.root);
    this.lights = new ViewmodelLights(this.scene);
    this.layer = {
      scene: this.scene, camera: this.camera, visible: false,
      beforeRender: (r) => this.#beforeRender(r), afterRender: (r) => this.#afterRender(r),
    };
    this.removeLayer = render.pipeline.addLayer(this.layer);
    this._shadowForced = false;
    this._shadowPending = false;

    this.arms = { direita: null, esquerda: null };
    this.armsReady = null;
    this.weapon = null; // instância na mão
    this.recipe = null;
    this.itemKey = null; // `${id}:${lod}:${facção}` pedido
    this.loadedKey = null; // o que está na mão
    this.request = { id: null, lod: null, faction: null, fresh: false }; // o último pedido (evita refazer a chave por quadro)
    this.token = 0;
    this.category = null;
    this.center = new THREE.Vector3(); // centro da arma no referencial dela
    this.radius = 10;
    this.dirty = true;
    this.tune = {}; // ajustes ao vivo por categoria (viewmodel_ajuste)
    this.anchorTune = {}; // ajustes ao vivo das âncoras das mãos por arma: {id: {maoDireita: {pos, rot}}}
    this.team = null;
    this.placement = { position: new THREE.Vector3(), quaternion: new THREE.Quaternion() };
    this._pose = { position: new THREE.Vector3(), quaternion: new THREE.Quaternion() };
    this._elbow = new THREE.Vector3();
    this.localPoints = []; // pontos da oclusão no referencial da câmera
    this.worldPoints = [];
    this.localSphere = new THREE.Sphere();
    this.worldSphere = new THREE.Sphere();

    this.subs = new Subscriptions();
    this.subs.add(config.watch('viewmodel.', () => {
      this.dirty = true;
    }));
    this.subs.add(config.watch('debug.armband', () => this.#applyTeam()));
    // Receita relida do disco (Blender): a instância antiga sai agora, antes de a biblioteca descartar as malhas.
    this.subs.on(events, EV.WEAPON_MODEL, ({ id, phase }) => {
      if (phase === 'relendo' && this.recipe?.id === id) this.#drop();
      if (id === this.itemKey?.split(':')[0]) this.#invalidate();
    });
    this.#applyTeam();
  }

  /** Liga à cena do mapa (as luzes copiadas) e ao mundo de colisão (o que tapa a luz; null na bancada). */
  attach(mapScene, world = null) {
    this.lights.attach(mapScene, world);
  }

  /** Time da braçadeira (cl_bracadeira; nas partidas de time, o do jogador): cor da faixa e acento das armas dos dois lados. */
  #applyTeam() {
    const v = this.config.get('debug.armband');
    this.team = v === 'tr' || v === 'ct' ? v : null;
    const color = armbandColor(this.team, this.armColor);
    for (const side of SIDES) this.arms[side]?.setArmband(color);
    this.#invalidate(); // o acento das armas dos dois lados muda com o time
  }

  /** Esquece o pedido: o próximo quadro pede a arma de novo (receita relida, time trocado). */
  #invalidate() {
    this.itemKey = null;
    this.request.fresh = false;
  }

  /** Cria os dois braços uma vez (a malha da mão sai da HandLibrary, gerada uma vez por sessão). */
  #ensureArms() {
    if (!this.armsReady) {
      this.armsReady = Promise.all(SIDES.map((side) => this.hands.createArm(side, { color: this.armColor }))).then((arms) => {
        if (this.disposed) {
          for (const a of arms) a.dispose();
          throw new Error('viewmodel descartado');
        }
        const color = armbandColor(this.team, this.armColor);
        SIDES.forEach((side, i) => {
          const arm = arms[i];
          arm.mesh.visible = false;
          arm.setArmband(color);
          this.root.add(arm.mesh);
          this.arms[side] = arm;
        });
        this.dirty = true;
      });
      this.armsReady.catch((err) => {
        if (!this.disposed) this.log?.error('viewmodel: braços', err);
      });
    }
    return this.armsReady;
  }

  /**
   * Pede o item na mão (id de arma com receita, ou null). `faction` força o acento (a bancada); sem ela, as armas dos
   * dois lados pegam o time da braçadeira.
   * @param {string|null} id @param {{lod?:string, faction?:string|null}} [options]
   */
  #want(id, { lod = 'perto', faction = null } = {}) {
    const r = this.request;
    if (r.fresh && r.id === id && r.lod === lod && r.faction === faction) return;
    r.id = id;
    r.lod = lod;
    r.faction = faction;
    r.fresh = true;
    const has = id && this.weapons.has(id) && viewCategory(id);
    const key = has ? `${id}:${lod}:${faction ?? viewFaction(id, this.team)}` : null;
    if (key === this.itemKey) return;
    this.itemKey = key;
    const token = ++this.token;
    if (!key) {
      this.#drop();
      return;
    }
    const [wid, wlod, wfaction] = key.split(':');
    Promise.all([this.weapons.instance(wid, { lod: wlod, faction: wfaction }), this.#ensureArms()]).then(([instance]) => {
      if (this.disposed || token !== this.token) return;
      this.#swap(instance, key);
    }).catch((err) => {
      if (!this.disposed && token === this.token) this.log?.error(`viewmodel: ${wid}`, err);
    });
  }

  /** Troca a arma da mão pela instância nova: centro e raio, poses das mãos pela âncora, posição a refazer. */
  #swap(instance, key) {
    this.#drop();
    const info = instance.userData.weapon;
    this.weapon = instance;
    this.recipe = this.weapons.recipe(info.id);
    this.loadedKey = key;
    this.category = viewCategory(info.id);
    instance.updateMatrixWorld(true);
    new THREE.Box3().setFromObject(instance).getCenter(this.center);
    this.radius = info.radius;
    this.holder.add(instance);
    for (const side of SIDES) {
      const anchor = this.#anchor(HAND_ANCHOR[side]);
      if (anchor) this.arms[side]?.setPose(anchor.pose ?? 'aberta');
    }
    this.dirty = true;
  }

  /** Âncora da receita na mão, com o ajuste ao vivo por cima (viewmodel_ajuste mao). */
  #anchor(name) {
    const base = this.recipe?.anchors[name];
    const tuned = this.anchorTune[this.recipe?.id]?.[name];
    return base && tuned ? { ...base, ...tuned } : base;
  }

  /** Tira a arma da mão (a instância só aponta para malhas e materiais da biblioteca: basta sair da cena). */
  #drop() {
    this.weapon?.removeFromParent();
    this.weapon = null;
    this.recipe = null;
    this.loadedKey = null;
    this.category = null;
    for (const side of SIDES) if (this.arms[side]) this.arms[side].mesh.visible = false;
  }

  /** Arma e mãos no referencial da câmera: a posição da categoria + offsets, os pulsos nas âncoras, os cotovelos. */
  #place() {
    const cat = this.category;
    const cfg = this.config;
    const offset = { x: cfg.get('viewmodel.offsetX'), y: cfg.get('viewmodel.offsetY'), z: cfg.get('viewmodel.offsetZ') };
    const pl = viewPlacement(cat, { offset, tune: this.tune[cat] ?? null, nudge: weaponNudge(this.recipe.id) }, this.placement);
    this.holder.position.copy(pl.position);
    this.holder.quaternion.copy(pl.quaternion);
    // Pontos da oclusão (centro, boca, pulsos) e a esfera da sombra própria, no referencial da câmera.
    const pts = [];
    const center = this.center.clone().applyQuaternion(pl.quaternion).add(pl.position);
    let radius = this.radius;
    for (const name of VIEWMODEL.light.occlusion.points) {
      if (name === 'centro') {
        pts.push(center.clone());
        continue;
      }
      const anchor = this.#anchor(name);
      if (anchor) pts.push(anchorPose(pl, anchor, this._pose).position.clone());
    }
    for (const side of SIDES) {
      const arm = this.arms[side];
      const anchor = this.#anchor(HAND_ANCHOR[side]);
      if (!arm) continue;
      arm.mesh.visible = Boolean(anchor);
      if (!anchor) continue;
      const pose = anchorPose(pl, anchor, this._pose);
      arm.place(pose.position, pose.quaternion, elbowTarget(cat, side, this.tune[cat] ?? null, this._elbow));
      radius = Math.max(radius, pose.position.distanceTo(center) + HAND_REACH);
    }
    this.localPoints = pts;
    while (this.worldPoints.length < pts.length) this.worldPoints.push(new THREE.Vector3());
    this.worldPoints.length = pts.length;
    this.localSphere.set(center, radius + VIEWMODEL.light.selfShadow.padding);
    this.dirty = false;
  }

  /**
   * Um quadro. `item`: o que a mão segura (id, ou null); `visible`: a regra de quando aparece (placement.js) já
   * avaliada por quem chama; `faction`/`lod` forçam o acento e o nível (a bancada).
   * @param {THREE.PerspectiveCamera} camera câmera do jogador (já posta neste quadro)
   * @param {number} dt
   * @param {{item:string|null, visible:boolean, faction?:string|null, lod?:string}} state
   */
  frame(camera, dt, { item, visible, faction = null, lod = 'perto' }) {
    this.#want(item, { lod, faction });
    const show = Boolean(visible && this.weapon && this.arms.direita && this.loadedKey === this.itemKey);
    this.layer.visible = show;
    if (!show) return;
    // Câmera e raiz: a do jogador (posição, olhar e rolagem), com o FOV do viewmodel.
    camera.updateMatrixWorld();
    const cam = this.camera;
    camera.matrixWorld.decompose(cam.position, cam.quaternion, cam.scale);
    const fov = viewmodelVerticalFov(this.config.get('viewmodel.fov'));
    if (cam.fov !== fov || cam.aspect !== camera.aspect) {
      cam.fov = fov;
      cam.aspect = camera.aspect;
      cam.updateProjectionMatrix();
    }
    this.root.position.copy(cam.position);
    this.root.quaternion.copy(cam.quaternion);
    if (this.dirty) this.#place();
    this.root.updateMatrixWorld(true);
    const m = this.root.matrixWorld;
    for (let i = 0; i < this.localPoints.length; i++) this.worldPoints[i].copy(this.localPoints[i]).applyMatrix4(m);
    this.worldSphere.copy(this.localSphere).applyMatrix4(m);
    const renderer = this.render.renderer;
    this.lights.update({
      points: this.worldPoints, sphere: this.worldSphere, level: this.render.shadowLevel, shadows: renderer.shadowMap.enabled, dt,
    });
  }

  // Sombra própria com o mapa em sombras estáticas (shadowMap.autoUpdate desligado): a camada pede o passe de sombra só
  // para ela e devolve o pedido pendente do mapa como estava.
  #beforeRender(r) {
    if (!this.lights.casting) return;
    this._shadowPending = r.shadowMap.needsUpdate;
    r.shadowMap.needsUpdate = true;
    this._shadowForced = true;
  }

  #afterRender(r) {
    if (!this._shadowForced) return;
    r.shadowMap.needsUpdate = this._shadowPending;
    this._shadowForced = false;
  }

  /** Ajuste ao vivo da posição de uma categoria (viewmodel_ajuste): `pos`, `angles` ou `elbows.{lado}`. */
  setTune(category, patch) {
    if (!VIEWMODEL.categories[category]) throw new Error(`categoria desconhecida: ${category}`);
    const cur = this.tune[category] ?? {};
    this.tune[category] = { ...cur, ...patch, elbows: { ...(cur.elbows ?? {}), ...(patch.elbows ?? {}) } };
    this.dirty = true;
  }

  clearTune(category = null) {
    if (category) delete this.tune[category];
    else this.tune = {};
    this.anchorTune = {};
    this.dirty = true;
  }

  /** Ajuste ao vivo da âncora de uma mão da arma na mão ({pos, rot}); devolve a linha para a receita. */
  setAnchorTune(side, patch) {
    if (!this.recipe) throw new Error('nenhuma arma na mão');
    const name = HAND_ANCHOR[side];
    if (!this.recipe.anchors[name]) throw new Error(`${this.recipe.id} não tem ${name}`);
    const byWeapon = (this.anchorTune[this.recipe.id] ??= {});
    byWeapon[name] = { ...(byWeapon[name] ?? {}), ...patch };
    this.dirty = true;
    return this.anchorLine(side);
  }

  /** A linha da âncora de uma mão no formato da receita (src/data/armas/<id>.js). */
  anchorLine(side) {
    const name = HAND_ANCHOR[side];
    const a = this.#anchor(name);
    if (!a) return `${this.recipe?.id ?? '—'}: sem ${name}`;
    const r = (v) => Number(v.toFixed(4));
    return `"${name}": { "pos": [${a.pos.map(r).join(', ')}], "rot": [${(a.rot ?? [0, 0, 0]).map(r).join(', ')}], "pose": "${a.pose}" },`;
  }

  /** A linha de src/data/viewmodel.js com o ajuste atual de uma categoria (para colar nos dados). */
  tuneLine(category) {
    const p = categoryPlacement(category, this.tune[category] ?? null);
    const f = (a) => `F([${a.map((v) => Number(v.toFixed(2))).join(', ')}])`;
    return `${category}: F({ pos: ${f(p.pos)}, angles: ${f(p.angles)}, elbows: F({ direita: ${f(p.elbows.direita)}, esquerda: ${f(p.elbows.esquerda)} }) }),`;
  }

  /** Estado para o console e os testes. */
  status() {
    return {
      item: this.loadedKey?.split(':')[0] ?? null, wanted: this.itemKey, category: this.category, visible: this.layer.visible,
      team: this.team, arms: SIDES.filter((s) => this.arms[s]?.mesh.visible),
    };
  }

  dispose() {
    this.disposed = true;
    this.token++;
    this.subs.dispose();
    this.removeLayer();
    this.#drop();
    for (const side of SIDES) {
      this.arms[side]?.dispose();
      this.arms[side] = null;
    }
    this.lights.dispose();
    this.scene.clear();
  }
}
```

- [ ] **Passo 8: As chaves de configuração e a seção "Arma na mão"**

Em `src/data/configSchema.js`, trocar:

```
import { DEFAULT_TOUCH_BUTTONS, TOUCH_BUTTONS_SINCE, TOUCH_LAYOUT_VERSION, defaultTouchLayout } from './touchLayout.js';

```

por:

```
import { DEFAULT_TOUCH_BUTTONS, TOUCH_BUTTONS_SINCE, TOUCH_LAYOUT_VERSION, defaultTouchLayout } from './touchLayout.js';
import { VIEWMODEL } from './viewmodel.js';

```

Em `src/data/configSchema.js`, trocar:

```

  // ---------------- Acessibilidade ----------------
```

por:

```

  // ---------------- Arma na mão (viewmodel, Fase 4.1) ----------------
  // Como no CS:GO: viewmodel_fov (horizontal em 4:3) e viewmodel_offset_x/y/z (direita, frente, cima) — src/data/viewmodel.js.
  'viewmodel.fov': {
    type: 'number', min: VIEWMODEL.fov.min, max: VIEWMODEL.fov.max, step: 1, default: VIEWMODEL.fov.default,
    label: 'Campo de visão da arma (viewmodel_fov)', group: 'graphics',
  },
  'viewmodel.offsetX': {
    type: 'number', min: VIEWMODEL.offset.x.min, max: VIEWMODEL.offset.x.max, step: 0.1, default: VIEWMODEL.offset.x.default,
    label: 'Arma para a direita (viewmodel_offset_x)', group: 'graphics',
  },
  'viewmodel.offsetY': {
    type: 'number', min: VIEWMODEL.offset.y.min, max: VIEWMODEL.offset.y.max, step: 0.1, default: VIEWMODEL.offset.y.default,
    label: 'Arma para a frente (viewmodel_offset_y)', group: 'graphics',
  },
  'viewmodel.offsetZ': {
    type: 'number', min: VIEWMODEL.offset.z.min, max: VIEWMODEL.offset.z.max, step: 0.1, default: VIEWMODEL.offset.z.default,
    label: 'Arma para cima (viewmodel_offset_z)', group: 'graphics',
  },

  // ---------------- Acessibilidade ----------------
```

Em `src/data/configSchema.js`, trocar:

```
  'debug.monitor': { type: 'bool', default: false, transient: true, label: 'Monitor do movimento (cl_monitor)', group: 'debug' },
  'debug.consoleHistory': {
```

por:

```
  'debug.monitor': { type: 'bool', default: false, transient: true, label: 'Monitor do movimento (cl_monitor)', group: 'debug' },
  'debug.viewmodel': { type: 'bool', default: true, transient: true, label: 'Arma na mão em primeira pessoa (r_viewmodel)', group: 'debug' },
  'debug.armband': {
    type: 'enum', options: ['off', 'tr', 'ct'], default: 'off', transient: true, label: 'Braçadeira de teste (cl_bracadeira)', group: 'debug',
  },
  'debug.consoleHistory': {
```

Em `src/ui/settingControls.js`, trocar:

```
  'graphics.fov': (v) => `${v}°`,
  'graphics.exposure': (v) => v.toFixed(2),
```

por:

```
  'graphics.fov': (v) => `${v}°`,
  'viewmodel.fov': (v) => `${v}°`,
  'viewmodel.offsetX': (v) => v.toFixed(1),
  'viewmodel.offsetY': (v) => v.toFixed(1),
  'viewmodel.offsetZ': (v) => v.toFixed(1),
  'graphics.exposure': (v) => v.toFixed(2),
```

Em `src/ui/settingsScreen.js`, trocar:

```
import { PRESET_IDS, PRESET_LABELS } from '../data/qualityPresets.js';

```

por:

```
import { PRESET_IDS, PRESET_LABELS } from '../data/qualityPresets.js';
import { VIEWMODEL } from '../data/viewmodel.js';
import { applyViewmodelPreset, currentViewmodelPreset } from '../weapons/viewmodel/placement.js';

```

Em `src/ui/settingsScreen.js`, trocar:

```
});
// Conforto (subfase 3.5): a sensação da câmera acima do "Reduzir movimento", que zera as três.
```

por:

```
});
// Arma na mão (Fase 4.1): o viewmodel_fov e os viewmodel_offset do CS, com as três posições do viewmodel_presetpos.
const VIEWMODEL_KEYS = ['viewmodel.fov', 'viewmodel.offsetX', 'viewmodel.offsetY', 'viewmodel.offsetZ'];
const VIEWMODEL_HINTS = Object.freeze({
  'viewmodel.fov': 'medido como no CS (horizontal em 4:3): maior mostra a arma menor e mais longe',
  'viewmodel.offsetX': 'somado à posição de cada tipo de arma',
});
// Conforto (subfase 3.5): a sensação da câmera acima do "Reduzir movimento", que zera as três.
```

Em `src/ui/settingsScreen.js`, trocar:

```
    }, 'Detectar hardware de novo');
    return [
```

por:

```
    }, 'Detectar hardware de novo');
    const vmButtons = Object.entries(VIEWMODEL.presets).map(([id, p]) =>
      h('button.btn-clay.is-small.preset', { type: 'button', dataset: { preset: id }, onclick: () => applyViewmodelPreset(config, id) }, p.label),
    );
    const syncVm = () => {
      const cur = currentViewmodelPreset(config);
      for (const b of vmButtons) b.classList.toggle('is-on', b.dataset.preset === cur);
    };
    syncVm();
    disposers.push(config.watch('viewmodel.', syncVm));
    return [
```

Em `src/ui/settingsScreen.js`, trocar:

```
      section('Ajustes individuais', ...GRAPHICS_KEYS.map((k) => track(settingRow(config, k)))),
      section('Massinha', ...CLAY_KEYS.map((k) => track(settingRow(config, k)))),
```

por:

```
      section('Ajustes individuais', ...GRAPHICS_KEYS.map((k) => track(settingRow(config, k)))),
      section('Arma na mão', h('div.preset-row', null, vmButtons),
        ...VIEWMODEL_KEYS.map((k) => track(settingRow(config, k, { hint: VIEWMODEL_HINTS[k] ?? null })))),
      section('Massinha', ...CLAY_KEYS.map((k) => track(settingRow(config, k)))),
```

- [ ] **Passo 9: A suíte inteira**

Run: `npm test`
Expected: PASS — 326 testes passando.

- [ ] **Passo final: Commit** (só com o pedido do usuário)

```bash
git add src/weapons/viewmodel src/render/postPipeline.js src/data/configSchema.js src/ui/settingControls.js src/ui/settingsScreen.js tests/viewmodel.test.js
git commit -m "MASSACRE 4.1: viewmodel parado com as mãos nas âncoras, FOV e offsets do CS e a luz do set" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Tarefa 5: A bancada `arsenal` e a ligação no jogo

**Files:**
- Create: `src/maps/animatorDesk.js`, `src/clay/set/pegboardMaterial.js`, `src/data/arsenal.js`, `src/maps/arsenal/turntable.js`, `src/maps/arsenal/planSheets.js`, `src/maps/arsenal/bench.js`, `src/debug/panelControls.js`, `src/maps/arsenal/panel.js`, `src/maps/arsenal/index.js`, `src/debug/weaponCommands.js`
- Modify: `src/clay/set/index.js`, `src/debug/showcase.js`, `src/debug/showcasePanel.js`, `src/maps/index.js`, `src/render/dispose.js`, `src/player/freeCamera.js`, `src/debug/commands.js`, `src/modes/matchState.js`, `src/main.js`

A mesa do animador da vitrine (a mesma luz de vitrine) vira bancada de armeiro (QGW1, QGW6, QGW8, QGW14): as armas deitadas em fileiras por categoria no tapete de corte, com o lado direito para cima e a etiqueta de fita crepe escrita a caneta; na frente, a roda de modelar de metal (QTT11, com a giratória de produto QTT9) com a arma escolhida deitada num suporte de arame em garfo (QWS9, QWS12, QWS14); atrás, o quadro de hardboard perfurado com as ferramentas de modelar penduradas (QPB8, QPB13, QPB19; material procedural, sem textura) e as plantas a lápis presas com fita (QBP3, QBP13, QBP15: o contorno da planta, a cota e o nome). A mesa sai de `animatorDesk.js`, dividida com a vitrine, e os controles de painel de `panelControls.js`, divididos também. O painel de fita crepe (Tab) escolhe a arma, a facção do acento (nas dos dois lados), o nível, a skin, explode os grupos, mostra as âncoras, sobrepõe a planta à silhueta, para a roda, mede a silhueta contra a planta (IoU), relê a receita do disco (a arma da roda e a da fileira voltam com a receita nova — o caminho do Blender) e "Segurar" (a câmera estacionada e o viewmodel com a arma, para ver a pega). Na partida, o viewmodel entra no `matchState` (criado na entrada, ligado à camada, as mãos aquecidas e as armas do jogador pré-carregadas; atualizado no quadro; descartado na saída) e `main.js` cria os serviços `weaponModels` e `handModels`. O dispose das cenas deixa em paz o que é compartilhado (`userData.shared`: só o dono libera). Console: `viewmodel_fov`, `viewmodel_offset_x/y/z`, `viewmodel_presetpos`, `viewmodel_ajuste` (afina a categoria ou a âncora de uma mão ao vivo e devolve a linha pronta para os dados), `r_viewmodel`, `cl_bracadeira tr|ct|0`, `arsenal` (ou `bancada`), `arma <id>` e `armas`. Esta tarefa é o jogo em volta das contas testadas: a conferência é no navegador (Tarefa 7); no Node, o grafo de módulos do jogo precisa carregar inteiro.

- [ ] **Passo 1: Rodar e ver falhar** — o mapa ainda não existe.

Run: `node --input-type=module -e "await import('./src/maps/arsenal/index.js')"`
Expected: FAIL — `ERR_MODULE_NOT_FOUND`: `src/maps/arsenal/index.js`.

- [ ] **Passo 2: A mesa do animador, dividida com a vitrine**

```js file=src/maps/animatorDesk.js
// Mesa do animador (Fase 2, vitrine; Fase 4.1, arsenal): tampo de madeira com quatro pernas, tapete de corte A1 (placa
// de PVC com a face impressa) e o chão de molleton do estúdio. Os números vêm de SHOWCASE_SET (src/data/showcase.js).
// Referências: docs/art/moodboard.md item 10 (SMD3: bancada com tapete verde; SSD1/CSD14: ilha de luz no escuro).

import * as THREE from 'three';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';

/**
 * @param {import('../clay/set/index.js').SetLibrary} set
 * @param {{desk:object, mat:object, floorY:number, floorColor:string}} def
 * @returns {THREE.Group} com a face do tapete no topo em y = mat.thickness
 */
export function buildAnimatorDesk(set, { desk, mat, floorY, floorColor }) {
  const root = new THREE.Group();
  root.name = 'mesa-do-animador';
  const wood = set.benchWood();
  const top = new THREE.Mesh(new RoundedBoxGeometry(desk.width, desk.thickness, desk.depth, 3, 4), wood);
  top.position.y = -desk.thickness / 2;
  top.name = 'tampo-bancada';
  const legH = -floorY - desk.thickness;
  const legGeo = new RoundedBoxGeometry(desk.legSize, legH, desk.legSize, 2, 5);
  const legs = [];
  for (const sx of [-1, 1]) {
    for (const sz of [-1, 1]) {
      const leg = new THREE.Mesh(legGeo, wood);
      leg.position.set(sx * (desk.width / 2 - desk.legInset), floorY + legH / 2, sz * (desk.depth / 2 - desk.legInset));
      leg.name = 'perna-bancada';
      legs.push(leg);
    }
  }
  // Tapete: placa fina de PVC (lateral) + face de cima com o material do tapete de corte (uv 0..1).
  const slab = new THREE.Mesh(new THREE.BoxGeometry(mat.width, mat.thickness, mat.depth), set.plastic({ color: '#23553C', moldY: -1e4, name: 'pvc-tapete' }));
  slab.position.set(mat.x, mat.thickness / 2 - 0.05, mat.z);
  const face = new THREE.Mesh(new THREE.PlaneGeometry(mat.width, mat.depth), set.cuttingMat({ size: [mat.width, mat.depth], margin: mat.margin }));
  face.rotation.x = -Math.PI / 2;
  face.position.set(mat.x, mat.thickness, mat.z);
  face.name = 'tapete-de-corte';
  const floor = new THREE.Mesh(new THREE.PlaneGeometry(7000, 7000), set.fabric({ color: floorColor, name: 'molleton-chao' }));
  floor.rotation.x = -Math.PI / 2;
  floor.position.y = floorY;
  floor.name = 'chao-estudio';
  for (const m of [top, ...legs, slab, face, floor]) {
    m.castShadow = m !== floor && m !== face;
    m.receiveShadow = true;
    root.add(m);
  }
  return root;
}
```

Em `src/debug/showcase.js`, trocar:

```
import * as THREE from 'three';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';
import { SHOWCASE_SET, SHOWCASE_OBJECTS } from '../data/showcase.js';
import { buildShowcaseObject } from './showcaseObjects.js';
import { tapeStrip } from '../clay/set/propGeometry.js';
```

por:

```
import * as THREE from 'three';
import { SHOWCASE_SET, SHOWCASE_OBJECTS } from '../data/showcase.js';
import { buildShowcaseObject } from './showcaseObjects.js';
import { buildAnimatorDesk } from '../maps/animatorDesk.js';
import { tapeStrip } from '../clay/set/propGeometry.js';
```

Em `src/debug/showcase.js`, trocar:

```
  #buildDesk() {
    const { desk, mat, floorY, floorColor } = SHOWCASE_SET;
    const wood = this.set.benchWood();
    const top = new THREE.Mesh(new RoundedBoxGeometry(desk.width, desk.thickness, desk.depth, 3, 4), wood);
    top.position.y = -desk.thickness / 2;
    top.name = 'tampo-bancada';
    const legH = -floorY - desk.thickness;
    const legGeo = new RoundedBoxGeometry(desk.legSize, legH, desk.legSize, 2, 5);
    const legs = [];
    for (const sx of [-1, 1]) {
      for (const sz of [-1, 1]) {
        const leg = new THREE.Mesh(legGeo, wood);
        leg.position.set(sx * (desk.width / 2 - desk.legInset), floorY + legH / 2, sz * (desk.depth / 2 - desk.legInset));
        leg.name = 'perna-bancada';
        legs.push(leg);
      }
    }
    // Tapete: placa fina de PVC (lateral) + face de cima com o material do tapete de corte (uv 0..1).
    const slab = new THREE.Mesh(new THREE.BoxGeometry(mat.width, mat.thickness, mat.depth), this.set.plastic({ color: '#23553C', moldY: -1e4, name: 'pvc-tapete' }));
    slab.position.set(mat.x, mat.thickness / 2 - 0.05, mat.z);
    const face = new THREE.Mesh(new THREE.PlaneGeometry(mat.width, mat.depth), this.set.cuttingMat({ size: [mat.width, mat.depth], margin: mat.margin }));
    face.rotation.x = -Math.PI / 2;
    face.position.set(mat.x, mat.thickness, mat.z);
    face.name = 'tapete-de-corte';
    const floor = new THREE.Mesh(new THREE.PlaneGeometry(7000, 7000), this.set.fabric({ color: floorColor, name: 'molleton-chao' }));
    floor.rotation.x = -Math.PI / 2;
    floor.position.y = floorY;
    floor.name = 'chao-estudio';
    for (const m of [top, ...legs, slab, face, floor]) {
      m.castShadow = m !== floor && m !== face;
      m.receiveShadow = true;
      this.root.add(m);
    }
  }
```

por:

```
  #buildDesk() {
    this.root.add(buildAnimatorDesk(this.set, SHOWCASE_SET));
  }
```

- [ ] **Passo 3: O quadro de hardboard perfurado no kit do set**

```js file=src/clay/set/pegboardMaterial.js
// Quadro de ferramentas de hardboard perfurado (Fase 4.1, bancada `arsenal`; QPB8, QPB13, QPB19 no item 13 do
// moodboard): chapa de fibra prensada marrom, face lisa com o fibrado fino e manchas de uso, e a grade de furos
// redondos (furo escuro com a borda levemente afundada). Os furos são procedurais no espaço do objeto (a face é o
// plano XY da peça, a espessura em Z), sem textura: nítidos de perto e, de longe, viram o tom médio (sem moiré).

import * as THREE from 'three';
import { createSetMaterial } from './setShader.js';

const linear = (hex) => new THREE.Color(hex);

/**
 * @param {object} tex texturas assadas do set (não usadas: o hardboard é todo procedural)
 * @param {{color?:string, fiber?:string, holeColor?:string, pitch?:number, hole?:number, origin?:number[],
 *          name?:string}} [opts] `origin` = centro de um furo no XY da peça; `pitch` = passo da grade; `hole` = raio
 */
export function pegboardMaterial(tex, {
  color = '#8E6B49', fiber = '#6E4F33', holeColor = '#1B130D', pitch = 25.4, hole = 3.3, origin = [0, 0], name = 'hardboard',
} = {}) {
  return createSetMaterial({
    name,
    params: { color: 0xffffff, roughness: 0.78, metalness: 0 },
    uniforms: {
      uPegColor: { value: linear(color) },
      uPegFiber: { value: linear(fiber) },
      uPegHole: { value: linear(holeColor) },
      uPegGrid: { value: new THREE.Vector4(pitch, hole, origin[0], origin[1]) },
    },
    light: { wrap: 0.32, lift: 0.07 },
    fragPars: /* glsl */ `
uniform vec3 uPegColor;
uniform vec3 uPegFiber;
uniform vec3 uPegHole;
uniform vec4 uPegGrid;
`,
    surface: /* glsl */ `
vec3 p = setP;
// Fibrado da chapa: grão fino e curto em todas as direções, manchas largas de tom e marcas de uso.
float grain = clayFbm3(vec3(p.xy * 0.21, p.z * 0.21 + 1.7), 3) * 0.5 + 0.5;
float blotch = clayNoise3(vec3(p.xy * 0.006, 4.2)) * 0.5 + 0.5;
vec3 col = mix(uPegColor, uPegFiber, grain * 0.38 + blotch * 0.22);
setRough += (grain - 0.5) * 0.08;
if (abs(setN.z) > 0.5) {
  // Face: grade de furos. De longe (a célula do pixel passa de um quinto do passo) o furo vira o tom médio.
  vec2 g = (p.xy - uPegGrid.zw) / uPegGrid.x;
  vec2 c = floor(g + 0.5);
  vec2 d = (g - c) * uPegGrid.x;
  float r = length(d);
  float aa = max(fwidth(r), 1e-3);
  float far = smoothstep(0.12, 0.35, fwidth(g.x));
  float holeMask = (1.0 - smoothstep(uPegGrid.y - aa, uPegGrid.y + aa, r)) * (1.0 - far);
  float rim = smoothstep(uPegGrid.y - aa, uPegGrid.y, r) * (1.0 - smoothstep(uPegGrid.y, uPegGrid.y * 1.5, r)) * (1.0 - far);
  float coverage = 3.14159 * uPegGrid.y * uPegGrid.y / (uPegGrid.x * uPegGrid.x);
  col = mix(col, uPegHole, holeMask);
  col = mix(col, mix(col, uPegHole, coverage), far);
  col *= 1.0 - rim * 0.18;
  vec2 dir = r > 1e-4 ? d / r : vec2(0.0);
  setObjN = normalize(setN + vec3(-dir * rim * 0.55, 0.0) * sign(setN.z));
  setRough += holeMask * 0.15;
}
diffuseColor.rgb = col;
`,
  });
}
```

Em `src/clay/set/index.js`, trocar:

```
import { paintMaterial, floorPaintMaterial } from './paintMaterials.js';

```

por:

```
import { paintMaterial, floorPaintMaterial } from './paintMaterials.js';
import { pegboardMaterial } from './pegboardMaterial.js';

```

Em `src/clay/set/index.js`, trocar:

```
  floorPaint: floorPaintMaterial,
});
```

por:

```
  floorPaint: floorPaintMaterial,
  pegboard: pegboardMaterial,
});
```

- [ ] **Passo 4: Números da bancada**

```js file=src/data/arsenal.js
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
```

- [ ] **Passo 5: Roda de modelar e suporte de arame; plantas a lápis**

```js file=src/maps/arsenal/turntable.js
// Roda de modelar e suporte de arame da bancada `arsenal` (Fase 4.1; QTT11 — a roda de escultor de metal; QTT9 —
// giratória de produto; QWS9, QWS12, QWS14 — suportes de arame em garfo, no item 13 do moodboard).
// A roda: pé pesado torneado, coluna e prato com anéis de centragem, tudo em metal de ferramenta com restos de massa.
// O suporte: tira de compensado no prato e dois garfos de arame; cada garfo sobe até encostar na parte de baixo da arma
// naquele ponto (medida no SDF da receita), então qualquer arma deita certinho nele.

import * as THREE from 'three';
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';
import { wireGeometry } from '../../clay/set/propGeometry.js';
import { bounds, compile } from '../../clay/sdf/nodes.js';
import { recipeWholeTree } from '../../weapons/model/recipe.js';

// Torno em volta de Y a partir de pares [raio, altura].
function latheY(profile, segments = 48) {
  return new THREE.LatheGeometry(profile.map(([r, y]) => new THREE.Vector2(Math.max(r, 0.001), y)), segments);
}

/**
 * Roda de modelar. O `spinner` é o grupo que gira (em cima do prato, y = 0 na face do prato).
 * @param {import('../../clay/set/index.js').SetLibrary} set
 * @param {object} def ARSENAL.turntable
 * @returns {{root:THREE.Group, spinner:THREE.Group, top:number}}
 */
export function buildBandingWheel(set, def) {
  const { foot, column, plate } = def;
  const root = new THREE.Group();
  root.name = 'roda-de-modelar';
  const metal = set.toolMetal({ color: '#9FA5AB', residueFrom: 0.62, length: plate.radius * 2, name: 'roda-aluminio' });
  const dark = set.toolMetal({ color: '#6F757B', residueFrom: 2, length: foot.radius * 2, name: 'roda-ferro' });
  // Pé: disco pesado com o chanfro de fundição e o degrau onde a coluna entra.
  const footGeo = latheY([
    [0, 0], [foot.radius - 1.2, 0], [foot.radius, 0.8], [foot.radius, foot.height - 1.6], [foot.radius - 2.4, foot.height],
    [column.radius + 3.2, foot.height + 0.6], [column.radius + 2.2, foot.height + 2.4], [0, foot.height + 2.4],
  ]);
  const columnTop = foot.height + column.height;
  const colGeo = latheY([
    [0, foot.height], [column.radius, foot.height], [column.radius, columnTop - 3], [column.radius + 1.6, columnTop - 2.2],
    [column.radius + 1.6, columnTop], [0, columnTop],
  ], 32);
  // Prato: face de cima com os anéis de centragem torneados (sulcos rasos), aba e o cubo de baixo.
  const profile = [[0, columnTop], [column.radius + 3, columnTop], [plate.radius - 3, columnTop + 0.8], [plate.radius, columnTop + 1.4],
    [plate.radius, columnTop + plate.height - 0.8], [plate.radius - 0.8, columnTop + plate.height]];
  const top = columnTop + plate.height;
  for (let i = plate.rings; i >= 1; i--) {
    const r = (plate.radius - 4) * (i / (plate.rings + 0.5));
    profile.push([r + 0.5, top], [r + 0.25, top - plate.ringDepth], [r - 0.25, top - plate.ringDepth], [r - 0.5, top]);
  }
  profile.push([0, top]);
  const plateGeo = latheY(profile, 64);
  const parts = [
    ['pe', footGeo, dark], ['coluna', colGeo, metal], ['prato', plateGeo, metal],
  ];
  for (const [name, geo, mat] of parts) {
    const mesh = new THREE.Mesh(geo, mat);
    mesh.name = `roda-${name}`;
    mesh.castShadow = true;
    mesh.receiveShadow = true;
    root.add(mesh);
  }
  const spinner = new THREE.Group();
  spinner.name = 'roda-giratorio';
  spinner.position.y = top;
  root.add(spinner);
  return { root, spinner, top };
}

/**
 * Parte de baixo da silhueta da arma num x (y mínimo com massa em z = 0), por um raio de baixo para cima no SDF.
 * @returns {number|null} null se não há massa nesse x
 */
export function underside(compiled, box, x, step = 0.04) {
  let y = box.min[1] - 0.5;
  while (y <= box.max[1] + 0.5) {
    const d = compiled.distance(x, y, 0);
    if (d < 0) return y;
    y += Math.max(d * 0.9, step);
  }
  return null;
}

/**
 * Suporte de arame para uma receita: a tira de compensado e os dois garfos (a 18% e 76% do comprimento), com a arma
 * posta em cima. Devolve o grupo do suporte e a posição da origem da arma no referencial do suporte.
 * @param {import('../../clay/set/index.js').SetLibrary} set
 * @param {object} def ARSENAL.stand
 * @param {object} recipe
 * @returns {{group:THREE.Group, weaponOffset:THREE.Vector3}}
 */
export function buildWireStand(set, def, recipe) {
  const tree = recipeWholeTree(recipe);
  const box = bounds(tree);
  const compiled = compile(tree);
  const length = box.max[0] - box.min[0];
  const height = box.max[1] - box.min[1];
  const centerX = (box.min[0] + box.max[0]) / 2;
  const forkXs = [0.18, 0.76].map((f) => box.min[0] + length * f);
  // Arame e garfo na medida da arma: a Glock pede arame fino e garfo baixo; a AWP, o arame cheio.
  const wire = Math.min(def.wire, Math.max(0.3, length * 0.016));
  const depth = Math.min(def.forkDepth, height * 0.16);
  // A arma fica alta o bastante para a parte mais baixa (carregador, empunhadura) passar livre da tira.
  const baseT = def.base.thickness;
  const lift = Math.max(def.lift, baseT + 2.5 - box.min[1]);
  const group = new THREE.Group();
  group.name = `suporte-${recipe.id}`;
  const base = new THREE.Mesh(new RoundedBoxGeometry(length * 1.05 + 4, baseT, Math.max(8, def.base.depth * Math.min(1, length / 40)), 2, 0.6), set.plywood());
  base.position.y = baseT / 2;
  base.name = 'suporte-base';
  group.add(base);
  const wires = [];
  for (const fx of forkXs) {
    const bottom = underside(compiled, box, fx) ?? box.min[1];
    // Meia largura da massa logo acima do apoio: os braços do garfo encostam dos dois lados.
    let half = 0.3;
    while (half < 4 && compiled.distance(fx, bottom + 0.35, half) < 0) half += 0.05;
    const x = fx - centerX;
    const tipY = lift + bottom - wire; // o arame encosta por baixo da massa
    const w = half + wire * 1.1;
    const post = new THREE.LineCurve3(new THREE.Vector3(x, baseT, 0), new THREE.Vector3(x, tipY, 0));
    const cradle = new THREE.CatmullRomCurve3([
      new THREE.Vector3(x, tipY + depth * 1.5, -w),
      new THREE.Vector3(x, tipY + depth * 0.4, -w * 0.97),
      new THREE.Vector3(x, tipY, -w * 0.5),
      new THREE.Vector3(x, tipY, 0),
      new THREE.Vector3(x, tipY, w * 0.5),
      new THREE.Vector3(x, tipY + depth * 0.4, w * 0.97),
      new THREE.Vector3(x, tipY + depth * 1.5, w),
    ]);
    wires.push(wireGeometry(post, wire, { radialSegments: 8 }), wireGeometry(cradle, wire, { radialSegments: 8 }));
  }
  const wireMesh = new THREE.Mesh(mergeGeometries(wires, false), set.wire());
  for (const g of wires) g.dispose();
  wireMesh.name = 'suporte-arame';
  group.add(wireMesh);
  for (const m of [base, wireMesh]) {
    m.castShadow = true;
    m.receiveShadow = true;
  }
  return { group, weaponOffset: new THREE.Vector3(-centerX, lift, 0) };
}
```

```js file=src/maps/arsenal/planSheets.js
// Plantas a lápis da bancada `arsenal` (Fase 4.1; QBP3, QBP13, QBP15 no item 13 do moodboard): uma folha de papel
// creme quadriculado por arma, com o contorno da planta de referência (tools/blender/refs/<id>.json) em grafite, a
// linha do eixo do cano em traço-ponto, a cota do comprimento com as setas, o nome escrito à caneta e o crédito da
// foto de origem em letra miúda. A faca não tem planta: a folha dela é a silhueta lateral da própria receita, sombreada
// a lápis ("desenhada de cabeça").

import * as THREE from 'three';
import { RNG } from '../../core/rng.js';
import { drawHandwriting } from '../../clay/set/labelAtlas.js';
import { createSetMaterial } from '../../clay/set/setShader.js';
import { gridFor, sideMask } from '../../weapons/model/silhouette.js';
import { recipeWholeTree } from '../../weapons/model/recipe.js';
import { bounds } from '../../clay/sdf/nodes.js';

/** Lê a planta de uma arma (null se não houver: a faca, ou arquivo ausente). */
export async function loadPlan(id) {
  try {
    const res = await fetch(new URL(`../../../tools/blender/refs/${id}.json`, import.meta.url));
    return res.ok ? await res.json() : null;
  } catch {
    return null;
  }
}

function sketchPath(g, ring, map, rng, jitter) {
  g.beginPath();
  ring.forEach(([x, y], i) => {
    const [px, py] = map(x, y);
    const jx = rng.float(-jitter, jitter);
    const jy = rng.float(-jitter, jitter);
    if (i === 0) g.moveTo(px + jx, py + jy);
    else g.lineTo(px + jx, py + jy);
  });
  g.closePath();
}

function arrowHead(g, x, y, dir, size) {
  g.beginPath();
  g.moveTo(x, y);
  g.lineTo(x - dir * size, y - size * 0.45);
  g.moveTo(x, y);
  g.lineTo(x - dir * size, y + size * 0.45);
  g.stroke();
}

/**
 * Desenha a folha de uma arma num canvas.
 * @param {{id:string, name:string, recipe:object, plan:object|null, lengthU:number}} item
 * @param {object} def ARSENAL.plans
 * @param {string} font fonte da etiqueta (com "{px}")
 * @returns {HTMLCanvasElement}
 */
export function drawPlanSheet(item, def, font) {
  const { width: W, height: H } = def.texture;
  const canvas = document.createElement('canvas');
  canvas.width = W;
  canvas.height = H;
  const g = canvas.getContext('2d');
  const rng = new RNG(`planta:${item.id}`);
  g.fillStyle = def.paper;
  g.fillRect(0, 0, W, H);
  // Papel quadriculado de 5 mm (a folha tem 160 u de largura).
  const cell = (W / 160) * 5;
  g.strokeStyle = def.grid;
  g.lineWidth = 1;
  for (let x = cell; x < W; x += cell) {
    g.beginPath();
    g.moveTo(x, 0);
    g.lineTo(x, H);
    g.stroke();
  }
  for (let y = cell; y < H; y += cell) {
    g.beginPath();
    g.moveTo(0, y);
    g.lineTo(W, y);
    g.stroke();
  }
  // Área do desenho: a arma inteira com margem, escala única nos dois eixos.
  const tree = recipeWholeTree(item.recipe);
  const box = bounds(tree);
  const boca = item.recipe.anchors.boca?.pos ?? [0, 0, 0];
  const rings = item.plan
    ? [item.plan.points, ...(item.plan.holes ?? [])].map((r) => r.map(([x, y]) => [x + boca[0], y + boca[1]]))
    : null;
  let x0 = box.min[0];
  let x1 = box.max[0];
  let y0 = box.min[1];
  let y1 = box.max[1];
  if (rings) {
    for (const [x, y] of rings[0]) {
      x0 = Math.min(x0, x);
      x1 = Math.max(x1, x);
      y0 = Math.min(y0, y);
      y1 = Math.max(y1, y);
    }
  }
  const area = { x: W * 0.07, y: H * 0.2, w: W * 0.86, h: H * 0.56 };
  const s = Math.min(area.w / (x1 - x0), area.h / (y1 - y0));
  const ox = area.x + (area.w - (x1 - x0) * s) / 2;
  const oy = area.y + (area.h + (y1 - y0) * s) / 2;
  const map = (x, y) => [ox + (x - x0) * s, oy - (y - y0) * s];
  g.lineJoin = 'round';
  g.lineCap = 'round';
  g.strokeStyle = def.graphite;
  if (rings) {
    // Grafite: um traço firme e dois de rascunho por cima, com tremor de mão.
    for (const [alpha, widthPx, jitter] of [[0.85, 2.2, 0.4], [0.3, 1.2, 1.6], [0.22, 1, 2.2]]) {
      g.globalAlpha = alpha;
      g.lineWidth = widthPx;
      for (const r of rings) {
        sketchPath(g, r, map, rng, jitter);
        g.stroke();
      }
    }
  } else {
    // Sem planta: a silhueta da receita, sombreada a lápis (tom leve por baixo e hachuras a 45° por cima).
    const grid = gridFor(x0, y0, x1, y1, Math.max(0.03, (x1 - x0) / 260));
    const mask = sideMask(tree, grid);
    const inside = (i, j) => i >= 0 && j >= 0 && i < grid.nx && j < grid.ny && mask[j * grid.nx + i] === 1;
    const cellPx = grid.cell * s;
    g.fillStyle = def.graphite;
    g.globalAlpha = 0.16;
    for (let j = 0; j < grid.ny; j++) {
      for (let i = 0; i < grid.nx; i++) {
        if (!inside(i, j)) continue;
        const [px, py] = map(grid.x0 + i * grid.cell, grid.y0 + (j + 1) * grid.cell);
        g.fillRect(px, py, cellPx + 0.5, cellPx + 0.5);
      }
    }
    g.globalAlpha = 0.45;
    g.lineWidth = 1.2;
    for (let j = 0; j < grid.ny; j++) {
      for (let i = 0; i < grid.nx; i++) {
        if (!inside(i, j) || (i + j) % 4 !== 0) continue;
        const [px, py] = map(grid.x0 + (i + 0.5) * grid.cell, grid.y0 + (j + 0.5) * grid.cell);
        g.beginPath();
        g.moveTo(px - cellPx * 1.6, py + cellPx * 1.6);
        g.lineTo(px + cellPx * 1.6, py - cellPx * 1.6);
        g.stroke();
      }
    }
    // Contorno: as bordas das células de massa que encostam no vazio, com o tremor do lápis.
    g.globalAlpha = 0.85;
    g.lineWidth = 1.8;
    g.beginPath();
    for (let j = 0; j < grid.ny; j++) {
      for (let i = 0; i < grid.nx; i++) {
        if (!inside(i, j)) continue;
        const xa = grid.x0 + i * grid.cell;
        const ya = grid.y0 + j * grid.cell;
        const edges = [[!inside(i, j - 1), [xa, ya], [xa + grid.cell, ya]], [!inside(i, j + 1), [xa, ya + grid.cell], [xa + grid.cell, ya + grid.cell]],
          [!inside(i - 1, j), [xa, ya], [xa, ya + grid.cell]], [!inside(i + 1, j), [xa + grid.cell, ya], [xa + grid.cell, ya + grid.cell]]];
        for (const [open, a, b] of edges) {
          if (!open) continue;
          const [ax, ay] = map(a[0], a[1]);
          const [bx, by] = map(b[0], b[1]);
          g.moveTo(ax + rng.float(-0.3, 0.3), ay + rng.float(-0.3, 0.3));
          g.lineTo(bx, by);
        }
      }
    }
    g.stroke();
  }
  // Eixo do cano em traço-ponto, passando da boca.
  g.globalAlpha = 0.5;
  g.lineWidth = 1;
  g.setLineDash([14, 5, 3, 5]);
  const [ax0, ay] = map(x0 - 1, 0);
  const [ax1] = map(x1 + 1.5, 0);
  g.beginPath();
  g.moveTo(ax0, ay);
  g.lineTo(ax1, ay);
  g.stroke();
  g.setLineDash([]);
  // Cota do comprimento embaixo.
  const [dx0, dyBase] = map(x0, y0);
  const [dx1] = map(x1, y0);
  const dy = dyBase + H * 0.07;
  g.globalAlpha = 0.75;
  g.lineWidth = 1.3;
  for (const x of [dx0, dx1]) {
    g.beginPath();
    g.moveTo(x, dyBase + 6);
    g.lineTo(x, dy + 8);
    g.stroke();
  }
  g.beginPath();
  g.moveTo(dx0, dy);
  g.lineTo(dx1, dy);
  g.stroke();
  arrowHead(g, dx0, dy, -1, 12);
  arrowHead(g, dx1, dy, 1, 12);
  g.globalAlpha = 1;
  g.fillStyle = def.graphite;
  g.strokeStyle = def.graphite;
  const lengthText = `${item.lengthU.toFixed(1).replace('.', ',')} u`;
  const lx = (dx0 + dx1) / 2 - lengthText.length * H * 0.018;
  drawHandwriting(g, lengthText, { x: lx, baseline: dy - 6, size: H * 0.06, font, rng, stroke: 0.02, wobble: 0.6 });
  // Nome à caneta no alto e o crédito da foto embaixo.
  g.fillStyle = def.ink;
  g.strokeStyle = def.ink;
  drawHandwriting(g, item.name, { x: W * 0.17, baseline: H * 0.155, size: H * 0.11, font, rng });
  g.font = `${Math.round(H * 0.032)}px ui-monospace, "Cascadia Mono", Consolas, monospace`;
  g.fillStyle = def.graphite;
  g.globalAlpha = 0.8;
  const credit = item.plan
    ? `planta: ${item.plan.source.file.replace(/^File:/, '')} · ${item.plan.source.license} · ${item.plan.source.artist}`
    : 'desenhada de cabeça (sem foto de referência)';
  g.fillText(credit.length > 96 ? `${credit.slice(0, 93)}…` : credit, W * 0.05, H * 0.95);
  g.globalAlpha = 1;
  return canvas;
}

/** Papel da folha com o desenho: fibras do papel do set por cima da cor, grafite um pouco brilhante contra a luz. */
export function planSheetMaterial(tex, map, name) {
  return createSetMaterial({
    name,
    params: { color: 0xffffff, roughness: 0.88, metalness: 0, side: THREE.DoubleSide },
    uniforms: { uPlan: { value: map }, uPaperTex: { value: tex.paper } },
    light: { wrap: 0.35, lift: 0.08, translucency: 0.25 },
    fragPars: 'uniform sampler2D uPlan;\nuniform sampler2D uPaperTex;',
    surface: /* glsl */ `
vec3 art = texture(uPlan, setUv).rgb;
vec4 pt = texture(uPaperTex, setUv * vec2(3.2, 1.84));
float lum = dot(art, vec3(0.299, 0.587, 0.114));
float graphite = 1.0 - smoothstep(0.35, 0.75, lum);
vec3 col = art * (0.95 + 0.1 * (pt.b - 0.5));
diffuseColor.rgb = col;
setMetal += graphite * 0.25;
setRough += (pt.a - 0.5) * 0.06 - graphite * 0.3;
mat3 tbn = setCotangentFrame(setN, setP, setUv * vec2(3.2, 1.84));
setObjN = normalize(tbn * vec3((pt.rg * 2.0 - 1.0) * 0.25, 1.0));
`,
  });
}
```

- [ ] **Passo 6: A bancada**

```js file=src/maps/arsenal/bench.js
// Bancada de armas do mapa `arsenal` (Fase 4.1; docs/phases/phase-4.md, seção 4.1, "Bancada de armas"): a mesa do
// animador com o quadro de hardboard perfurado no fundo (ferramentas de modelar penduradas e a planta a lápis de cada
// arma presa com fita), as armas deitadas no tapete em fileiras com a etiqueta de fita de cada uma e, na frente, a roda
// de modelar com a arma escolhida no suporte de arame. Referências no item 13 do moodboard (QGW, QPB, QTT, QWS, QBP).

import * as THREE from 'three';
import { ARSENAL } from '../../data/arsenal.js';
import { WEAPONS } from '../../data/weapons.js';
import { RNG } from '../../core/rng.js';
import { buildAnimatorDesk } from '../animatorDesk.js';
import { sculptTool, tapeStrip, wireGeometry } from '../../clay/set/propGeometry.js';
import { bakeLabelAtlas } from '../../clay/set/labelAtlas.js';
import { tapeLabelMaterial } from '../../clay/set/paperMaterials.js';
import { bounds } from '../../clay/sdf/nodes.js';
import { recipeWholeTree, weaponFaction } from '../../weapons/model/recipe.js';
import { placeReference, silhouetteIoU, silhouetteLength } from '../../weapons/model/silhouette.js';
import { buildBandingWheel, buildWireStand } from './turntable.js';
import { drawPlanSheet, loadPlan, planSheetMaterial } from './planSheets.js';

const DEG = Math.PI / 180;
const labelLength = (aspect, L) => Math.max(L.tapeWidth * 2.2, aspect * L.textHeight + L.margin * 2);

export class ArsenalBench {
  /**
   * @param {{set:import('../../clay/set/index.js').SetLibrary, weapons:import('../../weapons/model/weaponLibrary.js').WeaponLibrary,
   *          anisotropy?:number, log?:object}} deps
   */
  constructor({ set, weapons, anisotropy = 8, log = null }) {
    this.set = set;
    this.weapons = weapons;
    this.anisotropy = anisotropy;
    this.log = log;
    this.root = new THREE.Group();
    this.root.name = 'arsenal';
    this.matTop = ARSENAL.desk.mat.thickness;
    this.plans = new Map(); // id → planta (ou null)
    this.displays = new Map(); // id → instância deitada na fileira
    this.textures = [];
    this.labelAtlas = null;
    this.wheel = null;
    this.stand = null;
    this.weapon = null; // instância na roda
    this.state = { id: null, faction: null, lod: 'perto', skin: null, explode: 0, anchors: false, plan: false, spin: true };
    this.skinMaterials = [];
    this.overlay = null;
    this.onChange = null; // o painel escuta (troca de arma, geração pronta)
    this.selecting = Promise.resolve();
  }

  /** Ids com receita, na ordem das fileiras. */
  get ids() {
    return ARSENAL.rows.flatMap((r) => r.ids).filter((id) => this.weapons.has(id));
  }

  async build(scene) {
    const t0 = performance.now();
    scene.add(this.root);
    this.root.add(buildAnimatorDesk(this.set, ARSENAL.desk));
    const ids = this.ids;
    await Promise.all(ids.map(async (id) => this.plans.set(id, await loadPlan(id))));
    this.#buildPegboard();
    this.#buildPlans(ids);
    await this.#buildRows();
    const t = ARSENAL.turntable;
    this.wheel = buildBandingWheel(this.set, t);
    this.wheel.root.position.set(t.x, this.matTop, t.z);
    this.root.add(this.wheel.root);
    await this.select(ids[0] ?? null);
    this.log?.info(`bancada de armas montada: ${ids.length} armas em ${(performance.now() - t0).toFixed(0)} ms`);
    return this;
  }

  #buildPegboard() {
    const P = ARSENAL.pegboard;
    const nx = Math.floor(P.width / P.pitch);
    const ny = Math.floor(P.height / P.pitch);
    const material = this.set.pegboard({
      color: P.color, fiber: P.fiber, holeColor: P.holeColor, pitch: P.pitch, hole: P.hole,
      origin: [-(nx - 1) * P.pitch / 2, -(ny - 1) * P.pitch / 2],
    });
    const board = new THREE.Mesh(new THREE.BoxGeometry(P.width, P.height, P.thickness), material);
    board.name = 'quadro-de-ferramentas';
    board.position.set(0, this.matTop + P.height / 2 + 6, P.z);
    board.castShadow = true;
    board.receiveShadow = true;
    this.root.add(board);
    this.board = board;
    // Dois pés de ripa atrás segurando o quadro em pé.
    const foot = new THREE.BoxGeometry(22, P.foot.height, P.foot.depth);
    for (const sx of [-1, 1]) {
      const f = new THREE.Mesh(foot, this.set.balsa());
      f.position.set(sx * (P.width / 2 - 60), this.matTop + P.foot.height / 2, P.z - P.thickness / 2 - P.foot.depth / 2);
      f.castShadow = true;
      f.receiveShadow = true;
      f.name = 'pe-do-quadro';
      this.root.add(f);
    }
    // Ferramentas de modelar penduradas, cada uma num gancho de arame.
    const wood = this.set.benchWood();
    const face = P.z + P.thickness / 2;
    for (const tdef of ARSENAL.tools) {
      const tool = sculptTool(tdef.kind, { length: tdef.length });
      const g = new THREE.Group();
      g.name = `ferramenta-${tdef.kind}`;
      g.add(new THREE.Mesh(tool.handle, wood), new THREE.Mesh(tool.metal, this.set.toolMetal({ length: tdef.length })));
      g.rotation.z = -tdef.rotDeg * DEG;
      const x = -P.width / 2 + tdef.at[0];
      const y = this.matTop + 6 + tdef.at[1];
      g.position.set(x, y + tdef.length / 2 - 18, face + 5);
      const hook = new THREE.CatmullRomCurve3([
        new THREE.Vector3(x, y + tdef.length / 2 - 4, face - 1), new THREE.Vector3(x, y + tdef.length / 2 - 4, face + 8),
        new THREE.Vector3(x, y + tdef.length / 2 + 2, face + 11),
      ]);
      const hookMesh = new THREE.Mesh(wireGeometry(hook, 0.9), this.set.wire());
      hookMesh.name = 'gancho';
      for (const m of [...g.children, hookMesh]) {
        m.castShadow = true;
        m.receiveShadow = true;
      }
      this.root.add(g, hookMesh);
    }
  }

  #buildPlans(ids) {
    const D = ARSENAL.plans;
    const P = ARSENAL.pegboard;
    const face = P.z + P.thickness / 2 + 0.35;
    const tape = this.set.tape({ width: 19 });
    const rng = new RNG('plantas-arsenal');
    ids.forEach((id, i) => {
      const recipe = this.weapons.recipe(id);
      const col = i % D.cols;
      const row = Math.floor(i / D.cols);
      const inRow = Math.min(D.cols, ids.length - row * D.cols);
      const canvas = drawPlanSheet({
        id, recipe, name: WEAPONS[id]?.name ?? id, plan: this.plans.get(id), lengthU: this.#length(recipe),
      }, D, ARSENAL.label.font);
      const texture = new THREE.CanvasTexture(canvas);
      texture.colorSpace = THREE.SRGBColorSpace;
      texture.anisotropy = this.anisotropy;
      this.textures.push(texture);
      const material = this.set.adopt(`planta-${id}`, planSheetMaterial(this.set.textures, texture, `planta-${id}`));
      const sheet = new THREE.Mesh(new THREE.PlaneGeometry(D.width, D.height), material);
      sheet.name = `planta-${id}`;
      const x = (col - (inRow - 1) / 2) * (D.width + D.gapX);
      const y = this.matTop + 6 + D.top - row * (D.height + D.gapY);
      sheet.position.set(x, y, face);
      sheet.rotation.z = rng.float(-1.6, 1.6) * DEG;
      sheet.receiveShadow = true;
      this.root.add(sheet);
      // Duas tiras de fita nos cantos de cima, tortas.
      for (const sx of [-1, 1]) {
        const strip = new THREE.Mesh(tapeStrip(D.tapeLength, 19, { seed: `planta-${id}-${sx}` }), tape);
        strip.rotation.set(0, 0, (sx * 38 + rng.float(-8, 8)) * DEG);
        strip.position.set(sx * (D.width / 2 - 6), D.height / 2 - 6, 0.25);
        strip.receiveShadow = true;
        sheet.add(strip);
      }
    });
  }

  #length(recipe) {
    return this.plans.get(recipe.id)?.lengthU ?? silhouetteLength(recipe);
  }

  async #buildRows() {
    const L = ARSENAL.label;
    const texts = [];
    for (const row of ARSENAL.rows) {
      texts.push(row.label);
      for (const id of row.ids) if (this.weapons.has(id)) texts.push(WEAPONS[id]?.name ?? id);
    }
    this.labelAtlas = bakeLabelAtlas(texts, {
      width: L.atlas.width, cellHeight: L.atlas.cellHeight, columns: L.atlas.columns, font: L.font, seed: 'etiquetas-arsenal', anisotropy: this.anisotropy,
    });
    const rng = new RNG('fileiras-arsenal');
    let k = 0;
    const strip = (text, x, z, tilt) => {
      const info = this.labelAtlas.labels[k++];
      const length = labelLength(info.aspect, L);
      const material = this.set.adopt(`etiqueta-arsenal-${text}`, tapeLabelMaterial(this.set.textures, {
        atlas: this.labelAtlas.texture, rect: info.rect, length, width: L.tapeWidth, margin: L.margin, textHeight: L.textHeight,
        ink: L.ink, name: `etiqueta-arsenal-${text}`,
      }));
      const mesh = new THREE.Mesh(tapeStrip(length, L.tapeWidth, { seed: `arsenal-${text}` }), material);
      mesh.rotation.set(-Math.PI / 2, 0, tilt * DEG);
      mesh.position.set(x + length / 2, this.matTop + L.lift, z);
      mesh.receiveShadow = true;
      mesh.name = `etiqueta-${text}`;
      this.root.add(mesh);
    };
    for (const row of ARSENAL.rows) {
      strip(row.label, ARSENAL.rowLabelX, row.z + 4, rng.float(-3, 3));
      let x = ARSENAL.rowX0;
      for (const id of row.ids) {
        if (!this.weapons.has(id)) continue;
        const inst = await this.weapons.instance(id, { lod: 'perto' });
        const b = bounds(recipeWholeTree(this.weapons.recipe(id)));
        // Deitada com o lado direito para cima: +Z da arma vira +Y do mundo (o topo aponta para o fundo).
        inst.rotation.set(-Math.PI / 2, 0, rng.float(-2, 2) * DEG);
        inst.position.set(x - b.min[0], this.matTop - b.min[2] + 0.15, row.z);
        inst.name = `fileira-${id}`;
        this.root.add(inst);
        this.displays.set(id, inst);
        strip(WEAPONS[id]?.name ?? id, x, row.z - b.min[1] + ARSENAL.labelForward, rng.float(-4, 4));
        x += b.max[0] - b.min[0] + ARSENAL.rowGap;
      }
    }
  }

  /** Troca a arma da roda (fila: pedidos seguidos esperam o anterior). */
  select(id) {
    this.selecting = this.selecting.then(() => this.#place(id, { faction: null })).catch((err) => this.log?.error('bancada:', err));
    return this.selecting;
  }

  /** Remonta a arma da roda com o estado atual (facção, nível). */
  refresh() {
    this.selecting = this.selecting.then(() => this.#place(this.state.id, { faction: this.state.faction })).catch((err) => this.log?.error('bancada:', err));
    return this.selecting;
  }

  async #place(id, { faction }) {
    this.#clearWheel();
    if (!id || !this.weapons.has(id)) {
      this.state.id = null;
      this.onChange?.();
      return;
    }
    const recipe = this.weapons.recipe(id);
    this.state.id = id;
    this.state.faction = faction ?? weaponFaction(id);
    const weapon = await this.weapons.instance(id, { lod: this.state.lod, faction: this.state.faction });
    if (this.state.id !== id) return;
    const stand = buildWireStand(this.set, ARSENAL.stand, recipe);
    stand.group.add(weapon);
    weapon.position.copy(stand.weaponOffset);
    this.stand = stand.group;
    this.weapon = weapon;
    this.wheel.spinner.add(stand.group);
    this.#applySkin();
    this.#applyExplode();
    this.#applyAnchors();
    this.#applyOverlay();
    this.onChange?.();
  }

  #clearWheel() {
    if (this.stand) {
      this.stand.removeFromParent();
      this.stand.traverse((o) => {
        if (o.geometry && !o.geometry.userData?.shared) o.geometry.dispose();
      });
    }
    this.#disposeSkin();
    this.overlay?.geometry.dispose();
    this.overlay?.material.dispose();
    this.overlay = null;
    this.stand = null;
    this.weapon = null;
  }

  setFaction(faction) {
    this.state.faction = faction;
    return this.refresh();
  }

  setLod(lod) {
    this.state.lod = lod;
    return this.refresh();
  }

  setSkin(skin) {
    this.state.skin = skin || null;
    this.#applySkin();
  }

  #disposeSkin() {
    for (const m of this.skinMaterials) m.dispose();
    this.skinMaterials = [];
  }

  #applySkin() {
    if (!this.weapon) return;
    this.#disposeSkin();
    const skin = this.state.skin;
    let clones = null;
    this.weapon.traverse((o) => {
      if (!o.isMesh) return;
      if (!o.userData.sharedMaterials) o.userData.sharedMaterials = o.material;
      if (!skin) {
        o.material = o.userData.sharedMaterials;
        return;
      }
      // A skin vale para a arma inteira: um clone de cada massa (os materiais compartilhados não mudam).
      if (!clones) {
        clones = o.userData.sharedMaterials.map((m) => {
          const c = m.clone().setSkin(skin);
          c.userData.shared = false;
          return c;
        });
        this.skinMaterials = clones;
      }
      o.material = clones;
    });
  }

  setExplode(v) {
    this.state.explode = v;
    this.#applyExplode();
  }

  #applyExplode() {
    const parts = this.weapon?.userData.weapon.parts;
    if (!parts) return;
    for (const [name, holder] of Object.entries(parts)) {
      const dir = ARSENAL.explode.dirs[name] ?? [0, 0, 0];
      const k = this.state.explode * ARSENAL.explode.max;
      holder.position.set(holder.userData.rest[0] + dir[0] * k, holder.userData.rest[1] + dir[1] * k, holder.userData.rest[2] + dir[2] * k);
    }
  }

  setAnchors(on) {
    this.state.anchors = on;
    this.#applyAnchors();
  }

  #applyAnchors() {
    const anchors = this.weapon?.userData.weapon.anchors;
    if (!anchors) return;
    for (const a of Object.values(anchors)) {
      const helper = a.getObjectByName('eixos-ancora');
      if (this.state.anchors && !helper) {
        const axes = new THREE.AxesHelper(ARSENAL.anchorSize);
        axes.name = 'eixos-ancora';
        axes.material.depthTest = false;
        axes.renderOrder = 10;
        a.add(axes);
      } else if (!this.state.anchors && helper) {
        helper.removeFromParent();
        helper.geometry.dispose();
        helper.material.dispose();
      }
    }
  }

  setPlanOverlay(on) {
    this.state.plan = on;
    this.#applyOverlay();
  }

  #applyOverlay() {
    this.overlay?.removeFromParent();
    this.overlay?.geometry.dispose();
    this.overlay?.material.dispose();
    this.overlay = null;
    const plan = this.plans.get(this.state.id);
    if (!this.state.plan || !plan || !this.weapon) return;
    const recipe = this.weapons.recipe(this.state.id);
    const { outline, holes } = placeReference(recipe, plan);
    const z = bounds(recipeWholeTree(recipe)).max[2] + ARSENAL.planOverlay.lift;
    const segs = [];
    for (const ring of [outline, ...holes]) {
      for (let i = 0; i < ring.length; i++) {
        const a = ring[i];
        const b = ring[(i + 1) % ring.length];
        segs.push(a[0], a[1], z, b[0], b[1], z);
      }
    }
    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.Float32BufferAttribute(segs, 3));
    const mat = new THREE.LineBasicMaterial({ color: ARSENAL.planOverlay.color, depthTest: false, transparent: true, opacity: 0.9 });
    this.overlay = new THREE.LineSegments(geo, mat);
    this.overlay.name = 'planta-sobreposta';
    this.overlay.renderOrder = 11;
    this.weapon.add(this.overlay);
  }

  setSpin(on) {
    this.state.spin = on;
  }

  /** IoU da silhueta lateral da arma da roda com a planta (null sem planta). */
  measure() {
    const plan = this.plans.get(this.state.id);
    if (!plan) return null;
    return silhouetteIoU(this.weapons.recipe(this.state.id), plan, { cell: 0.1 }).iou;
  }

  /**
   * Relê a receita da arma da roda do disco (depois de exportar do Blender) e remonta a roda e a fileira. As instâncias
   * dessa arma saem da cena antes de a biblioteca descartar as malhas (WeaponLibrary.reload) e voltam novas no fim,
   * mesmo se a releitura falhar (aí com a receita que continuou valendo).
   */
  async reload() {
    const id = this.state.id;
    if (!id) return;
    this.#clearWheel();
    const old = this.displays.get(id);
    const slot = old ? { parent: old.parent, position: old.position.clone(), rotation: old.rotation.clone(), name: old.name } : null;
    old?.removeFromParent();
    this.displays.delete(id);
    try {
      await this.weapons.reload(id, this.state.lod);
    } finally {
      if (slot) {
        try {
          const fresh = await this.weapons.instance(id, { lod: 'perto' });
          fresh.position.copy(slot.position);
          fresh.rotation.copy(slot.rotation);
          fresh.name = slot.name;
          slot.parent.add(fresh);
          this.displays.set(id, fresh);
        } catch (err) {
          this.log?.error(`bancada: a fileira ficou sem ${id}:`, err);
        }
      }
      await this.refresh();
    }
  }

  frame(dt) {
    if (this.state.spin && this.wheel) this.wheel.spinner.rotation.y += ARSENAL.turntable.spin * dt;
  }

  dispose() {
    this.#clearWheel();
    this.labelAtlas?.dispose();
    this.labelAtlas = null;
    for (const t of this.textures) t.dispose();
    this.textures = [];
    this.displays.clear();
    this.onChange = null;
  }
}
```

- [ ] **Passo 7: Controles de painel divididos, o painel da bancada e o mapa**

```js file=src/debug/panelControls.js
// Controles dos painéis de fita crepe dos mapas de teste (vitrine, arsenal): régua deslizante com rótulo e valor,
// cartão com a fita do título, interruptor com rótulo e grupo de botões "segmentado". Classes em styles/showcase.css.

import { h } from '../ui/dom.js';

let uid = 0;

/** Id único para ligar rótulo e controle. */
export const controlId = () => `vt-${++uid}`;

/** Régua deslizante com rótulo e valor. `onInput` a cada movimento; `onCommit` ao soltar (mudanças caras). */
export function slider({ label, min, max, step, value, format, onInput, onCommit = null }) {
  const id = controlId();
  const input = h('input.clay-range', { id, type: 'range', min, max, step });
  const out = h('output.vt-value', { for: id });
  const paint = (v) => {
    input.value = String(v);
    input.style.setProperty('--fill', `${((v - min) / (max - min)) * 100}%`);
    out.textContent = format(v);
  };
  input.addEventListener('input', () => {
    const v = Number(input.value);
    paint(v);
    onInput(v);
  });
  if (onCommit) input.addEventListener('change', () => onCommit(Number(input.value)));
  paint(value);
  const el = h('div.vt-row', null, h('label.vt-label', { for: id }, label), input, out);
  return { el, set: paint };
}

/** Cartão do painel com o título numa tira de fita. */
export function section(title, ...children) {
  return h('section.vt-card', null, h('h3.tape-label.vt-tape', null, title), ...children);
}

/** Interruptor (checkbox com papel de switch) com rótulo. */
export function switchRow(label, { checked = false, onChange }) {
  const id = controlId();
  const input = h('input.clay-switch', { id, type: 'checkbox', role: 'switch' });
  input.checked = checked;
  input.addEventListener('change', () => onChange(input.checked));
  const el = h('div.vt-row.vt-inline', null, input, h('label.vt-label', { for: id }, label));
  return { el, set: (v) => { input.checked = v; } };
}

/**
 * Grupo de botões de escolha única. `items` = [{id, label}]; `onPick(id)` no clique; `set(id)` marca o escolhido.
 */
export function segmented(ariaLabel, items, onPick) {
  const buttons = items.map(({ id, label }) => {
    const b = h('button.seg', { type: 'button', role: 'radio', dataset: { pick: id } }, label);
    b.addEventListener('click', () => onPick(id));
    return b;
  });
  const el = h('div.segmented', { role: 'radiogroup', 'aria-label': ariaLabel }, ...buttons);
  const set = (id) => {
    for (const b of buttons) {
      const on = b.dataset.pick === id;
      b.classList.toggle('is-on', on);
      b.setAttribute('aria-checked', on ? 'true' : 'false');
    }
  };
  return { el, set, buttons };
}
```

Em `src/debug/showcasePanel.js`, trocar:

```
import { h, clear } from '../ui/dom.js';
import { settingRow } from '../ui/settingControls.js';
```

por:

```
import { h, clear } from '../ui/dom.js';
import { controlId, section, slider } from './panelControls.js';
import { settingRow } from '../ui/settingControls.js';
```

Em `src/debug/showcasePanel.js`, trocar:

```

let uid = 0;

/** Régua deslizante com rótulo e valor. `onInput` a cada movimento; `onCommit` ao soltar (mudanças caras). */
function slider({ label, min, max, step, value, format, onInput, onCommit = null }) {
  const id = `vt-${++uid}`;
  const input = h('input.clay-range', { id, type: 'range', min, max, step });
  const out = h('output.vt-value', { for: id });
  const paint = (v) => {
    input.value = String(v);
    input.style.setProperty('--fill', `${((v - min) / (max - min)) * 100}%`);
    out.textContent = format(v);
  };
  input.addEventListener('input', () => {
    const v = Number(input.value);
    paint(v);
    onInput(v);
  });
  if (onCommit) input.addEventListener('change', () => onCommit(Number(input.value)));
  paint(value);
  const el = h('div.vt-row', null, h('label.vt-label', { for: id }, label), input, out);
  return { el, set: paint };
}

function section(title, ...children) {
  return h('section.vt-card', null, h('h3.tape-label.vt-tape', null, title), ...children);
}

const fx = (d) => (v) => v.toFixed(d);
```

por:

```

const fx = (d) => (v) => v.toFixed(d);
```

Em `src/debug/showcasePanel.js`, trocar:

```
  const prints = slider({ label: 'Digitais e ferramenta (×)', ...P.fingerprints, value: bench.multipliers.fingerprints, format: (v) => `×${v.toFixed(2)}`, onInput: (v) => bench.setClayMultipliers({ fingerprints: v }) });
  const probeId = `vt-${++uid}`;
  const probe = h('input.clay-switch', { id: probeId, type: 'checkbox', role: 'switch' });
```

por:

```
  const prints = slider({ label: 'Digitais e ferramenta (×)', ...P.fingerprints, value: bench.multipliers.fingerprints, format: (v) => `×${v.toFixed(2)}`, onInput: (v) => bench.setClayMultipliers({ fingerprints: v }) });
  const probeId = controlId();
  const probe = h('input.clay-switch', { id: probeId, type: 'checkbox', role: 'switch' });
```

Em `src/debug/showcasePanel.js`, trocar:

```
  });
  const autoId = `vt-${++uid}`;
  const autoFocus = h('input.clay-switch', { id: autoId, type: 'checkbox', role: 'switch' });
```

por:

```
  });
  const autoId = controlId();
  const autoFocus = h('input.clay-switch', { id: autoId, type: 'checkbox', role: 'switch' });
```

```js file=src/maps/arsenal/panel.js
// Painel de fita crepe da bancada `arsenal` (Tab solta o mouse; o MatchState chama open/close pelo `map.panel`):
// escolher a arma da roda, a facção do acento, o nível de detalhe e uma skin; explodir os grupos, mostrar as âncoras,
// sobrepor a planta, parar a roda, medir a silhueta contra a planta, reler a receita depois de exportar do Blender e
// "segurar" a arma (o viewmodel com a câmera parada). Linha de informação com triângulos e tempo de geração.

import { h } from '../../ui/dom.js';
import { WEAPONS } from '../../data/weapons.js';
import { CLAY_SKINS, CLAY_SKIN_IDS } from '../../data/claySkins.js';
import { section, segmented, slider, switchRow } from '../../debug/panelControls.js';

const FACTIONS = [
  { id: 'tr', label: 'Massa Crua' },
  { id: 'ct', label: 'Tropa do Estúdio' },
  { id: 'ambos', label: 'Dos dois lados' },
];
const LODS = [{ id: 'perto', label: 'Perto (0,14 u)' }, { id: 'mundo', label: 'Mundo (0,35 u)' }];

/**
 * @param {object} s serviços do jogo
 * @param {{bench:import('./bench.js').ArsenalBench, onClose:Function, onHold?:Function, isHolding?:()=>boolean}} deps
 *   `onHold` liga/desliga o "segurar" (o mapa cuida da câmera e do viewmodel); `isHolding` diz se está segurando
 */
export function createArsenalPanel(s, { bench, onClose, onHold = null, isHolding = () => false }) {
  const weaponSeg = segmented('Arma na roda', bench.ids.map((id) => ({ id, label: WEAPONS[id]?.name ?? id })), (id) => bench.select(id));
  const factionSeg = segmented('Facção do acento', FACTIONS, (id) => bench.setFaction(id));
  const lodSeg = segmented('Nível de detalhe', LODS, (id) => bench.setLod(id));
  const skinSelect = h('select.clay-select', { 'aria-label': 'Skin' },
    h('option', { value: '' }, 'Sem skin (a massa da receita)'),
    ...CLAY_SKIN_IDS.map((id) => h('option', { value: id }, CLAY_SKINS[id].label)));
  skinSelect.addEventListener('change', () => bench.setSkin(skinSelect.value));
  const explode = slider({
    label: 'Explodir os grupos', min: 0, max: 1, step: 0.01, value: 0, format: (v) => `${Math.round(v * 100)}%`,
    onInput: (v) => bench.setExplode(v),
  });
  const anchors = switchRow('Mostrar as âncoras (mãos, boca, ejeção)', { onChange: (v) => bench.setAnchors(v) });
  const plan = switchRow('Planta por cima da silhueta', { onChange: (v) => bench.setPlanOverlay(v) });
  const spin = switchRow('Girar a roda', { checked: true, onChange: (v) => bench.setSpin(v) });
  const info = h('p.vt-note', { role: 'status' });
  const measureOut = h('p.vt-note', { role: 'status' }, 'IoU da silhueta lateral × planta: aperte "Medir" (trava ~1 s).');
  const measure = h('button.btn-clay.is-small', { type: 'button' }, 'Medir a silhueta');
  measure.addEventListener('click', () => {
    const t0 = performance.now();
    const iou = bench.measure();
    measureOut.textContent = iou === null ? 'Esta arma não tem planta.'
      : `IoU ${iou.toFixed(3)} (aceite: ≥ 0,8) · ${(performance.now() - t0).toFixed(0)} ms`;
  });
  const reload = h('button.btn-clay.is-small', { type: 'button' }, 'Reler a receita do disco');
  const reloadOut = h('p.vt-note', { role: 'status' }, 'Depois de exportar do Blender: a arma da roda e a da fileira voltam com a receita nova.');
  reload.addEventListener('click', async () => {
    reloadOut.textContent = 'Relendo e gerando…';
    try {
      await bench.reload();
      reloadOut.textContent = `Receita de ${bench.state.id} relida.`;
    } catch (err) {
      reloadOut.textContent = `Falhou: ${err?.message ?? err}`;
    }
  });
  const HOLD_LABELS = ['Segurar (primeira pessoa)', 'Soltar a arma'];
  const hold = h('button.btn-clay.is-primary.is-small', { type: 'button', hidden: !onHold }, HOLD_LABELS[0]);
  hold.addEventListener('click', () => {
    onHold?.();
    sync();
  });

  const close = h('button.btn-clay.is-small', { type: 'button' }, 'Voltar à câmera (Tab)');
  close.addEventListener('click', () => onClose());
  const root = h('aside.vt-panel', { hidden: true, 'aria-label': 'Painel da bancada de armas' },
    h('header.vt-head', null, h('h2.vt-title', null, 'Bancada de armas'),
      h('p.vt-note', null, 'A arma da roda sai da receita em src/data/armas/. Clique na cena ou Tab/Esc para voltar à câmera.'), close),
    section('Arma', weaponSeg.el, hold, info),
    section('Massa', factionSeg.el, h('div.vt-row', null, h('span.vt-label', null, 'Skin'), skinSelect), lodSeg.el),
    section('Oficina', explode.el, anchors.el, plan.el, spin.el, measure, measureOut, reload, reloadOut),
  );
  root.addEventListener('keydown', (e) => {
    if (e.code === 'Tab') {
      e.preventDefault();
      onClose();
    }
  });
  s.uiRoot.append(root);

  function sync() {
    const st = bench.state;
    weaponSeg.set(st.id);
    factionSeg.set(st.faction);
    lodSeg.set(st.lod);
    skinSelect.value = st.skin ?? '';
    explode.set(st.explode);
    anchors.set(st.anchors);
    plan.set(st.plan);
    spin.set(st.spin);
    hold.textContent = HOLD_LABELS[isHolding() ? 1 : 0];
    const row = s.weaponModels.report().find((r) => r.id === st.id && r.lod === st.lod);
    info.textContent = row
      ? `${WEAPONS[st.id]?.name ?? st.id}: ${row.state} · ${row.triangles.toLocaleString('pt-BR')} triângulos em ${row.groups} grupo(s) · gerada em ${row.ms} ms`
      : 'Nenhuma arma na roda.';
  }
  bench.onChange = sync;

  return {
    root,
    open() {
      sync();
      root.hidden = false;
    },
    close() {
      root.hidden = true;
    },
    refresh: sync,
    dispose() {
      bench.onChange = null;
      root.remove();
    },
  };
}
```

```js file=src/maps/arsenal/index.js
// Mapa `arsenal` — bancada de armas da Fase 4.1 (docs/phases/phase-4.md, seção 4.1, "Bancada de armas"): a mesa do
// animador com a luz da vitrine virada em bancada de armeiro, as armas de massinha geradas das receitas deitadas em
// fileiras, a roda de modelar com a arma escolhida e o painel de fita crepe (Tab). É também o banco do aceite das
// armas: costura, boil, digitais, veios, acento, silhueta × planta, e o caminho do Blender (reler a receita).

import * as THREE from 'three';
import { STUDIO_RIGS } from '../../data/studioRigs.js';
import { ARSENAL } from '../../data/arsenal.js';
import { HULL } from '../../data/movement.js';
import { EV } from '../../core/events.js';
import { registerMap } from '../registry.js';
import { StudioRig } from '../../render/studio/studioRig.js';
import { ArsenalBench } from './bench.js';
import { createArsenalPanel } from './panel.js';

const DEG = Math.PI / 180;

async function build({ render, config, services }) {
  const scene = new THREE.Scene();
  scene.name = 'arsenal';
  scene.fog = new THREE.FogExp2(0x160f0c, 0.0001);

  const bench = new ArsenalBench({ set: services.set, weapons: services.weaponModels, anisotropy: render.anisotropy, log: services.log });
  await bench.build(scene);

  const rigDef = STUDIO_RIGS[ARSENAL.rig];
  const rig = new StudioRig({
    def: rigDef, set: services.set, renderer: render.renderer, tableY: ARSENAL.desk.mat.thickness,
    floorY: ARSENAL.desk.floorY, center: new THREE.Vector3(0, 60, 0),
  }).build(scene);
  rig.setDustDensity(config.get('graphics.particles'));

  // "Segurar": o viewmodel com a arma da roda (acento e nível da bancada) e a câmera parada no tapete, na altura do olho
  // do boneco; a troca de arma, de facção ou de nível no painel passa para a mão no quadro seguinte.
  const match = () => services.states.current;
  let holding = null;
  const holdSpec = () => ({ id: bench.state.id, faction: bench.state.faction, lod: bench.state.lod });
  const toggleHold = () => {
    if (holding) {
      match()?.setHold?.(null);
      holding = null;
      return false;
    }
    if (!bench.state.id) return false;
    const h = ARSENAL.hold;
    const spec = holdSpec();
    const on = match()?.setHold?.({
      ...spec,
      camera: { position: new THREE.Vector3(h.x, ARSENAL.desk.mat.thickness + HULL.standEye, h.z), yaw: h.yawDeg * DEG, pitch: h.pitchDeg * DEG },
    });
    if (!on) return false;
    holding = spec;
    match()?.setCursorMode?.(false);
    return true;
  };
  const panel = createArsenalPanel(services, {
    bench,
    onClose: () => match()?.setCursorMode?.(false),
    onHold: toggleHold,
    isHolding: () => Boolean(holding),
  });

  const offs = [
    services.events.on(EV.POSE, ({ pose }) => rig.onPose(pose)),
    config.watch('graphics.particles', (e) => rig.setDustDensity(e.value)),
    services.events.on(EV.RENDER_CONTEXT, ({ lost }) => {
      if (!lost) rig.bakeEnvironment();
    }),
  ];

  const { spawn, bounds } = ARSENAL;
  return {
    id: 'arsenal',
    scene,
    bounds: new THREE.Box3(new THREE.Vector3(...bounds.min), new THREE.Vector3(...bounds.max)),
    rig,
    bench,
    panel,
    move: { speedScale: ARSENAL.speedScale },
    post: { context: 'vitrine', exposure: rigDef.exposure },
    // A roda gira com a arma: a sombra acompanha a cada quadro.
    staticShadows: false,
    spawn: {
      position: new THREE.Vector3(spawn.x, spawn.y, spawn.z),
      yaw: spawn.yawDeg * DEG,
      pitch: spawn.pitchDeg * DEG,
    },
    frame(dt, camera) {
      rig.frame(camera, render.drawingHeight);
      bench.frame(dt);
      if (holding) {
        const spec = holdSpec();
        if (!spec.id) {
          match()?.setHold?.(null);
          holding = null;
          panel.refresh();
        } else if (spec.id !== holding.id || spec.faction !== holding.faction || spec.lod !== holding.lod) {
          holding = spec;
          match()?.setHold?.(spec);
        }
      }
    },
    get holding() {
      return Boolean(holding);
    },
    dispose() {
      holding = null;
      for (const off of offs) off();
      panel.dispose();
      rig.dispose();
      bench.dispose();
    },
  };
}

registerMap({
  id: 'arsenal',
  label: 'Bancada de armas',
  description: 'As armas de massinha geradas das receitas: fileiras no tapete, roda de modelar, plantas a lápis e o painel (Tab).',
  kind: 'teste',
  aliases: ['armas', 'oficina', 'armeiro'],
  build,
});
```

Em `src/maps/index.js`, trocar:

```
import './pista/index.js';

```

por:

```
import './pista/index.js';
import './arsenal/index.js';

```

- [ ] **Passo 8: Recursos compartilhados fora do dispose das cenas; câmera estacionada**

Em `src/render/dispose.js`, trocar:

```
// para não vazar memória (verificável em renderer.info.memory).

```

por:

```
// para não vazar memória (verificável em renderer.info.memory).
// Recursos com `userData.shared` são de um serviço que os empresta a várias cenas (as malhas e os materiais das armas,
// src/weapons/model/weaponLibrary.js): só o dono os libera.

```

Em `src/render/dispose.js`, trocar:

```
export function disposeMaterial(material, seen = new Set()) {
  if (!material || seen.has(material)) return;
  seen.add(material);
```

por:

```
export function disposeMaterial(material, seen = new Set()) {
  if (!material || seen.has(material) || material.userData?.shared) return;
  seen.add(material);
```

Em `src/render/dispose.js`, trocar:

```
      seen.add(obj.geometry);
      obj.geometry.dispose();
    }
```

por:

```
      seen.add(obj.geometry);
      if (!obj.geometry.userData?.shared) obj.geometry.dispose();
    }
```

Em `src/player/freeCamera.js`, trocar:

```
// (sv_accelerate/sv_friction), simulado a 64 Hz e interpolado no render. O olhar é aplicado por quadro.

```

por:

```
// (sv_accelerate/sv_friction), simulado a 64 Hz e interpolado no render. O olhar é aplicado por quadro.
// Estacionada (`parked`, o "Segurar" da bancada de armas): o olhar continua, a posição não sai do lugar.

```

Em `src/player/freeCamera.js`, trocar:

```
    this.speedScale = speedScale;
    this.stats = { distance: 0, topSpeed: 0, ticks: 0 };
```

por:

```
    this.speedScale = speedScale;
    this.parked = false;
    this.stats = { distance: 0, topSpeed: 0, ticks: 0 };
```

Em `src/player/freeCamera.js`, trocar:

```
    this.prevPos.copy(this.pos);
    const cp = Math.cos(this.pitch);
```

por:

```
    this.prevPos.copy(this.pos);
    if (this.parked) {
      this.vel.set(0, 0, 0);
      this.stats.ticks++;
      return;
    }
    const cp = Math.cos(this.pitch);
```

- [ ] **Passo 9: Os comandos de console**

```js file=src/debug/weaponCommands.js
// Comandos do console da Fase 4.1 (docs/phases/phase-4.md, seção 4.1, "Console e dados"): o viewmodel como no CS
// (viewmodel_fov, viewmodel_offset_x/y/z, viewmodel_presetpos, r_viewmodel), a braçadeira de teste (cl_bracadeira), a
// bancada de armas (arsenal, arma <id>), a lista das receitas geradas (armas) e o ajuste ao vivo da posição de cada
// categoria na mão (viewmodel_ajuste, para afinar src/data/viewmodel.js). Falam com a mesma config, a mesma biblioteca
// de armas e o mesmo viewmodel que o jogo usa.

import { EV } from '../core/events.js';
import { VIEWMODEL } from '../data/viewmodel.js';
import { WEAPONS, resolveWeaponId } from '../data/weapons.js';
import { SELECT } from '../player/moveCmd.js';
import { applyViewmodelPreset, currentViewmodelPreset } from '../weapons/viewmodel/placement.js';
import { onOff } from './consoleArgs.js';

const SLOT_SELECT = Object.freeze({ primary: SELECT.SLOT1, secondary: SELECT.SLOT2, melee: SELECT.SLOT3 });
const ARMBAND_ARGS = Object.freeze({ tr: 'tr', ct: 'ct', 0: 'off', off: 'off', nenhum: 'off' });

const num = (v, what) => {
  const n = Number(String(v).replace(',', '.'));
  if (!Number.isFinite(n)) throw new Error(`${what} precisa ser um número`);
  return n;
};

export function registerWeaponCommands(con, s, { goState, matchState }) {
  const reg = (def) => con.register(def);
  const cfg = s.config;

  /** Variável numérica da config no formato do CS: sem argumento mostra, com argumento ajusta (no limite do esquema). */
  const cvar = (name, key, help) => reg({
    name,
    usage: `[${cfg.spec(key).min} a ${cfg.spec(key).max}]`,
    help,
    run: ([v]) => {
      if (v !== undefined) cfg.set(key, num(v, name));
      return `${name} ${cfg.get(key)}`;
    },
  });
  cvar('viewmodel_fov', 'viewmodel.fov', 'campo de visão da arma na mão (horizontal em 4:3, como no CS; padrão 60)');
  cvar('viewmodel_offset_x', 'viewmodel.offsetX', 'arma na mão para a direita (+) ou a esquerda (−)');
  cvar('viewmodel_offset_y', 'viewmodel.offsetY', 'arma na mão para a frente (+) ou para trás (−)');
  cvar('viewmodel_offset_z', 'viewmodel.offsetZ', 'arma na mão para cima (+) ou para baixo (−)');
  reg({
    name: 'viewmodel_presetpos', usage: '[1|2|3]', help: 'posições prontas do CS: 1 Mesa, 2 Sofá, 3 Clássica',
    complete: () => Object.keys(VIEWMODEL.presets),
    run: ([id]) => {
      if (id === undefined) {
        const cur = currentViewmodelPreset(cfg);
        return cur ? `viewmodel_presetpos ${cur} (${VIEWMODEL.presets[cur].label})` : 'viewmodel_presetpos: ajustada à mão';
      }
      const p = applyViewmodelPreset(cfg, id);
      return `viewmodel_presetpos ${id} (${p.label}): fov ${p.fov}, offset ${p.x} ${p.y} ${p.z}`;
    },
  });
  reg({
    name: 'r_viewmodel', usage: '[0|1]', help: 'mostra ou esconde a arma na mão em primeira pessoa',
    run: ([v]) => `r_viewmodel ${cfg.set('debug.viewmodel', onOff(v, cfg.get('debug.viewmodel'))) ? 1 : 0}`,
  });
  reg({
    name: 'cl_bracadeira', usage: '[tr|ct|0]', help: 'braçadeira de teste do time no antebraço (e o acento das armas dos dois lados)',
    complete: () => ['tr', 'ct', '0'],
    run: ([v]) => {
      if (v !== undefined) {
        const value = ARMBAND_ARGS[String(v).toLowerCase()];
        if (!value) throw new Error('uso: cl_bracadeira tr|ct|0');
        cfg.set('debug.armband', value);
      }
      const cur = cfg.get('debug.armband');
      return `cl_bracadeira ${cur === 'off' ? '0 (sem time)' : cur}`;
    },
  });

  reg({
    name: 'arsenal', aliases: ['bancada'], help: 'abre a bancada de armas (as armas de massinha das receitas, Tab para o painel)',
    run: () => {
      goState('match', { map: 'arsenal', mode: 'livre' });
      return 'montando a bancada de armas…';
    },
  });

  reg({
    name: 'arma', usage: '<id>', help: 'na bancada, põe a arma na roda; nos mapas de andar, dá a arma e põe na mão',
    complete: () => s.weaponModels.ids,
    run: ([name]) => {
      const ids = s.weaponModels.ids;
      if (!name) throw new Error(`qual arma? (${ids.join(', ')})`);
      const id = resolveWeaponId(name) ?? name;
      if (!s.weaponModels.has(id)) throw new Error(`${name} ainda não tem receita de massinha (tem: ${ids.join(', ')})`);
      const m = matchState();
      if (m?.map?.bench) {
        m.map.bench.select(id);
        return `na roda: ${WEAPONS[id]?.name ?? id}`;
      }
      const p = m?.player;
      if (!p?.hands) throw new Error('abra a bancada (arsenal) ou um mapa de andar (sala de testes, pista)');
      const loadout = s.localLoadout;
      const slot = WEAPONS[id].slot;
      if (loadout[slot] !== id) {
        const res = loadout.give(id, { ignoreTeam: true });
        if (!res.ok) throw new Error(res.reason);
        s.events.emit(EV.LOADOUT, { owner: 'local', loadout: loadout.toJSON(), received: { kind: 'weapon', id, slot: res.slot } });
      }
      p.pendingSelect = SLOT_SELECT[slot];
      return `na mão: ${WEAPONS[id].name}`;
    },
  });

  reg({
    name: 'armas', help: 'receitas de massinha: estado, triângulos e tempo de geração por nível; e as mãos',
    run: () => {
      const head = `${'arma'.padEnd(8)}${'nível'.padEnd(7)}${'estado'.padEnd(9)}${'triângulos'.padStart(11)}${'ms'.padStart(7)}${'grupos'.padStart(8)}`;
      const rows = s.weaponModels.report().map((r) =>
        `${r.id.padEnd(8)}${r.lod.padEnd(7)}${r.state.padEnd(9)}${r.triangles.toLocaleString('pt-BR').padStart(11)}${String(r.ms).padStart(7)}${String(r.groups).padStart(8)}`);
      const hands = s.handModels.report();
      return [head, ...rows, `mãos: ${hands.state} · ${hands.triangles.toLocaleString('pt-BR')} triângulos por braço · ${hands.ms} ms`].join('\n');
    },
  });

  reg({
    name: 'viewmodel_ajuste',
    usage: '[pos x y z | ang arfagem guinada rolagem | cotovelo direita|esquerda x y z | mao direita|esquerda x y z rx ry rz | zerar]',
    help: 'afina ao vivo a posição da categoria (linha para src/data/viewmodel.js) ou a âncora de uma mão (linha para a receita)',
    complete: () => ['pos', 'ang', 'cotovelo', 'mao', 'zerar'],
    run: ([what, ...args]) => {
      const vm = matchState()?.viewmodel;
      const cat = vm?.category;
      if (!cat) throw new Error('segure uma arma com receita em primeira pessoa primeiro');
      if (what === 'mao') {
        const [side, ...v] = args;
        if ((side !== 'direita' && side !== 'esquerda') || (v.length !== 3 && v.length !== 6)) {
          throw new Error('uso: viewmodel_ajuste mao direita|esquerda x y z [rx ry rz] (rad, Euler XYZ da receita)');
        }
        const n = v.map((a) => num(a, 'mao'));
        return vm.setAnchorTune(side, n.length === 6 ? { pos: n.slice(0, 3), rot: n.slice(3) } : { pos: n });
      }
      if (what === 'zerar') vm.clearTune(cat);
      else if (what === 'pos' || what === 'ang') {
        if (args.length !== 3) throw new Error(`uso: viewmodel_ajuste ${what} <3 números>`);
        const v = args.map((a) => num(a, what));
        vm.setTune(cat, what === 'pos' ? { pos: v } : { angles: v });
      } else if (what === 'cotovelo') {
        const [side, ...xyz] = args;
        if (side !== 'direita' && side !== 'esquerda') throw new Error('uso: viewmodel_ajuste cotovelo direita|esquerda x y z');
        if (xyz.length !== 3) throw new Error('uso: viewmodel_ajuste cotovelo direita|esquerda x y z');
        vm.setTune(cat, { elbows: { [side]: xyz.map((a) => num(a, 'cotovelo')) } });
      } else if (what !== undefined) {
        throw new Error('uso: viewmodel_ajuste [pos x y z | ang arfagem guinada rolagem | cotovelo direita|esquerda x y z | mao direita|esquerda x y z rx ry rz | zerar]');
      }
      return vm.tuneLine(cat);
    },
  });
}
```

Em `src/debug/commands.js`, trocar:

```
import { registerVitalsCommands } from './vitalsCommands.js';
import { onOff } from './consoleArgs.js';
```

por:

```
import { registerVitalsCommands } from './vitalsCommands.js';
import { registerWeaponCommands } from './weaponCommands.js';
import { onOff } from './consoleArgs.js';
```

Em `src/debug/commands.js`, trocar:

```
  registerStationCommands(con, { matchState });
}
```

por:

```
  registerStationCommands(con, { matchState });
  // Armas de massinha (4.1): viewmodel como no CS, braçadeira de teste, bancada de armas, receitas geradas.
  registerWeaponCommands(con, s, { goState, matchState });
}
```

- [ ] **Passo 10: O viewmodel na partida e os serviços**

Em `src/modes/matchState.js`, trocar:

```
// jogador (o boneco de referência com squash & stretch, visível em terceira pessoa e no noclip), as pegadas nas peças
// de massinha que o mapa declara (`printSurfaces`), o monitor do movimento do aceite da Fase 3 (cl_monitor) e o resumo
// que vai para a tela de resultado.

```

por:

```
// jogador (o boneco de referência com squash & stretch, visível em terceira pessoa e no noclip), as pegadas nas peças
// de massinha que o mapa declara (`printSurfaces`), o monitor do movimento do aceite da Fase 3 (cl_monitor), a arma na
// mão em primeira pessoa (viewmodel, Fase 4.1; o "Segurar" da bancada de armas estaciona a câmera livre) e o resumo que
// vai para a tela de resultado.

```

Em `src/modes/matchState.js`, trocar:

```
import { PrintSystem } from '../clay/prints/printSystem.js';
import { itemName, zoomLevels } from '../player/hands.js';
```

por:

```
import { PrintSystem } from '../clay/prints/printSystem.js';
import { Viewmodel } from '../weapons/viewmodel/viewmodel.js';
import { viewmodelVisible } from '../weapons/viewmodel/placement.js';
import { itemName, zoomLevels } from '../player/hands.js';
```

Em `src/modes/matchState.js`, trocar:

```
    this.prints = null; // pegadas na massinha (subfase 3.5), nos mapas com `printSurfaces`
    this.physicsDebug = null;
```

por:

```
    this.prints = null; // pegadas na massinha (subfase 3.5), nos mapas com `printSurfaces`
    this.viewmodel = null; // arma na mão em primeira pessoa (Fase 4.1)
    this.hold = null; // "Segurar" da bancada de armas: {id, faction, lod} (câmera livre estacionada)
    this._vm = { item: null, visible: false, faction: null, lod: 'perto' }; // pedido do viewmodel neste quadro
    this.physicsDebug = null;
```

Em `src/modes/matchState.js`, trocar:

```
    s.render.setView(this.map.scene, this.camera, { staticShadows: this.map.staticShadows ?? false });
    // Contexto do pós (jogo, vitrine...) e exposição da montagem de luz do mapa.
```

por:

```
    s.render.setView(this.map.scene, this.camera, { staticShadows: this.map.staticShadows ?? false });
    // Arma na mão: camada própria com as luzes do mapa copiadas; o mundo de colisão tapa a luz. As mãos e as armas do
    // inventário começam a ser geradas já (a troca não espera).
    this.viewmodel = new Viewmodel({
      render: s.render, weapons: s.weaponModels, hands: s.handModels, config: s.config, events: s.events, log: s.log,
    });
    this.viewmodel.attach(this.map.scene, this.map.collision ?? null);
    s.handModels.geometries().catch((err) => s.log?.error('mãos de massinha:', err));
    this.#preloadWeapons();
    // Contexto do pós (jogo, vitrine...) e exposição da montagem de luz do mapa.
```

Em `src/modes/matchState.js`, trocar:

```
      this.subs.on(s.events, EV.LOADOUT, ({ owner, received }) => {
        if (owner === 'local') this.player?.onLoadout(received);
      });
```

por:

```
      this.subs.on(s.events, EV.LOADOUT, ({ owner, received }) => {
        if (owner !== 'local') return;
        this.player?.onLoadout(received);
        this.#preloadWeapons();
      });
```

Em `src/modes/matchState.js`, trocar:

```

  /** Etiqueta "na mão" do HUD de teste: item, velocidade no modo atual e nível da luneta. */
```

por:

```

  /** Gera (sem esperar) as malhas "perto" das armas do inventário local que têm receita. */
  #preloadWeapons() {
    const l = this.s.localLoadout;
    this.s.weaponModels.preload([l.primary, l.secondary, l.melee].filter(Boolean), 'perto');
  }

  /**
   * "Segurar" da bancada de armas (mapas sem colisão): a câmera livre para no ponto dado (o olhar continua) e o
   * viewmodel mostra a arma escolhida, com o acento e o nível da bancada; null solta. Devolve se está segurando.
   * @param {{id:string, faction?:string|null, lod?:string, camera?:{position:import('three').Vector3, yaw:number, pitch:number}}|null} spec
   */
  setHold(spec) {
    const p = this.player;
    if (!(p instanceof FreeCamera)) return false;
    const was = this.hold;
    this.hold = spec ? { id: spec.id, faction: spec.faction ?? null, lod: spec.lod ?? 'perto' } : null;
    p.parked = Boolean(this.hold);
    if (spec?.camera && !was) p.teleport(spec.camera.position, spec.camera.yaw, spec.camera.pitch);
    return Boolean(this.hold);
  }

  /** O que o viewmodel mostra neste quadro (placement.js decide quando aparece). */
  #viewmodelState() {
    const s = this.s;
    const vm = this._vm;
    const enabled = s.config.get('debug.viewmodel');
    const p = this.player;
    if (p instanceof PlayerPawn) {
      vm.item = p.hands.item;
      vm.faction = null;
      vm.lod = 'perto';
      vm.visible = viewmodelVisible({
        enabled, firstPerson: !p.thirdPerson, alive: p.vitals.alive, noclip: s.cheats.noclip, zoomed: p.hands.zoom !== 0,
        item: vm.item, hasRecipe: (id) => s.weaponModels.has(id),
      });
    } else {
      vm.item = this.hold?.id ?? null;
      vm.faction = this.hold?.faction ?? null;
      vm.lod = this.hold?.lod ?? 'perto';
      vm.visible = Boolean(enabled && this.hold);
    }
    return vm;
  }

  /** Etiqueta "na mão" do HUD de teste: item, velocidade no modo atual e nível da luneta. */
```

Em `src/modes/matchState.js`, trocar:

```
    this.player.updateCamera(this.camera, a);
    this.body?.update(this.player, a);
```

por:

```
    this.player.updateCamera(this.camera, a);
    this.viewmodel?.frame(this.camera, dt, this.#viewmodelState());
    this.body?.update(this.player, a);
```

Em `src/modes/matchState.js`, trocar:

```
    this.prints?.dispose();
    this.physicsDebug?.dispose();
```

por:

```
    this.prints?.dispose();
    this.viewmodel?.dispose();
    this.physicsDebug?.dispose();
```

Em `src/modes/matchState.js`, trocar:

```
    this.prints = null;
    this.physicsDebug = null;
```

por:

```
    this.prints = null;
    this.viewmodel = null;
    this.hold = null;
    this.physicsDebug = null;
```

Em `src/main.js`, trocar:

```
import { SdfMesher } from './clay/sdf/sdfMesher.js';
import { InputManager } from './input/inputManager.js';
```

por:

```
import { SdfMesher } from './clay/sdf/sdfMesher.js';
import { WeaponLibrary } from './weapons/model/weaponLibrary.js';
import { HandLibrary } from './characters/hands/handLibrary.js';
import { InputManager } from './input/inputManager.js';
```

Em `src/main.js`, trocar:

```
  const sdf = new SdfMesher({ store, log });
  config.watch('graphics.anisotropy', () => {
```

por:

```
  const sdf = new SdfMesher({ store, log });
  // Armas de massinha: malhas por (arma, nível) e materiais por (arma, facção), compartilhadas entre as cenas.
  const weaponModels = new WeaponLibrary({ sdf, log, events });
  // Mãos de massinha de 4 dedos: a malha e a braçadeira geradas uma vez, os dois lados com os pesos do skinning.
  const handModels = new HandLibrary({ sdf, log });
  config.watch('graphics.anisotropy', () => {
```

Em `src/main.js`, trocar:

```
  const services = {
    events, log, store, config, render, clay, set, sdf, quality, input, rebinder, loop, states, rng, cheats, roster,
    localLoadout, sv, focusNav, toasts, uiRoot, debugRoot, touchLayer,
  };
```

por:

```
  const services = {
    events, log, store, config, render, clay, set, sdf, weaponModels, handModels, quality, input, rebinder, loop, states, rng, cheats,
    roster, localLoadout, sv, focusNav, toasts, uiRoot, debugRoot, touchLayer,
  };
```

- [ ] **Passo 11: O grafo de módulos carrega e a suíte passa**

Run: `node --input-type=module -e "await import('./src/modes/matchState.js'); await import('./src/maps/arsenal/index.js'); await import('./src/debug/commands.js')"`
Expected: PASS
Run: `npm test`
Expected: PASS — 326 testes passando.

- [ ] **Passo final: Commit** (só com o pedido do usuário)

```bash
git add src/maps src/clay/set src/data/arsenal.js src/debug src/render/dispose.js src/player/freeCamera.js src/modes/matchState.js src/main.js
git commit -m "MASSACRE 4.1: bancada de armas (mapa arsenal), viewmodel na partida e comandos de console" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Tarefa 6: O Blender como editor da receita

**Files:**
- Create: `tools/blender/previa.mjs`, `tools/blender.mjs`, `tools/blender/massacre/__init__.py`, `tools/blender/massacre/receita.py`, `tools/blender/massacre/eixos.py`, `tools/blender/massacre/importar.py`, `tools/blender/massacre/exportar.py`, `tools/blender/massacre/previa.py`, `tools/blender/massacre/conferir.py`, `tools/blender/massacre_armas.py`, `tests/blenderPrevia.test.js`
- Modify: `package.json`, `.gitignore`

Decisão do usuário: o Blender gera a receita. `npm run blender -- <ação>` (`tools/blender.mjs`) acha o executável (`BLENDER_PATH`, `tools/blender/local.json` fora do git ou as pastas de instalação conhecidas), prepara no Node o contexto que o Blender não sabe calcular — a paleta, o acento da facção, a planta, a mão de massinha em cada pose (o rig do jogo) e, para `abrir` e `conferir`, a prévia do jogo — e roda o `tools/blender/massacre_armas.py`: `abrir` (com janela: a arma montada, vista lateral ortográfica, o painel "MASSACRE" na barra lateral com Exportar, Prévia do jogo, Conferir e Recarregar), `conferir` (sem janela: seis PNGs em `tools/blender/conferencia/<id>/`), `ida-volta` (sem janela: importa, exporta e compara byte a byte com a receita — a prova do caminho), `validar <arquivo>` (a validação do jogo; o exportador chama antes de gravar por cima da receita) e `previa <arquivo> <saída>`. No Blender: `receita.py` lê a receita e grava no formato canônico (o mesmo do formatador do jogo); `eixos.py` converte os eixos (o ponto (x, y, z) do jogo fica em (x, −z, y) no Blender; o Euler XYZ do three é a ordem 'ZYX' do mathutils; o exportador tira o Euler pelo atan2, porque as matrizes do Blender são float32); `importar.py` monta a cena (uma coleção por grupo com o pivô; `profile` em curva 2D com extrusão e bisel, `lathe` no modificador Parafuso, `tube` em curva 3D com raio por ponto, o resto em malhas; a origem das peças por pontos no centro delas, então escalar e girar acontecem no lugar; cortes em arame vermelho; âncoras com a mão desenhada na pose; a planta numa coleção que não exporta; propriedades `massacre_*` guardando a peça original); `exportar.py` faz o caminho de volta (dobra a escala nos parâmetros, devolve aos pontos a translação e a escala das peças por pontos, usa o valor guardado quando o novo é o mesmo a 5·10⁻⁵ u — sem edição, a receita volta idêntica —, cópia com Shift+D vira peça nova depois da original e objeto sem receita recusa a exportação); `previa.py` lê a prévia do jogo; `conferir.py` renderiza no Workbench a lateral com a planta, cima, frente, 3/4, as mãos e a primeira pessoa. `tools/blender/previa.mjs` gera no Node a malha que o jogo faz da receita (o mesmo SDF, nível `perto`), os braços de massinha nas âncoras (o rig do jogo com o skinning na CPU, como no viewmodel) e a câmera do viewmodel, num binário que o Python lê.

- [ ] **Passo 1: Escrever o teste da prévia** — o formato que o Python lê, sem o Blender.

```js file=tests/blenderPrevia.test.js
// Testes da prévia do jogo para o Blender (Fase 4.1; docs/phases/phase-4.md, seção 4.1, "Blender"): o formato que o
// tools/blender/massacre/previa.py lê — blocos alinhados a 4 bytes dentro do binário, contagens coerentes (3 números por
// vértice, 3 índices por triângulo, uma massa por triângulo), índices dentro dos vértices, massas dentro da lista —, um
// grupo por grupo da receita no pivô dele, um braço por âncora de mão com o pulso na âncora e a câmera do viewmodel
// olhando para a arma. Sem o Blender (o caminho dentro dele é o `npm run blender -- ida-volta|conferir`).
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, readFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import * as THREE from 'three';
import { ARMAS } from '../src/data/armas/index.js';
import { VIEWMODEL } from '../src/data/viewmodel.js';
import { HAND_ANCHOR, handSides, viewmodelVerticalFov } from '../src/weapons/viewmodel/placement.js';
import { gerarPrevia } from '../tools/blender/previa.mjs';

function malha(bin, m, comMassas, nMateriais) {
  const bloco = (b, Type) => {
    assert.equal(b.offset % 4, 0, 'bloco alinhado a 4 bytes');
    assert.ok(b.offset + b.count * Type.BYTES_PER_ELEMENT <= bin.byteLength, 'bloco dentro do binário');
    return new Type(bin, b.offset, b.count);
  };
  const pos = bloco(m.positions, Float32Array);
  const nor = bloco(m.normals, Float32Array);
  const idx = bloco(m.indices, Uint32Array);
  assert.equal(pos.length % 3, 0);
  assert.equal(nor.length, pos.length);
  assert.equal(idx.length % 3, 0);
  assert.ok(idx.length > 0);
  const nv = pos.length / 3;
  assert.ok(idx.every((i) => i < nv), 'índices dentro dos vértices');
  assert.ok(pos.every(Number.isFinite), 'posições finitas');
  for (let i = 0; i < nv; i += 97) {
    const l = Math.hypot(nor[i * 3], nor[i * 3 + 1], nor[i * 3 + 2]);
    assert.ok(Math.abs(l - 1) < 0.02, `normal unitária (${l})`);
  }
  if (comMassas) {
    const massas = bloco(m.massas, Uint8Array);
    assert.equal(massas.length, idx.length / 3, 'uma massa por triângulo');
    assert.ok(massas.every((k) => k < nMateriais), 'massas dentro da lista');
  }
  return { pos, nv };
}

for (const id of ['knife', 'glock']) {
  test(`prévia do jogo (${id}): blocos, contagens, grupos, braços nas âncoras e a câmera do viewmodel`, async () => {
    const recipe = ARMAS[id];
    const dir = mkdtempSync(join(tmpdir(), 'massacre-previa-'));
    try {
      const { json, triangulos } = await gerarPrevia(recipe, join(dir, id));
      const cab = JSON.parse(readFileSync(json, 'utf8'));
      const arquivo = readFileSync(join(dir, cab.bin));
      const bin = arquivo.buffer.slice(arquivo.byteOffset, arquivo.byteOffset + arquivo.byteLength);
      assert.equal(cab.id, id);
      assert.equal(cab.versao, 1);
      assert.ok(cab.materiais.length > 0);
      assert.deepEqual(cab.grupos.map((g) => g.nome), Object.keys(recipe.groups));
      let soma = 0;
      for (const g of cab.grupos) {
        assert.deepEqual(g.pivo, recipe.groups[g.nome].pivot ?? [0, 0, 0]);
        malha(bin, g, true, cab.materiais.length);
        soma += g.indices.count / 3;
      }
      // Um braço por âncora de mão, na pose dela, com o pulso na âncora (algum vértice a menos de um raio de dedo).
      assert.deepEqual(cab.maos.map((m) => m.lado), handSides(recipe));
      for (const m of cab.maos) {
        const anchor = recipe.anchors[HAND_ANCHOR[m.lado]];
        assert.equal(m.pose, anchor.pose);
        const { pos, nv } = malha(bin, m, false, 1);
        let perto = Infinity;
        for (let i = 0; i < nv; i++) {
          perto = Math.min(perto, Math.hypot(pos[i * 3] - anchor.pos[0], pos[i * 3 + 1] - anchor.pos[1], pos[i * 3 + 2] - anchor.pos[2]));
        }
        assert.ok(perto < 1.5, `a massa do braço passa pelo pulso (${perto.toFixed(2)} u)`);
        soma += m.indices.count / 3;
      }
      assert.equal(soma, triangulos);
      // A câmera do viewmodel: o FOV vertical do viewmodel_fov padrão e a arma na frente dela (−Z), perto.
      const c = cab.camera;
      assert.ok(Math.abs(c.fovY - viewmodelVerticalFov(VIEWMODEL.fov.default)) < 1e-9);
      assert.equal(c.near, VIEWMODEL.near);
      const q = new THREE.Quaternion(...c.quat);
      assert.ok(Math.abs(q.length() - 1) < 1e-6);
      const origem = new THREE.Vector3().sub(new THREE.Vector3(...c.pos)).applyQuaternion(q.clone().invert());
      assert.ok(origem.z < -5 && origem.z > -30, `a arma na frente da câmera (${origem.z.toFixed(2)} u)`);
    } finally {
      rmSync(dir, { recursive: true, force: true });
    }
  });
}
```

- [ ] **Passo 2: Rodar e ver falhar**

Run: `node --test tests/blenderPrevia.test.js`
Expected: FAIL — o teste não carrega (`ERR_MODULE_NOT_FOUND`: `tools/blender/previa.mjs`).

- [ ] **Passo 3: A prévia do jogo para o Blender**

```js file=tools/blender/previa.mjs
// Prévia do jogo para o Blender (Fase 4.1; docs/phases/phase-4.md, seção 4.1, "Blender"): a malha que o jogo gera de uma
// receita — o mesmo SDF, o mesmo nível de detalhe da bancada e do viewmodel (`perto`) —, os braços de massinha de
// verdade (a malha SDF da mão com o rig, pesos e poses do jogo) presos às âncoras como no viewmodel parado, e a câmera
// de primeira pessoa (viewmodel_fov e offsets padrão). O Blender mostra isso numa coleção que não exporta e o
// `conferir` renderiza a verdade, não as peças de edição.
// Saída: `<saída>.json` (cabeçalho) + `<saída>.bin` (Float32 posições e normais, Uint32 índices, Uint8 massa por
// triângulo, em blocos alinhados a 4 bytes). Tudo no referencial da arma no jogo (+X boca, +Y cima, +Z lado direito).

import { writeFileSync } from 'node:fs';
import { basename } from 'node:path';
import * as THREE from 'three';
import { SdfMesher } from '../../src/clay/sdf/sdfMesher.js';
import { PALETTE } from '../../src/data/palette.js';
import { VIEWMODEL } from '../../src/data/viewmodel.js';
import { ClayArm, buildArmGeometry, prepareArmGeometry } from '../../src/characters/hands/handRig.js';
import { buildWeaponMeshes } from '../../src/weapons/model/weaponModel.js';
import {
  HAND_ANCHOR, elbowTarget, handSides, viewCategory, viewPlacement, viewmodelVerticalFov, weaponNudge,
} from '../../src/weapons/viewmodel/placement.js';

class Blocos {
  constructor() {
    this.partes = [];
    this.bytes = 0;
  }

  /** Guarda um array tipado e devolve {offset, count}; cada bloco começa alinhado a 4 bytes. */
  add(tipado) {
    const offset = this.bytes;
    this.partes.push(Buffer.from(tipado.buffer, tipado.byteOffset, tipado.byteLength));
    this.bytes += tipado.byteLength;
    const sobra = (4 - (this.bytes % 4)) % 4;
    if (sobra) {
      this.partes.push(Buffer.alloc(sobra));
      this.bytes += sobra;
    }
    return { offset, count: tipado.length };
  }

  buffer() {
    return Buffer.concat(this.partes, this.bytes);
  }
}

/** Massa (índice em `materials`) de cada triângulo, pelos grupos contíguos da geometria. */
function massasPorTriangulo(geometry) {
  const out = new Uint8Array(geometry.index.count / 3);
  for (const g of geometry.groups) out.fill(g.materialIndex, g.start / 3, (g.start + g.count) / 3);
  return out;
}

/** Posições dos vértices depois do skinning (na CPU, a mesma conta do shader), no referencial do pai da malha. */
function posicoesSkinned(arm) {
  arm.mesh.updateMatrixWorld(true);
  const pos = arm.mesh.geometry.attributes.position;
  const out = new Float32Array(pos.count * 3);
  const v = new THREE.Vector3();
  for (let i = 0; i < pos.count; i++) {
    v.fromBufferAttribute(pos, i);
    arm.mesh.applyBoneTransform(i, v);
    out[i * 3] = v.x;
    out[i * 3 + 1] = v.y;
    out[i * 3 + 2] = v.z;
  }
  return out;
}

/**
 * Gera a prévia de uma receita (validada pelo gerador) e grava `<saida>.json` + `<saida>.bin`.
 * @param {object} recipe
 * @param {string} saida caminho sem extensão
 * @returns {Promise<{json:string, triangulos:number, ms:number}>}
 */
export async function gerarPrevia(recipe, saida) {
  const t0 = performance.now();
  const sdf = new SdfMesher({ workers: 0 });
  const blocos = new Blocos();
  try {
    const built = await buildWeaponMeshes(recipe, sdf, 'perto');
    const grupos = Object.entries(built.groups).map(([nome, g]) => ({
      nome,
      pivo: g.pivot,
      positions: blocos.add(g.geometry.attributes.position.array),
      normals: blocos.add(g.geometry.attributes.normal.array),
      indices: blocos.add(Uint32Array.from(g.geometry.index.array)),
      massas: blocos.add(massasPorTriangulo(g.geometry)),
    }));
    let triangulos = built.triangles;

    // Os braços e a câmera como no viewmodel parado (padrões do CS: viewmodel_fov 60, offsets 1, 1, −1).
    const category = viewCategory(recipe.id);
    const offset = { x: VIEWMODEL.offset.x.default, y: VIEWMODEL.offset.y.default, z: VIEWMODEL.offset.z.default };
    const place = viewPlacement(category, { offset, nudge: weaponNudge(recipe.id) });
    const inv = place.quaternion.clone().invert();
    const naArma = (p) => p.clone().sub(place.position).applyQuaternion(inv); // câmera → arma
    const maos = [];
    const sides = handSides(recipe);
    if (sides.length) {
      const fonte = await buildArmGeometry(sdf);
      for (const side of sides) {
        const anchor = recipe.anchors[HAND_ANCHOR[side]];
        const geometry = prepareArmGeometry(fonte, side);
        const arm = new ClayArm({ geometry, side, color: PALETTE.terracotta });
        arm.setPose(anchor.pose);
        const quat = new THREE.Quaternion().setFromEuler(new THREE.Euler(...(anchor.rot ?? [0, 0, 0]), 'XYZ'));
        arm.place(new THREE.Vector3(...anchor.pos), quat, naArma(elbowTarget(category, side)));
        const skinned = new THREE.BufferGeometry();
        skinned.setAttribute('position', new THREE.BufferAttribute(posicoesSkinned(arm), 3));
        skinned.setIndex(new THREE.BufferAttribute(Uint32Array.from(geometry.index.array), 1));
        skinned.computeVertexNormals();
        maos.push({
          lado: side,
          ancora: HAND_ANCHOR[side],
          pose: anchor.pose,
          positions: blocos.add(skinned.attributes.position.array),
          normals: blocos.add(skinned.attributes.normal.array),
          indices: blocos.add(skinned.index.array),
        });
        triangulos += skinned.index.count / 3;
        arm.dispose();
        geometry.dispose();
        skinned.dispose();
      }
      fonte.dispose();
    }
    for (const g of Object.values(built.groups)) g.geometry.dispose();

    const olho = new THREE.Vector3().sub(place.position).applyQuaternion(inv);
    const cabecalho = {
      id: recipe.id,
      versao: 1,
      bin: `${basename(saida)}.bin`,
      materiais: built.materials,
      corMao: PALETTE.terracotta,
      grupos,
      maos,
      // Câmera do viewmodel no referencial da arma (olha para −Z, +Y para cima); o quatérnio é [x, y, z, w].
      camera: {
        pos: olho.toArray(),
        quat: inv.toArray(),
        fovY: viewmodelVerticalFov(VIEWMODEL.fov.default),
        near: VIEWMODEL.near,
        far: VIEWMODEL.far,
      },
      triangulos,
      ms: Math.round(performance.now() - t0),
    };
    writeFileSync(`${saida}.bin`, blocos.buffer());
    writeFileSync(`${saida}.json`, JSON.stringify(cabecalho));
    return { json: `${saida}.json`, triangulos, ms: cabecalho.ms };
  } finally {
    sdf.dispose();
  }
}
```

Run: `node --test tests/blenderPrevia.test.js`
Expected: PASS

- [ ] **Passo 4: O lançador, o script do npm e o que fica fora do git**

```js file=tools/blender.mjs
// Editor de armas no Blender (Fase 4.1; docs/phases/phase-4.md, seção 4.1, "Blender"):
//
//   npm run blender -- abrir <arma>          Blender com janela, a arma montada e o painel "MASSACRE" (tecla N)
//   npm run blender -- conferir <arma|todas> renders sem janela em tools/blender/conferencia/<arma>/
//   npm run blender -- ida-volta <arma|todas> importa e exporta sem janela e compara com a receita (a prova do caminho)
//   npm run blender -- validar <arquivo.js>   a validação do jogo numa receita (o exportador chama antes de gravar)
//   npm run blender -- previa <arquivo.js> <saída>  a malha que o jogo gera de uma receita (o painel do Blender chama)
//
// Prepara o contexto que o Blender não sabe calcular sozinho — a paleta das massas, o acento da facção, a planta de
// referência, a mão de massinha em cada pose (o próprio rig do jogo, src/characters/hands/) e, para abrir e conferir,
// a prévia do jogo (tools/blender/previa.mjs: a malha que o jogo gera, com as mãos e a câmera do viewmodel) — em
// arquivos temporários.
// O executável vem de BLENDER_PATH, de tools/blender/local.json ({"blender": "caminho"}, fora do git) ou das pastas de
// instalação conhecidas.

import { spawn, spawnSync } from 'node:child_process';
import { existsSync, mkdirSync, readFileSync, readdirSync, rmSync, writeFileSync } from 'node:fs';
import { homedir, platform, tmpdir } from 'node:os';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import * as THREE from 'three';
import { gerarPrevia } from './blender/previa.mjs';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const SCRIPT = join(ROOT, 'tools', 'blender', 'massacre_armas.py');
const TMP = join(tmpdir(), 'massacre-blender');

function blenderExe() {
  const ok = (p) => p && existsSync(p);
  if (process.env.BLENDER_PATH) {
    if (ok(process.env.BLENDER_PATH)) return process.env.BLENDER_PATH;
    throw new Error(`BLENDER_PATH aponta para um arquivo que não existe: ${process.env.BLENDER_PATH}`);
  }
  const local = join(ROOT, 'tools', 'blender', 'local.json');
  if (existsSync(local)) {
    const exe = JSON.parse(readFileSync(local, 'utf8')).blender;
    if (ok(exe)) return exe;
    throw new Error(`tools/blender/local.json aponta para um arquivo que não existe: ${exe}`);
  }
  const candidatos = [];
  if (platform() === 'win32') {
    for (const base of [process.env.ProgramFiles, process.env['ProgramFiles(x86)'], 'C:\\Program Files']) {
      const dir = base && join(base, 'Blender Foundation');
      if (dir && existsSync(dir)) {
        const versoes = readdirSync(dir).filter((n) => /^Blender/i.test(n)).sort((a, b) => b.localeCompare(a, 'en', { numeric: true }));
        for (const v of versoes) candidatos.push(join(dir, v, 'blender.exe'));
      }
    }
    candidatos.push('C:\\Program Files (x86)\\Steam\\steamapps\\common\\Blender\\blender.exe');
  } else if (platform() === 'darwin') {
    candidatos.push('/Applications/Blender.app/Contents/MacOS/Blender', join(homedir(), 'Applications/Blender.app/Contents/MacOS/Blender'));
  } else {
    candidatos.push('/usr/bin/blender', '/usr/local/bin/blender', '/snap/bin/blender', join(homedir(), '.local/bin/blender'));
  }
  const achado = candidatos.find(ok);
  if (achado) return achado;
  const noPath = spawnSync('blender', ['--version'], { encoding: 'utf8' });
  if (noPath.status === 0) return 'blender';
  throw new Error('Blender não encontrado: defina BLENDER_PATH ou crie tools/blender/local.json com {"blender": "caminho do executável"}');
}

/** A mão de massinha em cada pose, no referencial da mão (pulso na origem), pelo rig do jogo. */
async function maosPorPose() {
  const { HAND_POSES } = await import('../src/data/hands.js');
  const { ClayArm, sideBones } = await import('../src/characters/hands/handRig.js');
  const out = {};
  for (const side of ['direita', 'esquerda']) {
    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute('position', new THREE.Float32BufferAttribute([0, 0, 0], 3));
    geometry.setAttribute('skinIndex', new THREE.Uint16BufferAttribute([0, 0, 0, 0], 4));
    geometry.setAttribute('skinWeight', new THREE.Float32BufferAttribute([1, 0, 0, 0], 4));
    const arm = new ClayArm({ geometry, side, color: '#C8553D' });
    const defs = sideBones(side).filter((d) => d.name !== 'antebraco');
    out[side] = {};
    for (const pose of Object.keys(HAND_POSES)) {
      arm.setPose(pose);
      arm.place(new THREE.Vector3(0, 0, 0), new THREE.Quaternion(), new THREE.Vector3(-11, 0, 0));
      arm.mesh.updateMatrixWorld(true);
      out[side][pose] = defs.map((d) => {
        const m = arm.bones[d.name].matrixWorld;
        const len = Math.hypot(d.tail[0] - d.head[0], d.tail[1] - d.head[1], d.tail[2] - d.head[2]);
        const r4 = (v) => Math.round(v * 1e4) / 1e4;
        return {
          name: d.name,
          head: new THREE.Vector3().setFromMatrixPosition(m).toArray().map(r4),
          tail: new THREE.Vector3(len, 0, 0).applyMatrix4(m).toArray().map(r4),
          radius: d.radius,
        };
      });
    }
    arm.dispose();
    geometry.dispose();
  }
  return out;
}

async function contexto(id, { comPrevia = false } = {}) {
  const { ARMAS } = await import('../src/data/armas/index.js');
  if (!ARMAS[id]) throw new Error(`arma sem receita: ${id} (tem: ${Object.keys(ARMAS).join(', ')})`);
  const { WEAPON_CLAYS, FACTION_ACCENTS } = await import('../src/data/weaponPalette.js');
  const { PALETTE } = await import('../src/data/palette.js');
  const { weaponFaction } = await import('../src/weapons/model/recipe.js');
  const refPath = join(ROOT, 'tools', 'blender', 'refs', `${id}.json`);
  const planta = existsSync(refPath) ? JSON.parse(readFileSync(refPath, 'utf8')) : null;
  const ctx = {
    id,
    raiz: ROOT,
    receita: join(ROOT, 'src', 'data', 'armas', `${id}.js`),
    faccao: weaponFaction(id),
    massas: WEAPON_CLAYS,
    acentos: FACTION_ACCENTS,
    corMao: PALETTE.terracotta,
    maos: await maosPorPose(),
    planta: planta && { points: planta.points, holes: planta.holes ?? [] },
    pasta: join(ROOT, 'tools', 'blender', 'conferencia', id),
    node: process.execPath,
    ferramenta: fileURLToPath(import.meta.url),
    previa: null,
  };
  mkdirSync(TMP, { recursive: true });
  if (comPrevia) ctx.previa = (await gerarPrevia(ARMAS[id], join(TMP, `${id}-previa`))).json;
  const arquivo = join(TMP, `${id}-contexto.json`);
  writeFileSync(arquivo, JSON.stringify(ctx));
  return arquivo;
}

function rodarSemJanela(args) {
  const res = spawnSync(blenderExe(), ['--background', '--factory-startup', '--python-exit-code', '1', '--python', SCRIPT, '--', ...args], {
    encoding: 'utf8', maxBuffer: 64 * 1024 * 1024,
  });
  if (res.status !== 0) {
    throw new Error(`o Blender falhou (código ${res.status}):\n${(res.stdout ?? '').split('\n').slice(-25).join('\n')}\n${res.stderr ?? ''}`);
  }
  return res.stdout;
}

/** A receita de um arquivo (sem o cache de módulos: o mesmo caminho pode ter mudado). */
async function lerReceita(arquivo) {
  const url = pathToFileURL(resolve(arquivo));
  url.searchParams.set('v', String(Date.now()));
  return (await import(url.href)).default;
}

async function validar(arquivo) {
  const { validateRecipe } = await import('../src/weapons/model/recipe.js');
  const recipe = validateRecipe(await lerReceita(arquivo));
  return `receita de ${recipe.id} válida (${recipe.parts.length} peças)`;
}

async function previa(arquivo, saida) {
  const { json, triangulos, ms } = await gerarPrevia(await lerReceita(arquivo), resolve(saida));
  return `MASSACRE-PREVIA ${json} (${triangulos} triângulos, ${ms} ms)`;
}

async function idaVolta(id) {
  const ctx = await contexto(id);
  const saida = join(TMP, `${id}-ida-volta.js`);
  rmSync(saida, { force: true });
  rodarSemJanela(['ida-volta', ctx, saida]);
  await validar(saida);
  const original = readFileSync(join(ROOT, 'src', 'data', 'armas', `${id}.js`), 'utf8');
  const volta = readFileSync(saida, 'utf8');
  if (original === volta) return `${id}: ida e volta idêntica (${original.length} bytes)`;
  const a = original.split('\n');
  const b = volta.split('\n');
  const i = a.findIndex((linha, k) => linha !== b[k]);
  throw new Error(`${id}: a volta difere na linha ${i + 1}:\n  receita: ${a[i]?.slice(0, 240)}\n  volta:   ${b[i]?.slice(0, 240)}`);
}

async function conferir(id) {
  const ctx = await contexto(id, { comPrevia: true });
  const out = rodarSemJanela(['conferir', ctx]);
  const linha = out.split('\n').find((l) => l.startsWith('MASSACRE-CONFERIR '));
  const arquivos = linha ? JSON.parse(linha.slice('MASSACRE-CONFERIR '.length)) : [];
  return `${id}: ${arquivos.length} vistas em ${join('tools', 'blender', 'conferencia', id)}`;
}

async function abrir(id) {
  const ctx = await contexto(id, { comPrevia: true });
  const filho = spawn(blenderExe(), ['--python', SCRIPT, '--', 'abrir', ctx], { detached: true, stdio: 'ignore' });
  filho.unref();
  return `Blender aberto com ${id} (painel "MASSACRE" na barra lateral da vista 3D, tecla N)`;
}

async function principal() {
  const [acao, alvo, extra] = process.argv.slice(2);
  const { ARMAS } = await import('../src/data/armas/index.js');
  const ids = alvo === 'todas' ? Object.keys(ARMAS) : [alvo];
  const acoes = { abrir, conferir, 'ida-volta': idaVolta };
  if (acao === 'validar') {
    if (!alvo) throw new Error('uso: npm run blender -- validar <arquivo.js>');
    console.log(await validar(alvo));
    return;
  }
  if (acao === 'previa') {
    if (!alvo || !extra) throw new Error('uso: npm run blender -- previa <arquivo.js> <saída sem extensão>');
    console.log(await previa(alvo, extra));
    return;
  }
  if (!acoes[acao] || !alvo) {
    throw new Error('uso: npm run blender -- <abrir|conferir|ida-volta> <arma|todas>, validar <arquivo.js> ou previa <arquivo.js> <saída>');
  }
  if (acao === 'abrir' && ids.length > 1) throw new Error('abrir é uma arma de cada vez');
  let falhas = 0;
  for (const id of ids) {
    try {
      console.log(await acoes[acao](id));
    } catch (err) {
      falhas++;
      console.error(err.message ?? err);
    }
  }
  if (falhas) process.exitCode = 1;
}

principal().catch((err) => {
  console.error(err.message ?? err);
  process.exitCode = 1;
});
```

Em `package.json`, trocar:

```
    "moodboard": "node tools/moodboard.mjs",
    "aceite:fase3": "node tools/phase3-acceptance.mjs",
```

por:

```
    "moodboard": "node tools/moodboard.mjs",
    "blender": "node tools/blender.mjs",
    "aceite:fase3": "node tools/phase3-acceptance.mjs",
```

Em `.gitignore`, trocar:

```
Thumbs.db

```

por:

```
Thumbs.db
# Editor de armas no Blender (Fase 4.1): o caminho do executável é da máquina; as conferências são geradas
tools/blender/local.json
tools/blender/conferencia/
__pycache__/

```

- [ ] **Passo 5: O pacote do Blender**

```python file=tools/blender/massacre/__init__.py
"""Pacote do editor de armas no Blender (Fase 4.1): receita (ler/gravar no formato canônico), eixos (jogo ↔ Blender),
importar, exportar, previa (a malha que o jogo gera, lida do tools/blender/previa.mjs) e conferir. O ponto de entrada é
tools/blender/massacre_armas.py.
"""
```

```python file=tools/blender/massacre/receita.py
"""Receita de arma de massinha (src/data/armas/<id>.js) do lado do Blender (Fase 4.1; docs/phases/phase-4.md,
seção 4.1, "Receita" e "Blender").

Ler: o corpo é JSON puro depois de `export default` (o primeiro `{`), com o comentário de cabeçalho em cima.
Gravar: o formato canônico, byte a byte igual ao dos geradores (números arredondados a 4 casas como o Math.round do
JavaScript e escritos como o String() do JavaScript; a ordem das chaves das peças fixa). Assim a ida e volta sem
edição devolve o mesmo arquivo — a prova do caminho do Blender.
"""

import json
import math

PART_KEYS = (
    'name', 'group', 'mat', 'shape', 'op', 'thin', 'pos', 'rot', 'size', 'r', 'h', 'round', 'a', 'b', 'ra', 'rb',
    'radii', 'R', 'r1', 'r2', 'corner', 'closed', 'points', 'k', 'crease',
)


def ler(caminho):
    """Lê a receita e o cabeçalho (as linhas de comentário antes de `export default`, sem o `// `)."""
    with open(caminho, encoding='utf-8') as f:
        texto = f.read()
    i = texto.find('export default')
    if i < 0:
        raise ValueError(f'{caminho}: falta o `export default`')
    j = texto.find('{', i)
    if j < 0:
        raise ValueError(f'{caminho}: falta o `{{` do corpo')
    receita, _ = json.JSONDecoder().raw_decode(texto[j:])
    cabecalho = [linha[3:] if linha.startswith('// ') else linha[2:] for linha in texto[:i].splitlines() if linha.startswith('//')]
    return receita, cabecalho


def arredonda(v):
    """Math.round(v * 1e4) / 1e4 do JavaScript (meio para cima, também nos negativos)."""
    return math.floor(v * 1e4 + 0.5) / 1e4


def numero(v):
    """Número como o String() do JavaScript depois de arredondar: inteiros sem `.0`, sem `-0`."""
    r = arredonda(float(v))
    if r == 0:
        return '0'
    if r == int(r) and abs(r) < 1e15:
        return str(int(r))
    return repr(r)


def valor(v):
    """Um valor no formato canônico (o `value()` dos geradores)."""
    if isinstance(v, bool):
        return 'true' if v else 'false'
    if v is None:
        return 'null'
    if isinstance(v, (int, float)):
        return numero(v)
    if isinstance(v, (list, tuple)):
        return '[' + ', '.join(valor(x) for x in v) + ']'
    if isinstance(v, dict):
        return '{ ' + ', '.join(f'{json.dumps(k, ensure_ascii=False)}: {valor(x)}' for k, x in v.items()) + ' }'
    return json.dumps(v, ensure_ascii=False)


def formatar(receita, cabecalho):
    """A receita inteira no formato canônico (o `formatRecipe()` dos geradores)."""
    linhas = [f'// {linha}' for linha in cabecalho]
    linhas.append('export default {')
    linhas.append(f'  "id": {json.dumps(receita["id"], ensure_ascii=False)},')
    linhas.append(f'  "version": {receita["version"]},')
    linhas.append(f'  "refs": {valor(receita["refs"])},')
    linhas.append(f'  "materials": {valor(receita["materials"])},')
    if receita.get('soft'):
        linhas.append(f'  "soft": {valor(receita["soft"])},')
    linhas.append('  "groups": {')
    linhas.append(',\n'.join(f'    {json.dumps(k)}: {valor(g)}' for k, g in receita['groups'].items()))
    linhas.append('  },')
    linhas.append('  "anchors": {')
    linhas.append(',\n'.join(f'    {json.dumps(k)}: {valor(a)}' for k, a in receita['anchors'].items()))
    linhas.append('  },')
    linhas.append('  "parts": [')
    pecas = []
    for p in receita['parts']:
        chaves = [k for k in PART_KEYS if k in p] + [k for k in p if k not in PART_KEYS]
        pecas.append('    { ' + ', '.join(f'{json.dumps(k)}: {valor(p[k])}' for k in chaves) + ' }')
    linhas.append(',\n'.join(pecas))
    linhas.append('  ]')
    linhas.append('};')
    return '\n'.join(linhas) + '\n'


def gravar(caminho, receita, cabecalho):
    with open(caminho, 'w', encoding='utf-8', newline='\n') as f:
        f.write(formatar(receita, cabecalho))
```

```python file=tools/blender/massacre/eixos.py
"""Eixos entre o jogo e o Blender (Fase 4.1; docs/phases/phase-4.md, "Referencial de cada arma").

Jogo (three.js): +X boca, +Y cima, +Z lado direito. Blender: Z para cima. Um ponto (x, y, z) do jogo fica em
(x, −z, y) no Blender; o exportador faz o caminho de volta: (x, y, z) do Blender → (x, z, −y) do jogo.
Cada peça guarda a geometria no referencial dela no jogo; o objeto do Blender recebe a matriz C · T(pos) · R(rot).
Os giros são o Euler 'XYZ' do three.js (matriz Rx · Ry · Rz), que no mathutils é a ordem 'ZYX'.
"""

import math

from mathutils import Euler, Matrix, Vector

# Jogo → Blender (e a volta).
C = Matrix(((1, 0, 0, 0), (0, 0, -1, 0), (0, 1, 0, 0), (0, 0, 0, 1)))
C_INV = C.inverted()


def rot_jogo(rot):
    """Matriz 3×3 do Euler XYZ do three.js ([x, y, z] em rad)."""
    a, b, c = rot if rot else (0.0, 0.0, 0.0)
    return Euler((a, b, c), 'ZYX').to_matrix()


def euler_jogo(m3):
    """Euler XYZ do three.js de uma matriz de rotação (o setFromRotationMatrix dele, com o mesmo corte perto de ±90°).
    O Y sai do atan2(sen, |cos|) em vez do asin(m13): o mesmo ângulo, sem perder precisão perto de ±90° com as matrizes
    float32 do Blender (asin(1 − 6·10⁻⁸) já erra 3·10⁻⁴ rad)."""
    m11, m12, m13 = m3[0][0], m3[0][1], m3[0][2]
    m22, m23 = m3[1][1], m3[1][2]
    m32, m33 = m3[2][1], m3[2][2]
    y = math.atan2(m13, math.hypot(m11, m12))
    if abs(m13) < 0.9999999:
        return [math.atan2(-m23, m33), y, math.atan2(-m12, m11)]
    return [math.atan2(m32, m22), y, 0.0]


def matriz_blender(pos=None, rot=None):
    """matrix_world do Blender de uma peça/âncora do jogo."""
    p = Vector(pos) if pos else Vector((0.0, 0.0, 0.0))
    return C @ Matrix.Translation(p) @ rot_jogo(rot).to_4x4()


def para_jogo(matrix_world):
    """Posição, rotação (3×3) e escala no referencial do jogo de um objeto do Blender."""
    loc, quat, escala = (C_INV @ matrix_world).decompose()
    return loc, quat.to_matrix(), escala


def ponto_blender(p):
    """Ponto do jogo no Blender (x, −z, y)."""
    return Vector((p[0], -p[2], p[1]))


def ponto_jogo(v):
    """Ponto do Blender no jogo (x, z, −y)."""
    return [v[0], v[2], -v[1]]


def mesma_rotacao(m3, rot, tol=1e-5):
    """A rotação do objeto ainda é a do Euler guardado (a volta não inventa um Euler equivalente com outros números)."""
    r = rot_jogo(rot)
    return all(abs(m3[i][j] - r[i][j]) <= tol for i in range(3) for j in range(3))
```

```python file=tools/blender/massacre/importar.py
"""Importar: a receita de uma arma vira a cena do Blender (Fase 4.1; docs/phases/phase-4.md, seção 4.1, "Blender").

- uma coleção por grupo animável (`grupo:<nome>`), com o pivô como Empty (`pivo:<nome>`);
- `profile` vira curva 2D preenchida com extrusão e bisel; `lathe`, o meridiano com o modificador Parafuso em volta
  do X; `tube`, curva 3D com bisel e o raio em cada ponto; as outras formas, malhas geradas pelos parâmetros;
- cortes (`op: subtract`) em arame vermelho; âncoras como Empties (as de mão com a mão de massinha desenhada na pose
  da âncora, calculada pelo rig do jogo); a planta de referência numa coleção que não exporta;
- cada objeto guarda o que o jogo precisa em propriedades `massacre_*` (a peça original em JSON, a ordem): o
  exportador usa o guardado quando a geometria não mudou, então a ida e volta devolve os mesmos números.
Toda geometria fica no referencial da peça no jogo; a matriz do objeto é C · T(pos) · R(rot) · T(centro) (eixos.py):
nas peças definidas por pontos (perfil, torno, tubo, cápsula, cone arredondado) a origem do objeto fica no centro da
peça, então girar e escalar acontece no lugar, como quem modela espera.
"""

import json
import math

import bmesh
import bpy
from mathutils import Matrix, Vector

from . import eixos

COR_CORTE = (0.92, 0.12, 0.1, 1.0)
COR_PLANTA = '#F28F3B'
SEGMENTOS = 32


def rgba(hexcor, alfa=1.0):
    """'#RRGGBB' (sRGB) → cor linear do Blender."""
    h = hexcor.lstrip('#')
    def lin(c):
        c /= 255.0
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return (lin(int(h[0:2], 16)), lin(int(h[2:4], 16)), lin(int(h[4:6], 16)), alfa)


def limpar_cena():
    """Cena dedicada à arma: tira objetos, coleções e o que ficou órfão."""
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    for c in list(bpy.data.collections):
        bpy.data.collections.remove(c)
    for bloco in (bpy.data.meshes, bpy.data.curves, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
        for d in list(bloco):
            if d.users == 0:
                bloco.remove(d)


def material(nome, hexcor, rugosidade=0.7):
    m = bpy.data.materials.get(nome) or bpy.data.materials.new(nome)
    m.diffuse_color = rgba(hexcor)
    m.roughness = rugosidade
    return m


# ---------------------------------------------------------------- malhas das formas (referencial da peça no jogo)

def _malha(nome, bm):
    me = bpy.data.meshes.new(nome)
    bm.to_mesh(me)
    bm.free()
    return me


def malha_caixa(nome, size):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=2.0)
    bmesh.ops.scale(bm, vec=Vector(size), verts=bm.verts)
    return _malha(nome, bm)


def malha_cilindro(nome, r1, r2, h):
    """Cilindro (ou cone truncado) em volta do Y local, de y = −h (raio r1) a y = +h (raio r2)."""
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=SEGMENTOS, radius1=r1, radius2=r2, depth=2 * h)
    bmesh.ops.rotate(bm, verts=bm.verts, matrix=Matrix.Rotation(-math.pi / 2, 3, 'X'))
    return _malha(nome, bm)


def malha_esfera(nome, raios):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=24, v_segments=16, radius=1.0)
    bmesh.ops.scale(bm, vec=Vector(raios), verts=bm.verts)
    return _malha(nome, bm)


def malha_toro(nome, R, r):
    """Toro no plano XZ local (eixo Y), como o do SDF."""
    bm = bmesh.new()
    nu, nv = SEGMENTOS, 16
    vs = []
    for i in range(nu):
        u = 2 * math.pi * i / nu
        for j in range(nv):
            v = 2 * math.pi * j / nv
            rr = R + r * math.cos(v)
            vs.append(bm.verts.new((rr * math.cos(u), r * math.sin(v), rr * math.sin(u))))
    for i in range(nu):
        for j in range(nv):
            a = vs[i * nv + j]
            b = vs[((i + 1) % nu) * nv + j]
            c = vs[((i + 1) % nu) * nv + (j + 1) % nv]
            d = vs[i * nv + (j + 1) % nv]
            bm.faces.new((a, d, c, b))
    return _malha(nome, bm)


def _capsula(bm, a, b, ra, rb, lados=16):
    """Cone arredondado de a até b (duas esferas e o tronco entre elas), direto num bmesh."""
    va, vb = Vector(a), Vector(b)
    eixo = vb - va
    comprimento = eixo.length
    for centro, raio in ((va, ra), (vb, rb)):
        m = Matrix.Translation(centro)
        bmesh.ops.create_uvsphere(bm, u_segments=lados, v_segments=max(6, lados // 2), radius=raio, matrix=m)
    if comprimento > 1e-6:
        z = eixo.normalized()
        rot = z.to_track_quat('Z', 'Y').to_matrix().to_4x4()
        m = Matrix.Translation((va + vb) / 2) @ rot
        bmesh.ops.create_cone(bm, cap_ends=False, segments=lados, radius1=ra, radius2=rb, depth=comprimento, matrix=m)


def malha_capsula(nome, a, b, ra, rb):
    bm = bmesh.new()
    _capsula(bm, a, b, ra, rb)
    return _malha(nome, bm)


def malha_mao(nome, segmentos):
    """A mão de massinha como proxy: uma cápsula por osso (cabeça, ponta, raio) no referencial da mão."""
    bm = bmesh.new()
    for s in segmentos:
        _capsula(bm, s['head'], s['tail'], s['radius'], s['radius'] * 0.96, lados=10)
    return _malha(nome, bm)


# ---------------------------------------------------------------- curvas

def curva_perfil(nome, pontos, h, arredondado):
    """Perfil recortado: curva 2D preenchida; extrusão + bisel com o deslocamento que mantém o contorno no lugar."""
    cu = bpy.data.curves.new(nome, 'CURVE')
    cu.dimensions = '2D'
    cu.fill_mode = 'BOTH'
    rd = min(arredondado, h)
    cu.extrude = h - rd
    cu.bevel_depth = rd
    cu.bevel_resolution = 3
    cu.offset = -rd
    sp = cu.splines.new('POLY')
    sp.points.add(len(pontos) - 1)
    for pt, (x, y) in zip(sp.points, pontos):
        pt.co = (x, y, 0.0, 1.0)
    sp.use_cyclic_u = True
    return cu


def malha_torno(nome, pontos, fechado):
    """Meridiano (x, ρ) no plano XY local; o Parafuso gira em volta do X."""
    bm = bmesh.new()
    vs = [bm.verts.new((x, rho, 0.0)) for x, rho in pontos]
    for i in range(len(vs) - 1):
        bm.edges.new((vs[i], vs[i + 1]))
    if fechado:
        bm.edges.new((vs[-1], vs[0]))
    return _malha(nome, bm)


def curva_tubo(nome, pontos, raios):
    cu = bpy.data.curves.new(nome, 'CURVE')
    cu.dimensions = '3D'
    cu.bevel_depth = 1.0
    cu.bevel_resolution = 4
    cu.use_fill_caps = True
    sp = cu.splines.new('POLY')
    sp.points.add(len(pontos) - 1)
    for pt, p, r in zip(sp.points, pontos, raios):
        pt.co = (p[0], p[1], p[2], 1.0)
        pt.radius = r
    return cu


# ---------------------------------------------------------------- peças

# Formas definidas por pontos no referencial da peça: a origem do objeto vai para o centro delas.
LIVRES = ('profile', 'lathe', 'tube', 'capsule', 'roundCone')


def centro_local(p):
    """Centro da peça no referencial dela (a origem do objeto no Blender): o meio da caixa dos pontos; no torno, só
    em X (o giro é em volta do X da peça); nas formas centradas por definição, a origem."""
    s = p['shape']
    if s == 'profile':
        xs, ys = [q[0] for q in p['points']], [q[1] for q in p['points']]
        return Vector(((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, 0.0))
    if s == 'lathe':
        xs = [q[0] for q in p['points']]
        return Vector(((min(xs) + max(xs)) / 2, 0.0, 0.0))
    if s == 'tube':
        return Vector([(min(q[i] for q in p['points']) + max(q[i] for q in p['points'])) / 2 for i in range(3)])
    if s in ('capsule', 'roundCone'):
        return (Vector(p['a']) + Vector(p['b'])) / 2
    return Vector((0.0, 0.0, 0.0))


def no_centro(p):
    """A peça com os pontos relativos ao centro (o que vai nos dados do objeto)."""
    c = centro_local(p)
    q = dict(p)
    s = p['shape']
    if s == 'profile':
        q['points'] = [[x - c.x, y - c.y] for x, y in p['points']]
    elif s == 'lathe':
        q['points'] = [[x - c.x, r] for x, r in p['points']]
    elif s == 'tube':
        q['points'] = [[x - c.x, y - c.y, z - c.z] for x, y, z in p['points']]
    elif s in ('capsule', 'roundCone'):
        q['a'] = list(Vector(p['a']) - c)
        q['b'] = list(Vector(p['b']) - c)
    return q


def matriz_peca(p):
    """matrix_world do objeto de uma peça: o referencial dela no jogo, com a origem no centro."""
    return eixos.matriz_blender(p.get('pos'), p.get('rot')) @ Matrix.Translation(centro_local(p))


def criar_peca(p):
    """Objeto do Blender de uma peça da receita (sem matriz: quem chama põe na coleção e posiciona com matriz_peca)."""
    p = no_centro(p)
    s = p['shape']
    nome = p['name']
    mods = []
    if s == 'profile':
        dados = curva_perfil(nome, p['points'], p['h'], p.get('round', 0))
    elif s == 'lathe':
        dados = malha_torno(nome, p['points'], p.get('closed', False))
        mods.append(('PARAFUSO', None))
    elif s == 'tube':
        raios = p['radii'] if 'radii' in p else [p['r']] * len(p['points'])
        dados = curva_tubo(nome, p['points'], raios)
    elif s == 'roundBox':
        dados = malha_caixa(nome, p['size'])
        if p.get('r', 0) > 0:
            mods.append(('BISEL', p['r']))
    elif s == 'cylinder':
        dados = malha_cilindro(nome, p['r'], p['r'], p['h'])
        if p.get('round', 0) > 0:
            mods.append(('BISEL', p['round']))
    elif s == 'cone':
        dados = malha_cilindro(nome, p['r1'], p['r2'], p['h'])
    elif s == 'sphere':
        dados = malha_esfera(nome, (p['r'],) * 3)
    elif s == 'ellipsoid':
        dados = malha_esfera(nome, p['radii'])
    elif s == 'torus':
        dados = malha_toro(nome, p['R'], p['r'])
    elif s == 'capsule':
        dados = malha_capsula(nome, p['a'], p['b'], p['r'], p['r'])
    elif s == 'roundCone':
        dados = malha_capsula(nome, p['a'], p['b'], p['ra'], p['rb'])
    else:
        raise ValueError(f'forma desconhecida: {s}')
    obj = bpy.data.objects.new(nome, dados)
    for tipo, valor in mods:
        if tipo == 'BISEL':
            m = obj.modifiers.new('bisel', 'BEVEL')
            m.width = valor
            m.segments = 3
            m.limit_method = 'NONE'
        elif tipo == 'PARAFUSO':
            m = obj.modifiers.new('parafuso', 'SCREW')
            m.axis = 'X'
            m.angle = 2 * math.pi
            m.steps = SEGMENTOS
            m.render_steps = SEGMENTOS
            m.use_merge_vertices = True
            m.merge_threshold = 1e-4
            m.use_normal_calculate = True
    return obj


def importar(receita, cabecalho, contexto):
    """Monta a cena da receita. Devolve a coleção raiz."""
    limpar_cena()
    cena = bpy.context.scene
    cena['massacre_contexto'] = json.dumps(contexto)
    raiz = bpy.data.collections.new(f"MASSACRE {receita['id']}")
    cena.collection.children.link(raiz)
    topo = {k: receita[k] for k in ('id', 'version', 'refs', 'materials', 'soft') if k in receita}
    raiz['massacre'] = json.dumps({**topo, 'cabecalho': cabecalho, 'ordemAncoras': list(receita['anchors'].keys())})

    faccao = contexto['faccao']
    mats = {}
    for slot, massa in receita['materials'].items():
        if massa in ('acento', 'acento2'):
            m = material(f'massa:{slot}', contexto['acentos'][faccao][massa], 0.6)
        else:
            clay = contexto['massas'][massa]
            m = material(f'massa:{slot}', clay['color'], clay.get('roughness', 0.7))
        m['massacre_massa'] = massa
        mats[slot] = m

    grupos = {}
    for ordem, (g, definicao) in enumerate(receita['groups'].items()):
        col = bpy.data.collections.new(f'grupo:{g}')
        raiz.children.link(col)
        col['massacre_ordem'] = ordem
        grupos[g] = col
        pivo = bpy.data.objects.new(f'pivo:{g}', None)
        pivo.empty_display_type = 'SPHERE'
        pivo.empty_display_size = 0.35
        pivo.matrix_world = eixos.matriz_blender(definicao.get('pivot'))
        pivo['massacre_grupo'] = json.dumps(definicao)
        col.objects.link(pivo)

    for ordem, p in enumerate(receita['parts']):
        obj = criar_peca(p)
        grupos[p['group']].objects.link(obj)
        obj.matrix_world = matriz_peca(p)
        obj.data.materials.append(mats[p['mat']])
        obj['massacre_parte'] = json.dumps(p)
        obj['massacre_ordem'] = float(ordem)
        if p.get('op') == 'subtract':
            obj.display_type = 'WIRE'
            obj.color = COR_CORTE
            obj.show_in_front = True

    ancoras = bpy.data.collections.new('ancoras')
    raiz.children.link(ancoras)
    mao_mat = material('massa:mao', contexto.get('corMao', '#C8553D'))
    for nome, a in receita['anchors'].items():
        e = bpy.data.objects.new(f'ancora:{nome}', None)
        e.empty_display_type = 'ARROWS'
        e.empty_display_size = 1.6
        ancoras.objects.link(e)
        e.matrix_world = eixos.matriz_blender(a['pos'], a.get('rot'))
        e['massacre_ancora'] = json.dumps(a)
        if 'pose' in a:
            e['pose'] = a['pose']  # editável no painel de propriedades (as poses de src/data/hands.js)
        lado = {'maoDireita': 'direita', 'maoEsquerda': 'esquerda'}.get(nome)
        if lado and a.get('pose') in contexto['maos'][lado]:
            proxy = bpy.data.objects.new(f'mao:{nome}', malha_mao(f'mao:{nome}', contexto['maos'][lado][a['pose']]))
            proxy.data.materials.append(mao_mat)
            ancoras.objects.link(proxy)
            proxy.parent = e
            proxy.matrix_parent_inverse = Matrix.Identity(4)
            proxy.hide_select = True
            proxy['massacre_proxy'] = True

    planta = contexto.get('planta')
    if planta:
        col = bpy.data.collections.new('planta (não exporta)')
        raiz.children.link(col)
        boca = receita['anchors'].get('boca', {}).get('pos', [0, 0, 0])
        cu = bpy.data.curves.new('planta', 'CURVE')
        cu.dimensions = '3D'
        cu.bevel_depth = 0.05
        cu.bevel_resolution = 2
        for anel in [planta['points'], *planta.get('holes', [])]:
            sp = cu.splines.new('POLY')
            sp.points.add(len(anel) - 1)
            for pt, (x, y) in zip(sp.points, anel):
                pt.co = (x + boca[0], y + boca[1], 0.0, 1.0)
            sp.use_cyclic_u = True
        obj = bpy.data.objects.new('planta', cu)
        obj.data.materials.append(material('planta', COR_PLANTA, 0.9))
        obj.matrix_world = eixos.C.copy()
        obj.hide_select = True
        obj['massacre_planta'] = True
        col.objects.link(obj)
    return raiz
```

```python file=tools/blender/massacre/exportar.py
"""Exportar: a cena do Blender volta a ser a receita (Fase 4.1; docs/phases/phase-4.md, seção 4.1, "Blender").

Lê a coleção `MASSACRE <id>`: as peças de cada `grupo:<nome>` (na ordem guardada; cópias entram depois da original),
os pivôs, as âncoras e as massas. Converte os eixos (Blender → jogo), dobra a escala dos objetos nos parâmetros da forma
e usa o valor guardado na importação sempre que o novo é o mesmo (dentro de 5·10⁻⁵ u): sem edição, a receita volta
idêntica. Nas peças definidas por pontos a origem do objeto é o centro da peça (importar.centro_local): mover e escalar
mexem nos pontos e o `pos` guardado fica; girar leva a peça para o referencial do objeto. A validação completa é a do jogo (tools/blender.mjs valida antes de gravar por cima da receita).
"""

import json

import bpy
from mathutils import Vector

from . import eixos
from .importar import LIVRES, centro_local

TOL = 5e-5
GEOMETRIA = ('MESH', 'CURVE', 'SURFACE', 'META', 'FONT')


def _perto(a, b, tol=TOL):
    if isinstance(a, (list, tuple)) and isinstance(b, (list, tuple)):
        return len(a) == len(b) and all(_perto(x, y, tol) for x, y in zip(a, b))
    if isinstance(a, (int, float)) and isinstance(b, (int, float)) and not isinstance(a, bool):
        return abs(a - b) <= tol
    return a == b


def _manter(guardado, novo):
    """O guardado se o novo é o mesmo; senão o novo (o formato canônico arredonda na gravação)."""
    return guardado if guardado is not None and _perto(guardado, novo) else novo


def raiz_da_cena():
    for c in bpy.data.collections:
        if c.name.startswith('MASSACRE ') and 'massacre' in c:
            return c
    raise RuntimeError('a cena não tem uma arma importada (coleção "MASSACRE <id>")')


def grupo_de(obj):
    for c in obj.users_collection:
        if c.name.startswith('grupo:'):
            return c.name[len('grupo:'):]
    return None


def _massa_de(obj):
    for slot in obj.material_slots:
        if slot.material and slot.material.name.startswith('massa:'):
            return slot.material.name[len('massa:'):]
    return None


def _caixa_local(obj):
    """Caixa dos vértices da malha (sem modificadores), no referencial da peça."""
    vs = [v.co for v in obj.data.vertices]
    lo = Vector((min(v.x for v in vs), min(v.y for v in vs), min(v.z for v in vs)))
    hi = Vector((max(v.x for v in vs), max(v.y for v in vs), max(v.z for v in vs)))
    return lo, hi


def _bisel(obj):
    m = obj.modifiers.get('bisel')
    return m.width if m else 0.0


def _ordem_das_arestas(me):
    """Vértices do meridiano na ordem das arestas, a partir do vértice 0 (o torno volta na ordem em que foi feito)."""
    viz = {v.index: [] for v in me.vertices}
    for e in me.edges:
        a, b = e.vertices
        viz[a].append(b)
        viz[b].append(a)
    ordem, anterior, atual = [0], None, 0
    while True:
        prox = [n for n in viz[atual] if n != anterior and n not in ordem]
        if not prox:
            break
        anterior, atual = atual, prox[0]
        ordem.append(atual)
    return [me.vertices[i].co for i in ordem]


def _pos(p, p0, pos):
    """`pos` na peça: ausente se era ausente e continua na origem; o guardado se não mudou."""
    if 'pos' not in p0 and _perto(list(pos), [0.0, 0.0, 0.0]):
        p.pop('pos', None)
    else:
        p['pos'] = _manter(p0.get('pos'), list(pos))


def _exportar_livre(obj, p0, p, loc, rot3, esc):
    """Peça definida por pontos (a origem do objeto no centro dela, importar.centro_local). Sem giro, o referencial
    guardado fica: a translação e a escala voltam aos pontos (o que o ponto não leva — o Z do perfil, o Y/Z do torno —
    vai para `pos`). Com giro, o referencial passa a ser o do objeto."""
    s = p0['shape']
    c = centro_local(p0)
    S = esc
    if eixos.mesma_rotacao(rot3, p0.get('rot')):
        R = eixos.rot_jogo(p0.get('rot'))
        pos = Vector(p0.get('pos', (0.0, 0.0, 0.0)))
        desl = c + R.transposed() @ (loc - (pos + R @ c))  # onde o centro foi parar, no referencial guardado
    else:
        R = rot3
        desl = Vector((S.x * c.x, S.y * c.y, S.z * c.z))
        pos = loc - R @ desl
        p['rot'] = eixos.euler_jogo(R)
    resto = Vector((0.0, 0.0, desl.z)) if s == 'profile' else Vector((0.0, desl.y, desl.z)) if s == 'lathe' else Vector()
    _pos(p, p0, pos + R @ resto)
    desl = desl - resto
    media = (S.x + S.y + S.z) / 3
    if s == 'profile':
        cu = obj.data
        pts = [[pt.co.x * S.x + desl.x, pt.co.y * S.y + desl.y] for pt in cu.splines[0].points]
        p['points'] = _manter(p0['points'], pts)
        rd = cu.bevel_depth
        p['h'] = _manter(p0['h'], (cu.extrude + rd) * S.z)
        if 'round' in p0 or rd > 0:
            # A importação limita o bisel à meia-espessura (como o SDF): o guardado vale se o limite bate.
            novo = rd * min(S.x, S.y, S.z)
            limitado = min(p0.get('round', 0), p0['h'])
            p['round'] = p0['round'] if 'round' in p0 and _perto(limitado, novo) else novo
    elif s == 'lathe':
        pts = [[v.x * S.x + desl.x, v.y * (S.y + S.z) / 2] for v in _ordem_das_arestas(obj.data)]
        p['points'] = _manter(p0['points'], pts)
    elif s == 'tube':
        sp = obj.data.splines[0]
        pts = [[pt.co.x * S.x + desl.x, pt.co.y * S.y + desl.y, pt.co.z * S.z + desl.z] for pt in sp.points]
        raios = [pt.radius * obj.data.bevel_depth * media for pt in sp.points]
        p['points'] = _manter(p0['points'], pts)
        if 'r' in p0 and all(abs(r - raios[0]) <= TOL for r in raios):
            p['r'] = _manter(p0['r'], raios[0])
        else:
            p.pop('r', None)
            p['radii'] = _manter(p0.get('radii'), raios)
    else:  # capsule, roundCone: as pontas saem da peça guardada (a malha é só o desenho)
        for k in ('a', 'b'):
            v = Vector(p0[k]) - c
            p[k] = _manter(p0[k], [v.x * S.x + desl.x, v.y * S.y + desl.y, v.z * S.z + desl.z])
        for k in (('r',) if s == 'capsule' else ('ra', 'rb')):
            p[k] = _manter(p0[k], p0[k] * media)


def exportar_peca(obj, p0):
    """A peça de um objeto: transformação, grupo e massa do Blender; parâmetros da forma com a escala dobrada."""
    loc, rot3, esc = eixos.para_jogo(obj.matrix_world)
    p = dict(p0)
    p['name'] = obj.name
    p['group'] = grupo_de(obj) or p0['group']
    p['mat'] = _massa_de(obj) or p0['mat']
    s = p0['shape']
    if s in LIVRES:
        _exportar_livre(obj, p0, p, loc, rot3, esc)
        return p
    # Formas centradas (malhas geradas pelos parâmetros): o centro da caixa dos vértices (se a malha foi mexida no
    # modo de edição) entra na posição; a escala entra nos parâmetros.
    sx, sy, sz = esc.x, esc.y, esc.z
    media_xz = (sx + sz) / 2
    lo, hi = _caixa_local(obj)
    meia = (hi - lo) / 2
    c = (hi + lo) / 2
    centro = Vector((c.x * sx, c.y * sy, c.z * sz)) if c.length > TOL else Vector((0.0, 0.0, 0.0))
    _pos(p, p0, loc + rot3 @ centro)
    if not eixos.mesma_rotacao(rot3, p0.get('rot')):
        p['rot'] = eixos.euler_jogo(rot3)
    if s == 'roundBox':
        p['size'] = _manter(p0['size'], [meia.x * sx, meia.y * sy, meia.z * sz])
        r = _bisel(obj) * min(sx, sy, sz)
        if 'r' in p0 or r > 0:
            p['r'] = _manter(p0.get('r'), r)
    elif s == 'cylinder':
        p['r'] = _manter(p0['r'], (meia.x + meia.z) / 2 * media_xz)
        p['h'] = _manter(p0['h'], meia.y * sy)
        rd = _bisel(obj) * min(sx, sy, sz)
        if 'round' in p0 or rd > 0:
            p['round'] = _manter(p0.get('round'), rd)
    elif s == 'cone':
        vs = [v.co for v in obj.data.vertices]
        y0 = min(v.y for v in vs)
        y1 = max(v.y for v in vs)
        raio = lambda y: max((Vector((v.x, v.z)).length for v in vs if abs(v.y - y) < 1e-4), default=0.0)
        p['h'] = _manter(p0['h'], (y1 - y0) / 2 * sy)
        p['r1'] = _manter(p0['r1'], raio(y0) * media_xz)
        p['r2'] = _manter(p0['r2'], raio(y1) * media_xz)
    elif s == 'sphere':
        p['r'] = _manter(p0['r'], (meia.x * sx + meia.y * sy + meia.z * sz) / 3)
    elif s == 'ellipsoid':
        p['radii'] = _manter(p0['radii'], [meia.x * sx, meia.y * sy, meia.z * sz])
    elif s == 'torus':
        r = meia.y * sy
        p['r'] = _manter(p0['r'], r)
        p['R'] = _manter(p0['R'], (meia.x * sx + meia.z * sz) / 2 - r)
    return p


def exportar():
    """Lê a cena e devolve (receita, cabecalho)."""
    bpy.context.view_layer.update()  # matrizes do mundo em dia (num script, mexer em location não as recalcula)
    raiz = raiz_da_cena()
    topo = json.loads(raiz['massacre'])
    cabecalho = topo.pop('cabecalho')
    ordem_ancoras = topo.pop('ordemAncoras')
    materials = dict(topo['materials'])
    for m in bpy.data.materials:
        if m.name.startswith('massa:') and 'massacre_massa' in m and m.users > 0:
            materials.setdefault(m.name[len('massa:'):], m['massacre_massa'])

    colecoes = sorted((c for c in raiz.children if c.name.startswith('grupo:')), key=lambda c: c.get('massacre_ordem', 99))
    groups = {}
    for c in colecoes:
        g = c.name[len('grupo:'):]
        pivo = bpy.data.objects.get(f'pivo:{g}')
        d0 = json.loads(pivo['massacre_grupo']) if pivo and 'massacre_grupo' in pivo else {}
        d = dict(d0)
        if pivo:
            loc, _, _ = eixos.para_jogo(pivo.matrix_world)
            d['pivot'] = _manter(d0.get('pivot'), list(loc))
        groups[g] = d

    # Objeto de geometria sem a peça guardada não tem forma do jogo: nada some calado na exportação.
    soltos = sorted(o.name for o in bpy.data.objects if o.type in GEOMETRIA and o.users_collection
                    and not any(k in o for k in ('massacre_parte', 'massacre_proxy', 'massacre_planta', 'massacre_previa')))
    if soltos:
        raise RuntimeError('objetos sem receita: ' + ', '.join(soltos) + ' — peça nova é cópia de uma peça da mesma '
                           'forma (Shift+D); o resto, apague')
    objetos = []
    for c in colecoes:
        for obj in c.objects:
            if 'massacre_parte' in obj:
                objetos.append(obj)
    objetos.sort(key=lambda o: (o['massacre_ordem'], o.name))
    parts = [exportar_peca(o, json.loads(o['massacre_parte'])) for o in objetos]

    anchors = {}
    empties = {o.name[len('ancora:'):]: o for o in bpy.data.objects if o.name.startswith('ancora:') and 'massacre_ancora' in o}
    for nome in [n for n in ordem_ancoras if n in empties] + sorted(n for n in empties if n not in ordem_ancoras):
        e = empties[nome]
        a0 = json.loads(e['massacre_ancora'])
        a = dict(a0)
        loc, rot3, _ = eixos.para_jogo(e.matrix_world)
        a['pos'] = _manter(a0['pos'], list(loc))
        if not eixos.mesma_rotacao(rot3, a0.get('rot')):
            a['rot'] = eixos.euler_jogo(rot3)
        if 'pose' in e:
            a['pose'] = e['pose']
        anchors[nome] = a

    receita = {**{k: topo[k] for k in ('id', 'version', 'refs') if k in topo}, 'materials': materials}
    if topo.get('soft'):
        receita['soft'] = topo['soft']
    receita.update({'groups': groups, 'anchors': anchors, 'parts': parts})
    return receita, cabecalho
```

```python file=tools/blender/massacre/previa.py
"""Prévia do jogo no Blender (Fase 4.1; docs/phases/phase-4.md, seção 4.1, "Blender").

A malha que o jogo gera da receita (o SDF de verdade, uma malha por grupo no pivô), os braços de massinha nas âncoras
como no viewmodel parado e a câmera de primeira pessoa, lidos do que o tools/blender/previa.mjs gravou. Ficam numa
coleção que não exporta (cada objeto com `massacre_previa`): o `conferir` renderiza isso, e no Blender com janela o
botão "Prévia do jogo" refaz a prévia da cena editada (exporta para um temporário, valida e gera pelo jogo).
"""

import json
import os
import subprocess
import tempfile

import bpy
import numpy as np
from mathutils import Matrix, Quaternion, Vector

from . import eixos
from .importar import material

COLECAO = 'prévia do jogo (não exporta)'


def _ler(dados, bloco, tipo):
    return np.frombuffer(dados, dtype=tipo, count=bloco['count'], offset=bloco['offset'])


def _malha(nome, dados, m, materiais):
    pos = _ler(dados, m['positions'], np.float32)
    nor = _ler(dados, m['normals'], np.float32)
    idx = _ler(dados, m['indices'], np.uint32).astype(np.int32)
    nv, nt = len(pos) // 3, len(idx) // 3
    me = bpy.data.meshes.new(nome)
    me.vertices.add(nv)
    me.vertices.foreach_set('co', pos)
    me.loops.add(nt * 3)
    me.loops.foreach_set('vertex_index', idx)
    me.polygons.add(nt)
    me.polygons.foreach_set('loop_start', np.arange(0, nt * 3, 3, dtype=np.int32))
    for mat in materiais:
        me.materials.append(mat)
    if 'massas' in m:
        me.polygons.foreach_set('material_index', _ler(dados, m['massas'], np.uint8).astype(np.int32))
    me.update(calc_edges=True)
    me.shade_smooth()
    me.normals_split_custom_set_from_vertices(nor.reshape(-1, 3))  # as normais do jogo (gradiente do SDF)
    return me


def remover():
    """Tira a prévia anterior (objetos, malhas e a coleção)."""
    col = bpy.data.collections.get(COLECAO)
    malhas = []
    for o in [o for o in bpy.data.objects if 'massacre_previa' in o]:
        if o.type == 'MESH':
            malhas.append(o.data)
        dados_cam = o.data if o.type == 'CAMERA' else None
        bpy.data.objects.remove(o, do_unlink=True)
        if dados_cam and dados_cam.users == 0:
            bpy.data.cameras.remove(dados_cam)
    for me in malhas:
        if me.users == 0:
            bpy.data.meshes.remove(me)
    if col:
        bpy.data.collections.remove(col)


def carregar(caminho_json, visivel=True):
    """Monta a prévia gravada pelo previa.mjs. Devolve a coleção."""
    remover()
    with open(caminho_json, encoding='utf-8') as f:
        cab = json.load(f)
    with open(os.path.join(os.path.dirname(caminho_json), cab['bin']), 'rb') as f:
        dados = f.read()
    col = bpy.data.collections.new(COLECAO)
    bpy.context.scene.collection.children.link(col)
    mats = [bpy.data.materials.get(f'massa:{slot}') or material(f'massa:{slot}', '#8F959C') for slot in cab['materiais']]
    for g in cab['grupos']:
        o = bpy.data.objects.new(f"jogo:{g['nome']}", _malha(f"jogo:{g['nome']}", dados, g, mats))
        col.objects.link(o)
        o.matrix_world = eixos.matriz_blender(g['pivo'])
        o['massacre_previa'] = 'arma'
    mao = bpy.data.materials.get('massa:mao') or material('massa:mao', cab['corMao'])
    for m in cab['maos']:
        o = bpy.data.objects.new(f"jogo:braco-{m['lado']}", _malha(f"jogo:braco-{m['lado']}", dados, m, [mao]))
        col.objects.link(o)
        o.matrix_world = eixos.C.copy()
        o['massacre_previa'] = 'mao'
    c = cab['camera']
    cam_dados = bpy.data.cameras.new('jogo:primeira-pessoa')
    cam_dados.sensor_fit = 'VERTICAL'
    cam_dados.angle_y = np.radians(c['fovY'])
    cam_dados.clip_start = c['near']
    cam_dados.clip_end = c['far']
    cam = bpy.data.objects.new('jogo:primeira-pessoa', cam_dados)
    col.objects.link(cam)
    x, y, z, w = c['quat']
    cam.matrix_world = eixos.C @ Matrix.Translation(Vector(c['pos'])) @ Quaternion((w, x, y, z)).to_matrix().to_4x4()
    cam['massacre_previa'] = 'camera'
    for o in col.objects:
        o.hide_select = True
    camada = bpy.context.view_layer.layer_collection.children.get(COLECAO)
    if camada:
        camada.hide_viewport = not visivel
    return col


def atualizar(contexto, receita_js, visivel=True):
    """Refaz a prévia a partir de uma receita já validada (a do disco ou a cena exportada para um temporário): o jogo
    gera a malha num temporário e a prévia entra no lugar da anterior."""
    pasta = os.path.join(tempfile.gettempdir(), 'massacre-blender')
    os.makedirs(pasta, exist_ok=True)
    saida = os.path.join(pasta, os.path.splitext(os.path.basename(receita_js))[0] + '-previa-cena')
    res = subprocess.run(
        [contexto['node'], contexto['ferramenta'], 'previa', receita_js, saida],
        capture_output=True, text=True, encoding='utf-8', cwd=contexto['raiz'],
    )
    if res.returncode != 0:
        raise RuntimeError('o jogo não gerou a prévia:\n' + (res.stdout + res.stderr).strip())
    try:
        return carregar(saida + '.json', visivel)
    finally:
        for ext in ('.json', '.bin'):
            if os.path.exists(saida + ext):
                os.remove(saida + ext)
```

```python file=tools/blender/massacre/conferir.py
"""Conferir: renderiza as vistas da arma (Workbench, sem janela) — Fase 4.1; docs/phases/phase-4.md, seção 4.1,
"Blender". Fundo creme de papel, cor pelas massas, contorno fino.

O render mostra a prévia do jogo (previa.py): a malha que o jogo gera da receita, com costuras, cortes e bordas
arredondadas do SDF, não as peças de edição. As vistas da arma saem sem as mãos — a lateral com a planta de referência
por cima, de cima, de frente e 3/4, em câmera ortográfica enquadrando a arma —; depois os braços de massinha nas âncoras
(3/4) e a primeira pessoa (a câmera do viewmodel com o viewmodel_fov e os offsets padrão). A cena volta como estava.
"""

import os

import bpy
from mathutils import Matrix, Vector

from . import eixos
from .importar import rgba

# (nome, direção de onde a câmera olha no referencial do jogo, "para cima" no do Blender, com a planta, com as mãos)
VISTAS = (
    ('lado', (0.0, 0.0, 1.0), (0.0, 0.0, 1.0), True, False),
    ('cima', (0.0, 1.0, 0.0), (0.0, 1.0, 0.0), False, False),
    ('frente', (1.0, 0.0, 0.0), (0.0, 0.0, 1.0), False, False),
    ('tres-quartos', (0.62, 0.42, 0.66), (0.0, 0.0, 1.0), False, False),
    ('maos', (0.62, 0.42, 0.66), (0.0, 0.0, 1.0), False, True),
)
PRIMEIRA_PESSOA = 'primeira-pessoa'
RESOLUCAO = (1600, 900)
FUNDO = '#F1E8D4'


def _caixa_mundo(objs):
    lo = Vector((float('inf'),) * 3)
    hi = Vector((float('-inf'),) * 3)
    for o in objs:
        for c in o.bound_box:
            w = o.matrix_world @ Vector(c)
            lo = Vector(map(min, lo, w))
            hi = Vector(map(max, hi, w))
    return lo, hi


def _preparar_cena(cena):
    cena.render.engine = 'BLENDER_WORKBENCH'
    cena.render.resolution_x, cena.render.resolution_y = RESOLUCAO
    cena.render.resolution_percentage = 100
    cena.render.image_settings.file_format = 'PNG'
    cena.render.film_transparent = False
    sh = cena.display.shading
    sh.light = 'STUDIO'
    sh.color_type = 'MATERIAL'
    sh.show_object_outline = True
    sh.object_outline_color = (0.12, 0.1, 0.09)
    sh.show_cavity = True
    sh.cavity_type = 'WORLD'
    if cena.world is None:
        cena.world = bpy.data.worlds.new('papel')
    cena.world.color = rgba(FUNDO)[:3]
    cena.view_settings.view_transform = 'Standard'


def _enquadrar(cam, cam_dados, lo, hi, olhar_jogo, cima):
    """Câmera ortográfica olhando de `olhar_jogo` para o centro da caixa, com a caixa inteira no quadro."""
    centro = (lo + hi) / 2
    raio = (hi - lo).length / 2 + 1.0
    d = eixos.ponto_blender(olhar_jogo).normalized()
    cam.matrix_world = Matrix.Translation(centro + d * (raio * 3)) @ _base_olhando(-d, Vector(cima))
    inv = cam.matrix_world.inverted()
    pts = [inv @ Vector((x, y, z)) for x in (lo.x, hi.x) for y in (lo.y, hi.y) for z in (lo.z, hi.z)]
    largura = max(p.x for p in pts) - min(p.x for p in pts)
    altura = max(p.y for p in pts) - min(p.y for p in pts)
    cam_dados.ortho_scale = max(largura, altura * RESOLUCAO[0] / RESOLUCAO[1]) * 1.12
    cam_dados.clip_start = 0.1
    cam_dados.clip_end = raio * 8
    return d


def conferir(pasta):
    """Renderiza as vistas da prévia do jogo em `pasta` e devolve os caminhos dos PNGs."""
    cena = bpy.context.scene
    bpy.context.view_layer.update()
    arma = [o for o in bpy.data.objects if o.get('massacre_previa') == 'arma']
    if not arma:
        raise RuntimeError('sem a prévia do jogo: gere a prévia antes de conferir')
    maos = [o for o in bpy.data.objects if o.get('massacre_previa') == 'mao']
    olho = next((o for o in bpy.data.objects if o.get('massacre_previa') == 'camera'), None)
    edicao = [o for o in bpy.data.objects if 'massacre_parte' in o or 'massacre_proxy' in o]
    planta = next((o for o in bpy.data.objects if 'massacre_planta' in o), None)
    todos = [*arma, *maos, *edicao, *([planta] if planta else [])]
    estado = {o.name: o.hide_render for o in todos}
    matriz_planta = planta.matrix_world.copy() if planta else None
    camera_antes = cena.camera
    _preparar_cena(cena)
    cam_dados = bpy.data.cameras.new('conferencia')
    cam_dados.type = 'ORTHO'
    cam = bpy.data.objects.new('conferencia', cam_dados)
    cena.collection.objects.link(cam)
    os.makedirs(pasta, exist_ok=True)
    arquivos = []

    def render(nome):
        cena.render.filepath = os.path.join(pasta, f'{nome}.png')
        bpy.ops.render.render(write_still=True)
        arquivos.append(cena.render.filepath)

    try:
        for o in edicao:
            o.hide_render = True
        for o in arma:
            o.hide_render = False
        lo_arma, hi_arma = _caixa_mundo(arma)
        lo_tudo, hi_tudo = _caixa_mundo([*arma, *maos])
        cena.camera = cam
        for nome, olhar_jogo, cima, com_planta, com_maos in VISTAS:
            if com_maos and not maos:
                continue
            for o in maos:
                o.hide_render = not com_maos
            lo, hi = (lo_tudo, hi_tudo) if com_maos else (lo_arma, hi_arma)
            d = _enquadrar(cam, cam_dados, lo, hi, olhar_jogo, cima)
            if planta:
                # A planta só na lateral, puxada para a frente da arma (a projeção ortográfica não muda).
                planta.hide_render = not com_planta
                planta.matrix_world = Matrix.Translation(d * (hi.y - lo.y)) @ matriz_planta
            render(nome)
        if olho and maos:
            for o in maos:
                o.hide_render = False
            if planta:
                planta.hide_render = True
            cena.camera = olho
            render(PRIMEIRA_PESSOA)
    finally:
        for o in todos:
            o.hide_render = estado[o.name]
        if planta:
            planta.matrix_world = matriz_planta
        cena.camera = camera_antes
        bpy.data.objects.remove(cam, do_unlink=True)
        bpy.data.cameras.remove(cam_dados)
    return arquivos


def _base_olhando(frente, cima):
    """Rotação de câmera (−Z para `frente`, +Y o mais perto de `cima`)."""
    z = -frente.normalized()
    x = cima.cross(z)
    if x.length < 1e-6:
        x = Vector((1.0, 0.0, 0.0)).cross(z)
    x.normalize()
    y = z.cross(x)
    m = Matrix((x, y, z)).transposed()
    return m.to_4x4()
```

```python file=tools/blender/massacre_armas.py
"""MASSACRE — as armas de massinha no Blender 5.2 (Fase 4.1; docs/phases/phase-4.md, seção 4.1, "Blender").

O Blender é o editor da receita (src/data/armas/<id>.js): importar monta a cena, exportar grava a receita de volta e
conferir renderiza as vistas da prévia do jogo (a malha que o jogo gera, com as mãos e a primeira pessoa) com a planta
de referência. Quem chama é o tools/blender.mjs (`npm run blender -- ...`), que prepara o contexto (paleta, planta, a mão
de massinha em cada pose calculada pelo rig do jogo, a prévia do jogo) num JSON:

  blender --python tools/blender/massacre_armas.py -- abrir <contexto.json>
  blender --background --python tools/blender/massacre_armas.py -- conferir <contexto.json>
  blender --background --python tools/blender/massacre_armas.py -- ida-volta <contexto.json> <saída.js>

Com janela, o painel "MASSACRE" (barra lateral da vista 3D, tecla N) tem Exportar (valida pelo jogo e grava por cima
da receita), Prévia do jogo (a malha que o jogo faria da cena como está), Conferir (as vistas em
tools/blender/conferencia/<id>/, da cena como está) e Recarregar (descarta a cena e relê a receita do disco).
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from massacre import conferir as conf  # noqa: E402
from massacre import exportar as exp  # noqa: E402
from massacre import importar as imp  # noqa: E402
from massacre import previa  # noqa: E402
from massacre import receita as rec  # noqa: E402


def carregar(contexto):
    """Lê a receita do disco e monta a cena."""
    receita, cabecalho = rec.ler(contexto['receita'])
    bpy.context.scene.unit_settings.system = 'NONE'  # u da arma = unidade do Blender, sem metros
    imp.importar(receita, cabecalho, contexto)
    return receita


def contexto_da_cena():
    cena = bpy.context.scene
    if 'massacre_contexto' not in cena:
        raise RuntimeError('esta cena não veio do `npm run blender -- abrir <arma>`')
    return json.loads(cena['massacre_contexto'])


def validar(contexto, arquivo):
    """Valida uma receita pelo jogo (a mesma validação do gerador): devolve (ok, mensagem)."""
    res = subprocess.run(
        [contexto['node'], contexto['ferramenta'], 'validar', arquivo],
        capture_output=True, text=True, encoding='utf-8', cwd=contexto['raiz'],
    )
    return res.returncode == 0, (res.stdout + res.stderr).strip()


def exportar_temporario(contexto):
    """Exporta a cena para uma receita temporária validada pelo jogo. Devolve (caminho, mensagem); quem chama apaga."""
    receita, cabecalho = exp.exportar()
    fd, tmp = tempfile.mkstemp(suffix='.js', prefix=f"{receita['id']}-")
    os.close(fd)
    try:
        rec.gravar(tmp, receita, cabecalho)
        ok, msg = validar(contexto, tmp)
        if not ok:
            raise RuntimeError(f'a receita exportada não passou na validação do jogo:\n{msg}')
    except BaseException:
        os.remove(tmp)
        raise
    return tmp, msg


def exportar_para(contexto, destino):
    """Exporta a cena, valida e só então grava em `destino`. Devolve a mensagem da validação."""
    tmp, msg = exportar_temporario(contexto)
    try:
        shutil.copyfile(tmp, destino)
    finally:
        os.remove(tmp)
    return msg


def previa_da_cena(contexto):
    """A prévia do jogo da cena como está (exporta para um temporário, valida, o jogo gera a malha)."""
    tmp, _ = exportar_temporario(contexto)
    try:
        return previa.atualizar(contexto, tmp)
    finally:
        os.remove(tmp)


# ---------------------------------------------------------------- painel (Blender com janela)

class MASSACRE_OT_exportar(bpy.types.Operator):
    bl_idname = 'massacre.exportar'
    bl_label = 'Exportar a receita'
    bl_description = 'Grava a arma em src/data/armas/<id>.js (valida pelo jogo antes; no jogo, "Reler a receita do disco")'

    def execute(self, context):
        try:
            ctx = contexto_da_cena()
            msg = exportar_para(ctx, ctx['receita'])
        except Exception as err:  # noqa: BLE001 — o painel mostra qualquer falha ao usuário
            self.report({'ERROR'}, str(err))
            return {'CANCELLED'}
        self.report({'INFO'}, f"{os.path.basename(ctx['receita'])} gravada · {msg}")
        return {'FINISHED'}


class MASSACRE_OT_previa(bpy.types.Operator):
    bl_idname = 'massacre.previa'
    bl_label = 'Prévia do jogo'
    bl_description = 'A malha que o jogo gera da cena como está (SDF, costuras, cortes, mãos), numa coleção que não exporta'

    def execute(self, context):
        try:
            col = previa_da_cena(contexto_da_cena())
        except Exception as err:  # noqa: BLE001
            self.report({'ERROR'}, str(err))
            return {'CANCELLED'}
        self.report({'INFO'}, f'prévia do jogo em "{col.name}" (o olho no Outliner mostra e esconde)')
        return {'FINISHED'}


class MASSACRE_OT_conferir(bpy.types.Operator):
    bl_idname = 'massacre.conferir'
    bl_label = 'Conferir (renders)'
    bl_description = ('Prévia do jogo da cena como está e as vistas lateral (com a planta), cima, frente, 3/4, mãos e '
                      'primeira pessoa em tools/blender/conferencia/<id>/')

    def execute(self, context):
        try:
            ctx = contexto_da_cena()
            previa_da_cena(ctx)
            arquivos = conf.conferir(ctx['pasta'])
        except Exception as err:  # noqa: BLE001
            self.report({'ERROR'}, str(err))
            return {'CANCELLED'}
        self.report({'INFO'}, f'{len(arquivos)} vistas em {os.path.dirname(arquivos[0])}')
        return {'FINISHED'}


class MASSACRE_OT_recarregar(bpy.types.Operator):
    bl_idname = 'massacre.recarregar'
    bl_label = 'Recarregar do disco'
    bl_description = 'Descarta a cena e relê a receita do disco (com a prévia do jogo dela, escondida)'

    def execute(self, context):
        try:
            ctx = contexto_da_cena()
            carregar(ctx)
            previa.atualizar(ctx, ctx['receita'], visivel=False)
        except Exception as err:  # noqa: BLE001
            self.report({'ERROR'}, str(err))
            return {'CANCELLED'}
        enquadrar()
        return {'FINISHED'}


class MASSACRE_PT_arma(bpy.types.Panel):
    bl_label = 'MASSACRE'
    bl_idname = 'MASSACRE_PT_arma'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'MASSACRE'

    def draw(self, context):
        col = self.layout.column(align=True)
        cena = context.scene
        if 'massacre_contexto' in cena:
            ctx = json.loads(cena['massacre_contexto'])
            col.label(text=f"Arma: {ctx['id']} (acento {ctx['faccao']})")
            col.label(text=os.path.relpath(ctx['receita'], ctx['raiz']))
        col.separator()
        col.operator('massacre.exportar', icon='EXPORT')
        col.operator('massacre.previa', icon='SHADING_RENDERED')
        col.operator('massacre.conferir', icon='RENDER_STILL')
        col.operator('massacre.recarregar', icon='FILE_REFRESH')
        col.separator()
        col.label(text='Peças: mova, gire, escale, edite pontos.')
        col.label(text='Peça nova: Shift+D numa da mesma forma.')
        col.label(text='Grupo: a coleção; massa: o material.')
        col.label(text='Âncora de mão: propriedade "pose".')


CLASSES = (MASSACRE_OT_exportar, MASSACRE_OT_previa, MASSACRE_OT_conferir, MASSACRE_OT_recarregar, MASSACRE_PT_arma)


def registrar():
    for c in CLASSES:
        if not hasattr(bpy.types, c.__name__):
            bpy.utils.register_class(c)


def sem_tela_de_abertura():
    """Com janela: a tela de abertura não cobre a arma. O Blender decide mostrá-la depois dos scripts da linha de
    comando; a preferência do usuário volta ao que era logo em seguida."""
    vista = bpy.context.preferences.view
    antes = vista.show_splash
    vista.show_splash = False

    def voltar():
        vista.show_splash = antes
        return None
    bpy.app.timers.register(voltar, first_interval=2.0)


def enquadrar():
    """Com janela: a vista 3D na lateral direita da arma (ortográfica, onde a planta guia; a boca à direita), sólida
    pela cor das massas, enquadrando as peças, com a barra lateral aberta (a aba MASSACRE)."""
    def fazer():
        pecas = [o for o in bpy.data.objects if 'massacre_parte' in o]
        for janela in bpy.context.window_manager.windows:
            for area in janela.screen.areas:
                if area.type != 'VIEW_3D':
                    continue
                esp = area.spaces.active
                esp.shading.type = 'SOLID'
                esp.shading.color_type = 'MATERIAL'
                esp.clip_start = 0.05
                esp.clip_end = 2000.0
                esp.show_region_ui = True
                regiao = next((r for r in area.regions if r.type == 'WINDOW'), None)
                if not regiao:
                    continue
                with bpy.context.temp_override(window=janela, screen=janela.screen, area=area, region=regiao):
                    bpy.ops.view3d.view_axis(type='FRONT')
                    for o in pecas:
                        o.select_set(True)
                    bpy.ops.view3d.view_selected()
                    for o in pecas:
                        o.select_set(False)
        return None
    bpy.app.timers.register(fazer, first_interval=1.0)


def principal():
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    if len(argv) < 2:
        raise SystemExit('uso: ... -- <abrir|conferir|ida-volta> <contexto.json> [saída.js]')
    acao, caminho = argv[0], argv[1]
    with open(caminho, encoding='utf-8') as f:
        contexto = json.load(f)
    if acao == 'abrir':
        sem_tela_de_abertura()
        registrar()
        carregar(contexto)
        if contexto.get('previa'):
            previa.carregar(contexto['previa'], visivel=False)
        enquadrar()
    elif acao == 'conferir':
        carregar(contexto)
        previa.carregar(contexto['previa'])
        arquivos = conf.conferir(contexto['pasta'])
        print('MASSACRE-CONFERIR ' + json.dumps(arquivos))
    elif acao == 'ida-volta':
        if len(argv) < 3:
            raise SystemExit('ida-volta precisa do arquivo de saída')
        carregar(contexto)
        receita, cabecalho = exp.exportar()
        rec.gravar(argv[2], receita, cabecalho)
        print(f'MASSACRE-IDA-VOLTA {argv[2]}')
    else:
        raise SystemExit(f'ação desconhecida: {acao}')


if __name__ == '__main__':
    principal()
```

- [ ] **Passo 6: O caminho no Blender** — com o Blender 5.2 instalado: o caminho do executável em `BLENDER_PATH` ou em `tools/blender/local.json` (`{ "blender": "<caminho do blender.exe>" }`, fora do git).

Run: `npm run blender -- ida-volta todas`
Expected: PASS (as sete linhas "ida e volta idêntica").
Run: `npm run blender -- conferir ak47`
Expected: PASS (seis vistas em `tools/blender/conferencia/ak47/`).

- [ ] **Passo 7: A suíte inteira**

Run: `npm test`
Expected: PASS — 328 testes passando.

- [ ] **Passo final: Commit** (só com o pedido do usuário)

```bash
git add tools/blender.mjs tools/blender package.json .gitignore tests/blenderPrevia.test.js
git commit -m "MASSACRE 4.1: o Blender como editor das receitas (importar, exportar, conferir, prévia do jogo)" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Tarefa 7: Verificação no navegador e no Blender

O servidor de desenvolvimento de outro chat pode estar na 5173: usar `massacre-dev-auto` (porta livre) ou uma configuração própria no `.claude/launch.json` da pasta-mãe (e tirar depois). A aba do jogo tem de ser a da frente do painel (aba de trás não recebe quadros); não emular um tamanho de tela maior que o painel (768 × 432 cabe). O `javascript_tool` corta em 45 s: para esperas longas, rodar em segundo plano e ler o resultado de `window` numa chamada seguinte.

- [ ] **Passo 1: A bancada** — `preview_start`; pelo `javascript_tool`, `massacre.console.execute('arsenal')` (ou `bancada`). Tab abre o painel. Para cada uma das sete (`massacre.states.current.map.bench.select('<id>')` ou o painel): na roda, a costura entre as massas, o boil "em dois", as digitais de perto, os veios da madeira (AK, faca) e o acento certo (Glock e AK terracota/laranja, M4A4 azul/verde-água, as dos dois lados amarelo/branco — trocar a facção no painel muda o acento); "Explodir" separa os grupos; "Âncoras" mostra as mãos e a boca; "Planta" sobrepõe a silhueta; "Medir" dá o IoU (0,873 · 0,931 · 0,937 · 0,945 · 0,894 · 0,947); as fileiras no tapete com as etiquetas, a roda com o suporte de arame, o quadro perfurado com as ferramentas e as plantas a lápis atrás.
- [ ] **Passo 2: Segurar** — no painel, "Segurar": a câmera estaciona e o viewmodel aparece com a arma escolhida e as duas mãos (a faca, uma); "Soltar" volta. Com a arma na mão, "Reler a receita do disco" troca a instância sem erro e sem vazar (`massacre.render.renderer.info.memory.geometries` igual antes e depois).
- [ ] **Passo 3: Primeira pessoa** — `massacre.console.execute('map pista')`, depois `arma glock`, `arma ak47`, `arma m4a4`, `arma awp`, `arma nova`, `arma p90`, `arma knife`: cada uma na mão com a mão direita na empunhadura (o primeiro dedo no gatilho), a esquerda no guarda-mão (pistola: em concha por baixo; faca: só a direita, em punho), a arma no canto de baixo à direita e os cotovelos fora da tela; a arma escurece fora do feixe da key e a mão faz sombra na arma. `viewmodel_presetpos 1`, `2` e `3` e `viewmodel_fov 54`/`68` mudam como no CS; `cl_bracadeira tr` mostra a braçadeira laranja no braço terracota e `cl_bracadeira ct` a azul; `thirdperson`, `noclip`, `kill` e `r_viewmodel 0` escondem o viewmodel; `firstperson`, `noclip` de novo e a volta depois da morte o trazem. `armas` lista as sete com triângulos e tempo de geração.
- [ ] **Passo 4: Memória em 3 ciclos** — colar no `javascript_tool` e ler `window.__ciclos` nas chamadas seguintes (a coleta leva ~2 min):

```js
const m = massacre; const st = m.states;
const mem = () => { const i = m.render.renderer.info; return { g: i.memory.geometries, t: i.memory.textures, p: i.programs?.length ?? null }; };
const wait = (ms) => new Promise((r) => setTimeout(r, ms));
const until = async (f, ms = 60000) => { const t0 = performance.now(); while (!f()) { if (performance.now() - t0 > ms) return false; await wait(200); } return true; };
const R = window.__ciclos = { log: [], errs: [], fim: false };
const oe = console.error; console.error = (...a) => { R.errs.push(a.map(String).join(' ').slice(0, 200)); oe(...a); };
const naMapa = (id) => () => st.name === 'match' && st.current?.map?.id === id && !st.busy;
const noMenu = () => st.name === 'menu' && !st.busy;
(async () => {
  if (!noMenu()) { await st.go('menu'); await until(noMenu); } await wait(1500); R.log.push(['menu0', mem()]);
  for (let c = 1; c <= 3; c++) {
    m.console.execute('arsenal'); await until(naMapa('arsenal')); await wait(3500); R.log.push([`arsenal${c}`, mem()]);
    await st.go('menu'); await until(noMenu); await wait(1500); R.log.push([`menu-a${c}`, mem()]);
    m.console.execute('map pista'); await until(naMapa('pista')); await wait(3500); R.log.push([`pista${c}`, mem()]);
    await st.go('menu'); await until(noMenu); await wait(1500); R.log.push([`menu-p${c}`, mem()]);
  }
  console.error = oe; R.fim = true;
})();
```

  Esperado: os mesmos números no menu nas três voltas (na implementação verificada, 27/35/35 em geometrias/texturas/programas; arsenal 76/43/51; pista 68/92/59) e `errs` vazio.
- [ ] **Passo 5: O caminho do Blender** — `npm run blender -- ida-volta todas` (as sete idênticas); `npm run blender -- conferir todas` e olhar os PNGs (a lateral com a planta laranja batendo na silhueta, as mãos nas âncoras, a primeira pessoa igual à do jogo); `npm run blender -- abrir ak47`: a janela abre sem a tela de abertura, na lateral ortográfica, com a aba MASSACRE; escalar a massa de mira (`massaMira`) ×1,6 (a origem está no centro dela: cresce no lugar), "Prévia do jogo" (a malha do jogo aparece por cima, com a bola maior), "Exportar" (grava `src/data/armas/ak47.js`, validada); no jogo, `arsenal`, a AK na roda, Tab → "Reler a receita do disco": a bola maior na massa de mira (topo de 2,017 u → 2,46 u na malha do grupo `corpo`). Voltar a receita (`git checkout -- src/data/armas/ak47.js` ou a cópia guardada antes), reler e conferir 2,017 u de novo.
- [ ] **Passo 6: Console sem erros do jogo** em todos os passos; arquivos abaixo de 600 linhas (`src/clay/sdf/shapes.js`, o maior tocado, com 541).

---

### Tarefa 8: Documentação, moodboard e memória

- [ ] **Passo 1:** `docs/art/moodboard.md` — os 14 boards novos na tabela (QPG, QPL, QCG, QRF, QSG, NFS, CMH, QHH, CTL, QGW, QPB, QTT, QWS, QBP), a nota de que entram com todos os pins na ordem da busca/board e o item 13 (armas, mãos e a bancada) só com os pins estudados (pin → decisão → arquivo) e as fotos do Commons; `docs/art/pinterest-boards.json` com os pins dos 14 boards; `tools/moodboard.mjs` com os boards novos (o par abaixo); `npm run moodboard`.

Em `tools/moodboard.mjs`, trocar:

```
  { id: 'CTL', label: 'Clay Sculpting Tools', url: 'https://www.pinterest.com/ideas/clay-sculpting-tools/953040767088/', phase: '4.1' },
];
```

por:

```
  { id: 'CTL', label: 'Clay Sculpting Tools', url: 'https://www.pinterest.com/ideas/clay-sculpting-tools/953040767088/', phase: '4.1' },
  // Bancada de armas (mapa `arsenal`): bancada de armeiro, quadro de ferramentas, roda de modelar, suporte e planta.
  { id: 'QGW', label: 'Busca: gunsmith workbench', url: 'https://www.pinterest.com/search/pins/?q=gunsmith%20workbench', phase: '4.1' },
  { id: 'QPB', label: 'Busca: pegboard tool wall workshop', url: 'https://www.pinterest.com/search/pins/?q=pegboard%20tool%20wall%20workshop', phase: '4.1' },
  { id: 'QTT', label: 'Busca: miniature figure turntable display', url: 'https://www.pinterest.com/search/pins/?q=miniature%20figure%20turntable%20display', phase: '4.1' },
  { id: 'QWS', label: 'Busca: wire display stand miniature gun', url: 'https://www.pinterest.com/search/pins/?q=wire%20display%20stand%20miniature%20gun', phase: '4.1' },
  { id: 'QBP', label: 'Busca: gun pencil drawing blueprint', url: 'https://www.pinterest.com/search/pins/?q=gun%20pencil%20drawing%20blueprint', phase: '4.1' },
];
```

- [ ] **Passo 2:** `docs/phases/phase-4.md` — 4.1 ✅ com a data na tabela de estado; na seção 4.1, o aceite marcado com os números, "Ajustes feitos na implementação" e "Medições".
- [ ] **Passo 3:** `docs/PROGRESS.md` — "Como rodar" com o `npm run blender`; a decisão do Blender em "Ferramentas externas"; os serviços `weaponModels` e `handModels` nas convenções; a seção da Fase 4 com a subfase 4.1 (o que entrou, como testar, números, checklist) e a próxima (4.2 — Tiro e dano).
- [ ] **Passo 4:** memória do projeto (`massacre-game-project.md`): 4.1 pronta; o caminho do Blender (executável em `tools/blender/local.json`); próxima a 4.2.
- [ ] **Passo 5:** encerrar pedindo um chat novo para a 4.2.
