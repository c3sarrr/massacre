# Glock 18 de 3ª geração, sem compensador — Fase 4.1c (desenho em docs/superpowers/specs/2026-09-28-4.1c-glock-m4a4-m9-
# design.md, seção 3.1). Construída em mm no referencial da ficha (tools/blender/refs/glock.json): o contorno e as peças
# da foto do MOD (Glock 17 Gen 4 pelo lado esquerdo, espelhada) pela régua; o seletor, o botão do retém e a textura de
# 3ª geração da foto da Glock 18C; a janela de ejeção e o extrator da Glock 35 (lado direito); as larguras da Glock.
# Lado direito da arma = -Y do Blender; a primeira pessoa mostra o esquerdo (+Y), com o seletor.
# Marcações genéricas (regra 9): o calibre, o modelo e o número de série — nenhum logotipo nem nome de fabricante.
import math

from . import pecas as P
from . import pecas_superficie as PS

ORIGEM_MM = (-105.6, 0.0)  # o pino do gatilho no eixo do cano: a origem da arma no jogo (como a AK)
PECAS = ('ferrolho', 'carregador', 'gatilho', 'seletor')
ANGULO_PUNHO = 22.0  # graus do eixo do punho com a vertical (o ajuste das linhas da frente e de trás do contorno: 19 e 27)
PERTO_MM = (-150.0, -10.0)  # a vista de perto da conferência: a traseira do ferrolho, o seletor e o retém
OLHO_M = (-0.42, 0.075, 0.055)  # o olho da vista de primeira pessoa da conferência, atrás e à esquerda da alça (m)
Y_MEIO_GUARDA = -26.8  # o alto do vão do guarda-mato (y da ficha): acima dele a armação é o guarda-pó
Y_PUNHO_LARGO = -32.0  # abaixo dele o punho tem a largura toda; acima, a do guarda-pó, com a rampa do alargamento
RAIO_GUIA, ALTURA_GUIA = 1.9, 1.0  # a ponta da guia da mola (raio) e o centro dela acima do fundo do ferrolho (mm)
Y_PUNHO_TEXTURA = -56.0  # abaixo do guarda-mato: a frente do punho já separada dele (as nervuras da frente começam aí)
PAREDE_PUNHO = 3.5  # a parede de polímero do punho na frente e atrás do carregador (mm)
ALARGAMENTO = 30.0  # graus da rampa que alarga o alto da armação (guarda-pó) até a largura do punho, com a vertical


def pivos(ficha):
    """Pivô (mm, ficha) e extras de cada peça (direções no referencial do jogo: +X boca, +Y cima, +Z direita)."""
    pt = ficha['pontos']
    a = math.radians(ANGULO_PUNHO)
    tras = min(p[0] for p in ficha['pecas']['ferrolho'])
    return {
        'base': (ORIGEM_MM, {}),
        'ferrolho': ((tras, 0.0), {'eixo': [-1.0, 0.0, 0.0]}),
        # o carregador desce pelo eixo do punho, para baixo e para trás
        'carregador': (tuple(pt['travaCarregador']), {'eixo': [round(-math.sin(a), 4), round(-math.cos(a), 4), 0.0]}),
        'gatilho': (tuple(pt['pinoGatilho']), {'eixo_giro': [0.0, 0.0, 1.0]}),
        'seletor': (tuple(pt['eixoSeletor']), {'eixo_giro': [0.0, 0.0, 1.0]}),
    }


def soquetes(ficha):
    """(nome, (x, y) da ficha, lado = Y do Blender em mm, rotação XYZ em graus no Blender)."""
    pt = ficha['pontos']
    j = pt['janela']
    face_direita = -ficha['vistaDeCima']['larguras']['ferrolho']['mm'] / 2
    return [
        ('boca', (0.0, 0.0), 0.0, (0, 0, 0)),
        # a cápsula sai pela janela da direita, para a frente e para cima (como na AK)
        ('ejecao', ((j['x0'] + j['x1']) / 2, (j['y0'] + j['y1']) / 2), face_direita, (0, -15, -75)),
        ('carregador', tuple(pt['travaCarregador']), 0.0, (0, ANGULO_PUNHO, 0)),
        ('mira_tras', tuple(pt['entalheAlca']), 0.0, (0, 0, 0)),
        ('mira_frente', tuple(pt['posteMassa']), 0.0, (0, 0, 0)),
        # o +Z do soquete (o +Y no jogo) sobe pelo eixo do punho, inclinado para trás
        ('mao_d', (-166.0, -70.0), 0.0, (0, ANGULO_PUNHO, 0)),
        ('mao_e', (-162.0, -84.0), 0.0, (0, ANGULO_PUNHO, 0)),
    ]


