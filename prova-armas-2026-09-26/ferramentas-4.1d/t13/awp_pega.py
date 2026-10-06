"""Tarefa 13 da 4.1d (a AWP na mão): o banco de prova das duas mãos na AWP de verdade, numa sessão do Blender que fica
aberta (servidor.py) — a arma e as luvas montadas uma vez, cada mão resolvida em segundos pelo mesmo caminho da pega
do construir (empunhadura_pega._uma_mao, o afundamento da palma e a validação da mão, conferir_mao).

Uso, num trabalho da fila do servidor (o espaço de nomes G persiste entre os trabalhos):
    import awp_pega as A
    A.preparar()        # uma vez: a .blend da conferência da AWP com as luvas montadas (awp_luvas.blend)
    A.carregar()        # abre awp_luvas.blend e monta o contexto do _uma_mao
    A.mao('d', {...})   # a mão direita com as correções (as chaves da regra `sniper`); devolve o resumo
    A.mao('e', {...}, vistas='fora,jogador')
O resumo traz o relatório da mão e as contas a mais desta prova: os nós (as juntas posadas, mm no referencial da arma),
para onde aponta a distal do polegar, a ponta dele, o dorso contra a câmera do jogador (a mão de apoio) e as folgas para
o bipé e o cano. As vistas são renders rápidos no Workbench (a luva posada com o afundamento da palma, a arma cinza) em
<TRABALHO>/renders/<nome>_<vista>.png — nada do jogo: só o nosso modelo.
"""
import copy
import json
import math
import os
import sys
import tempfile
import time
import traceback

import numpy as np

import bpy
from mathutils import Matrix, Vector

RAIZ = r'C:\Users\T-Gamer\Desktop\game tiro\trabalho-4.1d'
TRABALHO = (r'C:\Users\T-Gamer\AppData\Local\Temp\claude\C--Users-T-Gamer-Desktop-game-tiro'
            r'\c7a63f39-8955-467e-9908-7a258f968380\scratchpad\t13')
sys.path.insert(0, os.path.join(RAIZ, 'tools', 'blender'))

from armas import (empunhadura, empunhadura_arma as EA, empunhadura_furo as FURO,  # noqa: E402
                   empunhadura_palma as PALMA, empunhadura_pega as EP, empunhadura_polegar as EPO,
                   empunhadura_regras as ER, empunhadura_validacao as V, luvas, maos, maos_correcoes, maos_rig,
                   pecas as P)
from armas.unidades import S  # noqa: E402

CTX = os.path.join(tempfile.gettempdir(), 'massacre-blender', 'awp-real.json')
LUVAS_BLEND = os.path.join(TRABALHO, 'awp_luvas.blend')
RENDERS = os.path.join(TRABALHO, 'renders')
# a direção da câmera do jogador a partir da mão de apoio (a de provas_lateral.py: de trás, da esquerda e de cima)
DO_JOGADOR = Vector((-0.42, 0.15, 0.12)).normalized()
LADOS = {'d': 'direita', 'e': 'esquerda'}
try:
    C  # noqa: B018 — o contexto da sessão (carregar) sobrevive ao importlib.reload deste módulo
except NameError:
    C = {}


def contexto():
    with open(CTX, encoding='utf-8') as f:
        ctx = json.load(f)
    ctx['categoria'] = 'sniper'
    ctx['pega'] = True
    for chave, arquivo in (('ficha', 'awp.json'),):
        with open(os.path.join(RAIZ, 'tools', 'blender', 'refs', arquivo), encoding='utf-8') as f:
            ctx[chave] = json.load(f)
    with open(os.path.join(RAIZ, 'tools', 'blender', 'refs', 'luvas.json'), encoding='utf-8') as f:
        ctx['luvas']['ficha'] = json.load(f)
    return ctx


def colecao(nome):
    col = bpy.data.collections.get(nome) or bpy.data.collections.new(nome)
    if col.name not in bpy.context.scene.collection.children:
        bpy.context.scene.collection.children.link(col)
    return col


def preparar():
    """A .blend da conferência da AWP (o construir sem a pega) com as duas luvas montadas pelo caminho do construir."""
    ctx = contexto()
    bpy.ops.wm.open_mainfile(filepath=os.path.join(RAIZ, 'tools', 'blender', 'conferencia', 'awp', 'awp.blend'))
    t0 = time.time()
    EP.montar_luvas(ctx, colecao('luvas'))
    os.makedirs(TRABALHO, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=LUVAS_BLEND)
    print('PREPARAR luvas montadas em', round(time.time() - t0, 1), 's; gravado', LUVAS_BLEND)


def lacos(ficha):
    """Os laços do buraco do polegar: o da ficha (o traçado) e o que a coronha corta (o oval equivalente, awp.py)."""
    bruto = ficha['buracos'][ficha['buracosNomes'].index('buracoPolegar')]
    return {'ficha': [tuple(p) for p in bruto], 'oval': P.oval_equivalente(bruto, 48)}


