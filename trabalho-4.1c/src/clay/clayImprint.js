// Camadas de impressão do ClayMaterial (tiradas de ClayMaterial.js na subfase 3.5), na face de cima da peça e mapeadas
// pelo XZ do objeto:
//  - CLAY_IMPRINT (3.3): textura de relevo fixa — R = fundo da marca, G = lábio de massa empurrada, B = marcas do rolo
//    — das letras carimbadas e dos furinhos das placas da pista (item 11 do moodboard: CIM1/CIM5/CIM8).
//  - CLAY_PRINTS (3.5): o mapa de pegadas vivo da peça (src/clay/prints/), um alvo de render — R = fundo (× `depth` u),
//    G = lábio (× `lip` u), B = massa fresca. Altura = lip · G · (1 − R) − depth · R: o lábio velho some onde uma marca
//    nova afunda (FIM3/FIM5). Fundo 35% mais escuro (o clayDeepen) e mais liso, mais liso ainda com a massa fresca
//    (FIM6/FIM7); o lábio pega mais luz.
// As duas deslocam a normal por diferença central de 4 amostras (a das pegadas somada à da letra) e entram na chave do
// programa como defines. As texturas são de quem chama (o mapa e o sistema de pegadas as liberam).

import * as THREE from 'three';

/** Uniforms e variáveis das camadas (antes das funções do fragment). */
export const IMPRINT_PARS_GLSL = /* glsl */ `
#ifdef CLAY_IMPRINT
uniform sampler2D uClayImprint;
uniform vec4 uClayImprintRect;
uniform vec3 uClayImprintDepth;
uniform vec2 uClayImprintTexel;
#endif
#ifdef CLAY_PRINTS
uniform sampler2D uClayPrints;
uniform vec4 uClayPrintsRect;
uniform vec2 uClayPrintsDepth;
uniform vec2 uClayPrintsTexel;
float clayPrintHeight(vec4 c) {
  return uClayPrintsDepth.y * c.g * (1.0 - c.r) - uClayPrintsDepth.x * c.r;
}
#endif
float clayImprintMask = 0.0;
float clayPrintMask = 0.0;
float clayPrintFresh = 0.0;
`;

/** As duas camadas no fragment, depois do albedo e das digitais (mexem em clayObjN e diffuseColor). */
export const IMPRINT_SAMPLE_GLSL = /* glsl */ `
#ifdef CLAY_IMPRINT
{
  // uv da impressão pelo XZ do objeto (retângulo com largura negativa = espelhado); só a face de cima recebe.
  vec2 iuv = (vClayPos.xz - uClayImprintRect.xy) / uClayImprintRect.zw;
  float top = smoothstep(0.6, 0.9, clayN.y) * step(0.0, iuv.x) * step(iuv.x, 1.0) * step(0.0, iuv.y) * step(iuv.y, 1.0);
  vec3 hw = vec3(-uClayImprintDepth.x, uClayImprintDepth.y, uClayImprintDepth.z);
  vec2 tx = uClayImprintTexel;
  vec4 c0 = texture(uClayImprint, iuv);
  float hL = dot(texture(uClayImprint, iuv - vec2(tx.x, 0.0)).rgb, hw);
  float hR = dot(texture(uClayImprint, iuv + vec2(tx.x, 0.0)).rgb, hw);
  float hD = dot(texture(uClayImprint, iuv - vec2(0.0, tx.y)).rgb, hw);
  float hU = dot(texture(uClayImprint, iuv + vec2(0.0, tx.y)).rgb, hw);
  // Diferença central em u do objeto (o sinal do retângulo cuida do espelhamento).
  float dhdx = (hR - hL) / (2.0 * uClayImprintRect.z * tx.x);
  float dhdz = (hU - hD) / (2.0 * uClayImprintRect.w * tx.y);
  clayObjN = normalize(clayObjN + vec3(-dhdx, 0.0, -dhdz) * top);
  // Fundo da marca: massa comprimida, mais escura e mais lisa (o carimbo alisa); o lábio pega mais luz.
  clayImprintMask = c0.r * top;
  diffuseColor.rgb = mix(diffuseColor.rgb, clayDeepen(diffuseColor.rgb), clayImprintMask * 0.35);
  diffuseColor.rgb *= 1.0 + c0.g * top * 0.04;
}
#endif
#ifdef CLAY_PRINTS
{
  // Pegadas: o mapa cobre a peça inteira no XZ do objeto (centrado); só a face de cima recebe.
  vec2 puv = (vClayPos.xz - uClayPrintsRect.xy) / uClayPrintsRect.zw;
  float ptop = smoothstep(0.6, 0.9, clayN.y) * step(0.0, puv.x) * step(puv.x, 1.0)
    * step(0.0, puv.y) * step(puv.y, 1.0);
  vec2 ptx = uClayPrintsTexel;
  vec4 p0 = texture(uClayPrints, puv);
  float pL = clayPrintHeight(texture(uClayPrints, puv - vec2(ptx.x, 0.0)));
  float pR = clayPrintHeight(texture(uClayPrints, puv + vec2(ptx.x, 0.0)));
  float pD = clayPrintHeight(texture(uClayPrints, puv - vec2(0.0, ptx.y)));
  float pU = clayPrintHeight(texture(uClayPrints, puv + vec2(0.0, ptx.y)));
  float pdx = (pR - pL) / (2.0 * uClayPrintsRect.z * ptx.x);
  float pdz = (pU - pD) / (2.0 * uClayPrintsRect.w * ptx.y);
  clayObjN = normalize(clayObjN + vec3(-pdx, 0.0, -pdz) * ptop);
  clayPrintMask = p0.r * ptop;
  clayPrintFresh = p0.b * ptop;
  diffuseColor.rgb = mix(diffuseColor.rgb, clayDeepen(diffuseColor.rgb), clayPrintMask * 0.35);
  diffuseColor.rgb *= 1.0 + p0.g * (1.0 - p0.r) * ptop * 0.04;
}
#endif
`;

