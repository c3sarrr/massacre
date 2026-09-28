// Braço de massinha com a mão de 4 dedos e o rig (Fase 4.1; docs/phases/phase-4.md, seção 4.1, "Mãos de 4 dedos"):
// a malha SDF da mão direita em repouso (src/characters/hands/handShape.js) vira uma SkinnedMesh de 14 ossos com os pesos
// de handSkin.js; a esquerda é a direita espelhada em Z (malha, ossos e giros). O boil do ClayMaterial age na pose de
// repouso (antes do skinning) e as digitais ficam no espaço do objeto em repouso: a massa dobra com o dedo e as marcas
// vão junto. A braçadeira do time é uma faixa de massa presa ao osso do antebraço (seção 0.12).
// As geometrias (com os pesos) são preparadas uma vez por lado e divididas entre os braços (HandLibrary); cada braço tem
// o seu esqueleto e os seus materiais. A pose muda só na troca de pose (12/s, "em dois"); quem chama decide quando.

import * as THREE from 'three';
import { ClayMaterial } from '../../clay/ClayMaterial.js';
import { ARMBAND, HAND } from '../../data/hands.js';
import { WRIST, boneBasis, forearmRadius, handBones, handTree } from './handShape.js';
import { computeSkinWeights, mirrorRotations, poseRotations } from './handSkin.js';

const MIRROR = new THREE.Matrix4().makeScale(1, 1, -1);

/** Malha da mão direita em repouso (Workers e cache do SdfMesher). Quem recebe é dono. */
export function buildArmGeometry(sdf) {
  const tree = handTree();
  const extent = HAND.forearm.length + HAND.palm.half[0] * 2 + 4.5;
  return sdf.build(tree, {
    resolution: Math.min(1024, Math.ceil(extent / HAND.mesh.cell)), maxCells: HAND.mesh.maxCells, touchRadius: HAND.mesh.touchRadius,
  });
}

/** Faixa da braçadeira em volta do antebraço (anel torneado), no referencial do modelo. */
export function armbandTree() {
  const L = HAND.forearm.length;
  const x0 = ARMBAND.at * L - ARMBAND.width / 2;
  const x1 = x0 + ARMBAND.width;
  const r0 = forearmRadius(x0) - 0.12;
  const r1 = forearmRadius(x1) - 0.12;
  return {
    type: 'lathe', mat: 0, closed: true, corner: ARMBAND.round,
    points: [[x0, r0], [x1, r1], [x1, r1 + ARMBAND.thickness + 0.12], [x0, r0 + ARMBAND.thickness + 0.12]],
  };
}

/** Malha da braçadeira (Workers e cache do SdfMesher), no referencial do antebraço. Quem recebe é dono. */
export function buildArmbandGeometry(sdf) {
  const extent = 2 * (HAND.forearm.elbowRadius + ARMBAND.thickness + 0.5);
  return sdf.build(armbandTree(), {
    resolution: Math.min(512, Math.ceil(extent / ARMBAND.mesh.cell)), maxCells: ARMBAND.mesh.maxCells,
    touchRadius: ARMBAND.mesh.touchRadius,
  });
}

/** Cópia espelhada em Z (esquerda): posições e normais trocam o sinal de z e os triângulos invertem o sentido. */
export function mirrorGeometry(source) {
  const g = source.clone();
  for (const name of ['position', 'normal']) {
    const a = g.attributes[name];
    for (let i = 0; i < a.count; i++) a.setZ(i, -a.getZ(i));
    a.needsUpdate = true;
  }
  const idx = g.index;
  for (let i = 0; i < idx.count; i += 3) {
    const b = idx.getX(i + 1);
    idx.setX(i + 1, idx.getX(i + 2));
    idx.setX(i + 2, b);
  }
  idx.needsUpdate = true;
  g.computeBoundingBox();
  g.computeBoundingSphere();
  return g;
}

function mirrorBone(b) {
  const m = (p) => [p[0], p[1], -p[2]];
  return { ...b, head: m(b.head), tail: m(b.tail), dir: m(b.dir) };
}

