// A M4A4 do jogo (a carabina M4A1) exportada pelo Blender (Fase 4.1c; plano em docs/superpowers/plans/2026-09-28-4.1c-
// glock-m4a4-m9.md, Tarefa 6): a saída inteira passa no validador da classe fuzil (níveis, peças, zonas, soquetes,
// triângulos, texturas, tamanho, relatório aprovado com a silhueta e as medidas) e os números que o jogo usa: a boca a
// 504 mm da origem (o pino do gatilho), a linha de mira quase horizontal, a janela de ejeção à direita, as peças móveis
// novas (a alavanca de manejo e a tampa da janela, com a dobradiça na face direita) e a posição na tela da categoria rifle.
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
