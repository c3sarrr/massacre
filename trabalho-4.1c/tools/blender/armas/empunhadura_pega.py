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
#    (empunhadura_polegar.deitar_na_arma);
#  - a validação (seção 6.3, bloqueia a exportação): nenhum vértice da luva a mais de 0,3 mm dentro da arma; a palma
#    (com a tenar e a hipotenar), cada dedo da regra, a polpa do indicador (no gatilho) e a do polegar a no máximo 1 mm
#    da arma; a luva sem se atravessar e sem afinar nas juntas (validar_maos.conferir_uma, os limites das poses de
#    teste); os ângulos dentro dos limites da ficha; na mão da frente (regra do usuário de 2026-09-27), só o polegar de
#    um lado e os quatro dedos do outro (_lados: a polpa de cada um a pelo menos LADO_MM do plano do meio da arma, do
#    lado certo) e o polegar reto e deitado na arma (_polegar_deitado: a curva, a distal encostando, a proximal perto);
#    os dedos que abraçam a arma lado a lado, sem leque (a falange média de cada um a no máximo JUNTOS_MM da do vizinho,
#    empunhadura_arma.folgas_entre_dedos; a mão da frente os junta, empunhadura_arma.juntar_dedos);
#  - as sondas (o `luvas_contato` do jogo mede nelas): o vértice de cada contato mais perto da arma e a distância dele;
#  - a saída (seção 6.4): o nó `pega` com a marca, as sondas e as mãos da regra nos extras (`maos`: as duas, ou só a
#    direita na faca — 4.1c), os nós `pega_mao_d`/`pega_mao_e` das mãos da regra (o referencial do osso `mao` de cada
#    braço na pose, no da arma) e a armadura `pega_luvas` (os braços da regra) com a ação `empunhadura` de um quadro nas
#    rotações dos 17 ossos de dedo de cada mão (D1: a animação glTF).
# Unidades: mm e graus além do repouso (os totais no relatório); o Blender em metros.
import json
import time

import bpy
from mathutils import Matrix, Quaternion, Vector
from mathutils.bvhtree import BVHTree

from . import (empunhadura, empunhadura_arma as EA, empunhadura_polegar as polegar, empunhadura_regras as regras,
               luvas, maos, maos_rig, materiais, validar_maos)
from .maos import DEDOS4
from .maos_capsulas import mm
from .unidades import S

PENETRACAO_MM = 0.3
CONTATO_MM = 1.0
LADO_MM = 5.0  # o `ladoMM` de LIMITES_DA_PEGA (src/data/luvas.js): a polpa a pelo menos isto do meio, do lado certo
POLEGAR_CURVA_GRAUS = 20.0  # o `polegarCurvaGraus`: a MCP mais a IP do polegar deitado da mão da frente
POLEGAR_FOLGA_MM = 8.0  # o `polegarFolgaMM`: nenhum trecho do polegar deitado mais longe que isto da arma
# o `dedosJuntosMM`: a falange média de cada dedo que abraça a arma a no máximo isto da do vizinho — menos da metade da
# largura dela (17 a 19 mm na ficha); o leque da mão da frente antes de juntar_dedos chegava a 8,5 mm, a mão do gatilho
# fica em 2,5 e 3,3 mm
JUNTOS_MM = 8.0
# os ossos de dedo da pega (seção 6.4: 17 por mão)
OSSOS_DE_DEDO = (('polegar_1', 'polegar_2', 'polegar_3')
                 + tuple(f'{d}_{i}' for d in ('indicador', 'medio') for i in (1, 2, 3))
                 + tuple(f'{d}_{i}' for d in ('anelar', 'minimo') for i in (0, 1, 2, 3)))
LADOS = (('d', 'direita'), ('e', 'esquerda'))
PALMA = ('mao', 'polegar_1', 'anelar_0', 'minimo_0')


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


def _vertices_do_corpo(col):
    """Os vértices que chegam na arma com a palma: a luva sem os dedos e sem as falanges do polegar."""
    livres = {f'{d}_{i}' for d in DEDOS4 for i in (1, 2, 3)} | set(polegar.LIVRE)
    return [i for i, o in enumerate(col.dono) if o not in livres]


