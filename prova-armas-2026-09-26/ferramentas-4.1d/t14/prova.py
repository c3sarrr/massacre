"""Resume as linhas PROVA de um .out (B.mao): uma pega por bloco."""
import json
import sys

CHAVES = ['erro', 'penetracaoMM', 'contatosMM', 'ladosLateral', 'polegar', 'distalDoPolegar', 'distalAFrenteGraus',
          'pontaDoPolegar', 'dorsoAoJogadorGraus', 'juntosMM', 'altoDoDedoMM', 'distalAoEixoMM', 'entraPorOsso',
          'folgasMM', 'problemas', 'segundos']
for l in open(sys.argv[1], encoding='utf-8'):
    if l.startswith('PROVA'):
        s = json.loads(l[len('PROVA'):].strip())
        for k in CHAVES:
            if k in s:
                print(' ', k, json.dumps(s[k], ensure_ascii=False)[:900])
        print('-----')
    elif l.startswith('VISTAS') or 'Error' in l[:60]:
        print(l.rstrip()[:300])
