# O alvo `luvas` do principal.py (Fase 4.1b; desenho em docs/superpowers/specs/2026-09-26-4.1b-luvas-e-empunhadura-design.md,
# seção 3): as luvas construídas pela ficha (tools/blender/refs/luvas.json) e o registro (src/data/luvas.js), os dois
# validados pelo lançador.
#   construir: a luva direita — a malha base (maos_gaiola.py, subdividida 1 nível) e as peças de detalhe
#              (maos_detalhes.py) com os materiais de fábrica da pintura de Massa Crua, e o modelo alto (maos_alto.py:
#              a base no nível 4 com as rugas, as costuras e as máscaras, e as peças com os respiros e as nervuras) —,
#              o rig (maos_rig.py: a armadura, as peças juntadas com os pesos da superfície), o modelo das correções
#              das dobras (maos_correcoes.py, os parâmetros guardados na luva) e as poses de teste (maos_poses.py e
#              validar_maos.py), as medidas contra a ficha (±1 %), o assentamento das peças, os triângulos contra o
#              orçamento, a UV por costuras (assar.uv_por_costuras: sem sobreposição, a densidade de cada ilha a
#              0,6–1,6 da mediana), o braço esquerdo espelhado (maos_rig.espelhar, com as correções dele e a
#              conferência de que, em cada pose de teste espelhada, ele é o direito espelhado a 0,01 mm), a marca do
#              rig de cada braço, a prova do modelo das dobras (vértices avaliados nas poses, que o jogo refaz em
#              JS) e a .blend da conferência em tools/blender/conferencia/luvas/; aprovada, assa as
#              texturas `luvas_n` e `luvas_m` (2048, do modelo alto) e grava o luvas.glb (exportar.exportar_luvas) e o
#              relatório em assets/maos/;
#   validar:   reabre a .blend e refaz as medidas, as contas e as poses;
#   conferir:  as vistas do modelo alto (costas, palma, os dois lados, de frente para as pontas, três quartos, de perto
#              dos nós, dos dedos e do punho) nas duas facções, as zonas em cores chapadas e a gaiola em arame por cima
#              das costas.
# As linhas `MASSACRE-*` da saída são lidas pelo lançador; reprovado sai com código 1.
import json
import os
import sys
import time

import bmesh
import bpy
import numpy as np
from mathutils import Vector

from . import (assar, estudio, exportar, maos, maos_alto, maos_correcoes, maos_detalhes, maos_gaiola, maos_medidas, maos_poses, maos_rig,
               materiais, validar_maos)
from .unidades import S

TOLERANCIA = 0.01  # as medidas da malha a ±1 % dos alvos da ficha
ASSENTAMENTO_MM = 0.1  # a base das paredes de cada peça a 0,2 ± 0,1 mm dentro da luva: sem vão nem sobra
# Cores chapadas das zonas nas vistas `zonas_*` (a conferência das fronteiras entre os materiais).
_CORES_DAS_ZONAS = {'couro': (0.62, 0.36, 0.16), 'tecido': (0.16, 0.30, 0.52), 'reforco': (0.85, 0.78, 0.20)}
_CENTRO = (0.085, 0.0, 0.0)  # metros: mais ou menos o meio da mão, do punho às pontas
ZONAS = ('couro', 'tecido', 'reforco')  # os materiais da luva de jogo depois de juntar as peças, nesta ordem
REFORCO = ZONAS.index('reforco')
UV_MARGEM_PX = 8
DENSIDADE = (0.6, 1.6)  # a densidade de texel de cada ilha, relativa à mediana (as armas da 4.1a)
ESPELHO_MM = 0.01  # o braço esquerdo em pose contra o direito espelhado
# As gaiolas do assar (assar.assar_grupos), medidas pela normal de jogo nos vértices e no centro das faces: a base alta
# fica de −0,46 a +0,53 mm da de jogo — 0,8 mm para fora e 1,6 mm de raio, sem alcançar o dedo vizinho na membrana
# (com os 2 e 4 mm das armas, o raio pegava o dedo do lado e assava cunhas tortas nas ilhas dos dedos); as peças altas,
# de −1,6 a +1,42 mm das de jogo (as bordas arredondadas para dentro) — 1,9 mm para fora e 3,8 mm de raio.
# A prova do modelo das dobras no relatório (o teste de paridade do jogo): 1 vértice em 11 e as poses que exercitam o
# skin, as dobras dos dedos e do polegar e a do pulso.
PROVA_AMOSTRA = 11
PROVA_POSES = ('repouso', 'punho', 'pulso', 'apontar')
GAIOLA_BASE_MM = (0.8, 1.6)
GAIOLA_PECAS_MM = (1.9, 3.8)


