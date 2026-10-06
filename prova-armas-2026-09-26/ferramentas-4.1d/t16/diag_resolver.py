"""A pega inteira de uma arma pelo banco (t14/pega_banco.py, `resolver`: o caminho do construir, com o código da pega de
agora) sobre uma .blend da conferência com as luvas montadas — para conferir uma mudança do solver ou da validação nas
sete sem construir: os problemas e, de cada mão, o que a validação mede (ver RESUMO), e o JSON da pega (os graus de cada
osso de dedo, para o pega_json.py --comparar) em <pasta>/<rótulo>.pega.json.
    blender -b --factory-startup -P diag_resolver.py -- <arma> <categoria> <.blend> <pasta> <rótulo>
"""
import json
import math
import os
import sys

a = sys.argv[sys.argv.index('--') + 1:]
ARMA, CATEGORIA, BLEND, TRABALHO, ROTULO = a[:5]
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 't14'))
import pega_banco as B  # noqa: E402

B.configurar(ARMA, CATEGORIA, trabalho=TRABALHO)
B.CFG['blend'] = BLEND
B.carregar()
pega, rel, problemas = B.resolver()
emp = rel.get('empunhadura', rel)
CHAVES = ('palmaAndouMM', 'contatosMM', 'penetracaoMM', 'palmaMeioMM', 'indicador', 'polegar', 'ladosLateral',
          'polegarNoFuro', 'juntosMM', 'angulos')
for lado in ('d', 'e'):
    if lado in emp:
        print('RESUMO', lado, json.dumps({k: emp[lado].get(k) for k in CHAVES if k in emp[lado]}, ensure_ascii=False,
                                         default=str), flush=True)
print('PROBLEMAS', json.dumps(problemas, ensure_ascii=False), flush=True)
# os graus de cada osso de dedo (o quatérnio da pose, como o pega_json.py lê do .glb: o ângulo em graus em volta do eixo)
saida = {}
for lado, dados in pega.items():
    ossos = {}
    for osso, q in (dados.get('pose') or {}).items():
        try:
            w = max(-1.0, min(1.0, q.w if hasattr(q, 'w') else q[0]))
            ossos[osso] = round(math.degrees(2.0 * math.acos(abs(w))), 3)
        except (TypeError, IndexError, AttributeError):
            ossos[osso] = str(q)
    saida[lado] = ossos
with open(os.path.join(TRABALHO, f'{ROTULO}.pega.json'), 'w', encoding='utf-8') as f:
    json.dump(saida, f, ensure_ascii=False, indent=1)
print('FIM', flush=True)
