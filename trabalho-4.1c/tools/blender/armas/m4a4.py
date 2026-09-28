# M4A4 do jogo = a carabina M4A1 — Fase 4.1c (desenho em docs/superpowers/specs/2026-09-28-4.1c-glock-m4a4-m9-design.md,
# seção 3.2). Construída em mm no referencial da ficha (tools/blender/refs/m4a4.json): o contorno composto da foto da PEO
# (a frente, os receptores, o punho, o carregador) com a coronha M4 e a alça de transporte da foto da NSWC, pela régua; o
# lado esquerdo (o seletor, o retém do ferrolho) da File:M4w-att.jpg; as larguras da MIL-STD-1913, do tubo militar, da
# planta do receptor inferior e das deduções da ficha. Lado direito da arma = -Y do Blender; a primeira pessoa mostra o
# esquerdo (+Y). Aqui: os receptores, a alavanca de manejo, a tampa da janela e o transportador, os comandos, o punho,
# o guarda-mato, o gatilho, o carregador, a alça com a mira traseira, a coronha aberta e o tubo; a frente em
# m4a4_frente.py. Marcações genéricas (regra 9): as posições do seletor, o calibre e um número de série.
import math

from . import m4a4_frente as FRENTE
from . import pecas as P
from . import pecas_superficie as PS

ORIGEM_MM = (-504.0, 0.0)  # o pino do gatilho no eixo do cano: a origem da arma no jogo (como a AK)
PECAS = ('ferrolho', 'alavanca', 'tampa', 'carregador', 'gatilho', 'seletor')
PERTO_MM = (-470.0, 5.0)  # a vista de perto da conferência: a janela de ejeção, o assistente e o defletor
OLHO_M = (-0.75, 0.11, 0.09)  # o olho da vista de primeira pessoa da conferência (m), atrás e à esquerda da alça
Y_DIVISA = -8.5  # a divisa dos receptores (linhas.divisaReceptores)
X_TRAS_SUP, X_FRENTE_REC = -583.0, -386.8
X_TRILHO = -568.0  # o começo do trilho do receptor (o fim de trás, na trava da alavanca)


def pivos(ficha):
    """Pivô (mm, ficha; com o lado quando fora do meio) e extras de cada peça (direções no referencial do jogo: +X boca,
    +Y cima, +Z direita)."""
    pt = ficha['pontos']
    face = -ficha['vistaDeCima']['larguras']['receptorSuperior']['mm'] / 2 - 1.0
    return {
        'base': (ORIGEM_MM, {}),
        'ferrolho': ((-522.0, 0.0), {'eixo': [-1.0, 0.0, 0.0]}),
        'alavanca': ((X_TRAS_SUP - 8.0, 17.0), {'eixo': [-1.0, 0.0, 0.0]}),
        # a tampa gira na dobradiça de baixo, na face direita
        'tampa': ((sum(pt['tampa']['x']) / 2, pt['dobradica']['y'], face), {'eixo_giro': [1.0, 0.0, 0.0]}),
        # o carregador sai reto para baixo pelo poço
        'carregador': (tuple(pt['travaCarregador']), {'eixo': [0.0, -1.0, 0.0]}),
        'gatilho': (tuple(pt['pinoGatilho']), {'eixo_giro': [0.0, 0.0, 1.0]}),
        'seletor': (tuple(pt['eixoSeletor']), {'eixo_giro': [0.0, 0.0, 1.0]}),
    }


def soquetes(ficha):
    """(nome, (x, y) da ficha, lado = Y do Blender em mm, rotação XYZ em graus no Blender)."""
    pt = ficha['pontos']
    tp = pt['tampa']
    face = -ficha['vistaDeCima']['larguras']['receptorSuperior']['mm'] / 2
    a = pt['anguloPunho']
    return [
        ('boca', (0.0, 0.0), 0.0, (0, 0, 0)),
        # a cápsula sai pela janela da direita, para a frente e para cima (como na AK)
        ('ejecao', (sum(tp['x']) / 2, sum(tp['y']) / 2), face, (0, -15, -75)),
        ('carregador', tuple(pt['travaCarregador']), 0.0, (0, 0, 0)),
        ('mira_tras', tuple(pt['miraTras']), 0.0, (0, 0, 0)),
        ('mira_frente', tuple(pt['massaDeMira']), 0.0, (0, 0, 0)),
        # o +Z do soquete (o +Y no jogo) sobe pelo eixo do punho, inclinado para trás
        ('mao_d', (-576.0, -95.0), 0.0, (0, a, 0)),
        ('mao_e', (-290.0, pt['trilhoGuardaMao']['fundo']), 0.0, (0, 0, 0)),
    ]


