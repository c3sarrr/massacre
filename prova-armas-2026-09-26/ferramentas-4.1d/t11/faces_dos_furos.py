# As faces da peça em volta de um furo da ficha, medidas na malha de jogo (o perto) da .blend que o construir grava, pela
# mesma conta do solver (empunhadura_furo.Furo: os raios do plano do meio, logo por fora do laço, até sair da peça):
# a espessura de verdade em volta do buraco do polegar da AWP (34 mm no punho, 52 em cima e atrás) e do oval de trás da
# P90 (39,5 a 42,5 mm) — de onde saiu a placa de 34 mm da prova do furo (Tarefa 11).
#   S:\blender.exe -b <trabalho-4.1d>\tools\blender\conferencia\<arma>\<arma>.blend --factory-startup -P faces_dos_furos.py -- <arma> <furo>
# Imprime RESULTADO {faces_medias, direita e esquerda (mín, máx), espessura (mín, máx), amostras [x, alto, direita,
# esquerda] a cada três}.
import sys, os, json
import numpy as np
RAIZ = r'C:\Users\T-Gamer\Desktop\game tiro\trabalho-4.1d'
sys.path.insert(0, os.path.join(RAIZ, 'tools', 'blender'))
import bpy
from armas import empunhadura_arma as EA, empunhadura_furo as EF
arma_id, furo_nome = sys.argv[sys.argv.index('--') + 1:][:2]
ficha = json.load(open(os.path.join(RAIZ, 'tools', 'blender', 'refs', f'{arma_id}.json'), encoding='utf-8'))
laco = ficha['buracos'][ficha['buracosNomes'].index(furo_nome)]
objs = [o for o in bpy.data.collections['perto'].objects if o.type == 'MESH']
print('OBJS', [o.name for o in objs])
arma = EA.Arma(objs)
f = EF.Furo(furo_nome, laco, arma)
fa = f.faces
print('RESULTADO', json.dumps({'faces_medias': [round(v, 2) for v in f.faces_medias],
      'direita': [round(float(fa[:, 0].min()), 1), round(float(fa[:, 0].max()), 1)],
      'esquerda': [round(float(fa[:, 1].min()), 1), round(float(fa[:, 1].max()), 1)],
      'espessura': [round(float((fa[:, 1] - fa[:, 0]).min()), 1), round(float((fa[:, 1] - fa[:, 0]).max()), 1)],
      'amostras': [[round(float(x), 1), round(float(z), 1), round(float(d), 1), round(float(e), 1)]
                   for (x, z), (d, e) in zip(f.amostras, fa)][::3]}))
