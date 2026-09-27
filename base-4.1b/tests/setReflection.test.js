// Reflexo do set das armas realistas (Fase 4.1a; desenho, seção 5.4): o ponto de cada mapa — o `reflection` montado dos
// dados, no centro da área jogável e na altura do olho, ou o spawn — e os pontos dos três mapas dentro da área jogável,
// longe das paredes e das peças. A captura (PMREM de uma câmera cúbica) precisa da GPU e é conferida no navegador
// (Tarefa 18).
import { test } from 'node:test';
import assert from 'node:assert/strict';
import * as THREE from 'three';
import { ARSENAL } from '../src/data/arsenal.js';
import { REFLEXO } from '../src/data/armasReais.js';
import { HULL } from '../src/data/movement.js';
import { PISTA } from '../src/data/pista.js';
import { TEST_ROOM } from '../src/data/sandbox.js';
import { pontoDoReflexo } from '../src/render/setReflection.js';

test('reflexo do set: o ponto do mapa, ou o olho no spawn', () => {
  const r = new THREE.Vector3(1, 2, 3);
  const spawn = { position: new THREE.Vector3(10, 0, 20) };
  const p = pontoDoReflexo({ reflection: r, spawn, collision: {} });
  assert.deepEqual(p.toArray(), [1, 2, 3]);
  assert.notEqual(p, r, 'uma cópia: quem chama pode mexer');
  assert.deepEqual(pontoDoReflexo({ spawn, collision: {} }).toArray(), [10, HULL.standEye, 20], 'mapa de andar: o spawn é o pé');
  assert.deepEqual(pontoDoReflexo({ spawn, collision: null }).toArray(), [10, 0, 20], 'câmera livre: o spawn já é o olho');
  assert.deepEqual([REFLEXO.tamanho, REFLEXO.intensidade], [256, 1]);
});

test('reflexo do set: os pontos dos mapas no centro da área jogável, longe das paredes e das peças', () => {
  const T = TEST_ROOM;
  assert.ok(Math.abs(T.reflexo.x) <= T.width / 4 && Math.abs(T.reflexo.z) <= T.depth / 4, 'sala: no meio');
  assert.ok(HULL.standEye < T.height / 2, 'o olho bem abaixo do teto');
  const B = PISTA.base;
  assert.ok(Math.abs(PISTA.reflexo.x - (B.minX + B.maxX) / 2) <= 200 && Math.abs(PISTA.reflexo.z - (B.minZ + B.maxZ) / 2) <= 200,
    'pista: no meio do compensado');
  const S = PISTA.strafe.paper;
  assert.ok(PISTA.reflexo.x > S.x[0] && PISTA.reflexo.x < S.x[1] && PISTA.reflexo.z > S.z[0] && PISTA.reflexo.z < S.z[1],
    'pista: na quadra de strafe, aberta');
  for (const p of PISTA.strafe.pillars) assert.ok(Math.hypot(p.at[0] - PISTA.reflexo.x, p.at[1] - PISTA.reflexo.z) > 200, 'longe dos pilares');
  assert.deepEqual([ARSENAL.reflexo.x, ARSENAL.reflexo.z], [ARSENAL.hold.x, ARSENAL.hold.z], 'bancada: o olho do "Segurar"');
  const y = ARSENAL.desk.mat.thickness + HULL.standEye;
  assert.ok(y > ARSENAL.bounds.min[1] && y < ARSENAL.bounds.max[1]);
});
