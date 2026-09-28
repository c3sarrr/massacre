# Ponto de entrada do Blender para as armas realistas (Fase 4.1a; desenho em docs/superpowers/specs/
# 2026-09-26-armas-realistas-design.md, seção 4), chamado por tools/blender.mjs:
#   blender -b --factory-startup --python-exit-code 1 -P tools/blender/armas/principal.py -- <ação> <contexto.json>
# Ações: construir (modelo alto e de jogo, zonas, peças móveis, soquetes, UV, assar, LODs, validar, gravar a .blend da
# conferência e exportar), validar (reabre a .blend e refaz a validação, sem exportar) e conferir (reabre a .blend e
# renderiza as vistas). Desde a 4.1b o construir resolve também a pega das luvas (empunhadura_pega.py) e o validar a refaz. O contexto (JSON) traz a ficha, a pintura de fábrica, as peças, as zonas, os soquetes, o
# orçamento, as pastas e o hash das entradas. O alvo `luvas` (Fase 4.1b) tem as mesmas três ações em luvas.py. As linhas `MASSACRE-*` da saída são lidas pelo lançador; reprovado sai com
# código 1 (o lançador mostra os problemas).
import importlib
import json
import os
import sys
import time

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(AQUI))

import bpy  # noqa: E402

from armas import (assar, conferir, empunhadura_pega, exportar, lod, luvas, materiais, pecas, soquetes,  # noqa: E402
                   validar, zonas)


def _colecao(nome):
    col = bpy.data.collections.get(nome) or bpy.data.collections.new(nome)
    if col.name not in bpy.context.scene.collection.children:
        bpy.context.scene.collection.children.link(col)
    return col


def _malhas(col):
    return [o for o in col.objects if o.type == 'MESH' and not o.get('cortador')]


def _lados(ctx):
    orc = ctx['orcamento']
    lados = {}
    for sufixo, esperado in (('n', orc['textura']), ('m', orc['textura']), ('mundo_n', orc['texturaMundo']), ('mundo_m', orc['texturaMundo'])):
        nome = f"{ctx['id']}_{sufixo}.webp"
        img = bpy.data.images.load(os.path.join(ctx['saida'], nome), check_existing=False)
        lados[nome] = (img.size[0], esperado)
        bpy.data.images.remove(img)
    return lados


def _pecas(partes):
    return [o for k, o in partes.items() if not k.startswith('_')]


def _etapa(t0, nome):
    """Linha de progresso para o lançador: o construir leva minutos (assar no Cycles) e o terminal não fica mudo."""
    print('MASSACRE-ETAPA', json.dumps({'etapa': nome, 's': round(time.time() - t0, 1)}, ensure_ascii=False), flush=True)


def _validar(ctx, arma, lods, jogo):
    """A validação da seção 4.6 sobre o que foi construído: as peças de jogo (malha, cano), os níveis (silhueta, medidas,
    triângulos, peças, zonas), os soquetes, as texturas gravadas e as UVs dos dois conjuntos (perto e mundo; o longe
    usa as do mundo)."""
    pecas_jogo = _malhas(jogo)
    soquetes_def = arma.soquetes(ctx['ficha'])
    nomes_soq = [o.name[len('soquete_'):] for o in bpy.data.collections['soquetes'].objects]
    perto = _pecas(lods['perto'])
    uv = assar.sobreposicao_uv(perto) + assar.sobreposicao_uv(_pecas(lods['mundo']))
    densidade = assar.densidade_texel(perto, ctx['orcamento']['textura'])
    return validar.relatorio_e_problemas(ctx, ctx['ficha'], lods, soquetes_def, nomes_soq, pecas_jogo, _lados(ctx),
                                         uv, densidade, ctx['conferencia'])


