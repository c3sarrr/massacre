// Plano executado da 4.1a (Tarefa 19 do plano de desenho): o plano de desenho com o código final da execução. Os blocos
// inteiros dos arquivos que a revisão crítica e o aceite mudaram trazem a versão verificada da cópia de trabalho; a
// `tools/regua/lib.js`, que o plano de desenho copiava da pasta da prova, vira bloco; e três passos novos trazem os
// pares "trocar → por" do moodboard (Tarefa 6), da baioneta M9 (Tarefa 17) e do relatório (Tarefa 19). Os pares saem
// do estado depois do plano de desenho aplicado numa cópia limpa (`plano`) até a cópia de trabalho.
// Uso: node plano-executado-4.1a.mjs <plano de desenho.md> <trabalho> <plano aplicado, Tarefas 1–17> <saída.md>
import { readFileSync, writeFileSync } from 'node:fs';
import { makePairs } from './pairs.mjs';

const [DESENHO, WORK, PLANO, OUT] = process.argv.slice(2);
const read = (root, file) => readFileSync(`${root}/${file}`, 'utf8').replace(/\r\n/g, '\n');
let md = readFileSync(DESENHO, 'utf8').replace(/\r\n/g, '\n');

function uma(texto, velho, novo) {
  const n = texto.split(velho).length - 1;
  if (n !== 1) throw new Error(`"${velho.slice(0, 70)}…" aparece ${n} vezes`);
  return texto.replace(velho, () => novo);
}

function semCerca(file, texto) {
  if (/^```/m.test(texto)) throw new Error(`cerca de código dentro de ${file}`);
  return texto;
}

// 1. Blocos inteiros com a versão verificada.
const BLOCOS = [
  'tools/blender/refs/ak47.json', 'src/data/acabamentos.js', 'tools/blender/armas/pecas.py',
  'tools/blender/armas/materiais.py', 'tools/blender/armas/ak47.py', 'tools/blender/armas/assar.py',
  'tools/blender/armas/lod.py', 'src/weapons/model/glsl/acabamentos.js',
];
for (const file of BLOCOS) {
  const re = new RegExp('^(```[a-z]+ file=' + file.replace(/[.*+?^${}()|[\]\\/]/g, '\\$&') + ')\\n[\\s\\S]*?\\n```$', 'm');
  const achados = md.match(new RegExp(re.source, 'gm')) ?? [];
  if (achados.length !== 1) throw new Error(`${file}: ${achados.length} blocos`);
  const texto = semCerca(file, read(WORK, file));
  if (!texto.endsWith('\n')) throw new Error(`sem \\n no fim: ${file}`);
  md = md.replace(re, (_m, cab) => `${cab}\n${texto.slice(0, -1)}\n\`\`\``);
}

// 2. A lib.js da régua como bloco (o plano de desenho copiava da prova e acrescentava o cabeçalho à mão).
const inicioLib = '- [ ] **Passo 5: A página da régua** — `tools/regua/lib.js` é a cópia de';
const fimLib = 'cp ../prova-armas-2026-09-26/refsite/regua/lib.js tools/regua/lib.js\n```\n';
const i0 = md.indexOf(inicioLib);
const i1 = md.indexOf(fimLib, i0);
if (i0 < 0 || i1 < 0) throw new Error('passo da lib.js da régua não encontrado');
md = md.slice(0, i0) + `- [ ] **Passo 5: A página da régua** — \`tools/regua/lib.js\` (as funções da \`tools/silhueta.html\` da 4.1
  exportadas — \`sourceInfo\`, \`loadImage\`, \`weaponMask\`, \`largestComponent\`, \`traceLoops\`, \`area\`, \`simplify\` —, como
  a \`refsite/regua/lib.js\` da prova, com o cabeçalho):

\`\`\`js file=tools/regua/lib.js
${semCerca('tools/regua/lib.js', read(WORK, 'tools/regua/lib.js')).slice(0, -1)}
\`\`\`
` + md.slice(i1 + fimLib.length);

// Pares de um arquivo, do texto `antes` ao `depois`, no formato do executor.
function pares(file, antes, depois, filtro = () => true) {
  const ps = makePairs(antes, depois).filter(filtro);
  if (!ps.length) throw new Error(`sem mudança: ${file}`);
  for (const p of ps) if (/^```/m.test(p.from) || /^```/m.test(p.to)) throw new Error(`cerca num par: ${file}`);
  return ps.map((p) => `Em \`${file}\`, trocar:\n\n\`\`\`\n${p.from}\n\`\`\`\n\npor:\n\n\`\`\`\n${p.to}\n\`\`\``).join('\n\n');
}

