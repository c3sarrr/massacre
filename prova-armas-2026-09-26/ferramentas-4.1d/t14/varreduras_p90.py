"""As varreduras da Tarefa 15 (a P90 na mão), para pôr na fila do servidor (t13/servidor.py; cada uma num trabalho:
`import varreduras_p90 as V; V.direita_dedos_1()` etc., depois do `pega_banco.carregar()` com
`configurar('p90', 'smgBullpup')`). Cada linha RESUMO é uma pega; o JSON inteiro de cada varredura vai para
<TRABALHO>/<nome>.json. Os resultados estão no registro da Tarefa 15 no plano da 4.1d.

A mão do gatilho é a direita do fuzil no pescoço entre as duas aberturas (o soquete mao_d), com a âncora da MCP do
indicador a partir do ponto do gatilho (mm), a diagonal (no plano da palma: positiva leva as pontas para cima), o giro
em volta do eixo do punho (Z), a inclinação da mão para trás em volta do lado (Y: positiva leva as pontas para baixo e
o punho para trás) e a altura do ponto no gatilho, com o polegar pelo oval de trás (o furo `ovalTras`). A mão de apoio
é a LATERAL no lóbulo da frente (o soquete mao_e), com a âncora da palma a partir dele (mm) e as giradas em volta do X
(a inclinação), do Y (no plano da face) e do Z (a guinada: o dorso para o jogador), com a luva da direita de obstáculo:
cada varredura dela resolve antes a mão do gatilho da regra (`gatilho`), no mesmo servidor, ou usa a última que ele
resolveu (sem `gatilho`). `sem_polegar=True` deixa o polegar no afastado da chegada (o do furo, o deitado e o que dá a
volta por baixo da peça — o 'baixo' da LATERAL — levam de 15 s a minutos por pega; os dedos, segundos): a validação
acusa o polegar, e o resto da pega vale. O servidor vive 2 h (o limite do processo em segundo plano): cada pega vai
para o <nome>.progresso assim que sai, e as varreduras longas vão em partes.
"""
import itertools
import json

import pega_banco as B
from armas import empunhadura_furo as EF
from armas import empunhadura_pega as EP

FURO = {'furo': 'ovalTras', 'saida': [0.0, 1.0, 0.0], 'eixo': [1.0, 0.0, 0.0]}


def direita(dx, dz, diagonal, giro=0.0, inclina=None, altura=0.6, folga=1.0, dy=-40.0, afastado=True, polegar=None,
            tomba=None, juntar=False):
    """`tomba`: a girada em volta do X do soquete (o eixo da arma), antes das outras — negativa leva o lado do mínimo
    para fora da face e o do polegar para dentro (a palma virada para baixo e para a arma)."""
    giros = [['Z', giro]] if inclina is None else [['Y', inclina], ['Z', giro]]
    if tomba is not None:
        giros = [['X', tomba]] + giros
    cfg = {'ancora': {'ponto': 'mcp_indicador', 'de': 'gatilho', 'mm': [dx, dy, dz]}, 'diagonal': diagonal,
           'giros': giros, 'gatilho': {'altura': altura, 'abertura': 20.0, 'raio': 8.0, 'folga': folga},
           'polegar_afastado': afastado, 'polegar': polegar or FURO}
    if juntar:
        # os dedos lado a lado (empunhadura_arma.juntar_dedos, o da mão da frente e da de apoio): o de fora gira na MCP
        # para o vizinho e fecha de novo
        cfg['juntar'] = True
    return cfg


def esquerda(z, inc, gir, guin, x=0.0, y=0.0, polegar=None):
    cfg = {'ancora': {'ponto': 'palma', 'de': 'soquete', 'mm': [x, y, z]},
           'giros': [['X', inc], ['Y', gir], ['Z', guin]]}
    if polegar is not None:
        cfg['polegar'] = polegar
    return cfg


