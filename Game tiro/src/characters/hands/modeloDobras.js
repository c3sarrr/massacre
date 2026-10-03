// O modelo das dobras das luvas no jogo (Fase 4.1b; desenho em docs/superpowers/specs/2026-09-26-4.1b-luvas-e-
// empunhadura-design.md, seção 4; plano, Tarefa 9): as mesmas contas de tools/blender/armas/maos_correcoes.py, na CPU,
// para a malha da luva sair no jogo como saiu na validação e no solver do Blender — o skin linear pelos ossos, a
// correção de cada junta (o raio de repouso por fora, o plano de contato da dobra por dentro, na ordem das juntas) e as
// peças de reforço presas à base corrigida. Ver o cabeçalho do módulo em Python para o porquê de cada passo; aqui só o
// que muda:
//  - o referencial é o do glTF (Y para cima) em mm; os vetores dos parâmetros (o `correcoes` dos extras, no referencial
//    do Blender) passam por deBlender;
//  - cada vértice é um vértice do Blender (o glTF duplica os das costuras de UV e o Draco reordena; o atributo
//    `_VERTICE` casa os dois — dadosDasPrimitivas);
//  - a pose entra como as deformações dos ossos (a matriz da pose vezes a inversa da de repouso, no referencial do braço;
//    no jogo, vindas do esqueleto do three), não como os quaternions locais: o giro de cada junta (o eixo e o ângulo) sai
//    de D_pai⁻¹·D_osso, sem depender do referencial local dos ossos, que o exportador do glTF converte;
//  - a palma que cede (4.1c, tools/blender/armas/maos_palma.py): o afundamento da palma de uma pega (os extras do .glb
//    da arma; `afundamento` o converte) soma depois das juntas e antes das peças presas, girado pela deformação do osso
//    `mao`; a capacidade de cada vértice (o `palma` dos parâmetros) fica em `palma`, para conferir.
// Puro (sem o three), para os testes do Node conferirem com a prova do relatório das luvas.

const RAD = Math.PI / 180;

/** Vetor do referencial do Blender (Z para cima) no do glTF (Y para cima). */
export const deBlender = (v) => [v[0], v[2], -v[1]];

const suave = (t) => {
  const c = t < 0 ? 0 : t > 1 ? 1 : t;
  return c * c * (3 - 2 * c);
};
const log1pexp = (z) => (z > 0 ? z + Math.log1p(Math.exp(-z)) : Math.log1p(Math.exp(z)));
const dot = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
const cross = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
const norm = (a) => Math.hypot(a[0], a[1], a[2]);
const unit = (a) => {
  const l = norm(a) || 1e-12;
  return [a[0] / l, a[1] / l, a[2] / l];
};
/** v girado em volta do eixo (unitário) pelo ângulo (radianos), pela regra da mão direita (Rodrigues). */
function girarEm(v, eixo, ang) {
  const c = Math.cos(ang);
  const s = Math.sin(ang);
  const k = cross(eixo, v);
  const d = dot(eixo, v) * (1 - c);
  return [v[0] * c + k[0] * s + eixo[0] * d, v[1] * c + k[1] * s + eixo[1] * d, v[2] * c + k[2] * s + eixo[2] * d];
}
/** R (3×3 por linhas) vezes v. */
const mulR = (R, o, v) => [
  R[o] * v[0] + R[o + 1] * v[1] + R[o + 2] * v[2],
  R[o + 3] * v[0] + R[o + 4] * v[1] + R[o + 5] * v[2],
  R[o + 6] * v[0] + R[o + 7] * v[1] + R[o + 8] * v[2],
];
/** Matriz de giro (3×3 por linhas) em volta do eixo unitário. */
function matrizDoGiro(eixo, ang) {
  const [x, y, z] = eixo;
  const c = Math.cos(ang);
  const s = Math.sin(ang);
  const t = 1 - c;
  return [t * x * x + c, t * x * y - s * z, t * x * z + s * y, t * x * y + s * z, t * y * y + c, t * y * z - s * x,
    t * x * z - s * y, t * y * z + s * x, t * z * z + c];
}