# ------------------------------------------------------------------------------------------------ receptor superior
def _receptor_superior(ficha, M):
    """O receptor superior de alumínio: o perfil da foto até a base do trilho, o trilho MIL-STD-1913 com as fendas no
    passo da foto, a janela de ejeção (o vão atrás da tampa), o assistente de fechamento e o defletor de cápsulas."""
    pc, pt, L = ficha['pecas'], ficha['pontos'], ficha['vistaDeCima']['larguras']
    corpo, det = M['corpo'], M['detalhes']
    ls = L['receptorSuperior']['mm'] / 2
    topo = pt['trilho']['topo']
    h = PS.PICATINNY['alturaMinima']
    sup = P.prisma('receptor superior', pc['receptorSuperior'], 'XZ', -ls, ls, corpo, 'corpo', chanfro=1.0)
    # o alto sai do perfil e volta como o trilho da norma (os dentes da foto têm a escada de pixels)
    P.cortar(sup, P.caixa('alto do receptor', (X_TRILHO, -ls - 2, topo - h + 0.4), (X_FRENTE_REC + 1, ls + 2, topo + 5.0), corpo, 'corpo',
                          chanfro=0))
    # as fendas onde a foto da PEO as mostra (o passo dela), completadas para trás, embaixo da alça
    PS.trilho_picatinny('trilho do receptor', X_TRILHO, X_FRENTE_REC, corpo, 'corpo', 'base', z=topo, altura=h + 0.8,
                        fendas=list(pt['trilho']['fendas']))
    # a janela de ejeção: o vão atrás da tampa, com o transportador no fundo
    tp = pt['tampa']
    P.cortar(sup, P.caixa('janela de ejeção', (tp['x'][0] + 2.0, -ls - 2.0, tp['y'][0] + 1.5), (tp['x'][1] - 2.0, -ls + 7.0, tp['y'][1] - 1.5),
                          corpo, 'corpo', chanfro=0))
    # o assistente de fechamento: a caixa inclinada na traseira direita e o botão de trás
    a = pt['assistente']
    (xt, zt), (xf, zf) = a['centro'], a['ate']
    comp = math.hypot(xf - xt, zf - zt)
    ang = math.degrees(math.atan2(zt - zf, xf - xt))
    ya = -ls - 3.0
    caixa_af = P.torno('caixa do assistente', [(0, 0), (0, a['raio'] + 1.0), (comp - 3.0, a['raio'] + 1.0), (comp, a['raio'] - 1.0), (comp, 0)],
                       corpo, 'corpo', seg=28, centro=(xt, ya, zt), chanfro=0.6)
    botao = P.torno('botão do assistente', [(-6.0, 0), (-6.0, a['raio'] - 1.2), (-5.2, a['raio']), (0.5, a['raio']), (0.5, 0)], det,
                    'detalhes', seg=28, centro=(xt, ya, zt), chanfro=0.4)
    for ob in (caixa_af, botao):
        P.rotacionar(ob, 'Y', ang, (xt, ya, zt))
    for k in range(10):  # as estrias do botão (só no alto)
        g = P.caixa('estria do assistente', (xt - 6.5, ya - 0.35, zt + a['raio'] - 0.6), (xt - 0.8, ya + 0.35, zt + a['raio'] + 1.0), det,
                    'detalhes', chanfro=0, so_alto=True)
        if g is not None:
            P.rotacionar(g, 'X', k * 36.0, (0, ya, zt))
            P.rotacionar(g, 'Y', ang, (xt, ya, zt))
            P.cortar(botao, g)
    # o defletor de cápsulas atrás da janela
    P.prisma('defletor', pt['defletor'], 'XZ', -ls - 6.0, -ls + 1.0, corpo, 'corpo', chanfro=1.2)
    return sup, ls


