# Baioneta M9 (EUA, 1986), a faca do jogo — Fase 4.1c (desenho em docs/superpowers/specs/2026-09-28-4.1c-glock-m4a4-m9-
# design.md, seção 3.3). Construída em mm no referencial da ficha (tools/blender/refs/knife.json; plano da 4.1c, D4): a
# ponta da lâmina em x = 0, o eixo do cabo em y = 0, o dorso para +Y; no Blender X = x, Z = y e a espessura no Y. O
# contorno da foto "US Military M9 Bajonett COMPO.jpg" pela máscara de cor; a lâmina por seções com o gume (a biblioteca,
# pecas_superficie.lamina), o contrafio do clip, a serrilha do dorso, o sulco e o furo do corta-arame; a guarda com a
# argola da boca do cano; o cabo redondo com os anéis e o quadriculado; o pomo com a trava e a fenda do ressalto.
# Marcações genéricas (regra 9): o país e o lote, nada do fabricante.
import math

from . import pecas as P
from . import pecas_superficie as PS

PECAS = ()  # a faca é uma peça só (a base)
PERTO_MM = (-165.0, 5.0)  # a vista de perto da conferência: o ricasso, a serrilha e a guarda
OLHO_M = (-0.45, 0.10, 0.12)  # o olho da vista de primeira pessoa da conferência (m)
FIO = 0.5  # a largura do fio do gume (mm)
SEG_TORNO = 32  # lados do cabo, do pomo e da argola: com 48 o perto passava do orçamento da faca (9 506 de 8 000)
ORIGEM_MM = (-177.6, 0.0)  # a frente da guarda no eixo do cabo (plano da 4.1c, D4; a ficha, pontos.origem)


def pivos(_ficha):
    return {'base': (ORIGEM_MM, {})}


def soquetes(ficha):
    """(nome, (x, y) da ficha, lado = Y do Blender em mm, rotação XYZ em graus no Blender): a mão no meio do cabo, com o
    +Z (o +Y no jogo) para o dorso; a ponta da lâmina (o golpe da 4.6)."""
    pt = ficha['pontos']
    return [
        ('mao_d', tuple(pt['mao']), 0.0, (0, 0, 0)),
        ('ponta', tuple(pt['ponta']), 0.0, (0, 0, 0)),
    ]


# ------------------------------------------------------------------------------------------------ contas
def _na_linha(pts, x):
    """Valor em x de uma polilinha [(x, valor)] ordenada por x, presa nas pontas."""
    if x <= pts[0][0]:
        return pts[0][1]
    for (xa, a), (xb, b) in zip(pts, pts[1:]):
        if x <= xb:
            return a + (b - a) * (x - xa) / (xb - xa)
    return pts[-1][1]


