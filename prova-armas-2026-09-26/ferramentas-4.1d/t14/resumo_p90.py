"""Resume os JSON das varreduras da Tarefa 15 (varreduras_p90.rodar): uma linha por pega, com o que decide a mão do
gatilho da P90 — a penetração, os contatos, os dedos lado a lado, onde ficam as pontas (o y da distal: positivo é o
lado esquerdo, os dedos que abraçam), as flexões da MCP e da PIP de cada dedo e os problemas sem os do polegar (quando
a varredura é sem ele). Uso: resumo_p90.py <json>... [--com-polegar]"""
import json
import sys

com_polegar = '--com-polegar' in sys.argv
for arq in [a for a in sys.argv[1:] if not a.startswith('--')]:
    for s in json.load(open(arq, encoding='utf-8')):
        c = s.get('correcoes') or {}
        anc = (c.get('ancora') or {}).get('mm')
        giros = c.get('giros')
        chave = {'anc': anc, 'giros': giros, 'diag': c.get('diagonal'),
                 'alt': (c.get('gatilho') or {}).get('altura')}
        if s.get('erro'):
            print(json.dumps(chave), 'ERRO', s['erro'][:120])
            continue
        ang = s.get('angulos') or {}
        flex = {d: (ang.get(f'{d}_1'), ang.get(f'{d}_2')) for d in ('indicador', 'medio', 'anelar', 'minimo')}
        cen = s.get('centros') or {}
        pontas = {k: cen[k] for k in ('indicador_3', 'medio_3', 'minimo_3') if k in cen}
        probs = [p for p in s.get('problemas') or []
                 if com_polegar or not any(t in p for t in ('polegar', 'atravessa a si mesma'))]
        print(json.dumps(chave), 'pen', s.get('penetracaoMM'),
              'con', {k: round(v, 1) for k, v in (s.get('contatosMM') or {}).items()},
              'juntos', {k: v[0] for k, v in (s.get('juntosMM') or {}).items()},
              'alto', s.get('altoDoDedoMM'), 'pontas', pontas, 'flex', flex,
              'polpaAlvo', (s.get('indicador') or {}).get('polpaAoAlvoMM'))
        if com_polegar:
            print('   polegar', json.dumps(s.get('polegar'), ensure_ascii=False)[:300], 'furo',
                  json.dumps(s.get('polegarNoFuro'), ensure_ascii=False)[:200])
        for p in probs:
            print('      -', p[:150])
