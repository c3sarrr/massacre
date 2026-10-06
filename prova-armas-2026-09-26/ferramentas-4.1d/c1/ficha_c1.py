# A correção C1 na ficha da P90 (tools/blender/refs/p90.json): a parte de cima na forma do CS2, com os números medidos
# nas duas fontes do jogo (o ícone e o quadro de 108,6 s do vídeo de inspeção, pelo ajuste conjunto das duas câmeras),
# o contorno composto (o quadro da FN + a parte de cima do CS2), as fontes do jogo nas fotos (só números; nada guardado)
# e a caixa da vista de três quartos sem a parte de cima. Escreve no formato da ficha (indent 1, sem escapar, \n no fim).
#   python ficha_c1.py
import json

FICHA = r'C:/Users/T-Gamer/Desktop/game tiro/trabalho-4.1d/tools/blender/refs/p90.json'
f = json.load(open(FICHA, encoding='utf-8'))
LIC = '© Valve Corporation — só referência visual, lida no navegador, nada guardado'
AUTOR = 'Valve Corporation (modelo do jogo)'

# ---------------------------------------------------------------- o trilho de cima (MIL-STD-1913 no perfil, no CS2)
TOPO, BASE = 76.6, 67.2
FUNDO = round(TOPO - 2.997, 2)  # a fenda da norma: 0,118 pol. de fundo
MEIA = 5.232 / 2  # a fenda da norma: 0,206 pol. de largura
FENDAS = [round(-79.45 - 10.0 * k, 2) for k in range(13)]
X_TRILHO = (-205.7, -73.0)  # a frente embaixo da aba da base da mira da frente (a face dela em −69,5)
trilho = [(X_TRILHO[0], TOPO), (X_TRILHO[0], BASE), (X_TRILHO[1], BASE), (X_TRILHO[1], TOPO)]
for xc in FENDAS:  # da frente para trás, como o topo corre neste contorno
    trilho += [(round(xc + MEIA, 2), TOPO), (round(xc + MEIA, 2), FUNDO), (round(xc - MEIA, 2), FUNDO), (round(xc - MEIA, 2), TOPO)]

# ---------------------------------------------------------------- a ponte (o perfil de lado inteiro: corpo + pernas)
RAMPA_TRAS = [(-201.0, 67.2), (-203.6, 66.2), (-205.8, 64.2), (-207.8, 61.4), (-209.4, 58.4), (-210.6, 55.5), (-212.2, 51.5),
              (-214.0, 47.0), (-216.0, 42.0), (-217.6, 38.0), (-218.4, 33.0), (-219.2, 23.0), (-221.0, 1.3)]
FRENTE_PERNA = [(-186.0, 1.3), (-184.5, 23.5), (-179.2, 37.8), (-177.5, 39.3), (-172.5, 51.3)]
VAO = [(-155.5, 49.5), (-132.5, 44.8), (-101.0, 40.8), (-96.0, 38.8), (-82.2, 38.8)]
TORRE = [(-82.2, 36.3), (-79.0, 35.8), (-77.5, 33.8), (-78.0, 29.5), (-80.7, 27.3), (-80.7, 16.8), (-82.2, 14.3), (-82.2, 1.3),
         (-47.5, 1.3), (-47.5, 11.8), (-48.6, 26.5), (-49.6, 38.4), (-51.5, 47.9), (-68.4, 65.6), (-69.5, 67.2)]
ponte = RAMPA_TRAS + FRENTE_PERNA + VAO + TORRE
# as pernas de trás (as placas por fora do carregador): a frente e o pé da FN, o alto do CS2 (sobe de 52 a 58,6) e a
# traseira na mesma linha da rampa do corpo
pernas = ([(-172.5, 51.3), (-175.0, 52.3), (-180.1, 53.1), (-187.4, 55.3), (-194.9, 56.9), (-202.3, 58.2), (-206.6, 58.8), (-208.6, 58.7)]
          + RAMPA_TRAS[4:] + FRENTE_PERNA[:-1])

