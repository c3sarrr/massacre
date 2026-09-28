# A frente da M4A4 (a carabina M4A1) — Fase 4.1c (desenho em docs/superpowers/specs/2026-09-28-4.1c-glock-m4a4-m9-
# design.md, seção 3.2): o anel delta, o guarda-mão de trilhos de quatro lados (o tipo RAS: os quatro trilhos MIL-STD-1913
# da biblioteca e os furos de ventilação da metade de baixo), a torre da massa de mira A2 (as
# orelhas com a massa, a janela, os pinos cônicos, o ressalto da baioneta e o zarelho), o cano com o degrau do lançador e
# o quebra-chamas A2 (cinco fendas, o fundo fechado). Em mm no referencial da ficha (tools/blender/refs/m4a4.json);
# lado direito da arma = -Y do Blender. O resto da arma está em m4a4.py.
import math

from . import pecas as P
from . import pecas_superficie as PS

X_FRENTE_REC = -386.8  # a face da frente do receptor superior (a ficha, pecas.anelDelta)
X_ANEL = -375.0        # o fim do anel delta; daí para a frente o guarda-mão
X_FIM_GM = -214.0      # a tampa da frente do guarda-mão, encostada na torre
Y_TRILHO_LADO = 14.5   # o meio dos trilhos dos lados (a metade de cima do guarda-mão, na foto da PEO)
Y_FUNDO_PAINEL = -16.7  # a base do trilho de baixo (o alto dos dentes em -26 menos a altura da norma)


def _anel_delta(ficha, M):
    """O anel delta (a mola de arame fica dentro) e a porca do cano, de aço fosfatizado: o perfil da foto na largura do
    anel, arredondado pelo chanfro largo, com os dois frisos."""
    pc = ficha['pecas']['anelDelta']
    la = ficha['vistaDeCima']['larguras']['anelDelta']['mm'] / 2
    anel = P.prisma('anel delta', P.simplificar(pc), 'XZ', -la, la, M['detalhes'], 'detalhes', chanfro=6.0, seg=4)
    for x in (X_ANEL - 5.0, X_ANEL - 2.4):
        P.cortar(anel, P.torno('friso do anel', [(x, 0), (x, 60.0), (x + 0.8, 60.0), (x + 0.8, 0)], M['detalhes'], 'detalhes', seg=48),
                 depois_do_chanfro=True)
        P.cortar(anel, P.torno('fundo do friso', [(x - 1.0, 0), (x - 1.0, 60.0), (x + 1.8, 60.0), (x + 1.8, 0)], M['detalhes'], 'detalhes',
                               seg=48, so_alto=True))
    return anel


