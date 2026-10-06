# P90 do jogo — Fase 4.1d (desenho em docs/superpowers/specs/2026-10-03-4.1d-awp-nova-p90-design.md, seção 4.3; plano
# da 4.1d, Tarefa 10): a FN P90 TR de 5,7×28 com a forma, as cores e as peças do modelo do CS2 (item 9 do desenho: o
# contorno, os buracos e as peças de lado lidos da vista de lado do jogo pela régua, escalada à P90 de 505 mm; nenhuma
# malha, textura ou imagem do jogo entra) e a mecânica da arma real (o quadro bullpup de polímero com o buraco do
# polegar e a abertura do gatilho, o grupo do cano por cima com a ponte, o trilho e as miras de ferro rebatíveis da TR,
# as alças de manejo dos dois lados que levam o ferrolho, o gatilho que desliza, o seletor em disco, o obturador da
# janela de ejeção embaixo, atrás do punho, e o carregador de policarbonato deitado em cima, com os 50 cartuchos de
# través e o disco de transferência na ponta de trás). Construída em mm no referencial da ficha
# (tools/blender/refs/p90.json); a forma de três quartos conferida contra a foto 3/4 da FN (CC BY 2.0) pela câmera
# ajustada da ficha (tresQuartos). Lado direito da arma = -Y do Blender. Aqui: as constantes, os pivôs, os soquetes e a
# montagem; o quadro, a placa da coronha e os retentores em p90_quadro.py; a ponte, o corpo do grupo do cano, os
# trilhos, o cano com o quebra-chama e as miras em p90_cima.py; as alças, o ferrolho, o gatilho, o seletor e o
# obturador em p90_mecanica.py; o carregador e os cartuchos em p90_carregador.py. Sem marcação nenhuma (regra 9).
#
# Desvios da ficha e decisões da construção (registro da Tarefa 10 no plano):
#  - o carregador sai girando a traseira em volta da borda de cima da frente (o pivô em −84; 37, na própria ficha): com
#    o pivô embaixo, a parte de cima da tampa da frente andava para a frente no giro e entrava 1 mm na torre. O ressalto
#    de baixo da tampa corre, no curso para trás, por um canal no meio do corpo do grupo do cano, com a rampa atrás do
#    encaixe (invisível de lado);
#  - as miras de ferro do CS2 com as orelhas fixas na base e só a folha fina entre elas rebatendo (a de trás para trás,
#    a da frente para a frente), os pivôs no nó das folhas (na ficha), no lugar da mira rebatível genérica da
#    biblioteca, que não dá o desenho do CS2;
#  - o disco de transferência de eixo vertical, da altura do carregador (o prato preto redondo da ponta de trás das
#    fotos FNP90MAG01–03; o cilindro de eixo X da Tarefa 4 ficou na ficha como nota), com a janela de saída embaixo;
#  - a caixa da coronha abaixo do degrau 0,8 mm para dentro da largura do quadro (o degrau da vista de cima do CS2) e a
#    placa da coronha à parte, com a fenda;
#  - os retentores do carregador na zona `interno` (aço, como as molas), por dentro das paredes do quadro;
#  - os parafusos do quadro com a cabeça de sextavado interno do lado direito e a porca sextavada do esquerdo;
#  - os 48 cartuchos que aparecem (dois na rampa e no prato não aparecem; manual do armeiro §6.4): no jogo, os 48 só
#    no perto (num nó filho do carregador, desenhado antes do policarbonato) e duas fileiras simplificadas no mundo e
#    no longe;
#  - a seção arredondada do quadro (p90_secao.py) com o raio de cada lado do contorno pela distância ao segmento (o de
#    cima, o de baixo com o entalhe da frente do punho, 3 mm nas bordas de baixo acima de y = −30) e a face de lado em
#    triângulos pelo Delaunay restrito, com as fileiras nos ângulos do quarto de círculo; o laço e a caixa como regiões
#    do mesmo prisma com a face do degrau (os booleanos deles abriam a malha), e os rebaixos dos parafusos dos dois
#    lados com as costuras num cortador só; o buraco do polegar e a abertura da frente na mesma malha, com as fileiras
#    do arredondado em volta deles e a parede deles no prisma (cortados por um cortador arredondado, a face plana ficava
#    com os triângulos longos do Delaunay presos à borda do corte, e as normais puxadas por ela davam faixas claras
#    abaixo dos dois buracos, no modelo alto e, pelo assar, no de jogo);
#  - o quebra-chama com as portas e o serrilhado de borda viva, cortados depois do chanfro (antes dele, a borda das
#    portas se dobrava nos cruzamentos com os lados do torno), o torno girado meio lado e a boca de 64 lados um quarto;
#  - os furos do quadro com o contorno de 0,02 mm no modelo alto e 0,12 no de jogo (com 0,1 e 0,35, as facetas da borda
#    arredondada apareciam).
import math