# ---------------------------------------------------------------- as miras de ferro rebatíveis do CS2
BASE_FRENTE = [(-69.5, 67.2), (-73.0, 67.2), (-73.0, 70.0), (-105.0, 70.0), (-105.0, 77.2), (-92.0, 88.6), (-74.5, 88.6), (-69.5, 83.4)]
ORELHA_FRENTE = [(-78.2, 86.0), (-88.0, 86.0), (-87.6, 108.8), (-86.5, 112.7), (-84.0, 114.3), (-77.5, 114.2), (-75.0, 111.5), (-74.6, 108.0)]
BASE_TRAS = [(-160.0, 70.0), (-160.0, 86.0), (-165.0, 91.0), (-184.0, 91.0), (-199.0, 77.0), (-199.0, 70.0)]
ORELHA_TRAS = [(-163.5, 88.0), (-163.5, 91.0), (-163.8, 105.0), (-165.6, 109.6), (-167.8, 114.8), (-169.5, 117.3), (-172.7, 118.0),
               (-175.0, 117.4), (-176.6, 115.3), (-178.4, 112.4), (-180.2, 109.1), (-182.2, 105.2), (-182.5, 91.0), (-182.5, 88.0)]
MIRA_FRENTE = [(-69.5, 67.2), (-73.0, 67.2), (-73.0, 70.0), (-105.0, 70.0), (-105.0, 77.2), (-92.0, 88.6), (-88.0, 88.6), (-87.6, 108.8),
               (-86.5, 112.7), (-84.0, 114.3), (-77.5, 114.2), (-75.0, 111.5), (-74.6, 108.0), (-77.8, 88.6), (-74.5, 88.6), (-69.5, 83.4)]
MIRA_TRAS = [(-160.0, 70.0), (-160.0, 86.0), (-163.5, 89.5), (-163.8, 105.0), (-165.6, 109.6), (-167.8, 114.8), (-169.5, 117.3),
             (-172.7, 118.0), (-175.0, 117.4), (-176.6, 115.3), (-178.4, 112.4), (-180.2, 109.1), (-182.2, 105.2), (-182.5, 91.0),
             (-184.0, 91.0), (-199.0, 77.0), (-199.0, 70.0)]

# ---------------------------------------------------------------- o contorno composto (o quadro da FN + a parte de cima do CS2)
velho = [tuple(p) for p in f['contorno']]
i_coronha = velho.index((-482.7, 39.3))  # o alto da coronha, atrás
i_quebra = velho.index((-2.0, 10.9))  # o alto do quebra-chama, na ponta
topo = [(-74.6, 108.0), (-75.0, 111.5), (-77.5, 114.2), (-84.0, 114.3), (-86.5, 112.7), (-87.6, 108.8), (-88.0, 88.6), (-92.0, 88.6),
        (-105.0, 77.2), (-105.0, TOPO)]
for xc in FENDAS:  # as fendas à vista entre as bases (a de −159,45 até a face da base de trás)
    if -160.0 < xc + MEIA < -105.0:
        topo += [(round(xc + MEIA, 2), TOPO), (round(xc + MEIA, 2), FUNDO)]
        topo += [(round(xc - MEIA, 2), FUNDO), (round(xc - MEIA, 2), TOPO)] if xc - MEIA > -160.0 else [(-160.0, FUNDO)]
topo += [(-160.0, 86.0), (-163.5, 89.5), (-163.8, 105.0), (-165.6, 109.6), (-167.8, 114.8), (-169.5, 117.3), (-172.7, 118.0),
         (-175.0, 117.4), (-176.6, 115.3), (-178.4, 112.4), (-180.2, 109.1), (-182.2, 105.2), (-182.5, 91.0), (-184.0, 91.0),
         (-199.0, 77.0), (-199.0, FUNDO), (round(FENDAS[-1] - MEIA, 2), FUNDO), (round(FENDAS[-1] - MEIA, 2), TOPO), (X_TRILHO[0], TOPO),
         (X_TRILHO[0], BASE), (-201.0, 67.2)] + RAMPA_TRAS[1:10] + [(-217.6, 37.8)]
