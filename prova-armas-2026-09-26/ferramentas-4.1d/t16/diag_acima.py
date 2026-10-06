"""A margem do solver do indicador indexado da pistola acima do alto do gatilho (a reprovação da Glock na Tarefa 16: o
dedo a 0,11 mm abaixo dele, com a margem do solver igual ao limite da validação, 0 mm, e o custo dela pequeno — 0,44
contra 45 do resto): a pega inteira pelo banco (t14/pega_banco.py, `resolver`, o caminho do construir) sobre uma .blend
da conferência com as luvas montadas, com a margem do solver (empunhadura_pega.INDEXADO_ACIMA_MM, a do `indexar`) em
cada valor pedido e a validação com o limite dela (empunhadura_validacao.INDEXADO_ACIMA_MM) — o indicador, os contatos
e os problemas de cada uma.
    blender -b --factory-startup -P diag_acima.py -- <arma> <categoria> <.blend> <pasta> <margens, mm: 0,0.5,1>
"""
import json
import os
import sys

a = sys.argv[sys.argv.index('--') + 1:]
ARMA, CATEGORIA, BLEND, TRABALHO, MARGENS = a[:5]
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 't14'))
import pega_banco as B  # noqa: E402

B.configurar(ARMA, CATEGORIA, trabalho=TRABALHO)
B.CFG['blend'] = BLEND
B.carregar()
for margem in (float(x) for x in MARGENS.split(',')):
    B.EP.INDEXADO_ACIMA_MM = margem
    pega, rel, problemas = B.resolver()
    emp = rel.get('empunhadura', rel)
    saida = {'margem': margem, 'problemas': problemas}
    for lado in ('d', 'e'):
        if lado in emp:
            saida[lado] = {k: emp[lado].get(k) for k in ('indicador', 'contatosMM', 'palmaAndouMM', 'penetracaoMM',
                                                         'polegar', 'palmaMeioMM')}
    print('MARGEM', json.dumps(saida, ensure_ascii=False, default=str), flush=True)
print('FIM', flush=True)
