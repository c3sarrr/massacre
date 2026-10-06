# P90 — o grupo de cima (Fase 4.1d; desenho da 4.1d, seção 4.3; plano da 4.1d, Tarefa 10; o resto em p90.py): o grupo
# do cano da TR no cinza mais escuro do CS2 (zona `corpo`) — a ponte pelo contorno de lado da ficha (pecas.ponte) em
# partes de larguras diferentes: a torre da frente (30,2 mm, a largura da face da frente, com o botão de trava do grupo
# do cano e a janela da torre nos lados), o corpo largo sob o trilho de cima (40,8 mm, onde os trilhos laterais assentam;
# a janela e a fresta vazadas), a travessa
# de trás e as duas pernas por fora do carregador (52,8 mm), e o pé embaixo do carregador; o corpo do grupo do cano
# entre os pilares (pecas.receptor), com o canal do meio por onde o ressalto da frente do carregador sai; o trilho de
# cima (MIL-STD-1913, as fendas nos lugares da foto) e os dois laterais com os parafusos; o quebra-chama do jogo (o colar
# serrilhado e as três portas ovais em cada fileira de cima), o cano e a alma; e as miras de ferro rebatíveis do CS2 —
# a base presa no trilho com as orelhas de proteção e a folha fina que dobra entre elas (o anel no centro do tambor
# serrilhado, atrás; o poste, na frente). Mm no referencial da ficha; no Blender X = x, Z = y e o lado direito em -Y.
import math

import bmesh

from . import p90_mecanica as MEC
from . import p90_quadro as Q
from . import pecas as P
from . import pecas_mecanica as PM
from . import pecas_superficie as PS
from .unidades import v3

TORRE_X = -82.2  # a face de trás da torre (o pilar da frente)
CORPO_X = -172.5  # onde o corpo largo da ponte encontra a travessa e as pernas de trás
TRAVESSA_Y = 55.0  # o fundo da travessa de trás: o carregador girado (5,5°) passa embaixo dela
PE_Y = 14.6  # o alto do pé da ponte e da aba das pernas, embaixo do carregador (15,3)
ABA_Y = 11.5  # o fundo da aba em que as pernas assentam
PERNA_DENTRO = 23.0  # as pernas por fora do carregador (45 mm), com 0,5 mm de folga
CANAL_RESSALTO = {'meia': 8.5, 'rampa': (-93.2, -116.0)}  # o canal do ressalto do carregador no corpo do grupo do cano
MIRA_TRAS = {'base_topo': 99.0, 'meia_base': 12.2, 'orelha': (7.6, 10.4), 'folha': (-188.3, -182.3), 'meia_folha': 6.8,
             'anel': 5.6, 'abertura': 0.9, 'no': 2.4, 'pino': 1.2, 'tambor': (107.0, 3.2, 6.4)}
MIRA_FRENTE = {'base_topo': 104.0, 'meia_base': 12.2, 'orelha': (5.2, 8.2), 'folha': (-56.0, -51.0), 'meia_folha': 4.4,
               'poste': (1.6, 2.4), 'no': 2.2, 'pino': 1.0}


def _seg(alto, jogo):
    return alto if P.nivel() == 'alto' else jogo


def limpar(poli, tol=1e-6):
    """O polígono sem os pontos repetidos nem os colineares — os que o Sutherland–Hodgman deixa ao longo da reta de corte
    quando o polígono passa por ela e volta (a ponta de área zero) —, para o prisma não nascer com faces degeneradas."""
    p = [tuple(q) for q in poli]
    mudou = True
    while mudou and len(p) > 3:
        mudou = False
        for i in range(len(p)):
            a, b, c = p[i - 1], p[i], p[(i + 1) % len(p)]
            if math.dist(a, b) < tol or abs((b[0] - a[0]) * (c[1] - b[1]) - (b[1] - a[1]) * (c[0] - b[0])) < tol:
                del p[i]
                mudou = True
                break
    return p


def recortar(pts, x0=None, x1=None, y0=None, y1=None):
    """O polígono recortado pelas retas x = x0 (fica x ≥ x0), x = x1 (x ≤ x1), y = y0 (y ≥ y0) e y = y1 (y ≤ y1)."""
    p = [tuple(q) for q in pts]
    for valor, a, b, manter in ((x0, (x0, -1e4), (x0, 1e4), -1), (x1, (x1, -1e4), (x1, 1e4), 1), (y0, (-1e4, y0), (1e4, y0), 1),
                                (y1, (-1e4, y1), (1e4, y1), -1)):
        if valor is not None:
            p = P.cortar_poligono(p, a, b, manter)
    return limpar(p)


