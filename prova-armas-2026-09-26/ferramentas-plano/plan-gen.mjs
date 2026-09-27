// Gera docs/phases/phase-4.1-plan.md a partir dos modelos em Markdown (texto-*.md, na ordem) com as diretivas:
//   @@arquivo <caminho>            bloco com o arquivo inteiro (a versão verificada, na cópia de trabalho)
//   @@pares <caminho>              pares "Em `arquivo`, trocar: … por: …" da base até a versão verificada
//   @@run <comando> ::: <esperado> "Run: `comando`" e "Expected: esperado" (o validador executa)
//   @@commit <arquivos> ::: <msg>  passo de commit (só com o pedido do usuário)
//   @@extrator                     o código do extrator (Tarefa 0)
// Uso: node plan-gen.mjs <trabalho> <base> <saída.md>
import { readFileSync, writeFileSync } from 'node:fs';
import { makePairs } from './pairs.mjs';

const [WORK, BASE, OUT] = process.argv.slice(2);
const DIR = new URL('.', import.meta.url);
const read = (root, file) => readFileSync(`${root}/${file}`, 'utf8').replace(/\r\n/g, '\n');
const LANG = { '.py': 'python', '.html': 'html', '.json': 'json', '.css': 'css', '.md': 'md' };
const lang = (file) => LANG[file.slice(file.lastIndexOf('.'))] ?? 'js';
const usados = new Set();

function arquivo(file) {
  const text = read(WORK, file);
  if (!text.endsWith('\n')) throw new Error(`sem \\n no fim: ${file}`);
  if (/^```/m.test(text)) throw new Error(`cerca de código dentro do arquivo: ${file}`);
  usados.add(file);
  return `\`\`\`${lang(file)} file=${file}\n${text}\`\`\``;
}

function pares(file) {
  const ps = makePairs(read(BASE, file), read(WORK, file));
  if (!ps.length) throw new Error(`sem mudança: ${file}`);
  for (const p of ps) if (/^```/m.test(p.from) || /^```/m.test(p.to)) throw new Error(`cerca num par: ${file}`);
  usados.add(file);
  return ps.map((p) => `Em \`${file}\`, trocar:\n\n\`\`\`\n${p.from}\n\`\`\`\n\npor:\n\n\`\`\`\n${p.to}\n\`\`\``).join('\n\n');
}

const extrator = () => `\`\`\`js\n${readFileSync(new URL('extract-plan.mjs', DIR), 'utf8').trimEnd()}\n\`\`\``;

function expandir(md) {
  return md.split('\n').map((line) => {
    if (line.startsWith('@@arquivo ')) return arquivo(line.slice(10).trim());
    if (line.startsWith('@@pares ')) return pares(line.slice(8).trim());
    if (line.startsWith('@@run ')) {
      const [cmd, esperado] = line.slice(6).split(' ::: ');
      return `Run: \`${cmd.trim()}\`\nExpected: ${esperado.trim()}`;
    }
    if (line.startsWith('@@commit ')) {
      const [files, msg] = line.slice(9).split(' ::: ');
      return `- [ ] **Passo final: Commit** (só com o pedido do usuário)\n\n\`\`\`bash\ngit add ${files.trim()}\ngit commit -m "${msg.trim()}" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"\n\`\`\``;
    }
    if (line.trim() === '@@extrator') return extrator();
    if (line.startsWith('@@')) throw new Error(`diretiva desconhecida: ${line}`);
    return line;
  }).join('\n');
}

const partes = ['texto-1-cabecalho.md', 'texto-2-tarefas-1-3.md', 'texto-3-tarefas-4-6.md', 'texto-4-tarefas-7-8.md'];
const texto = partes.map((f) => expandir(readFileSync(new URL(f, DIR), 'utf8').replace(/\r\n/g, '\n'))).join('\n');
if (/\bTODO\b|\bTBD\b/.test(texto)) throw new Error('marcador proibido no plano');
writeFileSync(OUT, texto);
console.log(`plano: ${texto.split('\n').length} linhas, ${usados.size} arquivos`);
export { usados };
