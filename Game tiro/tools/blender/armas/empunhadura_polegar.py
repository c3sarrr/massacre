# O polegar do solver de empunhadura (Fase 4.1b; desenho em docs/superpowers/specs/2026-09-26-4.1b-luvas-e-
# empunhadura-design.md, seção 6.2): a polpa do polegar num alvo — a superfície de outra parte da mão nas poses de teste
# (as costas das falanges médias no punho fechado), a da arma na pega — e o polegar pousando nele até encostar.
#  - o alvo: um ponto de superfície e a normal dela (para fora); nos dedos, o raio que sai do meio do osso da falange
#    média pelas costas dele (o −Z do osso na pose) até a superfície da luva posada (maos_correcoes.Modelo), saindo
#    pelo protetor de borracha se houver um por cima;
#  - a polpa: o ponto da superfície da luva na frente do osso distal do polegar, a 55 % dele (o raio de repouso pelo
#    lado da polpa, o +Z do osso), preso ao osso — o skin ali é todo do polegar_3;
#  - a IK: os cinco graus do polegar — a abdução palmar, a flexão e a rotação axial da CMC (a pronação que acompanha a
#    oposição, Cooney 1981), a flexão da MCP e a da IP — dentro dos limites da ficha, pela cinemática da cadeia (as
#    matrizes de repouso dos ossos e a da mão posada, sem o Blender a cada tentativa), minimizando a distância da polpa
#    ao alvo, o desvio da polpa de ficar de frente para ele (15 mm por unidade de 1 + cos entre o lado da polpa e a
#    normal do alvo) e a entrada do polegar nos dedos (5 mm por mm de penetração entre as cápsulas de maos_capsulas.py,
#    com a seção achatada medida na luva, e 1 mm de tolerância para o encosto no alvo); uma grade de 10° (a rotação em
#    três passos) e depois a busca de padrão até 0,25°. Sem as cápsulas, a IK passava a falange proximal do polegar pela
#    ponta do indicador, que no punho fica escondida contra a palma por trás do polegar;
#  - o contato, pela malha: o polegar chega pela normal do alvo, como quem pousa o dedo — a mesma IK, local, a partir
#    da solução, com a polpa 6 mm acima do alvo (12, 18, 24 mm se ali ainda cruzar a mão), e os cinco graus seguindo
#    em linha dessa pose até a do alvo e metade além, parando no contato (bisseção até 0,05° no grau que mais anda);
#    depois, assenta: a MCP e a IP fecham até encostar (o primeiro toque costuma ser a falange proximal deitando no
#    indicador; a MCP leva o polegar por cima dos dedos e a IP desce a polpa sobre eles — com a IP primeiro, ela ia ao
#    limite no ar e o polegar virava um gancho);
#  - o relatório traz os ângulos totais, os da IK, o encosto do lado da polpa (a menor distância dos vértices do osso
#    distal do lado da polpa, o +Z dele no repouso, à superfície do alvo — os triângulos dele na pose; um ponto só, o
#    centro da polpa, cai no vão entre dois dedos quando o polegar deita de través sobre eles), a distância do centro
#    da polpa ao ponto do alvo, se encostou e de que altura chegou.
#  - na pega das armas (empunhadura_pega.py), a arma entra: na IK, os três ossos do polegar como cápsulas de seção
#    medida contra a superfície dela, e depois um refino pela busca de padrão com a entrada de verdade dos vértices do
#    polegar e da tenar (a malha refeita a cada avaliação: a pele da tenar não cabe na cápsula do metacarpo) e com a
#    dobra da tenar na palma (o metacarpo do polegar contra ela, os pares que no repouso estavam a mais de
#    empunhadura.PERTO_MM: com o polegar fechado no plano da palma — o de apoio da pistola, deitado na armação —, a
#    pele do fim do metacarpo e da base da falange proximal passava 4 a 6 mm por dentro da borda da palma junto da
#    cabeça do metacarpo do indicador, e a validação da luva reprovava; a mão de verdade encosta ali); o alvo,
#    quando a regra pede um lado (o polegar direito cruzando para o lado esquerdo do punho), é escolhido pela própria
#    IK — a polpa encostada na arma, de frente para ela, o mais longe possível para aquele lado (alvo_na_arma); e o
#    polegar assenta sem caminho de chegada (_assentar_na_arma): erguido pela normal ele dava ainda mais a volta e
#    cruzava o punho;
#  - o polegar deitado (a mão da frente, os polegares da pistola) e a espera erguida estão em
#    empunhadura_polegar_deitado.py.
# Unidades: mm e graus além do repouso (os totais no relatório); o rig em metros no Blender.
import itertools
import math