/** Ossos de um lado (a esquerda é a direita espelhada em Z). */
export function sideBones(side) {
  const defs = handBones();
  return side === 'esquerda' ? defs.map(mirrorBone) : defs;
}

/**
 * Geometria de um lado pronta para o skinning: a direita copiada, a esquerda espelhada, com `skinIndex`/`skinWeight`.
 * A fonte continua de quem a deu; quem recebe é dono da nova.
 * @param {THREE.BufferGeometry} source a mão direita em repouso (buildArmGeometry)
 * @param {'direita'|'esquerda'} side
 */
export function prepareArmGeometry(source, side) {
  const geo = side === 'esquerda' ? mirrorGeometry(source) : source.clone();
  const { skinIndex, skinWeight } = computeSkinWeights(geo.attributes.position.array, sideBones(side));
  geo.setAttribute('skinIndex', new THREE.Uint16BufferAttribute(skinIndex, 4));
  geo.setAttribute('skinWeight', new THREE.Float32BufferAttribute(skinWeight, 4));
  geo.name = `braco:${side}`;
  return geo;
}

/** A braçadeira de um lado (a esquerda espelhada). Quem recebe é dono. */
export function prepareArmbandGeometry(source, side) {
  const geo = side === 'esquerda' ? mirrorGeometry(source) : source.clone();
  geo.name = `bracadeira:${side}`;
  return geo;
}

function restMatrix(bone, left) {
  const { x, y, z } = boneBasis(bone.dir);
  const m = new THREE.Matrix4().makeBasis(new THREE.Vector3(...x), new THREE.Vector3(...y), new THREE.Vector3(...z));
  m.setPosition(bone.head[0], bone.head[1], bone.head[2]);
  return left ? MIRROR.clone().multiply(m).multiply(MIRROR) : m;
}

const _q = new THREE.Quaternion();
const _e = new THREE.Euler(0, 0, 0, 'YZX');
const _m = new THREE.Matrix4();
const _v = new THREE.Vector3();
const _x = new THREE.Vector3();
const _y = new THREE.Vector3();
const _z = new THREE.Vector3();

export class ClayArm {
  /**
   * @param {{geometry:THREE.BufferGeometry, armband?:THREE.BufferGeometry|null, side:'direita'|'esquerda', color:string}} opts
   *   `geometry`: a do lado já preparada (prepareArmGeometry); `armband`: a braçadeira do lado. As duas continuam de
   *   quem as deu (a HandLibrary divide entre os braços); o braço é dono só do esqueleto e dos materiais.
   */
  constructor({ geometry, armband = null, side, color }) {
    if (!geometry.attributes.skinIndex) throw new Error('ClayArm: a geometria precisa dos pesos (prepareArmGeometry)');
    this.side = side;
    const left = side === 'esquerda';
    this.left = left;
    const C = HAND.clay;
    this.material = new ClayMaterial({ color, roughness: C.roughness, wetness: C.wetness, touched: true, seed: `mao-${side}` });
    this.material.setObjectSize(C.objectSize);
    // Ossos: matriz de repouso de cada um no referencial do modelo; a local é a do pai invertida vezes a sua.
    this.bones = {};
    this.rest = {};
    const worlds = {};
    const list = [];
    for (const def of handBones()) {
      const bone = new THREE.Bone();
      bone.name = def.name;
      const world = restMatrix(def, left);
      worlds[def.name] = world;
      const local = def.parent ? _m.copy(worlds[def.parent]).invert().multiply(world) : world.clone();
      local.decompose(bone.position, bone.quaternion, bone.scale);
      this.rest[def.name] = bone.quaternion.clone();
      if (def.parent) this.bones[def.parent].add(bone);
      this.bones[def.name] = bone;
      list.push(bone);
    }
    this.mesh = new THREE.SkinnedMesh(geometry, this.material);
    this.mesh.name = `braco-${side}`;
    this.mesh.frustumCulled = false; // os ossos saem de perto da caixa de repouso
    this.mesh.castShadow = true;
    this.mesh.receiveShadow = true;
    this.mesh.add(this.bones.antebraco);
    this.mesh.updateMatrixWorld(true);
    this.skeleton = new THREE.Skeleton(list);
    this.mesh.bind(this.skeleton);
    // Braçadeira: presa ao osso do antebraço (rígida), escondida sem time.
    this.armbandMaterial = null;
    this.armband = null;
    if (armband) {
      const B = ARMBAND.clay;
      this.armbandMaterial = new ClayMaterial({ color, roughness: B.roughness, wetness: B.wetness, touched: true, seed: `bracadeira-${side}` });
      this.armbandMaterial.setObjectSize(B.objectSize);
      this.armband = new THREE.Mesh(armband, this.armbandMaterial);
      this.armband.name = `bracadeira-${side}`;
      this.armband.visible = false;
      this.armband.castShadow = true;
      this.armband.receiveShadow = true;
      this.bones.antebraco.add(this.armband);
    }
    this.pose = null;
    this.wristPose = null;
  }

