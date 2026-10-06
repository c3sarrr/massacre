# Ferramentas da 4.1d (sessões de 2026-10-03 a 2026-10-05: as Tarefas 8 a 16, a P1 e as correções C1, C2 e C4)

Scripts de apoio que ficaram fora do projeto (nada daqui entra no `trabalho-4.1d` nem no plano executado). Os de
Blender rodam com `S:\blender.exe -b --factory-startup -P <script> -- <args>`; os `pnp_*` são Python comum (numpy) e
precisam ser rodados **de dentro desta pasta** (eles se chamam por `runpy.run_path('pnp_icone_p90.py')`).

## A pose do ícone do CS2 e a volta ao plano de lado

- `p90_pontos.py` (Blender): os pontos do modelo da P90 (mm da ficha; x a boca, y o alto, z o lado, + esquerda) para o
  ajuste.
- `pnp_icone_p90.py` (e `pnp_icone.py` da AWP, `pnp_icone_nova.py` da Nova): a câmera de furo ajustada por
  Levenberg-Marquardt aos pontos marcados à mão no ícone do inventário do CS2 (512 × 384). Os pixels do ícone são lidos
  **no navegador** (a página `icone_comparar.html` / `ver_imagem.html` com `mira=1`), nunca gravados.
- `pnp_icone_dict.py`: a câmera ajustada no formato do `ICONE` do script da arma (`frente`, `cima`, `lente`, `distancia`,
  `mira`, `comprimento`, `quadro`).
- `pnp_marcas.py`: projeta pontos do modelo pela câmera (para conferir as marcas no navegador).
- `pnp_volta.py` / `pnp_volta2.py`: a volta de um pixel do ícone ao plano de lado (o plano Y = lado do Blender) pela
  câmera ajustada: (x, alto) em mm da ficha. Foi com ela que a ponte do CS2 saiu ~18 mm mais baixa que a da TR real (o
  topo do trilho a 75,7 mm; os dentes do trilho voltam numa reta a 75,5–75,9).
- `p90_camera_34.py` (+ `.npy`): a câmera da foto de três quartos da FN (CC BY 2.0), ajustada a pontos da ficha.

## Conferência e diagnóstico

- `icone_comparar.html` e `ver_imagem.html` (cópias das de `trabalho-4.1d/tools/blender/conferencia/`, que é
  git-ignorada; servidas pelo `massacre-trabalho` na 5176): o ícone × o render da pose do ícone (`?render=p90%2Ficone.png
  &icone=<url>&largura=512&so=0..3&zoom=3&cx=..&cy=..`) e uma imagem ampliada em volta de um ponto (`?url=..&zoom=..&cx=..
  &cy=..&mira=1`).
- `folha_p1.py <arma> <lado|lado_esquerdo>`: a folha da conferência (lado, três quartos, ícone, perto) em
  `conferencia/<arma>/folha_p1.png`.
- `recorte.py <png> x0 y0 x1 y1 escala <saida>`: recorta e amplia um PNG.
- `arma_previa.py <arma>`: a pré-construção só no nível de jogo (malha, triângulos, silhueta, medidas, fins de curso) em
  minutos, sem assar.
- `arma_alto_abertas.py <arma>`: as arestas abertas do modelo alto peça a peça (o `construir` só confere o de jogo) e,
  desde a Tarefa 16, as dobras de cada peça (`armas/dobras.py` na forma canônica com a grade de 1 µm).
- `chanfro_clamp_global.py <arma> <alto|jogo>` (e `chanfro_clamp.py`): as peças com o chanfro reduzido pelo "clamp
  overlap" GLOBAL do Blender (a mesma pilha avaliada com e sem o clamp). Na Tarefa 16 (a correção C4), nos dois
  níveis: a AK 37 e 34 peças, a Glock 20 e 15, a faca 3 e 3, a M4A4 34 e 29 (os logs na pasta de rascunho da sessão).
- `quadro_teste.py <rotulo>` e `abertura_teste.py`: só o quadro da P90 nos dois níveis (malha, cruzamentos, closes) e as
  folgas da abertura da frente em volta do gatilho e do seletor.
- `peso_textura.py`, `ver_textura.py`, `margem_teste.py`: onde pesa a textura assada e o teste da margem das ilhas de UV
  (a margem por repetição do texel da borda, hoje no `assar._estender`).
- `registro_t10_rascunho.md`: o rascunho do registro da Tarefa 10 (já copiado no plano).

## A correção C1 (2026-10-05): a parte de cima da P90 do CS2 (`c1/`)