def _resumo(chave, s):
    ll = s.get('ladosLateral') or {}
    pol = s.get('polegar') or {}
    nf = s.get('polegarNoFuro') or {}
    extra = {'medias': ll.get('mediasGraus'), 'polpas': ll.get('polpasMM'), 'direita': ll.get('direitaMM'),
             'dorso': ll.get('dorsoGraus'), 'polegarGraus': ll.get('polegarGraus'),
             'dorsoJog': s.get('dorsoAoJogadorGraus'), 'indicador': (s.get('indicador') or {}).get('graus'),
             'polpaAlvo': (s.get('indicador') or {}).get('polpaAoAlvoMM'),
             'polegar': {k: pol.get(k) for k in ('distalAoEixoGraus', 'polpaEncostaMM', 'coladoMM', 'curvaGraus')},
             'furo': {k: nf.get(k) for k in ('dentro', 'folgaBordaMM', 'ladoErradoMM')},
             'distal': s.get('distalDoPolegar'), 'aFrente': s.get('distalAFrenteGraus'),
             'ponta': s.get('pontaDoPolegar'),
             'juntos': {k: v[0] for k, v in (s.get('juntosMM') or {}).items()}, 'centros': s.get('centros'),
             'alto': s.get('altoDoDedoMM'), 'atravessa': (s.get('luva') or {}).get('atravessaMM'),
             'luva': {k: s.get(k) for k in ('penetracaoLuvaMM', 'folgaLuvaMM', 'pertoDaLuva')},
             'entra': s.get('entraPorOsso')}
    print('RESUMO', json.dumps(chave), s.get('erro', '')[:160], json.dumps(extra, ensure_ascii=False),
          'contatos', json.dumps(s.get('contatosMM')), 'pen', s.get('penetracaoMM'),
          'problemas', json.dumps(s.get('problemas'), ensure_ascii=False)[:700], flush=True)


def rodar(nome, lado, cfgs, sem_polegar=False, base=None, gatilho=None, vistas=None):
    """Cada pega da lista (chave, correções) na mão `lado`; com `gatilho` (as correções da mão direita), a mão do
    gatilho resolvida antes, de obstáculo para a de apoio; com `vistas`, os renders de cada pega
    (<nome>_<chave>_<vista>.png em <TRABALHO>/renders). Cada pega também vai, assim que sai, para
    <TRABALHO>/<nome>.progresso (uma linha JSON por pega): a saída do trabalho só aparece no fim dele."""
    deitar, passar = EP._deitar, EF.passar
    alvo_na_arma, fechar_no_alvo = EP.polegar.alvo_na_arma, EP.polegar.fechar_no_alvo
    if gatilho is not None:
        s = B.mao('d', gatilho, base=base)
        _resumo('gatilho', s)
    if sem_polegar:
        def _sem_deitar(col, na, mao, m, *_a, **_k):
            return m, {'erro': 'sem o polegar (a varredura dos dedos)'}

        def _sem_passar(col, mao, m, na, *_a, **_k):
            return m, {'erro': 'sem o polegar (a varredura dos dedos)'}
        def _sem_alvo(*_a, **_k):
            return None, None

        def _sem_fechar(col, mao, m, *_a, **_k):
            return m, {'erro': 'sem o polegar (a varredura dos dedos)', 'encostou': False, 'polpaEncostaMM': None}
        EP._deitar = _sem_deitar
        EF.passar = _sem_passar
        # o polegar que dá a volta (o 'baixo' da LATERAL: empunhadura_pega._pegar, o último ramo)
        EP.polegar.alvo_na_arma = _sem_alvo
        EP.polegar.fechar_no_alvo = _sem_fechar
    res = []
    progresso = f"{B.CFG['trabalho']}/{nome}.progresso"
    open(progresso, 'w', encoding='utf-8').close()
    try:
        for chave, cfg in cfgs:
            rotulo = '_'.join(str(c).replace('.0', '').replace('-', 'm') for c in chave)
            s = B.mao(lado, cfg, base=base, vistas=vistas, nome=f'{nome}_{rotulo}')
            res.append(s)
            _resumo(chave, s)
            with open(progresso, 'a', encoding='utf-8') as f:
                f.write(json.dumps(s, ensure_ascii=False, default=str) + '\n')
    finally:
        EP._deitar, EF.passar = deitar, passar
        EP.polegar.alvo_na_arma, EP.polegar.fechar_no_alvo = alvo_na_arma, fechar_no_alvo
    with open(f"{B.CFG['trabalho']}/{nome}.json", 'w', encoding='utf-8') as f:
        json.dump(res, f, ensure_ascii=False, default=str)


