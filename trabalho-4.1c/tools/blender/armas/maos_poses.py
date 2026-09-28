# As poses de teste das luvas que dependem de contato (Fase 4.1b; desenho em docs/superpowers/specs/2026-09-26-4.1b-
# luvas-e-empunhadura-design.md, seção 4; plano, Tarefa 5), resolvidas pelo núcleo do solver de empunhadura
# (empunhadura.py) e pelo polegar dele (empunhadura_polegar.py):
#  - punho: os quatro dedos fechando para a MCP 85°, a PIP 95° e a DIP 60° contra a palma, os vizinhos separados, e o
#    polegar com a polpa nas costas das falanges médias do indicador e do médio (o alvo no meio das duas), fechado até
#    encostar — o polegar por cima dos dedos, como no punho de verdade;
#  - apontar: o mesmo com o indicador esticado (o mínimo da AAOS em todas as juntas) e a polpa do polegar na falange
#    média do médio;
#  - mesa: as quatro MCP no limite com os dedos esticados (a PIP e a DIP no mínimo), os vizinhos separados, e o polegar
#    fora do caminho deles (a MCP e a IP no mínimo; a CMC estendendo se precisar).
# Os ângulos que o contato segurou antes do alvo vão para o relatório. Problemas: o polegar que não encostou nos dedos
# no punho ou no apontar, ou com o lado da polpa a mais de 0,5 mm da superfície dos dedos do alvo (as três falanges
# deles): o polegar tem de ficar apoiado pela polpa, não só pela base.
# Como na mão de verdade, o polegar sai do caminho antes de os dedos fecharem (para o lado, no plano da palma: a
# abdução palmar e a flexão da CMC no mínimo, a MCP e a IP esticadas) e os dedos fecham contra a mão inteira — a palma,
# a tenar e o polegar afastado; depois o polegar pousa por cima deles, e as pontas que a tenar alcançou (o metacarpo
# do polegar a leva junto) recuam ao contato. Sem isso, a ponta do indicador fechava para dentro da base do polegar de
# repouso (ou da tenar, quando o polegar inteiro saía do obstáculo).
from . import empunhadura, empunhadura_polegar
from .empunhadura import TOLERANCIA_GRAUS, Colisor, Mao, fechar, separar_vizinhos
from .maos import DEDOS4

POLPA_MM = 0.5
_ALVO_DO_POLEGAR = {'punho': {'indicador': 0.7, 'medio': 0.3}, 'apontar': {'medio': 1.0}}


def _fechar_dedos(col, rep, m, dedos):
    """Os dedos da lista fechando para o punho contra a mão (o obstáculo de cada um: a luva sem ele e os vizinhos), os
    vizinhos separados e cada junta recuando ao contato depois da separação. Devolve (pose, {osso: ângulo
    total em que o contato segurou}, correções dos vizinhos)."""
    segurou = {}
    todos = set(col.cabeca)
    total = {1: rep['mcp'], 2: rep['pip'], 3: rep['dip']}
    for d in dedos:
        fora = empunhadura._cadeia(d).union(*(empunhadura._cadeia(v) for v in empunhadura._VIZINHOS[d]))
        obstaculo = col.triangulos(todos - fora)
        for osso, alvo in ((f'{d}_1', 85 - rep['mcp']), (f'{d}_2', 95 - rep['pip']), (f'{d}_3', 60 - rep['dip'])):
            m, graus, encostou = fechar(col, m, osso, alvo, obstaculo)
            if encostou:
                segurou[osso] = round(graus + total[int(osso[-1])], 2)
    m, vizinhos = separar_vizinhos(col, m, DEDOS4)
    # a abertura dos vizinhos mudou onde as pontas encostam
    m = _reassentar(col, rep, m, dedos, segurou)
    return m, segurou, vizinhos


