# Fase 4 — Armas (plano técnico)

Base: PROMPT 0 seção 0.7 inteira + Fase 4 de `CLAUDE.md.md`. Desenho conversado e aprovado em 2026-09-25: oito
subfases nesta ordem, uma por conversa — primeiro uma "fatia vertical" (uma arma de cada forma, para provar o caminho de
modelagem em todos os tipos de peça), depois os sistemas feitos com essas armas e, por fim, o resto do arsenal no
caminho já provado.

**Redesenho de 2026-09-26 (armas realistas):** as armas de massinha da 4.1 foram reprovadas pelo usuário; o desenho
novo está em `docs/superpowers/specs/2026-09-26-armas-realistas-design.md` e reordena as subfases (tabela abaixo). A
4.1 fica registrada nas seções dela como histórico.

## Estado das subfases

| Subfase | Conteúdo | Estado |
|---|---|---|
| 4.1 (massinha) | Oficina de armas de massinha: formas novas do SDF, receita por arma, gerador receita → malha de massinha, o Blender como editor da receita, mãos de 4 dedos, viewmodel parado, mapa `arsenal` e o primeiro lote — substituída pelo redesenho de 2026-09-26 (armas realistas); fica registrada abaixo | ✅ 2026-09-26 |
| 4.1a | Pipeline realista e a AK-47 tipo 3 no nível final: régua e ficha, biblioteca de peças, construir, assar, exportar e validar; `GLTFLoader` no vendor e o novo `weaponModels`; material com zonas e acabamentos, reflexo do set e luz do viewmodel; a AK na bancada `arsenal` e em primeira pessoa, ainda sem mãos; comando `skin` e as três skins de exemplo; atualização das regras e da memória | ✅ 2026-09-26 |
| 4.1b | Luvas táticas realistas no braço de massinha do boneco (sem manga e sem roupa), rig de 20 ossos por braço e o solver de empunhadura dentro do `construir` da arma, com a mão da frente em "thumb break" (o polegar reto e deitado de um lado, os quatro dedos do outro); a AK segurada em primeira pessoa nas duas facções, com uma mão só na tela; os comandos `luvas` e `luvas_contato`; o rebatedor de isopor da bancada — desenho em `docs/superpowers/specs/2026-09-26-4.1b-luvas-e-empunhadura-design.md` | ✅ 2026-09-27 (aceite: `luvas_contato` a 0,02 mm do Blender nas duas facções e nas três posições, memória estável; o FPS na máquina do usuário a medir) |
| 4.1c | Glock-18, M4A4 e a faca — a baioneta M9 (EUA, 1986) — no caminho provado, com as empunhaduras | a fazer |
| 4.1d | AWP (com a luneta real), Nova e P90, com as empunhaduras | a fazer |
| 4.2 | Tiro e dano: estado da arma (munição, cadência, recarga, modo), hitscan com spread e a inaccuracy da 3.2, padrões de spray gerados como no CS:GO, recoil real (aim punch) × visual (view punch), dano por hitbox, colete, capacete, penetração de blindagem, queda por distância, wallbang por material e espessura; campo de tiro com alvos de massinha, medidor de DPS e visualizador de spray | a fazer |
| 4.3 | Animações suaves e a opção stop-motion (sacar, atirar, recarregar, inspecionar, correr); carregador de metal que sai e volta na recarga e cápsulas de latão que quicam e param no chão (e amassam a massinha do cenário); a marca de dedo na inspeção; tracers, luz de disparo, amassados e respingos na massa atingida, marcas nos outros materiais | a fazer |
| 4.4 | Arsenal completo: as outras 18 armas de fogo e a faca de ouro no caminho provado, com as empunhaduras (dividido em quantos chats o detalhe pedir) | a fazer |
| 4.5 | Mira e acessórios: lunetas reais (lente, retícula gravada, sombra de ocular) da AWP, Scout, SCAR-20 e G3SG1, miras da AUG e da SG 553, rajada da FAMAS e da Glock, silenciador removível da USP-S e da M4A1-S | a fazer |
| 4.6 | Faca: golpe leve e forte, backstab, bloqueio de frente com durabilidade, parry (devolve o tiro e atordoa), barra de carga e dash de execução — a katana do Doodle District sobre a faca do CS:GO | a fazer |
| 4.7 | Granadas reais — fragmentação, atordoante, fumaça, molotov de garrafa com pano, incendiária e decoy — com os modelos do Blender, a física de quique do CS:GO, o arremesso com carga (curto/médio/longo) da referência e os efeitos de estúdio; a smoke bloqueia a visão e o raycast (o mesmo teste que a percepção dos bots da Fase 7 usa) | a fazer |
| 4.8 | Sensação e aceite: passada de sensação por arma (coice do viewmodel, cadência, leitura), aceite da spec (sensação distinta, spray reproduzível, wallbang por material, smoke bloqueando raycast), desempenho e memória | a fazer |

## Decisões do usuário (2026-09-26 e 2026-09-27) — luvas e empunhadura (4.1b)

Desenho em `docs/superpowers/specs/2026-09-26-4.1b-luvas-e-empunhadura-design.md` (aprovado na parada da 4.1a); plano
em `docs/superpowers/plans/2026-09-26-4.1b-luvas-e-empunhadura.md`.

