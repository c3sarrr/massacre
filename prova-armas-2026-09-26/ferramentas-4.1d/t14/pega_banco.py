"""Tarefas 14 e 15 da 4.1d (a Nova e a P90 na mão): o banco de prova das mãos de uma arma de verdade, numa sessão do
Blender que fica aberta (t13/servidor.py) — o da Tarefa 13 (t13/awp_pega.py) para qualquer arma: a arma e as luvas
montadas uma vez, cada mão resolvida em segundos pelo mesmo caminho da pega do construir (empunhadura_pega._uma_mao, o
afundamento da palma e a validação da mão, conferir_mao).

Uso, num trabalho da fila do servidor (o espaço de nomes G persiste entre os trabalhos):
    import pega_banco as B
    B.configurar('nova', 'escopeta')   # a arma, a categoria (a regra) e a pasta de trabalho
    B.preparar()        # uma vez: a .blend da conferência da arma com as luvas montadas (<arma>_luvas.blend)
    B.carregar()        # abre <arma>_luvas.blend e monta o contexto do _uma_mao
    B.mao('d', {...})   # a mão direita com as correções (as chaves da regra da categoria); devolve o resumo
    B.mao('e', {...}, vistas='fora,jogador')
    B.no_fim_do_curso() # a última mão, com a peça do soquete dela no fim de cada passo (a mão de apoio da Nova, na bomba)
    B.resolver()        # a pega inteira, como no construir
A mão que entra com a luva da outra de obstáculo (`luva` na regra: a de apoio da P90, Tarefa 15) usa a última mão
resolvida desse lado (C['feitas']): a mão do gatilho primeiro, no mesmo trabalho — o afundamento da palma e a validação
dela contam a luva do gatilho posada, como no resolver.
O resumo traz o relatório da mão e as contas a mais desta prova: os nós (as juntas posadas, mm no referencial da arma),
para onde aponta a distal do polegar, a ponta dele, o dorso contra a câmera do jogador (a mão de apoio), as folgas para
cada peça do perto, a distância das distais ao eixo da peça de apoio e o alto de cada dedo. As vistas são renders
rápidos no Workbench (a luva posada com o afundamento da palma, a arma cinza) em <TRABALHO>/renders/<nome>_<vista>.png —
nada do jogo: só o nosso modelo.
"""
import copy
import importlib
import json
import math
import os
import sys
import tempfile
import time
import traceback

import numpy as np

import bpy
from mathutils import Matrix, Vector

RAIZ = r'C:\Users\T-Gamer\Desktop\game tiro\trabalho-4.1d'
SCRATCH = (r'C:\Users\T-Gamer\AppData\Local\Temp\claude\C--Users-T-Gamer-Desktop-game-tiro'
           r'\c7a63f39-8955-467e-9908-7a258f968380\scratchpad')
sys.path.insert(0, os.path.join(RAIZ, 'tools', 'blender'))

from armas import (empunhadura, empunhadura_arma as EA, empunhadura_palma as PALMA,  # noqa: E402
                   empunhadura_pega as EP, empunhadura_polegar as EPO, empunhadura_regras as ER,
                   empunhadura_validacao as V, fim_de_curso as FC, luvas, maos, maos_correcoes, maos_rig)
from armas.unidades import S  # noqa: E402

LADOS = {'d': 'direita', 'e': 'esquerda'}
# a direção da câmera do jogador a partir da mão de apoio (a de provas_lateral.py: de trás, da esquerda e de cima)
DO_JOGADOR = Vector((-0.42, 0.15, 0.12)).normalized()
# o eixo (y, z em mm) da peça de apoio de cada arma, para a distância das distais a ele: o cano da AWP no guarda-mão, o
# tubo do carregador da Nova dentro da bomba (tornos.tubo.centroY da ficha); na P90, o meio da abertura da frente (a
# altura do centro dela, ~−41 na ficha), por onde as pontas da mão de apoio podem enganchar
EIXO_DA_PECA = {'awp': (0.0, 0.0), 'nova': (0.0, -29.3), 'p90': (0.0, -41.0)}
try:
    C  # noqa: B018 — o contexto da sessão (carregar) sobrevive ao importlib.reload deste módulo
