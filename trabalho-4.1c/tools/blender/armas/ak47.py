# AK-47 tipo 3 (receptor fresado, coronha fixa de madeira) — Fase 4.1a (desenho em docs/superpowers/specs/
# 2026-09-26-armas-realistas-design.md; vem de prova-armas-2026-09-26/blender/ak_v3.py). Construída em mm no
# referencial da ficha (tools/blender/refs/ak47.json): contornos por peça, tornos e pontos medidos na foto
# "AK-47 assault rifle.jpg" (Commons, domínio público) pela régua; as larguras e as peças que só se veem de cima ou de
# baixo vêm da planta de fábrica soviética (ficha, vistaDeCima). Lado direito da arma = -Y do Blender.
# Marcações genéricas (regra 9): letras do seletor, graduação da alça, número de série e marca de controle — nenhuma
# marca de fabricante.
import math

from . import pecas as P

ORIGEM_MM = (-551.0, 0.0)  # o pino do gatilho no eixo do cano: a origem da arma no jogo (plano da 4.1a, D1)
PECAS = ('ferrolho', 'carregador', 'gatilho', 'cao', 'seletor')
FOLGA_EMBUTIDA = 0.08  # mm entre uma peça embutida na madeira (as espigas) e o rebaixo dela: a linha do encaixe


def pivos(ficha):
    """Pivô (mm, ficha) e extras de cada peça (direções no referencial do jogo: +X boca, +Y cima, +Z direita)."""
    pt = ficha['pontos']
    return {
        'base': (ORIGEM_MM, {}),
        'ferrolho': (tuple(pt['manejo']), {'eixo': [-1.0, 0.0, 0.0]}),
        'carregador': (tuple(pt['travaCarregador']), {'eixo_giro': [0.0, 0.0, 1.0]}),
        'gatilho': (tuple(pt['pinoGatilho']), {'eixo_giro': [0.0, 0.0, 1.0]}),
        'cao': (tuple(pt['pinoCao']), {'eixo_giro': [0.0, 0.0, 1.0]}),
        'seletor': (tuple(pt['eixoSeletor']), {'eixo_giro': [0.0, 0.0, 1.0]}),
    }


def soquetes(ficha):
    """(nome, (x, y) da ficha, lado = Y do Blender em mm, rotação XYZ em graus no Blender)."""
    pt = ficha['pontos']
    j = pt['janela']
    face_direita = -ficha['vistaDeCima']['larguras']['receptor']['mm'] / 2
    return [
        ('boca', (0.0, 0.0), 0.0, (0, 0, 0)),
        # A cápsula sai pela direita, da face do receptor, um pouco para a frente e para cima: +X do soquete girado -75° em
        # Z e -15° em Y.
        ('ejecao', ((j['x0'] + j['x1']) / 2, (j['y0'] + j['y1']) / 2), face_direita, (0, -15, -75)),
        ('carregador', (-457.0, -40.0), 0.0, (0, 0, 0)),
        ('mira_tras', tuple(pt['entalheAlca']), 0.0, (0, 0, 0)),
        ('mira_frente', tuple(pt['posteMassa']), 0.0, (0, 0, 0)),
        # O +Z do soquete (o +Y no jogo) sobe pelo eixo do punho, inclinado 27,8° para trás.
        ('mao_d', (-606.0, -100.0), 0.0, (0, 27.8, 0)),
        ('mao_e', (-290.0, -30.0), 0.0, (0, 0, 0)),
    ]


# ------------------------------------------------------------------------------------------------ contas
def _entre(v, a, b):
    """0 até a, 1 a partir de b, linear no meio (a < b)."""
    return min(1.0, max(0.0, (v - a) / (b - a)))


def _suave(t):
    """Degrau suave de 0 a 1 (smoothstep)."""
    return t * t * (3.0 - 2.0 * t)


def _na_linha(pts, v):
    """Valor em v de uma polilinha [(v, valor)] ordenada por v, preso nas pontas."""
    if v <= pts[0][0]:
        return pts[0][1]
    for (va, a), (vb, b) in zip(pts, pts[1:]):
        if v <= vb:
            return a + (b - a) * (v - va) / (vb - va)
    return pts[-1][1]


def _girar(objetos, eixo, graus, pivo):
    """pecas.rotacionar em vários objetos, pulando os que não nascem neste nível (os só do modelo alto)."""
    for ob in objetos:
        if ob is not None:
            P.rotacionar(ob, eixo, graus, pivo)


def _esticar(pivo_x, graus):
    """x projetado da planta (vista de cima ou de baixo) → x da peça feita na horizontal, antes de deitá-la na
    inclinação `graus` em volta de pivo_x."""
    c = math.cos(math.radians(graus))
    return lambda x: pivo_x + (x - pivo_x) / c


def _fundo_da_coronha(contorno):
    """A linha de baixo da coronha, do canto de baixo da soleira para a frente (x crescente)."""
    i0 = min(range(len(contorno)), key=lambda i: contorno[i][1])
    fundo = [tuple(contorno[i0])]
    for x, y in contorno[i0 + 1:]:
        if x <= fundo[-1][0]:
            break
        fundo.append((x, y))
    return fundo


def _contorno_espiga(esp, frente, folga, n=8):
    """Contorno visto de cima (x projetado, y) da espiga de cima: a lâmina com a ponta redonda, os lados retos entrando na
    face de trás do receptor por uma concordância (o centro dela fica fixo; `folga` mm para fora dá o rebaixo na madeira)
    e, por dentro do receptor, reta até `frente`."""
    meia = esp['mm'] / 2 + folga
    c = esp['concordancia']
    r = c['raio'] - folga
    xcc = c['face'] - c['raio']  # centro da concordância em x; em y, ±(meia + r)
    larga = meia + r
    xc = esp['ponta'] + esp['mm'] / 2  # centro da ponta redonda
    angs = [math.radians(90.0 * i / n) for i in range(n + 1)]
    return ([(frente + folga, -larga)]
            + [(xcc + r * math.cos(t), -larga + r * math.sin(t)) for t in angs]
            + P.arco(xc, 0.0, meia, -90, -270, 16)
            + [(xcc + r * math.cos(t), larga - r * math.sin(t)) for t in reversed(angs)]
            + [(frente + folga, larga)])