from mathutils import Quaternion, Vector
from mathutils.bvhtree import BVHTree

from . import empunhadura, maos_capsulas, maos_rig
from .maos import DEDOS4
from .maos_capsulas import mm
from .unidades import S

OSSOS = ('polegar_1', 'polegar_2', 'polegar_3')
GRAUS = ('abducao', 'cmc', 'rotacao', 'mcp', 'ip', 'desvio')
PESO_NORMAL_MM = 15.0
PESO_COLISAO = 5.0
TOLERANCIA_ENCOSTO_MM = 1.0
GRADE_GRAUS = 10.0
PASSO_INICIAL = 5.0
PASSO_FINAL = 0.25
POLPA_T = 0.55
CAMADA_MM = 4.0  # até onde o raio segue saindo por peças por cima da superfície (o protetor de borracha)
ACIMA_MM = (6.0, 12.0, 18.0, 24.0)  # as alturas da chegada, pela normal do alvo
ALEM = 0.5  # o caminho segue além da pose do alvo (a fração dele) até encostar
LIVRE = ('polegar_2', 'polegar_3')  # a parte do polegar que sai da mão (o metacarpo é a tenar, palma)
DEDOS = tuple(f'{d}_{i}' for d in DEDOS4 for i in (1, 2, 3))  # as cápsulas dos dedos que o polegar não atravessa
TENAR = ('polegar_1', 'mao')  # a tenar: com o polegar (LIVRE), os vértices do refino pela malha na pega
PASSO_REFINO = 2.0
PESO_MALHA = 30.0  # a entrada da malha do polegar e da tenar na arma, no refino: praticamente uma restrição
PESO_EIXO_MM = 20.0  # uma falange fora do eixo pedido (mão da frente): mm por unidade de 1 − cos
# as partidas do polegar deitado sem `inicio`: os melhores pontos da grade, a pelo menos DISTANCIA_CANDIDATOS graus uns
# dos outros no grau que mais difere (dois passos da grade: os vizinhos do melhor caem no mesmo vale)
CANDIDATOS_DEITADO = 6
DISTANCIA_CANDIDATOS = 20.0


def limites(mao):
    """{grau: (mínimo, máximo)} dos seis graus do polegar além do repouso: a AAOS da ficha menos o repouso (a CMC
    tem a flexão de repouso zero; o polegar de repouso está na abdução palmar e nas flexões da ficha), a rotação axial
    da CMC (Cooney, do repouso para a pronação) e o desvio lateral da MCP com a junta reta (Bookman & Fam; o repouso é
    sem desvio) — a flexão dela fecha o desvio (o efeito came: no_came)."""
    lim, rep = mao.f['limites']['polegar'], mao.rep
    rot = mao.f['rotacaoDoPolegar']['cmc']
    desvio = mao.f['desvioDoPolegar']['mcp']
    return {'abducao': (lim['cmcAbducao'][0] - rep['polegarAbducao'], lim['cmcAbducao'][1] - rep['polegarAbducao']),
            'cmc': (float(lim['cmcFlexao'][0]), float(lim['cmcFlexao'][1])), 'rotacao': (float(rot[0]), float(rot[1])),
            'mcp': (lim['mcp'][0] - rep['polegarMcp'], lim['mcp'][1] - rep['polegarMcp']),
            'ip': (lim['ip'][0] - rep['polegarIp'], lim['ip'][1] - rep['polegarIp']),
            'desvio': (float(desvio[0]), float(desvio[1]))}


def faixa_do_desvio(lim, mcp):
    """(mínimo, máximo) do desvio da MCP com a flexão `mcp` (além do repouso): a faixa da ficha com a junta reta (a
    flexão total zero, o mínimo da AAOS), caindo em linha até zero na flexão máxima — os colaterais da MCP, frouxos com
    ela reta e esticados com ela dobrada (o efeito came, Bookman & Fam)."""
    lo, hi = lim['mcp']
    frac = min(1.0, max(0.0, (hi - mcp) / (hi - lo)))
    return lim['desvio'][0] * frac, lim['desvio'][1] * frac


def no_came(g, lim):
    """Os graus `g` com o desvio da MCP dentro da faixa que a flexão dela deixa (faixa_do_desvio)."""
    a, b = faixa_do_desvio(lim, g['mcp'])
    if a <= g['desvio'] <= b:
        return g
    return dict(g, desvio=min(max(g['desvio'], a), b))


