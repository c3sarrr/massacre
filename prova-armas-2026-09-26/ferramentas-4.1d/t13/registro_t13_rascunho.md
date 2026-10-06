- **Tarefa 13 (2026-10-05):** a regra `sniper` — `SNIPER` em `empunhadura_regras.py` (a mão direita da `rifle` com o
  polegar pelo buraco do polegar e a esquerda pela `LATERAL`, com os números da AWP; o formato no cabeçalho), as
  aberturas como a arma as corta na pega (`awp.lacos_dos_furos`; `empunhadura_pega.furos_da_regra` e `resolver` com os
  `lacos`; `principal._lacos` no `construir` e no `validar`), a pseudonormal por planos na distância à arma
  (`empunhadura_arma.Arma.pseudonormal`), `CATEGORIAS_COM_PEGA` com a `sniper` (`src/data/luvas.js`), os testes
  (`pegaFuro.test.js`: a `sniper` na lista e a `escopeta` e a `smgBullpup` fora; `armaAwp.test.js`: a pega sniper no
  relatório) e a AWP construída com a pega.
  - **o banco de prova** (`ferramentas-4.1d/t13`: `servidor.py`, `awp_pega.py`, `varreduras.py`): a .blend da
    conferência da AWP com as luvas montadas uma vez, numa sessão do Blender que fica aberta e executa os trabalhos de
    uma fila; cada mão pelo `_uma_mao`, o afundamento da palma e a `conferir_mao`, como no `construir` — 5 s por pega
    com os dedos (o polegar parado no afastado da chegada), 15 s a 3 min com o polegar pelo furo, três sessões em
    paralelo; no fim, a pega inteira pelo `resolver`, com o EMPUNHADURA e os laços da arma (o trabalho de sair escrevia
    `G['_sair']`, que o espaço de nomes não tinha: as três sessões ficaram abertas até um `_sair = True`, e o
    `servidor.py` agora se enxerga como G);
  - **os achados, na ordem:**
    1. **a mão de apoio pela regra do bloco:** na AWP de verdade o anelar deita por cima da peça (a falange média a
       66,9° da face): a face do guarda-mão tem 46 mm (a do bloco, 56), e os dedos passam da borda. A varredura da
       altura da palma, da inclinação, da girada no plano da face (positiva leva as pontas para a frente), da guinada e
       do lado do polegar (24 + 81 + 27 + 18 pegas, `varreduras.py`) dá a palma 10 mm mais baixa (−72,5 mm do meio da
       face), a inclinação de −8,75°, a girada de 7,5° e a guinada de 20° da regra;
    2. **o polegar 'baixo' tem duas saídas** no guarda-mão de verdade: dando a volta até a quina de baixo do lado
       direito (encostado, a ponta 13 a 15 mm além da face direita, a distal a ~90° da frente) ou para a frente por
       baixo da peça, no ar — a IK deixa a polpa longe do alvo, e o `_assentar_na_arma` fecha a MCP e a IP até encostar:
       sem nada embaixo, a IP vai ao limite (80°) e a validação reprova. Nas 81 + 27 + 18 pegas das três últimas
       varreduras, 48 + 13 + 9 caíram na segunda (a polpa a 1,9 a 10,6 mm da arma, a IP a 80° em todas). A pega da regra
       fica na primeira com o lado do polegar de 20° a 50°, a inclinação a ±1,25°, a guinada a ±5° e a palma 2,5 mm mais
       baixa; 2,5 mm mais alta, ela cai na segunda; girada a 10° (2,5° a mais), na segunda e com o médio por cima da
       peça. A melhoria do solver (a IP que não fecha no ar; outro alvo quando a polpa não encosta) fica no RETOMAR para
       a P90 (Tarefa 15), que usa o mesmo polegar;
    3. **a mão do gatilho com a âncora do fuzil:** "o indicador cruza a arma mesmo com a polpa 20 mm acima do alvo" —
       com a MCP 27,6 mm atrás do gatilho (a do fuzil), ele cruzava a coronha na barra entre o buraco do polegar e o
       guarda-mato. A varredura dos dedos sem o polegar (a âncora, a diagonal, a altura do ponto no gatilho e a folga;
       24 + 36 + 27 pegas): com a MCP 27,6 a 36 mm atrás, 15 das 24 cruzavam assim; nas outras e com a MCP até 48 mm
       atrás, o médio ia esticado ao lado do guarda-mato (a barra de baixo dele no caminho), em leque com o anelar (19 a
       33 mm; com 25° de diagonal, o anelar com o mínimo, 22 a 32); com o ponto a 60 % da altura do gatilho e a folga de
       1 mm, a polpa parava a 2,3 a 9 mm dele (com a folga de −0,25 mm da M4A4, ela só encostava com a MCP 48 mm atrás);
       com 74 % (o da M4A4), ela encosta em todas até 55 mm atrás. Com a MCP 50 a 55 mm atrás, o leque só fecha com 5°
       de diagonal e a MCP 14 mm abaixo do ponto (2,8 a 3,0 mm; 4 a 9 mm abaixo, 12 a 14 mm; com os 15° do fuzil, 16 a
       25 mm; com 25°, 25 a 27 mm, ou o anelar do mínimo 17 a 19 mm); 60 mm atrás, com 5°, a polpa não chega (3,1 a 3,7
       mm do gatilho). A regra fica com a MCP 50 mm atrás e 13 mm abaixo do ponto, com 4° de diagonal (o punho da AWP é
       quase vertical, 3,8°); as seis vizinhas (2,5 mm para trás e para a frente, 2 mm para cima e para baixo, a
       diagonal a ±2°) passam;
    4. **o furo do polegar é o oval:** a coronha corta o oval equivalente do traçado (`P.oval_equivalente`, 48 lados), e
       a pega usava o traçado da ficha, que passa até 2,35 mm por dentro do oval e 0,46 mm por fora (o oval vai até 1,14
       mm por dentro do traçado e 1,16 por fora): o prisma e a borda do furo da pega saíam do traçado, não da malha. →
       `awp.lacos_dos_furos(ficha)` (o oval; a coronha corta o mesmo) e `furos_da_regra(..., lacos)` pelo
       `principal._lacos`;
    5. **o polegar pelo buraco** entra e passa — dentro, a 0,45 mm da borda, nada do lado errado —, com a polpa
       encostada (0,41 mm) na borda da frente do buraco, do lado esquerdo, e a distal a 53,6° da frente, para a frente,
       para fora e para baixo (0,594; 0,708; −0,381): a falange proximal (~31,5 mm) atravessa quase toda a largura da
       coronha no buraco (a MCP 14 mm à direita do meio, a IP 11 mm à esquerda), e a distal sai pela borda da frente sem
       espaço para deitar na face. O eixo 31° para baixo leva a distal 13° para baixo, e 31° para cima, 4° (ela fica a
       53° a 58° do eixo pedido); girar a mão em volta do punho cruza a arma já na chegada (−15°) ou deixa o indicador
       sem chegar ao gatilho sem cruzar a arma (+15°);
    6. **a falsa penetração de 15,7 mm:** três vizinhas da mão do gatilho reprovavam com "a luva entra 13,7 a 15,7 mm na
       arma" — um vértice da palma 15,7 mm FORA da coronha, perto da borda viva do buraco do polegar (a parede do oval
       contra a face inclinada da passagem do pulso para o punho). Longe da arma (mais de 6 mm), o sinal sai de três
       votos: a face mais perto (a parede: dentro), a pseudonormal (a soma das normais das faces a até 0,05 mm do ponto
       mais perto: três lascas finas da parede contra uma face do lado — dentro) e a paridade dos raios (fora); os dois
       primeiros erravam. → `Arma.pseudonormal`: as faces agrupadas pelo plano, cada plano pesado pelo ângulo dele no
       ponto (a pseudonormal com o peso do ângulo de Bærentzen e Aanæs, 2005, com as lascas de um plano juntas). Os três
       pontos saem fora (15,7, 14,1 e 13,7 mm), as três vizinhas passam, e as pegas que já passavam saem com os mesmos
       graus (o solver não mudou nelas); as quatro da 4.1c são resolvidas de novo na Tarefa 16, com a comparação dos
       ângulos;
    7. **o indicador quase reto:** a polpa no gatilho fica a ~73 mm da MCP do indicador (o alcance do punho de buraco do
       polegar: com a MCP mais perto, o dedo cruza a coronha, o achado 3), e o dedo chega quase esticado — a MCP a
       30,9°, a PIP a 6,1° e a DIP a 6,7°, com a PIP 13,9° mais aberta que na pose de pegar (20°) —, com a polpa
       encostada no gatilho (−0,05 mm) a 3,3 mm do ponto a 74 %; nas vizinhas da regra a PIP fica de 0,2° a 8,9° (11° a
       20° mais aberta). Na inspeção do CS2 é a mão do gatilho que aparece: fica para a P2;
    8. **a câmera do quadro pronto** (`t13/camera_cs2.py`, só números): a câmera ajustada à boca, à objetiva e à bola do
       ferrolho do quadro de 8:32,0, com a arma de pé, erra 3,4 % da tela (a média quadrática dos seis desvios; a boca
       2,5 % da largura e 1,6 % da altura, a objetiva 5,7 % e 3,6 %, a bola 3,2 % e 2,0 %); nela, os nós da nossa luva
       de apoio caem a (0,652; 0,782), contra (0,604; 0,755) do quadro — 4,8 % e 2,7 %, dentro do erro do ajuste. A
       conta não distingue as pegas da varredura (a bola do ferrolho da ficha é estimada); a comparação fica para a P2,
       no enquadramento do CS2 (Tarefa 17);
  - **o resultado:** `npm run blender -- construir awp --forcar` aprovado em 241 s (a pega em 70 s; a silhueta 98,6 %;
    hash `94588798c0d2`), com a pega igual à do banco de prova (o mesmo caminho e a mesma malha). A mão do gatilho: a
    palma encostada (0,0 mm; afunda 1,44 mm, 269 vértices) e o meio dela a 3,8 mm do punho (apoia nas eminências), o
    médio, o anelar e o mínimo em volta da frente do punho (0,007, 0,026 e −0,025 mm; lado a lado, 2,85 e 3,82 mm), a
    polpa do indicador no gatilho (−0,05 mm), o polegar pelo buraco (o achado 5), a luva entrando 0,049 mm, sem se
    atravessar (a junta que mais afina, a PIP do médio, 1 %). A de apoio: a palma a 0,1 mm, as quatro polpas na face
    (−0,05 a −0,02 mm), as falanges médias a 21,9° (o indicador), 0°, 0° e 0° da face, nenhum dedo à direita, o dorso a
    20,7° da normal da face e a 54,1° da câmera do jogador (as guinadas de 15° e 25°: 59,0° e 49,2°, as duas passam), o
    polegar encostado (−0,05 mm) na quina de baixo do lado direito (a normal da arma embaixo da polpa a 67,8° do
    'baixo', perto do máximo de 70°; a ponta 14,7 mm além da face direita, a distal a 97° da frente), a luva entrando
    0,049 mm (a junta que mais afina, a DIP do indicador, dobrada a 84° na borda de cima, 9,8 %; o máximo, 30 %); as
    pontas engancham na borda de cima e encostam no cano (o médio a 10,3 mm do eixo; o canal dele deixa 15 mm de borda),
    o leque das falanges médias em 3,4, 3,9 e 5,2 mm, e a luva fica a 28,5 mm do bipé dobrado. O modelo alto sem aresta
    aberta (`arma_alto_abertas.py`);
  - **revisão crítica das vistas** (`conferencia/awp/mao_*` e `primeira_pessoa_luvas`; os renders do banco de prova em
    Workbench): a mão de apoio, de trás e da esquerda, como o jogador vê — o dorso de frente, o protetor dos nós e as
    placas dos dedos à vista, os quatro dedos subindo pela face verde e enganchando na borda de cima, as pontas
    encostadas no cano preto —, e o polegar escondido; aparece só a membrana entre ele e o indicador, uma cunha embaixo
    do guarda-mão. Na primeira pessoa da conferência (ainda a posição da 4.1, não a do CS2) ela é a única mão à vista,
    com o dorso para a câmera e o antebraço de massa descendo para a borda de baixo, como no quadro pronto do CS2; a mão
    parece pendurada pelas pontas, com o punho dobrado — conferir na P2, no enquadramento do CS2. De fora, os dedos
    sobem um pouco abertos em leque (o mínimo se afasta na ponta, 10,6 mm entre as distais do anelar e do mínimo; as
    falanges médias passam no `juntosMM`). Pela direita, a ponta do polegar aparece além da face direita, apontando para
    cima, atrás da cabeça do bipé — na inspeção ela pode aparecer. A mão do gatilho: pela esquerda, as pontas do médio,
    do anelar e do mínimo em volta da frente do punho, lado a lado, o indicador dentro do guarda-mato e o polegar saindo
    do buraco como um gancho, a polpa na borda da frente, apontando para a frente e para fora (não deitado ao longo da
    face: o achado 5); pela direita, o indicador quase reto até o gatilho e os outros três fechados, o dorso com a faixa
    escura dos nós; por trás, a membrana na borda da frente do buraco. Para a P2, lado a lado com o CS2: a altura dos
    nós da mão de apoio no quadro pronto (o achado 8), os dedos por cima da borda encostando no cano, o polegar da mão
    do gatilho e o indicador quase reto na inspeção;
  - **a suíte:** 605/605 (as 604 de antes e a da pega sniper no `armaAwp.test.js`; o `pegaFuro.test.js` com a `sniper`
    em `CATEGORIAS_COM_PEGA`). O hash de todas as armas e das luvas mudou de novo com os scripts da pega (a
    pseudonormal, os laços): a Nova e a P90 são construídas com a pega nas Tarefas 14 e 15, e as quatro da 4.1c na 16.
