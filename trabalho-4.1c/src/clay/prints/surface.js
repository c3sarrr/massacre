// Superfície de pegadas (subfase 3.5): uma peça de chão de massinha que o mapa declara (`printSurfaces`: id, malha,
// material, largura, profundidade e o topo no y do objeto) com o seu mapa de pegadas — um alvo de render RGBA8 com
// mipmaps no referencial da peça (o XZ do objeto, centrado): 4 texels/u com teto de 1024 por lado (a peça maior perde
// densidade por igual nos dois eixos) — ligado ao ClayMaterial dela (camada CLAY_PRINTS, src/clay/clayImprint.js).
// Uma marca cai na peça quando o retângulo dela encosta no da peça e o topo da peça está a até 4 u dos pés; o que passa
// da borda sai cortado. A peça é estática: a inversa da matriz de mundo é tirada uma vez.

import * as THREE from 'three';
import { FOOTPRINTS } from '../../data/footprints.js';
import { markBounds, toLocal } from './marks.js';

const FP = FOOTPRINTS;
const _bounds = [0, 0, 0, 0];

/** Tamanho do mapa de pegadas de uma peça de `width` × `depth` u: {width, height} em texels e os texels por u. */
export function surfaceSize(width, depth) {
  const texelsPerUnit = Math.min(FP.texelsPerUnit, FP.maxTexels / Math.max(width, depth));
  return {
    width: Math.max(1, Math.min(FP.maxTexels, Math.round(width * texelsPerUnit))),
    height: Math.max(1, Math.min(FP.maxTexels, Math.round(depth * texelsPerUnit))),
    texelsPerUnit,
  };
}

/**
 * A marca `m` (no mundo) no referencial da peça {inverse, width, depth, top} se ela cair ali: o y dos pés a até
 * `topTolerance` do topo e o retângulo da marca encostando no da peça. Senão null. Escreve em `out`.
 */
export function placeMark(surface, m, out = {}) {
  const l = toLocal(m, surface.inverse, out);
  if (Math.abs(l.y - surface.top) > FP.topTolerance) return null;
  const b = markBounds(l, _bounds);
  const hw = surface.width / 2;
  const hd = surface.depth / 2;
  if (b[2] < -hw || b[0] > hw || b[3] < -hd || b[1] > hd) return null;
  return l;
}

export class PrintSurface {
  /**
   * @param {{id: string, mesh: THREE.Mesh, material: import('../ClayMaterial.js').ClayMaterial, width: number,
   *   depth: number, top: number}} decl
   */
  constructor({ id, mesh, material, width, depth, top }) {
    this.id = id;
    this.mesh = mesh;
    this.material = material;
    this.width = width;
    this.depth = depth;
    this.top = top;
    // Peça de matriz fixa (matrixAutoUpdate desligado): a matriz de mundo é refeita à força uma vez.
    mesh.updateWorldMatrix(true, false, true);
    this.inverse = mesh.matrixWorld.clone().invert().elements.slice();
    this.size = surfaceSize(width, depth);
    this.target = new THREE.WebGLRenderTarget(this.size.width, this.size.height, {
      type: THREE.UnsignedByteType, format: THREE.RGBAFormat, depthBuffer: false, stencilBuffer: false,
      generateMipmaps: true, minFilter: THREE.LinearMipmapLinearFilter, magFilter: THREE.LinearFilter,
      wrapS: THREE.ClampToEdgeWrapping, wrapT: THREE.ClampToEdgeWrapping, colorSpace: THREE.NoColorSpace,
    });
    this.target.texture.name = `massacre.pegadas.${id}`;
    this.life = 0; // poses até a última marca viva sumir (0: mapa limpo, nada a desenhar)
    material.setPrints({
      map: this.target.texture, rect: [-width / 2, -depth / 2, width, depth], depth: FP.depth, lip: FP.lip,
    });
  }

  /** A marca no referencial desta peça, se cair nela (placeMark). */
  place(m, out) {
    return placeMark(this, m, out);
  }

  dispose() {
    this.material.setPrints(null);
    this.target.dispose();
  }
}