except NameError:
    C = {}
try:
    CFG  # noqa: B018
except NameError:
    CFG = {}


def configurar(arma, categoria, trabalho=None):
    """A arma (o id), a categoria dela (a regra da pega) e a pasta de trabalho (o rascunho da sessão, t14 por padrão)."""
    CFG.update({'arma': arma, 'categoria': categoria, 'trabalho': trabalho or os.path.join(SCRATCH, 't14')})
    CFG['blend'] = os.path.join(CFG['trabalho'], f'{arma}_luvas.blend')
    CFG['renders'] = os.path.join(CFG['trabalho'], 'renders')
    os.makedirs(CFG['renders'], exist_ok=True)
    print('CONFIGURAR', json.dumps(CFG, ensure_ascii=False), flush=True)


def contexto():
    """O contexto do construir da arma (o JSON que o lançador grava) com a categoria, a pega e as fichas relidas."""
    with open(os.path.join(tempfile.gettempdir(), 'massacre-blender', f"{CFG['arma']}-real.json"), encoding='utf-8') as f:
        ctx = json.load(f)
    ctx['categoria'] = CFG['categoria']
    ctx['pega'] = True
    with open(os.path.join(RAIZ, 'tools', 'blender', 'refs', f"{CFG['arma']}.json"), encoding='utf-8') as f:
        ctx['ficha'] = json.load(f)
    with open(os.path.join(RAIZ, 'tools', 'blender', 'refs', 'luvas.json'), encoding='utf-8') as f:
        ctx['luvas']['ficha'] = json.load(f)
    return ctx


def colecao(nome):
    col = bpy.data.collections.get(nome) or bpy.data.collections.new(nome)
    if col.name not in bpy.context.scene.collection.children:
        bpy.context.scene.collection.children.link(col)
    return col


def modulo_da_arma():
    return importlib.import_module(f"armas.{CFG['arma']}")


def preparar():
    """A .blend da conferência da arma (o construir sem a pega) com as duas luvas montadas pelo caminho do construir."""
    ctx = contexto()
    bpy.ops.wm.open_mainfile(filepath=os.path.join(RAIZ, 'tools', 'blender', 'conferencia', CFG['arma'],
                                                   f"{CFG['arma']}.blend"))
    t0 = time.time()
    EP.montar_luvas(ctx, colecao('luvas'))
    bpy.ops.wm.save_as_mainfile(filepath=CFG['blend'])
    print('PREPARAR luvas montadas em', round(time.time() - t0, 1), 's; gravado', CFG['blend'], flush=True)


def lacos(ficha):
    """As aberturas como a arma as corta (`lacos_dos_furos` no script dela), ou nenhuma."""
    a = modulo_da_arma()
    return a.lacos_dos_furos(ficha) if hasattr(a, 'lacos_dos_furos') else None


