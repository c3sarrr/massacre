// Passadas do mapa de pegadas (subfase 3.5): numa chamada de render por peça e pose, primeiro o esmaecimento da pose
// inteira — um retângulo da peça toda com subtração reversa (n/255 no fundo e no lábio, 3n/255 no brilho) — e depois as
// marcas novas, todas numa malha instanciada: um retângulo por marca no referencial da peça, com mistura MAX por canal
// (fica a marca mais funda; o lábio velho some onde a nova afunda, no shader da massinha), cada uma já esmaecida pelos
// passos que vieram depois dela na fila (src/clay/prints/printQueue.js). O three refaz os mipmaps do alvo no fim da
// chamada, uma vez. A conta de cada texel é a de markTexel (src/clay/prints/marks.js), em GLSL dos mesmos números.

import * as THREE from 'three';
import { FOOTPRINTS, SOLE } from '../../data/footprints.js';
import { SOLE_GLSL, glslFloat as f } from './sole.js';
import { markBounds } from './marks.js';

const FP = FOOTPRINTS;
const LR = FP.lipRing;
const FADE = FP.fade;

const FADE_VERT = /* glsl */ `
precision highp float;
in vec3 position;
void main() {
  gl_Position = vec4(position.xy * 2.0 - 1.0, 0.0, 1.0);
}
`;

const FADE_FRAG = /* glsl */ `
precision highp float;
uniform vec3 uFade;
out vec4 fragColor;
void main() {
  fragColor = vec4(uFade, 0.0);
}
`;

const STAMP_VERT = /* glsl */ `
precision highp float;
in vec3 position;
in vec4 iBounds; // retângulo da marca no XZ da peça: x0, z0, x1, z1
in vec4 iPose; // x, z, dx, dz
in vec4 iShape; // tipo, força, passos do esmaecimento depois dela, lado de dentro
in vec4 iExtra; // calcanhar, frente, comprimento (sulco), meia largura (sulco) ou raio (montinho)
uniform vec4 uRect; // a peça: x0, z0, largura, profundidade
out vec2 vP;
flat out vec4 vPose;
flat out vec4 vShape;
flat out vec4 vExtra;
void main() {
  vec2 p = mix(iBounds.xy, iBounds.zw, position.xy);
  vP = p;
  vPose = iPose;
  vShape = iShape;
  vExtra = iExtra;
  gl_Position = vec4((p - uRect.xy) / uRect.zw * 2.0 - 1.0, 0.0, 1.0);
}
`;

const STAMP_FRAG = /* glsl */ `
precision highp float;
in vec2 vP;
flat in vec4 vPose;
flat in vec4 vShape;
flat in vec4 vExtra;
out vec4 fragColor;
${SOLE_GLSL}
float q8(float v) {
  return floor(clamp(v, 0.0, 1.0) * 255.0 + 0.5);
}
float lipRing(float d) {
  float t = (d - ${f(LR.offset)}) / ${f(LR.width)};
  return exp(-t * t);
}
void main() {
  vec2 p = vP - vPose.xy;
  vec2 dir = vPose.zw;
  float kind = vShape.x;
  float strength = vShape.y;
  float r = 0.0;
  float g = 0.0;
  float b = 0.0;
  if (kind < 0.5) {
    // Pé: a sola no referencial dele (a ao longo, bi para o lado de dentro).
    float peak = clamp(strength * max(vExtra.x, vExtra.y), 0.0, 1.0);
    float a = dot(p, dir);
    float bi = (p.y * dir.x - p.x * dir.y) * vShape.w;
    float d = soleDistance(vec2(a, bi));
    float push = vExtra.x + (vExtra.y - vExtra.x) * smoothstep(${f(SOLE.heel.a)}, ${f(SOLE.toe.a)}, a);
    r = smoothstep(0.0, ${f(FP.wall)}, -d) * soleCleats(vec2(a, bi)) * strength * push;
    if (d > 0.0) {
      float front = 1.0 + ${f(LR.front)} * smoothstep(${f(LR.frontFrom)}, ${f(LR.frontTo)}, a);
      g = min(peak, lipRing(d) * front * strength * ${f(LR.gain)});
    }
    b = d < ${f(FP.freshReach)} ? 1.0 : 0.0;
  } else if (kind < 1.5) {
    // Sulco do slide: cápsula ao longo do segmento.
    float peak = clamp(strength, 0.0, 1.0);
    float t = min(vExtra.z, max(0.0, dot(p, dir)));
    float d = length(p - dir * t) - vExtra.w;
    r = smoothstep(0.0, ${f(FP.wall)}, -d) * strength;
    if (d > 0.0) g = min(peak, lipRing(d) * strength * ${f(LR.gain)});
    b = d < ${f(FP.freshReach)} ? 1.0 : 0.0;
  } else {
    // Montinho: só lábio.
    float k = 1.0 - dot(p, p) / (vExtra.w * vExtra.w);
    if (k > 0.0) {
      g = strength * k * k;
      b = 1.0;
    }
  }
  vec3 q = vec3(q8(r), q8(g), q8(b)) - vShape.z * vec3(${f(FADE.depth)}, ${f(FADE.lip)}, ${f(FADE.fresh)});
  fragColor = vec4(max(q, 0.0) / 255.0, 0.0);
}
`;

