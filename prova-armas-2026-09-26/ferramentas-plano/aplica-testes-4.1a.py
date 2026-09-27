# Como o aplica-4.1a.py, mas só grava blocos e pares de arquivos com o prefixo pedido (tests/ por padrão), para ver o
# teste falhar antes da implementação. Uso: python3 aplica-testes-4.1a.py <plano.md> <raiz> <tarefa> <tarefa> [prefixo]
import pathlib
import re
import sys

plano = pathlib.Path(sys.argv[1]).read_text(encoding='utf-8').replace('\r\n', '\n').split('\n')
raiz = pathlib.Path(sys.argv[2])
de, ate = int(sys.argv[3]), int(sys.argv[4])
prefixo = sys.argv[5] if len(sys.argv) > 5 else 'tests/'

RE_TAREFA = re.compile(r'^### Tarefa (\d+):')
RE_ARQ = re.compile(r'^```[a-z]+ file=(\S+)\s*$')
RE_PAR = re.compile(r'[Ee]m `([^`]+)`, trocar:\s*$')
RE_TROCAR = re.compile(r'^(?:e )?trocar(?: \([^)]*\))?:\s*$')
RE_FENCE = re.compile(r'^```[a-z]*\s*$')
RE_RM = re.compile(r'(?:^|&& )rm (\S+)\s*$')

tarefa = -1
atual = None  # arquivo dos pares
i = 0
erros = 0
n_arq = n_par = n_rm = 0


def bloco(i):
    """Lê o bloco cercado que começa na linha i (a cerca); devolve (texto, índice depois da cerca de fechar)."""
    assert RE_FENCE.match(plano[i]) or RE_ARQ.match(plano[i]), plano[i]
    j = i + 1
    linhas = []
    while plano[j] != '```':
        linhas.append(plano[j])
        j += 1
    return '\n'.join(linhas), j + 1


def pula_vazias(i):
    while plano[i].strip() == '':
        i += 1
    return i


while i < len(plano):
    l = plano[i]
    m = RE_TAREFA.match(l)
    if m:
        tarefa = int(m.group(1))
        atual = None
        i += 1
        continue
    ativa = de <= tarefa <= ate
    m = RE_ARQ.match(l)
    if m:
        texto, i = bloco(i)
        if ativa and m.group(1).startswith(prefixo):
            destino = raiz / m.group(1)
            destino.parent.mkdir(parents=True, exist_ok=True)
            destino.write_text(texto + '\n', encoding='utf-8', newline='\n')
            n_arq += 1
        continue
    if l.startswith('```bash'):
        texto, i = bloco(i)
        if False:  # os `rm` ficam para o aplica.py da tarefa inteira
            for linha in texto.split('\n'):
                mr = RE_RM.search(linha)
                if mr and 'rm -rf' not in linha:
                    alvo = raiz / mr.group(1)
                    if alvo.exists():
                        alvo.unlink()
                        n_rm += 1
                    else:
                        print(f'  [T{tarefa}] rm: {mr.group(1)} não existe')
        continue
    m = RE_PAR.search(l)
    if m or (RE_TROCAR.match(l) and atual):
        if m:
            atual = m.group(1)
        j = pula_vazias(i + 1)
        velho, j = bloco(j)
        j = pula_vazias(j)
        assert plano[j].strip() == 'por:', (tarefa, atual, plano[j])
        j = pula_vazias(j + 1)
        novo, j = bloco(j)
        i = j
        if ativa and atual.startswith(prefixo):
            f = raiz / atual
            if not f.exists():
                print(f'  [T{tarefa}] ERRO: {atual} não existe')
                erros += 1
                continue
            t = f.read_text(encoding='utf-8').replace('\r\n', '\n')
            n = t.count(velho)
            if n != 1:
                print(f'  [T{tarefa}] ERRO: trecho aparece {n} vezes em {atual}:\n    {velho[:160]!r}')
                erros += 1
                continue
            f.write_text(t.replace(velho, novo, 1), encoding='utf-8', newline='\n')
            n_par += 1
        continue
    i += 1

print(f'tarefas {de}–{ate}: {n_arq} arquivos, {n_par} pares, {n_rm} remoções, {erros} erros')
sys.exit(1 if erros else 0)