def base_da_prova(base=None):
    """A regra base: a da categoria, se já existe; senão (ou com o nome de uma base de prova), a da prova (a categoria
    sem os números da arma). As bases de prova ficam pelo nome, para as varreduras que partiram delas continuarem
    reproduzíveis depois que a regra da categoria existe."""
    base = base or CFG['categoria']
    if base in ER.REGRAS:
        return ER.REGRAS[base]
    if base in ('escopeta', 'escopeta_borda'):
        # a Nova pelo desenho da 4.1d (seção 5.2), a base das varreduras da Tarefa 14 antes da regra escopeta: a mão
        # direita do fuzil no pescoço da coronha com o polegar deitado por cima do pescoço, apontando para a frente; a
        # esquerda pela LATERAL na bomba, pelo soquete `bomba`, com o polegar deitado ao longo da borda de cima,
        # apontando para a boca ('borda', que não coube: a regra ficou com o 'baixo')
        return {'direita': {**copy.deepcopy(ER.RIFLE['direita']),
                            'polegar': {'deitado': True, 'face': (0.0, 0.0, 1.0), 'eixo': (1.0, 0.0, 0.0)}},
                'esquerda': {**copy.deepcopy(ER.LATERAL), 'soquete': 'bomba',
                             'lateral': {**ER.LATERAL['lateral'], 'polegar': 'borda'},
                             'polegar': {'deitado': True, 'face': (0.0, 0.0, 1.0), 'eixo': (1.0, 0.0, 0.0),
                                         'para_frente': True}}}
    if base == 'smgBullpup':
        # a P90 pelo desenho da 4.1d (seção 5.3), a base das varreduras da Tarefa 15 antes da regra smgBullpup: a mão
        # direita do fuzil no pescoço entre as duas aberturas, com o polegar pelo oval de trás (o furo `ovalTras`,
        # saindo no lado esquerdo e apontando para a frente, como o da AWP pelo buraco do polegar) e a palma chegando
        # com ele afastado; a esquerda pela LATERAL no lóbulo da frente (o soquete mao_e), com a luva da direita de
        # obstáculo (`luva`)
        return {'direita': {**copy.deepcopy(ER.RIFLE['direita']),
                            'polegar': {'furo': 'ovalTras', 'saida': (0.0, 1.0, 0.0), 'eixo': (1.0, 0.0, 0.0)},
                            'polegar_afastado': True},
                'esquerda': {**copy.deepcopy(ER.LATERAL), 'luva': 'd'}}
    raise ValueError(f'sem regra de prova para a categoria {base}')


def carregar():
    """Abre <arma>_luvas.blend e monta o contexto do _uma_mao em C (os furos da regra da prova pelos laços da arma)."""
    ctx = contexto()
    bpy.ops.wm.open_mainfile(filepath=CFG['blend'])
    mao = maos.Mao(ctx['luvas']['ficha'])
    bracos = {lado: (bpy.data.objects[f'luva_{lado}'], bpy.data.objects[f'rig_{lado}']) for lado in ('d', 'e')}
    perto = {o.name[len('perto_'):]: o for o in bpy.data.collections['perto'].objects if o.type == 'MESH'}
    soqs = {o.name[len('soquete_'):]: o for o in bpy.data.collections['soquetes'].objects}
    objetos = [o for k, o in perto.items() if not k.startswith('_')]
    arma = EA.Arma(objetos)
    t0 = time.time()
    furos = EP.furos_da_regra(ctx['ficha'], base_da_prova(), arma, lacos(ctx['ficha']))
    C.clear()
    C.update({'ctx': ctx, 'mao': mao, 'bracos': bracos, 'perto': perto, 'soqs': soqs, 'objetos': objetos,
              'arma': arma, 'furos': furos,
              'contexto': (mao, bracos, objetos, arma, EA.Arma([perto['base']]), soqs, perto, furos)})
    print('CARREGAR', CFG['blend'], 'peças', sorted(perto), 'soquetes', sorted(soqs), 'furos', sorted(furos),
          round(time.time() - t0, 1), 's', flush=True)


def tuplas(d):
    """As listas do JSON como tuplas (as regras usam tuplas; o `giros` é uma tupla de pares)."""
    def t(v):
        return tuple(t(x) for x in v) if isinstance(v, list) else v
    return {k: (t(v) if isinstance(v, list) else ({kk: t(vv) for kk, vv in v.items()} if isinstance(v, dict) else v))
            for k, v in d.items()}


def regra(lado, correcoes=None, base=None):
    """A regra da mão do `lado` com as correções por cima (as chaves novas também entram: é uma prova)."""
    r = copy.deepcopy(base_da_prova(base)[LADOS[lado]])
    for k, v in tuplas(correcoes or {}).items():
        r[k] = v
    return r