Duas fontes do jogo, só lidas no navegador (nada do jogo gravado; só números): o ícone do inventário (o mesmo das
peles: `P90_Wash_me.png`, IoU 1,0000 com o do inventário) e o quadro de 108,6 s do vídeo de inspeção
(`y1NSHUq7WOI`, a aba do YouTube com o quadro parado e os auxiliares `window.__desenhar`, `__proj`, `__plano`, `__tri`
e `__linhas`, que desenham o quadro ampliado com as linhas do modelo por cima num canvas da própria aba).

- `cameras.py` (`cameras.json`) e `ajuste_conjunto.py` (`conjunto.json`, `cameras_conjunto.json`): as duas câmeras de furo
  ajustadas juntas (Levenberg-Marquardt), os nove parafusos da face esquerda presos nas posições da ficha e os pontos de
  cima livres (triangulados): 1,04 px no ícone e 1,88 no vídeo. A `p90.ICONE` sai daqui. `pnp_*`, `focal_curva.py` e
  `epipolar.py` são os passos do caminho (os PnP de cada imagem, a ambiguidade focal × distância, as retas epipolares
  para achar o mesmo canto na outra imagem).
- `volta.py`: a volta de um pixel ao plano de um lado e a triangulação dos raios das duas imagens (as mesmas contas dos
  `__plano` e `__tri` da aba do vídeo).
- `contornos_cima.py` (lê os perfis de cima das duas imagens, `topo_icone.json` e `topo_video.json`, tirados no navegador
  para a medida e apagados depois dela: para usar de novo, ler outra vez os perfis no navegador), `linhas.py`,
  `candidato.py` + `sobrepor.py`: os contornos de cima nas duas fontes e o candidato
  da parte de cima projetado nelas (em `tools/blender/conferencia/p90/cand_icone.json` e `cand_video.json`, a grade.html
  com `dados=` no ícone e o `__linhas` na aba do vídeo).
- `ficha_c1.py`: escreve a C1 na ficha `p90.json` (o contorno composto, as peças e os pontos de cima, as fontes do jogo
  nas fotos, a caixa de três quartos); `plot_ficha.py` desenha a ficha de antes e a de depois (`ficha_c1.png`). As
  cópias de antes da C1: `p90_antes_c1.json`, `p90_antes_c1.py`, `p90_cima_antes_c1.py`.
- `conferir_miras.py`: as miras da ficha (as bases, as orelhas, os botões, os parafusos e os furos da orelha)
  projetadas nas duas imagens (`conf_icone.json`, `conf_video.json`), para conferir os pontos de perto — foi por ela que
  os botões e os parafusos das miras saíram do lugar na pose do ícone e foram triangulados de novo.
- `tres_quartos_antes.py <blend> <ficha> <saida>`: a conta de três quartos de uma .blend guardada com a ficha que se
  pedir (o modelo de antes da C1 com a caixa nova, para separar o que a C1 mudou do que já estava lá).
- `exportar_modelo.py`: os triângulos do perto de uma arma no referencial da ficha (para os ajustes no navegador).

## A correção C2 (2026-10-05): o carregador curto da AWP em fileira dupla (`c2/`)

Duas fontes do jogo, só lidas no navegador (nada do jogo gravado; só números): o modelo do CS2 no visualizador 3D do
VSkin (`https://vskin.gg/skin-viewer?def=9&paint=279&seed=1&float=0`, a pele Asiimov: o carregador branco e a placa de
fundo laranja) e o ícone do inventário (`CS2_AWP_Inventory.png`). No VSkin o visualizador é um iframe de outro domínio
(render.vskin.gg): o truque é pôr o iframe `position: fixed` com 2400 × 2160 ou 4800 × 4320 px CSS e deslocamento
negativo — o WebGL refaz o render na resolução maior (9600 apaga a arma). A escala sai do comprimento total (a ponta do
freio e o fim da soleira: 1,5001 px/mm em 2400, 3,0002 em 4800; o pixel da captura é 1,1561 do CSS). Nunca usar o botão
"Take a screenshot" do site (ele baixa um arquivo). No vídeo do Tigerfield (`boSwnyDyezU`), a recarga da AWP vai de
513,4 a 514,3 s (o quadro de 514,27 s mostra o carregador entrando logo à frente do guarda-mato).

- `linhas_icone.py <saida.json> [<extra.json>]`: o contorno da ficha (lado ±30), os buracos (±9/±17) e a peça do
  carregador (±12) projetados pela câmera do ícone (`conferir.ICONE`) em pixels do ícone, para a `grade.html` com
  `dados=` (em `tools/blender/conferencia/awp/linhas_icone.json`); `proj(x, alto, lado)` projeta um ponto.
