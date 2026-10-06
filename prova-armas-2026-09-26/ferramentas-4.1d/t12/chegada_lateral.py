# Tarefa 12 (a regra lateral): a prova do bloco (provas_lateral.py) com outra chegada da palma (o CHEGADA do ambiente,
# mm), com AFASTADO=0 sem o polegar afastado na chegada e com PESO=<mm² por mm> outro peso do lado do polegar 'baixo',
# sem as vistas (para não trocar as da pega da regra): confere se os 60 mm e o `polegar_afastado` da LATERAL ainda fazem
# diferença (na mão chata, a pega da regra passa sem os dois) e o que o peso do lado muda no polegar.
#   CHEGADA=60 [AFASTADO=0] [PESO=20] blender -b --factory-startup --python-exit-code 1 -P chegada_lateral.py --
#   <contexto das luvas> <pegas...>
import os
import sys

ARMAS = 'C:/Users/T-Gamer/Desktop/game tiro/trabalho-4.1d/tools/blender/armas'
sys.path.insert(0, os.path.dirname(ARMAS))

from armas import empunhadura_regras as regras  # noqa: E402

regras.LATERAL['chegada'] = (float(os.environ['CHEGADA']), 60.0)
if os.environ.get('AFASTADO') == '0':
    regras.LATERAL['polegar_afastado'] = False
if os.environ.get('PESO'):
    regras.LATERAL['polegar'] = dict(regras.LATERAL['polegar'], peso=float(os.environ['PESO']))
print('MASSACRE-CHEGADA', regras.LATERAL['chegada'], regras.LATERAL['polegar_afastado'], regras.LATERAL['polegar'],
      flush=True)
fonte = open(ARMAS + '/provas_lateral.py', encoding='utf-8').read().rstrip()
assert fonte.endswith('\nprincipal()')
g = {'__file__': ARMAS + '/provas_lateral.py', '__name__': 'provas_lateral_chegada'}
exec(compile(fonte[:-len('principal()')], ARMAS + '/provas_lateral.py', 'exec'), g)
g['vistas'] = lambda *a: None
g['principal']()
