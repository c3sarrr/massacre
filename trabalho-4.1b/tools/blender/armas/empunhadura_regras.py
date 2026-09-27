# As regras da pega por categoria do viewmodel (Fase 4.1b; desenho em docs/superpowers/specs/2026-09-26-4.1b-luvas-e-
# empunhadura-design.md, seção 6.2, passo 4): onde cada mão entra na arma e em que ordem fecha. A do `rifle` (esta
# subfase); as outras categorias entram com as armas delas (4.1c e 4.1d). Cada arma pode corrigir os números no script
# dela (`EMPUNHADURA = {'direita': {...}, 'esquerda': {...}}`, as mesmas chaves), e passa pelas mesmas validações.
#  - mão direita (o punho): a luva entra com a linha dos nós quase paralela à frente do punho (15° de diagonal no
#    plano da palma: o punho cruza a palma da membrana do polegar para a base do mínimo, como na pega de força), a palma
#    rente à lateral direita (o giro em volta do eixo do punho em 0°: com a palma girada para abraçar a quina de trás, a
#    base dela se afastava do punho e o polegar não alcançava o outro lado), a MCP do indicador 27,6 mm atrás e 11,7 mm
#    abaixo do ponto do gatilho (a membrana alta no punho e o médio logo embaixo do guarda-mato), e chega pela normal da
#    palma até encostar; o médio, o anelar e o mínimo fecham em volta do punho; o indicador põe a polpa na face da frente
#    do gatilho a 60 % da altura dele, com pelo menos 1 mm do guarda-mato e do resto da arma; o polegar cruza para o
#    lado esquerdo do punho (a polpa encostada o mais à esquerda que ele alcança);
#  - mão esquerda (o guarda-mão): a palma por baixo, os dedos para a direita (o polegar para a frente), girada 25° em
#    volta da vertical (os dedos para a frente, o pulso para trás) e 15° em volta do eixo do cano (a palma abraçando o
#    canto de baixo à esquerda), chegando pela normal da palma até encostar; os quatro dedos fecham pelo lado direito; o
#    polegar sobe pelo lado esquerdo.
# A CMC do polegar fica na pose de pegar (a abdução palmar e a flexão no máximo da ficha) já na chegada da palma: com o
# polegar afastado, a palma encostava com a tenar tangente à arma, e qualquer movimento do polegar levava a pele da
# tenar 4 a 6 mm para dentro dela.
# Referenciais: a base de cada mão leva os eixos da luva (X para as pontas, Y para o lado do polegar na mão direita, Z
# para as costas) aos do soquete; as giradas vêm antes, no referencial do soquete, e a diagonal depois, no plano da
# palma (com o sinal trocado na esquerda, que é a direita espelhada em Y).
import copy
import math

from mathutils import Matrix, Vector

from .maos import DEDOS4

RIFLE = {
    'direita': {
        'soquete': 'mao_d',
        'base': ((1.0, 0.0, 0.0), (0.0, 0.0, -1.0), (0.0, 1.0, 0.0)),
        'giros': (('Z', 0.0),),
        'diagonal': 15.0,
        # a MCP do indicador a partir do ponto do gatilho (mm, Blender: x, y, z), antes de encostar a palma
        'ancora': {'ponto': 'mcp_indicador', 'de': 'gatilho', 'mm': (-27.6, -40.0, -11.7)},
        'chegada': (45.0, 60.0),
        'dedos': ('medio', 'anelar', 'minimo'),
        'gatilho': {'altura': 0.6, 'abertura': 20.0, 'raio': 8.0, 'folga': 1.0},
        'polegar': {'lado': (0.0, 1.0, 0.0), 'peso': 4.0},
    },
    'esquerda': {
        'soquete': 'mao_e',
        'base': ((0.0, -1.0, 0.0), (-1.0, 0.0, 0.0), (0.0, 0.0, -1.0)),
        'giros': (('Z', 25.0), ('X', -15.0)),
        'diagonal': 15.0,
        # o centro da palma a partir do soquete (mm), antes de encostar a palma
        'ancora': {'ponto': 'palma', 'de': 'soquete', 'mm': (0.0, 10.0, -30.0)},
        'chegada': (40.0, 60.0),
        'dedos': DEDOS4,
        'gatilho': None,
        'polegar': {'lado': (0.0, 1.0, 0.0), 'peso': 2.0},
    },
}
REGRAS = {'rifle': RIFLE}


def regra(categoria, correcoes=None):
    """A regra da categoria com as correções da arma (o `EMPUNHADURA` do script dela) por cima."""
    if categoria not in REGRAS:
        raise ValueError(f'sem regra de empunhadura para a categoria {categoria} (tem: {", ".join(REGRAS)})')
    r = copy.deepcopy(REGRAS[categoria])
    for mao, valores in (correcoes or {}).items():
        if mao not in r:
            raise ValueError(f'EMPUNHADURA: mão desconhecida {mao}')
        for chave, valor in valores.items():
            if chave not in r[mao]:
                raise ValueError(f'EMPUNHADURA: chave desconhecida {mao}.{chave}')
            r[mao][chave] = valor
    return r


def rotacao(r, soquete, lado):
    """A rotação (3×3) da luva no referencial da arma: o soquete, as giradas, a base e a diagonal no plano da palma."""
    R = soquete.to_3x3().normalized()
    for eixo, graus in r['giros']:
        R = R @ Matrix.Rotation(math.radians(graus), 3, eixo)
    R = R @ Matrix(r['base'])  # as linhas; as colunas são os eixos da luva no referencial do soquete
    sinal = 1.0 if lado == 'd' else -1.0
    return R @ Matrix.Rotation(math.radians(sinal * r['diagonal']), 3, 'Z')


def lado_do_polegar(r):
    return Vector(r['polegar']['lado']).normalized()
