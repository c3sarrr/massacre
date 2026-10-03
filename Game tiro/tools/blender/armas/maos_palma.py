# A palma que cede (Fase 4.1c, Tarefa 11; decisão do usuário de 2026-10-02, "Palma que cede"): o tecido mole da palma
# da luva afunda sob a pressão da pega, até o quanto a fonte mede em cada ponto. Com a palma rígida, num punho de
# pistola só as eminências encostavam e os nós ficavam a ~12 mm da armação: a mão do gatilho girada atrás da arma não
# chegava com o indicador nela.
#  - a fonte (a ficha, `palmaQueCede`): Pérez-González, Vergara e Sancho-Bru (2013), o deslocamento médio de 20 sujeitos
#    a 1 N com o indentador plano de 3,8 mm — 88 kPa, abaixo do limiar de desconforto da tenar (100 kPa; Johansson et
#    al. 1999): o tanto que a palma cede numa pega firme que se segura sem incomodar. Os oito pontos da palma da figura
#    1 do artigo (24 e 29 na tenar, 30 na hipotenar junto do pulso, 39 no meio, 25 a 28 sob as MCPs), cada um pelo
#    ângulo e pela distância a partir do centro do pulso: o ângulo em "raios" (1 a 4: as linhas do pulso aos pontos
#    sob as MCPs do indicador ao mínimo; entre eles, linear; fora, com o passo do raio vizinho) e a distância como
#    fração da do raio. Na luva, os raios são os do centro do pulso (a cabeça do osso `mao`) às cabeças das falanges
#    proximais (as MCPs): no repouso eles abrem −17,8°, −5,2°, 8,1° e 21,4° (positivo para o mínimo), contra −15,2°,
#    −2,2°, 8,9° e 21,5° na figura;
#  - a capacidade (mm) de cada vértice da base: a dos pontos interpolada pelo inverso do quadrado da distância no plano
#    da palma (mais IDW_MM2, para o vértice em cima de um ponto não dividir por zero), e só na palma — o peso dos ossos
#    da palma (`mao`, `polegar_1`, `anelar_0`, `minimo_0`; os dedos e o antebraço não cedem aqui), a normal de repouso
#    virada para a palma (−Z: maos.py; de nada em PALMAR[0] a inteira em PALMAR[1]) e a rampa do pulso (de nada no
#    centro dele a inteira PULSO_MM adiante: a dobra do pulso é das correções das juntas). As peças de reforço não têm
#    capacidade: seguem a base;
#  - o afundamento de uma pega (empunhadura_palma.py): o deslocamento de cada vértice da palma, no referencial do braço
#    com o osso `mao` em repouso, somado depois das correções das juntas e antes das peças presas — aqui (Modelo.avaliar,
#    girado pela pose do osso `mao`) e no jogo (modeloDobras.js), igual.
# Unidades: mm; o referencial é o do braço em repouso (maos.py: +X para as pontas, +Y para o polegar, +Z para as costas,
# a esquerda espelhada em Y).
import math

import numpy as np
from mathutils import Vector

from .unidades import S

OSSOS_DA_PALMA = ('mao', 'polegar_1', 'anelar_0', 'minimo_0')
RAIOS = ('indicador_1', 'medio_1', 'anelar_1', 'minimo_1')  # as cabeças: as MCPs dos quatro dedos
PALMAR = (0.2, 0.7)  # a normal de repouso · (−Z): de nada a inteira
PULSO_MM = 10.0
IDW_MM2 = 1.0
MINIMO_MM = 0.01  # abaixo disso o vértice não cede


def _suave(t):
    t = np.clip(t, 0.0, 1.0)
    return t * t * (3 - 2 * t)


def _interpolar(raio, valores):
    """O valor no `raio` contínuo (1 a 4) entre os dos quatro raios, linear, e fora deles com o passo do vizinho."""
    k = min(max(int(math.floor(raio)), 1), 3)
    a, b = valores[k - 1], valores[k]
    return a + (b - a) * (raio - k)


