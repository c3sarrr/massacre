// Roda de modelar e suporte de arame da bancada `arsenal` (Fase 4.1; QTT11 — a roda de escultor de metal; QTT9 —
// giratória de produto; QWS9, QWS12, QWS14 — suportes de arame em garfo, no item 13 do moodboard).
// A roda: pé pesado torneado, coluna e prato com anéis de centragem, tudo em metal de ferramenta com restos de massa.
// O suporte: tira de compensado no prato e dois garfos de arame; cada garfo sobe até encostar na parte de baixo da arma
// naquele ponto (medida no SDF da receita), então qualquer arma deita certinho nele.

import * as THREE from 'three';
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';
import { wireGeometry } from '../../clay/set/propGeometry.js';
import { bounds, compile } from '../../clay/sdf/nodes.js';
import { recipeWholeTree } from '../../weapons/model/recipe.js';

// Torno em volta de Y a partir de pares [raio, altura].
function latheY(profile, segments = 48) {
  return new THREE.LatheGeometry(profile.map(([r, y]) => new THREE.Vector2(Math.max(r, 0.001), y)), segments);
}

/**
 * Roda de modelar. O `spinner` é o grupo que gira (em cima do prato, y = 0 na face do prato).
 * @param {import('../../clay/set/index.js').SetLibrary} set
 * @param {object} def ARSENAL.turntable
 * @returns {{root:THREE.Group, spinner:THREE.Group, top:number}}
 */
export function buildBandingWheel(set, def) {
  const { foot, column, plate } = def;
  const root = new THREE.Group();
  root.name = 'roda-de-modelar';
  const metal = set.toolMetal({ color: '#9FA5AB', residueFrom: 0.62, length: plate.radius * 2, name: 'roda-aluminio' });
  const dark = set.toolMetal({ color: '#6F757B', residueFrom: 2, length: foot.radius * 2, name: 'roda-ferro' });
  // Pé: disco pesado com o chanfro de fundição e o degrau onde a coluna entra.
  const footGeo = latheY([
    [0, 0], [foot.radius - 1.2, 0], [foot.radius, 0.8], [foot.radius, foot.height - 1.6], [foot.radius - 2.4, foot.height],
    [column.radius + 3.2, foot.height + 0.6], [column.radius + 2.2, foot.height + 2.4], [0, foot.height + 2.4],
  ]);
  const columnTop = foot.height + column.height;
  const colGeo = latheY([
    [0, foot.height], [column.radius, foot.height], [column.radius, columnTop - 3], [column.radius + 1.6, columnTop - 2.2],
    [column.radius + 1.6, columnTop], [0, columnTop],
  ], 32);
  // Prato: face de cima com os anéis de centragem torneados (sulcos rasos), aba e o cubo de baixo.
  const profile = [[0, columnTop], [column.radius + 3, columnTop], [plate.radius - 3, columnTop + 0.8], [plate.radius, columnTop + 1.4],
    [plate.radius, columnTop + plate.height - 0.8], [plate.radius - 0.8, columnTop + plate.height]];
  const top = columnTop + plate.height;
  for (let i = plate.rings; i >= 1; i--) {
    const r = (plate.radius - 4) * (i / (plate.rings + 0.5));
    profile.push([r + 0.5, top], [r + 0.25, top - plate.ringDepth], [r - 0.25, top - plate.ringDepth], [r - 0.5, top]);
  }
  profile.push([0, top]);
  const plateGeo = latheY(profile, 64);
  const parts = [
    ['pe', footGeo, dark], ['coluna', colGeo, metal], ['prato', plateGeo, metal],
  ];
  for (const [name, geo, mat] of parts) {
    const mesh = new THREE.Mesh(geo, mat);
    mesh.name = `roda-${name}`;
    mesh.castShadow = true;
    mesh.receiveShadow = true;
    root.add(mesh);
  }
  const spinner = new THREE.Group();
  spinner.name = 'roda-giratorio';
  spinner.position.y = top;
  root.add(spinner);
  return { root, spinner, top };
}

