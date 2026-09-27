# Unidades e referenciais das armas realistas (Fase 4.1a; plano da 4.1a, decisão D1).
# Construção em milímetros no referencial da ficha: boca do cano em x = 0, eixo do cano em y = 0, +X para a boca, +Y
# para cima. No Blender a cena é em metros (1 mm = 0,001), X = x, Z = y e o lado direito da arma fica em -Y.
# Exportação: escala 1000/25,4 (1 unidade = 1 u = 1 polegada na escala do boneco) com a origem no pino do gatilho; com
# o Y para cima do glTF, o -Y do Blender vira o +Z do jogo (o lado direito).

S = 0.001                     # metros por milímetro
MM_POR_U = 25.4
U_POR_M = 1000.0 / MM_POR_U   # metros da cena → u do jogo


def v3(x, y, z):
    """Ponto em mm no Blender (x, y, z) → metros."""
    return (x * S, y * S, z * S)


def ficha(x, y, lado=0.0):
    """Ponto (x, y) da ficha no Blender, com a profundidade `lado` em mm (Y do Blender: + esquerda, - direita)."""
    return (x * S, lado * S, y * S)