- `ficha_c2.py` (com o Python do Blender, `S:\5.2\python\bin\python.exe`: o do sistema é o 3.7): escreve a C2 na ficha
  `awp.json` — a largura de 28 mm, `pontos.carregador` (a parte à vista, a frente escondida, o recuo dela, o topo, as
  paredes, a placa e os centros dos cinco calculados: o de cima a 0,05 mm do ferrolho fechado, os outros encostados na
  parede e no da outra fila), o pivô do retém e as duas fontes do jogo nas `fotos`. A cópia de antes: `awp_antes_c2.json`.
- A conta da fileira dupla (o desencontro, o passo, o de cima contra o ferrolho, os lábios concêntricos com o aro, o fundo
  rente à coronha pelo perfil suave dela) foi conferida fora do Blender com `contornos.py` do projeto (o perfil suave da
  coronha é `awp.perfil_suave`, puro Python).
- `coronha_cortes.py` (`S:\blender.exe -b --factory-startup -P coronha_cortes.py -- [alto|jogo]`): os defeitos dos
  cortes da coronha da AWP num nível — as arestas não manifold e as colisões novas, antes e depois dos cortes finais,
  com cada solucionador, e onde ficam (mm da ficha); os pesos do chanfro nas caixas das bocas. Foi o que mostrou que o
  poço e o vão do retém cortados depois do chanfro estragavam a coronha alta longe do corte (o achado 3 da C2) e conferiu
  o teto do chanfro (`pecas.limitar_chanfro`): zero e zero nos dois níveis.
- `carregador_closes.py` (`S:\blender.exe -b <trabalho-4.1d>\tools\blender\conferencia\awp\awp.blend --factory-startup
  -P carregador_closes.py [-- <vista> ...]`): os closes do carregador no modelo alto da .blend do construir — na arma de
  lado e por baixo (a frente escondida rente, o retém), só o carregador de lado, da direita, de cima, de cima de perto e
  de três quartos por baixo; as vistas de baixo com uma luz de área por baixo (o estúdio só ilumina de cima). Saem em
  `tools/blender/conferencia/awp/c2_*.png`.
- `icone_mascara.py` (`S:\blender.exe -b <...>\awp.blend --factory-startup -P icone_mascara.py`): a máscara do nosso
  modelo na pose do ícone (a câmera `ICONE` do conferir, 1600 × 1200), em Workbench chapado com o fundo transparente,
  o carregador em vermelho e o resto em branco (`conferencia/awp/c2_icone_mascara.png`). Só o nosso modelo.
- `icone_bordas.py` (`python icone_bordas.py`): as bordas da máscara em pixels do ícone (o alfa e o vermelho do
  carregador, nas linhas e colunas da conferência) e a luminância do render `icone` na altura do carregador. O lado do
  ícone sai no navegador, na `grade.html` com o ícone (`?url=<ícone>`), no console: `__bordas(u0, v, u1, v)`,
  `__bordas(u, v0, u, v1)` e `__perfil(...)` nas mesmas linhas — números, sem captura de tela (a captura do navegador
  fica gravada pelo harness na pasta `tool-results` da sessão: evitar). A `__bordas` da `grade.html` perdia a passagem
  do alfa que caía em cima de uma amostra (borda dura: o bilinear dá 0,5 exato entre dois pixels, e a linha numa
  coordenada inteira amostra ali); corrigida na C2 pela troca do lado, com a posição interpolada (a mesma conta no
  `icone_bordas.py`).
- `registro_c2_rascunho.md`: o rascunho do registro da C2 que foi para o plano.

## A Tarefa 11 (2026-10-05): o polegar pelo furo (`t11/`)

A prova sintética é do projeto (`trabalho-4.1d/tools/blender/armas/provas_furo.py`, `npm run blender -- provar furo`:
pelo caminho real da pega, ~5 min; as vistas em `tools/blender/conferencia/furo/`). Aqui ficam as contas de apoio.

- `faces_dos_furos.py` (`S:\blender.exe -b <trabalho-4.1d>\tools\blender\conferencia\<arma>\<arma>.blend
  --factory-startup -P faces_dos_furos.py -- <arma> <furo>`): as faces da peça em volta de um furo da ficha, na malha de
  jogo (o perto) da .blend do construir, pela conta do solver (`empunhadura_furo.Furo`). A AWP (`buracoPolegar`): 34 mm
  no punho, 52 em cima e atrás; a P90 (`ovalTras`): 39,5 a 42,5 mm.
