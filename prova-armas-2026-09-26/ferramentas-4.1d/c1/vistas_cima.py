# Vistas de perto da parte de cima da P90 (a C1): as miras, a ponte, o trilho e as pernas, no modelo alto com os
# materiais de fábrica e a luz da conferência (estudio.py), para a revisão crítica. Só os nossos renders.
#   S:\blender.exe -b --factory-startup -P vistas_cima.py -- <p90.blend> <pasta>
import os
import sys

sys.path.insert(0, r'C:\Users\T-Gamer\Desktop\game tiro\trabalho-4.1d\tools\blender')
import bpy  # noqa: E402

blend, pasta = sys.argv[sys.argv.index('--') + 1:][:2]
bpy.ops.wm.open_mainfile(filepath=blend)
from armas import estudio  # noqa: E402

sc = bpy.context.scene
alto = bpy.data.collections['alto']
for col in sc.collection.children:
    col.hide_render = col is not alto
S = 0.001


def m(x, alto_mm, lado):
    """(x, alto, lado) da ficha em mm → o ponto do Blender em metros."""
    return (x * S, lado * S, alto_mm * S)


estudio.montar(m(-130.0, 60.0, 0.0))
estudio.render(1600, 900, 128)
# (nome, posição, alvo, lente): a câmera olhando o alvo, sem rolagem
VISTAS = [
    ('c1_parte_de_cima_esq', m(-40.0, 180.0, 330.0), m(-128.0, 82.0, 0.0), 70),
    ('c1_parte_de_cima_dir', m(-40.0, 180.0, -330.0), m(-128.0, 82.0, 0.0), 70),
    ('c1_mira_frente_esq', m(-40.0, 120.0, 150.0), m(-82.0, 92.0, 6.0), 90),
    ('c1_mira_tras_esq', m(-140.0, 128.0, 150.0), m(-176.0, 96.0, 6.0), 90),
    ('c1_mira_tras_atras', m(-330.0, 125.0, 40.0), m(-175.0, 108.0, 0.0), 90),
    ('c1_ponte_esq_baixo', m(-260.0, -60.0, 260.0), m(-150.0, 45.0, 0.0), 55),
    ('c1_ponte_tras_esq', m(-420.0, 150.0, 300.0), m(-170.0, 60.0, 0.0), 60),
    ('c1_cima', m(-140.0, 600.0, 0.0), m(-140.0, 60.0, 0.0), 60),
]
os.makedirs(pasta, exist_ok=True)
for nome, pos, alvo, lente in VISTAS:
    sc.camera = estudio.camera(nome, pos, alvo, lente)
    sc.render.filepath = os.path.join(pasta, f'{nome}.png')
    bpy.ops.render.render(write_still=True)
    print('VISTA', sc.render.filepath, flush=True)
