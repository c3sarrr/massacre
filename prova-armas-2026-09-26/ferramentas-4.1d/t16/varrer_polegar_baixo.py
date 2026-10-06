"""O polegar 'baixo' da mão lateral com a medida nova do lugar (a P90 da Tarefa 16: pela direção do eixo da distal em
volta da arma, o polegar de apoio que "subia pelo entalhe" fica a 81,8° do 'baixo', e não a 67,2° — a normal de uma das
cinco faces do vértice do pé do lóbulo, conforme a ordem da malha): a mão de apoio pelo banco (t14/pega_banco.py) sobre
uma .blend da conferência, com o `polegar` da regra em cada variante pedida (o `lado` e o `peso` do alvo) e, opcional,
a âncora e as giradas; para cada uma, os problemas, o lugar do polegar, os graus dele e a polpa.
    blender -b --factory-startup -P varrer_polegar_baixo.py -- <arma> <categoria> <.blend> <pasta> <variantes.json>
        [--direita]
O JSON é uma lista de {"nome", "correcoes"} (as chaves da regra da mão esquerda, como no B.mao).
"""
import json
import os
import sys

a = sys.argv[sys.argv.index('--') + 1:]
ARMA, CATEGORIA, BLEND, TRABALHO, VARIANTES = a[:5]
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 't14'))
import pega_banco as B  # noqa: E402

B.configurar(ARMA, CATEGORIA, trabalho=TRABALHO)
B.CFG['blend'] = BLEND
B.carregar()
if '--direita' in a:
    B.mao('d')
with open(VARIANTES, encoding='utf-8') as f:
    variantes = json.load(f)
for v in variantes:
    s = B.mao('e', v['correcoes'])
    lat = s.get('ladosLateral') or {}
    print('VARIANTE', json.dumps({'nome': v['nome'], 'problemas': s.get('problemas'), 'erro': s.get('erro'),
                                  'polegarGraus': lat.get('polegarGraus'), 'medias': lat.get('mediasGraus'),
                                  'polegar': (s.get('polegar') or {}).get('graus'),
                                  'contatos': s.get('contatosMM'), 'ponta': s.get('pontaDoPolegar'),
                                  'centroDistal': (s.get('centros') or {}).get('polegar_3'),
                                  'segundos': s.get('segundos')}, ensure_ascii=False), flush=True)
print('FIM', flush=True)