def _guarda_mao(ficha, M):
    """O guarda-mão de trilhos (alumínio anodizado, zona guarnição): o corpo octogonal, os quatro trilhos (o de cima na
    altura do trilho do receptor, o de baixo com os dentes em -26, os dos lados na metade de cima), os oito furos de
    ventilação de cada lado da metade de baixo."""
    pt, L = ficha['pontos'], ficha['vistaDeCima']['larguras']
    mat = M['guarnicao']
    t = pt['trilhoGuardaMao']
    w = L['guardaMao']['mm'] / 2          # o alto dos trilhos dos lados
    h = PS.PICATINNY['alturaMinima']
    lado = w - h                          # a face do corpo onde os trilhos dos lados nascem
    cima, baixo = t['topo'] - h, t['fundo'] + h
    secao = [(-8.0, cima), (8.0, cima), (lado, cima - 4.0), (lado, baixo + 2.7), (8.0, baixo), (-8.0, baixo), (-lado, baixo + 2.7),
             (-lado, cima - 4.0)]
    corpo = P.prisma('guarda-mão', secao, 'YZ', X_ANEL, X_FIM_GM, mat, 'guarnicao', chanfro=1.0)
    x0, x1 = t['x']
    # as fendas onde a foto as mostra (em cima e embaixo; as dos lados no passo das de cima). A numeração das fendas
    # (R14 … R28 na foto) fica de fora: gravada no trilho, o booleano dela com o das fendas apagava fendas dos lados
    for nome, giro, y, z, fs in (('trilho de cima do guarda-mão', 0, 0.0, t['topo'], t['fendas']),
                                 ('trilho de baixo do guarda-mão', 180, 0.0, t['fundo'], t['fendasBaixo']),
                                 ('trilho esquerdo do guarda-mão', 90, w, Y_TRILHO_LADO, t['fendas']),
                                 ('trilho direito do guarda-mão', -90, -w, Y_TRILHO_LADO, t['fendas'])):
        PS.trilho_picatinny(nome, x0, x1, mat, 'guarnicao', 'base', y=y, z=z, giro=giro, altura=h + 0.8, fendas=list(fs))
    # os furos de ventilação: recortes de 6 mm na parede da metade de baixo (o guarda-mão é oco; o fundo escuro)
    f = pt['furosGuardaMao']
    for s in (-1, 1):
        for i, xf in enumerate(f['x']):
            P.cortar(corpo, P.pino(f'furo do guarda-mão {i}', xf, f['y'], f['raio'], mat, 'guarnicao', lado=s, de=lado - 6.0,
                                   ate=lado + 2.0))
    # a junta das duas metades (a de cima com três trilhos, a de baixo com o trilho e os furos)
    for s in (-1, 1):
        y0, y1 = sorted((s * (lado - 0.6), s * (lado + 2.0)))
        P.cortar(corpo, P.caixa('junta do guarda-mão', (X_ANEL + 3.0, y0, 1.6), (X_FIM_GM - 3.0, y1, 2.4), mat, 'guarnicao', chanfro=0),
                 depois_do_chanfro=True)
    return corpo