/** Rugosidade: o fundo das marcas alisa; as pegadas frescas alisam mais. */
export const IMPRINT_ROUGHNESS_GLSL = /* glsl */ `
roughnessFactor = clamp(roughnessFactor - clayImprintMask * 0.18
  - clayPrintMask * (0.18 + 0.14 * clayPrintFresh), 0.2, 1.0);
`;

/**
 * Objetos de uniform das duas camadas, criados com o material e nunca trocados: o programa compilado lê os mesmos
 * objetos, então ligar, trocar ou desligar uma camada mexe só nos valores (com a define desligada, o three os ignora).
 */
export function imprintUniforms() {
  return {
    uClayImprint: { value: null },
    uClayImprintRect: { value: new THREE.Vector4() },
    uClayImprintDepth: { value: new THREE.Vector3() },
    uClayImprintTexel: { value: new THREE.Vector2() },
    uClayPrints: { value: null },
    uClayPrintsRect: { value: new THREE.Vector4() },
    uClayPrintsDepth: { value: new THREE.Vector2() },
    uClayPrintsTexel: { value: new THREE.Vector2() },
  };
}

/** Largura e altura em texels de uma textura ou de um alvo de render (fallback 512). */
function texelSize(map) {
  const img = map.image;
  return [1 / (img?.width ?? 512), 1 / (img?.height ?? 512)];
}

/**
 * Liga (ou troca) a impressão fixa: `map` com R = fundo, G = lábio, B = rolo; `rect` = [x0, z0, largura, profundidade]
 * no XZ do objeto (largura negativa espelha); `depth`/`lip`/`roller` em u. Devolve se o define mudou.
 */
export function applyImprint(material, { map, rect, depth = 1.6, lip = 0.35, roller = 0.08 }) {
  const u = material.clayUniforms;
  u.uClayImprint.value = map;
  u.uClayImprintRect.value.set(rect[0], rect[1], rect[2], rect[3]);
  u.uClayImprintDepth.value.set(depth, lip, roller);
  u.uClayImprintTexel.value.set(...texelSize(map));
  material.clay.imprint = { map, rect: [...rect], depth, lip, roller };
  const changed = !material.clayImprint;
  material.clayImprint = true;
  return changed;
}

/**
 * Liga (ou troca) o mapa de pegadas: `map` (textura do alvo de render) com R = fundo, G = lábio, B = massa fresca;
 * `rect` = [x0, z0, largura, profundidade] no XZ do objeto; `depth`/`lip` em u. Devolve se o define mudou.
 */
export function applyPrints(material, { map, rect, depth, lip }) {
  const u = material.clayUniforms;
  u.uClayPrints.value = map;
  u.uClayPrintsRect.value.set(rect[0], rect[1], rect[2], rect[3]);
  u.uClayPrintsDepth.value.set(depth, lip);
  u.uClayPrintsTexel.value.set(...texelSize(map));
  const changed = !material.clayPrints;
  material.clayPrints = true;
  return changed;
}

/** Desliga o mapa de pegadas (o alvo de render foi liberado). Devolve se o define mudou. */
export function removePrints(material) {
  if (!material.clayPrints) return false;
  material.clayUniforms.uClayPrints.value = null;
  material.clayPrints = false;
  return true;
}