def _nos(f, lado):
    """As juntas posadas (as cabeças dos ossos, mm no referencial da arma)."""
    luva, rig = C['bracos'][lado]
    maos_rig.posar(rig, f['m'].pose())
    bpy.context.view_layer.update()
    e = f['na'].encaixe
    nos = {o: [round(c, 1) for c in e @ (rig.pose.bones[f'{o}_{lado}'].head / S)]
           for o in ('mao', 'polegar_1', 'polegar_2', 'polegar_3', 'indicador_1', 'medio_1', 'anelar_1', 'minimo_1',
                     'indicador_3', 'medio_3', 'anelar_3', 'minimo_3')}
    maos_rig.posar(rig, {})
    bpy.context.view_layer.update()
    return nos


def _extras(f, lado, pts):
    """As contas a mais desta prova (ver o cabeçalho)."""
    col, na = f['col'], f['na']
    dono = np.array(col.dono)
    pts = np.asarray(pts)
    ex = {'nos': _nos(f, lado)}
    cadeia = EPO.Cadeia(col, C['mao'], {})
    ms = cadeia.matrizes(EPO.graus_da_pose(f['m'], cadeia))
    distal = (na.encaixe.to_3x3() @ (ms[2].to_3x3() @ Vector((0.0, 1.0, 0.0)))).normalized()
    ex['distalDoPolegar'] = [round(v, 3) for v in distal]
    ex['distalAFrenteGraus'] = round(math.degrees(distal.angle(Vector((1.0, 0.0, 0.0)))), 1)
    p2 = pts[dono == 'polegar_2'].mean(0)
    p3 = pts[dono == 'polegar_3']
    ponta = p3[np.argmax(((p3 - p2) ** 2).sum(1))]
    ex['pontaDoPolegar'] = [round(float(c), 1) for c in ponta]
    ex['centros'] = {o: [round(float(c), 1) for c in pts[dono == o].mean(0)]
                     for o in ('polegar_2', 'polegar_3', 'mao', 'indicador_3', 'medio_3', 'minimo_3')}
    dorso = na.encaixe.to_3x3() @ Vector((0.0, 0.0, 1.0))
    ex['dorso'] = [round(v, 3) for v in dorso]
    ex['dorsoAoJogadorGraus'] = round(math.degrees(dorso.angle(DO_JOGADOR)), 1)
    # as folgas da luva para as peças do perto (cada uma sozinha)
    folgas = {}
    for nome, ob in C['perto'].items():
        if nome.startswith('_'):
            continue
        peca = EA.Arma([ob])
        folgas[nome] = round(min(peca.distancia(Vector(q), 40.0) or 40.0 for q in pts), 2)
    ex['folgasMM'] = folgas
    # a menor distância da pele de cada distal ao eixo da peça de apoio (EIXO_DA_PECA) e o alto de cada dedo
    ey, ez = EIXO_DA_PECA.get(CFG['arma'], (0.0, 0.0))
    ex['distalAoEixoMM'] = {d: round(float(np.hypot(pts[dono == f'{d}_3'][:, 1] - ey,
                                                     pts[dono == f'{d}_3'][:, 2] - ez).min()), 1)
                            for d in ('indicador', 'medio', 'anelar', 'minimo')}
    ex['altoDoDedoMM'] = {d: round(float(pts[np.isin(dono, [f'{d}_{i}' for i in (1, 2, 3)])][:, 2].max()), 1)
                          for d in ('indicador', 'medio', 'anelar', 'minimo')}
    # onde a luva entra na arma: a maior entrada de cada osso (mm, só os que entram mais de 0,05), da maior para a menor,
    # com o vértice e a peça mais perto dele
    entradas = {}
    for i, q in enumerate(pts):
        d = C['arma'].distancia(Vector(q), 2.0)
        if d is not None and d < -0.05 and -d > entradas.get(col.dono[i], (0.0,))[0]:
            entradas[col.dono[i]] = (-d, i)
    ex['entraPorOsso'] = {o: [round(e, 3), i, [round(float(c), 1) for c in pts[i]]]
                          for o, (e, i) in sorted(entradas.items(), key=lambda kv: -kv[1][0])[:6]}
    return ex


