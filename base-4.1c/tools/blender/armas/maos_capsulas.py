# As cápsulas dos ossos da luva (Fase 4.1b; desenho em docs/superpowers/specs/2026-09-26-4.1b-luvas-e-empunhadura-
# design.md, seção 6.2): cada osso como o segmento dele com a seção medida na luva de repouso, para as contas rápidas de
# encosto da IK do polegar (empunhadura_polegar.py) — o contato que vale é sempre o da malha (maos_contato.py).
#  - a seção: em volta do osso, 16 setores no plano X–Z dele; em cada um, o percentil 80 da distância ao eixo dos
#    vértices do osso (os de que ele é o dono) no meio dele (entre 15 % e 85 % do comprimento, fora do bojo das juntas);
#    um setor vazio fica com a média dos vizinhos. O polegar e os dedos são achatados (o polegar tem 24 mm de largura
#    na unha e bem menos de espessura): com um raio redondo, pela mediana, o polegar deitado com a polpa num dedo
#    parecia entrar nele uns 3 mm;
#  - o encosto entre duas cápsulas: os pontos mais próximos dos segmentos e o raio de cada uma na direção da outra
#    (interpolado entre os centros dos setores).
# Unidades: mm; as matrizes dos ossos em metros no Blender.
import math

from mathutils import Vector

from .unidades import S

SETORES = 16
PERCENTIL = 0.8
MEIO = (0.15, 0.85)
_VOLTA = 2.0 * math.pi


def mm(m):
    """A matriz de um osso (metros) em mm."""
    r = m.copy()
    r.translation = m.translation / S
    return r


def _entre(x):
    return min(max(x, 0.0), 1.0)


def mais_proximos(p1, q1, p2, q2):
    """(s, t) dos pontos mais próximos dos segmentos p1–q1 e p2–q2: p1 + s·(q1 − p1) e p2 + t·(q2 − p2)."""
    d1, d2, r = q1 - p1, q2 - p2, p1 - p2
    a, e, f = d1.dot(d1), d2.dot(d2), d2.dot(r)
    if a < 1e-12 and e < 1e-12:
        return 0.0, 0.0
    if a < 1e-12:
        return 0.0, _entre(f / e)
    c = d1.dot(r)
    if e < 1e-12:
        return _entre(-c / a), 0.0
    b = d1.dot(d2)
    den = a * e - b * b
    s = _entre((b * f - c * e) / den) if den > 1e-12 else 0.0
    t = (b * s + f) / e
    if t < 0.0:
        return _entre(-c / a), 0.0
    if t > 1.0:
        return _entre((b - c) / a), 1.0
    return s, t


def _percentil(valores):
    v = sorted(valores)
    return v[min(len(v) - 1, int(PERCENTIL * (len(v) - 1) + 0.5))]


class Secoes:
    """Os raios por setor da seção de cada osso ({osso sem lado: [16 raios]}), medidos na luva de repouso."""

    def __init__(self, col):
        pts = col.modelo.pontos({})
        por_osso = {}
        for i, dono in enumerate(col.dono):
            por_osso.setdefault(dono, []).append(i)
        self.raios = {}
        for b in col.rig.data.bones:
            nome = b.name[:-2]
            if nome not in por_osso:
                continue
            para_local = mm(b.matrix_local).inverted()
            comp = b.length / S
            setores = [[] for _ in range(SETORES)]
            for i in por_osso[nome]:
                q = para_local @ pts[i]
                if not MEIO[0] * comp <= q.y <= MEIO[1] * comp:
                    continue
                k = int((math.atan2(q.z, q.x) % _VOLTA) / _VOLTA * SETORES) % SETORES
                setores[k].append(math.hypot(q.x, q.z))
            raios = [_percentil(s) if s else None for s in setores]
            if all(r is None for r in raios):
                continue
            while any(r is None for r in raios):
                raios = [r if r is not None else _media_dos_vizinhos(raios, k) for k, r in enumerate(raios)]
            self.raios[nome] = raios

    def raio(self, osso, direcao):
        """O raio da seção do osso na `direcao` (no referencial dele; a componente em Y não conta), interpolado entre
        os centros dos setores."""
        r = self.raios[osso]
        f = (math.atan2(direcao.z, direcao.x) % _VOLTA) / _VOLTA * SETORES - 0.5
        k = math.floor(f)
        w = f - k
        return r[k % SETORES] * (1.0 - w) + r[(k + 1) % SETORES] * w

    def maior(self, osso):
        return max(self.raios[osso])


def _media_dos_vizinhos(raios, k):
    vizinhos = [raios[(k + d) % SETORES] for d in (-1, 1) if raios[(k + d) % SETORES] is not None]
    return sum(vizinhos) / len(vizinhos) if vizinhos else None


class Capsula:
    """Um osso posado: o segmento (mm), a rotação para o referencial dele e o maior raio (para descartar longe)."""

    def __init__(self, secoes, osso, matriz, comprimento):
        self.osso = osso
        self.cabeca = matriz.translation.copy()
        self.cauda = matriz @ Vector((0.0, comprimento, 0.0))
        self.meio = (self.cabeca + self.cauda) / 2
        self.alcance = comprimento / 2 + secoes.maior(osso)
        self.para_local = matriz.to_3x3().inverted()


def encosto(secoes, a, b):
    """Quanto as cápsulas `a` e `b` entram uma na outra (mm; negativo é a folga entre elas)."""
    if (a.meio - b.meio).length > a.alcance + b.alcance:
        return -math.inf
    s, t = mais_proximos(a.cabeca, a.cauda, b.cabeca, b.cauda)
    pa = a.cabeca.lerp(a.cauda, s)
    pb = b.cabeca.lerp(b.cauda, t)
    d = pb - pa
    dist = d.length
    if dist < 1e-9:
        return secoes.maior(a.osso) + secoes.maior(b.osso)
    return secoes.raio(a.osso, a.para_local @ d) + secoes.raio(b.osso, b.para_local @ -d) - dist
