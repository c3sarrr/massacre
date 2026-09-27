// O rebatedor da bancada `arsenal` (Fase 4.1b; desenho, seção 7.6; plano, Tarefa 12): o painel de isopor branco num
// C-stand, atrás de quem olha a bancada e virado para ela — na foto do reflexo das armas realistas (o olho do "Segurar")
// e no cone da luz que o alimenta (o rim da vitrine, a única que chega pela frente ali: a key e o fill ficam atrás
// dele), sem fazer sombra da key no tapete; o tripé no chão, fora da mesa; fosco e sem boil; e sai com o mapa (as
// geometrias; os materiais são da biblioteca do set, divididos).
import { test } from 'node:test';
import assert from 'node:assert/strict';
import * as THREE from 'three';
import { ARSENAL } from '../src/data/arsenal.js';
import { HULL } from '../src/data/movement.js';
import { STUDIO_RIGS } from '../src/data/studioRigs.js';
import { foamMaterial } from '../src/clay/set/surfaceMaterials.js';
import { construirRebatedor } from '../src/maps/arsenal/rebatedor.js';

const D = ARSENAL.desk;
const tableY = D.mat.thickness;
const olho = new THREE.Vector3(ARSENAL.reflexo.x, tableY + HULL.standEye, ARSENAL.reflexo.z);
const luzes = STUDIO_RIGS[ARSENAL.rig].lights;
const key = luzes.find((l) => l.id === 'key');
const fonte = luzes.find((l) => l.id === ARSENAL.rebatedor.luz);

function setFalso() {
  const mats = { foam: new THREE.MeshStandardMaterial(), blackMetal: new THREE.MeshStandardMaterial(), chrome: new THREE.MeshStandardMaterial() };
  return { mats, foam: () => mats.foam, blackMetal: () => mats.blackMetal, chrome: () => mats.chrome };
}

function montar() {
  const set = setFalso();
  const r = construirRebatedor(set, ARSENAL.rebatedor, { floorY: D.floorY, apoioY: 0, olho, luz: new THREE.Vector3(...fonte.position) });
  const scene = new THREE.Scene();
  scene.add(r.group);
  scene.updateMatrixWorld(true);
  return { set, r, scene, painel: r.group.getObjectByName('rebatedor-painel') };
}

/** O centro e a normal da frente do painel (a face +Z dele) no mundo. */
function frente(painel) {
  const centro = painel.getWorldPosition(new THREE.Vector3());
  const normal = new THREE.Vector3(0, 0, 1).applyQuaternion(painel.getWorldQuaternion(new THREE.Quaternion()));
  return { centro, normal };
}

test('rebatedor: o painel atrás do olho do reflexo, virado para ele e o primeiro que o olho vê naquela direção', () => {
  const { r, scene, painel } = montar();
  assert.ok(painel, 'o painel de isopor');
  const { centro, normal } = frente(painel);
  assert.ok(centro.z > ARSENAL.reflexo.z + 100, 'atrás de quem olha a bancada (o olho olha para −Z)');
  assert.ok(centro.y > tableY + 60, 'acima do tampo');
  const paraOlho = olho.clone().sub(centro).normalize();
  assert.ok(normal.dot(paraOlho) > 0.6, `virado para o olho (cos ${normal.dot(paraOlho).toFixed(2)})`);
  // a foto do reflexo é a cena inteira na camada 0: o painel está nela, visível e opaco, e nada o tapa do olho
  assert.ok(painel.visible && painel.layers.isEnabled(0) && !painel.material.transparent);
  const ray = new THREE.Raycaster(olho, centro.clone().sub(olho).normalize());
  const hit = ray.intersectObject(scene, true)[0];
  assert.equal(hit?.object, painel, 'o primeiro objeto na direção do painel');
  // cobre o reflexo do lado do receptor na roda: visto do olho, o lado virado para quem olha reflete +Z um pouco para
  // baixo (elevação −0,29, o tampo atrás do olho); pelo menos 60 % de um cone de 25° em volta dessa direção cai na placa
  const eixoDoReflexo = new THREE.Vector3(0, -0.29, 0.96).normalize();
  const giro = new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0, 0, 1), eixoDoReflexo);
  let cobre = 0;
  const N = 200;
  for (let i = 0; i < N; i++) {
    const cosA = 1 - ((i + 0.5) / N) * (1 - Math.cos(THREE.MathUtils.degToRad(25)));
    const sinA = Math.sqrt(1 - cosA * cosA);
    const d = new THREE.Vector3(sinA * Math.cos(i * 2.399963), sinA * Math.sin(i * 2.399963), cosA).applyQuaternion(giro);
    if (new THREE.Raycaster(olho, d).intersectObject(painel).length) cobre++;
  }
  assert.ok(cobre / N >= 0.6, `a placa cobre ${(100 * cobre / N).toFixed(0)} % do reflexo do receptor`);
  // tamanho de uma placa de isopor de 20 mm
  const caixa = new THREE.Box3().setFromBufferAttribute(painel.geometry.attributes.position);
  const lado = caixa.getSize(new THREE.Vector3());
  assert.deepEqual([lado.x, lado.y, lado.z].map(Math.round), [ARSENAL.rebatedor.largura, ARSENAL.rebatedor.altura, ARSENAL.rebatedor.espessura]);
  r.dispose();
});

