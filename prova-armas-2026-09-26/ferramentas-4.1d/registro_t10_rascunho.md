- **Tarefa 10 (2026-10-04):** a P90 em seis módulos — `p90.py` (as constantes, os pivôs, os soquetes, a montagem e a
  pose do ícone), `p90_quadro.py` (as duas metades de polímero pelo contorno da foto de lado da FN, com o oval de trás e
  a abertura da frente vazados — esta por trás do gatilho e, embaixo dele, a fenda do seletor —, na largura de cada
  seção; o laço do punho e a caixa da coronha como regiões do mesmo prisma, com a face do degrau; os dez parafusos
  sextavados com as porcas nos rebaixos; a fenda e a placa da coronha; os retentores do carregador), `p90_secao.py` (a
  seção arredondada do quadro moldado: o raio de cada lado do contorno e dos buracos pela distância ao segmento e a face
  de lado pela triangulação de Delaunay restrita, com os buracos nela e as fileiras nos ângulos do quarto de círculo),
  `p90_cima.py` (a ponte em partes de larguras diferentes — a torre da frente com o botão de trava e a janela, o corpo
  sob o trilho, a travessa e as pernas por fora do carregador, o pé —, o corpo do grupo do cano com o canal do ressalto
  do carregador, o trilho de cima e os laterais, o quebra-chama do jogo, o cano e a alma, e as miras de ferro do CS2 com
  as orelhas fixas e a folha que dobra), `p90_mecanica.py` (as alças com o ferrolho, o gatilho com a lâmina entrando na
  fenda do quadro, o seletor em disco, o obturador e os cortes deles no quadro) e `p90_carregador.py` (o policarbonato
  com o friso, as nervuras, o prato de trás com o disco de transferência, a tampa da frente com o ressalto, o seguidor e
  os 48 cartuchos num nó filho marcado `dentro_de_translucido`) —, a entrada `p90` no `armasReais.js`, o
  `armaP90.test.js` (5 testes) e, na bancada, as direções da "Explodir" das peças da P90 sem direção genérica (o seletor
  e o obturador para baixo, as duas miras rebatíveis para cima; `arsenal.js`), que o `bancada41c.test.js` pede de toda
  realista.

  Na biblioteca, achados da construção da P90 que valem para as três armas da 4.1d:
  - **o chanfro com o limite local (`chanfro_local.py`, opt-in pelo `pecas.chanfro_local()` nas três).** O "clamp
    overlap" do chanfro do Blender é global (`bmesh_bevel.cc`, `bevel_limit_offset`: o menor limite de todas as arestas
    multiplica todos os deslocamentos da peça): as arestas de 1 µm das portas do quebra-chama deixavam o chanfro dele com
    0,015 mm dos 0,3 pedidos, uma folga do quadro o deixava com 1 mm dos 3, as paredes do carregador com 0,7 dos 2, e a
    bomba da Nova com 0,04 do 1 mm. Cada aresta ganha um peso (o chanfro por peso) que respeita só as folgas em volta
    dela, pelas contas do próprio Blender (`geometry_collide_offset`: o encontro dos deslocamentos de três arestas
    seguidas e o deslize por uma aresta sem chanfro), muda devagar ao longo das chanfradas, fica igual nas alinhadas (a
    diferença de pesos delas é dividida pelo seno do ângulo, quase zero) e zera abaixo de 0,02 mm (a solda de 0,005 mm
    juntava os vértices dos chanfros de poucos µm e abria a malha); a pilha de antes do chanfro é aplicada na malha
    primeiro (as arestas novas dos booleanos nascem sem peso) e os vértices degenerados dissolvidos (o nó de uma mira
    deixava arestas de comprimento zero). Depois do chanfro, as dobras que ele faz onde dois deslocamentos grandes se
    cruzam (os triângulos que se atravessam, pela árvore BVH) são desfeitas reduzindo os pesos maiores em volta, e os
    cortes finais que abrem a malha ou cruzam triângulos passam ao Manifold ou à saída do chanfro triangulada. As três
    armas saem sem nenhum chanfro reduzido pelo limite global, sem triângulos que se cruzam e sem arestas abertas nos dois
    níveis — o modelo alto também, que a Tarefa 9 deixava com a Nova com 22 arestas abertas, a AWP com 343, a luneta com
    64 e a coronha com 6. As da 4.1c ficam como foram aceitas;
  - **a margem das ilhas de UV (`assar._estender`)**: a média dos vizinhos cobertos (o EXTEND do Blender) fazia um
    degradê diferente a cada anel da margem, que o WebP sem perdas guardava texel a texel — na P90, com milhares de
    ilhas pequenas, 1,48 MB dos 2,54 MB da `_n` e 1,37 MB dos 2,70 MB da `_m`, e ela passava do orçamento de 6 MB por
    13 KB. A margem agora repete o texel da borda (os quatro de lado antes das diagonais): as mesmas ilhas, o mesmo valor
    na borda para o filtro e o mipmap, e as carreiras iguais que o WebP guarda quase de graça;
  - a ordem dos lados dos cortadores redondos contra a das peças que eles cortam: o prato do carregador (os sulcos de 96
    lados com os vértices nas arestas do leque do disco: meio passo de giro), o torno do quebra-chama (meio passo) e a
    boca de 64 lados (um quarto), a boca e a lente da luneta da AWP (meio passo: o mesmo número de lados do tubo abria 64
    arestas no alto) — o booleano exato erra com os vértices de um em cima das arestas do outro;
  - a cova do pino do grupo do gatilho da Nova pelo Manifold (`cortar(..., solucionador=...)`): o exato abria a malha
    em quase toda configuração;
  - as cúpulas das lentes da luneta com 4 anéis no modelo de jogo (8 no alto): com os cartuchos no carregador a AWP
    passava do orçamento do perto (40.480).

  Achados da construção e da conferência da P90, corrigidos:
  - **o gatilho e o seletor escondidos no quadro** (na pose do ícone, contra o ícone do CS2, e na foto de lado da FN): o
    vão da ficha (`buracos.aberturaFrente`) é o fundo que aparece através da abertura — termina na frente do gatilho e em
    cima do disco do seletor, que tapam o resto, e é o que a silhueta de lado confere —, e o quadro fechava em volta dos
    dois: de lado, a abertura saía vazia. Na foto e no ícone, o gatilho largo enche o fundo da abertura até a borda de
    trás dela, e o disco serrilhado do seletor aparece embaixo dele, de lado. A abertura do quadro agora passa por trás
    dos dois (`p90_quadro.abertura_da_frente`: o vão da ficha à frente de x = −149 e na borda de cima; atrás, o fundo
    0,5 mm abaixo do disco e a borda de trás 0,5 mm atrás das costas do gatilho, a quina de baixo com 1,2 mm de raio; as
    folgas conferidas nos dois níveis depois da média e do `simplificar`: 0,5 mm do gatilho, 0,385 do chanfro do disco,
    2,0 da lingueta), a lâmina do gatilho sobe até y = −18 dentro da fenda do quadro (`p90_mecanica.contorno_do_gatilho`;
    a ficha a cortava na borda de cima da abertura, 0,2 mm abaixo dela) e a borda da abertura arredonda com 5 mm e com
    2 mm na fenda do seletor — o raio de um buraco pode ser uma função do ponto (`p90_secao`): entre o fundo da fenda e o
    entalhe de baixo do quadro ficam 8,3 mm, e com os dois arredondados (5 e 6) passando um do outro o maior recuo trocava
    de lado no meio da ponte e deixava um vinco. A silhueta de lado não muda (o gatilho e o disco enchem a abertura nova);
    o degrau de 3 mm da foto na frente da lingueta (x = −152 a −156) fica de fora: no ícone do CS2 o seletor sai do fundo
    da abertura sem ele, e com a borda arredondada dos dois lados ele virava uma aleta fina;
  - **as faixas claras abaixo dos buracos do quadro** (o buraco do polegar e a abertura da frente): cortados por um
    cortador com a borda arredondada, a face plana ficava com os triângulos longos do Delaunay presos à borda do corte, e
    as normais puxadas por ela davam faixas no modelo alto (e, pelo assar, no de jogo). Os dois buracos entraram na
    própria malha da face de lado (`p90_secao.lateral` com a forma de buracos: as fileiras do arredondado em volta deles
    e a parede no prisma do quadro), e o cortador saiu;
  - o quebra-chama: o serrilhado com a ponta no plano do degrau do colar (estendido 0,5 mm), as portas em estádio de
    verdade (as pontas de 1 µm deixavam o chanfro global em 0,015 mm), as portas e o serrilhado cortados depois do
    chanfro num cortador só, o torno meio passo girado e a boca de 64 lados um quarto (a de 60, a 0,19° dos lados do
    torno girado, virava faces);
  - os furos do quadro com o contorno de 0,02 mm no alto e 0,12 no de jogo (com 0,1 e 0,35, as facetas da borda
    arredondada apareciam).

  A pose do ícone do CS2 da P90 (`p90.ICONE`): a câmera de furo ajustada a nove pontos do ícone — o centro da boca, a
  face do botão da alavanca e os sete parafusos da face esquerda, com o lado de cada um no modelo —, 1,5 px de erro médio
  (3,0 no pior), a lente de 72,8 mm, a câmera 8,1° abaixo, olhando para cima. Na pose, a P90 bate com o ícone no quadro,
  nos dois buracos, no carregador, no botão da alavanca e no quebra-chama; acima do quadro, a ponte (abaixo). A P90
  aprovada: 3,77 MB (o .glb com 525 KB, as texturas do perto com 2,00 e 1,04 MB, as do mundo com 239 e 152 KB), a silhueta de lado com 99,6 % (98,7 % bruta), a de três quartos contra a foto da FN com 96,3 % (95,8 %), perto 38.572, mundo 5.700 e longe 1.414 triângulos, a densidade de texel de 1,59 px/mm, as medidas exatas (505 mm, o cano de 264, o raio de mira de 131,8; a altura de 231,7: −0,12 %), 429 faces escondidas tiradas e os sete fins de curso em zero. As três construídas de novo para a P1 com o chanfro local e a margem nova: a AWP com 3,74 MB (eram
  4,90), silhueta 98,1 %, perto 36.363 triângulos; a Nova com 3,39 MB (eram 4,90), silhueta 99,7 %, perto 25.736; as
  medidas e os fins de curso como na Tarefa 8 e na 9. Suíte 593/593.

  **Para a P1:**
  - **a ponte da P90 do CS2 é mais baixa que a da TR real.** Pela câmera do ícone (ajustada só nos pontos do quadro),
    a volta dos pixels do ícone ao plano de lado põe o topo do trilho a 75,7 mm do eixo (a TR real da foto da FN: 93,8;
    os dentes do trilho do ícone voltam numa reta horizontal, a 75,5–75,9, o que confere a câmera), as orelhas das miras
    a 113–118 mm (a ficha: 130 e 129,3), a da frente uns 25 mm mais para trás (x ≈ −74 a −83, a ficha −46 a −61), a
    ponta do trilho em x ≈ −52 (a ficha −34,7) e a janela da torre maior (≈ 23 × 42 mm). Seguir o CS2 (a regra do
    usuário: na dúvida do desenho, o CS2) baixa a ponte, o trilho, os trilhos laterais e as miras e muda a linha de
    mira, o raio de mira (≈ 95 a 100 mm) e as alturas; a conferência de três quartos contra a foto da FN deixa de valer
    na parte de cima (a foto é a TR real) e fica no quadro;
  - **o chanfro das armas da 4.1c**: pelo mesmo limite global, a M4A4 tem 34 peças com o chanfro reduzido (o receptor
    de baixo com 0,002 mm do 1 mm pedido, a coronha com 0,1 dos 2, o guarda-mão com 0,023, o quebra-chamas sem chanfro);
    a correção (o chanfro local nela) muda a geometria aceita e refaz as pegas;
  - as texturas das armas da 4.1c e das luvas, construídas de novo na Tarefa 16, encolhem com a margem nova (só a
    margem muda; o miolo das ilhas fica igual);
  - da Tarefa 8, o carregador da AWP (a fileira única dos cinco .338, mais comprido que o do jogo, ou a fileira dupla
    curta do jogo) e a cor das lentes; da Tarefa 9, o bloco da Nova que lê cinza nas renders do Cycles.
