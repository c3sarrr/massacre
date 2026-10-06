# Diagnóstico 3: o mapa da dobra da tenar (a medida da validação, só a pele do polegar contra a dele e a da palma)
# pelos graus da CMC, na última pega do servidor: abdução x flexão na rotação dela, e a rotação sozinha.
import json
from armas import empunhadura_polegar as EPO

exec(open(PROVA, encoding='utf-8').read().split('CONTA = ')[0])
C = B.C
f = C['ultima']['f']
col, m = f['col'], f['m']
cadeia = EPO.Cadeia(col, C['mao'], {o: q for o, q in m.pose().items() if not o.startswith('polegar')})
lim = EPO.limites(C['mao'])
g0 = EPO.graus_da_pose(m, cadeia)
print('DIAG3 limites', json.dumps(lim), flush=True)
print('DIAG3 graus finais', json.dumps({k: round(v, 2) for k, v in g0.items()}), flush=True)


def dobra(g):
    return atravessa_tenar(col, col.modelo.pontos(EPO._com_graus(m, cadeia, g).pose()))


def faixa(a, b, passo):
    v, x = [], a
    while x <= b + 1e-9:
        v.append(round(x, 2))
        x += passo
    return v


abd = faixa(lim['abducao'][0], lim['abducao'][1], 5.0)
cmc = faixa(lim['cmc'][0], lim['cmc'][1], 5.0)
print('DIAG3 abd', abd, flush=True)
for c in cmc:
    linha = [round(dobra(dict(g0, abducao=a, cmc=c)), 1) for a in abd]
    print('DIAG3 cmc', c, linha, flush=True)
rot = faixa(lim['rotacao'][0], lim['rotacao'][1], 5.0)
print('DIAG3 rotação', [(r, round(dobra(dict(g0, rotacao=r)), 2)) for r in rot], flush=True)