def _pegar(col, na, mao, r, soquete, gatilho, base, lado):
    """Uma mão na arma pela regra `r` (ver o cabeçalho). Devolve (pose, relatório do solver)."""
    rel = {}
    lim = polegar.limites(mao)
    m = EA.mao_aberta(mao, polegar.afastar(col, mao, empunhadura.Mao()))
    m = polegar._com_graus(m, polegar.Cadeia(col, mao, {}),
                           {'abducao': lim['abducao'][1], 'cmc': lim['cmc'][1], 'rotacao': 0.0, 'mcp': lim['mcp'][0],
                            'ip': lim['ip'][0]})
    R = regras.rotacao(r, soquete.matrix_world, lado)
    anc = r['ancora']
    ponto_da_luva = col.cabeca['indicador_1'] if anc['ponto'] == 'mcp_indicador' else _centro_da_palma(col)
    alvo_g = normal_g = None
    if r['gatilho']:
        alvo_g, normal_g = ponto_do_gatilho(gatilho, r['gatilho']['altura'])
    origem = alvo_g if anc['de'] == 'gatilho' else soquete.matrix_world.translation / S
    na.encaixe = Matrix.Translation(origem + Vector(anc['mm']) - R @ ponto_da_luva) @ R.to_4x4()
    palma = (R @ Vector((0.0, 0.0, -1.0))).normalized()
    na.encaixe, andou = EA.encostar(na, m, palma, na.encaixe, _vertices_do_corpo(col), *r['chegada'])
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

        m, rel['indicador'], _cadeia = EA.dedo_no_alvo(na, mao, m, 'indicador', alvo_g, normal_g, g['abertura'],
                                                       g['raio'], folga)
        rel['indicador']['folgaDoResto'] = round(folga(na.pontos(m.pose())) + g['folga'], 2)
    cadeia = polegar.Cadeia(col, mao, {o: q for o, q in m.pose().items() if not o.startswith('polegar')})
    p = r['polegar']
    if p.get('deitado'):
        eixo = (na.encaixe.inverted().to_3x3() @ Vector(p['eixo'])).normalized()
        m, rel['polegar'] = polegar.deitar_na_arma(col, mao, m, na, eixo, Vector(p['face']).normalized())
    else:
        alvo_p, normal_p = polegar.alvo_na_arma(cadeia, na, m, lim, regras.lado_do_polegar(r), p['peso'])
        m, rel['polegar'] = polegar.fechar_no_alvo(col, mao, m, alvo_p, normal_p, None, na=na)
    return m, rel


def _contatos(col, na, mao, pts, r):
    """{contato: [vértice, distância em mm]} da regra — a palma, cada dedo que fecha, a polpa do indicador (no gatilho)
    e a do polegar —, com o vértice de cada um mais perto da arma (as sondas)."""
    # a palma com as eminências (a tenar sobre o metacarpo do polegar e a hipotenar sobre os do anelar e do mínimo): é
    # nelas que a palma apoia num punho reto — o oco do meio fica afastado (o `palmaMeioMM` do relatório)
    grupos = {'palma': na.vertices(PALMA)}
    for d in r['dedos']:
        grupos[d] = na.vertices([f'{d}_{i}' for i in (1, 2, 3)])
    if r['gatilho']:
        grupos['indicador_gatilho'] = EA.CadeiaDedo(na, 'indicador', {}).lado_da_polpa
    grupos['polegar'] = polegar.Cadeia(col, mao, {}).lado_da_polpa
    saida = {}
    for nome, idx in grupos.items():
        dist = {i: na.arma.distancia(pts[i]) for i in idx}
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


def _polegar_deitado(rel_polegar):
    """Os problemas do polegar deitado da mão da frente (o relatório de empunhadura_polegar.deitar_na_arma): a curva (a
    MCP mais a IP) além de POLEGAR_CURVA_GRAUS, a falange distal sem encostar (o trecho dela mais perto a mais que o
    contato) ou algum trecho a mais de POLEGAR_FOLGA_MM da arma."""
    t = rel_polegar['trechosMM']
    meio = len(t) // 2
    problemas = []
    if rel_polegar['curvaGraus'] > POLEGAR_CURVA_GRAUS:
        problemas.append(f"o polegar da frente com {rel_polegar['curvaGraus']}° de curva (máximo {POLEGAR_CURVA_GRAUS}°): "
                         'tem de ficar reto, deitado na arma')
    if min(t[meio:]) > CONTATO_MM:
        problemas.append(f'a falange distal do polegar da frente não encosta na arma ({min(t[meio:]):.2f} mm)')
    for i, v in enumerate(t):
        if v > POLEGAR_FOLGA_MM:
            problemas.append(f"a falange {'proximal' if i < meio else 'distal'} do polegar da frente a {v:.2f} mm da arma "
                             f'(máximo {POLEGAR_FOLGA_MM} mm)')
    return problemas


def _angulos(mao, m):
    """(os ângulos totais das juntas dos dedos, os problemas de limite): cada flexão dentro da AAOS da ficha e cada
    abertura dentro da faixa do solver (±20° além do repouso)."""
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
    for osso, g in sorted(m.aberturas.items()):
        if abs(g) > empunhadura.ABERTURA_MAXIMA + 0.01:
            problemas.append(f'{osso}: abertura de {g:.2f}° (máximo ±{empunhadura.ABERTURA_MAXIMA}°)')
    return totais, problemas


def maos_da_regra(r_cat):
    """As mãos (lado, nome) que a regra da categoria tem: as duas, ou só a direita na faca (4.1c)."""
    maos_ = [(lado, nome) for lado, nome in LADOS if nome in r_cat]
    if not maos_ or maos_[0][0] != 'd':
        raise ValueError('a regra de empunhadura precisa da mão direita (a do gatilho ou a da faca)')
    return maos_


