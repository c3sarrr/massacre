# A pega de uma arma realista (Fase 4.1b; desenho em docs/superpowers/specs/2026-09-26-4.1b-luvas-e-empunhadura-
# design.md, seções 6.1 a 6.4; plano, Tarefa 7 e D1–D5): o solver de empunhadura dentro do construir da arma.
#  - as luvas: a luva de jogo direita com o rig, montada pelo mesmo caminho do alvo `luvas` (luvas.montar_jogo), e a
#    esquerda espelhada dela — as duas com a marca do rig (D4) que o luvas.glb traz;
#  - cada mão, pela regra da categoria (empunhadura_regras.py) com as correções da arma: a luva entra no soquete da mão
#    (a âncora, as giradas, a diagonal) e chega pela normal da palma até encostar (empunhadura_arma.encostar), com a CMC
#    do polegar na pose de pegar; os dedos da regra fecham em volta da arma (empunhadura_arma.agarrar) e os vizinhos se
#    separam (e, na mão da frente, se juntam lado a lado: empunhadura_arma.juntar_dedos); o indicador vai ao gatilho
#    (empunhadura_arma.dedo_no_alvo); o polegar pousa do lado da regra (empunhadura_polegar.alvo_na_arma e
#    fechar_no_alvo) ou, na mão da frente, deitado reto na face do lado dele e apontando para a boca
#    (empunhadura_polegar_deitado.deitar_na_arma);
#  - a palma que cede (4.1c, Tarefa 11; maos_palma.py): nas buscas, cada vértice da palma entra na arma até o que ele
#    cede (empunhadura_arma.NaArma); resolvidas as mãos, a palma afunda até a superfície (empunhadura_palma.afundamento:
#    a da mão do gatilho primeiro, a de apoio com a luva do gatilho já afundada de obstáculo);
#  - a validação (seção 6.3, bloqueia a exportação; empunhadura_validacao.py): nenhum vértice da luva a mais de 0,3 mm
#    dentro da arma, na malha afundada; a palma (com a tenar e a hipotenar), cada dedo da regra, a polpa do indicador
#    (no gatilho) e a do polegar a no máximo 1 mm da arma; a luva sem se atravessar e sem afinar nas juntas; os ângulos
#    dentro dos limites da ficha; na mão da frente (regra do usuário de 2026-09-27), só o polegar de um lado e os quatro
#    dedos do outro e o polegar reto e deitado na arma; os dedos que abraçam a arma lado a lado, sem leque; na pistola,
#    a luva com a luva, os polegares longe do ferrolho e para a frente, e o indicador indexado;
#  - as sondas (o `luvas_contato` do jogo mede nelas): o vértice de cada contato mais perto da arma e a distância dele;
#  - a saída (seção 6.4): o nó `pega` com a marca, as sondas, as mãos da regra (`maos`: as duas, ou só a direita na
#    faca — 4.1c) e o afundamento da palma de cada mão (`palma`: os vértices e os deslocamentos, mm no referencial do
#    braço com o osso `mao` em repouso, no do Blender) nos extras, os nós `pega_mao_d`/`pega_mao_e` das mãos da regra (o referencial do osso `mao` de cada
#    braço na pose, no da arma) e a armadura `pega_luvas` (os braços da regra) com a ação `empunhadura` de um quadro nas
#    rotações dos 17 ossos de dedo de cada mão (D1: a animação glTF).
# Unidades: mm e graus além do repouso (os totais no relatório); o Blender em metros.
import json
import time

import bpy
from mathutils import Matrix, Quaternion, Vector
from mathutils.bvhtree import BVHTree

from . import (empunhadura, empunhadura_arma as EA, empunhadura_dedo as dedo_indexado, empunhadura_palma as palma,
               empunhadura_polegar as polegar, empunhadura_polegar_deitado as polegar_deitado,
               empunhadura_regras as regras, empunhadura_validacao as validacao, luvas, maos, maos_rig, materiais,
               validar_maos)
from .maos import DEDOS4
from .maos_capsulas import mm
from .empunhadura_validacao import INDEXADO_ACIMA_MM, INDEXADO_GATILHO_MM
from .unidades import S