def mao(lado, correcoes=None, vistas=None, nome=None, base=None):
    """Uma mão da regra (as correções por cima) na arma: o _uma_mao, o afundamento e a validação. Devolve o resumo e
    imprime a linha PROVA."""
    t0 = time.time()
    r = regra(lado, correcoes, base)
    saida = {'lado': lado, 'correcoes': correcoes or {}}
    feitas = C.setdefault('feitas', {})
    outra = r.get('luva')
    if outra and outra not in feitas:
        raise RuntimeError(f'a mão {lado} entra com a luva {outra} de obstáculo: resolva a mão {outra} antes')
    try:
        f = EP._uma_mao(C['contexto'], lado, r, {k: v['f'] for k, v in feitas.items()})
    except (empunhadura.PolegarCruza, EA.ChegadaCruza, RuntimeError) as erro:
        saida.update({'erro': f'{type(erro).__name__}: {erro}', 'segundos': round(time.time() - t0, 1)})
        print('PROVA', json.dumps(saida, ensure_ascii=False), flush=True)
        traceback.print_exc()
        return saida
    arma, objetos, perto = C['arma'], C['objetos'], C['perto']
    # a luva da outra mão posada, com o afundamento dela: o obstáculo do afundamento desta e a da validação (resolver)
    luva_outra = None if not outra else EP._luva_posada(feitas[outra]['f'], arma, feitas[outra]['afundar'])
    obstaculo = arma if luva_outra is None else EA.Arma(objetos, extra=[luva_outra])
    afundar = PALMA.afundamento(EA.NaArma(f['col'], obstaculo, f['na'].encaixe), f['m'].pose())
    luva = C['bracos'][lado][0]
    rel, _sondas, problemas = V.conferir_mao(f, LADOS[lado], C['mao'], luva, arma, objetos, perto, afundar,
                                             luva_outra, outra)
    feitas[lado] = {'f': f, 'afundar': afundar}
    pts = EA.NaArma(f['col'], arma, f['na'].encaixe, ceder=False, afundar=afundar).pontos(f['m'].pose())
    saida.update({k: rel[k] for k in ('palmaAndouMM', 'dedosPararam', 'juntar', 'indicador', 'polegar', 'ladosLateral',
                                      'polegarNoFuro', 'penetracaoMM', 'contatosMM', 'palmaMeioMM', 'juntosMM', 'palma',
                                      'angulos', 'luva', 'penetracaoLuvaMM', 'folgaLuvaMM', 'pertoDaLuva',
                                      'contatosLuvaMM') if k in rel})
    saida.update(_extras(f, lado, pts))
    saida.update({'problemas': problemas, 'segundos': round(time.time() - t0, 1)})
    print('PROVA', json.dumps(saida, ensure_ascii=False, default=str), flush=True)
    C['ultima'] = {'f': f, 'afundar': afundar, 'lado': lado}
    if vistas:
        renders(f, lado, afundar, nome or f'{lado}_{int(time.time())}', vistas)
    return saida


