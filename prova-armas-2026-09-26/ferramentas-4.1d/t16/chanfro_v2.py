"""Protótipo (Tarefa 16, correção C4): o desdobrar do chanfro local tira o chanfro da aresta inteira, e os defeitos
ficam nas pontas das arestas longas (a quina em que elas encontram outras): na AWP de jogo, a aresta de cima da coronha
(220 mm) cai de 3,5 mm para 0,59 por causa de dobras a 5 mm da ponta. Aqui, com --trechos, a aresta longa em volta do
defeito é dividida em pedaços (TRECHO_MM) e só os pedaços perto dele perdem peso; a rampa até a largura cheia sai do
GRADIENTE do chanfro_local._suavizar. Com pesos diferentes em arestas alinhadas, a conta do limite global do Blender
divide pelo seno de quase zero e zera o chanfro da peça: as peças do chanfro local saem com o 'clamp overlap' desligado
(os pesos já respeitam as folgas) e a conta de _respeitar pula o par alinhado (--sem-clamp, que --trechos liga). Mede,
por peça, o chanfro (a largura vezes o comprimento) antes e depois do desdobrar, os vértices novos e as dobras de todas
as peças no fim (dobras.dobras na forma canônica, como a validação) e os triângulos de cada nível.
Com --trecho <mm> o tamanho dos pedaços (2 mm) e com --largura-minima <mm> a largura abaixo da qual a aresta é reduzida
inteira (0: todas divididas). Com --curtas, sem dividir nada: em volta de cada defeito, se há aresta curta entre as que
seriam reduzidas (até CURTA vezes o alcance), só as curtas perdem peso naquele passo; as longas, só quando não sobra
curta (a quina se resolve muitas vezes pelas arestas curtas dela, sem tirar o chanfro da aresta longa inteira).
    blender -b --factory-startup -P chanfro_v2.py -- <arma> <nivel> [--sem-clamp] [--trechos] [--trecho <mm>]
        [--largura-minima <mm>] [--curtas [vezes]] [--despejo <pasta>]
"""
import importlib
import json
import math
import os
import sys
import time

sys.path.insert(0, r'C:\Users\T-Gamer\Desktop\game tiro\trabalho-4.1d\tools\blender')
import bmesh  # noqa: E402
import bpy  # noqa: E402

from armas import canonica, dobras, lod, pecas, soquetes  # noqa: E402
from armas import chanfro_local as CL  # noqa: E402
from armas.unidades import S  # noqa: E402

a = sys.argv[sys.argv.index('--') + 1:]
ARMA, NIVEL = a[0], a[1]
TRECHOS = '--trechos' in a
CURTAS = '--curtas' in a
CURTA = (float(a[a.index('--curtas') + 1]) if CURTAS and len(a) > a.index('--curtas') + 1
         and not a[a.index('--curtas') + 1].startswith('--') else 4.0)
SEM_CLAMP = '--sem-clamp' in a or TRECHOS
DESPEJO = a[a.index('--despejo') + 1] if '--despejo' in a else None
TRECHO_MM = float(a[a.index('--trecho') + 1]) if '--trecho' in a else 2.0
LARGURA_MINIMA = float(a[a.index('--largura-minima') + 1]) if '--largura-minima' in a else 0.0
mod = importlib.import_module(f'armas.{ARMA}')
ficha = json.load(open(rf'C:\Users\T-Gamer\Desktop\game tiro\trabalho-4.1d\tools\blender\refs\{ARMA}.json',
                       encoding='utf-8'))
bpy.ops.wm.read_factory_settings(use_empty=True)
original = CL.desdobrar


