# O polegar deitado e a espera erguida do solver de empunhadura (Fase 4.1b, mão da frente; 4.1c, pistola) — fora de
# empunhadura_polegar.py (a cadeia, os limites, a IK e as buscas, que este módulo usa), que passava das ~600 linhas.
#  - na mão da frente (deitar_na_arma), o polegar deita reto na face do lado dele, apontando para a boca, como na pega
#    "thumb break" (os quatro dedos por baixo do guarda-mão e o polegar esticado ao longo do lado, apontando para o
#    alvo): a IK zera a folga das falanges proximal e distal para a arma ao longo do comprimento (quatro pontos em cada,
#    pela cápsula de seção medida), aponta as duas para o `eixo` e cobra a curva (a MCP mais a IP) além de CURVA_LIVRE; a
#    polpa num ponto, na primeira versão, deixava a CMC no limite da extensão e o polegar dobrado em arco (MCP 35°, IP
#    17°), só com a ponta encostada. O relatório traz a folga medida na malha ao longo do comprimento (`coladoMM`, o pior
#    trecho) e a curva (`curvaGraus`).
#  - na pistola (4.1c), o polegar do gatilho deita por cima do de apoio (`sobre`: a folga, a face e os trechos colados
#    medidos até os ossos do polegar da outra luva), longe do ferrolho que recua (`evitar`), com a CMC da chegada parada
#    se a regra pede (`fixos`); antes de a mão de apoio encaixar, ele espera erguido (erguer), fora do caminho dela.
# Unidades: mm e graus além do repouso (os totais no relatório); o rig em metros no Blender.
import math

from mathutils import Vector

from . import empunhadura
from .empunhadura_polegar import (GRAUS, LIVRE, OSSOS, PESO_COLISAO, PESO_EIXO_MM, TENAR, Cadeia, _com_graus, _cruza,
                                  _entrada_na_arma, _grade, _livre_e_resto, dobra_da_tenar, limites, minimizar,
                                  partidas_da_grade, refinar_na_malha, totais)
from .unidades import S

PONTOS_DEITADO = (0.15, 0.4, 0.65, 0.9)  # ao longo da falange proximal e da distal, na conta da folga do polegar deitado
CURVA_LIVRE = 12.0  # graus da MCP mais a IP que o polegar deitado dobra sem custo (o polegar relaxado não fica reto)
PESO_CURVA_MM = 0.6  # mm de custo por grau de curva além da livre
TRECHOS_DEITADO = ((0.1, 0.4), (0.4, 0.7), (0.7, 0.95))  # os trechos de cada falange na folga medida na malha
# a folga (mm) que a IK do polegar deitado mira: a cápsula é uma média da seção, e a malha encostada nela a 0 costuma
# entrar na arma (a mão da frente do fuzil sobe para 0,3); a primeira que não cruza a arma nem a mão vale. O 0 vem
# primeiro pelo polegar do gatilho da pistola, deitado no de apoio: começando em 0,3 ele ficava 1,1 a 1,4 mm acima dele
# o comprimento inteiro, sem encostar
FOLGAS_DEITADO = (0.0, 0.3, 0.6, 1.0, 1.5)
PESO_FACE_MM = 20.0  # o polegar deitado fora da face do lado dele: mm por unidade de 1 − cos entre as normais
# a peça que o polegar deitado evita (o ferrolho da pistola, 4.1c): a margem além da folga pedida, na conta da cápsula, e
# o peso de cada mm que falta — praticamente uma restrição
FERROLHO_MARGEM_MM = 0.5
PESO_FERROLHO = 30.0


def _folgas_na_arma(cadeia, ms, na, arma=None):
    """(folga, normal) das falanges proximal e distal do polegar para a arma (ou para `arma`, uma peça dela: o ferrolho
    da pistola) em PONTOS_DEITADO de cada uma: a folga (mm, > 0 afastado, < 0 entrando) é a distância do eixo à
    superfície menos o raio da seção medida na direção dela, e a normal é a da face mais perto (unitária, no
    referencial da arma)."""
    bvh = (arma or na.arma).bvh
    folgas = []
    for k in (1, 2):
        m = na.encaixe @ ms[k]
        para_local = m.to_3x3().inverted()
        for t in PONTOS_DEITADO:
            q = m @ Vector((0.0, cadeia.comp[k] * t, 0.0))
            co, n, _i, d = bvh.find_nearest(q)
            dentro = (q - co).dot(n) < 0.0
            direcao = (q - co) if dentro else (co - q)
            if direcao.length < 1e-9:
                direcao = -n
            raio = cadeia.secoes.raio(OSSOS[k], para_local @ direcao)
            folgas.append(((-d if dentro else d) - raio, n))
    return folgas