# as chegadas da palma quando o polegar deitado cruza a arma (resolver): a primeira na pose de pegar, as outras com a CMC
# da solução anterior, recuando estes mm pela normal da palma depois de encostar
RECUOS_DA_PALMA = (0.0, 0.0, 0.25, 0.5, 0.75, 1.0)
# para onde o polegar do gatilho da pistola espera erguido (no referencial da arma): para cima, pendendo para a direita
ESPERA_DO_POLEGAR = (0.0, -0.4, 1.0)
# os ossos de dedo da pega (seção 6.4: 17 por mão)
OSSOS_DE_DEDO = (('polegar_1', 'polegar_2', 'polegar_3')
                 + tuple(f'{d}_{i}' for d in ('indicador', 'medio') for i in (1, 2, 3))
                 + tuple(f'{d}_{i}' for d in ('anelar', 'minimo') for i in (0, 1, 2, 3)))
LADOS = (('d', 'direita'), ('e', 'esquerda'))


def montar_luvas(ctx, colecao):
    """As duas luvas de jogo com o rig (sem assar nem UV), na coleção, fora do render. Devolve (mao, {lado: (luva,
    rig)})."""
    mao = maos.Mao(ctx['luvas']['ficha'])
    M = materiais.materiais_das_luvas(ctx['luvas']['pinturas']['massaCrua'])
    luva, rig, _residuo = luvas.montar_jogo(mao, M, colecao)
    luva_e, rig_e = maos_rig.espelhar(luva, rig, mao, colecao)
    for ob in (luva, luva_e):
        ob.hide_render = True
    return mao, {'d': (luva, rig), 'e': (luva_e, rig_e)}


def _centro_da_palma(col):
    """O ponto da superfície da palma no meio da mão de repouso: do meio do osso `mao` para a palma (−Z da luva)."""
    pts = col.modelo.pontos({})
    bvh = BVHTree.FromPolygons([tuple(p) for p in pts], col.tris)
    co, _n, _i, _d = bvh.ray_cast((col.cabeca['mao'] + col.cabeca['medio_1']) / 2, Vector((0.0, 0.0, -1.0)))
    return co


def ponto_do_gatilho(gatilho, altura):
    """(ponto, normal) da face da frente do gatilho a `altura` dele (a fração de cima para baixo), no plano do meio da
    arma (mm): o raio que vem da frente acerta a face em que o dedo apoia."""
    pts = [(gatilho.matrix_world @ v.co) / S for v in gatilho.data.vertices]
    topo, fundo = max(p.z for p in pts), min(p.z for p in pts)
    frente = max(p.x for p in pts) + 20.0
    ponto, normal = EA.Arma([gatilho]).raio(Vector((frente, 0.0, topo - altura * (topo - fundo))), Vector((-1.0, 0.0, 0.0)))
    if ponto is None:
        raise RuntimeError('o raio do gatilho não acertou a face da frente dele')
    return ponto, normal


def topo_do_gatilho(gatilho):
    """A altura (mm, o z da arma) do alto do gatilho: a borda de baixo da armação em volta dele, de onde ele sai."""
    return max((gatilho.matrix_world @ v.co).z for v in gatilho.data.vertices) / S


def _vertices_do_corpo(col):
    """Os vértices que chegam na arma com a palma: a luva sem os dedos e sem as falanges do polegar."""
    livres = {f'{d}_{i}' for d in DEDOS4 for i in (1, 2, 3)} | set(polegar.LIVRE)
    return [i for i, o in enumerate(col.dono) if o not in livres]