# ------------------------------------------------------------------------------------------------ ponte
def _fendas_do_trilho(ficha):
    """Os centros das fendas do trilho de cima, onde a foto da FN as mostra (as sequências do contorno do trilho abaixo
    de y = 91,5 com 2 mm ou mais), na largura da norma."""
    pts = [tuple(p) for p in ficha['pecas']['trilhoCima'] if p[1] > 85.0]
    fendas, atual = [], []
    for x, y in pts + [(None, 99.0)]:
        if y < 91.5:
            atual.append(x)
        elif atual:
            if max(atual) - min(atual) >= 2.0:
                fendas.append((min(atual) + max(atual)) / 2)
            atual = []
    return sorted(fendas)


def contorno_da_ponte(ficha):
    """O contorno de lado da ponte (ficha pecas.ponte) com o pé da perna de trás descendo reto até o quadro: na foto, a
    perna encosta no degrau do quadro (−221,5) e na quilha do carregador; a reta da ficha de (−219,2; 23) a (−221; 1,3)
    deixava uma fresta de 0,5 a 2 mm à vista de lado. O pé fica 0,1 mm à frente do degrau e acima do alto do quadro, a
    perna 0,1 mm à frente da quilha."""
    pts = [tuple(p) for p in ficha['pecas']['ponte']]
    xq, yq = Q.degrau_sob_a_ponte(ficha)
    i = min(range(len(pts)), key=lambda k: (pts[k][0] if pts[k][1] < yq else 1e9))  # a quina de baixo de trás (−221; 1,3)
    xc, yc = pts[i]
    reto = [(xq - 0.4, yq + 5.7), (xq - 0.4, yq + 0.1), (xq + 0.1, yq + 0.1), (xq + 0.1, yc)]
    return pts[:i] + reto + pts[i + 1:]


def ponte(ficha, M):
    """A ponte do trilho de cima em partes (a mesma zona e a mesma peça base, juntadas depois): as larguras da ficha
    (vistaDeCima.larguras: a torre de 30,2, o corpo de 40,8, as pernas e a travessa de 52,8)."""
    co = M['corpo']
    L = ficha['vistaDeCima']['larguras']
    pt = contorno_da_ponte(ficha)
    mt, mc, mp = L['ponte']['mm'] / 2, L['ponteTrilhos']['mm'] / 2, L['trilhoLateral']['mm'] / 2
    mr = L['receptor']['mm'] / 2
    partes = {
        # a torre inteira na largura da face da frente (30,2): os trilhos laterais acabam atrás dela (x = −85,2), e na
        # vista de três quartos da FN o bloco embaixo da frente do trilho de cima é estreito
        'torre': (recortar(pt, x0=TORRE_X), -mt, mt),
        'corpo da ponte': (recortar(pt, x0=CORPO_X, x1=TORRE_X), -mc, mc),
        'travessa da ponte': (recortar(pt, x1=CORPO_X, y0=TRAVESSA_Y), -mp, mp),
        'pé da ponte': (recortar(pt, x1=CORPO_X, y1=PE_Y), -mr, mr),
        'aba das pernas': (recortar(pt, x1=CORPO_X, y0=ABA_Y, y1=PE_Y), -mp, mp),
    }
    obs = {nome: P.prisma(nome, poli, 'XZ', a, b, co, 'corpo', chanfro=0.8, seg=3) for nome, (poli, a, b) in partes.items()}
    perna = recortar(pt, x1=CORPO_X, y0=PE_Y - 0.4, y1=TRAVESSA_Y + 0.6)
    for lado in (1, -1):
        obs[f'perna {lado}'] = P.prisma('perna da ponte', perna, 'XZ', *sorted((lado * PERNA_DENTRO, lado * mp)), co, 'corpo', chanfro=0.8,
                                        seg=3)
    # a janela da ponte (atrás) e a fresta sob o trilho (na frente), vazadas
    buraco = {n: b for n, b in zip(ficha['buracosNomes'], ficha['buracos'])}
    janela = P.prisma('janela da ponte', [tuple(p) for p in buraco['janelaPonte']], 'XZ', -mp - 5.0, mp + 5.0, co, 'corpo', chanfro=0)
    for nome in ('travessa da ponte', 'corpo da ponte'):
        P.cortar(obs[nome], janela)
    fresta = P.prisma('fresta do trilho', [tuple(p) for p in buraco['frestaTrilho']], 'XZ', -mp - 5.0, mp + 5.0, co, 'corpo', chanfro=0)
    P.cortar(obs['corpo da ponte'], fresta)
    _janela_da_torre(ficha, co, obs['torre'], mt)
    _trava_do_grupo(ficha, M, [obs['torre']], mt)
    return obs


