// O .glb de uma arma realista no jogo (Fase 4.1a; desenho em docs/superpowers/specs/2026-09-26-armas-realistas-design.md,
// seções 4.2 e 5.2; plano da 4.1a, D2): o resumo da cena que o GLTFLoader devolve — por nível (perto, mundo, longe) as
// peças `<nivel>_<peca>` com as malhas (a zona de cada uma pelo nome do material), os triângulos e a caixa; os
// soquetes; o ponto de descanso e os extras das peças móveis — e a montagem de uma instância: um clone do nível
// (geometrias divididas) com o material de cada zona, as peças móveis com o descanso e o eixo, e as âncoras da 4.1
// (boca, mãos, ejeção…) tiradas dos soquetes, no formato que o viewmodel e a bancada já usam.

import * as THREE from 'three';
import { ANCORA_DO_SOQUETE, LODS_REAIS } from '../../data/armasReais.js';

const _e = new THREE.Euler();

/**
 * Resumo da cena do .glb. Marca as geometrias como compartilhadas e guarda a zona de cada malha em userData.zona (o
 * material do GLTFLoader é trocado logo depois).
 * @param {THREE.Object3D} cena gltf.scene
 * @param {string} id
 */
export function resumirGlb(cena, id) {
  const raiz = cena.getObjectByName(id);
  if (!raiz) throw new Error(`o .glb não tem a raiz ${id}`);
  raiz.updateMatrixWorld(true);
  const lods = {};
  const zonas = new Set();
  for (const lod of LODS_REAIS) {
    const no = raiz.children.find((c) => c.name === lod);
    if (!no) throw new Error(`o .glb de ${id} não tem o nível ${lod}`);
    const pecas = {};
    let triangulos = 0;
    for (const peca of no.children) {
      if (!peca.name.startsWith(`${lod}_`)) throw new Error(`peça ${peca.name} fora do padrão ${lod}_<peça>`);
      pecas[peca.name.slice(lod.length + 1)] = peca;
      peca.userData.rest = peca.position.toArray();
      peca.traverse((o) => {
        if (!o.isMesh) return;
        o.userData.zona = o.userData.zona ?? o.material?.name ?? null;
        if (o.userData.zona) zonas.add(o.userData.zona);
        o.geometry.userData.shared = true;
        triangulos += (o.geometry.index ? o.geometry.index.count : o.geometry.attributes.position.count) / 3;
      });
    }
    lods[lod] = { no, pecas, triangulos };
  }
  const soquetes = {};
  const pasta = raiz.children.find((c) => c.name === 'soquetes');
  for (const s of pasta?.children ?? []) {
    if (!s.name.startsWith('soquete_')) continue;
    _e.setFromQuaternion(s.quaternion, 'XYZ');
    soquetes[s.name.slice('soquete_'.length)] = { pos: s.position.toArray(), rot: [_e.x, _e.y, _e.z] };
  }
  const caixa = new THREE.Box3().setFromObject(lods.perto.no);
  caixa.applyMatrix4(new THREE.Matrix4().copy(raiz.matrixWorld).invert());
  return { raiz, lods, soquetes, caixa: { min: caixa.min.toArray(), max: caixa.max.toArray() }, zonas: [...zonas] };
}

/** Âncoras no formato da 4.1 ({pos, rot}; as das mãos com `pose: null` até as poses da 4.1b) a partir dos soquetes. */
export function ancorasDosSoquetes(soquetes) {
  const out = {};
  for (const [nome, s] of Object.entries(soquetes)) {
    const mao = ANCORA_DO_SOQUETE[nome];
    out[mao ?? nome] = { pos: [...s.pos], rot: [...s.rot], ...(mao ? { pose: null } : {}) };
  }
  return out;
}

/**
 * Instância de um nível: clone da hierarquia (geometrias divididas), cada malha com o material da sua zona.
 * userData.weapon = {id, lod, faction: null, source: 'glb', radius, parts: {peça móvel: Object3D}, anchors}.
 * @param {object} resumo resumirGlb()
 * @param {Object<string, THREE.Material>} materiais por zona
 * @param {Object<string, {pos:number[], rot:number[]}>} ancoras
 */
export function montarInstanciaGlb(resumo, id, lod, materiais, ancoras, raio) {
  const base = resumo.lods[lod];
  const root = new THREE.Group();
  root.name = `arma:${id}`;
  const parts = {};
  for (const [nome, peca] of Object.entries(base.pecas)) {
    const c = peca.clone(true);
    c.userData.rest = [...peca.userData.rest];
    c.userData.axis = peca.userData.eixo ?? null;
    c.userData.hinge = peca.userData.eixo_giro ?? null;
    c.traverse((o) => {
      if (!o.isMesh) return;
      const m = materiais[o.userData.zona];
      if (!m) throw new Error(`${id}: sem material para a zona ${o.userData.zona}`);
      o.material = m;
      o.castShadow = true;
      o.receiveShadow = true;
    });
    root.add(c);
    if (nome !== 'base') parts[nome] = c;
  }
  const anchors = {};
  for (const [nome, a] of Object.entries(ancoras)) {
    const o = new THREE.Object3D();
    o.name = `ancora:${nome}`;
    o.position.fromArray(a.pos);
    o.rotation.fromArray(a.rot);
    root.add(o);
    anchors[nome] = o;
  }
  root.userData.weapon = { id, lod, faction: null, source: 'glb', radius: raio, parts, anchors };
  return root;
}