def totais(mao, g):
    """Os graus do polegar (além do repouso) em ângulos totais na junta, arredondados para o relatório."""
    rep = mao.rep
    return {'abducao': round(g['abducao'] + rep['polegarAbducao'], 2), 'cmc': round(g['cmc'], 2),
            'rotacao': round(g['rotacao'], 2), 'mcp': round(g['mcp'] + rep['polegarMcp'], 2),
            'ip': round(g['ip'] + rep['polegarIp'], 2), 'desvio': round(g['desvio'], 2)}


def _malha(pts, tris):
    return BVHTree.FromPolygons([tuple(p) for p in pts], tris)


def _para_fora(bvh, origem, direcao):
    """O ponto da superfície na saída do raio de dentro da luva: a primeira face que ele cruza e, se houver uma peça por
    cima (o protetor de borracha, até CAMADA_MM adiante), a face de fora dela."""
    co, _n, _i, _d = bvh.ray_cast(origem, direcao)
    if co is None:
        raise RuntimeError(f'o raio de {tuple(round(c, 1) for c in origem)} não sai da luva')
    while True:
        prox, _n, _i, _d = bvh.ray_cast(co + direcao * 0.01, direcao, CAMADA_MM)
        if prox is None:
            return co
        co = prox


class Cadeia:
    """A cadeia do polegar para a IK: a mão posada (o pai do polegar_1 e as cápsulas dos dedos), as matrizes de repouso
    dos três ossos (mm), o eixo e o sinal da abdução, a polpa no referencial do osso distal e as seções das cápsulas."""

    def __init__(self, col, mao, pose_mao):
        rig, lado = col.rig, col.lado
        self.eixo_ab, self.sinal_ab = maos_rig.eixo_abducao_do_polegar(mao, rig)
        ossos = [rig.data.bones[f'{o}_{lado}'] for o in OSSOS]
        rep = [mm(b.matrix_local) for b in ossos]
        pai = ossos[0].parent
        self.rel = [mm(pai.matrix_local).inverted() @ rep[0], rep[0].inverted() @ rep[1], rep[1].inverted() @ rep[2]]
        self.comp = [b.length / S for b in ossos]
        self.secoes = maos_capsulas.Secoes(col)
        maos_rig.posar(rig, pose_mao)
        self.pai = mm(rig.pose.bones[pai.name].matrix)
        self.dedos = []
        for o in DEDOS:
            pb = rig.pose.bones[f'{o}_{lado}']
            self.dedos.append(maos_capsulas.Capsula(self.secoes, o, mm(pb.matrix), pb.bone.length / S))
        maos_rig.posar(rig, {})
        # a polpa de repouso: do meio do osso distal (a 55 %) pelo lado da polpa até a superfície da luva de repouso
        bvh = _malha(col.modelo.pontos({}), col.tris)
        m3 = rep[2]
        dentro = m3 @ Vector((0.0, self.comp[2] * POLPA_T, 0.0))
        lado_da_polpa = (m3.to_3x3() @ Vector((0.0, 0.0, 1.0))).normalized()
        self.polpa = m3.inverted() @ _para_fora(bvh, dentro, lado_da_polpa)
        # os vértices do lado da polpa do osso distal (os de que ele é o dono, com o +Z do osso para fora no repouso)
        para_local = m3.inverted()
        pts = col.modelo.pontos({})
        self.lado_da_polpa = [i for i, dono in enumerate(col.dono) if dono == OSSOS[2] and (para_local @ pts[i]).z > 0.0]

    def rotacoes(self, g):
        """{osso: quaternion} do polegar com os graus `g` (além do repouso): a CMC gira a pronação (em volta do
        próprio metacarpo; na mão direita, negativa no Y do osso), a flexão e depois a abdução (em volta do eixo preso à
        palma), como empunhadura.Mao.pose."""
        q1 = (Quaternion(self.eixo_ab, math.radians(self.sinal_ab * g['abducao'])) @ empunhadura._flexao(g['cmc'])
              @ empunhadura._rotacao(-self.sinal_ab * g['rotacao']))
        # a MCP como empunhadura.Mao.pose: a flexão depois da abertura (o desvio lateral, em volta do Z do osso)
        q2 = empunhadura._flexao(g['mcp']) @ empunhadura._abertura(g['desvio'])
        return {'polegar_1': q1, 'polegar_2': q2, 'polegar_3': empunhadura._flexao(g['ip'])}

    def matrizes(self, g):
        """As matrizes dos três ossos do polegar (mm) com os graus `g`."""
        q = self.rotacoes(g)
        m, ms = self.pai, []
        for rel, osso in zip(self.rel, OSSOS):
            m = m @ rel @ q[osso].to_matrix().to_4x4()
            ms.append(m)
        return ms

    def polpa_em(self, g, ms=None):
        """(o ponto da polpa, o lado da polpa) com os graus `g`."""
        m = (ms or self.matrizes(g))[2]
        return m @ self.polpa, (m.to_3x3() @ Vector((0.0, 0.0, 1.0))).normalized()

    def penetracao(self, ms):
        """A soma dos quadrados das entradas (mm, além da tolerância do encosto) das cápsulas da falange proximal e da
        distal do polegar nas dos dedos."""
        soma = 0.0
        for k in (1, 2):
            polegar = maos_capsulas.Capsula(self.secoes, OSSOS[k], ms[k], self.comp[k])
            for dedo in self.dedos:
                entra = maos_capsulas.encosto(self.secoes, polegar, dedo) - TOLERANCIA_ENCOSTO_MM
                if entra > 0.0:
                    soma += entra * entra
        return soma


