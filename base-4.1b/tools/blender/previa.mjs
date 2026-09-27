// Prévia do jogo para o Blender (Fase 4.1; docs/phases/phase-4.md, seção 4.1, "Blender"): a malha que o jogo gera de uma
// receita — o mesmo SDF, o mesmo nível de detalhe da bancada e do viewmodel (`perto`) —, os braços de massinha de
// verdade (a malha SDF da mão com o rig, pesos e poses do jogo) presos às âncoras como no viewmodel parado, e a câmera
// de primeira pessoa (viewmodel_fov e offsets padrão). O Blender mostra isso numa coleção que não exporta e o
// `conferir` renderiza a verdade, não as peças de edição.
// Saída: `<saída>.json` (cabeçalho) + `<saída>.bin` (Float32 posições e normais, Uint32 índices, Uint8 massa por
// triângulo, em blocos alinhados a 4 bytes). Tudo no referencial da arma no jogo (+X boca, +Y cima, +Z lado direito).

import { writeFileSync } from 'node:fs';
import { basename } from 'node:path';
import * as THREE from 'three';
import { SdfMesher } from '../../src/clay/sdf/sdfMesher.js';
import { PALETTE } from '../../src/data/palette.js';
import { VIEWMODEL } from '../../src/data/viewmodel.js';
import { ClayArm, buildArmGeometry, prepareArmGeometry } from '../../src/characters/hands/handRig.js';
import { buildWeaponMeshes } from '../../src/weapons/model/weaponModel.js';
import {
  HAND_ANCHOR, elbowTarget, handSides, viewCategory, viewPlacement, viewmodelVerticalFov, weaponNudge,
} from '../../src/weapons/viewmodel/placement.js';

class Blocos {
  constructor() {
    this.partes = [];
    this.bytes = 0;
  }

  /** Guarda um array tipado e devolve {offset, count}; cada bloco começa alinhado a 4 bytes. */
  add(tipado) {
    const offset = this.bytes;
    this.partes.push(Buffer.from(tipado.buffer, tipado.byteOffset, tipado.byteLength));
    this.bytes += tipado.byteLength;
    const sobra = (4 - (this.bytes % 4)) % 4;
    if (sobra) {
      this.partes.push(Buffer.alloc(sobra));
      this.bytes += sobra;
    }
    return { offset, count: tipado.length };
  }

  buffer() {
    return Buffer.concat(this.partes, this.bytes);
  }
}

/** Massa (índice em `materials`) de cada triângulo, pelos grupos contíguos da geometria. */
function massasPorTriangulo(geometry) {
  const out = new Uint8Array(geometry.index.count / 3);
  for (const g of geometry.groups) out.fill(g.materialIndex, g.start / 3, (g.start + g.count) / 3);
  return out;
}

/** Posições dos vértices depois do skinning (na CPU, a mesma conta do shader), no referencial do pai da malha. */
function posicoesSkinned(arm) {
  arm.mesh.updateMatrixWorld(true);
  const pos = arm.mesh.geometry.attributes.position;
  const out = new Float32Array(pos.count * 3);
  const v = new THREE.Vector3();
  for (let i = 0; i < pos.count; i++) {
    v.fromBufferAttribute(pos, i);
    arm.mesh.applyBoneTransform(i, v);
    out[i * 3] = v.x;
    out[i * 3 + 1] = v.y;
    out[i * 3 + 2] = v.z;
  }
  return out;
}

/**
 * Gera a prévia de uma receita (validada pelo gerador) e grava `<saida>.json` + `<saida>.bin`.
 * @param {object} recipe
 * @param {string} saida caminho sem extensão
 * @returns {Promise<{json:string, triangulos:number, ms:number}>}
 */
export async function gerarPrevia(recipe, saida) {
  const t0 = performance.now();
  const sdf = new SdfMesher({ workers: 0 });
  const blocos = new Blocos();
  try {
    const built = await buildWeaponMeshes(recipe, sdf, 'perto');
    const grupos = Object.entries(built.groups).map(([nome, g]) => ({
      nome,
      pivo: g.pivot,
      positions: blocos.add(g.geometry.attributes.position.array),
      normals: blocos.add(g.geometry.attributes.normal.array),
      indices: blocos.add(Uint32Array.from(g.geometry.index.array)),
      massas: blocos.add(massasPorTriangulo(g.geometry)),
    }));
    let triangulos = built.triangles;

    // Os braços e a câmera como no viewmodel parado (padrões do CS: viewmodel_fov 60, offsets 1, 1, −1).
    const category = viewCategory(recipe.id);
    const offset = { x: VIEWMODEL.offset.x.default, y: VIEWMODEL.offset.y.default, z: VIEWMODEL.offset.z.default };
    const place = viewPlacement(category, { offset, nudge: weaponNudge(recipe.id) });
    const inv = place.quaternion.clone().invert();
    const naArma = (p) => p.clone().sub(place.position).applyQuaternion(inv); // câmera → arma
    const maos = [];
    const sides = handSides(recipe);
    if (sides.length) {
      const fonte = await buildArmGeometry(sdf);
      for (const side of sides) {
        const anchor = recipe.anchors[HAND_ANCHOR[side]];
        const geometry = prepareArmGeometry(fonte, side);
        const arm = new ClayArm({ geometry, side, color: PALETTE.terracotta });
        arm.setPose(anchor.pose);
        const quat = new THREE.Quaternion().setFromEuler(new THREE.Euler(...(anchor.rot ?? [0, 0, 0]), 'XYZ'));
        arm.place(new THREE.Vector3(...anchor.pos), quat, naArma(elbowTarget(category, side)));
        const skinned = new THREE.BufferGeometry();
        skinned.setAttribute('position', new THREE.BufferAttribute(posicoesSkinned(arm), 3));
        skinned.setIndex(new THREE.BufferAttribute(Uint32Array.from(geometry.index.array), 1));
        skinned.computeVertexNormals();
        maos.push({
          lado: side,
          ancora: HAND_ANCHOR[side],
          pose: anchor.pose,
          positions: blocos.add(skinned.attributes.position.array),
          normals: blocos.add(skinned.attributes.normal.array),
          indices: blocos.add(skinned.index.array),
        });
        triangulos += skinned.index.count / 3;
        arm.dispose();
        geometry.dispose();
        skinned.dispose();
      }
      fonte.dispose();
    }
    for (const g of Object.values(built.groups)) g.geometry.dispose();

    const olho = new THREE.Vector3().sub(place.position).applyQuaternion(inv);
    const cabecalho = {
      id: recipe.id,
      versao: 1,
      bin: `${basename(saida)}.bin`,
      materiais: built.materials,
      corMao: PALETTE.terracotta,
      grupos,
      maos,
      // Câmera do viewmodel no referencial da arma (olha para −Z, +Y para cima); o quatérnio é [x, y, z, w].
      camera: {
        pos: olho.toArray(),
        quat: inv.toArray(),
        fovY: viewmodelVerticalFov(VIEWMODEL.fov.default),
        near: VIEWMODEL.near,
        far: VIEWMODEL.far,
      },
      triangulos,
      ms: Math.round(performance.now() - t0),
    };
    writeFileSync(`${saida}.bin`, blocos.buffer());
    writeFileSync(`${saida}.json`, JSON.stringify(cabecalho));
    return { json: `${saida}.json`, triangulos, ms: cabecalho.ms };
  } finally {
    sdf.dispose();
  }
}
