// Um braço de luva no jogo (Fase 4.1b; desenho em docs/superpowers/specs/2026-09-26-4.1b-luvas-e-empunhadura-design.md,
// seções 5 e 7.3; plano, Tarefa 9): o esqueleto próprio (os 20 ossos do luvas.glb debaixo da raiz com a escala do
// glTF), a luva deformada na CPU pelo modelo das dobras (as mesmas contas do Blender: a malha sai como saiu na validação
// e no solver da empunhadura), o antebraço e a braçadeira de massinha (skin de dois ossos na GPU, ClayMaterial sem boil).
//  - `aplicarPega(pega)`: os 17 ossos de dedo no quaternion do clipe `empunhadura` do .glb da arma — só com a mesma
//    marca do rig (as luvas e a arma construídas juntas);
//  - `colocar(pulso, maoQuat, cotovelo, cima)`: o osso `mao` no pulso e na orientação da pega (no referencial de quem
//    contém o braço); o antebraço apontando do cotovelo para o pulso, com o comprimento da ficha (o cotovelo de verdade
//    fica no alinhamento, a esse comprimento do pulso) e na torção neutra da anatomia (o polegar para `cima`, a meia
//    pronação do antebraço com o cotovelo dobrado); a torção até a mão dividida meio a meio entre a `torcao` e a `mao`;
//    devolve os ângulos do pulso e do antebraço e um aviso para cada limite da AAOS passado (a ficha);
//  - `setFaccao`, `setBracadeira`, `setCorDaMassa`.
// A luva só é recalculada quando a pose dos ossos muda (dedos, torção, pulso): mover o braço inteiro não custa nada.

import * as THREE from 'three';
import { ClayMaterial } from '../../clay/ClayMaterial.js';
import { BRACO_DE_MASSA, OSSOS_DE_DEDO } from '../../data/luvas.js';
import { OSSOS_DO_ANTEBRACO } from './antebracoMassa.js';
import { normaisDosVertices } from './modeloDobras.js';

const MM_POR_U = 25.4;
const GRAUS = 180 / Math.PI;
const IGUAL = 1e-10; // 1 − |q·q'| abaixo disso é o mesmo giro (≈ 3·10⁻⁵ rad)
const X = new THREE.Vector3(1, 0, 0);
const CIMA = Object.freeze(new THREE.Vector3(0, 1, 0));

const _d = new THREE.Vector3();
const _s = new THREE.Vector3();
const _y = new THREE.Vector3();
const _z = new THREE.Vector3();
const _f = new THREE.Vector3();
const _mat = new THREE.Matrix4();
const _q = new THREE.Quaternion();
const _r = new THREE.Quaternion();

/**
 * A torção de um giro Δ em volta do eixo do antebraço (+X do braço) e o que sobra para o pulso (swing-twist): Δ = T·B,
 * a pronação T do antebraço e o balanço B do pulso no referencial do rádio já girado — o rádio leva a pronação inteira
 * até o pulso, e a flexão e o desvio são medidos nele (a direção da mão, R(−τ)·Δ·X). A metade da torção vai para o osso
 * `torcao` e a outra para a `mao`: é a divisão do skin, para a malha do punho torcer ao longo do antebraço.
 * @param {THREE.Quaternion} delta o giro da mão no referencial do braço, do repouso para a pose
 * @param {number} polegar −1 (direita, polegar em −Z) ou +1 (esquerda)
 * @returns {{torcao:number, meia:THREE.Quaternion, flexao:number, desvio:number, pronacao:number}} a torção total
 *   (radianos, em +X), o giro da metade e os ângulos em graus: flexão (+) e extensão (−) do pulso, desvio radial (+) e
 *   ulnar (−), pronação (+) e supinação (−) do antebraço a partir da meia pronação
 */
export function torcaoDoPulso(delta, polegar) {
  const q = delta.w < 0 ? new THREE.Quaternion(-delta.x, -delta.y, -delta.z, -delta.w) : delta.clone();
  const torcao = Math.hypot(q.x, q.w) > 1e-12 ? 2 * Math.atan2(q.x, q.w) : 0;
  const meia = new THREE.Quaternion().setFromAxisAngle(X, torcao / 2);
  // a direção da mão no referencial do rádio: R(−τ)·Δ·X (a torção inteira desfeita)
  _f.copy(X).applyQuaternion(q).applyAxisAngle(X, -torcao);
  return {
    torcao, meia,
    flexao: Math.atan2(-_f.y, _f.x) * GRAUS,
    desvio: Math.atan2(polegar * _f.z, _f.x) * GRAUS,
    pronacao: polegar * torcao * GRAUS,
  };
}

