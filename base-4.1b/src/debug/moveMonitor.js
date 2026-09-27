// Monitor do movimento (subfase 3.5, aceite da Fase 3; `cl_monitor 1` no console, chave transitória debug.monitor;
// números em src/data/sandbox.js, MONITOR): a cada tick confere se a cápsula cabe onde está (canOccupy com 0,05 u de
// folga; a profundidade pelo contato mais fundo), se ficou presa e se caiu abaixo do chão do estúdio (o fundo do mapa);
// a cada quadro guarda o tempo dele (FPS médio e 1% low pela estatística pura do presetSweep); a cada segundo, a
// memória (geometrias, texturas, programas e o heap do JS); e o tempo em cada estação (o lote do mapa sob os pés).
// Painel na tela; `monitor` no console imprime o relatório e `monitor zerar` recomeça. O registro (MonitorLog) é puro:
// a varredura do Node (tests/pistaSim.js, tools/phase3-acceptance.mjs) faz as mesmas checagens com ele.

import { HULL } from '../data/movement.js';
import { MONITOR } from '../data/sandbox.js';
import { createContact } from '../physics/collisionWorld.js';
import { MOVETYPE } from '../player/movement.js';
import { h } from '../ui/dom.js';
import { summarizeFrames } from './presetSweep.js';

const OUTSIDE = 0; // "fora dos lotes": praça, caminhos e o que não é estação

/** Mínimo, máximo, primeiro e último de um campo das amostras de memória. */
function spread(samples, key) {
  const values = samples.map((m) => m[key]).filter((v) => typeof v === 'number');
  if (!values.length) return null;
  return { first: values[0], last: values.at(-1), min: Math.min(...values), max: Math.max(...values) };
}

export class MonitorLog {
  /**
   * @param {{world: import('../physics/collisionWorld.js').CollisionWorld, floorY?: number,
   *   lots?: Array<{number: number, label?: string, x: number[], z: number[]}>}} opts
   */
  constructor({ world, floorY = -Infinity, lots = [] }) {
    this.world = world;
    this.floorY = floorY;
    this.lots = lots;
    this._contact = createContact();
    this.reset();
  }

  reset() {
    this.time = 0; // s de jogo registrados
    this.ticks = 0;
    this.checked = 0; // ticks conferidos (fora do noclip)
    this.penetrations = 0;
    this.maxDepth = 0; // u: a penetração mais funda
    this.stuck = 0;
    this.below = 0;
    this.problems = []; // os primeiros, com o tick e o lugar
    this.frames = []; // ms de cada quadro
    this.frameMs = 0; // soma deles (a média da sessão sem percorrer a lista)
    this.memory = []; // uma amostra por segundo
    this.lotTime = new Map(); // número do lote (0 = fora) → s
  }

  /** Número do lote sob (x, z), ou 0 fora de todos. */
  lotAt(x, z) {
    for (const lot of this.lots) {
      if (x >= lot.x[0] && x <= lot.x[1] && z >= lot.z[0] && z <= lot.z[1]) return lot.number;
    }
    return OUTSIDE;
  }

  /** Um tick de jogo com o estado de movimento `s`; no noclip não confere (atravessa tudo de propósito). */
  tick(s, dt) {
    this.time += dt;
    this.ticks++;
    const o = s.origin;
    const lot = this.lotAt(o.x, o.z);
    this.lotTime.set(lot, (this.lotTime.get(lot) ?? 0) + dt);
    if (s.moveType === MOVETYPE.NOCLIP) return;
    this.checked++;
    if (!this.world.canOccupy(o.x, o.y, o.z, HULL.radius, s.height, MONITOR.tolerance)) {
      const c = this._contact;
      this.world.deepestContact(o.x, o.y, o.z, HULL.radius, s.height, HULL.radius, c);
      const depth = c.pierced ? HULL.radius + c.pierceDepth : HULL.radius - c.distance;
      this.penetrations++;
      this.maxDepth = Math.max(this.maxDepth, depth);
      this.#problem('penetração', o, depth);
    }
    if (s.stuck) {
      this.stuck++;
      this.#problem('preso', o);
    }
    if (o.y < this.floorY - MONITOR.floorSlack) {
      this.below++;
      this.#problem('abaixo do chão do estúdio', o);
    }
  }