def _material_de_zona(zona):
    m = bpy.data.materials.get(f'zona_{zona}') or bpy.data.materials.new(f'zona_{zona}')
    m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*_CORES_DAS_ZONAS[zona], 1)
    b.inputs['Roughness'].default_value = 0.7
    return m


def _colecao(nome):
    col = bpy.data.collections.get(nome) or bpy.data.collections.new(nome)
    if col.name not in bpy.context.scene.collection.children:
        bpy.context.scene.collection.children.link(col)
    return col


def _relatorio(ctx, mao, residuo=None):
    """As contas da luva de jogo direita (a base com as peças juntadas e o rig): medidas, triângulos, as poses de teste
    (com o assentamento das peças) e a marca do rig; e os problemas."""
    luva = bpy.data.objects['luva_d']
    rig = bpy.data.objects['rig_d']
    maos_rig.posar(rig, {})
    medidas = maos_medidas.medir_mao(luva, mao)
    me = luva.data
    tris = {'base': sum(len(p.vertices) - 2 for p in me.polygons if p.material_index != REFORCO),
            'detalhes': sum(len(p.vertices) - 2 for p in me.polygons if p.material_index == REFORCO)}
    tris['luva'] = tris['base'] + tris['detalhes']
    limite = ctx['orcamento']['triangulos'] // 2
    contato, rel_contato, problemas_contato = maos_poses.poses_de_teste(luva, rig, mao, REFORCO)
    testes = {'repouso': {}, **contato, **{p: maos_rig.pose_de_teste(p, mao) for p in ('aberta', 'pulso')}}
    poses, problemas_poses = validar_maos.validar_poses(luva, rig, mao, REFORCO, testes)
    poses['contato'] = rel_contato
    rig['poses_de_teste'] = json.dumps({n: maos_rig.pose_json(p) for n, p in testes.items()})
    assentamento = poses['repouso']['assentamentoMM']
    rel = {'triangulos': tris, 'vertices': len(me.vertices), 'grupos': sorted(g.name for g in luva.vertex_groups),
           'assentamentoMM': assentamento, 'medidas': medidas, 'poses': poses,
           'marca': {lado: maos_rig.marca(bpy.data.objects[f'rig_{lado}']) for lado in ('d', 'e')
                     if f'rig_{lado}' in bpy.data.objects},
           'correcoes': {'juntas': [j['junta'] for j in json.loads(luva['correcoes'])['juntas']]}}
    if residuo is not None:
        rel['residuoAjusteMM'] = round(residuo, 5)
    problemas = list(problemas_contato) + list(problemas_poses)
    for nome, m in medidas.items():
        desvio = m['mm'] / m['alvo'] - 1
        if abs(desvio) > TOLERANCIA:
            problemas.append(f"{nome}: {m['mm']:.2f} mm contra {m['alvo']:.2f} mm ({desvio * 100:+.2f} %, tolerância ±1 %)")
    if tris['luva'] > limite:
        problemas.append(f"triângulos: {tris['luva']} numa luva (orçamento {limite}, a metade dos dois braços)")
    if assentamento > ASSENTAMENTO_MM:
        problemas.append(f'assentamento: a base de uma peça a {assentamento:.3f} mm fora dos 0,2 mm dentro da luva '
                         f'(tolerância {ASSENTAMENTO_MM} mm)')
    return rel, problemas


