// Testes das formas por contorno do SDF (Fase 4.1): filete dos cantos, distância exata ao polígono, perfil
// recortado e extrudado, torno e tubo — distâncias contra força bruta e contra as formas antigas equivalentes,
// caixa envolvente, intervalo garantido, malha fechada e árvores inválidas.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { bounds, compile, createRange, evaluate, isEmptyBounds } from '../src/clay/sdf/nodes.js';
import { filletPolygon, latheOutline, polygonDistance, signedArea } from '../src/clay/sdf/polygon.js';
import { polygonize } from '../src/clay/sdf/marchingCubes.js';
import { RNG } from '../src/core/rng.js';
import { meshReport } from './sdfTestUtils.js';

const near = (actual, expected, eps = 1e-9, msg = '') => assert.ok(Math.abs(actual - expected) <= eps, `${msg} esperado ${expected}, veio ${actual}`);

// Ponto dentro de polígono por cruzamentos (independente do de iq) e distância aos lados.
function inside(poly, x, y) {
  let c = false;
  for (let i = 0, j = poly.length - 1; i < poly.length; j = i++) {
    const [xi, yi] = poly[i];
    const [xj, yj] = poly[j];
    if ((yi > y) !== (yj > y) && x < ((xj - xi) * (y - yi)) / (yj - yi) + xi) c = !c;
  }
  return c;
}
function segDist(px, py, a, b) {
  const ex = b[0] - a[0];
  const ey = b[1] - a[1];
  const t = Math.max(0, Math.min(1, ((px - a[0]) * ex + (py - a[1]) * ey) / (ex * ex + ey * ey)));
  return Math.hypot(px - a[0] - ex * t, py - a[1] - ey * t);
}
function bruteDistance(poly, x, y) {
  let d = Infinity;
  for (let i = 0; i < poly.length; i++) d = Math.min(d, segDist(x, y, poly[i], poly[(i + 1) % poly.length]));
  return inside(poly, x, y) ? -d : d;
}

// Estrela irregular (cantos convexos e côncavos) — um contorno de peça recortada.
const STAR = Array.from({ length: 14 }, (_, i) => {
  const a = (i / 14) * Math.PI * 2;
  const r = i % 2 ? 3.2 : 6 + (i % 4) * 0.7;
  return [Math.cos(a) * r, Math.sin(a) * r * 0.7];
});

test('polígono: distância exata igual à força bruta, dos dois sentidos de volta', () => {
  const rng = new RNG('poligono');
  for (const poly of [STAR, [...STAR].reverse()]) {
    const d = polygonDistance(poly);
    for (let i = 0; i < 3000; i++) {
      const x = rng.float(-9, 9);
      const y = rng.float(-7, 7);
      near(d(x, y), bruteDistance(poly, x, y), 1e-9, `(${x}, ${y})`);
    }
  }
});

test('filete: arcos tangentes de raio pedido, cantos côncavos cheios, raio limitado pelos lados', () => {
  const square = [[-5, -5], [5, -5], [5, 5], [-5, 5]];
  const f = filletPolygon(square, 1);
  // Cada ponto do contorno fica na borda do quadrado arredondado de raio 1 (distância ao quadrado encolhido = 1).
  const shrunk = polygonDistance([[-4, -4], [4, -4], [4, 4], [-4, 4]]);
  for (const [x, y] of f) near(shrunk(x, y), 1, 1e-9, 'ponto do filete');
  near(Math.abs(signedArea(f)), 100 - (4 - Math.PI), 0.05, 'área do quadrado arredondado');
  // L: o canto côncavo (em (0, 0)) ganha massa; os convexos perdem.
  const L = [[-4, -4], [4, -4], [4, 0], [0, 0], [0, 4], [-4, 4]];
  const fl = polygonDistance(filletPolygon(L, 1));
  assert.ok(fl(0.2, 0.2) < 0, 'canto côncavo cheio pelo filete');
  assert.ok(fl(3.9, -3.9) > 0, 'ponta convexa arredondada');
  near(fl(0.5, -2), polygonDistance(L)(0.5, -2), 1e-9, 'longe dos cantos nada muda');
  // Lado curto: o raio do canto cai para caber em metade dos lados (os arcos vizinhos não se cruzam).
  const thin = filletPolygon([[0, 0], [10, 0], [10, 0.4], [0, 0.4]], 1);
  for (const [, y] of thin) assert.ok(y >= -1e-12 && y <= 0.4 + 1e-12, 'filete limitado não sai da tira');
});

