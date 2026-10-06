- **Tarefa 12 (2026-10-05):** a regra `lateral` — o módulo `empunhadura_lateral.py` (`conferir_regra`,
  `direcao_do_lugar`, `fechar_ate_o_meio`, `medir` e `problemas`), a regra `LATERAL` em `empunhadura_regras.py` (o
  formato no cabeçalho dele), a pega (`empunhadura_pega._pegar`: os dedos da mão lateral fecham pelo
  `fechar_ate_o_meio`, também no `empunhadura_arma.juntar_dedos`, que ganhou o `fechar`; o polegar 'baixo' é o que dá a
  volta, pelo `alvo_na_arma` e o `fechar_no_alvo`, e o `_assentar_na_arma` agora levanta `PolegarCruza`, para a palma
  chegar de novo com a CMC da solução, e põe o desvio da MCP na faixa do came depois de fechar a MCP e a IP), a medida
  na validação (`empunhadura_validacao.conferir_mao`: o `ladosLateral`), o Node (`saidaPega.mjs`: `problemasDaLateral`,
  o polegar de cada lugar e os dedos lado a lado da mão de apoio; `src/data/luvas.js`: `LATERAL_DA_CATEGORIA` =
  `{sniper: 'e', escopeta: 'e', smgBullpup: 'e'}`, `POLEGAR_LATERAL_DA_CATEGORIA` = `{sniper: 'baixo', escopeta:
  'borda', smgBullpup: 'baixo'}` e, em `LIMITES_DA_PEGA`, `lateralDireitaMM` 1, `lateralDorsoGraus` 35,
  `lateralPolegarGraus` 70 (achado 19) e `lateralMediaGraus` 45) e a prova (`provas_lateral.py`, `npm run blender --
  provar lateral [pegas...]`). O `src/characters/hands/pega.js` da lista do plano não mudou: o jogo lê as mãos da pega
  como antes (as duas, que as três têm desde a Tarefa 11); a regra é só do solver.
  - **os testes (`pegaLateral.test.js`, quatro):** as constantes (`LATERAL_DA_CATEGORIA`,
    `POLEGAR_LATERAL_DA_CATEGORIA`, a `FRENTE_DA_CATEGORIA` só com o `rifle`, as duas mãos das três e os limites); a
    aprovação das três categorias (a Nova com o polegar deitado na borda) e nos limites; a reprovação de cada conta — um
    dedo 1,6 mm à direita, o dorso virado para a arma (120°), o polegar fora do lugar (120°) ou no lugar de outra
    categoria, uma polpa a 1,6 mm ou faltando, a falange média deitada por cima da peça (88°) ou faltando, o polegar
    'baixo' com o contato a 1,6 mm ou sem ele, o 'borda' curvo (35°), torto (30°), sem a distal encostada ou faltando —,
    a falta do `ladosLateral` e a dos dedos lado a lado ("a mão de apoio sem a conferência dos dedos lado a lado"); o
    fuzil (a regra da frente) e a mão do gatilho não pedem. Viram falhar pelo import (`LATERAL_DA_CATEGORIA` não
    existia). O `pegaFuro.test.js` ganhou o `mediasGraus` e o contato do polegar no braço de apoio.
  - **o formato, diferente do D5 e do Passo 3 em um ponto:** o polegar 'baixo' (a AWP e a P90) não é o deitado sob a
    peça apontando para a frente, e sim o que dá a volta por baixo dela inteira até a quina de baixo do lado direito,
    encostado — o da mão do gatilho do fuzil (os achados 1 e 10 a 12); o 'borda' (a Nova) é o deitado do D5. Da seção
    5.0 do desenho, a pega da regra tem o dorso virado para o jogador, com o protetor dos nós à vista (a guinada de 20°,
    achado 18), e o polegar por baixo, escondido do jogador e apontando para a frente, para dentro e para cima (a distal
    a 63° da frente). O `cs2.md` diz da AWP só que "o polegar fica por baixo, escondido"; o "para a frente" do D5 era
    leitura minha.
  - **a prova do bloco (`provas_lateral.py`):** a mão esquerda pela regra num bloco de 54 × 56 mm com quinas de 3 mm (a
    seção do guarda-mão da AWP: a largura da ficha e a altura do contorno no ponto da mão de apoio, x −585), pelo mesmo
    caminho da pega das armas (o `_uma_mao`, o afundamento da palma e a `conferir_mao` inteira), com quatro vistas (de
    fora, de baixo, de cima e de trás, da esquerda e de cima, como a câmera do jogador) e, na linha de cada pega, o
    ângulo do dorso com a câmera do jogador e a direção da distal do polegar. Os achados, na ordem:
    1. **o polegar 'baixo' para a frente não existe na anatomia:** com a palma na face esquerda, o dorso para fora e os
       dedos para cima, o polegar de repouso da mão esquerda aponta para trás (o lado radial: T = N × F = −X, com a
       normal da palma N = −Y e os dedos F = +Z); deitado por baixo com o eixo para a frente, ele ficou a 93° da frente
       ou cruzou o bloco (`PolegarCruza`, 1,61 mm). → o 'baixo' passou a deitado por baixo da peça, apontando para trás
       e para dentro, e só o 'borda' (a Nova) apontando para a frente (`para_frente`) — trocado depois pelo polegar que
       dá a volta (achado 12);
    2. **o polegar que dá a volta cruzava o bloco:** o da mão do gatilho do fuzil (`alvo_na_arma` com o `lado` para
       baixo) cruzou o bloco em 3 das 4 pegas ("o polegar da solução cruza a arma ou a mão, mesmo com a MCP e a IP
       abertas"): o `_assentar_na_arma` levantava `RuntimeError`, sem a segunda chegada da palma com a CMC da solução,
       que o deitado e o do furo têm → na hora, o deitado; no fim, o `PolegarCruza` também ali (achado 12);
    3. **a mão espalmada na face deixava os dedos no ar:** a face do guarda-mão tem 56 mm e os dedos da luva ~90 mm; com
       a palma chata e alta na face (só a girada no plano dela), os nós ficavam na borda de cima e as polpas a 14–46 mm
       do bloco (os dedos parados no plano do meio, sem tocar nada) → a concha: a mão inclinada em volta do eixo da arma
       (o giro em X da regra, −30°), as pontas para fora da face e a palma para cima, mais baixa — trocada depois pela
       mão quase chata e baixa (achados 9 a 11 e 15);
    4. **os dedos dobravam por cima da peça:** com a palma a −35 mm, os nós ficavam no meio da face e as falanges médias
       deitavam no alto do bloco — as polpas encostadas, mas na face de cima, e a medida só olhava a distância → o
       `polpasGraus` (a normal da arma embaixo do ponto mais perto de cada polpa, a até 45° da da face), no Python e no
       Node — trocado depois pelo `mediasGraus` (achado 13);
    5. **a chegada:** na pose de pegar, a tenar fazia um calombo de 20 mm para o lado da palma e cruzava o bloco 40 mm
       antes da chegada → `polegar_afastado` (como a de apoio da pistola); na nova chegada com a CMC da solução, a tenar
       fica 20 a 25 mm à frente da palma, e de 40 mm ela já cruzava → `chegada` (60, 60). Na mão chata do fim, os dois
       viraram margem (achado 17);
    6. **as vistas:** a de baixo saía preta (a câmera embaixo do chão do estúdio) → o chão some só nela; a pega seguinte
       achava a luva fora da origem ("as correções pedem a luva e o rig na origem") → o rig volta ao repouso e à origem,
       com o `view_layer.update()` (a luva é filha do rig), depois das vistas;
    7. **a câmera do CS2 pela tela:** a altura dos nós da luva de apoio no quadro da AWP não sai da pose da câmera — o
       P3P com a boca, a objetiva e a bola do ferrolho (só os números do `cs2.md`; `ferramentas-4.1d/t12/p3p_cs2.py`) só
       acha a arma rolada, de pé, e o ajuste com ela em pé erra ~5 % da largura da tela: a bola da nossa ficha é
       estimada (o lado direito não aparece na vista de lado do jogo). A pega segue a descrição do quadro e a anatomia,
       e a comparação fica para a P2;
    8. **a suíte:** a mensagem da falta dos dedos lado a lado tinha perdido "a mão da frente" (o `pegaGlb.test.js`
       reprovou) → `problemasDosJuntos` diz de quem é ("a mão da frente" ou "a mão de apoio");
    9. **a concha leva o dorso para longe do jogador e o polegar para dentro do bloco:** inclinada −30°, a palma olha
       para cima e o dorso para baixo e para a esquerda — da câmera do jogador o protetor dos nós aparece de raspão —, e
       o polegar, que na oposição vai para o lado da palma, sobe para dentro do canto do bloco: a exploração
       (`ferramentas-4.1d/t12/explora_polegar_baixo.py`: a grade dos seis graus do polegar numa pega fixa, 12 960 poses)
       achou 2 535 poses com a polpa por baixo do bloco, todas cruzando o bloco ou a mão;
   10. **com a mão chata na face, a −55 mm, o polegar passa por baixo:** 94 das 3 600 poses da grade encostam a polpa na
       face de baixo sem cruzar nada — o polegar em oposição atravessa por baixo do bloco até o lado direito (a polpa em
       y −15 a −26 mm) e aponta para a frente e para cima. A anatomia que eu tinha suposto no achado 1 (o polegar para
       trás) é a do polegar no plano da palma, não a dele em oposição;
   11. **as posições da mão** (as 3 600 poses do polegar em cada uma): sem a concha (a inclinação 0 ou −15°) e sem girar
       a mão no plano da face, com a palma a −55 ou −65 mm, há 38 a 94 poses do polegar por baixo sem cruzar nada (a
       polpa na face de baixo, quase sempre perto da borda de baixo do lado direito, y −21 a −27 mm, a distal para a
       frente e para cima; algumas quase retas para a frente, (0,97; 0,04; 0,24)); com a mão girada 35° para a frente
       (−55 e −45 mm) ou inclinada para dentro (+10°), nenhuma — o polegar em oposição sobe para dentro do bloco;
   12. **o 'baixo' é o polegar que dá a volta:** deitado, ele não passa na mão chata — a −65 mm e −15°, a curva de
       27,4°, a falange proximal a 19,6 e 13,1 mm da arma e 61° da frente (quatro problemas); a −55 mm e 0°, 23,7°, 11,4
       mm e 76,3°. → o 'baixo' é o polegar que dá a volta (o `lado` da regra para baixo, 30° do −Z para dentro, o −Y; o
       `peso` 4), com a nova chegada: o `_assentar_na_arma` levanta `PolegarCruza` com os graus abertos, e o `_uma_mao`
       chega de novo com a CMC deles (o achado 2 resolvido). O `conferir_regra` pede no 'baixo' o `lado` a até 60° do −Z
       e nenhum deitado; no Node, o 'baixo' é o contato `polegar` (a até `contatoMM`, com os outros contatos) e as
       contas do deitado ficam só no 'borda';
   13. **a falange média no lugar da polpa:** com os dedos subindo até a borda de cima e a ponta enganchando nela — o
       "até a borda de cima" do quadro do CS2 —, a polpa fica na quina ou na face de cima, e o `polpasGraus` reprovava a
       pega certa; e com a palma alta (−55 mm, chata) as falanges médias deitavam por cima do bloco (67,5°), com o
       indicador e o médio parados no plano do meio e as polpas a 12 e 22 mm. → `mediasGraus` (a normal da arma embaixo
       do ponto mais perto da falange média de cada dedo a até 45° da da face: o `lateralMediaGraus` no lugar do
       `lateralPolpaGraus`), no Python e no Node;
   14. **o efeito came:** a −60 mm e −10°, o único problema era o desvio da MCP do polegar a 19,20° com a faixa em
       19,16° (a −65 mm e 0°, 18,30 contra 18,27): a flexão da MCP que o `fechar` acrescenta depois da IK estreita a
       faixa do desvio, e ele ficava de fora → o `_assentar_na_arma` põe o desvio na faixa (`no_came`) depois de fechar
       a MCP e a IP;
   15. **a mão quase chata, sem guinada (as varreduras com o polegar que dá a volta, `provas_lateral.py`):** a primeira
       pega que passou foi a −65 mm e −15°; em volta dela, com o limite de 45° do lugar do polegar daquela hora, passam
       a altura de −60 a −70 mm, a inclinação de −15° a −20° e a girada de −10° a 0°, com o `lado` do polegar de 0° a
       30°; reprovam −10° (o médio deita por cima da peça, 67,5°), −25° e −30° (o polegar na face esquerda, 90°), a
       guinada de +10° (o médio por cima e o polegar na quina) e a de +20° (o polegar no ar, a 4,49 mm). Mas essa pega
       mostra o polegar entre a palma e a peça, apontando para trás (a distal a 118° da frente), e o dorso de raspão
       para a câmera do jogador (a 75,7°; a câmera da prova é a de trás, da esquerda e de cima, `DO_JOGADOR`): a seção
       5.0 do desenho pede o dorso virado para o jogador, com o protetor dos nós à vista, e o polegar escondido,
       apontando para a frente;
   16. **o lado do polegar não muda nada no bloco:** com o `lado` a 0°, 15° e 30° do −Z, o polegar sai o mesmo (sem a
       guinada, os seis graus e o alvo iguais até a segunda casa; com ela, na −60/−10, a distal a 57,9° e 58,0° da
       frente): o `peso` (4 mm² de custo por mm andado no lado) é pequeno perto do encosto e da normal da polpa, e a
       solução fica no limite da rotação da CMC (17°) e perto do da extensão dela (−18,6° de −20). A regra fica com 30°
       (para baixo e para dentro, onde o CS2 esconde o polegar), e mais peso não leva a polpa para baixo da quina
       (achado 18);
   17. **a chegada e o polegar afastado viraram margem:** nas duas pegas que a regra teve (a −65/−15 sem guinada e a
       −62,5/−12,5 com ela), a palma chegando de 40 mm passa (a palma a 0,036 e a 0,0 mm da face) e sem o polegar
       afastado também (0,035 e 0,0): com a palma no canto de baixo, a tenar não chega na face antes dela
       (`ferramentas-4.1d/t12/chegada_lateral.py`). Os dois ficam, com o porquê nos comentários, de margem para as peças
       das armas, conferidos na varredura de cada uma;
   18. **a guinada (o dorso para o jogador):** girada de 15° a 25° em volta do alto, a mão mostra o dorso a 51–62° da
       câmera do jogador, com o protetor dos nós de frente, e o polegar fica escondido por baixo da peça, apontando para
       a frente, para dentro e para cima (na região da regra, a distal a 45–69° da frente; com a palma mais baixa, a
       −65/−10 e a −70/−5, ou a girada −10°, ela vira para o lado, a 93–108°) — o quadro do CS2 e a seção 5.0. Mas, com
       o limite de 45° do lugar do polegar, de 26 pegas com guinada só 6 passavam, em pontos soltos (a −60/−15, a
       −65/−10, a −70/−5 e a −60/−10 com a girada 0° e −10° e o `lado` 0° e 30°): a polpa assenta na quina, e a
       bissetriz dela trocava de lado com um milímetro (as faces da quina do bloco a 22,5° e 67,5°); as vistas das que
       passavam e das que reprovavam são iguais. Mais peso no lado do polegar não leva a polpa para baixo da quina (com
       20 ela fica na mesma; com 40 o alvo vai longe e o polegar fica no ar, a 4,6–6,7 mm, apontando para fora:
       `ferramentas-4.1d/t12/chegada_lateral.py`, com `PESO`);
   19. **o lugar do polegar é a face ou a quina dela:** o limite de 45° era a bissetriz da quina, onde a polpa assenta —
       no 'baixo' e, pior, no 'borda' (a Nova), em que o polegar deitado "ao longo da borda de cima" fica na quina por
       definição. → `lateralPolegarGraus` 70 (Node) e `POLEGAR_GRAUS` 70 (Python): a face do lugar ou uma quina dela,
       nunca uma face de lado (90°: a esquerda, à vista do jogador, ou a direita); os testes aprovam 70 e reprovam 90 e
       120 (vistos falhando antes, com o limite de 45). A falange média continua até a bissetriz da quina de cima (45°):
       passar dela é deitar por cima da peça. Relidas com o limite novo (os mesmos números), as pegas da guinada passam
       numa região contínua: a −62,5/−12,5 com a guinada de 15°, 20° e 25°; a −60/−15 com a girada de −10° a +10°; a
       −60/−10 (guinada de 15° a 25°, girada −10° e 0°, `lado` de 0° e 30°); a −65/−10, a −55/−15 e a −70/−5. Reprovam
       ainda o médio deitando por cima (a inclinação −5° ou −20°, ou a palma a −70 com −10°), o polegar no ar (a
       −65/−15, a −55/−10 e a girada +10° da −60/−10) e uma polpa longe (a −60/−5);
   20. **onde o polegar fica:** medido no referencial do bloco (`ferramentas-4.1d/t12/onde_polegar.py`), o polegar passa
       por baixo da peça inteira — a polpa assenta na quina de baixo do lado DIREITO (y −33 mm; o bloco vai de −27 a
       +27), e a ponta fica no ar, 14 a 16 mm ao lado da face direita, 4 a 9 mm acima da face de baixo —, nas duas pegas
       que a regra teve; as polpas dos quatro dedos ficam na face de cima (a ponta enganchada) e as falanges médias ao
       lado da face esquerda. Eu tinha escrito que a polpa assentava na quina de baixo da esquerda: corrigido nos
       comentários. Do lado do jogador o polegar não aparece (a peça o esconde); a ponta além da face direita fica para
       conferir na AWP de verdade (Tarefa 13) e na inspeção;
   21. **o resultado:** a regra fica com a palma a −62,5 mm, a inclinação de −12,5° e a guinada de 20°, o polegar com o
       `lado` a 30° e o `peso` 4. Pelo lançador (`npm run blender -- provar lateral`: a pega da regra e as seis
       vizinhas, com a altura, a inclinação e a guinada a ±5), a da regra aprovada — a palma encostada (0,0 mm) 26,3 mm
       antes da âncora, as quatro polpas a −0,05 a 0,0 mm da arma, as falanges médias a 22,5°, 0°, 0° e 0° da face,
       nenhum dedo à direita, o dorso a 23,5° da normal da face, o polegar encostado (−0,07 mm) na quina de baixo
       (67,5°), a distal dele a 63° da frente (0,455; −0,429; 0,780), a luva entrando 0,07 mm na arma e o dorso a 56,2°
       da câmera do jogador (contra 75,7° da pega sem guinada); 22 s de solver por pega. Das vizinhas passam a −57,5 mm,
       a −17,5°, a −7,5° (a distal vira para o lado, a 99,6°) e as guinadas de 15° e 25°; reprova a −67,5 mm (o médio
       deita por cima da peça, 67,5°). No fim, com o código final, a pega da regra de novo: nenhum problema;
  - **revisão crítica das vistas (`conferencia/lateral/-62_-12_+0_30_+20/`):** da câmera do jogador, o dorso de frente —
    o protetor dos nós e as placas dos dedos à vista, os dedos subindo pela face e enganchando na borda de cima, o punho
    embaixo — e o polegar escondido pela peça; aparece só a membrana entre ele e o indicador, uma cunha lisa embaixo da
    peça (a "tenda" da Tarefa 11, mais curta aqui). De fora, os quatro dedos sobem pela face um pouco abertos em leque
    (as frestas entre o indicador e o médio e entre o anelar e o mínimo; os pares passam no `juntosMM`), com as pontas
    por cima da borda e a mão de três quartos pela guinada. De cima, as quatro pontas enganchadas na face de cima e a
    ponta do polegar além da face direita. De baixo, o punho na frente cobre quase todo o polegar (a vista é pouco útil
    para ele). Para a AWP de verdade (Tarefa 13), na câmera do CS2 e de perto: a ponta do polegar além da face direita
    (na inspeção ela pode aparecer), a cunha da membrana e o leque dos dedos;
  - **a suíte:** 604/604 (as 600 de antes e as 4 da lateral; a do fim com o limite de 70° do polegar); o `provar
    lateral` pelo lançador aprovado (6 das 7 pegas). O hash de todas as armas mudou com os scripts da pega (como na
    Tarefa 11: a AWP, a Nova e a P90 são construídas com a pega nas Tarefas 13 a 15, e as quatro da 4.1c na 16).