from . import p90_carregador as CARREGADOR
from . import p90_cima as CIMA
from . import p90_mecanica as MEC
from . import p90_quadro as Q
from . import pecas as P

ORIGEM_MM = (-174.0, 0.0)  # o pino do gatilho no eixo do cano: a origem da arma no jogo
# A pose do ícone do inventário do CS2 da P90 (conferir.py, `icone`): a câmera de furo ajustada (Levenberg-Marquardt) a
# nove pontos do ícone — o centro da boca do quebra-chama, a face do botão da alavanca e os sete parafusos da face
# esquerda (o pé do lóbulo, os dois de baixo do punho e os quatro da coronha), com o lado de cada um no modelo —,
# marcados no navegador sobre o ícone, nada gravado; 1,5 px de erro médio (3,0 no pior), a lente de 72,8 mm. A câmera
# fica à frente, à esquerda e um pouco abaixo da arma, olhando 8,1° para cima. Pela mesma câmera, o trilho de cima e as
# miras do ícone voltam ao plano de lado ~18 mm mais baixos que os da TR real (o topo do trilho a 75,7 mm do eixo, as
# orelhas das miras a 113–118) e a mira da frente ~25 mm mais para trás: a ponte do CS2 é mais baixa (registro da
# Tarefa 10; a decisão é da P1).
ICONE = {
    'frente': (-0.6344, -0.7599, 0.1416), 'cima': (0.1329, 0.0732, 0.9884), 'lente': 72.8,
    'distancia': 0.9227, 'mira': (0.0223, -0.0173, 0.0069), 'comprimento': 0.505, 'quadro': (1600, 1200),
}
PECAS = ('carregador', 'alavanca', 'ferrolho', 'gatilho', 'seletor', 'obturador', 'rebativel_tras', 'rebativel_frente')
PERTO_MM = (-185.0, -35.0)  # a vista de perto da conferência: o punho, o gatilho, o seletor e o botão da alavanca
PUNHO_Y = (-25.0, -48.0)  # as duas alturas da linha do meio do punho (entre o buraco do polegar e o gatilho)


def _cruzamentos_x(poligono, y):
    """Os x em que a horizontal y corta o polígono fechado."""
    xs = []
    for (ax, ay), (bx, by) in zip(poligono, poligono[1:] + poligono[:1]):
        if (ay - y) * (by - y) < 0 or (ay == y and by != y):
            xs.append(ax + (y - ay) * (bx - ax) / (by - ay))
    return xs


def linha_do_punho(ficha):
    """A linha do meio do punho, de cima para baixo: o meio entre a borda da frente do buraco do polegar e a de trás do
    gatilho, nas alturas de PUNHO_Y."""
    oval = [tuple(p) for p in ficha['buracos'][ficha['buracosNomes'].index('ovalTras')]]
    gat = [tuple(p) for p in ficha['pecas']['gatilho']]
    return [((max(_cruzamentos_x(oval, y)) + min(_cruzamentos_x(gat, y))) / 2, y) for y in PUNHO_Y]