# ------------------------------------------------------------------------------------------------ contas
def _cruzamentos(contorno, z):
    """Os x em que a horizontal z corta o contorno, na faixa do punho (x < -120), em ordem."""
    xs = []
    n = len(contorno)
    for k in range(n):
        (ax, ay), (bx, by) = contorno[k], contorno[(k + 1) % n]
        if (ay > z) != (by > z):
            x = ax + (z - ay) / (by - ay) * (bx - ax)
            if x < -120.0:
                xs.append(x)
    return sorted(xs)


def _na_borda(contorno, z, frente):
    """O x da borda do punho na altura z: a de trás (frente=False) ou a da frente. A da frente sai da reta da frente do
    punho medida abaixo do guarda-mato (de Y_PUNHO_TEXTURA a 40 mm abaixo), para valer também na altura em que a frente
    do punho já se funde com o guarda-mato."""
    if not frente:
        return _cruzamentos(contorno, z)[0]
    za, zb = Y_PUNHO_TEXTURA - 4.0, Y_PUNHO_TEXTURA - 44.0
    xa, xb = _cruzamentos(contorno, za)[-1], _cruzamentos(contorno, zb)[-1]
    return xa + (z - za) * (xb - xa) / (zb - za)


def _dentro(pts, x, y):
    """Ponto dentro de um polígono (paridade)."""
    dentro = False
    n = len(pts)
    for k in range(n):
        (ax, ay), (bx, by) = pts[k], pts[(k + 1) % n]
        if (ay > y) != (by > y) and x < ax + (y - ay) / (by - ay) * (bx - ax):
            dentro = not dentro
    return dentro


def _pesos_de_chanfro(ob, peso):
    """Chanfro por peso em todas as arestas (acabar com o limite por peso): `peso(a, b)` (mm, Blender) → 0 a 1, o
    múltiplo da largura do chanfro da peça."""
    me = ob.data
    at = me.attributes.get('bevel_weight_edge') or me.attributes.new('bevel_weight_edge', 'FLOAT', 'EDGE')
    vs = me.vertices
    mm = lambda i: tuple(c / P.S for c in vs[i].co)
    at.data.foreach_set('value', [peso(mm(e.vertices[0]), mm(e.vertices[1])) for e in me.edges])
    ob['chanfro_peso'] = True