def direita_dedos_1(parte=0, partes=1):
    """A mão do gatilho no pescoço, de pé (as pontas para a frente): a âncora da MCP do indicador, a diagonal e a altura
    do ponto no gatilho (sem o polegar). `parte`/`partes`: a fatia da grade (um servidor cada)."""
    g = list(itertools.product((-40.0, -50.0, -60.0), (-15.0, 0.0, 12.0), (-30.0, -15.0, 0.0, 15.0), (0.6, 0.74)))
    g = g[parte::partes]
    rodar(f'p90_d1_{parte}', 'd', [((dx, dz, d, h), direita(dx, dz, d, altura=h)) for dx, dz, d, h in g],
          sem_polegar=True)


def ver(nome, lado, chaves_cfgs, vistas, sem_polegar=True, gatilho=None):
    """Os renders das pegas dadas ((chave, correções)), sem guardar a varredura de novo."""
    rodar(nome, lado, chaves_cfgs, sem_polegar=sem_polegar, gatilho=gatilho, vistas=vistas)


def direita_dedos_2(parte=0, partes=1):
    """A mão do gatilho alta e inclinada para trás (Y): a linha dos nós paralela à frente do punho, que desce para trás
    (o canto de baixo do pescoço e a borda da frente do lóbulo de trás, no vão entre os lóbulos), o indicador descendo
    para o gatilho e o médio, o anelar e o mínimo abraçando por baixo dele (sem o polegar). Na direita_dedos_1 (a mão
    de pé, as pontas para a frente), os três de baixo ficavam esticados na face direita, sem nada em que fechar."""
    g = list(itertools.product((-35.0, -45.0, -55.0), (5.0, 15.0, 25.0), (20.0, 30.0, 40.0, 50.0), (0.0, 15.0)))
    g = g[parte::partes]
    rodar(f'p90_d2_{parte}', 'd', [((dx, dz, i, d), direita(dx, dz, d, inclina=i)) for dx, dz, i, d in g],
          sem_polegar=True)


def direita_dedos_3(parte=0, partes=1):
    """A mão do gatilho baixa, de pé (sem a inclinação): o anelar e o mínimo abraçando a borda da frente do lóbulo de
    trás no vão entre os lóbulos (a (−40, −15) da direita_dedos_1 com a diagonal de −15°: o mínimo fechou 65° a 73° e
    passou para o lado esquerdo), e o médio procurando a abertura da frente, embaixo do gatilho (lá ele ficava deitado
    na face direita do lóbulo da frente): a âncora 5 a 15 mm mais alta, a diagonal e o giro em volta do punho (o
    negativo afasta as pontas da face, para a MCP fechar antes de encostar) — sem o polegar."""
    g = list(itertools.product((-35.0, -40.0, -45.0), (-10.0, -5.0, 0.0), (-25.0, -15.0, -5.0), (0.6, 0.74),
                               (0.0, -15.0)))
    g = g[parte::partes]
    rodar(f'p90_d3_{parte}', 'd', [((dx, dz, d, h, gi), direita(dx, dz, d, gi, altura=h)) for dx, dz, d, h, gi in g],
          sem_polegar=True)


def direita_dedos_4(parte=0, partes=1):
    """A grade larga da mão do gatilho (sem o polegar): a âncora, a inclinação para os dois lados (a negativa leva as
    pontas para cima e a linha dos nós para trás no alto), a diagonal — para achar onde o médio, o anelar e o mínimo
    fecham em volta de alguma borda (a abertura da frente embaixo do gatilho, o canto de baixo do pescoço, a borda da
    frente do lóbulo de trás no vão) em vez de deitar na face direita do lóbulo da frente."""
    g = list(itertools.product((-35.0, -45.0, -55.0), (-20.0, -10.0, 0.0, 10.0), (-30.0, -15.0, 0.0, 15.0, 30.0),
                               (-20.0, 0.0, 20.0)))
    g = g[parte::partes]
    rodar(f'p90_d4_{parte}', 'd', [((dx, dz, i, d), direita(dx, dz, d, inclina=i)) for dx, dz, i, d in g],
          sem_polegar=True)


