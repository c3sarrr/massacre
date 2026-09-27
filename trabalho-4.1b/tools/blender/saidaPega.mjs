// A pega das luvas na saída de uma arma realista (Fase 4.1b; desenho, seções 6.3 e 6.4; plano, Tarefa 7): a seção
// `empunhadura` do relatório do Blender (a penetração da luva na arma e a distância de cada contato da regra, nos dois
// braços) e a marca do rig, igual no relatório, no .glb da arma e no luvas.glb (D4). O que o .glb precisa ter (os nós
// e o clipe) é conferido por `lerPega` (src/characters/hands/pega.js), que lança.
import { LIMITES_DA_PEGA } from '../../src/data/luvas.js';

const fmt = (v) => v.toFixed(2).replace('.', ',');

/**
 * Os problemas da pega: o relatório sem a seção, a penetração acima de 0,3 mm ou um contato acima de 1 mm num braço, a
 * marca do .glb diferente da do relatório ou da das luvas (`marcaLuvas`, a do luvas.glb; null se ainda não há luvas).
 * @returns {string[]}
 */
export function validarPega(relatorio, pega, marcaLuvas) {
  const e = relatorio?.empunhadura;
  if (!e) return ['o relatório sem a seção empunhadura (a pega das luvas; construa a arma de novo)'];
  const problemas = [];
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
    if (pega.marca[lado] !== e.marca?.[lado]) problemas.push(`empunhadura ${lado}: a marca do .glb não é a do relatório`);
    if (marcaLuvas && pega.marca[lado] !== marcaLuvas[lado]) {
      problemas.push(`empunhadura ${lado}: a marca do rig da pega (${pega.marca[lado].slice(0, 12)}…) não é a do luvas.glb `
        + `(${String(marcaLuvas[lado]).slice(0, 12)}…): construa de novo as luvas e a arma`);
    }
  }
  return problemas;
}