# ------------------------------------------------------------------------------------------------ partes
def _ferrolho(ficha, M):
    """Ferrolho de aço nitretado: o perfil da foto na largura da Glock, os chanfros de 45° do alto, a serrilha de trás
    (inteira na direita; na esquerda, só à frente do seletor), a janela de ejeção com o extrator, os furos da frente (o
    cano e a guia da mola), a face da culatra à vista na janela, o seletor da 18 e as marcações."""
    pc, pt, L, D = ficha['pecas'], ficha['pontos'], ficha['vistaDeCima']['larguras'], ficha['vistaDeCima']['detalhes']
    corpo, det, interno = M['corpo'], M['detalhes'], M['interno']
    ls = L['ferrolho']['mm'] / 2
    f = P.prisma('ferrolho', pc['ferrolho'], 'XZ', -ls, ls, corpo, 'corpo', 'ferrolho', chanfro=0.6)
    xs = [p[0] for p in pc['ferrolho']]
    zs = [p[1] for p in pc['ferrolho']]
    tras, frente, topo, fundo = min(xs), max(xs), max(zs), min(zs)
    # Os chanfros de 45° dos dois lados do alto (o alto plano fica com a largura da ficha), cortados depois do chanfro
    # fino: faces planas, como o ferrolho fresado.
    c = (L['ferrolho']['mm'] - L['topoDoFerrolho']['mm']) / 2
    for lado in (-1, 1):
        cunha = [(lado * (ls + 1.0), topo - c - 1.0), (lado * (ls + 1.0), topo + 1.0), (lado * (ls - c - 1.0), topo + 1.0)]
        P.cortar(f, P.prisma('chanfro do alto', cunha, 'YZ', tras - 1.0, frente + 1.0, corpo, 'corpo', 'ferrolho', chanfro=0),
                 depois_do_chanfro=True)
    s = D['serrilha']
    for lado, faixa in ((-1, s['x']), (1, s['esquerdaDa18'])):
        PS.ranhuras('serrilha', f, s['sulcos'], s['largura'], s['profundidade'], (faixa[0] - 0.01, faixa[1] + 0.01),
                    tuple(s['y']), lado * ls, perfil='V')
    # Janela de ejeção (direita): abre no lado e na metade direita do alto, com o canto de baixo da frente arredondado
    # (foto da Glock 35); de cima, a frente dela é reta.
    j = pt['janela']
    r = 5.0
    janela = [(j['x0'], j['y0']), (j['x1'] - r, j['y0']), *P.arco(j['x1'] - r, j['y0'] + r, r, -90, 0, 8)[1:],
              (j['x1'], topo + 2.0), (j['x0'], topo + 2.0)]
    P.cortar(f, P.prisma('janela de ejeção', janela, 'XZ', -ls - 2.0, 1.0, corpo, 'corpo', 'ferrolho', chanfro=0))
    # A face da culatra no fundo da janela (aço polido, com o furo do percussor) e o extrator na face direita.
    culatra = P.caixa('face da culatra', (j['x0'] - 1.8, -5.0, -4.0), (j['x0'] + 0.2, 5.0, j['y0'] + 8.0), interno, 'interno',
                      'ferrolho', chanfro=0.3)
    P.cortar(culatra, P.torno('furo do percussor', [(j['x0'] - 3, 0), (j['x0'] - 3, 1.2), (j['x0'] + 1, 1.2), (j['x0'] + 1, 0)],
                              interno, 'interno', 'ferrolho', seg=16))
    ex = pt['extrator']
    P.caixa('extrator', (ex['x'][0], -ls - 0.35, ex['y'][0]), (ex['x'][1], -ls + 1.0, ex['y'][1]), det, 'detalhes', 'ferrolho',
            chanfro=0.3)
    P.cortar(f, P.caixa('rasgo do extrator', (ex['x'][0] - 0.3, -ls - 1.0, ex['y'][0] - 0.3), (ex['x'][1], -ls + 1.2,
                                                                                               ex['y'][1] + 0.3), corpo,
                        'corpo', 'ferrolho', chanfro=0))
    # o ressalto do indicador de câmara carregada, na ponta da frente do extrator
    P.esfera('indicador do extrator', (ex['x'][1] - 1.8, -ls - 0.35, (ex['y'][0] + ex['y'][1]) / 2), 1.2, (1.4, 0.45, 1.0), det,
             'detalhes', 'ferrolho', u=12, v=8)
    # A frente: o furo do cano (o cano sobressai 2 mm, com a folga de 0,2 mm à vista) e o da guia da mola, embaixo, aberto
    # no fundo do ferrolho (a armação fecha por baixo).
    rc = ficha['tornos']['cano']['perfil'][1][1] + 0.2
    P.cortar(f, P.torno('furo do cano', [(frente - 6.0, 0), (frente - 6.0, rc), (frente + 1.0, rc), (frente + 1.0, 0)], corpo,
                        'corpo', 'ferrolho', seg=32))
    P.cortar(f, P.torno('furo da guia da mola', [(frente - 8.0, 0), (frente - 8.0, RAIO_GUIA + 0.3), (frente + 1.0, RAIO_GUIA + 0.3),
                                                  (frente + 1.0, 0)], corpo, 'corpo', 'ferrolho', seg=24,
                        centro=(0, 0, fundo + ALTURA_GUIA)))
    # a tampa de trás do ferrolho (a placa de polímero na face de trás, com o canal do percussor): a primeira pessoa a vê
    placa = P.prisma('tampa do ferrolho', P.ret_arredondado(-7.6, 7.6, fundo + 2.8, topo - 4.2, 1.6, 4), 'YZ', tras - 0.5, tras + 1.5, M['detalhes'],
                     'detalhes', 'ferrolho', chanfro=0.3)
    P.cortar(placa, P.caixa('canal da tampa', (tras - 1.0, -1.2, -1.5), (tras + 0.2, 1.2, 1.5), M['detalhes'], 'detalhes', 'ferrolho', chanfro=0,
                            so_alto=True))
    _seletor(ficha, M, f, ls)
    P.gravacao('calibre', '9x19', -97.0, -3.2, 3.4, 'esquerda', ls, 0.25, f)
    P.gravacao('modelo', '18', -41.0, -3.4, 4.0, 'esquerda', ls, 0.25, f)
    P.gravacao('número de série', 'AFT318', -84.0, -6.2, 2.6, 'direita', -ls, 0.2, f)
    return f, (tras, frente, topo, fundo, ls)