def _estacoes(ficha):
    """As seções da lâmina, da frente da guarda à ponta: o ricasso sem gume (o fio da espessura toda), o começo do gume
    no degrau de baixo, o trecho reto com o dorso da serrilha e o bisel na altura da foto, e o clip — o dorso descendo
    pelo contrafio afiado, a espessura afinando e o bisel fechando na ponta."""
    pt = ficha['pontos']
    L = ficha['vistaDeCima']['larguras']
    e = L['lamina']['mm']
    ric, dorso, clip = pt['ricasso'], pt['dorso'], pt['clip']['x']
    gume, contra, bisel = pt['gume'], pt['contrafio'], pt['bisel']
    x0 = ORIGEM_MM[0]
    xs = [x0, x0 + 0.8, ric['degrau'] - 0.6, ric['degrau'] + 0.6, ric['x'][1], -150.0]
    xs += list(range(-140, int(clip), 10)) + [clip]
    xs += [-70.0, -65.0, -60.0, -55.0, -50.0, -45.0, -40.0, -35.0, -30.0, -25.0, -20.0, -15.0, -11.0, -8.0, -5.5, -3.5, -2.0]
    est = []
    for x in xs:
        if x < ric['degrau']:
            zd = ric['altoRicasso']
        elif x < clip:
            zd = dorso
        else:
            zd = _na_linha(contra, x)
        if x <= ric['x'][1]:
            zf = ric['baixoRicasso']
        else:
            zf = _na_linha(gume, x)
        # o gume nasce no degrau de baixo do ricasso (o fio vai da espessura toda a FIO)
        t_gume = min(1.0, max(0.0, (x - ric['x'][1]) / 5.0))
        ff = e + (FIO - e) * t_gume
        # a espessura afina no clip até ~1/4 na ponta; o bisel do gume tem a altura da foto no trecho reto e encolhe na
        # ponta, sem passar da metade da altura da lâmina ali
        t_ponta = min(1.0, max(0.0, (x - clip) / (0.0 - clip)))
        ex = e * (1.0 - 0.72 * t_ponta)
        altura = zd - zf
        if t_gume > 0:
            zb = zf + min((bisel - _na_linha(gume, -100.0)) * (1.0 - 0.75 * t_ponta), 0.55 * altura)
        else:
            zb = zf + 1.2
        if x < clip:
            fd, zbd = ex, zd - 0.8  # o dorso reto, de quina quebrada
        else:
            fd = 0.6  # o contrafio afiado do clip
            zbd = max(zb + 0.1 * altura, zd - min(4.0, 0.3 * altura))
        est.append((x, zd, zbd, zb, zf, min(ex, e), min(fd, ex), min(ff, ex)))
    est.append(tuple(pt['ponta']))
    return est


# ------------------------------------------------------------------------------------------------ partes
def _lamina(ficha, M):
    """A lâmina (aço com o revestimento preto): as seções com o gume, os dentes da serrilha cortados no dorso reto, o
    sulco dos dois lados, o furo do corta-arame e as marcações do ricasso."""
    pt = ficha['pontos']
    L = ficha['vistaDeCima']['larguras']
    mat = M['corpo']
    e = L['lamina']['mm']
    lam = PS.lamina('lamina', _estacoes(ficha), mat, 'corpo', chanfro=(0.15, 2))
    # a serrilha: o que fica acima do contorno dos dentes sai do dorso
    s = pt['serrilha']
    base = pt['dorso'] - s['altura']
    dentes = PS.dentes([(s['x'][0], base), (s['x'][1], base)], s['passo'], s['altura'])
    corte = [(s['x'][0], pt['dorso'] + 5.0), *dentes, (s['x'][1], pt['dorso'] + 5.0)]
    P.cortar(lam, P.prisma('serrilha do dorso', corte, 'XZ', -e, e, mat, 'corpo', chanfro=0))
    # o sulco: o canal raso dos dois lados, de pontas redondas
    su = pt['sulco']
    (x0, x1), (z0, z1) = su['x'], su['y']
    canal = P.ret_arredondado(x0, x1, z0, z1, (z1 - z0) / 2 - 0.01, 6)
    for lado in (-1, 1):
        a, b = sorted((lado * (e / 2 - su['profundidade']), lado * (e / 2 + 2.0)))
        P.cortar(lam, P.prisma('sulco', canal, 'XZ', a, b, mat, 'corpo', chanfro=0))
    # o furo do corta-arame: o contorno da máscara sem a escada de pixels (simplificado e arredondado)
    for b in ficha['buracos']:
        P.cortar(lam, P.prisma('furo do corta-arame', P.suavizar(P.simplificar(b, 0.2, 0.8), 2), 'XZ', -e, e, mat, 'corpo', chanfro=0))
    P.gravacao('país', 'U.S.A.', -171.0, -2.0, 2.8, 'direita', -e / 2, 0.12, lam)
    P.gravacao('lote', '0188', -168.0, -6.5, 2.4, 'direita', -e / 2, 0.12, lam)
    return lam


