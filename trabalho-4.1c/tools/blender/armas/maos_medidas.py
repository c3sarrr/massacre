# Medidas-chave da luva na malha (Fase 4.1b; desenho em docs/superpowers/specs/2026-09-26-4.1b-luvas-e-empunhadura-design.md,
# seção 3.2; plano, Tarefa 3): comprimento, largura nos nós, circunferência no pulso e na boca do punho, cada uma com o
# alvo da ficha mais a luva. Referencial e unidades: os de maos.py (mm).
import math

from .maos import DEDOS4
from .unidades import S


def _envoltoria(pts):
    """Envoltória convexa 2D (cadeia monótona de Andrew), no sentido anti-horário."""
    pts = sorted(set(pts))
    if len(pts) < 3:
        return pts

    def giro(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    baixo, alto = [], []
    for p in pts:
        while len(baixo) >= 2 and giro(baixo[-2], baixo[-1], p) <= 0:
            baixo.pop()
        baixo.append(p)
    for p in reversed(pts):
        while len(alto) >= 2 and giro(alto[-2], alto[-1], p) <= 0:
            alto.pop()
        alto.append(p)
    return baixo[:-1] + alto[:-1]


def perimetro_da_secao(pts3, arestas, x0):
    """Perímetro (mm) da seção da malha no plano x = x0: a envoltória convexa dos pontos onde as arestas cruzam o
    plano (as seções medidas — o pulso e a boca do punho — são convexas; a de fora envolve o forro)."""
    sec = []
    for a, b in arestas:
        pa, pb = pts3[a], pts3[b]
        da, db = pa.x - x0, pb.x - x0
        if abs(da) < 1e-6:
            sec.append((round(pa.y, 6), round(pa.z, 6)))
        if da * db < 0:
            t = da / (da - db)
            q = pa.lerp(pb, t)
            sec.append((round(q.y, 6), round(q.z, 6)))
    h = _envoltoria(sec)
    return sum(math.dist(h[i], h[(i + 1) % len(h)]) for i in range(len(h)))


def medir_mao(ob, mao):
    """Medidas-chave na malha (mm), pela pose de repouso, cada uma com o alvo (a ficha mais a luva):
    - comprimento: do pulso à ponta do médio como se o dedo estivesse esticado (a MCP do médio, as duas falanges e o
      alcance da malha além da DIP, na direção da ponta); na ponta, o tecido e o reforço de couro por cima;
    - largura: nos nós, da borda da MCP II à da V, sem o polegar nem os dedos;
    - pulso: a circunferência no pulso (a do ANSUR II mais a volta da luva);
    - boca: a circunferência do punho na borda (o antebraço de massinha ali, mais a folga e a luva)."""
    me = ob.data
    mw = ob.matrix_world
    # os nomes dos ossos sem o sufixo do lado (a luva com o rig tem _d/_e)
    nomes = {g.index: (g.name[:-2] if g.name[-2:] in ('_d', '_e') else g.name) for g in ob.vertex_groups}
    pts, pol, ded = [], [], []
    for v in me.vertices:
        pts.append((mw @ v.co) / S)
        pol.append(sum(e.weight for e in v.groups if nomes[e.group].startswith('polegar')))
        ded.append(sum(e.weight for e in v.groups
                       if nomes[e.group].rsplit('_', 1)[0] in DEDOS4 and not nomes[e.group].endswith('_0')))
    dd = mao.dedos['medio']
    alcance = max((p - dd['dip']).dot(dd['dirs'][2]) for p in pts if (p - dd['dip']).length < 45.0)
    comprimento = dd['mcp'].x + (dd['pip'] - dd['mcp']).length + (dd['dip'] - dd['pip']).length + alcance

    def janela(d):
        x = mao.dedos[d]['mcp'].x
        return [p for p, wp, wd in zip(pts, pol, ded) if wp < 0.05 and wd <= 0.5 and x - 12.0 <= p.x <= x + 6.0]

    largura = max(p.y for p in janela('indicador')) - min(p.y for p in janela('minimo'))
    arestas = [tuple(e.vertices) for e in me.edges]
    luva = mao.luva
    punho_mm = mao.f['luva']['punho']
    x_boca = -punho_mm + 0.6
    folga_boca = mao.f['luva']['folgaPunho'] * (-x_boca / punho_mm)
    return {
        'comprimento': {'mm': round(comprimento, 2),
                        'alvo': round(mao.f['mao']['comprimento']['mm'] + luva + mao.f['luva']['couro'], 2)},
        'largura': {'mm': round(largura, 2), 'alvo': round(mao.largura + 2 * luva, 2)},
        'pulso': {'mm': round(perimetro_da_secao(pts, arestas, 0.0), 2),
                  'alvo': round(mao.f['mao']['pulso']['mm'] + 2 * math.pi * luva, 2)},
        'boca': {'mm': round(perimetro_da_secao(pts, arestas, x_boca), 2),
                 'alvo': round(mao.circunferencia_antebraco(x_boca) + 2 * math.pi * (luva + folga_boca), 2)},
    }
