// Luz da camada do viewmodel (Fase 4.1; docs/phases/phase-4.md, seção 4.1, "Viewmodel parado"): cópias das luzes do mapa
// (spot, pontual, direcional, hemisférica e ambiente — mesmas posições, cores e intensidades, lidas a cada quadro, então
// o painel da vitrine e o console `luz` valem na hora) e o ambiente assado. Assim a arma escurece fora do feixe da key,
// como o resto do set. Duas coisas que a cópia sozinha não faz:
//  - o set tapar a luz: de alguns pontos da arma (centro, boca, pulsos), um raio no mundo de colisão até cada luz que
//    faz sombra no mapa; a fração livre multiplica a cópia (suavizada);
//  - a sombra própria (a mão na arma, a arma nos dedos): a cópia de cada spot/direcional que faz sombra no mapa projeta
//    sombra na camada, com a câmera de sombra apertada numa esfera em volta da arma e dos pulsos (mais texels no que
//    importa; o cone e a direção da luz continuam os do mapa).

import * as THREE from 'three';
import { VIEWMODEL } from '../../data/viewmodel.js';
import { createRayHit } from '../../physics/collisionWorld.js';

const L = VIEWMODEL.light;
const _p = new THREE.Vector3();
const _t = new THREE.Vector3();
const _d = new THREE.Vector3();

/**
 * A câmera de sombra de uma luz vista de onde ela está, apertada numa esfera (centro e raio no mundo). Usa a conta do
 * three (LightShadow.updateMatrices) com uma luz de mentira que "mira" o centro da esfera: a iluminação continua com o
 * cone e a direção da luz de verdade.
 */
function focusShadow(shadow) {
  shadow.sphere = new THREE.Sphere(new THREE.Vector3(), 10);
  const proxy = { matrixWorld: new THREE.Matrix4(), target: { matrixWorld: new THREE.Matrix4() } };
  const base = THREE.LightShadow.prototype.updateMatrices;
  shadow.updateMatrices = function updateMatrices(light) {
    const cam = this.camera;
    const { center, radius } = this.sphere;
    if (cam.isPerspectiveCamera) {
      _p.setFromMatrixPosition(light.matrixWorld);
      const d = Math.max(_p.distanceTo(center), radius * 1.05);
      const fov = (2 * Math.asin(Math.min(0.999, radius / d)) * 180) / Math.PI;
      const near = Math.max(0.05, d - radius);
      const far = d + radius;
      if (cam.fov !== fov || cam.near !== near || cam.far !== far || cam.aspect !== 1) {
        cam.fov = fov;
        cam.near = near;
        cam.far = far;
        cam.aspect = 1;
        cam.updateProjectionMatrix();
      }
      proxy.matrixWorld.copy(light.matrixWorld);
    } else {
      // Direcional: a câmera ortográfica sai de trás da esfera, na direção da luz.
      _p.setFromMatrixPosition(light.matrixWorld);
      _t.setFromMatrixPosition(light.target.matrixWorld);
      _d.subVectors(_p, _t).normalize();
      const back = radius * 3;
      proxy.matrixWorld.makeTranslation(center.x + _d.x * back, center.y + _d.y * back, center.z + _d.z * back);
      if (cam.right !== radius || cam.near !== back - radius || cam.far !== back + radius) {
        cam.left = cam.bottom = -radius;
        cam.right = cam.top = radius;
        cam.near = back - radius;
        cam.far = back + radius;
        cam.updateProjectionMatrix();
      }
    }
    proxy.target.matrixWorld.makeTranslation(center.x, center.y, center.z);
    base.call(this, proxy);
  };
  return shadow;
}

/** A luz visível de fato (ela e todos os pais visíveis, como o renderer do three decide). */
function effectivelyVisible(obj) {
  for (let o = obj; o; o = o.parent) if (!o.visible) return false;
  return true;
}