/** Retângulo unitário (dois triângulos). */
function unitQuad(geometry) {
  geometry.setAttribute('position', new THREE.Float32BufferAttribute([0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 1, 0], 3));
  geometry.setIndex([0, 1, 2, 0, 2, 3]);
  return geometry;
}

const INSTANCE_ATTRIBUTES = ['iBounds', 'iPose', 'iShape', 'iExtra'];
const _bounds = [0, 0, 0, 0];

export class StampPass {
  constructor(capacity = 64) {
    this.scene = new THREE.Scene();
    this.scene.name = 'pegadas';
    this.camera = new THREE.OrthographicCamera();
    const common = { glslVersion: THREE.GLSL3, depthTest: false, depthWrite: false, blending: THREE.CustomBlending };
    this.fadeMaterial = new THREE.RawShaderMaterial({
      ...common, name: 'pegadas-esmaecer', vertexShader: FADE_VERT, fragmentShader: FADE_FRAG,
      uniforms: { uFade: { value: new THREE.Vector3() } },
      blendEquation: THREE.ReverseSubtractEquation, blendSrc: THREE.OneFactor, blendDst: THREE.OneFactor,
    });
    this.stampMaterial = new THREE.RawShaderMaterial({
      ...common, name: 'pegadas-carimbo', vertexShader: STAMP_VERT, fragmentShader: STAMP_FRAG,
      uniforms: { uRect: { value: new THREE.Vector4() } },
      blendEquation: THREE.MaxEquation, blendSrc: THREE.OneFactor, blendDst: THREE.OneFactor,
    });
    this.fade = new THREE.Mesh(unitQuad(new THREE.BufferGeometry()), this.fadeMaterial);
    this.fade.frustumCulled = false;
    this.fade.renderOrder = 0;
    this.stamps = new THREE.Mesh(this.#geometry(capacity), this.stampMaterial);
    this.stamps.frustumCulled = false;
    this.stamps.renderOrder = 1;
    this.scene.add(this.fade, this.stamps);
  }

  /** Geometria instanciada com lugar para `capacity` marcas. */
  #geometry(capacity) {
    const geo = unitQuad(new THREE.InstancedBufferGeometry());
    for (const name of INSTANCE_ATTRIBUTES) {
      const attr = new THREE.InstancedBufferAttribute(new Float32Array(capacity * 4), 4);
      attr.setUsage(THREE.DynamicDrawUsage);
      geo.setAttribute(name, attr);
    }
    geo.instanceCount = 0;
    this.capacity = capacity;
    return geo;
  }

  /** Compila os dois programas (ao montar o mapa, e não no primeiro passo). */
  compile(renderer) {
    renderer.compile(this.scene, this.camera);
  }

  /** Enche as instâncias com as marcas (no referencial da peça, cada uma com `fades`). */
  #fill(marks) {
    if (marks.length > this.capacity) {
      let n = this.capacity;
      while (n < marks.length) n *= 2;
      this.stamps.geometry.dispose();
      this.stamps.geometry = this.#geometry(n);
    }
    const geo = this.stamps.geometry;
    const [bounds, pose, shape, extra] = INSTANCE_ATTRIBUTES.map((k) => geo.attributes[k]);
    for (let i = 0; i < marks.length; i++) {
      const m = marks[i];
      markBounds(m, _bounds);
      bounds.setXYZW(i, _bounds[0], _bounds[1], _bounds[2], _bounds[3]);
      pose.setXYZW(i, m.x, m.z, m.dx, m.dz);
      shape.setXYZW(i, m.kind, m.strength, m.fades ?? 0, m.inner ?? 1);
      extra.setXYZW(i, m.heel ?? 1, m.front ?? 1, m.length ?? 0, m.halfWidth ?? m.radius ?? 0);
    }
    for (const attr of [bounds, pose, shape, extra]) {
      attr.clearUpdateRanges();
      attr.addUpdateRange(0, marks.length * 4);
      attr.needsUpdate = true;
    }
    geo.instanceCount = marks.length;
  }

  /**
   * Uma chamada de render no alvo `target` da peça de `width` × `depth` u (centrada): `fades` passos do esmaecimento e
   * as marcas `marks`. O alvo e o autoClear do renderer voltam ao que eram.
   */
  draw(renderer, target, width, depth, fades, marks) {
    this.fade.visible = fades > 0;
    const step = (rate) => Math.min(1, (fades * rate) / 255);
    this.fadeMaterial.uniforms.uFade.value.set(step(FADE.depth), step(FADE.lip), step(FADE.fresh));
    this.stamps.visible = marks.length > 0;
    if (marks.length) this.#fill(marks);
    this.stampMaterial.uniforms.uRect.value.set(-width / 2, -depth / 2, width, depth);
    const previous = renderer.getRenderTarget();
    const autoClear = renderer.autoClear;
    renderer.autoClear = false;
    renderer.setRenderTarget(target);
    renderer.render(this.scene, this.camera);
    renderer.setRenderTarget(previous);
    renderer.autoClear = autoClear;
  }

  dispose() {
    this.fade.geometry.dispose();
    this.stamps.geometry.dispose();
    this.fadeMaterial.dispose();
    this.stampMaterial.dispose();
  }
}
