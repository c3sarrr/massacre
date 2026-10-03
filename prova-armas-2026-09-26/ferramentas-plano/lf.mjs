// Normaliza para LF todos os arquivos de texto de uma árvore (inclusive vendor/), fora node_modules e .git.
import { readdirSync, readFileSync, statSync, writeFileSync } from 'node:fs';
import { join, extname } from 'node:path';
const EXT = new Set(['.js', '.mjs', '.py', '.md', '.json', '.html', '.css', '.txt', '.sh', '']);
const SKIP = new Set(['node_modules', '.git', '__pycache__']);
let n = 0;
function walk(dir) {
  for (const nome of readdirSync(dir)) {
    if (SKIP.has(nome)) continue;
    const p = join(dir, nome);
    const st = statSync(p);
    if (st.isDirectory()) walk(p);
    else if (EXT.has(extname(nome)) && st.size < 2e7) {
      const s = readFileSync(p, 'utf8');
      if (s.includes('\r\n')) { writeFileSync(p, s.replace(/\r\n/g, '\n')); n++; }
    }
  }
}
walk(process.argv[2]);
console.log(`${n} arquivos convertidos para LF`);