def _torre(ficha, M):
    """A torre da massa de mira A2 (aço fosfatizado): o perfil da foto na largura do munhão, as orelhas mais estreitas
    em volta da massa, a janela, o furo vertical da massa com o poste dentro, os pinos cônicos, o ressalto da baioneta e
    o zarelho de arame em volta do rebite (o perfil perde a parte de baixo, que vira as duas peças)."""
    pc, pt, L = ficha['pecas'], ficha['pontos'], ficha['vistaDeCima']['larguras']
    det = M['detalhes']
    lt = L['torre']['mm'] / 2
    lo = L['orelhasTorre']['mm'] / 2
    torre = P.prisma('torre', P.simplificar(pc['torre']), 'XZ', -lt, lt, det, 'detalhes', chanfro=0.8)
    xs = [p[0] for p in pc['torre']]
    for s in (-1, 1):
        y0, y1 = sorted((s * lo, s * (lt + 3.0)))
        P.cortar(torre, P.caixa('largura das orelhas', (min(xs) - 1, y0, pt['orelhas']['y0']), (max(xs) + 1, y1, 80.0), det, 'detalhes',
                                chanfro=0))
    j = pt['janelaTorre']
    for b in ficha['buracos']:
        bx = [p[0] for p in b]
        if min(bx) >= j['x'][0] - 1 and max(bx) <= j['x'][1] + 1:
            P.cortar(torre, P.prisma('janela da torre', b, 'XZ', -lt - 2, lt + 2, det, 'detalhes', chanfro=0))
    # a parte de baixo do perfil (o zarelho da bandoleira e o ressalto da baioneta, vistos de lado) é fina: sai do bloco
    # e volta como uma chapa de 3,5 mm com o mesmo perfil, o rebite do zarelho e o vão do laço
    zr = pt['zarelho']
    fundo = [(x, min(z, -9.0)) for x, z in P.simplificar(pc['torre'])]
    P.cortar(torre, P.caixa('fundo da torre', (min(xs) - 1, -lt - 2, -40.0), (max(xs) + 1, lt + 2, -9.0), det, 'detalhes', chanfro=0))
    chapa = P.prisma('zarelho e ressalto', fundo, 'XZ', -1.75, 1.75, det, 'detalhes', chanfro=0.5)
    rs = pt['ressalto']
    P.caixa('ressalto da baioneta', (rs['x'][0], -4.0, rs['y'][0]), (rs['x'][1], 4.0, -8.0), det, 'detalhes', chanfro=0.6)
    rx, rz = zr['rebite']
    P.pino('rebite do zarelho', rx, rz, 2.4, det, 'detalhes', lado=-1, de=-4.0, ate=4.0)
    x0, x1 = zr['x']
    z0, z1 = zr['y']
    P.cortar(chapa, P.prisma('vão do zarelho', P.ret_arredondado(x0 + zr['fio'], x1 - zr['fio'], z0 + zr['fio'], z1 - 1.0, 2.0, 4), 'XZ',
                             -3.0, 3.0, det, 'detalhes', chanfro=0))
    # o furo vertical das orelhas e o poste da massa (a ponta um pouco abaixo do alto delas)
    ps = pt['poste']
    P.cortar(torre, P.torno('furo da massa', [(pt['orelhas']['y0'] + 12.0, 0), (pt['orelhas']['y0'] + 12.0, lo - 2.2), (90.0, lo - 2.2),
                                              (90.0, 0)], det, 'detalhes', seg=24, eixo='Z', centro=(ps['x'], 0, 0)))
    m = ps['lado'] / 2
    P.caixa('poste da massa', (ps['x'] - m, -m, pt['orelhas']['y0'] + 10.0), (ps['x'] + m, m, ps['topo']), det, 'detalhes', chanfro=0.3)
    for i, (px, pz) in enumerate(pt['pinosTorre']):
        for s in (-1, 1):
            P.pino(f'pino cônico {i}', px, pz, pt['raioPinoTorre'] * (1.0 if s > 0 else 0.85), det, 'detalhes', lado=s, de=lt - 0.3,
                   ate=lt + 0.25)
    return torre


def _cano_e_quebra_chamas(ficha, M):
    """O cano (o perfil da ficha, a alma de 5,56) e o quebra-chamas A2: o torno, a alma e as cinco fendas a 0°, ±60° e
    ±120° do alto — o fundo fica fechado (a arma não levanta poeira do chão)."""
    tn = ficha['tornos']
    det = M['detalhes']
    cano = P.torno('cano', tn['cano']['perfil'], det, 'detalhes', seg=40, chanfro=0.3)
    P.cortar(cano, P.torno('alma do cano', tn['alma']['perfil'], det, 'detalhes', seg=16))
    qc = P.torno('quebra-chamas', tn['quebraChamas']['perfil'], det, 'detalhes', seg=40, chanfro=0.3)
    # a alma com 30 lados e as fendas começando bem dentro dela: com 24 lados e as fendas a 4 mm do eixo o booleano
    # deixava arestas abertas onde a lateral da fenda cruzava a alma
    P.cortar(qc, P.torno('boca do quebra-chamas', [(-30.0, 0), (-30.0, 5.3), (1.0, 5.3), (1.0, 0)], det, 'detalhes', seg=30))
    for ang in (0, 60, -60, 120, -120):
        fenda = P.caixa(f'fenda do quebra-chamas {ang}', (-17.0, -1.3, 2.5), (-3.0, 1.3, 14.0), det, 'detalhes', chanfro=0)
        P.rotacionar(fenda, 'X', ang, (0, 0, 0))
        P.cortar(qc, fenda)
    return cano, qc


def construir(ficha, M):
    """A frente inteira no nível atual (pecas.iniciar)."""
    _anel_delta(ficha, M)
    _guarda_mao(ficha, M)
    _torre(ficha, M)
    _cano_e_quebra_chamas(ficha, M)
