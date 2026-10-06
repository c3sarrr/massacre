# A grade fina da mão de apoio da P90 com o código definitivo (a dobra da pele na busca do polegar e o alvo dele só na
# arma): em volta das pegas que passaram na prova 2, e o `lado` do polegar 'baixo'. Roda com NOME e PEGAS
# [(chave, x, z, inc, gir, guin, polegar ou None)] definidos antes.
V.rodar(NOME, 'e', [(chave, V.esquerda(z, i, gi, gu, x=x, polegar=pol)) for chave, x, z, i, gi, gu, pol in PEGAS],
        vistas=globals().get('VISTAS'))