def _janela_da_torre(ficha, mat, torre, meia):
    """A janela quadrada nos lados da torre (ficha pontos.janelaTorre), rebaixada 2,5 mm, de quinas arredondadas."""
    j = ficha['pontos']['janelaTorre']
    poli = P.ret_arredondado(j['x'][0], j['x'][1], j['y'][0], j['y'][1], 1.5, 3)
    for lado in (1, -1):
        P.cortar(torre, P.prisma('janela da torre', poli, 'XZ', *sorted((lado * (meia - 2.5), lado * (meia + 5.0))), mat, 'corpo',
                                 chanfro=0), depois_do_chanfro=True)


def _trava_do_grupo(ficha, M, alvos, meia):
    """O botão de trava do grupo do cano nos dois lados da torre (ficha pontos.travaGrupoCano): o rebaixo
    redondo de 1,2 mm, o botão 0,4 mm abaixo da face com o pino dele em relevo."""
    t = ficha['pontos']['travaGrupoCano']
    (cx, cy), r = t['centro'], t['raio']
    px, py = t['pino']
    det = M['detalhes']
    for lado in (1, -1):
        rebaixo = MEC.pino_y('rebaixo da trava', cx, cy, r + 0.4, M['corpo'], 'corpo', 'base', *sorted((lado * (meia - 1.2), lado * (meia + 5.0))),
                             seg=48, chanfro=0)
        for alvo in alvos:
            P.cortar(alvo, rebaixo, depois_do_chanfro=True)
        MEC.pino_y('botão da trava', cx, cy, r - 1.0, det, 'detalhes', 'base', *sorted((lado * (meia - 2.0), lado * (meia - 0.4))),
                   seg=_seg(48, 24), chanfro=0.4)
        MEC.pino_y('pino da trava', px, py, 2.0, det, 'detalhes', 'base', *sorted((lado * (meia - 0.6), lado * (meia + 0.2))), seg=_seg(20, 10),
                   chanfro=0.2)


def corpo_do_grupo(ficha, M):
    """O corpo do grupo do cano entre os pilares (ficha pecas.receptor, 30 mm), com o canal do meio para o ressalto de
    baixo da frente do carregador: o fundo do encaixe (y = 10,9) até a frente e a rampa até o alto do corpo (13,8) em
    x = −116 — o ressalto sobe por ela quando o carregador corre para trás."""
    co = M['corpo']
    mr = ficha['vistaDeCima']['larguras']['receptor']['mm'] / 2
    rec = P.prisma('corpo do grupo do cano', [tuple(p) for p in ficha['pecas']['receptor']], 'XZ', -mr, mr, co, 'corpo', chanfro=1.0, seg=3)
    ys = [y for _, y in ficha['pecas']['receptor']]
    fundo = sorted(set(ys))[1]  # o fundo do encaixe da frente (10,9)
    topo = max(ys)
    x0, x1 = CANAL_RESSALTO['rampa']
    canal = [(TORRE_X + 0.5, fundo), (x0, fundo), (x1, topo), (x1, topo + 3.0), (TORRE_X + 0.5, topo + 3.0)]
    m = CANAL_RESSALTO['meia']
    P.cortar(rec, P.prisma('canal do ressalto', canal, 'XZ', -m, m, co, 'corpo', chanfro=0), depois_do_chanfro=True)
    return rec


