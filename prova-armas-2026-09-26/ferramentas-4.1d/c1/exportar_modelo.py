# Os triângulos do nível `perto` de uma arma do projeto (o .glb de assets/armas/<id>/), no referencial da ficha (mm: x a
# boca, alto, lado + esquerda), para os ajustes de câmera e de forma no navegador (c1/ajuste.html). Só a nossa malha.
# Uso: blender -b --factory-startup -P exportar_modelo.py -- <glb> <saida.json> <origem_x_mm>
import bpy, sys, json
args = sys.argv[sys.argv.index('--') + 1:]
glb, saida, ox = args[0], args[1], float(args[2])
PREFIXO = (args[3] if len(args) > 3 else 'perto') + '_'
U = 25.4  # mm por unidade do jogo
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=glb)
dg = bpy.context.evaluated_depsgraph_get()
pecas = {}
for o in bpy.context.scene.objects:
    if o.type != 'MESH' or not o.name.startswith(PREFIXO):
        continue
    ev = o.evaluated_get(dg)
    me = ev.to_mesh()
    me.calc_loop_triangles()
    M = ev.matrix_world
    vs = []
    for v in me.vertices:
        w = M @ v.co  # Blender (import do glTF: Y-up -> Z-up): x, y = -z do glTF, z = y do glTF
        # unidade do jogo -> mm da ficha: x = X*U + origem, alto = Z*U, lado = Y*U (o glTF +Z direita = -Y do Blender)
        vs.append((round(w.x * U + ox, 3), round(w.z * U, 3), round(w.y * U, 3)))
    tris = [list(t.vertices) for t in me.loop_triangles]
    pecas[o.name[len(PREFIXO):]] = {'v': vs, 't': tris}
    ev.to_mesh_clear()
json.dump(pecas, open(saida, 'w'))
print('EXPORTADO', {k: (len(p['v']), len(p['t'])) for k, p in pecas.items()})
