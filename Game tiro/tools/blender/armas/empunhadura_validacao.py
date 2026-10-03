# A validação da pega de uma arma realista (Fase 4.1b; desenho em docs/superpowers/specs/2026-09-26-4.1b-luvas-e-
# empunhadura-design.md, seção 6.3; separada de empunhadura_pega.py na 4.1c, Tarefa 11): as contas de cada mão na pose
# final, com as duas mãos posadas — bloqueia a exportação:
#  - nenhum vértice da luva a mais de PENETRACAO_MM dentro da arma, medido na malha com o afundamento da palma (a palma
#    que cede, 4.1c: maos_palma.py e empunhadura_palma.py) e sem ceder — o que ainda entra além disso é colisão;
#  - a palma (com a tenar e a hipotenar), cada dedo da regra, a polpa do indicador (no gatilho) ou o indicador indexado
#    (na armação), e a do polegar a no máximo CONTATO_MM da arma (as sondas que o `luvas_contato` do jogo refaz);
#  - a luva sem se atravessar e sem afinar nas juntas (validar_maos.conferir_uma, com o afundamento), os ângulos dentro
#    dos limites da ficha, a mão da frente com o polegar de um lado e os quatro dedos do outro (_lados), o polegar
#    deitado reto (_polegar_deitado), os dedos lado a lado (JUNTOS_MM) e, na pistola, a luva com a luva e os polegares
#    longe do ferrolho (_duas_maos) e o indicador indexado (empunhadura_dedo.problemas).
# Os limites são os de LIMITES_DA_PEGA (src/data/luvas.js), que o validador da saída do Node confere de novo
# (tools/blender/saidaPega.mjs). Unidades: mm e graus além do repouso (os totais no relatório).
from mathutils import Vector

from . import (empunhadura, empunhadura_arma as EA, empunhadura_dedo as dedo_indexado, empunhadura_palma as palma,
               empunhadura_polegar as polegar, luvas, validar_maos)

PENETRACAO_MM = 0.3
CONTATO_MM = 1.0
POLEGAR_SOBRE_MM = 1.0  # a faca: a polpa do polegar a no máximo isto do indicador (desenho da 4.1c, seção 4.3)
LADO_MM = 5.0  # o `ladoMM` de LIMITES_DA_PEGA (src/data/luvas.js): a polpa a pelo menos isto do meio, do lado certo
POLEGAR_CURVA_GRAUS = 20.0  # o `polegarCurvaGraus`: a MCP mais a IP do polegar deitado da mão da frente
POLEGAR_FOLGA_MM = 8.0  # o `polegarFolgaMM`: nenhum trecho do polegar deitado mais longe que isto da arma
# o `polegarEixoGraus` (a pistola, `para_frente` na regra): a falange mais torta do polegar deitado a até isto do eixo
# da regra — deitado em cima do de apoio, o do gatilho saía a 38° dele, para fora da arma, com a folga passando
POLEGAR_EIXO_GRAUS = 20.0
INDEXADO_GATILHO_MM = 5.0  # o `indexadoGatilhoMM`: o indicador indexado da pistola a pelo menos isto do gatilho
# o `indexadoAcimaMM`: o eixo da falange média e da distal do indicador indexado a pelo menos isto acima do alto do
# gatilho — na lateral da armação, não ao longo do guarda-mato. Na Glock, com a âncora da mão 4 mm mais baixa, o
# indicador deitava na lateral do guarda-mato (o meio da distal 23 mm abaixo do alto do gatilho) e as folgas passavam
INDEXADO_ACIMA_MM = 0.0
# o `dedosJuntosMM`: a falange média de cada dedo que abraça a arma a no máximo isto da do vizinho — menos da metade da
# largura dela (17 a 19 mm na ficha); o leque da mão da frente antes de juntar_dedos chegava a 8,5 mm, a mão do gatilho
# fica em 2,5 e 3,3 mm
JUNTOS_MM = 8.0
# a pistola (4.1c; o `luvaPenetracaoMM` e o `folgaFerrolhoMM`): uma luva dentro da outra até isto, e os polegares a pelo
# menos isto do ferrolho
LUVA_PENETRACAO_MM = 0.3
FOLGA_FERROLHO_MM = 2.0
PALMA = ('mao', 'polegar_1', 'anelar_0', 'minimo_0')