  #problem(kind, o, depth = null) {
    if (this.problems.length >= MONITOR.keepProblems) return;
    this.problems.push({ kind, tick: this.ticks, at: [o.x, o.y, o.z], depth });
  }

  /** Nenhuma penetração, nenhum tick preso, nenhuma queda para fora. */
  get ok() {
    return this.penetrations + this.stuck + this.below === 0;
  }

  /** Um quadro do render (ms). */
  frame(dtMs) {
    if (dtMs <= 0) return;
    this.frames.push(dtMs);
    this.frameMs += dtMs;
  }

  /** FPS médio da sessão (sem ordenar nada: o painel pede algumas vezes por segundo), ou null sem quadros. */
  sessionFps() {
    return this.frames.length ? (this.frames.length * 1000) / this.frameMs : null;
  }

  /** Amostra de memória {geometries, textures, programs, heapMB} no tempo de jogo de agora. */
  sample(sample) {
    this.memory.push({ time: this.time, ...sample });
  }

  /** Estatística dos quadros dos últimos `seconds` s (null: a sessão inteira). */
  fps(seconds = null) {
    let frames = this.frames;
    if (seconds !== null) {
      let sum = 0;
      let i = frames.length;
      while (i > 0 && sum < seconds * 1000) sum += frames[--i];
      frames = frames.slice(i);
    }
    return summarizeFrames(frames.map((dtMs) => ({ dtMs })));
  }

  /** Relatório: minutos, checagens, FPS da sessão, memória (primeira, última, mín. e máx.) e o tempo por estação. */
  report() {
    const labels = new Map(this.lots.map((l) => [l.number, l.label ?? `estação ${l.number}`]));
    const lots = [...this.lotTime.entries()]
      .sort((a, b) => (a[0] || 99) - (b[0] || 99))
      .map(([number, seconds]) => ({ number, label: number ? labels.get(number) : 'fora dos lotes', seconds }));
    return {
      minutes: this.time / 60,
      ticks: this.ticks,
      checked: this.checked,
      penetrations: this.penetrations,
      maxDepth: this.maxDepth,
      stuck: this.stuck,
      below: this.below,
      ok: this.ok,
      problems: this.problems,
      fps: this.fps(),
      memory: {
        samples: this.memory.length,
        geometries: spread(this.memory, 'geometries'),
        textures: spread(this.memory, 'textures'),
        programs: spread(this.memory, 'programs'),
        heapMB: spread(this.memory, 'heapMB'),
      },
      lots,
    };
  }
}

const n1 = (v) => (v === null || v === undefined ? 'n/d' : v.toFixed(1));
const at = (p) => p.at.map((v) => v.toFixed(1)).join(' ');

/** Primeira → última (mínimo, máximo) de um campo de memória. */
function span(s, d = 0) {
  if (!s) return 'n/d';
  return `${s.first.toFixed(d)} → ${s.last.toFixed(d)} (mín. ${s.min.toFixed(d)}, máx. ${s.max.toFixed(d)})`;
}

/** Um problema guardado: tick, tipo, lugar e (penetração) a profundidade. */
function problemLine(p) {
  return `  tick ${p.tick}: ${p.kind} em ${at(p)}${p.depth === null ? '' : ` (${p.depth.toFixed(3)} u)`}`;
}

/** Relatório em texto (console, PROGRESS.md). */
export function formatMonitorReport(r) {
  const width = Math.max(0, ...r.lots.map((l) => l.label.length));
  const lines = [
    `monitor · ${r.minutes.toFixed(1)} min de jogo · ${r.ticks} ticks (${r.checked} conferidos fora do noclip)`,
    `penetração ${r.penetrations}${r.penetrations ? ` (máx. ${r.maxDepth.toFixed(3)} u)` : ''} · preso ${r.stuck}`
      + ` · abaixo do chão ${r.below} → ${r.ok ? 'OK' : 'FALHOU'}`,
    ...r.problems.map(problemLine),
    `FPS ${n1(r.fps.fps)} · 1% low ${n1(r.fps.low1Fps)} · quadro ${n1(r.fps.frameMs)} ms · p95 ${n1(r.fps.p95Ms)} ms`
      + ` (${r.fps.frames} quadros)`,
    `memória (${r.memory.samples} amostras): geometrias ${span(r.memory.geometries)}`
      + ` · texturas ${span(r.memory.textures)} · programas ${span(r.memory.programs)}`
      + ` · heap ${span(r.memory.heapMB, 1)} MB`,
    'estações:',
    ...r.lots.map((l) => {
      const number = l.number ? String(l.number).padStart(2) : ' —';
      return `  ${number} ${l.label.padEnd(width)} ${l.seconds.toFixed(0).padStart(5)} s`;
    }),
  ];
  return lines.join('\n');
}