def direita_dedos_5(parte=0, partes=1):
    """O indicador no alto do gatilho (30 % e 45 % da altura dele) e a mão alta, para o médio entrar na abertura da
    frente embaixo do gatilho, em volta da borda de trás dela (na grade larga, ele ficava deitado na face direita: a
    falange proximal batia no seletor e no canto de baixo da abertura) — sem o polegar."""
    g = list(itertools.product((-40.0, -50.0), (0.0, 8.0, 16.0), (0.3, 0.45), (-10.0, 5.0), (0.0, 15.0)))
    g = g[parte::partes]
    rodar(f'p90_d5_{parte}', 'd', [((dx, dz, h, d, i), direita(dx, dz, d, inclina=i, altura=h))
                                    for dx, dz, h, d, i in g], sem_polegar=True)


def direita_dedos_6(parte=0, partes=1):
    """Dois dedos no guarda-mato superdimensionado: o indicador no alto do gatilho e o médio entrando na abertura da
    frente embaixo dele (na direita_dedos_5, a (−50, 0) com a diagonal de 5° e a (−40, 16) com −10° levavam a ponta do
    médio para o lado esquerdo, pela abertura), e o anelar e o mínimo no vão entre os lóbulos — a fina em volta delas.
    A inclinação (Y) é a mesma rotação da diagonal na mão direita (a palma de lado): só a diagonal varia. Sem o
    polegar."""
    g = list(itertools.product((-45.0, -50.0, -55.0), (0.0, 5.0, 10.0, 15.0), (-15.0, -5.0, 5.0), (0.35, 0.45)))
    g = g[parte::partes]
    rodar(f'p90_d6_{parte}', 'd', [((dx, dz, d, h), direita(dx, dz, d, altura=h)) for dx, dz, d, h in g],
          sem_polegar=True)


def direita_dedos_7(parte=0, partes=1):
    """A mão tombada em volta do eixo da arma (X negativo: o lado do mínimo sai da face e o do polegar entra), para o
    médio, o anelar e o mínimo fecharem em garra até as pontas encostarem na face, em vez de deitar esticados nela — na
    face direita chata do quadro embaixo do gatilho não há borda para eles abraçarem (só o indicador cabe na abertura da
    frente, no gatilho). Sem o polegar."""
    g = list(itertools.product((-10.0, -20.0, -30.0), (-40.0, -50.0), (-5.0, 5.0), (0.0, 10.0)))
    g = g[parte::partes]
    rodar(f'p90_d7_{parte}', 'd', [((t, dx, dz, d), direita(dx, dz, d, tomba=t)) for t, dx, dz, d in g],
          sem_polegar=True)


def direita_dedos_8(parte=0, partes=1):
    """A mão baixa com os dedos de baixo lado a lado (`juntar`): na direita_dedos_3, o mínimo fechava por baixo do
    lóbulo da frente e o anelar ficava deitado na face (leque de 20 a 30 mm). Sem o polegar."""
    g = list(itertools.product((-40.0, -45.0), (-10.0, -5.0, 0.0), (-15.0, -5.0), (0.6, 0.74)))
    g = g[parte::partes]
    rodar(f'p90_d8_{parte}', 'd', [((dx, dz, d, h), direita(dx, dz, d, altura=h, juntar=True)) for dx, dz, d, h in g],
          sem_polegar=True)


def direita_dedos_9(parte=0, partes=1):
    """A C da varredura com o polegar (−40; 0, sem diagonal: passou em todas as validações, com os três dedos de baixo
    deitados na face) com o giro em volta do eixo do punho (Z: o negativo afasta as pontas da face, o positivo as
    encosta) e a âncora 5 mm mais baixa. Sem o polegar."""
    g = list(itertools.product((-10.0, -5.0, 5.0, 10.0), (0.0, -5.0), (-40.0, -45.0)))
    g = g[parte::partes]
    rodar(f'p90_d9_{parte}', 'd', [((gi, dz, dx), direita(dx, dz, 0.0, gi)) for gi, dz, dx in g], sem_polegar=True)