- `geometria_polegar.py` (`S:\blender.exe -b --factory-startup -P geometria_polegar.py -- <contexto das luvas.json>`,
  o contexto do `contextoLuvas` do lançador: `{id, ficha, pinturas}`): o comprimento dos ossos do polegar (46,2, 31,6 e
  27,3 mm), os limites dos seis graus além do repouso e as juntas, a palma e as falanges no referencial da luva no
  repouso, na pose afastada e na mão aberta da chegada (a MCP 14 mm à frente da palma no repouso).
- `gera_explora_eixo.py`: gera `explora_eixo.py` (na pasta temporária da sessão) a partir da `provas_furo.py`, com o
  `PESO_EIXO_MM` do furo pelo argumento e sem as vistas — com 80 (quatro vezes o de hoje) a distal ficou a 44,8° do eixo
  contra 46,5°: o desvio é da anatomia na orientação da prova, não do peso.
- `registro_t11_rascunho.md`: o rascunho do registro da Tarefa 11 que foi para o plano.

## A Tarefa 12 (2026-10-05): a regra lateral (`t12/`)

A prova do bloco é do projeto (`trabalho-4.1d/tools/blender/armas/provas_lateral.py`,
`npm run blender -- provar lateral [pegas...]`: pelo caminho real da pega, ~25 s de solver e ~2 min das quatro vistas
por pega; as vistas em `tools/blender/conferencia/lateral/<altura>_<inclinação>_<girada>_<polegar>_<guinada>/`). Para
varrer muitas pegas sem o lançador, o Blender direto com a saída num arquivo:
`S:\blender.exe -b --factory-startup --python-exit-code 1 -P tools/blender/armas/provas_lateral.py -- <contexto das
luvas> <pegas...> > <log> 2>&1` (o contexto das luvas é o JSON do `contextoLuvas` do lançador: `{id, ficha, pinturas}`).
Aqui ficam as contas de apoio.

- `explora_polegar_baixo.py` (`S:\blender.exe -b --factory-startup -P explora_polegar_baixo.py -- <contexto das luvas>
  <altura>,<inclinação>,<girada>[,<guinada>] ...`): onde o polegar da mão de apoio consegue encostar por baixo do bloco
  numa pega — a mão chega e fecha os dedos pelo caminho da pega com o polegar parado no afastado, e a grade dos seis
  graus do polegar (3 600 poses: a abdução em 6, a CMC em 4, a rotação em 2, a MCP e a IP em 5, o desvio em 3) é
  varrida; imprime as poses com a polpa a até 3 mm da face de baixo (a normal a até 45° do −Z) que não cruzam a arma nem
  a mão (o `_cruza` do solver), a direção da distal delas e as que cruzam menos. Foi com ela que a concha caiu (2 535
  poses por baixo, todas cruzando) e que a mão chata apareceu (38 a 94 poses limpas). Só leitura: nada gravado.
- `ler_lateral.py <log>`: resume as linhas `MASSACRE-PROVA-LATERAL` de um log da prova (a pega, quanto a palma andou, as
  polpas, as falanges médias, o lado direito, o dorso, o polegar, os contatos, a penetração, o ângulo do dorso com a
  câmera do jogador, a distal do polegar e os problemas).
- `chegada_lateral.py` (`CHEGADA=40 [AFASTADO=0] [PESO=20] S:\blender.exe -b --factory-startup --python-exit-code 1 -P
  chegada_lateral.py -- <contexto das luvas> <pegas...>`): a prova do bloco com outra chegada da palma, com `AFASTADO=0`
  sem o polegar afastado e com `PESO` outro peso do lado do polegar 'baixo', sem as vistas. Nas duas pegas que a regra
  teve, a pega passa sem a chegada de 60 e sem o polegar afastado (ficam de margem); o peso 20 deixa a polpa na mesma
  quina, e o 40 leva o alvo para longe e o polegar fica no ar.
- `p3p_cs2.py` (`python p3p_cs2.py awp`): a pose da câmera do viewmodel do CS2 pelo P3P, com três pontos de tela do
  `cs2.md` (a boca, a objetiva, a bola do ferrolho) e os do nosso modelo — só números. Só acha a arma rolada, de pé (a
  bola da nossa ficha é estimada): a altura dos nós no quadro não sai daqui, e a comparação fica para a P2.
- `onde_polegar.py` (`S:\blender.exe -b --factory-startup -P onde_polegar.py -- <contexto das luvas> <pegas...>`): a
  polpa e a ponta do polegar e as polpas dos dedos na pega da prova, em mm no referencial do bloco, com a distância e a
  normal do bloco embaixo, sem as vistas. Foi com ele que apareceu que o polegar passa por baixo do bloco inteiro: a
  polpa na quina de baixo do lado direito e a ponta no ar, 14 a 16 mm ao lado da face direita.