def _contatos(col, na, mao, pts, r, gatilho=None):
    """{contato: [vértice, distância em mm]} da regra — a palma, cada dedo que fecha, a polpa do indicador (no gatilho)
    e a do polegar —, com o vértice de cada um mais perto da arma (as sondas). A da polpa do indicador vai até a peça do
    gatilho (`gatilho`, a Arma dela): encostada no guarda-mato, a 10 mm do gatilho, ela contava como no gatilho."""
    # a palma com as eminências (a tenar sobre o metacarpo do polegar e a hipotenar sobre os do anelar e do mínimo): é
    # nelas que a palma apoia num punho reto — o oco do meio fica afastado (o `palmaMeioMM` do relatório)
    grupos = {'palma': na.vertices(PALMA)}
    for d in r['dedos']:
        grupos[d] = na.vertices([f'{d}_{i}' for i in (1, 2, 3)])
    if r['gatilho']:
        grupos['indicador_gatilho'] = EA.CadeiaDedo(na, 'indicador', {}).lado_da_polpa
    if r.get('indexado'):  # o dedo indexado encostado na armação
        grupos[r['indexado']['dedo']] = na.vertices([f"{r['indexado']['dedo']}_{i}" for i in (1, 2, 3)])
    if not r['polegar'].get('sobre'):  # na faca o polegar assenta no indicador, não na arma
        grupos['polegar'] = polegar.Cadeia(col, mao, {}).lado_da_polpa
    saida = {}
    for nome, idx in grupos.items():
        arma = gatilho if nome == 'indicador_gatilho' and gatilho is not None else na.arma
        dist = {i: arma.distancia(pts[i]) for i in idx}
        i = min(dist, key=dist.get)
        saida[nome] = [i, round(dist[i], 3)]
    return saida


def _lados(col, na, mao, pts, r):
    """Os lados da regra (a mão da frente): onde fica a polpa do polegar e a de cada dedo de `r['lados']['dedos']` no
    eixo do lado do polegar (mm, a partir do plano do meio da arma, que passa pela origem dela) — o centro dos vértices
    do lado da polpa do osso distal de cada um —, e os problemas: o polegar a menos de LADO_MM do lado dele ou um dedo a
    menos de LADO_MM do outro lado."""
    eixo = Vector(r['lados']['polegar']).normalized()

    def onde(indices):
        centro = sum((Vector(pts[i]) for i in indices), Vector()) / len(indices)
        return round(centro.dot(eixo), 2)

    lados = {'polegarMM': onde(polegar.Cadeia(col, mao, {}).lado_da_polpa),
             'dedosMM': {d: onde(EA.CadeiaDedo(na, d, {}).lado_da_polpa) for d in r['lados']['dedos']}}
    problemas = []
    if lados['polegarMM'] < LADO_MM:
        problemas.append(f"o polegar a {lados['polegarMM']:.2f} mm do meio da arma (tem de ficar do lado dele, a pelo "
                         f"menos {LADO_MM} mm)")
    for d, v in lados['dedosMM'].items():
        if v > -LADO_MM:
            problemas.append(f'o {d} a {v:.2f} mm do meio da arma, do lado do polegar ou no meio (tem de passar para o '
                             f'outro lado, a pelo menos {LADO_MM} mm)')
    return lados, problemas


def _polegar_deitado(rel_polegar, na='na arma', da='da arma', para_frente=False):
    """Os problemas do polegar deitado da mão da frente (o relatório de empunhadura_polegar_deitado.deitar_na_arma): a curva (a
    MCP mais a IP) além de POLEGAR_CURVA_GRAUS, a falange distal sem encostar (o trecho dela mais perto a mais que o
    contato) ou algum trecho a mais de POLEGAR_FOLGA_MM da arma (`na` e `da`: onde ele deita, no texto — o do gatilho da
    pistola, no polegar de apoio); com `para_frente`, a falange mais torta a mais de POLEGAR_EIXO_GRAUS do eixo."""
    t = rel_polegar['trechosMM']
    meio = len(t) // 2
    problemas = []
    if rel_polegar['curvaGraus'] > POLEGAR_CURVA_GRAUS:
        problemas.append(f"o polegar da frente com {rel_polegar['curvaGraus']}° de curva (máximo {POLEGAR_CURVA_GRAUS}°): "
                         f'tem de ficar reto, deitado {na}')
    if min(t[meio:]) > CONTATO_MM:
        problemas.append(f'a falange distal do polegar da frente não encosta {na} ({min(t[meio:]):.2f} mm)')
    for i, v in enumerate(t):
        if v > POLEGAR_FOLGA_MM:
            problemas.append(f"a falange {'proximal' if i < meio else 'distal'} do polegar da frente a {v:.2f} mm {da} "
                             f'(máximo {POLEGAR_FOLGA_MM} mm)')
    if para_frente and rel_polegar['desvioDoEixoGraus'] > POLEGAR_EIXO_GRAUS:
        problemas.append(f"o polegar a {rel_polegar['desvioDoEixoGraus']}° da frente da arma (máximo "
                         f'{POLEGAR_EIXO_GRAUS}°): tem de apontar para a frente')
    return problemas