# ------------------------------------------------------------------------------------------------ trilhos
def trilhos(ficha, M):
    """O trilho de cima (de −207 a −32, topo da ficha, o pescoço até o corpo da ponte) e os dois laterais (6 mm para
    fora do corpo largo), com os parafusos de sextavado interno nas fendas das pontas."""
    co, det = M['corpo'], M['detalhes']
    tc = ficha['pontos']['trilhoCima']
    topo = tc['topo']
    base = min(y for _, y in ficha['pecas']['trilhoCima'])
    PS.trilho_picatinny('trilho de cima', tc['x'][0], tc['x'][1], co, 'corpo', y=0.0, z=topo, altura=topo - base,
                        fendas=_fendas_do_trilho(ficha))
    tl = ficha['pontos']['trilhoLateral']
    xs = [x for x, _ in ficha['pecas']['trilhoLateral']]
    ys = [y for _, y in ficha['pecas']['trilhoLateral']]
    x0, x1 = min(xs), max(xs)
    zc = (min(ys) + max(ys)) / 2
    face = ficha['vistaDeCima']['larguras']['trilhoLateral']['mm'] / 2
    altura = max(tl['saliencia'], PS.PICATINNY['fundoPescoco'] + 0.5)
    fendas = PS.fendas_picatinny(x0, x1)
    fundo_fenda = face - PS.PICATINNY['fundoFenda']
    for lado in (1, -1):
        PS.trilho_picatinny(f'trilho lateral {"e" if lado > 0 else "d"}', x0, x1, co, 'corpo', y=lado * face, z=zc, giro=90.0 * lado,
                            altura=altura, fendas=fendas)
        for xp in (fendas[0], fendas[-1]):
            cab = MEC.pino_y('parafuso do trilho lateral', xp, zc, 2.3, det, 'detalhes', 'base',
                             *sorted((lado * (fundo_fenda - 0.6), lado * (fundo_fenda + 1.2))), seg=_seg(24, 12), chanfro=0.2)
            sext = [(xp + 1.1 * math.cos(math.radians(60 * k)), zc + 1.1 * math.sin(math.radians(60 * k))) for k in range(6)]
            P.cortar(cab, Q.prismas_y('sextavado do parafuso', [(sext, *sorted((lado * (fundo_fenda + 0.4), lado * (fundo_fenda + 3.0))))],
                                      det, 'detalhes', so_alto=True), depois_do_chanfro=True)


# ------------------------------------------------------------------------------------------------ cano
def _portas(ficha, mat):
    """As portas ovais do quebra-chama (ficha pontos.quebraChama.portas): três em cada fileira, as fileiras a 45° e 135°
    do +Y do Blender (em cima, dos dois lados), cada uma um estádio de `comprimento` × `largura` mm varado pela parede."""
    po = ficha['pontos']['quebraChama']['portas']
    meio_c, meia_l = po['comprimento'] / 2, po['largura'] / 2
    # o estádio de verdade: os dois semicírculos de raio meia_l ligados pelos lados compridos (o ret_arredondado deixava
    # um lado reto de 2 µm no meio de cada ponta, e a aresta de 1 µm que ficava no furo travava o chanfro da peça)
    estadio = [(c + meia_l * math.cos(math.radians(a0 + 180.0 * i / 12)), meia_l * math.sin(math.radians(a0 + 180.0 * i / 12)))
               for c, a0 in ((meio_c - meia_l, -90.0), (meia_l - meio_c, 90.0)) for i in range(13)]
    bm = bmesh.new()
    for g in po['graus']:
        a = math.radians(g)
        n = (0.0, math.cos(a), math.sin(a))
        t = (0.0, -math.sin(a), math.cos(a))
        for xc in po['x']:
            aneis = [[bm.verts.new(v3(xc + u, w * t[1] + r * n[1], w * t[2] + r * n[2])) for u, w in estadio] for r in (5.0, 14.0)]
            r0, r1 = aneis
            k = len(estadio)
            for i in range(k):
                bm.faces.new((r0[i], r0[(i + 1) % k], r1[(i + 1) % k], r1[i]))
            bm.faces.new(r0[::-1])
            bm.faces.new(r1)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return P.objeto('portas do quebra-chama', bm, mat, 'detalhes', 'base', False, (0, 0))


