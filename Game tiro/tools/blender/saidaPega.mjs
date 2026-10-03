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
// As duas mãos da pistola (4.1c, Tarefa 11; DUAS_MAOS_DA_CATEGORIA): os dois polegares do lado esquerdo (os `lados` nas
// duas mãos) e a pelo menos folgaFerrolhoMM do ferrolho (`folgaFerrolhoMM`), nenhuma luva mais de luvaPenetracaoMM
// dentro da outra (`penetracaoLuvaMM` de cada braço), os quatro dedos de apoio a até contatoMM da luva do gatilho e o
// polegar do gatilho a até contatoMM da de apoio, em que ele deita (`contatosLuvaMM`); os dois polegares apontando para a
// frente (`desvioDoEixoGraus` até polegarEixoGraus) e o indicador do gatilho indexado na armação (INDEXADO_DA_CATEGORIA:
// o `indicador` do relatório, conferido por problemasDoIndexado).
// A palma que cede (4.1c, Tarefa 11; tools/blender/armas/maos_palma.py): cada braço com o afundamento da palma no .glb
// (`palma` dos extras: os vértices e os vetores) e o resumo no relatório (`palma`: o maior afundamento, quantos vértices
// afundam, quantos encostaram e o quanto algum ainda entra além do que cede) — os dois batendo, nada entrando além do
// que cede mais que penetracaoMM, e, com as luvas construídas, cada vértice dos que cedem nelas e afundando até o que ele
// cede (a capacidade dos extras do luvas.glb).
import {
  DEDOS_DA_FRENTE, DUAS_MAOS_DA_CATEGORIA, FRENTE_DA_CATEGORIA, INDEXADO_DA_CATEGORIA, LIMITES_DA_PEGA, MAOS_DA_CATEGORIA,
  POLEGAR_SOBRE_DA_CATEGORIA,
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

/** As contas das duas mãos da pistola num braço (`papel` 'gatilho' ou 'apoio'; `outra`, o lado da outra luva). */
function problemasDasDuasMaos(lado, r, papel, outra) {
  const L = LIMITES_DA_PEGA;
  const problemas = [];
  if (!r.lados) {
    problemas.push(`empunhadura ${lado}: sem a conferência dos lados (o polegar do lado esquerdo da arma; construa a arma de novo)`);
  }
  if (!Number.isFinite(r.folgaFerrolhoMM)) {
    problemas.push(`empunhadura ${lado}: sem a folga do polegar ao ferrolho (construa a arma de novo)`);
  } else if (!(r.folgaFerrolhoMM >= L.folgaFerrolhoMM)) {
    problemas.push(`empunhadura ${lado}: o polegar a ${fmt(r.folgaFerrolhoMM)} mm do ferrolho (mínimo ${L.folgaFerrolhoMM} `
      + 'mm: o ferrolho recua no tiro)');
  }
  if (!Number.isFinite(r.penetracaoLuvaMM)) {
    problemas.push(`empunhadura ${lado}: sem a conta da luva com a luva (construa a arma de novo)`);
  } else if (!(r.penetracaoLuvaMM <= L.luvaPenetracaoMM)) {
    problemas.push(`empunhadura ${lado}: a luva entra ${fmt(r.penetracaoLuvaMM)} mm na luva ${outra} (máximo `
      + `${L.luvaPenetracaoMM} mm)`);
  }
  // os contatos com a outra luva: na de apoio, os quatro dedos por cima dos da mão do gatilho; na do gatilho, o polegar
  // deitado sobre o de apoio
  const contatos = r.contatosLuvaMM ?? {};
  for (const d of papel === 'apoio' ? DEDOS_DA_FRENTE : ['polegar']) {
    if (!(d in contatos)) {
      problemas.push(`empunhadura ${lado}: sem o contato do ${d} com a luva ${outra} (construa a arma de novo)`);
    } else if (!(contatos[d] <= L.contatoMM)) {
      problemas.push(`empunhadura ${lado}: o ${d} a ${fmt(contatos[d])} mm da luva ${outra} (máximo ${L.contatoMM} mm)`);
    }
  }
  return problemas;
}

/**
 * O polegar reto e deitado (`quem`: 'da frente', a mão da frente do fuzil; 'do gatilho' e 'de apoio', as duas da
 * pistola): a curva, a falange distal encostando e a folga ao longo dele. O do gatilho da pistola deita por cima do de
 * apoio: a folga dele é medida até o polegar da luva de apoio (o texto em `na` e `da`). Com `paraFrente` (os dois da
 * pistola, a pega de polegares para a frente), a falange mais torta a até `polegarEixoGraus` do eixo da regra: deitado
 * em cima do de apoio, o do gatilho saía a 38° dele, para fora da arma, e a folga ao longo dele passava.
 */
function problemasDoPolegar(lado, polegar, quem = 'da frente', { na = 'na arma', da = 'da arma', paraFrente = false } = {}) {
  const L = LIMITES_DA_PEGA;
  const t = polegar?.trechosMM;
  if (!Array.isArray(t) || t.length < 2 || !Number.isFinite(polegar.curvaGraus)) {
    return [`empunhadura ${lado}: sem a conferência do polegar deitado (o polegar ${quem}: a curva e a folga ao longo `
      + 'dele; construa a arma de novo)'];
  }
  const problemas = [];
  if (!(polegar.curvaGraus <= L.polegarCurvaGraus)) {
    problemas.push(`empunhadura ${lado}: o polegar ${quem} com ${fmt(polegar.curvaGraus)}° de curva (a MCP mais a IP; `
      + `máximo ${L.polegarCurvaGraus}°): tem de ficar reto, deitado ${na}`);
  }
  const meio = t.length / 2;
  const distal = Math.min(...t.slice(meio));
  if (!(distal <= L.contatoMM)) {
    problemas.push(`empunhadura ${lado}: a falange distal do polegar ${quem} não encosta ${na} (o trecho mais perto a `
      + `${fmt(distal)} mm; máximo ${L.contatoMM} mm)`);
  }
  t.forEach((mm, i) => {
    if (!(mm <= L.polegarFolgaMM)) {
      const falange = i < meio ? 'proximal' : 'distal';
      problemas.push(`empunhadura ${lado}: a falange ${falange} do polegar ${quem} a ${fmt(mm)} mm ${da} no trecho `
        + `${(i % meio) + 1} (máximo ${L.polegarFolgaMM} mm): tem de ficar deitada nela`);
    }
  });
  if (paraFrente) {
    if (!Number.isFinite(polegar.desvioDoEixoGraus)) {
      problemas.push(`empunhadura ${lado}: sem a direção do polegar ${quem} (o desvio do eixo da arma; construa a arma `
        + 'de novo)');
    } else if (!(polegar.desvioDoEixoGraus <= L.polegarEixoGraus)) {
      problemas.push(`empunhadura ${lado}: o polegar ${quem} a ${fmt(polegar.desvioDoEixoGraus)}° da frente da arma `
        + `(máximo ${L.polegarEixoGraus}°): tem de apontar para a frente`);
    }
  }
  return problemas;
}

/**
 * O indicador indexado da mão do gatilho da pistola (INDEXADO_DA_CATEGORIA; o `indicador` do relatório): a curva da PIP
 * e da DIP, cada trecho das três falanges (três por falange, da base para a ponta) a até polegarFolgaMM da armação, a
 * distal encostada, a falange mais torta até o eixo da arma, o dedo longe do gatilho e do ferrolho e a falange média e
 * a distal acima do alto do gatilho (na lateral da armação, não ao longo do guarda-mato).
 */
function problemasDoIndexado(lado, ind) {
  const L = LIMITES_DA_PEGA;
  const t = ind?.trechosMM;
  const contas = ['curvaGraus', 'desvioDoEixoGraus', 'folgaGatilhoMM', 'folgaFerrolhoMM', 'acimaDoGatilhoMM'];
  if (!Array.isArray(t) || t.length !== 9 || contas.some((k) => !Number.isFinite(ind[k]))) {
    return [`empunhadura ${lado}: sem a conferência do indicador indexado (a curva, a folga ao longo dele, a direção, `
      + 'as folgas do gatilho e do ferrolho e a altura acima do gatilho; construa a arma de novo)'];
  }
  const problemas = [];
  if (!(ind.curvaGraus <= L.polegarCurvaGraus)) {
    problemas.push(`empunhadura ${lado}: o indicador indexado com ${fmt(ind.curvaGraus)}° de curva (a PIP mais a DIP; `
      + `máximo ${L.polegarCurvaGraus}°): tem de ficar reto, deitado na armação`);
  }
  const falanges = ['proximal', 'média', 'distal'];
  t.forEach((mm, i) => {
    if (!(mm <= L.polegarFolgaMM)) {
      problemas.push(`empunhadura ${lado}: a falange ${falanges[Math.floor(i / 3)]} do indicador indexado a ${fmt(mm)} mm `
        + `da armação no trecho ${(i % 3) + 1} (máximo ${L.polegarFolgaMM} mm): tem de ficar deitada nela`);
    }
  });
  const distal = Math.min(...t.slice(6));
  if (!(distal <= L.contatoMM)) {
    problemas.push(`empunhadura ${lado}: a falange distal do indicador indexado não encosta na armação (o trecho mais `
      + `perto a ${fmt(distal)} mm; máximo ${L.contatoMM} mm)`);
  }
  if (!(ind.desvioDoEixoGraus <= L.polegarEixoGraus)) {
    problemas.push(`empunhadura ${lado}: o indicador indexado a ${fmt(ind.desvioDoEixoGraus)}° da frente da arma `
      + `(máximo ${L.polegarEixoGraus}°): tem de apontar para a frente`);
  }
  if (!(ind.folgaGatilhoMM >= L.indexadoGatilhoMM)) {
    problemas.push(`empunhadura ${lado}: o indicador indexado a ${fmt(ind.folgaGatilhoMM)} mm do gatilho (mínimo `
      + `${L.indexadoGatilhoMM} mm: fora do guarda-mato)`);
  }
  if (!(ind.folgaFerrolhoMM >= L.folgaFerrolhoMM)) {
    problemas.push(`empunhadura ${lado}: o indicador indexado a ${fmt(ind.folgaFerrolhoMM)} mm do ferrolho (mínimo `
      + `${L.folgaFerrolhoMM} mm: o ferrolho recua no tiro)`);
  }
  if (!(ind.acimaDoGatilhoMM >= L.indexadoAcimaMM)) {
    problemas.push(`empunhadura ${lado}: o indicador indexado a ${fmt(ind.acimaDoGatilhoMM)} mm do alto do gatilho `
      + `(mínimo ${L.indexadoAcimaMM} mm: acima do guarda-mato, na lateral da armação)`);
  }
  return problemas;
}

/**
 * Os problemas do afundamento da palma de um braço: `rel` (o resumo do relatório), `glb` (os vértices e os vetores dos
 * extras do .glb da arma) e `cap` (a capacidade do luvas.glb: {vertices, mm}; null sem as luvas).
 */
function problemasDaPalma(lado, rel, glb, cap) {
  if (!rel) return [`empunhadura ${lado}: o relatório sem o afundamento da palma (a palma que cede; construa a arma de novo)`];
  const problemas = [];
  const normas = (glb?.vetores ?? []).map((v) => Math.hypot(v[0], v[1], v[2]));
  const maior = normas.length ? Math.max(...normas) : 0;
  if (normas.length !== rel.vertices || Math.abs(maior - rel.afundaMM) > 0.01) {
    problemas.push(`empunhadura ${lado}: o afundamento da palma do .glb (${normas.length} vértices, ${fmt(maior)} mm) não é `
      + `o do relatório (${rel.vertices}, ${fmt(rel.afundaMM ?? NaN)} mm)`);
  }
  if (!(rel.alemMM <= LIMITES_DA_PEGA.penetracaoMM)) {
    problemas.push(`empunhadura ${lado}: a palma entra ${fmt(rel.alemMM ?? NaN)} mm na arma além do que cede (máximo `
      + `${LIMITES_DA_PEGA.penetracaoMM} mm)`);
  }
  if (cap) {
    const mm = new Map(cap.vertices.map((v, k) => [v, cap.mm[k]]));
    const fora = (glb?.vertices ?? []).filter((v, k) => !(normas[k] <= (mm.get(v) ?? -1) + 2e-3));
    if (fora.length) {
      problemas.push(`empunhadura ${lado}: ${fora.length} vértices da palma afundam além do que cedem nas luvas (o primeiro, `
        + `${fora[0]}): construa de novo as luvas e a arma`);
    }
  }
  return problemas;
}

/**
 * Os problemas da pega: o relatório sem a seção, as mãos do relatório ou do .glb diferentes das da categoria, a
 * penetração acima de 0,3 mm ou um contato acima de 1 mm num braço, a mão da frente sem só o polegar de um lado e os
 * quatro dedos do outro, os dedos em leque, a marca do .glb diferente da do relatório ou da das luvas (`marcaLuvas`, a
 * do luvas.glb; null se ainda não há luvas) e a palma afundada além do que cede (`palmaLuvas`, a capacidade de cada braço
 * nos extras do luvas.glb, {lado: {vertices, mm}}; null se ainda não há luvas).
 * @param {string} [categoria] a do viewmodel da arma (MAOS_DA_CATEGORIA); o fuzil, se não vier
 * @returns {string[]}
 */
export function validarPega(relatorio, pega, marcaLuvas, categoria = 'rifle', palmaLuvas = null) {
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
    const duas = DUAS_MAOS_DA_CATEGORIA[categoria];
    if (duas) {
      const papel = lado === duas.gatilho ? 'gatilho' : 'apoio';
      problemas.push(...problemasDasDuasMaos(lado, r, papel, papel === 'gatilho' ? duas.apoio : duas.gatilho));
      // os dois polegares retos e deitados para a frente: o de apoio na armação, o do gatilho por cima dele
      problemas.push(...(papel === 'gatilho'
        ? problemasDoPolegar(lado, r.polegar, 'do gatilho', { na: 'no polegar de apoio', da: 'do polegar de apoio',
          paraFrente: true })
        : problemasDoPolegar(lado, r.polegar, 'de apoio', { paraFrente: true })));
    }
    if (INDEXADO_DA_CATEGORIA[categoria] === lado) problemas.push(...problemasDoIndexado(lado, r.indicador));
    problemas.push(...problemasDosJuntos(lado, r.juntosMM, lado === e.frente ? PARES_DA_FRENTE : null));
    problemas.push(...problemasDaPalma(lado, r.palma, pega.palma?.[lado], palmaLuvas?.[lado] ?? null));
    if (pega.marca[lado] !== e.marca?.[lado]) problemas.push(`empunhadura ${lado}: a marca do .glb não é a do relatório`);
    if (marcaLuvas && pega.marca[lado] !== marcaLuvas[lado]) {
      problemas.push(`empunhadura ${lado}: a marca do rig da pega (${String(pega.marca[lado]).slice(0, 12)}…) não é a do `
        + `luvas.glb (${String(marcaLuvas[lado]).slice(0, 12)}…): construa de novo as luvas e a arma`);
    }
  }
  return problemas;
}
