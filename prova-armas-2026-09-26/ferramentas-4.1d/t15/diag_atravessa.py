# Diagnóstico: que pares da luva se atravessam na última pega do servidor (C['ultima']), com e sem o afundamento.
import json
from collections import Counter
from armas import validar_maos as VM, maos_contato as MC, luvas, empunhadura, empunhadura_polegar as EPO

C = B.C
u = C['ultima']
f, afundar, lado = u['f'], u['afundar'], u['lado']
luva = C['bracos'][lado][0]
col = f['col']
topo = VM.Topologia(luva, luvas.REFORCO)
pose = f['m'].pose()
nomes = {g.index: g.name for g in luva.vertex_groups}
dom = []
for v in luva.data.vertices:
    dom.append(nomes[max(v.groups, key=lambda g: g.weight).group] if len(v.groups) else '?')


def osso(k):
    return Counter(dom[v] for v in topo.tris[k]).most_common(1)[0][0]


def fundos(pts, n=14):
    medidor = MC.Medidor(topo.sup, pts)
    out = []
    for a, b in MC.pares(pts, topo.tris, list(range(len(topo.tris)))):
        pa, pb = topo.peca[a], topo.peca[b]
        if pa >= 0 and (pa == pb or (pb < 0 and b in topo.pegada[pa]) or (pa, pb) in topo.empilhadas):
            continue
        if pb >= 0 and pa < 0 and a in topo.pegada[pb]:
            continue
        d = medidor.par(a, b)
        if d > 0.1:
            m = (pts[topo.tris[a][0]] + pts[topo.tris[b][0]]) / 2
            out.append((round(d, 3), a, b, osso(a), osso(b), pa, pb, [round(c, 1) for c in m]))
    out.sort(reverse=True)
    return out[:n]


print('DIAG lado', lado, 'tris', len(topo.tris), 'polegar', json.dumps((f['rel'] or {}).get('polegar'), default=str)[:400])
for rot, af in (('com afundar', afundar), ('sem afundar', None)):
    pts = col.modelo.pontos(pose, af)
    for linha in fundos(pts):
        print('DIAG', rot, json.dumps(linha, default=str))
livre, resto = EPO._livre_e_resto(col)
pts = col.modelo.pontos(pose)
print('DIAG solver: livre no resto', round(col.profundidade_nos_pontos(pts, livre, resto, empunhadura.PERTO_MM), 3),
      'dobra_da_tenar', round(EPO.dobra_da_tenar(col, pts), 3))