def _seletor(ficha, M, f, ls):
    """O seletor de tiro da 18 no lado esquerdo do ferrolho (foto da Glock 18C): o rebaixo redondo, o cubo e a alavanca
    (peça móvel, na posição de tiro a tiro), e as duas marcas das posições gravadas no ferrolho."""
    pt, D = ficha['pontos'], ficha['vistaDeCima']['detalhes']['seletor']
    corpo, det = M['corpo'], M['detalhes']
    sai = ficha['vistaDeCima']['larguras']['seletor']['sai']
    hx, hz = pt['eixoSeletor']
    P.cortar(f, P.pino('rebaixo do seletor', hx, hz, D['raioRebaixo'], corpo, 'corpo', 'ferrolho', lado=1, de=ls - 0.7, ate=ls + 1.0))
    P.pino('cubo do seletor', hx, hz, 3.9, det, 'detalhes', 'seletor', lado=1, de=ls - 0.8, ate=ls + sai - D['espessura'])
    comp = D['alcance']
    lb = D['largura'] / 2
    alavanca = P.prisma('alavanca do seletor', P.ret_arredondado(hx - 2.5, hx + comp, hz - lb, hz + lb, lb, 4), 'XZ',
                        ls + sai - D['espessura'], ls + sai, det, 'detalhes', 'seletor', chanfro=0.3)
    P.rotacionar(alavanca, 'Y', -D['angulos'][0], (hx, 0, hz))
    # As marcas das posições (foto da 18C): um ponto em cima, à frente da ponta da alavanca levantada (tiro a tiro), e
    # dois embaixo, à frente da ponta abaixada (rajada), gravados no lado do ferrolho, fora do chanfro do alto.
    topo = max(p[1] for p in ficha['pecas']['ferrolho'])
    fundo = min(p[1] for p in ficha['pecas']['ferrolho'])
    chanfro = (ficha['vistaDeCima']['larguras']['ferrolho']['mm'] - ficha['vistaDeCima']['larguras']['topoDoFerrolho']['mm']) / 2
    pontos = []
    for ang, n, limite in ((D['angulos'][0], 1, topo - chanfro - 1.2), (D['angulos'][1], 2, fundo + 1.4)):
        a = math.radians(ang)
        mx, mz = hx + D['marcas'] * math.cos(a), hz + D['marcas'] * math.sin(a)
        mz = min(mz, limite) if ang > 0 else max(mz, limite)
        pontos += [(mx + 2.0 * k, mz) for k in range(n)]
    for mx, mz in pontos:
        P.cortar(f, P.pino('marca do seletor', mx, mz, 0.7, corpo, 'corpo', 'ferrolho', lado=1, de=ls - 0.3, ate=ls + 1.0,
                           so_alto=True))


