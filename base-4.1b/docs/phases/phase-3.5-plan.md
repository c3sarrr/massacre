# Subfase 3.5 — Sensação e aceite da Fase 3: plano de implementação

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** a sensação da câmera em primeira pessoa (balanço preso ao relógio dos passos, inclinação ao andar de lado, no slide e no wall-jump, mergulho com mola no pouso — só visual, com os três controles da seção "Conforto" e o "Reduzir movimento" zerando tudo), o corpo do jogador (o boneco de referência com botas de cravos e o squash & stretch "em dois", com a sombra de contato), as pegadas na massinha (um mapa por placa, desenhado na GPU na troca de pose e esmaecendo em ~21 s) e o aceite da Fase 3 (o monitor do movimento, o robô de 10 min no navegador, a varredura de 5 seeds × 10 min no Node, a memória em 3 ciclos e o usuário jogando 10 min).

**Architecture:** tudo o que é conta fica puro e por tick (64 Hz), com as molas pela solução exata: a sensação da câmera (`src/player/cameraFeel.js`) sai do estado de movimento, dos eventos do tick e do relógio dos passos (o `stepSpan` novo) e o `PlayerPawn` só a soma à câmera no render; a mola do corpo (`src/characters/squashStretch.js`) anda por tick e o corpo (`src/characters/playerBody.js`) mostra o valor da pose (`EV.POSE`, 12/s); as marcas das pegadas (`src/clay/prints/marks.js`) e a fila na ordem do jogo (`printQueue.js`) são JS puro, e a GPU faz a mesma conta num shader gerado dos mesmos números (`stampPass.js`), uma chamada de render por placa e pose (`printSystem.js`); o `ClayMaterial` ganha a camada `CLAY_PRINTS` (`src/clay/clayImprint.js`, tirado dele). O monitor (`src/debug/moveMonitor.js`) tem um registro puro que a varredura do Node também usa. Números em `src/data/cameraFeel.js`, `referenceDoll.js`, `footprints.js` e `sandbox.js`.

**Tech Stack:** JavaScript ES Modules, three 0.186.1 (alvos de render RGBA8 com mipmaps, `RawShaderMaterial` GLSL 3, `InstancedBufferGeometry`, mistura MAX e subtração reversa), three-mesh-bvh 0.9.15, `node --test`.

**Especificação:** `docs/phases/phase-3.md` (seção 3.5, com os ajustes feitos na implementação); números de origem no `player.js` do Doodle District e no `CheckFalling` do CS:GO, citados na seção; referências visuais no item 12 do moodboard. Regras: `CLAUDE.md` (sem placeholder, < 600 linhas por arquivo, números em `src/data/`).

**Como executar os blocos de código:** cada bloco ` ```js file=<caminho> ` (ou ` ```css file=<caminho> `) é o conteúdo completo do arquivo e é gravado com o extrator da Tarefa 0, sem redigitar — num arquivo que já existe, substitui o arquivo inteiro. Alterações em arquivos existentes vêm como pares "Em `arquivo`, trocar: … por: …", aplicados na ordem em que aparecem com a ferramenta de edição (cada trecho "trocar" é único no arquivo no momento em que é aplicado). Quatro arquivos passam por estados intermediários: `src/modes/matchState.js` (a sensação na Tarefa 2, o corpo na 3, as pegadas na 5 e o monitor na 6), `src/data/configSchema.js` (o Conforto na Tarefa 2 e a chave do monitor na 6), `tests/footprints.test.js` (a parte pura na Tarefa 4; a Tarefa 5 completa) e `src/maps/pista/index.js` (as superfícies na Tarefa 5 e os lotes na 6).

**Estado de partida:** a árvore da 3.4 (sem commit, sobre o commit `953425b` da branch `fase-3.1`) com o desenho da 3.5 já registrado na seção 3.5 de `docs/phases/phase-3.md`; `npm test` com 255 testes passando. A 3.5 entra na mesma árvore.

**Commits:** os passos "Commit" só rodam quando o usuário pedir (decisão da 3.3: nada de commit até o pedido). Toda mensagem termina com a linha `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.

**Números conferidos pelos testes** (64 tick; faca quando não dito): balanço de 1,7 u × (sen ψ − 2/π) preso ao relógio dos passos (o ponto mais baixo, −1,08 u a 100%, no tick do passo; média zero numa passada), lateral de 1,0 u e rolagem de 0,32° para o lado do pé do último passo, peso zero parado, no ar e no slide (andando a 130 u/s, 0,52); inclinação de 1,3° a 250 u/s de lado e 4,6° no slide; chute do wall-jump com pico de 5,7° em ~77 ms (4 ticks e meio), para longe da parede; mergulho com pico de 4,4 u no pouso do pulo, 12 u na queda de 420 u e 16,8 u no fatal (2,9 u e 7,8 u no nível Médio, o padrão); molas exatas (dois ticks de 1/64 s = um de 1/32 s); a sensação não muda o olho de verdade, o estado, a precisão nem a telemetria; corpo com volume constante, pulo e wall-jump de −10% a +14%, esticada de 12% caindo a 800 u/s, pouso achatando 11%, 17%, 30% e 42% (pulo, 128 u, 420 u, fatal) e passando ~25% do normal na volta, morte a −62%, agachar de 72 para 54 u com o pivô no tornozelo; sola de 15,8 × 7,8 u (16,4 sem o corte do bico); pegadas: passo com 75% de fundo (some em 191 poses, ~15,9 s), par do pouso com 100% (255 poses, 21,25 s), sulco do slide em 128 poses (~10,7 s), brilho em 85 (7,1 s); 12 passos do esmaecimento por segundo de tick, contados sem erro de arredondamento; a passada única por placa igual a aplicar a fila item a item; 720 × 520 texels na placa da pista (4/u), teto de 1024 por lado; 10 min simulados na pista sem nenhuma penetração, preso ou queda para fora e iguais bit a bit; 5 seeds × 10 min no `tools/phase3-acceptance.mjs`, idem.

**Números medidos no navegador** (a implementação verificada, com a entrada pelo `KeyboardMouse` do jogo e o ponteiro liberado por script): sensação no nível Médio (60/70/65): vertical de −0,65 u no tick do passo a +0,37 u no meio da passada, lateral ±0,6 u e rolagem ±0,19° a cada passo (faca: 19 ticks, 297 ms — o relógio de 291 ms do CS em ticks de 64 Hz); a 100% o ponto mais baixo em −1,08 u; "Reduzir movimento" zera tudo; slide na faixa com 151,2 u em 0,61 s, 300 → 204,7 u/s, a inclinação de −3,2° e o mergulho de −1,2 u; poço com as 4 paredes: ápice 253 u, de pé a 230 u, o chute do primeiro wall-jump com 3,9°; counter-strafe com a faca e com a AK: "contra" em 5 ticks (78 ms) e "soltar" em 13 ticks (203 ms); pegadas: GPU × JS em 374 400 texels de uma placa (22 889 marcados), lábio igual até 1/255, fundo e brilho até 2/255 fora de 2 texels exatamente num degrau (borda de cravo e fim do brilho); esmaecimento na GPU igual ao de 8 bits (brilho em 85 poses, passo em 191, pouso em 255) e nenhum desenho depois que a placa zera; corpo esticado 9,9% no ar com a sombra de contato a 28 u e 0,36; memória: pista com 40 geometrias / 90 texturas / 44 programas nas três entradas, menu com 2 / 34 / 21 (no projeto, numa sessão nova: 40 / 90 / 43 e 2 / 34 / 20, também iguais nos três ciclos), heap de volta a ~52 MB depois da coleta e nenhum ouvinte acumulando; robô de 10 min na pista com o monitor ligado, no projeto (com o zigue-zague no roteiro): 38 433 ticks conferidos, penetração 0 · preso 0 · abaixo do chão 0, FPS médio 143,9 e 1% low 119,2 (quadro de 7,0 ms, p95 de 7,1 ms, na tela de 144 Hz), memória em 597 amostras com texturas (96) e programas (45) parados e geometrias de 46 a 47 (uma peça que entra em cena pela primeira vez), heap entre 54 e 84 MB, as 12 estações visitadas, o slide, o poço e o counter-strafe iguais aos medidos à mão e o zigue-zague em B com 4 wall-jumps (folga de 136,7 u com a faca e 38,7 u com a AK, como na 3.4); na cópia de trabalho, antes do zigue-zague entrar no roteiro, 143,9 e 121,2.

**Validação do próprio plano:** antes de ser gravado, o plano foi aplicado tarefa por tarefa numa cópia limpa do projeto (a árvore da 3.4) com o extrator e os pares: em cada tarefa os testes novos falham antes da implementação (as falhas esperadas estão em cada passo) e passam depois, a suíte inteira passa ao fim de cada tarefa (255 → 267 → 269 → 279 → 288 → 290 → 294) e, no fim, cada arquivo criado ou alterado ficou idêntico ao da implementação verificada no navegador.

---

## Mapa de arquivos

| Arquivo | Responsabilidade |
|---|---|
| `src/player/footsteps.js`, `src/player/movement.js` | `stepSpan`: o tamanho do intervalo atual do relógio dos passos, junto com o `stepTimer` (passo, parado, pouso pesado, estado novo, cópia) |
| `src/data/cameraFeel.js` | **novo** — valores de 100% da sensação (a referência na escala do CS) e os níveis Desligado, Tático, Médio (padrão) e Forte |
| `src/player/cameraFeel.js` | **novo** — sensação da câmera, pura e por tick: balanço, inclinação, chute do wall-jump e mergulho, com as molas exatas |
| `src/player/playerPawn.js` | a sensação no tick (zera morto, no noclip e no teleporte) e somada à câmera interpolada |
| `src/data/configSchema.js`, `src/ui/settingControls.js`, `src/ui/settingsScreen.js` | seção "Conforto": balanço, inclinação e mergulho (0–100%) acima do "Reduzir movimento"; `debug.monitor` |
| `src/data/referenceDoll.js` | **novo** — boneco de referência: botas, mola do corpo, squash & stretch e sombra de contato |
| `src/data/footprints.js` | **novo** — sola da bota com cravos, forma da marca, marcas dos eventos, mapa por placa e esmaecimento |
| `src/clay/prints/sole.js` | **novo** — contorno e cravos da sola em JS e em GLSL gerado dos mesmos números |
| `src/clay/kit/boots.js` | **novo** — bota de massinha com cravos no contorno da sola |
| `src/clay/kit/scaleMarker.js` | o boneco de referência sobre as botas (`referenceDoll`: grupo, botas, corpo e o tornozelo) |
| `src/characters/squashStretch.js` | **novo** — mola do corpo, pura: pulo, queda, pouso, morte, limites e a forma com volume constante |
| `src/characters/playerBody.js` | **novo** — o corpo no mundo: pose a 12/s, pés interpolados, pivô no tornozelo, sombra de contato |
| `src/clay/prints/marks.js` | **novo** — marcas de cada evento, referencial da placa e o texel de cada marca em 8 bits |
| `src/clay/prints/printQueue.js` | **novo** — fila na ordem do jogo e o plano de uma pose; a vida de cada placa |
| `src/clay/prints/surface.js` | **novo** — tamanho do mapa, escolha da placa e a superfície (alvo de render ligado ao material) |
| `src/clay/clayImprint.js` | **novo** — as camadas de impressão do `ClayMaterial`: a fixa (3.3) e a das pegadas (`CLAY_PRINTS`) |
| `src/clay/ClayMaterial.js` | as camadas vêm do `clayImprint.js`; `setPrints`; a chave do programa com as pegadas |
| `src/clay/prints/stampPass.js` | **novo** — esmaecimento e carimbo instanciado numa chamada de render por placa |
| `src/clay/prints/printSystem.js` | **novo** — o sistema: marcas do tick, fila, desenho na pose, limpeza, GPU reiniciada |
| `src/maps/pista/visual/clayPlates.js`, `visual/index.js`, `index.js` | as sete placas como `printSurfaces`; os lotes das estações |
| `src/debug/commands.js` | `pegadas` e `pegadas limpar` |
| `src/data/sandbox.js` | `MONITOR`: folga da checagem, amostras de memória, janela do FPS e o painel |
| `src/debug/moveMonitor.js` | **novo** — monitor do movimento: registro puro, relatório em texto e o painel |
| `src/debug/movementCommands.js`, `styles/debug.css` | `cl_monitor` e `monitor [zerar]`; o painel do monitor |
| `src/modes/matchState.js` | escalas da sensação no tick, o corpo, as pegadas e o monitor |
| `tests/pistaSim.js` | **novo** — a simulação aleatória da pista (com as checagens do monitor) usada pela suíte e pela varredura |
| `tools/phase3-acceptance.mjs`, `package.json` | **novo** — varredura de aceite: 5 seeds × 10 min, repetição bit a bit, relatório (`npm run aceite:fase3`) |
| testes novos | `cameraFeel`, `squashStretch`, `footprints`, `moveMonitor` |
| testes que ganham casos | `footsteps`, `playerPawn`, `pistaFuzz` |

---

### Tarefa 0: Extrator dos blocos do plano

**Files:**
- Create: `<scratchpad>/extract-plan.mjs` (fora do projeto)

- [ ] **Passo 1: Criar o extrator** — o mesmo da 3.1 à 3.4: lê o plano e grava cada bloco ` ```js file=... ` (ou `css`) no caminho indicado, só para os arquivos pedidos na linha de comando.

```js
// Uso: node extract-plan.mjs <plano.md> <raiz do projeto> <arquivo> [arquivo...]
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { dirname, join } from 'node:path';

const [plan, root, ...wanted] = process.argv.slice(2);
const text = readFileSync(plan, 'utf8');
const re = /^```[a-z]+ file=(\S+)\n([\s\S]*?)^```$/gm;
const blocks = new Map();
for (const m of text.matchAll(re)) blocks.set(m[1], m[2]);
for (const file of wanted) {
  if (!blocks.has(file)) throw new Error(`bloco não encontrado no plano: ${file}`);
  const out = join(root, file);
  mkdirSync(dirname(out), { recursive: true });
  writeFileSync(out, blocks.get(file));
  console.log(`gravado ${file} (${blocks.get(file).split('\n').length - 1} linhas)`);
}
```

- [ ] **Passo 2: Conferir** — `node extract-plan.mjs docs/phases/phase-3.5-plan.md . src/data/cameraFeel.js` grava o arquivo pedido (apagar o arquivo de novo: a Tarefa 1 o cria no passo certo).

---

### Tarefa 1: O relógio dos passos (`stepSpan`) e a sensação da câmera, pura

**Files:**
- Create: `src/data/cameraFeel.js`, `src/player/cameraFeel.js`, `tests/cameraFeel.test.js`
- Modify: `src/player/movement.js`, `src/player/footsteps.js`, `tests/footsteps.test.js`

O balanço sai do relógio dos passos do CS (291 ms correndo, 388 ms andando, +100 ms agachado): a fase é ψ = π · (1 − `stepTimer` ÷ `stepSpan`), então o estado de movimento passa a guardar o tamanho do intervalo atual junto com o `stepTimer` — no passo, parado (o `firstStepDelay`), no pouso pesado (400 ms), no estado novo e no `copyMoveState`. A sensação é um módulo puro por tick sobre o estado depois do `playerMove`, os eventos do tick, o yaw e as três escalas (0–1): balanço (vertical com média zero, lateral e rolagem para o lado do pé do último passo, peso suavizado a 8/s), inclinação (de lado pela velocidade no eixo direito, e no slide, suavizada a 9/s), chute do wall-jump (mola crítica de rigidez 170 com o impulso para o lado da normal) e mergulho (mola de rigidez 170 e amortecimento 15; impulso na velocidade calculado para o pico dar 12 u × o fator da queda no pouso, 12% na saída do pulo, 15% no começo do slide e 12% no wall-jump). As molas usam a solução exata (o mesmo resultado em ticks de qualquer tamanho que somem o mesmo tempo). Os valores de 100% são os da referência na escala do CS (40 u por metro); o padrão é o nível Médio (60/70/65%).

- [ ] **Passo 1: Escrever os testes** — o `stepSpan` em todos os lugares do `stepTimer` e a sensação sobre o movimento de verdade (`playerMove` num chão).

Em `tests/footsteps.test.js`, trocar:

```
// Testes dos passos, do pulo e do pouso audíveis (Fase 3.2): cadências do CS:GO a 64 tick, primeiro passo, velocidade
// mínima, audível × silencioso por item e estado, volumes por superfície e agachado, pé alternado e o pouso pesado.
import { test } from 'node:test';
```

por:

```
// Testes dos passos, do pulo e do pouso audíveis (Fase 3.2): cadências do CS:GO a 64 tick, primeiro passo, velocidade
// mínima, audível × silencioso por item e estado, volumes por superfície e agachado, pé alternado e o pouso pesado; o
// tamanho do intervalo atual do relógio (`stepSpan`, subfase 3.5: o balanço da câmera).
import { test } from 'node:test';
```

Em `tests/footsteps.test.js`, trocar:

```
import { BTN } from '../src/player/moveCmd.js';
import { createMoveState } from '../src/player/movement.js';
import { floor, worldOf } from './worldTestUtils.js';
```

por:

```
import { BTN } from '../src/player/moveCmd.js';
import { copyMoveState, createMoveState } from '../src/player/movement.js';
import { floor, worldOf } from './worldTestUtils.js';
```

Em `tests/footsteps.test.js`, trocar:

```
  assert.ok(soft && !soft.audible && !soft.heavy, `queda baixa a ${soft?.speed}`);
});

```

por:

```
  assert.ok(soft && !soft.audible && !soft.heavy, `queda baixa a ${soft?.speed}`);
});

test('relógio (3.5): stepSpan guarda o intervalo atual — no passo, parado, no pouso pesado, no estado novo e na cópia', () => {
  const fresh = createMoveState();
  assert.equal(fresh.stepSpan, firstStepDelay(false));
  assert.equal(fresh.stepSpan, fresh.stepTimer);
  const runner = moving(250);
  assert.ok(stepOnce(runner));
  assert.equal(runner.stepSpan, 300 * 0.97);
  assert.equal(runner.stepSpan, runner.stepTimer);
  // Entre dois passos o tamanho fica e o relógio desce.
  assert.equal(stepOnce(runner), null);
  assert.equal(runner.stepSpan, 291);
  assert.ok(Math.abs(runner.stepTimer - (291 - 1000 / 64)) < 1e-9);
  const slow = moving(65, { duckFlag: true });
  assert.ok(stepOnce(slow));
  assert.equal(slow.stepSpan, 400 * 0.97 + 100);
  const stopped = moving(3, { duckFlag: true });
  stopped.stepSpan = 12;
  assert.equal(stepOnce(stopped), null);
  assert.equal(stopped.stepSpan, firstStepDelay(true));
  assert.equal(stopped.stepTimer, stopped.stepSpan);
  const faller = makePlayer(ground(), [0, 200, 0]);
  let land = null;
  for (let i = 0; i < 64 && !land; i++) land = run(faller, 1, idle).find((e) => e.type === 'land') ?? null;
  assert.ok(land?.heavy, 'queda de 200 u: pouso pesado');
  assert.equal(faller.state.stepSpan, STEPS.roughLandDelay);
  assert.equal(faller.state.stepTimer, STEPS.roughLandDelay);
  assert.equal(copyMoveState(faller.state, createMoveState()).stepSpan, STEPS.roughLandDelay);
});

```

```js file=tests/cameraFeel.test.js
// Testes da sensação da câmera (subfase 3.5): balanço preso ao relógio de passos (o ponto mais baixo no tick do passo,
// média zero numa passada, lado do pé), peso zero no ar, no slide e parado; inclinação de lado pela velocidade e o
// sinal; slide; chute do wall-jump (pico de 5,7° em ~77 ms, para longe da parede); picos do mergulho (4,4 u no pulo e
// 12 u na queda de 420 u a 100%) e o nível Médio; escalas; molas exatas (o mesmo resultado em ticks de qualquer tamanho
// que somem o mesmo tempo). O movimento é o de verdade (playerMove sobre um chão).
import { test } from 'node:test';
import assert from 'node:assert/strict';
import * as THREE from 'three';
import { CAMERA_FEEL, CAMERA_FEEL_DEFAULT, CAMERA_FEEL_LEVELS } from '../src/data/cameraFeel.js';
import { FALL } from '../src/data/movement.js';
import { FEEL_SPRINGS, createCameraFeel, landFactor, resetCameraFeel, updateCameraFeel } from '../src/player/cameraFeel.js';
import { BTN } from '../src/player/moveCmd.js';
import { createMoveState } from '../src/player/movement.js';
import { floor, worldOf } from './worldTestUtils.js';
import { DT, forward, makePlayer, run } from './playerTestUtils.js';

const DEG = Math.PI / 180;
const FULL = Object.freeze({ bob: 1, tilt: 1, dip: 1 });
const BOB = Object.freeze({ bob: 1, tilt: 0, dip: 0 });
const ground = () => worldOf((b) => floor(b));

/** Joga `ticks` ticks do jogador `p` com a sensação `f`; `drive(cmd, i)` monta o comando. Amostras por tick. */
function play(p, f, ticks, drive, scales = FULL) {
  const out = [];
  for (let i = 0; i < ticks; i++) {
    const events = run(p, 1, (c) => drive(c, i));
    updateCameraFeel(f, p.state, events, p.cmd.yaw, scales, DT);
    out.push({ i, y: f.y, side: f.side, roll: f.roll, weight: f.weight, events: events.map((e) => ({ ...e })) });
  }
  return out;
}

/** Estado parado no chão (sem o playerMove): para alimentar eventos soltos. */
function still() {
  const s = createMoveState();
  s.onGround = true;
  return s;
}

/** Aplica um evento no tick 0 e anda `ticks` ticks parado; devolve as saídas por tick. */
function afterEvent(event, ticks, scales = FULL, yaw = 0) {
  const f = createCameraFeel();
  const s = still();
  const out = [];
  for (let i = 0; i < ticks; i++) {
    updateCameraFeel(f, s, i === 0 ? [event] : [], yaw, scales, DT);
    out.push({ y: f.y, roll: f.roll });
  }
  return out;
}

test('dados: o nível Médio é o padrão; os valores de 100% vêm da referência na escala do CS', () => {
  assert.deepEqual(CAMERA_FEEL_DEFAULT, CAMERA_FEEL_LEVELS.medio);
  assert.deepEqual({ ...CAMERA_FEEL_LEVELS.medio }, { bob: 60, tilt: 70, dip: 65 });
  assert.ok(Math.abs(0.03 * 1.4 * 40 - CAMERA_FEEL.bob.vertical) < 0.05);
  assert.ok(Math.abs(0.018 * 1.4 * 40 - CAMERA_FEEL.bob.lateral) < 0.01);
  assert.ok(Math.abs(0.0056 / DEG - CAMERA_FEEL.bob.rollDeg) < 0.01);
  assert.ok(Math.abs(0.022 / DEG - CAMERA_FEEL.tilt.strafeDeg) < 0.05);
  assert.ok(Math.abs(0.08 / DEG - CAMERA_FEEL.tilt.slideDeg) < 0.05);
  assert.ok(Math.abs(0.1 / DEG - CAMERA_FEEL.kick.peakDeg) < 0.05);
  assert.ok(Math.abs(FEEL_SPRINGS.dipPeakTime - 0.09) < 0.002, `pico do mergulho em ${FEEL_SPRINGS.dipPeakTime}`);
  assert.ok(Math.abs(FEEL_SPRINGS.dipOvershoot - 0.11) < 0.005, `passa ${FEEL_SPRINGS.dipOvershoot} na volta`);
  assert.ok(Math.abs(FEEL_SPRINGS.kickPeakTime - 0.0767) < 0.001);
});

test('fator da queda: nada abaixo de 150 u/s, 0,368 no pouso do pulo, 1 no limite seguro e 1,4 no fatal', () => {
  assert.equal(landFactor(149), 0);
  assert.ok(Math.abs(landFactor(301.993377) - 0.3684) < 1e-3);
  assert.equal(landFactor(FALL.safeSpeed), 1);
  assert.ok(Math.abs(landFactor(FALL.fatalSpeed) - 1.4) < 1e-12);
  assert.ok(Math.abs(landFactor(5000) - 1.4) < 1e-12, 'acima do fatal não cresce');
  const mid = landFactor((FALL.safeSpeed + FALL.fatalSpeed) / 2);
  assert.ok(Math.abs(mid - 1.2) < 1e-12);
});

test('balanço: o ponto mais baixo no tick do passo, o mais alto no meio da passada e média zero numa passada', () => {
  const p = makePlayer(ground(), [0, 0, 0]);
  const f = createCameraFeel();
  const out = play(p, f, 64 * 3, (c) => forward(c), BOB);
  const steps = out.filter((o) => o.events.some((e) => e.type === 'step') && o.i > 64);
  assert.ok(steps.length >= 4, `passos: ${steps.length}`);
  const [a, b] = steps;
  const stride = out.slice(a.i, b.i);
  assert.equal(stride.length, 19, 'faca: um passo a cada 19 ticks');
  const w = a.weight;
  assert.ok(w > 0.99, `peso na corrida (250 u/s): ${w}`);
  const low = Math.min(...stride.map((o) => o.y));
  assert.equal(a.y, low, 'o mais baixo é o tick do passo');
  assert.ok(Math.abs(a.y + CAMERA_FEEL.bob.vertical * (2 / Math.PI) * w) < 1e-9);
  const high = Math.max(...stride.map((o) => o.y));
  assert.ok(Math.abs(high - CAMERA_FEEL.bob.vertical * (1 - 2 / Math.PI)) < 0.02, `mais alto: ${high}`);
  const mean = stride.reduce((m, o) => m + o.y, 0) / stride.length;
  assert.ok(Math.abs(mean) < 0.06, `média numa passada ${mean}`);
});

test('balanço: lateral e rolagem para o lado do pé do último passo', () => {
  const p = makePlayer(ground(), [0, 0, 0]);
  const f = createCameraFeel();
  const out = play(p, f, 64 * 3, (c) => forward(c), BOB);
  const steps = out.filter((o) => o.i > 64 && o.events.some((e) => e.type === 'step'));
  for (let k = 0; k + 1 < steps.length; k++) {
    const foot = steps[k].events.find((e) => e.type === 'step').foot;
    const mid = out[steps[k].i + 9];
    const sign = foot === 0 ? -1 : 1; // esquerdo: para a esquerda (lateral negativo) e cabeça para a esquerda (+)
    assert.ok(Math.sign(mid.side) === sign, `pé ${foot}: lateral ${mid.side}`);
    assert.ok(Math.sign(mid.roll) === -sign, `pé ${foot}: rolagem ${mid.roll}`);
    assert.ok(Math.abs(Math.abs(mid.side) - CAMERA_FEEL.bob.lateral) < 0.02, `lateral ${mid.side}`);
    assert.ok(Math.abs(Math.abs(mid.roll) - CAMERA_FEEL.bob.rollDeg * DEG) < 0.02 * DEG);
  }
});

test('peso do balanço: zero parado, no ar e no slide; segue a velocidade (andar a 130 u/s dá 0,52)', () => {
  const idleOut = play(makePlayer(ground(), [0, 0, 0]), createCameraFeel(), 64, (c) => { c.forward = 0; c.buttons = 0; }, BOB);
  assert.ok(idleOut.every((o) => o.weight === 0 && o.y === 0 && o.side === 0));
  const walk = play(makePlayer(ground(), [0, 0, 0]), createCameraFeel(), 64 * 2, (c) => {
    forward(c);
    c.buttons = BTN.WALK;
  }, BOB);
  assert.ok(Math.abs(walk.at(-1).weight - 130 / 250) < 0.01, `andando: ${walk.at(-1).weight}`);
  // Correndo e pulando: no ar o peso cai para zero.
  const p = makePlayer(ground(), [0, 0, 0]);
  const f = createCameraFeel();
  play(p, f, 64, (c) => forward(c), BOB);
  const air = play(p, f, 30, (c, i) => {
    forward(c);
    c.buttons = i === 0 ? BTN.JUMP : 0;
  }, BOB);
  assert.ok(air.at(-1).weight < 0.05, `no ar: ${air.at(-1).weight}`);
  // Slide: o peso cai para zero enquanto desliza.
  const q = makePlayer(ground(), [0, 0, 0]);
  const g = createCameraFeel();
  play(q, g, 64, (c) => forward(c), BOB);
  const slide = play(q, g, 30, (c) => {
    forward(c);
    c.buttons = BTN.DUCK;
  }, BOB);
  assert.ok(slide.some((o) => o.events.some((e) => e.type === 'slide' && e.phase === 'start')));
  assert.ok(slide[25].weight < 0.05, `no slide: ${slide[25].weight}`);
});

test('inclinação: a cabeça pende para o lado do movimento (1,3° a 250 u/s) e o sinal segue o lado', () => {
  const right = play(makePlayer(ground(), [0, 0, 0]), createCameraFeel(), 64 * 2, (c) => {
    c.forward = 0;
    c.side = 1;
    c.buttons = 0;
  }, { bob: 0, tilt: 1, dip: 0 });
  assert.ok(Math.abs(right.at(-1).roll + CAMERA_FEEL.tilt.strafeDeg * DEG) < 0.02 * DEG, `direita: ${right.at(-1).roll / DEG}°`);
  const left = play(makePlayer(ground(), [0, 0, 0]), createCameraFeel(), 64 * 2, (c) => {
    c.forward = 0;
    c.side = -1;
    c.buttons = 0;
  }, { bob: 0, tilt: 0.7, dip: 0 });
  assert.ok(Math.abs(left.at(-1).roll - 0.7 * CAMERA_FEEL.tilt.strafeDeg * DEG) < 0.02 * DEG, `esquerda (70%): ${left.at(-1).roll / DEG}°`);
  // Correndo para a frente: sem inclinação de lado.
  const fwd = play(makePlayer(ground(), [0, 0, 0]), createCameraFeel(), 64, (c) => forward(c), { bob: 0, tilt: 1, dip: 0 });
  assert.ok(Math.abs(fwd.at(-1).roll) < 1e-9);
});

test('slide: a cabeça pende para a direita (4,6°) enquanto desliza e volta depois', () => {
  const p = makePlayer(ground(), [0, 0, 0]);
  const f = createCameraFeel();
  play(p, f, 64, (c) => forward(c), { bob: 0, tilt: 1, dip: 0 });
  const out = play(p, f, 90, (c, i) => {
    forward(c);
    c.buttons = i < 38 ? BTN.DUCK : 0;
  }, { bob: 0, tilt: 1, dip: 0 });
  const minRoll = Math.min(...out.map((o) => o.roll));
  assert.ok(minRoll < -3.9 * DEG && minRoll > -4.61 * DEG, `no slide: ${minRoll / DEG}°`);
  assert.ok(Math.abs(out.at(-1).roll) < 0.4 * DEG, `depois: ${out.at(-1).roll / DEG}°`);
});

test('wall-jump: chute de 5,7° em ~77 ms para longe da parede (parede à direita → cabeça para a esquerda)', () => {
  // Olhando para −Z (yaw 0) o eixo direito é +X: parede à direita tem a normal −X (para o jogador).
  const out = afterEvent({ type: 'walljump', nx: -1, nz: 0 }, 40, { bob: 0, tilt: 1, dip: 0 });
  const peak = Math.max(...out.map((o) => o.roll));
  const at = out.findIndex((o) => o.roll === peak) + 1;
  assert.ok(Math.abs(peak - CAMERA_FEEL.kick.peakDeg * DEG) < 0.03 * DEG, `pico ${peak / DEG}°`);
  assert.equal(at, 5, 'no 5º tick (78 ms)');
  const fade = out[Math.round(0.4 * 64) - 1].roll / peak;
  assert.ok(fade > 0.05 && fade < 0.1, `~8% em 0,4 s: ${fade}`);
  const mirrored = afterEvent({ type: 'walljump', nx: 1, nz: 0 }, 10, { bob: 0, tilt: 1, dip: 0 });
  assert.ok(Math.abs(Math.min(...mirrored.map((o) => o.roll)) + peak) < 1e-12, 'parede à esquerda: o espelho');
  const ahead = afterEvent({ type: 'walljump', nx: 0, nz: 1 }, 10, { bob: 0, tilt: 1, dip: 0 });
  assert.ok(ahead.every((o) => Math.abs(o.roll) < 1e-12), 'parede à frente: sem chute de lado');
});

test('mergulho: pico de 4,4 u no pouso do pulo e de 12 u na queda de 420 u a 100%; 2,9 u e 7,8 u no Médio', () => {
  const dipOf = (speed, k) => -Math.min(...afterEvent({ type: 'land', speed }, 40, { bob: 0, tilt: 0, dip: k }).map((o) => o.y));
  assert.ok(Math.abs(dipOf(301.993377, 1) - 4.42) < 0.03, `pulo ${dipOf(301.993377, 1)}`);
  assert.ok(Math.abs(dipOf(FALL.safeSpeed, 1) - 12) < 0.05, `420 u ${dipOf(FALL.safeSpeed, 1)}`);
  assert.ok(Math.abs(dipOf(FALL.fatalSpeed, 1) - 16.8) < 0.07, `fatal ${dipOf(FALL.fatalSpeed, 1)}`);
  assert.ok(Math.abs(dipOf(301.993377, 0.65) - 2.87) < 0.03, `Médio, pulo ${dipOf(301.993377, 0.65)}`);
  assert.ok(Math.abs(dipOf(FALL.safeSpeed, 0.65) - 7.8) < 0.04, `Médio, 420 u ${dipOf(FALL.safeSpeed, 0.65)}`);
  assert.ok(dipOf(140, 1) === 0, 'pouso lento não mergulha');
  const land = afterEvent({ type: 'land', speed: FALL.safeSpeed }, 64);
  const low = Math.min(...land.map((o) => o.y));
  assert.equal(land.findIndex((o) => o.y === low) + 1, 6, 'pico em ~90 ms (6º tick)');
  const over = Math.max(...land.map((o) => o.y));
  assert.ok(over > 0.1 * 12 && over < 0.12 * 12, `passa ~11% na volta: ${over}`);
  // Pulo, começo do slide e wall-jump: 12%, 15% e 12% do máximo.
  const peakOf = (e) => -Math.min(...afterEvent(e, 20, { bob: 0, tilt: 0, dip: 1 }).map((o) => o.y));
  assert.ok(Math.abs(peakOf({ type: 'jump' }) - 1.44) < 0.02);
  assert.ok(Math.abs(peakOf({ type: 'slide', phase: 'start' }) - 1.8) < 0.02);
  assert.ok(peakOf({ type: 'slide', phase: 'end' }) === 0, 'o fim do slide não mergulha');
  assert.ok(Math.abs(peakOf({ type: 'walljump', nx: 0, nz: 1 }) - 1.44) < 0.02);
});

test('escalas: zero em tudo não mexe a câmera; cada controle só mexe o seu efeito', () => {
  const zero = { bob: 0, tilt: 0, dip: 0 };
  const p = makePlayer(ground(), [0, 0, 0]);
  const f = createCameraFeel();
  const out = play(p, f, 64 * 3, (c, i) => {
    c.forward = 1;
    c.side = i % 60 < 30 ? 1 : -1;
    c.buttons = i % 50 === 0 ? BTN.JUMP : 0;
  }, zero);
  assert.ok(out.every((o) => o.y === 0 && o.side === 0 && o.roll === 0));
  const onlyDip = afterEvent({ type: 'walljump', nx: -1, nz: 0 }, 20, { bob: 0, tilt: 0, dip: 1 });
  assert.ok(onlyDip.every((o) => o.roll === 0) && onlyDip.some((o) => o.y < 0));
  const onlyTilt = afterEvent({ type: 'land', speed: FALL.safeSpeed }, 20, { bob: 0, tilt: 1, dip: 0 });
  assert.ok(onlyTilt.every((o) => o.y === 0));
});

test('molas exatas: dois ticks de 1/64 s dão o mesmo que um de 1/32 s; reset zera tudo', () => {
  const s = still();
  const a = createCameraFeel();
  const b = createCameraFeel();
  const events = [{ type: 'land', speed: 900 }, { type: 'walljump', nx: -0.6, nz: 0.8 }];
  updateCameraFeel(a, s, events, 0.3, FULL, 0);
  updateCameraFeel(b, s, events, 0.3, FULL, 0);
  for (let i = 0; i < 20; i++) {
    updateCameraFeel(a, s, [], 0.3, FULL, DT);
    updateCameraFeel(a, s, [], 0.3, FULL, DT);
    updateCameraFeel(b, s, [], 0.3, FULL, 2 * DT);
  }
  for (const k of ['dip', 'dipV', 'kick', 'kickV', 'y', 'roll', 'tilt', 'weight']) {
    assert.ok(Math.abs(a[k] - b[k]) < 1e-9, `${k}: ${a[k]} × ${b[k]}`);
  }
  resetCameraFeel(a);
  assert.deepEqual(a, createCameraFeel());
  // A velocidade do tick só entra pela velocidade do estado: o mesmo estado em yaw oposto espelha a inclinação.
  const t1 = createCameraFeel();
  const t2 = createCameraFeel();
  const moving = still();
  moving.velocity.copy(new THREE.Vector3(200, 0, 0));
  updateCameraFeel(t1, moving, [], 0, { bob: 0, tilt: 1, dip: 0 }, DT);
  updateCameraFeel(t2, moving, [], Math.PI, { bob: 0, tilt: 1, dip: 0 }, DT);
  assert.ok(Math.abs(t1.roll + t2.roll) < 1e-12 && t1.roll < 0);
});
```