// 3. Tarefa 6: as linhas do moodboard que a revisão acrescentou (a planta soviética, o tubo de gases, a janela de ejeção).
const passoMoodboard = `- [ ] **Passo 5: As referências da revisão no moodboard** — as fontes que a revisão crítica usou, na seção 14:

${pares('docs/art/moodboard.md', read(PLANO, 'docs/art/moodboard.md'), read(WORK, 'docs/art/moodboard.md'))}

`;
md = uma(md, '\n---\n\n### Tarefa 7: Assar e níveis de detalhe', `\n${passoMoodboard}---\n\n### Tarefa 7: Assar e níveis de detalhe`);

// 4. Tarefa 17: a faca é a baioneta M9 (decisão do usuário na execução).
// Na tabela de subfases, a linha da 4.1c muda aqui e a da 4.1a (o ✅) na Tarefa 19; vizinhas, o makePairs as juntaria.
const fase4Plano = read(PLANO, 'docs/phases/phase-4.md');
const fase4M9 = uma(fase4Plano, '| 4.1c | Glock-18, M4A4 e a faca de combate no caminho provado, com as empunhaduras | a fazer |',
  '| 4.1c | Glock-18, M4A4 e a faca — a baioneta M9 (EUA, 1986) — no caminho provado, com as empunhaduras | a fazer |');
const passoM9 = `- [ ] **Passo 7: A faca é a baioneta M9** (decisão do usuário de 2026-09-26, na execução): as regras, a tabela de
  subfases e o desenho passam a falar da baioneta M9 (EUA, 1986) no lugar da faca de combate genérica.

${pares('CLAUDE.md', read(PLANO, 'CLAUDE.md'), read(WORK, 'CLAUDE.md'))}

${pares('CLAUDE.md.md', read(PLANO, 'CLAUDE.md.md'), read(WORK, 'CLAUDE.md.md'))}

${pares('docs/phases/phase-4.md', fase4Plano, fase4M9)}

${pares('docs/superpowers/specs/2026-09-26-armas-realistas-design.md', read(PLANO, 'docs/superpowers/specs/2026-09-26-armas-realistas-design.md'), read(WORK, 'docs/superpowers/specs/2026-09-26-armas-realistas-design.md'))}

`;
md = uma(md, '\n---\n\n### Tarefa 18: Aceite no navegador e a revisão crítica', `\n${passoM9}---\n\n### Tarefa 18: Aceite no navegador e a revisão crítica`);

// 5. Tarefa 19: o relatório e o ✅ com os números do aceite, no lugar da instrução de escrever.
const passo1Inicio = '- [ ] **Passo 1: O relatório da subfase** (na cópia de trabalho)';
const passo2Inicio = '- [ ] **Passo 2: Os textos do gerador**';
const j0 = md.indexOf(passo1Inicio);
const j1 = md.indexOf(passo2Inicio, j0);
if (j0 < 0 || j1 < 0) throw new Error('passos 1 e 2 da Tarefa 19 não encontrados');
const passoRelatorio = `- [ ] **Passo 1: O relatório da subfase** — o relatório da 4.1a com os números do aceite no \`docs/PROGRESS.md\`
  (no lugar da seção da 4.2, que passa a ser a próxima depois da 4.1b) e o ✅ na tabela de subfases:

${pares('docs/PROGRESS.md', read(PLANO, 'docs/PROGRESS.md'), read(WORK, 'docs/PROGRESS.md'))}

${pares('docs/phases/phase-4.md', fase4M9, read(WORK, 'docs/phases/phase-4.md'))}

- [ ] **Passo 2: O plano executado** — este documento, gerado do plano de desenho, da cópia de trabalho e de uma cópia
  limpa da base com as Tarefas 1–17 do plano de desenho aplicadas (a origem dos pares), pelas ferramentas de
  \`prova-armas-2026-09-26/ferramentas-plano/\` (fora do repositório; o executor da 4.1a é \`aplica-4.1a.py\`, que entende
  as cercas com linguagem e os "trocar:" em sequência deste formato — o \`validate-plan.mjs\` da 4.1 não):

\`\`\`bash
cd "/c/Users/T-Gamer/Desktop/game tiro"
rm -rf plano-4.1a && cp -r base-4.1a plano-4.1a
python3 prova-armas-2026-09-26/ferramentas-plano/aplica-4.1a.py "Game tiro/docs/superpowers/plans/2026-09-26-4.1a-pipeline-realista-ak47.md" plano-4.1a 1 17
node prova-armas-2026-09-26/ferramentas-plano/plano-executado-4.1a.mjs "Game tiro/docs/superpowers/plans/2026-09-26-4.1a-pipeline-realista-ak47.md" trabalho-4.1a plano-4.1a trabalho-4.1a/docs/phases/phase-4.1a-plan.md
\`\`\`

- [ ] **Passo 3: Validar numa cópia limpa** — uma cópia nova da base e o roteiro \`valida-4.1a.sh\`, tarefa por
  tarefa: só os testes gravados falham, a tarefa inteira faz passar, a suíte inteira passa (370 no fim), o \`construir\`
  do Blender aprovado depois da Tarefa 8 e o vendor regenerado depois da 9; no fim, a comparação com a cópia de
  trabalho não mostra nenhum arquivo diferente fora os binários de \`assets/armas/ak47/\` (conferidos pelas métricas do
  relatório: medidas 0,2 %, IoU 0,002, triângulos 1 %, arquivos 5 %).

\`\`\`bash
cd "/c/Users/T-Gamer/Desktop/game tiro"
rm -rf validacao-4.1a && cp -r base-4.1a validacao-4.1a
bash prova-armas-2026-09-26/ferramentas-plano/valida-4.1a.sh "$PWD/trabalho-4.1a/docs/phases/phase-4.1a-plan.md" validacao-4.1a "$PWD/trabalho-4.1a"
\`\`\`

- [ ] **Passo 4: Aplicar no projeto** — o mesmo roteiro no \`Game tiro\` (que tem a árvore de \`base-4.1a\`), e o plano
  executado ao lado:

\`\`\`bash
cd "/c/Users/T-Gamer/Desktop/game tiro"
bash prova-armas-2026-09-26/ferramentas-plano/valida-4.1a.sh "$PWD/trabalho-4.1a/docs/phases/phase-4.1a-plan.md" "Game tiro" "$PWD/trabalho-4.1a"
cp trabalho-4.1a/docs/phases/phase-4.1a-plan.md "Game tiro/docs/phases/phase-4.1a-plan.md"
\`\`\`

- [ ] **Passo 5: Conferir no navegador** — no servidor do projeto (\`massacre-dev\`), a bancada com a AK (de lado, as
  três skins, os níveis) e a AK na mão na pista, como no passo 2 da Tarefa 18, rapidamente, e o console sem erros.

`;
md = md.slice(0, j0) + passoRelatorio + md.slice(md.indexOf('- [ ] **Passo 6: Arrumar**', j1));