def _pegar(col, na, mao, r, soquete, gatilho, base, lado, cmc=None, polegar_inicio=None, evitar=None, recuo=0.0,
           sobre=None):
    """Uma mão na arma pela regra `r` (ver o cabeçalho), com a CMC do polegar na chegada nos graus `cmc` (a abdução, a
    flexão e a rotação além do repouso; sem eles, a pose de pegar) e o polegar deitado partindo de `polegar_inicio` (os
    graus da solução da primeira chegada) e longe da peça de `evitar` (o ferrolho da pistola: (peça, folga em mm)), com a
    palma recuando `recuo` mm pela normal dela depois de encostar; o polegar deitado medido até `sobre` (a arma sem a
    outra luva: o de apoio da pistola, na armação), se vier. O
    polegar `sobre_luva` (o do gatilho da pistola) deita aqui na arma, provisório, e de novo no fim, com a luva da outra
    mão de obstáculo (resolver). Devolve (pose, relatório do solver)."""
    rel = {}
    lim = polegar.limites(mao)
    m = EA.mao_aberta(mao, polegar.afastar(col, mao, empunhadura.Mao()))
    chegada = {'abducao': lim['abducao'][1], 'cmc': lim['cmc'][1], 'rotacao': 0.0, 'mcp': lim['mcp'][0],
               'ip': lim['ip'][0], 'desvio': 0.0}
    espera = r['polegar'].get('espera') if r['polegar'].get('sobre_luva') or r['polegar'].get('cmc_fixa') else None
    if isinstance(espera, dict) and cmc is None:
        # o polegar do gatilho da pistola esperando numa pose da regra: a palma chega com a CMC dela (a pele da palma
        # e da tenar muda com a CMC; chegando com a da pega, ela entrava ~1,4 mm no punho na pose da espera)
        cmc = {k: espera[k] for k in ('abducao', 'cmc', 'rotacao')}
    if r.get('polegar_afastado'):
        # a palma chata no lado do punho (a mão de apoio da pistola): o polegar afastado no plano da palma, como no
        # começo do punho fechado (empunhadura_polegar.afastar) — na pose de pegar, a tenar fazia um calombo de 20 mm
        # para o lado da palma e encostava sozinha no punho, com a palma longe dele
        chegada.update({'abducao': lim['abducao'][0], 'cmc': lim['cmc'][0]})
    chegada.update(cmc or {})
    m = polegar._com_graus(m, polegar.Cadeia(col, mao, {}), chegada)
    R = regras.rotacao(r, soquete.matrix_world, lado)
    anc = r['ancora']
    ponto_da_luva = col.cabeca['indicador_1'] if anc['ponto'] == 'mcp_indicador' else _centro_da_palma(col)
    alvo_g = normal_g = None
    if r['gatilho'] or anc['de'] == 'gatilho':
        # o ponto do gatilho: o alvo da polpa, ou só a referência da âncora (o indicador indexado da pistola)
        alvo_g, normal_g = ponto_do_gatilho(gatilho, r['gatilho']['altura'] if r['gatilho'] else anc['altura'])
    origem = alvo_g if anc['de'] == 'gatilho' else soquete.matrix_world.translation / S
    na.encaixe = Matrix.Translation(origem + Vector(anc['mm']) - R @ ponto_da_luva) @ R.to_4x4()
    palma = (R @ Vector((0.0, 0.0, -1.0))).normalized()
    # a palma que aperta (`aperto` na regra: as duas mãos da pistola) chega afundando até o que cada vértice cede; nas
    # outras ela chega só encostando e cede depois, onde os dedos e o polegar a puxam para a arma (as buscas com `na`)
    na_chegada = na if r.get('aperto') else EA.NaArma(col, na.arma, na.encaixe, ceder=False)
    na.encaixe, andou = EA.encostar(na_chegada, m, palma, na.encaixe, _vertices_do_corpo(col), *r['chegada'])
    if recuo:
        # a palma recua pela normal dela (a nova chegada que ainda prendia a membrana: resolver)
        na.encaixe = Matrix.Translation(-palma * recuo) @ na.encaixe
        andou -= recuo
    rel['palmaAndouMM'] = round(andou, 2)
    parou = {}
    aberta = m
    for d in r['dedos']:
        m, p = EA.agarrar(na, mao, m, d)
        parou.update(p)
    m, vizinhos = empunhadura.separar_vizinhos(col, m, [d for d in DEDOS4 if d in r['dedos']])
    rel.update({'dedosPararam': parou, 'vizinhos': vizinhos})
    if r.get('juntar'):
        topo = validar_maos.Topologia(col.luva, luvas.REFORCO)
        m, rel['juntar'] = EA.juntar_dedos(col, na, mao, m, aberta, r['dedos'],
                                           lambda pts: validar_maos.atravessa(pts, topo)[0])
    if r['gatilho']:
        g = r['gatilho']
        guarda = na.vertices(['indicador_2', 'indicador_3'])

        def folga(pts):
            return min(base.distancia(pts[i]) for i in guarda) - g['folga']

        # a folga negativa é o aperto da luva no vão (empunhadura_regras, a M4A4): só no resto da arma, não no gatilho
        m, rel['indicador'], _cadeia = EA.dedo_no_alvo(na, mao, m, 'indicador', alvo_g, normal_g, g['abertura'],
                                                       g['raio'], folga, aperto=max(0.0, -g['folga']),
                                                       alvo_arma=EA.Arma([gatilho]))
        rel['indicador']['folgaDoResto'] = round(folga(na.pontos(m.pose())) + g['folga'], 2)
    if r.get('indexado'):
        # o indicador indexado na lateral da armação (a pistola): longe do ferrolho, fora do guarda-mato e acima dele (o
        # eixo da falange média e da distal acima do alto do gatilho, onde a armação desce até o guarda-mato)
        x = r['indexado']
        m, rel['indicador'] = dedo_indexado.indexar(
            na, mao, m, x['dedo'], Vector(x['face']).normalized(), Vector(x['eixo']).normalized(), x['raio'],
            x['abertura'], evitar, (EA.Arma([gatilho]), INDEXADO_GATILHO_MM),
            (topo_do_gatilho(gatilho), INDEXADO_ACIMA_MM))
    cadeia = polegar.Cadeia(col, mao, {o: q for o, q in m.pose().items() if not o.startswith('polegar')})
    p = r['polegar']
    if p.get('sobre_luva') and isinstance(p.get('espera'), dict):
        # o polegar do gatilho da pistola espera na pose da regra (os graus além do repouso), por cima de onde a mão de
        # apoio encaixa; deita por último, por cima dela (resolver)
        cadeia_p = polegar.Cadeia(col, mao, {o: q for o, q in m.pose().items() if not o.startswith('polegar')})
        espera = {'desvio': 0.0, **p['espera']}
        m = polegar._com_graus(m, cadeia_p, espera)
        rel['polegar'] = {'espera': polegar.totais(mao, espera)}
    elif p.get('sobre_luva') and p.get('espera') == 'erguido':
        # o polegar do gatilho da pistola espera erguido, fora do caminho (empunhadura_polegar_deitado.erguer: para cima, o +Z
        # da arma, pendendo para o lado da mão dele — só para cima, a ponta mais alta pendia para o lado esquerdo, por
        # onde a mão de apoio chega, e ela começava a chegada dentro dele), enquanto a mão de apoio encaixa embaixo
        # dele; deita por último, por cima do polegar de apoio
        # (resolver). É a sequência de ensinar a pega (American Shooting Journal, "Thumbs Up… Er, Forward!": a mão do
        # gatilho com o polegar para cima, a de apoio encaixada com o polegar ao longo da armação, e o do gatilho
        # descendo sobre ele): deitado aqui na armação, provisório, ele ocupava o lugar do de apoio
        m, graus = polegar_deitado.erguer(col, mao, m, na, Vector(ESPERA_DO_POLEGAR).normalized())
        rel['polegar'] = {'espera': polegar.totais(mao, graus)}
    elif p.get('deitado'):
        # com `cmc_fixa`, a CMC da espera (com que a palma chegou) fica parada também aqui
        fixos = ({k: espera[k] for k in ('abducao', 'cmc', 'rotacao')}
                 if p.get('cmc_fixa') and isinstance(espera, dict) else None)
        m, rel['polegar'] = _deitar(col, na, mao, m, p, polegar_inicio, evitar, sobre, fixos)
    elif p.get('sobre'):
        # o polegar dobrado por cima dos dedos de `sobre` (a faca: a falange média do indicador), como no punho fechado
        # das poses de teste: a polpa assenta nas falanges deles (a superfície do fechar_no_alvo), e a arma é obstáculo
        alvo_p, normal_p = polegar.alvo_nas_falanges(col, m.pose(), p['sobre'])
        dedos_sobre = sorted({polegar.dedo_do_alvo(k) for k in p['sobre']})
        superficie = col.triangulos({f'{d}_{i}' for d in dedos_sobre for i in (1, 2, 3)})
        try:
            m, rel['polegar'] = polegar.fechar_no_alvo(col, mao, m, alvo_p, normal_p, superficie, arma=na)
        except RuntimeError as erro:
            # a validação reprova (o polegar sem assentar) e a .blend fica salva para as vistas de perto
            rel['polegar'] = {'erro': str(erro), 'encostou': False, 'polpaEncostaMM': None}
        rel['polegar']['sobre'] = dedos_sobre
    else:
        alvo_p, normal_p = polegar.alvo_na_arma(cadeia, na, m, lim, regras.lado_do_polegar(r), p['peso'])
        m, rel['polegar'] = polegar.fechar_no_alvo(col, mao, m, alvo_p, normal_p, None, na=na)
    return m, rel


