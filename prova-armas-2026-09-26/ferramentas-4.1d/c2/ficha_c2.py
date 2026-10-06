# A correção C2 na ficha da AWP (plano da 4.1d, P1): o carregador curto do jogo em fileira dupla. Escreve em
# tools/blender/refs/awp.json:
#  - vistaDeCima.larguras.carregador: 28 mm (a fileira dupla da carga militar de .338 Lapua Magnum: a conta abaixo);
#  - pontos.carregador: a parte à vista (a peça da vista), a frente escondida na coronha (rente ao fundo dela), as
#    paredes, o topo e os centros dos cinco cartuchos desencontrados (3 + 2), calculados aqui;
#  - pontos.travaCarregador: o pivô do retém na frente do guarda-mato (o lugar do manual da AW e da faixa da vista);
#  - as duas fontes do CS2 do carregador nas fotos (o modelo no visualizador 3D e o ícone), só números;
#  - a nota da C2.
# Rodar uma vez sobre a ficha de antes (a cópia awp_antes_c2.json fica ao lado); rodar de novo reescreve os mesmos
# valores (idempotente). Com o Python do Blender (o do sistema é o 3.7):
#   S:\5.2\python\bin\python.exe ficha_c2.py
import json
import math
import os
import shutil
import sys

sys.stdout.reconfigure(encoding='utf-8')
AQUI = os.path.dirname(os.path.abspath(__file__))
FICHA = r'C:/Users/T-Gamer/Desktop/game tiro/trabalho-4.1d/tools/blender/refs/awp.json'
ANTES = os.path.join(AQUI, 'awp_antes_c2.json')
if not os.path.exists(ANTES):
    shutil.copyfile(FICHA, ANTES)
f = json.load(open(FICHA, encoding='utf-8'))

LICENCA = '© Valve Corporation — só referência visual, lida no navegador, nada guardado'
AUTOR = 'Valve Corporation (modelo do jogo)'

# ------------------------------------------------------------------------------------------------ a fileira dupla
LARGURA = 28.0  # o corpo de aço por fora (o "~28 mm" da C2)
PAREDE = 0.8
R_ARO = 14.93 / 2  # o aro do .338 Lapua Magnum (C.I.P.): os cartuchos se tocam e tocam as paredes pelo aro
R_FERROLHO = f['pontos']['ferrolho']['raio']
MEIO = LARGURA / 2 - PAREDE - R_ARO  # o centro de cada fila a 5,735 mm do meio
PASSO = math.sqrt((2 * R_ARO) ** 2 - (2 * MEIO) ** 2)  # a altura entre um cartucho e o da outra fila: 9,557
# o de cima encostado embaixo do ferrolho fechado (o aro a 0,05 mm do corpo do ferrolho, Ø 20, no eixo do cano), como
# na arma com o ferrolho fechado: o ferrolho aperta a pilha para baixo. Os lábios seguram o de cima nessa mesma altura
# (o perfil está em awp_acao.py); na arma real ele sobe uns 2 mm aos lábios quando o ferrolho recua, e o ferrolho pega o
# culote por essa sobreposição — a peça rígida do carregador não mostra a subida
Z_DE_CIMA = -math.sqrt((R_FERROLHO + R_ARO + 0.05) ** 2 - MEIO ** 2)
centros = [[round(MEIO if i % 2 == 0 else -MEIO, 3), round(Z_DE_CIMA - i * PASSO, 3)] for i in range(5)]
# a parte à vista: a peça `carregador` da vista (a traseira a −828,5/−829,5, a frente a −753,9); a frente escondida por
# dentro da coronha: 91,7 mm por dentro (a carga militar de 91,44 mm, com 0,05 atrás e 0,21 na frente)
X_TRAS, X_FRENTE = -829.2, -753.9
X_FRENTE_ESCONDIDA = round(X_TRAS + PAREDE + 91.7 + PAREDE, 1)  # −735,9
# o fundo da frente escondida rente ao fundo da coronha, 0,3 mm para dentro: o poço é reto e o carregador sai reto para
# baixo (com o fundo da frente acima do fundo da coronha, a coronha embaixo dele o prendia: para sair, ele atravessava
# 6 a 9 mm de plástico)
RECUO_DA_FRENTE = 0.3
# as duas fendas de cada lado pelo modelo do CS2 no visualizador 3D (4800 px CSS, 3 px/mm): 5,8 mm de largura (±0,6) e
# os centros nas frações do comprimento à vista medidas nas duas leituras (−782,6 e −815,0 no carregador de −760,5 a
# −834,9 e de −760,1 a −836,2: 29,6 % e 72,7 % da frente), postas no nosso de 75,3 mm. A vista do CS:GO (0,98 mm/px) não
# resolve a largura: as fendas dela têm 10 px com as bordas claras
FRACOES_FENDAS = ((782.6 - 760.5) / 74.4 + (782.6 - 760.1) / 76.1) / 2, ((815.0 - 760.5) / 74.4 + (815.0 - 760.1) / 76.1) / 2
FENDAS = {'x': [round(X_FRENTE - fr * (X_FRENTE - X_TRAS), 1) for fr in FRACOES_FENDAS], 'largura': 5.8}

