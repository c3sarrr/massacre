"""A pseudonormal pelos planos distintos em volta do ponto mais perto (prova da Tarefa 13): as faces a até QUINA_MM do
ponto, agrupadas pelo plano (as normais a até ~2,6° uma da outra); cada plano pesa o ângulo dele no ponto — a soma dos
ângulos de canto das faces dele que têm o ponto por vértice (até 2π), ou π (o ponto numa aresta ou no meio dela). A
soma sem pesos contava cada triângulo fino de um plano: na borda viva do buraco do polegar da AWP, três lascas da parede
contra uma face do lado, e um ponto 15,7 mm fora da coronha saía dentro."""
import math

from mathutils import Vector

from armas import empunhadura_arma as EA
from armas.unidades import S

MESMO_PLANO = 0.999  # o cosseno entre as normais de um mesmo plano (~2,6°)


def montar(arma, objetos, extra=()):
    verts, polys = [], []
    for ob in objetos:
        mw = ob.matrix_world
        base = len(verts)
        verts += [(mw @ v.co) / S for v in ob.data.vertices]
        polys += [[base + i for i in p.vertices] for p in ob.data.polygons]
    for pts, tris in extra:
        base = len(verts)
        verts += [Vector(p) for p in pts]
        polys += [[base + i for i in t] for t in tris]
    arma._verts, arma._polys = verts, polys


def pseudonormal(arma, co):
    planos = []  # [normal, soma dos ângulos de canto, tem canto]
    for _c, n, i, _d in arma.bvh.find_nearest_range(co, EA.QUINA_MM):
        vs = [arma._verts[k] for k in arma._polys[i]]
        j = min(range(len(vs)), key=lambda k: (vs[k] - co).length_squared)
        canto = None
        if (vs[j] - co).length <= EA.QUINA_MM:
            a, b = vs[j - 1] - vs[j], vs[(j + 1) % len(vs)] - vs[j]
            if a.length > 1e-12 and b.length > 1e-12:
                canto = a.angle(b)
        for pl in planos:
            if pl[0].dot(n) >= MESMO_PLANO:
                if canto is not None:
                    pl[1] += canto
                    pl[2] = True
                break
        else:
            planos.append([Vector(n), canto or 0.0, canto is not None])
    total = Vector()
    for n, soma, tem_canto in planos:
        total += n * (min(soma, math.tau) if tem_canto else math.pi)
    return total


def distancia(self, p, limite=None):
    """Arma.distancia com a pseudonormal pelos planos (o resto igual)."""
    r = self.bvh.find_nearest(p) if limite is None else self.bvh.find_nearest(p, limite)
    if r[0] is None:
        return None
    co, n, _i, d = r
    para_fora = Vector(p) - co
    dentro = para_fora.dot(n) < 0.0
    if dentro or d > EA.PERTO_DA_ARMA_MM:
        media = pseudonormal(self, co)
        pela_media = para_fora.dot(media) < 0.0 if media.length > 1e-9 else dentro
        if d > EA.PERTO_DA_ARMA_MM:
            dentro = dentro + pela_media + self._impar(p) >= 2
        else:
            dentro = pela_media
    return -d if dentro else d
