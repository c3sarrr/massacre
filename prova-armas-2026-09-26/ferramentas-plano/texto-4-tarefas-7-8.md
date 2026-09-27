### Tarefa 7: Verificação no navegador e no Blender

O servidor de desenvolvimento de outro chat pode estar na 5173: usar `massacre-dev-auto` (porta livre) ou uma configuração própria no `.claude/launch.json` da pasta-mãe (e tirar depois). A aba do jogo tem de ser a da frente do painel (aba de trás não recebe quadros); não emular um tamanho de tela maior que o painel (768 × 432 cabe). O `javascript_tool` corta em 45 s: para esperas longas, rodar em segundo plano e ler o resultado de `window` numa chamada seguinte.

- [ ] **Passo 1: A bancada** — `preview_start`; pelo `javascript_tool`, `massacre.console.execute('arsenal')` (ou `bancada`). Tab abre o painel. Para cada uma das sete (`massacre.states.current.map.bench.select('<id>')` ou o painel): na roda, a costura entre as massas, o boil "em dois", as digitais de perto, os veios da madeira (AK, faca) e o acento certo (Glock e AK terracota/laranja, M4A4 azul/verde-água, as dos dois lados amarelo/branco — trocar a facção no painel muda o acento); "Explodir" separa os grupos; "Âncoras" mostra as mãos e a boca; "Planta" sobrepõe a silhueta; "Medir" dá o IoU (0,873 · 0,931 · 0,937 · 0,945 · 0,894 · 0,947); as fileiras no tapete com as etiquetas, a roda com o suporte de arame, o quadro perfurado com as ferramentas e as plantas a lápis atrás.
- [ ] **Passo 2: Segurar** — no painel, "Segurar": a câmera estaciona e o viewmodel aparece com a arma escolhida e as duas mãos (a faca, uma); "Soltar" volta. Com a arma na mão, "Reler a receita do disco" troca a instância sem erro e sem vazar (`massacre.render.renderer.info.memory.geometries` igual antes e depois).
- [ ] **Passo 3: Primeira pessoa** — `massacre.console.execute('map pista')`, depois `arma glock`, `arma ak47`, `arma m4a4`, `arma awp`, `arma nova`, `arma p90`, `arma knife`: cada uma na mão com a mão direita na empunhadura (o primeiro dedo no gatilho), a esquerda no guarda-mão (pistola: em concha por baixo; faca: só a direita, em punho), a arma no canto de baixo à direita e os cotovelos fora da tela; a arma escurece fora do feixe da key e a mão faz sombra na arma. `viewmodel_presetpos 1`, `2` e `3` e `viewmodel_fov 54`/`68` mudam como no CS; `cl_bracadeira tr` mostra a braçadeira laranja no braço terracota e `cl_bracadeira ct` a azul; `thirdperson`, `noclip`, `kill` e `r_viewmodel 0` escondem o viewmodel; `firstperson`, `noclip` de novo e a volta depois da morte o trazem. `armas` lista as sete com triângulos e tempo de geração.
- [ ] **Passo 4: Memória em 3 ciclos** — colar no `javascript_tool` e ler `window.__ciclos` nas chamadas seguintes (a coleta leva ~2 min):

```js
const m = massacre; const st = m.states;
const mem = () => { const i = m.render.renderer.info; return { g: i.memory.geometries, t: i.memory.textures, p: i.programs?.length ?? null }; };
const wait = (ms) => new Promise((r) => setTimeout(r, ms));
const until = async (f, ms = 60000) => { const t0 = performance.now(); while (!f()) { if (performance.now() - t0 > ms) return false; await wait(200); } return true; };
const R = window.__ciclos = { log: [], errs: [], fim: false };
const oe = console.error; console.error = (...a) => { R.errs.push(a.map(String).join(' ').slice(0, 200)); oe(...a); };
const naMapa = (id) => () => st.name === 'match' && st.current?.map?.id === id && !st.busy;
const noMenu = () => st.name === 'menu' && !st.busy;
(async () => {
  if (!noMenu()) { await st.go('menu'); await until(noMenu); } await wait(1500); R.log.push(['menu0', mem()]);
  for (let c = 1; c <= 3; c++) {
    m.console.execute('arsenal'); await until(naMapa('arsenal')); await wait(3500); R.log.push([`arsenal${c}`, mem()]);
    await st.go('menu'); await until(noMenu); await wait(1500); R.log.push([`menu-a${c}`, mem()]);
    m.console.execute('map pista'); await until(naMapa('pista')); await wait(3500); R.log.push([`pista${c}`, mem()]);
    await st.go('menu'); await until(noMenu); await wait(1500); R.log.push([`menu-p${c}`, mem()]);
  }
  console.error = oe; R.fim = true;
})();
```

  Esperado: os mesmos números no menu nas três voltas (na implementação verificada, 27/35/35 em geometrias/texturas/programas; arsenal 76/43/51; pista 68/92/59) e `errs` vazio.
- [ ] **Passo 5: O caminho do Blender** — `npm run blender -- ida-volta todas` (as sete idênticas); `npm run blender -- conferir todas` e olhar os PNGs (a lateral com a planta laranja batendo na silhueta, as mãos nas âncoras, a primeira pessoa igual à do jogo); `npm run blender -- abrir ak47`: a janela abre sem a tela de abertura, na lateral ortográfica, com a aba MASSACRE; escalar a massa de mira (`massaMira`) ×1,6 (a origem está no centro dela: cresce no lugar), "Prévia do jogo" (a malha do jogo aparece por cima, com a bola maior), "Exportar" (grava `src/data/armas/ak47.js`, validada); no jogo, `arsenal`, a AK na roda, Tab → "Reler a receita do disco": a bola maior na massa de mira (topo de 2,017 u → 2,46 u na malha do grupo `corpo`). Voltar a receita (`git checkout -- src/data/armas/ak47.js` ou a cópia guardada antes), reler e conferir 2,017 u de novo.
- [ ] **Passo 6: Console sem erros do jogo** em todos os passos; arquivos abaixo de 600 linhas (`src/clay/sdf/shapes.js`, o maior tocado, com 541).

---

### Tarefa 8: Documentação, moodboard e memória

- [ ] **Passo 1:** `docs/art/moodboard.md` — os 14 boards novos na tabela (QPG, QPL, QCG, QRF, QSG, NFS, CMH, QHH, CTL, QGW, QPB, QTT, QWS, QBP), a nota de que entram com todos os pins na ordem da busca/board e o item 13 (armas, mãos e a bancada) só com os pins estudados (pin → decisão → arquivo) e as fotos do Commons; `docs/art/pinterest-boards.json` com os pins dos 14 boards; `tools/moodboard.mjs` com os boards novos (o par abaixo); `npm run moodboard`.

@@pares tools/moodboard.mjs

- [ ] **Passo 2:** `docs/phases/phase-4.md` — 4.1 ✅ com a data na tabela de estado; na seção 4.1, o aceite marcado com os números, "Ajustes feitos na implementação" e "Medições".
- [ ] **Passo 3:** `docs/PROGRESS.md` — "Como rodar" com o `npm run blender`; a decisão do Blender em "Ferramentas externas"; os serviços `weaponModels` e `handModels` nas convenções; a seção da Fase 4 com a subfase 4.1 (o que entrou, como testar, números, checklist) e a próxima (4.2 — Tiro e dano).
- [ ] **Passo 4:** memória do projeto (`massacre-game-project.md`): 4.1 pronta; o caminho do Blender (executável em `tools/blender/local.json`); próxima a 4.2.
- [ ] **Passo 5:** encerrar pedindo um chat novo para a 4.2.
