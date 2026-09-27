// Sistema das pegadas (subfase 3.5; desenho em docs/phases/phase-3.md, seção 3.5; números em src/data/footprints.js):
// liga as peças de chão de massinha que o mapa declara (`printSurfaces`) aos mapas de pegadas delas e, a cada tick do
// jogador, põe na fila as marcas do tick (src/clay/prints/marks.js: passo, pouso, pulo, sulcos e montinho do slide) nas
// peças onde elas caem, com os passos do esmaecimento no tempo do jogo. Na troca de pose do render (EV.POSE, junto com
// o boil) a fila vira desenho: uma chamada por peça com marca nova ou viva (src/clay/prints/stampPass.js); peça sem
// marca viva não recebe desenho. GPU reiniciada (EV.RENDER_CONTEXT) limpa as marcas; `dispose` libera os alvos.
// Console: `pegadas` e `pegadas limpar` (src/debug/commands.js).

import { EV } from '../../core/events.js';
import { FOOTPRINTS } from '../../data/footprints.js';
import { MOVETYPE } from '../../player/movement.js';
import { createPrintTrack, resetPrintTrack, tickMarks } from './marks.js';
import { PrintQueue, createPlan, surfaceLife } from './printQueue.js';
import { PrintSurface } from './surface.js';
import { StampPass } from './stampPass.js';

/** Esmaecimento que zera qualquer mapa (o brilho, o canal mais rápido, também). */
const CLEAR_FADES = 255;

export class PrintSystem {
  /**
   * @param {{render: import('../../render/renderSystem.js').RenderSystem,
   *   events: import('../../core/events.js').EventBus,
   *   surfaces: Array<{id: string, mesh: import('three').Mesh, material: import('../ClayMaterial.js').ClayMaterial,
   *   width: number, depth: number, top: number}>}} opts
   */
  constructor({ render, events, surfaces }) {
    this.render = render;
    this.surfaces = surfaces.map((decl) => new PrintSurface(decl));
    this.queue = new PrintQueue();
    this.plan = createPlan(this.surfaces.length);
    this.pass = new StampPass();
    this.track = createPrintTrack();
    this._marks = [];
    this._local = {};
    this.counts = { marks: 0, draws: 0 }; // marcas postas na fila e chamadas de render desde a montagem
    this._off = events.on(EV.RENDER_CONTEXT, ({ lost }) => {
      if (!lost) this.clear();
    });
    if (!render.contextLost) this.pass.compile(render.renderer);
    this.clear();
  }

  /**
   * Um tick, depois do tick do jogador (`pawn`): o tempo do esmaecimento anda e as marcas do tick entram na fila de
   * cada peça em que caem. Morto ou no noclip, nada marca.
   */
  tick(pawn, dt) {
    this.queue.advance(dt);
    const s = pawn.state;
    if (!pawn.vitals.alive || s.moveType === MOVETYPE.NOCLIP) {
      resetPrintTrack(this.track);
      return;
    }
    const marks = tickMarks(this.track, s, pawn.prevOrigin, pawn.env.events, pawn.yaw, this._marks);
    for (const m of marks) {
      for (let i = 0; i < this.surfaces.length; i++) {
        const local = this.surfaces[i].place(m, this._local);
        if (!local) continue;
        this.queue.push(i, { ...local });
        this.counts.marks++;
      }
    }
  }

  /** Volta ao jogo e teleporte: o sulco do slide não continua de onde parou. */
  reset() {
    resetPrintTrack(this.track);
  }

  /** Troca de pose (EV.POSE): a fila vira desenho, uma chamada por peça com marca nova ou viva. */
  onPose() {
    const plan = this.queue.drain(this.plan);
    if (this.render.contextLost) return;
    const renderer = this.render.renderer;
    for (let i = 0; i < this.surfaces.length; i++) {
      const surface = this.surfaces[i];
      const stamps = plan.stamps[i];
      if (!stamps.length && surface.life <= 0) continue;
      const fades = surface.life > 0 ? plan.fades : 0;
      this.pass.draw(renderer, surface.target, surface.width, surface.depth, fades, stamps);
      surface.life = surfaceLife(surface.life, plan.fades, stamps);
      this.counts.draws++;
    }
  }

  /** Apaga todas as marcas (e a fila): o mapa de cada peça volta a zero, com os mipmaps. */
  clear() {
    this.queue.clear();
    resetPrintTrack(this.track);
    for (const surface of this.surfaces) surface.life = 0;
    if (this.render.contextLost) return;
    for (const surface of this.surfaces) {
      this.pass.draw(this.render.renderer, surface.target, surface.width, surface.depth, CLEAR_FADES, []);
    }
  }

  /**
   * Para o console: peças, peças com marca viva (e os segundos de jogo até a última sumir), itens na fila, marcas e
   * desenhos desde a montagem e a memória dos mapas (com os mipmaps).
   */
  info() {
    const live = this.surfaces.filter((s) => s.life > 0);
    const bytes = this.surfaces.reduce((sum, s) => sum + (s.size.width * s.size.height * 4 * 4) / 3, 0);
    return {
      surfaces: this.surfaces.length,
      live: live.map((s) => ({ id: s.id, seconds: s.life / FOOTPRINTS.fade.rate })),
      queue: this.queue.size,
      marks: this.counts.marks,
      draws: this.counts.draws,
      megabytes: bytes / (1024 * 1024),
    };
  }

  dispose() {
    this._off();
    this.pass.dispose();
    for (const surface of this.surfaces) surface.dispose();
    this.surfaces = [];
  }
}
