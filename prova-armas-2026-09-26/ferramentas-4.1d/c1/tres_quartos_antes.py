# A conta de três quartos (validar.silhueta_tres_quartos) de uma .blend de conferência guardada, com a ficha que se
# pedir: o modelo de antes da C1 (a .blend da Tarefa 10) com a caixa da parte de cima de agora, para separar o que a C1
# mudou do que já estava lá. Só os nossos renders; a sobreposição vai para <saida>.
#   S:\blender.exe -b --factory-startup -P tres_quartos_antes.py -- <blend> <ficha.json> <saida>
import json
import os
import sys

sys.path.insert(0, r'C:\Users\T-Gamer\Desktop\game tiro\trabalho-4.1d\tools\blender')
import bpy  # noqa: E402

blend, caminho_ficha, saida = sys.argv[sys.argv.index('--') + 1:][:3]
bpy.ops.wm.open_mainfile(filepath=blend)
from armas import validar  # noqa: E402

ficha = json.load(open(caminho_ficha, encoding='utf-8'))
perto = [o for o in bpy.data.collections['perto'].all_objects if o.type == 'MESH']
os.makedirs(saida, exist_ok=True)
print('RESULTADO', json.dumps({'objetos': len(perto), **validar.silhueta_tres_quartos(perto, ficha, saida)}, ensure_ascii=False))
