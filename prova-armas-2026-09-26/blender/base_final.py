def finalizar():
    for ob in bpy.data.objects:
        if ob.type != 'MESH' or ob.get('cortador'):
            continue
        c, s = ob.get('chanfro', (0.6, 3))
        acabar(ob, c, int(s))


# ---------------------------------------------------------------- estúdio
def estudio():
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
    bmesh.ops.translate(bm, vec=(-0.45, 0.2, -0.27), verts=bm.verts[:])
    objeto('fundo', bm, chao)

    def luz(nome, pos, alvo, tam, energia, cor):
        d = bpy.data.lights.new(nome, 'AREA')
        d.size = tam
        d.energy = energia
        d.color = cor
        o = bpy.data.objects.new(nome, d)
        sc.collection.objects.link(o)
        o.location = pos
        dirv = Vector(alvo) - Vector(pos)
        o.rotation_euler = dirv.to_track_quat('-Z', 'Y').to_euler()
    luz('principal', (-0.2, -0.9, 0.9), (-0.45, 0, -0.05), 1.2, 30, (1.0, 0.9, 0.78))
    luz('preenchimento', (-0.9, -0.7, 0.2), (-0.45, 0, -0.05), 1.0, 9, (0.75, 0.85, 1.0))
    luz('recorte', (-0.5, 0.9, 0.5), (-0.45, 0, -0.05), 0.8, 22, (1.0, 1.0, 1.0))
    luz('topo', (-0.45, 0.0, 1.2), (-0.45, 0, 0), 1.8, 14, (1.0, 0.97, 0.92))


def camera(nome, pos, alvo, lente, orto=None):
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
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'
    prefs = bpy.context.preferences.addons['cycles'].preferences
    for tipo in ('OPTIX', 'CUDA'):
        try:
            prefs.compute_device_type = tipo
            prefs.get_devices()
            achou = [d for d in prefs.devices if d.type == tipo]
            if achou:
                for d in prefs.devices:
                    d.use = d.type == tipo
                sc.cycles.device = 'GPU'
                return tipo
        except Exception:
            pass
    return 'CPU'


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    construir()
    finalizar()
    estudio()
    sc = bpy.context.scene
    dev = gpu()
    sc.cycles.samples = 160
    sc.cycles.use_denoising = True
    sc.render.resolution_x = 1600
    sc.render.resolution_y = 900
    sc.view_settings.view_transform = 'AgX'
    sc.view_settings.look = 'AgX - Medium High Contrast'
    cams = {
        'tres': camera('tres', (-0.16, -0.78, 0.26), (-0.44, 0.0, -0.06), 50),
        'lado': camera('lado', (-0.44, -1.5, -0.055), (-0.44, 0.0, -0.055), 50, orto=0.98),
        'perto': camera('perto', (-0.50, -0.26, 0.085), (-0.60, 0.0, -0.015), 55),
    }
    for nome in VISTAS:
        sc.camera = cams[nome]
        sc.render.filepath = os.path.join(SAIDA, f'ak_{nome}.png')
        bpy.ops.render.render(write_still=True)
        print('render', nome, dev)
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(SAIDA, 'ak_spike.blend'))


main()