frente = [(-47.5, 10.9), (-47.5, 11.8), (-48.6, 26.5), (-49.6, 38.4), (-51.5, 47.9), (-68.4, 65.6), (-69.5, 67.2), (-69.5, 83.4),
          (-74.5, 88.6), (-77.8, 88.6)]
contorno = topo + velho[i_coronha:i_quebra + 1] + frente
f['contorno'] = [[round(x, 2), round(y, 2)] for x, y in contorno]

# ---------------------------------------------------------------- as peças de lado
pc = f['pecas']
novas = {}
for k, v in pc.items():
    if k == 'trilhoLateral':
        continue
    novas[k] = v
    if k == 'ponte':
        novas['pernasPonte'] = None
    if k == 'rebativelFrente':
        for n in ('baseMiraTras', 'orelhaMiraTras', 'baseMiraFrente', 'orelhaMiraFrente'):
            novas[n] = None
novas.update({'ponte': ponte, 'pernasPonte': pernas, 'trilhoCima': trilho, 'rebativelTras': MIRA_TRAS, 'rebativelFrente': MIRA_FRENTE,
              'baseMiraTras': BASE_TRAS, 'orelhaMiraTras': ORELHA_TRAS, 'baseMiraFrente': BASE_FRENTE, 'orelhaMiraFrente': ORELHA_FRENTE})
f['pecas'] = {k: [[round(x, 2), round(y, 2)] for x, y in v] for k, v in novas.items()}

# ---------------------------------------------------------------- os buracos: as janelas da TR saem (as do CS2 são rebaixos)
buracos = [(n, b) for n, b in zip(f['buracosNomes'], f['buracos']) if n not in ('janelaPonte', 'frestaTrilho')]
f['buracosNomes'] = [n for n, _ in buracos]
f['buracos'] = [b for _, b in buracos]

# ---------------------------------------------------------------- as linhas e os pontos
f['linhas']['linhaDeMira'] = [[-173.0, 112.2], [-81.1, 112.2]]
pt = f['pontos']
FONTE_CS2 = ('a parte de cima do CS2 medida no ícone do inventário (o mesmo das peles: P90_Wash_me.png e as outras de 2024 a 2026, '
             'IoU 1,0000 entre elas) e no quadro de 108,6 s do vídeo de inspeção (y1NSHUq7WOI), lidos no navegador: as duas câmeras '
             'de furo pelo ajuste conjunto (os nove parafusos da face esquerda presos nas posições da ficha, os pontos de cima livres; '
             'ícone 1,04 px, vídeo 1,88 px) e os cantos marcados nas duas imagens triangulados ou cortados no plano de lado de cada '
             'face; o grupo de cima sai ~3,9 mm para a direita nesse referencial (as duas miras simétricas em volta dele: o erro dos '
             'lados dos parafusos), e o modelo o põe no eixo (correção C1, 2026-10-05)')
novos_pontos = {}
for k, v in pt.items():
    if k in ('trilhoLateral', 'travaGrupoCano'):
        continue
    novos_pontos[k] = v
    if k == 'janelaTorre':
        novos_pontos['janelasPonte'] = None
    if k == 'rebativelFrente':
        novos_pontos['miras'] = None
novos_pontos['trilhoCima'] = {'x': list(X_TRILHO), 'topo': TOPO, 'fundo': FUNDO, 'base': BASE, 'passo': 10.0, 'largura': 21.2, 'fendas': FENDAS,
                              'fonte': 'o topo a 76,6 mm do eixo e o fim de trás em −205,7 (o canto de cima triangulado nas duas imagens), a '
                                       'base na ponte a 67,2; as fendas a cada 10 mm a partir de −79,45 (a média do ícone e do vídeo: cada '
                                       'vista põe a fenda na parede de perto, e a média tira o viés); o perfil e a fenda, da MIL-STD-1913; '
                                       'a frente embaixo da aba da base da mira da frente (−73: a face dela em −69,5 cobre a ponta). '
                                       + FONTE_CS2}
