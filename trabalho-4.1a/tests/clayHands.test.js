// Testes das mãos de massinha de 4 dedos (Fase 4.1; docs/phases/phase-4.md, seção 4.1, "Mãos de 4 dedos" e "Testes"):
// o esqueleto de 14 ossos, os pesos do skinning (normalizados, no máximo 4, cada vértice dos dedos puxado pelo seu
// osso e nenhum dedo arrastando o vizinho), as poses dentro dos limites das juntas, o espelho da esquerda (malha,
// pesos e giros), o braço posto numa âncora (pulso no lugar, antebraço apontando para o cotovelo) e a cor da braçadeira.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import * as THREE from 'three';
import { bounds, compile } from '../src/clay/sdf/nodes.js';
import { polygonize } from '../src/clay/sdf/marchingCubes.js';
import { meshToGeometry } from '../src/clay/sdf/sdfMesher.js';
import { ARMBAND, HAND, HAND_LIMITS, HAND_POSES } from '../src/data/hands.js';
import { PALETTE, TEAM_COLORS } from '../src/data/palette.js';
import { handBones, handTree, WRIST } from '../src/characters/hands/handShape.js';
import { computeSkinWeights, mirrorRotations, poseRotations } from '../src/characters/hands/handSkin.js';
import { ClayArm, mirrorGeometry, prepareArmGeometry } from '../src/characters/hands/handRig.js';
import { armbandColor, deltaE, hexToLab } from '../src/characters/hands/armband.js';
import { meshReport } from './sdfTestUtils.js';

// Malha da mão numa grade mais grossa que a do jogo (os pesos não dependem da resolução; o teste fica rápido).
const tree = handTree();
const data = polygonize(compile(tree), bounds(tree), { resolution: 90 });
const source = meshToGeometry(data, 'mao-teste');

function segmentT(p, h, t) {
  const d = [t[0] - h[0], t[1] - h[1], t[2] - h[2]];
  const l2 = d[0] ** 2 + d[1] ** 2 + d[2] ** 2;
  return ((p[0] - h[0]) * d[0] + (p[1] - h[1]) * d[1] + (p[2] - h[2]) * d[2]) / l2;
}
function segmentDist(p, h, t) {
  const s = Math.max(0, Math.min(1, segmentT(p, h, t)));
  return Math.hypot(p[0] - h[0] - s * (t[0] - h[0]), p[1] - h[1] - s * (t[1] - h[1]), p[2] - h[2] - s * (t[2] - h[2]));
}

test('mãos: 14 ossos em ordem, cadeias certas e falanges emendadas', () => {
  const bones = handBones();
  assert.equal(bones.length, 14);
  const seen = new Set();
  for (const b of bones) {
    if (b.parent) assert.ok(seen.has(b.parent), `${b.name}: o pai ${b.parent} vem antes`);
    seen.add(b.name);
  }
  assert.deepEqual([...new Set(bones.map((b) => b.chain))].sort(), ['braco', 'dedo1', 'dedo2', 'dedo3', 'polegar']);
  assert.deepEqual(bones[0].tail, [...WRIST], 'o antebraço termina no pulso');
  for (const b of bones) {
    const parent = bones.find((x) => x.name === b.parent);
    if (parent && parent.chain === b.chain && b.chain !== 'braco') assert.deepEqual(b.head, parent.tail, `${b.name} emenda no pai`);
  }
  // A mão fica com ~7 u do pulso à ponta do dedo do meio (a medida da empunhadura da Glock).
  const tip = bones.find((b) => b.name === 'dedo2_3').tail;
  assert.ok(Math.abs(tip[0] - WRIST[0] - 7) < 0.8, `mão de ${(tip[0] - WRIST[0]).toFixed(2)} u`);
});

test('mãos: a malha da mão é fechada e tem o tamanho do desenho', () => {
  const rep = meshReport(data);
  assert.equal(rep.open, 0, 'estanque');
  assert.equal(rep.badWinding, 0, 'enrolamento de fora');
  const box = new THREE.Box3().setFromBufferAttribute(source.attributes.position);
  assert.ok(box.min.x < 0.5 - HAND.forearm.elbowRadius + 0.3, 'começa no cotovelo');
  assert.ok(box.max.x > WRIST[0] + 6, 'vai até a ponta dos dedos');
});