/** Gira v pela rotação mínima que leva `de` a `para` (unitários). */
function girarMinimo(v, de, para) {
  const k = cross(de, para);
  const s = norm(k);
  if (s <= 1e-9) return v;
  const c = dot(de, para);
  const e = [k[0] / s, k[1] / s, k[2] / s];
  const kv = dot(e, v);
  const ev = cross(e, v);
  return [v[0] * c + ev[0] * s + e[0] * kv * (1 - c), v[1] * c + ev[1] * s + e[1] * kv * (1 - c), v[2] * c + ev[2] * s + e[2] * kv * (1 - c)];
}

/** O eixo (unitário) e o ângulo (0–π) de uma rotação 3×3 (por linhas, no deslocamento `o`). */
function eixoAngulo(Q) {
  const tr = Q[0] + Q[4] + Q[8];
  const ang = Math.acos(Math.min(1, Math.max(-1, (tr - 1) / 2)));
  const v = [Q[7] - Q[5], Q[2] - Q[6], Q[3] - Q[1]];
  const s = norm(v);
  if (s > 1e-9) return { eixo: [v[0] / s, v[1] / s, v[2] / s], ang };
  // perto de 0 ou de π: pela diagonal (em 0 o eixo não importa, a junta fica em repouso)
  const d = [Math.sqrt(Math.max(0, (Q[0] + 1) / 2)), Math.sqrt(Math.max(0, (Q[4] + 1) / 2)), Math.sqrt(Math.max(0, (Q[8] + 1) / 2))];
  if (Q[1] < 0) d[1] = -d[1];
  if (Q[2] < 0) d[2] = -d[2];
  return { eixo: unit(d), ang };
}

/**
 * Os dados de um braço por vértice do Blender, das primitivas do glTF (uma por zona): as posições de repouso em mm, as
 * quatro influências de cada vértice, se é da base (as zonas fora do reforço) e os triângulos (todos e os da base),
 * pelos índices do Blender (`vertice`, o `_VERTICE` arredondado). O exportador grava a malha com skin no referencial da
 * cena, já na escala da raiz (u: `mmPorUnidade` = 25,4), e os ossos em metros dentro dela.
 * @param {{posicoes:ArrayLike<number>, juntas:ArrayLike<number>, pesos:ArrayLike<number>, vertice:ArrayLike<number>,
 *   indices:ArrayLike<number>, zona:string}[]} primitivas
 * @param {{zonaDasPecas?:string, mmPorUnidade?:number}} [o] a zona das peças presas (o reforço) e a escala da malha
 */
export function dadosDasPrimitivas(primitivas, { zonaDasPecas = 'reforco', mmPorUnidade = 25.4 } = {}) {
  let n = 0;
  for (const p of primitivas) for (let k = 0; k < p.vertice.length; k++) n = Math.max(n, Math.round(p.vertice[k]) + 1);
  const repouso = new Float64Array(n * 3);
  const juntas = new Uint16Array(n * 4);
  const pesos = new Float64Array(n * 4);
  const base = new Uint8Array(n);
  const visto = new Uint8Array(n);
  const tris = [];
  const trisBase = [];
  for (const p of primitivas) {
    const daBase = p.zona !== zonaDasPecas;
    const v = Array.from(p.vertice, (x) => Math.round(x));
    for (let k = 0; k < v.length; k++) {
      const i = v[k];
      if (!visto[i]) {
        visto[i] = 1;
        for (let c = 0; c < 3; c++) repouso[i * 3 + c] = p.posicoes[k * 3 + c] * mmPorUnidade;
        let soma = 0;
        for (let c = 0; c < 4; c++) soma += p.pesos[k * 4 + c];
        for (let c = 0; c < 4; c++) {
          juntas[i * 4 + c] = p.juntas[k * 4 + c];
          pesos[i * 4 + c] = p.pesos[k * 4 + c] / (soma || 1);
        }
      }
      if (daBase) base[i] = 1;
    }
    for (let k = 0; k < p.indices.length; k++) {
      tris.push(v[p.indices[k]]);
      if (daBase) trisBase.push(v[p.indices[k]]);
    }
  }
  if (visto.some((x) => !x)) throw new Error('modelo das dobras: há vértice do Blender sem vértice no glTF');
  return { n, repouso, juntas, pesos, base, triangulos: Uint32Array.from(tris), triangulosBase: Uint32Array.from(trisBase) };
}