- `registro_t12_rascunho.md`: o rascunho do registro da Tarefa 12 que foi para o plano.

## A Tarefa 13 (2026-10-05): a AWP na mão (`t13/`)

O banco de prova das duas mãos na AWP de verdade: uma sessão do Blender que fica aberta (a arma e as luvas montadas uma
vez) e executa os trabalhos de uma fila, cada mão resolvida em segundos pelo mesmo caminho da pega do `construir`
(`empunhadura_pega._uma_mao`, o afundamento da palma e a `conferir_mao`). Os arquivos de trabalho (a .blend com as
luvas, os JSON das varreduras e os renders) ficam numa pasta de rascunho (`TRABALHO` em `awp_pega.py`), fora do
projeto; os renders são só do nosso modelo.

- `servidor.py` (`S:\blender.exe -b --factory-startup -P servidor.py -- <raiz do trabalho-4.1d> <pasta da fila>`):
  executa cada `<fila>/*.py` num espaço de nomes que persiste, com a saída em `<nome>.out` e o código em `<nome>.feito`;
  um `.py` com `G['_sair'] = True` encerra. Rodaram três ao mesmo tempo (a mão de apoio e a do gatilho em paralelo;
  nunca durante um `construir`).
- `awp_pega.py`: `preparar()` (a .blend da conferência da AWP com as luvas montadas pelo caminho do construir),
  `carregar(laco)` (o contexto do `_uma_mao`; o furo pelo oval que a coronha corta ou pelo traçado da ficha),
  `mao(lado, correcoes, vistas, nome)` (uma mão com as correções por cima da regra `sniper`: o relatório da mão e as
  contas a mais — as juntas posadas, a distal e a ponta do polegar, o dorso contra a câmera do jogador, as folgas para
  cada peça, a distância das distais ao eixo do cano e o alto de cada dedo; os renders rápidos no Workbench) e
  `resolver(vistas_d, vistas_e, nome)` (a pega inteira pelo `empunhadura_pega.resolver`, com o EMPUNHADURA e os laços
  da arma: o que o `construir` faz).
- `varreduras.py`: as grades das varreduras (a mão de apoio: a altura, a inclinação, a girada no plano da face, a
  guinada e o lado do polegar; a do gatilho: a âncora, a diagonal, a altura do ponto no gatilho, o eixo do polegar e o
  giro da mão; `sem_polegar=True` deixa o polegar no afastado da chegada, para varrer os dedos em 5 s por pega).
- `pseudo_planos.py`: a pseudonormal por planos que foi para `empunhadura_arma.Arma.pseudonormal`, em forma de remendo
  (o `__init__` e a `distancia` da `Arma` trocados na sessão), para comparar com a antiga: nos três pontos da palma
  15,7, 14,1 e 13,7 mm fora da coronha, perto da borda viva do buraco do polegar, a antiga dava dentro e a nova, fora;
  as cinco pegas da mão do gatilho saíram com os mesmos graus.
- `camera_cs2.py` (`python camera_cs2.py`, com o numpy): a câmera do quadro pronto da AWP do CS2 ajustada, com a arma de
  pé, aos três pontos de tela do `cs2.md` (a boca, a objetiva e a bola do ferrolho; só números, nada do jogo gravado),
  por mínimos quadrados, e onde os nós da nossa luva de apoio cairiam nela: o resíduo de 3,4 % da tela e os nós a 4,8 %
  e 2,7 % dos do quadro (o achado 8 do registro).
- `registro_t13_rascunho.md`: o rascunho do registro da Tarefa 13 que foi para o plano.

## A Tarefa 14 (2026-10-05): a Nova na mão (`t14/`)

O banco de prova da Tarefa 13 generalizado para qualquer arma e categoria (a Nova, e a P90 na Tarefa 15), com o mesmo
`t13/servidor.py`. O trabalho entra na fila escrito num `.tmp` e renomeado para `.py` (escrito direto, o servidor o lia
pela metade). Os arquivos de trabalho (a `<arma>_luvas.blend`, os JSON das varreduras e os renders) ficam na pasta de
rascunho da sessão (`B.configurar(arma, categoria, trabalho)`), fora do projeto; os renders são só do nosso modelo.

