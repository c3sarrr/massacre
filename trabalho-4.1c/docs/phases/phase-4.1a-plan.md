# Subfase 4.1a — Pipeline realista e a AK-47 tipo 3: plano executado

> **Plano executado (2026-09-26).** É o plano de desenho (`docs/superpowers/plans/2026-09-26-4.1a-pipeline-realista-ak47.md`)
> com o código final da execução: os blocos dos arquivos que a revisão crítica e o aceite mudaram — a ficha
> (`vistaDeCima` e as correções de lado), a régua, os acabamentos, o pacote do Blender (`pecas.py`, `materiais.py`,
> `ak47.py`, `assar.py`, `lod.py`) e o shader — trazem a versão verificada, e três passos novos trazem os pares do
> moodboard (Tarefa 6), da baioneta M9 (Tarefa 17) e do relatório (Tarefa 19). Aplicado numa cópia limpa da base pelo
> mesmo executor, reproduz a cópia de trabalho arquivo por arquivo; os binários (`assets/armas/ak47/`) o `construir`
> regera, conferidos pelas métricas do relatório.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** a AK-47 tipo 3 (receptor fresado) no nível final — construída por script Python no Blender a partir da ficha
e da régua sobre a foto real, assada e exportada como `.glb` + `.webp`, validada (silhueta ≥ 98 % com tolerância de
1 px da foto, medidas-chave ±1 %, orçamentos, nomes, malha e UV) — e mostrada no jogo, na bancada `arsenal` e em
primeira pessoa (ainda sem mãos), com o material de zonas e acabamentos, o reflexo do set, a pintura de fábrica, as três
skins de exemplo e o comando `skin`; a receita de massinha da AK sai e as outras seis armas continuam de massinha até a
4.1c/4.1d.

**Architecture:** o lado do Blender é o pacote `tools/blender/armas/` (biblioteca de peças, materiais de fábrica,
zonas, soquetes, assar, LOD, exportar, validar, conferir e o script `ak47.py`), chamado pelo lançador
`npm run blender -- construir|validar|conferir|abrir ak47`, que grava `assets/armas/ak47/` e o relatório; o Node confere
o `.glb` (bloco JSON), o cabeçalho de cada `.webp` e o relatório contra `src/data/armasReais.js`. No jogo, o serviço
`weaponModels` (`WeaponLibrary`) passa a ter duas origens — `massinha` (o gerador SDF da 4.1) e `glb` (`GlbSource`, com
o `GLTFLoader` e o `DRACOLoader` do vendor) — e a interface `info(id)` no lugar de `recipe(id)`; cada zona da arma
realista é um
`MeshPhysicalMaterial` com um trecho de shader que lê a textura `_m` e desenha o acabamento, com os números vindos da
função pura `acabamentoParaMaterial`; o reflexo do set é um PMREM capturado do mapa carregado; o viewmodel e a bancada
usam `info(id)` e mostram a AK sem braços.

**Tech Stack:** JavaScript ES Modules, three 0.186.1 (`GLTFLoader`, `DRACOLoader`, `MeshPhysicalMaterial` com
`onBeforeCompile`, `PMREMGenerator`, `TextureLoader`), `node --test`; Blender 5.2.2 (`bpy`, `bmesh`, Cycles com OptiX
para assar, exportador glTF com Draco, `numpy` embutido); WebP sem perdas.

**Especificação:** `docs/superpowers/specs/2026-09-26-armas-realistas-design.md` (aprovada pelo usuário em
2026-09-26; seções 1–9 e 11). Referências visuais: `docs/art/moodboard.md`, seção 14 (boards QVM a QMP). Regras:
`CLAUDE.md` com a exceção das regras 3 e 4 para armas e mãos (decisão 3 do desenho), arquivos com menos de ~600
linhas, números em `src/data/`, sem placeholder, nunca simplificar.

**Prova de conceito (fora do repositório):** `C:\Users\T-Gamer\Desktop\game tiro\prova-armas-2026-09-26\` —
`blender/ak_v3.py` (AK-47 tipo 3, 95,9 % bruto / 99,1 % com tolerância), `blender/base_helpers.py`,
`blender/base_final.py` e o trecho de `blender/ak_v2.py` entre `def mat_quadriculado` e `def construir2`; a régua em
`refsite/regua/` (`index.html`, `sobrepor.html`, `lib.js`, `ver.html`) com os contornos medidos em
`refsite/regua/ak47-tipo3.json`; renders em `refsite/spike/`; as ferramentas de gerar e validar plano da 4.1 em
`ferramentas-plano/`. O servidor de desenvolvimento da prova é `refsite/tools/dev-server.mjs` (porta 5181).

**Estado de partida:** a árvore da 4.1 na branch `fase-3.1` (3.5, 4.1 e os documentos do redesenho sem commit, sobre o
commit `953425b`); `npm test` com **328 testes passando**; Blender 5.2.2 em `S:\blender.exe`
(`tools/blender/local.json`, fora do git).

**Commits:** os passos "Commit" só rodam quando o usuário pedir (decisão da 3.3). Toda mensagem termina com a linha
`Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.

---

## Como este plano é executado

É o método das subfases grandes do projeto (memória `massacre-game-project`, 3.1 a 4.1):

1. **Cópia de trabalho** (Tarefa 0): `base-4.1a/` (o estado de partida, intocado) e `trabalho-4.1a/` (onde se
   implementa), na pasta-mãe `game tiro/`, cada uma com o seu `node_modules`.
2. **Tarefas 1 a 18 na cópia de trabalho**, na ordem. Os módulos puros (dados, contas, leitores, comando) vão por TDD
   com os testes deste plano: o teste falha antes (a falha esperada está no passo) e passa depois; a suíte inteira passa
   no fim de cada tarefa. O código completo dos arquivos novos está nos blocos; as mudanças em arquivos que já existem
   vêm como pares **trocar → por**, cada trecho "trocar" único no arquivo no momento em que se aplica.
3. **O Blender e o visual iteram.** As tarefas do Blender (5 a 8) e do aceite (18) trazem o código inicial completo e os
   critérios numéricos que o resultado precisa bater (silhueta, medidas, orçamentos, nomes, malha, UV); a revisão
   crítica compara render e foto e corrige até não sobrar defeito (regra do usuário: ser crítico e honesto e arrumar
   o que estiver ruim ou mediano). O código que sair dessa iteração é o que vale.
4. **Plano gerado do diff** (Tarefa 19): com tudo verificado, `docs/phases/phase-4.1a-plan.md` é gerado por script do
   diff `trabalho-4.1a` × `base-4.1a` (blocos inteiros para arquivos novos, pares únicos, estados intermediários quando
   um arquivo muda em várias tarefas), validado numa cópia limpa (falha antes / passa depois, contagem da suíte por
   tarefa, o `construir` do Blender aprovado) e aplicado no projeto com o mesmo executor.
5. **Arquivos binários** (`.glb`, `.webp`) não cabem no plano em Markdown: quem aplica roda
   `npm run blender -- construir ak47` e a comparação com a cópia de trabalho é pelos números do relatório (tolerância
   de 0,2 % nas medidas, 0,002 no IoU, 1 % nos triângulos e 5 % no tamanho dos arquivos), não por bytes.

Convenções que valem em todas as tarefas: arquivos com LF (a árvore do git sai com CRLF por `core.autocrlf`; os pares
casam em LF e gravam LF — normalizar antes de comparar); conteúdo com barra invertida vai pelas ferramentas de edição,
nunca por heredoc do Bash; PowerShell bloqueado por política (usar o Bash); o servidor de desenvolvimento só pelo
painel de pré-visualização (`.claude/launch.json` na pasta-mãe; entrada temporária para servir a cópia de trabalho).

---

## Decisões que este plano fixa

Tiradas do desenho e da leitura do código da 4.1; valem para todas as tarefas.

- **D1 — Referencial e unidades.** A construção é em milímetros no referencial da ficha (boca em x = 0, eixo do cano em
  y = 0, +X para a boca, +Y para cima). No Blender, X = x, Z = y e o lado direito da arma fica em −Y (cena em metros,
  1 mm = 0,001). A exportação escala por 1000/25,4 (1 unidade = 1 u = 1 polegada na escala do boneco) e põe a origem no
  eixo do cano sobre o **pino do gatilho** (AK: x = −551 mm, então a boca fica em +21,69 u, perto dos +21,2 u da receita
  de massinha — a posição da categoria `rifle` do viewmodel continua valendo). Com o Y para cima do glTF, o −Y do
  Blender vira +Z: no jogo a arma fica com +X na boca, +Y em cima e +Z no lado direito, como na 4.1.
- **D2 — Nomes no `.glb`.** Só `[a-z0-9_]`, porque o `GLTFLoader` apaga `:`, `/`, `.`, `[` e `]` dos nomes dos nós
  (`PropertyBinding.sanitizeNodeName`). Raiz `<id>`; níveis `perto`, `mundo` e `longe`; peças `<nivel>_<peca>`, com
  `base` (tudo o que não se mexe) mais as peças móveis da arma; soquetes `soquete_<nome>` dentro do nó `soquetes`; a
  zona de cada primitiva é o **nome do material** (`corpo`, `guarnicao`, `carregador`, `detalhes`, `interno`); o eixo
  de cada peça móvel vai nos `extras` do nó (o three põe em `userData`).
- **D3 — Texturas.** `_n` = normal em espaço tangente (MikkTSpace do Blender, convenção OpenGL); `_m` = R sombra de
  contato, G variação de aspereza (em torno de 0,5), B borda/desgaste, A variação de cor (em torno de 0,5). **WebP sem
  perdas:** o WebP com perdas guarda em YUV 4:2:0, subamostra o croma e mistura os canais empacotados e o relevo fino da
  normal. Gravadas de uma imagem de **8 bits** (a de ponto flutuante do Blender guarda o RGB multiplicado pelo alfa e
  divide ao gravar: estragava a `_m`), com o alfa da `_m` em 1/255 no mínimo (o WebP sem perdas pode trocar o RGB de
  pixel de alfa 0). O relevo e os canais são assados com antisserrilhado (16 amostras); a sombra (64 amostras) e a
  aspereza passam por um filtro binomial de 1 pixel e os canais de dados são quantizados em degraus que não aparecem
  no jogo (2/255 na sombra, 4/255 na aspereza e na cor). No jogo: `flipY = false` (convenção do glTF), `NoColorSpace`
  nas duas, a anisotropia da config (`graphics.anisotropy`, como o resto do set). O `.glb` leva as tangentes
  (`export_tangents`; as peças são trianguladas antes, porque o exportador pula sem aviso as tangentes de malha com
  n-gonos) para o relevo casar com o assado; com tangente no vértice, `normalScale` = (1, 1).
  O `mundo` usa o conjunto `_mundo_*`, assado de novo sobre o LOD1; o `longe` sai do LOD1 com as mesmas UVs e usa o
  mesmo conjunto.
- **D4 — Orçamento de arquivos (decisão do usuário, 2026-09-26).** A validação deste plano construiu a AK de ponta a
  ponta e mediu 7,1 MB sem compressão; o orçamento de 2,5 MB da primeira versão do desenho só fecharia com as texturas
  em 1024. O usuário escolheu o detalhe máximo: texturas de 2048 sem perdas, a quantização dos canais de dados (D3) e a
  geometria com **Draco** (`KHR_draco_mesh_compression`), com os orçamentos **fuzil 6 MB, pistola 3 MB, faca 2 MB,
  luvas 6 MB** (desenho, decisão 8 e seção 5.1). A AK medida: `.glb` 0,29 MB, `_n` 1,34 MB, `_m` 2,97 MB e o conjunto
  do mundo 0,54 MB — 5,1 MB. Se uma arma passar, primeiro baixar a entropia do que foi assado (variação na frequência
  que aparece na tela, não ruído de pixel); persistindo, parar e perguntar.
- **D5 — Raio de mira.** A foto, na escala de 870 mm, dá ≈ 370 mm do entalhe da alça (x ≈ −395,4) ao poste da massa
  (x ≈ −25,5); a ficha técnica diz 378 mm (2 % a mais, fora do ±1 %). A Tarefa 1 concilia antes de modelar (passo
  "Conciliar as medidas-chave"); a validação usa o alvo que a ficha registrar, com a fonte e a nota da divergência.
- **D6 — `info(id)` no lugar de `recipe(id)`.** A interface (Tarefa 11) serve as duas origens até a 4.1d; `describe(id)`
  (assíncrono) carrega o que falta — o `.glb`, o relatório e a ficha das realistas; a planta das de massinha.
- **D7 — AK sem mãos na 4.1a.** `info.hands = false`: o viewmodel mostra só a arma (a condição de aparecer deixa de
  exigir os braços quando a arma não usa mãos); `viewmodel_ajuste mao` avisa que as luvas chegam na 4.1b.
- **D8 — Skin é estado do serviço.** Uma skin atual por arma no `weaponModels` (`skinOf`/`setSkin`, evento
  `EV.WEAPON_MODEL` com `phase: 'skin'`), aplicada na roda, na fileira e na mão; o comando `skin` e o painel da bancada
  escrevem nele. As skins nomeadas são por zona e valem para qualquer arma realista (zona que a arma não tem é
  ignorada).
- **D9 — Reflexo do set.** Ponto `reflexo` (x, z) nos dados da sala de testes (`TEST_ROOM`), da pista (`PISTA`) e da
  bancada (`ARSENAL`), no centro da área jogável, na altura do olho do boneco (`HULL.standEye` acima do chão dali); mapa
  sem ponto usa o spawn (mais o olho, nos mapas de andar). Capturado logo depois de o mapa ser montado (antes do corpo do
  jogador entrar na cena) e de novo quando a GPU volta; vira o `envMap` dos materiais das armas realistas. O
  `scene.environment` de cada mapa — e o da camada do viewmodel, copiado dele — continua o do estúdio para o resto,
  inclusive os braços de massinha.
- **D10 — Fichas.** `tools/blender/refs/ak47.json` passa ao **formato 2** (ficha do desenho, seção 3.1); as plantas das
  outras cinco armas continuam no formato 1 até a 4.1c/4.1d; a biblioteca lê os dois.
- **D11 — Saídas.** `assets/armas/ak47/` entra no git (produto do script, regenerável); o `.blend` e os renders vão para
  `tools/blender/conferencia/ak47/` (fora do git, já no `.gitignore`).
- **D12 — Peças móveis da AK.** `ferrolho` (transportador com a alavanca de manejo e a cabeça do ferrolho que aparece na
  janela; desliza em −X), `carregador` (gira na trava dianteira do poço), `gatilho` (gira no pino do gatilho), `cao`
  (gira no pino do cão; interno) e `seletor` (gira no eixo do seletor). O `extras.eixo` de cada uma diz a direção (a
  4.3 anima por ele).
- **D13 — Lançador.** `construir` e `validar <id|todas>` valem para as armas de `src/data/armasReais.js`; `conferir` e
  `abrir` atendem as duas origens (a de massinha continua pelo caminho da 4.1); `validar <arquivo.js>`, `previa` e
  `ida-volta` continuam só de massinha até a 4.1d. `todas` = todas as armas daquela ação.
- **D14 — Construção incremental.** `construir` pula a arma quando o hash das entradas (os `.py` do pacote, a ficha e os
  dados da arma) é igual ao do relatório gravado e os arquivos existem; `--forcar` refaz.
- **D15 — O que a validação de ponta a ponta deste plano mudou** (as Tarefas 1–17 aplicadas numa cópia descartável,
  a AK construída de verdade pelo `construir`, a suíte com 370 testes passando e a AK carregada na bancada e na pista
  do navegador). Cada item já está no código das tarefas; fica aqui o porquê, para ninguém "simplificar" de volta:
  1. **Malha:** a solda de 0,001 mm depois do chanfro (os chanfros que se encontram na parede de 0,9 mm das cabeças
     de pino e os que tocam as faces de um booleano deixavam 346 faces de área zero); a varredura por transporte
     paralelo e o caminho fechado em anel (as argolas saíam com quads torcidos, que também sobrepunham a UV); o `А`
     cirílico trocado pelo `A` latino e a malha do texto soldada na gravação (a letra saía "–В"); a triangulação das
     peças juntadas (as tangentes).
  2. **Faces escondidas:** só sai a face com todos os cantos e o centro dentro de outra peça e longe da superfície dela
     (apagar pelo centro tirava faces em parte visíveis: a silhueta caía de 98,9 para 97,6 %); cada cópia fica só com o
     material da zona (o booleano deixava o do cortador na lista).
  3. **Assar:** fonte única (uma cópia juntada do modelo alto: o `construir` caiu de 13 min para 77 s), sem limpar a
     imagem antes (o fundo neutro se perdia), 8 bits, ruído dos materiais de fábrica no referencial do objeto com
     período em mm maior que o texel (era ruído de pixel, caro de guardar e sem sentido no jogo), e o resto de D3.
  4. **Jogo:** o filtro de frequência (`fwidth`) nos padrões procedurais do acabamento (o grão de 0,4 mm do oxidado e
     os flocos do metálico cintilariam com o balanço da arma); a planta da receita de massinha pelo caminho que a
     receita aponta (a faca dava um 404 no console); o resumo do `.glb` na ordem do registro (o exportador grava os nós
     em ordem alfabética).

---

## Mapa de arquivos

| Arquivo | Tarefa | Responsabilidade |
|---|---|---|
| `tools/regua.html`, `tools/regua/lib.js`, `tools/regua/geometria.js` | 1 | **novos** — a régua (substitui `tools/silhueta.html`, que sai): foto na escala com grade em mm, eixo pelo cano exposto, perfis, contorno, buracos, cores, sobreposição com o render e a saída da ficha |
| `tools/blender/refs/ak47.json` | 1 | ficha no formato 2 (substitui a planta antiga da AK-47 tipo II) |
| `src/weapons/model/ficha.js` | 1 | **novo** — validação da ficha e a conversão ficha → planta (formato 1, em u) |
| `src/data/armasReais.js` | 2 | **novo** — registro das armas realistas, zonas, soquetes por categoria, peças, orçamentos, pintura de fábrica, ponto de reflexo padrão |
| `src/data/acabamentos.js`, `src/data/coresSkin.js`, `src/data/skinsArma.js` | 2 | **novos** — os 15 acabamentos, as 20 cores nomeadas e as três skins de exemplo |
| `src/weapons/skins/acabamento.js`, `src/weapons/skins/skin.js` | 3 | **novos** — acabamento → parâmetros do material (puro); skins de fábrica e nomeadas, validação, argumentos do `skin` |
| `tools/blender/saida.mjs` | 4 | **novo** — leitor do `.glb` (bloco JSON) e do cabeçalho `.webp`, validação da saída contra o registro e o relatório |
| `tools/blender/armas/*.py` | 5–8 | **novos** — `unidades`, `pecas`, `materiais`, `estudio`, `zonas`, `soquetes`, `ak47`, `assar`, `lod`, `validar`, `exportar`, `conferir`, `principal` |
| `tools/blender.mjs` | 1, 8 | a planta pela ficha no contexto de massinha (1); ações `construir`, `validar`, `conferir`, `abrir` para as armas realistas (8; as de massinha pelo caminho da 4.1) |
| `assets/armas/ak47/*` | 8 | **novos** (gerados) — `ak47.glb`, `ak47_n.webp`, `ak47_m.webp`, `ak47_mundo_n.webp`, `ak47_mundo_m.webp`, `ak47.relatorio.json` |
| `tools/vendor.mjs`, `vendor/three/examples/jsm/loaders/GLTFLoader.js`, `…/loaders/DRACOLoader.js`, `…/libs/draco/gltf/` | 9 | exceção para o `GLTFLoader`, o `DRACOLoader`, o que eles importam e o decodificador Draco |
| `tools/dev-server.mjs` | 9 | tipos MIME de `.glb`, `.gltf`, `.bin` e `.webp` |
| `src/weapons/model/glsl/acabamentos.js`, `src/weapons/model/materialArma.js` | 10 | **novos** — o trecho de shader das zonas (padrões procedurais, desgaste, variações) e o material de uma zona |
| `src/weapons/model/glbWeapon.js`, `src/weapons/model/glbSource.js` | 11 | **novos** — resumo e instância do `.glb`; a origem `glb` do serviço (carga com o Draco, texturas, materiais por skin, ambiente) |
| `src/weapons/model/weaponLibrary.js`, `src/core/events.js`, `src/main.js` | 11 | duas origens, `info`/`describe`, níveis por origem, `skinOf`/`setSkin`, `setEnvironment`; `phase: 'skin'` |
| `src/render/setReflection.js` | 12 | **novo** — captura do reflexo do set (PMREM de uma câmera cúbica no mapa) |
| `src/data/sandbox.js`, `src/data/pista.js`, `src/data/arsenal.js` | 12, 14 | ponto `reflexo` de cada mapa; direções de explodir de `cao` e `seletor` |
| `src/maps/testRoom.js`, `src/maps/pista/index.js`, `src/maps/arsenal/index.js`, `src/maps/registry.js` | 12, 14 | o ponto do reflexo no mapa montado (`reflection`); na bancada, a pré-compilação e a troca de skin |
| `src/modes/matchState.js` | 12, 13 | captura, recaptura e descarte do reflexo; `hasModel` |
| `src/weapons/viewmodel/viewmodel.js`, `src/weapons/viewmodel/placement.js` | 13 | `info` no lugar da receita; arma sem mãos; troca de skin |
| `src/maps/arsenal/bench.js`, `panel.js`, `turntable.js`, `planSheets.js` | 1, 14 | a planta pela ficha (1); bancada pelas duas origens (14): caixa, suporte por raios, planta de `info`, sobreposição, medir pelo relatório, peças móveis, soquetes, skins de acabamento, nível `longe` |
| `src/debug/weaponCommands.js` | 15 | comando `skin`; `armas` com a origem; `arma` com a mensagem nova |
| `src/data/armas/ak47.js`, `src/data/armas/index.js` | 16 | a receita de massinha da AK sai do registro e do disco |
| `tests/*.test.js` | 1–16 | **novos:** `fichaArma`, `regua`, `skinsArma`, `armasSaida`, `armaAk47`, `vendorGltf`, `materialArma`, `weaponLibraryGlb`, `setReflection`, `arsenalStand`, `skinCommand`; **ajustados:** `weaponRecipes`, `viewmodel` |
| `CLAUDE.md.md`, `CLAUDE.md`, `docs/phases/phase-4.md`, `docs/PROGRESS.md`, memória | 17 | exceção das regras 3 e 4, seções 0.7, 0.12, 0.13 e 0.15, Fases 4, 5 e 11; subfases novas; relatório da 4.1a |
| `docs/phases/phase-4.1a-plan.md` | 19 | **novo** — o plano com código completo, gerado do diff |

---

### Tarefa 0: Cópias de trabalho, servidor e contagem de partida

**Files:**
- Create: `game tiro/base-4.1a/`, `game tiro/trabalho-4.1a/` (fora do repositório)
- Modify: `game tiro/.claude/launch.json` (entrada temporária, sai na Tarefa 19)

- [ ] **Passo 1: Criar as duas cópias** (arquivos versionados e os não ignorados — a 3.5, a 4.1 e os documentos do
  redesenho estão sem commit —, mais o `node_modules` e o `local.json` do Blender, que ficam fora do git):

```bash
cd "/c/Users/T-Gamer/Desktop/game tiro/Game tiro"
for d in base-4.1a trabalho-4.1a; do
  rm -rf "../$d" && mkdir "../$d"
  git ls-files -co --exclude-standard -z | xargs -0 cp --parents -t "../$d"
  cp -r node_modules "../$d/"
  cp tools/blender/local.json "../$d/tools/blender/"
done
ls ../base-4.1a ../trabalho-4.1a
```

Expected: as duas pastas com `index.html`, `src/`, `tools/`, `tests/`, `docs/`, `vendor/`, `node_modules/`.

- [ ] **Passo 2: Contagem de partida nas duas cópias**

Run: `cd "/c/Users/T-Gamer/Desktop/game tiro/trabalho-4.1a" && npm test 2>&1 | tail -8`
Expected: `# tests 328` e `# fail 0` (o mesmo na `base-4.1a`).

- [ ] **Passo 3: Servir a cópia de trabalho** — acrescentar em `game tiro/.claude/launch.json`, dentro de
  `configurations`, a entrada abaixo (sai na Tarefa 19) e abrir pelo painel com `preview_start {name: "massacre-trabalho"}`:

```json
    {
      "name": "massacre-trabalho",
      "runtimeExecutable": "node",
      "runtimeArgs": ["trabalho-4.1a/tools/dev-server.mjs", "5176"],
      "port": 5176
    }
```

- [ ] **Passo 4: Ferramentas do plano** — as de `prova-armas-2026-09-26/ferramentas-plano/` (as da 4.1: `plan-gen.mjs`,
  `pairs.mjs`, `validate-plan.mjs`, `extract-plan.mjs`, `crlf.mjs`, `eol.mjs`, `cmp.mjs`, `compara.mjs`, `sonda.mjs`,
  `tarefas.mjs`) recebem os caminhos pela linha de comando; os modelos `texto-*.md` são da 4.1 e são reescritos para a
  4.1a na Tarefa 19. Nada a fazer agora além de conferir que existem:

Run: `ls "/c/Users/T-Gamer/Desktop/game tiro/prova-armas-2026-09-26/ferramentas-plano"`
Expected: os dez `.mjs` e os quatro `texto-*.md`.

---

### Tarefa 1: Ficha da AK-47 tipo 3 e a régua

**Files:**
- Create: `tools/regua/geometria.js`, `tools/regua/lib.js`, `tools/regua.html`, `src/weapons/model/ficha.js`
- Create: `tests/regua.test.js`, `tests/fichaArma.test.js`
- Modify (substituir inteiro): `tools/blender/refs/ak47.json`
- Modify: `tests/weaponRecipes.test.js`, `src/maps/arsenal/planSheets.js`, `tools/blender.mjs` (os leitores da planta
  aceitam a ficha)
- Delete: `tools/silhueta.html`

A régua substitui a página da silhueta da 4.1 (seção 3.3 do desenho): mesma leitura da foto no canvas e o mesmo
referencial, mais a grade em mm, o eixo pelo cano exposto, os perfis, as cores por região e a saída no formato da
ficha. As contas puras ficam em `geometria.js`, testadas no Node e repetidas em numpy no `validar.py` do Blender
(Tarefa 8). A ficha da AK sai da medição já feita na prova (`refsite/regua/ak47-tipo3.json`) e dos contornos por peça
do `ak_v3.py`, no formato 2.

- [ ] **Passo 1: Testes da geometria da régua**

```js file=tests/regua.test.js
// Contas puras da régua (Fase 4.1a): Chaikin, área e caixa de polígono, rasterização com buracos, dilatação, IoU bruto
// e com a tolerância de raio r, perfis de cima e de baixo. Os números são conferíveis à mão.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { areaPoligono, caixaDoPoligono, chaikin, dilatar, iou, perfis, rasterizar } from '../tools/regua/geometria.js';

const QUADRADO = [[0, 0], [10, 0], [10, 10], [0, 10]];

test('régua: área com sinal, caixa e Chaikin (um corte tira 1/8 da área do quadrado)', () => {
  assert.equal(areaPoligono(QUADRADO), 100);
  assert.equal(areaPoligono([...QUADRADO].reverse()), -100);
  assert.deepEqual(caixaDoPoligono(QUADRADO), { x0: 0, y0: 0, x1: 10, y1: 10 });
  const suave = chaikin(QUADRADO, 1);
  assert.equal(suave.length, 8);
  assert.ok(Math.abs(areaPoligono(suave) - 87.5) < 1e-9);
  assert.equal(chaikin(QUADRADO, 2).length, 16);
});

test('régua: rasterização pelo centro da célula, com buraco', () => {
  const grade = { x0: 0, y1: 10, passo: 1, largura: 10, altura: 10 };
  const cheio = rasterizar([QUADRADO], grade);
  assert.equal(cheio.reduce((a, b) => a + b, 0), 100);
  const buraco = [[2, 2], [5, 2], [5, 5], [2, 5]];
  const vazado = rasterizar([QUADRADO, buraco], grade);
  assert.equal(vazado.reduce((a, b) => a + b, 0), 91);
  // Linha 0 é a de cima (y entre 9 e 10); a célula (3, 6) cobre x 3..4, y 3..4 → dentro do buraco.
  assert.equal(vazado[6 * 10 + 3], 0);
  assert.equal(vazado[0], 1);
});

test('régua: dilatação por disco e IoU com tolerância', () => {
  const L = 20;
  const a = new Uint8Array(L * L);
  const b = new Uint8Array(L * L);
  for (let j = 0; j < 10; j++) {
    for (let i = 0; i < 10; i++) a[j * L + i] = 1;
    for (let i = 1; i < 11; i++) b[j * L + i] = 1;
  }
  const d = dilatar(a, L, L, 1);
  assert.equal(d[0 * L + 10], 1, 'um pixel para a direita');
  assert.equal(d[10 * L + 10], 0, 'a diagonal fica fora do disco de raio 1');
  const r0 = iou(a, b, L, L, 0);
  assert.equal(r0.inter, 90);
  assert.ok(Math.abs(r0.bruto - 90 / 110) < 1e-12);
  assert.equal(r0.tolerancia, r0.bruto, 'sem tolerância as duas contas coincidem');
  const r1 = iou(a, b, L, L, 1);
  assert.equal(r1.tolerancia, 1, 'a diferença de 1 px some com r = 1');
  const longe = new Uint8Array(L * L);
  for (let j = 0; j < 10; j++) for (let i = 3; i < 13; i++) longe[j * L + i] = 1;
  assert.ok(iou(a, longe, L, L, 1).tolerancia < 1, 'deslocamento de 3 px ainda conta com r = 1');
});

test('régua: perfis de cima e de baixo por coluna', () => {
  const L = 4;
  const m = new Uint8Array([0, 1, 0, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0]);
  assert.deepEqual(perfis(m, L, L), { cima: [-1, 0, 1, -1], baixo: [-1, 2, 2, -1] });
});
```

- [ ] **Passo 2: Rodar e ver falhar**

Run: `node --test tests/regua.test.js`
Expected: FAIL — `Cannot find module '.../tools/regua/geometria.js'`.

- [ ] **Passo 3: Implementar a geometria da régua**

```js file=tools/regua/geometria.js
// Contas puras da régua (Fase 4.1a; desenho em docs/superpowers/specs/2026-09-26-armas-realistas-design.md, seção 3.3):
// suavização de contorno lido de foto de baixa resolução (Chaikin), área e caixa de polígono, rasterização de contorno
// com buracos numa grade, dilatação por disco, perfis de cima e de baixo por coluna e a coincidência (IoU) entre duas
// máscaras com a tolerância de raio r (a diferença a até r pixels da outra silhueta não conta: é o ruído do próprio
// contorno). A página tools/regua.html usa no navegador e os testes no Node; tools/blender/armas/validar.py faz as
// mesmas contas em numpy.

/** Chaikin em polígono fechado: cada lado vira dois pontos, a 1/4 e a 3/4. */
export function chaikin(pontos, iteracoes = 1) {
  let pts = pontos;
  for (let k = 0; k < iteracoes; k++) {
    const novo = [];
    for (let i = 0; i < pts.length; i++) {
      const [ax, ay] = pts[i];
      const [bx, by] = pts[(i + 1) % pts.length];
      novo.push([0.75 * ax + 0.25 * bx, 0.75 * ay + 0.25 * by], [0.25 * ax + 0.75 * bx, 0.25 * ay + 0.75 * by]);
    }
    pts = novo;
  }
  return pts;
}

/** Área com sinal (positiva no sentido anti-horário, com +Y para cima). */
export function areaPoligono(pontos) {
  let s = 0;
  for (let i = 0; i < pontos.length; i++) {
    const [ax, ay] = pontos[i];
    const [bx, by] = pontos[(i + 1) % pontos.length];
    s += ax * by - bx * ay;
  }
  return s / 2;
}

export function caixaDoPoligono(pontos) {
  let x0 = Infinity;
  let y0 = Infinity;
  let x1 = -Infinity;
  let y1 = -Infinity;
  for (const [x, y] of pontos) {
    x0 = Math.min(x0, x);
    y0 = Math.min(y0, y);
    x1 = Math.max(x1, x);
    y1 = Math.max(y1, y);
  }
  return { x0, y0, x1, y1 };
}

/**
 * Máscara (1 = dentro) de um contorno com buracos numa grade: a célula (i, j) cobre x ∈ [x0 + i·passo, x0 + (i+1)·passo)
 * e y ∈ [y1 − (j+1)·passo, y1 − j·passo) — a linha 0 fica em cima, como numa imagem. O centro da célula decide, pela
 * paridade dos cruzamentos com todos os anéis.
 * @param {number[][][]} aneis [contorno, ...buracos]
 * @param {{x0:number, y1:number, passo:number, largura:number, altura:number}} grade
 * @returns {Uint8Array}
 */
export function rasterizar(aneis, { x0, y1, passo, largura, altura }) {
  const mascara = new Uint8Array(largura * altura);
  const cruz = [];
  for (let j = 0; j < altura; j++) {
    const y = y1 - (j + 0.5) * passo;
    cruz.length = 0;
    for (const anel of aneis) {
      for (let k = 0; k < anel.length; k++) {
        const [ax, ay] = anel[k];
        const [bx, by] = anel[(k + 1) % anel.length];
        if ((ay > y) !== (by > y)) cruz.push(ax + ((y - ay) / (by - ay)) * (bx - ax));
      }
    }
    cruz.sort((a, b) => a - b);
    for (let k = 0; k + 1 < cruz.length; k += 2) {
      const i0 = Math.max(0, Math.ceil((cruz[k] - x0) / passo - 0.5));
      const i1 = Math.min(largura - 1, Math.floor((cruz[k + 1] - x0) / passo - 0.5));
      for (let i = i0; i <= i1; i++) mascara[j * largura + i] = 1;
    }
  }
  return mascara;
}

/** Dilatação da máscara por um disco de raio r pixels (r = 0 devolve uma cópia). */
export function dilatar(mascara, largura, altura, r) {
  if (r <= 0) return mascara.slice();
  const out = new Uint8Array(mascara.length);
  const offs = [];
  for (let dy = -r; dy <= r; dy++) for (let dx = -r; dx <= r; dx++) if (dx * dx + dy * dy <= r * r) offs.push([dx, dy]);
  for (let j = 0; j < altura; j++) {
    for (let i = 0; i < largura; i++) {
      if (!mascara[j * largura + i]) continue;
      for (const [dx, dy] of offs) {
        const x = i + dx;
        const y = j + dy;
        if (x >= 0 && y >= 0 && x < largura && y < altura) out[y * largura + x] = 1;
      }
    }
  }
  return out;
}

/**
 * Coincidência entre duas máscaras do mesmo tamanho. Bruta: |A∩B| / |A∪B|. Com tolerância r: o pixel de A fora de B que
 * está a até r pixels de B não conta (e o de B fora de A a até r de A): |A∩B| / (|A∩B| + a diferença que conta).
 * @returns {{bruto:number, tolerancia:number, inter:number, soA:number, soB:number}}
 */
export function iou(a, b, largura, altura, r = 0) {
  const da = r > 0 ? dilatar(a, largura, altura, r) : a;
  const db = r > 0 ? dilatar(b, largura, altura, r) : b;
  let inter = 0;
  let soA = 0;
  let soB = 0;
  let contaA = 0;
  let contaB = 0;
  for (let k = 0; k < a.length; k++) {
    if (a[k] && b[k]) inter++;
    else if (a[k]) {
      soA++;
      if (!db[k]) contaA++;
    } else if (b[k]) {
      soB++;
      if (!da[k]) contaB++;
    }
  }
  return {
    bruto: inter / (inter + soA + soB || 1),
    tolerancia: inter / (inter + contaA + contaB || 1),
    inter, soA, soB,
  };
}

/** Primeira (cima) e última (baixo) linha com 1 em cada coluna; −1 na coluna vazia. */
export function perfis(mascara, largura, altura) {
  const cima = new Array(largura).fill(-1);
  const baixo = new Array(largura).fill(-1);
  for (let i = 0; i < largura; i++) {
    for (let j = 0; j < altura; j++) {
      if (!mascara[j * largura + i]) continue;
      if (cima[i] < 0) cima[i] = j;
      baixo[i] = j;
    }
  }
  return { cima, baixo };
}
```

- [ ] **Passo 4: Rodar e ver passar**

Run: `node --test tests/regua.test.js`
Expected: PASS (4 testes).

- [ ] **Passo 5: A página da régua** — `tools/regua/lib.js` (as funções da `tools/silhueta.html` da 4.1
  exportadas — `sourceInfo`, `loadImage`, `weaponMask`, `largestComponent`, `traceLoops`, `area`, `simplify` —, como
  a `refsite/regua/lib.js` da prova, com o cabeçalho):

```js file=tools/regua/lib.js
// Leitura da foto no canvas para a régua (Fase 4.1a; vem da tools/silhueta.html da 4.1): informação do arquivo no
// Commons (licença, autor, miniatura na largura ?largura=), máscara da arma (transparência ou fundo ligado à borda com o
// limiar ?limiar=), maior componente, contornos por marching squares, área e simplificação (Douglas-Peucker).
const P0 = new URLSearchParams(location.search);
const WIDTH = Number(P0.get('largura') || 4000);
const THRESHOLD = Number(P0.get('limiar') || 48);
const HOLE_MIN = Number(P0.get('buraco') || 0.004);
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

export { sourceInfo, loadImage, weaponMask, largestComponent, traceLoops, area, simplify };
```

E a página:

```html file=tools/regua.html
<!doctype html>
<html lang="pt-BR">
<meta charset="utf-8">
<title>Régua de fidelidade — MASSACRE</title>
<style>
  body { margin: 0; background: #1f1a18; color: #F6F0E4; font: 12px system-ui, sans-serif; }
  #info, #ferramentas { padding: 6px 8px; color: #E8D9A8; }
  #ferramentas button { margin-right: 6px; }
  canvas { display: block; margin: 4px 0 14px; cursor: crosshair; }
  pre { margin: 0 8px 12px; padding: 8px; background: #2A2320; max-height: 40vh; overflow: auto; }
</style>
<div id="info">carregando…</div>
<div id="ferramentas">
  <button id="fechar" type="button">Fechar peça</button>
  <button id="linha" type="button">Guardar linha aberta</button>
  <button id="desfazer" type="button">Desfazer ponto</button>
  <button id="limpar" type="button">Limpar pontos</button>
  <button id="copiar" type="button">Copiar JSON</button>
  <span id="pontos">0 pontos</span>
</div>
<pre id="saida"></pre>
<div id="faixas"></div>
<script type="module">
// Régua de fidelidade (Fase 4.1a; desenho em docs/superpowers/specs/2026-09-26-armas-realistas-design.md, seção 3.3).
// A foto do Commons é lida só no canvas (nada vai para o disco); a escala sai do comprimento oficial (?mm=); boca do
// cano em x = 0 e eixo do cano em y = 0 pelo centro do cano exposto (?eixox=a,b em mm; sem ele, o meio da boca, que
// erra quando a boca tem quebra-chamas oblíquo); grade em mm (linhas a cada 10, rótulos a cada 50) em faixas ampliadas
// (?pxmm= e ?faixa=); perfis de cima e de baixo a cada mm; contorno e buracos simplificados; média de cor por retângulo
// em mm (?cores=nome:x0,y0,x1,y1;…, só os pixels da arma); clique nas faixas para marcar o contorno de uma peça. A saída
// é o JSON no formato da ficha, para completar (medidas oficiais com a fonte, correção de cor) e gravar em
// tools/blender/refs/<id>.json. Exemplo:
//   tools/regua.html?arma=ak47&arquivo=File:AK-47%20assault%20rifle.jpg&mm=870&eixox=-130,-80
import { sourceInfo, loadImage, weaponMask, largestComponent, traceLoops, area, simplify } from './regua/lib.js';

const P = new URLSearchParams(location.search);
const ARMA = P.get('arma') || 'arma';
const FILE = P.get('arquivo');
const MM = Number(P.get('mm'));
const MIRROR = P.get('espelhar') === '1';
const PX = Number(P.get('pxmm') || 2.8);
const FAIXA = Number(P.get('faixa') || 220);
const info = document.getElementById('info');
const saida = document.getElementById('saida');
const r1 = (v) => Math.round(v * 10) / 10;
const hex2 = (v) => Math.round(v).toString(16).padStart(2, '0');
const srgbParaLinear = (c) => (c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4);

const marcados = { atual: [], pecas: {}, linhas: {} };

async function run() {
  if (!FILE || !(MM > 0)) throw new Error('use ?arquivo=File:… e ?mm=<comprimento oficial>');
  const src = await sourceInfo(FILE);
  const img = await loadImage(src.url);
  const W = img.naturalWidth;
  const H = img.naturalHeight;
  const cv = document.createElement('canvas');
  cv.width = W;
  cv.height = H;
  const g = cv.getContext('2d', { willReadFrequently: true });
  if (MIRROR) {
    g.translate(W, 0);
    g.scale(-1, 1);
  }
  g.drawImage(img, 0, 0);
  g.setTransform(1, 0, 0, 1, 0, 0);
  const pixels = g.getImageData(0, 0, W, H);
  const { mask: raw, mode } = weaponMask(pixels, W, H);
  const mask = largestComponent(raw, W, H);
  const loops = traceLoops(mask, W, H).map((l) => ({ l, a: area(l) }));
  loops.sort((p, q) => Math.abs(q.a) - Math.abs(p.a));
  const outer = loops[0];
  let minX = Infinity;
  let maxX = -Infinity;
  for (const [x] of outer.l) {
    minX = Math.min(minX, x);
    maxX = Math.max(maxX, x);
  }
  const s = MM / (maxX - minX); // mm por pixel da foto
  let top = Infinity;
  let bottom = -Infinity;
  const band = (maxX - minX) * 0.01;
  for (const [x, y] of outer.l) {
    if (x >= maxX - band) {
      top = Math.min(top, y);
      bottom = Math.max(bottom, y);
    }
  }
  let axisY = (top + bottom) / 2;
  let eixo = null;
  if (P.has('eixox')) {
    // Centro da primeira faixa de pixels (de cima) em cada coluna pedida: o cano exposto.
    const [a, b] = P.get('eixox').split(',').map(Number);
    const centros = [];
    for (let xm = a; xm <= b; xm += 2) {
      const px = Math.round(maxX + xm / s);
      let t = -1;
      let e = -1;
      for (let y = 0; y < H; y++) {
        if (mask[y * W + px]) {
          if (t < 0) t = y;
          e = y;
        } else if (t >= 0) break;
      }
      if (t >= 0) centros.push({ c: (t + e) / 2, d: (e - t + 1) * s });
    }
    centros.sort((p, q) => p.c - q.c);
    const med = centros[centros.length >> 1];
    axisY = med.c;
    eixo = { medidoEntreX: [a, b], canoMedidoMM: r1(med.d * 10) / 10, amostras: centros.length };
  }
  const toMM = (x, y) => [(x - maxX) * s, -(y - axisY) * s];
  const perfil = [];
  for (let xm = -MM; xm <= 0; xm += 1) {
    const px = Math.min(W - 1, Math.max(0, Math.round(maxX + xm / s)));
    let t = -1;
    let bt = -1;
    for (let y = 0; y < H; y++) {
      if (mask[y * W + px]) {
        if (t < 0) t = y;
        bt = y;
      }
    }
    if (t >= 0) perfil.push([xm, r1(toMM(px, t)[1]), r1(toMM(px, bt)[1])]);
  }
  const contorno = simplify(outer.l, 1.0).map(([x, y]) => toMM(x, y).map(r1));
  const buracos = loops.slice(1)
    .filter((h) => Math.abs(h.a) > Math.abs(outer.a) * 0.002 && Math.sign(h.a) !== Math.sign(outer.a))
    .map((h) => simplify(h.l, 1.0).map(([x, y]) => toMM(x, y).map(r1)));

  // Média de cor por retângulo (só os pixels da arma), em sRGB e em linear.
  const cores = {};
  for (const item of (P.get('cores') || '').split(';').filter(Boolean)) {
    const [nome, ret] = item.split(':');
    const [x0, y0, x1, y1] = ret.split(',').map(Number);
    const soma = [0, 0, 0];
    const lin = [0, 0, 0];
    let n = 0;
    for (let py = Math.round(axisY - y1 / s); py <= Math.round(axisY - y0 / s); py++) {
      for (let px = Math.round(maxX + x0 / s); px <= Math.round(maxX + x1 / s); px++) {
        if (px < 0 || py < 0 || px >= W || py >= H || !mask[py * W + px]) continue;
        const k = (py * W + px) * 4;
        for (let c = 0; c < 3; c++) {
          soma[c] += pixels.data[k + c];
          lin[c] += srgbParaLinear(pixels.data[k + c] / 255);
        }
        n++;
      }
    }
    if (!n) continue;
    cores[nome] = {
      foto: { srgb: `#${soma.map((v) => hex2(v / n)).join('')}`, linear: lin.map((v) => Math.round((v / n) * 1000) / 1000) },
      pixels: n,
    };
  }

  const ficha = () => ({
    formato: 2,
    arma: ARMA,
    variante: P.get('variante') || '',
    unidade: 'mm',
    referencial: 'boca do cano em x = 0; eixo do cano em y = 0 (centro do cano exposto); +X para a boca, +Y para cima; lado direito da arma',
    fotos: [{
      lado: MIRROR ? 'direito (espelhada)' : 'direito', arquivo: src.file, pagina: src.page, autor: src.artist, licenca: src.license,
      pixels: [W, H], mmPorPixel: Math.round(s * 10000) / 10000, eixo,
    }],
    contorno, buracos, pecas: marcados.pecas, linhas: marcados.linhas, cores,
    medidasDaFoto: {
      comprimento: MM,
      alturaTotal: r1(Math.max(...perfil.map((p) => p[1])) - Math.min(...perfil.map((p) => p[2]))),
    },
    perfil,
  });
  const mostrar = () => {
    saida.textContent = JSON.stringify(ficha(), null, 1);
    document.getElementById('pontos').textContent = `${marcados.atual.length} pontos marcados`;
  };
  window.__ficha = ficha;
  info.textContent = `${src.file} · ${src.license} · ${src.artist} · ${W}×${H} px · ${mode} · 1 px = ${s.toFixed(3)} mm · `
    + `buracos ${buracos.length}${eixo ? ` · cano ${eixo.canoMedidoMM} mm` : ''}`;

  // Faixas ampliadas com a grade; o clique marca um ponto (mm) da peça atual.
  const cont = document.getElementById('faixas');
  const faixas = [];
  for (let x0 = -MM; x0 < 0; x0 += FAIXA) {
    const x1 = Math.min(0, x0 + FAIXA);
    let yMin = Infinity;
    let yMax = -Infinity;
    for (const [xm, t, b] of perfil) {
      if (xm >= x0 && xm <= x1) {
        yMin = Math.min(yMin, b);
        yMax = Math.max(yMax, t);
      }
    }
    yMin = Math.floor((yMin - 12) / 10) * 10;
    yMax = Math.ceil((yMax + 12) / 10) * 10;
    const c = document.createElement('canvas');
    c.width = Math.round((x1 - x0 + 24) * PX);
    c.height = Math.round((yMax - yMin) * PX);
    const q = c.getContext('2d');
    const X = (xm) => (xm - x0 + 12) * PX;
    const Y = (ym) => (yMax - ym) * PX;
    const desenhar = () => {
      q.fillStyle = '#e9e4da';
      q.fillRect(0, 0, c.width, c.height);
      q.imageSmoothingQuality = 'high';
      q.drawImage(cv, maxX + (x0 - 12) / s, axisY - yMax / s, c.width / PX / s, c.height / PX / s, 0, 0, c.width, c.height);
      for (let xm = Math.ceil((x0 - 12) / 10) * 10; xm <= x1 + 12; xm += 10) {
        const major = xm % 50 === 0;
        q.strokeStyle = major ? 'rgba(0,120,255,0.75)' : 'rgba(0,120,255,0.28)';
        q.lineWidth = major ? 1.2 : 0.7;
        q.beginPath();
        q.moveTo(X(xm) + 0.5, 0);
        q.lineTo(X(xm) + 0.5, c.height);
        q.stroke();
        if (major) {
          q.fillStyle = '#0050d0';
          q.font = 'bold 12px system-ui';
          q.fillText(String(xm), X(xm) + 2, 12);
        }
      }
      for (let ym = yMin; ym <= yMax; ym += 10) {
        const major = ym % 50 === 0;
        q.strokeStyle = ym === 0 ? 'rgba(255,40,40,0.9)' : major ? 'rgba(0,160,80,0.75)' : 'rgba(0,160,80,0.28)';
        q.lineWidth = ym === 0 || major ? 1.2 : 0.7;
        q.beginPath();
        q.moveTo(0, Y(ym) + 0.5);
        q.lineTo(c.width, Y(ym) + 0.5);
        q.stroke();
        if (major || ym === 0) {
          q.fillStyle = '#007a3c';
          q.font = 'bold 12px system-ui';
          q.fillText(String(ym), 2, Y(ym) - 2);
        }
      }
      // Pontos da peça atual e das guardadas que caem nesta faixa.
      const riscar = (pts, cor, fechar) => {
        if (!pts.length) return;
        q.strokeStyle = cor;
        q.fillStyle = cor;
        q.lineWidth = 1.5;
        q.beginPath();
        pts.forEach(([xm, ym], i) => (i ? q.lineTo(X(xm), Y(ym)) : q.moveTo(X(xm), Y(ym))));
        if (fechar) q.closePath();
        q.stroke();
        for (const [xm, ym] of pts) q.fillRect(X(xm) - 2, Y(ym) - 2, 4, 4);
      };
      for (const pts of Object.values(marcados.pecas)) riscar(pts, 'rgba(210,54,47,0.9)', true);
      for (const pts of Object.values(marcados.linhas)) riscar(pts, 'rgba(242,143,59,0.9)', false);
      riscar(marcados.atual, 'rgba(108,63,181,0.95)', false);
    };
    c.addEventListener('click', (ev) => {
      const r = c.getBoundingClientRect();
      const xm = x0 - 12 + (ev.clientX - r.left) / PX;
      const ym = yMax - (ev.clientY - r.top) / PX;
      marcados.atual.push([r1(xm), r1(ym)]);
      for (const f of faixas) f();
      mostrar();
    });
    faixas.push(desenhar);
    desenhar();
    const h = document.createElement('div');
    h.textContent = `faixa x ${x0} … ${x1} mm, y ${yMin} … ${yMax} mm`;
    cont.appendChild(h);
    cont.appendChild(c);
  }
  const guardar = (onde) => {
    if (marcados.atual.length < 2) return;
    const nome = prompt('Nome (sem acento, camelCase):');
    if (!nome) return;
    marcados[onde][nome] = marcados.atual;
    marcados.atual = [];
    for (const f of faixas) f();
    mostrar();
  };
  document.getElementById('fechar').onclick = () => guardar('pecas');
  document.getElementById('linha').onclick = () => guardar('linhas');
  document.getElementById('desfazer').onclick = () => {
    marcados.atual.pop();
    for (const f of faixas) f();
    mostrar();
  };
  document.getElementById('limpar').onclick = () => {
    marcados.atual = [];
    for (const f of faixas) f();
    mostrar();
  };
  document.getElementById('copiar').onclick = () => navigator.clipboard.writeText(saida.textContent);
  mostrar();
  window.__pronto = true;
}
run().catch((err) => {
  info.textContent = `erro: ${err.message}`;
  window.__pronto = true;
});
</script>
</html>
```

- [ ] **Passo 6: Tirar a página antiga**

```bash
cd "/c/Users/T-Gamer/Desktop/game tiro/trabalho-4.1a" && rm tools/silhueta.html
```

- [ ] **Passo 7: Testes da ficha**

```js file=tests/fichaArma.test.js
// Ficha de fidelidade no formato 2 (Fase 4.1a; desenho, seção 3.1): a da AK-47 tipo 3 é válida, o contorno bate com as
// medidas, as peças cabem no contorno e a conversão para a planta da 4.1 (u, relativo à boca) — que a bancada desenha —
// é exata. A cor de fábrica × a pintura de fábrica do registro fica em tests/skinsArma.test.js (Tarefa 2).
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { MEDIDAS_CHAVE, MM_POR_U, fichaParaPlanta, plantaDoArquivo, problemasDaFicha, validarFicha } from '../src/weapons/model/ficha.js';
import { areaPoligono, caixaDoPoligono } from '../tools/regua/geometria.js';

const ficha = JSON.parse(readFileSync(new URL('../tools/blender/refs/ak47.json', import.meta.url), 'utf8'));

test('ficha da AK-47 tipo 3: formato 2, válida, cinco medidas-chave com fonte e a foto do lado direito', () => {
  assert.deepEqual(problemasDaFicha(ficha), []);
  assert.equal(ficha.arma, 'ak47');
  assert.match(ficha.variante, /tipo 3/);
  for (const m of MEDIDAS_CHAVE) assert.ok(ficha.medidas[m].mm > 0 && ficha.medidas[m].fonte.length > 3, m);
  assert.equal(ficha.medidas.comprimento.mm, 870);
  assert.equal(ficha.medidas.cano.mm, 415);
  const foto = ficha.fotos.find((f) => f.lado === 'direito');
  assert.equal(foto.arquivo, 'File:AK-47 assault rifle.jpg');
  assert.equal(foto.licenca, 'Domínio público');
  assert.equal(foto.mmPorPixel, 1.018);
});

test('ficha da AK: contorno com a boca em x = 0, comprimento e altura das medidas, buracos e peças dentro', () => {
  const c = caixaDoPoligono(ficha.contorno);
  assert.ok(Math.abs(c.x1) <= 0.5, 'boca em x = 0');
  assert.ok(Math.abs((c.x1 - c.x0) - 870) <= 870 * 0.005, `comprimento ${c.x1 - c.x0}`);
  assert.ok(Math.abs((c.y1 - c.y0) - ficha.medidas.alturaComCarregador.mm) <= 1, 'altura com o carregador');
  assert.ok(Math.abs(areaPoligono(ficha.contorno)) > 40000, 'área de um fuzil de lado (mm²)');
  for (const b of ficha.buracos) {
    const cb = caixaDoPoligono(b);
    assert.ok(cb.x0 >= c.x0 && cb.x1 <= c.x1 && cb.y0 >= c.y0 && cb.y1 <= c.y1);
  }
  for (const [nome, anel] of Object.entries(ficha.pecas)) {
    const cp = caixaDoPoligono(anel);
    assert.ok(cp.x0 >= c.x0 - 1 && cp.x1 <= c.x1 + 1 && cp.y0 >= c.y0 - 1 && cp.y1 <= c.y1 + 1, nome);
  }
  for (const nome of ['coronha', 'soleira', 'receptor', 'tampa', 'punho', 'carregador', 'guardaMaoSuperior', 'guardaMaoInferior', 'torreMassa']) {
    assert.ok(ficha.pecas[nome], `peça ${nome}`);
  }
});

test('ficha → planta: pontos em u relativos à boca, comprimento em u e a fonte', () => {
  const p = fichaParaPlanta(ficha);
  assert.equal(p.weapon, 'ak47');
  assert.ok(Math.abs(p.lengthU - 870 / MM_POR_U) < 1e-12);
  assert.equal(p.points.length, ficha.contorno.length);
  assert.deepEqual(p.points[0], [ficha.contorno[0][0] / MM_POR_U, ficha.contorno[0][1] / MM_POR_U]);
  assert.equal(p.holes.length, ficha.buracos.length);
  assert.equal(p.source.license, 'Domínio público');
  assert.deepEqual(plantaDoArquivo(ficha), p);
  const antiga = { weapon: 'glock', points: [[0, 0], [1, 0], [1, 1]], holes: [], lengthU: 7.3 };
  assert.equal(plantaDoArquivo(antiga), antiga, 'a planta da 4.1 (formato 1) passa como está');
});

test('ficha: cada problema aparece com o campo', () => {
  const ruim = structuredClone(ficha);
  ruim.formato = 1;
  delete ruim.medidas.cano.fonte;
  ruim.fotos = ruim.fotos.map((f) => ({ ...f, lado: 'esquerdo' }));
  ruim.contorno = ruim.contorno.map(([x, y]) => [x - 20, y]);
  const p = problemasDaFicha(ruim);
  assert.ok(p.some((m) => m.startsWith('formato')));
  assert.ok(p.some((m) => m.startsWith('medidas.cano.fonte')));
  assert.ok(p.some((m) => m.includes('lado direito')));
  assert.ok(p.some((m) => m.includes('x = 0')));
  assert.throws(() => validarFicha(ruim), /ficha de ak47 inválida/);
});
```

- [ ] **Passo 8: Rodar e ver falhar**

Run: `node --test tests/fichaArma.test.js`
Expected: FAIL — `Cannot find module '.../src/weapons/model/ficha.js'`.

- [ ] **Passo 9: Implementar a ficha**

```js file=src/weapons/model/ficha.js
// Ficha de fidelidade de uma arma realista (Fase 4.1a; desenho em docs/superpowers/specs/2026-09-26-armas-realistas-
// design.md, seção 3.1): tools/blender/refs/<id>.json no formato 2 — a variante real, as medidas oficiais com a fonte,
// as fotos do Commons (a do lado direito é obrigatória: é o lado do viewmodel), o contorno geral, os buracos, os
// contornos por peça e as linhas abertas em milímetros no referencial da foto (boca do cano em x = 0, eixo do cano em
// y = 0, +X para a boca, +Y para cima), os pontos nomeados e as cores medidas com a correção de exposição. Aqui: a
// validação (o Node confere antes de o Blender construir) e a conversão para a planta da 4.1 (formato 1: pontos em u
// relativos à boca), que a bancada desenha na folha quadriculada e sobrepõe à arma.

export const MM_POR_U = 25.4;
export const MEDIDAS_CHAVE = Object.freeze(['comprimento', 'cano', 'raioDeMira', 'alturaSemCarregador', 'alturaComCarregador']);
const HEX = /^#[0-9A-F]{6}$/;

const anelValido = (anel) => Array.isArray(anel) && anel.length >= 2
  && anel.every((p) => Array.isArray(p) && p.length === 2 && p.every(Number.isFinite));

/**
 * Confere a ficha (formato 2).
 * @param {object} ficha
 * @returns {string[]} os problemas (vazio = válida)
 */
export function problemasDaFicha(ficha) {
  const p = [];
  const exigir = (cond, msg) => {
    if (!cond) p.push(msg);
  };
  exigir(ficha?.formato === 2, 'formato precisa ser 2');
  exigir(typeof ficha?.arma === 'string' && /^[a-z0-9]+$/.test(ficha.arma), 'arma: o id em minúsculas');
  exigir(typeof ficha?.variante === 'string' && ficha.variante.length > 3, 'variante: o nome da variante real');
  exigir(ficha?.unidade === 'mm', 'unidade precisa ser "mm"');
  for (const m of MEDIDAS_CHAVE) {
    const d = ficha?.medidas?.[m];
    exigir(Boolean(d) && Number.isFinite(d.mm) && d.mm > 0, `medidas.${m}.mm: número positivo`);
    exigir(Boolean(d) && typeof d.fonte === 'string' && d.fonte.length > 3, `medidas.${m}.fonte: de onde veio o número`);
  }
  const fotos = Array.isArray(ficha?.fotos) ? ficha.fotos : [];
  exigir(fotos.some((f) => f.lado === 'direito'), 'fotos: a do lado direito é obrigatória');
  fotos.forEach((f, i) => {
    for (const k of ['arquivo', 'pagina', 'autor', 'licenca']) exigir(typeof f[k] === 'string' && f[k].length > 0, `fotos[${i}].${k}`);
    exigir(Number.isFinite(f.mmPorPixel) && f.mmPorPixel > 0, `fotos[${i}].mmPorPixel`);
  });
  exigir(anelValido(ficha?.contorno) && ficha.contorno.length >= 3, 'contorno: polígono com 3 pontos ou mais');
  (ficha?.buracos ?? []).forEach((b, i) => exigir(anelValido(b) && b.length >= 3, `buracos[${i}]: polígono`));
  for (const [nome, anel] of Object.entries(ficha?.pecas ?? {})) exigir(anelValido(anel) && anel.length >= 3, `pecas.${nome}: polígono`);
  for (const [nome, linha] of Object.entries(ficha?.linhas ?? {})) exigir(anelValido(linha), `linhas.${nome}: polilinha`);
  for (const [nome, c] of Object.entries(ficha?.cores ?? {})) {
    exigir(HEX.test(c?.fabrica ?? ''), `cores.${nome}.fabrica: "#RRGGBB" maiúsculo`);
    exigir(c?.foto === null || HEX.test(c?.foto?.srgb ?? ''), `cores.${nome}.foto: null ou {srgb, linear}`);
    exigir(typeof c?.correcao === 'string' && c.correcao.length > 3, `cores.${nome}.correcao: como a cor da foto virou a de fábrica`);
  }
  if (anelValido(ficha?.contorno) && ficha.contorno.length >= 3) {
    const xs = ficha.contorno.map((q) => q[0]);
    const x1 = Math.max(...xs);
    exigir(Math.abs(x1) <= 0.5, `contorno: a boca (x máximo, ${x1}) precisa estar em x = 0`);
    const alvo = ficha?.medidas?.comprimento?.mm;
    const comprimento = x1 - Math.min(...xs);
    exigir(!alvo || Math.abs(comprimento - alvo) / alvo <= 0.005,
      `contorno: comprimento ${comprimento.toFixed(1)} mm longe do oficial (${alvo} mm)`);
  }
  return p;
}

/** Lança com a lista de problemas; devolve a ficha quando está boa. */
export function validarFicha(ficha) {
  const p = problemasDaFicha(ficha);
  if (p.length) throw new Error(`ficha de ${ficha?.arma ?? '?'} inválida:\n  ${p.join('\n  ')}`);
  return ficha;
}

/**
 * A planta no formato 1 (a da 4.1: pontos em u relativos à boca) tirada da ficha.
 * @returns {{weapon:string, lengthU:number, points:number[][], holes:number[][][], source:object}}
 */
export function fichaParaPlanta(ficha) {
  const u = ([x, y]) => [x / MM_POR_U, y / MM_POR_U];
  const direita = ficha.fotos.find((f) => f.lado === 'direito');
  return {
    weapon: ficha.arma,
    lengthU: ficha.medidas.comprimento.mm / MM_POR_U,
    points: ficha.contorno.map(u),
    holes: (ficha.buracos ?? []).map((b) => b.map(u)),
    source: { file: direita.arquivo, page: direita.pagina, license: direita.licenca, artist: direita.autor },
  };
}

/** A planta de um arquivo de tools/blender/refs/: a ficha (formato 2) vira planta; a planta da 4.1 passa como está. */
export function plantaDoArquivo(json) {
  return json?.formato === 2 ? fichaParaPlanta(validarFicha(json)) : json;
}
```

- [ ] **Passo 10: A ficha da AK-47 tipo 3** — substituir `tools/blender/refs/ak47.json` inteiro. Os números vêm da
  medição da prova (régua sobre a foto, 1,018 mm/px, eixo pelo cano exposto entre x = −130 e −80) e dos contornos por
  peça do `ak_v3.py`; a porca da boca vai até x = 0 (no `ak_v3.py` parava em −1) e o cano começa na face da câmara, 415
  mm atrás da coroa.

```json file=tools/blender/refs/ak47.json
{
 "formato": 2,
 "arma": "ak47",
 "variante": "AK-47 tipo 3 (receptor fresado, coronha fixa de madeira)",
 "unidade": "mm",
 "referencial": "boca do cano em x = 0; eixo do cano em y = 0 (centro do cano exposto medido entre x = -130 e -80); +X para a boca, +Y para cima; lado direito da arma",
 "notas": [
  "Revisão da 4.1a (régua a 6 px/mm e mapa de pixels da foto): o entalhe da alça é a lâmina da ponta de trás da folha, não o vão até o cursor (ver medidas.raioDeMira).",
  "Alça conferida na foto de perto 'File:AK47-rear-sight.jpg' (Erik Gregg, CC BY-SA 2.0): o disco escuro de -391 a -383 é o botão de trava do cursor (na posição de combate, logo à frente da lâmina); o ressalto de -356 a -350 fica nas bochechas da base, em volta do eixo da folha (eixoFolha); a peça que a prova chamava de cursor é essa bochecha.",
  "Torre da massa: a janela (vazada na foto) fica logo acima do cano, de x -37 a -21,5 e y 14,5 a 24, e entrou nos buracos; o tambor do poste aparece de lado como um círculo de raio 4,6 em (-25,5; 34).",
  "Guarda-mãos: a faixa escura entre eles (y 14 a 17,5) é o tubo de gases à mostra, em sombra (a foto não vaza ali): o de baixo sobe até 14, o de cima começa em 17,5 e o tubo de gases vai da alça (x -330) ao bloco de gases.",
  "Carregador: as bordas de trás e da frente são arcos concêntricos (centro (-243,6; -7,05), raios 251,59 e 184,83 mm) ajustados aos pontos da foto (resíduo máximo 1,57 e 0,8 mm, do tamanho de 1 px da foto): a ondulação do contorno lido era ruído da foto, e a chapa estampada tem a borda lisa.",
  "Revisão da 4.1a (2026-09-26; régua e mapa de pixels da foto 1, com a foto do tipo II do Armémuseum para as peças pequenas): o receptor sobe até a tampa na região da janela (o lado esquerdo é inteiro; a janela do lado direito é o corte) e a tampa vai até a traseira (x = -634,7); o botão da mola recuperadora fica num rasgo no alto da traseira do receptor (pecas.botaoMola é o perfil de lado dele); embaixo entram a espiga do guarda-mato, o guarda-mato com a perna de trás e o rebordo certos, a caixa do retém com o eixo (pinoRetem) e o retém pendurado; o carregador sobe por dentro do poço; o bloco de gases, a guia da vareta e a base da massa descem até a borda da foto; o colar do guarda-mão (colarGuardaMao) fica na frente da braçadeira; o cano atrás do bloco de gases (15,5 mm) é mais grosso que na frente (14,3 mm); a fenda de respiro do tubo de gases deu lugar às estrias e aos furos de vistaDeCima.detalhes.",
  "As larguras vistas de cima e as peças que só se veem de cima ou de baixo vêm da planta de fábrica soviética, em vistaDeCima (só números derivados, com a fonte).",
  "Revisão r07 da 4.1a (2026-09-26): o modelo renderizado de cima na escala da planta (5,876 px/mm) e sobreposto a ela corrigiu a concordância da espiga (raio 5 na face do receptor), o parafuso dela, o entalhe da tampa, o eixo do seletor, a posição da alavanca de manejo, a serrilha do botão da mola e o bloco em frente à braçadeira (que de cima tem 22,6 → 19,2 mm, e não um colar redondo no cano); o cano volta ao diâmetro medido na foto (15,26 mm à frente do bloco de gases; 16,2 atrás, entre a braçadeira e o bloco).",
  "Revisão r08 da 4.1a (mapa de pixels da foto 1): o receptor desce em rampa até 35,8 mm abaixo do eixo na frente (a ponta do aço sob o guarda-mão de baixo), que começa ali; o tubo de gases entra 0,3 mm na base da alça.",
  "Revisão r09: no mapa de pixels a face de trás do bloco de gases é reta, em x = -147,5, do vão de baixo ao tubo (as bordas dos vãos no contorno são 1 px mais soltas); o tubo de gases entra 1,5 mm no bloco."
 ],
 "medidas": {
  "comprimento": { "mm": 870, "fonte": "Wikipédia, artigo AK-47 (ficha técnica): 870 mm com a coronha fixa" },
  "cano": { "mm": 415, "fonte": "Wikipédia, artigo AK-47 (ficha técnica): cano de 415 mm" },
  "raioDeMira": { "mm": 378, "fonte": "Wikipédia, artigo AK-47 (ficha técnica): raio de mira de 378 mm", "foto": 374.9, "foto2": 378.2, "nota": "conciliado na 4.1a (D5, régua a 6 px/mm): o entalhe fica na lâmina da ponta de trás da folha (borda de trás em x = -401,4, centro em -400,4); o 'V' logo à frente, lido antes como o entalhe (369,9 mm), é o vão até o botão de trava do cursor, como mostra a foto de perto 'File:AK47-rear-sight.jpg' (Erik Gregg, CC BY-SA 2.0). A foto 1 dá 374,9 mm (-0,8 %) e a foto 2 ('File:AK47.jpg', espelhada, 1,438 mm/px) dá 378,2 mm (+0,05 %); as duas diferem 0,9 % entre si, mais que os 0,5 % que trocariam o número da ficha técnica. Decisão do usuário (2026-09-26): o alvo é o 378 da ficha técnica e a geometria segue a foto 1 (374,9 mm, dentro do ±1 %). Alturas: o entalhe e a ponta do poste não aparecem de lado; o entalhe fica 2,3 mm abaixo do topo da lâmina (46,8) e o poste 4,5 mm acima do tambor da massa (topo em 39, visto de lado), e a linha de mira desce 1 mm até a massa (zeragem de combate)" },
  "alturaSemCarregador": { "mm": 199.4, "fonte": "régua sobre a foto: do topo das orelhas da massa (y = 51,9) ao pé do punho (y = -147,5)" },
  "alturaComCarregador": { "mm": 265.6, "fonte": "régua sobre a foto: do topo das orelhas da massa (y = 51,9) à base do carregador (y = -213,7)" }
 },
 "fotos": [
  {
   "lado": "direito",
   "arquivo": "File:AK-47 assault rifle.jpg",
   "pagina": "https://commons.wikimedia.org/wiki/File:AK-47_assault_rifle.jpg",
   "autor": "Ickybicky (en.wikipedia)",
   "licenca": "Domínio público",
   "descricao": "AK-47 Type 3A assault rifle",
   "pixels": [900, 332],
   "mmPorPixel": 1.018,
   "eixo": { "medidoEntreX": [-130, -80], "canoMedidoMM": 15.26 }
  },
  {
   "lado": "esquerdo (espelhada)",
   "arquivo": "File:AK47.jpg",
   "pagina": "https://commons.wikimedia.org/wiki/File:AK47.jpg",
   "autor": "Governo dos EUA (via Olive-Drab.com, 'Rifle AK47 Olive Drab.gif'); sombra removida por PawełMM",
   "licenca": "Domínio público",
   "descricao": "AK-47 tipo 3 de lado (lado esquerdo); só serviu para conciliar o raio de mira (D5)",
   "pixels": [615, 195],
   "mmPorPixel": 1.438,
   "eixo": { "medidoEntreX": [-130, -80], "canoMedidoMM": 15.79 }
  }
 ],
 "contorno": [[-27.5,51.9],[-33.6,49.9],[-35.6,46.8],[-35.6,36.6],[-44.8,18.3],[-47.8,7.1],[-107.9,7.1],[-108.9,9.2],[-115,9.2],[-127.2,15.3],[-135.3,24.4],[-139.4,33.6],[-204.5,33.6],[-216.7,34.6],[-217.8,38.7],[-223.9,39.7],[-252.4,40.7],[-322.6,40.7],[-326.6,39.7],[-328.7,34.6],[-331.7,34.6],[-331.7,40.7],[-333.8,43.8],[-350,43.8],[-350,45.8],[-355.1,45.8],[-356.1,43.8],[-363.3,43.8],[-365.3,40.7],[-366.3,42.7],[-373.4,42.7],[-373.4,40.7],[-374.5,42.7],[-378.5,42.7],[-379.5,40.7],[-379.5,42.7],[-382.6,42.7],[-383.6,45.8],[-389.7,46.8],[-392.8,41.7],[-396.8,40.7],[-397.9,45.8],[-401.9,46.8],[-401.9,39.7],[-398.9,36.6],[-398.9,34.6],[-547.4,33.6],[-607.5,31.5],[-614.6,28.5],[-627.8,16.3],[-632.9,16.3],[-638,7.1],[-638,2],[-642.1,-1],[-642.1,-3.1],[-708.2,-16.3],[-716.4,-16.3],[-728.6,-11.2],[-742.8,-11.2],[-781.5,-17.3],[-805.9,-19.3],[-812,-21.4],[-858.8,-26.5],[-869,-29.5],[-870,-41.7],[-865.9,-58],[-865.9,-65.1],[-858.8,-99.7],[-857.8,-112.9],[-856.8,-117],[-853.7,-120.1],[-838.5,-119.1],[-830.3,-115],[-826.2,-115],[-824.2,-112.9],[-788.6,-101.8],[-786.6,-99.7],[-771.3,-95.6],[-769.3,-93.6],[-759.1,-91.6],[-747.9,-86.5],[-743.8,-86.5],[-741.8,-84.5],[-692.9,-69.2],[-690.9,-67.2],[-680.7,-65.1],[-669.5,-60],[-665.5,-60],[-663.4,-58],[-632.9,-48.8],[-631.9,-46.8],[-627.8,-46.8],[-626.8,-54.9],[-619.7,-65.1],[-618.7,-72.2],[-623.8,-88.5],[-626.8,-92.6],[-628.8,-101.8],[-631.9,-105.8],[-632.9,-111.9],[-638,-122.1],[-638,-132.3],[-629.9,-142.5],[-616.6,-147.5],[-602.4,-147.5],[-596.3,-143.5],[-595.3,-126.2],[-593.2,-124.1],[-589.2,-109.9],[-586.1,-105.8],[-579,-85.5],[-574.9,-79.4],[-573.9,-74.3],[-570.8,-71.2],[-564.7,-68.2],[-563.7,-71.2],[-556.6,-76.3],[-520,-75.3],[-511.8,-74.3],[-510.8,-72.2],[-508.8,-72.2],[-507.8,-66.1],[-501.6,-66.1],[-499.6,-68.2],[-499.6,-79.4],[-497.6,-80.4],[-495.5,-77.3],[-494.5,-64.1],[-490.5,-61.1],[-489.4,-56],[-486.4,-76.3],[-481.3,-91.6],[-478.2,-95.6],[-476.2,-104.8],[-470.1,-115],[-470.1,-118],[-468.1,-119.1],[-465,-128.2],[-463,-129.2],[-462,-133.3],[-455.9,-140.4],[-454.8,-144.5],[-452.8,-145.5],[-448.7,-153.6],[-441.6,-160.8],[-440.6,-164.8],[-436.5,-167.9],[-436.5,-169.9],[-407,-199.4],[-405,-199.4],[-396.8,-208.6],[-392.8,-209.6],[-388.7,-213.7],[-382.6,-213.7],[-380.6,-211.6],[-376.5,-211.6],[-376.5,-208.6],[-371.4,-204.5],[-370.4,-200.5],[-368.4,-199.4],[-368.4,-197.4],[-356.1,-181.1],[-355.1,-177.1],[-352.1,-175],[-351.1,-170.9],[-349,-169.9],[-344.9,-161.8],[-352.1,-155.7],[-357.2,-153.6],[-360.2,-149.6],[-362.2,-149.6],[-381.6,-131.3],[-381.6,-129.2],[-387.7,-124.1],[-387.7,-122.1],[-391.8,-119.1],[-391.8,-117],[-401.9,-103.8],[-404,-97.7],[-406,-96.7],[-413.1,-82.4],[-413.1,-79.4],[-415.2,-77.3],[-415.2,-74.3],[-420.2,-63.1],[-424.3,-46.8],[-423.3,-35.6],[-376.5,-32.6],[-362.2,-39.7],[-351.1,-39.7],[-340.9,-33.6],[-320.5,-27.5],[-225.9,-25.4],[-222.8,-22.4],[-215.7,-23.4],[-213.7,-18.3],[-193.3,-17.3],[-142.5,-17.3],[-141.4,-19.3],[-134.3,-17.3],[-19.3,-18.3],[-18.3,-15.3],[-15.3,-14.2],[-14.2,-8.1],[-1,-7.1],[0,7.1],[-2,9.2],[-8.1,8.1],[-10.2,9.2],[-11.2,13.2],[-15.3,13.2],[-15.3,48.8],[-18.3,51.9]],
 "buracos": [
  [[-515.9,-40.7],[-512.8,-40.7],[-510.8,-61.1],[-510.8,-68.2],[-513.9,-72.2],[-542.4,-74.3],[-553.5,-74.3],[-559.6,-72.2],[-560.7,-65.1],[-558.6,-64.1],[-558.6,-42.7],[-554.6,-42.7],[-554.6,-44.8],[-551.5,-46.8],[-552.5,-51.9],[-549.5,-61.1],[-543.4,-66.1],[-537.3,-67.2],[-546.4,-58],[-546.4,-47.8],[-538.3,-41.7]],
  [[-163.8,14.2],[-148.6,14.2],[-147.5,7.1],[-205.5,7.1],[-205.5,12.2],[-202.5,13.2]],
  [[-107.9,-8.1],[-46.8,-8.1],[-34.6,-9.2],[-33.6,-12.2],[-110.9,-12.2],[-107.9,-10.2]],
  [[-205.5,-9.2],[-147.5,-9.2],[-146.5,-12.2],[-212.7,-13.2],[-212.7,-11.2],[-206.6,-12.2]],
  [[-37,14.5],[-21.5,14.5],[-21.5,24],[-35,24]]
 ],
 "pecas": {
  "coronha": [[-636,0],[-642.1,-1],[-642.1,-3.1],[-708.2,-16.3],[-716.4,-16.3],[-728.6,-11.2],[-742.8,-11.2],[-781.5,-17.3],[-805.9,-19.3],[-812,-21.4],[-858.8,-26.5],[-864,-28.7],[-865,-41.7],[-860.9,-58],[-860.9,-65.1],[-853.8,-99.7],[-852.8,-112.9],[-851.8,-117],[-848.7,-120.1],[-838.5,-119.1],[-830.3,-115],[-824.2,-112.9],[-788.6,-101.8],[-771.3,-95.6],[-759.1,-91.6],[-743.8,-86.5],[-692.9,-69.2],[-680.7,-65.1],[-669.5,-60],[-663.4,-58],[-632.9,-48.8],[-627.8,-46.8],[-627.8,-44],[-636,-44]],
  "soleira": [[-869,-29.5],[-870,-41.7],[-865.9,-58],[-865.9,-65.1],[-858.8,-99.7],[-857.8,-112.9],[-856.8,-117],[-853.7,-120.1],[-848.7,-120.1],[-851.8,-117],[-852.8,-112.9],[-853.8,-99.7],[-860.9,-65.1],[-860.9,-58],[-865,-41.7],[-864,-29.5]],
  "receptor": [[-634.7,13],[-478,13],[-474,18.8],[-399,18.8],[-399,12],[-368,12],[-368,-35.8],[-370,-35.6],[-373,-34.3],[-376.5,-32.6],[-423.3,-35.6],[-424.3,-40.7],[-560,-40.7],[-564,-44],[-630,-44],[-642.1,-42],[-642.1,-1],[-638,2],[-638,7.1]],
  "tampa": [[-399,18.8],[-399,34.6],[-547.4,33.6],[-607.5,31.5],[-614.6,28.5],[-627.8,16.3],[-632.9,16.3],[-634.7,13],[-478,13],[-474,18.8]],
  "botaoMola": [[-638,3],[-638,5.8],[-632.5,14.4],[-627,14.4],[-627,3]],
  "punho": [[-626.6,-50],[-626.8,-54.9],[-619.7,-65.1],[-618.7,-72.2],[-623.8,-88.5],[-626.8,-92.6],[-628.8,-101.8],[-631.9,-105.8],[-632.9,-111.9],[-638,-122.1],[-638,-132.3],[-629.9,-142.5],[-616.6,-147.5],[-602.4,-147.5],[-596.3,-143.5],[-595.3,-126.2],[-593.2,-124.1],[-589.2,-109.9],[-586.1,-105.8],[-579,-85.5],[-574.9,-79.4],[-574.6,-74.3],[-573.2,-72.2],[-572.3,-71.2],[-571,-70.2],[-570.3,-69.2],[-569.3,-68.2],[-568.3,-67.2],[-566.5,-66.1],[-565.5,-65.1],[-564,-64.1],[-561.5,-63.3],[-561.5,-50]],
  "espigaGuardaMato": [[-627.3,-43.5],[-562,-43.5],[-562,-51.6],[-569.2,-51.6],[-569.2,-50.3],[-627.3,-50.3]],
  "guardaMato": [[-569,-40.5],[-569,-51.6],[-562.8,-51.6],[-562.8,-63.4],[-565.3,-65.2],[-565.3,-67],[-564.6,-68.5],[-564.4,-70.2],[-563.6,-71.4],[-562.4,-72.6],[-559.5,-74.6],[-556,-75.3],[-547,-75.2],[-535,-74.8],[-522,-74.6],[-516,-74.2],[-513.5,-73.4],[-511.8,-72.3],[-510.2,-71.3],[-509.4,-70.2],[-508.7,-69],[-508.7,-40.5],[-512,-40.5],[-512,-60],[-512.2,-66],[-512.9,-69.3],[-514.4,-71.3],[-517.5,-72.5],[-524,-73],[-541,-73.1],[-547,-73.5],[-554,-73.6],[-557,-73.2],[-558.6,-72.5],[-559.4,-71.9],[-560.3,-71],[-561.4,-69.6],[-561.5,-68.1],[-562.2,-66.8],[-562.2,-65],[-561.2,-64],[-559.7,-63.3],[-559.7,-42.2],[-555.8,-42.2],[-555.8,-40.5]],
  "caixaRetem": [[-509.5,-40.5],[-491.2,-40.5],[-490.6,-58.4],[-491.8,-61],[-493.6,-62.1],[-494.6,-63.1],[-495.6,-64.2],[-496,-65.6],[-509.5,-65.6]],
  "gatilho": [[-555.5,-40],[-554.6,-44.8],[-551.5,-46.8],[-552.5,-51.9],[-549.5,-61.1],[-543.4,-66.1],[-537.3,-67.2],[-546.4,-58],[-546.4,-47.8],[-540,-40]],
  "retem": [[-502.8,-58.5],[-495.4,-58.5],[-495.4,-65.5],[-495.8,-67.5],[-496.3,-69.5],[-496.7,-72.2],[-497.1,-74.3],[-497.6,-76.3],[-498.1,-78.2],[-498.7,-79.1],[-499.8,-79.2],[-500.7,-78.4],[-500.9,-76.3],[-500.6,-72.2],[-500.4,-68.4],[-501.4,-67.1],[-502.8,-66]],
  "carregador": [[-494.6,-24],[-494,-32],[-493,-40],[-492.5,-44],[-491.8,-48],[-491.1,-52],[-490.3,-56.2],[-489.5,-60.1],[-488.6,-64.1],[-487.7,-68.0],[-486.7,-71.9],[-485.6,-75.8],[-484.5,-79.7],[-483.3,-83.6],[-482.0,-87.4],[-480.7,-91.2],[-479.3,-95.0],[-477.9,-98.8],[-476.4,-102.6],[-474.8,-106.3],[-473.2,-110.0],[-471.5,-113.7],[-469.7,-117.3],[-467.9,-120.9],[-466.1,-124.5],[-464.2,-128.1],[-462.2,-131.6],[-460.2,-135.1],[-458.1,-138.6],[-455.9,-142.0],[-453.7,-145.4],[-451.5,-148.8],[-449.2,-152.1],[-446.8,-155.4],[-444.4,-158.6],[-441.9,-161.8],[-439.4,-165.0],[-436.9,-168.1],[-434.2,-171.2],[-431.6,-174.3],[-428.9,-177.3],[-426.1,-180.2],[-423.3,-183.1],[-420.5,-186.0],[-417.6,-188.8],[-414.6,-191.6],[-411.6,-194.3],[-408.6,-197.0],[-405.5,-199.6],[-402.4,-202.2],[-399.2,-204.7],[-396.0,-207.2],[-392.8,-209.6],[-388.7,-213.7],[-382.6,-213.7],[-380.6,-211.6],[-376.5,-211.6],[-376.5,-208.6],[-371.4,-204.5],[-370.4,-200.5],[-368.4,-199.4],[-356.1,-181.1],[-352.1,-175],[-349,-169.9],[-344.9,-161.8],[-352.6,-156.3],[-355.8,-153.9],[-359.0,-151.4],[-362.1,-148.9],[-365.2,-146.2],[-368.3,-143.5],[-371.2,-140.8],[-374.1,-137.9],[-377.0,-135.0],[-379.7,-132.1],[-382.4,-129.1],[-385.1,-126.0],[-387.7,-122.9],[-390.2,-119.7],[-392.6,-116.4],[-395.0,-113.1],[-397.2,-109.8],[-399.5,-106.4],[-401.6,-103.0],[-403.7,-99.5],[-405.7,-95.9],[-407.6,-92.4],[-409.4,-88.7],[-411.2,-85.1],[-412.8,-81.4],[-414.4,-77.7],[-415.9,-73.9],[-417.3,-70.1],[-418.7,-66.3],[-419.9,-62.4],[-421.1,-58.5],[-422.2,-54.6],[-423.2,-50.7],[-424.1,-46.8],[-424.5,-40],[-426.7,-32],[-427.6,-24]],
  "seletor": [[-582,-8],[-487,9.5],[-481,8],[-480,1],[-486,-1],[-491,3],[-571,-20]],
  "baseAlca": [[-401.9,12],[-401.9,36.6],[-331.7,36.6],[-331.7,12]],
  "folhaAlca": [[-401.9,37],[-401.9,46.8],[-398.3,46.2],[-397,41.2],[-393,41.6],[-383,42.3],[-363.3,43.8],[-350,43.8],[-350,37]],
  "cursorAlca": [[-391.5,37],[-391.5,43.2],[-390.5,43.6],[-384,43.6],[-383,43.2],[-383,37]],
  "bochechasAlca": [[-358,36.6],[-358,43.4],[-356.1,45.8],[-350,45.8],[-349,44],[-333.8,44],[-331.7,40.7],[-331.7,36.6]],
  "guardaMaoSuperior": [[-328.7,17.5],[-328.7,34.6],[-326.6,39.7],[-322.6,40.7],[-252.4,40.7],[-223.9,39.7],[-217.8,38.7],[-216.7,34.6],[-216.7,17.5]],
  "guardaMaoInferior": [[-368,14],[-222.6,14],[-222.6,-25.4],[-225.9,-25.4],[-320.5,-27.5],[-340.9,-33.6],[-351.1,-39.7],[-362.2,-39.7],[-368,-35.8]],
  "bracadeira": [[-225,-24],[-214,-22.4],[-214,12],[-225,12]],
  "bracadeiraTubo": [[-225,12],[-214,12],[-214,36],[-225,36]],
  "colarGuardaMao": [[-214.5,13.9],[-214.5,-9.6],[-214.23,-10.6],[-213.5,-11.33],[-212.5,-11.6],[-208.5,-11.6],[-207.0,-11.2],[-205.9,-10.1],[-205.5,-8.6],[-205.5,13.9]],
  "blocoDeGases": [[-147.5,-12],[-147.5,33.6],[-139.4,33.6],[-135.3,24.4],[-127.2,15.3],[-115,9.2],[-108.9,9.2],[-108.9,-11.2],[-131,-11.3],[-134,-12]],
  "guiaVareta": [[-142.6,-17.9],[-133.5,-17.9],[-133.5,-10],[-142.6,-10]],
  "baseMassa": [[-47.8,7.1],[-44,13.2],[-15.3,13.2],[-11.2,13.2],[-10.2,9.2],[-10.2,-9],[-14.2,-8.1],[-15.3,-14.2],[-18.3,-15.3],[-19.3,-12.6],[-33.4,-12.6],[-33.6,-10.2],[-34.6,-8.9],[-47.8,-8.6]],
  "torreMassa": [[-47.8,7.1],[-44.8,18.3],[-35.6,36.6],[-35.6,46.8],[-33.6,49.9],[-27.5,51.9],[-18.3,51.9],[-15.3,48.8],[-15.3,13.2]],
  "janelaTorre": [[-37,14.5],[-21.5,14.5],[-21.5,24],[-35,24]],
  "orelhaMassa": [[-35.6,30],[-35.6,46.8],[-33.6,49.9],[-27.5,51.9],[-18.3,51.9],[-15.3,48.8],[-15.3,30]]
 },
 "linhas": {
  "carregadorTras": [[-490.3,-56.2],[-489.5,-60.1],[-488.6,-64.1],[-487.7,-68.0],[-486.7,-71.9],[-485.6,-75.8],[-484.5,-79.7],[-483.3,-83.6],[-482.0,-87.4],[-480.7,-91.2],[-479.3,-95.0],[-477.9,-98.8],[-476.4,-102.6],[-474.8,-106.3],[-473.2,-110.0],[-471.5,-113.7],[-469.7,-117.3],[-467.9,-120.9],[-466.1,-124.5],[-464.2,-128.1],[-462.2,-131.6],[-460.2,-135.1],[-458.1,-138.6],[-455.9,-142.0],[-453.7,-145.4],[-451.5,-148.8],[-449.2,-152.1],[-446.8,-155.4],[-444.4,-158.6],[-441.9,-161.8],[-439.4,-165.0],[-436.9,-168.1],[-434.2,-171.2],[-431.6,-174.3],[-428.9,-177.3],[-426.1,-180.2],[-423.3,-183.1],[-420.5,-186.0],[-417.6,-188.8],[-414.6,-191.6],[-411.6,-194.3],[-408.6,-197.0],[-405.5,-199.6],[-402.4,-202.2],[-399.2,-204.7],[-396.0,-207.2],[-392.8,-209.6],[-388.7,-213.7]],
  "carregadorFrente": [[-424.1,-46.8],[-423.2,-50.7],[-422.2,-54.6],[-421.1,-58.5],[-419.9,-62.4],[-418.7,-66.3],[-417.3,-70.1],[-415.9,-73.9],[-414.4,-77.7],[-412.8,-81.4],[-411.2,-85.1],[-409.4,-88.7],[-407.6,-92.4],[-405.7,-95.9],[-403.7,-99.5],[-401.6,-103.0],[-399.5,-106.4],[-397.2,-109.8],[-395.0,-113.1],[-392.6,-116.4],[-390.2,-119.7],[-387.7,-122.9],[-385.1,-126.0],[-382.4,-129.1],[-379.7,-132.1],[-377.0,-135.0],[-374.1,-137.9],[-371.2,-140.8],[-368.3,-143.5],[-365.2,-146.2],[-362.1,-148.9],[-359.0,-151.4],[-355.8,-153.9],[-352.6,-156.3]],
  "baseDoCarregador": [[-388.7,-213.7],[-344.9,-161.8]]
 },
 "tornos": {
  "cano": { "centroY": 0, "perfil": [[-416.5,0],[-416.5,8.2],[-399,8.2],[-150,8.1],[-146,7.65],[-11,7.6],[-11,6.2],[-1.5,6.2],[-1.5,0]] },
  "tuboDeGases": { "centroY": 23.9, "perfil": [[-332,0],[-332,9.7],[-218.5,9.7],[-218,10.7],[-204,9.7],[-146,9.7],[-146,0]] },
  "vareta": { "centroY": -15.1, "perfil": [[-368,0],[-368,2.9],[-19.3,2.9],[-19.3,0]] },
  "porca": { "centroY": 0, "perfil": [[-11,0],[-11,8.4],[-1.2,8.4],[0,7.2],[0,0]] },
  "alma": { "centroY": 0, "perfil": [[-60,0],[-60,3.9],[3,3.9],[3,0]] }
 },
 "pontos": {
  "pinos": [[-551,-33],[-532,-29.4],[-511,-24.4],[-496.5,-29.7],[-485.6,-31.2]],
  "pinoGatilho": [-551,-33],
  "pinoCao": [-532,-29.4],
  "eixoSeletor": [-575,-13.2],
  "manejo": [-402,12],
  "entalheAlca": [-400.4,44.5],
  "eixoFolha": [-353,41.5],
  "posteMassa": [-25.5,43.5],
  "tamborMassa": { "x": -25.5, "y": 34, "raio": 4.6 },
  "travaCarregador": [-424.4,-40.5],
  "pinoRetem": [-501,-57],
  "janela": { "x0": -474, "x1": -405, "y0": 4.5, "y1": 19 },
  "recorteDeAlivio": { "x0": -462, "x1": -377, "y0": -26.8, "y1": -10.6 }
 },
 "vistaDeCima": {
  "fonte": {
   "descricao": "planta de fábrica soviética do AK (vista pela esquerda, vista de cima e vista pela direita, com cotas e notas em russo), achada no Pinterest na busca 'ak 47 top view' em 2026-09-26; o pin não abre sem login e a origem é desconhecida (plantas assim circulam em fóruns russos e europeus, segundo o The Firearm Blog, 'AK-47, AKM/AKMS and AK-74 Blueprints', 2017-04-03)",
   "imagem": "https://i.pinimg.com/originals/e4/bf/e8/e4bfe8574a4eda630145448f0337097b.gif",
   "pixels": [5313,3402],
   "licenca": "desconhecida: lida só no navegador, sem baixar; a ficha guarda só números derivados (medidas em mm), nenhuma imagem",
   "pxPorMm": 5.87,
   "escala": "as cotas da vista de cima — 37 (largura do receptor) e 39 (largura da traseira do guarda-mão de baixo) — dão 5,87 e 5,83 px/mm; o comprimento '878 (для справок)', só para referência, dá 5,90"
  },
  "notas": [
   "Orientação: na vista de cima a boca fica à direita e o lado direito da arma embaixo — a alavanca de manejo e o seletor saem por baixo, e a graduação da folha tem os ímpares embaixo, como na foto de perto da alça (Erik Gregg).",
   "Da planta vêm as larguras e o que só se vê de cima ou de baixo; as posições ao longo do cano e as alturas ficam as da foto 1 (a silhueta validada). A arma da planta tem 878 mm, com a coronha e a porca da boca mais compridas; do receptor à boca as duas batem a menos de ~10 mm, e cada largura vai para a peça correspondente da foto.",
   "A porca da boca da planta (mais comprida, mais larga que alta) não é a da foto: fica a da foto. O cano também segue a foto; a planta o dá 0,5 a 1,5 mm mais grosso.",
   "O tubo de gases tem 17,9 mm de largura na planta e 19,4 de altura na foto: fica oval (a largura da planta, a altura da foto).",
   "Ficaram de fora por falta de identificação segura: uma peça marcada '9' do lado esquerdo da braçadeira (sai 24,8 mm do eixo) e duas abas simétricas de 25,6 mm na frente do bloco de gases, junto do pino transversal.",
   "As estrias e os furos do tubo de gases vêm da vista pela esquerda da planta e da foto 'File:AK-47 type II noBG.png' (Nemo5576, CC BY-SA 4.0; peça do Armémuseum): seis estrias rasas, a 30°, 90° e 150° do alto de cada lado, e quatro furos de cada lado entre a estria de cima e a do meio.",
   "Da vista pela seta A (por baixo do pescoço da coronha) vem a espiga de baixo: lâmina com a ponta de trás redonda, dois parafusos e o bloco da frente sob o receptor; ela e a espiga de cima prendem a coronha. A argola traseira fica por baixo da coronha (marca 'c' da vista pela esquerda), não do lado esquerdo; a foto 1 não mostra nada abaixo da coronha, e a alça fica rebatida."
  ],
  "larguras": {
   "coronha": { "mm": [37.2,32.2], "x": [-860,-645], "nota": "a madeira afina em linha reta da soleira (37,2, um pouco dentro da chapa) ao pescoço (32,2)" },
   "soleira": { "mm": 37.7, "raioDeCima": 36.8, "flecha": 5.2, "nota": "vista de cima a face de trás é um arco: o meio fica 5,2 mm atrás dos cantos" },
   "receptor": { "mm": 37, "nota": "cota 37 da planta" },
   "tampa": { "mm": 37, "topoPlano": 22.8, "nota": "rente ao receptor (a planta admite até 0,2 mm de folga de cada lado); o alto é plano em 22,8 mm e os ombros são arredondados" },
   "baseAlca": { "mm": 22.9 },
   "folhaAlca": { "mm": 14.1 },
   "cursorAlca": { "mm": 26.7, "nota": "sobre os botões de trava" },
   "guardaMaoInferior": { "mm": [39,32.4], "x": [-345,-325], "nota": "39 (cota da planta) no ressalto de trás até x = -345; afina até 32,4 em x = -325 e segue assim até a braçadeira" },
   "guardaMaoSuperior": { "mm": [35.0,32.6], "x": [-328.7,-216.7] },
   "bracadeira": { "mm": 30.8 },
   "colarGuardaMao": { "mm": [22.6,19.2], "labio": [-214.5,-212.1], "concordancia": [-212.1,-207.6], "nota": "o bloco em frente à braçadeira, entre o cano e o tubo de gases (vista pela esquerda da planta): lábio de trás de 22,6 mm e, depois de uma concordância, 19,2 mm até a frente" },
   "tuboDeGases": { "mm": 17.9, "colar": { "x": [-218,-204], "mm": [21.9,17.9] } },
   "blocoDeGases": { "mm": 20.2 },
   "baseMassa": { "mm": 18.7 },
   "torreMassa": { "mm": 15.0, "vao": 11.2, "nota": "as orelhas vistas de cima, com o vão do poste entre elas" }
  },
  "detalhes": {
   "espiga": { "mm": 15.5, "ponta": -679.4, "concordancia": { "raio": 5.0, "face": -642.1 }, "espessura": 3, "nota": "a língua de aço do receptor deitada no pescoço da coronha, embutida rente à madeira, com a ponta redonda; os lados retos entram na face de trás do receptor por uma concordância de raio 5 (medidas a partir da face de trás do receptor da planta, x = -643,3 na planta = -642,1 na foto)" },
   "parafusoEspiga": { "x": -671.4, "diametro": 10.0, "fenda": 1.3, "nota": "vertical, com a cabeça de fenda (a fenda atravessada, de um lado ao outro da espiga) 29,3 mm atrás da face de trás do receptor; atravessa a coronha até a espiga de baixo" },
   "espigaInferior": { "mm": 14.5, "x": [-700,-640], "espessura": 2.5, "parafusos": [-694,-662], "diametroParafuso": 8.5, "bloco": { "x": [-643,-633], "mm": 26 }, "nota": "embutida rente à linha de baixo do pescoço da coronha" },
   "tampaEntalhe": { "x": -634.0, "raio": 14.4, "nota": "o entalhe de trás da tampa, um arco de raio 14,4 com o ápice 12,4 mm à frente da ponta de trás, por onde aparecem o botão da mola recuperadora e o alto do receptor" },
   "botaoMola": { "mm": 10.9, "x": [-638,-627], "serrilha": [-638,-634], "ranhuras": 5, "nota": "o botão fica num rasgo no alto da traseira do receptor: a face de trás, inclinada e serrilhada nos 4 mm de trás, fica à mostra, e a frente passa pelo entalhe da tampa (perfil de lado em pecas.botaoMola)" },
   "seletor": { "eixoSai": 2.8, "aba": { "x": [-500,-480], "dobra": [-500,-490], "sai": 6.8 }, "nota": "a alavanca corre rente ao lado direito; o cubo do eixo (Ø 14 na planta) e a aba da frente, dobrada para fora, saem do receptor (medidas a partir da face do receptor). A alavanca da planta é ~10 mm mais curta que a da foto: fica a da foto" },
   "manejo": { "frente": -400.5, "ponta": 44.6, "comprimentos": [[18.5,10.9],[29.2,7.4],[40.0,5.4],[43.4,3.7]], "centroY": 8, "altura": [6.0,5.0], "nota": "vista de cima a alavanca afina da raiz (10,9 mm ao longo do cano) até a ponta redonda, a 44,6 mm do eixo, com a frente reta (x = -402,5 na planta; a base da alça dá a diferença de 2 mm entre a planta e a foto); de frente (foto 1) ela sai baixa, entre y = 5 e 11. Os pares são [distância do eixo, comprimento ao longo do cano]" },
   "estriasTuboGases": { "x": [-214.9,-160.8], "largura": 3.8, "profundidade": 1.0, "angulos": [30,90,150] },
   "furosTuboGases": { "x": [-192.3,-183.8,-175.3,-166.8], "diametro": 4.3, "angulo": 60 },
   "argolaDianteira": { "x": [-138,-134.4], "sai": 19.5, "nota": "do lado esquerdo do bloco de gases, uma alça no plano transversal saindo para o lado" },
   "pinoArgolaDianteira": { "x": [-139.5,-134.5], "sai": 1.3, "z": [1.0,9.0], "nota": "do lado direito do bloco de gases, na altura da argola (marca '9' da planta): a cabeça achatada do pino que prende a argola" },
   "argolaTraseira": { "x": -807, "nota": "por baixo da coronha; o pé embutido e a alça rebatida para a frente" }
  }
 },
 "cores": {
  "madeira": { "foto": { "srgb": "#B07150", "linear": [0.435, 0.167, 0.079] }, "fabrica": "#A4673F", "fabricaEscura": "#794224", "correcao": "estúdio claro: a coronha (a leitura mais confiável da madeira) mediu #B07150; a de fábrica é a mesma matiz com a exposição e a saturação corrigidas — claro #A4673F (linear 0,370/0,135/0,050) e o veio #794224 (linear 0,190/0,055/0,018)" },
  "aco": { "foto": { "srgb": "#18130C", "linear": [0.009, 0.007, 0.004] }, "fabrica": "#303135", "correcao": "a tampa mediu #18130C na sombra e o receptor #9B999E estourado pelo reflexo do fundo; o aço oxidado de fábrica fica #303135 (linear 0,030/0,031/0,036), entre os dois" },
  "carregador": { "foto": { "srgb": "#918E8D", "linear": [0.285, 0.270, 0.267] }, "fabrica": "#4D5054", "correcao": "o carregador mediu #918E8D com o reflexo do fundo; de fábrica, aço oxidado um pouco mais claro que o do receptor, #4D5054 (linear 0,075/0,080/0,088)" },
  "acoPolido": { "foto": null, "fabrica": "#ADADAF", "correcao": "peças internas (transportador do ferrolho, alavanca de manejo) sem leitura na foto: aço polido #ADADAF (linear 0,42/0,42/0,43), como na prova" }
 }
}
```

- [ ] **Passo 11: Os leitores da planta aceitam a ficha** — a `ak47.json` deixou de ser a planta da 4.1 (formato 1) e
  três lugares a liam direto: o teste das receitas, a bancada e o contexto do Blender de massinha. Os três passam por
  `plantaDoArquivo` (a ficha vira planta; as outras cinco plantas passam como estão). A receita de massinha da AK
  (tipo II) continua no registro até a Tarefa 16, mas não se compara mais com a planta, que agora é a do tipo 3.

Em `tests/weaponRecipes.test.js`, trocar:

```js
import { hashNode } from '../src/clay/sdf/nodes.js';
```

por:

```js
import { hashNode } from '../src/clay/sdf/nodes.js';
import { plantaDoArquivo } from '../src/weapons/model/ficha.js';
```

trocar:

```js
const plan = (id) => JSON.parse(readFileSync(new URL(`../tools/blender/refs/${id}.json`, import.meta.url), 'utf8'));
```

por:

```js
const plan = (id) => plantaDoArquivo(JSON.parse(readFileSync(new URL(`../tools/blender/refs/${id}.json`, import.meta.url), 'utf8')));
// A planta da AK virou a ficha da AK-47 tipo 3 realista (4.1a); a receita de massinha dela (tipo II) não se compara mais.
const COM_PLANTA = IDS.filter((x) => x !== 'knife' && x !== 'ak47');
```

trocar:

```js
test('receitas: silhueta lateral × planta de referência com IoU ≥ 0,8 (as seis com planta)', () => {
  for (const id of IDS.filter((x) => x !== 'knife')) {
```

por:

```js
test('receitas: silhueta lateral × planta de referência com IoU ≥ 0,8 (as de massinha com planta da 4.1)', () => {
  for (const id of COM_PLANTA) {
```

e trocar:

```js
    if (id !== 'knife') assert.equal(plan(id).lengthU, TABLE[id].length, `${id}: planta`);
```

por:

```js
    if (COM_PLANTA.includes(id)) assert.equal(plan(id).lengthU, TABLE[id].length, `${id}: planta`);
```

Em `src/maps/arsenal/planSheets.js`, trocar:

```js
import { bounds } from '../../clay/sdf/nodes.js';

/** Lê a planta de uma arma (null se não houver: a faca, ou arquivo ausente). */
export async function loadPlan(id) {
  try {
    const res = await fetch(new URL(`../../../tools/blender/refs/${id}.json`, import.meta.url));
    return res.ok ? await res.json() : null;
```

por:

```js
import { bounds } from '../../clay/sdf/nodes.js';
import { plantaDoArquivo } from '../../weapons/model/ficha.js';

/** Lê a planta de uma arma (null se não houver: a faca, ou arquivo ausente); a ficha (formato 2) vira planta. */
export async function loadPlan(id) {
  try {
    const res = await fetch(new URL(`../../../tools/blender/refs/${id}.json`, import.meta.url));
    return res.ok ? plantaDoArquivo(await res.json()) : null;
```

Em `tools/blender.mjs`, trocar:

```js
  const planta = existsSync(refPath) ? JSON.parse(readFileSync(refPath, 'utf8')) : null;
```

por:

```js
  const { plantaDoArquivo } = await import('../src/weapons/model/ficha.js');
  const planta = existsSync(refPath) ? plantaDoArquivo(JSON.parse(readFileSync(refPath, 'utf8'))) : null;
```

- [ ] **Passo 12: Rodar e ver passar**

Run: `node --test tests/fichaArma.test.js tests/regua.test.js tests/weaponRecipes.test.js`
Expected: PASS (4 + 4 + 8 testes). Suíte inteira: `npm test 2>&1 | tail -8` → `# tests 336`, `# fail 0`.

- [ ] **Passo 13: Conciliar as medidas-chave (D5), antes de modelar** — na régua (servidor da cópia de trabalho,
  `http://localhost:5176/tools/regua.html?arma=ak47&arquivo=File:AK-47%20assault%20rifle.jpg&mm=870&eixox=-130,-80&pxmm=6&faixa=120`):
  1. ler de novo, com a faixa ampliada a 6 px/mm, a posição do entalhe da alça (o fundo do "V" da folha) e do poste da
     massa (entre as orelhas) e registrar em `pontos.entalheAlca` e `pontos.posteMassa`;
  2. procurar no Commons uma segunda foto de lado de uma AK-47 tipo 3 de licença livre (lado direito ou esquerdo,
     espelhada) e medir nela a razão raio de mira ÷ comprimento com a régua;
  3. decidir pela regra: se as duas fotos concordarem entre si a 0,5 % e discordarem da ficha técnica, a geometria das
     fotos vale — `medidas.raioDeMira.mm` = a média medida, `fonte` = "régua sobre duas fotos (…)", e o 378 da ficha
     técnica vai para a `nota` com a explicação; se a segunda foto der 378 ± 1 %, a primeira tem erro de escala local
     (lente) e o modelo segue a ficha técnica, com os contornos daquela região corrigidos pela segunda foto; se não
     houver segunda foto utilizável, **perguntar ao usuário** qual número vale, mostrando as duas medições;
  4. atualizar `tools/blender/refs/ak47.json` e rodar de novo o teste da ficha.

---

### Tarefa 2: Dados — armas realistas, acabamentos, cores e skins

**Files:**
- Create: `src/data/armasReais.js`, `src/data/acabamentos.js`, `src/data/coresSkin.js`, `src/data/skinsArma.js`
- Test: `tests/skinsArma.test.js` (as tabelas; as funções vêm na Tarefa 3)

- [ ] **Passo 1: Testes das tabelas**

```js file=tests/skinsArma.test.js
// Skins das armas realistas (Fase 4.1a; desenho, seção 6): as tabelas dos acabamentos, das cores e das skins nomeadas,
// o registro das armas realistas (zonas, soquetes, peças, orçamentos, pintura de fábrica) e as contas puras de
// src/weapons/skins/ (acabamento → material, skins de fábrica e nomeadas, os argumentos do comando `skin`).
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { ACABAMENTOS, PADROES } from '../src/data/acabamentos.js';
import { CORES_SKIN } from '../src/data/coresSkin.js';
import { SKINS_ARMA } from '../src/data/skinsArma.js';
import {
  ARMAS_REAIS, CLASSE_DA_CATEGORIA, LODS_REAIS, ORCAMENTOS, PECAS_MOVEIS, ZONAS, orcamentoDaArma, soquetesDaArma,
} from '../src/data/armasReais.js';
import { VIEWMODEL } from '../src/data/viewmodel.js';

const HEX = /^#[0-9A-F]{6}$/;

test('acabamentos: os 15 da seção 6.1 com metal e aspereza da tabela', () => {
  const tabela = {
    oxidado: [1, 0.34], fosfatizado: [1, 0.55], fosco: [0, 0.85], acetinado: [0, 0.5], brilhante: [0, 0.25],
    metalico: [0.6, 0.35], perolado: [0.2, 0.3], anodizado: [1, 0.25], escovado: [1, 0.3], cromado: [1, 0.05],
    cerakote: [0, 0.7], carbono: [0, 0.35], madeira: [0, 0.45], polimero: [0, 0.65], borracha: [0, 0.9],
  };
  assert.deepEqual(Object.keys(ACABAMENTOS).sort(), Object.keys(tabela).sort());
  for (const [id, [metal, aspereza]] of Object.entries(tabela)) {
    const a = ACABAMENTOS[id];
    assert.equal(a.metal, metal, `${id}.metal`);
    assert.equal(a.aspereza, aspereza, `${id}.aspereza`);
    assert.ok(PADROES.includes(a.padrao), `${id}.padrao`);
    assert.match(a.gasto.cor, HEX, `${id}.gasto.cor`);
    assert.ok(a.varAspereza >= 0 && a.varAspereza <= 0.3 && a.varCor >= 0 && a.varCor <= 0.3, `${id}: variações`);
    if (a.duasCores) assert.ok(a.cor2Fator > 0, `${id}.cor2Fator`);
  }
  assert.equal(ACABAMENTOS.brilhante.verniz, 1);
  assert.equal(ACABAMENTOS.brilhante.asperezaVerniz, 0.05);
  assert.equal(ACABAMENTOS.metalico.verniz, 0.8);
  assert.equal(ACABAMENTOS.perolado.iridescencia, 0.8);
  assert.equal(ACABAMENTOS.perolado.iorIridescencia, 1.3);
  assert.deepEqual(ACABAMENTOS.perolado.filme, [250, 600]);
  assert.equal(ACABAMENTOS.anodizado.iridescencia, 0.2);
  assert.equal(ACABAMENTOS.escovado.anisotropia, 0.8);
  assert.equal(ACABAMENTOS.madeira.verniz, 0.6);
  assert.equal(ACABAMENTOS.carbono.padrao, 'carbono');
  assert.equal(ACABAMENTOS.madeira.padrao, 'veio');
  assert.equal(ACABAMENTOS.polimero.padrao, 'pontilhado');
});

test('cores: as 20 da paleta da seção 6.2', () => {
  const tabela = {
    preto: '#1B1B1D', brancoTitanio: '#EDEDE8', cinzaGrafite: '#4A4E54', carmesim: '#9E1B32', vermelho: '#D1362F',
    laranja: '#F28F3B', acafrao: '#E9A13B', amarelo: '#FFD23F', lima: '#9BD13B', verdeFloresta: '#2F5D3A',
    verdeAgua: '#3FB8AF', azulCobalto: '#2F4FB5', azulCeleste: '#5DADE2', roxo: '#6C3FB5', rosa: '#E86FA3',
    marromSiena: '#8C5A3C', areia: '#C2A878', verdeOliva: '#5B5F3A', terracota: '#C8553D', azulTropa: '#2F6DB5',
  };
  assert.deepEqual(Object.fromEntries(Object.entries(CORES_SKIN).map(([k, c]) => [k, c.hex])), tabela);
  for (const c of Object.values(CORES_SKIN)) assert.ok(c.nome.length > 2);
  assert.equal(CORES_SKIN.brancoTitanio.nome, 'Branco Titânio');
  assert.equal(CORES_SKIN.verdeAgua.nome, 'Verde-água');
});

test('skins nomeadas: as três de exemplo, com zonas, acabamentos e cores que existem', () => {
  assert.deepEqual(Object.values(SKINS_ARMA).map((s) => s.nome), ['Anodizado Terracota', 'Cromo e Carbono', 'Madeira Clara e Aço Escovado']);
  for (const [id, s] of Object.entries(SKINS_ARMA)) {
    for (const [zona, z] of Object.entries(s.zonas)) {
      assert.ok(ZONAS.includes(zona), `${id}.${zona}`);
      assert.ok(ACABAMENTOS[z.acabamento], `${id}.${zona}.acabamento`);
      for (const c of [z.cor, z.cor2].filter(Boolean)) assert.ok(CORES_SKIN[c] || HEX.test(c), `${id}.${zona}: cor ${c}`);
      assert.ok(z.desgaste >= 0 && z.desgaste <= 1, `${id}.${zona}.desgaste`);
      if (zona === 'interno') assert.equal(ACABAMENTOS[z.acabamento].metal, 1, `${id}: interno só metal`);
    }
  }
});

test('registro das armas realistas: a AK-47 com zonas, peças, soquetes, orçamento e pintura de fábrica', () => {
  assert.deepEqual(ZONAS, ['corpo', 'guarnicao', 'carregador', 'detalhes', 'interno']);
  assert.deepEqual(LODS_REAIS, ['perto', 'mundo', 'longe']);
  assert.deepEqual(PECAS_MOVEIS, ['ferrolho', 'carregador', 'gatilho', 'cao', 'seletor']);
  const ak = ARMAS_REAIS.ak47;
  assert.equal(ak.categoria, VIEWMODEL.weapons.ak47.category);
  assert.equal(ak.pasta, 'assets/armas/ak47/');
  assert.deepEqual(ak.zonas, ZONAS);
  assert.deepEqual(ak.pecas, ['ferrolho', 'carregador', 'gatilho', 'cao', 'seletor']);
  assert.deepEqual(soquetesDaArma('ak47'), ['boca', 'ejecao', 'carregador', 'mira_tras', 'mira_frente', 'mao_d', 'mao_e']);
  const o = orcamentoDaArma('ak47');
  assert.equal(o, ORCAMENTOS[CLASSE_DA_CATEGORIA.rifle]);
  assert.deepEqual(o.triangulos, { perto: 40000, mundo: 6000, longe: 1500 });
  assert.equal(o.textura, 2048);
  assert.equal(o.texturaMundo, 512);
  assert.equal(o.arquivosMB, 6);
  assert.deepEqual(Object.keys(ak.fabrica.zonas), ZONAS);
  for (const z of Object.values(ak.fabrica.zonas)) {
    assert.ok(ACABAMENTOS[z.acabamento]);
    assert.match(z.cor, HEX);
  }
  assert.equal(ak.fabrica.zonas.interno.acabamento, 'escovado');
  for (const id of Object.keys(ARMAS_REAIS)) assert.ok(VIEWMODEL.weapons[id], `${id} tem categoria no viewmodel`);
});

test('registro × ficha: a pintura de fábrica usa as cores de fábrica da ficha da AK', () => {
  const ficha = JSON.parse(readFileSync(new URL('../tools/blender/refs/ak47.json', import.meta.url), 'utf8'));
  const z = ARMAS_REAIS.ak47.fabrica.zonas;
  assert.equal(ficha.cores.aco.fabrica, z.corpo.cor);
  assert.equal(ficha.cores.aco.fabrica, z.detalhes.cor);
  assert.equal(ficha.cores.madeira.fabrica, z.guarnicao.cor);
  assert.equal(ficha.cores.madeira.fabricaEscura, z.guarnicao.cor2);
  assert.equal(ficha.cores.carregador.fabrica, z.carregador.cor);
  assert.equal(ficha.cores.acoPolido.fabrica, z.interno.cor);
});
```

- [ ] **Passo 2: Rodar e ver falhar**

Run: `node --test tests/skinsArma.test.js`
Expected: FAIL — `Cannot find module '.../src/data/acabamentos.js'`.

- [ ] **Passo 3: Acabamentos**

```js file=src/data/acabamentos.js
// Acabamentos das skins das armas realistas (Fase 4.1a; desenho em docs/superpowers/specs/2026-09-26-armas-realistas-
// design.md, seção 6.1; referências QCK2/5/7/10/13 e QRL2/5/8/11 no item 14 do moodboard): cada um com os parâmetros do
// material físico (MeshPhysicalMaterial) e o padrão procedural que o trecho de shader das armas desenha por cima
// (src/weapons/model/glsl/acabamentos.js). `gasto` é o que o desgaste mostra por baixo, pelo canal de borda (_m.b): o
// metal nu nas pinturas, o aço claro nos metais, a madeira lixada, o plástico raspado. `varAspereza` e `varCor` dosam o
// quanto a variação assada (_m.g e _m.a, em torno de 0,5) mexe na aspereza e na cor. `verniz` liga a camada de verniz
// (clearcoat), `iridescencia` o filme fino, `anisotropia` o escovado ao longo do X da arma — só quando o acabamento
// pede, para limitar as variantes de shader. `cor2Fator` faz a segunda cor (veio, trama) quando a skin não traz uma.

const F = Object.freeze;

// Padrões procedurais do shader, na ordem do define ARMA_PADRAO.
export const PADROES = F(['nenhum', 'fino', 'granulado', 'flocos', 'carbono', 'veio', 'pontilhado', 'ceramica']);

const NU = F({ cor: '#8F959C', metal: 1, aspereza: 0.32 }); // aço nu debaixo da tinta

export const ACABAMENTOS = F({
  oxidado: F({ nome: 'Oxidado de fábrica', metal: 1, aspereza: 0.34, padrao: 'fino', varAspereza: 0.16, varCor: 0.06, gasto: F({ cor: '#A7ABB0', metal: 1, aspereza: 0.2 }) }),
  fosfatizado: F({ nome: 'Fosfatizado', metal: 1, aspereza: 0.55, padrao: 'granulado', varAspereza: 0.14, varCor: 0.05, gasto: F({ cor: '#9CA0A6', metal: 1, aspereza: 0.26 }) }),
  fosco: F({ nome: 'Fosco', metal: 0, aspereza: 0.85, padrao: 'nenhum', varAspereza: 0.06, varCor: 0.04, gasto: NU }),
  acetinado: F({ nome: 'Acetinado', metal: 0, aspereza: 0.5, padrao: 'nenhum', varAspereza: 0.06, varCor: 0.04, gasto: NU }),
  brilhante: F({ nome: 'Brilhante', metal: 0, aspereza: 0.25, verniz: 1, asperezaVerniz: 0.05, padrao: 'nenhum', varAspereza: 0.04, varCor: 0.03, gasto: NU }),
  metalico: F({ nome: 'Metálico', metal: 0.6, aspereza: 0.35, verniz: 0.8, asperezaVerniz: 0.08, padrao: 'flocos', varAspereza: 0.05, varCor: 0.03, gasto: NU }),
  perolado: F({
    nome: 'Perolado', metal: 0.2, aspereza: 0.3, verniz: 1, asperezaVerniz: 0.06, iridescencia: 0.8, iorIridescencia: 1.3,
    filme: F([250, 600]), padrao: 'nenhum', varAspereza: 0.04, varCor: 0.03, gasto: NU,
  }),
  anodizado: F({
    nome: 'Anodizado', metal: 1, aspereza: 0.25, iridescencia: 0.2, iorIridescencia: 1.3, filme: F([250, 600]), padrao: 'fino',
    varAspereza: 0.08, varCor: 0.04, gasto: F({ cor: '#C9CCD0', metal: 1, aspereza: 0.2 }),
  }),
  escovado: F({ nome: 'Aço escovado', metal: 1, aspereza: 0.3, anisotropia: 0.8, padrao: 'nenhum', varAspereza: 0.06, varCor: 0.03, gasto: F({ cor: '#B8BBBF', metal: 1, aspereza: 0.18 }) }),
  cromado: F({ nome: 'Cromado', metal: 1, aspereza: 0.05, padrao: 'nenhum', varAspereza: 0.03, varCor: 0.02, gasto: NU }),
  cerakote: F({ nome: 'Cerakote', metal: 0, aspereza: 0.7, padrao: 'ceramica', varAspereza: 0.08, varCor: 0.04, gasto: NU }),
  carbono: F({
    nome: 'Fibra de carbono', metal: 0, aspereza: 0.35, verniz: 1, asperezaVerniz: 0.05, padrao: 'carbono', duasCores: true, cor2Fator: 2.2,
    varAspereza: 0.04, varCor: 0.03, gasto: F({ cor: '#3A3C40', metal: 0, aspereza: 0.6 }),
  }),
  madeira: F({
    nome: 'Madeira', metal: 0, aspereza: 0.45, verniz: 0.6, asperezaVerniz: 0.18, padrao: 'veio', duasCores: true, cor2Fator: 0.45,
    varAspereza: 0.1, varCor: 0.3, gasto: F({ cor: '#C49A6C', metal: 0, aspereza: 0.62 }),
  }),
  polimero: F({ nome: 'Polímero texturizado', metal: 0, aspereza: 0.65, padrao: 'pontilhado', varAspereza: 0.08, varCor: 0.05, gasto: F({ cor: '#6E7074', metal: 0, aspereza: 0.8 }) }),
  borracha: F({ nome: 'Borracha', metal: 0, aspereza: 0.9, padrao: 'nenhum', varAspereza: 0.05, varCor: 0.04, gasto: F({ cor: '#55575B', metal: 0, aspereza: 0.95 }) }),
});
```

- [ ] **Passo 4: Cores**

```js file=src/data/coresSkin.js
// Paleta das skins das armas (Fase 4.1a; desenho em docs/superpowers/specs/2026-09-26-armas-realistas-design.md, seção
// 6.2): cores nomeadas como as pinturas do Rocket League, várias vindas dos tokens das facções e da UI (terracota e
// azul da tropa, amarelo-massinha, laranja). A chave é o que o console aceita (também pelo nome, sem acento).

const F = Object.freeze;

export const CORES_SKIN = F({
  preto: F({ nome: 'Preto', hex: '#1B1B1D' }),
  brancoTitanio: F({ nome: 'Branco Titânio', hex: '#EDEDE8' }),
  cinzaGrafite: F({ nome: 'Cinza Grafite', hex: '#4A4E54' }),
  carmesim: F({ nome: 'Carmesim', hex: '#9E1B32' }),
  vermelho: F({ nome: 'Vermelho', hex: '#D1362F' }),
  laranja: F({ nome: 'Laranja', hex: '#F28F3B' }),
  acafrao: F({ nome: 'Açafrão', hex: '#E9A13B' }),
  amarelo: F({ nome: 'Amarelo', hex: '#FFD23F' }),
  lima: F({ nome: 'Lima', hex: '#9BD13B' }),
  verdeFloresta: F({ nome: 'Verde Floresta', hex: '#2F5D3A' }),
  verdeAgua: F({ nome: 'Verde-água', hex: '#3FB8AF' }),
  azulCobalto: F({ nome: 'Azul Cobalto', hex: '#2F4FB5' }),
  azulCeleste: F({ nome: 'Azul Celeste', hex: '#5DADE2' }),
  roxo: F({ nome: 'Roxo', hex: '#6C3FB5' }),
  rosa: F({ nome: 'Rosa', hex: '#E86FA3' }),
  marromSiena: F({ nome: 'Marrom Siena', hex: '#8C5A3C' }),
  areia: F({ nome: 'Areia', hex: '#C2A878' }),
  verdeOliva: F({ nome: 'Verde-oliva', hex: '#5B5F3A' }),
  terracota: F({ nome: 'Terracota', hex: '#C8553D' }),
  azulTropa: F({ nome: 'Azul Tropa', hex: '#2F6DB5' }),
});
```

- [ ] **Passo 5: Skins de exemplo**

```js file=src/data/skinsArma.js
// Skins nomeadas das armas realistas (Fase 4.1a; desenho em docs/superpowers/specs/2026-09-26-armas-realistas-design.md,
// seção 6.3): por zona, acabamento + cor (+ segunda cor no veio e na trama) + desgaste. São genéricas — valem para
// qualquer arma realista; a zona que a arma não tem é ignorada e a que a skin não traz fica de fábrica. As três abaixo
// são as do aceite da 4.1a; o catálogo, o desbloqueio e a tela de escolha são da Fase 11.

const F = Object.freeze;

export const SKINS_ARMA = F({
  anodizadoTerracota: F({
    nome: 'Anodizado Terracota',
    zonas: F({
      corpo: F({ acabamento: 'anodizado', cor: 'terracota', desgaste: 0.12 }),
      guarnicao: F({ acabamento: 'polimero', cor: 'preto', desgaste: 0.1 }),
      carregador: F({ acabamento: 'anodizado', cor: 'cinzaGrafite', desgaste: 0.15 }),
      detalhes: F({ acabamento: 'anodizado', cor: 'preto', desgaste: 0.2 }),
      interno: F({ acabamento: 'escovado', cor: 'brancoTitanio', desgaste: 0 }),
    }),
  }),
  cromoECarbono: F({
    nome: 'Cromo e Carbono',
    zonas: F({
      corpo: F({ acabamento: 'cromado', cor: 'brancoTitanio', desgaste: 0.05 }),
      guarnicao: F({ acabamento: 'carbono', cor: 'preto', cor2: 'cinzaGrafite', desgaste: 0.05 }),
      carregador: F({ acabamento: 'carbono', cor: 'preto', cor2: 'cinzaGrafite', desgaste: 0.1 }),
      detalhes: F({ acabamento: 'cromado', cor: 'brancoTitanio', desgaste: 0.1 }),
      interno: F({ acabamento: 'cromado', cor: 'brancoTitanio', desgaste: 0 }),
    }),
  }),
  madeiraClaraEAcoEscovado: F({
    nome: 'Madeira Clara e Aço Escovado',
    zonas: F({
      corpo: F({ acabamento: 'escovado', cor: 'brancoTitanio', desgaste: 0.08 }),
      guarnicao: F({ acabamento: 'madeira', cor: 'areia', cor2: 'marromSiena', desgaste: 0.15 }),
      carregador: F({ acabamento: 'escovado', cor: 'cinzaGrafite', desgaste: 0.12 }),
      detalhes: F({ acabamento: 'escovado', cor: 'cinzaGrafite', desgaste: 0.15 }),
      interno: F({ acabamento: 'escovado', cor: 'brancoTitanio', desgaste: 0 }),
    }),
  }),
});
```

- [ ] **Passo 6: Registro das armas realistas**

```js file=src/data/armasReais.js
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
```

- [ ] **Passo 7: Rodar e ver passar** (os testes das funções entram na Tarefa 3)

Run: `node --test tests/skinsArma.test.js`
Expected: PASS (5 testes).

- [ ] **Passo 8: Suíte inteira**

Run: `npm test 2>&1 | tail -8`
Expected: `# tests 341`, `# fail 0` (336 + 5 das tabelas).

---

### Tarefa 3: Acabamento → material e as skins (funções puras)

**Files:**
- Create: `src/weapons/skins/acabamento.js`, `src/weapons/skins/skin.js`
- Modify: `tests/skinsArma.test.js` (acrescentar os testes das funções)

- [ ] **Passo 1: Acrescentar os testes** — em `tests/skinsArma.test.js`, trocar:

```js
import { VIEWMODEL } from '../src/data/viewmodel.js';
```

por:

```js
import { VIEWMODEL } from '../src/data/viewmodel.js';
import {
  acabamentoParaMaterial, hexParaLinear, normalizarNome, resolverAcabamento, resolverCor, srgbParaLinear,
} from '../src/weapons/skins/acabamento.js';
import {
  FABRICA, aplicarZonas, chaveDaSkin, descreverSkin, lerArgumentosSkin, skinDeFabrica, skinPorNome, validarSkin,
} from '../src/weapons/skins/skin.js';
```

e trocar (o fim do arquivo):

```js
  assert.equal(ficha.cores.carregador.fabrica, z.carregador.cor);
  assert.equal(ficha.cores.acoPolido.fabrica, z.interno.cor);
});
```

por:

```js
  assert.equal(ficha.cores.carregador.fabrica, z.carregador.cor);
  assert.equal(ficha.cores.acoPolido.fabrica, z.interno.cor);
});

test('nomes: sem acento, sem espaço, cor pela chave, pelo nome ou em hex; acabamento pelo nome da tabela', () => {
  assert.equal(normalizarNome('Branco Titânio'), 'brancotitanio');
  assert.equal(normalizarNome('verde-água'), 'verdeagua');
  assert.equal(resolverCor('Branco Titânio'), '#EDEDE8');
  assert.equal(resolverCor('branco-titanio'), '#EDEDE8');
  assert.equal(resolverCor('brancoTitanio'), '#EDEDE8');
  assert.equal(resolverCor('#abcdef'), '#ABCDEF');
  assert.equal(resolverCor('abcdef'), '#ABCDEF');
  assert.equal(resolverCor('ciano'), null);
  assert.equal(resolverAcabamento('Aço escovado'), 'escovado');
  assert.equal(resolverAcabamento('fibra de carbono'), 'carbono');
  assert.equal(resolverAcabamento('verniz'), null);
});

test('cor: sRGB → linear (IEC 61966-2-1)', () => {
  assert.equal(srgbParaLinear(0), 0);
  assert.equal(srgbParaLinear(1), 1);
  assert.ok(Math.abs(srgbParaLinear(0.04045) - 0.04045 / 12.92) < 1e-12);
  assert.ok(Math.abs(hexParaLinear('#808080')[0] - 0.2158605) < 1e-6);
  assert.deepEqual(hexParaLinear('#FFFFFF'), [1, 1, 1]);
});

test('acabamento → material: números da tabela, recursos só quando o acabamento pede, segunda cor e desgaste', () => {
  const ox = acabamentoParaMaterial({ acabamento: 'oxidado', cor: '#303135', desgaste: 0.22 });
  assert.equal(ox.acabamento, 'oxidado');
  assert.equal(ox.metalness, 1);
  assert.equal(ox.roughness, 0.34);
  assert.deepEqual(ox.recursos, []);
  assert.equal(ox.clearcoat, 0);
  assert.equal(ox.padrao, 'fino');
  assert.equal(ox.padraoId, 1);
  assert.equal(ox.color2, null);
  assert.equal(ox.desgaste, 0.22);
  assert.deepEqual(ox.gasto.color, hexParaLinear('#A7ABB0'));
  const br = acabamentoParaMaterial({ acabamento: 'brilhante', cor: 'vermelho' });
  assert.deepEqual(br.recursos, ['verniz']);
  assert.equal(br.clearcoat, 1);
  assert.equal(br.clearcoatRoughness, 0.05);
  const pe = acabamentoParaMaterial({ acabamento: 'Perolado', cor: 'rosa' });
  assert.deepEqual(pe.recursos, ['verniz', 'iridescencia']);
  assert.equal(pe.iridescence, 0.8);
  assert.equal(pe.iridescenceIOR, 1.3);
  assert.deepEqual(pe.iridescenceThicknessRange, [250, 600]);
  const es = acabamentoParaMaterial({ acabamento: 'escovado', cor: '#ADADAF' });
  assert.deepEqual(es.recursos, ['anisotropia']);
  assert.equal(es.anisotropy, 0.8);
  const md = acabamentoParaMaterial({ acabamento: 'madeira', cor: '#A4673F' });
  assert.deepEqual(md.color2, md.color.map((c) => c * 0.45), 'sem cor2, o veio sai da cor pelo fator');
  const md2 = acabamentoParaMaterial({ acabamento: 'madeira', cor: '#A4673F', cor2: '#794224' });
  assert.deepEqual(md2.color2, hexParaLinear('#794224'));
  const cb = acabamentoParaMaterial({ acabamento: 'carbono', cor: 'preto' });
  assert.ok(cb.color2.every((c, i) => c > cb.color[i]), 'a trama clara sai mais clara que o preto');
  assert.equal(acabamentoParaMaterial({ acabamento: 'fosco', cor: 'preto', desgaste: 7 }).desgaste, 1);
  assert.equal(acabamentoParaMaterial({ acabamento: 'fosco', cor: 'preto', desgaste: -1 }).desgaste, 0);
  assert.throws(() => acabamentoParaMaterial({ acabamento: 'verniz', cor: 'preto' }), /acabamento desconhecido/);
  assert.throws(() => acabamentoParaMaterial({ acabamento: 'fosco', cor: 'ciano' }), /cor desconhecida/);
});

test('skins: fábrica, nomeadas por cima da fábrica, chave estável e validação', () => {
  const fab = skinDeFabrica('ak47');
  assert.equal(fab.chave, FABRICA);
  assert.equal(fab.nome, 'De fábrica');
  assert.deepEqual(Object.keys(fab.zonas), ZONAS);
  assert.equal(fab.zonas.guarnicao.cor2, '#794224');
  const cc = skinPorNome('ak47', 'Cromo e Carbono');
  assert.equal(cc.chave, 'cromoECarbono');
  assert.equal(cc.zonas.corpo.acabamento, 'cromado');
  assert.equal(cc.zonas.guarnicao.cor2, '#4A4E54');
  assert.deepEqual(skinPorNome('ak47', 'fabrica'), fab);
  assert.equal(skinPorNome('ak47', 'madeira clara e aco escovado').chave, 'madeiraClaraEAcoEscovado');
  assert.throws(() => skinPorNome('ak47', 'Dourada'), /skin desconhecida/);
  assert.equal(chaveDaSkin(fab), 'fabrica');
  const p1 = aplicarZonas('ak47', fab, { zonas: { corpo: { acabamento: 'fosco', cor: 'preto' } }, desgaste: null });
  const p2 = aplicarZonas('ak47', fab, { zonas: { corpo: { acabamento: 'fosco', cor: 'preto' } }, desgaste: null });
  assert.equal(p1.chave, 'personalizada');
  assert.equal(chaveDaSkin(p1), chaveDaSkin(p2), 'a mesma skin personalizada dá a mesma chave');
  assert.notEqual(chaveDaSkin(p1), chaveDaSkin(fab));
  assert.throws(() => validarSkin('ak47', { ...fab, zonas: { ...fab.zonas, interno: { acabamento: 'fosco', cor: '#FFFFFF', desgaste: 0 } } }),
    /interno só aceita acabamento de metal/);
  const linhas = descreverSkin(fab);
  assert.equal(linhas.length, ZONAS.length);
  assert.match(linhas[0], /^corpo: Oxidado de fábrica #303135 · desgaste 0,22$/);
});

test('comando skin: leitura dos argumentos', () => {
  assert.deepEqual(lerArgumentosSkin([]), { tipo: 'mostrar' });
  assert.deepEqual(lerArgumentosSkin(['fabrica']), { tipo: 'nome', nome: FABRICA });
  assert.deepEqual(lerArgumentosSkin(['Fábrica']), { tipo: 'nome', nome: FABRICA });
  assert.deepEqual(lerArgumentosSkin(['Anodizado', 'Terracota']), { tipo: 'nome', nome: 'anodizadoTerracota' });
  assert.deepEqual(lerArgumentosSkin(['corpo=anodizado:terracota', 'guarnição=madeira:areia,marrom-siena', 'desgaste=0,3']), {
    tipo: 'zonas',
    zonas: {
      corpo: { acabamento: 'anodizado', cor: '#C8553D', cor2: null },
      guarnicao: { acabamento: 'madeira', cor: '#C2A878', cor2: '#8C5A3C' },
    },
    desgaste: 0.3,
  });
  assert.deepEqual(lerArgumentosSkin(['desgaste=1']), { tipo: 'zonas', zonas: {}, desgaste: 1 });
  assert.throws(() => lerArgumentosSkin(['Dourada']), /skin desconhecida: Dourada/);
  assert.throws(() => lerArgumentosSkin(['cano=fosco:preto']), /zona desconhecida: cano/);
  assert.throws(() => lerArgumentosSkin(['corpo=verniz:preto']), /acabamento desconhecido: verniz/);
  assert.throws(() => lerArgumentosSkin(['corpo=fosco:ciano']), /cor desconhecida: ciano/);
  assert.throws(() => lerArgumentosSkin(['corpo=fosco']), /use <zona>=<acabamento>:<cor>/);
  assert.throws(() => lerArgumentosSkin(['desgaste=2']), /desgaste entre 0 e 1/);
});

test('comando skin: aplicar zonas na skin atual (desgaste nas zonas citadas, ou em todas sem zona)', () => {
  const fab = skinDeFabrica('ak47');
  const a = aplicarZonas('ak47', fab, lerArgumentosSkin(['corpo=anodizado:terracota', 'desgaste=0.4']));
  assert.equal(a.zonas.corpo.acabamento, 'anodizado');
  assert.equal(a.zonas.corpo.cor, '#C8553D');
  assert.equal(a.zonas.corpo.desgaste, 0.4);
  assert.equal(a.zonas.guarnicao.desgaste, fab.zonas.guarnicao.desgaste, 'as outras zonas ficam');
  const b = aplicarZonas('ak47', fab, lerArgumentosSkin(['desgaste=0']));
  for (const z of ZONAS) assert.equal(b.zonas[z].desgaste, 0);
  assert.throws(() => aplicarZonas('ak47', fab, lerArgumentosSkin(['interno=fosco:preto'])), /interno só aceita acabamento de metal/);
});
```

- [ ] **Passo 2: Rodar e ver falhar**

Run: `node --test tests/skinsArma.test.js`
Expected: FAIL — `Cannot find module '.../src/weapons/skins/acabamento.js'`.

- [ ] **Passo 3: Acabamento → material**

```js file=src/weapons/skins/acabamento.js
// Acabamento + cor + desgaste → parâmetros do material físico das armas realistas (Fase 4.1a; desenho em
// docs/superpowers/specs/2026-09-26-armas-realistas-design.md, seções 5.3 e 6). Função pura, testada no Node: o
// material de cada zona (src/weapons/model/materialArma.js) só copia estes números; nada aqui depende do three.
// Também os nomes digitados no console: sem acento, sem espaço, pela chave ou pelo nome da tabela.

import { ACABAMENTOS, PADROES } from '../../data/acabamentos.js';
import { CORES_SKIN } from '../../data/coresSkin.js';

const HEX = /^#?([0-9a-f]{6})$/i;

/** Nome digitado → chave de busca ("Branco Titânio" → "brancotitanio", "verde-água" → "verdeagua"). */
export function normalizarNome(texto) {
  return String(texto).normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase().replace(/[\s_-]+/g, '');
}

function indice(tabela) {
  const mapa = new Map();
  for (const [chave, def] of Object.entries(tabela)) {
    mapa.set(normalizarNome(chave), chave);
    mapa.set(normalizarNome(def.nome), chave);
  }
  return mapa;
}

const CORES = indice(CORES_SKIN);
const ACABS = indice(ACABAMENTOS);

/** Chave do acabamento pela chave ou pelo nome da tabela (null se não existe). */
export function resolverAcabamento(nome) {
  return nome == null ? null : ACABS.get(normalizarNome(nome)) ?? null;
}

/** Cor da paleta (chave ou nome) ou hex ("#RRGGBB" ou "RRGGBB") → "#RRGGBB" maiúsculo (null se não reconhece). */
export function resolverCor(valor) {
  if (valor == null) return null;
  const m = HEX.exec(String(valor).trim());
  if (m) return `#${m[1].toUpperCase()}`;
  const chave = CORES.get(normalizarNome(valor));
  return chave ? CORES_SKIN[chave].hex.toUpperCase() : null;
}

/** Componente sRGB (0–1) → linear. */
export function srgbParaLinear(c) {
  return c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4;
}

/** "#RRGGBB" → [r, g, b] linear. */
export function hexParaLinear(hex) {
  const m = HEX.exec(hex);
  if (!m) throw new Error(`cor inválida: ${hex}`);
  const n = parseInt(m[1], 16);
  return [(n >> 16) & 255, (n >> 8) & 255, n & 255].map((v) => srgbParaLinear(v / 255));
}

const limitar = (v, a, b) => Math.min(b, Math.max(a, v));

/**
 * Parâmetros do material de uma zona.
 * @param {{acabamento:string, cor:string, cor2?:string|null, desgaste?:number}} zona chave ou nome do acabamento; cor da
 *   paleta ou hex; segunda cor (madeira e carbono — sem ela, sai da primeira pelo `cor2Fator`); desgaste de 0 a 1
 * @returns {{acabamento:string, metalness:number, roughness:number, color:number[], color2:number[]|null,
 *   clearcoat:number, clearcoatRoughness:number, iridescence:number, iridescenceIOR:number,
 *   iridescenceThicknessRange:number[], anisotropy:number, padrao:string, padraoId:number, varAspereza:number,
 *   varCor:number, desgaste:number, gasto:{color:number[], metalness:number, roughness:number}, recursos:string[]}}
 *   cores em linear; `recursos` = os do material físico que o acabamento liga (verniz, iridescência, anisotropia)
 */
export function acabamentoParaMaterial({ acabamento, cor, cor2 = null, desgaste = 0 }) {
  const chave = resolverAcabamento(acabamento);
  if (!chave) throw new Error(`acabamento desconhecido: ${acabamento} (use ${Object.keys(ACABAMENTOS).join(', ')})`);
  const a = ACABAMENTOS[chave];
  const hex = resolverCor(cor);
  if (!hex) throw new Error(`cor desconhecida: ${cor}`);
  const color = hexParaLinear(hex);
  let color2 = null;
  if (a.duasCores) {
    const hex2 = resolverCor(cor2);
    if (cor2 != null && !hex2) throw new Error(`cor desconhecida: ${cor2}`);
    color2 = hex2 ? hexParaLinear(hex2) : color.map((c) => limitar(c * a.cor2Fator, 0, 1));
  }
  const clearcoat = a.verniz ?? 0;
  const iridescence = a.iridescencia ?? 0;
  const anisotropy = a.anisotropia ?? 0;
  const recursos = [];
  if (clearcoat > 0) recursos.push('verniz');
  if (iridescence > 0) recursos.push('iridescencia');
  if (anisotropy > 0) recursos.push('anisotropia');
  return {
    acabamento: chave,
    metalness: a.metal,
    roughness: a.aspereza,
    color,
    color2,
    clearcoat,
    clearcoatRoughness: a.asperezaVerniz ?? 0,
    iridescence,
    iridescenceIOR: a.iorIridescencia ?? 1.3,
    iridescenceThicknessRange: [...(a.filme ?? [250, 600])],
    anisotropy,
    padrao: a.padrao,
    padraoId: PADROES.indexOf(a.padrao),
    varAspereza: a.varAspereza,
    varCor: a.varCor,
    desgaste: limitar(Number(desgaste) || 0, 0, 1),
    gasto: { color: hexParaLinear(a.gasto.cor), metalness: a.gasto.metal, roughness: a.gasto.aspereza },
    recursos,
  };
}
```

- [ ] **Passo 4: Skins**

```js file=src/weapons/skins/skin.js
// Skins das armas realistas (Fase 4.1a; desenho em docs/superpowers/specs/2026-09-26-armas-realistas-design.md, seção
// 6.3): uma skin é, por zona, acabamento + cor (+ segunda cor) + desgaste. Aqui ficam as contas puras — a skin de
// fábrica de cada arma (src/data/armasReais.js), as nomeadas (src/data/skinsArma.js) por cima da de fábrica, a
// validação, a chave estável (o cache dos materiais) e o comando de console `skin` (texto → pedido → skin nova). Formato
// de uma skin resolvida: {chave, nome, zonas: {zona: {acabamento, cor, cor2, desgaste}}}, cores em "#RRGGBB".

import { ACABAMENTOS } from '../../data/acabamentos.js';
import { ARMAS_REAIS, ZONAS } from '../../data/armasReais.js';
import { SKINS_ARMA } from '../../data/skinsArma.js';
import { normalizarNome, resolverAcabamento, resolverCor } from './acabamento.js';

export const FABRICA = 'fabrica';
export const PERSONALIZADA = 'personalizada';

const SKINS = new Map();
for (const [chave, def] of Object.entries(SKINS_ARMA)) {
  SKINS.set(normalizarNome(chave), chave);
  SKINS.set(normalizarNome(def.nome), chave);
}
const ZONA = new Map(ZONAS.map((z) => [normalizarNome(z), z]));
const USO = 'use <zona>=<acabamento>:<cor>[,<cor2>] (zonas: corpo, guarnicao, carregador, detalhes, interno) e desgaste=<0..1>';
const virgula = (v) => String(v).replace('.', ',');

function arma(id) {
  const a = ARMAS_REAIS[id];
  if (!a) throw new Error(`${id} não é uma arma realista (skins de acabamento só nas armas feitas no Blender)`);
  return a;
}

/** Uma zona validada: acabamento pela chave, cores em "#RRGGBB", desgaste de 0 a 1; o `interno` só aceita metal. */
function zonaValida(zona, def) {
  const acabamento = resolverAcabamento(def?.acabamento);
  if (!acabamento) throw new Error(`${zona}: acabamento desconhecido: ${def?.acabamento}`);
  const cor = resolverCor(def.cor);
  if (!cor) throw new Error(`${zona}: cor desconhecida: ${def.cor}`);
  const cor2 = def.cor2 == null ? null : resolverCor(def.cor2);
  if (def.cor2 != null && !cor2) throw new Error(`${zona}: cor desconhecida: ${def.cor2}`);
  const desgaste = Number(def.desgaste ?? 0);
  if (!(desgaste >= 0 && desgaste <= 1)) throw new Error(`${zona}: desgaste entre 0 e 1 (veio ${def.desgaste})`);
  if (zona === 'interno' && ACABAMENTOS[acabamento].metal !== 1) {
    throw new Error(`interno só aceita acabamento de metal (oxidado, fosfatizado, anodizado, escovado, cromado): ${acabamento}`);
  }
  return { acabamento, cor, cor2, desgaste };
}

/** Skin completa e válida para a arma (todas as zonas dela). */
export function validarSkin(id, skin) {
  const a = arma(id);
  const zonas = {};
  for (const z of a.zonas) {
    if (!skin?.zonas?.[z]) throw new Error(`skin de ${id} sem a zona ${z}`);
    zonas[z] = zonaValida(z, skin.zonas[z]);
  }
  return { chave: skin.chave ?? PERSONALIZADA, nome: skin.nome ?? 'Personalizada', zonas };
}

/** A pintura de fábrica da arma. */
export function skinDeFabrica(id) {
  const a = arma(id);
  return validarSkin(id, { chave: FABRICA, nome: a.fabrica.nome, zonas: a.fabrica.zonas });
}

/** Chave da skin nomeada pela chave ou pelo nome (sem acento nem espaço), ou null. */
export function resolverSkinNomeada(nome) {
  return SKINS.get(normalizarNome(nome)) ?? null;
}

/** Skin por nome: "fabrica" ou uma nomeada, por cima da de fábrica (a zona que a skin não traz fica de fábrica). */
export function skinPorNome(id, nome) {
  const fab = skinDeFabrica(id);
  if (normalizarNome(nome) === FABRICA) return fab;
  const chave = resolverSkinNomeada(nome);
  if (!chave) throw new Error(`skin desconhecida: ${nome} (tem: fabrica, ${Object.values(SKINS_ARMA).map((s) => s.nome).join(', ')})`);
  const def = SKINS_ARMA[chave];
  const zonas = {};
  for (const z of Object.keys(fab.zonas)) zonas[z] = def.zonas[z] ?? fab.zonas[z];
  return validarSkin(id, { chave, nome: def.nome, zonas });
}

/** Chave estável da skin: a da tabela, ou "p:" + o hash do conteúdo para a personalizada (o cache dos materiais). */
export function chaveDaSkin(skin) {
  if (skin.chave !== PERSONALIZADA) return skin.chave;
  const texto = JSON.stringify(Object.keys(skin.zonas).sort().map((z) => [z, skin.zonas[z]]));
  let h = 0x811c9dc5;
  for (let i = 0; i < texto.length; i++) h = Math.imul(h ^ texto.charCodeAt(i), 0x01000193) >>> 0;
  return `p:${h.toString(16).padStart(8, '0')}`;
}

/**
 * Argumentos do comando `skin` depois do id da arma:
 *   []                                        → {tipo: 'mostrar'}
 *   ['fabrica'] ou ['Anodizado', 'Terracota'] → {tipo: 'nome', nome} (a chave; o nome pode ter espaços)
 *   ['corpo=anodizado:terracota', 'guarnicao=madeira:areia,marromSiena', 'desgaste=0.3']
 *                                             → {tipo: 'zonas', zonas: {zona: {acabamento, cor, cor2}}, desgaste}
 */
export function lerArgumentosSkin(args) {
  if (!args.length) return { tipo: 'mostrar' };
  if (!args.some((a) => a.includes('='))) {
    const nome = args.join(' ');
    if (normalizarNome(nome) === FABRICA) return { tipo: 'nome', nome: FABRICA };
    const chave = resolverSkinNomeada(nome);
    if (!chave) throw new Error(`skin desconhecida: ${nome} (tem: fabrica, ${Object.values(SKINS_ARMA).map((s) => s.nome).join(', ')})`);
    return { tipo: 'nome', nome: chave };
  }
  const zonas = {};
  let desgaste = null;
  for (const arg of args) {
    const [k, v] = arg.split('=');
    if (v === undefined || !k) throw new Error(`argumento sem "=": ${arg} (${USO})`);
    if (normalizarNome(k) === 'desgaste') {
      desgaste = Number(v.replace(',', '.'));
      if (!(desgaste >= 0 && desgaste <= 1)) throw new Error(`desgaste entre 0 e 1 (veio ${v})`);
      continue;
    }
    const zona = ZONA.get(normalizarNome(k));
    if (!zona) throw new Error(`zona desconhecida: ${k} (${USO})`);
    const [acab, cores] = v.split(':');
    if (!acab || !cores) throw new Error(`${arg}: ${USO}`);
    const acabamento = resolverAcabamento(acab);
    if (!acabamento) throw new Error(`acabamento desconhecido: ${acab} (use ${Object.keys(ACABAMENTOS).join(', ')})`);
    const [c1, c2] = cores.split(',');
    const cor = resolverCor(c1);
    if (!cor) throw new Error(`cor desconhecida: ${c1}`);
    const cor2 = c2 === undefined ? null : resolverCor(c2);
    if (c2 !== undefined && !cor2) throw new Error(`cor desconhecida: ${c2}`);
    zonas[zona] = { acabamento, cor, cor2 };
  }
  return { tipo: 'zonas', zonas, desgaste };
}

/**
 * Aplica um pedido de zonas numa skin: troca as zonas citadas (com o desgaste pedido, ou o que a zona tinha) e, sem
 * zona citada, põe o desgaste em todas. O resultado é a skin personalizada.
 */
export function aplicarZonas(id, atual, pedido) {
  const a = arma(id);
  const zonas = {};
  const citadas = Object.keys(pedido.zonas ?? {});
  for (const z of citadas) if (!a.zonas.includes(z)) throw new Error(`${id} não tem a zona ${z}`);
  for (const z of a.zonas) {
    const velha = atual.zonas[z];
    const nova = pedido.zonas?.[z];
    if (nova) zonas[z] = { ...nova, desgaste: pedido.desgaste ?? velha.desgaste };
    else if (!citadas.length && pedido.desgaste != null) zonas[z] = { ...velha, desgaste: pedido.desgaste };
    else zonas[z] = velha;
  }
  return validarSkin(id, { chave: PERSONALIZADA, nome: 'Personalizada', zonas });
}

/** Uma linha por zona, para o console: "corpo: Oxidado de fábrica #303135 · desgaste 0,22". */
export function descreverSkin(skin) {
  return Object.entries(skin.zonas).map(([z, d]) =>
    `${z}: ${ACABAMENTOS[d.acabamento].nome} ${d.cor}${d.cor2 ? `,${d.cor2}` : ''} · desgaste ${virgula(d.desgaste)}`);
}
```

- [ ] **Passo 5: Rodar e ver passar**

Run: `node --test tests/skinsArma.test.js`
Expected: PASS (5 + 6 = 11 testes).

- [ ] **Passo 6: Suíte inteira**

Run: `npm test 2>&1 | tail -8`
Expected: `# tests 347`, `# fail 0`.

---

### Tarefa 4: Leitor e validador da saída do Blender (Node)

**Files:**
- Create: `tools/blender/saida.mjs`, `tests/armasSaida.test.js`

O Node confere o que o Blender gravou sem carregar o three: o bloco JSON do `.glb` (nomes, hierarquia, primitivas,
materiais, acessores), o cabeçalho de cada `.webp` (lado e se é sem perdas) e o relatório; tudo contra o registro
(`src/data/armasReais.js`). O teste com a AK de verdade entra na Tarefa 8, quando os arquivos existirem.

- [ ] **Passo 1: Testes com arquivos sintéticos**

```js file=tests/armasSaida.test.js
// Leitor e validador da saída do Blender (Fase 4.1a; desenho, seções 4.5, 4.6 e 9.1), com arquivos montados no teste:
// o .glb (cabeçalho, bloco JSON e bloco binário), o resumo por nível (peças, zonas, triângulos, tangentes, UV), os
// soquetes e o cabeçalho do .webp (VP8L sem perdas, VP8 com perdas, VP8X estendido). A AK de verdade é conferida em
// tests/armaAk47.test.js (Tarefa 8).
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { ladoWebp, lerGlb, resumoGlb } from '../tools/blender/saida.mjs';

/** Monta um .glb com o JSON e um binário (os dois alinhados a 4 bytes). */
function montarGlb(json, bin = Buffer.alloc(0)) {
  let j = Buffer.from(JSON.stringify(json), 'utf8');
  if (j.length % 4) j = Buffer.concat([j, Buffer.alloc(4 - (j.length % 4), 0x20)]);
  let b = bin;
  if (b.length % 4) b = Buffer.concat([b, Buffer.alloc(4 - (b.length % 4), 0)]);
  const cab = Buffer.alloc(12);
  cab.writeUInt32LE(0x46546c67, 0);
  cab.writeUInt32LE(2, 4);
  cab.writeUInt32LE(12 + 8 + j.length + (b.length ? 8 + b.length : 0), 8);
  const cj = Buffer.alloc(8);
  cj.writeUInt32LE(j.length, 0);
  cj.writeUInt32LE(0x4e4f534a, 4);
  const partes = [cab, cj, j];
  if (b.length) {
    const cb = Buffer.alloc(8);
    cb.writeUInt32LE(b.length, 0);
    cb.writeUInt32LE(0x004e4942, 4);
    partes.push(cb, b);
  }
  return Buffer.concat(partes);
}

/** Um glTF mínimo com a hierarquia da arma: 3 níveis × (base + ferrolho), soquetes e duas zonas. */
function gltfArma() {
  const accessors = [];
  const acessor = (count) => {
    accessors.push({ count, componentType: 5126, type: 'VEC3' });
    return accessors.length - 1;
  };
  const meshes = [];
  const malha = (tris, comTangente, mats) => {
    meshes.push({
      primitives: mats.map((material) => ({
        attributes: { POSITION: acessor(tris * 3), NORMAL: acessor(tris * 3), TEXCOORD_0: acessor(tris * 3), ...(comTangente ? { TANGENT: acessor(tris * 3) } : {}) },
        indices: acessor(tris * 3),
        material,
      })),
    });
    return meshes.length - 1;
  };
  const nodes = [{ name: 'ak47', children: [] }];
  const no = (def, pai) => {
    nodes.push(def);
    nodes[pai].children = [...(nodes[pai].children ?? []), nodes.length - 1];
    return nodes.length - 1;
  };
  for (const [lod, tris, tangente] of [['perto', 100, true], ['mundo', 20, false], ['longe', 5, false]]) {
    const l = no({ name: lod }, 0);
    no({ name: `${lod}_base`, mesh: malha(tris, tangente, [0, 1]) }, l);
    no({ name: `${lod}_ferrolho`, mesh: malha(tris / 5, tangente, [1]), translation: [1, 2, 3], extras: { eixo: [-1, 0, 0] } }, l);
  }
  const s = no({ name: 'soquetes' }, 0);
  no({ name: 'soquete_boca', translation: [21.69, 0, 0] }, s);
  no({ name: 'soquete_mao_d', translation: [-2, -3, 0.5], rotation: [0, 0, 0.7071068, 0.7071068] }, s);
  return {
    asset: { version: '2.0' }, scene: 0, scenes: [{ nodes: [0] }], nodes, meshes, accessors,
    materials: [{ name: 'corpo' }, { name: 'interno' }], animations: [{ name: 'empunhadura', channels: [], samplers: [] }],
  };
}

test('glb: cabeçalho, bloco JSON e bloco binário', () => {
  const bin = Buffer.from([1, 2, 3, 4, 5]);
  const { json, bin: b } = lerGlb(montarGlb({ asset: { version: '2.0' } }, bin));
  assert.deepEqual(json, { asset: { version: '2.0' } });
  assert.equal(b.length, 8, 'o binário vem com o preenchimento');
  assert.equal(b[4], 5);
  assert.throws(() => lerGlb(Buffer.from('nada disso aqui')), /não é um \.glb/);
});

test('glb: resumo por nível — peças, zonas, triângulos, tangentes, UV, extras, soquetes, animações e o Draco', () => {
  const r = resumoGlb(lerGlb(montarGlb(gltfArma())).json, 'ak47');
  assert.equal(r.raiz, 'ak47');
  assert.deepEqual(Object.keys(r.lods), ['perto', 'mundo', 'longe']);
  assert.equal(r.lods.perto.triangulos, 100 * 2 + 20);
  assert.equal(r.lods.mundo.triangulos, 20 * 2 + 4);
  assert.equal(r.lods.longe.triangulos, 5 * 2 + 1);
  assert.deepEqual(Object.keys(r.lods.perto.pecas), ['base', 'ferrolho']);
  assert.deepEqual(r.lods.perto.pecas.base.zonas, ['corpo', 'interno']);
  assert.deepEqual(r.lods.perto.pecas.ferrolho.extras, { eixo: [-1, 0, 0] });
  assert.deepEqual(r.lods.perto.pecas.ferrolho.posicao, [1, 2, 3]);
  assert.equal(r.lods.perto.tangentes, true);
  assert.equal(r.lods.mundo.tangentes, false);
  assert.equal(r.lods.perto.uv, true);
  assert.deepEqual(r.zonas, ['corpo', 'interno']);
  assert.deepEqual(Object.keys(r.soquetes), ['boca', 'mao_d']);
  assert.deepEqual(r.soquetes.boca.posicao, [21.69, 0, 0]);
  assert.deepEqual(r.soquetes.mao_d.rotacao, [0, 0, 0.7071068, 0.7071068]);
  assert.deepEqual(r.animacoes, ['empunhadura']);
  assert.equal(r.draco, false);
  assert.equal(resumoGlb({ ...gltfArma(), extensionsUsed: ['KHR_draco_mesh_compression'] }, 'ak47').draco, true);
  const alfabetica = gltfArma();
  alfabetica.nodes[0].children.reverse();
  assert.deepEqual(Object.keys(resumoGlb(alfabetica, 'ak47').lods), ['perto', 'mundo', 'longe'], 'a ordem do registro, não a do arquivo');
  assert.throws(() => resumoGlb(gltfArma(), 'm4a4'), /a raiz do \.glb é ak47, esperava m4a4/);
});

test('webp: VP8L sem perdas, VP8 com perdas e VP8X estendido', () => {
  const riff = (fourcc, dados) => {
    const cab = Buffer.alloc(12);
    cab.write('RIFF', 0, 'ascii');
    cab.writeUInt32LE(4 + 8 + dados.length, 4);
    cab.write('WEBP', 8, 'ascii');
    const ch = Buffer.alloc(8);
    ch.write(fourcc, 0, 'ascii');
    ch.writeUInt32LE(dados.length, 4);
    return Buffer.concat([cab, ch, dados]);
  };
  const l = Buffer.alloc(5);
  l[0] = 0x2f;
  l.writeUInt32LE(((2048 - 1) | ((2048 - 1) << 14) | (1 << 28)) >>> 0, 1);
  assert.deepEqual(ladoWebp(riff('VP8L', l)), { largura: 2048, altura: 2048, semPerdas: true, alfa: true });
  const v = Buffer.alloc(10);
  v[3] = 0x9d;
  v[4] = 0x01;
  v[5] = 0x2a;
  v.writeUInt16LE(512, 6);
  v.writeUInt16LE(256, 8);
  assert.deepEqual(ladoWebp(riff('VP8 ', v)), { largura: 512, altura: 256, semPerdas: false, alfa: false });
  const x = Buffer.alloc(10);
  x[0] = 0x10; // bit do alfa
  x.writeUIntLE(1024 - 1, 4, 3);
  x.writeUIntLE(1024 - 1, 7, 3);
  const estendido = Buffer.concat([riff('VP8X', x), Buffer.from('VP8L'), Buffer.from([5, 0, 0, 0]), l]);
  estendido.writeUInt32LE(estendido.length - 8, 4);
  assert.deepEqual(ladoWebp(estendido), { largura: 1024, altura: 1024, semPerdas: true, alfa: true });
  assert.throws(() => ladoWebp(Buffer.from('RIFF0000WAVEfmt ')), /não é um \.webp/);
});
```

- [ ] **Passo 2: Rodar e ver falhar**

Run: `node --test tests/armasSaida.test.js`
Expected: FAIL — `Cannot find module '.../tools/blender/saida.mjs'`.

- [ ] **Passo 3: Implementar o leitor e o validador**

```js file=tools/blender/saida.mjs
// Leitor e validador da saída do Blender (Fase 4.1a; desenho em docs/superpowers/specs/2026-09-26-armas-realistas-
// design.md, seções 4.5, 4.6 e 9.1). Sem o three: o Node só precisa do bloco JSON do .glb (nomes, hierarquia,
// primitivas, materiais e acessores), do cabeçalho de cada .webp (lado e se é sem perdas) e do relatório que o Blender
// gravou. `validarSaida` confere tudo contra o registro das armas realistas (src/data/armasReais.js): os três níveis com
// as peças da arma, as zonas, os soquetes da categoria, os triângulos e as texturas do orçamento, as tangentes e as UV
// do nível de perto, o total dos arquivos e os números do relatório (medidas ±1 %, silhueta ≥ 98 % com tolerância).

import { readFileSync, statSync, existsSync } from 'node:fs';
import { join } from 'node:path';
import { ARMAS_REAIS, LODS_REAIS, orcamentoDaArma, soquetesDaArma } from '../../src/data/armasReais.js';

const GLTF = 0x46546c67;
const JSON_CHUNK = 0x4e4f534a;
const BIN_CHUNK = 0x004e4942;

/** Blocos de um .glb (versão 2). @returns {{json:object, bin:Buffer|null}} */
export function lerGlb(buf) {
  if (buf.length < 20 || buf.readUInt32LE(0) !== GLTF) throw new Error('não é um .glb (falta o "glTF" no começo)');
  if (buf.readUInt32LE(4) !== 2) throw new Error(`glTF versão ${buf.readUInt32LE(4)} (esperava 2)`);
  const total = Math.min(buf.readUInt32LE(8), buf.length);
  let pos = 12;
  let json = null;
  let bin = null;
  while (pos + 8 <= total) {
    const len = buf.readUInt32LE(pos);
    const tipo = buf.readUInt32LE(pos + 4);
    const dados = buf.subarray(pos + 8, pos + 8 + len);
    if (tipo === JSON_CHUNK) json = JSON.parse(dados.toString('utf8'));
    else if (tipo === BIN_CHUNK) bin = dados;
    pos += 8 + len;
  }
  if (!json) throw new Error('o .glb não tem o bloco JSON');
  return { json, bin };
}

/**
 * Resumo do glTF de uma arma: a raiz (tem de ser o id), os níveis (peças `<nivel>_<peca>` com as zonas, os triângulos,
 * a posição e os extras), se o nível tem tangentes e UV em todas as primitivas, as zonas usadas, os soquetes e as
 * animações.
 */
export function resumoGlb(json, id) {
  const cena = json.scenes?.[json.scene ?? 0];
  const raizes = (cena?.nodes ?? []).map((i) => json.nodes[i]);
  if (raizes.length !== 1) throw new Error(`o .glb precisa de uma raiz só (tem ${raizes.length})`);
  const raiz = raizes[0];
  if (raiz.name !== id) throw new Error(`a raiz do .glb é ${raiz.name}, esperava ${id}`);
  const filhos = (n) => (n.children ?? []).map((i) => json.nodes[i]);
  const materiais = json.materials ?? [];
  const contaPrimitiva = (p) => {
    const mode = p.mode ?? 4;
    if (mode !== 4) throw new Error(`primitiva que não é de triângulos (mode ${mode})`);
    const n = p.indices !== undefined ? json.accessors[p.indices].count : json.accessors[p.attributes.POSITION].count;
    return n / 3;
  };
  const lods = {};
  const zonasUsadas = new Set();
  // Na ordem do registro (perto, mundo, longe): o exportador do Blender grava os nós em ordem alfabética.
  for (const nome of LODS_REAIS) {
    const no = filhos(raiz).find((n) => n.name === nome);
    if (!no) continue;
    const lod = { pecas: {}, triangulos: 0, tangentes: true, uv: true };
    for (const peca of filhos(no)) {
      const prefixo = `${no.name}_`;
      if (!peca.name?.startsWith(prefixo)) throw new Error(`peça ${peca.name} fora do padrão ${prefixo}<peça>`);
      const nome = peca.name.slice(prefixo.length);
      const zonas = [];
      let triangulos = 0;
      const pilha = [peca];
      while (pilha.length) {
        const n = pilha.pop();
        if (n.mesh !== undefined) {
          for (const p of json.meshes[n.mesh].primitives) {
            triangulos += contaPrimitiva(p);
            const zona = materiais[p.material]?.name ?? null;
            if (zona && !zonas.includes(zona)) zonas.push(zona);
            if (zona) zonasUsadas.add(zona);
            if (!p.attributes.TANGENT) lod.tangentes = false;
            if (!p.attributes.TEXCOORD_0) lod.uv = false;
          }
        }
        pilha.push(...filhos(n));
      }
      lod.pecas[nome] = { zonas, triangulos, posicao: peca.translation ?? [0, 0, 0], extras: peca.extras ?? null };
      lod.triangulos += triangulos;
    }
    lods[no.name] = lod;
  }
  const soquetes = {};
  const pasta = filhos(raiz).find((n) => n.name === 'soquetes');
  for (const s of pasta ? filhos(pasta) : []) {
    if (!s.name?.startsWith('soquete_')) throw new Error(`nó ${s.name} dentro de "soquetes" fora do padrão soquete_<nome>`);
    soquetes[s.name.slice('soquete_'.length)] = { posicao: s.translation ?? [0, 0, 0], rotacao: s.rotation ?? [0, 0, 0, 1] };
  }
  return {
    raiz: raiz.name,
    lods,
    zonas: [...zonasUsadas],
    soquetes,
    animacoes: (json.animations ?? []).map((a) => a.name),
    draco: (json.extensionsUsed ?? []).includes('KHR_draco_mesh_compression'),
  };
}

/** Lado e tipo de um .webp pelo cabeçalho (VP8, VP8L ou VP8X + o bloco da imagem). */
export function ladoWebp(buf) {
  if (buf.length < 20 || buf.toString('ascii', 0, 4) !== 'RIFF' || buf.toString('ascii', 8, 12) !== 'WEBP') {
    throw new Error('não é um .webp');
  }
  let pos = 12;
  let largura = 0;
  let altura = 0;
  let alfa = false;
  while (pos + 8 <= buf.length) {
    const tipo = buf.toString('ascii', pos, pos + 4);
    const len = buf.readUInt32LE(pos + 4);
    const d = pos + 8;
    if (tipo === 'VP8X') {
      alfa = (buf[d] & 0x10) !== 0;
      largura = buf.readUIntLE(d + 4, 3) + 1;
      altura = buf.readUIntLE(d + 7, 3) + 1;
    } else if (tipo === 'VP8L') {
      const b = buf.readUInt32LE(d + 1);
      return { largura: largura || (b & 0x3fff) + 1, altura: altura || ((b >>> 14) & 0x3fff) + 1, semPerdas: true, alfa: alfa || ((b >>> 28) & 1) === 1 };
    } else if (tipo === 'VP8 ') {
      return { largura: largura || buf.readUInt16LE(d + 6) & 0x3fff, altura: altura || buf.readUInt16LE(d + 8) & 0x3fff, semPerdas: false, alfa };
    }
    pos = d + len + (len % 2);
  }
  throw new Error('.webp sem o bloco da imagem');
}

/** Arquivos que a construção grava para uma arma (pasta do registro). */
export function arquivosDaArma(id) {
  return {
    glb: `${id}.glb`,
    n: `${id}_n.webp`,
    m: `${id}_m.webp`,
    mundoN: `${id}_mundo_n.webp`,
    mundoM: `${id}_mundo_m.webp`,
    relatorio: `${id}.relatorio.json`,
  };
}

/**
 * Confere a saída de uma arma na raiz do projeto.
 * @returns {{problemas:string[], resumo:object|null, relatorio:object|null, bytes:number}}
 */
export function validarSaida(id, raiz) {
  const problemas = [];
  const a = ARMAS_REAIS[id];
  if (!a) return { problemas: [`${id} não está em src/data/armasReais.js`], resumo: null, relatorio: null, bytes: 0 };
  const orc = orcamentoDaArma(id);
  const pasta = join(raiz, a.pasta);
  const arqs = arquivosDaArma(id);
  const faltando = Object.values(arqs).filter((f) => !existsSync(join(pasta, f)));
  if (faltando.length) return { problemas: [`faltam em ${a.pasta}: ${faltando.join(', ')}`], resumo: null, relatorio: null, bytes: 0 };
  let bytes = 0;
  for (const f of Object.values(arqs)) bytes += statSync(join(pasta, f)).size;
  if (bytes > orc.arquivosMB * 1024 * 1024) problemas.push(`arquivos: ${(bytes / 1048576).toFixed(2)} MB (orçamento ${orc.arquivosMB} MB)`);

  const resumo = resumoGlb(lerGlb(readFileSync(join(pasta, arqs.glb))).json, id);
  const pecas = ['base', ...a.pecas];
  for (const lod of LODS_REAIS) {
    const l = resumo.lods[lod];
    if (!l) {
      problemas.push(`falta o nível ${lod}`);
      continue;
    }
    const nomes = Object.keys(l.pecas);
    for (const p of pecas) if (!nomes.includes(p)) problemas.push(`${lod}: falta a peça ${p}`);
    for (const p of nomes) if (!pecas.includes(p)) problemas.push(`${lod}: peça a mais ${p}`);
    if (l.triangulos > orc.triangulos[lod]) problemas.push(`${lod}: ${l.triangulos} triângulos (orçamento ${orc.triangulos[lod]})`);
    if (!l.uv) problemas.push(`${lod}: primitiva sem UV`);
  }
  if (resumo.lods.perto && !resumo.lods.perto.tangentes) problemas.push('perto: primitiva sem tangentes (o relevo assado precisa delas)');
  if (!resumo.draco) problemas.push('o .glb sem a compressão Draco (KHR_draco_mesh_compression; desenho, seção 4.5)');
  for (const z of resumo.zonas) if (!a.zonas.includes(z)) problemas.push(`zona desconhecida no .glb: ${z}`);
  for (const z of a.zonas) if (!resumo.zonas.includes(z)) problemas.push(`falta a zona ${z}`);
  for (const s of soquetesDaArma(id)) if (!resumo.soquetes[s]) problemas.push(`falta o soquete ${s}`);

  const texturas = { [arqs.n]: orc.textura, [arqs.m]: orc.textura, [arqs.mundoN]: orc.texturaMundo, [arqs.mundoM]: orc.texturaMundo };
  for (const [arq, lado] of Object.entries(texturas)) {
    const w = ladoWebp(readFileSync(join(pasta, arq)));
    if (w.largura !== lado || w.altura !== lado) problemas.push(`${arq}: ${w.largura}×${w.altura} (esperava ${lado}×${lado})`);
    if (!w.semPerdas) problemas.push(`${arq}: WebP com perdas (os canais empacotados precisam do sem perdas)`);
    if (arq.endsWith('_m.webp') && !w.alfa) problemas.push(`${arq}: sem o canal alfa (variação de cor)`);
  }

  const relatorio = JSON.parse(readFileSync(join(pasta, arqs.relatorio), 'utf8'));
  if (relatorio.arma !== id) problemas.push(`relatório de ${relatorio.arma}, esperava ${id}`);
  if (!relatorio.aprovado) problemas.push(`o Blender reprovou: ${(relatorio.problemas ?? []).join('; ')}`);
  for (const [m, d] of Object.entries(relatorio.medidas ?? {})) {
    if (!(Math.abs(d.erro) <= 0.01)) problemas.push(`medida ${m}: ${d.mm} mm contra ${d.alvo} mm (erro ${(d.erro * 100).toFixed(2)} %)`);
  }
  if (!(relatorio.silhueta?.iouTolerancia >= 0.98)) problemas.push(`silhueta: ${relatorio.silhueta?.iouTolerancia} com tolerância (mínimo 0,98)`);
  for (const lod of LODS_REAIS) {
    const t = relatorio.lods?.[lod]?.triangulos;
    if (resumo.lods[lod] && t !== resumo.lods[lod].triangulos) problemas.push(`${lod}: o relatório diz ${t} triângulos e o .glb tem ${resumo.lods[lod].triangulos}`);
  }
  return { problemas, resumo, relatorio, bytes };
}
```

- [ ] **Passo 4: Rodar e ver passar**

Run: `node --test tests/armasSaida.test.js`
Expected: PASS (3 testes).

- [ ] **Passo 5: Suíte inteira**

Run: `npm test 2>&1 | tail -8`
Expected: `# tests 350`, `# fail 0`.

---

### Tarefa 5: Pacote do Blender — unidades, peças, materiais de fábrica, estúdio, zonas e soquetes

**Files:**
- Create: `tools/blender/armas/__init__.py`, `unidades.py`, `pecas.py`, `materiais.py`, `estudio.py`, `zonas.py`,
  `soquetes.py`

A biblioteca de peças é a da prova (`base_helpers.py`, os ajudantes do `ak_v3.py` e do `ak_v2.py`) organizada em
módulo, com o que o desenho pede a mais (seção 4.1): perfil suavizado, varredura e tubo por polilinha, mola, rosca em
hélice, fileira, tira, gravação de marcações, peça só do modelo alto, e cada peça marcada com a zona, a peça móvel e o
chanfro. O modelo alto e o de jogo saem do mesmo script da arma, em duas coleções (`alto` e `jogo`): o nível diz os
segmentos do chanfro e se o microdetalhe nasce.

- [ ] **Passo 1: O pacote e as unidades**

```python file=tools/blender/armas/__init__.py
# Armas realistas feitas por script no Blender (Fase 4.1a; desenho em docs/superpowers/specs/
# 2026-09-26-armas-realistas-design.md, seção 4): cada arma é construída a partir da ficha
# (tools/blender/refs/<id>.json), assada e exportada como o .glb e as texturas .webp que o jogo carrega
# (assets/armas/<id>/). Ponto de entrada: principal.py, chamado por tools/blender.mjs.
```

```python file=tools/blender/armas/unidades.py
# Unidades e referenciais das armas realistas (Fase 4.1a; plano da 4.1a, decisão D1).
# Construção em milímetros no referencial da ficha: boca do cano em x = 0, eixo do cano em y = 0, +X para a boca, +Y
# para cima. No Blender a cena é em metros (1 mm = 0,001), X = x, Z = y e o lado direito da arma fica em -Y.
# Exportação: escala 1000/25,4 (1 unidade = 1 u = 1 polegada na escala do boneco) com a origem no pino do gatilho; com
# o Y para cima do glTF, o -Y do Blender vira o +Z do jogo (o lado direito).

S = 0.001                     # metros por milímetro
MM_POR_U = 25.4
U_POR_M = 1000.0 / MM_POR_U   # metros da cena → u do jogo


def v3(x, y, z):
    """Ponto em mm no Blender (x, y, z) → metros."""
    return (x * S, y * S, z * S)


def ficha(x, y, lado=0.0):
    """Ponto (x, y) da ficha no Blender, com a profundidade `lado` em mm (Y do Blender: + esquerda, - direita)."""
    return (x * S, lado * S, y * S)
```

- [ ] **Passo 2: A biblioteca de peças**

```python file=tools/blender/armas/pecas.py
# Biblioteca de peças das armas realistas (Fase 4.1a; desenho, seção 4.1; vem da prova de conceito de 2026-09-26).
# Tudo em mm no referencial da ficha (unidades.py). Cada peça é um objeto de malha com as propriedades que o resto do
# pacote lê:
#   zona     — corpo, guarnicao, carregador, detalhes ou interno (zonas.py)
#   peca     — 'base' ou a peça móvel (soquetes.py junta por peça)
#   chanfro  — (largura em mm, segmentos no modelo alto); o de jogo usa 1 segmento (chanfro < 1 mm) ou 2
#   so_alto  — microdetalhe que só existe no modelo alto (vai para o relevo assado)
#   cortador — objeto usado só num booleano (escondido; nunca exportado)
# `iniciar` diz em que nível ('alto' ou 'jogo') e em que coleção as peças nascem; peça `so_alto` não nasce no de jogo.
import math

import bmesh
import bpy
from mathutils import Matrix, Quaternion, Vector

from .unidades import S, ficha, v3

_estado = {'nivel': 'alto', 'colecao': None}


def iniciar(nivel, nome_colecao):
    """Nível da construção ('alto' ou 'jogo') e a coleção onde as peças nascem (criada e ligada à cena)."""
    assert nivel in ('alto', 'jogo'), nivel
    col = bpy.data.collections.get(nome_colecao) or bpy.data.collections.new(nome_colecao)
    if col.name not in bpy.context.scene.collection.children:
        bpy.context.scene.collection.children.link(col)
    _estado['nivel'] = nivel
    _estado['colecao'] = col
    return col


def nivel():
    return _estado['nivel']


def _pula(so_alto):
    return so_alto and _estado['nivel'] == 'jogo'


def objeto(nome, bm, mat, zona, peca='base', so_alto=False, chanfro=(0.6, 3)):
    me = bpy.data.meshes.new(nome)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(nome, me)
    _estado['colecao'].objects.link(ob)
    if mat is not None:
        me.materials.append(mat)
    for p in me.polygons:
        p.use_smooth = True
    ob['zona'] = zona
    ob['peca'] = peca
    ob['so_alto'] = bool(so_alto)
    ob['chanfro'] = chanfro
    return ob


# ------------------------------------------------------------------------------------------------ contornos 2D
def suavizar(pts, it=2):
    """Chaikin em polígono fechado: tira o serrilhado de contorno lido de foto de baixa resolução."""
    for _ in range(it):
        novo = []
        for i, (ax, ay) in enumerate(pts):
            bx, by = pts[(i + 1) % len(pts)]
            novo += [(0.75 * ax + 0.25 * bx, 0.75 * ay + 0.25 * by), (0.25 * ax + 0.75 * bx, 0.25 * ay + 0.75 * by)]
        pts = novo
    return pts


def reamostrar(poli, n):
    """n pontos igualmente espaçados ao longo de uma polilinha."""
    comp = [0.0]
    for (ax, ay), (bx, by) in zip(poli, poli[1:]):
        comp.append(comp[-1] + math.hypot(bx - ax, by - ay))
    out = []
    for i in range(n):
        alvo = comp[-1] * i / (n - 1)
        k = max(1, next((j for j, c in enumerate(comp) if c >= alvo), len(comp) - 1))
        t = (alvo - comp[k - 1]) / max(1e-9, comp[k] - comp[k - 1])
        (ax, ay), (bx, by) = poli[k - 1], poli[k]
        out.append((ax + (bx - ax) * t, ay + (by - ay) * t))
    return out


def faixa_poligono(linha, larg):
    """Contorno de uma tira de largura `larg` em volta de uma polilinha (nervuras, frisos)."""
    esq, dir_ = [], []
    for i, (x, y) in enumerate(linha):
        a = linha[max(0, i - 1)]
        b = linha[min(len(linha) - 1, i + 1)]
        tx, ty = b[0] - a[0], b[1] - a[1]
        L = math.hypot(tx, ty) or 1.0
        nx, ny = -ty / L * larg / 2, tx / L * larg / 2
        esq.append((x + nx, y + ny))
        dir_.append((x - nx, y - ny))
    return esq + dir_[::-1]


def arco(cx, cy, r, a0, a1, n):
    """n + 1 pontos de um arco (graus) em volta de (cx, cy)."""
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)), cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / n)))
            for i in range(n + 1)]


# ------------------------------------------------------------------------------------------------ sólidos
def prisma(nome, pts, plano, a, b, mat, zona, peca='base', chanfro=0.8, seg=3, so_alto=False):
    """Polígono 2D extrudado. plano 'XZ' (extrude em Y de a até b, mm), 'YZ' (em X) ou 'XY' (em Z)."""
    if _pula(so_alto):
        return None
    bm = bmesh.new()

    def p3(u, v, w):
        if plano == 'XZ':
            return v3(u, w, v)
        if plano == 'YZ':
            return v3(w, u, v)
        return v3(u, v, w)
    vs = [bm.verts.new(p3(u, v, a)) for u, v in pts]
    f = bm.faces.new(vs)
    ret = bmesh.ops.extrude_face_region(bm, geom=[f])
    novos = [e for e in ret['geom'] if isinstance(e, bmesh.types.BMVert)]
    d = (b - a) * S
    bmesh.ops.translate(bm, vec={'XZ': (0, d, 0), 'YZ': (d, 0, 0), 'XY': (0, 0, d)}[plano], verts=novos)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return objeto(nome, bm, mat, zona, peca, so_alto, (chanfro, seg))


def perfil_suave(nome, pts, plano, a, b, mat, zona, peca='base', chanfro=0.8, seg=3, it=2, so_alto=False):
    """Prisma de um contorno lido de foto, suavizado por Chaikin antes (it iterações)."""
    return prisma(nome, suavizar(pts, it), plano, a, b, mat, zona, peca, chanfro, seg, so_alto)


def caixa(nome, minimo, maximo, mat, zona, peca='base', chanfro=0.6, so_alto=False):
    """Caixa alinhada aos eixos do Blender (mm): mínimo e máximo (x, y, z)."""
    x0, y0, z0 = minimo
    x1, y1, z1 = maximo
    return prisma(nome, [(x0, z0), (x1, z0), (x1, z1), (x0, z1)], 'XZ', y0, y1, mat, zona, peca, chanfro, 3, so_alto)


def torno(nome, perfil, mat, zona, peca='base', seg=48, eixo='X', centro=(0, 0, 0), chanfro=0.5, so_alto=False):
    """Perfil (posição ao longo do eixo, raio) em mm girado em volta de X (ou de Z) e posto no centro (mm)."""
    if _pula(so_alto):
        return None
    bm = bmesh.new()
    if eixo == 'X':
        vs = [bm.verts.new(v3(x, 0, r)) for x, r in perfil]
        ax = (1, 0, 0)
    else:
        vs = [bm.verts.new(v3(r, 0, z)) for z, r in perfil]
        ax = (0, 0, 1)
    es = [bm.edges.new((p, q)) for p, q in zip(vs, vs[1:])]
    bmesh.ops.spin(bm, geom=vs + es, cent=(0, 0, 0), axis=ax, angle=math.tau, steps=seg, use_merge=True)
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=0.00001)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bmesh.ops.translate(bm, vec=v3(*centro), verts=bm.verts[:])
    return objeto(nome, bm, mat, zona, peca, so_alto, (chanfro, 2))


def esfera(nome, centro, raio, escala, mat, zona, peca='base', u=24, v=12, so_alto=False):
    """Esfera (mm) achatada por `escala` (x, y, z)."""
    if _pula(so_alto):
        return None
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=u, v_segments=v, radius=raio * S)
    bmesh.ops.scale(bm, vec=escala, verts=bm.verts[:])
    bmesh.ops.translate(bm, vec=v3(*centro), verts=bm.verts[:])
    return objeto(nome, bm, mat, zona, peca, so_alto, (0, 0))


def _referenciais(P, fechado):
    """Tangente e os dois eixos do perfil em cada ponto da polilinha, por transporte paralelo: o perfil não gira de
    repente onde a tangente cruza um eixo fixo (o que torcia as faces em "gravata-borboleta"). No caminho fechado, a
    torção que sobra na emenda é repartida ao longo da volta."""
    n = len(P)
    if fechado:
        tang = [(P[(i + 1) % n] - P[(i - 1) % n]).normalized() for i in range(n)]
    else:
        tang = [(P[min(n - 1, i + 1)] - P[max(0, i - 1)]).normalized() for i in range(n)]
    ref = Vector((0, 0, 1)) if abs(tang[0].z) < 0.9 else Vector((1, 0, 0))
    us = [tang[0].cross(ref).normalized()]
    for i in range(1, n):
        u = tang[i - 1].rotation_difference(tang[i]) @ us[-1]
        us.append((u - tang[i] * u.dot(tang[i])).normalized())
    if fechado:
        u = tang[-1].rotation_difference(tang[0]) @ us[-1]
        u = (u - tang[0] * u.dot(tang[0])).normalized()
        sobra = math.atan2(tang[0].dot(u.cross(us[0])), u.dot(us[0]))
        us = [Quaternion(tang[i], sobra * i / n) @ us[i] for i in range(n)]
    return [(t, u, t.cross(u).normalized()) for t, u in zip(tang, us)]


def varrer(nome, perfil, caminho, mat, zona, peca='base', fechar_pontas=True, so_alto=False):
    """Perfil 2D (mm, no plano perpendicular ao caminho) varrido ao longo de uma polilinha 3D (mm, Blender x, y, z).
    Caminho que volta ao primeiro ponto (argolas) fecha em anel, sem tampas."""
    if _pula(so_alto):
        return None
    bm = bmesh.new()
    P = [Vector(v3(*p)) for p in caminho]
    fechado = len(P) > 3 and (P[0] - P[-1]).length < 1e-7
    if fechado:
        P = P[:-1]
    aneis = [[bm.verts.new(p + (u * a + w * b) * S) for a, b in perfil] for p, (_t, u, w) in zip(P, _referenciais(P, fechado))]
    n = len(perfil)
    pares = list(zip(aneis, aneis[1:])) + ([(aneis[-1], aneis[0])] if fechado else [])
    for r0, r1 in pares:
        for k in range(n):
            bm.faces.new((r0[k], r0[(k + 1) % n], r1[(k + 1) % n], r1[k]))
    if fechar_pontas and not fechado:
        bm.faces.new(aneis[0][::-1])
        bm.faces.new(aneis[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return objeto(nome, bm, mat, zona, peca, so_alto, (0, 0))


def tubo(nome, caminho, raio, mat, zona, peca='base', seg=12, so_alto=False):
    """Tubo de raio constante (mm) ao longo de uma polilinha 3D: molas, varetas, arames, argolas."""
    circulo = [(raio * math.cos(k * math.tau / seg), raio * math.sin(k * math.tau / seg)) for k in range(seg)]
    return varrer(nome, circulo, caminho, mat, zona, peca, True, so_alto)


def mola(nome, x0, x1, centro_yz, raio, fio, espiras, mat, zona, peca='base', passos=16, so_alto=False):
    """Mola helicoidal ao longo de X (mm): de x0 a x1, centro (y, z) do Blender, raio da hélice e do fio."""
    n = max(2, int(espiras * passos))
    pts = []
    for i in range(n + 1):
        f = i / n
        ang = f * espiras * math.tau
        pts.append((x0 + (x1 - x0) * f, centro_yz[0] + raio * math.cos(ang), centro_yz[1] + raio * math.sin(ang)))
    return tubo(nome, pts, fio, mat, zona, peca, 8, so_alto)


def rosca(nome, x0, x1, raio, passo, profundidade, mat, zona, peca='base', seg=24, centro=(0, 0), so_alto=False):
    """Filete de rosca em hélice ao longo de X (mm): um dente triangular de base `passo` girado de x0 até x1 sobre o
    raio (o núcleo é um torno à parte, de raio `raio - profundidade`). Sólido fechado: o dente é uma face extrudada."""
    if _pula(so_alto):
        return None
    bm = bmesh.new()
    cy, cz = centro
    vs = [bm.verts.new(v3(x0, cy, cz + raio - profundidade)), bm.verts.new(v3(x0 + passo / 2, cy, cz + raio)),
          bm.verts.new(v3(x0 + passo, cy, cz + raio - profundidade))]
    f = bm.faces.new(vs)
    voltas = max(1, int((x1 - x0 - passo) / passo))
    bmesh.ops.spin(bm, geom=[f] + vs + list(f.edges), cent=v3(x0, cy, cz), axis=(1, 0, 0), dvec=(passo * S / seg, 0, 0),
                   angle=math.tau * voltas, steps=seg * voltas, use_duplicate=False)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return objeto(nome, bm, mat, zona, peca, so_alto, (0, 0))


def tira(nome, linha, largura, plano, a, b, mat, zona, peca='base', chanfro=0.4, seg=2, so_alto=False):
    """Prisma de uma tira de `largura` mm em volta de uma polilinha (nervuras de carregador, frisos)."""
    return prisma(nome, faixa_poligono(linha, largura), plano, a, b, mat, zona, peca, chanfro, seg, so_alto)


def ret_arredondado(u0, u1, v0, v1, raio, n=4):
    """Contorno 2D (anti-horário) de um retângulo de cantos arredondados, com n segmentos por canto (os anéis de um
    lofting). O raio fica limitado à metade do lado menor."""
    r = max(0.0, min(raio, (u1 - u0) / 2 - 1e-4, (v1 - v0) / 2 - 1e-4))
    cantos = ((u1 - r, v0 + r, -90.0), (u1 - r, v1 - r, 0.0), (u0 + r, v1 - r, 90.0), (u0 + r, v0 + r, 180.0))
    pts = []
    for cu, cv, a0 in cantos:
        for i in range(n + 1):
            a = math.radians(a0 + 90.0 * i / n)
            pts.append((cu + r * math.cos(a), cv + r * math.sin(a)))
    return pts


def lofting(nome, aneis, mat, zona, peca='base', so_alto=False, chanfro=(0, 0)):
    """Malha fechada a partir de anéis de pontos 3D (mm, Blender x, y, z), todos com o mesmo número de pontos e na
    mesma ordem: cada anel ligado ao próximo por quads e as duas pontas fechadas por n-gons (a alavanca de manejo
    afinando até a ponta)."""
    if _pula(so_alto):
        return None
    bm = bmesh.new()
    vs = [[bm.verts.new(v3(*p)) for p in anel] for anel in aneis]
    n = len(aneis[0])
    for r0, r1 in zip(vs, vs[1:]):
        for k in range(n):
            bm.faces.new((r0[k], r0[(k + 1) % n], r1[(k + 1) % n], r1[k]))
    bm.faces.new(vs[0][::-1])
    bm.faces.new(vs[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return objeto(nome, bm, mat, zona, peca, so_alto, chanfro)


def pino(nome, x, y, r, mat, zona, peca='base', lado=-1, de=16.0, ate=16.9, so_alto=False):
    """Cabeça de pino ou de eixo aflorando na lateral: cilindro curto ao longo de Y no lado direito (lado=-1) ou
    esquerdo (+1), com o centro em (x, y) da ficha e a face de `de` a `ate` mm do plano do meio."""
    ob = torno(nome, [(de, 0), (de, r), (ate, r), (ate, 0)], mat, zona, peca, 24, eixo='Z', centro=(x, 0, y), so_alto=so_alto)
    if ob:
        rotacionar(ob, 'X', 90 if lado < 0 else -90, (x, 0, y))
    return ob


def fileira(fabrica, n, passo):
    """n peças feitas por `fabrica(i, dx, dy)` com `passo` = (dx, dy) mm entre uma e a próxima (rebites, parafusos,
    nervuras, dentes de trilho, serrilhas). Devolve os objetos."""
    return [fabrica(i, passo[0] * i, passo[1] * i) for i in range(n)]


# O А cirílico da fonte do Blender (Bfont) tem contornos que se cruzam: a malha dele sai aberta e o booleano exato corta
# errado (o "АВ" do seletor virava "–В"). O A latino tem o mesmo desenho; as outras letras usadas saem inteiras.
HOMOGLIFOS = str.maketrans({'А': 'A'})


def _malha_do_texto(fonte, nome):
    """Malha fechada do texto: solda as tampas nas paredes (o texto convertido sai com as costuras abertas) e recusa
    letra quebrada — com um cortador aberto o booleano exato corta errado sem avisar."""
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(fonte.evaluated_get(dg))
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-7)
    abertas = sum(1 for e in bm.edges if not e.is_manifold)
    bm.to_mesh(me)
    bm.free()
    if abertas:
        raise ValueError(f'gravação "{nome}": a fonte gerou {abertas} arestas abertas (letra com contornos cruzados); '
                         'troque a letra por uma de mesmo desenho em HOMOGLIFOS')
    return me


def gravacao(nome, texto, x, y, altura, face, plano_mm, profundidade, alvo, rotacao=0.0):
    """Marcação estampada (letras do seletor, número de série, graduação da alça, marca de controle): o texto vira um
    cortador de `profundidade` mm na peça `alvo`, só no modelo alto (vai para o relevo assado). (x, y) = canto de baixo à
    esquerda na ficha (na face de cima, x e o Y do Blender); `face` 'direita', 'esquerda' ou 'cima'; `plano_mm` = Y do
    Blender da face (direita/esquerda) ou Z da face de cima; `altura` das letras em mm; `rotacao` em graus no plano da
    face (na de cima, -90 deixa a leitura de quem olha de trás da arma)."""
    if _estado['nivel'] == 'jogo' or alvo is None:
        return None
    cu = bpy.data.curves.new(nome, 'FONT')
    cu.body = texto.translate(HOMOGLIFOS)
    cu.size = altura * S
    cu.extrude = profundidade * S
    fonte = bpy.data.objects.new(nome, cu)
    _estado['colecao'].objects.link(fonte)
    if face == 'cima':
        fonte.location = v3(x, y, plano_mm)
        fonte.rotation_euler = (0.0, 0.0, math.radians(rotacao))
    else:
        fonte.location = ficha(x, y, plano_mm)
        # A face de texto (XY local) vira o plano XZ; na direita a leitura é de fora, na esquerda espelha pelo Z.
        fonte.rotation_euler = (math.radians(90), 0.0, 0.0) if face == 'direita' else (math.radians(90), 0.0, math.radians(180))
        fonte.rotation_euler[1] = math.radians(rotacao)
    me = _malha_do_texto(fonte, nome)
    corte = bpy.data.objects.new(f'{nome}.corte', me)
    corte.matrix_world = fonte.matrix_world.copy()
    _estado['colecao'].objects.link(corte)
    bpy.data.objects.remove(fonte)
    bpy.data.curves.remove(cu)
    corte['zona'] = alvo.get('zona')
    corte['peca'] = alvo.get('peca')
    cortar(alvo, corte)
    return corte


# ------------------------------------------------------------------------------------------------ operações
def cortar(alvo, cortador, depois_do_chanfro=False):
    """Booleano exato de diferença; o cortador fica escondido e fora da exportação. Sem cortador (peça só do modelo
    alto, no nível de jogo) não faz nada. `depois_do_chanfro`: o corte vem depois do chanfro na pilha (acabar), com a
    aresta viva — o entalhe da tampa, que não pode herdar o arredondado grande dos ombros."""
    if alvo is None or cortador is None:
        return
    m = alvo.modifiers.new('corte final' if depois_do_chanfro else 'corte', 'BOOLEAN')
    m.operation = 'DIFFERENCE'
    m.object = cortador
    m.solver = 'EXACT'
    cortador.hide_render = True
    cortador.hide_viewport = True
    cortador['cortador'] = True


def unir(alvo, outro):
    """Booleano exato de união; o outro objeto fica escondido e fora da exportação."""
    if alvo is None or outro is None:
        return
    m = alvo.modifiers.new('uniao', 'BOOLEAN')
    m.operation = 'UNION'
    m.object = outro
    m.solver = 'EXACT'
    outro.hide_render = True
    outro.hide_viewport = True
    outro['cortador'] = True


def rotacionar(ob, eixo, graus, pivo):
    """Gira a malha em volta de um eixo ('X', 'Y', 'Z') passando pelo pivô (mm)."""
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bmesh.ops.rotate(bm, verts=bm.verts[:], cent=v3(*pivo), matrix=Matrix.Rotation(math.radians(graus), 3, eixo))
    bm.to_mesh(ob.data)
    bm.free()


def afinar(ob, fn):
    """Escala a espessura (Y) de cada vértice por fn(x_mm, z_mm): coronhas e guarda-mãos que afinam."""
    if ob is None:
        return
    for vt in ob.data.vertices:
        vt.co.y *= fn(vt.co.x / S, vt.co.z / S)


def fatiar(ob, eixo, valores, onde=None):
    """Corta a malha por planos perpendiculares ao eixo ('X', 'Y' ou 'Z') nas posições (mm): laços novos no meio das
    faces, onde uma deformação depois (a soleira curva vista de cima, a aba dobrada do seletor) precisa de vértices.
    `onde(x, y, z)` (mm, o centro da face) limita o corte às faces escolhidas — só a traseira da coronha, sem gastar
    triângulos no resto; a face vizinha que não entra ganha o vértice novo na aresta comum (sem rachadura)."""
    if ob is None:
        return
    i = 'XYZ'.index(eixo)
    normal = [0.0, 0.0, 0.0]
    normal[i] = 1.0
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    for valor in valores:
        ponto = [0.0, 0.0, 0.0]
        ponto[i] = valor * S
        faces = [f for f in bm.faces if onde is None or onde(*(c / S for c in f.calc_center_median()))]
        geom = list({v for f in faces for v in f.verts}) + list({e for f in faces for e in f.edges}) + faces
        bmesh.ops.bisect_plane(bm, geom=geom, dist=1e-7, plane_co=ponto, plane_no=normal)
    bm.to_mesh(ob.data)
    bm.free()


def deslocar(ob, fn):
    """Move cada vértice por fn(x, y, z) → (dx, dy, dz), tudo em mm no referencial do Blender: curvaturas e dobras
    (a face de trás da soleira, a aba do seletor)."""
    if ob is None:
        return
    for vt in ob.data.vertices:
        dx, dy, dz = fn(vt.co.x / S, vt.co.y / S, vt.co.z / S)
        vt.co.x += dx * S
        vt.co.y += dy * S
        vt.co.z += dz * S


def marcar_chanfro(ob, pred):
    """Chanfro só nas arestas em que pred(a, b) é verdadeiro — a e b são os dois vértices em mm (x, y, z) do Blender:
    a tampa arredonda os ombros de cima sem arredondar as pontas. Liga o limite por peso no acabamento (acabar)."""
    if ob is None:
        return
    me = ob.data
    peso = me.attributes.get('bevel_weight_edge') or me.attributes.new('bevel_weight_edge', 'FLOAT', 'EDGE')
    vs = me.vertices
    mm = lambda i: tuple(c / S for c in vs[i].co)
    valores = [1.0 if pred(mm(e.vertices[0]), mm(e.vertices[1])) else 0.0 for e in me.edges]
    peso.data.foreach_set('value', valores)
    ob['chanfro_peso'] = True


ANGULO_VIVO = 40.0  # graus entre as faces a partir dos quais a aresta fica viva no sombreado (arestas_vivas)


def _grupo_arestas_vivas():
    """Grupo de Geometry Nodes que marca como vivas (sharp_edge) as arestas com mais de ANGULO_VIVO graus entre as faces
    — o "Smooth by Angle" do Blender, feito aqui para não depender do asset. Sem ele o sombreado liso vazava pela borda
    dos cortes feitos depois do chanfro (o entalhe da tampa, as estrias do tubo) e pelas quinas sem chanfro, e a borda
    parecia amassada. Os passos de cilindro (até 36° com 10 segmentos) e de chanfro continuam lisos."""
    nome = f'arestas vivas {ANGULO_VIVO:g}°'
    g = bpy.data.node_groups.get(nome)
    if g is not None:
        return g
    g = bpy.data.node_groups.new(nome, 'GeometryNodeTree')
    g.interface.new_socket('Geometry', in_out='INPUT', socket_type='NodeSocketGeometry')
    g.interface.new_socket('Geometry', in_out='OUTPUT', socket_type='NodeSocketGeometry')
    n, l = g.nodes, g.links
    entrada, saida = n.new('NodeGroupInput'), n.new('NodeGroupOutput')
    angulo = n.new('GeometryNodeInputMeshEdgeAngle')
    liso = n.new('FunctionNodeCompare')
    liso.data_type = 'FLOAT'
    liso.operation = 'LESS_EQUAL'
    liso.inputs[1].default_value = math.radians(ANGULO_VIVO)
    l.new(angulo.outputs['Unsigned Angle'], liso.inputs[0])
    sombreado = n.new('GeometryNodeSetShadeSmooth')
    sombreado.domain = 'EDGE'
    l.new(entrada.outputs[0], sombreado.inputs['Mesh'])
    l.new(liso.outputs['Result'], sombreado.inputs['Shade Smooth'])
    l.new(sombreado.outputs['Mesh'], saida.inputs[0])
    return g


def acabar(ob):
    """Chanfro, solda e normais pelo nível: o alto usa os segmentos da peça (no mínimo 3); o de jogo, 1 segmento nos
    chanfros finos (< 1 mm) e 2 nos outros. A solda (0,001 mm) junta os vértices repetidos que os chanfros deixam onde se
    encontram numa parede fina (cabeça de pino) ou tocam as faces de um booleano — sem ela sobram faces de área zero.
    Arestas vivas acima de ANGULO_VIVO e normais ponderadas por área, mantendo as vivas. Peça com `chanfro_peso`
    (marcar_chanfro) chanfra só as arestas marcadas; os cortes feitos com `depois_do_chanfro` vão para depois do chanfro
    na pilha."""
    largura, seg = ob.get('chanfro', (0.6, 3))
    if largura > 0:
        m = ob.modifiers.new('chanfro', 'BEVEL')
        m.width = largura * S
        m.segments = max(3, int(seg)) if _estado['nivel'] == 'alto' else (1 if largura < 1.0 else 2)
        if ob.get('chanfro_peso'):
            m.limit_method = 'WEIGHT'
        else:
            m.limit_method = 'ANGLE'
            m.angle_limit = math.radians(32.0)
        m.harden_normals = True
        m.miter_outer = 'MITER_ARC'
        m.use_clamp_overlap = True
        for nome in [md.name for md in ob.modifiers if md.name.startswith('corte final')]:
            ob.modifiers.move(ob.modifiers.find(nome), len(ob.modifiers) - 1)
    s = ob.modifiers.new('solda', 'WELD')
    s.mode = 'ALL'
    s.merge_threshold = 0.001 * S
    vivas = ob.modifiers.new('arestas vivas', 'NODES')
    vivas.node_group = _grupo_arestas_vivas()
    w = ob.modifiers.new('normais', 'WEIGHTED_NORMAL')
    w.keep_sharp = True
    return ob


def finalizar(colecao):
    """Chanfro, solda e normais em todas as peças da coleção (os cortadores ficam de fora). Chamar logo depois de
    construir o nível, antes de iniciar o próximo."""
    for ob in colecao.objects:
        if ob.type == 'MESH' and not ob.get('cortador'):
            acabar(ob)
```

- [ ] **Passo 3: Materiais de fábrica** — os da prova, cada um com três nós nomeados que o `assar.py` liga numa
  emissão para assar os canais da `_m`: `canal_aspereza` (0,5 = sem variação), `canal_cor` (0,5 = sem variação; o veio
  na madeira) e `canal_borda` (máscara de borda pelo nó Bevel).

```python file=tools/blender/armas/materiais.py
# Materiais de fábrica procedurais das armas realistas (Fase 4.1a; desenho, seções 4.1 e 4.4; vêm da prova de conceito):
# aço oxidado, aço polido, madeira envernizada, polímero/baquelite com ou sem quadriculado. Servem ao modelo alto — as
# renders da conferência e o assar. Cada um tem três nós nomeados, lidos pelo assar.py:
#   canal_aspereza — variação de aspereza em torno de 0,5 (vira _m.g)
#   canal_cor      — variação de cor em torno de 0,5; o veio na madeira (vira _m.a)
#   canal_borda    — máscara de borda (1 na aresta) pelo nó Bevel (vira _m.b, o desgaste)
# As cores de fábrica vêm do contexto (a pintura de fábrica do registro, src/data/armasReais.js).
import math

import bpy

from .unidades import S


def linear(hexa):
    """'#RRGGBB' → (r, g, b) linear."""
    h = hexa.lstrip('#')
    def canal(v):
        c = int(v, 16) / 255
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return (canal(h[0:2]), canal(h[2:4]), canal(h[4:6]))


def sock(sockets, nome, tipo):
    for s in sockets:
        if s.name == nome and s.type == tipo:
            return s
    raise KeyError(f'{nome} {tipo}')


def novo_mat(nome):
    m = bpy.data.materials.new(nome)
    m.use_nodes = True
    return m, m.node_tree.nodes, m.node_tree.links, m.node_tree.nodes['Principled BSDF']


def mascara_borda(n, l, raio_mm, de=0.90, ate=0.995):
    """Nó Bevel (normal arredondada) e a máscara de borda: 1 onde a normal arredondada se afasta da geométrica."""
    bev = n.new('ShaderNodeBevel')
    bev.samples = 8
    bev.inputs['Radius'].default_value = raio_mm * S
    geo = n.new('ShaderNodeNewGeometry')
    dot = n.new('ShaderNodeVectorMath')
    dot.operation = 'DOT_PRODUCT'
    l.new(bev.outputs['Normal'], dot.inputs[0])
    l.new(geo.outputs['Normal'], dot.inputs[1])
    mr = n.new('ShaderNodeMapRange')
    mr.inputs['From Min'].default_value = de
    mr.inputs['From Max'].default_value = ate
    mr.inputs['To Min'].default_value = 1.0
    mr.inputs['To Max'].default_value = 0.0
    l.new(sock(dot.outputs, 'Value', 'VALUE'), mr.inputs['Value'])
    return bev, mr


def ruido(n, escala, detalhe=6.0):
    """Ruído nas coordenadas que o nó receber (o veio da madeira liga as dele, esticadas ao longo de X)."""
    t = n.new('ShaderNodeTexNoise')
    t.inputs['Scale'].default_value = escala
    t.inputs['Detail'].default_value = detalhe
    return t


def ruido_mm(n, l, periodo_mm, detalhe=2.0):
    """Ruído no referencial do objeto (as peças nascem com a origem na do mundo, em metros), com o período em mm. A
    variação assada tem de ser maior que o texel (≈ 0,34 mm na textura de 2048 do fuzil): abaixo disso vira ruído de
    pixel — caro de guardar sem perdas e sem sentido no jogo, onde o grão fino é o padrão do acabamento, no shader."""
    tc = n.new('ShaderNodeTexCoord')
    t = ruido(n, 1.0 / (periodo_mm * S), detalhe)
    l.new(tc.outputs['Object'], t.inputs['Vector'])
    return t


def faixa(n, l, fonte, a, b):
    mr = n.new('ShaderNodeMapRange')
    mr.inputs['To Min'].default_value = a
    mr.inputs['To Max'].default_value = b
    l.new(fonte, mr.inputs['Value'])
    return mr.outputs['Result']


def mistura_cor(n, l, fator, a, b):
    mx = n.new('ShaderNodeMix')
    mx.data_type = 'RGBA'
    l.new(fator, sock(mx.inputs, 'Factor', 'VALUE'))
    ea, eb = sock(mx.inputs, 'A', 'RGBA'), sock(mx.inputs, 'B', 'RGBA')
    if isinstance(a, tuple):
        ea.default_value = (*a, 1)
    else:
        l.new(a, ea)
    if isinstance(b, tuple):
        eb.default_value = (*b, 1)
    else:
        l.new(b, eb)
    return sock(mx.outputs, 'Result', 'RGBA')


def canal(n, l, nome, fonte=None, valor=0.5):
    """Nó nomeado de um canal assado: um Map Range 0–1 ligado à fonte (ou constante em `valor`)."""
    mr = n.new('ShaderNodeMapRange')
    mr.name = nome
    mr.label = nome
    if fonte is None:
        mr.inputs['Value'].default_value = valor
        mr.inputs['From Min'].default_value = 0.0
        mr.inputs['From Max'].default_value = 1.0
    else:
        l.new(fonte, mr.inputs['Value'])
    return mr


def mat_aco(nome, cor, rug, gasto=(0.30, 0.30, 0.31), borda=0.9):
    """Aço (oxidado, polido, do carregador): aspereza com ruído fino, borda gasta clara, relevo arredondado."""
    m, n, l, b = novo_mat(nome)
    b.inputs['Metallic'].default_value = 1.0
    r = ruido_mm(n, l, 6.0)
    l.new(faixa(n, l, r.outputs['Fac'], rug - 0.07, rug + 0.09), b.inputs['Roughness'])
    bev, borda_m = mascara_borda(n, l, borda)
    l.new(bev.outputs['Normal'], b.inputs['Normal'])
    rc = ruido_mm(n, l, 30.0, 3.0)
    base = mistura_cor(n, l, faixa(n, l, rc.outputs['Fac'], 0.0, 0.25), cor, tuple(c * 0.8 for c in cor))
    l.new(mistura_cor(n, l, borda_m.outputs['Result'], base, gasto), b.inputs['Base Color'])
    canal(n, l, 'canal_aspereza', r.outputs['Fac'])
    canal(n, l, 'canal_cor', rc.outputs['Fac'])
    canal(n, l, 'canal_borda', borda_m.outputs['Result'])
    return m


def mat_madeira(nome, claro, escuro):
    """Madeira laminada envernizada: veio fino e alongado ao longo de X, contraste baixo, verniz."""
    m, n, l, b = novo_mat(nome)
    tc = n.new('ShaderNodeTexCoord')
    mp = n.new('ShaderNodeMapping')
    mp.inputs['Scale'].default_value = (0.25, 7.0, 7.0)
    # O centro dos anéis fica longe das peças, embaixo e à direita (a tora de onde a tábua saiu): nas faces o veio corre
    # ao longo do comprimento, em linhas quase retas. Com o centro no eixo do cano (a origem), perto dele o veio virava
    # listras em pé nos lados do guarda-mão e manchas derretidas nas faces de cima.
    mp.inputs['Location'].default_value = (0.0, 1.3, 1.9)
    l.new(tc.outputs['Object'], mp.inputs['Vector'])
    w = n.new('ShaderNodeTexWave')
    w.wave_type = 'RINGS'
    w.rings_direction = 'X'
    w.inputs['Scale'].default_value = 34.0
    w.inputs['Distortion'].default_value = 14.0
    w.inputs['Detail'].default_value = 3.0
    w.inputs['Detail Roughness'].default_value = 0.7
    l.new(mp.outputs['Vector'], w.inputs['Vector'])
    r = ruido(n, 60.0, 3.0)
    l.new(mp.outputs['Vector'], r.inputs['Vector'])
    mx = n.new('ShaderNodeMath')
    mx.operation = 'MULTIPLY_ADD'
    l.new(w.outputs['Fac'], mx.inputs[0])
    mx.inputs[1].default_value = 0.55
    l.new(r.outputs['Fac'], mx.inputs[2])
    rp = n.new('ShaderNodeValToRGB')
    rp.color_ramp.elements[0].position = 0.35
    rp.color_ramp.elements[0].color = (*escuro, 1)
    rp.color_ramp.elements[1].position = 1.0
    rp.color_ramp.elements[1].color = (*claro, 1)
    l.new(mx.outputs['Value'], rp.inputs['Fac'])
    l.new(rp.outputs['Color'], b.inputs['Base Color'])
    # Verniz acetinado (goma-laca das coronhas da época): com 0,6 de camada e rugosidade 0,18 a face de cima da coronha e
    # dos guarda-mãos virava uma faixa branca sob a luz principal do estúdio.
    b.inputs['Roughness'].default_value = 0.5
    b.inputs['Coat Weight'].default_value = 0.45
    b.inputs['Coat Roughness'].default_value = 0.3
    bev, borda_m = mascara_borda(n, l, 2.0)
    l.new(bev.outputs['Normal'], b.inputs['Normal'])
    rr = ruido_mm(n, l, 8.0)
    canal(n, l, 'canal_aspereza', rr.outputs['Fac'])
    veio = n.new('ShaderNodeMath')
    veio.operation = 'MULTIPLY'
    l.new(mx.outputs['Value'], veio.inputs[0])
    veio.inputs[1].default_value = 1 / 1.55
    canal(n, l, 'canal_cor', veio.outputs['Value'])
    canal(n, l, 'canal_borda', borda_m.outputs['Result'])
    return m


def mat_plastico(nome, cor, rug, relevo=0.0, pontilhado_mm=0.7, quadriculado=False):
    """Polímero/baquelite: pontilhado em relevo (relevo > 0, grão de `pontilhado_mm`) ou quadriculado a 45°
    (quadriculado=True)."""
    m, n, l, b = novo_mat(nome)
    r = ruido_mm(n, l, 25.0, 3.0)
    l.new(mistura_cor(n, l, faixa(n, l, r.outputs['Fac'], 0.0, 0.35), cor, tuple(c * 0.7 for c in cor)), b.inputs['Base Color'])
    b.inputs['Roughness'].default_value = rug
    bev, borda_m = mascara_borda(n, l, 1.2)
    altura = None
    if quadriculado:
        tc = n.new('ShaderNodeTexCoord')
        onda = []
        for ang in (45.0, -45.0):
            mp = n.new('ShaderNodeMapping')
            mp.inputs['Rotation'].default_value = (math.radians(90), math.radians(ang), 0)
            l.new(tc.outputs['Object'], mp.inputs['Vector'])
            w = n.new('ShaderNodeTexWave')
            w.wave_type = 'BANDS'
            w.inputs['Scale'].default_value = 420.0
            w.inputs['Distortion'].default_value = 0.0
            l.new(mp.outputs['Vector'], w.inputs['Vector'])
            onda.append(w)
        mul = n.new('ShaderNodeMath')
        mul.operation = 'MULTIPLY'
        l.new(onda[0].outputs['Fac'], mul.inputs[0])
        l.new(onda[1].outputs['Fac'], mul.inputs[1])
        altura = mul.outputs['Value']
    elif relevo > 0:
        altura = ruido_mm(n, l, pontilhado_mm).outputs['Fac']
    if altura is not None:
        bp = n.new('ShaderNodeBump')
        bp.inputs['Strength'].default_value = 0.55 if quadriculado else relevo
        bp.inputs['Distance'].default_value = 0.0003 if quadriculado else 0.0004
        l.new(altura, bp.inputs['Height'])
        l.new(bev.outputs['Normal'], bp.inputs['Normal'])
        l.new(bp.outputs['Normal'], b.inputs['Normal'])
    else:
        l.new(bev.outputs['Normal'], b.inputs['Normal'])
    canal(n, l, 'canal_aspereza', ruido_mm(n, l, 6.0).outputs['Fac'])
    canal(n, l, 'canal_cor', r.outputs['Fac'])
    canal(n, l, 'canal_borda', borda_m.outputs['Result'])
    return m


def materiais_de_fabrica(fabrica):
    """Os materiais do modelo alto a partir da pintura de fábrica (zonas → cores do contexto)."""
    z = fabrica['zonas']
    aco = linear(z['corpo']['cor'])
    return {
        'aco': mat_aco('aço oxidado', aco, 0.34, gasto=(0.32, 0.32, 0.34)),
        'aco_detalhes': mat_aco('aço dos detalhes', linear(z['detalhes']['cor']), 0.34, gasto=(0.36, 0.36, 0.38)),
        'aco_carregador': mat_aco('aço do carregador', linear(z['carregador']['cor']), 0.34, gasto=(0.36, 0.37, 0.39)),
        'aco_polido': mat_aco('aço polido', linear(z['interno']['cor']), 0.22, gasto=(0.6, 0.6, 0.6)),
        'madeira': mat_madeira('madeira', linear(z['guarnicao']['cor']), linear(z['guarnicao'].get('cor2') or z['guarnicao']['cor'])),
    }
```

- [ ] **Passo 4: Estúdio da conferência** (o da prova: luzes em W com a cena em metros, câmera, GPU e AgX)

```python file=tools/blender/armas/estudio.py
# Estúdio das renders de conferência (Fase 4.1a; desenho, seção 4.7; vem da prova de conceito): fundo escuro, quatro
# luzes de área (principal quente, preenchimento frio, recorte e topo) em watts para a cena em metros, câmeras
# perspectiva e ortográfica, Cycles na GPU (OptiX, senão CUDA) e AgX com contraste médio-alto.
import bmesh
import bpy
from mathutils import Vector


def montar(centro=(-0.45, 0.0, -0.05)):
    """Fundo e luzes em volta do centro da arma (metros)."""
    sc = bpy.context.scene
    w = bpy.data.worlds.new('mundo')
    sc.world = w
    w.use_nodes = True
    w.node_tree.nodes['Background'].inputs['Color'].default_value = (0.018, 0.017, 0.016, 1)
    w.node_tree.nodes['Background'].inputs['Strength'].default_value = 1.0
    chao = bpy.data.materials.new('fundo')
    chao.use_nodes = True
    chao.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (0.05, 0.048, 0.045, 1)
    chao.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = 0.8
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=3.0)
    bmesh.ops.translate(bm, vec=(centro[0], 0.2, centro[2] - 0.22), verts=bm.verts[:])
    me = bpy.data.meshes.new('fundo')
    bm.to_mesh(me)
    bm.free()
    fundo = bpy.data.objects.new('fundo', me)
    me.materials.append(chao)
    sc.collection.objects.link(fundo)
    c = Vector(centro)

    def luz(nome, pos, tam, energia, cor):
        d = bpy.data.lights.new(nome, 'AREA')
        d.size = tam
        d.energy = energia
        d.color = cor
        o = bpy.data.objects.new(nome, d)
        sc.collection.objects.link(o)
        o.location = c + Vector(pos)
        o.rotation_euler = (c - o.location).to_track_quat('-Z', 'Y').to_euler()
    luz('principal', (0.25, -0.9, 0.95), 1.2, 30, (1.0, 0.9, 0.78))
    luz('preenchimento', (-0.45, -0.7, 0.25), 1.0, 9, (0.75, 0.85, 1.0))
    luz('recorte', (-0.05, 0.9, 0.55), 0.8, 22, (1.0, 1.0, 1.0))
    luz('topo', (0.0, 0.0, 1.25), 1.8, 14, (1.0, 0.97, 0.92))
    return fundo


def camera(nome, pos, alvo, lente=50, orto=None):
    """Câmera em `pos` olhando para `alvo` (metros); `orto` = largura da vista ortográfica (metros)."""
    sc = bpy.context.scene
    d = bpy.data.cameras.new(nome)
    d.lens = lente
    d.clip_start = 0.005
    if orto:
        d.type = 'ORTHO'
        d.ortho_scale = orto
    o = bpy.data.objects.new(nome, d)
    sc.collection.objects.link(o)
    o.location = pos
    o.rotation_euler = (Vector(alvo) - Vector(pos)).to_track_quat('-Z', 'Y').to_euler()
    return o


def gpu():
    """Cycles na GPU (OptiX, senão CUDA); devolve o dispositivo usado."""
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'
    prefs = bpy.context.preferences.addons['cycles'].preferences
    for tipo in ('OPTIX', 'CUDA'):
        try:
            prefs.compute_device_type = tipo
            prefs.get_devices()
            if any(d.type == tipo for d in prefs.devices):
                for d in prefs.devices:
                    d.use = d.type == tipo
                sc.cycles.device = 'GPU'
                return tipo
        except Exception:
            pass
    sc.cycles.device = 'CPU'
    return 'CPU'


def render(largura, altura, amostras=160):
    sc = bpy.context.scene
    dispositivo = gpu()
    sc.cycles.samples = amostras
    sc.cycles.use_denoising = True
    sc.render.resolution_x = largura
    sc.render.resolution_y = altura
    sc.render.resolution_percentage = 100
    sc.view_settings.view_transform = 'AgX'
    sc.view_settings.look = 'AgX - Medium High Contrast'
    return dispositivo
```

- [ ] **Passo 5: Zonas e soquetes**

```python file=tools/blender/armas/zonas.py
# Zonas das armas realistas (Fase 4.1a; desenho, seção 4.2): grupos de material, a base das skins. No modelo de jogo cada
# peça recebe o material da sua zona, que se chama exatamente como a zona — é assim que o .glb diz a zona de cada
# primitiva (plano da 4.1a, D2). As cores aqui só servem para ver no Blender; o jogo pinta pelo acabamento.
import bpy

ZONAS = ('corpo', 'guarnicao', 'carregador', 'detalhes', 'interno')
_VISTA = {
    'corpo': (0.03, 0.031, 0.036), 'guarnicao': (0.37, 0.135, 0.05), 'carregador': (0.075, 0.08, 0.088),
    'detalhes': (0.05, 0.05, 0.055), 'interno': (0.42, 0.42, 0.43),
}


def material_da_zona(zona):
    assert zona in ZONAS, zona
    m = bpy.data.materials.get(zona)
    if m is None:
        m = bpy.data.materials.new(zona)
        m.use_nodes = True
        b = m.node_tree.nodes['Principled BSDF']
        b.inputs['Base Color'].default_value = (*_VISTA[zona], 1)
        b.inputs['Metallic'].default_value = 0.0 if zona == 'guarnicao' else 1.0
        b.inputs['Roughness'].default_value = 0.4
    return m


def aplicar_zonas(colecao):
    """Troca o material de cada peça da coleção (modelo de jogo) pelo da zona dela."""
    for ob in colecao.objects:
        if ob.type != 'MESH' or ob.get('cortador'):
            continue
        z = ob.get('zona')
        if z not in ZONAS:
            raise ValueError(f'{ob.name}: zona "{z}" desconhecida (use {", ".join(ZONAS)})')
        ob.data.materials.clear()
        ob.data.materials.append(material_da_zona(z))
```

```python file=tools/blender/armas/soquetes.py
# Soquetes e peças móveis das armas realistas (Fase 4.1a; desenho, seção 4.2). Soquete = vazio `soquete_<nome>` com
# posição e orientação. Peça móvel = as peças marcadas com o mesmo `peca`, com os modificadores aplicados, juntadas num
# objeto `<nivel>_<peca>` triangulado, com a origem no pivô real (o eixo de giro ou a linha de deslize); `base` é o resto
# da arma. As
# faces da base que ficam inteiras dentro de outra peça da base (cano dentro do munhão, espiga da coronha dentro do
# receptor) saem no modelo de jogo — só a face com todos os cantos e o centro dentro da outra peça e longe da superfície
# dela, para nenhuma face em parte visível sumir; as das peças móveis ficam, porque aparecem quando a peça se mexe.
import math

import bmesh
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

from .unidades import S, ficha


def soquete(colecao, nome, x, y, lado=0.0, rot=(0.0, 0.0, 0.0)):
    """Vazio `soquete_<nome>` no ponto (x, y) da ficha, com `lado` = Y do Blender (mm) e a rotação XYZ em graus."""
    ob = bpy.data.objects.new(f'soquete_{nome}', None)
    ob.empty_display_type = 'ARROWS'
    ob.empty_display_size = 0.02
    ob.location = ficha(x, y, lado)
    ob.rotation_euler = [math.radians(a) for a in rot]
    colecao.objects.link(ob)
    return ob


def _aplicadas(objetos, colecao, nome):
    """Cópias das peças com os modificadores aplicados (normais personalizadas preservadas), cada uma só com o material
    da zona dela: o booleano deixa na lista da malha avaliada o material do cortador, sem face nenhuma."""
    dg = bpy.context.evaluated_depsgraph_get()
    copias = []
    for ob in objetos:
        me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg), preserve_all_data_layers=True, depsgraph=dg)
        zona = ob.data.materials[0]
        me.materials.clear()
        me.materials.append(zona)
        me.polygons.foreach_set('material_index', [0] * len(me.polygons))
        c = bpy.data.objects.new(f'{nome}.{ob.name}', me)
        c.matrix_world = ob.matrix_world.copy()
        colecao.objects.link(c)
        copias.append(c)
    return copias


_DIRECOES = (Vector((0.577, 0.577, 0.577)), Vector((-0.267, 0.534, -0.802)), Vector((0.832, -0.555, 0.0)))


def _dentro(bvh, p):
    """Ponto dentro de uma malha fechada: paridade dos cruzamentos de um raio, em três direções (a maioria decide; um
    raio que raspa uma aresta conta um cruzamento a mais)."""
    votos = 0
    for direcao in _DIRECOES:
        n = 0
        origem = p.copy()
        for _ in range(64):
            hit, _nrm, _i, _d = bvh.ray_cast(origem, direcao)
            if hit is None:
                break
            n += 1
            origem = hit + direcao * 1e-6
        votos += n % 2
    return votos >= 2


def _escondida(bvh, pontos, folga):
    """Todos os pontos dentro da malha fechada e a mais de `folga` (m) da superfície dela: ponto na superfície (peças
    que só se encostam) não esconde nada."""
    for p in pontos:
        _co, _nrm, _i, dist = bvh.find_nearest(p)
        if dist is None or dist < folga or not _dentro(bvh, p):
            return False
    return True


def remover_escondidas(copias, folga_mm=0.02):
    """Tira das cópias da base as faces inteiras dentro de outra cópia da base (malhas fechadas): os cantos e o centro
    da face dentro dela e a mais de `folga_mm` da superfície."""
    dg = bpy.context.evaluated_depsgraph_get()
    arvores = {c.name: BVHTree.FromObject(c, dg, deform=False) for c in copias}
    mundos = {c.name: c.matrix_world for c in copias}
    caixas = {}
    for c in copias:
        pts = [c.matrix_world @ Vector(v) for v in c.bound_box]
        caixas[c.name] = (Vector((min(q.x for q in pts), min(q.y for q in pts), min(q.z for q in pts))),
                          Vector((max(q.x for q in pts), max(q.y for q in pts), max(q.z for q in pts))))
    removidas = 0
    for c in copias:
        bm = bmesh.new()
        bm.from_mesh(c.data)
        tirar = []
        for f in bm.faces:
            pontos = [mundos[c.name] @ f.calc_center_median()] + [mundos[c.name] @ v.co for v in f.verts]
            for outra in copias:
                if outra is c:
                    continue
                lo, hi = caixas[outra.name]
                if not all(lo.x <= q.x <= hi.x and lo.y <= q.y <= hi.y and lo.z <= q.z <= hi.z for q in pontos):
                    continue
                inversa = mundos[outra.name].inverted()
                if _escondida(arvores[outra.name], [inversa @ q for q in pontos], folga_mm * S):
                    tirar.append(f)
                    break
        if tirar:
            bmesh.ops.delete(bm, geom=tirar, context='FACES')
            removidas += len(tirar)
            bm.to_mesh(c.data)
        bm.free()
    return removidas


def juntar_pecas(colecao_origem, colecao_destino, prefixo, pivos, filtro=None):
    """Um objeto `<prefixo>_<peca>` por peça (base e móveis), com a origem no pivô (mm da ficha).
    `filtro(ob)` decide que peças entram (o LOD tira as pequenas). Devolve {peca: objeto, '_removidas': n}."""
    grupos = {}
    for ob in colecao_origem.objects:
        if ob.type != 'MESH' or ob.get('cortador') or ob.hide_render:
            continue
        if filtro and not filtro(ob):
            continue
        grupos.setdefault(ob.get('peca', 'base'), []).append(ob)
    faltando = [p for p in pivos if p not in grupos]
    if faltando:
        raise ValueError(f'peças sem nenhum objeto: {", ".join(faltando)}')
    saida = {'_removidas': 0}
    for peca, objetos in grupos.items():
        nome = f'{prefixo}_{peca}'
        copias = _aplicadas(objetos, colecao_destino, nome)
        if peca == 'base':
            saida['_removidas'] = remover_escondidas(copias)
        bpy.ops.object.select_all(action='DESELECT')
        for c in copias:
            c.select_set(True)
        bpy.context.view_layer.objects.active = copias[0]
        if len(copias) > 1:
            bpy.ops.object.join()
        alvo = bpy.context.view_layer.objects.active
        alvo.name = nome
        alvo.data.name = nome
        # Triangulado (desenho, seção 4.3): o exportador só calcula as tangentes (MikkTSpace) em triângulos e
        # quadriláteros e pula sem aviso a malha com n-gonos; triangulada aqui, o assar e o .glb usam o mesmo
        # referencial do relevo. As normais personalizadas (chanfros duros, normais ponderadas) ficam.
        tri = alvo.modifiers.new('triangular', 'TRIANGULATE')
        tri.quad_method = 'BEAUTY'
        tri.ngon_method = 'BEAUTY'
        tri.keep_custom_normals = True
        with bpy.context.temp_override(object=alvo, active_object=alvo):
            bpy.ops.object.modifier_apply(modifier='triangular')
        (px, py), extras = pivos[peca]
        bpy.context.scene.cursor.location = ficha(px, py)
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
        for chave in list(alvo.keys()):
            del alvo[chave]
        for chave, valor in extras.items():
            alvo[chave] = valor
        saida[peca] = alvo
    return saida
```

- [ ] **Passo 6: Conferir que o pacote importa no Blender** (sem janela; o `S:\blender.exe` do `local.json`):

```bash
cd "/c/Users/T-Gamer/Desktop/game tiro/trabalho-4.1a"
"/s/blender.exe" -b --factory-startup --python-expr "import sys; sys.path.insert(0, 'tools/blender'); from armas import pecas, materiais, estudio, zonas, soquetes; print('MASSACRE-OK', pecas.nivel())" 2>&1 | grep MASSACRE
```

Expected: `MASSACRE-OK alto`.

---

### Tarefa 6: A AK-47 tipo 3 no nível final

**Files:**
- Create: `tools/blender/armas/validar.py`, `tools/blender/armas/ak47.py`

O script da prova (`ak_v3.py`, função `construir3`) portado para a biblioteca, lendo os contornos, tornos e pontos da
ficha, com cada peça na zona e na peça móvel certas, mais tudo o que a prova não tinha e a arma real tem: a cabeça do
ferrolho na janela, o cão, a espiga e o parafuso da coronha, os parafusos e o alçapão da soleira, o parafuso do punho,
os rebites do guarda-mato, o retentor do guarda-mão, as argolas de bandoleira (lado esquerdo), as marcações estampadas
(letras do seletor, graduação da alça, número de série e marca de controle genéricos — regra 9: nada de marca de
fabricante) e o recorte de alívio dos dois lados. O que a prova deixou mediano (seção 11 do desenho: madeira chapada,
aço limpo demais, linhas e marcações do receptor) é resolvido aqui e na revisão do passo 3. O tipo 3 tem **punho de
madeira liso** (o quadriculado de baquelite é da AKM).

- [ ] **Passo 1: A validação** (a Tarefa 8 usa a mesma no `construir`; aqui ela já mede a forma)

```python file=tools/blender/armas/validar.py
# Validação que bloqueia a exportação das armas realistas (Fase 4.1a; desenho em docs/superpowers/specs/
# 2026-09-26-armas-realistas-design.md, seção 4.6): as medidas-chave dentro de ±1 % do alvo da ficha; a silhueta de lado
# ≥ 98 % com a tolerância de 1 px da foto — a máscara renderizada pela câmera ortográfica que olha o lado direito contra
# o contorno da ficha, na mesma conta de tools/regua/geometria.js (rasterizar pelo centro da célula, dilatar por disco,
# IoU bruto e com tolerância), aqui em numpy; os orçamentos de triângulos e de texturas; os soquetes, as zonas e as peças
# com os nomes certos; as peças fechadas e sem faces degeneradas; a UV sem sobreposição. Grava a sobreposição da
# silhueta (cinza = as duas, verde = falta no modelo, magenta = sobra) e a máscara para a conferência.
import math
import os

import bmesh
import bpy
import numpy as np

from . import lod
from .unidades import S

MM_POR_PX = 0.5   # resolução da máscara de lado
MARGEM_MM = 20.0  # folga em volta do contorno da ficha


def rasterizar(aneis, x0, y1, passo, largura, altura):
    """Máscara (bool, linha 0 em cima) de um contorno com buracos: o centro da célula decide, pela paridade."""
    mascara = np.zeros((altura, largura), bool)
    for j in range(altura):
        y = y1 - (j + 0.5) * passo
        cruz = []
        for anel in aneis:
            n = len(anel)
            for k in range(n):
                ax, ay = anel[k]
                bx, by = anel[(k + 1) % n]
                if (ay > y) != (by > y):
                    cruz.append(ax + (y - ay) / (by - ay) * (bx - ax))
        cruz.sort()
        for k in range(0, len(cruz) - 1, 2):
            i0 = max(0, math.ceil((cruz[k] - x0) / passo - 0.5))
            i1 = min(largura - 1, math.floor((cruz[k + 1] - x0) / passo - 0.5))
            if i1 >= i0:
                mascara[j, i0:i1 + 1] = True
    return mascara


def dilatar(m, r):
    """Dilatação por um disco de raio r pixels."""
    if r <= 0:
        return m.copy()
    out = np.zeros_like(m)
    h, w = m.shape
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            if dx * dx + dy * dy > r * r:
                continue
            ys0, ys1 = max(0, -dy), min(h, h - dy)
            xs0, xs1 = max(0, -dx), min(w, w - dx)
            out[ys0 + dy:ys1 + dy, xs0 + dx:xs1 + dx] |= m[ys0:ys1, xs0:xs1]
    return out


def iou(a, b, r=0):
    """IoU bruto e com tolerância r (a diferença a até r pixels da outra máscara não conta)."""
    da, db = (dilatar(a, r), dilatar(b, r)) if r > 0 else (a, b)
    inter = int((a & b).sum())
    so_a = a & ~b
    so_b = b & ~a
    conta = int((so_a & ~db).sum() + (so_b & ~da).sum())
    return {
        'iouBruto': inter / max(1, inter + int(so_a.sum()) + int(so_b.sum())),
        'iouTolerancia': inter / max(1, inter + conta),
    }


def _mascara_render(objetos, x0, y0, x1, y1, pasta):
    """Máscara (bool, linha 0 em cima) dos objetos vistos do lado direito, na área (mm) pedida, a MM_POR_PX."""
    sc = bpy.context.scene
    largura = int(round((x1 - x0) / MM_POR_PX))
    altura = int(round((y1 - y0) / MM_POR_PX))
    cam_d = bpy.data.cameras.new('camera_mascara')
    cam_d.type = 'ORTHO'
    cam_d.ortho_scale = (x1 - x0) * S
    cam_d.clip_start = 0.01
    cam_d.clip_end = 10.0
    cam = bpy.data.objects.new('camera_mascara', cam_d)
    sc.collection.objects.link(cam)
    cam.location = ((x0 + x1) / 2 * S, -3.0, (y0 + y1) / 2 * S)
    cam.rotation_euler = (math.radians(90), 0.0, 0.0)  # olha para +Y: o lado direito da arma, com a boca à direita
    escondidos = [o for o in sc.objects if o.type in {'MESH', 'CURVE', 'FONT'} and o not in objetos and not o.hide_render]
    for o in escondidos:
        o.hide_render = True
    antes = (sc.render.engine, sc.camera, sc.render.film_transparent, sc.render.resolution_x, sc.render.resolution_y,
             sc.render.resolution_percentage, sc.display.render_aa, sc.render.filepath)
    sc.render.engine = 'BLENDER_WORKBENCH'
    sc.display.shading.light = 'FLAT'
    sc.display.shading.color_type = 'SINGLE'
    sc.display.shading.single_color = (1, 1, 1)
    sc.display.render_aa = 'OFF'
    sc.render.film_transparent = True
    sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = largura, altura, 100
    sc.render.image_settings.file_format = 'PNG'
    sc.render.image_settings.color_mode = 'RGBA'
    sc.camera = cam
    caminho = os.path.join(pasta, 'mascara_lado.png')
    sc.render.filepath = caminho
    bpy.ops.render.render(write_still=True)
    img = bpy.data.images.load(caminho, check_existing=False)
    px = np.empty(largura * altura * 4, np.float32)
    img.pixels.foreach_get(px)
    alfa = px.reshape(altura, largura, 4)[::-1, :, 3] > 0.5
    bpy.data.images.remove(img)
    (sc.render.engine, sc.camera, sc.render.film_transparent, sc.render.resolution_x, sc.render.resolution_y,
     sc.render.resolution_percentage, sc.display.render_aa, sc.render.filepath) = antes
    for o in escondidos:
        o.hide_render = False
    bpy.data.objects.remove(cam)
    bpy.data.cameras.remove(cam_d)
    return alfa


def silhueta(objetos, ficha, pasta):
    """IoU da silhueta de lado (render × contorno da ficha), com a tolerância de 1 px da foto; grava a sobreposição."""
    os.makedirs(pasta, exist_ok=True)
    xs = [p[0] for p in ficha['contorno']]
    ys = [p[1] for p in ficha['contorno']]
    x0, x1 = min(xs) - MARGEM_MM, max(xs) + MARGEM_MM
    y0, y1 = min(ys) - MARGEM_MM, max(ys) + MARGEM_MM
    modelo = _mascara_render(objetos, x0, y0, x1, y1, pasta)
    altura, largura = modelo.shape
    foto = rasterizar([ficha['contorno'], *ficha.get('buracos', [])], x0, y1, MM_POR_PX, largura, altura)
    mm_px_foto = next(f for f in ficha['fotos'] if f['lado'].startswith('direito'))['mmPorPixel']
    r = max(1, round(mm_px_foto / MM_POR_PX))
    res = iou(modelo, foto, r)
    rgba = np.zeros((altura, largura, 4), np.float32)
    rgba[..., 3] = 1.0
    rgba[modelo & foto] = (0.55, 0.55, 0.55, 1.0)
    rgba[foto & ~modelo] = (0.1, 0.85, 0.2, 1.0)
    rgba[modelo & ~foto] = (0.9, 0.1, 0.8, 1.0)
    img = bpy.data.images.new('sobreposicao', largura, altura, alpha=True)
    img.pixels.foreach_set(np.ascontiguousarray(rgba[::-1]).ravel())
    img.filepath_raw = os.path.join(pasta, 'sobreposicao.png')
    img.file_format = 'PNG'
    img.save()
    bpy.data.images.remove(img)
    return {'silhueta': {'iouBruto': round(res['iouBruto'], 5), 'iouTolerancia': round(res['iouTolerancia'], 5),
                         'raioToleranciaPx': r, 'mmPorPx': MM_POR_PX}}


def _peca(ob):
    """A peça de um objeto: a propriedade (peças separadas) ou o fim do nome `<nivel>_<peca>` (peças juntadas)."""
    return ob.get('peca') or ob.name.split('_', 1)[-1]


def _extremos(objetos):
    """Mínimo e máximo (mm, no referencial do Blender) dos vértices avaliados dos objetos."""
    dg = bpy.context.evaluated_depsgraph_get()
    lo = np.full(3, np.inf)
    hi = np.full(3, -np.inf)
    for ob in objetos:
        ev = ob.evaluated_get(dg)
        me = ev.to_mesh()
        co = np.empty(len(me.vertices) * 3, np.float32)
        me.vertices.foreach_get('co', co)
        co = co.reshape(-1, 3)
        mw = np.array(ob.matrix_world)
        w = co @ mw[:3, :3].T + mw[:3, 3]
        lo = np.minimum(lo, w.min(0))
        hi = np.maximum(hi, w.max(0))
        ev.to_mesh_clear()
    return lo / S, hi / S


def medidas(objetos, canos, soquetes_def, ficha):
    """As cinco medidas-chave (mm) com o alvo da ficha e o erro relativo."""
    lo, hi = _extremos(objetos)
    lo_s, hi_s = _extremos([o for o in objetos if _peca(o) != 'carregador'])
    lo_c, hi_c = _extremos(canos)
    soq = {nome: xy for nome, xy, _lado, _rot in soquetes_def}
    valores = {
        'comprimento': hi[0] - lo[0],
        'cano': hi_c[0] - lo_c[0],
        'raioDeMira': abs(soq['mira_tras'][0] - soq['mira_frente'][0]),
        'alturaSemCarregador': hi_s[2] - lo_s[2],
        'alturaComCarregador': hi[2] - lo[2],
    }
    saida = {}
    for nome, mm in valores.items():
        alvo = ficha['medidas'][nome]['mm']
        saida[nome] = {'mm': round(float(mm), 2), 'alvo': alvo, 'erro': round((float(mm) - alvo) / alvo, 5)}
    return saida


def malha(objetos):
    """Peças fechadas (arestas que não são de exatamente duas faces) e sem faces degeneradas, com os modificadores."""
    dg = bpy.context.evaluated_depsgraph_get()
    abertas = 0
    degeneradas = 0
    nomes = []
    for ob in objetos:
        ev = ob.evaluated_get(dg)
        me = ev.to_mesh()
        bm = bmesh.new()
        bm.from_mesh(me)
        a = sum(1 for e in bm.edges if not e.is_manifold)
        d = sum(1 for f in bm.faces if f.calc_area() < 1e-12)
        bm.free()
        ev.to_mesh_clear()
        abertas += a
        degeneradas += d
        if a or d:
            nomes.append(ob.name)
    return {'bordasAbertas': abertas, 'facesDegeneradas': degeneradas, 'pecasComProblema': nomes[:20]}


def relatorio_e_problemas(ctx, ficha, lods, soquetes_def, soquetes_nomes, canos, pecas_jogo, lados, uv, densidade, pasta):
    """Tudo o que a seção 4.6 pede, num dicionário do relatório e na lista de problemas (vazia = aprovado)."""
    perto = [o for k, o in lods['perto'].items() if not k.startswith('_')]
    rel = {}
    rel.update(silhueta(perto, ficha, pasta))
    rel['medidas'] = medidas(perto, canos, soquetes_def, ficha)
    rel['malha'] = malha(pecas_jogo)
    rel['malha']['facesNaoTrianguladas'] = sum(1 for o in perto for f in o.data.polygons if f.loop_total > 3)
    rel['lods'] = {nome: {'triangulos': lod.triangulos([o for k, o in partes.items() if not k.startswith('_')])}
                   for nome, partes in lods.items()}
    rel['uv'] = {'sobreposicao': uv, 'densidadeTexel': densidade}
    rel['soquetes'] = sorted(soquetes_nomes)
    rel['pecas'] = ['base', *ctx['pecas']]
    rel['zonas'] = list(ctx['zonas'])
    orc = ctx['orcamento']
    p = []
    if rel['silhueta']['iouTolerancia'] < 0.98:
        p.append(f"silhueta {rel['silhueta']['iouTolerancia']:.4f} com tolerância (mínimo 0,98)")
    for nome, d in rel['medidas'].items():
        if abs(d['erro']) > 0.01:
            p.append(f"medida {nome}: {d['mm']} mm contra {d['alvo']} mm ({d['erro'] * 100:+.2f} %)")
    if rel['malha']['bordasAbertas'] or rel['malha']['facesDegeneradas']:
        p.append(f"malha: {rel['malha']['bordasAbertas']} arestas abertas, {rel['malha']['facesDegeneradas']} faces degeneradas "
                 f"({', '.join(rel['malha']['pecasComProblema'])})")
    if rel['malha']['facesNaoTrianguladas']:
        p.append(f"perto: {rel['malha']['facesNaoTrianguladas']} faces com mais de três lados (o .glb sairia sem tangentes)")
    if uv:
        p.append(f'UV: {uv} texels sobrepostos (grade de conferência de 1024)')
    for nome, d in rel['lods'].items():
        if d['triangulos'] > orc['triangulos'][nome]:
            p.append(f"{nome}: {d['triangulos']} triângulos (orçamento {orc['triangulos'][nome]})")
    for nome, partes in lods.items():
        tem = {k for k in partes if not k.startswith('_')}
        for pc in rel['pecas']:
            if pc not in tem:
                p.append(f'{nome}: falta a peça {pc}')
    for s in ctx['soquetes']:
        if s not in soquetes_nomes:
            p.append(f'falta o soquete {s}')
    usadas = {slot.material.name for o in perto for slot in o.material_slots if slot.material}
    for z in ctx['zonas']:
        if z not in usadas:
            p.append(f'falta a zona {z}')
    for z in sorted(usadas - set(ctx['zonas'])):
        p.append(f'material fora das zonas: {z}')
    for nome, (lado, esperado) in lados.items():
        if lado != esperado:
            p.append(f'{nome}: textura de {lado} px (esperava {esperado})')
    return rel, p
```

- [ ] **Passo 2: O script da arma**

```python file=tools/blender/armas/ak47.py
# AK-47 tipo 3 (receptor fresado, coronha fixa de madeira) — Fase 4.1a (desenho em docs/superpowers/specs/
# 2026-09-26-armas-realistas-design.md; vem de prova-armas-2026-09-26/blender/ak_v3.py). Construída em mm no
# referencial da ficha (tools/blender/refs/ak47.json): contornos por peça, tornos e pontos medidos na foto
# "AK-47 assault rifle.jpg" (Commons, domínio público) pela régua; as larguras e as peças que só se veem de cima ou de
# baixo vêm da planta de fábrica soviética (ficha, vistaDeCima). Lado direito da arma = -Y do Blender.
# Marcações genéricas (regra 9): letras do seletor, graduação da alça, número de série e marca de controle — nenhuma
# marca de fabricante.
import math

from . import pecas as P

ORIGEM_MM = (-551.0, 0.0)  # o pino do gatilho no eixo do cano: a origem da arma no jogo (plano da 4.1a, D1)
PECAS = ('ferrolho', 'carregador', 'gatilho', 'cao', 'seletor')
FOLGA_EMBUTIDA = 0.08  # mm entre uma peça embutida na madeira (as espigas) e o rebaixo dela: a linha do encaixe


def pivos(ficha):
    """Pivô (mm, ficha) e extras de cada peça (direções no referencial do jogo: +X boca, +Y cima, +Z direita)."""
    pt = ficha['pontos']
    return {
        'base': (ORIGEM_MM, {}),
        'ferrolho': (tuple(pt['manejo']), {'eixo': [-1.0, 0.0, 0.0]}),
        'carregador': (tuple(pt['travaCarregador']), {'eixo_giro': [0.0, 0.0, 1.0]}),
        'gatilho': (tuple(pt['pinoGatilho']), {'eixo_giro': [0.0, 0.0, 1.0]}),
        'cao': (tuple(pt['pinoCao']), {'eixo_giro': [0.0, 0.0, 1.0]}),
        'seletor': (tuple(pt['eixoSeletor']), {'eixo_giro': [0.0, 0.0, 1.0]}),
    }


def soquetes(ficha):
    """(nome, (x, y) da ficha, lado = Y do Blender em mm, rotação XYZ em graus no Blender)."""
    pt = ficha['pontos']
    j = pt['janela']
    face_direita = -ficha['vistaDeCima']['larguras']['receptor']['mm'] / 2
    return [
        ('boca', (0.0, 0.0), 0.0, (0, 0, 0)),
        # A cápsula sai pela direita, da face do receptor, um pouco para a frente e para cima: +X do soquete girado -75° em
        # Z e -15° em Y.
        ('ejecao', ((j['x0'] + j['x1']) / 2, (j['y0'] + j['y1']) / 2), face_direita, (0, -15, -75)),
        ('carregador', (-457.0, -40.0), 0.0, (0, 0, 0)),
        ('mira_tras', tuple(pt['entalheAlca']), 0.0, (0, 0, 0)),
        ('mira_frente', tuple(pt['posteMassa']), 0.0, (0, 0, 0)),
        # O +Z do soquete (o +Y no jogo) sobe pelo eixo do punho, inclinado 27,8° para trás.
        ('mao_d', (-606.0, -100.0), 0.0, (0, 27.8, 0)),
        ('mao_e', (-290.0, -30.0), 0.0, (0, 0, 0)),
    ]


# ------------------------------------------------------------------------------------------------ contas
def _entre(v, a, b):
    """0 até a, 1 a partir de b, linear no meio (a < b)."""
    return min(1.0, max(0.0, (v - a) / (b - a)))


def _suave(t):
    """Degrau suave de 0 a 1 (smoothstep)."""
    return t * t * (3.0 - 2.0 * t)


def _na_linha(pts, v):
    """Valor em v de uma polilinha [(v, valor)] ordenada por v, preso nas pontas."""
    if v <= pts[0][0]:
        return pts[0][1]
    for (va, a), (vb, b) in zip(pts, pts[1:]):
        if v <= vb:
            return a + (b - a) * (v - va) / (vb - va)
    return pts[-1][1]


def _girar(objetos, eixo, graus, pivo):
    """pecas.rotacionar em vários objetos, pulando os que não nascem neste nível (os só do modelo alto)."""
    for ob in objetos:
        if ob is not None:
            P.rotacionar(ob, eixo, graus, pivo)


def _esticar(pivo_x, graus):
    """x projetado da planta (vista de cima ou de baixo) → x da peça feita na horizontal, antes de deitá-la na
    inclinação `graus` em volta de pivo_x."""
    c = math.cos(math.radians(graus))
    return lambda x: pivo_x + (x - pivo_x) / c


def _fundo_da_coronha(contorno):
    """A linha de baixo da coronha, do canto de baixo da soleira para a frente (x crescente)."""
    i0 = min(range(len(contorno)), key=lambda i: contorno[i][1])
    fundo = [tuple(contorno[i0])]
    for x, y in contorno[i0 + 1:]:
        if x <= fundo[-1][0]:
            break
        fundo.append((x, y))
    return fundo


def _contorno_espiga(esp, frente, folga, n=8):
    """Contorno visto de cima (x projetado, y) da espiga de cima: a lâmina com a ponta redonda, os lados retos entrando na
    face de trás do receptor por uma concordância (o centro dela fica fixo; `folga` mm para fora dá o rebaixo na madeira)
    e, por dentro do receptor, reta até `frente`."""
    meia = esp['mm'] / 2 + folga
    c = esp['concordancia']
    r = c['raio'] - folga
    xcc = c['face'] - c['raio']  # centro da concordância em x; em y, ±(meia + r)
    larga = meia + r
    xc = esp['ponta'] + esp['mm'] / 2  # centro da ponta redonda
    angs = [math.radians(90.0 * i / n) for i in range(n + 1)]
    return ([(frente + folga, -larga)]
            + [(xcc + r * math.cos(t), -larga + r * math.sin(t)) for t in angs]
            + P.arco(xc, 0.0, meia, -90, -270, 16)
            + [(xcc + r * math.cos(t), larga - r * math.sin(t)) for t in reversed(angs)]
            + [(frente + folga, larga)])


def _contorno_espiga_baixo(ei, folga):
    """Contorno visto de baixo (x projetado, y) da espiga de baixo (vista pela seta A da planta): a lâmina com a ponta de
    trás redonda e o bloco largo da frente, sob o receptor; `folga` mm para fora dá o rebaixo."""
    meia = ei['mm'] / 2 + folga
    bl = ei['bloco']
    mb = bl['mm'] / 2 + folga
    xc = ei['x'][0] + ei['mm'] / 2
    xb0, xb1 = bl['x']
    return P.arco(xc, 0.0, meia, 90, 270, 16) + [(xb0 - 3.0, -meia), (xb0 - folga, -mb), (xb1 + folga, -mb),
                                                   (xb1 + folga, mb), (xb0 - folga, mb), (xb0 - 3.0, meia)]


def _charuto(x0, x1, largura, n=8):
    """Contorno (x, y) de um rasgo reto de pontas redondas, centrado em y = 0 (as estrias do tubo de gases)."""
    r = largura / 2
    return P.arco(x1 - r, 0.0, r, -90, 90, n) + P.arco(x0 + r, 0.0, r, 90, 270, n)


def _secao_do_manejo(mj, d):
    """Comprimento ao longo do cano e altura (mm) da alavanca de manejo a d mm do eixo: afina da raiz à ponta pela vista
    de cima e termina num quarto de elipse (a ponta redonda)."""
    comps = mj['comprimentos']
    d_ult, c_ult = comps[-1]
    h0, h1 = mj['altura']
    if d <= d_ult:
        return _na_linha(comps, d), h0 + (h1 - h0) * _entre(d, comps[0][0], d_ult)
    e = (d - d_ult) / (mj['ponta'] - d_ult)
    k = math.sqrt(max(0.0, 1.0 - e * e))
    return c_ult * k, h1 * (0.45 + 0.55 * k)


# ------------------------------------------------------------------------------------------------ partes
def _coronha(ficha, M):
    """Coronha de madeira e soleira de aço com os parafusos e o alçapão do estojo. Vista de cima (planta), a madeira afina
    em linha reta da soleira ao pescoço e a face de trás é um arco — o meio fica atrás dos cantos: a soleira curva
    inteira e a madeira a acompanha nos 30 mm de trás. Devolve a coronha (as espigas se embutem nela)."""
    pc, L = ficha['pecas'], ficha['vistaDeCima']['larguras']
    aco, det, madeira = M['aco'], M['aco_detalhes'], M['madeira']
    lc, ls = L['coronha'], L['soleira']
    (l_tras, l_pesc), (x_tras, x_pesc) = lc['mm'], lc['x']
    coronha = P.perfil_suave('coronha', pc['coronha'], 'XZ', -l_tras / 2, l_tras / 2, madeira, 'guarnicao', chanfro=3.4, seg=4)
    P.afinar(coronha, lambda x, z: 1.0 - (1.0 - l_pesc / l_tras) * _entre(x, x_tras, x_pesc))
    raio = ls['raioDeCima']

    def curva(y):
        """Quanto a face de trás avança para a boca (mm) a y do meio: o arco de raio `raio` visto de cima."""
        return raio - math.sqrt(max(0.0, raio * raio - y * y))
    encosto = sorted((z, x) for x, z in pc['soleira'][8:])  # a face da soleira que encosta na madeira: x pela altura

    def peso(x, z):
        """1 na face de trás da madeira, 0 a 30 mm dela: quanto da curva a madeira acompanha."""
        return min(1.0, max(0.0, 1.0 - (x - _na_linha(encosto, z)) / 30.0))
    fatias = (-17.5, -15.0, -12.0, -8.0, -4.0, 0.0, 4.0, 8.0, 12.0, 15.0, 17.5)
    P.fatiar(coronha, 'Y', fatias, onde=lambda x, y, z: peso(x - 2.0, z) > 0.0)
    P.deslocar(coronha, lambda x, y, z: (curva(y) * peso(x, z), 0.0, 0.0))
    soleira = P.prisma('soleira', pc['soleira'], 'XZ', -ls['mm'] / 2, ls['mm'] / 2, aco, 'corpo', chanfro=1.0)
    P.fatiar(soleira, 'Y', fatias)
    P.deslocar(soleira, lambda x, y, z: (curva(y), 0.0, 0.0))
    # A face de trás da soleira é inclinada de lado (avança para a boca descendo): os parafusos e o alçapão acompanham ela.
    atras = pc['soleira'][:8]

    def face_de_tras(y):
        """x da face de trás no meio (y do Blender = 0) na altura y e a inclinação dela (graus; + = avança descendo)."""
        for (xa, ya), (xb, yb) in zip(atras, atras[1:]):
            if yb <= y <= ya:
                return xa + (xb - xa) * (y - ya) / (yb - ya), math.degrees(math.atan2(xb - xa, ya - yb))
        return atras[-1][0], 0.0
    for y in (-48.0, -104.0):
        # Cabeça rente à face (0,4 mm para fora), perpendicular a ela, no meio da curva; a fenda só no modelo alto.
        xa, ang = face_de_tras(y)
        cabeca = P.torno('parafuso da soleira', [(xa - 0.4, 0), (xa - 0.4, 3.6), (xa, 3.9), (xa + 1.6, 3.9), (xa + 1.6, 0)], det,
                         'detalhes', eixo='X', centro=(0, 0, y), seg=20)
        fenda = P.caixa('fenda do parafuso', (xa - 1.0, -0.5, y - 3.2), (xa - 0.1, 0.5, y + 3.2), det, 'detalhes', chanfro=0, so_alto=True)
        P.cortar(cabeca, fenda)
        _girar((cabeca, fenda), 'Y', -ang, (xa, 0, y))
    # Alçapão do estojo de limpeza: sulco de 0,7 mm acompanhando a face de trás (e a curva dela), entre os dois parafusos.
    for y in (-56.0, -97.0):
        x = face_de_tras(y)[0]
        sulco = P.caixa('sulco do alçapão', (x - 1.0, -11.0, y - 0.3), (x + 0.7, 11.0, y + 0.3), aco, 'corpo', chanfro=0, so_alto=True)
        P.fatiar(sulco, 'Y', (-8.0, -4.0, 0.0, 4.0, 8.0))
        P.deslocar(sulco, lambda x_, y_, z_: (curva(y_), 0.0, 0.0))
        P.cortar(soleira, sulco)
    borda = [(face_de_tras(y)[0] + 0.35, y) for y in [-56.0 + (-97.0 + 56.0) * k / 12 for k in range(13)]]
    for lado in (-11.0, 11.0):
        sulco = P.tira('sulco do alçapão', borda, 1.4, 'XZ', lado - 0.3, lado + 0.3, aco, 'corpo', chanfro=0, so_alto=True)
        P.deslocar(sulco, lambda x_, y_, z_: (curva(y_), 0.0, 0.0))
        P.cortar(soleira, sulco)
    return coronha


def _espigas(ficha, M, coronha):
    """As duas espigas que prendem a coronha ao receptor, embutidas rente à madeira (planta: a vista de cima e a vista
    pela seta A, por baixo do pescoço). Cada uma é feita na horizontal, com o contorno da planta (x projetado) esticado
    pelo cosseno da inclinação, e deitada na linha da madeira; o rebaixo na coronha é o mesmo contorno com a folga do
    encaixe, cortado depois do chanfro (a aresta viva é a linha do encaixe)."""
    pc, D = ficha['pecas'], ficha['vistaDeCima']['detalhes']
    aco, det, madeira = M['aco'], M['aco_detalhes'], M['madeira']
    c = pc['coronha']
    # Espiga de cima: a linha de cima do pescoço vai da face de trás do receptor (c[2]) para trás (c[3]); a ponta da
    # frente entra 2,6 mm no receptor. O parafuso de fenda vertical atravessa a coronha até a espiga de baixo.
    (xa, za), (xb, zb) = c[2], c[3]
    inclinacao = (za - zb) / (xa - xb)
    graus = math.degrees(math.atan(inclinacao))
    esp = D['espiga']
    frente = xa + 2.6
    z0 = za + (frente - xa) * inclinacao
    estica = _esticar(frente, graus)
    lamina = P.prisma('espiga da coronha', [(estica(x), y) for x, y in _contorno_espiga(esp, frente, 0.0)], 'XY',
                      z0 - esp['espessura'], z0, aco, 'corpo', chanfro=0.4)
    rebaixo = P.prisma('rebaixo da espiga', [(estica(x), y) for x, y in _contorno_espiga(esp, frente, FOLGA_EMBUTIDA)], 'XY',
                       z0 - esp['espessura'] - FOLGA_EMBUTIDA, z0 + 3.0, madeira, 'guarnicao', chanfro=0)
    pe = D['parafusoEspiga']
    xp, rp, fe = estica(pe['x']), pe['diametro'] / 2, pe['fenda'] / 2
    cabeca = P.torno('parafuso da espiga', [(-0.5, 0), (-0.5, rp), (0.3, rp), (0.8, rp * 0.69), (0.9, 0)], det, 'detalhes',
                     seg=24, eixo='Z', centro=(xp, 0, z0))
    # A fenda atravessada, de um lado ao outro da espiga (planta).
    fenda = P.caixa('fenda do parafuso da espiga', (xp - fe, -rp - 0.3, z0 + 0.35), (xp + fe, rp + 0.3, z0 + 1.5), det,
                    'detalhes', chanfro=0, so_alto=True)
    P.cortar(cabeca, fenda)
    _girar((lamina, rebaixo, cabeca, fenda), 'Y', -graus, (frente, 0.0, z0))
    P.cortar(coronha, rebaixo, depois_do_chanfro=True)
    # Espiga de baixo: rente à linha de baixo do pescoço (a corda entre as pontas dela), com os dois parafusos.
    ei = D['espigaInferior']
    fundo = _fundo_da_coronha(c)
    xt, xf = ei['x']
    zt, zf = _na_linha(fundo, xt), _na_linha(fundo, xf)
    graus_b = math.degrees(math.atan((zf - zt) / (xf - xt)))
    estica_b = _esticar(xf, graus_b)
    baixo = P.prisma('espiga de baixo', [(estica_b(x), y) for x, y in _contorno_espiga_baixo(ei, 0.0)], 'XY',
                     zf, zf + ei['espessura'], aco, 'corpo', chanfro=0.4)
    rebaixo_b = P.prisma('rebaixo da espiga de baixo', [(estica_b(x), y) for x, y in _contorno_espiga_baixo(ei, FOLGA_EMBUTIDA)],
                         'XY', zf - 1.5, zf + ei['espessura'] + FOLGA_EMBUTIDA, madeira, 'guarnicao', chanfro=0)
    objetos = [baixo, rebaixo_b]
    rb = ei['diametroParafuso'] / 2
    for xs in ei['parafusos']:
        x = estica_b(xs)
        cab = P.torno('parafuso da espiga de baixo', [(0.5, 0), (0.5, rb), (-0.15, rb), (-0.45, rb * 0.7), (-0.55, 0)], det,
                      'detalhes', seg=24, eixo='Z', centro=(x, 0, zf))
        fen = P.caixa('fenda do parafuso da espiga de baixo', (x - 0.55, -rb - 0.3, zf - 1.2), (x + 0.55, rb + 0.3, zf - 0.25), det,
                      'detalhes', chanfro=0, so_alto=True)
        P.cortar(cab, fen)
        objetos += [cab, fen]
    _girar(objetos, 'Y', -graus_b, (xf, 0.0, zf))
    P.cortar(coronha, rebaixo_b, depois_do_chanfro=True)


def _argolas(ficha, M):
    """Argolas de bandoleira (planta): a da frente do lado esquerdo do bloco de gases, uma alça no plano transversal
    saindo para o lado; a de trás por baixo da coronha, com a placa embutida e a alça rebatida para a frente — rente,
    porque a foto 1 não mostra nada abaixo da coronha."""
    L, D = ficha['vistaDeCima']['larguras'], ficha['vistaDeCima']['detalhes']
    aco, det = M['aco'], M['aco_detalhes']
    ad = D['argolaDianteira']
    xa0, xa1 = ad['x']
    face = L['blocoDeGases']['mm'] / 2
    fio = 1.2
    P.caixa('olhal da argola dianteira', (xa0, face - 0.3, 0.3), (xa1, face + 2.2, 9.7), aco, 'corpo', chanfro=0.4)
    anel = P.ret_arredondado(face + 1.2, ad['sai'] - fio, 1.5, 8.5, 3.0, 6)
    xm = (xa0 + xa1) / 2
    P.tubo('argola dianteira', [(xm, u, v) for u, v in anel + anel[:1]], fio, det, 'detalhes', seg=10)
    # Do lado direito, a cabeça achatada do pino que prende a argola (marca '9' da planta).
    pa = D['pinoArgolaDianteira']
    P.caixa('pino da argola dianteira', (pa['x'][0], -face - pa['sai'], pa['z'][0]), (pa['x'][1], -face + 0.3, pa['z'][1]), aco, 'corpo',
            chanfro=0.4)
    fundo = _fundo_da_coronha(ficha['pecas']['coronha'])
    xs = D['argolaTraseira']['x']
    zs = _na_linha(fundo, xs)
    graus = math.degrees(math.atan2(_na_linha(fundo, xs + 5.0) - _na_linha(fundo, xs - 5.0), 10.0))
    placa = P.prisma('placa da argola traseira', P.ret_arredondado(xs - 14.0, xs + 14.0, -6.0, 6.0, 3.0), 'XY', zs - 0.15, zs + 1.2,
                     det, 'detalhes', chanfro=0.3)
    pe = P.torno('pé da argola traseira', [(0.5, 0), (0.5, 2.6), (-0.6, 2.6), (-0.9, 1.8), (-0.95, 0)], det, 'detalhes', seg=20,
                 eixo='Z', centro=(xs - 6.0, 0, zs))
    anel = P.ret_arredondado(xs - 6.0, xs + 9.0, -4.5, 4.5, 3.5, 6)
    alca = P.tubo('argola traseira', [(u, v, zs - 0.05) for u, v in anel + anel[:1]], 0.95, det, 'detalhes', seg=10)
    _girar((placa, pe, alca), 'Y', -graus, (xs, 0.0, zs))


def _tubo_de_gases(ficha, M):
    """Tubo de gases oval (a largura da planta, 17,9 mm; a altura da foto, 19,4) com o colar de trás, as seis estrias
    rasas e os oito furos de respiro (planta, vista pela esquerda, e a foto do tipo II do Armémuseum). Estrias e furos
    cortados depois do chanfro: arestas vivas de usinagem."""
    tn, L, D = ficha['tornos'], ficha['vistaDeCima']['larguras'], ficha['vistaDeCima']['detalhes']
    aco = M['aco']
    t = tn['tuboDeGases']
    zt = t['centroY']
    tubo = P.torno('tubo de gases', t['perfil'], aco, 'corpo', seg=48, centro=(0, 0, zt))
    lt = L['tuboDeGases']
    r_tubo = t['perfil'][1][1]
    r_colar = max(r for _x, r in t['perfil'])
    i_colar = next(i for i, (_x, r) in enumerate(t['perfil']) if r == r_colar)
    (xc0, xc1), (wc0, _wc1) = lt['colar']['x'], lt['colar']['mm']
    f_tubo, f_colar = lt['mm'] / (2 * r_tubo), wc0 / (2 * r_colar)
    largura = [(t['perfil'][i_colar - 1][0], f_tubo), (xc0, f_colar), (xc1, f_tubo)]
    P.afinar(tubo, lambda x, z: _na_linha(largura, x))
    a_oval, b_oval = lt['mm'] / 2, r_tubo

    def raio_oval(graus):
        """Raio da seção oval a `graus` do alto."""
        s, c = math.sin(math.radians(graus)), math.cos(math.radians(graus))
        return 1.0 / math.sqrt((s / a_oval) ** 2 + (c / b_oval) ** 2)
    et = D['estriasTuboGases']
    charuto = _charuto(et['x'][0], et['x'][1], et['largura'])
    for ang in et['angulos']:
        r = raio_oval(ang)
        for lado in (-1, 1):
            estria = P.prisma('estria do tubo de gases', charuto, 'XY', zt + r - et['profundidade'], zt + r + 3.0, aco, 'corpo',
                              chanfro=0)
            P.rotacionar(estria, 'X', -lado * ang, (0.0, 0.0, zt))
            P.cortar(tubo, estria, depois_do_chanfro=True)
    fu = D['furosTuboGases']
    r = raio_oval(fu['angulo'])
    for x in fu['x']:
        for lado in (-1, 1):
            furo = P.torno('furo do tubo de gases', [(r - 5.0, 0), (r - 5.0, fu['diametro'] / 2), (r + 4.0, fu['diametro'] / 2),
                                                     (r + 4.0, 0)], aco, 'corpo', seg=20, eixo='Z', centro=(x, 0, zt))
            P.rotacionar(furo, 'X', -lado * fu['angulo'], (0.0, 0.0, zt))
            P.cortar(tubo, furo, depois_do_chanfro=True)


def construir(ficha, M):
    """Todas as peças no nível atual (pecas.iniciar). M = materiais de fábrica (materiais.materiais_de_fabrica)."""
    pc, tn, pt, ln = ficha['pecas'], ficha['tornos'], ficha['pontos'], ficha['linhas']
    L, D = ficha['vistaDeCima']['larguras'], ficha['vistaDeCima']['detalhes']
    aco, det, aco_c, polido, madeira = M['aco'], M['aco_detalhes'], M['aco_carregador'], M['aco_polido'], M['madeira']
    lr = L['receptor']['mm'] / 2  # a face dos lados do receptor (e da tampa, rente a ele)

    # --- Coronha, soleira e as espigas embutidas; as argolas de bandoleira
    coronha = _coronha(ficha, M)
    _espigas(ficha, M, coronha)
    _argolas(ficha, M)

    # --- Receptor fresado: recorte de alívio dos dois lados, janela de ejeção com a fenda da alavanca de manejo, o rasgo
    # do botão da mola, o poço do carregador, pinos e o eixo do seletor
    rec = P.prisma('receptor', pc['receptor'], 'XZ', -lr, lr, aco, 'corpo', chanfro=0.9)
    ra = pt['recorteDeAlivio']
    for y0, y1 in ((-lr - 5.5, -lr + 2.0), (lr - 2.0, lr + 5.5)):
        P.cortar(rec, P.caixa('recorte de alívio', (ra['x0'], y0, ra['y0']), (ra['x1'], y1, ra['y1']), aco, 'corpo', chanfro=0))
    j = pt['janela']
    # A janela atravessa a parede de 3 mm e abre no vão onde corre o transportador, mais fundo que ela embaixo: pela
    # janela se vê o transportador a 1 mm da parede e, atrás da ponta dele, o escuro do receptor (foto de museu "7,62 RK
    # 54 Kalasnikov", lado direito). Um corte só, em L: dois cortes encostados deixavam degraus de 0,1 mm que o chanfro
    # do receptor dobrava (UV sobreposta no assar).
    parede = -lr + 3.0
    P.cortar(rec, P.prisma('janela e vão do transportador', [(-lr - 11.5, j['y0']), (parede, j['y0']), (parede, 0.0),
                                                             (-lr + 12.0, 0.0), (-lr + 12.0, j['y1']), (-lr - 11.5, j['y1'])],
                           'YZ', j['x0'], j['x1'], aco, 'corpo', chanfro=0))
    mj = D['manejo']
    zm0, zm1 = mj['centroY'] - mj['altura'][0] / 2 - 0.2, mj['centroY'] + mj['altura'][0] / 2 + 0.2
    P.cortar(rec, P.caixa('fenda do manejo', (j['x1'] - 1.0, -lr - 11.5, zm0), (mj['frente'] + 1.5, -lr + 3.0, zm1), aco, 'corpo',
                          chanfro=0))
    bt = D['botaoMola']
    z_botao = min(z for _x, z in pc['botaoMola'])
    P.cortar(rec, P.caixa('rasgo do botão da mola', (bt['x'][0] - 1.0, -bt['mm'] / 2 - 0.3, z_botao - 0.4),
                          (bt['x'][1] + 0.4, bt['mm'] / 2 + 0.3, 20.0), aco, 'corpo', chanfro=0))
    # Poço do carregador: o vão no fundo do receptor onde o carregador entra, com 0,3 mm de folga em volta.
    tras = [(x - 0.3, y) for x, y in pc['carregador'] if y >= -44.0 and x < -470.0]
    frente = [(x + 0.3, y) for x, y in pc['carregador'] if y >= -41.0 and x > -440.0]
    tras[0] = (tras[0][0], tras[0][1] + 0.3)
    frente[-1] = (frente[-1][0], frente[-1][1] + 0.3)
    P.cortar(rec, P.prisma('poço do carregador', tras + [(frente[0][0], -42.0)] + frente, 'XZ', -14.3, 14.3, aco, 'corpo', chanfro=0))
    for x, y in pt['pinos']:
        for lado in (-1, 1):
            P.pino('pino', x, y, 2.4, det, 'detalhes', lado=lado, de=lr, ate=lr + 0.8)
    ex, ey = pt['eixoSeletor']
    se = D['seletor']
    P.pino('eixo do seletor', ex, ey, 6.5, det, 'detalhes', lado=-1, de=lr, ate=lr + se['eixoSai'])
    # Letras do seletor logo à frente da aba, na trajetória dela (raio de 96 mm em volta do eixo): АВ no meio, ОД embaixo.
    P.gravacao('letras AB', 'АВ', -477.0, -22.5, 4.2, 'direita', -lr, 0.3, rec)
    P.gravacao('letras OD', 'ОД', -478.0, -37.0, 4.2, 'direita', -lr, 0.3, rec)
    P.gravacao('número de série', 'КЛ 4178', -545.0, -12.0, 4.0, 'esquerda', lr, 0.25, rec)
    P.gravacao('marca de controle', 'ОТК', -470.0, -33.0, 3.0, 'esquerda', lr, 0.2, rec)

    # --- Ferrolho (peça móvel). O transportador enche a janela (foto de museu "7,62 RK 54 Kalasnikov", lado direito): em
    # cima o dorso arredondado, embaixo a face lisa polida, com um vinco entre os dois (45 % da janela embaixo, 55 % em
    # cima); atrás, a parte de baixo acaba 6 mm antes da borda da janela e a de cima, em rampa, um pouco antes — ali se vê
    # o escuro do receptor. A cabeça do ferrolho com o extrator e a alavanca de manejo: vista de cima ela afina da raiz
    # até a ponta redonda, com a frente reta; de frente sai baixa (planta e foto 1)
    face, fundo = -lr + 4.0, -lr + 11.8  # a face lisa a 1 mm da parede de dentro; o fundo antes da parede do vão
    z_baixo, topo = 1.0, 18.2
    z_vinco = j['y0'] + 0.45 * (j['y1'] - j['y0'])
    raio_dorso = topo - z_vinco
    perfil = [(face, z_baixo), (face, z_vinco - 0.4)]
    perfil += P.arco(face + 0.4 + raio_dorso, z_vinco, raio_dorso, 180.0, 90.0, 10)
    perfil += [(fundo, topo), (fundo, z_baixo)]
    transp = P.prisma('transportador', perfil, 'YZ', j['x0'] - 0.5, j['x1'] + 1.0, polido, 'interno', 'ferrolho', chanfro=0.4)
    P.cortar(transp, P.caixa('ponta de baixo do transportador', (j['x0'] - 10, face - 5, z_baixo - 5),
                             (j['x0'] + 6.0, fundo + 5, z_vinco), polido, 'interno', chanfro=0))
    xa, xb = j['x0'] + 2.4, j['x0'] + 7.3  # a rampa da ponta de cima: do vinco (atrás) até y = 19 (à frente)
    k = (xb - xa) / (19.0 - z_vinco)
    P.cortar(transp, P.prisma('rampa do transportador', [(j['x0'] - 10, z_vinco - 0.3), (xa - 0.3 * k, z_vinco - 0.3),
                                                         (xa + (topo + 1 - z_vinco) * k, topo + 1), (j['x0'] - 10, topo + 1)],
                              'XZ', face - 5, fundo + 5, polido, 'interno', chanfro=0))
    P.torno('cabeça do ferrolho', [(j['x1'] - 12, 0), (j['x1'] - 12, 5.6), (j['x1'] + 4, 5.6), (j['x1'] + 4, 0)], polido, 'interno',
            'ferrolho', seg=24, centro=(0, 0, 0))
    P.caixa('extrator', (j['x1'] - 10, -6.4, 3.0), (j['x1'] + 2, -4.8, 7.0), polido, 'interno', 'ferrolho', chanfro=0.2)
    d_ult = mj['comprimentos'][-1][0]
    estacoes = [lr - 4.5] + [d for d, _c in mj['comprimentos'][:1]] + [24.0, 29.2, 35.0, 40.0, d_ult]
    estacoes += [d_ult + (mj['ponta'] - d_ult) * e for e in (0.5, 0.8, 0.95)]
    aneis = []
    for d in sorted(set(estacoes)):
        comp, h = _secao_do_manejo(mj, d)
        z0, z1 = mj['centroY'] - h / 2, mj['centroY'] + h / 2
        raio = min(1.6, 0.45 * min(comp, h))
        aneis.append([(u, -d, v) for u, v in P.ret_arredondado(mj['frente'] - comp, mj['frente'], z0, z1, raio, 4)])
    P.lofting('manejo', aneis, polido, 'interno', 'ferrolho', chanfro=(0.3, 2))

    # --- Cão (peça móvel, interno): aparece pela janela com o ferrolho atrás
    cx, cy = pt['pinoCao']
    P.prisma('cão', [(cx - 5, cy - 4), (cx + 5, cy - 4), (cx + 14, cy + 22), (cx + 18, cy + 36), (cx + 10, cy + 38), (cx + 2, cy + 16)],
             'XZ', -4.0, 4.0, polido, 'interno', 'cao', chanfro=0.4)

    # --- Tampa lisa (a AK-47 não tem nervuras), rente ao receptor: o alto plano e os ombros arredondados (planta), com o
    # entalhe de trás; o botão da mola recuperadora no rasgo do receptor, com a face de trás serrilhada
    tampa = P.prisma('tampa', pc['tampa'], 'XZ', -lr, lr, aco, 'corpo')
    lt = L['tampa']
    topo = [tuple(p) for p in pc['tampa'][1:7]]  # o perfil de cima, da frente (-399) até o degrau de trás

    def no_topo(p):
        return any(abs(p[0] - x) < 0.01 and abs(p[2] - z) < 0.01 for x, z in topo)
    P.marcar_chanfro(tampa, lambda a, b: min(abs(a[1]), abs(b[1])) > lr - 0.1 and no_topo(a) and no_topo(b))
    tampa['chanfro'] = ((lt['mm'] - lt['topoPlano']) / 2, 6)
    en = D['tampaEntalhe']
    P.cortar(tampa, P.torno('entalhe da tampa', [(10.0, 0), (10.0, en['raio']), (40.0, en['raio']), (40.0, 0)], aco, 'corpo',
                            seg=48, eixo='Z', centro=(en['x'], 0, 0)), depois_do_chanfro=True)
    botao = P.prisma('botão da mola', pc['botaoMola'], 'XZ', -bt['mm'] / 2, bt['mm'] / 2, det, 'detalhes', chanfro=0.5)
    (ax_, az_), (bx_, bz_) = pc['botaoMola'][1], pc['botaoMola'][2]  # a face de trás inclinada
    comp_face = math.hypot(bx_ - ax_, bz_ - az_)
    tx, tz = (bx_ - ax_) / comp_face, (bz_ - az_) / comp_face
    nx, nz = -tz, tx  # para fora: para trás e para cima
    s0, s1 = bt['serrilha']
    for i in range(bt['ranhuras']):
        x = s0 + (s1 - s0) * (i + 0.5) / bt['ranhuras']
        z = az_ + (x - ax_) * (bz_ - az_) / (bx_ - ax_)
        ranhura = [(x + tx * a + nx * b, z + tz * a + nz * b) for a, b in ((-0.22, -0.35), (0.22, -0.35), (0.22, 0.6), (-0.22, 0.6))]
        P.cortar(botao, P.prisma('serrilha do botão', ranhura, 'XZ', -bt['mm'] / 2 - 0.2, bt['mm'] / 2 + 0.2, det, 'detalhes',
                                 chanfro=0, so_alto=True))

    # --- Punho de madeira liso (tipo 3) com o parafuso de baixo; a espiga do guarda-mato por cima dele, o guarda-mato com
    # o rebite, o gatilho, a caixa do retém com o eixo e o retém pendurado
    punho = P.perfil_suave('punho', pc['punho'], 'XZ', -15, 15, madeira, 'guarnicao', chanfro=6.0)
    punho['chanfro'] = (6.5, 5)
    # O pé do punho é plano (y = -147,5 entre x = -616,6 e -602,4): o parafuso entra reto por ele, cabeça rente (0,2 mm).
    parafuso = P.torno('parafuso do punho', [(-0.2, 0), (-0.2, 3.4), (2.4, 3.4), (2.4, 0)], det, 'detalhes', eixo='Z', seg=20,
                       centro=(-609.5, 0, -147.5))
    P.cortar(parafuso, P.caixa('fenda do parafuso do punho', (-612.8, -0.5, -147.8), (-606.2, 0.5, -147.4), det, 'detalhes',
                               chanfro=0, so_alto=True))
    P.prisma('espiga do guarda-mato', pc['espigaGuardaMato'], 'XZ', -12.0, 12.0, aco, 'corpo', chanfro=0.6)
    P.prisma('guarda-mato', pc['guardaMato'], 'XZ', -5.5, 5.5, aco, 'corpo', chanfro=0.6)
    # Rebite da aba de trás, que encosta no fundo do receptor (pontas de dentro da perna de trás: guardaMato[-3] e [-2]).
    (xr0, zr), (xr1, _z) = pc['guardaMato'][-3], pc['guardaMato'][-2]
    P.esfera('rebite do guarda-mato', ((xr0 + xr1) / 2, 0, zr), 1.8, (1.0, 1.0, 0.45), det, 'detalhes', u=16, v=8)
    P.prisma('gatilho', pc['gatilho'], 'XZ', -3.5, 3.5, det, 'detalhes', 'gatilho', chanfro=0.5)
    P.fileira(lambda i, dx, dy: P.caixa('estria do gatilho', (-552.6 + dx, -3.6, -52.0 + dy), (-551.8 + dx, 3.6, -51.4 + dy), det, 'detalhes', 'gatilho',
                                        chanfro=0, so_alto=True), 5, (0.9, -2.2))
    P.prisma('caixa do retém', pc['caixaRetem'], 'XZ', -7.5, 7.5, aco, 'corpo', chanfro=0.6)
    P.prisma('retém do carregador', pc['retem'], 'XZ', -6.5, 6.5, det, 'detalhes', chanfro=0.5)
    xr, yr = pt['pinoRetem']
    for lado in (-1, 1):
        P.pino('eixo do retém', xr, yr, 1.6, det, 'detalhes', lado=lado, de=7.5, ate=8.1)

    # --- Carregador (peça móvel): contorno da foto (sobe por dentro do poço), base e nervuras (três perto das costas, uma
    # perto da frente)
    P.perfil_suave('carregador', pc['carregador'], 'XZ', -14, 14, aco_c, 'carregador', 'carregador', chanfro=1.2, it=1)
    rt = P.reamostrar(ln['carregadorTras'], 44)
    fr = P.reamostrar(ln['carregadorFrente'], 44)
    for f in (0.16, 0.28, 0.40, 0.82):
        linha = [(a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f) for a, b in zip(rt, fr)][4:39]
        for lado in (-1, 1):
            # Nervura estampada: um cordão de perfil redondo meio embutido na chapa (sai 0,9 mm), e não uma tira de quina viva.
            P.tubo('nervura do carregador', [(x, lado * 13.5, z) for x, z in linha], 1.4, aco_c, 'carregador', 'carregador', seg=10)
    b0, b1 = ln['baseDoCarregador']
    ex_, ey_ = b1[0] - b0[0], b1[1] - b0[1]
    comp_base = math.hypot(ex_, ey_)
    ex_, ey_ = ex_ / comp_base, ey_ / comp_base
    nx_, ny_ = -ey_, ex_
    P.prisma('base do carregador', [(b0[0] - ex_ * 1.5, b0[1] - ey_ * 1.5), (b1[0] + ex_ * 1.5, b1[1] + ey_ * 1.5),
                                    (b1[0] + ex_ * 1.5 + nx_ * 7, b1[1] + ey_ * 1.5 + ny_ * 7), (b0[0] - ex_ * 1.5 + nx_ * 7, b0[1] - ey_ * 1.5 + ny_ * 7)],
             'XZ', -15.5, 15.5, aco_c, 'carregador', 'carregador', chanfro=1.0)

    # --- Seletor (peça móvel, posição de segurança) rente ao lado direito, com a aba da frente dobrada para fora (planta)
    xd0, xd1 = se['aba']['dobra']
    sai = se['aba']['sai'] - 2.0  # a partir da face de fora da alavanca (2 mm de chapa)
    seletor = P.prisma('seletor', pc['seletor'], 'XZ', -lr - 2.0, -lr, det, 'detalhes', 'seletor', chanfro=0.5)
    P.fatiar(seletor, 'X', [xd0 + (xd1 - xd0) * k / 10 for k in range(1, 11)])
    P.deslocar(seletor, lambda x, y, z: (0.0, -sai * _suave(_entre(x, xd0, xd1)), 0.0))

    # --- Alça (anatomia conferida na foto de perto "File:AK47-rear-sight.jpg", Erik Gregg, CC BY-SA 2.0; larguras da
    # planta): a base com as duas bochechas da frente, onde passa o eixo da folha; a folha gira nesse eixo e tem o entalhe
    # em U na lâmina da ponta de trás; o cursor, com um botão de trava redondo de cada lado, fica logo à frente da lâmina
    # na posição de combate (П); a graduação 1–8 cresce para a frente, os ímpares no lado direito e os pares no esquerdo,
    # cada número ao lado do entalhe da trava daquele lado. O que sobe acima da linha de mira (a 44,4 mm do eixo do cano na
    # altura do cursor) fica nos lados — os botões e as bochechas —, e o meio fica baixo: a visada pelo entalhe fica livre
    # até o poste da massa.
    lb = L['baseAlca']['mm'] / 2
    P.prisma('base da alça', pc['baseAlca'], 'XZ', -lb, lb, aco, 'corpo', chanfro=0.9)
    for y0, y1 in ((-9.0, -7.2), (7.2, 9.0)):
        P.prisma('bochecha da alça', pc['bochechasAlca'], 'XZ', y0, y1, aco, 'corpo', chanfro=0.5)
    lf = L['folhaAlca']['mm'] / 2
    folha = P.prisma('folha da alça', pc['folhaAlca'], 'XZ', -lf, lf, det, 'detalhes', chanfro=0.5)
    ex_a, ey_a = pt['entalheAlca']
    P.cortar(folha, P.caixa('entalhe da alça', (ex_a - 3.0, -1.1, ey_a + 1.1), (ex_a + 3.0, 1.1, ey_a + 5.0), det, 'detalhes', chanfro=0))
    P.cortar(folha, P.torno('fundo do entalhe', [(ex_a - 3.0, 0), (ex_a - 3.0, 1.1), (ex_a + 3.0, 1.1), (ex_a + 3.0, 0)], det, 'detalhes',
                            seg=16, centro=(0, 0, ey_a + 1.1)))

    def topo_da_folha(x):
        """Z da face de cima da folha em x (ela sobe de 42,3 em x = -383 a 43,8 em x = -363,3)."""
        return 42.3 + (43.8 - 42.3) * min(1.0, max(0.0, (x + 383.0) / (383.0 - 363.3)))
    for i, x in enumerate((-379.5, -376.75, -374.0, -371.25, -368.5, -365.75, -363.0, -360.25)):
        lado = -1 if i % 2 == 0 else 1
        y0, y1 = (-lf - 0.55, -6.0) if lado < 0 else (6.0, lf + 0.55)
        P.cortar(folha, P.caixa('entalhe da trava', (x - 0.6, y0, 36.0), (x + 0.6, y1, 50.0), det, 'detalhes', chanfro=0))
        # Algarismo de 1,8 mm centrado em (x, ±3,4), lido de trás da arma (o pé do número para a coronha).
        P.gravacao(f'graduação {i + 1}', str(i + 1), x - 0.9, 3.4 * lado + 0.5, 1.8, 'cima', topo_da_folha(x), 0.3, folha, rotacao=-90)
    cursor = pc['cursorAlca']
    P.prisma('cursor da alça', cursor, 'XZ', -8.2, 8.2, det, 'detalhes', chanfro=0.5)
    xb = (min(p[0] for p in cursor) + max(p[0] for p in cursor)) / 2
    for lado in (-1, 1):
        # O botão redondo (r 3,5, centro a 42,5) é o disco escuro da foto, de -391 a -383, com o topo em 46; de ponta a
        # ponta dos botões, a largura da planta.
        P.pino('botão do cursor', xb, 42.5, 3.5, det, 'detalhes', lado=lado, de=8.2, ate=L['cursorAlca']['mm'] / 2)
    fx, fz = pt['eixoFolha']
    for lado in (-1, 1):
        P.pino('eixo da folha', fx, fz, 1.6, det, 'detalhes', lado=lado, de=9.0, ate=9.5)

    # --- Guarda-mãos de madeira (fresta entre eles), afinando para a frente como na planta; o de baixo entra na braçadeira.
    # Braçadeiras e o retentor do guarda-mão (lado direito)
    gs = L['guardaMaoSuperior']
    (ls0, ls1), (xs0, xs1) = gs['mm'], gs['x']
    sup = P.prisma('guarda-mão superior', pc['guardaMaoSuperior'], 'XZ', -ls0 / 2, ls0 / 2, madeira, 'guarnicao', chanfro=6.0)
    sup['chanfro'] = (6.5, 5)
    P.afinar(sup, lambda x, z: 1.0 - (1.0 - ls1 / ls0) * _entre(x, xs0, xs1))
    gi = L['guardaMaoInferior']
    (li0, li1), (xi0, xi1) = gi['mm'], gi['x']
    lbr = L['bracadeira']['mm']
    inf = P.prisma('guarda-mão inferior', pc['guardaMaoInferior'], 'XZ', -li0 / 2, li0 / 2, madeira, 'guarnicao', chanfro=3.2)
    inf['chanfro'] = (3.6, 4)
    x_bracadeira = min(p[0] for p in pc['bracadeira'])
    largura_inf = [(xi0, 1.0), (xi1, li1 / li0), (x_bracadeira, (lbr - 1.8) / li0)]  # a ponta cabe na braçadeira (0,9 mm de cada lado)
    # Vértices em cada quebra do afinamento: sem eles, a face do lado (um n-gon só) liga a traseira à ponta e afina torto.
    P.fatiar(inf, 'X', [x for x, _f in largura_inf])
    P.afinar(inf, lambda x, z: _na_linha(largura_inf, x))
    P.prisma('braçadeira', pc['bracadeira'], 'XZ', -lbr / 2, lbr / 2, aco, 'corpo', chanfro=1.0)
    P.prisma('braçadeira do tubo', pc['bracadeiraTubo'], 'XZ', -12.5, 12.5, aco, 'corpo', chanfro=1.2)
    P.prisma('retentor do guarda-mão', [(-374, -2), (-362, -2), (-360, 6), (-376, 6)], 'XZ', -lr - 1.8, -lr, det, 'detalhes', chanfro=0.4)
    P.pino('eixo do retentor', -368.0, 2.0, 2.2, det, 'detalhes', lado=-1, de=lr + 1.8, ate=lr + 2.6)

    # --- Cano (mais grosso atrás do bloco de gases), o bloco em frente à braçadeira, tubo de gases, bloco de gases, vareta,
    # massa, porca e a alma
    c = tn['cano']
    cano = P.torno('cano', c['perfil'], aco, 'corpo', seg=48, centro=(0, 0, c['centroY']))
    # O bloco em frente à braçadeira vai de baixo do cano até o tubo de gases (vista pela esquerda da planta; a foto o mostra
    # cheio): de cima, o lábio de trás largo e, depois de uma concordância, mais estreito até a frente.
    cgl = L['colarGuardaMao']
    (wl, wf), (xk0, xk1) = cgl['mm'], cgl['concordancia']  # o lábio vai da traseira do bloco até o começo da concordância
    colar = P.prisma('colar do guarda-mão', pc['colarGuardaMao'], 'XZ', -wl / 2, wl / 2, aco, 'corpo', chanfro=0.6)
    P.fatiar(colar, 'X', [xk0 + (xk1 - xk0) * k / 8 for k in range(9)])
    P.afinar(colar, lambda x, z: (wf + (wl - wf) * (1.0 - _entre(x, xk0, xk1)) ** 2) / wl)
    _tubo_de_gases(ficha, M)
    lg = L['blocoDeGases']['mm'] / 2
    P.prisma('bloco de gases', pc['blocoDeGases'], 'XZ', -lg, lg, aco, 'corpo', chanfro=1.2)
    P.prisma('guia da vareta', pc['guiaVareta'], 'XZ', -6, 6, aco, 'corpo', chanfro=0.8)
    v = tn['vareta']
    P.torno('vareta', v['perfil'], det, 'detalhes', seg=20, centro=(0, 0, v['centroY']))
    lbm = L['baseMassa']['mm'] / 2
    P.prisma('base da massa', pc['baseMassa'], 'XZ', -lbm, lbm, aco, 'corpo', chanfro=1.0)
    # Torre da massa: a janela logo acima do cano, o tambor do poste na horizontal (a deriva ajusta ele de lado) e as
    # orelhas saindo da própria torre, com o vão aberto em volta do poste — pela mira, "( | )".
    tm = L['torreMassa']
    lt_ = tm['mm'] / 2
    torre = P.prisma('torre da massa', pc['torreMassa'], 'XZ', -lt_, lt_, aco, 'corpo', chanfro=0.8)
    P.cortar(torre, P.prisma('janela da torre', pc['janelaTorre'], 'XZ', -lt_ - 1.2, lt_ + 1.2, aco, 'corpo', chanfro=0))
    tb = pt['tamborMassa']
    P.cortar(torre, P.caixa('vão das orelhas', (-40.0, -tm['vao'] / 2, tb['y'] + tb['raio']), (-12.0, tm['vao'] / 2, 60.0), aco, 'corpo',
                            chanfro=0))
    # O tambor sai 0,2 mm de cada lado da torre (as pontas dele aparecem nas faces).
    P.pino('tambor da massa', tb['x'], tb['y'], tb['raio'], det, 'detalhes', lado=-1, de=-lt_ - 0.2, ate=lt_ + 0.2)
    px, py = pt['posteMassa']
    P.torno('poste da massa', [(tb['y'], 0), (tb['y'], 1.1), (py, 1.1), (py, 0)], det, 'detalhes', seg=16, eixo='Z', centro=(px, 0, 0))
    po = tn['porca']
    porca = P.torno('porca da boca', po['perfil'], aco, 'corpo', seg=48, centro=(0, 0, po['centroY']), chanfro=0.4)
    al = tn['alma']
    alma = P.torno('alma', al['perfil'], aco, 'corpo', seg=24, centro=(0, 0, al['centroY']))
    P.cortar(porca, alma)
    P.cortar(cano, alma)
```

- [ ] **Passo 3: Primeira construção só da forma** (o `principal.py` completo chega na Tarefa 8; aqui um script de
  rascunho no scratchpad monta a coleção `jogo`, renderiza a máscara de lado em Workbench e mede a silhueta com a mesma
  conta da régua). Rodar e corrigir até o script terminar sem erro e a máscara sair inteira:

```python
# <scratchpad>/forma_ak47.py — rascunho da Tarefa 6: constrói, renderiza a máscara de lado e imprime o IoU.
import json, sys
sys.path.insert(0, 'tools/blender')
import bpy
from armas import ak47, materiais, pecas, validar
bpy.ops.wm.read_factory_settings(use_empty=True)
ficha = json.load(open('tools/blender/refs/ak47.json', encoding='utf-8'))
fab = json.load(open(sys.argv[sys.argv.index('--') + 1], encoding='utf-8'))
M = materiais.materiais_de_fabrica(fab)
col = pecas.iniciar('jogo', 'jogo')
ak47.construir(ficha, M)
pecas.finalizar(col)
objs = [o for o in col.objects if o.type == 'MESH' and not o.get('cortador')]
r = validar.silhueta(objs, ficha, 'tools/blender/conferencia/ak47')
m = validar.medidas(objs, [o for o in objs if o.name.split('.')[0] == 'cano'], ak47.soquetes(ficha), ficha)
print('MASSACRE-MEDIDAS', json.dumps(m))
print('MASSACRE-FORMA', json.dumps(r['silhueta']))
```

Run (com a pintura de fábrica exportada do registro para um JSON):

```bash
cd "/c/Users/T-Gamer/Desktop/game tiro/trabalho-4.1a"
node -e "import('./src/data/armasReais.js').then(m => require('fs').writeFileSync(process.env.TEMP + '/fabrica-ak47.json', JSON.stringify(m.ARMAS_REAIS.ak47.fabrica)))"
"/s/blender.exe" -b --factory-startup --python-exit-code 1 -P "<scratchpad>/forma_ak47.py" -- "$TEMP/fabrica-ak47.json" 2>&1 | grep MASSACRE
```

Expected: `MASSACRE-FORMA {"iouBruto": …, "iouTolerancia": …, …}` com `iouTolerancia` ≥ 0,98 (a prova deu 0,991 com as
peças do `ak_v3.py`; peça nova fora do contorno aparece aqui) e `MASSACRE-MEDIDAS` com as cinco medidas e o erro de
cada uma dentro de ±1 % (o raio de mira contra o alvo conciliado na Tarefa 1). A silhueta e as medidas saem das peças
separadas (no `construir`, das peças juntadas do nível `perto`); a peça do carregador é a de `peca = 'carregador'`.

- [ ] **Passo 4: Revisão crítica da forma, até não sobrar defeito** (regra do usuário: ser crítico e honesto e
  arrumar o que estiver ruim ou mediano). Renderizar as vistas da conferência (`conferir.py`, Tarefa 8: lado, cima,
  frente, 3/4 dos dois lados, perto do receptor, sobreposição) e comparar lado a lado com a foto da ficha e com as
  referências da seção 14 do moodboard (QCS1/2/4/18 e QHS1/3/15 para a leitura de "fábrica tipo CS2"; QMP1/5/7/11 para o
  adereço de metal em miniatura). Para cada defeito: anotar (vista, peça, o que está errado, a referência), corrigir no
  script e renderizar de novo. Itens que a revisão confere um por um:
  - a silhueta de lado ≥ 98 % com tolerância e a sobreposição sem mancha verde (falta) ou magenta (sobra) maior que 1 px
    da foto em nenhuma peça;
  - as cinco medidas-chave dentro de ±1 % do alvo da ficha (depois da conciliação da Tarefa 1);
  - de cima e de frente (não há foto: proporções pela ficha técnica e pelas referências): largura do receptor (32 mm),
    da tampa (33 mm), da coronha (42 mm na soleira, afinando), dos guarda-mãos, do carregador (28 mm);
  - chanfros: nenhuma aresta viva de 90° sem chanfro, nenhum chanfro "de sabonete" (largo demais);
  - madeira com veio visível e verniz; aço com variação de aspereza e borda levemente gasta (não chapado, não limpo
    demais); as marcações legíveis de perto e discretas de longe;
  - nenhuma peça flutuando nem atravessando outra (pinos rentes, braçadeiras abraçando os guarda-mãos, vareta na guia);
  - de 3/4 esquerdo: recorte de alívio, pinos, número de série e as argolas presentes.
  Registrar o que foi achado e corrigido (com o número de renders) para o relatório da subfase.

- [ ] **Passo 5: As referências da revisão no moodboard** — as fontes que a revisão crítica usou, na seção 14:

Em `docs/art/moodboard.md`, trocar:

```
| Fotos laterais reais medidas em milímetros: o contorno de cada peça, a posição das miras e as cores. | Commons: AK-47 tipo 3 (domínio público); AKM do Armémuseum (CC BY-SA 4.0) | Ficha de fidelidade e régua; a AK-47 tipo 3 da prova v3 bate 99,1 % com tolerância de 1 px da foto (seção 2; `tools/regua.html`, `tools/blender/refs/<id>.json`). |

```

por:

```
| Fotos laterais reais medidas em milímetros: o contorno de cada peça, a posição das miras e as cores. | Commons: AK-47 tipo 3 (domínio público); AKM do Armémuseum (CC BY-SA 4.0) | Ficha de fidelidade e régua; a AK-47 tipo 3 da prova v3 bate 99,1 % com tolerância de 1 px da foto (seção 2; `tools/regua.html`, `tools/blender/refs/<id>.json`). |
| A foto de lado não dá largura. A planta de fábrica soviética do AK (vista pela esquerda, de cima e pela direita, com cotas em russo) dá as larguras e as peças que só aparecem de cima ou de baixo: as espigas da coronha com os parafusos, o botão da mola recuperadora e o entalhe da tampa, o cubo do seletor e a aba dobrada, a alavanca de manejo afinando até a ponta, as estrias e os furos do tubo de gases, o bloco em frente à braçadeira e as argolas de bandoleira. | Pinterest, busca "ak 47 top view" (a planta, `i.pinimg.com/originals/e4/bf/e8/e4bfe8574a4eda630145448f0337097b.gif`, lida só no navegador, sem baixar); The Firearm Blog, "AK-47, AKM/AKMS and AK-74 Blueprints" (2017-04-03); archive.org, "AK47AKMTechnicalDrawingsRussian" | Seção `vistaDeCima` da ficha, só com números derivados e a fonte; na revisão da 4.1a o modelo renderizado de cima na escala da planta (5,876 px/mm) foi sobreposto a ela, e as larguras batem com a planta (receptor 37, soleira 37,7, pescoço 32,2, tampa com o alto de 22,8) (`tools/blender/refs/ak47.json`, `tools/blender/armas/ak47.py`). |
| As estrias rasas e os furos de respiro do tubo de gases de perto. | Commons: "File:AK-47 type II noBG.png" (Nemo5576, CC BY-SA 4.0; peça do Armémuseum) | Seis estrias a 30°, 90° e 150° do alto e oito furos a 60° no tubo oval (`ak47.py`, `_tubo_de_gases`). |
| A janela de ejeção de uma AK-47 tipo 3 pelo lado direito: o transportador em branco enche a abertura — dorso arredondado em cima, face lisa e polida embaixo, um vinco entre os dois — e atrás da ponta dele se vê o escuro do receptor; o ferrolho não aparece. A busca do Pinterest ("ak 47 ejection port bolt") só mostrou vistas explodidas e ferrolhos de outras armas sem entrar na conta. | Commons: "File:7,62 RK 54 Kalasnikov.JPG" (MKFI, domínio público; Museu de Infantaria de Mikkeli), lida só no navegador | O vão atrás da parede de 3 mm e o transportador a 1 mm dela, 45 % da janela de face lisa e 55 % de dorso, a ponta de baixo 6 mm antes da borda de trás e a de cima em rampa (`ak47.py`, bloco do ferrolho). |

```

---

### Tarefa 7: Assar e níveis de detalhe

**Files:**
- Create: `tools/blender/armas/assar.py`, `tools/blender/armas/lod.py`

Do modelo alto para o de jogo (desenho, seções 4.3 e 4.4): UV automático por peça com um empacotamento só (margem de 8
px em 2048), conferência de densidade de texel e de sobreposição, e o assar no Cycles (GPU) de uma cópia juntada do
modelo alto (fonte única) para uma cópia juntada das peças de jogo: normal em espaço tangente, sombra de contato com
todas as peças juntas, e os três canais dos materiais de fábrica (aspereza, borda, cor) por emissão — gravados e
empacotados como diz D3. O LOD1 (`mundo`) sai das peças de jogo sem as pequenas e sem chanfro, juntado, dizimado até o
orçamento e assado de novo em 512; o LOD2 (`longe`) sai do LOD1 (mesmas UVs) sem as ilhas pequenas da base, dizimado.
Na RTX 2070, o assar da AK leva cerca de 40 s no perto e 20 s no mundo.

- [ ] **Passo 1: Assar**

```python file=tools/blender/armas/assar.py
# Assar do modelo alto para o de jogo (Fase 4.1a; desenho em docs/superpowers/specs/2026-09-26-armas-realistas-design.md,
# seções 4.3 e 4.4; plano da 4.1a, D3): UV automático por peça com um empacotamento só (a mesma textura para a arma
# inteira), conferência de densidade de texel e de sobreposição, e o assar no Cycles na GPU — normal em espaço tangente
# (convenção OpenGL), sombra de contato com todas as peças juntas, e os canais dos materiais de fábrica por emissão
# (canal_aspereza, canal_borda, canal_cor). Empacota `_n` (RGB) e `_m` (R sombra, G aspereza, B borda, A cor) e grava em
# WebP sem perdas (qualidade 100 no Blender = VP8L).
import math

import bmesh
import bpy
import numpy as np

from . import estudio
from .unidades import S


def selecionar(objetos, ativo=None):
    bpy.ops.object.select_all(action='DESELECT')
    for o in objetos:
        o.select_set(True)
    bpy.context.view_layer.objects.active = ativo or objetos[0]


def _empacotar(objetos, lado_px, margem_px):
    """Um empacotamento só para todas as peças, com a margem exata em fração da textura."""
    selecionar(objetos)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.select_all(action='SELECT')
    bpy.ops.uv.pack_islands(rotate=True, margin_method='FRACTION', margin=margem_px / lado_px)
    bpy.ops.object.mode_set(mode='OBJECT')


def uv_automatico(objetos, lado_px, margem_px=8, tentativas=4):
    """Projeção por ângulo em cada peça e um empacotamento só para todas (margem em pixels do lado da textura). A
    projeção às vezes junta numa ilha faces viradas para o mesmo lado em alturas diferentes (na AK, o fundo do vão do
    transportador, o degrau do receptor e o alto dele), que caem umas sobre as outras na UV, e o empacotamento às vezes
    encosta duas ilhas: depois dele, a face que cair sobre outra vira uma ilha própria, projetada no plano dela na escala
    da arma, e tudo é empacotado de novo, até não sobrar nenhuma. (Baixar o limite para 45° também tirava as dobras, mas
    as ilhas a mais, cada uma com a sua margem, custavam 17 % da densidade de texel.)"""
    selecionar(objetos)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=math.radians(66.0), island_margin=margem_px / lado_px, area_weight=0.0,
                             correct_aspect=True, scale_to_bounds=False)
    bpy.ops.object.mode_set(mode='OBJECT')
    _empacotar(objetos, lado_px, margem_px)
    for _ in range(tentativas):
        marcadas = _faces_sobrepostas(objetos)
        if not marcadas:
            return
        _cada_uma_no_seu_plano(objetos, marcadas)
        _empacotar(objetos, lado_px, margem_px)


def _triangulo_na_grade(uv, tri, grade):
    """Texels (da grade de conferência) cobertos pelo triângulo: (y0, x0, máscara) ou None."""
    p = np.array([[uv[i].uv.x * grade, uv[i].uv.y * grade] for i in tri.loops])
    x0, y0 = np.floor(p.min(0)).astype(int)
    x1, y1 = np.ceil(p.max(0)).astype(int)
    x0, y0, x1, y1 = max(0, x0), max(0, y0), min(grade, x1), min(grade, y1)
    if x1 <= x0 or y1 <= y0:
        return None
    xs, ys = np.meshgrid(np.arange(x0, x1) + 0.5, np.arange(y0, y1) + 0.5)
    (ax, ay), (bx, by), (cx, cy) = p
    d = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy)
    if abs(d) < 1e-12:
        return None
    l1 = ((by - cy) * (xs - cx) + (cx - bx) * (ys - cy)) / d
    l2 = ((cy - ay) * (xs - cx) + (ax - cx) * (ys - cy)) / d
    return y0, x0, (l1 >= 0) & (l2 >= 0) & (l1 + l2 <= 1)


def _faces_sobrepostas(objetos, grade=1024):
    """{nome da peça: índices das faces} que cobrem um texel coberto por outra face — a mesma conta da
    `sobreposicao_uv` (dois triângulos da mesma face não contam)."""
    dono = np.full((grade, grade), -1, np.int64)
    faces = []
    marcadas = set()
    for oi, ob in enumerate(objetos):
        me = ob.data
        uv = me.uv_layers.active.data
        me.calc_loop_triangles()
        for tri in me.loop_triangles:
            r = _triangulo_na_grade(uv, tri, grade)
            if r is None:
                continue
            y0, x0, dentro = r
            chave = (oi, tri.polygon_index)
            if not faces or faces[-1] != chave:
                faces.append(chave)
            k = len(faces) - 1
            bloco = dono[y0:y0 + dentro.shape[0], x0:x0 + dentro.shape[1]]
            outros = np.unique(bloco[dentro & (bloco >= 0) & (bloco != k)])
            if outros.size:
                marcadas.add(k)
                marcadas.update(int(o) for o in outros)
            bloco[dentro & (bloco < 0)] = k
    res = {}
    for k in marcadas:
        oi, pi = faces[k]
        res.setdefault(objetos[oi].name, set()).add(pi)
    return res


def _cada_uma_no_seu_plano(objetos, marcadas):
    """Cada face marcada vira uma ilha própria, projetada no plano dela com a escala de UV por mm da arma inteira (a
    densidade de texel continua a mesma quando o empacotamento seguinte escala tudo junto)."""
    area_uv = area_3d = 0.0
    for ob in objetos:
        me = ob.data
        uv = me.uv_layers.active.data
        for p in me.polygons:
            pts = [uv[i].uv for i in p.loop_indices]
            area_uv += abs(sum(pts[i].x * pts[i - 1].y - pts[i - 1].x * pts[i].y for i in range(len(pts)))) / 2
            area_3d += p.area
    k = math.sqrt(area_uv / area_3d)
    for ob in objetos:
        me = ob.data
        uv = me.uv_layers.active.data
        for pi in marcadas.get(ob.name, ()):
            p = me.polygons[pi]
            cos = [me.vertices[me.loops[li].vertex_index].co for li in p.loop_indices]
            eu = (cos[1] - cos[0]).normalized()
            ev = p.normal.cross(eu).normalized()
            for li, co in zip(p.loop_indices, cos):
                d = co - cos[0]
                uv[li].uv = (d.dot(eu) * k, d.dot(ev) * k)


def densidade_texel(objetos, lado_px):
    """Pixels por mm de cada peça (raiz da área em UV × lado² sobre a área em mm²), relativos à mediana."""
    valores = {}
    for ob in objetos:
        me = ob.data
        uv = me.uv_layers.active.data
        area_mm = 0.0
        area_uv = 0.0
        for p in me.polygons:
            area_mm += p.area / (S * S)
            pts = [uv[i].uv for i in p.loop_indices]
            for k in range(1, len(pts) - 1):
                a, b, c = pts[0], pts[k], pts[k + 1]
                area_uv += abs((b.x - a.x) * (c.y - a.y) - (c.x - a.x) * (b.y - a.y)) / 2
        if area_mm > 0:
            valores[ob.name] = math.sqrt(area_uv * lado_px * lado_px / area_mm)
    med = float(np.median(list(valores.values())))
    rel = {k: v / med for k, v in valores.items()}
    return {'medianaPxPorMm': round(med, 3), 'minimo': round(min(rel.values()), 3), 'maximo': round(max(rel.values()), 3)}


def sobreposicao_uv(objetos, grade=1024):
    """Texels (numa grade de conferência) cobertos por dois triângulos ou mais: ilhas encavaladas ou uma dobra dentro
    da ilha (face torcida)."""
    conta = np.zeros((grade, grade), np.int32)
    for ob in objetos:
        me = ob.data
        uv = me.uv_layers.active.data
        me.calc_loop_triangles()
        for tri in me.loop_triangles:
            p = np.array([[uv[i].uv.x * grade, uv[i].uv.y * grade] for i in tri.loops])
            x0, y0 = np.floor(p.min(0)).astype(int)
            x1, y1 = np.ceil(p.max(0)).astype(int)
            x0, y0, x1, y1 = max(0, x0), max(0, y0), min(grade, x1), min(grade, y1)
            if x1 <= x0 or y1 <= y0:
                continue
            xs, ys = np.meshgrid(np.arange(x0, x1) + 0.5, np.arange(y0, y1) + 0.5)
            (ax, ay), (bx, by), (cx, cy) = p
            d = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy)
            if abs(d) < 1e-12:
                continue
            l1 = ((by - cy) * (xs - cx) + (cx - bx) * (ys - cy)) / d
            l2 = ((cy - ay) * (xs - cx) + (ax - cx) * (ys - cy)) / d
            dentro = (l1 >= 0) & (l2 >= 0) & (l1 + l2 <= 1)
            conta[y0:y1, x0:x1] += dentro
    return int((conta > 1).sum())


def _imagem(nome, lado, fundo=(0.0, 0.0, 0.0, 1.0)):
    """Imagem de ponto flutuante do assar, sem gestão de cor, com o `fundo` onde nenhuma ilha é assada: o valor neutro
    do canal, para os mipmaps de longe não puxarem as bordas das ilhas para o preto."""
    img = bpy.data.images.new(nome, lado, lado, alpha=False, float_buffer=True)
    img.generated_color = fundo
    img.colorspace_settings.name = 'Non-Color'
    return img


def _gravar_webp(pasta, nome, rgba, alfa):
    """Grava `rgba` (lado × lado × 4, de 0 a 1, na ordem de linhas do Blender) em WebP sem perdas por uma imagem de 8
    bits: a de ponto flutuante do Blender guarda o RGB multiplicado pelo alfa e divide ao gravar — o que estragava os
    canais de dados da `_m` (o alfa dela é a variação de cor, não transparência)."""
    lado = rgba.shape[0]
    img = bpy.data.images.new(nome, lado, lado, alpha=alfa, float_buffer=False)
    img.colorspace_settings.name = 'Non-Color'
    img.alpha_mode = 'STRAIGHT'
    img.pixels.foreach_set(np.clip(rgba, 0.0, 1.0).astype(np.float32).ravel())
    caminho = f'{pasta}/{nome}.webp'
    img.filepath_raw = caminho
    img.file_format = 'WEBP'
    img.save(filepath=caminho, quality=100)
    bpy.data.images.remove(img)
    return caminho


def _suavizar(canal):
    """Filtro binomial 5 × 5 (quase um gaussiano de 1 pixel): tira o ruído de amostragem da sombra de contato, que é
    larga por natureza, sem mudar a forma dela — o WebP sem perdas guarda ruído a peso de ouro."""
    k = np.array([1.0, 4.0, 6.0, 4.0, 1.0], np.float32) / 16.0
    altura, largura = canal.shape
    c = np.pad(canal, 2, mode='edge')
    c = sum(k[i] * c[:, i:i + largura] for i in range(5))
    return sum(k[i] * c[i:i + altura, :] for i in range(5))


def _juntar_copias(objetos, nome):
    """Uma cópia juntada das peças, com os modificadores aplicados (mantém as UVs e os materiais): o alvo único do assar
    (as peças de jogo) e a fonte única (o modelo alto — uma árvore de raios em vez de uma por peça)."""
    dg = bpy.context.evaluated_depsgraph_get()
    copias = []
    for ob in objetos:
        me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg), preserve_all_data_layers=True, depsgraph=dg)
        c = bpy.data.objects.new(f'{nome}.{ob.name}', me)
        c.matrix_world = ob.matrix_world.copy()
        bpy.context.scene.collection.objects.link(c)
        copias.append(c)
    selecionar(copias)
    if len(copias) > 1:
        bpy.ops.object.join()
    alvo = bpy.context.view_layer.objects.active
    alvo.name = nome
    return alvo


def _ligar_imagem(alvo, img):
    """Nó de imagem ativo em cada material do alvo (o Cycles assa no nó ativo)."""
    nos = []
    for slot in alvo.material_slots:
        nt = slot.material.node_tree
        n = nt.nodes.new('ShaderNodeTexImage')
        n.image = img
        nt.nodes.active = n
        nos.append((nt, n))
    return nos


def _emitir_canal(fontes, canal):
    """Liga o `canal` de cada material de fábrica das fontes numa emissão na saída; devolve como desfazer."""
    desfazer = []
    vistos = set()
    for ob in fontes:
        for slot in ob.material_slots:
            m = slot.material
            if m is None or m.name in vistos:
                continue
            vistos.add(m.name)
            nt = m.node_tree
            saida = next(n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL')
            antigo = saida.inputs['Surface'].links[0].from_socket if saida.inputs['Surface'].links else None
            em = nt.nodes.new('ShaderNodeEmission')
            no = nt.nodes.get(canal)
            if no is None:
                em.inputs['Color'].default_value = (0.5, 0.5, 0.5, 1)
            else:
                nt.links.new(no.outputs[0], em.inputs['Color'])
            nt.links.new(em.outputs['Emission'], saida.inputs['Surface'])
            desfazer.append((nt, saida, antigo, em))
    return desfazer


def _desfazer(desfazer):
    for nt, saida, antigo, em in desfazer:
        if antigo is not None:
            nt.links.new(antigo, saida.inputs['Surface'])
        nt.nodes.remove(em)


def _pixels(img, lado):
    a = np.empty(lado * lado * 4, np.float32)
    img.pixels.foreach_get(a)
    return a.reshape(lado, lado, 4)


def assar_conjunto(fontes, pecas_jogo, lado_px, margem_px, pasta, nome_n, nome_m, amostras_ao=64, amostras_aa=16,
                   extrusao_mm=2.0):
    """Assa o conjunto de texturas de um nível: normal, sombra de contato e os três canais. Grava `_n` e `_m`. O relevo
    e os canais usam `amostras_aa` por pixel (antisserrilhado: o detalhe menor que o texel vira a média dele, não ruído);
    a sombra de contato, `amostras_ao`; a sombra e a aspereza passam pelo filtro binomial e os canais de dados são
    quantizados em degraus que não aparecem."""
    sc = bpy.context.scene
    estudio.gpu()
    sc.render.bake.use_selected_to_active = True
    # Sem limpar a imagem antes: o fundo neutro de cada canal fica onde nenhuma ilha é assada (limpar zerava tudo).
    sc.render.bake.use_clear = False
    sc.render.bake.cage_extrusion = extrusao_mm * S
    sc.render.bake.max_ray_distance = extrusao_mm * 2 * S
    sc.render.bake.margin = margem_px
    sc.render.bake.margin_type = 'EXTEND'
    alvo = _juntar_copias(pecas_jogo, f'alvo_{nome_n}')
    fonte = _juntar_copias(fontes, f'fonte_{nome_n}')
    for vis in ('visible_diffuse', 'visible_glossy', 'visible_shadow', 'visible_transmission', 'visible_volume_scatter'):
        setattr(alvo, vis, False)
    # Só a cópia do modelo alto faz sombra de contato: as peças (as do alto também), os LODs e o estúdio saem do assar.
    fora = [o for o in bpy.context.scene.objects if o is not fonte and o is not alvo and not o.hide_render]
    for o in fora:
        o.hide_render = True
    imgs = {}

    def assar(tipo, chave, fundo, amostras=1, canal=None):
        img = _imagem(f'{nome_n}_{chave}', lado_px, fundo=fundo)
        nos = _ligar_imagem(alvo, img)
        desfazer = _emitir_canal(fontes, canal) if canal else []
        sc.cycles.samples = amostras
        selecionar([fonte, alvo], ativo=alvo)
        if tipo == 'NORMAL':
            sc.render.bake.normal_space = 'TANGENT'
            sc.render.bake.normal_r, sc.render.bake.normal_g, sc.render.bake.normal_b = 'POS_X', 'POS_Y', 'POS_Z'
        bpy.ops.object.bake(type=tipo)
        _desfazer(desfazer)
        for nt, n in nos:
            nt.nodes.remove(n)
        imgs[chave] = img

    assar('NORMAL', 'normal', (0.5, 0.5, 1.0, 1.0), amostras_aa)
    assar('AO', 'ao', (1.0, 1.0, 1.0, 1.0), amostras_ao)
    for chave, canal, neutro in (('aspereza', 'canal_aspereza', 0.5), ('borda', 'canal_borda', 0.0), ('cor', 'canal_cor', 0.5)):
        assar('EMIT', chave, (neutro, neutro, neutro, 1.0), amostras_aa, canal)
    n = _pixels(imgs['normal'], lado_px)[..., :3]
    ao = _suavizar(_pixels(imgs['ao'], lado_px)[..., 0])
    aspereza = _suavizar(_pixels(imgs['aspereza'], lado_px)[..., 0])
    m = np.stack([ao, aspereza] + [_pixels(imgs[k], lado_px)[..., 0] for k in ('borda', 'cor')], axis=2)
    # Os canais de dados só modulam o material (no oxidado, ±16 % de aspereza e ±6 % de cor): degraus de 4/255 na
    # aspereza e na cor e de 2/255 na sombra de contato não aparecem no jogo e cortam cerca de 30 % do WebP sem perdas
    # (a `_m` da AK fica em 2,97 MB). A borda (o desgaste) fica inteira.
    for canal, passo in ((0, 2.0), (1, 4.0), (3, 4.0)):
        m[..., canal] = np.round(m[..., canal] * 255.0 / passo) * passo / 255.0
    # O WebP sem perdas pode trocar o RGB dos pixels de alfa 0: a variação de cor (o alfa) fica em 1/255 no mínimo.
    m[..., 3] = np.maximum(m[..., 3], 1.0 / 255.0)
    caminhos = {
        nome_n: _gravar_webp(pasta, nome_n, np.concatenate([n, np.ones((lado_px, lado_px, 1), np.float32)], axis=2), False),
        nome_m: _gravar_webp(pasta, nome_m, m, True),
    }
    bpy.data.objects.remove(alvo)
    bpy.data.objects.remove(fonte)
    for o in fora:
        o.hide_render = False
    for img in imgs.values():
        bpy.data.images.remove(img)
    return caminhos
```

- [ ] **Passo 2: Níveis de detalhe**

```python file=tools/blender/armas/lod.py
# Níveis de detalhe das armas realistas (Fase 4.1a; desenho, seções 4.3 e 5.1): o LOD1 (`mundo`) sai das peças de jogo
# sem as pequenas e sem chanfro, juntado por peça, dizimado até caber no orçamento e com UV próprio (assado de novo em
# 512/256); o LOD2 (`longe`) sai de uma cópia do LOD1 (as mesmas UVs, então as mesmas texturas) sem as ilhas pequenas da
# base e dizimado. Nenhuma peça móvel some: sem ela o nó não existiria e o jogo perderia a animação.
import bmesh
import bpy

from . import soquetes
from .unidades import S


def diagonal_mm(ob):
    d = [ob.dimensions.x, ob.dimensions.y, ob.dimensions.z]
    return (d[0] ** 2 + d[1] ** 2 + d[2] ** 2) ** 0.5 / S


def triangulos(objetos):
    dg = bpy.context.evaluated_depsgraph_get()
    total = 0
    for ob in objetos:
        me = ob.evaluated_get(dg).to_mesh()
        me.calc_loop_triangles()
        total += len(me.loop_triangles)
        ob.evaluated_get(dg).to_mesh_clear()
    return total


def dizimar_ate(objetos, orcamento, margem=0.95, piso=12):
    """Mesma razão de dizimação em todas as peças, por bisseção, até caber em `orcamento` × `margem`; aplica. Peça
    pequena não desce de `piso` triângulos: a razão comum achatava o cão e o gatilho do longe em dois triângulos colados
    (a mesma face de frente e de costas), que o Draco reduz a um ao exportar."""
    antes = {ob.name: triangulos([ob]) for ob in objetos}
    for ob in objetos:
        m = ob.modifiers.new('dizimar', 'DECIMATE')
        m.decimate_type = 'COLLAPSE'
        m.use_collapse_triangulate = True

    def razao(ob, r):
        return min(1.0, max(r, piso / max(1, antes[ob.name])))
    lo, hi = 0.01, 1.0
    for _ in range(18):
        meio = (lo + hi) / 2
        for ob in objetos:
            ob.modifiers['dizimar'].ratio = razao(ob, meio)
        if triangulos(objetos) <= orcamento * margem:
            lo = meio
        else:
            hi = meio
    for ob in objetos:
        ob.modifiers['dizimar'].ratio = razao(ob, lo)
        bpy.context.view_layer.objects.active = ob
        bpy.ops.object.modifier_apply(modifier='dizimar')
        _sem_degeneradas(ob)
        w = ob.modifiers.new('normais', 'WEIGHTED_NORMAL')
        w.keep_sharp = True
        bpy.ops.object.modifier_apply(modifier='normais')
    return lo


def _sem_degeneradas(ob, distancia_mm=0.06):
    """Tira as arestas mais curtas que `distancia_mm`, as faces de área zero e as repetidas que a dizimação deixa: o
    Draco (posição em 14 bits, ~0,05 mm na arma inteira) as descarta ao exportar, e a contagem do relatório deixaria de
    bater com a do .glb."""
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bmesh.ops.dissolve_degenerate(bm, dist=distancia_mm * S, edges=bm.edges[:])
    # A mesma face duas vezes (de frente e de costas): o Draco guarda uma só.
    bm.verts.index_update()
    vistas, repetidas = set(), []
    for f in bm.faces:
        chave = tuple(sorted(v.index for v in f.verts))
        if chave in vistas:
            repetidas.append(f)
        vistas.add(chave)
    if repetidas:
        bmesh.ops.delete(bm, geom=repetidas, context='FACES_ONLY')
    bm.to_mesh(ob.data)
    bm.free()


def lod_mundo(col_jogo, col_destino, pivos, orcamento, menor_mm=8.0):
    """LOD1 a partir das peças de jogo: some a peça da base menor que `menor_mm`; tira o chanfro; junta; dizima."""
    removidos = []
    for ob in col_jogo.objects:
        m = ob.modifiers.get('chanfro')
        if m is not None:
            m.show_render = False
            m.show_viewport = False
            removidos.append(m)
    filtro = lambda ob: ob.get('peca', 'base') != 'base' or diagonal_mm(ob) >= menor_mm
    partes = soquetes.juntar_pecas(col_jogo, col_destino, 'mundo', pivos, filtro)
    for m in removidos:
        m.show_render = True
        m.show_viewport = True
    objs = [partes[p] for p in pivos]
    razao = dizimar_ate(objs, orcamento)
    return partes, razao


def lod_longe(partes_mundo, col_destino, pivos, orcamento, menor_mm=25.0):
    """LOD2 a partir de cópias do LOD1 (mesmas UVs): some a ilha da base menor que `menor_mm`; dizima."""
    partes = {}
    for peca, ob in partes_mundo.items():
        if peca.startswith('_'):
            continue
        c = ob.copy()
        c.data = ob.data.copy()
        c.name = f'longe_{peca}'
        c.data.name = c.name
        col_destino.objects.link(c)
        if peca == 'base':
            bm = bmesh.new()
            bm.from_mesh(c.data)
            vistos = set()
            tirar = []
            for f in bm.faces:
                if f.index in vistos:
                    continue
                ilha, pilha = [], [f]
                vistos.add(f.index)
                while pilha:
                    g = pilha.pop()
                    ilha.append(g)
                    for e in g.edges:
                        for h in e.link_faces:
                            if h.index not in vistos:
                                vistos.add(h.index)
                                pilha.append(h)
                xs = [v.co for g in ilha for v in g.verts]
                dx = max(v.x for v in xs) - min(v.x for v in xs)
                dy = max(v.y for v in xs) - min(v.y for v in xs)
                dz = max(v.z for v in xs) - min(v.z for v in xs)
                if (dx * dx + dy * dy + dz * dz) ** 0.5 / S < menor_mm:
                    tirar.extend(ilha)
            if tirar:
                bmesh.ops.delete(bm, geom=list(set(tirar)), context='FACES')
            bm.to_mesh(c.data)
            bm.free()
        partes[peca] = c
    razao = dizimar_ate([partes[p] for p in pivos], orcamento)
    return partes, razao
```

- [ ] **Passo 3: Conferir as texturas** — depois do primeiro `construir` (Tarefa 8), abrir `ak47_n.webp` e
  `ak47_m.webp` (e os de mundo) e olhar canal por canal: a normal sem costura visível nas junções das ilhas nem
  "espelho" de relevo; a sombra de contato escurecendo as frestas (guarda-mãos, braçadeiras, pinos) sem manchas; a
  borda só nas arestas; o veio da madeira no canal A; nenhuma ilha fora do quadrado. Densidade de texel entre 0,6 e 1,6
  da mediana (fora disso, costura sugerida por peça — `bpy.ops.uv.mark_seam` nas arestas escolhidas antes do
  `smart_project` — e assar de novo).

---

### Tarefa 8: Construir, exportar, conferir e o lançador

**Files:**
- Create: `tools/blender/armas/exportar.py`, `tools/blender/armas/conferir.py`, `tools/blender/armas/principal.py`
- Modify: `tools/blender.mjs`
- Create (gerados): `assets/armas/ak47/ak47.glb`, `ak47_n.webp`, `ak47_m.webp`, `ak47_mundo_n.webp`,
  `ak47_mundo_m.webp`, `ak47.relatorio.json`
- Test: `tests/armaAk47.test.js`

- [ ] **Passo 1: Exportar**

```python file=tools/blender/armas/exportar.py
# Exportação das armas realistas (Fase 4.1a; desenho em docs/superpowers/specs/2026-09-26-armas-realistas-design.md,
# seção 4.5; plano da 4.1a, D1 e D2): a hierarquia do .glb — raiz `<id>`, os níveis `perto`, `mundo` e `longe` com as
# peças `<nivel>_<peca>` (origem no pivô), os soquetes `soquete_<nome>` dentro de `soquetes` —, a escala para u
# (1000/25,4) com a origem no pino do gatilho e o glTF binário com o Y para cima, as tangentes, as UV, as normais e os
# extras (o eixo das peças móveis), com a geometria comprimida pelo Draco (decisão do usuário de 2026-09-26: a AK cai de
# 1,22 para 0,29 MB; posição em 14 bits, normal em 10, UV e tangente em 12). As texturas já foram gravadas pelo assar;
# o relatório vai ao lado.
import json
import os

import bpy
from mathutils import Matrix, Vector

from .unidades import S, U_POR_M


def _vazio(nome, colecao, pai=None):
    ob = bpy.data.objects.new(nome, None)
    colecao.objects.link(ob)
    ob.parent = pai
    return ob


def _mover(ob, colecao):
    for c in list(ob.users_collection):
        c.objects.unlink(ob)
    colecao.objects.link(ob)


def exportar(ctx, origem_mm, lods, soquetes_objs, pasta):
    """Monta a hierarquia na escala do jogo e grava `<id>.glb`. Muda a cena: a .blend da conferência é gravada antes."""
    col = bpy.data.collections.new('exportar')
    bpy.context.scene.collection.children.link(col)
    origem = Vector((origem_mm[0] * S, 0.0, origem_mm[1] * S))
    escala = Matrix.Scale(U_POR_M, 4)
    raiz = _vazio(ctx['id'], col)
    selecionados = [raiz]
    for nome, partes in lods.items():
        grupo = _vazio(nome, col, raiz)
        selecionados.append(grupo)
        for peca, ob in partes.items():
            if peca.startswith('_'):
                continue
            ob.data.transform(escala)
            ob.location = (ob.location - origem) * U_POR_M
            _mover(ob, col)
            ob.parent = grupo
            selecionados.append(ob)
    pasta_soq = _vazio('soquetes', col, raiz)
    selecionados.append(pasta_soq)
    for s in soquetes_objs:
        s.location = (s.location - origem) * U_POR_M
        _mover(s, col)
        s.parent = pasta_soq
        selecionados.append(s)
    bpy.ops.object.select_all(action='DESELECT')
    for o in selecionados:
        o.select_set(True)
    bpy.context.view_layer.objects.active = raiz
    caminho = os.path.join(pasta, f"{ctx['id']}.glb")
    bpy.ops.export_scene.gltf(
        filepath=caminho, export_format='GLB', use_selection=True, export_yup=True, export_apply=True,
        export_texcoords=True, export_normals=True, export_tangents=True, export_materials='EXPORT',
        export_image_format='NONE', export_extras=True, export_cameras=False, export_lights=False,
        export_animations=False, export_skins=False, export_morph=False, export_draco_mesh_compression_enable=True,
        export_draco_mesh_compression_level=6, export_draco_position_quantization=14, export_draco_normal_quantization=10,
        export_draco_texcoord_quantization=12, export_draco_generic_quantization=12)
    return caminho


def gravar_relatorio(pasta, id_, relatorio):
    caminho = os.path.join(pasta, f'{id_}.relatorio.json')
    with open(caminho, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(relatorio, f, ensure_ascii=False, indent=1)
        f.write('\n')
    return caminho
```

- [ ] **Passo 2: Conferir**

```python file=tools/blender/armas/conferir.py
# Renders da conferência das armas realistas (Fase 4.1a; desenho, seção 4.7): lado, cima, frente, 3/4 dos dois lados,
# perto do receptor e a vista aproximada da primeira pessoa (sem as luvas até a 4.1b; a câmera no olho do boneco com o
# FOV do viewmodel — 60 horizontais em 4:3 = 75,2° em 16:9 — e a arma na posição da categoria `rifle`), no modelo alto
# com os materiais de fábrica, em tools/blender/conferencia/<id>/ (fora do git). A sobreposição da silhueta com a foto
# (sobreposicao.png) sai do validar.py.
import os

import bpy

from . import estudio
from .unidades import S


def conferir(ctx, pasta, amostras=160):
    sc = bpy.context.scene
    alto = bpy.data.collections['alto']
    for col in sc.collection.children:
        col.hide_render = col is not alto
    xs = [p[0] for p in ctx['ficha']['contorno']]
    ys = [p[1] for p in ctx['ficha']['contorno']]
    cx, cy = (min(xs) + max(xs)) / 2 * S, (min(ys) + max(ys)) / 2 * S
    comp = (max(xs) - min(xs)) * S
    estudio.montar((cx, 0.0, cy))
    dispositivo = estudio.render(1600, 900, amostras)
    c = (cx, 0.0, cy)
    receptor = (-0.50, 0.0, -0.01)
    olho = (-0.78, 0.114, 0.079)  # 9 u atrás, 4,5 u à esquerda e 3,1 u acima da origem (o pino do gatilho)
    vistas = {
        'lado': estudio.camera('lado', (cx, -1.5, cy), c, orto=comp * 1.04),
        'cima': estudio.camera('cima', (cx, 0.0, cy + 1.5), c, orto=comp * 1.04),
        'frente': estudio.camera('frente', (0.9, 0.0, cy), (0.0, 0.0, cy), orto=0.45),
        'tres_direita': estudio.camera('tres_direita', (cx + 0.27, -0.72, cy + 0.29), c, 50),
        'tres_esquerda': estudio.camera('tres_esquerda', (cx + 0.27, 0.72, cy + 0.29), c, 50),
        'perto': estudio.camera('perto', (receptor[0] + 0.08, -0.24, receptor[2] + 0.07), receptor, 55),
        'primeira_pessoa': estudio.camera('primeira_pessoa', olho, (olho[0] + 1.0, olho[1] - 0.02, olho[2] - 0.03), 23.4),
    }
    arquivos = []
    for nome, cam in vistas.items():
        sc.camera = cam
        sc.render.filepath = os.path.join(pasta, f'{nome}.png')
        bpy.ops.render.render(write_still=True)
        arquivos.append(sc.render.filepath)
    for col in sc.collection.children:
        col.hide_render = False
    return arquivos, dispositivo
```

- [ ] **Passo 3: O ponto de entrada**

```python file=tools/blender/armas/principal.py
# Ponto de entrada do Blender para as armas realistas (Fase 4.1a; desenho em docs/superpowers/specs/
# 2026-09-26-armas-realistas-design.md, seção 4), chamado por tools/blender.mjs:
#   blender -b --factory-startup --python-exit-code 1 -P tools/blender/armas/principal.py -- <ação> <contexto.json>
# Ações: construir (modelo alto e de jogo, zonas, peças móveis, soquetes, UV, assar, LODs, validar, gravar a .blend da
# conferência e exportar), validar (reabre a .blend e refaz a validação, sem exportar) e conferir (reabre a .blend e
# renderiza as vistas). O contexto (JSON) traz a ficha, a pintura de fábrica, as peças, as zonas, os soquetes, o
# orçamento, as pastas e o hash das entradas. As linhas `MASSACRE-*` da saída são lidas pelo lançador; reprovado sai com
# código 1 (o lançador mostra os problemas).
import importlib
import json
import os
import sys
import time

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(AQUI))

import bpy  # noqa: E402

from armas import assar, conferir, exportar, lod, materiais, pecas, soquetes, validar, zonas  # noqa: E402


def _colecao(nome):
    col = bpy.data.collections.get(nome) or bpy.data.collections.new(nome)
    if col.name not in bpy.context.scene.collection.children:
        bpy.context.scene.collection.children.link(col)
    return col


def _malhas(col):
    return [o for o in col.objects if o.type == 'MESH' and not o.get('cortador')]


def _lados(ctx):
    orc = ctx['orcamento']
    lados = {}
    for sufixo, esperado in (('n', orc['textura']), ('m', orc['textura']), ('mundo_n', orc['texturaMundo']), ('mundo_m', orc['texturaMundo'])):
        nome = f"{ctx['id']}_{sufixo}.webp"
        img = bpy.data.images.load(os.path.join(ctx['saida'], nome), check_existing=False)
        lados[nome] = (img.size[0], esperado)
        bpy.data.images.remove(img)
    return lados


def _pecas(partes):
    return [o for k, o in partes.items() if not k.startswith('_')]


def _etapa(t0, nome):
    """Linha de progresso para o lançador: o construir leva minutos (assar no Cycles) e o terminal não fica mudo."""
    print('MASSACRE-ETAPA', json.dumps({'etapa': nome, 's': round(time.time() - t0, 1)}, ensure_ascii=False), flush=True)


def _validar(ctx, arma, lods, jogo):
    """A validação da seção 4.6 sobre o que foi construído: as peças de jogo (malha, cano), os níveis (silhueta, medidas,
    triângulos, peças, zonas), os soquetes, as texturas gravadas e as UVs dos dois conjuntos (perto e mundo; o longe
    usa as do mundo)."""
    pecas_jogo = _malhas(jogo)
    canos = [o for o in pecas_jogo if o.name.split('.')[0] == 'cano']
    soquetes_def = arma.soquetes(ctx['ficha'])
    nomes_soq = [o.name[len('soquete_'):] for o in bpy.data.collections['soquetes'].objects]
    perto = _pecas(lods['perto'])
    uv = assar.sobreposicao_uv(perto) + assar.sobreposicao_uv(_pecas(lods['mundo']))
    densidade = assar.densidade_texel(perto, ctx['orcamento']['textura'])
    return validar.relatorio_e_problemas(ctx, ctx['ficha'], lods, soquetes_def, nomes_soq, canos, pecas_jogo, _lados(ctx),
                                         uv, densidade, ctx['conferencia'])


def construir(ctx):
    t0 = time.time()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    ficha = ctx['ficha']
    arma = importlib.import_module(f"armas.{ctx['id']}")
    orc = ctx['orcamento']
    os.makedirs(ctx['saida'], exist_ok=True)
    os.makedirs(ctx['conferencia'], exist_ok=True)
    M = materiais.materiais_de_fabrica(ctx['fabrica'])
    alto = pecas.iniciar('alto', 'alto')
    arma.construir(ficha, M)
    pecas.finalizar(alto)
    jogo = pecas.iniciar('jogo', 'jogo')
    arma.construir(ficha, M)
    pecas.finalizar(jogo)
    zonas.aplicar_zonas(jogo)
    _etapa(t0, 'modelo alto e de jogo')
    pivos = arma.pivos(ficha)
    perto = soquetes.juntar_pecas(jogo, _colecao('perto'), 'perto', pivos)
    col_soq = _colecao('soquetes')
    soqs = [soquetes.soquete(col_soq, nome, x, y, lado, rot) for nome, (x, y), lado, rot in arma.soquetes(ficha)]
    lista_perto = [perto[p] for p in pivos]
    fontes = _malhas(alto)
    _etapa(t0, 'peças móveis e soquetes')
    assar.uv_automatico(lista_perto, orc['textura'], 8)
    assar.assar_conjunto(fontes, lista_perto, orc['textura'], 8, ctx['saida'], f"{ctx['id']}_n", f"{ctx['id']}_m")
    _etapa(t0, f"UV e assar o perto ({orc['textura']} px)")
    mundo, razao_mundo = lod.lod_mundo(jogo, _colecao('mundo'), pivos, orc['triangulos']['mundo'])
    lista_mundo = [mundo[p] for p in pivos]
    margem_mundo = max(2, round(8 * orc['texturaMundo'] / orc['textura']))
    assar.uv_automatico(lista_mundo, orc['texturaMundo'], margem_mundo)
    assar.assar_conjunto(fontes, lista_mundo, orc['texturaMundo'], margem_mundo, ctx['saida'], f"{ctx['id']}_mundo_n",
                         f"{ctx['id']}_mundo_m")
    _etapa(t0, f"mundo: LOD, UV e assar ({orc['texturaMundo']} px)")
    longe, razao_longe = lod.lod_longe(mundo, _colecao('longe'), pivos, orc['triangulos']['longe'])
    lods = {'perto': perto, 'mundo': mundo, 'longe': longe}
    _etapa(t0, 'longe: LOD')
    rel, problemas = _validar(ctx, arma, lods, jogo)
    _etapa(t0, 'validar')
    rel.update({
        'arma': ctx['id'], 'versao': 1, 'blender': bpy.app.version_string, 'gerado': time.strftime('%Y-%m-%dT%H:%M:%S'),
        'entradas': {'hash': ctx['hash']}, 'origemMM': list(arma.ORIGEM_MM),
        'dizimacao': {'mundo': round(razao_mundo, 4), 'longe': round(razao_longe, 4)},
        'facesEscondidasRemovidas': perto['_removidas'],
    })
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ctx['conferencia'], f"{ctx['id']}.blend"))
    if problemas:
        rel.update({'aprovado': False, 'problemas': problemas})
        exportar.gravar_relatorio(ctx['saida'], ctx['id'], rel)
        print('MASSACRE-REPROVADO', json.dumps(problemas, ensure_ascii=False))
        sys.exit(1)
    exportar.exportar(ctx, arma.ORIGEM_MM, lods, soqs, ctx['saida'])
    _etapa(t0, 'exportar')
    tamanhos = {nome: os.path.getsize(os.path.join(ctx['saida'], nome)) for nome in sorted(os.listdir(ctx['saida']))
                if nome.startswith(ctx['id']) and not nome.endswith('.relatorio.json')}
    total = sum(tamanhos.values())
    if total > orc['arquivosMB'] * 1024 * 1024:
        problemas.append(f"arquivos: {total / 1048576:.2f} MB (orçamento {orc['arquivosMB']} MB)")
    rel.update({'arquivos': tamanhos, 'aprovado': not problemas, 'problemas': problemas, 'segundos': round(time.time() - t0, 1)})
    exportar.gravar_relatorio(ctx['saida'], ctx['id'], rel)
    print('MASSACRE-RELATORIO', json.dumps({'silhueta': rel['silhueta'], 'lods': rel['lods'], 'bytes': total}, ensure_ascii=False))
    if problemas:
        print('MASSACRE-REPROVADO', json.dumps(problemas, ensure_ascii=False))
        sys.exit(1)


def revalidar(ctx):
    bpy.ops.wm.open_mainfile(filepath=os.path.join(ctx['conferencia'], f"{ctx['id']}.blend"))
    arma = importlib.import_module(f"armas.{ctx['id']}")
    lods = {}
    for nivel in ('perto', 'mundo', 'longe'):
        lods[nivel] = {o.name[len(nivel) + 1:]: o for o in bpy.data.collections[nivel].objects if o.type == 'MESH'}
    rel, problemas = _validar(ctx, arma, lods, bpy.data.collections['jogo'])
    print('MASSACRE-VALIDACAO', json.dumps({'silhueta': rel['silhueta'], 'medidas': rel['medidas'], 'problemas': problemas},
                                           ensure_ascii=False))
    if problemas:
        sys.exit(1)


def acao_conferir(ctx):
    bpy.ops.wm.open_mainfile(filepath=os.path.join(ctx['conferencia'], f"{ctx['id']}.blend"))
    arquivos, dispositivo = conferir.conferir(ctx, ctx['conferencia'])
    print('MASSACRE-CONFERIR', json.dumps(arquivos, ensure_ascii=False))
    print('MASSACRE-DISPOSITIVO', dispositivo)


def principal():
    args = sys.argv[sys.argv.index('--') + 1:]
    acao, caminho = args[0], args[1]
    with open(caminho, encoding='utf-8') as f:
        ctx = json.load(f)
    {'construir': construir, 'validar': revalidar, 'conferir': acao_conferir}[acao](ctx)


principal()
```

- [ ] **Passo 4: O lançador** — em `tools/blender.mjs`, trocar:

```js
//   npm run blender -- previa <arquivo.js> <saída>  a malha que o jogo gera de uma receita (o painel do Blender chama)
//
```

por:

```js
//   npm run blender -- previa <arquivo.js> <saída>  a malha que o jogo gera de uma receita (o painel do Blender chama)
//
// Armas realistas (Fase 4.1a; as de src/data/armasReais.js, construídas por tools/blender/armas/principal.py):
//   npm run blender -- construir <arma|todas> [--forcar]  modelo, assar, LODs, validar e exportar em assets/armas/<arma>/
//                                                         (pula a arma quando o hash das entradas não mudou)
//   npm run blender -- validar <arma|todas>   refaz a validação na .blend gravada e confere os arquivos exportados
//   npm run blender -- conferir <arma|todas>  renders em tools/blender/conferencia/<arma>/ (as de massinha, como acima)
//   npm run blender -- abrir <arma>           abre a .blend da conferência (as de massinha, como acima)
//
```

trocar:

```js
import { spawn, spawnSync } from 'node:child_process';
import { existsSync, mkdirSync, readFileSync, readdirSync, rmSync, writeFileSync } from 'node:fs';
```

por:

```js
import { spawn, spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { existsSync, mkdirSync, readFileSync, readdirSync, rmSync, writeFileSync } from 'node:fs';
```

trocar:

```js
import { gerarPrevia } from './blender/previa.mjs';
```

por:

```js
import { gerarPrevia } from './blender/previa.mjs';
import { validarSaida } from './blender/saida.mjs';
```

trocar:

```js
const SCRIPT = join(ROOT, 'tools', 'blender', 'massacre_armas.py');
```

por:

```js
const SCRIPT = join(ROOT, 'tools', 'blender', 'massacre_armas.py');
const SCRIPT_REAIS = join(ROOT, 'tools', 'blender', 'armas', 'principal.py');
```

trocar:

```js
function rodarSemJanela(args) {
  const res = spawnSync(blenderExe(), ['--background', '--factory-startup', '--python-exit-code', '1', '--python', SCRIPT, '--', ...args], {
```

por:

```js
function rodarSemJanela(args, script = SCRIPT) {
  const res = spawnSync(blenderExe(), ['--background', '--factory-startup', '--python-exit-code', '1', '--python', script, '--', ...args], {
```

trocar:

```js
async function principal() {
  const [acao, alvo, extra] = process.argv.slice(2);
  const { ARMAS } = await import('../src/data/armas/index.js');
  const ids = alvo === 'todas' ? Object.keys(ARMAS) : [alvo];
  const acoes = { abrir, conferir, 'ida-volta': idaVolta };
```

por:

```js
/**
 * Como rodarSemJanela, mas mostra as etapas (`MASSACRE-ETAPA`) enquanto o Blender trabalha: o construir leva minutos.
 * Devolve a saída inteira; com código diferente de zero lança com as últimas linhas, como o rodarSemJanela.
 */
function rodarComEtapas(args, script, rotulo) {
  return new Promise((aoTerminar, aoFalhar) => {
    const filho = spawn(blenderExe(), ['--background', '--factory-startup', '--python-exit-code', '1', '--python', script, '--', ...args], {
      stdio: ['ignore', 'pipe', 'pipe'],
    });
    let saida = '';
    let erro = '';
    let resto = '';
    filho.stdout.setEncoding('utf8');
    filho.stderr.setEncoding('utf8');
    filho.stdout.on('data', (pedaco) => {
      saida += pedaco;
      const linhas = (resto + pedaco).split('\n');
      resto = linhas.pop();
      for (const linha of linhas) {
        if (!linha.startsWith('MASSACRE-ETAPA ')) continue;
        const { etapa, s } = JSON.parse(linha.slice('MASSACRE-ETAPA '.length));
        console.log(`  ${rotulo} · ${etapa} (${s} s)`);
      }
    });
    filho.stderr.on('data', (pedaco) => {
      erro += pedaco;
    });
    filho.on('error', aoFalhar);
    filho.on('close', (codigo) => {
      if (codigo === 0) aoTerminar(saida);
      else aoFalhar(new Error(`o Blender falhou (código ${codigo}):\n${saida.split('\n').slice(-25).join('\n')}\n${erro}`));
    });
  });
}

/** Hash das entradas de uma arma realista: os .py do pacote, a ficha e o registro da arma (plano da 4.1a, D14). */
function hashEntradas(id, def, ficha) {
  const h = createHash('sha256');
  const pasta = join(ROOT, 'tools', 'blender', 'armas');
  for (const nome of readdirSync(pasta).filter((n) => n.endsWith('.py')).sort()) {
    h.update(nome);
    h.update(readFileSync(join(pasta, nome), 'utf8').replace(/\r\n/g, '\n'));
  }
  h.update(JSON.stringify(ficha));
  h.update(JSON.stringify({ id, def }));
  return h.digest('hex');
}

/** Contexto de uma arma realista para o principal.py: ficha validada, pintura de fábrica, orçamento, pastas, hash. */
async function contextoReal(id, { forcar = false } = {}) {
  const { ARMAS_REAIS, orcamentoDaArma, soquetesDaArma } = await import('../src/data/armasReais.js');
  const { validarFicha } = await import('../src/weapons/model/ficha.js');
  const def = ARMAS_REAIS[id];
  if (!def) throw new Error(`${id} não é uma arma realista (tem: ${Object.keys(ARMAS_REAIS).join(', ')})`);
  const ficha = validarFicha(JSON.parse(readFileSync(join(ROOT, 'tools', 'blender', 'refs', `${id}.json`), 'utf8')));
  const ctx = {
    id, raiz: ROOT, ficha, fabrica: def.fabrica, pecas: def.pecas, zonas: def.zonas, soquetes: soquetesDaArma(id),
    orcamento: orcamentoDaArma(id), saida: join(ROOT, def.pasta), conferencia: join(ROOT, 'tools', 'blender', 'conferencia', id),
    hash: hashEntradas(id, def, ficha), forcar,
  };
  mkdirSync(TMP, { recursive: true });
  const arquivo = join(TMP, `${id}-real.json`);
  writeFileSync(arquivo, JSON.stringify(ctx));
  return { arquivo, ctx };
}

/** Uma linha com a silhueta, os triângulos e o tamanho; lança com a lista quando a saída tem problema. */
function resumoSaida(id) {
  const { problemas, relatorio, bytes } = validarSaida(id, ROOT);
  if (problemas.length) throw new Error(`${id}: a saída tem problemas:\n  ${problemas.join('\n  ')}`);
  const s = relatorio.silhueta;
  const t = Object.entries(relatorio.lods).map(([l, d]) => `${l} ${d.triangulos.toLocaleString('pt-BR')}`).join(' · ');
  return `silhueta ${(s.iouTolerancia * 100).toFixed(1)} % (bruto ${(s.iouBruto * 100).toFixed(1)} %) · ${t} triângulos · ${(bytes / 1048576).toFixed(2)} MB`;
}

async function construirReal(id, forcar) {
  const { arquivo, ctx } = await contextoReal(id, { forcar });
  const rel = join(ctx.saida, `${id}.relatorio.json`);
  if (!forcar && existsSync(rel)) {
    const antigo = JSON.parse(readFileSync(rel, 'utf8'));
    if (antigo.entradas?.hash === ctx.hash && !validarSaida(id, ROOT).problemas.length) {
      return `${id}: sem mudança nas entradas — ${resumoSaida(id)}`;
    }
  }
  const t0 = Date.now();
  await rodarComEtapas(['construir', arquivo], SCRIPT_REAIS, id);
  return `${id}: construída em ${((Date.now() - t0) / 1000).toFixed(0)} s — ${resumoSaida(id)}`;
}

async function validarReal(id) {
  const { arquivo } = await contextoReal(id);
  rodarSemJanela(['validar', arquivo], SCRIPT_REAIS);
  return `${id}: validação aprovada — ${resumoSaida(id)}`;
}

async function conferirReal(id) {
  const { arquivo, ctx } = await contextoReal(id);
  const out = rodarSemJanela(['conferir', arquivo], SCRIPT_REAIS);
  const linha = out.split('\n').find((l) => l.startsWith('MASSACRE-CONFERIR '));
  const arquivos = linha ? JSON.parse(linha.slice('MASSACRE-CONFERIR '.length)) : [];
  return `${id}: ${arquivos.length} vistas em ${ctx.conferencia}`;
}

async function abrirReal(id) {
  const blend = join(ROOT, 'tools', 'blender', 'conferencia', id, `${id}.blend`);
  if (!existsSync(blend)) throw new Error(`${id}: rode antes npm run blender -- construir ${id}`);
  const filho = spawn(blenderExe(), [blend], { detached: true, stdio: 'ignore' });
  filho.unref();
  return `Blender aberto com ${blend}`;
}

async function principal() {
  const argv = process.argv.slice(2);
  const forcar = argv.includes('--forcar');
  const [acao, alvo, extra] = argv.filter((a) => a !== '--forcar');
  const { ARMAS } = await import('../src/data/armas/index.js');
  const { ARMAS_REAIS } = await import('../src/data/armasReais.js');
  const real = (id) => Boolean(ARMAS_REAIS[id]);
  if (acao === 'construir' || (acao === 'validar' && alvo && !alvo.endsWith('.js'))) {
    if (!alvo) throw new Error(`uso: npm run blender -- ${acao} <${Object.keys(ARMAS_REAIS).join('|')}|todas>`);
    let falhas = 0;
    for (const id of alvo === 'todas' ? Object.keys(ARMAS_REAIS) : [alvo]) {
      try {
        if (!real(id)) throw new Error(`${id} não é uma arma realista (tem: ${Object.keys(ARMAS_REAIS).join(', ')})`);
        console.log(acao === 'construir' ? await construirReal(id, forcar) : await validarReal(id));
      } catch (err) {
        falhas++;
        console.error(err.message ?? err);
      }
    }
    if (falhas) process.exitCode = 1;
    return;
  }
  // As de massinha que ainda não foram refeitas (a receita da AK fica no disco até a Tarefa 16, mas quem vale é a realista).
  const deMassinha = Object.keys(ARMAS).filter((id) => !real(id));
  const ids = alvo !== 'todas' ? [alvo] : acao === 'conferir' ? [...Object.keys(ARMAS_REAIS), ...deMassinha] : deMassinha;
  const acoes = {
    abrir: (id) => (real(id) ? abrirReal(id) : abrir(id)),
    conferir: (id) => (real(id) ? conferirReal(id) : conferir(id)),
    'ida-volta': idaVolta,
  };
```

e trocar:

```js
    throw new Error('uso: npm run blender -- <abrir|conferir|ida-volta> <arma|todas>, validar <arquivo.js> ou previa <arquivo.js> <saída>');
```

por:

```js
    throw new Error('uso: npm run blender -- <construir|validar|abrir|conferir|ida-volta> <arma|todas> [--forcar], validar <arquivo.js> ou previa <arquivo.js> <saída>');
```

- [ ] **Passo 5: Construir a AK-47**

Run: `cd "/c/Users/T-Gamer/Desktop/game tiro/trabalho-4.1a" && npm run blender -- construir ak47`
Expected: as etapas aparecendo enquanto o Blender trabalha (`  ak47 · modelo alto e de jogo (… s)`, `peças móveis e
soquetes`, `UV e assar o perto (2048 px)`, `mundo: LOD, UV e assar (512 px)`, `longe: LOD`, `validar`, `exportar`) e,
no fim, `ak47: construída em … s — silhueta ≥ 98,0 % (bruto …) · perto ≤ 40 000 · mundo ≤ 6 000 · longe ≤ 1 500
triângulos · ≤ 6,00 MB` (a AK desta execução: construída em 105 a 150 s, silhueta 99,9 % com tolerância
e 98,2 % bruta, perto 27 381 · mundo 5 700 · longe 1 425 triângulos, 5,16 MB). Se reprovar, a lista `MASSACRE-REPROVADO` diz o quê; corrigir na peça, no assar ou no LOD e
construir de novo. Se o único problema for o tamanho dos arquivos com o WebP sem perdas, seguir a decisão **D4**
(baixar a entropia do que foi assado; persistindo, parar e perguntar ao usuário). Rodar de novo sem mudar nada:

Run: `npm run blender -- construir ak47`
Expected: `ak47: sem mudança nas entradas — …` em menos de 2 s.

- [ ] **Passo 6: Teste da saída da AK**

```js file=tests/armaAk47.test.js
// A AK-47 tipo 3 exportada pelo Blender (Fase 4.1a): a saída inteira passa no validador (níveis, peças, zonas, soquetes,
// triângulos, texturas sem perdas, tamanho, relatório aprovado com a silhueta e as medidas) e os números que o jogo usa:
// a boca a +21,69 u da origem (o pino do gatilho), a linha de mira quase horizontal, a janela de ejeção à direita e os
// eixos das peças móveis.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { fileURLToPath } from 'node:url';
import { validarSaida } from '../tools/blender/saida.mjs';

const RAIZ = fileURLToPath(new URL('..', import.meta.url));

test('AK-47 tipo 3: a saída do Blender passa em todas as validações', () => {
  const { problemas, resumo, relatorio, bytes } = validarSaida('ak47', RAIZ);
  assert.deepEqual(problemas, []);
  assert.ok(bytes > 0);
  assert.equal(relatorio.aprovado, true);
  assert.ok(relatorio.silhueta.iouTolerancia >= 0.98);
  for (const d of Object.values(relatorio.medidas)) assert.ok(Math.abs(d.erro) <= 0.01);
  assert.deepEqual(Object.keys(resumo.lods), ['perto', 'mundo', 'longe']);
});

test('AK-47 tipo 3: soquetes e peças móveis no referencial do jogo', () => {
  const { resumo } = validarSaida('ak47', RAIZ);
  const boca = resumo.soquetes.boca.posicao;
  assert.ok(Math.abs(boca[0] - 551 / 25.4) < 0.02, `boca em x = ${boca[0]} u`);
  assert.ok(Math.abs(boca[1]) < 0.01 && Math.abs(boca[2]) < 0.01, 'a boca no eixo do cano');
  const tras = resumo.soquetes.mira_tras.posicao;
  const frente = resumo.soquetes.mira_frente.posicao;
  assert.ok(Math.abs(tras[1] - frente[1]) < 0.05, 'a linha de mira quase horizontal');
  assert.ok(resumo.soquetes.ejecao.posicao[2] > 0.5, 'a janela de ejeção no lado direito (+Z)');
  assert.deepEqual(resumo.lods.perto.pecas.ferrolho.extras, { eixo: [-1, 0, 0] });
  for (const p of ['carregador', 'gatilho', 'cao', 'seletor']) assert.deepEqual(resumo.lods.perto.pecas[p].extras, { eixo_giro: [0, 0, 1] });
});
```

Run: `node --test tests/armaAk47.test.js`
Expected: PASS (2 testes). Suíte inteira: `npm test 2>&1 | tail -8` → `# tests 352`, `# fail 0`.

- [ ] **Passo 7: Conferência e revisão crítica** — `npm run blender -- conferir ak47` (sete vistas em
  `tools/blender/conferencia/ak47/`) e voltar à revisão da Tarefa 6, passo 4, agora com o modelo assado: a render do
  modelo alto e a foto lado a lado; a textura assada conferida canal por canal (Tarefa 7, passo 3). Anotar os defeitos
  achados e corrigidos.

---

### Tarefa 9: `GLTFLoader` e `DRACOLoader` no vendor e os tipos MIME

**Files:**
- Modify: `tools/vendor.mjs`, `tools/dev-server.mjs`
- Create (gerado por `npm run vendor`): `vendor/three/examples/jsm/loaders/GLTFLoader.js`,
  `vendor/three/examples/jsm/loaders/DRACOLoader.js` e o decodificador `vendor/three/examples/jsm/libs/draco/gltf/`
  (`draco_decoder.wasm`, `draco_wasm_wrapper.js` e o `draco_decoder.js` para navegador sem WebAssembly)
- Test: `tests/vendorGltf.test.js`

- [ ] **Passo 1: Teste**

```js file=tests/vendorGltf.test.js
// O vendor tem o GLTFLoader e o DRACOLoader do three fixado, o que eles importam e o decodificador Draco (Fase 4.1a;
// desenho, seções 4.5 e 5.2) — de loaders/, fora os dois, só o que outro arquivo do vendor importa; o servidor de
// desenvolvimento serve .glb, .gltf, .bin e .webp com o tipo certo.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { existsSync, readFileSync, readdirSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const JSM = new URL('../vendor/three/examples/jsm/', import.meta.url);
const IMPORT = /from\s*['"](\.{1,2}\/[^'"]+)['"]/g;

const CARREGADORES = ['GLTFLoader.js', 'DRACOLoader.js'];
const DECODIFICADOR = ['draco_decoder.js', 'draco_decoder.wasm', 'draco_wasm_wrapper.js'];

test('vendor: GLTFLoader, DRACOLoader e o decodificador iguais aos do node_modules; o resto de loaders/ só por import', () => {
  for (const nome of CARREGADORES) {
    const arquivo = new URL(`loaders/${nome}`, JSM);
    assert.ok(existsSync(arquivo), `vendor/three/examples/jsm/loaders/${nome}`);
    const texto = readFileSync(arquivo, 'utf8');
    assert.equal(texto, readFileSync(new URL(`../node_modules/three/examples/jsm/loaders/${nome}`, import.meta.url), 'utf8'));
    for (const m of texto.matchAll(IMPORT)) assert.ok(existsSync(new URL(m[1], arquivo)), `${nome}: import ${m[1]}`);
  }
  for (const nome of DECODIFICADOR) {
    const arquivo = new URL(`libs/draco/gltf/${nome}`, JSM);
    assert.ok(existsSync(arquivo), `vendor/three/examples/jsm/libs/draco/gltf/${nome}`);
    assert.ok(readFileSync(arquivo).equals(readFileSync(new URL(`../node_modules/three/examples/jsm/libs/draco/gltf/${nome}`, import.meta.url))), nome);
  }
  // O fechamento de imports do vendor.mjs já trazia o FontLoader (TextGeometry) e o MD2Loader (MD2Character): fora os
  // dois de propósito, todo arquivo de loaders/ tem quem o importe — nenhum carregador solto.
  const pasta = fileURLToPath(JSM);
  const importados = new Set();
  for (const f of readdirSync(pasta, { recursive: true }).filter((x) => x.endsWith('.js'))) {
    const caminho = join(pasta, f);
    for (const m of readFileSync(caminho, 'utf8').matchAll(IMPORT)) importados.add(resolve(dirname(caminho), m[1]));
  }
  for (const nome of readdirSync(new URL('loaders/', JSM))) {
    if (!CARREGADORES.includes(nome)) assert.ok(importados.has(join(pasta, 'loaders', nome)), `loaders/${nome} sem quem o importe`);
  }
});

test('servidor de desenvolvimento: .glb, .gltf, .bin e .webp com o tipo MIME', () => {
  const texto = readFileSync(new URL('../tools/dev-server.mjs', import.meta.url), 'utf8');
  assert.match(texto, /'\.glb': 'model\/gltf-binary'/);
  assert.match(texto, /'\.gltf': 'model\/gltf\+json'/);
  assert.match(texto, /'\.bin': 'application\/octet-stream'/);
  assert.match(texto, /'\.webp': 'image\/webp'/);
});
```

Run: `node --test tests/vendorGltf.test.js`
Expected: FAIL — `vendor/three/examples/jsm/loaders/GLTFLoader.js` não existe; o MIME `.glb` não está na tabela.

(O `DRACOLoader` busca o decodificador em tempo de execução, sem `import`: por isso os três arquivos de
`libs/draco/gltf/` entram pela lista, não pelo fechamento de imports. O navegador baixa o `draco_wasm_wrapper.js` e o
`draco_decoder.wasm`, cerca de 0,25 MB, uma vez.)

- [ ] **Passo 2: A exceção no vendor** — em `tools/vendor.mjs`, trocar:

```js
// Nada de loaders/tsl/webxr/inspector: o MASSACRE é 100% procedural e roda em WebGL2.
const EXCLUDE_FILES = new Set(['capabilities/WebGPU.js']);
```

por:

```js
// Nada de tsl/webxr/inspector (o jogo roda em WebGL2) e, de loaders/, só o GLTFLoader e o DRACOLoader, com o
// decodificador Draco que o DRACOLoader busca em tempo de execução: as armas e as mãos realistas são o único modelo em
// arquivo do jogo (exceção à regra 4 decidida em 2026-09-26; docs/superpowers/specs/2026-09-26-armas-realistas-design.md,
// seções 4.5 e 5.2). Os imports relativos dos carregadores entram pelo fechamento abaixo.
const EXCLUDE_FILES = new Set(['capabilities/WebGPU.js']);
const THREE_ADDON_FILES = ['loaders/GLTFLoader.js', 'loaders/DRACOLoader.js', 'libs/draco/gltf'];
```

e trocar:

```js
  const extra = await closeImports(addonsSrc, addonsOut);
```

por:

```js
  for (const f of THREE_ADDON_FILES) {
    await mkdir(dirname(join(addonsOut, f)), { recursive: true });
    await cp(join(addonsSrc, f), join(addonsOut, f), { recursive: true });
  }
  const extra = await closeImports(addonsSrc, addonsOut);
```

- [ ] **Passo 3: Os tipos MIME** — em `tools/dev-server.mjs`, trocar:

```js
  '.png': 'image/png',
```

por:

```js
  '.png': 'image/png',
  '.webp': 'image/webp',
  '.glb': 'model/gltf-binary',
  '.gltf': 'model/gltf+json',
  '.bin': 'application/octet-stream',
```

- [ ] **Passo 4: Regenerar o vendor e conferir que só entraram os dois carregadores e o decodificador**

```bash
cd "/c/Users/T-Gamer/Desktop/game tiro/trabalho-4.1a"
npm run vendor
diff -rq vendor ../base-4.1a/vendor
```

Expected: `vendor/ atualizado: { three: '0.186.1', … }` e o `diff` só com
`Only in vendor/three/examples/jsm/loaders: DRACOLoader.js`, `Only in vendor/three/examples/jsm/loaders: GLTFLoader.js`
e `Only in vendor/three/examples/jsm/libs: draco` (os imports do GLTFLoader, `utils/BufferGeometryUtils.js` e
`utils/SkeletonUtils.js`, já estavam no vendor; o `FontLoader.js` e o `MD2Loader.js` de `loaders/` também; o
DRACOLoader só importa o `three`).

Run: `node --test tests/vendorGltf.test.js`
Expected: PASS (2 testes). Suíte inteira: `# tests 354`, `# fail 0`.

---

### Tarefa 10: Material das zonas

**Files:**
- Create: `src/weapons/model/glsl/acabamentos.js`, `src/weapons/model/materialArma.js`
- Test: `tests/materialArma.test.js`

- [ ] **Passo 1: Testes**

```js file=tests/materialArma.test.js
// Material de zona das armas realistas (Fase 4.1a; desenho, seção 5.3): os números do acabamento viram o
// MeshPhysicalMaterial; os recursos só ligam quando o acabamento pede; a chave do programa e os defines separam as
// variantes; as texturas e o ambiente entram; o trecho de shader entra nos pontos certos do shader do three r186.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import * as THREE from 'three';
import { ambienteDoMaterial, criarMaterialZona } from '../src/weapons/model/materialArma.js';

const tex = () => ({ n: new THREE.Texture(), m: new THREE.Texture() });

test('material de zona: oxidado de fábrica', () => {
  const t = tex();
  const m = criarMaterialZona({ zona: 'corpo', def: { acabamento: 'oxidado', cor: '#303135', desgaste: 0.22 }, texturas: t });
  assert.ok(m.isMeshPhysicalMaterial);
  assert.equal(m.metalness, 1);
  assert.equal(m.roughness, 0.34);
  assert.equal(m.clearcoat, 0);
  assert.equal(m.iridescence, 0);
  assert.equal(m.anisotropy, 0);
  assert.equal(m.normalMap, t.n);
  assert.equal(m.aoMap, t.m);
  assert.deepEqual(m.normalScale.toArray(), [1, 1]);
  assert.equal(m.defines.ARMA_PADRAO, 1);
  assert.equal(m.defines.ARMA_ESCOVADO, undefined);
  assert.equal(m.userData.uniforms.desgaste.value, 0.22);
  assert.equal(m.userData.uniforms.mapaM.value, t.m);
  assert.equal(m.customProgramCacheKey(), 'arma:fino:');
  assert.equal(m.userData.zona, 'corpo');
  assert.equal(m.userData.shared, true);
  assert.ok(Math.abs(m.color.r - 0.02956) < 0.0005, 'a cor em linear');
});

test('material de zona: recursos do material físico só quando o acabamento pede', () => {
  const pe = criarMaterialZona({ zona: 'corpo', def: { acabamento: 'perolado', cor: 'rosa' }, texturas: tex() });
  assert.equal(pe.clearcoat, 1);
  assert.equal(pe.iridescence, 0.8);
  assert.deepEqual(pe.iridescenceThicknessRange, [250, 600]);
  assert.equal(pe.customProgramCacheKey(), 'arma:nenhum:verniz+iridescencia');
  const es = criarMaterialZona({ zona: 'interno', def: { acabamento: 'escovado', cor: '#ADADAF' }, texturas: tex() });
  assert.equal(es.anisotropy, 0.8);
  assert.equal(es.defines.ARMA_ESCOVADO, '');
  const md = criarMaterialZona({ zona: 'guarnicao', def: { acabamento: 'madeira', cor: '#A4673F', cor2: '#794224' }, texturas: tex() });
  assert.equal(md.defines.ARMA_PADRAO, 5);
  assert.ok(md.userData.uniforms.corDois.value.r < md.color.r, 'o veio mais escuro que a madeira');
});

test('material de zona: o trecho de shader entra nos pontos do shader do three', () => {
  const m = criarMaterialZona({ zona: 'corpo', def: { acabamento: 'escovado', cor: '#ADADAF', desgaste: 0.3 }, texturas: tex() });
  const shader = { uniforms: {}, vertexShader: THREE.ShaderLib.physical.vertexShader, fragmentShader: THREE.ShaderLib.physical.fragmentShader };
  m.onBeforeCompile(shader);
  for (const k of ['mapaM', 'corDois', 'corGasto', 'metalGasto', 'asperezaGasto', 'desgaste', 'varAspereza', 'varCor']) {
    assert.ok(shader.uniforms[k], `uniform ${k}`);
  }
  assert.match(shader.vertexShader, /vPosArma = position;/);
  assert.match(shader.fragmentShader, /vec4 armaM = texture2D\( mapaM, vAoMapUv \);/);
  assert.match(shader.fragmentShader, /roughnessFactor = mix\( roughnessFactor, asperezaGasto, armaGasto \);/);
  assert.match(shader.fragmentShader, /metalnessFactor = mix\( metalnessFactor, metalGasto, armaGasto \);/);
  assert.match(shader.fragmentShader, /material\.anisotropyT = /);
  const ambiente = new THREE.Texture();
  const versao = m.version;
  ambienteDoMaterial(m, ambiente, 0.8);
  assert.equal(m.envMap, ambiente);
  assert.equal(m.envMapIntensity, 0.8);
  assert.ok(m.version > versao, 'a variante com o ambiente compila de novo');
});
```

Run: `node --test tests/materialArma.test.js`
Expected: FAIL — `Cannot find module '.../src/weapons/model/materialArma.js'`.

- [ ] **Passo 2: O trecho de shader**

```js file=src/weapons/model/glsl/acabamentos.js
// Trecho de shader das zonas das armas realistas (Fase 4.1a; desenho em docs/superpowers/specs/2026-09-26-armas-
// realistas-design.md, seção 5.3), injetado no MeshPhysicalMaterial por src/weapons/model/materialArma.js. Lê a textura
// _m (R sombra de contato — já pelo aoMap —, G variação de aspereza, B borda, A variação de cor), desenha o padrão
// procedural do acabamento em projeção triplanar no referencial da peça (u) e aplica o desgaste pela borda: a cor, o
// metal e a aspereza do que está por baixo (gasto). No aço escovado, a anisotropia segue o eixo X da arma (e não as UV,
// que o UV automático gira por ilha): as ranhuras correm ao longo de X, então a aspereza maior (T) fica atravessada.
// O padrão fino some pelo filtro de frequência (fwidth) quando fica menor que o pixel, para não cintilar com o balanço
// da arma. Nenhum boil, nenhuma digital de massinha. ARMA_PADRAO segue a ordem de PADROES (src/data/acabamentos.js).

export const ARMA_VERTEX_PARS = /* glsl */ `
varying vec3 vPosArma;
varying vec3 vNormalArma;
varying vec3 vEixoXVista;
`;

export const ARMA_VERTEX = /* glsl */ `
vPosArma = position;
vNormalArma = normal;
vEixoXVista = normalize( ( modelViewMatrix * vec4( 1.0, 0.0, 0.0, 0.0 ) ).xyz );
`;

export const ARMA_FRAGMENT_PARS = /* glsl */ `
uniform sampler2D mapaM;
uniform vec3 corDois;
uniform vec3 corGasto;
uniform float metalGasto;
uniform float asperezaGasto;
uniform float desgaste;
uniform float varAspereza;
uniform float varCor;
varying vec3 vPosArma;
varying vec3 vNormalArma;
varying vec3 vEixoXVista;

float armaHash( vec3 p ) {
  p = fract( p * 0.3183099 + 0.1 );
  p *= 17.0;
  return fract( p.x * p.y * p.z * ( p.x + p.y + p.z ) );
}
float armaRuido( vec3 x ) {
  vec3 i = floor( x );
  vec3 f = fract( x );
  f = f * f * ( 3.0 - 2.0 * f );
  return mix(
    mix( mix( armaHash( i ), armaHash( i + vec3( 1.0, 0.0, 0.0 ) ), f.x ), mix( armaHash( i + vec3( 0.0, 1.0, 0.0 ) ), armaHash( i + vec3( 1.0, 1.0, 0.0 ) ), f.x ), f.y ),
    mix( mix( armaHash( i + vec3( 0.0, 0.0, 1.0 ) ), armaHash( i + vec3( 1.0, 0.0, 1.0 ) ), f.x ), mix( armaHash( i + vec3( 0.0, 1.0, 1.0 ) ), armaHash( i + vec3( 1.0, 1.0, 1.0 ) ), f.x ), f.y ),
    f.z );
}
// Sarja 2×2 de fibra de carbono num plano: 1 no fio de cima, com o sombreado da curva do fio.
float armaTrama( vec2 p ) {
  vec2 c = floor( p );
  float sobe = mod( c.x + c.y, 4.0 ) < 2.0 ? 1.0 : 0.0;
  vec2 f = fract( p );
  float fio = sobe > 0.5 ? sin( f.y * 3.14159265 ) : sin( f.x * 3.14159265 );
  return mix( 0.25, 1.0, sobe ) * ( 0.6 + 0.4 * fio );
}
vec3 armaPesos( vec3 n ) {
  vec3 w = pow( abs( normalize( n ) ), vec3( 4.0 ) );
  return w / ( w.x + w.y + w.z );
}
// Filtro de frequência: 1 enquanto a coordenada do padrão anda menos que 1/4 de período por pixel, 0 a partir de 3/4.
// Detalhe menor que o pixel cintilaria com o balanço da arma; no lugar dele fica a média do padrão.
float armaFiltro( vec3 q ) {
  return 1.0 - smoothstep( 0.25, 0.75, length( fwidth( q ) ) );
}
float armaFiltro1( float q ) {
  return 1.0 - smoothstep( 0.25, 0.75, fwidth( q ) );
}
// Padrão do acabamento no ponto (u, referencial da peça), com a variação de cor assada (_m.a): x = mistura para a
// segunda cor (veio, trama), y = soma na aspereza.
vec2 armaPadrao( vec3 p, vec3 n, float varAssada ) {
  vec3 w = armaPesos( n );
  #if ARMA_PADRAO == 1
    vec3 q = p * 60.0;
    return vec2( 0.0, ( armaRuido( q ) - 0.5 ) * 0.08 * armaFiltro( q ) );
  #elif ARMA_PADRAO == 2
    vec3 q = p * 160.0;
    return vec2( 0.0, ( armaRuido( q ) - 0.5 ) * 0.2 * armaFiltro( q ) );
  #elif ARMA_PADRAO == 3
    vec3 q = p * 420.0;
    return vec2( 0.0, mix( -0.015, -0.25 * step( 0.94, armaHash( floor( q ) ) ), armaFiltro( q ) ) );
  #elif ARMA_PADRAO == 4
    float t = armaTrama( p.yz * 8.5 ) * w.x + armaTrama( p.xz * 8.5 ) * w.y + armaTrama( p.xy * 8.5 ) * w.z;
    t = mix( 0.54, t, armaFiltro( p * 17.0 ) );
    return vec2( t, ( 1.0 - t ) * 0.12 );
  #elif ARMA_PADRAO == 5
    // Veio da madeira: o desenho vem do assar — o veio do material de fábrica do Blender, no canal A da _m, com os anéis
    // ao longo do comprimento como na peça real —, na segunda cor onde o canal cai; por cima, a fibra fina ao longo de X,
    // que some pelo filtro quando fica menor que o pixel. (Anéis procedurais em volta do eixo da peça viravam arcos
    // grandes de desenho animado na coronha, o mesmo defeito que a madeira do Blender teve na revisão da 4.1a.)
    float veio = smoothstep( 0.5, 0.36, varAssada );
    float fibra = ( armaRuido( p * vec3( 0.8, 40.0, 40.0 ) ) - 0.5 ) * armaFiltro1( p.y * 40.0 + p.z * 40.0 );
    veio = clamp( veio * 0.85 + fibra * 0.3, 0.0, 1.0 );
    return vec2( veio, veio * 0.08 );
  #elif ARMA_PADRAO == 6
    vec3 q = p * 90.0;
    return vec2( 0.0, mix( 0.07, smoothstep( 0.45, 0.75, armaRuido( q ) ) * 0.22, armaFiltro( q ) ) );
  #elif ARMA_PADRAO == 7
    vec3 a = p * 70.0;
    vec3 b = p * 190.0;
    return vec2( 0.0, ( ( armaRuido( a ) - 0.5 ) * armaFiltro( a ) + ( armaRuido( b ) - 0.5 ) * armaFiltro( b ) ) * 0.08 );
  #else
    return vec2( 0.0 );
  #endif
}
`;

export const ARMA_COR = /* glsl */ `
vec4 armaM = texture2D( mapaM, vAoMapUv );
vec2 armaPad = armaPadrao( vPosArma, vNormalArma, armaM.a );
diffuseColor.rgb = mix( diffuseColor.rgb, corDois, clamp( armaPad.x, 0.0, 1.0 ) );
diffuseColor.rgb *= 1.0 + ( armaM.a - 0.5 ) * 2.0 * varCor;
float armaGasto = desgaste > 0.0 ? smoothstep( 1.0 - desgaste, 1.0 - desgaste + 0.15, armaM.b ) : 0.0;
diffuseColor.rgb = mix( diffuseColor.rgb, corGasto, armaGasto );
`;

export const ARMA_ASPEREZA = /* glsl */ `
roughnessFactor = clamp( roughnessFactor + ( armaM.g - 0.5 ) * 2.0 * varAspereza + armaPad.y, 0.03, 1.0 );
roughnessFactor = mix( roughnessFactor, asperezaGasto, armaGasto );
`;

export const ARMA_METAL = /* glsl */ `
metalnessFactor = mix( metalnessFactor, metalGasto, armaGasto );
`;

export const ARMA_ANISOTROPIA = /* glsl */ `
#ifdef ARMA_ESCOVADO
  vec3 armaX = vEixoXVista - dot( vEixoXVista, normal ) * normal;
  if ( dot( armaX, armaX ) > 1e-6 ) {
    armaX = normalize( armaX );
    material.anisotropyT = normalize( cross( normal, armaX ) );
    material.anisotropyB = armaX;
  }
#endif
`;
```

- [ ] **Passo 3: O material**

```js file=src/weapons/model/materialArma.js
// Material de uma zona das armas realistas (Fase 4.1a; desenho em docs/superpowers/specs/2026-09-26-armas-realistas-
// design.md, seção 5.3; plano da 4.1a, D3): MeshPhysicalMaterial com a normal assada (_n, espaço tangente com as
// tangentes do .glb, normalScale 1), a sombra de contato (_m.r pelo aoMap), o reflexo do set (envMap; sem ele, o
// ambiente da cena) e o trecho de shader do acabamento (glsl/acabamentos.js): padrão procedural, variações assadas,
// desgaste pela borda, anisotropia no eixo da arma. Os números vêm da função pura acabamentoParaMaterial. Os recursos do
// material físico (verniz, iridescência, anisotropia) só ligam quando o acabamento pede: cada combinação é uma variante
// de shader, e a chave do programa diz qual (defines + customProgramCacheKey), para a compilação no carregamento
// (renderer.compileAsync, no viewmodel e na bancada) cobrir todas.

import * as THREE from 'three';
import { acabamentoParaMaterial } from '../skins/acabamento.js';
import {
  ARMA_ANISOTROPIA, ARMA_ASPEREZA, ARMA_COR, ARMA_FRAGMENT_PARS, ARMA_METAL, ARMA_VERTEX, ARMA_VERTEX_PARS,
} from './glsl/acabamentos.js';

const linear = (c) => new THREE.Color().setRGB(c[0], c[1], c[2], THREE.LinearSRGBColorSpace);

/**
 * @param {{zona:string, def:{acabamento:string, cor:string, cor2?:string|null, desgaste?:number},
 *   texturas:{n:THREE.Texture, m:THREE.Texture}, ambiente?:THREE.Texture|null, intensidade?:number, nome?:string}} o
 *   `ambiente` = o reflexo do set (null: o ambiente da cena); `intensidade` = a dele no material
 * @returns {THREE.MeshPhysicalMaterial} marcado `userData.shared` (quem cria descarta)
 */
export function criarMaterialZona({ zona, def, texturas, ambiente = null, intensidade = 1, nome = `arma:${zona}` }) {
  const p = acabamentoParaMaterial(def);
  const m = new THREE.MeshPhysicalMaterial({
    name: nome,
    color: linear(p.color),
    metalness: p.metalness,
    roughness: p.roughness,
    normalMap: texturas.n,
    normalScale: new THREE.Vector2(1, 1),
    aoMap: texturas.m,
    aoMapIntensity: 1,
    envMap: ambiente,
    envMapIntensity: intensidade,
    clearcoat: p.clearcoat,
    clearcoatRoughness: p.clearcoatRoughness,
    iridescence: p.iridescence,
    iridescenceIOR: p.iridescenceIOR,
    iridescenceThicknessRange: p.iridescenceThicknessRange,
    anisotropy: p.anisotropy,
  });
  m.userData.zona = zona;
  m.userData.acabamento = p.acabamento;
  m.userData.shared = true;
  m.defines = { ARMA_PADRAO: p.padraoId };
  if (p.anisotropy > 0) m.defines.ARMA_ESCOVADO = '';
  const u = {
    mapaM: { value: texturas.m },
    corDois: { value: linear(p.color2 ?? p.color) },
    corGasto: { value: linear(p.gasto.color) },
    metalGasto: { value: p.gasto.metalness },
    asperezaGasto: { value: p.gasto.roughness },
    desgaste: { value: p.desgaste },
    varAspereza: { value: p.varAspereza },
    varCor: { value: p.varCor },
  };
  m.userData.uniforms = u;
  m.onBeforeCompile = (shader) => {
    Object.assign(shader.uniforms, u);
    shader.vertexShader = shader.vertexShader
      .replace('#include <common>', `#include <common>\n${ARMA_VERTEX_PARS}`)
      .replace('#include <begin_vertex>', `#include <begin_vertex>\n${ARMA_VERTEX}`);
    shader.fragmentShader = shader.fragmentShader
      .replace('#include <common>', `#include <common>\n${ARMA_FRAGMENT_PARS}`)
      .replace('#include <color_fragment>', `#include <color_fragment>\n${ARMA_COR}`)
      .replace('#include <roughnessmap_fragment>', `#include <roughnessmap_fragment>\n${ARMA_ASPEREZA}`)
      .replace('#include <metalnessmap_fragment>', `#include <metalnessmap_fragment>\n${ARMA_METAL}`)
      .replace('#include <lights_physical_fragment>', `#include <lights_physical_fragment>\n${ARMA_ANISOTROPIA}`);
  };
  m.customProgramCacheKey = () => `arma:${p.padrao}:${p.recursos.join('+')}`;
  return m;
}

/** Troca o ambiente (o reflexo do set, ou null para o da cena) de um material de zona. */
export function ambienteDoMaterial(m, textura, intensidade = 1) {
  m.envMap = textura;
  m.envMapIntensity = intensidade;
  m.needsUpdate = true;
}
```

- [ ] **Passo 4: Rodar e ver passar**

Run: `node --test tests/materialArma.test.js`
Expected: PASS (3 testes). Suíte inteira: `# tests 357`, `# fail 0`.

---

### Tarefa 11: Serviço `weaponModels` com duas origens

**Files:**
- Create: `src/weapons/model/glbWeapon.js`, `src/weapons/model/glbSource.js`
- Modify (substituir inteiro): `src/weapons/model/weaponLibrary.js`
- Modify: `src/core/events.js`, `src/main.js`
- Test: `tests/weaponLibraryGlb.test.js`

A interface da 4.1 continua (`has`, `ids`, `meshes`, `preload`, `instance`, `report`, `reload`, `dispose`); `recipe(id)`
dá lugar a `describe(id)` (assíncrono, carrega o que falta) e `info(id)` (síncrono, o que já está carregado), no mesmo
formato para as duas origens:

```js
// info(id) — as duas origens (massinha até a 4.1d; glb daqui em diante)
{
  id: 'ak47', source: 'glb' | 'massinha', category: 'rifle',
  bounds: { min: [x, y, z], max: [x, y, z] },   // u, referencial da arma (+X boca, +Y cima, +Z direita)
  radius: 17.9,                                  // meia diagonal da caixa
  anchors: { boca: {pos, rot}, maoDireita: {pos, rot, pose}, maoEsquerda: {…}, ejecao: {…}, … },  // formato da 4.1
  sockets: { boca: {pos, rot}, mao_d: {…}, … } | null,   // só glb
  hands: false | true,                           // glb na 4.1a: sem mãos (D7)
  plan: { weapon, lengthU, points, holes, source } | null, // formato 1 (u, relativo à boca)
  lengthU: 34.25, parts: ['ferrolho', …], zones: ['corpo', …] | null, lods: ['perto', 'mundo', 'longe'],
  report: {…} | null, ficha: {…} | null, iou: 0.99 | null, recipe: {…} | null,
}
```

- [ ] **Passo 1: Testes com carregadores falsos**

```js file=tests/weaponLibraryGlb.test.js
// Serviço weaponModels com a origem glb (Fase 4.1a; desenho, seção 5.2), com carregadores falsos (uma cena montada no
// teste no lugar do GLTFLoader, texturas vazias, a ficha real e um relatório): info no formato da 4.1, instância com as
// peças móveis e as âncoras, geometrias e materiais divididos, cada coisa carregada uma vez, skin trocando os materiais
// (evento `skin`), ambiente em todos os materiais, recarga com os eventos e o descarte de tudo; a origem de massinha
// continua respondendo.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import * as THREE from 'three';
import { EV, EventBus } from '../src/core/events.js';
import { ARMAS_REAIS, LODS_REAIS, ZONAS } from '../src/data/armasReais.js';
import { WeaponLibrary } from '../src/weapons/model/weaponLibrary.js';
import { skinPorNome } from '../src/weapons/skins/skin.js';

const FICHA = JSON.parse(readFileSync(new URL('../tools/blender/refs/ak47.json', import.meta.url), 'utf8'));
const ZONA_DA_PECA = { base: 'corpo', ferrolho: 'interno', carregador: 'carregador', gatilho: 'detalhes', cao: 'interno', seletor: 'detalhes' };

function cenaFalsa() {
  const cena = new THREE.Group();
  const raiz = new THREE.Group();
  raiz.name = 'ak47';
  cena.add(raiz);
  for (const lod of LODS_REAIS) {
    const no = new THREE.Group();
    no.name = lod;
    raiz.add(no);
    for (const peca of ['base', ...ARMAS_REAIS.ak47.pecas]) {
      const m = new THREE.Mesh(new THREE.BoxGeometry(peca === 'base' ? 34 : 2, 2, 2), new THREE.MeshStandardMaterial({ name: ZONA_DA_PECA[peca] }));
      m.name = `${lod}_${peca}`;
      if (peca === 'ferrolho') {
        m.position.set(5.9, 0.5, 0);
        m.userData.eixo = [-1, 0, 0];
      }
      no.add(m);
    }
    // A base tem mais zonas: uma segunda malha filha com a guarnição.
    const g = new THREE.Mesh(new THREE.BoxGeometry(8, 3, 1.6), new THREE.MeshStandardMaterial({ name: 'guarnicao' }));
    g.position.set(-10, -1, 0);
    no.getObjectByName(`${lod}_base`).add(g);
  }
  const soq = new THREE.Group();
  soq.name = 'soquetes';
  raiz.add(soq);
  for (const [nome, x] of [['boca', 21.69], ['ejecao', 4.4], ['carregador', 3.7], ['mira_tras', 6.1], ['mira_frente', 20.7], ['mao_d', -2.2], ['mao_e', 10.3]]) {
    const s = new THREE.Object3D();
    s.name = `soquete_${nome}`;
    s.position.set(x, 0, nome === 'ejecao' ? 0.63 : 0);
    soq.add(s);
  }
  return cena;
}

function carregadoresFalsos() {
  const conta = { glb: 0, textura: 0, json: 0, urls: [] };
  return {
    conta,
    carregadores: {
      async glb(url) {
        conta.glb++;
        conta.urls.push(url);
        return { scene: cenaFalsa() };
      },
      async textura(url) {
        conta.textura++;
        conta.urls.push(url);
        const t = new THREE.Texture();
        t.name = url;
        return t;
      },
      async json(url) {
        conta.json++;
        if (url.includes('relatorio')) return { arma: 'ak47', silhueta: { iouTolerancia: 0.991, iouBruto: 0.96 } };
        if (url.includes('refs/ak47.json')) return structuredClone(FICHA);
        throw new Error(`sem ${url}`);
      },
    },
  };
}

const nova = (extra = {}) => {
  const f = carregadoresFalsos();
  const events = new EventBus();
  const lib = new WeaponLibrary({ sdf: null, events, carregadores: f.carregadores, ...extra });
  return { lib, events, conta: f.conta };
};

test('weaponModels: as duas origens, os níveis de cada uma e o info da AK no formato da 4.1', async () => {
  const { lib, conta } = nova();
  assert.equal(lib.source('ak47'), 'glb');
  assert.equal(lib.source('glock'), 'massinha');
  assert.equal(lib.source('usps'), null);
  assert.ok(lib.ids.includes('ak47') && lib.ids.includes('glock'));
  assert.equal(lib.ids.filter((id) => id === 'ak47').length, 1, 'a realista vale sobre a receita de massinha do mesmo id');
  assert.deepEqual(lib.lods('ak47'), ['perto', 'mundo', 'longe']);
  assert.deepEqual(lib.lods('glock'), ['perto', 'mundo']);
  assert.equal(lib.info('ak47'), null, 'antes de carregar');
  const info = await lib.describe('ak47');
  assert.equal(info.source, 'glb');
  assert.equal(info.category, 'rifle');
  assert.equal(info.hands, false);
  assert.deepEqual(info.parts, ['ferrolho', 'carregador', 'gatilho', 'cao', 'seletor']);
  assert.deepEqual(info.anchors.boca.pos, [21.69, 0, 0]);
  assert.equal(info.anchors.maoDireita.pose, null);
  assert.ok(info.anchors.maoEsquerda && info.anchors.ejecao);
  assert.ok(Math.abs(info.plan.lengthU - 870 / 25.4) < 1e-9);
  assert.equal(info.iou, 0.991);
  assert.ok(info.bounds.max[0] > info.bounds.min[0]);
  assert.equal(lib.info('ak47'), info);
  const glock = lib.info('glock');
  assert.equal(glock.source, 'massinha');
  assert.equal(glock.hands, true);
  assert.ok(glock.recipe && glock.anchors.maoDireita);
  const buscas = conta.json;
  assert.equal((await lib.describe('knife')).plan, null, 'a faca não tem planta');
  assert.equal(conta.json, buscas, 'e nada é buscado para ela (sem 404 no console)');
  await assert.rejects(lib.describe('glock'), /sem .*tools\/blender\/refs\/glock\.json/, 'a planta que a receita aponta, e a falha aparece');
});

test('weaponModels: instância glb com as peças móveis, as âncoras, os materiais de zona e tudo dividido', async () => {
  const { lib, conta } = nova();
  const a = await lib.instance('ak47', { lod: 'perto' });
  const b = await lib.instance('ak47', { lod: 'perto' });
  const w = a.userData.weapon;
  assert.equal(w.id, 'ak47');
  assert.equal(w.source, 'glb');
  assert.deepEqual(Object.keys(w.parts).sort(), ['cao', 'carregador', 'ferrolho', 'gatilho', 'seletor']);
  assert.deepEqual(w.parts.ferrolho.userData.rest, [5.9, 0.5, 0]);
  assert.ok(w.anchors.boca.isObject3D && w.anchors.maoDireita.isObject3D);
  const malhas = (inst) => {
    const out = [];
    inst.traverse((o) => o.isMesh && out.push(o));
    return out;
  };
  const ma = malhas(a);
  const mb = malhas(b);
  assert.equal(ma.length, mb.length);
  ma.forEach((m, i) => {
    assert.ok(m.material.isMeshPhysicalMaterial);
    assert.equal(m.material.userData.zona, m.userData.zona);
    assert.equal(m.geometry, mb[i].geometry, 'geometria dividida');
    assert.equal(m.material, mb[i].material, 'material dividido');
    assert.equal(m.geometry.userData.shared, true);
  });
  assert.equal(conta.glb, 1, 'o .glb carregado uma vez');
  assert.equal(conta.textura, 2, 'o conjunto perto: _n e _m');
  await lib.instance('ak47', { lod: 'mundo' });
  assert.equal(conta.textura, 4, 'o conjunto mundo: _mundo_n e _mundo_m');
  await lib.instance('ak47', { lod: 'longe' });
  assert.equal(conta.textura, 4, 'o longe usa o conjunto do mundo');
  assert.ok(conta.urls.some((u) => u.endsWith('assets/armas/ak47/ak47_mundo_m.webp')));
  await assert.rejects(lib.instance('ak47', { lod: 'medio' }), /nível de detalhe desconhecido/);
});

test('weaponModels: skin e ambiente', async () => {
  const { lib, events } = nova();
  const fab = await lib.instance('ak47');
  const matFab = fab.getObjectByName('perto_base').material;
  assert.equal(lib.skinOf('ak47').chave, 'fabrica');
  const ouvidos = [];
  events.on(EV.WEAPON_MODEL, (e) => ouvidos.push(e));
  lib.setSkin('ak47', skinPorNome('ak47', 'Cromo e Carbono'));
  assert.deepEqual(ouvidos, [{ id: 'ak47', phase: 'skin' }]);
  const cc = await lib.instance('ak47');
  const matCc = cc.getObjectByName('perto_base').material;
  assert.notEqual(matCc, matFab);
  assert.equal(matCc.userData.acabamento, 'cromado');
  assert.throws(() => lib.setSkin('glock', skinPorNome('ak47', 'fabrica')), /skins de acabamento só nas armas realistas/);
  const env = new THREE.Texture();
  lib.setEnvironment(env, 0.9);
  assert.equal(matFab.envMap, env);
  assert.equal(matCc.envMap, env);
  assert.equal(matCc.envMapIntensity, 0.9);
  const depois = await lib.instance('ak47', { lod: 'mundo' });
  const matMundo = depois.getObjectByName('mundo_base').material;
  assert.equal(matMundo.envMap, env, 'material novo já nasce com o ambiente');
  assert.equal(matMundo.envMapIntensity, 0.9);
  assert.equal(matFab.normalMap.anisotropy, 8, 'a anisotropia de partida');
  const versao = matFab.normalMap.version;
  lib.setAnisotropy(4);
  assert.equal(matFab.normalMap.anisotropy, 4);
  assert.equal(matMundo.aoMap.anisotropy, 4);
  assert.ok(matFab.normalMap.version > versao, 'a textura sobe de novo com a anisotropia nova');
});

test('weaponModels: recarga (relendo → pronta, ?v= novo, o velho descartado) e o descarte de tudo', async () => {
  const { lib, events, conta } = nova();
  const velha = await lib.instance('ak47');
  const geo = velha.getObjectByName('perto_base').geometry;
  let geoDescartada = false;
  geo.addEventListener('dispose', () => {
    geoDescartada = true;
  });
  const fases = [];
  events.on(EV.WEAPON_MODEL, (e) => fases.push(e.phase));
  await lib.reload('ak47', 'perto');
  assert.deepEqual(fases, ['relendo', 'pronta']);
  assert.ok(geoDescartada, 'a geometria velha saiu');
  assert.equal(conta.glb, 2);
  assert.match(conta.urls.filter((u) => u.includes('ak47.glb')).at(-1), /\?v=\d+/);
  const nova_ = await lib.instance('ak47');
  const mats = new Set();
  nova_.traverse((o) => o.isMesh && mats.add(o.material));
  let descartados = 0;
  for (const m of mats) m.addEventListener('dispose', () => descartados++);
  lib.dispose();
  assert.equal(descartados, mats.size, 'os materiais de zona saíram no dispose');
  await assert.rejects(lib.instance('ak47'), /descartada/);
});

test('weaponModels: o relatório do console tem as duas origens', async () => {
  const { lib } = nova();
  await lib.describe('ak47');
  const linhas = lib.report();
  const ak = linhas.filter((r) => r.id === 'ak47');
  assert.deepEqual(ak.map((r) => r.lod), ['perto', 'mundo', 'longe']);
  assert.ok(ak.every((r) => r.source === 'glb' && r.state === 'pronta' && r.triangles > 0));
  assert.ok(linhas.some((r) => r.id === 'glock' && r.source === 'massinha'));
  assert.equal(ZONAS.length, 5);
});
```

Run: `node --test tests/weaponLibraryGlb.test.js`
Expected: FAIL — `Cannot find module '.../src/weapons/model/glbSource.js'` (importado pelo `weaponLibrary.js` novo, que
ainda não existe) ou os métodos novos ausentes.

- [ ] **Passo 2: O `.glb` no jogo**

```js file=src/weapons/model/glbWeapon.js
// O .glb de uma arma realista no jogo (Fase 4.1a; desenho em docs/superpowers/specs/2026-09-26-armas-realistas-design.md,
// seções 4.2 e 5.2; plano da 4.1a, D2): o resumo da cena que o GLTFLoader devolve — por nível (perto, mundo, longe) as
// peças `<nivel>_<peca>` com as malhas (a zona de cada uma pelo nome do material), os triângulos e a caixa; os
// soquetes; o ponto de descanso e os extras das peças móveis — e a montagem de uma instância: um clone do nível
// (geometrias divididas) com o material de cada zona, as peças móveis com o descanso e o eixo, e as âncoras da 4.1
// (boca, mãos, ejeção…) tiradas dos soquetes, no formato que o viewmodel e a bancada já usam.

import * as THREE from 'three';
import { ANCORA_DO_SOQUETE, LODS_REAIS } from '../../data/armasReais.js';

const _e = new THREE.Euler();

/**
 * Resumo da cena do .glb. Marca as geometrias como compartilhadas e guarda a zona de cada malha em userData.zona (o
 * material do GLTFLoader é trocado logo depois).
 * @param {THREE.Object3D} cena gltf.scene
 * @param {string} id
 */
export function resumirGlb(cena, id) {
  const raiz = cena.getObjectByName(id);
  if (!raiz) throw new Error(`o .glb não tem a raiz ${id}`);
  raiz.updateMatrixWorld(true);
  const lods = {};
  const zonas = new Set();
  for (const lod of LODS_REAIS) {
    const no = raiz.children.find((c) => c.name === lod);
    if (!no) throw new Error(`o .glb de ${id} não tem o nível ${lod}`);
    const pecas = {};
    let triangulos = 0;
    for (const peca of no.children) {
      if (!peca.name.startsWith(`${lod}_`)) throw new Error(`peça ${peca.name} fora do padrão ${lod}_<peça>`);
      pecas[peca.name.slice(lod.length + 1)] = peca;
      peca.userData.rest = peca.position.toArray();
      peca.traverse((o) => {
        if (!o.isMesh) return;
        o.userData.zona = o.userData.zona ?? o.material?.name ?? null;
        if (o.userData.zona) zonas.add(o.userData.zona);
        o.geometry.userData.shared = true;
        triangulos += (o.geometry.index ? o.geometry.index.count : o.geometry.attributes.position.count) / 3;
      });
    }
    lods[lod] = { no, pecas, triangulos };
  }
  const soquetes = {};
  const pasta = raiz.children.find((c) => c.name === 'soquetes');
  for (const s of pasta?.children ?? []) {
    if (!s.name.startsWith('soquete_')) continue;
    _e.setFromQuaternion(s.quaternion, 'XYZ');
    soquetes[s.name.slice('soquete_'.length)] = { pos: s.position.toArray(), rot: [_e.x, _e.y, _e.z] };
  }
  const caixa = new THREE.Box3().setFromObject(lods.perto.no);
  caixa.applyMatrix4(new THREE.Matrix4().copy(raiz.matrixWorld).invert());
  return { raiz, lods, soquetes, caixa: { min: caixa.min.toArray(), max: caixa.max.toArray() }, zonas: [...zonas] };
}

/** Âncoras no formato da 4.1 ({pos, rot}; as das mãos com `pose: null` até as poses da 4.1b) a partir dos soquetes. */
export function ancorasDosSoquetes(soquetes) {
  const out = {};
  for (const [nome, s] of Object.entries(soquetes)) {
    const mao = ANCORA_DO_SOQUETE[nome];
    out[mao ?? nome] = { pos: [...s.pos], rot: [...s.rot], ...(mao ? { pose: null } : {}) };
  }
  return out;
}

/**
 * Instância de um nível: clone da hierarquia (geometrias divididas), cada malha com o material da sua zona.
 * userData.weapon = {id, lod, faction: null, source: 'glb', radius, parts: {peça móvel: Object3D}, anchors}.
 * @param {object} resumo resumirGlb()
 * @param {Object<string, THREE.Material>} materiais por zona
 * @param {Object<string, {pos:number[], rot:number[]}>} ancoras
 */
export function montarInstanciaGlb(resumo, id, lod, materiais, ancoras, raio) {
  const base = resumo.lods[lod];
  const root = new THREE.Group();
  root.name = `arma:${id}`;
  const parts = {};
  for (const [nome, peca] of Object.entries(base.pecas)) {
    const c = peca.clone(true);
    c.userData.rest = [...peca.userData.rest];
    c.userData.axis = peca.userData.eixo ?? null;
    c.userData.hinge = peca.userData.eixo_giro ?? null;
    c.traverse((o) => {
      if (!o.isMesh) return;
      const m = materiais[o.userData.zona];
      if (!m) throw new Error(`${id}: sem material para a zona ${o.userData.zona}`);
      o.material = m;
      o.castShadow = true;
      o.receiveShadow = true;
    });
    root.add(c);
    if (nome !== 'base') parts[nome] = c;
  }
  const anchors = {};
  for (const [nome, a] of Object.entries(ancoras)) {
    const o = new THREE.Object3D();
    o.name = `ancora:${nome}`;
    o.position.fromArray(a.pos);
    o.rotation.fromArray(a.rot);
    root.add(o);
    anchors[nome] = o;
  }
  root.userData.weapon = { id, lod, faction: null, source: 'glb', radius: raio, parts, anchors };
  return root;
}
```

- [ ] **Passo 3: A origem `glb`**

```js file=src/weapons/model/glbSource.js
// Origem `glb` do serviço weaponModels (Fase 4.1a; desenho em docs/superpowers/specs/2026-09-26-armas-realistas-design.md,
// seção 5.2): as armas realistas feitas no Blender (assets/armas/<id>/; registro em src/data/armasReais.js). Carrega o
// .glb uma vez por arma (os três níveis, os soquetes, as peças móveis), o relatório e a ficha (a planta da bancada); as
// texturas por conjunto (`perto`: 2048/1024; `mundo`: 512/256, que também serve o `longe`) quando o primeiro material do
// conjunto é pedido; os materiais por (arma, conjunto, skin), guardando a de fábrica e as duas últimas usadas. Tudo
// marcado `userData.shared` (o dispose das cenas não toca); sai no `forget` (recarga) e no `dispose`. Os carregadores
// são injetados: no navegador, o GLTFLoader do vendor e o TextureLoader; no Node, falsos.

import * as THREE from 'three';
import { ARMAS_REAIS, LODS_REAIS, TEXTURAS_DO_LOD } from '../../data/armasReais.js';
import { VIEWMODEL } from '../../data/viewmodel.js';
import { FABRICA, chaveDaSkin, skinDeFabrica } from '../skins/skin.js';
import { fichaParaPlanta, MM_POR_U, validarFicha } from './ficha.js';
import { ancorasDosSoquetes, montarInstanciaGlb, resumirGlb } from './glbWeapon.js';
import { ambienteDoMaterial, criarMaterialZona } from './materialArma.js';

const now = () => (globalThis.performance?.now ? globalThis.performance.now() : Date.now());
const RAIZ = new URL('../../../', import.meta.url);
const DECODIFICADOR_DRACO = new URL('vendor/three/examples/jsm/libs/draco/gltf/', RAIZ).href;
const SKINS_GUARDADAS = 2; // além da de fábrica, por (arma, conjunto)

/**
 * Carregadores do navegador: GLTFLoader do vendor com o DRACOLoader (a geometria vem comprimida), TextureLoader com as
 * texturas no padrão do glTF, fetch do JSON. `descartar` encerra os workers do decodificador.
 */
export function carregadoresDoNavegador() {
  let gltf = null; // Promise<GLTFLoader>: um carregador só, mesmo com pedidos ao mesmo tempo
  let draco = null;
  const texturas = new THREE.TextureLoader();
  const carregador = () => (gltf ??= Promise.all([
    import('three/addons/loaders/GLTFLoader.js'),
    import('three/addons/loaders/DRACOLoader.js'),
  ]).then(([{ GLTFLoader }, { DRACOLoader }]) => {
    draco = new DRACOLoader().setDecoderPath(DECODIFICADOR_DRACO);
    return new GLTFLoader().setDRACOLoader(draco);
  }));
  return {
    async glb(url) {
      return (await carregador()).loadAsync(url);
    },
    async textura(url) {
      const t = await texturas.loadAsync(url);
      t.flipY = false;
      t.colorSpace = THREE.NoColorSpace;
      return t;
    },
    async json(url) {
      const r = await fetch(url);
      if (!r.ok) throw new Error(`${url}: HTTP ${r.status}`);
      return r.json();
    },
    descartar() {
      draco?.dispose();
      draco = null;
      gltf = null;
    },
  };
}

export class GlbSource {
  #carregar;
  #log;
  #glb = new Map(); // id → Promise<pronto>
  #prontos = new Map(); // id → {resumo, info, ms, neutro}
  #texturas = new Map(); // `${id}:${conjunto}` → Promise<{n, m}>
  #materiais = new Map(); // `${id}:${conjunto}:${skin}` → Promise<{zona: material}>
  #prontosMat = new Map(); // mesma chave → {zona: material}
  #usadas = new Map(); // `${id}:${conjunto}` → chaves de skin na ordem de uso (a de fábrica fica sempre)
  #skins = new Map(); // id → skin atual
  #versoes = new Map(); // id → número da recarga (?v=)
  #texturasProntas = new Set(); // as carregadas (a anisotropia segue a config)
  #anisotropia;
  #ambiente = null;
  #intensidade = 1;
  #descartada = false;

  /**
   * @param {{carregadores:{glb:(url:string)=>Promise<{scene:THREE.Object3D}>, textura:(url:string)=>Promise<THREE.Texture>,
   *   json:(url:string)=>Promise<object>}, log?:object|null, anisotropia?:number}} deps
   */
  constructor({ carregadores, log = null, anisotropia = 8 }) {
    this.#carregar = carregadores;
    this.#log = log;
    this.#anisotropia = anisotropia;
  }

  get ids() {
    return Object.keys(ARMAS_REAIS);
  }

  has(id) {
    return Boolean(ARMAS_REAIS[id]);
  }

  lods() {
    return LODS_REAIS;
  }

  #url(id, arquivo) {
    const url = new URL(`${ARMAS_REAIS[id].pasta}${arquivo}`, RAIZ);
    const v = this.#versoes.get(id);
    if (v) url.searchParams.set('v', String(v));
    return url.href;
  }

  /** Carrega o .glb, o relatório e a ficha de uma arma (uma vez; pedidos iguais dividem a promessa). */
  carregar(id) {
    if (this.#descartada) return Promise.reject(new Error('WeaponLibrary: já foi descartada'));
    if (!this.has(id)) return Promise.reject(new Error(`${id} não é uma arma realista`));
    let p = this.#glb.get(id);
    if (!p) {
      const t0 = now();
      p = Promise.all([
        this.#carregar.glb(this.#url(id, `${id}.glb`)),
        this.#carregar.json(this.#url(id, `${id}.relatorio.json`)),
        this.#carregar.json(new URL(`tools/blender/refs/${id}.json`, RAIZ).href),
      ]).then(([gltf, relatorio, ficha]) => {
        const resumo = resumirGlb(gltf.scene, id);
        // O modelo carregado é o molde das instâncias e nunca vai à cena: as malhas dele guardam só a geometria, com um
        // material neutro no lugar dos do arquivo; cada instância recebe os materiais das zonas (montarInstanciaGlb).
        const neutro = new THREE.MeshBasicMaterial({ name: `molde:${id}` });
        resumo.raiz.traverse((o) => {
          if (!o.isMesh) return;
          for (const m of Array.isArray(o.material) ? o.material : [o.material]) m?.dispose();
          o.material = neutro;
        });
        if (this.#descartada || this.#glb.get(id) !== p) {
          resumo.raiz.traverse((o) => o.isMesh && o.geometry.dispose());
          neutro.dispose();
          throw new Error(`arma ${id} descartada durante a carga`);
        }
        const pronto = { resumo, info: this.#info(id, resumo, relatorio, validarFicha(ficha)), ms: now() - t0, neutro };
        this.#prontos.set(id, pronto);
        this.#log?.debug?.(`arma ${id} (glb): ${LODS_REAIS.map((l) => `${l} ${resumo.lods[l].triangulos}`).join(' · ')} triângulos em ${pronto.ms.toFixed(0)} ms`);
        return pronto;
      });
      p.catch((err) => {
        if (this.#glb.get(id) === p) this.#glb.delete(id);
        if (!this.#descartada) this.#log?.error?.(`arma ${id}: não carregou — ${err?.message ?? err}`);
      });
      this.#glb.set(id, p);
    }
    return p;
  }

  #info(id, resumo, relatorio, ficha) {
    const a = ARMAS_REAIS[id];
    const min = new THREE.Vector3().fromArray(resumo.caixa.min);
    const max = new THREE.Vector3().fromArray(resumo.caixa.max);
    return {
      id, source: 'glb', category: VIEWMODEL.weapons[id]?.category ?? a.categoria,
      bounds: resumo.caixa, radius: max.distanceTo(min) / 2,
      anchors: ancorasDosSoquetes(resumo.soquetes), sockets: resumo.soquetes,
      hands: false, // as luvas chegam na 4.1b (plano da 4.1a, D7)
      plan: fichaParaPlanta(ficha), lengthU: ficha.medidas.comprimento.mm / MM_POR_U,
      parts: [...a.pecas], zones: [...a.zonas], lods: [...LODS_REAIS],
      report: relatorio, ficha, iou: relatorio?.silhueta?.iouTolerancia ?? null, recipe: null,
    };
  }

  /** Info da arma (null antes de carregar). */
  info(id) {
    return this.#prontos.get(id)?.info ?? null;
  }

  /** Skin atual da arma (a de fábrica até alguém trocar). */
  skinOf(id) {
    if (!this.#skins.has(id)) this.#skins.set(id, skinDeFabrica(id));
    return this.#skins.get(id);
  }

  setSkin(id, skin) {
    this.#skins.set(id, skin);
  }

  #texturasDe(id, conjunto) {
    const chave = `${id}:${conjunto}`;
    let p = this.#texturas.get(chave);
    if (!p) {
      const pre = conjunto === 'perto' ? id : `${id}_mundo`;
      p = Promise.all([this.#carregar.textura(this.#url(id, `${pre}_n.webp`)), this.#carregar.textura(this.#url(id, `${pre}_m.webp`))])
        .then(([n, m]) => {
          for (const t of [n, m]) {
            t.userData.shared = true;
            t.anisotropy = this.#anisotropia;
            this.#texturasProntas.add(t);
          }
          return { n, m };
        });
      p.catch(() => {
        if (this.#texturas.get(chave) === p) this.#texturas.delete(chave);
      });
      this.#texturas.set(chave, p);
    }
    return p;
  }

  /** Materiais (um por zona) de uma arma num conjunto de texturas com uma skin. */
  materiais(id, conjunto, skin = this.skinOf(id)) {
    const sk = chaveDaSkin(skin);
    const chave = `${id}:${conjunto}:${sk}`;
    this.#usar(`${id}:${conjunto}`, sk);
    let p = this.#materiais.get(chave);
    if (!p) {
      p = this.#texturasDe(id, conjunto).then((texturas) => {
        const mats = {};
        for (const zona of ARMAS_REAIS[id].zonas) {
          mats[zona] = criarMaterialZona({
            zona, def: skin.zonas[zona], texturas, ambiente: this.#ambiente, intensidade: this.#intensidade,
            nome: `arma:${id}:${zona}:${sk}:${conjunto}`,
          });
        }
        if (this.#materiais.get(chave) !== p) {
          for (const m of Object.values(mats)) m.dispose();
          throw new Error(`arma ${id} descartada durante a carga`);
        }
        this.#prontosMat.set(chave, mats);
        return mats;
      });
      p.catch(() => {
        if (this.#materiais.get(chave) === p) this.#materiais.delete(chave);
      });
      this.#materiais.set(chave, p);
    }
    return p;
  }

  /** Guarda a de fábrica e as últimas skins usadas por (arma, conjunto); descarta os materiais da mais antiga. */
  #usar(grupo, sk) {
    const lista = (this.#usadas.get(grupo) ?? []).filter((k) => k !== sk);
    if (sk !== FABRICA) lista.push(sk);
    while (lista.length > SKINS_GUARDADAS) {
      const velha = `${grupo}:${lista.shift()}`;
      for (const m of Object.values(this.#prontosMat.get(velha) ?? {})) m.dispose();
      this.#prontosMat.delete(velha);
      this.#materiais.delete(velha);
    }
    this.#usadas.set(grupo, lista);
  }

  /** Instância nova da arma num nível, com a skin atual. */
  async instancia(id, { lod = 'perto' } = {}) {
    if (!LODS_REAIS.includes(lod)) throw new Error(`nível de detalhe desconhecido: ${lod} (use ${LODS_REAIS.join(', ')})`);
    const pronto = await this.carregar(id);
    const mats = await this.materiais(id, TEXTURAS_DO_LOD[lod]);
    return montarInstanciaGlb(pronto.resumo, id, lod, mats, pronto.info.anchors, pronto.info.radius);
  }

  /** Reflexo do set nos materiais de todas as armas (null volta ao ambiente da cena). */
  setAmbiente(textura, intensidade = 1) {
    this.#ambiente = textura;
    this.#intensidade = intensidade;
    for (const mats of this.#prontosMat.values()) for (const m of Object.values(mats)) ambienteDoMaterial(m, textura, intensidade);
  }

  /** Anisotropia das texturas das armas (graphics.anisotropy); as já carregadas sobem de novo para a GPU. */
  setAnisotropia(n) {
    this.#anisotropia = n;
    for (const t of this.#texturasProntas) {
      t.anisotropy = n;
      t.needsUpdate = true;
    }
  }

  /** Linhas do console `armas`: uma por (arma, nível). */
  relatorio() {
    const rows = [];
    for (const id of this.ids) {
      const pronto = this.#prontos.get(id);
      for (const lod of LODS_REAIS) {
        rows.push({
          id, lod, source: 'glb',
          state: pronto ? 'pronta' : this.#glb.has(id) ? 'carregando' : '—',
          triangles: pronto ? Math.round(pronto.resumo.lods[lod].triangulos) : 0,
          ms: pronto ? Math.round(pronto.ms) : 0,
          groups: pronto ? Object.keys(pronto.resumo.lods[lod].pecas).length : 0,
        });
      }
    }
    return rows;
  }

  /** Esquece a arma: descarta materiais, texturas e geometrias; a próxima carga busca de novo. */
  forget(id) {
    for (const [k, mats] of [...this.#prontosMat]) {
      if (!k.startsWith(`${id}:`)) continue;
      for (const m of Object.values(mats)) m.dispose();
      this.#prontosMat.delete(k);
    }
    for (const k of [...this.#materiais.keys()]) if (k.startsWith(`${id}:`)) this.#materiais.delete(k);
    for (const k of [...this.#usadas.keys()]) if (k.startsWith(`${id}:`)) this.#usadas.delete(k);
    for (const [k, p] of [...this.#texturas]) {
      if (!k.startsWith(`${id}:`)) continue;
      p.then(({ n, m }) => {
        for (const t of [n, m]) {
          this.#texturasProntas.delete(t);
          t.dispose();
        }
      }, () => {});
      this.#texturas.delete(k);
    }
    const pronto = this.#prontos.get(id);
    if (pronto) {
      pronto.resumo.raiz.traverse((o) => o.isMesh && o.geometry.dispose());
      pronto.neutro.dispose();
    }
    this.#prontos.delete(id);
    this.#glb.delete(id);
  }

  /** Recarga depois de exportar do Blender: esquece e busca de novo com ?v= novo (sem o cache do navegador). */
  async recarregar(id) {
    this.forget(id);
    this.#versoes.set(id, Date.now());
    return this.carregar(id);
  }

  dispose() {
    for (const id of this.ids) this.forget(id);
    this.#carregar.descartar?.();
    this.#descartada = true;
  }
}
```

- [ ] **Passo 4: O serviço com as duas origens** — substituir `src/weapons/model/weaponLibrary.js` inteiro:

```js file=src/weapons/model/weaponLibrary.js
// Serviço `weaponModels` (Fase 4.1: docs/phases/phase-4.md, seção 4.1, "Gerador"; Fase 4.1a:
// docs/superpowers/specs/2026-09-26-armas-realistas-design.md, seção 5.2): guarda e empresta as armas do jogo, de duas
// origens até o fim da 4.1d —
//  - `glb`: as realistas feitas no Blender (src/data/armasReais.js), pela GlbSource: o .glb, as texturas, os materiais
//    de zona com a skin atual e o reflexo do set;
//  - `massinha`: as receitas da 4.1 (src/data/armas/), pelo gerador SDF: malhas por (arma, nível), materiais por (arma,
//    facção), a planta de referência para a bancada.
// A interface é a mesma para as duas: `ids`, `has`, `source`, `lods`, `describe`/`info` (no lugar da `recipe` da 4.1),
// `meshes`/`preload`, `instance`, `report`, `reload` (depois de exportar do Blender) e `dispose`; as skins de acabamento
// (`skinOf`/`setSkin`) e o ambiente (`setEnvironment`) valem para as realistas. Geometrias, materiais e texturas são
// compartilhados (userData.shared: o dispose das cenas não os toca) e saem só aqui.

import * as THREE from 'three';
import { EV } from '../../core/events.js';
import { ARMAS } from '../../data/armas/index.js';
import { ARMAS_REAIS } from '../../data/armasReais.js';
import { VIEWMODEL } from '../../data/viewmodel.js';
import { bounds } from '../../clay/sdf/nodes.js';
import { plantaDoArquivo } from './ficha.js';
import { GlbSource, carregadoresDoNavegador } from './glbSource.js';
import { recipeWholeTree, validateRecipe, weaponFaction } from './recipe.js';
import { silhouetteLength } from './silhouette.js';
import { WEAPON_LODS, assembleWeapon, buildWeaponMeshes, createWeaponMaterials } from './weaponModel.js';

const RAIZ = new URL('../../../', import.meta.url);

export class WeaponLibrary {
  #sdf;
  #log;
  #events;
  #carregar;
  #glb;
  // A arma realista vale sobre a receita de massinha do mesmo id (a da AK fica no disco até sair, na Tarefa 16).
  #recipes = new Map(Object.entries(ARMAS).filter(([id]) => !ARMAS_REAIS[id]));
  #meshes = new Map(); // `${id}:${lod}` → Promise<built> (massinha)
  #built = new Map(); // `${id}:${lod}` → built (pronto)
  #materials = new Map(); // `${id}:${facção}` → ClayMaterial[]
  #plans = new Map(); // id → planta (massinha)
  #infos = new Map(); // id → info (massinha)
  #disposed = false;

  /**
   * @param {{sdf:import('../../clay/sdf/sdfMesher.js').SdfMesher|null, log?:object|null,
   *          events?:import('../../core/events.js').EventBus|null, anisotropy?:number,
   *          carregadores?:object|null}} deps `carregadores` substitui o GLTFLoader/TextureLoader/fetch (testes)
   */
  constructor({ sdf, log = null, events = null, anisotropy = 8, carregadores = null }) {
    this.#sdf = sdf;
    this.#log = log;
    this.#events = events;
    this.#carregar = carregadores ?? carregadoresDoNavegador();
    this.#glb = new GlbSource({ carregadores: this.#carregar, log, anisotropia: anisotropy });
  }

  /** Armas com modelo: as realistas, depois as de massinha (a ordem dos registros). */
  get ids() {
    return [...this.#glb.ids, ...this.#recipes.keys()];
  }

  has(id) {
    return this.#glb.has(id) || this.#recipes.has(id);
  }

  /** 'glb', 'massinha' ou null. */
  source(id) {
    if (this.#glb.has(id)) return 'glb';
    return this.#recipes.has(id) ? 'massinha' : null;
  }

  /** Níveis de detalhe da arma. */
  lods(id) {
    return this.#glb.has(id) ? this.#glb.lods() : WEAPON_LODS;
  }

  /** Carrega o que falta para o `info` (o .glb, o relatório e a ficha; a planta das de massinha) e devolve o info. */
  async describe(id) {
    if (this.#disposed) throw new Error('WeaponLibrary: já foi descartada');
    if (this.#glb.has(id)) return (await this.#glb.carregar(id)).info;
    if (!this.#recipes.has(id)) throw new Error(`arma sem modelo: ${id}`);
    if (!this.#plans.has(id)) {
      // A planta vem do arquivo que a receita aponta (`refs.planta`); a faca não tem (é desenhada de cabeça): sem busca.
      const arquivo = this.#recipes.get(id).refs?.planta;
      const plan = arquivo ? plantaDoArquivo(await this.#carregar.json(new URL(arquivo, RAIZ).href)) : null;
      this.#plans.set(id, plan);
      this.#infos.delete(id);
    }
    return this.info(id);
  }

  /** Info da arma no formato comum (ver o plano da 4.1a, Tarefa 11); null antes de carregar (glb) ou sem modelo. */
  info(id) {
    if (this.#glb.has(id)) return this.#glb.info(id);
    const recipe = this.#recipes.get(id);
    if (!recipe) return null;
    let info = this.#infos.get(id);
    if (!info) {
      const b = bounds(recipeWholeTree(recipe));
      const plan = this.#plans.get(id) ?? null;
      const size = new THREE.Vector3(b.max[0] - b.min[0], b.max[1] - b.min[1], b.max[2] - b.min[2]);
      info = {
        id, source: 'massinha', category: VIEWMODEL.weapons[id]?.category ?? null,
        bounds: { min: [...b.min], max: [...b.max] }, radius: size.length() / 2,
        anchors: recipe.anchors, sockets: null, hands: true,
        plan, lengthU: plan?.lengthU ?? silhouetteLength(recipe),
        parts: [...new Set(recipe.parts.map((p) => p.group))], zones: null, lods: [...WEAPON_LODS],
        report: null, ficha: null, iou: null, recipe,
      };
      this.#infos.set(id, info);
    }
    return info;
  }

  /**
   * Malhas de uma arma num nível (massinha: gera na primeira vez; glb: carrega o .glb). Pedidos iguais dividem a mesma
   * promessa.
   */
  meshes(id, lod = 'perto') {
    if (this.#disposed) return Promise.reject(new Error('WeaponLibrary: já foi descartada'));
    if (this.#glb.has(id)) {
      if (!this.#glb.lods().includes(lod)) return Promise.reject(new Error(`nível de detalhe desconhecido: ${lod}`));
      return this.#glb.carregar(id).then((p) => ({
        id, lod, source: 'glb', triangles: p.resumo.lods[lod].triangulos, ms: p.ms, groups: p.resumo.lods[lod].pecas,
      }));
    }
    const recipe = this.#recipes.get(id);
    if (!recipe) return Promise.reject(new Error(`arma sem modelo: ${id}`));
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

  /** Materiais de massinha de uma arma para uma facção (um por massa, na ordem do `mat`). */
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
   * Instância nova da arma (THREE.Group com userData.weapon). Pode ser posta em qualquer cena; tirar da cena basta.
   * @param {string} id
   * @param {{lod?:string, faction?:'tr'|'ct'|'ambos'}} [options] a facção só vale para as de massinha (o acento)
   */
  async instance(id, { lod = 'perto', faction = weaponFaction(id) } = {}) {
    if (this.#disposed) throw new Error('WeaponLibrary: já foi descartada');
    if (this.#glb.has(id)) return this.#glb.instancia(id, { lod });
    const built = await this.meshes(id, lod);
    const recipe = this.#recipes.get(id);
    return assembleWeapon(recipe, built, this.#materialsFor(recipe, built, faction), faction);
  }

  /** Pré-carrega (sem esperar): as armas do jogador ao entrar no mapa. */
  preload(ids, lod = 'perto') {
    return Promise.allSettled(ids.filter((id) => this.has(id)).map((id) =>
      (this.#glb.has(id) ? this.#glb.instancia(id, { lod: this.#glb.lods().includes(lod) ? lod : 'perto' }) : this.meshes(id, lod))));
  }

  /** Skin atual de uma arma realista. */
  skinOf(id) {
    if (!this.#glb.has(id)) throw new Error(`${id} não é uma arma realista (skins de acabamento só nas armas realistas)`);
    return this.#glb.skinOf(id);
  }

  /** Troca a skin de uma arma realista; quem tem instância na cena pede outra (EV.WEAPON_MODEL, phase 'skin'). */
  setSkin(id, skin) {
    if (!this.#glb.has(id)) throw new Error(`${id} não é uma arma realista (skins de acabamento só nas armas realistas)`);
    this.#glb.setSkin(id, skin);
    this.#events?.emit(EV.WEAPON_MODEL, { id, phase: 'skin' });
    return skin;
  }

  /** Reflexo do set (PMREM do mapa carregado) nos materiais das armas realistas; null volta ao ambiente da cena. */
  setEnvironment(texture, intensity = 1) {
    this.#glb.setAmbiente(texture, intensity);
  }

  /** Anisotropia das texturas das armas realistas (graphics.anisotropy). */
  setAnisotropy(n) {
    this.#glb.setAnisotropia(n);
  }

  /** Relatório do console (`armas`): uma linha por (arma, nível), das duas origens. */
  report() {
    const rows = this.#glb.relatorio();
    for (const id of this.#recipes.keys()) {
      for (const lod of WEAPON_LODS) {
        const built = this.#built.get(`${id}:${lod}`);
        const pending = this.#meshes.has(`${id}:${lod}`);
        rows.push({
          id, lod, source: 'massinha',
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
   * Relê a arma do disco (depois de exportar do Blender) sem recarregar a página. Emite EV.WEAPON_MODEL duas vezes:
   * `relendo` logo antes de descartar (quem tem instância na cena tira agora: uma malha descartada que continua sendo
   * desenhada volta para a GPU e ninguém a libera depois) e `pronta` com a arma nova carregada (glb) ou gerada no nível
   * pedido (massinha).
   */
  async reload(id, lod = 'perto') {
    if (this.#glb.has(id)) {
      this.#events?.emit(EV.WEAPON_MODEL, { id, phase: 'relendo' });
      await this.#glb.recarregar(id);
      await this.#glb.instancia(id, { lod: this.#glb.lods().includes(lod) ? lod : 'perto' });
      this.#events?.emit(EV.WEAPON_MODEL, { id, phase: 'pronta' });
      return this.#glb.info(id);
    }
    if (!this.#recipes.has(id)) throw new Error(`arma sem modelo: ${id}`);
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
    return this.info(id);
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
    this.#infos.delete(id);
  }

  dispose() {
    for (const id of this.#recipes.keys()) this.#forget(id);
    this.#glb.dispose();
    this.#disposed = true;
  }
}
```

- [ ] **Passo 5: O evento e o serviço no `main.js`** (a anisotropia das texturas das armas segue a config, como a do
  set) — em `src/core/events.js`, trocar:

```js
  WEAPON_MODEL: 'weapon:model', // {id, phase: 'relendo'|'pronta'} — a receita da arma foi relida: tire a instância antiga / a nova está pronta
```

por:

```js
  WEAPON_MODEL: 'weapon:model', // {id, phase: 'relendo'|'pronta'|'skin'} — a arma foi relida (tire a instância antiga / a nova está pronta) ou trocou de skin (peça outra instância)
```

e em `src/main.js`, trocar:

```js
  // Armas de massinha: malhas por (arma, nível) e materiais por (arma, facção), compartilhadas entre as cenas.
  const weaponModels = new WeaponLibrary({ sdf, log, events });
```

por:

```js
  // Armas: as realistas pelo .glb do Blender (níveis, texturas, materiais de zona com a skin) e as de massinha ainda não
  // refeitas pelo gerador SDF — tudo compartilhado entre as cenas.
  const weaponModels = new WeaponLibrary({ sdf, log, events, anisotropy: render.anisotropy });
```

e trocar:

```js
  config.watch('graphics.anisotropy', () => {
    clay.setAnisotropy(render.anisotropy);
    set.setAnisotropy(render.anisotropy);
  });
```

por:

```js
  config.watch('graphics.anisotropy', () => {
    clay.setAnisotropy(render.anisotropy);
    set.setAnisotropy(render.anisotropy);
    weaponModels.setAnisotropy(render.anisotropy);
  });
```

- [ ] **Passo 6: Rodar e ver passar**

Run: `node --test tests/weaponLibraryGlb.test.js`
Expected: PASS (5 testes).

Run: `npm test 2>&1 | tail -8`
Expected: `# tests 362`, `# fail 0`. Nenhum teste da 4.1 chama `weaponModels.recipe`; quem chama são o viewmodel e a
bancada, que passam a `info` nas Tarefas 13 e 14 — **até lá o jogo no navegador fica quebrado** na arma na mão e na
bancada (a suíte do Node passa); não abrir o jogo para conferir nada entre esta tarefa e a 14.

---

### Tarefa 12: Reflexo do set

**Files:**
- Create: `src/render/setReflection.js`
- Modify: `src/data/sandbox.js`, `src/data/pista.js`, `src/data/arsenal.js`, `src/maps/registry.js`, `src/maps/testRoom.js`,
  `src/maps/pista/index.js`, `src/maps/arsenal/index.js`, `src/modes/matchState.js`
- Test: `tests/setReflection.test.js`

A seção 5.4 do desenho: ao carregar o mapa, uma câmera cúbica (256² por face) fotografa o set de um ponto na altura do
olho, no centro da área jogável, e o PMREM vira o `envMap` dos materiais das armas realistas (D9). A luz própria do
viewmodel pedida na mesma seção já existe desde a 4.1 (`viewmodelLights.js`: cópia de cada luz do mapa, com a sombra
própria apertada em volta da arma e dos pulsos, 512 a 1024² pelo nível de sombra) e serve à arma realista sem mudança.

- [ ] **Passo 1: Testes**

```js file=tests/setReflection.test.js
// Reflexo do set das armas realistas (Fase 4.1a; desenho, seção 5.4): o ponto de cada mapa — o `reflection` montado dos
// dados, no centro da área jogável e na altura do olho, ou o spawn — e os pontos dos três mapas dentro da área jogável,
// longe das paredes e das peças. A captura (PMREM de uma câmera cúbica) precisa da GPU e é conferida no navegador
// (Tarefa 18).
import { test } from 'node:test';
import assert from 'node:assert/strict';
import * as THREE from 'three';
import { ARSENAL } from '../src/data/arsenal.js';
import { REFLEXO } from '../src/data/armasReais.js';
import { HULL } from '../src/data/movement.js';
import { PISTA } from '../src/data/pista.js';
import { TEST_ROOM } from '../src/data/sandbox.js';
import { pontoDoReflexo } from '../src/render/setReflection.js';

test('reflexo do set: o ponto do mapa, ou o olho no spawn', () => {
  const r = new THREE.Vector3(1, 2, 3);
  const spawn = { position: new THREE.Vector3(10, 0, 20) };
  const p = pontoDoReflexo({ reflection: r, spawn, collision: {} });
  assert.deepEqual(p.toArray(), [1, 2, 3]);
  assert.notEqual(p, r, 'uma cópia: quem chama pode mexer');
  assert.deepEqual(pontoDoReflexo({ spawn, collision: {} }).toArray(), [10, HULL.standEye, 20], 'mapa de andar: o spawn é o pé');
  assert.deepEqual(pontoDoReflexo({ spawn, collision: null }).toArray(), [10, 0, 20], 'câmera livre: o spawn já é o olho');
  assert.deepEqual([REFLEXO.tamanho, REFLEXO.intensidade], [256, 1]);
});

test('reflexo do set: os pontos dos mapas no centro da área jogável, longe das paredes e das peças', () => {
  const T = TEST_ROOM;
  assert.ok(Math.abs(T.reflexo.x) <= T.width / 4 && Math.abs(T.reflexo.z) <= T.depth / 4, 'sala: no meio');
  assert.ok(HULL.standEye < T.height / 2, 'o olho bem abaixo do teto');
  const B = PISTA.base;
  assert.ok(Math.abs(PISTA.reflexo.x - (B.minX + B.maxX) / 2) <= 200 && Math.abs(PISTA.reflexo.z - (B.minZ + B.maxZ) / 2) <= 200,
    'pista: no meio do compensado');
  const S = PISTA.strafe.paper;
  assert.ok(PISTA.reflexo.x > S.x[0] && PISTA.reflexo.x < S.x[1] && PISTA.reflexo.z > S.z[0] && PISTA.reflexo.z < S.z[1],
    'pista: na quadra de strafe, aberta');
  for (const p of PISTA.strafe.pillars) assert.ok(Math.hypot(p.at[0] - PISTA.reflexo.x, p.at[1] - PISTA.reflexo.z) > 200, 'longe dos pilares');
  assert.deepEqual([ARSENAL.reflexo.x, ARSENAL.reflexo.z], [ARSENAL.hold.x, ARSENAL.hold.z], 'bancada: o olho do "Segurar"');
  const y = ARSENAL.desk.mat.thickness + HULL.standEye;
  assert.ok(y > ARSENAL.bounds.min[1] && y < ARSENAL.bounds.max[1]);
});
```

Run: `node --test tests/setReflection.test.js`
Expected: FAIL — `Cannot find module '.../src/render/setReflection.js'`.

- [ ] **Passo 2: A captura**

```js file=src/render/setReflection.js
// Reflexo do set das armas realistas (Fase 4.1a; desenho em docs/superpowers/specs/2026-09-26-armas-realistas-design.md,
// seção 5.4; plano da 4.1a, D9): uma câmera cúbica (256² por face) fotografa o set de um ponto na altura do olho do
// boneco — o `reflection` do mapa montado (o centro da área jogável, dos dados dele) ou, sem ele, o spawn — e o PMREM
// filtra a foto no mapa de ambiente dos materiais das armas realistas (weaponModels.setEnvironment): o metal reflete o
// set de verdade. O `scene.environment` de cada mapa continua o do estúdio para o resto. O MatchState fotografa ao
// montar o mapa e de novo quando a GPU volta (EV.RENDER_CONTEXT), com o corpo do jogador fora da foto.

import * as THREE from 'three';
import { REFLEXO } from '../data/armasReais.js';
import { HULL } from '../data/movement.js';

/**
 * Ponto do reflexo de um mapa montado (mundo): o `reflection` dele; sem ele, o spawn — que é o pé nos mapas de andar
 * (soma a altura do olho) e já é o olho na câmera livre.
 * @param {{reflection?:THREE.Vector3, spawn:{position:THREE.Vector3}, collision?:object|null}} map
 * @returns {THREE.Vector3} uma cópia
 */
export function pontoDoReflexo(map) {
  if (map.reflection) return map.reflection.clone();
  const p = map.spawn.position.clone();
  if (map.collision) p.y += HULL.standEye;
  return p;
}

/**
 * Fotografa o set e devolve o render target do PMREM (a textura em `.texture`); quem chama descarta com `dispose()`.
 * @param {THREE.WebGLRenderer} renderer
 * @param {THREE.Scene} scene
 * @param {THREE.Vector3} position
 * @returns {THREE.WebGLRenderTarget}
 */
export function capturarReflexo(renderer, scene, position) {
  const pmrem = new THREE.PMREMGenerator(renderer);
  try {
    return pmrem.fromScene(scene, 0, REFLEXO.perto, REFLEXO.longe, { size: REFLEXO.tamanho, position });
  } finally {
    pmrem.dispose();
  }
}
```

- [ ] **Passo 3: O ponto nos dados de cada mapa**

Em `src/data/sandbox.js`, trocar:

```js
  spawn: Object.freeze({ x: 0, y: 0, z: 560, yawDeg: 0, pitchDeg: -4 }), // pés do jogador (o olho fica 64 u acima)
```

por:

```js
  spawn: Object.freeze({ x: 0, y: 0, z: 560, yawDeg: 0, pitchDeg: -4 }), // pés do jogador (o olho fica 64 u acima)
  // Reflexo das armas realistas (Fase 4.1a, src/render/setReflection.js): o centro da sala, na altura do olho do boneco.
  reflexo: Object.freeze({ x: 0, z: 0 }),
```

Em `src/data/pista.js`, trocar:

```js
  spawn: F({ at: F([0, 0, 1200]), heading: 0, pitch: -2 }),
```

por:

```js
  spawn: F({ at: F([0, 0, 1200]), heading: 0, pitch: -2 }),
  // Reflexo das armas realistas (Fase 4.1a, src/render/setReflection.js): o centro do compensado — a quadra de strafe,
  // aberta —, na altura do olho do boneco acima do chão dali.
  reflexo: F({ x: 0, z: 0 }),
```

Em `src/data/arsenal.js`, trocar:

```js
  hold: F({ x: 0, z: 236, yawDeg: 0, pitchDeg: -8 }),
```

por:

```js
  hold: F({ x: 0, z: 236, yawDeg: 0, pitchDeg: -8 }),
  // Reflexo das armas realistas (Fase 4.1a, src/render/setReflection.js): o olho do "Segurar", de pé no tapete de frente
  // para a roda — de onde a arma na mão vê a bancada (a arma da roda entra só como parte do set, a 51 u).
  reflexo: F({ x: 0, z: 236 }),
```

- [ ] **Passo 4: O ponto no mapa montado**

Em `src/maps/registry.js`, trocar:

```js
//   stations?: [{ number, id, label, aliases, spots: [{ id, label, position, yaw, pitch }] }] (console `estacao`;
//   src/maps/stations.js) }
```

por:

```js
//   stations?: [{ number, id, label, aliases, spots: [{ id, label, position, yaw, pitch }] }] (console `estacao`;
//   src/maps/stations.js),
//   reflection?: Vector3 (de onde a câmera cúbica fotografa o set para o reflexo das armas realistas; sem ele, o spawn —
//   src/render/setReflection.js) }
```

Em `src/maps/testRoom.js`, trocar:

```js
import { TEST_ROOM } from '../data/sandbox.js';
```

por:

```js
import { TEST_ROOM } from '../data/sandbox.js';
import { HULL } from '../data/movement.js';
```

e trocar:

```js
    post: { context: 'jogo', exposure: rigDef.exposure },
    spawn: {
```

por:

```js
    post: { context: 'jogo', exposure: rigDef.exposure },
    reflection: new THREE.Vector3(TEST_ROOM.reflexo.x, HULL.standEye, TEST_ROOM.reflexo.z),
    spawn: {
```

Em `src/maps/pista/index.js`, trocar:

```js
import { PISTA } from '../../data/pista.js';
```

por:

```js
import { PISTA } from '../../data/pista.js';
import { HULL } from '../../data/movement.js';
```

trocar:

```js
    if (spawnY === null) throw new Error('spawn da pista sem chão');
```

por:

```js
    if (spawnY === null) throw new Error('spawn da pista sem chão');
    const rf = PISTA.reflexo;
    const reflexoY = groundAt(collision, rf.x, rf.z);
    if (reflexoY === null) throw new Error('ponto do reflexo da pista sem chão');
```

e trocar:

```js
      staticShadows: true,
      spawn: {
```

por:

```js
      staticShadows: true,
      reflection: new THREE.Vector3(rf.x, reflexoY + HULL.standEye, rf.z),
      spawn: {
```

Em `src/maps/arsenal/index.js`, trocar:

```js
    // A roda gira com a arma: a sombra acompanha a cada quadro.
    staticShadows: false,
```

por:

```js
    // A roda gira com a arma: a sombra acompanha a cada quadro.
    staticShadows: false,
    reflection: new THREE.Vector3(ARSENAL.reflexo.x, ARSENAL.desk.mat.thickness + HULL.standEye, ARSENAL.reflexo.z),
```

- [ ] **Passo 5: Fotografar, refazer e descartar no `MatchState`**

Em `src/modes/matchState.js`, trocar:

```js
import { disposeObject3D } from '../render/dispose.js';
```

por:

```js
import { disposeObject3D } from '../render/dispose.js';
import { capturarReflexo, pontoDoReflexo } from '../render/setReflection.js';
import { REFLEXO } from '../data/armasReais.js';
```

trocar:

```js
    this.viewmodel = null; // arma na mão em primeira pessoa (Fase 4.1)
```

por:

```js
    this.viewmodel = null; // arma na mão em primeira pessoa (Fase 4.1)
    this.reflection = null; // reflexo do set das armas realistas (Fase 4.1a): o render target do PMREM
```

trocar:

```js
    s.render.setView(this.map.scene, this.camera, { staticShadows: this.map.staticShadows ?? false });
```

por:

```js
    s.render.setView(this.map.scene, this.camera, { staticShadows: this.map.staticShadows ?? false });
    // Reflexo do set das armas realistas: fotografado com o mapa pronto e as sombras como no jogo.
    this.#captureReflection();
```

trocar:

```js
    this.viewmodel.attach(this.map.scene, this.map.collision ?? null);
```

por:

```js
    this.viewmodel.attach(this.map.scene, this.map.collision ?? null);
    // GPU reiniciada: o reflexo se perdeu com ela (o mapa reassa o ambiente dele antes: inscreveu-se na montagem).
    this.subs.on(s.events, EV.RENDER_CONTEXT, ({ lost }) => {
      if (!lost) this.#captureReflection();
    });
```

trocar:

```js
  /** Gera (sem esperar) as malhas "perto" das armas do inventário local que têm receita. */
```

por:

```js
  /**
   * Fotografa o set para o reflexo das armas realistas (seção 5.4 do desenho) e entrega ao serviço de armas; o corpo do
   * jogador (visível em terceira pessoa e no noclip) fica fora da foto.
   */
  #captureReflection() {
    const s = this.s;
    const body = this.body;
    const was = body ? [body.root.visible, body.shadow.visible] : null;
    if (body) body.root.visible = body.shadow.visible = false;
    try {
      this.reflection?.dispose();
      this.reflection = capturarReflexo(s.render.renderer, this.map.scene, pontoDoReflexo(this.map));
      s.weaponModels.setEnvironment(this.reflection.texture, REFLEXO.intensidade);
    } finally {
      if (body) [body.root.visible, body.shadow.visible] = was;
    }
  }

  /** Gera (sem esperar) as malhas "perto" das armas do inventário local que têm modelo. */
```

e trocar:

```js
    this.viewmodel?.dispose();
    this.physicsDebug?.dispose();
```

por:

```js
    this.viewmodel?.dispose();
    s.weaponModels.setEnvironment(null);
    this.reflection?.dispose();
    this.reflection = null;
    this.physicsDebug?.dispose();
```

- [ ] **Passo 6: Rodar e ver passar**

Run: `node --test tests/setReflection.test.js`
Expected: PASS (2 testes). Suíte inteira: `npm test 2>&1 | tail -8` → `# tests 364`, `# fail 0`.

---

### Tarefa 13: A arma realista em primeira pessoa (sem mãos) e a troca de skin

**Files:**
- Modify: `src/weapons/viewmodel/viewmodel.js`, `src/weapons/viewmodel/placement.js`, `src/modes/matchState.js`
- Test: `tests/viewmodel.test.js`, `tests/armaAk47.test.js`

O viewmodel passa do `recipe(id)` da 4.1 para o `info(id)` (D6): a arma realista vem sem braços (D7: `hands: false`,
as luvas chegam na 4.1b), a condição de aparecer deixa de exigir os braços quando a arma não usa mãos, a troca de skin
pede outra instância (a antiga fica na mão até a nova estar pronta) e as variantes de shader compilam antes de a arma
aparecer (`renderer.compileAsync`, sem travada na primeira aparição). O "tem receita" vira "tem modelo" (`hasModel`).

- [ ] **Passo 1: Testes** — em `tests/viewmodel.test.js`, trocar:

```js
import { ARMAS } from '../src/data/armas/index.js';
```

por:

```js
import { ARMAS } from '../src/data/armas/index.js';
import { ARMAS_REAIS } from '../src/data/armasReais.js';
```

trocar:

```js
    assert.deepEqual(handSides(r), id === 'knife' ? ['direita'] : ['direita', 'esquerda'], id);
  }
});
```

por:

```js
    assert.deepEqual(handSides(r), id === 'knife' ? ['direita'] : ['direita', 'esquerda'], id);
  }
  // A arma realista sem as luvas (4.1a): as âncoras das mãos existem (os soquetes), mas nenhuma mão aparece.
  assert.deepEqual(handSides({ hands: false, anchors: ARMAS.glock.anchors }), []);
});
```

trocar:

```js
    enabled: true, firstPerson: true, alive: true, noclip: false, zoomed: false, item: 'ak47', hasRecipe: (id) => Boolean(ARMAS[id]),
  };
```

por:

```js
    enabled: true, firstPerson: true, alive: true, noclip: false, zoomed: false, item: 'ak47',
    hasModel: (id) => Boolean(ARMAS[id] || ARMAS_REAIS[id]),
  };
```

e trocar:

```js
  assert.equal(viewmodelVisible({ ...base, item: 'usps' }), false, 'arma sem receita (4.4)');
```

por:

```js
  assert.equal(viewmodelVisible({ ...base, item: 'usps' }), false, 'arma sem modelo (4.4)');
```

Em `tests/armaAk47.test.js`, trocar:

```js
import { fileURLToPath } from 'node:url';
import { validarSaida } from '../tools/blender/saida.mjs';
```

por:

```js
import { fileURLToPath } from 'node:url';
import * as THREE from 'three';
import { VIEWMODEL } from '../src/data/viewmodel.js';
import { viewCategory, viewPlacement, viewmodelVerticalFov, weaponNudge } from '../src/weapons/viewmodel/placement.js';
import { validarSaida } from '../tools/blender/saida.mjs';
```

e trocar:

```js
  for (const p of ['carregador', 'gatilho', 'cao', 'seletor']) assert.deepEqual(resumo.lods.perto.pecas[p].extras, { eixo_giro: [0, 0, 1] });
});
```

por:

```js
  for (const p of ['carregador', 'gatilho', 'cao', 'seletor']) assert.deepEqual(resumo.lods.perto.pecas[p].extras, { eixo_giro: [0, 0, 1] });
});

test('AK-47 tipo 3: na posição da categoria rifle, a boca aparece embaixo à direita da tela (16:9, valores padrão)', () => {
  const { resumo } = validarSaida('ak47', RAIZ);
  const offset = { x: VIEWMODEL.offset.x.default, y: VIEWMODEL.offset.y.default, z: VIEWMODEL.offset.z.default };
  const pl = viewPlacement(viewCategory('ak47'), { offset, nudge: weaponNudge('ak47') });
  const t = Math.tan((viewmodelVerticalFov(VIEWMODEL.fov.default) * Math.PI) / 360);
  const p = new THREE.Vector3(...resumo.soquetes.boca.posicao).applyQuaternion(pl.quaternion).add(pl.position);
  const x = p.x / (-p.z * t * (16 / 9));
  const y = p.y / (-p.z * t);
  assert.ok(p.z < -VIEWMODEL.near && Math.abs(x) < 1 && Math.abs(y) < 1, `a boca fora da tela (${x.toFixed(2)}, ${y.toFixed(2)})`);
  assert.ok(x > -0.2 && y < 0.1, `a arma embaixo à direita (${x.toFixed(2)}, ${y.toFixed(2)})`);
});
```

Run: `node --test tests/viewmodel.test.js`
Expected: FAIL — `s.hasModel is not a function` (e `handSides` devolvendo as duas mãos para a arma sem luvas).

- [ ] **Passo 2: As contas** — em `src/weapons/viewmodel/placement.js`, trocar:

```js
/** Mãos que a arma usa: as âncoras `maoDireita`/`maoEsquerda` da receita (a faca só tem a direita). */
export function handSides(recipe) {
  const sides = [];
  if (recipe?.anchors?.maoDireita) sides.push('direita');
  if (recipe?.anchors?.maoEsquerda) sides.push('esquerda');
  return sides;
}
```

por:

```js
/**
 * Mãos que a arma usa: as âncoras `maoDireita`/`maoEsquerda` (a faca só tem a direita); nenhuma na arma realista sem
 * as luvas (`hands: false`, a AK da 4.1a). Aceita a receita de massinha ou o `info(id)` da biblioteca de armas.
 */
export function handSides(model) {
  const sides = [];
  if (model?.hands === false) return sides;
  if (model?.anchors?.maoDireita) sides.push('direita');
  if (model?.anchors?.maoEsquerda) sides.push('esquerda');
  return sides;
}
```

e trocar:

```js
 * luneta é da 4.5; no CS a arma some com o zoom), com `r_viewmodel 1` e com receita para o item na mão (as outras 18
 * armas até a 4.4, granadas até a 4.7, a bomba até a Fase 8). A bancada `arsenal` força com "Segurar".
 * @param {{enabled:boolean, firstPerson:boolean, alive:boolean, noclip:boolean, zoomed:boolean, item:string|null,
 *          hasRecipe:(id:string)=>boolean}} s
 */
export function viewmodelVisible(s) {
  return Boolean(s.enabled && s.firstPerson && s.alive && !s.noclip && !s.zoomed && s.item && s.hasRecipe(s.item));
}
```

por:

```js
 * luneta é da 4.5; no CS a arma some com o zoom), com `r_viewmodel 1` e com modelo para o item na mão — o `.glb` do
 * Blender ou a receita de massinha (as outras 18 armas até a 4.4, granadas até a 4.7, a bomba até a Fase 8). A bancada
 * `arsenal` força com "Segurar".
 * @param {{enabled:boolean, firstPerson:boolean, alive:boolean, noclip:boolean, zoomed:boolean, item:string|null,
 *          hasModel:(id:string)=>boolean}} s
 */
export function viewmodelVisible(s) {
  return Boolean(s.enabled && s.firstPerson && s.alive && !s.noclip && !s.zoomed && s.item && s.hasModel(s.item));
}
```

Em `src/modes/matchState.js`, trocar:

```js
        item: vm.item, hasRecipe: (id) => s.weaponModels.has(id),
```

por:

```js
        item: vm.item, hasModel: (id) => s.weaponModels.has(id),
```

- [ ] **Passo 3: O viewmodel pelo `info`** — em `src/weapons/viewmodel/viewmodel.js`, trocar:

```js
// Viewmodel parado (Fase 4.1; docs/phases/phase-4.md, seção 4.1, "Viewmodel parado"): a arma na mão em primeira pessoa
// numa camada própria do pipeline (postPipeline.addLayer) — cena com a arma e os dois braços de massinha, câmera que
// copia a do jogador com o FOV do viewmodel (viewmodel_fov) e a luz do mapa copiada (viewmodelLights.js). A arma fica na
// posição da categoria (src/data/viewmodel.js) mais os offsets; cada mão vai para a âncora da receita com a pose da
// âncora e o antebraço aponta para um cotovelo fixo fora da tela. Na 4.1 não anima: segura parado, com o boil "em
// dois" da massinha. Quem decide o que segurar e quando aparece é o MatchState (placement.js: viewmodelVisible).
```

por:

```js
// Viewmodel parado (Fase 4.1; docs/phases/phase-4.md, seção 4.1, "Viewmodel parado"; Fase 4.1a: a arma realista): a
// arma na mão em primeira pessoa numa camada própria do pipeline (postPipeline.addLayer) — cena com a arma e os braços
// de massinha, câmera que copia a do jogador com o FOV do viewmodel (viewmodel_fov) e a luz do mapa copiada
// (viewmodelLights.js). A arma fica na posição da categoria (src/data/viewmodel.js) mais os offsets; nas de massinha,
// cada mão vai para a âncora da receita com a pose da âncora e o antebraço aponta para um cotovelo fixo fora da tela; a
// realista (o .glb do Blender, com o reflexo do set) aparece sem braços até as luvas da 4.1b. Ainda não anima (4.3).
// Tudo sai do `info(id)` da biblioteca de armas, o mesmo para as duas origens. Quem decide o que segurar e quando
// aparece é o MatchState (placement.js: viewmodelVisible).
```

trocar:

```js
import {
  HAND_ANCHOR, anchorPose, categoryPlacement, elbowTarget, viewCategory, viewFaction, viewPlacement, viewmodelVerticalFov,
  weaponNudge,
} from './placement.js';
```

por:

```js
import {
  HAND_ANCHOR, anchorPose, categoryPlacement, elbowTarget, handSides, viewCategory, viewFaction, viewPlacement,
  viewmodelVerticalFov, weaponNudge,
} from './placement.js';
```

trocar:

```js
    this.weapon = null; // instância na mão
    this.recipe = null;
    this.itemKey = null; // `${id}:${lod}:${facção}` pedido
```

por:

```js
    this.weapon = null; // instância na mão
    this.info = null; // info(id) da arma na mão (weaponModels)
    this.sides = new Set(); // mãos que ela usa (nenhuma na realista sem as luvas)
    this.itemKey = null; // `${id}:${lod}:${facção}` pedido
```

trocar:

```js
    // Receita relida do disco (Blender): a instância antiga sai agora, antes de a biblioteca descartar as malhas.
    this.subs.on(events, EV.WEAPON_MODEL, ({ id, phase }) => {
      if (phase === 'relendo' && this.recipe?.id === id) this.#drop();
```

por:

```js
    // Arma relida do disco (Blender): a instância antiga sai agora, antes de a biblioteca descartar as malhas. Skin
    // trocada: pede outra instância (a antiga fica na mão até a nova estar pronta e compilada).
    this.subs.on(events, EV.WEAPON_MODEL, ({ id, phase }) => {
      if (phase === 'relendo' && this.info?.id === id) this.#drop();
```

trocar:

```js
   * Pede o item na mão (id de arma com receita, ou null). `faction` força o acento (a bancada); sem ela, as armas dos
   * dois lados pegam o time da braçadeira.
```

por:

```js
   * Pede o item na mão (id de arma com modelo, ou null). `faction` força o acento das de massinha (a bancada); sem ela,
   * as armas dos dois lados pegam o time da braçadeira.
```

trocar:

```js
    const [wid, wlod, wfaction] = key.split(':');
    Promise.all([this.weapons.instance(wid, { lod: wlod, faction: wfaction }), this.#ensureArms()]).then(([instance]) => {
      if (this.disposed || token !== this.token) return;
      this.#swap(instance, key);
    }).catch((err) => {
```

por:

```js
    const [wid, wlod, wfaction] = key.split(':');
    // A realista vem sem braços até a 4.1b; as variantes de shader compilam antes de a arma aparecer (sem travada).
    const arms = this.weapons.source(wid) === 'glb' ? null : this.#ensureArms();
    Promise.all([this.weapons.instance(wid, { lod: wlod, faction: wfaction }), arms]).then(async ([instance]) => {
      if (this.disposed || token !== this.token) return;
      await this.render.renderer.compileAsync(instance, this.camera, this.scene);
      if (this.disposed || token !== this.token) return;
      this.#swap(instance, key);
    }).catch((err) => {
```

trocar:

```js
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
```

por:

```js
  /** Troca a arma da mão pela instância nova: centro e raio, as mãos que ela usa e as poses pela âncora, posição a refazer. */
  #swap(instance, key) {
    this.#drop();
    const w = instance.userData.weapon;
    this.weapon = instance;
    this.info = this.weapons.info(w.id);
    this.sides = new Set(handSides(this.info));
    this.loadedKey = key;
    this.category = viewCategory(w.id);
    instance.updateMatrixWorld(true);
    new THREE.Box3().setFromObject(instance).getCenter(this.center);
    this.radius = w.radius;
    this.holder.add(instance);
    for (const side of this.sides) {
      const anchor = this.#anchor(HAND_ANCHOR[side]);
      if (anchor) this.arms[side]?.setPose(anchor.pose ?? 'aberta');
    }
    this.dirty = true;
  }

  /** Âncora da arma na mão (da receita ou dos soquetes do .glb), com o ajuste ao vivo por cima (viewmodel_ajuste mao). */
  #anchor(name) {
    const base = this.info?.anchors[name];
    const tuned = this.anchorTune[this.info?.id]?.[name];
    return base && tuned ? { ...base, ...tuned } : base;
  }
```

trocar:

```js
    this.weapon = null;
    this.recipe = null;
    this.loadedKey = null;
```

por:

```js
    this.weapon = null;
    this.info = null;
    this.sides = new Set();
    this.loadedKey = null;
```

trocar:

```js
    const pl = viewPlacement(cat, { offset, tune: this.tune[cat] ?? null, nudge: weaponNudge(this.recipe.id) }, this.placement);
```

por:

```js
    const pl = viewPlacement(cat, { offset, tune: this.tune[cat] ?? null, nudge: weaponNudge(this.info.id) }, this.placement);
```

trocar:

```js
      const arm = this.arms[side];
      const anchor = this.#anchor(HAND_ANCHOR[side]);
      if (!arm) continue;
```

por:

```js
      const arm = this.arms[side];
      const anchor = this.sides.has(side) ? this.#anchor(HAND_ANCHOR[side]) : null;
      if (!arm) continue;
```

trocar:

```js
    const show = Boolean(visible && this.weapon && this.arms.direita && this.loadedKey === this.itemKey);
```

por:

```js
    const show = Boolean(visible && this.weapon && (!this.sides.size || this.arms.direita) && this.loadedKey === this.itemKey);
```

e trocar:

```js
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
```

por:

```js
  setAnchorTune(side, patch) {
    if (!this.info) throw new Error('nenhuma arma na mão');
    if (this.info.source === 'glb') {
      throw new Error(`${this.info.id} é a arma realista: as mãos dela são as luvas da 4.1b (a empunhadura sai do Blender, não deste ajuste)`);
    }
    const name = HAND_ANCHOR[side];
    if (!this.info.anchors[name]) throw new Error(`${this.info.id} não tem ${name}`);
    const byWeapon = (this.anchorTune[this.info.id] ??= {});
    byWeapon[name] = { ...(byWeapon[name] ?? {}), ...patch };
    this.dirty = true;
    return this.anchorLine(side);
  }

  /** A linha da âncora de uma mão no formato da receita (src/data/armas/<id>.js). */
  anchorLine(side) {
    const name = HAND_ANCHOR[side];
    const a = this.#anchor(name);
    if (!a) return `${this.info?.id ?? '—'}: sem ${name}`;
```

- [ ] **Passo 4: Rodar e ver passar**

Run: `node --test tests/viewmodel.test.js tests/armaAk47.test.js`
Expected: PASS (9 + 3 testes). Suíte inteira: `npm test 2>&1 | tail -8` → `# tests 365`, `# fail 0`.

---

### Tarefa 14: A bancada `arsenal` pelas duas origens

**Files:**
- Modify (substituir inteiro): `src/maps/arsenal/turntable.js`, `src/maps/arsenal/bench.js`, `src/maps/arsenal/panel.js`
- Modify: `src/maps/arsenal/planSheets.js`, `src/maps/arsenal/index.js`, `src/data/arsenal.js`
- Test: `tests/arsenalStand.test.js`

A bancada deixa a receita e passa ao `info(id)` (D6) para tudo o que depende da arma: a caixa (fileiras), a planta e o
comprimento (folhas do quadro e a sobreposição), as âncoras (a boca da planta). O suporte de arame mede a arma por raios
na malha da própria instância — serve à realista e à de massinha —, no lugar do SDF da receita. A skin da realista é a
do serviço (D8): o painel e o console escrevem nele e o evento `skin` remonta a roda e a fileira (a mão troca sozinha,
Tarefa 13); a de massinha continua com a skin de massa da 4.1. Na realista, a facção some do painel e o nível `longe`
aparece; "Medir" mostra a silhueta medida no Blender. As variantes de shader compilam antes de cada arma entrar na cena,
com a luz da bancada já montada.

- [ ] **Passo 1: Testes do suporte**

```js file=tests/arsenalStand.test.js
// Suporte de arame da bancada `arsenal` (Fase 4.1a): a forma da arma medida por raios na malha da instância — a caixa,
// a parte de baixo em cada x e a meia largura numa altura —, a mesma conta para a arma realista (.glb) e a de massinha;
// os garfos do suporte encostam por baixo dela e a arma fica acima da tira de compensado.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import * as THREE from 'three';
import { ARSENAL } from '../src/data/arsenal.js';
import { buildWireStand, formaDaArma } from '../src/maps/arsenal/turntable.js';

const near = (a, b, eps, msg) => assert.ok(Math.abs(a - b) <= eps, `${msg}: ${a} ≠ ${b}`);

/** Uma "arma" de caixas: corpo de 20 × 2 × 1,6 u e, como peça móvel, um carregador de 2 × 4 × 1,2 u embaixo. */
function armaDeTeste() {
  const root = new THREE.Group();
  const corpo = new THREE.Mesh(new THREE.BoxGeometry(20, 2, 1.6), new THREE.MeshBasicMaterial());
  const carregador = new THREE.Group();
  carregador.position.set(4, -1, 0);
  const pente = new THREE.Mesh(new THREE.BoxGeometry(2, 4, 1.2), new THREE.MeshBasicMaterial());
  pente.position.set(0, -2, 0);
  carregador.add(pente);
  root.add(corpo, carregador);
  root.userData.weapon = { id: 'teste' };
  return root;
}

test('suporte: a forma da arma por raios na malha (caixa, parte de baixo e meia largura)', () => {
  const f = formaDaArma(armaDeTeste());
  near(f.box.min[0], -10, 1e-9, 'x mínimo');
  near(f.box.max[0], 10, 1e-9, 'x máximo');
  near(f.box.min[1], -5, 1e-9, 'y mínimo: o pé do carregador');
  near(f.underside(-8), -1, 1e-6, 'debaixo do corpo');
  near(f.underside(4), -5, 1e-6, 'debaixo do carregador');
  assert.equal(f.underside(15), null, 'fora da arma');
  near(f.halfWidth(-8, -0.65), 0.8, 1e-6, 'meia largura do corpo');
  near(f.halfWidth(4, -3), 0.6, 1e-6, 'meia largura do carregador');
});

test('suporte: os garfos encostam por baixo da arma e a arma fica acima da tira', () => {
  const set = { plywood: () => new THREE.MeshBasicMaterial(), wire: () => new THREE.MeshBasicMaterial() };
  const { group, weaponOffset } = buildWireStand(set, ARSENAL.stand, armaDeTeste());
  assert.equal(group.name, 'suporte-teste');
  near(weaponOffset.x, 0, 1e-9, 'centrada em x');
  assert.ok(weaponOffset.y - 5 > ARSENAL.stand.base.thickness, 'o pé do carregador livre da tira');
  const arame = group.getObjectByName('suporte-arame');
  arame.geometry.computeBoundingBox();
  assert.ok(arame.geometry.boundingBox.max.y > weaponOffset.y - 1, 'os garfos sobem até a parte de baixo do corpo');
});
```

Run: `node --test tests/arsenalStand.test.js`
Expected: FAIL — `does not provide an export named 'formaDaArma'`.

- [ ] **Passo 2: A roda e o suporte por raios** — substituir `src/maps/arsenal/turntable.js` inteiro:

```js file=src/maps/arsenal/turntable.js
// Roda de modelar e suporte de arame da bancada `arsenal` (Fase 4.1; QTT11 — a roda de escultor de metal; QTT9 —
// giratória de produto; QWS9, QWS12, QWS14 — suportes de arame em garfo, no item 13 do moodboard).
// A roda: pé pesado torneado, coluna e prato com anéis de centragem, tudo em metal de ferramenta com restos de massa.
// O suporte: tira de compensado no prato e dois garfos de arame; cada garfo sobe até encostar na parte de baixo da arma
// naquele ponto — medida por raios na malha da própria instância (Fase 4.1a: serve à arma realista do .glb e à de
// massinha) —, então qualquer arma deita certinho nele.

import * as THREE from 'three';
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';
import { wireGeometry } from '../../clay/set/propGeometry.js';

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

const _ray = new THREE.Raycaster();
const _o = new THREE.Vector3();
const _d = new THREE.Vector3();

/**
 * A forma da arma para o suporte, medida por raios na malha da instância (no referencial dela: +X boca, +Y cima, +Z
 * direita; a instância ainda sem pai, na origem): a caixa, a parte de baixo num x (o primeiro toque de um raio de baixo
 * para cima no plano do meio, z = 0) e a meia largura numa altura (o toque mais largo de dois raios vindos dos lados).
 * @param {THREE.Object3D} weapon
 * @returns {{box:{min:number[], max:number[]}, underside:(x:number)=>number|null, halfWidth:(x:number, y:number)=>number|null}}
 */
export function formaDaArma(weapon) {
  weapon.updateMatrixWorld(true);
  const meshes = [];
  weapon.traverse((o) => {
    if (o.isMesh) meshes.push(o);
  });
  const b = new THREE.Box3().setFromObject(weapon);
  const box = { min: b.min.toArray(), max: b.max.toArray() };
  const cast = (far) => {
    _ray.set(_o, _d);
    _ray.far = far;
    return _ray.intersectObjects(meshes, false)[0] ?? null;
  };
  return {
    box,
    underside(x) {
      _o.set(x, box.min[1] - 1, 0);
      _d.set(0, 1, 0);
      const hit = cast(box.max[1] - box.min[1] + 2);
      return hit ? hit.point.y : null;
    },
    halfWidth(x, y) {
      const span = box.max[2] - box.min[2] + 2;
      _o.set(x, y, box.max[2] + 1);
      _d.set(0, 0, -1);
      const a = cast(span);
      const za = a ? Math.abs(a.point.z) : null;
      _o.set(x, y, box.min[2] - 1);
      _d.set(0, 0, 1);
      const c = cast(span);
      const zc = c ? Math.abs(c.point.z) : null;
      if (za === null && zc === null) return null;
      return Math.max(za ?? 0, zc ?? 0);
    },
  };
}

/**
 * Suporte de arame para uma arma: a tira de compensado e os dois garfos (a 18% e 76% do comprimento), com a arma posta
 * em cima. Devolve o grupo do suporte e a posição da origem da arma no referencial do suporte.
 * @param {import('../../clay/set/index.js').SetLibrary} set
 * @param {object} def ARSENAL.stand
 * @param {THREE.Object3D} weapon a instância (weaponModels.instance), ainda sem pai
 * @returns {{group:THREE.Group, weaponOffset:THREE.Vector3}}
 */
export function buildWireStand(set, def, weapon) {
  const forma = formaDaArma(weapon);
  const { box } = forma;
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
  group.name = `suporte-${weapon.userData.weapon?.id ?? weapon.name}`;
  const base = new THREE.Mesh(new RoundedBoxGeometry(length * 1.05 + 4, baseT, Math.max(8, def.base.depth * Math.min(1, length / 40)), 2, 0.6), set.plywood());
  base.position.y = baseT / 2;
  base.name = 'suporte-base';
  group.add(base);
  const wires = [];
  for (const fx of forkXs) {
    const bottom = forma.underside(fx) ?? box.min[1];
    // Meia largura da arma logo acima do apoio: os braços do garfo encostam dos dois lados.
    const half = Math.min(4, Math.max(0.3, forma.halfWidth(fx, bottom + 0.35) ?? 0.3));
    const x = fx - centerX;
    const tipY = lift + bottom - wire; // o arame encosta por baixo da arma
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

Run: `node --test tests/arsenalStand.test.js`
Expected: PASS (2 testes).

- [ ] **Passo 3: As plantas pelo `info`** — em `src/maps/arsenal/planSheets.js`, trocar:

```js
// Plantas a lápis da bancada `arsenal` (Fase 4.1; QBP3, QBP13, QBP15 no item 13 do moodboard): uma folha de papel
// creme quadriculado por arma, com o contorno da planta de referência (tools/blender/refs/<id>.json) em grafite, a
```

por:

```js
// Plantas a lápis da bancada `arsenal` (Fase 4.1; QBP3, QBP13, QBP15 no item 13 do moodboard): uma folha de papel
// creme quadriculado por arma, com o contorno da planta de referência (o `info(id).plan` da biblioteca de armas: a
// planta de tools/blender/refs/<id>.json, ou a ficha da arma realista convertida) em grafite, a
```

trocar:

```js
import { recipeWholeTree } from '../../weapons/model/recipe.js';
import { bounds } from '../../clay/sdf/nodes.js';
import { plantaDoArquivo } from '../../weapons/model/ficha.js';

/** Lê a planta de uma arma (null se não houver: a faca, ou arquivo ausente); a ficha (formato 2) vira planta. */
export async function loadPlan(id) {
  try {
    const res = await fetch(new URL(`../../../tools/blender/refs/${id}.json`, import.meta.url));
    return res.ok ? plantaDoArquivo(await res.json()) : null;
  } catch {
    return null;
  }
}
```

por:

```js
import { recipeWholeTree } from '../../weapons/model/recipe.js';
```

trocar:

```js
 * @param {{id:string, name:string, recipe:object, plan:object|null, lengthU:number}} item
```

por:

```js
 * @param {{id:string, name:string, info:object, plan:object|null, lengthU:number}} item `info` = weaponModels.info(id)
```

trocar:

```js
  const tree = recipeWholeTree(item.recipe);
  const box = bounds(tree);
  const boca = item.recipe.anchors.boca?.pos ?? [0, 0, 0];
```

por:

```js
  const box = item.info.bounds;
  const boca = item.info.anchors.boca?.pos ?? [0, 0, 0];
```

e trocar:

```js
    // Sem planta: a silhueta da receita, sombreada a lápis (tom leve por baixo e hachuras a 45° por cima).
    const grid = gridFor(x0, y0, x1, y1, Math.max(0.03, (x1 - x0) / 260));
    const mask = sideMask(tree, grid);
```

por:

```js
    // Sem planta (só a faca de massinha): a silhueta da receita, sombreada a lápis (tom leve por baixo e hachuras a 45°).
    if (!item.info.recipe) throw new Error(`${item.id}: arma sem planta e sem receita para desenhar a silhueta`);
    const grid = gridFor(x0, y0, x1, y1, Math.max(0.03, (x1 - x0) / 260));
    const mask = sideMask(recipeWholeTree(item.info.recipe), grid);
```

- [ ] **Passo 4: As direções de explodir das peças novas** — em `src/data/arsenal.js`, trocar:

```js
  // "Explodir" do painel: cada grupo se afasta do corpo nessa direção (u por unidade da régua).
  explode: F({
    max: 8,
    dirs: F({
      carregador: F([0, -1, 0]), ferrolho: F([0, 0, 1]), slide: F([0, 1, 0]), gatilho: F([0, -0.8, 0.6]),
      bomba: F([1, -0.2, 0]), alavanca: F([0, 0.3, 1]), silenciador: F([1, 0, 0]),
    }),
  }),
```

por:

```js
  // "Explodir" do painel: cada grupo (massinha) ou peça móvel (realista) se afasta do corpo nessa direção (u por unidade
  // da régua). O cão da realista sai por cima e para a direita; o seletor, para a direita.
  explode: F({
    max: 8,
    dirs: F({
      carregador: F([0, -1, 0]), ferrolho: F([0, 0, 1]), slide: F([0, 1, 0]), gatilho: F([0, -0.8, 0.6]),
      bomba: F([1, -0.2, 0]), alavanca: F([0, 0.3, 1]), silenciador: F([1, 0, 0]), cao: F([0, 0.5, 1]), seletor: F([0, 0, 1]),
    }),
  }),
```

- [ ] **Passo 5: A bancada** — substituir `src/maps/arsenal/bench.js` inteiro:

```js file=src/maps/arsenal/bench.js
// Bancada de armas do mapa `arsenal` (Fase 4.1; docs/phases/phase-4.md, seção 4.1, "Bancada de armas"; Fase 4.1a:
// docs/superpowers/specs/2026-09-26-armas-realistas-design.md): a mesa do animador com o quadro de hardboard perfurado
// no fundo (ferramentas de modelar penduradas e a planta a lápis de cada arma presa com fita), as armas deitadas no
// tapete em fileiras com a etiqueta de fita de cada uma e, na frente, a roda de modelar com a arma escolhida no suporte
// de arame. Referências no item 13 do moodboard (QGW, QPB, QTT, QWS, QBP). Serve as duas origens da biblioteca de
// armas: tudo o que depende da arma sai do `info(id)` (a caixa, as âncoras, a planta, o comprimento); a skin da arma
// realista é a do serviço (weaponModels.setSkin: a roda, a fileira e a mão trocam juntas), a da de massinha é a skin de
// massa da 4.1 (clone dos materiais, só na roda).

import * as THREE from 'three';
import { ARSENAL } from '../../data/arsenal.js';
import { WEAPONS } from '../../data/weapons.js';
import { RNG } from '../../core/rng.js';
import { buildAnimatorDesk } from '../animatorDesk.js';
import { sculptTool, tapeStrip, wireGeometry } from '../../clay/set/propGeometry.js';
import { bakeLabelAtlas } from '../../clay/set/labelAtlas.js';
import { tapeLabelMaterial } from '../../clay/set/paperMaterials.js';
import { weaponFaction } from '../../weapons/model/recipe.js';
import { placeReference, silhouetteIoU } from '../../weapons/model/silhouette.js';
import { FABRICA, skinPorNome } from '../../weapons/skins/skin.js';
import { buildBandingWheel, buildWireStand } from './turntable.js';
import { drawPlanSheet, planSheetMaterial } from './planSheets.js';

const DEG = Math.PI / 180;
const labelLength = (aspect, L) => Math.max(L.tapeWidth * 2.2, aspect * L.textHeight + L.margin * 2);

export class ArsenalBench {
  /**
   * @param {{set:import('../../clay/set/index.js').SetLibrary, weapons:import('../../weapons/model/weaponLibrary.js').WeaponLibrary,
   *          anisotropy?:number, log?:object, precompile?:((obj:THREE.Object3D)=>Promise<unknown>)|null}} deps
   *   `precompile` compila as variantes de shader de uma instância antes de ela entrar na cena (renderer.compileAsync)
   */
  constructor({ set, weapons, anisotropy = 8, log = null, precompile = null }) {
    this.set = set;
    this.weapons = weapons;
    this.anisotropy = anisotropy;
    this.log = log;
    this.precompile = precompile;
    this.root = new THREE.Group();
    this.root.name = 'arsenal';
    this.matTop = ARSENAL.desk.mat.thickness;
    this.displays = new Map(); // id → instância deitada na fileira
    this.textures = [];
    this.labelAtlas = null;
    this.wheel = null;
    this.stand = null;
    this.weapon = null; // instância na roda
    // `skin`: a skin de massa da de massinha (a da realista é a do serviço); `faction`: null na realista.
    this.state = { id: null, faction: null, lod: 'perto', skin: null, explode: 0, anchors: false, plan: false, spin: true };
    this.skinMaterials = [];
    this.overlay = null;
    this.onChange = null; // o painel escuta (troca de arma, carga pronta, skin)
    this.selecting = Promise.resolve();
  }

  /** Ids com modelo, na ordem das fileiras. */
  get ids() {
    return ARSENAL.rows.flatMap((r) => r.ids).filter((id) => this.weapons.has(id));
  }

  async build(scene) {
    const t0 = performance.now();
    scene.add(this.root);
    this.root.add(buildAnimatorDesk(this.set, ARSENAL.desk));
    const ids = this.ids;
    // O `info` de cada arma: a caixa, as âncoras, a planta e o comprimento (na realista, o .glb, a ficha e o relatório).
    await Promise.all(ids.map((id) => this.weapons.describe(id)));
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
      const info = this.weapons.info(id);
      const col = i % D.cols;
      const row = Math.floor(i / D.cols);
      const inRow = Math.min(D.cols, ids.length - row * D.cols);
      const canvas = drawPlanSheet({
        id, info, name: WEAPONS[id]?.name ?? id, plan: info.plan, lengthU: info.lengthU,
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
        await this.precompile?.(inst);
        const b = this.weapons.info(id).bounds;
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
    this.state.id = id;
    const glb = this.weapons.source(id) === 'glb';
    // A realista não tem acento de facção (a identidade do time fica nas luvas, 4.1b); a de massinha pega a pedida ou a dela.
    this.state.faction = glb ? null : faction ?? weaponFaction(id);
    if (!this.weapons.lods(id).includes(this.state.lod)) this.state.lod = 'perto';
    const weapon = await this.weapons.instance(id, glb ? { lod: this.state.lod } : { lod: this.state.lod, faction: this.state.faction });
    await this.precompile?.(weapon);
    if (this.state.id !== id) return;
    const stand = buildWireStand(this.set, ARSENAL.stand, weapon);
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

  /**
   * Skin da arma da roda. Na realista, `value` é "fabrica" ou a chave de uma skin nomeada e a troca é no serviço (o
   * evento `skin` volta por onSkin e remonta a roda e a fileira; a mão troca sozinha); na de massinha, a chave de uma
   * skin de massa (ou "" para a massa da receita), só na roda.
   */
  setSkin(value) {
    const id = this.state.id;
    if (id && this.weapons.source(id) === 'glb') {
      this.weapons.setSkin(id, skinPorNome(id, value || FABRICA));
      return;
    }
    this.state.skin = value || null;
    this.#applySkin();
  }

  /** Skin trocada no serviço (o painel ou o console `skin`): a arma da fileira e, se estiver nela, a da roda voltam novas. */
  onSkin(id) {
    if (this.weapons.source(id) !== 'glb') return this.selecting;
    this.selecting = this.selecting.then(async () => {
      await this.#renewDisplay(id);
      if (this.state.id === id) await this.#place(id, { faction: null });
      else this.onChange?.();
    }).catch((err) => this.log?.error('bancada:', err));
    return this.selecting;
  }

  /** Troca a instância da fileira por uma nova (skin nova), no mesmo lugar. */
  async #renewDisplay(id) {
    const old = this.displays.get(id);
    if (!old) return;
    const fresh = await this.weapons.instance(id, { lod: 'perto' });
    await this.precompile?.(fresh);
    fresh.position.copy(old.position);
    fresh.rotation.copy(old.rotation);
    fresh.name = old.name;
    old.parent.add(fresh);
    old.removeFromParent();
    this.displays.set(id, fresh);
  }

  #disposeSkin() {
    for (const m of this.skinMaterials) m.dispose();
    this.skinMaterials = [];
  }

  #applySkin() {
    if (!this.weapon) return;
    this.#disposeSkin();
    // A realista já vem com os materiais da skin atual do serviço.
    if (this.weapon.userData.weapon.source === 'glb') return;
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
    const info = this.state.id ? this.weapons.info(this.state.id) : null;
    if (!this.state.plan || !info?.plan || !this.weapon) return;
    const { outline, holes } = placeReference(info, info.plan);
    const z = info.bounds.max[2] + ARSENAL.planOverlay.lift;
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

  /**
   * Silhueta lateral da arma da roda contra a planta: a de massinha mede aqui (IoU do SDF; aceite ≥ 0,8); a realista
   * traz a do Blender (relatório: com a tolerância de 1 px da foto, aceite ≥ 0,98). null sem planta.
   * @returns {{iou:number, bruto:number|null, origem:'glb'|'massinha'}|null}
   */
  measure() {
    const info = this.state.id ? this.weapons.info(this.state.id) : null;
    if (!info?.plan) return null;
    if (info.source === 'glb') return { iou: info.report.silhueta.iouTolerancia, bruto: info.report.silhueta.iouBruto, origem: 'glb' };
    return { iou: silhouetteIoU(info.recipe, info.plan, { cell: 0.1 }).iou, bruto: null, origem: 'massinha' };
  }

  /**
   * Relê do disco a arma da roda (depois de exportar do Blender) e remonta a roda e a fileira. As instâncias dessa arma
   * saem da cena antes de a biblioteca descartar as malhas (WeaponLibrary.reload) e voltam novas no fim, mesmo se a
   * releitura falhar (aí com o modelo que continuou valendo).
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
          await this.precompile?.(fresh);
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

- [ ] **Passo 6: O painel** — substituir `src/maps/arsenal/panel.js` inteiro:

```js file=src/maps/arsenal/panel.js
// Painel de fita crepe da bancada `arsenal` (Tab solta o mouse; o MatchState chama open/close pelo `map.panel`):
// escolher a arma da roda, a skin — de cor e acabamento na arma realista (a de fábrica e as nomeadas; o console `skin`
// faz as personalizadas por zona), de massa nas de massinha, que também escolhem a facção do acento — e o nível de
// detalhe; explodir as peças, mostrar as âncoras e os soquetes, sobrepor a planta, parar a roda, medir a silhueta contra
// a planta (a realista traz a medida do Blender), reler do disco depois de exportar do Blender e "segurar" a arma (o
// viewmodel com a câmera parada). Linha de informação com a origem, os triângulos e o tempo de carga ou de geração.

import { h } from '../../ui/dom.js';
import { WEAPONS } from '../../data/weapons.js';
import { CLAY_SKINS, CLAY_SKIN_IDS } from '../../data/claySkins.js';
import { SKINS_ARMA } from '../../data/skinsArma.js';
import { FABRICA, PERSONALIZADA } from '../../weapons/skins/skin.js';
import { section, segmented, slider, switchRow } from '../../debug/panelControls.js';

const FACTIONS = [
  { id: 'tr', label: 'Massa Crua' },
  { id: 'ct', label: 'Tropa do Estúdio' },
  { id: 'ambos', label: 'Dos dois lados' },
];
// O `longe` só existe na realista (o LOD2 do .glb); as de massinha têm perto (célula de 0,14 u) e mundo (0,35 u).
const LODS = [{ id: 'perto', label: 'Perto' }, { id: 'mundo', label: 'Mundo' }, { id: 'longe', label: 'Longe' }];
const pct = (v) => `${(v * 100).toFixed(1).replace('.', ',')} %`;

/**
 * @param {object} s serviços do jogo
 * @param {{bench:import('./bench.js').ArsenalBench, onClose:Function, onHold?:Function, isHolding?:()=>boolean}} deps
 *   `onHold` liga/desliga o "segurar" (o mapa cuida da câmera e do viewmodel); `isHolding` diz se está segurando
 */
export function createArsenalPanel(s, { bench, onClose, onHold = null, isHolding = () => false }) {
  const weaponSeg = segmented('Arma na roda', bench.ids.map((id) => ({ id, label: WEAPONS[id]?.name ?? id })), (id) => bench.select(id));
  const factionSeg = segmented('Facção do acento', FACTIONS, (id) => bench.setFaction(id));
  const lodSeg = segmented('Nível de detalhe', LODS, (id) => bench.setLod(id));
  const skinSelect = h('select.clay-select', { 'aria-label': 'Skin' });
  let skinKind = null; // 'glb' ou 'massinha': o jogo de opções que o seletor tem agora
  const fillSkins = (kind) => {
    if (kind === skinKind) return;
    skinKind = kind;
    skinSelect.replaceChildren(...(kind === 'glb'
      ? [
        h('option', { value: FABRICA }, 'De fábrica'),
        ...Object.entries(SKINS_ARMA).map(([key, def]) => h('option', { value: key }, def.nome)),
        h('option', { value: PERSONALIZADA, disabled: true }, 'Personalizada (pelo console: skin)'),
      ]
      : [
        h('option', { value: '' }, 'Sem skin (a massa da receita)'),
        ...CLAY_SKIN_IDS.map((id) => h('option', { value: id }, CLAY_SKINS[id].label)),
      ]));
  };
  skinSelect.addEventListener('change', () => bench.setSkin(skinSelect.value));
  const explode = slider({
    label: 'Explodir as peças', min: 0, max: 1, step: 0.01, value: 0, format: (v) => `${Math.round(v * 100)}%`,
    onInput: (v) => bench.setExplode(v),
  });
  const anchors = switchRow('Mostrar as âncoras e os soquetes (mãos, boca, ejeção, miras)', { onChange: (v) => bench.setAnchors(v) });
  const plan = switchRow('Planta por cima da silhueta', { onChange: (v) => bench.setPlanOverlay(v) });
  const spin = switchRow('Girar a roda', { checked: true, onChange: (v) => bench.setSpin(v) });
  const info = h('p.vt-note', { role: 'status' });
  const measureOut = h('p.vt-note', { role: 'status' }, 'Silhueta lateral × planta: aperte "Medir" (na de massinha trava ~1 s).');
  const measure = h('button.btn-clay.is-small', { type: 'button' }, 'Medir a silhueta');
  measure.addEventListener('click', () => {
    const t0 = performance.now();
    const m = bench.measure();
    if (!m) measureOut.textContent = 'Esta arma não tem planta.';
    else if (m.origem === 'glb') {
      measureOut.textContent = `Medida no Blender: ${pct(m.iou)} com a tolerância de 1 px da foto (bruto ${pct(m.bruto)}; aceite: ≥ 98 %).`;
    } else {
      measureOut.textContent = `IoU ${m.iou.toFixed(3)} (aceite: ≥ 0,8) · ${(performance.now() - t0).toFixed(0)} ms`;
    }
  });
  const reload = h('button.btn-clay.is-small', { type: 'button' }, 'Reler do disco');
  const reloadOut = h('p.vt-note', { role: 'status' }, 'Depois de exportar do Blender: a arma da roda e a da fileira voltam com o modelo novo.');
  reload.addEventListener('click', async () => {
    reloadOut.textContent = 'Relendo…';
    try {
      await bench.reload();
      reloadOut.textContent = `${WEAPONS[bench.state.id]?.name ?? bench.state.id} relida do disco.`;
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
      h('p.vt-note', null, 'As armas realistas saem do Blender (assets/armas/); as de massinha, das receitas em src/data/armas/. Clique na cena ou Tab/Esc para voltar à câmera.'), close),
    section('Arma', weaponSeg.el, hold, info),
    section('Aparência', h('div.vt-row', null, h('span.vt-label', null, 'Skin'), skinSelect), factionSeg.el, lodSeg.el),
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
    const glb = Boolean(st.id) && s.weaponModels.source(st.id) === 'glb';
    weaponSeg.set(st.id);
    factionSeg.el.hidden = glb;
    factionSeg.set(st.faction);
    for (const b of lodSeg.buttons) b.hidden = b.dataset.pick === 'longe' && !glb;
    lodSeg.set(st.lod);
    fillSkins(glb ? 'glb' : 'massinha');
    skinSelect.value = glb ? s.weaponModels.skinOf(st.id).chave : st.skin ?? '';
    explode.set(st.explode);
    anchors.set(st.anchors);
    plan.set(st.plan);
    spin.set(st.spin);
    hold.textContent = HOLD_LABELS[isHolding() ? 1 : 0];
    const name = WEAPONS[st.id]?.name ?? st.id;
    const row = s.weaponModels.report().find((r) => r.id === st.id && r.lod === st.lod);
    if (!row) info.textContent = 'Nenhuma arma na roda.';
    else if (glb) {
      info.textContent = `${name} (Blender): ${row.state} · ${row.triangles.toLocaleString('pt-BR')} triângulos em ${row.groups} peça(s) · carregada em ${row.ms} ms · skin ${s.weaponModels.skinOf(st.id).nome}`;
    } else {
      info.textContent = `${name} (massinha): ${row.state} · ${row.triangles.toLocaleString('pt-BR')} triângulos em ${row.groups} grupo(s) · gerada em ${row.ms} ms`;
    }
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

- [ ] **Passo 7: O mapa** — em `src/maps/arsenal/index.js`, trocar:

```js
// Mapa `arsenal` — bancada de armas da Fase 4.1 (docs/phases/phase-4.md, seção 4.1, "Bancada de armas"): a mesa do
// animador com a luz da vitrine virada em bancada de armeiro, as armas de massinha geradas das receitas deitadas em
// fileiras, a roda de modelar com a arma escolhida e o painel de fita crepe (Tab). É também o banco do aceite das
// armas: costura, boil, digitais, veios, acento, silhueta × planta, e o caminho do Blender (reler a receita).
```

por:

```js
// Mapa `arsenal` — bancada de armas da Fase 4.1 (docs/phases/phase-4.md, seção 4.1, "Bancada de armas"): a mesa do
// animador com a luz da vitrine virada em bancada de armeiro, as armas deitadas em fileiras — a realista do Blender
// (Fase 4.1a) e as de massinha das receitas —, a roda de modelar com a arma escolhida e o painel de fita crepe (Tab). É
// também o banco do aceite das armas: forma, acabamento e skins, silhueta × planta, e o caminho do Blender (reler do
// disco).
```

trocar:

```js
import { StudioRig } from '../../render/studio/studioRig.js';
```

por:

```js
import { StudioRig } from '../../render/studio/studioRig.js';
import { disposeObject3D } from '../../render/dispose.js';
```

trocar:

```js
  const bench = new ArsenalBench({ set: services.set, weapons: services.weaponModels, anisotropy: render.anisotropy, log: services.log });
  await bench.build(scene);

  const rigDef = STUDIO_RIGS[ARSENAL.rig];
  const rig = new StudioRig({
    def: rigDef, set: services.set, renderer: render.renderer, tableY: ARSENAL.desk.mat.thickness,
    floorY: ARSENAL.desk.floorY, center: new THREE.Vector3(0, 60, 0),
  }).build(scene);
  rig.setDustDensity(config.get('graphics.particles'));
```

por:

```js
  // A luz primeiro: as variantes de shader das armas compilam com as luzes da cena, antes de cada arma entrar nela.
  const rigDef = STUDIO_RIGS[ARSENAL.rig];
  const rig = new StudioRig({
    def: rigDef, set: services.set, renderer: render.renderer, tableY: ARSENAL.desk.mat.thickness,
    floorY: ARSENAL.desk.floorY, center: new THREE.Vector3(0, 60, 0),
  }).build(scene);
  rig.setDustDensity(config.get('graphics.particles'));

  const compileCamera = new THREE.PerspectiveCamera();
  const bench = new ArsenalBench({
    set: services.set, weapons: services.weaponModels, anisotropy: render.anisotropy, log: services.log,
    precompile: (obj) => render.renderer.compileAsync(obj, compileCamera, scene),
  });
  try {
    await bench.build(scene);
  } catch (err) {
    // Montagem pela metade: o matchState não recebe o mapa, então a GPU sai aqui.
    bench.dispose();
    rig.dispose();
    disposeObject3D(scene);
    throw err;
  }
```

trocar:

```js
    services.events.on(EV.RENDER_CONTEXT, ({ lost }) => {
      if (!lost) rig.bakeEnvironment();
    }),
  ];
```

por:

```js
    services.events.on(EV.RENDER_CONTEXT, ({ lost }) => {
      if (!lost) rig.bakeEnvironment();
    }),
    // Skin trocada (o painel ou o console `skin`): a arma da roda e a da fileira voltam com os materiais novos.
    services.events.on(EV.WEAPON_MODEL, ({ id, phase }) => {
      if (phase === 'skin') bench.onSkin(id);
    }),
  ];
```

e trocar:

```js
  description: 'As armas de massinha geradas das receitas: fileiras no tapete, roda de modelar, plantas a lápis e o painel (Tab).',
```

por:

```js
  description: 'A AK-47 realista do Blender e as armas de massinha das receitas: fileiras no tapete, roda de modelar, plantas a lápis e o painel (Tab).',
```

- [ ] **Passo 8: Rodar e ver passar**

Run: `node --test tests/arsenalStand.test.js`
Expected: PASS (2 testes). Suíte inteira: `npm test 2>&1 | tail -8` → `# tests 367`, `# fail 0`.

A bancada é conferida no navegador na Tarefa 18 (o jogo volta a funcionar inteiro a partir daqui: o viewmodel e a
bancada já leem o `info`).

---

### Tarefa 15: O comando `skin` e o console das armas

**Files:**
- Modify: `src/debug/weaponCommands.js`
- Test: `tests/skinCommand.test.js`

O comando da seção 6.3 do desenho: `skin` (as armas realistas com a skin atual, as skins, os acabamentos e as cores),
`skin <arma>` (a skin atual, zona por zona), `skin <arma> fabrica`, `skin <arma> <nome da skin>` e
`skin <arma> <zona>=<acabamento>:<cor>[,<cor2>] … desgaste=<0..1>` (pinta por cima da atual). A troca vai para o
serviço (D8), que avisa a roda, a fileira e a mão. O `armas` ganha a coluna da origem; o `arma` e o `viewmodel_ajuste`
deixam de falar em receita.

- [ ] **Passo 1: Testes**

```js file=tests/skinCommand.test.js
// Comando `skin` do console (Fase 4.1a; desenho, seção 6.3): lista as armas realistas com a skin atual, as skins, os
// acabamentos e as cores; mostra a skin de uma arma; troca pela de fábrica ou por uma nomeada; pinta por zona por cima
// da atual (com desgaste); recusa a arma de massinha e os erros de digitação com a mensagem certa. E o `armas` com a
// origem de cada arma e o `arma` com a mensagem de quem ainda não tem modelo.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { registerWeaponCommands } from '../src/debug/weaponCommands.js';
import { skinDeFabrica } from '../src/weapons/skins/skin.js';

/** Console mínimo com o mesmo registro do console do jogo (nome e apelidos apontam para a definição). */
function fakeConsole() {
  const commands = new Map();
  return {
    commands,
    register(def) {
      commands.set(def.name, def);
      for (const a of def.aliases ?? []) commands.set(a, def);
    },
  };
}

/** Serviços falsos: a biblioteca de armas só com o que os comandos usam (a real é testada em weaponLibraryGlb). */
function montar() {
  const skins = new Map();
  const trocas = [];
  const weaponModels = {
    ids: ['ak47', 'glock'],
    has: (id) => id === 'ak47' || id === 'glock',
    source: (id) => (id === 'ak47' ? 'glb' : id === 'glock' ? 'massinha' : null),
    skinOf: (id) => skins.get(id) ?? skinDeFabrica(id),
    setSkin: (id, skin) => {
      skins.set(id, skin);
      trocas.push([id, skin.chave]);
      return skin;
    },
    report: () => [
      { id: 'ak47', lod: 'perto', source: 'glb', state: 'pronta', triangles: 38412, ms: 180, groups: 6 },
      { id: 'glock', lod: 'perto', source: 'massinha', state: '—', triangles: 0, ms: 0, groups: 0 },
    ],
  };
  const s = {
    config: { spec: () => ({ min: 0, max: 1 }), get: () => 0, set: () => {} },
    weaponModels,
    handModels: { report: () => ({ state: 'pronta', triangles: 5200, ms: 90 }) },
    events: { emit() {} },
    localLoadout: {},
  };
  const con = fakeConsole();
  registerWeaponCommands(con, s, { goState() {}, matchState: () => null });
  return { con, s, trocas };
}

test('skin: lista as realistas, mostra, troca por nome e volta à de fábrica', () => {
  const { con, trocas } = montar();
  const skin = con.commands.get('skin');
  const lista = skin.run([]);
  assert.match(lista, /^ak47: De fábrica$/m);
  assert.match(lista, /^skins: fabrica, Anodizado Terracota, Cromo e Carbono, Madeira Clara e Aço Escovado$/m);
  assert.match(lista, /^acabamentos: oxidado, fosfatizado, /m);
  assert.match(lista, /^cores: preto, brancoTitanio, /m);
  assert.doesNotMatch(lista, /glock/, 'só as realistas');
  assert.match(skin.run(['ak47']), /^ak47 — De fábrica:\n {2}corpo: Oxidado de fábrica #303135 · desgaste 0,22$/m);
  assert.match(skin.run(['AK-47', 'Cromo', 'e', 'Carbono']), /^ak47 — Cromo e Carbono:/);
  assert.deepEqual(trocas.at(-1), ['ak47', 'cromoECarbono']);
  skin.run(['ak47', 'fabrica']);
  assert.deepEqual(trocas.at(-1), ['ak47', 'fabrica']);
  assert.deepEqual(skin.complete(0, ''), ['ak47']);
  assert.ok(skin.complete(1, '').includes('cromoECarbono') && skin.complete(1, '').includes('corpo='));
});

test('skin: pinta por zona por cima da atual, com desgaste; recusa a de massinha e os erros de digitação', () => {
  const { con, s } = montar();
  const skin = con.commands.get('skin');
  const out = skin.run(['ak47', 'corpo=anodizado:terracota', 'desgaste=0,4']);
  assert.match(out, /^ak47 — Personalizada:/);
  assert.match(out, /corpo: Anodizado #C8553D · desgaste 0,4$/m);
  assert.match(out, /guarnicao: Madeira #A4673F,#794224 · desgaste 0,18$/m, 'as outras zonas ficam');
  assert.equal(s.weaponModels.skinOf('ak47').chave, 'personalizada');
  assert.throws(() => skin.run(['glock', 'fabrica']), /glock não é uma arma realista \(skins de acabamento só nas feitas no Blender: ak47\)/);
  assert.throws(() => skin.run(['ak47', 'Dourada']), /skin desconhecida: Dourada/);
  assert.throws(() => skin.run(['ak47', 'cano=fosco:preto']), /zona desconhecida: cano/);
  assert.throws(() => skin.run(['ak47', 'interno=fosco:preto']), /interno só aceita acabamento de metal/);
});

test('armas: a origem de cada uma; arma: a mensagem de quem ainda não tem modelo', () => {
  const { con } = montar();
  const armas = con.commands.get('armas').run([]);
  assert.match(armas, /^arma\s+origem\s+nível/);
  assert.match(armas, /^ak47\s+glb\s+perto\s+pronta\s+38\.412/m);
  assert.match(armas, /^glock\s+massinha\s+perto\s+—/m);
  assert.throws(() => con.commands.get('arma').run(['usps']), /usps ainda não tem modelo \(tem: ak47, glock\)/);
});
```

Run: `node --test tests/skinCommand.test.js`
Expected: FAIL — `Cannot read properties of undefined (reading 'run')` (não há comando `skin`).

- [ ] **Passo 2: Os comandos** — em `src/debug/weaponCommands.js`, trocar:

```js
// Comandos do console da Fase 4.1 (docs/phases/phase-4.md, seção 4.1, "Console e dados"): o viewmodel como no CS
// (viewmodel_fov, viewmodel_offset_x/y/z, viewmodel_presetpos, r_viewmodel), a braçadeira de teste (cl_bracadeira), a
// bancada de armas (arsenal, arma <id>), a lista das receitas geradas (armas) e o ajuste ao vivo da posição de cada
// categoria na mão (viewmodel_ajuste, para afinar src/data/viewmodel.js). Falam com a mesma config, a mesma biblioteca
// de armas e o mesmo viewmodel que o jogo usa.

import { EV } from '../core/events.js';
import { VIEWMODEL } from '../data/viewmodel.js';
import { WEAPONS, resolveWeaponId } from '../data/weapons.js';
```

por:

```js
// Comandos do console da Fase 4.1 (docs/phases/phase-4.md, seção 4.1, "Console e dados"): o viewmodel como no CS
// (viewmodel_fov, viewmodel_offset_x/y/z, viewmodel_presetpos, r_viewmodel), a braçadeira de teste (cl_bracadeira), a
// bancada de armas (arsenal, arma <id>), a lista das armas com a origem (armas: o .glb do Blender ou a receita de
// massinha), o ajuste ao vivo da posição de cada categoria na mão (viewmodel_ajuste, para afinar src/data/viewmodel.js)
// e, na 4.1a, as skins de cor e acabamento das armas realistas (skin). Falam com a mesma config, a mesma biblioteca de
// armas e o mesmo viewmodel que o jogo usa.

import { EV } from '../core/events.js';
import { ACABAMENTOS } from '../data/acabamentos.js';
import { ZONAS } from '../data/armasReais.js';
import { CORES_SKIN } from '../data/coresSkin.js';
import { SKINS_ARMA } from '../data/skinsArma.js';
import { VIEWMODEL } from '../data/viewmodel.js';
import { WEAPONS, resolveWeaponId } from '../data/weapons.js';
import { FABRICA, aplicarZonas, descreverSkin, lerArgumentosSkin, skinPorNome } from '../weapons/skins/skin.js';
```

trocar:

```js
    name: 'arsenal', aliases: ['bancada'], help: 'abre a bancada de armas (as armas de massinha das receitas, Tab para o painel)',
```

por:

```js
    name: 'arsenal', aliases: ['bancada'], help: 'abre a bancada de armas (a AK realista e as de massinha; Tab para o painel)',
```

trocar:

```js
      if (!s.weaponModels.has(id)) throw new Error(`${name} ainda não tem receita de massinha (tem: ${ids.join(', ')})`);
```

por:

```js
      if (!s.weaponModels.has(id)) throw new Error(`${name} ainda não tem modelo (tem: ${ids.join(', ')})`);
```

trocar:

```js
  reg({
    name: 'armas', help: 'receitas de massinha: estado, triângulos e tempo de geração por nível; e as mãos',
    run: () => {
      const head = `${'arma'.padEnd(8)}${'nível'.padEnd(7)}${'estado'.padEnd(9)}${'triângulos'.padStart(11)}${'ms'.padStart(7)}${'grupos'.padStart(8)}`;
      const rows = s.weaponModels.report().map((r) =>
        `${r.id.padEnd(8)}${r.lod.padEnd(7)}${r.state.padEnd(9)}${r.triangles.toLocaleString('pt-BR').padStart(11)}${String(r.ms).padStart(7)}${String(r.groups).padStart(8)}`);
```

por:

```js
  reg({
    name: 'armas', help: 'armas com modelo: a origem (glb do Blender ou massinha), o estado, os triângulos e o tempo por nível; e as mãos',
    run: () => {
      const head = `${'arma'.padEnd(8)}${'origem'.padEnd(10)}${'nível'.padEnd(7)}${'estado'.padEnd(12)}${'triângulos'.padStart(11)}${'ms'.padStart(7)}${'peças'.padStart(7)}`;
      const rows = s.weaponModels.report().map((r) =>
        `${r.id.padEnd(8)}${r.source.padEnd(10)}${r.lod.padEnd(7)}${r.state.padEnd(12)}${r.triangles.toLocaleString('pt-BR').padStart(11)}${String(r.ms).padStart(7)}${String(r.groups).padStart(7)}`);
```

trocar:

```js
  reg({
    name: 'viewmodel_ajuste',
```

por:

```js
  // Skins de cor e acabamento das armas realistas (Fase 4.1a; desenho, seção 6.3). A troca vai para o serviço de armas
  // (weaponModels.setSkin), que avisa a roda da bancada, a fileira e a mão (EV.WEAPON_MODEL, phase 'skin').
  const realistas = () => s.weaponModels.ids.filter((id) => s.weaponModels.source(id) === 'glb');
  const linhasDaSkin = (id, skin) => [`${id} — ${skin.nome}:`, ...descreverSkin(skin).map((l) => `  ${l}`)].join('\n');
  reg({
    name: 'skin',
    usage: '[<arma> [fabrica | <nome da skin> | <zona>=<acabamento>:<cor>[,<cor2>] … desgaste=<0..1>]]',
    help: 'skin de cor e acabamento das armas realistas: mostra, troca pela de fábrica ou por uma nomeada, ou pinta por zona',
    complete: (index) => (index === 0
      ? realistas()
      : [FABRICA, ...Object.keys(SKINS_ARMA), ...ZONAS.map((z) => `${z}=`), 'desgaste=']),
    run: ([nome, ...args]) => {
      const reais = realistas();
      if (!nome) {
        return [
          ...reais.map((id) => `${id}: ${s.weaponModels.skinOf(id).nome}`),
          `skins: fabrica, ${Object.values(SKINS_ARMA).map((k) => k.nome).join(', ')}`,
          `acabamentos: ${Object.keys(ACABAMENTOS).join(', ')}`,
          `cores: ${Object.keys(CORES_SKIN).join(', ')} (ou #RRGGBB)`,
          'uso: skin <arma> [fabrica | <nome> | <zona>=<acabamento>:<cor>[,<cor2>] … desgaste=<0..1>]',
        ].join('\n');
      }
      const id = resolveWeaponId(nome) ?? nome;
      if (!reais.includes(id)) throw new Error(`${nome} não é uma arma realista (skins de acabamento só nas feitas no Blender: ${reais.join(', ')})`);
      const pedido = lerArgumentosSkin(args);
      if (pedido.tipo === 'mostrar') return linhasDaSkin(id, s.weaponModels.skinOf(id));
      const skin = pedido.tipo === 'nome' ? skinPorNome(id, pedido.nome) : aplicarZonas(id, s.weaponModels.skinOf(id), pedido);
      s.weaponModels.setSkin(id, skin);
      return linhasDaSkin(id, skin);
    },
  });

  reg({
    name: 'viewmodel_ajuste',
```

e trocar:

```js
      if (!cat) throw new Error('segure uma arma com receita em primeira pessoa primeiro');
```

por:

```js
      if (!cat) throw new Error('segure uma arma em primeira pessoa primeiro');
```

- [ ] **Passo 3: Rodar e ver passar**

Run: `node --test tests/skinCommand.test.js`
Expected: PASS (3 testes). Suíte inteira: `npm test 2>&1 | tail -8` → `# tests 370`, `# fail 0`.

---

### Tarefa 16: A receita de massinha da AK sai

**Files:**
- Delete: `src/data/armas/ak47.js`
- Modify: `src/data/armas/index.js`, `src/data/viewmodel.js`, `tests/weaponRecipes.test.js`

A troca em etapas da seção 8.2 do desenho: na 4.1a sai a receita de massinha da AK (a planta antiga já saiu na Tarefa
1, quando a `ak47.json` virou a ficha do tipo 3); as outras seis continuam de massinha até a 4.1c e a 4.1d.

- [ ] **Passo 1: Tirar a receita**

```bash
cd "/c/Users/T-Gamer/Desktop/game tiro/trabalho-4.1a" && rm src/data/armas/ak47.js
```

Em `src/data/armas/index.js`, trocar:

```js
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

por:

```js
// gerador (src/weapons/model/); a ordem aqui é a do comando `armas`.
// Na troca para as armas realistas (docs/superpowers/specs/2026-09-26-armas-realistas-design.md, seção 8.2), cada arma
// refeita no Blender sai daqui e entra em src/data/armasReais.js: a AK-47 na 4.1a; a Glock-18, a M4A4 e a faca na
// 4.1c; a AWP, a Nova e a P90 na 4.1d, quando esta pasta e o gerador de massinha das armas saem de vez.

import glock from './glock.js';
import m4a4 from './m4a4.js';
import awp from './awp.js';
import nova from './nova.js';
import p90 from './p90.js';
import knife from './knife.js';

export const ARMAS = Object.freeze({ glock, m4a4, awp, nova, p90, knife });
```

Em `src/data/viewmodel.js`, trocar:

```js
  // Categoria de cada arma com receita (as da 4.4 entram aqui junto com a receita) e, quando a silhueta pede, um ajuste
  // fino somado à posição da categoria (`nudge`, u no referencial da câmera): a alça de transporte da M4A4 fica mais
  // alta que a tampa da AK, então a M4 desce um pouco para não tapar o lado direito da tela.
```

por:

```js
  // Categoria de cada arma com modelo — a receita de massinha ou o .glb do Blender (as da 4.4 entram aqui junto com o
  // modelo) — e, quando a silhueta pede, um ajuste fino somado à posição da categoria (`nudge`, u no referencial da
  // câmera): a alça de transporte da M4A4 fica mais alta que a tampa da AK, então a M4 desce um pouco para não tapar o
  // lado direito da tela.
```

- [ ] **Passo 2: Os testes das receitas com as seis** — em `tests/weaponRecipes.test.js`, trocar:

```js
// Testes das receitas das armas de massinha (Fase 4.1; docs/phases/phase-4.md, seção 4.1, "Testes"): as sete validam;
```

por:

```js
// Testes das receitas das armas de massinha (Fase 4.1; docs/phases/phase-4.md, seção 4.1, "Testes"): as seis que ainda
// são de massinha validam (a AK-47 virou a arma realista do Blender na 4.1a);
```

trocar:

```js
import { ARMAS } from '../src/data/armas/index.js';
```

por:

```js
import { ARMAS } from '../src/data/armas/index.js';
import { ARMAS_REAIS } from '../src/data/armasReais.js';
```

trocar:

```js
const IDS = ['glock', 'ak47', 'm4a4', 'awp', 'nova', 'p90', 'knife'];
```

por:

```js
const IDS = ['glock', 'm4a4', 'awp', 'nova', 'p90', 'knife'];
```

trocar:

```js
  glock: { faction: 'tr', clays: ['grafite', 'grafiteClaro'], groups: ['corpo', 'slide', 'carregador', 'gatilho'], length: 7.3 },
  ak47: { faction: 'tr', clays: ['grafite', 'madeira', 'madeiraEscura'], groups: ['corpo', 'carregador', 'ferrolho', 'gatilho'], length: 34.6 },
```

por:

```js
  glock: { faction: 'tr', clays: ['grafite', 'grafiteClaro'], groups: ['corpo', 'slide', 'carregador', 'gatilho'], length: 7.3 },
```

trocar:

```js
// A planta da AK virou a ficha da AK-47 tipo 3 realista (4.1a); a receita de massinha dela (tipo II) não se compara mais.
const COM_PLANTA = IDS.filter((x) => x !== 'knife' && x !== 'ak47');
```

por:

```js
const COM_PLANTA = IDS.filter((x) => x !== 'knife');
```

trocar:

```js
test('receitas: as sete estão no registro, validam e são das armas da tabela', () => {
```

por:

```js
test('receitas: as seis estão no registro, validam e são das armas da tabela', () => {
```

e trocar:

```js
  for (const id of Object.keys(VIEWMODEL.weapons)) assert.ok(ARMAS[id], `${id}: categoria sem receita`);
```

por:

```js
  for (const id of Object.keys(VIEWMODEL.weapons)) assert.ok(ARMAS[id] || ARMAS_REAIS[id], `${id}: categoria sem modelo`);
```

- [ ] **Passo 3: Rodar e ver passar**

Run: `node --test tests/weaponRecipes.test.js tests/viewmodel.test.js tests/weaponLibraryGlb.test.js`
Expected: PASS (8 + 9 + 5 testes). Suíte inteira: `npm test 2>&1 | tail -8` → `# tests 370`, `# fail 0`.

Conferir que nada mais aponta para a receita que saiu:

Run: `grep -rn "data/armas/ak47\|ARMAS\.ak47\|from './ak47.js'" src tests tools --include=*.js --include=*.mjs`
Expected: nenhuma linha.

---

### Tarefa 17: Regras, documentos e memória

**Files:**
- Modify: `CLAUDE.md`, `CLAUDE.md.md`, `docs/phases/phase-4.md`, `docs/PROGRESS.md`
- Conferir: a memória `massacre-workflow-rules` (fora do repositório)

A seção 8.3 do desenho: a exceção das regras 3 e 4 e da linha "100% gerado em código" da tabela de paridade, só para armas e mãos; a seção 0.7 reescrita (estilo de fábrica, construção, carregador, cápsulas, luneta, inspeção, faca, granadas, mãos, skins temáticas); a 0.12 (viewmodel suave com a opção stop-motion); a 0.13 (loja com a arma realista na mini-bancada, ícones do killfeed da silhueta do `.glb`, o kit de massinha e o boil fora das armas); a 0.15 (skins de cor e acabamento) e os textos das Fases 4, 5 e 11. As seções 0.3 a 0.15 são iguais nos dois arquivos: os mesmos pares valem para `CLAUDE.md` e para `CLAUDE.md.md` (aplicar em cada um); os das fases só existem no `CLAUDE.md.md`. O relatório da 4.1a no `docs/PROGRESS.md` e o ✅ da tabela entram na Tarefa 19, com os números do aceite.

- [ ] **Passo 1: As regras (nos dois arquivos)**

Em `CLAUDE.md`, trocar:

```md
| 100% gerado em código: sem arquivos de imagem, modelo ou áudio | Igual. Geometria, texturas (canvas/shader), personagens, armas, mapas, música e efeitos sonoros são procedurais |
```

por:

```md
| 100% gerado em código: sem arquivos de imagem, modelo ou áudio | Igual, com uma exceção decidida em 2026-09-26: **as armas e as mãos** (luvas e mangas) são modelos realistas construídos por scripts Python nossos no Blender (`tools/blender/armas/`) e entram no jogo como `.glb` + texturas `.webp` assadas (`assets/`). Nada é baixado de terceiros; o resto — geometria, texturas (canvas/shader), personagens, mapas, música e efeitos sonoros — continua procedural |
```

Em `CLAUDE.md.md`, trocar:

```md
| 100% gerado em código: sem arquivos de imagem, modelo ou áudio | Igual. Geometria, texturas (canvas/shader), personagens, armas, mapas, música e efeitos sonoros são procedurais |
```

por:

```md
| 100% gerado em código: sem arquivos de imagem, modelo ou áudio | Igual, com uma exceção decidida em 2026-09-26: **as armas e as mãos** (luvas e mangas) são modelos realistas construídos por scripts Python nossos no Blender (`tools/blender/armas/`) e entram no jogo como `.glb` + texturas `.webp` assadas (`assets/`). Nada é baixado de terceiros; o resto — geometria, texturas (canvas/shader), personagens, mapas, música e efeitos sonoros — continua procedural |
```

Em `CLAUDE.md`, trocar:

```md
3. **Design e estética em primeiro lugar.** Cada elemento visível (arma, boneco, mapa, HUD, menu, efeito, fonte) precisa parecer massinha de modelar filmada em stop-motion. Nada de visual genérico de "jogo de programador".
```

por:

```md
3. **Design e estética em primeiro lugar.** Cada elemento visível (boneco, mapa, HUD, menu, efeito, fonte) precisa parecer massinha de modelar filmada em stop-motion. Nada de visual genérico de "jogo de programador". **Exceção (2026-09-26): as armas e as mãos que as seguram são realistas** — metal, madeira e polímero de fábrica, muito detalhados e fiéis à arma real em tamanho e forma —, como adereços de metal em miniatura feitos pelo aderecista do estúdio (seção 0.7); as skins delas são de cor e acabamento (seção 0.15).
```

Em `CLAUDE.md.md`, trocar:

```md
3. **Design e estética em primeiro lugar.** Cada elemento visível (arma, boneco, mapa, HUD, menu, efeito, fonte) precisa parecer massinha de modelar filmada em stop-motion. Nada de visual genérico de "jogo de programador".
```

por:

```md
3. **Design e estética em primeiro lugar.** Cada elemento visível (boneco, mapa, HUD, menu, efeito, fonte) precisa parecer massinha de modelar filmada em stop-motion. Nada de visual genérico de "jogo de programador". **Exceção (2026-09-26): as armas e as mãos que as seguram são realistas** — metal, madeira e polímero de fábrica, muito detalhados e fiéis à arma real em tamanho e forma —, como adereços de metal em miniatura feitos pelo aderecista do estúdio (seção 0.7); as skins delas são de cor e acabamento (seção 0.15).
```

Em `CLAUDE.md`, trocar:

```md
4. **Tudo procedural.** Sem baixar imagens, GLB, fontes decorativas ou áudio. Fontes do sistema/Google Fonts só como base; letreiros decorativos são geometria de massinha.
```

por:

```md
4. **Tudo procedural.** Sem baixar imagens, GLB, fontes decorativas ou áudio. Fontes do sistema/Google Fonts só como base; letreiros decorativos são geometria de massinha. **Exceção (2026-09-26), só para armas e mãos:** os modelos são construídos por scripts Python nossos no Blender (`tools/blender/armas/`, a partir de números medidos em fotos de licença livre — nenhum arquivo de terceiros entra no projeto) e exportados como `.glb` + `.webp` em `assets/`; qualquer outro modelo em arquivo precisa de nova decisão do usuário.
```

Em `CLAUDE.md.md`, trocar:

```md
4. **Tudo procedural.** Sem baixar imagens, GLB, fontes decorativas ou áudio. Fontes do sistema/Google Fonts só como base; letreiros decorativos são geometria de massinha.
```

por:

```md
4. **Tudo procedural.** Sem baixar imagens, GLB, fontes decorativas ou áudio. Fontes do sistema/Google Fonts só como base; letreiros decorativos são geometria de massinha. **Exceção (2026-09-26), só para armas e mãos:** os modelos são construídos por scripts Python nossos no Blender (`tools/blender/armas/`, a partir de números medidos em fotos de licença livre — nenhum arquivo de terceiros entra no projeto) e exportados como `.glb` + `.webp` em `assets/`; qualquer outro modelo em arquivo precisa de nova decisão do usuário.
```

Em `CLAUDE.md`, trocar:

```md
**Estilo das armas de massinha** (cada arma tem modelo próprio, gerado em código):
- Silhueta fiel à arma real, mas **esculpida à mão**: bordas arredondadas, leve assimetria, marcas de ferramenta de modelar, impressões digitais visíveis de perto.
- Materiais: massinha de cores diferentes por peça (coronha "madeira" em massa marrom com veios riscados a palito, corpo em massa cinza-grafite, detalhes em massa colorida).
- **Carregador** é um "pão de massa" que o boneco arranca e aperta de volta na recarga. **Cápsulas** ejetadas são bolinhas de massa amarela que quicam e grudam no chão.
- **Luneta da AWP/Scout:** a visão pela luneta é um **anel de massinha** com retícula de fio de arame esticado; ao mirar, o mundo aparece com leve distorção de lente de vidro barato e poeira.
- **Inspeção (tecla F):** o boneco gira a arma e mostra a marca do dedo do "animador" nela.
- **Faca:** espátula de modelar afiada. Herda da katana da referência: segurar o botão direito **bloqueia** projéteis de frente (com durabilidade) e um bloqueio no tempo certo faz **parry** (devolve o tiro e atordoa). Barra de carga que libera um **dash de execução**.
- **Granadas:** HE é uma bola de massa com pavio de barbante (explode em respingos); Flash é massa branca brilhante que "estoura" a tela em branco-massinha; Smoke solta nuvem de algodão de set (fumaça volumétrica fake com sprites em camadas); Molotov é pote de tinta com pano em chamas (fogo de papel celofane laranja animado em stop-motion). Granadas quicam com física e têm arremesso com carga (curto/médio/longo), como na referência.
```

por:

```md
**Estilo das armas** (decisão de 2026-09-26; desenho em `docs/superpowers/specs/2026-09-26-armas-realistas-design.md`):
- **Realistas, de fábrica, tipo CS2:** a variante real escolhida na ficha de fidelidade de cada arma, nas medidas reais, com todas as peças visíveis (pinos, rebites, parafusos, molas, miras, serrilhas, frestas entre peças) e marcações genéricas estampadas (regra 9: nenhum logotipo nem nome de fabricante). O material segue a peça real — aço oxidado ou fosfatizado, alumínio anodizado, polímero texturizado, madeira envernizada, baquelite, borracha, aço polido nas peças internas — com desgaste leve só onde a mão e o uso encostam. São adereços de metal em miniatura feitos pelo aderecista do estúdio, dentro do mundo de massinha.
- **Fidelidade com número:** ficha por arma (variante, medidas oficiais com a fonte, contornos medidos com a régua sobre fotos de licença livre); o `construir` do Blender só exporta com as medidas-chave a ±1 % e a silhueta de lado ≥ 98 % da foto.
- **Construção:** um script Python por arma no Blender (`tools/blender/armas/`), o modelo alto assado no de jogo (normal, sombra de contato, borda, variações), três níveis de detalhe, zonas de material (`corpo`, `guarnicao`, `carregador`, `detalhes`, `interno`), soquetes (boca, ejeção, carregador, miras, mãos) e peças móveis com o pivô real. **Sem boil** nas armas, mãos, carregadores, cápsulas, granadas e lunetas.
- **Carregador** de metal ou polímero de verdade, que o boneco tira e põe de volta na recarga. **Cápsulas** de latão que quicam e param no chão, amassando de leve a massinha do cenário.
- **Luneta da AWP/Scout:** a luneta real, com a lente, a retícula gravada e a sombra da ocular ao mirar.
- **Inspeção (tecla F):** o boneco gira a arma e aparece, sutil, a marca do dedo do "animador" no metal, visível no reflexo.
- **Faca:** faca de combate realista, de lâmina fixa. Herda da katana da referência: segurar o botão direito **bloqueia** projéteis de frente (com durabilidade) e um bloqueio no tempo certo faz **parry** (devolve o tiro e atordoa). Barra de carga que libera um **dash de execução**.
- **Granadas:** reais (fragmentação, atordoante, fumaça, molotov de garrafa com pano, incendiária e decoy), com os efeitos de estúdio: a explosão em respingos de massa, a flash que "estoura" a tela em branco-massinha, a nuvem de algodão de set (fumaça volumétrica fake com sprites em camadas), o fogo de papel celofane laranja animado em stop-motion. Quicam com física e têm arremesso com carga (curto/médio/longo), como na referência.
- **Mãos:** luva tática de 5 dedos com a manga de tecido na cor do time (e a braçadeira), com a empunhadura resolvida por arma: nenhum dedo atravessando a arma nem flutuando.
- **Skins temáticas (futuro):** caneta, lápis, skate, arma de água e o que vier trocam o modelo inteiro no mesmo pipeline, com os mesmos soquetes, zonas e peças móveis da arma base (a espátula, a bola de massa, o pote de tinta, o pão de massa, as bolinhas amarelas e o anel de massinha da versão anterior ficam como ideias delas).
```

Em `CLAUDE.md.md`, trocar:

```md
**Estilo das armas de massinha** (cada arma tem modelo próprio, gerado em código):
- Silhueta fiel à arma real, mas **esculpida à mão**: bordas arredondadas, leve assimetria, marcas de ferramenta de modelar, impressões digitais visíveis de perto.
- Materiais: massinha de cores diferentes por peça (coronha "madeira" em massa marrom com veios riscados a palito, corpo em massa cinza-grafite, detalhes em massa colorida).
- **Carregador** é um "pão de massa" que o boneco arranca e aperta de volta na recarga. **Cápsulas** ejetadas são bolinhas de massa amarela que quicam e grudam no chão.
- **Luneta da AWP/Scout:** a visão pela luneta é um **anel de massinha** com retícula de fio de arame esticado; ao mirar, o mundo aparece com leve distorção de lente de vidro barato e poeira.
- **Inspeção (tecla F):** o boneco gira a arma e mostra a marca do dedo do "animador" nela.
- **Faca:** espátula de modelar afiada. Herda da katana da referência: segurar o botão direito **bloqueia** projéteis de frente (com durabilidade) e um bloqueio no tempo certo faz **parry** (devolve o tiro e atordoa). Barra de carga que libera um **dash de execução**.
- **Granadas:** HE é uma bola de massa com pavio de barbante (explode em respingos); Flash é massa branca brilhante que "estoura" a tela em branco-massinha; Smoke solta nuvem de algodão de set (fumaça volumétrica fake com sprites em camadas); Molotov é pote de tinta com pano em chamas (fogo de papel celofane laranja animado em stop-motion). Granadas quicam com física e têm arremesso com carga (curto/médio/longo), como na referência.
```

por:

```md
**Estilo das armas** (decisão de 2026-09-26; desenho em `docs/superpowers/specs/2026-09-26-armas-realistas-design.md`):
- **Realistas, de fábrica, tipo CS2:** a variante real escolhida na ficha de fidelidade de cada arma, nas medidas reais, com todas as peças visíveis (pinos, rebites, parafusos, molas, miras, serrilhas, frestas entre peças) e marcações genéricas estampadas (regra 9: nenhum logotipo nem nome de fabricante). O material segue a peça real — aço oxidado ou fosfatizado, alumínio anodizado, polímero texturizado, madeira envernizada, baquelite, borracha, aço polido nas peças internas — com desgaste leve só onde a mão e o uso encostam. São adereços de metal em miniatura feitos pelo aderecista do estúdio, dentro do mundo de massinha.
- **Fidelidade com número:** ficha por arma (variante, medidas oficiais com a fonte, contornos medidos com a régua sobre fotos de licença livre); o `construir` do Blender só exporta com as medidas-chave a ±1 % e a silhueta de lado ≥ 98 % da foto.
- **Construção:** um script Python por arma no Blender (`tools/blender/armas/`), o modelo alto assado no de jogo (normal, sombra de contato, borda, variações), três níveis de detalhe, zonas de material (`corpo`, `guarnicao`, `carregador`, `detalhes`, `interno`), soquetes (boca, ejeção, carregador, miras, mãos) e peças móveis com o pivô real. **Sem boil** nas armas, mãos, carregadores, cápsulas, granadas e lunetas.
- **Carregador** de metal ou polímero de verdade, que o boneco tira e põe de volta na recarga. **Cápsulas** de latão que quicam e param no chão, amassando de leve a massinha do cenário.
- **Luneta da AWP/Scout:** a luneta real, com a lente, a retícula gravada e a sombra da ocular ao mirar.
- **Inspeção (tecla F):** o boneco gira a arma e aparece, sutil, a marca do dedo do "animador" no metal, visível no reflexo.
- **Faca:** faca de combate realista, de lâmina fixa. Herda da katana da referência: segurar o botão direito **bloqueia** projéteis de frente (com durabilidade) e um bloqueio no tempo certo faz **parry** (devolve o tiro e atordoa). Barra de carga que libera um **dash de execução**.
- **Granadas:** reais (fragmentação, atordoante, fumaça, molotov de garrafa com pano, incendiária e decoy), com os efeitos de estúdio: a explosão em respingos de massa, a flash que "estoura" a tela em branco-massinha, a nuvem de algodão de set (fumaça volumétrica fake com sprites em camadas), o fogo de papel celofane laranja animado em stop-motion. Quicam com física e têm arremesso com carga (curto/médio/longo), como na referência.
- **Mãos:** luva tática de 5 dedos com a manga de tecido na cor do time (e a braçadeira), com a empunhadura resolvida por arma: nenhum dedo atravessando a arma nem flutuando.
- **Skins temáticas (futuro):** caneta, lápis, skate, arma de água e o que vier trocam o modelo inteiro no mesmo pipeline, com os mesmos soquetes, zonas e peças móveis da arma base (a espátula, a bola de massa, o pote de tinta, o pão de massa, as bolinhas amarelas e o anel de massinha da versão anterior ficam como ideias delas).
```

Em `CLAUDE.md`, trocar:

```md
- **Animação stop-motion:** todas as animações de personagem e viewmodel rodam "em dois" (12 poses/s) com leve variação de forma a cada pose ("boil"), enquanto a câmera e o input continuam a 60+ FPS. Squash & stretch em pulo, pouso, dano e morte.
```

por:

```md
- **Animação stop-motion:** as animações dos personagens rodam "em dois" (12 poses/s) com leve variação de forma a cada pose ("boil"), enquanto a câmera e o input continuam a 60+ FPS. Squash & stretch em pulo, pouso, dano e morte. **O viewmodel (a arma e as mãos em primeira pessoa) anima suave, a 60+ FPS e sem boil** (decisão de 2026-09-26), com a opção "viewmodel em stop-motion" nas configurações: a mesma animação amostrada a 12 poses/s. O "em dois" continua nos bonecos em terceira pessoa, na killcam e nos menus.
```

Em `CLAUDE.md.md`, trocar:

```md
- **Animação stop-motion:** todas as animações de personagem e viewmodel rodam "em dois" (12 poses/s) com leve variação de forma a cada pose ("boil"), enquanto a câmera e o input continuam a 60+ FPS. Squash & stretch em pulo, pouso, dano e morte.
```

por:

```md
- **Animação stop-motion:** as animações dos personagens rodam "em dois" (12 poses/s) com leve variação de forma a cada pose ("boil"), enquanto a câmera e o input continuam a 60+ FPS. Squash & stretch em pulo, pouso, dano e morte. **O viewmodel (a arma e as mãos em primeira pessoa) anima suave, a 60+ FPS e sem boil** (decisão de 2026-09-26), com a opção "viewmodel em stop-motion" nas configurações: a mesma animação amostrada a 12 poses/s. O "em dois" continua nos bonecos em terceira pessoa, na killcam e nos menus.
```

Em `CLAUDE.md`, trocar:

```md
- **Loja (B):** roda radial estilo CS, com cada arma de massinha girando em 3D numa mini-bancada; categorias, preços, atalhos numéricos, compra rápida e loadouts salvos.
```

por:

```md
- **Loja (B):** roda radial estilo CS, com cada arma realista girando em 3D numa mini-bancada de armeiro; categorias, preços, atalhos numéricos, compra rápida e loadouts salvos.
```

Em `CLAUDE.md.md`, trocar:

```md
- **Loja (B):** roda radial estilo CS, com cada arma de massinha girando em 3D numa mini-bancada; categorias, preços, atalhos numéricos, compra rápida e loadouts salvos.
```

por:

```md
- **Loja (B):** roda radial estilo CS, com cada arma realista girando em 3D numa mini-bancada de armeiro; categorias, preços, atalhos numéricos, compra rápida e loadouts salvos.
```

Em `CLAUDE.md`, trocar:

```md
- **Killfeed:** ícones de arma em massinha achatada; headshot = marca de digital vermelha.
```

por:

```md
- **Killfeed:** ícones de arma gerados da silhueta de lado do `.glb` de cada arma, achatados como um recorte de massinha; headshot = marca de digital vermelha.
```

Em `CLAUDE.md.md`, trocar:

```md
- **Killfeed:** ícones de arma em massinha achatada; headshot = marca de digital vermelha.
```

por:

```md
- **Killfeed:** ícones de arma gerados da silhueta de lado do `.glb` de cada arma, achatados como um recorte de massinha; headshot = marca de digital vermelha.
```

Em `CLAUDE.md`, trocar:

```md
Personagens e armas são montados com esse kit.
```

por:

```md
Os personagens são montados com esse kit (as armas e as mãos são realistas, feitas no Blender — seção 0.7).
```

Em `CLAUDE.md.md`, trocar:

```md
Personagens e armas são montados com esse kit.
```

por:

```md
Os personagens são montados com esse kit (as armas e as mãos são realistas, feitas no Blender — seção 0.7).
```

Em `CLAUDE.md`, trocar:

```md
- **Boil de stop-motion:** deslocamento de vértice por ruído 3D cuja seed muda **a cada 1/12 s**, com amplitude pequena (~0,3–0,6% do tamanho do objeto). A seed fica congelada entre as poses, como massa que o animador tocou.
```

por:

```md
- **Boil de stop-motion:** deslocamento de vértice por ruído 3D cuja seed muda **a cada 1/12 s**, com amplitude pequena (~0,3–0,6% do tamanho do objeto). A seed fica congelada entre as poses, como massa que o animador tocou. Nunca nas armas, nas mãos, nos carregadores, nas cápsulas, nas granadas e nas lunetas (seção 0.7), que ficam paradas.
```

Em `CLAUDE.md.md`, trocar:

```md
- **Boil de stop-motion:** deslocamento de vértice por ruído 3D cuja seed muda **a cada 1/12 s**, com amplitude pequena (~0,3–0,6% do tamanho do objeto). A seed fica congelada entre as poses, como massa que o animador tocou.
```

por:

```md
- **Boil de stop-motion:** deslocamento de vértice por ruído 3D cuja seed muda **a cada 1/12 s**, com amplitude pequena (~0,3–0,6% do tamanho do objeto). A seed fica congelada entre as poses, como massa que o animador tocou. Nunca nas armas, nas mãos, nos carregadores, nas cápsulas, nas granadas e nas lunetas (seção 0.7), que ficam paradas.
```

Em `CLAUDE.md`, trocar:

```md
- **Skins de arma:** padrões procedurais de massinha desbloqueáveis por nível e conquista: marmorizado, glitter, massa de escola desbotada, neon que brilha no escuro, "massa misturada" de criança, madeira falsa, camuflagem de massinha, ouro (Gun Game). Aplicadas pelo mesmo ClayMaterial com parâmetros.
```

por:

```md
- **Skins de arma:** de cor e acabamento, como as pinturas dos carros do Rocket League: por zona da arma (corpo, guarnição, carregador, detalhes, interno), um acabamento (oxidado de fábrica, fosfatizado, fosco, acetinado, brilhante, metálico, perolado, anodizado, aço escovado, cromado, cerakote, fibra de carbono, madeira, polímero texturizado, borracha), uma cor da paleta nomeada (duas na madeira e no carbono) e o desgaste. "De fábrica" é a skin padrão, com os acabamentos e as cores reais; as skins nomeadas e as combinações desbloqueiam por nível e conquista (ouro no Gun Game). As skins temáticas (seção 0.7) trocam o modelo inteiro.
```

Em `CLAUDE.md.md`, trocar:

```md
- **Skins de arma:** padrões procedurais de massinha desbloqueáveis por nível e conquista: marmorizado, glitter, massa de escola desbotada, neon que brilha no escuro, "massa misturada" de criança, madeira falsa, camuflagem de massinha, ouro (Gun Game). Aplicadas pelo mesmo ClayMaterial com parâmetros.
```

por:

```md
- **Skins de arma:** de cor e acabamento, como as pinturas dos carros do Rocket League: por zona da arma (corpo, guarnição, carregador, detalhes, interno), um acabamento (oxidado de fábrica, fosfatizado, fosco, acetinado, brilhante, metálico, perolado, anodizado, aço escovado, cromado, cerakote, fibra de carbono, madeira, polímero texturizado, borracha), uma cor da paleta nomeada (duas na madeira e no carbono) e o desgaste. "De fábrica" é a skin padrão, com os acabamentos e as cores reais; as skins nomeadas e as combinações desbloqueiam por nível e conquista (ouro no Gun Game). As skins temáticas (seção 0.7) trocam o modelo inteiro.
```

- [ ] **Passo 2: Os textos das Fases 4, 5 e 11** (só no `CLAUDE.md.md`)

Em `CLAUDE.md.md`, trocar:

```md
- Todas as armas da tabela, com modelo de massinha único cada, viewmodel com animações stop-motion (sacar, atirar, recarregar, inspecionar, correr).
```

por:

```md
- Todas as armas da tabela, cada uma com o modelo realista próprio feito por script no Blender (ficha de fidelidade e validação por número, seção 0.7), luvas de 5 dedos com a empunhadura resolvida por arma e o viewmodel com animações suaves e a opção stop-motion (sacar, atirar, recarregar, inspecionar, correr).
```

Em `CLAUDE.md.md`, trocar:

```md
- AWP/Scout/AUG/SG com luneta de anel de massinha e distorção; FAMAS com rajada; USP-S e M4A1-S com silenciador removível.
```

por:

```md
- AWP/Scout/AUG/SG com a luneta real (lente, retícula gravada, sombra de ocular); FAMAS com rajada; USP-S e M4A1-S com silenciador removível.
```

Em `CLAUDE.md.md`, trocar:

```md
- Efeitos: cápsulas de massa que grudam, amassados na massa atingida, respingos, tracers, luz de disparo.
```

por:

```md
- Efeitos: cápsulas de latão que quicam e param no chão (amassando de leve a massinha do cenário), amassados na massa atingida, respingos, tracers, luz de disparo.
```

Em `CLAUDE.md.md`, trocar:

```md
- Braçadeira e contorno de time sem perder a personalização.
```

por:

```md
- Braçadeira e contorno de time sem perder a personalização.
- Mãos: as mesmas luvas de 5 dedos e mangas do viewmodel (Fase 4), adaptadas às proporções de cada boneco.
```

Em `CLAUDE.md.md`, trocar:

```md
Implemente a seção 0.15 inteira: XP, níveis, 18 patentes, rating, skins procedurais, estatísticas com mapa de calor, 40+ conquistas, killcam em stop-motion, melhores momentos automáticos e visualizador de replay com câmera livre. Tudo salvo em IndexedDB com exportar/importar perfil (arquivo JSON).
```

por:

```md
Implemente a seção 0.15 inteira: XP, níveis, 18 patentes, rating, skins de cor e acabamento das armas (o catálogo, o desbloqueio e a tela de escolha sobre o sistema da 4.1a), estatísticas com mapa de calor, 40+ conquistas, killcam em stop-motion, melhores momentos automáticos e visualizador de replay com câmera livre. Tudo salvo em IndexedDB com exportar/importar perfil (arquivo JSON).
```

- [ ] **Passo 3: O plano da fase** — em `docs/phases/phase-4.md`:

Em `docs/phases/phase-4.md`, trocar:

```md
Base: PROMPT 0 seção 0.7 inteira + Fase 4 de `CLAUDE.md.md`. Desenho conversado e aprovado em 2026-09-25: oito
subfases nesta ordem, uma por conversa — primeiro uma "fatia vertical" (uma arma de cada forma, para provar o caminho de
modelagem em todos os tipos de peça), depois os sistemas feitos com essas armas e, por fim, o resto do arsenal no
caminho já provado.
```

por:

```md
Base: PROMPT 0 seção 0.7 inteira + Fase 4 de `CLAUDE.md.md`. Desenho conversado e aprovado em 2026-09-25: oito
subfases nesta ordem, uma por conversa — primeiro uma "fatia vertical" (uma arma de cada forma, para provar o caminho de
modelagem em todos os tipos de peça), depois os sistemas feitos com essas armas e, por fim, o resto do arsenal no
caminho já provado.

**Redesenho de 2026-09-26 (armas realistas):** as armas de massinha da 4.1 foram reprovadas pelo usuário; o desenho
novo está em `docs/superpowers/specs/2026-09-26-armas-realistas-design.md` e reordena as subfases (tabela abaixo). A
4.1 fica registrada nas seções dela como histórico.
```

trocar:

```md
| Subfase | Conteúdo | Estado |
|---|---|---|
| 4.1 | Oficina de armas: formas novas do SDF (perfil recortado, torno, tubo), receita de cada arma em `src/data/armas/`, gerador receita → malha de massinha por grupo animável, o Blender como editor da receita (importador, exportador, conferência sem janela, plantas de referência), mãos de 4 dedos com rig, viewmodel parado segurando a arma, mapa `arsenal` e o primeiro lote: Glock-18, AK-47, M4A4, AWP, Nova, P90 e a faca | ✅ 2026-09-26 |
| 4.2 | Tiro e dano: estado da arma (munição, cadência, recarga, modo), hitscan com spread e a inaccuracy da 3.2, padrões de spray gerados como no CS:GO, recoil real (aim punch) × visual (view punch), dano por hitbox, colete, capacete, penetração de blindagem, queda por distância, wallbang por material e espessura; campo de tiro com alvos de massinha, medidor de DPS e visualizador de spray | a fazer |
| 4.3 | Viewmodel stop-motion e efeitos: sacar, atirar, recarregar (arranca e aperta o pão de massa), inspecionar (a digital do animador), correr — poses-chave por categoria feitas no Blender e presas às âncoras de cada arma, "em dois"; cápsulas de massa amarela que quicam e grudam, amassados na massa atingida, respingos, tracers, luz de disparo, marcas nos outros materiais | a fazer |
| 4.4 | Arsenal completo: as outras 18 armas de fogo e a faca de ouro no caminho da 4.1, com as âncoras e as poses da categoria (se não couber num chat, 4.4a e 4.4b) | a fazer |
| 4.5 | Mira e acessórios: lunetas (anel de massinha, retícula de arame, distorção de vidro barato, poeira) da AWP, Scout, SCAR-20 e G3SG1, miras da AUG e da SG 553, rajada da FAMAS e da Glock, silenciador removível da USP-S e da M4A1-S | a fazer |
| 4.6 | Faca: golpe leve e forte, backstab, bloqueio de frente com durabilidade, parry (devolve o tiro e atordoa), barra de carga e dash de execução — a katana do Doodle District sobre a faca do CS:GO | a fazer |
| 4.7 | Granadas: HE, Flash, Smoke, Molotov/Incendiária e Decoy com modelos, física de quique do CS:GO, arremesso com carga (curto/médio/longo) da referência e os efeitos; a smoke bloqueia a visão e o raycast (o mesmo teste que a percepção dos bots da Fase 7 usa) | a fazer |
| 4.8 | Sensação e aceite: passada de sensação por arma (coice do viewmodel, cadência, leitura), aceite da spec (sensação distinta, spray reproduzível, wallbang por material, smoke bloqueando raycast), desempenho e memória | a fazer |
```

por:

```md
| Subfase | Conteúdo | Estado |
|---|---|---|
| 4.1 (massinha) | Oficina de armas de massinha: formas novas do SDF, receita por arma, gerador receita → malha de massinha, o Blender como editor da receita, mãos de 4 dedos, viewmodel parado, mapa `arsenal` e o primeiro lote — substituída pelo redesenho de 2026-09-26 (armas realistas); fica registrada abaixo | ✅ 2026-09-26 |
| 4.1a | Pipeline realista e a AK-47 tipo 3 no nível final: régua e ficha, biblioteca de peças, construir, assar, exportar e validar; `GLTFLoader` no vendor e o novo `weaponModels`; material com zonas e acabamentos, reflexo do set e luz do viewmodel; a AK na bancada `arsenal` e em primeira pessoa, ainda sem mãos; comando `skin` e as três skins de exemplo; atualização das regras e da memória | em andamento |
| 4.1b | Luvas, mangas, rig e o solver de empunhadura; a AK segurada em primeira pessoa | a fazer |
| 4.1c | Glock-18, M4A4 e a faca de combate no caminho provado, com as empunhaduras | a fazer |
| 4.1d | AWP (com a luneta real), Nova e P90, com as empunhaduras | a fazer |
| 4.2 | Tiro e dano: estado da arma (munição, cadência, recarga, modo), hitscan com spread e a inaccuracy da 3.2, padrões de spray gerados como no CS:GO, recoil real (aim punch) × visual (view punch), dano por hitbox, colete, capacete, penetração de blindagem, queda por distância, wallbang por material e espessura; campo de tiro com alvos de massinha, medidor de DPS e visualizador de spray | a fazer |
| 4.3 | Animações suaves e a opção stop-motion (sacar, atirar, recarregar, inspecionar, correr); carregador de metal que sai e volta na recarga e cápsulas de latão que quicam e param no chão (e amassam a massinha do cenário); a marca de dedo na inspeção; tracers, luz de disparo, amassados e respingos na massa atingida, marcas nos outros materiais | a fazer |
| 4.4 | Arsenal completo: as outras 18 armas de fogo e a faca de ouro no caminho provado, com as empunhaduras (dividido em quantos chats o detalhe pedir) | a fazer |
| 4.5 | Mira e acessórios: lunetas reais (lente, retícula gravada, sombra de ocular) da AWP, Scout, SCAR-20 e G3SG1, miras da AUG e da SG 553, rajada da FAMAS e da Glock, silenciador removível da USP-S e da M4A1-S | a fazer |
| 4.6 | Faca: golpe leve e forte, backstab, bloqueio de frente com durabilidade, parry (devolve o tiro e atordoa), barra de carga e dash de execução — a katana do Doodle District sobre a faca do CS:GO | a fazer |
| 4.7 | Granadas reais — fragmentação, atordoante, fumaça, molotov de garrafa com pano, incendiária e decoy — com os modelos do Blender, a física de quique do CS:GO, o arremesso com carga (curto/médio/longo) da referência e os efeitos de estúdio; a smoke bloqueia a visão e o raycast (o mesmo teste que a percepção dos bots da Fase 7 usa) | a fazer |
| 4.8 | Sensação e aceite: passada de sensação por arma (coice do viewmodel, cadência, leitura), aceite da spec (sensação distinta, spray reproduzível, wallbang por material, smoke bloqueando raycast), desempenho e memória | a fazer |
```

trocar:

```md
## Decisões do usuário (2026-09-25)
```

por:

```md
## Decisões do usuário (2026-09-26) — armas realistas

O usuário reprovou as armas de massinha da 4.1: feias, sem detalhe, pulsando por causa do boil e com os dedos tortos na
arma. Desenho completo em `docs/superpowers/specs/2026-09-26-armas-realistas-design.md` (aprovado seção por seção);
plano da 4.1a em `docs/superpowers/plans/2026-09-26-4.1a-pipeline-realista-ak47.md`.

1. **Realismo de fábrica, tipo CS2.** A arma real em peças, medidas e materiais, limpa, com desgaste leve nas bordas;
   descartados o hiper-realismo sujo (CoD MW, Tarkov), o realismo estilizado (Valorant) e o visual de maquete.
2. **Luva tática de 5 dedos com a manga de tecido da facção** em primeira pessoa (e nos bonecos em terceira pessoa, na
   Fase 5).
3. **Exceção à regra 4 (e à paridade "100% gerado em código") só para armas e mãos:** scripts Python nossos no Blender
   constroem os modelos e as texturas assadas, entregues como `.glb` e `.webp`. Nada é baixado de terceiros.
4. **Faca, granadas, carregadores e cápsulas, e lunetas passam a ser realistas.** As versões de massinha ficam como
   ideias de skin temática.
5. **Animação suave em primeira pessoa**, com a opção "viewmodel em stop-motion" (a mesma animação a 12 poses/s).
6. **A AK-47 do jogo é a tipo 3, de receptor fresado**, no tamanho e no formato reais.
7. **Fidelidade vira regra do pipeline:** ficha por arma, régua sobre a foto real, medidas e silhueta conferidas por
   número antes de exportar.
8. **Orçamento de arquivos: detalhe máximo.** Texturas de 2048 sem perdas (com a quantização dos canais de dados, que
   não aparece) e a geometria com Draco: fuzil 6 MB, pistola 3 MB, faca 2 MB, luvas 6 MB (a AK: 5,1 MB). Decidido
   depois da medição do `construir` completo; o orçamento de 2,5 MB da primeira versão do desenho só fecharia com as
   texturas em 1024.

Para as armas e as mãos, substituem as decisões 1 a 4 de 2026-09-25 (o Blender gerando a receita de massinha, o estilo
"fiel e gordinha", as mãos de 4 dedos e o acento da facção nas armas). O Blender continua sendo a ferramenta, agora
construindo o modelo realista por script; as skins de massinha da seção 0.15 viram skins de cor e acabamento.

## Decisões do usuário (2026-09-25)
```

- [ ] **Passo 4: O progresso** — em `docs/PROGRESS.md`:

Em `docs/PROGRESS.md`, trocar:

```
npm run blender -- <abrir|conferir|ida-volta> <arma|todas>   # editor de armas no Blender 5.2 (Fase 4.1)
```

por:

```
npm run blender -- <abrir|conferir|ida-volta> <arma|todas>   # editor de armas no Blender 5.2 (Fase 4.1)
npm run blender -- construir <arma|todas> [--forcar]   # armas realistas: constrói, assa, valida e exporta (Fase 4.1a)
```

trocar:

```md
  passado aos estados. `weaponModels` (as malhas e os materiais das armas de massinha) e `handModels` (a malha das mãos)
  entraram na 4.1.
```

por:

```md
  passado aos estados. `weaponModels` (as armas: o `.glb` das realistas, desde a 4.1a, e as malhas e os materiais das
  de massinha) e `handModels` (a malha das mãos de massinha) entraram na 4.1.
```

trocar:

```md
Plano técnico da fase: `docs/phases/phase-4.md` (oito subfases; decisões do usuário de 2026-09-25: o Blender gera a
receita, o estilo "fiel e gordinha", as mãos de 4 dedos gordinhos e a cor real com o acento da facção).
```

por:

```md
Plano técnico da fase: `docs/phases/phase-4.md` (oito subfases; decisões do usuário de 2026-09-25: o Blender gera a
receita, o estilo "fiel e gordinha", as mãos de 4 dedos gordinhos e a cor real com o acento da facção).

Redesenho de 2026-09-26: as armas de massinha foram reprovadas; as armas e as mãos passam a ser realistas, feitas por
script no Blender (`docs/superpowers/specs/2026-09-26-armas-realistas-design.md`), com a nova ordem de subfases
(4.1a, 4.1b, 4.1c, 4.1d e depois 4.2 a 4.8) em `docs/phases/phase-4.md`.
```

- [ ] **Passo 5: A memória** — conferir que `massacre-workflow-rules.md` (pasta de memória do projeto, fora do repositório) já diz que o Blender gera os modelos das armas e das mãos por script, com a exceção à regra 4 só para eles, e a regra de fidelidade (ficha, régua, validação por número); o que faltar entra lá agora. O estado do projeto (`massacre-game-project.md`) é atualizado na Tarefa 19.

- [ ] **Passo 6: Conferir** — nenhuma regra ainda falando das armas de massinha como regra atual:

Run: `grep -n "arma de massinha\|armas de massinha\|modelo de massinha único\|luneta de anel" CLAUDE.md CLAUDE.md.md`
Expected: nenhuma linha. Suíte inteira: `npm test 2>&1 | tail -8` → `# tests 370`, `# fail 0` (só documentos).

- [ ] **Passo 7: A faca é a baioneta M9** (decisão do usuário de 2026-09-26, na execução): as regras, a tabela de
  subfases e o desenho passam a falar da baioneta M9 (EUA, 1986) no lugar da faca de combate genérica.

Em `CLAUDE.md`, trocar:

```
- **Inspeção (tecla F):** o boneco gira a arma e aparece, sutil, a marca do dedo do "animador" no metal, visível no reflexo.
- **Faca:** faca de combate realista, de lâmina fixa. Herda da katana da referência: segurar o botão direito **bloqueia** projéteis de frente (com durabilidade) e um bloqueio no tempo certo faz **parry** (devolve o tiro e atordoa). Barra de carga que libera um **dash de execução**.
- **Granadas:** reais (fragmentação, atordoante, fumaça, molotov de garrafa com pano, incendiária e decoy), com os efeitos de estúdio: a explosão em respingos de massa, a flash que "estoura" a tela em branco-massinha, a nuvem de algodão de set (fumaça volumétrica fake com sprites em camadas), o fogo de papel celofane laranja animado em stop-motion. Quicam com física e têm arremesso com carga (curto/médio/longo), como na referência.
```

por:

```
- **Inspeção (tecla F):** o boneco gira a arma e aparece, sutil, a marca do dedo do "animador" no metal, visível no reflexo.
- **Faca:** a baioneta M9 (EUA, 1986) realista, de lâmina fixa (decisão do usuário de 2026-09-26). Herda da katana da referência: segurar o botão direito **bloqueia** projéteis de frente (com durabilidade) e um bloqueio no tempo certo faz **parry** (devolve o tiro e atordoa). Barra de carga que libera um **dash de execução**.
- **Granadas:** reais (fragmentação, atordoante, fumaça, molotov de garrafa com pano, incendiária e decoy), com os efeitos de estúdio: a explosão em respingos de massa, a flash que "estoura" a tela em branco-massinha, a nuvem de algodão de set (fumaça volumétrica fake com sprites em camadas), o fogo de papel celofane laranja animado em stop-motion. Quicam com física e têm arremesso com carga (curto/médio/longo), como na referência.
```

Em `CLAUDE.md.md`, trocar:

```
- **Inspeção (tecla F):** o boneco gira a arma e aparece, sutil, a marca do dedo do "animador" no metal, visível no reflexo.
- **Faca:** faca de combate realista, de lâmina fixa. Herda da katana da referência: segurar o botão direito **bloqueia** projéteis de frente (com durabilidade) e um bloqueio no tempo certo faz **parry** (devolve o tiro e atordoa). Barra de carga que libera um **dash de execução**.
- **Granadas:** reais (fragmentação, atordoante, fumaça, molotov de garrafa com pano, incendiária e decoy), com os efeitos de estúdio: a explosão em respingos de massa, a flash que "estoura" a tela em branco-massinha, a nuvem de algodão de set (fumaça volumétrica fake com sprites em camadas), o fogo de papel celofane laranja animado em stop-motion. Quicam com física e têm arremesso com carga (curto/médio/longo), como na referência.
```

por:

```
- **Inspeção (tecla F):** o boneco gira a arma e aparece, sutil, a marca do dedo do "animador" no metal, visível no reflexo.
- **Faca:** a baioneta M9 (EUA, 1986) realista, de lâmina fixa (decisão do usuário de 2026-09-26). Herda da katana da referência: segurar o botão direito **bloqueia** projéteis de frente (com durabilidade) e um bloqueio no tempo certo faz **parry** (devolve o tiro e atordoa). Barra de carga que libera um **dash de execução**.
- **Granadas:** reais (fragmentação, atordoante, fumaça, molotov de garrafa com pano, incendiária e decoy), com os efeitos de estúdio: a explosão em respingos de massa, a flash que "estoura" a tela em branco-massinha, a nuvem de algodão de set (fumaça volumétrica fake com sprites em camadas), o fogo de papel celofane laranja animado em stop-motion. Quicam com física e têm arremesso com carga (curto/médio/longo), como na referência.
```

Em `docs/phases/phase-4.md`, trocar:

```
| 4.1b | Luvas, mangas, rig e o solver de empunhadura; a AK segurada em primeira pessoa | a fazer |
| 4.1c | Glock-18, M4A4 e a faca de combate no caminho provado, com as empunhaduras | a fazer |
| 4.1d | AWP (com a luneta real), Nova e P90, com as empunhaduras | a fazer |
```

por:

```
| 4.1b | Luvas, mangas, rig e o solver de empunhadura; a AK segurada em primeira pessoa | a fazer |
| 4.1c | Glock-18, M4A4 e a faca — a baioneta M9 (EUA, 1986) — no caminho provado, com as empunhaduras | a fazer |
| 4.1d | AWP (com a luneta real), Nova e P90, com as empunhaduras | a fazer |
```

Em `docs/superpowers/specs/2026-09-26-armas-realistas-design.md`, trocar:

```
  4.1 sai das armas: a identidade do time fica na manga e na luva.
- **Itens que ficam realistas:** faca de combate de lâmina fixa (seção 3.2), granadas (fragmentação, atordoante,
  fumaça, molotov de garrafa com pano, incendiária e decoy, na 4.7), carregadores de metal ou polímero, cápsulas de
```

por:

```
  4.1 sai das armas: a identidade do time fica na manga e na luva.
- **Itens que ficam realistas:** a faca, que é a baioneta M9 (EUA, 1986) de lâmina fixa (seção 3.2), granadas (fragmentação, atordoante,
  fumaça, molotov de garrafa com pano, incendiária e decoy, na 4.7), carregadores de metal ou polímero, cápsulas de
```

Em `docs/superpowers/specs/2026-09-26-armas-realistas-design.md`, trocar:

```
| M4A4 | carabina M4A1, coronha aberta | 840 mm | escolhida na 4.1c |
| Faca | faca de combate genérica: lâmina fixa de 180 mm com ponta clip point e dorso reto, guarda cruzada de aço, cabo de elastômero ranhurado, pomo de aço | 300 mm | escolhida na 4.1c (faca real equivalente) |
| AWP | Accuracy International AWM .338 | 1230 mm | escolhida na 4.1d |
```

por:

```
| M4A4 | carabina M4A1, coronha aberta | 840 mm | escolhida na 4.1c |
| Faca | baioneta M9 (EUA, 1986; decisão do usuário de 2026-09-26): lâmina clip point de 178 mm, guarda com a argola que encaixa na boca do cano, cabo e bainha de polímero; o resto (serrilha do dorso, furo do corta-arame, quadriculado do cabo, pomo com a trava) sai da ficha da 4.1c | 305 mm | escolhida na 4.1c |
| AWP | Accuracy International AWM .338 | 1230 mm | escolhida na 4.1d |
```

Em `docs/superpowers/specs/2026-09-26-armas-realistas-design.md`, trocar:

```
| 4.1b | Luvas, mangas, rig e o solver de empunhadura; a AK segurada em primeira pessoa |
| 4.1c | Glock-18, M4A4 e a faca de combate no caminho provado, com as empunhaduras |
| 4.1d | AWP (com a luneta real), Nova e P90, com as empunhaduras |
```

por:

```
| 4.1b | Luvas, mangas, rig e o solver de empunhadura; a AK segurada em primeira pessoa |
| 4.1c | Glock-18, M4A4 e a faca — a baioneta M9 (EUA, 1986) — no caminho provado, com as empunhaduras |
| 4.1d | AWP (com a luneta real), Nova e P90, com as empunhaduras |
```

---

### Tarefa 18: Aceite no navegador e a revisão crítica

**Files:** nenhum arquivo novo; o que a revisão achar volta às tarefas de origem (o script da arma, o assar, o material,
os dados) e é corrigido lá, com a suíte e o `construir` passando de novo.

O aceite da 4.1a (seções 9.3 e 9.4 do desenho), no servidor da cópia de trabalho (entrada `massacre-trabalho` do
`.claude/launch.json` da pasta-mãe, porta 5176, pelo painel de pré-visualização), com o preset gráfico Alto na RTX 2070.
O console do jogo abre com a crase (`` ` ``) ou F1.

- [ ] **Passo 1: Subir e conferir o console limpo** — `preview_start` com `massacre-trabalho`; no jogo, `arsenal`.
  Ler o console do navegador (`read_console_messages`, só erros): **nenhum** erro nem aviso do jogo durante a montagem.
  No console do jogo, `armas`: a AK com a origem `glb`, `pronta` nos três níveis (perto ≤ 40 000, mundo ≤ 6 000, longe ≤
  1 500 triângulos, os mesmos números do `ak47.relatorio.json`), as outras seis com `massinha`.

- [ ] **Passo 2: A AK na bancada** — no painel (Tab), com a AK na roda, conferir e registrar com captura de tela:
  1. forma: de lado, a silhueta bate com a foto da ficha (planta por cima da silhueta ligada: o contorno laranja passa
     rente à arma em toda a volta); "Medir" mostra a silhueta do Blender (≥ 98 % com a tolerância);
  2. material de fábrica: o aço oxidado reflete o set (as softboxes e a bancada aparecem no receptor e na tampa); a
     madeira com veio e verniz; o desgaste leve só nas bordas; nenhuma face preta, nenhuma costura de UV visível,
     nenhum relevo invertido (luz vindo de cima: as bordas chanfradas acendem em cima);
  3. níveis: `Perto`, `Mundo` e `Longe` trocam sem salto de posição; o `Longe` mantém a silhueta;
  4. peças móveis: "Explodir as peças" afasta ferrolho, carregador, gatilho, cão e seletor nas direções dos dados;
     "Mostrar as âncoras e os soquetes" mostra os eixos na boca, na janela de ejeção (apontando para fora à direita), no
     poço do carregador, nas duas miras e nas duas mãos;
  5. skins: `De fábrica`, `Anodizado Terracota`, `Cromo e Carbono` e `Madeira Clara e Aço Escovado` pelo seletor — a
     da roda e a da fileira trocam juntas, sem piscar a arma vazia; no console, `skin ak47 corpo=perolado:rosa
     guarnicao=carbono:preto,cinzaGrafite desgaste=0,5` — a roda, a fileira e o seletor ("Personalizada") acompanham;
     conferir cada acabamento contra a referência dele (seção 14 do moodboard: QCK e QRL);
  6. boil zero: com "Girar a roda" desligado, duas capturas de tela seguidas (≥ 0,2 s entre elas) iguais na região da
     arma (a massinha em volta pode mudar; a arma não).

- [ ] **Passo 3: Em primeira pessoa** — "Segurar (primeira pessoa)" no painel e, na pista (`map pista`), a AK na mão
  (`give ak47` e a tecla 1):
  1. a arma na posição da categoria `rifle`, sem braços (as luvas são da 4.1b), sem cortar no plano de perto, com o
     reflexo do set e a sombra própria (a arma escurece no feixe tapado, como a massinha em volta);
  2. troca de skin pelo console com a arma na mão: a mão troca sozinha, sem piscar;
  3. `viewmodel_ajuste mao direita 0 0 0` avisa que a realista usa as luvas da 4.1b; as de massinha continuam com os
     braços de massinha.

- [ ] **Passo 4: Desempenho e memória**
  1. 60 FPS no preset Alto (overlay `cl_showfps completo`): na bancada com a AK na roda e segurando, e na pista com a AK
     na mão andando pela quadra de strafe por 30 s — quadro p95 ≤ 16,7 ms;
  2. memória estável (`mem`): trocar a arma da roda 20 vezes passando pelas sete (e as quatro skins da AK) e voltar à
     AK — geometrias, texturas e programas voltam aos mesmos números; depois 3 ciclos menu ↔ arsenal ↔ pista com os
     mesmos números em cada volta (como na 4.1: 27/35/35 no menu; os do arsenal e da pista mudam com a AK nova e ficam
     registrados);
  3. a recarga do disco: no terminal, `npm run blender -- construir ak47 --forcar`; na bancada, "Reler do disco" — a AK
     volta nova na roda e na fileira, sem erro, e o `mem` não cresce.

- [ ] **Passo 5: O jogo e o Blender lado a lado** — `npm run blender -- conferir ak47` e, no jogo, as mesmas vistas
  (a roda parada de lado e em 3/4; a primeira pessoa): as duas imagens lado a lado não mostram diferença de forma (o
  material difere só pela luz do set). Registrar as imagens usadas.

- [ ] **Passo 6: Revisão crítica, até não sobrar defeito** (regra do usuário) — olhar cada captura como quem vai jogar:
  o que estiver ruim ou mediano (proporção, chanfro, peça faltando ou flutuando, material chapado ou plástico demais,
  reflexo errado, marcação ilegível ou gritante, textura borrada de perto, serrilhado, costura) é anotado com a vista, a
  peça e a referência, corrigido na tarefa de origem e conferido de novo neste passo. Só termina quando uma rodada
  inteira de revisão não achar nada; a lista (achado → correção → conferência) vai para o relatório da subfase.

---

### Tarefa 19: Plano gerado do diff, validação limpa, aplicação e relatório

**Files:**
- Create: `docs/phases/phase-4.1a-plan.md` (gerado)
- Modify: `docs/PROGRESS.md`, `docs/phases/phase-4.md` (o relatório e o ✅ com os números do aceite)
- Memória: `massacre-game-project.md` e o índice `MEMORY.md`

O passo 4 de "Como este plano é executado": o plano com o código completo sai do diff `trabalho-4.1a` × `base-4.1a`, é
validado numa cópia limpa e aplicado no projeto pelo mesmo roteiro.

- [ ] **Passo 1: O relatório da subfase** — o relatório da 4.1a com os números do aceite no `docs/PROGRESS.md`
  (no lugar da seção da 4.2, que passa a ser a próxima depois da 4.1b) e o ✅ na tabela de subfases:

Em `docs/PROGRESS.md`, trocar:

```

### Próxima: subfase 4.2 — Tiro e dano

Estado da arma (munição, cadência, recarga, modo), hitscan com spread e a inaccuracy da 3.2, padrões de spray gerados
como no CS:GO, recoil real (aim punch) × visual (view punch), dano por hitbox com colete, capacete e penetração de
blindagem, queda por distância, wallbang por material e espessura; campo de tiro com alvos de massinha, medidor de DPS e
visualizador de spray (`docs/phases/phase-4.md`, tabela de subfases; o desenho detalhado é feito no começo do chat dela).

```

por:

```

### Subfase 4.1a — Pipeline realista e a AK-47 tipo 3 ✅ (2026-09-26)

Desenho em `docs/superpowers/specs/2026-09-26-armas-realistas-design.md`; plano de desenho em
`docs/superpowers/plans/2026-09-26-4.1a-pipeline-realista-ak47.md`; plano executado (gerado do diff da cópia de
trabalho, validado numa cópia limpa e aplicado aqui pelo mesmo roteiro): `docs/phases/phase-4.1a-plan.md`. Referências no
item 14 do moodboard: os boards QVM a QMP do Pinterest, a planta de fábrica soviética da AK achada no Pinterest (lida só
no navegador), a foto de museu "7,62 RK 54 Kalasnikov" (domínio público) para a janela de ejeção e as fotos do Commons,
das quais só números entraram no projeto.

O que entrou:
- **Ficha e régua**: `tools/blender/refs/ak47.json` no formato 2 (contornos por peça, tornos, pontos, cores e a seção
  `vistaDeCima` com as larguras da planta), medida pela régua `tools/regua.html` na foto "AK-47 assault rifle.jpg"
  (domínio público); `src/weapons/model/ficha.js` lê e valida os dois formatos. Regra das duas fontes: posições ao longo
  da arma e alturas de lado vêm da foto; larguras e peças que só aparecem de cima ou de baixo, da planta.
- **Pacote do Blender** (`tools/blender/armas/`): unidades, biblioteca de peças (prisma, torno, lofting, tubo, mola,
  rosca, gravação, cortes booleanos antes e depois do chanfro, arestas vivas por Geometry Nodes), materiais de fábrica,
  estúdio, zonas e soquetes; `ak47.py` com a AK-47 tipo 3 (receptor fresado com a janela de ejeção funda e o
  transportador, espigas embutidas, argolas de bandoleira, tubo de gases com estrias e furos, coronha que afina, soleira
  em arco); `assar.py` (UV automático sem sobreposição, normal, sombra de contato e os canais de fábrica), `lod.py`
  (mundo e longe, com piso de triângulos por peça), `exportar.py` (glTF com Draco), `conferir.py`, `validar.py` e
  `principal.py`; `npm run blender -- construir|validar|conferir|abrir ak47` no `tools/blender.mjs`.
- **Jogo**: `GLTFLoader` e `DRACOLoader` no vendor (só eles e o decodificador), `weaponModels` com as duas origens
  (`glb` e massinha), material de zona com os acabamentos e o padrão procedural (`src/weapons/model/materialArma.js`,
  `glsl/acabamentos.js`), reflexo do set (`src/render/setReflection.js`), a AK na bancada `arsenal` e em primeira pessoa
  sem mãos, o comando `skin` e as três skins de exemplo; a receita de massinha da AK saiu.
- **Documentos**: regras 3 e 4 com a exceção das armas e das mãos, seções 0.7, 0.12, 0.13 e 0.15 reescritas, a faca
  como a baioneta M9 (EUA, 1986), a nova ordem de subfases.

Números medidos:
- `construir ak47`: 105 a 150 s na RTX 2070 (o assar do perto leva ~50 s); silhueta 99,86 % com tolerância de 2 px e
  98,24 % bruta; medidas: comprimento 870,0 (0 %), cano 415,0 (0 %), raio de mira 374,9 (alvo 378: −0,82 %, decisão D5,
  geometria da foto 1), altura sem carregador 199,6 (+0,10 %), com carregador 266,3 (+0,28 %); triângulos perto 27 381,
  mundo 5 700, longe 1 425; UV sem sobreposição, densidade de texel 2,24 px/mm (de 0,98 a 1,04 da mediana); arquivos
  5,16 MB (`.glb` 0,36; `_n` 1,57; `_m` 2,98; os dois do mundo 0,50) no orçamento de 6 MB; construir de novo sem mudança
  pula pelo hash em menos de 1 s.
- No jogo: cada nível carrega em ~130 ms; na pista com a AK na mão, 144 FPS (limite do monitor) e quadro p95 de 7,1 ms
  no preset Alto; memória igual nos ciclos (menu 29/38/46, arsenal 103/50/62, pista 77/103/71 em
  geometrias/texturas/programas) e ao trocar 60 vezes a arma da roda com as quatro skins da AK; "Reler do disco" depois
  de `construir ak47 --forcar` sem erro e sem crescer a memória; nenhum erro do jogo no console.

Revisão crítica (achado → correção):
- Leituras erradas da foto no lado (concordância da espiga, parafuso e fenda, entalhe da tampa, cubo do seletor, frente
  da alavanca de manejo, serrilha do botão) → conferidas e corrigidas pela planta soviética.
- A foto de lado não dá largura → seção `vistaDeCima` da ficha, com o modelo sobreposto à planta na escala dela.
- Colar do guarda-mão redondo, cano fino (14,2 mm) e face traseira do bloco de gases fora do lugar → bloco da vista
  esquerda da planta, cano de 15,2/16,2 mm e o bloco pelo mapa de pixels da foto.
- Madeira do Blender com riscos verticais e desenho "derretido" → o centro dos anéis fora da peça e os anéis ao longo do
  comprimento; verniz mais baixo.
- Nervuras do carregador parecendo arames colados → cordões meio embutidos.
- Sombreado amassado na borda do entalhe da tampa → arestas vivas por Geometry Nodes.
- Janela de ejeção rasa (3 mm, com o fundo do receptor à mostra) → vão atrás da parede e o transportador enchendo a
  janela, com dorso arredondado, face lisa e o escuro atrás da ponta (foto de museu).
- UV sobreposta no assar (degraus de 0,1 mm entre dois cortes, dobras da projeção e ilhas encostadas) → um corte só em
  L; faces que caem sobre outras viram ilhas próprias e tudo é reempacotado, com a margem exata.
- Cão e gatilho do longe achatados em dois triângulos colados (o Draco descartava um) → piso de 12 triângulos por peça
  e limpeza de faces degeneradas e repetidas.
- Madeira do jogo rosada, com anéis de desenho animado em volta do eixo do cano e o veio assado quase invisível → o veio
  sai do canal assado, nas duas cores, com a fibra fina procedural por cima.

Ficou de fora ou é dedução (registrado para as próximas):
- Na bancada, o lado do receptor reflete o estúdio escuro atrás de quem olha e sai quase preto; as skins de cromo e de
  aço escovado refletem o painel laranja. É o reflexo real do set; a correção fotográfica (um rebatedor branco atrás da
  bancada) muda o set da vitrine e fica para decidir com o usuário.
- Da planta, a peça "9" ao lado da braçadeira, as "asas" do bloco de gases e a trava do bloco do colar não entraram;
  o afinamento do guarda-mão de baixo dentro da braçadeira e a argola traseira dobrada são dedução.

Como testar: `npm test` (370 testes, 42 novos); `npm run blender -- construir ak47` (e `--forcar`); `npm run blender --
conferir ak47`; no jogo, `arsenal` (Tab para o painel: arma, nível, skin, explodir, âncoras, planta e medir) e `map
pista` + `give ak47`; no console, `armas` e `skin ak47 corpo=perolado:rosa guarnicao=carbono:preto,cinzaGrafite
desgaste=0,5`.

Git: a 4.1a está na árvore de trabalho da `fase-3.1`, junto com a 3.5 e a 4.1, sem commit, esperando o pedido.

### Próxima: subfase 4.1b — Luvas, mangas e empunhadura

Luvas táticas de 5 dedos e a manga de tecido na cor do time, com a braçadeira, feitas no Blender como as armas; o rig
das mãos e o solver de empunhadura (nenhum dedo atravessando a arma nem flutuando); a AK segurada em primeira pessoa
(`docs/phases/phase-4.md`, tabela de subfases; o desenho detalhado é feito no começo do chat dela).

```

Em `docs/phases/phase-4.md`, trocar:

```
| 4.1 (massinha) | Oficina de armas de massinha: formas novas do SDF, receita por arma, gerador receita → malha de massinha, o Blender como editor da receita, mãos de 4 dedos, viewmodel parado, mapa `arsenal` e o primeiro lote — substituída pelo redesenho de 2026-09-26 (armas realistas); fica registrada abaixo | ✅ 2026-09-26 |
| 4.1a | Pipeline realista e a AK-47 tipo 3 no nível final: régua e ficha, biblioteca de peças, construir, assar, exportar e validar; `GLTFLoader` no vendor e o novo `weaponModels`; material com zonas e acabamentos, reflexo do set e luz do viewmodel; a AK na bancada `arsenal` e em primeira pessoa, ainda sem mãos; comando `skin` e as três skins de exemplo; atualização das regras e da memória | em andamento |
| 4.1b | Luvas, mangas, rig e o solver de empunhadura; a AK segurada em primeira pessoa | a fazer |
```

por:

```
| 4.1 (massinha) | Oficina de armas de massinha: formas novas do SDF, receita por arma, gerador receita → malha de massinha, o Blender como editor da receita, mãos de 4 dedos, viewmodel parado, mapa `arsenal` e o primeiro lote — substituída pelo redesenho de 2026-09-26 (armas realistas); fica registrada abaixo | ✅ 2026-09-26 |
| 4.1a | Pipeline realista e a AK-47 tipo 3 no nível final: régua e ficha, biblioteca de peças, construir, assar, exportar e validar; `GLTFLoader` no vendor e o novo `weaponModels`; material com zonas e acabamentos, reflexo do set e luz do viewmodel; a AK na bancada `arsenal` e em primeira pessoa, ainda sem mãos; comando `skin` e as três skins de exemplo; atualização das regras e da memória | ✅ 2026-09-26 |
| 4.1b | Luvas, mangas, rig e o solver de empunhadura; a AK segurada em primeira pessoa | a fazer |
```

- [ ] **Passo 2: O plano executado** — este documento, gerado do plano de desenho, da cópia de trabalho e de uma cópia
  limpa da base com as Tarefas 1–17 do plano de desenho aplicadas (a origem dos pares), pelas ferramentas de
  `prova-armas-2026-09-26/ferramentas-plano/` (fora do repositório; o executor da 4.1a é `aplica-4.1a.py`, que entende
  as cercas com linguagem e os "trocar:" em sequência deste formato — o `validate-plan.mjs` da 4.1 não):

```bash
cd "/c/Users/T-Gamer/Desktop/game tiro"
rm -rf plano-4.1a && cp -r base-4.1a plano-4.1a
python3 prova-armas-2026-09-26/ferramentas-plano/aplica-4.1a.py "Game tiro/docs/superpowers/plans/2026-09-26-4.1a-pipeline-realista-ak47.md" plano-4.1a 1 17
node prova-armas-2026-09-26/ferramentas-plano/plano-executado-4.1a.mjs "Game tiro/docs/superpowers/plans/2026-09-26-4.1a-pipeline-realista-ak47.md" trabalho-4.1a plano-4.1a trabalho-4.1a/docs/phases/phase-4.1a-plan.md
```

- [ ] **Passo 3: Validar numa cópia limpa** — uma cópia nova da base e o roteiro `valida-4.1a.sh`, tarefa por
  tarefa: só os testes gravados falham, a tarefa inteira faz passar, a suíte inteira passa (370 no fim), o `construir`
  do Blender aprovado depois da Tarefa 8 e o vendor regenerado depois da 9; no fim, a comparação com a cópia de
  trabalho não mostra nenhum arquivo diferente fora os binários de `assets/armas/ak47/` (conferidos pelas métricas do
  relatório: medidas 0,2 %, IoU 0,002, triângulos 1 %, arquivos 5 %).

```bash
cd "/c/Users/T-Gamer/Desktop/game tiro"
rm -rf validacao-4.1a && cp -r base-4.1a validacao-4.1a
bash prova-armas-2026-09-26/ferramentas-plano/valida-4.1a.sh "$PWD/trabalho-4.1a/docs/phases/phase-4.1a-plan.md" validacao-4.1a "$PWD/trabalho-4.1a"
```

- [ ] **Passo 4: Aplicar no projeto** — o mesmo roteiro no `Game tiro` (que tem a árvore de `base-4.1a`), e o plano
  executado ao lado:

```bash
cd "/c/Users/T-Gamer/Desktop/game tiro"
bash prova-armas-2026-09-26/ferramentas-plano/valida-4.1a.sh "$PWD/trabalho-4.1a/docs/phases/phase-4.1a-plan.md" "Game tiro" "$PWD/trabalho-4.1a"
cp trabalho-4.1a/docs/phases/phase-4.1a-plan.md "Game tiro/docs/phases/phase-4.1a-plan.md"
```

- [ ] **Passo 5: Conferir no navegador** — no servidor do projeto (`massacre-dev`), a bancada com a AK (de lado, as
  três skins, os níveis) e a AK na mão na pista, como no passo 2 da Tarefa 18, rapidamente, e o console sem erros.

- [ ] **Passo 6: Arrumar** — tirar a entrada `massacre-trabalho` do `.claude/launch.json` da pasta-mãe; manter
  `base-4.1a/` e `trabalho-4.1a/` como cópia de segurança até o usuário pedir o commit (como a 4.1); apagar
  `validacao-4.1a/` e `plano-4.1a/`.

- [ ] **Passo 7: Memória** — `massacre-game-project.md`: a 4.1a pronta (o que existe, onde está, os números
  principais), a próxima (4.1b, no mesmo chat por decisão do usuário: luvas, mangas, rig e solver de
  empunhadura), como retomar, e o estado do git; a linha do `MEMORY.md` que aponta para ele.

- [ ] **Passo 8: A entrega ao usuário** (regra 8 do `CLAUDE.md`) — em português, curto e honesto: o que foi feito, a
  lista de arquivos criados e alterados, como testar (`npm test`, `npm run blender -- construir ak47`, `arsenal`,
  `skin ak47 …`), o checklist do aceite marcado com o que passou e o que ficou de fora (e por quê), a revisão crítica, e
  a próxima subfase (4.1b), que segue no mesmo chat (decisão do usuário). Commit só se o usuário pedir.