def _duas_maos(col, na, pts, r, luva_outra, outra, ferrolho):
    """As contas da luva com a luva da pistola num braço (`pts`: a luva dele na pose final, no referencial da arma): a
    penetração na luva da mão `outra` (`luva_outra`: os pontos e os triângulos dela), os contatos com ela — os quatro
    dedos da mão de apoio (a regra com `luva`) ou o polegar do gatilho, deitado sobre o de apoio (`sobre_luva`) — e a
    folga do polegar ao ferrolho (`ferrolho`, a Arma dele), que recua no tiro. Devolve (o relatório, os problemas)."""
    luva = EA.Arma([], extra=[luva_outra])
    na_l = EA.NaArma(col, luva, na.encaixe, ceder=False)
    grupos = ({d: [f'{d}_{i}' for i in (1, 2, 3)] for d in r['dedos']} if r.get('luva')
              else {'polegar': list(polegar.LIVRE)})
    contatos = {k: round(min(luva.distancia(pts[i]) for i in na_l.vertices(ossos)), 3) for k, ossos in grupos.items()}
    rel = {'penetracaoLuvaMM': round(na_l.penetracao(pts, limite=None), 3), 'contatosLuvaMM': contatos,
           'folgaFerrolhoMM': round(min(ferrolho.distancia(pts[i]) for i in na.vertices(polegar.LIVRE)), 2)}
    problemas = []
    if rel['penetracaoLuvaMM'] > LUVA_PENETRACAO_MM:
        problemas.append(f"a luva entra {rel['penetracaoLuvaMM']:.2f} mm na luva {outra} (máximo {LUVA_PENETRACAO_MM} mm)")
    for k, d in contatos.items():
        if d > CONTATO_MM:
            problemas.append(f'o {k} a {d:.2f} mm da luva {outra} (máximo {CONTATO_MM} mm)')
    if rel['folgaFerrolhoMM'] < FOLGA_FERROLHO_MM:
        problemas.append(f"o polegar a {rel['folgaFerrolhoMM']:.2f} mm do ferrolho (mínimo {FOLGA_FERROLHO_MM} mm: o "
                         'ferrolho recua no tiro)')
    return rel, problemas


def _angulos(mao, m):
    """(os ângulos totais das juntas dos dedos, os problemas de limite): cada flexão dentro da AAOS da ficha, cada
    abertura dentro da faixa do solver (±20° além do repouso) e o desvio da MCP do polegar dentro da faixa da ficha que
    a flexão dela deixa (empunhadura_polegar.faixa_do_desvio)."""
    lim, rep = mao.f['limites'], mao.rep
    faixas = {1: 'mcp', 2: 'pip', 3: 'dip'}
    totais, problemas = {}, []
    for osso, g in sorted(m.flexao.items()):
        if osso.startswith('polegar') or osso.endswith('_0'):
            continue
        junta = faixas[int(osso[-1])]
        a, b = lim[junta]
        totais[osso] = round(g + rep[junta], 2)
        if not a - 0.01 <= totais[osso] <= b + 0.01:
            problemas.append(f'{osso}: {totais[osso]}° fora da {junta} da ficha ({a}–{b}°)')
    lim_p = polegar.limites(mao)
    for osso, g in sorted(m.aberturas.items()):
        if osso == 'polegar_2':
            # o desvio lateral da MCP do polegar: a faixa da ficha que a flexão dela deixa (o efeito came)
            a, b = polegar.faixa_do_desvio(lim_p, m.flexao.get('polegar_2', 0.0))
            if not a - 0.01 <= g <= b + 0.01:
                problemas.append(f'polegar_2: desvio de {g:.2f}° fora da faixa da ficha com a flexão da MCP '
                                 f'({a:.2f}° a {b:.2f}°)')
            continue
        if abs(g) > empunhadura.ABERTURA_MAXIMA + 0.01:
            problemas.append(f'{osso}: abertura de {g:.2f}° (máximo ±{empunhadura.ABERTURA_MAXIMA}°)')
    return totais, problemas