1. **Sem roupa por enquanto** (2026-09-26): nas próximas fases a bala fura o boneco de massinha e o tiro atravessa o
   corpo de massa, "e muito mais"; o corpo não pode ficar escondido por roupa. Em primeira pessoa, a luva tática
   realista (Blender) na mão e, do punho para trás, o braço de massinha do boneco, em código, na cor da massa dele.
2. **O antebraço de massinha não pulsa** no viewmodel (sem boil), como a arma e a luva; mantém as digitais, a
   translucidez e o brilho de massinha.
3. **A braçadeira do time** continua, como faixa de massa no antebraço, só em modo de time.
4. **Os nós da luva com protetor de borracha moldada** (do tipo das luvas táticas mais comuns), no lugar do reforço
   acolchoado.
5. **Rebatedor branco** atrás de quem olha a bancada `arsenal`: o lado do receptor da AK saía quase preto.
6. **A mão da frente** (2026-09-27, na parada P2): em toda arma que tem mão da frente, só o polegar fica de um lado e os
   outros quatro dedos do outro, como a AK no CS:GO — o polegar reto, deitado e encostado na arma, apontando para a
   frente, sem curva. O `construir` reprova a arma que sair diferente.
7. **Uma mão só na tela** (2026-09-27): nas três posições prontas do CS, só a mão da frente aparece, como na imagem de
   referência do CS:GO; a mão do gatilho continua montada (inspeção na 4.3, terceira pessoa na Fase 5).
8. **Texturas CC0 no Blender** (2026-09-27): os scripts do Blender podem usar texturas de domínio público de
   cgbookcase, Poly Haven, ambientCG e do CC0 Asset Index como base dos materiais das armas e das luvas; elas chegam ao
   jogo só assadas no `.webp`, e modelos de terceiros continuam fora (a lista e as regras ficam na seção 0.7 do
   `CLAUDE.md`, "Texturas CC0 no Blender").

## Decisões do usuário (2026-09-26) — armas realistas

O usuário reprovou as armas de massinha da 4.1: feias, sem detalhe, pulsando por causa do boil e com os dedos tortos na
arma. Desenho completo em `docs/superpowers/specs/2026-09-26-armas-realistas-design.md` (aprovado seção por seção);
plano da 4.1a em `docs/superpowers/plans/2026-09-26-4.1a-pipeline-realista-ak47.md`.

1. **Realismo de fábrica, tipo CS2.** A arma real em peças, medidas e materiais, limpa, com desgaste leve nas bordas;
   descartados o hiper-realismo sujo (CoD MW, Tarkov), o realismo estilizado (Valorant) e o visual de maquete.
2. **Luva tática de 5 dedos com a manga de tecido da facção** em primeira pessoa (e nos bonecos em terceira pessoa, na
   Fase 5). *Mudado na 4.1b (abaixo): sem manga e sem roupa — a luva no braço de massinha do boneco.*
3. **Exceção à regra 4 (e à paridade "100% gerado em código") só para armas e mãos:** scripts Python nossos no Blender
   constroem os modelos e as texturas assadas, entregues como `.glb` e `.webp`. Nada é baixado de terceiros. *Mudado
   em 2026-09-27 (abaixo): nenhum modelo de terceiros, mas texturas CC0 de bibliotecas abertas podem servir de base dos
   materiais no Blender.*
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

1. **Blender gera a receita.** Cada arma é modelada no Blender por cima de plantas de referência, só com peças que o
   gerador de massinha entende; um exportador grava a receita em `src/data/armas/<id>.js` e o jogo continua gerando a
   malha em código (boil, digitais, costuras, skins e os amassados de tiro valem igual). A regra 4 do `CLAUDE.md` e a
   paridade "100% gerado em código" do Doodle District ficam intactas: a receita são números, como o layout da pista.
   Há importador de volta — o `.blend` é só área de trabalho, a receita é a fonte da verdade — e o usuário pode abrir
   qualquer arma no Blender e mexer à mão. As poses das animações "em dois" (4.3) também saem do Blender como dados.
   As plantas ficam fora do jogo, como os pins do Pinterest.
2. **Estilo "fiel e gordinha".** Silhueta da arma real com espessura mínima de massa: cano, alma, miras e guarda-mato
   engrossam e arredondam; detalhes minúsculos (rebites, frisos, dentes de trilho) viram marcas de ferramenta — cortes de
   estilete e dedadas — em vez de peças soltas. Madeira marrom com veios riscados a palito, corpo grafite e costuras onde
   as massas se juntam. É a leitura literal da spec ("silhueta fiel à arma real, mas esculpida à mão") e do revólver do
   pinguim de *The Wrong Trousers* (QCG1, QCG7). Descartados: a miniatura fiel de peças finas (QPG5, QPL6 — cara de kit
   de plástico, sem área para boil e digitais) e o brinquedo inflado (QSG2, NFS1 — foge da silhueta fiel).
3. **Mãos de 4 dedos gordinhos** (três dedos e o polegar, grossos e arredondados, como os humanos da Aardman), na cor
   da massa do personagem, com a braçadeira do time no antebraço (seção 0.12). A Fase 5 herda o modelo e o rig.
