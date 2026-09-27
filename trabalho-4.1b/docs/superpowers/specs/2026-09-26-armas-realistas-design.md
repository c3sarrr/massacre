# Armas realistas de metal e luvas — desenho

- **Data:** 2026-09-26
- **Estado:** as sete seções foram aprovadas na conversa, uma a uma, e o documento inteiro foi aprovado pelo usuário em
  2026-09-26; o plano da 4.1a está em `docs/superpowers/plans/2026-09-26-4.1a-pipeline-realista-ak47.md`.
- **Substitui:** a direção de arte da subfase 4.1 ("fiel e gordinha", mãos de 4 dedos de massinha, o Blender gerando a
  receita de SDF e o acento da facção nas armas), registrada em `docs/phases/phase-4.md`.
- **Atualizado na 4.1b (2026-09-26 e 2026-09-27):** sem manga e sem roupa — a luva vai no braço de massinha do próprio
  boneco (desenho da 4.1b, `docs/superpowers/specs/2026-09-26-4.1b-luvas-e-empunhadura-design.md`, seção 0); a mão da
  frente com o polegar reto de um lado e os quatro dedos do outro; texturas CC0 de bibliotecas abertas como base dos
  materiais no Blender. As seções 1, 2, 4.1, 4.4, 5.1, 5.3, 6.5, 7, 8.1 e 8.2 trazem cada mudança no lugar, com o que era.
- **Referências:** `docs/art/moodboard.md`, seção 14 (boards QVM a QMP), e as fotos do Wikimedia Commons da seção 3.
- **Escopo:** o redesenho inteiro das armas e das mãos da Fase 4. Cada subfase da seção 8.1 tem o seu plano de
  implementação; o primeiro é o da 4.1a.

## 0. Por que mudar

O usuário reprovou as armas de massinha da 4.1: feias, sem detalhe, pulsando em vez de paradas e com os dedos tortos na
arma. A revisão dos renders da conferência (AK-47 de lado, 3/4, primeira pessoa e mãos) confirmou e explicou cada
problema:

- O SDF com marching cubes arredonda toda aresta; arma de metal tem aresta viva com chanfro fino. É isso que dá a cara
  de sabonete e de brinquedo.
- A espessura mínima de 1,2 u engrossou o que é fino: a massa de mira virou uma bola, o gatilho um rabisco.
- Nenhum detalhe mecânico (rebites, pinos, nervuras, alça, seletor de verdade, marcações) e um único material fosco:
  metal sem reflexo nunca lê como metal.
- O boil (a forma muda a cada 1/12 s) é o "pulsar" que o usuário viu.
- Dedos em cápsula com o serrilhado do marching cubes, antebraço sem pulso, a mão de apoio atravessando o guarda-mão; em
  primeira pessoa a mão do gatilho nem aparece.

O método da 4.1 (massinha por SDF) não chega numa arma realista: não é ajuste fino, é troca de caminho.

## 1. Decisões do usuário (2026-09-26)

1. **Realismo de fábrica, tipo CS2.** A arma real em peças, medidas e materiais, limpa, com desgaste leve nas bordas;
   descartados o hiper-realismo sujo (CoD MW, Tarkov), o realismo estilizado (Valorant) e o visual de maquete aparente
   (parafusos exagerados, marcas de montagem).
2. **Luva tática de 5 dedos com a manga de tecido da facção** em primeira pessoa. **Atualizado na 4.1b (decisão do
   usuário de 2026-09-26): sem manga e sem roupa** — do punho para trás, o braço é o de massinha do boneco, porque nas
   próximas fases a bala fura o boneco e atravessa o corpo de massa, e o corpo não pode ficar escondido por roupa.
3. **Exceção à regra 4 (e à paridade "100% gerado em código") só para armas e mãos:** scripts Python nossos no
   Blender constroem os modelos e as texturas assadas, entregues como `.glb` e `.webp`. Nenhum modelo é baixado de
   terceiros; o resto do jogo continua 100% procedural. **Atualizado em 2026-09-27 (decisão do usuário):** os scripts
   do Blender podem usar texturas CC0 de bibliotecas abertas (cgbookcase, Poly Haven, ambientCG e o CC0 Asset Index)
   como base dos materiais, e elas chegam ao jogo só assadas no `.webp` (seção 4.4; a lista e as regras ficam na seção
   0.7 do `CLAUDE.md`).
4. **Faca, granadas, carregadores e cápsulas, e lunetas passam a ser realistas.** A espátula, a bola de massa, o pote de
   tinta, o pão de massa, as bolinhas amarelas e o anel de massinha ficam como ideias de skin temática.
5. **Animação suave em primeira pessoa, com a opção "viewmodel em stop-motion"** (a mesma animação a 12 poses/s).
6. **A AK-47 do jogo é a AK-47 tipo 3, de receptor fresado** (não a AKM), no tamanho e no formato reais.
7. **Fidelidade vira regra do pipeline** (ficha por arma, régua sobre a foto real, conferência objetiva da silhueta).
8. **Orçamento de arquivos: detalhe máximo** (decidido depois do `construir` completo da AK na validação do plano da
   4.1a, que mediu 7,1 MB com o WebP sem perdas e sem compressão; o orçamento de 2,5 MB desta seção 5.1 só fecharia com
   as texturas em 1024). As texturas de perto ficam em 2048 sem perdas, com a quantização dos canais de dados em
   degraus que não aparecem no jogo, e a geometria vai com compressão **Draco**: **fuzil 6 MB, pistola 3 MB, faca 2 MB,
   luvas 6 MB** (a AK medida: 5,1 MB). A memória de vídeo não muda.

