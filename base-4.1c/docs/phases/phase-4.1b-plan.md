# Subfase 4.1b — Luvas, braço de massinha e empunhadura: plano executado

> **Plano executado** (Tarefa 15 do plano de desenho, `docs/superpowers/plans/2026-09-26-4.1b-luvas-e-empunhadura.md`): o plano de desenho inteiro, com as notas
> da execução, e depois de cada tarefa o código verificado dela — gerado por `prova-armas-2026-09-26/ferramentas-plano/
> plano-executado-4.1b.mjs` a partir de `base-4.1b` (o `Game tiro` depois da 4.1a) e `trabalho-4.1b`. Cada arquivo entra
> numa tarefa só, na versão final; a ordem segue os imports: o `src/data/luvas.js` entra com a ficha (Tarefa 2); o solver
> inteiro e a saída da pega entram com a construção das luvas (Tarefa 6), porque o `principal.py` chama o solver no
> `construir` de cada arma e o `luvas.py` fecha as poses de teste até o contato; os documentos que mudaram em várias
> tarefas entram na 13 e na 15. Os binários de `assets/` saem do `construir` (Tarefa 6: as luvas e a AK).
> **Como aplicar:** `python3 prova-armas-2026-09-26/ferramentas-plano/aplica-4.1a.py <este plano> <raiz> <primeira>
> <última>` grava os blocos `file=` e aplica os pares em ordem (cada "trocar" é único no arquivo naquele momento); o
> validador `valida-4.1b.sh` faz isso numa cópia limpa da base, tarefa por tarefa, com os testes falhando antes e
> passando depois e a suíte inteira passando no fim de cada tarefa.


> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** a AK-47 segurada em primeira pessoa por luvas táticas realistas feitas no Blender — esqueleto de 20 ossos por
braço, pega resolvida por um solver contra a malha da arma —, com o antebraço de massinha do boneco (sem boil) e a
braçadeira de massa, nas duas facções, sem dedo atravessando nem flutuando (medido no Blender e no jogo); mais o
rebatedor branco na bancada `arsenal`.

**Architecture:** no Blender, o pacote `tools/blender/armas/` ganha a ficha das luvas (`refs/luvas.json`), o gerador
de quadriláteros (`maos.py`), os detalhes (`maos_detalhes.py`), o rig e os pesos (`maos_rig.py`), a validação
(`validar_maos.py`) e o solver (`empunhadura.py`); o `principal.py` ganha o alvo `luvas` e roda o solver no `construir`
de cada arma, que passa a levar a pega no `.glb` (nós `pega_mao_*`, clipe `empunhadura`, marca do rig). No jogo,
`src/data/luvas.js`, os acabamentos novos, `luvasSource.js`, `bracoLuva.js` e `antebracoMassa.js` em
`src/characters/hands/`, o viewmodel escolhendo luvas (arma com pega) ou massinha (as outras, até a 4.1d), a bancada, os
comandos `luvas`/`luvas_contato` e o rebatedor.

**Tech Stack:** Blender 5.2.2 (`bpy`, `bmesh`, `mathutils.bvhtree`, Cycles para assar, exportador glTF com skins e
Draco); three 0.186.1 (`SkinnedMesh`, `AnimationClip`, `three-mesh-bvh` do vendor para o `luvas_contato`); `node --test`.

**Desenho:** `docs/superpowers/specs/2026-09-26-4.1b-luvas-e-empunhadura-design.md` (aprovado em 2026-09-26) e a seção 7
do desenho geral (`docs/superpowers/specs/2026-09-26-armas-realistas-design.md`), com as mudanças do usuário.

---

## Como este plano é executado

1. **Cópia de trabalho.** Tudo acontece em `game tiro/trabalho-4.1b` (cópia do `Game tiro` depois da 4.1a); a base
   intocada fica em `game tiro/base-4.1b`. O servidor `massacre-trabalho` (porta 5176) serve a cópia de trabalho.
2. **Formato deste plano.** É o plano de desenho, no formato em que a 4.1 foi executada: tarefas, arquivos, contratos
   (formatos de dados e assinaturas), casos de teste com as asserções, comandos e números. O código completo de cada
   passo sai do diff da cópia de trabalho no **plano executado** (`docs/phases/phase-4.1b-plan.md`), gerado por script,
   validado numa cópia limpa (cada tarefa: os testes novos falham antes e passam depois; a suíte inteira passa) e
   aplicado no projeto pelo mesmo executor, como na 4.1a. Motivo: o modelo orgânico da luva e o solver dependem de
   iteração com renders e revisão crítica, que código escrito antes de rodar não acerta de primeira (na 4.1a, a revisão
   reescreveu `ak47.py`, `pecas.py`, `assar.py`, `lod.py` e o shader do plano de desenho).
3. **TDD.** Nas tarefas com código do jogo ou do Node, o teste vem antes e falha pelo motivo certo; no Blender, a
   validação do `construir` é o teste (bloqueia a exportação) e cada tarefa roda o `construir` de verdade.
4. **Paradas de conferência** (o usuário confere antes de seguir): **P1** depois da Tarefa 6 (as vistas da luva e as
   poses de teste) e **P2** depois da Tarefa 11 (a AK segurada em primeira pessoa nas duas facções, mais as vistas de
   perto do Blender).
5. **Revisão crítica** (regra do usuário): em cada vista, comparar com as referências da seção 15 do moodboard e
   corrigir o que estiver medíocre antes da parada; registrar achado → correção.
6. **Commit só a pedido do usuário.**

## Decisões de execução

- **D1 — Formato da pega no `.glb` da arma.** Preferido: animação glTF `empunhadura` com os canais nos ossos de uma
  armadura só de ossos (`pega_luvas`) dentro do `.glb` da arma, com os mesmos nomes dos ossos do `luvas.glb`. Reserva,
  se a prova da Tarefa 1 mostrar que o exportador não grava ossos sem skin: os mesmos quaternions em
  `extras.empunhadura.ossos` do nó `pega` e o jogo monta o `AnimationClip`. O jogo lê as duas formas pela mesma função
  (`lerPega`), e a escolha fica registrada aqui ao fim da Tarefa 1.
  **Resultado da prova (2026-09-26): vale a animação.** O exportador do Blender 5.2.2 grava a armadura sem malha como
  nós (com um `skin` sem malha, só com as juntas) e a ação de 1 quadro como a animação `empunhadura`, com os canais
  `translation`/`rotation`/`scale` de cada osso; o `GLTFLoader` do three r186 dá as trilhas `<osso>.quaternion`, e
  aplicadas por nome no esqueleto de um `.glb` com skin comprimido no Draco (juntas e pesos dentro do Draco) a pose bate
  com a do Blender a 0,003–0,005 mm num objeto de 15 cm. O jogo usa só as trilhas `quaternion` dos ossos de dedo; a
  forma de reserva (`extras`) não é implementada.
- **D2 — Nomes dos ossos:** `antebraco`, `torcao`, `mao`, `polegar_1..3`, `indicador_1..3`, `medio_1..3`, `anelar_0..3`,
  `minimo_0..3`, com o sufixo `_d`/`_e`. Nós do `.glb` da arma: `pega` (grupo), `pega_mao_d`, `pega_mao_e`.
- **D3 — Referencial das luvas:** Blender: pulso na origem, +X pontas, +Z costas, +Y polegar (mão direita); `.glb`: +X
  pontas, +Y costas, −Z polegar (o das mãos da 4.1). Escala: mm na ficha, metro no Blender (`S`), u no `.glb`
  (`U_POR_M`), como as armas.
- **D4 — Marca do rig:** SHA-256 dos comprimentos dos ossos e dos quaternions da pose de repouso (arredondados a 1e-5),
  gravado no relatório e nos `extras` do `luvas.glb` e do `.glb` de cada arma; o jogo compara as duas.
- **D5 — Hash das entradas das armas:** passa a incluir `refs/luvas.json` (os `.py` do pacote já entram todos); mudar
  as luvas refaz a pega de todas as armas no próximo `construir`.
- **D6 — Orçamento das luvas** em `src/data/luvas.js`: 14 000 triângulos nos dois braços, textura 2048, 6 MB.

## Arquivos

**Criar**
- `tools/blender/refs/luvas.json` — a ficha das luvas (seção 2 do desenho).
- `tools/blender/armas/maos.py` — ficha → juntas e ossos na pose de repouso → malha de quadriláteros (palma, dedos,
  pontas, punho) com as costuras marcadas e o osso de cada anel.
- `tools/blender/armas/maos_detalhes.py` — protetor de borracha dos nós, almofadas, pontas reforçadas, reforço da palma,
  tira de velcro e puxador (jogo e alto); costuras, rugas, nervuras, grão e trama (só no alto).
- `tools/blender/armas/maos_rig.py` — armadura de 20 ossos por braço, pesos, espelho para o braço esquerdo, poses de
  teste.
- `tools/blender/armas/validar_maos.py` — medidas-chave, orçamentos, nomes, pesos, poses de teste, UV, marca do rig.
- `tools/blender/armas/empunhadura.py` — o solver, as regras por categoria (a do fuzil nesta subfase), a validação e a
  saída da pega.
- `src/characters/hands/fichaLuvas.js` — a validação da ficha e as escalas (como a `ficha.js` das armas).
- `src/data/luvas.js` — registro das luvas (pasta, zonas, ossos, orçamento, pinturas por facção, braço de massinha).
- `src/characters/hands/luvasSource.js` — carga do `.glb` e das texturas, materiais por facção, cache e descarte.
- `src/characters/hands/bracoLuva.js` — um braço: malha com esqueleto próprio, pega, pulso, antebraço, torção, facção,
  braçadeira.
- `src/characters/hands/antebracoMassa.js` — a árvore SDF do antebraço de massinha (pura) e o material sem boil.
- `src/characters/hands/pega.js` — `lerPega` (os nós, o clipe ou os `extras`, a marca) e `contatoDasLuvas` (a medida do
  `luvas_contato`).
- `src/debug/luvasCommands.js` — os comandos `luvas` e `luvas_contato`.
- `src/maps/arsenal/rebatedor.js` — o rebatedor da vitrine.
- Testes: `tests/fichaLuvas.test.js`, `tests/luvasSaida.test.js`, `tests/luvasGlb.test.js`, `tests/pegaGlb.test.js`,
  `tests/materialLuva.test.js`, `tests/luvasSource.test.js`, `tests/bracoLuva.test.js`, `tests/luvasCommand.test.js`,
  `tests/rebatedor.test.js`.

**Alterar**
- `tools/blender/armas/principal.py` (alvo `luvas`; solver no `construir` das armas), `assar.py`
  (`uv_por_costuras`), `materiais.py` (couro, tecido, borracha), `exportar.py` (skins; a pega), `conferir.py` (vistas de
  perto das mãos), `ak47.py` (correções de pega, se precisar).
- `tools/blender.mjs` (alvo `luvas`; `luvas.json` no hash das armas), `tools/blender/saida.mjs` (validação da saída das
  luvas e da pega das armas).
- `src/data/acabamentos.js`, `src/weapons/model/materialArma.js` e `glsl/acabamentos.js` (couro, tecido com brilho de
  tecido, borracha; trama e grão procedurais).
- `src/weapons/model/glbSource.js` e `glbWeapon.js` (`info.pega`, `hands: true` quando a arma tem pega).
- `src/weapons/viewmodel/viewmodel.js`, `placement.js`, `src/data/viewmodel.js` (luvas × massinha, facção, cotovelos do
  `rifle`, sombra própria e oclusão com as luvas).
- `src/main.js` (o serviço das luvas), `src/maps/arsenal/bench.js`, `panel.js`, `index.js`, `src/data/arsenal.js`
  (Segurar com luvas, facção, rebatedor), `src/debug/weaponCommands.js` (registro dos comandos novos).
- Documentos: `CLAUDE.md`, `CLAUDE.md.md`, o desenho geral, `docs/phases/phase-4.md`, `docs/PROGRESS.md`,
  `docs/art/moodboard.md`; memória.

---

### Tarefa 0: Cópias de trabalho e servidor

- [ ] **Passo 1: As cópias** — `base-4.1b` e `trabalho-4.1b` a partir do `Game tiro` (sem o `.git` e sem
  `tools/blender/conferencia/`; com `node_modules` e `tools/blender/local.json`, que o `construir` e a suíte usam):

```bash
cd "/c/Users/T-Gamer/Desktop/game tiro"
for d in base-4.1b trabalho-4.1b; do mkdir "$d" && (cd "Game tiro" && tar cf - --exclude=./.git --exclude=./tools/blender/conferencia .) | (cd "$d" && tar xf -); done
diff -rq "Game tiro" base-4.1b -x .git -x conferencia && echo iguais
```

- [ ] **Passo 2: Contagem de partida** — nas duas cópias: `node --test --test-reporter=tap "tests/**/*.test.js" | grep -E "^# (tests|pass|fail)"`
  → `# tests 370`, `# pass 370`, `# fail 0`.
- [ ] **Passo 3: Servidor** — entrada `massacre-trabalho` no `.claude/launch.json` da pasta-mãe
  (`"runtimeArgs": ["trabalho-4.1b/tools/dev-server.mjs", "5176"]`, porta 5176); `preview_start`; `map arsenal` sem
  erro no console.


### Tarefa 1: Provas técnicas (riscos da seção 10 do desenho)

Fora do projeto, no rascunho da sessão; decide a D1.

- [ ] **Passo 1: Skin com Draco** — script do Blender que monta um cilindro com 3 ossos e pesos, exporta `.glb` com
  `export_skins=True` e Draco (posição 14 bits, genéricos 12) e grava ao lado a posição de 3 vértices numa pose
  conhecida. No navegador (servidor da cópia de trabalho, página de teste no rascunho servida pelo mesmo servidor),
  `GLTFLoader` + `DRACOLoader` carregam; a pose aplicada nos ossos dá as mesmas posições (±0,05 mm na escala real).
- [ ] **Passo 2: Pose sem skin** — o mesmo script exporta só a armadura (sem malha) com uma ação de 1 quadro, com
  `export_animations=True`; conferir no JSON do `.glb` que os ossos viraram nós e que a animação tem os canais neles; no
  navegador, o `AnimationClip` carregado tem trilhas `<osso>.quaternion` e, aplicado ao esqueleto do Passo 1 por
  `AnimationMixer` (ou copiando os quaternions do primeiro quadro), dá a mesma pose.
- [ ] **Passo 3: Registrar a D1** — escrever aqui qual forma vale (animação ou `extras`) e o porquê.


### Tarefa 2: Ficha das luvas

**Files:** Create `tools/blender/refs/luvas.json`, `src/characters/hands/fichaLuvas.js` (a validação, como a
`ficha.js` das armas), `tests/fichaLuvas.test.js`.

- [ ] **Passo 1: Testes** — `tests/fichaLuvas.test.js`:
  - `validarFichaLuvas(json)` (em `src/characters/hands/fichaLuvas.js`) aceita a ficha real e devolve a mesma
    estrutura congelada; `escalasDaFicha` dá as escalas de Greiner para a mão da ficha;
  - recusa ficha sem `fontes`, sem algum dos cinco dedos, com comprimento de osso ≤ 0 ou sem a fonte de um grupo de
    medidas, com a mensagem apontando o campo;
  - a ficha real tem: `mao.comprimento.mm = 189.3`, `mao.largura.mm = 85`, os 19 comprimentos de osso da tabela da
    seção 2 do desenho (Buryanov & Kotiuk), as larguras/circunferências do Greiner com `escala = 85/90.4`, os limites
    da AAOS e a espessura da luva;
  - coerência: do pulso à ponta do médio (carpo + metacarpo + 3 falanges + polpa, com o carpo da ficha) = 189,3 ± 1 %.
- [ ] **Passo 2: Rodar e ver falhar** — `node --test tests/fichaLuvas.test.js` → falha por `validarFichaLuvas` não existir.
- [ ] **Passo 3: A ficha** — `refs/luvas.json` com `formato: 1`, `fontes` (ANSUR II, Buryanov & Kotiuk 2010, Greiner
  1991, AAOS, as referências visuais), `mao`, `ossos`, `juntas` (com `escala`), `carpo` (as posições das CMC e o
  carpo do médio, dedução registrada), `limites`, `repouso`, `luva`, `antebraco` (comprimento de 260 mm; largura e
  espessura no pulso da ficha).
- [ ] **Passo 4: O validador** — `problemasDaFichaLuvas`, `validarFichaLuvas` e `escalasDaFicha` em
  `src/characters/hands/fichaLuvas.js` (funções puras).
- [ ] **Passo 5: Rodar e ver passar**; **Passo 6: suíte inteira** (371+).


**Código da tarefa** (a versão verificada no navegador e no Blender; os blocos `file=` são o arquivo inteiro, os pares são aplicados na ordem).

- [ ] **Os testes** — `tests/fichaLuvas.test.js`, `tests/luvasDados.test.js`:

```js file=tests/fichaLuvas.test.js
// Ficha das luvas (Fase 4.1b; desenho em docs/superpowers/specs/2026-09-26-4.1b-luvas-e-empunhadura-design.md,
// seção 2): tools/blender/refs/luvas.json com as medidas da mão e de cada osso, as larguras nas juntas, os limites das
// juntas e a luva, cada grupo com a fonte. O Blender constrói a luva só com o que está aqui; o Node confere antes.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import {
  DEDOS, OSSOS_DO_DEDO, escalasDaFicha, perimetroRetanguloArredondado, problemasDaFichaLuvas, validarFichaLuvas,
} from '../src/characters/hands/fichaLuvas.js';

const ler = () => JSON.parse(readFileSync(new URL('../tools/blender/refs/luvas.json', import.meta.url), 'utf8'));

test('ficha das luvas: formato 1, válida, congelada, com as seis fontes', () => {
  const f = validarFichaLuvas(ler());
  assert.equal(f.formato, 1);
  assert.equal(f.id, 'luvas');
  assert.ok(Object.isFrozen(f) && Object.isFrozen(f.ossos.medio) && Object.isFrozen(f.juntas.medio.pip));
  for (const fonte of ['ansur2', 'ansur2Explorador', 'buryanov', 'greiner', 'aaos', 'referencias']) {
    assert.ok(f.fontes[fonte].titulo.length > 10 && /^https:\/\//.test(f.fontes[fonte].url), fonte);
  }
  assert.deepEqual(DEDOS, ['polegar', 'indicador', 'medio', 'anelar', 'minimo']);
});

test('ficha das luvas: os números das fontes, como publicados', () => {
  const f = ler();
  assert.equal(f.mao.comprimento.mm, 189.3);
  assert.equal(f.mao.largura.mm, 85);
  assert.equal(f.mao.palma.mm, 113.9);
  assert.equal(f.mao.circunferencia.mm, 203.9);
  assert.equal(f.mao.pulso.mm, 169);
  // ANSUR II no Data Explorer do OPEN Design Lab: medianas dos dois sexos.
  assert.deepEqual([f.antebraco.circunferenciaFlexionado.mm, f.antebraco.pulso.mm], [285, 165]);
  // Buryanov & Kotiuk (2010), tabela I.
  const b = f.ossos;
  assert.deepEqual([b.polegar.metacarpo, b.polegar.proximal, b.polegar.distal, b.polegar.polpa], [46.22, 31.57, 21.67, 5.67]);
  assert.deepEqual([b.indicador.metacarpo, b.indicador.proximal, b.indicador.media, b.indicador.distal, b.indicador.polpa], [68.12, 39.78, 22.38, 15.82, 3.84]);
  assert.deepEqual([b.medio.metacarpo, b.medio.proximal, b.medio.media, b.medio.distal, b.medio.polpa], [64.6, 44.63, 26.33, 17.4, 3.95]);
  assert.deepEqual([b.anelar.metacarpo, b.anelar.proximal, b.anelar.media, b.anelar.distal, b.anelar.polpa], [58, 41.37, 25.65, 17.3, 3.95]);
  assert.deepEqual([b.minimo.metacarpo, b.minimo.proximal, b.minimo.media, b.minimo.distal, b.minimo.polpa], [53.69, 32.74, 18.11, 15.96, 3.73]);
  // Greiner (1991), médias dos homens.
  const j = f.juntas;
  assert.deepEqual([j.polegar.ip.largura, j.polegar.ip.circunferencia], [24, 72.3]);
  assert.deepEqual(['indicador', 'medio', 'anelar', 'minimo'].map((d) => j[d].pip.largura), [23, 22.5, 21.4, 19.2]);
  assert.deepEqual(['indicador', 'medio', 'anelar', 'minimo'].map((d) => j[d].pip.circunferencia), [68.4, 69.6, 64.9, 57.8]);
  assert.deepEqual(['medio', 'anelar', 'minimo'].map((d) => j[d].dip.largura), [19.8, 18.5, 17.4]);
  assert.deepEqual(['indicador', 'medio', 'anelar', 'minimo'].map((d) => j[d].dip.circunferencia), [57.4, 57.8, 53.8, 49.2]);
  assert.deepEqual([j.pulso.largura, j.pulso.circunferencia], [65.8, 174.3]);
  assert.deepEqual(DEDOS.map((d) => j.pontaAoPulso[d]), [137.9, 185.2, 194.5, 185, 159.9]);
  assert.equal(j.larguraDaMao, 90.4);
  assert.deepEqual([j.dobras.polegarIndicador, j.dobras.indicadorMedio, j.dobras.medioAnelar, j.dobras.anelarMinimo], [69.1, 110.4, 109.9, 96.6]);
  assert.equal(j.cotoveloAoPulso, 290);
  // AAOS.
  const l = f.limites;
  assert.deepEqual([l.mcp, l.pip, l.dip, l.abertura], [[0, 90], [0, 100], [0, 90], [-20, 20]]);
  assert.deepEqual([l.polegar.cmcAbducao, l.polegar.cmcFlexao, l.polegar.mcp, l.polegar.ip], [[0, 70], [-20, 15], [0, 50], [0, 80]]);
  assert.deepEqual(l.pulso, { flexao: 80, extensao: 70, radial: 20, ulnar: 30 });
  assert.deepEqual(l.antebraco, { pronacao: 80, supinacao: 80 });
  // Cooney (1981): a rotação axial da CMC do polegar.
  assert.deepEqual(f.rotacaoDoPolegar.cmc, [0, 17]);
  assert.equal(f.rotacaoDoPolegar.fonte, 'cooney');
});

test('ficha das luvas: as escalas das médias dos homens para a mão da ficha', () => {
  const e = escalasDaFicha(ler());
  assert.ok(Math.abs(e.comprimento - 189.3 / 194.5) < 1e-12, 'comprimento pela ponta do médio ao pulso');
  assert.ok(Math.abs(e.largura - 85 / 90.4) < 1e-12, 'largura pela largura da mão');
});

test('ficha das luvas: cada dedo cabe entre o pulso e a ponta, o médio é o mais longo e o mínimo o mais curto', () => {
  const f = ler();
  const e = escalasDaFicha(f);
  const comprimento = (d) => OSSOS_DO_DEDO[d].filter((o) => o !== 'metacarpo').reduce((s, o) => s + f.ossos[d][o], 0);
  for (const d of DEDOS.slice(1)) {
    const mcp = f.juntas.pontaAoPulso[d] * e.comprimento - comprimento(d);
    const cmc = mcp - f.ossos[d].metacarpo;
    assert.ok(cmc > 20 && cmc < 45, `${d}: a base do metacarpo a ${cmc.toFixed(1)} mm do pulso`);
  }
  const pontas = DEDOS.slice(1).map((d) => f.juntas.pontaAoPulso[d]);
  assert.equal(Math.max(...pontas), f.juntas.pontaAoPulso.medio);
  assert.equal(Math.min(...pontas), f.juntas.pontaAoPulso.minimo);
  assert.ok(Math.abs(f.juntas.pontaAoPulso.medio * e.comprimento - f.mao.comprimento.mm) < 0.05, 'a ponta do médio é o comprimento da mão');
});

test('ficha das luvas: a luva, o repouso e as deduções com o porquê', () => {
  const f = ler();
  for (const k of ['tecido', 'couro', 'almofada', 'protetor', 'tira', 'punho', 'folgaPunho']) assert.ok(f.luva[k] > 0, `luva.${k}`);
  assert.ok(f.luva.nota.length > 20);
  for (const k of ['mcp', 'pip', 'dip', 'abertura', 'polegarAbducao', 'polegarMcp', 'polegarIp']) assert.ok(Number.isFinite(f.repouso[k]), `repouso.${k}`);
  for (const [nome, d] of Object.entries(f.deducoes)) assert.ok(typeof d.porque === 'string' && d.porque.length > 20, `deducoes.${nome}.porque`);
  assert.ok(f.deducoes.polegar.cmc.length === 3 && Number.isFinite(f.deducoes.polegar.anguloNaPalma));
  assert.ok(f.deducoes.pulso.espessura > 30 && f.deducoes.antebraco.divisao > 0 && f.deducoes.antebraco.divisao < 1);
  assert.ok(f.deducoes.leque.fator > 0 && f.deducoes.leque.fator < 1);
  assert.deepEqual(Object.keys(f.deducoes.arco.mm), ['indicador', 'medio', 'anelar', 'minimo']);
  assert.deepEqual(Object.keys(f.deducoes.convergencia.graus), ['indicador', 'medio', 'anelar', 'minimo']);
  assert.ok(f.deducoes.espessuraDaMao.mm > 20 && f.deducoes.espessuraDaMao.mm < 40);
});

test('ficha das luvas: as seções de retângulo arredondado batem com as circunferências', () => {
  const f = ler();
  const e = escalasDaFicha(f);
  const d = f.deducoes;
  // O pulso: a largura de Greiner na escala da ficha e a espessura e o raio deduzidos dão a circunferência do ANSUR II.
  const pulso = perimetroRetanguloArredondado(f.juntas.pulso.largura * e.largura, d.pulso.espessura, d.pulso.raio);
  assert.ok(Math.abs(pulso - f.mao.pulso.mm) < 1, `pulso: ${pulso.toFixed(1)} mm`);
  // A mão nos nós: a largura e a espessura com o raio deduzido ficam a ±2 % da circunferência do ANSUR II.
  const nos = perimetroRetanguloArredondado(f.mao.largura.mm, d.espessuraDaMao.mm, d.espessuraDaMao.raio);
  assert.ok(Math.abs(nos / f.mao.circunferencia.mm - 1) < 0.02, `nós: ${nos.toFixed(1)} mm`);
  // O antebraço: a razão das medianas aplicada ao pulso da ficha; o expoente deixa o terço do pulso quase reto.
  const p = d.perfilDoAntebraco;
  assert.ok(Math.abs(p.circunferenciaNoCotovelo - f.mao.pulso.mm * f.antebraco.circunferenciaFlexionado.mm / f.antebraco.pulso.mm) < 0.05);
  assert.ok(p.expoente > 1 && p.expoente < 2);
  const comprimento = f.juntas.cotoveloAoPulso * e.comprimento;
  const naBoca = f.mao.pulso.mm + (p.circunferenciaNoCotovelo - f.mao.pulso.mm) * (f.luva.punho / comprimento) ** p.expoente;
  assert.ok(naBoca / f.mao.pulso.mm > 1.04 && naBoca / f.mao.pulso.mm < 1.1, `na boca do punho: ${naBoca.toFixed(1)} mm`);
});

test('ficha das luvas: cada problema aparece com o campo', () => {
  const ruim = ler();
  delete ruim.fontes.greiner;
  delete ruim.ossos.anelar;
  ruim.ossos.medio.proximal = 0;
  delete ruim.juntas.fonte;
  delete ruim.juntas.dobras.anelarMinimo;
  delete ruim.deducoes.arco;
  delete ruim.antebraco.circunferenciaFlexionado;
  ruim.deducoes.pulso.raio = -1;
  delete ruim.deducoes.perfilDoAntebraco.expoente;
  ruim.limites.pip = [0];
  delete ruim.limites.antebraco.supinacao;
  ruim.rotacaoDoPolegar.cmc = [17];
  const p = problemasDaFichaLuvas(ruim);
  assert.ok(p.some((m) => m.includes('fontes.greiner')), p.join(' | '));
  assert.ok(p.some((m) => m.includes('ossos.anelar')), p.join(' | '));
  assert.ok(p.some((m) => m.includes('ossos.medio.proximal')), p.join(' | '));
  assert.ok(p.some((m) => m.includes('juntas.fonte')), p.join(' | '));
  assert.ok(p.some((m) => m.includes('limites.pip')), p.join(' | '));
  assert.ok(p.some((m) => m.includes('limites.antebraco.supinacao')), p.join(' | '));
  assert.ok(p.some((m) => m.includes('rotacaoDoPolegar.cmc')), p.join(' | '));
  assert.ok(p.some((m) => m.includes('juntas.dobras.anelarMinimo')), p.join(' | '));
  assert.ok(p.some((m) => m.includes('deducoes.arco')), p.join(' | '));
  assert.ok(p.some((m) => m.includes('antebraco.circunferenciaFlexionado')), p.join(' | '));
  assert.ok(p.some((m) => m.includes('deducoes.pulso.raio')), p.join(' | '));
  assert.ok(p.some((m) => m.includes('deducoes.perfilDoAntebraco.expoente')), p.join(' | '));
  assert.throws(() => validarFichaLuvas(ruim), /ficha das luvas/);
});
```

```js file=tests/luvasDados.test.js
// Registro das luvas (Fase 4.1b; desenho em docs/superpowers/specs/2026-09-26-4.1b-luvas-e-empunhadura-design.md,
// seção 7.1; plano, D2 e D6): a pasta, as zonas, os 20 ossos por braço, o orçamento e a pintura de cada facção.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { ARMAS_REAIS } from '../src/data/armasReais.js';
import { FACCOES_DAS_LUVAS, LUVAS, OSSOS_DO_BRACO, ZONAS_DAS_LUVAS, ossosDoLado } from '../src/data/luvas.js';

const rgb = (hex) => [1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16) / 255);
/** A luminância relativa (sRGB linear, pesos da Rec. 709). */
const luminancia = (hex) => rgb(hex).map((v) => (v <= 0.04045 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4))
  .reduce((s, v, i) => s + v * [0.2126, 0.7152, 0.0722][i], 0);
/** O matiz (graus) do HSV. */
function matiz(hex) {
  const [r, g, b] = rgb(hex);
  const max = Math.max(r, g, b);
  const d = max - Math.min(r, g, b);
  if (d === 0) return 0;
  const h = max === r ? ((g - b) / d) % 6 : max === g ? (b - r) / d + 2 : (r - g) / d + 4;
  return (h * 60 + 360) % 360;
}

test('luvas: a pasta, as três zonas e o orçamento da D6', () => {
  assert.equal(LUVAS.pasta, 'assets/maos/');
  assert.deepEqual(ZONAS_DAS_LUVAS, ['couro', 'tecido', 'reforco']);
  assert.deepEqual(LUVAS.orcamento, { triangulos: 14000, textura: 2048, arquivosMB: 6 });
  assert.ok(Object.isFrozen(LUVAS) && Object.isFrozen(LUVAS.pinturas.massaCrua.zonas.couro));
});

test('luvas: os 20 ossos por braço com os nomes da D2 e o sufixo do lado', () => {
  assert.equal(OSSOS_DO_BRACO.length, 20);
  assert.deepEqual(OSSOS_DO_BRACO.slice(0, 3), ['antebraco', 'torcao', 'mao']);
  for (const d of ['polegar', 'indicador', 'medio']) {
    assert.deepEqual(OSSOS_DO_BRACO.filter((o) => o.startsWith(`${d}_`)), [1, 2, 3].map((i) => `${d}_${i}`));
  }
  for (const d of ['anelar', 'minimo']) {
    assert.deepEqual(OSSOS_DO_BRACO.filter((o) => o.startsWith(`${d}_`)), [0, 1, 2, 3].map((i) => `${d}_${i}`));
  }
  assert.equal(ossosDoLado('d')[2], 'mao_d');
  assert.equal(ossosDoLado('e').at(-1), 'minimo_3_e');
  assert.throws(() => ossosDoLado('x'), /lado/);
});

test('luvas: o coiote da Massa Crua separa da madeira de fábrica da AK (na P2 sumia contra ela na luz quente)', () => {
  // Medido na pista: o coiote de partida (#8B6B4A) saía na tela rgb(180, 117, 75), o mesmo laranja da madeira da AK
  // (188, 129, 97) com só 1,2× de diferença de luminância. O coiote fica mais escuro e puxado para o oliva.
  const madeira = ARMAS_REAIS.ak47.fabrica.zonas.guarnicao.cor;
  for (const zona of ZONAS_DAS_LUVAS) {
    const c = LUVAS.pinturas.massaCrua.zonas[zona].cor;
    assert.ok(luminancia(c) <= 0.6 * luminancia(madeira), `${zona}: ${c} claro demais perto da madeira ${madeira}`);
    assert.ok(Math.abs(matiz(c) - matiz(madeira)) >= 12, `${zona}: ${c} no matiz da madeira ${madeira}`);
  }
});

test('luvas: a pintura de cada facção, zona a zona, com as cores do desenho', () => {
  assert.deepEqual(FACCOES_DAS_LUVAS, ['massaCrua', 'tropa']);
  const cores = (f) => ZONAS_DAS_LUVAS.map((z) => LUVAS.pinturas[f].zonas[z].cor);
  assert.deepEqual(cores('massaCrua'), ['#5C5139', '#4D4432', '#342E24']);
  assert.deepEqual(cores('tropa'), ['#1D1D1F', '#232326', '#2C2D30']);
  for (const f of FACCOES_DAS_LUVAS) {
    const z = LUVAS.pinturas[f].zonas;
    assert.deepEqual([z.couro.acabamento, z.tecido.acabamento, z.reforco.acabamento], ['couro', 'tecido', 'borracha']);
    for (const zona of ZONAS_DAS_LUVAS) assert.ok(z[zona].desgaste >= 0 && z[zona].desgaste <= 1, `${f}.${zona}`);
    assert.ok(LUVAS.pinturas[f].nome.length > 3);
  }
});
```

Run: `node --test tests/fichaLuvas.test.js tests/luvasDados.test.js`
Expected: FAIL — # tests 2 # pass 0 # fail 2 .

- [ ] **A implementação** — `tools/blender/refs/luvas.json`, `src/characters/hands/fichaLuvas.js`, `src/data/luvas.js`:

```json file=tools/blender/refs/luvas.json
{
  "formato": 1,
  "id": "luvas",
  "descricao": "Luva tática de 5 dedos na mão de um adulto médio (Fase 4.1b). Unidades: mm e graus. Referencial da mão direita: origem no centro da junta do pulso, +X para as pontas dos dedos, +Y para o lado do polegar, +Z para as costas da mão (a esquerda é a direita espelhada).",
  "fontes": {
    "ansur2": {
      "titulo": "ANSUR II (levantamento antropométrico do Exército dos EUA, 2012) — medidas da mão, média de homens e mulheres, N = 6 068 (tabela do benchmark Sota2)",
      "url": "https://www.sota2.com/research/sota/hand-anthropometry-on-ansur-ii-combined-male-and-female"
    },
    "buryanov": {
      "titulo": "Buryanov A., Kotiuk V. (2010). Proportions of Hand Segments. Int. J. Morphol. 28(3):755–758 — tabela I: comprimentos entre as juntas em radiografias de 66 adultos",
      "url": "https://scielo.conicyt.cl/scielo.php?script=sci_arttext&pid=S0717-95022010000300015&lng=en&nrm=iso&tlng=en"
    },
    "greiner": {
      "titulo": "Greiner T. M. (1991). Hand Anthropometry of U.S. Army Personnel. Natick TR-92/011 (DTIC ADA244533) — médias dos 1 003 homens",
      "url": "https://archive.org/details/DTIC_ADA244533"
    },
    "ansur2Explorador": {
      "titulo": "ANSUR II (2012) no Data Explorer do OPEN Design Lab (Penn State) — medianas dos dois sexos da circunferência do antebraço flexionado e da do pulso, lidas no navegador em 2026-09-26",
      "url": "https://tools.openlab.psu.edu/tools/data-explorer"
    },
    "aaos": {
      "titulo": "American Academy of Orthopaedic Surgeons — amplitude normal de movimento das juntas da mão, do pulso e do antebraço (pronação e supinação), conferida no navegador em 2026-09-27",
      "url": "https://goniometer.io/rom-chart.pdf"
    },
    "cooney": {
      "titulo": "Cooney W. P., Lucca M. J., Chao E. Y., Linscheid R. L. (1981). The kinesiology of the thumb trapeziometacarpal joint. J Bone Joint Surg 63:1371–81 — a CMC do polegar com 53° de flexão-extensão, 42° de abdução-adução e 17° de rotação axial (citado e conferido em Halilaj et al., 2013, PMC3594374)",
      "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC3594374/"
    },
    "referencias": {
      "titulo": "Referências visuais da luva tática: busca do Pinterest de 2026-09-26 e os boards QGL, QFH e QTG (moodboard, seção 15)",
      "url": "https://www.pinterest.com/search/pins/?q=tactical%20gloves%20knuckle%20protection%20close%20up"
    }
  },
  "mao": {
    "fonte": "ansur2",
    "comprimento": { "mm": 189.3, "nota": "da prega do pulso à ponta do médio" },
    "largura": { "mm": 85, "nota": "nos nós, do indicador ao mínimo" },
    "palma": { "mm": 113.9, "nota": "da prega do pulso à prega da base do médio" },
    "circunferencia": { "mm": 203.9, "nota": "em volta dos nós, sem o polegar" },
    "pulso": { "mm": 169, "nota": "circunferência do pulso" }
  },
  "ossos": {
    "fonte": "buryanov",
    "polegar": { "metacarpo": 46.22, "proximal": 31.57, "distal": 21.67, "polpa": 5.67 },
    "indicador": { "metacarpo": 68.12, "proximal": 39.78, "media": 22.38, "distal": 15.82, "polpa": 3.84 },
    "medio": { "metacarpo": 64.6, "proximal": 44.63, "media": 26.33, "distal": 17.4, "polpa": 3.95 },
    "anelar": { "metacarpo": 58, "proximal": 41.37, "media": 25.65, "distal": 17.3, "polpa": 3.95 },
    "minimo": { "metacarpo": 53.69, "proximal": 32.74, "media": 18.11, "distal": 15.96, "polpa": 3.73 }
  },
  "juntas": {
    "fonte": "greiner",
    "nota": "Médias dos homens como publicadas; o script multiplica os comprimentos por mao.comprimento / pontaAoPulso.medio e as larguras e circunferências por mao.largura / larguraDaMao (a mão da ficha).",
    "larguraDaMao": 90.4,
    "pontaAoPulso": { "polegar": 137.9, "indicador": 185.2, "medio": 194.5, "anelar": 185, "minimo": 159.9 },
    "dobras": { "polegarIndicador": 69.1, "indicadorMedio": 110.4, "medioAnelar": 109.9, "anelarMinimo": 96.6, "nota": "altura da dobra entre dois dedos acima da prega do pulso (crotch height)" },
    "cotoveloAoPulso": 290,
    "pulso": { "largura": 65.8, "circunferencia": 174.3 },
    "polegar": { "ip": { "largura": 24, "circunferencia": 72.3 } },
    "indicador": { "pip": { "largura": 23, "circunferencia": 68.4 }, "dip": { "circunferencia": 57.4 } },
    "medio": { "pip": { "largura": 22.5, "circunferencia": 69.6 }, "dip": { "largura": 19.8, "circunferencia": 57.8 } },
    "anelar": { "pip": { "largura": 21.4, "circunferencia": 64.9 }, "dip": { "largura": 18.5, "circunferencia": 53.8 } },
    "minimo": { "pip": { "largura": 19.2, "circunferencia": 57.8 }, "dip": { "largura": 17.4, "circunferencia": 49.2 } }
  },
  "antebraco": {
    "fonte": "ansur2Explorador",
    "circunferenciaFlexionado": { "mm": 285, "nota": "mediana dos dois sexos: cotovelo a 90°, punho cerrado, a fita na prega do cotovelo" },
    "pulso": { "mm": 165, "nota": "mediana dos dois sexos da circunferência do pulso no estilóide, a mesma base" }
  },
  "limites": {
    "fonte": "aaos",
    "mcp": [0, 90],
    "pip": [0, 100],
    "dip": [0, 90],
    "abertura": [-20, 20],
    "polegar": { "cmcAbducao": [0, 70], "cmcFlexao": [-20, 15], "mcp": [0, 50], "ip": [0, 80] },
    "pulso": { "flexao": 80, "extensao": 70, "radial": 20, "ulnar": 30 },
    "antebraco": { "pronacao": 80, "supinacao": 80 }
  },
  "rotacaoDoPolegar": {
    "fonte": "cooney",
    "cmc": [0, 17],
    "nota": "A rotação axial do metacarpo do polegar na CMC (17° de amplitude), contada do repouso para a pronação que acompanha a flexão e a oposição (a polpa virando para os dedos; a rotação vem passiva, pela tensão dos ligamentos oblíquos). Sem ela o polegar do punho deita sobre os dedos com a polpa de lado."
  },
  "repouso": {
    "nota": "Mão relaxada, que dobra bem tanto para abrir quanto para fechar (desenho da 4.1b, seção 3.1).",
    "mcp": 15,
    "pip": 20,
    "dip": 10,
    "abertura": 5,
    "polegarAbducao": 40,
    "polegarMcp": 10,
    "polegarIp": 15
  },
  "luva": {
    "nota": "Decisões de desenho conferidas nas referências (moodboard, seção 15): tecido elástico nas costas e nos lados, couro sintético na palma e nas pontas, almofadas nas falanges, protetor de borracha moldada nos nós, tira de velcro no punho com o puxador.",
    "tecido": 1.2,
    "couro": 1,
    "almofada": 3,
    "protetor": 7,
    "tira": 38,
    "punho": 45,
    "folgaPunho": 2
  },
  "deducoes": {
    "polegar": {
      "cmc": [20, 22, -10],
      "anguloNaPalma": 25,
      "pronacao": 80,
      "porque": "A base do polegar (CMC, no trapézio) fica ~20 mm à frente do pulso, ~22 mm para o lado do polegar e abaixo do plano da palma. Com o polegar deitado no plano da mão a 25° do eixo, a ponta cai a 134 mm do pulso — a medida de Greiner (137,9 × 189,3/194,5 = 134,2). A rotação de 80° em volta dele põe a unha de lado, virada para fora da mão, e a polpa de frente para o indicador, como na mão relaxada (e a flexão do polegar leva a ponta para a palma e o mínimo)."
    },
    "espessuraDaMao": {
      "mm": 29,
      "raio": 12,
      "porque": "A circunferência nos nós (203,9) com a largura (85) numa seção de retângulo arredondado de raio 12 mm dá 28–29 mm de espessura; uma elipse daria 41 mm, grossa demais para a mão nos nós."
    },
    "pulso": {
      "espessura": 38,
      "raio": 18,
      "porque": "A largura do pulso de Greiner na escala da ficha (65,8 × 85/90,4 = 61,9) e a circunferência do ANSUR II (169) numa seção de retângulo arredondado de raio 18 mm (o mesmo modelo da espessura da mão) dão 38 mm de espessura; uma elipse daria 45, grossa demais."
    },
    "folgaEntreDedos": {
      "mm": 1,
      "porque": "Os quatro nós repartem a largura da mão (85) na proporção das larguras nas PIP, com 1 mm entre um dedo e o outro na linha dos nós."
    },
    "leque": {
      "fator": 0.42,
      "porque": "Os metacarpos saem juntos do carpo e abrem em leque até os nós: a base de cada um fica a 0,42 da distância lateral do nó dele ao eixo da mão (as bases do indicador ao mínimo somam ~27 mm entre os centros, contra os 65 dos nós), da anatomia do carpo."
    },
    "arco": {
      "mm": { "indicador": -2, "medio": 0, "anelar": -1.5, "minimo": -4 },
      "porque": "O arco transverso da palma: os nós do indicador, do anelar e sobretudo do mínimo ficam um pouco abaixo (para o lado da palma) do nó do médio, que é o mais alto; da anatomia, conferido nas vistas de frente para as pontas."
    },
    "convergencia": {
      "graus": { "indicador": -4, "medio": 0, "anelar": 4, "minimo": 9 },
      "porque": "Os dedos fecham apontando para a base do polegar (a 'cascata' dos dedos): os eixos de flexão da PIP e da DIP de cada um inclinam um pouco para o médio; a MCP dobra reta (com as falanges esticadas e a MCP a 90°, a 'mesa', os dedos ficam lado a lado: inclinada, a da MCP levava o mínimo 13 mm por cima do anelar). Da anatomia, conferido nas vistas do punho fechado e da mesa."
    },
    "antebraco": {
      "divisao": 0.5,
      "porque": "O antebraço tem o comprimento do cotovelo ao pulso de Greiner (290 × 189,3/194,5 = 282 mm); o osso `antebraco` vai do cotovelo à metade e a `torcao` da metade ao pulso, para a torção do punho se repartir ao longo do antebraço sem torcer a malha num ponto só."
    },
    "perfilDoAntebraco": {
      "circunferenciaNoCotovelo": 291.9,
      "expoente": 1.3,
      "porque": "A razão entre o antebraço flexionado e o pulso nas medianas do ANSUR II (285/165 = 1,727) aplicada ao pulso da ficha (169) dá 291,9 mm na prega do cotovelo. Entre os dois a circunferência cresce como t^1,3 (t = distância do pulso sobre os 282 mm do antebraço): quase reta no terço do pulso, onde só passam tendões, e abrindo no do cotovelo, onde ficam os ventres dos músculos — na boca do punho da luva (45 mm) dá 180,3 mm, 6,7 % acima do pulso. A seção é o retângulo arredondado do pulso na escala da circunferência."
    }
  }
}
```

```js file=src/characters/hands/fichaLuvas.js
// Ficha das luvas (Fase 4.1b; desenho em docs/superpowers/specs/2026-09-26-4.1b-luvas-e-empunhadura-design.md, seção 2):
// tools/blender/refs/luvas.json — a mão média (ANSUR II), os ossos entre as juntas (Buryanov & Kotiuk 2010), as larguras
// e circunferências nas juntas e as pontas dos dedos ao pulso (Greiner 1991, médias dos homens, levadas à mão da ficha
// pelas escalas), o antebraço (medianas do ANSUR II), os limites das juntas (AAOS), a pose de repouso, a luva e as
// deduções, cada uma com o porquê. O Node confere antes de o Blender construir; o lançador passa a ficha validada ao
// principal.py, que não inventa medida. O antebraço de massinha do jogo (antebracoMassa.js) lê o mesmo perfil.

const F = Object.freeze;

export const DEDOS = F(['polegar', 'indicador', 'medio', 'anelar', 'minimo']);
export const OSSOS_DO_DEDO = F({
  polegar: F(['metacarpo', 'proximal', 'distal', 'polpa']),
  indicador: F(['metacarpo', 'proximal', 'media', 'distal', 'polpa']),
  medio: F(['metacarpo', 'proximal', 'media', 'distal', 'polpa']),
  anelar: F(['metacarpo', 'proximal', 'media', 'distal', 'polpa']),
  minimo: F(['metacarpo', 'proximal', 'media', 'distal', 'polpa']),
});
const FONTES = F(['ansur2', 'ansur2Explorador', 'buryanov', 'greiner', 'aaos', 'cooney', 'referencias']);
const MEDIDAS_DA_MAO = F(['comprimento', 'largura', 'palma', 'circunferencia', 'pulso']);
const MEDIDAS_DA_LUVA = F(['tecido', 'couro', 'almofada', 'protetor', 'tira', 'punho', 'folgaPunho']);
const REPOUSO = F(['mcp', 'pip', 'dip', 'abertura', 'polegarAbducao', 'polegarMcp', 'polegarIp']);
const DOBRAS = F(['polegarIndicador', 'indicadorMedio', 'medioAnelar', 'anelarMinimo']);

const positivo = (v) => Number.isFinite(v) && v > 0;
const faixa = (v) => Array.isArray(v) && v.length === 2 && v.every(Number.isFinite) && v[0] < v[1];

/**
 * Confere a ficha das luvas (formato 1).
 * @param {object} f
 * @returns {string[]} os problemas (vazio = válida), cada um começando pelo campo
 */
export function problemasDaFichaLuvas(f) {
  const p = [];
  const exigir = (cond, msg) => {
    if (!cond) p.push(msg);
  };
  exigir(f?.formato === 1, 'formato: precisa ser 1');
  exigir(f?.id === 'luvas', 'id: precisa ser "luvas"');
  for (const nome of FONTES) {
    const fo = f?.fontes?.[nome];
    exigir(typeof fo?.titulo === 'string' && fo.titulo.length > 10 && /^https:\/\//.test(fo?.url ?? ''),
      `fontes.${nome}: título e endereço https`);
  }
  const fonteValida = (grupo) => exigir(FONTES.includes(f?.[grupo]?.fonte) && Boolean(f?.fontes?.[f[grupo].fonte]),
    `${grupo}.fonte: uma das fontes da ficha`);
  fonteValida('mao');
  for (const m of MEDIDAS_DA_MAO) exigir(positivo(f?.mao?.[m]?.mm), `mao.${m}.mm: número positivo`);
  fonteValida('ossos');
  for (const d of DEDOS) {
    if (!f?.ossos?.[d]) {
      p.push(`ossos.${d}: falta o dedo`);
      continue;
    }
    for (const o of OSSOS_DO_DEDO[d]) exigir(positivo(f.ossos[d][o]), `ossos.${d}.${o}: número positivo`);
  }
  fonteValida('juntas');
  const j = f?.juntas;
  exigir(positivo(j?.larguraDaMao), 'juntas.larguraDaMao: número positivo');
  for (const d of DEDOS) exigir(positivo(j?.pontaAoPulso?.[d]), `juntas.pontaAoPulso.${d}: número positivo`);
  for (const k of DOBRAS) exigir(positivo(j?.dobras?.[k]), `juntas.dobras.${k}: número positivo`);
  exigir(positivo(j?.cotoveloAoPulso), 'juntas.cotoveloAoPulso: número positivo');
  exigir(positivo(j?.pulso?.largura) && positivo(j?.pulso?.circunferencia), 'juntas.pulso: largura e circunferência');
  exigir(positivo(j?.polegar?.ip?.largura) && positivo(j?.polegar?.ip?.circunferencia), 'juntas.polegar.ip: largura e circunferência');
  for (const d of DEDOS.slice(1)) {
    exigir(positivo(j?.[d]?.pip?.largura) && positivo(j?.[d]?.pip?.circunferencia), `juntas.${d}.pip: largura e circunferência`);
    exigir(positivo(j?.[d]?.dip?.circunferencia), `juntas.${d}.dip.circunferencia: número positivo`);
    exigir(j?.[d]?.dip?.largura === undefined || positivo(j[d].dip.largura), `juntas.${d}.dip.largura: número positivo quando houver`);
  }
  fonteValida('antebraco');
  exigir(positivo(f?.antebraco?.circunferenciaFlexionado?.mm), 'antebraco.circunferenciaFlexionado.mm: número positivo');
  exigir(positivo(f?.antebraco?.pulso?.mm), 'antebraco.pulso.mm: número positivo');
  fonteValida('limites');
  const l = f?.limites;
  for (const k of ['mcp', 'pip', 'dip', 'abertura']) exigir(faixa(l?.[k]), `limites.${k}: [mínimo, máximo]`);
  for (const k of ['cmcAbducao', 'cmcFlexao', 'mcp', 'ip']) exigir(faixa(l?.polegar?.[k]), `limites.polegar.${k}: [mínimo, máximo]`);
  for (const k of ['flexao', 'extensao', 'radial', 'ulnar']) exigir(positivo(l?.pulso?.[k]), `limites.pulso.${k}: graus positivos`);
  for (const k of ['pronacao', 'supinacao']) exigir(positivo(l?.antebraco?.[k]), `limites.antebraco.${k}: graus positivos`);
  fonteValida('rotacaoDoPolegar');
  exigir(faixa(f?.rotacaoDoPolegar?.cmc), 'rotacaoDoPolegar.cmc: [mínimo, máximo]');
  exigir(typeof f?.rotacaoDoPolegar?.nota === 'string' && f.rotacaoDoPolegar.nota.length > 20,
    'rotacaoDoPolegar.nota: de onde veio e para que serve');
  for (const k of REPOUSO) exigir(Number.isFinite(f?.repouso?.[k]), `repouso.${k}: número`);
  for (const k of MEDIDAS_DA_LUVA) exigir(positivo(f?.luva?.[k]), `luva.${k}: número positivo`);
  exigir(typeof f?.luva?.nota === 'string' && f.luva.nota.length > 20, 'luva.nota: de onde vieram as decisões');
  for (const [nome, d] of Object.entries(f?.deducoes ?? {})) {
    exigir(typeof d?.porque === 'string' && d.porque.length > 20, `deducoes.${nome}.porque: como o número foi deduzido`);
  }
  for (const nome of ['polegar', 'espessuraDaMao', 'pulso', 'folgaEntreDedos', 'leque', 'arco', 'convergencia', 'antebraco',
    'perfilDoAntebraco']) {
    exigir(Boolean(f?.deducoes?.[nome]), `deducoes.${nome}: falta`);
  }
  const d = f?.deducoes;
  exigir(positivo(d?.pulso?.espessura) && positivo(d?.pulso?.raio), 'deducoes.pulso.raio: espessura e raio positivos');
  exigir(positivo(d?.espessuraDaMao?.mm) && positivo(d?.espessuraDaMao?.raio), 'deducoes.espessuraDaMao.raio: espessura e raio positivos');
  exigir(positivo(d?.perfilDoAntebraco?.circunferenciaNoCotovelo),
    'deducoes.perfilDoAntebraco.circunferenciaNoCotovelo: número positivo');
  const expoente = d?.perfilDoAntebraco?.expoente;
  exigir(Number.isFinite(expoente) && expoente >= 1 && expoente <= 3, 'deducoes.perfilDoAntebraco.expoente: entre 1 e 3');
  return p;
}

function congelar(o) {
  if (o && typeof o === 'object') {
    for (const v of Object.values(o)) congelar(v);
    Object.freeze(o);
  }
  return o;
}

/** A ficha conferida e congelada (uma cópia); lança com todos os problemas. */
export function validarFichaLuvas(f) {
  const p = problemasDaFichaLuvas(f);
  if (p.length) throw new Error(`ficha das luvas: ${p.join('; ')}`);
  return congelar(structuredClone(f));
}

/** Perímetro do retângulo arredondado (o modelo de seção da ficha para o pulso, a mão nos nós e o antebraço). */
export function perimetroRetanguloArredondado(largura, altura, raio) {
  return 2 * (largura - 2 * raio) + 2 * (altura - 2 * raio) + 2 * Math.PI * raio;
}

/**
 * Escalas das médias dos homens de Greiner para a mão da ficha: os comprimentos pela ponta do médio ao pulso (o mesmo
 * referencial do comprimento da mão), as larguras e circunferências pela largura da mão.
 */
export function escalasDaFicha(f) {
  return {
    comprimento: f.mao.comprimento.mm / f.juntas.pontaAoPulso.medio,
    largura: f.mao.largura.mm / f.juntas.larguraDaMao,
  };
}
```

```js file=src/data/luvas.js
// Registro das luvas táticas (Fase 4.1b; desenho em docs/superpowers/specs/2026-09-26-4.1b-luvas-e-empunhadura-design.md,
// seção 7.1; plano da 4.1b, D2 e D6): o que o Blender constrói (tools/blender/armas/luvas.py, pela ficha
// tools/blender/refs/luvas.json), o que o validador da saída confere e o que o jogo carrega.
//  - Zonas: os grupos de material das duas malhas (`couro` na palma, nas pontas e entre o polegar e o indicador;
//    `tecido` nas costas e nos lados; `reforco` no protetor dos nós, nas almofadas e na tira do punho).
//  - Ossos: 20 por braço, com o sufixo do lado (`_d`, `_e`); os dedos em três falanges, o anelar e o mínimo com o
//    metacarpo próprio (a borda da palma fecha em concha).
//  - Orçamento: os dois braços juntos (D6).
//  - Pinturas: acabamento, cor e desgaste por zona, no formato das skins das armas; Massa Crua em coiote e Tropa do
//    Estúdio em preto (seção 7.1). O coiote de partida (#8B6B4A) saía na pista, sob a luz quente, no mesmo laranja da
//    madeira de fábrica da AK e da mesa (P2, 2026-09-27: rgb 180/117/75 contra 188/129/97, 1,2× de luminância): ficou
//    mais escuro e puxado para o oliva (o matiz ~40°, longe dos ~23° da madeira), e o couro gasta menos (o gasto do
//    couro clareia).

const F = Object.freeze;

export const ZONAS_DAS_LUVAS = F(['couro', 'tecido', 'reforco']);
export const OSSOS_DO_BRACO = F([
  'antebraco', 'torcao', 'mao',
  'polegar_1', 'polegar_2', 'polegar_3',
  'indicador_1', 'indicador_2', 'indicador_3',
  'medio_1', 'medio_2', 'medio_3',
  'anelar_0', 'anelar_1', 'anelar_2', 'anelar_3',
  'minimo_0', 'minimo_1', 'minimo_2', 'minimo_3',
]);
export const FACCOES_DAS_LUVAS = F(['massaCrua', 'tropa']);
// A pega das armas (seção 6.4 do desenho; plano, D1): os 17 ossos de dedo de cada mão que o clipe `empunhadura` do
// .glb da arma gira, e os limites da validação da seção 6.3 (o relatório do Blender e o `luvas_contato` do jogo).
export const OSSOS_DE_DEDO = F([
  'polegar_1', 'polegar_2', 'polegar_3',
  'indicador_1', 'indicador_2', 'indicador_3',
  'medio_1', 'medio_2', 'medio_3',
  'anelar_0', 'anelar_1', 'anelar_2', 'anelar_3',
  'minimo_0', 'minimo_1', 'minimo_2', 'minimo_3',
]);
// `ladoMM` (regra do usuário de 2026-09-27, para toda arma com mão da frente): na mão da frente só o polegar fica de um
// lado da arma e os quatro dedos do outro, como a pega da AK no CS:GO — a polpa de cada um a pelo menos esta distância
// do plano do meio da arma, do lado certo (a mão do gatilho, quando a regra dela diz os lados, passa pela mesma conta).
// `polegarCurvaGraus` e `polegarFolgaMM` (o usuário, 2026-09-27: "o dedo tem que estar colado com a arma", sem curva):
// o polegar da mão da frente reto e deitado na face do lado dele — a MCP mais a IP até 20° (a versão recusada fazia um
// arco de 52°), a falange distal encostando (o trecho dela mais perto até `contatoMM`) e nenhum trecho a mais de 8 mm (a
// cunha da base, que sai da quina de baixo do guarda-mão).
// `dedosJuntosMM` (a revisão crítica da 4.1b, 2026-09-27): os dedos que abraçam a arma lado a lado, sem leque — a falange
// média de cada um a no máximo esta distância da do vizinho, menos da metade da largura dela (17 a 19 mm na ficha).
// Fechando cada dedo sozinho, os da mão da frente da AK saíam em leque (até 8,53 mm, a ponta a 17 mm); a ponta não
// conta, porque o dedo que dobra mais sai da ponta do vizinho.
export const LIMITES_DA_PEGA = F({
  penetracaoMM: 0.3, contatoMM: 1, contatoJogoMM: 0.05, ladoMM: 5, polegarCurvaGraus: 20, polegarFolgaMM: 8,
  dedosJuntosMM: 8,
});
export const DEDOS_DA_FRENTE = F(['indicador', 'medio', 'anelar', 'minimo']);
// As categorias do viewmodel com regra de pega no Blender (tools/blender/armas/empunhadura_regras.py): a arma realista
// delas sai com a pega no .glb; as outras entram com as armas delas (4.1c, 4.1d).
export const CATEGORIAS_COM_PEGA = F(['rifle']);

/** Os 20 nomes de osso de um braço (`d` ou `e`). */
export function ossosDoLado(lado) {
  if (lado !== 'd' && lado !== 'e') throw new Error(`lado das luvas: 'd' ou 'e' (veio ${lado})`);
  return OSSOS_DO_BRACO.map((o) => `${o}_${lado}`);
}

export const LUVAS = F({
  pasta: 'assets/maos/',
  orcamento: F({ triangulos: 14000, textura: 2048, arquivosMB: 6 }),
  pinturas: F({
    massaCrua: F({
      nome: 'Massa Crua (coiote)',
      zonas: F({
        couro: F({ acabamento: 'couro', cor: '#5C5139', desgaste: 0.15 }),
        tecido: F({ acabamento: 'tecido', cor: '#4D4432', desgaste: 0.12 }),
        reforco: F({ acabamento: 'borracha', cor: '#342E24', desgaste: 0.15 }),
      }),
    }),
    tropa: F({
      nome: 'Tropa do Estúdio (preta)',
      zonas: F({
        couro: F({ acabamento: 'couro', cor: '#1D1D1F', desgaste: 0.25 }),
        tecido: F({ acabamento: 'tecido', cor: '#232326', desgaste: 0.15 }),
        reforco: F({ acabamento: 'borracha', cor: '#2C2D30', desgaste: 0.2 }),
      }),
    }),
  }),
});

// O antebraço de massinha que entra no punho da luva e a braçadeira do time (seção 5 do desenho; plano, Tarefa 9). A
// seção vem da ficha (o retângulo arredondado do pulso crescendo até a circunferência do cotovelo, `perfilDoAntebraco`
// — o mesmo modelo que o Blender usou para vestir o punho da luva); aqui fica só o que é do jogo, em mm (a árvore SDF sai
// em u):
//  - o tronco vai de `dentroDoPunhoMM` antes do pulso (dentro do punho, que tem 45 mm: a ponta não fura a luva quando o
//    pulso dobra, e a boca do punho nunca mostra o fim da massa) até `alemDoCotoveloMM` depois do cotovelo, fora da
//    tela; `secoes` amostram a curva t^1,3;
//  - a irregularidade de massa moldada à mão (o `displace` do SDF, como a mão de massinha da 4.1) fica abaixo da folga
//    do forro do punho (1,6 mm na borda de dentro; medida com a luva de verdade, a menor folga sai 1,2 mm);
//  - a célula da malha: o antebraço tem curvatura baixa (cantos de 18 a 31 mm), e com 4 mm a silhueta erra ~0,1 mm
//    (h²/8r) — 12 mil triângulos, contra 35 mil do braço de massinha da 4.1; a braçadeira, com a borda arredondada de
//    2,5 mm, pede 2,3 mm;
//  - a torção passa do osso `antebraco` ao `torcao` em rampa linear do cotovelo à boca do punho (100 % `torcao`, como o
//    punho da luva): meia torção do pulso repartida ao longo do antebraço;
//  - a massa: a do boneco, com as digitais, a translucidez e o brilho de massinha, sem boil (seção 0.7);
//  - a braçadeira: uma faixa de massa em volta do antebraço, a `doPulsoMM` do pulso (depois da boca do punho, onde a
//    câmera do viewmodel pega), só com time.
export const BRACO_DE_MASSA = F({
  dentroDoPunhoMM: 20,
  alemDoCotoveloMM: 60,
  secoes: 24,
  irregularidade: F({ ampMM: 0.4, freqPorU: 0.5, oitavas: 2 }),
  malha: F({ celulaU: 0.16, maxCells: 1400000, touchRadius: 0.5 }),
  massa: F({ roughness: 0.7, wetness: 0.36, objectSize: 5 }),
  bracadeira: F({
    doPulsoMM: 110, larguraMM: 40, espessuraMM: 5, arredondaMM: 2.5, dentroMM: 1.5,
    irregularidade: F({ ampMM: 0.25, freqPorU: 0.9, oitavas: 2 }),
    massa: F({ roughness: 0.66, wetness: 0.4, objectSize: 3 }),
    malha: F({ celulaU: 0.09, maxCells: 800000, touchRadius: 0.3 }),
  }),
});
```

Run: `node --test tests/fichaLuvas.test.js tests/luvasDados.test.js`
Expected: PASS — # tests 11 # pass 11 # fail 0 .

Run: `node --test "tests/**/*.test.js"`
Expected: PASS — # tests 381 # pass 381 # fail 0 .

### Tarefa 3: Esqueleto e malha base (`maos.py`)

**Files:** Create `tools/blender/armas/maos.py`; Modify `principal.py` (alvo `luvas`, só a malha base por enquanto),
`tools/blender.mjs` (alvo `luvas` no `construir`/`conferir`/`abrir`).

- [ ] **Passo 1: Juntas e ossos** — `juntas(ficha)` → dicionário `{osso: (cabeça, cauda, rolagem)}` na pose de
  repouso, em mm, da mão direita (D3): as CMC pelo `carpo`, as MCP pelos metacarpos, as falanges pelos comprimentos, as
  rotações de repouso da ficha; o polegar sai da CMC com a abdução de repouso.
- [ ] **Passo 2: O gerador** — `malha_base(ficha, juntas)` → `bmesh` de quadriláteros: palma em grade (costas, palma,
  lados) com as cinco portas de 8 vértices; dedos em anéis elípticos (largura × espessura da ficha + a luva), três anéis
  por junta; pontas em calota; punho até 45 mm atrás do pulso. Cada vértice guarda o osso e o parâmetro ao longo dele
  (camadas `osso` e `t` do `bmesh`); as costuras (lados dos dedos, borda palma/costas, punho) ficam marcadas.
- [ ] **Passo 3: Medidas na malha** — `medir_mao(obj)`: comprimento (pulso à ponta do médio, no eixo X), largura na
  linha das MCP, circunferência do pulso na boca do punho. Alvos: 189,3 / 85 / a do punho (± 1 %).
- [ ] **Passo 4: `construir luvas`** (primeira versão: só a malha base, subdividida 1 nível, sem assar) e as vistas da
  `conferir` (costas, palma, lado do polegar, lado do mínimo, de frente para as pontas, três quartos), com a malha em
  arame por cima numa delas.
- [ ] **Passo 5: Revisão crítica** — comparar com as fotos de mão e de luva (QGL3, QGL5, QTG e a busca da seção 15):
  proporção dos dedos, arco das MCP, largura do punho, espessura da palma, abertura do polegar; registrar achado →
  correção.


**Código da tarefa** (a versão verificada no navegador e no Blender; os blocos `file=` são o arquivo inteiro, os pares são aplicados na ordem).

- [ ] **A implementação** — `tools/blender/armas/maos.py`, `tools/blender/armas/maos_medidas.py`, `tools/blender/armas/maos_limite.py`, `tools/blender/armas/maos_gaiola.py`, `tools/blender/armas/maos_capsulas.py`:

```python file=tools/blender/armas/maos.py
# Luvas táticas realistas (Fase 4.1b; desenho em docs/superpowers/specs/2026-09-26-4.1b-luvas-e-empunhadura-design.md,
# seções 2 e 3): a anatomia da mão direita pela ficha (tools/blender/refs/luvas.json) — as juntas e os ossos na pose de
# repouso, as seções dos dedos nas juntas, o pulso e o perfil do antebraço de massinha que entra no punho da luva. O
# script não inventa medida: cada número sai da ficha (medida publicada ou dedução com o porquê). A gaiola de
# quadriláteros e a malha saem de maos_gaiola.py.
# Referencial (mão direita, mm): origem no centro da junta do pulso, +X para as pontas, +Y para o polegar, +Z para as
# costas da mão. A esquerda é esta espelhada em Y (maos_rig.py).
import math

from mathutils import Quaternion, Vector

DEDOS4 = ('indicador', 'medio', 'anelar', 'minimo')
# Abertura de repouso de cada dedo, em múltiplos de `repouso.abertura` (o médio é o eixo; + para o polegar).
_ABERTURA = {'indicador': 1.0, 'medio': 0.0, 'anelar': -1.0, 'minimo': -2.0}
# Metacarpo que carrega a borda da palma (os outros dois vão na `mao`).
METACARPO = {'anelar': 'anelar_0', 'minimo': 'minimo_0'}


def perimetro_elipse(a, b):
    """Ramanujan: perímetro da elipse de semieixos a e b."""
    return math.pi * (3 * (a + b) - math.sqrt((3 * a + b) * (a + 3 * b)))


def perimetro_retangulo_arredondado(largura, altura, raio):
    """Perímetro do retângulo arredondado (o modelo de seção da ficha para o pulso e para a mão nos nós)."""
    return 2 * (largura - 2 * raio) + 2 * (altura - 2 * raio) + 2 * math.pi * raio


def espessura_pela_circunferencia(largura, circ):
    """A espessura (2b) da elipse com a largura (2a) e o perímetro dados (bisseção)."""
    a = largura / 2
    lo, hi = 0.2 * a, 3.0 * a
    for _ in range(60):
        b = (lo + hi) / 2
        if perimetro_elipse(a, b) < circ:
            lo = b
        else:
            hi = b
    return lo + hi


def meia_altura_no_contorno(y, meia_l, meia_a, raio):
    """Metade da altura do retângulo arredondado (meia largura, meia altura, raio do canto) na posição y."""
    raio = min(raio, meia_l, meia_a)
    reto = meia_l - raio
    if abs(y) <= reto:
        return meia_a
    dy = min(abs(y) - reto, raio)
    return meia_a - raio + math.sqrt(max(0.0, raio * raio - dy * dy))


class Mao:
    """As juntas, os referenciais e as seções da mão direita na pose de repouso, em mm, pela ficha."""

    def __init__(self, ficha):
        self.f = ficha
        j = ficha['juntas']
        self.esc_c = ficha['mao']['comprimento']['mm'] / j['pontaAoPulso']['medio']
        self.esc_l = ficha['mao']['largura']['mm'] / j['larguraDaMao']
        self.luva = ficha['luva']['tecido']
        self.rep = ficha['repouso']
        self.ded = ficha['deducoes']
        self.largura = ficha['mao']['largura']['mm']
        self._larguras_nos()
        self.dedos = {d: self._dedo(d) for d in DEDOS4}
        self.polegar = self._polegar()
        self._pulso()
        self.antebraco = j['cotoveloAoPulso'] * self.esc_c

    # ------------------------------------------------------------------ medidas
    def _larguras_juntas(self, d):
        """(largura, espessura) na PIP e na DIP, na escala da ficha e sem a luva."""
        j = self.f['juntas'][d]
        lp = j['pip']['largura'] * self.esc_l
        ep = espessura_pela_circunferencia(lp, j['pip']['circunferencia'] * self.esc_l)
        if 'largura' in j['dip']:
            ld = j['dip']['largura'] * self.esc_l
        else:
            # A largura da DIP do indicador (ilegível na cópia de Greiner) na proporção largura/circunferência do médio.
            m = self.f['juntas']['medio']['dip']
            ld = j['dip']['circunferencia'] * m['largura'] / m['circunferencia'] * self.esc_l
        ed = espessura_pela_circunferencia(ld, j['dip']['circunferencia'] * self.esc_l)
        return (lp, ep), (ld, ed)

    def _larguras_nos(self):
        """Os quatro nós repartem a largura da mão na proporção das larguras nas PIP, com a folga entre os dedos. As
        fronteiras (do indicador ao mínimo) ficam em `y_fronteira`; as bordas de fora são ± a meia largura da mão."""
        folga = self.ded['folgaEntreDedos']['mm']
        pips = {d: self._larguras_juntas(d)[0][0] for d in DEDOS4}
        k = (self.largura - 3 * folga) / sum(pips.values())
        self.larg_no = {d: pips[d] * k for d in DEDOS4}
        y = self.largura / 2
        self.y_no = {}
        self.y_fronteira = [self.largura / 2]
        for d in DEDOS4:
            self.y_no[d] = y - self.larg_no[d] / 2
            y -= self.larg_no[d] + folga
            self.y_fronteira.append(y + folga / 2)
        self.y_fronteira[-1] = -self.largura / 2

    def _dedo(self, d):
        o = self.f['ossos'][d]
        comprimento = o['proximal'] + o['media'] + o['distal'] + o['polpa']
        x_mcp = self.f['juntas']['pontaAoPulso'][d] * self.esc_c - comprimento
        mcp = Vector((x_mcp, self.y_no[d], self.ded['arco']['mm'][d]))
        leque = self.ded['leque']['fator']
        dy = mcp.y - mcp.y * leque
        dx = math.sqrt(max(1.0, o['metacarpo'] ** 2 - dy ** 2 - mcp.z ** 2))
        cmc = Vector((x_mcp - dx, mcp.y * leque, 0.0))
        ab = math.radians(_ABERTURA[d] * self.rep['abertura'])
        frente = Vector((math.cos(ab), math.sin(ab), 0.0))
        costas = Vector((0.0, 0.0, 1.0))
        # A MCP dobra em volta do eixo reto, através do dedo no plano da palma; a PIP e a DIP em volta dele inclinado
        # pela convergência (a cascata dos dedos), levado pela flexão de repouso da MCP.
        eixo_mcp = costas.cross(frente).normalized()
        q_mcp = Quaternion(eixo_mcp, math.radians(self.rep['mcp']))
        eixo_ip = (q_mcp @ (Quaternion(frente, math.radians(self.ded['convergencia']['graus'][d])) @ eixo_mcp))
        eixo_ip.normalize()
        comps = [o['proximal'], o['media'], o['distal'] + o['polpa']]
        giros = [q_mcp, Quaternion(eixo_ip, math.radians(self.rep['pip'])),
                 Quaternion(eixo_ip, math.radians(self.rep['dip']))]
        pontos = [mcp]
        dirs, normais = [], []
        frente_agora, costas_agora = frente, costas
        for q, comp in zip(giros, comps):
            frente_agora = (q @ frente_agora).normalized()
            costas_agora = (q @ costas_agora).normalized()
            dirs.append(frente_agora)
            normais.append(costas_agora)
            pontos.append(pontos[-1] + dirs[-1] * comp)
        (lp, ep), (ld, ed) = self._larguras_juntas(d)
        return {
            'cmc': cmc, 'mcp': mcp, 'pip': pontos[1], 'dip': pontos[2], 'ponta': pontos[3],
            'dirs': dirs, 'normais': normais, 'eixo_mcp': eixo_mcp, 'eixo_ip': eixo_ip, 'frente': frente,
            'larg_no': self.larg_no[d], 'pip_sec': (lp, ep), 'dip_sec': (ld, ed), 'polpa': o['polpa'],
            'distal': o['distal'],
        }

    def _polegar(self):
        o = self.f['ossos']['polegar']
        p = self.ded['polegar']
        cmc = Vector(p['cmc'])
        ang = math.radians(p['anguloNaPalma'])
        t0 = Vector((math.cos(ang), math.sin(ang), 0.0))
        costas = Vector((0.0, 0.0, 1.0))
        eixo_abd = costas.cross(t0).normalized()
        frente = (Quaternion(eixo_abd, math.radians(self.rep['polegarAbducao'])) @ t0).normalized()
        # "Costas" do polegar: a normal da palma perpendicular à direção dele, girada pela pronação para o lado do polegar
        # (+Y): a unha de lado, virada para fora, e a polpa de frente para o indicador — como na mão relaxada, e a flexão
        # (que dobra para o lado da polpa) leva a ponta para a palma e o mínimo. Na mão direita esse giro é negativo em
        # volta da direção do polegar (positivo levaria a unha para o indicador e a flexão para fora da mão).
        n0 = (costas - frente * costas.dot(frente)).normalized()
        normal = (Quaternion(frente, -math.radians(p['pronacao'])) @ n0).normalized()
        eixo = normal.cross(frente).normalized()
        comps = [o['metacarpo'], o['proximal'], o['distal'] + o['polpa']]
        angulos = [0.0, self.rep['polegarMcp'], self.rep['polegarIp']]
        pontos = [cmc]
        dirs, normais = [], []
        acumulado = 0.0
        for ang2, comp in zip(angulos, comps):
            acumulado += ang2
            q = Quaternion(eixo, math.radians(acumulado))
            dirs.append((q @ frente).normalized())
            normais.append((q @ normal).normalized())
            pontos.append(pontos[-1] + dirs[-1] * comp)
        ip = self.f['juntas']['polegar']['ip']
        lip = ip['largura'] * self.esc_l
        eip = espessura_pela_circunferencia(lip, ip['circunferencia'] * self.esc_l)
        return {
            'cmc': cmc, 'mcp': pontos[1], 'ip': pontos[2], 'ponta': pontos[3], 'dirs': dirs, 'normais': normais,
            'eixo': eixo, 'ip_sec': (lip, eip), 'polpa': o['polpa'], 'distal': o['distal'],
        }

    def _pulso(self):
        pulso = self.ded['pulso']
        self.pulso_larg = self.f['juntas']['pulso']['largura'] * self.esc_l
        self.pulso_esp = pulso['espessura']
        self.pulso_raio = pulso['raio']
        self.esp_mao = self.ded['espessuraDaMao']['mm']
        self.raio_mao = self.ded['espessuraDaMao']['raio']

    # ------------------------------------------------------------------ antebraço
    def circunferencia_antebraco(self, x):
        """Circunferência (mm) do antebraço de massinha a x ≤ 0 do pulso: a do pulso da ficha crescendo até a do cotovelo
        como t^expoente (t = distância do pulso sobre o comprimento do antebraço), pela dedução `perfilDoAntebraco`."""
        perfil = self.ded['perfilDoAntebraco']
        c_pulso = self.f['mao']['pulso']['mm']
        t = min(1.0, max(0.0, -x / self.antebraco))
        return c_pulso + (perfil['circunferenciaNoCotovelo'] - c_pulso) * t ** perfil['expoente']

    def secao_antebraco(self, x):
        """(largura, espessura, raio) do antebraço a x ≤ 0: o retângulo arredondado do pulso na escala da circunferência."""
        s = self.circunferencia_antebraco(x) / perimetro_retangulo_arredondado(self.pulso_larg, self.pulso_esp,
                                                                               self.pulso_raio)
        return self.pulso_larg * s, self.pulso_esp * s, self.pulso_raio * s

    # ------------------------------------------------------------------ ossos
    def ossos(self):
        """{nome: (cabeça, cauda, normal das costas)} da mão direita em repouso (mm), sem o sufixo do lado."""
        o = {
            'antebraco': (Vector((-self.antebraco, 0, 0)), Vector((-self.antebraco * self.ded['antebraco']['divisao'], 0, 0)),
                          Vector((0, 0, 1))),
            'torcao': (Vector((-self.antebraco * self.ded['antebraco']['divisao'], 0, 0)), Vector((0, 0, 0)), Vector((0, 0, 1))),
            'mao': (Vector((0, 0, 0)), self.dedos['medio']['mcp'].copy(), Vector((0, 0, 1))),
        }
        pol = self.polegar
        for i, (a, b) in enumerate((('cmc', 'mcp'), ('mcp', 'ip'), ('ip', 'ponta'))):
            o[f'polegar_{i + 1}'] = (pol[a].copy(), pol[b].copy(), pol['normais'][i].copy())
        for d in DEDOS4:
            dd = self.dedos[d]
            if d in METACARPO:
                o[METACARPO[d]] = (dd['cmc'].copy(), dd['mcp'].copy(), Vector((0, 0, 1)))
            for i, (a, b) in enumerate((('mcp', 'pip'), ('pip', 'dip'), ('dip', 'ponta'))):
                o[f'{d}_{i + 1}'] = (dd[a].copy(), dd[b].copy(), dd['normais'][i].copy())
        return o
```

```python file=tools/blender/armas/maos_medidas.py
# Medidas-chave da luva na malha (Fase 4.1b; desenho em docs/superpowers/specs/2026-09-26-4.1b-luvas-e-empunhadura-design.md,
# seção 3.2; plano, Tarefa 3): comprimento, largura nos nós, circunferência no pulso e na boca do punho, cada uma com o
# alvo da ficha mais a luva. Referencial e unidades: os de maos.py (mm).
import math

from .maos import DEDOS4
from .unidades import S


def _envoltoria(pts):
    """Envoltória convexa 2D (cadeia monótona de Andrew), no sentido anti-horário."""
    pts = sorted(set(pts))
    if len(pts) < 3:
        return pts

    def giro(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    baixo, alto = [], []
    for p in pts:
        while len(baixo) >= 2 and giro(baixo[-2], baixo[-1], p) <= 0:
            baixo.pop()
        baixo.append(p)
    for p in reversed(pts):
        while len(alto) >= 2 and giro(alto[-2], alto[-1], p) <= 0:
            alto.pop()
        alto.append(p)
    return baixo[:-1] + alto[:-1]


def perimetro_da_secao(pts3, arestas, x0):
    """Perímetro (mm) da seção da malha no plano x = x0: a envoltória convexa dos pontos onde as arestas cruzam o
    plano (as seções medidas — o pulso e a boca do punho — são convexas; a de fora envolve o forro)."""
    sec = []
    for a, b in arestas:
        pa, pb = pts3[a], pts3[b]
        da, db = pa.x - x0, pb.x - x0
        if abs(da) < 1e-6:
            sec.append((round(pa.y, 6), round(pa.z, 6)))
        if da * db < 0:
            t = da / (da - db)
            q = pa.lerp(pb, t)
            sec.append((round(q.y, 6), round(q.z, 6)))
    h = _envoltoria(sec)
    return sum(math.dist(h[i], h[(i + 1) % len(h)]) for i in range(len(h)))


def medir_mao(ob, mao):
    """Medidas-chave na malha (mm), pela pose de repouso, cada uma com o alvo (a ficha mais a luva):
    - comprimento: do pulso à ponta do médio como se o dedo estivesse esticado (a MCP do médio, as duas falanges e o
      alcance da malha além da DIP, na direção da ponta); na ponta, o tecido e o reforço de couro por cima;
    - largura: nos nós, da borda da MCP II à da V, sem o polegar nem os dedos;
    - pulso: a circunferência no pulso (a do ANSUR II mais a volta da luva);
    - boca: a circunferência do punho na borda (o antebraço de massinha ali, mais a folga e a luva)."""
    me = ob.data
    mw = ob.matrix_world
    # os nomes dos ossos sem o sufixo do lado (a luva com o rig tem _d/_e)
    nomes = {g.index: (g.name[:-2] if g.name[-2:] in ('_d', '_e') else g.name) for g in ob.vertex_groups}
    pts, pol, ded = [], [], []
    for v in me.vertices:
        pts.append((mw @ v.co) / S)
        pol.append(sum(e.weight for e in v.groups if nomes[e.group].startswith('polegar')))
        ded.append(sum(e.weight for e in v.groups
                       if nomes[e.group].rsplit('_', 1)[0] in DEDOS4 and not nomes[e.group].endswith('_0')))
    dd = mao.dedos['medio']
    alcance = max((p - dd['dip']).dot(dd['dirs'][2]) for p in pts if (p - dd['dip']).length < 45.0)
    comprimento = dd['mcp'].x + (dd['pip'] - dd['mcp']).length + (dd['dip'] - dd['pip']).length + alcance

    def janela(d):
        x = mao.dedos[d]['mcp'].x
        return [p for p, wp, wd in zip(pts, pol, ded) if wp < 0.05 and wd <= 0.5 and x - 12.0 <= p.x <= x + 6.0]

    largura = max(p.y for p in janela('indicador')) - min(p.y for p in janela('minimo'))
    arestas = [tuple(e.vertices) for e in me.edges]
    luva = mao.luva
    punho_mm = mao.f['luva']['punho']
    x_boca = -punho_mm + 0.6
    folga_boca = mao.f['luva']['folgaPunho'] * (-x_boca / punho_mm)
    return {
        'comprimento': {'mm': round(comprimento, 2),
                        'alvo': round(mao.f['mao']['comprimento']['mm'] + luva + mao.f['luva']['couro'], 2)},
        'largura': {'mm': round(largura, 2), 'alvo': round(mao.largura + 2 * luva, 2)},
        'pulso': {'mm': round(perimetro_da_secao(pts, arestas, 0.0), 2),
                  'alvo': round(mao.f['mao']['pulso']['mm'] + 2 * math.pi * luva, 2)},
        'boca': {'mm': round(perimetro_da_secao(pts, arestas, x_boca), 2),
                 'alvo': round(mao.circunferencia_antebraco(x_boca) + 2 * math.pi * (luva + folga_boca), 2)},
    }
```

```python file=tools/blender/armas/maos_limite.py
# Ajuste da gaiola ao limite de Catmull-Clark (Fase 4.1b; desenho em
# docs/superpowers/specs/2026-09-26-4.1b-luvas-e-empunhadura-design.md, seção 3.2): as âncoras da gaiola são movidas
# para que a superfície limite (onde o modificador Subdivision Surface com "Use Limit Surface" põe os vértices) passe
# pelos pontos de desenho delas. Separado de maos_gaiola.py, que desenha a gaiola.


def ajustar_ao_limite(bm, livres=(), iteracoes=120):
    """Move as âncoras da gaiola (só quadriláteros; todos os vértices menos os `livres`) para que a superfície limite
    de Catmull-Clark passe pelos pontos de desenho delas (a posição de cada vértice ao entrar); os livres ficam onde
    estão. A posição limite de um vértice de valência n é (n²·v + 4·Σ vizinhos pelas arestas + Σ opostos nas faces) /
    (n·(n+5)); na borda livre (o forro, com a borda suave), (a + 4·v + b)/6. A iteração de Jacobi soma a cada âncora a
    diferença entre o ponto de desenho e a posição limite; o operador é uma média de pesos positivos, então converge.
    Devolve o maior resíduo nas âncoras (mm)."""
    alvo = {v: v.co.copy() for v in bm.verts}
    regras = []
    for v in bm.verts:
        borda = [e.other_vert(v) for e in v.link_edges if e.is_boundary]
        if borda:
            if len(borda) != 2:
                raise ValueError(f'gaiola: vértice de borda com {len(borda)} vizinhos na borda')
            regras.append((v, 0, borda, ()))
            continue
        arestas = [e.other_vert(v) for e in v.link_edges]
        opostos = []
        for f in v.link_faces:
            vs = list(f.verts)
            if len(vs) != 4:
                raise ValueError('gaiola: só quadriláteros')
            opostos.append(vs[(vs.index(v) + 2) % 4])
        regras.append((v, len(arestas), arestas, opostos))

    def limites():
        lim = []
        for v, n, arestas, opostos in regras:
            if n == 0:
                a, b = arestas
                lim.append((a.co + v.co * 4.0 + b.co) / 6.0)
            else:
                s = v.co * float(n * n)
                for u in arestas:
                    s += u.co * 4.0
                for u in opostos:
                    s += u.co
                lim.append(s / float(n * (n + 5)))
        return lim

    for _ in range(iteracoes):
        for (v, *_r), p in zip(regras, limites()):
            if v not in livres:
                v.co += alvo[v] - p
    return max((alvo[v] - p).length for (v, *_r), p in zip(regras, limites()) if v not in livres)
```

```python file=tools/blender/armas/maos_gaiola.py
# Gaiola de quadriláteros da luva direita e a malha base (Fase 4.1b; desenho em
# docs/superpowers/specs/2026-09-26-4.1b-luvas-e-empunhadura-design.md, seção 3.2). A palma em anéis de 20 vértices
# (costas do mínimo ao indicador, lado do polegar, palma do indicador ao mínimo, lado do mínimo) do pulso à linha dos
# nós, com as quatro portas dos dedos na linha dos nós e a do polegar no canto da palma do lado do indicador (a
# eminência tenar); os dedos em anéis elípticos, três em cada junta, e a ponta em cúpula; o punho da luva sobre o
# antebraço de massinha, com a borda dobrada para dentro.
# Cada vértice nasce num PONTO DE DESENHO. Os que carregam medida — as seções das juntas de Greiner, as pontas dos
# dedos, o pulso e o punho, o contorno da palma e os lados da linha dos nós, tudo com a espessura da luva — são
# âncoras: o ajuste ao limite move a gaiola até a superfície limite de Catmull-Clark (onde o modificador Subdivision
# Surface, com "Use Limit Surface", põe os vértices da malha subdividida) passar por eles, e as medidas da malha saem
# as da ficha sem fator de folga chutado. As junções (as portas dos dedos e do polegar, a tenar, a linha dos nós, as
# dobras entre os dedos, a estação antes dos nós) ficam livres, com a suavização natural da subdivisão: forçar a
# superfície por pontos tão próximos ali dobraria a malha. O modelo alto (3 níveis) é a mesma superfície do de jogo.
# Cada vértice leva os pesos dos ossos (a subdivisão interpola), cada face a zona (couro na palma, na face palmar dos
# dedos, nas pontas e entre o polegar e o indicador; tecido no resto) e as arestas das costuras ficam marcadas para as
# UV (lados, base de cada dedo, a porta do polegar, o pulso); as faces do forro do punho (a volta da borda para dentro)
# ficam no atributo de face `forro`. O ajuste ao limite está em maos_limite.py e as medidas em maos_medidas.py.
# Referencial e unidades: os de maos.py (mm).
import math

import bmesh
import bpy
from mathutils import Vector

from .maos import DEDOS4, METACARPO, meia_altura_no_contorno
from .maos_limite import ajustar_ao_limite
from .unidades import S

# Estações da palma (mm, sem a luva): x a partir do pulso, largura, costas e palma (z), raio do canto do retângulo
# arredondado, quanto a borda das costas desce (o arco transverso), a queda a mais do lado do mínimo (os metacarpos IV e
# V ficam mais baixos), o oco no meio da palma e a eminência hipotenar na borda do mínimo. A estação do pulso vem da
# ficha (retângulo arredondado de 61,9 × 38 com raio 18); a última fica a meio caminho entre a terceira e a linha dos
# nós, coluna a coluna (paralela aos nós). As três primeiras levam a porta do polegar: a terceira em x = 64, perto da
# dobra entre o polegar e o indicador de Greiner (69,1 × 189,3/194,5 = 67,3 mm).
_PALMA = (
    # x,    largura, costas, palma, raio, arco, queda, oco, hipotenar
    (21.0, 72.0, 17.0, -20.5, 16.0, 2.5, 1.0, 1.5, 3.0),
    (43.0, 80.0, 15.0, -21.5, 14.5, 3.0, 1.5, 3.5, 3.5),
    (64.0, 84.0, 13.5, -20.5, 13.0, 3.0, 2.0, 3.0, 2.5),
    (None, 85.0, 12.3, -19.0, 12.0, 2.5, 2.5, 1.5, 1.0),
)
_PORTA_POLEGAR = (1, 2, 3)  # anéis da palma com a porta do polegar, nos índices 10–12 (a palma do lado do indicador)
_X_PUNHO = (-12.0, -24.0, -36.0)  # anéis do punho antes da borda
_COS45 = math.sqrt(0.5)
_BOJO_JUNTA = 1.015  # o anel do centro de cada junta, um pouco mais largo que os vizinhos (o volume da junta)


def _suave(t):
    t = min(1.0, max(0.0, t))
    return t * t * (3.0 - 2.0 * t)


def _entre(v, a, b):
    return _suave((v - a) / (b - a))


def _mistura(pesos):
    """Normaliza um dicionário osso → peso (tira os nulos)."""
    total = sum(w for w in pesos.values() if w > 0)
    return {k: w / total for k, w in pesos.items() if w > 1e-4}


class _Gaiola:
    """A gaiola em construção: vértices com pesos, faces com zona, arestas de costura."""

    def __init__(self):
        self.bm = bmesh.new()
        self.pesos = {}  # vértice → {osso: peso}
        self.zonas = {}  # face → zona
        self.costuras = set()  # pares de vértices
        self.livres = set()  # vértices das junções, fora do ajuste ao limite
        self.estufar = {}  # vértice → mm para fora (os reforços de couro por cima da luva)
        self.forro = set()  # faces da volta da borda do punho para dentro (a parede de dentro)

    def v(self, co, pesos):
        vert = self.bm.verts.new(co)
        self.pesos[vert] = _mistura(pesos)
        return vert

    def face(self, verts, zona):
        f = self.bm.faces.new(verts)
        self.zonas[f] = zona
        return f

    def costura(self, a, b):
        self.costuras.add(frozenset((a, b)))

    def faixa(self, anel_a, anel_b, zonas):
        """Quadriláteros entre dois anéis fechados do mesmo tamanho; `zonas[i]` é a zona da face que começa no vértice i."""
        n = len(anel_a)
        return [self.face((anel_a[i], anel_a[(i + 1) % n], anel_b[(i + 1) % n], anel_b[i]), zonas[i]) for i in range(n)]


# ---------------------------------------------------------------------------------------------- seções
def _colunas(mao):
    """As 9 colunas da linha dos nós (y, do mínimo ao indicador: a borda, o centro de cada dedo e as fronteiras) e o dedo
    de cada coluna (a fronteira entre dois dedos fica com o de fora, o do lado do mínimo)."""
    fr = list(reversed(mao.y_fronteira))
    centros = [mao.y_no[d] for d in reversed(DEDOS4)]
    ys = []
    for i in range(4):
        ys += [fr[i], centros[i]]
    ys.append(fr[4])
    dedos = [d for d in reversed(DEDOS4) for _ in (0, 1)] + ['indicador']
    return ys, dedos


def _secao_palma(mao, ys_nos, largura, costas, palma, raio, arco, queda, oco, hipo):
    """Os 20 pontos (y, z) de uma estação da palma, na ordem do anel. O contorno é o retângulo arredondado com a luva;
    as bordas das costas e da palma ficam no canto (a 45°), o lado no extremo da largura (a meia largura mais a luva, por
    onde a superfície final passa), e as colunas de dentro na proporção das colunas dos nós."""
    luva = mao.luva
    meia_l = largura / 2 + luva
    meia_a = (costas - palma) / 2 + luva
    zc = (costas + palma) / 2
    r = raio + luva
    k = (meia_l - r * (1 - _COS45)) / (mao.largura / 2)
    cols = []
    for y0 in ys_nos:
        y = y0 * k
        u = y / meia_l
        h = meia_altura_no_contorno(y, meia_l, meia_a, r)
        zd = zc + h - arco * u * u - queda * max(0.0, -u) ** 2
        zp = zc - h + oco * (1 - u * u) ** 2 - hipo * math.exp(-((u + 0.62) / 0.3) ** 2)
        cols.append((y, zd, zp))
    anel = [(y, zd) for y, zd, _ in cols]
    anel.append((meia_l, (cols[8][1] + cols[8][2]) / 2))
    anel += [(y, zp) for y, _, zp in reversed(cols)]
    anel.append((-meia_l, (cols[0][1] + cols[0][2]) / 2))
    return anel


def _pontos_elipticos(centro, frente, costas, meia_l, meia_e):
    """Oito pontos em volta de `centro`, no plano perpendicular a `frente`: a partir de costas-ulnar (-45°) girando
    para o lado do polegar (a ordem canônica dos anéis; as zonas e a calota contam com ela)."""
    radial = costas.cross(frente).normalized()
    costas = frente.cross(radial).normalized()
    pts = []
    for k in range(8):
        th = math.radians(-45.0 + 45.0 * k)
        pts.append(centro + costas * (meia_e * math.cos(th)) + radial * (meia_l * math.sin(th)))
    return pts


def _casar_porta(porta, pontos):
    """A porta (8 vértices da palma) reordenada para casar com o primeiro anel na ordem canônica: o giro e o sentido
    de menor distância somada. Sem isso a faixa entre os dois torceria."""
    melhor = None
    n = len(porta)
    for sentido in (1, -1):
        for s in range(n):
            perm = [(s + sentido * i) % n for i in range(n)]
            dist = sum((porta[perm[i]].co - pontos[i]).length for i in range(n))
            if melhor is None or dist < melhor[0]:
                melhor = (dist, perm)
    return [porta[i] for i in melhor[1]]


def _referencial(dd, seg):
    """(frente, costas) de um anel: o do segmento `seg`, ou a bissetriz de dois segmentos (o anel do centro de uma
    junta dobrada fica no meio do ângulo, senão belisca o lado de dentro da dobra)."""
    if isinstance(seg, tuple):
        a, b = seg
        return (dd['dirs'][a] + dd['dirs'][b]).normalized(), (dd['normais'][a] + dd['normais'][b]).normalized()
    return dd['dirs'][seg], dd['normais'][seg]


def _fator_cupula(t_anel, t_a, t_ponta):
    """Seção relativa de um anel da cúpula da ponta, no perfil de elipse que vai do anel `t_a` (seção inteira) à ponta."""
    s = (t_anel - t_a) / (t_ponta - t_a)
    return math.sqrt(max(0.0, 1.0 - s * s))


# ---------------------------------------------------------------------------------------------- gaiola
def gerar_gaiola(mao):
    """A gaiola da luva direita (bmesh em mm) com os pontos de desenho, os pesos, as zonas e as costuras."""
    g = _Gaiola()
    luva = mao.luva
    ys_nos, dedo_da_coluna = _colunas(mao)
    mcp = {d: mao.dedos[d]['mcp'] for d in DEDOS4}
    cmc4 = mao.dedos['anelar']['cmc'].x

    def pesos_palma(x, y):
        w = {'mao': 1.0}
        if x < 12.0:
            t = _entre(x, -8.0, 12.0)
            w = {'mao': t, 'torcao': 1.0 - t}
        # A borda do mínimo e do anelar fecha em concha com os metacarpos deles.
        tx = _entre(x, cmc4 + 5.0, cmc4 + 35.0)
        w5 = tx * _entre(-y, 18.0, 36.0)
        w4 = tx * max(0.0, 1.0 - abs(y - mao.y_no['anelar']) / 14.0) * 0.6
        if w5 > 0:
            w['minimo_0'] = w5
        if w4 > 0:
            w['anelar_0'] = w4
        w['mao'] = max(0.0, w.get('mao', 0.0) - w5 - w4)
        return w

    # ---------------------------------------------------------------- a linha dos nós (os pontos antes dos anéis)
    # Costas: o alto de cada nó (centro do dedo) e os vales entre eles; as bordas de fora no canto do retângulo
    # arredondado da mão nos nós (85 × 29 com raio 12, da ficha). Palma: a almofada na base de cada dedo e as pregas
    # entre eles. Lados: no extremo da largura da mão (a borda da MCP II e da V), por onde passa a largura da ficha.
    r_nos = mao.raio_mao + luva
    meia_l_nos = mao.largura / 2 + luva
    y_canto = meia_l_nos - r_nos * (1 - _COS45)

    def topo_fundo(d):
        return (mcp[d].z + mao.esp_mao * 0.38 + luva, mcp[d].z - mao.esp_mao * 0.62 - luva)

    nos_costas, nos_palma = [], []
    for j in range(9):
        if j in (0, 8):
            d = dedo_da_coluna[j]
            topo, fundo = topo_fundo(d)
            zc, meia_a = (topo + fundo) / 2, (topo - fundo) / 2
            y = y_canto if j == 8 else -y_canto
            h = meia_altura_no_contorno(y, meia_l_nos, meia_a, r_nos)
            nos_costas.append(Vector((mcp[d].x - 2.0, y, zc + h)))
            nos_palma.append(Vector((mcp[d].x + 9.0, y, zc - h)))
        elif j % 2 == 1:
            d = dedo_da_coluna[j]
            topo, fundo = topo_fundo(d)
            nos_costas.append(Vector((mcp[d].x + 1.5, ys_nos[j], topo + 1.2)))
            nos_palma.append(Vector((mcp[d].x + 15.0, ys_nos[j], fundo)))
        else:  # vale entre dois dedos: a média dos dois
            a, b = dedo_da_coluna[j - 1], dedo_da_coluna[j + 1]
            ta, fa = topo_fundo(a)
            tb, fb = topo_fundo(b)
            x = (mcp[a].x + mcp[b].x) / 2
            nos_costas.append(Vector((x - 2.0, ys_nos[j], (ta + tb) / 2 - 1.5)))
            nos_palma.append(Vector((x + 9.0, ys_nos[j], (fa + fb) / 2 + 2.0)))
    lados_nos = {}
    for lado, d in (('polegar', 'indicador'), ('minimo', 'minimo')):
        topo, fundo = topo_fundo(d)
        lados_nos[lado] = Vector((mcp[d].x + 2.0, meia_l_nos if lado == 'polegar' else -meia_l_nos, (topo + fundo) / 2))

    # ---------------------------------------------------------------- anéis da palma
    def anel_de(pts_yz, xs):
        """Vértices de um anel a partir dos (y, z) e do x de cada um."""
        return [g.v(Vector((x, y, z)), pesos_palma(x, y)) for (y, z), x in zip(pts_yz, xs)]

    aneis = []
    sec0 = _secao_palma(mao, ys_nos, mao.pulso_larg, mao.pulso_esp / 2, -mao.pulso_esp / 2, mao.pulso_raio,
                        0.0, 0.0, 0.0, 0.0)
    aneis.append(anel_de(sec0, [0.0] * 20))
    for est in _PALMA[:3]:
        aneis.append(anel_de(_secao_palma(mao, ys_nos, *est[1:]), [est[0]] * 20))
    x3 = _PALMA[2][0]
    xs4 = ([(x3 + p.x) / 2 for p in nos_costas] + [(x3 + lados_nos['polegar'].x) / 2]
           + [(x3 + p.x) / 2 for p in reversed(nos_palma)] + [(x3 + lados_nos['minimo'].x) / 2])
    aneis.append(anel_de(_secao_palma(mao, ys_nos, *_PALMA[3][1:]), xs4))
    nos_pts = nos_costas + [lados_nos['polegar']] + list(reversed(nos_palma)) + [lados_nos['minimo']]
    nos = []
    for i, p in enumerate(nos_pts):
        if i == 9:
            w = {'mao': 0.7, 'indicador_1': 0.3}
        elif i == 19:
            w = {'minimo_0': 0.6, 'mao': 0.2, 'minimo_1': 0.2}
        else:
            # Costas: 55 % no metacarpo e 45 % na falange; palma, o contrário. Um vale divide entre os dois dedos.
            j = i if i < 9 else 18 - i
            vizinhos = [dedo_da_coluna[j]] if j % 2 == 1 or j in (0, 8) else [dedo_da_coluna[j - 1], dedo_da_coluna[j + 1]]
            no_meta, na_falange = (0.55, 0.45) if i < 9 else (0.45, 0.55)
            w = {}
            for d in vizinhos:
                base = METACARPO.get(d, 'mao')
                w[base] = w.get(base, 0.0) + no_meta / len(vizinhos)
                w[f'{d}_1'] = w.get(f'{d}_1', 0.0) + na_falange / len(vizinhos)
        nos.append(g.v(p, w))
    aneis.append(nos)
    # Zonas da palma: a metade da palma, de um lado ao outro (as faces que começam nos índices 9..18), é couro; as
    # costas, tecido.
    zonas = ['tecido'] * 9 + ['couro'] * 10 + ['tecido']
    for a, b in zip(aneis[:-1], aneis[1:]):
        g.faixa(a, b, zonas)

    # ---------------------------------------------------------------- tampa: portas dos dedos e as dobras entre eles
    dobras = mao.f['juntas']['dobras']
    x_web = [dobras['anelarMinimo'], dobras['medioAnelar'], dobras['indicadorMedio']]
    meio = {0: nos[19], 8: nos[9]}
    for j, xw in zip((2, 4, 6), x_web):
        a, b = dedo_da_coluna[j - 1], dedo_da_coluna[j + 1]
        z = (mcp[a].z + mcp[b].z) / 2 - 3.5
        meio[j] = g.v(Vector((xw * mao.esc_c, ys_nos[j], z)), {f'{a}_1': 0.35, f'{b}_1': 0.35, 'mao': 0.3})
    costas = nos[0:9]
    palma = [nos[18 - j] for j in range(9)]  # palma[j] na coluna j (do mínimo ao indicador)
    portas = {}
    for k, d in enumerate(reversed(DEDOS4)):
        j0 = 2 * k
        portas[d] = [costas[j0], costas[j0 + 1], costas[j0 + 2], meio[j0 + 2], palma[j0 + 2], palma[j0 + 1], palma[j0],
                     meio[j0]]
    for d in DEDOS4:
        _dedo(g, mao, d, portas[d])

    # ---------------------------------------------------------------- polegar: porta no canto da palma (a tenar)
    r1, r2, r3 = (aneis[i] for i in _PORTA_POLEGAR)
    dentro = {r1[10], r1[11], r1[12], r2[10], r2[11], r2[12], r3[10], r3[11], r3[12]}
    for f in list(g.bm.faces):
        if set(f.verts) <= dentro:
            del g.zonas[f]
            g.bm.faces.remove(f)
    g.bm.verts.remove(r2[11])
    del g.pesos[r2[11]]
    porta_pol = [r1[10], r1[11], r1[12], r2[12], r3[12], r3[11], r3[10], r2[10]]
    for v in porta_pol:
        g.pesos[v] = _mistura({**g.pesos[v], 'polegar_1': 0.8 * sum(g.pesos[v].values())})
    aneis_pol = _polegar(g, mao, porta_pol)
    # A palma em volta da tenar acompanha o metacarpo do polegar, pela distância a ele.
    pol = mao.polegar
    seg_a, seg_b = pol['cmc'], pol['mcp']
    no_polegar = set(porta_pol).union(*aneis_pol)
    for anel in aneis[:5]:
        for v in anel:
            if not v.is_valid or v in no_polegar:
                continue
            ab = seg_b - seg_a
            t = max(0.0, min(1.0, (v.co - seg_a).dot(ab) / ab.length_squared))
            dist = (v.co - (seg_a + ab * t)).length
            w_pol = 0.3 * (1.0 - _suave(dist / 32.0))
            if w_pol > 0.01:
                total = sum(g.pesos[v].values())
                g.pesos[v] = _mistura({**{k: w * (1 - w_pol) / total for k, w in g.pesos[v].items()},
                                        'polegar_1': w_pol})

    # Livres: a linha dos nós (menos os dois lados, que dão a largura), a estação antes dela, as dobras entre os dedos,
    # a porta do polegar e a palma em volta dela.
    g.livres.update(v for i, v in enumerate(nos) if i not in (9, 19))
    g.livres.update(aneis[4])
    g.livres.update(meio[j] for j in (2, 4, 6))
    g.livres.update(porta_pol)
    for r in (r1, r2, r3):
        g.livres.update((r[9], r[13]))
    g.livres.update(aneis[0][i] for i in (10, 11, 12))
    # O reforço da palma: uma segunda camada de couro sobre a palma, da base da mão até a linha da dobra do polegar
    # (a terceira estação, x = 64), com a borda saliente atravessando a palma do polegar ao mínimo; continua na tenar
    # e na volta entre o polegar e o indicador, e dobra um pouco para os lados.
    couro = mao.f['luva']['couro']
    for r, k in ((r1, 1.0), (r2, 1.0), (r3, 1.8)):
        for i in range(10, 19):
            if r[i].is_valid:
                g.estufar[r[i]] = couro * k
        for i in (9, 19):
            g.estufar[r[i]] = couro * 0.5
    for v in aneis_pol[0]:
        g.estufar[v] = couro

    # ---------------------------------------------------------------- punho e borda
    # O punho veste o antebraço de massinha (o perfil da ficha) com a folga crescendo do pulso (0) até a boca
    # (folgaPunho); por fora, mais a espessura do tecido. A borda dobra para dentro num lábio e volta 8 mm por dentro
    # (o forro), sem parede de espessura zero.
    punho_mm = mao.f['luva']['punho']
    folga_boca = mao.f['luva']['folgaPunho']
    base = aneis[0]
    meia_l0, meia_a0 = mao.pulso_larg / 2 + luva, mao.pulso_esp / 2 + luva

    def folga(x):
        return folga_boca * min(1.0, -x / punho_mm)

    def anel_punho(x, desloc):
        largura, espessura, _ = mao.secao_antebraco(x)
        sy = (largura / 2 + desloc) / meia_l0
        sz = (espessura / 2 + desloc) / meia_a0
        return [g.v(Vector((x, v.co.y * sy, v.co.z * sz)), {'torcao': 1.0}) for v in base]

    punho = [base]
    for x in _X_PUNHO:
        punho.append(anel_punho(x, luva + folga(x)))
    x_borda = -punho_mm + 0.6
    punho.append(anel_punho(x_borda, luva + folga(x_borda)))
    labio = anel_punho(-punho_mm, luva / 2 + folga(-punho_mm))
    dentro_borda = anel_punho(x_borda, folga(x_borda))
    x_forro = -punho_mm + 8.0
    forro = anel_punho(x_forro, folga(x_forro))
    for a, b in zip(punho[:-1], punho[1:]):
        g.faixa(b, a, ['tecido'] * 20)
    g.faixa(labio, punho[-1], ['tecido'] * 20)
    g.forro.update(g.faixa(dentro_borda, labio, ['tecido'] * 20))
    g.forro.update(g.faixa(forro, dentro_borda, ['tecido'] * 20))

    # ---------------------------------------------------------------- costuras das UV
    for i in range(20):
        g.costura(aneis[0][i], aneis[0][(i + 1) % 20])
    for a, b in zip(aneis[:-1], aneis[1:]):
        g.costura(a[19], b[19])  # lado do mínimo
        g.costura(a[9], b[9])  # lado do polegar
    for a, b in zip(punho[:-1] + [punho[-1], labio, dentro_borda], punho[1:] + [labio, dentro_borda, forro]):
        g.costura(a[19], b[19])
    # O reforço da palma é um painel costurado: as bordas dele na primeira estação e na da dobra do polegar (a borda
    # saliente), de um lado da palma ao outro.
    for r in (r1, r3):
        for i in range(9, 19):
            if r[i].is_valid and r[i + 1].is_valid:
                g.costura(r[i], r[i + 1])
    bmesh.ops.recalc_face_normals(g.bm, faces=g.bm.faces[:])
    return g


def _dedo(g, mao, d, porta):
    """Os anéis de um dedo a partir da porta dele: meio da falange proximal, a PIP em três anéis, o meio da média, a
    DIP em três anéis, a polpa e a cúpula da ponta em dois anéis e o centro — a ponta de desenho no comprimento do osso
    mais a polpa e a luva (a ponta do médio dá o comprimento da mão)."""
    dd = mao.dedos[d]
    luva = mao.luva
    (lp, ep), (ld, ed) = dd['pip_sec'], dd['dip_sec']
    base_sec = (dd['larg_no'] + 2 * luva, ep * 1.12 + 2 * luva)
    pip_sec = (lp + 2 * luva, ep + 2 * luva)
    dip_sec = (ld + 2 * luva, ed + 2 * luva)
    polpa_sec = (ld * 0.97 + 2 * luva, ed * 0.95 + 2 * luva)
    osso = [f'{d}_1', f'{d}_2', f'{d}_3']
    aneis = [porta]

    def anel(ponto, seg, sec, pesos, palmar=0.0):
        frente, costas = _referencial(dd, seg)
        pts = _pontos_elipticos(ponto - costas * palmar, frente, costas, sec[0] / 2, sec[1] / 2)
        if len(aneis) == 1:
            aneis[0] = _casar_porta(aneis[0], pts)
        a = [g.v(p, pesos) for p in pts]
        aneis.append(a)
        return a

    def vezes(sec, k):
        return sec[0] * k, sec[1] * k

    comp1 = (dd['pip'] - dd['mcp']).length
    comp2 = (dd['dip'] - dd['pip']).length
    comp3 = (dd['ponta'] - dd['dip']).length
    meio1 = ((base_sec[0] + pip_sec[0]) / 2 * 0.97, (base_sec[1] + pip_sec[1]) / 2 * 0.95)
    anel(dd['mcp'] + dd['dirs'][0] * comp1 * 0.5, 0, meio1, {osso[0]: 1.0})
    e = 4.0
    anel(dd['pip'] - dd['dirs'][0] * e, 0, pip_sec, {osso[0]: 0.85, osso[1]: 0.15})
    anel(dd['pip'], (0, 1), vezes(pip_sec, _BOJO_JUNTA), {osso[0]: 0.5, osso[1]: 0.5})
    anel(dd['pip'] + dd['dirs'][1] * e, 1, pip_sec, {osso[0]: 0.15, osso[1]: 0.85})
    meio2 = ((pip_sec[0] + dip_sec[0]) / 2 * 0.97, (pip_sec[1] + dip_sec[1]) / 2 * 0.95)
    anel(dd['pip'] + dd['dirs'][1] * comp2 * 0.5, 1, meio2, {osso[1]: 1.0})
    e = 3.0
    anel(dd['dip'] - dd['dirs'][1] * e, 1, dip_sec, {osso[1]: 0.85, osso[2]: 0.15})
    anel(dd['dip'], (1, 2), vezes(dip_sec, _BOJO_JUNTA), {osso[1]: 0.5, osso[2]: 0.5})
    anel(dd['dip'] + dd['dirs'][2] * e, 2, dip_sec, {osso[1]: 0.15, osso[2]: 0.85})
    ponta_t = comp3 + luva
    anel(dd['dip'] + dd['dirs'][2] * comp3 * 0.45, 2, polpa_sec, {osso[2]: 1.0}, ed * 0.04)
    anel(dd['dip'] + dd['dirs'][2] * comp3 * 0.76, 2, vezes(polpa_sec, 0.9), {osso[2]: 1.0}, ed * 0.08)
    k = 0.9 * _fator_cupula(comp3 * 0.93, comp3 * 0.76, ponta_t)
    ponta = anel(dd['dip'] + dd['dirs'][2] * comp3 * 0.93, 2, vezes(polpa_sec, k), {osso[2]: 1.0}, ed * 0.12)
    _soltar_dentro_das_juntas(g, aneis)
    _reforco_da_ponta(g, mao, aneis)
    # Zonas: couro na metade palmar do dedo inteiro (de um lado ao outro) e em volta da ponta (da polpa em diante);
    # tecido nas costas.
    for i, (a, b) in enumerate(zip(aneis[:-1], aneis[1:])):
        zonas = ['couro' if (i >= 9 or 3 <= k2 <= 6) else 'tecido' for k2 in range(8)]
        g.faixa(a, b, zonas)
        g.costura(a[7], b[7])  # lado de fora do dedo (para o mínimo)
    porta = aneis[0]
    for k2 in range(8):
        g.costura(porta[k2], porta[(k2 + 1) % 8])
    centro = dd['dip'] + dd['dirs'][2] * ponta_t - dd['normais'][2] * ed * 0.12
    c = g.v(centro, {osso[2]: 1.0})
    g.estufar[c] = mao.f['luva']['couro']
    for k2 in (0, 2, 4, 6):
        g.face((ponta[k2], ponta[k2 + 1], ponta[(k2 + 2) % 8], c), 'couro')
    g.costura(ponta[7], ponta[0])
    g.costura(ponta[0], c)


def _soltar_dentro_das_juntas(g, aneis):
    """Solta do ajuste ao limite o lado da palma (os pontos 4, 5 e 6) dos anéis de antes e de depois de cada junta
    (os anéis 2, 4, 6 e 8 a partir da porta, nos dedos e no polegar). No repouso a junta já dobra (PIP 20°, DIP 10°) e,
    por dentro, esses anéis ficam a 2,5 mm do anel do centro: forçar a superfície limite pelos três pontos tão juntos no
    lado côncavo cruzava a gaiola (o anel de antes passava à frente do de depois) e a malha dobrava sobre si mesma. O
    anel do centro, com a seção medida da junta, continua âncora."""
    for i in (2, 4, 6, 8):
        g.livres.update(aneis[i][k] for k in (4, 5, 6))


def _reforco_da_ponta(g, mao, aneis):
    """O reforço de couro da ponta (a volta da unha até a polpa): a camada de couro por cima do tecido, dos anéis da
    cúpula em diante, com a borda no anel da polpa (meia espessura: o degrau da borda)."""
    couro = mao.f['luva']['couro']
    for v in aneis[9]:
        g.estufar[v] = couro * 0.5
    for anel in aneis[10:12]:
        for v in anel:
            g.estufar[v] = couro


def _polegar(g, mao, porta):
    """Os anéis do polegar a partir da porta na palma: a tenar (um anel de transição entre a porta e a MCP, estufado para
    o lado da palma — o metacarpo do polegar some dentro da eminência tenar, só o que passa da MCP é "o dedo"), a MCP
    em três anéis, o meio da falange proximal, a IP em três anéis, a polpa e a cúpula da ponta. Devolve os anéis (sem
    a porta)."""
    p = mao.polegar
    luva = mao.luva
    lip, eip = p['ip_sec']
    fr = p['dirs'][0]
    mcp_sec = (lip * 1.10 + 2 * luva, eip * 1.12 + 2 * luva)
    ip_sec = (lip + 2 * luva, eip + 2 * luva)
    polpa_sec = (lip * 0.95 + 2 * luva, eip * 0.92 + 2 * luva)
    aneis = [porta]

    def anel(ponto, seg, sec, pesos, palmar=0.0):
        frente, costas = _referencial(p, seg)
        pts = _pontos_elipticos(ponto - costas * palmar, frente, costas, sec[0] / 2, sec[1] / 2)
        a = [g.v(q, pesos) for q in pts]
        aneis.append(a)
        return a

    def vezes(sec, k):
        return sec[0] * k, sec[1] * k

    comp2 = (p['ip'] - p['mcp']).length
    comp3 = (p['ponta'] - p['ip']).length
    e = 4.5
    # A tenar: a porta casada com o primeiro anel da MCP e o anel do meio entre os dois, estufado para fora — mais do
    # lado da palma (-Z), onde ficam os músculos da tenar, e pouco do lado das costas do metacarpo.
    mcp_menos = _pontos_elipticos(p['mcp'] - fr * e, fr, p['normais'][0], mcp_sec[0] / 2, mcp_sec[1] / 2)
    aneis[0] = _casar_porta(porta, mcp_menos)
    centro = sum((v.co for v in aneis[0]), Vector()).lerp(sum(mcp_menos, Vector()), 0.5) / 8.0
    tenar = []
    for v, q in zip(aneis[0], mcp_menos):
        meio = v.co.lerp(q, 0.5)
        fora = (meio - centro).normalized()
        tenar.append(g.v(meio + fora * (1.5 + 3.5 * max(0.0, -fora.z)), {'polegar_1': 0.75, 'mao': 0.25}))
    aneis.append(tenar)
    g.livres.update(tenar)
    anel(p['mcp'] - fr * e, 0, mcp_sec, {'polegar_1': 0.85, 'polegar_2': 0.15})
    anel(p['mcp'], (0, 1), vezes(mcp_sec, _BOJO_JUNTA), {'polegar_1': 0.5, 'polegar_2': 0.5})
    anel(p['mcp'] + p['dirs'][1] * e, 1, mcp_sec, {'polegar_1': 0.15, 'polegar_2': 0.85})
    meio = ((mcp_sec[0] + ip_sec[0]) / 2 * 0.97, (mcp_sec[1] + ip_sec[1]) / 2 * 0.95)
    anel(p['mcp'] + p['dirs'][1] * comp2 * 0.5, 1, meio, {'polegar_2': 1.0})
    e = 4.0
    anel(p['ip'] - p['dirs'][1] * e, 1, ip_sec, {'polegar_2': 0.85, 'polegar_3': 0.15})
    anel(p['ip'], (1, 2), vezes(ip_sec, _BOJO_JUNTA), {'polegar_2': 0.5, 'polegar_3': 0.5})
    anel(p['ip'] + p['dirs'][2] * e, 2, ip_sec, {'polegar_2': 0.15, 'polegar_3': 0.85})
    ponta_t = comp3 + luva
    anel(p['ip'] + p['dirs'][2] * comp3 * 0.45, 2, polpa_sec, {'polegar_3': 1.0}, eip * 0.04)
    anel(p['ip'] + p['dirs'][2] * comp3 * 0.76, 2, vezes(polpa_sec, 0.9), {'polegar_3': 1.0}, eip * 0.08)
    k = 0.9 * _fator_cupula(comp3 * 0.93, comp3 * 0.76, ponta_t)
    ponta = anel(p['ip'] + p['dirs'][2] * comp3 * 0.93, 2, vezes(polpa_sec, k), {'polegar_3': 1.0}, eip * 0.12)
    _soltar_dentro_das_juntas(g, aneis)
    _reforco_da_ponta(g, mao, aneis)
    # Zonas: couro na metade palmar (de um lado ao outro) e na ponta; a tenar é couro inteira (a palma continua nela).
    for i, (a, b) in enumerate(zip(aneis[:-1], aneis[1:])):
        zonas = ['couro' if (i <= 1 or i >= 9 or 3 <= k2 <= 6) else 'tecido' for k2 in range(8)]
        g.faixa(a, b, zonas)
        g.costura(a[7], b[7])
    porta = aneis[0]
    for k2 in range(8):
        g.costura(porta[k2], porta[(k2 + 1) % 8])
    c = g.v(p['ip'] + p['dirs'][2] * ponta_t - p['normais'][2] * eip * 0.12, {'polegar_3': 1.0})
    g.estufar[c] = mao.f['luva']['couro']
    for k2 in (0, 2, 4, 6):
        g.face((ponta[k2], ponta[k2 + 1], ponta[(k2 + 2) % 8], c), 'couro')
    g.costura(ponta[7], ponta[0])
    g.costura(ponta[0], c)
    return aneis[1:] + [[c]]


# ---------------------------------------------------------------------------------------------- malha
ZONAS_BASE = ('couro', 'tecido')


def malha_base(mao, colecao, materiais, nome='luva_d', subdividir=1):
    """O objeto da luva direita (metros): a gaiola ajustada ao limite, com os grupos de vértices dos ossos, as zonas em
    materiais, as costuras marcadas e a subdivisão aplicada (`subdividir` níveis, os vértices na superfície limite).
    `materiais` = {zona: material}. Devolve (objeto, maior resíduo do ajuste em mm)."""
    g = gerar_gaiola(mao)
    bm = g.bm
    bm.normal_update()
    for v, mm in g.estufar.items():
        v.co += v.normal * mm
    residuo = ajustar_ao_limite(bm, g.livres)
    bmesh.ops.scale(bm, vec=(S, S, S), verts=bm.verts[:])
    for e in bm.edges:
        e.seam = frozenset(e.verts) in g.costuras
    idx_zona = {z: i for i, z in enumerate(ZONAS_BASE)}
    bm.verts.index_update()
    pesos = [(v.index, g.pesos[v]) for v in bm.verts]
    # Os dicionários da gaiola têm as faces como chave e uma camada nova invalida as referências a elas: tudo que é
    # lido deles vem antes, pela ordem das faces (que a camada não muda).
    faces = [(idx_zona[g.zonas[f]], int(f in g.forro)) for f in bm.faces]
    camada_forro = bm.faces.layers.int.new('forro')
    for f, (zona, forro) in zip(bm.faces, faces):
        f.material_index = zona
        f.smooth = True
        f[camada_forro] = forro
    me = bpy.data.meshes.new(nome)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(nome, me)
    colecao.objects.link(ob)
    for z in ZONAS_BASE:
        me.materials.append(materiais[z])
    grupos = {}
    for i, w in pesos:
        for osso, peso in w.items():
            if osso not in grupos:
                grupos[osso] = ob.vertex_groups.new(name=osso)
            grupos[osso].add([i], peso, 'REPLACE')
    if subdividir:
        m = ob.modifiers.new('subdividir', 'SUBSURF')
        m.levels = subdividir
        m.render_levels = subdividir
        m.use_limit_surface = True
        m.quality = 6
        m.uv_smooth = 'PRESERVE_BOUNDARIES'
        m.boundary_smooth = 'ALL'
        with bpy.context.temp_override(object=ob, active_object=ob):
            bpy.ops.object.modifier_apply(modifier=m.name)
    return ob, residuo
```

```python file=tools/blender/armas/maos_capsulas.py
# As cápsulas dos ossos da luva (Fase 4.1b; desenho em docs/superpowers/specs/2026-09-26-4.1b-luvas-e-empunhadura-
# design.md, seção 6.2): cada osso como o segmento dele com a seção medida na luva de repouso, para as contas rápidas de
# encosto da IK do polegar (empunhadura_polegar.py) — o contato que vale é sempre o da malha (maos_contato.py).
#  - a seção: em volta do osso, 16 setores no plano X–Z dele; em cada um, o percentil 80 da distância ao eixo dos
#    vértices do osso (os de que ele é o dono) no meio dele (entre 15 % e 85 % do comprimento, fora do bojo das juntas);
#    um setor vazio fica com a média dos vizinhos. O polegar e os dedos são achatados (o polegar tem 24 mm de largura
#    na unha e bem menos de espessura): com um raio redondo, pela mediana, o polegar deitado com a polpa num dedo
#    parecia entrar nele uns 3 mm;
#  - o encosto entre duas cápsulas: os pontos mais próximos dos segmentos e o raio de cada uma na direção da outra
#    (interpolado entre os centros dos setores).
# Unidades: mm; as matrizes dos ossos em metros no Blender.
import math

from mathutils import Vector

from .unidades import S

SETORES = 16
PERCENTIL = 0.8
MEIO = (0.15, 0.85)
_VOLTA = 2.0 * math.pi


def mm(m):
    """A matriz de um osso (metros) em mm."""
    r = m.copy()
    r.translation = m.translation / S
    return r


def _entre(x):
    return min(max(x, 0.0), 1.0)


def mais_proximos(p1, q1, p2, q2):
    """(s, t) dos pontos mais próximos dos segmentos p1–q1 e p2–q2: p1 + s·(q1 − p1) e p2 + t·(q2 − p2)."""
    d1, d2, r = q1 - p1, q2 - p2, p1 - p2
    a, e, f = d1.dot(d1), d2.dot(d2), d2.dot(r)
    if a < 1e-12 and e < 1e-12:
        return 0.0, 0.0
    if a < 1e-12:
        return 0.0, _entre(f / e)
    c = d1.dot(r)
    if e < 1e-12:
        return _entre(-c / a), 0.0
    b = d1.dot(d2)
    den = a * e - b * b
    s = _entre((b * f - c * e) / den) if den > 1e-12 else 0.0
    t = (b * s + f) / e
    if t < 0.0:
        return _entre(-c / a), 0.0
    if t > 1.0:
        return _entre((b - c) / a), 1.0
    return s, t


def _percentil(valores):
    v = sorted(valores)
    return v[min(len(v) - 1, int(PERCENTIL * (len(v) - 1) + 0.5))]


class Secoes:
    """Os raios por setor da seção de cada osso ({osso sem lado: [16 raios]}), medidos na luva de repouso."""

    def __init__(self, col):
        pts = col.modelo.pontos({})
        por_osso = {}
        for i, dono in enumerate(col.dono):
            por_osso.setdefault(dono, []).append(i)
        self.raios = {}
        for b in col.rig.data.bones:
            nome = b.name[:-2]
            if nome not in por_osso:
                continue
            para_local = mm(b.matrix_local).inverted()
            comp = b.length / S
            setores = [[] for _ in range(SETORES)]
            for i in por_osso[nome]:
                q = para_local @ pts[i]
                if not MEIO[0] * comp <= q.y <= MEIO[1] * comp:
                    continue
                k = int((math.atan2(q.z, q.x) % _VOLTA) / _VOLTA * SETORES) % SETORES
                setores[k].append(math.hypot(q.x, q.z))
            raios = [_percentil(s) if s else None for s in setores]
            if all(r is None for r in raios):
                continue
            while any(r is None for r in raios):
                raios = [r if r is not None else _media_dos_vizinhos(raios, k) for k, r in enumerate(raios)]
            self.raios[nome] = raios

    def raio(self, osso, direcao):
        """O raio da seção do osso na `direcao` (no referencial dele; a componente em Y não conta), interpolado entre
        os centros dos setores."""
        r = self.raios[osso]
        f = (math.atan2(direcao.z, direcao.x) % _VOLTA) / _VOLTA * SETORES - 0.5
        k = math.floor(f)
        w = f - k
        return r[k % SETORES] * (1.0 - w) + r[(k + 1) % SETORES] * w

    def maior(self, osso):
        return max(self.raios[osso])


def _media_dos_vizinhos(raios, k):
    vizinhos = [raios[(k + d) % SETORES] for d in (-1, 1) if raios[(k + d) % SETORES] is not None]
    return sum(vizinhos) / len(vizinhos) if vizinhos else None


class Capsula:
    """Um osso posado: o segmento (mm), a rotação para o referencial dele e o maior raio (para descartar longe)."""

    def __init__(self, secoes, osso, matriz, comprimento):
        self.osso = osso
        self.cabeca = matriz.translation.copy()
        self.cauda = matriz @ Vector((0.0, comprimento, 0.0))
        self.meio = (self.cabeca + self.cauda) / 2
        self.alcance = comprimento / 2 + secoes.maior(osso)
        self.para_local = matriz.to_3x3().inverted()


def encosto(secoes, a, b):
    """Quanto as cápsulas `a` e `b` entram uma na outra (mm; negativo é a folga entre elas)."""
    if (a.meio - b.meio).length > a.alcance + b.alcance:
        return -math.inf
    s, t = mais_proximos(a.cabeca, a.cauda, b.cabeca, b.cauda)
    pa = a.cabeca.lerp(a.cauda, s)
    pb = b.cabeca.lerp(b.cauda, t)
    d = pb - pa
    dist = d.length
    if dist < 1e-9:
        return secoes.maior(a.osso) + secoes.maior(b.osso)
    return secoes.raio(a.osso, a.para_local @ d) + secoes.raio(b.osso, b.para_local @ -d) - dist
```

Run: `node --test "tests/**/*.test.js"`
Expected: PASS — # tests 381 # pass 381 # fail 0 .

### Tarefa 4: Detalhes da luva (`maos_detalhes.py`) e materiais de fábrica

**Files:** Create `maos_detalhes.py`; Modify `materiais.py` (couro, tecido, borracha, com os três nós que o assar liga).

- [ ] **Passo 1: Detalhes do jogo** — protetor de borracha dos nós (os quatro domos ligados pela ponte, com a espessura
  da ficha), almofadas das falanges proximal e média (os quatro dedos), pontas reforçadas (a volta da unha até a polpa),
  reforço da palma (a borda saliente, do polegar ao mínimo), tira de velcro com o puxador no dorso do punho. Cada peça
  guarda a zona e fica encostada na malha base (sem vão nem sobra além de 0,2 mm).
- [ ] **Passo 2: Só no alto** — costuras (fileiras de pontos de 2,5 mm num sulco, nas bordas das peças e nos lados dos
  dedos), nervuras e respiros do protetor, rugas nas costas das juntas (deslocamento pela camada `t`), grão do couro,
  trama do tecido, textura antiderrapante da palma, gancho do velcro.
- [ ] **Passo 3: Materiais de fábrica** — `mat_couro`, `mat_tecido`, `mat_borracha` em `materiais.py`, no formato dos
  da 4.1a (aspereza, variação de cor, relevo).
- [ ] **Passo 4: `construir luvas` e as vistas**; **Passo 5: revisão crítica** contra as referências (a busca de
  2026-09-26: protetor com domos e ponte, dedos com segmentos acolchoados, tira de velcro larga com puxador; QGL3,
  QGL5).


**Código da tarefa** (a versão verificada no navegador e no Blender; os blocos `file=` são o arquivo inteiro, os pares são aplicados na ordem).

- [ ] **A implementação** — `tools/blender/armas/maos_detalhes.py`, `tools/blender/armas/maos_alto.py`, `tools/blender/armas/materiais.py`:

```python file=tools/blender/armas/maos_detalhes.py
# Detalhes da luva direita (Fase 4.1b; desenho em docs/superpowers/specs/2026-09-26-4.1b-luvas-e-empunhadura-design.md,
# seção 3.3; plano, Tarefa 4): as peças de jogo que fazem silhueta, cada uma assentada na malha base — o protetor de
# borracha moldada dos nós (um lóbulo com domo por nó, unidos pela ponte, tipo TPR), as almofadas de borracha nas costas
# das falanges proximal e média dos quatro dedos e a tira do punho com a borda saliente e o puxador. Os reforços de
# couro (a volta das pontas e a palma com a borda saliente) são a própria malha base estufada (maos_gaiola.py), sem
# triângulo a mais.
# Referências (moodboard, seção 15): luvas táticas com protetor de domos unidos e almofadas ovais nas falanges
# (QTG0–QTG3), o TPR moldado com um lóbulo por nó e guardas nas falanges (busca "mechanix m-pact glove knuckle"), a
# tira larga com o puxador no lado do mínimo (QTG1, QTG3).
# Cada peça é uma grade sobre a superfície: os pontos da base achados na malha base (raio de fora para dentro ou o
# ponto mais próximo), a face de cima a `altura` para fora pela normal suave dali, e as paredes descendo até 0,2 mm
# dentro da superfície (sem vão nem sobra); sem face de baixo, que ficaria escondida contra a luva. A quina entre o
# topo e a parede é marcada viva (a normal não se mistura).
import math

import bmesh
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

from .maos import DEDOS4
from .unidades import S

_DENTRO = 0.2  # a parede desce até 0,2 mm dentro da luva (mm)

# O protetor dos nós (mm). Contorno: a borda de trás a 24 mm da linha dos nós, sobre as costas da mão; na frente, um
# lóbulo elíptico por nó (meio eixo `lobulo` ao longo do dedo e de lado, centrado 1,5 mm além da MCP), e entre dois
# lóbulos a ponte para 3 mm antes dos nós — o vale onde a luva começa a descer para a dobra entre os dedos; dos lados,
# além do centro do mínimo e do indicador, com os cantos de trás arredondados (a borda de trás avança até `canto` mm
# nas pontas). Altura: a ponte e a borda (o chanfro em volta, em duas linhas da grade), e o domo de cada nó (meios
# eixos) com a altura da ficha (luva.protetor) no alto.
_PROTETOR = {'tras': -24.0, 'canto': 7.0, 'centro': 1.5, 'lobulo': (7.5, 10.8), 'vale': -3.0, 'lado_minimo': 9.5,
             'lado_indicador': 10.0, 'ponte': 3.0, 'borda': 0.8, 'chanfro': 2.0, 'domo': (8.0, 8.5),
             'colunas_do_domo': (-7.5, -4.5, -1.5, 1.5, 4.5, 7.5),
             # frações de trás para a frente do contorno, mais juntas perto dos domos
             'linhas': (0.0, 0.21, 0.42, 0.575, 0.68, 0.79, 0.9, 1.0)}
# As almofadas (mm e graus): o comprimento em fração da falange, a meia abertura em volta das costas, o expoente da
# superelipse do contorno (4: retângulo de cantos redondos), a borda e a cúpula (a altura no meio sobre a da ficha,
# luva.almofada, que vale no anel de dentro).
_ALMOFADA = {'comprimento': 0.55, 'abertura': 38.0, 'expoente': 4.0, 'borda': 0.6, 'cupula': 0.4}
# A tira do punho (mm e graus): o centro no punho, a volta (do lado do polegar, onde é costurada, até a ponta solta do
# lado do mínimo), a espessura nas bordas salientes, no meio (um pouco rebaixado) e no bisel de fora, e o puxador na
# ponta solta — uma aba mais estreita que vai levantando da luva. A largura é a da ficha (luva.tira).
_TIRA = {'centro': -22.0, 'de': 100.0, 'ate': -80.0, 'passos': 16, 'aba': 1.5,
         'espessura': {'bisel': 1.6, 'borda': 2.6, 'meio': 2.2},
         'puxador': {'comprimento': 14.0, 'largura': 16.0, 'espessura': 2.0, 'levanta': 1.2}}


def _suave(t):
    t = min(1.0, max(0.0, t))
    return t * t * (3.0 - 2.0 * t)


class Superficie:
    """A malha base (avaliada, em mm) numa BVH de triângulos, com as normais suaves interpoladas no ponto achado."""

    def __init__(self, ob):
        me = ob.data
        me.calc_loop_triangles()
        mw = ob.matrix_world
        self.co = [(mw @ v.co) / S for v in me.vertices]
        rot = mw.to_3x3().normalized()
        self.nv = [(rot @ v.normal).normalized() for v in me.vertices]
        self.tris = [tuple(t.vertices) for t in me.loop_triangles]
        self.bvh = BVHTree.FromPolygons(self.co, self.tris)

    def _normal(self, p, i):
        a, b, c = (self.co[k] for k in self.tris[i])
        v0, v1, v2 = b - a, c - a, p - a
        d00, d01, d11 = v0.dot(v0), v0.dot(v1), v1.dot(v1)
        d20, d21 = v2.dot(v0), v2.dot(v1)
        den = d00 * d11 - d01 * d01
        if abs(den) < 1e-12:
            return self.nv[self.tris[i][0]]
        w1 = (d11 * d20 - d01 * d21) / den
        w2 = (d00 * d21 - d01 * d20) / den
        w0 = 1.0 - w1 - w2
        na, nb, nc = (self.nv[k] for k in self.tris[i])
        return (na * w0 + nb * w1 + nc * w2).normalized()

    def raio(self, origem, direcao):
        """(ponto, normal) onde o raio encontra a malha."""
        p, _n, i, _d = self.bvh.ray_cast(origem, direcao)
        if p is None:
            raise ValueError(f'detalhe da luva: o raio de {tuple(round(c, 1) for c in origem)} não achou a malha')
        return p, self._normal(p, i)

    def perto(self, ponto):
        """(ponto, normal) mais perto na malha."""
        p, _n, i, _d = self.bvh.find_nearest(ponto)
        return p, self._normal(p, i)

    def distancia(self, ponto):
        """Distância (mm) do ponto à malha."""
        return self.bvh.find_nearest(ponto)[3]


def _peca(nome, grade, colecao, material, zona):
    """A peça a partir da grade de (ponto na superfície, normal, altura): a face de cima e as paredes da borda até
    _DENTRO dentro da superfície. `grade[i][j]`: i ao longo, j de lado; as faces saem para fora."""
    bm = bmesh.new()
    nu, nv = len(grade), len(grade[0])
    topo = [[bm.verts.new(p + n * h) for (p, n, h) in linha] for linha in grade]
    for i in range(nu - 1):
        for j in range(nv - 1):
            bm.faces.new((topo[i][j], topo[i + 1][j], topo[i + 1][j + 1], topo[i][j + 1]))
    borda = ([(0, j) for j in range(nv)] + [(i, nv - 1) for i in range(1, nu)] + [(nu - 1, j) for j in range(nv - 2, -1, -1)]
             + [(i, 0) for i in range(nu - 2, 0, -1)])
    base = {(i, j): bm.verts.new(grade[i][j][0] - grade[i][j][1] * _DENTRO) for i, j in borda}
    for k in range(len(borda)):
        a, b = borda[k], borda[(k + 1) % len(borda)]
        bm.faces.new((topo[a[0]][a[1]], base[a], base[b], topo[b[0]][b[1]]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    # recalc_face_normals decide pelo volume, e a peça é aberta embaixo: garante que o topo aponte para fora da luva.
    i0, j0 = nu // 2, nv // 2
    do_topo = {x for linha in topo for x in linha}
    f0 = next(f for f in topo[i0][j0].link_faces if all(v in do_topo for v in f.verts))
    if f0.normal.dot(grade[i0][j0][1]) < 0:
        bmesh.ops.reverse_faces(bm, faces=bm.faces[:])
    contorno = {topo[i][j] for i, j in borda}
    for e in bm.edges:
        e.smooth = not (e.verts[0] in contorno and e.verts[1] in contorno)
    bmesh.ops.scale(bm, vec=(S, S, S), verts=bm.verts[:])
    for f in bm.faces:
        f.smooth = True
    me = bpy.data.meshes.new(nome)
    bm.to_mesh(me)
    bm.free()
    me.materials.append(material)
    # `assento` = 1 na base das paredes (0,2 mm dentro da luva): a conta do assentamento continua possível depois de a
    # peça ser juntada à luva (maos_rig.pesos).
    at = me.attributes.new('assento', 'FLOAT', 'POINT')
    at.data.foreach_set('value', [0.0] * (nu * nv) + [1.0] * (len(me.vertices) - nu * nv))
    ob = bpy.data.objects.new(nome, me)
    ob['zona'] = zona
    ob['vertices_do_topo'] = nu * nv  # os de depois são a base das paredes, 0,2 mm dentro da luva
    colecao.objects.link(ob)
    return ob


def _chanfro(i, j, nu, nv, alcance):
    """0 no contorno da grade, 1 a partir de `alcance` linhas/colunas para dentro (em índices)."""
    d = min(i, j, nu - 1 - i, nv - 1 - j)
    return _suave(d / alcance)


# ---------------------------------------------------------------------------------------------- protetor
def _x_mcp_na_coluna(mao, y):
    """O x da linha dos nós na posição y (entre os centros dos dedos, linear; fora deles, o do dedo da ponta)."""
    pts = sorted((mao.y_no[d], mao.dedos[d]['mcp'].x) for d in DEDOS4)
    if y <= pts[0][0]:
        return pts[0][1]
    if y >= pts[-1][0]:
        return pts[-1][1]
    for (y0, x0), (y1, x1) in zip(pts[:-1], pts[1:]):
        if y0 <= y <= y1:
            return x0 + (x1 - x0) * (y - y0) / (y1 - y0)
    return pts[-1][1]


def protetor(mao, sup, colecao, material):
    """O protetor de borracha dos nós: a placa sobre a linha dos nós com um lóbulo por nó na frente, a ponte entre
    eles e o domo de cada um, da altura da ficha no alto. A grade acompanha os lóbulos: as colunas se juntam em cada
    domo e as linhas vão, coluna a coluna, da borda de trás até a frente do contorno ali."""
    P = _PROTETOR
    rxl, ryl = P['lobulo']
    rx, ry = P['domo']
    h_domo = mao.f['luva']['protetor']
    ordem = list(reversed(DEDOS4))  # do mínimo ao indicador (y crescente)
    cols = [mao.y_no['minimo'] - P['lado_minimo']]
    for k, d in enumerate(ordem):
        cols += [mao.y_no[d] + dy for dy in P['colunas_do_domo']]
        if k < 3:
            cols.append((mao.y_no[d] + mao.y_no[ordem[k + 1]]) / 2)
    cols.append(mao.y_no['indicador'] + P['lado_indicador'])

    def frente(y):
        t = P['vale']
        for d in DEDOS4:
            s = (y - mao.y_no[d]) / ryl
            if abs(s) < 1.0:
                t = max(t, P['centro'] + rxl * math.sqrt(1.0 - s * s))
        return t

    meio_y, meia_l = (cols[0] + cols[-1]) / 2, (cols[-1] - cols[0]) / 2

    def tras(y):
        u = abs(y - meio_y) / meia_l
        return P['tras'] + P['canto'] * max(0.0, (u - 0.7) / 0.3) ** 2

    nu, nv = len(P['linhas']), len(cols)
    grade = []
    for i, f in enumerate(P['linhas']):
        linha = []
        for j, y in enumerate(cols):
            dx = tras(y) + (frente(y) - tras(y)) * f
            x = _x_mcp_na_coluna(mao, y) + dx
            p, n = sup.raio(Vector((x, y, 60.0)), Vector((0.0, 0.0, -1.0)))
            h = P['ponte']
            for d in DEDOS4:
                u = (dx - P['centro']) / rx if d == _dedo_da_coluna(mao, y) else 9.0
                v = (y - mao.y_no[d]) / ry
                s = 1.0 - u * u - v * v
                if s > 0:
                    h = max(h, P['ponte'] + (h_domo - P['ponte']) * s ** 0.6)
            k = _chanfro(i, j, nu, nv, P['chanfro'])
            linha.append((p, n, P['borda'] + (h - P['borda']) * k))
        grade.append(linha)
    return _peca('luva_d_protetor', grade, colecao, material, 'reforco')


def _dedo_da_coluna(mao, y):
    """O dedo com o centro mais perto de y."""
    return min(DEDOS4, key=lambda d: abs(mao.y_no[d] - y))


# ---------------------------------------------------------------------------------------------- almofadas
def _secao_estimada(mao, d, seg, t):
    """(meia largura, meia espessura) aproximadas do dedo no ponto t (0..1) da falange `seg` (para achar a superfície
    pelo ponto mais próximo: basta cair perto dela)."""
    dd = mao.dedos[d]
    luva = mao.luva
    (lp, ep), (ld, ed) = dd['pip_sec'], dd['dip_sec']
    base = (dd['larg_no'], ep * 1.12)
    a, b = (base, (lp, ep)) if seg == 0 else ((lp, ep), (ld, ed))
    return (a[0] + (b[0] - a[0]) * t) / 2 + luva, (a[1] + (b[1] - a[1]) * t) / 2 + luva


def _superelipse(u, v, expoente):
    """O ponto (u, v) do quadrado [-1, 1]² levado para a superelipse de mesmo "raio" (os meios dos lados ficam, os
    cantos entram)."""
    m = max(abs(u), abs(v))
    if m < 1e-9:
        return u, v
    r = m / (abs(u) ** expoente + abs(v) ** expoente) ** (1.0 / expoente)
    return u * r, v * r


def almofadas(mao, sup, colecao, material):
    """As almofadas de borracha nas costas das falanges proximal e média dos quatro dedos: uma superelipse sobre o meio
    de cada falange, só nas costas, com a espessura da ficha no anel de dentro e a cúpula no meio."""
    A = _ALMOFADA
    h = mao.f['luva']['almofada']
    us = (-1.0, -0.55, 0.0, 0.55, 1.0)  # ao longo da falange
    vs = (-1.0, -0.36, 0.36, 1.0)  # em volta das costas
    pecas = []
    for d in DEDOS4:
        dd = mao.dedos[d]
        for seg, (a, b) in enumerate((('mcp', 'pip'), ('pip', 'dip'))):
            comp = (dd[b] - dd[a]).length
            frente, costas = dd['dirs'][seg], dd['normais'][seg]
            radial = costas.cross(frente).normalized()
            meio = (dd[a] + dd[b]) / 2
            meio_comp = A['comprimento'] * comp / 2
            grade = []
            for i, u0 in enumerate(us):
                linha = []
                for j, v0 in enumerate(vs):
                    u, v = _superelipse(u0, v0, A['expoente'])
                    ml, me_ = _secao_estimada(mao, d, seg, 0.5 + u * A['comprimento'] / 2)
                    th = math.radians(v * A['abertura'])
                    alvo = meio + frente * (u * meio_comp) + costas * (me_ * math.cos(th)) + radial * (ml * math.sin(th))
                    p, n = sup.perto(alvo)
                    k = _chanfro(i, j, len(us), len(vs), 1.0)
                    cupula = A['cupula'] * (1.0 - u * u) * (1.0 - v * v)
                    linha.append((p, n, A['borda'] + (h + cupula - A['borda']) * k))
                grade.append(linha)
            ob = _peca(f'luva_d_almofada_{d}_{seg + 1}', grade, colecao, material, 'reforco')
            # O referencial da almofada, para as nervuras do modelo alto (maos_alto.py).
            ob['centro'], ob['frente'], ob['meio_comp'] = list(meio), list(frente), meio_comp
            pecas.append(ob)
    return pecas


# ---------------------------------------------------------------------------------------------- tira do punho
def tira(mao, sup, colecao, material):
    """A tira do punho (a largura da ficha, luva.tira): costurada do lado do polegar, passando pelas costas e fechando
    do lado do mínimo, onde a ponta solta tem o puxador (uma aba mais estreita que levanta da luva). De lado a lado: o
    bisel, a borda saliente, o meio um pouco rebaixado, a borda e o bisel."""
    T = _TIRA
    E = T['espessura']
    meia = mao.f['luva']['tira'] / 2
    c = T['centro']
    xs = (c - meia, c - meia + T['aba'], c, c + meia - T['aba'], c + meia)
    hs = (E['bisel'], E['borda'], E['meio'], E['borda'], E['bisel'])

    def na_volta(x, graus):
        th = math.radians(graus)
        direcao = Vector((0.0, math.sin(th), math.cos(th)))
        return sup.raio(Vector((x, 0.0, 0.0)) + direcao * 90.0, -direcao)

    grade = []
    for k in range(T['passos'] + 1):
        graus = T['de'] + (T['ate'] - T['de']) * k / T['passos']
        linha = []
        for x, hh in zip(xs, hs):
            p, n = na_volta(x, graus)
            # nas duas pontas da volta, o bisel também (a ponta costurada e a solta)
            linha.append((p, n, E['bisel'] if k in (0, T['passos']) else hh))
        grade.append(linha)
    pecas = [_peca('luva_d_tira', grade, colecao, material, 'reforco')]
    # O puxador: continua a volta além da ponta solta, mais estreito, e vai levantando da luva.
    X = T['puxador']
    raio_medio = sum((p.yz.length for p, _n, _h in grade[-1]), 0.0) / len(grade[-1])
    passo_graus = math.degrees(X['comprimento'] / raio_medio) / 2
    xs_p = (c - X['largura'] / 2, c, c + X['largura'] / 2)
    grade_p = []
    for k in range(3):
        graus = T['ate'] - passo_graus * k + (passo_graus * 0.35 if k == 0 else 0.0)
        linha = []
        for j, x in enumerate(xs_p):
            p, n = na_volta(x, graus)
            linha.append((p, n, X['espessura'] + X['levanta'] * k / 2 - (0.4 if j != 1 else 0.0)))
        grade_p.append(linha)
    pecas.append(_peca('luva_d_puxador', grade_p, colecao, material, 'reforco'))
    return pecas


def construir(mao, luva, colecao, material):
    """As peças de jogo da luva direita sobre a malha base `luva` (o objeto subdividido). Devolve (peças, o maior
    desvio em mm da base das paredes em relação aos 0,2 mm dentro da luva: o assentamento)."""
    sup = Superficie(luva)
    pecas = [protetor(mao, sup, colecao, material)]
    pecas += almofadas(mao, sup, colecao, material)
    pecas += tira(mao, sup, colecao, material)
    folga = 0.0
    for ob in pecas:
        mw = ob.matrix_world
        base = [(mw @ v.co) / S for v in ob.data.vertices[ob['vertices_do_topo']:]]
        folga = max(folga, max(abs(sup.distancia(p) - _DENTRO) for p in base))
    return pecas, folga
```

```python file=tools/blender/armas/maos_alto.py
# Modelo alto da luva direita (Fase 4.1b; desenho em docs/superpowers/specs/2026-09-26-4.1b-luvas-e-empunhadura-design.md,
# seção 3.3; plano, Tarefa 4, Passo 2): a fonte do assar — o que vira relevo e máscaras nas texturas da luva de jogo.
#  - A base: a mesma gaiola ajustada ao limite, subdividida 4 níveis (a mesma superfície da de jogo, com vértices a
#    0,2–1,2 mm), com as rugas do tecido nas costas das juntas dos dedos e do polegar e no pulso, em deslocamento de
#    verdade.
#  - As costuras: as linhas onde os painéis se juntam (as costuras das UV e as fronteiras entre as zonas, que a
#    subdivisão leva da gaiola) viram atributos por vértice — `costura_d` (a distância à linha, mm) e `costura_s` (o
#    comprimento ao longo dela, mm), com `costura_ok` = 1 — e o relevo dos materiais (materiais.py) desenha o sulco na
#    linha e a fileira de pontos de 2,5 mm de cada lado, nítidos no pixel do assar. As peças levam a costura no
#    contorno (a linha é a borda delas).
#  - As máscaras dos padrões finos dos materiais: `antiderrapante` (o painel de reforço da palma, entre a primeira
#    estação e a da dobra do polegar), `velcro` (o puxador da tira) e `tira` (as nervuras moldadas da tira).
#  - As peças: as de jogo com a quina de cima vincada e subdivididas; os respiros (duas fendas por domo) e as nervuras
#    da ponte no protetor; três nervuras em cada almofada.
# Referências (moodboard, seção 15): QTG0–QTG3 e as fotos do TPR moldado (M-Pact) — costuras duplas nas bordas dos
# painéis, fendas nos domos, nervuras nas guardas dos dedos.
import math

import bmesh
import bpy
import numpy as np
from mathutils import Vector
from mathutils.kdtree import KDTree

from . import maos_gaiola
from .maos import DEDOS4
from .unidades import S

NIVEL_BASE = 4
_PASSO_AMOSTRA = 0.2  # mm entre as amostras das linhas de costura
# As rugas do tecido (mm): amplitude, período ao longo do dedo e a largura da faixa do pulso.
_RUGAS = {'amplitude': 0.22, 'periodo': 2.4, 'pulso': (-6.0, 7.0), 'amplitude_pulso': 0.16, 'periodo_pulso': 3.2}
# O protetor (mm): as fendas de cada domo (meio comprimento ao longo do dedo, meia largura, a distância entre as duas,
# a profundidade) e as nervuras da ponte (x a partir da linha dos nós, meia largura, altura).
_RESPIRO = {'meio_comp': 3.0, 'meia_larg': 0.85, 'afastamento': 2.6, 'fundo': 1.0, 'suave': 0.3}
_NERVURAS_PONTE = {'xs': (-19.0, -15.0, -11.0), 'meia_larg': 0.6, 'altura': 0.45}
# As almofadas: as nervuras (posições em fração do meio comprimento, meia largura e altura, mm).
_NERVURAS_ALMOFADA = {'us': (-0.45, 0.0, 0.45), 'meia_larg': 0.55, 'altura': 0.35}


def _suave(t):
    t = min(1.0, max(0.0, t))
    return t * t * (3.0 - 2.0 * t)


def _atributo(me, nome, valores):
    at = me.attributes.get(nome) or me.attributes.new(nome, 'FLOAT', 'POINT')
    at.data.foreach_set('value', valores)


# ---------------------------------------------------------------------------------------------- linhas de costura
def _cadeias(pares):
    """As arestas (pares de índices) encadeadas em linhas: de ponta a ponta (vértices de grau ≠ 2) e os laços."""
    viz = {}
    for a, b in pares:
        viz.setdefault(a, []).append(b)
        viz.setdefault(b, []).append(a)
    usadas = set()
    cadeias = []

    def andar(inicio, prox):
        cadeia = [inicio, prox]
        usadas.add(frozenset((inicio, prox)))
        atual, antes = prox, inicio
        while len(viz[atual]) == 2:
            seguinte = viz[atual][0] if viz[atual][0] != antes else viz[atual][1]
            chave = frozenset((atual, seguinte))
            if chave in usadas:
                break
            usadas.add(chave)
            cadeia.append(seguinte)
            antes, atual = atual, seguinte
        return cadeia

    for v, vs in viz.items():
        if len(vs) != 2:
            for u in vs:
                if frozenset((v, u)) not in usadas:
                    cadeias.append(andar(v, u))
    for v, vs in viz.items():
        for u in vs:
            if frozenset((v, u)) not in usadas:
                cadeias.append(andar(v, u))
    return cadeias


def _amostras(pontos_das_cadeias):
    """KDTree das amostras (a cada _PASSO_AMOSTRA mm) das linhas, com o comprimento ao longo de cada uma."""
    amostras, ss = [], []
    for pts in pontos_das_cadeias:
        s = 0.0
        for a, b in zip(pts[:-1], pts[1:]):
            comp = (b - a).length
            n = max(1, int(math.ceil(comp / _PASSO_AMOSTRA)))
            for k in range(n):
                amostras.append(a.lerp(b, k / n))
                ss.append(s + comp * k / n)
            s += comp
        amostras.append(pts[-1])
        ss.append(s)
    kd = KDTree(len(amostras))
    for i, p in enumerate(amostras):
        kd.insert(p, i)
    kd.balance()
    return kd, ss


def _gravar_costura(ob, kd, ss):
    """Os atributos da costura nos vértices do objeto (mm, no referencial do mundo)."""
    me = ob.data
    mw = ob.matrix_world
    ds, sv = [], []
    for v in me.vertices:
        _co, i, dist = kd.find((mw @ v.co) / S)
        ds.append(dist)
        sv.append(ss[i])
    _atributo(me, 'costura_d', ds)
    _atributo(me, 'costura_s', sv)
    _atributo(me, 'costura_ok', [1.0] * len(me.vertices))


def costuras_da_base(ob):
    """As linhas de costura da base alta: as arestas marcadas como costura (as das UV, que a subdivisão leva da gaiola)
    e as fronteiras entre faces de zonas diferentes."""
    me = ob.data
    mw = ob.matrix_world
    zona_da_aresta = {}
    for p in me.polygons:
        for k in p.edge_keys:
            zona_da_aresta.setdefault(k, set()).add(p.material_index)
    pares = [tuple(e.vertices) for e in me.edges if e.use_seam or len(zona_da_aresta.get(e.key, ())) > 1]
    pts = [(mw @ v.co) / S for v in me.vertices]
    return [[pts[i] for i in c] for c in _cadeias(pares)]


# ---------------------------------------------------------------------------------------------- rugas e máscaras
def _pesos(ob):
    """[{osso: peso}] por vértice."""
    nomes = {g.index: g.name for g in ob.vertex_groups}
    return [{nomes[e.group]: e.weight for e in v.groups} for v in ob.data.vertices]


def _vertices_da_zona(me, zona):
    """Máscara (numpy, por vértice) dos vértices de alguma face da zona."""
    idx = maos_gaiola.ZONAS_BASE.index(zona)
    mats = np.empty(len(me.polygons), np.int32)
    me.polygons.foreach_get('material_index', mats)
    inicio = np.empty(len(me.polygons), np.int32)
    me.polygons.foreach_get('loop_start', inicio)
    total = np.empty(len(me.polygons), np.int32)
    me.polygons.foreach_get('loop_total', total)
    loops = np.empty(len(me.loops), np.int32)
    me.loops.foreach_get('vertex_index', loops)
    mask = np.zeros(len(me.vertices), bool)
    faces = np.nonzero(mats == idx)[0]
    for k in range(4):
        sel = faces[total[faces] > k]
        mask[loops[inicio[sel] + k]] = True
    return mask


def rugas(ob, mao):
    """As rugas do tecido: ondas de través nas costas de cada junta dos dedos (PIP e DIP) e do polegar (MCP e IP), num
    envelope de 3,5 mm em volta do centro da junta e só perto do eixo daquele dedo, e em volta do pulso, nas costas.
    Só no tecido (couro e reforços não enrugam assim). Em numpy, sobre todos os vértices de uma vez."""
    R = _RUGAS
    me = ob.data
    n_v = len(me.vertices)
    co = np.empty(n_v * 3)
    me.vertices.foreach_get('co', co)
    co = co.reshape(-1, 3) / S
    nor = np.empty(n_v * 3)
    me.vertices.foreach_get('normal', nor)
    nor = nor.reshape(-1, 3)
    tecido = _vertices_da_zona(me, 'tecido')
    juntas = []
    for d in DEDOS4:
        dd = mao.dedos[d]
        (lp, ep), (ld, ed) = dd['pip_sec'], dd['dip_sec']
        juntas.append((dd['pip'], dd['dirs'][0] + dd['dirs'][1], dd['normais'][0] + dd['normais'][1], max(lp, ep) / 2))
        juntas.append((dd['dip'], dd['dirs'][1] + dd['dirs'][2], dd['normais'][1] + dd['normais'][2], max(ld, ed) / 2))
    p = mao.polegar
    lip, eip = p['ip_sec']
    juntas.append((p['mcp'], p['dirs'][0] + p['dirs'][1], p['normais'][0] + p['normais'][1], max(lip, eip) * 0.6))
    juntas.append((p['ip'], p['dirs'][1] + p['dirs'][2], p['normais'][1] + p['normais'][2], max(lip, eip) / 2))
    h = np.zeros(n_v)
    for ponto, frente, costas, raio in juntas:
        f = np.array(frente.normalized())
        c = np.array(costas.normalized())
        rel = co - np.array(ponto)
        t_ax = rel @ f
        lado = rel @ np.cross(c, f)
        radial = np.linalg.norm(rel - np.outer(t_ax, f), axis=1)
        costas_n = np.clip(nor @ c, 0.0, 1.0)
        env = np.exp(-(t_ax / 3.5) ** 2) * (radial < raio + mao.luva + 1.5)
        h += R['amplitude'] * env * costas_n ** 2 * np.sin(2 * np.pi * t_ax / R['periodo'] + 0.35 * np.sin(lado / 3.0))
    x0, x1 = R['pulso']
    no_pulso = (co[:, 0] > x0) & (co[:, 0] < x1) & (nor[:, 2] > 0.2)
    env = np.where(no_pulso, np.sin(np.pi * np.clip((co[:, 0] - x0) / (x1 - x0), 0, 1)) * nor[:, 2], 0.0)
    h += R['amplitude_pulso'] * env * np.sin(2 * np.pi * co[:, 0] / R['periodo_pulso'] + 0.5 * np.sin(co[:, 1] / 6.0))
    h *= tecido
    co += nor * h[:, None]
    me.vertices.foreach_set('co', (co * S).ravel())
    me.update()


def mascara_antiderrapante(ob, mao):
    """1 no painel de reforço da palma (a palma entre a primeira estação e a da dobra do polegar, fora dos dedos e do
    polegar), com a borda suave de 1,5 mm."""
    me = ob.data
    mw = ob.matrix_world
    couro = maos_gaiola.ZONAS_BASE.index('couro')
    no_couro = set()
    for p in me.polygons:
        if p.material_index == couro:
            no_couro.update(p.vertices)
    pesos = _pesos(ob)
    x0, x1 = maos_gaiola._PALMA[0][0], maos_gaiola._PALMA[2][0]
    valores = []
    for i, v in enumerate(me.vertices):
        co = (mw @ v.co) / S
        w = pesos[i]
        dedos = sum(p for o, p in w.items() if o.rsplit('_', 1)[0] in DEDOS4 and not o.endswith('_0'))
        pol = sum(p for o, p in w.items() if o.startswith('polegar_') and o != 'polegar_1')
        if i in no_couro and dedos < 0.3 and pol < 0.3 and co.z < 0:
            valores.append(_suave((co.x - x0) / 1.5) * _suave((x1 - co.x) / 1.5))
        else:
            valores.append(0.0)
    _atributo(me, 'antiderrapante', valores)


# ---------------------------------------------------------------------------------------------- peças
def _peca_alta(ob_jogo, colecao, nivel):
    """A peça de jogo copiada, com a quina de cima vincada (o contorno do topo), subdividida `nivel` níveis na superfície
    limite. Devolve o objeto e o índice dos vértices do contorno do topo (para a linha de costura)."""
    me = ob_jogo.data.copy()
    ob = bpy.data.objects.new(ob_jogo.name + '_alto', me)
    for k in ('zona', 'centro', 'frente', 'meio_comp'):
        if k in ob_jogo:
            ob[k] = ob_jogo[k]
    colecao.objects.link(ob)
    n_topo = ob_jogo['vertices_do_topo']
    bm = bmesh.new()
    bm.from_mesh(me)
    bm.verts.ensure_lookup_table()
    base = {v for v in bm.verts if v.index >= n_topo}
    contorno = {v for v in bm.verts if v.index < n_topo and any(e.other_vert(v) in base for e in v.link_edges)}
    vinco = bm.edges.layers.float.get('crease_edge') or bm.edges.layers.float.new('crease_edge')
    for e in bm.edges:
        if e.verts[0] in contorno and e.verts[1] in contorno:
            e[vinco] = 0.75
        elif e.verts[0] in base and e.verts[1] in base:
            e[vinco] = 1.0
    bm.to_mesh(me)
    bm.free()
    m = ob.modifiers.new('subdividir', 'SUBSURF')
    m.levels = m.render_levels = nivel
    m.use_limit_surface = True
    m.quality = 6
    m.boundary_smooth = 'ALL'
    m.use_creases = True
    with bpy.context.temp_override(object=ob, active_object=ob):
        bpy.ops.object.modifier_apply(modifier=m.name)
    return ob


def _contorno_do_topo(ob_jogo):
    """A quina de cima da peça de jogo (os vértices do topo que tocam a base das paredes), encadeada em linha, em mm: a
    linha da costura do contorno (a peça alta arredonda a quina a menos de 0,3 mm dela)."""
    me = ob_jogo.data
    mw = ob_jogo.matrix_world
    n_topo = ob_jogo['vertices_do_topo']
    contorno = set()
    for e in me.edges:
        a, b = e.vertices
        if (a < n_topo) != (b < n_topo):
            contorno.add(a if a < n_topo else b)
    pares = [tuple(e.vertices) for e in me.edges if e.vertices[0] in contorno and e.vertices[1] in contorno]
    pts = [(mw @ v.co) / S for v in me.vertices]
    return [[pts[i] for i in c] for c in _cadeias(pares)]


def _deslocar_topo(ob, sup, altura_em):
    """Desloca os vértices do topo da peça (os virados para fora da luva, acima da borda) pela normal da luva embaixo
    deles: `altura_em(p)` em mm (negativa afunda). A normal da luva é a mesma para os vértices vizinhos; a do próprio
    vértice gira nas paredes de uma fenda e amassava a malha."""
    me = ob.data
    mw = ob.matrix_world
    rot = mw.to_3x3().normalized()
    inv = rot.inverted()
    novos = []
    for v in me.vertices:
        p = (mw @ v.co) / S
        _q, n_sup = sup.perto(p)
        n = (rot @ v.normal).normalized()
        if n.dot(n_sup) < 0.6 or sup.distancia(p) < 0.6:
            continue
        h = altura_em(p)
        if h:
            novos.append((v, inv @ (n_sup * (h * S))))
    for v, d in novos:
        v.co += d


def _faixa(d, meia, suave=0.25):
    """1 dentro de |d| < meia, 0 fora, com a transição de `suave` mm."""
    return _suave((meia + suave - abs(d)) / (2 * suave))


def protetor_alto(ob_jogo, mao, sup, colecao):
    # Nível 4: as fendas dos domos têm 1,7 mm de largura (vértices a ~0,2 mm; no nível 3 a borda delas serrilhava).
    ob = _peca_alta(ob_jogo, colecao, 4)
    Rp, N = _RESPIRO, _NERVURAS_PONTE

    def x_mcp(y):
        pts = sorted((mao.y_no[d], mao.dedos[d]['mcp'].x) for d in DEDOS4)
        if y <= pts[0][0]:
            return pts[0][1]
        if y >= pts[-1][0]:
            return pts[-1][1]
        for (y0, x0), (y1, x1) in zip(pts[:-1], pts[1:]):
            if y0 <= y <= y1:
                return x0 + (x1 - x0) * (y - y0) / (y1 - y0)
        return pts[-1][1]

    y_min, y_max = mao.y_no['minimo'] - 5.0, mao.y_no['indicador'] + 5.0

    def altura(p):
        fenda = 0.0
        for d in DEDOS4:
            cx, cy = mao.dedos[d]['mcp'].x + 1.5, mao.y_no[d]
            for lado in (-1, 1):
                dy = p.y - (cy + lado * Rp['afastamento'])
                dx = max(0.0, abs(p.x - cx) - (Rp['meio_comp'] - Rp['meia_larg']))
                fenda = max(fenda, _faixa(math.hypot(dx, dy), Rp['meia_larg'], Rp['suave']))
        nervura = 0.0
        if y_min < p.y < y_max:
            dx = p.x - x_mcp(p.y)
            nervura = max(_faixa(dx - xn, N['meia_larg'], 0.25) for xn in N['xs'])
        return N['altura'] * nervura - Rp['fundo'] * fenda

    _deslocar_topo(ob, sup, altura)
    return ob


def almofada_alta(ob_jogo, sup, colecao):
    ob = _peca_alta(ob_jogo, colecao, 3)
    Na = _NERVURAS_ALMOFADA
    centro, frente, meio = Vector(ob['centro']), Vector(ob['frente']), ob['meio_comp']

    def altura(p):
        t = (p - centro).dot(frente) / meio
        return max(Na['altura'] * _faixa((t - u) * meio, Na['meia_larg'], 0.25) for u in Na['us'])

    _deslocar_topo(ob, sup, altura)
    return ob


def construir(mao, materiais, pecas_jogo, colecao, etapa=lambda nome: None):
    """O modelo alto da luva direita na coleção `colecao`: a base (nível 4, rugas, costuras e máscaras) e as peças
    altas (com as costuras no contorno). `materiais` = {zona: material}; `pecas_jogo` = as peças de maos_detalhes.
    Devolve a lista dos objetos."""
    base, _ = maos_gaiola.malha_base(mao, colecao, {z: materiais[z] for z in maos_gaiola.ZONAS_BASE}, 'luva_d_alto',
                                     subdividir=NIVEL_BASE)
    etapa('alto: base no nível 4')
    kd, ss = _amostras(costuras_da_base(base))
    _gravar_costura(base, kd, ss)
    etapa('alto: costuras da base')
    mascara_antiderrapante(base, mao)
    _atributo(base.data, 'velcro', [0.0] * len(base.data.vertices))
    _atributo(base.data, 'tira', [0.0] * len(base.data.vertices))
    etapa('alto: máscaras')
    rugas(base, mao)
    etapa('alto: rugas')
    from .maos_detalhes import Superficie
    sup = Superficie(base)
    altos = [base]
    for ob_jogo in pecas_jogo:
        nome = ob_jogo.name
        if nome.endswith('_protetor'):
            ob = protetor_alto(ob_jogo, mao, sup, colecao)
        elif '_almofada_' in nome:
            ob = almofada_alta(ob_jogo, sup, colecao)
        else:
            ob = _peca_alta(ob_jogo, colecao, 2)
        kd_p, ss_p = _amostras(_contorno_do_topo(ob_jogo))
        _gravar_costura(ob, kd_p, ss_p)
        _atributo(ob.data, 'antiderrapante', [0.0] * len(ob.data.vertices))
        _atributo(ob.data, 'velcro', [1.0 if nome.endswith('_puxador') else 0.0] * len(ob.data.vertices))
        _atributo(ob.data, 'tira', [1.0 if nome.endswith('_tira') else 0.0] * len(ob.data.vertices))
        ob.data.materials.clear()
        ob.data.materials.append(materiais[ob['zona']])
        altos.append(ob)
    etapa('alto: peças')
    return altos
```

Em `tools/blender/armas/materiais.py`, trocar:

```
# Materiais de fábrica procedurais das armas realistas (Fase 4.1a; desenho, seções 4.1 e 4.4; vêm da prova de conceito):
# aço oxidado, aço polido, madeira envernizada, polímero/baquelite com ou sem quadriculado. Servem ao modelo alto — as
# renders da conferência e o assar. Cada um tem três nós nomeados, lidos pelo assar.py:
#   canal_aspereza — variação de aspereza em torno de 0,5 (vira _m.g)
```

por:

```
# Materiais de fábrica procedurais das armas realistas (Fase 4.1a; desenho, seções 4.1 e 4.4; vêm da prova de conceito):
# aço oxidado, aço polido, madeira envernizada, polímero/baquelite com ou sem quadriculado; e os das luvas (Fase 4.1b;
# desenho da 4.1b, seção 3.4): couro sintético, tecido elástico e borracha moldada. Servem ao modelo alto — as renders
# da conferência e o assar. Cada um tem três nós nomeados, lidos pelo assar.py:
#   canal_aspereza — variação de aspereza em torno de 0,5 (vira _m.g)
```

Em `tools/blender/armas/materiais.py`, trocar:

```

def materiais_de_fabrica(fabrica):
```

por:

```

def escala_da_onda(periodo_mm):
    """Escala do nó Wave (bandas ao longo de um eixo) para o período dado: o Blender faz sen(20·escala·coordenada), então
    a onda repete a cada 2π/(20·escala) na coordenada (metros)."""
    return 2 * math.pi / (20.0 * periodo_mm * S)


def _relevo(n, l, altura, forca, distancia_mm, normal_de_baixo, fino=False):
    """Nó Bump sobre a normal arredondada da borda: `altura` (0–1) com a força e a distância (mm) dadas. `fino`: um
    relevo menor do que a textura assada guarda (período abaixo de uns 8 texels) — fica nas renders do modelo alto e
    sai do assar (assar.assar_grupos desliga os nós `fino`); no jogo ele vem do shader, procedural."""
    bp = n.new('ShaderNodeBump')
    if fino:
        bp.label = 'fino'
    bp.inputs['Strength'].default_value = forca
    bp.inputs['Distance'].default_value = distancia_mm * S
    l.new(altura, bp.inputs['Height'])
    l.new(normal_de_baixo, bp.inputs['Normal'])
    return bp.outputs['Normal']


def _no_atributo(n, nome):
    """A saída de um atributo de geometria do modelo alto (0 onde a malha não tem o atributo: a de jogo)."""
    a = n.new('ShaderNodeAttribute')
    a.attribute_type = 'GEOMETRY'
    a.attribute_name = nome
    return a.outputs['Fac']


def _conta(n, l, op, a, b=None, c=None):
    """Nó Math `op` com as entradas (números ou saídas); devolve a saída."""
    no = n.new('ShaderNodeMath')
    no.operation = op
    for i, x in enumerate((a, b, c)):
        if x is None:
            continue
        if isinstance(x, (int, float)):
            no.inputs[i].default_value = x
        else:
            l.new(x, no.inputs[i])
    return no.outputs['Value']


def _degrau(n, l, x, de, ate):
    """smoothstep(de, ate, x) pelo Map Range."""
    mr = n.new('ShaderNodeMapRange')
    mr.interpolation_type = 'SMOOTHSTEP'
    mr.inputs['From Min'].default_value = de
    mr.inputs['From Max'].default_value = ate
    l.new(x, mr.inputs['Value'])
    return mr.outputs['Result']


def _gauss(n, l, x, centro, sigma):
    """exp(-((x - centro)/sigma)²)."""
    q = _conta(n, l, 'DIVIDE', _conta(n, l, 'SUBTRACT', x, centro), sigma)
    return _conta(n, l, 'EXPONENT', _conta(n, l, 'MULTIPLY', _conta(n, l, 'MULTIPLY', q, q), -1.0))


def costura(n, l):
    """O sulco e os pontos das costuras pelos atributos do modelo alto (maos_alto.py): `costura_d` (a distância à linha,
    mm), `costura_s` (o comprimento ao longo dela, mm) e `costura_ok` (1 no modelo alto). O sulco na linha (0,45 mm de
    meia largura) e uma fileira de pontos de cada lado a 1 mm, com o passo de 2,5 mm e o fio de 1,6 mm. Devolve (altura
    em 0–1 com 0,5 neutro, o sulco já multiplicado por `costura_ok`)."""
    d = _no_atributo(n, 'costura_d')
    s = _no_atributo(n, 'costura_s')
    ok = _no_atributo(n, 'costura_ok')
    sulco = _conta(n, l, 'MULTIPLY', _gauss(n, l, d, 0.0, 0.45), ok)
    fileira = _gauss(n, l, d, 1.0, 0.22)
    fase = _conta(n, l, 'FRACT', _conta(n, l, 'DIVIDE', s, 2.5))
    liga = _conta(n, l, 'MULTIPLY', _degrau(n, l, fase, 0.04, 0.12),
                  _conta(n, l, 'SUBTRACT', 1.0, _degrau(n, l, fase, 0.64, 0.72)))
    pontos = _conta(n, l, 'MULTIPLY', _conta(n, l, 'MULTIPLY', fileira, liga), ok)
    altura = _conta(n, l, 'ADD', _conta(n, l, 'SUBTRACT', _conta(n, l, 'MULTIPLY', pontos, 0.35),
                                          _conta(n, l, 'MULTIPLY', sulco, 0.45)), 0.5)
    return altura, sulco


def _pontinhos(n, l, periodo_mm, raio, plano=False):
    """Pontinhos em cúpula numa grade regular (Voronoi F1 sem aleatoriedade: a distância ao centro da célula), com o
    raio em fração do período: 1 no alto, 0 fora. `plano`: a grade no plano XY do objeto, projetada de baixo (a
    palma olha para -Z); a grade em 3D, fatiada por uma superfície curva, deixava faixas sem pontinho."""
    tc = n.new('ShaderNodeTexCoord')
    vor = n.new('ShaderNodeTexVoronoi')
    if plano:
        vor.voronoi_dimensions = '2D'
    vor.feature = 'F1'
    vor.inputs['Scale'].default_value = 1.0 / (periodo_mm * S)
    vor.inputs['Randomness'].default_value = 0.0
    l.new(tc.outputs['Object'], vor.inputs['Vector'])
    q = _conta(n, l, 'DIVIDE', sock(vor.outputs, 'Distance', 'VALUE'), raio)
    return _conta(n, l, 'MAXIMUM', _conta(n, l, 'SUBTRACT', 1.0, _conta(n, l, 'MULTIPLY', q, q)), 0.0)


def _escurecer_no_sulco(n, l, cor_saida, sulco):
    """A cor escurecida no sulco da costura (a sujeira que junta ali)."""
    return mistura_cor(n, l, _conta(n, l, 'MULTIPLY', sulco, 0.45), cor_saida, (0.0, 0.0, 0.0))


def mat_couro(nome, cor):
    """Couro sintético da palma e das pontas (tipo camurça sintética de luva tática): grão de poros de ~0,7 mm, manchas
    leves de tingimento, aspereza média com brilho leve."""
    m, n, l, b = novo_mat(nome)
    tc = n.new('ShaderNodeTexCoord')
    vor = n.new('ShaderNodeTexVoronoi')
    vor.feature = 'F1'
    vor.inputs['Scale'].default_value = 1.0 / (0.7 * S)
    vor.inputs['Randomness'].default_value = 0.9
    l.new(tc.outputs['Object'], vor.inputs['Vector'])
    fino = ruido_mm(n, l, 0.35, 2.0)
    grao = n.new('ShaderNodeMath')
    grao.operation = 'MULTIPLY_ADD'
    l.new(sock(vor.outputs, 'Distance', 'VALUE'), grao.inputs[0])
    grao.inputs[1].default_value = 0.8
    l.new(fino.outputs['Fac'], grao.inputs[2])
    mancha = ruido_mm(n, l, 18.0, 3.0)
    alt_costura, sulco = costura(n, l)
    base_cor = mistura_cor(n, l, faixa(n, l, mancha.outputs['Fac'], 0.0, 0.3), cor, tuple(c * 0.82 for c in cor))
    l.new(_escurecer_no_sulco(n, l, base_cor, sulco), b.inputs['Base Color'])
    asp = ruido_mm(n, l, 4.0)
    l.new(faixa(n, l, asp.outputs['Fac'], 0.49, 0.61), b.inputs['Roughness'])
    b.inputs['Sheen Weight'].default_value = 0.15
    bev, borda_m = mascara_borda(n, l, 0.8)
    normal = _relevo(n, l, grao.outputs['Value'], 0.3, 0.12, bev.outputs['Normal'], fino=True)
    # O painel de reforço da palma: pontinhos antiderrapantes de 0,3 mm num passo de 1,4 mm.
    anti = _conta(n, l, 'MULTIPLY', _pontinhos(n, l, 1.4, 0.3, plano=True), _no_atributo(n, 'antiderrapante'))
    normal = _relevo(n, l, anti, 0.8, 0.25, normal)
    l.new(_relevo(n, l, alt_costura, 1.0, 0.35, normal), b.inputs['Normal'])
    canal(n, l, 'canal_aspereza', asp.outputs['Fac'])
    canal(n, l, 'canal_cor', _conta(n, l, 'MULTIPLY', mancha.outputs['Fac'], _conta(n, l, 'SUBTRACT', 1.0,
                                                                                   _conta(n, l, 'MULTIPLY', sulco, 0.6))))
    canal(n, l, 'canal_borda', borda_m.outputs['Result'])
    return m


def mat_tecido(nome, cor):
    """Tecido elástico das costas e dos lados (malha de poliéster e elastano): as nervuras de 0,9 mm ao longo da mão
    cruzadas pelas carreiras de 0,6 mm, aspereza alta e o brilho de tecido (sheen) nos ângulos rasantes."""
    m, n, l, b = novo_mat(nome)
    tc = n.new('ShaderNodeTexCoord')
    ondas = []
    for eixo, periodo, torcer in (('X', 0.9, 1.5), ('Y', 0.6, 0.8)):
        w = n.new('ShaderNodeTexWave')
        w.wave_type = 'BANDS'
        w.bands_direction = eixo
        w.inputs['Scale'].default_value = escala_da_onda(periodo)
        w.inputs['Distortion'].default_value = torcer
        w.inputs['Detail'].default_value = 1.0
        l.new(tc.outputs['Object'], w.inputs['Vector'])
        ondas.append(w)
    malha = n.new('ShaderNodeMath')
    malha.operation = 'MULTIPLY'
    l.new(ondas[0].outputs['Fac'], malha.inputs[0])
    l.new(ondas[1].outputs['Fac'], malha.inputs[1])
    tinta = ruido_mm(n, l, 25.0, 3.0)
    alt_costura, sulco = costura(n, l)
    base_cor = mistura_cor(n, l, faixa(n, l, tinta.outputs['Fac'], 0.0, 0.2), cor, tuple(c * 0.85 for c in cor))
    l.new(_escurecer_no_sulco(n, l, base_cor, sulco), b.inputs['Base Color'])
    asp = ruido_mm(n, l, 5.0)
    l.new(faixa(n, l, asp.outputs['Fac'], 0.84, 0.93), b.inputs['Roughness'])
    # O brilho de tecido na cor da própria trama (um tom acima): com o branco, a malha marrom lia como pele.
    b.inputs['Sheen Weight'].default_value = 0.35
    b.inputs['Sheen Roughness'].default_value = 0.5
    b.inputs['Sheen Tint'].default_value = (*tuple(min(1.0, c * 1.3) for c in cor), 1)
    bev, borda_m = mascara_borda(n, l, 0.8)
    normal = _relevo(n, l, malha.outputs['Value'], 0.35, 0.15, bev.outputs['Normal'], fino=True)
    l.new(_relevo(n, l, alt_costura, 1.0, 0.35, normal), b.inputs['Normal'])
    canal(n, l, 'canal_aspereza', asp.outputs['Fac'])
    canal(n, l, 'canal_cor', _conta(n, l, 'MULTIPLY', tinta.outputs['Fac'], _conta(n, l, 'SUBTRACT', 1.0,
                                                                                  _conta(n, l, 'MULTIPLY', sulco, 0.6))))
    canal(n, l, 'canal_borda', borda_m.outputs['Result'])
    return m


def mat_borracha(nome, cor):
    """Borracha moldada (TPR) do protetor, das almofadas e da tira: o pontilhado fino do molde (0,35 mm), aspereza de
    borracha e um brilho leve nas quinas gastas."""
    m, n, l, b = novo_mat(nome)
    pont = ruido_mm(n, l, 0.35, 1.0)
    manchas = ruido_mm(n, l, 22.0, 3.0)
    alt_costura, sulco = costura(n, l)
    base_cor = mistura_cor(n, l, faixa(n, l, manchas.outputs['Fac'], 0.0, 0.18), cor, tuple(c * 0.88 for c in cor))
    l.new(_escurecer_no_sulco(n, l, base_cor, sulco), b.inputs['Base Color'])
    asp = ruido_mm(n, l, 4.0)
    l.new(faixa(n, l, asp.outputs['Fac'], 0.58, 0.7), b.inputs['Roughness'])
    bev, borda_m = mascara_borda(n, l, 0.6)
    normal = _relevo(n, l, pont.outputs['Fac'], 0.22, 0.1, bev.outputs['Normal'], fino=True)
    # O puxador: o gancho do velcro, pontinhos densos de 0,15 mm num passo de 0,45 mm.
    gancho = _conta(n, l, 'MULTIPLY', _pontinhos(n, l, 0.45, 0.33), _no_atributo(n, 'velcro'))
    normal = _relevo(n, l, gancho, 0.9, 0.15, normal, fino=True)
    # A tira: nervuras moldadas em diagonal (passo de 3,2 mm), como a banda de TPR do fecho. A tira dá a volta no
    # punho (o eixo X): a diagonal é entre o X e o arco em volta dele (o ângulo vezes o raio do punho, ~33 mm).
    tc = n.new('ShaderNodeTexCoord')
    xyz = n.new('ShaderNodeSeparateXYZ')
    l.new(tc.outputs['Object'], xyz.inputs['Vector'])
    arco = _conta(n, l, 'MULTIPLY', _conta(n, l, 'ARCTAN2', xyz.outputs['Y'], xyz.outputs['Z']), 33.0 * S)
    diagonal = _conta(n, l, 'MULTIPLY', _conta(n, l, 'ADD', xyz.outputs['X'], arco), math.sqrt(0.5))
    onda = _conta(n, l, 'SINE', _conta(n, l, 'MULTIPLY', diagonal, 2 * math.pi / (3.2 * S)))
    nervuras = _conta(n, l, 'MULTIPLY', _degrau(n, l, onda, 0.35, 0.8), _no_atributo(n, 'tira'))
    normal = _relevo(n, l, nervuras, 0.8, 0.3, normal)
    l.new(_relevo(n, l, alt_costura, 1.0, 0.35, normal), b.inputs['Normal'])
    canal(n, l, 'canal_aspereza', asp.outputs['Fac'])
    canal(n, l, 'canal_cor', _conta(n, l, 'MULTIPLY', manchas.outputs['Fac'], _conta(n, l, 'SUBTRACT', 1.0,
                                                                                    _conta(n, l, 'MULTIPLY', sulco, 0.6))))
    canal(n, l, 'canal_borda', borda_m.outputs['Result'])
    return m


def materiais_das_luvas(pintura):
    """Os materiais das luvas a partir da pintura de uma facção (src/data/luvas.js), por zona, com o nome da zona: é
    ele que vai para o luvas.glb e que o jogo lê (o reforço é de borracha, mas a zona é `reforco`)."""
    z = pintura['zonas']
    return {
        'couro': mat_couro('couro', linear(z['couro']['cor'])),
        'tecido': mat_tecido('tecido', linear(z['tecido']['cor'])),
        'reforco': mat_borracha('reforco', linear(z['reforco']['cor'])),
    }


def materiais_de_fabrica(fabrica):
```

Run: `node --test "tests/**/*.test.js"`
Expected: PASS — # tests 381 # pass 381 # fail 0 .

### Tarefa 5: Rig e pesos (`maos_rig.py`)

**Files:** Create `maos_rig.py`; Modify `principal.py`.

- [ ] **Passo 1: Armadura** — 20 ossos por braço com os nomes da D2, a hierarquia `antebraco → torcao → mao →` dedos
  (`anelar_0 → anelar_1…`, `minimo_0 → minimo_1…`), rolagens coerentes (o eixo de flexão de cada dedo perpendicular ao
  plano de fechamento).
- [ ] **Passo 2: Pesos** — pela camada `osso`/`t` da malha base (mistura suave nos três anéis de cada junta; a borda
  ulnar da palma entre `mao`, `anelar_0` e `minimo_0`; o punho entre `mao` e `torcao`); as peças de detalhe herdam da
  superfície mais próxima (modificador Data Transfer aplicado); no máximo 4 influências, normalizadas, sem peso < 0,01.
- [ ] **Passo 3: Espelho** — o braço esquerdo é o direito espelhado em Y (malha, armadura, grupos `_d` → `_e`), com as
  mesmas UV.
- [ ] **Passo 4: Poses de teste e validação** (`validar_maos.py`): punho fechado (MCP 85°, PIP 95°, DIP 60°, polegar
  fechado sobre o médio), mão aberta (todas as juntas no mínimo, abertura 15°) e pulso a 60° de flexão: nenhuma junta
  afina mais de 30 % (espessura mínima da seção transversal medida nos anéis das juntas, pose × repouso) e nenhum
  vértice atravessa a própria malha mais de 0,3 mm; vistas das três poses na `conferir`.


**Código da tarefa** (a versão verificada no navegador e no Blender; os blocos `file=` são o arquivo inteiro, os pares são aplicados na ordem).

- [ ] **A implementação** — `tools/blender/armas/maos_rig.py`, `tools/blender/armas/maos_contato.py`, `tools/blender/armas/maos_correcoes.py`, `tools/blender/armas/validar_maos.py`, `tools/blender/armas/empunhadura.py`, `tools/blender/armas/empunhadura_polegar.py`, `tools/blender/armas/maos_poses.py`:

```python file=tools/blender/armas/maos_rig.py
# Rig das luvas (Fase 4.1b; desenho em docs/superpowers/specs/2026-09-26-4.1b-luvas-e-empunhadura-design.md, seção 4;
# plano, Tarefa 5 e D2–D4): a armadura de 20 ossos por braço na pose de repouso da ficha, os pesos (os da gaiola,
# interpolados pela subdivisão; as peças de detalhe herdam da superfície da luva embaixo), o espelho para o braço
# esquerdo e a marca do rig.
# Ossos (D2): antebraco → torcao → mao → polegar_1..3, indicador_1..3, medio_1..3, anelar_0..3, minimo_0..3 (o anelar e o
# mínimo com o metacarpo próprio: a borda da palma fecha em concha), com o sufixo do lado (_d, _e).
# Eixos: o Y de cada osso ao longo dele; o X no eixo de flexão (nos dedos, a MCP reta e a PIP e a DIP inclinadas pela
# convergência; o do polegar; o de através da mão para a palma, o pulso e o antebraço) e o Z = X × Y do lado da palma
# — girar positivo em X fecha a junta (dobra o dedo para a palma, flexiona o pulso); girar em Y torce (a pronação). O
# braço esquerdo é o direito espelhado em Y com o X invertido, para girar positivo em X continuar fechando.
# As correções das dobras (maos_correcoes.py) são aplicadas depois do skin, pela pose do rig.
import hashlib
import json
import math

import bpy
from mathutils import Matrix, Quaternion, Vector

from .maos import DEDOS4, METACARPO
from .unidades import S

OSSOS = ('antebraco', 'torcao', 'mao',
         'polegar_1', 'polegar_2', 'polegar_3',
         'indicador_1', 'indicador_2', 'indicador_3',
         'medio_1', 'medio_2', 'medio_3',
         'anelar_0', 'anelar_1', 'anelar_2', 'anelar_3',
         'minimo_0', 'minimo_1', 'minimo_2', 'minimo_3')
MAX_INFLUENCIAS = 4
PESO_MINIMO = 0.01


def _pai(osso):
    if osso == 'antebraco':
        return None
    if osso == 'torcao':
        return 'antebraco'
    if osso == 'mao':
        return 'torcao'
    dedo, i = osso.rsplit('_', 1)
    i = int(i)
    if i == 0 or (i == 1 and dedo not in METACARPO):
        return 'mao'
    return f'{dedo}_{i - 1}'


def eixos_de_flexao(mao):
    """{osso: eixo de flexão (mm, unitário)} da mão direita em repouso."""
    atraves = Vector((0.0, 1.0, 0.0))
    eixos = {'antebraco': atraves, 'torcao': atraves, 'mao': atraves, 'anelar_0': atraves, 'minimo_0': atraves}
    for i in range(3):
        eixos[f'polegar_{i + 1}'] = mao.polegar['eixo'].copy()
    for d in DEDOS4:
        eixos[f'{d}_1'] = mao.dedos[d]['eixo_mcp'].copy()
        eixos[f'{d}_2'] = mao.dedos[d]['eixo_ip'].copy()
        eixos[f'{d}_3'] = mao.dedos[d]['eixo_ip'].copy()
    return eixos


def armadura(mao, colecao, lado='d'):
    """A armadura da mão direita (ou a esquerda espelhada, lado 'e') em metros, com os nomes da D2 e o sufixo."""
    ossos = mao.ossos()
    eixos = eixos_de_flexao(mao)
    arm = bpy.data.armatures.new(f'rig_{lado}')
    ob = bpy.data.objects.new(f'rig_{lado}', arm)
    colecao.objects.link(ob)
    espelho = Matrix.Diagonal((1.0, -1.0 if lado == 'e' else 1.0, 1.0))
    with bpy.context.temp_override(active_object=ob, object=ob, selected_objects=[ob]):
        bpy.context.view_layer.objects.active = ob
        bpy.ops.object.mode_set(mode='EDIT')
        for nome in OSSOS:
            cabeca, cauda, _normal = ossos[nome]
            eb = arm.edit_bones.new(f'{nome}_{lado}')
            eb.head = (espelho @ cabeca) * S
            eb.tail = (espelho @ cauda) * S
            y = (eb.tail - eb.head).normalized()
            x = espelho @ eixos[nome]
            if lado == 'e':
                x = -x  # o espelho troca a mão do referencial: com o X invertido, girar positivo continua fechando
            x = (x - y * x.dot(y)).normalized()
            eb.align_roll(x.cross(y))  # align_roll põe o Z do osso na direção dada: Z = X × Y
        for nome in OSSOS:
            pai = _pai(nome)
            if pai:
                eb = arm.edit_bones[f'{nome}_{lado}']
                eb.parent = arm.edit_bones[f'{pai}_{lado}']
                eb.use_connect = (eb.head - eb.parent.tail).length < 1e-6
        bpy.ops.object.mode_set(mode='OBJECT')
    return ob


def marca(rig):
    """A marca do rig (D4): SHA-256 dos comprimentos dos ossos e dos quaternions da pose de repouso (a orientação de cada
    osso em relação ao pai), arredondados a 1e-5, na ordem dos OSSOS."""
    lado = rig.name.rsplit('_', 1)[1]
    dados = []
    for nome in OSSOS:
        b = rig.data.bones[f'{nome}_{lado}']
        m = b.matrix_local if b.parent is None else b.parent.matrix_local.inverted() @ b.matrix_local
        q = m.to_quaternion()
        if q.w < 0:
            q.negate()
        dados.append([nome, round(b.length, 5), [round(c, 5) for c in q]])
    return hashlib.sha256(json.dumps(dados, separators=(',', ':')).encode()).hexdigest()


# ---------------------------------------------------------------------------------------------- pesos
def _limpar_pesos(ob):
    """No máximo MAX_INFLUENCIAS ossos por vértice (os maiores), normalizados, sem peso abaixo de PESO_MINIMO."""
    me = ob.data
    grupos = ob.vertex_groups
    for v in me.vertices:
        ws = sorted(((g.group, g.weight) for g in v.groups if g.weight > 0), key=lambda t: -t[1])
        fica = [(gi, w) for gi, w in ws[:MAX_INFLUENCIAS] if w >= PESO_MINIMO]
        if not fica:
            fica = ws[:1]
        total = sum(w for _, w in fica)
        manter = {gi for gi, _ in fica}
        for gi, _ in ws:
            if gi not in manter:
                grupos[gi].remove([v.index])
        for gi, w in fica:
            grupos[gi].add([v.index], w / total, 'REPLACE')


def pesos(luva, pecas, lado='d'):
    """Junta as peças de detalhe na luva com os pesos da superfície embaixo (Data Transfer do ponto mais próximo na face,
    interpolado), limita e normaliza os pesos e põe o sufixo do lado nos grupos. Devolve a luva."""
    for ob in pecas:
        for g in luva.vertex_groups:
            ob.vertex_groups.new(name=g.name)
        dt = ob.modifiers.new('pesos', 'DATA_TRANSFER')
        dt.object = luva
        dt.use_vert_data = True
        dt.data_types_verts = {'VGROUP_WEIGHTS'}
        dt.vert_mapping = 'POLYINTERP_NEAREST'
        dt.layers_vgroup_select_src = 'ALL'
        dt.layers_vgroup_select_dst = 'NAME'
        with bpy.context.temp_override(object=ob, active_object=ob):
            bpy.ops.object.modifier_apply(modifier=dt.name)
    if pecas:
        with bpy.context.temp_override(active_object=luva, object=luva, selected_objects=[luva, *pecas],
                                       selected_editable_objects=[luva, *pecas]):
            bpy.ops.object.join()
    _limpar_pesos(luva)
    for g in luva.vertex_groups:
        if not g.name.endswith(f'_{lado}'):
            g.name = f'{g.name}_{lado}'
    return luva


def ligar(luva, rig):
    """A luva presa ao rig: pai e modificador Armature (pelos grupos de vértices)."""
    luva.parent = rig
    m = luva.modifiers.new('rig', 'ARMATURE')
    m.object = rig
    m.use_vertex_groups = True
    return m


def _espelhar_coordenadas(dados):
    co = [0.0] * (len(dados) * 3)
    dados.foreach_get('co', co)
    co[1::3] = [-y for y in co[1::3]]
    dados.foreach_set('co', co)


def espelhar(luva_d, rig_d, mao, colecao):
    """O braço esquerdo: a malha da direita espelhada em Y (com as mesmas UV e as faces viradas de volta), os grupos
    com `_e` e a armadura esquerda (armadura(..., 'e')). Devolve (luva_e, rig_e)."""
    me = luva_d.data.copy()
    me.name = luva_d.data.name.replace('_d', '_e')
    luva_e = bpy.data.objects.new(luva_d.name.replace('_d', '_e'), me)
    colecao.objects.link(luva_e)
    _espelhar_coordenadas(me.vertices)
    me.flip_normals()
    me.update()
    # Os pesos e os nomes dos grupos vêm com a malha copiada (desde o Blender 3.0 os nomes ficam na malha, não no
    # objeto): os grupos `_d` da cópia são renomeados. Criar grupos `_e` novos deixava o braço esquerdo sem peso nenhum
    # (os pesos nos grupos `_d`, que não casam com os ossos do rig esquerdo; a conferência do espelho pegou).
    for g in luva_e.vertex_groups:
        if g.name.endswith('_d'):
            g.name = g.name[:-2] + '_e'
    if {g.name for g in luva_e.vertex_groups} != {g.name[:-2] + '_e' for g in luva_d.vertex_groups}:
        raise RuntimeError('espelhar: os grupos do braço esquerdo não casam com os do direito')
    rig_e = armadura(mao, colecao, 'e')
    ligar(luva_e, rig_e)
    return luva_e, rig_e


# ---------------------------------------------------------------------------------------------- poses
def _flexao(graus):
    return Quaternion((1.0, 0.0, 0.0), math.radians(graus))


def espelhar_pose(pose):
    """A pose da mão direita no braço esquerdo: o mesmo movimento, espelhado em Y. Os ossos esquerdos têm o X invertido
    do espelho (X' = −M·X, Y' = M·Y, Z' = M·Z), então uma rotação da direita, no referencial do osso, vira a conjugação
    dela pela meia volta em X — (w, x, y, z) → (w, x, −y, −z): a flexão (em X) igual, os giros em Y e em Z com o sinal
    trocado (a abertura dos dedos, a pronação e a abdução do polegar)."""
    return {o: Quaternion((q.w, q.x, -q.y, -q.z)) for o, q in pose.items()}


def eixo_abducao_do_polegar(mao, rig):
    """(eixo no referencial de repouso do polegar_1, sinal) da abdução palmar da CMC: o eixo da ficha (a normal da palma
    × a direção do polegar na palma, o de maos.Mao._polegar), preso à palma; no braço esquerdo, o eixo espelhado e o
    sinal trocado (o espelho inverte o sentido dos giros). Positivo leva o polegar para a frente da palma."""
    ang = math.radians(mao.ded['polegar']['anguloNaPalma'])
    eixo = Vector((-math.sin(ang), math.cos(ang), 0.0))
    lado = rig.name.rsplit('_', 1)[1]
    sinal = 1.0
    if lado == 'e':
        eixo, sinal = Vector((eixo.x, -eixo.y, eixo.z)), -1.0
    b = rig.data.bones[f'polegar_1_{lado}']
    return (b.matrix_local.to_3x3().inverted() @ eixo).normalized(), sinal


def pose_de_teste(nome, mao):
    """{osso: quaternion} de uma pose de teste da seção 4 do desenho que não depende de contato, relativa ao repouso
    (graus totais na junta menos o repouso da ficha): `aberta` (todas as juntas no mínimo da AAOS, abertura de 15°) e
    `pulso` (a mão em repouso com o pulso a 60° de flexão). As que fecham até encostar (o punho, o apontar e a mesa)
    estão em empunhadura.poses_de_teste."""
    rep = mao.rep
    p = {}
    if nome == 'aberta':
        lim = mao.f['limites']
        for d in DEDOS4:
            # A abertura gira em volta do Z do osso (para a palma), antes da flexão (como no solver de empunhadura):
            # positivo leva o dedo para o lado do mínimo.
            ab = {'indicador': 1.0, 'medio': 0.0, 'anelar': -1.0, 'minimo': -2.0}[d] * (15 - rep['abertura'])
            p[f'{d}_1'] = _flexao(lim['mcp'][0] - rep['mcp']) @ Quaternion((0.0, 0.0, 1.0), math.radians(-ab))
            p[f'{d}_2'] = _flexao(lim['pip'][0] - rep['pip'])
            p[f'{d}_3'] = _flexao(lim['dip'][0] - rep['dip'])
        p['polegar_2'] = _flexao(lim['polegar']['mcp'][0] - rep['polegarMcp'])
        p['polegar_3'] = _flexao(lim['polegar']['ip'][0] - rep['polegarIp'])
    elif nome == 'pulso':
        p['mao'] = _flexao(60.0)
    else:
        raise ValueError(f'pose de teste desconhecida: {nome}')
    return p


def posar(rig, pose):
    """Põe a pose ({osso sem sufixo: quaternion}) no rig, os outros ossos em repouso."""
    lado = rig.name.rsplit('_', 1)[1]
    for pb in rig.pose.bones:
        pb.rotation_mode = 'QUATERNION'
        pb.rotation_quaternion = Quaternion()
    for nome, q in pose.items():
        rig.pose.bones[f'{nome}_{lado}'].rotation_quaternion = q
    bpy.context.view_layer.update()


def pose_json(pose):
    """A pose ({osso: quaternion}) em JSON ({osso: [w, x, y, z]})."""
    return {o: [round(c, 7) for c in q] for o, q in pose.items()}


def pose_de_json(dados):
    return {o: Quaternion(q) for o, q in dados.items()}
```

```python file=tools/blender/armas/maos_contato.py
# Cruzamento e penetração da luva (Fase 4.1b; desenho em docs/superpowers/specs/2026-09-26-4.1b-luvas-e-empunhadura-design.md,
# seções 4 e 6.3; plano, Tarefas 5 e 7): as medidas de "a malha não atravessa a si mesma mais de 0,3 mm" (as poses de
# teste) e de "encostou" (o solver de empunhadura), sobre a malha avaliada numa pose.
#  - Os pares de triângulos que se cruzam: a BVH dos dois conjuntos (ou de um consigo mesmo), fora os que dividem um
#    vértice.
#  - A penetração de um par é a do vértice mais fundo: cada vértice de um triângulo contra a superfície em volta do outro
#    (ele e os vizinhos até três anéis), pelo ponto mais próximo dela e o sinal da pseudo-normal ali (a normal da face
#    no meio dela; na aresta ou no vértice, a média das faces que tocam o ponto) — quanto o vértice está dentro da
#    superfície. O plano infinito de um triângulo não serve: numa dobra fechada, com triângulos finos quase paralelos,
#    um vértice fica "atrás do plano" do outro a milímetros de distância sem estar dentro de nada (a medida pelo plano
#    dava 3,6 mm onde a penetração real era 0,24 mm).
# Unidades: as dos pontos (mm nas validações).
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.geometry import closest_point_on_tri

ANEIS = 3
DENTRO_DA_FACE = 1e-4  # mm: o ponto mais próximo a menos disso de uma face é daquela face (para a pseudo-normal)


class Superficie:
    """Os triângulos de uma malha e, por vértice, os triângulos que o usam (a topologia não muda entre as poses)."""

    def __init__(self, tris):
        self.tris = [tuple(t) for t in tris]
        self.de_vertice = {}
        for k, t in enumerate(self.tris):
            for v in t:
                self.de_vertice.setdefault(v, []).append(k)

    def regiao(self, k, dentro=None):
        """O triângulo k e os vizinhos até ANEIS anéis (só os de `dentro`, se dado)."""
        r, borda = {k}, {k}
        for _ in range(ANEIS):
            novos = {j for t in borda for v in self.tris[t] for j in self.de_vertice[v]} - r
            if dentro is not None:
                novos &= dentro
            r |= novos
            borda = novos
        return sorted(r)


def pares(pts, tris, A, B=None):
    """Os pares (a, b) de triângulos (índices em `tris`) de A com B (ou de A consigo mesmo) que se cruzam, sem os que
    dividem um vértice."""
    ta = BVHTree.FromPolygons(pts, [tris[k] for k in A])
    tb = ta if B is None else BVHTree.FromPolygons(pts, [tris[k] for k in B])
    B = A if B is None else B
    saida = []
    for i, j in ta.overlap(tb):
        a, b = A[i], B[j]
        if (B is A and a >= b) or set(tris[a]) & set(tris[b]):
            continue
        saida.append((a, b))
    return saida


def _normal(pts, t):
    a, b, c = (pts[i] for i in t)
    n = (b - a).cross(c - a)
    return n.normalized() if n.length > 1e-12 else Vector()


class Medidor:
    """A penetração dos pares numa pose (os pontos), com as regiões e as BVH delas guardadas para os pares repetidos."""

    def __init__(self, sup, pts):
        self.sup, self.pts = sup, pts
        self._bvh = {}

    def _regiao(self, k, dentro):
        chave = (k, id(dentro))
        if chave not in self._bvh:
            reg = self.sup.regiao(k, dentro)
            tris = [self.sup.tris[j] for j in reg]
            self._bvh[chave] = (reg, BVHTree.FromPolygons(self.pts, tris), {v for t in tris for v in t})
        return self._bvh[chave]

    def _pseudo_normal(self, reg, j, co):
        t = self.sup.tris[reg[j]]
        faces = {reg[j]}
        for v in t:
            for k in self.sup.de_vertice[v]:
                if k in faces:
                    continue
                a, b, c = (self.pts[i] for i in self.sup.tris[k])
                if (closest_point_on_tri(co, a, b, c) - co).length < DENTRO_DA_FACE:
                    faces.add(k)
        n = Vector()
        for k in faces:
            n += _normal(self.pts, self.sup.tris[k])
        return n.normalized() if n.length > 1e-12 else _normal(self.pts, t)

    def vertice_em(self, v, k, dentro=None):
        """Quanto o vértice v está dentro da superfície em volta do triângulo k (mm; 0 se fora ou se ele é dela)."""
        reg, bvh, vs = self._regiao(k, dentro)
        if v in vs:
            return 0.0
        co, _n, j, _d = bvh.find_nearest(self.pts[v])
        if co is None:
            return 0.0
        s = (self.pts[v] - co).dot(self._pseudo_normal(reg, j, co))
        return max(0.0, -s)

    def par(self, a, b, dentro_a=None, dentro_b=None):
        """A penetração do par: o vértice mais fundo de cada triângulo na superfície em volta do outro."""
        ta, tb = self.sup.tris[a], self.sup.tris[b]
        return max(max(self.vertice_em(v, b, dentro_b) for v in ta), max(self.vertice_em(v, a, dentro_a) for v in tb))
```

```python file=tools/blender/armas/maos_correcoes.py
# Correções das dobras das luvas (Fase 4.1b; desenho em docs/superpowers/specs/2026-09-26-4.1b-luvas-e-empunhadura-design.md,
# seção 4; plano, Tarefa 5, Passo 4). O skin linear dos pesos (LBS) numa junta que fecha perde volume por fora (o nó
# afina: a média das duas matrizes encolhe o raio) e se atravessa por dentro (a palma da falange de baixo entra na de
# cima; no punho fechado, 6 mm). Depois do skin, cada junta corrige a malha, uma depois da outra, pela pose dela:
#  - por fora, os vértices da mistura dos pesos (nem só da parte parada nem só da que gira) voltam ao raio de repouso em
#    volta do eixo do giro da junta, pelo centro dela (o nó redondo, como a pele esticada sobre a cabeça do osso; o eixo
#    é o do giro inteiro da junta, então a abertura da MCP e a adução da CMC entram certas). Só do lado de fora da
#    dobra (as costas, u = eixo × normal apontando para dentro): inteiro a 2 mm para fora do plano do eixo, nada a 2 mm
#    para dentro, suave nos lados — por dentro, devolver o raio empurraria a pele da dobra contra o plano de contato;
#  - por dentro, a dobra: o plano de contato passa pelo eixo de flexão (preso ao osso de cima) e fica no meio entre a
#    direção reta da falange de cima e a do osso da junta — no repouso, a bissetriz do ângulo de repouso; na pose, a do
#    ângulo dela, com a abertura. Cada vértice é de um lado dele — o de lá se gira com a junta (os pesos), senão o de
#    cá; a base da falange, que no repouso fica atrás do plano da MCP, continua girando com o dedo e não entra na
#    palma —, empurrado pela normal do plano o quanto o softplus (escala 0,1 mm) da distância d a ele, menos a folga de
#    0,2 mm, cresceu desde o repouso (d₀): g(d − f) − g(d₀ − f), com g(x) = softplus(x) − x. Nada longe do plano; a pele
#    dos dois lados encostada a 0,2 mm dele sem as lâminas da dobra se sobreporem; nada no repouso; e, como o softplus
#    só empurra quem chega mais perto do plano do que estava, só do lado de dentro da dobra (por fora as duas partes se
#    afastam dele).
# Participam os vértices perto da junta — na faixa da largura dela ao longo do eixo e a até o alcance dela em volta do
# eixo (o raio da seção, mais a luva e 4 mm; na MCP, 22 mm, o coxim da palma diante dela; no pulso, a meia largura
# mais 6 mm) —, na proporção em que não são de outro dedo: a palma participa inteira de qualquer metacarpo (a diante da
# MCP do mínimo é do metacarpo do anelar) e a membrana entre dois dedos pela parte que é do dedo da junta.
# As peças de reforço seguem a base corrigida: cada vértice preso ao ponto mais próximo dela em repouso (o triângulo e
# as coordenadas baricêntricas), com o afastamento de repouso girado com a normal suave dali — o assentamento fica
# exato em qualquer pose (só o skin já tirava o protetor dos nós 0,6 mm do assento no punho fechado, com os pesos de
# três ossos nos nós).
# O jogo deforma as luvas pelo mesmo modelo, na CPU, a cada quadro (bracoLuva.js: o skin pelos ossos, as correções e
# as peças presas), com os parâmetros de cada junta e as amarras das peças nos `extras` do .glb (`parametros`); a
# validação e o solver de empunhadura avaliam a malha por aqui (`Modelo.avaliar`: o LBS em numpy, igual ao do Blender
# a 3e-5 mm, as correções e as peças). Um modelo analítico e não chaves de forma: exato em qualquer pose (as
# combinações de dedos vizinhos, a abertura), sem as dezenas de alvos de morph que as combinações pediriam; e na CPU,
# porque no shader um vértice não enxerga os da base em que a peça está presa. Unidades: mm; as malhas em metros no
# Blender.
import math

import bpy
import numpy as np
from mathutils import Matrix, Quaternion, Vector
from mathutils.bvhtree import BVHTree

from . import maos_rig
from .maos import DEDOS4
from .unidades import S

SUAVE_MM = 0.1  # a escala do softplus no plano de contato da dobra
FOLGA_MM = 0.2  # cada lado da dobra fica a esta distância do plano de contato
FAIXA_MM = 3.0  # a faixa da junta ao longo do eixo: a meia largura mais a luva e 3 mm, e mais 3 mm para sumir
FORA_MM = 2.0  # a restauração do raio vai de inteira (2 mm para fora do plano do eixo) a nada (2 mm para dentro)
RAIO_MCP_MM = 22.0  # o alcance da dobra da MCP em volta do eixo: o coxim da palma diante dela
GIRO_MINIMO = 1e-4  # radianos: abaixo disso a junta está em repouso


def juntas(mao):
    """[(junta, osso sem o lado, graus de repouso, graus máximos a partir do repouso, meia largura mm, alcance mm)] das
    juntas de flexão, na ordem em que as correções se aplicam: MCP, PIP e DIP dos quatro dedos (os limites da AAOS), a
    CMC, a MCP e a IP do polegar e o pulso."""
    lim = mao.f['limites']
    rep = mao.rep
    luva = mao.luva
    lista = []
    for d in DEDOS4:
        dd = mao.dedos[d]
        (lp, ep), (ld, ed) = dd['pip_sec'], dd['dip_sec']
        lista += [(f'{d}_mcp', f'{d}_1', rep['mcp'], lim['mcp'][1] - rep['mcp'], dd['larg_no'] / 2, RAIO_MCP_MM),
                  (f'{d}_pip', f'{d}_2', rep['pip'], lim['pip'][1] - rep['pip'], lp / 2, max(lp, ep) / 2 + luva + 4),
                  (f'{d}_dip', f'{d}_3', rep['dip'], lim['dip'][1] - rep['dip'], ld / 2, max(ld, ed) / 2 + luva + 4)]
    lp = lim['polegar']
    lip, eip = mao.polegar['ip_sec']
    # A CMC dobra a tenar contra a palma: a faixa é a largura da eminência tenar, ~1,5 × a da IP, e o alcance, o da MCP.
    lista += [('polegar_cmc', 'polegar_1', 0.0, lp['cmcFlexao'][1], lip * 0.75, RAIO_MCP_MM),
              ('polegar_mcp', 'polegar_2', rep['polegarMcp'], lp['mcp'][1] - rep['polegarMcp'], lip * 0.55,
               max(lip * 1.1, eip * 1.12) / 2 + luva + 4),
              ('polegar_ip', 'polegar_3', rep['polegarIp'], lp['ip'][1] - rep['polegarIp'], lip / 2,
               max(lip, eip) / 2 + luva + 4),
              ('pulso', 'mao', 0.0, lim['pulso']['flexao'], mao.pulso_larg / 2,
               max(mao.pulso_larg, mao.pulso_esp) / 2 + luva + 6)]
    return lista


def _digito(osso):
    """O dedo de um osso de falange (sem o lado) ou None (a palma: mão, metacarpos do anelar e do mínimo, antebraço)."""
    nome, _, i = osso.rpartition('_')
    if nome == 'polegar' or (nome in DEDOS4 and i in ('1', '2', '3')):
        return nome
    return None


def _suave(t):
    t = np.clip(t, 0.0, 1.0)
    return t * t * (3 - 2 * t)


def _softplus_menos_x(x):
    return SUAVE_MM * np.logaddexp(0.0, -x / SUAVE_MM)


class _Junta:
    """Os dados de repouso de uma junta para a correção: o centro, o eixo de flexão, a normal do plano de contato e a
    direção reta da falange de cima, e por vértice o peso do lado que gira, a participação e a distância ao plano."""

    def __init__(self, malha, junta):
        self.nome, osso0, self.repouso, self.maximo, self.meia, self.alcance = junta
        self.osso = f'{osso0}_{malha.lado}'
        b = malha.rig.data.bones[self.osso]
        self.pai = b.parent.name if b.parent else None
        m = b.matrix_local
        self.c0 = np.array(b.head_local) / S
        self.a0 = np.array(m.col[0].xyz.normalized())
        y0 = m.col[1].xyz.normalized()
        a0 = Vector(self.a0)
        self.n0 = np.array(Quaternion(a0, math.radians(-self.repouso / 2)) @ y0)
        self.reto0 = np.array(Quaternion(a0, math.radians(-self.repouso)) @ y0)
        abaixo = {self.osso} | {c.name for c in b.children_recursive}
        self.abaixo = sorted(o[:-2] for o in abaixo)
        dedo = _digito(osso0)
        self.outros = sorted(o[:-2] for o in malha.ossos if _digito(o[:-2]) not in (None, dedo))
        idx = {o: i for i, o in enumerate(malha.ossos)}
        self.w_abaixo = malha.W[:, [idx[o] for o in abaixo]].sum(1)
        w_outro = malha.W[:, [idx[f'{o}_{malha.lado}'] for o in self.outros]].sum(1) if self.outros else 0.0
        rel0 = malha.p - self.c0
        raio0 = np.linalg.norm(rel0 - np.outer(rel0 @ self.a0, self.a0), axis=1)
        faixa = _suave((self.meia + malha.luva_mm + FAIXA_MM - np.abs(rel0 @ self.a0)) / FAIXA_MM)
        perto = _suave((self.alcance + FAIXA_MM - raio0) / FAIXA_MM)
        self.peso = faixa * perto * np.clip(1.0 - w_outro, 0.0, 1.0) * malha.base
        self.lado = np.where(self.w_abaixo >= 0.5, 1.0, -1.0)
        self.d0 = self.lado * (rel0 @ self.n0)
        u0 = np.cross(self.a0, self.n0)  # para dentro da dobra (o lado da palma)
        self.fora = _suave((FORA_MM - rel0 @ u0) / (2 * FORA_MM))
        self.mistura = (self.w_abaixo > 0.002) & (self.w_abaixo < 0.998) & (self.peso * self.fora > 0)
        self.rel0 = rel0

    def parametros(self):
        """Os números que o shader do jogo precisa (mm e unitários, no referencial do braço)."""
        return {'junta': self.nome, 'osso': self.osso[:-2], 'repouso': float(self.repouso),
                'meia': round(float(self.meia), 4), 'alcance': round(float(self.alcance), 4),
                'centro': [round(float(c), 5) for c in self.c0], 'eixo': [round(float(c), 6) for c in self.a0],
                'normal': [round(float(c), 6) for c in self.n0], 'reto': [round(float(c), 6) for c in self.reto0],
                'abaixo': self.abaixo, 'outros': self.outros}

    def aplicar(self, rig, alvo):
        """A correção desta junta na pose atual do rig, sobre `alvo` (mm, as posições depois do skin e das juntas
        anteriores)."""
        pb = rig.pose.bones[self.osso]
        q = pb.rotation_quaternion if pb.rotation_mode == 'QUATERNION' else pb.matrix_basis.to_quaternion()
        angulo = q.angle
        if angulo < GIRO_MINIMO:
            return alvo
        if self.pai:
            pp = rig.pose.bones[self.pai]
            P = np.array((pp.matrix @ rig.data.bones[self.pai].matrix_local.inverted()).to_3x3())
        else:
            P = np.eye(3)
        c = np.array(pb.head) / S
        a = P @ self.a0
        # por fora: o raio de repouso em volta do eixo do giro inteiro da junta (no referencial de repouso do braço)
        b = rig.data.bones[self.osso]
        e0 = np.array((b.matrix_local.to_3x3() @ q.axis).normalized())
        e = P @ e0
        m = self.mistura
        if m.any():
            r0 = np.linalg.norm(self.rel0[m] - np.outer(self.rel0[m] @ e0, e0), axis=1)
            rel = alvo[m] - c
            ax = rel @ e
            perp = rel - np.outer(ax, e)
            rp = np.linalg.norm(perp, axis=1)
            ok = (rp > 1.0) & (r0 > 1.0)
            novo = c + np.outer(ax, e) + perp * (r0 / np.maximum(rp, 1e-9))[:, None]
            alvo[m] += np.where(ok[:, None], (novo - alvo[m]) * (self.peso * self.fora)[m, None], 0.0)
        # por dentro: o plano de contato entre a direção reta de cima e a do osso da junta
        y = np.array(pb.matrix.col[1].xyz.normalized())
        n = y + P @ self.reto0
        n -= a * (n @ a)
        n /= max(np.linalg.norm(n), 1e-12)
        d = self.lado * ((alvo - c) @ n)
        empurra = np.maximum(_softplus_menos_x(d - FOLGA_MM) - _softplus_menos_x(self.d0 - FOLGA_MM), 0.0)
        alvo += np.outer(self.lado * empurra * self.peso, n)
        return alvo


def _normais_dos_vertices(p, tri):
    """Normais suaves (pela área) dos vértices dos triângulos."""
    fn = np.cross(p[tri[:, 1]] - p[tri[:, 0]], p[tri[:, 2]] - p[tri[:, 0]])
    vn = np.zeros_like(p)
    for k in range(3):
        np.add.at(vn, tri[:, k], fn)
    return vn / np.maximum(np.linalg.norm(vn, axis=1, keepdims=True), 1e-12)


def _girar(v, de, para):
    """Gira cada v pela rotação mínima que leva `de` a `para` (unitários), vetorizado."""
    k = np.cross(de, para)
    s = np.linalg.norm(k, axis=1)
    c = np.einsum('ij,ij->i', de, para)
    eixo = k / np.maximum(s, 1e-12)[:, None]
    kv = np.einsum('ij,ij->i', eixo, v)
    out = v * c[:, None] + np.cross(eixo, v) * s[:, None] + eixo * (kv * (1 - c))[:, None]
    return np.where((s > 1e-9)[:, None], out, v)


class Malha:
    """A luva ligada ao rig, em numpy (mm): o repouso, os pesos, a base (as faces fora do reforço) com as peças presas
    a ela, e o skin linear na pose atual do rig."""

    def __init__(self, luva, rig, luva_mm, reforco):
        for ob in (luva, rig):
            if any(abs(ob.matrix_world[i][j] - (i == j)) > 1e-9 for i in range(4) for j in range(4)):
                raise ValueError(f'{ob.name}: as correções pedem a luva e o rig na origem, sem escala nem giro')
        self.luva, self.rig, self.luva_mm = luva, rig, luva_mm
        self.lado = rig.name.rsplit('_', 1)[1]
        me = luva.data
        n = len(me.vertices)
        co = np.empty(n * 3)
        me.vertices.foreach_get('co', co)
        self.p = co.reshape(-1, 3) / S
        self.ossos = [b.name for b in rig.data.bones]
        idx = {nome: i for i, nome in enumerate(self.ossos)}
        grupo = {g.index: idx[g.name] for g in luva.vertex_groups if g.name in idx}
        W = np.zeros((n, len(self.ossos)))
        for v in me.vertices:
            for g in v.groups:
                if g.group in grupo:
                    W[v.index, grupo[g.group]] = g.weight
        self.W = W / np.maximum(W.sum(1, keepdims=True), 1e-12)
        me.calc_loop_triangles()
        nt = len(me.loop_triangles)
        tri = np.empty(nt * 3, np.int32)
        me.loop_triangles.foreach_get('vertices', tri)
        poly = np.empty(nt, np.int32)
        me.loop_triangles.foreach_get('polygon_index', poly)
        mats = np.empty(len(me.polygons), np.int32)
        me.polygons.foreach_get('material_index', mats)
        self.tri_base = tri.reshape(-1, 3)[mats[poly] != reforco]
        self.base = np.zeros(n, bool)
        self.base[self.tri_base.ravel()] = True
        self._prender_pecas()

    def _prender_pecas(self):
        """Cada vértice de peça no ponto mais próximo da base em repouso: o triângulo, as coordenadas baricêntricas, o
        afastamento até ele e a normal suave dali."""
        pecas = np.nonzero(~self.base)[0]
        tb = self.tri_base
        bvh = BVHTree.FromPolygons(self.p.tolist(), tb.tolist())
        vn = _normais_dos_vertices(self.p, tb)
        self.pecas = pecas
        self.prende_tri = np.empty(len(pecas), np.int64)
        self.prende_bar = np.empty((len(pecas), 3))
        self.prende_off = np.empty((len(pecas), 3))
        for k, i in enumerate(pecas):
            co, _n, t, _d = bvh.find_nearest(Vector(self.p[i]))
            a, b, c = (self.p[j] for j in tb[t])
            v0, v1, v2 = b - a, c - a, np.array(co) - a
            d00, d01, d11 = v0 @ v0, v0 @ v1, v1 @ v1
            d20, d21 = v2 @ v0, v2 @ v1
            den = d00 * d11 - d01 * d01
            bv = (d11 * d20 - d01 * d21) / den
            bw = (d00 * d21 - d01 * d20) / den
            self.prende_tri[k] = t
            self.prende_bar[k] = (1 - bv - bw, bv, bw)
            self.prende_off[k] = self.p[i] - np.array(co)
        ns = np.einsum('kj,kji->ki', self.prende_bar, vn[tb[self.prende_tri]])
        self.prende_ns = ns / np.maximum(np.linalg.norm(ns, axis=1, keepdims=True), 1e-12)

    def seguir_base(self, alvo):
        """Leva as peças para a base em `alvo` (as posições das peças são reescritas)."""
        tb = self.tri_base
        vn = _normais_dos_vertices(alvo, tb)
        cantos = tb[self.prende_tri]
        ponto = np.einsum('kj,kji->ki', self.prende_bar, alvo[cantos])
        ns = np.einsum('kj,kji->ki', self.prende_bar, vn[cantos])
        ns /= np.maximum(np.linalg.norm(ns, axis=1, keepdims=True), 1e-12)
        alvo[self.pecas] = ponto + _girar(self.prende_off, self.prende_ns, ns)
        return alvo

    def amarras(self):
        """As amarras das peças para o jogo: por vértice de peça, o vértice, os três da base, as baricêntricas, o
        afastamento e a normal de repouso (mm)."""
        return {'vertices': self.pecas.tolist(), 'base': self.tri_base[self.prende_tri].tolist(),
                'bar': np.round(self.prende_bar, 6).tolist(), 'afastamento': np.round(self.prende_off, 5).tolist(),
                'normal': np.round(self.prende_ns, 6).tolist()}

    def skin(self):
        """As posições pelo LBS (mm) na pose atual do rig."""
        nb = len(self.ossos)
        R = np.empty((nb, 3, 3))
        t = np.empty((nb, 3))
        for i, nome in enumerate(self.ossos):
            M = self.rig.pose.bones[nome].matrix @ self.rig.data.bones[nome].matrix_local.inverted()
            R[i] = np.array(M.to_3x3())
            t[i] = np.array(M.translation) / S
        B = np.einsum('vb,bij->vij', self.W, R)
        return np.einsum('vij,vj->vi', B, self.p) + self.W @ t


class Modelo:
    """O skin das luvas com as correções das dobras (ver o cabeçalho)."""

    def __init__(self, luva, rig, mao, reforco):
        self.malha = Malha(luva, rig, mao.luva, reforco)
        self.juntas = [_Junta(self.malha, j) for j in juntas(mao)]

    def avaliar(self, pose=None):
        """As posições (mm, numpy) da luva na pose (ou na atual do rig)."""
        if pose is not None:
            maos_rig.posar(self.malha.rig, pose)
        alvo = self.malha.skin()
        for j in self.juntas:
            alvo = j.aplicar(self.malha.rig, alvo)
        return self.malha.seguir_base(alvo)

    def pontos(self, pose=None):
        """As posições como Vectors (mm), para as BVH."""
        return [Vector(p) for p in self.avaliar(pose)]

    def parametros(self):
        """Os parâmetros do modelo para o shader do jogo (os `extras` do .glb)."""
        return {'suaveMM': SUAVE_MM, 'folgaMM': FOLGA_MM, 'faixaMM': FAIXA_MM, 'foraMM': FORA_MM, 'giroMinimo': GIRO_MINIMO,
                'luvaMM': float(self.malha.luva_mm), 'juntas': [j.parametros() for j in self.juntas],
                'pecas': self.malha.amarras()}

    def para_malha(self, nome, colecao, pose=None):
        """Um objeto com a malha da luva nas posições da pose, sem rig (para as vistas): a mesma topologia, os mesmos
        materiais."""
        me = self.malha.luva.data.copy()
        me.name = nome
        co = (self.avaliar(pose) * S).ravel()
        me.vertices.foreach_set('co', co)
        me.update()
        ob = bpy.data.objects.new(nome, me)
        ob.matrix_world = Matrix.Identity(4)
        colecao.objects.link(ob)
        return ob
```

```python file=tools/blender/armas/validar_maos.py
# Validação do rig das luvas nas poses de teste (Fase 4.1b; desenho em
# docs/superpowers/specs/2026-09-26-4.1b-luvas-e-empunhadura-design.md, seção 4; plano, Tarefa 5, Passo 4): em cada pose
# (o repouso; o punho fechado, o apontar e a mesa de empunhadura.poses_de_teste, fechados até o contato; a mão aberta e o
# pulso a 60°) e em cada junta sozinha no limite da AAOS — as PIP, as DIP, as do polegar e o pulso; as MCP dobram juntas
# na mesa, porque uma MCP no fim com a vizinha esticada não existe (os tendões do médio, do anelar e do mínimo são
# ligados) —, a malha deformada pelo modelo das luvas (o skin e as correções das dobras, maos_correcoes.Modelo — o
# mesmo do shader do jogo) é conferida:
#  - nenhuma junta afina mais de 30 %: a espessura mínima da seção no anel do meio da junta (os vértices com os dois
#    ossos da junta entre 35 % e 65 %), medida em todas as direções perpendiculares à junta, pose sobre repouso; a
#    parede do punho (o forro até a face de fora) também;
#  - a malha não atravessa a si mesma mais de 0,3 mm: os pares de triângulos que se cruzam (fora os de uma mesma peça,
#    os da peça com a pegada dela e os de duas peças empilhadas desde o repouso), cada par com a penetração do vértice
#    mais fundo na superfície em volta do outro (maos_contato.py). A pegada de uma peça é onde ela se assenta: os
#    triângulos da luva que ela cruza no repouso (as paredes descem 0,2 mm para dentro) e os vizinhos deles, e os que
#    ficam a até 1,5 mm dos vértices dela;
#  - as peças de reforço continuam assentadas: a base das paredes delas a 0,2 ± 0,3 mm dentro da luva.
import math

import numpy as np
from mathutils import Quaternion
from mathutils.bvhtree import BVHTree

from . import maos_contato, maos_correcoes, maos_rig
from .maos import DEDOS4, METACARPO
from .unidades import S

AFINAMENTO_MAXIMO = 0.30
ATRAVESSA_MM = 0.3
ASSENTO_MM = 0.3
PEGADA_MM = 1.5  # os triângulos da luva a até 1,5 mm de uma peça em repouso são a pegada dela (onde ela se assenta)


def _componentes(n_tris, tris):
    """Componente conexa (pelos vértices) de cada triângulo."""
    pai = list(range(n_tris))

    def raiz(i):
        while pai[i] != i:
            pai[i] = pai[pai[i]]
            i = pai[i]
        return i

    dono = {}
    for k, t in enumerate(tris):
        for v in t:
            if v in dono:
                a, b = raiz(k), raiz(dono[v])
                if a != b:
                    pai[a] = b
            else:
                dono[v] = k
    return [raiz(k) for k in range(n_tris)]


class Topologia:
    """O que não muda entre as poses: os triângulos, as peças (componentes do reforço) e a pegada de cada uma, os anéis
    das juntas, a base das paredes das peças e o forro do punho."""

    def __init__(self, luva, reforco):
        me = luva.data
        me.calc_loop_triangles()
        nt = len(me.loop_triangles)
        self.tris = [tuple(t.vertices) for t in me.loop_triangles]
        self.sup = maos_contato.Superficie(self.tris)
        poly = [t.polygon_index for t in me.loop_triangles]
        mats = np.empty(len(me.polygons), np.int32)
        me.polygons.foreach_get('material_index', mats)
        at = me.attributes.get('forro')
        forro = np.zeros(len(me.polygons), np.int32)
        if at is not None:
            at.data.foreach_get('value', forro)
        de_peca = [mats[p] == reforco for p in poly]
        comp = _componentes(nt, self.tris)
        self.peca = [comp[k] if de_peca[k] else -1 for k in range(nt)]
        self.base = [k for k in range(nt) if not de_peca[k]]
        self.fora = [k for k in self.base if not forro[poly[k]]]
        # a pegada de cada peça e as peças empilhadas (ver o cabeçalho)
        pts = [v.co / S for v in me.vertices]
        bvh_base = BVHTree.FromPolygons(pts, [self.tris[k] for k in self.base])
        self.pegada = {}
        for k in range(nt):
            if self.peca[k] >= 0:
                s = self.pegada.setdefault(self.peca[k], set())
                for v in self.tris[k]:
                    for *_r, j, _d in bvh_base.find_nearest_range(pts[v], PEGADA_MM):
                        s.add(self.base[j])
        tris_do_vertice = [[] for _ in me.vertices]
        for k, t in enumerate(self.tris):
            for v in t:
                tris_do_vertice[v].append(k)
        self.empilhadas = set()
        bvh = BVHTree.FromPolygons(pts, self.tris)
        for a, b in bvh.overlap(bvh):
            pa, pb = self.peca[a], self.peca[b]
            if pa >= 0 and pb >= 0 and pa != pb:
                self.empilhadas.add((pa, pb))
            elif pa >= 0 and pb < 0:
                self.pegada[pa].update(j for v in self.tris[b] for j in tris_do_vertice[v] if self.peca[j] < 0)
        # o forro: vértices só de faces do forro
        faces_do_vertice = [set() for _ in me.vertices]
        for p in me.polygons:
            for v in p.vertices:
                faces_do_vertice[v].add(bool(forro[p.index]))
        self.forro = [i for i, s in enumerate(faces_do_vertice) if s == {True}]
        self.juntas = _juntas(luva)
        at = me.attributes.get('assento')
        valores = [0.0] * len(me.vertices)
        if at is not None:
            at.data.foreach_get('value', valores)
        self.assento = [i for i, v in enumerate(valores) if v > 0.5]


def _juntas(luva):
    """{nome da junta: índices dos vértices do anel do meio dela} pelos pesos (os dois ossos entre 35 % e 65 %)."""
    nomes = {g.index: g.name[:-2] for g in luva.vertex_groups}
    pares = {'pulso': ('torcao', 'mao')}
    for d in DEDOS4:
        pares[f'{d}_mcp'] = (METACARPO.get(d, 'mao'), f'{d}_1')
        pares[f'{d}_pip'] = (f'{d}_1', f'{d}_2')
        pares[f'{d}_dip'] = (f'{d}_2', f'{d}_3')
    pares['polegar_mcp'] = ('polegar_1', 'polegar_2')
    pares['polegar_ip'] = ('polegar_2', 'polegar_3')
    aneis = {j: [] for j in pares}
    for v in luva.data.vertices:
        w = {nomes[g.group]: g.weight for g in v.groups}
        for j, (a, b) in pares.items():
            if 0.35 <= w.get(a, 0.0) <= 0.65 and 0.35 <= w.get(b, 0.0) <= 0.65:
                aneis[j].append(v.index)
    return {j: idx for j, idx in aneis.items() if len(idx) >= 6}


def _espessura_minima(pts):
    """A menor largura do conjunto de pontos entre as direções perpendiculares ao eixo principal dele (o anel da junta
    fica num plano; o eixo é a normal desse plano, pela menor variância)."""
    a = np.array([tuple(p) for p in pts])
    a -= a.mean(0)
    _, _, vt = np.linalg.svd(a, full_matrices=False)
    u, v = vt[0], vt[1]
    menor = math.inf
    for k in range(90):
        th = math.pi * k / 90
        d = u * math.cos(th) + v * math.sin(th)
        proj = a @ d
        menor = min(menor, proj.max() - proj.min())
    return menor


def atravessa(pts, topo):
    """(a maior penetração da malha nela mesma em mm, o ponto) — ver o cabeçalho."""
    tris = topo.tris
    medidor = maos_contato.Medidor(topo.sup, pts)
    pior, onde = 0.0, None
    for a, b in maos_contato.pares(pts, tris, list(range(len(tris)))):
        ta, tb = tris[a], tris[b]
        pa, pb = topo.peca[a], topo.peca[b]
        if pa >= 0 and (pa == pb or (pb < 0 and b in topo.pegada[pa]) or (pa, pb) in topo.empilhadas):
            continue
        if pb >= 0 and pa < 0 and a in topo.pegada[pb]:
            continue
        d = medidor.par(a, b)
        if d > pior:
            pior, onde = d, (pts[ta[0]] + pts[tb[0]]) / 2
    return pior, onde


def _assentamento(pts, topo):
    """O maior desvio (mm) da base das paredes das peças em relação aos 0,2 mm dentro da luva, na pose."""
    if not topo.assento:
        return 0.0
    bvh = BVHTree.FromPolygons(pts, [topo.tris[k] for k in topo.base])
    return max(abs(bvh.find_nearest(pts[i])[3] - 0.2) for i in topo.assento)


def _parede_do_punho(pts, topo):
    """As distâncias (mm) de cada vértice do forro à face de fora da luva."""
    bvh = BVHTree.FromPolygons(pts, [topo.tris[k] for k in topo.fora])
    return np.array([bvh.find_nearest(pts[i])[3] for i in topo.forro])


class _Repouso:
    def __init__(self, modelo, topo):
        pts = modelo.pontos({})
        self.espessuras = {j: _espessura_minima([pts[i] for i in idx]) for j, idx in topo.juntas.items()}
        self.parede = _parede_do_punho(pts, topo) if topo.forro else None


def conferir_pose(modelo, topo, repouso, nome, pose, juntas=None):
    """{juntas: razão da espessura, pior junta, parede do punho, atravessa, assentamento} de uma pose e os problemas."""
    pts = modelo.pontos(pose)
    aneis = {j: idx for j, idx in topo.juntas.items() if juntas is None or j in juntas}
    razoes = {j: round(_espessura_minima([pts[i] for i in idx]) / repouso.espessuras[j], 4) for j, idx in aneis.items()}
    prof, onde = atravessa(pts, topo)
    assento = _assentamento(pts, topo)
    rel = {'juntas': razoes, 'atravessaMM': round(prof, 3), 'assentamentoMM': round(assento, 3)}
    problemas = []
    if razoes:
        pior = min(razoes, key=razoes.get)
        rel['piorJunta'] = [pior, razoes[pior]]
        if razoes[pior] < 1 - AFINAMENTO_MAXIMO:
            problemas.append(f'pose {nome}: a junta {pior} afina {(1 - razoes[pior]) * 100:.1f} % (máximo 30 %)')
    if repouso.parede is not None:
        parede = float((_parede_do_punho(pts, topo) / np.maximum(repouso.parede, 1e-6)).min())
        rel['paredeDoPunho'] = round(parede, 4)
        if parede < 1 - AFINAMENTO_MAXIMO:
            problemas.append(f'pose {nome}: a parede do punho afina {(1 - parede) * 100:.1f} % (máximo 30 %)')
    if onde is not None:
        rel['ondeAtravessa'] = [round(c, 2) for c in onde]
    if prof > ATRAVESSA_MM:
        problemas.append(f'pose {nome}: a luva atravessa a si mesma {prof:.2f} mm (máximo {ATRAVESSA_MM} mm)')
    if assento > ASSENTO_MM:
        problemas.append(f'pose {nome}: uma peça sai do assento {assento:.2f} mm (máximo {ASSENTO_MM} mm)')
    return rel, problemas


def validar_poses(luva, rig, mao, reforco, poses):
    """As poses de teste ({nome: pose}) e cada junta de flexão sozinha no limite da AAOS: (relatório, problemas)."""
    topo = Topologia(luva, reforco)
    modelo = maos_correcoes.Modelo(luva, rig, mao, reforco)
    repouso = _Repouso(modelo, topo)
    rel, problemas = {}, []
    for nome, pose in poses.items():
        rel[nome], p = conferir_pose(modelo, topo, repouso, nome, pose)
        problemas += p
    no_limite = {}
    for junta, osso, _rep, maximo, _meia, _alcance in maos_correcoes.juntas(mao):
        if junta.endswith('_mcp') and not junta.startswith('polegar'):
            continue
        r, p = conferir_pose(modelo, topo, repouso, f'{junta} no limite',
                             {osso: Quaternion((1.0, 0.0, 0.0), math.radians(maximo))}, juntas={junta})
        no_limite[junta] = {k: r[k] for k in ('atravessaMM', 'assentamentoMM') if k in r}
        no_limite[junta]['espessura'] = r['juntas'].get(junta)
        problemas += p
    rel['juntasNoLimite'] = no_limite
    maos_rig.posar(rig, {})
    return rel, problemas


def conferir_uma(modelo, luva, reforco, nome, pose):
    """Uma pose avulsa (a pega das armas, empunhadura_pega.py) nas mesmas contas das poses de teste: (relatório,
    problemas)."""
    topo = Topologia(luva, reforco)
    return conferir_pose(modelo, topo, _Repouso(modelo, topo), nome, pose)
```

```python file=tools/blender/armas/empunhadura.py
# Solver de empunhadura (Fase 4.1b; desenho em docs/superpowers/specs/2026-09-26-4.1b-luvas-e-empunhadura-design.md,
# seção 6.2): o núcleo que fecha a mão até encostar, sobre a luva de jogo com o rig e as correções das dobras (a malha
# avaliada pelo modelo das luvas, maos_correcoes.Modelo, em cada tentativa).
#  - fechar uma junta: a flexão por bisseção (tolerância 0,05°) entre o ângulo atual e o alvo, parando no maior ângulo
#    em que a parte que dobra (os triângulos dos ossos dela para baixo) não entra no obstáculo mais que 0,05 mm (o
#    contato). Na própria luva, o obstáculo é o resto dela, e só contam os pares de triângulos que estavam a mais de
#    12 mm um do outro no repouso: os que estavam perto são a pele da dobra de uma junta ou a membrana entre dois dedos
#    (as correções cuidam deles), não contato entre partes;
#  - vizinhos: se dois dedos se atravessam, o de fora (a partir do médio) abre na MCP até 20° para longe; se não bastar,
#    recua a flexão da MCP dele até separar. A abertura gira antes da flexão (o quaternion da pose é flexão · abertura):
#    o dedo abre no plano da palma e dobra em volta do eixo de flexão, e o afastamento da ponta continua com a MCP
#    fechada (girando depois, em 90° a abertura só torceria o dedo em volta dele mesmo);
#  - quem conta como obstáculo ao fechar um dedo: o resto da luva menos ele e os dedos vizinhos (o lado de um dedo
#    encostado no do vizinho é o passo dos vizinhos, não um limite da flexão);
# O polegar (a polpa num alvo e fechando até encostar) está em empunhadura_polegar.py, e as poses de teste das luvas
# que dependem de contato (o punho, o apontar e a mesa) em maos_poses.py. A pega das armas (a palma no soquete, as
# regras da categoria, a arma como obstáculo) usa este mesmo núcleo.
import math

from mathutils import Quaternion, Vector

from . import maos_contato, maos_correcoes
from .unidades import S

TOLERANCIA_GRAUS = 0.05
CONTATO_MM = 0.05
PERTO_MM = 12.0  # pares de triângulos a menos disso no repouso não são contato (dobra ou membrana)
DOBRA_MM = 22.0  # a membrana entre dois dedos: a pele a até 22 mm da MCP deles (o alcance da dobra da MCP)
ABERTURA_MAXIMA = 20.0
# o sinal da abertura (giro em Z) para longe do médio, na mão direita (a esquerda: para_fora)
_FORA = {'indicador': -1.0, 'anelar': 1.0, 'minimo': 1.0}
_VIZINHOS = {'indicador': ('medio',), 'medio': ('indicador', 'anelar'), 'anelar': ('medio', 'minimo'),
             'minimo': ('anelar',)}


def para_fora(dedo, lado):
    """O sinal da abertura que afasta o dedo do médio no lado `lado` ('d' ou 'e'): a luva esquerda é a direita
    espelhada, e o giro em Z do osso espelhado anda para o outro lado (na esquerda, o sinal da direita juntava os dedos
    em vez de afastar)."""
    return _FORA[dedo] * (1.0 if lado == 'd' else -1.0)


def _cadeia(d):
    return {f'{d}_{i}' for i in range(4)}


def _falanges(d):
    """Os ossos das falanges de um dedo (sem o metacarpo do anelar e do mínimo, que é palma)."""
    return {f'{d}_{i}' for i in range(1, 4)}


class Colisor:
    """A luva ligada ao rig para as perguntas de contato: os triângulos, o osso dominante de cada vértice e as cabeças
    dos ossos em repouso."""

    def __init__(self, luva, rig, mao, reforco):
        self.luva, self.rig = luva, rig
        self.modelo = maos_correcoes.Modelo(luva, rig, mao, reforco)
        me = luva.data
        me.calc_loop_triangles()
        self.tris = [tuple(t.vertices) for t in me.loop_triangles]
        self.sup = maos_contato.Superficie(self.tris)
        nomes = {g.index: g.name[:-2] for g in luva.vertex_groups}
        self.dono = []
        for v in me.vertices:
            w = {nomes[g.group]: g.weight for g in v.groups}
            self.dono.append(max(w, key=w.get) if w else '')
        self.dono_tri = [self._dono_do_tri(t) for t in self.tris]
        self.centro = [sum((me.vertices[i].co for i in t), Vector()) / (3 * S) for t in self.tris]
        self.lado = rig.name.rsplit('_', 1)[1]
        self.cabeca = {b.name[:-2]: Vector(b.head_local) / S for b in rig.data.bones}

    def _dono_do_tri(self, t):
        contagem = {}
        for i in t:
            contagem[self.dono[i]] = contagem.get(self.dono[i], 0) + 1
        return max(contagem, key=contagem.get)

    def triangulos(self, ossos, longe_de=()):
        """Os triângulos dominados pelos `ossos`, fora dos a até DOBRA_MM (em repouso) da cabeça dos ossos `longe_de`
        (a pele da dobra daquelas juntas)."""
        cs = [self.cabeca[o] for o in longe_de]
        return [k for k, o in enumerate(self.dono_tri)
                if o in ossos and all((self.centro[k] - c).length > DOBRA_MM for c in cs)]

    def abaixo(self, osso):
        """O osso e os de baixo dele (sem o lado)."""
        b = self.rig.data.bones[f'{osso}_{self.lado}']
        return {osso} | {c.name[:-2] for c in b.children_recursive}

    def profundidade(self, pose, A, B, perto_mm=0.0):
        """A maior penetração (mm) entre os triângulos A e os B na pose (maos_contato.py: cada superfície medida só com
        os triângulos do conjunto dela), sem os pares que estavam a menos de `perto_mm` um do outro no repouso."""
        if not A or not B:
            return 0.0
        pts = self.modelo.pontos(pose)
        medidor = maos_contato.Medidor(self.sup, pts)
        sa, sb = set(A), set(B)
        pior = 0.0
        for a, b in maos_contato.pares(pts, self.tris, A, B):
            if (self.centro[a] - self.centro[b]).length < perto_mm:
                continue
            pior = max(pior, medidor.par(a, b, sa, sb))
        return pior


def _flexao(graus):
    return Quaternion((1.0, 0.0, 0.0), math.radians(graus))


def _abertura(graus):
    return Quaternion((0.0, 0.0, 1.0), math.radians(graus))


def _rotacao(graus):
    return Quaternion((0.0, 1.0, 0.0), math.radians(graus))


def _bissecao(ok, de, ate):
    """O maior valor entre `de` (aceito) e `ate` com ok(valor), por bisseção até TOLERANCIA_GRAUS."""
    if ok(ate):
        return ate
    a, b = de, ate
    while abs(b - a) > TOLERANCIA_GRAUS:
        m = (a + b) / 2
        if ok(m):
            a = m
        else:
            b = m
    return a


class Mao:
    """Uma pose de mão sendo resolvida: flexão, abertura e rotação axial por osso (graus além do repouso). A rotação
    (em volta do Y do osso, a pronação do metacarpo do polegar) gira primeiro, depois a abertura, a flexão e o giro."""

    def __init__(self):
        self.flexao, self.aberturas, self.rotacoes = {}, {}, {}
        self.giros = {}  # osso → (eixo no referencial de repouso, graus), girado depois da flexão (a CMC do polegar)

    def pose(self):
        p = {}
        for osso in set(self.flexao) | set(self.aberturas) | set(self.giros) | set(self.rotacoes):
            q = (_flexao(self.flexao.get(osso, 0.0)) @ _abertura(self.aberturas.get(osso, 0.0))
                 @ _rotacao(self.rotacoes.get(osso, 0.0)))
            if osso in self.giros:
                eixo, graus = self.giros[osso]
                q = Quaternion(eixo, math.radians(graus)) @ q
            p[osso] = q
        return p

    def com(self, osso, flexao=None, abertura=None):
        m = Mao()
        m.flexao, m.aberturas, m.giros = dict(self.flexao), dict(self.aberturas), dict(self.giros)
        m.rotacoes = dict(self.rotacoes)
        if flexao is not None:
            m.flexao[osso] = flexao
        if abertura is not None:
            m.aberturas[osso] = abertura
        return m


def fechar(col, mao_pose, osso, alvo, obstaculo=None, na=None):
    """Fecha a junta `osso` do ângulo atual até `alvo` (graus além do repouso), parando no contato da parte que dobra
    com os triângulos `obstaculo` (o resto da luva, sem ele) e, com `na` (a luva na arma, empunhadura_arma.NaArma),
    com a arma. Devolve (nova pose, ângulo, encostou)."""
    A = col.triangulos(col.abaixo(osso))
    if obstaculo is None:
        dentro = set(A)
        obstaculo = [k for k in range(len(col.tris)) if k not in dentro]
    B = obstaculo
    de = mao_pose.flexao.get(osso, 0.0)
    vertices = na.vertices(col.abaixo(osso)) if na is not None else None

    def livre(g):
        pose = mao_pose.com(osso, flexao=g).pose()
        if col.profundidade(pose, A, B, PERTO_MM) > CONTATO_MM:
            return False
        return na is None or na.penetracao(na.pontos(pose), vertices) <= CONTATO_MM

    graus = _bissecao(livre, de, alvo)
    return mao_pose.com(osso, flexao=graus), graus, graus < alvo - TOLERANCIA_GRAUS


def separar_vizinhos(col, mao_pose, dedos):
    """Os dedos vizinhos (da lista, na ordem da mão) sem se atravessar: a partir do médio, o de fora abre na MCP até
    20° para longe; se não bastar, recua a flexão da MCP dele. Devolve (pose, {dedo: o que mudou})."""
    mudou = {}
    ordem = [('medio', 'anelar'), ('anelar', 'minimo'), ('medio', 'indicador')]
    for dentro, fora in ordem:
        if dentro not in dedos or fora not in dedos:
            continue
        # a pele entre os dois dedos, perto das MCP, é a membrana entre eles (as correções cuidam)
        longe = (f'{fora}_1', f'{dentro}_1')
        A = col.triangulos(_falanges(fora), longe)
        B = col.triangulos(_falanges(dentro), longe)
        osso = f'{fora}_1'
        if col.profundidade(mao_pose.pose(), A, B) <= CONTATO_MM:
            continue
        sinal = para_fora(fora, col.lado)
        ab0 = mao_pose.aberturas.get(osso, 0.0)

        def cruza_aberto(g):
            return col.profundidade(mao_pose.com(osso, abertura=ab0 + sinal * g).pose(), A, B) > CONTATO_MM

        if not cruza_aberto(ABERTURA_MAXIMA):
            a, b = 0.0, ABERTURA_MAXIMA  # a menor abertura que separa
            while b - a > TOLERANCIA_GRAUS:
                m = (a + b) / 2
                if cruza_aberto(m):
                    a = m
                else:
                    b = m
            mao_pose = mao_pose.com(osso, abertura=ab0 + sinal * b)
            mudou[fora] = {'abertura': round(sinal * b, 2)}
            continue
        # a abertura toda não basta: o de fora recua a MCP (a maior flexão, até a de agora, que separa)
        mao_pose = mao_pose.com(osso, abertura=ab0 + sinal * ABERTURA_MAXIMA)
        f0 = mao_pose.flexao.get(osso, 0.0)
        g = _bissecao(lambda f: col.profundidade(mao_pose.com(osso, flexao=f).pose(), A, B) <= CONTATO_MM, 0.0, f0)
        mao_pose = mao_pose.com(osso, flexao=g)
        mudou[fora] = {'abertura': round(sinal * ABERTURA_MAXIMA, 2), 'recuoMcp': round(f0 - g, 2)}
    return mao_pose, mudou

```

```python file=tools/blender/armas/empunhadura_polegar.py
# O polegar do solver de empunhadura (Fase 4.1b; desenho em docs/superpowers/specs/2026-09-26-4.1b-luvas-e-
# empunhadura-design.md, seção 6.2): a polpa do polegar num alvo — a superfície de outra parte da mão nas poses de teste
# (as costas das falanges médias no punho fechado), a da arma na pega — e o polegar pousando nele até encostar.
#  - o alvo: um ponto de superfície e a normal dela (para fora); nos dedos, o raio que sai do meio do osso da falange
#    média pelas costas dele (o −Z do osso na pose) até a superfície da luva posada (maos_correcoes.Modelo), saindo
#    pelo protetor de borracha se houver um por cima;
#  - a polpa: o ponto da superfície da luva na frente do osso distal do polegar, a 55 % dele (o raio de repouso pelo
#    lado da polpa, o +Z do osso), preso ao osso — o skin ali é todo do polegar_3;
#  - a IK: os cinco graus do polegar — a abdução palmar, a flexão e a rotação axial da CMC (a pronação que acompanha a
#    oposição, Cooney 1981), a flexão da MCP e a da IP — dentro dos limites da ficha, pela cinemática da cadeia (as
#    matrizes de repouso dos ossos e a da mão posada, sem o Blender a cada tentativa), minimizando a distância da polpa
#    ao alvo, o desvio da polpa de ficar de frente para ele (15 mm por unidade de 1 + cos entre o lado da polpa e a
#    normal do alvo) e a entrada do polegar nos dedos (5 mm por mm de penetração entre as cápsulas de maos_capsulas.py,
#    com a seção achatada medida na luva, e 1 mm de tolerância para o encosto no alvo); uma grade de 10° (a rotação em
#    três passos) e depois a busca de padrão até 0,25°. Sem as cápsulas, a IK passava a falange proximal do polegar pela
#    ponta do indicador, que no punho fica escondida contra a palma por trás do polegar;
#  - o contato, pela malha: o polegar chega pela normal do alvo, como quem pousa o dedo — a mesma IK, local, a partir
#    da solução, com a polpa 6 mm acima do alvo (12, 18, 24 mm se ali ainda cruzar a mão), e os cinco graus seguindo
#    em linha dessa pose até a do alvo e metade além, parando no contato (bisseção até 0,05° no grau que mais anda);
#    depois, assenta: a MCP e a IP fecham até encostar (o primeiro toque costuma ser a falange proximal deitando no
#    indicador; a MCP leva o polegar por cima dos dedos e a IP desce a polpa sobre eles — com a IP primeiro, ela ia ao
#    limite no ar e o polegar virava um gancho);
#  - o relatório traz os ângulos totais, os da IK, o encosto do lado da polpa (a menor distância dos vértices do osso
#    distal do lado da polpa, o +Z dele no repouso, à superfície do alvo — os triângulos dele na pose; um ponto só, o
#    centro da polpa, cai no vão entre dois dedos quando o polegar deita de través sobre eles), a distância do centro
#    da polpa ao ponto do alvo, se encostou e de que altura chegou.
#  - na pega das armas (empunhadura_pega.py), a arma entra: na IK, os três ossos do polegar como cápsulas de seção
#    medida contra a superfície dela, e depois um refino pela busca de padrão com a entrada de verdade dos vértices do
#    polegar e da tenar (a malha refeita a cada avaliação: a pele da tenar não cabe na cápsula do metacarpo); o alvo,
#    quando a regra pede um lado (o polegar direito cruzando para o lado esquerdo do punho), é escolhido pela própria
#    IK — a polpa encostada na arma, de frente para ela, o mais longe possível para aquele lado (alvo_na_arma); e o
#    polegar assenta sem caminho de chegada (_assentar_na_arma): erguido pela normal ele dava ainda mais a volta e
#    cruzava o punho;
#  - na mão da frente (deitar_na_arma), o polegar deita reto na face do lado dele, apontando para a boca, como na pega
#    "thumb break" (os quatro dedos por baixo do guarda-mão e o polegar esticado ao longo do lado, apontando para o
#    alvo): a IK zera a folga das falanges proximal e distal para a arma ao longo do comprimento (quatro pontos em cada,
#    pela cápsula de seção medida), aponta as duas para o `eixo` e cobra a curva (a MCP mais a IP) além de CURVA_LIVRE; a
#    polpa num ponto, na primeira versão, deixava a CMC no limite da extensão e o polegar dobrado em arco (MCP 35°, IP
#    17°), só com a ponta encostada. O relatório traz a folga medida na malha ao longo do comprimento (`coladoMM`, o pior
#    trecho) e a curva (`curvaGraus`).
# Unidades: mm e graus além do repouso (os totais no relatório); o rig em metros no Blender.
import itertools
import math

from mathutils import Quaternion, Vector
from mathutils.bvhtree import BVHTree

from . import empunhadura, maos_capsulas, maos_rig
from .maos import DEDOS4
from .maos_capsulas import mm
from .unidades import S

OSSOS = ('polegar_1', 'polegar_2', 'polegar_3')
GRAUS = ('abducao', 'cmc', 'rotacao', 'mcp', 'ip')
PESO_NORMAL_MM = 15.0
PESO_COLISAO = 5.0
TOLERANCIA_ENCOSTO_MM = 1.0
GRADE_GRAUS = 10.0
PASSO_INICIAL = 5.0
PASSO_FINAL = 0.25
POLPA_T = 0.55
CAMADA_MM = 4.0  # até onde o raio segue saindo por peças por cima da superfície (o protetor de borracha)
ACIMA_MM = (6.0, 12.0, 18.0, 24.0)  # as alturas da chegada, pela normal do alvo
ALEM = 0.5  # o caminho segue além da pose do alvo (a fração dele) até encostar
LIVRE = ('polegar_2', 'polegar_3')  # a parte do polegar que sai da mão (o metacarpo é a tenar, palma)
DEDOS = tuple(f'{d}_{i}' for d in DEDOS4 for i in (1, 2, 3))  # as cápsulas dos dedos que o polegar não atravessa
TENAR = ('polegar_1', 'mao')  # a tenar: com o polegar (LIVRE), os vértices do refino pela malha na pega
PASSO_REFINO = 2.0
PESO_MALHA = 30.0  # a entrada da malha do polegar e da tenar na arma, no refino: praticamente uma restrição
PESO_EIXO_MM = 20.0  # uma falange fora do eixo pedido (mão da frente): mm por unidade de 1 − cos
PONTOS_DEITADO = (0.15, 0.4, 0.65, 0.9)  # ao longo da falange proximal e da distal, na conta da folga do polegar deitado
CURVA_LIVRE = 12.0  # graus da MCP mais a IP que o polegar deitado dobra sem custo (o polegar relaxado não fica reto)
PESO_CURVA_MM = 0.6  # mm de custo por grau de curva além da livre
TRECHOS_DEITADO = ((0.1, 0.4), (0.4, 0.7), (0.7, 0.95))  # os trechos de cada falange na folga medida na malha
# a folga (mm) que a IK do polegar deitado mira: a cápsula é uma média da seção, e a malha encostada nela a 0 entra na
# arma; a primeira que não cruza a arma nem a mão vale
FOLGAS_DEITADO = (0.3, 0.6, 1.0, 1.5)
PESO_FACE_MM = 20.0  # o polegar deitado fora da face do lado dele: mm por unidade de 1 − cos entre as normais


def limites(mao):
    """{grau: (mínimo, máximo)} dos cinco graus do polegar além do repouso: a AAOS da ficha menos o repouso (a CMC
    tem a flexão de repouso zero; o polegar de repouso está na abdução palmar e nas flexões da ficha) e a rotação axial
    da CMC (Cooney, do repouso para a pronação)."""
    lim, rep = mao.f['limites']['polegar'], mao.rep
    rot = mao.f['rotacaoDoPolegar']['cmc']
    return {'abducao': (lim['cmcAbducao'][0] - rep['polegarAbducao'], lim['cmcAbducao'][1] - rep['polegarAbducao']),
            'cmc': (float(lim['cmcFlexao'][0]), float(lim['cmcFlexao'][1])), 'rotacao': (float(rot[0]), float(rot[1])),
            'mcp': (lim['mcp'][0] - rep['polegarMcp'], lim['mcp'][1] - rep['polegarMcp']),
            'ip': (lim['ip'][0] - rep['polegarIp'], lim['ip'][1] - rep['polegarIp'])}


def totais(mao, g):
    """Os graus do polegar (além do repouso) em ângulos totais na junta, arredondados para o relatório."""
    rep = mao.rep
    return {'abducao': round(g['abducao'] + rep['polegarAbducao'], 2), 'cmc': round(g['cmc'], 2),
            'rotacao': round(g['rotacao'], 2), 'mcp': round(g['mcp'] + rep['polegarMcp'], 2),
            'ip': round(g['ip'] + rep['polegarIp'], 2)}


def _malha(pts, tris):
    return BVHTree.FromPolygons([tuple(p) for p in pts], tris)


def _para_fora(bvh, origem, direcao):
    """O ponto da superfície na saída do raio de dentro da luva: a primeira face que ele cruza e, se houver uma peça por
    cima (o protetor de borracha, até CAMADA_MM adiante), a face de fora dela."""
    co, _n, _i, _d = bvh.ray_cast(origem, direcao)
    if co is None:
        raise RuntimeError(f'o raio de {tuple(round(c, 1) for c in origem)} não sai da luva')
    while True:
        prox, _n, _i, _d = bvh.ray_cast(co + direcao * 0.01, direcao, CAMADA_MM)
        if prox is None:
            return co
        co = prox


class Cadeia:
    """A cadeia do polegar para a IK: a mão posada (o pai do polegar_1 e as cápsulas dos dedos), as matrizes de repouso
    dos três ossos (mm), o eixo e o sinal da abdução, a polpa no referencial do osso distal e as seções das cápsulas."""

    def __init__(self, col, mao, pose_mao):
        rig, lado = col.rig, col.lado
        self.eixo_ab, self.sinal_ab = maos_rig.eixo_abducao_do_polegar(mao, rig)
        ossos = [rig.data.bones[f'{o}_{lado}'] for o in OSSOS]
        rep = [mm(b.matrix_local) for b in ossos]
        pai = ossos[0].parent
        self.rel = [mm(pai.matrix_local).inverted() @ rep[0], rep[0].inverted() @ rep[1], rep[1].inverted() @ rep[2]]
        self.comp = [b.length / S for b in ossos]
        self.secoes = maos_capsulas.Secoes(col)
        maos_rig.posar(rig, pose_mao)
        self.pai = mm(rig.pose.bones[pai.name].matrix)
        self.dedos = []
        for o in DEDOS:
            pb = rig.pose.bones[f'{o}_{lado}']
            self.dedos.append(maos_capsulas.Capsula(self.secoes, o, mm(pb.matrix), pb.bone.length / S))
        maos_rig.posar(rig, {})
        # a polpa de repouso: do meio do osso distal (a 55 %) pelo lado da polpa até a superfície da luva de repouso
        bvh = _malha(col.modelo.pontos({}), col.tris)
        m3 = rep[2]
        dentro = m3 @ Vector((0.0, self.comp[2] * POLPA_T, 0.0))
        lado_da_polpa = (m3.to_3x3() @ Vector((0.0, 0.0, 1.0))).normalized()
        self.polpa = m3.inverted() @ _para_fora(bvh, dentro, lado_da_polpa)
        # os vértices do lado da polpa do osso distal (os de que ele é o dono, com o +Z do osso para fora no repouso)
        para_local = m3.inverted()
        pts = col.modelo.pontos({})
        self.lado_da_polpa = [i for i, dono in enumerate(col.dono) if dono == OSSOS[2] and (para_local @ pts[i]).z > 0.0]

    def rotacoes(self, g):
        """{osso: quaternion} do polegar com os graus `g` (além do repouso): a CMC gira a pronação (em volta do
        próprio metacarpo; na mão direita, negativa no Y do osso), a flexão e depois a abdução (em volta do eixo preso à
        palma), como empunhadura.Mao.pose."""
        q1 = (Quaternion(self.eixo_ab, math.radians(self.sinal_ab * g['abducao'])) @ empunhadura._flexao(g['cmc'])
              @ empunhadura._rotacao(-self.sinal_ab * g['rotacao']))
        return {'polegar_1': q1, 'polegar_2': empunhadura._flexao(g['mcp']), 'polegar_3': empunhadura._flexao(g['ip'])}

    def matrizes(self, g):
        """As matrizes dos três ossos do polegar (mm) com os graus `g`."""
        q = self.rotacoes(g)
        m, ms = self.pai, []
        for rel, osso in zip(self.rel, OSSOS):
            m = m @ rel @ q[osso].to_matrix().to_4x4()
            ms.append(m)
        return ms

    def polpa_em(self, g, ms=None):
        """(o ponto da polpa, o lado da polpa) com os graus `g`."""
        m = (ms or self.matrizes(g))[2]
        return m @ self.polpa, (m.to_3x3() @ Vector((0.0, 0.0, 1.0))).normalized()

    def penetracao(self, ms):
        """A soma dos quadrados das entradas (mm, além da tolerância do encosto) das cápsulas da falange proximal e da
        distal do polegar nas dos dedos."""
        soma = 0.0
        for k in (1, 2):
            polegar = maos_capsulas.Capsula(self.secoes, OSSOS[k], ms[k], self.comp[k])
            for dedo in self.dedos:
                entra = maos_capsulas.encosto(self.secoes, polegar, dedo) - TOLERANCIA_ENCOSTO_MM
                if entra > 0.0:
                    soma += entra * entra
        return soma


def alvo_nas_falanges(col, pose, pesos):
    """(ponto, normal para fora) do alvo nas costas das falanges médias dos dedos de `pesos` ({dedo: peso}) na pose: a
    média ponderada dos pontos de saída dos raios pelas costas de cada uma e das direções deles."""
    rig, lado = col.rig, col.lado
    maos_rig.posar(rig, pose)
    bvh = _malha(col.modelo.pontos(pose), col.tris)
    ponto, normal, soma = Vector(), Vector(), 0.0
    for dedo, peso in pesos.items():
        pb = rig.pose.bones[f'{dedo}_2_{lado}']
        m = mm(pb.matrix)
        meio = m @ Vector((0.0, pb.bone.length / S * 0.5, 0.0))
        costas = -(m.to_3x3() @ Vector((0.0, 0.0, 1.0))).normalized()
        ponto += _para_fora(bvh, meio, costas) * peso
        normal += costas * peso
        soma += peso
    maos_rig.posar(rig, {})
    return ponto / soma, normal.normalized()


def _entrada_na_arma(cadeia, ms, na):
    """A soma dos quadrados das entradas (mm, além da tolerância do encosto) dos três ossos do polegar na arma, como
    cápsulas de seção medida (maos_capsulas.py): em cinco pontos do eixo de cada um, o raio da seção na direção da
    superfície mais perto contra a distância a ela (o eixo dentro da arma soma a profundidade). O metacarpo entra: sem
    ele, a abdução levava a tenar para dentro das costas do punho."""
    soma = 0.0
    for k, osso in enumerate(OSSOS):
        m = na.encaixe @ ms[k]
        para_local = m.to_3x3().inverted()
        alcance = cadeia.secoes.maior(osso) + 2.0
        for t in (0.1, 0.3, 0.5, 0.7, 0.9):
            q = m @ Vector((0.0, cadeia.comp[k] * t, 0.0))
            r = na.arma.bvh.find_nearest(q, alcance)
            if r[0] is None:
                continue
            co, n, _i, d = r
            dentro = (q - co).dot(n) < 0.0
            direcao = (q - co) if dentro else (co - q)
            if direcao.length < 1e-9:
                direcao = -n
            raio = cadeia.secoes.raio(osso, para_local @ direcao)
            entra = (raio + d if dentro else raio - d) - TOLERANCIA_ENCOSTO_MM
            if entra > 0.0:
                soma += entra * entra
    return soma


def _direcao_distal(ms):
    """Para onde aponta a falange distal (o +Y do osso), unitária, no referencial das matrizes."""
    return (ms[2].to_3x3() @ Vector((0.0, 1.0, 0.0))).normalized()


def _custo(cadeia, g, alvo, normal, na=None, eixo=None):
    ms = cadeia.matrizes(g)
    p, lado = cadeia.polpa_em(g, ms)
    c = ((p - alvo).length_squared + (PESO_NORMAL_MM * (1.0 + lado.dot(normal))) ** 2
         + PESO_COLISAO ** 2 * cadeia.penetracao(ms))
    if na is not None:
        c += PESO_COLISAO ** 2 * _entrada_na_arma(cadeia, ms, na)
    if eixo is not None:
        c += (PESO_EIXO_MM * (1.0 - _direcao_distal(ms).dot(eixo))) ** 2
    return c


def _padrao(custo_de, lim, melhor, custo, passo=PASSO_INICIAL):
    while passo >= PASSO_FINAL:
        melhorou = False
        for grau in GRAUS:
            for s in (1.0, -1.0):
                g = dict(melhor)
                g[grau] = min(max(g[grau] + s * passo, lim[grau][0]), lim[grau][1])
                c = custo_de(g)
                if c < custo - 1e-9:
                    melhor, custo, melhorou = g, c, True
        if not melhorou:
            passo /= 2
    return melhor


def minimizar(custo_de, lim, inicio=None):
    """Os graus do polegar (além do repouso) de menor `custo_de(g)`: a grade de 10° (a rotação em três passos) e a busca
    de padrão até 0,25° (só a busca, a partir de `inicio`, se vier: a solução perto de outra)."""
    def valores(a, b):
        n = max(1, math.ceil((b - a) / GRADE_GRAUS))
        return [a + (b - a) * k / n for k in range(n + 1)]

    melhor, custo = None, math.inf
    if inicio is not None:
        melhor, custo = dict(inicio), custo_de(inicio)
    else:
        for combinacao in itertools.product(*(valores(*lim[k]) for k in GRAUS)):
            g = dict(zip(GRAUS, combinacao))
            c = custo_de(g)
            if c < custo:
                melhor, custo = g, c
    return _padrao(custo_de, lim, melhor, custo)


def _tenar(na, m, cadeia, g, vertices):
    """A soma dos quadrados das entradas (mm) dos vértices da tenar (o metacarpo do polegar e a palma) na arma, com o
    polegar nos graus `g` — a malha de verdade (maos_correcoes.Modelo), para o refino da IK na pega."""
    return na.entrada_quadrada(na.pontos(_com_graus(m, cadeia, g).pose()), vertices)


def refinar_na_malha(custo_de, lim, g, na, m, cadeia):
    """A busca de padrão, a partir da solução das cápsulas, com a entrada da tenar na arma medida na malha: a pele da
    tenar não cabe na cápsula do metacarpo, e a abdução no máximo a levava 5 mm para dentro das costas do punho. Só a
    busca (cada avaliação refaz a luva, 18 ms)."""
    vertices = na.vertices(LIVRE + TENAR)

    def com_malha(gg):
        return custo_de(gg) + PESO_MALHA ** 2 * _tenar(na, m, cadeia, gg, vertices)

    return _padrao(com_malha, lim, g, com_malha(g), passo=PASSO_REFINO)


def resolver(cadeia, alvo, normal, lim, inicio=None, na=None, m=None, eixo=None):
    """Os graus do polegar (além do repouso) que põem a polpa no alvo, de frente para ele e fora dos dedos (e da arma,
    com `na`, a luva na arma de empunhadura_arma.NaArma, e a pose da mão `m`: aí o refino pela malha da tenar); com o
    `eixo` (unitário, no referencial da luva), a falange distal apontando para ele."""
    def custo_de(g):
        return _custo(cadeia, g, alvo, normal, na, eixo)

    g = minimizar(custo_de, lim, inicio)
    return g if na is None else refinar_na_malha(custo_de, lim, g, na, m, cadeia)


def alvo_na_arma(cadeia, na, m, lim, lado, peso_lado):
    """O alvo da polpa do polegar na arma, quando a regra pede um lado e não um ponto (o polegar cruzando para o lado
    esquerdo do punho): os graus que põem a polpa encostada na superfície da arma (a distância com sinal a ela, dentro
    pesando o dobro), de frente para ela, fora dos dedos e da arma, e o mais longe possível na direção `lado` (unitária,
    no referencial da arma; `peso_lado` mm² de custo por mm andado). Devolve (ponto da superfície mais perto da polpa,
    normal dela), no referencial da luva — o alvo do fechar_no_alvo, que o polegar alcança."""
    inv = na.encaixe.inverted()
    rot_inv = inv.to_3x3()

    def custo_de(g):
        ms = cadeia.matrizes(g)
        p, lado_polpa = cadeia.polpa_em(g, ms)
        q = na.encaixe @ p
        co, n, _i, d = na.arma.bvh.find_nearest(q)
        dentro = (q - co).dot(n) < 0.0
        normal = (rot_inv @ n).normalized()
        return ((2.0 * d if dentro else d) ** 2 + (PESO_NORMAL_MM * (1.0 + lado_polpa.dot(normal))) ** 2
                + PESO_COLISAO ** 2 * (cadeia.penetracao(ms) + _entrada_na_arma(cadeia, ms, na))
                - peso_lado * q.dot(lado))

    g = refinar_na_malha(custo_de, lim, minimizar(custo_de, lim), na, m, cadeia)
    p, _l = cadeia.polpa_em(g)
    co, n, _i, _d = na.arma.bvh.find_nearest(na.encaixe @ p)
    return inv @ co, (rot_inv @ n).normalized()


def _folgas_na_arma(cadeia, ms, na):
    """(folga, normal) das falanges proximal e distal do polegar para a arma em PONTOS_DEITADO de cada uma: a folga
    (mm, > 0 afastado, < 0 entrando) é a distância do eixo à superfície menos o raio da seção medida na direção dela, e a
    normal é a da face mais perto (unitária, no referencial da arma)."""
    folgas = []
    for k in (1, 2):
        m = na.encaixe @ ms[k]
        para_local = m.to_3x3().inverted()
        for t in PONTOS_DEITADO:
            q = m @ Vector((0.0, cadeia.comp[k] * t, 0.0))
            co, n, _i, d = na.arma.bvh.find_nearest(q)
            dentro = (q - co).dot(n) < 0.0
            direcao = (q - co) if dentro else (co - q)
            if direcao.length < 1e-9:
                direcao = -n
            raio = cadeia.secoes.raio(OSSOS[k], para_local @ direcao)
            folgas.append(((-d if dentro else d) - raio, n))
    return folgas


def colado_na_malha(col, na, pts):
    """A folga (mm) do polegar deitado medida na malha: em cada trecho de TRECHOS_DEITADO da falange proximal e da
    distal, a menor distância dos vértices do trecho à arma (o lado que encosta). Devolve a lista, da base para a
    ponta."""
    rig, lado = col.rig, col.lado
    trechos = []
    repouso = col.modelo.pontos({})
    for osso in LIVRE:
        b = rig.data.bones[f'{osso}_{lado}']
        cabeca, cauda = Vector(b.head_local) / S, Vector(b.tail_local) / S
        eixo = cauda - cabeca
        comp2 = eixo.length_squared
        indices = [i for i, dono in enumerate(col.dono) if dono == osso]
        for a, z in TRECHOS_DEITADO:
            trecho = [i for i in indices if a <= (Vector(repouso[i]) - cabeca).dot(eixo) / comp2 < z]
            if trecho:
                trechos.append(round(min(na.arma.distancia(pts[i]) for i in trecho), 2))
    return trechos


def deitar_na_arma(col, mao, m, na, eixo, face):
    """O polegar da mão da frente deitado reto na arma (ver o cabeçalho): a pose `m` com o polegar resolvido e o
    relatório (os graus totais, a folga ao longo do comprimento medida na malha, a curva e o desvio das falanges do
    `eixo`, unitário no referencial da luva), na face do lado `face` (unitária, no referencial da arma: a normal da
    superfície mais perto de cada trecho do polegar tem de ser ela, senão ele deita na face de baixo, ao lado do
    indicador). Se a solução ainda entrar mais que o contato, a MCP e a IP abrem juntas até
    soltar (o polegar fica mais reto, nunca mais curvo)."""
    lim = limites(mao)
    rep = mao.rep
    cadeia = Cadeia(col, mao, {o: q for o, q in m.pose().items() if not o.startswith('polegar')})

    def custo_de(g, folga_alvo=0.0):
        ms = cadeia.matrizes(g)
        c = 0.0
        for f, n in _folgas_na_arma(cadeia, ms, na):
            c += (f - folga_alvo) ** 2 + (PESO_FACE_MM * (1.0 - n.dot(face))) ** 2
        c += PESO_COLISAO ** 2 * (cadeia.penetracao(ms) + _entrada_na_arma(cadeia, ms, na))
        for k in (1, 2):
            c += (PESO_EIXO_MM * (1.0 - (ms[k].to_3x3() @ Vector((0.0, 1.0, 0.0))).normalized().dot(eixo))) ** 2
        curva = g['mcp'] + rep['polegarMcp'] + g['ip'] + rep['polegarIp'] - CURVA_LIVRE
        if curva > 0.0:
            c += (PESO_CURVA_MM * curva) ** 2
        return c

    livre, resto = _livre_e_resto(col)
    inicio = minimizar(custo_de, lim)
    for folga_alvo in FOLGAS_DEITADO:
        g = refinar_na_malha(lambda gg: custo_de(gg, folga_alvo), lim, inicio, na, m, cadeia)
        if not _cruza(col, _com_graus(m, cadeia, g), livre, resto, na):
            break
    if _cruza(col, _com_graus(m, cadeia, g), livre, resto, na):
        aberto = dict(g, mcp=lim['mcp'][0], ip=lim['ip'][0])
        if _cruza(col, _com_graus(m, cadeia, aberto), livre, resto, na):
            pose = _com_graus(m, cadeia, aberto).pose()
            na_mao = col.profundidade(pose, livre, resto, empunhadura.PERTO_MM)
            na_arma = na.penetracao(na.pontos(pose), na.vertices(LIVRE + TENAR))
            raise RuntimeError(f'o polegar deitado cruza a mão ({na_mao:.2f} mm) ou a arma ({na_arma:.2f} mm), mesmo com '
                               f'a MCP e a IP abertas (graus {totais(mao, aberto)})')
        anda = max(abs(g[k] - aberto[k]) for k in GRAUS)
        tolerancia = empunhadura.TOLERANCIA_GRAUS / max(anda, 1e-6)
        a, b = 0.0, 1.0  # a entra, b solta
        while b - a > tolerancia:
            s = (a + b) / 2
            if _cruza(col, _com_graus(m, cadeia, {k: g[k] + (aberto[k] - g[k]) * s for k in GRAUS}), livre, resto, na):
                a = s
            else:
                b = s
        g = {k: g[k] + (aberto[k] - g[k]) * b for k in GRAUS}
    m = _com_graus(m, cadeia, g)
    pts = na.pontos(m.pose())
    ms = cadeia.matrizes(g)
    desvio = max(math.degrees(math.acos(max(-1.0, min(1.0, (ms[k].to_3x3() @ Vector((0.0, 1.0, 0.0))).normalized()
                                                         .dot(eixo))))) for k in (1, 2))
    t = totais(mao, g)
    trechos = colado_na_malha(col, na, pts)
    rel = {'graus': t, 'coladoMM': max(trechos), 'trechosMM': trechos, 'curvaGraus': round(t['mcp'] + t['ip'], 1),
           'desvioDoEixoGraus': round(desvio, 1), 'polpaEncostaMM': round(na.encosto(pts, cadeia.lado_da_polpa), 2)}
    return m, rel


def graus_da_pose(m, cadeia):
    """Os graus do polegar numa pose da mão feita por _com_graus (ou por afastar): a leitura de volta."""
    return {'abducao': cadeia.sinal_ab * m.giros['polegar_1'][1] if 'polegar_1' in m.giros else 0.0,
            'cmc': m.flexao.get('polegar_1', 0.0), 'rotacao': -cadeia.sinal_ab * m.rotacoes.get('polegar_1', 0.0),
            'mcp': m.flexao.get('polegar_2', 0.0), 'ip': m.flexao.get('polegar_3', 0.0)}


def _com_graus(m, cadeia, g):
    """A pose da mão `m` com o polegar nos graus `g`."""
    m = m.com('polegar_1', flexao=g['cmc']).com('polegar_2', flexao=g['mcp']).com('polegar_3', flexao=g['ip'])
    m.giros['polegar_1'] = (cadeia.eixo_ab, cadeia.sinal_ab * g['abducao'])
    m.rotacoes['polegar_1'] = -cadeia.sinal_ab * g['rotacao']
    return m


def _livre_e_resto(col):
    livre = col.triangulos(set(LIVRE))
    dentro = set(livre)
    return livre, [k for k in range(len(col.tris)) if k not in dentro]


def _cruza(col, m, livre, resto, na=None):
    if col.profundidade(m.pose(), livre, resto, empunhadura.PERTO_MM) > empunhadura.CONTATO_MM:
        return True
    return na is not None and na.penetracao(na.pontos(m.pose()), na.vertices(LIVRE + TENAR)) > empunhadura.CONTATO_MM


def _assentar_na_arma(col, lim, m, cadeia, ik, livre, resto, na):
    """O polegar da solução da IK na arma, sem caminho de chegada: a IK já foi refinada na malha (o polegar e a tenar
    contra a arma), então a solução encosta; se ainda entrar mais que o contato, a MCP e a IP abrem juntas, em linha
    para o mínimo da AAOS, até soltar (bisseção). Depois as duas fecham até encostar, a MCP primeiro. Erguido pela
    normal do alvo (a face do outro lado do punho), o polegar teria de dar ainda mais a volta e cruzava; em linha do
    polegar afastado, a ponta batia no receptor antes de chegar atrás do punho; esticado com a CMC da solução, ele
    atravessava o punho. Devolve (pose, graus, encostou)."""
    aberto = dict(ik, mcp=lim['mcp'][0], ip=lim['ip'][0])

    def em(s):
        return {k: ik[k] + (aberto[k] - ik[k]) * s for k in GRAUS}

    if _cruza(col, _com_graus(m, cadeia, ik), livre, resto, na):
        if _cruza(col, _com_graus(m, cadeia, aberto), livre, resto, na):
            raise RuntimeError('o polegar da solução cruza a arma ou a mão, mesmo com a MCP e a IP abertas')
        anda = max(abs(ik[k] - aberto[k]) for k in GRAUS)
        tolerancia = empunhadura.TOLERANCIA_GRAUS / max(anda, 1e-6)
        a, b = 0.0, 1.0  # a entra, b solta
        while b - a > tolerancia:
            s = (a + b) / 2
            if _cruza(col, _com_graus(m, cadeia, em(s)), livre, resto, na):
                a = s
            else:
                b = s
        g = em(b)
    else:
        g = dict(ik)
    m = _com_graus(m, cadeia, g)
    encostou = False
    for grau, osso in (('mcp', 'polegar_2'), ('ip', 'polegar_3')):
        m, g[grau], enc = empunhadura.fechar(col, m, osso, lim[grau][1], na=na)
        encostou = encostou or enc
    return m, g, encostou


def fechar_no_alvo(col, mao, m, alvo, normal, superficie, na=None, eixo=None):
    """O polegar da pose `m` com a polpa no alvo, chegando pela normal dele até encostar e assentando pela IP e pela
    MCP; `superficie` são os triângulos da luva em que a polpa deve assentar (nas poses de teste). Na pega, `na` é a
    luva na arma (empunhadura_arma.NaArma): o alvo e a normal vêm no referencial da luva, a arma entra na IK e no
    contato e o encosto da polpa é medido nela; o `eixo` (a mão da frente, no referencial da luva) é para onde a
    falange distal aponta. Devolve (pose, relatório): os graus totais, os da IK, a distância da polpa à superfície e ao
    ponto do alvo (mm), se encostou, a altura de onde chegou (mm) e, com o `eixo`, o desvio da falange distal (graus)."""
    lim = limites(mao)
    cadeia = Cadeia(col, mao, {o: q for o, q in m.pose().items() if not o.startswith('polegar')})
    ik = resolver(cadeia, alvo, normal, lim, na=na, m=m, eixo=eixo)
    livre, resto = _livre_e_resto(col)
    if na is not None:
        m, g, encostou = _assentar_na_arma(col, lim, m, cadeia, ik, livre, resto, na)
        acima = None
    else:
        for acima in ACIMA_MM:
            de = resolver(cadeia, alvo + normal * acima, normal, lim, inicio=ik)
            if not _cruza(col, _com_graus(m, cadeia, de), livre, resto):
                break
        else:
            raise RuntimeError(f'o polegar cruza a mão mesmo com a polpa {ACIMA_MM[-1]} mm acima do alvo')

        def em(s):
            return {k: min(max(de[k] + (ik[k] - de[k]) * s, lim[k][0]), lim[k][1]) for k in GRAUS}

        anda = max(abs(ik[k] - de[k]) for k in GRAUS)
        tolerancia = empunhadura.TOLERANCIA_GRAUS / max(anda, 1e-6)
        a, b = 0.0, 1.0 + ALEM
        if _cruza(col, _com_graus(m, cadeia, em(b)), livre, resto):
            while b - a > tolerancia:
                s = (a + b) / 2
                if _cruza(col, _com_graus(m, cadeia, em(s)), livre, resto):
                    b = s
                else:
                    a = s
            encostou = True
        else:
            a, encostou = b, False
        g = em(a)
        m = _com_graus(m, cadeia, g)
        for grau, osso in (('mcp', 'polegar_2'), ('ip', 'polegar_3')):
            m, g[grau], enc = empunhadura.fechar(col, m, osso, lim[grau][1])
            encostou = encostou or enc
    polpa, _lado = cadeia.polpa_em(g)
    if na is None:
        pts = col.modelo.pontos(m.pose())
        bvh = _malha(pts, [col.tris[k] for k in superficie])
        encosto = min(bvh.find_nearest(pts[i])[3] for i in cadeia.lado_da_polpa)
    else:
        encosto = na.encosto(na.pontos(m.pose()), cadeia.lado_da_polpa)
    rel = {'graus': totais(mao, g), 'ik': totais(mao, ik), 'polpaEncostaMM': round(encosto, 2),
           'polpaAoAlvoMM': round((polpa - alvo).length, 2), 'encostou': encostou, 'chegouDeMM': acima}
    if eixo is not None:
        cosseno = max(-1.0, min(1.0, _direcao_distal(cadeia.matrizes(g)).dot(eixo)))
        rel['desvioDoEixoGraus'] = round(math.degrees(math.acos(cosseno)), 1)
    return m, rel


def afastar(col, mao, m):
    """O polegar fora do caminho dos dedos que vão fechar (o começo do punho): para o lado, no plano da palma — a
    abdução palmar e a flexão da CMC no mínimo da AAOS (a extensão), a MCP e a IP esticadas. Erguido para a frente da
    palma (a abdução palmar no máximo), ficava no caminho da ponta do indicador, que não dobrava."""
    lim = limites(mao)
    eixo, sinal = maos_rig.eixo_abducao_do_polegar(mao, col.rig)
    m = m.com('polegar_1', flexao=lim['cmc'][0]).com('polegar_2', flexao=lim['mcp'][0])
    m = m.com('polegar_3', flexao=lim['ip'][0])
    m.giros['polegar_1'] = (eixo, sinal * lim['abducao'][0])
    return m


def abrir(col, mao, m):
    """O polegar fora do caminho dos dedos (a mesa): a MCP e a IP no mínimo da AAOS e, se ainda cruzar a mão, a CMC
    estendendo até soltar. Devolve (pose, relatório com os graus totais)."""
    lim = limites(mao)
    cadeia = Cadeia(col, mao, {o: q for o, q in m.pose().items() if not o.startswith('polegar')})
    g = {'abducao': 0.0, 'cmc': 0.0, 'rotacao': 0.0, 'mcp': lim['mcp'][0], 'ip': lim['ip'][0]}
    livre, resto = _livre_e_resto(col)

    def solto(cmc):
        return not _cruza(col, _com_graus(m, cadeia, {**g, 'cmc': cmc}), livre, resto)

    if not solto(g['cmc']):
        if not solto(lim['cmc'][0]):
            raise RuntimeError('o polegar cruza os dedos mesmo aberto e com a CMC estendida no limite')
        # a maior flexão da CMC (a menor extensão) que solta: a bisseção sobe do limite estendido, que solta
        g['cmc'] = empunhadura._bissecao(solto, lim['cmc'][0], g['cmc'])
    return _com_graus(m, cadeia, g), {'graus': totais(mao, g)}
```

```python file=tools/blender/armas/maos_poses.py
# As poses de teste das luvas que dependem de contato (Fase 4.1b; desenho em docs/superpowers/specs/2026-09-26-4.1b-
# luvas-e-empunhadura-design.md, seção 4; plano, Tarefa 5), resolvidas pelo núcleo do solver de empunhadura
# (empunhadura.py) e pelo polegar dele (empunhadura_polegar.py):
#  - punho: os quatro dedos fechando para a MCP 85°, a PIP 95° e a DIP 60° contra a palma, os vizinhos separados, e o
#    polegar com a polpa nas costas das falanges médias do indicador e do médio (o alvo no meio das duas), fechado até
#    encostar — o polegar por cima dos dedos, como no punho de verdade;
#  - apontar: o mesmo com o indicador esticado (o mínimo da AAOS em todas as juntas) e a polpa do polegar na falange
#    média do médio;
#  - mesa: as quatro MCP no limite com os dedos esticados (a PIP e a DIP no mínimo), os vizinhos separados, e o polegar
#    fora do caminho deles (a MCP e a IP no mínimo; a CMC estendendo se precisar).
# Os ângulos que o contato segurou antes do alvo vão para o relatório. Problemas: o polegar que não encostou nos dedos
# no punho ou no apontar, ou com o lado da polpa a mais de 0,5 mm da superfície dos dedos do alvo (as três falanges
# deles): o polegar tem de ficar apoiado pela polpa, não só pela base.
# Como na mão de verdade, o polegar sai do caminho antes de os dedos fecharem (para o lado, no plano da palma: a
# abdução palmar e a flexão da CMC no mínimo, a MCP e a IP esticadas) e os dedos fecham contra a mão inteira — a palma,
# a tenar e o polegar afastado; depois o polegar pousa por cima deles, e as pontas que a tenar alcançou (o metacarpo
# do polegar a leva junto) recuam ao contato. Sem isso, a ponta do indicador fechava para dentro da base do polegar de
# repouso (ou da tenar, quando o polegar inteiro saía do obstáculo).
from . import empunhadura, empunhadura_polegar
from .empunhadura import TOLERANCIA_GRAUS, Colisor, Mao, fechar, separar_vizinhos
from .maos import DEDOS4

POLPA_MM = 0.5
_ALVO_DO_POLEGAR = {'punho': {'indicador': 0.7, 'medio': 0.3}, 'apontar': {'medio': 1.0}}


def _fechar_dedos(col, rep, m, dedos):
    """Os dedos da lista fechando para o punho contra a mão (o obstáculo de cada um: a luva sem ele e os vizinhos), os
    vizinhos separados e cada junta recuando ao contato depois da separação. Devolve (pose, {osso: ângulo
    total em que o contato segurou}, correções dos vizinhos)."""
    segurou = {}
    todos = set(col.cabeca)
    total = {1: rep['mcp'], 2: rep['pip'], 3: rep['dip']}
    for d in dedos:
        fora = empunhadura._cadeia(d).union(*(empunhadura._cadeia(v) for v in empunhadura._VIZINHOS[d]))
        obstaculo = col.triangulos(todos - fora)
        for osso, alvo in ((f'{d}_1', 85 - rep['mcp']), (f'{d}_2', 95 - rep['pip']), (f'{d}_3', 60 - rep['dip'])):
            m, graus, encostou = fechar(col, m, osso, alvo, obstaculo)
            if encostou:
                segurou[osso] = round(graus + total[int(osso[-1])], 2)
    m, vizinhos = separar_vizinhos(col, m, DEDOS4)
    # a abertura dos vizinhos mudou onde as pontas encostam
    m = _reassentar(col, rep, m, dedos, segurou)
    return m, segurou, vizinhos


def _reassentar(col, rep, m, dedos, segurou):
    """Cada junta dos dedos que ficou dentro da mão (a palma, a tenar, o polegar, os outros dedos) recua ao contato, da
    ponta para a base; o ângulo total em que o contato segurou vai para `segurou`."""
    todos = set(col.cabeca)
    total = {1: rep['mcp'], 2: rep['pip'], 3: rep['dip']}
    for d in dedos:
        fora = empunhadura._cadeia(d).union(*(empunhadura._cadeia(v) for v in empunhadura._VIZINHOS[d]))
        obstaculo = col.triangulos(todos - fora)
        for osso in (f'{d}_3', f'{d}_2', f'{d}_1'):
            agora = m.flexao.get(osso, 0.0)
            m, graus, _ = fechar(col, m.com(osso, flexao=min(agora, 0.0)), osso, agora, obstaculo)
            if graus < agora - TOLERANCIA_GRAUS:
                segurou[osso] = round(graus + total[int(osso[-1])], 2)
    return m


def _dedos(m):
    return {'flexao': {o: round(g, 2) for o, g in sorted(m.flexao.items()) if not o.startswith('polegar')},
            'abertura': {o: round(g, 2) for o, g in sorted(m.aberturas.items())}}


def poses_de_teste(luva, rig, mao, reforco):
    """{nome: pose} das poses de teste que dependem de contato (punho, apontar, mesa), o relatório de cada uma (os
    ângulos alcançados, as juntas que o contato segurou, as correções entre vizinhos e o polegar) e os problemas."""
    col = Colisor(luva, rig, mao, reforco)
    rep, lim = mao.rep, mao.f['limites']
    poses, rel, problemas = {}, {}, []
    for nome, dedos in (('punho', DEDOS4), ('apontar', ('medio', 'anelar', 'minimo'))):
        m = empunhadura_polegar.afastar(col, mao, Mao())
        if nome == 'apontar':
            for i, j in ((1, 'mcp'), (2, 'pip'), (3, 'dip')):
                m.flexao[f'indicador_{i}'] = lim[j][0] - rep[j]
        m, segurou, vizinhos = _fechar_dedos(col, rep, m, dedos)
        alvo, normal = empunhadura_polegar.alvo_nas_falanges(col, m.pose(), _ALVO_DO_POLEGAR[nome])
        superficie = col.triangulos({f'{d}_{i}' for d in _ALVO_DO_POLEGAR[nome] for i in (1, 2, 3)})
        m, polegar = empunhadura_polegar.fechar_no_alvo(col, mao, m, alvo, normal, superficie)
        # o metacarpo do polegar leva a tenar junto: as pontas que ela alcançou recuam ao contato
        m = _reassentar(col, rep, m, dedos, segurou)
        poses[nome] = m.pose()
        rel[nome] = {**_dedos(m), 'contatoSegurou': segurou, 'vizinhos': vizinhos, 'polegar': polegar}
        if not polegar['encostou']:
            problemas.append(f'pose {nome}: o polegar não encostou nos dedos (a polpa a '
                             f'{polegar["polpaEncostaMM"]} mm deles)')
        elif polegar['polpaEncostaMM'] > POLPA_MM:
            problemas.append(f'pose {nome}: o polegar encostou, mas com o lado da polpa a {polegar["polpaEncostaMM"]} mm '
                             f'dos dedos do alvo (máximo {POLPA_MM} mm)')
    m = Mao()
    for d in DEDOS4:
        m.flexao[f'{d}_1'] = lim['mcp'][1] - rep['mcp']
        m.flexao[f'{d}_2'] = lim['pip'][0] - rep['pip']
        m.flexao[f'{d}_3'] = lim['dip'][0] - rep['dip']
    m, vizinhos = separar_vizinhos(col, m, DEDOS4)
    m, polegar = empunhadura_polegar.abrir(col, mao, m)
    poses['mesa'] = m.pose()
    rel['mesa'] = {**_dedos(m), 'vizinhos': vizinhos, 'polegar': polegar}
    return poses, rel, problemas
```

Run: `node --test "tests/**/*.test.js"`
Expected: PASS — # tests 381 # pass 381 # fail 0 .

### Tarefa 6: UV, assar, exportar e a saída das luvas

**Files:** Modify `assar.py` (`uv_por_costuras`), `exportar.py` (`exportar_luvas`), `principal.py`,
`tools/blender.mjs`, `tools/blender/saida.mjs`; Create `tests/luvasSaida.test.js`, `tests/luvasGlb.test.js`.

- [ ] **Passo 1: Testes com arquivos sintéticos** — `tests/luvasSaida.test.js` (como `armasSaida.test.js`):
  `validarSaidaLuvas(raiz)` aponta `luvas.glb` ausente, relatório reprovado, triângulos acima de 14 000, braço com
  osso faltando ou com nome errado, textura com o lado errado, arquivos acima de 6 MB, marca do rig diferente entre o
  relatório e o `.glb`; e aprova uma saída sintética completa.
- [ ] **Passo 2: Ver falhar**; **Passo 3: `validarSaidaLuvas`** em `saida.mjs`; **Passo 4: ver passar**.
- [ ] **Passo 5: UV por costuras** — `uv_por_costuras(objetos, lado_px, margem_px)`: desdobramento conforme pelas
  costuras marcadas, as ilhas do braço direito (o esquerdo herda as mesmas UV), o empacotamento com a margem exata;
  sobreposição zero e densidade de texel dentro de 0,6–1,6 da mediana (as funções da 4.1a).
- [ ] **Passo 6: Assar e exportar** — `_n` e `_m` de 2048 com o alto como fonte; `luvas.glb` com as duas malhas com
  skin (`luva_d`, `luva_e`), as duas armaduras, as zonas, Draco, `extras` com a marca do rig; o relatório (medidas,
  triângulos, ossos, pesos, poses, UV, marca, arquivos, tempo).
- [ ] **Passo 7: `npm run blender -- construir luvas`** aprovado; `tests/luvasGlb.test.js` lê a saída real: 20 ossos
  por braço com os nomes da D2, as três zonas nas duas malhas, triângulos ≤ 14 000, as duas texturas de 2048 (cabeçalho
  WebP), arquivos ≤ 6 MB, marca do rig igual no relatório e no `.glb`; construir de novo sem mudança pula pelo hash.
- [ ] **Passo 8: Revisão crítica das texturas** (o `_n` e o `_m` abertos no navegador: costuras, rugas, grão, trama,
  nenhuma ilha vazia ou borrada).

### Parada de conferência P1

As vistas da luva (costas, palma, lados, três quartos, de perto dos nós e do punho) nas duas facções (pintura provisória
no render do Blender), as três poses de teste e as texturas; o usuário confere antes do solver.


**Código da tarefa** (a versão verificada no navegador e no Blender; os blocos `file=` são o arquivo inteiro, os pares são aplicados na ordem).

- [ ] **Os testes** — `tests/luvasSaida.test.js`, `tests/luvasGlb.test.js`, `tests/modeloDobras.test.js`, `tests/luvasTestUtils.js`, `tests/pegaGlb.test.js`:

```js file=tests/luvasSaida.test.js
// Validador da saída das luvas (Fase 4.1b; plano, Tarefa 6), com a saída montada no teste numa pasta temporária: o
// luvas.glb (a raiz `luvas` com a marca do rig nos extras, as duas armaduras, as duas malhas com skin por zona, o
// atributo `_VERTICE` e as correções das dobras nos extras), as duas texturas e o relatório. A saída de verdade é
// conferida em tests/luvasGlb.test.js.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, mkdirSync, rmSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { tmpdir } from 'node:os';
import { ossosDoLado } from '../src/data/luvas.js';
import { resumoLuvasGlb, validarSaidaLuvas } from '../tools/blender/saidaLuvas.mjs';

/** Monta um .glb com o JSON e um binário (os dois alinhados a 4 bytes). */
function montarGlb(json, bin = Buffer.alloc(0)) {
  let j = Buffer.from(JSON.stringify(json), 'utf8');
  if (j.length % 4) j = Buffer.concat([j, Buffer.alloc(4 - (j.length % 4), 0x20)]);
  let b = bin;
  if (b.length % 4) b = Buffer.concat([b, Buffer.alloc(4 - (b.length % 4), 0)]);
  const cab = Buffer.alloc(12);
  cab.writeUInt32LE(0x46546c67, 0);
  cab.writeUInt32LE(2, 4);
  cab.writeUInt32LE(12 + 8 + j.length + (b.length ? 8 + b.length : 0), 8);
  const cj = Buffer.alloc(8);
  cj.writeUInt32LE(j.length, 0);
  cj.writeUInt32LE(0x4e4f534a, 4);
  const partes = [cab, cj, j];
  if (b.length) {
    const cb = Buffer.alloc(8);
    cb.writeUInt32LE(b.length, 0);
    cb.writeUInt32LE(0x004e4942, 4);
    partes.push(cb, b);
  }
  return Buffer.concat(partes);
}

const MARCA = { d: 'a'.repeat(64), e: 'b'.repeat(64) };
const CORRECOES = JSON.stringify({ suaveMM: 0.1, juntas: [{ junta: 'indicador_mcp' }], pecas: { vertices: [] } });

/** O glTF das luvas: `tris` triângulos por zona em cada braço (3 zonas), os 20 ossos de cada lado. */
function gltfLuvas({ tris = 1000, ossos = { d: ossosDoLado('d'), e: ossosDoLado('e') }, zonas = ['couro', 'tecido', 'reforco'] } = {}) {
  const accessors = [];
  const acessor = (count, type = 'VEC3') => {
    accessors.push({ count, componentType: 5126, type });
    return accessors.length - 1;
  };
  const materials = zonas.map((name) => ({ name }));
  const nodes = [{ name: 'luvas', children: [], extras: { marca: { ...MARCA } } }];
  const no = (def, pai) => {
    nodes.push(def);
    nodes[pai].children = [...(nodes[pai].children ?? []), nodes.length - 1];
    return nodes.length - 1;
  };
  const meshes = [];
  const skins = [];
  for (const lado of ['d', 'e']) {
    const rig = no({ name: `rig_${lado}` }, 0);
    const juntas = ossos[lado].map((nome) => no({ name: nome }, rig));
    skins.push({ joints: juntas });
    meshes.push({
      primitives: materials.map((_, material) => ({
        attributes: {
          POSITION: acessor(tris * 3), NORMAL: acessor(tris * 3), TANGENT: acessor(tris * 3, 'VEC4'),
          TEXCOORD_0: acessor(tris * 3, 'VEC2'), JOINTS_0: acessor(tris * 3, 'VEC4'), WEIGHTS_0: acessor(tris * 3, 'VEC4'),
          _VERTICE: acessor(tris * 3, 'SCALAR'),
        },
        indices: acessor(tris * 3, 'SCALAR'),
        material,
      })),
    });
    no({ name: `luva_${lado}`, mesh: meshes.length - 1, skin: skins.length - 1, extras: { correcoes: CORRECOES } }, rig);
  }
  return {
    asset: { version: '2.0' }, scene: 0, scenes: [{ nodes: [0] }], nodes, meshes, skins, accessors, materials,
    extensionsUsed: ['KHR_draco_mesh_compression'], extensionsRequired: ['KHR_draco_mesh_compression'],
  };
}

/** Um .webp VP8L de `lado`×`lado` (só o cabeçalho), com ou sem alfa. */
function webp(lado, alfa = true) {
  const l = Buffer.alloc(5);
  l[0] = 0x2f;
  l.writeUInt32LE(((lado - 1) | ((lado - 1) << 14) | ((alfa ? 1 : 0) << 28)) >>> 0, 1);
  const cab = Buffer.alloc(12);
  cab.write('RIFF', 0, 'ascii');
  cab.writeUInt32LE(4 + 8 + l.length, 4);
  cab.write('WEBP', 8, 'ascii');
  const ch = Buffer.alloc(8);
  ch.write('VP8L', 0, 'ascii');
  ch.writeUInt32LE(l.length, 4);
  return Buffer.concat([cab, ch, l]);
}

function relatorio(tris = 3000) {
  return { luvas: true, aprovado: true, problemas: [], triangulos: { luva: tris, base: tris - 600, detalhes: 600 }, marca: { ...MARCA } };
}

/** Grava a saída sintética numa pasta temporária; `mexer` altera as partes antes. Devolve a raiz. */
function saida(mexer = () => {}) {
  const raiz = mkdtempSync(join(tmpdir(), 'luvas-saida-'));
  const pasta = join(raiz, 'assets', 'maos');
  mkdirSync(pasta, { recursive: true });
  const partes = { gltf: gltfLuvas(), bin: Buffer.alloc(0), n: webp(2048), m: webp(2048), relatorio: relatorio() };
  mexer(partes);
  if (partes.gltf) writeFileSync(join(pasta, 'luvas.glb'), montarGlb(partes.gltf, partes.bin));
  writeFileSync(join(pasta, 'luvas_n.webp'), partes.n);
  writeFileSync(join(pasta, 'luvas_m.webp'), partes.m);
  writeFileSync(join(pasta, 'luvas.relatorio.json'), JSON.stringify(partes.relatorio));
  return raiz;
}

function problemas(mexer) {
  const raiz = saida(mexer);
  try {
    return validarSaidaLuvas(raiz).problemas;
  } finally {
    rmSync(raiz, { recursive: true, force: true });
  }
}

test('saída das luvas: resumo do glb — as duas malhas, os ossos de cada lado, as zonas, os atributos e os extras', () => {
  const r = resumoLuvasGlb(gltfLuvas());
  assert.equal(r.raiz, 'luvas');
  assert.deepEqual(Object.keys(r.malhas), ['luva_d', 'luva_e']);
  assert.equal(r.malhas.luva_d.triangulos, 3000);
  assert.deepEqual(r.malhas.luva_e.ossos, ossosDoLado('e'));
  assert.deepEqual(r.malhas.luva_d.zonas, ['couro', 'tecido', 'reforco']);
  for (const k of ['uv', 'tangentes', 'pesos', 'vertice']) assert.equal(r.malhas.luva_d[k], true, k);
  assert.equal(r.malhas.luva_d.correcoes.juntas, 1);
  assert.deepEqual(r.marca, MARCA);
  assert.equal(r.draco, true);
  // o atributo no acessor 0 (o exportador do Blender põe o _VERTICE primeiro) conta como presente
  const zero = gltfLuvas();
  zero.meshes[0].primitives[0].attributes._VERTICE = 0;
  assert.equal(resumoLuvasGlb(zero).malhas.luva_d.vertice, true);
  assert.throws(() => resumoLuvasGlb({ ...gltfLuvas(), nodes: [{ name: 'ak47' }], scenes: [{ nodes: [0] }] }),
    /a raiz do \.glb é ak47, esperava luvas/);
});

test('saída das luvas: a completa passa', () => {
  assert.deepEqual(problemas(), []);
});

test('saída das luvas: arquivo faltando e relatório reprovado', () => {
  assert.ok(problemas((p) => { p.gltf = null; }).some((m) => m.includes('faltam') && m.includes('luvas.glb')));
  const p = problemas((s) => { s.relatorio = { ...s.relatorio, aprovado: false, problemas: ['pose punho: atravessa 2 mm'] }; });
  assert.ok(p.some((m) => m.includes('o Blender reprovou') && m.includes('atravessa 2 mm')), p.join(' | '));
});

test('saída das luvas: triângulos acima do orçamento dos dois braços e o relatório diferente do glb', () => {
  const p = problemas((s) => {
    s.gltf = gltfLuvas({ tris: 2500 });
    s.relatorio = relatorio(7500);
  });
  assert.ok(p.some((m) => m.includes('15000 triângulos') && m.includes('14000')), p.join(' | '));
  const q = problemas((s) => { s.relatorio = relatorio(2999); });
  assert.ok(q.some((m) => m.includes('luva_d: o relatório diz 2999')), q.join(' | '));
});

test('saída das luvas: osso faltando, com o nome errado ou do outro lado', () => {
  const ossos = { d: ossosDoLado('d'), e: ossosDoLado('e').filter((o) => o !== 'minimo_3_e') };
  let p = problemas((s) => { s.gltf = gltfLuvas({ ossos }); });
  assert.ok(p.some((m) => m.includes('luva_e: falta o osso minimo_3_e')), p.join(' | '));
  ossos.e = [...ossosDoLado('e').slice(0, 19), 'mindinho_3_e'];
  p = problemas((s) => { s.gltf = gltfLuvas({ ossos }); });
  assert.ok(p.some((m) => m.includes('luva_e: osso a mais mindinho_3_e')), p.join(' | '));
  ossos.e = ossosDoLado('d');
  p = problemas((s) => { s.gltf = gltfLuvas({ ossos }); });
  assert.ok(p.some((m) => m.includes('luva_e: falta o osso mao_e')), p.join(' | '));
});

test('saída das luvas: zonas, UV, tangentes, pesos, o índice dos vértices, as correções e o Draco', () => {
  let p = problemas((s) => { s.gltf = gltfLuvas({ zonas: ['couro', 'tecido'] }); });
  assert.ok(p.some((m) => m.includes('luva_d: falta a zona reforco')), p.join(' | '));
  p = problemas((s) => {
    for (const pr of s.gltf.meshes[1].primitives) {
      delete pr.attributes.TEXCOORD_0;
      delete pr.attributes.TANGENT;
      delete pr.attributes.WEIGHTS_0;
      delete pr.attributes._VERTICE;
    }
    delete s.gltf.nodes.find((n) => n.name === 'luva_e').extras;
    delete s.gltf.extensionsUsed;
  });
  for (const esperado of ['luva_e: primitiva sem UV', 'luva_e: primitiva sem tangentes', 'luva_e: primitiva sem os pesos',
    'luva_e: primitiva sem o _VERTICE', 'luva_e: sem as correções das dobras', 'sem a compressão Draco']) {
    assert.ok(p.some((m) => m.includes(esperado)), `${esperado} — ${p.join(' | ')}`);
  }
});

test('saída das luvas: texturas com o lado errado, com perdas ou sem alfa, e os arquivos acima de 6 MB', () => {
  let p = problemas((s) => { s.n = webp(1024); s.m = webp(2048, false); });
  assert.ok(p.some((m) => m.includes('luvas_n.webp: 1024×1024 (esperava 2048×2048)')), p.join(' | '));
  assert.ok(p.some((m) => m.includes('luvas_m.webp: sem o canal alfa')), p.join(' | '));
  p = problemas((s) => { s.bin = Buffer.alloc(6.5 * 1024 * 1024); });
  assert.ok(p.some((m) => /^arquivos: 6\.5\d MB \(orçamento 6 MB\)$/.test(m)), p.join(' | '));
});

test('saída das luvas: a marca do rig do relatório diferente da do glb', () => {
  const p = problemas((s) => { s.relatorio = { ...s.relatorio, marca: { d: MARCA.d, e: 'c'.repeat(64) } }; });
  assert.ok(p.some((m) => m.includes('marca do rig e') && m.includes('relatório')), p.join(' | '));
  const q = problemas((s) => { delete s.gltf.nodes[0].extras; });
  assert.ok(q.some((m) => m.includes('o .glb sem a marca do rig')), q.join(' | '));
});
```

```js file=tests/luvasGlb.test.js
// A saída de verdade das luvas (Fase 4.1b; plano, Tarefa 6, Passo 7), depois de `npm run blender -- construir luvas`:
// o validador da saída sem problemas (os 20 ossos de cada braço com os nomes da D2, as três zonas nas duas malhas, os
// triângulos dos dois braços ≤ 14 000, as duas texturas de 2048 sem perdas, os arquivos ≤ 6 MB, a marca do rig igual no
// relatório e no .glb) e o `_VERTICE` decodificado do Draco (o decodificador do vendor, em JS): em cada braço, depois de
// arredondado, um índice inteiro de vértice do Blender por vértice do glTF, cobrindo todos os vértices da luva — o que o
// jogo usa para casar o modelo das dobras e as amarras das peças com a malha do glTF.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import vm from 'node:vm';
import { LUVAS } from '../src/data/luvas.js';
import { lerGlb } from '../tools/blender/saida.mjs';
import { validarSaidaLuvas } from '../tools/blender/saidaLuvas.mjs';

const RAIZ = join(dirname(fileURLToPath(import.meta.url)), '..');
const PASTA = join(RAIZ, LUVAS.pasta);

/** O módulo do decodificador Draco do vendor (Emscripten, CommonJS) carregado no Node. */
async function decodificadorDraco() {
  const arquivo = join(RAIZ, 'vendor', 'three', 'examples', 'jsm', 'libs', 'draco', 'gltf', 'draco_decoder.js');
  const modulo = { exports: {} };
  vm.runInThisContext(`(function (module, exports, require, __filename, __dirname) {${readFileSync(arquivo, 'utf8')}\n})`)(
    modulo, modulo.exports, createRequire(arquivo), arquivo, dirname(arquivo));
  return modulo.exports();
}

/** Os valores de um atributo (pelo id único da extensão Draco) de uma primitiva comprimida. */
function atributoDraco(draco, json, bin, primitiva, nome) {
  const ext = primitiva.extensions.KHR_draco_mesh_compression;
  const vista = json.bufferViews[ext.bufferView];
  const bytes = new Int8Array(bin.buffer, bin.byteOffset + (vista.byteOffset ?? 0), vista.byteLength);
  const decodificador = new draco.Decoder();
  const buffer = new draco.DecoderBuffer();
  buffer.Init(bytes, bytes.length);
  const malha = new draco.Mesh();
  try {
    const estado = decodificador.DecodeBufferToMesh(buffer, malha);
    assert.ok(estado.ok(), `o Draco não decodificou: ${estado.error_msg()}`);
    const atributo = decodificador.GetAttributeByUniqueId(malha, ext.attributes[nome]);
    const n = malha.num_points() * atributo.num_components();
    const arr = new draco.DracoFloat32Array();
    decodificador.GetAttributeFloatForAllPoints(malha, atributo, arr);
    const valores = new Float32Array(n);
    for (let i = 0; i < n; i++) valores[i] = arr.GetValue(i);
    draco.destroy(arr);
    return valores;
  } finally {
    draco.destroy(malha);
    draco.destroy(buffer);
    draco.destroy(decodificador);
  }
}

test('luvas.glb de verdade: o validador da saída sem problemas', () => {
  const { problemas, resumo, relatorio, bytes } = validarSaidaLuvas(RAIZ);
  assert.deepEqual(problemas, []);
  assert.equal(resumo.malhas.luva_d.ossos.length, 20);
  assert.equal(resumo.malhas.luva_e.ossos.length, 20);
  assert.ok(resumo.malhas.luva_d.triangulos + resumo.malhas.luva_e.triangulos <= LUVAS.orcamento.triangulos);
  assert.ok(bytes <= LUVAS.orcamento.arquivosMB * 1024 * 1024);
  assert.equal(relatorio.aprovado, true);
  assert.equal(relatorio.uv.sobreposicao, 0);
});

test('luvas.glb de verdade: o _VERTICE do Draco cobre os vértices do Blender, um inteiro por vértice do glTF', async () => {
  const { json, bin } = lerGlb(readFileSync(join(PASTA, 'luvas.glb')));
  const relatorio = JSON.parse(readFileSync(join(PASTA, 'luvas.relatorio.json'), 'utf8'));
  const draco = await decodificadorDraco();
  for (const nome of ['luva_d', 'luva_e']) {
    const no = json.nodes.find((n) => n.name === nome);
    const vistos = new Set();
    let pior = 0;
    for (const p of json.meshes[no.mesh].primitives) {
      for (const v of atributoDraco(draco, json, bin, p, '_VERTICE')) {
        const i = Math.round(v);
        pior = Math.max(pior, Math.abs(v - i));
        vistos.add(i);
      }
    }
    assert.ok(pior < 0.1, `${nome}: o _VERTICE a ${pior} de um inteiro (a quantização do Draco)`);
    assert.equal(vistos.size, relatorio.vertices, `${nome}: ${vistos.size} índices, ${relatorio.vertices} vértices no Blender`);
    assert.equal(Math.min(...vistos), 0);
    assert.equal(Math.max(...vistos), relatorio.vertices - 1);
  }
});
```

```js file=tests/modeloDobras.test.js
// O modelo das dobras em JS (Fase 4.1b; plano, Tarefa 9) contra o do Blender: montado do luvas.glb de verdade como o
// jogo monta (as primitivas casadas pelo `_VERTICE`, o esqueleto pelas matrizes de ligação inversas, as correções dos
// extras), avaliado nas poses da prova do relatório (os giros no referencial do braço) e comparado com as posições que o
// Blender gravou, nos dois braços — a mesma tolerância do `luvas_contato` (0,05 mm; a posição do glTF vem do Draco em
// 14 bits). E as contas puras: o skin sem giro devolve o repouso, as juntas em repouso não mexem, as peças presas.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import { LIMITES_DA_PEGA, LUVAS } from '../src/data/luvas.js';
import { deBlender, normaisDosVertices } from '../src/characters/hands/modeloDobras.js';
import { lerGlb } from '../tools/blender/saida.mjs';
import { RAIZ, decodificadorDraco, modeloDoGlb, primitivaDraco } from './luvasTestUtils.js';

const PASTA = join(RAIZ, LUVAS.pasta);

async function montar() {
  const { json, bin } = lerGlb(readFileSync(join(PASTA, 'luvas.glb')));
  const relatorio = JSON.parse(readFileSync(join(PASTA, 'luvas.relatorio.json'), 'utf8'));
  const draco = await decodificadorDraco();
  return { json, bin, relatorio, draco };
}

test('modelo das dobras: o JS casa com o Blender nas poses da prova, nos dois braços (≤ 0,05 mm)', async () => {
  const { json, bin, relatorio, draco } = await montar();
  assert.ok(relatorio.provaDoModelo, 'o relatório das luvas sem a prova do modelo: construa as luvas de novo');
  for (const lado of ['d', 'e']) {
    const modelo = modeloDoGlb(draco, json, bin, `luva_${lado}`);
    const prova = relatorio.provaDoModelo[lado];
    assert.equal(modelo.malha.n, relatorio.vertices, `${lado}: vértices`);
    for (const [pose, dados] of Object.entries(prova.poses)) {
      const giros = {};
      for (const [osso, g] of Object.entries(dados.giros)) giros[`${osso}_${lado}`] = [...deBlender(g.slice(0, 3)), g[3]];
      const pts = modelo.avaliar(modelo.deformacoesDosGiros(giros));
      let pior = 0;
      let onde = -1;
      prova.vertices.forEach((v, k) => {
        const esperado = deBlender(dados.mm[k]);
        const d = Math.hypot(pts[v * 3] - esperado[0], pts[v * 3 + 1] - esperado[1], pts[v * 3 + 2] - esperado[2]);
        if (d > pior) {
          pior = d;
          onde = v;
        }
      });
      assert.ok(pior <= LIMITES_DA_PEGA.contatoJogoMM, `${lado}, pose ${pose}: o vértice ${onde} a ${pior.toFixed(4)} mm do Blender`);
    }
  }
});

test('modelo das dobras: sem giro, a malha fica no repouso (as peças a menos de 0,02 mm) e as normais batem com as do Blender', async () => {
  const { json, bin, draco } = await montar();
  const modelo = modeloDoGlb(draco, json, bin, 'luva_d');
  const pts = modelo.avaliar(modelo.deformacoesDosGiros({}));
  let pior = 0;
  for (let i = 0; i < pts.length; i++) pior = Math.max(pior, Math.abs(pts[i] - modelo.malha.repouso[i]));
  // a base fica exata; as peças são sempre reassentadas na base (como no Blender), e a posição do Draco é quantizada
  assert.ok(pior < 0.02, `repouso a ${pior} mm`);
  // as normais do modelo (pela área dos triângulos, por vértice do Blender) contra as que o Blender exportou (o NORMAL
  // do glTF, igual nos vértices duplicados das costuras): o mesmo sentido (o giro dos triângulos certo) e quase a
  // mesma direção
  const vn = normaisDosVertices(pts, modelo.malha.triangulos, modelo.malha.n);
  const no = json.nodes.find((n) => n.name === 'luva_d');
  let soma = 0;
  let conta = 0;
  let contra = 0;
  for (const p of json.meshes[no.mesh].primitives) {
    const d = primitivaDraco(draco, json, bin, p, ['NORMAL', '_VERTICE']);
    for (let k = 0; k < d._VERTICE.length; k++) {
      const v = Math.round(d._VERTICE[k]);
      const c = d.NORMAL[k * 3] * vn[v * 3] + d.NORMAL[k * 3 + 1] * vn[v * 3 + 1] + d.NORMAL[k * 3 + 2] * vn[v * 3 + 2];
      soma += c;
      conta++;
      if (c < 0) contra++;
    }
  }
  assert.ok(soma / conta > 0.95, `as normais do modelo a ${(soma / conta).toFixed(3)} de cosseno médio das do Blender`);
  assert.ok(contra / conta < 0.01, `${contra} normais do modelo contra as do Blender`);
});
```

```js file=tests/luvasTestUtils.js
// Utilitários dos testes das luvas de verdade (Fase 4.1b): o decodificador Draco do vendor carregado no Node, os
// atributos e os índices de uma primitiva comprimida, e o modelo das dobras de um braço montado do luvas.glb (as
// primitivas por zona, o esqueleto pelas matrizes de ligação inversas e as correções dos extras), como o jogo monta; e o
// GLTFLoader do vendor lendo um .glb do disco com o Draco sem Workers.
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import vm from 'node:vm';
import * as THREE from 'three';
import { bounds, compile } from '../src/clay/sdf/nodes.js';
import { polygonize } from '../src/clay/sdf/marchingCubes.js';
import { ModeloDobras, dadosDasPrimitivas } from '../src/characters/hands/modeloDobras.js';

export const RAIZ = join(dirname(fileURLToPath(import.meta.url)), '..');

/** O módulo do decodificador Draco do vendor (Emscripten, CommonJS) carregado no Node. */
export async function decodificadorDraco() {
  const arquivo = join(RAIZ, 'vendor', 'three', 'examples', 'jsm', 'libs', 'draco', 'gltf', 'draco_decoder.js');
  const modulo = { exports: {} };
  vm.runInThisContext(`(function (module, exports, require, __filename, __dirname) {${readFileSync(arquivo, 'utf8')}\n})`)(
    modulo, modulo.exports, createRequire(arquivo), arquivo, dirname(arquivo));
  return modulo.exports();
}

/** Os atributos pedidos ({nome glTF: valores}) e os índices dos triângulos de uma primitiva comprimida pelo Draco. */
export function primitivaDraco(draco, json, bin, primitiva, nomes) {
  const ext = primitiva.extensions.KHR_draco_mesh_compression;
  const vista = json.bufferViews[ext.bufferView];
  const bytes = new Int8Array(bin.buffer, bin.byteOffset + (vista.byteOffset ?? 0), vista.byteLength);
  const decodificador = new draco.Decoder();
  const buffer = new draco.DecoderBuffer();
  buffer.Init(bytes, bytes.length);
  const malha = new draco.Mesh();
  try {
    const estado = decodificador.DecodeBufferToMesh(buffer, malha);
    assert.ok(estado.ok(), `o Draco não decodificou: ${estado.error_msg()}`);
    const saida = {};
    for (const nome of nomes) {
      const atributo = decodificador.GetAttributeByUniqueId(malha, ext.attributes[nome]);
      const n = malha.num_points() * atributo.num_components();
      const arr = new draco.DracoFloat32Array();
      decodificador.GetAttributeFloatForAllPoints(malha, atributo, arr);
      const valores = new Float32Array(n);
      for (let i = 0; i < n; i++) valores[i] = arr.GetValue(i);
      draco.destroy(arr);
      saida[nome] = valores;
    }
    const indices = new Uint32Array(malha.num_faces() * 3);
    const face = new draco.DracoInt32Array();
    for (let f = 0; f < malha.num_faces(); f++) {
      decodificador.GetFaceFromMesh(malha, f, face);
      for (let k = 0; k < 3; k++) indices[f * 3 + k] = face.GetValue(k);
    }
    draco.destroy(face);
    saida.indices = indices;
    return saida;
  } finally {
    draco.destroy(malha);
    draco.destroy(buffer);
    draco.destroy(decodificador);
  }
}

/** Um acessor comum (não comprimido) como Float32Array. */
function acessor(json, bin, i) {
  const a = json.accessors[i];
  const vista = json.bufferViews[a.bufferView];
  const comp = { SCALAR: 1, VEC2: 2, VEC3: 3, VEC4: 4, MAT4: 16 }[a.type];
  assert.equal(a.componentType, 5126, 'o acessor não é float');
  return new Float32Array(bin.buffer.slice(bin.byteOffset + (vista.byteOffset ?? 0) + (a.byteOffset ?? 0),
    bin.byteOffset + (vista.byteOffset ?? 0) + (a.byteOffset ?? 0) + a.count * comp * 4));
}

/** A translação da inversa de uma matriz afim 4×4 (glTF, por colunas; a parte linear pode ter escala): −A⁻¹·t. */
function translacaoDaInversa(m) {
  const a = [[m[0], m[4], m[8]], [m[1], m[5], m[9]], [m[2], m[6], m[10]]];
  const t = [m[12], m[13], m[14]];
  const det = a[0][0] * (a[1][1] * a[2][2] - a[1][2] * a[2][1]) - a[0][1] * (a[1][0] * a[2][2] - a[1][2] * a[2][0])
    + a[0][2] * (a[1][0] * a[2][1] - a[1][1] * a[2][0]);
  const inv = [
    [(a[1][1] * a[2][2] - a[1][2] * a[2][1]) / det, (a[0][2] * a[2][1] - a[0][1] * a[2][2]) / det, (a[0][1] * a[1][2] - a[0][2] * a[1][1]) / det],
    [(a[1][2] * a[2][0] - a[1][0] * a[2][2]) / det, (a[0][0] * a[2][2] - a[0][2] * a[2][0]) / det, (a[0][2] * a[1][0] - a[0][0] * a[1][2]) / det],
    [(a[1][0] * a[2][1] - a[1][1] * a[2][0]) / det, (a[0][1] * a[2][0] - a[0][0] * a[2][1]) / det, (a[0][0] * a[1][1] - a[0][1] * a[1][0]) / det],
  ];
  return [0, 1, 2].map((r) => -(inv[r][0] * t[0] + inv[r][1] * t[1] + inv[r][2] * t[2]));
}

/** O modelo das dobras de um braço (`luva_d` ou `luva_e`) montado do luvas.glb, como o jogo faz. */
export function modeloDoGlb(draco, json, bin, nomeDaMalha) {
  const no = json.nodes.find((n) => n.name === nomeDaMalha);
  const lado = nomeDaMalha.slice(-1);
  const materiais = json.materials ?? [];
  const primitivas = json.meshes[no.mesh].primitives.map((p) => {
    const d = primitivaDraco(draco, json, bin, p, ['POSITION', 'JOINTS_0', 'WEIGHTS_0', '_VERTICE']);
    return { posicoes: d.POSITION, juntas: d.JOINTS_0, pesos: d.WEIGHTS_0, vertice: d._VERTICE, indices: d.indices, zona: materiais[p.material]?.name };
  });
  const malha = dadosDasPrimitivas(primitivas);
  const skin = json.skins[no.skin];
  const ossos = skin.joints.map((j) => json.nodes[j].name);
  const pais = skin.joints.map((j) => skin.joints.findIndex((k) => (json.nodes[k].children ?? []).includes(j)));
  const ibm = acessor(json, bin, skin.inverseBindMatrices);
  const cabecas = [];
  // as cabeças de repouso no referencial da malha (u; a inversa da matriz de ligação inversa), em mm
  for (let i = 0; i < ossos.length; i++) cabecas.push(...translacaoDaInversa(ibm.subarray(i * 16, i * 16 + 16)).map((v) => v * 25.4));
  const parametros = typeof no.extras.correcoes === 'string' ? JSON.parse(no.extras.correcoes) : no.extras.correcoes;
  return new ModeloDobras({ malha, ossos, pais, cabecas, parametros, lado });
}

/**
 * O DRACOLoader do three sem Workers (o Node não tem Worker de navegador): a mesma decodificação do worker dele
 * (atributos pelo id único, com o tipo que o GLTFLoader pede, e os índices), síncrona, para o GLTFLoader do vendor ler
 * o .glb de verdade nos testes.
 */
export function dracoSincrono(draco) {
  const tipos = {
    Float32Array: draco.DT_FLOAT32, Int8Array: draco.DT_INT8, Int16Array: draco.DT_INT16, Int32Array: draco.DT_INT32,
    Uint8Array: draco.DT_UINT8, Uint16Array: draco.DT_UINT16, Uint32Array: draco.DT_UINT32,
  };
  return {
    decodeDracoFile(buffer, callback, attributeIDs, attributeTypes, _cor, onError = () => {}) {
      const decodificador = new draco.Decoder();
      const malha = new draco.Mesh();
      try {
        const bytes = new Int8Array(buffer);
        const estado = decodificador.DecodeArrayToMesh(bytes, bytes.byteLength, malha);
        if (!estado.ok() || malha.ptr === 0) throw new Error(`Draco: ${estado.error_msg()}`);
        const g = new THREE.BufferGeometry();
        for (const [nome, id] of Object.entries(attributeIDs)) {
          const Tipo = globalThis[attributeTypes[nome]];
          const atributo = decodificador.GetAttributeByUniqueId(malha, id);
          const n = malha.num_points() * atributo.num_components();
          const ptr = draco._malloc(n * Tipo.BYTES_PER_ELEMENT);
          decodificador.GetAttributeDataArrayForAllPoints(malha, atributo, tipos[attributeTypes[nome]], n * Tipo.BYTES_PER_ELEMENT, ptr);
          const valores = new Tipo(draco.HEAPF32.buffer, ptr, n).slice();
          draco._free(ptr);
          g.setAttribute(nome, new THREE.BufferAttribute(valores, atributo.num_components()));
        }
        const ni = malha.num_faces() * 3;
        const ptr = draco._malloc(ni * 4);
        decodificador.GetTrianglesUInt32Array(malha, ni * 4, ptr);
        g.setIndex(new THREE.BufferAttribute(new Uint32Array(draco.HEAPF32.buffer, ptr, ni).slice(), 1));
        draco._free(ptr);
        callback(g);
      } catch (e) {
        onError(e);
      } finally {
        draco.destroy(malha);
        draco.destroy(decodificador);
      }
      return Promise.resolve();
    },
    preload() {
      return this;
    },
    dispose() {},
  };
}

/** Um .glb do disco pelo GLTFLoader do vendor (o mesmo código do jogo), com o Draco síncrono. */
export async function carregarGlbNoNode(arquivo, draco) {
  const { GLTFLoader } = await import('three/addons/loaders/GLTFLoader.js');
  const loader = new GLTFLoader().setDRACOLoader(dracoSincrono(draco));
  const b = readFileSync(arquivo);
  return loader.parseAsync(b.buffer.slice(b.byteOffset, b.byteOffset + b.byteLength), '');
}

/** SdfMesher de teste: a mesma árvore pelo marching cubes, numa grade grossa, e o registro dos pedidos. */
export function sdfDeTeste(resolucao = 48) {
  const pedidos = [];
  return {
    pedidos,
    async build(tree, opts) {
      pedidos.push({ tree, opts });
      const m = polygonize(compile(tree), bounds(tree), { resolution: Math.min(resolucao, opts.resolution), maxCells: 600000 });
      const g = new THREE.BufferGeometry();
      g.setAttribute('position', new THREE.BufferAttribute(Float32Array.from(m.positions), 3));
      g.setAttribute('normal', new THREE.BufferAttribute(Float32Array.from(m.normals), 3));
      g.setIndex(new THREE.BufferAttribute(Uint32Array.from(m.indices), 1));
      return g;
    },
  };
}
```

```js file=tests/pegaGlb.test.js
// A pega das luvas no .glb das armas (Fase 4.1b; desenho, seção 6.4; plano, Tarefa 7 e D1): `lerPega` (os nós `pega`,
// `pega_mao_d` e `pega_mao_e`, o clipe `empunhadura` com as rotações dos 34 ossos de dedo, a marca do rig e as sondas
// nos extras), a validação da seção `empunhadura` do relatório e a AK de verdade depois do construir, com a marca igual
// à do luvas.glb.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { existsSync, readFileSync } from 'node:fs';
import { join } from 'node:path';
import { LIMITES_DA_PEGA, OSSOS_DE_DEDO, ossosDoLado } from '../src/data/luvas.js';
import { lerPega } from '../src/characters/hands/pega.js';
import { lerGlb, validarSaida } from '../tools/blender/saida.mjs';
import { validarPega } from '../tools/blender/saidaPega.mjs';

const ROOT = join(import.meta.dirname, '..');
const MARCA = { d: 'a'.repeat(64), e: 'b'.repeat(64) };
const SONDAS = {
  d: { palma: { vertice: 12, mm: 0.03 }, indicador_gatilho: { vertice: 400, mm: 0.02 }, polegar: { vertice: 900, mm: 0.04 } },
  e: { palma: { vertice: 15, mm: 0.04 }, polegar: { vertice: 901, mm: 0.05 } },
};

/** O glTF da pega: a raiz da arma, o nó `pega` com os extras, as duas mãos e a armadura com os 40 ossos; o clipe gira os
 *  ossos de `giram` (por padrão os 34 de dedo) e, como o exportador com amostragem, move todos. */
function gltfPega({ extras = { luvas: JSON.stringify({ marca: MARCA, sondas: SONDAS }) }, maos = ['d', 'e'],
  giram = [...OSSOS_DE_DEDO.map((o) => `${o}_d`), ...OSSOS_DE_DEDO.map((o) => `${o}_e`)], comClipe = true } = {}) {
  const nodes = [{ name: 'ak47', children: [1] }, { name: 'pega', extras, children: [] }];
  for (const lado of maos) {
    nodes.push({ name: `pega_mao_${lado}`, translation: [1, 2, 3], rotation: [0, 0, 0, 1] });
    nodes[1].children.push(nodes.length - 1);
  }
  nodes.push({ name: 'pega_luvas', children: [] });
  const arm = nodes.length - 1;
  nodes[1].children.push(arm);
  const indice = {};
  for (const nome of new Set([...ossosDoLado('d'), ...ossosDoLado('e'), ...giram])) {
    nodes.push({ name: nome, rotation: [0, 0, 0, 1] });
    indice[nome] = nodes.length - 1;
    nodes[arm].children.push(nodes.length - 1);
  }
  const channels = [];
  for (const nome of giram) channels.push({ sampler: 0, target: { node: indice[nome], path: 'rotation' } });
  for (const nome of ossosDoLado('d')) channels.push({ sampler: 1, target: { node: indice[nome], path: 'translation' } });
  const animations = comClipe ? [{ name: 'empunhadura', channels, samplers: [{ input: 0, output: 1 }, { input: 0, output: 2 }] }] : [];
  return { scene: 0, scenes: [{ nodes: [0] }], nodes, animations };
}

test('lerPega acha as duas mãos, as 34 trilhas de dedo, a marca e as sondas', () => {
  const p = lerPega(gltfPega());
  assert.deepEqual(Object.keys(p.maos).sort(), ['d', 'e']);
  assert.deepEqual(p.maos.d.posicao, [1, 2, 3]);
  assert.deepEqual(p.maos.d.rotacao, [0, 0, 0, 1]);
  assert.equal(Object.keys(p.trilhas).length, 34);
  assert.ok(p.trilhas.indicador_1_d >= 0 && p.trilhas.minimo_0_e >= 0);
  assert.deepEqual(p.marca, MARCA);
  assert.equal(p.sondas.d.indicador_gatilho.vertice, 400);
});

test('lerPega aceita os extras já como objeto', () => {
  const p = lerPega(gltfPega({ extras: { luvas: { marca: MARCA, sondas: SONDAS } } }));
  assert.deepEqual(p.marca, MARCA);
});

test('lerPega recusa a pega sem uma das mãos', () => {
  assert.throws(() => lerPega(gltfPega({ maos: ['d'] })), /pega_mao_e/);
});

test('lerPega recusa o clipe sem um osso de dedo', () => {
  const giram = [...OSSOS_DE_DEDO.map((o) => `${o}_d`), ...OSSOS_DE_DEDO.map((o) => `${o}_e`)].filter((n) => n !== 'minimo_3_e');
  assert.throws(() => lerPega(gltfPega({ giram })), /minimo_3_e/);
});

test('lerPega recusa trilha em osso de nome desconhecido', () => {
  const giram = [...OSSOS_DE_DEDO.map((o) => `${o}_d`), ...OSSOS_DE_DEDO.map((o) => `${o}_e`), 'mindinho_1_d'];
  assert.throws(() => lerPega(gltfPega({ giram })), /desconhecid/);
});

test('lerPega recusa sem o clipe, sem o nó pega ou sem a marca', () => {
  assert.throws(() => lerPega(gltfPega({ comClipe: false })), /empunhadura/);
  const semPega = gltfPega();
  semPega.nodes[1].name = 'outro';
  assert.throws(() => lerPega(semPega), /pega/);
  assert.throws(() => lerPega(gltfPega({ extras: { luvas: { sondas: SONDAS } } })), /marca/);
});

const REL_OK = {
  empunhadura: {
    d: {
      penetracaoMM: 0.05, contatosMM: { palma: 0.03, indicador_gatilho: 0.02, polegar: 0.04 },
      lados: { polegarMM: 14.2, dedosMM: { medio: -12.5, anelar: -13.1, minimo: -11.8 } },
      juntosMM: { 'medio-anelar': [2.45, 0.98], 'anelar-minimo': [3.34, 4.55] },
    },
    e: {
      penetracaoMM: 0.04, contatosMM: { palma: 0.04, polegar: 0.05 },
      lados: { polegarMM: 19.6, dedosMM: { indicador: -18.4, medio: -19.9, anelar: -18.7, minimo: -17.2 } },
      polegar: { curvaGraus: 0, trechosMM: [6.48, 5.23, 4.01, 2.36, 0.2, 0.09] },
      juntosMM: { 'indicador-medio': [3.98, 9.71], 'medio-anelar': [2.64, 3.72], 'anelar-minimo': [6.77, 15.68] },
    },
    frente: 'e',
    marca: MARCA,
  },
};

test('validarPega aprova o relatório e o .glb certos', () => {
  assert.deepEqual(validarPega(REL_OK, lerPega(gltfPega()), MARCA), []);
});

test('validarPega aponta o relatório sem a empunhadura, a penetração, o contato e a marca', () => {
  assert.match(validarPega({}, lerPega(gltfPega()), MARCA).join('\n'), /empunhadura/);
  const fundo = structuredClone(REL_OK);
  fundo.empunhadura.d.penetracaoMM = 0.35;
  assert.match(validarPega(fundo, lerPega(gltfPega()), MARCA).join('\n'), /0,35|0\.35/);
  const longe = structuredClone(REL_OK);
  longe.empunhadura.e.contatosMM.polegar = 1.2;
  assert.match(validarPega(longe, lerPega(gltfPega()), MARCA).join('\n'), /polegar/);
  assert.match(validarPega(REL_OK, lerPega(gltfPega()), { d: 'c'.repeat(64), e: MARCA.e }).join('\n'), /marca/);
});

test('validarPega exige na mão da frente só o polegar de um lado e os quatro dedos do outro', () => {
  const semLados = structuredClone(REL_OK);
  delete semLados.empunhadura.e.lados;
  assert.match(validarPega(semLados, lerPega(gltfPega()), MARCA).join('\n'), /mão da frente.*lados/);
  const semFrente = structuredClone(REL_OK);
  delete semFrente.empunhadura.frente;
  assert.match(validarPega(semFrente, lerPega(gltfPega()), MARCA).join('\n'), /mão da frente/);
  const faltaDedo = structuredClone(REL_OK);
  delete faltaDedo.empunhadura.e.lados.dedosMM.minimo;
  assert.match(validarPega(faltaDedo, lerPega(gltfPega()), MARCA).join('\n'), /minimo/);
  const indicadorTrocado = structuredClone(REL_OK);
  indicadorTrocado.empunhadura.e.lados.dedosMM.indicador = 6.1;
  assert.match(validarPega(indicadorTrocado, lerPega(gltfPega()), MARCA).join('\n'), /indicador.*lado do polegar/);
  // perto demais do meio da arma (dentro da margem) também reprova: o dedo não chegou ao outro lado
  const noMeio = structuredClone(REL_OK);
  noMeio.empunhadura.e.lados.dedosMM.anelar = -(LIMITES_DA_PEGA.ladoMM - 0.5);
  assert.match(validarPega(noMeio, lerPega(gltfPega()), MARCA).join('\n'), /anelar/);
  const polegarTrocado = structuredClone(REL_OK);
  polegarTrocado.empunhadura.e.lados.polegarMM = -15;
  assert.match(validarPega(polegarTrocado, lerPega(gltfPega()), MARCA).join('\n'), /polegar.*lado dos dedos/);
  // a mão do gatilho, quando traz os lados, passa pela mesma conta
  const gatilho = structuredClone(REL_OK);
  gatilho.empunhadura.d.lados.dedosMM.medio = 3;
  assert.match(validarPega(gatilho, lerPega(gltfPega()), MARCA).join('\n'), /empunhadura d.*medio/);
});

test('validarPega exige na mão da frente o polegar reto e deitado na arma (sem a curva)', () => {
  const semPolegar = structuredClone(REL_OK);
  delete semPolegar.empunhadura.e.polegar;
  assert.match(validarPega(semPolegar, lerPega(gltfPega()), MARCA).join('\n'), /polegar.*deitado/);
  // a versão que o usuário recusou: o polegar em arco (MCP 35°, IP 17°), só com a ponta encostada
  const curvo = structuredClone(REL_OK);
  curvo.empunhadura.e.polegar.curvaGraus = 52;
  assert.match(validarPega(curvo, lerPega(gltfPega()), MARCA).join('\n'), /curva/);
  const pontaNoAr = structuredClone(REL_OK);
  for (const i of [3, 4, 5]) pontaNoAr.empunhadura.e.polegar.trechosMM[i] = LIMITES_DA_PEGA.contatoMM + 0.5;
  assert.match(validarPega(pontaNoAr, lerPega(gltfPega()), MARCA).join('\n'), /distal/);
  const baseLonge = structuredClone(REL_OK);
  baseLonge.empunhadura.e.polegar.trechosMM[0] = LIMITES_DA_PEGA.polegarFolgaMM + 1;
  assert.match(validarPega(baseLonge, lerPega(gltfPega()), MARCA).join('\n'), /proximal/);
});

test('validarPega exige os dedos que abraçam a arma lado a lado, sem leque', () => {
  const semJuntos = structuredClone(REL_OK);
  delete semJuntos.empunhadura.e.juntosMM;
  assert.match(validarPega(semJuntos, lerPega(gltfPega()), MARCA).join('\n'), /mão da frente.*lado a lado/);
  const faltaPar = structuredClone(REL_OK);
  delete faltaPar.empunhadura.e.juntosMM['indicador-medio'];
  assert.match(validarPega(faltaPar, lerPega(gltfPega()), MARCA).join('\n'), /indicador-medio/);
  // o leque da primeira pega da mão da frente da AK: a falange média do mínimo a 8,53 mm da do anelar
  const leque = structuredClone(REL_OK);
  leque.empunhadura.e.juntosMM['anelar-minimo'][0] = 8.53;
  assert.match(validarPega(leque, lerPega(gltfPega()), MARCA).join('\n'), /anelar-minimo.*leque/);
  // só a falange média conta: a ponta do dedo que dobra mais pode sair da do vizinho
  const pontas = structuredClone(REL_OK);
  pontas.empunhadura.e.juntosMM['indicador-medio'][1] = 20;
  assert.deepEqual(validarPega(pontas, lerPega(gltfPega()), MARCA), []);
  // a mão do gatilho passa pela mesma conta nos dedos que abraçam o punho
  const gatilho = structuredClone(REL_OK);
  gatilho.empunhadura.d.juntosMM['medio-anelar'][0] = LIMITES_DA_PEGA.dedosJuntosMM + 1;
  assert.match(validarPega(gatilho, lerPega(gltfPega()), MARCA).join('\n'), /empunhadura d.*medio-anelar/);
});

test('a AK de verdade: a pega no .glb, a marca igual à do luvas.glb e a saída aprovada', () => {
  const ak = join(ROOT, 'assets', 'armas', 'ak47', 'ak47.glb');
  const luvas = join(ROOT, 'assets', 'maos', 'luvas.glb');
  assert.ok(existsSync(ak) && existsSync(luvas), 'rode npm run blender -- construir todas');
  const p = lerPega(lerGlb(readFileSync(ak)).json);
  const marcaLuvas = lerGlb(readFileSync(luvas)).json.nodes.find((n) => n.name === 'luvas').extras.marca;
  assert.deepEqual(p.marca, marcaLuvas);
  assert.deepEqual(validarSaida('ak47', ROOT).problemas, []);
});
```

Run: `node --test tests/luvasSaida.test.js tests/luvasGlb.test.js tests/modeloDobras.test.js tests/pegaGlb.test.js`
Expected: FAIL — # tests 4 # pass 0 # fail 4 .

- [ ] **A implementação** — `tools/blender/armas/luvas.py`, `tools/blender/armas/empunhadura_regras.py`, `tools/blender/armas/empunhadura_arma.py`, `tools/blender/armas/empunhadura_pega.py`, `tools/blender/saidaLuvas.mjs`, `tools/blender/saidaPega.mjs`, `src/characters/hands/pega.js`, `src/characters/hands/modeloDobras.js`, `tools/blender/armas/assar.py`, `tools/blender/armas/exportar.py`, `tools/blender/armas/conferir.py`, `tools/blender/armas/principal.py`, `tools/blender.mjs`, `tools/blender/saida.mjs`:

```python file=tools/blender/armas/luvas.py
# O alvo `luvas` do principal.py (Fase 4.1b; desenho em docs/superpowers/specs/2026-09-26-4.1b-luvas-e-empunhadura-design.md,
# seção 3): as luvas construídas pela ficha (tools/blender/refs/luvas.json) e o registro (src/data/luvas.js), os dois
# validados pelo lançador.
#   construir: a luva direita — a malha base (maos_gaiola.py, subdividida 1 nível) e as peças de detalhe
#              (maos_detalhes.py) com os materiais de fábrica da pintura de Massa Crua, e o modelo alto (maos_alto.py:
#              a base no nível 4 com as rugas, as costuras e as máscaras, e as peças com os respiros e as nervuras) —,
#              o rig (maos_rig.py: a armadura, as peças juntadas com os pesos da superfície), o modelo das correções
#              das dobras (maos_correcoes.py, os parâmetros guardados na luva) e as poses de teste (maos_poses.py e
#              validar_maos.py), as medidas contra a ficha (±1 %), o assentamento das peças, os triângulos contra o
#              orçamento, a UV por costuras (assar.uv_por_costuras: sem sobreposição, a densidade de cada ilha a
#              0,6–1,6 da mediana), o braço esquerdo espelhado (maos_rig.espelhar, com as correções dele e a
#              conferência de que, em cada pose de teste espelhada, ele é o direito espelhado a 0,01 mm), a marca do
#              rig de cada braço, a prova do modelo das dobras (vértices avaliados nas poses, que o jogo refaz em
#              JS) e a .blend da conferência em tools/blender/conferencia/luvas/; aprovada, assa as
#              texturas `luvas_n` e `luvas_m` (2048, do modelo alto) e grava o luvas.glb (exportar.exportar_luvas) e o
#              relatório em assets/maos/;
#   validar:   reabre a .blend e refaz as medidas, as contas e as poses;
#   conferir:  as vistas do modelo alto (costas, palma, os dois lados, de frente para as pontas, três quartos, de perto
#              dos nós, dos dedos e do punho) nas duas facções, as zonas em cores chapadas e a gaiola em arame por cima
#              das costas.
# As linhas `MASSACRE-*` da saída são lidas pelo lançador; reprovado sai com código 1.
import json
import os
import sys
import time

import bmesh
import bpy
import numpy as np
from mathutils import Vector

from . import (assar, estudio, exportar, maos, maos_alto, maos_correcoes, maos_detalhes, maos_gaiola, maos_medidas, maos_poses, maos_rig,
               materiais, validar_maos)
from .unidades import S

TOLERANCIA = 0.01  # as medidas da malha a ±1 % dos alvos da ficha
ASSENTAMENTO_MM = 0.1  # a base das paredes de cada peça a 0,2 ± 0,1 mm dentro da luva: sem vão nem sobra
# Cores chapadas das zonas nas vistas `zonas_*` (a conferência das fronteiras entre os materiais).
_CORES_DAS_ZONAS = {'couro': (0.62, 0.36, 0.16), 'tecido': (0.16, 0.30, 0.52), 'reforco': (0.85, 0.78, 0.20)}
_CENTRO = (0.085, 0.0, 0.0)  # metros: mais ou menos o meio da mão, do punho às pontas
ZONAS = ('couro', 'tecido', 'reforco')  # os materiais da luva de jogo depois de juntar as peças, nesta ordem
REFORCO = ZONAS.index('reforco')
UV_MARGEM_PX = 8
DENSIDADE = (0.6, 1.6)  # a densidade de texel de cada ilha, relativa à mediana (as armas da 4.1a)
ESPELHO_MM = 0.01  # o braço esquerdo em pose contra o direito espelhado
# As gaiolas do assar (assar.assar_grupos), medidas pela normal de jogo nos vértices e no centro das faces: a base alta
# fica de −0,46 a +0,53 mm da de jogo — 0,8 mm para fora e 1,6 mm de raio, sem alcançar o dedo vizinho na membrana
# (com os 2 e 4 mm das armas, o raio pegava o dedo do lado e assava cunhas tortas nas ilhas dos dedos); as peças altas,
# de −1,6 a +1,42 mm das de jogo (as bordas arredondadas para dentro) — 1,9 mm para fora e 3,8 mm de raio.
# A prova do modelo das dobras no relatório (o teste de paridade do jogo): 1 vértice em 11 e as poses que exercitam o
# skin, as dobras dos dedos e do polegar e a do pulso.
PROVA_AMOSTRA = 11
PROVA_POSES = ('repouso', 'punho', 'pulso', 'apontar')
GAIOLA_BASE_MM = (0.8, 1.6)
GAIOLA_PECAS_MM = (1.9, 3.8)


def _material_de_zona(zona):
    m = bpy.data.materials.get(f'zona_{zona}') or bpy.data.materials.new(f'zona_{zona}')
    m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*_CORES_DAS_ZONAS[zona], 1)
    b.inputs['Roughness'].default_value = 0.7
    return m


def _colecao(nome):
    col = bpy.data.collections.get(nome) or bpy.data.collections.new(nome)
    if col.name not in bpy.context.scene.collection.children:
        bpy.context.scene.collection.children.link(col)
    return col


def _relatorio(ctx, mao, residuo=None):
    """As contas da luva de jogo direita (a base com as peças juntadas e o rig): medidas, triângulos, as poses de teste
    (com o assentamento das peças) e a marca do rig; e os problemas."""
    luva = bpy.data.objects['luva_d']
    rig = bpy.data.objects['rig_d']
    maos_rig.posar(rig, {})
    medidas = maos_medidas.medir_mao(luva, mao)
    me = luva.data
    tris = {'base': sum(len(p.vertices) - 2 for p in me.polygons if p.material_index != REFORCO),
            'detalhes': sum(len(p.vertices) - 2 for p in me.polygons if p.material_index == REFORCO)}
    tris['luva'] = tris['base'] + tris['detalhes']
    limite = ctx['orcamento']['triangulos'] // 2
    contato, rel_contato, problemas_contato = maos_poses.poses_de_teste(luva, rig, mao, REFORCO)
    testes = {'repouso': {}, **contato, **{p: maos_rig.pose_de_teste(p, mao) for p in ('aberta', 'pulso')}}
    poses, problemas_poses = validar_maos.validar_poses(luva, rig, mao, REFORCO, testes)
    poses['contato'] = rel_contato
    rig['poses_de_teste'] = json.dumps({n: maos_rig.pose_json(p) for n, p in testes.items()})
    assentamento = poses['repouso']['assentamentoMM']
    rel = {'triangulos': tris, 'vertices': len(me.vertices), 'grupos': sorted(g.name for g in luva.vertex_groups),
           'assentamentoMM': assentamento, 'medidas': medidas, 'poses': poses,
           'marca': {lado: maos_rig.marca(bpy.data.objects[f'rig_{lado}']) for lado in ('d', 'e')
                     if f'rig_{lado}' in bpy.data.objects},
           'correcoes': {'juntas': [j['junta'] for j in json.loads(luva['correcoes'])['juntas']]}}
    if residuo is not None:
        rel['residuoAjusteMM'] = round(residuo, 5)
    problemas = list(problemas_contato) + list(problemas_poses)
    for nome, m in medidas.items():
        desvio = m['mm'] / m['alvo'] - 1
        if abs(desvio) > TOLERANCIA:
            problemas.append(f"{nome}: {m['mm']:.2f} mm contra {m['alvo']:.2f} mm ({desvio * 100:+.2f} %, tolerância ±1 %)")
    if tris['luva'] > limite:
        problemas.append(f"triângulos: {tris['luva']} numa luva (orçamento {limite}, a metade dos dois braços)")
    if assentamento > ASSENTAMENTO_MM:
        problemas.append(f'assentamento: a base de uma peça a {assentamento:.3f} mm fora dos 0,2 mm dentro da luva '
                         f'(tolerância {ASSENTAMENTO_MM} mm)')
    return rel, problemas


def _uv_e_espelho(ctx, mao, luva, rig, colecao):
    """A UV da luva direita pelas costuras e o braço esquerdo espelhado dela (as mesmas UV), com as correções das
    dobras dele. Devolve (luva_e, rig_e, a conta da UV, o maior desvio do espelho em mm, os problemas)."""
    lado = ctx['orcamento']['textura']
    assar.uv_por_costuras([luva], lado, UV_MARGEM_PX)
    uv = {'sobreposicao': assar.sobreposicao_uv([luva]), **assar.densidade_por_ilha(luva, lado)}
    luva_e, rig_e = maos_rig.espelhar(luva, rig, mao, colecao)
    modelo_d = maos_correcoes.Modelo(luva, rig, mao, REFORCO)
    modelo_e = maos_correcoes.Modelo(luva_e, rig_e, mao, REFORCO)
    luva_e['correcoes'] = json.dumps(modelo_e.parametros(), separators=(',', ':'))
    desvio = 0.0
    for pose in (maos_rig.pose_de_json(p) for p in json.loads(rig['poses_de_teste']).values()):
        d = modelo_d.avaliar(pose)
        d[:, 1] *= -1.0
        desvio = max(desvio, float(np.abs(modelo_e.avaliar(maos_rig.espelhar_pose(pose)) - d).max()))
    prova = {'d': _prova_do_modelo(modelo_d, rig), 'e': _prova_do_modelo(modelo_e, rig, espelhada=True)}
    maos_rig.posar(rig, {})
    maos_rig.posar(rig_e, {})
    problemas = []
    if uv['sobreposicao']:
        problemas.append(f"UV: {uv['sobreposicao']} texels cobertos por mais de uma face")
    if not DENSIDADE[0] <= uv['minimo'] <= uv['maximo'] <= DENSIDADE[1]:
        problemas.append(f"UV: a densidade das ilhas de {uv['minimo']} a {uv['maximo']} da mediana (dentro de "
                         f"{DENSIDADE[0]}–{DENSIDADE[1]})")
    if desvio > ESPELHO_MM:
        problemas.append(f'espelho: o braço esquerdo a {desvio:.4f} mm do direito espelhado (máximo {ESPELHO_MM} mm)')
    return luva_e, rig_e, uv, round(desvio, 5), problemas, prova


def _prova_do_modelo(modelo, rig, espelhada=False):
    """A prova do modelo das dobras para o jogo (modeloDobras.js refaz as mesmas contas em JS): uma amostra de vértices
    (1 em PROVA_AMOSTRA, pelo índice do Blender) avaliada nas poses de PROVA_POSES (no braço esquerdo, as da direita
    espelhadas), em mm no referencial do braço no Blender, e cada giro da pose como eixo (no referencial do braço, em
    repouso: o do osso levado pela orientação de repouso dele) e ângulo em radianos — a forma que não depende do
    referencial local dos ossos, que o glTF converte."""
    poses = json.loads(rig['poses_de_teste'])  # as poses de teste ficam no rig direito
    lado = modelo.malha.lado
    n = len(modelo.malha.p)
    idx = list(range(0, n, PROVA_AMOSTRA))
    saida = {'vertices': idx, 'poses': {}}
    for nome in PROVA_POSES:
        pose = maos_rig.pose_de_json(poses[nome])
        if espelhada:
            pose = maos_rig.espelhar_pose(pose)
        giros = {}
        for osso, q in pose.items():
            if q.angle < 1e-9:
                continue
            eixo = (modelo.malha.rig.data.bones[f'{osso}_{lado}'].matrix_local.to_3x3() @ q.axis).normalized()
            giros[osso] = [round(c, 7) for c in eixo] + [round(q.angle, 7)]
        pts = modelo.avaliar(pose)
        saida['poses'][nome] = {'giros': giros, 'mm': np.round(pts[idx], 4).tolist()}
    return saida


def _alvos_do_assar(luva):
    """Duas cópias da luva de jogo em repouso para o assar por grupos: a base (couro e tecido) e as peças (o reforço)."""
    alvos = []
    for nome, pecas in (('base', False), ('pecas', True)):
        me = luva.data.copy()
        bm = bmesh.new()
        bm.from_mesh(me)
        bmesh.ops.delete(bm, geom=[f for f in bm.faces if (f.material_index == REFORCO) != pecas], context='FACES')
        bm.to_mesh(me)
        bm.free()
        ob = bpy.data.objects.new(f'assar_{nome}', me)
        bpy.context.scene.collection.objects.link(ob)
        alvos.append(ob)
    return alvos


def _etapa(t0, nome):
    """Linha de progresso para o lançador (o modelo alto leva um tempo)."""
    print('MASSACRE-ETAPA', json.dumps({'etapa': nome, 's': round(time.time() - t0, 1)}, ensure_ascii=False), flush=True)


def montar_jogo(mao, M, colecao, antes_do_rig=None):
    """A luva de jogo direita com o rig: a malha base (maos_gaiola.py, subdividida 1 nível), as peças de detalhe
    (maos_detalhes.py) juntadas nela com os pesos da superfície, a armadura e as correções das dobras guardadas na luva.
    `antes_do_rig(peças)` roda com as peças ainda soltas (o modelo alto usa elas). O mesmo caminho serve às luvas e ao
    solver de empunhadura de cada arma (empunhadura_pega.py): as duas saem do mesmo esqueleto (D4, a marca do rig).
    Devolve (luva, rig, o resíduo do ajuste da gaiola)."""
    luva, residuo = maos_gaiola.malha_base(mao, colecao, {z: M[z] for z in maos_gaiola.ZONAS_BASE}, 'luva_d',
                                           subdividir=1)
    pecas, _ = maos_detalhes.construir(mao, luva, colecao, M['reforco'])
    if antes_do_rig:
        antes_do_rig(pecas)
    rig = maos_rig.armadura(mao, colecao, 'd')
    maos_rig.pesos(luva, pecas, 'd')
    maos_rig.ligar(luva, rig)
    luva['correcoes'] = json.dumps(maos_correcoes.Modelo(luva, rig, mao, REFORCO).parametros(), separators=(',', ':'))
    return luva, rig, residuo


def construir(ctx):
    t0 = time.time()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    os.makedirs(ctx['conferencia'], exist_ok=True)
    mao = maos.Mao(ctx['ficha'])
    M = materiais.materiais_das_luvas(ctx['pinturas']['massaCrua'])
    jogo = _colecao('jogo')
    altos = []

    def alto(pecas):
        _etapa(t0, 'malha de jogo e detalhes')
        altos.extend(maos_alto.construir(mao, M, pecas, _colecao('alto'), lambda nome: _etapa(t0, nome)))

    luva, rig, residuo = montar_jogo(mao, M, jogo, alto)
    _etapa(t0, 'rig, pesos e correções das dobras')
    gaiola, _ = maos_gaiola.malha_base(mao, _colecao('gaiola'), {z: _material_de_zona(z) for z in maos_gaiola.ZONAS_BASE},
                                       'gaiola_d', subdividir=0)
    gaiola.hide_render = True
    rel, problemas = _relatorio(ctx, mao, residuo)
    _etapa(t0, 'medidas e poses de teste')
    luva_e, rig_e, uv, espelho, problemas_uv, prova = _uv_e_espelho(ctx, mao, luva, rig, jogo)
    problemas += problemas_uv
    rel.update({'uv': uv, 'espelhoMM': espelho, 'marca': {'d': maos_rig.marca(rig), 'e': maos_rig.marca(rig_e)},
                'provaDoModelo': prova,
                'alto': {'objetos': len(altos), 'faces': sum(len(o.data.polygons) for o in altos)},
                'entradas': {'hash': ctx['hash']}})
    _etapa(t0, 'UV e o braço esquerdo')
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ctx['conferencia'], 'luvas.blend'))
    if problemas:
        rel['segundos'] = round(time.time() - t0, 1)
        print('MASSACRE-LUVAS', json.dumps(rel, ensure_ascii=False))
        print('MASSACRE-REPROVADO', json.dumps(problemas, ensure_ascii=False))
        sys.exit(1)
    pasta = ctx['saida']
    os.makedirs(pasta, exist_ok=True)
    base_alta = bpy.data.objects['luva_d_alto']
    pecas_altas = [o for o in bpy.data.collections['alto'].objects if o.type == 'MESH' and o is not base_alta]
    base, pecas_jogo = _alvos_do_assar(luva)
    assar.assar_grupos([([base_alta], [base], *GAIOLA_BASE_MM), (pecas_altas, [pecas_jogo], *GAIOLA_PECAS_MM)],
                       ctx['orcamento']['textura'], UV_MARGEM_PX, pasta, 'luvas_n', 'luvas_m')
    for ob in (base, pecas_jogo):
        bpy.data.objects.remove(ob)
    _etapa(t0, 'assar')
    exportar.exportar_luvas(pasta, [(luva, rig), (luva_e, rig_e)], rel['marca'])
    _etapa(t0, 'exportar')
    rel.update({'luvas': True, 'aprovado': True, 'problemas': [],
                'arquivos': {n: os.path.getsize(os.path.join(pasta, n))
                             for n in ('luvas.glb', 'luvas_n.webp', 'luvas_m.webp')},
                'segundos': round(time.time() - t0, 1)})
    exportar.gravar_relatorio(pasta, 'luvas', rel)
    print('MASSACRE-LUVAS', json.dumps(rel, ensure_ascii=False))


def validar(ctx):
    bpy.ops.wm.open_mainfile(filepath=os.path.join(ctx['conferencia'], 'luvas.blend'))
    rel, problemas = _relatorio(ctx, maos.Mao(ctx['ficha']))
    print('MASSACRE-VALIDACAO', json.dumps({**rel, 'problemas': problemas}, ensure_ascii=False))
    if problemas:
        sys.exit(1)


def _pintar(pintura_ou_zonas):
    """Troca os materiais das luvas de jogo e altas (bases e peças): por uma pintura (os de fábrica) ou pelas cores
    chapadas das zonas."""
    if pintura_ou_zonas == 'zonas':
        M = {z: _material_de_zona(z) for z in _CORES_DAS_ZONAS}
    else:
        M = materiais.materiais_das_luvas(pintura_ou_zonas)
    for nome_col in ('jogo', 'alto'):
        for ob in bpy.data.collections[nome_col].objects:
            if ob.type != 'MESH':
                continue
            if 'zona' in ob:
                ob.data.materials[0] = M[ob['zona']]
            else:
                for i in range(len(ob.data.materials)):
                    ob.data.materials[i] = M[ZONAS[i]]


def conferir(ctx, amostras=96):
    bpy.ops.wm.open_mainfile(filepath=os.path.join(ctx['conferencia'], 'luvas.blend'))
    sc = bpy.context.scene
    pasta = ctx['conferencia']
    bpy.data.collections['jogo'].hide_render = True  # as vistas são do modelo alto
    fundo = estudio.montar(_CENTRO)
    fundo.hide_render = True  # as vistas de baixo e dos lados veriam o chão entre a câmera e a mão
    # O estúdio das armas ilumina de cima; a palma pede uma luz de baixo, fria e fraca (a do rebatedor do set).
    baixo = bpy.data.lights.new('baixo', 'AREA')
    baixo.size, baixo.energy, baixo.color = 0.9, 9.0, (0.92, 0.95, 1.0)
    ob_baixo = bpy.data.objects.new('baixo', baixo)
    sc.collection.objects.link(ob_baixo)
    ob_baixo.location = Vector(_CENTRO) + Vector((0.05, -0.25, -0.7))
    ob_baixo.rotation_euler = (Vector(_CENTRO) - ob_baixo.location).to_track_quat('-Z', 'Y').to_euler()
    dispositivo = estudio.render(1600, 1100, amostras)
    c = Vector(_CENTRO)
    nos = Vector((0.094, 0.0, 0.012))  # a linha dos nós, por cima
    punho = Vector((-0.022, -0.01, 0.0))  # a tira do punho
    vistas = {
        'costas': (c + Vector((0.0, 0.0, 0.6)), c, 0.3),
        'palma': (c + Vector((0.0, 0.0, -0.6)), c, 0.3),
        'polegar': (c + Vector((0.0, 0.6, 0.0)), c, 0.3),
        'minimo': (c + Vector((0.0, -0.6, 0.0)), c, 0.3),
        'pontas': (c + Vector((0.6, 0.0, 0.05)), c, 0.2),
        'tres_quartos': (c + Vector((0.28, -0.3, 0.3)), c, None),
        'perto_nos': (nos + Vector((0.07, -0.09, 0.11)), nos, None),
        'perto_punho': (punho + Vector((0.02, -0.12, 0.1)), punho, None),
        'perto_dedos': (Vector((0.18, -0.08, 0.1)), Vector((0.13, 0.0, 0.0)), None),
        'perto_palma': (Vector((0.07, -0.05, -0.15)), Vector((0.05, 0.0, -0.01)), None),
    }
    arquivos = []

    def fotografar(nome, pos, alvo, orto):
        sc.camera = estudio.camera(nome, pos, alvo, 45, orto)
        sc.render.filepath = os.path.join(pasta, f'{nome}.png')
        bpy.ops.render.render(write_still=True)
        arquivos.append(sc.render.filepath)

    for nome, (pos, alvo, orto) in vistas.items():
        fotografar(nome, pos, alvo, orto)
    # A outra facção: as vistas que mostram a pintura inteira.
    _pintar(ctx['pinturas']['tropa'])
    for nome in ('costas', 'palma', 'tres_quartos', 'perto_nos', 'perto_punho'):
        pos, alvo, orto = vistas[nome]
        fotografar(f'tropa_{nome}', pos, alvo, orto)
    # As zonas em cores chapadas, de costas e de palma.
    _pintar('zonas')
    fotografar('zonas_costas', *vistas['costas'])
    fotografar('zonas_palma', *vistas['palma'])
    # A gaiola em arame por cima das costas.
    gaiola = bpy.data.objects['gaiola_d']
    arame = gaiola.modifiers.new('arame', 'WIREFRAME')
    arame.thickness = 0.35 * S
    m_arame = bpy.data.materials.new('arame')
    m_arame.use_nodes = True
    em = m_arame.node_tree.nodes.new('ShaderNodeEmission')
    em.inputs['Color'].default_value = (1.0, 0.8, 0.1, 1)
    em.inputs['Strength'].default_value = 3.0
    m_arame.node_tree.links.new(em.outputs[0], m_arame.node_tree.nodes['Material Output'].inputs[0])
    gaiola.data.materials.clear()
    gaiola.data.materials.append(m_arame)
    gaiola.hide_render = False
    fotografar('costas_arame', *vistas['costas'])
    # As poses de teste na luva de jogo com o rig (pintura de Massa Crua), de três quartos e de baixo.
    gaiola.hide_render = True
    _pintar(ctx['pinturas']['massaCrua'])
    bpy.data.collections['jogo'].hide_render = False
    bpy.data.collections['alto'].hide_render = True
    # (a luva de jogo pelo modelo das luvas — o skin e as correções das dobras — numa cópia sem rig, como no jogo)
    luva = bpy.data.objects['luva_d']
    rig = bpy.data.objects['rig_d']
    modelo = maos_correcoes.Modelo(luva, rig, maos.Mao(ctx['ficha']), REFORCO)
    poses = json.loads(rig['poses_de_teste'])
    luva.hide_render = True
    for nome in ('punho', 'apontar', 'mesa', 'aberta', 'pulso'):
        ob = modelo.para_malha(f'pose_{nome}', bpy.data.collections['jogo'], maos_rig.pose_de_json(poses[nome]))
        fotografar(f'pose_{nome}', *vistas['tres_quartos'])
        fotografar(f'pose_{nome}_palma', c + Vector((0.12, -0.25, -0.35)), c, None)
        bpy.data.objects.remove(ob)
    maos_rig.posar(rig, {})
    return arquivos, dispositivo
```

```python file=tools/blender/armas/empunhadura_regras.py
# As regras da pega por categoria do viewmodel (Fase 4.1b; desenho em docs/superpowers/specs/2026-09-26-4.1b-luvas-e-
# empunhadura-design.md, seção 6.2, passo 4): onde cada mão entra na arma e em que ordem fecha. A do `rifle` (esta
# subfase); as outras categorias entram com as armas delas (4.1c e 4.1d). Cada arma pode corrigir os números no script
# dela (`EMPUNHADURA = {'direita': {...}, 'esquerda': {...}}`, as mesmas chaves), e passa pelas mesmas validações.
#  - mão direita (o punho): a luva entra com a linha dos nós quase paralela à frente do punho (15° de diagonal no
#    plano da palma: o punho cruza a palma da membrana do polegar para a base do mínimo, como na pega de força), a palma
#    rente à lateral direita (o giro em volta do eixo do punho em 0°: com a palma girada para abraçar a quina de trás, a
#    base dela se afastava do punho e o polegar não alcançava o outro lado), a MCP do indicador 27,6 mm atrás e 11,7 mm
#    abaixo do ponto do gatilho (a membrana alta no punho e o médio logo embaixo do guarda-mato), e chega pela normal da
#    palma até encostar; o médio, o anelar e o mínimo fecham em volta do punho; o indicador põe a polpa na face da frente
#    do gatilho a 60 % da altura dele, com pelo menos 1 mm do guarda-mato e do resto da arma; o polegar cruza para o
#    lado esquerdo do punho (a polpa encostada o mais à esquerda que ele alcança);
#  - a mão da frente (FRENTE; regra fixa do usuário de 2026-09-27, para toda arma que tem mão da frente — no guarda-mão,
#    no cano, na telha da escopeta): só o polegar de um lado da arma e os outros quatro dedos do outro, como a pega da
#    AK no CS:GO. A palma por baixo, os dedos para a direita (o polegar para a frente), girada em volta da vertical (os
#    dedos para a frente, o pulso para trás) e um pouco em volta do eixo do cano (a palma para cima, a base do polegar
#    na quina de baixo à esquerda), chegando pela normal da palma até encostar; o indicador, o médio, o
#    anelar e o mínimo fecham por baixo e sobem pelo lado direito; o polegar fica reto e deitado na face esquerda,
#    encostado nela e apontando para a frente e para cima (empunhadura_polegar.deitar_na_arma), como na pega "thumb
#    break" — os quatro dedos por baixo do guarda-mão e o polegar esticado ao longo do lado. Primeiro o polegar ia "o mais
#    à esquerda possível" e subia na vertical por cima do guarda-mão; depois, mirando um ponto com a polpa, dobrava em
#    arco (MCP 35°, IP 17°) com só a ponta encostada — o usuário recusou as duas. A validação reprova a arma se a polpa
#    do polegar não ficar do lado dele, se a de um dos quatro dedos não passar para o outro (`lados`) ou se o polegar não
#    ficar reto e deitado (a curva, a distal encostando, a proximal perto).
# A CMC do polegar fica na pose de pegar (a abdução palmar e a flexão no máximo da ficha) já na chegada da palma: com o
# polegar afastado, a palma encostava com a tenar tangente à arma, e qualquer movimento do polegar levava a pele da
# tenar 4 a 6 mm para dentro dela.
# Referenciais: a base de cada mão leva os eixos da luva (X para as pontas, Y para o lado do polegar na mão direita, Z
# para as costas) aos do soquete; as giradas vêm antes, no referencial do soquete, e a diagonal depois, no plano da
# palma (com o sinal trocado na esquerda, que é a direita espelhada em Y).
import copy
import math

from mathutils import Matrix, Vector

from .maos import DEDOS4

RIFLE = {
    'direita': {
        'soquete': 'mao_d',
        'base': ((1.0, 0.0, 0.0), (0.0, 0.0, -1.0), (0.0, 1.0, 0.0)),
        'giros': (('Z', 0.0),),
        'diagonal': 15.0,
        # a MCP do indicador a partir do ponto do gatilho (mm, Blender: x, y, z), antes de encostar a palma
        'ancora': {'ponto': 'mcp_indicador', 'de': 'gatilho', 'mm': (-27.6, -40.0, -11.7)},
        'chegada': (45.0, 60.0),
        'dedos': ('medio', 'anelar', 'minimo'),
        'gatilho': {'altura': 0.6, 'abertura': 20.0, 'raio': 8.0, 'folga': 1.0},
        'polegar': {'lado': (0.0, 1.0, 0.0), 'peso': 4.0},
    },
}
# A mão da frente (ver o cabeçalho): a base de toda categoria; cada uma ajusta os números dela (a âncora, as giradas, o
# alvo do polegar) sem mudar a forma — o polegar de um lado e os quatro dedos do outro.
FRENTE = {
    'soquete': 'mao_e',
    'frente': True,
    'base': ((0.0, -1.0, 0.0), (-1.0, 0.0, 0.0), (0.0, 0.0, -1.0)),
    # 35° em volta da vertical e −10° em volta do cano, com 20° de diagonal no plano da palma: das varreduras de
    # 2026-09-27 com o polegar deitado (giro, diagonal e altura da palma; a última com a penetração medida sem o limite
    # das buscas, que deixava passar um indicador 7 mm dentro da arma), a que deixa o polegar mais rente à face sem outro
    # problema — a distal encostada e a proximal em cunha de 4 a 6,5 mm, porque a base sai da quina de baixo. Girando a
    # palma para a direita os dedos não alcançam o lado direito; com a palma mais à esquerda a cunha cresce
    'giros': (('Z', 35.0), ('X', -10.0)),
    'diagonal': 20.0,
    # o centro da palma a partir do soquete (mm), antes de encostar a palma (mais para trás, o calcanhar da mão bate na
    # curva do carregador da AK)
    'ancora': {'ponto': 'palma', 'de': 'soquete', 'mm': (0.0, 10.0, -30.0)},
    'chegada': (40.0, 60.0),
    'dedos': DEDOS4,
    # os quatro dedos lado a lado, encostados no vizinho (empunhadura_arma.juntar_dedos): fechando cada um sozinho, eles
    # saíam em leque pelo lado direito da arma
    'juntar': True,
    'gatilho': None,
    # o polegar deitado reto na face `face` (a esquerda), encostado ao longo da falange proximal e da distal, as duas
    # apontando para `eixo` (unitários, no referencial da arma: a boca, subindo um pouco) —
    # empunhadura_polegar.deitar_na_arma
    'polegar': {'deitado': True, 'face': (0.0, 1.0, 0.0), 'eixo': (1.0, 0.0, 0.6)},
    # o lado do polegar (unitário, no referencial da arma, a partir do plano do meio dela) e os dedos que vão ao outro
    'lados': {'polegar': (0.0, 1.0, 0.0), 'dedos': DEDOS4},
}
RIFLE['esquerda'] = copy.deepcopy(FRENTE)
REGRAS = {'rifle': RIFLE}


def regra(categoria, correcoes=None):
    """A regra da categoria com as correções da arma (o `EMPUNHADURA` do script dela) por cima."""
    if categoria not in REGRAS:
        raise ValueError(f'sem regra de empunhadura para a categoria {categoria} (tem: {", ".join(REGRAS)})')
    r = copy.deepcopy(REGRAS[categoria])
    for mao, valores in (correcoes or {}).items():
        if mao not in r:
            raise ValueError(f'EMPUNHADURA: mão desconhecida {mao}')
        for chave, valor in valores.items():
            if chave not in r[mao]:
                raise ValueError(f'EMPUNHADURA: chave desconhecida {mao}.{chave}')
            r[mao][chave] = valor
    return r


def rotacao(r, soquete, lado):
    """A rotação (3×3) da luva no referencial da arma: o soquete, as giradas, a base e a diagonal no plano da palma."""
    R = soquete.to_3x3().normalized()
    for eixo, graus in r['giros']:
        R = R @ Matrix.Rotation(math.radians(graus), 3, eixo)
    R = R @ Matrix(r['base'])  # as linhas; as colunas são os eixos da luva no referencial do soquete
    sinal = 1.0 if lado == 'd' else -1.0
    return R @ Matrix.Rotation(math.radians(sinal * r['diagonal']), 3, 'Z')


def lado_do_polegar(r):
    return Vector(r['polegar']['lado']).normalized()
```

```python file=tools/blender/armas/empunhadura_arma.py
# A mão na arma, do solver de empunhadura (Fase 4.1b; desenho em docs/superpowers/specs/2026-09-26-4.1b-luvas-e-
# empunhadura-design.md, seção 6.2): a arma como obstáculo, a luva posta no soquete e os dedos fechando nela.
#  - a arma: as peças do perto (as móveis em repouso) numa BVH em mm; a distância com sinal de um ponto (negativa
#    dentro) pela face mais próxima e a normal dela;
#  - a luva na arma: a luva de jogo pelo modelo das luvas (maos_correcoes.Modelo: o skin e as correções das dobras) na
#    pose, levada pela matriz do encaixe (o referencial da luva — o pulso na origem — no da arma, em mm). A penetração
#    é a dos vértices (a validação da seção 6.3), de um conjunto deles (os de um osso, os de um dedo) ou de todos;
#  - a chegada: a mão aberta (os dedos esticados, no mínimo da AAOS) transladada ao longo de uma direção — a normal da
#    palma, na pega — até os vértices do corpo da mão encostarem (bisseção até 0,02 mm);
#  - os dedos: fechando juntos em volta da arma, como no "autograsp" (Miller e Allen, GraspIt!): a MCP, a PIP e a DIP
#    avançam em passos, a DIP a 2/3 da PIP (o acoplamento natural do dedo); quando uma falange encosta, a junta dela e
#    as de cima param (não podem andar sem empurrar a falange para dentro) e as de baixo seguem; cada toque é achado
#    por bisseção (0,05° na junta que mais anda) e as juntas param nos limites da ficha. Fechar uma junta de cada vez,
#    da base para a ponta, parava o dedo esticado com a ponta na frente do punho e a falange proximal no ar;
#  - os dedos juntos (a mão da frente, `juntar_dedos`): o de fora gira na MCP para o vizinho e fecha de novo, até os
#    dois se encostarem lado a lado; `folgas_entre_dedos` mede o que sobra entre eles (a validação da pega);
#  - o dedo num alvo (o indicador no gatilho): a IK das três juntas mais a abertura pela cinemática da cadeia, e a
#    chegada pela normal do alvo até encostar, como o polegar (empunhadura_polegar.py).
# Unidades: mm e graus além do repouso; o Blender em metros.
import itertools
import math

import numpy as np
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree

from . import empunhadura, maos_rig
from .empunhadura import CONTATO_MM, TOLERANCIA_GRAUS
from .maos import DEDOS4
from .maos_capsulas import mm
from .unidades import S

PERTO_DA_ARMA_MM = 6.0  # só os vértices a menos disso da arma entram na conta da penetração (o resto está fora)
PASSO_GRAUS = 3.0  # o passo do fechar em volta da arma (a junta que mais anda)
VELOCIDADES = (1.0, 1.0, 2.0 / 3.0)  # MCP, PIP, DIP: a DIP acompanha 2/3 da PIP
CHEGADA_MM = 40.0  # de onde a palma chega pela normal dela
ACIMA_MM = (4.0, 8.0, 14.0, 20.0)
ALEM = 0.5
GRADE_GRAUS = 10.0
PASSO_INICIAL = 4.0
PASSO_FINAL = 0.25
PESO_NORMAL_MM = 15.0
PESO_ARMA = 5.0
POLPA_T = 0.55
# os dedos juntos: o de fora e o vizinho para onde ele gira, a partir do médio; a bisseção da abertura
JUNTAR = (('anelar', 'medio'), ('minimo', 'anelar'), ('indicador', 'medio'))
PASSO_JUNTAR_GRAUS = 0.25
JUNTAR_ATRAVESSA_MM = 0.15  # metade do limite da validação da luva (0,3 mm), com folga
PARES_VIZINHOS = (('indicador', 'medio'), ('medio', 'anelar'), ('anelar', 'minimo'))


class Arma:
    """A malha de jogo da arma numa BVH em mm (referencial do Blender)."""

    def __init__(self, objetos):
        verts, polys = [], []
        for ob in objetos:
            mw = ob.matrix_world
            base = len(verts)
            verts += [(mw @ v.co) / S for v in ob.data.vertices]
            polys += [[base + i for i in p.vertices] for p in ob.data.polygons]
        self.bvh = BVHTree.FromPolygons(verts, polys)

    def distancia(self, p, limite=None):
        """Distância com sinal (mm) do ponto à superfície, negativa dentro; None além do `limite`."""
        r = self.bvh.find_nearest(p) if limite is None else self.bvh.find_nearest(p, limite)
        if r[0] is None:
            return None
        co, n, _i, d = r
        return -d if (Vector(p) - co).dot(n) < 0.0 else d

    def raio(self, origem, direcao, limite=1000.0):
        """(ponto, normal) da primeira face no raio, ou (None, None)."""
        co, n, _i, _d = self.bvh.ray_cast(origem, direcao, limite)
        return co, n


class NaArma:
    """Uma luva (o Colisor de empunhadura.py) na arma: a matriz do encaixe (mm, luva → arma) e as contas contra ela."""

    def __init__(self, col, arma, encaixe=None):
        self.col, self.arma = col, arma
        self.encaixe = encaixe or Matrix.Identity(4)
        self.por_osso = {}
        for i, dono in enumerate(col.dono):
            self.por_osso.setdefault(dono, []).append(i)

    def vertices(self, ossos):
        return [i for o in ossos for i in self.por_osso.get(o, ())]

    def pontos(self, pose, encaixe=None):
        """As posições (mm, numpy) da luva na pose, no referencial da arma."""
        e = np.array(encaixe or self.encaixe)
        p = self.col.modelo.avaliar(pose)
        return p @ e[:3, :3].T + e[:3, 3]

    def penetracao(self, pts, indices=None, limite=PERTO_DA_ARMA_MM):
        """A maior entrada (mm, ≥ 0) dos vértices `indices` (todos, sem eles) na arma. Com o `limite` (o padrão, nas
        buscas do solver), só os vértices a até ele da superfície contam — rápido, mas um vértice mais fundo que isso
        dentro da arma passa despercebido; a validação da pega mede sem limite (`limite=None`)."""
        pior = 0.0
        for i in range(len(pts)) if indices is None else indices:
            d = self.arma.distancia(pts[i], limite)
            if d is not None and -d > pior:
                pior = -d
        return pior

    def entrada_quadrada(self, pts, indices):
        """A soma dos quadrados das entradas (mm) dos vértices `indices` na arma: a conta suave da penetração, para as
        buscas."""
        soma = 0.0
        for i in indices:
            d = self.arma.distancia(pts[i], PERTO_DA_ARMA_MM)
            if d is not None and d < 0.0:
                soma += d * d
        return soma

    def encosto(self, pts, indices):
        """A menor distância (mm) dos vértices `indices` à superfície da arma (negativa: dentro)."""
        return min(self.arma.distancia(pts[i]) for i in indices)


def mao_aberta(mao, polegar):
    """A mão aberta para chegar na arma: os quatro dedos no mínimo da AAOS (esticados, sem abrir) e o polegar da pose
    `polegar` (afastado)."""
    lim, rep = mao.f['limites'], mao.rep
    m = polegar
    for d in DEDOS4:
        for i, j in ((1, 'mcp'), (2, 'pip'), (3, 'dip')):
            m = m.com(f'{d}_{i}', flexao=lim[j][0] - rep[j])
    return m


def encostar(na, m, direcao, encaixe, indices=None, chegada=CHEGADA_MM, alcance=None):
    """O encaixe transladado ao longo de `direcao` (unitária, no referencial da arma) do ponto de chegada, `chegada` mm
    para trás, até a luva na pose `m` (os vértices `indices`, ou todos) encostar na arma. Devolve (encaixe, quanto
    andou além do encaixe dado, em mm)."""
    pose = m.pose()
    p0 = na.pontos(pose, encaixe)

    def em(d):
        t = Matrix.Translation(direcao * (d - chegada))
        return t @ encaixe

    def cruza(d):
        desloc = np.array(direcao * (d - chegada))
        return na.penetracao(p0 + desloc, indices) > CONTATO_MM

    if cruza(0.0):
        raise RuntimeError(f'a mão cruza a arma já {chegada} mm antes do ponto de chegada')
    a, b = 0.0, chegada + (chegada if alcance is None else alcance)
    if not cruza(b):
        raise RuntimeError(f"a mão não encosta na arma em {b} mm de chegada")
    while b - a > 0.02:
        c = (a + b) / 2
        if cruza(c):
            b = c
        else:
            a = c
    return em(a), a - chegada


def agarrar(na, mao, m, dedo):
    """O dedo fechando em volta da arma (ver o cabeçalho) a partir da pose `m`. Uma falange encosta quando entra na arma
    mais que o contato além do que já entrava no começo (o dedo esticado da mão aberta pode começar raspando numa
    peça); só contam as falanges que alguma junta ativa ainda move. Devolve (pose, {osso: 'contato' | 'limite'})."""
    lim, rep = mao.f['limites'], mao.rep
    ossos = [f'{dedo}_{i}' for i in (1, 2, 3)]
    maximo = {ossos[0]: lim['mcp'][1] - rep['mcp'], ossos[1]: lim['pip'][1] - rep['pip'],
              ossos[2]: lim['dip'][1] - rep['dip']}
    segmentos = [na.vertices([o]) for o in ossos]
    pts0 = na.pontos(m.pose())
    base = [na.penetracao(pts0, s) for s in segmentos]
    ativos = [True, True, True]
    parou = {}

    def com_passo(de, s):
        r = de
        for k, osso in enumerate(ossos):
            if ativos[k]:
                r = r.com(osso, flexao=min(de.flexao.get(osso, 0.0) + s * VELOCIDADES[k], maximo[osso]))
        return r

    def encostados(pose_m):
        pts = na.pontos(pose_m.pose())
        movidos = [k for k in range(3) if any(ativos[:k + 1])]
        return [k for k in movidos if na.penetracao(pts, segmentos[k]) > base[k] + CONTATO_MM]

    while any(ativos):
        for k, osso in enumerate(ossos):
            if ativos[k] and m.flexao.get(osso, 0.0) >= maximo[osso] - 1e-6:
                ativos[k] = False
                parou[osso] = 'limite'
        if not any(ativos):
            break
        tentativa = com_passo(m, PASSO_GRAUS)
        tocam = encostados(tentativa)
        if not tocam:
            m = tentativa
            continue
        a, b = 0.0, PASSO_GRAUS
        while b - a > TOLERANCIA_GRAUS:
            c = (a + b) / 2
            if encostados(com_passo(m, c)):
                b = c
            else:
                a = c
        m = com_passo(m, a)
        # a falange mais perto da base que encostou: a junta dela e as de cima param (sempre há uma ativa entre elas,
        # pela conta de `encostados`, então cada volta para pelo menos uma junta)
        k = min(encostados(com_passo(m, b - a)) or tocam)
        for j in range(k + 1):
            if ativos[j]:
                ativos[j] = False
                parou[ossos[j]] = 'contato'
    return m, parou


def juntar_dedos(col, na, mao, m, aberta, dedos, atravessa):
    """Os dedos lado a lado, como numa mão fechada de verdade: dobrados, os dedos convergem para a palma. Fechando cada
    um sozinho na arma a partir da abertura do repouso, os da mão da frente saíam em leque (na AK, a ponta de um a 12 a
    17 mm da do vizinho). A partir do médio, o de fora gira na MCP para o vizinho (a abertura, até a ABERTURA_MAXIMA
    além do repouso) e fecha de novo na arma a partir da mão aberta (`aberta`); fica a maior abertura (bisseção de
    PASSO_JUNTAR_GRAUS) em que ele não atravessa o vizinho nem entra na arma e em que a luva inteira não se atravessa
    mais que JUNTAR_ATRAVESSA_MM (`atravessa(pontos)`: a conta da validação, validar_maos.atravessa — a membrana entre
    dois dedos, perto das MCP, amassa quando eles se juntam). Devolve (pose, {dedo: graus girados})."""
    girou = {}
    for dedo, vizinho in JUNTAR:
        if dedo not in dedos or vizinho not in dedos:
            continue
        osso = f'{dedo}_1'
        # a pele entre os dois, perto das MCP, é a membrana entre eles (como em separar_vizinhos)
        longe = (osso, f'{vizinho}_1')
        A = col.triangulos(empunhadura._falanges(dedo), longe)
        B = col.triangulos(empunhadura._falanges(vizinho), longe)
        vertices = na.vertices(empunhadura._falanges(dedo))
        sinal = -empunhadura.para_fora(dedo, col.lado)  # para o vizinho
        ab0 = m.aberturas.get(osso, 0.0)
        inicio = m
        for i in (1, 2, 3):
            o = f'{dedo}_{i}'
            inicio = inicio.com(o, flexao=aberta.flexao.get(o, 0.0))

        def fechado(g, inicio=inicio, osso=osso, ab0=ab0, sinal=sinal, dedo=dedo):
            return agarrar(na, mao, inicio.com(osso, abertura=ab0 + sinal * g), dedo)[0]

        def cabe(p, A=A, B=B, vertices=vertices):
            pose = p.pose()
            return (col.profundidade(pose, A, B) <= CONTATO_MM
                    and na.penetracao(na.pontos(pose), vertices, limite=None) <= CONTATO_MM
                    and atravessa(col.modelo.pontos(pose)) <= JUNTAR_ATRAVESSA_MM)

        a, b = 0.0, empunhadura.ABERTURA_MAXIMA - abs(ab0)
        if cabe(fechado(b)):
            a = b
        else:
            while b - a > PASSO_JUNTAR_GRAUS:
                c = (a + b) / 2
                if cabe(fechado(c)):
                    a = c
                else:
                    b = c
        if a > 0.0:
            m = fechado(a)
            girou[dedo] = round(sinal * a, 2)
    return m, girou


def folgas_entre_dedos(col, pose, dedos):
    """A folga (mm) entre cada par de dedos vizinhos, na falange média e na distal: a menor distância entre os vértices
    de uma e os da mesma falange do vizinho, na luva posada (no referencial dela). {'indicador-medio': [média,
    distal], ...}."""
    pts = np.asarray(col.modelo.pontos(pose))
    por = {}
    for i, dono in enumerate(col.dono):
        por.setdefault(dono, []).append(i)
    folgas = {}
    for a, b in PARES_VIZINHOS:
        if a not in dedos or b not in dedos:
            continue
        par = []
        for f in (2, 3):
            ia, ib = por.get(f'{a}_{f}', []), por.get(f'{b}_{f}', [])
            kd = KDTree(len(ib))
            for k, i in enumerate(ib):
                kd.insert(Vector(pts[i]), k)
            kd.balance()
            par.append(round(min(kd.find(Vector(pts[i]))[2] for i in ia), 2))
        folgas[f'{a}-{b}'] = par
    return folgas


class CadeiaDedo:
    """A cadeia de um dedo (as três falanges) para a IK: as matrizes de repouso (mm) relativas, a mão posada (a matriz do
    pai da falange proximal, no referencial da arma) e a polpa no referencial do osso distal."""

    def __init__(self, na, dedo, pose_mao):
        col = na.col
        rig, lado = col.rig, col.lado
        self.dedo = dedo
        self.ossos = [f'{dedo}_{i}' for i in (1, 2, 3)]
        bs = [rig.data.bones[f'{o}_{lado}'] for o in self.ossos]
        rep = [mm(b.matrix_local) for b in bs]
        pai = bs[0].parent
        self.rel = [mm(pai.matrix_local).inverted() @ rep[0], rep[0].inverted() @ rep[1], rep[1].inverted() @ rep[2]]
        self.comp = [b.length / S for b in bs]
        maos_rig.posar(rig, pose_mao)
        self.pai = na.encaixe @ mm(rig.pose.bones[pai.name].matrix)
        maos_rig.posar(rig, {})
        # a polpa de repouso: do osso distal a 55 %, pelo lado da palma (+Z do osso), até a superfície da luva
        pts = col.modelo.pontos({})
        bvh = BVHTree.FromPolygons([tuple(p) for p in pts], col.tris)
        m3 = rep[2]
        dentro = m3 @ Vector((0.0, self.comp[2] * POLPA_T, 0.0))
        lado_polpa = (m3.to_3x3() @ Vector((0.0, 0.0, 1.0))).normalized()
        co, _n, _i, _d = bvh.ray_cast(dentro, lado_polpa)
        self.polpa = m3.inverted() @ co
        para_local = m3.inverted()
        self.lado_da_polpa = [i for i, dono in enumerate(col.dono)
                              if dono == self.ossos[2] and (para_local @ pts[i]).z > 0.0]

    def matrizes(self, g):
        """As matrizes (mm, na arma) das três falanges com g = {'abertura', 'mcp', 'pip', 'dip'} além do repouso."""
        q = [empunhadura._flexao(g['mcp']) @ empunhadura._abertura(g['abertura']), empunhadura._flexao(g['pip']),
             empunhadura._flexao(g['dip'])]
        m, ms = self.pai, []
        for rel, qi in zip(self.rel, q):
            m = m @ rel @ qi.to_matrix().to_4x4()
            ms.append(m)
        return ms

    def polpa_em(self, g):
        m = self.matrizes(g)[2]
        return m @ self.polpa, (m.to_3x3() @ Vector((0.0, 0.0, 1.0))).normalized()


GRAUS_DO_DEDO = ('abertura', 'mcp', 'pip', 'dip')


def limites_do_dedo(mao, abertura):
    lim, rep = mao.f['limites'], mao.rep
    return {'abertura': (-abertura, abertura), 'mcp': (lim['mcp'][0] - rep['mcp'], lim['mcp'][1] - rep['mcp']),
            'pip': (lim['pip'][0] - rep['pip'], lim['pip'][1] - rep['pip']),
            'dip': (lim['dip'][0] - rep['dip'], lim['dip'][1] - rep['dip'])}


def _eixo(cadeia, ms):
    """Os pontos do eixo das falanges (5 por osso): a conta rápida da entrada do dedo na arma, na IK."""
    pts = []
    for m, c in zip(ms, cadeia.comp):
        for t in (0.1, 0.3, 0.5, 0.7, 0.9):
            pts.append(m @ Vector((0.0, c * t, 0.0)))
    return pts


def _custo_dedo(cadeia, arma, g, alvo, normal, raio_mm):
    ms = cadeia.matrizes(g)
    p, lado = cadeia.polpa_em(g)
    entra = 0.0
    for q in _eixo(cadeia, ms):
        d = arma.distancia(q, raio_mm + 4.0)
        if d is not None and d < raio_mm:
            entra += (raio_mm - d) ** 2
    return (p - alvo).length_squared + (PESO_NORMAL_MM * (1.0 + lado.dot(normal))) ** 2 + PESO_ARMA ** 2 * entra


def ik_dedo(cadeia, arma, alvo, normal, lim, raio_mm, inicio=None):
    """Os graus do dedo (além do repouso) que põem a polpa no alvo, de frente para ele e com as falanges fora da arma
    (o eixo a `raio_mm` da superfície): a grade de 10° e a busca de padrão até 0,25° (só a busca, a partir de
    `inicio`)."""
    def valores(a, b):
        n = max(1, math.ceil((b - a) / GRADE_GRAUS))
        return [a + (b - a) * k / n for k in range(n + 1)]

    if inicio is not None:
        melhor = dict(inicio)
        custo = _custo_dedo(cadeia, arma, melhor, alvo, normal, raio_mm)
    else:
        melhor, custo = None, math.inf
        for comb in itertools.product(*(valores(*lim[k]) for k in GRAUS_DO_DEDO)):
            g = dict(zip(GRAUS_DO_DEDO, comb))
            c = _custo_dedo(cadeia, arma, g, alvo, normal, raio_mm)
            if c < custo:
                melhor, custo = g, c
    passo = PASSO_INICIAL
    while passo >= PASSO_FINAL:
        melhorou = False
        for grau in GRAUS_DO_DEDO:
            for s in (1.0, -1.0):
                g = dict(melhor)
                g[grau] = min(max(g[grau] + s * passo, lim[grau][0]), lim[grau][1])
                c = _custo_dedo(cadeia, arma, g, alvo, normal, raio_mm)
                if c < custo - 1e-9:
                    melhor, custo, melhorou = g, c, True
        if not melhorou:
            passo /= 2
    return melhor


def _com_dedo(m, dedo, g):
    return (m.com(f'{dedo}_1', flexao=g['mcp'], abertura=g['abertura']).com(f'{dedo}_2', flexao=g['pip'])
            .com(f'{dedo}_3', flexao=g['dip']))


def dedo_no_alvo(na, mao, m, dedo, alvo, normal, abertura_max, raio_mm, folga=None):
    """O dedo com a polpa no alvo (a normal para fora da superfície), chegando pela normal até encostar na arma.
    `folga(pts)`, se vier, é uma conta extra (mm) que tem de ficar ≥ 0 no caminho (o guarda-mato). Devolve (pose,
    relatório)."""
    lim = limites_do_dedo(mao, abertura_max)
    cadeia = CadeiaDedo(na, dedo, m.pose())
    ik = ik_dedo(cadeia, na.arma, alvo, normal, lim, raio_mm)
    dedo_v = na.vertices(cadeia.ossos)

    def cruza(g):
        pts = na.pontos(_com_dedo(m, dedo, g).pose())
        if na.penetracao(pts, dedo_v) > CONTATO_MM:
            return True
        return folga is not None and folga(pts) < 0.0

    for acima in ACIMA_MM:
        de = ik_dedo(cadeia, na.arma, alvo + normal * acima, normal, lim, raio_mm, inicio=ik)
        if not cruza(de):
            break
    else:
        raise RuntimeError(f'o {dedo} cruza a arma mesmo com a polpa {ACIMA_MM[-1]} mm acima do alvo')

    def em(s):
        return {k: min(max(de[k] + (ik[k] - de[k]) * s, lim[k][0]), lim[k][1]) for k in GRAUS_DO_DEDO}

    anda = max(abs(ik[k] - de[k]) for k in GRAUS_DO_DEDO)
    tol = TOLERANCIA_GRAUS / max(anda, 1e-6)
    a, b = 0.0, 1.0 + ALEM
    if cruza(em(b)):
        while b - a > tol:
            s = (a + b) / 2
            if cruza(em(s)):
                b = s
            else:
                a = s
        encostou = True
    else:
        a, encostou = b, False
    g = em(a)
    m = _com_dedo(m, dedo, g)
    pts = na.pontos(m.pose())
    polpa, _lado = cadeia.polpa_em(g)
    rel = {'graus': {k: round(v, 2) for k, v in g.items()}, 'encostou': encostou, 'chegouDeMM': acima,
           'polpaEncostaMM': round(na.encosto(pts, cadeia.lado_da_polpa), 2),
           'polpaAoAlvoMM': round((polpa - alvo).length, 2)}
    return m, rel, cadeia
```

```python file=tools/blender/armas/empunhadura_pega.py
# A pega de uma arma realista (Fase 4.1b; desenho em docs/superpowers/specs/2026-09-26-4.1b-luvas-e-empunhadura-
# design.md, seções 6.1 a 6.4; plano, Tarefa 7 e D1–D5): o solver de empunhadura dentro do construir da arma.
#  - as luvas: a luva de jogo direita com o rig, montada pelo mesmo caminho do alvo `luvas` (luvas.montar_jogo), e a
#    esquerda espelhada dela — as duas com a marca do rig (D4) que o luvas.glb traz;
#  - cada mão, pela regra da categoria (empunhadura_regras.py) com as correções da arma: a luva entra no soquete da mão
#    (a âncora, as giradas, a diagonal) e chega pela normal da palma até encostar (empunhadura_arma.encostar), com a CMC
#    do polegar na pose de pegar; os dedos da regra fecham em volta da arma (empunhadura_arma.agarrar) e os vizinhos se
#    separam (e, na mão da frente, se juntam lado a lado: empunhadura_arma.juntar_dedos); o indicador vai ao gatilho
#    (empunhadura_arma.dedo_no_alvo); o polegar pousa do lado da regra (empunhadura_polegar.alvo_na_arma e
#    fechar_no_alvo) ou, na mão da frente, deitado reto na face do lado dele e apontando para a boca
#    (empunhadura_polegar.deitar_na_arma);
#  - a validação (seção 6.3, bloqueia a exportação): nenhum vértice da luva a mais de 0,3 mm dentro da arma; a palma
#    (com a tenar e a hipotenar), cada dedo da regra, a polpa do indicador (no gatilho) e a do polegar a no máximo 1 mm
#    da arma; a luva sem se atravessar e sem afinar nas juntas (validar_maos.conferir_uma, os limites das poses de
#    teste); os ângulos dentro dos limites da ficha; na mão da frente (regra do usuário de 2026-09-27), só o polegar de
#    um lado e os quatro dedos do outro (_lados: a polpa de cada um a pelo menos LADO_MM do plano do meio da arma, do
#    lado certo) e o polegar reto e deitado na arma (_polegar_deitado: a curva, a distal encostando, a proximal perto);
#    os dedos que abraçam a arma lado a lado, sem leque (a falange média de cada um a no máximo JUNTOS_MM da do vizinho,
#    empunhadura_arma.folgas_entre_dedos; a mão da frente os junta, empunhadura_arma.juntar_dedos);
#  - as sondas (o `luvas_contato` do jogo mede nelas): o vértice de cada contato mais perto da arma e a distância dele;
#  - a saída (seção 6.4): o nó `pega` com a marca e as sondas nos extras, os nós `pega_mao_d`/`pega_mao_e` (o
#    referencial do osso `mao` de cada braço na pose, no da arma) e a armadura `pega_luvas` (os dois braços) com a ação
#    `empunhadura` de um quadro nas rotações dos 17 ossos de dedo de cada mão (D1: a animação glTF).
# Unidades: mm e graus além do repouso (os totais no relatório); o Blender em metros.
import json
import time

import bpy
from mathutils import Matrix, Quaternion, Vector
from mathutils.bvhtree import BVHTree

from . import (empunhadura, empunhadura_arma as EA, empunhadura_polegar as polegar, empunhadura_regras as regras,
               luvas, maos, maos_rig, materiais, validar_maos)
from .maos import DEDOS4
from .maos_capsulas import mm
from .unidades import S

PENETRACAO_MM = 0.3
CONTATO_MM = 1.0
LADO_MM = 5.0  # o `ladoMM` de LIMITES_DA_PEGA (src/data/luvas.js): a polpa a pelo menos isto do meio, do lado certo
POLEGAR_CURVA_GRAUS = 20.0  # o `polegarCurvaGraus`: a MCP mais a IP do polegar deitado da mão da frente
POLEGAR_FOLGA_MM = 8.0  # o `polegarFolgaMM`: nenhum trecho do polegar deitado mais longe que isto da arma
# o `dedosJuntosMM`: a falange média de cada dedo que abraça a arma a no máximo isto da do vizinho — menos da metade da
# largura dela (17 a 19 mm na ficha); o leque da mão da frente antes de juntar_dedos chegava a 8,5 mm, a mão do gatilho
# fica em 2,5 e 3,3 mm
JUNTOS_MM = 8.0
# os ossos de dedo da pega (seção 6.4: 17 por mão)
OSSOS_DE_DEDO = (('polegar_1', 'polegar_2', 'polegar_3')
                 + tuple(f'{d}_{i}' for d in ('indicador', 'medio') for i in (1, 2, 3))
                 + tuple(f'{d}_{i}' for d in ('anelar', 'minimo') for i in (0, 1, 2, 3)))
LADOS = (('d', 'direita'), ('e', 'esquerda'))
PALMA = ('mao', 'polegar_1', 'anelar_0', 'minimo_0')


def montar_luvas(ctx, colecao):
    """As duas luvas de jogo com o rig (sem assar nem UV), na coleção, fora do render. Devolve (mao, {lado: (luva,
    rig)})."""
    mao = maos.Mao(ctx['luvas']['ficha'])
    M = materiais.materiais_das_luvas(ctx['luvas']['pinturas']['massaCrua'])
    luva, rig, _residuo = luvas.montar_jogo(mao, M, colecao)
    luva_e, rig_e = maos_rig.espelhar(luva, rig, mao, colecao)
    for ob in (luva, luva_e):
        ob.hide_render = True
    return mao, {'d': (luva, rig), 'e': (luva_e, rig_e)}


def _centro_da_palma(col):
    """O ponto da superfície da palma no meio da mão de repouso: do meio do osso `mao` para a palma (−Z da luva)."""
    pts = col.modelo.pontos({})
    bvh = BVHTree.FromPolygons([tuple(p) for p in pts], col.tris)
    co, _n, _i, _d = bvh.ray_cast((col.cabeca['mao'] + col.cabeca['medio_1']) / 2, Vector((0.0, 0.0, -1.0)))
    return co


def ponto_do_gatilho(gatilho, altura):
    """(ponto, normal) da face da frente do gatilho a `altura` dele (a fração de cima para baixo), no plano do meio da
    arma (mm): o raio que vem da frente acerta a face em que o dedo apoia."""
    pts = [(gatilho.matrix_world @ v.co) / S for v in gatilho.data.vertices]
    topo, fundo = max(p.z for p in pts), min(p.z for p in pts)
    frente = max(p.x for p in pts) + 20.0
    ponto, normal = EA.Arma([gatilho]).raio(Vector((frente, 0.0, topo - altura * (topo - fundo))), Vector((-1.0, 0.0, 0.0)))
    if ponto is None:
        raise RuntimeError('o raio do gatilho não acertou a face da frente dele')
    return ponto, normal


def _vertices_do_corpo(col):
    """Os vértices que chegam na arma com a palma: a luva sem os dedos e sem as falanges do polegar."""
    livres = {f'{d}_{i}' for d in DEDOS4 for i in (1, 2, 3)} | set(polegar.LIVRE)
    return [i for i, o in enumerate(col.dono) if o not in livres]


def _pegar(col, na, mao, r, soquete, gatilho, base, lado):
    """Uma mão na arma pela regra `r` (ver o cabeçalho). Devolve (pose, relatório do solver)."""
    rel = {}
    lim = polegar.limites(mao)
    m = EA.mao_aberta(mao, polegar.afastar(col, mao, empunhadura.Mao()))
    m = polegar._com_graus(m, polegar.Cadeia(col, mao, {}),
                           {'abducao': lim['abducao'][1], 'cmc': lim['cmc'][1], 'rotacao': 0.0, 'mcp': lim['mcp'][0],
                            'ip': lim['ip'][0]})
    R = regras.rotacao(r, soquete.matrix_world, lado)
    anc = r['ancora']
    ponto_da_luva = col.cabeca['indicador_1'] if anc['ponto'] == 'mcp_indicador' else _centro_da_palma(col)
    alvo_g = normal_g = None
    if r['gatilho']:
        alvo_g, normal_g = ponto_do_gatilho(gatilho, r['gatilho']['altura'])
    origem = alvo_g if anc['de'] == 'gatilho' else soquete.matrix_world.translation / S
    na.encaixe = Matrix.Translation(origem + Vector(anc['mm']) - R @ ponto_da_luva) @ R.to_4x4()
    palma = (R @ Vector((0.0, 0.0, -1.0))).normalized()
    na.encaixe, andou = EA.encostar(na, m, palma, na.encaixe, _vertices_do_corpo(col), *r['chegada'])
    rel['palmaAndouMM'] = round(andou, 2)
    parou = {}
    aberta = m
    for d in r['dedos']:
        m, p = EA.agarrar(na, mao, m, d)
        parou.update(p)
    m, vizinhos = empunhadura.separar_vizinhos(col, m, [d for d in DEDOS4 if d in r['dedos']])
    rel.update({'dedosPararam': parou, 'vizinhos': vizinhos})
    if r.get('juntar'):
        topo = validar_maos.Topologia(col.luva, luvas.REFORCO)
        m, rel['juntar'] = EA.juntar_dedos(col, na, mao, m, aberta, r['dedos'],
                                           lambda pts: validar_maos.atravessa(pts, topo)[0])
    if r['gatilho']:
        g = r['gatilho']
        guarda = na.vertices(['indicador_2', 'indicador_3'])

        def folga(pts):
            return min(base.distancia(pts[i]) for i in guarda) - g['folga']

        m, rel['indicador'], _cadeia = EA.dedo_no_alvo(na, mao, m, 'indicador', alvo_g, normal_g, g['abertura'],
                                                       g['raio'], folga)
        rel['indicador']['folgaDoResto'] = round(folga(na.pontos(m.pose())) + g['folga'], 2)
    cadeia = polegar.Cadeia(col, mao, {o: q for o, q in m.pose().items() if not o.startswith('polegar')})
    p = r['polegar']
    if p.get('deitado'):
        eixo = (na.encaixe.inverted().to_3x3() @ Vector(p['eixo'])).normalized()
        m, rel['polegar'] = polegar.deitar_na_arma(col, mao, m, na, eixo, Vector(p['face']).normalized())
    else:
        alvo_p, normal_p = polegar.alvo_na_arma(cadeia, na, m, lim, regras.lado_do_polegar(r), p['peso'])
        m, rel['polegar'] = polegar.fechar_no_alvo(col, mao, m, alvo_p, normal_p, None, na=na)
    return m, rel


def _contatos(col, na, mao, pts, r):
    """{contato: [vértice, distância em mm]} da regra — a palma, cada dedo que fecha, a polpa do indicador (no gatilho)
    e a do polegar —, com o vértice de cada um mais perto da arma (as sondas)."""
    # a palma com as eminências (a tenar sobre o metacarpo do polegar e a hipotenar sobre os do anelar e do mínimo): é
    # nelas que a palma apoia num punho reto — o oco do meio fica afastado (o `palmaMeioMM` do relatório)
    grupos = {'palma': na.vertices(PALMA)}
    for d in r['dedos']:
        grupos[d] = na.vertices([f'{d}_{i}' for i in (1, 2, 3)])
    if r['gatilho']:
        grupos['indicador_gatilho'] = EA.CadeiaDedo(na, 'indicador', {}).lado_da_polpa
    grupos['polegar'] = polegar.Cadeia(col, mao, {}).lado_da_polpa
    saida = {}
    for nome, idx in grupos.items():
        dist = {i: na.arma.distancia(pts[i]) for i in idx}
        i = min(dist, key=dist.get)
        saida[nome] = [i, round(dist[i], 3)]
    return saida


def _lados(col, na, mao, pts, r):
    """Os lados da regra (a mão da frente): onde fica a polpa do polegar e a de cada dedo de `r['lados']['dedos']` no
    eixo do lado do polegar (mm, a partir do plano do meio da arma, que passa pela origem dela) — o centro dos vértices
    do lado da polpa do osso distal de cada um —, e os problemas: o polegar a menos de LADO_MM do lado dele ou um dedo a
    menos de LADO_MM do outro lado."""
    eixo = Vector(r['lados']['polegar']).normalized()

    def onde(indices):
        centro = sum((Vector(pts[i]) for i in indices), Vector()) / len(indices)
        return round(centro.dot(eixo), 2)

    lados = {'polegarMM': onde(polegar.Cadeia(col, mao, {}).lado_da_polpa),
             'dedosMM': {d: onde(EA.CadeiaDedo(na, d, {}).lado_da_polpa) for d in r['lados']['dedos']}}
    problemas = []
    if lados['polegarMM'] < LADO_MM:
        problemas.append(f"o polegar a {lados['polegarMM']:.2f} mm do meio da arma (tem de ficar do lado dele, a pelo "
                         f"menos {LADO_MM} mm)")
    for d, v in lados['dedosMM'].items():
        if v > -LADO_MM:
            problemas.append(f'o {d} a {v:.2f} mm do meio da arma, do lado do polegar ou no meio (tem de passar para o '
                             f'outro lado, a pelo menos {LADO_MM} mm)')
    return lados, problemas


def _polegar_deitado(rel_polegar):
    """Os problemas do polegar deitado da mão da frente (o relatório de empunhadura_polegar.deitar_na_arma): a curva (a
    MCP mais a IP) além de POLEGAR_CURVA_GRAUS, a falange distal sem encostar (o trecho dela mais perto a mais que o
    contato) ou algum trecho a mais de POLEGAR_FOLGA_MM da arma."""
    t = rel_polegar['trechosMM']
    meio = len(t) // 2
    problemas = []
    if rel_polegar['curvaGraus'] > POLEGAR_CURVA_GRAUS:
        problemas.append(f"o polegar da frente com {rel_polegar['curvaGraus']}° de curva (máximo {POLEGAR_CURVA_GRAUS}°): "
                         'tem de ficar reto, deitado na arma')
    if min(t[meio:]) > CONTATO_MM:
        problemas.append(f'a falange distal do polegar da frente não encosta na arma ({min(t[meio:]):.2f} mm)')
    for i, v in enumerate(t):
        if v > POLEGAR_FOLGA_MM:
            problemas.append(f"a falange {'proximal' if i < meio else 'distal'} do polegar da frente a {v:.2f} mm da arma "
                             f'(máximo {POLEGAR_FOLGA_MM} mm)')
    return problemas


def _angulos(mao, m):
    """(os ângulos totais das juntas dos dedos, os problemas de limite): cada flexão dentro da AAOS da ficha e cada
    abertura dentro da faixa do solver (±20° além do repouso)."""
    lim, rep = mao.f['limites'], mao.rep
    faixas = {1: 'mcp', 2: 'pip', 3: 'dip'}
    totais, problemas = {}, []
    for osso, g in sorted(m.flexao.items()):
        if osso.startswith('polegar') or osso.endswith('_0'):
            continue
        junta = faixas[int(osso[-1])]
        a, b = lim[junta]
        totais[osso] = round(g + rep[junta], 2)
        if not a - 0.01 <= totais[osso] <= b + 0.01:
            problemas.append(f'{osso}: {totais[osso]}° fora da {junta} da ficha ({a}–{b}°)')
    for osso, g in sorted(m.aberturas.items()):
        if abs(g) > empunhadura.ABERTURA_MAXIMA + 0.01:
            problemas.append(f'{osso}: abertura de {g:.2f}° (máximo ±{empunhadura.ABERTURA_MAXIMA}°)')
    return totais, problemas


def resolver(ctx, mao, bracos, perto, soquetes, correcoes):
    """A pega das duas mãos na arma (as peças do perto, as móveis em repouso). Devolve ({lado: {'encaixe': mm,
    'pose': {osso: quaternion}, 'contatos': ...}}, a seção `empunhadura` do relatório, os problemas)."""
    t0 = time.time()
    r_cat = regras.regra(ctx['categoria'], correcoes)
    arma = EA.Arma([o for k, o in perto.items() if not k.startswith('_')])
    base = EA.Arma([perto['base']])
    soq = {o.name[len('soquete_'):]: o for o in soquetes}
    pega, rel, problemas = {}, {}, []
    for lado, nome in LADOS:
        r = r_cat[nome]
        luva, rig = bracos[lado]
        col = empunhadura.Colisor(luva, rig, mao, luvas.REFORCO)
        na = EA.NaArma(col, arma)
        m, rel_m = _pegar(col, na, mao, r, soq[r['soquete']], perto.get('gatilho'), base, lado)
        pose = m.pose()
        pts = na.pontos(pose)
        penetracao = na.penetracao(pts, limite=None)  # sem o limite das buscas: um dedo inteiro dentro da arma conta
        contatos = _contatos(col, na, mao, pts, r)
        conta, problemas_luva = validar_maos.conferir_uma(col.modelo, luva, luvas.REFORCO, f'pega {nome}', pose)
        totais, problemas_angulos = _angulos(mao, m)
        meio = min(na.arma.distancia(pts[i]) for i in na.vertices(['mao']))
        rel[lado] = {**rel_m, 'penetracaoMM': round(penetracao, 3), 'contatosMM': {k: v[1] for k, v in contatos.items()},
                     'palmaMeioMM': round(meio, 2), 'luva': conta, 'angulos': totais}
        if r.get('lados'):
            rel[lado]['lados'], problemas_lados = _lados(col, na, mao, pts, r)
            problemas += [f'pega {nome}: {p}' for p in problemas_lados]
        if r['polegar'].get('deitado'):
            problemas += [f'pega {nome}: {p}' for p in _polegar_deitado(rel_m['polegar'])]
        rel[lado]['juntosMM'] = EA.folgas_entre_dedos(col, pose, r['dedos'])
        for par, (media, _distal) in rel[lado]['juntosMM'].items():
            if media > JUNTOS_MM:
                problemas.append(f'pega {nome}: {par} com a falange média a {media:.2f} mm uma da outra (máximo '
                                 f'{JUNTOS_MM} mm): os dedos em leque, não lado a lado')
        if r.get('frente'):
            rel['frente'] = lado
        if penetracao > PENETRACAO_MM:
            problemas.append(f'pega {nome}: a luva entra {penetracao:.2f} mm na arma (máximo {PENETRACAO_MM} mm)')
        for k, (_i, d) in contatos.items():
            if d > CONTATO_MM:
                problemas.append(f'pega {nome}: o contato {k} a {d:.2f} mm da arma (máximo {CONTATO_MM} mm)')
        problemas += problemas_luva + [f'pega {nome}: {p}' for p in problemas_angulos]
        pega[lado] = {'encaixe': na.encaixe.copy(), 'pose': pose, 'contatos': contatos}
    rel['marca'] = {lado: maos_rig.marca(bracos[lado][1]) for lado, _n in LADOS}
    rel['segundos'] = round(time.time() - t0, 1)
    return pega, rel, problemas


def guardar(bracos, pega):
    """A pega de cada braço nos rigs (o encaixe e a pose), para as vistas de perto do conferir na .blend."""
    for lado, dados in pega.items():
        bracos[lado][1]['pega'] = json.dumps({'encaixe': [list(r) for r in dados['encaixe']],
                                              'pose': maos_rig.pose_json(dados['pose'])})


def luvas_da_blend(ctx):
    """(mao, {lado: (luva, rig)}) das luvas guardadas na .blend da arma (o validar)."""
    return maos.Mao(ctx['luvas']['ficha']), {lado: (bpy.data.objects[f'luva_{lado}'], bpy.data.objects[f'rig_{lado}'])
                                             for lado, _n in LADOS}


def objetos_da_saida(mao, bracos, pega, marca, colecao):
    """Os objetos da pega no .glb da arma (ver o cabeçalho), em metros no referencial do Blender: o vazio `pega` (os
    extras: a marca e as sondas), os vazios `pega_mao_d`/`pega_mao_e` e a armadura `pega_luvas` com a ação
    `empunhadura`. Devolve [pega, pega_mao_d, pega_mao_e, pega_luvas]."""
    raiz = bpy.data.objects.new('pega', None)
    colecao.objects.link(raiz)
    sondas = {lado: {k: {'vertice': v[0], 'mm': v[1]} for k, v in pega[lado]['contatos'].items()} for lado in pega}
    raiz['luvas'] = json.dumps({'marca': marca, 'sondas': sondas}, separators=(',', ':'))
    objetos = [raiz]
    for lado, _nome in LADOS:
        rig = bracos[lado][1]
        m = pega[lado]['encaixe'] @ mm(rig.data.bones[f'mao_{lado}'].matrix_local)
        m.translation = m.translation * S
        ob = bpy.data.objects.new(f'pega_mao_{lado}', None)
        colecao.objects.link(ob)
        ob.matrix_world = m
        objetos.append(ob)
    armaduras = [maos_rig.armadura(mao, colecao, lado) for lado, _n in LADOS]
    bpy.ops.object.select_all(action='DESELECT')
    with bpy.context.temp_override(active_object=armaduras[0], selected_editable_objects=armaduras,
                                   selected_objects=armaduras):
        bpy.ops.object.join()
    arm = armaduras[0]
    arm.name = arm.data.name = 'pega_luvas'
    acao = bpy.data.actions.new('empunhadura')
    arm.animation_data_create()
    arm.animation_data.action = acao
    for lado, _nome in LADOS:
        for osso in OSSOS_DE_DEDO:
            pb = arm.pose.bones[f'{osso}_{lado}']
            pb.rotation_mode = 'QUATERNION'
            pb.rotation_quaternion = pega[lado]['pose'].get(osso, Quaternion())
            pb.keyframe_insert('rotation_quaternion', frame=1)
    objetos.append(arm)
    return objetos
```

```js file=tools/blender/saidaLuvas.mjs
// Leitor e validador da saída das luvas (Fase 4.1b; desenho em docs/superpowers/specs/2026-09-26-4.1b-luvas-e-
// empunhadura-design.md, seção 7; plano, Tarefa 6). O irmão do saida.mjs das armas, com os mesmos leitores do .glb e
// do .webp. O luvas.glb tem a raiz `luvas` (a marca do rig de cada braço nos extras, D4), as duas armaduras (`rig_d`,
// `rig_e`) e as duas malhas com skin (`luva_d`, `luva_e`), uma primitiva por zona, com o atributo `_VERTICE` (o índice
// do vértice no Blender: as costuras de UV duplicam vértices e o Draco reordena, e o modelo das dobras e as amarras das
// peças são indexados por ele) e as correções das dobras nos extras (o JSON de maos_correcoes.Modelo.parametros).
// `validarSaidaLuvas` confere tudo contra o registro (src/data/luvas.js): os 20 ossos de cada lado, as zonas, os
// atributos, os triângulos dos dois braços, as texturas, o total dos arquivos, o relatório aprovado, os triângulos e a
// marca do relatório iguais aos do .glb.

import { readFileSync, statSync, existsSync } from 'node:fs';
import { join } from 'node:path';
import { LUVAS, ZONAS_DAS_LUVAS, ossosDoLado } from '../../src/data/luvas.js';
import { ladoWebp, lerGlb } from './saida.mjs';

export const ARQUIVOS_DAS_LUVAS = Object.freeze({
  glb: 'luvas.glb', n: 'luvas_n.webp', m: 'luvas_m.webp', relatorio: 'luvas.relatorio.json',
});
const ATRIBUTOS = Object.freeze({ TEXCOORD_0: 'UV', TANGENT: 'tangentes', WEIGHTS_0: 'os pesos', _VERTICE: 'o _VERTICE' });

/**
 * Resumo do glTF das luvas: a raiz, a marca, o Draco e, por malha (`luva_d`, `luva_e`), os triângulos, as zonas, os
 * nomes dos ossos do skin, se todas as primitivas têm UV, tangentes, pesos e o `_VERTICE`, e as correções dos extras.
 */
export function resumoLuvasGlb(json) {
  const cena = json.scenes?.[json.scene ?? 0];
  const raizes = (cena?.nodes ?? []).map((i) => json.nodes[i]);
  if (raizes.length !== 1) throw new Error(`o .glb precisa de uma raiz só (tem ${raizes.length})`);
  const raiz = raizes[0];
  if (raiz.name !== 'luvas') throw new Error(`a raiz do .glb é ${raiz.name}, esperava luvas`);
  const materiais = json.materials ?? [];
  const malhas = {};
  const pilha = [raiz];
  while (pilha.length) {
    const n = pilha.pop();
    pilha.push(...(n.children ?? []).map((i) => json.nodes[i]));
    if (n.mesh === undefined) continue;
    const m = { triangulos: 0, zonas: [], ossos: [], uv: true, tangentes: true, pesos: true, vertice: true, correcoes: null };
    for (const p of json.meshes[n.mesh].primitives) {
      if ((p.mode ?? 4) !== 4) throw new Error(`${n.name}: primitiva que não é de triângulos (mode ${p.mode})`);
      const conta = p.indices !== undefined ? json.accessors[p.indices].count : json.accessors[p.attributes.POSITION].count;
      m.triangulos += conta / 3;
      const zona = materiais[p.material]?.name ?? null;
      if (zona && !m.zonas.includes(zona)) m.zonas.push(zona);
      // pela chave: o acessor 0 é um índice válido
      const tem = (nome) => p.attributes[nome] !== undefined;
      if (!tem('TEXCOORD_0')) m.uv = false;
      if (!tem('TANGENT')) m.tangentes = false;
      if (!tem('JOINTS_0') || !tem('WEIGHTS_0')) m.pesos = false;
      if (!tem('_VERTICE')) m.vertice = false;
    }
    if (n.skin !== undefined) m.ossos = json.skins[n.skin].joints.map((i) => json.nodes[i].name);
    if (typeof n.extras?.correcoes === 'string') {
      const c = JSON.parse(n.extras.correcoes);
      m.correcoes = { juntas: c.juntas?.length ?? 0, pecas: Boolean(c.pecas) };
    }
    malhas[n.name] = m;
  }
  const ordenadas = {};
  for (const nome of Object.keys(malhas).sort()) ordenadas[nome] = malhas[nome];
  return {
    raiz: raiz.name,
    malhas: ordenadas,
    marca: raiz.extras?.marca ?? null,
    draco: (json.extensionsUsed ?? []).includes('KHR_draco_mesh_compression'),
  };
}

/**
 * Confere a saída das luvas na raiz do projeto.
 * @returns {{problemas:string[], resumo:object|null, relatorio:object|null, bytes:number}}
 */
export function validarSaidaLuvas(raiz) {
  const problemas = [];
  const orc = LUVAS.orcamento;
  const pasta = join(raiz, LUVAS.pasta);
  const faltando = Object.values(ARQUIVOS_DAS_LUVAS).filter((f) => !existsSync(join(pasta, f)));
  if (faltando.length) {
    return { problemas: [`faltam em ${LUVAS.pasta}: ${faltando.join(', ')}`], resumo: null, relatorio: null, bytes: 0 };
  }
  let bytes = 0;
  for (const f of Object.values(ARQUIVOS_DAS_LUVAS)) bytes += statSync(join(pasta, f)).size;
  if (bytes > orc.arquivosMB * 1024 * 1024) {
    problemas.push(`arquivos: ${(bytes / 1048576).toFixed(2)} MB (orçamento ${orc.arquivosMB} MB)`);
  }

  const resumo = resumoLuvasGlb(lerGlb(readFileSync(join(pasta, ARQUIVOS_DAS_LUVAS.glb))).json);
  let total = 0;
  for (const lado of ['d', 'e']) {
    const nome = `luva_${lado}`;
    const m = resumo.malhas[nome];
    if (!m) {
      problemas.push(`falta a malha ${nome}`);
      continue;
    }
    total += m.triangulos;
    const ossos = ossosDoLado(lado);
    for (const o of ossos) if (!m.ossos.includes(o)) problemas.push(`${nome}: falta o osso ${o}`);
    for (const o of m.ossos) if (!ossos.includes(o)) problemas.push(`${nome}: osso a mais ${o}`);
    for (const z of ZONAS_DAS_LUVAS) if (!m.zonas.includes(z)) problemas.push(`${nome}: falta a zona ${z}`);
    for (const z of m.zonas) if (!ZONAS_DAS_LUVAS.includes(z)) problemas.push(`${nome}: zona desconhecida ${z}`);
    const tem = { TEXCOORD_0: m.uv, TANGENT: m.tangentes, WEIGHTS_0: m.pesos, _VERTICE: m.vertice };
    for (const [atributo, descricao] of Object.entries(ATRIBUTOS)) {
      if (!tem[atributo]) problemas.push(`${nome}: primitiva sem ${descricao}`);
    }
    if (!m.correcoes || !m.correcoes.juntas || !m.correcoes.pecas) {
      problemas.push(`${nome}: sem as correções das dobras nos extras (as juntas e as amarras das peças)`);
    }
  }
  if (total > orc.triangulos) problemas.push(`${total} triângulos nos dois braços (orçamento ${orc.triangulos})`);
  if (!resumo.draco) problemas.push('o .glb sem a compressão Draco (KHR_draco_mesh_compression)');

  for (const arq of [ARQUIVOS_DAS_LUVAS.n, ARQUIVOS_DAS_LUVAS.m]) {
    const w = ladoWebp(readFileSync(join(pasta, arq)));
    if (w.largura !== orc.textura || w.altura !== orc.textura) {
      problemas.push(`${arq}: ${w.largura}×${w.altura} (esperava ${orc.textura}×${orc.textura})`);
    }
    if (!w.semPerdas) problemas.push(`${arq}: WebP com perdas (os canais empacotados precisam do sem perdas)`);
    if (arq === ARQUIVOS_DAS_LUVAS.m && !w.alfa) problemas.push(`${arq}: sem o canal alfa (variação de cor)`);
  }

  const relatorio = JSON.parse(readFileSync(join(pasta, ARQUIVOS_DAS_LUVAS.relatorio), 'utf8'));
  if (!relatorio.aprovado) problemas.push(`o Blender reprovou: ${(relatorio.problemas ?? []).join('; ')}`);
  for (const lado of ['d', 'e']) {
    const m = resumo.malhas[`luva_${lado}`];
    const t = relatorio.triangulos?.luva;
    if (m && t !== m.triangulos) problemas.push(`luva_${lado}: o relatório diz ${t} triângulos e o .glb tem ${m.triangulos}`);
    if (!resumo.marca?.[lado]) {
      problemas.push(`o .glb sem a marca do rig ${lado} (extras da raiz)`);
    } else if (resumo.marca[lado] !== relatorio.marca?.[lado]) {
      problemas.push(`a marca do rig ${lado} do .glb (${resumo.marca[lado].slice(0, 12)}…) não é a do relatório `
        + `(${String(relatorio.marca?.[lado]).slice(0, 12)}…)`);
    }
  }
  return { problemas, resumo, relatorio, bytes };
}
```

```js file=tools/blender/saidaPega.mjs
// A pega das luvas na saída de uma arma realista (Fase 4.1b; desenho, seções 6.3 e 6.4; plano, Tarefa 7): a seção
// `empunhadura` do relatório do Blender (a penetração da luva na arma e a distância de cada contato da regra, nos dois
// braços; os lados dos dedos) e a marca do rig, igual no relatório, no .glb da arma e no luvas.glb (D4). O que o .glb
// precisa ter (os nós e o clipe) é conferido por `lerPega` (src/characters/hands/pega.js), que lança.
// Os lados (regra do usuário de 2026-09-27): na mão da frente (`frente` no relatório) só o polegar de um lado da arma e
// o indicador, o médio, o anelar e o mínimo do outro — `lados.polegarMM` e `lados.dedosMM` são a posição da polpa de
// cada um no eixo do lado do polegar (mm, a partir do plano do meio da arma); a do polegar tem de passar de +ladoMM e a
// de cada dedo de −ladoMM. A mão do gatilho, quando traz os lados (o polegar cruzando o punho), passa pela mesma conta.
// E o polegar da frente reto e deitado na arma (`polegar.curvaGraus` e `polegar.trechosMM`, a folga de cada trecho da
// falange proximal e da distal, da base para a ponta): a curva até polegarCurvaGraus, a distal encostando (o trecho
// mais perto dela até contatoMM) e nenhum trecho além de polegarFolgaMM.
// E os dedos que abraçam a arma lado a lado, sem leque (`juntosMM`: por par de vizinhos, a folga na falange média e na
// distal): a média até dedosJuntosMM, nas duas mãos; a mão da frente tem de trazer os três pares dos quatro dedos.
import { DEDOS_DA_FRENTE, LIMITES_DA_PEGA } from '../../src/data/luvas.js';

const fmt = (v) => v.toFixed(2).replace('.', ',');

/** Os problemas dos lados de um braço: o polegar do lado dele e cada dedo (os `exigidos`, se vierem) do outro. */
function problemasDosLados(lado, lados, exigidos) {
  const m = LIMITES_DA_PEGA.ladoMM;
  const problemas = [];
  if (!(lados.polegarMM >= m)) {
    problemas.push(`empunhadura ${lado}: o polegar a ${fmt(lados.polegarMM ?? NaN)} mm do meio da arma — tem de ficar do `
      + `lado dele, a pelo menos ${m} mm, e não do lado dos dedos`);
  }
  const dedos = lados.dedosMM ?? {};
  for (const d of exigidos ?? []) {
    if (!(d in dedos)) problemas.push(`empunhadura ${lado}: sem o lado do ${d} (a mão da frente conta os quatro dedos)`);
  }
  for (const [d, mm] of Object.entries(dedos)) {
    if (!(mm <= -m)) {
      problemas.push(`empunhadura ${lado}: o ${d} a ${fmt(mm)} mm do meio da arma, no lado do polegar ou no meio — tem de `
        + `passar para o outro lado, a pelo menos ${m} mm`);
    }
  }
  return problemas;
}

/** Os problemas do polegar da mão da frente: reto (a curva) e deitado na arma (a distal encostada, a proximal perto). */
const PARES_DA_FRENTE = DEDOS_DA_FRENTE.slice(1).map((d, i) => `${DEDOS_DA_FRENTE[i]}-${d}`);

/** Os problemas dos dedos lado a lado de um braço (os pares `exigidos` têm de vir). */
function problemasDosJuntos(lado, juntos, exigidos) {
  if (!juntos) {
    return exigidos ? [`empunhadura ${lado}: a mão da frente sem a conferência dos dedos lado a lado (construa a arma de novo)`] : [];
  }
  const problemas = [];
  for (const par of exigidos ?? []) {
    if (!juntos[par]) problemas.push(`empunhadura ${lado}: sem a folga entre os dedos ${par} (construa a arma de novo)`);
  }
  for (const [par, [media]] of Object.entries(juntos)) {
    if (!(media <= LIMITES_DA_PEGA.dedosJuntosMM)) {
      problemas.push(`empunhadura ${lado}: ${par} com a falange média a ${fmt(media ?? NaN)} mm uma da outra (máximo `
        + `${LIMITES_DA_PEGA.dedosJuntosMM} mm): os dedos em leque, não lado a lado`);
    }
  }
  return problemas;
}

function problemasDoPolegar(lado, polegar) {
  const L = LIMITES_DA_PEGA;
  const t = polegar?.trechosMM;
  if (!Array.isArray(t) || t.length < 2 || !Number.isFinite(polegar.curvaGraus)) {
    return [`empunhadura ${lado}: a mão da frente sem a conferência do polegar deitado (a curva e a folga ao longo dele; `
      + 'construa a arma de novo)'];
  }
  const problemas = [];
  if (!(polegar.curvaGraus <= L.polegarCurvaGraus)) {
    problemas.push(`empunhadura ${lado}: o polegar da frente com ${fmt(polegar.curvaGraus)}° de curva (a MCP mais a IP; `
      + `máximo ${L.polegarCurvaGraus}°): tem de ficar reto, deitado na arma`);
  }
  const meio = t.length / 2;
  const distal = Math.min(...t.slice(meio));
  if (!(distal <= L.contatoMM)) {
    problemas.push(`empunhadura ${lado}: a falange distal do polegar da frente não encosta na arma (o trecho mais perto a `
      + `${fmt(distal)} mm; máximo ${L.contatoMM} mm)`);
  }
  t.forEach((mm, i) => {
    if (!(mm <= L.polegarFolgaMM)) {
      const falange = i < meio ? 'proximal' : 'distal';
      problemas.push(`empunhadura ${lado}: a falange ${falange} do polegar da frente a ${fmt(mm)} mm da arma no trecho `
        + `${(i % meio) + 1} (máximo ${L.polegarFolgaMM} mm): tem de ficar deitada nela`);
    }
  });
  return problemas;
}

/**
 * Os problemas da pega: o relatório sem a seção, a penetração acima de 0,3 mm ou um contato acima de 1 mm num braço, a
 * mão da frente sem só o polegar de um lado e os quatro dedos do outro, os dedos em leque, a marca do .glb diferente da do relatório ou da
 * das luvas (`marcaLuvas`, a do luvas.glb; null se ainda não há luvas).
 * @returns {string[]}
 */
export function validarPega(relatorio, pega, marcaLuvas) {
  const e = relatorio?.empunhadura;
  if (!e) return ['o relatório sem a seção empunhadura (a pega das luvas; construa a arma de novo)'];
  const problemas = [];
  if (e.frente !== 'd' && e.frente !== 'e') {
    problemas.push('empunhadura: o relatório não diz qual é a mão da frente (construa a arma de novo)');
  } else if (!e[e.frente]?.lados) {
    problemas.push(`empunhadura ${e.frente}: a mão da frente sem a conferência dos lados (o polegar de um lado e os `
      + 'quatro dedos do outro; construa a arma de novo)');
  }
  for (const lado of ['d', 'e']) {
    const r = e[lado];
    if (!r) {
      problemas.push(`empunhadura: sem o braço ${lado}`);
      continue;
    }
    if (!(r.penetracaoMM <= LIMITES_DA_PEGA.penetracaoMM)) {
      problemas.push(`empunhadura ${lado}: a luva entra ${fmt(r.penetracaoMM)} mm na arma (máximo ${LIMITES_DA_PEGA.penetracaoMM} mm)`);
    }
    for (const [contato, mm] of Object.entries(r.contatosMM ?? {})) {
      if (!(mm <= LIMITES_DA_PEGA.contatoMM)) {
        problemas.push(`empunhadura ${lado}: o contato ${contato} a ${fmt(mm)} mm da arma (máximo ${LIMITES_DA_PEGA.contatoMM} mm)`);
      }
    }
    if (r.lados) problemas.push(...problemasDosLados(lado, r.lados, lado === e.frente ? DEDOS_DA_FRENTE : null));
    if (lado === e.frente) problemas.push(...problemasDoPolegar(lado, r.polegar));
    problemas.push(...problemasDosJuntos(lado, r.juntosMM, lado === e.frente ? PARES_DA_FRENTE : null));
    if (pega.marca[lado] !== e.marca?.[lado]) problemas.push(`empunhadura ${lado}: a marca do .glb não é a do relatório`);
    if (marcaLuvas && pega.marca[lado] !== marcaLuvas[lado]) {
      problemas.push(`empunhadura ${lado}: a marca do rig da pega (${pega.marca[lado].slice(0, 12)}…) não é a do luvas.glb `
        + `(${String(marcaLuvas[lado]).slice(0, 12)}…): construa de novo as luvas e a arma`);
    }
  }
  return problemas;
}
```

```js file=src/characters/hands/pega.js
// A pega das luvas numa arma realista (Fase 4.1b; desenho em docs/superpowers/specs/2026-09-26-4.1b-luvas-e-
// empunhadura-design.md, seção 6.4; plano, D1): o que o solver de empunhadura do Blender grava no .glb da arma e o jogo
// lê pelo bloco JSON do glTF (o `parser.json` do GLTFLoader, ou o JSON cru nos testes e no validador da saída).
//  - o nó `pega` (debaixo da raiz da arma), com `extras.luvas` = {marca: {d, e}, sondas: {lado: {contato: {vertice, mm}}}}
//    (a marca do rig de cada braço, D4 — o jogo só aplica a pega a luvas com a mesma marca — e o vértice de cada contato
//    da regra com a distância que o Blender mediu, que o `luvas_contato` refaz com o skinning do three); o exportador
//    grava os extras como texto JSON ou como objeto, e os dois servem;
//  - os nós `pega_mao_d` e `pega_mao_e`, filhos de `pega`: o referencial do osso `mao` de cada braço na pose, no da arma
//    (u); o braço põe o pulso ali;
//  - a animação `empunhadura`: um quadro com a rotação dos 17 ossos de dedo de cada mão (OSSOS_DE_DEDO) nos nós da
//    armadura `pega_luvas`, com os nomes do luvas.glb; o exportador com amostragem grava também a posição e a escala, e
//    o jogo usa só as rotações. Trilha em nó de nome que não é osso das luvas é erro (o esqueleto errado).
// No jogo, `pegaDoGltf` junta as três coisas para os braços (a marca, os dedos do clipe carregado e o referencial do osso
// `mao` de cada lado no da raiz da arma).
import * as THREE from 'three';
import { OSSOS_DE_DEDO, ossosDoLado } from '../../data/luvas.js';

const LADOS = ['d', 'e'];
const MARCA = /^[0-9a-f]{64}$/;

function extrasDasLuvas(no) {
  const bruto = no.extras?.luvas;
  if (bruto === undefined) throw new Error('pega: o nó pega sem os extras das luvas (marca e sondas)');
  let luvas;
  try {
    luvas = typeof bruto === 'string' ? JSON.parse(bruto) : bruto;
  } catch (e) {
    throw new Error(`pega: os extras das luvas não são JSON (${e.message})`);
  }
  for (const lado of LADOS) {
    if (!MARCA.test(luvas?.marca?.[lado] ?? '')) throw new Error(`pega: sem a marca do rig ${lado} nos extras`);
  }
  return luvas;
}

/**
 * Lê a pega do glTF de uma arma. Devolve {pega: índice do nó, maos: {d|e: {no, posicao, rotacao}}, trilhas: {osso_lado:
 * índice do nó}, marca: {d, e}, sondas: {d, e}}; lança com a explicação se falta alguma parte.
 */
export function lerPega(json) {
  const nos = json.nodes ?? [];
  const iPega = nos.findIndex((n) => n.name === 'pega');
  if (iPega < 0) throw new Error('pega: o .glb não tem o nó pega');
  const pega = nos[iPega];
  const luvas = extrasDasLuvas(pega);
  const filhos = pega.children ?? [];
  const maos = {};
  for (const lado of LADOS) {
    const i = filhos.find((k) => nos[k]?.name === `pega_mao_${lado}`);
    if (i === undefined) throw new Error(`pega: falta o nó pega_mao_${lado} dentro de pega`);
    maos[lado] = { no: i, posicao: nos[i].translation ?? [0, 0, 0], rotacao: nos[i].rotation ?? [0, 0, 0, 1] };
  }
  const clipe = (json.animations ?? []).find((a) => a.name === 'empunhadura');
  if (!clipe) throw new Error('pega: o .glb não tem a animação empunhadura');
  const ossos = new Set([...ossosDoLado('d'), ...ossosDoLado('e')]);
  const trilhas = {};
  for (const canal of clipe.channels ?? []) {
    const nome = nos[canal.target?.node]?.name;
    if (!ossos.has(nome)) throw new Error(`pega: trilha no nó desconhecido ${nome} (não é osso das luvas)`);
    if (canal.target.path === 'rotation') trilhas[nome] = canal.target.node;
  }
  for (const lado of LADOS) {
    for (const osso of OSSOS_DE_DEDO) {
      if (trilhas[`${osso}_${lado}`] === undefined) throw new Error(`pega: o clipe sem a rotação de ${osso}_${lado}`);
    }
  }
  for (const nome of Object.keys(trilhas)) {
    if (!OSSOS_DE_DEDO.includes(nome.slice(0, -2))) delete trilhas[nome];
  }
  return { pega: iPega, maos, trilhas, marca: luvas.marca, sondas: luvas.sondas ?? {} };
}

/**
 * Os quaternions dos 17 ossos de dedo de cada mão no clipe `empunhadura` carregado pelo GLTFLoader (um
 * THREE.AnimationClip com as trilhas `<osso>_<lado>.quaternion`): {d: {osso: [x, y, z, w]}, e: {...}}, o primeiro
 * quadro de cada trilha. As outras trilhas do clipe (posição e escala da amostragem, os ossos do braço) ficam de fora.
 */
export function dedosDoClipe(clip) {
  const dedos = { d: {}, e: {} };
  for (const t of clip?.tracks ?? []) {
    const m = /^(.+)_([de])\.quaternion$/.exec(t.name);
    if (!m || !OSSOS_DE_DEDO.includes(m[1])) continue;
    if (t.values.length < 4) throw new Error(`pega: a trilha ${t.name} sem quadro`);
    dedos[m[2]][m[1]] = Array.from(t.values.slice(0, 4));
  }
  for (const lado of LADOS) {
    for (const osso of OSSOS_DE_DEDO) if (!dedos[lado][osso]) throw new Error(`pega: o clipe sem a rotação de ${osso}_${lado}`);
  }
  return dedos;
}

// O exportador do glTF leva os objetos para o Y para cima conjugando (C·R·C⁻¹) e os ossos só pela esquerda (C·R: o osso
// fica com os eixos locais do Blender), com C = Rx(−90°): o osso `mao` na pose, que o Blender gravou no nó `pega_mao_*`,
// tem no jogo a rotação do nó vezes C.
const C = Object.freeze(new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(1, 0, 0), -Math.PI / 2));

/**
 * A pega de uma arma carregada pelo GLTFLoader, pronta para os braços de luva: `lerPega` confere as partes no JSON cru
 * (`gltf.parser.json`), `dedosDoClipe` tira os dedos do clipe carregado, e o referencial do osso `mao` de cada lado sai
 * do nó `pega_mao_*` no referencial da raiz da arma (u).
 * @param {{scene:THREE.Object3D, animations:THREE.AnimationClip[], parser:{json:object}}} gltf
 * @param {string} id o nome da raiz da arma no .glb
 * @returns {{marca:{d:string, e:string}, sondas:object, dedos:{d:object, e:object},
 *   maos:{d:{posicao:THREE.Vector3, quaternion:THREE.Quaternion}, e:{posicao:THREE.Vector3, quaternion:THREE.Quaternion}}}}
 */
export function pegaDoGltf(gltf, id) {
  const lida = lerPega(gltf.parser.json);
  const dedos = dedosDoClipe((gltf.animations ?? []).find((a) => a.name === 'empunhadura'));
  const raiz = gltf.scene.getObjectByName(id);
  if (!raiz) throw new Error(`pega: o .glb não tem a raiz ${id}`);
  gltf.scene.updateMatrixWorld(true);
  const inv = new THREE.Matrix4().copy(raiz.matrixWorld).invert();
  const maos = {};
  for (const lado of LADOS) {
    const no = gltf.scene.getObjectByName(`pega_mao_${lado}`);
    const posicao = new THREE.Vector3();
    const quaternion = new THREE.Quaternion();
    new THREE.Matrix4().multiplyMatrices(inv, no.matrixWorld).decompose(posicao, quaternion, new THREE.Vector3());
    maos[lado] = { posicao, quaternion: quaternion.multiply(C) };
  }
  return { marca: lida.marca, sondas: lida.sondas, dedos, maos };
}
```

```js file=src/characters/hands/modeloDobras.js
// O modelo das dobras das luvas no jogo (Fase 4.1b; desenho em docs/superpowers/specs/2026-09-26-4.1b-luvas-e-
// empunhadura-design.md, seção 4; plano, Tarefa 9): as mesmas contas de tools/blender/armas/maos_correcoes.py, na CPU,
// para a malha da luva sair no jogo como saiu na validação e no solver do Blender — o skin linear pelos ossos, a
// correção de cada junta (o raio de repouso por fora, o plano de contato da dobra por dentro, na ordem das juntas) e as
// peças de reforço presas à base corrigida. Ver o cabeçalho do módulo em Python para o porquê de cada passo; aqui só o
// que muda:
//  - o referencial é o do glTF (Y para cima) em mm; os vetores dos parâmetros (o `correcoes` dos extras, no referencial
//    do Blender) passam por deBlender;
//  - cada vértice é um vértice do Blender (o glTF duplica os das costuras de UV e o Draco reordena; o atributo
//    `_VERTICE` casa os dois — dadosDasPrimitivas);
//  - a pose entra como as deformações dos ossos (a matriz da pose vezes a inversa da de repouso, no referencial do braço;
//    no jogo, vindas do esqueleto do three), não como os quaternions locais: o giro de cada junta (o eixo e o ângulo) sai
//    de D_pai⁻¹·D_osso, sem depender do referencial local dos ossos, que o exportador do glTF converte.
// Puro (sem o three), para os testes do Node conferirem com a prova do relatório das luvas.

const RAD = Math.PI / 180;

/** Vetor do referencial do Blender (Z para cima) no do glTF (Y para cima). */
export const deBlender = (v) => [v[0], v[2], -v[1]];

const suave = (t) => {
  const c = t < 0 ? 0 : t > 1 ? 1 : t;
  return c * c * (3 - 2 * c);
};
const log1pexp = (z) => (z > 0 ? z + Math.log1p(Math.exp(-z)) : Math.log1p(Math.exp(z)));
const dot = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
const cross = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
const norm = (a) => Math.hypot(a[0], a[1], a[2]);
const unit = (a) => {
  const l = norm(a) || 1e-12;
  return [a[0] / l, a[1] / l, a[2] / l];
};
/** v girado em volta do eixo (unitário) pelo ângulo (radianos), pela regra da mão direita (Rodrigues). */
function girarEm(v, eixo, ang) {
  const c = Math.cos(ang);
  const s = Math.sin(ang);
  const k = cross(eixo, v);
  const d = dot(eixo, v) * (1 - c);
  return [v[0] * c + k[0] * s + eixo[0] * d, v[1] * c + k[1] * s + eixo[1] * d, v[2] * c + k[2] * s + eixo[2] * d];
}
/** R (3×3 por linhas) vezes v. */
const mulR = (R, o, v) => [
  R[o] * v[0] + R[o + 1] * v[1] + R[o + 2] * v[2],
  R[o + 3] * v[0] + R[o + 4] * v[1] + R[o + 5] * v[2],
  R[o + 6] * v[0] + R[o + 7] * v[1] + R[o + 8] * v[2],
];
/** Matriz de giro (3×3 por linhas) em volta do eixo unitário. */
function matrizDoGiro(eixo, ang) {
  const [x, y, z] = eixo;
  const c = Math.cos(ang);
  const s = Math.sin(ang);
  const t = 1 - c;
  return [t * x * x + c, t * x * y - s * z, t * x * z + s * y, t * x * y + s * z, t * y * y + c, t * y * z - s * x,
    t * x * z - s * y, t * y * z + s * x, t * z * z + c];
}

/** Gira v pela rotação mínima que leva `de` a `para` (unitários). */
function girarMinimo(v, de, para) {
  const k = cross(de, para);
  const s = norm(k);
  if (s <= 1e-9) return v;
  const c = dot(de, para);
  const e = [k[0] / s, k[1] / s, k[2] / s];
  const kv = dot(e, v);
  const ev = cross(e, v);
  return [v[0] * c + ev[0] * s + e[0] * kv * (1 - c), v[1] * c + ev[1] * s + e[1] * kv * (1 - c), v[2] * c + ev[2] * s + e[2] * kv * (1 - c)];
}

/** O eixo (unitário) e o ângulo (0–π) de uma rotação 3×3 (por linhas, no deslocamento `o`). */
function eixoAngulo(Q) {
  const tr = Q[0] + Q[4] + Q[8];
  const ang = Math.acos(Math.min(1, Math.max(-1, (tr - 1) / 2)));
  const v = [Q[7] - Q[5], Q[2] - Q[6], Q[3] - Q[1]];
  const s = norm(v);
  if (s > 1e-9) return { eixo: [v[0] / s, v[1] / s, v[2] / s], ang };
  // perto de 0 ou de π: pela diagonal (em 0 o eixo não importa, a junta fica em repouso)
  const d = [Math.sqrt(Math.max(0, (Q[0] + 1) / 2)), Math.sqrt(Math.max(0, (Q[4] + 1) / 2)), Math.sqrt(Math.max(0, (Q[8] + 1) / 2))];
  if (Q[1] < 0) d[1] = -d[1];
  if (Q[2] < 0) d[2] = -d[2];
  return { eixo: unit(d), ang };
}

/**
 * Os dados de um braço por vértice do Blender, das primitivas do glTF (uma por zona): as posições de repouso em mm, as
 * quatro influências de cada vértice, se é da base (as zonas fora do reforço) e os triângulos (todos e os da base),
 * pelos índices do Blender (`vertice`, o `_VERTICE` arredondado). O exportador grava a malha com skin no referencial da
 * cena, já na escala da raiz (u: `mmPorUnidade` = 25,4), e os ossos em metros dentro dela.
 * @param {{posicoes:ArrayLike<number>, juntas:ArrayLike<number>, pesos:ArrayLike<number>, vertice:ArrayLike<number>,
 *   indices:ArrayLike<number>, zona:string}[]} primitivas
 * @param {{zonaDasPecas?:string, mmPorUnidade?:number}} [o] a zona das peças presas (o reforço) e a escala da malha
 */
export function dadosDasPrimitivas(primitivas, { zonaDasPecas = 'reforco', mmPorUnidade = 25.4 } = {}) {
  let n = 0;
  for (const p of primitivas) for (let k = 0; k < p.vertice.length; k++) n = Math.max(n, Math.round(p.vertice[k]) + 1);
  const repouso = new Float64Array(n * 3);
  const juntas = new Uint16Array(n * 4);
  const pesos = new Float64Array(n * 4);
  const base = new Uint8Array(n);
  const visto = new Uint8Array(n);
  const tris = [];
  const trisBase = [];
  for (const p of primitivas) {
    const daBase = p.zona !== zonaDasPecas;
    const v = Array.from(p.vertice, (x) => Math.round(x));
    for (let k = 0; k < v.length; k++) {
      const i = v[k];
      if (!visto[i]) {
        visto[i] = 1;
        for (let c = 0; c < 3; c++) repouso[i * 3 + c] = p.posicoes[k * 3 + c] * mmPorUnidade;
        let soma = 0;
        for (let c = 0; c < 4; c++) soma += p.pesos[k * 4 + c];
        for (let c = 0; c < 4; c++) {
          juntas[i * 4 + c] = p.juntas[k * 4 + c];
          pesos[i * 4 + c] = p.pesos[k * 4 + c] / (soma || 1);
        }
      }
      if (daBase) base[i] = 1;
    }
    for (let k = 0; k < p.indices.length; k++) {
      tris.push(v[p.indices[k]]);
      if (daBase) trisBase.push(v[p.indices[k]]);
    }
  }
  if (visto.some((x) => !x)) throw new Error('modelo das dobras: há vértice do Blender sem vértice no glTF');
  return { n, repouso, juntas, pesos, base, triangulos: Uint32Array.from(tris), triangulosBase: Uint32Array.from(trisBase) };
}

/** Normais suaves (pela área) por vértice, dos triângulos. */
export function normaisDosVertices(pts, tris, n = pts.length / 3) {
  const vn = new Float64Array(n * 3);
  for (let t = 0; t < tris.length; t += 3) {
    const a = tris[t] * 3;
    const b = tris[t + 1] * 3;
    const c = tris[t + 2] * 3;
    const u = [pts[b] - pts[a], pts[b + 1] - pts[a + 1], pts[b + 2] - pts[a + 2]];
    const w = [pts[c] - pts[a], pts[c + 1] - pts[a + 1], pts[c + 2] - pts[a + 2]];
    const f = cross(u, w);
    for (const i of [a, b, c]) {
      vn[i] += f[0];
      vn[i + 1] += f[1];
      vn[i + 2] += f[2];
    }
  }
  for (let i = 0; i < vn.length; i += 3) {
    const l = Math.hypot(vn[i], vn[i + 1], vn[i + 2]) || 1e-12;
    vn[i] /= l;
    vn[i + 1] /= l;
    vn[i + 2] /= l;
  }
  return vn;
}

export class ModeloDobras {
  /**
   * @param {{malha:ReturnType<typeof dadosDasPrimitivas>, ossos:string[], pais:number[], cabecas:ArrayLike<number>,
   *   parametros:object, lado:string}} o `ossos` na ordem das juntas do skin (com o lado), `pais` o índice do pai de
   *   cada um (−1 na raiz), `cabecas` as cabeças de repouso (mm, glTF) e `parametros` o `correcoes` dos extras
   */
  constructor({ malha, ossos, pais, cabecas, parametros, lado }) {
    this.malha = malha;
    this.ossos = ossos;
    this.pais = pais;
    this.cabecas = Float64Array.from(cabecas);
    this.lado = lado;
    const pr = parametros;
    this.suave = pr.suaveMM;
    this.folga = pr.folgaMM;
    this.giroMinimo = pr.giroMinimo;
    const indice = new Map(ossos.map((o, i) => [o, i]));
    const { n, repouso: p, juntas: J, pesos: W, base } = malha;
    const somaDe = (nomes) => {
      const alvo = new Set(nomes.map((o) => indice.get(`${o}_${lado}`)));
      const s = new Float64Array(n);
      for (let v = 0; v < n; v++) for (let c = 0; c < 4; c++) if (alvo.has(J[v * 4 + c])) s[v] += W[v * 4 + c];
      return s;
    };
    this.juntas = pr.juntas.map((j) => {
      const osso = indice.get(`${j.osso}_${lado}`);
      if (osso === undefined) throw new Error(`modelo das dobras: sem o osso ${j.osso}_${lado}`);
      const c0 = deBlender(j.centro);
      const a0 = deBlender(j.eixo);
      const n0 = deBlender(j.normal);
      const reto0 = deBlender(j.reto);
      const y0 = girarEm(reto0, a0, j.repouso * RAD);
      const wAbaixo = somaDe(j.abaixo);
      const wOutro = j.outros.length ? somaDe(j.outros) : new Float64Array(n);
      const u0 = cross(a0, n0);
      const ativos = [];
      const mistos = [];
      const peso = new Float64Array(n);
      const ladoV = new Float64Array(n);
      const d0 = new Float64Array(n);
      const fora = new Float64Array(n);
      for (let v = 0; v < n; v++) {
        const rel = [p[v * 3] - c0[0], p[v * 3 + 1] - c0[1], p[v * 3 + 2] - c0[2]];
        const ax = dot(rel, a0);
        const raio = norm([rel[0] - ax * a0[0], rel[1] - ax * a0[1], rel[2] - ax * a0[2]]);
        const faixa = suave((j.meia + pr.luvaMM + pr.faixaMM - Math.abs(ax)) / pr.faixaMM);
        const perto = suave((j.alcance + pr.faixaMM - raio) / pr.faixaMM);
        peso[v] = faixa * perto * Math.min(1, Math.max(0, 1 - wOutro[v])) * (base[v] ? 1 : 0);
        ladoV[v] = wAbaixo[v] >= 0.5 ? 1 : -1;
        d0[v] = ladoV[v] * dot(rel, n0);
        fora[v] = suave((pr.foraMM - dot(rel, u0)) / (2 * pr.foraMM));
        if (peso[v] > 0) ativos.push(v);
        if (wAbaixo[v] > 0.002 && wAbaixo[v] < 0.998 && peso[v] * fora[v] > 0) mistos.push(v);
      }
      return { nome: j.junta, osso, pai: pais[osso], c0, a0, reto0, y0, peso, ladoV, d0, fora,
        ativos: Uint32Array.from(ativos), mistos: Uint32Array.from(mistos) };
    });
    const pc = pr.pecas;
    this.pecas = {
      vertices: Uint32Array.from(pc.vertices), base: Uint32Array.from(pc.base.flat()), bar: Float64Array.from(pc.bar.flat()),
      afastamento: pc.afastamento.map(deBlender), normal: pc.normal.map(deBlender),
    };
  }

  /**
   * As deformações dos ossos (Float64Array de 12 por osso: R 3×3 por linhas e t) a partir dos giros de cada osso em
   * volta da cabeça dele, no referencial do braço em repouso ({osso com o lado: [ex, ey, ez, ângulo]}, glTF), pela
   * cadeia: D = D_pai · giro. Os ossos sem giro seguem o pai.
   */
  deformacoesDosGiros(giros) {
    const nb = this.ossos.length;
    const D = new Float64Array(nb * 12);
    const feito = new Uint8Array(nb);
    const fazer = (i) => {
      if (feito[i]) return;
      const pai = this.pais[i];
      if (pai >= 0) fazer(pai);
      const g = giros[this.ossos[i]];
      const G = g ? matrizDoGiro(unit([g[0], g[1], g[2]]), g[3]) : [1, 0, 0, 0, 1, 0, 0, 0, 1];
      const c = [this.cabecas[i * 3], this.cabecas[i * 3 + 1], this.cabecas[i * 3 + 2]];
      const Gc = mulR(G, 0, c);
      const tg = [c[0] - Gc[0], c[1] - Gc[1], c[2] - Gc[2]]; // o giro em volta da cabeça: x → G·x + (c − G·c)
      const o = i * 12;
      if (pai < 0) {
        for (let k = 0; k < 9; k++) D[o + k] = G[k];
        D.set(tg, o + 9);
      } else {
        const op = pai * 12;
        for (let r = 0; r < 3; r++) {
          for (let col = 0; col < 3; col++) {
            D[o + r * 3 + col] = D[op + r * 3] * G[col] + D[op + r * 3 + 1] * G[3 + col] + D[op + r * 3 + 2] * G[6 + col];
          }
        }
        const t = mulR(D, op, tg);
        D[o + 9] = t[0] + D[op + 9];
        D[o + 10] = t[1] + D[op + 10];
        D[o + 11] = t[2] + D[op + 11];
      }
      feito[i] = 1;
    };
    for (let i = 0; i < nb; i++) fazer(i);
    return D;
  }

  /** As posições (mm, glTF, Float64Array de 3 por vértice do Blender) com as deformações D (ver deformacoesDosGiros). */
  avaliar(D) {
    const { n, repouso: p, juntas: J, pesos: W } = this.malha;
    const alvo = new Float64Array(n * 3);
    for (let v = 0; v < n; v++) {
      const x = p[v * 3];
      const y = p[v * 3 + 1];
      const z = p[v * 3 + 2];
      for (let c = 0; c < 4; c++) {
        const w = W[v * 4 + c];
        if (w === 0) continue;
        const o = J[v * 4 + c] * 12;
        alvo[v * 3] += w * (D[o] * x + D[o + 1] * y + D[o + 2] * z + D[o + 9]);
        alvo[v * 3 + 1] += w * (D[o + 3] * x + D[o + 4] * y + D[o + 5] * z + D[o + 10]);
        alvo[v * 3 + 2] += w * (D[o + 6] * x + D[o + 7] * y + D[o + 8] * z + D[o + 11]);
      }
    }
    for (const j of this.juntas) this.#aplicar(j, D, alvo);
    this.#seguirBase(alvo);
    return alvo;
  }

  #aplicar(j, D, alvo) {
    const o = j.osso * 12;
    const op = j.pai >= 0 ? j.pai * 12 : -1;
    // o giro da junta: D_pai⁻¹·D_osso (a parte de rotação), no referencial do braço em repouso
    const Q = new Array(9);
    for (let r = 0; r < 3; r++) {
      for (let c = 0; c < 3; c++) {
        Q[r * 3 + c] = op < 0 ? D[o + r * 3 + c]
          : D[op + r] * D[o + c] + D[op + 3 + r] * D[o + 3 + c] + D[op + 6 + r] * D[o + 6 + c];
      }
    }
    const { eixo: e0, ang } = eixoAngulo(Q);
    if (ang < this.giroMinimo) return;
    const P = (v) => (op < 0 ? v : mulR(D, op, v));
    const c = mulR(D, o, j.c0);
    c[0] += D[o + 9];
    c[1] += D[o + 10];
    c[2] += D[o + 11];
    const a = P(j.a0);
    const e = P(e0);
    // por fora: o raio de repouso em volta do eixo do giro inteiro
    const p = this.malha.repouso;
    for (const v of j.mistos) {
      const r0v = [p[v * 3] - j.c0[0], p[v * 3 + 1] - j.c0[1], p[v * 3 + 2] - j.c0[2]];
      const ax0 = dot(r0v, e0);
      const r0 = norm([r0v[0] - ax0 * e0[0], r0v[1] - ax0 * e0[1], r0v[2] - ax0 * e0[2]]);
      const rel = [alvo[v * 3] - c[0], alvo[v * 3 + 1] - c[1], alvo[v * 3 + 2] - c[2]];
      const ax = dot(rel, e);
      const perp = [rel[0] - ax * e[0], rel[1] - ax * e[1], rel[2] - ax * e[2]];
      const rp = norm(perp);
      if (!(rp > 1 && r0 > 1)) continue;
      const k = r0 / Math.max(rp, 1e-9);
      const w = j.peso[v] * j.fora[v];
      for (let q = 0; q < 3; q++) {
        const novo = c[q] + ax * e[q] + perp[q] * k;
        alvo[v * 3 + q] += (novo - alvo[v * 3 + q]) * w;
      }
    }
    // por dentro: o plano de contato entre a direção reta de cima e a do osso da junta
    const y = unit(mulR(D, o, j.y0));
    const rt = P(j.reto0);
    let nn = [y[0] + rt[0], y[1] + rt[1], y[2] + rt[2]];
    const na = dot(nn, a);
    nn = unit([nn[0] - a[0] * na, nn[1] - a[1] * na, nn[2] - a[2] * na]);
    const s = this.suave;
    const g = (x) => s * log1pexp(-x / s);
    for (const v of j.ativos) {
      const lv = j.ladoV[v];
      const d = lv * ((alvo[v * 3] - c[0]) * nn[0] + (alvo[v * 3 + 1] - c[1]) * nn[1] + (alvo[v * 3 + 2] - c[2]) * nn[2]);
      const empurra = Math.max(g(d - this.folga) - g(j.d0[v] - this.folga), 0);
      if (empurra === 0) continue;
      const m = lv * empurra * j.peso[v];
      alvo[v * 3] += m * nn[0];
      alvo[v * 3 + 1] += m * nn[1];
      alvo[v * 3 + 2] += m * nn[2];
    }
  }

  #seguirBase(alvo) {
    const { vertices, base, bar, afastamento, normal } = this.pecas;
    const vn = normaisDosVertices(alvo, this.malha.triangulosBase, this.malha.n);
    for (let k = 0; k < vertices.length; k++) {
      const ponto = [0, 0, 0];
      const ns = [0, 0, 0];
      for (let c = 0; c < 3; c++) {
        const i = base[k * 3 + c] * 3;
        const b = bar[k * 3 + c];
        for (let q = 0; q < 3; q++) {
          ponto[q] += b * alvo[i + q];
          ns[q] += b * vn[i + q];
        }
      }
      const off = girarMinimo(afastamento[k], normal[k], unit(ns));
      const v = vertices[k] * 3;
      alvo[v] = ponto[0] + off[0];
      alvo[v + 1] = ponto[1] + off[1];
      alvo[v + 2] = ponto[2] + off[2];
    }
  }
}

```

Em `tools/blender/armas/assar.py`, trocar:

```
# (canal_aspereza, canal_borda, canal_cor). Empacota `_n` (RGB) e `_m` (R sombra, G aspereza, B borda, A cor) e grava em
# WebP sem perdas (qualidade 100 no Blender = VP8L).
import math
```

por:

```
# (canal_aspereza, canal_borda, canal_cor). Empacota `_n` (RGB) e `_m` (R sombra, G aspereza, B borda, A cor) e grava em
# WebP sem perdas (qualidade 100 no Blender = VP8L). As luvas (Fase 4.1b) desdobram pelas costuras (`uv_por_costuras`)
# e conferem a densidade por ilha de UV (`densidade_por_ilha`: são uma malha só, base e peças juntas).
import math
```

Em `tools/blender/armas/assar.py`, trocar:

```

def _triangulo_na_grade(uv, tri, grade):
```

por:

```

def uv_por_costuras(objetos, lado_px, margem_px=8):
    """Desdobramento pelas costuras marcadas (Fase 4.1b: as ilhas seguem os painéis costurados da luva, e cada peça de
    reforço é as suas), pelo método de ângulos (ABF, conforme: sem cisalhar a trama do tecido e o grão do couro) e o
    empacotamento de sempre, com a margem exata."""
    for ob in objetos:
        if not ob.data.uv_layers:
            ob.data.uv_layers.new(name='UVMap')
    selecionar(objetos)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.unwrap(method='ANGLE_BASED', fill_holes=True, correct_aspect=True, margin_method='FRACTION',
                      margin=margem_px / lado_px)
    bpy.ops.object.mode_set(mode='OBJECT')
    _empacotar(objetos, lado_px, margem_px)


def densidade_por_ilha(ob, lado_px):
    """A densidade de texel (pixels por mm) de cada ilha de UV de uma malha — as faces ligadas por arestas que não são
    costura e em que as UV dos dois lados batem —, relativa à mediana das ilhas; e a das faces (percentis 1 e 99), que
    mostra a distorção de área dentro das ilhas."""
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    uv = bm.loops.layers.uv.active
    bm.faces.ensure_lookup_table()
    pai = list(range(len(bm.faces)))

    def raiz(i):
        while pai[i] != i:
            pai[i] = pai[pai[i]]
            i = pai[i]
        return i

    for e in bm.edges:
        if e.seam or len(e.link_faces) != 2:
            continue
        la, lb = e.link_loops
        # a UV de cada ponta da aresta nos dois lados (pelo vértice, qualquer que seja o sentido das faces)
        ua = {la.vert: la[uv].uv, la.link_loop_next.vert: la.link_loop_next[uv].uv}
        ub = {lb.vert: lb[uv].uv, lb.link_loop_next.vert: lb.link_loop_next[uv].uv}
        if all((ua[v] - ub[v]).length < 1e-6 for v in e.verts):
            pai[raiz(la.face.index)] = raiz(lb.face.index)
    area_mm, area_uv = {}, {}
    faces = []
    for f in bm.faces:
        pts = [l[uv].uv for l in f.loops]
        auv = abs(sum(pts[i].x * pts[i - 1].y - pts[i - 1].x * pts[i].y for i in range(len(pts)))) / 2
        amm = f.calc_area() / (S * S)
        r = raiz(f.index)
        area_mm[r] = area_mm.get(r, 0.0) + amm
        area_uv[r] = area_uv.get(r, 0.0) + auv
        if amm > 1e-9:
            faces.append(math.sqrt(auv * lado_px * lado_px / amm))
    bm.free()
    ilhas = {r: math.sqrt(area_uv[r] * lado_px * lado_px / area_mm[r]) for r in area_mm if area_mm[r] > 1e-9}
    med = float(np.median(list(ilhas.values())))
    rel = [v / med for v in ilhas.values()]
    f1, f99 = np.percentile(np.array(faces) / med, [1, 99])
    return {'ilhas': len(ilhas), 'medianaPxPorMm': round(med, 3), 'minimo': round(min(rel), 3),
            'maximo': round(max(rel), 3), 'faces1': round(float(f1), 3), 'faces99': round(float(f99), 3)}


def _triangulo_na_grade(uv, tri, grade):
```

Em `tools/blender/armas/assar.py`, trocar:

```

def _pixels(img, lado):
```

por:

```

def _desligar_finos(fontes):
    """Zera a força dos relevos `fino` dos materiais das fontes (materiais._relevo): os que a textura não guarda. Devolve
    como religar."""
    religar = []
    vistos = set()
    for ob in fontes:
        for slot in ob.material_slots:
            m = slot.material
            if m is None or m.name in vistos or not m.use_nodes:
                continue
            vistos.add(m.name)
            for no in m.node_tree.nodes:
                if no.type == 'BUMP' and no.label == 'fino':
                    religar.append((no, no.inputs['Strength'].default_value))
                    no.inputs['Strength'].default_value = 0.0
    return religar


def _pixels(img, lado):
```

Em `tools/blender/armas/assar.py`, trocar:

```

def assar_conjunto(fontes, pecas_jogo, lado_px, margem_px, pasta, nome_n, nome_m, amostras_ao=64, amostras_aa=16,
                   extrusao_mm=2.0):
    """Assa o conjunto de texturas de um nível: normal, sombra de contato e os três canais. Grava `_n` e `_m`. O relevo
    e os canais usam `amostras_aa` por pixel (antisserrilhado: o detalhe menor que o texel vira a média dele, não ruído);
    a sombra de contato, `amostras_ao`; a sombra e a aspereza passam pelo filtro binomial e os canais de dados são
    quantizados em degraus que não aparecem."""
    sc = bpy.context.scene
```

por:

```

def _cobertura(alvo, lado):
    """Os texels (linhas de baixo para cima, como os pixels do Blender) com o centro dentro de algum triângulo da UV."""
    cob = np.zeros((lado, lado), bool)
    me = alvo.data
    uv = me.uv_layers.active.data
    me.calc_loop_triangles()
    for tri in me.loop_triangles:
        r = _triangulo_na_grade(uv, tri, lado)
        if r is not None:
            y0, x0, dentro = r
            cob[y0:y0 + dentro.shape[0], x0:x0 + dentro.shape[1]] |= dentro
    return cob


def _estender(img, coberto, passos):
    """A margem das ilhas: cada texel fora delas, vizinho de um coberto, recebe a média dos vizinhos cobertos, `passos`
    vezes (o EXTEND do Blender, feito aqui para compor imagens assadas em grupos)."""
    img, cob = img.copy(), coberto.copy()
    for _ in range(passos):
        soma = np.zeros_like(img)
        conta = np.zeros(cob.shape, np.float32)
        cp = np.pad(cob, 1)
        ip = np.pad(img, ((1, 1), (1, 1), (0, 0)))
        for dy in (0, 1, 2):
            for dx in (0, 1, 2):
                if dy == 1 and dx == 1:
                    continue
                c = cp[dy:dy + cob.shape[0], dx:dx + cob.shape[1]]
                soma += ip[dy:dy + cob.shape[0], dx:dx + cob.shape[1]] * c[..., None]
                conta += c
        novo = ~cob & (conta > 0)
        img[novo] = soma[novo] / conta[novo][:, None]
        cob |= novo
    return img


def assar_conjunto(fontes, pecas_jogo, lado_px, margem_px, pasta, nome_n, nome_m, amostras_ao=64, amostras_aa=16,
                   extrusao_mm=2.0):
    """O conjunto de texturas de um nível de uma arma: um grupo só (as fontes para as peças de jogo, a gaiola de
    `extrusao_mm` e o raio do dobro). Ver assar_grupos."""
    return assar_grupos([(fontes, pecas_jogo, extrusao_mm, 2 * extrusao_mm)], lado_px, margem_px, pasta, nome_n, nome_m,
                        amostras_ao, amostras_aa)


def assar_grupos(grupos, lado_px, margem_px, pasta, nome_n, nome_m, amostras_ao=64, amostras_aa=16):
    """Assa o conjunto de texturas: normal, sombra de contato e os três canais, e grava `_n` e `_m`. `grupos` =
    [(fontes, alvos, extrusão da gaiola em mm, raio em mm)]: cada grupo casa os alvos (malhas de jogo) só com as fontes
    dele (o modelo alto), na sua imagem, e as imagens são compostas pela cobertura de UV de cada grupo, com a margem
    estendida depois (a margem de um grupo assada pelo Blender invadiria as ilhas do outro). A sombra de contato vê
    todas as fontes (as peças fazem sombra na base). As luvas assam a base e as peças separadas: as bordas das peças
    altas são arredondadas 1,6 mm para dentro das de jogo, e com tudo junto o raio da borda da peça atravessava e
    pegava a base embaixo (manchas tortas nos cantos). O relevo e os canais usam `amostras_aa` por pixel
    (antisserrilhado: o detalhe menor que o texel vira a média dele, não ruído); a sombra de contato, `amostras_ao`; a
    sombra e a aspereza passam pelo filtro binomial e os canais de dados são quantizados em degraus que não aparecem.
    Os relevos `fino` das fontes (o grão, a trama, o pontilhado das luvas) ficam fora: com um período de poucos texels,
    viravam moiré e ruído no WebP; no jogo eles vêm do shader."""
    sc = bpy.context.scene
```

Em `tools/blender/armas/assar.py`, trocar:

```
    sc.render.bake.use_clear = False
    sc.render.bake.cage_extrusion = extrusao_mm * S
    sc.render.bake.max_ray_distance = extrusao_mm * 2 * S
    sc.render.bake.margin = margem_px
    sc.render.bake.margin_type = 'EXTEND'
    alvo = _juntar_copias(pecas_jogo, f'alvo_{nome_n}')
    fonte = _juntar_copias(fontes, f'fonte_{nome_n}')
    for vis in ('visible_diffuse', 'visible_glossy', 'visible_shadow', 'visible_transmission', 'visible_volume_scatter'):
        setattr(alvo, vis, False)
    # Só a cópia do modelo alto faz sombra de contato: as peças (as do alto também), os LODs e o estúdio saem do assar.
    fora = [o for o in bpy.context.scene.objects if o is not fonte and o is not alvo and not o.hide_render]
    for o in fora:
        o.hide_render = True
    imgs = {}

    def assar(tipo, chave, fundo, amostras=1, canal=None):
        img = _imagem(f'{nome_n}_{chave}', lado_px, fundo=fundo)
        nos = _ligar_imagem(alvo, img)
        desfazer = _emitir_canal(fontes, canal) if canal else []
        sc.cycles.samples = amostras
        selecionar([fonte, alvo], ativo=alvo)
        if tipo == 'NORMAL':
```

por:

```
    sc.render.bake.use_clear = False
    sc.render.bake.margin = 2  # só para não sobrar texel de borda sem valor; a margem de verdade é a composta
    sc.render.bake.margin_type = 'EXTEND'
    pares = []
    for k, (fontes, alvos, extrusao_mm, raio_mm) in enumerate(grupos):
        alvo = _juntar_copias(alvos, f'alvo_{nome_n}_{k}')
        fonte = _juntar_copias(fontes, f'fonte_{nome_n}_{k}')
        for vis in ('visible_diffuse', 'visible_glossy', 'visible_shadow', 'visible_transmission',
                    'visible_volume_scatter'):
            setattr(alvo, vis, False)
        pares.append((fonte, alvo, extrusao_mm, raio_mm, _cobertura(alvo, lado_px)))
    todas_as_fontes = [f for g in grupos for f in g[0]]
    # Só as cópias do modelo alto fazem sombra de contato: os originais, os LODs e o estúdio saem do assar.
    nossos = {o for par in pares for o in par[:2]}
    fora = [o for o in sc.objects if o not in nossos and not o.hide_render]
    for o in fora:
        o.hide_render = True
    religar = _desligar_finos([par[0] for par in pares])
    coberto = np.zeros((lado_px, lado_px), bool)
    for par in pares:
        coberto |= par[4]
    arrays = {}

    def assar(tipo, chave, fundo, amostras=1, canal=None):
        desfazer = _emitir_canal(todas_as_fontes, canal) if canal else []
        sc.cycles.samples = amostras
        if tipo == 'NORMAL':
```

Em `tools/blender/armas/assar.py`, trocar:

```
            sc.render.bake.normal_r, sc.render.bake.normal_g, sc.render.bake.normal_b = 'POS_X', 'POS_Y', 'POS_Z'
        bpy.ops.object.bake(type=tipo)
        _desfazer(desfazer)
        for nt, n in nos:
            nt.nodes.remove(n)
        imgs[chave] = img

```

por:

```
            sc.render.bake.normal_r, sc.render.bake.normal_g, sc.render.bake.normal_b = 'POS_X', 'POS_Y', 'POS_Z'
        final = np.empty((lado_px, lado_px, 4), np.float32)
        final[...] = fundo
        for k, (fonte, alvo, extrusao_mm, raio_mm, cob) in enumerate(pares):
            img = _imagem(f'{nome_n}_{chave}_{k}', lado_px, fundo=fundo)
            nos = _ligar_imagem(alvo, img)
            sc.render.bake.cage_extrusion = extrusao_mm * S
            sc.render.bake.max_ray_distance = raio_mm * S
            selecionar([fonte, alvo], ativo=alvo)
            bpy.ops.object.bake(type=tipo)
            for nt, n in nos:
                nt.nodes.remove(n)
            final[cob] = _pixels(img, lado_px)[cob]
            bpy.data.images.remove(img)
        _desfazer(desfazer)
        arrays[chave] = _estender(final, coberto, margem_px)

```

Em `tools/blender/armas/assar.py`, trocar:

```
        assar('EMIT', chave, (neutro, neutro, neutro, 1.0), amostras_aa, canal)
    n = _pixels(imgs['normal'], lado_px)[..., :3]
    ao = _suavizar(_pixels(imgs['ao'], lado_px)[..., 0])
    aspereza = _suavizar(_pixels(imgs['aspereza'], lado_px)[..., 0])
    m = np.stack([ao, aspereza] + [_pixels(imgs[k], lado_px)[..., 0] for k in ('borda', 'cor')], axis=2)
    # Os canais de dados só modulam o material (no oxidado, ±16 % de aspereza e ±6 % de cor): degraus de 4/255 na
```

por:

```
        assar('EMIT', chave, (neutro, neutro, neutro, 1.0), amostras_aa, canal)
    n = arrays['normal'][..., :3]
    ao = _suavizar(arrays['ao'][..., 0])
    aspereza = _suavizar(arrays['aspereza'][..., 0])
    m = np.stack([ao, aspereza] + [arrays[k][..., 0] for k in ('borda', 'cor')], axis=2)
    # Os canais de dados só modulam o material (no oxidado, ±16 % de aspereza e ±6 % de cor): degraus de 4/255 na
```

Em `tools/blender/armas/assar.py`, trocar:

```
    }
    bpy.data.objects.remove(alvo)
    bpy.data.objects.remove(fonte)
    for o in fora:
        o.hide_render = False
    for img in imgs.values():
        bpy.data.images.remove(img)
    return caminhos
```

por:

```
    }
    for no, forca in religar:
        no.inputs['Strength'].default_value = forca
    for fonte, alvo, *_ in pares:
        bpy.data.objects.remove(alvo)
        bpy.data.objects.remove(fonte)
    for o in fora:
        o.hide_render = False
    return caminhos
```

Em `tools/blender/armas/exportar.py`, trocar:

```
# 1,22 para 0,29 MB; posição em 14 bits, normal em 10, UV e tangente em 12). As texturas já foram gravadas pelo assar;
# o relatório vai ao lado.
import json
```

por:

```
# 1,22 para 0,29 MB; posição em 14 bits, normal em 10, UV e tangente em 12). As texturas já foram gravadas pelo assar;
# o relatório vai ao lado. As luvas (Fase 4.1b) têm a exportação delas, com skin (`exportar_luvas`).
import json
```

Em `tools/blender/armas/exportar.py`, trocar:

```

from .unidades import S, U_POR_M
```

por:

```

from . import maos_rig
from .unidades import S, U_POR_M
```

Em `tools/blender/armas/exportar.py`, trocar:

```

def exportar(ctx, origem_mm, lods, soquetes_objs, pasta):
    """Monta a hierarquia na escala do jogo e grava `<id>.glb`. Muda a cena: a .blend da conferência é gravada antes."""
    col = bpy.data.collections.new('exportar')
```

por:

```

def exportar(ctx, origem_mm, lods, soquetes_objs, pasta, pega=None):
    """Monta a hierarquia na escala do jogo e grava `<id>.glb`. `pega` = os objetos da pega das luvas
    (empunhadura_pega.objetos_da_saida: o vazio `pega`, os `pega_mao_*` e a armadura com a ação `empunhadura`), que
    entram debaixo da raiz com a animação (D1). Muda a cena: a .blend da conferência é gravada antes."""
    col = bpy.data.collections.new('exportar')
```

Em `tools/blender/armas/exportar.py`, trocar:

```
        selecionados.append(s)
    bpy.ops.object.select_all(action='DESELECT')
```

por:

```
        selecionados.append(s)
    if pega:
        no_pega, *filhos = pega
        _mover(no_pega, col)
        no_pega.parent = raiz
        selecionados.append(no_pega)
        for ob in filhos:
            mundo = ob.matrix_world.copy()
            _mover(ob, col)
            ob.parent = no_pega
            if ob.type == 'ARMATURE':
                # a armadura em metros no referencial do Blender, levada à escala e à origem do jogo (o jogo só lê as
                # rotações dos ossos de dedo, que não mudam com isso)
                ob.matrix_world = Matrix.Scale(U_POR_M, 4) @ Matrix.Translation(-origem) @ mundo
            else:
                ob.matrix_world = Matrix.Translation((mundo.translation - origem) * U_POR_M) @ mundo.to_quaternion().to_matrix().to_4x4()
            selecionados.append(ob)
    bpy.ops.object.select_all(action='DESELECT')
```

Em `tools/blender/armas/exportar.py`, trocar:

```
        export_image_format='NONE', export_extras=True, export_cameras=False, export_lights=False,
        export_animations=False, export_skins=False, export_morph=False, export_draco_mesh_compression_enable=True,
        export_draco_mesh_compression_level=6, export_draco_position_quantization=14, export_draco_normal_quantization=10,
```

por:

```
        export_image_format='NONE', export_extras=True, export_cameras=False, export_lights=False,
        export_animations=bool(pega), export_animation_mode='ACTIONS', export_force_sampling=True,
        export_frame_range=False, export_skins=bool(pega), export_morph=False, export_draco_mesh_compression_enable=True,
        export_draco_mesh_compression_level=6, export_draco_position_quantization=14, export_draco_normal_quantization=10,
```

Em `tools/blender/armas/exportar.py`, trocar:

```

def gravar_relatorio(pasta, id_, relatorio):
```

por:

```

def exportar_luvas(pasta, bracos, marcas):
    """Grava `luvas.glb` (Fase 4.1b; plano, Tarefa 6, D3 e D4): a raiz `luvas` na escala do jogo (u por metro; dentro,
    a cena em metros) com a marca do rig de cada braço nos extras, e para cada braço (`bracos` = [(luva, rig)]) a
    armadura em repouso e a malha com skin — uma primitiva por zona, com o atributo `_VERTICE` (o índice do vértice no
    Blender: o jogo casa com ele o modelo das dobras e as amarras das peças, indexados pelos vértices do Blender, com os
    do glTF, que as costuras de UV duplicam e o Draco reordena) e as correções das dobras nos extras. O Draco com a
    quantização genérica em 16 bits: o `_VERTICE` sai em ponto flutuante, e em 12 bits o passo passava de 0,8 com uns
    3 400 vértices. Muda a cena: a .blend da conferência é gravada antes."""
    col = bpy.data.collections.new('exportar_luvas')
    bpy.context.scene.collection.children.link(col)
    raiz = _vazio('luvas', col)
    raiz.scale = (U_POR_M, U_POR_M, U_POR_M)
    raiz['marca'] = dict(marcas)
    selecionados = [raiz]
    for luva, rig in bracos:
        maos_rig.posar(rig, {})
        _mover(rig, col)
        rig.parent = raiz
        _mover(luva, col)
        luva.parent = rig
        me = luva.data
        vert = me.attributes.get('_VERTICE') or me.attributes.new('_VERTICE', 'FLOAT', 'POINT')
        vert.data.foreach_set('value', [float(i) for i in range(len(me.vertices))])
        selecionados += [rig, luva]
    bpy.ops.object.select_all(action='DESELECT')
    for o in selecionados:
        o.select_set(True)
    bpy.context.view_layer.objects.active = raiz
    caminho = os.path.join(pasta, 'luvas.glb')
    bpy.ops.export_scene.gltf(
        filepath=caminho, export_format='GLB', use_selection=True, export_yup=True, export_apply=False,
        export_texcoords=True, export_normals=True, export_tangents=True, export_materials='EXPORT',
        export_image_format='NONE', export_extras=True, export_attributes=True, export_cameras=False,
        export_lights=False, export_animations=False, export_skins=True, export_morph=False,
        export_draco_mesh_compression_enable=True, export_draco_mesh_compression_level=6,
        export_draco_position_quantization=14, export_draco_normal_quantization=10,
        export_draco_texcoord_quantization=12, export_draco_generic_quantization=16)
    return caminho


def gravar_relatorio(pasta, id_, relatorio):
```

Em `tools/blender/armas/conferir.py`, trocar:

```
# Renders da conferência das armas realistas (Fase 4.1a; desenho, seção 4.7): lado, cima, frente, 3/4 dos dois lados,
# perto do receptor e a vista aproximada da primeira pessoa (sem as luvas até a 4.1b; a câmera no olho do boneco com o
# FOV do viewmodel — 60 horizontais em 4:3 = 75,2° em 16:9 — e a arma na posição da categoria `rifle`), no modelo alto
# com os materiais de fábrica, em tools/blender/conferencia/<id>/ (fora do git). A sobreposição da silhueta com a foto
# (sobreposicao.png) sai do validar.py.
import os
```

por:

```
# Renders da conferência das armas realistas (Fase 4.1a; desenho, seção 4.7): lado, cima, frente, 3/4 dos dois lados,
# perto do receptor e a vista aproximada da primeira pessoa (a câmera no olho do boneco com o FOV do viewmodel — 60
# horizontais em 4:3 = 75,2° em 16:9 — e a arma na posição da categoria `rifle`), no modelo alto com os materiais de
# fábrica, em tools/blender/conferencia/<id>/ (fora do git). A sobreposição da silhueta com a foto (sobreposicao.png)
# sai do validar.py. Desde a 4.1b, as luvas na pega (a luva de jogo pelo modelo das luvas, na pose e no encaixe que o
# construir guardou nos rigs): as vistas de perto de cada mão pelos dois lados, por baixo e por trás, e a primeira
# pessoa com as luvas (seção 6.3 do desenho da 4.1b).
import json
import os
```

Em `tools/blender/armas/conferir.py`, trocar:

```
import bpy

from . import estudio
from .unidades import S
```

por:

```
import bpy
from mathutils import Matrix, Vector

from . import estudio, luvas, maos, maos_correcoes, maos_rig
from .unidades import S
```

Em `tools/blender/armas/conferir.py`, trocar:

```
    comp = (max(xs) - min(xs)) * S
    estudio.montar((cx, 0.0, cy))
    dispositivo = estudio.render(1600, 900, amostras)
```

por:

```
    comp = (max(xs) - min(xs)) * S
    fundo = estudio.montar((cx, 0.0, cy))
    dispositivo = estudio.render(1600, 900, amostras)
```

Em `tools/blender/armas/conferir.py`, trocar:

```
        arquivos.append(sc.render.filepath)
    for col in sc.collection.children:
```

por:

```
        arquivos.append(sc.render.filepath)
    arquivos += _maos(ctx, pasta, sc, fundo)
    for col in sc.collection.children:
```

Em `tools/blender/armas/conferir.py`, trocar:

```
    return arquivos, dispositivo

```

por:

```
    return arquivos, dispositivo


def _maos(ctx, pasta, sc, fundo):
    """As luvas na pega: as malhas posadas (sem rig, como no jogo) e as vistas de perto de cada mão (as de baixo sem o
    chão do estúdio, que fica entre a câmera e a mão)."""
    rigs = [bpy.data.objects.get(f'rig_{lado}') for lado in ('d', 'e')]
    if not all(r is not None and 'pega' in r for r in rigs):
        return []
    col = bpy.data.collections.new('maos_da_pega')
    sc.collection.children.link(col)
    mao = maos.Mao(ctx['luvas']['ficha'])
    for lado, rig in zip(('d', 'e'), rigs):
        dados = json.loads(rig['pega'])
        luva = bpy.data.objects[f'luva_{lado}']
        modelo = maos_correcoes.Modelo(luva, rig, mao, luvas.REFORCO)
        ob = modelo.para_malha(f'pega_{lado}', col, maos_rig.pose_de_json(dados['pose']))
        e = Matrix(dados['encaixe'])
        e.translation = e.translation * S
        ob.matrix_world = e
        ob.hide_render = False
    maos_rig.posar(rigs[0], {})
    maos_rig.posar(rigs[1], {})
    arquivos = []
    for lado, nome in (('d', 'direita'), ('e', 'esquerda')):
        c = bpy.data.objects[f'soquete_mao_{lado}'].matrix_world.translation.copy()
        # A de trás vem de trás, de fora (−Y é a direita da arma) e de cima, como o atirador vê a própria mão: bem atrás
        # e no eixo, a coronha tapava a mão direita e o receptor, metade da esquerda; a da direita sobe mais (na altura
        # do antebraço, a câmera olhava para dentro do punho da luva, que no Blender não tem o braço de massinha).
        atras = {'d': (-0.18, -0.12, 0.18), 'e': (-0.24, 0.13, 0.05)}[lado]
        for vista, desloc in (('dir', (0.0, -0.3, 0.02)), ('esq', (0.0, 0.3, 0.02)), ('baixo', (0.04, -0.06, -0.3)),
                              ('tras', atras)):
            fundo.hide_render = vista == 'baixo'
            sc.camera = estudio.camera(f'mao_{nome}_{vista}', c + Vector(desloc), c, 45)
            sc.render.filepath = os.path.join(pasta, f'mao_{nome}_{vista}.png')
            bpy.ops.render.render(write_still=True)
            arquivos.append(sc.render.filepath)
    fundo.hide_render = False
    olho = (-0.78, 0.114, 0.079)
    sc.camera = estudio.camera('primeira_pessoa_luvas', olho, (olho[0] + 1.0, olho[1] - 0.02, olho[2] - 0.03), 23.4)
    sc.render.filepath = os.path.join(pasta, 'primeira_pessoa_luvas.png')
    bpy.ops.render.render(write_still=True)
    arquivos.append(sc.render.filepath)
    return arquivos

```

Em `tools/blender/armas/principal.py`, trocar:

```
# conferência e exportar), validar (reabre a .blend e refaz a validação, sem exportar) e conferir (reabre a .blend e
# renderiza as vistas). O contexto (JSON) traz a ficha, a pintura de fábrica, as peças, as zonas, os soquetes, o
# orçamento, as pastas e o hash das entradas. As linhas `MASSACRE-*` da saída são lidas pelo lançador; reprovado sai com
# código 1 (o lançador mostra os problemas).
```

por:

```
# conferência e exportar), validar (reabre a .blend e refaz a validação, sem exportar) e conferir (reabre a .blend e
# renderiza as vistas). Desde a 4.1b o construir resolve também a pega das luvas (empunhadura_pega.py) e o validar a refaz. O contexto (JSON) traz a ficha, a pintura de fábrica, as peças, as zonas, os soquetes, o
# orçamento, as pastas e o hash das entradas. O alvo `luvas` (Fase 4.1b) tem as mesmas três ações em luvas.py. As linhas `MASSACRE-*` da saída são lidas pelo lançador; reprovado sai com
# código 1 (o lançador mostra os problemas).
```

Em `tools/blender/armas/principal.py`, trocar:

```

from armas import assar, conferir, exportar, lod, materiais, pecas, soquetes, validar, zonas  # noqa: E402

```

por:

```

from armas import (assar, conferir, empunhadura_pega, exportar, lod, luvas, materiais, pecas, soquetes,  # noqa: E402
                   validar, zonas)

```

Em `tools/blender/armas/principal.py`, trocar:

```
    _etapa(t0, 'peças móveis e soquetes')
    assar.uv_automatico(lista_perto, orc['textura'], 8)
```

por:

```
    _etapa(t0, 'peças móveis e soquetes')
    # A pega (Fase 4.1b): as luvas refeitas pelo mesmo script e o solver na arma de jogo (o perto, peças em repouso).
    mao, bracos = empunhadura_pega.montar_luvas(ctx, _colecao('luvas'))
    pega, rel_pega, problemas_pega = empunhadura_pega.resolver(ctx, mao, bracos, perto, soqs,
                                                               getattr(arma, 'EMPUNHADURA', None))
    empunhadura_pega.guardar(bracos, pega)
    _etapa(t0, f"empunhadura ({rel_pega['segundos']} s)")
    assar.uv_automatico(lista_perto, orc['textura'], 8)
```

Em `tools/blender/armas/principal.py`, trocar:

```
    rel, problemas = _validar(ctx, arma, lods, jogo)
    _etapa(t0, 'validar')
    rel.update({
        'arma': ctx['id'], 'versao': 1, 'blender': bpy.app.version_string, 'gerado': time.strftime('%Y-%m-%dT%H:%M:%S'),
```

por:

```
    rel, problemas = _validar(ctx, arma, lods, jogo)
    problemas += problemas_pega
    _etapa(t0, 'validar')
    rel.update({
        'empunhadura': rel_pega,
        'arma': ctx['id'], 'versao': 1, 'blender': bpy.app.version_string, 'gerado': time.strftime('%Y-%m-%dT%H:%M:%S'),
```

Em `tools/blender/armas/principal.py`, trocar:

```
        sys.exit(1)
    exportar.exportar(ctx, arma.ORIGEM_MM, lods, soqs, ctx['saida'])
    _etapa(t0, 'exportar')
```

por:

```
        sys.exit(1)
    objetos_pega = empunhadura_pega.objetos_da_saida(mao, bracos, pega, rel_pega['marca'], _colecao('pega'))
    exportar.exportar(ctx, arma.ORIGEM_MM, lods, soqs, ctx['saida'], objetos_pega)
    _etapa(t0, 'exportar')
```

Em `tools/blender/armas/principal.py`, trocar:

```
    rel, problemas = _validar(ctx, arma, lods, bpy.data.collections['jogo'])
    print('MASSACRE-VALIDACAO', json.dumps({'silhueta': rel['silhueta'], 'medidas': rel['medidas'], 'problemas': problemas},
                                           ensure_ascii=False))
    if problemas:
```

por:

```
    rel, problemas = _validar(ctx, arma, lods, bpy.data.collections['jogo'])
    mao, bracos = empunhadura_pega.luvas_da_blend(ctx)
    soqs = list(bpy.data.collections['soquetes'].objects)
    _pega, rel_pega, problemas_pega = empunhadura_pega.resolver(ctx, mao, bracos, lods['perto'], soqs,
                                                                getattr(arma, 'EMPUNHADURA', None))
    problemas += problemas_pega
    print('MASSACRE-VALIDACAO', json.dumps({'silhueta': rel['silhueta'], 'medidas': rel['medidas'],
                                            'empunhadura': rel_pega, 'problemas': problemas}, ensure_ascii=False))
    if problemas:
```

Em `tools/blender/armas/principal.py`, trocar:

```

def principal():
```

por:

```

def conferir_luvas(ctx):
    arquivos, dispositivo = luvas.conferir(ctx)
    print('MASSACRE-CONFERIR', json.dumps(arquivos, ensure_ascii=False))
    print('MASSACRE-DISPOSITIVO', dispositivo)


def principal():
```

Em `tools/blender/armas/principal.py`, trocar:

```
        ctx = json.load(f)
    {'construir': construir, 'validar': revalidar, 'conferir': acao_conferir}[acao](ctx)

```

por:

```
        ctx = json.load(f)
    if ctx['id'] == 'luvas':
        acoes = {'construir': luvas.construir, 'validar': luvas.validar, 'conferir': conferir_luvas}
    else:
        acoes = {'construir': construir, 'validar': revalidar, 'conferir': acao_conferir}
    acoes[acao](ctx)

```

Em `tools/blender.mjs`, trocar:

```
//
// Prepara o contexto que o Blender não sabe calcular sozinho — a paleta das massas, o acento da facção, a planta de
```

por:

```
//
// Luvas (Fase 4.1b; tools/blender/armas/luvas.py, a ficha em tools/blender/refs/luvas.json): o alvo `luvas` nas mesmas
// quatro ações (construir, validar, conferir, abrir); `todas` no construir e no validar começa pelas luvas.
//
// Prepara o contexto que o Blender não sabe calcular sozinho — a paleta das massas, o acento da facção, a planta de
```

Em `tools/blender.mjs`, trocar:

```
import { validarSaida } from './blender/saida.mjs';

```

por:

```
import { validarSaida } from './blender/saida.mjs';
import { validarSaidaLuvas } from './blender/saidaLuvas.mjs';
import { LUVAS } from '../src/data/luvas.js';

```

Em `tools/blender.mjs`, trocar:

```

/** Hash das entradas de uma arma realista: os .py do pacote, a ficha e o registro da arma (plano da 4.1a, D14). */
function hashEntradas(id, def, ficha) {
```

por:

```

/**
 * Hash das entradas de uma arma realista (os .py do pacote, a ficha e o registro da arma; plano da 4.1a, D14) ou das
 * luvas (os .py e a ficha delas, com `def` nulo).
 */
function hashEntradas(id, def, ficha) {
```

Em `tools/blender.mjs`, trocar:

```
  const ficha = validarFicha(JSON.parse(readFileSync(join(ROOT, 'tools', 'blender', 'refs', `${id}.json`), 'utf8')));
  const ctx = {
```

por:

```
  const ficha = validarFicha(JSON.parse(readFileSync(join(ROOT, 'tools', 'blender', 'refs', `${id}.json`), 'utf8')));
  // A pega (Fase 4.1b, D5): o solver refaz o rig das luvas dentro do construir da arma, então a ficha e as pinturas das
  // luvas entram no contexto e no hash — mudar as luvas refaz a pega de todas as armas.
  const { validarFichaLuvas } = await import('../src/characters/hands/fichaLuvas.js');
  const luvas = {
    ficha: validarFichaLuvas(JSON.parse(readFileSync(join(ROOT, 'tools', 'blender', 'refs', 'luvas.json'), 'utf8'))),
    pinturas: LUVAS.pinturas,
  };
  const ctx = {
```

Em `tools/blender.mjs`, trocar:

```
    orcamento: orcamentoDaArma(id), saida: join(ROOT, def.pasta), conferencia: join(ROOT, 'tools', 'blender', 'conferencia', id),
    hash: hashEntradas(id, def, ficha), forcar,
  };
```

por:

```
    orcamento: orcamentoDaArma(id), saida: join(ROOT, def.pasta), conferencia: join(ROOT, 'tools', 'blender', 'conferencia', id),
    categoria: def.categoria, luvas, hash: hashEntradas(id, def, { ficha, luvas }), forcar,
  };
```

Em `tools/blender.mjs`, trocar:

```
  const t = Object.entries(relatorio.lods).map(([l, d]) => `${l} ${d.triangulos.toLocaleString('pt-BR')}`).join(' · ');
  return `silhueta ${(s.iouTolerancia * 100).toFixed(1)} % (bruto ${(s.iouBruto * 100).toFixed(1)} %) · ${t} triângulos · ${(bytes / 1048576).toFixed(2)} MB`;
}
```

por:

```
  const t = Object.entries(relatorio.lods).map(([l, d]) => `${l} ${d.triangulos.toLocaleString('pt-BR')}`).join(' · ');
  return `silhueta ${(s.iouTolerancia * 100).toFixed(1)} % (bruto ${(s.iouBruto * 100).toFixed(1)} %) · ${t} triângulos · ${(bytes / 1048576).toFixed(2)} MB`
    + resumoPega(relatorio.empunhadura);
}

/** A pega das luvas numa linha: a maior entrada na arma e o contato mais longe de cada mão (Fase 4.1b). */
function resumoPega(e) {
  if (!e) return '';
  const maos = ['d', 'e'].map((l) => {
    const c = Object.entries(e[l].contatosMM);
    const [nome, mm] = c.reduce((a, b) => (b[1] > a[1] ? b : a));
    return `${l === 'd' ? 'direita' : 'esquerda'} entra ${e[l].penetracaoMM} mm, contato mais longe ${nome} ${mm} mm`;
  });
  return ` · pega (${e.segundos} s): ${maos.join('; ')}`;
}

/** Contexto das luvas para o principal.py: a ficha validada, o registro (pinturas e orçamento), as pastas e o hash. */
async function contextoLuvas() {
  const { validarFichaLuvas } = await import('../src/characters/hands/fichaLuvas.js');
  const ficha = validarFichaLuvas(JSON.parse(readFileSync(join(ROOT, 'tools', 'blender', 'refs', 'luvas.json'), 'utf8')));
  const ctx = {
    id: 'luvas', raiz: ROOT, ficha, pinturas: LUVAS.pinturas, orcamento: LUVAS.orcamento, saida: join(ROOT, LUVAS.pasta),
    conferencia: join(ROOT, 'tools', 'blender', 'conferencia', 'luvas'), hash: hashEntradas('luvas', LUVAS, ficha),
  };
  mkdirSync(TMP, { recursive: true });
  const arquivo = join(TMP, 'luvas-real.json');
  writeFileSync(arquivo, JSON.stringify(ctx));
  return { arquivo, ctx };
}

/** A linha `MASSACRE-<nome>` da saída do Blender, lida como JSON. */
function linhaJson(saida, nome) {
  const linha = saida.split('\n').find((l) => l.startsWith(`MASSACRE-${nome} `));
  if (!linha) throw new Error(`o Blender não devolveu a linha MASSACRE-${nome}`);
  return JSON.parse(linha.slice(`MASSACRE-${nome} `.length));
}

/** As contas das luvas numa linha: os triângulos, cada medida com o alvo e o desvio, e o assentamento das peças. */
// As poses de teste do relatório das luvas: a maior penetração da luva nela mesma (e em que pose), a das juntas
// sozinhas no limite, a junta que mais afinou, o pior assentamento das peças e o encosto da polpa do polegar nos dedos.
function resumoPoses(poses) {
  let pen = { mm: 0, pose: '—' };
  let junta = { razao: 1, nome: '—', pose: '—' };
  let assento = 0;
  for (const [nome, p] of Object.entries(poses)) {
    if (typeof p?.atravessaMM !== 'number') continue;
    if (p.atravessaMM > pen.mm) pen = { mm: p.atravessaMM, pose: nome };
    if (p.piorJunta && p.piorJunta[1] < junta.razao) junta = { razao: p.piorJunta[1], nome: p.piorJunta[0], pose: nome };
    assento = Math.max(assento, p.assentamentoMM);
  }
  const limite = Object.values(poses.juntasNoLimite ?? {}).reduce((m, j) => Math.max(m, j.atravessaMM), 0);
  const polegar = Object.entries(poses.contato ?? {})
    .filter(([, c]) => typeof c?.polegar?.polpaEncostaMM === 'number')
    .map(([nome, c]) => `${nome} ${c.polegar.polpaEncostaMM} mm`);
  return `poses: penetração ${pen.mm} mm (${pen.pose}), juntas no limite ${limite} mm, `
    + `pior junta ${junta.razao} (${junta.nome}, ${junta.pose}), assento ${assento} mm, `
    + `polpa do polegar nos dedos (${polegar.join(', ')})`;
}

function resumoLuvas(rel) {
  const medidas = Object.entries(rel.medidas)
    .map(([nome, m]) => `${nome} ${m.mm.toFixed(2)}/${m.alvo.toFixed(2)} mm (${((m.mm / m.alvo - 1) * 100).toFixed(2)} %)`);
  const t = rel.triangulos;
  return `${t.luva.toLocaleString('pt-BR')} triângulos por luva (base ${t.base.toLocaleString('pt-BR')}, detalhes `
    + `${t.detalhes.toLocaleString('pt-BR')}) · ${medidas.join(' · ')} · assentamento ${rel.assentamentoMM} mm · `
    + resumoPoses(rel.poses);
}

/** A saída das luvas em assets/maos/ conferida contra o registro (tools/blender/saidaLuvas.mjs); lança os problemas. */
function saidaLuvas() {
  const { problemas, bytes } = validarSaidaLuvas(ROOT);
  if (problemas.length) throw new Error(`luvas: a saída em ${LUVAS.pasta} tem problemas:\n  - ${problemas.join('\n  - ')}`);
  return `${LUVAS.pasta}luvas.glb e texturas em ${(bytes / 1048576).toFixed(2)} MB`;
}

async function construirLuvas(forcar) {
  const { arquivo, ctx } = await contextoLuvas();
  const rel = join(ctx.saida, 'luvas.relatorio.json');
  if (!forcar && existsSync(rel)) {
    const antigo = JSON.parse(readFileSync(rel, 'utf8'));
    if (antigo.entradas?.hash === ctx.hash && !validarSaidaLuvas(ROOT).problemas.length) {
      return `luvas: sem mudança nas entradas — ${resumoLuvas(antigo)} · ${saidaLuvas()}`;
    }
  }
  const t0 = Date.now();
  const saida = await rodarComEtapas(['construir', arquivo], SCRIPT_REAIS, 'luvas');
  return `luvas: construídas em ${((Date.now() - t0) / 1000).toFixed(0)} s — ${resumoLuvas(linhaJson(saida, 'LUVAS'))} · `
    + saidaLuvas();
}

async function validarLuvas() {
  const { arquivo } = await contextoLuvas();
  const rel = linhaJson(rodarSemJanela(['validar', arquivo], SCRIPT_REAIS), 'VALIDACAO');
  return `luvas: validação aprovada — ${resumoLuvas(rel)} · ${saidaLuvas()}`;
}

async function conferirLuvas() {
  const { arquivo, ctx } = await contextoLuvas();
  const arquivos = linhaJson(rodarSemJanela(['conferir', arquivo], SCRIPT_REAIS), 'CONFERIR');
  return `luvas: ${arquivos.length} vistas em ${ctx.conferencia}`;
}

async function abrirLuvas() {
  const blend = join(ROOT, 'tools', 'blender', 'conferencia', 'luvas', 'luvas.blend');
  if (!existsSync(blend)) throw new Error('luvas: rode antes npm run blender -- construir luvas');
  const filho = spawn(blenderExe(), [blend], { detached: true, stdio: 'ignore' });
  filho.unref();
  return `Blender aberto com ${blend}`;
}
```

Em `tools/blender.mjs`, trocar:

```
  if (acao === 'construir' || (acao === 'validar' && alvo && !alvo.endsWith('.js'))) {
    if (!alvo) throw new Error(`uso: npm run blender -- ${acao} <${Object.keys(ARMAS_REAIS).join('|')}|todas>`);
    let falhas = 0;
    for (const id of alvo === 'todas' ? Object.keys(ARMAS_REAIS) : [alvo]) {
      try {
        if (!real(id)) throw new Error(`${id} não é uma arma realista (tem: ${Object.keys(ARMAS_REAIS).join(', ')})`);
```

por:

```
  if (acao === 'construir' || (acao === 'validar' && alvo && !alvo.endsWith('.js'))) {
    if (!alvo) throw new Error(`uso: npm run blender -- ${acao} <luvas|${Object.keys(ARMAS_REAIS).join('|')}|todas>`);
    let falhas = 0;
    for (const id of alvo === 'todas' ? ['luvas', ...Object.keys(ARMAS_REAIS)] : [alvo]) {
      try {
        if (id === 'luvas') {
          console.log(acao === 'construir' ? await construirLuvas(forcar) : await validarLuvas());
          continue;
        }
        if (!real(id)) throw new Error(`${id} não é uma arma realista (tem: ${Object.keys(ARMAS_REAIS).join(', ')})`);
```

Em `tools/blender.mjs`, trocar:

```
  const deMassinha = Object.keys(ARMAS).filter((id) => !real(id));
  const ids = alvo !== 'todas' ? [alvo] : acao === 'conferir' ? [...Object.keys(ARMAS_REAIS), ...deMassinha] : deMassinha;
  const acoes = {
    abrir: (id) => (real(id) ? abrirReal(id) : abrir(id)),
    conferir: (id) => (real(id) ? conferirReal(id) : conferir(id)),
    'ida-volta': idaVolta,
```

por:

```
  const deMassinha = Object.keys(ARMAS).filter((id) => !real(id));
  const ids = alvo !== 'todas' ? [alvo] : acao === 'conferir' ? ['luvas', ...Object.keys(ARMAS_REAIS), ...deMassinha] : deMassinha;
  const acoes = {
    abrir: (id) => (id === 'luvas' ? abrirLuvas() : real(id) ? abrirReal(id) : abrir(id)),
    conferir: (id) => (id === 'luvas' ? conferirLuvas() : real(id) ? conferirReal(id) : conferir(id)),
    'ida-volta': idaVolta,
```

Em `tools/blender/saida.mjs`, trocar:

```
// as peças da arma, as zonas, os soquetes da categoria, os triângulos e as texturas do orçamento, as tangentes e as UV
// do nível de perto, o total dos arquivos e os números do relatório (medidas ±1 %, silhueta ≥ 98 % com tolerância).

```

por:

```
// as peças da arma, as zonas, os soquetes da categoria, os triângulos e as texturas do orçamento, as tangentes e as UV
// do nível de perto, o total dos arquivos e os números do relatório (medidas ±1 %, silhueta ≥ 98 % com tolerância); desde
// a 4.1b, a pega das luvas nas categorias com regra (saidaPega.mjs e src/characters/hands/pega.js).

```

Em `tools/blender/saida.mjs`, trocar:

```
import { ARMAS_REAIS, LODS_REAIS, orcamentoDaArma, soquetesDaArma } from '../../src/data/armasReais.js';

```

por:

```
import { ARMAS_REAIS, LODS_REAIS, orcamentoDaArma, soquetesDaArma } from '../../src/data/armasReais.js';
import { CATEGORIAS_COM_PEGA, LUVAS } from '../../src/data/luvas.js';
import { lerPega } from '../../src/characters/hands/pega.js';
import { validarPega } from './saidaPega.mjs';

```

Em `tools/blender/saida.mjs`, trocar:

```
            if (zona) zonasUsadas.add(zona);
            if (!p.attributes.TANGENT) lod.tangentes = false;
            if (!p.attributes.TEXCOORD_0) lod.uv = false;
          }
```

por:

```
            if (zona) zonasUsadas.add(zona);
            if (p.attributes.TANGENT === undefined) lod.tangentes = false; // pela chave: o acessor 0 é válido
            if (p.attributes.TEXCOORD_0 === undefined) lod.uv = false;
          }
```

Em `tools/blender/saida.mjs`, trocar:

```

  const resumo = resumoGlb(lerGlb(readFileSync(join(pasta, arqs.glb))).json, id);
  const pecas = ['base', ...a.pecas];
```

por:

```

  const json = lerGlb(readFileSync(join(pasta, arqs.glb))).json;
  const resumo = resumoGlb(json, id);
  const pecas = ['base', ...a.pecas];
```

Em `tools/blender/saida.mjs`, trocar:

```
  }
  return { problemas, resumo, relatorio, bytes };
```

por:

```
  }
  // A pega das luvas (Fase 4.1b): nas categorias com regra, os nós e o clipe no .glb, a seção do relatório e a marca
  // igual à do luvas.glb (se as luvas já foram construídas).
  if (CATEGORIAS_COM_PEGA.includes(a.categoria)) {
    try {
      const glbLuvas = join(raiz, LUVAS.pasta, 'luvas.glb');
      const marcaLuvas = existsSync(glbLuvas)
        ? lerGlb(readFileSync(glbLuvas)).json.nodes?.find((n) => n.name === 'luvas')?.extras?.marca ?? null
        : null;
      problemas.push(...validarPega(relatorio, lerPega(json), marcaLuvas));
    } catch (e) {
      problemas.push(e.message);
    }
  }
  return { problemas, resumo, relatorio, bytes };
```

- [ ] **Construir no Blender** — `npm run blender -- construir luvas` (aprovado, sem problema na validação).

- [ ] **Construir no Blender** — `npm run blender -- construir ak47 --forcar` (aprovado, sem problema na validação).

Run: `node --test tests/luvasSaida.test.js tests/luvasGlb.test.js tests/modeloDobras.test.js tests/pegaGlb.test.js`
Expected: PASS — # tests 24 # pass 24 # fail 0 .

Run: `node --test "tests/**/*.test.js"`
Expected: PASS — # tests 405 # pass 405 # fail 0 .

### Tarefa 7: Solver de empunhadura e a pega da AK

**Files:** Create `empunhadura.py`, `tests/pegaGlb.test.js`; Modify `principal.py` (solver no `construir` das armas),
`exportar.py` (a pega), `conferir.py` (vistas de perto das mãos), `validar.py` (a seção `empunhadura`), `ak47.py` (se
precisar de correção), `tools/blender.mjs` (D5), `tools/blender/saida.mjs` (a pega na saída das armas).

- [ ] **Passo 1: Testes** — `tests/pegaGlb.test.js`: `lerPega(gltfJson)` (em `src/characters/hands/pega.js`) acha
  `pega_mao_d`/`pega_mao_e`, o clipe (ou os `extras`, pela D1) com as trilhas dos 34 ossos de dedos, a marca e as
  sondas; recusa pega sem um dos nós, com osso de dedo faltando ou com nome desconhecido; `validarSaida` da AK aponta
  relatório sem `empunhadura`, penetração acima de 0,3 mm e contato acima de 1 mm; e o `.glb` real da AK (depois do
  `construir`) passa, com a marca igual à do `luvas.glb`.
- [ ] **Passo 2: Ver falhar.**
- [ ] **Passo 3: O solver** — em `empunhadura.py`, sobre o rig refeito pelo `maos.py`/`maos_rig.py` (sem assar) e a
  malha de jogo da arma (as peças do `perto` juntas, peças móveis em repouso) numa BVH:
  1. a palma no soquete e deslizando pela normal dele até encostar;
  2. cada dedo fechando junta a junta por bisseção (tolerância 0,05°) até a polpa daquela falange encostar, dentro dos
     limites da ficha, com a DIP livre acompanhando 2/3 da PIP;
  3. correção entre vizinhos pela abertura na MCP (±20°), senão o de fora recua;
  4. as regras do `rifle` (indicador na face do gatilho a 60 % da altura, folga ≥ 1 mm do guarda-mato; polegar para o
     lado esquerdo do punho; a esquerda por baixo do guarda-mão, dedos pela direita, polegar pela esquerda);
  5. as correções da arma (`EMPUNHADURA` no script da arma), se houver.
- [ ] **Passo 4: A validação da pega** — na malha deformada avaliada pelo Blender: penetração ≤ 0,3 mm, cada contato
  da regra ≤ 1 mm, dedos sem se atravessar (≤ 0,3 mm), ângulos nos limites; a seção `empunhadura` do relatório.
- [ ] **Passo 5: A saída** — os nós `pega`, `pega_mao_d`, `pega_mao_e` (referencial do osso `mao_*` na pose, em u) e o
  clipe `empunhadura` (ou os `extras`, pela D1), a marca e as sondas.
- [ ] **Passo 6: `npm run blender -- construir ak47 --forcar`** aprovado com a pega; vistas de perto das duas mãos na
  `conferir`; **ver passar** os testes; suíte inteira.
- [ ] **Passo 7: Revisão crítica da pega** (as vistas contra as fotos de mãos segurando AK da seção 15 do moodboard:
  o polegar, o indicador no gatilho, a mão de apoio, a altura da mão no punho).


**Código da tarefa:** nenhum arquivo novo — o `principal.py` chama o solver da pega no `construir` de cada arma, então o solver inteiro e a saída da pega entraram com a Tarefa 6; aqui fica a construção da AK com a pega e a conferência (o validador constrói a AK logo depois da Tarefa 6).

### Tarefa 8: Acabamentos e material das luvas

**Files:** Modify `src/data/acabamentos.js`, `src/weapons/model/materialArma.js`, `glsl/acabamentos.js`,
`src/data/luvas.js` (pinturas por facção); Create `tests/materialLuva.test.js`.

- [ ] **Passo 1: Testes** — `acabamentoParaMaterial` com `couro`, `tecido` e `borracha`: metalicidade 0; aspereza nas
  faixas (couro 0,45–0,65; tecido 0,8–0,95; borracha 0,55–0,75); o `tecido` liga o `sheen` (cor e aspereza do brilho de
  tecido) e os outros não; o padrão procedural certo (`ARMA_PADRAO` da trama e do grão); as pinturas de Massa Crua e
  Tropa do Estúdio do desenho (seção 7.1) passam pela validação das skins (zona e acabamento existentes, cores
  válidas).
- [ ] **Passo 2: Ver falhar**; **Passo 3: implementar**; **Passo 4: ver passar**; suíte inteira.


**Código da tarefa** (a versão verificada no navegador e no Blender; os blocos `file=` são o arquivo inteiro, os pares são aplicados na ordem).

- [ ] **Os testes** — `tests/materialLuva.test.js`, `tests/materialArma.test.js`, `tests/skinsArma.test.js`:

```js file=tests/materialLuva.test.js
// Os acabamentos das luvas (Fase 4.1b; desenho em docs/superpowers/specs/2026-09-26-4.1b-luvas-e-empunhadura-design.md,
// seção 7.2; plano, Tarefa 8): couro, tecido (com o brilho de tecido, o `sheen` do material físico) e borracha — os
// números da função pura, o material de zona com o brilho e o padrão pela pose de repouso (a malha das luvas se deforma
// na CPU: o padrão lê os atributos de repouso), e as pinturas das duas facções pela validação das skins.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import * as THREE from 'three';
import { PADROES } from '../src/data/acabamentos.js';
import { LUVAS, ZONAS_DAS_LUVAS } from '../src/data/luvas.js';
import { acabamentoParaMaterial } from '../src/weapons/skins/acabamento.js';
import { validarPintura } from '../src/weapons/skins/skin.js';
import { criarMaterialZona } from '../src/weapons/model/materialArma.js';

const FAIXAS = { couro: [0.45, 0.65], tecido: [0.8, 0.95], borracha: [0.55, 0.75] };
const PADRAO = { couro: 'grao', tecido: 'trama', borracha: 'pontilhado' };

test('couro, tecido e borracha: sem metal, a aspereza na faixa e o padrão procedural deles', () => {
  for (const [acabamento, [a, b]] of Object.entries(FAIXAS)) {
    const p = acabamentoParaMaterial({ acabamento, cor: '#8B6B4A' });
    assert.equal(p.metalness, 0, acabamento);
    assert.ok(p.roughness >= a && p.roughness <= b, `${acabamento}: aspereza ${p.roughness} fora de ${a}–${b}`);
    assert.equal(p.padrao, PADRAO[acabamento]);
    assert.equal(p.padraoId, PADROES.indexOf(PADRAO[acabamento]));
    assert.ok(p.padraoId > 0);
  }
});

test('só o tecido liga o brilho de tecido, com a cor e a aspereza dele', () => {
  const t = acabamentoParaMaterial({ acabamento: 'tecido', cor: '#6B5038' });
  assert.ok(t.sheen > 0);
  assert.ok(t.sheenRoughness > 0 && t.sheenRoughness < 1);
  assert.equal(t.sheenColor.length, 3);
  assert.ok(t.sheenColor[0] > t.color[0], 'o brilho mais claro que o fio');
  assert.ok(t.recursos.includes('tecido'));
  for (const acabamento of ['couro', 'borracha', 'oxidado', 'madeira']) {
    const p = acabamentoParaMaterial({ acabamento, cor: '#303135' });
    assert.equal(p.sheen, 0, acabamento);
    assert.ok(!p.recursos.includes('tecido'), acabamento);
  }
});

test('o couro e o tecido escurecem o fundo do padrão (a segunda cor sai da primeira)', () => {
  for (const acabamento of ['couro', 'tecido']) {
    const p = acabamentoParaMaterial({ acabamento, cor: '#8B6B4A' });
    assert.ok(p.color2 && p.color2[0] < p.color[0], acabamento);
  }
});

test('material de zona das luvas: o brilho de tecido, a chave do programa e o padrão pela pose de repouso', () => {
  const texturas = { n: new THREE.Texture(), m: new THREE.Texture() };
  const t = criarMaterialZona({ zona: 'tecido', def: { acabamento: 'tecido', cor: '#6B5038', desgaste: 0.15 }, texturas, repouso: true });
  assert.equal(t.sheen, 1);
  assert.ok(t.sheenRoughness > 0);
  assert.ok(t.sheenColor.r > t.color.r);
  assert.equal(t.customProgramCacheKey(), 'arma:trama:tecido:repouso');
  assert.equal(t.defines.ARMA_REPOUSO, '');
  const shader = { uniforms: {}, vertexShader: THREE.ShaderLib.physical.vertexShader, fragmentShader: THREE.ShaderLib.physical.fragmentShader };
  t.onBeforeCompile(shader);
  assert.match(shader.vertexShader, /attribute vec3 repouso;\nattribute vec3 normalRepouso;/);
  assert.match(shader.vertexShader, /#ifdef ARMA_REPOUSO\nvPosArma = repouso;\nvNormalArma = normalRepouso;/);
  const c = criarMaterialZona({ zona: 'couro', def: { acabamento: 'couro', cor: '#8B6B4A' }, texturas });
  assert.equal(c.sheen, 0);
  assert.equal(c.defines.ARMA_REPOUSO, undefined, 'as armas leem a posição da malha');
  assert.equal(c.customProgramCacheKey(), 'arma:grao:');
  assert.equal(c.defines.ARMA_PADRAO, PADROES.indexOf('grao'));
});

test('as pinturas de Massa Crua e da Tropa do Estúdio passam pela validação das skins', () => {
  for (const [faccao, pintura] of Object.entries(LUVAS.pinturas)) {
    const v = validarPintura(ZONAS_DAS_LUVAS, pintura);
    assert.deepEqual(Object.keys(v.zonas).sort(), [...ZONAS_DAS_LUVAS].sort(), faccao);
    assert.equal(v.zonas.couro.acabamento, 'couro');
    assert.equal(v.zonas.tecido.acabamento, 'tecido');
    assert.equal(v.zonas.reforco.acabamento, 'borracha');
  }
  assert.throws(() => validarPintura(ZONAS_DAS_LUVAS, { zonas: { couro: LUVAS.pinturas.tropa.zonas.couro } }), /tecido/);
  assert.throws(() => validarPintura(ZONAS_DAS_LUVAS, { zonas: { ...LUVAS.pinturas.tropa.zonas, tecido: { acabamento: 'linho', cor: '#000000' } } }), /linho/);
});
```

Em `tests/materialArma.test.js`, trocar:

```
  }
  assert.match(shader.vertexShader, /vPosArma = position;/);
  assert.match(shader.fragmentShader, /vec4 armaM = texture2D\( mapaM, vAoMapUv \);/);
```

por:

```
  }
  assert.match(shader.vertexShader, /#else\nvPosArma = position;\nvNormalArma = normal;/);
  assert.match(shader.fragmentShader, /vec4 armaM = texture2D\( mapaM, vAoMapUv \);/);
```

Em `tests/skinsArma.test.js`, trocar:

```

test('acabamentos: os 15 da seção 6.1 com metal e aspereza da tabela', () => {
  const tabela = {
```

por:

```

// Os 15 da seção 6.1 do desenho das armas mais os 2 das luvas (4.1b: couro e tecido); a borracha passou a ser a borracha
// moldada (TPR) semifosca das luvas e das armas (0,9 → 0,68, desenho da 4.1b, seção 7.2).
test('acabamentos: os 15 da seção 6.1 e os 2 das luvas com metal e aspereza da tabela', () => {
  const tabela = {
```

Em `tests/skinsArma.test.js`, trocar:

```
    metalico: [0.6, 0.35], perolado: [0.2, 0.3], anodizado: [1, 0.25], escovado: [1, 0.3], cromado: [1, 0.05],
    cerakote: [0, 0.7], carbono: [0, 0.35], madeira: [0, 0.45], polimero: [0, 0.65], borracha: [0, 0.9],
  };
```

por:

```
    metalico: [0.6, 0.35], perolado: [0.2, 0.3], anodizado: [1, 0.25], escovado: [1, 0.3], cromado: [1, 0.05],
    cerakote: [0, 0.7], carbono: [0, 0.35], madeira: [0, 0.45], polimero: [0, 0.65], borracha: [0, 0.68],
    couro: [0, 0.56], tecido: [0, 0.88],
  };
```

Run: `node --test tests/materialLuva.test.js tests/materialArma.test.js tests/skinsArma.test.js`
Expected: FAIL — # tests 15 # pass 12 # fail 3 .

- [ ] **A implementação** — `src/data/acabamentos.js`, `src/weapons/skins/acabamento.js`, `src/weapons/skins/skin.js`, `src/weapons/model/materialArma.js`, `src/weapons/model/glsl/acabamentos.js`:

Em `src/data/acabamentos.js`, trocar:

```
// quanto a variação assada (_m.g e _m.a, em torno de 0,5) mexe na aspereza e na cor. `verniz` liga a camada de verniz
// (clearcoat), `iridescencia` o filme fino, `anisotropia` o escovado ao longo do X da arma — só quando o acabamento
// pede, para limitar as variantes de shader. `cor2Fator` faz a segunda cor (veio, trama) quando a skin não traz uma.

```

por:

```
// quanto a variação assada (_m.g e _m.a, em torno de 0,5) mexe na aspereza e na cor. `verniz` liga a camada de verniz
// (clearcoat), `iridescencia` o filme fino, `anisotropia` o escovado ao longo do X da arma, `brilhoTecido` o brilho de
// tecido (o sheen do material físico: a intensidade, a aspereza e o quanto a cor dele clareia a do fio) — só quando o
// acabamento pede, para limitar as variantes de shader. `cor2Fator` faz a segunda cor (veio, trama, o fundo do grão)
// quando a skin não traz uma. Os das luvas (Fase 4.1b; desenho da 4.1b, seção 7.2): o couro sintético da palma e das
// pontas, com o grão fino; o tecido elástico das costas, com a trama e o brilho de tecido; a borracha moldada (TPR) do
// protetor dos nós, das almofadas e da tira, pontilhada. O grão, a trama e o pontilhado são finos demais para o assar
// (viravam moiré na _n; plano da 4.1b, Tarefa 6) e saem do shader.

```

Em `src/data/acabamentos.js`, trocar:

```
// Padrões procedurais do shader, na ordem do define ARMA_PADRAO.
export const PADROES = F(['nenhum', 'fino', 'granulado', 'flocos', 'carbono', 'veio', 'pontilhado', 'ceramica']);

```

por:

```
// Padrões procedurais do shader, na ordem do define ARMA_PADRAO.
export const PADROES = F(['nenhum', 'fino', 'granulado', 'flocos', 'carbono', 'veio', 'pontilhado', 'ceramica', 'grao', 'trama']);

```

Em `src/data/acabamentos.js`, trocar:

```
  polimero: F({ nome: 'Polímero texturizado', metal: 0, aspereza: 0.65, padrao: 'pontilhado', varAspereza: 0.08, varCor: 0.05, gasto: F({ cor: '#6E7074', metal: 0, aspereza: 0.8 }) }),
  borracha: F({ nome: 'Borracha', metal: 0, aspereza: 0.9, padrao: 'nenhum', varAspereza: 0.05, varCor: 0.04, gasto: F({ cor: '#55575B', metal: 0, aspereza: 0.95 }) }),
});
```

por:

```
  polimero: F({ nome: 'Polímero texturizado', metal: 0, aspereza: 0.65, padrao: 'pontilhado', varAspereza: 0.08, varCor: 0.05, gasto: F({ cor: '#6E7074', metal: 0, aspereza: 0.8 }) }),
  // Borracha moldada (TPR): semifosca, com o pontilhado do molde; gasta, fica mais lisa e um pouco mais clara.
  borracha: F({ nome: 'Borracha', metal: 0, aspereza: 0.68, padrao: 'pontilhado', varAspereza: 0.06, varCor: 0.04, gasto: F({ cor: '#55575B', metal: 0, aspereza: 0.5 }) }),
  // Couro sintético: brilho leve, o grão pequeno com o fundo das dobrinhas mais escuro; gasto, alisa e clareia.
  couro: F({ nome: 'Couro', metal: 0, aspereza: 0.56, padrao: 'grao', cor2Fator: 0.8, varAspereza: 0.08, varCor: 0.06, gasto: F({ cor: '#9C8468', metal: 0, aspereza: 0.4 }) }),
  // Tecido elástico: bem fosco, a trama com o fundo mais escuro e o brilho de tecido rente à superfície.
  tecido: F({
    nome: 'Tecido', metal: 0, aspereza: 0.88, padrao: 'trama', cor2Fator: 0.72, brilhoTecido: F({ intensidade: 1, aspereza: 0.5, clareia: 0.35 }),
    varAspereza: 0.04, varCor: 0.05, gasto: F({ cor: '#8A7F74', metal: 0, aspereza: 0.95 }),
  }),
});
```

Em `src/weapons/skins/acabamento.js`, trocar:

```
 *   clearcoat:number, clearcoatRoughness:number, iridescence:number, iridescenceIOR:number,
 *   iridescenceThicknessRange:number[], anisotropy:number, padrao:string, padraoId:number, varAspereza:number,
 *   varCor:number, desgaste:number, gasto:{color:number[], metalness:number, roughness:number}, recursos:string[]}}
 *   cores em linear; `recursos` = os do material físico que o acabamento liga (verniz, iridescência, anisotropia)
 */
```

por:

```
 *   clearcoat:number, clearcoatRoughness:number, iridescence:number, iridescenceIOR:number,
 *   iridescenceThicknessRange:number[], anisotropy:number, sheen:number, sheenRoughness:number, sheenColor:number[],
 *   padrao:string, padraoId:number, varAspereza:number,
 *   varCor:number, desgaste:number, gasto:{color:number[], metalness:number, roughness:number}, recursos:string[]}}
 *   cores em linear; `recursos` = os do material físico que o acabamento liga (verniz, iridescência, anisotropia,
 *   tecido — o brilho de tecido)
 */
```

Em `src/weapons/skins/acabamento.js`, trocar:

```
    color2 = hex2 ? hexParaLinear(hex2) : color.map((c) => limitar(c * a.cor2Fator, 0, 1));
  }
  const clearcoat = a.verniz ?? 0;
```

por:

```
    color2 = hex2 ? hexParaLinear(hex2) : color.map((c) => limitar(c * a.cor2Fator, 0, 1));
  } else if (a.cor2Fator) {
    color2 = color.map((c) => limitar(c * a.cor2Fator, 0, 1)); // o fundo do padrão (o grão, a trama), da própria cor
  }
  const brilho = a.brilhoTecido ?? null;
  const clearcoat = a.verniz ?? 0;
```

Em `src/weapons/skins/acabamento.js`, trocar:

```
  if (anisotropy > 0) recursos.push('anisotropia');
  return {
```

por:

```
  if (anisotropy > 0) recursos.push('anisotropia');
  if (brilho) recursos.push('tecido');
  return {
```

Em `src/weapons/skins/acabamento.js`, trocar:

```
    anisotropy,
    padrao: a.padrao,
```

por:

```
    anisotropy,
    sheen: brilho ? brilho.intensidade : 0,
    sheenRoughness: brilho ? brilho.aspereza : 0,
    sheenColor: brilho ? color.map((c) => c + (1 - c) * brilho.clareia) : [0, 0, 0],
    padrao: a.padrao,
```

Em `src/weapons/skins/skin.js`, trocar:

```

/** Skin completa e válida para a arma (todas as zonas dela). */
export function validarSkin(id, skin) {
  const a = arma(id);
  const zonas = {};
  for (const z of a.zonas) {
    if (!skin?.zonas?.[z]) throw new Error(`skin de ${id} sem a zona ${z}`);
    zonas[z] = zonaValida(z, skin.zonas[z]);
  }
  return { chave: skin.chave ?? PERSONALIZADA, nome: skin.nome ?? 'Personalizada', zonas };
}
```

por:

```

/**
 * Pintura completa e válida para uma lista de zonas (as de uma arma, as das luvas): acabamento e cores reconhecidos e
 * desgaste de 0 a 1 em cada zona.
 */
export function validarPintura(zonasDaPeca, pintura, rotulo = 'pintura') {
  const zonas = {};
  for (const z of zonasDaPeca) {
    if (!pintura?.zonas?.[z]) throw new Error(`${rotulo} sem a zona ${z}`);
    zonas[z] = zonaValida(z, pintura.zonas[z]);
  }
  return { chave: pintura.chave ?? PERSONALIZADA, nome: pintura.nome ?? 'Personalizada', zonas };
}

/** Skin completa e válida para a arma (todas as zonas dela). */
export function validarSkin(id, skin) {
  return validarPintura(arma(id).zonas, skin, `skin de ${id}`);
}
```

Em `src/weapons/model/materialArma.js`, trocar:

```
// de shader, e a chave do programa diz qual (defines + customProgramCacheKey), para a compilação no carregamento
// (renderer.compileAsync, no viewmodel e na bancada) cobrir todas.

```

por:

```
// de shader, e a chave do programa diz qual (defines + customProgramCacheKey), para a compilação no carregamento
// (renderer.compileAsync, no viewmodel e na bancada) cobrir todas. As luvas (Fase 4.1b) usam o mesmo material, com o
// brilho de tecido no tecido e o padrão pela pose de repouso (`repouso`: a malha delas se deforma na CPU).

```

Em `src/weapons/model/materialArma.js`, trocar:

```
 * @param {{zona:string, def:{acabamento:string, cor:string, cor2?:string|null, desgaste?:number},
 *   texturas:{n:THREE.Texture, m:THREE.Texture}, ambiente?:THREE.Texture|null, intensidade?:number, nome?:string}} o
 *   `ambiente` = o reflexo do set (null: o ambiente da cena); `intensidade` = a dele no material
 * @returns {THREE.MeshPhysicalMaterial} marcado `userData.shared` (quem cria descarta)
 */
export function criarMaterialZona({ zona, def, texturas, ambiente = null, intensidade = 1, nome = `arma:${zona}` }) {
  const p = acabamentoParaMaterial(def);
```

por:

```
 * @param {{zona:string, def:{acabamento:string, cor:string, cor2?:string|null, desgaste?:number},
 *   texturas:{n:THREE.Texture, m:THREE.Texture}, ambiente?:THREE.Texture|null, intensidade?:number, nome?:string,
 *   repouso?:boolean}} o
 *   `ambiente` = o reflexo do set (null: o ambiente da cena); `intensidade` = a dele no material; `repouso` = o padrão
 *   pelos atributos de repouso da malha (`repouso`, `normalRepouso`), nas malhas que se deformam na CPU (as luvas)
 * @returns {THREE.MeshPhysicalMaterial} marcado `userData.shared` (quem cria descarta)
 */
export function criarMaterialZona({ zona, def, texturas, ambiente = null, intensidade = 1, nome = `arma:${zona}`, repouso = false }) {
  const p = acabamentoParaMaterial(def);
```

Em `src/weapons/model/materialArma.js`, trocar:

```
    anisotropy: p.anisotropy,
  });
```

por:

```
    anisotropy: p.anisotropy,
    sheen: p.sheen,
    sheenRoughness: p.sheenRoughness,
    sheenColor: linear(p.sheenColor),
  });
```

Em `src/weapons/model/materialArma.js`, trocar:

```
  if (p.anisotropy > 0) m.defines.ARMA_ESCOVADO = '';
  const u = {
```

por:

```
  if (p.anisotropy > 0) m.defines.ARMA_ESCOVADO = '';
  if (repouso) m.defines.ARMA_REPOUSO = '';
  const u = {
```

Em `src/weapons/model/materialArma.js`, trocar:

```
  };
  m.customProgramCacheKey = () => `arma:${p.padrao}:${p.recursos.join('+')}`;
  return m;
```

por:

```
  };
  m.customProgramCacheKey = () => `arma:${p.padrao}:${p.recursos.join('+')}${repouso ? ':repouso' : ''}`;
  return m;
```

Em `src/weapons/model/glsl/acabamentos.js`, trocar:

```
// da arma. Nenhum boil, nenhuma digital de massinha. ARMA_PADRAO segue a ordem de PADROES (src/data/acabamentos.js).

export const ARMA_VERTEX_PARS = /* glsl */ `
varying vec3 vPosArma;
```

por:

```
// da arma. Nenhum boil, nenhuma digital de massinha. ARMA_PADRAO segue a ordem de PADROES (src/data/acabamentos.js).
// As luvas (Fase 4.1b) têm os padrões do couro (o grão: seixinhos arredondados de 0,8 mm com o vale largo e raso entre
// eles, nas células de Voronoi de domínio torcido) e do tecido (a malha de jérsei de 0,6 mm, os fios subindo e descendo);
// a borracha usa o pontilhado.
// A malha delas se deforma na CPU (o modelo das dobras, src/characters/hands/modeloDobras.js): com ARMA_REPOUSO, o
// padrão sai da posição e da normal de repouso (os atributos `repouso` e `normalRepouso`, u) e fica preso ao couro e ao
// tecido quando os dedos dobram, em vez de escorregar pela luva.

export const ARMA_VERTEX_PARS = /* glsl */ `
#ifdef ARMA_REPOUSO
attribute vec3 repouso;
attribute vec3 normalRepouso;
#endif
varying vec3 vPosArma;
```

Em `src/weapons/model/glsl/acabamentos.js`, trocar:

```
export const ARMA_VERTEX = /* glsl */ `
vPosArma = position;
vNormalArma = normal;
vEixoXVista = normalize( ( modelViewMatrix * vec4( 1.0, 0.0, 0.0, 0.0 ) ).xyz );
```

por:

```
export const ARMA_VERTEX = /* glsl */ `
#ifdef ARMA_REPOUSO
vPosArma = repouso;
vNormalArma = normalRepouso;
#else
vPosArma = position;
vNormalArma = normal;
#endif
vEixoXVista = normalize( ( modelViewMatrix * vec4( 1.0, 0.0, 0.0, 0.0 ) ).xyz );
```

Em `src/weapons/model/glsl/acabamentos.js`, trocar:

```
}
vec3 armaPesos( vec3 n ) {
```

por:

```
}
// Grão de couro (o seixinho do couro sintético de luva): a célula de Voronoi mais perto e a segunda, num plano; 0 no alto
// do seixo, subindo em rampa larga até 1 no vale entre dois, e o ombro do seixo arredondando para ele. O domínio vem
// torcido por ruído (as células saem irregulares, não polígonos) e o vale é largo e raso: o vale fino e escuro (0,18 da
// célula) da primeira versão desenhava uma rede de trincas, que de perto lia como verniz craquelado e não como couro.
float armaGrao( vec2 p ) {
  p += vec2( armaRuido( vec3( p * 0.6, 3.1 ) ), armaRuido( vec3( p * 0.6, 8.9 ) ) ) * 0.7 - 0.35;
  vec2 c = floor( p );
  vec2 f = fract( p );
  float d1 = 8.0;
  float d2 = 8.0;
  for ( int j = -1; j <= 1; j++ ) {
    for ( int i = -1; i <= 1; i++ ) {
      vec2 o = vec2( float( i ), float( j ) );
      vec2 r = o + vec2( armaHash( vec3( c + o, 1.7 ) ), armaHash( vec3( c + o, 5.3 ) ) ) - f;
      float d = dot( r, r );
      if ( d < d1 ) {
        d2 = d1;
        d1 = d;
      } else if ( d < d2 ) {
        d2 = d;
      }
    }
  }
  float vale = 1.0 - smoothstep( 0.04, 0.5, sqrt( d2 ) - sqrt( d1 ) );
  float ombro = smoothstep( 0.1, 0.7, sqrt( d1 ) );
  return clamp( vale * 0.75 + ombro * 0.25, 0.0, 1.0 );
}
// Malha de tecido (jérsei): fileiras de laçadas em V, o fio subindo e descendo; 1 no alto do fio, 0 no fundo.
float armaMalha( vec2 p ) {
  vec2 f = fract( p );
  float v = abs( fract( p.x + ( abs( f.y - 0.5 ) - 0.25 ) * 0.8 ) - 0.5 ) * 2.0;
  return smoothstep( 0.15, 0.85, v ) * ( 0.7 + 0.3 * sin( f.y * 3.14159265 ) );
}
vec3 armaPesos( vec3 n ) {
```

Em `src/weapons/model/glsl/acabamentos.js`, trocar:

```
    return vec2( 0.0, ( ( armaRuido( a ) - 0.5 ) * armaFiltro( a ) + ( armaRuido( b ) - 0.5 ) * armaFiltro( b ) ) * 0.08 );
  #else
```

por:

```
    return vec2( 0.0, ( ( armaRuido( a ) - 0.5 ) * armaFiltro( a ) + ( armaRuido( b ) - 0.5 ) * armaFiltro( b ) ) * 0.08 );
  #elif ARMA_PADRAO == 8
    // grão do couro: 31,75 células por u (0,8 mm); o vale vai um pouco para a segunda cor e fica mais áspero (o topo do
    // seixo, alisado pelo uso, brilha um pouco mais)
    float g = armaGrao( p.yz * 31.75 ) * w.x + armaGrao( p.xz * 31.75 ) * w.y + armaGrao( p.xy * 31.75 ) * w.z;
    g = mix( 0.35, g, armaFiltro( p * 31.75 ) );
    return vec2( g * 0.3, ( g - 0.35 ) * 0.14 );
  #elif ARMA_PADRAO == 9
    // trama do tecido: 42,3 laçadas por u (0,6 mm); o fundo na segunda cor, o alto do fio um pouco mais liso
    float t = armaMalha( p.yz * 42.3 ) * w.x + armaMalha( p.xz * 42.3 ) * w.y + armaMalha( p.xy * 42.3 ) * w.z;
    t = mix( 0.5, t, armaFiltro( p * 42.3 ) );
    return vec2( ( 1.0 - t ) * 0.6, ( 0.5 - t ) * 0.06 );
  #else
```

Run: `node --test tests/materialLuva.test.js tests/materialArma.test.js tests/skinsArma.test.js`
Expected: PASS — # tests 19 # pass 19 # fail 0 .

Run: `node --test "tests/**/*.test.js"`
Expected: PASS — # tests 410 # pass 410 # fail 0 .

### Tarefa 9: Carga das luvas, braço e antebraço de massinha

**Files:** Create `src/characters/hands/luvasSource.js`, `bracoLuva.js`, `antebracoMassa.js`,
`tests/luvasSource.test.js`, `tests/bracoLuva.test.js`; Modify `src/main.js` (o serviço `luvasModels`).

- [ ] **Passo 1: Testes da carga** (`tests/luvasSource.test.js`, com carregadores falsos como os da
  `weaponLibraryGlb.test.js`): uma carga só para pedidos ao mesmo tempo; materiais por (facção, zona) em cache e
  marcados `userData.shared`; `instanciar(lado, facção)` devolve um braço com esqueleto próprio (dois braços não
  dividem ossos); `setAmbiente` chega a todos os materiais; `dispose` descarta geometrias, materiais e texturas e
  recusa carga depois; erro de carga chega ao log com o arquivo.
- [ ] **Passo 2: Testes do braço** (`tests/bracoLuva.test.js`, sem GPU): `aplicarPega(pega, lado)` põe cada osso de
  dedo no quaternion do clipe; `colocar(pulso, cotovelo)`: o osso `mao` no pulso e na orientação da pega; o
  `antebraco` apontando do cotovelo para o pulso, com o comprimento da ficha; a torção dividida meio a meio entre
  `torcao` e `mao` (ângulo de rolagem de cada um = metade do total, ±0,5°); pulso fora dos limites da AAOS gera aviso
  com o ângulo; a pega com a marca diferente é recusada com a mensagem; `setFaccao` troca os materiais; `setBracadeira`
  (cor ou null) mostra/esconde a faixa de massa.
- [ ] **Passo 3: Ver falhar.**
- [ ] **Passo 4: `antebracoMassa.js`** — árvore SDF do antebraço (tronco de cone arredondado, largura e espessura da
  ficha no pulso, mais largo no cotovelo, até 60 mm depois do cotovelo), gerada uma vez por sessão no `SdfMesher`
  (workers e cache, como as mãos da 4.1), skin de dois ossos (`antebraco`, `torcao`), `ClayMaterial` na cor da massa do
  boneco com `boil: 0`; a braçadeira de massa da 4.1 (`armband.js`) presa ao `antebraco`.
- [ ] **Passo 5: `luvasSource.js` e `bracoLuva.js`**; **Passo 6: ver passar**; suíte inteira.


**Código da tarefa** (a versão verificada no navegador e no Blender; os blocos `file=` são o arquivo inteiro, os pares são aplicados na ordem).

- [ ] **Os testes** — `tests/sdfTronco.test.js`, `tests/antebracoMassa.test.js`, `tests/bracoLuva.test.js`, `tests/luvasSource.test.js`:

```js file=tests/sdfTronco.test.js
// A forma `tronco` do SDF (Fase 4.1b; o antebraço de massinha que entra no punho da luva): com a seção constante e o
// arredondamento das pontas igual ao canto, é a caixa arredondada da biblioteca; com a seção mudando, a superfície
// passa nas medidas de cada seção, o campo continua 1-Lipschitz, a caixa envolvente contém a massa, o intervalo é
// garantido, a malha sai fechada e bem orientada, e os nós inválidos explicam o problema.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { bounds, compile, createRange, evaluate, isEmptyBounds } from '../src/clay/sdf/nodes.js';
import { polygonize } from '../src/clay/sdf/marchingCubes.js';
import { lerTronco } from '../src/clay/sdf/tronco.js';
import { RNG } from '../src/core/rng.js';
import { meshReport } from './sdfTestUtils.js';

const near = (a, e, eps, msg) => assert.ok(Math.abs(a - e) <= eps, `${msg}: esperado ${e}, veio ${a}`);

// Um antebraço em miniatura: achatado no pulso (x = 0), mais largo e redondo no cotovelo (x = −10), girado e deslocado.
const ANTEBRACO = {
  type: 'tronco', round: 0.6, pos: [0.3, -0.2, 0.5], rot: [0.2, -0.4, 0.1],
  secoes: [[-10, 4.2, 2.6, 1.2], [-6, 3.4, 2.1, 1.05], [-3, 2.8, 1.8, 0.9], [0, 2.4, 1.5, 0.7]],
};

test('tronco de seção constante com as pontas arredondadas pelo canto = a caixa arredondada', () => {
  const rng = new RNG('tronco-caixa');
  const tronco = { type: 'tronco', round: 0.4, secoes: [[-3, 2.4, 1.6, 0.4], [3, 2.4, 1.6, 0.4]] };
  const caixa = { type: 'roundBox', size: [3, 0.8, 1.2], r: 0.4 };
  assert.equal(lerTronco(tronco, 'raiz').lipschitz, 1, 'a seção não muda: o campo é exato');
  for (let i = 0; i < 4000; i++) {
    const p = [rng.float(-5, 5), rng.float(-3, 3), rng.float(-3, 3)];
    near(evaluate(tronco, ...p), evaluate(caixa, ...p), 1e-12, `(${p.map((v) => v.toFixed(3))})`);
  }
});

test('tronco: a superfície passa nas medidas de cada seção e entre elas em linha reta', () => {
  const t = lerTronco({ ...ANTEBRACO, pos: undefined, rot: undefined }, 'raiz');
  for (const [x, l, e] of ANTEBRACO.secoes.slice(1, -1)) {
    near(t.d(x, 0, l / 2), 0, 1e-12, `meia largura em x = ${x}`);
    near(t.d(x, e / 2, 0), 0, 1e-12, `meia espessura em x = ${x}`);
    near(t.d(x, 0, -l / 2), 0, 1e-12, `do outro lado em x = ${x}`);
  }
  // a meio caminho entre −6 e −3: a média das duas seções
  near(t.d(-4.5, 0, (3.4 + 2.8) / 4), 0, 1e-12, 'largura interpolada');
  near(t.d(-4.5, (2.1 + 1.8) / 4, 0), 0, 1e-12, 'espessura interpolada');
  // o canto: a distância do centro do arco do canto é o raio
  const [x, l, e, r] = ANTEBRACO.secoes[1];
  const k = Math.SQRT1_2 * r;
  near(t.d(x, e / 2 - r + k, l / 2 - r + k), 0, 1e-12, 'no arco do canto');
  // as pontas: arredondadas, e o centro das pontas a 0 na tampa
  near(t.d(0, 0, 0), 0, 1e-12, 'tampa do pulso');
  near(t.d(-10, 0, 0), 0, 1e-12, 'tampa do cotovelo');
  assert.ok(t.d(0.2, 0, 0) > 0 && t.d(-5, 0, 0) < 0, 'fora da tampa, dentro no meio');
});

test('tronco: o campo é 1-Lipschitz (a poda e os intervalos do SdfMesher valem)', () => {
  const rng = new RNG('tronco-lipschitz');
  const t = lerTronco(ANTEBRACO, 'raiz');
  assert.ok(t.lipschitz > 1 && t.lipschitz < 1.2, `fator ${t.lipschitz}`);
  for (let i = 0; i < 20000; i++) {
    const p = [rng.float(-12, 2), rng.float(-3, 3), rng.float(-3, 3)];
    const dir = rng.onUnitSphere();
    const s = rng.float(1e-4, 0.3);
    const q = [p[0] + dir.x * s, p[1] + dir.y * s, p[2] + dir.z * s];
    assert.ok(Math.abs(t.d(...p) - t.d(...q)) <= s * (1 + 1e-9), `inclinação acima de 1 em (${p.map((v) => v.toFixed(3))})`);
  }
});

test('tronco: a caixa envolvente contém a massa, o intervalo é garantido e a malha sai fechada', () => {
  const rng = new RNG('tronco-caixa-envolvente');
  const q = createRange();
  const b = bounds(ANTEBRACO);
  assert.ok(!isEmptyBounds(b));
  const ext = b.max.map((v, i) => v - b.min[i]);
  let massa = 0;
  for (let i = 0; i < 6000; i++) {
    const p = [0, 1, 2].map((a) => b.min[a] - ext[a] * 0.5 + rng.next() * ext[a] * 2);
    if (evaluate(ANTEBRACO, ...p) > 0) continue;
    massa++;
    for (let a = 0; a < 3; a++) assert.ok(p[a] >= b.min[a] - 1e-9 && p[a] <= b.max[a] + 1e-9, 'massa fora da caixa');
  }
  assert.ok(massa > 100, 'amostrou a massa');
  const sdf = compile(ANTEBRACO);
  const plain = compile(ANTEBRACO, { cull: false });
  for (let i = 0; i < 400; i++) {
    const c = [0, 1, 2].map((a) => b.min[a] - 2 + rng.next() * (ext[a] + 4));
    const R = rng.float(0.05, 3);
    sdf.range(...c, R, q);
    for (let j = 0; j < 8; j++) {
      const dir = rng.onUnitSphere();
      const s = R * Math.cbrt(rng.next());
      const p = [c[0] + dir.x * s, c[1] + dir.y * s, c[2] + dir.z * s];
      const d = sdf.distance(...p);
      assert.ok(d >= q.lo - 1e-9 && d <= q.hi + 1e-9, 'fora do intervalo');
      assert.equal(d, plain.distance(...p), 'a poda mudou a distância');
    }
  }
  const mesh = polygonize(compile(ANTEBRACO), bounds(ANTEBRACO), { resolution: 64, maxCells: 400000 });
  const r = meshReport(mesh);
  assert.ok(mesh.indices.length > 600, 'gerou triângulos');
  assert.equal(r.open, 0, 'arestas abertas');
  assert.equal(r.badWinding, 0, 'triângulos virados');
  assert.equal(r.chi, 2, 'uma peça só, sem furo');
});

test('tronco inválido explica o problema', () => {
  const bad = [
    [{ type: 'tronco', secoes: [[0, 1, 1, 0.2]] }, /2 a 256 seções/],
    [{ type: 'tronco', secoes: [[0, 1, 1, 0.2], [1, 1, 1]] }, /\[x, largura, espessura, raio\]/],
    [{ type: 'tronco', secoes: [[0, 1, 1, 0.2], [0, 1, 1, 0.2]] }, /depois da anterior em x/],
    [{ type: 'tronco', secoes: [[0, 1, 1, 0.2], [1, 0, 1, 0]] }, /largura e espessura positivas/],
    [{ type: 'tronco', secoes: [[0, 1, 1, 0.6], [1, 1, 1, 0.2]] }, /raio fora/],
    [{ type: 'tronco', round: 0.8, secoes: [[0, 1, 1, 0.2], [4, 1, 1, 0.2]] }, /'round'/],
    [{ type: 'tronco', secoes: [[0, 1, Infinity, 0.2], [1, 1, 1, 0.2]] }, /não finito/],
  ];
  for (const [tree, re] of bad) assert.throws(() => compile(tree), re, JSON.stringify(tree));
});
```

```js file=tests/antebracoMassa.test.js
// O antebraço de massinha das luvas (Fase 4.1b; plano, Tarefa 9, Passo 4): a seção igual à do Blender (a medida da
// boca do punho do relatório das luvas), a árvore SDF do pulso ao depois do cotovelo, o antebraço cabendo no punho da
// luva de verdade com folga (a malha de repouso do luvas.glb, com a irregularidade da massa), a rampa da torção entre os
// dois ossos, a braçadeira em volta do antebraço, e as malhas pelo SdfMesher com os pesos.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import { evaluate } from '../src/clay/sdf/nodes.js';
import { lerTronco } from '../src/clay/sdf/tronco.js';
import { BRACO_DE_MASSA, LUVAS } from '../src/data/luvas.js';
import { perimetroRetanguloArredondado, validarFichaLuvas } from '../src/characters/hands/fichaLuvas.js';
import {
  arvoreDaBracadeira, arvoreDoAntebraco, circunferenciaDoAntebraco, comprimentoDoAntebraco, construirAntebraco,
  extensaoDoAntebraco, pesosDoAntebraco, secaoDoAntebraco,
} from '../src/characters/hands/antebracoMassa.js';
import { lerGlb } from '../tools/blender/saida.mjs';
import { RAIZ, decodificadorDraco, modeloDoGlb, sdfDeTeste } from './luvasTestUtils.js';

const MM = 25.4;
const FICHA = validarFichaLuvas(JSON.parse(readFileSync(join(RAIZ, 'tools/blender/refs/luvas.json'), 'utf8')));
const RELATORIO = JSON.parse(readFileSync(join(RAIZ, LUVAS.pasta, 'luvas.relatorio.json'), 'utf8'));

test('antebraço: a seção é a do Blender (o punho da luva foi vestido nela)', () => {
  const L = comprimentoDoAntebraco(FICHA);
  assert.ok(Math.abs(L - 290 * 189.3 / 194.5) < 1e-9, `comprimento ${L}`);
  // o relatório das luvas mede a boca do punho: a circunferência do antebraço ali mais a volta do tecido e da folga
  const punho = FICHA.luva.punho;
  const xBoca = -punho + 0.6;
  const folga = FICHA.luva.folgaPunho * (-xBoca / punho);
  const alvo = circunferenciaDoAntebraco(FICHA, xBoca) + 2 * Math.PI * (FICHA.luva.tecido + folga);
  assert.ok(Math.abs(alvo - RELATORIO.medidas.boca.alvo) < 0.01, `boca ${alvo} × ${RELATORIO.medidas.boca.alvo}`);
  // no pulso, a circunferência da ficha; no cotovelo e depois dele, a do perfil
  const perimetro = (s) => perimetroRetanguloArredondado(s.largura, s.espessura, s.raio);
  assert.ok(Math.abs(perimetro(secaoDoAntebraco(FICHA, 0)) - FICHA.mao.pulso.mm) < 1e-9);
  assert.ok(Math.abs(perimetro(secaoDoAntebraco(FICHA, -L)) - FICHA.deducoes.perfilDoAntebraco.circunferenciaNoCotovelo) < 1e-9);
  assert.deepEqual(secaoDoAntebraco(FICHA, -L - 60), secaoDoAntebraco(FICHA, -L));
  // o retângulo arredondado do pulso da ficha (61,9 × 38, canto 18) na escala da circunferência exata
  const s0 = secaoDoAntebraco(FICHA, 0);
  const largura = 65.8 * 85 / 90.4;
  assert.ok(Math.abs(s0.largura / s0.espessura - largura / 38) < 1e-12 && Math.abs(s0.raio / s0.espessura - 18 / 38) < 1e-12, 'as proporções do pulso');
  assert.ok(Math.abs(s0.espessura - 38) < 0.1, `espessura ${s0.espessura}`);
});

test('antebraço: a árvore vai de dentro do punho até depois do cotovelo, na seção de cada ponto', () => {
  const tree = arvoreDoAntebraco(FICHA);
  assert.equal(tree.type, 'displace');
  assert.equal(tree.amp, BRACO_DE_MASSA.irregularidade.ampMM / MM);
  const t = lerTronco(tree.child, 'raiz');
  const { pulso, cotovelo } = extensaoDoAntebraco(FICHA);
  assert.ok(Math.abs(t.x1 * MM - pulso) < 1e-9 && Math.abs(t.x0 * MM - cotovelo) < 1e-9);
  assert.equal(t.secoes.length, BRACO_DE_MASSA.secoes + 1);
  for (const x of [-60, -100, -150, -200, -250]) {
    const s = secaoDoAntebraco(FICHA, x);
    // entre as seções a curva t^1,3 vira reta: a diferença fica bem abaixo da irregularidade da massa
    assert.ok(Math.abs(t.d(x / MM, 0, s.largura / 2 / MM) * MM) < 0.05, `largura em ${x}`);
    assert.ok(Math.abs(t.d(x / MM, s.espessura / 2 / MM, 0) * MM) < 0.05, `espessura em ${x}`);
  }
});

test('antebraço: cabe no punho da luva de verdade, com folga, nos dois braços', async () => {
  const { json, bin } = lerGlb(readFileSync(join(RAIZ, LUVAS.pasta, 'luvas.glb')));
  const draco = await decodificadorDraco();
  const tree = arvoreDoAntebraco(FICHA);
  for (const lado of ['d', 'e']) {
    const p = modeloDoGlb(draco, json, bin, `luva_${lado}`).malha.repouso;
    let pior = Infinity;
    let conta = 0;
    for (let v = 0; v < p.length / 3; v++) {
      const x = p[v * 3];
      if (x > -BRACO_DE_MASSA.dentroDoPunhoMM || x < -FICHA.luva.punho) continue;
      conta++;
      pior = Math.min(pior, evaluate(tree, x / MM, p[v * 3 + 1] / MM, p[v * 3 + 2] / MM) * MM);
    }
    assert.ok(conta > 100, `${lado}: vértices do punho`);
    // o forro do punho fica a 1,6 mm do antebraço na ponta de dentro; com a massa irregular, pelo menos 1 mm
    assert.ok(pior >= 1, `${lado}: a luva a ${pior.toFixed(2)} mm do antebraço de massinha`);
  }
});

test('antebraço: a torção passa em rampa do antebraco (cotovelo) à torcao (boca do punho)', () => {
  const L = comprimentoDoAntebraco(FICHA);
  const xs = [-L - 60, -L, -L * 0.75, -L / 2, -100, -FICHA.luva.punho, -30, -20];
  const pos = new Float32Array(xs.flatMap((x) => [x / MM, 0.3, -0.2]));
  const { skinIndex, skinWeight } = pesosDoAntebraco(pos, FICHA);
  const torcao = xs.map((_, i) => skinWeight[i * 4 + 1]);
  for (let i = 0; i < xs.length; i++) {
    assert.deepEqual([...skinIndex.slice(i * 4, i * 4 + 4)], [0, 1, 0, 0]);
    assert.ok(Math.abs(skinWeight[i * 4] + skinWeight[i * 4 + 1] - 1) < 1e-6);
    if (i) assert.ok(torcao[i] >= torcao[i - 1], 'sobe do cotovelo ao pulso');
  }
  assert.equal(torcao[0], 0);
  assert.equal(torcao[1], 0);
  assert.ok(Math.abs(torcao[3] - (L / 2) / (L - FICHA.luva.punho)) < 1e-6);
  assert.deepEqual(torcao.slice(5), [1, 1, 1], 'o pedaço dentro do punho é todo da torcao, como o punho da luva');
});

test('braçadeira: um anel de massa por fora do antebraço, depois da boca do punho', () => {
  const b = BRACO_DE_MASSA.bracadeira;
  const tree = arvoreDaBracadeira(FICHA);
  const x = -b.doPulsoMM;
  const s = secaoDoAntebraco(FICHA, x);
  const d = (xx, y, z) => evaluate(tree, xx / MM, y / MM, z / MM) * MM;
  assert.ok(d(x, 0, s.largura / 2 + b.espessuraMM / 2) < 0, 'massa em volta da largura');
  assert.ok(d(x, s.espessura / 2 + b.espessuraMM / 2, 0) < 0, 'massa em volta da espessura');
  assert.ok(d(x, 0, s.largura / 2 + b.espessuraMM + 1) > 0, 'por fora do anel');
  assert.ok(d(x, 0, s.largura / 2 - 3) > 0, 'dentro do antebraço não tem massa da faixa');
  assert.ok(d(x, 0, 0) > 0, 'o miolo é oco');
  assert.ok(d(x - b.larguraMM / 2 - 3, 0, s.largura / 2 + 1) > 0 && d(x + b.larguraMM / 2 + 3, 0, s.largura / 2 + 1) > 0, 'a largura da faixa');
  assert.ok(x + b.larguraMM / 2 < -FICHA.luva.punho, 'depois da boca do punho');
});

test('antebraço: as malhas saem do SdfMesher com os pesos, marcadas como divididas', async () => {
  const sdf = sdfDeTeste();
  const { antebraco, bracadeira } = await construirAntebraco(sdf, FICHA);
  assert.equal(sdf.pedidos.length, 2);
  const [a, b] = sdf.pedidos;
  const { pulso, cotovelo } = extensaoDoAntebraco(FICHA);
  assert.equal(a.opts.resolution, Math.ceil((pulso - cotovelo) / MM / BRACO_DE_MASSA.malha.celulaU));
  assert.equal(b.opts.maxCells, BRACO_DE_MASSA.bracadeira.malha.maxCells);
  for (const g of [antebraco, bracadeira]) {
    assert.equal(g.userData.shared, true);
    assert.equal(g.attributes.skinIndex.count, g.attributes.position.count);
    assert.equal(g.attributes.skinWeight.itemSize, 4);
  }
  assert.equal(antebraco.name, 'antebraco-de-massinha');
  assert.equal(bracadeira.name, 'bracadeira-de-massinha');
});
```

```js file=tests/bracoLuva.test.js
// Um braço de luva (Fase 4.1b; plano, Tarefa 9, Passo 2), sem GPU, montado do luvas.glb de verdade pelo GLTFLoader do
// vendor e com a pega do clipe `empunhadura` do .glb da AK: os dedos no quaternion do clipe e a marca do rig conferida;
// `colocar` com o osso `mao` no pulso e na orientação pedidas, o antebraço do cotovelo ao pulso no comprimento da
// ficha, a torção meio a meio entre a `torcao` e a `mao` (±0,5°), os ângulos do pulso e os avisos dos limites da AAOS;
// em repouso a luva fica onde o Blender a exportou; o antebraço de massinha vai junto com a `torcao` no punho; a facção
// troca os materiais; a braçadeira aparece com a cor do time.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import * as THREE from 'three';
import { LUVAS, OSSOS_DE_DEDO, ZONAS_DAS_LUVAS } from '../src/data/luvas.js';
import { comprimentoDoAntebraco, construirAntebraco } from '../src/characters/hands/antebracoMassa.js';
import { BracoLuva, avisosDoPulso, torcaoDoPulso } from '../src/characters/hands/bracoLuva.js';
import { validarFichaLuvas } from '../src/characters/hands/fichaLuvas.js';
import { moldeDoBraco } from '../src/characters/hands/moldeLuva.js';
import { dedosDoClipe, lerPega } from '../src/characters/hands/pega.js';
import { RNG } from '../src/core/rng.js';
import { RAIZ, carregarGlbNoNode, decodificadorDraco, sdfDeTeste } from './luvasTestUtils.js';

const MM = 25.4;
const X = new THREE.Vector3(1, 0, 0);
const FICHA = validarFichaLuvas(JSON.parse(readFileSync(join(RAIZ, 'tools/blender/refs/luvas.json'), 'utf8')));

let base = null;
async function montagem() {
  if (!base) {
    base = (async () => {
      const draco = await decodificadorDraco();
      const luvas = await carregarGlbNoNode(join(RAIZ, LUVAS.pasta, 'luvas.glb'), draco);
      const ak = await carregarGlbNoNode(join(RAIZ, 'assets/armas/ak47/ak47.glb'), draco);
      const moldes = { d: moldeDoBraco(luvas.scene, 'd', ZONAS_DAS_LUVAS), e: moldeDoBraco(luvas.scene, 'e', ZONAS_DAS_LUVAS) };
      const antebraco = await construirAntebraco(sdfDeTeste(40), FICHA);
      const clipe = ak.animations.find((a) => a.name === 'empunhadura');
      const lida = lerPega(ak.parser.json);
      return { moldes, antebraco, pega: { marca: lida.marca, dedos: dedosDoClipe(clipe) } };
    })();
  }
  return base;
}

const materiaisFalsos = (nome) => Object.fromEntries(ZONAS_DAS_LUVAS.map((z) => [z, new THREE.MeshBasicMaterial({ name: `${nome}:${z}` })]));

async function braco(lado, extra = {}) {
  const m = await montagem();
  return new BracoLuva({
    molde: m.moldes[lado], faccao: 'massaCrua', materiais: materiaisFalsos('massaCrua'),
    materiaisDe: async (f) => materiaisFalsos(f), antebraco: m.antebraco, corDaMassa: '#C8553D', limites: FICHA.limites, ...extra,
  });
}

/** O giro (radianos) em volta de +X contido num quaternion (a torção do swing-twist). */
function torcaoEmX(q) {
  const s = q.w < 0 ? -1 : 1;
  return 2 * Math.atan2(s * q.x, s * q.w);
}

/** O ângulo (radianos) entre dois giros (os quaternions normalizados: o arquivo é float32). */
function angulo(a, b) {
  return 2 * Math.acos(Math.min(1, Math.abs(a.clone().normalize().dot(b.clone().normalize()))));
}

/** A rotação do osso no referencial do braço (o grupo). */
function noBraco(b, osso) {
  b.grupo.updateMatrixWorld(true);
  const g = b.grupo.getWorldQuaternion(new THREE.Quaternion()).invert();
  return g.multiply(b.ossos[osso].getWorldQuaternion(new THREE.Quaternion()));
}

const graus = (r) => (r * 180) / Math.PI;

test('braço: a pega põe cada osso de dedo no quaternion do clipe da AK e recusa outra marca', async () => {
  const { pega } = await montagem();
  for (const lado of ['d', 'e']) {
    const b = await braco(lado);
    b.aplicarPega(pega);
    for (const osso of OSSOS_DE_DEDO) {
      const q = new THREE.Quaternion().fromArray(pega.dedos[lado][osso]).normalize();
      assert.ok(angulo(b.ossos[osso].quaternion, q) < 1e-7, `${lado}: ${osso}`);
    }
    assert.equal(b.pega, pega);
    assert.throws(() => b.aplicarPega({ ...pega, marca: { d: 'f'.repeat(64), e: 'f'.repeat(64) } }), /marca do rig .* não é a das luvas/);
    const semPolegar = structuredClone(pega);
    delete semPolegar.dedos[lado].polegar_2;
    assert.throws(() => b.aplicarPega(semPolegar), new RegExp(`polegar_2_${lado}`));
    b.soltarPega();
    assert.equal(b.pega, null);
    b.dispose();
  }
});

test('braço: colocar põe o osso mao no pulso e na orientação pedidas, e o antebraço do cotovelo ao pulso', async () => {
  const rng = new RNG('colocar-luvas');
  const L = comprimentoDoAntebraco(FICHA) / MM;
  const pai = new THREE.Group();
  pai.position.set(3, -2, 5);
  pai.quaternion.setFromEuler(new THREE.Euler(0.3, -0.7, 0.2));
  for (const lado of ['d', 'e']) {
    const b = await braco(lado);
    pai.add(b.grupo);
    for (let i = 0; i < 12; i++) {
      const pulso = new THREE.Vector3(rng.float(-4, 4), rng.float(-4, 4), rng.float(-8, -2));
      const cotovelo = pulso.clone().add(new THREE.Vector3(rng.float(-1, 1), rng.float(-1.5, -0.5), rng.float(0.5, 1.5)).normalize().multiplyScalar(rng.float(4, 12)));
      const maoQuat = new THREE.Quaternion().setFromEuler(new THREE.Euler(rng.float(-3, 3), rng.float(-3, 3), rng.float(-3, 3))).normalize();
      b.colocar(pulso, maoQuat, cotovelo);
      pai.updateMatrixWorld(true);
      const mao = b.ossos.mao;
      const pm = pai.worldToLocal(mao.getWorldPosition(new THREE.Vector3()));
      assert.ok(pm.distanceTo(pulso) * MM < 1e-4, `${lado}: o pulso a ${pm.distanceTo(pulso) * MM} mm`);
      const qm = pai.getWorldQuaternion(new THREE.Quaternion()).invert().multiply(mao.getWorldQuaternion(new THREE.Quaternion()));
      assert.ok(angulo(qm, maoQuat) < 1e-5, `${lado}: a orientação da mão a ${angulo(qm, maoQuat)} rad`);
      const pc = pai.worldToLocal(b.ossos.antebraco.getWorldPosition(new THREE.Vector3()));
      const esperado = pulso.clone().add(cotovelo.clone().sub(pulso).normalize().multiplyScalar(L));
      assert.ok(pc.distanceTo(esperado) * MM < 0.01, `${lado}: o cotovelo a ${(pc.distanceTo(esperado) * MM).toFixed(4)} mm do alinhamento`);
    }
    b.dispose();
  }
});

test('braço: a torção vai meio a meio para a torcao e para a mao, com a pronação no sentido da anatomia', async () => {
  const { moldes } = await montagem();
  const pulso = new THREE.Vector3(0, 0, 0);
  const cotovelo = new THREE.Vector3(-8, -3, 4);
  for (const lado of ['d', 'e']) {
    const b = await braco(lado);
    const m = moldes[lado];
    const repM = m.quatRepouso[m.ossos.indexOf(`mao_${lado}`)];
    const repT = m.quatRepouso[m.ossos.indexOf(`torcao_${lado}`)];
    b.colocar(pulso, new THREE.Quaternion(), cotovelo);
    const Q = b.grupo.quaternion.clone();
    for (const tau of [-150, -80, -35, 0, 20, 60, 120]) {
      // a mão girada τ em volta do antebraço (+X do braço) e com um balanço de pulso por cima
      const delta = new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0, 0.6, 0.8), 0.3)
        .multiply(new THREE.Quaternion().setFromAxisAngle(X, (tau * Math.PI) / 180));
      const { angulos } = b.colocar(pulso, Q.clone().multiply(delta).multiply(repM), cotovelo);
      const rt = noBraco(b, 'torcao').multiply(repT.clone().invert());
      const rm = noBraco(b, 'mao').multiply(repM.clone().invert());
      const rolT = graus(torcaoEmX(rt));
      const rolM = graus(torcaoEmX(rt.clone().invert().multiply(rm)));
      const total = graus(torcaoEmX(rm));
      assert.ok(Math.abs(rolT - total / 2) < 0.5 && Math.abs(rolM - total / 2) < 0.5, `${lado}, τ ${tau}: torcao ${rolT.toFixed(2)}°, mao ${rolM.toFixed(2)}° de ${total.toFixed(2)}°`);
      assert.ok(Math.abs(total - tau) < 1e-4, `${lado}: a torção total ${total}`);
      // pronação: a palma para baixo com o polegar para cima de partida — na direita é o giro negativo em +X
      assert.ok(Math.abs(angulos.pronacao - (lado === 'd' ? -tau : tau)) < 1e-4, `${lado}: pronação ${angulos.pronacao} para τ ${tau}`);
    }
    b.dispose();
  }
});

test('braço: os ângulos do pulso e os avisos dos limites da AAOS da ficha', async () => {
  const { moldes } = await montagem();
  const pulso = new THREE.Vector3(0, 0, 0);
  const cotovelo = new THREE.Vector3(-10, 0, 0);
  for (const lado of ['d', 'e']) {
    const b = await braco(lado);
    const m = moldes[lado];
    const repM = m.quatRepouso[m.ossos.indexOf(`mao_${lado}`)];
    const r0 = b.colocar(pulso, new THREE.Quaternion(), cotovelo);
    assert.ok(Array.isArray(r0.avisos));
    const Q = b.grupo.quaternion.clone();
    const pose = (eixo, g) => Q.clone().multiply(new THREE.Quaternion().setFromAxisAngle(eixo, (g * Math.PI) / 180)).multiply(repM);
    const neutro = b.colocar(pulso, pose(X, 0), cotovelo);
    assert.deepEqual(neutro.avisos, []);
    assert.ok(Math.abs(neutro.angulos.flexao) < 1e-4 && Math.abs(neutro.angulos.desvio) < 1e-4 && Math.abs(neutro.angulos.pronacao) < 1e-4);
    // flexão: as pontas para a palma (−Y do braço), em volta de +Z; desvio radial: para o polegar (σ·Z)
    const Z = new THREE.Vector3(0, 0, 1);
    const Y = new THREE.Vector3(0, 1, 0);
    const s = m.polegar;
    const casos = [
      [pose(Z, -60), 'flexao', 60, []],
      [pose(Z, -85), 'flexao', 85, [/pulso: flexão de 85\.0° \(limite 80°\)/]],
      [pose(Z, 75), 'flexao', -75, [/pulso: extensão de 75\.0° \(limite 70°\)/]],
      [pose(Y, -25 * s), 'desvio', 25, [/pulso: desvio radial de 25\.0° \(limite 20°\)/]],
      [pose(Y, 35 * s), 'desvio', -35, [/pulso: desvio ulnar de 35\.0° \(limite 30°\)/]],
      [pose(X, 90 * s), 'pronacao', 90, [/antebraço: pronação de 90\.0° \(limite 80°\)/]],
      [pose(X, -85 * s), 'pronacao', -85, [/antebraço: supinação de 85\.0° \(limite 80°\)/]],
    ];
    for (const [q, campo, valor, avisos] of casos) {
      const r = b.colocar(pulso, q, cotovelo);
      assert.ok(Math.abs(r.angulos[campo] - valor) < 1e-4, `${lado}: ${campo} ${r.angulos[campo]} (esperado ${valor})`);
      assert.equal(r.avisos.length, avisos.length, `${lado}: ${r.avisos.join('; ')}`);
      avisos.forEach((re, i) => assert.match(r.avisos[i], re));
    }
    b.dispose();
  }
  // a conta pura: o pulso flexionado 60° no rádio girado 90° continua flexão (a torção inteira sai antes de medir), e o
  // mesmo giro de 60° em volta do Z fixo depois da supinação é desvio ulnar — a mão já está de lado
  const Zf = new THREE.Vector3(0, 0, 1);
  const t = torcaoDoPulso(new THREE.Quaternion().setFromAxisAngle(X, Math.PI / 2).multiply(new THREE.Quaternion().setFromAxisAngle(Zf, -Math.PI / 3)), -1);
  assert.ok(Math.abs(t.flexao - 60) < 1e-9 && Math.abs(t.desvio) < 1e-9 && Math.abs(t.pronacao + 90) < 1e-9, JSON.stringify(t));
  const u = torcaoDoPulso(new THREE.Quaternion().setFromAxisAngle(Zf, -Math.PI / 3).multiply(new THREE.Quaternion().setFromAxisAngle(X, Math.PI / 2)), -1);
  assert.ok(Math.abs(u.flexao) < 1e-9 && Math.abs(u.desvio + 60) < 1e-9 && Math.abs(u.pronacao + 90) < 1e-9, JSON.stringify(u));
  assert.deepEqual(avisosDoPulso({ flexao: 80, desvio: -30, pronacao: 80 }, FICHA.limites), [], 'nos limites não avisa');
});

test('braço: em repouso a luva fica onde o Blender a exportou, e sem giro nenhum osso mexe', async () => {
  const { moldes } = await montagem();
  for (const lado of ['d', 'e']) {
    const b = await braco(lado);
    const m = moldes[lado];
    const repM = m.quatRepouso[m.ossos.indexOf(`mao_${lado}`)];
    b.colocar(new THREE.Vector3(1, 2, 3), new THREE.Quaternion(), new THREE.Vector3(-5, 2, 3));
    b.colocar(new THREE.Vector3(1, 2, 3), b.grupo.quaternion.clone().multiply(repM), new THREE.Vector3(-5, 2, 3));
    let pior = 0;
    for (const malha of b.malhas) {
      const zona = malha.geometry.name.split(':')[1];
      const original = m.primitivas.find((p) => p.zona === zona).geometria.attributes.position.array;
      const agora = malha.geometry.attributes.position.array;
      for (let i = 0; i < agora.length; i++) pior = Math.max(pior, Math.abs(agora[i] - original[i]) * MM);
      assert.ok(malha.geometry.attributes.repouso, 'o padrão lê a posição de repouso');
    }
    assert.ok(pior < 0.02, `${lado}: a luva a ${pior.toFixed(4)} mm do repouso`);
    b.dispose();
  }
});

test('braço: com a pega da AK a luva dobra e as normais acompanham', async () => {
  const { pega } = await montagem();
  const b = await braco('d');
  const antes = b.malhas.map((mm) => mm.geometry.attributes.position.array.slice());
  const normais = b.malhas.map((mm) => mm.geometry.attributes.normal.array.slice());
  b.aplicarPega(pega);
  let andou = 0;
  let viradas = 0;
  let total = 0;
  b.malhas.forEach((mm, k) => {
    const p = mm.geometry.attributes.position.array;
    const n = mm.geometry.attributes.normal.array;
    for (let i = 0; i < p.length; i++) andou = Math.max(andou, Math.abs(p[i] - antes[k][i]) * MM);
    for (let i = 0; i < n.length; i += 3) {
      total++;
      if (Math.abs(Math.hypot(n[i], n[i + 1], n[i + 2]) - 1) > 1e-3) viradas++;
    }
    assert.ok(normais[k].some((v, i) => Math.abs(v - n[i]) > 1e-3), 'as normais giram com a malha');
  });
  assert.ok(andou > 20, `as pontas dos dedos andaram ${andou.toFixed(1)} mm`);
  assert.equal(viradas, 0, `${viradas} de ${total} normais fora do comprimento 1`);
  assert.equal(b.atualizar(), false, 'sem mudança, não recalcula');
  b.dispose();
});

test('braço: o antebraço de massinha no punho vai junto com a torcao', async () => {
  const b = await braco('e');
  const { moldes } = await montagem();
  const m = moldes.e;
  const repM = m.quatRepouso[m.ossos.indexOf('mao_e')];
  b.colocar(new THREE.Vector3(), new THREE.Quaternion(), new THREE.Vector3(-9, 0, 0));
  b.colocar(new THREE.Vector3(), b.grupo.quaternion.clone().multiply(new THREE.Quaternion().setFromAxisAngle(X, 1.2)).multiply(repM), new THREE.Vector3(-9, 0, 0));
  b.grupo.updateMatrixWorld(true);
  b.skeleton.update();
  const g = b.antebraco.geometry;
  const pos = g.attributes.position;
  const torcao = b.ossos.torcao;
  const it = m.ossos.indexOf('torcao_e');
  const Mt = b.grupo.matrixWorld.clone().invert().multiply(torcao.matrixWorld).multiply(m.relRepousoInv[it]);
  let conta = 0;
  for (let i = 0; i < pos.count; i++) {
    if (g.attributes.skinWeight.getY(i) < 1) continue;
    const v = new THREE.Vector3().fromBufferAttribute(pos, i);
    const esperado = v.clone().applyMatrix4(Mt);
    const pele = b.antebraco.applyBoneTransform(i, v.clone());
    assert.ok(pele.distanceTo(esperado) * MM < 1e-3, 'o pedaço do punho é todo da torcao');
    conta++;
  }
  assert.ok(conta > 20, 'amostrou o pedaço do punho');
  b.dispose();
});

test('braço: a facção troca os materiais da luva; a braçadeira aparece com a cor do time; o descarte', async () => {
  const b = await braco('d');
  const antes = b.malhas.map((mm) => mm.material);
  assert.deepEqual(antes.map((x) => x.name).sort(), ZONAS_DAS_LUVAS.map((z) => `massaCrua:${z}`).sort());
  const p1 = b.setFaccao('massaCrua');
  const p2 = b.setFaccao('tropa');
  assert.equal(await p1, false, 'o pedido velho não troca');
  assert.equal(await p2, true);
  assert.equal(b.faccao, 'tropa');
  for (const mm of b.malhas) assert.equal(mm.material.name, `tropa:${mm.geometry.name.split(':')[1]}`);
  assert.equal(b.bracadeira.visible, false);
  b.setBracadeira('#2F6DB5');
  assert.equal(b.bracadeira.visible, true);
  assert.equal(b.materialBracadeira.color.getHexString(), '2f6db5');
  b.setBracadeira(null);
  assert.equal(b.bracadeira.visible, false);
  assert.equal(b.materialMassa.clay.boil, 0, 'sem boil');
  const pai = new THREE.Group();
  pai.add(b.grupo);
  const descartadas = [];
  for (const mm of b.malhas) mm.geometry.addEventListener('dispose', () => descartadas.push(mm.geometry.name));
  const antebraco = b.antebraco.geometry;
  let dividida = false;
  antebraco.addEventListener('dispose', () => {
    dividida = true;
  });
  b.dispose();
  assert.equal(b.grupo.parent, null);
  assert.equal(descartadas.length, ZONAS_DAS_LUVAS.length);
  assert.equal(dividida, false, 'a malha de massinha é da fonte, dividida entre os braços');
});
```

```js file=tests/luvasSource.test.js
// O serviço das luvas (Fase 4.1b; plano, Tarefa 9, Passo 1), com carregadores falsos como os da weaponLibraryGlb.test.js
// — o .glb é o de verdade, lido pelo GLTFLoader do vendor (o Draco sem Workers), as texturas vazias, o relatório e a
// ficha do disco, e o SdfMesher pelo marching cubes numa grade grossa: uma carga só para pedidos ao mesmo tempo; os
// materiais por (facção, zona) em cache e marcados como divididos; cada braço com o esqueleto e as malhas da luva
// dele; o ambiente em todos os materiais; o descarte de tudo e a recusa depois; o erro de carga no log com o arquivo.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import * as THREE from 'three';
import { FACCOES_DAS_LUVAS, LUVAS, ZONAS_DAS_LUVAS } from '../src/data/luvas.js';
import { LuvasSource } from '../src/characters/hands/luvasSource.js';
import { RAIZ, carregarGlbNoNode, decodificadorDraco, sdfDeTeste } from './luvasTestUtils.js';

const RELATORIO = JSON.parse(readFileSync(join(RAIZ, LUVAS.pasta, 'luvas.relatorio.json'), 'utf8'));
const FICHA = JSON.parse(readFileSync(join(RAIZ, 'tools/blender/refs/luvas.json'), 'utf8'));
let draco = null;

function logFalso() {
  const linhas = { debug: [], warn: [], error: [] };
  return { linhas, debug: (m) => linhas.debug.push(m), warn: (m) => linhas.warn.push(m), error: (m) => linhas.error.push(m) };
}

async function nova({ falhaGlb = null } = {}) {
  draco ??= await decodificadorDraco();
  const conta = { glb: 0, textura: 0, json: 0, urls: [], texturas: [] };
  const sdf = sdfDeTeste(32);
  const log = logFalso();
  const carregadores = {
    async glb(url) {
      conta.glb++;
      conta.urls.push(url);
      if (falhaGlb) throw new Error(falhaGlb);
      return carregarGlbNoNode(join(RAIZ, LUVAS.pasta, 'luvas.glb'), draco);
    },
    async textura(url) {
      conta.textura++;
      conta.urls.push(url);
      const t = new THREE.Texture();
      t.name = url;
      conta.texturas.push(t);
      return t;
    },
    async json(url) {
      conta.json++;
      conta.urls.push(url);
      if (url.endsWith('luvas.relatorio.json')) return structuredClone(RELATORIO);
      if (url.endsWith('refs/luvas.json')) return structuredClone(FICHA);
      throw new Error(`sem ${url}`);
    },
    descartar() {
      conta.descartou = true;
    },
  };
  return { fonte: new LuvasSource({ carregadores, sdf, log }), conta, sdf, log };
}

test('luvas: uma carga só para pedidos ao mesmo tempo (o .glb, o relatório, a ficha, as texturas e a massa)', async () => {
  const { fonte, conta, sdf } = await nova();
  const [a, b, d, e] = await Promise.all([fonte.carregar(), fonte.carregar(), fonte.instanciar('d', 'tropa', { corDaMassa: '#C8553D' }),
    fonte.instanciar('e', 'massaCrua', { corDaMassa: '#C8553D' })]);
  assert.equal(a, b);
  assert.equal(conta.glb, 1);
  assert.equal(conta.json, 2);
  assert.equal(conta.textura, 2, 'as texturas _n e _m uma vez para as duas facções');
  assert.ok(conta.urls.some((u) => u.endsWith('assets/maos/luvas_n.webp')) && conta.urls.some((u) => u.endsWith('assets/maos/luvas_m.webp')));
  assert.equal(sdf.pedidos.length, 2, 'o antebraço e a braçadeira gerados uma vez');
  assert.equal(d.lado, 'd');
  assert.equal(e.lado, 'e');
  const r = fonte.relatorio();
  assert.equal(r.estado, 'pronta');
  assert.deepEqual(r.triangulos, { d: RELATORIO.triangulos.luva, e: RELATORIO.triangulos.luva }, 'os triângulos de cada luva, como o Blender contou');
  assert.deepEqual(r.marca, RELATORIO.marca);
  assert.equal(r.bracos, 2);
  assert.ok(r.antebraco > 0);
  fonte.dispose();
});

test('luvas: materiais por facção e zona, em cache, divididos, com o padrão pela pose de repouso e as duas faces', async () => {
  const { fonte } = await nova();
  const tropa = await fonte.materiais('tropa');
  assert.equal(await fonte.materiais('tropa'), tropa);
  const crua = await fonte.materiais('massaCrua');
  assert.deepEqual(Object.keys(tropa).sort(), [...ZONAS_DAS_LUVAS].sort());
  for (const z of ZONAS_DAS_LUVAS) {
    const m = tropa[z];
    assert.equal(m.userData.shared, true);
    assert.equal(m.side, THREE.DoubleSide);
    assert.equal(m.defines.ARMA_REPOUSO, '');
    assert.equal(m.name, `luvas:tropa:${z}`);
    assert.notEqual(crua[z], m);
    assert.equal(m.userData.acabamento, LUVAS.pinturas.tropa.zonas[z].acabamento);
  }
  assert.ok(crua.couro.color.r > tropa.couro.color.r, 'o coiote mais claro que o preto');
  await assert.rejects(fonte.materiais('azul'), /facção das luvas desconhecida/);
  assert.deepEqual([...FACCOES_DAS_LUVAS].sort(), ['massaCrua', 'tropa']);
  fonte.dispose();
});

test('luvas: cada braço tem o esqueleto e as malhas da luva dele; dividem os materiais e a massa', async () => {
  const { fonte } = await nova();
  const opts = { corDaMassa: '#C8553D' };
  const [a, b, c] = await Promise.all([fonte.instanciar('d', 'tropa', opts), fonte.instanciar('d', 'tropa', opts), fonte.instanciar('e', 'tropa', opts)]);
  assert.notEqual(a.ossos.mao, b.ossos.mao);
  assert.notEqual(a.ossos.indicador_2, b.ossos.indicador_2);
  const geoA = new Set(a.malhas.map((m) => m.geometry));
  for (const m of b.malhas) assert.ok(!geoA.has(m.geometry), 'as malhas da luva são do braço');
  assert.deepEqual(a.malhas.map((m) => m.material), b.malhas.map((m) => m.material));
  assert.equal(a.antebraco.geometry, b.antebraco.geometry);
  assert.notEqual(a.materialMassa, b.materialMassa);
  assert.notEqual(a.marca, c.marca, 'a marca de cada braço');
  assert.equal(a.marca, RELATORIO.marca.d);
  // posar um não mexe no outro
  a.colocar(new THREE.Vector3(), new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(1, 0, 0), 1), new THREE.Vector3(-8, 0, 0));
  assert.notDeepEqual(a.malhas[0].geometry.attributes.position.array.slice(0, 30), b.malhas[0].geometry.attributes.position.array.slice(0, 30));
  await assert.rejects(fonte.instanciar('x', 'tropa', opts), /'d' ou 'e'/);
  fonte.dispose();
});

test('luvas: o ambiente chega a todos os materiais das duas facções', async () => {
  const { fonte } = await nova();
  await fonte.materiais('tropa');
  const ambiente = new THREE.Texture();
  fonte.setAmbiente(ambiente, 0.7);
  await fonte.materiais('massaCrua');
  for (const f of FACCOES_DAS_LUVAS) {
    for (const m of Object.values(await fonte.materiais(f))) {
      assert.equal(m.envMap, ambiente, `${f}: ${m.name}`);
      assert.equal(m.envMapIntensity, 0.7);
    }
  }
  fonte.setAmbiente(null);
  for (const m of Object.values(await fonte.materiais('tropa'))) assert.equal(m.envMap, null);
  fonte.dispose();
});

test('luvas: o descarte leva geometrias, materiais, texturas e braços, e recusa carga depois', async () => {
  const { fonte, conta } = await nova();
  const braco = await fonte.instanciar('d', 'massaCrua', { corDaMassa: '#C8553D' });
  const mats = Object.values(await fonte.materiais('massaCrua'));
  const eventos = [];
  const ouvir = (o, nome) => o.addEventListener('dispose', () => eventos.push(nome));
  for (const m of mats) ouvir(m, m.name);
  for (const t of conta.texturas) ouvir(t, t.name);
  ouvir(braco.antebraco.geometry, 'antebraco');
  ouvir(braco.bracadeira.geometry, 'bracadeira');
  for (const m of braco.malhas) ouvir(m.geometry, m.geometry.name);
  const pai = new THREE.Group();
  pai.add(braco.grupo);
  fonte.dispose();
  for (const m of mats) assert.ok(eventos.includes(m.name), m.name);
  for (const t of conta.texturas) assert.ok(eventos.includes(t.name), t.name);
  assert.ok(eventos.includes('antebraco') && eventos.includes('bracadeira'));
  assert.ok(braco.malhas.length === 0 || eventos.filter((x) => x.startsWith('luva_d')).length === ZONAS_DAS_LUVAS.length);
  assert.equal(braco.grupo.parent, null, 'o braço saiu da cena');
  assert.equal(conta.descartou, true);
  await assert.rejects(fonte.carregar(), /descartada/);
  await assert.rejects(fonte.instanciar('d', 'tropa', { corDaMassa: '#C8553D' }), /descartada/);
});

test('luvas: o erro de carga chega ao log com o arquivo, e a próxima carga tenta de novo', async () => {
  const { fonte, conta, log } = await nova({ falhaGlb: 'HTTP 404' });
  await assert.rejects(fonte.carregar(), /luvas\.glb: HTTP 404/);
  assert.equal(log.linhas.error.length, 1);
  assert.match(log.linhas.error[0], /luvas: não carregaram — luvas\.glb: HTTP 404/);
  assert.equal(fonte.relatorio().estado, 'erro');
  await assert.rejects(fonte.carregar(), /HTTP 404/);
  assert.equal(conta.glb, 2, 'tentou de novo');
  fonte.dispose();
});
```

Run: `node --test tests/sdfTronco.test.js tests/antebracoMassa.test.js tests/bracoLuva.test.js tests/luvasSource.test.js`
Expected: FAIL — # tests 4 # pass 0 # fail 4 .

- [ ] **A implementação** — `src/clay/sdf/tronco.js`, `src/characters/hands/antebracoMassa.js`, `src/characters/hands/moldeLuva.js`, `src/characters/hands/bracoLuva.js`, `src/characters/hands/luvasSource.js`, `src/clay/sdf/params.js`, `src/clay/sdf/bounds.js`, `src/clay/sdf/shapes.js`, `src/main.js`:

```js file=src/clay/sdf/tronco.js
// Forma `tronco` das árvores SDF (Fase 4.1b; desenho em docs/superpowers/specs/2026-09-26-4.1b-luvas-e-empunhadura-
// design.md, seção 5): um tronco ao longo do eixo X local cuja seção é um retângulo arredondado que muda de tamanho de
// uma seção para a outra — o antebraço de massinha que entra no punho da luva (achatado no pulso na largura da ficha,
// mais largo e mais redondo no cotovelo) e a braçadeira em volta dele. Cada seção é [x, largura (ao longo de Z),
// espessura (ao longo de Y), raio do canto]; entre duas seções os quatro números variam em linha reta, e fora das
// pontas vale a seção da ponta. As pontas são arredondadas com `round`, como o perfil extrudado (opExtrusion
// arredondado de iq). A distância ao retângulo arredondado é a exata de iq (sdRoundBox 2D); como a seção muda com x, a
// distância é dividida pelo pior fator de Lipschitz dos trechos (√(1 + g²), g = a soma das inclinações das meias
// medidas e do raio), e a forma continua 1-Lipschitz para a poda e os intervalos do SdfMesher — a superfície (o zero) é
// a mesma.
// Puro: a leitura valida o nó e devolve a distância no espaço local; shapes.js aplica a transformação e o material, e
// bounds.js usa o suporte.

import { MAX_POINTS, MIN_EDGE, fail, readNonNegative } from './params.js';

/**
 * Lê e valida um nó `tronco`.
 * @returns {{secoes:number[][], x0:number, x1:number, rd:number, lipschitz:number, alcance:number,
 *   d:(x:number, y:number, z:number)=>number}} `d` = a distância no espaço local (já 1-Lipschitz); `alcance` = a maior
 *   meia diagonal das seções
 */
export function lerTronco(node, path) {
  const v = node.secoes;
  if (!Array.isArray(v) || v.length < 2 || v.length > MAX_POINTS) fail(path, `'secoes' precisa ser uma lista de 2 a ${MAX_POINTS} seções`);
  const secoes = v.map((s, i) => {
    if (!Array.isArray(s) || s.length !== 4) fail(path, `'secoes[${i}]' precisa ser [x, largura, espessura, raio]`);
    const q = s.map(Number);
    if (!q.every(Number.isFinite)) fail(path, `'secoes[${i}]' tem número não finito (${JSON.stringify(s)})`);
    const [, l, e, r] = q;
    if (!(l > 0 && e > 0)) fail(path, `'secoes[${i}]' precisa de largura e espessura positivas`);
    if (!(r >= 0 && r <= Math.min(l, e) / 2)) fail(path, `'secoes[${i}]' tem o raio fora de 0 a metade do menor lado`);
    if (i > 0 && q[0] - v[i - 1][0] < MIN_EDGE) fail(path, `'secoes[${i}]' precisa vir depois da anterior em x`);
    return q;
  });
  const x0 = secoes[0][0];
  const x1 = secoes[secoes.length - 1][0];
  let menor = Infinity;
  let alcance = 0;
  let g = 0;
  for (let i = 0; i < secoes.length; i++) {
    const [x, l, e, r] = secoes[i];
    menor = Math.min(menor, l / 2, e / 2);
    alcance = Math.max(alcance, Math.hypot(l / 2, e / 2));
    if (i === 0) continue;
    const [xa, la, ea, ra] = secoes[i - 1];
    const dx = x - xa;
    g = Math.max(g, (Math.abs(l - la) / 2 + Math.abs(e - ea) / 2 + Math.abs(r - ra)) / dx);
  }
  const rd = readNonNegative(node, 'round', path, 0);
  if (rd > menor || rd > (x1 - x0) / 2) fail(path, `'round' (${rd}) maior que a meia medida da seção ou que a metade do comprimento`);
  const lipschitz = Math.sqrt(1 + g * g);
  const inv = 1 / lipschitz;
  const n = secoes.length;
  const xs = Float64Array.from(secoes, (s) => s[0]);
  const meiaL = Float64Array.from(secoes, (s) => s[1] / 2);
  const meiaE = Float64Array.from(secoes, (s) => s[2] / 2);
  const raio = Float64Array.from(secoes, (s) => s[3]);
  const xc = (x0 + x1) / 2;
  const eh = (x1 - x0) / 2 - rd;
  const d = (x, y, z) => {
    // a seção em x (a das pontas fora delas), pelo trecho da busca binária
    let a;
    let b;
    let r;
    if (x <= x0) {
      a = meiaL[0];
      b = meiaE[0];
      r = raio[0];
    } else if (x >= x1) {
      a = meiaL[n - 1];
      b = meiaE[n - 1];
      r = raio[n - 1];
    } else {
      let lo = 0;
      let hi = n - 1;
      while (hi - lo > 1) {
        const m = (lo + hi) >> 1;
        if (xs[m] <= x) lo = m;
        else hi = m;
      }
      const t = (x - xs[lo]) / (xs[hi] - xs[lo]);
      a = meiaL[lo] + (meiaL[hi] - meiaL[lo]) * t;
      b = meiaE[lo] + (meiaE[hi] - meiaE[lo]) * t;
      r = raio[lo] + (raio[hi] - raio[lo]) * t;
    }
    // o retângulo arredondado (meias medidas a em Z e b em Y, canto r), encolhido de rd para o arredondamento da ponta
    const qz = Math.abs(z) - a + r;
    const qy = Math.abs(y) - b + r;
    const mz = qz > 0 ? qz : 0;
    const my = qy > 0 ? qy : 0;
    const dentro = qz > qy ? qz : qy;
    const wx = Math.sqrt(mz * mz + my * my) + (dentro < 0 ? dentro : 0) - r + rd;
    const wy = Math.abs(x - xc) - eh;
    const ox = wx > 0 ? wx : 0;
    const oy = wy > 0 ? wy : 0;
    const w = wx > wy ? wx : wy;
    return ((w < 0 ? w : 0) + Math.sqrt(ox * ox + oy * oy) - rd) * inv;
  };
  return { secoes, x0, x1, rd, lipschitz, alcance, d };
}

/** Função suporte da casca convexa das seções (os retângulos sem o arredondamento, que só encolhe): h(u). */
export function suporteDoTronco(node, path) {
  const { secoes } = lerTronco(node, path);
  return (ux, uy, uz) => {
    let m = -Infinity;
    for (const [x, l, e] of secoes) m = Math.max(m, ux * x + Math.abs(uy) * (e / 2) + Math.abs(uz) * (l / 2));
    return m;
  };
}
```

```js file=src/characters/hands/antebracoMassa.js
// O antebraço de massinha das luvas e a braçadeira do time (Fase 4.1b; desenho em docs/superpowers/specs/2026-09-26-
// 4.1b-luvas-e-empunhadura-design.md, seção 5; plano, Tarefa 9, Passo 4): a massa do boneco que entra no punho da luva
// e passa do cotovelo, fora da tela. A seção é a mesma que o Blender usou para vestir o punho (tools/blender/armas/
// maos.py, `secao_antebraco`): o retângulo arredondado do pulso da ficha (largura em Z, espessura em Y — o referencial
// das luvas no glTF: +X pontas, +Y costas) na escala da circunferência, que cresce do pulso ao cotovelo como t^expoente
// (`perfilDoAntebraco`). A árvore SDF (a forma `tronco`, src/clay/sdf/tronco.js, com a irregularidade de massa moldada)
// sai em u no referencial do braço (o pulso na origem, o cotovelo em −X) e vira malha uma vez por sessão no SdfMesher
// (Workers e cache); a seção é simétrica em Z, então uma malha serve aos dois braços. O skin tem dois ossos
// (`antebraco` e `torcao`), na rampa da torção de BRACO_DE_MASSA; a braçadeira é uma faixa de massa em volta do
// antebraço, com os mesmos pesos, que torce junto.
// Puro nas contas (os testes do Node conferem com o relatório das luvas e com a malha delas); construirAntebraco usa o
// SdfMesher.

import * as THREE from 'three';
import { BRACO_DE_MASSA } from '../../data/luvas.js';
import { escalasDaFicha, perimetroRetanguloArredondado } from './fichaLuvas.js';

const MM_POR_U = 25.4;
const B = BRACO_DE_MASSA;

/** Os dois ossos do skin do antebraço (sem o sufixo do lado), na ordem dos índices do skin. */
export const OSSOS_DO_ANTEBRACO = Object.freeze(['antebraco', 'torcao']);

/** Comprimento do antebraço (mm): do cotovelo ao pulso de Greiner, na escala do comprimento da mão da ficha. */
export function comprimentoDoAntebraco(f) {
  return f.juntas.cotoveloAoPulso * escalasDaFicha(f).comprimento;
}

/** Circunferência (mm) do antebraço a x ≤ 0 do pulso (mm): a do pulso crescendo até a do cotovelo como t^expoente. */
export function circunferenciaDoAntebraco(f, x) {
  const perfil = f.deducoes.perfilDoAntebraco;
  const pulso = f.mao.pulso.mm;
  const t = Math.min(1, Math.max(0, -x / comprimentoDoAntebraco(f)));
  return pulso + (perfil.circunferenciaNoCotovelo - pulso) * t ** perfil.expoente;
}

/** Seção (mm) do antebraço a x ≤ 0: o retângulo arredondado do pulso na escala da circunferência. */
export function secaoDoAntebraco(f, x) {
  const largura = f.juntas.pulso.largura * escalasDaFicha(f).largura;
  const { espessura, raio } = f.deducoes.pulso;
  const s = circunferenciaDoAntebraco(f, x) / perimetroRetanguloArredondado(largura, espessura, raio);
  return { largura: largura * s, espessura: espessura * s, raio: raio * s };
}

/** As seções [x, largura, espessura, raio] em u, com `ganho` mm a mais em cada lado (negativo encolhe). */
function secoesEmU(f, xs, ganho = 0) {
  return xs.map((x) => {
    const s = secaoDoAntebraco(f, x);
    return [x, s.largura + 2 * ganho, s.espessura + 2 * ganho, Math.max(0, s.raio + ganho)].map((v) => v / MM_POR_U);
  });
}

/** Onde o tronco começa e acaba (mm): da ponta dentro do punho até depois do cotovelo. */
export function extensaoDoAntebraco(f) {
  return { pulso: -B.dentroDoPunhoMM, cotovelo: -(comprimentoDoAntebraco(f) + B.alemDoCotoveloMM) };
}

/** A árvore SDF do antebraço (u, referencial do braço): o tronco das seções com a irregularidade de massa. */
export function arvoreDoAntebraco(f) {
  const L = comprimentoDoAntebraco(f);
  const { pulso, cotovelo } = extensaoDoAntebraco(f);
  const n = B.secoes;
  // do cotovelo (t = 1, a seção para de crescer) até a ponta do pulso, e a ponta depois do cotovelo com a do cotovelo
  const xs = [cotovelo];
  for (let k = n - 1; k >= 0; k--) xs.push(pulso + ((-L - pulso) * k) / (n - 1));
  const secoes = secoesEmU(f, xs);
  const menor = Math.min(...secoes.map((s) => Math.min(s[1], s[2]) / 2));
  const I = B.irregularidade;
  return {
    type: 'displace', amp: I.ampMM / MM_POR_U, freq: I.freqPorU, octaves: I.oitavas, seed: 'antebraco-de-massinha',
    child: { type: 'tronco', mat: 0, round: Math.min(menor, 10 / MM_POR_U), secoes },
  };
}

/** A árvore SDF da braçadeira: a faixa por fora do antebraço menos o antebraço encolhido (um anel, sem massa dentro). */
export function arvoreDaBracadeira(f) {
  const b = B.bracadeira;
  const x0 = -(b.doPulsoMM + b.larguraMM / 2);
  const x1 = -(b.doPulsoMM - b.larguraMM / 2);
  const fora = Array.from({ length: 5 }, (_, k) => x0 + ((x1 - x0) * k) / 4);
  const dentro = [x0 - 4, (x0 + x1) / 2, x1 + 4];
  const I = b.irregularidade;
  return {
    type: 'displace', amp: I.ampMM / MM_POR_U, freq: I.freqPorU, octaves: I.oitavas, seed: 'bracadeira-de-massinha',
    child: {
      type: 'subtract',
      a: { type: 'tronco', mat: 0, round: b.arredondaMM / MM_POR_U, secoes: secoesEmU(f, fora, b.espessuraMM) },
      b: { type: 'tronco', mat: 0, secoes: secoesEmU(f, dentro, -b.dentroMM) },
    },
  };
}

/**
 * Pesos dos dois ossos por vértice (posições em u, referencial do braço): a `torcao` sobe em rampa linear do cotovelo
 * (0) à boca do punho (1), como o punho da luva, que é todo dela.
 * @returns {{skinIndex:Uint16Array, skinWeight:Float32Array}} 4 por vértice (índices 0 = antebraco, 1 = torcao)
 */
export function pesosDoAntebraco(posicoes, f) {
  const L = comprimentoDoAntebraco(f);
  const boca = f.luva.punho;
  const n = posicoes.length / 3;
  const skinIndex = new Uint16Array(n * 4);
  const skinWeight = new Float32Array(n * 4);
  for (let v = 0; v < n; v++) {
    const x = posicoes[v * 3] * MM_POR_U;
    const w = Math.min(1, Math.max(0, (x + L) / (L - boca)));
    skinIndex[v * 4] = 0;
    skinIndex[v * 4 + 1] = 1;
    skinWeight[v * 4] = 1 - w;
    skinWeight[v * 4 + 1] = w;
  }
  return { skinIndex, skinWeight };
}

function comPesos(g, f, nome) {
  const { skinIndex, skinWeight } = pesosDoAntebraco(g.attributes.position.array, f);
  g.setAttribute('skinIndex', new THREE.Uint16BufferAttribute(skinIndex, 4));
  g.setAttribute('skinWeight', new THREE.Float32BufferAttribute(skinWeight, 4));
  g.name = nome;
  g.userData.shared = true;
  return g;
}

/**
 * As malhas do antebraço e da braçadeira (Workers e cache do SdfMesher), com os pesos. Quem recebe é dono (a
 * LuvasSource divide entre os braços e descarta no fim).
 * @param {import('../../clay/sdf/sdfMesher.js').SdfMesher} sdf
 * @returns {Promise<{antebraco:THREE.BufferGeometry, bracadeira:THREE.BufferGeometry}>}
 */
export async function construirAntebraco(sdf, f) {
  const { pulso, cotovelo } = extensaoDoAntebraco(f);
  const extensao = (pulso - cotovelo) / MM_POR_U;
  const b = B.bracadeira;
  const extBracadeira = Math.max(b.larguraMM, secaoDoAntebraco(f, -b.doPulsoMM).largura + 2 * b.espessuraMM) / MM_POR_U;
  const [antebraco, bracadeira] = await Promise.all([
    sdf.build(arvoreDoAntebraco(f), {
      resolution: Math.min(1024, Math.ceil(extensao / B.malha.celulaU)), maxCells: B.malha.maxCells, touchRadius: B.malha.touchRadius,
    }),
    sdf.build(arvoreDaBracadeira(f), {
      resolution: Math.min(1024, Math.ceil(extBracadeira / b.malha.celulaU)), maxCells: b.malha.maxCells, touchRadius: b.malha.touchRadius,
    }),
  ]);
  return { antebraco: comPesos(antebraco, f, 'antebraco-de-massinha'), bracadeira: comPesos(bracadeira, f, 'bracadeira-de-massinha') };
}
```

```js file=src/characters/hands/moldeLuva.js
// O molde de um braço de luva (Fase 4.1b; desenho em docs/superpowers/specs/2026-09-26-4.1b-luvas-e-empunhadura-
// design.md, seção 7.3; plano, Tarefa 9): o que o luvas.glb carregado pelo GLTFLoader dá para montar os braços — as
// primitivas de cada zona (as geometrias, que o molde guarda e cada braço copia), o modelo das dobras (modeloDobras.js,
// com o esqueleto pelas matrizes de ligação inversas e as correções dos extras) e o esqueleto de repouso (o referencial
// de cada osso no do braço, a raiz `luvas` com a escala do glTF e o `rig_d`/`rig_e`).
// O referencial do braço é o da cena do glTF (u): o pulso na origem, o antebraço em −X, +Y as costas, o polegar em −Z
// na direita e em +Z na esquerda (o espelho do Blender é no eixo do polegar). A malha com skin está nele (a raiz leva a
// escala dos ossos, que estão em metros). O molde confere isso na carga: um .glb com o referencial diferente não monta.

import * as THREE from 'three';
import { OSSOS_DO_BRACO, ossosDoLado } from '../../data/luvas.js';
import { ModeloDobras, dadosDasPrimitivas, normaisDosVertices } from './modeloDobras.js';

const MM_POR_U = 25.4;
const MARCA = /^[0-9a-f]{64}$/;

const _m = new THREE.Matrix4();
const _v = new THREE.Vector3();

function jsonDe(v, oque) {
  if (v === undefined) throw new Error(`luvas: faltam ${oque} nos extras do .glb`);
  try {
    return typeof v === 'string' ? JSON.parse(v) : v;
  } catch (e) {
    throw new Error(`luvas: ${oque} dos extras não são JSON (${e.message})`);
  }
}

/** As malhas com skin de um braço (a do nó `luva_<lado>` ou as filhas dele, uma por zona). */
function malhasDoBraco(no) {
  const out = [];
  no.traverse((o) => o.isSkinnedMesh && out.push(o));
  return out;
}

/**
 * O molde de um braço a partir da cena carregada.
 * @param {THREE.Object3D} cena a `gltf.scene` do luvas.glb
 * @param {'d'|'e'} lado
 * @param {string[]} zonas as zonas esperadas (ZONAS_DAS_LUVAS)
 */
export function moldeDoBraco(cena, lado, zonas) {
  const raiz = cena.getObjectByName('luvas');
  const rig = cena.getObjectByName(`rig_${lado}`);
  const luva = cena.getObjectByName(`luva_${lado}`);
  if (!raiz || !rig || !luva) throw new Error(`luvas: o .glb sem os nós luvas, rig_${lado} e luva_${lado}`);
  const marca = jsonDe(raiz.userData.marca, 'a marca do rig')?.[lado];
  if (!MARCA.test(marca ?? '')) throw new Error(`luvas: sem a marca do rig ${lado} nos extras da raiz`);
  const parametros = jsonDe(luva.userData.correcoes, 'as correções das dobras');
  const malhas = malhasDoBraco(luva);
  if (!malhas.length) throw new Error(`luvas: luva_${lado} sem malha com skin`);
  const skeleton = malhas[0].skeleton;
  for (const m of malhas) if (m.skeleton.bones.some((b, i) => b !== skeleton.bones[i])) throw new Error(`luvas: as zonas de luva_${lado} com esqueletos diferentes`);
  const ossos = skeleton.bones.map((b) => b.name);
  const esperados = ossosDoLado(lado);
  const faltam = esperados.filter((o) => !ossos.includes(o));
  if (faltam.length || ossos.length !== OSSOS_DO_BRACO.length) throw new Error(`luvas: o esqueleto de luva_${lado} sem ${faltam.join(', ') || 'os 20 ossos'}`);
  const pais = skeleton.bones.map((b) => skeleton.bones.indexOf(b.parent));
  const primitivas = malhas.map((m) => {
    const g = m.geometry;
    const zona = m.material?.name;
    if (!zonas.includes(zona)) throw new Error(`luvas: zona desconhecida em luva_${lado}: ${zona}`);
    for (const a of ['position', 'normal', 'tangent', 'uv', 'skinIndex', 'skinWeight', '_vertice']) {
      if (!g.attributes[a]) throw new Error(`luvas: luva_${lado} (${zona}) sem o atributo ${a}`);
    }
    return {
      zona, geometria: g,
      posicoes: g.attributes.position.array, juntas: g.attributes.skinIndex.array, pesos: g.attributes.skinWeight.array,
      vertice: Uint32Array.from(g.attributes._vertice.array, (x) => Math.round(x)), indices: g.index.array,
    };
  });
  const faltaZona = zonas.filter((z) => !primitivas.some((p) => p.zona === z));
  if (faltaZona.length) throw new Error(`luvas: luva_${lado} sem as zonas ${faltaZona.join(', ')}`);
  const malha = dadosDasPrimitivas(primitivas);
  // as cabeças de repouso no referencial da malha (u), pelas matrizes de ligação inversas, em mm
  const cabecas = [];
  for (const inv of skeleton.boneInverses) cabecas.push(..._v.setFromMatrixPosition(_m.copy(inv).invert()).toArray().map((x) => x * MM_POR_U));
  const modelo = new ModeloDobras({ malha, ossos, pais, cabecas, parametros, lado });
  // o esqueleto de repouso no referencial do braço: a raiz e o rig por cima da cadeia dos ossos
  // (os quaternions do arquivo são float32, com a norma a 10⁻⁸ de 1: normalizados, a álgebra dos giros fecha)
  const trs = (o) => ({ posicao: o.position.clone(), quaternion: o.quaternion.clone().normalize(), escala: o.scale.clone() });
  const rRaiz = trs(raiz);
  const rRig = trs(rig);
  const repousoLocal = skeleton.bones.map(trs);
  const base = new THREE.Matrix4().compose(rRaiz.posicao, rRaiz.quaternion, rRaiz.escala)
    .multiply(new THREE.Matrix4().compose(rRig.posicao, rRig.quaternion, rRig.escala));
  const relRepouso = [];
  for (let i = 0; i < ossos.length; i++) {
    const r = repousoLocal[i];
    const local = new THREE.Matrix4().compose(r.posicao, r.quaternion, r.escala);
    relRepouso.push((pais[i] >= 0 ? relRepouso[pais[i]].clone() : base.clone()).multiply(local));
  }
  const iMao = ossos.indexOf(`mao_${lado}`);
  const iAnte = ossos.indexOf(`antebraco_${lado}`);
  const pulso = new THREE.Vector3().setFromMatrixPosition(relRepouso[iMao]);
  const cotovelo = new THREE.Vector3().setFromMatrixPosition(relRepouso[iAnte]);
  const eixo = pulso.clone().sub(cotovelo);
  const comprimento = eixo.length();
  if (eixo.normalize().distanceTo(new THREE.Vector3(1, 0, 0)) > 1e-4) throw new Error(`luvas: o antebraço de ${lado} fora do eixo X (${eixo.toArray()})`);
  const polegar = Math.sign(new THREE.Vector3().setFromMatrixPosition(relRepouso[ossos.indexOf(`polegar_1_${lado}`)]).z);
  if (polegar !== (lado === 'd' ? -1 : 1)) throw new Error(`luvas: o polegar de ${lado} do lado errado do braço`);
  return {
    lado, marca, ossos, pais, modelo, primitivas,
    raiz: rRaiz, rig: rRig, repousoLocal,
    relRepouso,
    relRepousoInv: relRepouso.map((m) => m.clone().invert()),
    quatRepouso: relRepouso.map((m) => new THREE.Quaternion().setFromRotationMatrix(_m.extractRotation(m))),
    normaisRepouso: normaisDosVertices(malha.repouso, malha.triangulos, malha.n),
    pulso, cotovelo, comprimento, polegar,
    triangulos: primitivas.reduce((s, p) => s + p.indices.length / 3, 0),
  };
}

/** Descarta as geometrias do molde (as do .glb carregado; os braços têm as cópias deles). */
export function descartarMolde(molde) {
  for (const p of molde.primitivas) p.geometria.dispose();
}
```

```js file=src/characters/hands/bracoLuva.js
// Um braço de luva no jogo (Fase 4.1b; desenho em docs/superpowers/specs/2026-09-26-4.1b-luvas-e-empunhadura-design.md,
// seções 5 e 7.3; plano, Tarefa 9): o esqueleto próprio (os 20 ossos do luvas.glb debaixo da raiz com a escala do
// glTF), a luva deformada na CPU pelo modelo das dobras (as mesmas contas do Blender: a malha sai como saiu na validação
// e no solver da empunhadura), o antebraço e a braçadeira de massinha (skin de dois ossos na GPU, ClayMaterial sem boil).
//  - `aplicarPega(pega)`: os 17 ossos de dedo no quaternion do clipe `empunhadura` do .glb da arma — só com a mesma
//    marca do rig (as luvas e a arma construídas juntas);
//  - `colocar(pulso, maoQuat, cotovelo, cima)`: o osso `mao` no pulso e na orientação da pega (no referencial de quem
//    contém o braço); o antebraço apontando do cotovelo para o pulso, com o comprimento da ficha (o cotovelo de verdade
//    fica no alinhamento, a esse comprimento do pulso) e na torção neutra da anatomia (o polegar para `cima`, a meia
//    pronação do antebraço com o cotovelo dobrado); a torção até a mão dividida meio a meio entre a `torcao` e a `mao`;
//    devolve os ângulos do pulso e do antebraço e um aviso para cada limite da AAOS passado (a ficha);
//  - `setFaccao`, `setBracadeira`, `setCorDaMassa`.
// A luva só é recalculada quando a pose dos ossos muda (dedos, torção, pulso): mover o braço inteiro não custa nada.

import * as THREE from 'three';
import { ClayMaterial } from '../../clay/ClayMaterial.js';
import { BRACO_DE_MASSA, OSSOS_DE_DEDO } from '../../data/luvas.js';
import { OSSOS_DO_ANTEBRACO } from './antebracoMassa.js';
import { normaisDosVertices } from './modeloDobras.js';

const MM_POR_U = 25.4;
const GRAUS = 180 / Math.PI;
const IGUAL = 1e-10; // 1 − |q·q'| abaixo disso é o mesmo giro (≈ 3·10⁻⁵ rad)
const X = new THREE.Vector3(1, 0, 0);
const CIMA = Object.freeze(new THREE.Vector3(0, 1, 0));

const _d = new THREE.Vector3();
const _s = new THREE.Vector3();
const _y = new THREE.Vector3();
const _z = new THREE.Vector3();
const _f = new THREE.Vector3();
const _mat = new THREE.Matrix4();
const _q = new THREE.Quaternion();
const _r = new THREE.Quaternion();

/**
 * A torção de um giro Δ em volta do eixo do antebraço (+X do braço) e o que sobra para o pulso (swing-twist): Δ = T·B,
 * a pronação T do antebraço e o balanço B do pulso no referencial do rádio já girado — o rádio leva a pronação inteira
 * até o pulso, e a flexão e o desvio são medidos nele (a direção da mão, R(−τ)·Δ·X). A metade da torção vai para o osso
 * `torcao` e a outra para a `mao`: é a divisão do skin, para a malha do punho torcer ao longo do antebraço.
 * @param {THREE.Quaternion} delta o giro da mão no referencial do braço, do repouso para a pose
 * @param {number} polegar −1 (direita, polegar em −Z) ou +1 (esquerda)
 * @returns {{torcao:number, meia:THREE.Quaternion, flexao:number, desvio:number, pronacao:number}} a torção total
 *   (radianos, em +X), o giro da metade e os ângulos em graus: flexão (+) e extensão (−) do pulso, desvio radial (+) e
 *   ulnar (−), pronação (+) e supinação (−) do antebraço a partir da meia pronação
 */
export function torcaoDoPulso(delta, polegar) {
  const q = delta.w < 0 ? new THREE.Quaternion(-delta.x, -delta.y, -delta.z, -delta.w) : delta.clone();
  const torcao = Math.hypot(q.x, q.w) > 1e-12 ? 2 * Math.atan2(q.x, q.w) : 0;
  const meia = new THREE.Quaternion().setFromAxisAngle(X, torcao / 2);
  // a direção da mão no referencial do rádio: R(−τ)·Δ·X (a torção inteira desfeita)
  _f.copy(X).applyQuaternion(q).applyAxisAngle(X, -torcao);
  return {
    torcao, meia,
    flexao: Math.atan2(-_f.y, _f.x) * GRAUS,
    desvio: Math.atan2(polegar * _f.z, _f.x) * GRAUS,
    pronacao: polegar * torcao * GRAUS,
  };
}

/** Os avisos dos limites da AAOS (a ficha: `limites.pulso` e `limites.antebraco`, graus) passados. */
export function avisosDoPulso(a, limites) {
  const p = limites.pulso;
  const b = limites.antebraco;
  const out = [];
  const passa = (valor, limite, nome) => {
    if (valor > limite + 1e-9) out.push(`${nome} de ${valor.toFixed(1)}° (limite ${limite}°)`);
  };
  passa(a.flexao, p.flexao, 'pulso: flexão');
  passa(-a.flexao, p.extensao, 'pulso: extensão');
  passa(a.desvio, p.radial, 'pulso: desvio radial');
  passa(-a.desvio, p.ulnar, 'pulso: desvio ulnar');
  passa(a.pronacao, b.pronacao, 'antebraço: pronação');
  passa(-a.pronacao, b.supinacao, 'antebraço: supinação');
  return out;
}

const mesmoGiro = (a, b) => 1 - Math.abs(a.dot(b)) < IGUAL;

export class BracoLuva {
  #molde;
  #materiaisDe;
  #faccaoPedida;
  #malhas = [];
  #bones = [];
  #iMao;
  #iTorcao;
  #iAnte;
  #rel;
  #D;
  #pts = null;
  #raiz;
  #rig;
  #sujo = true;

  /**
   * @param {{molde:ReturnType<import('./moldeLuva.js').moldeDoBraco>, faccao:string, materiais:Object<string, THREE.Material>,
   *   materiaisDe:(faccao:string)=>Promise<Object<string, THREE.Material>>, antebraco:{antebraco:THREE.BufferGeometry,
   *   bracadeira:THREE.BufferGeometry}, corDaMassa:string, limites:{pulso:object, antebraco:object}, log?:object|null}} o
   *   `materiais` = os da facção (da LuvasSource, divididos entre os braços); `antebraco` = as malhas de massinha
   *   (divididas); o braço é dono do esqueleto, das cópias das malhas da luva e dos materiais de massinha
   */
  constructor({ molde, faccao, materiais, materiaisDe, antebraco, corDaMassa, limites, log = null }) {
    this.#molde = molde;
    this.#materiaisDe = materiaisDe;
    this.lado = molde.lado;
    this.marca = molde.marca;
    this.faccao = faccao;
    this.#faccaoPedida = faccao;
    this.limites = limites;
    this.log = log;
    this.grupo = new THREE.Group();
    this.grupo.name = `luvas:${this.lado}`;
    // o esqueleto: a raiz com a escala do glTF, o rig e os ossos na pose de repouso
    const raiz = new THREE.Object3D();
    raiz.name = 'luvas';
    raiz.position.copy(molde.raiz.posicao);
    raiz.quaternion.copy(molde.raiz.quaternion);
    raiz.scale.copy(molde.raiz.escala);
    const rig = new THREE.Object3D();
    rig.name = `rig_${this.lado}`;
    rig.position.copy(molde.rig.posicao);
    rig.quaternion.copy(molde.rig.quaternion);
    rig.scale.copy(molde.rig.escala);
    raiz.add(rig);
    this.grupo.add(raiz);
    this.#raiz = raiz;
    this.#rig = rig;
    this.ossos = {};
    molde.ossos.forEach((nome, i) => {
      const b = new THREE.Bone();
      b.name = nome;
      const r = molde.repousoLocal[i];
      b.position.copy(r.posicao);
      b.quaternion.copy(r.quaternion);
      b.scale.copy(r.escala);
      (molde.pais[i] >= 0 ? this.#bones[molde.pais[i]] : rig).add(b);
      this.#bones.push(b);
      this.ossos[nome.slice(0, -2)] = b;
    });
    this.#iMao = molde.ossos.indexOf(`mao_${this.lado}`);
    this.#iTorcao = molde.ossos.indexOf(`torcao_${this.lado}`);
    this.#iAnte = molde.ossos.indexOf(`antebraco_${this.lado}`);
    this.#rel = molde.ossos.map(() => new THREE.Matrix4());
    this.#D = new Float64Array(molde.ossos.length * 12);
    // a luva: uma malha por zona, com as posições, as normais e as tangentes da pose (a cópia do braço) e as de repouso
    for (const p of molde.primitivas) {
      const g = p.geometria.clone();
      g.deleteAttribute('skinIndex');
      g.deleteAttribute('skinWeight');
      g.deleteAttribute('_vertice');
      g.setAttribute('repouso', g.attributes.position.clone());
      g.setAttribute('normalRepouso', g.attributes.normal.clone());
      g.name = `luva_${this.lado}:${p.zona}`;
      const m = new THREE.Mesh(g, materiais[p.zona]);
      m.name = g.name;
      m.castShadow = true;
      m.receiveShadow = true;
      this.grupo.add(m);
      this.#malhas.push({
        malha: m, zona: p.zona, vertice: p.vertice,
        normal: g.attributes.normal.array.slice(), tangente: g.attributes.tangent.array.slice(),
      });
    }
    // o antebraço e a braçadeira de massinha: skin de dois ossos na GPU, preso ao grupo (a malha no referencial do braço)
    const M = BRACO_DE_MASSA;
    const doisOssos = OSSOS_DO_ANTEBRACO.map((o) => this.ossos[o]);
    const inversas = OSSOS_DO_ANTEBRACO.map((o) => molde.relRepousoInv[molde.ossos.indexOf(`${o}_${this.lado}`)].clone());
    this.skeleton = new THREE.Skeleton(doisOssos, inversas);
    this.materialMassa = new ClayMaterial({ color: corDaMassa, roughness: M.massa.roughness, wetness: M.massa.wetness, touched: true, boil: 0, seed: `antebraco-${this.lado}` });
    this.materialMassa.setObjectSize(M.massa.objectSize);
    this.antebraco = this.#pele(antebraco.antebraco, this.materialMassa, `antebraco-${this.lado}`);
    const B = M.bracadeira;
    this.materialBracadeira = new ClayMaterial({ color: corDaMassa, roughness: B.massa.roughness, wetness: B.massa.wetness, touched: true, boil: 0, seed: `bracadeira-${this.lado}` });
    this.materialBracadeira.setObjectSize(B.massa.objectSize);
    this.bracadeira = this.#pele(antebraco.bracadeira, this.materialBracadeira, `bracadeira-${this.lado}`);
    this.bracadeira.visible = false;
    this.pega = null;
    this.angulos = { flexao: 0, desvio: 0, pronacao: 0 };
    this.avisos = [];
    this.#deformar();
  }

  #pele(geometria, material, nome) {
    const m = new THREE.SkinnedMesh(geometria, material);
    m.name = nome;
    m.frustumCulled = false; // os ossos saem da caixa de repouso
    m.castShadow = true;
    m.receiveShadow = true;
    this.grupo.add(m);
    m.bind(this.skeleton, new THREE.Matrix4());
    return m;
  }

  /** As malhas da luva (uma por zona). */
  get malhas() {
    return this.#malhas.map((m) => m.malha);
  }

  get triangulos() {
    return this.#molde.triangulos;
  }

  /** As posições da luva na pose atual (mm, referencial do braço), uma por vértice do Blender (o `luvas_contato`). */
  get posicoesMM() {
    return this.#pts;
  }

  /**
   * Os dedos na pega de uma arma: {marca: {d, e}, dedos: {d|e: {osso: [x, y, z, w]}}} (lida do .glb da arma).
   * Recusa a pega de um rig diferente (as luvas mudaram depois de a arma ser construída).
   */
  aplicarPega(pega) {
    const marca = pega?.marca?.[this.lado];
    if (marca !== this.marca) {
      throw new Error(`pega: a marca do rig ${this.lado} da arma (${String(marca).slice(0, 12)}) não é a das luvas (${this.marca.slice(0, 12)}); construa a arma de novo`);
    }
    const dedos = pega.dedos?.[this.lado] ?? {};
    for (const osso of OSSOS_DE_DEDO) if (!dedos[osso]) throw new Error(`pega: sem a rotação de ${osso}_${this.lado}`);
    for (const osso of OSSOS_DE_DEDO) this.ossos[osso].quaternion.fromArray(dedos[osso]).normalize();
    this.pega = pega;
    this.#sujo = true;
    this.atualizar();
  }

  /** Os dedos de volta ao repouso (sem arma). */
  soltarPega() {
    const m = this.#molde;
    for (const osso of OSSOS_DE_DEDO) this.ossos[osso].quaternion.copy(m.repousoLocal[m.ossos.indexOf(`${osso}_${this.lado}`)].quaternion);
    this.pega = null;
    this.#sujo = true;
    this.atualizar();
  }

  /**
   * Põe o braço: o osso `mao` em `pulso` com a rotação `maoQuat` (a do osso no referencial de quem contém o grupo) e o
   * antebraço apontando de `cotovelo` para o pulso, na torção neutra com o polegar para `cima`.
   * @param {THREE.Vector3} pulso @param {THREE.Quaternion} maoQuat @param {THREE.Vector3} cotovelo
   * @param {THREE.Vector3} [cima] a direção do polegar do antebraço na meia pronação (padrão: +Y de quem contém)
   * @returns {{angulos:{flexao:number, desvio:number, pronacao:number}, avisos:string[]}}
   */
  colocar(pulso, maoQuat, cotovelo, cima = CIMA) {
    const m = this.#molde;
    _d.subVectors(pulso, cotovelo);
    const dist = _d.length();
    if (!(dist > 1e-9)) throw new Error('braço: o cotovelo em cima do pulso');
    _d.divideScalar(dist);
    _s.copy(cima).addScaledVector(_d, -cima.dot(_d));
    if (_s.lengthSq() < 1e-12) _s.set(0, 0, 1).addScaledVector(_d, -_d.z); // o antebraço em pé: qualquer lado serve
    _s.normalize();
    // o grupo: +X do braço no antebraço, o polegar (σ·Z) para cima
    _z.copy(_s).multiplyScalar(m.polegar);
    _y.crossVectors(_z, _d);
    _mat.makeBasis(_d, _y, _z);
    this.grupo.quaternion.setFromRotationMatrix(_mat);
    this.grupo.position.copy(pulso).sub(_f.copy(m.pulso).applyQuaternion(this.grupo.quaternion));
    // o giro da mão no referencial do braço, do repouso para a pose: Δ = Q⁻¹·M·R_mão⁻¹
    const delta = _q.copy(this.grupo.quaternion).invert().multiply(maoQuat).multiply(_r.copy(m.quatRepouso[this.#iMao]).invert());
    const t = torcaoDoPulso(delta, m.polegar);
    // a `torcao` com a metade; a `mao` com o resto (o giro inteiro no referencial do braço)
    const rt = t.meia.clone().multiply(m.quatRepouso[this.#iTorcao]);
    const localT = m.quatRepouso[this.#iAnte].clone().invert().multiply(rt);
    const rm = delta.clone().multiply(m.quatRepouso[this.#iMao]);
    const localM = rt.clone().invert().multiply(rm);
    const torcao = this.#bones[this.#iTorcao];
    const mao = this.#bones[this.#iMao];
    if (!mesmoGiro(torcao.quaternion, localT) || !mesmoGiro(mao.quaternion, localM)) {
      torcao.quaternion.copy(localT);
      mao.quaternion.copy(localM);
      this.#sujo = true;
    }
    this.angulos = { flexao: t.flexao, desvio: t.desvio, pronacao: t.pronacao };
    const avisos = avisosDoPulso(this.angulos, this.limites);
    if (avisos.join() !== this.avisos.join() && avisos.length) this.log?.warn?.(`luvas ${this.lado}: ${avisos.join('; ')}`);
    this.avisos = avisos;
    this.atualizar();
    return { angulos: this.angulos, avisos };
  }

  /** Recalcula a luva se a pose dos ossos mudou; true se recalculou. */
  atualizar() {
    if (!this.#sujo) return false;
    this.#deformar();
    return true;
  }

  // As deformações dos ossos no referencial do braço (a pose vezes a inversa do repouso; mm), o modelo das dobras e as
  // posições, normais e tangentes de cada vértice do glTF pelo vértice do Blender dele. A normal e a tangente de
  // repouso (as do Blender) giram pela rotação mínima entre a normal de repouso do modelo e a da pose.
  #deformar() {
    const m = this.#molde;
    this.#raiz.updateMatrix();
    this.#rig.updateMatrix();
    const base = _mat.multiplyMatrices(this.#raiz.matrix, this.#rig.matrix);
    const D = this.#D;
    for (let i = 0; i < this.#bones.length; i++) {
      const b = this.#bones[i];
      b.updateMatrix();
      const pai = m.pais[i];
      this.#rel[i].multiplyMatrices(pai >= 0 ? this.#rel[pai] : base, b.matrix);
      const e = _m2.multiplyMatrices(this.#rel[i], m.relRepousoInv[i]).elements;
      const o = i * 12;
      for (let r = 0; r < 3; r++) for (let c = 0; c < 3; c++) D[o + r * 3 + c] = e[c * 4 + r];
      D[o + 9] = e[12] * MM_POR_U;
      D[o + 10] = e[13] * MM_POR_U;
      D[o + 11] = e[14] * MM_POR_U;
    }
    const pts = m.modelo.avaliar(D);
    this.#pts = pts;
    const n = m.modelo.malha.n;
    const vn = normaisDosVertices(pts, m.modelo.malha.triangulos, n);
    const n0 = m.normaisRepouso;
    // o giro mínimo de cada vértice do Blender (eixo·seno e cosseno)
    const giro = new Float64Array(n * 4);
    for (let v = 0; v < n; v++) {
      const a = v * 3;
      const kx = n0[a + 1] * vn[a + 2] - n0[a + 2] * vn[a + 1];
      const ky = n0[a + 2] * vn[a] - n0[a] * vn[a + 2];
      const kz = n0[a] * vn[a + 1] - n0[a + 1] * vn[a];
      giro[v * 4] = kx;
      giro[v * 4 + 1] = ky;
      giro[v * 4 + 2] = kz;
      giro[v * 4 + 3] = n0[a] * vn[a] + n0[a + 1] * vn[a + 1] + n0[a + 2] * vn[a + 2];
    }
    for (const z of this.#malhas) {
      const g = z.malha.geometry;
      const P = g.attributes.position.array;
      const N = g.attributes.normal.array;
      const T = g.attributes.tangent.array;
      for (let k = 0; k < z.vertice.length; k++) {
        const v = z.vertice[k];
        P[k * 3] = pts[v * 3] / MM_POR_U;
        P[k * 3 + 1] = pts[v * 3 + 1] / MM_POR_U;
        P[k * 3 + 2] = pts[v * 3 + 2] / MM_POR_U;
        girarMinimo(z.normal, k * 3, giro, v, N, k * 3);
        girarMinimo(z.tangente, k * 4, giro, v, T, k * 4);
        T[k * 4 + 3] = z.tangente[k * 4 + 3];
      }
      g.attributes.position.needsUpdate = true;
      g.attributes.normal.needsUpdate = true;
      g.attributes.tangent.needsUpdate = true;
      g.computeBoundingSphere();
      g.computeBoundingBox();
    }
    this.#sujo = false;
  }

  /** Troca a pintura da luva pela da facção (a nova entra quando os materiais estão prontos). */
  async setFaccao(faccao) {
    this.#faccaoPedida = faccao;
    const mats = await this.#materiaisDe(faccao);
    if (this.#faccaoPedida !== faccao || !this.#malhas.length) return false;
    for (const z of this.#malhas) z.malha.material = mats[z.zona];
    this.faccao = faccao;
    return true;
  }

  /** Braçadeira do time: cor (hex) ou null para esconder. */
  setBracadeira(cor) {
    this.bracadeira.visible = Boolean(cor);
    if (cor) this.materialBracadeira.color.set(cor);
  }

  /** Cor da massa do antebraço (a do boneco). */
  setCorDaMassa(cor) {
    this.materialMassa.color.set(cor);
  }

  dispose() {
    this.grupo.removeFromParent();
    for (const z of this.#malhas) z.malha.geometry.dispose();
    this.#malhas = [];
    this.materialMassa.dispose();
    this.materialBracadeira.dispose();
    this.skeleton.dispose();
  }
}

const _m2 = new THREE.Matrix4();

/** Gira o vetor (3 componentes em `de[i]`) pelo giro mínimo do vértice v (eixo·sen e cos em `giro`) e grava em `para[j]`. */
function girarMinimo(de, i, giro, v, para, j) {
  const x = de[i];
  const y = de[i + 1];
  const z = de[i + 2];
  const kx = giro[v * 4];
  const ky = giro[v * 4 + 1];
  const kz = giro[v * 4 + 2];
  const c = giro[v * 4 + 3];
  const s2 = kx * kx + ky * ky + kz * kz;
  if (s2 < 1e-18) {
    para[j] = x;
    para[j + 1] = y;
    para[j + 2] = z;
    return;
  }
  // Rodrigues com k = eixo·sen: v·c + (k×v) + k·(k·v)·(1 − c)/sen²
  const f = (kx * x + ky * y + kz * z) * (1 - c) / s2;
  para[j] = x * c + (ky * z - kz * y) + kx * f;
  para[j + 1] = y * c + (kz * x - kx * z) + ky * f;
  para[j + 2] = z * c + (kx * y - ky * x) + kz * f;
}
```

```js file=src/characters/hands/luvasSource.js
// Serviço `luvasModels` (Fase 4.1b; desenho em docs/superpowers/specs/2026-09-26-4.1b-luvas-e-empunhadura-design.md,
// seção 7.3; plano, Tarefa 9): as luvas táticas feitas no Blender (assets/maos/; registro em src/data/luvas.js) com o
// antebraço de massinha. Carrega uma vez o luvas.glb (os dois braços com o esqueleto e as correções das dobras), o
// relatório e a ficha; as texturas (_n e _m) quando o primeiro material é pedido; os materiais por facção (as pinturas
// de LUVAS, no material das zonas das armas, com o padrão pela pose de repouso e as duas faces, como o .glb pede); e as
// malhas do antebraço e da braçadeira de massinha, geradas uma vez por sessão no SdfMesher. Tudo marcado
// `userData.shared` (o dispose das cenas não toca) e dividido entre os braços; cada braço (`instanciar`) tem o esqueleto
// e as cópias das malhas da luva dele. Os carregadores são injetados: no navegador, os da origem glb das armas
// (GLTFLoader do vendor com o Draco); no Node, os dos testes.

import * as THREE from 'three';
import { FACCOES_DAS_LUVAS, LUVAS, ZONAS_DAS_LUVAS } from '../../data/luvas.js';
import { ambienteDoMaterial, criarMaterialZona } from '../../weapons/model/materialArma.js';
import { validarPintura } from '../../weapons/skins/skin.js';
import { construirAntebraco } from './antebracoMassa.js';
import { BracoLuva } from './bracoLuva.js';
import { validarFichaLuvas } from './fichaLuvas.js';
import { descartarMolde, moldeDoBraco } from './moldeLuva.js';

const now = () => (globalThis.performance?.now ? globalThis.performance.now() : Date.now());
const RAIZ = new URL('../../../', import.meta.url);
const LADOS = Object.freeze(['d', 'e']);

export class LuvasSource {
  #carregar;
  #sdf;
  #log;
  #anisotropia;
  #pronto = null; // Promise<dados>
  #dados = null; // {moldes: {d, e}, ficha, relatorio, ms}
  #texturas = null; // Promise<{n, m}>
  #texturasProntas = [];
  #materiais = new Map(); // facção → Promise<{zona: material}>
  #prontosMat = new Map(); // facção → {zona: material}
  #antebraco = null; // Promise<{antebraco, bracadeira}>
  #antebracoPronto = null;
  #bracos = new Set();
  #ambiente = null;
  #intensidade = 1;
  #erro = null;
  #descartada = false;

  /**
   * @param {{carregadores:{glb:(url:string)=>Promise<{scene:THREE.Object3D}>, textura:(url:string)=>Promise<THREE.Texture>,
   *   json:(url:string)=>Promise<object>, descartar?:()=>void}, sdf:{build:(tree:object, o:object)=>Promise<THREE.BufferGeometry>},
   *   log?:object|null, anisotropia?:number}} deps
   */
  constructor({ carregadores, sdf, log = null, anisotropia = 8 }) {
    this.#carregar = carregadores;
    this.#sdf = sdf;
    this.#log = log;
    this.#anisotropia = anisotropia;
  }

  #url(arquivo) {
    return new URL(`${LUVAS.pasta}${arquivo}`, RAIZ).href;
  }

  /** Um arquivo pelo carregador, com o nome dele no erro. */
  #buscar(tipo, url) {
    const arquivo = url.slice(url.lastIndexOf('/') + 1);
    return this.#carregar[tipo](url).catch((e) => {
      throw new Error(`${arquivo}: ${e?.message ?? e}`);
    });
  }

  /** Carrega o .glb, o relatório e a ficha (uma vez; pedidos ao mesmo tempo dividem a promessa). */
  carregar() {
    if (this.#descartada) return Promise.reject(new Error('LuvasSource: já foi descartada'));
    if (!this.#pronto) {
      const t0 = now();
      const p = Promise.all([
        this.#buscar('glb', this.#url('luvas.glb')),
        this.#buscar('json', this.#url('luvas.relatorio.json')),
        this.#buscar('json', new URL('tools/blender/refs/luvas.json', RAIZ).href),
      ]).then(([gltf, relatorio, ficha]) => {
        const f = validarFichaLuvas(ficha);
        const moldes = {};
        try {
          for (const lado of LADOS) moldes[lado] = moldeDoBraco(gltf.scene, lado, ZONAS_DAS_LUVAS);
        } finally {
          // os materiais do arquivo não entram: cada zona recebe os da facção
          gltf.scene.traverse((o) => {
            if (o.isMesh) for (const m of [o.material].flat()) m?.dispose();
          });
        }
        if (this.#descartada || this.#pronto !== p) {
          for (const lado of LADOS) descartarMolde(moldes[lado]);
          throw new Error('luvas descartadas durante a carga');
        }
        for (const lado of LADOS) {
          if (relatorio?.marca?.[lado] && relatorio.marca[lado] !== moldes[lado].marca) {
            this.#log?.warn?.(`luvas: a marca do rig ${lado} do relatório não é a do .glb (arquivos de construções diferentes)`);
          }
        }
        if (relatorio?.aprovado === false) this.#log?.warn?.(`luvas: o relatório do Blender não aprovou as luvas (${(relatorio.problemas ?? []).join('; ')})`);
        const dados = { moldes, ficha: f, relatorio, ms: now() - t0 };
        this.#dados = dados;
        this.#erro = null;
        this.#log?.debug?.(`luvas: ${moldes.d.triangulos} + ${moldes.e.triangulos} triângulos em ${dados.ms.toFixed(0)} ms`);
        return dados;
      });
      p.catch((err) => {
        if (this.#pronto === p) this.#pronto = null;
        if (this.#descartada) return;
        this.#erro = err?.message ?? String(err);
        this.#log?.error?.(`luvas: não carregaram — ${this.#erro}`);
      });
      this.#pronto = p;
    }
    return this.#pronto;
  }

  #texturasDasLuvas() {
    if (!this.#texturas) {
      const p = Promise.all([this.#buscar('textura', this.#url('luvas_n.webp')), this.#buscar('textura', this.#url('luvas_m.webp'))])
        .then(([n, m]) => {
          for (const t of [n, m]) {
            t.userData.shared = true;
            t.anisotropy = this.#anisotropia;
            this.#texturasProntas.push(t);
          }
          return { n, m };
        });
      p.catch(() => {
        if (this.#texturas === p) this.#texturas = null;
      });
      this.#texturas = p;
    }
    return this.#texturas;
  }

  /** Os materiais (um por zona) da pintura de uma facção; divididos entre os braços. */
  materiais(faccao) {
    if (this.#descartada) return Promise.reject(new Error('LuvasSource: já foi descartada'));
    if (!FACCOES_DAS_LUVAS.includes(faccao)) return Promise.reject(new Error(`facção das luvas desconhecida: ${faccao} (use ${FACCOES_DAS_LUVAS.join(', ')})`));
    let p = this.#materiais.get(faccao);
    if (!p) {
      p = this.#texturasDasLuvas().then((texturas) => {
        const pintura = validarPintura(ZONAS_DAS_LUVAS, LUVAS.pinturas[faccao], `luvas ${faccao}`);
        const mats = {};
        for (const zona of ZONAS_DAS_LUVAS) {
          const m = criarMaterialZona({
            zona, def: pintura.zonas[zona], texturas, ambiente: this.#ambiente, intensidade: this.#intensidade,
            nome: `luvas:${faccao}:${zona}`, repouso: true,
          });
          m.side = THREE.DoubleSide; // o punho mostra o forro por dentro da boca, como no .glb
          mats[zona] = m;
        }
        if (this.#descartada || this.#materiais.get(faccao) !== p) {
          for (const m of Object.values(mats)) m.dispose();
          throw new Error('luvas descartadas durante a carga');
        }
        this.#prontosMat.set(faccao, mats);
        return mats;
      });
      p.catch(() => {
        if (this.#materiais.get(faccao) === p) this.#materiais.delete(faccao);
      });
      this.#materiais.set(faccao, p);
    }
    return p;
  }

  /** As malhas do antebraço e da braçadeira de massinha (uma vez por sessão). */
  #antebracoDe(ficha) {
    if (!this.#antebraco) {
      const p = construirAntebraco(this.#sdf, ficha).then((g) => {
        if (this.#descartada || this.#antebraco !== p) {
          g.antebraco.dispose();
          g.bracadeira.dispose();
          throw new Error('luvas descartadas durante a geração do antebraço');
        }
        this.#antebracoPronto = g;
        return g;
      });
      p.catch((err) => {
        if (this.#antebraco === p) this.#antebraco = null;
        if (!this.#descartada) this.#log?.error?.(`luvas: o antebraço de massinha não foi gerado — ${err?.message ?? err}`);
      });
      this.#antebraco = p;
    }
    return this.#antebraco;
  }

  /**
   * Um braço novo (esqueleto e malhas da luva próprios) na pintura da facção, com a massa do antebraço na cor dada.
   * @param {'d'|'e'} lado @param {string} faccao @param {{corDaMassa:string}} o
   */
  async instanciar(lado, faccao, { corDaMassa }) {
    if (!LADOS.includes(lado)) throw new Error(`lado das luvas: 'd' ou 'e' (veio ${lado})`);
    const dados = await this.carregar();
    const [materiais, antebraco] = await Promise.all([this.materiais(faccao), this.#antebracoDe(dados.ficha)]);
    if (this.#descartada) throw new Error('LuvasSource: já foi descartada');
    const braco = new BracoLuva({
      molde: dados.moldes[lado], faccao, materiais, materiaisDe: (f) => this.materiais(f), antebraco, corDaMassa,
      limites: dados.ficha.limites, log: this.#log,
    });
    this.#bracos.add(braco);
    const descartar = braco.dispose.bind(braco);
    braco.dispose = () => {
      this.#bracos.delete(braco);
      descartar();
    };
    return braco;
  }

  /** A ficha validada (null antes de carregar). */
  get ficha() {
    return this.#dados?.ficha ?? null;
  }

  /** A marca do rig de cada braço (null antes de carregar). */
  get marca() {
    const d = this.#dados;
    return d ? { d: d.moldes.d.marca, e: d.moldes.e.marca } : null;
  }

  /** Reflexo do set nos materiais das luvas (null volta ao ambiente da cena). */
  setAmbiente(textura, intensidade = 1) {
    this.#ambiente = textura;
    this.#intensidade = intensidade;
    for (const mats of this.#prontosMat.values()) for (const m of Object.values(mats)) ambienteDoMaterial(m, textura, intensidade);
  }

  /** Anisotropia das texturas das luvas (graphics.anisotropy). */
  setAnisotropia(n) {
    this.#anisotropia = n;
    for (const t of this.#texturasProntas) {
      t.anisotropy = n;
      t.needsUpdate = true;
    }
  }

  /** O estado do console `luvas`: carga, triângulos por braço, o antebraço de massinha, a marca e os braços vivos. */
  relatorio() {
    const d = this.#dados;
    return {
      estado: d ? 'pronta' : this.#pronto ? 'carregando' : this.#erro ? 'erro' : '—',
      erro: this.#erro,
      triangulos: d ? { d: d.moldes.d.triangulos, e: d.moldes.e.triangulos } : { d: 0, e: 0 },
      antebraco: this.#antebracoPronto ? this.#antebracoPronto.antebraco.index.count / 3 : 0,
      ms: d ? Math.round(d.ms) : 0,
      marca: this.marca,
      bracos: this.#bracos.size,
    };
  }

  dispose() {
    this.#descartada = true;
    for (const b of [...this.#bracos]) b.dispose();
    for (const mats of this.#prontosMat.values()) for (const m of Object.values(mats)) m.dispose();
    this.#prontosMat.clear();
    this.#materiais.clear();
    for (const t of this.#texturasProntas) t.dispose();
    this.#texturasProntas = [];
    this.#texturas = null;
    if (this.#antebracoPronto) {
      this.#antebracoPronto.antebraco.dispose();
      this.#antebracoPronto.bracadeira.dispose();
    }
    this.#antebracoPronto = null;
    this.#antebraco = null;
    if (this.#dados) for (const lado of LADOS) descartarMolde(this.#dados.moldes[lado]);
    this.#dados = null;
    this.#pronto = null;
    this.#carregar.descartar?.();
  }
}
```

Em `src/clay/sdf/params.js`, trocar:

```
  'sphere', 'ellipsoid', 'capsule', 'roundCone', 'roundBox', 'cylinder', 'torus', 'cone', 'spiral',
  'profile', 'lathe', 'tube',
]);
```

por:

```
  'sphere', 'ellipsoid', 'capsule', 'roundCone', 'roundBox', 'cylinder', 'torus', 'cone', 'spiral',
  'profile', 'lathe', 'tube', 'tronco',
]);
```

Em `src/clay/sdf/bounds.js`, trocar:

```
} from './params.js';

```

por:

```
} from './params.js';
import { suporteDoTronco } from './tronco.js';

```

Em `src/clay/sdf/bounds.js`, trocar:

```
    }
    default:
```

por:

```
    }
    case 'tronco':
      // Casca convexa dos retângulos das seções (o arredondamento só encolhe).
      return suporteDoTronco(node, path);
    default:
```

Em `src/clay/sdf/shapes.js`, trocar:

```
// por uma polilinha) — formas de peça de massa cortada à mão (QPG2, QPL4); contornos em src/clay/sdf/polygon.js.
// Todas aceitam pos/rot/scale (rígida + escala uniforme, então o SDF continua exato) e mat.
```

por:

```
// por uma polilinha) — formas de peça de massa cortada à mão (QPG2, QPL4); contornos em src/clay/sdf/polygon.js.
// Fase 4.1b (luvas): o tronco de seção de retângulo arredondado que muda ao longo de X (src/clay/sdf/tronco.js), o
// antebraço de massinha que entra no punho da luva.
// Todas aceitam pos/rot/scale (rígida + escala uniforme, então o SDF continua exato) e mat.
```

Em `src/clay/sdf/shapes.js`, trocar:

```
import { filletPolygon, latheOutline, polygonDistance } from './polygon.js';

```

por:

```
import { filletPolygon, latheOutline, polygonDistance } from './polygon.js';
import { lerTronco } from './tronco.js';

```

Em `src/clay/sdf/shapes.js`, trocar:

```
      return tubeShape(node, t, mat, path);
    default:
```

por:

```
      return tubeShape(node, t, mat, path);
    case 'tronco': {
      const { x0, x1, alcance, d } = lerTronco(node, path);
      return exactShape((x, y, z) => {
        toLocal(t, x, y, z);
        return t.s * d(LP[0], LP[1], LP[2]);
      }, mat, sphereBound(t, (x0 + x1) / 2, 0, 0, Math.hypot((x1 - x0) / 2, alcance), 1));
    }
    default:
```

Em `src/main.js`, trocar:

```
import { HandLibrary } from './characters/hands/handLibrary.js';
import { InputManager } from './input/inputManager.js';
```

por:

```
import { HandLibrary } from './characters/hands/handLibrary.js';
import { LuvasSource } from './characters/hands/luvasSource.js';
import { carregadoresDoNavegador } from './weapons/model/glbSource.js';
import { InputManager } from './input/inputManager.js';
```

Em `src/main.js`, trocar:

```
  const handModels = new HandLibrary({ sdf, log });
  config.watch('graphics.anisotropy', () => {
```

por:

```
  const handModels = new HandLibrary({ sdf, log });
  // Luvas táticas das armas realistas (Fase 4.1b): o .glb do Blender com os dois braços, as pinturas das facções e o
  // antebraço de massinha gerado uma vez — cada braço com o esqueleto e a luva dele.
  const luvasModels = new LuvasSource({ carregadores: carregadoresDoNavegador(), sdf, log, anisotropia: render.anisotropy });
  config.watch('graphics.anisotropy', () => {
```

Em `src/main.js`, trocar:

```
    weaponModels.setAnisotropy(render.anisotropy);
  });
```

por:

```
    weaponModels.setAnisotropy(render.anisotropy);
    luvasModels.setAnisotropia(render.anisotropy);
  });
```

Em `src/main.js`, trocar:

```
  const services = {
    events, log, store, config, render, clay, set, sdf, weaponModels, handModels, quality, input, rebinder, loop, states, rng, cheats,
    roster, localLoadout, sv, focusNav, toasts, uiRoot, debugRoot, touchLayer,
  };
```

por:

```
  const services = {
    events, log, store, config, render, clay, set, sdf, weaponModels, handModels, luvasModels, quality, input, rebinder, loop, states,
    rng, cheats, roster, localLoadout, sv, focusNav, toasts, uiRoot, debugRoot, touchLayer,
  };
```

Run: `node --test tests/sdfTronco.test.js tests/antebracoMassa.test.js tests/bracoLuva.test.js tests/luvasSource.test.js`
Expected: PASS — # tests 25 # pass 25 # fail 0 .

Run: `node --test "tests/**/*.test.js"`
Expected: PASS — # tests 435 # pass 435 # fail 0 .

### Tarefa 10: O viewmodel com as luvas

**Files:** Modify `src/weapons/viewmodel/viewmodel.js`, `placement.js`, `src/data/viewmodel.js`,
`src/weapons/model/glbSource.js`, `glbWeapon.js`, `tests/viewmodel.test.js`, `tests/weaponLibraryGlb.test.js`.

- [ ] **Passo 1: Testes** — `handSides(info)` dá os dois lados para a AK com pega (e nenhum para arma realista sem
  pega); `info.pega` vem de `lerPega`; o viewmodel usa os braços de luva na AK e os de massinha na Glock; a facção vem
  do time (`cl_bracadeira tr|ct`) e, sem time, da do boneco (Massa Crua); a braçadeira só aparece com time; trocar de
  facção troca os materiais sem recriar a malha; `status()` diz `braços: luvas` ou `massinha`; a esfera da sombra
  própria cobre as duas mãos de luva; os cotovelos do `rifle` deixam o pulso dos dois lados dentro dos limites
  (`colocar` sem aviso) nas três posições prontas do CS.
- [ ] **Passo 2: Ver falhar**; **Passo 3: implementar** (o `viewmodel.js` continua abaixo de ~600 linhas: a escolha
  entre luvas e massinha fica num módulo próprio se precisar); **Passo 4: ver passar**; suíte inteira.


**Código da tarefa** (a versão verificada no navegador e no Blender; os blocos `file=` são o arquivo inteiro, os pares são aplicados na ordem).

- [ ] **Os testes** — `tests/viewmodelLuvas.test.js`, `tests/weaponLibraryGlb.test.js`:

```js file=tests/viewmodelLuvas.test.js
// O viewmodel com as luvas (Fase 4.1b; plano, Tarefa 10), sem GPU: a AK de verdade (o .glb pela biblioteca de armas,
// com o GLTFLoader do vendor e o Draco sem Workers) e as luvas de verdade (LuvasSource), a Glock de massinha falsa.
// `handSides` dá os dois lados para a AK com pega e nenhum para a realista sem pega; `info.pega` vem do .glb; o
// viewmodel segura a AK com as luvas e a Glock com os braços de massinha; a facção vem do time (`cl_bracadeira`) e,
// sem time, da do boneco; a braçadeira só com time; a facção troca os materiais sem recriar a malha; `status()` diz
// os braços; a esfera da sombra própria cobre as duas mãos de luva; e os cotovelos do `rifle` deixam o pulso dos dois
// lados dentro dos limites da AAOS nas três posições prontas do CS.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import * as THREE from 'three';
import { Config } from '../src/core/config.js';
import { EventBus } from '../src/core/events.js';
import { ARMAS } from '../src/data/armas/index.js';
import { CONFIG_SCHEMA } from '../src/data/configSchema.js';
import { LUVAS } from '../src/data/luvas.js';
import { VIEWMODEL } from '../src/data/viewmodel.js';
import { LuvasSource } from '../src/characters/hands/luvasSource.js';
import { WeaponLibrary } from '../src/weapons/model/weaponLibrary.js';
import {
  applyViewmodelPreset, categoryPlacement, gloveFaction, gloveTarget, handSides, viewmodelVerticalFov,
} from '../src/weapons/viewmodel/placement.js';
import { Viewmodel } from '../src/weapons/viewmodel/viewmodel.js';
import { RAIZ, carregarGlbNoNode, decodificadorDraco, sdfDeTeste } from './luvasTestUtils.js';

const MM = 25.4;
let draco = null;

const json = (arquivo) => JSON.parse(readFileSync(join(RAIZ, arquivo), 'utf8'));

function carregadores() {
  return {
    async glb(url) {
      const caminho = decodeURIComponent(new URL(url).pathname).replace(/^\/([A-Za-z]:)/, '$1');
      return carregarGlbNoNode(caminho.split('?')[0], draco);
    },
    async textura() {
      return new THREE.Texture();
    },
    async json(url) {
      const caminho = decodeURIComponent(new URL(url).pathname).replace(/^\/([A-Za-z]:)/, '$1').split('?')[0];
      return JSON.parse(readFileSync(caminho, 'utf8'));
    },
  };
}

/** As armas: a AK pela biblioteca de verdade (origem glb); a Glock de massinha falsa (a receita, uma caixa). */
function armas() {
  const lib = new WeaponLibrary({ sdf: null, carregadores: carregadores() });
  const glockInfo = { id: 'glock', source: 'massinha', category: 'pistola', hands: true, anchors: ARMAS.glock.anchors, radius: 5 };
  return {
    lib,
    has: (id) => id === 'ak47' || id === 'glock',
    source: (id) => (id === 'ak47' ? 'glb' : 'massinha'),
    describe: (id) => (id === 'ak47' ? lib.describe(id) : Promise.resolve(glockInfo)),
    info: (id) => (id === 'ak47' ? lib.info(id) : glockInfo),
    instance: async (id, o) => {
      if (id === 'ak47') return lib.instance(id, o);
      const g = new THREE.Mesh(new THREE.BoxGeometry(6, 3, 1), new THREE.MeshBasicMaterial());
      g.userData.weapon = { id: 'glock', radius: 5 };
      return g;
    },
  };
}

function maosDeMassinha() {
  const criadas = [];
  return {
    criadas,
    async createArm(side) {
      const mesh = new THREE.Object3D();
      mesh.name = `braco-${side}`;
      const arm = { side, mesh, poses: [], faixa: undefined, setPose(p) { this.poses.push(p); }, setArmband(c) { this.faixa = c; }, place() {}, dispose() {} };
      criadas.push(arm);
      return arm;
    },
  };
}

async function montar() {
  draco ??= await decodificadorDraco();
  const events = new EventBus();
  const config = new Config(CONFIG_SCHEMA, { events });
  const render = {
    renderer: { compileAsync: async () => {}, shadowMap: { enabled: false, needsUpdate: false } },
    pipeline: { addLayer: () => () => {} }, shadowLevel: 0,
  };
  const luvas = new LuvasSource({ carregadores: carregadores(), sdf: sdfDeTeste(24) });
  const weapons = armas();
  const vm = new Viewmodel({ render, weapons, hands: maosDeMassinha(), luvas, config, events });
  const camera = new THREE.PerspectiveCamera(74, 16 / 9, 0.5, 400);
  return { vm, config, luvas, weapons, camera };
}

/** Quadros até o item pedido estar na mão (as cargas são promessas). */
async function segurar(vm, camera, item) {
  for (let i = 0; i < 400; i++) {
    vm.frame(camera, 1 / 60, { item, visible: true });
    if (vm.status().item === item && vm.layer.visible) return;
    await new Promise((r) => setTimeout(r, 5));
  }
  throw new Error(`o viewmodel não segurou ${item}`);
}

test('placement: o alvo do osso mao pela pega e a facção das luvas pelo time', () => {
  const pl = { position: new THREE.Vector3(1, -2, -9), quaternion: new THREE.Quaternion().setFromEuler(new THREE.Euler(0.1, 1.5, -0.05)) };
  const mao = { posicao: new THREE.Vector3(-4, -3, 2), quaternion: new THREE.Quaternion().setFromEuler(new THREE.Euler(-1, 0.4, 2)) };
  const a = gloveTarget(pl, mao);
  const m = new THREE.Matrix4().compose(pl.position, pl.quaternion, new THREE.Vector3(1, 1, 1));
  assert.ok(a.position.distanceTo(mao.posicao.clone().applyMatrix4(m)) < 1e-12);
  assert.ok(1 - Math.abs(a.quaternion.dot(pl.quaternion.clone().multiply(mao.quaternion))) < 1e-12);
  assert.equal(gloveFaction('tr'), 'massaCrua');
  assert.equal(gloveFaction('ct'), 'tropa');
  assert.equal(gloveFaction(null), 'massaCrua', 'sem time, a do boneco de referência');
  assert.equal(gloveFaction(null, 'tropa'), 'tropa');
});

test('viewmodel: a AK com pega nos dois lados, a info.pega do .glb; a realista sem pega sem mãos', async () => {
  const { weapons } = await montar();
  const info = await weapons.describe('ak47');
  assert.equal(info.hands, true);
  assert.deepEqual(handSides(info), ['direita', 'esquerda']);
  const rel = json('assets/armas/ak47/ak47.relatorio.json');
  assert.equal(info.pega.marca.d, json(`${LUVAS.pasta}luvas.relatorio.json`).marca.d, 'a marca do rig da AK é a das luvas');
  assert.ok(info.pega.dedos.d.indicador_1 && info.pega.dedos.e.minimo_3);
  assert.ok(info.pega.maos.d.posicao.isVector3 && info.pega.maos.e.quaternion.isQuaternion);
  assert.ok(rel.empunhadura?.d, 'o relatório com a empunhadura');
  assert.deepEqual(handSides({ ...info, hands: false, pega: null }), []);
});

test('viewmodel: luvas na AK, massinha na Glock, e o status diz os braços', async () => {
  const { vm, camera } = await montar();
  await segurar(vm, camera, 'ak47');
  let s = vm.status();
  assert.equal(s.bracos, 'luvas');
  assert.deepEqual(s.arms, ['direita', 'esquerda']);
  assert.equal(s.faccao, 'massaCrua');
  assert.ok(vm.gloves.bracos.direita.grupo.parent === vm.root, 'os braços de luva no referencial da câmera');
  await segurar(vm, camera, 'glock');
  s = vm.status();
  assert.equal(s.bracos, 'massinha');
  assert.deepEqual(vm.gloves.visiveis(), [], 'as luvas somem com a Glock');
  vm.frame(camera, 1 / 60, { item: 'glock', visible: true });
  assert.deepEqual(vm.status().arms, ['direita', 'esquerda']);
  await segurar(vm, camera, 'ak47');
  assert.equal(vm.status().bracos, 'luvas');
  vm.dispose();
});

test('viewmodel: a facção das luvas pelo time (e a do boneco sem time), a braçadeira só com time, as malhas ficam', async () => {
  const { vm, camera, config } = await montar();
  await segurar(vm, camera, 'ak47');
  const d = vm.gloves.bracos.direita;
  const malhas = d.malhas.slice();
  const nomes = () => d.malhas.map((m) => m.material.name).sort();
  assert.deepEqual(nomes(), ['luvas:massaCrua:couro', 'luvas:massaCrua:reforco', 'luvas:massaCrua:tecido']);
  assert.equal(d.bracadeira.visible, false, 'sem time, sem braçadeira');
  config.set('debug.armband', 'ct');
  await vm.gloves.setFaccao(vm.gloves.faccao); // espera os materiais da facção nova
  assert.equal(vm.status().faccao, 'tropa');
  assert.deepEqual(nomes(), ['luvas:tropa:couro', 'luvas:tropa:reforco', 'luvas:tropa:tecido']);
  assert.deepEqual(d.malhas, malhas, 'as malhas são as mesmas');
  assert.equal(d.bracadeira.visible, true);
  config.set('debug.armband', 'tr');
  await vm.gloves.setFaccao(vm.gloves.faccao);
  assert.equal(vm.status().faccao, 'massaCrua');
  assert.equal(vm.gloves.bracos.esquerda.bracadeira.visible, true);
  config.set('debug.armband', 'off');
  await vm.gloves.setFaccao(vm.gloves.faccao);
  assert.equal(vm.status().faccao, 'massaCrua');
  assert.equal(d.bracadeira.visible, false);
  vm.dispose();
});

test('viewmodel: a esfera da sombra própria cobre as duas mãos de luva inteiras', async () => {
  const { vm, camera } = await montar();
  await segurar(vm, camera, 'ak47');
  vm.frame(camera, 1 / 60, { item: 'ak47', visible: true });
  for (const lado of ['direita', 'esquerda']) {
    const b = vm.gloves.bracos[lado];
    b.grupo.updateMatrix();
    const pts = b.posicoesMM;
    let fora = 0;
    for (let v = 0; v < pts.length / 3; v++) {
      if (pts[v * 3] < -45) continue; // o antebraço e o punho saem da tela: a esfera é das mãos
      const p = new THREE.Vector3(pts[v * 3] / MM, pts[v * 3 + 1] / MM, pts[v * 3 + 2] / MM).applyMatrix4(b.grupo.matrix);
      if (!vm.localSphere.containsPoint(p)) fora++;
    }
    assert.equal(fora, 0, `${lado}: ${fora} vértices da mão fora da esfera da sombra própria`);
  }
  vm.dispose();
});

test('viewmodel: os cotovelos do rifle deixam os dois pulsos nos limites da AAOS nas três posições prontas do CS', async () => {
  const { vm, camera, config } = await montar();
  await segurar(vm, camera, 'ak47');
  for (const id of Object.keys(VIEWMODEL.presets)) {
    applyViewmodelPreset(config, id);
    vm.frame(camera, 1 / 60, { item: 'ak47', visible: true });
    const { avisos } = vm.status();
    assert.deepEqual(avisos, { direita: [], esquerda: [] }, `posição ${id}: ${JSON.stringify(avisos)}`);
    // e com folga: nenhum ângulo a mais de 93 % do limite (na P2 a supinação da esquerda ficava a 97 %, 77,8° de 80°)
    for (const lado of ['direita', 'esquerda']) {
      const { angulos: a, limites: l } = vm.gloves.bracos[lado];
      const razoes = {
        flexao: a.flexao >= 0 ? a.flexao / l.pulso.flexao : -a.flexao / l.pulso.extensao,
        desvio: a.desvio >= 0 ? a.desvio / l.pulso.radial : -a.desvio / l.pulso.ulnar,
        pronacao: a.pronacao >= 0 ? a.pronacao / l.antebraco.pronacao : -a.pronacao / l.antebraco.supinacao,
      };
      for (const [k, r] of Object.entries(razoes)) assert.ok(r <= 0.93, `posição ${id}, ${lado}: ${k} a ${(100 * r).toFixed(0)} % do limite`);
    }
    // o cotovelo de verdade (o osso antebraco) fora da tela em 16:9 e 21:9 e abaixo do pulso
    const fovV = viewmodelVerticalFov(VIEWMODEL.presets[id].fov);
    const t = Math.tan((fovV * Math.PI) / 360);
    for (const lado of ['direita', 'esquerda']) {
      const b = vm.gloves.bracos[lado];
      b.grupo.updateMatrixWorld(true);
      const inv = vm.root.matrixWorld.clone().invert();
      const cotovelo = b.ossos.antebraco.getWorldPosition(new THREE.Vector3()).applyMatrix4(inv);
      const pulso = b.ossos.mao.getWorldPosition(new THREE.Vector3()).applyMatrix4(inv);
      assert.ok(cotovelo.y < pulso.y, `posição ${id}, ${lado}: o cotovelo acima do pulso`);
      for (const aspect of [16 / 9, 21 / 9]) {
        const naTela = cotovelo.z < -VIEWMODEL.near && Math.abs(cotovelo.x / (-cotovelo.z * t * aspect)) < 1 && Math.abs(cotovelo.y / (-cotovelo.z * t)) < 1;
        assert.ok(!naTela, `posição ${id}, ${lado}: o cotovelo aparece em ${aspect.toFixed(2)}`);
      }
    }
  }
  // as categorias sem cotovelos de luva usam os de massinha
  assert.deepEqual(categoryPlacement('pistola').gloveElbows, categoryPlacement('pistola').elbows);
  assert.deepEqual(categoryPlacement('rifle').gloveElbows, { direita: [13.1, -8.2, 13.9], esquerda: [-9.9, -52.4, -9.7] });
  vm.dispose();
});

test('viewmodel: a facção das luvas forçada pela bancada vale sobre a do time e sai quando solta', async () => {
  const { vm, camera, config } = await montar();
  await segurar(vm, camera, 'ak47');
  config.set('debug.armband', 'tr');
  vm.frame(camera, 1 / 60, { item: 'ak47', visible: true, gloves: 'tropa' });
  await vm.gloves.setFaccao(vm.gloves.faccao);
  assert.equal(vm.status().faccao, 'tropa', 'a bancada escolheu a Tropa com o time TR');
  assert.ok(vm.gloves.bracos.direita.malhas.every((m) => m.material.name.startsWith('luvas:tropa:')));
  vm.frame(camera, 1 / 60, { item: 'ak47', visible: true, gloves: null });
  await vm.gloves.setFaccao(vm.gloves.faccao);
  assert.equal(vm.status().faccao, 'massaCrua', 'solta: a do time');
  vm.dispose();
});
```

Em `tests/weaponLibraryGlb.test.js`, trocar:

```
  assert.equal(info.category, 'rifle');
  assert.equal(info.hands, false);
  assert.deepEqual(info.parts, ['ferrolho', 'carregador', 'gatilho', 'cao', 'seletor']);
```

por:

```
  assert.equal(info.category, 'rifle');
  // a cena falsa não tem a pega das luvas (um .glb de antes da 4.1b): sem braços (a AK de verdade: viewmodelLuvas.test.js)
  assert.equal(info.hands, false);
  assert.equal(info.pega, null);
  assert.deepEqual(info.parts, ['ferrolho', 'carregador', 'gatilho', 'cao', 'seletor']);
```

Em `tests/weaponLibraryGlb.test.js`, trocar:

```
  assert.equal(ZONAS.length, 5);
});

```

por:

```
  assert.equal(ZONAS.length, 5);
});

test('weaponModels: o .glb de rifle sem a pega das luvas aparece sem braços, com o erro no log pedindo a reconstrução', async () => {
  const erros = [];
  const { lib } = nova({ log: { error: (m) => erros.push(m), debug() {}, warn() {} } });
  const info = await lib.describe('ak47');
  assert.equal(info.hands, false);
  assert.equal(info.pega, null);
  assert.equal(erros.length, 1);
  assert.match(erros[0], /arma ak47: sem a pega das luvas \(construa a arma de novo no Blender\)/);
});

```

Run: `node --test tests/viewmodelLuvas.test.js tests/weaponLibraryGlb.test.js`
Expected: FAIL — # tests 7 # pass 4 # fail 3 .

- [ ] **A implementação** — `src/weapons/viewmodel/bracosLuva.js`, `src/data/viewmodel.js`, `src/weapons/viewmodel/placement.js`, `src/weapons/viewmodel/viewmodel.js`, `src/weapons/model/glbSource.js`, `src/modes/matchState.js`:

```js file=src/weapons/viewmodel/bracosLuva.js
// Os braços de luva do viewmodel (Fase 4.1b; desenho em docs/superpowers/specs/2026-09-26-4.1b-luvas-e-empunhadura-
// design.md, seção 7.4; plano, Tarefa 10): os dois braços da LuvasSource (serviço `luvasModels`) na mão das armas
// realistas com pega. A pega do .glb da arma põe os dedos (a marca do rig conferida), cada osso `mao` vai para o
// referencial dele na pega (a pose da arma na câmera), o antebraço aponta para o cotovelo da categoria com o polegar
// para cima na meia pronação, a pintura é a da facção (a do time, ou a do boneco sem time) e a braçadeira só aparece
// com time. As variantes de shader compilam antes de o braço aparecer (sem travada).

import * as THREE from 'three';
import { GLOVE_SIDE, gloveTarget } from './placement.js';

const SIDES = Object.freeze(['direita', 'esquerda']);
const CIMA = Object.freeze(new THREE.Vector3(0, 1, 0));
const MM_POR_U = 25.4;

export class BracosDeLuva {
  #luvas;
  #log;
  #corDaMassa;
  #pronto = null;
  #descartado = false;
  #alvo = { position: new THREE.Vector3(), quaternion: new THREE.Quaternion() };

  /**
   * @param {{luvas:import('../../characters/hands/luvasSource.js').LuvasSource, log?:object|null, corDaMassa:string,
   *   faccao:string}} deps
   */
  constructor({ luvas, log = null, corDaMassa, faccao }) {
    this.#luvas = luvas;
    this.#log = log;
    this.#corDaMassa = corDaMassa;
    this.faccao = faccao;
    this.bracadeira = null;
    this.bracos = { direita: null, esquerda: null };
    this.pega = null;
    this.avisos = { direita: [], esquerda: [] };
  }

  get prontos() {
    return Boolean(this.bracos.direita && this.bracos.esquerda);
  }

  /** Alcance da mão de luva a partir do pulso (u): a ponta do médio com o tecido e o couro da ponta. */
  get alcance() {
    const f = this.#luvas.ficha;
    return f ? (f.mao.comprimento.mm + f.luva.tecido + f.luva.couro) / MM_POR_U : 0;
  }

  /**
   * Cria os dois braços uma vez, presos em `pai` e escondidos; `compilar(objeto)` compila as variantes de shader deles
   * antes (o compile do three só percorre o que está visível).
   * @param {THREE.Object3D} pai @param {(o:THREE.Object3D)=>Promise<void>} [compilar]
   */
  garantir(pai, compilar = null) {
    if (!this.#pronto) {
      const p = Promise.all(SIDES.map((s) => this.#luvas.instanciar(GLOVE_SIDE[s], this.faccao, { corDaMassa: this.#corDaMassa })))
        .then(async (bracos) => {
          if (this.#descartado) {
            for (const b of bracos) b.dispose();
            throw new Error('viewmodel descartado');
          }
          SIDES.forEach((s, i) => {
            const b = bracos[i];
            b.setBracadeira(this.bracadeira);
            pai.add(b.grupo);
            this.bracos[s] = b;
          });
          // visíveis (como nasceram) para o compile; escondidos até a arma com pega entrar na mão
          if (compilar) for (const b of bracos) await compilar(b.grupo);
          for (const b of bracos) b.grupo.visible = false;
          // a facção pode ter mudado durante a carga
          await this.setFaccao(this.faccao);
        });
      p.catch((err) => {
        if (this.#pronto === p) this.#pronto = null;
        if (!this.#descartado) this.#log?.error?.('viewmodel: braços de luva', err);
      });
      this.#pronto = p;
    }
    return this.#pronto;
  }

  /** Os dedos na pega da arma nos dois braços; false (e o erro no log) se a pega é de outro rig. */
  aplicarPega(pega) {
    try {
      for (const s of SIDES) this.bracos[s].aplicarPega(pega);
      this.pega = pega;
      return true;
    } catch (err) {
      this.pega = null;
      this.#log?.error?.(`viewmodel: ${err?.message ?? err}`);
      return false;
    }
  }

  /**
   * Põe os braços nos lados pedidos: o osso `mao` na pega (pela pose da arma) e o antebraço para o cotovelo.
   * @param {{position:THREE.Vector3, quaternion:THREE.Quaternion}} placement a pose da arma na câmera
   * @param {(side:string)=>THREE.Vector3} cotovelo o cotovelo de cada lado no referencial da câmera
   * @param {Set<string>} lados
   * @returns {THREE.Vector3[]} os pulsos (para a esfera da sombra própria)
   */
  colocar(placement, cotovelo, lados) {
    const pulsos = [];
    for (const s of SIDES) {
      const b = this.bracos[s];
      if (!b) continue;
      b.grupo.visible = Boolean(this.pega && lados.has(s));
      if (!b.grupo.visible) continue;
      const alvo = gloveTarget(placement, this.pega.maos[GLOVE_SIDE[s]], this.#alvo);
      this.avisos[s] = b.colocar(alvo.position, alvo.quaternion, cotovelo(s), CIMA).avisos;
      pulsos.push(alvo.position.clone());
    }
    return pulsos;
  }

  /** Esconde os dois braços (a arma saiu da mão ou é de massinha). */
  esconder() {
    for (const s of SIDES) if (this.bracos[s]) this.bracos[s].grupo.visible = false;
  }

  /** Lados visíveis agora. */
  visiveis() {
    return SIDES.filter((s) => this.bracos[s]?.grupo.visible);
  }

  /** A pintura das luvas pela facção (os materiais trocam; as malhas ficam). */
  async setFaccao(faccao) {
    this.faccao = faccao;
    await Promise.all(SIDES.map((s) => this.bracos[s]?.setFaccao(faccao)));
  }

  /** Braçadeira do time: cor ou null. */
  setBracadeira(cor) {
    this.bracadeira = cor;
    for (const s of SIDES) this.bracos[s]?.setBracadeira(cor);
  }

  dispose() {
    this.#descartado = true;
    for (const s of SIDES) {
      this.bracos[s]?.dispose();
      this.bracos[s] = null;
    }
    this.pega = null;
  }
}
```

Em `src/data/viewmodel.js`, trocar:

```
   * (o cotovelo real fica no alinhamento, a um antebraço do pulso).
   */
```

por:

```
   * (o cotovelo real fica no alinhamento, a um antebraço do pulso).
   * `gloveElbows` (Fase 4.1b) = os mesmos alvos para os braços de luva, nas categorias das armas com pega (sem ele, os
   * `elbows`): o braço realista tem o pulso e o antebraço com os limites da AAOS. Achados por varredura das direções do
   * antebraço com a pega da AK de verdade — o cotovelo fora da tela em 16:9 e 21:9, abaixo do pulso e o antebraço a
   * mais de 3 mm da arma, nas três posições prontas do CS: a mão do gatilho com o menor Σ(ângulo/limite)² — 11–19° de
   * extensão e 9–13° de desvio ulnar (a pegada do punho de pistola) e o antebraço na meia pronação; a da frente, desde a
   * pega em C do CS:GO (2026-09-27: o polegar reto e deitado no lado esquerdo, os quatro dedos no direito), com o menor
   * pior ângulo em relação ao limite (minimax — a soma dos quadrados trocava extensão por supinação e a deixava a 79,9°
   * de 80°): 68–72° de supinação, 60–62° de extensão e 14–18° de desvio radial, todos a no máximo 91 % do limite (na
   * P2, a pega antiga pedia 77,8° de supinação, 97 %), com o antebraço a 6,6 mm da arma. A palma para cima debaixo do
   * guarda-mão pede muita supinação: o braço pendente é a referência da torção (o polegar para cima da câmera). Uma
   * referência pelo ombro (o úmero) não serve: as posições do viewmodel são estilizadas como as do CS (a mão do gatilho
   * a 16 cm do ombro, o cotovelo do apoio 44 cm à frente do olho) e a torção passava de 100°.
   */
```

Em `src/data/viewmodel.js`, trocar:

```
    pistola: F({ pos: F([1.8, -0.9, -13.5]), angles: F([3, 4, -2]), elbows: F({ direita: F([12, -20, 2]), esquerda: F([-10, -20, 0]) }) }),
    rifle: F({ pos: F([4.5, -3.1, -9]), angles: F([4, 1, -2]), elbows: F({ direita: F([15, -18, 6]), esquerda: F([-18, -16, -4]) }) }),
    sniper: F({ pos: F([5, -4.1, -9.6]), angles: F([3.5, 1, -1.5]), elbows: F({ direita: F([15, -18, 6]), esquerda: F([-18, -17, -8]) }) }),
```

por:

```
    pistola: F({ pos: F([1.8, -0.9, -13.5]), angles: F([3, 4, -2]), elbows: F({ direita: F([12, -20, 2]), esquerda: F([-10, -20, 0]) }) }),
    rifle: F({
      pos: F([4.5, -3.1, -9]), angles: F([4, 1, -2]), elbows: F({ direita: F([15, -18, 6]), esquerda: F([-18, -16, -4]) }),
      gloveElbows: F({ direita: F([13.1, -8.2, 13.9]), esquerda: F([-9.9, -52.4, -9.7]) }),
    }),
    sniper: F({ pos: F([5, -4.1, -9.6]), angles: F([3.5, 1, -1.5]), elbows: F({ direita: F([15, -18, 6]), esquerda: F([-18, -17, -8]) }) }),
```

Em `src/weapons/viewmodel/placement.js`, trocar:

```
 * Posição de uma categoria com um ajuste por cima (o `viewmodel_ajuste` do console afina os dados ao vivo).
 * @param {string} category
 * @param {{pos?:number[], angles?:number[], elbows?:{direita?:number[], esquerda?:number[]}}|null} [tune]
 */
```

por:

```
 * Posição de uma categoria com um ajuste por cima (o `viewmodel_ajuste` do console afina os dados ao vivo).
 * `gloveElbows`: os cotovelos dos braços de luva (sem os da categoria, os `elbows`).
 * @param {string} category
 * @param {{pos?:number[], angles?:number[], elbows?:{direita?:number[], esquerda?:number[]},
 *   gloveElbows?:{direita?:number[], esquerda?:number[]}}|null} [tune]
 */
```

Em `src/weapons/viewmodel/placement.js`, trocar:

```
  if (!base) throw new Error(`categoria de viewmodel desconhecida: ${category}`);
  return {
```

por:

```
  if (!base) throw new Error(`categoria de viewmodel desconhecida: ${category}`);
  const elbows = { direita: tune?.elbows?.direita ?? base.elbows.direita, esquerda: tune?.elbows?.esquerda ?? base.elbows.esquerda };
  const luva = base.gloveElbows ?? base.elbows;
  return {
```

Em `src/weapons/viewmodel/placement.js`, trocar:

```
    angles: tune?.angles ?? base.angles,
    elbows: { direita: tune?.elbows?.direita ?? base.elbows.direita, esquerda: tune?.elbows?.esquerda ?? base.elbows.esquerda },
  };
```

por:

```
    angles: tune?.angles ?? base.angles,
    elbows,
    gloveElbows: { direita: tune?.gloveElbows?.direita ?? luva.direita, esquerda: tune?.gloveElbows?.esquerda ?? luva.esquerda },
  };
```

Em `src/weapons/viewmodel/placement.js`, trocar:

```
}

/**
 * Mãos que a arma usa: as âncoras `maoDireita`/`maoEsquerda` (a faca só tem a direita); nenhuma na arma realista sem
```

por:

```
}

/** Cotovelo do braço de luva de um lado, no referencial da câmera. */
export function gloveElbowTarget(category, side, tune = null, out = new THREE.Vector3()) {
  return out.fromArray(categoryPlacement(category, tune).gloveElbows[side]);
}

/**
 * Mãos que a arma usa: as âncoras `maoDireita`/`maoEsquerda` (a faca só tem a direita); nenhuma na arma realista sem
```

Em `src/weapons/viewmodel/placement.js`, trocar:

```
export const HAND_ANCHOR = Object.freeze({ direita: 'maoDireita', esquerda: 'maoEsquerda' });

/**
 * Facção do acento da arma na mão: as de um lado só (Glock, AK, M4A4...) ficam com o seu; as dos dois lados pegam o
```

por:

```
export const HAND_ANCHOR = Object.freeze({ direita: 'maoDireita', esquerda: 'maoEsquerda' });

/** O braço de luva de cada lado do viewmodel. */
export const GLOVE_SIDE = Object.freeze({ direita: 'd', esquerda: 'e' });

/**
 * Onde vai o osso `mao` de uma luva, no referencial da câmera, dada a pose da arma: o pulso e a rotação do referencial
 * do osso na pega (`info.pega.maos[lado]`, no referencial da raiz da arma).
 * @param {{position:THREE.Vector3, quaternion:THREE.Quaternion}} placement
 * @param {{posicao:THREE.Vector3, quaternion:THREE.Quaternion}} mao
 */
export function gloveTarget(placement, mao, out = { position: new THREE.Vector3(), quaternion: new THREE.Quaternion() }) {
  out.position.copy(mao.posicao).applyQuaternion(placement.quaternion).add(placement.position);
  out.quaternion.copy(placement.quaternion).multiply(mao.quaternion);
  return out;
}

/**
 * A facção das luvas: a do time da partida (Massa Crua no TR, Tropa do Estúdio no CT) ou, sem time, a do boneco (Massa
 * Crua no de referência até o criador da Fase 5).
 * @param {'tr'|'ct'|null} team @param {string} [dollFaction]
 */
export function gloveFaction(team, dollFaction = 'massaCrua') {
  if (team === 'tr') return 'massaCrua';
  if (team === 'ct') return 'tropa';
  return dollFaction;
}

/**
 * Facção do acento da arma na mão: as de um lado só (Glock, AK, M4A4...) ficam com o seu; as dos dois lados pegam o
```

Em `src/weapons/viewmodel/viewmodel.js`, trocar:

```
// (viewmodelLights.js). A arma fica na posição da categoria (src/data/viewmodel.js) mais os offsets; nas de massinha,
// cada mão vai para a âncora da receita com a pose da âncora e o antebraço aponta para um cotovelo fixo fora da tela; a
// realista (o .glb do Blender, com o reflexo do set) aparece sem braços até as luvas da 4.1b. Ainda não anima (4.3).
// Tudo sai do `info(id)` da biblioteca de armas, o mesmo para as duas origens. Quem decide o que segurar e quando
```

por:

```
// (viewmodelLights.js). A arma fica na posição da categoria (src/data/viewmodel.js) mais os offsets; nas de massinha,
// cada mão vai para a âncora da receita com a pose da âncora e o antebraço aponta para um cotovelo fixo fora da tela.
// Fase 4.1b: a realista com pega (o .glb do Blender, com o reflexo do set) é segurada pelas luvas (bracosLuva.js: a pega
// da arma nos dedos, o osso `mao` no referencial da pega, a facção do time ou a do boneco, a braçadeira só com time); a
// realista sem pega aparece sem braços. Ainda não anima (4.3).
// Tudo sai do `info(id)` da biblioteca de armas, o mesmo para as duas origens. Quem decide o que segurar e quando
```

Em `src/weapons/viewmodel/viewmodel.js`, trocar:

```
import { ViewmodelLights } from './viewmodelLights.js';
import {
  HAND_ANCHOR, anchorPose, categoryPlacement, elbowTarget, handSides, viewCategory, viewFaction, viewPlacement,
  viewmodelVerticalFov, weaponNudge,
} from './placement.js';
```

por:

```
import { ViewmodelLights } from './viewmodelLights.js';
import { BracosDeLuva } from './bracosLuva.js';
import {
  HAND_ANCHOR, anchorPose, categoryPlacement, elbowTarget, gloveElbowTarget, gloveFaction, handSides, viewCategory, viewFaction,
  viewPlacement, viewmodelVerticalFov, weaponNudge,
} from './placement.js';
```

Em `src/weapons/viewmodel/viewmodel.js`, trocar:

```
   * @param {import('../../core/events.js').EventBus} deps.events
   * @param {object|null} [deps.log]
   * @param {string} [deps.armColor] massa dos braços (a do boneco; terracota no de referência)
   */
  constructor({ render, weapons, hands, config, events, log = null, armColor = PALETTE.terracotta }) {
    this.render = render;
```

por:

```
   * @param {import('../../core/events.js').EventBus} deps.events
   * @param {import('../../characters/hands/luvasSource.js').LuvasSource|null} [deps.luvas] as luvas das armas com pega
   * @param {object|null} [deps.log]
   * @param {string} [deps.armColor] massa dos braços (a do boneco; terracota no de referência)
   * @param {string} [deps.dollFaction] facção do boneco (a das luvas sem time; Massa Crua até o criador da Fase 5)
   */
  constructor({ render, weapons, hands, luvas = null, config, events, log = null, armColor = PALETTE.terracotta, dollFaction = 'massaCrua' }) {
    this.render = render;
```

Em `src/weapons/viewmodel/viewmodel.js`, trocar:

```
    this.hands = hands;
    this.config = config;
```

por:

```
    this.hands = hands;
    this.dollFaction = dollFaction;
    this.gloves = luvas ? new BracosDeLuva({ luvas, log, corDaMassa: armColor, faccao: gloveFaction(null, dollFaction) }) : null;
    this.armsKind = null; // 'luvas' | 'massinha' | null (a arma na mão)
    this.gloveOverride = null; // facção das luvas forçada (a bancada); null: a do time ou a do boneco
    this.config = config;
```

Em `src/weapons/viewmodel/viewmodel.js`, trocar:

```
    for (const side of SIDES) this.arms[side]?.setArmband(color);
    this.#invalidate(); // o acento das armas dos dois lados muda com o time
```

por:

```
    for (const side of SIDES) this.arms[side]?.setArmband(color);
    this.gloves?.setBracadeira(color);
    this.#applyGloveFaction();
    this.#invalidate(); // o acento das armas dos dois lados muda com o time
```

Em `src/weapons/viewmodel/viewmodel.js`, trocar:

```

  /** Esquece o pedido: o próximo quadro pede a arma de novo (receita relida, time trocado). */
```

por:

```

  /** A pintura das luvas: a forçada pela bancada ou, sem ela, a do time (ou a do boneco sem time). */
  #applyGloveFaction() {
    this.gloves?.setFaccao(this.gloveOverride ?? gloveFaction(this.team, this.dollFaction))
      .catch((err) => this.log?.error('viewmodel: facção das luvas', err));
  }

  /** Esquece o pedido: o próximo quadro pede a arma de novo (receita relida, time trocado). */
```

Em `src/weapons/viewmodel/viewmodel.js`, trocar:

```
    const [wid, wlod, wfaction] = key.split(':');
    // A realista vem sem braços até a 4.1b; as variantes de shader compilam antes de a arma aparecer (sem travada).
    const arms = this.weapons.source(wid) === 'glb' ? null : this.#ensureArms();
    Promise.all([this.weapons.instance(wid, { lod: wlod, faction: wfaction }), arms]).then(async ([instance]) => {
```

por:

```
    const [wid, wlod, wfaction] = key.split(':');
    // A realista com pega vem com as luvas (a outra, sem braços); as variantes de shader compilam antes de a arma e os
    // braços aparecerem (sem travada).
    const arms = this.weapons.source(wid) === 'glb' ? this.#glovesFor(wid) : this.#ensureArms();
    Promise.all([this.weapons.instance(wid, { lod: wlod, faction: wfaction }), arms]).then(async ([instance]) => {
```

Em `src/weapons/viewmodel/viewmodel.js`, trocar:

```

  /** Troca a arma da mão pela instância nova: centro e raio, as mãos que ela usa e as poses pela âncora, posição a refazer. */
```

por:

```

  /** Os braços de luva, se a arma realista tem pega (criados uma vez, compilados antes de aparecer). */
  #glovesFor(id) {
    return this.weapons.describe(id).then((info) => {
      if (!info?.pega || !this.gloves) return null;
      return this.gloves.garantir(this.root, (o) => this.render.renderer.compileAsync(o, this.camera, this.scene));
    });
  }

  /** Troca a arma da mão pela instância nova: centro e raio, as mãos que ela usa e as poses pela âncora, posição a refazer. */
```

Em `src/weapons/viewmodel/viewmodel.js`, trocar:

```
    this.sides = new Set(handSides(this.info));
    this.loadedKey = key;
```

por:

```
    this.sides = new Set(handSides(this.info));
    this.armsKind = this.sides.size ? (this.info.pega ? 'luvas' : 'massinha') : null;
    if (this.armsKind === 'luvas' && !(this.gloves?.prontos && this.gloves.aplicarPega(this.info.pega))) {
      this.sides = new Set(); // a pega de outro rig (o erro já foi ao log): a arma sem braços
      this.armsKind = null;
    }
    this.loadedKey = key;
```

Em `src/weapons/viewmodel/viewmodel.js`, trocar:

```
    this.holder.add(instance);
    for (const side of this.sides) {
      const anchor = this.#anchor(HAND_ANCHOR[side]);
      if (anchor) this.arms[side]?.setPose(anchor.pose ?? 'aberta');
    }
```

por:

```
    this.holder.add(instance);
    if (this.armsKind === 'massinha') {
      for (const side of this.sides) {
        const anchor = this.#anchor(HAND_ANCHOR[side]);
        if (anchor) this.arms[side]?.setPose(anchor.pose ?? 'aberta');
      }
    }
```

Em `src/weapons/viewmodel/viewmodel.js`, trocar:

```
    this.category = null;
    for (const side of SIDES) if (this.arms[side]) this.arms[side].mesh.visible = false;
  }
```

por:

```
    this.category = null;
    this.armsKind = null;
    for (const side of SIDES) if (this.arms[side]) this.arms[side].mesh.visible = false;
    this.gloves?.esconder();
  }
```

Em `src/weapons/viewmodel/viewmodel.js`, trocar:

```
    }
    for (const side of SIDES) {
      const arm = this.arms[side];
      const anchor = this.sides.has(side) ? this.#anchor(HAND_ANCHOR[side]) : null;
      if (!arm) continue;
      arm.mesh.visible = Boolean(anchor);
      if (!anchor) continue;
      const pose = anchorPose(pl, anchor, this._pose);
      arm.place(pose.position, pose.quaternion, elbowTarget(cat, side, this.tune[cat] ?? null, this._elbow));
      radius = Math.max(radius, pose.position.distanceTo(center) + HAND_REACH);
    }
```

por:

```
    }
    if (this.armsKind === 'luvas') {
      for (const side of SIDES) if (this.arms[side]) this.arms[side].mesh.visible = false;
      const tune = this.tune[cat] ?? null;
      const wrists = this.gloves.colocar(pl, (side) => gloveElbowTarget(cat, side, tune, new THREE.Vector3()), this.sides);
      for (const w of wrists) radius = Math.max(radius, w.distanceTo(center) + this.gloves.alcance);
    } else {
      this.gloves?.esconder();
      for (const side of SIDES) {
        const arm = this.arms[side];
        const anchor = this.sides.has(side) ? this.#anchor(HAND_ANCHOR[side]) : null;
        if (!arm) continue;
        arm.mesh.visible = Boolean(anchor);
        if (!anchor) continue;
        const pose = anchorPose(pl, anchor, this._pose);
        arm.place(pose.position, pose.quaternion, elbowTarget(cat, side, this.tune[cat] ?? null, this._elbow));
        radius = Math.max(radius, pose.position.distanceTo(center) + HAND_REACH);
      }
    }
```

Em `src/weapons/viewmodel/viewmodel.js`, trocar:

```
   * Um quadro. `item`: o que a mão segura (id, ou null); `visible`: a regra de quando aparece (placement.js) já
   * avaliada por quem chama; `faction`/`lod` forçam o acento e o nível (a bancada).
   * @param {THREE.PerspectiveCamera} camera câmera do jogador (já posta neste quadro)
   * @param {number} dt
   * @param {{item:string|null, visible:boolean, faction?:string|null, lod?:string}} state
   */
  frame(camera, dt, { item, visible, faction = null, lod = 'perto' }) {
    this.#want(item, { lod, faction });
    const show = Boolean(visible && this.weapon && (!this.sides.size || this.arms.direita) && this.loadedKey === this.itemKey);
    this.layer.visible = show;
```

por:

```
   * Um quadro. `item`: o que a mão segura (id, ou null); `visible`: a regra de quando aparece (placement.js) já
   * avaliada por quem chama; `faction`/`lod` forçam o acento e o nível (a bancada); `gloves` força a facção das luvas
   * (a bancada; null: a do time).
   * @param {THREE.PerspectiveCamera} camera câmera do jogador (já posta neste quadro)
   * @param {number} dt
   * @param {{item:string|null, visible:boolean, faction?:string|null, lod?:string, gloves?:string|null}} state
   */
  frame(camera, dt, { item, visible, faction = null, lod = 'perto', gloves = null }) {
    if (gloves !== this.gloveOverride) {
      this.gloveOverride = gloves;
      this.#applyGloveFaction();
    }
    this.#want(item, { lod, faction });
    const armsReady = this.armsKind === 'luvas' ? this.gloves?.prontos : this.arms.direita;
    const show = Boolean(visible && this.weapon && (!this.sides.size || armsReady) && this.loadedKey === this.itemKey);
    this.layer.visible = show;
```

Em `src/weapons/viewmodel/viewmodel.js`, trocar:

```

  /** Ajuste ao vivo da posição de uma categoria (viewmodel_ajuste): `pos`, `angles` ou `elbows.{lado}`. */
  setTune(category, patch) {
```

por:

```

  /** Ajuste ao vivo da posição de uma categoria (viewmodel_ajuste): `pos`, `angles`, `elbows.{lado}` ou `gloveElbows.{lado}`. */
  setTune(category, patch) {
```

Em `src/weapons/viewmodel/viewmodel.js`, trocar:

```
    const cur = this.tune[category] ?? {};
    this.tune[category] = { ...cur, ...patch, elbows: { ...(cur.elbows ?? {}), ...(patch.elbows ?? {}) } };
    this.dirty = true;
```

por:

```
    const cur = this.tune[category] ?? {};
    this.tune[category] = {
      ...cur, ...patch,
      elbows: { ...(cur.elbows ?? {}), ...(patch.elbows ?? {}) },
      gloveElbows: { ...(cur.gloveElbows ?? {}), ...(patch.gloveElbows ?? {}) },
    };
    this.dirty = true;
```

Em `src/weapons/viewmodel/viewmodel.js`, trocar:

```
    const f = (a) => `F([${a.map((v) => Number(v.toFixed(2))).join(', ')}])`;
    return `${category}: F({ pos: ${f(p.pos)}, angles: ${f(p.angles)}, elbows: F({ direita: ${f(p.elbows.direita)}, esquerda: ${f(p.elbows.esquerda)} }) }),`;
  }
```

por:

```
    const f = (a) => `F([${a.map((v) => Number(v.toFixed(2))).join(', ')}])`;
    const luva = VIEWMODEL.categories[category].gloveElbows || this.tune[category]?.gloveElbows?.direita || this.tune[category]?.gloveElbows?.esquerda
      ? `, gloveElbows: F({ direita: ${f(p.gloveElbows.direita)}, esquerda: ${f(p.gloveElbows.esquerda)} })` : '';
    return `${category}: F({ pos: ${f(p.pos)}, angles: ${f(p.angles)}, elbows: F({ direita: ${f(p.elbows.direita)}, esquerda: ${f(p.elbows.esquerda)} })${luva} }),`;
  }
```

Em `src/weapons/viewmodel/viewmodel.js`, trocar:

```
      item: this.loadedKey?.split(':')[0] ?? null, wanted: this.itemKey, category: this.category, visible: this.layer.visible,
      team: this.team, arms: SIDES.filter((s) => this.arms[s]?.mesh.visible),
    };
```

por:

```
      item: this.loadedKey?.split(':')[0] ?? null, wanted: this.itemKey, category: this.category, visible: this.layer.visible,
      team: this.team,
      arms: this.armsKind === 'luvas' ? this.gloves.visiveis() : SIDES.filter((s) => this.arms[s]?.mesh.visible),
      bracos: this.armsKind, faccao: this.gloves?.faccao ?? null, avisos: this.armsKind === 'luvas' ? this.gloves.avisos : null,
    };
```

Em `src/weapons/viewmodel/viewmodel.js`, trocar:

```
    }
    this.lights.dispose();
```

por:

```
    }
    this.gloves?.dispose();
    this.lights.dispose();
```

Em `src/weapons/model/glbSource.js`, trocar:

```
// são injetados: no navegador, o GLTFLoader do vendor e o TextureLoader; no Node, falsos.

```

por:

```
// são injetados: no navegador, o GLTFLoader do vendor e o TextureLoader; no Node, falsos.
// Fase 4.1b: nas categorias com regra de pega (CATEGORIAS_COM_PEGA), o `info.pega` (pegaDoGltf: a marca do rig, os dedos
// do clipe `empunhadura` e o referencial do osso `mao` de cada lado) e `hands: true` — o viewmodel segura com as luvas.
// Sem a pega no .glb (construído antes das luvas) a arma aparece sem braços, com o erro no log.

```

Em `src/weapons/model/glbSource.js`, trocar:

```
import { ARMAS_REAIS, LODS_REAIS, TEXTURAS_DO_LOD } from '../../data/armasReais.js';
import { VIEWMODEL } from '../../data/viewmodel.js';
import { FABRICA, chaveDaSkin, skinDeFabrica } from '../skins/skin.js';
```

por:

```
import { ARMAS_REAIS, LODS_REAIS, TEXTURAS_DO_LOD } from '../../data/armasReais.js';
import { CATEGORIAS_COM_PEGA } from '../../data/luvas.js';
import { VIEWMODEL } from '../../data/viewmodel.js';
import { pegaDoGltf } from '../../characters/hands/pega.js';
import { FABRICA, chaveDaSkin, skinDeFabrica } from '../skins/skin.js';
```

Em `src/weapons/model/glbSource.js`, trocar:

```
        const resumo = resumirGlb(gltf.scene, id);
        // O modelo carregado é o molde das instâncias e nunca vai à cena: as malhas dele guardam só a geometria, com um
```

por:

```
        const resumo = resumirGlb(gltf.scene, id);
        const pega = this.#pega(id, gltf);
        // O modelo carregado é o molde das instâncias e nunca vai à cena: as malhas dele guardam só a geometria, com um
```

Em `src/weapons/model/glbSource.js`, trocar:

```
        }
        const pronto = { resumo, info: this.#info(id, resumo, relatorio, validarFicha(ficha)), ms: now() - t0, neutro };
        this.#prontos.set(id, pronto);
```

por:

```
        }
        const pronto = { resumo, info: this.#info(id, resumo, relatorio, validarFicha(ficha), pega), ms: now() - t0, neutro };
        this.#prontos.set(id, pronto);
```

Em `src/weapons/model/glbSource.js`, trocar:

```

  #info(id, resumo, relatorio, ficha) {
    const a = ARMAS_REAIS[id];
```

por:

```

  /** A pega das luvas da arma (null na categoria sem regra de pega, ou com o erro no log se o .glb não a tem). */
  #pega(id, gltf) {
    if (!CATEGORIAS_COM_PEGA.includes(this.#categoria(id))) return null;
    try {
      return pegaDoGltf(gltf, id);
    } catch (e) {
      this.#log?.error?.(`arma ${id}: sem a pega das luvas (construa a arma de novo no Blender) — ${e?.message ?? e}`);
      return null;
    }
  }

  #categoria(id) {
    return VIEWMODEL.weapons[id]?.category ?? ARMAS_REAIS[id].categoria;
  }

  #info(id, resumo, relatorio, ficha, pega) {
    const a = ARMAS_REAIS[id];
```

Em `src/weapons/model/glbSource.js`, trocar:

```
    return {
      id, source: 'glb', category: VIEWMODEL.weapons[id]?.category ?? a.categoria,
      bounds: resumo.caixa, radius: max.distanceTo(min) / 2,
      anchors: ancorasDosSoquetes(resumo.soquetes), sockets: resumo.soquetes,
      hands: false, // as luvas chegam na 4.1b (plano da 4.1a, D7)
      plan: fichaParaPlanta(ficha), lengthU: ficha.medidas.comprimento.mm / MM_POR_U,
```

por:

```
    return {
      id, source: 'glb', category: this.#categoria(id),
      bounds: resumo.caixa, radius: max.distanceTo(min) / 2,
      anchors: ancorasDosSoquetes(resumo.soquetes), sockets: resumo.soquetes,
      hands: Boolean(pega), pega,
      plan: fichaParaPlanta(ficha), lengthU: ficha.medidas.comprimento.mm / MM_POR_U,
```

Em `src/modes/matchState.js`, trocar:

```
    this.hold = null; // "Segurar" da bancada de armas: {id, faction, lod} (câmera livre estacionada)
    this._vm = { item: null, visible: false, faction: null, lod: 'perto' }; // pedido do viewmodel neste quadro
    this.physicsDebug = null;
```

por:

```
    this.hold = null; // "Segurar" da bancada de armas: {id, faction, lod} (câmera livre estacionada)
    this._vm = { item: null, visible: false, faction: null, lod: 'perto', gloves: null }; // pedido do viewmodel neste quadro
    this.physicsDebug = null;
```

Em `src/modes/matchState.js`, trocar:

```
    this.viewmodel = new Viewmodel({
      render: s.render, weapons: s.weaponModels, hands: s.handModels, config: s.config, events: s.events, log: s.log,
    });
```

por:

```
    this.viewmodel = new Viewmodel({
      render: s.render, weapons: s.weaponModels, hands: s.handModels, luvas: s.luvasModels, config: s.config, events: s.events, log: s.log,
    });
```

Em `src/modes/matchState.js`, trocar:

```
    s.handModels.geometries().catch((err) => s.log?.error('mãos de massinha:', err));
    this.#preloadWeapons();
```

por:

```
    s.handModels.geometries().catch((err) => s.log?.error('mãos de massinha:', err));
    s.luvasModels?.carregar().catch(() => {}); // o erro de carga das luvas já vai ao log pela fonte
    this.#preloadWeapons();
```

Em `src/modes/matchState.js`, trocar:

```
      s.weaponModels.setEnvironment(this.reflection.texture, REFLEXO.intensidade);
    } finally {
```

por:

```
      s.weaponModels.setEnvironment(this.reflection.texture, REFLEXO.intensidade);
      s.luvasModels?.setAmbiente(this.reflection.texture, REFLEXO.intensidade);
    } finally {
```

Em `src/modes/matchState.js`, trocar:

```
   * "Segurar" da bancada de armas (mapas sem colisão): a câmera livre para no ponto dado (o olhar continua) e o
   * viewmodel mostra a arma escolhida, com o acento e o nível da bancada; null solta. Devolve se está segurando.
   * @param {{id:string, faction?:string|null, lod?:string, camera?:{position:import('three').Vector3, yaw:number, pitch:number}}|null} spec
   */
```

por:

```
   * "Segurar" da bancada de armas (mapas sem colisão): a câmera livre para no ponto dado (o olhar continua) e o
   * viewmodel mostra a arma escolhida, com o acento, o nível e a facção das luvas da bancada; null solta. Devolve se está
   * segurando.
   * @param {{id:string, faction?:string|null, lod?:string, gloves?:string|null,
   *   camera?:{position:import('three').Vector3, yaw:number, pitch:number}}|null} spec
   */
```

Em `src/modes/matchState.js`, trocar:

```
    const was = this.hold;
    this.hold = spec ? { id: spec.id, faction: spec.faction ?? null, lod: spec.lod ?? 'perto' } : null;
    p.parked = Boolean(this.hold);
```

por:

```
    const was = this.hold;
    this.hold = spec ? { id: spec.id, faction: spec.faction ?? null, lod: spec.lod ?? 'perto', gloves: spec.gloves ?? null } : null;
    p.parked = Boolean(this.hold);
```

Em `src/modes/matchState.js`, trocar:

```
      vm.lod = 'perto';
      vm.visible = viewmodelVisible({
```

por:

```
      vm.lod = 'perto';
      vm.gloves = null;
      vm.visible = viewmodelVisible({
```

Em `src/modes/matchState.js`, trocar:

```
      vm.lod = this.hold?.lod ?? 'perto';
      vm.visible = Boolean(enabled && this.hold);
```

por:

```
      vm.lod = this.hold?.lod ?? 'perto';
      vm.gloves = this.hold?.gloves ?? null;
      vm.visible = Boolean(enabled && this.hold);
```

Em `src/modes/matchState.js`, trocar:

```
    s.weaponModels.setEnvironment(null);
    this.reflection?.dispose();
```

por:

```
    s.weaponModels.setEnvironment(null);
    s.luvasModels?.setAmbiente(null);
    this.reflection?.dispose();
```

Run: `node --test tests/viewmodelLuvas.test.js tests/weaponLibraryGlb.test.js`
Expected: PASS — # tests 13 # pass 13 # fail 0 .

Run: `node --test "tests/**/*.test.js"`
Expected: PASS — # tests 443 # pass 443 # fail 0 .

### Tarefa 11: Bancada e console

**Files:** Modify `src/maps/arsenal/bench.js`, `panel.js`, `src/debug/weaponCommands.js`; Create
`src/debug/luvasCommands.js`, `tests/luvasCommand.test.js`.

- [ ] **Passo 1: Testes** — `luvas`: estado (carregando/pronta/erro), triângulos por braço, facção atual, marca do rig
  e se bate com a da arma na mão; `luvas_contato` sem arma com pega avisa; com a AK, devolve a penetração máxima e a
  distância de cada contato (com a malha e a arma falsas do teste: um contato a 0,4 mm sai 0,4); formata em mm com duas
  casas; a bancada: "Segurar" com a AK mostra as luvas e o seletor de facção troca a pintura delas.
- [ ] **Passo 2: Ver falhar**; **Passo 3: implementar** — `contatoDasLuvas` em `pega.js` (vértices da malha deformada
  pelo `SkinnedMesh.applyBoneTransform`; a arma numa BVH do `three-mesh-bvh`; dentro/fora pela normal do ponto mais
  perto); **Passo 4: ver passar**; suíte inteira.
- [ ] **Passo 5: No navegador** — `map pista`, `give ak47`: as luvas na mão, `luvas_contato` batendo com o relatório do
  Blender (diferença ≤ 0,05 mm); `cl_bracadeira tr` e `ct`: pintura e braçadeira trocando; a bancada com "Segurar".

### Parada de conferência P2

A AK segurada em primeira pessoa nas duas facções (capturas do jogo em três posições prontas do CS e de perto de cada
mão), as vistas de perto do Blender e os números do `luvas_contato`; o usuário confere antes do acabamento final.

**Resposta do usuário (2026-09-27):** corrigir os erros críticos e, **sempre**, a mão da frente com só o polegar de um
lado e os outros quatro dedos do outro, como a pega da AK no CS:GO (a imagem de referência que ele mandou). O que mudou:

- **A mão da frente** (achado → correção, em duas rodadas): (1) o polegar esquerdo subia na vertical ao lado do
  guarda-mão e passava por cima do topo (a regra só pedia "o mais à esquerda possível", e na face lateral todo ponto é
  igualmente à esquerda) → a polpa num ponto da face e um eixo; (2) o usuário recusou o resultado — o polegar dobrava em
  arco (MCP 35°, IP 17°, a CMC no limite da extensão) com só a ponta encostada: "o dedo tem que estar colado com a arma"
  → o polegar **reto e deitado** (`empunhadura_polegar.deitar_na_arma`): a IK zera a folga da falange proximal e da
  distal para a face esquerda ao longo do comprimento (pela cápsula de seção medida, com a normal da superfície mais
  perto tendo de ser a da face — sem isso ele deitava na face de baixo, ao lado do indicador), aponta as duas para o
  eixo e cobra a curva além de 12°; a referência é a pega "thumb break" (os quatro dedos por baixo do guarda-mão e o
  polegar esticado ao longo do lado, apontando para o alvo). O Pinterest e os sites de tiro estão bloqueados pela rede
  desta sessão; só a busca respondeu. A regra `FRENTE` em `empunhadura_regras.py`, base de toda categoria, com a mão
  girada 35° na vertical, −10° no cano e 20° de diagonal (varreduras de giro, diagonal e altura da palma; a âncora não
  recua — o calcanhar da mão bate na curva do carregador). Na AK: o polegar com 0° de curva, a distal encostada (0 a
  0,2 mm) e a proximal em cunha de 4 a 6,5 mm (a base sai da quina de baixo). As validações novas (bloqueiam o
  `construir` e se repetem na saída do Node, `saidaPega.mjs`): os `lados` — a polpa do polegar e a de cada um dos quatro
  dedos a pelo menos 5 mm do plano do meio da arma, cada uma do seu lado (`LIMITES_DA_PEGA.ladoMM`; na AK, polegar
  +20,1 mm, indicador −16,5, médio −24,6, anelar −25,5, mínimo −25,6 mm) — e o polegar deitado: a curva até 20°, a
  distal encostando (até 1 mm) e nenhum trecho a mais de 8 mm (`polegarCurvaGraus`, `polegarFolgaMM`).
- **A penetração passava despercebida além de 6 mm** (achado na segunda rodada): a medida da validação usava o limite
  das buscas do solver, e um vértice mais fundo que isso dentro da arma não contava — numa das posições varridas o
  indicador entrava 7,35 mm e a validação dizia 0,047 mm → a validação mede sem limite (`NaArma.penetracao(...,
  limite=None)`). As pegas exportadas antes não tinham isso (os contatos, medidos sem limite, estavam em ±0,05 mm).
- **O cotovelo da mão da frente**: com a pega nova e o cotovelo antigo, o desvio radial passava do limite na posição 3 →
  varredura com o menor pior ângulo em relação ao limite (minimax; a soma dos quadrados deixava a supinação em 79,9° de
  80°): `gloveElbows.esquerda` = [−9,9, −52,4, −9,7], todos os ângulos a no máximo 91 % do limite (a supinação, que a
  P2 viu a 97 %, fica em 68–72°) e o antebraço a 6,6 mm da arma. O teste do viewmodel passou a exigir no máximo 93 %.
- **O polegar da mão do gatilho** (fica para depois): ele cruza o punho com a IP a 78,8° de 80°, em gancho. O mesmo
  polegar deitado não serve ali (reto, ele não contorna a traseira do punho: a base entra 0,1 mm), e o peso do lado não
  muda nada (a CMC já está no limite da ficha); o conserto é reposicionar a mão no punho. Essa mão fica fora da tela em
  primeira pessoa (o usuário não quer as duas mãos no quadro); aparece na inspeção (4.3) e em terceira pessoa (Fase 5).
- **O coiote pálido**: medido na pista, o coiote de partida saía rgb(180, 117, 75), o mesmo laranja da madeira da AK
  (1,20× de luminância) → `#5C5139` / `#4D4432` / `#342E24`, mais escuro e puxado para o oliva, e o couro gastando
  menos: madeira/luva 1,68× e mesa/luva 3,02× (antes 1,98×). O teste dos dados exige o coiote a no máximo 60 % da
  luminância da madeira de fábrica da AK e a 12° de matiz dela.
- **O grão do couro craquelado**: o padrão do shader era uma rede de linhas finas e escuras entre células de Voronoi →
  seixinhos arredondados com o vale largo e raso, no domínio torcido por ruído (`armaGrao`), e menos mistura de cor.
- **Ficam para a Tarefa 14** (não críticos): as facetas de perto nos protetores dos nós e nas pontas (só na inspeção,
  que chega na 4.3; o orçamento de 7 mil triângulos por luva está quase cheio) e o gancho do polegar da mão do gatilho
  (acima). A mão direita continua fora da tela nas três posições prontas (o topo dela fica 0,24 da meia-altura abaixo da borda), como na referência do
  CS:GO que ele mandou; o enquadramento com as duas mãos do CS2 muda a posição do `rifle` e os cotovelos. **Decidido
  pelo usuário (2026-09-27): uma mão só na tela** — o enquadramento fica.
- **Ambiente**: nesta sessão (nuvem, Linux) o Blender é o módulo `bpy` 5.2.2 do PyPI atrás de um lançador que imita a
  linha de comando (`tools/blender/local.json`, fora do git), com a ponte do Draco compilada da fonte do Blender 5.1 e o
  Mesa para o Workbench; as luvas reconstruídas por ele saem com as mesmas medidas, triângulos e marca do rig do
  Windows.


**Código da tarefa** (a versão verificada no navegador e no Blender; os blocos `file=` são o arquivo inteiro, os pares são aplicados na ordem).

- [ ] **Os testes** — `tests/luvasCommand.test.js`:

```js file=tests/luvasCommand.test.js
// Os comandos `luvas` e `luvas_contato` (Fase 4.1b; plano, Tarefa 11): a medida do contato com uma arma e uma luva
// falsas de posição conhecida (um contato a 0,4 mm sai 0,4; um vértice 0,2 mm dentro dá a penetração), o formato em mm
// com duas casas e o veredito, o aviso sem arma com pega, e o `luvas` com o estado, os triângulos, a facção, a marca
// do rig conferida com a da arma na mão e os pulsos.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import * as THREE from 'three';
import { bvhDaArma, contatoDasLuvas } from '../src/characters/hands/luvasContato.js';
import { emMM, formatarContato, registerLuvasCommands, relatorioDasLuvas } from '../src/debug/luvasCommands.js';

const MM = 25.4;
const MARCA = { d: 'a'.repeat(64), e: 'b'.repeat(64) };

/** A arma falsa: uma caixa de 4 × 2 × 2 u girada e deslocada, dentro de um grupo que faz a vez da instância. */
function armaFalsa() {
  const raiz = new THREE.Group();
  raiz.position.set(1, -2, -5);
  raiz.quaternion.setFromEuler(new THREE.Euler(0.2, 0.5, -0.1));
  const caixa = new THREE.Mesh(new THREE.BoxGeometry(4, 2, 2), new THREE.MeshBasicMaterial());
  caixa.position.set(0.5, 0, 0);
  raiz.add(caixa);
  raiz.updateMatrixWorld(true);
  return raiz;
}

/** A luva falsa: três vértices no referencial da arma (0,4 mm fora da face +Y, 0,2 mm dentro, longe), noutro grupo. */
function lucaFalsa(raiz) {
  const grupo = new THREE.Group();
  grupo.position.set(-3, 1, 2);
  grupo.quaternion.setFromEuler(new THREE.Euler(-0.4, 0.3, 0.9));
  grupo.updateMatrixWorld(true);
  const naArma = [new THREE.Vector3(0.7, 1 + 0.4 / MM, 0.1), new THREE.Vector3(-0.8, 1 - 0.2 / MM, -0.3), new THREE.Vector3(0.5, 4, 0)];
  const paraBraco = grupo.matrixWorld.clone().invert().multiply(raiz.matrixWorld);
  const pts = new Float64Array(9);
  naArma.forEach((p, i) => {
    const q = p.clone().applyMatrix4(paraBraco).multiplyScalar(MM);
    pts.set([q.x, q.y, q.z], i * 3);
  });
  return { grupo, posicoesMM: pts };
}

test('luvas_contato: a distância com sinal de cada sonda e a penetração máxima, no referencial da arma', () => {
  const raiz = armaFalsa();
  const braco = lucaFalsa(raiz);
  const bvh = bvhDaArma(raiz);
  const r = contatoDasLuvas({ bvh, raizDaArma: raiz, braco, sondas: { palma: { vertice: 0, mm: 0.38 }, polegar: { vertice: 1, mm: -0.21 } } });
  const [palma, polegar] = r.sondas;
  assert.ok(Math.abs(palma.jogoMM - 0.4) < 1e-4, `um contato a 0,4 mm sai ${palma.jogoMM}`);
  assert.ok(Math.abs(palma.diferencaMM - 0.02) < 1e-4);
  assert.ok(Math.abs(polegar.jogoMM + 0.2) < 1e-4, `dentro sai negativo: ${polegar.jogoMM}`);
  assert.ok(Math.abs(r.penetracaoMM - 0.2) < 1e-4, `penetração ${r.penetracaoMM}`);
  assert.ok(Math.abs(r.piorDiferencaMM - 0.02) < 1e-4);
});

test('luvas_contato: um ponto longe da quina da caixa sai fora (o lado pela pseudonormal, não por uma face só)', () => {
  const raiz = armaFalsa();
  const grupo = new THREE.Group();
  // em volta da quina (+X, +Y, +Z) e das arestas: todos fora, a distância certa
  const casos = [[4, 3, 3], [3, 1.5, 0.2], [0.3, 2, 1.8], [2.6, -1.4, 1.3]];
  for (const c of casos) {
    const pts = new Float64Array(new THREE.Vector3(...c).applyMatrix4(raiz.matrixWorld).multiplyScalar(MM).toArray());
    const r = contatoDasLuvas({ bvh: bvhDaArma(raiz), raizDaArma: raiz, braco: { grupo, posicoesMM: pts }, sondas: { p: { vertice: 0, mm: 0 } } });
    const b = new THREE.Box3(new THREE.Vector3(-1.5, -1, -1), new THREE.Vector3(2.5, 1, 1));
    assert.ok(Math.abs(r.sondas[0].jogoMM - b.distanceToPoint(new THREE.Vector3(...c)) * MM) < 1e-3, `(${c}): ${r.sondas[0].jogoMM}`);
    assert.equal(r.penetracaoMM, 0);
  }
});

test('luvas_contato: o formato em mm com duas casas e o veredito', () => {
  const lado = (dif, entra) => ({ penetracaoMM: entra, piorDiferencaMM: dif, sondas: [{ contato: 'palma', jogoMM: -0.029, blenderMM: -0.044, diferencaMM: dif }] });
  const txt = formatarContato('ak47', { direita: lado(0.016, 0.053), esquerda: lado(0.08, 0.06) }, { d: { penetracaoMM: 0.044 }, e: { penetracaoMM: 0.05 } });
  assert.match(txt, /^luvas_contato ak47 \(a diferença para o Blender até 0,05 mm; entra até 0,30 mm\)/);
  assert.match(txt, /direita: entra 0,05 mm \(Blender 0,04 mm\) · pior diferença 0,02 mm ✓/);
  assert.match(txt, /esquerda: entra 0,06 mm \(Blender 0,05 mm\) · pior diferença 0,08 mm ✗/);
  assert.match(txt, /palma +jogo +−0,03 mm · Blender +−0,04 mm · diferença 0,02 mm/);
  assert.equal(emMM(0.4), '0,40 mm');
});

/** Console mínimo e o viewmodel falso do jeito que os comandos leem. */
function montar({ vm = null, estado = 'pronta' } = {}) {
  const commands = new Map();
  const con = { register: (def) => commands.set(def.name, def) };
  const relatorio = {
    estado, erro: estado === 'erro' ? 'luvas.glb: HTTP 404' : null, triangulos: { d: 6748, e: 6748 }, antebraco: 12500, ms: 1192,
    marca: estado === 'pronta' ? MARCA : null, bracos: vm ? 2 : 0,
  };
  const s = { luvasModels: { relatorio: () => relatorio } };
  registerLuvasCommands(con, s, { matchState: () => (vm ? { viewmodel: vm } : null) });
  return (nome) => commands.get(nome).run([]);
}

function vmFalso({ bracos = 'luvas', marca = MARCA, avisos = { direita: [], esquerda: ['antebraço: supinação de 85,0° (limite 80°)'] } } = {}) {
  const angulos = { flexao: -15.2, desvio: -10.2, pronacao: -2.9 };
  return {
    info: { id: 'ak47', pega: { marca, sondas: {} } },
    status: () => ({ item: 'ak47', bracos, faccao: 'tropa', avisos }),
    gloves: { prontos: bracos === 'luvas', bracos: { direita: { angulos }, esquerda: { angulos: { ...angulos, pronacao: -85 } } } },
  };
}

test('luvas: o estado, os triângulos, a marca do rig e, na mão, a facção, a marca da arma e os pulsos', () => {
  let txt = montar({ vm: vmFalso() })('luvas');
  assert.match(txt, /^luvas: pronta · 6\.748 \+ 6\.748 triângulos · antebraço de massinha 12\.500 · carregadas em 1192 ms · 2 braço\(s\) na cena/);
  assert.match(txt, /marca do rig: d aaaaaaaaaaaa… · e bbbbbbbbbbbb…/);
  assert.match(txt, /na mão: ak47 com as luvas · Tropa do Estúdio \(preta\) · a marca da arma bate com a das luvas ✓/);
  assert.match(txt, /direita: pulso −15,2° de flexão, −10,2° de desvio, antebraço −2,9° de pronação$/m);
  assert.match(txt, /esquerda: .* antebraço −85,0° de pronação — antebraço: supinação de 85,0° \(limite 80°\)/);
  txt = montar({ vm: vmFalso({ marca: { d: 'c'.repeat(64), e: 'b'.repeat(64) } }) })('luvas');
  assert.match(txt, /a marca da arma NÃO bate com a das luvas ✗/);
  txt = montar({ vm: vmFalso({ bracos: null, marca: { d: 'c'.repeat(64), e: 'b'.repeat(64) } }) })('luvas');
  assert.match(txt, /na mão: ak47 com nenhum braço/);
  assert.match(txt, /construa a arma de novo no Blender/);
  assert.match(montar({ estado: 'erro' })('luvas'), /^luvas: erro — luvas\.glb: HTTP 404/);
  assert.match(montar({ estado: 'carregando' })('luvas'), /^luvas: carregando/);
  assert.match(montar({ estado: '—' })('luvas'), /^luvas: não carregadas/);
  assert.match(montar()('luvas'), /na mão: nada/);
});

test('luvas_contato: sem arma com pega na mão, o aviso', () => {
  assert.match(montar()('luvas_contato'), /segure em primeira pessoa uma arma com a pega das luvas \(give ak47\)/);
  assert.match(montar({ vm: vmFalso({ bracos: 'massinha' }) })('luvas_contato'), /segure em primeira pessoa/);
});

test('luvas_contato: o zero arredondado sai sem sinal', () => {
  assert.equal(emMM(-0.001), '0,00 mm');
  assert.equal(emMM(-0.006), '−0,01 mm');
});
```

Run: `node --test tests/luvasCommand.test.js`
Expected: FAIL — # tests 1 # pass 0 # fail 1 .

- [ ] **A implementação** — `src/characters/hands/luvasContato.js`, `src/debug/luvasCommands.js`, `src/debug/weaponCommands.js`, `src/maps/arsenal/bench.js`, `src/maps/arsenal/panel.js`:

```js file=src/characters/hands/luvasContato.js
// A medida do `luvas_contato` (Fase 4.1b; desenho em docs/superpowers/specs/2026-09-26-4.1b-luvas-e-empunhadura-design.md,
// seção 7.5; plano, Tarefa 11): a luva deformada de verdade no jogo (as posições que o braço calculou pelo modelo das
// dobras, as mesmas contas do Blender) contra a malha da arma numa BVH (three-mesh-bvh), no referencial da raiz da arma.
// Para cada sonda que o solver do Blender gravou nos extras da pega (o vértice de cada contato e a distância que ele
// mediu), a distância com sinal no jogo — negativa dentro da arma, pelo lado da normal do triângulo mais perto — e a
// diferença; e a penetração máxima de todos os vértices da luva. As duas medidas têm de bater (≤ 0,05 mm): prova que a
// pega, o referencial do osso `mao` e as dobras chegam ao jogo como saíram do Blender.

import * as THREE from 'three';
import { MeshBVH } from 'three-mesh-bvh';

const MM_POR_U = 25.4;
const _p = new THREE.Vector3();
const _a = new THREE.Vector3();
const _b = new THREE.Vector3();
const _c = new THREE.Vector3();
const _n = new THREE.Vector3();
const _m = new THREE.Matrix4();

/**
 * A malha de uma arma numa BVH, no referencial de `raiz` (as malhas dela e das filhas; as geometrias com índice).
 * @param {THREE.Object3D} raiz a instância da arma (ou a raiz do nível `perto` no .glb)
 * @param {(malha:THREE.Mesh)=>boolean} [filtro]
 */
export function bvhDaArma(raiz, filtro = () => true) {
  raiz.updateMatrixWorld(true);
  const inv = new THREE.Matrix4().copy(raiz.matrixWorld).invert();
  const pos = [];
  const idx = [];
  raiz.traverse((o) => {
    if (!o.isMesh || !filtro(o)) return;
    const g = o.geometry;
    const m = _m.multiplyMatrices(inv, o.matrixWorld);
    const base = pos.length / 3;
    const p = g.attributes.position;
    for (let i = 0; i < p.count; i++) {
      _p.fromBufferAttribute(p, i).applyMatrix4(m);
      pos.push(_p.x, _p.y, _p.z);
    }
    if (g.index) for (let i = 0; i < g.index.count; i++) idx.push(base + g.index.getX(i));
    else for (let i = 0; i < p.count; i++) idx.push(base + i);
  });
  if (!idx.length) throw new Error('luvas_contato: a arma sem malha');
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.BufferAttribute(Float32Array.from(pos), 3));
  g.setIndex(new THREE.BufferAttribute(Uint32Array.from(idx), 1));
  return new MeshBVH(g);
}

const _q = new THREE.Vector3();
const _pn = new THREE.Vector3();
const _bar = new THREE.Vector3();
const _tri = new THREE.Triangle();

/** Ângulo interno do triângulo (a, b, c) no vértice a. */
function anguloEm(a, b, c) {
  return _p.subVectors(b, a).angleTo(_q.subVectors(c, a));
}

/**
 * Distância com sinal (u) de um ponto (referencial da BVH) à superfície: negativa do lado de dentro. O lado sai da
 * pseudonormal ponderada pelo ângulo no ponto mais perto (Bærentzen e Aanæs, 2005): quando ele cai numa aresta ou num
 * vértice da malha, a normal de um triângulo só pode apontar para o lado errado (um ponto a 4 cm da arma saía "dentro");
 * todos os triângulos que tocam o ponto mais perto entram, cada um com o ângulo dele ali (π nas arestas, o ângulo
 * interno nos vértices, 1 no meio de uma face).
 */
function distanciaComSinal(bvh, ponto, alvo) {
  const r = bvh.closestPointToPoint(ponto, alvo);
  if (!r) return Infinity;
  const perto = r.point.clone();
  const tol = Math.max(1e-6, r.distance * 1e-4);
  _pn.set(0, 0, 0);
  bvh.shapecast({
    intersectsBounds: (caixa) => caixa.distanceToPoint(perto) <= tol,
    intersectsTriangle: (tri) => {
      tri.closestPointToPoint(perto, _q);
      if (_q.distanceToSquared(perto) > tol * tol) return false;
      _tri.set(tri.a, tri.b, tri.c);
      _tri.getBarycoord(perto, _bar);
      const zeros = [_bar.x, _bar.y, _bar.z].filter((w) => Math.abs(w) < 1e-6).length;
      let peso = 1;
      if (zeros === 2) {
        // num vértice: o ângulo interno do triângulo nele
        if (_bar.x > 0.5) peso = anguloEm(tri.a, tri.b, tri.c);
        else if (_bar.y > 0.5) peso = anguloEm(tri.b, tri.c, tri.a);
        else peso = anguloEm(tri.c, tri.a, tri.b);
      } else if (zeros === 1) {
        peso = Math.PI;
      }
      tri.getNormal(_n);
      _pn.addScaledVector(_n, peso);
      return false;
    },
  });
  if (_pn.lengthSq() === 0) {
    // sem triângulo no ponto (não acontece com a BVH íntegra): o do resultado
    const g = bvh.geometry;
    const i = g.index.array;
    const P = g.attributes.position;
    const f = r.faceIndex * 3;
    _a.fromBufferAttribute(P, i[f]);
    _b.fromBufferAttribute(P, i[f + 1]);
    _c.fromBufferAttribute(P, i[f + 2]);
    _pn.subVectors(_c, _b).cross(_a.sub(_b));
  }
  return _pn.dot(_p.subVectors(ponto, perto)) < 0 ? -r.distance : r.distance;
}

/**
 * O contato de um braço de luva com a arma.
 * @param {{bvh:MeshBVH, raizDaArma:THREE.Object3D, braco:import('./bracoLuva.js').BracoLuva, sondas:object}} o
 *   `sondas` = as do lado do braço nos extras da pega ({contato: {vertice, mm}}); a arma e o braço na mesma cena
 * @returns {{sondas:{contato:string, vertice:number, jogoMM:number, blenderMM:number, diferencaMM:number}[],
 *   penetracaoMM:number, piorDiferencaMM:number}}
 */
export function contatoDasLuvas({ bvh, raizDaArma, braco, sondas }) {
  raizDaArma.updateMatrixWorld(true);
  braco.grupo.updateMatrixWorld(true);
  // do referencial do braço (u) ao da arma
  const m = new THREE.Matrix4().copy(raizDaArma.matrixWorld).invert().multiply(braco.grupo.matrixWorld);
  const pts = braco.posicoesMM;
  const alvo = { point: new THREE.Vector3(), distance: 0, faceIndex: 0 };
  const ponto = new THREE.Vector3();
  const noJogo = (v) => {
    ponto.set(pts[v * 3] / MM_POR_U, pts[v * 3 + 1] / MM_POR_U, pts[v * 3 + 2] / MM_POR_U).applyMatrix4(m);
    return distanciaComSinal(bvh, ponto, alvo) * MM_POR_U;
  };
  const linhas = [];
  let pior = 0;
  for (const [contato, s] of Object.entries(sondas ?? {})) {
    const jogo = noJogo(s.vertice);
    const diferenca = Math.abs(jogo - s.mm);
    pior = Math.max(pior, diferenca);
    linhas.push({ contato, vertice: s.vertice, jogoMM: jogo, blenderMM: s.mm, diferencaMM: diferenca });
  }
  let penetracao = 0;
  for (let v = 0; v < pts.length / 3; v++) penetracao = Math.max(penetracao, -noJogo(v));
  return { sondas: linhas, penetracaoMM: penetracao, piorDiferencaMM: pior };
}
```

```js file=src/debug/luvasCommands.js
// Comandos de console das luvas (Fase 4.1b; desenho em docs/superpowers/specs/2026-09-26-4.1b-luvas-e-empunhadura-
// design.md, seção 7.5; plano, Tarefa 11):
//  - `luvas`: o estado da carga, os triângulos de cada luva e do antebraço de massinha, a marca do rig, e na mão a
//    facção, se a marca da arma bate com a das luvas e os ângulos de cada pulso (com os avisos dos limites da AAOS);
//  - `luvas_contato`: a luva deformada de verdade (as posições do modelo das dobras) contra a malha da arma na mão
//    (numa BVH, guardada por instância), sonda por sonda com a medida do Blender ao lado, e a penetração máxima de cada
//    luva — a diferença tem de ficar em LIMITES_DA_PEGA.contatoJogoMM (0,05 mm).

import { LIMITES_DA_PEGA, LUVAS } from '../data/luvas.js';
import { bvhDaArma, contatoDasLuvas } from '../characters/hands/luvasContato.js';

const LADOS = Object.freeze([['direita', 'd'], ['esquerda', 'e']]);
// (sem o sinal quando arredonda para zero: "0,00", não "−0,00")
const num = (v, casas) => (Math.abs(v) < 0.5 * 10 ** -casas ? 0 : v).toFixed(casas).replace('.', ',').replace(/^-/, '−');
/** mm com duas casas (o jeito do console: vírgula e o sinal de menos). */
export const emMM = (v) => `${num(v, 2)} mm`;
const graus = (v) => `${num(v, 1)}°`;

/**
 * As linhas do `luvas_contato` a partir do resultado de cada lado (contatoDasLuvas) e do relatório da arma.
 * @param {string} id @param {{direita?:object, esquerda?:object}} porLado @param {object|null} [empunhadura] a seção do
 *   relatório do Blender (a penetração dele)
 */
export function formatarContato(id, porLado, empunhadura = null) {
  const lim = LIMITES_DA_PEGA.contatoJogoMM;
  const linhas = [`luvas_contato ${id} (a diferença para o Blender até ${emMM(lim)}; entra até ${emMM(LIMITES_DA_PEGA.penetracaoMM)})`];
  for (const [side, lado] of LADOS) {
    const r = porLado[side];
    if (!r) continue;
    const blender = empunhadura?.[lado]?.penetracaoMM;
    const ok = r.piorDiferencaMM <= lim && r.penetracaoMM <= LIMITES_DA_PEGA.penetracaoMM;
    linhas.push(`${side}: entra ${emMM(r.penetracaoMM)}${blender !== undefined ? ` (Blender ${emMM(blender)})` : ''} · pior diferença ${emMM(r.piorDiferencaMM)} ${ok ? '✓' : '✗'}`);
    for (const s of r.sondas) {
      linhas.push(`  ${s.contato.padEnd(18)} jogo ${emMM(s.jogoMM).padStart(10)} · Blender ${emMM(s.blenderMM).padStart(10)} · diferença ${emMM(s.diferencaMM)}`);
    }
  }
  return linhas.join('\n');
}

/**
 * As linhas do `luvas`.
 * @param {{relatorio:()=>object}} luvasModels @param {object|null} vm o viewmodel (null fora da partida)
 */
export function relatorioDasLuvas(luvasModels, vm) {
  const r = luvasModels.relatorio();
  const mil = (n) => n.toLocaleString('pt-BR');
  const linhas = [];
  if (r.estado === 'erro') linhas.push(`luvas: erro — ${r.erro}`);
  else if (r.estado !== 'pronta') linhas.push(`luvas: ${r.estado === '—' ? 'não carregadas (entre num mapa)' : r.estado}`);
  else {
    linhas.push(`luvas: pronta · ${mil(r.triangulos.d)} + ${mil(r.triangulos.e)} triângulos · antebraço de massinha ${r.antebraco ? mil(r.antebraco) : 'não gerado'} · carregadas em ${r.ms} ms · ${r.bracos} braço(s) na cena`);
    linhas.push(`marca do rig: d ${r.marca.d.slice(0, 12)}… · e ${r.marca.e.slice(0, 12)}…`);
  }
  const st = vm?.status?.();
  if (!st?.item) {
    linhas.push('na mão: nada');
  } else if (st.bracos !== 'luvas') {
    const pega = vm.info?.pega;
    linhas.push(`na mão: ${st.item} com ${st.bracos === 'massinha' ? 'os braços de massinha' : 'nenhum braço'}${pega ? '' : ' (a arma não tem a pega das luvas)'}`);
    if (pega && r.marca && (pega.marca.d !== r.marca.d || pega.marca.e !== r.marca.e)) {
      linhas.push('  a marca do rig da arma não é a das luvas: construa a arma de novo no Blender');
    }
  } else {
    const pega = vm.info.pega;
    const bate = r.marca && pega.marca.d === r.marca.d && pega.marca.e === r.marca.e;
    linhas.push(`na mão: ${st.item} com as luvas · ${LUVAS.pinturas[st.faccao]?.nome ?? st.faccao} · a marca da arma ${bate ? 'bate com a das luvas ✓' : 'NÃO bate com a das luvas ✗'}`);
    for (const [side] of LADOS) {
      const b = vm.gloves.bracos[side];
      if (!b) continue;
      const a = b.angulos;
      const avisos = st.avisos?.[side] ?? [];
      linhas.push(`  ${side}: pulso ${graus(a.flexao)} de flexão, ${graus(a.desvio)} de desvio, antebraço ${graus(a.pronacao)} de pronação${avisos.length ? ` — ${avisos.join('; ')}` : ''}`);
    }
  }
  return linhas.join('\n');
}

/** Registra `luvas` e `luvas_contato` no console. */
export function registerLuvasCommands(con, s, { matchState }) {
  const bvhs = new WeakMap(); // instância da arma → BVH (refeita quando a instância muda)
  con.register({
    name: 'luvas',
    usage: '',
    help: 'estado das luvas: carga, triângulos, marca do rig e, na mão, a facção, a marca da arma e os pulsos',
    run: () => relatorioDasLuvas(s.luvasModels, matchState()?.viewmodel ?? null),
  });
  con.register({
    name: 'luvas_contato',
    usage: '',
    help: 'mede no jogo o contato das luvas com a arma na mão (a malha deformada de verdade) e compara com o Blender',
    run: () => {
      const vm = matchState()?.viewmodel;
      const info = vm?.info;
      if (!info?.pega || vm.status().bracos !== 'luvas' || !vm.gloves?.prontos) {
        return 'luvas_contato: segure em primeira pessoa uma arma com a pega das luvas (give ak47)';
      }
      let bvh = bvhs.get(vm.weapon);
      if (!bvh) {
        bvh = bvhDaArma(vm.weapon);
        bvhs.set(vm.weapon, bvh);
      }
      const porLado = {};
      for (const [side, lado] of LADOS) {
        porLado[side] = contatoDasLuvas({ bvh, raizDaArma: vm.weapon, braco: vm.gloves.bracos[side], sondas: info.pega.sondas[lado] });
      }
      return formatarContato(info.id, porLado, info.report?.empunhadura ?? null);
    },
  });
}
```

Em `src/debug/weaponCommands.js`, trocar:

```
// massinha), o ajuste ao vivo da posição de cada categoria na mão (viewmodel_ajuste, para afinar src/data/viewmodel.js)
// e, na 4.1a, as skins de cor e acabamento das armas realistas (skin). Falam com a mesma config, a mesma biblioteca de
// armas e o mesmo viewmodel que o jogo usa.

```

por:

```
// massinha), o ajuste ao vivo da posição de cada categoria na mão (viewmodel_ajuste, para afinar src/data/viewmodel.js)
// e, na 4.1a, as skins de cor e acabamento das armas realistas (skin). Na 4.1b, o viewmodel_ajuste afina também os
// cotovelos das luvas (gloveElbows) quando a arma na mão tem a pega, e os comandos das luvas (luvas, luvas_contato)
// vêm de luvasCommands.js. Falam com a mesma config, a mesma biblioteca de armas e o mesmo viewmodel que o jogo usa.

```

Em `src/debug/weaponCommands.js`, trocar:

```
import { onOff } from './consoleArgs.js';

```

por:

```
import { onOff } from './consoleArgs.js';
import { registerLuvasCommands } from './luvasCommands.js';

```

Em `src/debug/weaponCommands.js`, trocar:

```
        if (xyz.length !== 3) throw new Error('uso: viewmodel_ajuste cotovelo direita|esquerda x y z');
        vm.setTune(cat, { elbows: { [side]: xyz.map((a) => num(a, 'cotovelo')) } });
      } else if (what !== undefined) {
```

por:

```
        if (xyz.length !== 3) throw new Error('uso: viewmodel_ajuste cotovelo direita|esquerda x y z');
        // o cotovelo dos braços que estão na mão: os de luva (armas com pega) ou os de massinha
        const chave = vm.status().bracos === 'luvas' ? 'gloveElbows' : 'elbows';
        vm.setTune(cat, { [chave]: { [side]: xyz.map((a) => num(a, 'cotovelo')) } });
      } else if (what !== undefined) {
```

Em `src/debug/weaponCommands.js`, trocar:

```
  });
}
```

por:

```
  });
  registerLuvasCommands(con, s, { matchState });
}
```

Em `src/maps/arsenal/bench.js`, trocar:

```
    // `skin`: a skin de massa da de massinha (a da realista é a do serviço); `faction`: null na realista.
    this.state = { id: null, faction: null, lod: 'perto', skin: null, explode: 0, anchors: false, plan: false, spin: true };
    this.skinMaterials = [];
```

por:

```
    // `skin`: a skin de massa da de massinha (a da realista é a do serviço); `faction`: null na realista.
    // `gloves`: a facção das luvas no "Segurar" das armas com pega (Fase 4.1b).
    this.state = { id: null, faction: null, lod: 'perto', gloves: 'massaCrua', skin: null, explode: 0, anchors: false, plan: false, spin: true };
    this.skinMaterials = [];
```

Em `src/maps/arsenal/bench.js`, trocar:

```
  }

  /**
   * Skin da arma da roda. Na realista, `value` é "fabrica" ou a chave de uma skin nomeada e a troca é no serviço (o
```

por:

```
  }

  /** A facção das luvas no "Segurar" (a arma da roda não muda: a pintura é das luvas). */
  setGloveFaction(faccao) {
    this.state.gloves = faccao;
    this.onChange?.();
  }

  /**
   * Skin da arma da roda. Na realista, `value` é "fabrica" ou a chave de uma skin nomeada e a troca é no serviço (o
```

Em `src/maps/arsenal/panel.js`, trocar:

```
// viewmodel com a câmera parada). Linha de informação com a origem, os triângulos e o tempo de carga ou de geração.

```

por:

```
// viewmodel com a câmera parada). Linha de informação com a origem, os triângulos e o tempo de carga ou de geração.
// Fase 4.1b: na realista com pega, o seletor da facção das luvas (a pintura do "Segurar"; a arma não tem acento).

```

Em `src/maps/arsenal/panel.js`, trocar:

```
import { SKINS_ARMA } from '../../data/skinsArma.js';
import { FABRICA, PERSONALIZADA } from '../../weapons/skins/skin.js';
```

por:

```
import { SKINS_ARMA } from '../../data/skinsArma.js';
import { FACCOES_DAS_LUVAS, LUVAS } from '../../data/luvas.js';
import { FABRICA, PERSONALIZADA } from '../../weapons/skins/skin.js';
```

Em `src/maps/arsenal/panel.js`, trocar:

```
  const factionSeg = segmented('Facção do acento', FACTIONS, (id) => bench.setFaction(id));
  const lodSeg = segmented('Nível de detalhe', LODS, (id) => bench.setLod(id));
```

por:

```
  const factionSeg = segmented('Facção do acento', FACTIONS, (id) => bench.setFaction(id));
  const glovesSeg = segmented('Facção das luvas', FACCOES_DAS_LUVAS.map((id) => ({ id, label: LUVAS.pinturas[id].nome })), (id) => bench.setGloveFaction(id));
  const lodSeg = segmented('Nível de detalhe', LODS, (id) => bench.setLod(id));
```

Em `src/maps/arsenal/panel.js`, trocar:

```
    section('Arma', weaponSeg.el, hold, info),
    section('Aparência', h('div.vt-row', null, h('span.vt-label', null, 'Skin'), skinSelect), factionSeg.el, lodSeg.el),
    section('Oficina', explode.el, anchors.el, plan.el, spin.el, measure, measureOut, reload, reloadOut),
```

por:

```
    section('Arma', weaponSeg.el, hold, info),
    section('Aparência', h('div.vt-row', null, h('span.vt-label', null, 'Skin'), skinSelect), factionSeg.el, glovesSeg.el, lodSeg.el),
    section('Oficina', explode.el, anchors.el, plan.el, spin.el, measure, measureOut, reload, reloadOut),
```

Em `src/maps/arsenal/panel.js`, trocar:

```
    factionSeg.set(st.faction);
    for (const b of lodSeg.buttons) b.hidden = b.dataset.pick === 'longe' && !glb;
```

por:

```
    factionSeg.set(st.faction);
    glovesSeg.el.hidden = !(glb && s.weaponModels.info(st.id)?.pega);
    glovesSeg.set(st.gloves);
    for (const b of lodSeg.buttons) b.hidden = b.dataset.pick === 'longe' && !glb;
```

Run: `node --test tests/luvasCommand.test.js`
Expected: PASS — # tests 6 # pass 6 # fail 0 .

Run: `node --test "tests/**/*.test.js"`
Expected: PASS — # tests 449 # pass 449 # fail 0 .

### Tarefa 12: O rebatedor

**Files:** Create `src/maps/arsenal/rebatedor.js`, `tests/rebatedor.test.js`; Modify `src/maps/arsenal/index.js`,
`src/data/arsenal.js`.

- [ ] **Passo 1: Testes** — o rebatedor entra na cena da bancada (posição e giro dos dados: atrás do ponto do reflexo,
  virado para a bancada), fica fora da colisão do jogador, é descartado com o mapa e aparece na lista do que a captura
  do reflexo vê.
- [ ] **Passo 2: Ver falhar**; **Passo 3: implementar** (painel de isopor branco num tripé do set, com os materiais do
  set); **Passo 4: ver passar**.
- [ ] **Passo 5: Medir** — na bancada, a luminância média do lado do receptor da AK (a mesma vista, antes e depois):
  o aço lê como aço escurecido, não preto; registrar os dois números.

Execução (2026-09-27; desenho, seção 7.6):
- **Arquivos a mais:** `src/clay/set/surfaceMaterials.js` (`foamMaterial`, o isopor: Voronoi 3D das contas fundidas com
  o sulco entre elas e o tom de cada conta), `src/clay/set/index.js` (`set.foam`), `src/render/studio/fixtures.js` (o
  `buildCStand` com o `reach` do braço, para a coluna descer fora da mesa).
- **A luz:** a key e o fill ficam atrás do lugar da placa; quem a acende é o rim (os dados, `rebatedor.luz`).
- **A posição:** três medidas até a final (a tabela da seção 7.6): alta e girada; em pé na beira da mesa; deitada 25°
  para trás, 700 × 220 × 20 mm, assentada no tampo atrás do tapete. O rebatedor só pode ficar abaixo dos raios da key
  que vão ao tapete: as posições que clareavam mais o aço faziam sombra nele (o teste confere a grade inteira).
- **Números:** o lado do receptor na roda, de 0,0024 para 0,0390 (16×, roda a 0) e de 0,0004 para 0,0269 (60×, roda a π); o
  "Segurar" (que já não saía preto), de 0,0347 para 0,0354; nenhuma sombra na bancada.
- **Testes:** `tests/rebatedor.test.js` (5): atrás do olho e virado para ele, o primeiro objeto naquela direção e ≥ 60 %
  do cone do reflexo do receptor; no cone do rim e sem sombra da key no tapete nem na roda; assentado no tampo atrás do
  tapete; o C-stand no chão, fora da mesa; o isopor fosco e sem boil, e o descarte das geometrias sem os materiais do set.


**Código da tarefa** (a versão verificada no navegador e no Blender; os blocos `file=` são o arquivo inteiro, os pares são aplicados na ordem).

- [ ] **Os testes** — `tests/rebatedor.test.js`:

```js file=tests/rebatedor.test.js
// O rebatedor da bancada `arsenal` (Fase 4.1b; desenho, seção 7.6; plano, Tarefa 12): o painel de isopor branco num
// C-stand, atrás de quem olha a bancada e virado para ela — na foto do reflexo das armas realistas (o olho do "Segurar")
// e no cone da luz que o alimenta (o rim da vitrine, a única que chega pela frente ali: a key e o fill ficam atrás
// dele), sem fazer sombra da key no tapete; o tripé no chão, fora da mesa; fosco e sem boil; e sai com o mapa (as
// geometrias; os materiais são da biblioteca do set, divididos).
import { test } from 'node:test';
import assert from 'node:assert/strict';
import * as THREE from 'three';
import { ARSENAL } from '../src/data/arsenal.js';
import { HULL } from '../src/data/movement.js';
import { STUDIO_RIGS } from '../src/data/studioRigs.js';
import { foamMaterial } from '../src/clay/set/surfaceMaterials.js';
import { construirRebatedor } from '../src/maps/arsenal/rebatedor.js';

const D = ARSENAL.desk;
const tableY = D.mat.thickness;
const olho = new THREE.Vector3(ARSENAL.reflexo.x, tableY + HULL.standEye, ARSENAL.reflexo.z);
const luzes = STUDIO_RIGS[ARSENAL.rig].lights;
const key = luzes.find((l) => l.id === 'key');
const fonte = luzes.find((l) => l.id === ARSENAL.rebatedor.luz);

function setFalso() {
  const mats = { foam: new THREE.MeshStandardMaterial(), blackMetal: new THREE.MeshStandardMaterial(), chrome: new THREE.MeshStandardMaterial() };
  return { mats, foam: () => mats.foam, blackMetal: () => mats.blackMetal, chrome: () => mats.chrome };
}

function montar() {
  const set = setFalso();
  const r = construirRebatedor(set, ARSENAL.rebatedor, { floorY: D.floorY, apoioY: 0, olho, luz: new THREE.Vector3(...fonte.position) });
  const scene = new THREE.Scene();
  scene.add(r.group);
  scene.updateMatrixWorld(true);
  return { set, r, scene, painel: r.group.getObjectByName('rebatedor-painel') };
}

/** O centro e a normal da frente do painel (a face +Z dele) no mundo. */
function frente(painel) {
  const centro = painel.getWorldPosition(new THREE.Vector3());
  const normal = new THREE.Vector3(0, 0, 1).applyQuaternion(painel.getWorldQuaternion(new THREE.Quaternion()));
  return { centro, normal };
}

test('rebatedor: o painel atrás do olho do reflexo, virado para ele e o primeiro que o olho vê naquela direção', () => {
  const { r, scene, painel } = montar();
  assert.ok(painel, 'o painel de isopor');
  const { centro, normal } = frente(painel);
  assert.ok(centro.z > ARSENAL.reflexo.z + 100, 'atrás de quem olha a bancada (o olho olha para −Z)');
  assert.ok(centro.y > tableY + 60, 'acima do tampo');
  const paraOlho = olho.clone().sub(centro).normalize();
  assert.ok(normal.dot(paraOlho) > 0.6, `virado para o olho (cos ${normal.dot(paraOlho).toFixed(2)})`);
  // a foto do reflexo é a cena inteira na camada 0: o painel está nela, visível e opaco, e nada o tapa do olho
  assert.ok(painel.visible && painel.layers.isEnabled(0) && !painel.material.transparent);
  const ray = new THREE.Raycaster(olho, centro.clone().sub(olho).normalize());
  const hit = ray.intersectObject(scene, true)[0];
  assert.equal(hit?.object, painel, 'o primeiro objeto na direção do painel');
  // cobre o reflexo do lado do receptor na roda: visto do olho, o lado virado para quem olha reflete +Z um pouco para
  // baixo (elevação −0,29, o tampo atrás do olho); pelo menos 60 % de um cone de 25° em volta dessa direção cai na placa
  const eixoDoReflexo = new THREE.Vector3(0, -0.29, 0.96).normalize();
  const giro = new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0, 0, 1), eixoDoReflexo);
  let cobre = 0;
  const N = 200;
  for (let i = 0; i < N; i++) {
    const cosA = 1 - ((i + 0.5) / N) * (1 - Math.cos(THREE.MathUtils.degToRad(25)));
    const sinA = Math.sqrt(1 - cosA * cosA);
    const d = new THREE.Vector3(sinA * Math.cos(i * 2.399963), sinA * Math.sin(i * 2.399963), cosA).applyQuaternion(giro);
    if (new THREE.Raycaster(olho, d).intersectObject(painel).length) cobre++;
  }
  assert.ok(cobre / N >= 0.6, `a placa cobre ${(100 * cobre / N).toFixed(0)} % do reflexo do receptor`);
  // tamanho de uma placa de isopor de 20 mm
  const caixa = new THREE.Box3().setFromBufferAttribute(painel.geometry.attributes.position);
  const lado = caixa.getSize(new THREE.Vector3());
  assert.deepEqual([lado.x, lado.y, lado.z].map(Math.round), [ARSENAL.rebatedor.largura, ARSENAL.rebatedor.altura, ARSENAL.rebatedor.espessura]);
  r.dispose();
});

test('rebatedor: no cone do rim, com a frente para ele, e sem fazer sombra da key no tapete nem na roda', () => {
  const { r, scene, painel } = montar();
  const { centro, normal } = frente(painel);
  const pos = new THREE.Vector3(...fonte.position);
  const eixo = new THREE.Vector3(...fonte.target).sub(pos).normalize();
  const angulo = THREE.MathUtils.radToDeg(eixo.angleTo(centro.clone().sub(pos).normalize()));
  assert.ok(angulo < fonte.angleDeg * 0.8, `dentro do cone do ${fonte.id} (${angulo.toFixed(1)}° de ${fonte.angleDeg}°)`);
  assert.ok(normal.dot(pos.clone().sub(centro).normalize()) > 0.6, `a frente recebe o ${fonte.id}`);
  // a key (atrás do painel) chega a todo o tapete e ao prato da roda
  const kpos = new THREE.Vector3(...key.position);
  const rebatedor = [];
  r.group.traverse((o) => o.isMesh && rebatedor.push(o));
  const alvos = [new THREE.Vector3(ARSENAL.turntable.x, tableY + 30, ARSENAL.turntable.z)];
  for (let x = -D.mat.width / 2; x <= D.mat.width / 2; x += 50) {
    for (let z = D.mat.z - D.mat.depth / 2; z <= D.mat.z + D.mat.depth / 2; z += 50) alvos.push(new THREE.Vector3(x, tableY, z));
  }
  for (const alvo of alvos) {
    const hits = new THREE.Raycaster(kpos, alvo.clone().sub(kpos).normalize(), 0, alvo.distanceTo(kpos)).intersectObjects(rebatedor, true);
    assert.equal(hits.length, 0, `o rebatedor tapa a key em ${alvo.toArray().map(Math.round)}`);
  }
  scene.remove(r.group);
  r.dispose();
});

test('rebatedor: a placa assenta no tampo atrás do tapete — a borda de baixo encosta, sem entrar e sem flutuar', () => {
  const { r, painel } = montar();
  const p = painel.geometry.attributes.position;
  const v = new THREE.Vector3();
  let baixo = Infinity;
  const apoiados = [];
  for (let i = 0; i < p.count; i++) {
    v.fromBufferAttribute(p, i).applyMatrix4(painel.matrixWorld);
    if (v.y < baixo - 1e-6) {
      baixo = v.y;
      apoiados.length = 0;
    }
    // a BoxGeometry repete cada canto uma vez por face: conta os cantos, não os vértices
    if (Math.abs(v.y - baixo) < 1e-6 && !apoiados.some((a) => a.distanceTo(v) < 1e-6)) apoiados.push(v.clone());
  }
  // o tampo da mesa fica em y = 0 (src/data/showcase.js)
  assert.ok(Math.abs(baixo) < 0.01, `a borda de baixo a ${baixo.toFixed(2)} mm do tampo`);
  // a aresta que encosta (os dois cantos de baixo de trás: deitada para trás, a placa se apoia nela) fica na madeira:
  // dentro da mesa (longe da borda arredondada) e atrás da beira de trás do tapete — em cima dele, a placa entraria
  // 2,2 mm nele
  assert.equal(apoiados.length, 2, 'uma aresta inteira encosta');
  const beiraDoTapete = D.mat.z + D.mat.depth / 2;
  for (const a of apoiados) {
    const onde = a.toArray().map(Math.round);
    assert.ok(Math.abs(a.x) <= D.desk.width / 2 - 10 && Math.abs(a.z) <= D.desk.depth / 2 - 10, `canto fora da mesa em ${onde}`);
    assert.ok(a.z >= beiraDoTapete + 5, `canto no tapete em ${onde} (a beira de trás dele em z ${beiraDoTapete})`);
  }
  // e nenhum pedaço da placa dentro do tapete: pontos nos segmentos entre os cantos (a caixa é convexa, então cobrem as
  // arestas, as faces e o miolo)
  const cantos = [];
  for (let i = 0; i < p.count; i++) {
    v.fromBufferAttribute(p, i).applyMatrix4(painel.matrixWorld);
    if (!cantos.some((c) => c.distanceTo(v) < 1e-6)) cantos.push(v.clone());
  }
  assert.equal(cantos.length, 8);
  const tapete = new THREE.Box3(
    new THREE.Vector3(D.mat.x - D.mat.width / 2, 0, D.mat.z - D.mat.depth / 2),
    new THREE.Vector3(D.mat.x + D.mat.width / 2, tableY, D.mat.z + D.mat.depth / 2),
  );
  const q = new THREE.Vector3();
  for (let i = 0; i < 8; i++) {
    for (let j = i + 1; j < 8; j++) {
      for (let t = 0; t <= 1; t += 1 / 40) {
        q.lerpVectors(cantos[i], cantos[j], t);
        assert.ok(!tapete.containsPoint(q), `a placa entra no tapete em ${q.toArray().map((c) => c.toFixed(1))}`);
      }
    }
  }
  r.dispose();
});

test('rebatedor: o C-stand no chão do estúdio, fora da mesa', () => {
  const { r } = montar();
  const tripe = r.group.getObjectByName('c-stand');
  assert.ok(tripe, 'o tripé');
  const caixa = new THREE.Box3().setFromObject(tripe);
  assert.ok(Math.abs(caixa.min.y - D.floorY) < 1, 'os pés no chão');
  // a coluna (o que desce do tampo até o chão) passa fora da mesa: nenhum vértice do tripé dentro do volume do tampo
  const tampo = new THREE.Box3(new THREE.Vector3(-D.desk.width / 2, -D.desk.thickness, -D.desk.depth / 2), new THREE.Vector3(D.desk.width / 2, 0, D.desk.depth / 2));
  const v = new THREE.Vector3();
  tripe.traverse((o) => {
    if (!o.isMesh) return;
    const p = o.geometry.attributes.position;
    for (let i = 0; i < p.count; i++) {
      v.fromBufferAttribute(p, i).applyMatrix4(o.matrixWorld);
      assert.ok(!tampo.containsPoint(v), `vértice do tripé dentro do tampo em ${v.toArray().map(Math.round)}`);
    }
  });
  r.dispose();
});

test('rebatedor: isopor fosco, sem metal e sem boil; sai com o mapa sem levar os materiais do set', () => {
  const m = foamMaterial({});
  assert.equal(m.name, 'massacre.set.isopor');
  assert.ok(m.roughness >= 0.85 && m.metalness === 0);
  assert.ok(!m.userData?.boil, 'o set não pulsa');
  m.dispose();
  const { set, r } = montar();
  const geos = [];
  r.group.traverse((o) => o.isMesh && geos.push(o.geometry));
  let descartadas = 0;
  for (const g of geos) g.addEventListener('dispose', () => descartadas++);
  let materiais = 0;
  for (const mat of Object.values(set.mats)) mat.addEventListener('dispose', () => materiais++);
  r.dispose();
  assert.equal(descartadas, geos.length, 'todas as geometrias');
  assert.equal(materiais, 0, 'os materiais são da biblioteca (divididos)');
});
```

Run: `node --test tests/rebatedor.test.js`
Expected: FAIL — # tests 1 # pass 0 # fail 1 .

- [ ] **A implementação** — `src/maps/arsenal/rebatedor.js`, `src/clay/set/surfaceMaterials.js`, `src/clay/set/index.js`, `src/render/studio/fixtures.js`, `src/data/arsenal.js`, `src/maps/arsenal/index.js`:

```js file=src/maps/arsenal/rebatedor.js
// O rebatedor da bancada `arsenal` (Fase 4.1b; desenho da 4.1b, seção 7.6; plano, Tarefa 12): uma placa de isopor
// branco num C-stand, atrás de quem olha a bancada e virada para ela, como os rebatedores dos sets de estúdio (seção
// 0.9; item 3 do moodboard: o C-stand e as formas de luz das bordas, SSD14 e SMD7). O lado do receptor das armas
// realistas refletia o estúdio escuro atrás do olho e saía quase preto: a placa entra na foto do reflexo (a cena
// inteira, fotografada do olho do "Segurar", src/render/setReflection.js) e na vista da bancada.
//  - a placa: caixa de largura × altura × espessura (u = mm) com o isopor do set (`set.foam`), a frente (+Z local)
//    virada para a bissetriz, no plano horizontal, entre a luz que a acende (o `luz` da montagem, o rim) e o olho do
//    reflexo, deitada `inclinacao` graus para trás em volta do eixo de baixo dela — o cartão rebatedor de mesa, que
//    devolve a contraluz para a frente (os dados explicam a posição) — e com a borda de baixo assentada no apoio (o
//    tampo, atrás do tapete): a altura do centro sai da inclinação;
//  - o tripé: o C-stand do equipamento de luz (src/render/studio/fixtures.js), com o encaixe no meio das costas da placa
//    e a coluna `braco` para trás dela, no chão do estúdio (desce fora da mesa);
//  - fora da colisão (a bancada não tem); as geometrias saem com o mapa, os materiais são da biblioteca do set.

import * as THREE from 'three';
import { buildCStand } from '../../render/studio/fixtures.js';

/**
 * A direção da frente da placa em pé: a bissetriz entre a direção da luz e a do olho, a partir do centro dela, no plano
 * horizontal.
 * @param {THREE.Vector3} centro
 * @param {THREE.Vector3} olho
 * @param {THREE.Vector3} luz
 * @returns {THREE.Vector3} unitária
 */
export function frenteDoRebatedor(centro, olho, luz) {
  const paraOlho = olho.clone().sub(centro).normalize();
  const paraLuz = luz.clone().sub(centro).normalize();
  return paraOlho.add(paraLuz).setY(0).normalize();
}

/**
 * A altura do centro da placa acima do apoio com a borda de baixo encostada nele: só o giro em volta de Y (a frente no
 * plano horizontal) e a inclinação em volta do eixo de baixo; o giro em Y não muda a altura, e o ponto mais baixo é a
 * aresta de baixo de trás — deitada para trás, a placa se apoia nela — (a metade da altura pelo cosseno, a metade da
 * espessura pelo seno); a de baixo da frente fica a espessura pelo seno acima do apoio.
 * @param {{altura:number, espessura:number, inclinacao?:number}} def
 * @returns {number}
 */
export function alturaDoCentro(def) {
  const t = THREE.MathUtils.degToRad(def.inclinacao ?? 0);
  return (def.altura / 2) * Math.cos(t) + (def.espessura / 2) * Math.sin(t);
}

/**
 * @param {object} set a biblioteca de materiais do set (foam, blackMetal, chrome)
 * @param {object} def ARSENAL.rebatedor
 * @param {{floorY:number, apoioY:number, olho:THREE.Vector3, luz:THREE.Vector3}} ctx o chão do estúdio, a altura da
 *   superfície em que a placa assenta (o tampo), o olho do reflexo e a posição da luz que acende a placa (mundo)
 * @returns {{group:THREE.Group, painel:THREE.Mesh, dispose:()=>void}}
 */
export function construirRebatedor(set, def, { floorY, apoioY, olho, luz }) {
  const [x, z] = def.centro;
  const centro = new THREE.Vector3(x, apoioY + alturaDoCentro(def), z);
  const frente = frenteDoRebatedor(centro, olho, luz);
  const group = new THREE.Group();
  group.name = 'rebatedor';

  const painel = new THREE.Mesh(
    new THREE.BoxGeometry(def.largura, def.altura, def.espessura),
    set.foam({ color: def.cor, conta: def.conta }),
  );
  painel.name = 'rebatedor-painel';
  painel.position.copy(centro);
  painel.lookAt(centro.clone().add(frente)); // o +Z da placa na frente; o `up` do mundo deixa o lado de cima em pé
  painel.rotateX(-THREE.MathUtils.degToRad(def.inclinacao ?? 0)); // o topo deita para trás, a frente sobe
  painel.castShadow = true;
  painel.receiveShadow = true;
  group.add(painel);

  painel.updateMatrixWorld(true);
  const face = new THREE.Vector3(0, 0, 1).applyQuaternion(painel.quaternion);
  const encaixe = centro.clone().addScaledVector(face, -def.espessura / 2);
  const tripe = buildCStand(set, { mountWorld: encaixe, awayDir: face.clone().negate(), floorY, reach: def.braco });
  group.add(tripe.group);

  return {
    group,
    painel,
    dispose() {
      group.traverse((o) => {
        if (o.isMesh) o.geometry.dispose();
      });
      group.removeFromParent();
    },
  };
}
```

Em `src/clay/set/surfaceMaterials.js`, trocar:

```
//  - diffuser: frente da softbox / lente do fresnel / lâmpada (emissivo com ponto quente no centro e costura).

```

por:

```
//  - diffuser: frente da softbox / lente do fresnel / lâmpada (emissivo com ponto quente no centro e costura).
//  - foam: isopor expandido (EPS) branco das placas de rebater (Fase 4.1b, o rebatedor da bancada): as contas fundidas
//    de ~4 mm (célula de Voronoi 3D no espaço do objeto: cada conta abaulada, um tom próprio e o sulco raso entre elas),
//    bem fosco, sem metal; a conta some pelo filtro de frequência quando fica menor que o pixel (sem cintilar).

```

Em `src/clay/set/surfaceMaterials.js`, trocar:

```
diffuseColor.rgb = vec3(0.02);
`,
  });
}

```

por:

```
diffuseColor.rgb = vec3(0.02);
`,
  });
}

/**
 * Isopor (EPS) branco: contas fundidas de `conta` mm. Fosco (rugosidade 0,92), sem metal; o relevo da conta e o sulco
 * entre elas saem de uma célula de Voronoi 3D no espaço do objeto e somem pelo filtro de frequência de longe.
 */
export function foamMaterial(tex, { color = '#F2F1EC', conta = 4, name = 'isopor' } = {}) {
  return createSetMaterial({
    name,
    params: { color: 0xffffff, roughness: 0.92, metalness: 0 },
    uniforms: { uFoam: { value: linear(color) }, uConta: { value: conta } },
    light: { wrap: 0.3, lift: 0.06 },
    fragPars: 'uniform vec3 uFoam;\nuniform float uConta;',
    surface: /* glsl */ `
vec3 q = setP / uConta;
vec3 c = floor(q);
vec3 f = fract(q);
float d1 = 8.0;
float d2 = 8.0;
vec3 perto = vec3(0.0);
vec3 celula = c;
for (int k = -1; k <= 1; k++) {
  for (int j = -1; j <= 1; j++) {
    for (int i = -1; i <= 1; i++) {
      vec3 o = vec3(float(i), float(j), float(k));
      vec3 r = o + clayHash33(c + o) * 0.8 + 0.1 - f;
      float d = dot(r, r);
      if (d < d1) {
        d2 = d1;
        d1 = d;
        perto = r;
        celula = c + o;
      } else if (d < d2) {
        d2 = d;
      }
    }
  }
}
// 1 enquanto a conta tem uns pixels; 0 quando fica menor que o pixel (fica a média: o branco liso)
float filtro = 1.0 - smoothstep(0.25, 0.75, length(fwidth(q)));
float sulco = (1.0 - smoothstep(0.0, 0.14, sqrt(d2) - sqrt(d1))) * filtro;
float tom = (clayHash13(celula + 7.3) - 0.5) * 0.06 * filtro;
diffuseColor.rgb = uFoam * (1.0 + tom - sulco * 0.14);
setRough += sulco * 0.04;
// a conta abaulada: a normal inclina do centro dela para fora (perto aponta do ponto para o centro)
vec3 abaulado = -(perto - setN * dot(perto, setN)) * 0.5 * filtro;
setObjN = normalize(setN + abaulado);
`,
  });
}

```

Em `src/clay/set/index.js`, trocar:

```
// e a perda/recuperação do contexto WebGL (as texturas assadas precisam ser refeitas).
// Mapas pedem materiais aqui: set.cardboard(), set.tape({ width }), set.cuttingMat({ size }), ...
// Materiais que leem um atlas do próprio mapa (livros, desenhos, fita com etiquetas) são criados pelo mapa com as
```

por:

```
// e a perda/recuperação do contexto WebGL (as texturas assadas precisam ser refeitas).
// Mapas pedem materiais aqui: set.cardboard(), set.tape({ width }), set.cuttingMat({ size }), set.foam(), ...
// Materiais que leem um atlas do próprio mapa (livros, desenhos, fita com etiquetas) são criados pelo mapa com as
```

Em `src/clay/set/index.js`, trocar:

```
import { balsaMaterial, beechMaterial, benchWoodMaterial, plywoodMaterial } from './woodMaterials.js';
import { cuttingMatMaterial, plasticMaterial, fabricMaterial, diffuserMaterial } from './surfaceMaterials.js';
import { measureMaterial } from './measureMaterials.js';
```

por:

```
import { balsaMaterial, beechMaterial, benchWoodMaterial, plywoodMaterial } from './woodMaterials.js';
import { cuttingMatMaterial, plasticMaterial, fabricMaterial, diffuserMaterial, foamMaterial } from './surfaceMaterials.js';
import { measureMaterial } from './measureMaterials.js';
```

Em `src/clay/set/index.js`, trocar:

```
  diffuser: diffuserMaterial,
  measure: measureMaterial,
```

por:

```
  diffuser: diffuserMaterial,
  foam: foamMaterial,
  measure: measureMaterial,
```

Em `src/render/studio/fixtures.js`, trocar:

```
 * Tripé C-stand em espaço de mundo: da base no chão (floorY) até o ponto de encaixe `mountWorld`.
 * A coluna fica deslocada para trás (longe do alvo) e um braço horizontal vai até a luz.
 */
export function buildCStand(set, { mountWorld, awayDir, floorY }) {
  const away = awayDir.clone().setY(0).normalize();
  const columnPos = mountWorld.clone().addScaledVector(away, 70).setY(floorY);
  const top = mountWorld.y;
```

por:

```
 * Tripé C-stand em espaço de mundo: da base no chão (floorY) até o ponto de encaixe `mountWorld`.
 * A coluna fica deslocada para trás (longe do alvo) `reach` u e um braço horizontal vai até a luz (ou a placa).
 */
export function buildCStand(set, { mountWorld, awayDir, floorY, reach = 70 }) {
  const away = awayDir.clone().setY(0).normalize();
  const columnPos = mountWorld.clone().addScaledVector(away, reach).setY(floorY);
  const top = mountWorld.y;
```

Em `src/data/arsenal.js`, trocar:

```
  reflexo: F({ x: 0, z: 236 }),
  // Roda de modelar (QTT11): pé de metal pesado, coluna e prato torneado com anéis de centragem; gira devagar.
```

por:

```
  reflexo: F({ x: 0, z: 236 }),
  // Rebatedor (Fase 4.1b; desenho da 4.1b, seção 7.6): uma placa de isopor branco de 20 mm num C-stand, atrás de quem
  // olha a bancada e virada para ela — o lado do receptor das armas realistas refletia o estúdio escuro atrás do olho e
  // saía quase preto. Quem acende a placa é o `luz` da montagem (o rim: alto, do outro lado do set e apontando para cá,
  // é a única luz que chega pela frente ali; a key e o fill ficam atrás dela), e ela olha para a bissetriz entre essa luz
  // e o olho do reflexo, no plano horizontal, e deita `inclinacao` graus para trás (o cartão rebatedor de mesa do
  // estúdio de verdade, que devolve a contraluz para a frente). O lado do receptor virado para quem olha a roda
  // reflete, a partir do olho, a direção +Z um pouco para baixo (elevação −0,29): o tampo logo atrás dele. Medido na
  // bancada (a luminância do receptor): em pé na beira da mesa, a placa começava acima desse reflexo e clareava menos o
  // aço que alta e girada; deitada, a borda de baixo fica perto e rente ao tampo (cobre o centro do reflexo), a de
  // cima longe e alta — quase de frente para o rim — e abaixo dos raios da key que vão ao tapete (sem sombra na
  // bancada). `centro` = x e z do centro da placa; a altura sai da inclinação: a aresta de baixo de trás assenta no
  // tampo, na madeira atrás do tapete (girada para o rim, ela cruzaria a beira de trás do tapete em diagonal; o canto
  // mais perto fica 11 mm atrás dela, e a aresta de baixo da frente passa 6 mm acima do tapete). `braco` = do encaixe atrás da placa até a coluna do tripé (a coluna desce fora da
  // mesa); `conta` = o diâmetro das contas de isopor fundidas (mm).
  rebatedor: F({
    luz: 'rim',
    centro: F([0, 400]),
    largura: 700, altura: 220, espessura: 20, inclinacao: 25,
    braco: 150,
    conta: 4, cor: '#F2F1EC',
  }),
  // Roda de modelar (QTT11): pé de metal pesado, coluna e prato torneado com anéis de centragem; gira devagar.
```

Em `src/maps/arsenal/index.js`, trocar:

```
// também o banco do aceite das armas: forma, acabamento e skins, silhueta × planta, e o caminho do Blender (reler do
// disco).

```

por:

```
// também o banco do aceite das armas: forma, acabamento e skins, silhueta × planta, e o caminho do Blender (reler do
// disco). Na 4.1b, o rebatedor de isopor atrás de quem olha a bancada (rebatedor.js), aceso pelo rim: o lado do
// receptor das armas realistas refletia o estúdio escuro.

```

Em `src/maps/arsenal/index.js`, trocar:

```
import { createArsenalPanel } from './panel.js';

```

por:

```
import { createArsenalPanel } from './panel.js';
import { construirRebatedor } from './rebatedor.js';

```

Em `src/maps/arsenal/index.js`, trocar:

```

  // "Segurar": o viewmodel com a arma da roda (acento e nível da bancada) e a câmera parada no tapete, na altura do olho
```

por:

```

  // O rebatedor: a placa de isopor atrás do olho do "Segurar" (o ponto da foto do reflexo), acesa pela luz da montagem
  // que chega pela frente ali, assentada no tampo (y = 0) atrás do tapete; entra na foto do reflexo que o MatchState
  // tira com o mapa pronto.
  const olhoDoReflexo = new THREE.Vector3(ARSENAL.reflexo.x, ARSENAL.desk.mat.thickness + HULL.standEye, ARSENAL.reflexo.z);
  const luzDoRebatedor = rigDef.lights.find((l) => l.id === ARSENAL.rebatedor.luz);
  const rebatedor = construirRebatedor(services.set, ARSENAL.rebatedor, {
    floorY: ARSENAL.desk.floorY, apoioY: 0, olho: olhoDoReflexo, luz: new THREE.Vector3(...luzDoRebatedor.position),
  });
  scene.add(rebatedor.group);

  // "Segurar": o viewmodel com a arma da roda (acento e nível da bancada) e a câmera parada no tapete, na altura do olho
```

Em `src/maps/arsenal/index.js`, trocar:

```
  let holding = null;
  const holdSpec = () => ({ id: bench.state.id, faction: bench.state.faction, lod: bench.state.lod });
  const toggleHold = () => {
```

por:

```
  let holding = null;
  const holdSpec = () => ({ id: bench.state.id, faction: bench.state.faction, lod: bench.state.lod, gloves: bench.state.gloves });
  const toggleHold = () => {
```

Em `src/maps/arsenal/index.js`, trocar:

```
    staticShadows: false,
    reflection: new THREE.Vector3(ARSENAL.reflexo.x, ARSENAL.desk.mat.thickness + HULL.standEye, ARSENAL.reflexo.z),
    spawn: {
```

por:

```
    staticShadows: false,
    reflection: olhoDoReflexo.clone(),
    spawn: {
```

Em `src/maps/arsenal/index.js`, trocar:

```
          panel.refresh();
        } else if (spec.id !== holding.id || spec.faction !== holding.faction || spec.lod !== holding.lod) {
          holding = spec;
```

por:

```
          panel.refresh();
        } else if (spec.id !== holding.id || spec.faction !== holding.faction || spec.lod !== holding.lod || spec.gloves !== holding.gloves) {
          holding = spec;
```

Em `src/maps/arsenal/index.js`, trocar:

```
      panel.dispose();
      rig.dispose();
```

por:

```
      panel.dispose();
      rebatedor.dispose();
      rig.dispose();
```

Run: `node --test tests/rebatedor.test.js`
Expected: PASS — # tests 5 # pass 5 # fail 0 .

Run: `node --test "tests/**/*.test.js"`
Expected: PASS — # tests 454 # pass 454 # fail 0 .

### Tarefa 13: Documentos e memória

- [ ] **Passo 1: Regras** — `CLAUDE.md` e `CLAUDE.md.md`: a tabela de paridade e as regras 3 e 4 ("as armas e as luvas");
  a seção 0.7 "Mãos": luva tática realista no braço de massinha do boneco, sem roupa por enquanto; a seção 0.12: o
  boneco sem roupa, com o motivo (as próximas fases furam e atravessam o corpo de massa).
- [ ] **Passo 2: O desenho geral** — seções 5.1 ("Luvas (dois braços)"), 6.5 (zonas `couro`, `tecido`, `reforco`), 7
  (sem manga; o braço de massinha; o protetor de borracha) e 8.2 (o antebraço e a braçadeira de massinha ficam depois
  da 4.1d).
- [ ] **Passo 3: `docs/phases/phase-4.md`** (a linha da 4.1b) e o moodboard (seção 15: as referências da 4.1b e as
  medidas, cada uma com a decisão e o arquivo).
- [ ] **Passo 4: Memória** — `massacre-workflow-rules.md` já diz "o Blender gera as armas e as mãos"; conferir e
  acrescentar o "sem roupa por enquanto" se faltar.

Execução (2026-09-27):
- **Pedido novo do usuário na mesma rodada:** registrar no `.md` do projeto que o Blender pode pegar texturas de
  cgbookcase, Poly Haven, ambientCG e do CC0 Asset Index. Entrou como decisão de 2026-09-27: a regra 4 e a tabela de
  paridade (nenhum modelo de terceiros; texturas CC0 como base dos materiais, que chegam ao jogo só assadas) e a seção
  0.7 nova, "Texturas CC0 no Blender" (a lista, só CC0, a proveniência em `tools/blender/texturas/fontes.json`, a ficha
  do material dizendo qual usou); o mesmo no desenho geral (decisão 3 e seção 4.4), no `phase-4.md`, no `PROGRESS.md`
  e na seção 15 do moodboard. As quatro bibliotecas são CC0 (o índice valida a licença de cada registro). Nesta sessão
  da nuvem, a rede bloqueia cgbookcase, Poly Haven e ambientCG; só o índice no GitHub responde.
- **Passo 1:** `CLAUDE.md` e `CLAUDE.md.md` com o Mestre igual nos dois (conferido por `diff`): a tabela de paridade e
  as regras 3 e 4 em "as armas e as luvas", com o braço de massinha do punho para trás; a seção 0.7 "Mãos" (sem manga e
  sem roupa, o protetor de borracha, as cores por facção, a braçadeira de massa); a 0.12 com o "sem roupa por enquanto"
  e o motivo, e o viewmodel sem boil incluindo o antebraço de massinha.
- **Passo 2:** o desenho geral com cada mudança no lugar e o que era (seções 1, 2, 4.1, 4.4, 5.1 com as luvas medidas —
  6 748 triângulos por luva e 3,6 MB —, 5.3, 6.5, 7, 7.3 com a regra da mão da frente, 7.5, 8.1, 8.2 e 8.3). Na 8.2, o
  que sai no fim da 4.1d são só os arquivos da mão de 4 dedos (`handShape`, `handRig`, `handSkin`, `handLibrary`,
  `src/data/hands.js`): a pasta `src/characters/hands/` tem as luvas, o antebraço e a braçadeira, que ficam.
- **Passo 3:** `docs/phases/phase-4.md` (a linha da 4.1b, as decisões da 4.1b e as notas nas decisões 2 e 3 de
  2026-09-26) e a seção 15 do moodboard, que as fichas e o código já citavam e não existia (as fontes da ficha, os
  boards QTG, as buscas, a imagem do CS:GO, a medida do coiote, o rebatedor e as bibliotecas CC0). O `PROGRESS.md`
  ganhou a decisão das texturas e o resumo da 4.1b em andamento (o relatório entra na Tarefa 15).
- **Passo 4:** a memória (`massacre-workflow-rules.md`, `massacre-game-project.md`) é a do Windows e não existe nesta
  sessão da nuvem; fica para a próxima sessão no Windows, com o que acrescentar: "sem roupa por enquanto" (e o motivo),
  a regra da mão da frente, "uma mão só na tela" e as bibliotecas CC0 de texturas liberadas para o Blender.


**Código da tarefa** (a versão verificada no navegador e no Blender; os blocos `file=` são o arquivo inteiro, os pares são aplicados na ordem).

- [ ] **A implementação** — `CLAUDE.md`, `CLAUDE.md.md`, `docs/superpowers/specs/2026-09-26-armas-realistas-design.md`, `docs/superpowers/specs/2026-09-26-4.1b-luvas-e-empunhadura-design.md`, `docs/phases/phase-4.md`, `docs/art/moodboard.md`:

Em `CLAUDE.md`, trocar:

```
> Regra do usuário: nunca simplificar nada; sempre buscar referências de design e estética no Pinterest antes de trabalho visual.

```

por:

```
> Regra do usuário: nunca simplificar nada; sempre buscar referências de design e estética no Pinterest antes de trabalho visual.
> Texturas para o Blender: bibliotecas CC0 liberadas pelo usuário em 2026-09-27 (cgbookcase, Poly Haven, ambientCG e o CC0 Asset Index) — lista, regras e proveniência na seção 0.7, "Texturas CC0 no Blender".

```

Em `CLAUDE.md`, trocar:

```
|---|---|
| 100% gerado em código: sem arquivos de imagem, modelo ou áudio | Igual, com uma exceção decidida em 2026-09-26: **as armas e as mãos** (luvas e mangas) são modelos realistas construídos por scripts Python nossos no Blender (`tools/blender/armas/`) e entram no jogo como `.glb` + texturas `.webp` assadas (`assets/`). Nada é baixado de terceiros; o resto — geometria, texturas (canvas/shader), personagens, mapas, música e efeitos sonoros — continua procedural |
| FPS 3D em three.js | Igual |
```

por:

```
|---|---|
| 100% gerado em código: sem arquivos de imagem, modelo ou áudio | Igual, com uma exceção decidida em 2026-09-26: **as armas e as mãos** (as luvas; do punho para trás, o braço é o de massinha do boneco) são modelos realistas construídos por scripts Python nossos no Blender (`tools/blender/armas/`) e entram no jogo como `.glb` + texturas `.webp` assadas (`assets/`). Nenhum modelo é baixado de terceiros; desde 2026-09-27 o Blender pode usar texturas CC0 das bibliotecas abertas da seção 0.7 como base dos materiais, e elas chegam ao jogo só assadas no `.webp`. O resto — geometria, texturas (canvas/shader), personagens, mapas, música e efeitos sonoros — continua procedural |
| FPS 3D em three.js | Igual |
```

Em `CLAUDE.md`, trocar:

```
2. **Proibido placeholder.** Nada de `// TODO`, "implementar depois", cubos cinza, funções vazias, dados falsos ou "exemplo simplificado". Todo código entregue roda e está completo.
3. **Design e estética em primeiro lugar.** Cada elemento visível (boneco, mapa, HUD, menu, efeito, fonte) precisa parecer massinha de modelar filmada em stop-motion. Nada de visual genérico de "jogo de programador". **Exceção (2026-09-26): as armas e as mãos que as seguram são realistas** — metal, madeira e polímero de fábrica, muito detalhados e fiéis à arma real em tamanho e forma —, como adereços de metal em miniatura feitos pelo aderecista do estúdio (seção 0.7); as skins delas são de cor e acabamento (seção 0.15).
4. **Tudo procedural.** Sem baixar imagens, GLB, fontes decorativas ou áudio. Fontes do sistema/Google Fonts só como base; letreiros decorativos são geometria de massinha. **Exceção (2026-09-26), só para armas e mãos:** os modelos são construídos por scripts Python nossos no Blender (`tools/blender/armas/`, a partir de números medidos em fotos de licença livre — nenhum arquivo de terceiros entra no projeto) e exportados como `.glb` + `.webp` em `assets/`; qualquer outro modelo em arquivo precisa de nova decisão do usuário.
5. **Arquitetura modular** (seção 0.5). Nenhum arquivo acima de ~600 linhas; separe por responsabilidade.
```

por:

```
2. **Proibido placeholder.** Nada de `// TODO`, "implementar depois", cubos cinza, funções vazias, dados falsos ou "exemplo simplificado". Todo código entregue roda e está completo.
3. **Design e estética em primeiro lugar.** Cada elemento visível (boneco, mapa, HUD, menu, efeito, fonte) precisa parecer massinha de modelar filmada em stop-motion. Nada de visual genérico de "jogo de programador". **Exceção (2026-09-26): as armas e as luvas que as seguram são realistas** — metal, madeira e polímero de fábrica, couro sintético, tecido e borracha, muito detalhados e fiéis à arma real em tamanho e forma —, como adereços de metal em miniatura feitos pelo aderecista do estúdio (seção 0.7); do punho para trás, o braço é o de massinha do boneco; as skins delas são de cor e acabamento (seção 0.15).
4. **Tudo procedural.** Sem baixar imagens, GLB, fontes decorativas ou áudio. Fontes do sistema/Google Fonts só como base; letreiros decorativos são geometria de massinha. **Exceção (2026-09-26), só para as armas e as luvas:** os modelos são construídos por scripts Python nossos no Blender (`tools/blender/armas/`, a partir de números medidos em fotos de licença livre — nenhum modelo de terceiros entra no projeto) e exportados como `.glb` + `.webp` em `assets/`; qualquer outro modelo em arquivo precisa de nova decisão do usuário. **Texturas CC0 no Blender (decisão do usuário de 2026-09-27):** os scripts do Blender podem usar texturas de domínio público (CC0) das bibliotecas abertas listadas na seção 0.7 como base dos materiais das armas e das luvas; elas chegam ao jogo só assadas nas texturas `.webp`.
5. **Arquitetura modular** (seção 0.5). Nenhum arquivo acima de ~600 linhas; separe por responsabilidade.
```

Em `CLAUDE.md`, trocar:

```
- **Construção:** um script Python por arma no Blender (`tools/blender/armas/`), o modelo alto assado no de jogo (normal, sombra de contato, borda, variações), três níveis de detalhe, zonas de material (`corpo`, `guarnicao`, `carregador`, `detalhes`, `interno`), soquetes (boca, ejeção, carregador, miras, mãos) e peças móveis com o pivô real. **Sem boil** nas armas, mãos, carregadores, cápsulas, granadas e lunetas.
- **Carregador** de metal ou polímero de verdade, que o boneco tira e põe de volta na recarga. **Cápsulas** de latão que quicam e param no chão, amassando de leve a massinha do cenário.
```

por:

```
- **Construção:** um script Python por arma no Blender (`tools/blender/armas/`), o modelo alto assado no de jogo (normal, sombra de contato, borda, variações), três níveis de detalhe, zonas de material (`corpo`, `guarnicao`, `carregador`, `detalhes`, `interno`), soquetes (boca, ejeção, carregador, miras, mãos) e peças móveis com o pivô real. **Sem boil** nas armas, mãos, carregadores, cápsulas, granadas e lunetas.
- **Texturas CC0 no Blender (decisão do usuário de 2026-09-27):** os scripts do Blender podem pegar texturas de domínio público (CC0: sem atribuição obrigatória, uso comercial e modificação livres) como base dos materiais das armas e das luvas — o grão do couro e do polímero, a trama do tecido, a borracha, a madeira, o metal oxidado ou fosfatizado — nestas bibliotecas abertas:
  - **cgbookcase** — https://www.cgbookcase.com/textures (texturas PBR CC0);
  - **Poly Haven** — https://polyhaven.com/textures (CC0; por exemplo, plástico e borracha: https://polyhaven.com/textures/plastic-rubber);
  - **ambientCG** — https://ambientcg.com/list?type=substance&sort=popular (materiais CC0);
  - **CC0 Asset Index** — https://github.com/xiaoqianran/Blender-cc0-asset-index (catálogo de ~2 500 recursos CC0 validados, com a ferramenta `cc0a` que busca e baixa cada um com o `LICENSE.json` da proveniência).

  Como usar: só CC0, conferido na página de cada textura; cada textura usada fica registrada em `tools/blender/texturas/fontes.json` (site, página, nome, licença, data e resolução), com os arquivos ao lado, e a ficha do material diz qual usou e por quê. A textura entra só no Blender: o `construir` a assa com o resto e o jogo carrega apenas o `.webp` assado. Os modelos (`.blend`, `.glb`, `.fbx`) desses sites continuam fora — as armas e as luvas são construídas pelos nossos scripts —, e o resto do jogo (set, massinha, personagens) continua procedural (regra 4).
- **Carregador** de metal ou polímero de verdade, que o boneco tira e põe de volta na recarga. **Cápsulas** de latão que quicam e param no chão, amassando de leve a massinha do cenário.
```

Em `CLAUDE.md`, trocar:

```
- **Granadas:** reais (fragmentação, atordoante, fumaça, molotov de garrafa com pano, incendiária e decoy), com os efeitos de estúdio: a explosão em respingos de massa, a flash que "estoura" a tela em branco-massinha, a nuvem de algodão de set (fumaça volumétrica fake com sprites em camadas), o fogo de papel celofane laranja animado em stop-motion. Quicam com física e têm arremesso com carga (curto/médio/longo), como na referência.
- **Mãos:** luva tática de 5 dedos com a manga de tecido na cor do time (e a braçadeira), com a empunhadura resolvida por arma: nenhum dedo atravessando a arma nem flutuando.
- **Skins temáticas (futuro):** caneta, lápis, skate, arma de água e o que vier trocam o modelo inteiro no mesmo pipeline, com os mesmos soquetes, zonas e peças móveis da arma base (a espátula, a bola de massa, o pote de tinta, o pão de massa, as bolinhas amarelas e o anel de massinha da versão anterior ficam como ideias delas).
```

por:

```
- **Granadas:** reais (fragmentação, atordoante, fumaça, molotov de garrafa com pano, incendiária e decoy), com os efeitos de estúdio: a explosão em respingos de massa, a flash que "estoura" a tela em branco-massinha, a nuvem de algodão de set (fumaça volumétrica fake com sprites em camadas), o fogo de papel celofane laranja animado em stop-motion. Quicam com física e têm arremesso com carga (curto/médio/longo), como na referência.
- **Mãos:** luva tática realista de 5 dedos (Blender) no braço de massinha do próprio boneco — **sem manga e sem roupa por enquanto** (decisão do usuário de 2026-09-26, seção 0.12): do punho para trás, o antebraço é de massa, na cor da massa do boneco, sem boil no viewmodel —, com os nós cobertos por um protetor de borracha moldada, a cor por facção (Massa Crua coiote, Tropa do Estúdio preta) e a braçadeira do time como faixa de massa no antebraço, só em modo de time; a empunhadura é resolvida por arma: nenhum dedo atravessando a arma nem flutuando. **Mão da frente (regra do usuário de 2026-09-27):** em toda arma que tem mão da frente (guarda-mão, cano, telha), só o polegar fica de um lado da arma e os outros quatro dedos do outro, como a pega da AK no CS:GO — o polegar **reto e deitado** no lado esquerdo, encostado na arma e apontando para a frente, sem curva (a pega "thumb break"), e o indicador, o médio, o anelar e o mínimo abraçando por baixo até o lado direito, lado a lado (sem leque); o `construir` reprova a arma que sair diferente.
- **Skins temáticas (futuro):** caneta, lápis, skate, arma de água e o que vier trocam o modelo inteiro no mesmo pipeline, com os mesmos soquetes, zonas e peças móveis da arma base (a espátula, a bola de massa, o pote de tinta, o pão de massa, as bolinhas amarelas e o anel de massinha da versão anterior ficam como ideias delas).
```

Em `CLAUDE.md`, trocar:

```
- **Facções:** **Massa Crua** (TR, massas terracota, laranja e vermelho, bandanas de fita crepe) e **Tropa do Estúdio** (CT, azul, verde-água e branco, capacetes de tampinha de garrafa). Cada lado tem **5 modelos prontos** com silhuetas bem distintas (baixinho largo, alto magro, gordinho, etc.).
- **Criador de boneco:** proporções do corpo (sliders), cor da massa com mistura de duas cores (efeito marmorizado), olhos (botões, miçangas, olhos de massinha), boca, sobrancelhas, chapéus e acessórios de miniatura. Em partidas de time, o boneco ganha braçadeira e contorno na cor do time sem perder a personalização.
- **Animação stop-motion:** as animações dos personagens rodam "em dois" (12 poses/s) com leve variação de forma a cada pose ("boil"), enquanto a câmera e o input continuam a 60+ FPS. Squash & stretch em pulo, pouso, dano e morte. **O viewmodel (a arma e as mãos em primeira pessoa) anima suave, a 60+ FPS e sem boil** (decisão de 2026-09-26), com a opção "viewmodel em stop-motion" nas configurações: a mesma animação amostrada a 12 poses/s. O "em dois" continua nos bonecos em terceira pessoa, na killcam e nos menus.
- **Morte:** o boneco é atingido e **amassa** (achata como massa caindo na mesa) ou **se desfaz em pedaços de massa** com explosão; os pedaços grudam no chão por alguns segundos.
```

por:

```
- **Facções:** **Massa Crua** (TR, massas terracota, laranja e vermelho, bandanas de fita crepe) e **Tropa do Estúdio** (CT, azul, verde-água e branco, capacetes de tampinha de garrafa). Cada lado tem **5 modelos prontos** com silhuetas bem distintas (baixinho largo, alto magro, gordinho, etc.).
- **Sem roupa por enquanto** (decisão do usuário de 2026-09-26): o corpo de massinha fica à mostra — nenhuma roupa cobre o tronco, os braços ou as pernas —, porque nas próximas fases a bala fura o boneco e o tiro atravessa o corpo de massa, e o corpo não pode ficar escondido. Os acessórios de miniatura (bandana, capacete de tampinha, chapéus) continuam; em primeira pessoa, só a luva tática vai na mão (seção 0.7).
- **Criador de boneco:** proporções do corpo (sliders), cor da massa com mistura de duas cores (efeito marmorizado), olhos (botões, miçangas, olhos de massinha), boca, sobrancelhas, chapéus e acessórios de miniatura. Em partidas de time, o boneco ganha braçadeira e contorno na cor do time sem perder a personalização.
- **Animação stop-motion:** as animações dos personagens rodam "em dois" (12 poses/s) com leve variação de forma a cada pose ("boil"), enquanto a câmera e o input continuam a 60+ FPS. Squash & stretch em pulo, pouso, dano e morte. **O viewmodel (a arma, as luvas e o antebraço de massinha em primeira pessoa) anima suave, a 60+ FPS e sem boil** (decisão de 2026-09-26), com a opção "viewmodel em stop-motion" nas configurações: a mesma animação amostrada a 12 poses/s. O "em dois" continua nos bonecos em terceira pessoa, na killcam e nos menus.
- **Morte:** o boneco é atingido e **amassa** (achata como massa caindo na mesa) ou **se desfaz em pedaços de massa** com explosão; os pedaços grudam no chão por alguns segundos.
```

Em `CLAUDE.md.md`, trocar:

```
|---|---|
| 100% gerado em código: sem arquivos de imagem, modelo ou áudio | Igual, com uma exceção decidida em 2026-09-26: **as armas e as mãos** (luvas e mangas) são modelos realistas construídos por scripts Python nossos no Blender (`tools/blender/armas/`) e entram no jogo como `.glb` + texturas `.webp` assadas (`assets/`). Nada é baixado de terceiros; o resto — geometria, texturas (canvas/shader), personagens, mapas, música e efeitos sonoros — continua procedural |
| FPS 3D em three.js | Igual |
```

por:

```
|---|---|
| 100% gerado em código: sem arquivos de imagem, modelo ou áudio | Igual, com uma exceção decidida em 2026-09-26: **as armas e as mãos** (as luvas; do punho para trás, o braço é o de massinha do boneco) são modelos realistas construídos por scripts Python nossos no Blender (`tools/blender/armas/`) e entram no jogo como `.glb` + texturas `.webp` assadas (`assets/`). Nenhum modelo é baixado de terceiros; desde 2026-09-27 o Blender pode usar texturas CC0 das bibliotecas abertas da seção 0.7 como base dos materiais, e elas chegam ao jogo só assadas no `.webp`. O resto — geometria, texturas (canvas/shader), personagens, mapas, música e efeitos sonoros — continua procedural |
| FPS 3D em three.js | Igual |
```

Em `CLAUDE.md.md`, trocar:

```
2. **Proibido placeholder.** Nada de `// TODO`, "implementar depois", cubos cinza, funções vazias, dados falsos ou "exemplo simplificado". Todo código entregue roda e está completo.
3. **Design e estética em primeiro lugar.** Cada elemento visível (boneco, mapa, HUD, menu, efeito, fonte) precisa parecer massinha de modelar filmada em stop-motion. Nada de visual genérico de "jogo de programador". **Exceção (2026-09-26): as armas e as mãos que as seguram são realistas** — metal, madeira e polímero de fábrica, muito detalhados e fiéis à arma real em tamanho e forma —, como adereços de metal em miniatura feitos pelo aderecista do estúdio (seção 0.7); as skins delas são de cor e acabamento (seção 0.15).
4. **Tudo procedural.** Sem baixar imagens, GLB, fontes decorativas ou áudio. Fontes do sistema/Google Fonts só como base; letreiros decorativos são geometria de massinha. **Exceção (2026-09-26), só para armas e mãos:** os modelos são construídos por scripts Python nossos no Blender (`tools/blender/armas/`, a partir de números medidos em fotos de licença livre — nenhum arquivo de terceiros entra no projeto) e exportados como `.glb` + `.webp` em `assets/`; qualquer outro modelo em arquivo precisa de nova decisão do usuário.
5. **Arquitetura modular** (seção 0.5). Nenhum arquivo acima de ~600 linhas; separe por responsabilidade.
```

por:

```
2. **Proibido placeholder.** Nada de `// TODO`, "implementar depois", cubos cinza, funções vazias, dados falsos ou "exemplo simplificado". Todo código entregue roda e está completo.
3. **Design e estética em primeiro lugar.** Cada elemento visível (boneco, mapa, HUD, menu, efeito, fonte) precisa parecer massinha de modelar filmada em stop-motion. Nada de visual genérico de "jogo de programador". **Exceção (2026-09-26): as armas e as luvas que as seguram são realistas** — metal, madeira e polímero de fábrica, couro sintético, tecido e borracha, muito detalhados e fiéis à arma real em tamanho e forma —, como adereços de metal em miniatura feitos pelo aderecista do estúdio (seção 0.7); do punho para trás, o braço é o de massinha do boneco; as skins delas são de cor e acabamento (seção 0.15).
4. **Tudo procedural.** Sem baixar imagens, GLB, fontes decorativas ou áudio. Fontes do sistema/Google Fonts só como base; letreiros decorativos são geometria de massinha. **Exceção (2026-09-26), só para as armas e as luvas:** os modelos são construídos por scripts Python nossos no Blender (`tools/blender/armas/`, a partir de números medidos em fotos de licença livre — nenhum modelo de terceiros entra no projeto) e exportados como `.glb` + `.webp` em `assets/`; qualquer outro modelo em arquivo precisa de nova decisão do usuário. **Texturas CC0 no Blender (decisão do usuário de 2026-09-27):** os scripts do Blender podem usar texturas de domínio público (CC0) das bibliotecas abertas listadas na seção 0.7 como base dos materiais das armas e das luvas; elas chegam ao jogo só assadas nas texturas `.webp`.
5. **Arquitetura modular** (seção 0.5). Nenhum arquivo acima de ~600 linhas; separe por responsabilidade.
```

Em `CLAUDE.md.md`, trocar:

```
- **Construção:** um script Python por arma no Blender (`tools/blender/armas/`), o modelo alto assado no de jogo (normal, sombra de contato, borda, variações), três níveis de detalhe, zonas de material (`corpo`, `guarnicao`, `carregador`, `detalhes`, `interno`), soquetes (boca, ejeção, carregador, miras, mãos) e peças móveis com o pivô real. **Sem boil** nas armas, mãos, carregadores, cápsulas, granadas e lunetas.
- **Carregador** de metal ou polímero de verdade, que o boneco tira e põe de volta na recarga. **Cápsulas** de latão que quicam e param no chão, amassando de leve a massinha do cenário.
```

por:

```
- **Construção:** um script Python por arma no Blender (`tools/blender/armas/`), o modelo alto assado no de jogo (normal, sombra de contato, borda, variações), três níveis de detalhe, zonas de material (`corpo`, `guarnicao`, `carregador`, `detalhes`, `interno`), soquetes (boca, ejeção, carregador, miras, mãos) e peças móveis com o pivô real. **Sem boil** nas armas, mãos, carregadores, cápsulas, granadas e lunetas.
- **Texturas CC0 no Blender (decisão do usuário de 2026-09-27):** os scripts do Blender podem pegar texturas de domínio público (CC0: sem atribuição obrigatória, uso comercial e modificação livres) como base dos materiais das armas e das luvas — o grão do couro e do polímero, a trama do tecido, a borracha, a madeira, o metal oxidado ou fosfatizado — nestas bibliotecas abertas:
  - **cgbookcase** — https://www.cgbookcase.com/textures (texturas PBR CC0);
  - **Poly Haven** — https://polyhaven.com/textures (CC0; por exemplo, plástico e borracha: https://polyhaven.com/textures/plastic-rubber);
  - **ambientCG** — https://ambientcg.com/list?type=substance&sort=popular (materiais CC0);
  - **CC0 Asset Index** — https://github.com/xiaoqianran/Blender-cc0-asset-index (catálogo de ~2 500 recursos CC0 validados, com a ferramenta `cc0a` que busca e baixa cada um com o `LICENSE.json` da proveniência).

  Como usar: só CC0, conferido na página de cada textura; cada textura usada fica registrada em `tools/blender/texturas/fontes.json` (site, página, nome, licença, data e resolução), com os arquivos ao lado, e a ficha do material diz qual usou e por quê. A textura entra só no Blender: o `construir` a assa com o resto e o jogo carrega apenas o `.webp` assado. Os modelos (`.blend`, `.glb`, `.fbx`) desses sites continuam fora — as armas e as luvas são construídas pelos nossos scripts —, e o resto do jogo (set, massinha, personagens) continua procedural (regra 4).
- **Carregador** de metal ou polímero de verdade, que o boneco tira e põe de volta na recarga. **Cápsulas** de latão que quicam e param no chão, amassando de leve a massinha do cenário.
```

Em `CLAUDE.md.md`, trocar:

```
- **Granadas:** reais (fragmentação, atordoante, fumaça, molotov de garrafa com pano, incendiária e decoy), com os efeitos de estúdio: a explosão em respingos de massa, a flash que "estoura" a tela em branco-massinha, a nuvem de algodão de set (fumaça volumétrica fake com sprites em camadas), o fogo de papel celofane laranja animado em stop-motion. Quicam com física e têm arremesso com carga (curto/médio/longo), como na referência.
- **Mãos:** luva tática de 5 dedos com a manga de tecido na cor do time (e a braçadeira), com a empunhadura resolvida por arma: nenhum dedo atravessando a arma nem flutuando.
- **Skins temáticas (futuro):** caneta, lápis, skate, arma de água e o que vier trocam o modelo inteiro no mesmo pipeline, com os mesmos soquetes, zonas e peças móveis da arma base (a espátula, a bola de massa, o pote de tinta, o pão de massa, as bolinhas amarelas e o anel de massinha da versão anterior ficam como ideias delas).
```

por:

```
- **Granadas:** reais (fragmentação, atordoante, fumaça, molotov de garrafa com pano, incendiária e decoy), com os efeitos de estúdio: a explosão em respingos de massa, a flash que "estoura" a tela em branco-massinha, a nuvem de algodão de set (fumaça volumétrica fake com sprites em camadas), o fogo de papel celofane laranja animado em stop-motion. Quicam com física e têm arremesso com carga (curto/médio/longo), como na referência.
- **Mãos:** luva tática realista de 5 dedos (Blender) no braço de massinha do próprio boneco — **sem manga e sem roupa por enquanto** (decisão do usuário de 2026-09-26, seção 0.12): do punho para trás, o antebraço é de massa, na cor da massa do boneco, sem boil no viewmodel —, com os nós cobertos por um protetor de borracha moldada, a cor por facção (Massa Crua coiote, Tropa do Estúdio preta) e a braçadeira do time como faixa de massa no antebraço, só em modo de time; a empunhadura é resolvida por arma: nenhum dedo atravessando a arma nem flutuando. **Mão da frente (regra do usuário de 2026-09-27):** em toda arma que tem mão da frente (guarda-mão, cano, telha), só o polegar fica de um lado da arma e os outros quatro dedos do outro, como a pega da AK no CS:GO — o polegar **reto e deitado** no lado esquerdo, encostado na arma e apontando para a frente, sem curva (a pega "thumb break"), e o indicador, o médio, o anelar e o mínimo abraçando por baixo até o lado direito, lado a lado (sem leque); o `construir` reprova a arma que sair diferente.
- **Skins temáticas (futuro):** caneta, lápis, skate, arma de água e o que vier trocam o modelo inteiro no mesmo pipeline, com os mesmos soquetes, zonas e peças móveis da arma base (a espátula, a bola de massa, o pote de tinta, o pão de massa, as bolinhas amarelas e o anel de massinha da versão anterior ficam como ideias delas).
```

Em `CLAUDE.md.md`, trocar:

```
- **Facções:** **Massa Crua** (TR, massas terracota, laranja e vermelho, bandanas de fita crepe) e **Tropa do Estúdio** (CT, azul, verde-água e branco, capacetes de tampinha de garrafa). Cada lado tem **5 modelos prontos** com silhuetas bem distintas (baixinho largo, alto magro, gordinho, etc.).
- **Criador de boneco:** proporções do corpo (sliders), cor da massa com mistura de duas cores (efeito marmorizado), olhos (botões, miçangas, olhos de massinha), boca, sobrancelhas, chapéus e acessórios de miniatura. Em partidas de time, o boneco ganha braçadeira e contorno na cor do time sem perder a personalização.
- **Animação stop-motion:** as animações dos personagens rodam "em dois" (12 poses/s) com leve variação de forma a cada pose ("boil"), enquanto a câmera e o input continuam a 60+ FPS. Squash & stretch em pulo, pouso, dano e morte. **O viewmodel (a arma e as mãos em primeira pessoa) anima suave, a 60+ FPS e sem boil** (decisão de 2026-09-26), com a opção "viewmodel em stop-motion" nas configurações: a mesma animação amostrada a 12 poses/s. O "em dois" continua nos bonecos em terceira pessoa, na killcam e nos menus.
- **Morte:** o boneco é atingido e **amassa** (achata como massa caindo na mesa) ou **se desfaz em pedaços de massa** com explosão; os pedaços grudam no chão por alguns segundos.
```

por:

```
- **Facções:** **Massa Crua** (TR, massas terracota, laranja e vermelho, bandanas de fita crepe) e **Tropa do Estúdio** (CT, azul, verde-água e branco, capacetes de tampinha de garrafa). Cada lado tem **5 modelos prontos** com silhuetas bem distintas (baixinho largo, alto magro, gordinho, etc.).
- **Sem roupa por enquanto** (decisão do usuário de 2026-09-26): o corpo de massinha fica à mostra — nenhuma roupa cobre o tronco, os braços ou as pernas —, porque nas próximas fases a bala fura o boneco e o tiro atravessa o corpo de massa, e o corpo não pode ficar escondido. Os acessórios de miniatura (bandana, capacete de tampinha, chapéus) continuam; em primeira pessoa, só a luva tática vai na mão (seção 0.7).
- **Criador de boneco:** proporções do corpo (sliders), cor da massa com mistura de duas cores (efeito marmorizado), olhos (botões, miçangas, olhos de massinha), boca, sobrancelhas, chapéus e acessórios de miniatura. Em partidas de time, o boneco ganha braçadeira e contorno na cor do time sem perder a personalização.
- **Animação stop-motion:** as animações dos personagens rodam "em dois" (12 poses/s) com leve variação de forma a cada pose ("boil"), enquanto a câmera e o input continuam a 60+ FPS. Squash & stretch em pulo, pouso, dano e morte. **O viewmodel (a arma, as luvas e o antebraço de massinha em primeira pessoa) anima suave, a 60+ FPS e sem boil** (decisão de 2026-09-26), com a opção "viewmodel em stop-motion" nas configurações: a mesma animação amostrada a 12 poses/s. O "em dois" continua nos bonecos em terceira pessoa, na killcam e nos menus.
- **Morte:** o boneco é atingido e **amassa** (achata como massa caindo na mesa) ou **se desfaz em pedaços de massa** com explosão; os pedaços grudam no chão por alguns segundos.
```

Em `docs/superpowers/specs/2026-09-26-armas-realistas-design.md`, trocar:

```
  receita de SDF e o acento da facção nas armas), registrada em `docs/phases/phase-4.md`.
- **Referências:** `docs/art/moodboard.md`, seção 14 (boards QVM a QMP), e as fotos do Wikimedia Commons da seção 3.
```

por:

```
  receita de SDF e o acento da facção nas armas), registrada em `docs/phases/phase-4.md`.
- **Atualizado na 4.1b (2026-09-26 e 2026-09-27):** sem manga e sem roupa — a luva vai no braço de massinha do próprio
  boneco (desenho da 4.1b, `docs/superpowers/specs/2026-09-26-4.1b-luvas-e-empunhadura-design.md`, seção 0); a mão da
  frente com o polegar reto de um lado e os quatro dedos do outro; texturas CC0 de bibliotecas abertas como base dos
  materiais no Blender. As seções 1, 2, 4.1, 4.4, 5.1, 5.3, 6.5, 7, 8.1 e 8.2 trazem cada mudança no lugar, com o que era.
- **Referências:** `docs/art/moodboard.md`, seção 14 (boards QVM a QMP), e as fotos do Wikimedia Commons da seção 3.
```

Em `docs/superpowers/specs/2026-09-26-armas-realistas-design.md`, trocar:

```
   (parafusos exagerados, marcas de montagem).
2. **Luva tática de 5 dedos com a manga de tecido da facção** em primeira pessoa.
3. **Exceção à regra 4 (e à paridade "100% gerado em código") só para armas e mãos:** scripts Python nossos no
   Blender constroem os modelos e as texturas assadas, entregues como `.glb` e `.webp`. Nada é baixado de terceiros; o
   resto do jogo continua 100% procedural.
4. **Faca, granadas, carregadores e cápsulas, e lunetas passam a ser realistas.** A espátula, a bola de massa, o pote de
```

por:

```
   (parafusos exagerados, marcas de montagem).
2. **Luva tática de 5 dedos com a manga de tecido da facção** em primeira pessoa. **Atualizado na 4.1b (decisão do
   usuário de 2026-09-26): sem manga e sem roupa** — do punho para trás, o braço é o de massinha do boneco, porque nas
   próximas fases a bala fura o boneco e atravessa o corpo de massa, e o corpo não pode ficar escondido por roupa.
3. **Exceção à regra 4 (e à paridade "100% gerado em código") só para armas e mãos:** scripts Python nossos no
   Blender constroem os modelos e as texturas assadas, entregues como `.glb` e `.webp`. Nenhum modelo é baixado de
   terceiros; o resto do jogo continua 100% procedural. **Atualizado em 2026-09-27 (decisão do usuário):** os scripts
   do Blender podem usar texturas CC0 de bibliotecas abertas (cgbookcase, Poly Haven, ambientCG e o CC0 Asset Index)
   como base dos materiais, e elas chegam ao jogo só assadas no `.webp` (seção 4.4; a lista e as regras ficam na seção
   0.7 do `CLAUDE.md`).
4. **Faca, granadas, carregadores e cápsulas, e lunetas passam a ser realistas.** A espátula, a bola de massa, o pote de
```

Em `docs/superpowers/specs/2026-09-26-armas-realistas-design.md`, trocar:

```
  estúdio.
- **Boil zero** em armas, luvas, mangas, carregadores, cápsulas, granadas e lunetas. O resto do mundo mantém o boil (a
  opção de desligar já existe nas configurações).
```

por:

```
  estúdio.
- **Boil zero** em armas, luvas (e no antebraço de massinha delas no viewmodel, desde a 4.1b), carregadores, cápsulas,
  granadas e lunetas. O resto do mundo mantém o boil (a
  opção de desligar já existe nas configurações).
```

Em `docs/superpowers/specs/2026-09-26-armas-realistas-design.md`, trocar:

```
  seletor, números de série, marcas de prova), estampadas no metal.
- **Mãos:** luva tática de 5 dedos e manga de tecido na cor do time, com a braçadeira (seção 7). O "acento da facção" da
  4.1 sai das armas: a identidade do time fica na manga e na luva.
- **Itens que ficam realistas:** a faca, que é a baioneta M9 (EUA, 1986) de lâmina fixa (seção 3.2), granadas (fragmentação, atordoante,
```

por:

```
  seletor, números de série, marcas de prova), estampadas no metal.
- **Mãos:** luva tática de 5 dedos na cor da facção, no braço de massinha do boneco, com a braçadeira de massa em modo
  de time (seção 7; era "e manga de tecido na cor do time" até a 4.1b). O "acento da facção" da 4.1 sai das armas: a
  identidade do time fica na luva e na braçadeira.
- **Itens que ficam realistas:** a faca, que é a baioneta M9 (EUA, 1986) de lâmina fixa (seção 3.2), granadas (fragmentação, atordoante,
```

Em `docs/superpowers/specs/2026-09-26-armas-realistas-design.md`, trocar:

```
  - `exportar.py`: glTF, texturas e relatório; `validar.py`: as validações da seção 4.6; `conferir.py`: renders;
  - `maos.py` (luvas e mangas) e `empunhadura.py` (rig e solver, seção 7);
  - um script por arma: `ak47.py`, `glock.py`, `m4a4.py`, `faca.py`, `awp.py`, `nova.py`, `p90.py`.
```

por:

```
  - `exportar.py`: glTF, texturas e relatório; `validar.py`: as validações da seção 4.6; `conferir.py`: renders;
  - `maos.py` (as luvas; sem manga desde a 4.1b) e `empunhadura.py` (rig e solver, seção 7) — na 4.1b viraram
    `luvas.py` (o alvo do lançador), os módulos `maos_*.py` (malha, detalhes, modelo alto, rig, poses, medidas,
    contato) e `validar_maos.py`, e o solver em `empunhadura.py` com os módulos `empunhadura_*.py` (regras, arma,
    polegar, pega);
  - um script por arma: `ak47.py`, `glock.py`, `m4a4.py`, `faca.py`, `awp.py`, `nova.py`, `p90.py`.
```

Em `docs/superpowers/specs/2026-09-26-armas-realistas-design.md`, trocar:

```
  quantizados em degraus que não aparecem no jogo (2/255 na sombra, 4/255 na aspereza e na cor; decisão 8).
- **Tamanhos:** 2048 px para fuzis, escopetas e submetralhadoras e para as luvas; 1024 px para pistolas e a faca; 512
```

por:

```
  quantizados em degraus que não aparecem no jogo (2/255 na sombra, 4/255 na aspereza e na cor; decisão 8).
- **Texturas CC0 de base (decisão do usuário de 2026-09-27):** os materiais de fábrica do Blender podem partir de
  texturas de domínio público (CC0) de cgbookcase (https://www.cgbookcase.com/textures), Poly Haven
  (https://polyhaven.com/textures), ambientCG (https://ambientcg.com/list?type=substance&sort=popular) e do CC0 Asset
  Index (https://github.com/xiaoqianran/Blender-cc0-asset-index) — o grão do couro e do polímero, a trama do tecido, a
  borracha, a madeira, o metal. Só CC0, conferido na página de cada uma; cada textura usada fica registrada em
  `tools/blender/texturas/fontes.json` (site, página, nome, licença, data e resolução) e a ficha do material diz qual
  usou. Elas entram só no assar: o jogo carrega apenas `_n` e `_m`, e a cor continua vindo do acabamento.
- **Tamanhos:** 2048 px para fuzis, escopetas e submetralhadoras e para as luvas; 1024 px para pistolas e a faca; 512
```

Em `docs/superpowers/specs/2026-09-26-armas-realistas-design.md`, trocar:

```
| Faca | ≤ 8 mil | ≤ 1,5 mil | ≤ 400 | 2 × 1024² | 2 × 256² | ≤ 2 MB |
| Luvas e mangas (dois braços) | ≤ 14 mil | — (Fase 5) | — | 2 × 2048² | — | ≤ 6 MB |

```

por:

```
| Faca | ≤ 8 mil | ≤ 1,5 mil | ≤ 400 | 2 × 1024² | 2 × 256² | ≤ 2 MB |
| Luvas (dois braços; sem manga desde a 4.1b) | ≤ 14 mil | — (Fase 5) | — | 2 × 2048² | — | ≤ 6 MB |

```

Em `docs/superpowers/specs/2026-09-26-armas-realistas-design.md`, trocar:

```
fechavam com as texturas de 2048 sem perdas). A AK-47 tipo 3 medida: `.glb` 0,29 MB, `_n` 1,34 MB, `_m` 2,97 MB e o
conjunto do mundo 0,54 MB — 5,1 MB.

```

por:

```
fechavam com as texturas de 2048 sem perdas). A AK-47 tipo 3 medida: `.glb` 0,29 MB, `_n` 1,34 MB, `_m` 2,97 MB e o
conjunto do mundo 0,54 MB — 5,1 MB. As luvas medidas na 4.1b: 6 748 triângulos por luva (13 496 nos dois braços),
`luvas.glb` 0,34 MB, `_n` 1,69 MB e `_m` 1,61 MB — 3,6 MB.

```

Em `docs/superpowers/specs/2026-09-26-armas-realistas-design.md`, trocar:

```
  pede (verniz para brilhante, metálico, perolado, madeira e carbono; iridescência para perolado e anodizado;
  anisotropia para aço escovado; brilho de tecido para luvas e mangas), para limitar as variantes de shader; as
  variantes são compiladas no carregamento, sem travada na primeira aparição.
```

por:

```
  pede (verniz para brilhante, metálico, perolado, madeira e carbono; iridescência para perolado e anodizado;
  anisotropia para aço escovado; brilho de tecido para o tecido das luvas), para limitar as variantes de shader; as
  variantes são compiladas no carregamento, sem travada na primeira aparição.
```

Em `docs/superpowers/specs/2026-09-26-armas-realistas-design.md`, trocar:

```

As luvas e mangas também têm zonas (`couro`, `tecido`, `reforco`, `manga`), prontas para skins de luva.

## 7. Mãos: luvas, mangas e empunhadura

```

por:

```

As luvas também têm zonas, prontas para skins de luva: `couro` (palma, pontas e o reforço entre o polegar e o
indicador), `tecido` (costas e lados elásticos) e `reforco` (o protetor de borracha moldada dos nós, as almofadas e a
tira do punho). A zona `manga` saiu com a manga na 4.1b; a pintura de cada facção fica em `src/data/luvas.js`.

## 7. Mãos: luvas, braço de massinha e empunhadura

(Até a 4.1b: "luvas, mangas e empunhadura". O detalhe do que foi construído está no desenho da 4.1b.)

```

Em `docs/superpowers/specs/2026-09-26-armas-realistas-design.md`, trocar:

```
- Proporção humana real (comprimento da mão 190 mm, largura da palma 85 mm), feita por script: um esqueleto de juntas
  com raios (punho, palma, três falanges por dedo, polegar com o metacarpo) vira malha pelo modificador Skin, recebe
  subdivisão e a forma da luva.
- Detalhes: reforço acolchoado nos nós dos dedos, costuras aparentes (geometria no modelo alto, assada no relevo), palma
  antiderrapante, punho com tira de velcro, pontas reforçadas.
- Manga de tecido com dobras e o punho da manga, com a braçadeira do time (seção 0.12 da spec).
- Padrão por facção: Massa Crua com manga terracota e luva marrom; Tropa do Estúdio com manga azul e luva preta.

```

por:

```
- Proporção humana real (comprimento da mão 190 mm, largura da palma 85 mm), feita por script: um esqueleto de juntas
  com raios (punho, palma, três falanges por dedo, polegar com o metacarpo) vira malha, recebe subdivisão e a forma da
  luva. **Na 4.1b** a malha sai de um gerador de quadriláteros próprio (anéis elípticos em cada junta, portas na palma
  de onde saem os dedos) no lugar do modificador Skin, que torcia os quadriláteros onde os cinco dedos saem da palma.
- Detalhes: protetor de borracha moldada nos nós dos dedos (decisão do usuário de 2026-09-26, no lugar do reforço
  acolchoado), costuras aparentes (geometria no modelo alto, assada no relevo), palma antiderrapante, punho com tira de
  velcro, pontas reforçadas.
- **Sem manga e sem roupa** (decisão do usuário de 2026-09-26; era a manga de tecido com dobras e o punho da manga):
  do punho da luva para trás, o antebraço é de massinha, gerado em código (SDF), na cor da massa do boneco, com as
  digitais, a translucidez e o brilho de massinha e sem boil no viewmodel; a braçadeira do time é uma faixa de massa
  nele, só em modo de time (seção 0.12 da spec).
- Padrão por facção: Massa Crua com a luva coiote (couro `#5C5139`) e Tropa do Estúdio com a luva preta (era: manga
  terracota e luva marrom, manga azul e luva preta).

```

Em `docs/superpowers/specs/2026-09-26-armas-realistas-design.md`, trocar:

```
   nas pistolas, as duas mãos com os polegares para a frente; na faca, empunhadura de martelo.
4. Correções manuais por arma, quando precisar, ficam no script da arma e passam pelas mesmas validações.
```

por:

```
   nas pistolas, as duas mãos com os polegares para a frente; na faca, empunhadura de martelo.
   **Mão da frente (regra do usuário de 2026-09-27, válida para toda arma que tem mão da frente):** só o polegar fica de
   um lado da arma e os outros quatro dedos do outro, como a pega da AK no CS:GO — o polegar reto e deitado no lado
   esquerdo, encostado na arma e apontando para a frente, sem curva (a pega "thumb break"), e os quatro dedos abraçando
   por baixo até o lado direito, lado a lado (sem leque); a validação do `construir` reprova a arma que sair diferente
   (desenho da 4.1b, seção 6.2).
4. Correções manuais por arma, quando precisar, ficam no script da arma e passam pelas mesmas validações.
```

Em `docs/superpowers/specs/2026-09-26-armas-realistas-design.md`, trocar:

```
A decisão da 4.1 de mãos de 4 dedos de massinha para os bonecos é substituída: em terceira pessoa, os bonecos de
massinha usam as mesmas luvas e mangas, adaptadas às proporções deles.

```

por:

```
A decisão da 4.1 de mãos de 4 dedos de massinha para os bonecos é substituída: em terceira pessoa, os bonecos de
massinha usam as mesmas luvas, no braço de massinha deles e adaptadas às proporções deles (sem manga desde a 4.1b).

```

Em `docs/superpowers/specs/2026-09-26-armas-realistas-design.md`, trocar:

```
| 4.1a | Pipeline realista e a AK-47 tipo 3 no nível final: régua e ficha, biblioteca de peças, construir, assar, exportar e validar; `GLTFLoader` no vendor e o novo `weaponModels`; material com zonas e acabamentos, reflexo do set e luz do viewmodel; a AK na bancada `arsenal` e em primeira pessoa, ainda sem mãos (as de massinha não servem na geometria nova; as luvas chegam na 4.1b); comando `skin` e as três skins de exemplo; atualização das regras e da memória |
| 4.1b | Luvas, mangas, rig e o solver de empunhadura; a AK segurada em primeira pessoa |
| 4.1c | Glock-18, M4A4 e a faca — a baioneta M9 (EUA, 1986) — no caminho provado, com as empunhaduras |
```

por:

```
| 4.1a | Pipeline realista e a AK-47 tipo 3 no nível final: régua e ficha, biblioteca de peças, construir, assar, exportar e validar; `GLTFLoader` no vendor e o novo `weaponModels`; material com zonas e acabamentos, reflexo do set e luz do viewmodel; a AK na bancada `arsenal` e em primeira pessoa, ainda sem mãos (as de massinha não servem na geometria nova; as luvas chegam na 4.1b); comando `skin` e as três skins de exemplo; atualização das regras e da memória |
| 4.1b | Luvas no braço de massinha do boneco (sem manga e sem roupa, decisão de 2026-09-26), rig e o solver de empunhadura com a mão da frente em "thumb break"; a AK segurada em primeira pessoa, com uma mão só na tela (decisão de 2026-09-27); o rebatedor da bancada |
| 4.1c | Glock-18, M4A4 e a faca — a baioneta M9 (EUA, 1986) — no caminho provado, com as empunhaduras |
```

Em `docs/superpowers/specs/2026-09-26-armas-realistas-design.md`, trocar:

```
- **4.1b:** as luvas substituem as mãos de massinha na AK; as armas ainda de massinha continuam com as mãos de massinha.
- **4.1c e 4.1d:** cada arma refeita perde a receita e a planta antigas. No fim da 4.1d saem de vez o gerador de SDF das
  armas (`src/weapons/model/recipe.js`, `silhouette.js`, `weaponModel.js`), as receitas restantes, as mãos de massinha
  (`src/characters/hands/`, `src/data/hands.js`), a paleta de massinha das armas (`src/data/weaponPalette.js`) e o
  importador e exportador de receita do Blender (`tools/blender/massacre/`, `tools/blender/massacre_armas.py`), com os
  testes deles.
- **Fica:** as formas novas do SDF (perfil, torno, tubo), que servem para o cenário; o viewmodel (`src/weapons/viewmodel/`,
```

por:

```
- **4.1b:** as luvas substituem as mãos de massinha na AK; as armas ainda de massinha continuam com as mãos de massinha.
  O antebraço de massinha das luvas (`src/characters/hands/antebracoMassa.js`) e a braçadeira de massa (`armband.js`)
  são o braço do boneco: ficam depois da 4.1d.
- **4.1c e 4.1d:** cada arma refeita perde a receita e a planta antigas. No fim da 4.1d saem de vez o gerador de SDF das
  armas (`src/weapons/model/recipe.js`, `silhouette.js`, `weaponModel.js`), as receitas restantes, as mãos de 4 dedos
  de massinha (`src/characters/hands/handShape.js`, `handRig.js`, `handSkin.js`, `handLibrary.js` e
  `src/data/hands.js` — não a pasta inteira, que desde a 4.1b tem as luvas, o antebraço e a braçadeira), a paleta de
  massinha das armas (`src/data/weaponPalette.js`) e o importador e exportador de receita do Blender
  (`tools/blender/massacre/`, `tools/blender/massacre_armas.py`), com os testes deles.
- **Fica:** as formas novas do SDF (perfil, torno, tubo), que servem para o cenário; o viewmodel (`src/weapons/viewmodel/`,
```

Em `docs/superpowers/specs/2026-09-26-armas-realistas-design.md`, trocar:

```
  (`massacre-workflow-rules`: "o Blender gera os modelos das armas e das mãos por script").

```

por:

```
  (`massacre-workflow-rules`: "o Blender gera os modelos das armas e das mãos por script").
- **Atualizados na 4.1b:** as regras 3 e 4 e a tabela de paridade falam em luvas (do punho para trás, o braço de
  massinha); a seção 0.7 "Mãos" (sem manga e sem roupa, a regra da mão da frente) e a nova "Texturas CC0 no Blender"
  (2026-09-27); a seção 0.12 com o "sem roupa por enquanto" e o motivo; este desenho (seções 1, 2, 4, 5.1, 5.3, 6.5, 7,
  8.1 e 8.2).

```

Em `docs/superpowers/specs/2026-09-26-4.1b-luvas-e-empunhadura-design.md`, trocar:

```
   acompanha 2/3 da PIP (o acoplamento natural do dedo).
3. **Vizinhos:** se dois dedos se atravessam, a abertura na MCP corrige (±20°); se não bastar, o de fora recua.
4. **Regras da categoria `rifle`** (as das outras categorias entram com as armas delas):
```

por:

```
   acompanha 2/3 da PIP (o acoplamento natural do dedo).
3. **Vizinhos:** se dois dedos se atravessam, a abertura na MCP corrige (±20°); se não bastar, o de fora recua. O
   sentido da abertura "para fora" troca na mão esquerda, que é a direita espelhada (`empunhadura.para_fora`).
   **Dedos juntos (a revisão crítica da 4.1b, 2026-09-27):** fechando cada dedo sozinho a partir da abertura do
   repouso, os quatro da mão da frente saíam em leque pelo lado direito do guarda-mão (na AK, a falange média de um a
   4,5 a 8,5 mm da do vizinho e as pontas a 12 a 17 mm), e numa mão fechada de verdade os dedos dobrados convergem.
   Na regra da mão da frente (`juntar`), a partir do médio, o de fora gira na MCP para o vizinho (até os 20° da
   abertura) e fecha de novo na arma; fica a maior abertura em que ele não atravessa o vizinho nem entra na arma e em
   que a luva inteira não se atravessa mais que 0,15 mm (metade do limite da validação: a membrana entre os dedos, perto
   das MCP, amassa quando eles se juntam) — `empunhadura_arma.juntar_dedos`. Na AK: a falange média a 1,55 / 2,64 /
   6,77 mm da do vizinho (do indicador ao mínimo) e as pontas do indicador ao anelar a 2,6 e 3,7 mm; o mínimo, que
   dobra mais, fica com a ponta a 15,7 mm da do anelar, por cima do guarda-mão.
4. **Regras da categoria `rifle`** (as das outras categorias entram com as armas delas):
```

Em `docs/superpowers/specs/2026-09-26-4.1b-luvas-e-empunhadura-design.md`, trocar:

```
   - Mão esquerda: a palma por baixo do guarda-mão, os dedos abraçando pelo lado direito, o polegar pelo esquerdo.
5. **Correções por arma**, quando precisar, ficam no script da arma (`EMPUNHADURA = {...}`) e passam pelas mesmas
```

por:

```
   - Mão esquerda: a palma por baixo do guarda-mão, os dedos abraçando pelo lado direito, o polegar pelo esquerdo.
   - **Mão da frente, regra fixa do usuário (2026-09-27), para toda categoria:** só o polegar de um lado da arma e os
     quatro dedos do outro, como a pega da AK no CS:GO. O polegar fica **reto e deitado** na face esquerda, encostado
     nela e apontando para a frente e para cima, como na pega "thumb break" (os quatro dedos por baixo do guarda-mão e o
     polegar esticado ao longo do lado, apontando para o alvo): a IK dele zera a folga da falange proximal e da distal
     para a face ao longo do comprimento, aponta as duas para um eixo e cobra a curva (a MCP mais a IP) além de 12°. Duas
     versões recusadas pelo usuário: o polegar "o mais à esquerda possível" subia na vertical por cima do guarda-mão; a
     polpa mirando um ponto da face dobrava o polegar em arco (MCP 35°, IP 17°) com só a ponta encostada. A validação da
     seção 6.3 ganha, na mão da frente, os `lados` — a polpa do polegar e a de cada um dos quatro dedos a pelo menos 5 mm
     do plano do meio da arma, cada uma do seu lado (`LIMITES_DA_PEGA.ladoMM`) — e o polegar deitado: a curva até 20°, a
     falange distal encostando (até 1 mm) e nenhum trecho a mais de 8 mm (`polegarCurvaGraus`, `polegarFolgaMM`). O
     relatório diz qual é a mão da frente (`frente`), onde ficou cada polpa e a folga de cada trecho do polegar, e a
     validação da saída no Node repete as contas. A penetração da seção 6.3 passa a ser medida sem o limite de 6 mm das
     buscas do solver (um dedo inteiro dentro da arma passava despercebido).
5. **Correções por arma**, quando precisar, ficam no script da arma (`EMPUNHADURA = {...}`) e passam pelas mesmas
```

Em `docs/superpowers/specs/2026-09-26-4.1b-luvas-e-empunhadura-design.md`, trocar:

```
- **Contato:** cada contato da regra (as polpas e a palma) a no máximo 1 mm da superfície.
- **Dedos:** nenhum a mais de 0,3 mm dentro de outro; todos os ângulos dentro dos limites.
- **Conferência:** vistas de perto de cada mão no `conferir` da arma.
```

por:

```
- **Contato:** cada contato da regra (as polpas e a palma) a no máximo 1 mm da superfície.
- **Dedos:** nenhum a mais de 0,3 mm dentro de outro; todos os ângulos dentro dos limites; os que abraçam a arma lado
  a lado, sem leque — a falange média de cada um a no máximo 8 mm da do vizinho (`LIMITES_DA_PEGA.dedosJuntosMM`, menos
  da metade da largura dela; a ponta não conta, porque o dedo que dobra mais sai da ponta do vizinho), nas duas mãos,
  com o relatório trazendo a folga de cada par (`juntosMM`) e a validação da saída no Node repetindo a conta.
- **Conferência:** vistas de perto de cada mão no `conferir` da arma.
```

Em `docs/superpowers/specs/2026-09-26-4.1b-luvas-e-empunhadura-design.md`, trocar:

```
|---|---|---|---|
| Massa Crua (TR) | couro `#8B6B4A` (coiote) | tecido `#6B5038` | borracha `#4A3A2C` |
| Tropa do Estúdio (CT) | couro `#1D1D1F` | tecido `#232326` | borracha `#2C2D30` |
```

por:

```
|---|---|---|---|
| Massa Crua (TR) | couro `#5C5139` (coiote; era `#8B6B4A`) | tecido `#4D4432` (era `#6B5038`) | borracha `#342E24` (era `#4A3A2C`) |
| Tropa do Estúdio (CT) | couro `#1D1D1F` | tecido `#232326` | borracha `#2C2D30` |
```

Em `docs/superpowers/specs/2026-09-26-4.1b-luvas-e-empunhadura-design.md`, trocar:

```

## 8. Testes e aceite
```

por:

```

Execução (2026-09-27): a placa (700 × 220 × 20 mm, isopor expandido com as contas de 4 mm fundidas, o material novo
`set.foam`) num C-stand cuja coluna desce fora da mesa. Quem a acende é o **rim** da vitrine: a key e o fill ficam atrás
do lugar dela (z de 520 a 560), então uma placa virada para a bancada as receberia pelas costas; o rim, alto e do outro
lado do set, chega pela frente. A frente olha para a bissetriz entre o rim e o olho do reflexo, no plano horizontal, e a
placa deita 25° para trás — o cartão rebatedor de mesa dos estúdios — apoiada na aresta de baixo de trás, no tampo, na
madeira logo atrás do tapete (a altura do centro sai da inclinação; girada para o rim, a aresta cruzaria a beira de trás
do tapete em diagonal: o canto mais perto fica 11 mm atrás dela, e a aresta de baixo da frente passa 6 mm acima do
tapete).

Por que deitada: o lado do receptor virado para quem olha a roda reflete, a partir do olho do reflexo, a direção +Z um
pouco para baixo (elevação −0,29) — o tampo logo atrás do olho. As duas primeiras posições medidas (alta e girada, e em
pé na beira da mesa com 600 × 360) começavam acima desse reflexo e clarearam pouco o aço. Deitada, a borda de baixo fica
perto e rente ao tampo (a placa cobre ≥ 60 % de um cone de 25° em volta do reflexo; o teste confere), e a de cima fica
longe, quase de frente para o rim e abaixo dos raios da key que vão ao tapete — nenhuma sombra dela na bancada (o teste
confere o tapete inteiro numa grade de 5 cm e o prato da roda).

Medido (a luminância média de um recorte do lado do receptor da AK na roda, a mesma vista, SwiftShader no preset leve):

| Roda | Antes | Alta e girada | Em pé na beira | Deitada (final) |
|---|---|---|---|---|
| 0 | 0,0024 | 0,0127 | 0,0089 | 0,0390 (16×) |
| π | 0,0004 | 0,0049 | 0,0029 | 0,0269 (60×) |

O "Segurar" (a arma na mão, a arma perto do olho) já não saía preto, e muda pouco: 0,0347 → 0,0354. Na bancada, o aço
do receptor e do carregador lê como aço escurecido, não mais preto chapado (as nervuras do carregador aparecem), e a
madeira não muda.

## 8. Testes e aceite
```

Em `docs/phases/phase-4.md`, trocar:

```
| 4.1a | Pipeline realista e a AK-47 tipo 3 no nível final: régua e ficha, biblioteca de peças, construir, assar, exportar e validar; `GLTFLoader` no vendor e o novo `weaponModels`; material com zonas e acabamentos, reflexo do set e luz do viewmodel; a AK na bancada `arsenal` e em primeira pessoa, ainda sem mãos; comando `skin` e as três skins de exemplo; atualização das regras e da memória | ✅ 2026-09-26 |
| 4.1b | Luvas, mangas, rig e o solver de empunhadura; a AK segurada em primeira pessoa | a fazer |
| 4.1c | Glock-18, M4A4 e a faca — a baioneta M9 (EUA, 1986) — no caminho provado, com as empunhaduras | a fazer |
```

por:

```
| 4.1a | Pipeline realista e a AK-47 tipo 3 no nível final: régua e ficha, biblioteca de peças, construir, assar, exportar e validar; `GLTFLoader` no vendor e o novo `weaponModels`; material com zonas e acabamentos, reflexo do set e luz do viewmodel; a AK na bancada `arsenal` e em primeira pessoa, ainda sem mãos; comando `skin` e as três skins de exemplo; atualização das regras e da memória | ✅ 2026-09-26 |
| 4.1b | Luvas táticas realistas no braço de massinha do boneco (sem manga e sem roupa), rig de 20 ossos por braço e o solver de empunhadura dentro do `construir` da arma, com a mão da frente em "thumb break" (o polegar reto e deitado de um lado, os quatro dedos do outro); a AK segurada em primeira pessoa nas duas facções, com uma mão só na tela; os comandos `luvas` e `luvas_contato`; o rebatedor de isopor da bancada — desenho em `docs/superpowers/specs/2026-09-26-4.1b-luvas-e-empunhadura-design.md` | ✅ 2026-09-27 (aceite: `luvas_contato` a 0,02 mm do Blender nas duas facções e nas três posições, memória estável; o FPS na máquina do usuário a medir) |
| 4.1c | Glock-18, M4A4 e a faca — a baioneta M9 (EUA, 1986) — no caminho provado, com as empunhaduras | a fazer |
```

Em `docs/phases/phase-4.md`, trocar:

```

## Decisões do usuário (2026-09-26) — armas realistas
```

por:

```

## Decisões do usuário (2026-09-26 e 2026-09-27) — luvas e empunhadura (4.1b)

Desenho em `docs/superpowers/specs/2026-09-26-4.1b-luvas-e-empunhadura-design.md` (aprovado na parada da 4.1a); plano
em `docs/superpowers/plans/2026-09-26-4.1b-luvas-e-empunhadura.md`.

1. **Sem roupa por enquanto** (2026-09-26): nas próximas fases a bala fura o boneco de massinha e o tiro atravessa o
   corpo de massa, "e muito mais"; o corpo não pode ficar escondido por roupa. Em primeira pessoa, a luva tática
   realista (Blender) na mão e, do punho para trás, o braço de massinha do boneco, em código, na cor da massa dele.
2. **O antebraço de massinha não pulsa** no viewmodel (sem boil), como a arma e a luva; mantém as digitais, a
   translucidez e o brilho de massinha.
3. **A braçadeira do time** continua, como faixa de massa no antebraço, só em modo de time.
4. **Os nós da luva com protetor de borracha moldada** (do tipo das luvas táticas mais comuns), no lugar do reforço
   acolchoado.
5. **Rebatedor branco** atrás de quem olha a bancada `arsenal`: o lado do receptor da AK saía quase preto.
6. **A mão da frente** (2026-09-27, na parada P2): em toda arma que tem mão da frente, só o polegar fica de um lado e os
   outros quatro dedos do outro, como a AK no CS:GO — o polegar reto, deitado e encostado na arma, apontando para a
   frente, sem curva. O `construir` reprova a arma que sair diferente.
7. **Uma mão só na tela** (2026-09-27): nas três posições prontas do CS, só a mão da frente aparece, como na imagem de
   referência do CS:GO; a mão do gatilho continua montada (inspeção na 4.3, terceira pessoa na Fase 5).
8. **Texturas CC0 no Blender** (2026-09-27): os scripts do Blender podem usar texturas de domínio público de
   cgbookcase, Poly Haven, ambientCG e do CC0 Asset Index como base dos materiais das armas e das luvas; elas chegam ao
   jogo só assadas no `.webp`, e modelos de terceiros continuam fora (a lista e as regras ficam na seção 0.7 do
   `CLAUDE.md`, "Texturas CC0 no Blender").

## Decisões do usuário (2026-09-26) — armas realistas
```

Em `docs/phases/phase-4.md`, trocar:

```
2. **Luva tática de 5 dedos com a manga de tecido da facção** em primeira pessoa (e nos bonecos em terceira pessoa, na
   Fase 5).
3. **Exceção à regra 4 (e à paridade "100% gerado em código") só para armas e mãos:** scripts Python nossos no Blender
   constroem os modelos e as texturas assadas, entregues como `.glb` e `.webp`. Nada é baixado de terceiros.
4. **Faca, granadas, carregadores e cápsulas, e lunetas passam a ser realistas.** As versões de massinha ficam como
```

por:

```
2. **Luva tática de 5 dedos com a manga de tecido da facção** em primeira pessoa (e nos bonecos em terceira pessoa, na
   Fase 5). *Mudado na 4.1b (abaixo): sem manga e sem roupa — a luva no braço de massinha do boneco.*
3. **Exceção à regra 4 (e à paridade "100% gerado em código") só para armas e mãos:** scripts Python nossos no Blender
   constroem os modelos e as texturas assadas, entregues como `.glb` e `.webp`. Nada é baixado de terceiros. *Mudado
   em 2026-09-27 (abaixo): nenhum modelo de terceiros, mas texturas CC0 de bibliotecas abertas podem servir de base dos
   materiais no Blender.*
4. **Faca, granadas, carregadores e cápsulas, e lunetas passam a ser realistas.** As versões de massinha ficam como
```

Em `docs/art/moodboard.md`, trocar:

```
da 4.1b a 4.1d e são estudados em cada subfase.

```

por:

```
da 4.1b a 4.1d e são estudados em cada subfase.

## 15. Luvas, braço de massinha e empunhadura (subfase 4.1b, 2026-09-26 e 2026-09-27)

A luva tática realista de 5 dedos, feita por script no Blender, no braço de massinha do boneco (sem manga e sem roupa
por decisão do usuário: nas próximas fases a bala fura o boneco e atravessa o corpo de massa). As medidas da mão vêm de
levantamentos antropométricos e de radiografia, cada número com a fonte na ficha (`tools/blender/refs/luvas.json`); a
construção da luva vem dos boards QTG (luvas táticas reais), QGL e QFH da seção 14 e de duas buscas do Pinterest. Na
parada P2 (2026-09-27), a pega da mão da frente passou a seguir a imagem da AK no CS:GO que o usuário mandou; nessa
sessão (na nuvem) o Pinterest e os sites de tiro estavam bloqueados pela rede, e a pega "thumb break" foi conferida por
busca de texto. Desenho completo em `docs/superpowers/specs/2026-09-26-4.1b-luvas-e-empunhadura-design.md`.

| Observação | Referências | Decisão (arquivo) |
|---|---|---|
| A mão média de um adulto: 189,3 mm do pulso à ponta do médio, 85,0 mm de largura nos nós, 169,0 mm de volta no pulso. | ANSUR II (Exército dos EUA, 2012; N = 6 068, homens e mulheres), tabela do benchmark Sota2; as medianas do antebraço flexionado e do pulso no Data Explorer do OPEN Design Lab (Penn State) | A mão da ficha e o antebraço de massinha na mesma seção do punho da luva (`tools/blender/refs/luvas.json`, `tools/blender/armas/maos.py`, `src/characters/hands/antebracoMassa.js`). |
| Os comprimentos entre as juntas de cada dedo, medidos em radiografia. | Buryanov e Kotiuk (2010), *Int. J. Morphol.* 28(3), 66 adultos | Os ossos do esqueleto da luva, falange a falange (`luvas.json`, `ossos`; `maos.py`). |
| A largura e a volta de cada dedo nas juntas (IP, PIP e DIP). | Greiner (1991), levantamento de mãos do Exército dos EUA (Natick TR-92/011) | Os anéis elípticos do gerador de quadriláteros, na escala da mão da ficha (`luvas.json`, `juntas`; `maos.py`). |
| Quanto cada junta dobra: dedos, polegar, pulso e a torção do antebraço; e a rotação do metacarpo do polegar que vira a polpa para os dedos ao fechar. | AAOS (amplitude normal das juntas); Cooney et al. (1981), a cinemática da CMC do polegar (17° de rotação axial) | Os limites do rig e do solver, e o teste do viewmodel que deixa cada ângulo do pulso a no máximo 93 % do limite (`luvas.json`, `limites`, `rotacaoDoPolegar`; `maos_rig.py`, `empunhadura_*.py`; `src/data/viewmodel.js`). |
| A luva tática de verdade: tecido elástico nas costas e nos lados, couro sintético na palma e nas pontas, almofadas nas falanges, protetor de borracha moldada com um domo por nó unido por uma ponte, e a tira larga do punho com o puxador do lado do mínimo. | QTG0–QTG3; busca "tactical gloves knuckle protection close up"; busca "mechanix m-pact glove knuckle" (o TPR moldado) | As zonas `couro`, `tecido` e `reforco`; o protetor dos nós no lugar do reforço acolchoado do desenho geral (decisão do usuário); as almofadas e a tira na geometria de jogo, porque fazem silhueta (`maos_detalhes.py`, `maos_gaiola.py`). |
| De perto: costura dupla nas bordas dos painéis, fendas de respiro nos domos, nervuras nas guardas dos dedos, o grão do couro e a trama do tecido. | QTG0–QTG3; as fotos do TPR moldado | Só no modelo alto, assados no relevo (`maos_alto.py`); o grão em "seixinhos" arredondados com o vale largo e raso (`armaGrao`, `src/weapons/model/glsl/acabamentos.js`), depois que a P2 viu o primeiro padrão como couro craquelado. |
| A mão da frente na AK do CS:GO: só o polegar de um lado do guarda-mão, reto e deitado ao longo dele, apontando para a frente, e os outros quatro dedos abraçando por baixo até o outro lado — a pega "thumb break". | A imagem do CS:GO mandada pelo usuário (P2, 2026-09-27); a descrição da pega "thumb break" (busca de texto) | Regra do usuário para toda arma com mão da frente: a regra `FRENTE` e o polegar deitado pela IK (`empunhadura_regras.py`, `empunhadura_polegar.deitar_na_arma`); o `construir` e a leitura no jogo reprovam o polegar com mais de 20° de curva ou a mais de 8 mm da arma, e cada ponta de dedo a menos de 5 mm do meio da arma do lado errado (`empunhadura_pega.py`, `tools/blender/saidaPega.mjs`, `LIMITES_DA_PEGA` em `src/data/luvas.js`). Na AK: curva 0°, polegar +20,1 mm, dedos −16,5 a −25,6 mm. |
| Na mesma imagem, a mão do gatilho fica fora do quadro: só a da frente aparece. | A imagem do CS:GO mandada pelo usuário | Decisão do usuário: uma mão só na tela nas três posições prontas; a mão do gatilho continua montada e com a pega resolvida, e vai aparecer na inspeção (4.3) e em terceira pessoa (Fase 5) (`src/data/viewmodel.js`). |
| O coiote de partida saía no mesmo laranja da madeira da AK na luz quente da bancada (1,20× de luminância). | Medida no jogo (a pista, SwiftShader); as luvas coiote dos boards QTG | Coiote mais escuro e puxado para o oliva: couro `#5C5139`, tecido `#4D4432`, borracha `#342E24`; o teste exige a luva a no máximo 60 % da luminância da madeira e a 12° de matiz dela (`src/data/luvas.js`, `tests/luvasDados.test.js`). |
| O lado do receptor da AK na roda refletia o estúdio escuro atrás do olho e saía quase preto; os sets de verdade põem rebatedores brancos (isopor, placas de espuma) para devolver a luz. | Seção 3 (o C-stand e as formas de luz nas bordas, SSD14, SMD7) | A placa de isopor de 700 × 220 × 20 mm num C-stand, deitada 25° para trás e acesa pelo rim: o receptor de 0,0024 para 0,0390 (16×) e de 0,0004 para 0,0269 (60×) de luminância, sem sombra na bancada (`src/maps/arsenal/rebatedor.js`, `set.foam` em `src/clay/set/surfaceMaterials.js`). |
| Bibliotecas abertas de texturas CC0 (domínio público: sem atribuição, uso comercial e modificação livres) para os materiais do Blender. | cgbookcase (https://www.cgbookcase.com/textures), Poly Haven (https://polyhaven.com/textures, por exemplo https://polyhaven.com/textures/plastic-rubber), ambientCG (https://ambientcg.com/list?type=substance&sort=popular) e o CC0 Asset Index (https://github.com/xiaoqianran/Blender-cc0-asset-index) | Liberadas pelo usuário em 2026-09-27 como base dos materiais das armas e das luvas no Blender, só CC0 e com a proveniência em `tools/blender/texturas/fontes.json`; chegam ao jogo só assadas no `.webp` (`CLAUDE.md`, seção 0.7, "Texturas CC0 no Blender"). |

```

Run: `node --test "tests/**/*.test.js"`
Expected: PASS — # tests 454 # pass 454 # fail 0 .

### Tarefa 14: Aceite no navegador e revisão crítica

- [ ] **Passo 1:** console limpo na bancada e na pista.
- [ ] **Passo 2:** a AK segurada nas duas facções, nas três posições prontas do CS, de perto de cada mão; nenhum dedo
  atravessando nem flutuando (`luvas_contato` ≤ 0,3 mm de penetração e ≤ 1 mm nos contatos).
- [ ] **Passo 3:** desempenho e memória como na 4.1a (FPS e quadro p95 na pista com a AK; ciclos menu → bancada → pista
  com a memória estável; trocar 20 vezes de arma entre a AK e as de massinha).
- [ ] **Passo 4:** o Blender e o jogo lado a lado (as vistas de perto das mãos).
- [ ] **Passo 5:** revisão crítica até não sobrar defeito; o que ficar de fora, registrado com o porquê.

Execução (2026-09-27, sessão da nuvem: Chromium com SwiftShader no preset Leve a 0,75 da resolução — no Médio a página
caía ao carregar as luvas —, o Blender 5.2.2 do PyPI):
- **Passo 1 — console:** na pista, na bancada e nos ciclos, nenhum erro do jogo. Só o certificado das fontes do Google
  (o proxy da nuvem corta: `ERR_CERT_AUTHORITY_INVALID`) e o aviso do three de que o SwiftShader não tem a extensão
  `KHR_parallel_shader_compile`.
- **Passo 2 — a AK nas duas facções e nas três posições prontas:** `luvas_contato` igual nas seis — direita entra 0,05
  mm (Blender 0,04), esquerda 0,06 mm (Blender 0,05), cada contato a no máximo 0,03 mm da arma e a pior diferença para
  o Blender 0,02 mm (limites: 0,3 mm, 1 mm e 0,05 mm); a marca da arma bate com a das luvas; uma mão só na tela, o
  polegar deitado no lado esquerdo do guarda-mão e os dedos do outro lado, como na referência.
- **Passo 3 — memória:** do segundo ciclo em diante, os mesmos números em cada parada (geometrias/texturas/programas):
  menu 32/26/49, bancada 109/35/66, pista 86/93/76 (o primeiro ciclo fica abaixo porque os programas do shader são
  compilados e guardados na primeira vez); 30 trocas na pista (10 × Glock → M4A4 → AK): 67/94/58 antes, 76/95/60 depois
  da primeira volta (as malhas de massinha da Glock e da M4A4 feitas uma vez e guardadas) e 76/95/60 até a décima, com o
  heap em 77,6 MB. **O FPS e o quadro p95 ficam para a máquina do usuário** (o SwiftShader desenha na CPU e não diz nada
  sobre a RTX 2070): `map pista`, `arma ak47`, `r_preset alto`, `overlay completo`.
- **Passo 4 — o Blender e o jogo lado a lado:** a mesma pega na primeira pessoa (o `conferir ak47` com as luvas e a foto
  da pista na posição 1) e as vistas de perto da mão da frente pelos quatro lados.
- **Passo 5 — revisão crítica** (achado → correção):
  - **Os dedos da mão da frente em leque** (vistos pela direita, na inspeção e em terceira pessoa): cada dedo fechava
    sozinho na arma a partir da abertura do repouso, e a falange média de um ficava a 4,5–8,5 mm da do vizinho (as
    pontas a 12–17 mm) → `empunhadura_arma.juntar_dedos` na regra `FRENTE` (`juntar`): a partir do médio, o de fora gira
    na MCP para o vizinho e fecha de novo, até encostar sem atravessar nem entrar na arma, e sem a luva se atravessar
    mais que 0,15 mm (a membrana entre os dedos amassa). Na AK: 1,55 / 2,64 / 6,77 mm na falange média e as pontas do
    indicador ao anelar a 2,6 e 3,7 mm. Nova validação (Blender e Node): a falange média de cada dedo que abraça a arma
    a no máximo 8 mm da do vizinho (`dedosJuntosMM`), nas duas mãos; o relatório traz `juntosMM`.
  - **O sinal da abertura na mão esquerda** (achado junto): a luva esquerda é a direita espelhada, e o giro em Z que
    afastava um dedo do médio na direita juntava na esquerda — `separar_vizinhos` teria juntado em vez de separar (na
    AK ele nunca disparou na esquerda) → `empunhadura.para_fora(dedo, lado)`.
  - **Fica de fora, com o porquê:** (1) as facetas de perto no protetor dos nós e nas pontas: nas seis fotos da primeira
    pessoa não aparecem (a mão fica a um palmo da câmera e o protetor dela nem entra no quadro); aparecem nas vistas de
    perto do Blender, que a inspeção da 4.3 traz para o jogo. Cada luva está com 6 748 dos 7 000 triângulos, e alisar
    pede mais triângulos no protetor e nas pontas — ou tirar das costas e da palma, que são quase planas, ou subir o
    orçamento de 14 mil dos dois braços (decisão do usuário) —, a fazer na 4.3 com a inspeção na tela. (2) O gancho do
    polegar da mão do gatilho (a IP a 78,8° de 80°): a mão fica fora da tela nas três posições; entra na inspeção (4.3)
    e em terceira pessoa (Fase 5). (3) A ponta do mínimo da mão da frente a 15,7 mm da do anelar, por cima do
    guarda-mão: é o dedo que mais dobra (55°) e sai da ponta do vizinho; a falange média dele está a 6,8 mm.


**Código da tarefa:** nenhum arquivo (tarefa de conferência no navegador e no Blender).

### Tarefa 15: Plano executado, validação limpa, aplicação e relatório

- [ ] **Passo 1: O relatório da 4.1b** no `docs/PROGRESS.md` (no lugar da seção "Próxima: 4.1b") e o ✅ na tabela de
  `docs/phases/phase-4.md`, com os números do aceite.
- [ ] **Passo 2: O plano executado** — `docs/phases/phase-4.1b-plan.md`, gerado deste plano, da cópia de trabalho e da
  base pelas ferramentas de `prova-armas-2026-09-26/ferramentas-plano/` (o gerador e o validador da 4.1a adaptados:
  blocos inteiros para arquivos novos, pares "trocar/por" para os alterados, estados intermediários quando um arquivo
  muda em mais de uma tarefa).
- [ ] **Passo 3: Validar numa cópia limpa** de `base-4.1b` pelo validador (cada tarefa: os testes falham antes e passam
  depois; a suíte inteira passa; o `construir luvas` depois da Tarefa 6 e o `construir ak47 --forcar` depois da 7;
  comparação final sem diferença fora dos binários, conferidos pelas métricas dos relatórios).
- [ ] **Passo 4: Aplicar no `Game tiro`** pelo mesmo roteiro, com os binários da construção aceita; copiar o plano
  executado.
- [ ] **Passo 5: Conferir no navegador** pelo servidor do projeto.
- [ ] **Passo 6: Arrumar** — tirar a entrada `massacre-trabalho`; manter `base-4.1b/` e `trabalho-4.1b/` até o commit.
- [ ] **Passo 7: Memória** — `massacre-game-project.md` (a 4.1b pronta, os números, a próxima: 4.1c no mesmo chat).
- [ ] **Passo 8: A entrega ao usuário** — o que foi feito, os arquivos, como testar, o checklist do aceite, a revisão
  crítica, o que ficou de fora e a próxima subfase (4.1c: Glock-18, M4A4 e a baioneta M9), com as fontes. Commit só se
  o usuário pedir.

Execução (2026-09-27, sessão da nuvem):
- **Passo 1:** o relatório no `docs/PROGRESS.md` e o ✅ no `phase-4.md` — com o FPS e o quadro p95 a medir na máquina do
  usuário (o SwiftShader da nuvem não mede a RTX 2070).
- **Passo 2:** `prova-armas-2026-09-26/ferramentas-plano/tarefas-4.1b.mjs` (os arquivos de cada tarefa, um arquivo numa
  tarefa só) e `plano-executado-4.1b.mjs` (este plano, tarefa por tarefa, seguido do código: o arquivo inteiro para os
  novos e os pares "trocar → por" da base para os alterados, com os testes e as contagens). A ordem segue os imports: o
  `src/data/luvas.js` entra com a ficha (2); o solver inteiro e a saída da pega entram com as luvas (6), porque o
  `principal.py` chama o solver no `construir` de cada arma e o `luvas.py` fecha as poses de teste até o contato — a 7
  fica sem arquivo e a AK é construída logo depois da 6; os documentos que mudaram em várias tarefas entram na 13 e na
  15. Saída: `docs/phases/phase-4.1b-plan.md`.
- **Passo 3:** `valida-4.1b.sh` numa cópia limpa de `base-4.1b` (com o `node_modules` completo e o lançador do
  Blender): em cada tarefa com testes, eles falham antes e passam depois; a suíte passa no fim de cada uma (370 → 381 →
  405 → 410 → 435 → 443 → 449 → 454); depois da 6, `construir luvas` (6 748 triângulos por luva, as mesmas medidas) e
  `construir ak47 --forcar` (aprovada, a pega com a mão do gatilho entrando 0,044 mm); no fim, a cópia igual à de
  trabalho fora os binários — 0 erros.
- **Passo 4:** aplicado no `Game tiro` pelo mesmo roteiro, com os binários da construção aceita (`--sem-blender`), e o
  plano executado copiado.
- **Passo 6:** fica para o Windows a entrada `massacre-trabalho` do `.claude/launch.json` (a pasta-mãe não está nesta
  sessão); `base-4.1b/` e `trabalho-4.1b/` ficam até o usuário decidir.
- **Passo 7:** a memória é a do Windows (ver a Tarefa 13).


**Código da tarefa** (a versão verificada no navegador e no Blender; os blocos `file=` são o arquivo inteiro, os pares são aplicados na ordem).

- [ ] **A implementação** — `docs/PROGRESS.md`, `docs/superpowers/plans/2026-09-26-4.1b-luvas-e-empunhadura.md`:

Em `docs/PROGRESS.md`, trocar:

```
  dados. Caminho em `tools/blender/` (`npm run blender`); o executável vem de `BLENDER_PATH` ou de
  `tools/blender/local.json` (fora do git).
- **Massinha saindo ao levar tiro:** já está na spec (respingos e amassados na Fase 4; dano e morte em pedaços que
```

por:

```
  dados. Caminho em `tools/blender/` (`npm run blender`); o executável vem de `BLENDER_PATH` ou de
  `tools/blender/local.json` (fora do git). **Mudado em 2026-09-26 (redesenho das armas realistas):** o Blender
  constrói por script os modelos realistas das armas e das luvas, que entram no jogo como `.glb` + `.webp` assados
  (`tools/blender/armas/`, `assets/`); a receita de massinha fica só para as armas ainda não refeitas.
- **Texturas CC0 para o Blender (decisão do Cesar, 2026-09-27):** os scripts do Blender podem pegar texturas de domínio
  público como base dos materiais das armas e das luvas, nestas bibliotecas: cgbookcase
  (https://www.cgbookcase.com/textures), Poly Haven (https://polyhaven.com/textures — por exemplo, plástico e borracha:
  https://polyhaven.com/textures/plastic-rubber), ambientCG (https://ambientcg.com/list?type=substance&sort=popular) e
  o CC0 Asset Index (https://github.com/xiaoqianran/Blender-cc0-asset-index, com a ferramenta `cc0a` que baixa cada
  recurso com o `LICENSE.json`). Só CC0; cada textura usada registrada em `tools/blender/texturas/fontes.json`; o jogo
  recebe só o `.webp` assado; modelos desses sites continuam fora. Regras completas no `CLAUDE.md`, seção 0.7
  ("Texturas CC0 no Blender"). Na sessão da nuvem de 2026-09-27, a rede bloqueava cgbookcase, Poly Haven e ambientCG
  (só o índice no GitHub respondia): é preciso liberar esses domínios no ambiente antes de baixar.
- **Massinha saindo ao levar tiro:** já está na spec (respingos e amassados na Fase 4; dano e morte em pedaços que
```

Em `docs/PROGRESS.md`, trocar:

```

### Próxima: subfase 4.1b — Luvas, mangas e empunhadura

Luvas táticas de 5 dedos e a manga de tecido na cor do time, com a braçadeira, feitas no Blender como as armas; o rig
das mãos e o solver de empunhadura (nenhum dedo atravessando a arma nem flutuando); a AK segurada em primeira pessoa
(`docs/phases/phase-4.md`, tabela de subfases; o desenho detalhado é feito no começo do chat dela).

```

por:

```

### Subfase 4.1b — Luvas, braço de massinha e empunhadura ✅ (2026-09-27; o FPS na máquina do usuário a medir)

Desenho em `docs/superpowers/specs/2026-09-26-4.1b-luvas-e-empunhadura-design.md`; plano de desenho em
`docs/superpowers/plans/2026-09-26-4.1b-luvas-e-empunhadura.md`; plano executado (gerado do diff da cópia de trabalho,
validado numa cópia limpa e aplicado aqui pelo mesmo roteiro): `docs/phases/phase-4.1b-plan.md`. Referências na seção 15
do moodboard: as fontes da ficha das luvas (ANSUR II, Buryanov e Kotiuk, Greiner, AAOS, Cooney), os boards QTG, QGL e
QFH, as buscas das luvas táticas e do TPR moldado, e a imagem da AK no CS:GO que o usuário mandou na parada P2.

Decisões do usuário: sem manga e sem roupa por enquanto (as próximas fases furam o boneco de massinha); a luva tática
realista no braço de massinha do boneco, com a braçadeira de massa em modo de time; o protetor de borracha moldada nos
nós; na mão da frente de toda arma, só o polegar de um lado — reto, deitado e encostado, sem curva — e os quatro dedos
do outro, como a AK no CS:GO; uma mão só na tela; o rebatedor branco na bancada; texturas CC0 de bibliotecas abertas
liberadas para o Blender (cgbookcase, Poly Haven, ambientCG e o CC0 Asset Index; seção 0.7 do `CLAUDE.md`).

O que entrou:
- **Ficha das luvas** (`tools/blender/refs/luvas.json`, validada por `src/characters/hands/fichaLuvas.js`): cada número
  com a fonte — a mão média, os ossos entre as juntas, a largura e a volta nas juntas, os limites das juntas e a rotação
  do metacarpo do polegar.
- **Luvas no Blender** (`tools/blender/armas/`): o gerador de quadriláteros (`maos.py`, com medidas, limites, gaiola e
  cápsulas), os detalhes que fazem silhueta e o modelo alto assado no relevo (`maos_detalhes.py`, `maos_alto.py`),
  couro, tecido e borracha em `materiais.py`, o rig de 20 ossos por braço com os pesos do gerador e as correções das
  dobras (`maos_rig.py`, `maos_correcoes.py`), a validação das poses (`validar_maos.py`), a UV por costuras, o assar e a
  exportação (`luvas.py`); `npm run blender -- construir|validar|conferir|abrir luvas`.
- **Solver de empunhadura** dentro do `construir` de cada arma (`empunhadura*.py`): a palma no soquete, os dedos
  fechando juntos até encostar, os vizinhos sem se atravessar (e, na mão da frente, lado a lado), o indicador no
  gatilho pela IK, o polegar deitado na face esquerda na mão da frente; a pega vai no `.glb` da arma (nós `pega_mao_*`,
  o clipe `empunhadura`, a marca do rig, as sondas). A validação bloqueia a exportação: penetração, contatos, os lados
  (o polegar de um, os dedos do outro), o polegar reto e deitado, os dedos lado a lado, a luva sem se atravessar e os
  ângulos no limite da ficha; a saída do Node (`tools/blender/saidaLuvas.mjs`, `saidaPega.mjs`) repete as contas.
- **Jogo**: `src/data/luvas.js` (zonas, pinturas por facção, limites da pega), os acabamentos de couro e tecido e a
  borracha moldada, a carga das luvas (`luvasSource.js`), o braço de luva com o modelo das dobras igual ao do Blender
  (`bracoLuva.js`, `modeloDobras.js`, `moldeLuva.js`), o antebraço de massinha em SDF (`antebracoMassa.js`, a forma
  `tronco`), o viewmodel com as luvas na arma com pega e a massinha nas outras (`bracosLuva.js`), os cotovelos do
  `rifle` com o pulso dentro dos limites nas três posições do CS, a bancada com "Segurar" e o seletor de facção, os
  comandos `luvas` e `luvas_contato` (a luva deformada de verdade contra a arma, comparada com o Blender) e o rebatedor
  de isopor (`src/maps/arsenal/rebatedor.js`, `set.foam`).
- **Documentos**: regras 3 e 4 e a tabela de paridade em "as armas e as luvas"; a seção 0.7 "Mãos" e a nova "Texturas
  CC0 no Blender"; a 0.12 com o "sem roupa por enquanto"; o desenho geral com cada mudança e o que era; a seção 15 do
  moodboard.

Números medidos:
- `construir luvas`: 6 748 triângulos por luva (base 5 568, detalhes 1 180; orçamento 7 000); medidas 0,00 % no
  comprimento e na largura, −0,35 % no pulso; poses de teste com penetração de 0,049 mm e a pior junta a 0,90 da
  espessura; 3,66 MB (`luvas.glb` 0,34, `_n` 1,69, `_m` 1,61; orçamento 6 MB).
- `construir ak47` com a pega: aprovada, silhueta 99,9 %, 5,10 MB; mão do gatilho entrando 0,044 mm; mão da frente com o
  polegar a 0° de curva e +20,1 mm do meio da arma, os dedos de −16,2 a −25,3 mm do outro lado e a falange média de
  cada dedo a 1,55 / 2,64 / 6,77 mm da do vizinho.
- No jogo (Chromium com SwiftShader na nuvem, preset Leve): `luvas_contato` nas duas facções e nas três posições do CS
  com a pior diferença para o Blender de 0,02 mm (limite 0,05), a luva entrando no máximo 0,06 mm e cada contato a até
  0,03 mm; memória igual do segundo ciclo em diante (menu 32/26/49, bancada 109/35/66, pista 86/93/76) e nas 30 trocas
  de arma (76/95/60, heap 77,6 MB); o rebatedor clareia o receptor de 0,0024 para 0,0390 e de 0,0004 para 0,0269 de
  luminância; nenhum erro do jogo no console. **FPS e quadro p95 na pista com a AK: a medir na máquina do usuário** (o
  SwiftShader desenha na CPU): `map pista`, `arma ak47`, `r_preset alto`, `overlay completo`.

Revisão crítica (achado → correção; o detalhe de cada uma no plano de desenho, paradas P1 e P2 e Tarefas 12 a 14):
- O polegar da mão da frente subia na vertical, depois dobrava em arco com só a ponta encostada → o polegar reto e
  deitado na face esquerda (a IK pelo comprimento, com a face e o eixo), e a validação da curva e da folga.
- Os dedos da mão da frente do lado do polegar → a regra dos lados (a polpa de cada um a pelo menos 5 mm do meio).
- Os dedos da mão da frente em leque pelo lado direito → `juntar_dedos` e a validação dos dedos lado a lado.
- O sinal da abertura na mão esquerda (espelhada) invertido → `para_fora(dedo, lado)`.
- A penetração passava despercebida além de 6 mm → a validação mede sem o limite das buscas.
- O coiote saía no mesmo laranja da madeira da AK → mais escuro e puxado para o oliva, com o teste do contraste.
- O grão do couro parecia craquelado → seixinhos arredondados com o vale largo e raso.
- O pulso da mão da frente perto do limite → os cotovelos por minimax, cada ângulo a no máximo 91 % do limite.
- O receptor quase preto na bancada → o rebatedor de isopor aceso pelo rim, sem sombra no tapete.

Ficou de fora (com o porquê, no plano): as facetas de perto no protetor dos nós e nas pontas (não aparecem na primeira
pessoa; entram com a inspeção da 4.3 — pedem triângulos das costas e da palma ou mais orçamento); o gancho do polegar da
mão do gatilho (a IP a 78,8° de 80°; a mão fica fora da tela até a inspeção e a terceira pessoa); a memória
(`massacre-workflow-rules`, `massacre-game-project`) fica para a próxima sessão no Windows, com o que acrescentar
anotado no plano.

Como testar: `npm test` (454 testes, 84 novos); `npm run blender -- construir luvas` e `construir ak47 --forcar`;
`npm run blender -- conferir ak47` (as vistas de perto das mãos); no jogo, `map pista`, `arma ak47`, `luvas`,
`luvas_contato`, `cl_bracadeira tr|ct`, `viewmodel_presetpos 1|2|3`; `arsenal` com "Segurar (primeira pessoa)" e o
seletor de facção no painel (Tab).

### Próxima: subfase 4.1c — Glock-18, M4A4 e a baioneta M9

As três armas no caminho provado, cada uma com a ficha, a régua e a pega (a regra da mão da frente vale na M4A4; as
regras da pistola e da faca entram com elas), no desenho geral (`docs/superpowers/specs/2026-09-26-armas-realistas-
design.md`, seção 8.1).

```

Em `docs/superpowers/plans/2026-09-26-4.1b-luvas-e-empunhadura.md`, trocar:

```
  (`lerPega`), e a escolha fica registrada aqui ao fim da Tarefa 1.
- **D2 — Nomes dos ossos:** `antebraco`, `torcao`, `mao`, `polegar_1..3`, `indicador_1..3`, `medio_1..3`, `anelar_0..3`,
```

por:

```
  (`lerPega`), e a escolha fica registrada aqui ao fim da Tarefa 1.
  **Resultado da prova (2026-09-26): vale a animação.** O exportador do Blender 5.2.2 grava a armadura sem malha como
  nós (com um `skin` sem malha, só com as juntas) e a ação de 1 quadro como a animação `empunhadura`, com os canais
  `translation`/`rotation`/`scale` de cada osso; o `GLTFLoader` do three r186 dá as trilhas `<osso>.quaternion`, e
  aplicadas por nome no esqueleto de um `.glb` com skin comprimido no Draco (juntas e pesos dentro do Draco) a pose bate
  com a do Blender a 0,003–0,005 mm num objeto de 15 cm. O jogo usa só as trilhas `quaternion` dos ossos de dedo; a
  forma de reserva (`extras`) não é implementada.
- **D2 — Nomes dos ossos:** `antebraco`, `torcao`, `mao`, `polegar_1..3`, `indicador_1..3`, `medio_1..3`, `anelar_0..3`,
```

Em `docs/superpowers/plans/2026-09-26-4.1b-luvas-e-empunhadura.md`, trocar:

```
  saída da pega.
- `src/data/luvas.js` — registro das luvas (pasta, zonas, ossos, orçamento, pinturas por facção, braço de massinha).
```

por:

```
  saída da pega.
- `src/characters/hands/fichaLuvas.js` — a validação da ficha e as escalas (como a `ficha.js` das armas).
- `src/data/luvas.js` — registro das luvas (pasta, zonas, ossos, orçamento, pinturas por facção, braço de massinha).
```

Em `docs/superpowers/plans/2026-09-26-4.1b-luvas-e-empunhadura.md`, trocar:

```

**Files:** Create `tools/blender/refs/luvas.json`, `tests/fichaLuvas.test.js`, `src/data/luvas.js` (só o registro e a
validação da ficha nesta tarefa).

- [ ] **Passo 1: Testes** — `tests/fichaLuvas.test.js`:
  - `validarFichaLuvas(json)` (em `src/data/luvas.js`) aceita a ficha real e devolve a mesma estrutura congelada;
  - recusa ficha sem `fontes`, sem algum dos cinco dedos, com comprimento de osso ≤ 0 ou sem a fonte de um grupo de
```

por:

```

**Files:** Create `tools/blender/refs/luvas.json`, `src/characters/hands/fichaLuvas.js` (a validação, como a
`ficha.js` das armas), `tests/fichaLuvas.test.js`.

- [ ] **Passo 1: Testes** — `tests/fichaLuvas.test.js`:
  - `validarFichaLuvas(json)` (em `src/characters/hands/fichaLuvas.js`) aceita a ficha real e devolve a mesma
    estrutura congelada; `escalasDaFicha` dá as escalas de Greiner para a mão da ficha;
  - recusa ficha sem `fontes`, sem algum dos cinco dedos, com comprimento de osso ≤ 0 ou sem a fonte de um grupo de
```

Em `docs/superpowers/plans/2026-09-26-4.1b-luvas-e-empunhadura.md`, trocar:

```
  espessura no pulso da ficha).
- [ ] **Passo 4: O validador** — `validarFichaLuvas` em `src/data/luvas.js` (funções puras).
- [ ] **Passo 5: Rodar e ver passar**; **Passo 6: suíte inteira** (371+).
```

por:

```
  espessura no pulso da ficha).
- [ ] **Passo 4: O validador** — `problemasDaFichaLuvas`, `validarFichaLuvas` e `escalasDaFicha` em
  `src/characters/hands/fichaLuvas.js` (funções puras).
- [ ] **Passo 5: Rodar e ver passar**; **Passo 6: suíte inteira** (371+).
```

Em `docs/superpowers/plans/2026-09-26-4.1b-luvas-e-empunhadura.md`, trocar:

```

## Tarefa 12: O rebatedor
```

por:

```

**Resposta do usuário (2026-09-27):** corrigir os erros críticos e, **sempre**, a mão da frente com só o polegar de um
lado e os outros quatro dedos do outro, como a pega da AK no CS:GO (a imagem de referência que ele mandou). O que mudou:

- **A mão da frente** (achado → correção, em duas rodadas): (1) o polegar esquerdo subia na vertical ao lado do
  guarda-mão e passava por cima do topo (a regra só pedia "o mais à esquerda possível", e na face lateral todo ponto é
  igualmente à esquerda) → a polpa num ponto da face e um eixo; (2) o usuário recusou o resultado — o polegar dobrava em
  arco (MCP 35°, IP 17°, a CMC no limite da extensão) com só a ponta encostada: "o dedo tem que estar colado com a arma"
  → o polegar **reto e deitado** (`empunhadura_polegar.deitar_na_arma`): a IK zera a folga da falange proximal e da
  distal para a face esquerda ao longo do comprimento (pela cápsula de seção medida, com a normal da superfície mais
  perto tendo de ser a da face — sem isso ele deitava na face de baixo, ao lado do indicador), aponta as duas para o
  eixo e cobra a curva além de 12°; a referência é a pega "thumb break" (os quatro dedos por baixo do guarda-mão e o
  polegar esticado ao longo do lado, apontando para o alvo). O Pinterest e os sites de tiro estão bloqueados pela rede
  desta sessão; só a busca respondeu. A regra `FRENTE` em `empunhadura_regras.py`, base de toda categoria, com a mão
  girada 35° na vertical, −10° no cano e 20° de diagonal (varreduras de giro, diagonal e altura da palma; a âncora não
  recua — o calcanhar da mão bate na curva do carregador). Na AK: o polegar com 0° de curva, a distal encostada (0 a
  0,2 mm) e a proximal em cunha de 4 a 6,5 mm (a base sai da quina de baixo). As validações novas (bloqueiam o
  `construir` e se repetem na saída do Node, `saidaPega.mjs`): os `lados` — a polpa do polegar e a de cada um dos quatro
  dedos a pelo menos 5 mm do plano do meio da arma, cada uma do seu lado (`LIMITES_DA_PEGA.ladoMM`; na AK, polegar
  +20,1 mm, indicador −16,5, médio −24,6, anelar −25,5, mínimo −25,6 mm) — e o polegar deitado: a curva até 20°, a
  distal encostando (até 1 mm) e nenhum trecho a mais de 8 mm (`polegarCurvaGraus`, `polegarFolgaMM`).
- **A penetração passava despercebida além de 6 mm** (achado na segunda rodada): a medida da validação usava o limite
  das buscas do solver, e um vértice mais fundo que isso dentro da arma não contava — numa das posições varridas o
  indicador entrava 7,35 mm e a validação dizia 0,047 mm → a validação mede sem limite (`NaArma.penetracao(...,
  limite=None)`). As pegas exportadas antes não tinham isso (os contatos, medidos sem limite, estavam em ±0,05 mm).
- **O cotovelo da mão da frente**: com a pega nova e o cotovelo antigo, o desvio radial passava do limite na posição 3 →
  varredura com o menor pior ângulo em relação ao limite (minimax; a soma dos quadrados deixava a supinação em 79,9° de
  80°): `gloveElbows.esquerda` = [−9,9, −52,4, −9,7], todos os ângulos a no máximo 91 % do limite (a supinação, que a
  P2 viu a 97 %, fica em 68–72°) e o antebraço a 6,6 mm da arma. O teste do viewmodel passou a exigir no máximo 93 %.
- **O polegar da mão do gatilho** (fica para depois): ele cruza o punho com a IP a 78,8° de 80°, em gancho. O mesmo
  polegar deitado não serve ali (reto, ele não contorna a traseira do punho: a base entra 0,1 mm), e o peso do lado não
  muda nada (a CMC já está no limite da ficha); o conserto é reposicionar a mão no punho. Essa mão fica fora da tela em
  primeira pessoa (o usuário não quer as duas mãos no quadro); aparece na inspeção (4.3) e em terceira pessoa (Fase 5).
- **O coiote pálido**: medido na pista, o coiote de partida saía rgb(180, 117, 75), o mesmo laranja da madeira da AK
  (1,20× de luminância) → `#5C5139` / `#4D4432` / `#342E24`, mais escuro e puxado para o oliva, e o couro gastando
  menos: madeira/luva 1,68× e mesa/luva 3,02× (antes 1,98×). O teste dos dados exige o coiote a no máximo 60 % da
  luminância da madeira de fábrica da AK e a 12° de matiz dela.
- **O grão do couro craquelado**: o padrão do shader era uma rede de linhas finas e escuras entre células de Voronoi →
  seixinhos arredondados com o vale largo e raso, no domínio torcido por ruído (`armaGrao`), e menos mistura de cor.
- **Ficam para a Tarefa 14** (não críticos): as facetas de perto nos protetores dos nós e nas pontas (só na inspeção,
  que chega na 4.3; o orçamento de 7 mil triângulos por luva está quase cheio) e o gancho do polegar da mão do gatilho
  (acima). A mão direita continua fora da tela nas três posições prontas (o topo dela fica 0,24 da meia-altura abaixo da borda), como na referência do
  CS:GO que ele mandou; o enquadramento com as duas mãos do CS2 muda a posição do `rifle` e os cotovelos. **Decidido
  pelo usuário (2026-09-27): uma mão só na tela** — o enquadramento fica.
- **Ambiente**: nesta sessão (nuvem, Linux) o Blender é o módulo `bpy` 5.2.2 do PyPI atrás de um lançador que imita a
  linha de comando (`tools/blender/local.json`, fora do git), com a ponte do Draco compilada da fonte do Blender 5.1 e o
  Mesa para o Workbench; as luvas reconstruídas por ele saem com as mesmas medidas, triângulos e marca do rig do
  Windows.

## Tarefa 12: O rebatedor
```

Em `docs/superpowers/plans/2026-09-26-4.1b-luvas-e-empunhadura.md`, trocar:

```

## Tarefa 13: Documentos e memória
```

por:

```

Execução (2026-09-27; desenho, seção 7.6):
- **Arquivos a mais:** `src/clay/set/surfaceMaterials.js` (`foamMaterial`, o isopor: Voronoi 3D das contas fundidas com
  o sulco entre elas e o tom de cada conta), `src/clay/set/index.js` (`set.foam`), `src/render/studio/fixtures.js` (o
  `buildCStand` com o `reach` do braço, para a coluna descer fora da mesa).
- **A luz:** a key e o fill ficam atrás do lugar da placa; quem a acende é o rim (os dados, `rebatedor.luz`).
- **A posição:** três medidas até a final (a tabela da seção 7.6): alta e girada; em pé na beira da mesa; deitada 25°
  para trás, 700 × 220 × 20 mm, assentada no tampo atrás do tapete. O rebatedor só pode ficar abaixo dos raios da key
  que vão ao tapete: as posições que clareavam mais o aço faziam sombra nele (o teste confere a grade inteira).
- **Números:** o lado do receptor na roda, de 0,0024 para 0,0390 (16×, roda a 0) e de 0,0004 para 0,0269 (60×, roda a π); o
  "Segurar" (que já não saía preto), de 0,0347 para 0,0354; nenhuma sombra na bancada.
- **Testes:** `tests/rebatedor.test.js` (5): atrás do olho e virado para ele, o primeiro objeto naquela direção e ≥ 60 %
  do cone do reflexo do receptor; no cone do rim e sem sombra da key no tapete nem na roda; assentado no tampo atrás do
  tapete; o C-stand no chão, fora da mesa; o isopor fosco e sem boil, e o descarte das geometrias sem os materiais do set.

## Tarefa 13: Documentos e memória
```

Em `docs/superpowers/plans/2026-09-26-4.1b-luvas-e-empunhadura.md`, trocar:

```

## Tarefa 14: Aceite no navegador e revisão crítica
```

por:

```

Execução (2026-09-27):
- **Pedido novo do usuário na mesma rodada:** registrar no `.md` do projeto que o Blender pode pegar texturas de
  cgbookcase, Poly Haven, ambientCG e do CC0 Asset Index. Entrou como decisão de 2026-09-27: a regra 4 e a tabela de
  paridade (nenhum modelo de terceiros; texturas CC0 como base dos materiais, que chegam ao jogo só assadas) e a seção
  0.7 nova, "Texturas CC0 no Blender" (a lista, só CC0, a proveniência em `tools/blender/texturas/fontes.json`, a ficha
  do material dizendo qual usou); o mesmo no desenho geral (decisão 3 e seção 4.4), no `phase-4.md`, no `PROGRESS.md`
  e na seção 15 do moodboard. As quatro bibliotecas são CC0 (o índice valida a licença de cada registro). Nesta sessão
  da nuvem, a rede bloqueia cgbookcase, Poly Haven e ambientCG; só o índice no GitHub responde.
- **Passo 1:** `CLAUDE.md` e `CLAUDE.md.md` com o Mestre igual nos dois (conferido por `diff`): a tabela de paridade e
  as regras 3 e 4 em "as armas e as luvas", com o braço de massinha do punho para trás; a seção 0.7 "Mãos" (sem manga e
  sem roupa, o protetor de borracha, as cores por facção, a braçadeira de massa); a 0.12 com o "sem roupa por enquanto"
  e o motivo, e o viewmodel sem boil incluindo o antebraço de massinha.
- **Passo 2:** o desenho geral com cada mudança no lugar e o que era (seções 1, 2, 4.1, 4.4, 5.1 com as luvas medidas —
  6 748 triângulos por luva e 3,6 MB —, 5.3, 6.5, 7, 7.3 com a regra da mão da frente, 7.5, 8.1, 8.2 e 8.3). Na 8.2, o
  que sai no fim da 4.1d são só os arquivos da mão de 4 dedos (`handShape`, `handRig`, `handSkin`, `handLibrary`,
  `src/data/hands.js`): a pasta `src/characters/hands/` tem as luvas, o antebraço e a braçadeira, que ficam.
- **Passo 3:** `docs/phases/phase-4.md` (a linha da 4.1b, as decisões da 4.1b e as notas nas decisões 2 e 3 de
  2026-09-26) e a seção 15 do moodboard, que as fichas e o código já citavam e não existia (as fontes da ficha, os
  boards QTG, as buscas, a imagem do CS:GO, a medida do coiote, o rebatedor e as bibliotecas CC0). O `PROGRESS.md`
  ganhou a decisão das texturas e o resumo da 4.1b em andamento (o relatório entra na Tarefa 15).
- **Passo 4:** a memória (`massacre-workflow-rules.md`, `massacre-game-project.md`) é a do Windows e não existe nesta
  sessão da nuvem; fica para a próxima sessão no Windows, com o que acrescentar: "sem roupa por enquanto" (e o motivo),
  a regra da mão da frente, "uma mão só na tela" e as bibliotecas CC0 de texturas liberadas para o Blender.

## Tarefa 14: Aceite no navegador e revisão crítica
```

Em `docs/superpowers/plans/2026-09-26-4.1b-luvas-e-empunhadura.md`, trocar:

```

## Tarefa 15: Plano executado, validação limpa, aplicação e relatório
```

por:

```

Execução (2026-09-27, sessão da nuvem: Chromium com SwiftShader no preset Leve a 0,75 da resolução — no Médio a página
caía ao carregar as luvas —, o Blender 5.2.2 do PyPI):
- **Passo 1 — console:** na pista, na bancada e nos ciclos, nenhum erro do jogo. Só o certificado das fontes do Google
  (o proxy da nuvem corta: `ERR_CERT_AUTHORITY_INVALID`) e o aviso do three de que o SwiftShader não tem a extensão
  `KHR_parallel_shader_compile`.
- **Passo 2 — a AK nas duas facções e nas três posições prontas:** `luvas_contato` igual nas seis — direita entra 0,05
  mm (Blender 0,04), esquerda 0,06 mm (Blender 0,05), cada contato a no máximo 0,03 mm da arma e a pior diferença para
  o Blender 0,02 mm (limites: 0,3 mm, 1 mm e 0,05 mm); a marca da arma bate com a das luvas; uma mão só na tela, o
  polegar deitado no lado esquerdo do guarda-mão e os dedos do outro lado, como na referência.
- **Passo 3 — memória:** do segundo ciclo em diante, os mesmos números em cada parada (geometrias/texturas/programas):
  menu 32/26/49, bancada 109/35/66, pista 86/93/76 (o primeiro ciclo fica abaixo porque os programas do shader são
  compilados e guardados na primeira vez); 30 trocas na pista (10 × Glock → M4A4 → AK): 67/94/58 antes, 76/95/60 depois
  da primeira volta (as malhas de massinha da Glock e da M4A4 feitas uma vez e guardadas) e 76/95/60 até a décima, com o
  heap em 77,6 MB. **O FPS e o quadro p95 ficam para a máquina do usuário** (o SwiftShader desenha na CPU e não diz nada
  sobre a RTX 2070): `map pista`, `arma ak47`, `r_preset alto`, `overlay completo`.
- **Passo 4 — o Blender e o jogo lado a lado:** a mesma pega na primeira pessoa (o `conferir ak47` com as luvas e a foto
  da pista na posição 1) e as vistas de perto da mão da frente pelos quatro lados.
- **Passo 5 — revisão crítica** (achado → correção):
  - **Os dedos da mão da frente em leque** (vistos pela direita, na inspeção e em terceira pessoa): cada dedo fechava
    sozinho na arma a partir da abertura do repouso, e a falange média de um ficava a 4,5–8,5 mm da do vizinho (as
    pontas a 12–17 mm) → `empunhadura_arma.juntar_dedos` na regra `FRENTE` (`juntar`): a partir do médio, o de fora gira
    na MCP para o vizinho e fecha de novo, até encostar sem atravessar nem entrar na arma, e sem a luva se atravessar
    mais que 0,15 mm (a membrana entre os dedos amassa). Na AK: 1,55 / 2,64 / 6,77 mm na falange média e as pontas do
    indicador ao anelar a 2,6 e 3,7 mm. Nova validação (Blender e Node): a falange média de cada dedo que abraça a arma
    a no máximo 8 mm da do vizinho (`dedosJuntosMM`), nas duas mãos; o relatório traz `juntosMM`.
  - **O sinal da abertura na mão esquerda** (achado junto): a luva esquerda é a direita espelhada, e o giro em Z que
    afastava um dedo do médio na direita juntava na esquerda — `separar_vizinhos` teria juntado em vez de separar (na
    AK ele nunca disparou na esquerda) → `empunhadura.para_fora(dedo, lado)`.
  - **Fica de fora, com o porquê:** (1) as facetas de perto no protetor dos nós e nas pontas: nas seis fotos da primeira
    pessoa não aparecem (a mão fica a um palmo da câmera e o protetor dela nem entra no quadro); aparecem nas vistas de
    perto do Blender, que a inspeção da 4.3 traz para o jogo. Cada luva está com 6 748 dos 7 000 triângulos, e alisar
    pede mais triângulos no protetor e nas pontas — ou tirar das costas e da palma, que são quase planas, ou subir o
    orçamento de 14 mil dos dois braços (decisão do usuário) —, a fazer na 4.3 com a inspeção na tela. (2) O gancho do
    polegar da mão do gatilho (a IP a 78,8° de 80°): a mão fica fora da tela nas três posições; entra na inspeção (4.3)
    e em terceira pessoa (Fase 5). (3) A ponta do mínimo da mão da frente a 15,7 mm da do anelar, por cima do
    guarda-mão: é o dedo que mais dobra (55°) e sai da ponta do vizinho; a falange média dele está a 6,8 mm.

## Tarefa 15: Plano executado, validação limpa, aplicação e relatório
```

Em `docs/superpowers/plans/2026-09-26-4.1b-luvas-e-empunhadura.md`, trocar:

```
  o usuário pedir.

```

por:

```
  o usuário pedir.

Execução (2026-09-27, sessão da nuvem):
- **Passo 1:** o relatório no `docs/PROGRESS.md` e o ✅ no `phase-4.md` — com o FPS e o quadro p95 a medir na máquina do
  usuário (o SwiftShader da nuvem não mede a RTX 2070).
- **Passo 2:** `prova-armas-2026-09-26/ferramentas-plano/tarefas-4.1b.mjs` (os arquivos de cada tarefa, um arquivo numa
  tarefa só) e `plano-executado-4.1b.mjs` (este plano, tarefa por tarefa, seguido do código: o arquivo inteiro para os
  novos e os pares "trocar → por" da base para os alterados, com os testes e as contagens). A ordem segue os imports: o
  `src/data/luvas.js` entra com a ficha (2); o solver inteiro e a saída da pega entram com as luvas (6), porque o
  `principal.py` chama o solver no `construir` de cada arma e o `luvas.py` fecha as poses de teste até o contato — a 7
  fica sem arquivo e a AK é construída logo depois da 6; os documentos que mudaram em várias tarefas entram na 13 e na
  15. Saída: `docs/phases/phase-4.1b-plan.md`.
- **Passo 3:** `valida-4.1b.sh` numa cópia limpa de `base-4.1b` (com o `node_modules` completo e o lançador do
  Blender): em cada tarefa com testes, eles falham antes e passam depois; a suíte passa no fim de cada uma (370 → 381 →
  405 → 410 → 435 → 443 → 449 → 454); depois da 6, `construir luvas` (6 748 triângulos por luva, as mesmas medidas) e
  `construir ak47 --forcar` (aprovada, a pega com a mão do gatilho entrando 0,044 mm); no fim, a cópia igual à de
  trabalho fora os binários — 0 erros.
- **Passo 4:** aplicado no `Game tiro` pelo mesmo roteiro, com os binários da construção aceita (`--sem-blender`), e o
  plano executado copiado.
- **Passo 6:** fica para o Windows a entrada `massacre-trabalho` do `.claude/launch.json` (a pasta-mãe não está nesta
  sessão); `base-4.1b/` e `trabalho-4.1b/` ficam até o usuário decidir.
- **Passo 7:** a memória é a do Windows (ver a Tarefa 13).

```

Run: `node --test "tests/**/*.test.js"`
Expected: PASS — # tests 454 # pass 454 # fail 0 .