4. **Cor real + acento da facção.** A base segue a arma real traduzida em massinha (grafite no metal preto, marrom com
   veios na madeira, verde-oliva nas de polímero verde, areia nas de cor de areia, prata na Deagle); os detalhes pequenos
   (massa de mira, gatilho, base do carregador, seletor) vêm na cor da facção: terracota e laranja nas armas da Massa
   Crua, azul e verde-água nas da Tropa do Estúdio, amarelo-massinha (com branco-massa) nas dos dois lados. As skins da
   Fase 11 entram por cima pelo mesmo `ClayMaterial`.

## Unidades e escala

A unidade é a do CS (o boneco tem 72 u; 1 u = 1 polegada na escala do boneco), então **cada arma tem o comprimento da
arma real em polegadas**. No estúdio (a leitura da pista, 1 u = 1 mm), são miniaturas de massinha de 1 a 5 cm ao lado de
um boneco de 7,2 cm — exatamente a escala das armas de polymer clay na palma da mão das referências (QPG3, QPG4, QPG7,
QPG12). O boil e as digitais já escalam pelo tamanho do objeto (`ClayMaterial.setObjectSize`; o ladrilho das digitais
cobre 96 u), então a digital do animador fica grande na arma — o que a inspeção da 4.3 vai mostrar.

| Arma (primeiro lote) | Referência real | Comprimento | u |
|---|---|---|---|
| Glock-18 | Glock 18 | 186 mm | 7,3 |
| AK-47 | AKM de coronha fixa de madeira | 880 mm | 34,6 |
| M4A4 | carabina M4A1 com a coronha aberta | 840 mm | 33,1 |
| AWP | Accuracy International AWM .338 | 1230 mm | 48,4 |
| Nova | Benelli Nova, cano de 18,5" | 995 mm | 39,2 |
| P90 | FN P90 | 500 mm | 19,7 |
| Faca | espátula de modelar de aço com cabo de madeira | 200 mm | 7,9 |

**Espessura mínima de massa:** nenhuma peça da arma fica mais fina que 1,2 u (1,2 mm de massa na miniatura — o dobro do
cano real de um fuzil), exceto a lâmina da faca (0,5 u, com a borda arredondada) e os cortes (subtrações). É a regra que
faz o "gordinha": o gerador confere e a suíte testa.

**Referencial de cada arma:** +X para a boca do cano, +Y para cima, +Z para o lado direito da arma (o da janela de
ejeção do AK e do M4); a origem fica no eixo do cano, em cima do gatilho. Vista lateral = o plano XY visto de +Z (a arma
aponta para a direita). No Blender, Z para cima: o exportador converte (x, y, z) do Blender em (x, z, −y) do jogo.

## Fonte dos números

As mesmas da 3.2 (`docs/research/`): o código do CS:GO no port Kisak-Strike (o vazamento de ~2017) e o `items_game`
final (2023), para recoil (`recoil_*` e a geração da tabela), dano (`ScaleDamage`, `CS_ARMOR_*`), penetração
(`HandleBulletPenetration`), faca (`weapon_knife`) e granadas (`basecsgrenade_projectile`); o Doodle District
(`sarvan-2187/doodleshooter`) para o bloqueio, o parry e o dash da katana e o arremesso com carga. Tudo vai para
`src/data/`. As dimensões das armas reais vêm das fichas técnicas dos fabricantes (comprimentos na tabela acima) e das
fotos laterais de domínio público ou licença livre do Wikimedia Commons (as plantas).

---

## 4.1 — Oficina de armas

O caminho de modelagem inteiro e a fatia vertical: formas novas no SDF, receita, gerador, Blender como editor, plantas,
mãos, viewmodel parado, a bancada `arsenal` e as sete primeiras peças.

### Referências (item 13 do moodboard)

Nove conjuntos novos estudados em 2026-09-25 (buscas públicas e páginas "ideas" do Pinterest; os IDs ficam em
`docs/art/pinterest-boards.json` e na folha de contato):

- **QPG** (busca "polymer clay gun miniature") e **QPL** ("plasticine gun"): armas de massinha e polymer clay feitas à mão
  — a pistola preta fosca no tapete de corte verde (QPG1), a AK montada em etapas a partir de uma placa preta com a
  madeira marrom por cima (QPG2), espingarda e cartuchos na palma (QPG3), a Glock com cartuchos de latão (QPG5), a PPSh
  e o fuzil de ferrolho com madeira (QPG7, QPG8), a AK de plasticina com a madeira marrom (QPL4), a 1911 com as serrilhas
  do ferrolho em cortes (QPL6), revólveres cinza crus no tapete de corte (QPL5, QPL8) e a pistola no alvo com cápsulas
  (QPL7).
- **QCG** (busca "claymation gun stop motion"): o pinguim de *The Wrong Trousers* com o revólver gordinho e simples no
  trem (QCG1, QCG3, QCG7, QCG11) — a referência do estilo escolhido.
- **QRF** ("clay rifle sculpture"): a AK de massa cinza crua (QRF1), revólveres de massa rosa fiéis na forma (QRF3), o
  fuzil pintado na mão da figura sobre o tapete de corte (QRF4).