def respeitar_sem_alinhadas(bm, w, cantos, t):
    """CL._respeitar com o termo do par alinhado (o seno do ângulo da face abaixo de SENO_ALINHADO) fora da conta: os
    deslocamentos de duas arestas em linha são paralelos e não se encontram no vértice entre elas."""
    mudou = False
    chanfrados = CL._vertices_chanfrados(bm, w)
    for vb, ia, ib, ic, comp, s1, c1, s2, c2, des_a, des_c in cantos:
        if vb not in chanfrados:
            continue
        wa, wb, wc = w[ia], w[ib], w[ic]
        if wa <= 0.0 and wb <= 0.0 and wc <= 0.0:
            continue
        soma = (((wa + c1 * wb) / s1 if abs(s1) >= CL.SENO_ALINHADO else 0.0) +
                ((wc + c2 * wb) / s2 if abs(s2) >= CL.SENO_ALINHADO else 0.0))
        if soma * t > CL.MARGEM * comp * (1.0 + CL.FOLGA_NUMERICA):
            k = CL.MARGEM * comp / (soma * t)
            for i in (ia, ib, ic):
                if w[i] > 0.0:
                    w[i] *= k
            mudou = True
            wa, wb, wc = w[ia], w[ib], w[ic]
        if wb > 0.0:
            folga = min(des_a if wa <= 0.0 else math.inf, des_c if wc <= 0.0 else math.inf)
            if wb * t > CL.MARGEM * folga * (1.0 + CL.FOLGA_NUMERICA):
                w[ib] = max(0.0, CL.MARGEM * folga / t)
                mudou = True
    return mudou


if SEM_CLAMP:
    CL._respeitar = respeitar_sem_alinhadas
    CL._grupos = lambda bm: []


def soma_chanfro(me, largura):
    at = me.attributes.get(CL.CAMADA)
    w = [0.0] * len(me.edges)
    if at is not None:
        at.data.foreach_get('value', w)
    return sum(x * (me.vertices[e.vertices[0]].co - me.vertices[e.vertices[1]].co).length / S
               for x, e in zip(w, me.edges)) * largura


def dividir(bm, e, cortes):
    """Divide a aresta `e` nas distâncias `cortes` (unidades do Blender, a partir de e.verts[0], em ordem). Devolve os
    pedaços na ordem."""
    v0 = e.verts[0]
    pedacos = []
    atual, origem, feito = e, v0, 0.0
    for s in cortes:
        comp = atual.calc_length()
        fac = (s - feito) / comp
        if fac <= 1e-6 or fac >= 1.0 - 1e-6:
            continue
        ne, nv = bmesh.utils.edge_split(atual, origem, fac)
        tras = ne if origem in ne.verts else atual
        frente = atual if tras is ne else ne
        pedacos.append(tras)
        atual, origem, feito = frente, nv, s
    pedacos.append(atual)
    return pedacos