def _miras(ficha, M):
    """A alça em U (o entalhe no meio) e a massa de mira, de polímero, presas no ferrolho."""
    pc, pt, L = ficha['pecas'], ficha['pontos'], ficha['vistaDeCima']['larguras']
    det = M['detalhes']
    lt = L['miraTras']['mm'] / 2
    alca = P.prisma('alça', pc['miraTras'], 'XZ', -lt, lt, det, 'detalhes', 'ferrolho', chanfro=0.4)
    e = L['miraTras']['entalhe'] / 2
    ex, ez = pt['entalheAlca']
    P.cortar(alca, P.caixa('entalhe da alça', (ex - 8.0, -e, ez + e), (ex + 8.0, e, ez + 10.0), det, 'detalhes', 'ferrolho',
                           chanfro=0))
    P.cortar(alca, P.torno('fundo do entalhe', [(ex - 8.0, 0), (ex - 8.0, e), (ex + 8.0, e), (ex + 8.0, 0)], det, 'detalhes',
                           'ferrolho', seg=20, centro=(0, 0, ez + e)))
    lf = L['miraFrente']['mm'] / 2
    massa = P.prisma('massa de mira', pc['miraFrente'], 'XZ', -lf, lf, det, 'detalhes', 'ferrolho', chanfro=0.3)
    # o ponto da massa (em relevo raso, de frente para o atirador)
    px, pz = pt['posteMassa']
    P.cortar(massa, P.torno('ponto da massa', [(px - 5.5, 0), (px - 5.5, 1.0), (px - 4.2, 1.0), (px - 4.2, 0)], det, 'detalhes',
                            'ferrolho', seg=16, centro=(0, 0, pz - 1.4), so_alto=True))


def _cano(ficha, M, janela, topo):
    """O cano (a boca sai 2 mm da face do ferrolho), com a alma hexagonal do raiamento poligonal e o bloco da culatra à
    vista na janela; a ponta da guia da mola embaixo."""
    tn = ficha['tornos']
    corpo, interno = M['corpo'], M['interno']
    cano = P.torno('cano', tn['cano']['perfil'], corpo, 'corpo', seg=48, centro=(0, 0, tn['cano']['centroY']))
    P.cortar(cano, P.torno('alma', tn['alma']['perfil'], corpo, 'corpo', seg=6, centro=(0, 0, tn['alma']['centroY'])))
    bloco = P.caixa('bloco da culatra', (janela['x0'] + 0.5, -6.2, -1.0), (janela['x1'] - 2.0, 6.2, topo - 0.9), corpo, 'corpo',
                    chanfro=0.8)
    P.gravacao('série do cano', '318', janela['x0'] + 12.0, 4.0, 2.2, 'direita', -6.2, 0.2, bloco)
    return cano


