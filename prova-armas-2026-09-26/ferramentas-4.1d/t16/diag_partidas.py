"""As partidas da IK do polegar (a reprovação da AK na Tarefa 16): a IK com a arma (empunhadura_polegar.resolver)
parte só do melhor ponto da grade de 10°, e na geometria nova da AK ela caiu num vale de custo 22,9 (as cápsulas) com
o da solução de antes, 3,4, ainda lá e sem cruzar. Aqui, em cada IK com a arma das mãos pedidas, pelo banco
(t14/pega_banco.py) sobre uma .blend da conferência com as luvas montadas: a solução do solver (que segue valendo) e as
`n` melhores partidas da grade a pelo menos `distancia` graus umas das outras (empunhadura_polegar.partidas_da_grade),
cada uma com a busca de padrão, o custo das cápsulas com a dobra da tabela, o refino pela malha (o custo dele) e o
`_cruza` do resultado — a escolha de uma IK de várias partidas, medida antes de mudar o solver. Com `--completa`, a
pega inteira pelo caminho do construir (pega_banco.resolver: a regra da categoria com as correções da arma, o
EMPUNHADURA dela) no lugar das mãos pedidas.
    blender -b --factory-startup -P diag_partidas.py -- <arma> <categoria> <lados: d | e | d,e> <.blend> <pasta>
        [--n 6] [--distancia 20] [--completa]
"""
import json
import os
import sys
import time

a = sys.argv[sys.argv.index('--') + 1:]
ARMA, CATEGORIA, LADOS, BLEND, TRABALHO = a[:5]
N = int(a[a.index('--n') + 1]) if '--n' in a else 6
DISTANCIA = float(a[a.index('--distancia') + 1]) if '--distancia' in a else 20.0
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 't14'))
import pega_banco as B  # noqa: E402

from armas import empunhadura  # noqa: E402

EPO = B.EPO
B.configurar(ARMA, CATEGORIA, trabalho=TRABALHO)
B.CFG['blend'] = BLEND
B.carregar()
original_resolver = EPO.resolver
ik_n = [0]


def cruza(col, m, livre, resto, na):
    pts = na.pontos(m.pose())
    return {'naMao': round(col.profundidade_nos_pontos(pts, livre, resto, empunhadura.PERTO_MM), 3),
            'dobraTenar': round(EPO.dobra_da_tenar(col, pts), 3),
            'naArma': round(na.penetracao(pts, na.vertices(EPO.LIVRE + EPO.TENAR)), 3)}


def resolver(cadeia, alvo, normal, lim, inicio=None, na=None, m=None, eixo=None):
    t0 = time.time()
    g0 = original_resolver(cadeia, alvo, normal, lim, inicio, na, m, eixo)
    if na is None:
        return g0
    mao = B.C['mao']
    livre, resto = EPO._livre_e_resto(na.col)
    tabela = EPO.tabela_da_dobra(na.col, cadeia, lim)

    def custo_de(gg):
        return EPO._custo(cadeia, gg, alvo, normal, na, eixo)

    def com_tabela(gg):
        return custo_de(gg) + EPO._custo_da_dobra(EPO._na_tabela(tabela, gg))

    vertices = na.vertices(EPO.LIVRE + EPO.TENAR)

    def com_malha(gg):
        pts = na.pontos(EPO._com_graus(m, cadeia, gg).pose())
        return (custo_de(gg) + EPO.PESO_MALHA ** 2 * (na.entrada_quadrada(pts, vertices)
                                                      + EPO.dobra_da_tenar(na.col, pts) ** 2)
                + EPO._custo_da_dobra(EPO.dobra_da_pele(na.col, pts)))

    print('SOLVER', json.dumps({'ik': ik_n[0], 'inicio': inicio and EPO.totais(mao, inicio),
                                'graus': EPO.totais(mao, g0), 'capsulas': round(com_tabela(g0), 3),
                                'malha': round(com_malha(g0), 3),
                                'cruza': cruza(na.col, EPO._com_graus(m, cadeia, g0), livre, resto, na),
                                'segundos': round(time.time() - t0, 1)}), flush=True)
    t1 = time.time()
    grade = EPO._grade(com_tabela, lim)
    escolhidos = []
    for c, g in grade:
        if all(max(abs(g[k] - e[1][k]) for k in EPO.GRAUS) >= DISTANCIA for e in escolhidos):
            escolhidos.append((c, g))
            if len(escolhidos) == N:
                break
    for k, (c, g) in enumerate(escolhidos):
        gp = EPO._padrao(com_tabela, lim, g, com_tabela(g))
        gr = EPO.refinar_na_malha(custo_de, lim, gp, na, m, cadeia)
        print('PARTIDA', json.dumps({'ik': ik_n[0], 'k': k, 'grade': EPO.totais(mao, g), 'custoGrade': round(c, 3),
                                     'padrao': EPO.totais(mao, gp), 'capsulas': round(com_tabela(gp), 3),
                                     'refino': EPO.totais(mao, gr), 'malha': round(com_malha(gr), 3),
                                     'cruza': cruza(na.col, EPO._com_graus(m, cadeia, gr), livre, resto, na)}),
              flush=True)
    print('PARTIDAS-SEGUNDOS', ik_n[0], round(time.time() - t1, 1), flush=True)
    ik_n[0] += 1
    return g0


EPO.resolver = resolver
if '--completa' in a:
    B.resolver()
else:
    for lado in LADOS.split(','):
        s = B.mao(lado)
print('FIM', flush=True)