def _deitar(col, na, mao, m, p, inicio=None, evitar=None, sobre=None, fixos=None):
    """O polegar deitado reto na arma pela regra `p` (o `polegar` dela: a face, o eixo e o plano), partindo de `inicio`
    e longe da peça de `evitar`; com `sobre`, deitado nessa superfície (o polegar da luva de apoio), e com os graus de
    `fixos` parados. Devolve (pose, relatório de empunhadura_polegar_deitado.deitar_na_arma)."""
    eixo = (na.encaixe.inverted().to_3x3() @ Vector(p['eixo'])).normalized()
    face = Vector(p['face']).normalized()
    medir = None
    if p.get('plano') is not None:
        # a falange proximal medida até o plano da face (o alto do trilho do lado da M4A4: ela passa por cima do vão
        # entre o trilho e o corpo do guarda-mão), e a distal até a malha, em que ela encosta
        def medir(osso, q):
            return face.dot(Vector(q)) - p['plano'] if osso == polegar.LIVRE[0] else na.arma.distancia(q)
    return polegar_deitado.deitar_na_arma(col, mao, m, na, eixo, face, inicio, medir, evitar, sobre, fixos)


def _luva_na_arma(col, na, pose, sem=(), so=None):
    """(pontos em mm no referencial da arma, triângulos) da luva na pose, no encaixe dela: a outra luva como
    obstáculo (EA.Arma, `extra`), sem os triângulos dos ossos de `sem` (ou só os dos ossos de `so`)."""
    tris = [t for t, dono in zip(col.tris, col.dono_tri) if dono not in sem and (so is None or dono in so)]
    return na.pontos(pose), tris