def _contorno_espiga_baixo(ei, folga):
    """Contorno visto de baixo (x projetado, y) da espiga de baixo (vista pela seta A da planta): a lâmina com a ponta de
    trás redonda e o bloco largo da frente, sob o receptor; `folga` mm para fora dá o rebaixo."""
    meia = ei['mm'] / 2 + folga
    bl = ei['bloco']
    mb = bl['mm'] / 2 + folga
    xc = ei['x'][0] + ei['mm'] / 2
    xb0, xb1 = bl['x']
    return P.arco(xc, 0.0, meia, 90, 270, 16) + [(xb0 - 3.0, -meia), (xb0 - folga, -mb), (xb1 + folga, -mb),
                                                   (xb1 + folga, mb), (xb0 - folga, mb), (xb0 - 3.0, meia)]


def _charuto(x0, x1, largura, n=8):
    """Contorno (x, y) de um rasgo reto de pontas redondas, centrado em y = 0 (as estrias do tubo de gases)."""
    r = largura / 2
    return P.arco(x1 - r, 0.0, r, -90, 90, n) + P.arco(x0 + r, 0.0, r, 90, 270, n)


def _secao_do_manejo(mj, d):
    """Comprimento ao longo do cano e altura (mm) da alavanca de manejo a d mm do eixo: afina da raiz à ponta pela vista
    de cima e termina num quarto de elipse (a ponta redonda)."""
    comps = mj['comprimentos']
    d_ult, c_ult = comps[-1]
    h0, h1 = mj['altura']
    if d <= d_ult:
        return _na_linha(comps, d), h0 + (h1 - h0) * _entre(d, comps[0][0], d_ult)
    e = (d - d_ult) / (mj['ponta'] - d_ult)
    k = math.sqrt(max(0.0, 1.0 - e * e))
    return c_ult * k, h1 * (0.45 + 0.55 * k)


# ------------------------------------------------------------------------------------------------ partes
def _coronha(ficha, M):
    """Coronha de madeira e soleira de aço com os parafusos e o alçapão do estojo. Vista de cima (planta), a madeira afina
    em linha reta da soleira ao pescoço e a face de trás é um arco — o meio fica atrás dos cantos: a soleira curva
    inteira e a madeira a acompanha nos 30 mm de trás. Devolve a coronha (as espigas se embutem nela)."""
    pc, L = ficha['pecas'], ficha['vistaDeCima']['larguras']
    aco, det, madeira = M['aco'], M['aco_detalhes'], M['madeira']
    lc, ls = L['coronha'], L['soleira']
    (l_tras, l_pesc), (x_tras, x_pesc) = lc['mm'], lc['x']
    coronha = P.perfil_suave('coronha', pc['coronha'], 'XZ', -l_tras / 2, l_tras / 2, madeira, 'guarnicao', chanfro=3.4, seg=4)
    P.afinar(coronha, lambda x, z: 1.0 - (1.0 - l_pesc / l_tras) * _entre(x, x_tras, x_pesc))
    raio = ls['raioDeCima']

    def curva(y):
        """Quanto a face de trás avança para a boca (mm) a y do meio: o arco de raio `raio` visto de cima."""
        return raio - math.sqrt(max(0.0, raio * raio - y * y))
    encosto = sorted((z, x) for x, z in pc['soleira'][8:])  # a face da soleira que encosta na madeira: x pela altura

    def peso(x, z):
        """1 na face de trás da madeira, 0 a 30 mm dela: quanto da curva a madeira acompanha."""
        return min(1.0, max(0.0, 1.0 - (x - _na_linha(encosto, z)) / 30.0))
    fatias = (-17.5, -15.0, -12.0, -8.0, -4.0, 0.0, 4.0, 8.0, 12.0, 15.0, 17.5)
    P.fatiar(coronha, 'Y', fatias, onde=lambda x, y, z: peso(x - 2.0, z) > 0.0)
    P.deslocar(coronha, lambda x, y, z: (curva(y) * peso(x, z), 0.0, 0.0))
    soleira = P.prisma('soleira', pc['soleira'], 'XZ', -ls['mm'] / 2, ls['mm'] / 2, aco, 'corpo', chanfro=1.0)
    P.fatiar(soleira, 'Y', fatias)
    P.deslocar(soleira, lambda x, y, z: (curva(y), 0.0, 0.0))
    # A face de trás da soleira é inclinada de lado (avança para a boca descendo): os parafusos e o alçapão acompanham ela.
    atras = pc['soleira'][:8]

    def face_de_tras(y):
        """x da face de trás no meio (y do Blender = 0) na altura y e a inclinação dela (graus; + = avança descendo)."""
        for (xa, ya), (xb, yb) in zip(atras, atras[1:]):
            if yb <= y <= ya:
                return xa + (xb - xa) * (y - ya) / (yb - ya), math.degrees(math.atan2(xb - xa, ya - yb))
        return atras[-1][0], 0.0
    for y in (-48.0, -104.0):
        # Cabeça rente à face (0,4 mm para fora), perpendicular a ela, no meio da curva; a fenda só no modelo alto.
        xa, ang = face_de_tras(y)
        cabeca = P.torno('parafuso da soleira', [(xa - 0.4, 0), (xa - 0.4, 3.6), (xa, 3.9), (xa + 1.6, 3.9), (xa + 1.6, 0)], det,
                         'detalhes', eixo='X', centro=(0, 0, y), seg=20)
        fenda = P.caixa('fenda do parafuso', (xa - 1.0, -0.5, y - 3.2), (xa - 0.1, 0.5, y + 3.2), det, 'detalhes', chanfro=0, so_alto=True)
        P.cortar(cabeca, fenda)
        _girar((cabeca, fenda), 'Y', -ang, (xa, 0, y))
    # Alçapão do estojo de limpeza: sulco de 0,7 mm acompanhando a face de trás (e a curva dela), entre os dois parafusos.
    for y in (-56.0, -97.0):
        x = face_de_tras(y)[0]
        sulco = P.caixa('sulco do alçapão', (x - 1.0, -11.0, y - 0.3), (x + 0.7, 11.0, y + 0.3), aco, 'corpo', chanfro=0, so_alto=True)
        P.fatiar(sulco, 'Y', (-8.0, -4.0, 0.0, 4.0, 8.0))
        P.deslocar(sulco, lambda x_, y_, z_: (curva(y_), 0.0, 0.0))
        P.cortar(soleira, sulco)
    borda = [(face_de_tras(y)[0] + 0.35, y) for y in [-56.0 + (-97.0 + 56.0) * k / 12 for k in range(13)]]
    for lado in (-11.0, 11.0):
        sulco = P.tira('sulco do alçapão', borda, 1.4, 'XZ', lado - 0.3, lado + 0.3, aco, 'corpo', chanfro=0, so_alto=True)
        P.deslocar(sulco, lambda x_, y_, z_: (curva(y_), 0.0, 0.0))
        P.cortar(soleira, sulco)
    return coronha


