// A medida do `luvas_contato` (Fase 4.1b; desenho em docs/superpowers/specs/2026-09-26-4.1b-luvas-e-empunhadura-design.md,
// seção 7.5; plano, Tarefa 11): a luva deformada de verdade no jogo (as posições que o braço calculou pelo modelo das
// dobras, as mesmas contas do Blender) contra a malha da arma numa BVH (three-mesh-bvh), no referencial da raiz da arma.
// Para cada sonda que o solver do Blender gravou nos extras da pega (o vértice de cada contato e a distância que ele
// mediu), a distância com sinal no jogo — negativa dentro da arma, pelo lado da normal do triângulo mais perto — e a
// diferença; e a penetração máxima de todos os vértices da luva. As duas medidas têm de bater (≤ 0,05 mm): prova que a
// pega, o referencial do osso `mao` e as dobras chegam ao jogo como saíram do Blender.

import * as THREE from 'three';
import { MeshBVH } from 'three-mesh-bvh';

const MM_POR_U = 25.4;
const _p = new THREE.Vector3();
const _a = new THREE.Vector3();
const _b = new THREE.Vector3();
const _c = new THREE.Vector3();
const _n = new THREE.Vector3();
const _m = new THREE.Matrix4();

/**
 * A malha de uma arma numa BVH, no referencial de `raiz` (as malhas dela e das filhas; as geometrias com índice).
 * @param {THREE.Object3D} raiz a instância da arma (ou a raiz do nível `perto` no .glb)
 * @param {(malha:THREE.Mesh)=>boolean} [filtro]
 */
export function bvhDaArma(raiz, filtro = () => true) {
  raiz.updateMatrixWorld(true);
  const inv = new THREE.Matrix4().copy(raiz.matrixWorld).invert();
  const pos = [];
  const idx = [];
  raiz.traverse((o) => {
    if (!o.isMesh || !filtro(o)) return;
    const g = o.geometry;
    const m = _m.multiplyMatrices(inv, o.matrixWorld);
    const base = pos.length / 3;
    const p = g.attributes.position;
    for (let i = 0; i < p.count; i++) {
      _p.fromBufferAttribute(p, i).applyMatrix4(m);
      pos.push(_p.x, _p.y, _p.z);
    }
    if (g.index) for (let i = 0; i < g.index.count; i++) idx.push(base + g.index.getX(i));
    else for (let i = 0; i < p.count; i++) idx.push(base + i);
  });
  if (!idx.length) throw new Error('luvas_contato: a arma sem malha');
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.BufferAttribute(Float32Array.from(pos), 3));
  g.setIndex(new THREE.BufferAttribute(Uint32Array.from(idx), 1));
  return new MeshBVH(g);
}

const _q = new THREE.Vector3();
const _pn = new THREE.Vector3();
const _bar = new THREE.Vector3();
const _tri = new THREE.Triangle();

/** Ângulo interno do triângulo (a, b, c) no vértice a. */
function anguloEm(a, b, c) {
  return _p.subVectors(b, a).angleTo(_q.subVectors(c, a));
}

/**
 * Distância com sinal (u) de um ponto (referencial da BVH) à superfície: negativa do lado de dentro. O lado sai da
 * pseudonormal ponderada pelo ângulo no ponto mais perto (Bærentzen e Aanæs, 2005): quando ele cai numa aresta ou num
 * vértice da malha, a normal de um triângulo só pode apontar para o lado errado (um ponto a 4 cm da arma saía "dentro");
 * todos os triângulos que tocam o ponto mais perto entram, cada um com o ângulo dele ali (π nas arestas, o ângulo
 * interno nos vértices, 1 no meio de uma face).
 */