## 2. Direção de arte

- **Padrão de fábrica.** Cada arma é a variante real escolhida na ficha (seção 3), nas medidas reais (1 u = 1 polegada
  na escala do boneco, como na 4.1), com todas as peças visíveis da arma real: pinos, rebites, parafusos, molas, miras,
  marcações, serrilhas, frestas entre peças. O material segue a peça real: aço oxidado ou fosfatizado, alumínio
  anodizado, polímero texturizado, madeira envernizada, baquelite, borracha, aço polido nas peças internas. O desgaste é
  leve e só onde a mão e o uso encostam (bordas, cantos, a face do gatilho). Critério de revisão herdado do Valorant:
  a arma tem de ler rápido, de qualquer ângulo e em qualquer preset (QVS5, QVS10).
- **Coerência com o estúdio.** A arma é um **adereço de metal em miniatura** feito pelo aderecista do estúdio, como os
  adereços realistas e as roupas de tecido dos bonecos de *O Fantástico Sr. Raposo* (QMP1, QMP5, QMP7, QMP11). O mundo,
  os bonecos, os amassados de tiro na massinha e os efeitos (fumaça de algodão, fogo de celofane, respingos) continuam de
  estúdio.
- **Boil zero** em armas, luvas (e no antebraço de massinha delas no viewmodel, desde a 4.1b), carregadores, cápsulas,
  granadas e lunetas. O resto do mundo mantém o boil (a
  opção de desligar já existe nas configurações).
- **Sem marcas registradas** (regra 9): nenhum logotipo nem nome de fabricante; as marcações são genéricas (letras do
  seletor, números de série, marcas de prova), estampadas no metal.
- **Mãos:** luva tática de 5 dedos na cor da facção, no braço de massinha do boneco, com a braçadeira de massa em modo
  de time (seção 7; era "e manga de tecido na cor do time" até a 4.1b). O "acento da facção" da 4.1 sai das armas: a
  identidade do time fica na luva e na braçadeira.
- **Itens que ficam realistas:** a faca, que é a baioneta M9 (EUA, 1986) de lâmina fixa (seção 3.2), granadas (fragmentação, atordoante,
  fumaça, molotov de garrafa com pano, incendiária e decoy, na 4.7), carregadores de metal ou polímero, cápsulas de
  latão (4.3) e lunetas reais com lente, retícula gravada e sombra de ocular (4.5).
- **Animação:** suave, a 60+ FPS, com a opção "viewmodel em stop-motion" (4.3). O "em dois" continua nos bonecos em
  terceira pessoa, na killcam e nos menus.
- **Inspeção (tecla F):** a "digital do animador" da spec vira uma marca de dedo sutil sobre o metal, visível no
  reflexo (4.3).

## 3. Ficha de fidelidade e régua

### 3.1 Ficha por arma

`tools/blender/refs/<id>.json`, uma por arma, com:

- a **variante real** e as **medidas oficiais** (comprimento, cano, raio de mira, altura) com a fonte de cada número;
- as **fotos de referência** do Wikimedia Commons de licença livre ou domínio público (título, autor, licença, página):
  o lado direito é obrigatório (é o lado do viewmodel); cima e frente quando existirem;
- o **contorno geral** e os **contornos por peça** em milímetros, no referencial da foto (boca do cano em x = 0, eixo
  do cano em y = 0, +X para a boca, +Y para cima), mais os buracos (guarda-mato, frestas);
- as **cores medidas** em cada material (sRGB e linear) e a correção de exposição usada para chegar à cor de fábrica.

As fotos são só lidas no navegador; o projeto guarda apenas números derivados (contornos, medidas, cores) com a ficha da
fonte, como na 4.1.

### 3.2 Primeiro lote

| Arma do jogo | Variante real | Medidas oficiais | Foto de lado |
|---|---|---|---|
| AK-47 | AK-47 tipo 3 (receptor fresado, coronha fixa de madeira) | 870 mm; cano 415 mm; raio de mira 378 mm | "AK-47 assault rifle.jpg" (Ickybicky, domínio público) — já medida |
| Glock-18 | Glock 18 | 186 mm | escolhida na 4.1c |
| M4A4 | carabina M4A1, coronha aberta | 840 mm | escolhida na 4.1c |
| Faca | baioneta M9 (EUA, 1986; decisão do usuário de 2026-09-26): lâmina clip point de 178 mm, guarda com a argola que encaixa na boca do cano, cabo e bainha de polímero; o resto (serrilha do dorso, furo do corta-arame, quadriculado do cabo, pomo com a trava) sai da ficha da 4.1c | 305 mm | escolhida na 4.1c |
| AWP | Accuracy International AWM .338 | 1230 mm | escolhida na 4.1d |
| Nova | Benelli Nova, cano de 18,5" | 995 mm | escolhida na 4.1d |
| P90 | FN P90 | 500 mm | escolhida na 4.1d |

Critério de escolha da foto: lado direito, fundo limpo, a maior resolução disponível (a precisão do contorno é a
resolução da foto: 1 px da foto de 900 px da AK-47 é 1 mm). As plantas da 4.1 de variantes diferentes (AK-47 tipo II,
AW PSG 90, Benelli M3) são substituídas.

### 3.3 Régua

`tools/regua.html` substitui `tools/silhueta.html` (mesma leitura da foto no canvas, mesmo referencial) e acrescenta:

