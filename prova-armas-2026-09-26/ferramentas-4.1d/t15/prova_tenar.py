# Prova: o refino do polegar (empunhadura_polegar.refinar_na_malha) com a luva contra si mesma na tenar medida como na
# validação (validar_maos.atravessa: os pares que se cruzam, fora os que dividem um vértice, a penetração pelo
# maos_contato.Medidor), só a pele do polegar contra a do polegar e da palma, o excesso acima de 0,1 mm.
import time
from mathutils import Vector
from armas import validar_maos as VM, maos_contato as MC, luvas, empunhadura_polegar as EPO

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


CONTA = {'n': 0, 's': 0.0}


def refinar_com_tenar(custo_de, lim, g, na, m, cadeia):
    vertices = na.vertices(EPO.LIVRE + EPO.TENAR)

    def com_malha(gg):
        pts = na.pontos(EPO._com_graus(m, cadeia, gg).pose())
        t0 = time.time()
        exc = max(0.0, atravessa_tenar(na.col, pts) - FOLGA)
        CONTA['n'] += 1
        CONTA['s'] += time.time() - t0
        return custo_de(gg) + EPO.PESO_MALHA ** 2 * (na.entrada_quadrada(pts, vertices)
                                                     + EPO.dobra_da_tenar(na.col, pts) ** 2 + exc ** 2)

    return EPO._padrao(com_malha, lim, g, com_malha(g), passo=EPO.PASSO_REFINO)


_orig = EPO.refinar_na_malha
EPO.refinar_na_malha = refinar_com_tenar
try:
    V.esquerda_polegar_na_arma(NOME, PEGAS, vistas=None)
finally:
    EPO.refinar_na_malha = _orig
print('PROVA_TENAR avaliações', CONTA['n'], 'segundos na medida', round(CONTA['s'], 1), flush=True)