- **QSG** ("stylized gun 3d model cartoon") e **NFS** (Nerf Snipers): o extremo "brinquedo" que foi descartado; guardados
  como contraste.
- **CMH** (Claymation Hands) e **QHH** (busca "claymation hands holding"): mãos de boneco com armadura de arame (CMH2,
  CMH11, CMH20), poses de mão em massa (CMH3, CMH14, CMH16, CMH19), mãos simples de Morph (CMH15, CMH18), mãos de
  plasticina (QHH11).
- **CTL** (Clay Sculpting Tools): as espátulas de modelar de aço com cabo de madeira (CTL6, CTL7, CTL16) e as facas de
  madeira (CTL12) — a faca do jogo.

### Receita (`src/data/armas/<id>.js`)

Um módulo por arma com `export default {…}` e o corpo em JSON puro (o exportador do Blender grava; o importador lê
achando o primeiro `{` depois de `export default`). Campos:

- `id`, `version` (formato), `refs` (IDs de pins e das plantas usadas).
- `materials`: slot da receita → massa da paleta (`grafite`, `grafiteClaro`, `madeira`, `madeiraEscura`, `verdeOliva`,
  `areia`, `prata`, `aco`) ou `acento`/`acento2` (resolvidos pela facção da arma em `src/data/weapons.js`).
- `soft`: suavidade padrão da união entre peças do mesmo grupo (k da união suave, 0,25 u) e o vinco da costura
  (`crease: {depth, width}`, 0,08 u e 0,18 u); `lumps`: calombos da massa inteira (amplitude 0,03 u, frequência 0,35/u).
- `groups`: as partes que se mexem, cada uma vira malha própria — `corpo` (sempre) e, conforme a arma, `carregador`,
  `ferrolho` (alavanca de manejo), `slide`, `gatilho`, `bomba` (Nova), `alavanca` (AWP), `silenciador` (4.5). Cada grupo
  tem `pivot` (o ponto em volta do qual gira) e, se for o caso, `axis` (eixo de rotação ou de deslize).
- `anchors`: pontos com posição e rotação no referencial da arma — `maoDireita` (empunhadura), `maoEsquerda` (apoio:
  guarda-mão, bomba, frente da armação), `boca` (boca do cano, direção +X), `ejecao` (janela de ejeção e a direção em que
  a cápsula sai), `mira` (centro óptico da luneta, para a 4.5) e a pose de mão de cada âncora de mão (`pose`).
- `parts`: lista de peças; cada uma com `name`, `group`, `mat`, `shape` (as formas do SDF: `roundBox`, `cylinder`,
  `capsule`, `sphere`, `ellipsoid`, `roundCone`, `torus`, `cone` e as novas `profile`, `lathe`, `tube`), os parâmetros
  da forma, `pos`/`rot` (Euler XYZ do three.js) e, opcionais, `op: 'subtract'` (corte: janela de ejeção, alma do cano,
  buraco do guarda-mato, serrilhas), `k` (suavidade própria) e `crease` (vinco próprio).

### Formas novas do SDF (`src/clay/sdf/`)

- **`profile`** — perfil recortado e extrudado: polígono em XY (`points`), meia-espessura `h` em Z, `corner` (filete 2D
  nos cantos, convexos e côncavos — a massa preenche os cantos de dentro) e `round` (arredondado das arestas da
  extrusão). O filete é feito uma vez na compilação (arcos tangentes aos dois lados, raio limitado pelos lados, 6
  segmentos por arco) e o `corner` fica ≥ `round`, o que torna exata a distância do contorno encolhido de `round` usada
  no "opExtrusion" arredondado de iq. Distância 2D exata ao polígono (distância aos segmentos + sinal pelo número de
  cruzamentos), então a forma é 1-Lipschitz e entra no intervalo garantido d ± R. É a peça principal: corpo, coronha,
  empunhadura, carregador, guarda-mão, ferrolho, lâmina.
- **`lathe`** — sólido de revolução em volta do eixo X local: polígono no semiplano (x, ρ ≥ 0) com o mesmo filete;
  distância exata = distância 2D ao polígono em (x, √(y² + z²)). Freios de boca, luneta, guarda-mão redondo do M4, cabo
  e virola da faca, e as granadas da 4.7.
- **`tube`** — cobrinha de massa por uma polilinha 3D com raio por ponto (cones arredondados encadeados; distância
  exata = o mínimo das distâncias aos segmentos). Guarda-mato, alavanca de manejo, alavanca do ferrolho, pavio.
- `bounds.js` ganha a função suporte de cada uma (o polígono e a revolução do polígono; o tubo, a casca das esferas das
  pontas) e `params.js` os leitores e os limites (polígono de 3 a 256 pontos, sem lado de comprimento zero).

### Gerador (`src/weapons/model/`)

- `recipe.js` (puro, testado no Node): valida a receita (formas, grupos, âncoras, massas, espessura mínima) e monta uma
  árvore SDF por grupo — as peças somadas na união suave com vinco (`smoothUnionCrease`, faixa de costura de 0,25 u entre
  massas diferentes), os cortes numa subtração suave (`smoothSubtract`, k 0,12 u) e os calombos (`displace`). Cada massa
  vira um `mat` (índice no array de materiais da malha).
