// Sonda: para cada tarefa k, parte da base com as tarefas < k aplicadas (arquivos finais do trabalho), grava os testes
// da tarefa k e roda só eles (a falha esperada); depois aplica a tarefa k e roda a suíte (a contagem).
// Uso: node sonda.mjs <trabalho> <base limpa> <pasta temporária>
import { cpSync, mkdirSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { spawnSync } from 'node:child_process';
import { TAREFAS } from './tarefas.mjs';

const [work, base, tmp] = process.argv.slice(2);
const copia = (root, file) => {
  const out = join(root, file);
  mkdirSync(dirname(out), { recursive: true });
  writeFileSync(out, readFileSync(join(work, file), 'utf8').replace(/\r\n/g, '\n'));
};
rmSync(tmp, { recursive: true, force: true });
cpSync(base, tmp, { recursive: true });
for (const k of Object.keys(TAREFAS).map(Number)) {
  const t = TAREFAS[k];
  for (const f of t.testes) copia(tmp, f);
  if (t.testes.length) {
    const r = spawnSync('node', ['--test', ...t.testes], { cwd: tmp, encoding: 'utf8', maxBuffer: 1 << 26 });
    const out = `${r.stdout}\n${r.stderr}`;
    const linhas = out.split('\n').filter((l) => /not ok|Error|ERR_|Cannot find|does not provide|# (pass|fail)/.test(l));
    console.log(`\n=== Tarefa ${k} — antes (status ${r.status})\n${[...new Set(linhas)].slice(0, 14).join('\n')}`);
  }
  for (const f of [...t.novos, ...t.pares]) copia(tmp, f);
  const r = spawnSync('npm', ['test'], { cwd: tmp, encoding: 'utf8', shell: true, maxBuffer: 1 << 26 });
  const out = `${r.stdout}\n${r.stderr}`;
  console.log(`=== Tarefa ${k} — depois: ${/# pass (\d+)/.exec(out)?.[1]} passando, ${/# fail (\d+)/.exec(out)?.[1]} falhando`);
  if (!/# fail 0/.test(out)) console.log(out.split('\n').filter((l) => /not ok|Error/.test(l)).slice(0, 10).join('\n'));
}
