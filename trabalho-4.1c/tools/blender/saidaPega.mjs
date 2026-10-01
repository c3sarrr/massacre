// A pega das luvas na saída de uma arma realista (Fase 4.1b; desenho, seções 6.3 e 6.4; plano, Tarefa 7): a seção
// `empunhadura` do relatório do Blender (a penetração da luva na arma e a distância de cada contato da regra, nos dois
// braços; os lados dos dedos) e a marca do rig, igual no relatório, no .glb da arma e no luvas.glb (D4). O que o .glb
// precisa ter (os nós e o clipe) é conferido por `lerPega` (src/characters/hands/pega.js), que lança.
// Os lados (regra do usuário de 2026-09-27): na mão da frente (`frente` no relatório) só o polegar de um lado da arma e
// o indicador, o médio, o anelar e o mínimo do outro — `lados.polegarMM` e `lados.dedosMM` são a posição da polpa de
// cada um no eixo do lado do polegar (mm, a partir do plano do meio da arma); a do polegar tem de passar de +ladoMM e a
// de cada dedo de −ladoMM. A mão do gatilho, quando traz os lados (o polegar cruzando o punho), passa pela mesma conta.
// E o polegar da frente reto e deitado na arma (`polegar.curvaGraus` e `polegar.trechosMM`, a folga de cada trecho da
// falange proximal e da distal, da base para a ponta): a curva até polegarCurvaGraus, a distal encostando (o trecho
// mais perto dela até contatoMM) e nenhum trecho além de polegarFolgaMM.
// E os dedos que abraçam a arma lado a lado, sem leque (`juntosMM`: por par de vizinhos, a folga na falange média e na
// distal): a média até dedosJuntosMM, nas duas mãos; a mão da frente tem de trazer os três pares dos quatro dedos.
// As mãos (4.1c): a regra da categoria diz quais (MAOS_DA_CATEGORIA: a faca só com a direita), e o relatório
// (`empunhadura.maos`; sem o campo, as duas — as armas da 4.1b) e o .glb (`lerPega`) têm de bater com ela; a mão da
// frente só onde a categoria tem uma (FRENTE_DA_CATEGORIA: o fuzil).
import {
  DEDOS_DA_FRENTE, FRENTE_DA_CATEGORIA, LIMITES_DA_PEGA, MAOS_DA_CATEGORIA, POLEGAR_SOBRE_DA_CATEGORIA,
} from '../../src/data/luvas.js';

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

/** Os problemas do polegar da mão da frente: reto (a curva) e deitado na arma (a distal encostada, a proximal perto). */
const PARES_DA_FRENTE = DEDOS_DA_FRENTE.slice(1).map((d, i) => `${DEDOS_DA_FRENTE[i]}-${d}`);

/** Os problemas dos dedos lado a lado de um braço (os pares `exigidos` têm de vir). */
function problemasDosJuntos(lado, juntos, exigidos) {
  if (!juntos) {
    return exigidos ? [`empunhadura ${lado}: a mão da frente sem a conferência dos dedos lado a lado (construa a arma de novo)`] : [];
  }
  const problemas = [];
  for (const par of exigidos ?? []) {
    if (!juntos[par]) problemas.push(`empunhadura ${lado}: sem a folga entre os dedos ${par} (construa a arma de novo)`);
  }
  for (const [par, [media]] of Object.entries(juntos)) {
    if (!(media <= LIMITES_DA_PEGA.dedosJuntosMM)) {
      problemas.push(`empunhadura ${lado}: ${par} com a falange média a ${fmt(media ?? NaN)} mm uma da outra (máximo `
        + `${LIMITES_DA_PEGA.dedosJuntosMM} mm): os dedos em leque, não lado a lado`);
    }
  }
  return problemas;
}

/** O polegar dobrado por cima dos dedos `sobre` (a faca): encostado neles, a polpa a até contatoMM. */
function problemasDoPolegarSobre(lado, polegar, sobre) {
  const m = LIMITES_DA_PEGA.contatoMM;
  const nos = sobre.join(', ');
  if (!polegar || (polegar.sobre ?? []).join() !== sobre.join()) {
    return [`empunhadura ${lado}: o polegar não está dobrado por cima do ${nos} (a regra da faca; construa a arma de novo)`];
  }
  if (!polegar.encostou || !(polegar.polpaEncostaMM <= m)) {
    return [`empunhadura ${lado}: o polegar não assenta no ${nos} (a polpa a ${fmt(polegar.polpaEncostaMM ?? NaN)} mm; `
      + `máximo ${m} mm)`];
  }
  return [];
}

