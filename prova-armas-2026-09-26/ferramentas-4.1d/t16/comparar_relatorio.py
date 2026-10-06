"""O relatório de uma arma antes e depois de construir de novo (a Tarefa 16): a silhueta, os triângulos de cada nível, o
tamanho dos arquivos, as medidas-chave, os problemas e os contatos da pega.
    comparar_relatorio.py <antes.relatorio.json> <depois.relatorio.json>
"""
import json
import sys


def ler(caminho):
    return json.load(open(caminho, encoding='utf-8'))


def silhueta(r):
    s = r.get('silhueta') or {}
    t = r.get('silhuetaTresQuartos') or {}
    return {'lado': s.get('iouTolerancia'), 'bruto': s.get('iouBruto'), 'tresQuartos': t.get('iouTolerancia')}


def triangulos(r):
    return {k: (v or {}).get('triangulos') for k, v in (r.get('lods') or {}).items()}


def medidas(r):
    m = r.get('medidas') or {}
    if isinstance(m, dict):
        return {k: (v.get('mm') if isinstance(v, dict) else v) for k, v in m.items()}
    return m


a, b = ler(sys.argv[1]), ler(sys.argv[2])
print('aprovado', a.get('aprovado'), '->', b.get('aprovado'), '| problemas', b.get('problemas'))
print('silhueta', silhueta(a), '->', silhueta(b))
print('triângulos', triangulos(a), '->', triangulos(b))
print('arquivos', sum((a.get('arquivos') or {}).values()), '->', sum((b.get('arquivos') or {}).values()))
ma, mb = medidas(a), medidas(b)
if isinstance(ma, dict) and isinstance(mb, dict):
    mud = {k: (ma.get(k), mb.get(k)) for k in sorted(set(ma) | set(mb)) if ma.get(k) != mb.get(k)}
    print('medidas que mudaram', json.dumps(mud, ensure_ascii=False)[:1500])
ea, eb = a.get('empunhadura') or {}, b.get('empunhadura') or {}
for lado in eb.get('maos', []):
    print(f'pega {lado}: entra', (ea.get(lado) or {}).get('penetracaoMM'), '->', eb[lado].get('penetracaoMM'),
          '| contatos', json.dumps((ea.get(lado) or {}).get('contatosMM')), '->', json.dumps(eb[lado].get('contatosMM')),
          '| atravessa', ((ea.get(lado) or {}).get('luva') or {}).get('atravessaMM'), '->',
          (eb[lado].get('luva') or {}).get('atravessaMM'))
