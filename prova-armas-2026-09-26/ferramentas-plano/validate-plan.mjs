// Aplica o plano numa cópia limpa, na ordem do documento: blocos `file=` (extrator), pares "Em `x`, trocar: … por: …"
// e cada "Run: `cmd`" conferido contra o "Expected:" (FAIL: sai com erro e mostra os trechos citados; PASS: sai limpo,
// com a contagem de testes quando dita). Uso: node validate-plan.mjs <plano.md> <cópia limpa> [tarefa final]
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { spawnSync } from 'node:child_process';

const [planPath, root, lastTask = '7'] = process.argv.slice(2);
const plan = readFileSync(planPath, 'utf8').replace(/\r\n/g, '\n');
const last = Number(lastTask);

// Itens na ordem: [pos, tipo, dados].
const items = [];
for (const m of plan.matchAll(/^### Tarefa (\d+):/gm)) items.push([m.index, 'task', Number(m[1])]);
for (const m of plan.matchAll(/^```[a-z]+ file=(\S+)\n([\s\S]*?)^```$/gm)) items.push([m.index, 'file', { path: m[1], text: m[2] }]);
for (const m of plan.matchAll(/^Em `([^`]+)`, trocar:\n\n```\n([\s\S]*?)\n```\n\npor:\n\n```\n([\s\S]*?)\n```$/gm)) {
  items.push([m.index, 'pair', { path: m[1], from: m[2], to: m[3] }]);
}
for (const m of plan.matchAll(/^Run: `([^`]+)`\nExpected: (PASS|FAIL)(.*)$/gm)) items.push([m.index, 'run', { cmd: m[1], kind: m[2], rest: m[3] }]);
items.sort((a, b) => a[0] - b[0]);

let task = -1;
const log = [];
for (const [, type, data] of items) {
  if (type === 'task') {
    task = data;
    if (task > last) break;
    console.log(`\n=== Tarefa ${task}`);
    continue;
  }
  if (task < 1 || task > last) continue;
  if (type === 'file') {
    const out = join(root, data.path);
    mkdirSync(dirname(out), { recursive: true });
    writeFileSync(out, data.text);
    console.log(`  gravado ${data.path}`);
  } else if (type === 'pair') {
    const f = join(root, data.path);
    // O checkout tem arquivos com CRLF (core.autocrlf): a ferramenta de edição casa os trechos em LF e grava LF.
    const t = readFileSync(f, 'utf8').replace(/\r\n/g, '\n');
    const n = t.split(data.from).length - 1;
    if (n !== 1) throw new Error(`Tarefa ${task}: trecho aparece ${n} vezes em ${data.path}:\n${data.from.slice(0, 200)}`);
    writeFileSync(f, t.replace(data.from, () => data.to));
    console.log(`  par em ${data.path}`);
  } else {
    const r = spawnSync(data.cmd, { cwd: root, shell: true, encoding: 'utf8', maxBuffer: 64 * 1024 * 1024 });
    const out = `${r.stdout}\n${r.stderr}`.replace(/\\\\/g, '/').replace(/\\/g, '/');
    const passN = /# pass (\d+)/.exec(out)?.[1];
    const failN = /# fail (\d+)/.exec(out)?.[1];
    const notOk = [...out.matchAll(/^not ok \d+ - (.*)$/gm)].map((m) => m[1]);
    let ok;
    let why = '';
    if (data.kind === 'PASS') {
      const want = /(\d+) testes passando/.exec(data.rest)?.[1];
      ok = r.status === 0 && (failN === undefined || failN === '0') && (!want || passN === want);
      why = `status ${r.status}, pass ${passN}, fail ${failN}${want ? ` (esperado ${want})` : ''}`;
    } else {
      const quoted = [...data.rest.matchAll(/`([^`]+)`/g)].map((m) => m[1]);
      const named = [...data.rest.matchAll(/"([^"]+)"/g)].map((m) => m[1].replace(/…$/, ''));
      const missing = [...quoted, ...named].filter((q) => !out.includes(q));
      ok = r.status !== 0 && missing.length === 0;
      why = `status ${r.status}, pass ${passN}, fail ${failN}; não achou: ${JSON.stringify(missing)}; not ok: ${JSON.stringify(notOk)}`;
    }
    console.log(`  run ${data.cmd} → ${data.kind} ${ok ? 'OK' : 'ERRO'} (${why})`);
    log.push({ task, cmd: data.cmd, kind: data.kind, ok, why });
    if (!ok) {
      console.log(out.split('\n').filter((l) => /not ok|Error|error:|expected|actual|Cannot find|does not provide/.test(l)).slice(0, 30).join('\n'));
      process.exitCode = 1;
    }
  }
}
console.log(`\n${log.filter((l) => l.ok).length}/${log.length} execuções conforme o esperado`);
