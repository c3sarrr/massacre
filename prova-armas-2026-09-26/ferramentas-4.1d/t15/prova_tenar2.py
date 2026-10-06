# Prova 2: a dobra da tenar (a luva contra si mesma na pele do polegar e na da palma, a medida da validação) tabelada
# pelos graus da CMC — ela só depende do polegar_1 (diag2: sem a MCP, a IP ou qualquer dedo, a mesma) — e somada ao
# custo da busca global do polegar (minimizar: a IK das cápsulas e a escolha do alvo na arma), com a medida de verdade
# no refino pela malha (prova 1). Roda com NOME, PEGAS (as da esquerda) e PARTES opcionais definidos antes.
import json
import time
from mathutils import Vector
from armas import validar_maos as VM, maos_contato as MC, luvas, empunhadura, empunhadura_polegar as EPO

FOLGA = 0.1


def _tenar(col):
    if not hasattr(col, '_prova_tenar'):
        t = VM.Topologia(col.luva, luvas.REFORCO)
        a = [k for k, o in enumerate(col.dono_tri) if o in EPO.OSSOS and t.peca[k] < 0]
        b = [k for k, o in enumerate(col.dono_tri) if o in EPO.OSSOS + ('mao',) and t.peca[k] < 0]
        col._prova_tenar = (t, a, b)
    return col._prova_tenar


def atravessa_tenar(col, pts):
    t, a, b = _tenar(col)
    if not isinstance(pts[0], Vector):
        pts = [Vector(p) for p in pts]
    med = MC.Medidor(t.sup, pts)
    return max((med.par(x, y) for x, y in MC.pares(pts, t.tris, a, b)), default=0.0)


def _faixa(a, b, n):
    return [a + (b - a) * i / n for i in range(n + 1)]


TABELAS = B.C.setdefault('_tabelas_tenar', {})


def tabela(col, mao):
    chave = col.luva.name
    if chave not in TABELAS:
        t0 = time.time()
        lim = EPO.limites(mao)
        cadeia = EPO.Cadeia(col, mao, {})
        m0 = empunhadura.Mao()
        ea = _faixa(*lim['abducao'], round((lim['abducao'][1] - lim['abducao'][0]) / 5.0))
        ec = _faixa(*lim['cmc'], round((lim['cmc'][1] - lim['cmc'][0]) / 5.0))
        er = _faixa(*lim['rotacao'], 4)
        zero = {k: 0.0 for k in EPO.GRAUS}
        v = [[[atravessa_tenar(col, col.modelo.pontos(
            EPO._com_graus(m0, cadeia, dict(zero, abducao=a, cmc=c, rotacao=r)).pose())) for r in er] for c in ec]
            for a in ea]
        TABELAS[chave] = (ea, ec, er, v)
        print('TABELA', chave, round(time.time() - t0, 1), 's', json.dumps([[round(max(x), 1) for x in linha]
                                                                         for linha in v]), flush=True)
    return TABELAS[chave]


def _onde(eixo, x):
    n = len(eixo) - 1
    t = (min(max(x, eixo[0]), eixo[-1]) - eixo[0]) / (eixo[-1] - eixo[0]) * n
    i = min(int(t), n - 1)
    return i, t - i


def dobra_tabelada(tab, g):
    ea, ec, er, v = tab
    (i, fi), (j, fj), (k, fk) = _onde(ea, g['abducao']), _onde(ec, g['cmc']), _onde(er, g['rotacao'])
    s = 0.0
    for di, wi in ((0, 1.0 - fi), (1, fi)):
        for dj, wj in ((0, 1.0 - fj), (1, fj)):
            for dk, wk in ((0, 1.0 - fk), (1, fk)):
                s += wi * wj * wk * v[i + di][j + dj][k + dk]
    return s


ATUAL = {}
_alvo, _resolver, _min, _ref = EPO.alvo_na_arma, EPO.resolver, EPO.minimizar, EPO.refinar_na_malha


def alvo2(cadeia, na, m, lim, lado, peso_lado):
    ATUAL['tab'] = tabela(na.col, B.C['mao'])
    try:
        return _alvo(cadeia, na, m, lim, lado, peso_lado)
    finally:
        ATUAL.pop('tab', None)


def resolver2(cadeia, alvo, normal, lim, inicio=None, na=None, m=None, eixo=None):
    if na is not None:
        ATUAL['tab'] = tabela(na.col, B.C['mao'])
    try:
        return _resolver(cadeia, alvo, normal, lim, inicio=inicio, na=na, m=m, eixo=eixo)
    finally:
        ATUAL.pop('tab', None)


def min2(custo_de, lim, inicio=None):
    tab = ATUAL.get('tab')
    if tab is None:
        return _min(custo_de, lim, inicio)
    return _min(lambda g: custo_de(g) + EPO.PESO_MALHA ** 2 * max(0.0, dobra_tabelada(tab, g) - FOLGA) ** 2, lim,
                inicio)


def ref2(custo_de, lim, g, na, m, cadeia):
    vertices = na.vertices(EPO.LIVRE + EPO.TENAR)

    def com_malha(gg):
        pts = na.pontos(EPO._com_graus(m, cadeia, gg).pose())
        exc = max(0.0, atravessa_tenar(na.col, pts) - FOLGA)
        return custo_de(gg) + EPO.PESO_MALHA ** 2 * (na.entrada_quadrada(pts, vertices)
                                                     + EPO.dobra_da_tenar(na.col, pts) ** 2 + exc ** 2)

    return EPO._padrao(com_malha, lim, g, com_malha(g), passo=EPO.PASSO_REFINO)


EPO.alvo_na_arma, EPO.resolver, EPO.minimizar, EPO.refinar_na_malha = alvo2, resolver2, min2, ref2
try:
    V.esquerda_polegar_na_arma(NOME, PEGAS, vistas=globals().get('VISTAS'))
finally:
    EPO.alvo_na_arma, EPO.resolver, EPO.minimizar, EPO.refinar_na_malha = _alvo, _resolver, _min, _ref
