// Plano executado da 4.1b (Tarefa 15 do plano de desenho): o plano de desenho, tarefa por tarefa, seguido do código
// verificado de cada uma — o arquivo inteiro para os novos e os pares "trocar → por" da base (`base-4.1b`) até a cópia
// de trabalho para os alterados, com os comandos dos testes (antes: falham; depois: passam) e a contagem da suíte. Os
// arquivos de cada tarefa vêm de tarefas-4.1b.mjs; as contagens, do relatório do validador (`contagens.json`, opcional:
// sem ele o plano sai sem os números, para a primeira validação).
// Uso: node plano-executado-4.1b.mjs <trabalho> <base> <saída.md> [contagens.json]
import { existsSync, readFileSync, writeFileSync } from 'node:fs';
import { makePairs } from './pairs.mjs';
import { TAREFAS, CONSTRUIR } from './tarefas-4.1b.mjs';

const [WORK, BASE, OUT, CONTAGENS] = process.argv.slice(2);
const DESENHO = 'docs/superpowers/plans/2026-09-26-4.1b-luvas-e-empunhadura.md';
const read = (root, file) => readFileSync(`${root}/${file}`, 'utf8').replace(/\r\n/g, '\n');
const contagens = CONTAGENS && existsSync(CONTAGENS) ? JSON.parse(readFileSync(CONTAGENS, 'utf8')) : {};
const LANG = { '.py': 'python', '.html': 'html', '.json': 'json', '.css': 'css', '.md': 'md', '.sh': 'bash' };
const lang = (file) => LANG[file.slice(file.lastIndexOf('.'))] ?? 'js';

