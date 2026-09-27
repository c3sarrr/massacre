// A pega das luvas na saída de uma arma realista (Fase 4.1b; desenho, seções 6.3 e 6.4; plano, Tarefa 7): a seção
// `empunhadura` do relatório do Blender (a penetração da luva na arma e a distância de cada contato da regra, nos dois
// braços; os lados dos dedos) e a marca do rig, igual no relatório, no .glb da arma e no luvas.glb (D4). O que o .glb
// precisa ter (os nós e o clipe) é conferido por `lerPega` (src/characters/hands/pega.js), que lança.
// Os lados (regra do usuário de 2026-09-27): na mão da frente (`frente` no relatório) só o polegar de um lado da arma e
// o indicador, o médio, o anelar e o mínimo do outro — `lados.polegarMM` e `lados.dedosMM` são a posição da polpa de
// cada um no eixo do lado do polegar (mm, a partir do plano do meio da arma); a do polegar tem de passar de +ladoMM e a
// de cada dedo de −ladoMM. A mão do gatilho, quando traz os lados (o polegar cruzando o punho), passa pela mesma conta.
import { DEDOS_DA_FRENTE, LIMITES_DA_PEGA } from '../../src/data/luvas.js';

const fmt = (v) => v.toFixed(2).replace('.', ',');

/** Os problemas dos lados de um braço: o polegar do lado dele e cada dedo (os `exigidos`, se vierem) do outro. */
function problemasDosLados(lado, lados, exigidos) {
  const m = LIMITES_DA_PEGA.ladoMM;
  const problemas = [];
  if (!(lados.polegarMM >= m)) {
    problemas.push(`empunhadura ${lado}: o polegar a ${fmt(lados.polegarMM ?? NaN)} mm do meio da arma — tem de ficar do `
      + `lado dele, a pelo menos ${m} mm, e não do lado dos dedos`);
  }
  const dedos = lados.dedosMM ?? {};
  for (const d of exigidos ?? []) {
    if (!(d in dedos)) problemas.push(`empunhadura ${lado}: sem o lado do ${d} (a mão da frente conta os quatro dedos)`);
  }
  for (const [d, mm] of Object.entries(dedos)) {
    if (!(mm <= -m)) {
      problemas.push(`empunhadura ${lado}: o ${d} a ${fmt(mm)} mm do meio da arma, no lado do polegar ou no meio — tem de `
        + `passar para o outro lado, a pelo menos ${m} mm`);
    }
  }
  return problemas;
}

/**
 * Os problemas da pega: o relatório sem a seção, a penetração acima de 0,3 mm ou um contato acima de 1 mm num braço, a
 * mão da frente sem só o polegar de um lado e os quatro dedos do outro, a marca do .glb diferente da do relatório ou da
 * das luvas (`marcaLuvas`, a do luvas.glb; null se ainda não há luvas).
 * @returns {string[]}
 */
export function validarPega(relatorio, pega, marcaLuvas) {
  const e = relatorio?.empunhadura;
  if (!e) return ['o relatório sem a seção empunhadura (a pega das luvas; construa a arma de novo)'];
  const problemas = [];
  if (e.frente !== 'd' && e.frente !== 'e') {
    problemas.push('empunhadura: o relatório não diz qual é a mão da frente (construa a arma de novo)');
  } else if (!e[e.frente]?.lados) {
    problemas.push(`empunhadura ${e.frente}: a mão da frente sem a conferência dos lados (o polegar de um lado e os `
      + 'quatro dedos do outro; construa a arma de novo)');
  }
  for (const lado of ['d', 'e']) {
    const r = e[lado];
    if (!r) {
      problemas.push(`empunhadura: sem o braço ${lado}`);
      continue;
    }
    if (!(r.penetracaoMM <= LIMITES_DA_PEGA.penetracaoMM)) {
      problemas.push(`empunhadura ${lado}: a luva entra ${fmt(r.penetracaoMM)} mm na arma (máximo ${LIMITES_DA_PEGA.penetracaoMM} mm)`);
    }
    for (const [contato, mm] of Object.entries(r.contatosMM ?? {})) {
      if (!(mm <= LIMITES_DA_PEGA.contatoMM)) {
        problemas.push(`empunhadura ${lado}: o contato ${contato} a ${fmt(mm)} mm da arma (máximo ${LIMITES_DA_PEGA.contatoMM} mm)`);
      }
    }
    if (r.lados) problemas.push(...problemasDosLados(lado, r.lados, lado === e.frente ? DEDOS_DA_FRENTE : null));
    if (pega.marca[lado] !== e.marca?.[lado]) problemas.push(`empunhadura ${lado}: a marca do .glb não é a do relatório`);
    if (marcaLuvas && pega.marca[lado] !== marcaLuvas[lado]) {
      problemas.push(`empunhadura ${lado}: a marca do rig da pega (${pega.marca[lado].slice(0, 12)}…) não é a do luvas.glb `
        + `(${String(marcaLuvas[lado]).slice(0, 12)}…): construa de novo as luvas e a arma`);
    }
  }
  return problemas;
}