- `pega_banco.py`: `configurar(arma, categoria, trabalho)`, `preparar()` (a .blend da conferência da arma com as luvas
  montadas pelo caminho do construir), `carregar()` (o contexto do `_uma_mao`, com os furos da regra pelos laços da
  arma), `base_da_prova(base)` (a regra da categoria; sem ela, ou pelo nome, a base de prova — `escopeta_borda`, a Nova
  do desenho com o polegar de apoio na borda de cima, de onde partiram as varreduras dele), `mao(lado, correcoes,
  vistas, nome, base)` (uma mão com as correções por cima da base: o relatório e as contas a mais — a entrada de cada
  osso, a folga para cada peça, a distal e a ponta do polegar, o dorso contra a câmera do jogador, as distais ao eixo
  da peça —; a linha `PROVA`; os renders no Workbench), `no_fim_do_curso()` (o protótipo da conferência da mão que vai
  com a peça: a peça do soquete e a que ela arrasta no fim de cada passo, a luva levada junto) e `resolver(vistas_d,
  vistas_e, nome)` (a pega inteira pelo `empunhadura_pega.resolver`, como o construir).
- `varreduras_nova.py`: as grades da Nova (`direita_dedos_1` a `_3` e `esquerda_dedos_1` e `_2` sem o polegar;
  `direita_polegar_1` a `_5` com o polegar deitado no pescoço; `esquerda_borda_1` e `esquerda_por_cima` com o polegar na
  borda de cima, pela base `escopeta_borda`; `esquerda_baixo_1` e `_2` com o polegar por baixo, a regra); cada pega numa
  linha `RESUMO` e o JSON da varredura em `<trabalho>/<nome>.json`.
- `resumo.py <.out> [campos]` e `prova.py <.out>` (o Python do Blender serve): uma linha por pega das linhas `RESUMO` de
  uma varredura e um bloco por pega das linhas `PROVA` de `mao()`; `esperar.sh <.out> [segundos]`: espera o trabalho
  terminar.
- `registro_t14_rascunho.md`: o rascunho do registro da Tarefa 14 que foi para o plano.

## A Tarefa 15 (2026-10-05): a P90 na mão (`t14/` e `t15/`)

O banco da Tarefa 14 (`t14/pega_banco.py`, com a base de prova `smgBullpup` enquanto a regra não existia) com a mão do
gatilho resolvida no servidor antes da de apoio (`B.mao('d', V.GATILHO)` fica em `C['feitas']` e entra de obstáculo na
de apoio, que tem `luva`), e os renders das duas luvas juntas (a outra na cor dela). O processo em segundo plano vive
2 h: as varreduras gravam cada pega no `<trabalho>/<nome>.progresso` assim que ela sai, e as longas vão em partes
(`parte`, `partes`: um servidor cada). Um servidor carrega os scripts das armas uma vez: depois de mudar o solver, suba
servidores novos (o `importlib.reload` do trabalho só recarrega a varredura).

- `t14/varreduras_p90.py`: as grades da P90 — a mão do gatilho (`direita_dedos_1` a `_10`, sem o polegar; `GATILHO`, a
  escolhida, a C), a de apoio (`esquerda_1`, com o polegar, a que caiu no limite de 2 h; `esquerda_dedos_1` a `_5`, sem
  o polegar — o `sem_polegar` também para o 'baixo'; `APOIO_DEDOS_LIMPOS`, as 36 que passam nos dedos) e o polegar de
  apoio (`esquerda_polegar_1` e `_2`, com o alvo na arma e na luva do gatilho; `esquerda_polegar_na_arma` e `_todas`,
  com o alvo só na arma — a prova do que foi para o `empunhadura_pega._pegar`).
- `t14/resumo_p90e.py <JSON ou .progresso>... [--com-polegar] [--so-boas]`: uma linha por pega da mão de apoio (as
  polpas, as falanges médias, o dedo à direita, o dorso, a palma, os dedos lado a lado, a luva com a luva).
- `t15/` (o que rodou da pasta de rascunho da sessão; os caminhos dentro deles são os dela): `novo_trabalho.sh <n da
  fila> <nome> <código>` (o trabalho na fila pela renomeação, com o `pega_banco` e o `varreduras_p90` importados),
  `diag_atravessa.py` (os pares da luva que se atravessam na última pega do servidor, pelo osso de cada triângulo, com
  e sem o afundamento), `diag_tenar2.py` (a dobra da tenar com cada junta de volta ao repouso: só a CMC a faz),
  `diag_tenar3.py` (o mapa da dobra pela abdução e pela flexão da CMC), `prova_tenar.py` (a dobra medida só no refino:
  não sai), `prova_tenar2.py` (a tabela na busca global e a medida no refino: o que foi para o `empunhadura_polegar`),
  `grade_fina.py` (as pegas da mão de apoio com o código definitivo), `curto_ept.py <pasta> <padrão>` e `curto_epb.py`
  (uma linha por pega: os problemas, o lugar e o contato do polegar, a dobra e os graus da CMC) e `registro_t15.md`, o
  rascunho do registro que foi para o plano.

