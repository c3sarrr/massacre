# A geometria do polegar da luva de jogo (a direita): o comprimento dos três ossos (o metacarpo, a falange proximal e a
# distal), os limites dos seis graus além do repouso (empunhadura_polegar.limites), o repouso da ficha, e as juntas, a
# palma e as falanges livres no referencial da luva (mm) no repouso, na pose afastada e na mão aberta da chegada.
# Foi daqui a conta da prova do furo (Tarefa 11): a proximal com 31,6 mm, a MCP 14 mm à frente da palma no repouso.
#   S:\blender.exe -b --factory-startup -P geometria_polegar.py -- <contexto das luvas.json>
import sys, os, json
RAIZ = r'C:\Users\T-Gamer\Desktop\game tiro\trabalho-4.1d'
sys.path.insert(0, os.path.join(RAIZ, 'tools', 'blender'))
import bpy
import numpy as np
from mathutils import Vector
from armas import empunhadura, empunhadura_polegar as polegar, empunhadura_arma as EA, luvas, maos, maos_rig, materiais
args = sys.argv[sys.argv.index('--') + 1:]
ctx = json.load(open(args[0], encoding='utf-8'))
bpy.ops.wm.read_factory_settings(use_empty=True)
colecao = bpy.data.collections.new('g')
bpy.context.scene.collection.children.link(colecao)
mao = maos.Mao(ctx['ficha'])
luva, rig, _ = luvas.montar_jogo(mao, materiais.materiais_das_luvas(ctx['pinturas']['massaCrua']), colecao)
col = empunhadura.Colisor(luva, rig, mao, luvas.REFORCO)
cad = polegar.Cadeia(col, mao, {})
lim = polegar.limites(mao)
print('COMP', [round(c, 1) for c in cad.comp])
print('LIM', {k: [round(a, 1), round(b, 1)] for k, (a, b) in lim.items()})
print('REP', {k: v for k, v in mao.rep.items() if k.startswith('polegar')})
def info(nome, m):
    pts = np.array(col.modelo.pontos(m.pose()))
    dono = np.array(col.dono)
    palma = pts[dono == 'mao']
    juntas = {}
    maos_rig.posar(rig, m.pose())
    for o in ('polegar_1', 'polegar_2', 'polegar_3', 'indicador_1', 'medio_1'):
        pb = rig.pose.bones[f'{o}_{col.lado}']
        juntas[o] = [round(v / 0.001 if False else v, 1) for v in (Vector(pb.head) * 1000.0)]
    maos_rig.posar(rig, {})
    pol = pts[np.isin(dono, polegar.LIVRE)]
    ponta = pol[pol[:, 0].argmax()] if False else None
    print('POSE', nome, json.dumps({'juntas': juntas, 'palma_z': [round(float(palma[:, 2].min()), 1), round(float(palma[:, 2].max()), 1)],
          'palma_x': [round(float(palma[:, 0].min()), 1), round(float(palma[:, 0].max()), 1)],
          'palma_y': [round(float(palma[:, 1].min()), 1), round(float(palma[:, 1].max()), 1)],
          'polegar_livre_min': [round(float(v), 1) for v in pol.min(0)], 'polegar_livre_max': [round(float(v), 1) for v in pol.max(0)]}))
m0 = empunhadura.Mao()
info('repouso', m0)
info('afastar', polegar.afastar(col, mao, m0))
info('aberta_afastar', EA.mao_aberta(mao, polegar.afastar(col, mao, m0)))
print('SCALE S', polegar.S if hasattr(polegar, 'S') else None)
