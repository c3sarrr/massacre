// Fins de linha do trabalho iguais aos da base: arquivo que existe na base com CRLF fica CRLF; o resto (LF na base ou
// novo) volta para LF — o projeto é LF, com 16 arquivos antigos em CRLF.
import { existsSync, readdirSync, readFileSync, statSync, writeFileSync } from 'node:fs';
import { join, extname, relative } from 'node:path';
const [work, base] = process.argv.slice(2);
const EXT = new Set(['.js', '.mjs', '.py', '.md', '.json', '.html', '.css', '.txt', '']);
const SKIP = new Set(['node_modules', 'vendor', '.git', '__pycache__', 'conferencia']);
const fixed = [];
function walk(dir) {
  for (const n of readdirSync(dir)) {
    if (SKIP.has(n)) continue;
    const p = join(dir, n);
    const st = statSync(p);
    if (st.isDirectory()) walk(p);
    else if (EXT.has(extname(n)) && st.size < 5e6) {
      const s = readFileSync(p, 'utf8');
      if (!s.includes('\r\n')) continue;
      const b = join(base, relative(work, p));
      const baseCrlf = existsSync(b) && readFileSync(b, 'utf8').includes('\r\n');
      if (!baseCrlf) {
        writeFileSync(p, s.replace(/\r\n/g, '\n'));
        fixed.push(relative(work, p));
      }
    }
  }
}
walk(work);
console.log(`${fixed.length} arquivos voltaram para LF`);
for (const f of fixed) console.log('  ' + f);