test('perfil: extrusão com as arestas arredondadas e os cantos em filete, exata em pontos conhecidos', () => {
  const p = { type: 'profile', points: [[-5, -2], [5, -2], [5, 2], [-5, 2]], h: 1, round: 0.25, corner: 0.5 };
  near(evaluate(p, 0, 0, 1), 0, 1e-9, 'face de cima (z = h)');
  near(evaluate(p, 0, 0, 0), -1, 1e-9, 'meio');
  near(evaluate(p, 5, 0, 0), 0, 1e-9, 'lado');
  near(evaluate(p, 6, 0, 0), 1, 1e-9, 'fora do lado');
  near(evaluate(p, 0, 0, 2), 1, 1e-9, 'acima da face');
  near(evaluate(p, 5.5, 0, 1.5), Math.hypot(0.75, 0.75) - 0.25, 1e-9, 'aresta arredondada');
  near(evaluate(p, 6, 3, 0), Math.hypot(1.5, 1.5) - 0.5, 1e-9, 'canto em filete');
  // Contra força bruta 3D do sólido arredondado: prisma do contorno encolhido engordado de `round`.
  const rng = new RNG('perfil');
  const shape = { type: 'profile', points: STAR, h: 0.9, round: 0.3, corner: 0.6 };
  const outline = polygonDistance(filletPolygon(STAR, 0.6));
  for (let i = 0; i < 2000; i++) {
    const x = rng.float(-8, 8);
    const y = rng.float(-6, 6);
    const z = rng.float(-2, 2);
    const wx = outline(x, y) + 0.3;
    const wy = Math.abs(z) - 0.6;
    const expect = Math.min(Math.max(wx, wy), 0) + Math.hypot(Math.max(wx, 0), Math.max(wy, 0)) - 0.3;
    near(evaluate(shape, x, y, z), expect, 1e-9);
  }
});

test('torno: igual ao cilindro da biblioteca girado para o eixo X; anel fechado; ponta com filete', () => {
  const lathe = { type: 'lathe', points: [[-5, 0], [-5, 2], [5, 2], [5, 0]] };
  const cyl = { type: 'cylinder', h: 5, r: 2, rot: [0, 0, Math.PI / 2] };
  const rng = new RNG('torno');
  for (let i = 0; i < 2000; i++) {
    const p = [rng.float(-8, 8), rng.float(-4, 4), rng.float(-4, 4)];
    near(evaluate(lathe, ...p), evaluate(cyl, ...p), 1e-9, `(${p})`);
  }
  const ring = { type: 'lathe', closed: true, points: [[-1, 3], [1, 3], [1, 4], [-1, 4]] };
  near(evaluate(ring, 0, 3.5, 0), -0.5);
  near(evaluate(ring, 0, 0, 3.5), -0.5, 1e-9, 'anel gira em volta de X');
  near(evaluate(ring, 0, 0, 0), 3, 1e-9, 'furo do anel');
  const tip = { type: 'lathe', corner: 0.8, points: [[0, 0], [0, 2], [6, 2], [6, 0]] };
  assert.ok(evaluate(tip, 6, 1.7, 0) > 0, 'quina da ponta arredondada');
  near(evaluate(tip, 3, 0, 2), 0, 1e-9, 'meio da lateral intacto');
  assert.deepEqual(latheOutline([[0, 0], [1, 2], [3, 0]], false), [[0, 0], [1, 2], [3, 0], [1, -2]]);
});

test('tubo: um trecho igual à cápsula e ao cone arredondado; vários trechos pegam o mais perto', () => {
  const rng = new RNG('tubo');
  const tube = { type: 'tube', points: [[0, 0, 0], [0, 10, 0]], r: 2 };
  const cap = { type: 'capsule', a: [0, 0, 0], b: [0, 10, 0], r: 2 };
  const cone = { type: 'tube', points: [[0, 0, 0], [0, 10, 0]], radii: [3, 1] };
  const rc = { type: 'roundCone', a: [0, 0, 0], b: [0, 10, 0], ra: 3, rb: 1 };
  const bent = { type: 'tube', points: [[0, 0, 0], [6, 0, 0], [6, 6, 2]], radii: [1, 1.5, 0.8] };
  for (let i = 0; i < 1500; i++) {
    const p = [rng.float(-6, 12), rng.float(-6, 14), rng.float(-6, 6)];
    near(evaluate(tube, ...p), evaluate(cap, ...p), 1e-9);
    near(evaluate(cone, ...p), evaluate(rc, ...p), 1e-9);
    const expect = Math.min(
      evaluate({ type: 'roundCone', a: [0, 0, 0], b: [6, 0, 0], ra: 1, rb: 1.5 }, ...p),
      evaluate({ type: 'roundCone', a: [6, 0, 0], b: [6, 6, 2], ra: 1.5, rb: 0.8 }, ...p),
    );
    near(evaluate(bent, ...p), expect, 1e-9);
  }
});