## A Tarefa 16 (2026-10-05): as quatro da 4.1c com o chanfro local e as dobras (`t16/`)

O chanfro local (`pecas.chanfro_local()`) nas quatro da 4.1c (a correção C4) e o detector de dobras
(`trabalho-4.1d/tools/blender/armas/dobras.py`) no desdobrar do chanfro e na validação. Todos são de Blender e leem a
`.blend` da conferência (`tools/blender/conferencia/<arma>/<arma>.blend`: as coleções `jogo`, `alto` e `perto`) ou
constroem a arma como o `construir` faz (sem gravar nada no projeto). As coordenadas são mm da arma no referencial do
Blender (+Y é a esquerda).

- Os defeitos de uma peça:
  - `varrer_dobras.py <arma> [--alto]`: as dobras de todas as peças do nível de jogo (e do alto) e os triângulos virados
    da `perto_base`, por tipo; `opostas.py <arma> [--sem-alto]`: a população dos pares quase opostos e dos polígonos
    virados por faixa de graus (a escolha do limite das faces viradas, `dobras.OPOSTO`);
  - `fresta.py <arma> <peça> <x> <y> <z> [raio] [cosseno]`: os pares de polígonos quase opostos em volta de um ponto,
    com o tipo (cunha, fresta, misto), as normais e os cantos; `poligonos_canto.py`: os polígonos em volta de um ponto,
    a planaridade e a triangulação BEAUTY de cada um (a da junção) contra os triângulos da `perto_base`;
  - `dobras_peca.py <arma> <nível> <peça>...` (+ `ler_dobras.py <log>`): os triângulos que se cortam em cada etapa do
    acabamento; `faces_perto.py <arma> <nível> <x> <y> <z> [--todas]`: as faces a até 2 mm de um ponto e se apontam
    para fora; `abertas_peca.py <arma> <peça>`: as arestas abertas de uma peça e os polígonos em volta;
    `diag_escondidas.py <arma> <x> <y> <z> [raio]`: as faces da `base` do perto em volta de um ponto, de que peça vêm
    e se a junção as tira por estarem dentro de outra;
  - `agulha.py <arma> <nível> <peça> <x> <y> <z> [raio] [--cortes]`: os polígonos em volta de um ponto na saída dos
    cortes de antes do chanfro e o corte que faz a dobra; `armacao_pilha.py <arma> <nível> <peça>`: onde a malha abre
    na preparação do chanfro local (achou as faces em buraco de fechadura da armação da Glock,
    `chanfro_local._abrir_fechaduras`); `dobra_grade.py <arma> <nível> <peça>... [--cru] [--sem-finais]`: as dobras
    sem a grade e na forma canônica (se a dobra nasce do arredondamento à grade);
  - `canto_pesos.py <arma> <nível> <peça> <x> <y> <z> [raio]`: a entrada do chanfro em volta de um ponto (os pesos, a
    largura, o ângulo entre as faces) e a saída dele ali.
- O chanfro e o desdobrar:
  - `experimento_deslize.py <arma> <nível> [--sem-deslize] [--sem-chanfro] [--global] [--velho]`: a arma construída e
    as dobras de cada peça no fim (o `TOTAL` é o que a validação conta), com o "Loop Slide" desligado, sem o chanfro,
    com o limite global da 4.1c ou com o desdobrar de antes da correção;
  - `perdas.py <arma> <nível> [--despejo <pasta>] [--sem-espelho]`: em cada peça do chanfro local, o chanfro pedido, o
    do limite local e o que ficou depois do desdobrar (a largura vezes o comprimento), os defeitos do começo por tipo e
    os lugares em que o chanfro caiu; com `--despejo`, um JSON por peça (as arestas e os defeitos), que `causa.py
    <json> [raio]` (os defeitos em volta das arestas que mais perderam: quase sempre nas pontas, as quinas) e
    `assimetria.py <pasta>` (a diferença entre os dois lados da arma, pela largura vezes o comprimento) leem (Python
    comum, com numpy);
  - `clamp_vivo.py <arma> <nível>`: se o limite global do Blender ainda age em alguma peça do chanfro local (a malha com
    e sem o "clamp overlap"): em nenhuma das sete;
  - `chanfro_v2.py <arma> <nível> [--sem-clamp] [--trechos] [--trecho <mm>] [--largura-minima <mm>] [--curtas [vezes]]
    [--despejo <pasta>]`: o protótipo das três ideias para tirar menos chanfro — o limite global desligado com as
    arestas alinhadas de pesos diferentes, a aresta longa dividida em pedaços em volta do defeito (a redução só no
    trecho, com a rampa do gradiente) e as arestas curtas primeiro (a que foi para o `chanfro_local.desdobrar`, com a
    redução espelhada) —, com o perto juntado como o construir para o orçamento de triângulos; `taper.py <pasta>`: a
    barra de prova do chanfro com a aresta dividida (em degrau e em rampa); `vistas_blend.py <.blend> <vistas.json>
    <pasta> <rótulo>`: vistas de perto das `.blend` do protótipo (`--despejo`).