def maos_da_regra(r_cat):
    """As mãos (lado, nome) que a regra da categoria tem: as duas, ou só a direita na faca (4.1c)."""
    maos_ = [(lado, nome) for lado, nome in LADOS if nome in r_cat]
    if not maos_ or maos_[0][0] != 'd':
        raise ValueError('a regra de empunhadura precisa da mão direita (a do gatilho ou a da faca)')
    return maos_


def _uma_mao(contexto, lado, r, feitas, chegada=None, recuo_chegada=0.0):
    """Uma mão da regra na arma, com a outra luva já posada de obstáculo se a regra pede (`luva`); com `chegada` (os
    graus do polegar `sobre_luva` que não deitou), a palma chega com a CMC deles e recua `recuo_chegada` mm. Devolve o
    registro da mão (a regra, o colisor, o encaixe, a pose, o relatório e a peça de evitar)."""
    mao, bracos, objetos, arma, base, soq, perto = contexto
    luva, rig = bracos[lado]
    col = empunhadura.Colisor(luva, rig, mao, luvas.REFORCO)
    obstaculo = arma
    if r.get('luva'):
        # luva com luva (a mão de apoio da pistola): a luva da outra mão posada é obstáculo — sem as falanges do
        # polegar dela que deita por último por cima desta (`sobre_luva`): na pega de verdade ele está erguido enquanto
        # a mão de apoio entra e só depois deita sobre o polegar dela (a sequência das fotos da ASJ, "Thumbs Up… Er,
        # Forward!"); a tenar e o metacarpo dele ficam no obstáculo
        o = feitas[r['luva']]
        sem = polegar.LIVRE if o['r']['polegar'].get('sobre_luva') else ()
        obstaculo = EA.Arma(objetos, extra=[_luva_na_arma(o['col'], o['na'], o['m'].pose(), sem)])
    na = EA.NaArma(col, obstaculo)
    evitar = (EA.Arma([perto['ferrolho']]), r['ferrolho']) if r.get('ferrolho') else None
    args = (col, na, mao, r, soq[r['soquete']], perto.get('gatilho'), base, lado)
    # o polegar de apoio deita na armação: a folga dele medida só até a arma — contra a luva do gatilho sem as falanges
    # do polegar (aberta onde elas saem), o sinal da distância errava e a base dele saía 17 mm "dentro"
    sobre = arma if r.get('luva') else None
    # o polegar deitado que entra na arma mesmo aberto (a mão da frente da M4A4, no canto de baixo do guarda-mão
    # largo; o polegar de apoio da pistola): a palma encostou com a CMC na pose de pegar, e a da solução levava a pele
    # da tenar para dentro. Ela chega de novo com a CMC da solução, como a da faca. Se ainda cruzar (a membrana presa nas
    # quinas, 0,15 e 0,4 mm), a palma chega de novo e recua RECUOS_DA_PALMA mm pela normal dela, até soltar
    graus = chegada
    for tentativa, recuo in enumerate(RECUOS_DA_PALMA):
        try:
            if graus is None:
                m, rel_m = _pegar(*args, evitar=evitar, sobre=sobre)
            else:
                m, rel_m = _pegar(*args, cmc={k: graus[k] for k in ('abducao', 'cmc', 'rotacao')},
                                  polegar_inicio=graus, evitar=evitar,
                                  recuo=recuo_chegada if graus is chegada else recuo, sobre=sobre)
            break
        except empunhadura.PolegarCruza as erro:
            if tentativa == len(RECUOS_DA_PALMA) - 1:
                raise
            graus = erro.graus
    if r['polegar'].get('sobre') and 'erro' not in rel_m['polegar']:
        # a segunda chegada (a faca): a palma chega de novo com a CMC do polegar da solução. Na pose de pegar, a
        # tenar encostava no cabo antes da palma, e a abdução da solução depois a tirava dele (a palma a 2,4 mm)
        # ou a punha dentro (0,7 mm)
        g = polegar.graus_da_pose(m, polegar.Cadeia(col, mao, {}))
        m, rel_m = _pegar(*args, cmc={k: g[k] for k in ('abducao', 'cmc', 'rotacao')})
    return {'r': r, 'col': col, 'na': na, 'm': m, 'rel': rel_m, 'evitar': evitar}


