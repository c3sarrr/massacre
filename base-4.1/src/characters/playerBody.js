// Corpo do jogador no mundo (subfase 3.5; desenho em docs/phases/phase-3.md, seção 3.5): o boneco de referência de
// botas (src/clay/kit/scaleMarker.js) com o squash & stretch (src/characters/squashStretch.js) e a sombra de contato. A
// mola anda por tick (64 Hz); a forma (mola e agachar), a virada (o yaw do olhar) e o alargamento das botas ficam
// congelados a cada pose (EV.POSE, 12/s, "em dois"), enquanto a posição acompanha os pés interpolados a cada quadro (dá
// para mirar nele). Pivô no tornozelo: as botas ficam plantadas e o corpo achata e estica em cima delas. Visível em
// terceira pessoa (debug) e no noclip, como a cápsula do r_colisao; escondido em primeira pessoa. Não projeta sombra no
// mapa de sombra (a da pista é estática, feita uma vez): a sombra de contato é um disco de borda macia no chão embaixo
// dele (BBR32: a sombra diz a altura), que encolhe e clareia com a altura.

import * as THREE from 'three';
import { REFERENCE_DOLL } from '../data/referenceDoll.js';
import { referenceDoll } from '../clay/kit/scaleMarker.js';
import { createRayHit } from '../physics/collisionWorld.js';
import { MOVETYPE } from '../player/movement.js';
import { bodyShape, createSquash, resetSquash, updateSquash } from './squashStretch.js';

const SH = REFERENCE_DOLL.shadow;
const UP = new THREE.Vector3(0, 1, 0);

/** Disco de borda macia: alfa 1 no meio caindo suave até 0 na borda (textura procedural, sem arquivo). */
function contactShadowTexture(size = SH.texture) {
  const data = new Uint8Array(size * size * 4);
  for (let j = 0; j < size; j++) {
    for (let i = 0; i < size; i++) {
      const x = ((i + 0.5) / size) * 2 - 1;
      const y = ((j + 0.5) / size) * 2 - 1;
      const r = Math.min(1, Math.hypot(x, y));
      const t = 1 - r;
      const a = t * t * (3 - 2 * t); // smoothstep(1, 0, r)
      data[(j * size + i) * 4 + 3] = Math.round(a * a * 255);
    }
  }
  const tex = new THREE.DataTexture(data, size, size, THREE.RGBAFormat);
  tex.name = 'massacre.sombra-de-contato';
  tex.magFilter = THREE.LinearFilter;
  tex.minFilter = THREE.LinearFilter;
  tex.needsUpdate = true;
  return tex;
}

export class PlayerBody {
  /**
   * @param {{scene: THREE.Scene, world: import('../physics/collisionWorld.js').CollisionWorld, color?: string,
   *   seed?: string}} opts
   */
  constructor({ scene, world, color, seed = 'jogador' }) {
    this.world = world;
    const doll = referenceDoll(REFERENCE_DOLL.height, { color, seed });
    this.root = new THREE.Group();
    this.root.name = 'corpo-do-jogador';
    this.pivot = new THREE.Group();
    this.pivot.position.y = doll.ankle;
    for (const mesh of doll.upper) {
      mesh.position.y = -doll.ankle;
      this.pivot.add(mesh);
    }
    this.boots = doll.boots;
    this.root.add(this.boots, this.pivot);
    this.root.traverse((o) => {
      o.castShadow = false;
    });
    this.shadowMap = contactShadowTexture();
    this.shadow = new THREE.Mesh(
      new THREE.PlaneGeometry(1, 1).rotateX(-Math.PI / 2),
      new THREE.MeshBasicMaterial({
        color: 0x000000, map: this.shadowMap, transparent: true, depthWrite: false, opacity: SH.opacity,
        polygonOffset: true, polygonOffsetFactor: -2, polygonOffsetUnits: -2,
      }),
    );
    this.shadow.name = 'sombra-de-contato';
    this.shadow.castShadow = false;
    this.shadow.receiveShadow = false;
    this.root.visible = false;
    this.shadow.visible = false;
    scene.add(this.root, this.shadow);
    this.squash = createSquash();
    this.shape = { sy: 1, sxz: 1, widen: 0 }; // forma mostrada (a da última pose)
    this.yaw = 0; // virada mostrada
    this._hit = createRayHit();
    this._q = new THREE.Quaternion();
  }

  /** Um tick da mola (depois do tick do jogador, com os eventos dele). */
  tick(pawn, dt) {
    updateSquash(this.squash, pawn.state, pawn.env.events, pawn.vitals.alive, dt);
  }

  /** Volta ao jogo: a mola zera (a forma aparece normal já na próxima pose). */
  reset() {
    resetSquash(this.squash);
  }

  /** Troca de pose (EV.POSE): congela a forma, a virada e as botas no valor da mola de agora. */
  onPose(pawn) {
    const sh = bodyShape(this.squash, pawn.state.duckAmount, this.shape);
    this.yaw = pawn.yaw;
    this.pivot.scale.set(sh.sxz, sh.sy, sh.sxz);
    this.boots.scale.set(1 + sh.widen, 1, 1);
    this.root.rotation.y = this.yaw + Math.PI; // o boneco olha para +Z; o jogador, para −Z no yaw 0
  }

  /** Um quadro: pés interpolados e a sombra de contato no chão embaixo (visível só fora da primeira pessoa). */
  update(pawn, alpha) {
    const visible = pawn.thirdPerson || pawn.state.moveType === MOVETYPE.NOCLIP;
    this.root.visible = visible;
    if (!visible) {
      this.shadow.visible = false;
      return;
    }
    const s = pawn.state;
    const p = pawn.prevOrigin;
    const x = p.x + (s.origin.x - p.x) * alpha;
    const y = p.y + (s.origin.y - p.y) * alpha;
    const z = p.z + (s.origin.z - p.z) * alpha;
    this.root.position.set(x, y, z);
    const hit = this._hit;
    if (!this.world.raycast(x, y + 1, z, 0, -1, 0, SH.probe, hit)) {
      this.shadow.visible = false;
      return;
    }
    const k = Math.min(1, Math.max(0, (y - hit.point.y) / SH.fadeHeight));
    const size = SH.diameter * (1 + (SH.minScale - 1) * k);
    const n = hit.normal.y < 0 ? hit.normal.negate() : hit.normal;
    this.shadow.visible = true;
    this.shadow.position.copy(hit.point).addScaledVector(n, SH.lift);
    this.shadow.quaternion.copy(this._q.setFromUnitVectors(UP, n));
    this.shadow.scale.set(size, 1, size);
    this.shadow.material.opacity = SH.opacity * (1 + (SH.minOpacity - 1) * k);
  }

  dispose() {
    this.root.removeFromParent();
    this.shadow.removeFromParent();
    this.root.traverse((o) => {
      if (!o.isMesh) return;
      o.geometry.dispose();
      o.material.dispose();
    });
    this.shadow.geometry.dispose();
    this.shadow.material.dispose();
    this.shadowMap.dispose();
  }
}
