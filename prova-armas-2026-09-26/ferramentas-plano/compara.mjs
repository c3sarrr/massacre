// Compara duas árvores (texto com CRLF normalizado para LF): novos, diferentes e ausentes, fora das pastas geradas.
// Uso: node compara.mjs <a> <b>
import { existsSync, readdirSync, readFileSync, statSync } from 'node:fs';
import { join, relative, sep } from 'node:path';

const [a, b] = process.argv.slice(2);
const SKIP = new Set(['node_modules', '.git', '.claude', '__pycache__', 'conferencia']);
const SKIPF = new Set(['tools/blender/local.json']);
function walk(root, dir = root, out = []) {
  for (const n of readdirSync(dir)) {
    if (SKIP.has(n)) continue;
    const p = join(dir, n);
    if (statSync(p).isDirectory()) walk(root, p, out);
    else out.push(relative(root, p).split(sep).join('/'));
  }
  return out;
}
const norm = (p) => readFileSync(p, 'utf8').replace(/\r\n/g, '\n');
const fa = walk(a).filter((f) => !SKIPF.has(f));
const fb = new Set(walk(b).filter((f) => !SKIPF.has(f)));
const res = [];
for (const f of fa) {
  if (!fb.has(f)) res.push(`só em A  ${f}`);
  else if (norm(join(a, f)) !== norm(join(b, f))) res.push(`diferente ${f}`);
  fb.delete(f);
}
for (const f of fb) res.push(`só em B  ${f}`);
console.log(res.length ? res.join('\n') : 'idênticas (com CRLF normalizado)');