def colado_na_malha(col, na, pts, medir=None):
    """A folga (mm) do polegar deitado medida na malha: em cada trecho de TRECHOS_DEITADO da falange proximal e da
    distal, a menor distância dos vértices do trecho à arma (o lado que encosta), ou `medir(osso, ponto)` se vier (o
    plano do trilho da M4A4). Devolve a lista, da base para a ponta."""
    rig, lado, medir = col.rig, col.lado, medir or (lambda _o, q: na.arma.distancia(q))
    trechos = []
    repouso = col.modelo.pontos({})
    for osso in LIVRE:
        b = rig.data.bones[f'{osso}_{lado}']
        cabeca, cauda = Vector(b.head_local) / S, Vector(b.tail_local) / S
        eixo = cauda - cabeca
        comp2 = eixo.length_squared
        indices = [i for i, dono in enumerate(col.dono) if dono == osso]
        for a, z in TRECHOS_DEITADO:
            trecho = [i for i in indices if a <= (Vector(repouso[i]) - cabeca).dot(eixo) / comp2 < z]
            if trecho:
                trechos.append(round(min(medir(osso, pts[i]) for i in trecho), 2))
    return trechos


def deitar_na_arma(col, mao, m, na, eixo, face, inicio=None, medir=None, evitar=None, sobre=None, fixos=None):
    """O polegar da mão da frente deitado reto na arma (ver o cabeçalho): a pose `m` com o polegar resolvido e o
    relatório (os graus totais, a folga ao longo do comprimento medida na malha, a curva e o desvio das falanges do
    `eixo`, unitário no referencial da luva), na face do lado `face` (unitária, no referencial da arma: a normal da
    superfície mais perto de cada trecho do polegar tem de ser ela, senão ele deita na face de baixo, ao lado do
    indicador). Se a solução ainda entrar mais que o contato, a MCP e a IP abrem juntas até
    soltar (o polegar fica mais reto, nunca mais curvo); com `inicio`, a busca parte dele (a segunda chegada da palma);
    `medir` vai ao colado_na_malha. Com `evitar` = (peça, folga em mm) — o ferrolho da pistola, que recua no tiro —, as
    falanges ficam a pelo menos a folga da peça (mais FERROLHO_MARGEM_MM: a cápsula é a média da seção). Com `sobre`
    (uma Arma: a superfície em que ele deita — o polegar da luva de apoio, para o do gatilho da pistola), a folga, a face
    e os trechos colados são medidos até ela; `na` (a arma com a outra luva) continua o obstáculo. Os graus de `fixos`
    ficam parados (a CMC com que a palma chegou: a do polegar do gatilho da pistola)."""
    lim = limites(mao)
    if fixos:
        lim = dict(lim, **{k: (float(v), float(v)) for k, v in fixos.items()})
    rep = mao.rep
    cadeia = Cadeia(col, mao, {o: q for o, q in m.pose().items() if not o.startswith('polegar')})

    def custo_de(g, folga_alvo=0.0):
        ms = cadeia.matrizes(g)
        c = 0.0
        for f, n in _folgas_na_arma(cadeia, ms, na, sobre):
            c += (f - folga_alvo) ** 2 + (PESO_FACE_MM * (1.0 - n.dot(face))) ** 2
        if evitar is not None:
            peca, folga = evitar
            for f, _n in _folgas_na_arma(cadeia, ms, na, peca):
                falta = folga + FERROLHO_MARGEM_MM - f
                if falta > 0.0:
                    c += (PESO_FERROLHO * falta) ** 2
        c += PESO_COLISAO ** 2 * (cadeia.penetracao(ms) + _entrada_na_arma(cadeia, ms, na))
        for k in (1, 2):
            c += (PESO_EIXO_MM * (1.0 - (ms[k].to_3x3() @ Vector((0.0, 1.0, 0.0))).normalized().dot(eixo))) ** 2
        curva = g['mcp'] + rep['polegarMcp'] + g['ip'] + rep['polegarIp'] - CURVA_LIVRE
        if curva > 0.0:
            c += (PESO_CURVA_MM * curva) ** 2
        return c

    livre, resto = _livre_e_resto(col)
    # sem `inicio`, as partidas são os melhores pontos distintos da grade, em ordem, e fica o primeiro que deita sem
    # cruzar: o polegar do gatilho da pistola, deitado de novo sobre a tenar de apoio — o melhor ponto da grade, levado
    # pela malha, entrava 6 mm na luva de apoio, e o de segunda ordem deitava por fora dela. Na mão da frente do fuzil
    # o primeiro já não cruza, e a pega é a mesma de antes
    partidas = [minimizar(custo_de, lim, inicio)] if inicio is not None else partidas_da_grade(custo_de, lim)
    primeira = None
    for partida in partidas:
        for folga_alvo in FOLGAS_DEITADO:
            g = refinar_na_malha(lambda gg: custo_de(gg, folga_alvo), lim, partida, na, m, cadeia)
            if not _cruza(col, _com_graus(m, cadeia, g), livre, resto, na):
                break
        if primeira is None:
            primeira = (partida, g)
        if not _cruza(col, _com_graus(m, cadeia, g), livre, resto, na):
            inicio = partida
            break
    else:
        inicio, g = primeira
    if _cruza(col, _com_graus(m, cadeia, g), livre, resto, na):
        aberto = dict(g, mcp=lim['mcp'][0], ip=lim['ip'][0])
        if _cruza(col, _com_graus(m, cadeia, aberto), livre, resto, na):
            # a CMC da solução leva a tenar para dentro da arma; com `inicio` (a CMC com que a palma chegou: ela encostou
            # sem cruzar), o polegar volta em linha para ela até soltar — o polegar do gatilho da pistola, que puxava a
            # pele da tenar 0,4 mm para dentro da traseira do punho a cada nova chegada
            de_volta = dict(inicio, mcp=lim['mcp'][0], ip=lim['ip'][0]) if inicio is not None else None
            if de_volta is None or _cruza(col, _com_graus(m, cadeia, de_volta), livre, resto, na):
                pose = _com_graus(m, cadeia, aberto).pose()
                na_mao = col.profundidade(pose, livre, resto, empunhadura.PERTO_MM)
                na_arma = na.penetracao(na.pontos(pose), na.vertices(LIVRE + TENAR))
                raise empunhadura.PolegarCruza(f'o polegar deitado cruza a mão ({na_mao:.2f} mm) ou a arma '
                                               f'({na_arma:.2f} mm), mesmo com a MCP e a IP abertas (graus '
                                               f'{totais(mao, aberto)})', aberto)
            aberto = de_volta
        anda = max(abs(g[k] - aberto[k]) for k in GRAUS)
        tolerancia = empunhadura.TOLERANCIA_GRAUS / max(anda, 1e-6)
        a, b = 0.0, 1.0  # a entra, b solta
        while b - a > tolerancia:
            s = (a + b) / 2
            if _cruza(col, _com_graus(m, cadeia, {k: g[k] + (aberto[k] - g[k]) * s for k in GRAUS}), livre, resto, na):
                a = s
            else:
                b = s
        g = {k: g[k] + (aberto[k] - g[k]) * b for k in GRAUS}
    m = _com_graus(m, cadeia, g)
    pts = na.pontos(m.pose())
    ms = cadeia.matrizes(g)
    desvio = max(math.degrees(math.acos(max(-1.0, min(1.0, (ms[k].to_3x3() @ Vector((0.0, 1.0, 0.0))).normalized()
                                                         .dot(eixo))))) for k in (1, 2))
    t = totais(mao, g)
    if sobre is not None and medir is None:
        def medir(_osso, q):
            return sobre.distancia(q)
    trechos = colado_na_malha(col, na, pts, medir)
    rel = {'graus': t, 'coladoMM': max(trechos), 'trechosMM': trechos, 'curvaGraus': round(t['mcp'] + t['ip'], 1),
           'desvioDoEixoGraus': round(desvio, 1), 'polpaEncostaMM': round(na.encosto(pts, cadeia.lado_da_polpa), 2)}
    return m, rel


