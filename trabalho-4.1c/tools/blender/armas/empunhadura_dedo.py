# O dedo deitado reto na arma (Fase 4.1c; desenho da 4.1c, seção 4.2): o indicador da mão do gatilho da pistola
# indexado na lateral da armação, fora do guarda-mato, reto e apontando para a frente — a pose de segurança do passo 2
# da ASJ ("Thumbs Up… Er, Forward!": "the trigger finger should index on the side of the slide"). Decisão do usuário de
# 2026-10-02: com a mão do gatilho girada atrás da arma para o polegar dela apontar para a frente, a polpa do indicador
# não alcançava o gatilho (parava a 2 a 5 mm, deitada na armação); os polegares ficam retos para a frente e o dedo no
# gatilho é da animação do tiro.
# Como o polegar deitado (empunhadura_polegar_deitado.deitar_na_arma): a grade dos quatro graus do dedo (a abertura e as
# flexões da MCP, da PIP e da DIP) e a busca de padrão num custo — a folga de cada falange até a lateral (o eixo a
# `raio` da superfície), a normal dela de frente para a `face`, cada falange ao longo do `eixo`, a curva da PIP e da DIP,
# a entrada na arma, as folgas do ferrolho (que recua no tiro) e do gatilho (fora do guarda-mato) e a altura da
# falange média e da distal acima do alto do gatilho (na lateral da armação, não ao longo do guarda-mato) —; depois a
# malha: se a luva ainda entra na arma, o raio cresce em passos até soltar.
# Unidades: mm e graus além do repouso, no referencial da arma.
import itertools
import math

from mathutils import Vector

from . import empunhadura_arma as EA
from .empunhadura import CONTATO_MM

PONTOS = (0.2, 0.5, 0.8)  # onde cada falange é medida (frações do comprimento), da base para a ponta
GRADE_GRAUS = 10.0
PASSO_INICIAL, PASSO_FINAL = 4.0, 0.25
PESO_FACE_MM = 12.0
PESO_EIXO_MM = 30.0
PESO_CURVA_MM = 0.6  # por grau de PIP + DIP além de reto (a curva total, com o repouso)
PESO_ARMA = 6.0
PESO_LONGE = 6.0
RAIO_PASSO_MM, RAIO_PASSOS = 0.5, 8
FERROLHO_MARGEM_MM = 1.0  # a seção média do dedo (o `raio`) não cobre o lado mais largo dele


def _pontos(cadeia, ms):
    """Os pontos do eixo das três falanges (PONTOS de cada uma), da proximal à distal."""
    return [m @ Vector((0.0, c * t, 0.0)) for m, c in zip(ms, cadeia.comp) for t in PONTOS]


def _distancia(arma, q):
    co, n, _i, d = arma.bvh.find_nearest(q)
    return (-d if (q - co).dot(n) < 0.0 else d), n


def indexar(na, mao, m, dedo, face, eixo, raio, abertura, evitar=None, longe=None, acima=None):
    """O dedo `dedo` deitado reto na arma de `na`, na face `face` e ao longo do `eixo` (unitários, no referencial da
    arma), com o eixo das falanges a `raio` mm da superfície; `evitar` = (peça, folga em mm) — o ferrolho — e `longe` =
    (peça, folga em mm) — o gatilho — ficam a pelo menos a folga, e com `acima` = (altura, margem em mm) — o alto do
    gatilho —, o eixo da falange média e da distal fica a pelo menos a margem acima da altura (o z da arma). Devolve
    (pose, relatório: os graus, a curva, os trechos colados na malha, o desvio do eixo, as folgas e a altura)."""
    lim = EA.limites_do_dedo(mao, abertura)
    rep = mao.rep
    cadeia = EA.CadeiaDedo(na, dedo, m.pose())
    dedo_v = na.vertices(cadeia.ossos)

    def custo_de(g, r):
        ms = cadeia.matrizes(g)
        c = 0.0
        pontos = _pontos(cadeia, ms)
        if acima is not None:
            for q in pontos[len(PONTOS):]:
                falta = acima[0] + acima[1] - q.z
                if falta > 0.0:
                    c += (PESO_LONGE * falta) ** 2
        for q in pontos:
            d, n = _distancia(na.arma, q)
            f = d - r
            c += f * f + (PESO_FACE_MM * (1.0 - n.dot(face))) ** 2
            if f < 0.0:
                c += (PESO_ARMA * f) ** 2
            for peca in (evitar, longe):
                if peca is not None:
                    falta = peca[1] + r + FERROLHO_MARGEM_MM - _distancia(peca[0], q)[0]
                    if falta > 0.0:
                        c += (PESO_LONGE * falta) ** 2
        for k in range(3):
            direcao = (ms[k].to_3x3() @ Vector((0.0, 1.0, 0.0))).normalized()
            c += (PESO_EIXO_MM * (1.0 - direcao.dot(eixo))) ** 2
        curva = abs(g['pip'] + rep['pip']) + abs(g['dip'] + rep['dip'])
        return c + (PESO_CURVA_MM * curva) ** 2

    def valores(a, b):
        n = max(1, math.ceil((b - a) / GRADE_GRAUS))
        return [a + (b - a) * k / n for k in range(n + 1)]

    def buscar(r, inicio=None):
        if inicio is None:
            inicio = min((dict(zip(EA.GRAUS_DO_DEDO, comb))
                          for comb in itertools.product(*(valores(*lim[k]) for k in EA.GRAUS_DO_DEDO))),
                         key=lambda g: custo_de(g, r))
        melhor, custo, passo = dict(inicio), custo_de(inicio, r), PASSO_INICIAL
        while passo >= PASSO_FINAL:
            melhorou = False
            for grau in EA.GRAUS_DO_DEDO:
                for s in (1.0, -1.0):
                    g = dict(melhor)
                    g[grau] = min(max(g[grau] + s * passo, lim[grau][0]), lim[grau][1])
                    c = custo_de(g, r)
                    if c < custo - 1e-9:
                        melhor, custo, melhorou = g, c, True
            if not melhorou:
                passo /= 2
        return melhor

    # a malha: as cápsulas do raio médio deixam a luva entrar nas quinas da armação; o raio cresce até ela soltar
    g = buscar(raio)
    for passo in range(1, RAIO_PASSOS + 1):
        if na.penetracao(na.pontos(EA._com_dedo(m, dedo, g).pose()), dedo_v) <= CONTATO_MM * 0.3:
            break
        g = buscar(raio + passo * RAIO_PASSO_MM, g)
    m = EA._com_dedo(m, dedo, g)
    pts = na.pontos(m.pose())
    ms = cadeia.matrizes(g)
    desvio = max(math.degrees(math.acos(max(-1.0, min(1.0, (ms[k].to_3x3() @ Vector((0.0, 1.0, 0.0))).normalized()
                                                         .dot(eixo))))) for k in range(3))
    rel = {'graus': {k: round(v, 2) for k, v in g.items()},
           'curvaGraus': round(abs(g['pip'] + rep['pip']) + abs(g['dip'] + rep['dip']), 1),
           'trechosMM': _trechos(na, cadeia, pts), 'desvioDoEixoGraus': round(desvio, 1)}
    for nome, peca in (('folgaFerrolhoMM', evitar), ('folgaGatilhoMM', longe)):
        if peca is not None:
            rel[nome] = round(min(peca[0].distancia(Vector(pts[i])) for i in dedo_v), 2)
    if acima is not None:
        rel['acimaDoGatilhoMM'] = round(min(q.z for q in _pontos(cadeia, ms)[len(PONTOS):]) - acima[0], 2)
    return m, rel


