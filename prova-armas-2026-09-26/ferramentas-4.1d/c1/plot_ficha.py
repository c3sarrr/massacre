# O desenho da ficha da P90 depois da C1 (o contorno composto e as peças de cima) contra o de antes, para conferir a olho.
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
f = json.load(open(r'C:/Users/T-Gamer/Desktop/game tiro/trabalho-4.1d/tools/blender/refs/p90.json', encoding='utf-8'))
v = json.load(open('p90_antes_c1.json', encoding='utf-8'))
fig, ax = plt.subplots(2, 1, figsize=(16, 14), gridspec_kw={'height_ratios': [1, 1.3]})
for a, (x0, x1, y0, y1) in zip(ax, ((-510, 5, -105, 135), (-235, -40, 30, 122))):
    def anel(p, **k):
        xs = [q[0] for q in p] + [p[0][0]]
        ys = [q[1] for q in p] + [p[0][1]]
        a.plot(xs, ys, **k)
    anel(v['contorno'], color='0.7', lw=1, ls='--')
    anel(f['contorno'], color='k', lw=1.4)
    cores = {'ponte': 'm', 'pernasPonte': 'tab:purple', 'trilhoCima': 'c', 'baseMiraTras': 'tab:orange', 'orelhaMiraTras': 'g',
             'baseMiraFrente': 'tab:orange', 'orelhaMiraFrente': 'g', 'carregador': 'tab:red', 'receptor': 'b'}
    for n, c in cores.items():
        anel(f['pecas'][n], color=c, lw=0.9)
    for n, b in zip(f['buracosNomes'], f['buracos']):
        anel(b, color='tab:brown', lw=0.8, ls=':')
    jp = f['pontos']['janelasPonte']
    for k in ('frente', 'tras'):
        (xa, xb), (ya, yb) = jp[k]['x'], jp[k]['y']
        anel([(xa, ya), (xb, ya), (xb, yb), (xa, yb)], color='y', lw=1.0)
    jt = f['pontos']['janelaTorre']
    anel([(jt['x'][0], jt['y'][0]), (jt['x'][1], jt['y'][0]), (jt['x'][1], jt['y'][1]), (jt['x'][0], jt['y'][1])], color='y', lw=1.0)
    m = f['pontos']['miras']
    import math
    for k in ('tras', 'frente'):
        cx, cy = m['botoes'][k]
        anel([(cx + 6.5 * math.cos(t / 20 * math.tau), cy + 6.5 * math.sin(t / 20 * math.tau)) for t in range(20)], color='r', lw=0.8)
        cx, cy = m['parafusos'][k]['centro']
        r = m['parafusos'][k]['raio']
        anel([(cx + r * math.cos(t / 20 * math.tau), cy + r * math.sin(t / 20 * math.tau)) for t in range(20)], color='0.4', lw=0.8)
    for nome in ('miraTras', 'miraFrente'):
        a.plot(*f['pontos'][nome], 'k+', ms=10)
    for nome in ('rebativelTras', 'rebativelFrente'):
        a.plot(*f['pontos'][nome]['pivo'], 'bx', ms=8)
    a.set_xlim(x0, x1); a.set_ylim(y0, y1); a.set_aspect('equal'); a.grid(True, lw=0.3)
fig.tight_layout()
fig.savefig(r'C:/Users/T-Gamer/Desktop/game tiro/trabalho-4.1d/tools/blender/conferencia/p90/ficha_c1.png', dpi=80)
print('ok')