def _alavanca(ficha, M, ls):
    """A alavanca de manejo (peça móvel): o T atrás do receptor, a trava à esquerda do T (a cauda sobe acima do trilho) e
    a haste por baixo do trilho."""
    pc = ficha['pecas']
    corpo = M['corpo']
    t = pc['alavancaTras']
    P.prisma('alavanca de manejo', t, 'XZ', -19.0, 19.0, corpo, 'corpo', 'alavanca', chanfro=1.0)
    zs = [p[1] for p in t]
    P.caixa('haste da alavanca', (X_TRAS_SUP - 1.0, -4.5, min(zs) + 1.0), (-470.0, 4.5, max(zs) - 1.0), corpo, 'corpo', 'alavanca',
            chanfro=0.5)
    P.prisma('trava da alavanca', pc['trava'], 'XZ', 3.0, 15.0, corpo, 'corpo', 'alavanca', chanfro=0.6)


def _tampa_e_ferrolho(ficha, M, ls):
    """A tampa da janela (chapa de aço com o trinco e a borda enrolada na dobradiça; peça móvel) e o transportador do
    ferrolho (aço polido, peça móvel) que aparece pela janela quando ela abre; a haste da dobradiça fica na base."""
    pt = ficha['pontos']
    det, interno = M['detalhes'], M['interno']
    tp, db, tr = pt['tampa'], pt['dobradica'], pt['trincoTampa']
    face = -ls
    P.caixa('tampa da janela', (tp['x'][0], face - 1.4, tp['y'][0] + 1.2), (tp['x'][1], face + 0.2, tp['y'][1]), det, 'detalhes', 'tampa',
            chanfro=0.4)
    P.caixa('trinco da tampa', (tr['x'][0], face - 2.4, tr['y'][0]), (tr['x'][1], face - 1.2, tr['y'][1]), det, 'detalhes', 'tampa',
            chanfro=0.3)
    P.torno('borda da tampa', [(tp['x'][0], 0), (tp['x'][0], db['raio'] + 0.6), (tp['x'][1], db['raio'] + 0.6), (tp['x'][1], 0)], det,
            'detalhes', 'tampa', seg=16, centro=(0, face - 1.0, db['y']), chanfro=0.2)
    P.torno('dobradiça', [(db['x'][0], 0), (db['x'][0], db['raio']), (db['x'][1], db['raio']), (db['x'][1], 0)], det, 'detalhes', seg=12,
            centro=(0, face - 1.0, db['y']), chanfro=0.2)
    car = P.torno('transportador', [(-522.0, 0), (-522.0, 12.0), (-404.0, 12.0), (-402.0, 8.5), (-392.0, 8.5), (-392.0, 0)], interno,
                  'interno', 'ferrolho', seg=32, chanfro=0.5)
    # o rebaixo do transportador na frente (a faixa lisa por onde a cápsula passa)
    P.cortar(car, P.caixa('rebaixo do transportador', (-470.0, -14.0, 2.0), (-430.0, -10.5, 11.0), interno, 'interno', 'ferrolho', chanfro=0))


