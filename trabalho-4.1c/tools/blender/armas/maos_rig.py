# Rig das luvas (Fase 4.1b; desenho em docs/superpowers/specs/2026-09-26-4.1b-luvas-e-empunhadura-design.md, seção 4;
# plano, Tarefa 5 e D2–D4): a armadura de 20 ossos por braço na pose de repouso da ficha, os pesos (os da gaiola,
# interpolados pela subdivisão; as peças de detalhe herdam da superfície da luva embaixo), o espelho para o braço
# esquerdo e a marca do rig.
# Ossos (D2): antebraco → torcao → mao → polegar_1..3, indicador_1..3, medio_1..3, anelar_0..3, minimo_0..3 (o anelar e o
# mínimo com o metacarpo próprio: a borda da palma fecha em concha), com o sufixo do lado (_d, _e).
# Eixos: o Y de cada osso ao longo dele; o X no eixo de flexão (nos dedos, a MCP reta e a PIP e a DIP inclinadas pela
# convergência; o do polegar; o de através da mão para a palma, o pulso e o antebraço) e o Z = X × Y do lado da palma
# — girar positivo em X fecha a junta (dobra o dedo para a palma, flexiona o pulso); girar em Y torce (a pronação). O
# braço esquerdo é o direito espelhado em Y com o X invertido, para girar positivo em X continuar fechando.
# As correções das dobras (maos_correcoes.py) são aplicadas depois do skin, pela pose do rig.
import hashlib
import json
import math

import bpy
from mathutils import Matrix, Quaternion, Vector

from .maos import DEDOS4, METACARPO
from .unidades import S

OSSOS = ('antebraco', 'torcao', 'mao',
         'polegar_1', 'polegar_2', 'polegar_3',
         'indicador_1', 'indicador_2', 'indicador_3',
         'medio_1', 'medio_2', 'medio_3',
         'anelar_0', 'anelar_1', 'anelar_2', 'anelar_3',
         'minimo_0', 'minimo_1', 'minimo_2', 'minimo_3')
MAX_INFLUENCIAS = 4
PESO_MINIMO = 0.01


def _pai(osso):
    if osso == 'antebraco':
        return None
    if osso == 'torcao':
        return 'antebraco'
    if osso == 'mao':
        return 'torcao'
    dedo, i = osso.rsplit('_', 1)
    i = int(i)
    if i == 0 or (i == 1 and dedo not in METACARPO):
        return 'mao'
    return f'{dedo}_{i - 1}'


def eixos_de_flexao(mao):
    """{osso: eixo de flexão (mm, unitário)} da mão direita em repouso."""
    atraves = Vector((0.0, 1.0, 0.0))
    eixos = {'antebraco': atraves, 'torcao': atraves, 'mao': atraves, 'anelar_0': atraves, 'minimo_0': atraves}
    for i in range(3):
        eixos[f'polegar_{i + 1}'] = mao.polegar['eixo'].copy()
    for d in DEDOS4:
        eixos[f'{d}_1'] = mao.dedos[d]['eixo_mcp'].copy()
        eixos[f'{d}_2'] = mao.dedos[d]['eixo_ip'].copy()
        eixos[f'{d}_3'] = mao.dedos[d]['eixo_ip'].copy()
    return eixos


def armadura(mao, colecao, lado='d'):
    """A armadura da mão direita (ou a esquerda espelhada, lado 'e') em metros, com os nomes da D2 e o sufixo."""
    ossos = mao.ossos()
    eixos = eixos_de_flexao(mao)
    arm = bpy.data.armatures.new(f'rig_{lado}')
    ob = bpy.data.objects.new(f'rig_{lado}', arm)
    colecao.objects.link(ob)
    espelho = Matrix.Diagonal((1.0, -1.0 if lado == 'e' else 1.0, 1.0))
    with bpy.context.temp_override(active_object=ob, object=ob, selected_objects=[ob]):
        bpy.context.view_layer.objects.active = ob
        bpy.ops.object.mode_set(mode='EDIT')
        for nome in OSSOS:
            cabeca, cauda, _normal = ossos[nome]
            eb = arm.edit_bones.new(f'{nome}_{lado}')
            eb.head = (espelho @ cabeca) * S
            eb.tail = (espelho @ cauda) * S
            y = (eb.tail - eb.head).normalized()
            x = espelho @ eixos[nome]
            if lado == 'e':
                x = -x  # o espelho troca a mão do referencial: com o X invertido, girar positivo continua fechando
            x = (x - y * x.dot(y)).normalized()
            eb.align_roll(x.cross(y))  # align_roll põe o Z do osso na direção dada: Z = X × Y
        for nome in OSSOS:
            pai = _pai(nome)
            if pai:
                eb = arm.edit_bones[f'{nome}_{lado}']
                eb.parent = arm.edit_bones[f'{pai}_{lado}']
                eb.use_connect = (eb.head - eb.parent.tail).length < 1e-6
        bpy.ops.object.mode_set(mode='OBJECT')
    return ob