novos_pontos['janelaTorre'] = {'x': [-71.0, -52.0], 'y': [14.0, 33.0], 'raio': 2.0, 'profundidade': 6.0,
                               'fonte': 'o rebaixo quadrado dos lados da torre, escuro no ícone e no vídeo (fundo, não vazado: o ícone não '
                                        'mostra o fundo através dele); a profundidade é estimativa. ' + FONTE_CS2}
novos_pontos['janelasPonte'] = {'frente': {'x': [-157.5, -86.0], 'y': [58.2, 65.2]}, 'tras': {'x': [-196.0, -163.0], 'y': [58.5, 67.2]},
                                'raio': 1.5, 'profundidade': 4.0,
                                'fonte': 'os dois rebaixos compridos dos lados da ponte, sob o trilho, com a nervura entre eles em x = −157,5 a '
                                         '−163 (a faixa clara no ícone): o da frente com o lábio de 2 mm embaixo do trilho, o de trás aberto '
                                         'em cima até o trilho; a altura é a média do ícone (58,2 a 64,5) e do vídeo (58,3 a 66) e varia ±2 mm '
                                         'entre as fontes; fundos, não vazados (o ícone não mostra o fundo através deles: no lugar das janelas '
                                         'vazadas da TR); a profundidade é estimativa. ' + FONTE_CS2}
novos_pontos['miraTras'] = [-173.0, 112.2]
novos_pontos['miraFrente'] = [-81.1, 112.2]
novos_pontos['rebativelTras'] = {'pivo': [-173.0, 95.0], 'graus': 90.0,
                                 'fonte': 'a folha do anel da mira de trás (o centro do anel em −173; 112,2, a linha de mira) dobra para trás '
                                          'entre as orelhas fixas, como no CS2; o pino 4 mm acima do alto da base — a posição do pino é '
                                          'estimativa (as miras ficam sempre levantadas no jogo)'}
novos_pontos['rebativelFrente'] = {'pivo': [-81.1, 92.5], 'graus': 90.0,
                                   'fonte': 'a folha do poste da mira da frente (o topo do poste em −81,1; 112,2) dobra para a frente entre as '
                                            'orelhas fixas; o pino 3,9 mm acima do alto da base — a posição do pino é estimativa'}
novos_pontos['miras'] = {
    'baseMeia': 12.2, 'orelhasTras': [8.75, 11.25], 'orelhasFrente': [5.5, 8.0],
    'botoes': {'tras': [-171.2, 82.3], 'frente': [-77.0, 82.3], 'raio': 6.3, 'lado': 15.4},
    'parafusos': {'tras': {'centro': [-185.2, 77.7], 'raio': 4.7}, 'frente': {'centro': [-91.5, 78.0], 'raio': 4.7}, 'lado': 16.0},
    'furosOrelha': {'centro': [-171.1, 105.4], 'raio': 5.6, 'n': 8, 'diametro': 1.6},
    'anel': {'raio': 5.0, 'abertura': 1.0}, 'poste': {'largura': 1.6, 'comprimento': 2.4},
    'fonte': ('as miras do CS2: as bases presas no trilho (a da frente de −69,5 a −105 com a rampa de trás, a de trás de −160 a '
              '−199), as orelhas fixas (as da frente de 5,5 a 8 mm do eixo, até 114,6; as de trás de 8,75 a 11,25, arredondadas, '
              'até 118, a da esquerda com o anel de oito furos de Ø 1,6 a 45° em volta de −171,1; 105,4, r 5,6 — os oito centros no'
              ' quadro do vídeo, voltados ao plano da face da orelha: fonte única, o ícone não resolve os furos), o botão do aperto'
              ' à esquerda, baixo, de prato fundo (Ø 12,6, a face a 15,4 mm do eixo: o contorno dele nas duas imagens é quase só o '
              'do prato; o centro triangulado nas duas, −77,0; 82,3 e −171,2; 82,3, com 0,3 a 0,7 mm entre os raios) e o parafuso '
              'de fenda de cabeça alta atrás dele, mais baixo (Ø 9,4, o topo a 16 mm do eixo; o da frente triangulado nas duas, '
              '−91,5; 78,0, a 0,3–0,7 mm; o de trás pelo vídeo no plano do topo, −185,2; 77,7: no ícone a cabeça dele se mistura '
              'com a rampa da base); a linha de mira a 112,2 (o centro do anel e o topo do poste, pelo quadro de primeira pessoa: '
              'fonte única, aproximada); o lado direito das bases (a porca do aperto) não aparece em nenhuma das duas: estimativa '
              'pela mecânica. ') + FONTE_CS2}