- [ ] **Passo 2: Rodar e ver falhar**

Run: `node --test tests/footsteps.test.js tests/cameraFeel.test.js`
Expected: FAIL — `cameraFeel.test.js` não carrega (`ERR_MODULE_NOT_FOUND`: `src/data/cameraFeel.js`); em `footsteps.test.js`, "relógio (3.5): stepSpan guarda o intervalo atual…" falha (o estado não tem `stepSpan`).

- [ ] **Passo 3: `stepSpan` no estado de movimento e no relógio dos passos**

Em `src/player/movement.js`, trocar:

```
    stepTimer: firstStepDelay(false), // relógio dos passos (ms)
    stepFoot: 0, // pé do próximo passo (0 esquerdo, 1 direito)
```

por:

```
    stepTimer: firstStepDelay(false), // relógio dos passos (ms)
    stepSpan: firstStepDelay(false), // tamanho (ms) do intervalo atual do relógio (o balanço da câmera da 3.5)
    stepFoot: 0, // pé do próximo passo (0 esquerdo, 1 direito)
```

Em `src/player/movement.js`, trocar:

```
  dst.stepTimer = src.stepTimer;
  dst.stepFoot = src.stepFoot;
```

por:

```
  dst.stepTimer = src.stepTimer;
  dst.stepSpan = src.stepSpan;
  dst.stepFoot = src.stepFoot;
```

Em `src/player/movement.js`, trocar:

```
  s.stamina = Math.min(sv.staminamax, Math.max(0, s.stamina + sv.staminalandcost * fall));
  if (fall >= STEPS.roughLandSpeed) s.stepTimer = STEPS.roughLandDelay;
  env.events.push({
```

por:

```
  s.stamina = Math.min(sv.staminamax, Math.max(0, s.stamina + sv.staminalandcost * fall));
  if (fall >= STEPS.roughLandSpeed) s.stepTimer = s.stepSpan = STEPS.roughLandDelay;
  env.events.push({
```

Em `src/player/footsteps.js`, trocar:

```
// enquanto o passo é silencioso; aqui continua contando. No slide (subfase 3.4) não há passo: o relógio fica parado e
// segue de onde estava depois. Eventos no `env.events` do playerMove.

```

por:

```
// enquanto o passo é silencioso; aqui continua contando. No slide (subfase 3.4) não há passo: o relógio fica parado e
// segue de onde estava depois. Eventos no `env.events` do playerMove. O estado guarda também o tamanho do intervalo
// atual (`stepSpan`, subfase 3.5): o balanço da câmera acompanha o relógio (src/player/cameraFeel.js).

```

Em `src/player/footsteps.js`, trocar:

```

/** Um tick do relógio dos passos. Estado em `s.stepTimer` (ms) e `s.stepFoot` (0 esquerdo, 1 direito). */
export function updateSteps(s, env) {
```

por:

```

/**
 * Um tick do relógio dos passos. Estado em `s.stepTimer` (ms que faltam), `s.stepSpan` (ms do intervalo atual) e
 * `s.stepFoot` (pé do próximo passo: 0 esquerdo, 1 direito).
 */
export function updateSteps(s, env) {
```

Em `src/player/footsteps.js`, trocar:

```
  if (speedSq < STEPS.stoppedSpeedSq) {
    s.stepTimer = firstStepDelay(s.duckFlag);
    return;
```

por:

```
  if (speedSq < STEPS.stoppedSpeedSq) {
    s.stepTimer = s.stepSpan = firstStepDelay(s.duckFlag);
    return;
```

Em `src/player/footsteps.js`, trocar:

```
  const fast = speed >= (ducked ? STEPS.duckRunSpeed : STEPS.runSpeed);
  s.stepTimer = (fast ? STEPS.fastInterval : STEPS.slowInterval) * STEPS.frequency + (ducked ? STEPS.duckExtra : 0);
  const surface = SURFACES[s.groundSurface];
```

por:

```
  const fast = speed >= (ducked ? STEPS.duckRunSpeed : STEPS.runSpeed);
  const interval = (fast ? STEPS.fastInterval : STEPS.slowInterval) * STEPS.frequency + (ducked ? STEPS.duckExtra : 0);
  s.stepTimer = s.stepSpan = interval;
  const surface = SURFACES[s.groundSurface];
```

- [ ] **Passo 4: Números da sensação**

```js file=src/data/cameraFeel.js
// Sensação da câmera em primeira pessoa (subfase 3.5; desenho em docs/phases/phase-3.md, seção 3.5): balanço preso ao
// relógio dos passos, inclinação ao andar de lado e no slide, chute de rolagem no wall-jump e mergulho com mola no
// pouso, na saída do pulo, no começo do slide e no wall-jump. Os valores de 100% são os do Doodle District
// (src/player.js da referência, em metros) na escala do CS: 40 u por metro (olho de 64 u ÷ 1,6 m) e a corrida da
// referência (10,6 m/s) na faca (250 u/s). Os três controles da seção "Conforto" (0–100%) multiplicam os valores de
// 100%; "Reduzir movimento" zera os três. Só visual: tiro, precisão, rede, replay e medidores usam o olho de verdade
// (PlayerPawn.eyeOffset).
// Ficam de fora, de propósito: o chute de FOV da referência (o FOV fixo preserva a leitura da mira e da luneta) e a
// tremida aleatória dos pousos duros (determinismo e conforto).

const F = Object.freeze;

export const CAMERA_FEEL = F({
  referenceSpeed: 250, // u/s: a corrida da referência na escala do CS (a faca)
  bob: F({
    // Referência: vertical |sen| × 0,03 m, lateral 0,018 m e rolagem 0,004 rad, com o peso de 1,4 na corrida.
    vertical: 1.7, // u: o ponto mais baixo no passo, o mais alto no meio da passada (o corpo sobre o pé de apoio)
    lateral: 1.0, // u: para o lado do pé do último passo
    rollDeg: 0.32, // °: para o mesmo lado
    weightRate: 8, // 1/s: o peso segue o alvo (velocidade no plano ÷ referência) com 1 − e^(−8·dt) por tick
    minSpeed: 90, // u/s: abaixo disso não há passo (STEPS.walkSpeed) nem balanço
    minSpeedDuck: 60, // o mesmo agachado (STEPS.duckWalkSpeed)
  }),
  tilt: F({
    strafeDeg: 1.3, // ° na velocidade de referência para o lado (0,022 rad): a cabeça pende para o lado do movimento
    slideDeg: 4.6, // ° no slide (0,08 rad), sempre para a direita, como na referência
    rate: 9, // 1/s: suavização da inclinação (1 − e^(−9·dt) por tick)
  }),
  kick: F({
    // Wall-jump: rolagem para longe da parede (0,1 rad da referência) numa mola crítica — pico em 1/ω = 77 ms e ~8% do
    // pico em 0,4 s.
    peakDeg: 5.7,
    stiffness: 170, // ω = √170 = 13,04/s
  }),
  dip: F({
    // Mergulho do olho (u, para baixo) numa mola sub-amortecida: pico em 90 ms, passa ~11% na volta. O impulso vai na
    // velocidade da mola, calculado para o pico dar `max` × o fator.
    max: 12, // u no fator 1: o pouso da queda do limite seguro (420 u, FALL.safeSpeed)
    stiffness: 170,
    damping: 15,
    minFall: 150, // u/s: pouso mais lento não mergulha
    fatalExtra: 0.4, // acima do limite seguro, mais até 40% na queda fatal (FALL.fatalSpeed)
    jump: 0.12, // fração do máximo na saída do pulo
    slide: 0.15, // no começo do slide (a queda de 18 u do olho continua sendo a suavização da 3.4)
    wallJump: 0.12, // no wall-jump
  }),
});

/** Níveis mostrados no desenho: % de balanço, inclinação e mergulho. O padrão do jogo é o Médio. */
export const CAMERA_FEEL_LEVELS = F({
  desligado: F({ bob: 0, tilt: 0, dip: 0 }),
  tatico: F({ bob: 0, tilt: 30, dip: 35 }),
  medio: F({ bob: 60, tilt: 70, dip: 65 }),
  forte: F({ bob: 100, tilt: 100, dip: 100 }),
});

export const CAMERA_FEEL_DEFAULT = CAMERA_FEEL_LEVELS.medio;
```

- [ ] **Passo 5: A sensação, pura**

```js file=src/player/cameraFeel.js
// Sensação da câmera em primeira pessoa (subfase 3.5; números em src/data/cameraFeel.js): módulo puro, por tick (64
// Hz), sobre o estado de movimento e os eventos do tick. As molas andam pela solução exata (o mesmo resultado em
// qualquer tamanho de tick) e as suavizações por 1 − e^(−taxa·dt); a saída do tick anterior e a do atual são
// interpoladas no quadro como o resto da câmera (PlayerPawn.updateCamera). Saídas: deslocamento vertical e lateral (u,
// no eixo direito da câmera) e rolagem (rad, em volta do eixo da vista: a mira não sai do lugar). Sem giro de pitch — o
// "view punch" do CS tiraria a mira do lugar. Só visual.
//  - Balanço: ψ = π · (1 − stepTimer ÷ stepSpan), o ritmo do relógio de passos do CS; o ponto mais baixo no passo, o
//    mais alto no meio da passada, média zero numa passada; lateral e rolagem para o lado do pé do último passo. O peso
//    segue a velocidade no plano no chão, fora do slide e acima da velocidade mínima de passo.
//  - Inclinação: a cabeça pende para o lado do movimento; no slide, para a direita. Wall-jump: chute numa mola crítica
//    para longe da parede.
//  - Mergulho: mola sub-amortecida com impulso no pouso (pelo fator da queda, o mesmo do achatamento do corpo), na
//    saída do pulo, no começo do slide e no wall-jump.

import { CAMERA_FEEL } from '../data/cameraFeel.js';
import { FALL } from '../data/movement.js';

const DEG = Math.PI / 180;
const C = CAMERA_FEEL;
const TWO_OVER_PI = 2 / Math.PI;

const clamp = (v, lo, hi) => (v < lo ? lo : v > hi ? hi : v);

/** Mola sub-amortecida x'' = −k·x − d·x' (ζ < 1): constantes da solução exata e o pico por unidade de velocidade. */
function damped(k, d) {
  const w0 = Math.sqrt(k);
  const a = d / 2; // ζ·ω0
  const wd = Math.sqrt(k - a * a);
  const tPeak = Math.atan2(wd, a) / wd;
  return { k, a, wd, tPeak, peak: (Math.exp(-a * tPeak) * Math.sin(wd * tPeak)) / wd, w0 };
}

const DIP = damped(C.dip.stiffness, C.dip.damping);
const KICK_W = Math.sqrt(C.kick.stiffness);
/** Pico da mola crítica por unidade de velocidade: x(t) = v·t·e^(−ωt), máximo em t = 1/ω. */
const KICK_PEAK = 1 / (KICK_W * Math.E);

/** Constantes das molas (os testes conferem os tempos do desenho). */
export const FEEL_SPRINGS = Object.freeze({
  dipPeakTime: DIP.tPeak, // s até o pico do mergulho (~90 ms)
  dipOvershoot: Math.exp((-DIP.a * Math.PI) / DIP.wd), // fração que passa na volta (~11%)
  kickPeakTime: 1 / KICK_W, // s até o pico do chute do wall-jump (~77 ms)
});

/**
 * Fator da queda no pouso (o mergulho da câmera e o achatamento do corpo): 0 abaixo de 150 u/s; queda ÷ limite seguro
 * até ele (0,368 no pouso do pulo, 1 na queda de 420 u); acima, mais até 40% na queda fatal.
 */
export function landFactor(fall) {
  if (!(fall >= C.dip.minFall)) return 0;
  if (fall <= FALL.safeSpeed) return fall / FALL.safeSpeed;
  return 1 + C.dip.fatalExtra * Math.min(1, (fall - FALL.safeSpeed) / (FALL.fatalSpeed - FALL.safeSpeed));
}

/** Estado da sensação de um jogador (dados simples). */
export function createCameraFeel() {
  return {
    weight: 0, // peso do balanço (0–1)
    tilt: 0, // inclinação suavizada (rad)
    kick: 0, // rolagem do chute do wall-jump (rad) e a velocidade da mola
    kickV: 0,
    dip: 0, // mergulho (u, negativo = para baixo) e a velocidade da mola
    dipV: 0,
    y: 0, // saída do tick: deslocamento vertical (u)
    side: 0, // deslocamento lateral no eixo direito da câmera (u)
    roll: 0, // rolagem (rad; positivo = cabeça para a esquerda, a rolagem do three.js)
  };
}

/** Zera tudo na hora (morto, noclip, teleporte, volta ao jogo). */
export function resetCameraFeel(f) {
  f.weight = 0;
  f.tilt = 0;
  f.kick = 0;
  f.kickV = 0;
  f.dip = 0;
  f.dipV = 0;
  f.y = 0;
  f.side = 0;
  f.roll = 0;
  return f;
}

/** Um passo exato da mola sub-amortecida do mergulho (dt qualquer). */
function stepDip(f, dt) {
  const e = Math.exp(-DIP.a * dt);
  const c = Math.cos(DIP.wd * dt);
  const s = Math.sin(DIP.wd * dt);
  const x = f.dip;
  const v = f.dipV;
  f.dip = e * (x * c + ((v + DIP.a * x) / DIP.wd) * s);
  f.dipV = e * (v * c - ((DIP.a * v + DIP.k * x) / DIP.wd) * s);
}

/** Um passo exato da mola crítica do chute (dt qualquer). */
function stepKick(f, dt) {
  const e = Math.exp(-KICK_W * dt);
  const x = f.kick;
  const v = f.kickV;
  const b = v + KICK_W * x;
  f.kick = (x + b * dt) * e;
  f.kickV = (v - KICK_W * b * dt) * e;
}

/**
 * Um tick. `s`: estado de movimento depois do playerMove; `events`: os eventos do tick (land {speed}, jump,
 * slide {phase}, walljump {nx, nz}); `yaw`: o olhar do tick; `scales`: {bob, tilt, dip} de 0 a 1 (a seção "Conforto").
 */
export function updateCameraFeel(f, s, events, yaw, scales, dt) {
  const kb = scales.bob;
  const kt = scales.tilt;
  const kd = scales.dip;
  const dipUnit = (C.dip.max * kd) / DIP.peak;
  const rightX = Math.cos(yaw);
  const rightZ = -Math.sin(yaw);
  for (let i = 0; i < events.length; i++) {
    const e = events[i];
    switch (e.type) {
      case 'land':
        f.dipV -= dipUnit * landFactor(e.speed);
        break;
      case 'jump':
        f.dipV -= dipUnit * C.dip.jump;
        break;
      case 'slide':
        if (e.phase === 'start') f.dipV -= dipUnit * C.dip.slide;
        break;
      case 'walljump': {
        f.dipV -= dipUnit * C.dip.wallJump;
        // Normal da parede (para o jogador) no eixo direito do olhar: parede à direita → normal para a esquerda → a
        // cabeça tomba para a esquerda, para longe da parede.
        const lateral = e.nx * rightX + e.nz * rightZ;
        f.kickV -= (lateral * C.kick.peakDeg * DEG * kt) / KICK_PEAK;
        break;
      }
      default:
        break;
    }
  }
  const v = s.velocity;
  const speed = Math.hypot(v.x, v.z);
  const minSpeed = s.duckFlag ? C.bob.minSpeedDuck : C.bob.minSpeed;
  const weightTarget = s.onGround && !s.sliding && speed >= minSpeed ? Math.min(1, speed / C.referenceSpeed) : 0;
  f.weight += (weightTarget - f.weight) * (1 - Math.exp(-C.bob.weightRate * dt));
  const lateralSpeed = clamp((v.x * rightX + v.z * rightZ) / C.referenceSpeed, -1, 1);
  const tiltTarget = -C.tilt.strafeDeg * DEG * kt * lateralSpeed - (s.sliding ? C.tilt.slideDeg * DEG * kt : 0);
  f.tilt += (tiltTarget - f.tilt) * (1 - Math.exp(-C.tilt.rate * dt));
  stepDip(f, dt);
  stepKick(f, dt);
  const span = s.stepSpan > 0 ? s.stepSpan : 1;
  const psi = Math.PI * clamp(1 - s.stepTimer / span, 0, 1);
  const sn = Math.sin(psi);
  const w = f.weight * kb;
  // Pé do último passo: o relógio já trocou para o próximo (stepFoot), então é o outro. Esquerdo (0) → lado −1.
  const side = s.stepFoot === 1 ? -1 : 1;
  f.y = f.dip + C.bob.vertical * w * (sn - TWO_OVER_PI);
  f.side = side * C.bob.lateral * w * sn;
  f.roll = f.tilt + f.kick - side * C.bob.rollDeg * DEG * w * sn;
  return f;
}
```

- [ ] **Passo 6: Rodar os testes da tarefa**

Run: `node --test tests/footsteps.test.js tests/cameraFeel.test.js tests/movementFuzz.test.js`
Expected: PASS — todos os testes dos três arquivos passando.

- [ ] **Passo 7: Suíte inteira**

Run: `npm test`
Expected: PASS — 267 testes passando.

- [ ] **Passo final: Commit** (só com o pedido do usuário)

```bash
git add src/player/movement.js src/player/footsteps.js src/data/cameraFeel.js src/player/cameraFeel.js tests/footsteps.test.js tests/cameraFeel.test.js
git commit -m "MASSACRE 3.5: relógio dos passos com stepSpan e a sensação da câmera, pura" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Tarefa 2: A câmera no jogo e a seção "Conforto"

**Files:**
- Modify: `src/player/playerPawn.js`, `src/data/configSchema.js`, `src/ui/settingControls.js`, `src/ui/settingsScreen.js`, `src/modes/matchState.js`, `tests/playerPawn.test.js`

O `PlayerPawn` roda a sensação no fim do tick, depois dos eventos (o pouso de agora já mergulha), com as escalas que o `MatchState` passa (`feel`, como já passa o `reduceMotion`); morto (inclusive quem morreu no tick), no noclip e no teleporte, zera na hora. A saída do tick anterior e a do atual são interpoladas no quadro como o resto da câmera: o deslocamento vertical e o lateral (no eixo direito do yaw) somam na posição e a rolagem soma à do morto — o olho de verdade (`eyeOffset`), o estado, a precisão, a telemetria e o `cl_showpos` não mudam. A seção "Conforto" da aba Gráficos ganha os três controles (0–100%, passo 5, com o valor em %) acima do "Reduzir movimento", que zera os três (rótulo "Reduzir movimento (sem balanço, flicker nem boil)").

- [ ] **Passo 1: Escrever os testes** — a sensação só mexe na câmera; o pouso de 420 u mergulha ~12 u a 100% e zera morto, no noclip e no teleporte.

Em `tests/playerPawn.test.js`, trocar:

```
// Testes do jogador local (Fases 3.1, 3.2 e 3.4): comando do tick a partir da entrada, andar, interpolação da câmera,
// suavização do degrau, noclip pelo tick, teleporte; troca de item pelo comando e automática, luneta (FOV interpolado,
// sensibilidade, velocidade), precisão no tick, telemetria e os eventos no barramento — com o slide e o wall-jump.
import { test } from 'node:test';
```

por:

```
// Testes do jogador local (Fases 3.1, 3.2, 3.4 e 3.5): comando do tick a partir da entrada, andar, interpolação da
// câmera, suavização do degrau, noclip pelo tick, teleporte; troca de item pelo comando e automática, luneta (FOV
// interpolado, sensibilidade, velocidade), precisão no tick, telemetria e os eventos no barramento — com o slide e o
// wall-jump; a sensação da câmera (só a câmera se mexe; zera morto, no noclip e no teleporte).
import { test } from 'node:test';
```

Em `tests/playerPawn.test.js`, trocar:

```
  assert.ok(t.flags[t.slot(t.count - 1)] & TFLAG.WALLJUMP, 'marca do wall-jump no tick do chute');
});

```

por:

```
  assert.ok(t.flags[t.slot(t.count - 1)] & TFLAG.WALLJUMP, 'marca do wall-jump no tick do chute');
});

const FULL_FEEL = Object.freeze({ bob: 1, tilt: 1, dip: 1 });

test('pawn (3.5): a sensação mexe só a câmera — olho de verdade, estado, precisão e telemetria iguais sem ela', () => {
  const world = worldOf((b) => floor(b));
  const a = pawnOn(world);
  const b = pawnOn(world);
  const input = testInput();
  const cam = new THREE.PerspectiveCamera();
  let bobbed = 0;
  for (let i = 0; i < 160; i++) {
    input.move.y = 1;
    input.move.x = i < 80 ? 0 : 1;
    input.down.clear();
    if (i === 120) input.down.add('jump');
    a.tick(1 / 64, input, { tick: i });
    b.tick(1 / 64, input, { tick: i, feel: FULL_FEEL });
    assert.equal(b.eyeOffset, a.eyeOffset);
    assert.deepEqual(b.state.origin.toArray(), a.state.origin.toArray());
    assert.equal(b.inaccuracy.total, a.inaccuracy.total);
    b.updateCamera(cam, 1);
    bobbed = Math.max(bobbed, Math.abs(cam.position.y - (b.state.origin.y + b.eyeOffset)));
  }
  assert.ok(bobbed > 0.5, `a câmera balançou ${bobbed} u`);
  const ta = a.telemetry;
  const tb = b.telemetry;
  assert.deepEqual([...tb.speed], [...ta.speed]);
});

test('pawn (3.5): pouso de 420 u mergulha a câmera ~12 u; zera na hora morto, no noclip e no teleporte', () => {
  const world = worldOf((b) => floor(b));
  const pawn = pawnOn(world, [0, 420, 0]);
  const input = testInput();
  const cam = new THREE.PerspectiveCamera();
  let landed = -1;
  let low = 0;
  for (let i = 0; i < 120; i++) {
    pawn.tick(1 / 64, input, { tick: i, feel: FULL_FEEL });
    if (landed < 0 && pawn.env.events.some((e) => e.type === 'land')) landed = i;
    pawn.updateCamera(cam, 1);
    low = Math.min(low, cam.position.y - (pawn.state.origin.y + pawn.eyeOffset));
    if (landed >= 0 && i === landed + 2) {
      // Interpolação: no meio do quadro a câmera fica no meio do caminho entre os dois ticks (com a sensação).
      pawn.updateCamera(cam, 0);
      const y0 = cam.position.y;
      pawn.updateCamera(cam, 1);
      const y1 = cam.position.y;
      pawn.updateCamera(cam, 0.5);
      assert.ok(Math.abs(cam.position.y - (y0 + y1) / 2) < 1e-9 && y1 < y0, 'descendo no mergulho');
    }
  }
  assert.ok(landed > 0 && pawn.vitals.health === 100, 'queda do limite seguro: sem dano');
  assert.ok(low < -11.5 && low > -12.3, `mergulho ${low}`);
  // Teleporte: a câmera volta exata ao olho, sem resto da mola nem da interpolação.
  input.move.y = 1;
  for (let i = 0; i < 40; i++) pawn.tick(1 / 64, input, { tick: 300 + i, feel: FULL_FEEL });
  pawn.teleport(new THREE.Vector3(0, 0, 0));
  for (const alpha of [0, 0.5, 1]) {
    pawn.updateCamera(cam, alpha);
    assert.ok(Math.abs(cam.position.y - (pawn.state.origin.y + HULL.standEye)) < 1e-9, `teleporte, alpha ${alpha}`);
    assert.equal(cam.rotation.z, 0);
  }
  // Noclip: nada da sensação.
  for (let i = 0; i < 20; i++) pawn.tick(1 / 64, input, { tick: 400 + i, feel: FULL_FEEL, noclip: true });
  pawn.updateCamera(cam, 0.5);
  assert.equal(pawn.feel.y, 0);
  assert.equal(pawn.feel.roll, 0);
  // Morto: a câmera é a do morto (desce e tomba), sem balanço.
  for (let i = 0; i < 30; i++) pawn.tick(1 / 64, input, { tick: 500 + i, feel: FULL_FEEL });
  pawn.kill('kill');
  pawn.tick(1 / 64, input, { tick: 600, feel: FULL_FEEL });
  assert.deepEqual([pawn.feel.y, pawn.feel.side, pawn.feel.roll], [0, 0, 0]);
  assert.deepEqual([pawn.prevFeel.y, pawn.prevFeel.side, pawn.prevFeel.roll], [0, 0, 0]);
});

```

- [ ] **Passo 2: Rodar e ver falhar**

Run: `node --test tests/playerPawn.test.js`
Expected: FAIL — "pawn (3.5): a sensação mexe só a câmera…" e "pawn (3.5): pouso de 420 u mergulha a câmera ~12 u…" (o pawn ainda não tem a sensação).

- [ ] **Passo 3: A sensação no pawn e na câmera**

Em `src/player/playerPawn.js`, trocar:

```
// render interpola pés, altura do olho, o tombo da câmera do morto e o FOV da luneta entre os ticks e suaviza degraus e a
// troca de cápsula no ar. Em terceira pessoa (debug) a câmera recua atrás do jogador e se recolhe ao encostar em parede.
// Morto, o comando do tick fica vazio (o olhar continua livre); quem chama respawn() é o estado da partida.

```

por:

```
// render interpola pés, altura do olho, o tombo da câmera do morto e o FOV da luneta entre os ticks e suaviza degraus e a
// troca de cápsula no ar. A sensação da câmera (subfase 3.5: balanço, inclinação e mergulho, src/player/cameraFeel.js)
// anda no tick e também é interpolada; ela só desloca a câmera — o olho de verdade (eyeOffset) segue para o tiro, a
// precisão e os medidores — e zera na hora morto, no noclip e no teleporte. Em terceira pessoa (debug) a câmera recua
// atrás do jogador e se recolhe ao encostar em parede. Morto, o comando do tick fica vazio (o olhar continua livre);
// quem chama respawn() é o estado da partida.

```

Em `src/player/playerPawn.js`, trocar:

```
import { applyDamage, createVitals, killVitals, respawnVitals } from './vitals.js';

```

por:

```
import { applyDamage, createVitals, killVitals, respawnVitals } from './vitals.js';
import { createCameraFeel, resetCameraFeel, updateCameraFeel } from './cameraFeel.js';

```

Em `src/player/playerPawn.js`, trocar:

```
const US_SMOOTHING = 0.05;

```

por:

```
const US_SMOOTHING = 0.05;
/** Sensação da câmera desligada (quem não passa as escalas: testes, ferramentas). */
const NO_FEEL = Object.freeze({ bob: 0, tilt: 0, dip: 0 });

```

Em `src/player/playerPawn.js`, trocar:

```
    this.prevRoll = 0;
    this.lastLanding = null;
```

por:

```
    this.prevRoll = 0;
    // Sensação da câmera (3.5): o estado das molas e a saída do tick anterior (interpolada no quadro).
    this.feel = createCameraFeel();
    this.prevFeel = { y: 0, side: 0, roll: 0 };
    this.lastLanding = null;
```

Em `src/player/playerPawn.js`, trocar:

```
   * Um tick: lê a entrada (morto, o comando fica vazio), troca de item, move, atualiza precisão e luneta, suaviza a
   * câmera e publica os eventos. `god`: o cheat (sem dano); `reduceMotion`: a câmera do morto só desce, sem tombar.
   */
  tick(dt, input, { noclip = false, tick = 0, god = false, reduceMotion = false } = {}) {
    const s = this.state;
```

por:

```
   * Um tick: lê a entrada (morto, o comando fica vazio), troca de item, move, atualiza precisão e luneta, suaviza a
   * câmera, publica os eventos e anda a sensação da câmera. `god`: o cheat (sem dano); `reduceMotion`: a câmera do
   * morto só desce, sem tombar; `feel`: escalas {bob, tilt, dip} de 0 a 1 da sensação (seção "Conforto").
   */
  tick(dt, input, { noclip = false, tick = 0, god = false, reduceMotion = false, feel = NO_FEEL } = {}) {
    const s = this.state;
```

Em `src/player/playerPawn.js`, trocar:

```
    this.prevRoll = this.roll;
    this.god = god;
```

por:

```
    this.prevRoll = this.roll;
    const pf = this.prevFeel;
    pf.y = this.feel.y;
    pf.side = this.feel.side;
    pf.roll = this.feel.roll;
    this.god = god;
```

Em `src/player/playerPawn.js`, trocar:

```
    for (let i = 0; i < events.length; i++) this.#onEvent(events[i], tick);
    this.#record(cmd);
```

por:

```
    for (let i = 0; i < events.length; i++) this.#onEvent(events[i], tick);
    // Sensação da câmera depois dos eventos (o pouso de agora já mergulha); morto (inclusive quem morreu neste tick)
    // ou no noclip, zera na hora.
    if (v.alive && !noclip) updateCameraFeel(this.feel, s, events, this.yaw, feel, dt);
    else this.#clearFeel();
    this.#record(cmd);
```

Em `src/player/playerPawn.js`, trocar:

```

  /**
   * Câmera: pés, olho, tombo do morto e FOV da luneta interpolados entre ticks; rotação do olhar do último quadro
   * (resposta imediata).
   */
  updateCamera(camera, alpha) {
    camera.position.lerpVectors(this.prevOrigin, this.state.origin, alpha);
    camera.position.y += this.prevEyeOffset + (this.eyeOffset - this.prevEyeOffset) * alpha;
    camera.rotation.set(this.pitch, this.yaw, this.prevRoll + (this.roll - this.prevRoll) * alpha, 'YXZ');
    const zoom = this.fov.prev + (this.fov.now - this.fov.prev) * alpha;
```

por:

```

  /** Sensação da câmera zerada na hora (sem arrastar a interpolação do tick anterior). */
  #clearFeel() {
    resetCameraFeel(this.feel);
    const pf = this.prevFeel;
    pf.y = 0;
    pf.side = 0;
    pf.roll = 0;
  }

  /**
   * Câmera: pés, olho, tombo do morto, sensação (mergulho e balanço na vertical, balanço no eixo direito do olhar e a
   * rolagem) e FOV da luneta interpolados entre ticks; rotação do olhar do último quadro (resposta imediata).
   */
  updateCamera(camera, alpha) {
    const f = this.feel;
    const pf = this.prevFeel;
    const side = pf.side + (f.side - pf.side) * alpha;
    camera.position.lerpVectors(this.prevOrigin, this.state.origin, alpha);
    const eye = this.prevEyeOffset + (this.eyeOffset - this.prevEyeOffset) * alpha;
    camera.position.y += eye + pf.y + (f.y - pf.y) * alpha;
    camera.position.x += Math.cos(this.yaw) * side;
    camera.position.z -= Math.sin(this.yaw) * side;
    const roll = this.prevRoll + (this.roll - this.prevRoll) * alpha + pf.roll + (f.roll - pf.roll) * alpha;
    camera.rotation.set(this.pitch, this.yaw, roll, 'YXZ');
    const zoom = this.fov.prev + (this.fov.now - this.fov.prev) * alpha;
```

Em `src/player/playerPawn.js`, trocar:

```
  /**
   * Teleporte (setpos, estacao, respawn): interrompe o slide e o voo (paredes usadas zeradas), zera velocidade e
   * interpolação e procura o chão.
   */
```

por:

```
  /**
   * Teleporte (setpos, estacao, respawn): interrompe o slide e o voo (paredes usadas zeradas), zera velocidade,
   * interpolação e a sensação da câmera e procura o chão.
   */
```

Em `src/player/playerPawn.js`, trocar:

```
    this.prevEyeOffset = this.eyeOffset;
  }
```

por:

```
    this.prevEyeOffset = this.eyeOffset;
    this.#clearFeel();
  }
```

- [ ] **Passo 4: Os controles do Conforto**

Em `src/data/configSchema.js`, trocar:

```
import { PRESET_IDS } from './qualityPresets.js';
import { DEFAULT_TOUCH_BUTTONS, TOUCH_BUTTONS_SINCE, TOUCH_LAYOUT_VERSION, defaultTouchLayout } from './touchLayout.js';
```

por:

```
import { PRESET_IDS } from './qualityPresets.js';
import { CAMERA_FEEL_DEFAULT } from './cameraFeel.js';
import { DEFAULT_TOUCH_BUTTONS, TOUCH_BUTTONS_SINCE, TOUCH_LAYOUT_VERSION, defaultTouchLayout } from './touchLayout.js';
```

Em `src/data/configSchema.js`, trocar:

```
  // ---------------- Acessibilidade ----------------
  'accessibility.reduceMotion': {
    type: 'bool', default: false, label: 'Reduzir movimento (sem flicker/boil)', group: 'accessibility',
  },
```

por:

```
  // ---------------- Acessibilidade ----------------
  // Sensação da câmera (subfase 3.5, src/data/cameraFeel.js): % dos valores da referência; o padrão é o nível Médio.
  'accessibility.cameraBob': {
    type: 'number', min: 0, max: 100, step: 5, default: CAMERA_FEEL_DEFAULT.bob, label: 'Balanço da câmera ao andar',
    group: 'accessibility',
  },
  'accessibility.cameraTilt': {
    type: 'number', min: 0, max: 100, step: 5, default: CAMERA_FEEL_DEFAULT.tilt,
    label: 'Inclinação da câmera (de lado, slide e wall-jump)', group: 'accessibility',
  },
  'accessibility.cameraDip': {
    type: 'number', min: 0, max: 100, step: 5, default: CAMERA_FEEL_DEFAULT.dip, label: 'Mergulho da câmera no pouso',
    group: 'accessibility',
  },
  'accessibility.reduceMotion': {
    type: 'bool', default: false, label: 'Reduzir movimento (sem balanço, flicker nem boil)', group: 'accessibility',
  },
```

Em `src/ui/settingControls.js`, trocar:

```
  'graphics.particles': (v) => `${Math.round(v * 100)}%`,
});
```

por:

```
  'graphics.particles': (v) => `${Math.round(v * 100)}%`,
  'accessibility.cameraBob': (v) => `${v}%`,
  'accessibility.cameraTilt': (v) => `${v}%`,
  'accessibility.cameraDip': (v) => `${v}%`,
});
```

Em `src/ui/settingsScreen.js`, trocar:

```
});
const COMFORT_KEYS = ['accessibility.reduceMotion'];
const MOUSE_KEYS = ['controls.mouseSensitivity', 'controls.zoomSensitivity', 'controls.invertY', 'controls.rawInput'];
```

por:

```
});
// Conforto (subfase 3.5): a sensação da câmera acima do "Reduzir movimento", que zera as três.
const COMFORT_KEYS = [
  'accessibility.cameraBob', 'accessibility.cameraTilt', 'accessibility.cameraDip', 'accessibility.reduceMotion',
];
const COMFORT_HINTS = Object.freeze({
  'accessibility.cameraBob': 'sobe e desce no ritmo dos passos',
  'accessibility.cameraTilt': 'a cabeça pende para o lado; no wall-jump, para longe da parede',
  'accessibility.cameraDip': 'o olho afunda e volta ao pousar, pular e deslizar',
  'accessibility.reduceMotion': 'zera os três acima',
});
const MOUSE_KEYS = ['controls.mouseSensitivity', 'controls.zoomSensitivity', 'controls.invertY', 'controls.rawInput'];
```

Em `src/ui/settingsScreen.js`, trocar:

```
      section('Lente e luz de estúdio', ...POST_KEYS.map((k) => track(settingRow(config, k, { hint: POST_HINTS[k] ?? null })))),
      section('Conforto', ...COMFORT_KEYS.map((k) => track(settingRow(config, k)))),
    ];
```

por:

```
      section('Lente e luz de estúdio', ...POST_KEYS.map((k) => track(settingRow(config, k, { hint: POST_HINTS[k] ?? null })))),
      section('Conforto', ...COMFORT_KEYS.map((k) => track(settingRow(config, k, { hint: COMFORT_HINTS[k] })))),
    ];
```

- [ ] **Passo 5: As escalas no tick da partida** — "Reduzir movimento" zera as três; senão, cada chave ÷ 100.

Em `src/modes/matchState.js`, trocar:

```
// anda com a cápsula (PlayerPawn, Fase 3) e o inventário local; sem colisão (vitrine) voa com a câmera livre.
// Responsável por: montar/desmontar o mapa (sem vazar GPU), jogador e câmera, contexto de entrada, pointer lock,
// pausa, a vida no HUD de teste, a morte e a volta em 2 s (subfase 3.4: no ponto de volta — o último teleporte do
// console que se sustentou, senão o spawn —; cair do set mata, com god volta ao spawn), sensibilidade da luneta,
// trincos do andar, ferramentas de debug da física e do movimento (medidores de counter-strafe e de salto e queda), o
// teleporte das estações (`estacao`, pista de testes) e o resumo que vai para a tela de resultado.