def osso_do_alvo(chave):
    """O osso de uma chave do alvo do polegar: o dedo sozinho é a falange média dele (`indicador` → `indicador_2`); com
    a falange, ela (`indicador_3`, a distal: a faca, em que o cabo grosso leva a média para baixo do cabo)."""
    return chave if chave[-2:] in ('_1', '_2', '_3') else f'{chave}_2'


def dedo_do_alvo(chave):
    """O dedo de uma chave do alvo do polegar (`indicador_3` → `indicador`)."""
    return chave[:-2] if chave[-2:] in ('_1', '_2', '_3') else chave


def alvo_nas_falanges(col, pose, pesos):
    """(ponto, normal para fora) do alvo nas costas das falanges de `pesos` ({dedo ou falange: peso}; o dedo sozinho é a
    falange média) na pose: a média ponderada dos pontos de saída dos raios pelas costas de cada uma e das direções
    deles."""
    rig, lado = col.rig, col.lado
    maos_rig.posar(rig, pose)
    bvh = _malha(col.modelo.pontos(pose), col.tris)
    ponto, normal, soma = Vector(), Vector(), 0.0
    for chave, peso in pesos.items():
        pb = rig.pose.bones[f'{osso_do_alvo(chave)}_{lado}']
        m = mm(pb.matrix)
        meio = m @ Vector((0.0, pb.bone.length / S * 0.5, 0.0))
        costas = -(m.to_3x3() @ Vector((0.0, 0.0, 1.0))).normalized()
        ponto += _para_fora(bvh, meio, costas) * peso
        normal += costas * peso
        soma += peso
    maos_rig.posar(rig, {})
    return ponto / soma, normal.normalized()


def _entrada_na_arma(cadeia, ms, na):
    """A soma dos quadrados das entradas (mm, além da tolerância do encosto) dos três ossos do polegar na arma, como
    cápsulas de seção medida (maos_capsulas.py): em cinco pontos do eixo de cada um, o raio da seção na direção da
    superfície mais perto contra a distância a ela (o eixo dentro da arma soma a profundidade). O metacarpo entra: sem
    ele, a abdução levava a tenar para dentro das costas do punho."""
    soma = 0.0
    for k, osso in enumerate(OSSOS):
        m = na.encaixe @ ms[k]
        para_local = m.to_3x3().inverted()
        alcance = cadeia.secoes.maior(osso) + 2.0
        for t in (0.1, 0.3, 0.5, 0.7, 0.9):
            q = m @ Vector((0.0, cadeia.comp[k] * t, 0.0))
            r = na.arma.bvh.find_nearest(q, alcance)
            if r[0] is None:
                continue
            co, n, _i, d = r
            dentro = (q - co).dot(n) < 0.0
            direcao = (q - co) if dentro else (co - q)
            if direcao.length < 1e-9:
                direcao = -n
            raio = cadeia.secoes.raio(osso, para_local @ direcao)
            entra = (raio + d if dentro else raio - d) - TOLERANCIA_ENCOSTO_MM
            if entra > 0.0:
                soma += entra * entra
    return soma