f['vistaDeCima']['larguras']['carregador'] = {
    'mm': LARGURA,
    'nota': ('a fileira dupla desencontrada (3 + 2) da carga militar de .338 Lapua Magnum (correção C2 da P1, ~28 mm): '
             'o aro de Ø 14,93 encostado nas paredes de 0,8 e no cartucho da outra fila — os centros a ±5,735 do meio '
             '(0,77 diâmetro entre as filas, perto do desencontro dos carregadores de fuzil) e 9,557 mm de altura entre '
             'um e o próximo. É a fileira dupla que deixa o carregador curto do jogo levar os cinco: a pilha fica acima '
             'do fundo da coronha e a frente escondida (os projéteis passam da frente da parte à vista) cabe dentro '
             'dela; em fileira única o de baixo desceria a −84,7 e a frente sairia da coronha, à vista. O modelo do CS2 '
             'no visualizador 3D (de frente e de baixo) mostra 25 a 30 mm (estimativa: sem uma largura conhecida no '
             'mesmo plano); o ícone, na pose dele contra o nosso modelo, ~17,5 mm (a frente com 11,7 px, a nossa com '
             '18,7), com o comprimento do nosso. A AWM real é de fileira única (a brochura da AI)')
}
f['pontos']['carregador'] = {
    'fileira': 'dupla',
    'cartuchos': 5,
    'carga': '.338LM militar',
    'x': [X_TRAS, X_FRENTE],
    'frenteEscondida': X_FRENTE_ESCONDIDA,
    'recuoDaFrente': RECUO_DA_FRENTE,
    'topo': -12.0,
    'parede': PAREDE,
    'placaDeFundo': 6.5,
    'centros': centros,
    'passo': round(PASSO, 3),
    'fendas': FENDAS,
    'fonte': ('correção C2 da P1 (plano da 4.1d): a parte à vista é a da vista do jogo (a peça `carregador`: a frente, '
              'o fundo inclinado e as duas fendas, 75 mm), conferida no modelo do CS2 (o visualizador 3D: 74,4 a '
              '76,1 mm, o fundo de −92,5 na frente a −98,3 atrás, as fendas a 30 % e 73 % do comprimento, a placa de '
              'fundo à parte, ~6,5 mm) e no ícone; por dentro da coronha, a frente escondida até 91,7 mm por dentro '
              '(x = −735,9), com o fundo rente ao fundo da coronha (recuoDaFrente mm para dentro: o poço é reto e o '
              'carregador sai reto para baixo); os centros ([lado, alto], + à esquerda, o de cima primeiro) da conta '
              'da fileira dupla (vistaDeCima.larguras.carregador), o de cima a 0,05 mm do ferrolho fechado; as fendas '
              '(os centros em x e a largura) pelo modelo do CS2, nas frações do comprimento medidas nele (29,6 % e '
              '72,7 % da frente), com 5,8 mm de largura — a vista do CS:GO não resolve a largura')
}
f['pontos']['travaCarregador'] = [-833.0, -62.0]

