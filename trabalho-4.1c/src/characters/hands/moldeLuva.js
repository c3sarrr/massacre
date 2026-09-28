// O molde de um braço de luva (Fase 4.1b; desenho em docs/superpowers/specs/2026-09-26-4.1b-luvas-e-empunhadura-
// design.md, seção 7.3; plano, Tarefa 9): o que o luvas.glb carregado pelo GLTFLoader dá para montar os braços — as
// primitivas de cada zona (as geometrias, que o molde guarda e cada braço copia), o modelo das dobras (modeloDobras.js,
// com o esqueleto pelas matrizes de ligação inversas e as correções dos extras) e o esqueleto de repouso (o referencial
// de cada osso no do braço, a raiz `luvas` com a escala do glTF e o `rig_d`/`rig_e`).
// O referencial do braço é o da cena do glTF (u): o pulso na origem, o antebraço em −X, +Y as costas, o polegar em −Z
// na direita e em +Z na esquerda (o espelho do Blender é no eixo do polegar). A malha com skin está nele (a raiz leva a
// escala dos ossos, que estão em metros). O molde confere isso na carga: um .glb com o referencial diferente não monta.

import * as THREE from 'three';
import { OSSOS_DO_BRACO, ossosDoLado } from '../../data/luvas.js';
import { ModeloDobras, dadosDasPrimitivas, normaisDosVertices } from './modeloDobras.js';

const MM_POR_U = 25.4;
const MARCA = /^[0-9a-f]{64}$/;

const _m = new THREE.Matrix4();
const _v = new THREE.Vector3();

function jsonDe(v, oque) {
  if (v === undefined) throw new Error(`luvas: faltam ${oque} nos extras do .glb`);
  try {
    return typeof v === 'string' ? JSON.parse(v) : v;
  } catch (e) {
    throw new Error(`luvas: ${oque} dos extras não são JSON (${e.message})`);
  }
}

/** As malhas com skin de um braço (a do nó `luva_<lado>` ou as filhas dele, uma por zona). */
function malhasDoBraco(no) {
  const out = [];
  no.traverse((o) => o.isSkinnedMesh && out.push(o));
  return out;
}

/**
 * O molde de um braço a partir da cena carregada.
 * @param {THREE.Object3D} cena a `gltf.scene` do luvas.glb
 * @param {'d'|'e'} lado
 * @param {string[]} zonas as zonas esperadas (ZONAS_DAS_LUVAS)
 */
