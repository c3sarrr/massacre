"""Resume as pegas da mão de apoio da P90 (varreduras_p90.rodar com lado 'e'): uma linha por pega, com o que decide a
LATERAL no lóbulo da frente — as polpas e as falanges médias de cada dedo contra a face, um dedo à direita do meio, o
dorso, a palma, os dedos lado a lado, a luva com a luva do gatilho (a penetração e a folga, o osso mais perto) e os
problemas sem os do polegar (com `--com-polegar`, com eles e o lugar do polegar). Lê os JSON das varreduras ou os
.progresso (uma pega por linha) que elas gravam enquanto rodam.
    resumo_p90e.py <arquivo>... [--com-polegar] [--so-boas]
"""
import json
import sys

com_polegar = '--com-polegar' in sys.argv
so_boas = '--so-boas' in sys.argv


def pegas(arq):
    with open(arq, encoding='utf-8') as f:
        if arq.endswith('.progresso'):
            return [json.loads(l) for l in f if l.strip()]
        return json.load(f)


def do_polegar(p):
    return any(t in p for t in ('polegar', 'atravessa a si mesma'))


for arq in [a for a in sys.argv[1:] if not a.startswith('--')]:
    for s in pegas(arq):
        c = s.get('correcoes') or {}
        chave = {'anc': (c.get('ancora') or {}).get('mm'), 'giros': c.get('giros')}
        if s.get('erro'):
            if not so_boas:
                print(json.dumps(chave), 'ERRO', s['erro'][:140])
            continue
        probs = [p for p in s.get('problemas') or [] if com_polegar or not do_polegar(p)]
        if so_boas and probs:
            continue
        ll = s.get('ladosLateral') or {}
        con = s.get('contatosMM') or {}
        print(json.dumps(chave), 'OK' if not probs else f'{len(probs)} prob.',
              'polpas', ll.get('polpasMM'), 'medias', ll.get('mediasGraus'), 'dir', ll.get('direitaMM'),
              'dorso', ll.get('dorsoGraus'), 'dorsoJog', s.get('dorsoAoJogadorGraus'),
              'palma', con.get('palma'), 'pen', s.get('penetracaoMM'),
              'juntos', {k: v[0] for k, v in (s.get('juntosMM') or {}).items()},
              'luva', {k: s.get(k) for k in ('penetracaoLuvaMM', 'folgaLuvaMM', 'pertoDaLuva')},
              'afunda', (s.get('palma') or {}).get('afundaMM'))
        if com_polegar:
            print('   polegar', ll.get('polegar'), ll.get('polegarGraus'), 'contato', con.get('polegar'),
                  'ponta', s.get('pontaDoPolegar'), 'distal', s.get('distalDoPolegar'))
        for p in probs:
            print('      -', p[:160])
