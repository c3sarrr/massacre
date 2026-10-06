"""Como o chanfro do Blender (o modificador, limite por peso, como o acabamento das armas) trata uma aresta longa dividida
em pedaços em linha com pesos diferentes (a pergunta da Tarefa 16: dá para reduzir o chanfro só perto do canto em que
ele se dobra, e não na aresta inteira?): uma barra de 100 × 20 × 20 mm com a aresta de cima da frente dividida, pesos em
degraus ou em rampa, e a largura do chanfro medida ao longo dela (a distância da aresta de cima até onde a face de cima
deixa de ser plana, em fatias de x). Imprime as larguras por x e salva uma vista (Workbench) de cima e de três quartos.
    blender -b --factory-startup -P taper.py -- <pasta de saída>
"""
import math
import os
import sys

import bmesh
import bpy
from mathutils import Vector

SAIDA = sys.argv[sys.argv.index('--') + 1]
os.makedirs(SAIDA, exist_ok=True)
S = 0.001  # 1 mm em unidades do Blender (m)
LARGURA = 3.0  # mm


def barra(nome, divisoes, pesos, x0=0.0):
    """A barra com a aresta de cima da frente (y = -10, z = 10) cortada nos x de `divisoes` (mm), com os `pesos` de
    cada pedaço (um a mais que as divisões); as outras arestas de cima com peso 1, as de baixo e as verticais sem."""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    # a camada antes das divisões: criar uma camada refaz os dados e invalida as arestas guardadas
    camada = bm.edges.layers.float.new('bevel_weight_edge')
    for v in bm.verts:
        v.co = Vector((v.co.x * 100 + 50 + x0, v.co.y * 20, v.co.z * 20)) * S
    bm.edges.ensure_lookup_table()
    alvo = next(e for e in bm.edges if all(abs(v.co.y + 0.010) < 1e-9 and abs(v.co.z - 0.010) < 1e-9 for v in e.verts))
    a = min(alvo.verts, key=lambda v: v.co.x)
    feitos = []
    e = alvo
    origem = a
    for xd in divisoes:
        outra = e.other_vert(origem)
        fac = (xd * S + x0 * S - origem.co.x) / (outra.co.x - origem.co.x)
        ne, nv = bmesh.utils.edge_split(e, origem, fac)
        # o pedaço de `origem` até `nv` é o que ficou para trás
        tras = ne if origem in ne.verts else e
        frente = e if tras is ne else ne
        feitos.append(tras)
        e, origem = frente, nv
    feitos.append(e)
    for ed in bm.edges:
        cima = all(abs(v.co.z - 0.010) < 1e-9 for v in ed.verts)
        ed[camada] = 1.0 if cima else 0.0
    for ed, w in zip(feitos, pesos):
        ed[camada] = w
    me = bpy.data.meshes.new(nome)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(nome, me)
    bpy.context.scene.collection.objects.link(ob)
    m = ob.modifiers.new('chanfro', 'BEVEL')
    m.width = LARGURA * S
    m.segments = 2
    m.limit_method = 'WEIGHT'
    m.harden_normals = True
    m.miter_outer = 'MITER_ARC'
    m.use_clamp_overlap = True
    return ob


def larguras(ob, x0=0.0):
    """A largura do chanfro da aresta de cima da frente por fatia de x: na malha avaliada, o y mais à frente (menor) dos
    vértices da face de cima (z = 10 mm) perto de cada x, menos -10 mm."""
    dg = bpy.context.evaluated_depsgraph_get()
    me = ob.evaluated_get(dg).to_mesh()
    topo = [(v.co.x / S - x0, v.co.y / S) for v in me.vertices if abs(v.co.z / S - 10.0) < 1e-4]
    lado = [(v.co.x / S - x0, v.co.z / S) for v in me.vertices if abs(v.co.y / S + 10.0) < 1e-4]
    saida = []
    for x in (0, 2, 5, 8, 10, 12, 15, 20, 25, 30, 40, 50, 70, 99):
        ys = [y for xx, y in topo if abs(xx - x) < 0.6]
        zs = [z for xx, z in lado if abs(xx - x) < 0.6]
        saida.append((x, round(min(ys) + 10.0, 3) if ys else None, round(10.0 - max(zs), 3) if zs else None))
    ob.evaluated_get(dg).to_mesh_clear()
    return saida


bpy.ops.wm.read_factory_settings(use_empty=True)
casos = [
    ('inteira', [], [1.0]),
    ('degrau', [10.0], [0.2, 1.0]),
    ('rampa', [10.0, 14.0, 18.0, 22.0, 26.0], [0.2, 0.36, 0.52, 0.68, 0.84, 1.0]),
]
for i, (nome, divs, ps) in enumerate(casos):
    ob = barra(nome, divs, ps, x0=i * 150.0)
    print('LARGURAS', nome, larguras(ob, x0=i * 150.0), flush=True)

cena = bpy.context.scene
cena.render.engine = 'BLENDER_WORKBENCH'
cena.display.shading.light = 'STUDIO'
cena.display.shading.show_cavity = True
cena.display.shading.cavity_type = 'BOTH'
cena.render.resolution_x = 1400
cena.render.resolution_y = 500
cena.world = bpy.data.worlds.new('fundo')
cena.world.color = (0.18, 0.18, 0.2)
cam_dados = bpy.data.cameras.new('camera')
cam_dados.type = 'ORTHO'
cam = bpy.data.objects.new('camera', cam_dados)
cena.collection.objects.link(cam)
cena.camera = cam
for nome, de, alvo, escala in (('tres_quartos', Vector((0.5, -1.0, 0.8)), Vector((0.2, 0.0, 0.0)), 0.48),
                               ('perto_inteira', Vector((0.3, -1.0, 0.9)), Vector((0.02, -0.01, 0.01)), 0.07),
                               ('perto_degrau', Vector((0.3, -1.0, 0.9)), Vector((0.16, -0.01, 0.01)), 0.07),
                               ('perto_rampa', Vector((0.3, -1.0, 0.9)), Vector((0.318, -0.01, 0.01)), 0.07)):
    cam.location = alvo + de.normalized() * 2.0
    cam.rotation_euler = (-de).to_track_quat('-Z', 'Z').to_euler()
    cam_dados.ortho_scale = escala
    cena.render.filepath = os.path.join(SAIDA, f'taper_{nome}.png')
    bpy.ops.render.render(write_still=True)
print('FIM', flush=True)