def _uv_e_espelho(ctx, mao, luva, rig, colecao):
    """A UV da luva direita pelas costuras e o braço esquerdo espelhado dela (as mesmas UV), com as correções das
    dobras dele. Devolve (luva_e, rig_e, a conta da UV, o maior desvio do espelho em mm, os problemas)."""
    lado = ctx['orcamento']['textura']
    assar.uv_por_costuras([luva], lado, UV_MARGEM_PX)
    uv = {'sobreposicao': assar.sobreposicao_uv([luva]), **assar.densidade_por_ilha(luva, lado)}
    luva_e, rig_e = maos_rig.espelhar(luva, rig, mao, colecao)
    modelo_d = maos_correcoes.Modelo(luva, rig, mao, REFORCO)
    modelo_e = maos_correcoes.Modelo(luva_e, rig_e, mao, REFORCO)
    luva_e['correcoes'] = json.dumps(modelo_e.parametros(), separators=(',', ':'))
    desvio = 0.0
    for pose in (maos_rig.pose_de_json(p) for p in json.loads(rig['poses_de_teste']).values()):
        d = modelo_d.avaliar(pose)
        d[:, 1] *= -1.0
        desvio = max(desvio, float(np.abs(modelo_e.avaliar(maos_rig.espelhar_pose(pose)) - d).max()))
    prova = {'d': _prova_do_modelo(modelo_d, rig), 'e': _prova_do_modelo(modelo_e, rig, espelhada=True)}
    maos_rig.posar(rig, {})
    maos_rig.posar(rig_e, {})
    problemas = []
    if uv['sobreposicao']:
        problemas.append(f"UV: {uv['sobreposicao']} texels cobertos por mais de uma face")
    if not DENSIDADE[0] <= uv['minimo'] <= uv['maximo'] <= DENSIDADE[1]:
        problemas.append(f"UV: a densidade das ilhas de {uv['minimo']} a {uv['maximo']} da mediana (dentro de "
                         f"{DENSIDADE[0]}–{DENSIDADE[1]})")
    if desvio > ESPELHO_MM:
        problemas.append(f'espelho: o braço esquerdo a {desvio:.4f} mm do direito espelhado (máximo {ESPELHO_MM} mm)')
    return luva_e, rig_e, uv, round(desvio, 5), problemas, prova


def _prova_do_modelo(modelo, rig, espelhada=False):
    """A prova do modelo das dobras para o jogo (modeloDobras.js refaz as mesmas contas em JS): uma amostra de vértices
    (1 em PROVA_AMOSTRA, pelo índice do Blender) avaliada nas poses de PROVA_POSES (no braço esquerdo, as da direita
    espelhadas), em mm no referencial do braço no Blender, e cada giro da pose como eixo (no referencial do braço, em
    repouso: o do osso levado pela orientação de repouso dele) e ângulo em radianos — a forma que não depende do
    referencial local dos ossos, que o glTF converte."""
    poses = json.loads(rig['poses_de_teste'])  # as poses de teste ficam no rig direito
    lado = modelo.malha.lado
    n = len(modelo.malha.p)
    idx = list(range(0, n, PROVA_AMOSTRA))
    saida = {'vertices': idx, 'poses': {}}
    for nome in PROVA_POSES:
        pose = maos_rig.pose_de_json(poses[nome])
        if espelhada:
            pose = maos_rig.espelhar_pose(pose)
        giros = {}
        for osso, q in pose.items():
            if q.angle < 1e-9:
                continue
            eixo = (modelo.malha.rig.data.bones[f'{osso}_{lado}'].matrix_local.to_3x3() @ q.axis).normalized()
            giros[osso] = [round(c, 7) for c in eixo] + [round(q.angle, 7)]
        pts = modelo.avaliar(pose)
        saida['poses'][nome] = {'giros': giros, 'mm': np.round(pts[idx], 4).tolist()}
    return saida