/** Os avisos dos limites da AAOS (a ficha: `limites.pulso` e `limites.antebraco`, graus) passados. */
export function avisosDoPulso(a, limites) {
  const p = limites.pulso;
  const b = limites.antebraco;
  const out = [];
  const passa = (valor, limite, nome) => {
    if (valor > limite + 1e-9) out.push(`${nome} de ${valor.toFixed(1)}° (limite ${limite}°)`);
  };
  passa(a.flexao, p.flexao, 'pulso: flexão');
  passa(-a.flexao, p.extensao, 'pulso: extensão');
  passa(a.desvio, p.radial, 'pulso: desvio radial');
  passa(-a.desvio, p.ulnar, 'pulso: desvio ulnar');
  passa(a.pronacao, b.pronacao, 'antebraço: pronação');
  passa(-a.pronacao, b.supinacao, 'antebraço: supinação');
  return out;
}

const mesmoGiro = (a, b) => 1 - Math.abs(a.dot(b)) < IGUAL;

export class BracoLuva {
  #molde;
  #materiaisDe;
  #faccaoPedida;
  #malhas = [];
  #bones = [];
  #iMao;
  #iTorcao;
  #iAnte;
  #rel;
  #D;
  #pts = null;
  #raiz;
  #rig;
  #sujo = true;