def _direcao_distal(ms):
    """Para onde aponta a falange distal (o +Y do osso), unitária, no referencial das matrizes."""
    return (ms[2].to_3x3() @ Vector((0.0, 1.0, 0.0))).normalized()


def _custo(cadeia, g, alvo, normal, na=None, eixo=None):
    ms = cadeia.matrizes(g)
    p, lado = cadeia.polpa_em(g, ms)
    c = ((p - alvo).length_squared + (PESO_NORMAL_MM * (1.0 + lado.dot(normal))) ** 2
         + PESO_COLISAO ** 2 * cadeia.penetracao(ms))
    if na is not None:
        c += PESO_COLISAO ** 2 * _entrada_na_arma(cadeia, ms, na)
    if eixo is not None:
        c += (PESO_EIXO_MM * (1.0 - _direcao_distal(ms).dot(eixo))) ** 2
    return c


def _padrao(custo_de, lim, melhor, custo, passo=PASSO_INICIAL):
    while passo >= PASSO_FINAL:
        melhorou = False
        for grau in GRAUS:
            for s in (1.0, -1.0):
                g = dict(melhor)
                g[grau] = min(max(g[grau] + s * passo, lim[grau][0]), lim[grau][1])
                g = no_came(g, lim)
                c = custo_de(g)
                if c < custo - 1e-9:
                    melhor, custo, melhorou = g, c, True
        if not melhorou:
            passo /= 2
    return melhor


def _grade(custo_de, lim):
    """[(custo, graus)] da grade de 10° (a rotação em três passos), do menor custo para o maior."""
    def valores(a, b):
        n = max(1, math.ceil((b - a) / GRADE_GRAUS))
        return [a + (b - a) * k / n for k in range(n + 1)]

    pontos = [dict(zip(GRAUS, combinacao)) for combinacao in itertools.product(*(valores(*lim[k]) for k in GRAUS))]
    pontos = [g for g in pontos if no_came(g, lim) is g]  # os do desvio que a flexão da MCP não deixa ficam de fora
    return sorted(((custo_de(g), g) for g in pontos), key=lambda cg: cg[0])


def minimizar(custo_de, lim, inicio=None):
    """Os graus do polegar (além do repouso) de menor `custo_de(g)`: a grade de 10° (a rotação em três passos) e a busca
    de padrão até 0,25° (só a busca, a partir de `inicio`, se vier: a solução perto de outra)."""
    if inicio is not None:
        melhor, custo = dict(inicio), custo_de(inicio)
    else:
        custo, melhor = _grade(custo_de, lim)[0]
    return _padrao(custo_de, lim, melhor, custo)


def partidas_da_grade(custo_de, lim, n=None, distancia=None):
    """Os `n` melhores pontos da grade, cada um a pelo menos `distancia` graus (no grau que mais difere) dos escolhidos
    antes, cada um levado pela busca de padrão: as partidas do polegar deitado, em ordem de custo."""
    n, distancia = n or CANDIDATOS_DEITADO, distancia or DISTANCIA_CANDIDATOS
    escolhidos = []
    for c, g in _grade(custo_de, lim):
        if all(max(abs(g[k] - e[k]) for k in GRAUS) >= distancia for e in escolhidos):
            escolhidos.append(g)
            if len(escolhidos) == n:
                break
    return [_padrao(custo_de, lim, g, custo_de(g)) for g in escolhidos]


def _metacarpo_e_palma(col):
    """(os triângulos do metacarpo do polegar, os da palma) da luva, guardados nela."""
    if not hasattr(col, '_metacarpo_e_palma'):
        col._metacarpo_e_palma = (col.triangulos({OSSOS[0]}), col.triangulos({'mao'}))
    return col._metacarpo_e_palma


def dobra_da_tenar(col, pts):
    """A maior entrada (mm) do metacarpo do polegar na palma, com a luva avaliada (`pts`): os pares de triângulos que
    no repouso estavam a mais de empunhadura.PERTO_MM (os de perto são a pele da dobra da CMC, das correções)."""
    metacarpo, palma = _metacarpo_e_palma(col)
    return col.profundidade_nos_pontos(pts, metacarpo, palma, empunhadura.PERTO_MM)