/** Normais suaves (pela área) por vértice, dos triângulos. */
export function normaisDosVertices(pts, tris, n = pts.length / 3) {
  const vn = new Float64Array(n * 3);
  for (let t = 0; t < tris.length; t += 3) {
    const a = tris[t] * 3;
    const b = tris[t + 1] * 3;
    const c = tris[t + 2] * 3;
    const u = [pts[b] - pts[a], pts[b + 1] - pts[a + 1], pts[b + 2] - pts[a + 2]];
    const w = [pts[c] - pts[a], pts[c + 1] - pts[a + 1], pts[c + 2] - pts[a + 2]];
    const f = cross(u, w);
    for (const i of [a, b, c]) {
      vn[i] += f[0];
      vn[i + 1] += f[1];
      vn[i + 2] += f[2];
    }
  }
  for (let i = 0; i < vn.length; i += 3) {
    const l = Math.hypot(vn[i], vn[i + 1], vn[i + 2]) || 1e-12;
    vn[i] /= l;
    vn[i + 1] /= l;
    vn[i + 2] /= l;
  }
  return vn;
}

export class ModeloDobras {
  /**
   * @param {{malha:ReturnType<typeof dadosDasPrimitivas>, ossos:string[], pais:number[], cabecas:ArrayLike<number>,
   *   parametros:object, lado:string}} o `ossos` na ordem das juntas do skin (com o lado), `pais` o índice do pai de
   *   cada um (−1 na raiz), `cabecas` as cabeças de repouso (mm, glTF) e `parametros` o `correcoes` dos extras
   */
  constructor({ malha, ossos, pais, cabecas, parametros, lado }) {
    this.malha = malha;
    this.ossos = ossos;
    this.pais = pais;
    this.cabecas = Float64Array.from(cabecas);
    this.lado = lado;
    const pr = parametros;
    this.suave = pr.suaveMM;
    this.folga = pr.folgaMM;
    this.giroMinimo = pr.giroMinimo;
    const indice = new Map(ossos.map((o, i) => [o, i]));
    this.iMao = indice.get(`mao_${lado}`);
    if (this.iMao === undefined) throw new Error(`modelo das dobras: sem o osso mao_${lado}`);
    if (!pr.palma) throw new Error('modelo das dobras: os parâmetros sem a palma que cede (construa as luvas de novo)');
    this.palma = { vertices: Uint32Array.from(pr.palma.vertices), mm: Float64Array.from(pr.palma.mm) };
    const { n, repouso: p, juntas: J, pesos: W, base } = malha;
    const somaDe = (nomes) => {
      const alvo = new Set(nomes.map((o) => indice.get(`${o}_${lado}`)));
      const s = new Float64Array(n);
      for (let v = 0; v < n; v++) for (let c = 0; c < 4; c++) if (alvo.has(J[v * 4 + c])) s[v] += W[v * 4 + c];
      return s;
    };
    this.juntas = pr.juntas.map((j) => {
      const osso = indice.get(`${j.osso}_${lado}`);
      if (osso === undefined) throw new Error(`modelo das dobras: sem o osso ${j.osso}_${lado}`);
      const c0 = deBlender(j.centro);
      const a0 = deBlender(j.eixo);
      const n0 = deBlender(j.normal);
      const reto0 = deBlender(j.reto);
      const y0 = girarEm(reto0, a0, j.repouso * RAD);
      const wAbaixo = somaDe(j.abaixo);
      const wOutro = j.outros.length ? somaDe(j.outros) : new Float64Array(n);
      const u0 = cross(a0, n0);
      const ativos = [];
      const mistos = [];
      const peso = new Float64Array(n);
      const ladoV = new Float64Array(n);
      const d0 = new Float64Array(n);
      const fora = new Float64Array(n);
      for (let v = 0; v < n; v++) {
        const rel = [p[v * 3] - c0[0], p[v * 3 + 1] - c0[1], p[v * 3 + 2] - c0[2]];
        const ax = dot(rel, a0);
        const raio = norm([rel[0] - ax * a0[0], rel[1] - ax * a0[1], rel[2] - ax * a0[2]]);
        const faixa = suave((j.meia + pr.luvaMM + pr.faixaMM - Math.abs(ax)) / pr.faixaMM);
        const perto = suave((j.alcance + pr.faixaMM - raio) / pr.faixaMM);
        peso[v] = faixa * perto * Math.min(1, Math.max(0, 1 - wOutro[v])) * (base[v] ? 1 : 0);
        ladoV[v] = wAbaixo[v] >= 0.5 ? 1 : -1;
        d0[v] = ladoV[v] * dot(rel, n0);
        fora[v] = suave((pr.foraMM - dot(rel, u0)) / (2 * pr.foraMM));
        if (peso[v] > 0) ativos.push(v);
        if (wAbaixo[v] > 0.002 && wAbaixo[v] < 0.998 && peso[v] * fora[v] > 0) mistos.push(v);
      }
      return { nome: j.junta, osso, pai: pais[osso], c0, a0, reto0, y0, peso, ladoV, d0, fora,
        ativos: Uint32Array.from(ativos), mistos: Uint32Array.from(mistos) };
    });
    const pc = pr.pecas;
    this.pecas = {
      vertices: Uint32Array.from(pc.vertices), base: Uint32Array.from(pc.base.flat()), bar: Float64Array.from(pc.bar.flat()),
      afastamento: pc.afastamento.map(deBlender), normal: pc.normal.map(deBlender),
    };
  }

