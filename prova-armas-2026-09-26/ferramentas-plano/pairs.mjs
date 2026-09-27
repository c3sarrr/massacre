// Pares "trocar → por" que levam o texto `before` ao `after`, aplicados em ordem como substituição de texto (cada
// "trocar" único no texto do momento). Hunks do `git diff -U0`; contexto de linhas inteiras em volta, crescendo até o
// trecho ficar único; hunks cujo contexto encostaria no seguinte viram um par só. Confere no fim: aplicar dá `after`.
import { execFileSync } from 'node:child_process';
import { mkdtempSync, rmSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { tmpdir } from 'node:os';

function hunksOf(before, after) {
  const dir = mkdtempSync(join(tmpdir(), 'pairs-'));
  const a = join(dir, 'a');
  const b = join(dir, 'b');
  writeFileSync(a, before);
  writeFileSync(b, after);
  let out = '';
  try {
    execFileSync('git', ['diff', '--no-index', '--no-color', '-U0', '--minimal', a, b], { encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'] });
  } catch (err) {
    out = err.stdout; // git diff --no-index sai com 1 quando há diferença
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
  const hunks = [];
  for (const line of out.split('\n')) {
    const m = /^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@/.exec(line);
    if (!m) continue;
    const oldCount = m[2] === undefined ? 1 : Number(m[2]);
    const newCount = m[4] === undefined ? 1 : Number(m[4]);
    // Início 0-based na lista de linhas de `before`/`after` (com contagem 0, o git dá a linha de antes da inserção).
    const oldStart = oldCount === 0 ? Number(m[1]) : Number(m[1]) - 1;
    const newStart = newCount === 0 ? Number(m[3]) : Number(m[3]) - 1;
    hunks.push({ oldStart, oldCount, newStart, newCount });
  }
  return hunks;
}

const count = (text, piece) => text.split(piece).length - 1;

/**
 * @returns {{from: string, to: string}[]} pares na ordem de aplicação
 */
export function makePairs(before, after, { minContext = 1 } = {}) {
  if (before === after) return [];
  const A = before.split('\n');
  const B = after.split('\n');
  const hunks = hunksOf(before, after);
  if (!hunks.length) throw new Error('diff vazio para textos diferentes');
  // Agrupa hunks próximos (≤ 2 linhas iguais entre eles) desde já.
  const groups = [];
  for (const h of hunks) {
    const g = groups.at(-1);
    if (g && h.oldStart - (g.oldStart + g.oldCount) <= 2) {
      g.oldCount = h.oldStart + h.oldCount - g.oldStart;
      g.newCount = h.newStart + h.newCount - g.newStart;
    } else {
      groups.push({ ...h });
    }
  }
  const pairs = [];
  let cur = before;
  let curLines = A.slice();
  let delta = 0; // índice em curLines = índice em A + delta (para o que ainda não foi trocado)
  for (let gi = 0; gi < groups.length; gi++) {
    let g = groups[gi];
    for (;;) {
      const s = g.oldStart + delta; // começo da região em curLines
      const e = s + g.oldCount; // fim (exclusivo)
      const next = groups[gi + 1];
      const nextStart = next ? next.oldStart + delta : curLines.length;
      const newLines = B.slice(g.newStart, g.newStart + g.newCount);
      let found = null;
      for (let k = minContext; ; k++) {
        const pre = Math.max(0, s - k);
        const post = Math.min(e + k, curLines.length);
        if (post > nextStart) break; // o contexto encostaria no próximo grupo: junta
        const fromLines = curLines.slice(pre, post);
        const toLines = [...curLines.slice(pre, s), ...newLines, ...curLines.slice(e, post)];
        const from = fromLines.join('\n');
        if (from.trim() !== '' && count(cur, from) === 1) {
          found = { pre, post, from, to: toLines.join('\n') };
          break;
        }
        if (pre === 0 && post === curLines.length) break;
      }
      if (found) {
        pairs.push({ from: found.from, to: found.to });
        cur = cur.replace(found.from, () => found.to);
        const toLines = found.to.split('\n');
        curLines = [...curLines.slice(0, found.pre), ...toLines, ...curLines.slice(found.post)];
        delta += g.newCount - g.oldCount;
        break;
      }
      if (!groups[gi + 1]) throw new Error('não achou trecho único nem para juntar');
      const n = groups.splice(gi + 1, 1)[0];
      g = { oldStart: g.oldStart, oldCount: n.oldStart + n.oldCount - g.oldStart, newStart: g.newStart,
        newCount: n.newStart + n.newCount - g.newStart };
      groups[gi] = g;
    }
  }
  // Conferência: aplicar os pares em ordem dá `after`.
  let t = before;
  for (const p of pairs) {
    if (count(t, p.from) !== 1) throw new Error(`par não único na aplicação: ${p.from.slice(0, 60)}`);
    t = t.replace(p.from, () => p.to);
  }
  if (t !== after) throw new Error('os pares não reproduzem o arquivo final');
  return pairs;
}
