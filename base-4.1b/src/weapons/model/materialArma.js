// Material de uma zona das armas realistas (Fase 4.1a; desenho em docs/superpowers/specs/2026-09-26-armas-realistas-
// design.md, seção 5.3; plano da 4.1a, D3): MeshPhysicalMaterial com a normal assada (_n, espaço tangente com as
// tangentes do .glb, normalScale 1), a sombra de contato (_m.r pelo aoMap), o reflexo do set (envMap; sem ele, o
// ambiente da cena) e o trecho de shader do acabamento (glsl/acabamentos.js): padrão procedural, variações assadas,
// desgaste pela borda, anisotropia no eixo da arma. Os números vêm da função pura acabamentoParaMaterial. Os recursos do
// material físico (verniz, iridescência, anisotropia) só ligam quando o acabamento pede: cada combinação é uma variante
// de shader, e a chave do programa diz qual (defines + customProgramCacheKey), para a compilação no carregamento
// (renderer.compileAsync, no viewmodel e na bancada) cobrir todas.

import * as THREE from 'three';
import { acabamentoParaMaterial } from '../skins/acabamento.js';
import {
  ARMA_ANISOTROPIA, ARMA_ASPEREZA, ARMA_COR, ARMA_FRAGMENT_PARS, ARMA_METAL, ARMA_VERTEX, ARMA_VERTEX_PARS,
} from './glsl/acabamentos.js';

const linear = (c) => new THREE.Color().setRGB(c[0], c[1], c[2], THREE.LinearSRGBColorSpace);

/**
 * @param {{zona:string, def:{acabamento:string, cor:string, cor2?:string|null, desgaste?:number},
 *   texturas:{n:THREE.Texture, m:THREE.Texture}, ambiente?:THREE.Texture|null, intensidade?:number, nome?:string}} o
 *   `ambiente` = o reflexo do set (null: o ambiente da cena); `intensidade` = a dele no material
 * @returns {THREE.MeshPhysicalMaterial} marcado `userData.shared` (quem cria descarta)
 */
export function criarMaterialZona({ zona, def, texturas, ambiente = null, intensidade = 1, nome = `arma:${zona}` }) {
  const p = acabamentoParaMaterial(def);
  const m = new THREE.MeshPhysicalMaterial({
    name: nome,
    color: linear(p.color),
    metalness: p.metalness,
    roughness: p.roughness,
    normalMap: texturas.n,
    normalScale: new THREE.Vector2(1, 1),
    aoMap: texturas.m,
    aoMapIntensity: 1,
    envMap: ambiente,
    envMapIntensity: intensidade,
    clearcoat: p.clearcoat,
    clearcoatRoughness: p.clearcoatRoughness,
    iridescence: p.iridescence,
    iridescenceIOR: p.iridescenceIOR,
    iridescenceThicknessRange: p.iridescenceThicknessRange,
    anisotropy: p.anisotropy,
  });
  m.userData.zona = zona;
  m.userData.acabamento = p.acabamento;
  m.userData.shared = true;
  m.defines = { ARMA_PADRAO: p.padraoId };
  if (p.anisotropy > 0) m.defines.ARMA_ESCOVADO = '';
  const u = {
    mapaM: { value: texturas.m },
    corDois: { value: linear(p.color2 ?? p.color) },
    corGasto: { value: linear(p.gasto.color) },
    metalGasto: { value: p.gasto.metalness },
    asperezaGasto: { value: p.gasto.roughness },
    desgaste: { value: p.desgaste },
    varAspereza: { value: p.varAspereza },
    varCor: { value: p.varCor },
  };
  m.userData.uniforms = u;
  m.onBeforeCompile = (shader) => {
    Object.assign(shader.uniforms, u);
    shader.vertexShader = shader.vertexShader
      .replace('#include <common>', `#include <common>\n${ARMA_VERTEX_PARS}`)
      .replace('#include <begin_vertex>', `#include <begin_vertex>\n${ARMA_VERTEX}`);
    shader.fragmentShader = shader.fragmentShader
      .replace('#include <common>', `#include <common>\n${ARMA_FRAGMENT_PARS}`)
      .replace('#include <color_fragment>', `#include <color_fragment>\n${ARMA_COR}`)
      .replace('#include <roughnessmap_fragment>', `#include <roughnessmap_fragment>\n${ARMA_ASPEREZA}`)
      .replace('#include <metalnessmap_fragment>', `#include <metalnessmap_fragment>\n${ARMA_METAL}`)
      .replace('#include <lights_physical_fragment>', `#include <lights_physical_fragment>\n${ARMA_ANISOTROPIA}`);
  };
  m.customProgramCacheKey = () => `arma:${p.padrao}:${p.recursos.join('+')}`;
  return m;
}

/** Troca o ambiente (o reflexo do set, ou null para o da cena) de um material de zona. */
export function ambienteDoMaterial(m, textura, intensidade = 1) {
  m.envMap = textura;
  m.envMapIntensity = intensidade;
  m.needsUpdate = true;
}