f['pontos'] = novos_pontos

# ---------------------------------------------------------------- as medidas e as larguras
md = f['medidas']
md['raioDeMira'] = {'mm': 91.9, 'fonte': 'as miras de ferro do CS2: do centro do anel da mira de trás (x = −173,0) ao topo do poste da da '
                                         'frente (x = −81,1), medidas no ícone e no vídeo (correção C1)'}
md['alturaSemCarregador'] = {'mm': 220.0, 'fonte': 'foto de lado da FN (−102, o pé do lóbulo da frente) e as orelhas da mira de trás do CS2 '
                                                   '(118, medidas no ícone e no vídeo); o carregador fica dentro da altura'}
md['alturaComCarregador'] = {'mm': 220.0, 'fonte': 'a mesma: o carregador fica deitado em cima do quadro, sob a ponte'}
md['alturaSemMiras'] = {'mm': 178.6, 'fonte': 'foto de lado da FN (−102) e o topo do trilho de cima do CS2 (76,6; a TR real, 93,8: a ponte do '
                                              'CS2 é mais baixa, correção C1)'}
L = f['vistaDeCima']['larguras']
novas_l = {}
for k, v in L.items():
    if k in ('trilhoLateral', 'ponteTrilhos'):
        if k == 'trilhoLateral':
            novas_l['pernasPonte'] = {'mm': 52.8, 'nota': 'as pernas de trás da ponte por fora do carregador: a face delas a 26,4 mm do eixo '
                                                          '(a da TR pelo ajuste da câmera da foto 3/4, os parafusos dos trilhos laterais na '
                                                          'mesma face; no CS2, sem os trilhos, as placas à vista no vídeo)'}
        continue
    novas_l[k] = v
novas_l['ponte'] = {'mm': 32.0, 'nota': 'a ponte do CS2 (a torre e o corpo sob o trilho): as faces a 16 mm do eixo, a da torre triangulada no '
                                        'ícone e no vídeo e a do corpo conferida pelas janelas e pela rampa de trás (correção C1); a TR real '
                                        'tem a torre de 30,2 e o corpo de 40,8 com os trilhos laterais'}
novas_l['rebativelTras'] = {'mm': 24.4, 'nota': 'a base da mira de trás em volta do trilho de 21,2 (as orelhas a 11,25 do eixo; o botão do '
                                                'aperto até 15,4 e o parafuso de fenda até 16, à esquerda)'}
novas_l['rebativelFrente'] = {'mm': 24.4, 'nota': 'a base da mira da frente em volta do trilho de 21,2 (as orelhas a 8 do eixo; o botão até 15,4 e o parafuso até 16)'}
f['vistaDeCima']['larguras'] = novas_l

# ---------------------------------------------------------------- a vista de três quartos sem a parte de cima
f['tresQuartos']['foraCaixas'] = [{
    'nome': 'parteDeCima', 'caixa': [[-232.0, 37.5, -28.0], [-28.0, 135.0, 28.0]],
    'nota': 'a parte de cima do CS2 (a ponte de 32 mm sem os trilhos laterais, o trilho de cima a 76,6 e as miras levantadas; correção C1) '
            'no lugar da da TR da foto: a conta compara o quadro, o carregador e o cano'}]