- `weaponModel.js`: a receita vira um `THREE.Group` com uma malha por grupo (grupos por material do `SdfMesher`, nos
  Workers e com o cache do IndexedDB), cada grupo num `Object3D` posto no `pivot`, as âncoras como `Object3D` vazios, e
  dois níveis: **perto** (célula de 0,14 u — viewmodel e a bancada) e **mundo** (0,35 u — arma no chão e na mão dos
  outros, Fases 5, 8 e 9).
- `weaponLibrary.js` (serviço `weaponModels`): guarda as malhas por (arma, nível) e os materiais por (massa, facção);
  entrega instâncias (a geometria é compartilhada; `dispose` só na saída do serviço); pré-carrega as armas do jogador ao
  entrar no mapa, para a troca não esperar.
- `weaponPalette.js` em `src/data/`: as massas (cor, rugosidade, umidade, skin — a madeira usa a skin "madeira falsa" com
  os veios; o aço é massa prata mais úmida e brilhante) e o acento de cada facção.

### Blender (`tools/blender/`)

- `massacre_armas.py` (roda dentro do Blender 5.2): **importar** monta a cena a partir da receita (uma coleção por grupo;
  `profile` e `lathe` viram curvas 2D com extrusão/bisel ou parafuso; `tube`, curva 3D com bisel; as outras formas, malhas
  geradas pelos parâmetros; cortes em arame vermelho; âncoras como Empties com a mão desenhada; a planta de referência
  numa coleção que não exporta; propriedades `massacre_*` guardando o que o jogo precisa); **exportar** lê a cena,
  converte os eixos, dobra escalas nos parâmetros, valida e grava a receita; **conferir** renderiza (Workbench, sem janela)
  as vistas lateral, de cima, de frente e 3/4 com a planta por cima, em PNG; no Blender com janela, um painel "MASSACRE"
  na barra lateral com Exportar, Recarregar e Conferir.
- `tools/blender.mjs` + `npm run blender -- <ação> <arma>`: `abrir` (Blender com janela e a arma montada), `conferir`
  (renders numa pasta), `ida-volta` (importa e exporta sem janela e compara com a receita — a prova do caminho). O
  executável vem de `BLENDER_PATH`, de `tools/blender/local.json` (fora do git) ou das pastas de instalação conhecidas.

### Plantas de referência (`tools/blender/refs/<id>.json`)

Silhueta lateral da arma real tirada de uma foto de domínio público ou licença livre do Wikimedia Commons, sobre fundo
claro: a página `tools/silhueta.html` (servida pelo servidor de desenvolvimento) carrega a imagem pelo CORS do Commons
num canvas, separa a arma do fundo por limiar, segue o contorno (marching squares), simplifica (Douglas-Peucker) e escala
pelo comprimento real em u, com a boca do cano e o eixo alinhados ao referencial da arma. Nenhum arquivo de imagem é
baixado para o disco nem entra no projeto: só o contorno e a ficha da fonte (arquivo, autor, licença). O contorno serve
para três coisas: guia no Blender, recorte das peças (o perfil de cada peça sai do contorno cortado nas faixas dela e
depois engrossa pela espessura mínima) e a conferência na suíte — **a silhueta lateral do SDF (máximo em Z) contra a
planta, com IoU ≥ 0,8** — a prova numérica do "silhueta fiel".

### Mãos de 4 dedos (`src/characters/hands/` + `src/data/hands.js`)

- Modelo: palma (caixa arredondada 3,4 × 3,0 × 1,5 u), três dedos de raio 0,62 u com falanges de 1,25/1,05/0,90 u,
  polegar de raio 0,7 u e o antebraço (cone arredondado de 1,25 u no pulso a 1,65 u no cotovelo, 11 u), tudo numa árvore
  SDF com as costuras nos nós dos dedos (a mão inteira fica com ~7 u, na medida da empunhadura da Glock). Mão direita;
  a esquerda é a espelhada.
- Rig: 14 ossos (antebraço, mão, 3 × 3 falanges, polegar em 3) e pesos calculados pela distância de cada vértice ao
  segmento de cada osso (queda suave, os 4 maiores, normalizados), numa `SkinnedMesh`. O boil do `ClayMaterial` age na
  pose de repouso (antes do skinning) e as digitais ficam no espaço do objeto em repouso: a massa dobra com o dedo e as
  marcas vão junto.
- Poses de mão (dados): `empunhadura` (três dedos em volta, o primeiro no gatilho), `apoio` (mão em concha por baixo),
  `guardaMao`, `bomba`, `faca` (punho fechado) e `aberta` — ângulos de cada falange e do polegar. A pose muda só na troca
  de pose (12/s). O Blender importa a mão como proxy nas âncoras (a 4.3 traz o rig completo para animar lá).
- Braçadeira: faixa de massa na cor do time a 55% do antebraço (visível só com time; `cl_bracadeira` testa); cor da
  massa do braço = a do boneco (terracota no boneco de referência; o criador da Fase 5 troca).

### Viewmodel parado (`src/weapons/viewmodel/` + `src/data/viewmodel.js`)

