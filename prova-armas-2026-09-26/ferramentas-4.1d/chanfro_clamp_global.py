# O "clamp overlap" do chanfro do Blender é global: a menor folga de uma peça reduz o chanfro dela inteira. Para cada
# peça (não cortador) de uma arma no nível pedido, a pilha até o chanfro avaliada com o clamp e sem ele: os vértices que
# mudam dizem que o chanfro foi reduzido; o fator é a razão entre os deslocamentos dos vértices do chanfro.
# Uso: blender -b --factory-startup -P chanfro_clamp.py -- <arma> <nivel> [nome da peça]
import importlib
import json
import sys

sys.path.insert(0, r'C:\Users\T-Gamer\Desktop\game tiro\trabalho-4.1d\tools\blender')
import bmesh  # noqa: E402
import bpy  # noqa: E402
from mathutils import kdtree  # noqa: E402

from armas import pecas  # noqa: E402
pecas.chanfro_local = lambda: None
from armas.unidades import S  # noqa: E402

a = sys.argv[sys.argv.index('--') + 1:]
ARMA, NIVEL = a[0], a[1]
SO = ' '.join(a[2:]) or None
mod = importlib.import_module(f'armas.{ARMA}')
ficha = json.load(open(rf'C:\Users\T-Gamer\Desktop\game tiro\trabalho-4.1d\tools\blender\refs\{ARMA}.json', encoding='utf-8'))
bpy.ops.wm.read_factory_settings(use_empty=True)


class Materiais(dict):
    """Um material por nome pedido: as zonas (as da 4.1d) e os nomes da AK e das outras da 4.1c (aco, aco_detalhes,
    madeira...). O material não muda a geometria do chanfro."""

    def __missing__(self, k):
        return self.setdefault(k, bpy.data.materials.new(k))


M = Materiais({z: bpy.data.materials.new(z) for z in ("corpo", "guarnicao", "carregador", "detalhes", "interno", "municao",
                                                     "vidro")})
col = pecas.iniciar(NIVEL, NIVEL)
mod.construir(ficha, M)
pecas.finalizar(col)


def avaliar(ob):
    dg = bpy.context.evaluated_depsgraph_get()
    me = ob.evaluated_get(dg).to_mesh()
    vs = [v.co.copy() for v in me.vertices]
    ob.evaluated_get(dg).to_mesh_clear()
    return vs


reduzidas = []
for ob in sorted(col.objects, key=lambda o: o.name):
    if ob.type != 'MESH' or ob.get('cortador') or (SO and ob.name != SO):
        continue
    pilha = list(ob.modifiers)
    ch = next((m for m in pilha if m.type == 'BEVEL'), None)
    if ch is None:
        continue
    vis = [m.show_viewport for m in pilha]
    depois = False
    for m in pilha:
        if depois:
            m.show_viewport = False
        if m is ch:
            depois = True
    # antes do chanfro (a entrada)
    ch.show_viewport = False
    antes = avaliar(ob)
    ch.show_viewport = True
    com = avaliar(ob)
    ch.use_clamp_overlap = False
    sem = avaliar(ob)
    ch.use_clamp_overlap = True
    for m, v in zip(pilha, vis):
        m.show_viewport = v
    largura = ch.width / S
    if len(com) != len(sem):
        print(f'  {ob.name}: topologia diferente com e sem o clamp ({len(com)} × {len(sem)})', flush=True)
        continue
    # o deslocamento de cada vértice da saída até o vértice da entrada mais perto, com e sem o clamp
    kd = kdtree.KDTree(len(antes))
    for i, v in enumerate(antes):
        kd.insert(v, i)
    kd.balance()
    razoes = []
    for vc, vs_ in zip(com, sem):
        ds = (vs_ - kd.find(vs_)[0]).length / S
        if ds > 0.2 * largura:
            dc = (vc - kd.find(vc)[0]).length / S
            razoes.append(dc / ds)
    dif = max(((c - s).length / S for c, s in zip(com, sem)), default=0.0)
    if dif < 1e-5:
        continue
    razoes.sort()
    f = razoes[len(razoes) // 2] if razoes else float('nan')
    reduzidas.append((ob.name, largura, f, dif))
    print(f'  {ob.name}: chanfro {largura:.3f} mm reduzido; fator mediano {f:.3f} (≈ {largura * f:.4f} mm); maior diferença {dif:.4f}',
          flush=True)
print('peças com o chanfro reduzido:', len(reduzidas), flush=True)
