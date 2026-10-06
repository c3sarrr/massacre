# Pré-construção de uma arma da 4.1d só no nível de jogo (sem assar): malha fechada, triângulos por peça e no perto,
# silhueta de lado (e de três quartos, onde a arma tem), medidas e fins de curso. Nada vai para o projeto.
# Uso: blender -b --factory-startup -P arma_previa.py -- <arma>
import importlib
import json
import os
import sys
import time

sys.path.insert(0, r'C:\Users\T-Gamer\Desktop\game tiro\trabalho-4.1d\tools\blender')
import bpy  # noqa: E402

from armas import fim_de_curso, lod, pecas, soquetes, validar  # noqa: E402

ARMA = sys.argv[sys.argv.index('--') + 1]
mod = importlib.import_module(f'armas.{ARMA}')
t0 = time.time()
SAIDA = os.path.join(os.path.dirname(os.path.abspath(__file__)), f'{ARMA}_previa')
os.makedirs(SAIDA, exist_ok=True)
ficha = json.load(open(rf'C:\Users\T-Gamer\Desktop\game tiro\trabalho-4.1d\tools\blender\refs\{ARMA}.json', encoding='utf-8'))
bpy.ops.wm.read_factory_settings(use_empty=True)
M = {z: bpy.data.materials.new(z) for z in ("corpo", "guarnicao", "carregador", "detalhes", "interno", "municao", "vidro")}
jogo = pecas.iniciar('jogo', 'jogo')
mod.construir(ficha, M)
pecas.finalizar(jogo)
print('construido', round(time.time() - t0, 1), flush=True)
objs = [o for o in jogo.objects if o.type == 'MESH' and not o.get('cortador')]
print('malha', json.dumps(validar.malha(objs), ensure_ascii=False), flush=True)
perto_objs = [o for o in objs if lod.no_nivel(o, 'perto')]
print('triangulos perto', lod.triangulos(perto_objs), flush=True)
print('maiores', sorted(((lod.triangulos([o]), o.name) for o in objs), reverse=True)[:12], flush=True)


def colecao(nome):
    col = bpy.data.collections.get(nome) or bpy.data.collections.new(nome)
    if col.name not in bpy.context.scene.collection.children:
        bpy.context.scene.collection.children.link(col)
    return col


perto = soquetes.juntar_pecas(jogo, colecao('perto'), 'perto', mod.pivos(ficha), lambda ob: lod.no_nivel(ob, 'perto'))
lista = [o for k, o in perto.items() if not k.startswith('_')]
print('silhueta', json.dumps(validar.silhueta(lista, ficha, SAIDA)), flush=True)
if hasattr(validar, 'silhueta_tres_quartos') and ficha.get('vistaTresQuartos'):
    print('tres quartos', json.dumps(validar.silhueta_tres_quartos(lista, ficha, SAIDA)), flush=True)
print('medidas', json.dumps(validar.medidas(lista, objs, mod.soquetes(ficha), ficha)), flush=True)
pecas_perto = {k: o for k, o in perto.items() if not k.startswith('_') and not soquetes.e_no_filho(k)}
print('declaracao', fim_de_curso.problemas_da_declaracao(pecas_perto), flush=True)
rel, p = fim_de_curso.fim_de_curso(pecas_perto, soquetes.nos_filhos(perto))
print('fim de curso', json.dumps(rel), p, flush=True)
print('fim', round(time.time() - t0, 1), flush=True)