def pontos_na_luva(ficha, rig, lado):
    """[(x, y, mm)] dos pontos da ficha (`palmaQueCede.pontos`) na luva de repouso do lado (mm, referencial do braço)."""
    s = 1.0 if lado == 'd' else -1.0
    centro = Vector(rig.data.bones[f'mao_{lado}'].head_local) / S
    angulos, compr = [], []
    for o in RAIOS:
        v = Vector(rig.data.bones[f'{o}_{lado}'].head_local) / S - centro
        angulos.append(math.atan2(-s * v.y, v.x))  # positivo para o mínimo, nos dois lados
        compr.append(math.hypot(v.x, v.y))
    saida = []
    for p in ficha['palmaQueCede']['pontos'].values():
        ang = _interpolar(p['raio'], angulos)
        # a distância: a fração da do raio, que fora dos quatro fica a do raio da ponta (não cresce com o passo)
        r = p['fracao'] * _interpolar(min(max(p['raio'], 1.0), 4.0), compr)
        saida.append((centro.x + r * math.cos(ang), centro.y - s * r * math.sin(ang), float(p['mm'])))
    return saida


def capacidade(malha, ficha):
    """O quanto (mm) cada vértice da malha (maos_correcoes.Malha) pode afundar (ver o cabeçalho)."""
    p = malha.p
    tris = malha.tri_base
    fn = np.cross(p[tris[:, 1]] - p[tris[:, 0]], p[tris[:, 2]] - p[tris[:, 0]])
    vn = np.zeros_like(p)
    for k in range(3):
        np.add.at(vn, tris[:, k], fn)
    vn /= np.maximum(np.linalg.norm(vn, axis=1, keepdims=True), 1e-12)
    pts = np.array([(x, y) for x, y, _mm in pontos_na_luva(ficha, malha.rig, malha.lado)])
    mm = np.array([v for _x, _y, v in pontos_na_luva(ficha, malha.rig, malha.lado)])
    d2 = ((p[:, None, :2] - pts[None, :, :]) ** 2).sum(2) + IDW_MM2
    w = 1.0 / d2
    cap = (w * mm).sum(1) / w.sum(1)
    idx = [malha.ossos.index(f'{o}_{malha.lado}') for o in OSSOS_DA_PALMA]
    palma = np.clip(malha.W[:, idx].sum(1), 0.0, 1.0)
    palmar = _suave((-vn[:, 2] - PALMAR[0]) / (PALMAR[1] - PALMAR[0]))
    centro = np.array(malha.rig.data.bones[f'mao_{malha.lado}'].head_local) / S
    pulso = _suave((p[:, 0] - centro[0]) / PULSO_MM)
    cap = cap * palma * palmar * pulso * malha.base
    cap[cap < MINIMO_MM] = 0.0
    return cap


def giro_da_mao(rig, lado):
    """A rotação (3×3, numpy) do osso `mao` da pose atual do rig, no referencial do braço."""
    nome = f'mao_{lado}'
    M = rig.pose.bones[nome].matrix @ rig.data.bones[nome].matrix_local.inverted()
    return np.array(M.to_3x3())


def aplicar(alvo, rig, lado, afundar):
    """Soma o afundamento (`afundar`: {'vertices': [...], 'vetores': [[x, y, z], ...]}, mm no referencial do braço com
    o osso `mao` em repouso) às posições `alvo` (mm, na pose atual do rig), girado pela pose do osso `mao`."""
    if not afundar or not len(afundar['vertices']):
        return alvo
    idx = np.asarray(afundar['vertices'], np.int64)
    alvo[idx] += np.asarray(afundar['vetores'], float) @ giro_da_mao(rig, lado).T
    return alvo


def parametros(cap):
    """A capacidade dos vértices que cedem, para os `extras` das luvas (o validador da saída das armas confere o
    afundamento de cada pega com ela)."""
    idx = np.nonzero(cap > 0.0)[0]
    return {'vertices': idx.tolist(), 'mm': np.round(cap[idx], 3).tolist()}
