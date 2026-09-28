# Ajuste da gaiola ao limite de Catmull-Clark (Fase 4.1b; desenho em
# docs/superpowers/specs/2026-09-26-4.1b-luvas-e-empunhadura-design.md, seção 3.2): as âncoras da gaiola são movidas
# para que a superfície limite (onde o modificador Subdivision Surface com "Use Limit Surface" põe os vértices) passe
# pelos pontos de desenho delas. Separado de maos_gaiola.py, que desenha a gaiola.


def ajustar_ao_limite(bm, livres=(), iteracoes=120):
    """Move as âncoras da gaiola (só quadriláteros; todos os vértices menos os `livres`) para que a superfície limite
    de Catmull-Clark passe pelos pontos de desenho delas (a posição de cada vértice ao entrar); os livres ficam onde
    estão. A posição limite de um vértice de valência n é (n²·v + 4·Σ vizinhos pelas arestas + Σ opostos nas faces) /
    (n·(n+5)); na borda livre (o forro, com a borda suave), (a + 4·v + b)/6. A iteração de Jacobi soma a cada âncora a
    diferença entre o ponto de desenho e a posição limite; o operador é uma média de pesos positivos, então converge.
    Devolve o maior resíduo nas âncoras (mm)."""
    alvo = {v: v.co.copy() for v in bm.verts}
    regras = []
    for v in bm.verts:
        borda = [e.other_vert(v) for e in v.link_edges if e.is_boundary]
        if borda:
            if len(borda) != 2:
                raise ValueError(f'gaiola: vértice de borda com {len(borda)} vizinhos na borda')
            regras.append((v, 0, borda, ()))
            continue
        arestas = [e.other_vert(v) for e in v.link_edges]
        opostos = []
        for f in v.link_faces:
            vs = list(f.verts)
            if len(vs) != 4:
                raise ValueError('gaiola: só quadriláteros')
            opostos.append(vs[(vs.index(v) + 2) % 4])
        regras.append((v, len(arestas), arestas, opostos))

    def limites():
        lim = []
        for v, n, arestas, opostos in regras:
            if n == 0:
                a, b = arestas
                lim.append((a.co + v.co * 4.0 + b.co) / 6.0)
            else:
                s = v.co * float(n * n)
                for u in arestas:
                    s += u.co * 4.0
                for u in opostos:
                    s += u.co
                lim.append(s / float(n * (n + 5)))
        return lim

    for _ in range(iteracoes):
        for (v, *_r), p in zip(regras, limites()):
            if v not in livres:
                v.co += alvo[v] - p
    return max((alvo[v] - p).length for (v, *_r), p in zip(regras, limites()) if v not in livres)
