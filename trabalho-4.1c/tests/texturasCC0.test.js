// Texturas CC0 do Blender (decisão do usuário de 2026-09-27; CLAUDE.md, seção 0.7): o registro em
// tools/blender/texturas/fontes.json com a página, a licença, a data, a medida e o md5 de cada arquivo, os arquivos ao
// lado com o md5 e o tamanho do registro; e a madeira da revisão crítica da P1 da 4.1c — o veio da lâmina de cerejeira
// no canal A da _m, com a mesma conta no jogo (o padrão `veio` do shader) e no modelo alto do Blender.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { existsSync, readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { join } from 'node:path';
import { ACABAMENTOS } from '../src/data/acabamentos.js';
import { ARMA_FRAGMENT_PARS } from '../src/weapons/model/glsl/acabamentos.js';

const PASTA = fileURLToPath(new URL('../tools/blender/texturas/', import.meta.url));

/** Largura e altura de um JPEG pelo marcador SOF (baseline ou progressivo). */
function tamanhoJpeg(buf) {
  assert.equal(buf.readUInt16BE(0), 0xffd8, 'não é um JPEG');
  let i = 2;
  while (i < buf.length) {
    const marcador = buf.readUInt16BE(i);
    const tamanho = buf.readUInt16BE(i + 2);
    if ([0xffc0, 0xffc1, 0xffc2].includes(marcador)) return [buf.readUInt16BE(i + 7), buf.readUInt16BE(i + 5)];
    i += 2 + tamanho;
  }
  throw new Error('JPEG sem o marcador SOF');
}

test('texturas CC0: cada uma registrada com a página, a licença, a data, a medida e o md5 dos arquivos', () => {
  const fontes = JSON.parse(readFileSync(join(PASTA, 'fontes.json'), 'utf8'));
  assert.ok(fontes.texturas.length >= 1);
  const ids = new Set();
  for (const t of fontes.texturas) {
    assert.ok(!ids.has(t.id), `${t.id} repetida`);
    ids.add(t.id);
    assert.match(t.pagina, /^https:\/\//, `${t.id}: página`);
    assert.ok(t.site && t.nome && t.autor && t.uso, `${t.id}: site, nome, autor e uso`);
    assert.match(t.licenca, /^CC0/, `${t.id}: só CC0`);
    assert.match(t.data, /^\d{4}-\d{2}-\d{2}$/, `${t.id}: data`);
    assert.ok(t.mm.length === 2 && t.mm.every((v) => v > 0), `${t.id}: a medida da textura (mm)`);
    for (const [arquivo, info] of Object.entries(t.arquivos)) {
      const caminho = join(PASTA, t.id, arquivo);
      assert.ok(existsSync(caminho), `${t.id}/${arquivo} ao lado do registro`);
      const buf = readFileSync(caminho);
      assert.equal(createHash('md5').update(buf).digest('hex'), info.md5, `${t.id}/${arquivo}: md5`);
      if (arquivo.endsWith('.jpg')) assert.deepEqual(tamanhoJpeg(buf), info.px, `${t.id}/${arquivo}: px`);
    }
  }
  assert.ok(ids.has('cherry_veneer'), 'a lâmina de cerejeira da madeira');
});

test('madeira: a conta do veio da tabela, a mesma no padrão do shader', () => {
  const v = ACABAMENTOS.madeira.veio;
  assert.deepEqual({ ...v }, { claro: 0.62, escuro: 0.22, peso: 0.8 });
  assert.ok(v.claro > v.escuro && v.peso > 0 && v.peso <= 1);
  // o padrão 5 (veio) lê o canal A com os números da tabela, em curva suave e com as bordas em ordem (o GLSL não
  // define o smoothstep com a borda de baixo maior que a de cima)
  assert.match(ARMA_FRAGMENT_PARS, /\( 1\.0 - smoothstep\( 0\.2200, 0\.6200, varAssada \) \) \* 0\.8000/);
});
