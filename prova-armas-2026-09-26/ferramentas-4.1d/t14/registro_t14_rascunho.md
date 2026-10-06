- **Tarefa 14 (2026-10-05):** a regra `escopeta` — `ESCOPETA` em `empunhadura_regras.py` (a mão direita da `rifle` no
  pescoço da coronha com o polegar deitado por cima dele e a esquerda pela `LATERAL` na bomba, pelo soquete `bomba`, com
  o polegar por baixo; o formato e os números no cabeçalho e na regra), a conferência da mão que pega numa peça móvel no
  fim do curso dela (`empunhadura_validacao.no_fim_do_curso`, chamada no `empunhadura_pega.resolver` quando o soquete
  tem a `peca`; no Node, `MAO_NA_PECA_DA_CATEGORIA` e `problemasDoFimDeCurso`), o polegar do gatilho deitado no Node
  (`POLEGAR_DEITADO_DA_CATEGORIA`; o texto do Python passa a dizer de quem é o polegar deitado), a mão de apoio lateral
  numa função só do Node (`problemasDoApoioLateral`, exportada: o lugar 'borda' ficou sem categoria e é conferido por
  ela nos testes), `CATEGORIAS_COM_PEGA` com a `escopeta` e `POLEGAR_LATERAL_DA_CATEGORIA.escopeta` em 'baixo'
  (`src/data/luvas.js`), os testes (`pegaLateral.test.js`: o fim do curso da bomba, o polegar deitado no pescoço e o
  'borda' pela função; `pegaFuro.test.js`: a `escopeta` na lista; `armaNova.test.js`: a pega escopeta no relatório) e a
  Nova construída com a pega.
  - **o banco de prova** (`ferramentas-4.1d/t14`: `pega_banco.py`, `varreduras_nova.py`): o da Tarefa 13 generalizado —
    `configurar(arma, categoria)`, a .blend da conferência com as luvas montadas uma vez, a regra da categoria (ou a
    base de prova pelo nome, `escopeta_borda`, para as varreduras que partiram dela continuarem reproduzíveis), cada mão
    pelo `_uma_mao`, o afundamento e a `conferir_mao` com as contas a mais da prova (a entrada por osso, a folga a cada
    peça, a ponta e a distal do polegar, o dorso contra a câmera do jogador), o protótipo do fim do curso e o
    `resolver`; até quatro sessões em paralelo. O trabalho entrava na fila escrito direto no `.py`, e o servidor o lia
    pela metade (um trabalho de 0,0 s sem saída): agora ele é escrito num `.tmp` e renomeado;
  - **os achados, na ordem:**
    1. **o vão do guarda-mato:** com a folga de 1 mm do fuzil, "o indicador cruza a arma mesmo com a polpa 20 mm acima
       do alvo" em 25 das 27 pegas da primeira varredura dos dedos (a MCP do indicador de 35 a 55 mm atrás do ponto do
       gatilho, de 15 abaixo a 5 acima, a diagonal de 0° a 30°) e em 31 das 36 da segunda (a MCP mais alta, o giro em
       volta do pescoço): a abertura do guarda-mato da Nova tem 20 mm de altura (z −50 a −70,9), e o dedo da luva, 17 a
       19 mm de espessura — com 1 mm de folga dos dois lados, não sobra vão. Com a folga de −0,25 mm (o aperto da M4A4:
       a luva comprimida no guarda-mato), nenhuma das 24 da terceira cruza (6 cruzam a arma na chegada) e a polpa
       encosta no gatilho;
    2. **o polegar do gatilho "deitado por cima do pescoço, apontando para a frente"** (o quadro pronto do CS2): em 159
       pegas com ele deitado (o giro em volta do pescoço de −25° a +25°, a MCP de 52,5 a 57,5 mm atrás e de 8 a 24 mm
       acima do ponto do gatilho, a diagonal de −10° a 10°, o eixo pela rampa de cima do pescoço, a face pedida de 0°,
       15° e 25° para a direita; `direita_polegar_1` a `_5`), 72 não chegam ao gatilho (o indicador cruza a arma); 76
       deitam o polegar reto por cima do pescoço, mas em diagonal, a 37° a 61° da frente, com a ponta até 29 mm além da
       face esquerda; 11 deitam para a frente (17° a 29°), mas pelo lado direito do receptor, 14 a 18 mm além da face
       direita, no ar — nas duas com o indicador no gatilho a luva atravessa a si mesma (3,3 e 3,5 mm), e nas outras a
       polpa do indicador fica a 1,1 a 14 mm dele. Com a mão no pescoço, a base do polegar fica no lado direito: para
       deitar por cima do pescoço ele cruza o alto; com o giro positivo (a mão por cima, a base no alto), o indicador
       não chega ao gatilho sem cruzar a arma. Passam 9, todas em diagonal (42° a 53°); a regra fica com a de MCP 56 mm
       atrás e 16 mm acima do ponto, o giro de −5° e a diagonal zero (o polegar a 43,6°, a ponta 13,4 mm além da face
       esquerda). A faixa que passa é estreita: 2 mm mais baixa ou 2,5° de giro a mais, a polpa do indicador para a 1,8
       a 2 mm do gatilho; 2 mm mais alta, o indicador cruza a arma. A regra pede o polegar reto, deitado e encostado
       (sem `para_frente`); a direção fica para a P2;
    3. **o polegar de apoio 'borda' não cabe na Nova:** o desenho (seção 5.2) e a pesquisa (cs2.md) põem o polegar da
       mão de apoio deitado ao longo da borda de cima da bomba, apontando para a boca, com os dedos subindo pela face.
       Com a palma na face esquerda e os dedos para cima, o polegar da mão esquerda aponta para trás (o lado radial);
       para a frente, só com a mão girada no plano da face até os dedos deitarem para a frente, e quatro dedos deitados
       (~76 mm) não cabem nos 51 mm da face da bomba (43 de face e a quina de baixo). As provas: girada de 50°, 55° e
       60° — o polegar cruza a mão (3,9, 6,1 e 2,8 mm); 65° — o polegar a 55° da frente, o mínimo a 27 mm da arma, o
       leque de 40 mm e a luva atravessando a si mesma 6,4 mm; a varredura `esquerda_borda_1` (girada de 80° a 100°, a
       palma em duas alturas, a inclinação de −12,5° a 35°; 18 pegas): nenhuma passa — 10 não fecham (o polegar cruza a
       mão ou a mão cruza a arma na chegada); nas 8 que fecham, o mínimo fica a 12 a 26 mm da bomba e o anelar longe
       dela ou embaixo (a faceta de 90°) — também nas três em que o polegar deita para a frente (13° a 19° da frente; a
       melhor, a 13,4°, reto e encostado, com o mínimo a 23 mm e o dorso a 55° da face). A mão "por cima" (girada 180°
       no plano da face, a única em que o polegar deitado na borda aponta para a frente sem cruzar a mão;
       `esquerda_por_cima`; a palma 0 e 15 mm acima do soquete, a inclinação de 0° a −45°; 6 pegas): nenhuma fecha — o
       polegar deitado não acha pose sem cruzar, ou a mão cruza a arma já na chegada. A regra fica com o 'baixo', como a
       AWP e a P90; o 'borda' continua na regra (o solver, a validação do Python e a `problemasDoApoioLateral` do Node),
       sem categoria, para a decisão da P2;
    4. **o 'baixo' na bomba e as facetas da quina:** a LATERAL do bloco na bomba (B1: a palma 62,5 mm abaixo do soquete,
       inclinada −12,5°, a guinada de 20°) passa em tudo, com o polegar a 67,5° do lugar (o máximo, 70°). A fina
       (`esquerda_baixo_1`, 36 pegas: a palma, a inclinação, a girada no plano da face e a guinada) passa 13 — nenhuma
       com a girada de −5° (as pontas para trás), 5 de 12 sem girada, 8 de 12 com 5° — e as reprovadas caem em degraus:
       a malha de jogo da bomba tem facetas de 15° nas quinas, e a normal embaixo da falange média vale 7,5°, 22,5°,
       37,5°, 52,5° ou 90°: o dedo que sobe para a faceta de 52,5° da quina de cima reprova (37,5° passa), o mínimo que
       desce para a de baixo (90°) também, e o polegar assenta na de 52,5° ou na de 67,5° da quina de baixo. A grade
       fina em volta da B1 (`esquerda_baixo_2`, 27 pegas: a palma a ±1,25 mm, a inclinação a ±1,25°, a guinada a ±2,5°)
       dá a guinada de 17,5° com as nove vizinhas passando (a de 20°, 4 de 9; a de 22,5°, 1 de 9: o anelar na faceta de
       52,5° ou a luva atravessando a si mesma ~1,9 mm); a regra fica com ela;
    5. **a mão no fim do curso:** a pega em repouso não diz se a mão de apoio, levada com a bomba, entra no receptor ou
       no guarda-mato no fim do curso. A conferência nova (`no_fim_do_curso`) leva a luva posada com a mesma mudança da
       peça em cada passo da ordem dela (a bomba recua 100 mm arrastando o ferrolho) e mede a entrada na arma movida; na
       B1, 0,046 mm em repouso e no fim do curso, igual ao protótipo do banco. Na revisão do código: os nós filhos da
       peça eram levados pelo `fim_de_curso._com_filhos`, que toma a matriz atual por repouso — no segundo passo de uma
       peça de vários (o giro e o curso de um ferrolho) eles iriam errado; agora vão a partir do repouso;
    6. **o polegar deitado no texto do Python:** o problema dizia sempre "o polegar da frente", também no do gatilho da
       Nova: o `_polegar_deitado` recebe quem é (o da frente, o do gatilho, o de apoio);
  - **o resultado:** `npm run blender -- construir nova --forcar` aprovado em 210 s (a pega em 34,1 s; a silhueta 99,7
    %, bruto 97,8 %; perto 25.736, mundo 5.700, longe 1.415 triângulos; 3,43 MB), com a pega igual à do banco. A mão do
    gatilho: a luva 0,047 mm dentro da arma, a polpa do indicador encostada no gatilho (−0,047 mm) e os outros três a
    até 0,04 mm do pescoço, lado a lado (2,2 e 2,4 mm na média); o polegar reto (0,2° de curva), os trechos a 6,78,
    5,40, 3,79, 1,38, −0,05 e 1,02 mm da arma, a 43,6° da frente; a palma afunda 0,04 mm (60 vértices). A de apoio:
    0,0 mm dentro da arma, as polpas a até 0,11 mm da face, as falanges médias a 7,5°, 37,5°, 22,5° e 0°, nenhum dedo à
    direita, o dorso a 21,4° da normal da face, o polegar por baixo, encostado (0,1 mm), a 67,5° do lugar, os dedos lado
    a lado (3,5 a 4,1 mm); a palma afunda 0,60 mm (119 vértices); no fim do curso da bomba (com o ferrolho), 0,0 mm
    dentro da arma. O modelo alto sem aresta aberta (`arma_alto_abertas.py nova`); `conferir nova`, 19 vistas; suíte
    608/608;
  - **revisão crítica das vistas** (as da conferência, `mao_direita_*`, `mao_esquerda_*` e `primeira_pessoa_luvas`, e as
    do banco): a direita fecha firme no pescoço — o indicador entra pelo guarda-mato até o gatilho (quase reto: a PIP e
    a DIP a 0,1° e 0,2°, como o da AWP), o médio, o anelar e o mínimo em volta da frente do pescoço — e o polegar deita
    reto por cima dele, em diagonal, com a polpa na quina de cima do lado esquerdo e a ponta sobrando no ar: rígido
    perto do polegar do CS2, que aponta para a frente. A esquerda sobe pela face da bomba e as pontas passam da borda de
    cima e encostam no lado do cano (vistas pela direita, três pontas aparecem por cima do cano); em primeira pessoa ela
    fica de pé, os dedos retos, e lê mais como mão espalmada do que como mão que agarra. O polegar de apoio, por baixo,
    sobe pela face direita (a distal para cima, invisível do jogador). Em primeira pessoa a mão do gatilho fica fora do
    quadro (no CS2, só o polegar e o dorso no canto de baixo à direita: o enquadramento é da Tarefa 17). Para a P2, lado
    a lado com o CS2: o polegar do gatilho em diagonal, o de apoio por baixo (o 'borda' do desenho não cabe), a mão de
    apoio de pé e as pontas no cano;
  - o hash de todas as armas e das luvas mudou de novo com os scripts da pega (a AWP e as da 4.1c ficam para o
    `construir` delas).
