# Zonas das armas realistas (Fase 4.1a; desenho, seção 4.2): grupos de material, a base das skins. No modelo de jogo cada
# peça recebe o material da sua zona, que se chama exatamente como a zona — é assim que o .glb diz a zona de cada
# primitiva (plano da 4.1a, D2). As cores aqui só servem para ver no Blender; o jogo pinta pelo acabamento.
import bpy

ZONAS = ('corpo', 'guarnicao', 'carregador', 'detalhes', 'interno')
_VISTA = {
    'corpo': (0.03, 0.031, 0.036), 'guarnicao': (0.37, 0.135, 0.05), 'carregador': (0.075, 0.08, 0.088),
    'detalhes': (0.05, 0.05, 0.055), 'interno': (0.42, 0.42, 0.43),
}


def material_da_zona(zona):
    assert zona in ZONAS, zona
    m = bpy.data.materials.get(zona)
    if m is None:
        m = bpy.data.materials.new(zona)
        m.use_nodes = True
        b = m.node_tree.nodes['Principled BSDF']
        b.inputs['Base Color'].default_value = (*_VISTA[zona], 1)
        b.inputs['Metallic'].default_value = 0.0 if zona == 'guarnicao' else 1.0
        b.inputs['Roughness'].default_value = 0.4
    return m


def aplicar_zonas(colecao):
    """Troca o material de cada peça da coleção (modelo de jogo) pelo da zona dela."""
    for ob in colecao.objects:
        if ob.type != 'MESH' or ob.get('cortador'):
            continue
        z = ob.get('zona')
        if z not in ZONAS:
            raise ValueError(f'{ob.name}: zona "{z}" desconhecida (use {", ".join(ZONAS)})')
        ob.data.materials.clear()
        ob.data.materials.append(material_da_zona(z))