```

por:

```
// anda com a cápsula (PlayerPawn, Fase 3) e o inventário local; sem colisão (vitrine) voa com a câmera livre.
// Responsável por: montar/desmontar o mapa (sem vazar GPU), jogador e câmera, contexto de entrada, pointer lock, pausa,
// a vida no HUD de teste, a morte e a volta em 2 s (subfase 3.4: no ponto de volta — o último teleporte do console que
// se sustentou, senão o spawn —; cair do set mata, com god volta ao spawn), sensibilidade da luneta, trincos do andar,
// ferramentas de debug da física e do movimento (medidores de counter-strafe e de salto e queda), o teleporte das
// estações (`estacao`, pista de testes), as escalas da sensação da câmera (subfase 3.5, seção "Conforto") e o resumo
// que vai para a tela de resultado.

```

Em `src/modes/matchState.js`, trocar:

```
    this.returnPoint = new ReturnPoint(); // ponto de volta: o último teleporte do console neste mapa (senão o spawn)
  }
```

por:

```
    this.returnPoint = new ReturnPoint(); // ponto de volta: o último teleporte do console neste mapa (senão o spawn)
    this._feel = { bob: 0, tilt: 0, dip: 0 }; // escalas da sensação da câmera do tick (0–1)
  }
```

Em `src/modes/matchState.js`, trocar:

```
      noclip: this.s.cheats.noclip, tick: tickIndex, god: this.s.cheats.god,
      reduceMotion: this.s.config.get('accessibility.reduceMotion'),
    });
```

por:

```
      noclip: this.s.cheats.noclip, tick: tickIndex, god: this.s.cheats.god,
      reduceMotion: this.s.config.get('accessibility.reduceMotion'), feel: this.#feelScales(),
    });
```

Em `src/modes/matchState.js`, trocar:

```
  }

  /**
   * Fora do set (noclip desligado lá fora, ou um buraco): bem abaixo do mapa o jogador morre ("Caiu do set"); com god,
```

por:

```
  }

  /** Escalas da sensação da câmera (0–1) pela seção "Conforto"; "Reduzir movimento" zera as três. */
  #feelScales() {
    const cfg = this.s.config;
    const off = cfg.get('accessibility.reduceMotion');
    const f = this._feel;
    f.bob = off ? 0 : cfg.get('accessibility.cameraBob') / 100;
    f.tilt = off ? 0 : cfg.get('accessibility.cameraTilt') / 100;
    f.dip = off ? 0 : cfg.get('accessibility.cameraDip') / 100;
    return f;
  }

  /**
   * Fora do set (noclip desligado lá fora, ou um buraco): bem abaixo do mapa o jogador morre ("Caiu do set"); com god,
```

- [ ] **Passo 6: Rodar os testes da tarefa**

Run: `node --test tests/playerPawn.test.js tests/core.test.js tests/input.test.js tests/post.test.js`
Expected: PASS — todos os testes dos quatro arquivos passando.

- [ ] **Passo 7: Suíte inteira**

Run: `npm test`
Expected: PASS — 269 testes passando.

- [ ] **Passo final: Commit** (só com o pedido do usuário)

```bash
git add src/player/playerPawn.js src/data/configSchema.js src/ui/settingControls.js src/ui/settingsScreen.js src/modes/matchState.js tests/playerPawn.test.js
git commit -m "MASSACRE 3.5: sensação da câmera no jogo e a seção Conforto" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Tarefa 3: O corpo — boneco de referência com botas e squash & stretch

**Files:**
- Create: `src/data/referenceDoll.js`, `src/data/footprints.js`, `src/clay/prints/sole.js`, `src/clay/kit/boots.js`, `src/characters/squashStretch.js`, `src/characters/playerBody.js`, `tests/squashStretch.test.js`
- Modify: `src/clay/kit/scaleMarker.js` (arquivo inteiro), `src/modes/matchState.js`

A bota é a sola das pegadas: `src/data/footprints.js` (a sola e, já com todos os números, as pegadas que a Tarefa 4 usa) e `src/clay/prints/sole.js` (a distância assinada ao contorno e os cravos, em JS e em GLSL gerado dos mesmos números — a Tarefa 5 desenha com ele). `clayBoot` extruda o contorno (bordas arredondadas) com as barras dos cravos por baixo e o acabamento do kit. O `scaleMarker` vira `referenceDoll`: corpo e cabeça 6% menores sobre as botas (a ±5,6 u, bico 6° para fora), a altura total continuando 72 u, uma malha por cor de massa; devolve o grupo, as botas, o resto do corpo e a altura do tornozelo (o `scaleMarker` de sempre é o grupo). A mola do corpo é pura e por tick (rigidez 260, amortecimento 13, solução exata): o tick do pulo e do wall-jump mostra −10% com o impulso que leva ao pico de +14% (o impulso sai de uma bisseção sobre o primeiro pico exato), caindo estica até 12% a 800 u/s, o pouso achata na hora 30% × o fator da queda da câmera, morto vai a −62%. O `PlayerBody` põe o boneco no mundo: a mola anda no tick, a forma (com o agachar, 72 → 54 u a partir do tornozelo), a virada e o alargamento das botas mudam só na troca de pose (`EV.POSE`), os pés seguem a posição interpolada a cada quadro; a sombra de contato (disco de borda macia numa textura procedural) fica no chão embaixo, alinhada à normal, encolhendo e clareando com a altura. Visível em terceira pessoa e no noclip; não projeta no mapa de sombra.

- [ ] **Passo 1: Escrever os testes**

```js file=tests/squashStretch.test.js
// Testes do corpo (subfase 3.5): volume constante; sequência do pulo e do wall-jump (−10% → +14%); estica caindo; o
// pouso achata na hora pelo fator (11%, 17%, 30%, 42%) e passa do normal na volta; limites; morte (−62%) e a volta;
// agachar (72 → 54 u como a cápsula); mola exata; o boneco de referência com botas (72 u, pivô no tornozelo, sola das
// pegadas) e o corpo no mundo (a forma só muda na troca de pose; visível em terceira pessoa e no noclip).
import { test } from 'node:test';
import assert from 'node:assert/strict';
import * as THREE from 'three';
import { FALL, HULL } from '../src/data/movement.js';
import { REFERENCE_DOLL } from '../src/data/referenceDoll.js';
import { SOLE } from '../src/data/footprints.js';
import {
  ANKLE, DUCK_DROP, JUMP_KICK, bodyShape, createSquash, resetSquash, updateSquash,
} from '../src/characters/squashStretch.js';
import { PlayerBody } from '../src/characters/playerBody.js';
import { clayBoot, cleatBars, soleOutline } from '../src/clay/kit/boots.js';
import { referenceDoll } from '../src/clay/kit/scaleMarker.js';
import { SOLE_EXTENT, soleDistance } from '../src/clay/prints/sole.js';
import { PlayerPawn } from '../src/player/playerPawn.js';
import { createMoveState } from '../src/player/movement.js';
import { createSvVars } from '../src/player/movementVars.js';
import { floor, worldOf } from './worldTestUtils.js';

const DT = 1 / 64;
const Q = REFERENCE_DOLL.squash;

/** Estado de movimento no chão ou no ar com a velocidade vertical dada. */
function moveState({ onGround = true, vy = 0 } = {}) {
  const s = createMoveState();
  s.onGround = onGround;
  s.velocity.y = vy;
  return s;
}

/** Roda a mola `ticks` ticks no estado `s`; eventos só no primeiro. Devolve os valores de x por tick. */
function springRun(sq, s, ticks, events = [], alive = true) {
  const xs = [];
  for (let i = 0; i < ticks; i++) {
    updateSquash(sq, s, i === 0 ? events : [], alive, DT);
    xs.push(sq.x);
  }
  return xs;
}

test('volume constante: altura × (1 + x), largura × 1/√(1 + x); botas alargam até 16%', () => {
  for (const x of [-0.45, -0.3, -0.1, 0, 0.12, 0.35]) {
    for (const duck of [0, 0.5, 1]) {
      const sh = bodyShape({ x, v: 0 }, duck);
      assert.ok(Math.abs(sh.sy * sh.sxz * sh.sxz - 1) < 1e-12, `x ${x}, agachar ${duck}`);
    }
  }
  assert.equal(bodyShape({ x: 0, v: 0 }, 0).widen, 0);
  assert.ok(Math.abs(bodyShape({ x: -0.3, v: 0 }, 0).widen - 0.105) < 1e-12);
  assert.equal(bodyShape({ x: -0.62, v: 0 }, 0).widen, REFERENCE_DOLL.bootWiden.max);
  assert.equal(bodyShape({ x: 0.2, v: 0 }, 0).widen, 0);
});

test('agachar: a altura acima do tornozelo cai junto com a cápsula (72 → 54 u)', () => {
  assert.ok(Math.abs(ANKLE - 72 * 0.06) < 1e-9);
  const top = (duck) => ANKLE + (HULL.standHeight - ANKLE) * bodyShape({ x: 0, v: 0 }, duck).sy;
  assert.ok(Math.abs(top(0) - HULL.standHeight) < 1e-9);
  assert.ok(Math.abs(top(1) - HULL.duckHeight) < 1e-9);
  assert.ok(DUCK_DROP > 0.26 && DUCK_DROP < 0.27, `queda por agachar ${DUCK_DROP}`);
});

test('pulo e wall-jump: o tick do evento mostra −10% e a mola estica até +14%', () => {
  for (const type of ['jump', 'walljump']) {
    const sq = createSquash();
    const xs = springRun(sq, moveState({ onGround: false, vy: 280 }), 40, [{ type }]);
    assert.equal(xs[0], Q.jumpStart, type);
    const peak = Math.max(...xs);
    assert.ok(peak > 0.138 && peak <= Q.jumpPeak + 1e-9, `${type}: pico ${peak}`);
    assert.ok(xs.indexOf(peak) >= 3 && xs.indexOf(peak) <= 8, `pico no tick ${xs.indexOf(peak)}`);
  }
  assert.ok(JUMP_KICK > 0);
});

test('caindo estica pela velocidade de queda (até 12% a 800 u/s); subindo não', () => {
  const settle = (vy) => springRun(createSquash(), moveState({ onGround: false, vy }), 128).at(-1);
  assert.ok(Math.abs(settle(-800) - Q.fall) < 1e-3, `a 800: ${settle(-800)}`);
  assert.ok(Math.abs(settle(-1600) - Q.fall) < 1e-3, 'acima de 800 não passa de 12%');
  assert.ok(Math.abs(settle(-400) - Q.fall / 2) < 1e-3, `a 400: ${settle(-400)}`);
  assert.ok(Math.abs(settle(300)) < 1e-3, 'subindo: normal');
});

test('pouso: achata na hora 30% × o fator da queda (11%, 17%, 30%, 42%) e volta passando do normal', () => {
  const cases = [[301.993377, 0.1105], [Math.sqrt(2 * 800 * 128), 0.1657], [FALL.safeSpeed, 0.3], [FALL.fatalSpeed, 0.42]];
  for (const [speed, want] of cases) {
    const sq = createSquash();
    const xs = springRun(sq, moveState(), 64, [{ type: 'land', speed }]);
    assert.ok(Math.abs(xs[0] + want) < 1e-3, `queda a ${speed}: ${xs[0]}`);
    assert.equal(Math.min(...xs), xs[0], 'a pose de contato é a mais achatada');
    const over = Math.max(...xs);
    assert.ok(over > want * 0.2 && over < want * 0.3, `passa do normal: ${over}`);
    assert.ok(Math.abs(xs.at(-1)) < want * 0.05, 'assenta em ~1 s');
  }
  // Pouso lento (abaixo de 150 u/s): nada muda na hora.
  const soft = createSquash();
  soft.x = 0.05;
  springRun(soft, moveState(), 1, [{ type: 'land', speed: 100 }]);
  assert.ok(soft.x > 0.04, 'pouso lento não achata');
});

test('limites (−45% e +35%), morte (−62%) e a volta ao jogo', () => {
  const sq = createSquash();
  sq.v = 100;
  updateSquash(sq, moveState(), [], true, DT);
  assert.equal(sq.x, Q.max);
  sq.x = 0;
  sq.v = -100;
  updateSquash(sq, moveState(), [], true, DT);
  assert.equal(sq.x, Q.min);
  const dead = createSquash();
  const xs = springRun(dead, moveState(), 128, [], false);
  assert.ok(Math.min(...xs) >= Q.dead - 1e-12, 'nunca abaixo do limite da morte');
  assert.ok(Math.abs(xs.at(-1) - Q.dead) < 1e-3, `morto: ${xs.at(-1)}`);
  const ignored = createSquash();
  springRun(ignored, moveState(), 1, [{ type: 'jump' }], false);
  assert.notEqual(ignored.x, Q.jumpStart, 'morto não pula');
  resetSquash(dead);
  assert.deepEqual(dead, createSquash());
});

test('mola exata: dois ticks de 1/64 s dão o mesmo que um de 1/32 s', () => {
  const a = createSquash();
  const b = createSquash();
  const s = moveState();
  updateSquash(a, s, [{ type: 'land', speed: 900 }], true, 0);
  updateSquash(b, s, [{ type: 'land', speed: 900 }], true, 0);
  for (let i = 0; i < 20; i++) {
    updateSquash(a, s, [], true, DT);
    updateSquash(a, s, [], true, DT);
    updateSquash(b, s, [], true, 2 * DT);
  }
  assert.ok(Math.abs(a.x - b.x) < 1e-9 && Math.abs(a.v - b.v) < 1e-9);
});

test('sola e botas: contorno de 15,8 × 7,8 u (16,4 sem o corte), bico desviado para dentro, cravos por baixo', () => {
  assert.ok(Math.abs(SOLE_EXTENT.nominalLength - 16.4) < 1e-9);
  assert.ok(Math.abs(SOLE_EXTENT.length - 15.8) < 1e-9);
  assert.equal(SOLE_EXTENT.width, 7.8);
  assert.ok(soleDistance(0, 0) < 0 && soleDistance(SOLE.cut + 0.01, 0) > 0 && soleDistance(-8.19, 0) < 0);
  // Bico para dentro: no bico, o lado de dentro (bi > 0) vai mais longe que o de fora.
  assert.ok(soleDistance(4.3, 4.1) < 0 && soleDistance(4.3, -4.1) > 0);
  const outline = soleOutline(0);
  const as = outline.map(([a]) => a);
  assert.ok(Math.abs(Math.min(...as) - SOLE_EXTENT.back) < 0.01 && Math.abs(Math.max(...as) - SOLE_EXTENT.front) < 0.01);
  assert.ok(outline.every(([a, bi]) => Math.abs(soleDistance(a, bi)) < 0.01), 'no contorno (cordas de ~0,1 u)');
  const bars = cleatBars();
  assert.equal(bars.filter((b) => b.a0 > -1.01).length, 4, 'quatro barras transversais na frente');
  assert.equal(bars.filter((b) => b.a1 <= -2.6 + 1e-9).length, 3, 'três barras ao comprido no calcanhar');
  for (const b of bars) assert.ok(soleDistance((b.a0 + b.a1) / 2, (b.b0 + b.b1) / 2) < 0);
  const left = clayBoot({ foot: 'left' });
  const right = clayBoot({ foot: 'right' });
  left.geometry.computeBoundingBox();
  right.geometry.computeBoundingBox();
  const L = left.geometry.boundingBox;
  const R = right.geometry.boundingBox;
  assert.ok(Math.abs(L.max.y - REFERENCE_DOLL.boots.height) < 0.1 && L.min.y > -0.1, `altura ${L.min.y}..${L.max.y}`);
  assert.ok(Math.abs(L.min.x + R.max.x) < 0.1 && Math.abs(L.max.x + R.min.x) < 0.1, 'pé esquerdo e direito espelhados');
  assert.ok(-L.min.x > L.max.x, 'lado de dentro do pé esquerdo em −X');
  assert.ok(left.distance(new THREE.Vector3(0, 2, 0)) < 0 && left.distance(new THREE.Vector3(0, 7, 0)) > 0);
  assert.ok(left.geometry.attributes.aTouch && left.geometry.attributes.aSeam);
});

test('boneco de referência: 72 u com as botas, corpo 6% menor sobre elas, uma malha por cor de massa', () => {
  const doll = referenceDoll(72, { seed: 'teste-boneco' });
  const box = new THREE.Box3().setFromObject(doll.group);
  assert.ok(box.max.y > 71 && box.max.y <= 72.2, `altura ${box.max.y}`);
  assert.ok(Math.abs(doll.ankle - 72 * (1 - REFERENCE_DOLL.bodyScale)) < 1e-9);
  assert.equal(doll.group.children.length, 4, 'corpo, olhos, pupilas e botas');
  assert.equal(doll.upper.length, 3);
  const boots = new THREE.Box3().setFromObject(doll.boots);
  assert.ok(boots.max.y < 5 && boots.min.x < -8 && boots.max.x > 8, 'as duas botas nos lados, até ~4,5 u');
  // Costura: o corpo ganhou sulco onde encosta nas botas.
  const body = doll.upper.find((m) => m.material.clay.color === REFERENCE_DOLL.boots.color) ?? doll.upper[0];
  const seam = body.geometry.attributes.aSeam.array;
  assert.ok(seam.some((v) => v > 0.2), 'costura no corpo');
});

test('corpo no mundo: a forma só muda na troca de pose; pés interpolados; visível em terceira pessoa e no noclip', () => {
  const scene = new THREE.Scene();
  const world = worldOf((b) => floor(b));
  const pawn = new PlayerPawn({ world, sv: createSvVars(), position: new THREE.Vector3(0, 0, 0) });
  const body = new PlayerBody({ scene, world, seed: 'teste-corpo' });
  const input = { move: { x: 0, y: 0 }, isDown: (a) => a === 'jump', pressed: () => false };
  body.onPose(pawn);
  const before = body.pivot.scale.toArray();
  pawn.tick(DT, input, { tick: 1 });
  body.tick(pawn, DT);
  assert.equal(body.squash.x, Q.jumpStart, 'a mola anda no tick');
  assert.deepEqual(body.pivot.scale.toArray(), before, 'sem pose, a forma não muda');
  body.onPose(pawn);
  assert.ok(body.pivot.scale.y < before[1] && body.pivot.scale.x > before[0], 'na pose, achata e alarga');
  assert.ok(Math.abs(body.pivot.scale.y * body.pivot.scale.x ** 2 - 1) < 1e-9);
  body.update(pawn, 0.5);
  assert.equal(body.root.visible, false, 'primeira pessoa: escondido');
  pawn.thirdPerson = true;
  body.update(pawn, 0.5);
  assert.ok(body.root.visible && body.shadow.visible);
  const mid = pawn.prevOrigin.clone().lerp(pawn.state.origin, 0.5);
  assert.ok(body.root.position.distanceTo(mid) < 1e-9);
  assert.ok(Math.abs(body.shadow.material.opacity - REFERENCE_DOLL.shadow.opacity) < 0.01, 'no chão: sombra cheia');
  assert.ok(Math.abs(body.root.rotation.y - (pawn.yaw + Math.PI)) < 1e-12);
  body.reset();
  assert.deepEqual(body.squash, createSquash());
  body.dispose();
  assert.equal(scene.children.length, 0);
});
```

- [ ] **Passo 2: Rodar e ver falhar**

Run: `node --test tests/squashStretch.test.js`
Expected: FAIL — o arquivo nem carrega: `ERR_MODULE_NOT_FOUND` (não acha `src/data/referenceDoll.js`).

- [ ] **Passo 3: Números do boneco e das pegadas**

```js file=src/data/referenceDoll.js
// Boneco de referência (subfase 3.5; desenho em docs/phases/phase-3.md, seção 3.5; referências no item 12 do
// moodboard): o boneco de escala da sala de testes e da vitrine e o corpo do jogador até a Fase 5 trazer os personagens
// (os bots da Fase 7 e os outros jogadores da Fase 9 também). Corpo em cápsula e cabeça de massinha sobre botas com
// cravos — a sola das pegadas (src/data/footprints.js). A mola do squash & stretch (src/characters/squashStretch.js)
// roda a 64 Hz e o corpo mostra o valor da pose (12 poses/s, "em dois"). Medidas para o boneco de 72 u (outras alturas
// escalam).

const F = Object.freeze;

export const REFERENCE_DOLL = F({
  height: 72,
  bodyScale: 0.94, // corpo e cabeça 6% menores, sobre as botas: a altura total continua 72 u
  boots: F({
    offset: 5.6, // u do centro do boneco ao centro de cada bota (PFT4: pés de massa de sola chata sob o boneco)
    toeOutDeg: 6, // bico para fora (CST16/CST19: bolotas com pezinhos; SFP1/SFP5: a trilha com o bico para fora)
    height: 4.5, // u: a subida da bota, dos cravos à borda de cima
    round: 1.2, // u: raio das bordas arredondadas (de cima e da sola)
    cleatHeight: 0.6, // u: os cravos em relevo embaixo
    cleatInset: 0.5, // u: os cravos param antes da borda da sola
    outline: 56, // pontos do contorno
    color: '#3B312B', // massa marrom-escura
  }),
  // Mola do corpo: passa ~25% e assenta em ~0,6 s (solução exata, por tick).
  spring: F({ stiffness: 260, damping: 13 }),
  // Squash & stretch com volume constante (SQS12, SQS17, SQS30): altura × (1 + x), largura × 1/√(1 + x).
  squash: F({
    jumpStart: -0.1, // saída do pulo e do wall-jump: começa achatado (SQS7, SQS11, SQS14, SQS19: antecipação)...
    jumpPeak: 0.14, // ...com o impulso que leva ao pico de esticada
    fall: 0.12, // caindo: estica até 12% × mín(1, queda ÷ fallSpeed) (SQS4, SQS24, BBR33)
    fallSpeed: 800,
    // Pouso: achata na hora 30% × o fator da queda da câmera (BBR7, BBR8, BBR22: a pose de contato é a mais achatada).
    land: 0.3,
    min: -0.45,
    max: 0.35,
    dead: -0.62, // morto: achata e alarga como massa caindo na mesa (a morte da seção 0.12)
  }),
  bootWiden: F({ gain: 0.35, max: 0.16 }), // as botas alargam 0,35 × o achatado, até 16%
  // Sombra de contato (BBR32: a sombra embaixo diz a altura): disco de borda macia no chão embaixo do boneco.
  shadow: F({
    diameter: 30, opacity: 0.4, // no chão
    fadeHeight: 300, minScale: 0.55, minOpacity: 0.35, // a 300 u de altura: 55% do tamanho e 35% da opacidade
    lift: 0.25, // u acima do chão
    probe: 2000, // u de busca do chão para baixo
    texture: 64, // px da textura do disco
  }),
});
```

```js file=src/data/footprints.js
// Pegadas na massinha (subfase 3.5; desenho em docs/phases/phase-3.md, seção 3.5; referências no item 12 do moodboard):
// a sola da bota com cravos (a mesma dos pés do boneco de referência, src/clay/kit/boots.js), a forma da marca (fundo
// pelos cravos, parede, lábio de massa empurrada, brilho de massa fresca), as marcas de cada evento do movimento, o
// mapa de pegadas de cada peça de chão de massinha e o esmaecimento. Unidades do jogo (u). A sola é descrita no
// referencial do pé: `a` ao longo do pé (positivo para o bico) e `bi` para o lado de dentro (o do dedão): pé esquerdo e
// direito são espelhos. Canais do mapa: R = fundo (0–1 × `depth`), G = lábio (0–1 × `lip`), B = massa fresca (0/1).

const F = Object.freeze;

/**
 * Sola da bota com cravos (FIM22: sola de cravos na lama; SFP20: o contorno do sapato transferido): calcanhar e bico
 * circulares ligados por tangentes, o bico cortado reto e desviado para dentro. 16,4 × 7,8 u de calcanhar a bico
 * (15,8 u com o bico cortado).
 */
export const SOLE = F({
  heel: F({ a: -5.0, radius: 3.2 }),
  toe: F({ a: 4.3, radius: 3.9 }),
  cut: 7.6, // bico cortado reto em a = +7,6
  inward: 0.3, // o bico desvia 0,3 u para o lado de dentro
  // Cravos (fundo relativo da marca: 1 nas barras): na frente, barras transversais em 55% de cada 1,8 u; no calcanhar,
  // barras ao comprido em metade de cada 1,6 u; o arco liso. `phase` (u) põe a borda das barras em (n · passo − phase).
  cleats: F({
    front: F({ from: -1, pitch: 1.8, duty: 0.55, gap: 0.74 }),
    heel: F({ to: -2.6, pitch: 1.6, duty: 0.5, gap: 0.78 }),
    arch: 0.58,
    phase: 20,
  }),
});

/** Forma da marca, mapa por peça, marcas dos eventos e esmaecimento. */
export const FOOTPRINTS = F({
  depth: 4, // u de fundo no R = 1 (o par do pouso)
  lip: 0.8, // u de lábio no G = 1
  wall: 1.1, // u: a parede da marca, da borda ao fundo (FIM10/FIM21: parede íngreme e borda nítida)
  // Lábio de massa empurrada fora da borda: gaussiana a `offset` u da borda com largura `width`, 60% mais alta na
  // frente (de a = 0 a a = 6, SFP6/FIM25: o impulso empurra a massa para a frente), na proporção da força da marca e
  // nunca acima do fundo máximo dela (a marca some inteira junto com a parte mais funda).
  lipRing: F({ offset: 0.9, width: 0.85, front: 0.6, frontFrom: 0, frontTo: 6, gain: 1 / 1.2 }),
  freshReach: 2.4, // u além da borda com brilho de massa fresca (FIM6/FIM7: o fundo molhado brilha mais)
  footReach: 13, // u: meia largura do retângulo de uma marca de pé (sola, lábio e brilho)
  // Mapa de pegadas por peça (o XZ do objeto, centrado): texels por u e o teto por lado (peça maior perde densidade).
  texelsPerUnit: 4,
  maxTexels: 1024,
  topTolerance: 4, // u: a peça recebe a marca se o topo dela está a até isto dos pés
  marks: F({
    // Passo: o pé do evento a ±offset do centro, virado para onde o jogador olha, bico para fora (SFP1/SFP5).
    step: F({ offset: 5.6, toeOutDeg: 6, strength: 0.75 }),
    // Pouso: o par lado a lado (FIM13/FIM24/FIM29); abaixo de `minFall` u/s de queda (descer meio degrau) não marca,
    // como a câmera e o corpo não reagem (src/data/cameraFeel.js, dip.minFall).
    land: F({ offset: 6.2, toeOutDeg: 8, strength: 1, minFall: 150 }),
    // Saída do pulo: o par com a frente mais funda e o calcanhar raso (o impulso), do calcanhar ao bico.
    jump: F({ offset: 6.2, toeOutDeg: 8, strength: 0.83, heel: 0.5, front: 1.3 }),
    // Slide: dois sulcos de calcanhar a ±offset da trajetória (um segmento por tick) e, no fim, um montinho de massa
    // empurrada `moundAhead` u à frente dos pés (só lábio, da força dos sulcos: some junto com eles).
    slide: F({ offset: 5.6, halfWidth: 1.5, strength: 0.5, moundRadius: 4, moundAhead: 8 }),
  }),
  // Esmaecimento: `rate` passos por segundo de simulação (um a cada 1/12 s, o ritmo das poses; a pausa congela); cada
  // passo tira 1/255 do fundo e do lábio e 3/255 do brilho (SFP17: as marcas somem com o tempo; SFP30: sobram as partes
  // mais fundas). O par do pouso some em 21,25 s, o passo em ~16 s, o sulco do slide em ~11 s e o brilho em 7,1 s.
  fade: F({ rate: 12, depth: 1, lip: 1, fresh: 3 }),
});
```

- [ ] **Passo 4: A sola**

```js file=src/clay/prints/sole.js
// Sola da bota com cravos (subfase 3.5; números em src/data/footprints.js): a distância assinada ao contorno da sola e
// o fundo relativo dos cravos, em JS e em GLSL gerado dos mesmos números (o mapa de pegadas é desenhado na GPU e
// conferido texel a texel com o JS). Referencial do pé: `a` ao longo do pé (positivo para o bico) e `bi` para o lado de
// dentro (o do dedão) — pé esquerdo e direito são espelhos. As botas do boneco de referência (src/clay/kit/boots.js)
// são moldadas no mesmo contorno. Contorno: "cápsula desigual" entre o círculo do calcanhar e o do bico (tangentes
// externas; a do bico desvia para dentro ao longo do pé), cortada reta na ponta.

import { SOLE } from '../../data/footprints.js';

const H = SOLE.heel;
const T = SOLE.toe;
const LEN = T.a - H.a;
const K0 = (H.radius - T.radius) / LEN;
const K1 = Math.sqrt(1 - K0 * K0);
const C = SOLE.cleats;

const clamp01 = (v) => (v < 0 ? 0 : v > 1 ? 1 : v);

/** smoothstep do GLSL (e0 < e1). */
export function smoothstep(e0, e1, x) {
  const t = clamp01((x - e0) / (e1 - e0));
  return t * t * (3 - 2 * t);
}

const fract = (v) => v - Math.floor(v);

/** Distância assinada (u) de (a, bi) ao contorno da sola: negativa dentro. */
export function soleDistance(a, bi) {
  const px = Math.abs(bi - SOLE.inward * smoothstep(H.a, T.a, a));
  const py = a - H.a;
  const k = -K0 * px + K1 * py;
  let d;
  if (k < 0) d = Math.hypot(px, py) - H.radius;
  else if (k > K1 * LEN) d = Math.hypot(px, py - LEN) - T.radius;
  else d = K1 * px + K0 * py - H.radius;
  return Math.max(d, a - SOLE.cut);
}

/** Fundo relativo da marca pelos cravos em (a, bi): 1 nas barras, `gap` entre elas, `arch` no arco. */
export function soleCleats(a, bi) {
  if (a > C.front.from) return fract((a + C.phase) / C.front.pitch) < C.front.duty ? 1 : C.front.gap;
  if (a < C.heel.to) return fract((bi + C.phase) / C.heel.pitch) < C.heel.duty ? 1 : C.heel.gap;
  return C.arch;
}

/** Limites da sola no referencial do pé: calcanhar, ponta (o corte) e meia largura (o bico). */
export const SOLE_EXTENT = Object.freeze({
  back: H.a - H.radius,
  front: SOLE.cut,
  half: Math.max(H.radius, T.radius) + SOLE.inward,
  length: SOLE.cut - (H.a - H.radius),
  width: 2 * Math.max(H.radius, T.radius),
  nominalLength: T.a + T.radius - (H.a - H.radius),
});

/** Número JS como literal float do GLSL (os shaders das pegadas saem dos mesmos números do JS). */
export function glslFloat(v) {
  const s = String(v);
  return s.includes('.') || s.includes('e') ? s : `${s}.0`;
}

const f = glslFloat;

/** GLSL das mesmas funções: `float soleDistance(vec2 p)` e `float soleCleats(vec2 p)` com p = (a, bi). */
export const SOLE_GLSL = /* glsl */ `
float soleDistance(vec2 p) {
  float px = abs(p.y - ${f(SOLE.inward)} * smoothstep(${f(H.a)}, ${f(T.a)}, p.x));
  float py = p.x - (${f(H.a)});
  float k = ${f(-K0)} * px + ${f(K1)} * py;
  float d;
  if (k < 0.0) d = length(vec2(px, py)) - ${f(H.radius)};
  else if (k > ${f(K1 * LEN)}) d = length(vec2(px, py - ${f(LEN)})) - ${f(T.radius)};
  else d = ${f(K1)} * px + ${f(K0)} * py - ${f(H.radius)};
  return max(d, p.x - ${f(SOLE.cut)});
}
float soleCleats(vec2 p) {
  if (p.x > ${f(C.front.from)}) {
    return fract((p.x + ${f(C.phase)}) / ${f(C.front.pitch)}) < ${f(C.front.duty)} ? 1.0 : ${f(C.front.gap)};
  }
  if (p.x < ${f(C.heel.to)}) {
    return fract((p.y + ${f(C.phase)}) / ${f(C.heel.pitch)}) < ${f(C.heel.duty)} ? 1.0 : ${f(C.heel.gap)};
  }
  return ${f(C.arch)};
}
`;
```

- [ ] **Passo 5: As botas e o boneco de referência** (o `scaleMarker` inteiro).

```js file=src/clay/kit/boots.js
// Bota de massinha com cravos (subfase 3.5; números em src/data/referenceDoll.js; referências no item 12 do moodboard:
// PFT4 pés de massa de sola chata, AAC1/AAC6 botas escuras de bico redondo, FIM22 sola de cravos). O contorno é a sola
// das pegadas (src/clay/prints/sole.js): a bota pisa na massa e deixa a marca da própria sola. Extrusão do contorno com
// as bordas de cima e da sola arredondadas, cravos em relevo embaixo (barras transversais na frente, ao comprido no
// calcanhar, arco liso) e o acabamento do kit (calombos, aTouch, aSeam para a costura com o corpo). Referencial da
// peça: +Z para o bico, Y para cima (sola dos cravos em y = 0), X para o lado — o lado de dentro é −X no pé esquerdo
// (que fica em +X no boneco) e +X no direito.

import * as THREE from 'three';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';
import { SOLE } from '../../data/footprints.js';
import { REFERENCE_DOLL } from '../../data/referenceDoll.js';
import { SOLE_EXTENT, smoothstep, soleDistance } from '../prints/sole.js';
import { finalizeClayGeometry, sculpt, weld } from './sculpt.js';

const B = REFERENCE_DOLL.boots;
const C = SOLE.cleats;

/** Ponto (a, bi) do raio que sai de (ca, cb) na direção (da, db) onde a distância à sola vale −inset (bisseção). */
function isoPoint(ca, cb, da, db, inset) {
  let lo = 0;
  let hi = SOLE_EXTENT.length;
  for (let i = 0; i < 48; i++) {
    const t = (lo + hi) / 2;
    if (soleDistance(ca + da * t, cb + db * t) + inset < 0) lo = t;
    else hi = t;
  }
  const t = (lo + hi) / 2;
  return [ca + da * t, cb + db * t];
}

/**
 * Contorno da sola recuado `inset` u, com `n` pontos igualmente espaçados ao longo dele, em (a, bi), no sentido de a
 * para bi (anti-horário no plano a × bi). O contorno é estrelado a partir do meio do pé: raios dali o cruzam uma vez.
 */
export function soleOutline(inset = 0, n = B.outline) {
  const ca = (SOLE.heel.a + SOLE.toe.a) / 2;
  const cb = SOLE.inward / 2;
  const m = n * 8;
  const dense = [];
  for (let i = 0; i < m; i++) {
    const th = (i / m) * Math.PI * 2;
    dense.push(isoPoint(ca, cb, Math.cos(th), Math.sin(th), inset));
  }
  const cum = [0];
  for (let i = 1; i <= m; i++) {
    const p = dense[i % m];
    const q = dense[i - 1];
    cum.push(cum[i - 1] + Math.hypot(p[0] - q[0], p[1] - q[1]));
  }
  const out = [];
  let j = 0;
  for (let k = 0; k < n; k++) {
    const s = (k / n) * cum[m];
    while (cum[j + 1] < s) j++;
    const t = (s - cum[j]) / (cum[j + 1] - cum[j]);
    const p = dense[j];
    const q = dense[(j + 1) % m];
    out.push([p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t]);
  }
  return out;
}

/** Trecho [lo, hi] de uma reta dentro da sola recuada `inset`: `at(t)` → (a, bi); bisseção a partir de `mid`. */
function span(at, mid, reach, inset) {
  const inside = (t) => {
    const [a, bi] = at(t);
    return soleDistance(a, bi) + inset < 0;
  };
  if (!inside(mid)) return null;
  const edge = (dir) => {
    let lo = 0;
    let hi = reach;
    for (let i = 0; i < 40; i++) {
      const t = (lo + hi) / 2;
      if (inside(mid + dir * t)) lo = t;
      else hi = t;
    }
    return mid + dir * lo;
  };
  return [edge(-1), edge(1)];
}

/**
 * Barras dos cravos em (a, bi): retângulos {a0, a1, b0, b1} dentro da sola recuada `inset` — na frente, faixas de a
 * (de `front.from` ao corte) com a largura da sola; no calcanhar, faixas de bi (até `heel.to`). Os mesmos intervalos do
 * fundo das pegadas (soleCleats).
 */
export function cleatBars(inset = B.cleatInset) {
  const bars = [];
  const minLength = 0.6;
  const fp = C.front.pitch;
  for (let n = Math.floor((C.front.from + C.phase) / fp); n * fp - C.phase < SOLE.cut; n++) {
    const a0 = Math.max(n * fp - C.phase, C.front.from);
    const a1 = Math.min(n * fp - C.phase + C.front.duty * fp, SOLE.cut - inset);
    if (a1 - a0 < 0.3) continue;
    const am = (a0 + a1) / 2;
    const centre = SOLE.inward * smoothstep(SOLE.heel.a, SOLE.toe.a, am);
    const s = span((t) => [am, t], centre, SOLE_EXTENT.half + 1, inset);
    if (s && s[1] - s[0] >= minLength) bars.push({ a0, a1, b0: s[0], b1: s[1] });
  }
  const hp = C.heel.pitch;
  for (let n = Math.floor((-SOLE_EXTENT.half + C.phase) / hp); n * hp - C.phase < SOLE_EXTENT.half; n++) {
    const b0 = n * hp - C.phase;
    const b1 = b0 + C.heel.duty * hp;
    const bm = (b0 + b1) / 2;
    const s = span((t) => [t, bm], SOLE.heel.a, SOLE_EXTENT.length, inset);
    if (!s) continue;
    const a1 = Math.min(s[1], C.heel.to);
    if (a1 - s[0] >= minLength) bars.push({ a0: s[0], a1, b0, b1 });
  }
  return bars;
}