def _armacao(ficha, M, ls):
    """A armação de polímero: o perfil da foto, com o guarda-pó e o alto na largura do guarda-pó, o punho na largura
    toda (alargando numa rampa de ALARGAMENTO graus) e o guarda-mato estreito; o vão do guarda-mato, o rasgo do
    gatilho, o trilho de uma fenda, os rebaixos e as alavancas (retém do ferrolho, desmontagem, botão do retém do
    carregador de 3ª geração), os três pinos e a textura do punho (só no modelo alto)."""
    pc, pt, L, D = ficha['pecas'], ficha['pontos'], ficha['vistaDeCima']['larguras'], ficha['vistaDeCima']['detalhes']
    pol, det = M['guarnicao'], M['detalhes']
    lp = L['punho']['mm'] / 2
    lg = L['guardaPo']['mm'] / 2
    lm = L['guardaMato']['mm'] / 2
    # o contorno do punho vem da foto com a escada de pixels nas diagonais: simplificado antes do chanfro
    a = P.prisma('armação', P.simplificar(pc['armacao']), 'XZ', -lp, lp, pol, 'guarnicao', chanfro=1.0)
    a['chanfro'] = (1.2, 4)
    # A largura por região: o alto (guarda-pó, alavancas) na do guarda-pó, alargando na rampa até a do punho; o guarda-mato
    # estreito na frente do punho.
    for lado in (-1, 1):
        rampa = (lp - lg) / math.tan(math.radians(ALARGAMENTO))  # a altura da rampa
        u = [(lado * lg, 5.0), (lado * lg, Y_PUNHO_LARGO + rampa), (lado * lp, Y_PUNHO_LARGO), (lado * (lp + 5), Y_PUNHO_LARGO),
             (lado * (lp + 5), 5.0)]
        P.cortar(a, P.prisma('largura do alto', u, 'YZ', -215.0, 5.0, pol, 'guarnicao', chanfro=0))
        g = [(lado * lm, Y_MEIO_GUARDA - 0.8), (lado * lm, -70.0), (lado * (lp + 5), -70.0), (lado * (lp + 5), Y_MEIO_GUARDA - 0.8)]
        P.cortar(a, P.prisma('largura do guarda-mato', g, 'YZ', -120.5, 5.0, pol, 'guarnicao', chanfro=0))
    for b in ficha['buracos']:
        P.cortar(a, P.prisma('vão do guarda-mato', b, 'XZ', -lp - 2, lp + 2, pol, 'guarnicao', chanfro=0))
    # o rasgo por onde o gatilho entra na armação
    lgat = L['gatilho']['mm'] / 2 + 0.3
    gx = [p[0] for p in pc['gatilho']]
    P.cortar(a, P.caixa('rasgo do gatilho', (min(gx) - 0.4, -lgat, Y_MEIO_GUARDA - 1.0), (max(gx) + 0.4, lgat, Y_MEIO_GUARDA + 4.5),
                        pol, 'guarnicao', chanfro=0))
    # Trilho de acessórios (uma fenda): os sulcos dos lados do guarda-pó e a fenda de recuo embaixo.
    t = pt['trilho']
    for lado in (-1, 1):
        y0, y1 = sorted((lado * (lg - 1.6), lado * (lg + 3.0)))  # 1,6 mm de fundo, o cortador passa 3 mm para fora
        P.cortar(a, P.caixa('sulco do trilho', (t['x'][0], y0, t['sulco'][0]), (t['x'][1] + 2.0, y1, t['sulco'][1]), pol, 'guarnicao',
                            chanfro=0), depois_do_chanfro=True)
    P.cortar(a, P.caixa('fenda do trilho', (t['fenda'][0], -lg - 1, -40.0), (t['fenda'][1], lg + 1, t['fundoFenda']), pol,
                        'guarnicao', chanfro=0), depois_do_chanfro=True)
    # Retém do ferrolho (esquerda) e a alavanca de desmontagem (dos dois lados), nos rebaixos da armação.
    rr, rt = pt['rebaixoRetem'], pt['retemFerrolho']
    P.cortar(a, P.prisma('rebaixo do retém', P.ret_arredondado(rr['x'][0], rr['x'][1], rr['y'][0], rr['y'][1], 2.5, 4), 'XZ',
                         lg - 1.0, lp + 5, pol, 'guarnicao', chanfro=0))
    retem = P.prisma('retém do ferrolho', P.ret_arredondado(rt['x'][0], rt['x'][1], rt['y'][0], rt['y'][1], 1.8, 4), 'XZ',
                     lg - 0.6, lg + 1.1, det, 'detalhes', chanfro=0.3)
    for k in range(4):
        z = rt['y'][0] + (rt['y'][1] - rt['y'][0]) * (k + 1) / 5
        P.cortar(retem, P.caixa('estria do retém', (rt['x'][0] - 1, lg + 0.8, z - 0.25), (rt['x'][1] + 1, lg + 2.0, z + 0.25), det,
                                'detalhes', chanfro=0, so_alto=True))
    ra, al = pt['rebaixoAlavanca'], pt['alavancaDesmontagem']
    for lado in (-1, 1):
        y0, y1 = (lg - 1.0, lp + 5) if lado > 0 else (-lp - 5, -lg + 1.0)
        P.cortar(a, P.prisma('rebaixo da desmontagem', P.ret_arredondado(ra['x'][0], ra['x'][1], ra['y'][0], ra['y'][1], 2.0, 4),
                             'XZ', y0, y1, pol, 'guarnicao', chanfro=0))
        a0, a1 = (lg - 0.8, lg + 0.4) if lado > 0 else (-lg - 0.4, -lg + 0.8)
        alav = P.prisma('alavanca de desmontagem', P.ret_arredondado(al['x'][0], al['x'][1], al['y'][0], al['y'][1], 0.8, 3),
                        'XZ', a0, a1, det, 'detalhes', chanfro=0.2)
        for k in range(5):
            x = al['x'][0] + (al['x'][1] - al['x'][0]) * (k + 1) / 6
            P.cortar(alav, P.caixa('estria da desmontagem', (x - 0.2, lado * lg - 1.0, al['y'][0] + 1), (x + 0.2, lado * lg + 1.0,
                                                                                                          al['y'][1] - 1), det,
                                   'detalhes', chanfro=0, so_alto=True))
    # Botão do retém do carregador (3ª geração, esquerda), com as nervuras.
    bt = pt['botaoRetem']
    P.cortar(a, P.prisma('rebaixo do botão', P.ret_arredondado(bt['x'][0] - 1.0, bt['x'][1] + 1.0, bt['y'][0] - 1.0, bt['y'][1] + 1.0,
                                                               1.5, 4), 'XZ', lp - 1.2, lp + 5, pol, 'guarnicao', chanfro=0))
    botao = P.prisma('botão do retém', P.ret_arredondado(bt['x'][0], bt['x'][1], bt['y'][0], bt['y'][1], 1.2, 4), 'XZ',
                     lp - 1.2, lp + 0.9, det, 'detalhes', chanfro=0.3)
    for k in range(bt['nervuras']):
        z = bt['y'][0] + (bt['y'][1] - bt['y'][0]) * (k + 0.5) / bt['nervuras']
        P.cortar(botao, P.caixa('nervura do botão', (bt['x'][0] - 1, lp + 0.6, z - 0.3), (bt['x'][1] + 1, lp + 1.5, z + 0.3), det,
                                'detalhes', chanfro=0, so_alto=True))
    # Os três pinos (os dois do alto na face do guarda-pó, o da caixa do gatilho na do punho).
    for nome, chave, raio, face in (('pino de travamento', 'pinoTravamento', 'raioPinoTravamento', lg),
                                    ('pino do gatilho', 'pinoGatilho', 'raioPinoGatilho', lg),
                                    ('pino da caixa do gatilho', 'pinoCaixaGatilho', 'raioPinoCaixa', lp)):
        x, z = pt[chave]
        for lado in (-1, 1):
            P.pino(nome, x, z, pt[raio], det, 'detalhes', lado=lado, de=face - 0.4, ate=face + 0.15)
    _textura_do_punho(ficha, a, lp)
    return a


