# Luvas táticas realistas (Fase 4.1b; desenho em docs/superpowers/specs/2026-09-26-4.1b-luvas-e-empunhadura-design.md,
# seções 2 e 3): a anatomia da mão direita pela ficha (tools/blender/refs/luvas.json) — as juntas e os ossos na pose de
# repouso, as seções dos dedos nas juntas, o pulso e o perfil do antebraço de massinha que entra no punho da luva. O
# script não inventa medida: cada número sai da ficha (medida publicada ou dedução com o porquê). A gaiola de
# quadriláteros e a malha saem de maos_gaiola.py.
# Referencial (mão direita, mm): origem no centro da junta do pulso, +X para as pontas, +Y para o polegar, +Z para as
# costas da mão. A esquerda é esta espelhada em Y (maos_rig.py).
import math

from mathutils import Quaternion, Vector

DEDOS4 = ('indicador', 'medio', 'anelar', 'minimo')
# Abertura de repouso de cada dedo, em múltiplos de `repouso.abertura` (o médio é o eixo; + para o polegar).
_ABERTURA = {'indicador': 1.0, 'medio': 0.0, 'anelar': -1.0, 'minimo': -2.0}
# Metacarpo que carrega a borda da palma (os outros dois vão na `mao`).
METACARPO = {'anelar': 'anelar_0', 'minimo': 'minimo_0'}


def perimetro_elipse(a, b):
    """Ramanujan: perímetro da elipse de semieixos a e b."""
    return math.pi * (3 * (a + b) - math.sqrt((3 * a + b) * (a + 3 * b)))


def perimetro_retangulo_arredondado(largura, altura, raio):
    """Perímetro do retângulo arredondado (o modelo de seção da ficha para o pulso e para a mão nos nós)."""
    return 2 * (largura - 2 * raio) + 2 * (altura - 2 * raio) + 2 * math.pi * raio


def espessura_pela_circunferencia(largura, circ):
    """A espessura (2b) da elipse com a largura (2a) e o perímetro dados (bisseção)."""
    a = largura / 2
    lo, hi = 0.2 * a, 3.0 * a
    for _ in range(60):
        b = (lo + hi) / 2
        if perimetro_elipse(a, b) < circ:
            lo = b
        else:
            hi = b
    return lo + hi


def meia_altura_no_contorno(y, meia_l, meia_a, raio):
    """Metade da altura do retângulo arredondado (meia largura, meia altura, raio do canto) na posição y."""
    raio = min(raio, meia_l, meia_a)
    reto = meia_l - raio
    if abs(y) <= reto:
        return meia_a
    dy = min(abs(y) - reto, raio)
    return meia_a - raio + math.sqrt(max(0.0, raio * raio - dy * dy))