def carregar(laco='oval'):
    """Abre awp_luvas.blend e monta o contexto do _uma_mao em C (o furo do polegar pelo `laco`: 'oval' ou 'ficha')."""
    ctx = contexto()
    bpy.ops.wm.open_mainfile(filepath=LUVAS_BLEND)
    mao = maos.Mao(ctx['luvas']['ficha'])
    bracos = {lado: (bpy.data.objects[f'luva_{lado}'], bpy.data.objects[f'rig_{lado}']) for lado in ('d', 'e')}
    perto = {o.name[len('perto_'):]: o for o in bpy.data.collections['perto'].objects if o.type == 'MESH'}
    soqs = {o.name[len('soquete_'):]: o for o in bpy.data.collections['soquetes'].objects}
    objetos = [o for k, o in perto.items() if not k.startswith('_')]
    arma = EA.Arma(objetos)
    t0 = time.time()
    furos = {'buracoPolegar': FURO.Furo('buracoPolegar', lacos(ctx['ficha'])[laco], arma)}
    C.update({'ctx': ctx, 'mao': mao, 'bracos': bracos, 'perto': perto, 'soqs': soqs, 'objetos': objetos,
              'arma': arma, 'furos': furos, 'laco': laco,
              'contexto': (mao, bracos, objetos, arma, EA.Arma([perto['base']]), soqs, perto, furos)})
    f = furos['buracoPolegar']
    print('CARREGAR', LUVAS_BLEND, 'furo', laco, 'faces (mediana) direita/esquerda', [round(v, 2) for v in f.faces_medias],
          'faces min/max', [round(float(v), 2) for v in (f.faces[:, 0].min(), f.faces[:, 0].max(), f.faces[:, 1].min(),
                                                         f.faces[:, 1].max())], round(time.time() - t0, 1), 's')


def tuplas(d):
    """As listas do JSON como tuplas (as regras usam tuplas; o `giros` é uma tupla de pares)."""
    def t(v):
        return tuple(t(x) for x in v) if isinstance(v, list) else v
    return {k: (t(v) if isinstance(v, list) else ({kk: t(vv) for kk, vv in v.items()} if isinstance(v, dict) else v))
            for k, v in d.items()}


def base_da_prova(base):
    """A regra base: a da categoria, se já existe; a `sniper` ainda sem os números da AWP é a mão direita da `rifle` com o
    polegar pelo buraco do polegar (o polegar afastado na chegada, como na prova do furo) e a esquerda pela LATERAL."""
    if base in ER.REGRAS:
        return ER.REGRAS[base]
    return {'direita': {**copy.deepcopy(ER.RIFLE['direita']),
                        'polegar': {'furo': 'buracoPolegar', 'saida': (0.0, 1.0, 0.0), 'eixo': (1.0, 0.0, 0.0)},
                        'polegar_afastado': True},
            'esquerda': copy.deepcopy(ER.LATERAL)}


def regra(lado, correcoes=None, base='sniper'):
    """A regra da mão do `lado` com as correções por cima (as chaves novas também entram: é uma prova)."""
    r = copy.deepcopy(base_da_prova(base)[LADOS[lado]])
    for k, v in tuplas(correcoes or {}).items():
        r[k] = v
    return r


def _nos(f, lado):
    """As juntas posadas (as cabeças dos ossos, mm no referencial da arma)."""
    luva, rig = C['bracos'][lado]
    maos_rig.posar(rig, f['m'].pose())
    bpy.context.view_layer.update()
    e = f['na'].encaixe
    nos = {o: [round(c, 1) for c in e @ (rig.pose.bones[f'{o}_{lado}'].head / S)]
           for o in ('mao', 'polegar_1', 'polegar_2', 'polegar_3', 'indicador_1', 'medio_1', 'anelar_1', 'minimo_1',
                     'indicador_3', 'medio_3', 'anelar_3', 'minimo_3')}
    maos_rig.posar(rig, {})
    bpy.context.view_layer.update()
    return nos


