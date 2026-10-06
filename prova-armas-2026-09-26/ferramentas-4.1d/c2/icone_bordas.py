# As bordas da nossa AWP na pose do ícone do CS2, em pixels do ícone (512 x 384), para comparar em números com as do
# ícone lidas no navegador — a grade.html com o ícone (`?url=<ícone>`), no console: `__bordas(u0, v, u1, v)` nas
# linhas e `__bordas(u, v0, u, v1)` nas colunas abaixo (o alfa a 0,5), `__perfil(u0, v, u1, v)` na luminância (a quina
# entre a frente e a face esquerda do carregador). Daqui só os nossos números: a máscara do `icone_mascara.py` (o
# alfa; o carregador em vermelho) e o render `icone` do conferir (a luminância). Nada do jogo é lido nem gravado.
#   python icone_bordas.py
import math
import os
import sys

from PIL import Image

sys.stdout.reconfigure(encoding='utf-8')
PASTA = r'C:\Users\T-Gamer\Desktop\game tiro\trabalho-4.1d\tools\blender\conferencia\awp'
LINHAS = (190, 200, 210, 220, 224, 226, 228, 230, 232, 234, 236, 238, 240, 242, 245, 250, 256, 262)  # u de 250 a 512
COLUNAS = (100, 200, 300, 320, 330, 340, 350, 356, 360, 364, 368, 372, 376, 380, 384, 388, 392, 396, 400, 404, 410,
           420, 430, 440, 450, 460, 480, 500)  # v de 60 a 300


class Imagem:
    """Uma imagem do quadro do ícone (o render tem 1600 x 1200: 3,125 px por pixel do ícone), lida em pixels do ícone
    com o bilinear da grade.html (o centro do pixel em +0,5)."""

    def __init__(self, caminho):
        self.im = Image.open(caminho).convert('RGBA')
        self.W, self.H = self.im.size
        self.k = self.W / 512.0
        self.px = self.im.load()

    def _canal(self, p, canal):
        if canal == 'alfa':
            return p[3] / 255
        if canal == 'vermelho':  # o carregador da máscara
            return (p[3] / 255) * max(0.0, (p[0] - p[1]) / 255)
        return (0.2126 * p[0] + 0.7152 * p[1] + 0.0722 * p[2]) / 255

    def amostra(self, u, v, canal='alfa'):
        x, y = u * self.k - 0.5, v * self.k - 0.5
        xa, ya = math.floor(x), math.floor(y)
        fx, fy = x - xa, y - ya

        def g(xx, yy):
            if xx < 0 or yy < 0 or xx >= self.W or yy >= self.H:
                return 0.0
            return self._canal(self.px[xx, yy], canal)
        return (g(xa, ya) * (1 - fx) * (1 - fy) + g(xa + 1, ya) * fx * (1 - fy)
                + g(xa, ya + 1) * (1 - fx) * fy + g(xa + 1, ya + 1) * fx * fy)

    def bordas(self, ua, va, ub, vb, canal='alfa', lim=0.5, passo=0.02):
        """As passagens por `lim` (pela troca do lado, como a grade.html corrigida na C2), interpoladas."""
        n = math.ceil(math.hypot(ub - ua, vb - va) / passo)
        out = []
        ant = self.amostra(ua, va, canal)
        lado = ant >= lim
        for i in range(1, n + 1):
            a = self.amostra(ua + (ub - ua) * i / n, va + (vb - va) * i / n, canal)
            novo = a >= lim
            if novo != lado:
                t = (i - 1 + ((lim - ant) / (a - ant) if a != ant else 0.5)) / n
                out.append((round(ua + (ub - ua) * t, 2), round(va + (vb - va) * t, 2), 'sobe' if novo else 'desce'))
            ant, lado = a, novo
        return out

    def perfil(self, ua, va, ub, vb, passo=0.5, canal='luminancia'):
        n = max(1, round(math.hypot(ub - ua, vb - va) / passo))
        return [(round(ua + (ub - ua) * i / n, 2), round(self.amostra(ua + (ub - ua) * i / n, va + (vb - va) * i / n, canal), 3))
                for i in range(n + 1)]


mascara = Imagem(os.path.join(PASTA, 'c2_icone_mascara.png'))
print('linhas (u: o alfa | o carregador)')
for v in LINHAS:
    print(f'  v={v}:', [(u, s) for u, _v, s in mascara.bordas(250, v, 512, v)], '|',
          [(u, s) for u, _v, s in mascara.bordas(340, v, 420, v, 'vermelho')])
print('colunas (v: o alfa)')
for u in COLUNAS:
    print(f'  u={u}:', [(v, s) for _u, v, s in mascara.bordas(u, 60, u, 300)])
render = Imagem(os.path.join(PASTA, 'icone.png'))
for v in (226, 230):
    print(f'luminância do render em v={v} (a frente do carregador escura, a face esquerda clara):',
          render.perfil(355, v, 400, v, 1.0))
