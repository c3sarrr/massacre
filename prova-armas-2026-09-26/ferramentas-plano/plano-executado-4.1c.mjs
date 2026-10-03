// Plano executado da 4.1c (Tarefa 16 do plano de desenho): o plano de desenho, tarefa por tarefa, seguido do código
// verificado de cada uma — o arquivo inteiro para os novos e os pares "trocar → por" para os alterados, da versão da
// tarefa anterior até a desta (um arquivo que mudou em várias tarefas entra pedaço por pedaço: tarefas-4.1c.mjs e
// blocos-diff.mjs) —, com os comandos dos testes (antes: falham; depois: passam), a prova das peças e o construir do
// Blender e a contagem da suíte. As contagens vêm do relatório do validador (`contagens.json`, opcional: sem ele o
// plano sai sem os números, para a primeira validação).
// Uso: node plano-executado-4.1c.mjs <trabalho> <base> <saída.md> [contagens.json]
import { existsSync, readFileSync, writeFileSync } from 'node:fs';
import { makePairs } from './pairs.mjs';
import { aplicarBlocos, blocosDoDiff } from './blocos-diff.mjs';
import {
  ARQUIVOS, BINARIOS, CONSTRUIR, GERAR, INTEIROS, JSON_CHAVES, PROVAR, REMOVER, SAIDAS,
} from './tarefas-4.1c.mjs';

const [WORK, BASE, OUT, CONTAGENS] = process.argv.slice(2);
const DESENHO = 'docs/superpowers/plans/2026-09-28-4.1c-glock-m4a4-m9.md';
const ULTIMA = 16;
const read = (root, file) => readFileSync(`${root}/${file}`, 'utf8').replace(/\r\n/g, '\n');
const naBase = (file) => existsSync(`${BASE}/${file}`);
const contagens = CONTAGENS && existsSync(CONTAGENS) ? JSON.parse(readFileSync(CONTAGENS, 'utf8')) : {};
const LANG = { '.py': 'python', '.html': 'html', '.json': 'json', '.css': 'css', '.md': 'md', '.sh': 'bash' };
const lang = (file) => LANG[file.slice(file.lastIndexOf('.'))] ?? 'js';

