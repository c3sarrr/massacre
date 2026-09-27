// Suporte de arame da bancada `arsenal` (Fase 4.1a): a forma da arma medida por raios na malha da instância — a caixa,
// a parte de baixo em cada x e a meia largura numa altura —, a mesma conta para a arma realista (.glb) e a de massinha;
// os garfos do suporte encostam por baixo dela e a arma fica acima da tira de compensado.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import * as THREE from 'three';
import { ARSENAL } from '../src/data/arsenal.js';
import { buildWireStand, formaDaArma } from '../src/maps/arsenal/turntable.js';

const near = (a, b, eps, msg) => assert.ok(Math.abs(a - b) <= eps, `${msg}: ${a} ≠ ${b}`);

/** Uma "arma" de caixas: corpo de 20 × 2 × 1,6 u e, como peça móvel, um carregador de 2 × 4 × 1,2 u embaixo. */
function armaDeTeste() {
  const root = new THREE.Group();
  const corpo = new THREE.Mesh(new THREE.BoxGeometry(20, 2, 1.6), new THREE.MeshBasicMaterial());
  const carregador = new THREE.Group();
  carregador.position.set(4, -1, 0);
  const pente = new THREE.Mesh(new THREE.BoxGeometry(2, 4, 1.2), new THREE.MeshBasicMaterial());
  pente.position.set(0, -2, 0);
  carregador.add(pente);
  root.add(corpo, carregador);
  root.userData.weapon = { id: 'teste' };
  return root;
}

test('suporte: a forma da arma por raios na malha (caixa, parte de baixo e meia largura)', () => {
  const f = formaDaArma(armaDeTeste());
  near(f.box.min[0], -10, 1e-9, 'x mínimo');
  near(f.box.max[0], 10, 1e-9, 'x máximo');
  near(f.box.min[1], -5, 1e-9, 'y mínimo: o pé do carregador');
  near(f.underside(-8), -1, 1e-6, 'debaixo do corpo');
  near(f.underside(4), -5, 1e-6, 'debaixo do carregador');
  assert.equal(f.underside(15), null, 'fora da arma');
  near(f.halfWidth(-8, -0.65), 0.8, 1e-6, 'meia largura do corpo');
  near(f.halfWidth(4, -3), 0.6, 1e-6, 'meia largura do carregador');
});

test('suporte: os garfos encostam por baixo da arma e a arma fica acima da tira', () => {
  const set = { plywood: () => new THREE.MeshBasicMaterial(), wire: () => new THREE.MeshBasicMaterial() };
  const { group, weaponOffset } = buildWireStand(set, ARSENAL.stand, armaDeTeste());
  assert.equal(group.name, 'suporte-teste');
  near(weaponOffset.x, 0, 1e-9, 'centrada em x');
  assert.ok(weaponOffset.y - 5 > ARSENAL.stand.base.thickness, 'o pé do carregador livre da tira');
  const arame = group.getObjectByName('suporte-arame');
  arame.geometry.computeBoundingBox();
  assert.ok(arame.geometry.boundingBox.max.y > weaponOffset.y - 1, 'os garfos sobem até a parte de baixo do corpo');
});