  /**
   * @param {{molde:ReturnType<import('./moldeLuva.js').moldeDoBraco>, faccao:string, materiais:Object<string, THREE.Material>,
   *   materiaisDe:(faccao:string)=>Promise<Object<string, THREE.Material>>, antebraco:{antebraco:THREE.BufferGeometry,
   *   bracadeira:THREE.BufferGeometry}, corDaMassa:string, limites:{pulso:object, antebraco:object}, log?:object|null}} o
   *   `materiais` = os da facção (da LuvasSource, divididos entre os braços); `antebraco` = as malhas de massinha
   *   (divididas); o braço é dono do esqueleto, das cópias das malhas da luva e dos materiais de massinha
   */
  constructor({ molde, faccao, materiais, materiaisDe, antebraco, corDaMassa, limites, log = null }) {
    this.#molde = molde;
    this.#materiaisDe = materiaisDe;
    this.lado = molde.lado;
    this.marca = molde.marca;
    this.faccao = faccao;
    this.#faccaoPedida = faccao;
    this.limites = limites;
    this.log = log;
    this.grupo = new THREE.Group();
    this.grupo.name = `luvas:${this.lado}`;
    // o esqueleto: a raiz com a escala do glTF, o rig e os ossos na pose de repouso
    const raiz = new THREE.Object3D();
    raiz.name = 'luvas';
    raiz.position.copy(molde.raiz.posicao);
    raiz.quaternion.copy(molde.raiz.quaternion);
    raiz.scale.copy(molde.raiz.escala);
    const rig = new THREE.Object3D();
    rig.name = `rig_${this.lado}`;
    rig.position.copy(molde.rig.posicao);
    rig.quaternion.copy(molde.rig.quaternion);
    rig.scale.copy(molde.rig.escala);
    raiz.add(rig);
    this.grupo.add(raiz);
    this.#raiz = raiz;
    this.#rig = rig;
    this.ossos = {};
    molde.ossos.forEach((nome, i) => {
      const b = new THREE.Bone();
      b.name = nome;
      const r = molde.repousoLocal[i];
      b.position.copy(r.posicao);
      b.quaternion.copy(r.quaternion);
      b.scale.copy(r.escala);
      (molde.pais[i] >= 0 ? this.#bones[molde.pais[i]] : rig).add(b);
      this.#bones.push(b);
      this.ossos[nome.slice(0, -2)] = b;
    });
    this.#iMao = molde.ossos.indexOf(`mao_${this.lado}`);
    this.#iTorcao = molde.ossos.indexOf(`torcao_${this.lado}`);
    this.#iAnte = molde.ossos.indexOf(`antebraco_${this.lado}`);
    this.#rel = molde.ossos.map(() => new THREE.Matrix4());
    this.#D = new Float64Array(molde.ossos.length * 12);
    // a luva: uma malha por zona, com as posições, as normais e as tangentes da pose (a cópia do braço) e as de repouso
    for (const p of molde.primitivas) {
      const g = p.geometria.clone();
      g.deleteAttribute('skinIndex');
      g.deleteAttribute('skinWeight');
      g.deleteAttribute('_vertice');
      g.setAttribute('repouso', g.attributes.position.clone());
      g.setAttribute('normalRepouso', g.attributes.normal.clone());
      g.name = `luva_${this.lado}:${p.zona}`;
      const m = new THREE.Mesh(g, materiais[p.zona]);
      m.name = g.name;
      m.castShadow = true;
      m.receiveShadow = true;
      this.grupo.add(m);
      this.#malhas.push({
        malha: m, zona: p.zona, vertice: p.vertice,
        normal: g.attributes.normal.array.slice(), tangente: g.attributes.tangent.array.slice(),
      });
    }
    // o antebraço e a braçadeira de massinha: skin de dois ossos na GPU, preso ao grupo (a malha no referencial do braço)
    const M = BRACO_DE_MASSA;
    const doisOssos = OSSOS_DO_ANTEBRACO.map((o) => this.ossos[o]);
    const inversas = OSSOS_DO_ANTEBRACO.map((o) => molde.relRepousoInv[molde.ossos.indexOf(`${o}_${this.lado}`)].clone());
    this.skeleton = new THREE.Skeleton(doisOssos, inversas);
    this.materialMassa = new ClayMaterial({ color: corDaMassa, roughness: M.massa.roughness, wetness: M.massa.wetness, touched: true, boil: 0, seed: `antebraco-${this.lado}` });
    this.materialMassa.setObjectSize(M.massa.objectSize);
    this.antebraco = this.#pele(antebraco.antebraco, this.materialMassa, `antebraco-${this.lado}`);
    const B = M.bracadeira;
    this.materialBracadeira = new ClayMaterial({ color: corDaMassa, roughness: B.massa.roughness, wetness: B.massa.wetness, touched: true, boil: 0, seed: `bracadeira-${this.lado}` });
    this.materialBracadeira.setObjectSize(B.massa.objectSize);
    this.bracadeira = this.#pele(antebraco.bracadeira, this.materialBracadeira, `bracadeira-${this.lado}`);
    this.bracadeira.visible = false;
    this.pega = null;
    this.angulos = { flexao: 0, desvio: 0, pronacao: 0 };
    this.avisos = [];
    this.#deformar();
  }

  #pele(geometria, material, nome) {
    const m = new THREE.SkinnedMesh(geometria, material);
    m.name = nome;
    m.frustumCulled = false; // os ossos saem da caixa de repouso
    m.castShadow = true;
    m.receiveShadow = true;
    this.grupo.add(m);
    m.bind(this.skeleton, new THREE.Matrix4());
    return m;
  }

  /** As malhas da luva (uma por zona). */
  get malhas() {
    return this.#malhas.map((m) => m.malha);
  }

  get triangulos() {
    return this.#molde.triangulos;
  }

  /** As posições da luva na pose atual (mm, referencial do braço), uma por vértice do Blender (o `luvas_contato`). */
  get posicoesMM() {
    return this.#pts;
  }

  /**
   * Os dedos na pega de uma arma: {marca: {d, e}, dedos: {d|e: {osso: [x, y, z, w]}}} (lida do .glb da arma).
   * Recusa a pega de um rig diferente (as luvas mudaram depois de a arma ser construída).
   */
  aplicarPega(pega) {
    const marca = pega?.marca?.[this.lado];
    if (marca !== this.marca) {
      throw new Error(`pega: a marca do rig ${this.lado} da arma (${String(marca).slice(0, 12)}) não é a das luvas (${this.marca.slice(0, 12)}); construa a arma de novo`);
    }
    const dedos = pega.dedos?.[this.lado] ?? {};
    for (const osso of OSSOS_DE_DEDO) if (!dedos[osso]) throw new Error(`pega: sem a rotação de ${osso}_${this.lado}`);
    for (const osso of OSSOS_DE_DEDO) this.ossos[osso].quaternion.fromArray(dedos[osso]).normalize();
    this.pega = pega;
    this.#sujo = true;
    this.atualizar();
  }

  /** Os dedos de volta ao repouso (sem arma). */
  soltarPega() {
    const m = this.#molde;
    for (const osso of OSSOS_DE_DEDO) this.ossos[osso].quaternion.copy(m.repousoLocal[m.ossos.indexOf(`${osso}_${this.lado}`)].quaternion);
    this.pega = null;
    this.#sujo = true;
    this.atualizar();
  }

  /**
   * Põe o braço: o osso `mao` em `pulso` com a rotação `maoQuat` (a do osso no referencial de quem contém o grupo) e o
   * antebraço apontando de `cotovelo` para o pulso, na torção neutra com o polegar para `cima`.
   * @param {THREE.Vector3} pulso @param {THREE.Quaternion} maoQuat @param {THREE.Vector3} cotovelo
   * @param {THREE.Vector3} [cima] a direção do polegar do antebraço na meia pronação (padrão: +Y de quem contém)
   * @returns {{angulos:{flexao:number, desvio:number, pronacao:number}, avisos:string[]}}
   */
  colocar(pulso, maoQuat, cotovelo, cima = CIMA) {
    const m = this.#molde;
    _d.subVectors(pulso, cotovelo);
    const dist = _d.length();
    if (!(dist > 1e-9)) throw new Error('braço: o cotovelo em cima do pulso');
    _d.divideScalar(dist);
    _s.copy(cima).addScaledVector(_d, -cima.dot(_d));
    if (_s.lengthSq() < 1e-12) _s.set(0, 0, 1).addScaledVector(_d, -_d.z); // o antebraço em pé: qualquer lado serve
    _s.normalize();
    // o grupo: +X do braço no antebraço, o polegar (σ·Z) para cima
    _z.copy(_s).multiplyScalar(m.polegar);
    _y.crossVectors(_z, _d);
    _mat.makeBasis(_d, _y, _z);
    this.grupo.quaternion.setFromRotationMatrix(_mat);
    this.grupo.position.copy(pulso).sub(_f.copy(m.pulso).applyQuaternion(this.grupo.quaternion));
    // o giro da mão no referencial do braço, do repouso para a pose: Δ = Q⁻¹·M·R_mão⁻¹
    const delta = _q.copy(this.grupo.quaternion).invert().multiply(maoQuat).multiply(_r.copy(m.quatRepouso[this.#iMao]).invert());
    const t = torcaoDoPulso(delta, m.polegar);
    // a `torcao` com a metade; a `mao` com o resto (o giro inteiro no referencial do braço)
    const rt = t.meia.clone().multiply(m.quatRepouso[this.#iTorcao]);
    const localT = m.quatRepouso[this.#iAnte].clone().invert().multiply(rt);
    const rm = delta.clone().multiply(m.quatRepouso[this.#iMao]);
    const localM = rt.clone().invert().multiply(rm);
    const torcao = this.#bones[this.#iTorcao];
    const mao = this.#bones[this.#iMao];
    if (!mesmoGiro(torcao.quaternion, localT) || !mesmoGiro(mao.quaternion, localM)) {
      torcao.quaternion.copy(localT);
      mao.quaternion.copy(localM);
      this.#sujo = true;
    }
    this.angulos = { flexao: t.flexao, desvio: t.desvio, pronacao: t.pronacao };
    const avisos = avisosDoPulso(this.angulos, this.limites);
    if (avisos.join() !== this.avisos.join() && avisos.length) this.log?.warn?.(`luvas ${this.lado}: ${avisos.join('; ')}`);
    this.avisos = avisos;
    this.atualizar();
    return { angulos: this.angulos, avisos };
  }

  /** Recalcula a luva se a pose dos ossos mudou; true se recalculou. */
  atualizar() {
    if (!this.#sujo) return false;
    this.#deformar();
    return true;
  }

  // As deformações dos ossos no referencial do braço (a pose vezes a inversa do repouso; mm), o modelo das dobras e as
  // posições, normais e tangentes de cada vértice do glTF pelo vértice do Blender dele. A normal e a tangente de
  // repouso (as do Blender) giram pela rotação mínima entre a normal de repouso do modelo e a da pose.
  #deformar() {
    const m = this.#molde;
    this.#raiz.updateMatrix();
    this.#rig.updateMatrix();
    const base = _mat.multiplyMatrices(this.#raiz.matrix, this.#rig.matrix);
    const D = this.#D;
    for (let i = 0; i < this.#bones.length; i++) {
      const b = this.#bones[i];
      b.updateMatrix();
      const pai = m.pais[i];
      this.#rel[i].multiplyMatrices(pai >= 0 ? this.#rel[pai] : base, b.matrix);
      const e = _m2.multiplyMatrices(this.#rel[i], m.relRepousoInv[i]).elements;
      const o = i * 12;
      for (let r = 0; r < 3; r++) for (let c = 0; c < 3; c++) D[o + r * 3 + c] = e[c * 4 + r];
      D[o + 9] = e[12] * MM_POR_U;
      D[o + 10] = e[13] * MM_POR_U;
      D[o + 11] = e[14] * MM_POR_U;
    }
    const pts = m.modelo.avaliar(D);
    this.#pts = pts;
    const n = m.modelo.malha.n;
    const vn = normaisDosVertices(pts, m.modelo.malha.triangulos, n);
    const n0 = m.normaisRepouso;
    // o giro mínimo de cada vértice do Blender (eixo·seno e cosseno)
    const giro = new Float64Array(n * 4);
    for (let v = 0; v < n; v++) {
      const a = v * 3;
      const kx = n0[a + 1] * vn[a + 2] - n0[a + 2] * vn[a + 1];
      const ky = n0[a + 2] * vn[a] - n0[a] * vn[a + 2];
      const kz = n0[a] * vn[a + 1] - n0[a + 1] * vn[a];
      giro[v * 4] = kx;
      giro[v * 4 + 1] = ky;
      giro[v * 4 + 2] = kz;
      giro[v * 4 + 3] = n0[a] * vn[a] + n0[a + 1] * vn[a + 1] + n0[a + 2] * vn[a + 2];
    }
    for (const z of this.#malhas) {
      const g = z.malha.geometry;
      const P = g.attributes.position.array;
      const N = g.attributes.normal.array;
      const T = g.attributes.tangent.array;
      for (let k = 0; k < z.vertice.length; k++) {
        const v = z.vertice[k];
        P[k * 3] = pts[v * 3] / MM_POR_U;
        P[k * 3 + 1] = pts[v * 3 + 1] / MM_POR_U;
        P[k * 3 + 2] = pts[v * 3 + 2] / MM_POR_U;
        girarMinimo(z.normal, k * 3, giro, v, N, k * 3);
        girarMinimo(z.tangente, k * 4, giro, v, T, k * 4);
        T[k * 4 + 3] = z.tangente[k * 4 + 3];
      }
      g.attributes.position.needsUpdate = true;
      g.attributes.normal.needsUpdate = true;
      g.attributes.tangent.needsUpdate = true;
      g.computeBoundingSphere();
      g.computeBoundingBox();
    }
    this.#sujo = false;
  }

  /** Troca a pintura da luva pela da facção (a nova entra quando os materiais estão prontos). */
  async setFaccao(faccao) {
    this.#faccaoPedida = faccao;
    const mats = await this.#materiaisDe(faccao);
    if (this.#faccaoPedida !== faccao || !this.#malhas.length) return false;
    for (const z of this.#malhas) z.malha.material = mats[z.zona];
    this.faccao = faccao;
    return true;
  }

  /** Braçadeira do time: cor (hex) ou null para esconder. */
  setBracadeira(cor) {
    this.bracadeira.visible = Boolean(cor);
    if (cor) this.materialBracadeira.color.set(cor);
  }

  /** Cor da massa do antebraço (a do boneco). */
  setCorDaMassa(cor) {
    this.materialMassa.color.set(cor);
  }

  dispose() {
    this.grupo.removeFromParent();
    for (const z of this.#malhas) z.malha.geometry.dispose();
    this.#malhas = [];
    this.materialMassa.dispose();
    this.materialBracadeira.dispose();
    this.skeleton.dispose();
  }
}

const _m2 = new THREE.Matrix4();

/** Gira o vetor (3 componentes em `de[i]`) pelo giro mínimo do vértice v (eixo·sen e cos em `giro`) e grava em `para[j]`. */
function girarMinimo(de, i, giro, v, para, j) {
  const x = de[i];
  const y = de[i + 1];
  const z = de[i + 2];
  const kx = giro[v * 4];
  const ky = giro[v * 4 + 1];
  const kz = giro[v * 4 + 2];
  const c = giro[v * 4 + 3];
  const s2 = kx * kx + ky * ky + kz * kz;
  if (s2 < 1e-18) {
    para[j] = x;
    para[j + 1] = y;
    para[j + 2] = z;
    return;
  }
  // Rodrigues com k = eixo·sen: v·c + (k×v) + k·(k·v)·(1 − c)/sen²
  const f = (kx * x + ky * y + kz * z) * (1 - c) / s2;
  para[j] = x * c + (ky * z - kz * y) + kx * f;
  para[j + 1] = y * c + (kz * x - kx * z) + ky * f;
  para[j + 2] = z * c + (kx * y - ky * x) + kz * f;
}
