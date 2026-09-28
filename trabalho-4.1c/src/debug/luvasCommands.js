// Comandos de console das luvas (Fase 4.1b; desenho em docs/superpowers/specs/2026-09-26-4.1b-luvas-e-empunhadura-
// design.md, seção 7.5; plano, Tarefa 11):
//  - `luvas`: o estado da carga, os triângulos de cada luva e do antebraço de massinha, a marca do rig, e na mão a
//    facção, se a marca da arma bate com a das luvas e os ângulos de cada pulso (com os avisos dos limites da AAOS);
//  - `luvas_contato`: a luva deformada de verdade (as posições do modelo das dobras) contra a malha da arma na mão
//    (numa BVH, guardada por instância), sonda por sonda com a medida do Blender ao lado, e a penetração máxima de cada
//    luva — a diferença tem de ficar em LIMITES_DA_PEGA.contatoJogoMM (0,05 mm).

import { LIMITES_DA_PEGA, LUVAS } from '../data/luvas.js';
import { bvhDaArma, contatoDasLuvas } from '../characters/hands/luvasContato.js';

const LADOS = Object.freeze([['direita', 'd'], ['esquerda', 'e']]);
// (sem o sinal quando arredonda para zero: "0,00", não "−0,00")
const num = (v, casas) => (Math.abs(v) < 0.5 * 10 ** -casas ? 0 : v).toFixed(casas).replace('.', ',').replace(/^-/, '−');
/** mm com duas casas (o jeito do console: vírgula e o sinal de menos). */
export const emMM = (v) => `${num(v, 2)} mm`;
const graus = (v) => `${num(v, 1)}°`;

/**
 * As linhas do `luvas_contato` a partir do resultado de cada lado (contatoDasLuvas) e do relatório da arma.
 * @param {string} id @param {{direita?:object, esquerda?:object}} porLado @param {object|null} [empunhadura] a seção do
 *   relatório do Blender (a penetração dele)
 */
export function formatarContato(id, porLado, empunhadura = null) {
  const lim = LIMITES_DA_PEGA.contatoJogoMM;
  const linhas = [`luvas_contato ${id} (a diferença para o Blender até ${emMM(lim)}; entra até ${emMM(LIMITES_DA_PEGA.penetracaoMM)})`];
  for (const [side, lado] of LADOS) {
    const r = porLado[side];
    if (!r) continue;
    const blender = empunhadura?.[lado]?.penetracaoMM;
    const ok = r.piorDiferencaMM <= lim && r.penetracaoMM <= LIMITES_DA_PEGA.penetracaoMM;
    linhas.push(`${side}: entra ${emMM(r.penetracaoMM)}${blender !== undefined ? ` (Blender ${emMM(blender)})` : ''} · pior diferença ${emMM(r.piorDiferencaMM)} ${ok ? '✓' : '✗'}`);
    for (const s of r.sondas) {
      linhas.push(`  ${s.contato.padEnd(18)} jogo ${emMM(s.jogoMM).padStart(10)} · Blender ${emMM(s.blenderMM).padStart(10)} · diferença ${emMM(s.diferencaMM)}`);
    }
  }
  return linhas.join('\n');
}

/**
 * As linhas do `luvas`.
 * @param {{relatorio:()=>object}} luvasModels @param {object|null} vm o viewmodel (null fora da partida)
 */
export function relatorioDasLuvas(luvasModels, vm) {
  const r = luvasModels.relatorio();
  const mil = (n) => n.toLocaleString('pt-BR');
  const linhas = [];
  if (r.estado === 'erro') linhas.push(`luvas: erro — ${r.erro}`);
  else if (r.estado !== 'pronta') linhas.push(`luvas: ${r.estado === '—' ? 'não carregadas (entre num mapa)' : r.estado}`);
  else {
    linhas.push(`luvas: pronta · ${mil(r.triangulos.d)} + ${mil(r.triangulos.e)} triângulos · antebraço de massinha ${r.antebraco ? mil(r.antebraco) : 'não gerado'} · carregadas em ${r.ms} ms · ${r.bracos} braço(s) na cena`);
    linhas.push(`marca do rig: d ${r.marca.d.slice(0, 12)}… · e ${r.marca.e.slice(0, 12)}…`);
  }
  const st = vm?.status?.();
  if (!st?.item) {
    linhas.push('na mão: nada');
  } else if (st.bracos !== 'luvas') {
    const pega = vm.info?.pega;
    linhas.push(`na mão: ${st.item} com ${st.bracos === 'massinha' ? 'os braços de massinha' : 'nenhum braço'}${pega ? '' : ' (a arma não tem a pega das luvas)'}`);
    if (pega && r.marca && (pega.marca.d !== r.marca.d || pega.marca.e !== r.marca.e)) {
      linhas.push('  a marca do rig da arma não é a das luvas: construa a arma de novo no Blender');
    }
  } else {
    const pega = vm.info.pega;
    const bate = r.marca && pega.marca.d === r.marca.d && pega.marca.e === r.marca.e;
    linhas.push(`na mão: ${st.item} com as luvas · ${LUVAS.pinturas[st.faccao]?.nome ?? st.faccao} · a marca da arma ${bate ? 'bate com a das luvas ✓' : 'NÃO bate com a das luvas ✗'}`);
    for (const [side] of LADOS) {
      const b = vm.gloves.bracos[side];
      if (!b) continue;
      const a = b.angulos;
      const avisos = st.avisos?.[side] ?? [];
      linhas.push(`  ${side}: pulso ${graus(a.flexao)} de flexão, ${graus(a.desvio)} de desvio, antebraço ${graus(a.pronacao)} de pronação${avisos.length ? ` — ${avisos.join('; ')}` : ''}`);
    }
  }
  return linhas.join('\n');
}

/** Registra `luvas` e `luvas_contato` no console. */
export function registerLuvasCommands(con, s, { matchState }) {
  const bvhs = new WeakMap(); // instância da arma → BVH (refeita quando a instância muda)
  con.register({
    name: 'luvas',
    usage: '',
    help: 'estado das luvas: carga, triângulos, marca do rig e, na mão, a facção, a marca da arma e os pulsos',
    run: () => relatorioDasLuvas(s.luvasModels, matchState()?.viewmodel ?? null),
  });
  con.register({
    name: 'luvas_contato',
    usage: '',
    help: 'mede no jogo o contato das luvas com a arma na mão (a malha deformada de verdade) e compara com o Blender',
    run: () => {
      const vm = matchState()?.viewmodel;
      const info = vm?.info;
      if (!info?.pega || vm.status().bracos !== 'luvas' || !vm.gloves?.prontos) {
        return 'luvas_contato: segure em primeira pessoa uma arma com a pega das luvas (give ak47)';
      }
      let bvh = bvhs.get(vm.weapon);
      if (!bvh) {
        bvh = bvhDaArma(vm.weapon);
        bvhs.set(vm.weapon, bvh);
      }
      const porLado = {};
      for (const [side, lado] of LADOS) {
        porLado[side] = contatoDasLuvas({ bvh, raizDaArma: vm.weapon, braco: vm.gloves.bracos[side], sondas: info.pega.sondas[lado] });
      }
      return formatarContato(info.id, porLado, info.report?.empunhadura ?? null);
    },
  });
}
