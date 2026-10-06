- **Correção C2 (2026-10-05):** o carregador curto da AWP em fileira dupla, medido em duas fontes do jogo só lidas no
  navegador (nada do jogo gravado; só os números na ficha, as duas com a licença e o autor do jogo nas `fotos`): o modelo
  do CS2 no visualizador 3D do VSkin (a pele Asiimov pinta o carregador de branco e a placa de fundo de laranja: as
  partes aparecem) e o ícone do inventário.
  - **as fontes:** no VSkin, o iframe do visualizador aumentado para 2400 e 4800 px CSS (o WebGL refaz o render na
    resolução maior), a câmera de lado padrão, a escala pelo comprimento total (1230 mm): o carregador de −760,5 a −834,9
    (74,4 mm) e de −760,1 a −836,2 (76,1) em duas posições, as fendas em −782,6 e −815,0 (5,8 de largura: 30 % e 73 % do
    comprimento), o fundo de −92,5 na frente a −98,3 atrás, a placa de fundo à parte (~6,5 mm); de frente e de baixo, a
    largura entre 25 e 30 mm (estimativa: sem medida conhecida no mesmo plano). A vista do CS:GO (a peça `carregador` da
    ficha) dá o mesmo: 75,3 mm, o fundo de −91,3 a −97,2, as fendas a 29 % e 71 %. O ícone mostra a frente (a face
    clara do aço), o fundo descendo para trás e o carregador logo à frente do guarda-mato; a posição, pela câmera de 7
    pontos, não se confirma nessa parte da arma (abaixo, na pose do ícone) — o modelo 3D manda. No vídeo do Tigerfield
    (514,27 s), o carregador entra logo à frente do guarda-mato;
  - **o que difere do CS:GO:** no CS2 o carregador sai ~6 mm mais para trás e o aro do guarda-mato avança em cima até ele
    (na vista há 14 mm de coronha entre os dois). O carregador segue a peça da vista (o mesmo comprimento, o mesmo fundo,
    as mesmas fendas) e a coronha fica a da vista (fora da C2), com a nota na ficha;
  - **a conta:** o .338LM militar tem 91,44 mm e a parte à vista do jogo, 75 — em qualquer fileira o carregador precisa
    de 91,7 mm por dentro. A fileira dupla é o que deixa os 18 mm a mais escondidos na coronha: os estojos (69,2) cabem
    na parte à vista, só os projéteis passam da frente dela, e a pilha fica acima do fundo da coronha (em fileira única o
    de baixo desceria a −84,7 e a frente sairia à vista). Os cinco desencontrados (3 + 2), 28 mm de largura (a C2: ~28):
    os centros a ±5,735 do meio, 9,557 mm entre um e o próximo (0,77 diâmetro entre as filas, perto do desencontro dos
    carregadores de fuzil);
  - **achado 1 (a frente presa):** no primeiro desenho (29 mm, a frente escondida com o fundo em −59,3, acima do fundo
    da coronha), a coronha embaixo da frente prendia o carregador: para sair reto para baixo ele atravessaria 6 a 9 mm
    de plástico (na recarga do jogo, a frente apareceria saindo de dentro da coronha). Correção: o fundo da frente
    escondida rente ao fundo da coronha, 0,3 mm para dentro (`recuoDaFrente`), pelo perfil suave da coronha
    (`awp.perfil_suave` e `fio_de_baixo`, o mesmo do prisma dela); o poço da coronha reto, com a boca viva (cortado
    depois do chanfro: o de 3,5 mm abriria um sulco redondo de 4 mm em volta da frente rente). Visto de baixo, a frente
    é uma chapa de aço na boca do poço; de lado nada muda. Com a frente rente, a largura de 28 da C2 volta a caber (o de
    baixo em −54,8, o projétil dele 6 mm acima do fundo da frente);
  - **achado 2 (o ferrolho não chegava ao de cima):** os lábios de antes (o de baixo deles em −13,15) seguravam o aro do
    de cima a −20,7, 4,3 mm abaixo do ferrolho de Ø 20, que passava por cima sem tocar o culote. Correção: a pilha sobe
    até o de cima encostar no ferrolho fechado (0,05 mm: o ferrolho fechado aperta a pilha, como na arma), e os lábios
    novos dobram da parede por cima do ombro dele, concêntricos com o aro (0,05 mm), dos 52° aos 14° do alto do aro — a
    borda a ~7,6 mm do meio: o de cima aparece entre os lábios, que cobrem 38 % da largura dele, como num carregador de
    fileira dupla de fuzil, e o alto da borda passa 1,5 mm abaixo do ferrolho e do poço da ação. A peça rígida não mostra
    o de cima subindo ~2 mm aos lábios quando o ferrolho recua (na arma real é essa sobreposição que o ferrolho empurra):
    registrado na ficha;
  - **o retém:** no lugar do manual da AW (A4: na frente do guarda-mato, com o polegar direito), na faixa de coronha da
    vista entre o carregador e o aro: a alavanca no vão da coronha (cortado depois do chanfro), o pino de aço
    (`pontos.travaCarregador`, −833; −62), o dente no entalhe da traseira do carregador (0,25 mm atrás do culote do de
    baixo) e a pá com o fundo rente ao fundo da coronha e as estrias de lado a lado (a primeira versão saía 2 mm abaixo
    do fundo: na vista do jogo não há nada abaixo da faixa, e daria magenta);
  - **as fendas pelo CS2:** a vista do CS:GO (0,98 mm/px) não resolve a largura (10 px com as bordas claras); no modelo
    do CS2, 5,8 mm, nas frações 29,6 % e 72,7 % do comprimento à vista — `pontos.carregador.fendas` (x = −776,2 e
    −808,6), no lugar das constantes de 7 mm em ±16 do meio que o código tinha;
  - **achado 3 (a boca do poço):** cortados depois do chanfro (a boca viva), o poço e o vão do retém faziam o booleano
    exato estragar a coronha alta longe do corte — 3 arestas abertas no guarda-mato (x = −905, à direita) e 60 colisões
    novas na soleira e no pulso (x = −1112 e −1062) —, e o conserto (o Manifold) deixava 6 colisões perto do adaptador
    do bipé; o arranjo escolhido nem cortava (o Manifold recusa a malha), e o modelo alto ficava sem o poço (o
    `construir` só confere o de jogo, onde o exato triangulado deu zero: foi a conferência do alto,
    `arma_alto_abertas.py`, que mostrou). Correção: o corte volta para antes do chanfro (o caminho robusto, como o poço
    antigo) e a biblioteca ganha o **teto do chanfro por caixa** (`pecas.limitar_chanfro`, `chanfro_local.tetos`: as
    arestas com o meio na caixa ficam com o chanfro até a largura dela): a boca do poço e a do vão com 0,6 mm, não os
    3,5 da coronha (que abririam um sulco redondo de 4 mm em volta da frente rente e arredondariam as quinas de dentro
    do poço contra o carregador). Nos dois níveis: zero arestas não manifold, zero colisões (`c2/coronha_cortes.py`);
  - **achado 4 (a mola, pela revisão dos closes):** a mola saía degenerada, um fio reto na frente (x ≈ −755,5, lado 0 a
    6,4) no lugar das 4,5 voltas — em `_no_retangulo_redondo`, o último trecho era achado pelo tipo e pelo comprimento, e
    o primeiro trecho (a outra metade da reta da frente) é igual a ele: todo ponto saía do primeiro. Pelo índice agora; o
    teste do `.glb` conferia só a altura da mola e passou — agora confere a mola de ponta a ponta e de parede a parede;
  - **achado 5 (a densidade de texel):** com a mola de verdade, a densidade da arma inteira caiu de 1,51 para 1,39
    px/mm: a projeção por ângulo (`smart_project`, 66°) partia a hélice em 484 ilhas para 872 faces (quase uma por
    face), cada uma com a margem de 8 px — o atlas do perto usava só 27 % da textura com ilhas (2.761 delas). Correção
    na biblioteca: os tubos (`pecas.varrer`: `tubo`, `mola`) nascem com a UV própria — a faixa em mm, ao longo do
    caminho (partida a cada 200 mm) e em volta do perfil, e as tampas no plano do perfil, as faces marcadas `uv_propria`
    — e o `assar.uv_automatico` as deixa fora da projeção e as põe na escala de UV por mm da arma antes do
    empacotamento. Vale para todos os tubos (a alavanca do ferrolho da AWP, as molas e os arames da AK, da M4A4, da Nova
    e da P90: as da 4.1c mudam na reconstrução da Tarefa 16);
  - **a pose do ícone, de novo** (o modelo final; em números, sem captura de tela: a máscara do nosso modelo na câmera do
    ícone, `c2/icone_mascara.py`, e as bordas dela, `c2/icone_bordas.py`, contra as do alfa e da luminância do ícone
    lidas no navegador pela `grade.html`): o carregador do ícone tem o comprimento do nosso (a face esquerda com 20,8 px,
    a nossa com 20,1) e a mesma descida do fundo ao longo dela (2,6 e 2,3 px), a frente mais estreita (11,7 px contra
    18,7: ~17,5 mm contra os 28 da fileira dupla — o desvio que a C2 pede) e fica ~10 px mais para trás (as quinas em
    u = 386,0 e 406,8; as nossas em 376,6 e 396,7). O fundo da coronha logo à frente dele, o da vista do CS:GO, sai
    deslocado o mesmo no ícone — casa com o nosso 10 a 14 px para trás (1,1 a 1,7 px de desvio; 3,6 sem o
    deslocamento) —: a câmera de 7 pontos erra nessa parte da arma, onde não tem ponto (e 3 a 6 px nos parafusos da
    coronha), e o carregador do ícone fica no lugar do nosso em relação à coronha; depois do deslocamento, ele desce uns
    2 a 5 px a mais (o VSkin: ~1,2 mm). O cano bate a ≤ 0,7 px e a traseira da soleira a 0,5–6,9 px. A leitura de
    antes, pela volta dos pixels do ícone ao plano de lado (58 a 70 mm de comprimento, ~19 de largura), não se sustenta
    na comparação direta: saiu das duas notas da ficha;
  - **a `grade.html`** (as bordas lidas no navegador) perdia a passagem do alfa que caía em cima de uma amostra: num alfa
    de borda dura, o bilinear dá 0,5 exato no meio entre dois pixels, e numa linha de coordenada inteira a amostra cai
    ali (a coluna u = 460 do ícone saía sem a soleira). Corrigida pela troca do lado, com a posição interpolada; as
    leituras de antes que acharam a borda não mudam;
  - **as fendas na arma mostram a mola:** com o de cima no ferrolho, a pilha dos cinco termina no seguidor em −62,3, e
    a coronha cobre o carregador até −68 na frente e −74 atrás — pela parte à vista das fendas aparece a mola (no close
    de lado, na arma). Os cartuchos aparecem pela parte de cima delas, com o carregador fora (na recarga). No jogo as
    fendas à vista também são escuras (o interior escuro e as bordas claras da vista do CS:GO); levar os cartuchos à
    parte à vista pediria a pilha 6 a 12 mm mais baixa, longe do ferrolho (o achado 2 de volta). Na sobreposição de lado,
    as fendas ficam verdes: a vista as traça cheias, e no nosso a luz passa de uma à outra entre as voltas da mola;
  - **fora da arma, o carregador é uma bota:** a parte à vista e, em cima dela, a frente escondida que avança 18 mm
    dentro da coronha com os projéteis — a parte à vista do jogo (75 mm) com os .338 de 91,44 mm. Na recarga, ele sai
    assim;
  - **os closes** (`c2/carregador_closes.py`, as vistas de baixo com uma luz por baixo): na arma, de lado (as fendas com
    a mola) e por baixo (a frente escondida como uma chapa de aço rente na boca do poço, a borda de 0,6 mm; o retém com a
    pá estriada no vão atrás do carregador; o guarda-mato vazado dos dois lados); só o carregador, de lado e da direita
    (os cartuchos na parte de cima das fendas, o seguidor, a mola), de cima (os lábios por cima do ombro do de cima, o
    segundo da outra fila embaixo dele, a frente aberta para os projéteis) e de três quartos por baixo (a bota, a placa
    de fundo inclinada) — nada fora do lugar;
  - **a AWP aprovada** (a quarta construção, 177 s, depois das notas do ícone na ficha: o `.glb` idêntico ao da terceira
    byte a byte; as texturas assadas diferem em alguns bytes, com o mesmo tamanho a ±2 — o assar não sai bit a bit igual
    entre duas execuções): 3,55 MB (o .glb com 547 KB, as texturas do perto com 1,84 e 0,95 MB, as do mundo com 234 e
    148 KB; eram 3,74 MB na P1), a silhueta de lado com 98,6 % (96,0 % bruta; 98,1 % na P1), perto 38.775, mundo 5.699 e
    longe 1.400 triângulos, a densidade de texel de 1,544 px/mm, as medidas exatas (o comprimento de 1229,6: −0,03 %; o
    cano de 635; o raio de mira de 308; a altura de 229,4: −0,12 %), 1.927 faces escondidas tiradas, nenhuma aresta
    aberta nos dois níveis (o alto pela `arma_alto_abertas.py`, sem aviso de corte) e os fins de curso em zero (o
    ferrolho no giro e no recuo, com a trava; a trava nas três posições; o bipé abrindo). Na sobreposição de lado, o
    magenta da frente do guarda-mato sumiu; no carregador sobram bordas de 1 a 2 px (a traseira reta contra a de 2 mm
    inclinada da vista, a aba de 0,4 da placa de fundo);
  - **os testes:** a ficha (`fichas41d.test.js`, a C2: a largura, o encosto no ferrolho, o comprimento por dentro, a
    boca, as fendas, as larguras na coronha e na ação, o retém, as duas fontes do CS2) e a AWP (`armaAwp.test.js`: o
    corpo de 28 com a placa, os 75 mm à vista, as bordas das fendas, a frente rente à boca do poço, os aros dos cinco, o
    latão por dentro das paredes, a folga do ferrolho, os lábios dos dois lados, o seguidor, a mola de ponta a ponta e
    de parede a parede, a pá do retém rente); a suíte, 596/596 (de novo depois da quarta construção); a prova das peças
    da biblioteca (mexi no `varrer`, no chanfro local e no `assar`), 21 provadas, nenhum problema;
  - a Nova e a P90 foram aprovadas antes da biblioteca nova (a UV própria dos tubos muda as molas e os arames delas; o
    teto do chanfro, só a AWP usa): pegam a UV nova na construção delas com a pega (Tarefas 14 e 15), e as da 4.1c na
    Tarefa 16.
