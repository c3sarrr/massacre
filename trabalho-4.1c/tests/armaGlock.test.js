// A Glock-18 de 3ª geração exportada pelo Blender (Fase 4.1c; plano em docs/superpowers/plans/2026-09-28-4.1c-glock-
// m4a4-m9.md, Tarefa 5): a saída inteira passa no validador da classe pistola (níveis, peças, zonas, soquetes,
// triângulos, texturas, tamanho, relatório aprovado com a silhueta e as medidas) e os números que o jogo usa: a boca a
// 105,6 mm da origem (o pino do gatilho), a linha de mira quase horizontal, a janela de ejeção à direita, o seletor à
// esquerda e os eixos das peças móveis (o carregador desce pelo eixo do punho, a 22° da vertical).
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

test('Glock-18: a saída do Blender passa em todas as validações da classe pistola', () => {
  const { problemas, resumo, relatorio, bytes } = validarSaida('glock', RAIZ);
  assert.deepEqual(problemas, []);
  assert.ok(bytes > 0 && bytes <= orcamentoDaArma('glock').arquivosMB * 1024 * 1024);
  assert.equal(relatorio.aprovado, true);
  assert.ok(relatorio.silhueta.iouTolerancia >= 0.98);
  assert.deepEqual(Object.keys(relatorio.medidas).sort(), ['alturaComCarregador', 'alturaSemCarregador', 'cano', 'comprimento', 'raioDeMira']);
  for (const d of Object.values(relatorio.medidas)) assert.ok(Math.abs(d.erro) <= 0.01);
  assert.deepEqual(Object.keys(resumo.lods), ['perto', 'mundo', 'longe']);
  const t = orcamentoDaArma('glock').triangulos;
  for (const n of ['perto', 'mundo', 'longe']) assert.ok(resumo.lods[n].triangulos <= t[n], `${n}: ${resumo.lods[n].triangulos}`);
});

test('Glock-18: soquetes e peças móveis no referencial do jogo', () => {
  const { resumo } = validarSaida('glock', RAIZ);
  const s = resumo.soquetes;
  assert.ok(Math.abs(s.boca.posicao[0] - 105.6 / U) < 0.02, `boca em x = ${s.boca.posicao[0]} u`);
  assert.ok(Math.abs(s.boca.posicao[1]) < 0.01 && Math.abs(s.boca.posicao[2]) < 0.01, 'a boca no eixo do cano');
  assert.ok(Math.abs(s.mira_tras.posicao[1] - s.mira_frente.posicao[1]) < 0.05, 'a linha de mira quase horizontal');
  assert.ok(Math.abs((s.mira_frente.posicao[0] - s.mira_tras.posicao[0]) * U - 166.4) < 1.7, 'o raio de mira da foto');
  assert.ok(s.ejecao.posicao[2] > 0.4, 'a janela de ejeção no lado direito (+Z)');
  assert.ok(s.mao_d.posicao[1] < -1.5 && s.mao_e.posicao[1] < s.mao_d.posicao[1], 'as mãos no punho, a de apoio embaixo');
  const p = resumo.lods.perto.pecas;
  assert.deepEqual(p.ferrolho.extras, { eixo: [-1, 0, 0] });
  const [cx, cy, cz] = p.carregador.extras.eixo;
  assert.ok(Math.abs(Math.atan2(-cx, -cy) * 180 / Math.PI - 22) < 0.1 && cz === 0, 'o carregador desce pelo eixo do punho');
  for (const n of ['gatilho', 'seletor']) assert.deepEqual(p[n].extras, { eixo_giro: [0, 0, 1] });
  const eixo = [(-170.5 + 105.6) / U, -1.8 / U];
  assert.ok(Math.abs(p.seletor.posicao[0] - eixo[0]) < 0.02 && Math.abs(p.seletor.posicao[1] - eixo[1]) < 0.02, 'o seletor gira no eixo da ficha');
});

test('Glock-18: na posição da categoria pistola, a boca aparece embaixo à direita da tela (16:9, valores padrão)', () => {
  const { resumo } = validarSaida('glock', RAIZ);
  const offset = { x: VIEWMODEL.offset.x.default, y: VIEWMODEL.offset.y.default, z: VIEWMODEL.offset.z.default };
  const pl = viewPlacement(viewCategory('glock'), { offset, nudge: weaponNudge('glock') });
  const t = Math.tan((viewmodelVerticalFov(VIEWMODEL.fov.default) * Math.PI) / 360);
  const p = new THREE.Vector3(...resumo.soquetes.boca.posicao).applyQuaternion(pl.quaternion).add(pl.position);
  const x = p.x / (-p.z * t * (16 / 9));
  const y = p.y / (-p.z * t);
  assert.ok(p.z < -VIEWMODEL.near && Math.abs(x) < 1 && Math.abs(y) < 1, `a boca fora da tela (${x.toFixed(2)}, ${y.toFixed(2)})`);
  assert.ok(x > -0.2 && y < 0.1, `a arma embaixo à direita (${x.toFixed(2)}, ${y.toFixed(2)})`);
});