def _alvos_do_assar(luva):
    """Duas cópias da luva de jogo em repouso para o assar por grupos: a base (couro e tecido) e as peças (o reforço)."""
    alvos = []
    for nome, pecas in (('base', False), ('pecas', True)):
        me = luva.data.copy()
        bm = bmesh.new()
        bm.from_mesh(me)
        bmesh.ops.delete(bm, geom=[f for f in bm.faces if (f.material_index == REFORCO) != pecas], context='FACES')
        bm.to_mesh(me)
        bm.free()
        ob = bpy.data.objects.new(f'assar_{nome}', me)
        bpy.context.scene.collection.objects.link(ob)
        alvos.append(ob)
    return alvos


def _etapa(t0, nome):
    """Linha de progresso para o lançador (o modelo alto leva um tempo)."""
    print('MASSACRE-ETAPA', json.dumps({'etapa': nome, 's': round(time.time() - t0, 1)}, ensure_ascii=False), flush=True)


def montar_jogo(mao, M, colecao, antes_do_rig=None):
    """A luva de jogo direita com o rig: a malha base (maos_gaiola.py, subdividida 1 nível), as peças de detalhe
    (maos_detalhes.py) juntadas nela com os pesos da superfície, a armadura e as correções das dobras guardadas na luva.
    `antes_do_rig(peças)` roda com as peças ainda soltas (o modelo alto usa elas). O mesmo caminho serve às luvas e ao
    solver de empunhadura de cada arma (empunhadura_pega.py): as duas saem do mesmo esqueleto (D4, a marca do rig).
    Devolve (luva, rig, o resíduo do ajuste da gaiola)."""
    luva, residuo = maos_gaiola.malha_base(mao, colecao, {z: M[z] for z in maos_gaiola.ZONAS_BASE}, 'luva_d',
                                           subdividir=1)
    pecas, _ = maos_detalhes.construir(mao, luva, colecao, M['reforco'])
    if antes_do_rig:
        antes_do_rig(pecas)
    rig = maos_rig.armadura(mao, colecao, 'd')
    maos_rig.pesos(luva, pecas, 'd')
    maos_rig.ligar(luva, rig)
    luva['correcoes'] = json.dumps(maos_correcoes.Modelo(luva, rig, mao, REFORCO).parametros(), separators=(',', ':'))
    return luva, rig, residuo


def construir(ctx):
    t0 = time.time()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    os.makedirs(ctx['conferencia'], exist_ok=True)
    mao = maos.Mao(ctx['ficha'])
    M = materiais.materiais_das_luvas(ctx['pinturas']['massaCrua'])
    jogo = _colecao('jogo')
    altos = []

    def alto(pecas):
        _etapa(t0, 'malha de jogo e detalhes')
        altos.extend(maos_alto.construir(mao, M, pecas, _colecao('alto'), lambda nome: _etapa(t0, nome)))

    luva, rig, residuo = montar_jogo(mao, M, jogo, alto)
    _etapa(t0, 'rig, pesos e correções das dobras')
    gaiola, _ = maos_gaiola.malha_base(mao, _colecao('gaiola'), {z: _material_de_zona(z) for z in maos_gaiola.ZONAS_BASE},
                                       'gaiola_d', subdividir=0)
    gaiola.hide_render = True
    rel, problemas = _relatorio(ctx, mao, residuo)
    _etapa(t0, 'medidas e poses de teste')
    luva_e, rig_e, uv, espelho, problemas_uv, prova = _uv_e_espelho(ctx, mao, luva, rig, jogo)
    problemas += problemas_uv
    rel.update({'uv': uv, 'espelhoMM': espelho, 'marca': {'d': maos_rig.marca(rig), 'e': maos_rig.marca(rig_e)},
                'provaDoModelo': prova,
                'alto': {'objetos': len(altos), 'faces': sum(len(o.data.polygons) for o in altos)},
                'entradas': {'hash': ctx['hash']}})
    _etapa(t0, 'UV e o braço esquerdo')
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ctx['conferencia'], 'luvas.blend'))
    if problemas:
        rel['segundos'] = round(time.time() - t0, 1)
        print('MASSACRE-LUVAS', json.dumps(rel, ensure_ascii=False))
        print('MASSACRE-REPROVADO', json.dumps(problemas, ensure_ascii=False))
        sys.exit(1)
    pasta = ctx['saida']
    os.makedirs(pasta, exist_ok=True)
    base_alta = bpy.data.objects['luva_d_alto']
    pecas_altas = [o for o in bpy.data.collections['alto'].objects if o.type == 'MESH' and o is not base_alta]
    base, pecas_jogo = _alvos_do_assar(luva)
    assar.assar_grupos([([base_alta], [base], *GAIOLA_BASE_MM), (pecas_altas, [pecas_jogo], *GAIOLA_PECAS_MM)],
                       ctx['orcamento']['textura'], UV_MARGEM_PX, pasta, 'luvas_n', 'luvas_m')
    for ob in (base, pecas_jogo):
        bpy.data.objects.remove(ob)
    _etapa(t0, 'assar')
    exportar.exportar_luvas(pasta, [(luva, rig), (luva_e, rig_e)], rel['marca'])
    _etapa(t0, 'exportar')
    rel.update({'luvas': True, 'aprovado': True, 'problemas': [],
                'arquivos': {n: os.path.getsize(os.path.join(pasta, n))
                             for n in ('luvas.glb', 'luvas_n.webp', 'luvas_m.webp')},
                'segundos': round(time.time() - t0, 1)})
    exportar.gravar_relatorio(pasta, 'luvas', rel)
    print('MASSACRE-LUVAS', json.dumps(rel, ensure_ascii=False))