def _espigas(ficha, M, coronha):
    """As duas espigas que prendem a coronha ao receptor, embutidas rente à madeira (planta: a vista de cima e a vista
    pela seta A, por baixo do pescoço). Cada uma é feita na horizontal, com o contorno da planta (x projetado) esticado
    pelo cosseno da inclinação, e deitada na linha da madeira; o rebaixo na coronha é o mesmo contorno com a folga do
    encaixe, cortado depois do chanfro (a aresta viva é a linha do encaixe)."""
    pc, D = ficha['pecas'], ficha['vistaDeCima']['detalhes']
    aco, det, madeira = M['aco'], M['aco_detalhes'], M['madeira']
    c = pc['coronha']
    # Espiga de cima: a linha de cima do pescoço vai da face de trás do receptor (c[2]) para trás (c[3]); a ponta da
    # frente entra 2,6 mm no receptor. O parafuso de fenda vertical atravessa a coronha até a espiga de baixo.
    (xa, za), (xb, zb) = c[2], c[3]
    inclinacao = (za - zb) / (xa - xb)
    graus = math.degrees(math.atan(inclinacao))
    esp = D['espiga']
    frente = xa + 2.6
    z0 = za + (frente - xa) * inclinacao
    estica = _esticar(frente, graus)
    lamina = P.prisma('espiga da coronha', [(estica(x), y) for x, y in _contorno_espiga(esp, frente, 0.0)], 'XY',
                      z0 - esp['espessura'], z0, aco, 'corpo', chanfro=0.4)
    rebaixo = P.prisma('rebaixo da espiga', [(estica(x), y) for x, y in _contorno_espiga(esp, frente, FOLGA_EMBUTIDA)], 'XY',
                       z0 - esp['espessura'] - FOLGA_EMBUTIDA, z0 + 3.0, madeira, 'guarnicao', chanfro=0)
    pe = D['parafusoEspiga']
    xp, rp, fe = estica(pe['x']), pe['diametro'] / 2, pe['fenda'] / 2
    cabeca = P.torno('parafuso da espiga', [(-0.5, 0), (-0.5, rp), (0.3, rp), (0.8, rp * 0.69), (0.9, 0)], det, 'detalhes',
                     seg=24, eixo='Z', centro=(xp, 0, z0))
    # A fenda atravessada, de um lado ao outro da espiga (planta).
    fenda = P.caixa('fenda do parafuso da espiga', (xp - fe, -rp - 0.3, z0 + 0.35), (xp + fe, rp + 0.3, z0 + 1.5), det,
                    'detalhes', chanfro=0, so_alto=True)
    P.cortar(cabeca, fenda)
    _girar((lamina, rebaixo, cabeca, fenda), 'Y', -graus, (frente, 0.0, z0))
    P.cortar(coronha, rebaixo, depois_do_chanfro=True)
    # Espiga de baixo: rente à linha de baixo do pescoço (a corda entre as pontas dela), com os dois parafusos.
    ei = D['espigaInferior']
    fundo = _fundo_da_coronha(c)
    xt, xf = ei['x']
    zt, zf = _na_linha(fundo, xt), _na_linha(fundo, xf)
    graus_b = math.degrees(math.atan((zf - zt) / (xf - xt)))
    estica_b = _esticar(xf, graus_b)
    baixo = P.prisma('espiga de baixo', [(estica_b(x), y) for x, y in _contorno_espiga_baixo(ei, 0.0)], 'XY',
                     zf, zf + ei['espessura'], aco, 'corpo', chanfro=0.4)
    rebaixo_b = P.prisma('rebaixo da espiga de baixo', [(estica_b(x), y) for x, y in _contorno_espiga_baixo(ei, FOLGA_EMBUTIDA)],
                         'XY', zf - 1.5, zf + ei['espessura'] + FOLGA_EMBUTIDA, madeira, 'guarnicao', chanfro=0)
    objetos = [baixo, rebaixo_b]
    rb = ei['diametroParafuso'] / 2
    for xs in ei['parafusos']:
        x = estica_b(xs)
        cab = P.torno('parafuso da espiga de baixo', [(0.5, 0), (0.5, rb), (-0.15, rb), (-0.45, rb * 0.7), (-0.55, 0)], det,
                      'detalhes', seg=24, eixo='Z', centro=(x, 0, zf))
        fen = P.caixa('fenda do parafuso da espiga de baixo', (x - 0.55, -rb - 0.3, zf - 1.2), (x + 0.55, rb + 0.3, zf - 0.25), det,
                      'detalhes', chanfro=0, so_alto=True)
        P.cortar(cab, fen)
        objetos += [cab, fen]
    _girar(objetos, 'Y', -graus_b, (xf, 0.0, zf))
    P.cortar(coronha, rebaixo_b, depois_do_chanfro=True)