/**
 * Bota de massinha. `foot`: 'left' ou 'right'; `scale`: altura do boneco ÷ 72. Devolve { geometry, radius, distance }
 * como as primitivas do kit (distance: SDF aproximado no espaço da peça, para a costura com o corpo).
 */
export function clayBoot({ foot = 'left', scale = 1, seed = 17 } = {}) {
  const side = foot === 'left' ? -1 : 1; // x = side × bi
  const round = B.round;
  const shell = B.height - B.cleatHeight;
  // Casco: o contorno recuado do raio das bordas, extrudado com bisel redondo (o bisel devolve o contorno inteiro).
  const shape = new THREE.Shape(soleOutline(round).map(([a, bi]) => new THREE.Vector2(side * bi, -a)));
  const hull = new THREE.ExtrudeGeometry(shape, {
    depth: Math.max(0.1, shell - 2 * round), steps: 2, bevelEnabled: true, bevelThickness: round, bevelSize: round,
    bevelSegments: 3, curveSegments: 1,
  });
  hull.rotateX(-Math.PI / 2); // (x, −a, z) → (x, z, a): extrusão para cima, bico em +Z
  hull.translate(0, B.cleatHeight + round, 0);
  const parts = [hull]; // a extrusão e as barras saem sem índice (mergeGeometries pede o mesmo formato)
  // Cravos: barras de canto arredondado embaixo da sola, entrando um pouco no casco.
  const h = B.cleatHeight + 0.15;
  for (const bar of cleatBars()) {
    const w = bar.b1 - bar.b0;
    const l = bar.a1 - bar.a0;
    const g = new RoundedBoxGeometry(w, h, l, 2, Math.min(0.2, w / 2 - 0.01, l / 2 - 0.01));
    g.translate(side * (bar.b0 + bar.b1) / 2, h / 2, (bar.a0 + bar.a1) / 2);
    parts.push(g);
  }
  const merged = mergeGeometries(parts, false);
  for (const p of parts) p.dispose();
  if (!merged) throw new Error('não foi possível fundir a bota');
  if (scale !== 1) merged.scale(scale, scale, scale);
  const radius = Math.hypot(SOLE_EXTENT.length / 2 + 0.4, B.height) * scale;
  const geometry = finalizeClayGeometry(sculpt(weld(merged), {
    seed, radius, lumpiness: 0.012, lumpFreq: 1.1, dents: 1, dentDepth: 0.02, dentRadius: 0.25,
  }));
  const H = B.height * scale;
  return {
    geometry,
    radius,
    // Extrusão da sola (o contorno no plano, de y = 0 a y = H).
    distance: (p) => {
      const d2 = soleDistance(p.z / scale, (side * p.x) / scale) * scale;
      const dy = Math.max(-p.y, p.y - H);
      return Math.hypot(Math.max(d2, 0), Math.max(dy, 0)) + Math.min(Math.max(d2, dy), 0);
    },
  };
}
```

```js file=src/clay/kit/scaleMarker.js
// Boneco de referência de massinha com a altura do jogador (72 u = a medida do mundo): corpo em cápsula, cabeça e olhos
// de massinha com pupila sobre botas com cravos (subfase 3.5: a sola das pegadas; corpo e cabeça 6% menores, sobre as
// botas, para a altura total continuar a mesma). Usado na sala de testes e na vitrine para conferir a escala de tudo em
// volta (PLA2/PLA14: a mesa e os objetos do dia a dia provam o tamanho do boneco) e como o corpo do jogador até a
// Fase 5 (src/characters/playerBody.js). Números em src/data/referenceDoll.js; referências no item 12 do moodboard
// (PFT4 pés de massa sob o boneco, CST16/CST19 bolotas com pezinhos).

import { PALETTE } from '../../data/palette.js';
import { REFERENCE_DOLL } from '../../data/referenceDoll.js';
import { ClayMaterial } from '../ClayMaterial.js';
import { ClayAssembly } from './assembly.js';
import { clayBoot } from './boots.js';
import { clayBall, clayCapsule } from './shapes.js';

const DEG = Math.PI / 180;

/**
 * O boneco com as partes separadas, para quem anima (o corpo do jogador): `group` pronto para a cena (uma malha por cor
 * de massa, costuradas onde se encostam), `boots` (a malha das duas botas), `upper` (as malhas do corpo, da cabeça e
 * dos olhos) e `ankle` (a altura onde o corpo encosta nas botas: o pivô do squash & stretch).
 * @param {number} height altura total (u)
 * @param {{color?:string, seed?:string}} [opts]
 */
export function referenceDoll(height, { color = PALETTE.terracotta, seed = 'marcador' } = {}) {
  const D = REFERENCE_DOLL;
  const body = new ClayMaterial({ color, touched: true, wetness: 0.3, seed: `${seed}-corpo` });
  const white = new ClayMaterial({ color: PALETTE.clayWhite, touched: true, wetness: 0.45, seed: `${seed}-olho` });
  const black = new ClayMaterial({ color: '#1E1A18', touched: true, wetness: 0.6, roughness: 0.55, seed: `${seed}-pupila` });
  const bootClay = new ClayMaterial({
    color: D.boots.color, touched: true, wetness: 0.25, roughness: 0.66, seed: `${seed}-botas`,
  });
  const scale = height / D.height;
  const ankle = height * (1 - D.bodyScale);
  const up = height * D.bodyScale; // corpo e cabeça
  const headR = up * 0.14;
  const bodyR = up * 0.21;
  const bodyTop = up - headR * 1.6;
  const bodyLen = Math.max(4, bodyTop - bodyR * 2);
  const headY = ankle + up - headR;
  const eyeR = headR * 0.26;
  const eyeZ = headR * 0.84;
  const asm = new ClayAssembly(`${seed}-escala-${height}u`);
  asm.add(clayCapsule({ radius: bodyR, length: bodyLen, seed: 11 }), {
    material: body, position: [0, ankle + bodyR + bodyLen / 2, 0],
  });
  asm.add(clayBall({ radius: headR, squash: [1, 0.94, 1], seed: 12 }), { material: body, position: [0, headY, 0] });
  for (const side of [-1, 1]) {
    asm.add(clayBall({ radius: eyeR, segments: 8, lumpiness: 0.03, dents: 1, seed: 13 + side }), {
      material: white, position: [side * headR * 0.36, headY + headR * 0.08, eyeZ],
    });
    asm.add(clayBall({ radius: eyeR * 0.45, segments: 6, lumpiness: 0.02, dents: 0, seed: 15 + side }), {
      material: black, position: [side * headR * 0.34, headY + headR * 0.1, eyeZ + eyeR * 0.72], seams: false,
    });
  }
  // Botas: o boneco olha para +Z; o pé esquerdo fica em +X, com o bico virado para fora.
  for (const foot of ['left', 'right']) {
    const side = foot === 'left' ? 1 : -1;
    asm.add(clayBoot({ foot, scale, seed: 18 + side }), {
      material: bootClay, position: [side * D.boots.offset * scale, 0, 0],
      rotation: [0, side * D.boots.toeOutDeg * DEG, 0], name: `bota-${foot}`,
    });
  }
  const group = asm.build();
  const boots = group.children.find((m) => m.material === bootClay);
  const upper = group.children.filter((m) => m !== boots);
  return { group, boots, upper, ankle };
}

/**
 * Boneco de escala (sala de testes, vitrine).
 * @param {number} height altura total (u)
 * @param {{color?:string, seed?:string}} [opts]
 * @returns {import('three').Group}
 */
export function scaleMarker(height, opts = {}) {
  return referenceDoll(height, opts).group;
}
```

- [ ] **Passo 6: A mola do corpo e o corpo no mundo**

```js file=src/characters/squashStretch.js
// Squash & stretch do corpo (subfase 3.5; números em src/data/referenceDoll.js; referências no item 12 do moodboard):
// uma mola de um escalar x (0 = normal; negativo achata, positivo estica), pura, por tick, pela solução exata. O corpo
// mostra o valor da pose (12 poses/s, src/characters/playerBody.js), com volume constante: altura × (1 + x) e largura ×
// 1/√(1 + x) (SQS12, SQS17, SQS30). Agachar e slide baixam a altura junto com a cápsula (72 → 54 u).
//  - Saída do pulo e do wall-jump: começa achatado (antecipação) com o impulso que leva ao pico de esticada (SQS7,
//    SQS11, SQS14, SQS19).
//  - No ar, caindo: estica pela velocidade de queda (SQS4, SQS24, BBR33).
//  - Pouso: achata na hora pelo fator da queda da câmera (a pose de contato é a mais achatada: BBR7, BBR8, BBR22) e
//    volta passando do normal (SQS7).
//  - Morto: achata e alarga como massa caindo na mesa; a volta ao jogo zera. A Fase 5 reaproveita a mola nas mortes dos
//    personagens.

import { HULL } from '../data/movement.js';
import { REFERENCE_DOLL } from '../data/referenceDoll.js';
import { landFactor } from '../player/cameraFeel.js';

const D = REFERENCE_DOLL;
const Q = D.squash;
const K = D.spring.stiffness;
const A = D.spring.damping / 2;
const WD = Math.sqrt(K - A * A);

/** Um passo exato da mola rumo a `target` (dt qualquer). */
function stepSpring(sq, target, dt) {
  const e = Math.exp(-A * dt);
  const c = Math.cos(WD * dt);
  const s = Math.sin(WD * dt);
  const x = sq.x - target;
  const v = sq.v;
  sq.x = target + e * (x * c + ((v + A * x) / WD) * s);
  sq.v = e * (v * c - ((A * v + K * x) / WD) * s);
}

/** Primeiro máximo de x(t) (a mola livre rumo a 0) partindo de x0 < 0 com velocidade v0 > 0. */
function firstPeak(x0, v0) {
  // Velocidade zero quando tan(ωt) = v0·ω / (A·v0 + K·x0); o primeiro instante positivo.
  const t = Math.atan2(v0 * WD, A * v0 + K * x0) / WD;
  return Math.exp(-A * t) * (x0 * Math.cos(WD * t) + ((v0 + A * x0) / WD) * Math.sin(WD * t));
}

/** Impulso da saída do pulo: a velocidade que leva de `jumpStart` ao pico `jumpPeak` (bisseção sobre o pico exato). */
function jumpKick() {
  let lo = 0;
  let hi = 100;
  for (let i = 0; i < 80; i++) {
    const v = (lo + hi) / 2;
    if (firstPeak(Q.jumpStart, v) > Q.jumpPeak) hi = v;
    else lo = v;
  }
  return (lo + hi) / 2;
}

export const JUMP_KICK = jumpKick();

/** Altura do pivô (tornozelo) e quanto a altura cai por unidade de agachar: 72 → 54 u acima do chão, como a cápsula. */
export const ANKLE = D.height * (1 - D.bodyScale);
export const DUCK_DROP = 1 - (HULL.duckHeight - ANKLE) / (HULL.standHeight - ANKLE);

/** Estado da mola (dados simples). */
export function createSquash() {
  return { x: 0, v: 0 };
}

export function resetSquash(sq) {
  sq.x = 0;
  sq.v = 0;
  return sq;
}

/**
 * Um tick. `s`: estado de movimento depois do playerMove; `events`: os do tick (jump, walljump, land {speed});
 * `alive`: morto, a mola vai para o achatado da morte. A mola anda primeiro e os eventos marcam o tick deles: o tick do
 * pulo mostra o achatado de partida e o do pouso, o achatado inteiro.
 */
export function updateSquash(sq, s, events, alive, dt) {
  let target = 0;
  if (!alive) target = Q.dead;
  else if (!s.onGround && s.velocity.y < 0) target = Q.fall * Math.min(1, -s.velocity.y / Q.fallSpeed);
  stepSpring(sq, target, dt);
  if (alive) {
    for (let i = 0; i < events.length; i++) {
      const e = events[i];
      if (e.type === 'jump' || e.type === 'walljump') {
        sq.x = Q.jumpStart;
        sq.v = JUMP_KICK;
      } else if (e.type === 'land') {
        const k = landFactor(e.speed);
        if (k > 0) {
          sq.x = Math.min(sq.x, -Q.land * k);
          sq.v = 0;
        }
      }
    }
  }
  const lo = alive ? Q.min : Q.dead;
  if (sq.x < lo) {
    sq.x = lo;
    if (sq.v < 0) sq.v = 0;
  } else if (sq.x > Q.max) {
    sq.x = Q.max;
    if (sq.v > 0) sq.v = 0;
  }
  return sq;
}

/**
 * Forma do corpo para a mola `sq` e o quanto agachou (0–1): `sy` (altura, acima do tornozelo), `sxz` (largura, volume
 * constante) e `widen` (as botas alargam no achatado).
 */
export function bodyShape(sq, duckAmount, out = { sy: 1, sxz: 1, widen: 0 }) {
  const sy = (1 + sq.x) * (1 - DUCK_DROP * duckAmount);
  out.sy = sy;
  out.sxz = 1 / Math.sqrt(sy);
  out.widen = Math.min(D.bootWiden.max, Math.max(0, -sq.x) * D.bootWiden.gain);
  return out;
}
```

```js file=src/characters/playerBody.js
// Corpo do jogador no mundo (subfase 3.5; desenho em docs/phases/phase-3.md, seção 3.5): o boneco de referência de
// botas (src/clay/kit/scaleMarker.js) com o squash & stretch (src/characters/squashStretch.js) e a sombra de contato. A
// mola anda por tick (64 Hz); a forma (mola e agachar), a virada (o yaw do olhar) e o alargamento das botas ficam
// congelados a cada pose (EV.POSE, 12/s, "em dois"), enquanto a posição acompanha os pés interpolados a cada quadro (dá
// para mirar nele). Pivô no tornozelo: as botas ficam plantadas e o corpo achata e estica em cima delas. Visível em
// terceira pessoa (debug) e no noclip, como a cápsula do r_colisao; escondido em primeira pessoa. Não projeta sombra no
// mapa de sombra (a da pista é estática, feita uma vez): a sombra de contato é um disco de borda macia no chão embaixo
// dele (BBR32: a sombra diz a altura), que encolhe e clareia com a altura.

import * as THREE from 'three';
import { REFERENCE_DOLL } from '../data/referenceDoll.js';
import { referenceDoll } from '../clay/kit/scaleMarker.js';
import { createRayHit } from '../physics/collisionWorld.js';
import { MOVETYPE } from '../player/movement.js';
import { bodyShape, createSquash, resetSquash, updateSquash } from './squashStretch.js';

const SH = REFERENCE_DOLL.shadow;
const UP = new THREE.Vector3(0, 1, 0);

/** Disco de borda macia: alfa 1 no meio caindo suave até 0 na borda (textura procedural, sem arquivo). */
function contactShadowTexture(size = SH.texture) {
  const data = new Uint8Array(size * size * 4);
  for (let j = 0; j < size; j++) {
    for (let i = 0; i < size; i++) {
      const x = ((i + 0.5) / size) * 2 - 1;
      const y = ((j + 0.5) / size) * 2 - 1;
      const r = Math.min(1, Math.hypot(x, y));
      const t = 1 - r;
      const a = t * t * (3 - 2 * t); // smoothstep(1, 0, r)
      data[(j * size + i) * 4 + 3] = Math.round(a * a * 255);
    }
  }
  const tex = new THREE.DataTexture(data, size, size, THREE.RGBAFormat);
  tex.name = 'massacre.sombra-de-contato';
  tex.magFilter = THREE.LinearFilter;
  tex.minFilter = THREE.LinearFilter;
  tex.needsUpdate = true;
  return tex;
}

export class PlayerBody {
  /**
   * @param {{scene: THREE.Scene, world: import('../physics/collisionWorld.js').CollisionWorld, color?: string,
   *   seed?: string}} opts
   */
  constructor({ scene, world, color, seed = 'jogador' }) {
    this.world = world;
    const doll = referenceDoll(REFERENCE_DOLL.height, { color, seed });
    this.root = new THREE.Group();
    this.root.name = 'corpo-do-jogador';
    this.pivot = new THREE.Group();
    this.pivot.position.y = doll.ankle;
    for (const mesh of doll.upper) {
      mesh.position.y = -doll.ankle;
      this.pivot.add(mesh);
    }
    this.boots = doll.boots;
    this.root.add(this.boots, this.pivot);
    this.root.traverse((o) => {
      o.castShadow = false;
    });
    this.shadowMap = contactShadowTexture();
    this.shadow = new THREE.Mesh(
      new THREE.PlaneGeometry(1, 1).rotateX(-Math.PI / 2),
      new THREE.MeshBasicMaterial({
        color: 0x000000, map: this.shadowMap, transparent: true, depthWrite: false, opacity: SH.opacity,
        polygonOffset: true, polygonOffsetFactor: -2, polygonOffsetUnits: -2,
      }),
    );
    this.shadow.name = 'sombra-de-contato';
    this.shadow.castShadow = false;
    this.shadow.receiveShadow = false;
    this.root.visible = false;
    this.shadow.visible = false;
    scene.add(this.root, this.shadow);
    this.squash = createSquash();
    this.shape = { sy: 1, sxz: 1, widen: 0 }; // forma mostrada (a da última pose)
    this.yaw = 0; // virada mostrada
    this._hit = createRayHit();
    this._q = new THREE.Quaternion();
  }

  /** Um tick da mola (depois do tick do jogador, com os eventos dele). */
  tick(pawn, dt) {
    updateSquash(this.squash, pawn.state, pawn.env.events, pawn.vitals.alive, dt);
  }

  /** Volta ao jogo: a mola zera (a forma aparece normal já na próxima pose). */
  reset() {
    resetSquash(this.squash);
  }

  /** Troca de pose (EV.POSE): congela a forma, a virada e as botas no valor da mola de agora. */
  onPose(pawn) {
    const sh = bodyShape(this.squash, pawn.state.duckAmount, this.shape);
    this.yaw = pawn.yaw;
    this.pivot.scale.set(sh.sxz, sh.sy, sh.sxz);
    this.boots.scale.set(1 + sh.widen, 1, 1);
    this.root.rotation.y = this.yaw + Math.PI; // o boneco olha para +Z; o jogador, para −Z no yaw 0
  }

  /** Um quadro: pés interpolados e a sombra de contato no chão embaixo (visível só fora da primeira pessoa). */
  update(pawn, alpha) {
    const visible = pawn.thirdPerson || pawn.state.moveType === MOVETYPE.NOCLIP;
    this.root.visible = visible;
    if (!visible) {
      this.shadow.visible = false;
      return;
    }
    const s = pawn.state;
    const p = pawn.prevOrigin;
    const x = p.x + (s.origin.x - p.x) * alpha;
    const y = p.y + (s.origin.y - p.y) * alpha;
    const z = p.z + (s.origin.z - p.z) * alpha;
    this.root.position.set(x, y, z);
    const hit = this._hit;
    if (!this.world.raycast(x, y + 1, z, 0, -1, 0, SH.probe, hit)) {
      this.shadow.visible = false;
      return;
    }
    const k = Math.min(1, Math.max(0, (y - hit.point.y) / SH.fadeHeight));
    const size = SH.diameter * (1 + (SH.minScale - 1) * k);
    const n = hit.normal.y < 0 ? hit.normal.negate() : hit.normal;
    this.shadow.visible = true;
    this.shadow.position.copy(hit.point).addScaledVector(n, SH.lift);
    this.shadow.quaternion.copy(this._q.setFromUnitVectors(UP, n));
    this.shadow.scale.set(size, 1, size);
    this.shadow.material.opacity = SH.opacity * (1 + (SH.minOpacity - 1) * k);
  }

  dispose() {
    this.root.removeFromParent();
    this.shadow.removeFromParent();
    this.root.traverse((o) => {
      if (!o.isMesh) return;
      o.geometry.dispose();
      o.material.dispose();
    });
    this.shadow.geometry.dispose();
    this.shadow.material.dispose();
    this.shadowMap.dispose();
  }
}
```

- [ ] **Passo 7: O corpo na partida** — criado com o jogador (mapa com colisão), mola no tick, forma na troca de pose, pés no quadro, zerado na volta e liberado na saída.

Em `src/modes/matchState.js`, trocar:

```
// ferramentas de debug da física e do movimento (medidores de counter-strafe e de salto e queda), o teleporte das
// estações (`estacao`, pista de testes), as escalas da sensação da câmera (subfase 3.5, seção "Conforto") e o resumo
// que vai para a tela de resultado.

```

por:

```
// ferramentas de debug da física e do movimento (medidores de counter-strafe e de salto e queda), o teleporte das
// estações (`estacao`, pista de testes), as escalas da sensação da câmera (subfase 3.5, seção "Conforto"), o corpo do
// jogador (o boneco de referência com squash & stretch, visível em terceira pessoa e no noclip) e o resumo que vai para
// a tela de resultado.

```

Em `src/modes/matchState.js`, trocar:

```
import { PlayerPawn } from '../player/playerPawn.js';
import { itemName, zoomLevels } from '../player/hands.js';
```

por:

```
import { PlayerPawn } from '../player/playerPawn.js';
import { PlayerBody } from '../characters/playerBody.js';
import { itemName, zoomLevels } from '../player/hands.js';
```

Em `src/modes/matchState.js`, trocar:

```
    this.camera = null;
    this.player = null;
    this.physicsDebug = null;
    this.showPos = null;
```

por:

```
    this.camera = null;
    this.player = null;
    this.body = null; // corpo do jogador (subfase 3.5)
    this.physicsDebug = null;
    this.showPos = null;
```

Em `src/modes/matchState.js`, trocar:

```
      });
      this.physicsDebug = new PhysicsDebugView({ scene: this.map.scene, world: this.map.collision });
```

por:

```
      });
      this.body = new PlayerBody({ scene: this.map.scene, world: this.map.collision });
      this.body.onPose(this.player);
      this.physicsDebug = new PhysicsDebugView({ scene: this.map.scene, world: this.map.collision });