def direita_dedos_10(parte=0, partes=1):
    """O indicador no pé do gatilho (74 % e 85 % da altura dele) com a mão baixa e recuada: o médio e o anelar na altura
    do entalhe entre o punho e o lóbulo, com a PIP dentro dele (a MCP 50 a 58 mm atrás do gatilho), para fecharem em
    volta da parede de trás do entalhe (a frente do punho); com a MCP 35 a 45 mm atrás, a falange proximal atravessava o
    entalhe e deitava na face do lóbulo da frente. Sem o polegar."""
    g = list(itertools.product((-50.0, -54.0, -58.0), (-12.0, -18.0), (0.74, 0.85), (-10.0, 0.0, 8.0)))
    g = g[parte::partes]
    rodar(f'p90_d10_{parte}', 'd', [((dx, dz, h, d), direita(dx, dz, d, altura=h)) for dx, dz, h, d in g],
          sem_polegar=True)


# A mão do gatilho escolhida (a C da varredura com o polegar: a MCP do indicador 40 mm atrás e 40 mm à direita do ponto
# do gatilho, na altura dele, sem diagonal, o ponto a 60 % da altura do gatilho): passa em todas as validações, com o
# polegar pelo oval de trás saindo deitado para a frente no lado esquerdo e os nós à direita do meio da arma, como os da
# luva do gatilho no quadro do CS2; o médio, o anelar e o mínimo ficam deitados na face direita (o mínimo dá a volta
# por baixo do lóbulo da frente) — não há borda embaixo do gatilho para eles fecharem (ver direita_dedos_1 a 10)
GATILHO = direita(-40.0, 0.0, 0.0, altura=0.6)


def esquerda_1(parte=0, partes=1):
    """A mão de apoio pela LATERAL no lóbulo da frente, com a mão do gatilho de obstáculo (GATILHO): o soquete mao_e
    fica no meio da barra embaixo da abertura da frente (x −128, z −80; a barra vai de −102, o pé do lóbulo, a −60, a
    borda de baixo da abertura), e a palma da LATERAL do bloco (62,5 mm abaixo do meio da peça) cairia abaixo do pé do
    lóbulo. A palma de 5 a 20 mm abaixo do soquete, 10 mm para trás e para a frente, a inclinação (X), a girada no
    plano da face (Y, as pontas para a frente) e a guinada (Z, o dorso para o jogador). Com o polegar 'baixo' da
    regra."""
    g = list(itertools.product((-10.0, 0.0, 10.0), (-5.0, -12.5, -20.0), (-12.5, -5.0), (0.0, 7.5), (15.0, 20.0)))
    g = g[parte::partes]
    rodar(f'p90_e1_{parte}', 'e', [((x, z, i, gi, gu), esquerda(z, i, gi, gu, x=x)) for x, z, i, gi, gu in g],
          gatilho=GATILHO)


def esquerda_dedos_1(parte=0, partes=1):
    """A grade da esquerda_1 sem o polegar (o 'baixo' levava minutos por pega: os 3 servidores passaram de 50 min nas 72
    sem terminar e caíram no limite de 2 h, sem nada gravado), com a mão do gatilho da última resolvida no servidor (o
    trabalho `B.mao('d', V.GATILHO)` antes): os dedos subindo pela face esquerda do lóbulo, a palma, o dorso e a luva
    com a luva. O polegar vem depois, nas melhores."""
    g = list(itertools.product((-10.0, 0.0, 10.0), (-5.0, -12.5, -20.0), (-12.5, -5.0), (0.0, 7.5), (15.0, 20.0)))
    g = g[parte::partes]
    rodar(f'p90_ed1_{parte}', 'e', [((x, z, i, gi, gu), esquerda(z, i, gi, gu, x=x)) for x, z, i, gi, gu in g],
          sem_polegar=True)