def construir(ctx):
    t0 = time.time()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    ficha = ctx['ficha']
    arma = importlib.import_module(f"armas.{ctx['id']}")
    orc = ctx['orcamento']
    os.makedirs(ctx['saida'], exist_ok=True)
    os.makedirs(ctx['conferencia'], exist_ok=True)
    M = materiais.materiais_de_fabrica(ctx['fabrica'])
    alto = pecas.iniciar('alto', 'alto')
    arma.construir(ficha, M)
    pecas.finalizar(alto)
    jogo = pecas.iniciar('jogo', 'jogo')
    arma.construir(ficha, M)
    pecas.finalizar(jogo)
    zonas.aplicar_zonas(jogo)
    _etapa(t0, 'modelo alto e de jogo')
    pivos = arma.pivos(ficha)
    perto = soquetes.juntar_pecas(jogo, _colecao('perto'), 'perto', pivos)
    col_soq = _colecao('soquetes')
    soqs = [soquetes.soquete(col_soq, nome, x, y, lado, rot) for nome, (x, y), lado, rot in arma.soquetes(ficha)]
    lista_perto = [perto[p] for p in pivos]
    fontes = _malhas(alto)
    _etapa(t0, 'peças móveis e soquetes')
    # A pega (Fase 4.1b): as luvas refeitas pelo mesmo script e o solver na arma de jogo (o perto, peças em repouso).
    mao, bracos = empunhadura_pega.montar_luvas(ctx, _colecao('luvas'))
    pega, rel_pega, problemas_pega = empunhadura_pega.resolver(ctx, mao, bracos, perto, soqs,
                                                               getattr(arma, 'EMPUNHADURA', None))
    empunhadura_pega.guardar(bracos, pega)
    _etapa(t0, f"empunhadura ({rel_pega['segundos']} s)")
    assar.uv_automatico(lista_perto, orc['textura'], 8)
    assar.assar_conjunto(fontes, lista_perto, orc['textura'], 8, ctx['saida'], f"{ctx['id']}_n", f"{ctx['id']}_m")
    _etapa(t0, f"UV e assar o perto ({orc['textura']} px)")
    mundo, razao_mundo = lod.lod_mundo(jogo, _colecao('mundo'), pivos, orc['triangulos']['mundo'])
    lista_mundo = [mundo[p] for p in pivos]
    margem_mundo = max(2, round(8 * orc['texturaMundo'] / orc['textura']))
    assar.uv_automatico(lista_mundo, orc['texturaMundo'], margem_mundo)
    assar.assar_conjunto(fontes, lista_mundo, orc['texturaMundo'], margem_mundo, ctx['saida'], f"{ctx['id']}_mundo_n",
                         f"{ctx['id']}_mundo_m")
    _etapa(t0, f"mundo: LOD, UV e assar ({orc['texturaMundo']} px)")
    longe, razao_longe = lod.lod_longe(mundo, _colecao('longe'), pivos, orc['triangulos']['longe'])
    lods = {'perto': perto, 'mundo': mundo, 'longe': longe}
    _etapa(t0, 'longe: LOD')
    rel, problemas = _validar(ctx, arma, lods, jogo)
    problemas += problemas_pega
    _etapa(t0, 'validar')
    rel.update({
        'empunhadura': rel_pega,
        'arma': ctx['id'], 'versao': 1, 'blender': bpy.app.version_string, 'gerado': time.strftime('%Y-%m-%dT%H:%M:%S'),
        'entradas': {'hash': ctx['hash']}, 'origemMM': list(arma.ORIGEM_MM),
        'dizimacao': {'mundo': round(razao_mundo, 4), 'longe': round(razao_longe, 4)},
        'facesEscondidasRemovidas': perto['_removidas'],
    })
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ctx['conferencia'], f"{ctx['id']}.blend"))
    if problemas:
        rel.update({'aprovado': False, 'problemas': problemas})
        exportar.gravar_relatorio(ctx['saida'], ctx['id'], rel)
        print('MASSACRE-REPROVADO', json.dumps(problemas, ensure_ascii=False))
        sys.exit(1)
    objetos_pega = empunhadura_pega.objetos_da_saida(mao, bracos, pega, rel_pega['marca'], _colecao('pega'))
    exportar.exportar(ctx, arma.ORIGEM_MM, lods, soqs, ctx['saida'], objetos_pega)
    _etapa(t0, 'exportar')
    tamanhos = {nome: os.path.getsize(os.path.join(ctx['saida'], nome)) for nome in sorted(os.listdir(ctx['saida']))
                if nome.startswith(ctx['id']) and not nome.endswith('.relatorio.json')}
    total = sum(tamanhos.values())
    if total > orc['arquivosMB'] * 1024 * 1024:
        problemas.append(f"arquivos: {total / 1048576:.2f} MB (orçamento {orc['arquivosMB']} MB)")
    rel.update({'arquivos': tamanhos, 'aprovado': not problemas, 'problemas': problemas, 'segundos': round(time.time() - t0, 1)})
    exportar.gravar_relatorio(ctx['saida'], ctx['id'], rel)
    print('MASSACRE-RELATORIO', json.dumps({'silhueta': rel['silhueta'], 'lods': rel['lods'], 'bytes': total}, ensure_ascii=False))
    if problemas:
        print('MASSACRE-REPROVADO', json.dumps(problemas, ensure_ascii=False))
        sys.exit(1)


def revalidar(ctx):
    bpy.ops.wm.open_mainfile(filepath=os.path.join(ctx['conferencia'], f"{ctx['id']}.blend"))
    arma = importlib.import_module(f"armas.{ctx['id']}")
    lods = {}
    for nivel in ('perto', 'mundo', 'longe'):
        lods[nivel] = {o.name[len(nivel) + 1:]: o for o in bpy.data.collections[nivel].objects if o.type == 'MESH'}
    rel, problemas = _validar(ctx, arma, lods, bpy.data.collections['jogo'])
    mao, bracos = empunhadura_pega.luvas_da_blend(ctx)
    soqs = list(bpy.data.collections['soquetes'].objects)
    _pega, rel_pega, problemas_pega = empunhadura_pega.resolver(ctx, mao, bracos, lods['perto'], soqs,
                                                                getattr(arma, 'EMPUNHADURA', None))
    problemas += problemas_pega
    print('MASSACRE-VALIDACAO', json.dumps({'silhueta': rel['silhueta'], 'medidas': rel['medidas'],
                                            'empunhadura': rel_pega, 'problemas': problemas}, ensure_ascii=False))
    if problemas:
        sys.exit(1)


def acao_conferir(ctx):
    bpy.ops.wm.open_mainfile(filepath=os.path.join(ctx['conferencia'], f"{ctx['id']}.blend"))
    arquivos, dispositivo = conferir.conferir(ctx, ctx['conferencia'], arma=importlib.import_module(f"armas.{ctx['id']}"))
    print('MASSACRE-CONFERIR', json.dumps(arquivos, ensure_ascii=False))
    print('MASSACRE-DISPOSITIVO', dispositivo)


def conferir_luvas(ctx):
    arquivos, dispositivo = luvas.conferir(ctx)
    print('MASSACRE-CONFERIR', json.dumps(arquivos, ensure_ascii=False))
    print('MASSACRE-DISPOSITIVO', dispositivo)


def principal():
    args = sys.argv[sys.argv.index('--') + 1:]
    acao, caminho = args[0], args[1]
    with open(caminho, encoding='utf-8') as f:
        ctx = json.load(f)
    if ctx['id'] == 'luvas':
        acoes = {'construir': luvas.construir, 'validar': luvas.validar, 'conferir': conferir_luvas}
    else:
        acoes = {'construir': construir, 'validar': revalidar, 'conferir': acao_conferir}
    acoes[acao](ctx)


principal()
