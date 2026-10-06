# A sessão do Blender que fica aberta e executa os trabalhos da fila (<fila>/*.py), num espaço de nomes persistente (G):
# a arma e as luvas montadas uma vez, as variantes da pega em segundos (a 4.1c usou a mesma, para a Glock).
#   blender -b --factory-startup -P servidor.py -- <raiz do projeto> <pasta da fila>
# Cada trabalho é um .py: roda com exec no G, a saída (stdout e stderr) vai para <nome>.out ao lado; um trabalho que
# levanta exceção não derruba o servidor (o traceback vai para o .out). `_sair = True` (ou `G['_sair'] = True`: o
# espaço de nomes se enxerga como G) encerra.
import contextlib
import glob
import io
import os
import sys
import time
import traceback

args = sys.argv[sys.argv.index('--') + 1:]
RAIZ, FILA = args[0], args[1]
sys.path.insert(0, os.path.join(RAIZ, 'tools', 'blender'))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.makedirs(FILA, exist_ok=True)

G = {'__name__': 'servidor', 'RAIZ': RAIZ, 'FILA': FILA}
G['G'] = G  # o trabalho que escreve G['_sair'] (sem isso, o NameError ficava no .out e o servidor não saía)
print('SERVIDOR pronto', flush=True)
while not G.get('_sair'):
    trabalhos = sorted(glob.glob(os.path.join(FILA, '*.py')))
    if not trabalhos:
        time.sleep(0.25)
        continue
    arq = trabalhos[0]
    base = arq[:-3]
    with open(arq, encoding='utf-8') as f:
        codigo = f.read()
    os.replace(arq, base + '.rodando')
    saida = io.StringIO()
    t0 = time.time()
    with contextlib.redirect_stdout(saida), contextlib.redirect_stderr(saida):
        try:
            exec(compile(codigo, arq, 'exec'), G)
        except BaseException:  # noqa: BLE001 — o servidor não cai por um trabalho
            traceback.print_exc()
    texto = saida.getvalue() + f'\n[{time.time() - t0:.1f} s]\n'
    with open(base + '.tmp', 'w', encoding='utf-8') as f:
        f.write(texto)
    os.replace(base + '.tmp', base + '.out')
    os.replace(base + '.rodando', base + '.feito')  # o código do trabalho fica ao lado da saída (o registro)
    print('SERVIDOR feito', os.path.basename(base), flush=True)