- a foto na escala real com grade em milímetros (linhas a cada 10 mm, rótulos a cada 50 mm), em faixas ampliadas para ler
  os detalhes internos (posição de pinos, seletor, linhas da tampa);
- o eixo do cano medido pelo centro do cano exposto (e não pela boca, que pode ter quebra-chamas oblíquo);
- os perfis de cima e de baixo a cada milímetro, o contorno simplificado e os buracos;
- a média de cor por região marcada (sRGB e linear);
- a saída em JSON no formato da ficha (a régua não grava arquivo: o JSON vai para `tools/blender/refs/<id>.json`).

### 3.4 Critérios de fidelidade

- **Silhueta de lado:** coincidência (IoU) com a foto **≥ 98 % com tolerância de 1 px da foto** — a diferença a até 1
  px da outra silhueta não conta, porque é o ruído do próprio contorno. O IoU bruto também é registrado.
- **Medidas-chave dentro de ±1 %:** comprimento total, cano, raio de mira (entalhe da alça até a massa), altura sem o
  carregador e altura com ele.
- **Cor de fábrica** tirada da foto com a correção de exposição registrada na ficha.
- Contornos lidos de foto de baixa resolução são suavizados (Chaikin) antes de virar peça.

A prova de conceito (seção 11) chegou a 99,1 % com tolerância (95,9 % bruto) na AK-47 tipo 3 e a 97,0 % bruto na AKM
de foto de 0,45 mm/px.

## 4. Pipeline de autoria no Blender

### 4.1 Arquivos

- `tools/blender/armas/` — pacote Python (fonte da verdade dos modelos):
  - `pecas.py`: biblioteca de peças — perfil extrudado com chanfro, perfil suavizado de contorno de foto, torno, varredura
    por curva, caixa, recorte e união booleanos, fileiras (rebites, parafusos, nervuras, dentes de trilho, serrilhas),
    rosca, mola, pino com cabeça, tira em volta de polilinha (nervuras de carregador), afinamento ao longo de um eixo;
  - `materiais.py`: materiais de fábrica procedurais (aço, alumínio, polímero, madeira, baquelite, borracha, aço polido)
    usados para assar e para a conferência;
  - `zonas.py`, `soquetes.py`: marcação de zona por peça e criação dos soquetes e das peças móveis;
  - `assar.py`: modelo alto e de jogo, UV, assar e empacotar texturas; `lod.py`: versões do mundo e de longe;
  - `exportar.py`: glTF, texturas e relatório; `validar.py`: as validações da seção 4.6; `conferir.py`: renders;
  - `maos.py` (as luvas; sem manga desde a 4.1b) e `empunhadura.py` (rig e solver, seção 7) — na 4.1b viraram
    `luvas.py` (o alvo do lançador), os módulos `maos_*.py` (malha, detalhes, modelo alto, rig, poses, medidas,
    contato) e `validar_maos.py`, e o solver em `empunhadura.py` com os módulos `empunhadura_*.py` (regras, arma,
    polegar, pega);
  - um script por arma: `ak47.py`, `glock.py`, `m4a4.py`, `faca.py`, `awp.py`, `nova.py`, `p90.py`.
- `tools/blender.mjs` (o lançador da 4.1) ganha as ações `construir`, `validar`, `conferir` e `abrir` para
  `<arma|maos|todas>`.
- Saída versionada no git (produto do script, regenerável):
  `assets/armas/<id>/<id>.glb`, `<id>_n.webp`, `<id>_m.webp`, `<id>_mundo_n.webp`, `<id>_mundo_m.webp` e
  `<id>.relatorio.json`; `assets/maos/luvas.glb` e as texturas das luvas. O `.blend` não entra no git: é gerado para
  abrir e conferir.

### 4.2 Construção

- A construção é em milímetros, no referencial da ficha; a exportação converte para u (÷ 25,4) e para o referencial da
  arma da 4.1: +X para a boca, +Y para cima, +Z para o lado direito, origem no eixo do cano em cima do gatilho.
- **Zonas** (grupos de material, a base das skins): `corpo` (metal principal), `guarnicao` (madeira ou polímero),
  `carregador`, `detalhes` (miras, gatilho, seletor, pinos, parafusos) e `interno` (ferrolho, alma, molas — só
  acabamentos metálicos).
- **Soquetes** (nós vazios com posição e orientação): `boca`, `ejecao`, `carregador`, `mira_tras` e `mira_frente` (a
  linha de mira), `mao_d` (empunhadura) e `mao_e` (apoio), mais os da categoria (`luneta`, `bomba` da Nova).
- **Peças móveis** como nós próprios, com o pivô no eixo real: `ferrolho`, `carregador`, `gatilho`, `cao`, `seletor` e
  as da arma (bomba da Nova, alavanca do ferrolho da AWP).

### 4.3 Modelo alto, modelo de jogo e LOD

- **Alto:** chanfros com 3–4 segmentos e o microdetalhe só para assar (serrilha, quadriculado, pontilhado do polímero,
  marcações estampadas, costuras).
- **Jogo (LOD0, viewmodel):** chanfros com 1–2 segmentos, faces escondidas removidas, triangulado, normais ponderadas.
- **Mundo (LOD1) e longe (LOD2):** redução por decimação e remoção das peças pequenas, com as mesmas zonas.

### 4.4 UV e texturas assadas

- UV automático por peça (projeção por ângulo + empacotamento, margem de 8 px em 2048), com costuras sugeridas pelas
  peças quando a projeção automática não bastar, e conferência de densidade de texel.