def esquerda_dedos_2(parte=0, partes=1):
    """A mão de apoio 10 a 30 mm mais para a frente que o soquete (a palma de x −118 a −98), sem o polegar: na
    esquerda_dedos_1 (a palma em volta do soquete) o polegar de repouso batia no polegar direito que sai do oval, e o
    'baixo' da primeira pega passada a ele (a −12,5; −5°, 7,5°, 15°) não achou pose sem cruzar a arma ou a mão — embaixo
    do lóbulo, de x −145 a −170, fica o mínimo da mão do gatilho (a C). Mais para a frente, o polegar passa por baixo da
    parte da frente do lóbulo, longe dele, e os nós da luva de apoio chegam mais perto da boca na tela, como no quadro
    pronto do CS2 (os nós quase embaixo do quebra-chama)."""
    g = list(itertools.product((10.0, 20.0, 30.0), (-5.0, -12.5, -20.0), (-12.5, -5.0), (0.0, 7.5), (15.0, 20.0)))
    g = g[parte::partes]
    rodar(f'p90_ed2_{parte}', 'e', [((x, z, i, gi, gu), esquerda(z, i, gi, gu, x=x)) for x, z, i, gi, gu in g],
          sem_polegar=True)


def esquerda_dedos_3(parte=0, partes=1):
    """A palma da LATERAL abaixo do lóbulo, como na AWP (−72,5 mm do meio do guarda-mão de 46 mm de face) e no bloco
    da prova (−62,5 do meio da peça de 56): o soquete mao_e fica no meio da barra embaixo da abertura da frente (42 mm,
    de z −102 a −60), e a palma vai de 45 a 75 mm abaixo dele — o punho embaixo do lóbulo, os nós perto do pé dele, os
    dedos subindo pela face da barra (o indicador e o médio até a abertura, onde as pontas podem enganchar; o anelar e o
    mínimo pela parte da frente do lóbulo) e o polegar com espaço para passar por baixo da peça. Na esquerda_dedos_1 e
    na _2 (a palma de 5 a 20 mm abaixo do soquete) a palma ficava em cima da face, os dedos subiam até o carregador (as
    pontas a z +30 a +50) e o polegar 'baixo' não passava por baixo do lóbulo (6 das 7 pegas sem pose, e a outra com a
    polpa subindo pela face direita, a 91,8° do lugar). Sem o polegar."""
    g = list(itertools.product((0.0, 10.0, 20.0), (-45.0, -55.0, -65.0, -75.0), (-12.5, -5.0), (0.0, 7.5),
                               (15.0, 20.0)))
    g = g[parte::partes]
    rodar(f'p90_ed3_{parte}', 'e', [((x, z, i, gi, gu), esquerda(z, i, gi, gu, x=x)) for x, z, i, gi, gu in g],
          sem_polegar=True)


def esquerda_dedos_4(parte=0, partes=1):
    """A palma abaixo do lóbulo, recuada (10 e 20 mm atrás do soquete) e com as pontas giradas para trás no plano da
    face (Y de −7,5° e −15°): na esquerda_dedos_3, com a palma no soquete ou à frente, o mínimo — o dedo da frente da
    mão esquerda — passava da frente do lóbulo, onde ele sobe arredondado até a boca, e ficava no ar (a polpa a 19 a 41
    mm da arma, em leque com o anelar). Sem o polegar."""
    g = list(itertools.product((-10.0, -20.0), (-50.0, -60.0, -70.0), (-12.5, -5.0), (-7.5, -15.0), (15.0, 20.0)))
    g = g[parte::partes]
    rodar(f'p90_ed4_{parte}', 'e', [((x, z, i, gi, gu), esquerda(z, i, gi, gu, x=x)) for x, z, i, gi, gu in g],
          sem_polegar=True)


# as pegas da mão de apoio que passam em tudo o que é dos dedos (esquerda_dedos_4): a palma 10 a 20 mm atrás e 50 a 60
# mm abaixo do soquete, inclinada −12,5°, as pontas 7,5° para trás no plano da face e a guinada de 15° a 20°
APOIO_LIMPAS = [(-10.0, -50.0, -12.5, -7.5, 15.0), (-10.0, -60.0, -12.5, -7.5, 20.0), (-20.0, -50.0, -12.5, -7.5, 15.0),
                (-20.0, -60.0, -12.5, -7.5, 20.0)]