def _trechos(na, cadeia, pts):
    """A folga (mm) do dedo deitado medida na malha: em três trechos de cada falange (a base, o meio e a ponta, pela
    posição de repouso dos vértices ao longo do osso), a menor distância dos vértices do trecho à arma."""
    col = na.col
    rig, lado = col.rig, col.lado
    repouso = col.modelo.pontos({})
    trechos = []
    for osso in cadeia.ossos:
        b = rig.data.bones[f'{osso}_{lado}']
        cabeca = Vector(b.head_local) / EA.S
        eixo = Vector(b.tail_local) / EA.S - cabeca
        comp2 = eixo.length_squared
        indices = [i for i, dono in enumerate(col.dono) if dono == osso]
        for a, z in ((0.0, 1.0 / 3.0), (1.0 / 3.0, 2.0 / 3.0), (2.0 / 3.0, 1.01)):
            trecho = [i for i in indices if a <= (Vector(repouso[i]) - cabeca).dot(eixo) / comp2 < z]
            if trecho:
                trechos.append(round(min(na.arma.distancia(Vector(pts[i])) for i in trecho), 2))
    return trechos


def problemas(rel, curva_graus, folga_mm, eixo_graus, gatilho_mm, ferrolho_mm, acima_mm, contato_mm):
    """Os problemas do dedo indexado (o relatório de `indexar`), com os limites de LIMITES_DA_PEGA (src/data/luvas.js) —
    a mesma conta do Node (tools/blender/saidaPega.mjs, problemasDoIndexado)."""
    t = rel['trechosMM']
    falanges = ('proximal', 'média', 'distal')
    saida = []
    if rel['curvaGraus'] > curva_graus:
        saida.append(f"o indicador indexado com {rel['curvaGraus']}° de curva (a PIP mais a DIP; máximo {curva_graus}°): "
                     'tem de ficar reto, deitado na armação')
    for i, v in enumerate(t):
        if v > folga_mm:
            saida.append(f'a falange {falanges[i // 3]} do indicador indexado a {v:.2f} mm da armação (máximo {folga_mm} mm)')
    if min(t[6:]) > contato_mm:
        saida.append(f'a falange distal do indicador indexado não encosta na armação ({min(t[6:]):.2f} mm; máximo '
                     f'{contato_mm} mm)')
    if rel['desvioDoEixoGraus'] > eixo_graus:
        saida.append(f"o indicador indexado a {rel['desvioDoEixoGraus']}° da frente da arma (máximo {eixo_graus}°)")
    if rel['folgaGatilhoMM'] < gatilho_mm:
        saida.append(f"o indicador indexado a {rel['folgaGatilhoMM']:.2f} mm do gatilho (mínimo {gatilho_mm} mm: fora do "
                     'guarda-mato)')
    if rel['folgaFerrolhoMM'] < ferrolho_mm:
        saida.append(f"o indicador indexado a {rel['folgaFerrolhoMM']:.2f} mm do ferrolho (mínimo {ferrolho_mm} mm)")
    if rel['acimaDoGatilhoMM'] < acima_mm:
        saida.append(f"o indicador indexado a {rel['acimaDoGatilhoMM']:.2f} mm do alto do gatilho (mínimo {acima_mm} mm: "
                     'acima do guarda-mato, na lateral da armação)')
    return saida
