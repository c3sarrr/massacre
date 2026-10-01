// A M4A4 do jogo (a carabina M4A1) exportada pelo Blender (Fase 4.1c; plano em docs/superpowers/plans/2026-09-28-4.1c-
// glock-m4a4-m9.md, Tarefa 6): a saída inteira passa no validador da classe fuzil (níveis, peças, zonas, soquetes,
// triângulos, texturas, tamanho, relatório aprovado com a silhueta e as medidas) e os números que o jogo usa: a boca a
// 504 mm da origem (o pino do gatilho), a linha de mira quase horizontal, a janela de ejeção à direita, as peças móveis
// novas (a alavanca de manejo e a tampa da janela, com a dobradiça na face direita), a pega rifle das duas mãos (Tarefa
// 10) e a posição na tela da categoria rifle.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { fileURLToPath } from 'node:url';
import * as THREE from 'three';
import { VIEWMODEL } from '../src/data/viewmodel.js';
import { orcamentoDaArma } from '../src/data/armasReais.js';
import { viewCategory, viewPlacement, viewmodelVerticalFov, weaponNudge } from '../src/weapons/viewmodel/placement.js';
import { validarSaida } from '../tools/blender/saida.mjs';

const RAIZ = fileURLToPath(new URL('..', import.meta.url));
const U = 25.4;

test('M4A4: a saída do Blender passa em todas as validações da classe fuzil', () => {
  const { problemas, resumo, relatorio, bytes } = validarSaida('m4a4', RAIZ);
  assert.deepEqual(problemas, []);
  assert.ok(bytes > 0 && bytes <= orcamentoDaArma('m4a4').arquivosMB * 1024 * 1024);
  assert.equal(relatorio.aprovado, true);
  assert.ok(relatorio.silhueta.iouTolerancia >= 0.98);
  // o relevo moldado (correções da P1 da 4.1c): o losango do punho A2
  assert.deepEqual(Object.keys(relatorio.relevos), ['guarnicao']);
  for (const d of Object.values(relatorio.medidas)) assert.ok(Math.abs(d.erro) <= 0.01);
  const t = orcamentoDaArma('m4a4').triangulos;
  for (const n of ['perto', 'mundo', 'longe']) assert.ok(resumo.lods[n].triangulos <= t[n], `${n}: ${resumo.lods[n].triangulos}`);
});

test('M4A4: soquetes e peças móveis no referencial do jogo', () => {
  const { resumo } = validarSaida('m4a4', RAIZ);
  const s = resumo.soquetes;
  assert.ok(Math.abs(s.boca.posicao[0] - 504 / U) < 0.02, `boca em x = ${s.boca.posicao[0]} u`);
  assert.ok(Math.abs(s.boca.posicao[1]) < 0.01 && Math.abs(s.boca.posicao[2]) < 0.01, 'a boca no eixo do cano');
  assert.ok(Math.abs(s.mira_tras.posicao[1] - s.mira_frente.posicao[1]) < 0.05, 'a linha de mira quase horizontal');
  assert.ok(Math.abs((s.mira_frente.posicao[0] - s.mira_tras.posicao[0]) * U - 361) < 3.6, 'o raio de mira da ficha (±1 %)');
  assert.ok(s.ejecao.posicao[2] > 0.4, 'a janela de ejeção no lado direito (+Z)');
  const p = resumo.lods.perto.pecas;
  for (const n of ['ferrolho', 'alavanca']) assert.deepEqual(p[n].extras, { eixo: [-1, 0, 0] });
  assert.deepEqual(p.carregador.extras, { eixo: [0, -1, 0] });
  assert.deepEqual(p.tampa.extras, { eixo_giro: [1, 0, 0] });
  assert.ok(p.tampa.posicao[2] > 0.4, 'a dobradiça da tampa na face direita');
  for (const n of ['gatilho', 'seletor']) assert.deepEqual(p[n].extras, { eixo_giro: [0, 0, 1] });
});

// A pega rifle (Tarefa 10; desenho da 4.1c, seção 4.1): as duas mãos e nada dentro da arma além do limite. A direita
// com a polpa do indicador no gatilho (o contato medido até a peça dele) e a luva apertada no vão do guarda-mato no
// máximo 0,25 mm (o vão de 21,3 mm é mais estreito que a luva), o médio, o anelar e o mínimo lado a lado no punho; a
// da frente com o polegar reto e deitado no trilho esquerdo e os quatro dedos lado a lado do outro lado.
test('M4A4: a pega rifle — o indicador no gatilho, a mão da frente com o polegar no trilho esquerdo', () => {
  const { relatorio } = validarSaida('m4a4', RAIZ);
  const e = relatorio.empunhadura;
  assert.deepEqual(e.maos, ['d', 'e']);
  assert.equal(e.frente, 'e');
  for (const lado of ['d', 'e']) {
    const m = e[lado];
    assert.ok(m.penetracaoMM <= 0.3, `${lado}: a luva entra ${m.penetracaoMM} mm na arma`);
    for (const [k, v] of Object.entries(m.contatosMM)) assert.ok(v <= 1, `${lado}: o contato ${k} a ${v} mm`);
    for (const [par, [media]] of Object.entries(m.juntosMM)) assert.ok(media <= 8, `${lado}: ${par} a ${media} mm`);
  }
  const d = e.d;
  assert.ok(d.contatosMM.indicador_gatilho <= 0.3, `a polpa do indicador a ${d.contatosMM.indicador_gatilho} mm do gatilho`);
  assert.ok(d.indicador.encostou && d.indicador.polpaAoAlvoMM <= 2, `a polpa a ${d.indicador.polpaAoAlvoMM} mm do ponto do gatilho`);
  assert.ok(d.indicador.folgaDoResto >= -0.25, `a luva aperta ${-d.indicador.folgaDoResto} mm no guarda-mato`);
  const f = e.e;
  assert.ok(f.lados.polegarMM > 20, `o polegar a ${f.lados.polegarMM} mm do meio, do lado esquerdo`);
  for (const [dedo, y] of Object.entries(f.lados.dedosMM)) assert.ok(y < -20, `${dedo} a ${y} mm do meio, do lado direito`);
  assert.ok(f.polegar.curvaGraus <= 20, `o polegar com ${f.polegar.curvaGraus}° de curva`);
  assert.ok(Math.max(...f.polegar.trechosMM) <= 8, `o polegar a até ${Math.max(...f.polegar.trechosMM)} mm do trilho`);
});

test('M4A4: na posição da categoria rifle, a boca aparece embaixo à direita da tela (16:9, valores padrão)', () => {
  const { resumo } = validarSaida('m4a4', RAIZ);
  const offset = { x: VIEWMODEL.offset.x.default, y: VIEWMODEL.offset.y.default, z: VIEWMODEL.offset.z.default };
  const pl = viewPlacement(viewCategory('m4a4'), { offset, nudge: weaponNudge('m4a4') });
  const t = Math.tan((viewmodelVerticalFov(VIEWMODEL.fov.default) * Math.PI) / 360);
  const p = new THREE.Vector3(...resumo.soquetes.boca.posicao).applyQuaternion(pl.quaternion).add(pl.position);
  const x = p.x / (-p.z * t * (16 / 9));
  const y = p.y / (-p.z * t);
  assert.ok(p.z < -VIEWMODEL.near && Math.abs(x) < 1 && Math.abs(y) < 1, `a boca fora da tela (${x.toFixed(2)}, ${y.toFixed(2)})`);
  assert.ok(x > -0.2 && y < 0.1, `a arma embaixo à direita (${x.toFixed(2)}, ${y.toFixed(2)})`);
});