# ------------------------------------------------------------------------------------------------ receptor inferior
def _receptor_inferior(ficha, M):
    """O receptor inferior de alumínio: o perfil da foto na largura do corpo, o poço do carregador mais largo, a cerca
    e o botão do retém do carregador (direita), o retém do ferrolho (esquerda), os pinos de desmontagem, do gatilho e do
    cão, o eixo do seletor, as marcações das posições e o guarda-mato."""
    pc, pt, L = ficha['pecas'], ficha['pontos'], ficha['vistaDeCima']['larguras']
    corpo, det = M['corpo'], M['detalhes']
    li = L['receptorInferior']['mm'] / 2
    lp = L['poco']['mm'] / 2
    inf = P.prisma('receptor inferior', pc['receptorInferior'], 'XZ', -lp, lp, corpo, 'corpo', chanfro=1.0)
    mx0 = pt['magwell']['x'][0]
    for s in (-1, 1):
        y0, y1 = sorted((s * li, s * (lp + 3.0)))
        # atrás do poço o receptor tem a largura do corpo; o poço vai até a divisa com a largura dele (o degrau à vista)
        P.cortar(inf, P.caixa('largura do receptor inferior', (-600.0, y0, -90.0), (mx0, y1, 30.0), corpo, 'corpo', chanfro=0))
    for b in ficha['buracos']:
        bx = [p[0] for p in b]
        by = [p[1] for p in b]
        if min(bx) > -530 and max(bx) < -460 and max(by) < -40:
            P.cortar(inf, P.prisma('vão do guarda-mato', b, 'XZ', -lp - 2, lp + 2, corpo, 'corpo', chanfro=0))
    # o botão do retém do carregador na cerca redonda (direita)
    br = pt['botaoRetem']
    bx, bz = br['centro']
    P.pino('cerca do retém', bx, bz, br['anel'], corpo, 'corpo', lado=-1, de=lp - 0.5, ate=lp + 1.6)
    P.cortar(inf, P.pino('vão do botão', bx, bz, br['raio'] + 0.5, corpo, 'corpo', lado=-1, de=lp - 1.5, ate=lp + 3.0))
    botao = P.pino('botão do retém', bx, bz, br['raio'], det, 'detalhes', lado=-1, de=lp - 1.5, ate=lp + 2.4)
    for k in range(4):
        P.cortar(botao, P.caixa('estria do botão', (bx - br['raio'] - 1, -lp - 3.0, bz - 2.4 + k * 1.6), (bx + br['raio'] + 1, -lp - 2.1,
                                                                                                     bz - 2.0 + k * 1.6), det,
                                'detalhes', chanfro=0, so_alto=True))
    # o retém do ferrolho (esquerda): a pá com as estrias
    rf = pt['retemFerrolho']
    pa = P.prisma('retém do ferrolho', P.ret_arredondado(rf['x'][0], rf['x'][1], rf['y'][0], rf['y'][1], 2.0, 4), 'XZ', li - 0.5, li + 2.4, det,
                  'detalhes', chanfro=0.4)
    for k in range(5):
        z = rf['y'][0] + 3.0 + k * 1.4
        P.cortar(pa, P.caixa('estria do retém', (rf['x'][0] - 1, li + 2.0, z), (rf['x'][1] + 1, li + 3.0, z + 0.5), det, 'detalhes', chanfro=0,
                             so_alto=True))
    # os pinos: a cabeça dos de desmontagem à esquerda, a ponta à direita; o do gatilho e o do cão dos dois lados
    for chave in ('pinoTras', 'pinoFrente'):
        (x, z), r = pt[chave]['centro'], pt[chave]['raio']
        face = lp if chave == 'pinoFrente' else li
        P.pino(f'cabeça do {chave}', x, z, r, det, 'detalhes', lado=1, de=face - 0.4, ate=face + 0.9)
        P.pino(f'ponta do {chave}', x, z, r - 0.6, det, 'detalhes', lado=-1, de=face - 0.4, ate=face + 0.3)
    for chave in ('pinoGatilho', 'pinoCao'):
        x, z = pt[chave]
        for s in (-1, 1):
            P.pino(chave, x, z, 2.0, det, 'detalhes', lado=s, de=li - 0.4, ate=li + 0.25)
    hx, hz = pt['eixoSeletor']
    P.pino('ponta do seletor', hx, hz, 3.6, det, 'detalhes', 'seletor', lado=-1, de=li - 0.4, ate=li + 0.6)
    # as marcações das posições do seletor (os dois lados), o calibre e o número de série à esquerda do poço
    for face, plano in (('esquerda', li), ('direita', -li)):
        tras = -1 if face == 'esquerda' else 1  # na esquerda o texto corre para -X
        P.gravacao('SAFE', 'SAFE', hx + (14.0 if face == 'direita' else 25.0), hz - 1.2, 2.6, face, plano, 0.2, inf)
        P.gravacao('SEMI', 'SEMI', hx - 3.8 * tras, hz + 6.5, 2.6, face, plano, 0.2, inf)
        P.gravacao('AUTO', 'AUTO', hx - (22.0 if face == 'direita' else 11.0), hz - 1.2, 2.6, face, plano, 0.2, inf)
    P.gravacao('calibre', 'CAL 5.56 MM', -408.0, -22.0, 2.4, 'esquerda', lp, 0.2, inf)
    P.gravacao('número de série', 'W284713', -410.0, -30.0, 2.4, 'esquerda', lp, 0.2, inf)
    # o guarda-mato de alavanca e o pino de trava dele na frente
    lg = L['guardaMato']['mm'] / 2
    P.prisma('guarda-mato', pc['guardaMato'], 'XZ', -lg, lg, corpo, 'corpo', chanfro=1.0)
    gx = max(p[0] for p in pc['guardaMato'])
    for s in (-1, 1):
        P.pino('pino do guarda-mato', gx - 3.0, -70.5, 1.4, det, 'detalhes', lado=s, de=lg - 0.3, ate=lg + 0.3)
    return inf, li