- Camada própria do pipeline (`postPipeline.addLayer`): cena com a arma e os dois braços, câmera que copia a do jogador
  com o FOV do viewmodel (60° por padrão, 54–68 como no CS; `viewmodel_fov`) e a luz: cópias das luzes do mapa (mesmas
  posições, cores e intensidades, sincronizadas quando o painel muda uma luz), a hemisférica e o ambiente assado — a arma
  escurece fora do feixe da key, como o resto do set.
- Posição por categoria (pistola, rifle, sniper, escopeta, SMG bullpup, faca) em dados (`viewmodel_offset_x/y/z` somam por
  cima), mãos nas âncoras da arma com a pose da âncora, antebraços apontando para cotovelos fixos fora da tela.
- Aparece em primeira pessoa com o `PlayerPawn` (sala de testes, pista); some em terceira pessoa, no noclip, morto e
  quando o item na mão ainda não tem receita (as outras 18 armas até a 4.4, granadas até a 4.7, a bomba até a Fase 8 — o
  HUD continua dizendo o que está na mão). Na 4.1 não anima: segura parado, com o boil "em dois".

### Bancada de armas (mapa `arsenal`)

A mesa do animador (a mesma luz de vitrine) virada em bancada de armeiro: as armas deitadas no tapete de corte em
fileiras por categoria, cada uma com a etiqueta de fita crepe escrita a caneta; na frente, a plataforma giratória com a
arma escolhida em pé num suporte de arame; atrás, a planta de cada arma desenhada a lápis em papel preso com fita (o
contorno da referência, desenhado por nós). Painel de fita crepe (Tab): escolher a arma, facção do acento (para as dos
dois lados), nível (perto/mundo), skin, explodir os grupos, mostrar âncoras, sobrepor a planta à silhueta, "segurar" (o
viewmodel com a câmera parada), triângulos e tempo de geração. Console: `arsenal`, `arma <id>`. A pesquisa visual da
bancada (quadro de ferramentas, suportes, plataforma giratória) entra antes de montá-la.

### Primeiro lote

| Arma | Facção (acento) | Massas | Grupos | Peças principais |
|---|---|---|---|---|
| Glock-18 | TR (terracota/laranja) | grafite, grafiteClaro | corpo, slide, carregador, gatilho | armação com o ângulo da empunhadura e as ondas dos dedos; slide com as serrilhas em cortes; cano aparecendo na frente; miras com os pontos em acento; base do carregador e seletor em acento |
| AK-47 | TR | grafite, madeira, madeiraEscura | corpo, carregador, ferrolho, gatilho | receptor e tampa; coronha, guarda-mãos e empunhadura de madeira; tubo e bloco de gás; massa de mira; freio de boca inclinado; carregador curvo com a base em acento; alavanca à direita |
| M4A4 | CT (azul/verde-água) | grafite, grafiteClaro | corpo, carregador, ferrolho, gatilho | receptores superior e inferior; trilho com os dentes em cortes; torre da massa de mira; guarda-mão redondo; abafador; tubo e coronha retrátil; carregador reto-curvo; alavanca em T; seletor em acento |
| AWP | ambos (amarelo/branco) | verdeOliva, grafite | corpo, carregador, alavanca, gatilho | chassi com o buraco do polegar; cano longo e freio; luneta com as torres; soleira; alavanca com a bola em acento |
| Nova | ambos | grafite, grafiteClaro | corpo, bomba, gatilho | receptor e coronha de uma peça; cano e tubo do carregador; bomba com os sulcos; massa de mira em bolinha de acento |
| P90 | ambos | grafite, grafiteClaro | corpo, carregador, gatilho | corpo bullpup com o buraco da empunhadura e a alça da frente; carregador em cima; mira de anel; seletor em acento |
| Faca | ambos | aco, madeira | corpo | lâmina de espátula em folha (0,5 u, borda arredondada), virola, cabo torneado de madeira |

As outras 18 armas de fogo e a faca de ouro ficam para a 4.4; granadas para a 4.7.

### Console e dados

- `src/data/armas/*.js` (receitas) e `src/data/armas/index.js` (registro), `src/data/weaponPalette.js`,
  `src/data/hands.js`, `src/data/viewmodel.js`, `src/data/arsenal.js`.
- Console: `viewmodel_fov`, `viewmodel_offset_x/y/z`, `r_viewmodel 0/1`, `cl_bracadeira tr|ct|0`, `arsenal`, `arma <id>`,
  `armas` (lista das receitas com triângulos e tempo de geração).

### Testes (Node, sem navegador)

- SDF: `profile`, `lathe` e `tube` contra a distância por força bruta ao contorno amostrado; filete (raio, tangência,
  cantos côncavos); caixa envolvente e intervalo garantidos; malha fechada no marching cubes.
- Receitas: todas as sete validam; grupos, âncoras e massas por arma; espessura mínima; acento pela facção; silhueta
  lateral × planta com IoU ≥ 0,8; o comprimento real na tabela; árvores determinísticas (a mesma chave de cache).
- Mãos: pesos normalizados, cada vértice dos dedos puxado pelo seu osso, poses dentro dos limites das juntas, espelho da
  esquerda.