test('mãos: pesos normalizados, no máximo 4 ossos, cada dedo puxado pelos seus ossos', () => {
  const bones = handBones();
  const P = source.attributes.position.array;
  const { skinIndex, skinWeight } = computeSkinWeights(P, bones);
  const n = P.length / 3;
  let fingerChecked = 0;
  for (let v = 0; v < n; v++) {
    let sum = 0;
    for (let k = 0; k < 4; k++) {
      const w = skinWeight[v * 4 + k];
      assert.ok(w >= 0 && w <= 1 + 1e-6);
      assert.ok(skinIndex[v * 4 + k] < bones.length);
      sum += w;
    }
    assert.ok(Math.abs(sum - 1) < 1e-5, `vértice ${v}: soma ${sum}`);
    // Vértices no meio de uma falange (bem longe das outras cadeias): o maior peso é dessa falange, e nenhum osso de
    // outro dedo puxa o vértice.
    const p = [P[v * 3], P[v * 3 + 1], P[v * 3 + 2]];
    for (const b of bones) {
      if (b.chain === 'braco' || !/_[23]$/.test(b.name)) continue;
      const t = segmentT(p, b.head, b.tail);
      if (t < 0.3 || t > 0.7 || segmentDist(p, b.head, b.tail) > b.radius + 0.12) continue;
      const others = bones.filter((o) => o.chain !== b.chain && o.chain !== 'braco');
      if (others.some((o) => segmentDist(p, o.head, o.tail) < o.radius + 0.4)) continue;
      let best = -1;
      let bw = -1;
      for (let k = 0; k < 4; k++) {
        if (skinWeight[v * 4 + k] > bw) {
          bw = skinWeight[v * 4 + k];
          best = skinIndex[v * 4 + k];
        }
        const chain = bones[skinIndex[v * 4 + k]].chain;
        if (skinWeight[v * 4 + k] > 0) assert.ok(chain === b.chain || chain === 'braco', `vértice ${v}: ${b.chain} puxado por ${chain}`);
      }
      assert.equal(bones[best].name, b.name, `vértice ${v} no meio de ${b.name}`);
      fingerChecked++;
    }
  }
  assert.ok(fingerChecked > 50, `vértices de falange conferidos: ${fingerChecked}`);
});

test('mãos: as poses ficam dentro dos limites das juntas', () => {
  const inRange = (v, [lo, hi], what) => assert.ok(v >= lo - 1e-9 && v <= hi + 1e-9, `${what}: ${v} fora de [${lo}, ${hi}]`);
  for (const [name, pose] of Object.entries(HAND_POSES)) {
    const r = poseRotations(name);
    assert.equal(Object.keys(r).length, 14, name);
    for (const f of HAND.fingers) {
      for (let i = 1; i <= 3; i++) inRange(-r[`${f.id}_${i}`][2], HAND_LIMITS.flex, `${name}.${f.id}_${i}`);
      inRange(r[`${f.id}_1`][1], HAND_LIMITS.spread, `${name}.${f.id} abertura`);
    }
    inRange(-r.polegar_1[1], HAND_LIMITS.thumbYaw, `${name}.polegar giro`);
    inRange(r.mao[1], HAND_LIMITS.wrist, `${name}.pulso desvio`);
    inRange(-r.mao[2], HAND_LIMITS.wrist, `${name}.pulso flexão`);
    // A pose fechada dobra mais que a aberta (empunhadura e faca fecham os dedos).
    if (name === 'faca') assert.ok(pose.fingers.every((f) => f[0] > HAND_POSES.aberta.fingers[0][0]));
  }
  // Fora do limite é preso ao limite.
  const wild = { ...HAND_POSES.aberta, fingers: [[9, 9, 9], [9, 9, 9], [9, 9, 9]] };
  assert.equal(poseRotations(wild).dedo1_1[2], -HAND_LIMITS.flex[1]);
  assert.throws(() => poseRotations('pose-que-nao-existe'), /pose de mão desconhecida/);
});

test('mãos: a esquerda é a direita espelhada (malha, pesos e giros)', () => {
  const right = prepareArmGeometry(source, 'direita');
  const left = prepareArmGeometry(source, 'esquerda');
  const pr = right.attributes.position;
  const pl = left.attributes.position;
  assert.equal(pr.count, pl.count);
  for (let i = 0; i < pr.count; i += 7) {
    assert.equal(pl.getX(i), pr.getX(i));
    assert.equal(pl.getY(i), pr.getY(i));
    assert.equal(pl.getZ(i), -pr.getZ(i));
    assert.equal(left.attributes.normal.getZ(i), -right.attributes.normal.getZ(i));
  }
  // Os pesos acompanham o espelho: o mesmo vértice, o mesmo osso.
  for (let i = 0; i < pr.count * 4; i += 13) {
    assert.equal(left.attributes.skinIndex.array[i], right.attributes.skinIndex.array[i]);
    assert.ok(Math.abs(left.attributes.skinWeight.array[i] - right.attributes.skinWeight.array[i]) < 1e-6);
  }
  // O espelho inverte o enrolamento (a malha continua virada para fora).
  const mirrored = { positions: mirrorGeometry(source).attributes.position.array, normals: mirrorGeometry(source).attributes.normal.array, indices: mirrorGeometry(source).index.array };
  assert.equal(meshReport(mirrored).badWinding, 0);
  const rot = poseRotations('empunhadura');
  const m = mirrorRotations(rot);
  for (const k of Object.keys(rot)) assert.deepEqual(m[k], [-rot[k][0], -rot[k][1], rot[k][2]]);
});