def validar(ctx):
    bpy.ops.wm.open_mainfile(filepath=os.path.join(ctx['conferencia'], 'luvas.blend'))
    rel, problemas = _relatorio(ctx, maos.Mao(ctx['ficha']))
    print('MASSACRE-VALIDACAO', json.dumps({**rel, 'problemas': problemas}, ensure_ascii=False))
    if problemas:
        sys.exit(1)


def _pintar(pintura_ou_zonas):
    """Troca os materiais das luvas de jogo e altas (bases e peças): por uma pintura (os de fábrica) ou pelas cores
    chapadas das zonas."""
    if pintura_ou_zonas == 'zonas':
        M = {z: _material_de_zona(z) for z in _CORES_DAS_ZONAS}
    else:
        M = materiais.materiais_das_luvas(pintura_ou_zonas)
    for nome_col in ('jogo', 'alto'):
        for ob in bpy.data.collections[nome_col].objects:
            if ob.type != 'MESH':
                continue
            if 'zona' in ob:
                ob.data.materials[0] = M[ob['zona']]
            else:
                for i in range(len(ob.data.materials)):
                    ob.data.materials[i] = M[ZONAS[i]]


def conferir(ctx, amostras=96):
    bpy.ops.wm.open_mainfile(filepath=os.path.join(ctx['conferencia'], 'luvas.blend'))
    sc = bpy.context.scene
    pasta = ctx['conferencia']
    bpy.data.collections['jogo'].hide_render = True  # as vistas são do modelo alto
    fundo = estudio.montar(_CENTRO)
    fundo.hide_render = True  # as vistas de baixo e dos lados veriam o chão entre a câmera e a mão
    # O estúdio das armas ilumina de cima; a palma pede uma luz de baixo, fria e fraca (a do rebatedor do set).
    baixo = bpy.data.lights.new('baixo', 'AREA')
    baixo.size, baixo.energy, baixo.color = 0.9, 9.0, (0.92, 0.95, 1.0)
    ob_baixo = bpy.data.objects.new('baixo', baixo)
    sc.collection.objects.link(ob_baixo)
    ob_baixo.location = Vector(_CENTRO) + Vector((0.05, -0.25, -0.7))
    ob_baixo.rotation_euler = (Vector(_CENTRO) - ob_baixo.location).to_track_quat('-Z', 'Y').to_euler()
    dispositivo = estudio.render(1600, 1100, amostras)
    c = Vector(_CENTRO)
    nos = Vector((0.094, 0.0, 0.012))  # a linha dos nós, por cima
    punho = Vector((-0.022, -0.01, 0.0))  # a tira do punho
    vistas = {
        'costas': (c + Vector((0.0, 0.0, 0.6)), c, 0.3),
        'palma': (c + Vector((0.0, 0.0, -0.6)), c, 0.3),
        'polegar': (c + Vector((0.0, 0.6, 0.0)), c, 0.3),
        'minimo': (c + Vector((0.0, -0.6, 0.0)), c, 0.3),
        'pontas': (c + Vector((0.6, 0.0, 0.05)), c, 0.2),
        'tres_quartos': (c + Vector((0.28, -0.3, 0.3)), c, None),
        'perto_nos': (nos + Vector((0.07, -0.09, 0.11)), nos, None),
        'perto_punho': (punho + Vector((0.02, -0.12, 0.1)), punho, None),
        'perto_dedos': (Vector((0.18, -0.08, 0.1)), Vector((0.13, 0.0, 0.0)), None),
        'perto_palma': (Vector((0.07, -0.05, -0.15)), Vector((0.05, 0.0, -0.01)), None),
    }
    arquivos = []

    def fotografar(nome, pos, alvo, orto):
        sc.camera = estudio.camera(nome, pos, alvo, 45, orto)
        sc.render.filepath = os.path.join(pasta, f'{nome}.png')
        bpy.ops.render.render(write_still=True)
        arquivos.append(sc.render.filepath)

    for nome, (pos, alvo, orto) in vistas.items():
        fotografar(nome, pos, alvo, orto)
    # A outra facção: as vistas que mostram a pintura inteira.
    _pintar(ctx['pinturas']['tropa'])
    for nome in ('costas', 'palma', 'tres_quartos', 'perto_nos', 'perto_punho'):
        pos, alvo, orto = vistas[nome]
        fotografar(f'tropa_{nome}', pos, alvo, orto)
    # As zonas em cores chapadas, de costas e de palma.
    _pintar('zonas')
    fotografar('zonas_costas', *vistas['costas'])
    fotografar('zonas_palma', *vistas['palma'])
    # A gaiola em arame por cima das costas.
    gaiola = bpy.data.objects['gaiola_d']
    arame = gaiola.modifiers.new('arame', 'WIREFRAME')
    arame.thickness = 0.35 * S
    m_arame = bpy.data.materials.new('arame')
    m_arame.use_nodes = True
    em = m_arame.node_tree.nodes.new('ShaderNodeEmission')
    em.inputs['Color'].default_value = (1.0, 0.8, 0.1, 1)
    em.inputs['Strength'].default_value = 3.0
    m_arame.node_tree.links.new(em.outputs[0], m_arame.node_tree.nodes['Material Output'].inputs[0])
    gaiola.data.materials.clear()
    gaiola.data.materials.append(m_arame)
    gaiola.hide_render = False
    fotografar('costas_arame', *vistas['costas'])
    # As poses de teste na luva de jogo com o rig (pintura de Massa Crua), de três quartos e de baixo.
    gaiola.hide_render = True
    _pintar(ctx['pinturas']['massaCrua'])
    bpy.data.collections['jogo'].hide_render = False
    bpy.data.collections['alto'].hide_render = True
    # (a luva de jogo pelo modelo das luvas — o skin e as correções das dobras — numa cópia sem rig, como no jogo)
    luva = bpy.data.objects['luva_d']
    rig = bpy.data.objects['rig_d']
    modelo = maos_correcoes.Modelo(luva, rig, maos.Mao(ctx['ficha']), REFORCO)
    poses = json.loads(rig['poses_de_teste'])
    luva.hide_render = True
    for nome in ('punho', 'apontar', 'mesa', 'aberta', 'pulso'):
        ob = modelo.para_malha(f'pose_{nome}', bpy.data.collections['jogo'], maos_rig.pose_de_json(poses[nome]))
        fotografar(f'pose_{nome}', *vistas['tres_quartos'])
        fotografar(f'pose_{nome}_palma', c + Vector((0.12, -0.25, -0.35)), c, None)
        bpy.data.objects.remove(ob)
    maos_rig.posar(rig, {})
    return arquivos, dispositivo