# ------------------------------------------------------------------------------------------------ as fontes do CS2
fotos = [p for p in f['fotos'] if p.get('arquivo') not in ('CS2_AWP_Inventory.png', 'VSkin — o modelo da AWP do CS2 no visualizador 3D')]
fotos.append({
    'lado': 'esquerdo', 'espelhada': False,
    'arquivo': 'VSkin — o modelo da AWP do CS2 no visualizador 3D',
    'pagina': 'https://vskin.gg/skin-viewer?def=9&paint=279&seed=1&float=0',
    'autor': AUTOR, 'licenca': LICENCA, 'origem': 'jogo',
    'pixels': [4800, 4320], 'mmPorPixel': 0.3333,
    'usos': ['o carregador do CS2 (correção C2): o comprimento à vista, a frente, o fundo inclinado, as duas fendas, a '
             'placa de fundo e o lugar dele contra o guarda-mato (a primeira fonte)',
             'a largura do carregador de frente e de baixo (estimativa: 25 a 30 mm)'],
    'nota': ('o modelo do CS2 renderizado em WebGL pelo visualizador do site (a pele Asiimov: o carregador branco com a '
             'placa de fundo laranja, que mostra as partes), só olhado no navegador: o iframe do visualizador aumentado '
             'para 2400 e 4800 px CSS (o render refaz na resolução maior), a câmera de lado padrão, quase ortográfica; '
             'a escala pelo comprimento total (a ponta do freio e o fim da soleira a 1845,1 px CSS em 2400: 1,5001 '
             'px/mm, 1230 mm) e o alto pelo centro do freio. Leituras (em 4800, ±0,6 mm): o carregador de x = −760,5 a '
             '−834,9 (74,4) e de −760,1 a −836,2 (76,1) em duas posições, as fendas em −782,6 e −815,0 (5,8 de largura), '
             'o fundo de −92,5 na frente a −98,3 atrás, o guarda-mato com a frente do aro em −837,6 em cima e −861,6 '
             'embaixo e o fundo em −87,6. Contra a vista do CS:GO (a ficha), o carregador sai ~6 mm mais para trás e '
             'o aro do guarda-mato avança em cima até ele (na vista há 14 mm de coronha entre os dois): o carregador '
             'segue a peça da vista, que dá o mesmo comprimento, o mesmo fundo e as mesmas fendas, e a coronha fica a '
             'da vista (fora da C2)')
})
fotos.append({
    'lado': 'esquerdo', 'espelhada': False,
    'arquivo': 'CS2_AWP_Inventory.png',
    'pagina': 'https://counterstrike.fandom.com/wiki/File:CS2_AWP_Inventory.png',
    'autor': AUTOR, 'licenca': LICENCA, 'origem': 'jogo',
    'url': 'https://static.wikia.nocookie.net/cswikia/images/5/50/CS2_AWP_Inventory.png/revision/latest?cb=20230928175407',
    'pixels': [512, 384], 'mmPorPixel': 1.45,
    'usos': ['a pose do ícone (conferir.ICONE: a câmera de furo de 7 pontos, 3,6 px)',
             'o carregador do CS2 (correção C2, a segunda fonte): logo à frente do guarda-mato, o fundo descendo para '
             'trás e a face da frente clara do aço'],
    'nota': ('pelo alfa e pela luminância do ícone (a grade.html, no navegador): a frente do carregador em u = 374,4, a '
             'quina da frente com a face esquerda em 386,0, a traseira em 406,8, o fundo de v = 238,1 na frente a 245,9 '
             'atrás; atrás dele o contorno segue no nível do fundo do guarda-mato (v = 237,6) até a frente do punho '
             '(417,8). Na pose do ícone, contra a máscara do nosso modelo na mesma câmera (os dois em números, nada '
             'gravado do jogo): a face esquerda com o comprimento da nossa (20,8 px contra 20,1) e a mesma descida do '
             'fundo ao longo dela (2,6 e 2,3 px), a frente mais estreita (11,7 px contra 18,7: ~17,5 mm) e o carregador '
             '~10 px mais para trás (as quinas em 386,0 e 406,8; as nossas em 376,6 e 396,7). O fundo da coronha logo à '
             'frente dele (o da vista do CS:GO) sai deslocado o mesmo: casa com o nosso 10 a 14 px para trás (1,1 a '
             '1,7 px de desvio, contra 3,6 sem o deslocamento) — a câmera de 7 pontos erra nessa parte da arma, onde '
             'não tem ponto (e 3 a 6 px nos parafusos da coronha), e o carregador do ícone fica no lugar do nosso em '
             'relação à coronha; depois do deslocamento ele desce uns 2 a 5 px a mais. O cano bate a ≤ 0,7 px e a '
             'traseira da soleira a 0,5–6,9 px')
})
f['fotos'] = fotos

nota = ('carregador (correção C2 da P1, 2026-10-05): o curto do jogo em fileira dupla — a parte à vista é a peça '
        '`carregador` da vista (75 mm), conferida no modelo do CS2 no visualizador 3D e no ícone (as fotos de origem '
        '`jogo`), e por dentro da coronha ele se estende para a frente até 91,7 mm por dentro, com o fundo dessa frente '
        'rente ao fundo da coronha (o poço é reto: o carregador sai reto para baixo), e os cinco .338LM militares '
        'desencontrados (3 + 2, pontos.carregador), o de cima encostado no ferrolho fechado; o retém na frente do '
        'guarda-mato (pontos.travaCarregador, o pivô), na faixa de coronha entre os dois da vista — o lugar do manual '
        'da AW (A4: "o retém na frente do guarda-mato, com o polegar direito")')
f['notas'] = [n for n in f['notas'] if not n.startswith('carregador (correção C2')] + [nota]
with open(FICHA, 'w', encoding='utf-8') as saida:
    saida.write(json.dumps(f, ensure_ascii=False, indent=1) + '\n')
print('centros', centros, 'passo', round(PASSO, 3), 'frente escondida', X_FRENTE_ESCONDIDA, 'fendas', FENDAS)
print('o de cima: o topo em', round(centros[0][1] + R_ARO, 3), '| o de baixo: o fundo do aro em', round(centros[-1][1] - R_ARO, 3),
      'e o do projétil em', round(centros[-1][1] - 8.61 / 2, 3))