function makeCopy(src) {
  let copy;
  if (src.isSpotLight) copy = new THREE.SpotLight();
  else if (src.isPointLight) copy = new THREE.PointLight();
  else if (src.isDirectionalLight) copy = new THREE.DirectionalLight();
  else if (src.isHemisphereLight) copy = new THREE.HemisphereLight();
  else if (src.isAmbientLight) copy = new THREE.AmbientLight();
  else return null;
  copy.name = `vm:${src.name || src.type}`;
  // A matriz de cada quadro é a do mundo da luz do mapa (o grupo das cópias fica na origem).
  copy.matrixAutoUpdate = false;
  if (copy.target) copy.target.matrixAutoUpdate = false;
  // Só as que fazem sombra no mapa podem fazer a sombra própria (e só spot e direcional: a pontual gastaria 6 faces).
  const selfShadow = src.castShadow && (src.isSpotLight || src.isDirectionalLight);
  if (selfShadow) {
    focusShadow(copy.shadow);
    copy.shadow.bias = L.selfShadow.bias;
    copy.shadow.normalBias = L.selfShadow.normalBias;
  }
  return { src, copy, selfShadow, occludes: Boolean(src.castShadow) && !src.isHemisphereLight && !src.isAmbientLight, visibility: 1 };
}

export class ViewmodelLights {
  /** @param {THREE.Scene} scene a cena da camada (as cópias entram nela) */
  constructor(scene) {
    this.scene = scene;
    this.group = new THREE.Group();
    this.group.name = 'viewmodel:luzes';
    scene.add(this.group);
    this.entries = [];
    this.source = null;
    this.world = null;
    this.hit = createRayHit();
    this.shadowSize = 0;
    this.shadowRadius = 0;
    this.shadowOn = false;
    this.scanClock = 0;
  }

  /**
   * Liga ao mapa: lê as luzes da cena dele (as cópias saem de novo quando a lista muda) e o mundo de colisão (null =
   * nada tapa a luz, como na bancada).
   */
  attach(sourceScene, world = null) {
    this.source = sourceScene;
    this.world = world;
    this.#rebuild();
  }