```

Em `src/modes/matchState.js`, trocar:

```
      });
      this.subs.on(s.events, EV.PLAYER_WEAPON, () => this.#syncHeld());
```

por:

```
      });
      // Corpo: forma, virada e botas mudam só na troca de pose (12/s), como a massinha animada "em dois".
      this.subs.on(s.events, EV.POSE, () => this.body?.onPose(this.player));
      this.subs.on(s.events, EV.PLAYER_WEAPON, () => this.#syncHeld());
```

Em `src/modes/matchState.js`, trocar:

```
    if (this.player instanceof PlayerPawn) {
      this.returnPoint.update(this.player.vitals.alive, this.player.state.onGround);
```

por:

```
    if (this.player instanceof PlayerPawn) {
      this.body.tick(this.player, dt);
      this.returnPoint.update(this.player.vitals.alive, this.player.state.onGround);
```

Em `src/modes/matchState.js`, trocar:

```
    this.player.respawn(point.position, point.yaw, point.pitch);
    this.returnPoint.placed();
```

por:

```
    this.player.respawn(point.position, point.yaw, point.pitch);
    this.body?.reset();
    this.returnPoint.placed();
```

Em `src/modes/matchState.js`, trocar:

```
    this.player.updateCamera(this.camera, a);
    this.physicsDebug?.update(this.player, a);
```

por:

```
    this.player.updateCamera(this.camera, a);
    this.body?.update(this.player, a);
    this.physicsDebug?.update(this.player, a);
```

Em `src/modes/matchState.js`, trocar:

```
    this.hud?.dispose();
    this.physicsDebug?.dispose();
```

por:

```
    this.hud?.dispose();
    this.body?.dispose();
    this.physicsDebug?.dispose();
```

Em `src/modes/matchState.js`, trocar:

```
    this.player = null;
    this.physicsDebug = null;
```

por:

```
    this.player = null;
    this.body = null;
    this.physicsDebug = null;
```

- [ ] **Passo 8: Rodar os testes da tarefa**

Run: `node --test tests/squashStretch.test.js tests/showcase.test.js tests/sdfMesh.test.js`
Expected: PASS — todos os testes dos três arquivos passando.

- [ ] **Passo 9: Suíte inteira**

Run: `npm test`
Expected: PASS — 279 testes passando.

- [ ] **Passo final: Commit** (só com o pedido do usuário)

```bash
git add src/data/referenceDoll.js src/data/footprints.js src/clay/prints/sole.js src/clay/kit src/characters src/modes/matchState.js tests/squashStretch.test.js
git commit -m "MASSACRE 3.5: boneco de referência com botas e o squash & stretch do corpo" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Tarefa 4: Pegadas — as marcas, a fila e a escolha da placa (puro)

**Files:**
- Create: `src/clay/prints/marks.js`, `src/clay/prints/printQueue.js`, `src/clay/prints/surface.js`, `tests/footprints.test.js` (a parte pura; a Tarefa 5 completa)

Tudo o que a GPU vai desenhar sai daqui, em JS: as marcas de cada evento (o pé do passo a ±5,6 u com o bico 6° para fora, virado para o olhar; o par do pouso a ±6,2 u, 8° para fora, acima de 150 u/s de queda; o par da saída do pulo, de onde ele saiu, com a frente mais funda; dois sulcos por tick de slide no chão e o montinho à frente no fim, depois de um tick no chão), a passagem para o referencial de uma placa (a inversa da matriz de mundo, com o y dos pés para comparar com o topo) e o valor de cada texel em inteiros de 8 bits — fundo pelos cravos com a parede de 1,1 u, lábio gaussiano fora da borda (60% mais alto na frente, nunca acima do fundo máximo da marca), brilho até 2,4 u — já esmaecido pelos passos que vieram depois da marca. A fila guarda marcas e passos do esmaecimento (12 por segundo de tick, conta exata) na ordem do jogo e vira, na troca de pose, o plano de uma passada por placa. A superfície tira o tamanho do mapa (4 texels/u, teto de 1024 com a mesma densidade nos dois eixos) e escolhe as placas: a que a marca encosta e com o topo a até 4 u dos pés. A classe `PrintSurface` (o alvo de render ligado ao material) já vem no arquivo; os testes dela entram na Tarefa 5, com o `setPrints` do `ClayMaterial`.

- [ ] **Passo 1: Escrever os testes**

```js file=tests/footprints.test.js
// Testes das pegadas (subfase 3.5): a forma da marca (contorno da sola com o bico cortado e o lado de dentro, cravos,
// lábio que não passa do fundo, brilho); a posição e o rumo dos pés (passo, par do pouso, pulo, sulcos e montinho do
// slide) e o referencial de uma placa girada; a escolha da placa (a que a marca encosta e está na altura dos pés;
// nenhuma fora da massinha); a fila na ordem do jogo e a pausa; o esmaecimento em inteiros de 8 bits (o pouso em 255
// poses, o passo em 191) e a passada única por peça igual a aplicar a fila item a item; o tamanho dos alvos e o teto de
// 1024.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import * as THREE from 'three';
import { FOOTPRINTS, SOLE } from '../src/data/footprints.js';
import { ClayMaterial } from '../src/clay/ClayMaterial.js';
import {
  MARK, createPrintTrack, fadeTexel, footMark, footPair, grooveMarks, markLife, markTexel, moundMark, tickMarks,
} from '../src/clay/prints/marks.js';
import { PrintQueue, createPlan, surfaceLife } from '../src/clay/prints/printQueue.js';
import { placeMark, surfaceSize } from '../src/clay/prints/surface.js';
import { createMoveState } from '../src/player/movement.js';

const M = FOOTPRINTS.marks;
const DEG = Math.PI / 180;
const DT = 1 / 64;

/** Placa de massinha da pista: 180 × 5 × 130, em pé sobre o kraft (0,3 u) em (x, z), girada `heading` graus. */
function plate(x, z, heading, id = 'placa') {
  const mesh = new THREE.Mesh(new THREE.BoxGeometry(180, 5, 130), new ClayMaterial({ seed: id }));
  mesh.matrixAutoUpdate = false;
  mesh.matrix.makeRotationY(-heading * DEG).setPosition(x, 0.3 + 2.5, z);
  return { id, mesh, material: mesh.material, width: 180, depth: 130, top: 2.5 };
}

/** Superfície pura (sem alvo) para a escolha da placa. */
function frame(decl) {
  decl.mesh.updateWorldMatrix(true, false, true);
  return { ...decl, inverse: decl.mesh.matrixWorld.clone().invert().elements.slice() };
}

/** Valor do texel da marca no ponto do referencial do pé (a ao longo, bi para dentro). */
function soleTexel(m, a, bi, fades = 0) {
  const rx = -m.dz;
  const rz = m.dx;
  const b = bi * m.inner;
  return markTexel(m, m.x + m.dx * a + rx * b, m.z + m.dz * a + rz * b, fades);
}

test('forma da marca: contorno da sola (16,4 u com o bico cortado em 7,6), lado de dentro, cravos, lábio e brilho', () => {
  const m = footMark(0, 0, 0, 0, 0, M.land);
  const depth = (a, bi) => soleTexel(m, a, bi)[0];
  // Comprimento: do calcanhar (−8,2) ao corte do bico (+7,6); largura no bico ±3,9 (desviado para dentro).
  assert.ok(depth(-7.5, 0) > 0 && depth(-8.4, 0) === 0, 'calcanhar');
  assert.ok(depth(7.4, 0) > 0 && depth(7.7, 0) === 0, 'bico cortado reto');
  assert.ok(depth(4.3, 3.8) > 0 && depth(4.3, -3.8) === 0, 'o bico desvia para o lado de dentro');
  // Cravos (longe da parede): barra 1, vão da frente 0,74, arco 0,58, vão do calcanhar 0,78.
  assert.equal(depth(2.0, 0), 255, 'barra da frente (de 1,6 a 2,59)');
  assert.equal(depth(1.2, 0), Math.round(SOLE.cleats.front.gap * 255), 'vão da frente (de 0,79 a 1,6)');
  assert.equal(depth(-1.8, 0), Math.round(SOLE.cleats.arch * 255), 'arco liso');
  assert.equal(depth(-5, 1.2), 255, 'barra do calcanhar (de 0,8 a 1,6)');
  assert.equal(depth(-5, 0.4), Math.round(SOLE.cleats.heel.gap * 255), 'vão do calcanhar (de 0 a 0,8)');
  // Lábio fora da borda (0 dentro), mais alto na frente, nunca acima do fundo máximo; brilho até 2,4 u da borda.
  const lip = (a, bi) => soleTexel(m, a, bi)[1];
  assert.equal(lip(0, 0), 0);
  const side = Math.max(...[3.6, 3.9, 4.2, 4.5, 4.8].map((b) => lip(-2, b)));
  const front = Math.max(...[8.2, 8.5, 8.8, 9.1].map((a) => lip(a, 0.3)));
  assert.ok(side > 150 && front === 255 && front > side, `lábio: lado ${side}, frente ${front}`);
  const step = footMark(0, 0, 0, 0, 0, M.step);
  const stepFront = Math.max(...[8.2, 8.5, 8.8, 9.1].map((a) => soleTexel(step, a, 0.3)[1]));
  assert.equal(stepFront, 191, 'o lábio do passo para no fundo dele (0,75)');
  assert.equal(soleTexel(m, 9.9, 0.3)[2], 255, 'brilho a 2,3 u do bico');
  assert.equal(soleTexel(m, 10.1, 0.3)[2], 0, 'sem brilho a 2,5 u');
});

test('pés: passo a ±5,6 u com o bico 6° para fora; pares do pouso e do pulo; sulcos e montinho do slide', () => {
  // Olhando para −Z (yaw 0): a direita do olhar é +X.
  const left = footMark(100, 5, 200, 0, 0, M.step);
  const right = footMark(100, 5, 200, 0, 1, M.step);
  assert.ok(Math.abs(left.x - 94.4) < 1e-9 && Math.abs(right.x - 105.6) < 1e-9 && left.z === 200 && left.y === 5);
  assert.ok(Math.abs(Math.atan2(-left.dx, -left.dz) - 6 * DEG) < 1e-9, 'esquerdo gira para a esquerda');
  assert.ok(Math.abs(Math.atan2(-right.dx, -right.dz) + 6 * DEG) < 1e-9, 'direito gira para a direita');
  assert.equal(left.inner, 1);
  assert.equal(right.inner, -1);
  // Andando de lado o pé continua de frente para o olhar: o rumo sai do yaw, não da velocidade.
  const turned = footMark(0, 0, 0, 90 * DEG, 1, M.step);
  assert.ok(Math.abs(Math.atan2(-turned.dx, -turned.dz) - 84 * DEG) < 1e-9);
  const [l, r] = footPair(0, 0, 0, 0, M.land);
  assert.ok(Math.abs(l.x + 6.2) < 1e-9 && Math.abs(r.x - 6.2) < 1e-9 && l.strength === 1);
  assert.ok(Math.abs(Math.atan2(-l.dx, -l.dz) - 8 * DEG) < 1e-9);
  // Pulo: nas barras, a frente 30% mais funda (satura em 1) e o calcanhar pela metade (o impulso).
  const [jl] = footPair(0, 0, 0, 0, M.jump);
  assert.equal(soleTexel(jl, 5.5, 0)[0], 255, 'frente funda');
  assert.equal(soleTexel(jl, -5, 1.2)[0], Math.round(M.jump.strength * M.jump.heel * 255), 'calcanhar raso');
  // Slide: dois sulcos a ±5,6 u da trajetória, com o comprimento do deslocamento.
  const grooves = grooveMarks(0, 0, 0, -10, 0);
  assert.equal(grooves.length, 2);
  assert.deepEqual(grooves.map((g) => g.x).sort((a, b) => a - b), [-5.6, 5.6]);
  assert.ok(grooves.every((g) => g.kind === MARK.GROOVE && g.length === 10 && g.dz === -1));
  assert.equal(markTexel(grooves[0], grooves[0].x, -5)[0], 128, 'fundo do sulco (0,5)');
  assert.deepEqual(grooveMarks(1, 1, 1, 1, 0), [], 'sem deslocamento, nada');
  const mound = moundMark(0, 0, 0, 0, -1);
  assert.equal(mound.z, -M.slide.moundAhead);
  assert.deepEqual(markTexel(mound, 0, -8), [0, 128, 255], 'montinho: só lábio, da força dos sulcos');
});

test('referencial de uma placa girada: posição (com o y dos pés) e rumo no XZ do objeto', () => {
  const p = frame(plate(600, 1580, 4));
  const yaw = 30 * DEG;
  const m = footMark(610, 5.3, 1560, yaw, 0, M.step);
  const local = placeMark(p, m);
  assert.ok(local, 'cai na placa');
  const want = new THREE.Vector3(m.x, m.y, m.z).applyMatrix4(p.mesh.matrixWorld.clone().invert());
  assert.ok(Math.abs(local.x - want.x) < 1e-9 && Math.abs(local.z - want.z) < 1e-9);
  assert.ok(Math.abs(local.y - 2.5) < 1e-9, 'os pés no topo da placa');
  // O rumo gira junto: o yaw do pé no objeto = o do mundo + o giro da placa.
  const worldYaw = Math.atan2(-m.dx, -m.dz);
  assert.ok(Math.abs(Math.atan2(-local.dx, -local.dz) - (worldYaw + 4 * DEG)) < 1e-9);
  assert.ok(Math.abs(Math.hypot(local.dx, local.dz) - 1) < 1e-12);
  assert.equal(local.inner, m.inner, 'o resto da marca vem junto');
});

test('escolha da placa: a que a marca encosta e está na altura dos pés; nenhuma fora da massinha', () => {
  const a = frame(plate(600, 1580, 3, 'P'));
  const b = frame(plate(400, 1580, -2, 'E'));
  const on = (x, z, y = 5.3) => [a, b].filter((p) => placeMark(p, footMark(x, y, z, 0, 1, M.step))).map((p) => p.id);
  assert.deepEqual(on(600, 1580), ['P'], 'no meio da placa');
  assert.deepEqual(on(400, 1600), ['E']);
  assert.deepEqual(on(600 + 90 - 5.6 + 8, 1580), ['P'], 'passando da borda: cortada, mas na placa');
  assert.deepEqual(on(600, 1580, 0.3), [], 'no kraft (5 u abaixo do topo): fora da massinha');
  assert.deepEqual(on(0, 1580), [], 'longe de qualquer placa');
  assert.deepEqual(on(600, 1580 + 65 + 20), [], 'além da borda com folga');
  // O limite da altura: 4 u.
  assert.deepEqual(on(600, 1580, 5.3 + 3.9), ['P']);
  assert.deepEqual(on(600, 1580, 5.3 + 4.1), []);
});

test('marcas do tick: passo onde o pé estava, pouso acima de 150 u/s, pulo de onde saiu, sulcos e montinho', () => {
  const t = createPrintTrack();
  const s = createMoveState({ position: new THREE.Vector3(10, 0, 0) });
  s.onGround = true;
  const from = new THREE.Vector3(10, 0, 4);
  const out = [];
  tickMarks(t, s, from, [{ type: 'step', foot: 1, x: 3, y: 0, z: 7 }], 0, out);
  assert.equal(out.length, 1);
  assert.ok(Math.abs(out[0].x - (3 + M.step.offset)) < 1e-9 && out[0].z === 7, 'o pé do evento');
  tickMarks(t, s, from, [{ type: 'land', speed: 100 }], 0, out);
  assert.equal(out.length, 0, 'pouso lento não marca');
  tickMarks(t, s, from, [{ type: 'land', speed: 420 }], 0, out);
  assert.equal(out.length, 2);
  assert.ok(out.every((m) => m.strength === M.land.strength && m.z === 0), 'o par onde parou');
  tickMarks(t, s, from, [{ type: 'jump' }], 0, out);
  assert.ok(out.length === 2 && out.every((m) => m.z === 4 && m.front === M.jump.front), 'o par de onde saiu');
  tickMarks(t, s, from, [{ type: 'walljump', nx: 1, nz: 0 }], 0, out);
  assert.equal(out.length, 0, 'wall-jump não marca o chão');
  // Slide no chão: dois sulcos por tick; o fim depois de um tick no chão deixa o montinho à frente.
  s.sliding = true;
  s.origin.set(10, 0, -6);
  tickMarks(t, s, new THREE.Vector3(10, 0, 0), [{ type: 'slide', phase: 'start' }], 0, out);
  assert.ok(out.length === 2 && out.every((m) => m.kind === MARK.GROOVE && m.length === 6));
  s.sliding = false;
  tickMarks(t, s, new THREE.Vector3(10, 0, -6), [{ type: 'slide', phase: 'end' }], 0, out);
  assert.equal(out.length, 1);
  assert.ok(out[0].kind === MARK.MOUND && out[0].x === 10 && out[0].z === -6 - M.slide.moundAhead);
  // Slide que sai do chão (e acaba no ar): sem montinho.
  s.sliding = true;
  s.onGround = false;
  tickMarks(t, s, new THREE.Vector3(10, 0, -6), [], 0, out);
  assert.equal(out.length, 0);
  s.sliding = false;
  tickMarks(t, s, new THREE.Vector3(10, 0, -6), [{ type: 'slide', phase: 'end' }], 0, out);
  assert.equal(out.length, 0);
});

test('fila na ordem do jogo: 12 passos do esmaecimento por segundo de tick; a pausa congela', () => {
  const q = new PrintQueue();
  const plan = createPlan(2);
  for (let i = 0; i < 64; i++) q.advance(DT);
  assert.equal(q.drain(plan).fades, 12, 'um segundo de tick, 12 passos (conta exata)');
  assert.equal(q.acc, 0);
  const a = { id: 'a' };
  const b = { id: 'b' };
  const c = { id: 'c' };
  q.push(0, a);
  for (let i = 0; i < 16; i++) q.advance(DT); // 3 passos
  q.push(1, b);
  q.push(0, c);
  for (let i = 0; i < 6; i++) q.advance(DT); // mais 1 (1,125)
  q.drain(plan);
  assert.equal(plan.fades, 4);
  assert.deepEqual(plan.stamps[0], [a, c], 'na ordem do jogo');
  assert.deepEqual(plan.stamps[1], [b]);
  assert.deepEqual([a.fades, b.fades, c.fades], [4, 1, 1], 'passos depois de cada marca');
  // Pausa: o MatchState não anda o tick; poses seguidas não esmaecem nada.
  q.push(0, { id: 'd' });
  assert.equal(q.drain(plan).fades, 0);
  assert.equal(q.drain(plan).stamps[0].length, 0, 'a fila esvaziou');
});

test('esmaecimento em 8 bits: o pouso some em 255 poses (21,25 s), o passo em 191, o sulco em 128, o brilho em 85', () => {
  const [land] = footPair(0, 0, 0, 0, M.land);
  const step = footMark(0, 0, 0, 0, 0, M.step);
  const [groove] = grooveMarks(0, 0, 0, -10, 0);
  assert.equal(markLife(land), 255);
  assert.equal(markLife(step), 191);
  assert.equal(markLife(groove), 128);
  assert.equal(markLife(moundMark(0, 0, 0, 0, -1)), 128);
  assert.equal(255 / FOOTPRINTS.fade.rate, 21.25);
  assert.equal(soleTexel(land, 2, 0, 254)[0], 1, 'a barra mais funda ainda está lá na pose 254');
  assert.equal(soleTexel(land, 2, 0, 255)[0], 0);
  assert.equal(soleTexel(step, 2, 0, 190)[0], 1);
  assert.equal(soleTexel(step, 2, 0, 191)[0], 0);
  assert.equal(soleTexel(land, 0, 0, 84)[2], 3);
  assert.equal(soleTexel(land, 0, 0, 85)[2], 0, 'brilho em 85 poses (7,1 s)');
  // Esmaecer o texel carimbado = carimbar já esmaecido (a GPU faz dos dois jeitos).
  for (const [a, bi] of [[2, 0], [8.6, 0.3], [-3, 4.1], [9.9, 0]]) {
    for (const k of [0, 3, 90, 200]) assert.deepEqual(soleTexel(land, a, bi, k), fadeTexel(soleTexel(land, a, bi), k));
  }
  // Toda marca some por inteiro na vida dela.
  for (const m of [land, step, groove]) {
    for (let x = -14; x <= 14; x += 0.5) {
      for (let z = -14; z <= 14; z += 0.5) {
        assert.deepEqual(markTexel(m, m.x + x, m.z + z, markLife(m)), [0, 0, 0]);
      }
    }
  }
});

test('uma passada por peça (esmaecer a pose, depois as marcas já esmaecidas) = aplicar a fila item a item', () => {
  const W = 48;
  const texel = (grid, m, fades) => {
    for (let j = 0; j < W; j++) {
      for (let i = 0; i < W; i++) {
        const v = markTexel(m, i - W / 2 + 0.5, j - W / 2 + 0.5, fades);
        for (let c = 0; c < 3; c++) grid[(j * W + i) * 3 + c] = Math.max(grid[(j * W + i) * 3 + c], v[c]);
      }
    }
  };
  const fade = (grid, n) => {
    for (let k = 0; k < grid.length; k++) grid[k] = Math.max(0, grid[k] - n * [1, 1, 3][k % 3]);
  };
  const marks = [
    ...footPair(0, 0, 4, 0.3, M.land), footMark(-3, 0, -6, 0.3, 0, M.step), ...grooveMarks(-10, 10, 8, -12, 0),
    moundMark(8, 0, -12, 0.6, -0.8),
  ];
  const q = new PrintQueue();
  const seq = new Uint8Array(W * W * 3);
  const old = new Uint8Array(W * W * 3);
  texel(seq, footMark(2, 0, 2, 1, 1, M.step), 0);
  texel(old, footMark(2, 0, 2, 1, 1, M.step), 0);
  marks.forEach((m, n) => {
    q.push(0, { ...m });
    texel(seq, m, 0);
    for (let k = 0; k < (n % 3) * 16 + 5; k++) {
      const before = q.size;
      q.advance(DT);
      if (q.size > before) fade(seq, q.size - before);
    }
  });
  const plan = q.drain(createPlan(1));
  assert.ok(plan.fades > 3);
  fade(old, plan.fades);
  for (const m of plan.stamps[0]) texel(old, m, m.fades);
  assert.deepEqual(old, seq);
  assert.equal(surfaceLife(0, plan.fades, plan.stamps[0]), Math.max(...plan.stamps[0].map((m) => markLife(m) - m.fades)));
  assert.equal(surfaceLife(100, 4, []), 96);
  assert.equal(surfaceLife(3, 4, []), 0);
});

test('alvos: 4 texels/u (720 × 520 na placa da pista), teto de 1024 por lado com a mesma densidade nos dois eixos', () => {
  assert.deepEqual(surfaceSize(180, 130), { width: 720, height: 520, texelsPerUnit: 4 });
  const wide = surfaceSize(300, 100);
  assert.equal(wide.width, 1024);
  assert.equal(wide.height, Math.round((100 * 1024) / 300));
  const huge = surfaceSize(4000, 4000);
  assert.deepEqual([huge.width, huge.height], [1024, 1024]);
  assert.equal(surfaceSize(2, 2).width, 8);
});
```

- [ ] **Passo 2: Rodar e ver falhar**

Run: `node --test tests/footprints.test.js`
Expected: FAIL — o arquivo nem carrega: `ERR_MODULE_NOT_FOUND` (não acha `src/clay/prints/marks.js`).

- [ ] **Passo 3: As marcas**

```js file=src/clay/prints/marks.js
// Marcas das pegadas (subfase 3.5; números em src/data/footprints.js; referências no item 12 do moodboard): o que cada
// evento do movimento deixa na massinha — o pé do passo, o par do pouso, o par da saída do pulo, os sulcos do slide e o
// montinho do fim —, a passagem para o referencial de uma peça de chão e o valor de cada texel do mapa de pegadas (R
// fundo, G lábio, B massa fresca) em inteiros de 8 bits, com o esmaecimento. É a mesma conta que a GPU faz ao carimbar
// (src/clay/prints/stampPass.js); no navegador as duas são comparadas texel a texel. Puro (sem WebGL). Referencial de
// uma marca de pé: `a` ao longo do pé (para o bico) e `b` para a direita do pé; a sola usa bi = b × inner (o lado de
// dentro positivo: +1 no pé esquerdo, −1 no direito).

import { FOOTPRINTS, SOLE } from '../../data/footprints.js';
import { smoothstep, soleCleats, soleDistance } from './sole.js';

const FP = FOOTPRINTS;
const LR = FP.lipRing;
const DEG = Math.PI / 180;

export const MARK = Object.freeze({ FOOT: 0, GROOVE: 1, MOUND: 2 });

/** Alcance do lábio (u além da borda): a gaussiana vale ~0 a partir daqui. */
export const LIP_REACH = LR.offset + 3 * LR.width;

const clamp01 = (v) => (v < 0 ? 0 : v > 1 ? 1 : v);

/** Valor de 0–1 no inteiro de 8 bits do mapa (o arredondamento da GPU ao gravar no alvo RGBA8). */
export const q8 = (v) => Math.round(clamp01(v) * 255);

/** Gaussiana do lábio a `d` u fora da borda. */
function lipRing(d) {
  const t = (d - LR.offset) / LR.width;
  return Math.exp(-t * t);
}

/**
 * Marca de um pé no mundo: pés do jogador em (x, y, z), olhar `yaw`, `foot` (0 esquerdo, 1 direito) e a especificação
 * (FOOTPRINTS.marks.step/land/jump): o pé a ±offset do centro no eixo direito do olhar, virado para a frente do olhar
 * com o bico `toeOutDeg` para fora; `heel`/`front` (pulo): o fundo cresce do calcanhar ao bico.
 */
export function footMark(x, y, z, yaw, foot, { offset, toeOutDeg, strength, heel = 1, front = 1 }) {
  const fx = -Math.sin(yaw);
  const fz = -Math.cos(yaw);
  const rx = Math.cos(yaw);
  const rz = -Math.sin(yaw);
  const side = foot === 0 ? -1 : 1;
  const turn = side * toeOutDeg * DEG; // esquerdo gira para a esquerda, direito para a direita
  const c = Math.cos(turn);
  const s = Math.sin(turn);
  return {
    kind: MARK.FOOT, x: x + rx * side * offset, y, z: z + rz * side * offset,
    dx: fx * c + rx * s, dz: fz * c + rz * s, inner: foot === 0 ? 1 : -1, strength, heel, front,
  };
}

/** O par de pés lado a lado (pouso, saída do pulo). */
export function footPair(x, y, z, yaw, spec) {
  return [footMark(x, y, z, yaw, 0, spec), footMark(x, y, z, yaw, 1, spec)];
}

/**
 * Sulcos de calcanhar do slide de (x0, z0) a (x1, z1): dois segmentos a ±offset da trajetória, com a meia largura e a
 * força do slide. Sem deslocamento, nenhum.
 */
export function grooveMarks(x0, z0, x1, z1, y, spec = FP.marks.slide) {
  const len = Math.hypot(x1 - x0, z1 - z0);
  if (len < 1e-6) return [];
  const dx = (x1 - x0) / len;
  const dz = (z1 - z0) / len;
  return [-1, 1].map((side) => ({
    kind: MARK.GROOVE, x: x0 - dz * side * spec.offset, y, z: z0 + dx * side * spec.offset, dx, dz, length: len,
    halfWidth: spec.halfWidth, strength: spec.strength,
  }));
}

/** Montinho de massa empurrada à frente dos pés no fim do slide (direção unitária dx, dz), da força dos sulcos. */
export function moundMark(x, y, z, dx, dz, spec = FP.marks.slide) {
  return {
    kind: MARK.MOUND, x: x + dx * spec.moundAhead, y, z: z + dz * spec.moundAhead, dx, dz, radius: spec.moundRadius,
    strength: spec.strength,
  };
}

/**
 * A marca no referencial de uma peça: `inv` = elementos (coluna a coluna) da inversa da matriz de mundo dela. Posição
 * (inclusive o y dos pés, para comparar com o topo da peça) e direção no XZ do objeto; o resto copiado. Escreve em
 * `out`.
 */
export function toLocal(m, inv, out = {}) {
  Object.assign(out, m);
  out.x = inv[0] * m.x + inv[4] * m.y + inv[8] * m.z + inv[12];
  out.y = inv[1] * m.x + inv[5] * m.y + inv[9] * m.z + inv[13];
  out.z = inv[2] * m.x + inv[6] * m.y + inv[10] * m.z + inv[14];
  const dx = inv[0] * m.dx + inv[8] * m.dz;
  const dz = inv[2] * m.dx + inv[10] * m.dz;
  const n = Math.hypot(dx, dz) || 1;
  out.dx = dx / n;
  out.dz = dz / n;
  return out;
}

/** Retângulo da marca no plano dela [x0, z0, x1, z1] (quanto o carimbo cobre). */
export function markBounds(m, out = [0, 0, 0, 0]) {
  let r;
  if (m.kind === MARK.FOOT) r = FP.footReach;
  else if (m.kind === MARK.MOUND) r = m.radius;
  else r = m.halfWidth + Math.max(LIP_REACH, FP.freshReach);
  const x1 = m.kind === MARK.GROOVE ? m.x + m.dx * m.length : m.x;
  const z1 = m.kind === MARK.GROOVE ? m.z + m.dz * m.length : m.z;
  out[0] = Math.min(m.x, x1) - r;
  out[1] = Math.min(m.z, z1) - r;
  out[2] = Math.max(m.x, x1) + r;
  out[3] = Math.max(m.z, z1) + r;
  return out;
}

/** Fundo máximo da marca (0–1): o lábio nunca passa dele. */
export function markPeak(m) {
  return clamp01(m.kind === MARK.FOOT ? m.strength * Math.max(m.heel, m.front) : m.strength);
}

/** Poses até a marca sumir inteira: o fundo máximo (e o lábio, que não passa dele) e o brilho, cada um no seu ritmo. */
export function markLife(m) {
  const f = FP.fade;
  const peak = q8(markPeak(m));
  return Math.max(Math.ceil(peak / f.depth), Math.ceil(peak / f.lip), Math.ceil(255 / f.fresh));
}

/**
 * Valor do mapa (R, G, B em 0–255) que a marca `m` (no plano dela) carimba no ponto (x, z), já com `fades` poses de
 * esmaecimento. A GPU faz a mesma conta (stampPass.js).
 */
export function markTexel(m, x, z, fades = 0, out = [0, 0, 0]) {
  let r = 0;
  let g = 0;
  let b = 0;
  const peak = markPeak(m);
  const px = x - m.x;
  const pz = z - m.z;
  if (m.kind === MARK.FOOT) {
    const a = px * m.dx + pz * m.dz;
    const bi = (pz * m.dx - px * m.dz) * m.inner;
    const d = soleDistance(a, bi);
    const push = m.heel + (m.front - m.heel) * smoothstep(SOLE.heel.a, SOLE.toe.a, a);
    r = smoothstep(0, FP.wall, -d) * soleCleats(a, bi) * m.strength * push;
    if (d > 0) {
      const front = 1 + LR.front * smoothstep(LR.frontFrom, LR.frontTo, a);
      g = Math.min(peak, lipRing(d) * front * m.strength * LR.gain);
    }
    b = d < FP.freshReach ? 1 : 0;
  } else if (m.kind === MARK.GROOVE) {
    const t = Math.min(m.length, Math.max(0, px * m.dx + pz * m.dz));
    const d = Math.hypot(px - m.dx * t, pz - m.dz * t) - m.halfWidth;
    r = smoothstep(0, FP.wall, -d) * m.strength;
    if (d > 0) g = Math.min(peak, lipRing(d) * m.strength * LR.gain);
    b = d < FP.freshReach ? 1 : 0;
  } else {
    const k = 1 - (px * px + pz * pz) / (m.radius * m.radius);
    if (k > 0) {
      g = m.strength * k * k;
      b = 1;
    }
  }
  const f = FP.fade;
  out[0] = Math.max(0, q8(r) - fades * f.depth);
  out[1] = Math.max(0, q8(g) - fades * f.lip);
  out[2] = Math.max(0, q8(b) - fades * f.fresh);
  return out;
}

/** Um texel já no mapa depois de `fades` poses de esmaecimento (a subtração reversa da GPU, em 8 bits). */
export function fadeTexel(rgb, fades, out = [0, 0, 0]) {
  const f = FP.fade;
  out[0] = Math.max(0, rgb[0] - fades * f.depth);
  out[1] = Math.max(0, rgb[1] - fades * f.lip);
  out[2] = Math.max(0, rgb[2] - fades * f.fresh);
  return out;
}

/** Rastro entre ticks: o slide no chão do tick anterior (os pés no fim do último sulco e a direção dele). */
export function createPrintTrack() {
  return { sliding: false, x: 0, y: 0, z: 0, dx: 0, dz: 0 };
}

export function resetPrintTrack(t) {
  t.sliding = false;
  return t;
}

/**
 * Marcas do tick no mundo (em `out`), de quem está vivo e fora do noclip: `s` = estado de movimento depois do
 * playerMove, `from` = a origem no começo do tick (a do pulo e o começo do sulco), `events` = os do tick, `yaw` = o
 * olhar. Passo: o pé do evento, onde ele estava; pouso (acima de `minFall`): o par onde parou; pulo: o par de onde
 * saiu; slide no chão: os dois sulcos do tick; fim do slide depois de um tick no chão: o montinho à frente.
 */
export function tickMarks(t, s, from, events, yaw, out = []) {
  const M = FP.marks;
  out.length = 0;
  const o = s.origin;
  for (let i = 0; i < events.length; i++) {
    const e = events[i];
    if (e.type === 'step') out.push(footMark(e.x, e.y, e.z, yaw, e.foot, M.step));
    else if (e.type === 'land' && e.speed >= M.land.minFall) out.push(...footPair(o.x, o.y, o.z, yaw, M.land));
    else if (e.type === 'jump') out.push(...footPair(from.x, from.y, from.z, yaw, M.jump));
    else if (e.type === 'slide' && e.phase === 'end' && t.sliding) out.push(moundMark(t.x, t.y, t.z, t.dx, t.dz));
  }
  if (s.sliding && s.onGround) {
    const grooves = grooveMarks(from.x, from.z, o.x, o.z, o.y);
    if (grooves.length) {
      out.push(...grooves);
      t.dx = grooves[0].dx;
      t.dz = grooves[0].dz;
    }
    t.sliding = t.sliding || grooves.length > 0;
    t.x = o.x;
    t.y = o.y;
    t.z = o.z;
  } else t.sliding = false;
  return out;
}
```

- [ ] **Passo 4: A fila e a vida da placa**

```js file=src/clay/prints/printQueue.js
// Fila das pegadas (subfase 3.5): as marcas (já no referencial da peça que as recebe) e os passos do esmaecimento na
// ordem do jogo — um passo a cada 1/12 s de simulação (FOOTPRINTS.fade.rate; a pausa não anda o tick e congela) —,
// esvaziada a cada troca de pose do render (EV.POSE) num plano: quantos passos a pose aplica e, por peça, as marcas com
// quantos passos vêm depois de cada uma. Assim a GPU desenha tudo numa passada por peça (src/clay/prints/stampPass.js):
// primeiro o esmaecimento da pose inteira, depois cada marca já esmaecida pelos passos que vieram depois dela — o mesmo
// resultado, em 8 bits, de aplicar a fila item a item. Puro (sem WebGL).

import { FOOTPRINTS } from '../../data/footprints.js';
import { markLife } from './marks.js';

const FADE = Object.freeze({ fade: true });

export class PrintQueue {
  constructor() {
    this.items = [];
    this.acc = 0; // fração de passo do esmaecimento acumulada (em passos)
  }

  /** Itens na fila (marcas e passos do esmaecimento). */
  get size() {
    return this.items.length;
  }

  /** Marca `mark` (no referencial da peça) para a peça de índice `surface`. */
  push(surface, mark) {
    this.items.push({ surface, mark });
  }

  /** Tempo de jogo: um passo do esmaecimento a cada 1/rate s (dt × 12 = 0,1875 por tick: conta exata). */
  advance(dt) {
    this.acc += dt * FOOTPRINTS.fade.rate;
    while (this.acc >= 1) {
      this.acc -= 1;
      this.items.push(FADE);
    }
  }

  /**
   * Esvazia a fila no plano `plan` (createPlan): `fades` = passos do esmaecimento da pose; `stamps[i]` = as marcas da
   * peça i na ordem do jogo, cada uma com `fades` = os passos que vieram depois dela.
   */
  drain(plan) {
    for (const list of plan.stamps) list.length = 0;
    let after = 0;
    for (let i = this.items.length - 1; i >= 0; i--) {
      const it = this.items[i];
      if (it === FADE) after++;
      else {
        it.mark.fades = after;
        plan.stamps[it.surface].push(it.mark);
      }
    }
    for (const list of plan.stamps) list.reverse();
    plan.fades = after;
    this.items.length = 0;
    return plan;
  }

  /** Descarta a fila (limpeza das marcas, GPU reiniciada); o tempo do esmaecimento continua. */
  clear() {
    this.items.length = 0;
  }
}

/** Plano vazio para `surfaces` peças. */
export function createPlan(surfaces) {
  return { fades: 0, stamps: Array.from({ length: surfaces }, () => []) };
}

/**
 * Vida de uma peça (poses até a última marca viva dela sumir) depois de uma pose com `fades` passos e as marcas
 * `stamps` (cada uma com os passos que vieram depois dela). Peça com vida zero e sem marca nova não recebe desenho.
 */
export function surfaceLife(life, fades, stamps) {
  let next = Math.max(0, life - fades);
  for (const m of stamps) next = Math.max(next, markLife(m) - m.fades);
  return next;
}
```

- [ ] **Passo 5: A superfície e a escolha da placa**

```js file=src/clay/prints/surface.js
// Superfície de pegadas (subfase 3.5): uma peça de chão de massinha que o mapa declara (`printSurfaces`: id, malha,
// material, largura, profundidade e o topo no y do objeto) com o seu mapa de pegadas — um alvo de render RGBA8 com
// mipmaps no referencial da peça (o XZ do objeto, centrado): 4 texels/u com teto de 1024 por lado (a peça maior perde
// densidade por igual nos dois eixos) — ligado ao ClayMaterial dela (camada CLAY_PRINTS, src/clay/clayImprint.js).
// Uma marca cai na peça quando o retângulo dela encosta no da peça e o topo da peça está a até 4 u dos pés; o que passa
// da borda sai cortado. A peça é estática: a inversa da matriz de mundo é tirada uma vez.

import * as THREE from 'three';
import { FOOTPRINTS } from '../../data/footprints.js';
import { markBounds, toLocal } from './marks.js';

const FP = FOOTPRINTS;
const _bounds = [0, 0, 0, 0];

/** Tamanho do mapa de pegadas de uma peça de `width` × `depth` u: {width, height} em texels e os texels por u. */
export function surfaceSize(width, depth) {
  const texelsPerUnit = Math.min(FP.texelsPerUnit, FP.maxTexels / Math.max(width, depth));
  return {
    width: Math.max(1, Math.min(FP.maxTexels, Math.round(width * texelsPerUnit))),
    height: Math.max(1, Math.min(FP.maxTexels, Math.round(depth * texelsPerUnit))),
    texelsPerUnit,
  };
}

/**
 * A marca `m` (no mundo) no referencial da peça {inverse, width, depth, top} se ela cair ali: o y dos pés a até
 * `topTolerance` do topo e o retângulo da marca encostando no da peça. Senão null. Escreve em `out`.
 */
export function placeMark(surface, m, out = {}) {
  const l = toLocal(m, surface.inverse, out);
  if (Math.abs(l.y - surface.top) > FP.topTolerance) return null;
  const b = markBounds(l, _bounds);
  const hw = surface.width / 2;
  const hd = surface.depth / 2;
  if (b[2] < -hw || b[0] > hw || b[3] < -hd || b[1] > hd) return null;
  return l;
}

export class PrintSurface {
  /**
   * @param {{id: string, mesh: THREE.Mesh, material: import('../ClayMaterial.js').ClayMaterial, width: number,
   *   depth: number, top: number}} decl
   */
  constructor({ id, mesh, material, width, depth, top }) {
    this.id = id;
    this.mesh = mesh;
    this.material = material;
    this.width = width;
    this.depth = depth;
    this.top = top;
    // Peça de matriz fixa (matrixAutoUpdate desligado): a matriz de mundo é refeita à força uma vez.
    mesh.updateWorldMatrix(true, false, true);
    this.inverse = mesh.matrixWorld.clone().invert().elements.slice();
    this.size = surfaceSize(width, depth);
    this.target = new THREE.WebGLRenderTarget(this.size.width, this.size.height, {
      type: THREE.UnsignedByteType, format: THREE.RGBAFormat, depthBuffer: false, stencilBuffer: false,
      generateMipmaps: true, minFilter: THREE.LinearMipmapLinearFilter, magFilter: THREE.LinearFilter,
      wrapS: THREE.ClampToEdgeWrapping, wrapT: THREE.ClampToEdgeWrapping, colorSpace: THREE.NoColorSpace,
    });
    this.target.texture.name = `massacre.pegadas.${id}`;
    this.life = 0; // poses até a última marca viva sumir (0: mapa limpo, nada a desenhar)
    material.setPrints({
      map: this.target.texture, rect: [-width / 2, -depth / 2, width, depth], depth: FP.depth, lip: FP.lip,
    });
  }

  /** A marca no referencial desta peça, se cair nela (placeMark). */
  place(m, out) {
    return placeMark(this, m, out);
  }

  dispose() {
    this.material.setPrints(null);
    this.target.dispose();
  }
}
```

- [ ] **Passo 6: Rodar os testes da tarefa**

Run: `node --test tests/footprints.test.js`
Expected: PASS — 9 testes passando.

- [ ] **Passo 7: Suíte inteira**

Run: `npm test`
Expected: PASS — 288 testes passando.

- [ ] **Passo final: Commit** (só com o pedido do usuário)

```bash
git add src/clay/prints/marks.js src/clay/prints/printQueue.js src/clay/prints/surface.js tests/footprints.test.js
git commit -m "MASSACRE 3.5: marcas das pegadas, fila e escolha da placa" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Tarefa 5: Pegadas na GPU — o mapa de cada placa, o carimbo, o esmaecimento e o shader

**Files:**
- Create: `src/clay/clayImprint.js`, `src/clay/prints/stampPass.js`, `src/clay/prints/printSystem.js`
- Modify: `src/clay/ClayMaterial.js`, `src/maps/pista/visual/clayPlates.js`, `src/maps/pista/visual/index.js`, `src/maps/pista/index.js`, `src/modes/matchState.js`, `src/debug/commands.js`, `tests/footprints.test.js`

As camadas de impressão saem do `ClayMaterial` (554 linhas) para o `clayImprint.js`: a letra carimbada da 3.3 (`CLAY_IMPRINT`, sem mudar nada) e a camada nova `CLAY_PRINTS` — altura = 0,8 · G · (1 − R) − 4 · R, normal por 4 amostras somada à da letra, fundo 35% mais escuro e mais liso (−0,18 · R), mais liso ainda com a massa fresca (−0,14 · B · R), só na face de cima; os uniforms das duas camadas nascem com o material e nunca são trocados (o programa compilado lê os mesmos objetos), `setPrints` liga e desliga e a chave do programa ganha a camada. Cada placa declarada ganha um alvo RGBA8 com mipmaps; a passada é uma chamada de render por placa e pose: o esmaecimento da pose inteira (retângulo da placa com subtração reversa: n/255 no fundo e no lábio, 3n/255 no brilho) e depois todas as marcas numa malha instanciada (um retângulo por marca, mistura MAX), cada uma já esmaecida pelos passos que vieram depois dela, com o shader da marca gerado dos mesmos números do JS (`RawShaderMaterial` GLSL 3); o renderer volta ao alvo e ao `autoClear` de antes e o three refaz os mipmaps uma vez no fim. O sistema põe as marcas do tick na fila (vivo e fora do noclip), desenha na troca de pose só as placas com marca nova ou viva, limpa tudo (`pegadas limpar`, e a GPU reiniciada) com um esmaecimento de 255 passos e compila os dois programas ao montar. A pista declara as sete placas (`printSurfaces`: malha, material, largura, profundidade e o topo em h/2); o `MatchState` cria o sistema nos mapas que declaram placas, anda no tick, desenha na pose (junto com o corpo), esquece o sulco no teleporte e na volta e libera na saída.

- [ ] **Passo 1: Escrever os testes** — a superfície no `ClayMaterial` e o sistema com um renderer que só anota as chamadas.

Em `tests/footprints.test.js`, trocar:

```
// poses, o passo em 191) e a passada única por peça igual a aplicar a fila item a item; o tamanho dos alvos e o teto de
// 1024.
import { test } from 'node:test';
```

por:

```
// poses, o passo em 191) e a passada única por peça igual a aplicar a fila item a item; o tamanho dos alvos e o teto de
// 1024; e o sistema (uma chamada de render por peça com marca nova ou viva, limpeza, GPU reiniciada, liberação).
import { test } from 'node:test';
```

Em `tests/footprints.test.js`, trocar:

```
import * as THREE from 'three';
import { FOOTPRINTS, SOLE } from '../src/data/footprints.js';
```

por:

```
import * as THREE from 'three';
import { EV, EventBus } from '../src/core/events.js';
import { FOOTPRINTS, SOLE } from '../src/data/footprints.js';
```

Em `tests/footprints.test.js`, trocar:

```
import { PrintQueue, createPlan, surfaceLife } from '../src/clay/prints/printQueue.js';
import { placeMark, surfaceSize } from '../src/clay/prints/surface.js';
import { createMoveState } from '../src/player/movement.js';

```

por:

```
import { PrintQueue, createPlan, surfaceLife } from '../src/clay/prints/printQueue.js';
import { PrintSurface, placeMark, surfaceSize } from '../src/clay/prints/surface.js';
import { PrintSystem } from '../src/clay/prints/printSystem.js';
import { createMoveState, MOVETYPE } from '../src/player/movement.js';

```

Em `tests/footprints.test.js`, trocar:

```
  assert.equal(surfaceSize(2, 2).width, 8);
});

```

por:

```
  assert.equal(surfaceSize(2, 2).width, 8);
});

/** Renderer que só anota as chamadas (a GPU é conferida no navegador). */
function fakeRender() {
  const draws = [];
  const renderer = {
    autoClear: true,
    target: null,
    compiled: 0,
    compile() {
      this.compiled++;
    },
    getRenderTarget() {
      return this.target;
    },
    setRenderTarget(t) {
      this.target = t;
    },
    render(scene) {
      const [fadeMesh, stamps] = scene.children;
      draws.push({
        target: this.target, autoClear: this.autoClear, fade: fadeMesh.visible ? fadeMesh.material.uniforms.uFade.value.x * 255 : 0,
        stamps: stamps.visible ? stamps.geometry.instanceCount : 0,
      });
    },
  };
  return { contextLost: false, renderer, draws };
}

/** Jogador de mentira: estado de movimento, origem do começo do tick, eventos, olhar e vida. */
function fakePawn(x, y, z) {
  const state = createMoveState({ position: new THREE.Vector3(x, y, z) });
  state.onGround = true;
  return { state, prevOrigin: state.origin.clone(), env: { events: [] }, yaw: 0, vitals: { alive: true } };
}

test('sistema: uma chamada por peça com marca nova ou viva, esmaecimento no tempo do jogo, limpeza e liberação', () => {
  const render = fakeRender();
  const events = new EventBus();
  const decls = [plate(600, 1580, 3, 'P'), plate(400, 1580, -2, 'E')];
  const sys = new PrintSystem({ render, events, surfaces: decls });
  assert.equal(render.renderer.compiled, 1, 'programas compilados na montagem');
  assert.equal(render.draws.length, 2, 'montagem: cada mapa zerado (e os mipmaps)');
  assert.ok(render.draws.every((d) => d.fade === 255 && d.stamps === 0 && d.autoClear === false));
  assert.equal(render.renderer.autoClear, true, 'o autoClear volta');
  assert.ok(decls.every((d) => d.material.clayPrints && d.material.clayUniforms.uClayPrints.value.isRenderTargetTexture));
  render.draws.length = 0;
  const pawn = fakePawn(600, 5.3, 1580);
  pawn.env.events = [{ type: 'land', speed: 420 }];
  sys.tick(pawn, DT);
  pawn.env.events = [];
  for (let i = 0; i < 5; i++) sys.tick(pawn, DT);
  sys.onPose();
  assert.equal(render.draws.length, 1, 'só a placa P desenha');
  assert.equal(render.draws[0].target, sys.surfaces[0].target);
  assert.deepEqual([render.draws[0].fade, render.draws[0].stamps], [0, 2], 'mapa limpo: sem esmaecer; o par do pouso');
  assert.equal(sys.surfaces[0].life, 255 - 1, 'um passo do esmaecimento veio depois do pouso');
  // Poses sem marca nova: a placa viva só esmaece; a limpa não desenha.
  render.draws.length = 0;
  for (let i = 0; i < 6; i++) sys.tick(pawn, DT);
  sys.onPose();
  assert.equal(render.draws.length, 1);
  assert.deepEqual([render.draws[0].fade, render.draws[0].stamps], [1, 0]);
  // Até sumir: depois, nenhuma chamada.
  for (let i = 0; i < 64 * 22; i++) sys.tick(pawn, DT);
  sys.onPose();
  assert.equal(sys.surfaces[0].life, 0);
  render.draws.length = 0;
  for (let i = 0; i < 16; i++) sys.tick(pawn, DT);
  sys.onPose();
  assert.equal(render.draws.length, 0, 'placa sem marca viva não recebe desenho');
  // Morto ou no noclip: nada marca.
  pawn.env.events = [{ type: 'step', foot: 0, x: 600, y: 5.3, z: 1580 }];
  pawn.vitals.alive = false;
  sys.tick(pawn, DT);
  pawn.vitals.alive = true;
  pawn.state.moveType = MOVETYPE.NOCLIP;
  sys.tick(pawn, DT);
  assert.equal(sys.queue.items.filter((it) => it.mark).length, 0);
  pawn.state.moveType = MOVETYPE.WALK;
  sys.tick(pawn, DT);
  assert.equal(sys.info().queue > 0, true);
  assert.equal(sys.info().surfaces, 2);
  // Limpar: a fila sai e os dois mapas zeram; GPU reiniciada faz o mesmo; perdida, nada desenha.
  render.draws.length = 0;
  sys.clear();
  assert.equal(sys.queue.size, 0);
  assert.equal(render.draws.length, 2);
  render.contextLost = true;
  sys.tick(pawn, DT);
  sys.onPose();
  assert.equal(render.draws.length, 2, 'contexto perdido: sem desenho');
  render.contextLost = false;
  events.emit(EV.RENDER_CONTEXT, { lost: false });
  assert.equal(render.draws.length, 4, 'recuperado: mapas zerados de novo');
  let disposed = 0;
  for (const s of sys.surfaces) s.target.addEventListener('dispose', () => disposed++);
  sys.dispose();
  assert.equal(disposed, 2, 'alvos liberados');
  assert.ok(decls.every((d) => !d.material.clayPrints), 'materiais sem o mapa');
  events.emit(EV.RENDER_CONTEXT, { lost: false });
  assert.equal(render.draws.length, 4, 'depois de liberado não ouve mais a GPU');
});

test('superfície: o mapa cobre a peça inteira (centrada) no ClayMaterial, com a chave do programa', () => {
  const decl = plate(0, 0, 0, 'S');
  const key = decl.material.customProgramCacheKey();
  const s = new PrintSurface(decl);
  assert.deepEqual([s.target.width, s.target.height], [720, 520]);
  assert.equal(s.target.texture.generateMipmaps, true);
  assert.equal(s.target.depthBuffer, false);
  const u = decl.material.clayUniforms;
  assert.deepEqual(u.uClayPrintsRect.value.toArray(), [-90, -65, 180, 130]);
  assert.deepEqual(u.uClayPrintsDepth.value.toArray(), [FOOTPRINTS.depth, FOOTPRINTS.lip]);
  assert.notEqual(decl.material.customProgramCacheKey(), key, 'a camada entra na chave do programa');
  s.dispose();
  assert.equal(decl.material.customProgramCacheKey(), key);
});