def esquerda_polegar_1(lados=((0.0, 0.0, -1.0), (0.0, 0.25882, -0.96593)), pegas=None):
    """O 'baixo' com o lado do polegar só para baixo (e 15° para a esquerda): com o da LATERAL (30° para a direita), a
    busca do alvo leva a polpa o mais longe para baixo e para a direita na arma com a luva do gatilho de obstáculo, e o
    mais longe é o mínimo dela, que dá a volta por baixo do lóbulo (as pegas da ep2: o polegar assenta nele, a 25 a 28
    mm da arma, e a validação reprova o lugar). Para baixo, a polpa assenta no pé do lóbulo, antes do mínimo."""
    pegas = pegas or APOIO_LIMPAS
    rodar('p90_ep3', 'e', [((x, z, i, gi, gu, round(l[1], 2)), {**esquerda(z, i, gi, gu, x=x),
                                                               'polegar': {'lado': l, 'peso': 4.0}})
                            for x, z, i, gi, gu in pegas for l in lados], vistas='fora,jogador,baixo,dir')


def esquerda_dedos_5(parte=0, partes=1):
    """A mão de apoio com o polegar à frente do mínimo da mão do gatilho: nas pegas limpas da esquerda_dedos_4 (a palma
    10 a 20 mm atrás do soquete), o polegar 'baixo' passa por baixo do lóbulo e assenta no mínimo da mão do gatilho (a
    ponta dele em x −150 a −165, 5 mm abaixo do pé do lóbulo), com qualquer lado (a busca do alvo pesa mais o encosto e
    a normal da polpa que o lado). Com a palma no soquete ou à frente dele, a base do polegar fica à frente do
    mínimo; as pontas mais giradas para trás no plano da face (Y até −22,5°) seguram o mínimo da mão de apoio em cima
    do lóbulo, que sobe arredondado na frente. Sem o polegar."""
    g = list(itertools.product((0.0, 5.0, 10.0, 15.0), (-50.0, -60.0), (-12.5,), (-7.5, -15.0, -22.5), (15.0, 20.0)))
    g = g[parte::partes]
    rodar(f'p90_ed5_{parte}', 'e', [((x, z, i, gi, gu), esquerda(z, i, gi, gu, x=x)) for x, z, i, gi, gu in g],
          sem_polegar=True)


# as pegas da esquerda_dedos_5 que passam em tudo o que é dos dedos, com a palma à frente do mínimo da mão do gatilho
APOIO_A_FRENTE = [(5.0, -60.0, -12.5, -22.5, 15.0), (10.0, -60.0, -12.5, -22.5, 15.0),
                  (15.0, -60.0, -12.5, -22.5, 15.0), (15.0, -50.0, -12.5, -22.5, 15.0),
                  (10.0, -60.0, -12.5, -22.5, 20.0), (15.0, -60.0, -12.5, -22.5, 20.0),
                  (5.0, -60.0, -12.5, -15.0, 15.0), (5.0, -50.0, -12.5, -22.5, 15.0)]


def esquerda_polegar_2(parte=0, partes=1):
    """O 'baixo' da regra nas pegas da APOIO_A_FRENTE, com as vistas das duas luvas."""
    pegas = APOIO_A_FRENTE[parte::partes]
    rodar(f'p90_ep4_{parte}', 'e', [((x, z, i, gi, gu), esquerda(z, i, gi, gu, x=x)) for x, z, i, gi, gu in pegas],
          vistas='fora,jogador,baixo,dir')


