# As contas de contorno 2D da biblioteca de peças (Fase 4.1a; separadas de pecas.py na 4.1c, Tarefa 15, pelo limite de
# ~600 linhas): suavizar (Chaikin), simplificar (Douglas-Peucker e os lados curtos), suavizar um trecho (a média
# gaussiana da borda), reamostrar, a faixa em volta de uma linha, o arco e o retângulo arredondado — em mm, no plano da
# ficha, sem o Blender. O pecas.py as reexporta (os scripts das armas chamam `P.simplificar`, `P.arco`...).
import math


def suavizar(pts, it=2):
    """Chaikin em polígono fechado: tira o serrilhado de contorno lido de foto de baixa resolução."""
    for _ in range(it):
        novo = []
        for i, (ax, ay) in enumerate(pts):
            bx, by = pts[(i + 1) % len(pts)]
            novo += [(0.75 * ax + 0.25 * bx, 0.75 * ay + 0.25 * by), (0.25 * ax + 0.75 * bx, 0.25 * ay + 0.75 * by)]
        pts = novo
    return pts


def simplificar(pts, tol=0.15, minimo=0.6):
    """Tira a escada de pixels de um contorno traçado na foto sem arredondar as quinas de verdade (o Chaikin arredonda):
    Douglas-Peucker fechado com `tol` mm (1 px da foto) e depois junta no meio os lados mais curtos que `minimo` mm — a
    escada de 0,1-0,4 mm fazia o chanfro de 1 segmento sair com faces de área zero nas diagonais do punho."""
    def dp(seq):
        (ax, ay), (bx, by) = seq[0], seq[-1]
        dx, dy = bx - ax, by - ay
        n = math.hypot(dx, dy) or 1e-9
        pior, k = -1.0, 0
        for i in range(1, len(seq) - 1):
            d = abs((seq[i][0] - ax) * dy - (seq[i][1] - ay) * dx) / n
            if d > pior:
                pior, k = d, i
        if pior <= tol:
            return [seq[0], seq[-1]]
        return dp(seq[:k + 1])[:-1] + dp(seq[k:])
    pts = [tuple(p) for p in pts]
    # parte o anel no ponto mais longe do primeiro, para o Douglas-Peucker ter duas pontas fixas
    k = max(range(len(pts)), key=lambda i: math.dist(pts[0], pts[i]))
    anel = dp(pts[:k + 1])[:-1] + dp(pts[k:] + [pts[0]])[:-1]
    mudou = True
    while mudou and len(anel) > 3:
        mudou = False
        for i in range(len(anel)):
            a, b = anel[i], anel[(i + 1) % len(anel)]
            if math.dist(a, b) < minimo:
                anel[i] = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
                del anel[(i + 1) % len(anel)]
                mudou = True
                break
    return anel


def suavizar_trecho(pts, dentro, sigma=1.5, passo=0.25):
    """O contorno fechado com os vértices do trecho em que `dentro(x, y)` dá 1 (de 0 a 1: a transição sem quina) levados
    para a média gaussiana de `sigma` mm da borda em volta deles (a borda reamostrada a cada `passo` mm, só para a
    conta) — tira o zigue-zague de 0,3 a 0,6 mm dos pixels da foto, que o `simplificar` deixa nas curvas e que, com o
    chanfro, vira uma fileira de facetas brilhando (o degrau de impressão 3D da frente do punho da Glock, nas correções
    da P1 da 4.1c). Os vértices de fora do trecho ficam exatamente onde estão (as quinas de verdade, e os planos que os
    cortes da peça encontram); passe o resultado pelo `simplificar`."""
    pts = [tuple(p) for p in pts]
    anel = pts + [pts[0]]
    comp = [0.0]
    for a, b in zip(anel, anel[1:]):
        comp.append(comp[-1] + math.dist(a, b))
    total = comp[-1]
    n = max(8, int(total / passo))
    amostras, k = [], 0
    for i in range(n):
        alvo = total * i / n
        while comp[k + 1] < alvo:
            k += 1
        t = (alvo - comp[k]) / max(comp[k + 1] - comp[k], 1e-9)
        (ax, ay), (bx, by) = anel[k], anel[k + 1]
        amostras.append((ax + (bx - ax) * t, ay + (by - ay) * t))
    d = total / n
    largura = int(math.ceil(3 * sigma / d))
    out = []
    for i, (x, y) in enumerate(pts):
        w = max(0.0, min(1.0, dentro(x, y)))
        if w <= 0.0:
            out.append((x, y))
            continue
        centro = comp[i] / d
        soma = mx = my = 0.0
        for j in range(int(math.floor(centro)) - largura, int(math.ceil(centro)) + largura + 1):
            p = math.exp(-0.5 * ((j - centro) * d / sigma) ** 2)
            ax, ay = amostras[j % n]
            soma += p
            mx += p * ax
            my += p * ay
        out.append((x + (mx / soma - x) * w, y + (my / soma - y) * w))
    return out


def reamostrar(poli, n):
    """n pontos igualmente espaçados ao longo de uma polilinha."""
    comp = [0.0]
    for (ax, ay), (bx, by) in zip(poli, poli[1:]):
        comp.append(comp[-1] + math.hypot(bx - ax, by - ay))
    out = []
    for i in range(n):
        alvo = comp[-1] * i / (n - 1)
        k = max(1, next((j for j, c in enumerate(comp) if c >= alvo), len(comp) - 1))
        t = (alvo - comp[k - 1]) / max(1e-9, comp[k] - comp[k - 1])
        (ax, ay), (bx, by) = poli[k - 1], poli[k]
        out.append((ax + (bx - ax) * t, ay + (by - ay) * t))
    return out


def faixa_poligono(linha, larg):
    """Contorno de uma tira de largura `larg` em volta de uma polilinha (nervuras, frisos)."""
    esq, dir_ = [], []
    for i, (x, y) in enumerate(linha):
        a = linha[max(0, i - 1)]
        b = linha[min(len(linha) - 1, i + 1)]
        tx, ty = b[0] - a[0], b[1] - a[1]
        L = math.hypot(tx, ty) or 1.0
        nx, ny = -ty / L * larg / 2, tx / L * larg / 2
        esq.append((x + nx, y + ny))
        dir_.append((x - nx, y - ny))
    return esq + dir_[::-1]


def arco(cx, cy, r, a0, a1, n):
    """n + 1 pontos de um arco (graus) em volta de (cx, cy)."""
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)), cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / n)))
            for i in range(n + 1)]


def ret_arredondado(u0, u1, v0, v1, raio, n=4):
    """Contorno 2D (anti-horário) de um retângulo de cantos arredondados, com n segmentos por canto (os anéis de um
    lofting). O raio fica limitado à metade do lado menor."""
    r = max(0.0, min(raio, (u1 - u0) / 2 - 1e-4, (v1 - v0) / 2 - 1e-4))
    cantos = ((u1 - r, v0 + r, -90.0), (u1 - r, v1 - r, 0.0), (u0 + r, v1 - r, 90.0), (u0 + r, v0 + r, 180.0))
    pts = []
    for cu, cv, a0 in cantos:
        for i in range(n + 1):
            a = math.radians(a0 + 90.0 * i / n)
            pts.append((cu + r * math.cos(a), cv + r * math.sin(a)))
    return pts