- Assar no Cycles (GPU), do alto para o de jogo: normal em espaço tangente; sombra de contato (com todas as peças juntas,
  para uma sombrear a outra); borda (curvatura) para o desgaste; variação de aspereza; variação de cor (veio da madeira,
  textura do polímero), a partir dos materiais de fábrica.
- **Empacotamento:** `_n` = normal (RGB); `_m` = R sombra de contato, G variação de aspereza, B borda/desgaste, A
  variação de cor. A cor e o tipo de material não ficam na textura: vêm do acabamento (seção 6), o que permite repintar
  qualquer zona. WebP sem perdas, gravado de uma imagem de 8 bits (a de ponto flutuante do Blender divide o RGB pelo
  alfa ao gravar); a sombra de contato e a variação de aspereza passam por um filtro de 1 pixel e os canais de dados são
  quantizados em degraus que não aparecem no jogo (2/255 na sombra, 4/255 na aspereza e na cor; decisão 8).
- **Texturas CC0 de base (decisão do usuário de 2026-09-27):** os materiais de fábrica do Blender podem partir de
  texturas de domínio público (CC0) de cgbookcase (https://www.cgbookcase.com/textures), Poly Haven
  (https://polyhaven.com/textures), ambientCG (https://ambientcg.com/list?type=substance&sort=popular) e do CC0 Asset
  Index (https://github.com/xiaoqianran/Blender-cc0-asset-index) — o grão do couro e do polímero, a trama do tecido, a
  borracha, a madeira, o metal. Só CC0, conferido na página de cada uma; cada textura usada fica registrada em
  `tools/blender/texturas/fontes.json` (site, página, nome, licença, data e resolução) e a ficha do material diz qual
  usou. Elas entram só no assar: o jogo carrega apenas `_n` e `_m`, e a cor continua vindo do acabamento.
- **Tamanhos:** 2048 px para fuzis, escopetas e submetralhadoras e para as luvas; 1024 px para pistolas e a faca; 512
  px (256 nas pistolas e na faca) para as versões do mundo.

### 4.5 Exportação

glTF binário com Y para cima, modificadores aplicados, nós, soquetes, zonas, peças móveis, esqueleto e animações quando
houver (as poses de empunhadura na 4.1b); texturas `.webp` separadas, carregadas pelo jogo. A geometria vai com
compressão **Draco** (`KHR_draco_mesh_compression`; posição em 14 bits, normal em 10, UV e tangente em 12; decisão 8):
na AK, 1,22 → 0,29 MB. As peças de jogo são trianguladas antes da UV e do assar: o exportador só calcula as tangentes
(MikkTSpace) em triângulos e quadriláteros e pula sem aviso a malha com n-gonos.

### 4.6 Validação que bloqueia a exportação

- medidas-chave ±1 % e silhueta ≥ 98 % com tolerância de 1 px da foto, calculadas no próprio Blender (máscara
  renderizada pela câmera ortográfica de lado comparada com o contorno da ficha, em numpy);
- orçamento de triângulos e de texturas da seção 5.1;
- todos os soquetes, zonas e peças móveis da categoria presentes, com os nomes certos;
- malha sem buracos nem faces degeneradas; UV sem sobreposição;
- mãos: nenhum dedo atravessando a arma mais que 0,3 mm e cada ponto de contato a no máximo 1 mm da superfície;
- o resultado vai para `<id>.relatorio.json`, que a suíte do Node confere.

### 4.7 Conferência

Renders em `tools/blender/conferencia/<id>/` (fora do git): lado, cima, frente, 3/4 dos dois lados, primeira pessoa com
as luvas, close-up de cada mão, e a sobreposição da silhueta com a foto (verde = falta no modelo, magenta = sobra). A
revisão crítica compara render e foto lado a lado até não sobrar defeito.

## 5. Formato e renderização no jogo

### 5.1 Orçamentos

| Item | LOD0 (viewmodel) | LOD1 (mundo) | LOD2 (longe) | Texturas LOD0 | Texturas mundo | Arquivos |
|---|---|---|---|---|---|---|
| Fuzil, escopeta, submetralhadora | ≤ 40 mil triângulos | ≤ 6 mil | ≤ 1,5 mil | 2 × 2048² | 2 × 512² | ≤ 6 MB |
| Pistola | ≤ 20 mil | ≤ 3 mil | ≤ 800 | 2 × 1024² | 2 × 256² | ≤ 3 MB |
| Faca | ≤ 8 mil | ≤ 1,5 mil | ≤ 400 | 2 × 1024² | 2 × 256² | ≤ 2 MB |
| Luvas (dois braços; sem manga desde a 4.1b) | ≤ 14 mil | — (Fase 5) | — | 2 × 2048² | — | ≤ 6 MB |

Os orçamentos de arquivos são os da decisão 8 (os de 2,5 / 1,2 / 0,8 / 2,5 MB da primeira versão deste desenho não
fechavam com as texturas de 2048 sem perdas). A AK-47 tipo 3 medida: `.glb` 0,29 MB, `_n` 1,34 MB, `_m` 2,97 MB e o
conjunto do mundo 0,54 MB — 5,1 MB. As luvas medidas na 4.1b: 6 748 triângulos por luva (13 496 nos dois braços),
`luvas.glb` 0,34 MB, `_n` 1,69 MB e `_m` 1,61 MB — 3,6 MB.

Memória de vídeo: o conjunto de alta de um fuzil ocupa cerca de 45 MB (duas texturas de 2048² com mipmaps); só a arma na
mão e as outras do loadout ficam em alta, o resto usa as texturas do mundo.

### 5.2 Carregamento

- `GLTFLoader` e `DRACOLoader` do three r186 entram no `/vendor`: exceção em `tools/vendor.mjs` para
  `loaders/GLTFLoader.js`, `loaders/DRACOLoader.js`, os imports que eles puxam e o decodificador Draco
  (`libs/draco/gltf/`: o navegador baixa o `draco_wasm_wrapper.js` e o `draco_decoder.wasm`, cerca de 0,25 MB, uma vez);
  o resto de `loaders/` continua fora.
- O serviço `weaponModels` (`WeaponLibrary`, `src/weapons/model/weaponLibrary.js`) mantém a interface da 4.1 — `has`,
  `meshes(id, lod)`, `preload(ids, lod)`, `report`, `dispose` e o recarregar a quente depois de exportar do Blender — e
  passa a carregar o `.glb` e as texturas, com cache por id; `recipe(id)` dá lugar a `info(id)` (a ficha e o relatório
  da arma). Enquanto houver armas de massinha (até a 4.1d), a biblioteca atende as duas origens. As armas da rodada são
  pré-carregadas, as outras quando entram em jogo; o `dispose` descarta geometrias, materiais e texturas (conferido com
  `renderer.info`, como na 4.1). Erro de carga aparece no overlay de debug com o arquivo que falhou.

### 5.3 Material

- `MeshPhysicalMaterial` com um trecho próprio de shader (`onBeforeCompile`) que lê `_m` (sombra, aspereza, borda,
  variação de cor) e aplica o acabamento de cada zona. Os recursos do material físico entram só quando o acabamento
  pede (verniz para brilhante, metálico, perolado, madeira e carbono; iridescência para perolado e anodizado;
  anisotropia para aço escovado; brilho de tecido para o tecido das luvas), para limitar as variantes de shader; as
  variantes são compiladas no carregamento, sem travada na primeira aparição.
- Uma função pura converte acabamento + cor + desgaste em parâmetros de material (testável no Node).
- Nenhum boil, nenhuma digital de massinha.

### 5.4 Reflexo do set e luz do viewmodel

- Ao carregar o mapa, uma câmera cúbica (256² por face) fotografa o set a partir de um ponto de referência definido nos
  dados de cada mapa (na altura dos olhos do boneco, no centro da área jogável) e vira o mapa de ambiente (PMREM) de armas
  e luvas: o metal reflete a bancada de verdade. É refeito na troca de mapa.
- O viewmodel ganha uma luz direcional alinhada com a luz principal do mapa, com sombra própria (1024², cobrindo só o
  volume do viewmodel), para as mãos sombrearem a arma; a sombra assada cuida das peças da arma entre si.
- O viewmodel continua na passada separada da 4.1 (`src/weapons/viewmodel/`), com o FOV e os offsets do CS.

### 5.5 Animação

Suave, pelo `AnimationMixer`; a opção `viewmodelStopMotion` (esquema de configurações) toca a mesma animação amostrada a
12 poses/s (entra na 4.3 junto com as animações).

### 5.6 Mundo

As versões LOD1 e LOD2 com as texturas pequenas servem para a arma em terceira pessoa (Fase 5), a arma no chão e a loja.

## 6. Skins de cor e acabamento (estilo Rocket League)

### 6.1 Acabamentos

`src/data/acabamentos.js`, cada um com os parâmetros do material físico:

| Acabamento | Metal | Aspereza | Extras |
|---|---|---|---|
| Oxidado de fábrica | 1,0 | 0,34 | variação fina de aspereza |
| Fosfatizado | 1,0 | 0,55 | microtextura granulada |
| Fosco | 0,0 | 0,85 | — |
| Acetinado | 0,0 | 0,50 | — |
| Brilhante | 0,0 | 0,25 | verniz 1,0 (aspereza 0,05) |
| Metálico | 0,6 | 0,35 | flocos finos no brilho, verniz 0,8 |
| Perolado | 0,2 | 0,30 | iridescência 0,8 (IOR 1,3, filme de 250–600 nm), verniz |
| Anodizado | 1,0 | 0,25 | cor forte no metal, iridescência 0,2 |
| Aço escovado | 1,0 | 0,30 | anisotropia 0,8 ao longo do eixo X da arma |
| Cromado | 1,0 | 0,05 | — |
| Cerakote | 0,0 | 0,70 | microtextura cerâmica |
| Fibra de carbono | 0,0 | 0,35 | trama 2×2 procedural em projeção triplanar, verniz |
| Madeira | 0,0 | 0,45 | veio procedural tingido pela cor, verniz 0,6 |
| Polímero texturizado | 0,0 | 0,65 | pontilhado procedural |
| Borracha | 0,0 | 0,90 | — |

Todo acabamento aceita **desgaste** de 0 a 1: pelo canal de borda, mostra o metal por baixo e sobe a aspereza.

### 6.2 Paleta

`src/data/coresSkin.js`, cores nomeadas como as do Rocket League: Preto #1B1B1D, Branco Titânio #EDEDE8, Cinza Grafite
#4A4E54, Carmesim #9E1B32, Vermelho #D1362F, Laranja #F28F3B, Açafrão #E9A13B, Amarelo #FFD23F, Lima #9BD13B, Verde
Floresta #2F5D3A, Verde-água #3FB8AF, Azul Cobalto #2F4FB5, Azul Celeste #5DADE2, Roxo #6C3FB5, Rosa #E86FA3, Marrom
Siena #8C5A3C, Areia #C2A878, Verde-oliva #5B5F3A, Terracota #C8553D e Azul Tropa #2F6DB5 (as duas últimas e várias
outras vêm dos tokens das facções e da UI).

### 6.3 Skin

- Uma skin é, por zona: acabamento + cor (+ segunda cor quando o acabamento usa duas, como carbono e madeira) + desgaste.
- **"De fábrica"** é a skin padrão de cada arma, com os acabamentos e as cores reais da ficha.
- Três skins de exemplo entram na 4.1a para o aceite: "Anodizado Terracota", "Cromo e Carbono" e "Madeira Clara e Aço
  Escovado".
- Comando de console na bancada `arsenal`: `skin <arma> <zona>=<acabamento>:<cor>[,<cor2>] [desgaste=<0..1>]`,
  `skin <arma> fabrica` e `skin <arma> <nome da skin>`.
- O catálogo, o desbloqueio por nível e conquista e a tela de escolha ficam na Fase 11 (a seção 0.15 da spec é
  atualizada para "cores e acabamentos").

### 6.4 Skins temáticas (futuro) — o contrato

Caneta, lápis, skate, arma de água e outras trocam o modelo inteiro e são feitas no mesmo pipeline, respeitando:

- os mesmos nomes de soquetes, zonas e peças móveis da arma base;
- os soquetes na mesma posição, com tolerância de ±2 mm;
- as superfícies onde a mão encosta a até ±1,5 mm das da arma base — ou a skin traz as próprias poses de empunhadura,
  resolvidas pelo mesmo solver.

### 6.5 Luvas

As luvas também têm zonas, prontas para skins de luva: `couro` (palma, pontas e o reforço entre o polegar e o
indicador), `tecido` (costas e lados elásticos) e `reforco` (o protetor de borracha moldada dos nós, as almofadas e a
tira do punho). A zona `manga` saiu com a manga na 4.1b; a pintura de cada facção fica em `src/data/luvas.js`.

## 7. Mãos: luvas, braço de massinha e empunhadura

(Até a 4.1b: "luvas, mangas e empunhadura". O detalhe do que foi construído está no desenho da 4.1b.)

### 7.1 Modelo

- Proporção humana real (comprimento da mão 190 mm, largura da palma 85 mm), feita por script: um esqueleto de juntas
  com raios (punho, palma, três falanges por dedo, polegar com o metacarpo) vira malha, recebe subdivisão e a forma da
  luva. **Na 4.1b** a malha sai de um gerador de quadriláteros próprio (anéis elípticos em cada junta, portas na palma
  de onde saem os dedos) no lugar do modificador Skin, que torcia os quadriláteros onde os cinco dedos saem da palma.
- Detalhes: protetor de borracha moldada nos nós dos dedos (decisão do usuário de 2026-09-26, no lugar do reforço
  acolchoado), costuras aparentes (geometria no modelo alto, assada no relevo), palma antiderrapante, punho com tira de
  velcro, pontas reforçadas.
- **Sem manga e sem roupa** (decisão do usuário de 2026-09-26; era a manga de tecido com dobras e o punho da manga):
  do punho da luva para trás, o antebraço é de massinha, gerado em código (SDF), na cor da massa do boneco, com as
  digitais, a translucidez e o brilho de massinha e sem boil no viewmodel; a braçadeira do time é uma faixa de massa
  nele, só em modo de time (seção 0.12 da spec).
- Padrão por facção: Massa Crua com a luva coiote (couro `#5C5139`) e Tropa do Estúdio com a luva preta (era: manga
  terracota e luva marrom, manga azul e luva preta).

### 7.2 Rig

Antebraço com osso de torção, mão, polegar (metacarpo e duas falanges), indicador, médio, anelar e mínimo (três
falanges cada) e os metacarpos do anelar e do mínimo para a mão fechar em concha: 20 ossos por braço. Pesos automáticos
com correção nos nós dos dedos e no punho.

### 7.3 Solver de empunhadura

1. A palma é colocada no soquete da mão (`mao_d` no punho, `mao_e` no ponto de apoio da categoria).
2. Cada dedo fecha falange a falange, da base para a ponta, até a polpa encostar na superfície da arma (distância pela
   BVH da malha), dentro dos limites anatômicos de cada junta e sem um dedo atravessar o outro.
3. Regras por categoria: o indicador vai à face do gatilho; o polegar cruza o outro lado do punho; a mão de apoio abraça
   o guarda-mão nos fuzis, segura a bomba na Nova, a empunhadura dianteira na P90, fica sob o guarda-mão na AWP;
   nas pistolas, as duas mãos com os polegares para a frente; na faca, empunhadura de martelo.
   **Mão da frente (regra do usuário de 2026-09-27, válida para toda arma que tem mão da frente):** só o polegar fica de
   um lado da arma e os outros quatro dedos do outro, como a pega da AK no CS:GO — o polegar reto e deitado no lado
   esquerdo, encostado na arma e apontando para a frente, sem curva (a pega "thumb break"), e os quatro dedos abraçando
   por baixo até o lado direito, lado a lado (sem leque); a validação do `construir` reprova a arma que sair diferente
   (desenho da 4.1b, seção 6.2).
4. Correções manuais por arma, quando precisar, ficam no script da arma e passam pelas mesmas validações.

### 7.4 Validação e exportação

- Nenhum dedo atravessando a arma mais que 0,3 mm; cada ponto de contato a no máximo 1 mm; renders de perto de cada
  mão.
- `assets/maos/luvas.glb` leva a malha com esqueleto e as zonas; a pose de empunhadura de cada arma vai no `.glb` da
  arma como o clipe `empunhadura` (as animações da 4.3 entram ao lado).

### 7.5 Consequência na Fase 5

A decisão da 4.1 de mãos de 4 dedos de massinha para os bonecos é substituída: em terceira pessoa, os bonecos de
massinha usam as mesmas luvas, no braço de massinha deles e adaptadas às proporções deles (sem manga desde a 4.1b).

## 8. Subfases e mudanças nas regras

### 8.1 Nova ordem

| Subfase | Conteúdo |
|---|---|
| 4.1 (massinha) | ✅ 2026-09-26 — substituída por este desenho; fica registrada |
| 4.1a | Pipeline realista e a AK-47 tipo 3 no nível final: régua e ficha, biblioteca de peças, construir, assar, exportar e validar; `GLTFLoader` no vendor e o novo `weaponModels`; material com zonas e acabamentos, reflexo do set e luz do viewmodel; a AK na bancada `arsenal` e em primeira pessoa, ainda sem mãos (as de massinha não servem na geometria nova; as luvas chegam na 4.1b); comando `skin` e as três skins de exemplo; atualização das regras e da memória |
| 4.1b | Luvas no braço de massinha do boneco (sem manga e sem roupa, decisão de 2026-09-26), rig e o solver de empunhadura com a mão da frente em "thumb break"; a AK segurada em primeira pessoa, com uma mão só na tela (decisão de 2026-09-27); o rebatedor da bancada |
| 4.1c | Glock-18, M4A4 e a faca — a baioneta M9 (EUA, 1986) — no caminho provado, com as empunhaduras |
| 4.1d | AWP (com a luneta real), Nova e P90, com as empunhaduras |
| 4.2 | Tiro e dano, como no plano |
| 4.3 | Animações suaves e a opção stop-motion; carregador de metal e cápsulas de latão que quicam e param no chão (e amassam a massinha do cenário); a marca de dedo na inspeção; efeitos de estúdio |
| 4.4 | O resto do arsenal no caminho provado (dividido em quantos chats o detalhe pedir) |
| 4.5 | Lunetas reais (lente, retícula gravada, sombra de ocular), miras da AUG e da SG 553, rajada, silenciadores |
| 4.6 | Faca: golpes, bloqueio, parry e dash, como no plano |
| 4.7 | Granadas reais com a física e os efeitos de estúdio |
| 4.8 | Sensação e aceite |

### 8.2 O que sai e o que fica da 4.1

A troca é em etapas, para nenhuma subfase deixar arma faltando nem pôr placeholder no lugar:

- **4.1a:** sai a receita de massinha da AK (`src/data/armas/ak47.js`) e a planta antiga dela; a `WeaponLibrary` passa a
  servir a AK pelo `.glb` e as outras seis ainda pelo gerador de massinha.
- **4.1b:** as luvas substituem as mãos de massinha na AK; as armas ainda de massinha continuam com as mãos de massinha.
  O antebraço de massinha das luvas (`src/characters/hands/antebracoMassa.js`) e a braçadeira de massa (`armband.js`)
  são o braço do boneco: ficam depois da 4.1d.
- **4.1c e 4.1d:** cada arma refeita perde a receita e a planta antigas. No fim da 4.1d saem de vez o gerador de SDF das
  armas (`src/weapons/model/recipe.js`, `silhouette.js`, `weaponModel.js`), as receitas restantes, as mãos de 4 dedos
  de massinha (`src/characters/hands/handShape.js`, `handRig.js`, `handSkin.js`, `handLibrary.js` e
  `src/data/hands.js` — não a pasta inteira, que desde a 4.1b tem as luvas, o antebraço e a braçadeira), a paleta de
  massinha das armas (`src/data/weaponPalette.js`) e o importador e exportador de receita do Blender
  (`tools/blender/massacre/`, `tools/blender/massacre_armas.py`), com os testes deles.
- **Fica:** as formas novas do SDF (perfil, torno, tubo), que servem para o cenário; o viewmodel (`src/weapons/viewmodel/`,
  `src/data/viewmodel.js`); a bancada `arsenal`; o lançador `npm run blender` e o conversor de eixos; a
  `tools/silhueta.html`, que evolui para a régua.

### 8.3 Regras e documentos (atualizados na 4.1a)

- `CLAUDE.md.md` e `CLAUDE.md`: exceção nas regras 3 e 4 e na linha "100% gerado em código" da tabela de paridade, só
  para armas e mãos; seção 0.7 reescrita (estilo de fábrica, faca, carregador, cápsulas, luneta); seção 0.12 (viewmodel
  suave com a opção stop-motion); seção 0.13 (loja com a arma realista na mini-bancada; ícones do killfeed gerados da
  silhueta do `.glb`); seção 0.15 (skins de cor e acabamento); textos das Fases 4, 5 e 11.
- `docs/phases/phase-4.md` (nova tabela de subfases e as decisões de 2026-09-26), `docs/PROGRESS.md` e a memória
  (`massacre-workflow-rules`: "o Blender gera os modelos das armas e das mãos por script").
- **Atualizados na 4.1b:** as regras 3 e 4 e a tabela de paridade falam em luvas (do punho para trás, o braço de
  massinha); a seção 0.7 "Mãos" (sem manga e sem roupa, a regra da mão da frente) e a nova "Texturas CC0 no Blender"
  (2026-09-27); a seção 0.12 com o "sem roupa por enquanto" e o motivo; este desenho (seções 1, 2, 4, 5.1, 5.3, 6.5, 7,
  8.1 e 8.2).

## 9. Testes e aceite

### 9.1 Suíte do Node

- Validador do `.glb` (lê o bloco JSON do binário): soquetes, zonas e peças móveis por categoria, triângulos por LOD,
  existência e tamanho das texturas (cabeçalho do WebP) e os limites do `<id>.relatorio.json`.
- Esquema dos acabamentos, da paleta e das skins (acabamento e zona existentes, cores válidas).
- Conversão acabamento → parâmetros de material (função pura).
- Cache e descarte do `weaponModels` com um carregador falso.
- O vendor tem o `GLTFLoader`, o `DRACOLoader` e o decodificador Draco; o `.glb` sai com o Draco e com as tangentes.

### 9.2 Blender

As validações da seção 4.6 em todo `construir`, com o relatório gravado ao lado dos arquivos.

### 9.3 Navegador (bancada `arsenal`)

Renders de cada vista e da primeira pessoa; 60 FPS no preset Alto medido na RTX 2070 (GPU integrada estimada com
margem, como o item já aberto na memória do projeto); memória estável depois de trocar de arma 20 vezes; boil zero;
troca de skin ao vivo pelo console; sem erro no console.

### 9.4 Aceite

- **4.1a:** a AK-47 tipo 3 no jogo com a pintura de fábrica e as três skins de exemplo; todas as validações passando; o
  render do jogo e o do Blender lado a lado sem diferença de forma; a revisão crítica comparando com as fotos até não
  sobrar defeito.
- **4.1b:** a AK segurada em primeira pessoa com as luvas, sem dedo atravessando nem flutuando, nas duas facções.
- **4.1c e 4.1d:** cada arma com a ficha completa e as mesmas validações, empunhadura incluída.

## 10. Riscos e respostas

- **Qualidade da geometria por script.** Depende de iteração: as métricas de fidelidade e a revisão por renders
  apontam o erro com número. Nível fotográfico de CoD/Tarkov não é a meta (decisão 1).
- **UV automático.** Pode dar densidade irregular: conferência de densidade e das texturas assadas, com costuras
  sugeridas por peça quando precisar.
- **Tempo de assar.** O assar usa uma cópia juntada do modelo alto como fonte única (uma árvore de raios em vez de uma
  por peça): a AK inteira sai em cerca de 80 s na RTX 2070 (eram 13 min com as peças separadas); o `construir` só refaz
  o que mudou (hash das entradas).
- **Tamanho e memória de vídeo.** Os orçamentos da seção 5.1 (decisão 8), a quantização dos canais de dados, o Draco,
  as texturas do mundo e o descarte ao liberar.
- **Diferença entre o Cycles e o tempo real.** Sombra assada, reflexo do próprio set e luz com sombra no viewmodel; o
  aceite compara o render do Blender com a captura do jogo.
- **Licença das referências.** Só números derivados entram no projeto, sempre com a ficha da fonte e a licença.
- **Casos difíceis do solver** (polegar, dedos colidindo). Limites das juntas, teste entre dedos e correção manual por
  arma validada igual.
- **Escopo da exceção à regra 4.** Vale só para armas e mãos; qualquer outro modelo em arquivo precisa de nova decisão do
  usuário.

## 11. Prova de conceito (registro)

Feita no rascunho da sessão (fora do projeto), com scripts Python rodando no Blender 5.2.2 e render no Cycles:

- **v1:** AKM com proporções no olho. Forma e detalhe mecânico funcionaram por script (chanfro, rebites, nervuras,
  seletor, covinha, furos, orelhas da massa, quebra-chamas), mas a exposição saiu estourada na primeira render e as
  proporções erradas (raio de mira de 404 mm contra 378 mm reais). Motivou a ficha de fidelidade.
- **v2:** AKM reconstruída sobre a foto do Armémuseum (0,45 mm/px) pela régua, com as cores tiradas da foto: 97,0 % de
  silhueta.
- **v3:** AK-47 tipo 3 (escolha do usuário) sobre "AK-47 assault rifle.jpg" (1 mm/px): 95,9 % bruto e 99,1 % com a
  tolerância de 1 px da foto, que passou a ser o critério. Contornos da foto de baixa resolução suavizados (Chaikin).
- **O que ficou mediano e cabe à 4.1a:** materiais (madeira chapada, aço limpo demais), quadriculado do punho e as linhas
  e marcações do receptor.

## 12. Referências

- Moodboard: `docs/art/moodboard.md`, seção 14 (QVM a QMP) e a folha `docs/art/moodboard.html`.
- Fotos do Wikimedia Commons (só lidas no navegador): "AK-47 assault rifle.jpg" (Ickybicky, domínio público) e
  "AKM automatkarbin Ryssland - 7,62x39mm - Armémuseum rightside noBG.png" (Armémuseum, CC BY-SA 4.0).
- Medidas: artigos AK-47 e AKM da Wikipédia (870 e 880 mm, cano de 415 mm, raio de mira de 378 mm).
- Riot Games, "VALORANT Shaders and Gameplay Clarity" (https://technology.riotgames.com/news/valorant-shaders-and-gameplay-clarity);
  entrevista de Moby Francke à Inverse sobre a arte do Valorant.
- Rocket League Wiki, "Paint Finish" (https://rocketleague.fandom.com/wiki/Paint_Finish).
- Polycount, discussões sobre pose de mãos em primeira pessoa (https://polycount.com/discussion/180905/how-to-actually-pose-hands).