def resolver(ctx, mao, bracos, perto, soquetes, correcoes):
    """A pega das mãos da regra na arma (as peças do perto, as móveis em repouso). Devolve ({lado: {'encaixe': mm,
    'pose': {osso: quaternion}, 'contatos': ...}}, a seção `empunhadura` do relatório, os problemas)."""
    t0 = time.time()
    r_cat = regras.regra(ctx['categoria'], correcoes)
    arma = EA.Arma([o for k, o in perto.items() if not k.startswith('_')])
    base = EA.Arma([perto['base']])
    soq = {o.name[len('soquete_'):]: o for o in soquetes}
    pega, rel, problemas = {}, {}, []
    maos_ = maos_da_regra(r_cat)
    for lado, nome in maos_:
        r = r_cat[nome]
        luva, rig = bracos[lado]
        col = empunhadura.Colisor(luva, rig, mao, luvas.REFORCO)
        na = EA.NaArma(col, arma)
        m, rel_m = _pegar(col, na, mao, r, soq[r['soquete']], perto.get('gatilho'), base, lado)
        pose = m.pose()
        pts = na.pontos(pose)
        penetracao = na.penetracao(pts, limite=None)  # sem o limite das buscas: um dedo inteiro dentro da arma conta
        contatos = _contatos(col, na, mao, pts, r)
        conta, problemas_luva = validar_maos.conferir_uma(col.modelo, luva, luvas.REFORCO, f'pega {nome}', pose)
        totais, problemas_angulos = _angulos(mao, m)
        meio = min(na.arma.distancia(pts[i]) for i in na.vertices(['mao']))
        rel[lado] = {**rel_m, 'penetracaoMM': round(penetracao, 3), 'contatosMM': {k: v[1] for k, v in contatos.items()},
                     'palmaMeioMM': round(meio, 2), 'luva': conta, 'angulos': totais}
        if r.get('lados'):
            rel[lado]['lados'], problemas_lados = _lados(col, na, mao, pts, r)
            problemas += [f'pega {nome}: {p}' for p in problemas_lados]
        if r['polegar'].get('deitado'):
            problemas += [f'pega {nome}: {p}' for p in _polegar_deitado(rel_m['polegar'])]
        rel[lado]['juntosMM'] = EA.folgas_entre_dedos(col, pose, r['dedos'])
        for par, (media, _distal) in rel[lado]['juntosMM'].items():
            if media > JUNTOS_MM:
                problemas.append(f'pega {nome}: {par} com a falange média a {media:.2f} mm uma da outra (máximo '
                                 f'{JUNTOS_MM} mm): os dedos em leque, não lado a lado')
        if r.get('frente'):
            rel['frente'] = lado
        if penetracao > PENETRACAO_MM:
            problemas.append(f'pega {nome}: a luva entra {penetracao:.2f} mm na arma (máximo {PENETRACAO_MM} mm)')
        for k, (_i, d) in contatos.items():
            if d > CONTATO_MM:
                problemas.append(f'pega {nome}: o contato {k} a {d:.2f} mm da arma (máximo {CONTATO_MM} mm)')
        problemas += problemas_luva + [f'pega {nome}: {p}' for p in problemas_angulos]
        pega[lado] = {'encaixe': na.encaixe.copy(), 'pose': pose, 'contatos': contatos}
    rel['maos'] = [lado for lado, _n in maos_]
    rel['marca'] = {lado: maos_rig.marca(bracos[lado][1]) for lado, _n in maos_}
    rel['segundos'] = round(time.time() - t0, 1)
    return pega, rel, problemas


def guardar(bracos, pega):
    """A pega de cada braço nos rigs (o encaixe e a pose), para as vistas de perto do conferir na .blend."""
    for lado, dados in pega.items():
        bracos[lado][1]['pega'] = json.dumps({'encaixe': [list(r) for r in dados['encaixe']],
                                              'pose': maos_rig.pose_json(dados['pose'])})


def luvas_da_blend(ctx):
    """(mao, {lado: (luva, rig)}) das luvas guardadas na .blend da arma (o validar)."""
    return maos.Mao(ctx['luvas']['ficha']), {lado: (bpy.data.objects[f'luva_{lado}'], bpy.data.objects[f'rig_{lado}'])
                                             for lado, _n in LADOS}


def objetos_da_saida(mao, bracos, pega, marca, colecao):
    """Os objetos da pega no .glb da arma (ver o cabeçalho), em metros no referencial do Blender: o vazio `pega` (os
    extras: a marca, as sondas e as mãos), os vazios `pega_mao_*` e a armadura `pega_luvas` (as mãos da pega) com a ação
    `empunhadura`. Devolve [pega, pega_mao_d, (pega_mao_e,) pega_luvas]."""
    lados = [(lado, nome) for lado, nome in LADOS if lado in pega]
    raiz = bpy.data.objects.new('pega', None)
    colecao.objects.link(raiz)
    sondas = {lado: {k: {'vertice': v[0], 'mm': v[1]} for k, v in pega[lado]['contatos'].items()} for lado in pega}
    raiz['luvas'] = json.dumps({'marca': {lado: marca[lado] for lado, _n in lados}, 'sondas': sondas,
                                'maos': [lado for lado, _n in lados]}, separators=(',', ':'))
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
