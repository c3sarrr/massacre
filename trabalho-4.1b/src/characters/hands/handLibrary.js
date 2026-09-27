// Serviço `handModels` (Fase 4.1; docs/phases/phase-4.md, seção 4.1, "Mãos de 4 dedos"): gera uma vez por sessão a malha
// da mão de massinha e a da braçadeira (SdfMesher: Workers e cache do IndexedDB), prepara os dois lados com os pesos do
// skinning e entrega braços (ClayArm) que só apontam para elas — as geometrias são compartilhadas (marcadas
// `userData.shared`, o dispose das cenas não as toca) e saem só no dispose do serviço. O viewmodel usa agora; os
// bonecos da Fase 5 herdam.

import { ClayArm, buildArmGeometry, buildArmbandGeometry, prepareArmGeometry, prepareArmbandGeometry } from './handRig.js';

const now = () => (globalThis.performance?.now ? globalThis.performance.now() : Date.now());
const SIDES = Object.freeze(['direita', 'esquerda']);

export class HandLibrary {
  #sdf;
  #log;
  #pending = null;
  #built = null;
  #disposed = false;

  /** @param {{sdf:import('../../clay/sdf/sdfMesher.js').SdfMesher, log?:object|null}} deps */
  constructor({ sdf, log = null }) {
    this.#sdf = sdf;
    this.#log = log;
  }

  /**
   * Geometrias prontas dos dois lados (gera na primeira vez; pedidos juntos dividem a mesma promessa).
   * @returns {Promise<{direita:{arm, armband}, esquerda:{arm, armband}, triangles:number, ms:number}>}
   */
  geometries() {
    if (this.#disposed) return Promise.reject(new Error('HandLibrary: já foi descartada'));
    if (!this.#pending) {
      const pending = this.#build();
      pending.catch(() => {
        if (this.#pending === pending) this.#pending = null;
      });
      this.#pending = pending;
    }
    return this.#pending;
  }

  async #build() {
    const t0 = now();
    const [arm, band] = await Promise.all([buildArmGeometry(this.#sdf), buildArmbandGeometry(this.#sdf)]);
    if (this.#disposed) {
      arm.dispose();
      band.dispose();
      throw new Error('HandLibrary: descartada durante a geração');
    }
    const out = { triangles: 0, ms: 0 };
    for (const side of SIDES) {
      const g = { arm: prepareArmGeometry(arm, side), armband: prepareArmbandGeometry(band, side) };
      g.arm.userData.shared = true;
      g.armband.userData.shared = true;
      out[side] = g;
      out.triangles += g.arm.index.count / 3;
    }
    arm.dispose();
    band.dispose();
    out.ms = now() - t0;
    this.#built = out;
    this.#log?.debug(`mãos de massinha: ${Math.round(out.triangles / 2)} triângulos por braço em ${out.ms.toFixed(0)} ms`);
    return out;
  }

  /** Relatório do console (`armas`): estado, triângulos por braço e tempo. */
  report() {
    const b = this.#built;
    return { state: b ? 'pronta' : this.#pending ? 'gerando' : '—', triangles: b ? Math.round(b.triangles / 2) : 0, ms: b ? Math.round(b.ms) : 0 };
  }

  /**
   * Braço novo de um lado, com a massa `color` (a do boneco). O braço é dono só do esqueleto e dos materiais.
   * @param {'direita'|'esquerda'} side
   * @param {{color:string}} options
   */
  async createArm(side, { color }) {
    const g = (await this.geometries())[side];
    if (!g) throw new Error(`lado desconhecido: ${side}`);
    return new ClayArm({ geometry: g.arm, armband: g.armband, side, color });
  }

  dispose() {
    this.#disposed = true;
    const b = this.#built;
    if (b) {
      for (const side of SIDES) {
        b[side].arm.dispose();
        b[side].armband.dispose();
      }
    }
    this.#built = null;
    this.#pending = null;
  }
}