def _seletor(ficha, M, li):
    """A alavanca do seletor (peça móvel) no lado esquerdo, em SAFE (apontando para a frente), com o cubo redondo."""
    pt = ficha['pontos']
    det = M['detalhes']
    hx, hz = pt['eixoSeletor']
    s = pt['seletor']
    P.pino('cubo do seletor', hx, hz, 4.6, det, 'detalhes', 'seletor', lado=1, de=li - 0.4, ate=li + 2.2)
    alav = P.prisma('alavanca do seletor', P.ret_arredondado(hx - 3.0, hx + s['comprimento'], hz - s['largura'] / 2, hz + s['largura'] / 2,
                                                             s['largura'] / 2 - 0.4, 4), 'XZ', li + 1.4, li + 3.2, det, 'detalhes', 'seletor',
                    chanfro=0.4)
    for k in range(4):  # as estrias da ponta
        x = hx + s['comprimento'] - 2.5 - k * 1.5
        P.cortar(alav, P.caixa('estria do seletor', (x - 0.3, li + 2.9, hz - s['largura']), (x + 0.3, li + 4.0, hz + s['largura']), det,
                               'detalhes', 'seletor', chanfro=0, so_alto=True))
    # a seta do cubo (o indicador de posição), gravada
    P.cortar(alav, P.caixa('seta do seletor', (hx + 1.0, li + 2.9, hz - 0.3), (hx + 5.0, li + 4.0, hz + 0.3), det, 'detalhes', 'seletor',
                           chanfro=0, so_alto=True))


def _gatilho(ficha, M):
    pc, L = ficha['pecas'], ficha['vistaDeCima']['larguras']
    lg = L['gatilho']['mm'] / 2
    P.prisma('gatilho', pc['gatilho'], 'XZ', -lg, lg, M['detalhes'], 'detalhes', 'gatilho', chanfro=0.6)


def _punho(ficha, M):
    """O punho A2 de polímero: o perfil da foto arredondado (o chanfro largo) e o painel quadriculado dos dois lados (o
    relevo das pirâmides, só no modelo alto)."""
    pc, pt, L = ficha['pecas'], ficha['pontos'], ficha['vistaDeCima']['larguras']
    pol = M['guarnicao']
    lp = L['punho']['mm'] / 2
    punho = P.prisma('punho', P.simplificar(pc['punho']), 'XZ', -lp, lp, pol, 'guarnicao', chanfro=5.0, seg=4)
    painel = pt['painelPunho']
    xs = [p[0] for p in painel]
    zs = [p[1] for p in painel]
    grade = PS.piramides(1.3, 0.4)

    def no_painel(u, v):
        n = len(painel)
        dentro = False
        for k in range(n):
            (ax, ay), (bx, by) = painel[k], painel[(k + 1) % n]
            if (ay > v) != (by > v) and u < ax + (v - ay) / (by - ay) * (bx - ax):
                dentro = not dentro
        return grade(u, v) if dentro else None
    for s in (-1, 1):
        PS.relevo('quadriculado do punho', punho, (min(xs) - 1, max(xs) + 1), (min(zs), max(zs)), 0.13,
                  lambda u, v, s=s: ((u, s * (lp + 20.0), v), (0, -s, 0)), no_painel)
    return punho