def _reassentar(col, rep, m, dedos, segurou):
    """Cada junta dos dedos que ficou dentro da mão (a palma, a tenar, o polegar, os outros dedos) recua ao contato, da
    ponta para a base; o ângulo total em que o contato segurou vai para `segurou`."""
    todos = set(col.cabeca)
    total = {1: rep['mcp'], 2: rep['pip'], 3: rep['dip']}
    for d in dedos:
        fora = empunhadura._cadeia(d).union(*(empunhadura._cadeia(v) for v in empunhadura._VIZINHOS[d]))
        obstaculo = col.triangulos(todos - fora)
        for osso in (f'{d}_3', f'{d}_2', f'{d}_1'):
            agora = m.flexao.get(osso, 0.0)
            m, graus, _ = fechar(col, m.com(osso, flexao=min(agora, 0.0)), osso, agora, obstaculo)
            if graus < agora - TOLERANCIA_GRAUS:
                segurou[osso] = round(graus + total[int(osso[-1])], 2)
    return m


def _dedos(m):
    return {'flexao': {o: round(g, 2) for o, g in sorted(m.flexao.items()) if not o.startswith('polegar')},
            'abertura': {o: round(g, 2) for o, g in sorted(m.aberturas.items())}}


def poses_de_teste(luva, rig, mao, reforco):
    """{nome: pose} das poses de teste que dependem de contato (punho, apontar, mesa), o relatório de cada uma (os
    ângulos alcançados, as juntas que o contato segurou, as correções entre vizinhos e o polegar) e os problemas."""
    col = Colisor(luva, rig, mao, reforco)
    rep, lim = mao.rep, mao.f['limites']
    poses, rel, problemas = {}, {}, []
    for nome, dedos in (('punho', DEDOS4), ('apontar', ('medio', 'anelar', 'minimo'))):
        m = empunhadura_polegar.afastar(col, mao, Mao())
        if nome == 'apontar':
            for i, j in ((1, 'mcp'), (2, 'pip'), (3, 'dip')):
                m.flexao[f'indicador_{i}'] = lim[j][0] - rep[j]
        m, segurou, vizinhos = _fechar_dedos(col, rep, m, dedos)
        alvo, normal = empunhadura_polegar.alvo_nas_falanges(col, m.pose(), _ALVO_DO_POLEGAR[nome])
        superficie = col.triangulos({f'{d}_{i}' for d in _ALVO_DO_POLEGAR[nome] for i in (1, 2, 3)})
        m, polegar = empunhadura_polegar.fechar_no_alvo(col, mao, m, alvo, normal, superficie)
        # o metacarpo do polegar leva a tenar junto: as pontas que ela alcançou recuam ao contato
        m = _reassentar(col, rep, m, dedos, segurou)
        poses[nome] = m.pose()
        rel[nome] = {**_dedos(m), 'contatoSegurou': segurou, 'vizinhos': vizinhos, 'polegar': polegar}
        if not polegar['encostou']:
            problemas.append(f'pose {nome}: o polegar não encostou nos dedos (a polpa a '
                             f'{polegar["polpaEncostaMM"]} mm deles)')
        elif polegar['polpaEncostaMM'] > POLPA_MM:
            problemas.append(f'pose {nome}: o polegar encostou, mas com o lado da polpa a {polegar["polpaEncostaMM"]} mm '
                             f'dos dedos do alvo (máximo {POLPA_MM} mm)')
    m = Mao()
    for d in DEDOS4:
        m.flexao[f'{d}_1'] = lim['mcp'][1] - rep['mcp']
        m.flexao[f'{d}_2'] = lim['pip'][0] - rep['pip']
        m.flexao[f'{d}_3'] = lim['dip'][0] - rep['dip']
    m, vizinhos = separar_vizinhos(col, m, DEDOS4)
    m, polegar = empunhadura_polegar.abrir(col, mao, m)
    poses['mesa'] = m.pose()
    rel['mesa'] = {**_dedos(m), 'vizinhos': vizinhos, 'polegar': polegar}
    return poses, rel, problemas