- Viewmodel: posição por categoria, mãos nas âncoras, cotovelo, quando aparece e some.
- Blender: `npm run blender -- ida-volta <arma>` nas sete (fora da suíte do Node, porque precisa do Blender).

### Aceite da 4.1

- [x] As sete peças geradas no jogo a partir das receitas, na bancada e na mão, com costura, boil, digitais, veios na
  madeira e o acento certo; silhueta × planta com IoU ≥ 0,8 (Glock 0,873, AK 0,931, M4A4 0,937, AWP 0,945, Nova 0,894,
  P90 0,947); espessura mínima respeitada (1,2 u; a lâmina da faca, 0,5 u).
- [x] O caminho do Blender: `abrir`, `conferir` e `ida-volta` funcionando nas sete (ida e volta idêntica byte a byte nas
  sete); exportar depois de uma edição no Blender muda a arma no jogo (a massa de mira da AK ×1,6 no Blender: topo de
  2,017 u → 2,46 u na bancada depois de "Reler a receita do disco").
- [x] Mãos de 4 dedos com rig, segurando cada uma das sete em primeira pessoa na sala de testes e na pista; somem em
  terceira pessoa, no noclip, morto e com a luneta.
- [x] Sem erros do jogo no console, sem vazamento em 3 ciclos menu ↔ arsenal e menu ↔ pista (27/35/35 geometrias,
  texturas e programas no menu nos três), arquivos abaixo de 600 linhas (o maior, `shapes.js`, 541), números em
  `src/data/`, item 13 do moodboard.

### Ajustes feitos na implementação

- **Plantas**: a M4A4 saiu da carabina M4A1 com a alça de transporte (a única foto lateral limpa; a M4A4 do jogo tem a
  mesma silhueta), a AWP da Accuracy International Arctic Warfare (PSG 90 sueco, a mesma família da AWM, escalada para
  48,4 u), a Nova da Benelli M3 Super 90 (a mesma família e o mesmo arranjo; não há foto lateral limpa da Nova no Commons)
  e a Glock-18 da Glock 17 (a mesma arma sem o seletor). As fontes e licenças estão em cada `refs/<id>.json`.
- **Massas**: a madeira usa uma skin de base nova, `veio` (riscada a palito ao longo da peça, cores do risco e da faixa
  clara na massa), e não a "madeira falsa" das skins de jogador; as skins de base ficam fora de `CLAY_SKIN_IDS`. Os
  materiais da biblioteca são por (arma, facção), não por (massa, facção): o boil de cada material segue o tamanho da
  arma.
- **Receitas**: os guarda-matos saíram alargados em relação à planta, para o dedo de massa (raio 0,6 u) caber no vão; as
  âncoras das mãos foram calculadas da geometria da empunhadura de cada arma (a mão direita com os dedos perpendiculares
  ao eixo da empunhadura inclinada, `rot` [π/2, −inclinação, 0], e os nós dos dedos logo à frente da borda dela; a
  esquerda por baixo do guarda-mão, palma para cima e para dentro; o apoio da pistola e o punho da faca).
- **Viewmodel**: `viewmodel_fov` como o do CS — horizontal num quadro 4:3, o vertical fixo (Hor+): 60 dá 46,83° na
  vertical —, os três `viewmodel_presetpos` (1 Mesa 60/1/1/−1, 2 Sofá 54/0/0/0, 3 Clássica 68/2,5/0/−1,5) e a seção "Arma
  na mão" nas configurações; um ajuste fino por arma (`nudge`) somado à categoria (a M4A4 desce por causa da alça); o
  viewmodel some também com a luneta e com `r_viewmodel 0`.
- **Luz do viewmodel**: além das cópias das luzes do mapa, a sombra própria (cada luz que faz sombra no mapa projeta na
  camada, com a câmera de sombra apertada na arma e nos pulsos, mapa de 512 a 1024) e a oclusão pelo set (raios no mundo
  de colisão do centro, da boca e dos pulsos até cada luz, suavizados em 0,08 s subindo e 0,14 s descendo); as camadas do
  pipeline ganharam `beforeRender`/`afterRender`.
- **Braçadeira**: a primeira cor do time (primária, secundária, acento) com ΔE ≥ 30 da massa do braço, senão a mais
  distante — no braço terracota do boneco de referência, a do TR vira o laranja.
- **Recarga da receita** em duas fases (`EV.WEAPON_MODEL` com `relendo` antes do descarte e `pronta` depois): o viewmodel
  e a bancada tiram a instância antiga antes das geometrias saírem da GPU.
- **Serviço `handModels`** (`HandLibrary`): a malha da mão sai uma vez (SDF, cache) e os braços dividem as geometrias
  de cada lado; cada braço só tem esqueleto e materiais próprios.
- **Console**: `viewmodel_presetpos 1|2|3`, `viewmodel_ajuste` (afina a categoria ao vivo, com a linha pronta para colar
  em `src/data/viewmodel.js`) e `bancada` (alias de `arsenal`).