def refinar_na_malha(custo_de, lim, g, na, m, cadeia):
    """A busca de padrão, a partir da solução das cápsulas, com a entrada da tenar na arma e a dobra dela na palma
    medidas na malha: a pele da tenar não cabe na cápsula do metacarpo, e a abdução no máximo a levava 5 mm para
    dentro das costas do punho; fechado no plano da palma, o metacarpo entrava nela. Só a busca (cada avaliação refaz
    a luva, 18 ms)."""
    vertices = na.vertices(LIVRE + TENAR)

    def com_malha(gg):
        pts = na.pontos(_com_graus(m, cadeia, gg).pose())
        return custo_de(gg) + PESO_MALHA ** 2 * (na.entrada_quadrada(pts, vertices) + dobra_da_tenar(na.col, pts) ** 2)

    return _padrao(com_malha, lim, g, com_malha(g), passo=PASSO_REFINO)


def resolver(cadeia, alvo, normal, lim, inicio=None, na=None, m=None, eixo=None):
    """Os graus do polegar (além do repouso) que põem a polpa no alvo, de frente para ele e fora dos dedos (e da arma,
    com `na`, a luva na arma de empunhadura_arma.NaArma, e a pose da mão `m`: aí o refino pela malha da tenar); com o
    `eixo` (unitário, no referencial da luva), a falange distal apontando para ele."""
    def custo_de(g):
        return _custo(cadeia, g, alvo, normal, na, eixo)

    g = minimizar(custo_de, lim, inicio)
    return g if na is None else refinar_na_malha(custo_de, lim, g, na, m, cadeia)


def alvo_na_arma(cadeia, na, m, lim, lado, peso_lado):
    """O alvo da polpa do polegar na arma, quando a regra pede um lado e não um ponto (o polegar cruzando para o lado
    esquerdo do punho): os graus que põem a polpa encostada na superfície da arma (a distância com sinal a ela, dentro
    pesando o dobro), de frente para ela, fora dos dedos e da arma, e o mais longe possível na direção `lado` (unitária,
    no referencial da arma; `peso_lado` mm² de custo por mm andado). Devolve (ponto da superfície mais perto da polpa,
    normal dela), no referencial da luva — o alvo do fechar_no_alvo, que o polegar alcança."""
    inv = na.encaixe.inverted()
    rot_inv = inv.to_3x3()

    def custo_de(g):
        ms = cadeia.matrizes(g)
        p, lado_polpa = cadeia.polpa_em(g, ms)
        q = na.encaixe @ p
        co, n, _i, d = na.arma.bvh.find_nearest(q)
        dentro = (q - co).dot(n) < 0.0
        normal = (rot_inv @ n).normalized()
        return ((2.0 * d if dentro else d) ** 2 + (PESO_NORMAL_MM * (1.0 + lado_polpa.dot(normal))) ** 2
                + PESO_COLISAO ** 2 * (cadeia.penetracao(ms) + _entrada_na_arma(cadeia, ms, na))
                - peso_lado * q.dot(lado))

    g = refinar_na_malha(custo_de, lim, minimizar(custo_de, lim), na, m, cadeia)
    p, _l = cadeia.polpa_em(g)
    co, n, _i, _d = na.arma.bvh.find_nearest(na.encaixe @ p)
    return inv @ co, (rot_inv @ n).normalized()


def graus_da_pose(m, cadeia):
    """Os graus do polegar numa pose da mão feita por _com_graus (ou por afastar): a leitura de volta."""
    return {'abducao': cadeia.sinal_ab * m.giros['polegar_1'][1] if 'polegar_1' in m.giros else 0.0,
            'cmc': m.flexao.get('polegar_1', 0.0), 'rotacao': -cadeia.sinal_ab * m.rotacoes.get('polegar_1', 0.0),
            'mcp': m.flexao.get('polegar_2', 0.0), 'ip': m.flexao.get('polegar_3', 0.0),
            'desvio': m.aberturas.get('polegar_2', 0.0)}


def _com_graus(m, cadeia, g):
    """A pose da mão `m` com o polegar nos graus `g`."""
    m = m.com('polegar_1', flexao=g['cmc']).com('polegar_2', flexao=g['mcp'], abertura=g['desvio'])
    m = m.com('polegar_3', flexao=g['ip'])
    m.giros['polegar_1'] = (cadeia.eixo_ab, cadeia.sinal_ab * g['abducao'])
    m.rotacoes['polegar_1'] = -cadeia.sinal_ab * g['rotacao']
    return m


def _livre_e_resto(col):
    livre = col.triangulos(set(LIVRE))
    dentro = set(livre)
    return livre, [k for k in range(len(col.tris)) if k not in dentro]