test('mãos: o braço vai para a âncora — pulso no lugar, antebraço apontando para o cotovelo, dedos fechando', () => {
  const geometry = prepareArmGeometry(source, 'direita');
  const arm = new ClayArm({ geometry, side: 'direita', color: PALETTE.terracotta });
  const tip = () => {
    arm.mesh.updateMatrixWorld(true);
    return new THREE.Vector3(HAND.fingers[1].phalanges[2], 0, 0).applyMatrix4(arm.bones.dedo2_3.matrixWorld);
  };
  const middleKnuckle = () => {
    arm.mesh.updateMatrixWorld(true);
    return new THREE.Vector3().setFromMatrixPosition(arm.bones.dedo2_2.matrixWorld);
  };
  arm.setPose('aberta');
  const wrist = new THREE.Vector3(5, -4, -12);
  const handQuat = new THREE.Quaternion().setFromEuler(new THREE.Euler(0.4, -0.3, 0.2));
  const elbow = new THREE.Vector3(15, -18, 6);
  arm.place(wrist, handQuat, elbow);
  arm.mesh.updateMatrixWorld(true);
  const w = new THREE.Vector3();
  const e = new THREE.Vector3();
  arm.joints(w, e);
  assert.ok(w.distanceTo(wrist) < 1e-9, 'pulso na âncora');
  assert.ok(Math.abs(w.distanceTo(e) - HAND.forearm.length) < 1e-9, 'antebraço com o comprimento');
  const toElbow = elbow.clone().sub(wrist).normalize();
  assert.ok(e.clone().sub(w).normalize().dot(toElbow) > 1 - 1e-9, 'antebraço na direção do cotovelo');
  const handWorld = new THREE.Vector3().setFromMatrixPosition(arm.bones.mao.matrixWorld);
  assert.ok(handWorld.distanceTo(wrist) < 1e-9, 'o osso da mão começa no pulso');
  // A mão fica na rotação da âncora (com a pose de pulso "aberta", que é neutra).
  const q = new THREE.Quaternion().setFromRotationMatrix(arm.bones.mao.matrixWorld);
  assert.ok(Math.abs(Math.abs(q.dot(handQuat)) - 1) < 1e-9, 'rotação da âncora');
  // Fechar a mão: o nó do meio desce para o lado da palma (−Y da mão), a ponta volta para perto do pulso e fica do
  // lado da palma.
  const open = tip();
  const openKnuckle = middleKnuckle();
  arm.setPose('faca');
  arm.place(wrist, handQuat, elbow);
  const fist = tip();
  const palmDown = new THREE.Vector3(0, -1, 0).applyQuaternion(handQuat);
  assert.ok(middleKnuckle().sub(openKnuckle).dot(palmDown) > 0.8, 'o nó do meio desce para a palma');
  assert.ok(fist.distanceTo(wrist) < open.distanceTo(wrist) - 3, 'a ponta volta para perto do pulso');
  assert.ok(fist.clone().sub(wrist).dot(palmDown) > 0, 'e fica do lado da palma');
  arm.setArmband(null);
  arm.dispose();
  geometry.dispose();
});

test('braçadeira: a cor do time que mais se destaca da massa do braço', () => {
  assert.equal(deltaE('#C8553D', '#C8553D'), 0);
  assert.ok(Math.abs(deltaE('#C8553D', '#2F6DB5') - deltaE('#2F6DB5', '#C8553D')) < 1e-12);
  const [L] = hexToLab('#FFFFFF');
  assert.ok(Math.abs(L - 100) < 1e-3, 'branco tem L* 100');
  // Braço terracota (o boneco de referência): a braçadeira TR não pode ser terracota; a CT é o azul.
  assert.equal(armbandColor('tr', PALETTE.terracotta), TEAM_COLORS.tr.secondary);
  assert.equal(armbandColor('ct', PALETTE.terracotta), TEAM_COLORS.ct.primary);
  // Braço azul (um boneco da Tropa do Estúdio): a CT troca para a segunda cor.
  assert.equal(armbandColor('ct', PALETTE.blue), TEAM_COLORS.ct.secondary);
  assert.equal(armbandColor(null, PALETTE.terracotta), null);
  for (const team of ['tr', 'ct']) {
    for (const arm of [PALETTE.terracotta, PALETTE.blue, PALETTE.clayWhite, '#6B4F3A']) {
      assert.ok(deltaE(armbandColor(team, arm), arm) >= ARMBAND.minDelta, `${team} em ${arm}`);
    }
  }
});
