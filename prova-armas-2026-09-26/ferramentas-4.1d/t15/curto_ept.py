import json, glob, sys
S, padrao = sys.argv[1], sys.argv[2]
for arq in sorted(glob.glob(f'{S}/{padrao}')):
    for l in open(arq, encoding='utf-8'):
        if not l.strip():
            continue
        s = json.loads(l)
        c = s.get('correcoes') or {}
        a = (c.get('ancora') or {}).get('mm')
        g = [x[1] for x in (c.get('giros') or [])]
        if s.get('erro'):
            print(a, g, 'ERRO', s['erro'][:90])
            continue
        ll = s.get('ladosLateral') or {}
        con = s.get('contatosMM') or {}
        pg = (s.get('polegar') or {}).get('graus') or {}
        pr = s.get('problemas') or []
        print(a, g, len(pr), 'polG', ll.get('polegarGraus'), 'cont', con.get('polegar'), 'atr',
              (s.get('luva') or {}).get('atravessaMM'), 'abd', pg.get('abducao'), 'cmc', pg.get('cmc'), 'rot',
              pg.get('rotacao'), '|', '; '.join(p[18:70] for p in pr)[:170])