/** As crases da cerca de um texto: uma a mais que a maior sequência no começo de uma linha dele (no mínimo três). */
function cerca(...textos) {
  let maior = 0;
  for (const t of textos) for (const m of t.matchAll(/^(`+)/gm)) maior = Math.max(maior, m[1].length);
  return '`'.repeat(Math.max(3, maior + 1));
}

// ---------------------------------------------------------------- as versões de cada arquivo, tarefa por tarefa

/** Os blocos do diff de cada arquivo alterado com a tarefa de cada um. */
const planos = new Map();
for (const [file, regra] of Object.entries(ARQUIVOS)) {
  if (!existsSync(`${WORK}/${file}`)) throw new Error(`não existe na cópia de trabalho: ${file}`);
  if (typeof regra === 'number') {
    planos.set(file, { tarefas: [regra] });
    continue;
  }
  if (!naBase(file)) throw new Error(`arquivo novo não se reparte: ${file}`);
  const blocos = blocosDoDiff(read(BASE, file), read(WORK, file));
  const tarefaDe = blocos.map(() => regra.resto);
  for (const [t, indices] of Object.entries(regra)) {
    if (t === 'resto') continue;
    for (const k of indices) {
      if (!(k in blocos)) throw new Error(`${file}: não há o bloco ${k} (são ${blocos.length})`);
      tarefaDe[k] = Number(t);
    }
  }
  planos.set(file, { blocos, tarefaDe, tarefas: [...new Set(tarefaDe)].sort((a, b) => a - b) });
}

/** O texto do arquivo depois da tarefa t (null: ainda não existe). */
function versao(file, t) {
  const p = planos.get(file);
  if (!p.blocos) {
    if (t >= p.tarefas[0]) return read(WORK, file);
    return naBase(file) ? read(BASE, file) : null;
  }
  return aplicarBlocos(read(BASE, file), p.blocos.filter((_b, k) => p.tarefaDe[k] <= t));
}

// ---------------------------------------------------------------- o código de uma tarefa

/** O arquivo inteiro; o que não termina em quebra de linha (as fichas que a régua grava) leva `sem-quebra`. */
function arquivoInteiro(file, texto) {
  const c = cerca(texto);
  if (!texto.endsWith('\n')) return `${c}${lang(file)} file=${file} sem-quebra\n${texto}\n${c}`;
  return `${c}${lang(file)} file=${file}\n${texto}${c}`;
}

function pares(file, antes, depois) {
  const ps = makePairs(antes, depois);
  if (!ps.length) throw new Error(`sem mudança: ${file}`);
  return ps.map((p) => {
    const c = cerca(p.from, p.to);
    return `Em \`${file}\`, trocar:\n\n${c}\n${p.from}\n${c}\n\npor:\n\n${c}\n${p.to}\n${c}`;
  }).join('\n\n');
}

/** O bloco do arquivo na tarefa t: inteiro (novo, ou trocado inteiro) ou os pares da versão anterior. */
function codigo(file, t) {
  const antes = versao(file, t - 1);
  const depois = versao(file, t);
  if (antes === null || (INTEIROS.has(file) && planos.get(file).tarefas[0] === t)) return arquivoInteiro(file, depois);
  return pares(file, antes, depois);
}

function chavesNovas(file) {
  const base = JSON.parse(read(BASE, file));
  const fim = JSON.parse(read(WORK, file));
  const linhas = Object.keys(fim).filter((k) => !(k in base)).map((k) => `${JSON.stringify(k)}: ${JSON.stringify(fim[k])}`);
  for (const k of Object.keys(base)) {
    if (JSON.stringify(base[k]) !== JSON.stringify(fim[k])) throw new Error(`${file}: a chave ${k} mudou (só chaves novas)`);
  }
  return `\`\`\`json chaves=${file}\n{\n${linhas.join(',\n')}\n}\n\`\`\``;
}

const lista = (fs) => fs.map((f) => `\`${f}\``).join(', ');
const arquivosDa = (t) => [...planos.entries()].filter(([, p]) => p.tarefas.includes(t)).map(([f]) => f);


function secaoDoCodigo(t) {
  const arqs = arquivosDa(t);
  const testes = arqs.filter((f) => f.startsWith('tests/'));
  const impl = arqs.filter((f) => !f.startsWith('tests/'));
  const extras = (REMOVER[t] ?? []).length + (JSON_CHAVES[t] ?? []).length + (GERAR[t] ?? []).length
    + (BINARIOS[t] ?? []).length + (PROVAR[t] ?? []).length + (CONSTRUIR[t] ?? []).length;
  if (!arqs.length && !extras) {
    if (t >= 8 && t <= 10) {
      return '\n**Código da tarefa:** só o Python dela, que entrou acima; nada no Node.\n';
    }
    return '\n**Código da tarefa:** nenhum arquivo (tarefa de conferência no navegador e no Blender).\n';
  }
  const c = contagens[t] ?? {};
  const partes = [`**Código da tarefa** (a versão verificada no navegador e no Blender; os blocos \`file=\` são o arquivo `
    + 'inteiro, os pares são aplicados na ordem).'];
  const rodar = testes.filter((f) => f.endsWith('.test.js')).join(' ');
  if (testes.length) {
    partes.push(`- [ ] **Os testes** — ${lista(testes)}:`);
    partes.push(testes.map((f) => codigo(f, t)).join('\n\n'));
    partes.push(`Run: \`node --test ${rodar}\`\nExpected: FAIL — ${c.antes ?? 'os testes novos falham (o código da tarefa ainda não existe)'}.`);
  }
  if (impl.length || (JSON_CHAVES[t] ?? []).length) {
    partes.push(`- [ ] **A implementação** — ${lista([...impl, ...(JSON_CHAVES[t] ?? [])])}:`);
    const blocos = impl.map((f) => codigo(f, t));
    for (const f of JSON_CHAVES[t] ?? []) {
      blocos.push(`O \`${f}\` é o objeto do \`JSON.stringify\` numa linha só; ele ganha estas chaves no fim, na ordem:\n\n${chavesNovas(f)}`);
    }
    partes.push(blocos.join('\n\n'));
  }
  for (const g of GERAR[t] ?? []) {
    partes.push(`- [ ] **Gerar** \`${g.arquivo}\`:\n\n\`\`\`bash\n${g.comando}\n\`\`\``);
  }
  if ((REMOVER[t] ?? []).length) {
    partes.push(`- [ ] **Remover** ${lista(REMOVER[t])}:\n\n\`\`\`bash\n${REMOVER[t].map((f) => `rm ${f}`).join('\n')}\n\`\`\``);
  }
  for (const b of BINARIOS[t] ?? []) {
    partes.push(`- [ ] **Baixar** \`${b.arquivo}\` — ${b.descricao}, da página ${b.pagina} (CC0, registrada em `
      + `\`tools/blender/texturas/fontes.json\`); o md5 tem de ser \`${b.md5}\` (o \`texturas.py\` recusa outro).`);
  }
  for (const alvo of PROVAR[t] ?? []) {
    partes.push(`- [ ] **Provar no Blender** — \`npm run blender -- provar ${alvo}\` (as medidas de cada peça, sem problema).`);
  }
  for (const alvo of CONSTRUIR[t] ?? []) {
    partes.push(`- [ ] **Construir no Blender** — \`npm run blender -- construir ${alvo}\` (as luvas e as quatro armas `
      + `aprovadas, sem problema na validação; saem ${lista(SAIDAS[t])}).`);
  }
  if (testes.length) {
    partes.push(`Run: \`node --test ${rodar}\`\nExpected: PASS${c.depois ? ` — ${c.depois}` : ''}.`);
  }
  partes.push(`Run: \`node --test "tests/**/*.test.js"\`\nExpected: PASS${c.suite ? ` — ${c.suite}` : ''}.`);
  return `\n${partes.join('\n\n')}\n`;
}

// ---------------------------------------------------------------- o plano

const desenho = read(WORK, DESENHO);
const titulo = '# Subfase 4.1c — Glock-18, M4A4 e a baioneta M9: plano executado';
const nota = `> **Plano executado** (Tarefa 16 do plano de desenho, \`${DESENHO}\`): o plano de desenho inteiro, com as notas
> da execução, e depois de cada tarefa o código verificado dela — gerado por \`prova-armas-2026-09-26/ferramentas-plano/
> plano-executado-4.1c.mjs\` a partir de \`base-4.1c\` (o \`Game tiro\` depois da 4.1b) e \`trabalho-4.1c\`. Um arquivo que
> mudou em várias tarefas entra pedaço por pedaço — cada tarefa com os pares da versão da anterior até a dela (os blocos
> do diff repartidos em \`tarefas-4.1c.mjs\`) —, então cada tarefa traz o código e os testes dela. A construção no
> Blender roda uma vez, depois da Tarefa 11 (as luvas e as quatro armas; a prova das peças, depois da 4): os scripts
> das armas, a biblioteca e o solver são Python sem teste do Node e entram inteiros, cada um na tarefa da mudança
> principal dele; o que lê os .glb novos (os testes das três armas, a pega com a palma que cede, as três que viram
> realistas no registro) entra com a construção. O \`pega.js\`, o \`saidaPega.mjs\` e o \`luvas.js\` entram inteiros na
> 11: a pega de uma mão (Tarefa 8), a da faca (9) e as duas mãos da pistola com a palma (11) estão nas mesmas funções, e
> a leitura da pega passou a exigir a palma, que só as construções novas trazem. Os binários de \`assets/\` saem do
> \`construir\`; a textura CC0 da madeira (Tarefa 7) é baixada da página dela, conferida pelo md5.
> **Como aplicar:** \`python3 prova-armas-2026-09-26/ferramentas-plano/aplica-4.1c.py <este plano> <raiz> <primeira>
> <última>\` grava os blocos \`file=\`, aplica os pares em ordem (cada "trocar" é único no arquivo naquele momento), põe
> as chaves novas do \`pinterest-boards.json\`, remove os arquivos dos \`rm\` e gera o \`moodboard.html\`; o validador
> \`valida-4.1c.sh\` faz isso numa cópia limpa da base, tarefa por tarefa, com os testes falhando antes e passando depois
> e a suíte inteira passando no fim de cada tarefa.`;

const linhas = desenho.split('\n');
const saida = [titulo, '', nota, ''];
let n = null;
let emTarefa = false;
const fecha = () => {
  if (n !== null && emTarefa) saida.push(secaoDoCodigo(n));
  emTarefa = false;
};
for (let i = 1; i < linhas.length; i++) {
  const l = linhas[i];
  const m = /^## Tarefa (\d+):(.*)$/.exec(l);
  if (m) {
    fecha();
    n = Number(m[1]);
    emTarefa = true;
    saida.push(`### Tarefa ${m[1]}:${m[2]}`);
    continue;
  }
  if (/^## /.test(l)) fecha();
  if (/^### Tarefa \d+:/.test(l)) throw new Error(`cabeçalho de tarefa inesperado: ${l}`);
  // dentro das tarefas, as seções de terceiro nível descem um nível (a tarefa é de terceiro no plano executado)
  saida.push(emTarefa && /^### /.test(l) ? `#${l}` : l);
}
fecha();
if (n !== ULTIMA) throw new Error(`a última tarefa do desenho é a ${n}, não a ${ULTIMA}`);
const texto = `${saida.join('\n').trimEnd()}\n`;
writeFileSync(OUT, texto);
console.log(`plano executado: ${texto.split('\n').length} linhas, ${planos.size} arquivos`);
