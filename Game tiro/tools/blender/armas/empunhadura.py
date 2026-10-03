# Solver de empunhadura (Fase 4.1b; desenho em docs/superpowers/specs/2026-09-26-4.1b-luvas-e-empunhadura-design.md,
# seção 6.2): o núcleo que fecha a mão até encostar, sobre a luva de jogo com o rig e as correções das dobras (a malha
# avaliada pelo modelo das luvas, maos_correcoes.Modelo, em cada tentativa).
#  - fechar uma junta: a flexão por bisseção (tolerância 0,05°) entre o ângulo atual e o alvo, parando no maior ângulo
#    em que a parte que dobra (os triângulos dos ossos dela para baixo) não entra no obstáculo mais que 0,05 mm (o
#    contato). Na própria luva, o obstáculo é o resto dela, e só contam os pares de triângulos que estavam a mais de
#    12 mm um do outro no repouso: os que estavam perto são a pele da dobra de uma junta ou a membrana entre dois dedos
#    (as correções cuidam deles), não contato entre partes;
#  - vizinhos: se dois dedos se atravessam, o de fora (a partir do médio) abre na MCP até 20° para longe; se não bastar,
#    recua a flexão da MCP dele até separar. A abertura gira antes da flexão (o quaternion da pose é flexão · abertura):
#    o dedo abre no plano da palma e dobra em volta do eixo de flexão, e o afastamento da ponta continua com a MCP
#    fechada (girando depois, em 90° a abertura só torceria o dedo em volta dele mesmo);
#  - quem conta como obstáculo ao fechar um dedo: o resto da luva menos ele e os dedos vizinhos (o lado de um dedo
#    encostado no do vizinho é o passo dos vizinhos, não um limite da flexão);
# O polegar (a polpa num alvo e fechando até encostar) está em empunhadura_polegar.py, e as poses de teste das luvas
# que dependem de contato (o punho, o apontar e a mesa) em maos_poses.py. A pega das armas (a palma no soquete, as
# regras da categoria, a arma como obstáculo) usa este mesmo núcleo.
import math

from mathutils import Quaternion, Vector

from . import maos_contato, maos_correcoes
from .unidades import S

TOLERANCIA_GRAUS = 0.05
CONTATO_MM = 0.05
PERTO_MM = 12.0  # pares de triângulos a menos disso no repouso não são contato (dobra ou membrana)
DOBRA_MM = 22.0  # a membrana entre dois dedos: a pele a até 22 mm da MCP deles (o alcance da dobra da MCP)
ABERTURA_MAXIMA = 20.0
# o sinal da abertura (giro em Z) para longe do médio, na mão direita (a esquerda: para_fora)
_FORA = {'indicador': -1.0, 'anelar': 1.0, 'minimo': 1.0}
_VIZINHOS = {'indicador': ('medio',), 'medio': ('indicador', 'anelar'), 'anelar': ('medio', 'minimo'),
             'minimo': ('anelar',)}


class PolegarCruza(RuntimeError):
    """O polegar que entra na mão ou na arma mesmo aberto (empunhadura_polegar_deitado.deitar_na_arma), com os graus da solução
    (além do repouso): a pega chega a palma de novo com a CMC deles (empunhadura_pega.resolver)."""

    def __init__(self, mensagem, graus):
        super().__init__(mensagem)
        self.graus = graus


def para_fora(dedo, lado):
    """O sinal da abertura que afasta o dedo do médio no lado `lado` ('d' ou 'e'): a luva esquerda é a direita
    espelhada, e o giro em Z do osso espelhado anda para o outro lado (na esquerda, o sinal da direita juntava os dedos
    em vez de afastar)."""
    return _FORA[dedo] * (1.0 if lado == 'd' else -1.0)


def _cadeia(d):
    return {f'{d}_{i}' for i in range(4)}


def _falanges(d):
    """Os ossos das falanges de um dedo (sem o metacarpo do anelar e do mínimo, que é palma)."""
    return {f'{d}_{i}' for i in range(1, 4)}


