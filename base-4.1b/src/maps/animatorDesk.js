// Mesa do animador (Fase 2, vitrine; Fase 4.1, arsenal): tampo de madeira com quatro pernas, tapete de corte A1 (placa
// de PVC com a face impressa) e o chão de molleton do estúdio. Os números vêm de SHOWCASE_SET (src/data/showcase.js).
// Referências: docs/art/moodboard.md item 10 (SMD3: bancada com tapete verde; SSD1/CSD14: ilha de luz no escuro).

import * as THREE from 'three';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';

/**
 * @param {import('../clay/set/index.js').SetLibrary} set
 * @param {{desk:object, mat:object, floorY:number, floorColor:string}} def
 * @returns {THREE.Group} com a face do tapete no topo em y = mat.thickness
 */
export function buildAnimatorDesk(set, { desk, mat, floorY, floorColor }) {
  const root = new THREE.Group();
  root.name = 'mesa-do-animador';
  const wood = set.benchWood();
  const top = new THREE.Mesh(new RoundedBoxGeometry(desk.width, desk.thickness, desk.depth, 3, 4), wood);
  top.position.y = -desk.thickness / 2;
  top.name = 'tampo-bancada';
  const legH = -floorY - desk.thickness;
  const legGeo = new RoundedBoxGeometry(desk.legSize, legH, desk.legSize, 2, 5);
  const legs = [];
  for (const sx of [-1, 1]) {
    for (const sz of [-1, 1]) {
      const leg = new THREE.Mesh(legGeo, wood);
      leg.position.set(sx * (desk.width / 2 - desk.legInset), floorY + legH / 2, sz * (desk.depth / 2 - desk.legInset));
      leg.name = 'perna-bancada';
      legs.push(leg);
    }
  }
  // Tapete: placa fina de PVC (lateral) + face de cima com o material do tapete de corte (uv 0..1).
  const slab = new THREE.Mesh(new THREE.BoxGeometry(mat.width, mat.thickness, mat.depth), set.plastic({ color: '#23553C', moldY: -1e4, name: 'pvc-tapete' }));
  slab.position.set(mat.x, mat.thickness / 2 - 0.05, mat.z);
  const face = new THREE.Mesh(new THREE.PlaneGeometry(mat.width, mat.depth), set.cuttingMat({ size: [mat.width, mat.depth], margin: mat.margin }));
  face.rotation.x = -Math.PI / 2;
  face.position.set(mat.x, mat.thickness, mat.z);
  face.name = 'tapete-de-corte';
  const floor = new THREE.Mesh(new THREE.PlaneGeometry(7000, 7000), set.fabric({ color: floorColor, name: 'molleton-chao' }));
  floor.rotation.x = -Math.PI / 2;
  floor.position.y = floorY;
  floor.name = 'chao-estudio';
  for (const m of [top, ...legs, slab, face, floor]) {
    m.castShadow = m !== floor && m !== face;
    m.receiveShadow = true;
    root.add(m);
  }
  return root;
}
