"""Resume as linhas RESUMO de um .out das varreduras da Tarefa 14 (uma linha por pega)."""
import json
import re
import sys

for l in open(sys.argv[1], encoding='utf-8'):
    if not l.startswith('RESUMO'):
        continue
    m = re.match(r'RESUMO (\[.*?\]) (.*?) ?(\{.*\}) contatos (.*?) pen (\S+) problemas (.*)$', l.strip())
    if not m:
        print('??', l[:200])
        continue
    k, err, ex, con, pen, prob = m.groups()
    try:
        ex = json.loads(ex)
    except ValueError:
        print(k, (err or l[len('RESUMO ') + len(k):])[:160])
        continue
    con = json.loads(con) if con not in ('null', '') else {}
    try:
        probs = json.loads(prob)
    except Exception:
        probs = [prob]
    probs = [p for p in (probs or []) if 'não deita' not in p]
    if err:
        print(k, err[:110])
        continue
    campos = {kk: ex.get(kk) for kk in sys.argv[2].split(',')} if len(sys.argv) > 2 else ex
    print(k, 'pen', pen, 'con', {a: round(b, 1) for a, b in (con or {}).items()}, json.dumps(campos, ensure_ascii=False))
    for p in probs:
        print('      -', p[:150])