def conferir_mao(f, nome, mao, luva, arma, objetos, perto, afundar, luva_outra=None, outra=None):
    """A validação de uma mão (o registro `f` de empunhadura_pega._uma_mao) na pose final, com o afundamento da palma
    (`afundar`, empunhadura_palma.afundamento) e, na pistola, a luva da outra mão posada (`luva_outra`: pontos e
    triângulos, já com o afundamento dela; `outra`: o lado). Devolve (o relatório da mão, as sondas, os problemas)."""
    r, col, m, rel_m = f['r'], f['col'], f['m'], f['rel']
    pose = m.pose()
    na = EA.NaArma(col, arma, f['na'].encaixe, ceder=False, afundar=afundar)
    pts = na.pontos(pose)
    penetracao = na.penetracao(pts, limite=None)  # sem o limite das buscas: um dedo inteiro dentro da arma conta
    gatilho = EA.Arma([perto['gatilho']]) if r['gatilho'] else None
    sondas = _contatos(col, na, mao, pts, r, gatilho)
    if luva_outra is not None:
        na_luva = EA.NaArma(col, EA.Arma(objetos, extra=[luva_outra]), na.encaixe, ceder=False)
        contatos = _contatos(col, na_luva, mao, pts, r, gatilho)
    else:
        contatos = sondas
    conta, problemas_luva = validar_maos.conferir_uma(col.modelo, luva, luvas.REFORCO, f'pega {nome}', pose, afundar)
    totais, problemas_angulos = _angulos(mao, m)
    meio = min(na.arma.distancia(pts[i]) for i in na.vertices(['mao']))
    rel = {**rel_m, 'penetracaoMM': round(penetracao, 3), 'contatosMM': {k: v[1] for k, v in contatos.items()},
           'palmaMeioMM': round(meio, 2), 'luva': conta, 'angulos': totais, 'palma': palma.resumo(afundar)}
    problemas = []
    if luva_outra is not None:
        rel_duas, problemas_duas = _duas_maos(col, na, pts, r, luva_outra, outra, EA.Arma([perto['ferrolho']]))
        rel.update(rel_duas)
        problemas += [f'pega {nome}: {p}' for p in problemas_duas]
    if r.get('lados'):
        rel['lados'], problemas_lados = _lados(col, na, mao, pts, r)
        problemas += [f'pega {nome}: {p}' for p in problemas_lados]
    if r['polegar'].get('deitado'):
        if 'erro' in rel_m['polegar']:
            problemas.append(f"pega {nome}: o polegar não deita: {rel_m['polegar']['erro']}")
        else:
            onde = (('no polegar de apoio', 'do polegar de apoio') if r['polegar'].get('sobre_luva')
                    else ('na arma', 'da arma'))
            problemas += [f'pega {nome}: {p}' for p in _polegar_deitado(rel_m['polegar'], *onde,
                                                                        r['polegar'].get('para_frente', False))]
    if r.get('indexado'):
        problemas += [f'pega {nome}: {p}' for p in dedo_indexado.problemas(
            rel_m['indicador'], POLEGAR_CURVA_GRAUS, POLEGAR_FOLGA_MM, POLEGAR_EIXO_GRAUS, INDEXADO_GATILHO_MM,
            FOLGA_FERROLHO_MM, INDEXADO_ACIMA_MM, CONTATO_MM)]
    if r['polegar'].get('sobre'):
        pol = rel_m['polegar']
        if pol.get('erro'):
            problemas.append(f"pega {nome}: o polegar não dobra por cima do {', '.join(pol['sobre'])}: {pol['erro']}")
        elif not pol['encostou'] or pol['polpaEncostaMM'] > POLEGAR_SOBRE_MM:
            problemas.append(f"pega {nome}: o polegar não assenta no {', '.join(pol['sobre'])} (a polpa a "
                             f"{pol['polpaEncostaMM']} mm; máximo {POLEGAR_SOBRE_MM} mm)")
    rel['juntosMM'] = EA.folgas_entre_dedos(col, pose, r['dedos'])
    for par, (media, _distal) in rel['juntosMM'].items():
        if media > JUNTOS_MM:
            problemas.append(f'pega {nome}: {par} com a falange média a {media:.2f} mm uma da outra (máximo '
                             f'{JUNTOS_MM} mm): os dedos em leque, não lado a lado')
    if penetracao > PENETRACAO_MM:
        problemas.append(f'pega {nome}: a luva entra {penetracao:.2f} mm na arma (máximo {PENETRACAO_MM} mm)')
    for k, (_i, d) in contatos.items():
        if d > CONTATO_MM:
            problemas.append(f'pega {nome}: o contato {k} a {d:.2f} mm da arma (máximo {CONTATO_MM} mm)')
    problemas += problemas_luva + [f'pega {nome}: {p}' for p in problemas_angulos]
    return rel, sondas, problemas
