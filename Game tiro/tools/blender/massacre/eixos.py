"""Eixos entre o jogo e o Blender (Fase 4.1; docs/phases/phase-4.md, "Referencial de cada arma").

Jogo (three.js): +X boca, +Y cima, +Z lado direito. Blender: Z para cima. Um ponto (x, y, z) do jogo fica em
(x, −z, y) no Blender; o exportador faz o caminho de volta: (x, y, z) do Blender → (x, z, −y) do jogo.
Cada peça guarda a geometria no referencial dela no jogo; o objeto do Blender recebe a matriz C · T(pos) · R(rot).
Os giros são o Euler 'XYZ' do three.js (matriz Rx · Ry · Rz), que no mathutils é a ordem 'ZYX'.
"""

import math

from mathutils import Euler, Matrix, Vector

# Jogo → Blender (e a volta).
C = Matrix(((1, 0, 0, 0), (0, 0, -1, 0), (0, 1, 0, 0), (0, 0, 0, 1)))
C_INV = C.inverted()


def rot_jogo(rot):
    """Matriz 3×3 do Euler XYZ do three.js ([x, y, z] em rad)."""
    a, b, c = rot if rot else (0.0, 0.0, 0.0)
    return Euler((a, b, c), 'ZYX').to_matrix()


def euler_jogo(m3):
    """Euler XYZ do three.js de uma matriz de rotação (o setFromRotationMatrix dele, com o mesmo corte perto de ±90°).
    O Y sai do atan2(sen, |cos|) em vez do asin(m13): o mesmo ângulo, sem perder precisão perto de ±90° com as matrizes
    float32 do Blender (asin(1 − 6·10⁻⁸) já erra 3·10⁻⁴ rad)."""
    m11, m12, m13 = m3[0][0], m3[0][1], m3[0][2]
    m22, m23 = m3[1][1], m3[1][2]
    m32, m33 = m3[2][1], m3[2][2]
    y = math.atan2(m13, math.hypot(m11, m12))
    if abs(m13) < 0.9999999:
        return [math.atan2(-m23, m33), y, math.atan2(-m12, m11)]
    return [math.atan2(m32, m22), y, 0.0]


def matriz_blender(pos=None, rot=None):
    """matrix_world do Blender de uma peça/âncora do jogo."""
    p = Vector(pos) if pos else Vector((0.0, 0.0, 0.0))
    return C @ Matrix.Translation(p) @ rot_jogo(rot).to_4x4()


def para_jogo(matrix_world):
    """Posição, rotação (3×3) e escala no referencial do jogo de um objeto do Blender."""
    loc, quat, escala = (C_INV @ matrix_world).decompose()
    return loc, quat.to_matrix(), escala


def ponto_blender(p):
    """Ponto do jogo no Blender (x, −z, y)."""
    return Vector((p[0], -p[2], p[1]))


def ponto_jogo(v):
    """Ponto do Blender no jogo (x, z, −y)."""
    return [v[0], v[2], -v[1]]


def mesma_rotacao(m3, rot, tol=1e-5):
    """A rotação do objeto ainda é a do Euler guardado (a volta não inventa um Euler equivalente com outros números)."""
    r = rot_jogo(rot)
    return all(abs(m3[i][j] - r[i][j]) <= tol for i in range(3) for j in range(3))
