import json, glob, sys
S = sys.argv[1]
for arq in sorted(glob.glob(S + '/p90_epb_*.progresso')):
    for l in open(arq, encoding='utf-8'):
        if not l.strip():
            continue
        s = json.loads(l)
        c = s.get('correcoes') or {}
        a = (c.get('ancora') or {}).get('mm')
        g = [x[1] for x in (c.get('giros') or [])]
        if s.get('erro'):
            print(a, g, 'ERRO', s['erro'][:50]); continue
        ll = s.get('ladosLateral') or {}
        con = s.get('contatosMM') or {}
        pr = s.get('problemas') or []
        at = s.get('atravessaMM', s.get('penetracaoLuvaPropriaMM'))
        print(a, g, len(pr), 'polG', ll.get('polegarGraus'), 'cont', con.get('polegar'), 'luva', s.get('penetracaoLuvaMM'),
              '|', '; '.join(p[:45] for p in pr)[:150])
