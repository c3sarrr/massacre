# MASSACRE — regras do projeto (PROMPT 0 Mestre)

> Arquivo gerado a partir de `CLAUDE.md.md` (fonte completa com os prompts de cada fase).
> Estado atual, decisões e mapa de arquivos: `docs/PROGRESS.md`. Bíblia visual com referências do Pinterest: `docs/art/moodboard.md`.
> Regra do usuário: nunca simplificar nada; sempre buscar referências de design e estética no Pinterest antes de trabalho visual.
> Texturas e modelos para o Blender (seção 0.7): **sempre que precisar de uma textura, consulte primeiro as bibliotecas CC0** — Poly Haven, ambientCG, 3D Textures, cgbookcase e o CC0 Asset Index (liberadas pelo usuário em 2026-09-27 e 2026-10-01); ShareTextures e Textures.com só como consulta (as licenças proíbem redistribuir o arquivo, e o repositório é público). Das armas da 4.1d em diante, o modelo pode partir de uma arma CC0 pronta do Blend Swap (decisão de 2026-10-01). Lista, regras e proveniência na seção 0.7, "Texturas CC0 no Blender" e "Modelos CC0 prontos de armas".

## PROMPT 0 — MESTRE

### 0.1 Papel

Você é um estúdio sênior inteiro em uma pessoa: engenheiro de gameplay, técnico de arte (shaders GLSL e pós-processamento em three.js), game designer de FPS competitivo, especialista em IA de jogos e engenheiro de rede em tempo real. Você escreve código de produção, modular, comentado e com desempenho medido.

### 0.2 Objetivo

Construir **MASSACRE**, um FPS multiplayer de navegador em **HTML + JavaScript (ES Modules) + three.js** para jogar online com amigos.