def cano(ficha, M):
    """O quebra-chama do jogo (o torno da ficha: o colar serrilhado atrás, a ponta arredondada, oco por dentro, com as
    portas), o cano (dentro do grupo e do quadro: a medida `cano`) e a alma de 5,7 mm, que aparece pela boca."""
    det = M['detalhes']
    tq = ficha['tornos']['quebraChama']
    seg = _seg(64, 32)
    qc = P.torno('quebra-chama', [tuple(p) for p in tq['perfil']], det, 'detalhes', 'base', seg, centro=(0.0, 0.0, tq['centroY']),
                 chanfro=0.3)
    # girado meio lado: os lados do torno fora do meio das portas (as fileiras a 45° e 135°, múltiplos de 360/64) e das
    # paredes dos sulcos do serrilhado (abaixo)
    P.rotacionar(qc, 'X', 180.0 / seg, (0.0, 0.0, tq['centroY']))
    # a boca oca antes do chanfro (a borda dela na face da frente arredondada com o resto), com os lados do torno girados
    # um quarto de lado: os vértices dela ficam a 1/4 de lado dos raios da face da frente (com 60 lados, a 0,19° deles,
    # o chanfro da borda se dobrava em cima de si) e as linhas da alma, fora do meio das portas
    boca = P.torno('boca do quebra-chama', [(-40.0, 0.0), (-40.0, 6.6), (0.6, 6.6), (0.6, 0.0)], det, 'detalhes', 'base', seg, chanfro=0)
    P.rotacionar(boca, 'X', 90.0 / seg, (0.0, 0.0, tq['centroY']))
    P.cortar(qc, boca)
    # as portas e o serrilhado do colar depois do chanfro, de borda viva (como a peça usinada), num booleano só: antes do
    # chanfro, as bordas das portas cruzam as linhas dos lados do torno e da alma em pontos quase coincidentes com os
    # vértices do estádio (a 10 µm) e o chanfro da borda se dobrava sobre si ali. O serrilhado sai pelas duas faces do
    # colar: o sulco (fundo a 0,45 mm do raio do colar, acima do raio da frente) vai 0,5 mm além do degrau da frente —
    # terminando no plano do degrau, com o anel de vértices do chanfro nele, o booleano abria o colar —, e os 36 sulcos (a
    # cada 10°) começam no alto: com as linhas do torno girado meio lado (2,8125° + k · 5,625°), as paredes deles ficam a
    # 0,27° delas no chanfro do colar (sem o giro, a parede de oito sulcos passava pelas linhas no raio de 10,7 mm)
    xs = [x for x, _ in tq['perfil']]
    colar = sorted(set(xs))[:2]
    serrilhado = PM.estrias_x('serrilhado do colar', colar[0] - 1.0, colar[1] + 0.5, max(r for _, r in tq['perfil']), 36, tq['centroY'],
                              det, 'detalhes')
    P.cortar(qc, Q._juntar([_portas(ficha, det), serrilhado]), depois_do_chanfro=True)
    tc = ficha['tornos']['cano']
    c = P.torno('cano', [tuple(p) for p in tc['perfil']], det, 'detalhes', 'base', _seg(32, 16), centro=(0.0, 0.0, tc['centroY']), chanfro=0.3)
    ta = ficha['tornos']['alma']
    P.cortar(c, P.torno('alma', [tuple(p) for p in ta['perfil']], det, 'detalhes', 'base', 16, centro=(0.0, 0.0, ta['centroY']), chanfro=0))


# ------------------------------------------------------------------------------------------------ miras
def _perfil_do_trilho(ficha, folga=0.15):
    """O corte do trilho na base de uma mira (o perfil da norma com `folga` mm, do topo do trilho até 15 mm abaixo)."""
    topo = ficha['pontos']['trilhoCima']['topo']
    return [(u + math.copysign(folga, u), v + topo + folga) for u, v in PS.perfil_picatinny(15.0)]


def _base_de_mira(nome, ficha, M, perfil, meia, x0, x1, nos):
    """A base de uma mira presa no trilho: o perfil de lado (`perfil`) na largura `meia`, o corte do trilho embaixo (as
    garras dos lados), o botão do aperto à esquerda (com o sextavado interno, só no modelo alto) e a porca à direita
    (`nos`: o (x, y) do aperto)."""
    det = M['detalhes']
    base = P.prisma(nome, perfil, 'XZ', -meia, meia, det, 'detalhes', chanfro=0.6, seg=3)
    P.cortar(base, P.prisma(f'{nome}: trilho', _perfil_do_trilho(ficha), 'YZ', x0 - 2.0, x1 + 2.0, det, 'detalhes', chanfro=0))
    bx, by = nos
    botao = MEC.pino_y(f'{nome}: aperto', bx, by, 3.6, det, 'detalhes', 'base', meia - 0.4, meia + 2.6, seg=_seg(32, 14), chanfro=0.4)
    sext = [(bx + 1.3 * math.cos(math.radians(60 * k)), by + 1.3 * math.sin(math.radians(60 * k))) for k in range(6)]
    P.cortar(botao, Q.prismas_y(f'{nome}: sextavado', [(sext, meia + 1.6, meia + 4.0)], det, 'detalhes', so_alto=True), depois_do_chanfro=True)
    porca = [(bx + 3.6 * math.cos(math.radians(30 + 60 * k)), by + 3.6 * math.sin(math.radians(30 + 60 * k))) for k in range(6)]
    Q.prismas_y(f'{nome}: porca', [(porca, -meia - 2.2, -meia + 0.4)], det, 'detalhes', chanfro=(0.3, 2))
    return base