def desdobrar_trechos(ob, chanfro):
    """CL.desdobrar com a divisão das arestas longas em volta de cada defeito (ver acima)."""
    finais = [m for m in ob.modifiers if m.name.startswith('corte final')]
    vistos = [m.show_viewport for m in finais]
    for m in finais:
        m.show_viewport = False
    chanfro.show_viewport = False
    antes = CL._arvore(CL._defeitos(ob))
    chanfro.show_viewport = True
    t = chanfro.width
    me = ob.data
    sobra = 0
    divididas = 0
    for _ in range(CL.PASSOS_DESDOBRAR + 1):
        novos = [p for p in CL._defeitos(ob) if not CL._perto(antes, p, CL.COLISAO_ANTES * S)]
        sobra = len(novos)
        if not novos:
            break
        bm = bmesh.new()
        bm.from_mesh(me)
        bm.edges.index_update()
        camada = bm.edges.layers.float.get(CL.CAMADA)
        alcance = t * CL.ALCANCE + 0.02 * S
        chanfradas = [e for e in bm.edges if e[camada] > 0.0]
        meios = CL._arvore([(e.verts[0].co + e.verts[1].co) / 2 for e in chanfradas])
        meia_maior = max((e.calc_length() / 2 for e in chanfradas), default=0.0)
        reduzir = {}  # aresta → os pontos dos defeitos em volta dela
        for p in novos:
            if meios is None:
                break
            em_volta = [chanfradas[i] for _co, i, _d in meios.find_range(p, meia_maior + alcance)
                        if CL._distancia_ao_segmento(p, chanfradas[i].verts[0].co, chanfradas[i].verts[1].co) <= alcance]
            if not em_volta:
                continue
            maior = max(e[camada] for e in em_volta)
            for e in em_volta:
                if e[camada] >= CL.MAIORES * maior:
                    reduzir.setdefault(e, []).append(p)
        if not reduzir:
            bm.free()
            break
        # as arestas longas: a parte a até o alcance de cada defeito, mais a rampa do gradiente dos dois lados, em
        # pedaços de TRECHO_MM; o resto da aresta fica inteiro
        cortar = []
        inteiras = []
        for e, pontos in reduzir.items():
            a0, a1 = e.verts[0].co.copy(), e.verts[1].co.copy()
            comp = (a1 - a0).length
            # a rampa inteira (do zero à largura dela): a redução final não se sabe no começo
            rampa = e[camada] * t / CL.GRADIENTE
            zonas = []
            for p in pontos:
                s = max(0.0, min(comp, (p - a0).dot(a1 - a0) / comp))
                d = CL._distancia_ao_segmento(p, a0, a1)
                meia = math.sqrt(max(0.0, alcance * alcance - d * d))
                zonas.append((max(0.0, s - meia - rampa), min(comp, s + meia + rampa)))
            zonas.sort()
            juntas = []
            for z in zonas:
                if juntas and z[0] <= juntas[-1][1]:
                    juntas[-1] = (juntas[-1][0], max(juntas[-1][1], z[1]))
                else:
                    juntas.append(z)
            coberto = sum(z1 - z0 for z0, z1 in juntas)
            if comp > 2 * TRECHO_MM * S and coberto < 0.8 * comp and e[camada] * t >= LARGURA_MINIMA * S:
                cortes = []
                for z0, z1 in juntas:
                    n = max(1, round((z1 - z0) / (TRECHO_MM * S)))
                    cortes.extend(z0 + (z1 - z0) * k / n for k in range(n + 1))
                cortar.append((e, sorted(set(c for c in cortes if 0.0 < c < comp)), pontos))
            else:
                inteiras.append(e)
        for e in inteiras:
            e[camada] *= CL.DESDOBRAR
        for e, cortes, pontos in cortar:
            for pedaco in dividir(bm, e, cortes):
                m = (pedaco.verts[0].co + pedaco.verts[1].co) / 2
                if any(CL._distancia_ao_segmento(p, pedaco.verts[0].co, pedaco.verts[1].co) <= alcance or
                       (m - p).length <= alcance for p in pontos):
                    pedaco[camada] *= CL.DESDOBRAR
            divididas += 1
        bm.edges.index_update()
        w = [e[camada] for e in bm.edges]
        w = CL.pesos(bm, t, True, w)
        CL._gravar(bm, me, w)
    for m, v in zip(finais, vistos):
        m.show_viewport = v
    ob['divididas'] = divididas
    return sobra


def desdobrar_curtas(ob, chanfro):
    """CL.desdobrar com as arestas curtas primeiro em volta de cada defeito (ver acima)."""
    finais = [m for m in ob.modifiers if m.name.startswith('corte final')]
    vistos = [m.show_viewport for m in finais]
    for m in finais:
        m.show_viewport = False
    chanfro.show_viewport = False
    antes = CL._arvore(CL._defeitos(ob))
    chanfro.show_viewport = True
    t = chanfro.width
    me = ob.data
    sobra = 0
    for _ in range(2 * CL.PASSOS_DESDOBRAR + 1):
        novos = [p for p in CL._defeitos(ob) if not CL._perto(antes, p, CL.COLISAO_ANTES * S)]
        sobra = len(novos)
        if not novos:
            break
        bm = bmesh.new()
        bm.from_mesh(me)
        bm.edges.index_update()
        camada = bm.edges.layers.float.get(CL.CAMADA)
        w = [e[camada] for e in bm.edges]
        alcance = t * CL.ALCANCE + 0.02 * S
        chanfradas = [e for e in bm.edges if w[e.index] > 0.0]
        meios = CL._arvore([(e.verts[0].co + e.verts[1].co) / 2 for e in chanfradas])
        meia_maior = max((e.calc_length() / 2 for e in chanfradas), default=0.0)
        reduzir = set()
        for p in novos:
            if meios is None:
                break
            em_volta = [chanfradas[i] for _co, i, _d in meios.find_range(p, meia_maior + alcance)
                        if CL._distancia_ao_segmento(p, chanfradas[i].verts[0].co, chanfradas[i].verts[1].co) <= alcance]
            if not em_volta:
                continue
            maior = max(w[e.index] for e in em_volta)
            alvo = [e for e in em_volta if w[e.index] >= CL.MAIORES * maior]
            curtas = [e for e in alvo if e.calc_length() <= CURTA * alcance]
            reduzir.update(e.index for e in (curtas or alvo))
        if not reduzir:
            bm.free()
            break
        for i in reduzir:
            w[i] *= CL.DESDOBRAR
        w = CL.pesos(bm, t, True, w)
        CL._gravar(bm, me, w)
    for m, v in zip(finais, vistos):
        m.show_viewport = v
    return sobra


