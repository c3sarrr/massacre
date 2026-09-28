# Cruzamento e penetração da luva (Fase 4.1b; desenho em docs/superpowers/specs/2026-09-26-4.1b-luvas-e-empunhadura-design.md,
# seções 4 e 6.3; plano, Tarefas 5 e 7): as medidas de "a malha não atravessa a si mesma mais de 0,3 mm" (as poses de
# teste) e de "encostou" (o solver de empunhadura), sobre a malha avaliada numa pose.
#  - Os pares de triângulos que se cruzam: a BVH dos dois conjuntos (ou de um consigo mesmo), fora os que dividem um
#    vértice.
#  - A penetração de um par é a do vértice mais fundo: cada vértice de um triângulo contra a superfície em volta do outro
#    (ele e os vizinhos até três anéis), pelo ponto mais próximo dela e o sinal da pseudo-normal ali (a normal da face
#    no meio dela; na aresta ou no vértice, a média das faces que tocam o ponto) — quanto o vértice está dentro da
#    superfície. O plano infinito de um triângulo não serve: numa dobra fechada, com triângulos finos quase paralelos,
#    um vértice fica "atrás do plano" do outro a milímetros de distância sem estar dentro de nada (a medida pelo plano
#    dava 3,6 mm onde a penetração real era 0,24 mm).
# Unidades: as dos pontos (mm nas validações).
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.geometry import closest_point_on_tri

ANEIS = 3
DENTRO_DA_FACE = 1e-4  # mm: o ponto mais próximo a menos disso de uma face é daquela face (para a pseudo-normal)


class Superficie:
    """Os triângulos de uma malha e, por vértice, os triângulos que o usam (a topologia não muda entre as poses)."""

    def __init__(self, tris):
        self.tris = [tuple(t) for t in tris]
        self.de_vertice = {}
        for k, t in enumerate(self.tris):
            for v in t:
                self.de_vertice.setdefault(v, []).append(k)

    def regiao(self, k, dentro=None):
        """O triângulo k e os vizinhos até ANEIS anéis (só os de `dentro`, se dado)."""
        r, borda = {k}, {k}
        for _ in range(ANEIS):
            novos = {j for t in borda for v in self.tris[t] for j in self.de_vertice[v]} - r
            if dentro is not None:
                novos &= dentro
            r |= novos
            borda = novos
        return sorted(r)


def pares(pts, tris, A, B=None):
    """Os pares (a, b) de triângulos (índices em `tris`) de A com B (ou de A consigo mesmo) que se cruzam, sem os que
    dividem um vértice."""
    ta = BVHTree.FromPolygons(pts, [tris[k] for k in A])
    tb = ta if B is None else BVHTree.FromPolygons(pts, [tris[k] for k in B])
    B = A if B is None else B
    saida = []
    for i, j in ta.overlap(tb):
        a, b = A[i], B[j]
        if (B is A and a >= b) or set(tris[a]) & set(tris[b]):
            continue
        saida.append((a, b))
    return saida


def _normal(pts, t):
    a, b, c = (pts[i] for i in t)
    n = (b - a).cross(c - a)
    return n.normalized() if n.length > 1e-12 else Vector()


class Medidor:
    """A penetração dos pares numa pose (os pontos), com as regiões e as BVH delas guardadas para os pares repetidos."""

    def __init__(self, sup, pts):
        self.sup, self.pts = sup, pts
        self._bvh = {}

    def _regiao(self, k, dentro):
        chave = (k, id(dentro))
        if chave not in self._bvh:
            reg = self.sup.regiao(k, dentro)
            tris = [self.sup.tris[j] for j in reg]
            self._bvh[chave] = (reg, BVHTree.FromPolygons(self.pts, tris), {v for t in tris for v in t})
        return self._bvh[chave]

    def _pseudo_normal(self, reg, j, co):
        t = self.sup.tris[reg[j]]
        faces = {reg[j]}
        for v in t:
            for k in self.sup.de_vertice[v]:
                if k in faces:
                    continue
                a, b, c = (self.pts[i] for i in self.sup.tris[k])
                if (closest_point_on_tri(co, a, b, c) - co).length < DENTRO_DA_FACE:
                    faces.add(k)
        n = Vector()
        for k in faces:
            n += _normal(self.pts, self.sup.tris[k])
        return n.normalized() if n.length > 1e-12 else _normal(self.pts, t)

    def vertice_em(self, v, k, dentro=None):
        """Quanto o vértice v está dentro da superfície em volta do triângulo k (mm; 0 se fora ou se ele é dela)."""
        reg, bvh, vs = self._regiao(k, dentro)
        if v in vs:
            return 0.0
        co, _n, j, _d = bvh.find_nearest(self.pts[v])
        if co is None:
            return 0.0
        s = (self.pts[v] - co).dot(self._pseudo_normal(reg, j, co))
        return max(0.0, -s)

    def par(self, a, b, dentro_a=None, dentro_b=None):
        """A penetração do par: o vértice mais fundo de cada triângulo na superfície em volta do outro."""
        ta, tb = self.sup.tris[a], self.sup.tris[b]
        return max(max(self.vertice_em(v, b, dentro_b) for v in ta), max(self.vertice_em(v, a, dentro_a) for v in tb))
