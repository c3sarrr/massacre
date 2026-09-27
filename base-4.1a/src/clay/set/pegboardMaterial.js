// Quadro de ferramentas de hardboard perfurado (Fase 4.1, bancada `arsenal`; QPB8, QPB13, QPB19 no item 13 do
// moodboard): chapa de fibra prensada marrom, face lisa com o fibrado fino e manchas de uso, e a grade de furos
// redondos (furo escuro com a borda levemente afundada). Os furos são procedurais no espaço do objeto (a face é o
// plano XY da peça, a espessura em Z), sem textura: nítidos de perto e, de longe, viram o tom médio (sem moiré).

import * as THREE from 'three';
import { createSetMaterial } from './setShader.js';

const linear = (hex) => new THREE.Color(hex);

/**
 * @param {object} tex texturas assadas do set (não usadas: o hardboard é todo procedural)
 * @param {{color?:string, fiber?:string, holeColor?:string, pitch?:number, hole?:number, origin?:number[],
 *          name?:string}} [opts] `origin` = centro de um furo no XY da peça; `pitch` = passo da grade; `hole` = raio
 */
export function pegboardMaterial(tex, {
  color = '#8E6B49', fiber = '#6E4F33', holeColor = '#1B130D', pitch = 25.4, hole = 3.3, origin = [0, 0], name = 'hardboard',
} = {}) {
  return createSetMaterial({
    name,
    params: { color: 0xffffff, roughness: 0.78, metalness: 0 },
    uniforms: {
      uPegColor: { value: linear(color) },
      uPegFiber: { value: linear(fiber) },
      uPegHole: { value: linear(holeColor) },
      uPegGrid: { value: new THREE.Vector4(pitch, hole, origin[0], origin[1]) },
    },
    light: { wrap: 0.32, lift: 0.07 },
    fragPars: /* glsl */ `
uniform vec3 uPegColor;
uniform vec3 uPegFiber;
uniform vec3 uPegHole;
uniform vec4 uPegGrid;
`,
    surface: /* glsl */ `
vec3 p = setP;
// Fibrado da chapa: grão fino e curto em todas as direções, manchas largas de tom e marcas de uso.
float grain = clayFbm3(vec3(p.xy * 0.21, p.z * 0.21 + 1.7), 3) * 0.5 + 0.5;
float blotch = clayNoise3(vec3(p.xy * 0.006, 4.2)) * 0.5 + 0.5;
vec3 col = mix(uPegColor, uPegFiber, grain * 0.38 + blotch * 0.22);
setRough += (grain - 0.5) * 0.08;
if (abs(setN.z) > 0.5) {
  // Face: grade de furos. De longe (a célula do pixel passa de um quinto do passo) o furo vira o tom médio.
  vec2 g = (p.xy - uPegGrid.zw) / uPegGrid.x;
  vec2 c = floor(g + 0.5);
  vec2 d = (g - c) * uPegGrid.x;
  float r = length(d);
  float aa = max(fwidth(r), 1e-3);
  float far = smoothstep(0.12, 0.35, fwidth(g.x));
  float holeMask = (1.0 - smoothstep(uPegGrid.y - aa, uPegGrid.y + aa, r)) * (1.0 - far);
  float rim = smoothstep(uPegGrid.y - aa, uPegGrid.y, r) * (1.0 - smoothstep(uPegGrid.y, uPegGrid.y * 1.5, r)) * (1.0 - far);
  float coverage = 3.14159 * uPegGrid.y * uPegGrid.y / (uPegGrid.x * uPegGrid.x);
  col = mix(col, uPegHole, holeMask);
  col = mix(col, mix(col, uPegHole, coverage), far);
  col *= 1.0 - rim * 0.18;
  vec2 dir = r > 1e-4 ? d / r : vec2(0.0);
  setObjN = normalize(setN + vec3(-dir * rim * 0.55, 0.0) * sign(setN.z));
  setRough += holeMask * 0.15;
}
diffuseColor.rgb = col;
`,
  });
}