def _extras(f, lado, pts):
    """As contas a mais desta prova (ver o cabeçalho)."""
    col, na = f['col'], f['na']
    dono = np.array(col.dono)
    pts = np.asarray(pts)
    ex = {'nos': _nos(f, lado)}
    cadeia = EPO.Cadeia(col, C['mao'], {})
    ms = cadeia.matrizes(EPO.graus_da_pose(f['m'], cadeia))
    distal = (na.encaixe.to_3x3() @ (ms[2].to_3x3() @ Vector((0.0, 1.0, 0.0)))).normalized()
    ex['distalDoPolegar'] = [round(v, 3) for v in distal]
    ex['distalAFrenteGraus'] = round(math.degrees(distal.angle(Vector((1.0, 0.0, 0.0)))), 1)
    p2 = pts[dono == 'polegar_2'].mean(0)
    p3 = pts[dono == 'polegar_3']
    ponta = p3[np.argmax(((p3 - p2) ** 2).sum(1))]
    ex['pontaDoPolegar'] = [round(float(c), 1) for c in ponta]
    ex['centros'] = {o: [round(float(c), 1) for c in pts[dono == o].mean(0)]
                     for o in ('polegar_2', 'polegar_3', 'mao', 'indicador_3', 'medio_3', 'minimo_3')}
    dorso = na.encaixe.to_3x3() @ Vector((0.0, 0.0, 1.0))
    ex['dorso'] = [round(v, 3) for v in dorso]
    if lado == 'e':
        ex['dorsoAoJogadorGraus'] = round(math.degrees(dorso.angle(DO_JOGADOR)), 1)
    # as folgas da luva para as peças do perto (o bipé, o cano e o resto)
    folgas = {}
    for nome, ob in C['perto'].items():
        if nome.startswith('_'):
            continue
        peca = EA.Arma([ob])
        folgas[nome] = round(min(peca.distancia(Vector(q), 40.0) or 40.0 for q in pts), 2)
    ex['folgasMM'] = folgas
    # o eixo do cano é o X da arma (y = z = 0): a menor distância a ele da pele de cada distal (o cano tem ~10 mm de
    # raio no guarda-mão) e o alto de cada dedo
    ex['distalAoEixoMM'] = {d: round(float(np.hypot(pts[dono == f'{d}_3'][:, 1], pts[dono == f'{d}_3'][:, 2]).min()), 1)
                            for d in ('indicador', 'medio', 'anelar', 'minimo')}
    ex['altoDoDedoMM'] = {d: round(float(pts[np.isin(dono, [f'{d}_{i}' for i in (1, 2, 3)])][:, 2].max()), 1)
                          for d in ('indicador', 'medio', 'anelar', 'minimo')}
    return ex


def mao(lado, correcoes=None, vistas=None, nome=None, base='sniper'):
    """Uma mão da regra (as correções por cima) na AWP: o _uma_mao, o afundamento e a validação. Devolve o resumo e
    imprime a linha PROVA-AWP."""
    t0 = time.time()
    r = regra(lado, correcoes, base)
    saida = {'lado': lado, 'correcoes': correcoes or {}}
    try:
        f = EP._uma_mao(C['contexto'], lado, r, {})
    except (empunhadura.PolegarCruza, EA.ChegadaCruza, RuntimeError) as erro:
        saida.update({'erro': f'{type(erro).__name__}: {erro}', 'segundos': round(time.time() - t0, 1)})
        print('PROVA-AWP', json.dumps(saida, ensure_ascii=False), flush=True)
        traceback.print_exc()
        return saida
    arma, objetos, perto = C['arma'], C['objetos'], C['perto']
    afundar = PALMA.afundamento(EA.NaArma(f['col'], arma, f['na'].encaixe), f['m'].pose())
    luva = C['bracos'][lado][0]
    rel, _sondas, problemas = V.conferir_mao(f, LADOS[lado], C['mao'], luva, arma, objetos, perto, afundar)
    pts = EA.NaArma(f['col'], arma, f['na'].encaixe, ceder=False, afundar=afundar).pontos(f['m'].pose())
    saida.update({k: rel[k] for k in ('palmaAndouMM', 'dedosPararam', 'juntar', 'indicador', 'polegar', 'ladosLateral',
                                      'polegarNoFuro', 'penetracaoMM', 'contatosMM', 'palmaMeioMM', 'juntosMM', 'palma',
                                      'angulos', 'luva') if k in rel})
    saida.update(_extras(f, lado, pts))
    saida.update({'problemas': problemas, 'segundos': round(time.time() - t0, 1)})
    print('PROVA-AWP', json.dumps(saida, ensure_ascii=False, default=str), flush=True)
    C['ultima'] = {'f': f, 'afundar': afundar, 'lado': lado}
    if vistas:
        renders(f, lado, afundar, nome or f'{lado}_{int(time.time())}', vistas)
    return saida


