// Fila das pegadas (subfase 3.5): as marcas (já no referencial da peça que as recebe) e os passos do esmaecimento na
// ordem do jogo — um passo a cada 1/12 s de simulação (FOOTPRINTS.fade.rate; a pausa não anda o tick e congela) —,
// esvaziada a cada troca de pose do render (EV.POSE) num plano: quantos passos a pose aplica e, por peça, as marcas com
// quantos passos vêm depois de cada uma. Assim a GPU desenha tudo numa passada por peça (src/clay/prints/stampPass.js):
// primeiro o esmaecimento da pose inteira, depois cada marca já esmaecida pelos passos que vieram depois dela — o mesmo
// resultado, em 8 bits, de aplicar a fila item a item. Puro (sem WebGL).

import { FOOTPRINTS } from '../../data/footprints.js';
import { markLife } from './marks.js';

const FADE = Object.freeze({ fade: true });

export class PrintQueue {
  constructor() {
    this.items = [];
    this.acc = 0; // fração de passo do esmaecimento acumulada (em passos)
  }

  /** Itens na fila (marcas e passos do esmaecimento). */
  get size() {
    return this.items.length;
  }

  /** Marca `mark` (no referencial da peça) para a peça de índice `surface`. */
  push(surface, mark) {
    this.items.push({ surface, mark });
  }

  /** Tempo de jogo: um passo do esmaecimento a cada 1/rate s (dt × 12 = 0,1875 por tick: conta exata). */
  advance(dt) {
    this.acc += dt * FOOTPRINTS.fade.rate;
    while (this.acc >= 1) {
      this.acc -= 1;
      this.items.push(FADE);
    }
  }

  /**
   * Esvazia a fila no plano `plan` (createPlan): `fades` = passos do esmaecimento da pose; `stamps[i]` = as marcas da
   * peça i na ordem do jogo, cada uma com `fades` = os passos que vieram depois dela.
   */
  drain(plan) {
    for (const list of plan.stamps) list.length = 0;
    let after = 0;
    for (let i = this.items.length - 1; i >= 0; i--) {
      const it = this.items[i];
      if (it === FADE) after++;
      else {
        it.mark.fades = after;
        plan.stamps[it.surface].push(it.mark);
      }
    }
    for (const list of plan.stamps) list.reverse();
    plan.fades = after;
    this.items.length = 0;
    return plan;
  }

  /** Descarta a fila (limpeza das marcas, GPU reiniciada); o tempo do esmaecimento continua. */
  clear() {
    this.items.length = 0;
  }
}

/** Plano vazio para `surfaces` peças. */
export function createPlan(surfaces) {
  return { fades: 0, stamps: Array.from({ length: surfaces }, () => []) };
}

/**
 * Vida de uma peça (poses até a última marca viva dela sumir) depois de uma pose com `fades` passos e as marcas
 * `stamps` (cada uma com os passos que vieram depois dela). Peça com vida zero e sem marca nova não recebe desenho.
 */
export function surfaceLife(life, fades, stamps) {
  let next = Math.max(0, life - fades);
  for (const m of stamps) next = Math.max(next, markLife(m) - m.fades);
  return next;
}