- O antes e o depois:
  - `pega_json.py <arma> <saída.json>` e `pega_json.py --comparar <antes.json> <depois.json>`: a pega do `.glb` (a
    rotação de cada osso de dedo no clipe `empunhadura`, o referencial de cada mão, as flexões e os graus do polegar)
    e quanto cada osso mudou; `comparar_relatorio.py <antes> <depois>`: os relatórios (silhueta, triângulos,
    arquivos, medidas, problemas, contatos da pega);
  - `antes_depois.py <antes.glb> <depois.glb> <pasta> <vistas.json> <origem x> <origem y>`: as mesmas vistas do nível
    perto das duas versões no Workbench;
  - `diag_entra.py <arma> <categoria> <d|e> <pasta>` (e `diag_ak_entra.py`): os vértices da luva que a distância com
    sinal dá dentro da arma, pela `.blend` de um construir reprovado (o banco da Tarefa 14).
- As pegas de novo (as reprovações da terceira volta do `construir todas`; todos pelo banco da Tarefa 14 sobre uma
  `.blend` da conferência com as luvas montadas — a do construir, ou a cópia de antes, a `.blend1` —, com o código da
  pega de agora):
  - `diag_chegada.py <arma> <categoria> <d|e> <.blend> <pasta>`: em cada chegada da palma (`encostar`), os vértices do
    corpo da luva que encostam primeiro (o osso, a peça, o ponto e a normal) e, no fim, os vértices da palma mais perto
    da arma — achou a segunda chegada da AK (a palma 16,4 mm antes do ponto de chegada, com a tenar no punho);
  - `diag_polegar.py <arma> <categoria> <d|e> <.blend> <pasta> [--outros <json>]`: o alvo do polegar que dá a volta, as
    três partes do `_cruza` na solução da IK e com a MCP e a IP abertas (a mão, a dobra da tenar, a arma) e o custo da
    IK (as cápsulas e o refino pela malha) na solução e em graus de outra `.blend`;
  - `diag_partidas.py <arma> <categoria> <d|e|d,e> <.blend> <pasta> [--n 6] [--distancia 20] [--completa]`: em cada IK
    do polegar com a arma, a solução do solver e as `n` melhores partidas da grade levadas pela busca e pelo refino,
    com o custo e o `_cruza` de cada uma — a escolha do `empunhadura_polegar._outra_partida`;
  - `diag_indexado.py <arma> <categoria> <.blend> <pasta> [--outros <json>]`: o custo do indicador indexado da pistola
    separado por termo (a folga, a face, a arma, o ferrolho, o gatilho, a altura, o eixo, a curva) na solução e em
    outros graus, com a face mais perto de cada ponto do eixo do dedo; `diag_acima.py <arma> <categoria> <.blend>
    <pasta> <margens>`: a pega inteira com a margem da busca acima do gatilho em cada valor (a
    `empunhadura_dedo.ACIMA_MARGEM_MM`);
  - `diag_lateral.py <arma> <categoria> <.blend> <pasta> [--direita]`: a medida da mão lateral — por dedo, o vértice
    da falange média mais perto, a face que a BVH devolve, a pseudonormal e as faces a até 1 mm; a medida pelo eixo
    do osso (a de agora, `empunhadura_lateral._em_volta`) e o lugar do polegar pelos dois jeitos — achou as quinas em
    que a medida antiga trocava de face conforme a ordem da malha (a Nova e a P90);
  - `diag_resolver.py <arma> <categoria> <.blend> <pasta> <rótulo>`: a pega inteira (o `resolver`, como no construir)
    e o resumo de cada mão, para conferir uma mudança do solver nas sete sem construir (o `resumo_res.py` da pasta de
    rascunho da sessão lê os logs);
  - `varrer_polegar_baixo.py <arma> <categoria> <.blend> <pasta> <variantes.json> [--direita]`: a mão de apoio com o
    `polegar` (o `lado` e o `peso`), a âncora ou as giradas de cada variante, e o lugar do polegar pela medida nova.