  /**
   * As deformações dos ossos (Float64Array de 12 por osso: R 3×3 por linhas e t) a partir dos giros de cada osso em
   * volta da cabeça dele, no referencial do braço em repouso ({osso com o lado: [ex, ey, ez, ângulo]}, glTF), pela
   * cadeia: D = D_pai · giro. Os ossos sem giro seguem o pai.
   */
  deformacoesDosGiros(giros) {
    const nb = this.ossos.length;
    const D = new Float64Array(nb * 12);
    const feito = new Uint8Array(nb);
    const fazer = (i) => {
      if (feito[i]) return;
      const pai = this.pais[i];
      if (pai >= 0) fazer(pai);
      const g = giros[this.ossos[i]];
      const G = g ? matrizDoGiro(unit([g[0], g[1], g[2]]), g[3]) : [1, 0, 0, 0, 1, 0, 0, 0, 1];
      const c = [this.cabecas[i * 3], this.cabecas[i * 3 + 1], this.cabecas[i * 3 + 2]];
      const Gc = mulR(G, 0, c);
      const tg = [c[0] - Gc[0], c[1] - Gc[1], c[2] - Gc[2]]; // o giro em volta da cabeça: x → G·x + (c − G·c)
      const o = i * 12;
      if (pai < 0) {
        for (let k = 0; k < 9; k++) D[o + k] = G[k];
        D.set(tg, o + 9);
      } else {
        const op = pai * 12;
        for (let r = 0; r < 3; r++) {
          for (let col = 0; col < 3; col++) {
            D[o + r * 3 + col] = D[op + r * 3] * G[col] + D[op + r * 3 + 1] * G[3 + col] + D[op + r * 3 + 2] * G[6 + col];
          }
        }
        const t = mulR(D, op, tg);
        D[o + 9] = t[0] + D[op + 9];
        D[o + 10] = t[1] + D[op + 10];
        D[o + 11] = t[2] + D[op + 11];
      }
      feito[i] = 1;
    };
    for (let i = 0; i < nb; i++) fazer(i);
    return D;
  }