export function moldeDoBraco(cena, lado, zonas) {
  const raiz = cena.getObjectByName('luvas');
  const rig = cena.getObjectByName(`rig_${lado}`);
  const luva = cena.getObjectByName(`luva_${lado}`);
  if (!raiz || !rig || !luva) throw new Error(`luvas: o .glb sem os nós luvas, rig_${lado} e luva_${lado}`);
  const marca = jsonDe(raiz.userData.marca, 'a marca do rig')?.[lado];
  if (!MARCA.test(marca ?? '')) throw new Error(`luvas: sem a marca do rig ${lado} nos extras da raiz`);
  const parametros = jsonDe(luva.userData.correcoes, 'as correções das dobras');
  const malhas = malhasDoBraco(luva);
  if (!malhas.length) throw new Error(`luvas: luva_${lado} sem malha com skin`);
  const skeleton = malhas[0].skeleton;
  for (const m of malhas) if (m.skeleton.bones.some((b, i) => b !== skeleton.bones[i])) throw new Error(`luvas: as zonas de luva_${lado} com esqueletos diferentes`);
  const ossos = skeleton.bones.map((b) => b.name);
  const esperados = ossosDoLado(lado);
  const faltam = esperados.filter((o) => !ossos.includes(o));
  if (faltam.length || ossos.length !== OSSOS_DO_BRACO.length) throw new Error(`luvas: o esqueleto de luva_${lado} sem ${faltam.join(', ') || 'os 20 ossos'}`);
  const pais = skeleton.bones.map((b) => skeleton.bones.indexOf(b.parent));
  const primitivas = malhas.map((m) => {
    const g = m.geometry;
    const zona = m.material?.name;
    if (!zonas.includes(zona)) throw new Error(`luvas: zona desconhecida em luva_${lado}: ${zona}`);
    for (const a of ['position', 'normal', 'tangent', 'uv', 'skinIndex', 'skinWeight', '_vertice']) {
      if (!g.attributes[a]) throw new Error(`luvas: luva_${lado} (${zona}) sem o atributo ${a}`);
    }
    return {
      zona, geometria: g,
      posicoes: g.attributes.position.array, juntas: g.attributes.skinIndex.array, pesos: g.attributes.skinWeight.array,
      vertice: Uint32Array.from(g.attributes._vertice.array, (x) => Math.round(x)), indices: g.index.array,
    };
  });
  const faltaZona = zonas.filter((z) => !primitivas.some((p) => p.zona === z));
  if (faltaZona.length) throw new Error(`luvas: luva_${lado} sem as zonas ${faltaZona.join(', ')}`);
  const malha = dadosDasPrimitivas(primitivas);
  // as cabeças de repouso no referencial da malha (u), pelas matrizes de ligação inversas, em mm
  const cabecas = [];
  for (const inv of skeleton.boneInverses) cabecas.push(..._v.setFromMatrixPosition(_m.copy(inv).invert()).toArray().map((x) => x * MM_POR_U));
  const modelo = new ModeloDobras({ malha, ossos, pais, cabecas, parametros, lado });
  // o esqueleto de repouso no referencial do braço: a raiz e o rig por cima da cadeia dos ossos
  // (os quaternions do arquivo são float32, com a norma a 10⁻⁸ de 1: normalizados, a álgebra dos giros fecha)
  const trs = (o) => ({ posicao: o.position.clone(), quaternion: o.quaternion.clone().normalize(), escala: o.scale.clone() });
  const rRaiz = trs(raiz);
  const rRig = trs(rig);
  const repousoLocal = skeleton.bones.map(trs);
  const base = new THREE.Matrix4().compose(rRaiz.posicao, rRaiz.quaternion, rRaiz.escala)
    .multiply(new THREE.Matrix4().compose(rRig.posicao, rRig.quaternion, rRig.escala));
  const relRepouso = [];
  for (let i = 0; i < ossos.length; i++) {
    const r = repousoLocal[i];
    const local = new THREE.Matrix4().compose(r.posicao, r.quaternion, r.escala);
    relRepouso.push((pais[i] >= 0 ? relRepouso[pais[i]].clone() : base.clone()).multiply(local));
  }
  const iMao = ossos.indexOf(`mao_${lado}`);
  const iAnte = ossos.indexOf(`antebraco_${lado}`);
  const pulso = new THREE.Vector3().setFromMatrixPosition(relRepouso[iMao]);
  const cotovelo = new THREE.Vector3().setFromMatrixPosition(relRepouso[iAnte]);
  const eixo = pulso.clone().sub(cotovelo);
  const comprimento = eixo.length();
  if (eixo.normalize().distanceTo(new THREE.Vector3(1, 0, 0)) > 1e-4) throw new Error(`luvas: o antebraço de ${lado} fora do eixo X (${eixo.toArray()})`);
  const polegar = Math.sign(new THREE.Vector3().setFromMatrixPosition(relRepouso[ossos.indexOf(`polegar_1_${lado}`)]).z);
  if (polegar !== (lado === 'd' ? -1 : 1)) throw new Error(`luvas: o polegar de ${lado} do lado errado do braço`);
  return {
    lado, marca, ossos, pais, modelo, primitivas,
    raiz: rRaiz, rig: rRig, repousoLocal,
    relRepouso,
    relRepousoInv: relRepouso.map((m) => m.clone().invert()),
    quatRepouso: relRepouso.map((m) => new THREE.Quaternion().setFromRotationMatrix(_m.extractRotation(m))),
    normaisRepouso: normaisDosVertices(malha.repouso, malha.triangulos, malha.n),
    pulso, cotovelo, comprimento, polegar,
    triangulos: primitivas.reduce((s, p) => s + p.indices.length / 3, 0),
  };
}

/** Descarta as geometrias do molde (as do .glb carregado; os braços têm as cópias deles). */
export function descartarMolde(molde) {
  for (const p of molde.primitivas) p.geometria.dispose();
}