def resolver(vistas_d=None, vistas_e=None, nome='pega'):
    """A pega inteira pelo caminho do construir (empunhadura_pega.resolver com a regra da categoria, o EMPUNHADURA da
    arma e os laços dela): imprime a seção `empunhadura` do relatório e os problemas; com as vistas, renders das duas
    mãos posadas (o afundamento da palma de cada uma)."""
    import importlib
    awp = importlib.import_module('armas.awp')
    ctx = C['ctx']
    soqs = list(bpy.data.collections['soquetes'].objects)
    t0 = time.time()
    pega, rel, problemas = EP.resolver(ctx, C['mao'], C['bracos'], C['perto'], soqs, getattr(awp, 'EMPUNHADURA', None),
                                       awp.lacos_dos_furos(ctx['ficha']))
    print('RESOLVER', round(time.time() - t0, 1), 's')
    print('RELATORIO', json.dumps(rel, ensure_ascii=False, default=str))
    print('PROBLEMAS', json.dumps(problemas, ensure_ascii=False))
    C['pega'] = pega
    for lado, quais in (('d', vistas_d), ('e', vistas_e)):
        if quais and lado in pega:
            dados = pega[lado]
            f = {'m': type('Pose', (), {'pose': staticmethod(lambda d=dados: d['pose'])})(),
                 'na': type('Encaixe', (), {'encaixe': dados['encaixe']})()}
            renders(f, lado, dados['palma'], f'{nome}_{lado}', quais)
    return pega, rel, problemas


# ------------------------------------------------------------------------------------------------ vistas
# (posição da câmera a partir do soquete da mão, alvo a partir dele; metros, referencial da arma), lente
VISTAS = {
    'd': {'dir': ((0.0, -0.32, 0.02), (0.0, 0.0, 0.0), 50), 'esq': ((0.0, 0.32, 0.02), (0.0, 0.0, 0.0), 50),
          'baixo': ((0.04, -0.06, -0.32), (0.0, 0.0, 0.0), 50), 'tras': ((-0.22, -0.14, 0.16), (0.02, 0.0, 0.0), 45),
          'cima': ((0.0, -0.04, 0.34), (0.0, 0.0, 0.0), 50), 'esqbaixo': ((0.05, 0.28, -0.14), (0.0, 0.0, 0.0), 50)},
    'e': {'fora': ((0.0, 0.34, -0.02), (0.0, 0.0, -0.03), 50), 'baixo': ((0.03, 0.10, -0.34), (0.0, 0.0, -0.03), 50),
          'cima': ((0.02, 0.06, 0.34), (0.0, 0.0, -0.02), 50),
          'jogador': (tuple(0.45 * c for c in DO_JOGADOR), (0.0, 0.0, -0.03), 50),
          'dir': ((0.0, -0.34, -0.02), (0.0, 0.0, -0.03), 50), 'frente': ((0.30, 0.10, -0.06), (0.0, 0.0, -0.03), 50)},
}


def renders(f, lado, afundar, nome, quais):
    """A luva posada (o afundamento da palma junto) na arma cinza, renders rápidos no Workbench."""
    sc = bpy.context.scene
    sc.render.engine = 'BLENDER_WORKBENCH'
    sc.display.shading.light = 'STUDIO'
    sc.display.shading.color_type = 'OBJECT'
    sc.display.shading.show_cavity = True
    sc.display.shading.show_shadows = False
    sc.render.resolution_x, sc.render.resolution_y = 960, 720
    sc.render.film_transparent = False
    os.makedirs(RENDERS, exist_ok=True)
    col = colecao('maos_da_prova')
    for o in list(col.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    for c in bpy.context.scene.collection.children:
        c.hide_render = c.name not in ('perto', 'maos_da_prova')
    for o in C['perto'].values():
        o.color = (0.55, 0.57, 0.6, 1.0)
        o.hide_render = False
    luva, rig = C['bracos'][lado]
    modelo = maos_correcoes.Modelo(luva, rig, C['mao'], luvas.REFORCO)
    ob = modelo.para_malha(f'prova_{lado}', col, f['m'].pose(), {'vertices': afundar['vertices'],
                                                                  'vetores': afundar['vetores']})
    e = f['na'].encaixe.copy()
    e.translation = e.translation * S
    ob.matrix_world = e
    ob.color = (0.62, 0.42, 0.25, 1.0) if lado == 'd' else (0.30, 0.45, 0.62, 1.0)
    ob.hide_render = False
    maos_rig.posar(rig, {})
    c = C['soqs'][f"mao_{lado}"].matrix_world.translation.copy()
    for vista in quais.split(','):
        pos, alvo, lente = VISTAS[lado][vista]
        cam = bpy.data.objects.get(f'cam_{vista}')
        if cam is None:
            cam = bpy.data.objects.new(f'cam_{vista}', bpy.data.cameras.new(f'cam_{vista}'))
            sc.collection.objects.link(cam)
        p, a = c + Vector(pos), c + Vector(alvo)
        cam.location = p
        cam.rotation_euler = (a - p).to_track_quat('-Z', 'Y').to_euler()
        cam.data.lens = lente
        cam.data.clip_start = 0.002
        sc.camera = cam
        sc.render.filepath = os.path.join(RENDERS, f'{nome}_{vista}.png')
        bpy.ops.render.render(write_still=True)
    print('VISTAS', nome, quais, flush=True)