def _textura_do_punho(ficha, armacao, lp):
    """Textura de 3ª geração, só no modelo alto (vai para o relevo assado): o painel de pontilhado de cada lado, recuado
    das bordas da frente e de trás do punho (sem entrar no rebaixo do botão do retém), e as nervuras horizontais na frente
    (abaixo do guarda-mato) e atrás (fotos da Glock 18C e da 35)."""
    tx = ficha['vistaDeCima']['detalhes']['texturaPunho']
    c = ficha['contorno']
    bt = ficha['pontos']['botaoRetem']
    z0, z1 = tx['painelY'][1], tx['painelY'][0]
    rec = tx['painelRecuo']
    painel = [(_na_borda(c, z1, False) + rec, z1), (_na_borda(c, z0, False) + rec, z0),
              (_na_borda(c, z0, True) - rec, z0), (_na_borda(c, z1, True) - rec, z1)]
    xs = [p[0] for p in painel]
    grao = PS.pontilhado(0.7, 0.4, 0.15)

    def no_painel(u, v):
        if not _dentro(painel, u, v):
            return None
        if bt['x'][0] - 2.5 <= u <= bt['x'][1] + 2.5 and bt['y'][0] - 2.5 <= v <= bt['y'][1] + 2.5:
            return None
        return grao(u, v)
    for lado in (-1, 1):
        PS.relevo('pontilhado do punho', armacao, (min(xs) - 1, max(xs) + 1), (z0, z1), 0.1,
                  lambda u, v, s=lado: ((u, s * (lp + 20.0), v), (0, -s, 0)), no_painel)
    nerv = tx['nervuras']

    def nervuras(_u, v):
        f = (v / nerv) - math.floor(v / nerv)
        return 0.22 if f < 0.5 else 0.0
    # frente (abaixo do guarda-mato, de fora para trás) e costas (de trás para a frente)
    for nome, x_fora, sinal, alto in (('nervuras da frente do punho', -110.0, -1, Y_PUNHO_TEXTURA),
                                      ('nervuras das costas do punho', -225.0, 1, z1)):
        PS.relevo(nome, armacao, (-lp + 3.0, lp - 3.0), (z0, alto), 0.12,
                  lambda u, v, xf=x_fora, s=sinal: ((xf, u, v), (s, 0, 0)), nervuras)


