"""MASSACRE — as armas de massinha no Blender 5.2 (Fase 4.1; docs/phases/phase-4.md, seção 4.1, "Blender").

O Blender é o editor da receita (src/data/armas/<id>.js): importar monta a cena, exportar grava a receita de volta e
conferir renderiza as vistas da prévia do jogo (a malha que o jogo gera, com as mãos e a primeira pessoa) com a planta
de referência. Quem chama é o tools/blender.mjs (`npm run blender -- ...`), que prepara o contexto (paleta, planta, a mão
de massinha em cada pose calculada pelo rig do jogo, a prévia do jogo) num JSON:

  blender --python tools/blender/massacre_armas.py -- abrir <contexto.json>
  blender --background --python tools/blender/massacre_armas.py -- conferir <contexto.json>
  blender --background --python tools/blender/massacre_armas.py -- ida-volta <contexto.json> <saída.js>

Com janela, o painel "MASSACRE" (barra lateral da vista 3D, tecla N) tem Exportar (valida pelo jogo e grava por cima
da receita), Prévia do jogo (a malha que o jogo faria da cena como está), Conferir (as vistas em
tools/blender/conferencia/<id>/, da cena como está) e Recarregar (descarta a cena e relê a receita do disco).
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from massacre import conferir as conf  # noqa: E402
from massacre import exportar as exp  # noqa: E402
from massacre import importar as imp  # noqa: E402
from massacre import previa  # noqa: E402
from massacre import receita as rec  # noqa: E402


def carregar(contexto):
    """Lê a receita do disco e monta a cena."""
    receita, cabecalho = rec.ler(contexto['receita'])
    bpy.context.scene.unit_settings.system = 'NONE'  # u da arma = unidade do Blender, sem metros
    imp.importar(receita, cabecalho, contexto)
    return receita


def contexto_da_cena():
    cena = bpy.context.scene
    if 'massacre_contexto' not in cena:
        raise RuntimeError('esta cena não veio do `npm run blender -- abrir <arma>`')
    return json.loads(cena['massacre_contexto'])


def validar(contexto, arquivo):
    """Valida uma receita pelo jogo (a mesma validação do gerador): devolve (ok, mensagem)."""
    res = subprocess.run(
        [contexto['node'], contexto['ferramenta'], 'validar', arquivo],
        capture_output=True, text=True, encoding='utf-8', cwd=contexto['raiz'],
    )
    return res.returncode == 0, (res.stdout + res.stderr).strip()


def exportar_temporario(contexto):
    """Exporta a cena para uma receita temporária validada pelo jogo. Devolve (caminho, mensagem); quem chama apaga."""
    receita, cabecalho = exp.exportar()
    fd, tmp = tempfile.mkstemp(suffix='.js', prefix=f"{receita['id']}-")
    os.close(fd)
    try:
        rec.gravar(tmp, receita, cabecalho)
        ok, msg = validar(contexto, tmp)
        if not ok:
            raise RuntimeError(f'a receita exportada não passou na validação do jogo:\n{msg}')
    except BaseException:
        os.remove(tmp)
        raise
    return tmp, msg


def exportar_para(contexto, destino):
    """Exporta a cena, valida e só então grava em `destino`. Devolve a mensagem da validação."""
    tmp, msg = exportar_temporario(contexto)
    try:
        shutil.copyfile(tmp, destino)
    finally:
        os.remove(tmp)
    return msg


def previa_da_cena(contexto):
    """A prévia do jogo da cena como está (exporta para um temporário, valida, o jogo gera a malha)."""
    tmp, _ = exportar_temporario(contexto)
    try:
        return previa.atualizar(contexto, tmp)
    finally:
        os.remove(tmp)


# ---------------------------------------------------------------- painel (Blender com janela)

class MASSACRE_OT_exportar(bpy.types.Operator):
    bl_idname = 'massacre.exportar'
    bl_label = 'Exportar a receita'
    bl_description = 'Grava a arma em src/data/armas/<id>.js (valida pelo jogo antes; no jogo, "Reler a receita do disco")'

    def execute(self, context):
        try:
            ctx = contexto_da_cena()
            msg = exportar_para(ctx, ctx['receita'])
        except Exception as err:  # noqa: BLE001 — o painel mostra qualquer falha ao usuário
            self.report({'ERROR'}, str(err))
            return {'CANCELLED'}
        self.report({'INFO'}, f"{os.path.basename(ctx['receita'])} gravada · {msg}")
        return {'FINISHED'}


class MASSACRE_OT_previa(bpy.types.Operator):
    bl_idname = 'massacre.previa'
    bl_label = 'Prévia do jogo'
    bl_description = 'A malha que o jogo gera da cena como está (SDF, costuras, cortes, mãos), numa coleção que não exporta'

    def execute(self, context):
        try:
            col = previa_da_cena(contexto_da_cena())
        except Exception as err:  # noqa: BLE001
            self.report({'ERROR'}, str(err))
            return {'CANCELLED'}
        self.report({'INFO'}, f'prévia do jogo em "{col.name}" (o olho no Outliner mostra e esconde)')
        return {'FINISHED'}


class MASSACRE_OT_conferir(bpy.types.Operator):
    bl_idname = 'massacre.conferir'
    bl_label = 'Conferir (renders)'
    bl_description = ('Prévia do jogo da cena como está e as vistas lateral (com a planta), cima, frente, 3/4, mãos e '
                      'primeira pessoa em tools/blender/conferencia/<id>/')

    def execute(self, context):
        try:
            ctx = contexto_da_cena()
            previa_da_cena(ctx)
            arquivos = conf.conferir(ctx['pasta'])
        except Exception as err:  # noqa: BLE001
            self.report({'ERROR'}, str(err))
            return {'CANCELLED'}
        self.report({'INFO'}, f'{len(arquivos)} vistas em {os.path.dirname(arquivos[0])}')
        return {'FINISHED'}


class MASSACRE_OT_recarregar(bpy.types.Operator):
    bl_idname = 'massacre.recarregar'
    bl_label = 'Recarregar do disco'
    bl_description = 'Descarta a cena e relê a receita do disco (com a prévia do jogo dela, escondida)'

    def execute(self, context):
        try:
            ctx = contexto_da_cena()
            carregar(ctx)
            previa.atualizar(ctx, ctx['receita'], visivel=False)
        except Exception as err:  # noqa: BLE001
            self.report({'ERROR'}, str(err))
            return {'CANCELLED'}
        enquadrar()
        return {'FINISHED'}


class MASSACRE_PT_arma(bpy.types.Panel):
    bl_label = 'MASSACRE'
    bl_idname = 'MASSACRE_PT_arma'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'MASSACRE'

    def draw(self, context):
        col = self.layout.column(align=True)
        cena = context.scene
        if 'massacre_contexto' in cena:
            ctx = json.loads(cena['massacre_contexto'])
            col.label(text=f"Arma: {ctx['id']} (acento {ctx['faccao']})")
            col.label(text=os.path.relpath(ctx['receita'], ctx['raiz']))
        col.separator()
        col.operator('massacre.exportar', icon='EXPORT')
        col.operator('massacre.previa', icon='SHADING_RENDERED')
        col.operator('massacre.conferir', icon='RENDER_STILL')
        col.operator('massacre.recarregar', icon='FILE_REFRESH')
        col.separator()
        col.label(text='Peças: mova, gire, escale, edite pontos.')
        col.label(text='Peça nova: Shift+D numa da mesma forma.')
        col.label(text='Grupo: a coleção; massa: o material.')
        col.label(text='Âncora de mão: propriedade "pose".')


CLASSES = (MASSACRE_OT_exportar, MASSACRE_OT_previa, MASSACRE_OT_conferir, MASSACRE_OT_recarregar, MASSACRE_PT_arma)


def registrar():
    for c in CLASSES:
        if not hasattr(bpy.types, c.__name__):
            bpy.utils.register_class(c)


def sem_tela_de_abertura():
    """Com janela: a tela de abertura não cobre a arma. O Blender decide mostrá-la depois dos scripts da linha de
    comando; a preferência do usuário volta ao que era logo em seguida."""
    vista = bpy.context.preferences.view
    antes = vista.show_splash
    vista.show_splash = False

    def voltar():
        vista.show_splash = antes
        return None
    bpy.app.timers.register(voltar, first_interval=2.0)


def enquadrar():
    """Com janela: a vista 3D na lateral direita da arma (ortográfica, onde a planta guia; a boca à direita), sólida
    pela cor das massas, enquadrando as peças, com a barra lateral aberta (a aba MASSACRE)."""
    def fazer():
        pecas = [o for o in bpy.data.objects if 'massacre_parte' in o]
        for janela in bpy.context.window_manager.windows:
            for area in janela.screen.areas:
                if area.type != 'VIEW_3D':
                    continue
                esp = area.spaces.active
                esp.shading.type = 'SOLID'
                esp.shading.color_type = 'MATERIAL'
                esp.clip_start = 0.05
                esp.clip_end = 2000.0
                esp.show_region_ui = True
                regiao = next((r for r in area.regions if r.type == 'WINDOW'), None)
                if not regiao:
                    continue
                with bpy.context.temp_override(window=janela, screen=janela.screen, area=area, region=regiao):
                    bpy.ops.view3d.view_axis(type='FRONT')
                    for o in pecas:
                        o.select_set(True)
                    bpy.ops.view3d.view_selected()
                    for o in pecas:
                        o.select_set(False)
        return None
    bpy.app.timers.register(fazer, first_interval=1.0)


def principal():
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    if len(argv) < 2:
        raise SystemExit('uso: ... -- <abrir|conferir|ida-volta> <contexto.json> [saída.js]')
    acao, caminho = argv[0], argv[1]
    with open(caminho, encoding='utf-8') as f:
        contexto = json.load(f)
    if acao == 'abrir':
        sem_tela_de_abertura()
        registrar()
        carregar(contexto)
        if contexto.get('previa'):
            previa.carregar(contexto['previa'], visivel=False)
        enquadrar()
    elif acao == 'conferir':
        carregar(contexto)
        previa.carregar(contexto['previa'])
        arquivos = conf.conferir(contexto['pasta'])
        print('MASSACRE-CONFERIR ' + json.dumps(arquivos))
    elif acao == 'ida-volta':
        if len(argv) < 3:
            raise SystemExit('ida-volta precisa do arquivo de saída')
        carregar(contexto)
        receita, cabecalho = exp.exportar()
        rec.gravar(argv[2], receita, cabecalho)
        print(f'MASSACRE-IDA-VOLTA {argv[2]}')
    else:
        raise SystemExit(f'ação desconhecida: {acao}')


if __name__ == '__main__':
    principal()
