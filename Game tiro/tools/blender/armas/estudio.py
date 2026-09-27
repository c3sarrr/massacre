# Estúdio das renders de conferência (Fase 4.1a; desenho, seção 4.7; vem da prova de conceito): fundo escuro, quatro
# luzes de área (principal quente, preenchimento frio, recorte e topo) em watts para a cena em metros, câmeras
# perspectiva e ortográfica, Cycles na GPU (OptiX, senão CUDA) e AgX com contraste médio-alto.
import bmesh
import bpy
from mathutils import Vector


def montar(centro=(-0.45, 0.0, -0.05)):
    """Fundo e luzes em volta do centro da arma (metros)."""
    sc = bpy.context.scene
    w = bpy.data.worlds.new('mundo')
    sc.world = w
    w.use_nodes = True
    w.node_tree.nodes['Background'].inputs['Color'].default_value = (0.018, 0.017, 0.016, 1)
    w.node_tree.nodes['Background'].inputs['Strength'].default_value = 1.0
    chao = bpy.data.materials.new('fundo')
    chao.use_nodes = True
    chao.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (0.05, 0.048, 0.045, 1)
    chao.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = 0.8
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=3.0)
    bmesh.ops.translate(bm, vec=(centro[0], 0.2, centro[2] - 0.22), verts=bm.verts[:])
    me = bpy.data.meshes.new('fundo')
    bm.to_mesh(me)
    bm.free()
    fundo = bpy.data.objects.new('fundo', me)
    me.materials.append(chao)
    sc.collection.objects.link(fundo)
    c = Vector(centro)

    def luz(nome, pos, tam, energia, cor):
        d = bpy.data.lights.new(nome, 'AREA')
        d.size = tam
        d.energy = energia
        d.color = cor
        o = bpy.data.objects.new(nome, d)
        sc.collection.objects.link(o)
        o.location = c + Vector(pos)
        o.rotation_euler = (c - o.location).to_track_quat('-Z', 'Y').to_euler()
    luz('principal', (0.25, -0.9, 0.95), 1.2, 30, (1.0, 0.9, 0.78))
    luz('preenchimento', (-0.45, -0.7, 0.25), 1.0, 9, (0.75, 0.85, 1.0))
    luz('recorte', (-0.05, 0.9, 0.55), 0.8, 22, (1.0, 1.0, 1.0))
    luz('topo', (0.0, 0.0, 1.25), 1.8, 14, (1.0, 0.97, 0.92))
    return fundo


def camera(nome, pos, alvo, lente=50, orto=None):
    """Câmera em `pos` olhando para `alvo` (metros); `orto` = largura da vista ortográfica (metros)."""
    sc = bpy.context.scene
    d = bpy.data.cameras.new(nome)
    d.lens = lente
    d.clip_start = 0.005
    if orto:
        d.type = 'ORTHO'
        d.ortho_scale = orto
    o = bpy.data.objects.new(nome, d)
    sc.collection.objects.link(o)
    o.location = pos
    o.rotation_euler = (Vector(alvo) - Vector(pos)).to_track_quat('-Z', 'Y').to_euler()
    return o


def gpu():
    """Cycles na GPU (OptiX, senão CUDA); devolve o dispositivo usado."""
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'
    prefs = bpy.context.preferences.addons['cycles'].preferences
    for tipo in ('OPTIX', 'CUDA'):
        try:
            prefs.compute_device_type = tipo
            prefs.get_devices()
            if any(d.type == tipo for d in prefs.devices):
                for d in prefs.devices:
                    d.use = d.type == tipo
                sc.cycles.device = 'GPU'
                return tipo
        except Exception:
            pass
    sc.cycles.device = 'CPU'
    return 'CPU'


def render(largura, altura, amostras=160):
    sc = bpy.context.scene
    dispositivo = gpu()
    sc.cycles.samples = amostras
    sc.cycles.use_denoising = True
    sc.render.resolution_x = largura
    sc.render.resolution_y = altura
    sc.render.resolution_percentage = 100
    sc.view_settings.view_transform = 'AgX'
    sc.view_settings.look = 'AgX - Medium High Contrast'
    return dispositivo
