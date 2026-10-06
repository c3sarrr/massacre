# A coronha da AWP num nível (alto ou jogo) com o poço do carregador e o vão do retém: as arestas não manifold, as
# colisões (triângulos que se cruzam) e, nas caixas das bocas (awp_acao.caixas_das_bocas), o maior peso do chanfro e a
# largura que ele dá — com o teto de 0,6 mm (pecas.limitar_chanfro) a boca fica com 0,6, não os 3,5 da coronha.
#   S:\blender.exe -b --factory-startup -P coronha_cortes.py -- [alto|jogo]
import json
import sys

sys.path.insert(0, r'C:\Users\T-Gamer\Desktop\game tiro\trabalho-4.1d\tools\blender')
import bmesh  # noqa: E402
import bpy  # noqa: E402

from armas import awp, awp_acao, chanfro_local as CL, pecas  # noqa: E402
from armas.unidades import S  # noqa: E402

NIVEL = sys.argv[sys.argv.index('--') + 1] if '--' in sys.argv and len(sys.argv) > sys.argv.index('--') + 1 else 'alto'
ficha = json.load(open(r'C:\Users\T-Gamer\Desktop\game tiro\trabalho-4.1d\tools\blender\refs\awp.json', encoding='utf-8'))
bpy.ops.wm.read_factory_settings(use_empty=True)
M = {z: bpy.data.materials.new(z) for z in ("corpo", "guarnicao", "carregador", "detalhes", "interno", "municao", "vidro")}
col = pecas.iniciar(NIVEL, NIVEL)
pecas.chanfro_local()
cor = awp._coronha(ficha, M)
pecas.finalizar(col)
print('modificadores', [(m.name, getattr(m, 'solver', '')) for m in cor.modifiers], flush=True)


def mm(v):
    return tuple(round(c / S, 2) for c in (v.x, v.y, v.z))


bm = CL._malha_avaliada(cor)
nm = [(len(e.link_faces), mm((e.verts[0].co + e.verts[1].co) / 2)) for e in bm.edges if not e.is_manifold]
print('não manifold', len(nm), nm[:12], flush=True)
bm.free()
col_ = [mm(p) for p in CL._colisoes(cor)]
print('colisões', len(col_), col_[:9], flush=True)
# os pesos do chanfro gravados na malha (antes do chanfro) dentro das caixas das bocas
me = cor.data
camada = me.attributes.get(CL.CAMADA)
largura = cor.get('chanfro', (0.6, 3))[0]
for minimo, maximo in awp_acao.caixas_das_bocas(ficha):
    pesos = []
    for e in me.edges:
        a, b = (me.vertices[i].co for i in e.vertices)
        m = [(a[k] + b[k]) / 2 / S for k in range(3)]
        if all(minimo[k] <= m[k] <= maximo[k] for k in range(3)):
            pesos.append(camada.data[e.index].value)
    print('caixa', minimo, maximo, 'arestas', len(pesos), 'maior peso', round(max(pesos), 4) if pesos else None,
          'largura máx.', round(max(pesos) * largura, 3) if pesos else None, flush=True)