def marca(rig):
    """A marca do rig (D4): SHA-256 dos comprimentos dos ossos e dos quaternions da pose de repouso (a orientação de cada
    osso em relação ao pai), arredondados a 1e-5, na ordem dos OSSOS."""
    lado = rig.name.rsplit('_', 1)[1]
    dados = []
    for nome in OSSOS:
        b = rig.data.bones[f'{nome}_{lado}']
        m = b.matrix_local if b.parent is None else b.parent.matrix_local.inverted() @ b.matrix_local
        q = m.to_quaternion()
        if q.w < 0:
            q.negate()
        dados.append([nome, round(b.length, 5), [round(c, 5) for c in q]])
    return hashlib.sha256(json.dumps(dados, separators=(',', ':')).encode()).hexdigest()


# ---------------------------------------------------------------------------------------------- pesos
def _limpar_pesos(ob):
    """No máximo MAX_INFLUENCIAS ossos por vértice (os maiores), normalizados, sem peso abaixo de PESO_MINIMO."""
    me = ob.data
    grupos = ob.vertex_groups
    for v in me.vertices:
        ws = sorted(((g.group, g.weight) for g in v.groups if g.weight > 0), key=lambda t: -t[1])
        fica = [(gi, w) for gi, w in ws[:MAX_INFLUENCIAS] if w >= PESO_MINIMO]
        if not fica:
            fica = ws[:1]
        total = sum(w for _, w in fica)
        manter = {gi for gi, _ in fica}
        for gi, _ in ws:
            if gi not in manter:
                grupos[gi].remove([v.index])
        for gi, w in fica:
            grupos[gi].add([v.index], w / total, 'REPLACE')


def pesos(luva, pecas, lado='d'):
    """Junta as peças de detalhe na luva com os pesos da superfície embaixo (Data Transfer do ponto mais próximo na face,
    interpolado), limita e normaliza os pesos e põe o sufixo do lado nos grupos. Devolve a luva."""
    for ob in pecas:
        for g in luva.vertex_groups:
            ob.vertex_groups.new(name=g.name)
        dt = ob.modifiers.new('pesos', 'DATA_TRANSFER')
        dt.object = luva
        dt.use_vert_data = True
        dt.data_types_verts = {'VGROUP_WEIGHTS'}
        dt.vert_mapping = 'POLYINTERP_NEAREST'
        dt.layers_vgroup_select_src = 'ALL'
        dt.layers_vgroup_select_dst = 'NAME'
        with bpy.context.temp_override(object=ob, active_object=ob):
            bpy.ops.object.modifier_apply(modifier=dt.name)
    if pecas:
        with bpy.context.temp_override(active_object=luva, object=luva, selected_objects=[luva, *pecas],
                                       selected_editable_objects=[luva, *pecas]):
            bpy.ops.object.join()
    _limpar_pesos(luva)
    for g in luva.vertex_groups:
        if not g.name.endswith(f'_{lado}'):
            g.name = f'{g.name}_{lado}'
    return luva


def ligar(luva, rig):
    """A luva presa ao rig: pai e modificador Armature (pelos grupos de vértices)."""
    luva.parent = rig
    m = luva.modifiers.new('rig', 'ARMATURE')
    m.object = rig
    m.use_vertex_groups = True
    return m


def _espelhar_coordenadas(dados):
    co = [0.0] * (len(dados) * 3)
    dados.foreach_get('co', co)
    co[1::3] = [-y for y in co[1::3]]
    dados.foreach_set('co', co)


def espelhar(luva_d, rig_d, mao, colecao):
    """O braço esquerdo: a malha da direita espelhada em Y (com as mesmas UV e as faces viradas de volta), os grupos
    com `_e` e a armadura esquerda (armadura(..., 'e')). Devolve (luva_e, rig_e)."""
    me = luva_d.data.copy()
    me.name = luva_d.data.name.replace('_d', '_e')
    luva_e = bpy.data.objects.new(luva_d.name.replace('_d', '_e'), me)
    colecao.objects.link(luva_e)
    _espelhar_coordenadas(me.vertices)
    me.flip_normals()
    me.update()
    # Os pesos e os nomes dos grupos vêm com a malha copiada (desde o Blender 3.0 os nomes ficam na malha, não no
    # objeto): os grupos `_d` da cópia são renomeados. Criar grupos `_e` novos deixava o braço esquerdo sem peso nenhum
    # (os pesos nos grupos `_d`, que não casam com os ossos do rig esquerdo; a conferência do espelho pegou).
    for g in luva_e.vertex_groups:
        if g.name.endswith('_d'):
            g.name = g.name[:-2] + '_e'
    if {g.name for g in luva_e.vertex_groups} != {g.name[:-2] + '_e' for g in luva_d.vertex_groups}:
        raise RuntimeError('espelhar: os grupos do braço esquerdo não casam com os do direito')
    rig_e = armadura(mao, colecao, 'e')
    ligar(luva_e, rig_e)
    return luva_e, rig_e