def desdobrar(ob, chanfro):
    if SEM_CLAMP:
        chanfro.use_clamp_overlap = False
    largura = chanfro.width / S
    soma0 = soma_chanfro(ob.data, largura)
    nv0 = len(ob.data.vertices)
    t0 = time.time()
    sobra = (desdobrar_trechos(ob, chanfro) if TRECHOS else desdobrar_curtas(ob, chanfro) if CURTAS
             else original(ob, chanfro))
    soma1 = soma_chanfro(ob.data, largura)
    if abs(soma1 - soma0) > 1e-9 or sobra:
        print('PECA', json.dumps({'peca': ob.name, 'largura': round(largura, 3), 'antes': round(soma0, 3),
                                  'depois': round(soma1, 3), 'perda': round(100 * (1 - soma1 / soma0), 1) if soma0 else 0,
                                  'sobra': sobra, 'verticesNovos': len(ob.data.vertices) - nv0,
                                  'divididas': ob.get('divididas', 0), 'segundos': round(time.time() - t0, 1)},
                                 ensure_ascii=False), flush=True)
    return sobra


CL.desdobrar = desdobrar


class Materiais(dict):
    def __missing__(self, k):
        return self.setdefault(k, bpy.data.materials.new(k))


t = time.time()
col = pecas.iniciar(NIVEL, NIVEL)
mod.construir(ficha, Materiais())
pecas.finalizar(col)
print('CONSTRUIDA', round(time.time() - t, 1), 's', flush=True)
total = {}
objs = [o for o in col.objects if o.type == 'MESH' and not o.get('cortador')]
for ob in sorted(objs, key=lambda o: o.name):
    me = canonica.avaliada(ob)
    bm = bmesh.new()
    bm.from_mesh(me)
    bm.transform(ob.matrix_world)
    ds = dobras.dobras(bm)
    bm.free()
    bpy.data.meshes.remove(me)
    if ds:
        tipos = {}
        for p, k in ds:
            tipos.setdefault(k, []).append([round(c / S, 2) for c in p])
        for k, ps in tipos.items():
            total[k] = total.get(k, 0) + len(ps)
        print('DOBRA', ob.name, json.dumps({k: [len(ps), ps[:8]] for k, ps in tipos.items()}, ensure_ascii=False),
              flush=True)
# o perto como o construir o junta (sem as faces escondidas dentro de outra peça da base), para o orçamento
destino = bpy.data.collections.new('perto')
bpy.context.scene.collection.children.link(destino)
partes = soquetes.juntar_pecas(col, destino, 'perto', mod.pivos(ficha), lambda ob: lod.no_nivel(ob, 'perto'))
print('TRIANGULOS', json.dumps({'bruto': lod.triangulos(objs),
                                'perto': lod.triangulos([o for k, o in partes.items() if not k.startswith('_')]),
                                'escondidas': partes['_removidas']}), flush=True)
modo = [k for k in ('--sem-clamp', '--trechos', '--curtas') if k in a] + [f'{k} {a[a.index(k) + 1]}' for k in
                                                                           ('--trecho', '--largura-minima') if k in a]
print('TOTAL', ARMA, NIVEL, ' '.join(modo) or 'como o construir', json.dumps(total), flush=True)
if DESPEJO:
    os.makedirs(DESPEJO, exist_ok=True)
    nome = '_'.join(m[2:].replace(' ', '') for m in modo)
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(DESPEJO, f'{ARMA}_{NIVEL}_{nome}.blend'))