def pivos(ficha):
    """Pivô (mm, ficha) e extras de cada peça (direções no referencial do jogo: +X boca, +Y cima, +Z direita)."""
    pt = ficha['pontos']
    c = pt['carregador']
    g = pt['seletor']['graus']
    return {
        'base': (ORIGEM_MM, {}),
        # o carregador: a traseira sobe em volta da borda de cima da frente até passar da coronha e ele sai para trás ao
        # longo dele mesmo (o ressalto da frente pelo canal do corpo do grupo do cano)
        'carregador': (tuple(c['pivo']), {'eixo_giro': [0.0, 0.0, -1.0], 'graus': c['graus'], 'eixo': list(c['eixo']), 'curso': c['curso'],
                                          'ordem': ['giro', 'curso']}),
        # as alças de manejo correm para trás e levam o ferrolho
        'alavanca': (tuple(pt['alavanca']['botao']), {'eixo': [-1.0, 0.0, 0.0], 'curso': pt['alavanca']['curso'], 'ordem': ['curso'],
                                                      'arrasta': {'peca': 'ferrolho', 'razao': 1.0}}),
        # o ferrolho só anda arrastado, ao longo do eixo do cano (o pivô na face, na câmara)
        'ferrolho': ((pt['ferrolho']['x'][1], 0.0), {'eixo': [-1.0, 0.0, 0.0]}),
        # o gatilho desliza para trás (meio curso: tiro único; o curso todo: rajada)
        'gatilho': (tuple(pt['pinoGatilho']), {'eixo': [-1.0, 0.0, 0.0], 'curso': pt['gatilho']['curso'], 'ordem': ['curso']}),
        # o seletor em disco gira em volta do eixo vertical pelas três posições (S, 1, A; a lingueta para a esquerda)
        'seletor': (tuple(pt['seletor']['centro']), {'eixo_giro': [0.0, 1.0, 0.0], 'graus': g[-1] - g[0], 'ordem': ['giro'],
                                                     'paradas': [v - g[0] for v in g]}),
        # o obturador abre para baixo pela dobradiça de trás
        'obturador': (tuple(pt['obturador']['pivo']), {'eixo_giro': [0.0, 0.0, -1.0], 'graus': pt['obturador']['graus'], 'ordem': ['giro']}),
        # as miras deitam: a de trás para trás, a da frente para a frente
        'rebativel_tras': (tuple(pt['rebativelTras']['pivo']), {'eixo_giro': [0.0, 0.0, 1.0], 'graus': pt['rebativelTras']['graus'],
                                                                'ordem': ['giro']}),
        'rebativel_frente': (tuple(pt['rebativelFrente']['pivo']), {'eixo_giro': [0.0, 0.0, -1.0], 'graus': pt['rebativelFrente']['graus'],
                                                                    'ordem': ['giro']}),
    }


def soquetes(ficha):
    """(nome, (x, y) da ficha, lado = Y do Blender em mm, rotação XYZ em graus no Blender[, peça que o soquete
    acompanha])."""
    pt = ficha['pontos']
    s0, s1 = MEC.JANELA['s']
    ejecao = MEC.no_fundo(ficha, (s0 + s1) / 2, 0.0)
    m = CARREGADOR.medidas(ficha)
    carregador = ((m['x_tras'] + m['x_frente']) / 2, (m['fundo'] + m['alto_tampa']) / 2)
    (tx, ty), (bx, by) = linha_do_punho(ficha)
    a = math.degrees(math.atan2(tx - bx, ty - by))
    return [
        ('boca', (0.0, 0.0), 0.0, (0, 0, 0)),
        # a cápsula sai por baixo, pela janela do obturador atrás do punho, para baixo e um pouco para trás (com o
        # ferrolho que recua)
        ('ejecao', ejecao, 0.0, (0, 100, 0)),
        # o carregador deitado em cima do quadro: o meio dele
        ('carregador', carregador, 0.0, (0, 0, 0)),
        # a linha de mira: o centro do tambor da mira de trás e o topo do poste da da frente
        ('mira_tras', tuple(pt['miraTras']), 0.0, (0, 0, 0)),
        ('mira_frente', tuple(pt['miraFrente']), 0.0, (0, 0, 0)),
        # o +Z do soquete (o +Y no jogo) sobe pela linha do punho
        ('mao_d', tuple(pt['pescoco']), 0.0, (0, a, 0)),
        ('mao_e', tuple(pt['maoApoio']), 0.0, (0, 0, 0)),
    ]


def construir(ficha, M):
    P.chanfro_local()  # o chanfro com o limite local (chanfro_local.py)
    Q.construir(ficha, M)
    CIMA.construir(ficha, M)
    MEC.construir(ficha, M)
    CARREGADOR.construir(ficha, M)
