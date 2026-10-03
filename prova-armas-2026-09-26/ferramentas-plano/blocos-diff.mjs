// Os blocos do diff de um arquivo (o `git diff -U0 --minimal`, como o pairs.mjs) e as versões intermediárias dele: a
// base com só os blocos das tarefas até uma dada aplicados. É o que deixa um arquivo que mudou em várias tarefas entrar
// no plano executado pedaço por pedaço — cada tarefa com os pares da versão anterior até a dela —, em vez de inteiro
// numa tarefa só (o plano da 4.1b). Os blocos não se sobrepõem na base, então qualquer subconjunto deles se aplica.
import { execFileSync } from 'node:child_process';
import { mkdtempSync, rmSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { tmpdir } from 'node:os';

/**
 * @returns {{oldStart: number, oldCount: number, newStart: number, newCount: number, antes: string[], depois: string[]}[]}
 *   os blocos em ordem, com o início 0-based nas linhas da base e do final e as linhas tiradas e postas
 */
export function blocosDoDiff(antes, depois) {
  if (antes === depois) return [];
  const dir = mkdtempSync(join(tmpdir(), 'blocos-'));
  const a = join(dir, 'a');
  const b = join(dir, 'b');
  writeFileSync(a, antes);
  writeFileSync(b, depois);
  let out = '';
  try {
    execFileSync('git', ['diff', '--no-index', '--no-color', '-U0', '--minimal', a, b],
      { encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'], maxBuffer: 1 << 28 });
  } catch (err) {
    out = err.stdout; // git diff --no-index sai com 1 quando há diferença
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
  const A = antes.split('\n');
  const B = depois.split('\n');
  const blocos = [];
  for (const linha of out.split('\n')) {
    const m = /^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@/.exec(linha);
    if (!m) continue;
    const oldCount = m[2] === undefined ? 1 : Number(m[2]);
    const newCount = m[4] === undefined ? 1 : Number(m[4]);
    // com contagem 0, o git dá a linha de antes da inserção
    const oldStart = oldCount === 0 ? Number(m[1]) : Number(m[1]) - 1;
    const newStart = newCount === 0 ? Number(m[3]) : Number(m[3]) - 1;
    blocos.push({
      oldStart, oldCount, newStart, newCount,
      antes: A.slice(oldStart, oldStart + oldCount), depois: B.slice(newStart, newStart + newCount),
    });
  }
  if (!blocos.length) throw new Error('diff vazio para textos diferentes');
  // conferência: todos os blocos aplicados dão o final
  if (aplicarBlocos(antes, blocos) !== depois) throw new Error('os blocos não reproduzem o arquivo final');
  return blocos;
}

/** A base com os blocos dados aplicados (qualquer subconjunto dos de `blocosDoDiff`, em qualquer ordem). */
export function aplicarBlocos(antes, blocos) {
  const A = antes.split('\n');
  const saida = [];
  let i = 0;
  for (const b of [...blocos].sort((x, y) => x.oldStart - y.oldStart)) {
    saida.push(...A.slice(i, b.oldStart), ...b.depois);
    i = b.oldStart + b.oldCount;
  }
  saida.push(...A.slice(i));
  return saida.join('\n');
}