  /**
   * O afundamento da palma de uma pega (os extras do .glb da arma, `palma` de um lado: {vertices, vetores} em mm no
   * referencial do braço com o osso `mao` em repouso, no do Blender) pronto para `avaliar`: os vetores no glTF. Lança se
   * um vértice não é desta malha ou não cede (o .glb de outras luvas) ou se algum vai além do que ele cede.
   * @param {{vertices:number[], vetores:number[][]}} palma
   * @returns {{vertices:Uint32Array, vetores:Float64Array}}
   */
  afundamento(palma) {
    const { vertices, vetores } = palma;
    if (!Array.isArray(vertices) || !Array.isArray(vetores) || vertices.length !== vetores.length) {
      throw new Error('palma: os vértices e os vetores do afundamento em listas do mesmo tamanho');
    }
    const cap = new Map(Array.from(this.palma.vertices, (v, k) => [v, this.palma.mm[k]]));
    const v = new Uint32Array(vertices.length);
    const vet = new Float64Array(vertices.length * 3);
    for (let k = 0; k < vertices.length; k++) {
      const i = vertices[k];
      const c = cap.get(i);
      if (!Number.isInteger(i) || c === undefined) throw new Error(`palma: o vértice ${i} não cede nestas luvas`);
      const g = deBlender(vetores[k]);
      if (!g.every(Number.isFinite)) throw new Error(`palma: o vetor do vértice ${i} não é número`);
      // a capacidade gravada com 3 casas: a folga do arredondamento
      if (norm(g) > c + 2e-3) throw new Error(`palma: o vértice ${i} afunda ${norm(g).toFixed(3)} mm, além dos ${c} mm que cede`);
      v[k] = i;
      vet.set(g, k * 3);
    }
    return { vertices: v, vetores: vet };
  }

  /**
   * As posições (mm, glTF, Float64Array de 3 por vértice do Blender) com as deformações D (ver deformacoesDosGiros) e o
   * afundamento da palma de uma pega (`afundar`, de `afundamento`), se houver.
   */
  avaliar(D, afundar = null) {
    const { n, repouso: p, juntas: J, pesos: W } = this.malha;
    const alvo = new Float64Array(n * 3);
    for (let v = 0; v < n; v++) {
      const x = p[v * 3];
      const y = p[v * 3 + 1];
      const z = p[v * 3 + 2];
      for (let c = 0; c < 4; c++) {
        const w = W[v * 4 + c];
        if (w === 0) continue;
        const o = J[v * 4 + c] * 12;
        alvo[v * 3] += w * (D[o] * x + D[o + 1] * y + D[o + 2] * z + D[o + 9]);
        alvo[v * 3 + 1] += w * (D[o + 3] * x + D[o + 4] * y + D[o + 5] * z + D[o + 10]);
        alvo[v * 3 + 2] += w * (D[o + 6] * x + D[o + 7] * y + D[o + 8] * z + D[o + 11]);
      }
    }
    for (const j of this.juntas) this.#aplicar(j, D, alvo);
    if (afundar) this.#afundar(D, afundar, alvo);
    this.#seguirBase(alvo);
    return alvo;
  }