# ---------------------------------------------------------------- as fotos: as duas fontes do jogo da parte de cima
fotos = f['fotos']
w = next(p for p in fotos if p['arquivo'] == 'W_p90_csgo.png')
w['usos'] = ['o quebra-chama do jogo (o cilindro liso com três portas ovais e a ponta arredondada)', 'cores (a mediana de cada peça)']
w['nota'] = (w['nota'] + '; as miras de ferro saíam dela na Tarefa 10 (levadas ao trilho da TR pela fração ao longo dele): a W_ é do CS:GO e a '
             'parte de cima do CS2 é outra (mais baixa, sem os trilhos laterais) — desde a correção C1 a parte de cima sai do ícone e do vídeo '
             'do CS2')
fotos = [p for p in fotos if p.get('url') != 'https://static.wikia.nocookie.net/cswikia/images/a/ae/P90_Wash_me.png/revision/latest?cb=20241006133724'
         and 'y1NSHUq7WOI' not in p.get('pagina', '')]
fotos.append({
    'lado': 'esquerdo', 'espelhada': False, 'arquivo': 'P90_Wash_me.png', 'pagina': 'https://counterstrike.fandom.com/wiki/File:P90_Wash_me.png',
    'autor': AUTOR, 'licenca': LIC, 'origem': 'jogo',
    'url': 'https://static.wikia.nocookie.net/cswikia/images/a/ae/P90_Wash_me.png/revision/latest?cb=20241006133724',
    'pixels': [512, 384], 'mmPorPixel': 0.83,
    'usos': ['a parte de cima do CS2 (correção C1): a ponte e a torre, o trilho de cima, as janelas, as pernas de trás e as miras de ferro '
             'rebatíveis — os cantos marcados aqui e no vídeo, triangulados',
             'a pose do ícone (p90.ICONE: a câmera do ajuste conjunto)'],
    'camera': {'posicao': [427.0, -109.6, 755.5], 'frente': [-0.6424, 0.1273, -0.7557], 'cima': [0.1305, 0.9899, 0.0557], 'focalPx': 1147.5,
               'erroPx': 1.04, 'metodo': 'câmera de furo pelo ajuste conjunto com a do vídeo: os nove parafusos da face esquerda nas posições '
                                         'da ficha e os pontos de cima livres, o ponto principal no centro (a posição em mm e os eixos em '
                                         '[x, y, lado] da ficha, como a tresQuartos.camera)'},
    'nota': 'o ícone do inventário da P90 e os das peles do CS2 (2024 a 2026) têm a mesma câmera e o mesmo alfa (IoU 1,0000); a pele Wash me, '
            'clara, mostra melhor a estrutura da ponte. Os ícones da época do CS:GO (a Nostalgia, 2019) mostram a parte de cima mais alta: '
            'o modelo do CS2 é outro. A escala, perto da ponte (a 0,96 m da câmera)'})
fotos.append({
    'lado': 'esquerdo', 'espelhada': False, 'arquivo': 'Counter-Strike 2 - All Inspect Animations (quadro de 108,6 s)',
    'pagina': 'https://www.youtube.com/watch?v=y1NSHUq7WOI', 'autor': AUTOR, 'licenca': LIC, 'origem': 'jogo',
    'pixels': [1920, 1080], 'mmPorPixel': 0.51,
    'usos': ['a parte de cima do CS2 (correção C1), vista de trás, da esquerda e de baixo: a rampa de trás da ponte, as pernas de trás, as '
             'janelas, a torre, as orelhas e os botões das miras e os parafusos de fenda das bases — a segunda fonte de cada canto (com o ícone)'],
    'camera': {'posicao': [-422.6, -149.0, 524.0], 'frente': [0.4096, 0.3447, -0.8447], 'cima': [0.0622, 0.9132, 0.4028], 'focalPx': 1231.4,
               'erroPx': 1.88, 'tempo': 108.6, 'metodo': 'câmera de furo pelo ajuste conjunto com a do ícone (os mesmos parafusos)'},
    'nota': 'a gravação do canal PC Gaming Videos da inspeção no CS2; o quadro parado no navegador, só lido. A escala, perto da ponte (a 0,63 m)'})