def _gatilho(ficha, M):
    """O gatilho de polímero com a lâmina da trava no meio, saindo 0,8 mm à frente da face na parte de baixo."""
    pc, L = ficha['pecas'], ficha['vistaDeCima']['larguras']
    det = M['detalhes']
    lg = L['gatilho']['mm'] / 2
    lt = L['gatilho']['trava'] / 2
    g = P.prisma('gatilho', pc['gatilho'], 'XZ', -lg, lg, det, 'detalhes', 'gatilho', chanfro=0.5)
    frente = sorted([p for p in pc['gatilho'] if p[0] > -112.0 and p[1] < -33.0], key=lambda p: -p[1])
    P.cortar(g, P.prisma('fenda da trava', [(x + 1.0, z) for x, z in frente] + [(x - 3.2, z) for x, z in reversed(frente)], 'XZ',
                         -lt - 0.15, lt + 0.15, det, 'detalhes', 'gatilho', chanfro=0))
    P.prisma('trava do gatilho', [(x + 0.8, z) for x, z in frente] + [(x - 3.0, z) for x, z in reversed(frente)], 'XZ', -lt, lt, det,
             'detalhes', 'gatilho', chanfro=0.25)


def _carregador(ficha, M):
    """O carregador de 17: a base (a peça da foto) e o corpo de polímero subindo pelo eixo do punho, dentro dele (as
    paredes da armação com PAREDE_PUNHO mm na frente e atrás), até a boca do carregador, escondida no alto da armação."""
    pc, L = ficha['pecas'], ficha['vistaDeCima']['larguras']
    mat = M['carregador']
    lb = L['baseCarregador']['mm'] / 2
    P.prisma('base do carregador', pc['carregador'], 'XZ', -lb, lb, mat, 'carregador', 'carregador', chanfro=0.8)
    c = ficha['contorno']
    z_base = max(p[1] for p in pc['carregador']) + 0.2
    alto = Y_PUNHO_TEXTURA + 20.0  # a boca do carregador, dentro da armação acima do guarda-mato
    corpo = [(_na_borda(c, z_base, False) + PAREDE_PUNHO, z_base), (_na_borda(c, z_base, True) - PAREDE_PUNHO, z_base),
             (_na_borda(c, alto, True) - PAREDE_PUNHO, alto), (_na_borda(c, alto, False) + PAREDE_PUNHO, alto)]
    P.prisma('corpo do carregador', corpo, 'XZ', -11.0, 11.0, mat, 'carregador', 'carregador', chanfro=1.0)


def construir(ficha, M):
    """Todas as peças no nível atual (pecas.iniciar). M = materiais de fábrica por zona (materiais.materiais_de_fabrica)."""
    f, (_tras, _frente, topo, fundo, ls) = _ferrolho(ficha, M)
    _miras(ficha, M)
    _cano(ficha, M, ficha['pontos']['janela'], topo)
    # a ponta da guia da mola, recolhida no furo da frente do ferrolho
    frente = max(p[0] for p in ficha['pecas']['ferrolho'])
    P.torno('guia da mola', [(frente - 30.0, 0), (frente - 30.0, RAIO_GUIA), (frente - 1.2, RAIO_GUIA), (frente - 0.8, RAIO_GUIA - 0.5),
                             (frente - 0.8, 0)], M['interno'], 'interno', seg=20, centro=(0, 0, fundo + ALTURA_GUIA))
    _armacao(ficha, M, ls)
    _gatilho(ficha, M)
    _carregador(ficha, M)
