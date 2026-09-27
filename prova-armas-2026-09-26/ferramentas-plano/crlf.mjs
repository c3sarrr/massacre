import { readdirSync, readFileSync, statSync, writeFileSync } from 'node:fs';
import { join, extname } from 'node:path';
const [root, fix] = [process.argv[2], process.argv[3] === '--fix'];
const EXT = new Set(['.js', '.mjs', '.py', '.md', '.json', '.html', '.css', '.txt', '']);
const SKIP = new Set(['node_modules', 'vendor', '.git', '__pycache__', 'conferencia']);
const out = [];
function walk(dir) {
  for (const n of readdirSync(dir)) {
    if (SKIP.has(n)) continue;
    const p = join(dir, n);
    const st = statSync(p);
    if (st.isDirectory()) walk(p);
    else if (EXT.has(extname(n)) && st.size < 5e6) {
      const s = readFileSync(p, 'utf8');
      if (s.includes('\r\n')) {
        out.push(p);
        if (fix) writeFileSync(p, s.replace(/\r\n/g, '\n'));
      }
    }
  }
}
walk(root);
console.log(`${out.length} arquivos com CRLF${fix ? ' (convertidos para LF)' : ''}`);
for (const p of out) console.log('  ' + p);