const TREES = {
  perfil: { type: 'profile', points: STAR, h: 0.8, round: 0.25, corner: 0.5, pos: [1, 2, -1], rot: [0.3, -0.7, 0.2] },
  torno: { type: 'lathe', corner: 0.3, points: [[-4, 0], [-4, 1.5], [-1, 1], [2, 2.2], [4, 1.2], [4, 0]], rot: [0, 0.6, 0.4] },
  anel: { type: 'lathe', closed: true, points: [[-1, 2], [1, 2], [1, 3], [-1, 3]], pos: [0, 1, 0] },
  tubo: { type: 'tube', points: [[0, 0, 0], [5, 1, 0], [6, 5, 3]], radii: [0.8, 1.4, 0.6], rot: [0.2, 0.2, 0.2] },
  uniao: {
    type: 'smoothUnion', k: 0.5, children: [
      { type: 'profile', points: [[0, 0], [8, 0], [8, 2], [0, 2]], h: 1, round: 0.3, corner: 0.4 },
      { type: 'lathe', points: [[7, 0], [7, 0.7], [14, 0.7], [14, 0]], pos: [0, 1, 0], mat: 1 },
    ],
  },
};

test('formas por contorno: a caixa envolvente contém a massa e o intervalo é garantido', () => {
  const rng = new RNG('caixas-contorno');
  const q = createRange();
  for (const [name, tree] of Object.entries(TREES)) {
    const b = bounds(tree);
    assert.ok(!isEmptyBounds(b), name);
    const ext = b.max.map((v, i) => v - b.min[i]);
    let massa = 0;
    for (let i = 0; i < 5000; i++) {
      const p = [0, 1, 2].map((a) => b.min[a] - ext[a] * 0.5 + rng.next() * ext[a] * 2);
      if (evaluate(tree, ...p) > 0) continue;
      massa++;
      for (let a = 0; a < 3; a++) assert.ok(p[a] >= b.min[a] - 1e-9 && p[a] <= b.max[a] + 1e-9, `${name}: massa fora da caixa`);
    }
    assert.ok(massa > 30, `${name}: amostrou a massa`);
    const sdf = compile(tree);
    const plain = compile(tree, { cull: false });
    for (let i = 0; i < 300; i++) {
      const c = [0, 1, 2].map((a) => b.min[a] - 2 + rng.next() * (ext[a] + 4));
      const R = rng.float(0.05, 3);
      sdf.range(...c, R, q);
      for (let j = 0; j < 8; j++) {
        const dir = rng.onUnitSphere();
        const t = R * Math.cbrt(rng.next());
        const p = [c[0] + dir.x * t, c[1] + dir.y * t, c[2] + dir.z * t];
        const d = sdf.distance(...p);
        assert.ok(d >= q.lo - 1e-9 && d <= q.hi + 1e-9, `${name}: fora do intervalo`);
        assert.equal(d, plain.distance(...p), `${name}: a poda mudou a distância`);
      }
    }
  }
});

test('formas por contorno viram malha fechada e bem orientada', () => {
  for (const name of ['perfil', 'torno', 'tubo', 'uniao']) {
    const tree = TREES[name];
    const mesh = polygonize(compile(tree), bounds(tree), { resolution: 56, maxCells: 400000 });
    const r = meshReport(mesh);
    assert.ok(mesh.indices.length > 300, `${name}: gerou triângulos`);
    assert.equal(r.open, 0, `${name}: arestas abertas`);
    assert.equal(r.badWinding, 0, `${name}: triângulos virados`);
  }
});

test('formas por contorno inválidas explicam o problema', () => {
  const bad = [
    [{ type: 'profile', points: [[0, 0], [1, 0]], h: 1 }, /3 a 256 pontos/],
    [{ type: 'profile', points: [[0, 0], [1, 0], [1, 0], [0, 1]], h: 1 }, /repete o ponto anterior/],
    [{ type: 'profile', points: [[0, 0], [1, 0], [0, 1], [0, 0]], h: 1 }, /fecha repetindo o primeiro ponto/],
    [{ type: 'profile', points: [[0, 0], [1, 0], [0, 1]] }, /'h' é obrigatório/],
    [{ type: 'lathe', points: [[0, 1], [2, 1], [2, 0]] }, /começa e termina no eixo/],
    [{ type: 'lathe', points: [[0, 0], [1, -1], [2, 0]] }, /ρ negativo/],
    [{ type: 'lathe', closed: true, points: [[0, 0], [1, 1], [2, 1]] }, /não pode tocar o eixo/],
    [{ type: 'tube', points: [[0, 0, 0], [1, 0, 0]], radii: [1] }, /um raio por ponto/],
    [{ type: 'tube', points: [[0, 0, 0], [1, 0]], r: 1 }, /3 coordenadas/],
  ];
  for (const [tree, re] of bad) assert.throws(() => compile(tree), re, JSON.stringify(tree));
});