def esquerda_polegar_na_arma(nome, pegas, vistas='fora,jogador,baixo,dir'):
    """O 'baixo' com o alvo do polegar buscado só na arma (a luva do gatilho fica de obstáculo no fechar, não de
    apoio): nas pegas da ep2 a ep4, a busca do alvo (empunhadura_polegar.alvo_na_arma) corria na arma com a outra
    luva, e a superfície mais perto da polpa, embaixo do lóbulo, era sempre a mão do gatilho — o polegar assentava
    nela, a 25 a 35 mm da arma. A prova troca o `na` da busca pelo da arma sozinha (o mesmo encaixe)."""
    import copy as _copy
    original = EP.polegar.alvo_na_arma

    def alvo_so_na_arma(cadeia, na, m, lim, lado, peso_lado):
        na_arma = _copy.copy(na)
        na_arma.arma = B.C['arma']
        return original(cadeia, na_arma, m, lim, lado, peso_lado)

    EP.polegar.alvo_na_arma = alvo_so_na_arma
    try:
        rodar(nome, 'e', [((x, z, i, gi, gu), esquerda(z, i, gi, gu, x=x)) for x, z, i, gi, gu in pegas],
              vistas=vistas)
    finally:
        EP.polegar.alvo_na_arma = original


# as 36 pegas da esquerda_dedos_4 e _5 que passam em tudo o que é dos dedos, sem dedo dentro da arma nem da outra luva
APOIO_DEDOS_LIMPOS = [
    (-20.0, -60.0, -12.5, -7.5, 15.0), (-20.0, -60.0, -12.5, -7.5, 20.0), (-20.0, -50.0, -12.5, -7.5, 15.0),
    (-20.0, -50.0, -12.5, -7.5, 20.0), (-20.0, -50.0, -5.0, -7.5, 15.0), (-10.0, -70.0, -12.5, -15.0, 15.0),
    (-10.0, -70.0, -12.5, -7.5, 15.0), (-10.0, -70.0, -12.5, -7.5, 20.0), (-10.0, -60.0, -12.5, -15.0, 15.0),
    (-10.0, -60.0, -12.5, -7.5, 15.0), (-10.0, -60.0, -12.5, -7.5, 20.0), (-10.0, -60.0, -5.0, -7.5, 15.0),
    (-10.0, -50.0, -12.5, -15.0, 15.0), (-10.0, -50.0, -12.5, -15.0, 20.0), (-10.0, -50.0, -12.5, -7.5, 15.0),
    (-10.0, -50.0, -12.5, -7.5, 20.0), (-10.0, -50.0, -5.0, -7.5, 15.0), (0.0, -60.0, -12.5, -15.0, 15.0),
    (0.0, -60.0, -12.5, -15.0, 20.0), (0.0, -60.0, -12.5, -7.5, 15.0), (0.0, -50.0, -12.5, -15.0, 15.0),
    (0.0, -50.0, -12.5, -7.5, 15.0), (5.0, -60.0, -12.5, -22.5, 15.0), (5.0, -60.0, -12.5, -15.0, 15.0),
    (5.0, -60.0, -12.5, -15.0, 20.0), (5.0, -50.0, -12.5, -22.5, 15.0), (5.0, -50.0, -12.5, -15.0, 15.0),
    (5.0, -50.0, -12.5, -7.5, 15.0), (10.0, -60.0, -12.5, -22.5, 15.0), (10.0, -60.0, -12.5, -22.5, 20.0),
    (10.0, -60.0, -12.5, -15.0, 15.0), (10.0, -50.0, -12.5, -15.0, 15.0), (15.0, -60.0, -12.5, -22.5, 15.0),
    (15.0, -60.0, -12.5, -22.5, 20.0), (15.0, -60.0, -12.5, -15.0, 15.0), (15.0, -50.0, -12.5, -22.5, 15.0),
]


def esquerda_polegar_na_arma_todas(parte=0, partes=1):
    """O 'baixo' com o alvo só na arma (esquerda_polegar_na_arma) nas APOIO_DEDOS_LIMPOS: nas quatro da prova (a epa),
    o polegar assentou na arma, a 67° do lugar, e a luva só encostou na do gatilho, mas atravessou a si mesma 2,0 a
    2,6 mm (a tenar, com o polegar recolhido)."""
    esquerda_polegar_na_arma(f'p90_epb_{parte}', APOIO_DEDOS_LIMPOS[parte::partes], vistas=None)