# ---------------------------------------------------------------------------------------------- poses
def _flexao(graus):
    return Quaternion((1.0, 0.0, 0.0), math.radians(graus))


def espelhar_pose(pose):
    """A pose da mão direita no braço esquerdo: o mesmo movimento, espelhado em Y. Os ossos esquerdos têm o X invertido
    do espelho (X' = −M·X, Y' = M·Y, Z' = M·Z), então uma rotação da direita, no referencial do osso, vira a conjugação
    dela pela meia volta em X — (w, x, y, z) → (w, x, −y, −z): a flexão (em X) igual, os giros em Y e em Z com o sinal
    trocado (a abertura dos dedos, a pronação e a abdução do polegar)."""
    return {o: Quaternion((q.w, q.x, -q.y, -q.z)) for o, q in pose.items()}


def eixo_abducao_do_polegar(mao, rig):
    """(eixo no referencial de repouso do polegar_1, sinal) da abdução palmar da CMC: o eixo da ficha (a normal da palma
    × a direção do polegar na palma, o de maos.Mao._polegar), preso à palma; no braço esquerdo, o eixo espelhado e o
    sinal trocado (o espelho inverte o sentido dos giros). Positivo leva o polegar para a frente da palma."""
    ang = math.radians(mao.ded['polegar']['anguloNaPalma'])
    eixo = Vector((-math.sin(ang), math.cos(ang), 0.0))
    lado = rig.name.rsplit('_', 1)[1]
    sinal = 1.0
    if lado == 'e':
        eixo, sinal = Vector((eixo.x, -eixo.y, eixo.z)), -1.0
    b = rig.data.bones[f'polegar_1_{lado}']
    return (b.matrix_local.to_3x3().inverted() @ eixo).normalized(), sinal


def pose_de_teste(nome, mao):
    """{osso: quaternion} de uma pose de teste da seção 4 do desenho que não depende de contato, relativa ao repouso
    (graus totais na junta menos o repouso da ficha): `aberta` (todas as juntas no mínimo da AAOS, abertura de 15°) e
    `pulso` (a mão em repouso com o pulso a 60° de flexão). As que fecham até encostar (o punho, o apontar e a mesa)
    estão em empunhadura.poses_de_teste."""
    rep = mao.rep
    p = {}
    if nome == 'aberta':
        lim = mao.f['limites']
        for d in DEDOS4:
            # A abertura gira em volta do Z do osso (para a palma), antes da flexão (como no solver de empunhadura):
            # positivo leva o dedo para o lado do mínimo.
            ab = {'indicador': 1.0, 'medio': 0.0, 'anelar': -1.0, 'minimo': -2.0}[d] * (15 - rep['abertura'])
            p[f'{d}_1'] = _flexao(lim['mcp'][0] - rep['mcp']) @ Quaternion((0.0, 0.0, 1.0), math.radians(-ab))
            p[f'{d}_2'] = _flexao(lim['pip'][0] - rep['pip'])
            p[f'{d}_3'] = _flexao(lim['dip'][0] - rep['dip'])
        p['polegar_2'] = _flexao(lim['polegar']['mcp'][0] - rep['polegarMcp'])
        p['polegar_3'] = _flexao(lim['polegar']['ip'][0] - rep['polegarIp'])
    elif nome == 'pulso':
        p['mao'] = _flexao(60.0)
    else:
        raise ValueError(f'pose de teste desconhecida: {nome}')
    return p


def posar(rig, pose):
    """Põe a pose ({osso sem sufixo: quaternion}) no rig, os outros ossos em repouso."""
    lado = rig.name.rsplit('_', 1)[1]
    for pb in rig.pose.bones:
        pb.rotation_mode = 'QUATERNION'
        pb.rotation_quaternion = Quaternion()
    for nome, q in pose.items():
        rig.pose.bones[f'{nome}_{lado}'].rotation_quaternion = q
    bpy.context.view_layer.update()


def pose_json(pose):
    """A pose ({osso: quaternion}) em JSON ({osso: [w, x, y, z]})."""
    return {o: [round(c, 7) for c in q] for o, q in pose.items()}


def pose_de_json(dados):
    return {o: Quaternion(q) for o, q in dados.items()}
