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