test('rebatedor: no cone do rim, com a frente para ele, e sem fazer sombra da key no tapete nem na roda', () => {
  const { r, scene, painel } = montar();
  const { centro, normal } = frente(painel);
  const pos = new THREE.Vector3(...fonte.position);
  const eixo = new THREE.Vector3(...fonte.target).sub(pos).normalize();
  const angulo = THREE.MathUtils.radToDeg(eixo.angleTo(centro.clone().sub(pos).normalize()));
  assert.ok(angulo < fonte.angleDeg * 0.8, `dentro do cone do ${fonte.id} (${angulo.toFixed(1)}° de ${fonte.angleDeg}°)`);
  assert.ok(normal.dot(pos.clone().sub(centro).normalize()) > 0.6, `a frente recebe o ${fonte.id}`);
  // a key (atrás do painel) chega a todo o tapete e ao prato da roda
  const kpos = new THREE.Vector3(...key.position);
  const rebatedor = [];
  r.group.traverse((o) => o.isMesh && rebatedor.push(o));
  const alvos = [new THREE.Vector3(ARSENAL.turntable.x, tableY + 30, ARSENAL.turntable.z)];
  for (let x = -D.mat.width / 2; x <= D.mat.width / 2; x += 50) {
    for (let z = D.mat.z - D.mat.depth / 2; z <= D.mat.z + D.mat.depth / 2; z += 50) alvos.push(new THREE.Vector3(x, tableY, z));
  }
  for (const alvo of alvos) {
    const hits = new THREE.Raycaster(kpos, alvo.clone().sub(kpos).normalize(), 0, alvo.distanceTo(kpos)).intersectObjects(rebatedor, true);
    assert.equal(hits.length, 0, `o rebatedor tapa a key em ${alvo.toArray().map(Math.round)}`);
  }
  scene.remove(r.group);
  r.dispose();
});

