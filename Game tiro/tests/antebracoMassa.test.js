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