  #collect() {
    const list = [];
    this.source?.traverse((o) => {
      if (o.isLight) list.push(o);
    });
    return list;
  }

  #rebuild() {
    this.#clear();
    for (const src of this.#collect()) {
      const e = makeCopy(src);
      if (!e) continue;
      this.group.add(e.copy);
      if (e.copy.target) this.group.add(e.copy.target);
      this.entries.push(e);
    }
    this.shadowSize = 0;
  }

  #clear() {
    for (const e of this.entries) {
      e.copy.shadow?.map?.dispose();
      e.copy.dispose?.();
      e.copy.removeFromParent();
      e.copy.target?.removeFromParent();
    }
    this.entries = [];
  }

  /**
   * As luzes do mapa mudaram de lista? Uma que saiu da cena aparece na hora (sem pai); uma que entrou, na varredura da
   * cena a cada `light.rescan` s (a lista quase nunca muda: o painel mexe nas propriedades, não na lista).
   */
  #changed(dt) {
    for (const e of this.entries) if (!e.src.parent) return true;
    this.scanClock += dt;
    if (this.scanClock < L.rescan) return false;
    this.scanClock = 0;
    return this.#stale();
  }

  /** Confere a lista inteira pelos objetos, sem alocar. */
  #stale() {
    let n = 0;
    let stale = false;
    this.source?.traverse((o) => {
      if (!o.isLight || stale) return;
      if (this.entries[n]?.src !== o) stale = true;
      n++;
    });
    return stale || n !== this.entries.length;
  }

  /**
   * Nível da sombra própria: lado do mapa pelo nível de sombra do jogo (× mapScale), filtro pelo raio do nível.
   * @param {{mapSize:number, radius:number}} level SHADOW_LEVELS do render
   * @param {boolean} enabled sombras ligadas no renderer
   */
  #applyShadowLevel(level, enabled) {
    const S = L.selfShadow;
    const on = enabled && level.mapSize > 0;
    const size = on ? Math.min(S.maxSize, Math.max(S.minSize, Math.round(level.mapSize * S.mapScale))) : 0;
    const radius = level.radius * S.softness;
    if (size === this.shadowSize && radius === this.shadowRadius && on === this.shadowOn) return;
    this.shadowSize = size;
    this.shadowRadius = radius;
    this.shadowOn = on;
    for (const e of this.entries) {
      if (!e.selfShadow) continue;
      e.copy.castShadow = on;
      if (!on) continue;
      if (e.copy.shadow.mapSize.x !== size) {
        e.copy.shadow.mapSize.set(size, size);
        e.copy.shadow.map?.dispose();
        e.copy.shadow.map = null;
      }
      e.copy.shadow.radius = radius;
    }
  }

  /** Há sombra própria neste quadro (a camada força o mapa de sombra quando o mapa usa sombras estáticas)? */
  get casting() {
    return this.shadowOn && this.entries.some((e) => e.selfShadow && e.copy.visible && e.copy.intensity > 0);
  }

  /**
   * Um quadro: copia as luzes (posição, alvo, cor, intensidade, cone), atualiza o quanto o set tapa cada uma e a esfera
   * da sombra própria.
   * @param {object} o
   * @param {THREE.Vector3[]} o.points pontos da arma no mundo (centro, boca, pulsos) para a oclusão
   * @param {THREE.Sphere} o.sphere esfera da arma e dos pulsos no mundo
   * @param {{mapSize:number, radius:number}} o.level nível de sombra do jogo
   * @param {boolean} o.shadows sombras ligadas no renderer
   * @param {number} o.dt segundos desde o quadro anterior
   */
  update({ points, sphere, level, shadows, dt }) {
    if (!this.source) return;
    if (this.#changed(dt)) this.#rebuild();
    this.#applyShadowLevel(level, shadows);
    const scene = this.scene;
    scene.environment = this.source.environment;
    scene.environmentIntensity = this.source.environmentIntensity ?? 1;
    scene.environmentRotation.copy(this.source.environmentRotation);
    const O = L.occlusion;
    for (const e of this.entries) {
      const { src, copy } = e;
      copy.visible = effectivelyVisible(src);
      copy.color.copy(src.color);
      if (src.isHemisphereLight) copy.groundColor.copy(src.groundColor);
      copy.matrix.copy(src.matrixWorld);
      copy.matrixWorld.copy(src.matrixWorld);
      if (copy.target) {
        copy.target.matrix.copy(src.target.matrixWorld);
        copy.target.matrixWorld.copy(src.target.matrixWorld);
      }
      if (src.isSpotLight || src.isPointLight) {
        copy.distance = src.distance;
        copy.decay = src.decay;
      }
      if (src.isSpotLight) {
        copy.angle = src.angle;
        copy.penumbra = src.penumbra;
      }
      if (e.occludes && copy.visible && this.world && points.length) {
        const target = this.#visibility(src, points);
        const tau = target > e.visibility ? O.rise : O.fall;
        e.visibility += (target - e.visibility) * (1 - Math.exp(-Math.max(0, dt) / tau));
      } else {
        e.visibility = 1;
      }
      copy.intensity = src.intensity * e.visibility;
      if (e.selfShadow && copy.castShadow) copy.shadow.sphere.copy(sphere);
    }
  }

  /** Fração dos pontos que enxergam a luz (raios no mundo de colisão). */
  #visibility(src, points) {
    _p.setFromMatrixPosition(src.matrixWorld);
    let free = 0;
    for (const pt of points) {
      let max;
      if (src.isDirectionalLight) {
        _t.setFromMatrixPosition(src.target.matrixWorld);
        _d.subVectors(_p, _t).normalize();
        max = 1e5;
      } else {
        _d.subVectors(_p, pt);
        max = _d.length() - 1;
        if (max <= 0) {
          free++;
          continue;
        }
        _d.normalize();
      }
      if (!this.world.raycast(pt.x, pt.y, pt.z, _d.x, _d.y, _d.z, max, this.hit)) free++;
    }
    return free / points.length;
  }

  dispose() {
    this.#clear();
    this.group.removeFromParent();
    this.scene.environment = null;
    this.source = null;
    this.world = null;
  }
}
