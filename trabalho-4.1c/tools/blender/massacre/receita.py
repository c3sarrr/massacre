"""Receita de arma de massinha (src/data/armas/<id>.js) do lado do Blender (Fase 4.1; docs/phases/phase-4.md,
seção 4.1, "Receita" e "Blender").

Ler: o corpo é JSON puro depois de `export default` (o primeiro `{`), com o comentário de cabeçalho em cima.
Gravar: o formato canônico, byte a byte igual ao dos geradores (números arredondados a 4 casas como o Math.round do
JavaScript e escritos como o String() do JavaScript; a ordem das chaves das peças fixa). Assim a ida e volta sem
edição devolve o mesmo arquivo — a prova do caminho do Blender.
"""

import json
import math

PART_KEYS = (
    'name', 'group', 'mat', 'shape', 'op', 'thin', 'pos', 'rot', 'size', 'r', 'h', 'round', 'a', 'b', 'ra', 'rb',
    'radii', 'R', 'r1', 'r2', 'corner', 'closed', 'points', 'k', 'crease',
)


def ler(caminho):
    """Lê a receita e o cabeçalho (as linhas de comentário antes de `export default`, sem o `// `)."""
    with open(caminho, encoding='utf-8') as f:
        texto = f.read()
    i = texto.find('export default')
    if i < 0:
        raise ValueError(f'{caminho}: falta o `export default`')
    j = texto.find('{', i)
    if j < 0:
        raise ValueError(f'{caminho}: falta o `{{` do corpo')
    receita, _ = json.JSONDecoder().raw_decode(texto[j:])
    cabecalho = [linha[3:] if linha.startswith('// ') else linha[2:] for linha in texto[:i].splitlines() if linha.startswith('//')]
    return receita, cabecalho


def arredonda(v):
    """Math.round(v * 1e4) / 1e4 do JavaScript (meio para cima, também nos negativos)."""
    return math.floor(v * 1e4 + 0.5) / 1e4


def numero(v):
    """Número como o String() do JavaScript depois de arredondar: inteiros sem `.0`, sem `-0`."""
    r = arredonda(float(v))
    if r == 0:
        return '0'
    if r == int(r) and abs(r) < 1e15:
        return str(int(r))
    return repr(r)


def valor(v):
    """Um valor no formato canônico (o `value()` dos geradores)."""
    if isinstance(v, bool):
        return 'true' if v else 'false'
    if v is None:
        return 'null'
    if isinstance(v, (int, float)):
        return numero(v)
    if isinstance(v, (list, tuple)):
        return '[' + ', '.join(valor(x) for x in v) + ']'
    if isinstance(v, dict):
        return '{ ' + ', '.join(f'{json.dumps(k, ensure_ascii=False)}: {valor(x)}' for k, x in v.items()) + ' }'
    return json.dumps(v, ensure_ascii=False)


def formatar(receita, cabecalho):
    """A receita inteira no formato canônico (o `formatRecipe()` dos geradores)."""
    linhas = [f'// {linha}' for linha in cabecalho]
    linhas.append('export default {')
    linhas.append(f'  "id": {json.dumps(receita["id"], ensure_ascii=False)},')
    linhas.append(f'  "version": {receita["version"]},')
    linhas.append(f'  "refs": {valor(receita["refs"])},')
    linhas.append(f'  "materials": {valor(receita["materials"])},')
    if receita.get('soft'):
        linhas.append(f'  "soft": {valor(receita["soft"])},')
    linhas.append('  "groups": {')
    linhas.append(',\n'.join(f'    {json.dumps(k)}: {valor(g)}' for k, g in receita['groups'].items()))
    linhas.append('  },')
    linhas.append('  "anchors": {')
    linhas.append(',\n'.join(f'    {json.dumps(k)}: {valor(a)}' for k, a in receita['anchors'].items()))
    linhas.append('  },')
    linhas.append('  "parts": [')
    pecas = []
    for p in receita['parts']:
        chaves = [k for k in PART_KEYS if k in p] + [k for k in p if k not in PART_KEYS]
        pecas.append('    { ' + ', '.join(f'{json.dumps(k)}: {valor(p[k])}' for k in chaves) + ' }')
    linhas.append(',\n'.join(pecas))
    linhas.append('  ]')
    linhas.append('};')
    return '\n'.join(linhas) + '\n'


def gravar(caminho, receita, cabecalho):
    with open(caminho, 'w', encoding='utf-8', newline='\n') as f:
        f.write(formatar(receita, cabecalho))
