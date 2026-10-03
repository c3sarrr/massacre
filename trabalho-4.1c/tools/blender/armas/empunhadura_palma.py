# O afundamento da palma numa pega (Fase 4.1c, Tarefa 11; a palma que cede, maos_palma.py): o solver resolve as mãos
# com a palma entrando na arma até o que cada vértice cede (empunhadura_arma.NaArma, `ceder`); depois, cada vértice da
# palma que ficou dentro vai ao ponto mais próximo da superfície, e a pele em volta afunda junto, como uma membrana: o
# deslocamento de cada vértice livre da palma é a média dos vizinhos (a solução harmônica), preso nos que encostaram e
# zero onde a palma não cede (a borda da região, os dedos, as costas). Cada um fica limitado ao que ele cede — o que
# ainda entrar além disso é penetração de verdade, que a validação reprova (o `alemMM` do relatório). Em RODADAS: a pele
# que afunda em volta do contato pode levar um vizinho para dentro de outra quina.
# O resultado vai no referencial do braço com o osso `mao` em repouso (o que maos_palma.aplicar gira pela pose dele) e
# no .glb da arma (os extras da pega), para o jogo afundar a mesma palma (modeloDobras.js).
# Unidades: mm, no referencial da arma até a conversão.
import numpy as np
from mathutils import Vector

from . import maos_palma

RODADAS = 4
ITERACOES = 600
TOLERANCIA_MM = 1e-4  # a membrana parou de mudar
MINIMO_MM = 1e-3  # o deslocamento abaixo disso não vai para o .glb
ALCANCE_MM = 1.0  # além do que o vértice cede: o que está mais fundo que isso só é medido (penetração de verdade)


def _vizinhos(tris, ativos):
    """A matriz (densa, ativos × ativos) da média dos vizinhos de cada vértice ativo pelas arestas da base: os vizinhos
    fora dos ativos (que não cedem) entram com deslocamento zero, no grau."""
    pos = {int(v): k for k, v in enumerate(ativos)}
    viz = [set() for _ in ativos]
    for t in tris:
        for a, b in ((t[0], t[1]), (t[1], t[2]), (t[2], t[0])):
            if a in pos:
                viz[pos[a]].add(int(b))
            if b in pos:
                viz[pos[b]].add(int(a))
    M = np.zeros((len(ativos), len(ativos)))
    for k, vs in enumerate(viz):
        for b in vs:
            if b in pos:
                M[k, pos[b]] = 1.0 / len(vs)
    return M


def afundamento(na, pose):
    """O afundamento da palma da luva de `na` (empunhadura_arma.NaArma: o colisor, o obstáculo — a arma, ou a arma e a
    outra luva — e o encaixe) na `pose`. Devolve {'vertices': [...], 'vetores': [[x, y, z], ...] (mm, o referencial do
    braço com o osso `mao` em repouso), 'afundaMM': o maior, 'encostam': quantos vértices encostaram, 'alemMM': o quanto
    algum ainda entra além do que cede}."""
    modelo = na.col.modelo
    cap = modelo.cede
    ativos = np.nonzero(cap > 0.0)[0]
    p = modelo.avaliar(pose)
    giro_mao = maos_palma.giro_da_mao(modelo.malha.rig, modelo.malha.lado)
    E = np.array(na.encaixe)
    P = p[ativos] @ E[:3, :3].T + E[:3, 3]
    M = _vizinhos(modelo.malha.tri_base, ativos)
    v = np.zeros((len(ativos), 3))
    fixo = np.zeros(len(ativos), bool)
    arma = na.arma
    for _rodada in range(RODADAS):
        Q = P + v
        novos = 0
        for k, i in enumerate(ativos):
            d = arma.distancia(Vector(Q[k]), float(cap[i]) + ALCANCE_MM)
            if d is None or d >= 0.0:
                continue
            co = np.array(arma.bvh.find_nearest(Vector(Q[k]))[0])
            v[k] += co - Q[k]
            novos += not fixo[k]
            fixo[k] = True
        if not novos and _rodada:
            break
        livres = ~fixo
        for _it in range(ITERACOES):
            media = M @ v
            mudou = np.abs(media[livres] - v[livres]).max() if livres.any() else 0.0
            v[livres] = media[livres]
            if mudou < TOLERANCIA_MM:
                break
        # cada um até o que cede
        norma = np.linalg.norm(v, axis=1)
        escala = np.minimum(1.0, cap[ativos] / np.maximum(norma, 1e-12))
        v *= escala[:, None]
    Q = P + v
    alem = 0.0
    for k in range(len(ativos)):
        d = arma.distancia(Vector(Q[k]), float(cap[ativos[k]]) + ALCANCE_MM)
        if d is not None and -d > alem:
            alem = -d
    # da arma ao braço (o encaixe é ortonormal) e do braço ao osso `mao` em repouso
    v_mao = (v @ E[:3, :3]) @ giro_mao
    norma = np.linalg.norm(v_mao, axis=1)
    sai = norma > MINIMO_MM
    return {'vertices': ativos[sai].tolist(), 'vetores': np.round(v_mao[sai], 4).tolist(),
            'afundaMM': round(float(norma.max()) if len(norma) else 0.0, 3), 'encostam': int(fixo.sum()),
            'alemMM': round(alem, 3)}


def resumo(afundar):
    """O que vai no relatório de uma mão: o maior afundamento, quantos vértices afundam e quantos encostaram, e o quanto
    algum ainda entra além do que cede."""
    return {'afundaMM': afundar['afundaMM'], 'vertices': len(afundar['vertices']), 'encostam': afundar['encostam'],
            'alemMM': afundar['alemMM']}
