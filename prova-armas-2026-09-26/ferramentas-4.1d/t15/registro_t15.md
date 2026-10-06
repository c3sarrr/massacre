- **Tarefa 15 (2026-10-05):** a regra `smgBullpup` — `SMG_BULLPUP` em `empunhadura_regras.py` (a mão direita da
  `rifle` no pescoço entre as duas aberturas, com o polegar pelo oval de trás, e a esquerda pela `LATERAL` no lóbulo da
  frente, com a luva do gatilho de obstáculo; o formato no cabeçalho), a luva com a luva da P90 (as duas juntas, sem
  empilhar: `empunhadura_validacao.LUVA_PERTO_MM`, `sobre_a_outra` e `_duas_maos`; `empunhadura_pega._com_quem`, que
  confere a mão do gatilho também contra a de apoio; `DUAS_MAOS_DA_CATEGORIA.smgBullpup` e, no `saidaPega.mjs`,
  `problemasDaLuvaComLuva` e `problemasDasMaosEmpilhadas`), o alvo do polegar que dá a volta buscado só na arma quando a
  regra entra com a outra luva (`empunhadura_pega._pegar`), a dobra da pele do polegar na busca dele
  (`empunhadura_polegar.dobra_da_pele`, `tabela_da_dobra`, o refino pela malha; `empunhadura.Colisor.reforco`),
  `CATEGORIAS_COM_PEGA` com a `smgBullpup` (`src/data/luvas.js`), os testes (`pegaPistola.test.js`: a luva com a luva
  da P90; `pegaFuro.test.js`: a `smgBullpup` na lista; `armaP90.test.js`: a pega smgBullpup no relatório) e a P90
  construída com a pega.
  - **o banco de prova** (`ferramentas-4.1d/t14`: `pega_banco.py` com a base de prova `smgBullpup` — a luva da outra
    mão nos renders, na cor dela —, `varreduras_p90.py`, `resumo_p90e.py`): o da Tarefa 14, com a mão do gatilho
    resolvida no servidor antes da de apoio (`B.mao('d', V.GATILHO)`, que fica em `C['feitas']`). O processo em
    segundo plano vive 2 h: a primeira varredura da mão de apoio com o polegar (72 pegas, ~52 min nos três servidores)
    caiu no limite sem nada gravado, e o `rodar` agora grava cada pega no `<nome>.progresso` assim que ela sai; o
    `sem_polegar` também para o polegar 'baixo' (a busca do alvo e o fechar levavam minutos por pega) — os dedos
    primeiro, em segundos, e o polegar depois, só nas pegas de dedos limpos;
  - **os achados, na ordem:**
    1. **a mão do gatilho no pescoço:** nas 652 pegas das 10 varreduras dos dedos (`direita_dedos_1` a `_10`: a MCP do
       indicador de 35 a 58 mm atrás e de 20 abaixo a 25 acima do ponto do gatilho, a diagonal de −30° a 50°, a
       inclinação, o giro e o tombo da mão, o ponto de 30 % a 85 % da altura do gatilho), 263 não chegam ao gatilho
       sem cruzar a arma. Só o indicador cabe na abertura da frente: a borda de trás dela é reta só de z −31 a −49,5
       (18,5 mm), com o gatilho de z −21,7 a −49,5 e o seletor embaixo; o médio, o anelar e o mínimo ficam deitados na
       face direita do quadro embaixo do gatilho, sem borda em que fechar (o mínimo dá a volta por baixo do lóbulo da
       frente). A mão mais baixa ou com a diagonal negativa fecha o mínimo por baixo do lóbulo e abre o leque do anelar
       (10 a 25 mm); inclinada para baixo (40° a 50°), ela fecha os três de baixo por baixo do pescoço, mas o indicador
       fica de lado no gatilho, a 3,6 a 8,6 mm do ponto, e o polegar aponta para cima, longe do oval; o giro em volta
       do punho dobra os dedos, mas tira a palma da face (6 mm) e o indicador do gatilho (2 a 4 mm). Com o polegar pelo
       oval (as varreduras `dp1` a `dp3`), passa a C — a MCP 40 mm atrás do ponto, na altura dele, sem diagonal: o
       polegar dentro do oval a 1,1 mm da borda, a distal saindo no lado esquerdo, a polpa na borda da frente dele a
       38,4° da frente; com o médio também na abertura (a MCP 45 a 50 mm atrás e 12 a 15 acima), a luva atravessa a
       si mesma (5,2 e 6,0 mm), e 6 a 12 mm mais alta (com a MCP até 5 mm mais para trás), 1,6 a 3,8 mm. A regra fica
       com a C;
    2. **o polegar de apoio assentava na mão do gatilho:** a mão de apoio pela `LATERAL` no lóbulo da frente (o
       soquete `mao_e` no meio da barra embaixo da abertura da frente, de z −102 a −60). Com a palma de 5 a 20 mm
       abaixo do soquete (`esquerda_dedos_1` e `_2`, 144 pegas), nenhuma passa nos dedos (a palma fica em cima da face,
       os dedos sobem até o carregador); de 45 a 75 mm abaixo, com a palma no soquete ou à frente (`_3`, 96), o mínimo
       passa da frente do lóbulo, que sobe arredondado até a boca, e fica no ar (a polpa a 19 a 41 mm da arma); com as
       pontas giradas para trás no plano da face (`_4` e `_5`, 96), 36 passam em tudo o que é dos dedos. Nelas, o
       polegar 'baixo' assentava no mínimo da mão do gatilho, a 25 a 35 mm da arma, com qualquer `lado` da regra: a
       busca do alvo (`alvo_na_arma`) corria na arma com a outra luva, e embaixo do lóbulo a superfície mais perto da
       polpa era a mão do gatilho, que dá a volta por baixo dele. O alvo agora é buscado só na arma (`sobre`, a arma
       sem a outra luva, que já ia ao `_pegar` para o polegar deitado da pistola), e a outra luva continua obstáculo no
       fechar;
    3. **a pele da tenar dobrava sobre si mesma:** com o alvo na arma, nas 36 pegas o polegar assenta na arma, mas 25
       ficam fora do lugar (a polpa numa face a 101° a 104° de "para baixo": o polegar sobe pelo entalhe entre o punho
       e o lóbulo e encosta numa parede dele), 6 não acham pose sem cruzar, e as 5 que acertam o lugar (a 63,4° e
       67,2°) atravessam a luva 2,0 a 3,7 mm. O par mais fundo é da própria tenar — a pele do metacarpo do polegar com
       ela mesma e com a da palma, triângulos que no repouso ficam a menos de 12 mm (o `PERTO_MM`), que a
       `dobra_da_tenar` do solver deixa de fora (são a pele da dobra da CMC). Ela vem só dos graus da CMC: com a MCP, a
       IP ou qualquer dedo no repouso, a mesma; com o polegar no repouso, zero. Mapeada pela abdução e pela flexão da
       CMC (a tabela da luva esquerda), ela só aparece com a abdução de 15° ou mais além do repouso para dentro da
       palma, em qualquer flexão (de 0,3 a 9 mm) — e o polegar dessas pegas chegava a 22°. Medida só no refino pela
       malha (a busca de padrão a partir da solução das cápsulas), ela não sai: as três pegas da prova ficam com 1,8 a
       2,05 mm. Na busca global, numa tabela por luva — a dobra medida como na validação da luva (os pares que se
       cruzam, fora os que dividem um vértice, cada um pelo vértice mais fundo; só a pele, sem as peças do reforço)
       pelos graus da CMC (a abdução e a flexão de 5° em 5°, a rotação em 4 passos: 600 avaliações, ~20 s) e somada à
       IK e à escolha do alvo, com o refino medindo na malha —, 4 das 36 passam em tudo, com a dobra de 0 a 0,30 mm;
       o código definitivo dá os mesmos números da prova;
    4. **a mão de apoio da regra:** a grade fina em volta das quatro (a palma a ±2,5 mm, as giradas a ±2,5°, a
       inclinação a ±1,25° e a guinada a ±2,5°; 57 pegas) passa 32. A da prova (5 mm à frente do soquete) tem 7 das 10
       vizinhas — com a girada a ±2,5°, o anelar deita a 55° da face ou a luva entra 2,3 mm na arma; a regra fica com a
       7,5 mm à frente, com 8 das 10: 2,5 mm mais à frente, a falange média do anelar deita a 55° da face, e com a
       inclinação de −11,25° o polegar fica a 1,02 mm da arma (o máximo, 1 mm). Na da prova, o `lado` do polegar não
       muda nada: só para baixo (com o peso de 4 e de 1), para baixo e para a esquerda e o da `LATERAL` com o peso de 1
       passam todos; a regra fica com o da `LATERAL`;
  - **o resultado:** `npm run blender -- construir p90 --forcar` aprovado em 503 s (a pega em 82,5 s, com as duas
    tabelas da dobra; a silhueta 99,6 %, bruto 98,8 %; a de três quartos 95,95 %; perto 38.880, mundo 5.700, longe
    1.415 triângulos; 3,89 MB), com a pega igual à do banco. A mão do gatilho: a luva 0,048 mm dentro da arma, a polpa
    do indicador encostada no gatilho (−0,045 mm), o médio, o anelar e o mínimo a até 0,028 mm do quadro, lado a lado
    (4,3 e 6,6 mm na média), o polegar dentro do oval a 1,08 mm da borda, sem lado errado, a polpa encostada (−0,012
    mm); a palma afunda 0,98 mm (260 vértices); a luva do gatilho fica 0,084 mm dentro da de apoio (o mínimo dela; o
    máximo é 0,3). A de apoio: 0,043 mm dentro da arma, as polpas a até 0,02 mm da face, as falanges médias a 0,2°,
    11,2°, 31,1° e 5,9°, nenhum dedo à direita do meio, o dorso a 22,8° da normal da face (a 64° da câmera do jogador,
    no banco), o polegar por baixo, encostado (−0,043 mm), a 67,2° do lugar, com a ponta a 0,07 mm da luva do gatilho,
    sem entrar nela; os dedos lado a lado (3,2 a 7,7 mm na média); a luva atravessa a si mesma 0,12 mm (a tenar; o
    máximo é 0,3); a palma afunda 0,40 mm (135 vértices). O modelo alto sem aresta aberta (`arma_alto_abertas.py
    p90`); `conferir p90`, 19 vistas; suíte 611/611;
  - **revisão crítica das vistas** (as da conferência — `mao_direita_*`, `mao_esquerda_*` e `primeira_pessoa_luvas` —
    e as do banco): a mão do gatilho fica rente à face direita do pescoço; o indicador entra pela abertura da frente até
    o gatilho, e a ponta dele aparece do lado esquerdo, entre o indicador e o médio da mão de apoio; o médio, o anelar e
    o mínimo ficam esticados, deitados na face direita embaixo do gatilho — de lado, a mão lê como espalmada, não como
    mão que fecha. O polegar sai pelo oval de trás, dobrado, e deita para a frente no lado esquerdo com a ponta no
    quadro; de perto, pela direita, a pele entre o polegar e o indicador entra no oval em pregas claras e vincadas (a
    "tenda" da Tarefa 11; a luva passa na validação). A mão de apoio fica de pé na face esquerda do lóbulo, com o dorso
    e o protetor dos nós para o jogador e os quatro dedos retos e um pouco afastados — como a da AWP e a da Nova, lê
    como espalmada —, e o polegar por baixo, que da câmera do jogador do banco aparece como uma alça embaixo da arma,
    entre a palma e o quadro (no CS2 ele fica escondido). As duas luvas quase se encostam embaixo do lóbulo. Em
    primeira pessoa, só os nós da mão de apoio aparecem, no canto de baixo à direita, com a arma baixa (o enquadramento
    é da Tarefa 17). Para a P2, lado a lado com o CS2: os dedos do gatilho esticados na face (os do desenho passavam
    pelo oval de trás, que fica atrás da palma), a mão de apoio de pé e espalmada, o polegar de apoio à vista embaixo
    da arma e a "tenda" no oval;
  - **a dobra da pele nas outras armas:** o solver do polegar mudou para todas. A AWP reconstruída (`construir awp
    --forcar`, 260 s; a pega em 87,4 s, 17 s a mais com as tabelas) sai igual: os mesmos graus dos dois polegares, os
    mesmos contatos e a luva sem atravessar (os polegares dela ficam fora da região da dobra); a silhueta 98,6 %, 3,60
    MB. A Nova reconstruída (`construir nova --forcar`, 217 s; a pega em 48,4 s, 14 s a mais) também: o relatório das
    duas mãos igual ao de antes; a silhueta 99,7 %, 3,43 MB. Suíte 611/611 de novo, com as duas;
  - o hash de todas as armas e das luvas mudou de novo com os scripts da pega e do polegar: a AWP, a Nova e a P90 estão
    construídas e válidas; as quatro da 4.1c ficam para a Tarefa 16 (o polegar do gatilho do fuzil é o que dá a volta,
    pelo `alvo_na_arma`: conferir lá se a dobra da pele muda alguma pega).