f['fotos'] = fotos

# ---------------------------------------------------------------- a variante e as notas
f['variante'] = ('a P90 do CS2 — a FN P90 TR de 5,7×28 mm com a parte de cima do modelo do jogo (a ponte de 32 mm sem os trilhos laterais, '
                 'o trilho de cima a 76,6 mm do eixo e as miras de ferro rebatíveis do CS2 levantadas), 50 tiros, o quebra-chama do modelo do '
                 'jogo, o quadro cinza-grafite e o carregador castanho-ferrugem quase opaco — na escala da FN P90 (505 mm)')
notas = f['notas']
notas[1] = ('as miras de ferro rebatíveis do CS2 (desde a correção C1, medidas no ícone e no vídeo do CS2; na Tarefa 10, levadas da W_ ao '
            'trilho da TR pela fração ao longo dele): a de trás com as orelhas arredondadas de −163,5 a −182,5 até 118 e o anel no centro '
            '(−173; 112,2), a da frente com as orelhas de −74,6 a −88 até 114,6 e o poste (−81,1; 112,2) — a linha de mira, na mesma '
            'altura, e o raio de 91,9 mm')
notas[6] = ('a altura sem as miras: −102 (a foto da FN) a 76,6 (o topo do trilho do CS2): 178,6 mm (a TR real, 93,8: 195,8; o manual dá 180 '
            'para a TR); com as miras do CS2 levantadas, 220 mm')
nota_c1 = ('Correção C1 (2026-10-05): a parte de cima na forma do CS2, medida em duas fontes do jogo independentes — o ícone do inventário '
           '(o mesmo das peles) e o quadro de 108,6 s do vídeo de inspeção —, só lidas no navegador, pelo ajuste conjunto das duas câmeras '
           '(os nove parafusos da face esquerda presos nas posições da ficha; os cantos de cima marcados nas duas e triangulados; ícone '
           '1,04 px e vídeo 1,88 px nos parafusos). No CS2: a ponte de 32 mm sem os trilhos laterais nem o botão de trava do grupo do cano, '
           'com a torre de frente inclinada (−47,5 embaixo a −51,5 em 47,9, o chanfro até −69,5 no alto), os dois rebaixos compridos dos '
           'lados sob o trilho com a nervura entre eles e o rebaixo da torre (fundos: o ícone não mostra o fundo através deles), as pernas '
           'de trás como placas por fora do carregador com o alto subindo de 52 a 58,6, e o corpo terminando numa rampa logo atrás do '
           'trilho (de −201 em 67,2 a −217,6 em 38, na linha da traseira das pernas: o ícone e o vídeo diferem ~3 mm nela e a ficha fica '
           'entre os dois); o trilho de cima a 76,6 (a TR, 93,75) de −205,7 a −73, com as fendas da norma a cada 10 mm desde −79,45; as '
           'miras com as orelhas fixas, o botão do aperto à esquerda e o parafuso de fenda atrás dele. O grupo de cima sai ~3,9 mm para a '
           'direita no referencial das câmeras (o erro dos lados dos parafusos da ficha; as duas miras são simétricas em volta dele) e o '
           'modelo o põe no eixo. O contorno é composto: o quadro, o carregador e o quebra-chama da foto de lado da FN; a parte de cima do '
           'CS2. A vista de três quartos da FN confere sem a parte de cima (tresQuartos.foraCaixas)')
notas = [n for n in notas if not n.startswith('Correção C1')] + [nota_c1]
f['notas'] = notas

open(FICHA, 'w', encoding='utf-8').write(json.dumps(f, indent=1, ensure_ascii=False) + '\n')
print('ok: contorno', len(f['contorno']), 'pontos; peças', list(f['pecas']), '; buracos', f['buracosNomes'])
xs = [p[0] for p in f['contorno']]
ys = [p[1] for p in f['contorno']]
print('caixa do contorno x', min(xs), max(xs), 'y', min(ys), max(ys))