function arquivo(file) {
  const text = read(WORK, file);
  if (!text.endsWith('\n')) throw new Error(`sem \\n no fim: ${file}`);
  if (/^```/m.test(text)) throw new Error(`cerca de código dentro do arquivo: ${file}`);
  return `\`\`\`${lang(file)} file=${file}\n${text}\`\`\``;
}

function pares(file) {
  const ps = makePairs(read(BASE, file), read(WORK, file));
  if (!ps.length) throw new Error(`sem mudança: ${file}`);
  for (const p of ps) if (/^```/m.test(p.from) || /^```/m.test(p.to)) throw new Error(`cerca num par: ${file}`);
  return ps.map((p) => `Em \`${file}\`, trocar:\n\n\`\`\`\n${p.from}\n\`\`\`\n\npor:\n\n\`\`\`\n${p.to}\n\`\`\``).join('\n\n');
}

const naBase = (file) => existsSync(`${BASE}/${file}`);
const codigo = (file) => (naBase(file) ? pares(file) : arquivo(file));
const lista = (fs) => fs.map((f) => `\`${f}\``).join(', ');

function secaoDoCodigo(n) {
  const t = TAREFAS[n];
  if (!t) return '';
  const c = contagens[n] ?? {};
  const partes = [];
  if (!t.testes.length && !t.novos.length && !t.pares.length) {
    if (n === 7) {
      partes.push('**Código da tarefa:** nenhum arquivo novo — o `principal.py` chama o solver da pega no `construir` de '
        + 'cada arma, então o solver inteiro e a saída da pega entraram com a Tarefa 6; aqui fica a construção da AK com a '
        + 'pega e a conferência (o validador constrói a AK logo depois da Tarefa 6).');
    } else {
      partes.push('**Código da tarefa:** nenhum arquivo (tarefa de conferência no navegador e no Blender).');
    }
    return `\n${partes.join('\n\n')}\n`;
  }
  partes.push(`**Código da tarefa** (a versão verificada no navegador e no Blender; os blocos \`file=\` são o arquivo `
    + 'inteiro, os pares são aplicados na ordem).');
  if (t.testes.length) {
    partes.push(`- [ ] **Os testes** — ${lista(t.testes)}:`);
    partes.push(t.testes.map(codigo).join('\n\n'));
    const so = t.testes.filter((f) => f.endsWith('.test.js')).join(' ');
    partes.push(`Run: \`node --test ${so}\`\nExpected: FAIL — ${c.antes ?? 'os testes novos falham (o código da tarefa ainda não existe)'}.`);
  }
  const impl = [...t.novos, ...t.pares];
  if (impl.length) {
    partes.push(`- [ ] **A implementação** — ${lista(impl)}:`);
    partes.push(impl.map(codigo).join('\n\n'));
  }
  for (const alvo of CONSTRUIR[n] ?? []) {
    partes.push(`- [ ] **Construir no Blender** — \`npm run blender -- construir ${alvo}\` (aprovado, sem problema na validação).`);
  }
  if (t.testes.length) {
    const so = t.testes.filter((f) => f.endsWith('.test.js')).join(' ');
    partes.push(`Run: \`node --test ${so}\`\nExpected: PASS${c.depois ? ` — ${c.depois}` : ''}.`);
  }
  partes.push(`Run: \`node --test "tests/**/*.test.js"\`\nExpected: PASS${c.suite ? ` — ${c.suite}` : ''}.`);
  return `\n${partes.join('\n\n')}\n`;
}

const desenho = read(WORK, DESENHO);
const titulo = '# Subfase 4.1b — Luvas, braço de massinha e empunhadura: plano executado';
const nota = `> **Plano executado** (Tarefa 15 do plano de desenho, \`${DESENHO}\`): o plano de desenho inteiro, com as notas
> da execução, e depois de cada tarefa o código verificado dela — gerado por \`prova-armas-2026-09-26/ferramentas-plano/
> plano-executado-4.1b.mjs\` a partir de \`base-4.1b\` (o \`Game tiro\` depois da 4.1a) e \`trabalho-4.1b\`. Cada arquivo entra
> numa tarefa só, na versão final; a ordem segue os imports: o \`src/data/luvas.js\` entra com a ficha (Tarefa 2); o solver
> inteiro e a saída da pega entram com a construção das luvas (Tarefa 6), porque o \`principal.py\` chama o solver no
> \`construir\` de cada arma e o \`luvas.py\` fecha as poses de teste até o contato; os documentos que mudaram em várias
> tarefas entram na 13 e na 15. Os binários de \`assets/\` saem do \`construir\` (Tarefa 6: as luvas e a AK).
> **Como aplicar:** \`python3 prova-armas-2026-09-26/ferramentas-plano/aplica-4.1a.py <este plano> <raiz> <primeira>
> <última>\` grava os blocos \`file=\` e aplica os pares em ordem (cada "trocar" é único no arquivo naquele momento); o
> validador \`valida-4.1b.sh\` faz isso numa cópia limpa da base, tarefa por tarefa, com os testes falhando antes e
> passando depois e a suíte inteira passando no fim de cada tarefa.`;

const linhas = desenho.split('\n');
const saida = [titulo, '', nota, ''];
let n = null;
const fecha = () => {
  if (n !== null) saida.push(secaoDoCodigo(n));
};
for (let i = 1; i < linhas.length; i++) {
  const m = /^## Tarefa (\d+):(.*)$/.exec(linhas[i]);
  if (m) {
    fecha();
    n = Number(m[1]);
    saida.push(`### Tarefa ${m[1]}:${m[2]}`);
    continue;
  }
  if (/^### Tarefa \d+:/.test(linhas[i])) throw new Error(`cabeçalho de tarefa inesperado: ${linhas[i]}`);
  saida.push(linhas[i]);
}
fecha();
const texto = `${saida.join('\n').trimEnd()}\n`;
writeFileSync(OUT, texto);
const usados = Object.values(TAREFAS).flatMap((t) => [...t.testes, ...t.novos, ...t.pares]);
console.log(`plano executado: ${texto.split('\n').length} linhas, ${usados.length} arquivos`);