def _guarda(ficha, M):
    """A guarda de aço pintada: a chapa de baixo e em volta da lâmina (na largura da guarda) e a argola da boca do cano
    em cima (o anel de 22 mm de dentro para o quebra-chamas)."""
    pc, pt, L = ficha['pecas'], ficha['pontos'], ficha['vistaDeCima']['larguras']
    det = M['detalhes']
    lg = L['guarda']['mm'] / 2
    ag = pt['argola']
    chapa = P.prisma('guarda', P.simplificar(pc['guarda']), 'XZ', -lg, lg, det, 'detalhes', chanfro=0.8)
    xs = [p[0] for p in pc['guarda']]
    P.cortar(chapa, P.caixa('alto da guarda', (min(xs) - 1, -lg - 2, ag['centroY'] - ag['raio'] + 0.6), (max(xs) + 1, lg + 2, 80.0), det,
                            'detalhes', chanfro=0))
    x0, x1 = min(xs), max(xs)
    P.torno('argola', [(x0, ag['raioInterno']), (x0, ag['raio']), (x1, ag['raio']), (x1, ag['raioInterno']), (x0, ag['raioInterno'])], det,
            'detalhes', seg=SEG_TORNO, centro=(0, 0, ag['centroY']), chanfro=0.6)


def _cabo(ficha, M):
    """O cabo de polímero: o torno da ficha (o inchaço de trás, o pescoço, os cinco anéis) e o quadriculado dos
    segmentos (o relevo das pirâmides em volta do cilindro, só no modelo alto)."""
    tn, pt = ficha['tornos'], ficha['pontos']
    cabo = P.torno('cabo', tn['cabo']['perfil'], M['guarnicao'], 'guarnicao', seg=SEG_TORNO, chanfro=0.4)
    perfil = tn['cabo']['perfil']
    aneis = pt['aneisCabo']
    pescoco = pt['pescoco']
    grade = PS.piramides(1.1, 0.3)
    r_med = 14.0

    def no_segmento(u, v):
        if any(abs(u - a) < 2.6 for a in aneis) or pescoco[0] - 1.0 <= u <= pescoco[1] + 1.0 or u > aneis[-1] - 2.6:
            return None
        return grade(u, v)

    def raio(u, v):
        ang = v / r_med
        return ((u, (r_med + 20.0) * math.sin(ang), (r_med + 20.0) * math.cos(ang)), (0.0, -math.sin(ang), -math.cos(ang)))
    x0 = perfil[0][0] + 1.0
    PS.relevo('quadriculado do cabo', cabo, (x0, aneis[-1]), (0.0, 2 * math.pi * r_med), 0.12, raio, no_segmento)
    return cabo


def _pomo(ficha, M):
    """O pomo de aço pintado: o torno da ficha, a trava de mola em cima (a alavanca que solta a baioneta do ressalto) e a
    fenda do ressalto no alto de trás."""
    tn, pt = ficha['tornos'], ficha['pontos']
    det = M['detalhes']
    pomo = P.torno('pomo', tn['pomo']['perfil'], det, 'detalhes', seg=SEG_TORNO, chanfro=0.5)
    tr = pt['trava']
    lt = tr['largura'] / 2
    P.caixa('trava do pomo', (tr['x'][0], -lt, tr['y'][0]), (tr['x'][1], lt, tr['y'][1]), det, 'detalhes', chanfro=0.4)
    fp = pt['fendaPomo']
    lf = fp['largura'] / 2
    P.cortar(pomo, P.caixa('fenda do ressalto', (fp['x'][0] - 1.0, -lf, fp['y'][0]), (fp['x'][1], lf, fp['y'][1] + 3.0), det, 'detalhes',
                           chanfro=0))
    return pomo


def construir(ficha, M):
    """A faca inteira no nível atual (pecas.iniciar). M = materiais de fábrica por zona."""
    _lamina(ficha, M)
    _guarda(ficha, M)
    _cabo(ficha, M)
    _pomo(ficha, M)
