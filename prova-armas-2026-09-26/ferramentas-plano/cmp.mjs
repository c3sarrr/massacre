// Uso: node cmp.mjs <cópia de trabalho> <projeto> — lista arquivos novos, alterados e removidos (sem node_modules etc.).
import { readdirSync, readFileSync } from 'node:fs';
import { join, relative, sep } from 'node:path';

const [a, b] = process.argv.slice(2);
const skip = new Set(['node_modules', '.git', '.claude', 'dist']);
function walk(root, dir = root, out = []) {
  for (const e of readdirSync(dir, { withFileTypes: true })) {
    if (skip.has(e.name)) continue;
    const p = join(dir, e.name);
    if (e.isDirectory()) walk(root, p, out);
    else out.push(relative(root, p).split(sep).join('/'));
  }
  return out;
}
const fa = new Set(walk(a));
const fb = new Set(walk(b));
const res = [];
for (const f of fa) {
  if (!fb.has(f)) res.push(['novo', f]);
  else if (!readFileSync(join(a, f)).equals(readFileSync(join(b, f)))) res.push(['mod', f]);
}
for (const f of fb) if (!fa.has(f)) res.push(['removido', f]);
res.sort((x, y) => x[1].localeCompare(y[1]));
for (const [k, f] of res) console.log(k.padEnd(9), f);