def _argolas(ficha, M):
    """Argolas de bandoleira (planta): a da frente do lado esquerdo do bloco de gases, uma alça no plano transversal
    saindo para o lado; a de trás por baixo da coronha, com a placa embutida e a alça rebatida para a frente — rente,
    porque a foto 1 não mostra nada abaixo da coronha."""
    L, D = ficha['vistaDeCima']['larguras'], ficha['vistaDeCima']['detalhes']
    aco, det = M['aco'], M['aco_detalhes']
    ad = D['argolaDianteira']
    xa0, xa1 = ad['x']
    face = L['blocoDeGases']['mm'] / 2
    fio = 1.2
    P.caixa('olhal da argola dianteira', (xa0, face - 0.3, 0.3), (xa1, face + 2.2, 9.7), aco, 'corpo', chanfro=0.4)
    anel = P.ret_arredondado(face + 1.2, ad['sai'] - fio, 1.5, 8.5, 3.0, 6)
    xm = (xa0 + xa1) / 2
    P.tubo('argola dianteira', [(xm, u, v) for u, v in anel + anel[:1]], fio, det, 'detalhes', seg=10)
    # Do lado direito, a cabeça achatada do pino que prende a argola (marca '9' da planta).
    pa = D['pinoArgolaDianteira']
    P.caixa('pino da argola dianteira', (pa['x'][0], -face - pa['sai'], pa['z'][0]), (pa['x'][1], -face + 0.3, pa['z'][1]), aco, 'corpo',
            chanfro=0.4)
    fundo = _fundo_da_coronha(ficha['pecas']['coronha'])
    xs = D['argolaTraseira']['x']
    zs = _na_linha(fundo, xs)
    graus = math.degrees(math.atan2(_na_linha(fundo, xs + 5.0) - _na_linha(fundo, xs - 5.0), 10.0))
    placa = P.prisma('placa da argola traseira', P.ret_arredondado(xs - 14.0, xs + 14.0, -6.0, 6.0, 3.0), 'XY', zs - 0.15, zs + 1.2,
                     det, 'detalhes', chanfro=0.3)
    pe = P.torno('pé da argola traseira', [(0.5, 0), (0.5, 2.6), (-0.6, 2.6), (-0.9, 1.8), (-0.95, 0)], det, 'detalhes', seg=20,
                 eixo='Z', centro=(xs - 6.0, 0, zs))
    anel = P.ret_arredondado(xs - 6.0, xs + 9.0, -4.5, 4.5, 3.5, 6)
    alca = P.tubo('argola traseira', [(u, v, zs - 0.05) for u, v in anel + anel[:1]], 0.95, det, 'detalhes', seg=10)
    _girar((placa, pe, alca), 'Y', -graus, (xs, 0.0, zs))


def _tubo_de_gases(ficha, M):
    """Tubo de gases oval (a largura da planta, 17,9 mm; a altura da foto, 19,4) com o colar de trás, as seis estrias
    rasas e os oito furos de respiro (planta, vista pela esquerda, e a foto do tipo II do Armémuseum). Estrias e furos
    cortados depois do chanfro: arestas vivas de usinagem."""
    tn, L, D = ficha['tornos'], ficha['vistaDeCima']['larguras'], ficha['vistaDeCima']['detalhes']
    aco = M['aco']
    t = tn['tuboDeGases']
    zt = t['centroY']
    tubo = P.torno('tubo de gases', t['perfil'], aco, 'corpo', seg=48, centro=(0, 0, zt))
    lt = L['tuboDeGases']
    r_tubo = t['perfil'][1][1]
    r_colar = max(r for _x, r in t['perfil'])
    i_colar = next(i for i, (_x, r) in enumerate(t['perfil']) if r == r_colar)
    (xc0, xc1), (wc0, _wc1) = lt['colar']['x'], lt['colar']['mm']
    f_tubo, f_colar = lt['mm'] / (2 * r_tubo), wc0 / (2 * r_colar)
    largura = [(t['perfil'][i_colar - 1][0], f_tubo), (xc0, f_colar), (xc1, f_tubo)]
    P.afinar(tubo, lambda x, z: _na_linha(largura, x))
    a_oval, b_oval = lt['mm'] / 2, r_tubo

    def raio_oval(graus):
        """Raio da seção oval a `graus` do alto."""
        s, c = math.sin(math.radians(graus)), math.cos(math.radians(graus))
        return 1.0 / math.sqrt((s / a_oval) ** 2 + (c / b_oval) ** 2)
    et = D['estriasTuboGases']
    charuto = _charuto(et['x'][0], et['x'][1], et['largura'])
    for ang in et['angulos']:
        r = raio_oval(ang)
        for lado in (-1, 1):
            estria = P.prisma('estria do tubo de gases', charuto, 'XY', zt + r - et['profundidade'], zt + r + 3.0, aco, 'corpo',
                              chanfro=0)
            P.rotacionar(estria, 'X', -lado * ang, (0.0, 0.0, zt))
            P.cortar(tubo, estria, depois_do_chanfro=True)
    fu = D['furosTuboGases']
    r = raio_oval(fu['angulo'])
    for x in fu['x']:
        for lado in (-1, 1):
            furo = P.torno('furo do tubo de gases', [(r - 5.0, 0), (r - 5.0, fu['diametro'] / 2), (r + 4.0, fu['diametro'] / 2),
                                                     (r + 4.0, 0)], aco, 'corpo', seg=20, eixo='Z', centro=(x, 0, zt))
            P.rotacionar(furo, 'X', -lado * fu['angulo'], (0.0, 0.0, zt))
            P.cortar(tubo, furo, depois_do_chanfro=True)


