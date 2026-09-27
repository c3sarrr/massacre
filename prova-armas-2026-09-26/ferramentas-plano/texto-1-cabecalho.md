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

@@extrator

- [ ] **Passo 2: Conferir** — `node extract-plan.mjs docs/phases/phase-4.1-plan.md . src/clay/sdf/polygon.js` grava o arquivo pedido (apagar o arquivo de novo: a Tarefa 1 o cria no passo certo).

---