class Colisor:
    """A luva ligada ao rig para as perguntas de contato: os triângulos, o osso dominante de cada vértice e as cabeças
    dos ossos em repouso."""

    def __init__(self, luva, rig, mao, reforco):
        self.luva, self.rig = luva, rig
        self.modelo = maos_correcoes.Modelo(luva, rig, mao, reforco)
        me = luva.data
        me.calc_loop_triangles()
        self.tris = [tuple(t.vertices) for t in me.loop_triangles]
        self.sup = maos_contato.Superficie(self.tris)
        nomes = {g.index: g.name[:-2] for g in luva.vertex_groups}
        self.dono = []
        for v in me.vertices:
            w = {nomes[g.group]: g.weight for g in v.groups}
            self.dono.append(max(w, key=w.get) if w else '')
        self.dono_tri = [self._dono_do_tri(t) for t in self.tris]
        self.centro = [sum((me.vertices[i].co for i in t), Vector()) / (3 * S) for t in self.tris]
        self.lado = rig.name.rsplit('_', 1)[1]
        self.cabeca = {b.name[:-2]: Vector(b.head_local) / S for b in rig.data.bones}

    def _dono_do_tri(self, t):
        contagem = {}
        for i in t:
            contagem[self.dono[i]] = contagem.get(self.dono[i], 0) + 1
        return max(contagem, key=contagem.get)

    def triangulos(self, ossos, longe_de=()):
        """Os triângulos dominados pelos `ossos`, fora dos a até DOBRA_MM (em repouso) da cabeça dos ossos `longe_de`
        (a pele da dobra daquelas juntas)."""
        cs = [self.cabeca[o] for o in longe_de]
        return [k for k, o in enumerate(self.dono_tri)
                if o in ossos and all((self.centro[k] - c).length > DOBRA_MM for c in cs)]

    def abaixo(self, osso):
        """O osso e os de baixo dele (sem o lado)."""
        b = self.rig.data.bones[f'{osso}_{self.lado}']
        return {osso} | {c.name[:-2] for c in b.children_recursive}

    def profundidade(self, pose, A, B, perto_mm=0.0):
        """A maior penetração (mm) entre os triângulos A e os B na pose (maos_contato.py: cada superfície medida só com
        os triângulos do conjunto dela), sem os pares que estavam a menos de `perto_mm` um do outro no repouso."""
        if not A or not B:
            return 0.0
        return self.profundidade_nos_pontos(self.modelo.pontos(pose), A, B, perto_mm)

    def profundidade_nos_pontos(self, pts, A, B, perto_mm=0.0):
        """A profundidade com a luva já avaliada (`pts`, em qualquer referencial rígido: o da arma, na pega; Vectors
        ou o numpy de empunhadura_arma.NaArma.pontos)."""
        if not A or not B:
            return 0.0
        if not isinstance(pts[0], Vector):
            pts = [Vector(p) for p in pts]
        medidor = maos_contato.Medidor(self.sup, pts)
        sa, sb = set(A), set(B)
        pior = 0.0
        for a, b in maos_contato.pares(pts, self.tris, A, B):
            if (self.centro[a] - self.centro[b]).length < perto_mm:
                continue
            pior = max(pior, medidor.par(a, b, sa, sb))
        return pior


def _flexao(graus):
    return Quaternion((1.0, 0.0, 0.0), math.radians(graus))


def _abertura(graus):
    return Quaternion((0.0, 0.0, 1.0), math.radians(graus))


def _rotacao(graus):
    return Quaternion((0.0, 1.0, 0.0), math.radians(graus))


def _bissecao(ok, de, ate):
    """O maior valor entre `de` (aceito) e `ate` com ok(valor), por bisseção até TOLERANCIA_GRAUS."""
    if ok(ate):
        return ate
    a, b = de, ate
    while abs(b - a) > TOLERANCIA_GRAUS:
        m = (a + b) / 2
        if ok(m):
            a = m
        else:
            b = m
    return a