def no_fim_do_curso(f=None, afundar=None):
    """A mão `f` (a última, sem ela) com a peça do soquete dela (o `peca` do vazio: a bomba da Nova) no fim de cada passo
    da ordem dela, e a que ela arrasta junto: a luva posada levada com a mesma mudança da peça, e a entrada dela (mm) na
    arma com as peças movidas, pela distância com sinal da validação (sem o limite das buscas). Devolve {passo:
    {penetracaoMM, folgasMM: {peça: mm}}} (None sem peça)."""
    if f is None:
        f, afundar = C['ultima']['f'], C['ultima']['afundar']
    soq = C['soqs'][f['r']['soquete']]
    nome = soq.get('peca')
    if not nome:
        return None
    pecas = {k: o for k, o in C['perto'].items() if not k.startswith('_') and '/' not in k}
    ob = pecas[nome]
    m = FC.movimento(ob)
    repouso = {k: o.matrix_world.copy() for k, o in pecas.items()}
    matrizes = {nome: repouso[nome].copy()}
    arrastada = (m['arrasta'] or {}).get('peca')
    if arrastada in pecas:
        matrizes[arrastada] = repouso[arrastada].copy()
    saida = {}
    try:
        for passo in m['ordem']:
            matrizes[nome] = FC._passo(ob, matrizes[nome], m, passo)
            if passo == 'curso' and arrastada in pecas:
                ma = FC.movimento(pecas[arrastada])
                matrizes[arrastada] = FC._passo(pecas[arrastada], matrizes[arrastada],
                                                {'eixo': ma['eixo'] or m['eixo'], 'curso': m['curso']}, 'curso',
                                                m['arrasta']['razao'])
            for k, mt in matrizes.items():
                pecas[k].matrix_world = mt
            bpy.context.view_layer.update()
            delta = matrizes[nome] @ repouso[nome].inverted()
            delta_mm = Matrix.Translation(delta.translation / S) @ delta.to_3x3().to_4x4()
            arma_fim = EA.Arma(list(pecas.values()))
            na = EA.NaArma(f['col'], arma_fim, delta_mm @ f['na'].encaixe, ceder=False, afundar=afundar)
            pts = na.pontos(f['m'].pose())
            folgas = {}
            for k, o in pecas.items():
                if k == nome:
                    continue
                peca = EA.Arma([o])
                folgas[k] = round(min(peca.distancia(Vector(q), 40.0) or 40.0 for q in pts), 2)
            saida[passo] = {'penetracaoMM': round(na.penetracao(pts, limite=None), 3), 'folgasMM': folgas,
                            'deslocamentoMM': [round(v, 1) for v in delta_mm.translation]}
    finally:
        for k, mt in repouso.items():
            pecas[k].matrix_world = mt
        bpy.context.view_layer.update()
    print('FIM-DO-CURSO', nome, json.dumps(saida, ensure_ascii=False), flush=True)
    return saida


def resolver(vistas_d=None, vistas_e=None, nome='pega'):
    """A pega inteira pelo caminho do construir (empunhadura_pega.resolver com a regra da categoria, o EMPUNHADURA da
    arma e os laços dela): imprime a seção `empunhadura` do relatório e os problemas; com as vistas, renders das duas
    mãos posadas (o afundamento da palma de cada uma)."""
    a = modulo_da_arma()
    ctx = C['ctx']
    soqs = list(bpy.data.collections['soquetes'].objects)
    t0 = time.time()
    pega, rel, problemas = EP.resolver(ctx, C['mao'], C['bracos'], C['perto'], soqs, getattr(a, 'EMPUNHADURA', None),
                                       lacos(ctx['ficha']))
    print('RESOLVER', round(time.time() - t0, 1), 's')
    print('RELATORIO', json.dumps(rel, ensure_ascii=False, default=str))
    print('PROBLEMAS', json.dumps(problemas, ensure_ascii=False), flush=True)
    C['pega'] = pega
    for lado, quais in (('d', vistas_d), ('e', vistas_e)):
        if quais and lado in pega:
            dados = pega[lado]
            f = {'m': type('Pose', (), {'pose': staticmethod(lambda d=dados: d['pose'])})(),
                 'na': type('Encaixe', (), {'encaixe': dados['encaixe']})(),
                 'r': ER.regra(ctx['categoria'], getattr(a, 'EMPUNHADURA', None))[LADOS[lado]]}
            renders(f, lado, dados['palma'], f'{nome}_{lado}', quais)
    return pega, rel, problemas