// 6. Cabeçalho e números desta execução.
md = uma(md, '# Subfase 4.1a — Pipeline realista e a AK-47 tipo 3: plano de implementação\n',
  `# Subfase 4.1a — Pipeline realista e a AK-47 tipo 3: plano executado

> **Plano executado (2026-09-26).** É o plano de desenho (\`docs/superpowers/plans/2026-09-26-4.1a-pipeline-realista-ak47.md\`)
> com o código final da execução: os blocos dos arquivos que a revisão crítica e o aceite mudaram — a ficha
> (\`vistaDeCima\` e as correções de lado), a régua, os acabamentos, o pacote do Blender (\`pecas.py\`, \`materiais.py\`,
> \`ak47.py\`, \`assar.py\`, \`lod.py\`) e o shader — trazem a versão verificada, e três passos novos trazem os pares do
> moodboard (Tarefa 6), da baioneta M9 (Tarefa 17) e do relatório (Tarefa 19). Aplicado numa cópia limpa da base pelo
> mesmo executor, reproduz a cópia de trabalho arquivo por arquivo; os binários (\`assets/armas/ak47/\`) o \`construir\`
> regera, conferidos pelas métricas do relatório.
`);
md = uma(md, '(a AK medida na validação deste plano: construída em 77 s, silhueta 98,9 % com tolerância\ne 96,7 % bruta, perto 18 403 · mundo 5 699 · longe 1 425 triângulos, 5,14 MB)',
  '(a AK desta execução: construída em 105 a 150 s, silhueta 99,9 % com tolerância\ne 98,2 % bruta, perto 27 381 · mundo 5 700 · longe 1 425 triângulos, 5,16 MB)');

md = uma(md, 'apagar\n  `validacao-4.1a/`.', 'apagar\n  `validacao-4.1a/` e `plano-4.1a/`.');
md = uma(md, 'a próxima (4.1b, num chat novo: luvas, mangas, rig e solver de empunhadura), como retomar, e o estado do\n  git; a linha',
  'a próxima (4.1b, no mesmo chat por decisão do usuário: luvas, mangas, rig e solver de\n  empunhadura), como retomar, e o estado do git; a linha');
md = uma(md, 'a próxima subfase (4.1b) — sugerindo abrir um chat novo para ela.',
  'a próxima subfase (4.1b), que segue no mesmo chat (decisão do usuário).');

if (/\bTODO\b|\bTBD\b/.test(md)) throw new Error('marcador proibido no plano');
writeFileSync(OUT, md);
console.log(`plano executado: ${md.split('\n').length} linhas`);