```

- [ ] **Passo 2: Rodar e ver falhar**

Run: `node --test tests/footprints.test.js`
Expected: FAIL — o arquivo nem carrega: `ERR_MODULE_NOT_FOUND` (não acha `src/clay/prints/printSystem.js`).

- [ ] **Passo 3: As camadas de impressão fora do `ClayMaterial`** — no checkout, o `ClayMaterial.js` está com CRLF (`core.autocrlf`): os trechos abaixo casam em LF e o arquivo fica com LF, como o resto da árvore.

```js file=src/clay/clayImprint.js
// Camadas de impressão do ClayMaterial (tiradas de ClayMaterial.js na subfase 3.5), na face de cima da peça e mapeadas
// pelo XZ do objeto:
//  - CLAY_IMPRINT (3.3): textura de relevo fixa — R = fundo da marca, G = lábio de massa empurrada, B = marcas do rolo
//    — das letras carimbadas e dos furinhos das placas da pista (item 11 do moodboard: CIM1/CIM5/CIM8).
//  - CLAY_PRINTS (3.5): o mapa de pegadas vivo da peça (src/clay/prints/), um alvo de render — R = fundo (× `depth` u),
//    G = lábio (× `lip` u), B = massa fresca. Altura = lip · G · (1 − R) − depth · R: o lábio velho some onde uma marca
//    nova afunda (FIM3/FIM5). Fundo 35% mais escuro (o clayDeepen) e mais liso, mais liso ainda com a massa fresca
//    (FIM6/FIM7); o lábio pega mais luz.
// As duas deslocam a normal por diferença central de 4 amostras (a das pegadas somada à da letra) e entram na chave do
// programa como defines. As texturas são de quem chama (o mapa e o sistema de pegadas as liberam).

import * as THREE from 'three';

/** Uniforms e variáveis das camadas (antes das funções do fragment). */
export const IMPRINT_PARS_GLSL = /* glsl */ `
#ifdef CLAY_IMPRINT
uniform sampler2D uClayImprint;
uniform vec4 uClayImprintRect;
uniform vec3 uClayImprintDepth;
uniform vec2 uClayImprintTexel;
#endif
#ifdef CLAY_PRINTS
uniform sampler2D uClayPrints;
uniform vec4 uClayPrintsRect;
uniform vec2 uClayPrintsDepth;
uniform vec2 uClayPrintsTexel;
float clayPrintHeight(vec4 c) {
  return uClayPrintsDepth.y * c.g * (1.0 - c.r) - uClayPrintsDepth.x * c.r;
}
#endif
float clayImprintMask = 0.0;
float clayPrintMask = 0.0;
float clayPrintFresh = 0.0;
`;

/** As duas camadas no fragment, depois do albedo e das digitais (mexem em clayObjN e diffuseColor). */
export const IMPRINT_SAMPLE_GLSL = /* glsl */ `
#ifdef CLAY_IMPRINT
{
  // uv da impressão pelo XZ do objeto (retângulo com largura negativa = espelhado); só a face de cima recebe.
  vec2 iuv = (vClayPos.xz - uClayImprintRect.xy) / uClayImprintRect.zw;
  float top = smoothstep(0.6, 0.9, clayN.y) * step(0.0, iuv.x) * step(iuv.x, 1.0) * step(0.0, iuv.y) * step(iuv.y, 1.0);
  vec3 hw = vec3(-uClayImprintDepth.x, uClayImprintDepth.y, uClayImprintDepth.z);
  vec2 tx = uClayImprintTexel;
  vec4 c0 = texture(uClayImprint, iuv);
  float hL = dot(texture(uClayImprint, iuv - vec2(tx.x, 0.0)).rgb, hw);
  float hR = dot(texture(uClayImprint, iuv + vec2(tx.x, 0.0)).rgb, hw);
  float hD = dot(texture(uClayImprint, iuv - vec2(0.0, tx.y)).rgb, hw);
  float hU = dot(texture(uClayImprint, iuv + vec2(0.0, tx.y)).rgb, hw);
  // Diferença central em u do objeto (o sinal do retângulo cuida do espelhamento).
  float dhdx = (hR - hL) / (2.0 * uClayImprintRect.z * tx.x);
  float dhdz = (hU - hD) / (2.0 * uClayImprintRect.w * tx.y);
  clayObjN = normalize(clayObjN + vec3(-dhdx, 0.0, -dhdz) * top);
  // Fundo da marca: massa comprimida, mais escura e mais lisa (o carimbo alisa); o lábio pega mais luz.
  clayImprintMask = c0.r * top;
  diffuseColor.rgb = mix(diffuseColor.rgb, clayDeepen(diffuseColor.rgb), clayImprintMask * 0.35);
  diffuseColor.rgb *= 1.0 + c0.g * top * 0.04;
}
#endif
#ifdef CLAY_PRINTS
{
  // Pegadas: o mapa cobre a peça inteira no XZ do objeto (centrado); só a face de cima recebe.
  vec2 puv = (vClayPos.xz - uClayPrintsRect.xy) / uClayPrintsRect.zw;
  float ptop = smoothstep(0.6, 0.9, clayN.y) * step(0.0, puv.x) * step(puv.x, 1.0)
    * step(0.0, puv.y) * step(puv.y, 1.0);
  vec2 ptx = uClayPrintsTexel;
  vec4 p0 = texture(uClayPrints, puv);
  float pL = clayPrintHeight(texture(uClayPrints, puv - vec2(ptx.x, 0.0)));
  float pR = clayPrintHeight(texture(uClayPrints, puv + vec2(ptx.x, 0.0)));
  float pD = clayPrintHeight(texture(uClayPrints, puv - vec2(0.0, ptx.y)));
  float pU = clayPrintHeight(texture(uClayPrints, puv + vec2(0.0, ptx.y)));
  float pdx = (pR - pL) / (2.0 * uClayPrintsRect.z * ptx.x);
  float pdz = (pU - pD) / (2.0 * uClayPrintsRect.w * ptx.y);
  clayObjN = normalize(clayObjN + vec3(-pdx, 0.0, -pdz) * ptop);
  clayPrintMask = p0.r * ptop;
  clayPrintFresh = p0.b * ptop;
  diffuseColor.rgb = mix(diffuseColor.rgb, clayDeepen(diffuseColor.rgb), clayPrintMask * 0.35);
  diffuseColor.rgb *= 1.0 + p0.g * (1.0 - p0.r) * ptop * 0.04;
}
#endif
`;

/** Rugosidade: o fundo das marcas alisa; as pegadas frescas alisam mais. */
export const IMPRINT_ROUGHNESS_GLSL = /* glsl */ `
roughnessFactor = clamp(roughnessFactor - clayImprintMask * 0.18
  - clayPrintMask * (0.18 + 0.14 * clayPrintFresh), 0.2, 1.0);
`;

/**
 * Objetos de uniform das duas camadas, criados com o material e nunca trocados: o programa compilado lê os mesmos
 * objetos, então ligar, trocar ou desligar uma camada mexe só nos valores (com a define desligada, o three os ignora).
 */
export function imprintUniforms() {
  return {
    uClayImprint: { value: null },
    uClayImprintRect: { value: new THREE.Vector4() },
    uClayImprintDepth: { value: new THREE.Vector3() },
    uClayImprintTexel: { value: new THREE.Vector2() },
    uClayPrints: { value: null },
    uClayPrintsRect: { value: new THREE.Vector4() },
    uClayPrintsDepth: { value: new THREE.Vector2() },
    uClayPrintsTexel: { value: new THREE.Vector2() },
  };
}

/** Largura e altura em texels de uma textura ou de um alvo de render (fallback 512). */
function texelSize(map) {
  const img = map.image;
  return [1 / (img?.width ?? 512), 1 / (img?.height ?? 512)];
}

/**
 * Liga (ou troca) a impressão fixa: `map` com R = fundo, G = lábio, B = rolo; `rect` = [x0, z0, largura, profundidade]
 * no XZ do objeto (largura negativa espelha); `depth`/`lip`/`roller` em u. Devolve se o define mudou.
 */
export function applyImprint(material, { map, rect, depth = 1.6, lip = 0.35, roller = 0.08 }) {
  const u = material.clayUniforms;
  u.uClayImprint.value = map;
  u.uClayImprintRect.value.set(rect[0], rect[1], rect[2], rect[3]);
  u.uClayImprintDepth.value.set(depth, lip, roller);
  u.uClayImprintTexel.value.set(...texelSize(map));
  material.clay.imprint = { map, rect: [...rect], depth, lip, roller };
  const changed = !material.clayImprint;
  material.clayImprint = true;
  return changed;
}

/**
 * Liga (ou troca) o mapa de pegadas: `map` (textura do alvo de render) com R = fundo, G = lábio, B = massa fresca;
 * `rect` = [x0, z0, largura, profundidade] no XZ do objeto; `depth`/`lip` em u. Devolve se o define mudou.
 */
export function applyPrints(material, { map, rect, depth, lip }) {
  const u = material.clayUniforms;
  u.uClayPrints.value = map;
  u.uClayPrintsRect.value.set(rect[0], rect[1], rect[2], rect[3]);
  u.uClayPrintsDepth.value.set(depth, lip);
  u.uClayPrintsTexel.value.set(...texelSize(map));
  const changed = !material.clayPrints;
  material.clayPrints = true;
  return changed;
}

/** Desliga o mapa de pegadas (o alvo de render foi liberado). Devolve se o define mudou. */
export function removePrints(material) {
  if (!material.clayPrints) return false;
  material.clayUniforms.uClayPrints.value = null;
  material.clayPrints = false;
  return true;
}
```

Em `src/clay/ClayMaterial.js`, trocar:

```
//  - Skins procedurais (src/data/claySkins.js) por define.
//  - Impressão (opcional, define CLAY_IMPRINT): textura de relevo na face de cima — R = fundo da marca, G = lábio de
//    massa empurrada, B = marcas do rolo — mapeada pelo XZ do objeto; desloca a normal (4 amostras) e escurece e alisa o
//    fundo. Letras carimbadas e furinhos das placas da pista (3.3); as pegadas da 3.5 vêm pelo mesmo caminho.

```

por:

```
//  - Skins procedurais (src/data/claySkins.js) por define.
//  - Impressões na face de cima, mapeadas pelo XZ do objeto (src/clay/clayImprint.js): a fixa (define CLAY_IMPRINT —
//    letras carimbadas e furinhos das placas da pista, 3.3) e o mapa de pegadas vivo (define CLAY_PRINTS, 3.5);
//    deslocam a normal e escurecem e alisam o fundo das marcas.

```

Em `src/clay/ClayMaterial.js`, trocar:

```
import { objectSpaceVaryings, objectSpaceVertex, TRIPLANAR_GLSL } from '../render/glsl/objectSpace.js';

```

por:

```
import { objectSpaceVaryings, objectSpaceVertex, TRIPLANAR_GLSL } from '../render/glsl/objectSpace.js';
import {
  IMPRINT_PARS_GLSL, IMPRINT_ROUGHNESS_GLSL, IMPRINT_SAMPLE_GLSL, applyImprint, applyPrints, imprintUniforms,
  removePrints,
} from './clayImprint.js';

```

Em `src/clay/ClayMaterial.js`, trocar:

```
uniform vec4 uClayProbe;
#ifdef CLAY_IMPRINT
uniform sampler2D uClayImprint;
uniform vec4 uClayImprintRect;
uniform vec3 uClayImprintDepth;
uniform vec2 uClayImprintTexel;
#endif
float clayImprintMask = 0.0;
${objectSpaceVaryings('Clay')}
```

por:

```
uniform vec4 uClayProbe;
${IMPRINT_PARS_GLSL}
${objectSpaceVaryings('Clay')}
```

Em `src/clay/ClayMaterial.js`, trocar:

```
}
#ifdef CLAY_IMPRINT
{
  // uv da impressão pelo XZ do objeto (retângulo com largura negativa = espelhado); só a face de cima recebe.
  vec2 iuv = (vClayPos.xz - uClayImprintRect.xy) / uClayImprintRect.zw;
  float top = smoothstep(0.6, 0.9, clayN.y) * step(0.0, iuv.x) * step(iuv.x, 1.0) * step(0.0, iuv.y) * step(iuv.y, 1.0);
  vec3 hw = vec3(-uClayImprintDepth.x, uClayImprintDepth.y, uClayImprintDepth.z);
  vec2 tx = uClayImprintTexel;
  vec4 c0 = texture(uClayImprint, iuv);
  float hL = dot(texture(uClayImprint, iuv - vec2(tx.x, 0.0)).rgb, hw);
  float hR = dot(texture(uClayImprint, iuv + vec2(tx.x, 0.0)).rgb, hw);
  float hD = dot(texture(uClayImprint, iuv - vec2(0.0, tx.y)).rgb, hw);
  float hU = dot(texture(uClayImprint, iuv + vec2(0.0, tx.y)).rgb, hw);
  // Diferença central em u do objeto (o sinal do retângulo cuida do espelhamento).
  float dhdx = (hR - hL) / (2.0 * uClayImprintRect.z * tx.x);
  float dhdz = (hU - hD) / (2.0 * uClayImprintRect.w * tx.y);
  clayObjN = normalize(clayObjN + vec3(-dhdx, 0.0, -dhdz) * top);
  // Fundo da marca: massa comprimida, mais escura e mais lisa (o carimbo alisa); o lábio pega mais luz.
  clayImprintMask = c0.r * top;
  diffuseColor.rgb = mix(diffuseColor.rgb, clayDeepen(diffuseColor.rgb), clayImprintMask * 0.35);
  diffuseColor.rgb *= 1.0 + c0.g * top * 0.04;
}
#endif
`;

```

por:

```
}
${IMPRINT_SAMPLE_GLSL}`;

```

Em `src/clay/ClayMaterial.js`, trocar:

```
roughnessFactor = mix(roughnessFactor, 0.16, claySkinFlake);
roughnessFactor = clamp(roughnessFactor - clayImprintMask * 0.18, 0.2, 1.0);
`;

```

por:

```
roughnessFactor = mix(roughnessFactor, 0.16, claySkinFlake);
${IMPRINT_ROUGHNESS_GLSL}`;

```

Em `src/clay/ClayMaterial.js`, trocar:

```
clayGeomN = normal;
#if defined(CLAY_FINGERPRINTS) || CLAY_SKIN == 2 || defined(CLAY_IMPRINT)
  normal = normalize(vClayAx * clayObjN.x + vClayAy * clayObjN.y + vClayAz * clayObjN.z);
```

por:

```
clayGeomN = normal;
#if defined(CLAY_FINGERPRINTS) || CLAY_SKIN == 2 || defined(CLAY_IMPRINT) || defined(CLAY_PRINTS)
  normal = normalize(vClayAx * clayObjN.x + vClayAy * clayObjN.y + vClayAz * clayObjN.z);
```

Em `src/clay/ClayMaterial.js`, trocar:

```
      uClaySkinParams: { value: new THREE.Vector4(...skin.params) },
    };
    this.clayImprint = false;
    if (p.imprint) this.setImprint(p.imprint);
    this.customProgramCacheKey = () =>
      `clay:${this.skinId}:${clayFlags.fingerprints ? 1 : 0}:${clayFlags.boil ? 1 : 0}:${clayFlags.blackProbe ? 1 : 0}:${this.clayImprint ? 1 : 0}`;
    this.onBeforeCompile = (shader) => this.#patch(shader);
```

por:

```
      uClaySkinParams: { value: new THREE.Vector4(...skin.params) },
      ...imprintUniforms(),
    };
    this.clayImprint = false;
    this.clayPrints = false; // mapa de pegadas ligado (setPrints)
    if (p.imprint) this.setImprint(p.imprint);
    const bit = (v) => (v ? 1 : 0);
    this.customProgramCacheKey = () => `clay:${this.skinId}:${bit(clayFlags.fingerprints)}:${bit(clayFlags.boil)}:`
      + `${bit(clayFlags.blackProbe)}:${bit(this.clayImprint)}:${bit(this.clayPrints)}`;
    this.onBeforeCompile = (shader) => this.#patch(shader);
```

Em `src/clay/ClayMaterial.js`, trocar:

```
    if (this.clayImprint) shader.defines.CLAY_IMPRINT = '';
    shader.vertexShader = shader.vertexShader
```

por:

```
    if (this.clayImprint) shader.defines.CLAY_IMPRINT = '';
    if (this.clayPrints) shader.defines.CLAY_PRINTS = '';
    shader.vertexShader = shader.vertexShader
```

Em `src/clay/ClayMaterial.js`, trocar:

```
   */
  setImprint({ map, rect, depth = 1.6, lip = 0.35, roller = 0.08 }) {
    const had = this.clayImprint;
    const u = this.clayUniforms;
    // Os objetos de uniform são os mesmos que o programa compilado lê: troca só o valor.
    if (!u.uClayImprint) {
      u.uClayImprint = { value: null };
      u.uClayImprintRect = { value: new THREE.Vector4() };
      u.uClayImprintDepth = { value: new THREE.Vector3() };
      u.uClayImprintTexel = { value: new THREE.Vector2() };
    }
    const img = map.image;
    u.uClayImprint.value = map;
    u.uClayImprintRect.value.set(rect[0], rect[1], rect[2], rect[3]);
    u.uClayImprintDepth.value.set(depth, lip, roller);
    u.uClayImprintTexel.value.set(1 / (img?.width ?? 512), 1 / (img?.height ?? 512));
    this.clay.imprint = { map, rect: [...rect], depth, lip, roller };
    this.clayImprint = true;
    if (!had) this.needsUpdate = true;
    return this;
```

por:

```
   */
  setImprint(imprint) {
    if (applyImprint(this, imprint)) this.needsUpdate = true;
    return this;
  }

  /**
   * Liga (ou troca) o mapa de pegadas: `map` (a textura do alvo de render) com R = fundo, G = lábio, B = massa fresca;
   * `rect` = [x0, z0, largura, profundidade] no XZ do objeto; `depth`/`lip` em u. null desliga. O alvo é de quem chama
   * (o sistema de pegadas, src/clay/prints/).
   */
  setPrints(prints) {
    if (prints ? applyPrints(this, prints) : removePrints(this)) this.needsUpdate = true;
    return this;
```

Em `src/clay/ClayMaterial.js`, trocar:

```
      this.clayImprint = source.clayImprint;
    }
```

por:

```
      this.clayImprint = source.clayImprint;
      this.clayPrints = source.clayPrints;
    }
```

- [ ] **Passo 4: A passada e o sistema**

```js file=src/clay/prints/stampPass.js
// Passadas do mapa de pegadas (subfase 3.5): numa chamada de render por peça e pose, primeiro o esmaecimento da pose
// inteira — um retângulo da peça toda com subtração reversa (n/255 no fundo e no lábio, 3n/255 no brilho) — e depois as
// marcas novas, todas numa malha instanciada: um retângulo por marca no referencial da peça, com mistura MAX por canal
// (fica a marca mais funda; o lábio velho some onde a nova afunda, no shader da massinha), cada uma já esmaecida pelos
// passos que vieram depois dela na fila (src/clay/prints/printQueue.js). O three refaz os mipmaps do alvo no fim da
// chamada, uma vez. A conta de cada texel é a de markTexel (src/clay/prints/marks.js), em GLSL dos mesmos números.

import * as THREE from 'three';
import { FOOTPRINTS, SOLE } from '../../data/footprints.js';
import { SOLE_GLSL, glslFloat as f } from './sole.js';
import { markBounds } from './marks.js';

const FP = FOOTPRINTS;
const LR = FP.lipRing;
const FADE = FP.fade;

const FADE_VERT = /* glsl */ `
precision highp float;
in vec3 position;
void main() {
  gl_Position = vec4(position.xy * 2.0 - 1.0, 0.0, 1.0);
}
`;

const FADE_FRAG = /* glsl */ `
precision highp float;
uniform vec3 uFade;
out vec4 fragColor;
void main() {
  fragColor = vec4(uFade, 0.0);
}
`;

const STAMP_VERT = /* glsl */ `
precision highp float;
in vec3 position;
in vec4 iBounds; // retângulo da marca no XZ da peça: x0, z0, x1, z1
in vec4 iPose; // x, z, dx, dz
in vec4 iShape; // tipo, força, passos do esmaecimento depois dela, lado de dentro
in vec4 iExtra; // calcanhar, frente, comprimento (sulco), meia largura (sulco) ou raio (montinho)
uniform vec4 uRect; // a peça: x0, z0, largura, profundidade
out vec2 vP;
flat out vec4 vPose;
flat out vec4 vShape;
flat out vec4 vExtra;
void main() {
  vec2 p = mix(iBounds.xy, iBounds.zw, position.xy);
  vP = p;
  vPose = iPose;
  vShape = iShape;
  vExtra = iExtra;
  gl_Position = vec4((p - uRect.xy) / uRect.zw * 2.0 - 1.0, 0.0, 1.0);
}
`;

const STAMP_FRAG = /* glsl */ `
precision highp float;
in vec2 vP;
flat in vec4 vPose;
flat in vec4 vShape;
flat in vec4 vExtra;
out vec4 fragColor;
${SOLE_GLSL}
float q8(float v) {
  return floor(clamp(v, 0.0, 1.0) * 255.0 + 0.5);
}
float lipRing(float d) {
  float t = (d - ${f(LR.offset)}) / ${f(LR.width)};
  return exp(-t * t);
}
void main() {
  vec2 p = vP - vPose.xy;
  vec2 dir = vPose.zw;
  float kind = vShape.x;
  float strength = vShape.y;
  float r = 0.0;
  float g = 0.0;
  float b = 0.0;
  if (kind < 0.5) {
    // Pé: a sola no referencial dele (a ao longo, bi para o lado de dentro).
    float peak = clamp(strength * max(vExtra.x, vExtra.y), 0.0, 1.0);
    float a = dot(p, dir);
    float bi = (p.y * dir.x - p.x * dir.y) * vShape.w;
    float d = soleDistance(vec2(a, bi));
    float push = vExtra.x + (vExtra.y - vExtra.x) * smoothstep(${f(SOLE.heel.a)}, ${f(SOLE.toe.a)}, a);
    r = smoothstep(0.0, ${f(FP.wall)}, -d) * soleCleats(vec2(a, bi)) * strength * push;
    if (d > 0.0) {
      float front = 1.0 + ${f(LR.front)} * smoothstep(${f(LR.frontFrom)}, ${f(LR.frontTo)}, a);
      g = min(peak, lipRing(d) * front * strength * ${f(LR.gain)});
    }
    b = d < ${f(FP.freshReach)} ? 1.0 : 0.0;
  } else if (kind < 1.5) {
    // Sulco do slide: cápsula ao longo do segmento.
    float peak = clamp(strength, 0.0, 1.0);
    float t = min(vExtra.z, max(0.0, dot(p, dir)));
    float d = length(p - dir * t) - vExtra.w;
    r = smoothstep(0.0, ${f(FP.wall)}, -d) * strength;
    if (d > 0.0) g = min(peak, lipRing(d) * strength * ${f(LR.gain)});
    b = d < ${f(FP.freshReach)} ? 1.0 : 0.0;
  } else {
    // Montinho: só lábio.
    float k = 1.0 - dot(p, p) / (vExtra.w * vExtra.w);
    if (k > 0.0) {
      g = strength * k * k;
      b = 1.0;
    }
  }
  vec3 q = vec3(q8(r), q8(g), q8(b)) - vShape.z * vec3(${f(FADE.depth)}, ${f(FADE.lip)}, ${f(FADE.fresh)});
  fragColor = vec4(max(q, 0.0) / 255.0, 0.0);
}
`;

/** Retângulo unitário (dois triângulos). */
function unitQuad(geometry) {
  geometry.setAttribute('position', new THREE.Float32BufferAttribute([0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 1, 0], 3));
  geometry.setIndex([0, 1, 2, 0, 2, 3]);
  return geometry;
}

const INSTANCE_ATTRIBUTES = ['iBounds', 'iPose', 'iShape', 'iExtra'];
const _bounds = [0, 0, 0, 0];

export class StampPass {
  constructor(capacity = 64) {
    this.scene = new THREE.Scene();
    this.scene.name = 'pegadas';
    this.camera = new THREE.OrthographicCamera();
    const common = { glslVersion: THREE.GLSL3, depthTest: false, depthWrite: false, blending: THREE.CustomBlending };
    this.fadeMaterial = new THREE.RawShaderMaterial({
      ...common, name: 'pegadas-esmaecer', vertexShader: FADE_VERT, fragmentShader: FADE_FRAG,
      uniforms: { uFade: { value: new THREE.Vector3() } },
      blendEquation: THREE.ReverseSubtractEquation, blendSrc: THREE.OneFactor, blendDst: THREE.OneFactor,
    });
    this.stampMaterial = new THREE.RawShaderMaterial({
      ...common, name: 'pegadas-carimbo', vertexShader: STAMP_VERT, fragmentShader: STAMP_FRAG,
      uniforms: { uRect: { value: new THREE.Vector4() } },
      blendEquation: THREE.MaxEquation, blendSrc: THREE.OneFactor, blendDst: THREE.OneFactor,
    });
    this.fade = new THREE.Mesh(unitQuad(new THREE.BufferGeometry()), this.fadeMaterial);
    this.fade.frustumCulled = false;
    this.fade.renderOrder = 0;
    this.stamps = new THREE.Mesh(this.#geometry(capacity), this.stampMaterial);
    this.stamps.frustumCulled = false;
    this.stamps.renderOrder = 1;
    this.scene.add(this.fade, this.stamps);
  }

  /** Geometria instanciada com lugar para `capacity` marcas. */
  #geometry(capacity) {
    const geo = unitQuad(new THREE.InstancedBufferGeometry());
    for (const name of INSTANCE_ATTRIBUTES) {
      const attr = new THREE.InstancedBufferAttribute(new Float32Array(capacity * 4), 4);
      attr.setUsage(THREE.DynamicDrawUsage);
      geo.setAttribute(name, attr);
    }
    geo.instanceCount = 0;
    this.capacity = capacity;
    return geo;
  }

  /** Compila os dois programas (ao montar o mapa, e não no primeiro passo). */
  compile(renderer) {
    renderer.compile(this.scene, this.camera);
  }

  /** Enche as instâncias com as marcas (no referencial da peça, cada uma com `fades`). */
  #fill(marks) {
    if (marks.length > this.capacity) {
      let n = this.capacity;
      while (n < marks.length) n *= 2;
      this.stamps.geometry.dispose();
      this.stamps.geometry = this.#geometry(n);
    }
    const geo = this.stamps.geometry;
    const [bounds, pose, shape, extra] = INSTANCE_ATTRIBUTES.map((k) => geo.attributes[k]);
    for (let i = 0; i < marks.length; i++) {
      const m = marks[i];
      markBounds(m, _bounds);
      bounds.setXYZW(i, _bounds[0], _bounds[1], _bounds[2], _bounds[3]);
      pose.setXYZW(i, m.x, m.z, m.dx, m.dz);
      shape.setXYZW(i, m.kind, m.strength, m.fades ?? 0, m.inner ?? 1);
      extra.setXYZW(i, m.heel ?? 1, m.front ?? 1, m.length ?? 0, m.halfWidth ?? m.radius ?? 0);
    }
    for (const attr of [bounds, pose, shape, extra]) {
      attr.clearUpdateRanges();
      attr.addUpdateRange(0, marks.length * 4);
      attr.needsUpdate = true;
    }
    geo.instanceCount = marks.length;
  }

  /**
   * Uma chamada de render no alvo `target` da peça de `width` × `depth` u (centrada): `fades` passos do esmaecimento e
   * as marcas `marks`. O alvo e o autoClear do renderer voltam ao que eram.
   */
  draw(renderer, target, width, depth, fades, marks) {
    this.fade.visible = fades > 0;
    const step = (rate) => Math.min(1, (fades * rate) / 255);
    this.fadeMaterial.uniforms.uFade.value.set(step(FADE.depth), step(FADE.lip), step(FADE.fresh));
    this.stamps.visible = marks.length > 0;
    if (marks.length) this.#fill(marks);
    this.stampMaterial.uniforms.uRect.value.set(-width / 2, -depth / 2, width, depth);
    const previous = renderer.getRenderTarget();
    const autoClear = renderer.autoClear;
    renderer.autoClear = false;
    renderer.setRenderTarget(target);
    renderer.render(this.scene, this.camera);
    renderer.setRenderTarget(previous);
    renderer.autoClear = autoClear;
  }

  dispose() {
    this.fade.geometry.dispose();
    this.stamps.geometry.dispose();
    this.fadeMaterial.dispose();
    this.stampMaterial.dispose();
  }
}
```

```js file=src/clay/prints/printSystem.js
// Sistema das pegadas (subfase 3.5; desenho em docs/phases/phase-3.md, seção 3.5; números em src/data/footprints.js):
// liga as peças de chão de massinha que o mapa declara (`printSurfaces`) aos mapas de pegadas delas e, a cada tick do
// jogador, põe na fila as marcas do tick (src/clay/prints/marks.js: passo, pouso, pulo, sulcos e montinho do slide) nas
// peças onde elas caem, com os passos do esmaecimento no tempo do jogo. Na troca de pose do render (EV.POSE, junto com
// o boil) a fila vira desenho: uma chamada por peça com marca nova ou viva (src/clay/prints/stampPass.js); peça sem
// marca viva não recebe desenho. GPU reiniciada (EV.RENDER_CONTEXT) limpa as marcas; `dispose` libera os alvos.
// Console: `pegadas` e `pegadas limpar` (src/debug/commands.js).

import { EV } from '../../core/events.js';
import { FOOTPRINTS } from '../../data/footprints.js';
import { MOVETYPE } from '../../player/movement.js';
import { createPrintTrack, resetPrintTrack, tickMarks } from './marks.js';
import { PrintQueue, createPlan, surfaceLife } from './printQueue.js';
import { PrintSurface } from './surface.js';
import { StampPass } from './stampPass.js';

/** Esmaecimento que zera qualquer mapa (o brilho, o canal mais rápido, também). */
const CLEAR_FADES = 255;

export class PrintSystem {
  /**
   * @param {{render: import('../../render/renderSystem.js').RenderSystem,
   *   events: import('../../core/events.js').EventBus,
   *   surfaces: Array<{id: string, mesh: import('three').Mesh, material: import('../ClayMaterial.js').ClayMaterial,
   *   width: number, depth: number, top: number}>}} opts
   */
  constructor({ render, events, surfaces }) {
    this.render = render;
    this.surfaces = surfaces.map((decl) => new PrintSurface(decl));
    this.queue = new PrintQueue();
    this.plan = createPlan(this.surfaces.length);
    this.pass = new StampPass();
    this.track = createPrintTrack();
    this._marks = [];
    this._local = {};
    this.counts = { marks: 0, draws: 0 }; // marcas postas na fila e chamadas de render desde a montagem
    this._off = events.on(EV.RENDER_CONTEXT, ({ lost }) => {
      if (!lost) this.clear();
    });
    if (!render.contextLost) this.pass.compile(render.renderer);
    this.clear();
  }

  /**
   * Um tick, depois do tick do jogador (`pawn`): o tempo do esmaecimento anda e as marcas do tick entram na fila de
   * cada peça em que caem. Morto ou no noclip, nada marca.
   */
  tick(pawn, dt) {
    this.queue.advance(dt);
    const s = pawn.state;
    if (!pawn.vitals.alive || s.moveType === MOVETYPE.NOCLIP) {
      resetPrintTrack(this.track);
      return;
    }
    const marks = tickMarks(this.track, s, pawn.prevOrigin, pawn.env.events, pawn.yaw, this._marks);
    for (const m of marks) {
      for (let i = 0; i < this.surfaces.length; i++) {
        const local = this.surfaces[i].place(m, this._local);
        if (!local) continue;
        this.queue.push(i, { ...local });
        this.counts.marks++;
      }
    }
  }

  /** Volta ao jogo e teleporte: o sulco do slide não continua de onde parou. */
  reset() {
    resetPrintTrack(this.track);
  }

  /** Troca de pose (EV.POSE): a fila vira desenho, uma chamada por peça com marca nova ou viva. */
  onPose() {
    const plan = this.queue.drain(this.plan);
    if (this.render.contextLost) return;
    const renderer = this.render.renderer;
    for (let i = 0; i < this.surfaces.length; i++) {
      const surface = this.surfaces[i];
      const stamps = plan.stamps[i];
      if (!stamps.length && surface.life <= 0) continue;
      const fades = surface.life > 0 ? plan.fades : 0;
      this.pass.draw(renderer, surface.target, surface.width, surface.depth, fades, stamps);
      surface.life = surfaceLife(surface.life, plan.fades, stamps);
      this.counts.draws++;
    }
  }

  /** Apaga todas as marcas (e a fila): o mapa de cada peça volta a zero, com os mipmaps. */
  clear() {
    this.queue.clear();
    resetPrintTrack(this.track);
    for (const surface of this.surfaces) surface.life = 0;
    if (this.render.contextLost) return;
    for (const surface of this.surfaces) {
      this.pass.draw(this.render.renderer, surface.target, surface.width, surface.depth, CLEAR_FADES, []);
    }
  }

  /**
   * Para o console: peças, peças com marca viva (e os segundos de jogo até a última sumir), itens na fila, marcas e
   * desenhos desde a montagem e a memória dos mapas (com os mipmaps).
   */
  info() {
    const live = this.surfaces.filter((s) => s.life > 0);
    const bytes = this.surfaces.reduce((sum, s) => sum + (s.size.width * s.size.height * 4 * 4) / 3, 0);
    return {
      surfaces: this.surfaces.length,
      live: live.map((s) => ({ id: s.id, seconds: s.life / FOOTPRINTS.fade.rate })),
      queue: this.queue.size,
      marks: this.counts.marks,
      draws: this.counts.draws,
      megabytes: bytes / (1024 * 1024),
    };
  }

  dispose() {
    this._off();
    this.pass.dispose();
    for (const surface of this.surfaces) surface.dispose();
    this.surfaces = [];
  }
}
```

- [ ] **Passo 5: As placas da pista como superfícies de pegadas**

Em `src/maps/pista/visual/clayPlates.js`, trocar:

```
// carimbadas e borda de furinhos): as sete placas das pegadas, cada uma com a letra carimbada, a borda de furinhos e as
// marcas do rolo numa textura de impressão própria (o ClayMaterial desloca a normal por ela; a 3.5 põe as pegadas pelo
// mesmo caminho), e as bolotas que seguram as pontas das traves do slide e o palito da bandeirinha, numa malha só com
// a cor por vértice.

```

por:

```
// carimbadas e borda de furinhos): as sete placas das pegadas, cada uma com a letra carimbada, a borda de furinhos e as
// marcas do rolo numa textura de impressão própria (o ClayMaterial desloca a normal por ela), declaradas como
// superfícies de pegadas (`printSurfaces`, subfase 3.5: o mapa de pegadas vivo de cada uma, src/clay/prints/), e as
// bolotas que seguram as pontas das traves do slide e o palito da bandeirinha, numa malha só com a cor por vértice.

```

Em `src/maps/pista/visual/clayPlates.js`, trocar:

```
  let plates = 0;
  for (const p of layout.pieces) {
    if (p.look.kind !== 'clayPlate') continue;
    const [w, , d] = p.size;
    const map = imprintTexture(p.look.letter, [w, d], p.look.seed);
```

por:

```
  let plates = 0;
  const printSurfaces = [];
  for (const p of layout.pieces) {
    if (p.look.kind !== 'clayPlate') continue;
    const [w, h, d] = p.size;
    const map = imprintTexture(p.look.letter, [w, d], p.look.seed);
```

Em `src/maps/pista/visual/clayPlates.js`, trocar:

```
    material.setObjectSize(Math.hypot(w, d) / 2);
    group.add(placeMesh(new THREE.Mesh(plateGeometry(p.size, p.look.seed), material), p.matrix, { name: p.id }));
    plates++;
```

por:

```
    material.setObjectSize(Math.hypot(w, d) / 2);
    const mesh = placeMesh(new THREE.Mesh(plateGeometry(p.size, p.look.seed), material), p.matrix, { name: p.id });
    group.add(mesh);
    // Pegadas: o topo da placa (centrada na altura) fica em h/2 no y do objeto.
    printSurfaces.push({ id: p.id, mesh, material, width: w, depth: d, top: h / 2 });
    plates++;
```

Em `src/maps/pista/visual/clayPlates.js`, trocar:

```
  }
  return { plates, lumps: parts.length };
}
```

por:

```
  }
  return { plates, lumps: parts.length, printSurfaces };
}
```

Em `src/maps/pista/visual/index.js`, trocar:

```
// malhas próprias. Devolve o grupo, as contagens (draws e triângulos, para o aceite) e o dispose das texturas do mapa
// (os materiais são da biblioteca do set e saem em set.releaseMaterials()).

```

por:

```
// malhas próprias. Devolve o grupo, as contagens (draws e triângulos, para o aceite) e o dispose das texturas do mapa
// (os materiais são da biblioteca do set e saem em set.releaseMaterials()), com as placas de massinha que recebem
// pegadas (`printSurfaces`, subfase 3.5).

```

Em `src/maps/pista/visual/index.js`, trocar:

```
 * @param {{layout:object, set:import('../../../clay/set/index.js').SetLibrary, anisotropy?:number, data?:object}} opts
 * @returns {{group:THREE.Group, stats:object, dispose():void}}
 */