def _deitar_por_cima(feitas, mao, objetos, inicio=None):
    """O polegar `sobre_luva` (o do gatilho da pistola), por último: deitado de novo por cima do polegar de apoio,
    com a luva da outra mão inteira de obstáculo. As partidas, em ordem: `inicio` (os graus da solução de antes, com
    que a palma chegou de novo), o provisório deitado na armação (um refino: ele assenta no de apoio, que deitou embaixo
    dele) e a grade inteira dos cinco graus (a única, se ele esperava erguido, longe de onde deita). Devolve o
    PolegarCruza da última se nenhuma deita (fica o provisório, e a validação reprova), senão None."""
    for f in feitas.values():
        sobre = f['r']['polegar'].get('sobre_luva')
        if not sobre:
            continue
        o = feitas[sobre]
        na_luva = EA.NaArma(f['col'], EA.Arma(objetos, extra=[_luva_na_arma(o['col'], o['na'], o['m'].pose())]),
                            f['na'].encaixe)
        # ele deita sobre o polegar de apoio (o metacarpo e as falanges da outra luva), não na armação embaixo dele: a
        # ASJ ("Thumbs Up… Er, Forward!") — o polegar de apoio ao longo do ferrolho, apontando para a frente, e o do
        # gatilho descendo sobre ele até os dois apontarem para a frente. Medida até a arma e a luva, a folga deixava
        # ele deitar na armação, embaixo do de apoio
        sobre_polegar = EA.Arma([], extra=[_luva_na_arma(o['col'], o['na'], o['m'].pose(), so=polegar.OSSOS)])
        # com `cmc_fixa`, a CMC fica a da espera, com que a palma chegou: deitando com outra, a tenar mudava de forma, a
        # nova chegada punha a mão do gatilho em outro lugar e o indicador saía do gatilho (3,6 mm)
        p = f['r']['polegar']
        fixos = ({k: p['espera'][k] for k in ('abducao', 'cmc', 'rotacao')}
                 if p.get('cmc_fixa') and isinstance(p.get('espera'), dict) else None)
        partidas = [inicio] if inicio is not None else []
        if f['r']['polegar'].get('espera') != 'erguido':
            partidas.append(polegar.graus_da_pose(f['m'], polegar.Cadeia(f['col'], mao, {})))
        partidas.append(None)
        for partida in partidas:
            try:
                f['m'], rel_polegar = _deitar(f['col'], na_luva, mao, f['m'], p, partida, f['evitar'], sobre_polegar,
                                              fixos)
            except empunhadura.PolegarCruza as erro:
                ultimo = erro
                continue
            if 'espera' in f['rel']['polegar']:
                rel_polegar['espera'] = f['rel']['polegar']['espera']
            f['rel']['polegar'] = rel_polegar
            f['na'] = na_luva
            break
        else:
            f['rel']['polegar']['erro'] = str(ultimo)
            return ultimo
    return None