def _carregador(ficha, M):
    """O carregador de 30 de alumínio: o perfil da foto na largura dele, as duas nervuras estampadas dos lados, a base
    mais larga e o alto que entra no poço (escondido, para a recarga)."""
    pc, pt, ln, L = ficha['pecas'], ficha['pontos'], ficha['linhas'], ficha['vistaDeCima']['larguras']
    mat = M['carregador']
    lc = L['carregador']['mm'] / 2
    P.prisma('carregador', P.simplificar(pc['carregador']), 'XZ', -lc, lc, mat, 'carregador', 'carregador', chanfro=1.0)
    for nome in ('nervuraCarregador1', 'nervuraCarregador2'):
        for s in (-1, 1):
            a, b = sorted((s * (lc - 0.2), s * (lc + 0.7)))
            P.tira(nome, ln[nome], 3.2, 'XZ', a, b, mat, 'carregador', 'carregador', chanfro=0.3)
    # a base: a faixa de baixo do perfil (inclinada como a do carregador curvo), mais larga que o corpo
    P.prisma('base do carregador', pc['baseCarregador'], 'XZ', -lc - 1.3, lc + 1.3, mat, 'carregador', 'carregador', chanfro=1.2)
    mx = pt['magwell']['x']
    P.caixa('alto do carregador', (mx[0] + 4.0, -lc + 0.4, -60.0), (mx[1] - 4.0, lc - 0.4, Y_DIVISA - 6.0), mat, 'carregador', 'carregador',
            chanfro=0.8)


# ------------------------------------------------------------------------------------------------ alça, coronha e tubo
def _alca(ficha, M):
    """A alça de transporte de alumínio: o perfil da foto na largura dela com a janela; a mira traseira A2 (as orelhas
    com o vão, a chapa da abertura com o furo pequeno, o tambor de deriva à direita e o de elevação embaixo) e o
    parafuso do grampo à esquerda."""
    pc, pt, L = ficha['pecas'], ficha['pontos'], ficha['vistaDeCima']['larguras']
    corpo, det = M['corpo'], M['detalhes']
    la = L['alca']['mm'] / 2
    lm = L['miraTras']['mm'] / 2
    alca = P.prisma('alça de transporte', pc['alca'], 'XZ', -la, la, corpo, 'corpo', chanfro=1.2)
    xa = [p[0] for p in pc['alca']]
    for b in ficha['buracos']:
        bx = [p[0] for p in b]
        by = [p[1] for p in b]
        if min(bx) >= min(xa) - 1 and max(bx) <= max(xa) + 1 and min(by) > 35:
            P.cortar(alca, P.prisma('janela da alça', b, 'XZ', -la - 2, la + 2, corpo, 'corpo', chanfro=0))
    mt = pt['miraTras']
    td = pt['tamborDeriva']
    x0, x1 = td['centro'][0] - 12.0, td['centro'][0] + 12.0
    for s in (-1, 1):  # a mira é mais estreita que a alça
        y0, y1 = sorted((s * lm, s * (la + 3.0)))
        P.cortar(alca, P.caixa('largura da mira', (x0, y0, 56.0), (x1, y1, 90.0), corpo, 'corpo', chanfro=0))
    P.cortar(alca, P.caixa('vão das orelhas', (mt[0] - 5.0, -4.6, mt[1] + 2.5), (mt[0] + 5.0, 4.6, 90.0), corpo, 'corpo', chanfro=0))
    chapa = P.caixa('abertura', (mt[0] - 1.4, -4.4, mt[1] - 5.0), (mt[0] + 1.4, 4.4, mt[1] + 4.0), det, 'detalhes', chanfro=0.3)
    P.cortar(chapa, P.torno('furo da abertura', [(mt[0] - 3, 0), (mt[0] - 3, 0.9), (mt[0] + 3, 0.9), (mt[0] + 3, 0)], det, 'detalhes', seg=16,
                            centro=(0, 0, mt[1])))
    cx, cz = td['centro']
    tambor = P.pino('tambor de deriva', cx, cz, td['raio'], det, 'detalhes', lado=-1, de=lm - 0.5, ate=lm + 3.2)
    for k in range(18):  # o serrilhado do tambor (só no alto)
        g = P.caixa('serrilha do tambor', (cx - 0.35, -lm - 3.6, cz + td['raio'] - 0.5), (cx + 0.35, -lm - 0.2, cz + td['raio'] + 1.0), det,
                    'detalhes', chanfro=0, so_alto=True)
        if g is not None:
            P.rotacionar(g, 'Y', k * 20.0, (cx, 0, cz))
            P.cortar(tambor, g)
    P.torno('tambor de elevação', [(46.0, 0), (46.0, la + 0.8), (54.0, la + 0.8), (54.0, 0)], det, 'detalhes', seg=36, eixo='Z',
            centro=(cx, 0, 0), chanfro=0.4)
    # o grampo: o parafuso de mão na frente da base, à esquerda
    xf = max(xa)
    P.pino('parafuso do grampo', xf - 14.0, 38.0, 5.5, det, 'detalhes', lado=1, de=la - 0.5, ate=la + 6.0)
    P.pino('ponta do grampo', xf - 14.0, 38.0, 3.0, det, 'detalhes', lado=-1, de=la - 0.5, ate=la + 1.0)
    return alca


