# Executor do plano executado da 4.1c (docs/phases/phase-4.1c-plan.md): aplica o plano numa cópia do projeto, tarefa
# por tarefa — os blocos `file=` (o arquivo inteiro), os pares "Em `x`, trocar: … por: …", os blocos `json chaves=`
# (as chaves novas no fim de um JSON de uma linha, o do JSON.stringify), e nos blocos bash os `rm <arquivo>` e o
# `node tools/moodboard.mjs` (o moodboard.html sai dele). As cercas têm três crases ou mais: um bloco fecha na linha
# com as mesmas crases da cerca que o abriu (o arquivo com ``` dentro vai numa cerca de quatro); o `sem-quebra` depois
# do `file=` grava o arquivo sem a quebra de linha no fim (as fichas que a régua grava). Não roda o Blender
# nem os testes (o valida-4.1c.sh roda). Arquivos gravados com LF.
# Com um prefixo (o quinto argumento, por exemplo tests/), só grava os blocos e os pares dos arquivos com ele — os
# testes da tarefa antes da implementação, para vê-los falhar.
# Uso: python3 aplica-4.1c.py <plano.md> <raiz da cópia> <primeira tarefa> <última tarefa> [prefixo]
import json
import pathlib
import re
import subprocess
import sys

plano = pathlib.Path(sys.argv[1]).read_text(encoding='utf-8').replace('\r\n', '\n').split('\n')
raiz = pathlib.Path(sys.argv[2])
de, ate = int(sys.argv[3]), int(sys.argv[4])
prefixo = sys.argv[5] if len(sys.argv) > 5 else None

RE_TAREFA = re.compile(r'^### Tarefa (\d+):')
RE_CERCA = re.compile(r'^(`{3,})([a-z]*)(?: (file|chaves)=(\S+))?( sem-quebra)?\s*$')
RE_PAR = re.compile(r'[Ee]m `([^`]+)`, trocar:\s*$')
RE_RM = re.compile(r'^rm (\S+)\s*$')
COMANDOS = {'node tools/moodboard.mjs'}

tarefa = -1
i = 0
erros = 0
n_arq = n_par = n_rm = n_json = n_cmd = 0


def bloco(i):
    """Lê o bloco cercado que começa na linha i (a cerca); devolve (texto, tipo, índice depois da cerca de fechar)."""
    m = RE_CERCA.match(plano[i])
    assert m, plano[i]
    crases = m.group(1)
    j = i + 1
    linhas = []
    while plano[j] != crases:
        linhas.append(plano[j])
        j += 1
    return '\n'.join(linhas), m, j + 1


def pula_vazias(i):
    while plano[i].strip() == '':
        i += 1
    return i


def vale(caminho):
    return prefixo is None or caminho.startswith(prefixo)


while i < len(plano):
    linha = plano[i]
    m = RE_TAREFA.match(linha)
    if m:
        tarefa = int(m.group(1))
        i += 1
        continue
    ativa = de <= tarefa <= ate
    m = RE_PAR.search(linha)
    if m:
        atual = m.group(1)
        j = pula_vazias(i + 1)
        velho, _, j = bloco(j)
        j = pula_vazias(j)
        assert plano[j].strip() == 'por:', (tarefa, atual, plano[j])
        j = pula_vazias(j + 1)
        novo, _, j = bloco(j)
        i = j
        if ativa and vale(atual):
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
    m = RE_CERCA.match(linha)
    if m:
        texto, mc, i = bloco(i)
        tipo, caminho = mc.group(3), mc.group(4)
        if not ativa:
            continue
        if tipo == 'file' and vale(caminho):
            destino = raiz / caminho
            destino.parent.mkdir(parents=True, exist_ok=True)
            destino.write_text(texto if mc.group(5) else texto + '\n', encoding='utf-8', newline='\n')
            n_arq += 1
        elif tipo == 'chaves' and prefixo is None:
            f = raiz / caminho
            obj = json.loads(f.read_text(encoding='utf-8'))
            novas = json.loads(texto)
            repetidas = [k for k in novas if k in obj]
            if repetidas:
                print(f'  [T{tarefa}] ERRO: {caminho} já tem as chaves {repetidas}')
                erros += 1
                continue
            obj.update(novas)
            # como o JSON.stringify: sem espaços, sem escapar o que não é ASCII, sem a quebra de linha no fim
            f.write_text(json.dumps(obj, ensure_ascii=False, separators=(',', ':')), encoding='utf-8', newline='\n')
            n_json += 1
        elif mc.group(2) == 'bash' and tipo is None and prefixo is None:
            for cmd in texto.split('\n'):
                mr = RE_RM.match(cmd)
                if mr:
                    alvo = raiz / mr.group(1)
                    if alvo.exists():
                        alvo.unlink()
                        n_rm += 1
                    else:
                        print(f'  [T{tarefa}] ERRO: rm {mr.group(1)}: não existe')
                        erros += 1
                elif cmd.strip() in COMANDOS:
                    r = subprocess.run(cmd.split(), cwd=raiz, capture_output=True, text=True, encoding='utf-8')
                    if r.returncode != 0:
                        print(f'  [T{tarefa}] ERRO: {cmd}: {r.stderr.strip()[:300]}')
                        erros += 1
                    else:
                        n_cmd += 1
        continue
    i += 1

print(f'tarefas {de}–{ate}{f" ({prefixo})" if prefixo else ""}: {n_arq} arquivos, {n_par} pares, {n_json} JSON, '
      f'{n_rm} remoções, {n_cmd} comandos, {erros} erros')
sys.exit(1 if erros else 0)