# ------------------------------------------------------------------------------------------------ vistas
# (posição da câmera a partir do soquete da mão, alvo a partir dele; metros, referencial da arma), lente
VISTAS = {
    'd': {'dir': ((0.0, -0.32, 0.02), (0.0, 0.0, 0.0), 50), 'esq': ((0.0, 0.32, 0.02), (0.0, 0.0, 0.0), 50),
          'baixo': ((0.04, -0.06, -0.32), (0.0, 0.0, 0.0), 50), 'tras': ((-0.22, -0.14, 0.16), (0.02, 0.0, 0.0), 45),
          'cima': ((0.0, -0.04, 0.34), (0.0, 0.0, 0.0), 50), 'esqbaixo': ((0.05, 0.28, -0.14), (0.0, 0.0, 0.0), 50),
          'esqcima': ((-0.10, 0.22, 0.20), (0.0, 0.0, 0.0), 50)},
    'e': {'fora': ((0.0, 0.34, -0.02), (0.0, 0.0, -0.03), 50), 'baixo': ((0.03, 0.10, -0.34), (0.0, 0.0, -0.03), 50),
          'cima': ((0.02, 0.06, 0.34), (0.0, 0.0, -0.02), 50),
          'jogador': (tuple(0.45 * c for c in DO_JOGADOR), (0.0, 0.0, -0.03), 50),
          'dir': ((0.0, -0.34, -0.02), (0.0, 0.0, -0.03), 50), 'frente': ((0.30, 0.10, -0.06), (0.0, 0.0, -0.03), 50)},
}


def renders(f, lado, afundar, nome, quais):
    """A luva posada (o afundamento da palma junto) na arma cinza, renders rápidos no Workbench; com a outra mão
    resolvida no servidor (C['feitas']: a do gatilho, quando esta é a de apoio da P90, que entra com a luva dela de
    obstáculo), ela também, na cor dela — as duas juntas embaixo da arma."""
    sc = bpy.context.scene
    sc.render.engine = 'BLENDER_WORKBENCH'
    sc.display.shading.light = 'STUDIO'
    sc.display.shading.color_type = 'OBJECT'
    sc.display.shading.show_cavity = True
    sc.display.shading.show_shadows = False
    sc.render.resolution_x, sc.render.resolution_y = 960, 720
    sc.render.film_transparent = False
    col = colecao('maos_da_prova')
    for o in list(col.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    for c in bpy.context.scene.collection.children:
        c.hide_render = c.name not in ('perto', 'maos_da_prova')
    for o in C['perto'].values():
        o.color = (0.55, 0.57, 0.6, 1.0)
        o.hide_render = False
    posadas = [(lado, f, afundar)]
    if (f.get('r') or {}).get('luva') in C.get('feitas', {}):
        outra = f['r']['luva']
        posadas.append((outra, C['feitas'][outra]['f'], C['feitas'][outra]['afundar']))
    for lado_p, f_p, afundar_p in posadas:
        luva, rig = C['bracos'][lado_p]
        modelo = maos_correcoes.Modelo(luva, rig, C['mao'], luvas.REFORCO)
        ob = modelo.para_malha(f'prova_{lado_p}', col, f_p['m'].pose(), {'vertices': afundar_p['vertices'],
                                                                          'vetores': afundar_p['vetores']})
        e = f_p['na'].encaixe.copy()
        e.translation = e.translation * S
        ob.matrix_world = e
        ob.color = (0.62, 0.42, 0.25, 1.0) if lado_p == 'd' else (0.30, 0.45, 0.62, 1.0)
        ob.hide_render = False
        maos_rig.posar(rig, {})
    soquete = (f.get('r') or regra(lado))['soquete'] if isinstance(f, dict) else regra(lado)['soquete']
    c = C['soqs'][soquete].matrix_world.translation.copy()
    for vista in quais.split(','):
        pos, alvo, lente = VISTAS[lado][vista]
        cam = bpy.data.objects.get(f'cam_{vista}')
        if cam is None:
            cam = bpy.data.objects.new(f'cam_{vista}', bpy.data.cameras.new(f'cam_{vista}'))
            sc.collection.objects.link(cam)
        p, a = c + Vector(pos), c + Vector(alvo)
        cam.location = p
        cam.rotation_euler = (a - p).to_track_quat('-Z', 'Y').to_euler()
        cam.data.lens = lente
        cam.data.clip_start = 0.002
        sc.camera = cam
        sc.render.filepath = os.path.join(CFG['renders'], f'{nome}_{vista}.png')
        bpy.ops.render.render(write_still=True)
    print('VISTAS', nome, quais, flush=True)