class Mao:
    """Uma pose de mão sendo resolvida: flexão, abertura e rotação axial por osso (graus além do repouso). A rotação
    (em volta do Y do osso, a pronação do metacarpo do polegar) gira primeiro, depois a abertura, a flexão e o giro."""

    def __init__(self):
        self.flexao, self.aberturas, self.rotacoes = {}, {}, {}
        self.giros = {}  # osso → (eixo no referencial de repouso, graus), girado depois da flexão (a CMC do polegar)

    def pose(self):
        p = {}
        for osso in set(self.flexao) | set(self.aberturas) | set(self.giros) | set(self.rotacoes):
            q = (_flexao(self.flexao.get(osso, 0.0)) @ _abertura(self.aberturas.get(osso, 0.0))
                 @ _rotacao(self.rotacoes.get(osso, 0.0)))
            if osso in self.giros:
                eixo, graus = self.giros[osso]
                q = Quaternion(eixo, math.radians(graus)) @ q
            p[osso] = q
        return p

    def com(self, osso, flexao=None, abertura=None):
        m = Mao()
        m.flexao, m.aberturas, m.giros = dict(self.flexao), dict(self.aberturas), dict(self.giros)
        m.rotacoes = dict(self.rotacoes)
        if flexao is not None:
            m.flexao[osso] = flexao
        if abertura is not None:
            m.aberturas[osso] = abertura
        return m


def fechar(col, mao_pose, osso, alvo, obstaculo=None, na=None):
    """Fecha a junta `osso` do ângulo atual até `alvo` (graus além do repouso), parando no contato da parte que dobra
    com os triângulos `obstaculo` (o resto da luva, sem ele) e, com `na` (a luva na arma, empunhadura_arma.NaArma),
    com a arma. Devolve (nova pose, ângulo, encostou)."""
    A = col.triangulos(col.abaixo(osso))
    if obstaculo is None:
        dentro = set(A)
        obstaculo = [k for k in range(len(col.tris)) if k not in dentro]
    B = obstaculo
    de = mao_pose.flexao.get(osso, 0.0)
    vertices = na.vertices(col.abaixo(osso)) if na is not None else None

    def livre(g):
        pose = mao_pose.com(osso, flexao=g).pose()
        if col.profundidade(pose, A, B, PERTO_MM) > CONTATO_MM:
            return False
        return na is None or na.penetracao(na.pontos(pose), vertices) <= CONTATO_MM

    graus = _bissecao(livre, de, alvo)
    return mao_pose.com(osso, flexao=graus), graus, graus < alvo - TOLERANCIA_GRAUS


def separar_vizinhos(col, mao_pose, dedos):
    """Os dedos vizinhos (da lista, na ordem da mão) sem se atravessar: a partir do médio, o de fora abre na MCP até
    20° para longe; se não bastar, recua a flexão da MCP dele. Devolve (pose, {dedo: o que mudou})."""
    mudou = {}
    ordem = [('medio', 'anelar'), ('anelar', 'minimo'), ('medio', 'indicador')]
    for dentro, fora in ordem:
        if dentro not in dedos or fora not in dedos:
            continue
        # a pele entre os dois dedos, perto das MCP, é a membrana entre eles (as correções cuidam)
        longe = (f'{fora}_1', f'{dentro}_1')
        A = col.triangulos(_falanges(fora), longe)
        B = col.triangulos(_falanges(dentro), longe)
        osso = f'{fora}_1'
        if col.profundidade(mao_pose.pose(), A, B) <= CONTATO_MM:
            continue
        sinal = para_fora(fora, col.lado)
        ab0 = mao_pose.aberturas.get(osso, 0.0)

        def cruza_aberto(g):
            return col.profundidade(mao_pose.com(osso, abertura=ab0 + sinal * g).pose(), A, B) > CONTATO_MM

        if not cruza_aberto(ABERTURA_MAXIMA):
            a, b = 0.0, ABERTURA_MAXIMA  # a menor abertura que separa
            while b - a > TOLERANCIA_GRAUS:
                m = (a + b) / 2
                if cruza_aberto(m):
                    a = m
                else:
                    b = m
            mao_pose = mao_pose.com(osso, abertura=ab0 + sinal * b)
            mudou[fora] = {'abertura': round(sinal * b, 2)}
            continue
        # a abertura toda não basta: o de fora recua a MCP (a maior flexão, até a de agora, que separa)
        mao_pose = mao_pose.com(osso, abertura=ab0 + sinal * ABERTURA_MAXIMA)
        f0 = mao_pose.flexao.get(osso, 0.0)
        g = _bissecao(lambda f: col.profundidade(mao_pose.com(osso, flexao=f).pose(), A, B) <= CONTATO_MM, 0.0, f0)
        mao_pose = mao_pose.com(osso, flexao=g)
        mudou[fora] = {'abertura': round(sinal * ABERTURA_MAXIMA, 2), 'recuoMcp': round(f0 - g, 2)}
    return mao_pose, mudou