def erguer(col, mao, m, na, cima):
    """O polegar erguido, esperando a outra mão encaixar (o do gatilho da pistola): a pose da grade de `minimizar` com a
    ponta mais alta no `cima` (unitário, no referencial da arma) entre as que não entram na arma nem na própria mão — as
    cápsulas na conta da grade, e a malha conferida da melhor para a pior até a primeira que passa: as falanges fora
    da arma, sem entrar na mão nem dobrar a tenar na palma. A pele da tenar e da palma não conta na arma: a espera é de
    passagem, e qualquer CMC diferente da de chegada a empurrava ~1,4 mm para dentro do punho na mão girada — a
    conferência dela escolhia o polegar esticado para fora, embaixo, no caminho da mão de apoio. O `afastar`, no plano
    da palma, servia ao fuzil; com a mão do gatilho girada atrás da pistola ele punha o polegar dentro do ferrolho.
    Devolve (pose, graus)."""
    lim = limites(mao)
    cadeia = Cadeia(col, mao, {o: q for o, q in m.pose().items() if not o.startswith('polegar')})
    livre, resto = _livre_e_resto(col)
    falanges = na.vertices(LIVRE)

    def custo_de(g):
        ms = cadeia.matrizes(g)
        ponta = na.encaixe @ (ms[2] @ Vector((0.0, cadeia.comp[2], 0.0)))
        return -ponta.dot(cima) + PESO_COLISAO ** 2 * (cadeia.penetracao(ms) + _entrada_na_arma(cadeia, ms, na))

    for _c, g in _grade(custo_de, lim):
        erguido = _com_graus(m, cadeia, g)
        pts = na.pontos(erguido.pose())
        if (col.profundidade_nos_pontos(pts, livre, resto, empunhadura.PERTO_MM) <= empunhadura.CONTATO_MM
                and dobra_da_tenar(col, pts) <= empunhadura.CONTATO_MM
                and na.penetracao(pts, falanges) <= empunhadura.CONTATO_MM):
            return erguido, g
    raise empunhadura.PolegarCruza('nenhuma pose da grade ergue o polegar sem entrar na arma ou na mão', g)
