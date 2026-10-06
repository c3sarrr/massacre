import runpy
g = runpy.run_path('pnp_volta.py')
volta = g['volta']
for nome, (u, v), lado in [
    ('pilar da ponte, frente (face esq.)', (85.1, 150), 15.1), ('pilar da ponte, frente (face esq.)', (86.0, 165), 15.1),
    ('pilar, frente no alto', (94.0, 107), 15.1),
    ('trilho, ponta da frente', (106.0, 95), 10.6),
    ('janela do pilar, canto frente-cima', (106.0, 121), 15.1), ('janela do pilar, canto trás-cima', (128.6, 121), 15.1),
    ('janela do pilar, canto frente-baixo', (106.0, 171), 15.1), ('janela do pilar, canto trás-baixo', (128.6, 171), 15.1),
    ('laço da ponte, alto', (200.0, 143), 20.4), ('laço da ponte, trás', (282.0, 190), 20.4), ('laço, baixo', (200.0, 200), 20.4),
]:
    print(f'{nome:38s} {(u, v)} lado {lado:5.1f} -> x, alto {volta(u, v, lado)}')