def mira_de_tras(ficha, M):
    """A mira de trás do CS2 (ficha pecas.rebativelTras): a base no trilho até y = 99, as duas orelhas de proteção fixas
    pelo contorno de lado, o pino da dobradiça entre elas e a folha (peça `rebativel_tras`): o nó em volta do pino, a
    placa de 6 mm até o anel de 11,2 mm com a abertura de 1,8 no centro do tambor (a linha de mira) e o tambor
    serrilhado embaixo dele. A folha deita para trás entre as orelhas."""
    mt = MIRA_TRAS
    det = M['detalhes']
    contorno = [tuple(p) for p in ficha['pecas']['rebativelTras']]
    topo_trilho = ficha['pontos']['trilhoCima']['topo']
    x0, x1 = min(x for x, _ in contorno), max(x for x, _ in contorno)
    yb = mt['base_topo']
    # a traseira da base desce pela reta da ficha de (−197; 104) a (−205,5; 98,5)
    (ax, ay), (bx_, by_) = (-197.0, 104.0), (-205.5, 98.5)
    xr = ax + (yb - ay) * (bx_ - ax) / (by_ - ay)
    base = [(x0, 88.6), (x1, 88.6), (x1, yb), (xr, yb), (bx_, by_), (x0, topo_trilho)]
    _base_de_mira('base da mira de trás', ficha, M, base, mt['meia_base'], x0, x1, (-198.5, 94.2))
    # a orelha: o contorno da ficha acima da base (na ordem dele, anti-horária), da quina de baixo de trás (−205,5; 98,5)
    # pela quina de baixo da frente, subindo pela frente e voltando por cima
    tras = next(p for p in contorno if abs(p[1] - (yb - 0.5)) < 0.01)
    frente = [p for p in contorno if p[0] > -180.0 and p[1] > yb + 1.0]
    cima = [p for p in contorno if p[0] <= -180.0 and p[1] > yb + 1.0]
    orelha = [tras, (x1 - 0.2, yb - 0.5)] + frente + cima
    for lado in (1, -1):
        P.prisma('orelha da mira de trás', orelha, 'XZ', *sorted((lado * mt['orelha'][0], lado * mt['orelha'][1])), det, 'detalhes',
                 chanfro=0.5, seg=3)
    px, py = ficha['pontos']['rebativelTras']['pivo']
    MEC.pino_y('pino da mira de trás', px, py, mt['pino'], det, 'detalhes', 'base', -mt['orelha'][1], mt['orelha'][1], seg=_seg(16, 10),
               chanfro=0.1)
    # a folha
    peca = 'rebativel_tras'
    mf = mt['meia_folha']
    no = MEC.pino_y('nó da mira de trás', px, py, mt['no'], det, 'detalhes', peca, -mf, mf, seg=_seg(24, 12), chanfro=0.3)
    # o furo do pino passa pelo nó, pelo pé da placa (que nasce no eixo) e pelo tambor: nada da folha encosta no pino
    furo = MEC.pino_y('furo do nó de trás', px, py, mt['pino'] + 0.25, det, 'detalhes', peca, -mf - 1.0, mf + 1.0, seg=16, chanfro=0)
    P.cortar(no, furo)
    ax_, ay_ = ficha['pontos']['miraTras']
    ra = mt['anel']
    placa = [(-mf, py), (mf, py), (mf, ay_ - 5.4), *P.arco(0.0, ay_, ra, 0.0, 180.0, _seg(16, 10)), (-mf, ay_ - 5.4)]
    folha = P.prisma('folha da mira de trás', placa, 'YZ', *mt['folha'], det, 'detalhes', peca, chanfro=0.4, seg=3)
    P.cortar(folha, furo, depois_do_chanfro=True)
    P.cortar(folha, P.torno('abertura da mira de trás', [(mt['folha'][0] - 1.0, 0.0), (mt['folha'][0] - 1.0, mt['abertura']),
                                                         (mt['folha'][1] + 1.0, mt['abertura']), (mt['folha'][1] + 1.0, 0.0)], det,
                            'detalhes', peca, 16, centro=(0.0, 0.0, ay_), chanfro=0), depois_do_chanfro=True)
    ty, tr, tm = mt['tambor']
    dentes = 16
    estrela = [(ax_ + (tr if k % 2 == 0 else tr - 0.35) * math.cos(math.pi * k / dentes), ty + (tr if k % 2 == 0 else tr - 0.35) *
                math.sin(math.pi * k / dentes)) for k in range(2 * dentes)]
    tambor = P.prisma('tambor da mira de trás', estrela, 'XZ', -tm, tm, det, 'detalhes', peca, chanfro=0.15, seg=2)
    P.cortar(tambor, furo, depois_do_chanfro=True)


