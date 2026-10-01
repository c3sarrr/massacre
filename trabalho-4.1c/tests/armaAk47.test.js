// A AK-47 tipo 3 exportada pelo Blender (Fase 4.1a): a saída inteira passa no validador (níveis, peças, zonas, soquetes,
// triângulos, texturas sem perdas, tamanho, relatório aprovado com a silhueta e as medidas) e os números que o jogo usa:
// a boca a +21,69 u da origem (o pino do gatilho), a linha de mira quase horizontal, a janela de ejeção à direita e os
// eixos das peças móveis.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { fileURLToPath } from 'node:url';
import * as THREE from 'three';
import { VIEWMODEL } from '../src/data/viewmodel.js';
import { viewCategory, viewPlacement, viewmodelVerticalFov, weaponNudge } from '../src/weapons/viewmodel/placement.js';
import { validarSaida } from '../tools/blender/saida.mjs';

const RAIZ = fileURLToPath(new URL('..', import.meta.url));

test('AK-47 tipo 3: a saída do Blender passa em todas as validações', () => {
  const { problemas, resumo, relatorio, bytes } = validarSaida('ak47', RAIZ);
  assert.deepEqual(problemas, []);
  assert.ok(bytes > 0);
  assert.equal(relatorio.aprovado, true);
  assert.ok(relatorio.silhueta.iouTolerancia >= 0.98);
  // sem relevo moldado (a madeira e o metal da AK): o _n sem o canal alfa vale, o jogo lê liso
  assert.deepEqual(relatorio.relevos, {});
  for (const d of Object.values(relatorio.medidas)) assert.ok(Math.abs(d.erro) <= 0.01);
  assert.deepEqual(Object.keys(resumo.lods), ['perto', 'mundo', 'longe']);
});

test('AK-47 tipo 3: soquetes e peças móveis no referencial do jogo', () => {
  const { resumo } = validarSaida('ak47', RAIZ);
  const boca = resumo.soquetes.boca.posicao;
  assert.ok(Math.abs(boca[0] - 551 / 25.4) < 0.02, `boca em x = ${boca[0]} u`);
  assert.ok(Math.abs(boca[1]) < 0.01 && Math.abs(boca[2]) < 0.01, 'a boca no eixo do cano');
  const tras = resumo.soquetes.mira_tras.posicao;
  const frente = resumo.soquetes.mira_frente.posicao;
  assert.ok(Math.abs(tras[1] - frente[1]) < 0.05, 'a linha de mira quase horizontal');
  assert.ok(resumo.soquetes.ejecao.posicao[2] > 0.5, 'a janela de ejeção no lado direito (+Z)');
  assert.deepEqual(resumo.lods.perto.pecas.ferrolho.extras, { eixo: [-1, 0, 0] });
  for (const p of ['carregador', 'gatilho', 'cao', 'seletor']) assert.deepEqual(resumo.lods.perto.pecas[p].extras, { eixo_giro: [0, 0, 1] });
});

test('AK-47 tipo 3: na posição da categoria rifle, a boca aparece embaixo à direita da tela (16:9, valores padrão)', () => {
  const { resumo } = validarSaida('ak47', RAIZ);
  const offset = { x: VIEWMODEL.offset.x.default, y: VIEWMODEL.offset.y.default, z: VIEWMODEL.offset.z.default };
  const pl = viewPlacement(viewCategory('ak47'), { offset, nudge: weaponNudge('ak47') });
  const t = Math.tan((viewmodelVerticalFov(VIEWMODEL.fov.default) * Math.PI) / 360);
  const p = new THREE.Vector3(...resumo.soquetes.boca.posicao).applyQuaternion(pl.quaternion).add(pl.position);
  const x = p.x / (-p.z * t * (16 / 9));
  const y = p.y / (-p.z * t);
  assert.ok(p.z < -VIEWMODEL.near && Math.abs(x) < 1 && Math.abs(y) < 1, `a boca fora da tela (${x.toFixed(2)}, ${y.toFixed(2)})`);
  assert.ok(x > -0.2 && y < 0.1, `a arma embaixo à direita (${x.toFixed(2)}, ${y.toFixed(2)})`);
});
