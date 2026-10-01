// A faca do jogo, a baioneta M9, exportada pelo Blender (Fase 4.1c; plano em docs/superpowers/plans/2026-09-28-4.1c-
// glock-m4a4-m9.md, Tarefa 7): a saída inteira passa no validador da classe faca (a base só, as três zonas, os
// soquetes da mão e da ponta, triângulos, texturas, tamanho, relatório aprovado com a silhueta e as medidas da lâmina)
// e os números que o jogo usa: a ponta a 177,6 mm da origem (a frente da guarda), no alto do eixo do cabo, e a mão no
// meio do cabo.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { fileURLToPath } from 'node:url';
import { orcamentoDaArma, soquetesDaArma, zonasDaArma } from '../src/data/armasReais.js';
import { validarSaida } from '../tools/blender/saida.mjs';

const RAIZ = fileURLToPath(new URL('..', import.meta.url));
const U = 25.4;

test('faca M9: a saída do Blender passa em todas as validações da classe faca', () => {
  const { problemas, resumo, relatorio, bytes } = validarSaida('knife', RAIZ);
  assert.deepEqual(problemas, []);
  assert.ok(bytes > 0 && bytes <= orcamentoDaArma('knife').arquivosMB * 1024 * 1024);
  assert.equal(relatorio.aprovado, true);
  assert.ok(relatorio.silhueta.iouTolerancia >= 0.98);
  // o relevo moldado (correções da P1 da 4.1c): o recartilhado dos segmentos do cabo
  assert.deepEqual(Object.keys(relatorio.relevos), ['guarnicao']);
  assert.deepEqual(Object.keys(relatorio.medidas).sort(), ['comprimento', 'espessuraLamina', 'lamina']);
  for (const d of Object.values(relatorio.medidas)) assert.ok(Math.abs(d.erro) <= 0.01);
  assert.deepEqual([...resumo.zonas].sort(), [...zonasDaArma('knife')].sort());
  const t = orcamentoDaArma('knife').triangulos;
  for (const n of ['perto', 'mundo', 'longe']) assert.ok(resumo.lods[n].triangulos <= t[n], `${n}: ${resumo.lods[n].triangulos}`);
  assert.deepEqual(Object.keys(resumo.lods.perto.pecas), ['base'], 'a faca é uma peça só');
});

test('faca M9: a ponta e a mão no referencial do jogo', () => {
  const { resumo } = validarSaida('knife', RAIZ);
  const s = resumo.soquetes;
  assert.deepEqual(Object.keys(s).sort(), [...soquetesDaArma('knife')].sort());
  assert.ok(Math.abs(s.ponta.posicao[0] - 177.6 / U) < 0.02, `a ponta em x = ${s.ponta.posicao[0]} u`);
  assert.ok(s.ponta.posicao[1] > 0 && s.ponta.posicao[1] < 0.3, 'a ponta um pouco acima do eixo do cabo (o clip)');
  assert.ok(Math.abs(s.mao_d.posicao[0] - (-245 + 177.6) / U) < 0.02 && Math.abs(s.mao_d.posicao[1]) < 0.01, 'a mão no meio do cabo');
});