function distanciaComSinal(bvh, ponto, alvo) {
  const r = bvh.closestPointToPoint(ponto, alvo);
  if (!r) return Infinity;
  const perto = r.point.clone();
  const tol = Math.max(1e-6, r.distance * 1e-4);
  _pn.set(0, 0, 0);
  bvh.shapecast({
    intersectsBounds: (caixa) => caixa.distanceToPoint(perto) <= tol,
    intersectsTriangle: (tri) => {
      tri.closestPointToPoint(perto, _q);
      if (_q.distanceToSquared(perto) > tol * tol) return false;
      _tri.set(tri.a, tri.b, tri.c);
      _tri.getBarycoord(perto, _bar);
      const zeros = [_bar.x, _bar.y, _bar.z].filter((w) => Math.abs(w) < 1e-6).length;
      let peso = 1;
      if (zeros === 2) {
        // num vértice: o ângulo interno do triângulo nele
        if (_bar.x > 0.5) peso = anguloEm(tri.a, tri.b, tri.c);
        else if (_bar.y > 0.5) peso = anguloEm(tri.b, tri.c, tri.a);
        else peso = anguloEm(tri.c, tri.a, tri.b);
      } else if (zeros === 1) {
        peso = Math.PI;
      }
      tri.getNormal(_n);
      _pn.addScaledVector(_n, peso);
      return false;
    },
  });
  if (_pn.lengthSq() === 0) {
    // sem triângulo no ponto (não acontece com a BVH íntegra): o do resultado
    const g = bvh.geometry;
    const i = g.index.array;
    const P = g.attributes.position;
    const f = r.faceIndex * 3;
    _a.fromBufferAttribute(P, i[f]);
    _b.fromBufferAttribute(P, i[f + 1]);
    _c.fromBufferAttribute(P, i[f + 2]);
    _pn.subVectors(_c, _b).cross(_a.sub(_b));
  }
  return _pn.dot(_p.subVectors(ponto, perto)) < 0 ? -r.distance : r.distance;
}

/**
 * O contato de um braço de luva com a arma.
 * @param {{bvh:MeshBVH, raizDaArma:THREE.Object3D, braco:import('./bracoLuva.js').BracoLuva, sondas:object}} o
 *   `sondas` = as do lado do braço nos extras da pega ({contato: {vertice, mm}}); a arma e o braço na mesma cena
 * @returns {{sondas:{contato:string, vertice:number, jogoMM:number, blenderMM:number, diferencaMM:number}[],
 *   penetracaoMM:number, piorDiferencaMM:number}}
 */
export function contatoDasLuvas({ bvh, raizDaArma, braco, sondas }) {
  raizDaArma.updateMatrixWorld(true);
  braco.grupo.updateMatrixWorld(true);
  // do referencial do braço (u) ao da arma
  const m = new THREE.Matrix4().copy(raizDaArma.matrixWorld).invert().multiply(braco.grupo.matrixWorld);
  const pts = braco.posicoesMM;
  const alvo = { point: new THREE.Vector3(), distance: 0, faceIndex: 0 };
  const ponto = new THREE.Vector3();
  const noJogo = (v) => {
    ponto.set(pts[v * 3] / MM_POR_U, pts[v * 3 + 1] / MM_POR_U, pts[v * 3 + 2] / MM_POR_U).applyMatrix4(m);
    return distanciaComSinal(bvh, ponto, alvo) * MM_POR_U;
  };
  const linhas = [];
  let pior = 0;
  for (const [contato, s] of Object.entries(sondas ?? {})) {
    const jogo = noJogo(s.vertice);
    const diferenca = Math.abs(jogo - s.mm);
    pior = Math.max(pior, diferenca);
    linhas.push({ contato, vertice: s.vertice, jogoMM: jogo, blenderMM: s.mm, diferencaMM: diferenca });
  }
  let penetracao = 0;
  for (let v = 0; v < pts.length / 3; v++) penetracao = Math.max(penetracao, -noJogo(v));
  return { sondas: linhas, penetracaoMM: penetracao, piorDiferencaMM: pior };
}