  // o afundamento da palma girado pela deformação do osso `mao` (a parte de rotação de D, por linhas)
  #afundar(D, { vertices, vetores }, alvo) {
    const o = this.iMao * 12;
    for (let k = 0; k < vertices.length; k++) {
      const v = vertices[k] * 3;
      const x = vetores[k * 3];
      const y = vetores[k * 3 + 1];
      const z = vetores[k * 3 + 2];
      alvo[v] += D[o] * x + D[o + 1] * y + D[o + 2] * z;
      alvo[v + 1] += D[o + 3] * x + D[o + 4] * y + D[o + 5] * z;
      alvo[v + 2] += D[o + 6] * x + D[o + 7] * y + D[o + 8] * z;
    }
  }

  #aplicar(j, D, alvo) {
    const o = j.osso * 12;
    const op = j.pai >= 0 ? j.pai * 12 : -1;
    // o giro da junta: D_pai⁻¹·D_osso (a parte de rotação), no referencial do braço em repouso
    const Q = new Array(9);
    for (let r = 0; r < 3; r++) {
      for (let c = 0; c < 3; c++) {
        Q[r * 3 + c] = op < 0 ? D[o + r * 3 + c]
          : D[op + r] * D[o + c] + D[op + 3 + r] * D[o + 3 + c] + D[op + 6 + r] * D[o + 6 + c];
      }
    }
    const { eixo: e0, ang } = eixoAngulo(Q);
    if (ang < this.giroMinimo) return;
    const P = (v) => (op < 0 ? v : mulR(D, op, v));
    const c = mulR(D, o, j.c0);
    c[0] += D[o + 9];
    c[1] += D[o + 10];
    c[2] += D[o + 11];
    const a = P(j.a0);
    const e = P(e0);
    // por fora: o raio de repouso em volta do eixo do giro inteiro
    const p = this.malha.repouso;
    for (const v of j.mistos) {
      const r0v = [p[v * 3] - j.c0[0], p[v * 3 + 1] - j.c0[1], p[v * 3 + 2] - j.c0[2]];
      const ax0 = dot(r0v, e0);
      const r0 = norm([r0v[0] - ax0 * e0[0], r0v[1] - ax0 * e0[1], r0v[2] - ax0 * e0[2]]);
      const rel = [alvo[v * 3] - c[0], alvo[v * 3 + 1] - c[1], alvo[v * 3 + 2] - c[2]];
      const ax = dot(rel, e);
      const perp = [rel[0] - ax * e[0], rel[1] - ax * e[1], rel[2] - ax * e[2]];
      const rp = norm(perp);
      if (!(rp > 1 && r0 > 1)) continue;
      const k = r0 / Math.max(rp, 1e-9);
      const w = j.peso[v] * j.fora[v];
      for (let q = 0; q < 3; q++) {
        const novo = c[q] + ax * e[q] + perp[q] * k;
        alvo[v * 3 + q] += (novo - alvo[v * 3 + q]) * w;
      }
    }
    // por dentro: o plano de contato entre a direção reta de cima e a do osso da junta
    const y = unit(mulR(D, o, j.y0));
    const rt = P(j.reto0);
    let nn = [y[0] + rt[0], y[1] + rt[1], y[2] + rt[2]];
    const na = dot(nn, a);
    nn = unit([nn[0] - a[0] * na, nn[1] - a[1] * na, nn[2] - a[2] * na]);
    const s = this.suave;
    const g = (x) => s * log1pexp(-x / s);
    for (const v of j.ativos) {
      const lv = j.ladoV[v];
      const d = lv * ((alvo[v * 3] - c[0]) * nn[0] + (alvo[v * 3 + 1] - c[1]) * nn[1] + (alvo[v * 3 + 2] - c[2]) * nn[2]);
      const empurra = Math.max(g(d - this.folga) - g(j.d0[v] - this.folga), 0);
      if (empurra === 0) continue;
      const m = lv * empurra * j.peso[v];
      alvo[v * 3] += m * nn[0];
      alvo[v * 3 + 1] += m * nn[1];
      alvo[v * 3 + 2] += m * nn[2];
    }
  }

  #seguirBase(alvo) {
    const { vertices, base, bar, afastamento, normal } = this.pecas;
    const vn = normaisDosVertices(alvo, this.malha.triangulosBase, this.malha.n);
    for (let k = 0; k < vertices.length; k++) {
      const ponto = [0, 0, 0];
      const ns = [0, 0, 0];
      for (let c = 0; c < 3; c++) {
        const i = base[k * 3 + c] * 3;
        const b = bar[k * 3 + c];
        for (let q = 0; q < 3; q++) {
          ponto[q] += b * alvo[i + q];
          ns[q] += b * vn[i + q];
        }
      }
      const off = girarMinimo(afastamento[k], normal[k], unit(ns));
      const v = vertices[k] * 3;
      alvo[v] = ponto[0] + off[0];
      alvo[v + 1] = ponto[1] + off[1];
      alvo[v + 2] = ponto[2] + off[2];
    }
  }
}