def _cruza(col, m, livre, resto, na=None):
    """Se o polegar da pose `m` entra na mão (as falanges livres no resto da luva, ou o metacarpo na palma) ou na arma
    (com `na`) mais que o contato."""
    pts = na.pontos(m.pose()) if na is not None else col.modelo.pontos(m.pose())  # a luva consigo: qualquer referencial
    if (col.profundidade_nos_pontos(pts, livre, resto, empunhadura.PERTO_MM) > empunhadura.CONTATO_MM
            or dobra_da_tenar(col, pts) > empunhadura.CONTATO_MM):
        return True
    return na is not None and na.penetracao(pts, na.vertices(LIVRE + TENAR)) > empunhadura.CONTATO_MM


def _assentar_na_arma(col, lim, m, cadeia, ik, livre, resto, na):
    """O polegar da solução da IK na arma, sem caminho de chegada: a IK já foi refinada na malha (o polegar e a tenar
    contra a arma), então a solução encosta; se ainda entrar mais que o contato, a MCP e a IP abrem juntas, em linha
    para o mínimo da AAOS, até soltar (bisseção). Depois as duas fecham até encostar, a MCP primeiro. Erguido pela
    normal do alvo (a face do outro lado do punho), o polegar teria de dar ainda mais a volta e cruzava; em linha do
    polegar afastado, a ponta batia no receptor antes de chegar atrás do punho; esticado com a CMC da solução, ele
    atravessava o punho. Devolve (pose, graus, encostou)."""
    aberto = dict(ik, mcp=lim['mcp'][0], ip=lim['ip'][0])

    def em(s):
        return {k: ik[k] + (aberto[k] - ik[k]) * s for k in GRAUS}

    if _cruza(col, _com_graus(m, cadeia, ik), livre, resto, na):
        if _cruza(col, _com_graus(m, cadeia, aberto), livre, resto, na):
            raise RuntimeError('o polegar da solução cruza a arma ou a mão, mesmo com a MCP e a IP abertas')
        anda = max(abs(ik[k] - aberto[k]) for k in GRAUS)
        tolerancia = empunhadura.TOLERANCIA_GRAUS / max(anda, 1e-6)
        a, b = 0.0, 1.0  # a entra, b solta
        while b - a > tolerancia:
            s = (a + b) / 2
            if _cruza(col, _com_graus(m, cadeia, em(s)), livre, resto, na):
                a = s
            else:
                b = s
        g = em(b)
    else:
        g = dict(ik)
    m = _com_graus(m, cadeia, g)
    encostou = False
    for grau, osso in (('mcp', 'polegar_2'), ('ip', 'polegar_3')):
        m, g[grau], enc = empunhadura.fechar(col, m, osso, lim[grau][1], na=na)
        encostou = encostou or enc
    return m, g, encostou