def mira_da_frente(ficha, M):
    """A mira da frente do CS2 (ficha pecas.rebativelFrente): a base no trilho até y = 104 (a rampa de trás da ficha), as
    duas orelhas do capuz fixas pelo contorno de lado, o pino entre elas e a folha (peça `rebativel_frente`): o nó em
    volta do pino, a placa de 5 mm e o poste de 1,6 × 2,4 mm até a linha de mira. A folha deita para a frente."""
    mf_ = MIRA_FRENTE
    det = M['detalhes']
    contorno = [tuple(p) for p in ficha['pecas']['rebativelFrente']]
    topo_trilho = ficha['pontos']['trilhoCima']['topo']
    x0, x1 = min(x for x, _ in contorno), max(x for x, _ in contorno)
    yb = mf_['base_topo']
    base = [(x0, 88.6), (x1, 88.6), (x1, topo_trilho), (-41.5, 102.3), (-44.5, yb), (-64.0, yb), (-64.0, 105.5), (-72.0, 105.0),
            (-75.7, 103.3), (-79.5, 100.0), (x0, topo_trilho)]
    _base_de_mira('base da mira da frente', ficha, M, base, mf_['meia_base'], x0, x1, (-72.5, 96.5))
    orelha = [(-64.0, yb - 0.5), (-44.5, yb - 0.5), (-45.7, 129.3), (-46.5, 130.0), (-60.0, 130.0), (-61.2, 129.5), (-62.7, 126.8)]
    for lado in (1, -1):
        P.prisma('orelha da mira da frente', orelha, 'XZ', *sorted((lado * mf_['orelha'][0], lado * mf_['orelha'][1])), det, 'detalhes',
                 chanfro=0.5, seg=3)
    px, py = ficha['pontos']['rebativelFrente']['pivo']
    MEC.pino_y('pino da mira da frente', px, py, mf_['pino'], det, 'detalhes', 'base', -mf_['orelha'][1], mf_['orelha'][1], seg=_seg(16, 10),
               chanfro=0.1)
    peca = 'rebativel_frente'
    m = mf_['meia_folha']
    no = MEC.pino_y('nó da mira da frente', px, py, mf_['no'], det, 'detalhes', peca, -m, m, seg=_seg(24, 12), chanfro=0.3)
    furo = MEC.pino_y('furo do nó da frente', px, py, mf_['pino'] + 0.25, det, 'detalhes', peca, -m - 1.0, m + 1.0, seg=16, chanfro=0)
    P.cortar(no, furo)
    ax_, ay_ = ficha['pontos']['miraFrente']
    placa = [(-m, py), (m, py), (m, py + 3.0), (1.6, py + 5.0), (-1.6, py + 5.0), (-m, py + 3.0)]
    # o pé da placa nasce no eixo: o furo do pino passa por ele também
    P.cortar(P.prisma('folha da mira da frente', placa, 'YZ', *mf_['folha'], det, 'detalhes', peca, chanfro=0.4, seg=3), furo,
             depois_do_chanfro=True)
    lw, lx = mf_['poste']
    P.caixa('poste da mira da frente', (ax_ - lx / 2, -lw / 2, py + 4.4), (ax_ + lx / 2, lw / 2, ay_), det, 'detalhes', peca, chanfro=0.15)


def construir(ficha, M):
    ponte(ficha, M)
    corpo_do_grupo(ficha, M)
    trilhos(ficha, M)
    cano(ficha, M)
    mira_de_tras(ficha, M)
    mira_da_frente(ficha, M)
