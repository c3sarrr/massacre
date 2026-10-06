- **Tarefa 11 (2026-10-05):** o polegar pelo furo — o solver (`empunhadura_furo.py`: o `Furo`, a `medir`, os `problemas`
  e o `passar`), o ramo `furo` da pega (`empunhadura_pega._pegar`, com os furos da ficha em `furos_da_regra` e o furo no
  registro da mão; a nova chegada da palma com a CMC da solução pelo `PolegarCruza`, como a do polegar deitado), a
  medida na validação (`empunhadura_validacao.conferir_mao`: o `polegarNoFuro` na malha afundada), o Node
  (`saidaPega.mjs`: `problemasDoPolegarNoFuro`; `src/data/luvas.js`: `POLEGAR_NO_FURO_DA_CATEGORIA` = `{sniper: 'd',
  smgBullpup: 'd'}` e `furoFolgaMM` 0,3 em `LIMITES_DA_PEGA`) e o formato da regra no cabeçalho de
  `empunhadura_regras.py` (`polegar: {'furo', 'saida', 'eixo'}`).
  - **o formato, diferente do D6 em dois pontos:** a regra do furo leva o `eixo` (para onde a distal aponta, deitada na
    face de saída) no lugar do `deitado: True` — com ele, a validação do polegar deitado da mão da frente (a curva até
    20°, as duas falanges coladas) entraria no polegar que dobra para atravessar a peça; e o `dentro` é o do primeiro
    parágrafo do D6 e da seção 3.2 do desenho (a proximal dentro do prisma e a distal do lado da saída), não "a polpa e
    a proximal dentro do prisma" — a polpa fica do outro lado, na face de saída, e o contato dela é o da polpa do
    polegar da validação (até 1 mm);
  - **os testes (`pegaFuro.test.js`):** aprova `dentro`, a folga de 0,3 e o lado errado 0, na `sniper` e na
    `smgBullpup`; reprova `dentro: false`, a folga de 0,2, o lado errado de 0,1 e o braço sem o `polegarNoFuro` (ou com
    um campo faltando) na categoria que pede; a `escopeta` e a mão esquerda não pedem; a penetração continua valendo.
    Viram falhar pelo import (`POLEGAR_NO_FURO_DA_CATEGORIA` não existia). **Adiantado da Tarefa 12:**
    `MAOS_DA_CATEGORIA` das três com `['d', 'e']` — o `validarPega` confere as mãos do relatório contra as da categoria,
    e sem elas o teste do furo reprovava pelas mãos; o teste da 4.1c (`pegaUmaMao.test.js`) passou a listar as seis;
  - **a prova (`npm run blender -- provar furo`, `provas_furo.py`):** pelo mesmo caminho da pega das armas — a regra
    sintética `PROVA` no `_uma_mao` (a base da `rifle`, a âncora no soquete, nenhum dedo fechando), o afundamento da
    palma e a `conferir_mao` inteira (a penetração, os contatos da palma e da polpa, a luva sem se atravessar nem
    afinar, os ângulos e o `polegarNoFuro`). Os achados, na ordem:
    1. **a placa e o furo do plano não servem:** o furo de 30 × 22 mm não passa o polegar da luva (a seção da falange
       proximal tem 11,4 a 13,1 mm de raio: 22,8 mm de largura no mínimo, mais 0,3 de folga de cada lado), e na placa de
       20 mm, com a palma espalmada na face, a MCP do polegar (14 mm à frente da palma no repouso) ficava a 2,5 mm da
       face de saída: a proximal (31,6 mm) saía inteira do outro lado. As peças de verdade, medidas na malha de jogo
       pela conta do solver (`ferramentas-4.1d/t11/faces_dos_furos.py`): a coronha da AWP em volta do buraco do polegar
       tem 34 mm no punho (a borda da frente, onde o polegar cruza) e 52 em cima e atrás; o quadro da P90 em volta do
       oval de trás, 39,5 a 42,5. A prova passou a uma placa de **34 mm** com um furo de **50 × 40 mm** (cantos de 10
       mm), mais justo que os dois de verdade (59,9 × 50,0 na AWP, 69,0 × 45,5 na P90), com a MCP de repouso no meio do
       furo, 14 mm acima da borda de baixo — a membrana no alto de trás do punho, o meio da borda de baixo do buraco da
       AWP;
    2. **a luva quebrada pela placa:** `KeyError: 'indicador_1'` na cadeia do polegar — a placa nascia na coleção da
       luva, e o `pecas.finalizar` põe na ordem canônica toda malha da coleção: a luva reordenada perdia o modelo das
       correções. A placa ganhou a coleção dela;
    3. **o custo da curva:** com o do polegar deitado (0,6 mm por grau da MCP mais a IP além de 12°), a IP ficava em
       11,5° e a distal saía a 43° do eixo, 4 a 15 mm longe da face. O polegar que atravessa a peça e deita do outro
       lado dobra o que a geometria pede: sem custo de curva no furo;
    4. **a chegada da palma:** na pose de pegar (a abdução palmar no máximo), a tenar encostava na face 18 mm antes da
       palma (a palma a 1,98 mm da placa), a MCP ficava 9 mm fora da placa e o polegar não alcançava a face de saída (a
       distal parada dentro do furo, a polpa a 5,9 mm de tudo). A regra da prova chega com o polegar afastado no plano
       da palma (`polegar_afastado`, como a de apoio da pistola), e o furo usa a mesma nova chegada do polegar deitado:
       a pose que ainda cruza a arma ou a mão levanta `PolegarCruza` com os graus dela, e a palma chega de novo com a
       CMC deles (na segunda chegada a busca parte da solução, e a grade só entra se ela não passar);
    5. **a folga medida na tenar:** na malha afundada, a pele da tenar que cede contra a borda (a membrana em cima do
       punho, como a palma nele) ficava a 0,00 mm da borda e reprovava. A folga é das falanges livres (a proximal e a
       distal), como no refino do solver; o lado errado continua com a tenar;
    6. **o resultado:** a palma andou 8,0 mm além da âncora e encostou (0,00 mm; afunda 1,45 mm, 264 vértices); a MCP
       posada no meio do furo, 9,3 mm dentro da placa; o polegar com a abdução de 43,8° (o repouso é 40), a CMC em
       −7,1°, a rotação dela em 17° (o limite), a MCP em 2,5°, a IP em 52,1° e o desvio da MCP em −19,0° (o limite é −20
       com ela reta); **dentro, a folga de 0,60 mm e nada do lado errado**; a luva sem penetração (0,00 mm); a polpa a
       0,03 mm da face de saída, a distal encostada no meio (os trechos a 1,67, 0,03 e 3,05 mm), a curva de 54,6°; 284 s
       (a pega com as chegadas). **A distal fica a 46,5° do eixo:** com o peso do eixo quatro vezes maior (80 mm por
       unidade, `ferramentas-4.1d/t11/gera_explora_eixo.py`), 44,8° — não é o peso, é a anatomia nessa orientação da
       mão: com a palma espalmada na face e os dedos para a frente, a rotação da CMC e o desvio da MCP chegam ao limite
       e a polpa ainda não fica de frente para a boca, e a IP dobra a distal para a frente e para baixo. A orientação da
       mão (as giradas e a diagonal) é das varreduras das Tarefas 13 e 15, contra os quadros do CS2 — a P90 pede o
       polegar deitado ao longo do quadro;
  - **revisão crítica das vistas (`conferencia/furo/`):** de saída, o polegar passa pelo furo sem raspar e encosta na
    face, mas dobrado uns 50° em vez de deitado ao longo dela (o achado 6); atrás dele, dentro do furo, a pele da
    membrana esticada. De entrada, a membrana entre o polegar e o indicador sobe para o furo numa **"tenda" de pele
    afiada** (o skin da luva com o polegar atravessando a frente da palma): passa na validação da luva (sem se
    atravessar e sem afinar), mas fica estranha de perto — a conferir nas vistas de perto da AWP e da P90 (Tarefas 13 e
    15), na pose de verdade, e corrigir lá se aparecer. De cima, a distal sai da face a uns 45°;
  - **a suíte:** 600/600 (as 596 de antes e as 4 do furo); o `provar furo` pelo lançador aprovado. O hash de todas as
    armas mudou com os scripts da pega (como esperado: a AWP, a Nova e a P90 são construídas com a pega nas Tarefas 13 a
    15, e as quatro da 4.1c na 16).