def _coronha_e_tubo(ficha, M):
    """A coronha retrátil de polímero, aberta: o perfil da foto (mais estreita na alavanca da trava, embaixo), as duas
    fendas da bandoleira atrás e o pino da trava; o tubo do amortecedor e a porca castelo na placa do receptor."""
    pc, pt, tn, L = ficha['pecas'], ficha['pontos'], ficha['tornos'], ficha['vistaDeCima']['larguras']
    pol, corpo, det = M['guarnicao'], M['corpo'], M['detalhes']
    lc = L['coronha']['mm'] / 2
    cor = P.prisma('coronha', P.simplificar(pc['coronha']), 'XZ', -lc, lc, pol, 'guarnicao', chanfro=2.0, seg=3)
    # A seção: na frente da soleira, o alto é a luva redonda em volta do tubo (o meio dela no eixo do tubo, um pouco
    # acima) e embaixo o braço da trava, chato e mais estreito; a soleira de trás tem a largura toda. Os laços do
    # fatiar dão vértices ao afinamento.
    soleira = min(p[0] for p in pc['coronha']) + 42.0  # a frente da soleira (a parte alta de trás)
    alto_luva = max(p[1] for p in pc['coronha'] if p[0] > soleira + 10.0)
    fundo_luva = -18.5  # onde a luva encontra o braço da trava (a foto da NSWC)
    meio, raio = (alto_luva + fundo_luva) / 2, (alto_luva - fundo_luva) / 2

    def secao(x, z):
        luva = math.sqrt(max(0.0, 1.0 - ((z - meio) / raio) ** 2))
        largura = max(luva, 0.5 if z < -5.0 else 0.0, 0.3)
        t = min(1.0, max(0.0, (x - soleira) / 10.0))
        return 1.0 + (largura - 1.0) * t
    P.fatiar(cor, 'Z', [-16.0, -12.0, -8.0, -4.0, 0.0, 4.0, 8.0, 12.0, 16.0, 19.0, 22.0])
    P.fatiar(cor, 'X', [soleira, soleira + 5.0, soleira + 10.0])
    P.afinar(cor, secao)
    for b in ficha['buracos']:
        if max(p[0] for p in b) < pt['frenteDaCoronha']:
            P.cortar(cor, P.prisma('fenda da bandoleira', b, 'XZ', -lc - 2, lc + 2, pol, 'guarnicao', chanfro=0))
    tr = pt['travaCoronha']
    for s in (-1, 1):
        P.pino('pino da trava', tr['centro'][0], tr['centro'][1], tr['raio'], det, 'detalhes', lado=s, de=lc * 0.5 - 0.5,
               ate=lc * 0.5 + 0.8)
    P.torno('tubo do amortecedor', tn['tubo']['perfil'], corpo, 'corpo', seg=40, chanfro=0.4)
    porca = P.torno('porca castelo', tn['porca']['perfil'], det, 'detalhes', seg=40, chanfro=0.4)
    for k in range(3):  # os entalhes da porca (a chave)
        e = P.caixa('entalhe da porca', (-597.5, -2.0, 13.0), (-594.0, 2.0, 18.0), det, 'detalhes', chanfro=0)
        P.rotacionar(e, 'X', 60.0 + k * 120.0, (0, 0, 0))
        P.cortar(porca, e)


def construir(ficha, M):
    """Todas as peças no nível atual (pecas.iniciar). M = materiais de fábrica por zona (materiais.materiais_de_fabrica)."""
    _sup, ls = _receptor_superior(ficha, M)
    _alavanca(ficha, M, ls)
    _tampa_e_ferrolho(ficha, M, ls)
    _inf, li = _receptor_inferior(ficha, M)
    _seletor(ficha, M, li)
    _gatilho(ficha, M)
    _punho(ficha, M)
    _carregador(ficha, M)
    _alca(ficha, M)
    _coronha_e_tubo(ficha, M)
    FRENTE.construir(ficha, M)