test('rebatedor: a placa assenta no tampo atrás do tapete — a borda de baixo encosta, sem entrar e sem flutuar', () => {
  const { r, painel } = montar();
  const p = painel.geometry.attributes.position;
  const v = new THREE.Vector3();
  let baixo = Infinity;
  const apoiados = [];
  for (let i = 0; i < p.count; i++) {
    v.fromBufferAttribute(p, i).applyMatrix4(painel.matrixWorld);
    if (v.y < baixo - 1e-6) {
      baixo = v.y;
      apoiados.length = 0;
    }
    // a BoxGeometry repete cada canto uma vez por face: conta os cantos, não os vértices
    if (Math.abs(v.y - baixo) < 1e-6 && !apoiados.some((a) => a.distanceTo(v) < 1e-6)) apoiados.push(v.clone());
  }
  // o tampo da mesa fica em y = 0 (src/data/showcase.js)
  assert.ok(Math.abs(baixo) < 0.01, `a borda de baixo a ${baixo.toFixed(2)} mm do tampo`);
  // a aresta que encosta (os dois cantos de baixo de trás: deitada para trás, a placa se apoia nela) fica na madeira:
  // dentro da mesa (longe da borda arredondada) e atrás da beira de trás do tapete — em cima dele, a placa entraria
  // 2,2 mm nele
  assert.equal(apoiados.length, 2, 'uma aresta inteira encosta');
  const beiraDoTapete = D.mat.z + D.mat.depth / 2;
  for (const a of apoiados) {
    const onde = a.toArray().map(Math.round);
    assert.ok(Math.abs(a.x) <= D.desk.width / 2 - 10 && Math.abs(a.z) <= D.desk.depth / 2 - 10, `canto fora da mesa em ${onde}`);
    assert.ok(a.z >= beiraDoTapete + 5, `canto no tapete em ${onde} (a beira de trás dele em z ${beiraDoTapete})`);
  }
  // e nenhum pedaço da placa dentro do tapete: pontos nos segmentos entre os cantos (a caixa é convexa, então cobrem as
  // arestas, as faces e o miolo)
  const cantos = [];
  for (let i = 0; i < p.count; i++) {
    v.fromBufferAttribute(p, i).applyMatrix4(painel.matrixWorld);
    if (!cantos.some((c) => c.distanceTo(v) < 1e-6)) cantos.push(v.clone());
  }
  assert.equal(cantos.length, 8);
  const tapete = new THREE.Box3(
    new THREE.Vector3(D.mat.x - D.mat.width / 2, 0, D.mat.z - D.mat.depth / 2),
    new THREE.Vector3(D.mat.x + D.mat.width / 2, tableY, D.mat.z + D.mat.depth / 2),
  );
  const q = new THREE.Vector3();
  for (let i = 0; i < 8; i++) {
    for (let j = i + 1; j < 8; j++) {
      for (let t = 0; t <= 1; t += 1 / 40) {
        q.lerpVectors(cantos[i], cantos[j], t);
        assert.ok(!tapete.containsPoint(q), `a placa entra no tapete em ${q.toArray().map((c) => c.toFixed(1))}`);
      }
    }
  }
  r.dispose();
});

test('rebatedor: o C-stand no chão do estúdio, fora da mesa', () => {
  const { r } = montar();
  const tripe = r.group.getObjectByName('c-stand');
  assert.ok(tripe, 'o tripé');
  const caixa = new THREE.Box3().setFromObject(tripe);
  assert.ok(Math.abs(caixa.min.y - D.floorY) < 1, 'os pés no chão');
  // a coluna (o que desce do tampo até o chão) passa fora da mesa: nenhum vértice do tripé dentro do volume do tampo
  const tampo = new THREE.Box3(new THREE.Vector3(-D.desk.width / 2, -D.desk.thickness, -D.desk.depth / 2), new THREE.Vector3(D.desk.width / 2, 0, D.desk.depth / 2));
  const v = new THREE.Vector3();
  tripe.traverse((o) => {
    if (!o.isMesh) return;
    const p = o.geometry.attributes.position;
    for (let i = 0; i < p.count; i++) {
      v.fromBufferAttribute(p, i).applyMatrix4(o.matrixWorld);
      assert.ok(!tampo.containsPoint(v), `vértice do tripé dentro do tampo em ${v.toArray().map(Math.round)}`);
    }
  });
  r.dispose();
});

test('rebatedor: isopor fosco, sem metal e sem boil; sai com o mapa sem levar os materiais do set', () => {
  const m = foamMaterial({});
  assert.equal(m.name, 'massacre.set.isopor');
  assert.ok(m.roughness >= 0.85 && m.metalness === 0);
  assert.ok(!m.userData?.boil, 'o set não pulsa');
  m.dispose();
  const { set, r } = montar();
  const geos = [];
  r.group.traverse((o) => o.isMesh && geos.push(o.geometry));
  let descartadas = 0;
  for (const g of geos) g.addEventListener('dispose', () => descartadas++);
  let materiais = 0;
  for (const mat of Object.values(set.mats)) mat.addEventListener('dispose', () => materiais++);
  r.dispose();
  assert.equal(descartadas, geos.length, 'todas as geometrias');
  assert.equal(materiais, 0, 'os materiais são da biblioteca (divididos)');
});