def construir(ficha, M):
    """Todas as peças no nível atual (pecas.iniciar). M = materiais de fábrica (materiais.materiais_de_fabrica)."""
    pc, tn, pt, ln = ficha['pecas'], ficha['tornos'], ficha['pontos'], ficha['linhas']
    L, D = ficha['vistaDeCima']['larguras'], ficha['vistaDeCima']['detalhes']
    aco, det, aco_c, polido, madeira = M['aco'], M['aco_detalhes'], M['aco_carregador'], M['aco_polido'], M['madeira']
    lr = L['receptor']['mm'] / 2  # a face dos lados do receptor (e da tampa, rente a ele)

    # --- Coronha, soleira e as espigas embutidas; as argolas de bandoleira
    coronha = _coronha(ficha, M)
    _espigas(ficha, M, coronha)
    _argolas(ficha, M)

    # --- Receptor fresado: recorte de alívio dos dois lados, janela de ejeção com a fenda da alavanca de manejo, o rasgo
    # do botão da mola, o poço do carregador, pinos e o eixo do seletor
    rec = P.prisma('receptor', pc['receptor'], 'XZ', -lr, lr, aco, 'corpo', chanfro=0.9)
    ra = pt['recorteDeAlivio']
    for y0, y1 in ((-lr - 5.5, -lr + 2.0), (lr - 2.0, lr + 5.5)):
        P.cortar(rec, P.caixa('recorte de alívio', (ra['x0'], y0, ra['y0']), (ra['x1'], y1, ra['y1']), aco, 'corpo', chanfro=0))
    j = pt['janela']
    # A janela atravessa a parede de 3 mm e abre no vão onde corre o transportador, mais fundo que ela embaixo: pela
    # janela se vê o transportador a 1 mm da parede e, atrás da ponta dele, o escuro do receptor (foto de museu "7,62 RK
    # 54 Kalasnikov", lado direito). Um corte só, em L: dois cortes encostados deixavam degraus de 0,1 mm que o chanfro
    # do receptor dobrava (UV sobreposta no assar).
    parede = -lr + 3.0
    P.cortar(rec, P.prisma('janela e vão do transportador', [(-lr - 11.5, j['y0']), (parede, j['y0']), (parede, 0.0),
                                                             (-lr + 12.0, 0.0), (-lr + 12.0, j['y1']), (-lr - 11.5, j['y1'])],
                           'YZ', j['x0'], j['x1'], aco, 'corpo', chanfro=0))
    mj = D['manejo']
    zm0, zm1 = mj['centroY'] - mj['altura'][0] / 2 - 0.2, mj['centroY'] + mj['altura'][0] / 2 + 0.2
    P.cortar(rec, P.caixa('fenda do manejo', (j['x1'] - 1.0, -lr - 11.5, zm0), (mj['frente'] + 1.5, -lr + 3.0, zm1), aco, 'corpo',
                          chanfro=0))
    bt = D['botaoMola']
    z_botao = min(z for _x, z in pc['botaoMola'])
    P.cortar(rec, P.caixa('rasgo do botão da mola', (bt['x'][0] - 1.0, -bt['mm'] / 2 - 0.3, z_botao - 0.4),
                          (bt['x'][1] + 0.4, bt['mm'] / 2 + 0.3, 20.0), aco, 'corpo', chanfro=0))
    # Poço do carregador: o vão no fundo do receptor onde o carregador entra, com 0,3 mm de folga em volta.
    tras = [(x - 0.3, y) for x, y in pc['carregador'] if y >= -44.0 and x < -470.0]
    frente = [(x + 0.3, y) for x, y in pc['carregador'] if y >= -41.0 and x > -440.0]
    tras[0] = (tras[0][0], tras[0][1] + 0.3)
    frente[-1] = (frente[-1][0], frente[-1][1] + 0.3)
    P.cortar(rec, P.prisma('poço do carregador', tras + [(frente[0][0], -42.0)] + frente, 'XZ', -14.3, 14.3, aco, 'corpo', chanfro=0))
    for x, y in pt['pinos']:
        for lado in (-1, 1):
            P.pino('pino', x, y, 2.4, det, 'detalhes', lado=lado, de=lr, ate=lr + 0.8)
    ex, ey = pt['eixoSeletor']
    se = D['seletor']
    P.pino('eixo do seletor', ex, ey, 6.5, det, 'detalhes', lado=-1, de=lr, ate=lr + se['eixoSai'])
    # Letras do seletor logo à frente da aba, na trajetória dela (raio de 96 mm em volta do eixo): АВ no meio, ОД embaixo.
    P.gravacao('letras AB', 'АВ', -477.0, -22.5, 4.2, 'direita', -lr, 0.3, rec)
    P.gravacao('letras OD', 'ОД', -478.0, -37.0, 4.2, 'direita', -lr, 0.3, rec)
    P.gravacao('número de série', 'КЛ 4178', -545.0, -12.0, 4.0, 'esquerda', lr, 0.25, rec)
    P.gravacao('marca de controle', 'ОТК', -470.0, -33.0, 3.0, 'esquerda', lr, 0.2, rec)

    # --- Ferrolho (peça móvel). O transportador enche a janela (foto de museu "7,62 RK 54 Kalasnikov", lado direito): em
    # cima o dorso arredondado, embaixo a face lisa polida, com um vinco entre os dois (45 % da janela embaixo, 55 % em
    # cima); atrás, a parte de baixo acaba 6 mm antes da borda da janela e a de cima, em rampa, um pouco antes — ali se vê
    # o escuro do receptor. A cabeça do ferrolho com o extrator e a alavanca de manejo: vista de cima ela afina da raiz
    # até a ponta redonda, com a frente reta; de frente sai baixa (planta e foto 1)
    face, fundo = -lr + 4.0, -lr + 11.8  # a face lisa a 1 mm da parede de dentro; o fundo antes da parede do vão
    z_baixo, topo = 1.0, 18.2
    z_vinco = j['y0'] + 0.45 * (j['y1'] - j['y0'])
    raio_dorso = topo - z_vinco
    perfil = [(face, z_baixo), (face, z_vinco - 0.4)]
    perfil += P.arco(face + 0.4 + raio_dorso, z_vinco, raio_dorso, 180.0, 90.0, 10)
    perfil += [(fundo, topo), (fundo, z_baixo)]
    transp = P.prisma('transportador', perfil, 'YZ', j['x0'] - 0.5, j['x1'] + 1.0, polido, 'interno', 'ferrolho', chanfro=0.4)
    P.cortar(transp, P.caixa('ponta de baixo do transportador', (j['x0'] - 10, face - 5, z_baixo - 5),
                             (j['x0'] + 6.0, fundo + 5, z_vinco), polido, 'interno', chanfro=0))
    xa, xb = j['x0'] + 2.4, j['x0'] + 7.3  # a rampa da ponta de cima: do vinco (atrás) até y = 19 (à frente)
    k = (xb - xa) / (19.0 - z_vinco)
    P.cortar(transp, P.prisma('rampa do transportador', [(j['x0'] - 10, z_vinco - 0.3), (xa - 0.3 * k, z_vinco - 0.3),
                                                         (xa + (topo + 1 - z_vinco) * k, topo + 1), (j['x0'] - 10, topo + 1)],
                              'XZ', face - 5, fundo + 5, polido, 'interno', chanfro=0))
    P.torno('cabeça do ferrolho', [(j['x1'] - 12, 0), (j['x1'] - 12, 5.6), (j['x1'] + 4, 5.6), (j['x1'] + 4, 0)], polido, 'interno',
            'ferrolho', seg=24, centro=(0, 0, 0))
    P.caixa('extrator', (j['x1'] - 10, -6.4, 3.0), (j['x1'] + 2, -4.8, 7.0), polido, 'interno', 'ferrolho', chanfro=0.2)
    d_ult = mj['comprimentos'][-1][0]
    estacoes = [lr - 4.5] + [d for d, _c in mj['comprimentos'][:1]] + [24.0, 29.2, 35.0, 40.0, d_ult]
    estacoes += [d_ult + (mj['ponta'] - d_ult) * e for e in (0.5, 0.8, 0.95)]
    aneis = []
    for d in sorted(set(estacoes)):
        comp, h = _secao_do_manejo(mj, d)
        z0, z1 = mj['centroY'] - h / 2, mj['centroY'] + h / 2
        raio = min(1.6, 0.45 * min(comp, h))
        aneis.append([(u, -d, v) for u, v in P.ret_arredondado(mj['frente'] - comp, mj['frente'], z0, z1, raio, 4)])
    P.lofting('manejo', aneis, polido, 'interno', 'ferrolho', chanfro=(0.3, 2))

    # --- Cão (peça móvel, interno): aparece pela janela com o ferrolho atrás
    cx, cy = pt['pinoCao']
    P.prisma('cão', [(cx - 5, cy - 4), (cx + 5, cy - 4), (cx + 14, cy + 22), (cx + 18, cy + 36), (cx + 10, cy + 38), (cx + 2, cy + 16)],
             'XZ', -4.0, 4.0, polido, 'interno', 'cao', chanfro=0.4)

    # --- Tampa lisa (a AK-47 não tem nervuras), rente ao receptor: o alto plano e os ombros arredondados (planta), com o
    # entalhe de trás; o botão da mola recuperadora no rasgo do receptor, com a face de trás serrilhada
    tampa = P.prisma('tampa', pc['tampa'], 'XZ', -lr, lr, aco, 'corpo')
    lt = L['tampa']
    topo = [tuple(p) for p in pc['tampa'][1:7]]  # o perfil de cima, da frente (-399) até o degrau de trás

    def no_topo(p):
        return any(abs(p[0] - x) < 0.01 and abs(p[2] - z) < 0.01 for x, z in topo)
    P.marcar_chanfro(tampa, lambda a, b: min(abs(a[1]), abs(b[1])) > lr - 0.1 and no_topo(a) and no_topo(b))
    tampa['chanfro'] = ((lt['mm'] - lt['topoPlano']) / 2, 6)
    en = D['tampaEntalhe']
    P.cortar(tampa, P.torno('entalhe da tampa', [(10.0, 0), (10.0, en['raio']), (40.0, en['raio']), (40.0, 0)], aco, 'corpo',
                            seg=48, eixo='Z', centro=(en['x'], 0, 0)), depois_do_chanfro=True)
    botao = P.prisma('botão da mola', pc['botaoMola'], 'XZ', -bt['mm'] / 2, bt['mm'] / 2, det, 'detalhes', chanfro=0.5)
    (ax_, az_), (bx_, bz_) = pc['botaoMola'][1], pc['botaoMola'][2]  # a face de trás inclinada
    comp_face = math.hypot(bx_ - ax_, bz_ - az_)
    tx, tz = (bx_ - ax_) / comp_face, (bz_ - az_) / comp_face
    nx, nz = -tz, tx  # para fora: para trás e para cima
    s0, s1 = bt['serrilha']
    for i in range(bt['ranhuras']):
        x = s0 + (s1 - s0) * (i + 0.5) / bt['ranhuras']
        z = az_ + (x - ax_) * (bz_ - az_) / (bx_ - ax_)
        ranhura = [(x + tx * a + nx * b, z + tz * a + nz * b) for a, b in ((-0.22, -0.35), (0.22, -0.35), (0.22, 0.6), (-0.22, 0.6))]
        P.cortar(botao, P.prisma('serrilha do botão', ranhura, 'XZ', -bt['mm'] / 2 - 0.2, bt['mm'] / 2 + 0.2, det, 'detalhes',
                                 chanfro=0, so_alto=True))

    # --- Punho de madeira liso (tipo 3) com o parafuso de baixo; a espiga do guarda-mato por cima dele, o guarda-mato com
    # o rebite, o gatilho, a caixa do retém com o eixo e o retém pendurado
    punho = P.perfil_suave('punho', pc['punho'], 'XZ', -15, 15, madeira, 'guarnicao', chanfro=6.0)
    punho['chanfro'] = (6.5, 5)
    # O pé do punho é plano (y = -147,5 entre x = -616,6 e -602,4): o parafuso entra reto por ele, cabeça rente (0,2 mm).
    parafuso = P.torno('parafuso do punho', [(-0.2, 0), (-0.2, 3.4), (2.4, 3.4), (2.4, 0)], det, 'detalhes', eixo='Z', seg=20,
                       centro=(-609.5, 0, -147.5))
    P.cortar(parafuso, P.caixa('fenda do parafuso do punho', (-612.8, -0.5, -147.8), (-606.2, 0.5, -147.4), det, 'detalhes',
                               chanfro=0, so_alto=True))
    P.prisma('espiga do guarda-mato', pc['espigaGuardaMato'], 'XZ', -12.0, 12.0, aco, 'corpo', chanfro=0.6)
    P.prisma('guarda-mato', pc['guardaMato'], 'XZ', -5.5, 5.5, aco, 'corpo', chanfro=0.6)
    # Rebite da aba de trás, que encosta no fundo do receptor (pontas de dentro da perna de trás: guardaMato[-3] e [-2]).
    (xr0, zr), (xr1, _z) = pc['guardaMato'][-3], pc['guardaMato'][-2]
    P.esfera('rebite do guarda-mato', ((xr0 + xr1) / 2, 0, zr), 1.8, (1.0, 1.0, 0.45), det, 'detalhes', u=16, v=8)
    P.prisma('gatilho', pc['gatilho'], 'XZ', -3.5, 3.5, det, 'detalhes', 'gatilho', chanfro=0.5)
    P.fileira(lambda i, dx, dy: P.caixa('estria do gatilho', (-552.6 + dx, -3.6, -52.0 + dy), (-551.8 + dx, 3.6, -51.4 + dy), det, 'detalhes', 'gatilho',
                                        chanfro=0, so_alto=True), 5, (0.9, -2.2))
    P.prisma('caixa do retém', pc['caixaRetem'], 'XZ', -7.5, 7.5, aco, 'corpo', chanfro=0.6)
    P.prisma('retém do carregador', pc['retem'], 'XZ', -6.5, 6.5, det, 'detalhes', chanfro=0.5)
    xr, yr = pt['pinoRetem']
    for lado in (-1, 1):
        P.pino('eixo do retém', xr, yr, 1.6, det, 'detalhes', lado=lado, de=7.5, ate=8.1)

    # --- Carregador (peça móvel): contorno da foto (sobe por dentro do poço), base e nervuras (três perto das costas, uma
    # perto da frente)
    P.perfil_suave('carregador', pc['carregador'], 'XZ', -14, 14, aco_c, 'carregador', 'carregador', chanfro=1.2, it=1)
    rt = P.reamostrar(ln['carregadorTras'], 44)
    fr = P.reamostrar(ln['carregadorFrente'], 44)
    for f in (0.16, 0.28, 0.40, 0.82):
        linha = [(a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f) for a, b in zip(rt, fr)][4:39]
        for lado in (-1, 1):
            # Nervura estampada: um cordão de perfil redondo meio embutido na chapa (sai 0,9 mm), e não uma tira de quina viva.
            P.tubo('nervura do carregador', [(x, lado * 13.5, z) for x, z in linha], 1.4, aco_c, 'carregador', 'carregador', seg=10)
    b0, b1 = ln['baseDoCarregador']
    ex_, ey_ = b1[0] - b0[0], b1[1] - b0[1]
    comp_base = math.hypot(ex_, ey_)
    ex_, ey_ = ex_ / comp_base, ey_ / comp_base
    nx_, ny_ = -ey_, ex_
    P.prisma('base do carregador', [(b0[0] - ex_ * 1.5, b0[1] - ey_ * 1.5), (b1[0] + ex_ * 1.5, b1[1] + ey_ * 1.5),
                                    (b1[0] + ex_ * 1.5 + nx_ * 7, b1[1] + ey_ * 1.5 + ny_ * 7), (b0[0] - ex_ * 1.5 + nx_ * 7, b0[1] - ey_ * 1.5 + ny_ * 7)],
             'XZ', -15.5, 15.5, aco_c, 'carregador', 'carregador', chanfro=1.0)

    # --- Seletor (peça móvel, posição de segurança) rente ao lado direito, com a aba da frente dobrada para fora (planta)
    xd0, xd1 = se['aba']['dobra']
    sai = se['aba']['sai'] - 2.0  # a partir da face de fora da alavanca (2 mm de chapa)
    seletor = P.prisma('seletor', pc['seletor'], 'XZ', -lr - 2.0, -lr, det, 'detalhes', 'seletor', chanfro=0.5)
    P.fatiar(seletor, 'X', [xd0 + (xd1 - xd0) * k / 10 for k in range(1, 11)])
    P.deslocar(seletor, lambda x, y, z: (0.0, -sai * _suave(_entre(x, xd0, xd1)), 0.0))

    # --- Alça (anatomia conferida na foto de perto "File:AK47-rear-sight.jpg", Erik Gregg, CC BY-SA 2.0; larguras da
    # planta): a base com as duas bochechas da frente, onde passa o eixo da folha; a folha gira nesse eixo e tem o entalhe
    # em U na lâmina da ponta de trás; o cursor, com um botão de trava redondo de cada lado, fica logo à frente da lâmina
    # na posição de combate (П); a graduação 1–8 cresce para a frente, os ímpares no lado direito e os pares no esquerdo,
    # cada número ao lado do entalhe da trava daquele lado. O que sobe acima da linha de mira (a 44,4 mm do eixo do cano na
    # altura do cursor) fica nos lados — os botões e as bochechas —, e o meio fica baixo: a visada pelo entalhe fica livre
    # até o poste da massa.
    lb = L['baseAlca']['mm'] / 2
    P.prisma('base da alça', pc['baseAlca'], 'XZ', -lb, lb, aco, 'corpo', chanfro=0.9)
    for y0, y1 in ((-9.0, -7.2), (7.2, 9.0)):
        P.prisma('bochecha da alça', pc['bochechasAlca'], 'XZ', y0, y1, aco, 'corpo', chanfro=0.5)
    lf = L['folhaAlca']['mm'] / 2
    folha = P.prisma('folha da alça', pc['folhaAlca'], 'XZ', -lf, lf, det, 'detalhes', chanfro=0.5)
    ex_a, ey_a = pt['entalheAlca']
    P.cortar(folha, P.caixa('entalhe da alça', (ex_a - 3.0, -1.1, ey_a + 1.1), (ex_a + 3.0, 1.1, ey_a + 5.0), det, 'detalhes', chanfro=0))
    P.cortar(folha, P.torno('fundo do entalhe', [(ex_a - 3.0, 0), (ex_a - 3.0, 1.1), (ex_a + 3.0, 1.1), (ex_a + 3.0, 0)], det, 'detalhes',
                            seg=16, centro=(0, 0, ey_a + 1.1)))

    def topo_da_folha(x):
        """Z da face de cima da folha em x (ela sobe de 42,3 em x = -383 a 43,8 em x = -363,3)."""
        return 42.3 + (43.8 - 42.3) * min(1.0, max(0.0, (x + 383.0) / (383.0 - 363.3)))
    for i, x in enumerate((-379.5, -376.75, -374.0, -371.25, -368.5, -365.75, -363.0, -360.25)):
        lado = -1 if i % 2 == 0 else 1
        y0, y1 = (-lf - 0.55, -6.0) if lado < 0 else (6.0, lf + 0.55)
        P.cortar(folha, P.caixa('entalhe da trava', (x - 0.6, y0, 36.0), (x + 0.6, y1, 50.0), det, 'detalhes', chanfro=0))
        # Algarismo de 1,8 mm centrado em (x, ±3,4), lido de trás da arma (o pé do número para a coronha).
        P.gravacao(f'graduação {i + 1}', str(i + 1), x - 0.9, 3.4 * lado + 0.5, 1.8, 'cima', topo_da_folha(x), 0.3, folha, rotacao=-90)
    cursor = pc['cursorAlca']
    P.prisma('cursor da alça', cursor, 'XZ', -8.2, 8.2, det, 'detalhes', chanfro=0.5)
    xb = (min(p[0] for p in cursor) + max(p[0] for p in cursor)) / 2
    for lado in (-1, 1):
        # O botão redondo (r 3,5, centro a 42,5) é o disco escuro da foto, de -391 a -383, com o topo em 46; de ponta a
        # ponta dos botões, a largura da planta.
        P.pino('botão do cursor', xb, 42.5, 3.5, det, 'detalhes', lado=lado, de=8.2, ate=L['cursorAlca']['mm'] / 2)
    fx, fz = pt['eixoFolha']
    for lado in (-1, 1):
        P.pino('eixo da folha', fx, fz, 1.6, det, 'detalhes', lado=lado, de=9.0, ate=9.5)

    # --- Guarda-mãos de madeira (fresta entre eles), afinando para a frente como na planta; o de baixo entra na braçadeira.
    # Braçadeiras e o retentor do guarda-mão (lado direito)
    gs = L['guardaMaoSuperior']
    (ls0, ls1), (xs0, xs1) = gs['mm'], gs['x']
    sup = P.prisma('guarda-mão superior', pc['guardaMaoSuperior'], 'XZ', -ls0 / 2, ls0 / 2, madeira, 'guarnicao', chanfro=6.0)
    sup['chanfro'] = (6.5, 5)
    P.afinar(sup, lambda x, z: 1.0 - (1.0 - ls1 / ls0) * _entre(x, xs0, xs1))
    gi = L['guardaMaoInferior']
    (li0, li1), (xi0, xi1) = gi['mm'], gi['x']
    lbr = L['bracadeira']['mm']
    inf = P.prisma('guarda-mão inferior', pc['guardaMaoInferior'], 'XZ', -li0 / 2, li0 / 2, madeira, 'guarnicao', chanfro=3.2)
    inf['chanfro'] = (3.6, 4)
    x_bracadeira = min(p[0] for p in pc['bracadeira'])
    largura_inf = [(xi0, 1.0), (xi1, li1 / li0), (x_bracadeira, (lbr - 1.8) / li0)]  # a ponta cabe na braçadeira (0,9 mm de cada lado)
    # Vértices em cada quebra do afinamento: sem eles, a face do lado (um n-gon só) liga a traseira à ponta e afina torto.
    P.fatiar(inf, 'X', [x for x, _f in largura_inf])
    P.afinar(inf, lambda x, z: _na_linha(largura_inf, x))
    P.prisma('braçadeira', pc['bracadeira'], 'XZ', -lbr / 2, lbr / 2, aco, 'corpo', chanfro=1.0)
    P.prisma('braçadeira do tubo', pc['bracadeiraTubo'], 'XZ', -12.5, 12.5, aco, 'corpo', chanfro=1.2)
    P.prisma('retentor do guarda-mão', [(-374, -2), (-362, -2), (-360, 6), (-376, 6)], 'XZ', -lr - 1.8, -lr, det, 'detalhes', chanfro=0.4)
    P.pino('eixo do retentor', -368.0, 2.0, 2.2, det, 'detalhes', lado=-1, de=lr + 1.8, ate=lr + 2.6)

    # --- Cano (mais grosso atrás do bloco de gases), o bloco em frente à braçadeira, tubo de gases, bloco de gases, vareta,
    # massa, porca e a alma
    c = tn['cano']
    cano = P.torno('cano', c['perfil'], aco, 'corpo', seg=48, centro=(0, 0, c['centroY']))
    # O bloco em frente à braçadeira vai de baixo do cano até o tubo de gases (vista pela esquerda da planta; a foto o mostra
    # cheio): de cima, o lábio de trás largo e, depois de uma concordância, mais estreito até a frente.
    cgl = L['colarGuardaMao']
    (wl, wf), (xk0, xk1) = cgl['mm'], cgl['concordancia']  # o lábio vai da traseira do bloco até o começo da concordância
    colar = P.prisma('colar do guarda-mão', pc['colarGuardaMao'], 'XZ', -wl / 2, wl / 2, aco, 'corpo', chanfro=0.6)
    P.fatiar(colar, 'X', [xk0 + (xk1 - xk0) * k / 8 for k in range(9)])
    P.afinar(colar, lambda x, z: (wf + (wl - wf) * (1.0 - _entre(x, xk0, xk1)) ** 2) / wl)
    _tubo_de_gases(ficha, M)
    lg = L['blocoDeGases']['mm'] / 2
    P.prisma('bloco de gases', pc['blocoDeGases'], 'XZ', -lg, lg, aco, 'corpo', chanfro=1.2)
    P.prisma('guia da vareta', pc['guiaVareta'], 'XZ', -6, 6, aco, 'corpo', chanfro=0.8)
    v = tn['vareta']
    P.torno('vareta', v['perfil'], det, 'detalhes', seg=20, centro=(0, 0, v['centroY']))
    lbm = L['baseMassa']['mm'] / 2
    P.prisma('base da massa', pc['baseMassa'], 'XZ', -lbm, lbm, aco, 'corpo', chanfro=1.0)
    # Torre da massa: a janela logo acima do cano, o tambor do poste na horizontal (a deriva ajusta ele de lado) e as
    # orelhas saindo da própria torre, com o vão aberto em volta do poste — pela mira, "( | )".
    tm = L['torreMassa']
    lt_ = tm['mm'] / 2
    torre = P.prisma('torre da massa', pc['torreMassa'], 'XZ', -lt_, lt_, aco, 'corpo', chanfro=0.8)
    P.cortar(torre, P.prisma('janela da torre', pc['janelaTorre'], 'XZ', -lt_ - 1.2, lt_ + 1.2, aco, 'corpo', chanfro=0))
    tb = pt['tamborMassa']
    P.cortar(torre, P.caixa('vão das orelhas', (-40.0, -tm['vao'] / 2, tb['y'] + tb['raio']), (-12.0, tm['vao'] / 2, 60.0), aco, 'corpo',
                            chanfro=0))
    # O tambor sai 0,2 mm de cada lado da torre (as pontas dele aparecem nas faces).
    P.pino('tambor da massa', tb['x'], tb['y'], tb['raio'], det, 'detalhes', lado=-1, de=-lt_ - 0.2, ate=lt_ + 0.2)
    px, py = pt['posteMassa']
    P.torno('poste da massa', [(tb['y'], 0), (tb['y'], 1.1), (py, 1.1), (py, 0)], det, 'detalhes', seg=16, eixo='Z', centro=(px, 0, 0))
    po = tn['porca']
    porca = P.torno('porca da boca', po['perfil'], aco, 'corpo', seg=48, centro=(0, 0, po['centroY']), chanfro=0.4)
    al = tn['alma']
    alma = P.torno('alma', al['perfil'], aco, 'corpo', seg=24, centro=(0, 0, al['centroY']))
    P.cortar(porca, alma)
    P.cortar(cano, alma)