- **Gameplay e sistemas:** idênticos em escopo e sensação ao **Doodle District** (https://doodleshooter.vercel.app/ — código de referência: https://github.com/sarvan-2187/doodleshooter), expandidos com o arsenal, a economia e os modos no estilo Counter-Strike.
- **Estética:** totalmente diferente. Sai o "caneta azul no caderno", entra **CLAYMATION / MASSINHA DE MODELAR em um SET DE ESTÚDIO DE STOP-MOTION**. O jogador é um boneco de massinha lutando em cenários de miniatura montados em cima de uma bancada de animador.

### 0.3 O que replicar da referência (paridade obrigatória)

Tudo isto existe no Doodle District e **precisa existir no MASSACRE**, adaptado:

| Referência (Doodle District) | MASSACRE |
|---|---|
| 100% gerado em código: sem arquivos de imagem, modelo ou áudio | Igual, com uma exceção decidida em 2026-09-26: **as armas e as mãos** (as luvas; do punho para trás, o braço é o de massinha do boneco) são modelos realistas construídos por scripts Python nossos no Blender (`tools/blender/armas/`) e entram no jogo como `.glb` + texturas `.webp` assadas (`assets/`). Desde 2026-09-27 o Blender pode usar texturas CC0 das bibliotecas abertas da seção 0.7 como base dos materiais, e elas chegam ao jogo só assadas no `.webp`; desde 2026-10-01, as armas da subfase 4.1d em diante podem partir de um modelo pronto **CC0** (o Blend Swap, seção 0.7), adaptado pelos nossos scripts ao mesmo pipeline e à mesma validação — nenhum outro modelo de terceiros entra. O resto — geometria, texturas (canvas/shader), personagens, mapas, música e efeitos sonoros — continua procedural |
| FPS 3D em three.js | Igual |
| Multiplayer P2P via WebRTC/PeerJS, sem servidor de jogo, até 10 jogadores | Igual, com melhorias de netcode (seção 0.10) |
| Lobby: jogo rápido, sala pública/privada, reentrar na partida | Igual + convite por link e código de sala |
| Host guarda o placar, cada jogador simula o próprio corpo | Host autoritativo para placar, dano, economia, rodadas e bots |
| Modo solo em ondas, chefe a cada 5 ondas, checkpoints | Igual (modo "Ondas") com inimigos e chefes de massinha |
| 7 tipos de inimigo + 3 chefes | 7 tipos + 3 chefes reimaginados em massinha (seção 0.8) |
| Rifle, shotgun, sniper com luneta, katana com bloqueio/parry e dash, granada com carga | Arsenal completo estilo CS (seção 0.7) + a faca herda o bloqueio/parry da katana |
| Movimento rápido: pulo, wall-jump, slide, air-dash, gancho | Movimento **híbrido** (seção 0.6): base tática do CS + slide e wall-jump. Sem gancho |
| 2 mapas com props destrutíveis e itens de vida temáticos | 3 mapas de estúdio (seção 0.9), com props destrutíveis |
| Música e trilha procedurais | Igual, com identidade própria (seção 0.13) |
| Mouse/teclado, controle PS5, touch com botões personalizáveis e sensibilidade | Igual, para PC, controle e celular |

### 0.4 Regras invioláveis

1. **Nunca simplifique.** Não reduza escopo, não troque sistemas por versões "básicas", não pule itens das listas. Se algo for grande demais para uma resposta, divida em partes e continue na próxima, sem cortar.
2. **Proibido placeholder.** Nada de `// TODO`, "implementar depois", cubos cinza, funções vazias, dados falsos ou "exemplo simplificado". Todo código entregue roda e está completo.
3. **Design e estética em primeiro lugar.** Cada elemento visível (boneco, mapa, HUD, menu, efeito, fonte) precisa parecer massinha de modelar filmada em stop-motion. Nada de visual genérico de "jogo de programador". **Exceção (2026-09-26): as armas e as luvas que as seguram são realistas** — metal, madeira e polímero de fábrica, couro sintético, tecido e borracha, muito detalhados e fiéis à arma real em tamanho e forma —, como adereços de metal em miniatura feitos pelo aderecista do estúdio (seção 0.7); do punho para trás, o braço é o de massinha do boneco; as skins delas são de cor e acabamento (seção 0.15).
4. **Tudo procedural.** Sem baixar imagens, GLB, fontes decorativas ou áudio. Fontes do sistema/Google Fonts só como base; letreiros decorativos são geometria de massinha. **Exceção (2026-09-26), só para as armas e as luvas:** os modelos são construídos por scripts Python nossos no Blender (`tools/blender/armas/`, a partir de números medidos em fotos de licença livre) e exportados como `.glb` + `.webp` em `assets/`; qualquer outro modelo em arquivo precisa de nova decisão do usuário. **Modelos CC0 prontos (decisão do usuário de 2026-10-01), só para as armas da 4.1d em diante:** o script da arma pode partir de um modelo CC0 baixado (o Blend Swap, seção 0.7) em vez de modelar do zero, com a mesma ficha, as mesmas peças, zonas, soquetes e LODs e a mesma validação de medida e silhueta; as já construídas (AK-47, Glock-18, M4A4 e a M9) continuam como estão. **Texturas CC0 no Blender (decisão do usuário de 2026-09-27; os sites ampliados em 2026-10-01):** os scripts do Blender podem usar texturas de domínio público (CC0) das bibliotecas abertas listadas na seção 0.7 como base dos materiais das armas e das luvas — sempre que precisar de uma textura, consulte primeiro essas bibliotecas; elas chegam ao jogo só assadas nas texturas `.webp`.
5. **Arquitetura modular** (seção 0.5). Nenhum arquivo acima de ~600 linhas; separe por responsabilidade.
6. **Desempenho é requisito.** 60 FPS em desktop médio (GPU integrada recente) com 10 jogadores + bots; 30+ FPS em celular intermediário no preset "Leve". Meça e exiba no overlay de debug.
7. **Dados de balanceamento em arquivos de configuração** (`/src/data/*.js`), nunca espalhados no código.
8. **Ao fim de cada fase**, entregue: lista de arquivos criados/alterados, como testar, checklist de aceite marcado e o que a próxima fase vai construir.
9. **Nomes e marcas:** as armas usam nomes genéricos do mundo real (AK-47, AWP etc.). Não use logos, nomes de mapas ou marcas registradas do Counter-Strike. Os mapas são originais.

### 0.5 Stack e arquitetura

- **Sem etapa de build obrigatória:** `index.html` + ES Modules + `importmap`. Bibliotecas em `/vendor` com versão fixa (servidas localmente, sem depender de CDN em runtime). Script `npm run dev` opcional com servidor estático.
- **Bibliotecas permitidas:**
  - `three` (versão estável mais recente, fixada) + `three/addons` (EffectComposer, passes, SMAA/FXAA, BufferGeometryUtils, SimplexNoise)
  - `three-mesh-bvh` para colisão e raycast rápidos
  - `peerjs` para WebRTC
  - `recast-navigation` (WASM) para gerar navmesh, ou navmesh própria com A*. Opcional: `yuka` para steering
  - Nada além disso sem justificar.
- **Estrutura de pastas:**

```
/index.html
/styles/          (css da UI, tokens de design)
/vendor/          (three, peerjs, bvh, recast — versões fixas)
/src/
  main.js
  core/           (loop de passo fixo, tempo, eventos, config, save em IndexedDB, rng com seed)
  render/         (renderer, câmera, iluminação de estúdio, pós-processamento, presets de qualidade)
  clay/           (ClayMaterial, geradores de geometria de massinha, "boil", impressões digitais, stop-motion)
  input/          (teclado/mouse, gamepad, touch, remapeamento)
  physics/        (controlador de personagem, colisão BVH, hitscan, projéteis, penetração)
  player/         (movimento, câmera FPS, viewmodel, vida/colete)
  weapons/        (definições, disparo, recoil, spread, recarga, inspeção, granadas, faca)
  characters/     (bonecos de massinha, facções, criador de personagem, animação, hitboxes)
  maps/           (3 mapas de estúdio, destrutíveis, spawns, bomb sites, navmesh)
  ai/             (percepção, memória, navegação, behavior tree, tática, economia dos bots, níveis)
  modes/          (Mata-mata FFA, Mata-mata em Times, Competitivo, Gun Game, Ondas)
  economy/        (dinheiro, loja, recompensas)
  net/            (PeerJS, lobby, protocolo binário, snapshots, interpolação, predição, lag compensation, migração de host)
  ui/             (menus, HUD, loja, placar, killfeed, radar, chat, configurações, touch layout)
  audio/          (síntese WebAudio: armas, passos, massinha, UI, música generativa)
  progression/    (XP, patentes, skins, estatísticas, conquistas)
  replay/         (gravação de snapshots, killcam, destaques)
  data/           (armas, economia, patentes, níveis de bot, conquistas, paletas)
  debug/          (overlay FPS/ms/draw calls, visualização de navmesh e hitboxes, console)
/tests/           (testes de lógica pura: economia, dano, recoil, protocolo)
```

- **Loop de simulação** em passo fixo de 64 Hz (tick estilo CS), render desacoplado com interpolação.
- **Determinismo:** RNG com seed para spread e eventos de rodada (útil para replay e rede).

### 0.6 Movimento (híbrido)

Unidades: 1 unidade = 1 cm na escala do boneco (o boneco tem ~72 unidades de altura; o set é gigante em volta dele).

- **Base tática estilo CS:** velocidade máxima depende da arma na mão (faca 250, pistolas ~240, rifles ~215–225, AWP 200, com luneta 100, LMG ~195). Andar silencioso (Shift) a ~52% da velocidade. Agachar (Ctrl) reduz a velocidade e melhora a precisão. Aceleração/atrito com `sv_accelerate`/`sv_friction` configuráveis. Air-strafe e **bunny hop** possíveis, com penalidade de velocidade para não virar abuso.
- **Precisão:** o spread aumenta com velocidade, pulo e disparo contínuo. Parar (counter-strafe) devolve a precisão rápido.
- **Da referência:** **slide** (correr + agachar, dura ~0,6 s, com cooldown) e **wall-jump** (1 por contato de parede, reseta ao tocar o chão). Sem air-dash e sem gancho.
- **Feel de massinha:** ao pousar de uma queda, o boneco "achata" (squash) e volta (stretch). Pegadas deixam marcas leves no chão de massinha que somem com o tempo.
- **Dano de queda** a partir de ~420 unidades de altura.

### 0.7 Arsenal, dano e economia

**Hitboxes:** cabeça ×4, peito/braços ×1, estômago ×1,25, pernas ×0,75. O capacete protege a cabeça (exceto contra AWP e armas com penetração de blindagem alta, conforme a tabela). O colete reduz o dano pelo valor de **penetração de blindagem**.

**Penetração de parede (wallbang):** cada material do mapa tem uma espessura/densidade (papelão fino, madeira balsa, massinha, metal de ferramenta). O dano cai conforme o material atravessado e o poder de penetração da arma.

**Recoil:** cada arma automática tem um **padrão de spray fixo** (sequência de offsets, estilo CS) mais uma pequena variação aleatória. O padrão pode ser aprendido e é exibido no menu de inspeção da arma.

Valores base (referência inicial de balanceamento, ajustáveis em `/src/data/weapons.js`):

| Arma | Categoria | Preço | Dano | Pen. colete | RPM | Pente/Reserva | Recompensa por kill |
|---|---|---|---|---|---|---|---|
| Faca | Corpo a corpo | — | 40 / 65 (golpe forte) | 85% | — | — | $1500 |
| Glock-18 | Pistola | $200 | 30 | 47% | 400 | 20/120 | $300 |
| USP-S | Pistola | $200 | 35 | 50,5% | 352 | 12/24 | $300 |
| P250 | Pistola | $300 | 38 | 64% | 400 | 13/26 | $300 |
| Five-SeveN | Pistola | $500 | 32 | 91% | 400 | 20/100 | $300 |
| Desert Eagle | Pistola | $700 | 53 | 93% | 267 | 7/35 | $300 |
| MAC-10 | SMG | $1050 | 29 | 57,5% | 800 | 30/100 | $600 |
| MP9 | SMG | $1250 | 29 | 60% | 857 | 30/120 | $600 |
| UMP-45 | SMG | $1200 | 35 | 65% | 666 | 25/100 | $600 |
| P90 | SMG | $2350 | 26 | 69% | 857 | 50/100 | $300 |
| Nova | Shotgun | $1050 | 26 ×9 bagos | 50% | 68 | 8/32 | $900 |
| XM1014 | Shotgun | $2000 | 20 ×6 bagos | 80% | 171 | 7/32 | $600 |
| Galil AR | Rifle | $1800 | 30 | 77,5% | 666 | 35/90 | $300 |
| FAMAS | Rifle | $2050 | 30 | 70% | 666 (+rajada) | 25/90 | $300 |
| AK-47 | Rifle | $2700 | 36 | 77,5% | 600 | 30/90 | $300 |
| M4A4 | Rifle | $3000 | 33 | 70% | 666 | 30/90 | $300 |
| M4A1-S | Rifle | $2900 | 38 | 70% | 600 | 20/80 | $300 |
| AUG | Rifle (mira) | $3300 | 28 | 90% | 666 | 30/90 | $300 |
| SG 553 | Rifle (mira) | $3000 | 30 | 100% | 545 | 30/90 | $300 |
| SSG 08 (Scout) | Sniper | $1700 | 88 | 85% | 48 | 10/90 | $300 |
| AWP | Sniper | $4750 | 115 | 97,5% | 41 | 5/30 | $100 |
| SCAR-20 / G3SG1 | Sniper auto | $5000 | 80 | 82,5% | 240 | 20/90 | $300 |
| Negev | Metralhadora | $1700 | 35 | 71% | 800 | 150/300 | $300 |
| M249 | Metralhadora | $5200 | 32 | 80% | 750 | 100/200 | $300 |

**Utilitários:** Colete $650, Colete + Capacete $1000, Kit de desarme $400 (só CT), HE $300, Flash $200, Smoke $300, Molotov $400 (TR) / Incendiária $600 (CT), Decoy $50. Limite de 4 granadas, no máximo 2 flashes.

**Estilo das armas** (decisão de 2026-09-26; desenho em `docs/superpowers/specs/2026-09-26-armas-realistas-design.md`):
- **Realistas, de fábrica, tipo CS2:** a variante real escolhida na ficha de fidelidade de cada arma, nas medidas reais, com todas as peças visíveis (pinos, rebites, parafusos, molas, miras, serrilhas, frestas entre peças) e marcações genéricas estampadas (regra 9: nenhum logotipo nem nome de fabricante). O material segue a peça real — aço oxidado ou fosfatizado, alumínio anodizado, polímero texturizado, madeira envernizada, baquelite, borracha, aço polido nas peças internas — com desgaste leve só onde a mão e o uso encostam. São adereços de metal em miniatura feitos pelo aderecista do estúdio, dentro do mundo de massinha.
- **Fidelidade com número:** ficha por arma (variante, medidas oficiais com a fonte, contornos medidos com a régua sobre fotos de licença livre); o `construir` do Blender só exporta com as medidas-chave a ±1 % e a silhueta de lado ≥ 98 % da foto.
- **Construção:** um script Python por arma no Blender (`tools/blender/armas/`), o modelo alto assado no de jogo (normal, sombra de contato, borda, variações), três níveis de detalhe, zonas de material (`corpo`, `guarnicao`, `carregador`, `detalhes`, `interno`), soquetes (boca, ejeção, carregador, miras, mãos) e peças móveis com o pivô real. **Sem boil** nas armas, mãos, carregadores, cápsulas, granadas e lunetas. **Construção determinística (pedido do usuário de 2026-10-01):** cada cópia com os modificadores aplicados passa pela forma canônica (`tools/blender/armas/canonica.py`: as posições na grade de 1 µm, os vértices e os polígonos em ordem lexicográfica, os atributos e as UVs junto) antes de juntar, triangular, dizimar, desdobrar as UVs e assar — o booleano exato e os chanfros do Blender devolvem a mesma malha em ordem diferente a cada execução, a superfície do perto mudava até 0,09 mm e a pega das luvas mudava com ela. As entradas também: cada peça ao nascer e todas as malhas no `finalizar` (as peças e os cortadores dos booleanos) passam pela ordem canônica sem mexer nas posições (`canonizar(me, grade=False)`), porque o bmesh devolve as mesmas formas em outra ordem e o booleano exato errava conforme a ordem da entrada (a soleira da AK vazia, o quebra-chamas da M4A4 com arestas soltas); na grade de 1 µm, as entradas arredondadas faziam o booleano errar em outras peças. Peça nova entra pelo mesmo caminho.
- **Texturas CC0 no Blender (decisão do usuário de 2026-09-27; os sites ampliados em 2026-10-01):** os scripts do Blender podem pegar texturas de domínio público (CC0: sem atribuição obrigatória, uso comercial e modificação livres) como base dos materiais das armas e das luvas — o grão do couro e do polímero, a trama do tecido, a borracha, a madeira, o metal oxidado ou fosfatizado — nestas bibliotecas abertas:
  - **Poly Haven** — https://polyhaven.com/all (todos os recursos; as texturas em https://polyhaven.com/textures, por exemplo plástico e borracha: https://polyhaven.com/textures/plastic-rubber) — CC0;
  - **ambientCG** — https://ambientcg.com/ (materiais CC0; a lista: https://ambientcg.com/list?type=substance&sort=popular);
  - **3D Textures** — https://3dtextures.me/ (texturas PBR CC0; alguns pacotes só no Patreon do autor);
  - **cgbookcase** — https://www.cgbookcase.com/textures (texturas PBR CC0);
  - **CC0 Asset Index** — https://github.com/xiaoqianran/Blender-cc0-asset-index (catálogo de ~2 500 recursos CC0 validados, com a ferramenta `cc0a` que busca e baixa cada um com o `LICENSE.json` da proveniência).

  Como usar: só CC0, conferido na página de cada textura; cada textura usada fica registrada em `tools/blender/texturas/fontes.json` (site, página, nome, licença, data e resolução), com os arquivos ao lado, e a ficha do material diz qual usou e por quê. A textura entra só no Blender: o `construir` a assa com o resto e o jogo carrega apenas o `.webp` assado. Os modelos (`.blend`, `.glb`, `.fbx`) desses sites de textura continuam fora (os modelos prontos de armas seguem o item abaixo), e o resto do jogo (set, massinha, personagens) continua procedural (regra 4).

  **Regra do usuário (2026-10-01): sempre que precisar de uma textura, consulte primeiro estas bibliotecas** — escolha nelas antes de pintar ou gerar o material à mão, e registre a escolha (ou por que nenhuma serviu) na ficha do material.

  **Só para consulta, fora do projeto** (licenças conferidas em 2026-10-01): **ShareTextures** — https://www.sharetextures.com/textures (licença própria "baseada em CC0": uso comercial livre e sem crédito, mas proíbe redistribuir o arquivo em outros sites e baixar por script) e **Textures.com** — https://www.textures.com/library (licença proprietária: pede conta e créditos; permite usar em jogo, proíbe redistribuir). O repositório do projeto é público no GitHub e o `construir` precisa do arquivo ao lado, no git (o md5 no `fontes.json`): por decisão do usuário de 2026-10-01, os arquivos desses dois não entram — servem para comparar e achar a referência de um material.
- **Modelos CC0 prontos de armas (decisão do usuário de 2026-10-01), da 4.1d em diante:** o Blend Swap — https://blendswap.com/3d/weapons — tem armas em `.blend` com a licença de cada modelo (CC-0, CC-BY, CC-BY-SA, CC-BY-NC ou a GAL, licença própria do site); só **CC-0** entra, conferido na página do modelo (o CC-BY obriga o crédito, o CC-BY-SA a mesma licença no jogo, o CC-BY-NC proíbe o uso comercial). O download pede conta: o usuário baixa e põe o `.blend` em `tools/blender/modelos/<arma>/`, registrado em `tools/blender/modelos/fontes.json` (página, autor, licença, data, versão do Blender e md5). O script da arma parte dele — separa as peças móveis com o pivô real, as zonas, os soquetes, o modelo alto e o de jogo, os LODs e o assar — e passa pela mesma ficha e pela mesma validação (medidas-chave a ±1 %, silhueta de lado ≥ 98 %, regra 9: tira os logotipos e os nomes de fabricante); o modelo que não passar fica de fora e a arma é modelada do zero, como as da 4.1c. As quatro da 4.1c (AK-47, Glock-18, M4A4 e a M9) ficam como estão.
- **Carregador** de metal ou polímero de verdade, que o boneco tira e põe de volta na recarga. **Cápsulas** de latão que quicam e param no chão, amassando de leve a massinha do cenário.
- **Luneta da AWP/Scout:** a luneta real, com a lente, a retícula gravada e a sombra da ocular ao mirar.
- **Inspeção (tecla F):** o boneco gira a arma e aparece, sutil, a marca do dedo do "animador" no metal, visível no reflexo.
- **Faca:** a baioneta M9 (EUA, 1986) realista, de lâmina fixa (decisão do usuário de 2026-09-26). Herda da katana da referência: segurar o botão direito **bloqueia** projéteis de frente (com durabilidade) e um bloqueio no tempo certo faz **parry** (devolve o tiro e atordoa). Barra de carga que libera um **dash de execução**.
- **Granadas:** reais (fragmentação, atordoante, fumaça, molotov de garrafa com pano, incendiária e decoy), com os efeitos de estúdio: a explosão em respingos de massa, a flash que "estoura" a tela em branco-massinha, a nuvem de algodão de set (fumaça volumétrica fake com sprites em camadas), o fogo de papel celofane laranja animado em stop-motion. Quicam com física e têm arremesso com carga (curto/médio/longo), como na referência.
- **Mãos:** luva tática realista de 5 dedos (Blender) no braço de massinha do próprio boneco — **sem manga e sem roupa por enquanto** (decisão do usuário de 2026-09-26, seção 0.12): do punho para trás, o antebraço é de massa, na cor da massa do boneco, sem boil no viewmodel —, com os nós cobertos por um protetor de borracha moldada, a cor por facção (Massa Crua coiote, Tropa do Estúdio preta) e a braçadeira do time como faixa de massa no antebraço, só em modo de time; a empunhadura é resolvida por arma: nenhum dedo atravessando a arma nem flutuando. **Mão da frente (regra do usuário de 2026-09-27):** em toda arma que tem mão da frente (guarda-mão, cano, telha), só o polegar fica de um lado da arma e os outros quatro dedos do outro, como a pega da AK no CS:GO — o polegar **reto e deitado** no lado esquerdo, encostado na arma e apontando para a frente, sem curva (a pega "thumb break"), e o indicador, o médio, o anelar e o mínimo abraçando por baixo até o lado direito, lado a lado (sem leque); o `construir` reprova a arma que sair diferente. **Pistola (4.1c, decisões do usuário de 2026-10-02):** as duas mãos com os polegares para a frente — a mão do gatilho alta no punho e a de apoio com o calcanhar no lado esquerdo dele e os quatro dedos por cima dos da mão do gatilho; o polegar de apoio reto ao longo da armação, abaixo do ferrolho, e o do gatilho reto por cima dele, os dois a até 20° do eixo do cano e longe do ferrolho que recua; luva encostando em luva sem atravessar; o indicador **indexado** reto na lateral da armação, acima do guarda-mato e fora do gatilho (o dedo no gatilho fica para a animação de tiro); e a **palma que cede** — o tecido mole da palma afunda no punho e na outra luva até o que a ficha mede em cada ponto (só as duas mãos da pistola chegam apertando). **Faca (4.1c):** uma mão só, a direita, na empunhadura de martelo — os quatro dedos fechados em volta do cabo, lado a lado, o indicador na guarda e o polegar dobrado por cima do indicador; o braço esquerdo não aparece. Os cotovelos das luvas saem por categoria (e por arma, quando a pega pede) de uma varredura que deixa cada ângulo do pulso a no máximo 93 % do limite anatômico (`tools/cotovelos.mjs`).
- **Skins temáticas (futuro):** caneta, lápis, skate, arma de água e o que vier trocam o modelo inteiro no mesmo pipeline, com os mesmos soquetes, zonas e peças móveis da arma base (a espátula, a bola de massa, o pote de tinta, o pão de massa, as bolinhas amarelas e o anel de massinha da versão anterior ficam como ideias delas).

**Economia (modo Competitivo):** dinheiro inicial $800, máximo $16000. Vitória por eliminação $3250, por bomba/desarme $3500. Bônus de derrota crescente: $1400 → $1900 → $2400 → $2900 → $3400. Plantar a bomba dá $300 ao plantador e $800 ao time mesmo se perder a rodada. Tempo de compra de 20 s dentro da zona de compra.

### 0.8 Modos de jogo

1. **Mata-mata (FFA) com bots:** modo principal. Até 10 participantes (humanos + bots completam as vagas). Primeiro a 30 kills ou 10 min. Respawn em 2 s com proteção de 1,5 s. Por padrão usa a mesma loja do CS com compra livre a cada respawn; o host pode ligar "Economia" (dinheiro por kill com os valores da tabela). Nível de IA configurável por bot ou global.
2. **Mata-mata em Times:** Massa Crua (TR) vs Tropa do Estúdio (CT), 5v5 com bots completando. Primeiro time a 75 kills. Loja igual ao FFA (compra livre ou economia ligada).
3. **Competitivo (bomba):** 5v5, MR12 (vence quem fizer 13 rodadas), troca de lado na rodada 13, prorrogação MR3. Rodada de 1:55, bomba de 40 s, desarme 10 s (5 s com kit). Economia completa da seção 0.7. Bomba = "bolota de massa com relógio de cozinha".
4. **Gun Game / Arms Race:** cada kill troca sua arma para a próxima da lista (pistolas → SMGs → shotguns → rifles → snipers → faca de ouro). Kill com faca rebaixa a vítima uma arma. Vence quem matar com a faca de ouro.
5. **Ondas (solo ou co-op até 4):** igual à referência. Ondas crescentes, chefe a cada 5 ondas, checkpoint a cada chefe derrotado. Inimigos de massinha:
   - **Bolotas** (grunts), **Minhocas** (rushers rápidos que rastejam), **Bolhas-bomba** (bombers que incham e explodem), **Olhudos** (snipers com olho de massinha gigante e laser de linha), **Morcegos de Massa** (flyers), **Tijolões** (heavies lentos que absorvem dano), **Escudeiros** (shield bearers com escudo de tampa de pote).
   - **Chefes:** **O Escultor** (onda 5, gigante que remodela o terreno e cria paredes de massa), **A Espátula** (onda 10, ferramenta viva que corta o mapa em fatias), **O Bolo Misturado** (onda 15, massa de todas as cores que se divide em cópias ao tomar dano).
   - Itens de vida temáticos: **pote de massinha fresca** (cura) e **rolinho de massa** (colete).

### 0.9 Mapas: sets de estúdio de stop-motion

**Conceito:** o boneco tem ~7 cm. O mundo é um **estúdio de animação real** visto na escala dele. Objetos do dia a dia viram arquitetura: um pote de tinta é uma torre, um estilete é uma ponte, um tapete de corte verde com grade é o chão. Nas bordas dos mapas aparecem **equipamentos de estúdio**: tripés de câmera, C-stands, softboxes, rebatedores, fios, a lente gigante da câmera de stop-motion observando a cena. Entre rodadas, uma **mão gigante do animador** entra em cena e reposiciona props (cinemática curta, nunca durante o combate).

Três mapas, cada um com layout competitivo (2 bomb sites A/B, mid, conectores, zonas de compra), rotas para FFA e spawns de Ondas:

1. **Bancada do Animador:** tapete de corte com grade como chão; potes de massinha como prédios; ferramentas de modelar como pontes e cobertura; um estojo de armaduras de arame aberto (site A); a base de uma luminária articulada (site B); rolos de fita crepe como túneis. Luz quente de luminária.
2. **Set da Cidade de Papelão:** um set de cidade em miniatura **pela metade**: fachadas de papelão com a parte de trás exposta (sustentadas por palitos e fita), ruas pintadas, um carrinho de massinha, uma área de chroma key verde, trilhos de travelling da câmera cortando o mapa. Luz azulada de "noite de cinema" com recortes de luz quente.
3. **Prateleira de Adereços:** uma estante gigante com vários andares (verticalidade forte, para aproveitar wall-jump e slide): caixas de papelão abertas, bonecos reserva empilhados, frascos de glitter, carretéis de linha como plataformas, gavetas entreabertas como corredores. Luz de janela lateral com poeira no ar.

**Destrutíveis:** papelão fino rasga com tiros, bolas de massa se deformam e quebram, potes plásticos racham. Marcas de tiro são **amassados e buracos na massa** (deformação real de vértices em superfícies de massinha próximas; decals nos demais materiais).

### 0.10 Rede P2P (WebRTC/PeerJS)

- **Topologia:** host autoritativo P2P (o navegador do host roda a simulação oficial: placar, dano, economia, rodadas e **todos os bots**). Clientes enviam inputs, recebem snapshots.
- **Tick:** simulação a 64 Hz; snapshots a 30 Hz; inputs a 64 Hz, agrupados em pacotes.
- **Netcode:** predição no cliente + reconciliação para o próprio movimento; interpolação de 100 ms para os outros; **lag compensation** no host (rewind das hitboxes até 250 ms para validar tiros). Protocolo binário (`ArrayBuffer`/`DataView`) com quantização e delta compression. Canal não confiável e sem ordem para snapshots/inputs; canal confiável para chat, compras e eventos.
- **Lobby:** jogo rápido, salas públicas (lista via peer "diretório" com ID conhecido) e privadas (código de 6 letras + link de convite). Reentrar na partida após queda. **Migração de host** automática se o host sair (o próximo com menor ping assume, a partir do último snapshot completo).
- **Extras:** chat de texto, chat de voz por proximidade opcional (WebRTC áudio), indicador de ping/perda, kick/ban pelo host, anti-cheat básico no host (limite de velocidade, taxa de tiro, validação de linha de visada).
- **Servidor de sinalização:** PeerJS Cloud por padrão, configurável para um PeerServer próprio. Servidores STUN públicos + campo para TURN.

### 0.11 IA dos bots (local, sem LLM)

Arquitetura em camadas, rodando no host:

1. **Percepção:** cone de visão com oclusão (raycast BVH), audição (passos, tiros, recargas, granadas com raio por tipo), visão reduzida por smoke e flash.
2. **Memória:** última posição conhecida de cada inimigo, com decaimento; posições perigosas aprendidas na partida (onde morreu).
3. **Navegação:** navmesh gerada dos mapas + A* + suavização de caminho + steering (separação entre bots, desvio de obstáculos). Links de navmesh para pulos, wall-jump e slide.
4. **Decisão:** Behavior Tree + Utility AI para escolher objetivos (caçar, segurar ângulo, flanquear, plantar, desarmar, retake, salvar arma, buscar item em Ondas).
5. **Tática:** posições de cobertura pré-calculadas, pré-mira em ângulos comuns, troca de kill (trade), uso de granadas com lineups calculados, rotação entre sites, compra de armas com economia do time (eco, force buy, full buy).
6. **Comunicação:** callouts no chat e com "voz" sintetizada de massinha ("Inimigo no A!").
7. **Personalidade:** cada bot tem nome e perfil (agressivo, suporte, AWPer, lurker).

**Níveis de inteligência (1 a 10)**, parametrizados em `/src/data/botLevels.js`:

| Nível | Nome | Reação | Erro de mira | Controle de spray | Tática |
|---|---|---|---|---|---|
| 1 | Massinha Mole | 900 ms | muito alto | nenhum | anda em linha reta, não usa granadas |
| 3 | Aprendiz | 600 ms | alto | fraco | cobre-se às vezes |
| 5 | Modelador | 400 ms | médio | médio | flanqueia, usa HE e flash |
| 7 | Escultor | 280 ms | baixo | bom | pré-mira, trade, smokes com lineup |
| 9 | Mestre do Stop-Motion | 190 ms | muito baixo | quase perfeito | rotação, economia de time, fakes |
| 10 | Lenda da Massinha | 150 ms | mínimo | perfeito | tudo acima + lê o som, joga em equipe coordenada |

(Níveis intermediários interpolam os valores.) Parâmetros adicionais por nível: velocidade de rastreio, tendência a mirar na cabeça, posicionamento da mira, frequência de counter-strafe, uso de utilitários, agressividade e disciplina de economia. O jogo nunca dá "wallhack" ao bot: ele só sabe o que percebeu.

### 0.12 Personagens: facções + criador

- **Facções:** **Massa Crua** (TR, massas terracota, laranja e vermelho, bandanas de fita crepe) e **Tropa do Estúdio** (CT, azul, verde-água e branco, capacetes de tampinha de garrafa). Cada lado tem **5 modelos prontos** com silhuetas bem distintas (baixinho largo, alto magro, gordinho, etc.).
- **Sem roupa por enquanto** (decisão do usuário de 2026-09-26): o corpo de massinha fica à mostra — nenhuma roupa cobre o tronco, os braços ou as pernas —, porque nas próximas fases a bala fura o boneco e o tiro atravessa o corpo de massa, e o corpo não pode ficar escondido. Os acessórios de miniatura (bandana, capacete de tampinha, chapéus) continuam; em primeira pessoa, só a luva tática vai na mão (seção 0.7).
- **Criador de boneco:** proporções do corpo (sliders), cor da massa com mistura de duas cores (efeito marmorizado), olhos (botões, miçangas, olhos de massinha), boca, sobrancelhas, chapéus e acessórios de miniatura. Em partidas de time, o boneco ganha braçadeira e contorno na cor do time sem perder a personalização.
- **Animação stop-motion:** as animações dos personagens rodam "em dois" (12 poses/s) com leve variação de forma a cada pose ("boil"), enquanto a câmera e o input continuam a 60+ FPS. Squash & stretch em pulo, pouso, dano e morte. **O viewmodel (a arma, as luvas e o antebraço de massinha em primeira pessoa) anima suave, a 60+ FPS e sem boil** (decisão de 2026-09-26), com a opção "viewmodel em stop-motion" nas configurações: a mesma animação amostrada a 12 poses/s. O "em dois" continua nos bonecos em terceira pessoa, na killcam e nos menus.
- **Morte:** o boneco é atingido e **amassa** (achata como massa caindo na mesa) ou **se desfaz em pedaços de massa** com explosão; os pedaços grudam no chão por alguns segundos.

### 0.13 Direção de arte (bíblia visual)

**Moodboard obrigatório** (estude antes de codar e cite quais referências usou em cada decisão visual):
- Claymation/Aardman/Laika: Pinterest "Claymation Set Design" (https://www.pinterest.com/ideas/claymation-set-design/893621988359/), "3D Plasticine" (https://www.pinterest.com/ideas/3d-plasticine/901418997915/), "Clay Illustration" (https://www.pinterest.com/ideas/clay-illustration/925869521463/), "Plastic 3D Style" (https://www.pinterest.com/cokards/plastic-3d-style/)
- Sets de estúdio: Pinterest "Stop Motion Set Design" (https://www.pinterest.com/ideas/stop-motion-set-design/939142592219/), "Stop Motion Set Building" (https://www.pinterest.com/ideas/stop-motion-set-building/913501904960/), "Stop Motion Desk" (https://www.pinterest.com/ideas/stop-motion-desk/951357298077/), guia de estúdio caseiro de Terry Ibele (https://terryibele.com/build-stop-motion-studio-at-home/)
- Jogos: The Neverhood, ClayFighter, Harold Halibut (https://en.wikipedia.org/wiki/Harold_Halibut), lista de jogos em stop-motion (https://www.thegamer.com/games-made-with-claymation/); escala miniatura: Toy Soldiers, Army Men, Small Soldiers
- Técnica de shader de massinha: https://zar67.github.io/Portfolio/assets/ClayRendering/ClayRendering-Report.pdf e http://slamatron.com/blog/2020/04/16/Claymation-Style-in-3D/

**ClayMaterial (shader próprio, `onBeforeCompile` sobre MeshStandard/MeshPhysical ou ShaderMaterial completo):**
- **Impressões digitais:** normal map procedural (espirais/arcos gerados por ruído com distorção de domínio) aplicado em triplanar, escala por objeto, intensidade que aumenta em superfícies "tocadas" (bordas e pontos de pega).
- **Marcas de ferramenta:** riscos finos e amassados de espátula via ruído direcional.
- **Especular em duas camadas:** base fosca (roughness ~0,65–0,8) + camada fina "úmida" com roughness menor, controlável entre massa seca e massa fresca.
- **Subsurface fake:** wrap lighting + leve translucidez de borda com cor saturada da própria massa (massinha nunca fica preta na sombra, a sombra puxa para um tom mais saturado e escuro da mesma cor).
- **Boil de stop-motion:** deslocamento de vértice por ruído 3D cuja seed muda **a cada 1/12 s**, com amplitude pequena (~0,3–0,6% do tamanho do objeto). A seed fica congelada entre as poses, como massa que o animador tocou. Nunca nas armas, nas mãos, nos carregadores, nas cápsulas, nas granadas e nas lunetas (seção 0.7), que ficam paradas.
- **Poeira e fiapos:** partículas de poeira nos feixes de luz e fiapos de tecido presos em algumas superfícies.

**Geometria de massinha (`/src/clay/`):** kit de primitivas "moldadas à mão": cilindros, esferas, cápsulas, "cobrinhas" (tubos ao longo de curvas), placas achatadas, tudo com irregularidade de silhueta, bordas arredondadas por subdivisão e ruído, e **costuras** onde duas massas se juntam (leve saliência e mudança de cor). Os personagens são montados com esse kit (as armas e as mãos são realistas, feitas no Blender — seção 0.7). Considere SDF + marching cubes para peças orgânicas geradas no load, com cache.

**Materiais do set (não-massa):** papelão (ondulado nas bordas cortadas), fita crepe, arame, madeira balsa, metal de ferramenta, plástico de pote, tapete de corte com grade impressa. Cada um com shader próprio, todos com a mesma iluminação suave.

**Iluminação de estúdio:** key light forte e quente com sombra suave (PCF soft / VSM), fill frio de baixa intensidade, rim light de recorte em personagens, luzes de softbox visíveis como formas. Ambient occlusion (SAO/GTAO) para "assentar" a massa. Leve **flicker de exposição** entre poses, como nas animações stop-motion reais (sutil, desligável).

**Pós-processamento:** tone mapping ACES/AgX, SMAA, bloom leve só nas luzes, **tilt-shift/profundidade de campo sutil** para vender a escala de miniatura (mais forte nos menus e killcam, mínimo durante o jogo), grão de filme fino, vinheta suave, leve aberração cromática de lente de câmera de stop-motion na killcam.

**Paleta base (tokens):**
- Massa Crua (TR): terracota `#C8553D`, laranja `#F28F3B`, vermelho `#D1362F`
- Tropa do Estúdio (CT): azul `#2F6DB5`, verde-água `#3FB8AF`, branco-massa `#F4EDE1`
- Set: papelão `#B98B5E`, tapete de corte `#2E6E4E`, madeira `#8C5A3C`, fita crepe `#E8D9A8`, metal `#8F959C`
- UI: papel creme `#F6F0E4`, tinta escura `#2A2320`, destaque amarelo-massinha `#FFD23F`, alerta `#E4572E`

**UI e HUD (tudo com cara de estúdio):**
- Menus como **mesa do animador**: a câmera 3D real passeia sobre a bancada; botões são **letras de massinha** que se deformam no hover (squash), etiquetas de fita crepe, cartões de papelão, a folha de exposição (X-sheet) de animação como tela de configurações.
- **HUD:** vida e colete em bolinhas de massa que se amassam ao levar dano; munição como pequenas bolinhas empilhadas; dinheiro num pedaço de fita crepe escrito à mão; relógio da rodada no **relógio de cozinha** da bomba.
- **Loja (B):** roda radial estilo CS, com cada arma realista girando em 3D numa mini-bancada de armeiro; categorias, preços, atalhos numéricos, compra rápida e loadouts salvos.
- **Killfeed:** ícones de arma gerados da silhueta de lado do `.glb` de cada arma, achatados como um recorte de massinha; headshot = marca de digital vermelha.
- **Radar/minimapa:** desenhado como storyboard a lápis, com setas de massinha.
- **Placar (TAB):** quadro de cortiça com fotos polaroid dos bonecos presas por alfinetes.
- **Mira:** editor completo (estilo, cor, espessura, gap, ponto, dinâmica), com códigos de compartilhamento.
- **Tipografia:** uma fonte arredondada e pesada para títulos (ex.: Google Fonts "Baloo 2" ou "Fredoka") + fonte limpa para números do HUD; títulos principais são geometria 3D de massinha.

**Áudio procedural (WebAudio):** tiros sintetizados por arma (transiente + corpo + cauda, com variação por disparo e distância/oclusão), sons de massinha (squish, plop, estalos de amassar), passos por material, recarga (massa sendo arrancada e apertada), UI com "poc" de massa, **música generativa** com instrumentos de brinquedo (xilofone, kazoo, piano de brinquedo, contrabaixo pizzicato) que muda de intensidade com o combate. Áudio espacial com HRTF opcional.

### 0.14 Controles e plataformas

- **PC:** pointer lock, sensibilidade com zoom separada, FOV, teclas totalmente remapeáveis, binds estilo CS (B loja, G largar arma, F inspecionar, E usar/desarmar, Q última arma, 1–5 slots, TAB placar, Y/U chat).
- **Controle (Gamepad API):** layouts PS5/Xbox com ícones corretos, curvas de resposta, deadzone, aim assist leve (slowdown perto do alvo, desligado em salas "somente PC" se o host quiser), vibração.
- **Celular:** joystick virtual esquerdo, área de olhar à direita, botões reposicionáveis e redimensionáveis (editor de layout), tiro automático opcional, giroscópio opcional, preset gráfico "Leve" automático, UI adaptada a telas pequenas e ao entalhe.

### 0.15 Progressão e persistência (IndexedDB, sem conta)

- **XP e níveis:** XP por kill, assistência, vitória, objetivo e desafios diários.
- **Patentes:** 18 patentes com ícones de massinha (de "Massinha Crua I" até "Mestre Animador Supremo"), com rating que sobe/desce em partidas Competitivas (inclusive contra bots, com peso menor).
- **Skins de arma:** de cor e acabamento, como as pinturas dos carros do Rocket League: por zona da arma (corpo, guarnição, carregador, detalhes, interno), um acabamento (oxidado de fábrica, fosfatizado, fosco, acetinado, brilhante, metálico, perolado, anodizado, aço escovado, cromado, cerakote, fibra de carbono, madeira, polímero texturizado, borracha), uma cor da paleta nomeada (duas na madeira e no carbono) e o desgaste. "De fábrica" é a skin padrão, com os acabamentos e as cores reais; as skins nomeadas e as combinações desbloqueiam por nível e conquista (ouro no Gun Game). As skins temáticas (seção 0.7) trocam o modelo inteiro.
- **Estatísticas:** K/D, HS%, precisão por arma, dano médio por rodada (ADR), vitórias por modo, mapa de calor de mortes por mapa.
- **Conquistas:** ao menos 40, com ícones de massinha (ex.: "Wallbang no papelão", "Parry num tiro de AWP", "Ace com pistola").
- **Replay e killcam:** o host grava snapshots; ao morrer, a **killcam em stop-motion** mostra os últimos 5 s do ponto de vista do matador a 12 fps com grão e tilt-shift. **Melhores momentos** gravados automaticamente (multi-kills, clutches) e um visualizador de replay com câmera livre, pausa, velocidade e linha do tempo.

### 0.16 Configurações gráficas

Presets Leve / Médio / Alto / Ultra + ajustes individuais: escala de resolução, sombras, AO, qualidade do shader de massa (digitais on/off, boil on/off), DOF, bloom, grão, flicker de stop-motion, densidade de partículas, distância de detalhe. Detecção automática de hardware no primeiro acesso. Modos para daltonismo nas cores de time e da mira.

### 0.17 Definição de pronto (vale para todas as fases)

- Sem erros no console. Sem vazamento de memória ao trocar de mapa/partida (verifique `renderer.info`).
- Meta de FPS da seção 0.4 atingida, medida no overlay de debug.
- Visual revisado contra o moodboard: a cena parece stop-motion de massinha, não um protótipo.
- Funciona em Chrome, Edge, Firefox e Safari (desktop e mobile).