class Mao:
    """As juntas, os referenciais e as seções da mão direita na pose de repouso, em mm, pela ficha."""

    def __init__(self, ficha):
        self.f = ficha
        j = ficha['juntas']
        self.esc_c = ficha['mao']['comprimento']['mm'] / j['pontaAoPulso']['medio']
        self.esc_l = ficha['mao']['largura']['mm'] / j['larguraDaMao']
        self.luva = ficha['luva']['tecido']
        self.rep = ficha['repouso']
        self.ded = ficha['deducoes']
        self.largura = ficha['mao']['largura']['mm']
        self._larguras_nos()
        self.dedos = {d: self._dedo(d) for d in DEDOS4}
        self.polegar = self._polegar()
        self._pulso()
        self.antebraco = j['cotoveloAoPulso'] * self.esc_c

    # ------------------------------------------------------------------ medidas
    def _larguras_juntas(self, d):
        """(largura, espessura) na PIP e na DIP, na escala da ficha e sem a luva."""
        j = self.f['juntas'][d]
        lp = j['pip']['largura'] * self.esc_l
        ep = espessura_pela_circunferencia(lp, j['pip']['circunferencia'] * self.esc_l)
        if 'largura' in j['dip']:
            ld = j['dip']['largura'] * self.esc_l
        else:
            # A largura da DIP do indicador (ilegível na cópia de Greiner) na proporção largura/circunferência do médio.
            m = self.f['juntas']['medio']['dip']
            ld = j['dip']['circunferencia'] * m['largura'] / m['circunferencia'] * self.esc_l
        ed = espessura_pela_circunferencia(ld, j['dip']['circunferencia'] * self.esc_l)
        return (lp, ep), (ld, ed)

    def _larguras_nos(self):
        """Os quatro nós repartem a largura da mão na proporção das larguras nas PIP, com a folga entre os dedos. As
        fronteiras (do indicador ao mínimo) ficam em `y_fronteira`; as bordas de fora são ± a meia largura da mão."""
        folga = self.ded['folgaEntreDedos']['mm']
        pips = {d: self._larguras_juntas(d)[0][0] for d in DEDOS4}
        k = (self.largura - 3 * folga) / sum(pips.values())
        self.larg_no = {d: pips[d] * k for d in DEDOS4}
        y = self.largura / 2
        self.y_no = {}
        self.y_fronteira = [self.largura / 2]
        for d in DEDOS4:
            self.y_no[d] = y - self.larg_no[d] / 2
            y -= self.larg_no[d] + folga
            self.y_fronteira.append(y + folga / 2)
        self.y_fronteira[-1] = -self.largura / 2

    def _dedo(self, d):
        o = self.f['ossos'][d]
        comprimento = o['proximal'] + o['media'] + o['distal'] + o['polpa']
        x_mcp = self.f['juntas']['pontaAoPulso'][d] * self.esc_c - comprimento
        mcp = Vector((x_mcp, self.y_no[d], self.ded['arco']['mm'][d]))
        leque = self.ded['leque']['fator']
        dy = mcp.y - mcp.y * leque
        dx = math.sqrt(max(1.0, o['metacarpo'] ** 2 - dy ** 2 - mcp.z ** 2))
        cmc = Vector((x_mcp - dx, mcp.y * leque, 0.0))
        ab = math.radians(_ABERTURA[d] * self.rep['abertura'])
        frente = Vector((math.cos(ab), math.sin(ab), 0.0))
        costas = Vector((0.0, 0.0, 1.0))
        # A MCP dobra em volta do eixo reto, através do dedo no plano da palma; a PIP e a DIP em volta dele inclinado
        # pela convergência (a cascata dos dedos), levado pela flexão de repouso da MCP.
        eixo_mcp = costas.cross(frente).normalized()
        q_mcp = Quaternion(eixo_mcp, math.radians(self.rep['mcp']))
        eixo_ip = (q_mcp @ (Quaternion(frente, math.radians(self.ded['convergencia']['graus'][d])) @ eixo_mcp))
        eixo_ip.normalize()
        comps = [o['proximal'], o['media'], o['distal'] + o['polpa']]
        giros = [q_mcp, Quaternion(eixo_ip, math.radians(self.rep['pip'])),
                 Quaternion(eixo_ip, math.radians(self.rep['dip']))]
        pontos = [mcp]
        dirs, normais = [], []
        frente_agora, costas_agora = frente, costas
        for q, comp in zip(giros, comps):
            frente_agora = (q @ frente_agora).normalized()
            costas_agora = (q @ costas_agora).normalized()
            dirs.append(frente_agora)
            normais.append(costas_agora)
            pontos.append(pontos[-1] + dirs[-1] * comp)
        (lp, ep), (ld, ed) = self._larguras_juntas(d)
        return {
            'cmc': cmc, 'mcp': mcp, 'pip': pontos[1], 'dip': pontos[2], 'ponta': pontos[3],
            'dirs': dirs, 'normais': normais, 'eixo_mcp': eixo_mcp, 'eixo_ip': eixo_ip, 'frente': frente,
            'larg_no': self.larg_no[d], 'pip_sec': (lp, ep), 'dip_sec': (ld, ed), 'polpa': o['polpa'],
            'distal': o['distal'],
        }

    def _polegar(self):
        o = self.f['ossos']['polegar']
        p = self.ded['polegar']
        cmc = Vector(p['cmc'])
        ang = math.radians(p['anguloNaPalma'])
        t0 = Vector((math.cos(ang), math.sin(ang), 0.0))
        costas = Vector((0.0, 0.0, 1.0))
        eixo_abd = costas.cross(t0).normalized()
        frente = (Quaternion(eixo_abd, math.radians(self.rep['polegarAbducao'])) @ t0).normalized()
        # "Costas" do polegar: a normal da palma perpendicular à direção dele, girada pela pronação para o lado do polegar
        # (+Y): a unha de lado, virada para fora, e a polpa de frente para o indicador — como na mão relaxada, e a flexão
        # (que dobra para o lado da polpa) leva a ponta para a palma e o mínimo. Na mão direita esse giro é negativo em
        # volta da direção do polegar (positivo levaria a unha para o indicador e a flexão para fora da mão).
        n0 = (costas - frente * costas.dot(frente)).normalized()
        normal = (Quaternion(frente, -math.radians(p['pronacao'])) @ n0).normalized()
        eixo = normal.cross(frente).normalized()
        comps = [o['metacarpo'], o['proximal'], o['distal'] + o['polpa']]
        angulos = [0.0, self.rep['polegarMcp'], self.rep['polegarIp']]
        pontos = [cmc]
        dirs, normais = [], []
        acumulado = 0.0
        for ang2, comp in zip(angulos, comps):
            acumulado += ang2
            q = Quaternion(eixo, math.radians(acumulado))
            dirs.append((q @ frente).normalized())
            normais.append((q @ normal).normalized())
            pontos.append(pontos[-1] + dirs[-1] * comp)
        ip = self.f['juntas']['polegar']['ip']
        lip = ip['largura'] * self.esc_l
        eip = espessura_pela_circunferencia(lip, ip['circunferencia'] * self.esc_l)
        return {
            'cmc': cmc, 'mcp': pontos[1], 'ip': pontos[2], 'ponta': pontos[3], 'dirs': dirs, 'normais': normais,
            'eixo': eixo, 'ip_sec': (lip, eip), 'polpa': o['polpa'], 'distal': o['distal'],
        }

    def _pulso(self):
        pulso = self.ded['pulso']
        self.pulso_larg = self.f['juntas']['pulso']['largura'] * self.esc_l
        self.pulso_esp = pulso['espessura']
        self.pulso_raio = pulso['raio']
        self.esp_mao = self.ded['espessuraDaMao']['mm']
        self.raio_mao = self.ded['espessuraDaMao']['raio']

    # ------------------------------------------------------------------ antebraço
    def circunferencia_antebraco(self, x):
        """Circunferência (mm) do antebraço de massinha a x ≤ 0 do pulso: a do pulso da ficha crescendo até a do cotovelo
        como t^expoente (t = distância do pulso sobre o comprimento do antebraço), pela dedução `perfilDoAntebraco`."""
        perfil = self.ded['perfilDoAntebraco']
        c_pulso = self.f['mao']['pulso']['mm']
        t = min(1.0, max(0.0, -x / self.antebraco))
        return c_pulso + (perfil['circunferenciaNoCotovelo'] - c_pulso) * t ** perfil['expoente']

    def secao_antebraco(self, x):
        """(largura, espessura, raio) do antebraço a x ≤ 0: o retângulo arredondado do pulso na escala da circunferência."""
        s = self.circunferencia_antebraco(x) / perimetro_retangulo_arredondado(self.pulso_larg, self.pulso_esp,
                                                                               self.pulso_raio)
        return self.pulso_larg * s, self.pulso_esp * s, self.pulso_raio * s

    # ------------------------------------------------------------------ ossos
    def ossos(self):
        """{nome: (cabeça, cauda, normal das costas)} da mão direita em repouso (mm), sem o sufixo do lado."""
        o = {
            'antebraco': (Vector((-self.antebraco, 0, 0)), Vector((-self.antebraco * self.ded['antebraco']['divisao'], 0, 0)),
                          Vector((0, 0, 1))),
            'torcao': (Vector((-self.antebraco * self.ded['antebraco']['divisao'], 0, 0)), Vector((0, 0, 0)), Vector((0, 0, 1))),
            'mao': (Vector((0, 0, 0)), self.dedos['medio']['mcp'].copy(), Vector((0, 0, 1))),
        }
        pol = self.polegar
        for i, (a, b) in enumerate((('cmc', 'mcp'), ('mcp', 'ip'), ('ip', 'ponta'))):
            o[f'polegar_{i + 1}'] = (pol[a].copy(), pol[b].copy(), pol['normais'][i].copy())
        for d in DEDOS4:
            dd = self.dedos[d]
            if d in METACARPO:
                o[METACARPO[d]] = (dd['cmc'].copy(), dd['mcp'].copy(), Vector((0, 0, 1)))
            for i, (a, b) in enumerate((('mcp', 'pip'), ('pip', 'dip'), ('dip', 'ponta'))):
                o[f'{d}_{i + 1}'] = (dd[a].copy(), dd[b].copy(), dd['normais'][i].copy())
        return o