def _outra(r):
    """O lado da outra luva com que esta mão conta (a pistola: a de apoio encaixa na do gatilho, o polegar do gatilho
    deita sobre o de apoio), ou None."""
    return r.get('luva') or r['polegar'].get('sobre_luva')


def _luva_posada(f, arma, afundar):
    """(pontos, triângulos) da luva do registro `f` na pose final, com o afundamento da palma dela (ou sem, `None`)."""
    return _luva_na_arma(f['col'], EA.NaArma(f['col'], arma, f['na'].encaixe, ceder=False, afundar=afundar),
                         f['m'].pose())


def resolver(ctx, mao, bracos, perto, soquetes, correcoes):
    """A pega das mãos da regra na arma (as peças do perto, as móveis em repouso). Devolve ({lado: {'encaixe': mm,
    'pose': {osso: quaternion}, 'contatos': ..., 'palma': o afundamento}}, a seção `empunhadura` do relatório, os
    problemas)."""
    t0 = time.time()
    r_cat = regras.regra(ctx['categoria'], correcoes)
    objetos = [o for k, o in perto.items() if not k.startswith('_')]
    arma = EA.Arma(objetos)
    base = EA.Arma([perto['base']])
    soq = {o.name[len('soquete_'):]: o for o in soquetes}
    pega, rel, problemas = {}, {}, []
    maos_ = maos_da_regra(r_cat)
    # a pistola: se o polegar do gatilho não deita por cima do de apoio (a pele da tenar e da palma, que muda com a CMC
    # do polegar, entrava ~1,4 mm no punho da mão girada atrás da arma), a mão do gatilho chega de novo com a CMC da
    # solução, recuando a palma RECUOS_DA_PALMA mm se preciso (como o polegar deitado de uma mão só, em _uma_mao), e a
    # de apoio encaixa de novo nela
    contexto = (mao, bracos, objetos, arma, base, soq, perto)
    graus_sobre, primeira, feitas = None, None, None
    for tentativa, recuo in enumerate(RECUOS_DA_PALMA):
        novas = {}
        try:
            for lado, nome in maos_:
                r = r_cat[nome]
                chegada = graus_sobre if r['polegar'].get('sobre_luva') else None
                novas[lado] = _uma_mao(contexto, lado, r, novas, chegada, recuo)
        except EA.ChegadaCruza:
            if primeira is None:
                raise
            # a palma com a CMC do polegar que não deitou já cruza a arma de onde chega (a abdução dele levava a
            # falange proximal para o ferrolho): para aqui
            break
        erro = _deitar_por_cima(novas, mao, objetos, graus_sobre)
        if erro is None:
            feitas = novas
            break
        primeira = primeira or novas
        if tentativa == len(RECUOS_DA_PALMA) - 1:
            break
        graus_sobre = erro.graus
    if feitas is None:
        # nenhuma chegada deitou o polegar por cima do de apoio: fica a primeira, com o polegar reprovado — as novas
        # chegadas com a CMC dele (a abdução e a rotação no limite) mudavam a tenar e punham a mão do gatilho 15 mm
        # para trás, com o indicador a 10 mm do gatilho
        feitas = primeira
    # a palma que cede: o afundamento de cada mão até a superfície, a do gatilho primeiro e a de apoio com a luva do
    # gatilho já afundada de obstáculo
    afundar = {}
    for lado, _nome in maos_:
        f = feitas[lado]
        outra = _outra(f['r'])
        obstaculo = arma if outra is None else EA.Arma(objetos, extra=[_luva_posada(feitas[outra], arma,
                                                                                    afundar.get(outra))])
        afundar[lado] = palma.afundamento(EA.NaArma(f['col'], obstaculo, f['na'].encaixe), f['m'].pose())
    for lado, nome in maos_:
        f = feitas[lado]
        outra = _outra(f['r'])
        luva_outra = None if outra is None else _luva_posada(feitas[outra], arma, afundar[outra])
        rel[lado], sondas, problemas_mao = validacao.conferir_mao(f, nome, mao, bracos[lado][0], arma, objetos, perto,
                                                                  afundar[lado], luva_outra, outra)
        problemas += problemas_mao
        if f['r'].get('frente'):
            rel['frente'] = lado
        pega[lado] = {'encaixe': f['na'].encaixe.copy(), 'pose': f['m'].pose(), 'contatos': sondas,
                      'palma': {'vertices': afundar[lado]['vertices'], 'vetores': afundar[lado]['vetores']}}
    rel['maos'] = [lado for lado, _n in maos_]
    rel['marca'] = {lado: maos_rig.marca(bracos[lado][1]) for lado, _n in maos_}
    rel['segundos'] = round(time.time() - t0, 1)
    return pega, rel, problemas