- **Blender**: além do desenho, (1) a **prévia do jogo** — o `tools/blender/previa.mjs` gera no Node a malha que o jogo
  faz da receita (o mesmo SDF, nível `perto`), os braços de massinha de verdade nas âncoras (o rig do jogo, skinning na
  CPU) e a câmera de primeira pessoa do viewmodel; o `conferir` renderiza a prévia (a verdade, com costuras, cortes e
  bordas do SDF) em vez das peças de edição, em seis vistas: lateral com a planta, cima, frente, 3/4, mãos (3/4) e
  primeira pessoa; no painel, o botão "Prévia do jogo" refaz a prévia da cena como está (exporta para um temporário,
  valida e gera pelo jogo), numa coleção que não exporta; (2) a origem de cada peça definida por pontos (perfil, torno,
  tubo, cápsula, cone arredondado) fica no centro dela: escalar e girar acontecem no lugar, mover e escalar voltam aos
  pontos e o `pos` guardado fica, girar leva a peça para o referencial do objeto; (3) um objeto de geometria sem a peça
  guardada recusa a exportação (peça nova é Shift+D de uma da mesma forma); (4) as ações `validar <arquivo>` e
  `previa <arquivo> <saída>` no `tools/blender.mjs`; (5) com janela: sem a tela de abertura (a preferência do usuário
  volta logo depois), vista lateral ortográfica enquadrando a arma e a barra lateral aberta na aba MASSACRE; (6) o Euler
  do exportador pelo atan2 (as matrizes do Blender são float32 e o asin perde 3·10⁻⁴ rad perto de ±90°).

### Medições

- **Node** (thread principal; triângulos e tempo por nível `perto`/`mundo`): Glock 13 066/2 496 (231/46 ms), AK
  54 904/9 694 (1,2 s/207 ms), M4A4 66 168/10 550 (3,6 s/803 ms), AWP 72 540/12 298 (2,1 s/277 ms), Nova 47 828/7 606
  (681/118 ms), P90 47 676/8 794 (824/141 ms), faca 4 360/846 (40/10 ms); a mão 34 880 triângulos (150 ms) e a
  braçadeira 55 488 (101 ms). Comprimentos da silhueta: 7,30 · 34,60 · 33,15 · 48,40 · 39,15 · 19,70 · 7,90 u.
- **Navegador** (RTX 2070, 144 Hz): a camada do viewmodel custa ~1,3–1,6 ms por quadro (0,07 ms de custo fixo com
  a camada vazia; o resto é o ClayMaterial dos braços e da arma); reler uma receita na bancada deixa as geometrias como
  estavam (78 → 78); 3 ciclos menu ↔ arsenal ↔ pista com 27/35/35 no menu, 76/43/51 no arsenal e 68/92/59 na pista
  (geometrias/texturas/programas) nas três voltas, sem erro no console.
- **Blender 5.2.2** (sem janela): `ida-volta todas` idêntica byte a byte nas sete em 11,7 s; o teste de edição (mover,
  escalar e girar peças de cada forma, pontos de perfil, torno e tubo, âncora, pose, massa, grupo, pivô e uma peça
  duplicada) exporta exatamente a receita esperada; `conferir todas` em 48,7 s (6 vistas × 7 armas); com janela, os
  quatro botões do painel rodando e a edição exportada chegando ao jogo.

---

## 4.2 a 4.8 — escopo (o desenho detalhado de cada uma é feito no começo do chat dela)

- **4.2 Tiro e dano.** Pesquisa no código do CS:GO: `FireBullet`, a tabela de recoil gerada por arma
  (`recoil_angle`, `recoil_angle_variance`, `recoil_magnitude`, `recoil_magnitude_variance`, `recoil_seed` com o
  gerador uniforme do Source), `weapon_recoil_*` (a 3.2 já anotou as variáveis), `ScaleDamage` e as constantes de
  blindagem, `HandleBulletPenetration` e os materiais (papelão fino, balsa, massinha, metal de ferramenta com espessura e
  densidade). Hitboxes dos alvos (cabeça, peito e braços, estômago, pernas) no formato que a Fase 5 vai reusar nos
  personagens. O campo de tiro é um mapa novo, com pesquisa no Pinterest no começo da subfase.
- **4.3 Viewmodel stop-motion e efeitos.** Poses-chave por categoria no Blender (o rig da mão completo no importador),
  presas às âncoras; o balanço e a inércia do viewmodel; os efeitos usando o sistema de impressão da 3.5 onde couber
  (amassado na massinha) e deformação de vértices nas peças de massa perto do impacto (seção 0.9).
- **4.4 Arsenal completo.** As outras 18: USP-S, P250, Five-SeveN, Desert Eagle, MAC-10, MP9, UMP-45, XM1014, Galil AR,
  FAMAS, M4A1-S, AUG, SG 553, SSG 08, SCAR-20, G3SG1, Negev, M249; e a faca de ouro (skin ouro sobre a faca).
- **4.5 Mira e acessórios**, **4.6 Faca**, **4.7 Granadas** e **4.8 Sensação e aceite** como na tabela do começo.

## Aceite da Fase 4 (PROMPT, Fase 4)

- [ ] Cada arma tem sensação distinta.
- [ ] Padrões de spray reproduzíveis.
- [ ] Wallbang varia por material.
- [ ] A smoke bloqueia a visão de verdade (inclusive o raycast dos bots).