function problemasDoPolegar(lado, polegar) {
  const L = LIMITES_DA_PEGA;
  const t = polegar?.trechosMM;
  if (!Array.isArray(t) || t.length < 2 || !Number.isFinite(polegar.curvaGraus)) {
    return [`empunhadura ${lado}: a mão da frente sem a conferência do polegar deitado (a curva e a folga ao longo dele; `
      + 'construa a arma de novo)'];
  }
  const problemas = [];
  if (!(polegar.curvaGraus <= L.polegarCurvaGraus)) {
    problemas.push(`empunhadura ${lado}: o polegar da frente com ${fmt(polegar.curvaGraus)}° de curva (a MCP mais a IP; `
      + `máximo ${L.polegarCurvaGraus}°): tem de ficar reto, deitado na arma`);
  }
  const meio = t.length / 2;
  const distal = Math.min(...t.slice(meio));
  if (!(distal <= L.contatoMM)) {
    problemas.push(`empunhadura ${lado}: a falange distal do polegar da frente não encosta na arma (o trecho mais perto a `
      + `${fmt(distal)} mm; máximo ${L.contatoMM} mm)`);
  }
  t.forEach((mm, i) => {
    if (!(mm <= L.polegarFolgaMM)) {
      const falange = i < meio ? 'proximal' : 'distal';
      problemas.push(`empunhadura ${lado}: a falange ${falange} do polegar da frente a ${fmt(mm)} mm da arma no trecho `
        + `${(i % meio) + 1} (máximo ${L.polegarFolgaMM} mm): tem de ficar deitada nela`);
    }
  });
  return problemas;
}

/**
 * Os problemas da pega: o relatório sem a seção, as mãos do relatório ou do .glb diferentes das da categoria, a
 * penetração acima de 0,3 mm ou um contato acima de 1 mm num braço, a mão da frente sem só o polegar de um lado e os
 * quatro dedos do outro, os dedos em leque, a marca do .glb diferente da do relatório ou da das luvas (`marcaLuvas`, a
 * do luvas.glb; null se ainda não há luvas).
 * @param {string} [categoria] a do viewmodel da arma (MAOS_DA_CATEGORIA); o fuzil, se não vier
 * @returns {string[]}
 */
export function validarPega(relatorio, pega, marcaLuvas, categoria = 'rifle') {
  const e = relatorio?.empunhadura;
  if (!e) return ['o relatório sem a seção empunhadura (a pega das luvas; construa a arma de novo)'];
  const maos = MAOS_DA_CATEGORIA[categoria];
  if (!maos) return [`empunhadura: a categoria ${categoria} não tem as mãos da regra (MAOS_DA_CATEGORIA)`];
  const problemas = [];
  const doRelatorio = e.maos ?? ['d', 'e'];
  if (doRelatorio.join() !== maos.join()) {
    problemas.push(`empunhadura: as mãos do relatório (${doRelatorio.join(', ')}) não são as da categoria ${categoria} `
      + `(${maos.join(', ')})`);
  }
  if ((pega.lados ?? ['d', 'e']).join() !== maos.join()) {
    problemas.push(`empunhadura: as mãos do .glb (${(pega.lados ?? []).join(', ')}) não são as da categoria ${categoria} `
      + `(${maos.join(', ')})`);
  }
  if (FRENTE_DA_CATEGORIA[categoria]) {
    if (e.frente !== 'd' && e.frente !== 'e') {
      problemas.push('empunhadura: o relatório não diz qual é a mão da frente (construa a arma de novo)');
    } else if (!e[e.frente]?.lados) {
      problemas.push(`empunhadura ${e.frente}: a mão da frente sem a conferência dos lados (o polegar de um lado e os `
        + 'quatro dedos do outro; construa a arma de novo)');
    }
  }
  for (const lado of maos) {
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
    const sobre = POLEGAR_SOBRE_DA_CATEGORIA[categoria];
    if (sobre && lado === 'd') problemas.push(...problemasDoPolegarSobre(lado, r.polegar, sobre));
    if (lado === e.frente) problemas.push(...problemasDoPolegar(lado, r.polegar));
    problemas.push(...problemasDosJuntos(lado, r.juntosMM, lado === e.frente ? PARES_DA_FRENTE : null));
    if (pega.marca[lado] !== e.marca?.[lado]) problemas.push(`empunhadura ${lado}: a marca do .glb não é a do relatório`);
    if (marcaLuvas && pega.marca[lado] !== marcaLuvas[lado]) {
      problemas.push(`empunhadura ${lado}: a marca do rig da pega (${String(pega.marca[lado]).slice(0, 12)}…) não é a do `
        + `luvas.glb (${String(marcaLuvas[lado]).slice(0, 12)}…): construa de novo as luvas e a arma`);
    }
  }
  return problemas;
}
