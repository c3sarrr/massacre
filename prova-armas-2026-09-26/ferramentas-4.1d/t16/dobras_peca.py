"""Os cruzamentos de uma peça (triângulos que se cortam) em cada etapa da pilha do acabamento, construída como o
construir faz (chanfro local quando a arma o liga), num nível: sem o chanfro (o que os booleanos de antes deixam), com
o chanfro sem os cortes finais, e com tudo. Para cada cruzamento final: onde está, o segmento comum, a distância ao
cruzamento mais perto de antes do chanfro (o desdobrar ignora os que ficam a menos de COLISAO_ANTES dele) e as arestas
chanfradas em volta (o peso, o comprimento, o ângulo entre as faces).
    blender -b --factory-startup -P dobras_peca.py -- <arma> <nivel> <peça> [<peça> ...]
"""
import importlib
import json
import math
import sys

sys.path.insert(0, r'C:\Users\T-Gamer\Desktop\game tiro\trabalho-4.1d\tools\blender')
import bmesh  # noqa: E402
import bpy  # noqa: E402
from mathutils.bvhtree import BVHTree  # noqa: E402

from armas import chanfro_local as CL  # noqa: E402
from armas import pecas  # noqa: E402
from armas.unidades import S  # noqa: E402

a = sys.argv[sys.argv.index('--') + 1:]
ARMA, NIVEL, NOMES = a[0], a[1], a[2:]
mod = importlib.import_module(f'armas.{ARMA}')
ficha = json.load(open(rf'C:\Users\T-Gamer\Desktop\game tiro\trabalho-4.1d\tools\blender\refs\{ARMA}.json',
                       encoding='utf-8'))
bpy.ops.wm.read_factory_settings(use_empty=True)


class Materiais(dict):
    def __missing__(self, k):
        return self.setdefault(k, bpy.data.materials.new(k))


def cruzamentos(ob):
    """Os pares de triângulos que se cortam (segmento comum acima de CL.CRUZA_MIN) na malha avaliada: o meio (mm), o
    segmento (mm), as normais e as áreas dos dois."""
    bm = CL._malha_avaliada(ob)
    bm.transform(ob.matrix_world)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    bm.faces.ensure_lookup_table()
    bm.normal_update()
    saida = []
    if bm.faces:
        arvore = BVHTree.FromBMesh(bm, epsilon=0.0)
        for i, j in arvore.overlap(arvore):
            fi, fj = bm.faces[i], bm.faces[j]
            if i < j and not (set(fi.verts) & set(fj.verts)):
                seg = CL.segmento_comum(fi, fj)
                if seg > CL.CRUZA_MIN * S:
                    meio = sum((v.co for f in (fi, fj) for v in f.verts), fi.verts[0].co * 0) / 6 / S
                    saida.append({'meio': [round(c, 3) for c in meio], 'segmentoMM': round(seg / S, 4),
                                  'normais': [[round(c, 3) for c in f.normal] for f in (fi, fj)],
                                  'areasMM2': [round(f.calc_area() / S / S, 4) for f in (fi, fj)]})
    bm.free()
    return saida


def mostrar(ob, nome_mod, ligado):
    for m in ob.modifiers:
        if m.name == nome_mod or (nome_mod == 'corte final' and m.name.startswith('corte final')):
            m.show_viewport = ligado


M = Materiais()
col = pecas.iniciar(NIVEL, NIVEL)
mod.construir(ficha, M)
pecas.finalizar(col)
for nome in NOMES:
    ob = bpy.data.objects[nome]
    pilha = [(m.name, m.type) for m in ob.modifiers]
    ch = ob.modifiers.get('chanfro')
    mostrar(ob, 'corte final', False)
    if ch:
        ch.show_viewport = False
    sem = cruzamentos(ob)
    if ch:
        ch.show_viewport = True
    com_chanfro = cruzamentos(ob)
    mostrar(ob, 'corte final', True)
    tudo = cruzamentos(ob)
    # as arestas chanfradas em volta de cada cruzamento final (na malha de entrada do chanfro, com os pesos)
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bm.transform(ob.matrix_world)
    camada = bm.edges.layers.float.get(CL.CAMADA)
    largura = ch.width / S if ch else 0.0
    for c in tudo:
        p = c['meio']
        perto_antes = min((math.dist(p, s['meio']) for s in sem), default=None)
        c['antesMaisPertoMM'] = None if perto_antes is None else round(perto_antes, 3)
        arestas = []
        for e in bm.edges:
            u, v = e.verts[0].co / S, e.verts[1].co / S
            meio = (u + v) / 2
            if math.dist(meio, p) <= 4.0:
                w = e[camada] if camada else None
                ang = math.degrees(e.calc_face_angle(0.0)) if len(e.link_faces) == 2 else None
                arestas.append({'de': [round(x, 2) for x in u], 'a': [round(x, 2) for x in v],
                                'mm': round(e.calc_length() / S, 3), 'peso': None if w is None else round(w, 4),
                                'chanfroMM': None if w is None else round(w * largura, 4),
                                'angulo': None if ang is None else round(ang, 1), 'faces': len(e.link_faces)})
        arestas.sort(key=lambda d: -(d['chanfroMM'] or 0))
        c['arestas'] = arestas[:14]
    bm.free()
    print('DOBRAS', nome, json.dumps({'pilha': pilha, 'larguraMM': round(largura, 4), 'semChanfro': sem,
                                      'comChanfro': len(com_chanfro), 'tudo': tudo}, ensure_ascii=False), flush=True)