```

por:

```
 * @param {{layout:object, set:import('../../../clay/set/index.js').SetLibrary, anisotropy?:number, data?:object}} opts
 * @returns {{group:THREE.Group, stats:object, printSurfaces:object[], dispose():void}}
 */
```

Em `src/maps/pista/visual/index.js`, trocar:

```
    },
    dispose() {
```

por:

```
    },
    printSurfaces: clay.printSurfaces,
    dispose() {
```

Em `src/maps/pista/index.js`, trocar:

```
// `pista` (key alta com a única sombra, fill, rim e as luzes práticas da praça e do túnel). Nada na pista se mexe: a
// sombra é feita uma vez (staticShadows).

```

por:

```
// `pista` (key alta com a única sombra, fill, rim e as luzes práticas da praça e do túnel). Nada na pista se mexe: a
// sombra é feita uma vez (staticShadows). As sete placas de massinha recebem pegadas (`printSurfaces`, subfase 3.5).

```

Em `src/maps/pista/index.js`, trocar:

```
      stats: visuals.stats,
      post: { context: 'jogo', exposure: rigDef.exposure },
```

por:

```
      stats: visuals.stats,
      printSurfaces: visuals.printSurfaces,
      post: { context: 'jogo', exposure: rigDef.exposure },
```

- [ ] **Passo 6: As pegadas na partida e o `pegadas` do console**

Em `src/modes/matchState.js`, trocar:

```
// estações (`estacao`, pista de testes), as escalas da sensação da câmera (subfase 3.5, seção "Conforto"), o corpo do
// jogador (o boneco de referência com squash & stretch, visível em terceira pessoa e no noclip) e o resumo que vai para
// a tela de resultado.

```

por:

```
// estações (`estacao`, pista de testes), as escalas da sensação da câmera (subfase 3.5, seção "Conforto"), o corpo do
// jogador (o boneco de referência com squash & stretch, visível em terceira pessoa e no noclip), as pegadas nas peças
// de massinha que o mapa declara (`printSurfaces`) e o resumo que vai para a tela de resultado.

```

Em `src/modes/matchState.js`, trocar:

```
import { PlayerBody } from '../characters/playerBody.js';
import { itemName, zoomLevels } from '../player/hands.js';
```

por:

```
import { PlayerBody } from '../characters/playerBody.js';
import { PrintSystem } from '../clay/prints/printSystem.js';
import { itemName, zoomLevels } from '../player/hands.js';
```

Em `src/modes/matchState.js`, trocar:

```
    this.body = null; // corpo do jogador (subfase 3.5)
    this.physicsDebug = null;
```

por:

```
    this.body = null; // corpo do jogador (subfase 3.5)
    this.prints = null; // pegadas na massinha (subfase 3.5), nos mapas com `printSurfaces`
    this.physicsDebug = null;
```

Em `src/modes/matchState.js`, trocar:

```
      this.body.onPose(this.player);
      this.physicsDebug = new PhysicsDebugView({ scene: this.map.scene, world: this.map.collision });
```

por:

```
      this.body.onPose(this.player);
      if (this.map.printSurfaces?.length) {
        this.prints = new PrintSystem({ render: s.render, events: s.events, surfaces: this.map.printSurfaces });
      }
      this.physicsDebug = new PhysicsDebugView({ scene: this.map.scene, world: this.map.collision });
```

Em `src/modes/matchState.js`, trocar:

```
      });
      // Corpo: forma, virada e botas mudam só na troca de pose (12/s), como a massinha animada "em dois".
      this.subs.on(s.events, EV.POSE, () => this.body?.onPose(this.player));
      this.subs.on(s.events, EV.PLAYER_WEAPON, () => this.#syncHeld());
```

por:

```
      });
      // Corpo: forma, virada e botas mudam só na troca de pose (12/s), como a massinha animada "em dois"; as pegadas da
      // fila vão para a GPU no mesmo ritmo (junto com o boil).
      this.subs.on(s.events, EV.POSE, () => {
        this.body?.onPose(this.player);
        this.prints?.onPose();
      });
      this.subs.on(s.events, EV.PLAYER_WEAPON, () => this.#syncHeld());
```

Em `src/modes/matchState.js`, trocar:

```
      this.body.tick(this.player, dt);
      this.returnPoint.update(this.player.vitals.alive, this.player.state.onGround);
```

por:

```
      this.body.tick(this.player, dt);
      this.prints?.tick(this.player, dt);
      this.returnPoint.update(this.player.vitals.alive, this.player.state.onGround);
```

Em `src/modes/matchState.js`, trocar:

```
    this.body?.reset();
    this.returnPoint.placed();
```

por:

```
    this.body?.reset();
    this.prints?.reset();
    this.returnPoint.placed();
```

Em `src/modes/matchState.js`, trocar:

```
    this.body?.dispose();
    this.physicsDebug?.dispose();
```

por:

```
    this.body?.dispose();
    this.prints?.dispose();
    this.physicsDebug?.dispose();
```

Em `src/modes/matchState.js`, trocar:

```
    this.body = null;
    this.physicsDebug = null;
```

por:

```
    this.body = null;
    this.prints = null;
    this.physicsDebug = null;
```

Em `src/modes/matchState.js`, trocar:

```
    this.player?.teleport(position, yaw, pitch);
    this.jump?.interrupt();
```

por:

```
    this.player?.teleport(position, yaw, pitch);
    this.prints?.reset();
    this.jump?.interrupt();
```

Em `src/debug/commands.js`, trocar:

```
    },
  });
  reg({
    name: 'hardware', help: 'GPU detectada, benchmark e preset recomendado',
```

por:

```
    },
  });
  reg({
    name: 'pegadas', usage: '[limpar]', help: 'pegadas na massinha: placas com marca viva e a fila; limpar apaga',
    complete: () => ['limpar'],
    run: ([arg]) => {
      const prints = matchState()?.prints;
      if (!prints) throw new Error('só numa partida em mapa com massinha que recebe pegadas (map pista)');
      if (arg !== undefined && arg !== 'limpar') throw new Error('uso: pegadas [limpar]');
      if (arg === 'limpar') {
        prints.clear();
        return 'pegadas apagadas';
      }
      const i = prints.info();
      const live = i.live.map((p) => `${p.id} (${p.seconds.toFixed(1)} s)`).join(', ') || 'nenhuma';
      return `${i.surfaces} placas · com marca viva: ${live}\nfila ${i.queue} · marcas ${i.marks} · desenhos ${i.draws}`
        + ` · mapas ${i.megabytes.toFixed(1)} MB`;
    },
  });
  reg({
    name: 'hardware', help: 'GPU detectada, benchmark e preset recomendado',
```

- [ ] **Passo 7: Rodar os testes da tarefa**

Run: `node --test tests/footprints.test.js tests/pistaMaterials.test.js`
Expected: PASS — todos os testes dos dois arquivos passando.

- [ ] **Passo 8: Suíte inteira**

Run: `npm test`
Expected: PASS — 290 testes passando.

- [ ] **Passo final: Commit** (só com o pedido do usuário)

```bash
git add src/clay src/maps/pista src/modes/matchState.js src/debug/commands.js tests/footprints.test.js
git commit -m "MASSACRE 3.5: pegadas na GPU — mapa por placa, carimbo, esmaecimento e a camada CLAY_PRINTS" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Tarefa 6: O monitor do movimento e a varredura de aceite

**Files:**
- Create: `src/debug/moveMonitor.js`, `tests/pistaSim.js`, `tests/moveMonitor.test.js`, `tools/phase3-acceptance.mjs`
- Modify: `src/data/sandbox.js`, `src/data/configSchema.js`, `src/debug/movementCommands.js`, `styles/debug.css`, `src/modes/matchState.js`, `src/maps/pista/index.js`, `tests/pistaFuzz.test.js` (arquivo inteiro), `package.json`

O registro do monitor é puro: a cada tick fora do noclip confere se a cápsula cabe onde está (`canOccupy` com 0,05 u de folga; a profundidade pelo contato mais fundo), se ficou presa e se caiu abaixo do chão do estúdio, guarda os primeiros problemas com o tick e o lugar e soma o tempo no lote sob os pés; guarda o tempo de cada quadro (FPS e 1% low pela estatística do `presetSweep`: a janela curta no painel, ao lado da média da sessão tirada da soma dos quadros — ordenar a sessão inteira quatro vezes por segundo pesava depois de alguns minutos —, e a sessão inteira no relatório) e uma amostra de memória por segundo (geometrias, texturas, programas e o heap). O `MoveMonitor` junta o painel (à direita, como o `cl_showpos`) e o relatório em texto; `cl_monitor 1` grava e mostra (chave transitória `debug.monitor`), `monitor` imprime o relatório e `monitor zerar` recomeça. A simulação da pista sai do teste de 10 min para `tests/pistaSim.js` com as checagens do monitor (as mesmas), e o `tools/phase3-acceptance.mjs` roda 5 seeds × 10 min, cada uma duas vezes (a repetição bit a bit), com o relatório (pulos, slides, wall-jumps, empurrões, altura máxima e o tempo em cada estação); a pista passa a declarar os lotes das estações.

- [ ] **Passo 1: Escrever os testes** — o monitor, a simulação compartilhada e os 10 min da pista pelo monitor (arquivo inteiro).

```js file=tests/moveMonitor.test.js
// Testes do monitor do movimento (subfase 3.5, aceite da Fase 3): a checagem por tick (penetração com a profundidade,
// preso, abaixo do chão do estúdio; nada no noclip), os problemas guardados com o tick e o lugar, o tempo por estação
// (o lote sob os pés), a estatística de FPS (média, 1% low e a janela do painel), a memória (primeira, última, mínimo e
// máximo) e o relatório em texto.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import * as THREE from 'three';
import { HULL } from '../src/data/movement.js';
import { MONITOR } from '../src/data/sandbox.js';
import { MonitorLog, formatMonitorReport, memorySample } from '../src/debug/moveMonitor.js';
import { createMoveState, MOVETYPE } from '../src/player/movement.js';
import { floor, worldOf } from './worldTestUtils.js';

const DT = 1 / 64;
const world = worldOf((b) => floor(b));
const LOTS = [
  { number: 1, label: 'Counter-strafe', x: [0, 400], z: [0, 400] },
  { number: 2, label: 'Escadas', x: [500, 900], z: [0, 400] },
];

function at(x, y, z) {
  const s = createMoveState({ position: new THREE.Vector3(x, y, z) });
  s.onGround = true;
  return s;
}

test('checagem por tick: cabe no chão; penetração com a profundidade; preso; abaixo do chão; nada no noclip', () => {
  const log = new MonitorLog({ world, floorY: -100, lots: LOTS }); // o chão do estúdio bem abaixo do tapete
  for (let i = 0; i < 64; i++) log.tick(at(100, 0, 100), DT);
  assert.ok(log.ok && log.checked === 64 && log.penetrations === 0);
  log.tick(at(100, -3, 100), DT);
  assert.equal(log.penetrations, 1);
  assert.ok(Math.abs(log.maxDepth - 3) < 1e-6, `3 u dentro do chão: ${log.maxDepth}`);
  // Encostado no chão (dentro da folga de 0,05 u): não conta.
  log.tick(at(100, -MONITOR.tolerance / 2, 100), DT);
  assert.equal(log.penetrations, 1);
  const stuck = at(100, 0, 100);
  stuck.stuck = true;
  log.tick(stuck, DT);
  assert.equal(log.stuck, 1);
  // Abaixo do chão do estúdio (o fundo do mapa): no ar, sem penetrar nada.
  const low = new MonitorLog({ world, floorY: 200 });
  low.tick(at(100, 150, 100), DT);
  assert.equal(low.below, 1);
  assert.equal(low.penetrations, 0);
  // Noclip atravessa tudo de propósito: não confere (mas o tempo e o lote contam).
  const ghost = at(100, -40, 100);
  ghost.moveType = MOVETYPE.NOCLIP;
  const before = log.checked;
  log.tick(ghost, DT);
  assert.equal(log.checked, before);
  assert.equal(log.penetrations, 1);
  assert.equal(log.ok, false);
  assert.deepEqual(log.problems.map((p) => p.kind), ['penetração', 'preso']);
  assert.equal(log.problems[0].tick, 65);
  assert.deepEqual(log.problems[0].at, [100, -3, 100]);
  // Problemas guardados até o limite; a contagem continua.
  for (let i = 0; i < 40; i++) log.tick(at(100, -3, 100), DT);
  assert.equal(log.problems.length, MONITOR.keepProblems);
  assert.equal(log.penetrations, 41);
  log.reset();
  assert.ok(log.ok && log.ticks === 0 && log.problems.length === 0 && log.lotTime.size === 0);
});

test('tempo por estação: o lote sob os pés; fora deles, "fora dos lotes"', () => {
  const log = new MonitorLog({ world, floorY: 0, lots: LOTS });
  for (let i = 0; i < 128; i++) log.tick(at(200, 0, 200), DT);
  for (let i = 0; i < 64; i++) log.tick(at(700, 0, 100), DT);
  for (let i = 0; i < 32; i++) log.tick(at(-300, 0, 0), DT);
  assert.equal(log.lotAt(400, 400), 1, 'a borda conta');
  assert.equal(log.lotAt(450, 0), 0);
  const r = log.report();
  assert.deepEqual(r.lots.map((l) => [l.number, l.label, l.seconds]), [
    [1, 'Counter-strafe', 2], [2, 'Escadas', 1], [0, 'fora dos lotes', 0.5],
  ]);
  assert.ok(Math.abs(r.minutes - 3.5 / 60) < 1e-12);
});

test('FPS da sessão e da janela (média e 1% low) e memória (primeira, última, mínimo, máximo)', () => {
  const log = new MonitorLog({ world });
  for (let i = 0; i < 99; i++) log.frame(10);
  log.frame(50);
  log.frame(0); // quadro sem tempo não entra
  const all = log.fps();
  assert.equal(all.frames, 100);
  assert.ok(Math.abs(all.fps - 100000 / 1040) < 1e-9);
  assert.ok(Math.abs(all.low1Fps - 20) < 1e-9, '1% low = o quadro de 50 ms');
  assert.ok(Math.abs(log.sessionFps() - all.fps) < 1e-9, 'a média da sessão pela soma, sem ordenar');
  const recent = log.fps(0.055);
  assert.equal(recent.frames, 2, 'a janela junta quadros do fim até cobrir o tempo');
  log.sample({ geometries: 120, textures: 40, programs: 30, heapMB: 80 });
  log.tick(at(0, 0, 0), DT);
  log.sample({ geometries: 126, textures: 40, programs: 31, heapMB: 95 });
  log.sample({ geometries: 120, textures: 40, programs: 31, heapMB: 82 });
  const m = log.report().memory;
  assert.equal(m.samples, 3);
  assert.deepEqual(m.geometries, { first: 120, last: 120, min: 120, max: 126 });
  assert.deepEqual(m.heapMB, { first: 80, last: 82, min: 80, max: 95 });
  assert.equal(log.memory[1].time, DT, 'amostra no tempo de jogo');
  const sample = memorySample({ stats: () => ({ geometries: 7, textures: 3, programs: 2 }) });
  assert.equal(sample.geometries, 7);
  assert.ok(sample.heapMB === null || sample.heapMB > 0);
});

test('relatório em texto: resultado, problemas, FPS, memória e estações', () => {
  const log = new MonitorLog({ world, floorY: 0, lots: LOTS });
  for (let i = 0; i < 64; i++) log.tick(at(10, 0, 10), DT);
  let text = formatMonitorReport(log.report());
  assert.match(text, /→ OK/);
  assert.match(text, / 1 Counter-strafe\s+1 s/);
  assert.match(text, /FPS n\/d/);
  log.tick(at(10, -2, 10), DT);
  text = formatMonitorReport(log.report());
  assert.match(text, /penetração 1 \(máx\. 2\.000 u\)/);
  assert.match(text, /FALHOU/);
  assert.match(text, /tick 65: penetração em 10\.0 -2\.0 10\.0 \(2\.000 u\)/);
  assert.ok(HULL.radius > 2);
});
```

```js file=tests/pistaSim.js
// Simulação aleatória na colisão da pista de testes (subfases 3.3 e 3.4; módulo próprio na 3.5): entrada com andar,
// spam de agachar, pulos, slides, wall-jumps e troca do item na mão, partindo de cada estação (a mesma fatia de tempo em
// cada uma, do primeiro ponto de teleporte), com empurrões de até 1500 u/s a cada 400 ticks. As checagens são as do
// monitor do movimento (src/debug/moveMonitor.js: nenhuma penetração além da folga, nunca preso, nunca abaixo do chão
// do estúdio), que também soma o tempo em cada lote. Usada pelo teste de 10 min (tests/pistaFuzz.test.js) e pela
// varredura de aceite da Fase 3 (tools/phase3-acceptance.mjs, 5 seeds × 10 min).

import { RNG } from '../src/core/rng.js';
import { PISTA } from '../src/data/pista.js';
import { buildPistaLayout } from '../src/maps/pista/layout.js';
import { buildPistaColliders } from '../src/maps/pista/colliders.js';
import { CollisionWorld } from '../src/physics/collisionWorld.js';
import { resolveStations } from '../src/maps/stations.js';
import { MonitorLog } from '../src/debug/moveMonitor.js';
import { BTN } from '../src/player/moveCmd.js';
import { playerMove } from '../src/player/movement.js';
import { DT, itemEnv, makePlayer } from './playerTestUtils.js';

export const layout = buildPistaLayout();
export const world = CollisionWorld.fromBuilder(buildPistaColliders(layout), 'pista');
export const stations = resolveStations(layout.stations, world);
export const TEN_MINUTES = 10 * 60 * 64;
export const FLOOR = -PISTA.base.thickness; // chão do estúdio
const ITEMS = [['knife', 0], ['ak47', 0], ['awp', 1], ['negev', 0], ['c4', 0]];
const LOTS = PISTA.lots.map((l) => ({
  number: l.number, x: l.x, z: l.z, label: stations.find((s) => s.number === l.number)?.label,
}));

/**
 * `ticks` ticks com a seed `seed`. Devolve o estado final, as contagens (pulos, agachadas, empurrões, altura máxima,
 * estações, slides e wall-jumps) e, com `check`, o registro do monitor (`log.ok`, os problemas e o tempo por lote).
 */
export function simulatePista(seed, ticks, { check = true } = {}) {
  const rng = new RNG(seed);
  const per = Math.ceil(ticks / stations.length);
  const stats = { jumps: 0, ducks: 0, kicks: 0, maxY: -Infinity, stations: 0, slides: 0, wallJumps: 0 };
  const log = check ? new MonitorLog({ world, floorY: FLOOR, lots: LOTS }) : null;
  let p = null;
  let phase = 0;
  let turn = 0;
  let rates = { jump: 0, duck: 0, walk: 0 };
  for (let i = 0; i < ticks; i++) {
    if (i % per === 0) {
      const st = stations[Math.floor(i / per)];
      const s = st.spots[0].position;
      p = makePlayer(world, [s.x, s.y, s.z], { yaw: st.spots[0].yaw });
      stats.stations++;
    }
    if (phase-- <= 0) {
      phase = rng.int(16, 64);
      let f = rng.bool(0.3) ? rng.float(-1, 1) : rng.pick([-1, 0, 1]);
      let sd = rng.bool(0.3) ? rng.float(-1, 1) : rng.pick([-1, 0, 1]);
      const len = Math.hypot(f, sd);
      if (len > 1) {
        f /= len;
        sd /= len;
      }
      p.cmd.forward = f;
      p.cmd.side = sd;
      turn = rng.float(-5, 5);
      rates = { jump: rng.pick([0, 0.05, 0.3]), duck: rng.pick([0, 0, 0.5, 1]), walk: rng.pick([0, 0, 1]) };
      const [item, zoom] = rng.pick(ITEMS);
      p.env.item = itemEnv(item, zoom);
    }
    p.cmd.yaw += turn * DT;
    p.cmd.buttons = (rng.bool(rates.jump) ? BTN.JUMP : 0) | (rng.bool(rates.duck) ? BTN.DUCK : 0) | (rng.bool(rates.walk) ? BTN.WALK : 0);
    if (i % 400 === 399) {
      const dir = rng.onUnitSphere();
      const v = rng.float(300, 1500);
      p.state.velocity.set(dir.x * v, Math.abs(dir.y) * v, dir.z * v);
      p.state.onGround = false;
      stats.kicks++;
    }
    p.cmd.tick = i;
    playerMove(p.state, p.cmd, p.env);
    const s = p.state;
    for (const e of p.env.events) {
      if (e.type === 'jump') stats.jumps++;
      if (e.type === 'duck') stats.ducks++;
      if (e.type === 'slide' && e.phase === 'start') stats.slides++;
      if (e.type === 'walljump') stats.wallJumps++;
    }
    stats.maxY = Math.max(stats.maxY, s.origin.y);
    log?.tick(s, DT);
  }
  return { state: p.state, stats, log };
}

/** Estado inteiro como texto: números com a representação exata do double (igual ⇔ bit a bit). */
export function snapshotState(s) {
  return JSON.stringify({
    ...s, origin: s.origin.toArray(), velocity: s.velocity.toArray(), groundNormal: s.groundNormal.toArray(),
  });
}

/** Os problemas do registro em texto (mensagem das falhas). */
export function describeProblems(log) {
  return log.problems.map((p) => `tick ${p.tick}: ${p.kind} em ${p.at.map((v) => v.toFixed(2)).join(' ')}`).join('; ');
}
```

```js file=tests/pistaFuzz.test.js
// 10 minutos simulados na colisão da pista de testes (subfases 3.3 e 3.4; a parte automática do aceite da Fase 3, na
// suíte com uma seed — a varredura de 5 seeds é o tools/phase3-acceptance.mjs): entrada aleatória com andar, spam de
// agachar, pulos, slides, wall-jumps e troca do item na mão, partindo de cada estação (50 s em cada uma, do primeiro
// ponto de teleporte), com empurrões de até 1500 u/s — pelas checagens do monitor do movimento, nenhuma penetração além
// da folga, nunca preso, nunca abaixo do chão do estúdio. Depois, a mesma seed repetida dá o mesmo estado inteiro, bit
// a bit. A simulação fica em tests/pistaSim.js.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { TEN_MINUTES, describeProblems, simulatePista, snapshotState } from './pistaSim.js';

test('10 min simulados na pista, partindo de cada estação: nenhuma penetração, nunca preso', () => {
  const { stats, log } = simulatePista('pista-dez-minutos', TEN_MINUTES, { check: true });
  assert.ok(log.ok, describeProblems(log));
  assert.equal(log.checked, TEN_MINUTES);
  assert.equal(stats.stations, 12);
  assert.ok(stats.jumps > 100, `pulos ${stats.jumps}`);
  assert.ok(stats.ducks > 100, `agachadas ${stats.ducks}`);
  assert.equal(stats.kicks, TEN_MINUTES / 400);
  assert.ok(stats.maxY > 200, `subiu em alguma coisa (${stats.maxY})`);
  assert.ok(stats.slides > 20, `slides ${stats.slides}`);
  assert.ok(stats.wallJumps > 20, `wall-jumps ${stats.wallJumps}`);
  // Cada fatia começa numa estação: os 12 lotes recebem tempo (os empurrões levam o jogador para a praça e os caminhos).
  const report = log.report();
  const lots = report.lots.filter((l) => l.number);
  assert.equal(lots.length, 12, lots.map((l) => `${l.number}: ${l.seconds.toFixed(0)} s`).join(', '));
  assert.ok(Math.abs(report.lots.reduce((sum, l) => sum + l.seconds, 0) - 600) < 1e-6, '10 min no total');
});

test('a mesma seed dá o mesmo estado inteiro na pista, bit a bit (2 min)', () => {
  const a = simulatePista('pista-repetivel', 2 * 60 * 64, { check: false }).state;
  const b = simulatePista('pista-repetivel', 2 * 60 * 64, { check: false }).state;
  assert.equal(snapshotState(a), snapshotState(b));
});
```

- [ ] **Passo 2: Rodar e ver falhar**

Run: `node --test tests/moveMonitor.test.js tests/pistaFuzz.test.js`
Expected: FAIL — os dois arquivos não carregam: `ERR_MODULE_NOT_FOUND` (não acha `src/debug/moveMonitor.js`, importado pelo teste do monitor e pelo `tests/pistaSim.js`).

- [ ] **Passo 3: Números e o monitor**

Em `src/data/sandbox.js`, trocar:

```
// Parâmetros da sala de testes e do modo livre (Fases 1 e 3): sala de papelão andável, volta ao spawn ao cair do set
// e a câmera livre (voo da vitrine e noclip).
// Unidades: 1 unidade = 1 cm na escala do boneco (o boneco tem ~72 unidades de altura).
```

por:

```
// Parâmetros da sala de testes e do modo livre (Fases 1 e 3): sala de papelão andável, volta ao spawn ao cair do set,
// a câmera livre (voo da vitrine e noclip) e o monitor do movimento do aceite da Fase 3 (subfase 3.5).
// Unidades: 1 unidade = 1 cm na escala do boneco (o boneco tem ~72 unidades de altura).
```

Em `src/data/sandbox.js`, trocar:

```

export const FREE_CAMERA = Object.freeze({
```

por:

```

/** Monitor do movimento (`cl_monitor`, src/debug/moveMonitor.js), o mesmo da varredura do Node. */
export const MONITOR = Object.freeze({
  tolerance: 0.05, // u de folga na checagem "a cápsula cabe aqui?" (a dos testes de varredura da 3.2 à 3.4)
  floorSlack: 0.01, // u abaixo do chão do estúdio que ainda não contam como queda para fora
  memoryEvery: 1, // s entre as amostras de memória (geometrias, texturas, programas e heap)
  window: 5, // s de quadros no FPS "agora" do painel (o do relatório é o da sessão inteira)
  panelHz: 4, // atualizações do texto do painel por segundo
  keepProblems: 20, // problemas guardados com o tick e o lugar (a contagem continua)
});

export const FREE_CAMERA = Object.freeze({
```

```js file=src/debug/moveMonitor.js
// Monitor do movimento (subfase 3.5, aceite da Fase 3; `cl_monitor 1` no console, chave transitória debug.monitor;
// números em src/data/sandbox.js, MONITOR): a cada tick confere se a cápsula cabe onde está (canOccupy com 0,05 u de
// folga; a profundidade pelo contato mais fundo), se ficou presa e se caiu abaixo do chão do estúdio (o fundo do mapa);
// a cada quadro guarda o tempo dele (FPS médio e 1% low pela estatística pura do presetSweep); a cada segundo, a
// memória (geometrias, texturas, programas e o heap do JS); e o tempo em cada estação (o lote do mapa sob os pés).
// Painel na tela; `monitor` no console imprime o relatório e `monitor zerar` recomeça. O registro (MonitorLog) é puro:
// a varredura do Node (tests/pistaSim.js, tools/phase3-acceptance.mjs) faz as mesmas checagens com ele.

import { HULL } from '../data/movement.js';
import { MONITOR } from '../data/sandbox.js';
import { createContact } from '../physics/collisionWorld.js';
import { MOVETYPE } from '../player/movement.js';
import { h } from '../ui/dom.js';
import { summarizeFrames } from './presetSweep.js';

const OUTSIDE = 0; // "fora dos lotes": praça, caminhos e o que não é estação

/** Mínimo, máximo, primeiro e último de um campo das amostras de memória. */
function spread(samples, key) {
  const values = samples.map((m) => m[key]).filter((v) => typeof v === 'number');
  if (!values.length) return null;
  return { first: values[0], last: values.at(-1), min: Math.min(...values), max: Math.max(...values) };
}

export class MonitorLog {
  /**
   * @param {{world: import('../physics/collisionWorld.js').CollisionWorld, floorY?: number,
   *   lots?: Array<{number: number, label?: string, x: number[], z: number[]}>}} opts
   */
  constructor({ world, floorY = -Infinity, lots = [] }) {
    this.world = world;
    this.floorY = floorY;
    this.lots = lots;
    this._contact = createContact();
    this.reset();
  }

  reset() {
    this.time = 0; // s de jogo registrados
    this.ticks = 0;
    this.checked = 0; // ticks conferidos (fora do noclip)
    this.penetrations = 0;
    this.maxDepth = 0; // u: a penetração mais funda
    this.stuck = 0;
    this.below = 0;
    this.problems = []; // os primeiros, com o tick e o lugar
    this.frames = []; // ms de cada quadro
    this.frameMs = 0; // soma deles (a média da sessão sem percorrer a lista)
    this.memory = []; // uma amostra por segundo
    this.lotTime = new Map(); // número do lote (0 = fora) → s
  }

  /** Número do lote sob (x, z), ou 0 fora de todos. */
  lotAt(x, z) {
    for (const lot of this.lots) {
      if (x >= lot.x[0] && x <= lot.x[1] && z >= lot.z[0] && z <= lot.z[1]) return lot.number;
    }
    return OUTSIDE;
  }

  /** Um tick de jogo com o estado de movimento `s`; no noclip não confere (atravessa tudo de propósito). */
  tick(s, dt) {
    this.time += dt;
    this.ticks++;
    const o = s.origin;
    const lot = this.lotAt(o.x, o.z);
    this.lotTime.set(lot, (this.lotTime.get(lot) ?? 0) + dt);
    if (s.moveType === MOVETYPE.NOCLIP) return;
    this.checked++;
    if (!this.world.canOccupy(o.x, o.y, o.z, HULL.radius, s.height, MONITOR.tolerance)) {
      const c = this._contact;
      this.world.deepestContact(o.x, o.y, o.z, HULL.radius, s.height, HULL.radius, c);
      const depth = c.pierced ? HULL.radius + c.pierceDepth : HULL.radius - c.distance;
      this.penetrations++;
      this.maxDepth = Math.max(this.maxDepth, depth);
      this.#problem('penetração', o, depth);
    }
    if (s.stuck) {
      this.stuck++;
      this.#problem('preso', o);
    }
    if (o.y < this.floorY - MONITOR.floorSlack) {
      this.below++;
      this.#problem('abaixo do chão do estúdio', o);
    }
  }

  #problem(kind, o, depth = null) {
    if (this.problems.length >= MONITOR.keepProblems) return;
    this.problems.push({ kind, tick: this.ticks, at: [o.x, o.y, o.z], depth });
  }

  /** Nenhuma penetração, nenhum tick preso, nenhuma queda para fora. */
  get ok() {
    return this.penetrations + this.stuck + this.below === 0;
  }

  /** Um quadro do render (ms). */
  frame(dtMs) {
    if (dtMs <= 0) return;
    this.frames.push(dtMs);
    this.frameMs += dtMs;
  }

  /** FPS médio da sessão (sem ordenar nada: o painel pede algumas vezes por segundo), ou null sem quadros. */
  sessionFps() {
    return this.frames.length ? (this.frames.length * 1000) / this.frameMs : null;
  }

  /** Amostra de memória {geometries, textures, programs, heapMB} no tempo de jogo de agora. */
  sample(sample) {
    this.memory.push({ time: this.time, ...sample });
  }

  /** Estatística dos quadros dos últimos `seconds` s (null: a sessão inteira). */
  fps(seconds = null) {
    let frames = this.frames;
    if (seconds !== null) {
      let sum = 0;
      let i = frames.length;
      while (i > 0 && sum < seconds * 1000) sum += frames[--i];
      frames = frames.slice(i);
    }
    return summarizeFrames(frames.map((dtMs) => ({ dtMs })));
  }

  /** Relatório: minutos, checagens, FPS da sessão, memória (primeira, última, mín. e máx.) e o tempo por estação. */
  report() {
    const labels = new Map(this.lots.map((l) => [l.number, l.label ?? `estação ${l.number}`]));
    const lots = [...this.lotTime.entries()]
      .sort((a, b) => (a[0] || 99) - (b[0] || 99))
      .map(([number, seconds]) => ({ number, label: number ? labels.get(number) : 'fora dos lotes', seconds }));
    return {
      minutes: this.time / 60,
      ticks: this.ticks,
      checked: this.checked,
      penetrations: this.penetrations,
      maxDepth: this.maxDepth,
      stuck: this.stuck,
      below: this.below,
      ok: this.ok,
      problems: this.problems,
      fps: this.fps(),
      memory: {
        samples: this.memory.length,
        geometries: spread(this.memory, 'geometries'),
        textures: spread(this.memory, 'textures'),
        programs: spread(this.memory, 'programs'),
        heapMB: spread(this.memory, 'heapMB'),
      },
      lots,
    };
  }
}

const n1 = (v) => (v === null || v === undefined ? 'n/d' : v.toFixed(1));
const at = (p) => p.at.map((v) => v.toFixed(1)).join(' ');

/** Primeira → última (mínimo, máximo) de um campo de memória. */
function span(s, d = 0) {
  if (!s) return 'n/d';
  return `${s.first.toFixed(d)} → ${s.last.toFixed(d)} (mín. ${s.min.toFixed(d)}, máx. ${s.max.toFixed(d)})`;
}

/** Um problema guardado: tick, tipo, lugar e (penetração) a profundidade. */
function problemLine(p) {
  return `  tick ${p.tick}: ${p.kind} em ${at(p)}${p.depth === null ? '' : ` (${p.depth.toFixed(3)} u)`}`;
}

/** Relatório em texto (console, PROGRESS.md). */
export function formatMonitorReport(r) {
  const width = Math.max(0, ...r.lots.map((l) => l.label.length));
  const lines = [
    `monitor · ${r.minutes.toFixed(1)} min de jogo · ${r.ticks} ticks (${r.checked} conferidos fora do noclip)`,
    `penetração ${r.penetrations}${r.penetrations ? ` (máx. ${r.maxDepth.toFixed(3)} u)` : ''} · preso ${r.stuck}`
      + ` · abaixo do chão ${r.below} → ${r.ok ? 'OK' : 'FALHOU'}`,
    ...r.problems.map(problemLine),
    `FPS ${n1(r.fps.fps)} · 1% low ${n1(r.fps.low1Fps)} · quadro ${n1(r.fps.frameMs)} ms · p95 ${n1(r.fps.p95Ms)} ms`
      + ` (${r.fps.frames} quadros)`,
    `memória (${r.memory.samples} amostras): geometrias ${span(r.memory.geometries)}`
      + ` · texturas ${span(r.memory.textures)} · programas ${span(r.memory.programs)}`
      + ` · heap ${span(r.memory.heapMB, 1)} MB`,
    'estações:',
    ...r.lots.map((l) => {
      const number = l.number ? String(l.number).padStart(2) : ' —';
      return `  ${number} ${l.label.padEnd(width)} ${l.seconds.toFixed(0).padStart(5)} s`;
    }),
  ];
  return lines.join('\n');
}

/** Amostra de memória do render e do heap do JS (o heap só no Chromium). */
export function memorySample(render) {
  const r = render.stats();
  const heap = globalThis.performance?.memory?.usedJSHeapSize;
  return { geometries: r.geometries, textures: r.textures, programs: r.programs, heapMB: heap ? heap / 1048576 : null };
}

export class MoveMonitor {
  /**
   * @param {{root: HTMLElement, world: import('../physics/collisionWorld.js').CollisionWorld, floorY: number,
   *   lots?: object[], stations?: Array<{number: number, label: string}>}} opts
   */
  constructor({ root, world, floorY, lots = [], stations = [] }) {
    const label = new Map(stations.map((s) => [s.number, s.label]));
    this.log = new MonitorLog({ world, floorY, lots: lots.map((l) => ({ ...l, label: label.get(l.number) })) });
    this.text = h('pre.dbg-monitor-text');
    this.el = h('div.dbg-monitor', { hidden: true, 'aria-hidden': 'true' }, this.text);
    root.append(this.el);
    this.visible = false;
    this.memoryAcc = 0;
    this.panelAcc = 0;
  }

  /** Liga (grava e mostra) ou desliga (para de gravar; o registro fica para o `monitor`). */
  setVisible(visible) {
    this.visible = visible;
    this.el.hidden = !visible;
    this.panelAcc = Infinity;
  }

  /** Um tick do jogo (depois do tick do jogador). */
  tick(pawn, dt) {
    if (this.visible) this.log.tick(pawn.state, dt);
  }

  /** Um quadro: o tempo dele, a memória a cada segundo e o texto do painel algumas vezes por segundo. */
  frame(dt, render, pawn) {
    if (!this.visible) return;
    this.log.frame(dt * 1000);
    this.memoryAcc += dt;
    if (this.memoryAcc >= MONITOR.memoryEvery) {
      this.memoryAcc = 0;
      this.log.sample(memorySample(render));
    }
    this.panelAcc += dt;
    if (this.panelAcc < 1 / MONITOR.panelHz) return;
    this.panelAcc = 0;
    const l = this.log;
    // A janela do painel é curta; o 1% low da sessão ordena todos os quadros e fica só no relatório (`monitor`).
    const now = l.fps(MONITOR.window);
    const mem = l.memory.at(-1);
    const lot = l.lotAt(pawn.state.origin.x, pawn.state.origin.z);
    const here = lot ? `${lot} · ${l.lots.find((x) => x.number === lot)?.label ?? ''}` : 'fora dos lotes';
    this.text.textContent = [
      `MONITOR  ${(l.time / 60).toFixed(1)} min · ${l.checked} ticks conferidos · ${l.ok ? 'OK' : 'PROBLEMA'}`,
      `cápsula  penetração ${l.penetrations} (máx. ${l.maxDepth.toFixed(3)} u) · preso ${l.stuck} · fora ${l.below}`,
      `FPS      agora ${n1(now.fps)} (1% ${n1(now.low1Fps)}) · média da sessão ${n1(l.sessionFps())}`,
      mem ? `memória  geo ${mem.geometries} · tex ${mem.textures} · prog ${mem.programs} · heap ${n1(mem.heapMB)} MB`
        : 'memória  —',
      `estação  ${here} · ${((l.lotTime.get(lot) ?? 0) / 60).toFixed(1)} min aqui`,
    ].join('\n');
  }

  report() {
    return formatMonitorReport(this.log.report());
  }

  reset() {
    this.log.reset();
    this.memoryAcc = 0;
    this.panelAcc = Infinity;
  }

  dispose() {
    this.el.remove();
  }
}
```

- [ ] **Passo 4: `cl_monitor`, `monitor` e o painel**

Em `src/data/configSchema.js`, trocar:

```
  'debug.thirdPerson': { type: 'bool', default: false, transient: true, label: 'Câmera em terceira pessoa', group: 'debug' },
  'debug.consoleHistory': {
```

por:

```
  'debug.thirdPerson': { type: 'bool', default: false, transient: true, label: 'Câmera em terceira pessoa', group: 'debug' },
  'debug.monitor': { type: 'bool', default: false, transient: true, label: 'Monitor do movimento (cl_monitor)', group: 'debug' },
  'debug.consoleHistory': {
```

Em `src/debug/movementCommands.js`, trocar:

```
// Comandos do console da Fase 3: variáveis sv_* de movimento (valores do CS:GO), colisão visível, posição/velocidade
// do jogador, medidas de counter-strafe e de salto e queda, e câmera em terceira pessoa. Falam com as mesmas variáveis,
// chaves de config e os mesmos medidores que o jogo usa.

```

por:

```
// Comandos do console da Fase 3: variáveis sv_* de movimento (valores do CS:GO), colisão visível, posição/velocidade
// do jogador, medidas de counter-strafe e de salto e queda, o monitor do movimento do aceite da fase (3.5) e câmera em
// terceira pessoa. Falam com as mesmas variáveis, chaves de config e os mesmos medidores que o jogo usa.

```

Em `src/debug/movementCommands.js`, trocar:

```
  toggle('cl_showpos', 'debug.showPos', 'jogador, item na mão, teto, precisão, passos, counter-strafe (com gráfico) e salto');
  /** Medidor da partida andando (strafe ou jump do matchState). */
```

por:

```
  toggle('cl_showpos', 'debug.showPos', 'jogador, item na mão, teto, precisão, passos, counter-strafe (com gráfico) e salto');
  toggle('cl_monitor', 'debug.monitor', 'monitor: penetração, preso, queda, FPS, memória e tempo por estação');
  /** Medidor da partida andando (strafe ou jump do matchState). */
```

Em `src/debug/movementCommands.js`, trocar:

```
    },
  });
  reg({
    name: 'thirdperson',
```

por:

```
    },
  });
  reg({
    name: 'monitor',
    usage: '[zerar]',
    help: 'relatório do monitor do movimento (cl_monitor 1 grava); zerar recomeça',
    complete: () => ['zerar'],
    run: ([arg]) => {
      if (arg !== undefined && arg !== 'zerar') throw new Error('uso: monitor [zerar]');
      const monitor = meterOf('monitor');
      if (arg === 'zerar') {
        monitor.reset();
        return 'monitor zerado';
      }
      const off = s.config.get('debug.monitor') ? '' : '\n(desligado: cl_monitor 1 volta a gravar)';
      return `${monitor.report()}${off}`;
    },
  });
  reg({
    name: 'thirdperson',
```

Em `styles/debug.css`, trocar:

```
/* Ferramentas de desenvolvimento: overlay de desempenho (F3), console (` / F1), cl_showpos e guias de toque. */

```

por:

```
/* Ferramentas de desenvolvimento: overlay de desempenho (F3), console (` / F1), cl_showpos, cl_monitor e guias de
   toque. */

```

Em `styles/debug.css`, trocar:

```
.dbg-showpos-legend .is-walljump::before { width: 0; height: 9px; border-top: 0; border-left: 1.5px solid currentColor; }

```

por:

```
.dbg-showpos-legend .is-walljump::before { width: 0; height: 9px; border-top: 0; border-left: 1.5px solid currentColor; }

/* Monitor do movimento (cl_monitor, aceite da Fase 3): cápsula, FPS, memória e estação. À direita, como o cl_showpos
   (as etiquetas do HUD de teste ficam à esquerda), com a largura da linha mais longa (62 caracteres); com os dois
   ligados, desce para a linha de baixo. */
.dbg-monitor {
  position: relative;
  z-index: 60;
  width: min(100%, calc(62ch + 18px));
  margin: 0 0 0 auto;
  padding: 6px 9px;
  border-radius: 6px;
  background: rgb(42 35 32 / 0.78);
  color: var(--paper);
  font: 600 11.5px/1.45 var(--font-mono);
  text-shadow: 0 1px 0 #000;
  font-variant-numeric: tabular-nums;
  pointer-events: none !important;
}

.dbg-monitor-text { margin: 0; font: inherit; white-space: pre-wrap; }

```

- [ ] **Passo 5: O monitor na partida e os lotes da pista**

Em `src/modes/matchState.js`, trocar:

```
// jogador (o boneco de referência com squash & stretch, visível em terceira pessoa e no noclip), as pegadas nas peças
// de massinha que o mapa declara (`printSurfaces`) e o resumo que vai para a tela de resultado.

```

por:

```
// jogador (o boneco de referência com squash & stretch, visível em terceira pessoa e no noclip), as pegadas nas peças
// de massinha que o mapa declara (`printSurfaces`), o monitor do movimento do aceite da Fase 3 (cl_monitor) e o resumo
// que vai para a tela de resultado.

```

Em `src/modes/matchState.js`, trocar:

```
import { JumpMeter } from '../debug/jumpMeter.js';
import { CONTEXT } from '../input/inputManager.js';
```

por:

```
import { JumpMeter } from '../debug/jumpMeter.js';
import { MoveMonitor } from '../debug/moveMonitor.js';
import { CONTEXT } from '../input/inputManager.js';
```

Em `src/modes/matchState.js`, trocar:

```
    this.jump = null; // medidor de salto e queda (cl_showpos)
    this.hud = null;
```

por:

```
    this.jump = null; // medidor de salto e queda (cl_showpos)
    this.monitor = null; // monitor do movimento (cl_monitor, aceite da Fase 3)
    this.hud = null;
```

Em `src/modes/matchState.js`, trocar:

```
      this.jump = new JumpMeter(s.loop.stepDt);
      this.#applyDebugView();
```

por:

```
      this.jump = new JumpMeter(s.loop.stepDt);
      this.monitor = new MoveMonitor({
        root: s.debugRoot, world: this.map.collision, floorY: this.map.bounds.min.y, lots: this.map.lots,
        stations: this.map.stations,
      });
      this.#applyDebugView();
```

Em `src/modes/matchState.js`, trocar:

```

  /** r_colisao, cl_showpos e terceira pessoa seguem as chaves de debug da config. */
  #applyDebugView() {
```

por:

```

  /** r_colisao, cl_showpos, cl_monitor e terceira pessoa seguem as chaves de debug da config. */
  #applyDebugView() {
```

Em `src/modes/matchState.js`, trocar:

```
    this.showPos?.setVisible(cfg.get('debug.showPos'));
    if (this.player instanceof PlayerPawn) this.player.thirdPerson = cfg.get('debug.thirdPerson');
```

por:

```
    this.showPos?.setVisible(cfg.get('debug.showPos'));
    this.monitor?.setVisible(cfg.get('debug.monitor'));
    if (this.player instanceof PlayerPawn) this.player.thirdPerson = cfg.get('debug.thirdPerson');
```

Em `src/modes/matchState.js`, trocar:

```
      this.prints?.tick(this.player, dt);
      this.returnPoint.update(this.player.vitals.alive, this.player.state.onGround);
```

por:

```
      this.prints?.tick(this.player, dt);
      this.monitor.tick(this.player, dt);
      this.returnPoint.update(this.player.vitals.alive, this.player.state.onGround);
```

Em `src/modes/matchState.js`, trocar:

```
    this.showPos?.update(this.player, { strafe: this.strafe, jump: this.jump });
    if (this.player instanceof PlayerPawn) {
```

por:

```
    this.showPos?.update(this.player, { strafe: this.strafe, jump: this.jump });
    if (!this.paused) this.monitor?.frame(dt, this.s.render, this.player);
    if (this.player instanceof PlayerPawn) {
```

Em `src/modes/matchState.js`, trocar:

```
    this.showPos?.dispose();
    s.render.clearView();
```

por:

```
    this.showPos?.dispose();
    this.monitor?.dispose();
    s.render.clearView();
```

Em `src/modes/matchState.js`, trocar:

```
    this.jump = null;
    this.camera = null;
```

por:

```
    this.jump = null;
    this.monitor = null;
    this.camera = null;
```

Em `src/maps/pista/index.js`, trocar:

```
      stations,
      layout,
```

por:

```
      stations,
      // Lotes das estações: o monitor do movimento (cl_monitor) mede o tempo em cada um.
      lots: PISTA.lots.map((l) => ({ number: l.number, x: [...l.x], z: [...l.z] })),
      layout,
```

- [ ] **Passo 6: A varredura de aceite**

```js file=tools/phase3-acceptance.mjs
// Varredura de aceite da Fase 3 (subfase 3.5; `npm run aceite:fase3`): 5 seeds × 10 min simulados na colisão da pista
// de testes (50 min) com a entrada aleatória da suíte (tests/pistaSim.js: andar, agachar, pulos, slides, wall-jumps,
// troca do item e empurrões de até 1500 u/s, partindo de cada estação) e as checagens do monitor do movimento
// (src/debug/moveMonitor.js): nenhuma penetração além da folga, nunca preso, nunca abaixo do chão do estúdio. Cada seed
// roda duas vezes e o estado final tem de sair igual, bit a bit. Imprime o relatório (pulos, slides, wall-jumps,
// empurrões, altura máxima e o tempo em cada estação) e sai com código 1 se algo falhou.
// Uso: node tools/phase3-acceptance.mjs [seed1 seed2 ...]

import { TEN_MINUTES, describeProblems, simulatePista, snapshotState } from '../tests/pistaSim.js';

const seeds = process.argv.slice(2);
if (!seeds.length) seeds.push('aceite-3-a', 'aceite-3-b', 'aceite-3-c', 'aceite-3-d', 'aceite-3-e');

const pad = (v, n) => String(v).padStart(n);
const totals = { jumps: 0, slides: 0, wallJumps: 0, kicks: 0, ticks: 0 };
const lotSeconds = new Map();
const lotLabels = new Map();
let failed = 0;

console.log(`Aceite da Fase 3 — ${seeds.length} seeds × 10 min na colisão da pista\n`);
console.log(`${'seed'.padEnd(12)} ${'pulos'.padStart(6)} ${'slides'.padStart(7)} ${'wall-j.'.padStart(8)} `
  + `${'empurr.'.padStart(8)} ${'alt. máx.'.padStart(10)} ${'checagem'.padStart(10)} ${'repete'.padStart(7)}  tempo`);
for (const seed of seeds) {
  const t0 = performance.now();
  const { state, stats, log } = simulatePista(seed, TEN_MINUTES, { check: true });
  const again = simulatePista(seed, TEN_MINUTES, { check: false }).state;
  const same = snapshotState(state) === snapshotState(again);
  const ok = log.ok && same;
  if (!ok) failed++;
  totals.jumps += stats.jumps;
  totals.slides += stats.slides;
  totals.wallJumps += stats.wallJumps;
  totals.kicks += stats.kicks;
  totals.ticks += log.checked;
  for (const l of log.report().lots) {
    lotSeconds.set(l.number, (lotSeconds.get(l.number) ?? 0) + l.seconds);
    lotLabels.set(l.number, l.label);
  }
  const check = log.ok ? 'ok' : `${log.penetrations + log.stuck + log.below} falhas`;
  console.log(`${seed.padEnd(12)} ${pad(stats.jumps, 6)} ${pad(stats.slides, 7)} ${pad(stats.wallJumps, 8)} `
    + `${pad(stats.kicks, 8)} ${pad(stats.maxY.toFixed(0), 10)} ${check.padStart(10)} `
    + `${(same ? 'sim' : 'NÃO').padStart(7)}  ${((performance.now() - t0) / 1000).toFixed(1)} s`);
  if (!log.ok) console.log(`  ${describeProblems(log)}`);
}

const minutes = totals.ticks / 64 / 60;
console.log(`\nTotal: ${minutes.toFixed(0)} min simulados · ${totals.ticks} ticks conferidos · ${totals.jumps} pulos · `
  + `${totals.slides} slides · ${totals.wallJumps} wall-jumps · ${totals.kicks} empurrões`);
console.log('Tempo em cada estação (todas as seeds):');
const width = Math.max(...[...lotLabels.values()].map((l) => String(l).length));
for (const [number, seconds] of [...lotSeconds.entries()].sort((a, b) => (a[0] || 99) - (b[0] || 99))) {
  const label = String(lotLabels.get(number)).padEnd(width);
  console.log(`  ${number ? pad(number, 2) : ' —'} ${label} ${pad((seconds / 60).toFixed(1), 5)} min`);
}
const verdict = failed ? `FALHOU em ${failed} de ${seeds.length} seeds.`
  : 'OK: nenhuma penetração, nunca preso, nunca abaixo do chão do estúdio; repetível bit a bit.';
console.log(`\n${verdict}`);
process.exitCode = failed ? 1 : 0;
```

Em `package.json`, trocar:

```
    "moodboard": "node tools/moodboard.mjs",
    "test": "node --test \"tests/**/*.test.js\""
```

por:

```
    "moodboard": "node tools/moodboard.mjs",
    "aceite:fase3": "node tools/phase3-acceptance.mjs",
    "test": "node --test \"tests/**/*.test.js\""
```

- [ ] **Passo 7: Rodar os testes da tarefa e a varredura**

Run: `node --test tests/moveMonitor.test.js tests/pistaFuzz.test.js`
Expected: PASS — todos os testes dos dois arquivos passando.

Run: `node tools/phase3-acceptance.mjs`
Expected: PASS — a tabela das 5 seeds com "ok" e "sim" em todas, o tempo em cada estação e "OK: nenhuma penetração, nunca preso, nunca abaixo do chão do estúdio; repetível bit a bit." (~10 s).

- [ ] **Passo 8: Suíte inteira**

Run: `npm test`
Expected: PASS — 294 testes passando.


Conferir: `wc -l src/modes/matchState.js src/player/playerPawn.js src/clay/ClayMaterial.js src/debug/commands.js` → 430, 452, 528 e 387 linhas (todos abaixo de 600).
- [ ] **Passo final: Commit** (só com o pedido do usuário)

```bash
git add src/data/sandbox.js src/data/configSchema.js src/debug src/modes/matchState.js src/maps/pista/index.js styles/debug.css tests/pistaSim.js tests/pistaFuzz.test.js tests/moveMonitor.test.js tools/phase3-acceptance.mjs package.json
git commit -m "MASSACRE 3.5: monitor do movimento e a varredura de aceite da Fase 3" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Tarefa 7: Verificação no navegador e o aceite da Fase 3

O servidor de desenvolvimento de outro chat pode estar na 5173: usar `massacre-dev-auto` (porta livre) ou uma configuração própria. O painel de preview não concede pointer lock a scripts: a entrada de teclado é a do próprio `KeyboardMouse` do jogo, liberada por script como na 3.2 à 3.4. Não emular um tamanho de tela maior que o painel. A aba do jogo tem de ser a da frente do painel: aba de trás não recebe quadros (`requestAnimationFrame` para) e o jogo congela — fechar as outras abas do painel (`tabs_context`, `tabs_close`, `tabs_select`).

- [ ] **Passo 1:** `preview_start`; pelo `javascript_tool`, `await massacre.states.go('match', { map: 'pista', mode: 'livre' })`.
- [ ] **Passo 2: Ajudante de entrada, ticks e robôs** (colar no `javascript_tool`; o mesmo da 3.4). O navegador pode mandar o `pointerlockerror` do pedido de captura depois do carregamento, o que desfaz a captura liberada e abre a pausa: `__t.unpause()` fecha a pausa e libera de novo.

```js
const m = massacre;
const T = {
  lock() { const k = m.input.kbm; k.pointerLocked = true; k.listener.onLockChange(true); },
  unpause() {
    const s = m.states.current;
    if (s.paused) {
      s.paused = false;
      s.pausedMs += performance.now() - s.pauseStart;
      s.pause.hide();
      m.input.setContext('game');
    }
    T.lock();
  },
  down(code) { window.dispatchEvent(new KeyboardEvent('keydown', { code, key: code, bubbles: true })); },
  up(code) { window.dispatchEvent(new KeyboardEvent('keyup', { code, key: code, bubbles: true })); },
  exec(line) { m.console.execute(line); return [...m.console.log.children].slice(-3).map((r) => r.textContent); },
  pawn: () => m.states.current.player,
  /** Roda `fn(i)` antes de cada tick da partida até devolver true (ou `max` ticks). */
  bot(fn, max = 600) {
    const s = m.states.current;
    const tick = Object.getPrototypeOf(s).tick;
    let i = 0;
    return new Promise((done) => {
      s.tick = function (dt, ti) {
        if (i >= max || fn(i++)) { delete s.tick; done(i); }
        return tick.call(this, dt, ti);
      };
    });
  },
};
window.__t = T;
T.unpause();
```

- [ ] **Passo 3: Pegadas na placa** — `__t.exec('estacao pegadas')` (de frente para as placas); andar com W até passar a placa verde (`s.origin.z > 1600`): passos em z ≈ 1513 e 1588 marcam a placa `pegadas-3` (o de z ≈ 1419, no kraft, não) e `pegadas` no console lista "pegadas-3 (15,x s)". Pular parado na placa (`__t.down('Space')`, 3 ticks, `__t.up('Space')`), `timescale 0.05` (o esmaecimento é no tempo de jogo) e olhar de perto (`setpos <x> 5.3 <z + 18> 0 -80` agachado): o par da saída do pulo e do pouso lado a lado, os bicos para fora, o corte reto do bico, as barras transversais na frente, as longitudinais no calcanhar, o arco liso, a parede nítida e o lábio claro em volta; o passo mais raso atrás. `timescale 1`.
- [ ] **Passo 4: GPU × JS, texel a texel** — com a partida pausada por script (sem tick, a fila não anda):

```js
const st = massacre.states.current;
const prints = st.prints;
const M = await import('/src/clay/prints/marks.js');
const FP = (await import('/src/data/footprints.js')).FOOTPRINTS;
st.paused = true;
prints.clear();
const si = 3;
const surf = prints.surfaces[si];
const W = surf.size.width, H = surf.size.height;
const marks = [
  { ...M.footMark(-20, 0, 10, 0.7, 0, FP.marks.land), fades: 0 },
  { ...M.footMark(25, 0, -8, -2.1, 1, FP.marks.jump), fades: 37 },
  ...M.grooveMarks(-50, -40, -20, -10, 0).map((g) => ({ ...g, fades: 5 })),
  { ...M.moundMark(40, 0, 30, 0.6, -0.8), fades: 0 },
];
for (const m of marks) prints.queue.push(si, m);
prints.onPose();
const buf = new Uint8Array(W * H * 4);
massacre.render.renderer.readRenderTargetPixels(surf.target, 0, 0, W, H, buf);
const maxDiff = [0, 0, 0]; let over = 0; let nonzero = 0; const worst = [];
const px = [0, 0, 0], ref = [0, 0, 0];
for (let j = 0; j < H; j++) for (let i = 0; i < W; i++) {
  const x = -surf.width / 2 + (i + 0.5) * surf.width / W;
  const z = -surf.depth / 2 + (j + 0.5) * surf.depth / H;
  ref[0] = ref[1] = ref[2] = 0;
  for (const m of marks) { M.markTexel(m, x, z, m.fades, px); for (let c = 0; c < 3; c++) ref[c] = Math.max(ref[c], px[c]); }
  const k = (j * W + i) * 4;
  let bad = false;
  for (let c = 0; c < 3; c++) { const d = Math.abs(buf[k + c] - ref[c]); maxDiff[c] = Math.max(maxDiff[c], d); if (d > 2) bad = true; }
  if (ref[0] || ref[1] || ref[2]) nonzero++;
  if (bad) { over++; if (worst.length < 8) worst.push({ i, j, gpu: [buf[k], buf[k + 1], buf[k + 2]], js: [...ref] }); }
}
st.paused = false; __t.unpause();
({ nonzero, maxDiff, over, worst });
```

  Esperado: ~22 900 texels marcados em 374 400; o lábio (G) igual até 1/255; fundo (R) e brilho (B) iguais até 2/255 fora dos poucos texels exatamente em cima de um degrau — a borda de uma barra de cravo (`fract` no limiar) ou o fim do brilho (`d < 2,4`), onde o float da GPU e o double do JS caem de lados diferentes (na verificação: 2 texels).
- [ ] **Passo 5: Esmaecimento em 8 bits** — de novo pausado e com `prints.clear()`: carimbar um pouso e um passo (`fades: 0`), aplicar os passos com `prints.queue.advance(n / 12); prints.onPose()` em 1, 84, 106 e 64 passos e comparar o alvo com `M.fadeTexel(ref, total)` a cada vez: diferença até 1/255 (fora o texel de degrau do brilho enquanto ele existe); o brilho some em 85, o passo em 191, o pouso em 255, com a vida da placa em 254, 170, 64 e 0; depois de zerada, `prints.counts.draws` não sobe mais.
- [ ] **Passo 6: Corpo** — `thirdperson`: o boneco com as botas marrons; `timescale 0.08` e um pulo: no ar, esticado (`st.body.pivot.scale` ≈ 0,954 / 1,099 / 0,954) e a sombra de contato no chão embaixo, menor e mais clara (≈ 28 u e 0,36 a ~49 u de altura); no pouso, achatado. `timescale 1`, `firstperson`. Na sala de testes (`massacre.states.go('match', { map: 'testroom', mode: 'livre' })`, `__t.unpause()`, `setpos 0 0 110 0 -18`): o boneco de escala sobre as botas, bicos para fora.
- [ ] **Passo 7: Câmera** — na estação 1, W por 90 ticks gravando `p.feel`: no nível Médio (60/70/65), vertical de −0,65 u no tick do passo a +0,37 u no meio da passada, lateral ±0,6 u, rolagem ±0,19°, passo a cada 19 ticks (297 ms: o relógio de 291 ms do CS em ticks de 64 Hz); com `accessibility.cameraBob` 100, o ponto mais baixo em −1,08 u; com "Reduzir movimento", tudo zero. Configurações → Gráficos → "Conforto": três controles (60%, 70%, 65%) com as dicas e o "Reduzir movimento (sem balanço, flicker nem boil)" com "zera os três acima".
- [ ] **Passo 8: Slide, poço e counter-strafe** — os roteiros da 3.4 (`docs/phases/phase-3.4-plan.md`, Tarefa 8, passos 4 e 5) com a faca: slide de 151,2 u em 0,61 s, 300 → 204,7 u/s, "tempo", com a inclinação de −3,2° e o mergulho de −1,2 u no Médio; poço com ápice de 253 u, de pé a 230 u, 4 wall-jumps, o chute do primeiro com ~3,9°. Counter-strafe na estação 1 com `cl_showpos 1` (A por 50 ticks e D até parar, 3 vezes; depois soltar, 3 vezes), com a faca e com a AK: "contra" em 5 ticks (78 ms) e "soltar" em 13 ticks (203 ms) nas duas.
- [ ] **Passo 9: Memória** — menu ↔ pista 3× (andando até a placa em cada entrada): geometrias, texturas e programas iguais em cada entrada e em cada saída (na verificação: 40 / 90 / 44 e 2 / 34 / 21 na cópia de trabalho; 40 / 90 / 43 e 2 / 34 / 20 no projeto, numa sessão nova); o heap volta a ~52 MB depois da coleta (esperar ~30 s no menu). Contando os ouvintes do barramento (o `bus.on` embrulhado da 3.4) em 2 ciclos: nada acumula (`render:context`, `stopmotion:pose` e `player:*` em 0 no menu).
- [ ] **Passo 10: Robô de 10 min** — na pista, com `__t` instalado (a aba na frente): colar o robô; ele roda sem bloquear e deixa o estado em `window.__robot`. Acompanhar com `({ ...window.__robot, report: null, t: massacre.states.current.monitor.log.time })`; no fim, `window.__robot.report`, `__robot.slide`, `__robot.well`, `__robot.zigzag` e `__robot.strafe`.

```js
// Robô de 10 min da pista (aceite da Fase 3, subfase 3.5): colar no javascript_tool com a partida na pista e o
// ajudante __t instalado. Roda sem bloquear (o estado fica em window.__robot) e usa só a entrada do KeyboardMouse do
// jogo e o olhar do jogador: as 12 estações (estacao n) com trechos aleatórios na mistura do pistaFuzz (correr, andar,
// agachar, pular, slide, wall-jump, troca de item), os roteiros da 3.4 (faixa do slide, poço das 4 paredes e o
// zigue-zague com a faca e com a AK) e o counter-strafe da AK e da faca; no fim, o relatório do monitor.
window.__robot = { phase: 'começando', done: false, segments: 0, error: null, report: null, strafe: null };
(async () => {
  const R = window.__robot;
  const m = massacre;
  const st = m.states.current;
  const p = () => __t.pawn();
  let seed = 35;
  const rnd = () => {
    seed = (seed + 0x6d2b79f5) | 0;
    let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
  const pick = (arr) => arr[Math.floor(rnd() * arr.length)];
  const held = new Set();
  const key = (code, on) => {
    if (on && !held.has(code)) { held.add(code); __t.down(code); }
    if (!on && held.has(code)) { held.delete(code); __t.up(code); }
  };
  const releaseAll = () => { for (const c of [...held]) key(c, false); };
  const guard = () => { if (st.paused) __t.unpause(); };
  const START = performance.now();
  const elapsed = () => (performance.now() - START) / 1000;
  /** Trechos aleatórios por `seconds` s (de jogo, contados em ticks). */
  async function wander(seconds) {
    let phase = 0, turn = 0, rates = { jump: 0, duck: 0, walk: 0 }, f = 0, sd = 0;
    await __t.bot((i) => {
      guard();
      const pw = p();
      if (phase-- <= 0) {
        R.segments++;
        phase = 16 + Math.floor(rnd() * 49);
        f = rnd() < 0.3 ? (rnd() < 0.5 ? -1 : 1) * (rnd() < 0.7 ? 1 : 0) : pick([-1, 0, 1]);
        sd = rnd() < 0.3 ? (rnd() < 0.5 ? -1 : 1) * (rnd() < 0.7 ? 1 : 0) : pick([-1, 0, 1]);
        turn = -5 + rnd() * 10;
        rates = { jump: pick([0, 0.05, 0.3]), duck: pick([0, 0, 0.5, 1]), walk: pick([0, 0, 1]) };
        const item = pick(['Digit1', 'Digit3', 'Digit2', null]);
        if (item) { __t.down(item); __t.up(item); }
      }
      key('KeyW', f > 0); key('KeyS', f < 0); key('KeyD', sd > 0); key('KeyA', sd < 0);
      key('ShiftLeft', rates.walk > 0);
      key('Space', rnd() < rates.jump);
      key('ControlLeft', rnd() < rates.duck);
      pw.yaw += turn / 64;
      return i >= seconds * 64;
    }, seconds * 64 + 10);
    releaseAll();
  }
  try {
    __t.exec('give ak47');
    __t.exec('cl_monitor 1');
    __t.exec('monitor zerar');
    for (let n = 1; n <= 12; n++) {
      R.phase = `estação ${n}`;
      __t.exec(`estacao ${n}`);
      await wander(35);
    }
    // Roteiros da 3.4: faixa do slide, poço das 4 paredes e zigue-zague.
    R.phase = 'faixa do slide';
    __t.down('Digit3'); __t.up('Digit3');
    __t.exec('estacao slide faixa');
    await __t.bot((i) => i > 8, 20);
    {
      const s = p().state;
      key('KeyW', true);
      await __t.bot(() => { guard(); if (s.origin.x >= -2096) key('ControlLeft', true); return s.origin.x > -1900; }, 900);
      releaseAll();
      R.slide = p().lastSlide;
    }
    R.phase = 'poço das 4 paredes';
    __t.exec('setpos -2498 0 202 0 0');
    await __t.bot((i) => i > 5, 10);
    {
      const pw = p(); const s = pw.state;
      const cx = -2450, cz = 150, h = 72, along = 36; const N = { N: [0, 1], S: [0, -1], E: [-1, 0], W: [1, 0] };
      const order = ['E', 'N', 'S', 'W'];
      const aim = (k) => (order[k] ? [cx - N[order[k]][0] * h + N[order[k]][1] * along, cz - N[order[k]][1] * h - N[order[k]][0] * along] : [-2298, cz]);
      const yawTo = ([x, z]) => Math.atan2(-(x - s.origin.x), -(z - s.origin.z));
      let jumped = false; let apex = 0;
      key('KeyW', true);
      const before = pw.stats.wallJumps;
      await __t.bot((i) => {
        guard();
        const k = s.wallJumps;
        if (!jumped) {
          pw.yaw = yawTo(aim(0));
          if (!(s.onGround && Math.hypot(aim(0)[0] - s.origin.x, aim(0)[1] - s.origin.z) > 90)) { jumped = true; key('Space', true); }
        } else {
          const w = order[k];
          const touching = w && s.wallTime <= 0.12 + 1e-9 && Math.abs(s.wallNx - N[w][0]) < 0.3 && Math.abs(s.wallNz - N[w][1]) < 0.3;
          pw.yaw = yawTo(aim(touching ? k + 1 : k));
          key('Space', i % 2 === 0 && k < 4 && !s.onGround);
        }
        apex = Math.max(apex, s.origin.y);
        return i > 200;
      }, 400);
      releaseAll();
      R.well = { apex, y: s.origin.y, wallJumps: pw.stats.wallJumps - before };
    }
    // Zigue-zague (o roteiro do teste crossZigzag), com a faca e com a AK: corre em A, pula na borda mirando o painel 0;
    // encostado no painel k, mira o seguinte a 35% do comprimento dele e pula a cada 2 ticks; em B, para.
    R.phase = 'zigue-zague';
    R.zigzag = {};
    for (const [label, slot] of [['faca', 'Digit3'], ['ak47', 'Digit1']]) {
      __t.down(slot); __t.up(slot);
      const pw = p(); const s = pw.state;
      const Z = { x: [-1822, -1678], A: [700, 900], B: [-44, 156], y: 128, panels: [[564, 700], [428, 564], [292, 428], [156, 292]] };
      const zx = (Z.x[0] + Z.x[1]) / 2; const half = (Z.x[1] - Z.x[0]) / 2 - 16;
      const target = (k) => (k < 4 ? [zx + (k % 2 === 0 ? -half : half), Z.panels[k][1] - (Z.panels[k][1] - Z.panels[k][0]) * 0.35] : [zx, (Z.B[0] + Z.B[1]) / 2]);
      const yawTo = ([x, z]) => Math.atan2(-(x - s.origin.x), -(z - s.origin.z));
      __t.exec(`setpos ${zx} ${Z.y} ${Z.A[1] - 20} 0 0`);
      await __t.bot((i) => { guard(); return i > 20; }, 30);
      let jumped = -1; let landed = false; let edgeY = null;
      key('KeyW', true);
      await __t.bot((i) => {
        guard();
        if (edgeY === null && s.origin.z < Z.B[1]) edgeY = s.origin.y;
        if (jumped < 0) {
          pw.yaw = 0;
          if (!(s.onGround && s.origin.z > Z.A[0] + 8)) { jumped = i; pw.yaw = yawTo(target(0)); key('Space', true); }
          return false;
        }
        if (landed || (s.onGround && i > jumped + 4)) { landed = true; return true; }
        const k = s.wallJumps;
        const touching = k < 4 && s.wallTime <= 0.12 + 1e-9 && Math.abs(s.wallNx - (k % 2 === 0 ? 1 : -1)) < 0.3;
        pw.yaw = yawTo(target(touching ? k + 1 : k));
        key('Space', touching && i % 2 === 0);
        return false;
      }, 500);
      releaseAll();
      R.zigzag[label] = { z: s.origin.z, y: s.origin.y, wallJumps: pw.lastWallJump?.count, folga: edgeY === null ? null : edgeY - Z.y };
    }
    // Counter-strafe: contra × soltar, com a faca e com a AK.
    R.phase = 'counter-strafe';
    __t.exec('estacao 1');
    __t.exec('cl_showpos 1');
    const strafe = {};
    for (const [label, slot] of [['faca', 'Digit3'], ['ak47', 'Digit1']]) {
      __t.down(slot); __t.up(slot);
      await __t.bot((i) => i > 20, 30);
      __t.exec('cl_strafe_reset');
      const s = p().state;
      for (let k = 0; k < 6; k++) {
        const counter = k < 3;
        key('KeyA', true); await __t.bot((i) => { guard(); return i > 50; }, 60); key('KeyA', false);
        if (counter) { key('KeyD', true); await __t.bot(() => Math.hypot(s.velocity.x, s.velocity.z) < 5, 40); key('KeyD', false); }
        await __t.bot(() => Math.hypot(s.velocity.x, s.velocity.z) < 1, 80);
        await __t.bot((i) => i > 8, 10);
      }
      const sc = st.strafe.scores;
      strafe[label] = { contra: { n: sc.contra.count, ms: sc.contra.avg }, soltar: { n: sc.soltar.count, ms: sc.soltar.avg } };
    }
    R.strafe = strafe;
    __t.exec('cl_showpos 0');
    // O resto dos 10 min: mais trechos aleatórios, uma estação sorteada a cada 30 s.
    while (st.monitor.log.time < 600) {
      const n = 1 + Math.floor(rnd() * 12);
      R.phase = `aleatório · estação ${n} · ${(st.monitor.log.time / 60).toFixed(1)} min`;
      __t.exec(`estacao ${n}`);
      await wander(Math.min(30, 600 - st.monitor.log.time + 0.5));
    }
    R.phase = 'fim';
    R.report = st.monitor.report();
    R.minutes = elapsed() / 60;
  } catch (err) {
    R.error = String(err?.stack ?? err);
  } finally {
    releaseAll();
    R.done = true;
  }
})();
'robô andando';
```

  Esperado: o slide, o poço e o counter-strafe como no passo 8; o zigue-zague em B com 4 wall-jumps, com a faca e com a AK (como na 3.4); "penetração 0 · preso 0 · abaixo do chão 0 → OK" em 10 min de jogo, o tempo nas 12 estações, FPS e 1% low da sessão (na verificação, 143,9 de média e 1% low de 119–121 numa tela de 144 Hz) e a memória sem subir: texturas e programas parados, geometrias só quando uma peça entra em cena pela primeira vez (46 → 47 na verificação no projeto); o painel mostra a janela de 5 s e a média da sessão.
- [ ] **Passo 11: O usuário joga 10 min** — pedir ao usuário para jogar 10 min na pista com `cl_monitor 1` (correr, pular, slide, wall-jump nas estações, andar nas placas de massinha), mandar o resultado de `monitor` e contar como sentiu o movimento, a câmera (nível Médio e os outros), o corpo em terceira pessoa e as pegadas. O relato entra no relatório.
- [ ] **Passo 12:** `read_console_messages` sem erros do jogo (o aviso `X4122 … double precision` do compilador de shader do Direct3D sobre as constantes do chunk `packing` do three.js é conhecido e não é do jogo); parar o servidor.

---

### Tarefa 8: Documentação, moodboard e memória

- [ ] **Passo 1:** `docs/art/moodboard.md` — item 12 (sensação: câmera, corpo e pegadas) com os 8 boards novos na tabela (PFT, SQS, BBR, CST, SFP, FIM, SDP, CFS) e só os pins estudados (pin → decisão → arquivo); `docs/art/pinterest-boards.json` com os pins dos 8 boards; `tools/moodboard.mjs` com os boards novos (fase 3.5); `npm run moodboard`.
- [ ] **Passo 2:** `docs/phases/phase-3.md` — 3.5 ✅ com a data na tabela de estado; "Ajustes feitos na implementação" e "Medições no navegador" na seção 3.5; o checklist de aceite da 3.5; "Aceite da Fase 3" marcado com os números.
- [ ] **Passo 3:** `docs/PROGRESS.md` — subfase 3.5 dentro da seção da Fase 3 (arquivos, como testar, números, checklist) e o fechamento da Fase 3 (o aceite: robô, varredura, memória e o relato do usuário).
- [ ] **Passo 4:** memória do projeto (`massacre-game-project.md`): 3.5 pronta, Fase 3 fechada; próxima a Fase 4 (decisão do Blender no começo).
- [ ] **Passo 5:** encerrar pedindo um chat novo para a Fase 4.