def fechar_no_alvo(col, mao, m, alvo, normal, superficie, na=None, eixo=None, arma=None):
    """O polegar da pose `m` com a polpa no alvo, chegando pela normal dele até encostar e assentando pela IP e pela
    MCP; `superficie` são os triângulos da luva em que a polpa deve assentar (nas poses de teste e na faca). Na pega,
    `na` é a luva na arma (empunhadura_arma.NaArma): o alvo e a normal vêm no referencial da luva, a arma entra na IK e
    no contato e o encosto da polpa é medido nela; o `eixo` (a mão da frente, no referencial da luva) é para onde a
    falange distal aponta. Com `arma` no lugar do `na` (a faca: a polpa assenta nos dedos que abraçam o cabo), a arma é
    só obstáculo — entra na IK (com o refino pela malha da tenar), na chegada e no fechar da MCP e da IP — e o encosto
    da polpa é medido na `superficie`: sem ela, o polegar que dá a volta por cima do cabo até o indicador passava por
    dentro dele, e a abdução levava a tenar para dentro do cabo. Devolve (pose, relatório): os graus totais, os da IK,
    a distância da polpa à superfície e ao ponto do alvo (mm), se encostou, a altura de onde chegou (mm) e, com o
    `eixo`, o desvio da falange distal (graus)."""
    lim = limites(mao)
    cadeia = Cadeia(col, mao, {o: q for o, q in m.pose().items() if not o.startswith('polegar')})
    ik = resolver(cadeia, alvo, normal, lim, na=na or arma, m=m, eixo=eixo)
    livre, resto = _livre_e_resto(col)
    if na is not None:
        m, g, encostou = _assentar_na_arma(col, lim, m, cadeia, ik, livre, resto, na)
        acima = None
    else:
        for acima in ACIMA_MM:
            de = resolver(cadeia, alvo + normal * acima, normal, lim, inicio=ik, na=arma, m=m)
            if not _cruza(col, _com_graus(m, cadeia, de), livre, resto, arma):
                break
        else:
            onde = 'a mão ou a arma' if arma is not None else 'a mão'
            raise RuntimeError(f'o polegar cruza {onde} mesmo com a polpa {ACIMA_MM[-1]} mm acima do alvo')

        def em(s):
            return {k: min(max(de[k] + (ik[k] - de[k]) * s, lim[k][0]), lim[k][1]) for k in GRAUS}

        anda = max(abs(ik[k] - de[k]) for k in GRAUS)
        tolerancia = empunhadura.TOLERANCIA_GRAUS / max(anda, 1e-6)
        a, b = 0.0, 1.0 + ALEM
        if _cruza(col, _com_graus(m, cadeia, em(b)), livre, resto, arma):
            while b - a > tolerancia:
                s = (a + b) / 2
                if _cruza(col, _com_graus(m, cadeia, em(s)), livre, resto, arma):
                    b = s
                else:
                    a = s
            encostou = True
        else:
            a, encostou = b, False
        g = em(a)
        m = _com_graus(m, cadeia, g)
        for grau, osso in (('mcp', 'polegar_2'), ('ip', 'polegar_3')):
            m, g[grau], enc = empunhadura.fechar(col, m, osso, lim[grau][1], na=arma)
            encostou = encostou or enc
    polpa, _lado = cadeia.polpa_em(g)
    if na is None:
        pts = col.modelo.pontos(m.pose())
        bvh = _malha(pts, [col.tris[k] for k in superficie])
        encosto = min(bvh.find_nearest(pts[i])[3] for i in cadeia.lado_da_polpa)
    else:
        encosto = na.encosto(na.pontos(m.pose()), cadeia.lado_da_polpa)
    rel = {'graus': totais(mao, g), 'ik': totais(mao, ik), 'polpaEncostaMM': round(encosto, 2),
           'polpaAoAlvoMM': round((polpa - alvo).length, 2), 'encostou': encostou, 'chegouDeMM': acima}
    if eixo is not None:
        cosseno = max(-1.0, min(1.0, _direcao_distal(cadeia.matrizes(g)).dot(eixo)))
        rel['desvioDoEixoGraus'] = round(math.degrees(math.acos(cosseno)), 1)
    return m, rel


def afastar(col, mao, m):
    """O polegar fora do caminho dos dedos que vão fechar (o começo do punho): para o lado, no plano da palma — a
    abdução palmar e a flexão da CMC no mínimo da AAOS (a extensão), a MCP e a IP esticadas. Erguido para a frente da
    palma (a abdução palmar no máximo), ficava no caminho da ponta do indicador, que não dobrava."""
    lim = limites(mao)
    eixo, sinal = maos_rig.eixo_abducao_do_polegar(mao, col.rig)
    m = m.com('polegar_1', flexao=lim['cmc'][0]).com('polegar_2', flexao=lim['mcp'][0])
    m = m.com('polegar_3', flexao=lim['ip'][0])
    m.giros['polegar_1'] = (eixo, sinal * lim['abducao'][0])
    return m


def abrir(col, mao, m):
    """O polegar fora do caminho dos dedos (a mesa): a MCP e a IP no mínimo da AAOS e, se ainda cruzar a mão, a CMC
    estendendo até soltar. Devolve (pose, relatório com os graus totais)."""
    lim = limites(mao)
    cadeia = Cadeia(col, mao, {o: q for o, q in m.pose().items() if not o.startswith('polegar')})
    g = {'abducao': 0.0, 'cmc': 0.0, 'rotacao': 0.0, 'mcp': lim['mcp'][0], 'ip': lim['ip'][0], 'desvio': 0.0}
    livre, resto = _livre_e_resto(col)

    def solto(cmc):
        return not _cruza(col, _com_graus(m, cadeia, {**g, 'cmc': cmc}), livre, resto)

    if not solto(g['cmc']):
        if not solto(lim['cmc'][0]):
            raise RuntimeError('o polegar cruza os dedos mesmo aberto e com a CMC estendida no limite')
        # a maior flexão da CMC (a menor extensão) que solta: a bisseção sobe do limite estendido, que solta
        g['cmc'] = empunhadura._bissecao(solto, lim['cmc'][0], g['cmc'])
    return _com_graus(m, cadeia, g), {'graus': totais(mao, g)}