/** Amostra de memória do render e do heap do JS (o heap só no Chromium). */
export function memorySample(render) {
  const r = render.stats();
  const heap = globalThis.performance?.memory?.usedJSHeapSize;
  return { geometries: r.geometries, textures: r.textures, programs: r.programs, heapMB: heap ? heap / 1048576 : null };
}

export class MoveMonitor {
  /**
   * @param {{root: HTMLElement, world: import('../physics/collisionWorld.js').CollisionWorld, floorY: number,
   *   lots?: object[], stations?: Array<{number: number, label: string}>}} opts
   */
  constructor({ root, world, floorY, lots = [], stations = [] }) {
    const label = new Map(stations.map((s) => [s.number, s.label]));
    this.log = new MonitorLog({ world, floorY, lots: lots.map((l) => ({ ...l, label: label.get(l.number) })) });
    this.text = h('pre.dbg-monitor-text');
    this.el = h('div.dbg-monitor', { hidden: true, 'aria-hidden': 'true' }, this.text);
    root.append(this.el);
    this.visible = false;
    this.memoryAcc = 0;
    this.panelAcc = 0;
  }

  /** Liga (grava e mostra) ou desliga (para de gravar; o registro fica para o `monitor`). */
  setVisible(visible) {
    this.visible = visible;
    this.el.hidden = !visible;
    this.panelAcc = Infinity;
  }

  /** Um tick do jogo (depois do tick do jogador). */
  tick(pawn, dt) {
    if (this.visible) this.log.tick(pawn.state, dt);
  }

  /** Um quadro: o tempo dele, a memória a cada segundo e o texto do painel algumas vezes por segundo. */
  frame(dt, render, pawn) {
    if (!this.visible) return;
    this.log.frame(dt * 1000);
    this.memoryAcc += dt;
    if (this.memoryAcc >= MONITOR.memoryEvery) {
      this.memoryAcc = 0;
      this.log.sample(memorySample(render));
    }
    this.panelAcc += dt;
    if (this.panelAcc < 1 / MONITOR.panelHz) return;
    this.panelAcc = 0;
    const l = this.log;
    // A janela do painel é curta; o 1% low da sessão ordena todos os quadros e fica só no relatório (`monitor`).
    const now = l.fps(MONITOR.window);
    const mem = l.memory.at(-1);
    const lot = l.lotAt(pawn.state.origin.x, pawn.state.origin.z);
    const here = lot ? `${lot} · ${l.lots.find((x) => x.number === lot)?.label ?? ''}` : 'fora dos lotes';
    this.text.textContent = [
      `MONITOR  ${(l.time / 60).toFixed(1)} min · ${l.checked} ticks conferidos · ${l.ok ? 'OK' : 'PROBLEMA'}`,
      `cápsula  penetração ${l.penetrations} (máx. ${l.maxDepth.toFixed(3)} u) · preso ${l.stuck} · fora ${l.below}`,
      `FPS      agora ${n1(now.fps)} (1% ${n1(now.low1Fps)}) · média da sessão ${n1(l.sessionFps())}`,
      mem ? `memória  geo ${mem.geometries} · tex ${mem.textures} · prog ${mem.programs} · heap ${n1(mem.heapMB)} MB`
        : 'memória  —',
      `estação  ${here} · ${((l.lotTime.get(lot) ?? 0) / 60).toFixed(1)} min aqui`,
    ].join('\n');
  }

  report() {
    return formatMonitorReport(this.log.report());
  }

  reset() {
    this.log.reset();
    this.memoryAcc = 0;
    this.panelAcc = Infinity;
  }

  dispose() {
    this.el.remove();
  }
}