/**
 * Parte de baixo da silhueta da arma num x (y mínimo com massa em z = 0), por um raio de baixo para cima no SDF.
 * @returns {number|null} null se não há massa nesse x
 */
export function underside(compiled, box, x, step = 0.04) {
  let y = box.min[1] - 0.5;
  while (y <= box.max[1] + 0.5) {
    const d = compiled.distance(x, y, 0);
    if (d < 0) return y;
    y += Math.max(d * 0.9, step);
  }
  return null;
}

/**
 * Suporte de arame para uma receita: a tira de compensado e os dois garfos (a 18% e 76% do comprimento), com a arma
 * posta em cima. Devolve o grupo do suporte e a posição da origem da arma no referencial do suporte.
 * @param {import('../../clay/set/index.js').SetLibrary} set
 * @param {object} def ARSENAL.stand
 * @param {object} recipe
 * @returns {{group:THREE.Group, weaponOffset:THREE.Vector3}}
 */
export function buildWireStand(set, def, recipe) {
  const tree = recipeWholeTree(recipe);
  const box = bounds(tree);
  const compiled = compile(tree);
  const length = box.max[0] - box.min[0];
  const height = box.max[1] - box.min[1];
  const centerX = (box.min[0] + box.max[0]) / 2;
  const forkXs = [0.18, 0.76].map((f) => box.min[0] + length * f);
  // Arame e garfo na medida da arma: a Glock pede arame fino e garfo baixo; a AWP, o arame cheio.
  const wire = Math.min(def.wire, Math.max(0.3, length * 0.016));
  const depth = Math.min(def.forkDepth, height * 0.16);
  // A arma fica alta o bastante para a parte mais baixa (carregador, empunhadura) passar livre da tira.
  const baseT = def.base.thickness;
  const lift = Math.max(def.lift, baseT + 2.5 - box.min[1]);
  const group = new THREE.Group();
  group.name = `suporte-${recipe.id}`;
  const base = new THREE.Mesh(new RoundedBoxGeometry(length * 1.05 + 4, baseT, Math.max(8, def.base.depth * Math.min(1, length / 40)), 2, 0.6), set.plywood());
  base.position.y = baseT / 2;
  base.name = 'suporte-base';
  group.add(base);
  const wires = [];
  for (const fx of forkXs) {
    const bottom = underside(compiled, box, fx) ?? box.min[1];
    // Meia largura da massa logo acima do apoio: os braços do garfo encostam dos dois lados.
    let half = 0.3;
    while (half < 4 && compiled.distance(fx, bottom + 0.35, half) < 0) half += 0.05;
    const x = fx - centerX;
    const tipY = lift + bottom - wire; // o arame encosta por baixo da massa
    const w = half + wire * 1.1;
    const post = new THREE.LineCurve3(new THREE.Vector3(x, baseT, 0), new THREE.Vector3(x, tipY, 0));
    const cradle = new THREE.CatmullRomCurve3([
      new THREE.Vector3(x, tipY + depth * 1.5, -w),
      new THREE.Vector3(x, tipY + depth * 0.4, -w * 0.97),
      new THREE.Vector3(x, tipY, -w * 0.5),
      new THREE.Vector3(x, tipY, 0),
      new THREE.Vector3(x, tipY, w * 0.5),
      new THREE.Vector3(x, tipY + depth * 0.4, w * 0.97),
      new THREE.Vector3(x, tipY + depth * 1.5, w),
    ]);
    wires.push(wireGeometry(post, wire, { radialSegments: 8 }), wireGeometry(cradle, wire, { radialSegments: 8 }));
  }
  const wireMesh = new THREE.Mesh(mergeGeometries(wires, false), set.wire());
  for (const g of wires) g.dispose();
  wireMesh.name = 'suporte-arame';
  group.add(wireMesh);
  for (const m of [base, wireMesh]) {
    m.castShadow = true;
    m.receiveShadow = true;
  }
  return { group, weaponOffset: new THREE.Vector3(-centerX, lift, 0) };
}