def guardar(bracos, pega):
    """A pega de cada braço nos rigs (o encaixe, a pose e o afundamento da palma), para as vistas de perto do conferir
    na .blend."""
    for lado, dados in pega.items():
        bracos[lado][1]['pega'] = json.dumps({'encaixe': [list(r) for r in dados['encaixe']],
                                              'pose': maos_rig.pose_json(dados['pose']), 'palma': dados['palma']})


def luvas_da_blend(ctx):
    """(mao, {lado: (luva, rig)}) das luvas guardadas na .blend da arma (o validar)."""
    return maos.Mao(ctx['luvas']['ficha']), {lado: (bpy.data.objects[f'luva_{lado}'], bpy.data.objects[f'rig_{lado}'])
                                             for lado, _n in LADOS}


def objetos_da_saida(mao, bracos, pega, marca, colecao):
    """Os objetos da pega no .glb da arma (ver o cabeçalho), em metros no referencial do Blender: o vazio `pega` (os
    extras: a marca, as sondas, as mãos e o afundamento da palma), os vazios `pega_mao_*` e a armadura `pega_luvas` (as mãos da pega) com a ação
    `empunhadura`. Devolve [pega, pega_mao_d, (pega_mao_e,) pega_luvas]."""
    lados = [(lado, nome) for lado, nome in LADOS if lado in pega]
    raiz = bpy.data.objects.new('pega', None)
    colecao.objects.link(raiz)
    sondas = {lado: {k: {'vertice': v[0], 'mm': v[1]} for k, v in pega[lado]['contatos'].items()} for lado in pega}
    raiz['luvas'] = json.dumps({'marca': {lado: marca[lado] for lado, _n in lados}, 'sondas': sondas,
                                'maos': [lado for lado, _n in lados],
                                'palma': {lado: pega[lado]['palma'] for lado, _n in lados}}, separators=(',', ':'))
    objetos = [raiz]
    for lado, _nome in lados:
        rig = bracos[lado][1]
        m = pega[lado]['encaixe'] @ mm(rig.data.bones[f'mao_{lado}'].matrix_local)
        m.translation = m.translation * S
        ob = bpy.data.objects.new(f'pega_mao_{lado}', None)
        colecao.objects.link(ob)
        ob.matrix_world = m
        objetos.append(ob)
    armaduras = [maos_rig.armadura(mao, colecao, lado) for lado, _n in lados]
    if len(armaduras) > 1:
        bpy.ops.object.select_all(action='DESELECT')
        with bpy.context.temp_override(active_object=armaduras[0], selected_editable_objects=armaduras,
                                       selected_objects=armaduras):
            bpy.ops.object.join()
    arm = armaduras[0]
    arm.name = arm.data.name = 'pega_luvas'
    acao = bpy.data.actions.new('empunhadura')
    arm.animation_data_create()
    arm.animation_data.action = acao
    for lado, _nome in lados:
        for osso in OSSOS_DE_DEDO:
            pb = arm.pose.bones[f'{osso}_{lado}']
            pb.rotation_mode = 'QUATERNION'
            pb.rotation_quaternion = pega[lado]['pose'].get(osso, Quaternion())
            pb.keyframe_insert('rotation_quaternion', frame=1)
    objetos.append(arm)
    return objetos