  /** Aplica uma pose de mão (nome em HAND_POSES ou objeto): giro de repouso × giro da pose em cada osso. */
  setPose(pose) {
    const rot = poseRotations(pose);
    const r = this.left ? mirrorRotations(rot) : rot;
    for (const [name, [x, y, z]] of Object.entries(r)) {
      if (name === 'antebraco') continue;
      _e.set(x, y, z, 'YZX');
      this.bones[name].quaternion.copy(this.rest[name]).multiply(_q.setFromEuler(_e));
    }
    this.pose = pose;
    this.wristPose = r.mao;
  }

  /** Cor da massa do braço (a do boneco). */
  setColor(color) {
    this.material.color.set(color);
  }

  /** Braçadeira do time: cor (hex) ou null para esconder. */
  setArmband(color) {
    if (!this.armband) return;
    this.armband.visible = Boolean(color);
    if (color) this.armbandMaterial.color.set(color);
  }

  /**
   * Põe a mão numa âncora: o pulso na posição e na rotação dadas (no espaço do pai da malha) e o antebraço apontando para
   * o cotovelo, com o comprimento do antebraço (o cotovelo real fica no alinhamento, a `forearm.length` do pulso). O giro
   * do antebraço acompanha o da mão (o +Y do antebraço é o +Y da mão, sem a componente ao longo do braço).
   * @param {THREE.Vector3} wrist @param {THREE.Quaternion} handQuat @param {THREE.Vector3} elbowTarget
   */
  place(wrist, handQuat, elbowTarget) {
    const L = HAND.forearm.length;
    _x.subVectors(wrist, elbowTarget).normalize();
    _y.set(0, 1, 0).applyQuaternion(handQuat);
    _y.addScaledVector(_x, -_y.dot(_x));
    if (_y.lengthSq() < 1e-6) _y.set(0, 1, 0).addScaledVector(_x, -_x.y);
    _y.normalize();
    _z.crossVectors(_x, _y);
    _m.makeBasis(_x, _y, _z);
    const forearm = this.bones.antebraco;
    forearm.quaternion.setFromRotationMatrix(_m);
    forearm.position.copy(_v.copy(wrist).addScaledVector(_x, -L));
    // A mão: rotação da âncora no referencial do antebraço, com o pulso da pose por cima.
    const hand = this.bones.mao;
    hand.quaternion.copy(forearm.quaternion).invert().multiply(handQuat);
    if (this.wristPose) {
      const [x, y, z] = this.wristPose;
      hand.quaternion.multiply(_q.setFromEuler(_e.set(x, y, z, 'YZX')));
    }
    hand.position.set(L, 0, 0);
  }

  /** Posição do pulso e do cotovelo (espaço do pai da malha), para os testes e o painel. */
  joints(outWrist, outElbow) {
    const f = this.bones.antebraco;
    outElbow.copy(f.position);
    outWrist.set(HAND.forearm.length, 0, 0).applyQuaternion(f.quaternion).add(f.position);
  }

  dispose() {
    this.mesh.removeFromParent();
    this.material.dispose();
    this.armbandMaterial?.dispose();
    this.skeleton.dispose();
  }
}

/** Pulso no referencial do modelo (para quem precisa do comprimento do antebraço). */
export const ARM_WRIST = WRIST;
