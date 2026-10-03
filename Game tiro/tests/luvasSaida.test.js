// Validador da saída das luvas (Fase 4.1b; plano, Tarefa 6), com a saída montada no teste numa pasta temporária: o
// luvas.glb (a raiz `luvas` com a marca do rig nos extras, as duas armaduras, as duas malhas com skin por zona, o
// atributo `_VERTICE` e as correções das dobras nos extras), as duas texturas e o relatório. A saída de verdade é
// conferida em tests/luvasGlb.test.js.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, mkdirSync, rmSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { tmpdir } from 'node:os';
import { ossosDoLado } from '../src/data/luvas.js';
import { resumoLuvasGlb, validarSaidaLuvas } from '../tools/blender/saidaLuvas.mjs';

/** Monta um .glb com o JSON e um binário (os dois alinhados a 4 bytes). */
function montarGlb(json, bin = Buffer.alloc(0)) {
  let j = Buffer.from(JSON.stringify(json), 'utf8');
  if (j.length % 4) j = Buffer.concat([j, Buffer.alloc(4 - (j.length % 4), 0x20)]);
  let b = bin;
  if (b.length % 4) b = Buffer.concat([b, Buffer.alloc(4 - (b.length % 4), 0)]);
  const cab = Buffer.alloc(12);
  cab.writeUInt32LE(0x46546c67, 0);
  cab.writeUInt32LE(2, 4);
  cab.writeUInt32LE(12 + 8 + j.length + (b.length ? 8 + b.length : 0), 8);
  const cj = Buffer.alloc(8);
  cj.writeUInt32LE(j.length, 0);
  cj.writeUInt32LE(0x4e4f534a, 4);
  const partes = [cab, cj, j];
  if (b.length) {
    const cb = Buffer.alloc(8);
    cb.writeUInt32LE(b.length, 0);
    cb.writeUInt32LE(0x004e4942, 4);
    partes.push(cb, b);
  }
  return Buffer.concat(partes);
}

const MARCA = { d: 'a'.repeat(64), e: 'b'.repeat(64) };
const CORRECOES = JSON.stringify({ suaveMM: 0.1, juntas: [{ junta: 'indicador_mcp' }], pecas: { vertices: [] } });

/** O glTF das luvas: `tris` triângulos por zona em cada braço (3 zonas), os 20 ossos de cada lado. */
function gltfLuvas({ tris = 1000, ossos = { d: ossosDoLado('d'), e: ossosDoLado('e') }, zonas = ['couro', 'tecido', 'reforco'] } = {}) {
  const accessors = [];
  const acessor = (count, type = 'VEC3') => {
    accessors.push({ count, componentType: 5126, type });
    return accessors.length - 1;
  };
  const materials = zonas.map((name) => ({ name }));
  const nodes = [{ name: 'luvas', children: [], extras: { marca: { ...MARCA } } }];
  const no = (def, pai) => {
    nodes.push(def);
    nodes[pai].children = [...(nodes[pai].children ?? []), nodes.length - 1];
    return nodes.length - 1;
  };
  const meshes = [];
  const skins = [];
  for (const lado of ['d', 'e']) {
    const rig = no({ name: `rig_${lado}` }, 0);
    const juntas = ossos[lado].map((nome) => no({ name: nome }, rig));
    skins.push({ joints: juntas });
    meshes.push({
      primitives: materials.map((_, material) => ({
        attributes: {
          POSITION: acessor(tris * 3), NORMAL: acessor(tris * 3), TANGENT: acessor(tris * 3, 'VEC4'),
          TEXCOORD_0: acessor(tris * 3, 'VEC2'), JOINTS_0: acessor(tris * 3, 'VEC4'), WEIGHTS_0: acessor(tris * 3, 'VEC4'),
          _VERTICE: acessor(tris * 3, 'SCALAR'),
        },
        indices: acessor(tris * 3, 'SCALAR'),
        material,
      })),
    });
    no({ name: `luva_${lado}`, mesh: meshes.length - 1, skin: skins.length - 1, extras: { correcoes: CORRECOES } }, rig);
  }
  return {
    asset: { version: '2.0' }, scene: 0, scenes: [{ nodes: [0] }], nodes, meshes, skins, accessors, materials,
    extensionsUsed: ['KHR_draco_mesh_compression'], extensionsRequired: ['KHR_draco_mesh_compression'],
  };
}

/** Um .webp VP8L de `lado`×`lado` (só o cabeçalho), com ou sem alfa. */
function webp(lado, alfa = true) {
  const l = Buffer.alloc(5);
  l[0] = 0x2f;
  l.writeUInt32LE(((lado - 1) | ((lado - 1) << 14) | ((alfa ? 1 : 0) << 28)) >>> 0, 1);
  const cab = Buffer.alloc(12);
  cab.write('RIFF', 0, 'ascii');
  cab.writeUInt32LE(4 + 8 + l.length, 4);
  cab.write('WEBP', 8, 'ascii');
  const ch = Buffer.alloc(8);
  ch.write('VP8L', 0, 'ascii');
  ch.writeUInt32LE(l.length, 4);
  return Buffer.concat([cab, ch, l]);
}

function relatorio(tris = 3000) {
  return { luvas: true, aprovado: true, problemas: [], triangulos: { luva: tris, base: tris - 600, detalhes: 600 }, marca: { ...MARCA } };
}

/** Grava a saída sintética numa pasta temporária; `mexer` altera as partes antes. Devolve a raiz. */
function saida(mexer = () => {}) {
  const raiz = mkdtempSync(join(tmpdir(), 'luvas-saida-'));
  const pasta = join(raiz, 'assets', 'maos');
  mkdirSync(pasta, { recursive: true });
  const partes = { gltf: gltfLuvas(), bin: Buffer.alloc(0), n: webp(2048), m: webp(2048), relatorio: relatorio() };
  mexer(partes);
  if (partes.gltf) writeFileSync(join(pasta, 'luvas.glb'), montarGlb(partes.gltf, partes.bin));
  writeFileSync(join(pasta, 'luvas_n.webp'), partes.n);
  writeFileSync(join(pasta, 'luvas_m.webp'), partes.m);
  writeFileSync(join(pasta, 'luvas.relatorio.json'), JSON.stringify(partes.relatorio));
  return raiz;
}

function problemas(mexer) {
  const raiz = saida(mexer);
  try {
    return validarSaidaLuvas(raiz).problemas;
  } finally {
    rmSync(raiz, { recursive: true, force: true });
  }
}

test('saída das luvas: resumo do glb — as duas malhas, os ossos de cada lado, as zonas, os atributos e os extras', () => {
  const r = resumoLuvasGlb(gltfLuvas());
  assert.equal(r.raiz, 'luvas');
  assert.deepEqual(Object.keys(r.malhas), ['luva_d', 'luva_e']);
  assert.equal(r.malhas.luva_d.triangulos, 3000);
  assert.deepEqual(r.malhas.luva_e.ossos, ossosDoLado('e'));
  assert.deepEqual(r.malhas.luva_d.zonas, ['couro', 'tecido', 'reforco']);
  for (const k of ['uv', 'tangentes', 'pesos', 'vertice']) assert.equal(r.malhas.luva_d[k], true, k);
  assert.equal(r.malhas.luva_d.correcoes.juntas, 1);
  assert.deepEqual(r.marca, MARCA);
  assert.equal(r.draco, true);
  // o atributo no acessor 0 (o exportador do Blender põe o _VERTICE primeiro) conta como presente
  const zero = gltfLuvas();
  zero.meshes[0].primitives[0].attributes._VERTICE = 0;
  assert.equal(resumoLuvasGlb(zero).malhas.luva_d.vertice, true);
  assert.throws(() => resumoLuvasGlb({ ...gltfLuvas(), nodes: [{ name: 'ak47' }], scenes: [{ nodes: [0] }] }),
    /a raiz do \.glb é ak47, esperava luvas/);
});

test('saída das luvas: a completa passa', () => {
  assert.deepEqual(problemas(), []);
});

test('saída das luvas: arquivo faltando e relatório reprovado', () => {
  assert.ok(problemas((p) => { p.gltf = null; }).some((m) => m.includes('faltam') && m.includes('luvas.glb')));
  const p = problemas((s) => { s.relatorio = { ...s.relatorio, aprovado: false, problemas: ['pose punho: atravessa 2 mm'] }; });
  assert.ok(p.some((m) => m.includes('o Blender reprovou') && m.includes('atravessa 2 mm')), p.join(' | '));
});

test('saída das luvas: triângulos acima do orçamento dos dois braços e o relatório diferente do glb', () => {
  const p = problemas((s) => {
    s.gltf = gltfLuvas({ tris: 2500 });
    s.relatorio = relatorio(7500);
  });
  assert.ok(p.some((m) => m.includes('15000 triângulos') && m.includes('14000')), p.join(' | '));
  const q = problemas((s) => { s.relatorio = relatorio(2999); });
  assert.ok(q.some((m) => m.includes('luva_d: o relatório diz 2999')), q.join(' | '));
});

test('saída das luvas: osso faltando, com o nome errado ou do outro lado', () => {
  const ossos = { d: ossosDoLado('d'), e: ossosDoLado('e').filter((o) => o !== 'minimo_3_e') };
  let p = problemas((s) => { s.gltf = gltfLuvas({ ossos }); });
  assert.ok(p.some((m) => m.includes('luva_e: falta o osso minimo_3_e')), p.join(' | '));
  ossos.e = [...ossosDoLado('e').slice(0, 19), 'mindinho_3_e'];
  p = problemas((s) => { s.gltf = gltfLuvas({ ossos }); });
  assert.ok(p.some((m) => m.includes('luva_e: osso a mais mindinho_3_e')), p.join(' | '));
  ossos.e = ossosDoLado('d');
  p = problemas((s) => { s.gltf = gltfLuvas({ ossos }); });
  assert.ok(p.some((m) => m.includes('luva_e: falta o osso mao_e')), p.join(' | '));
});

test('saída das luvas: zonas, UV, tangentes, pesos, o índice dos vértices, as correções e o Draco', () => {
  let p = problemas((s) => { s.gltf = gltfLuvas({ zonas: ['couro', 'tecido'] }); });
  assert.ok(p.some((m) => m.includes('luva_d: falta a zona reforco')), p.join(' | '));
  p = problemas((s) => {
    for (const pr of s.gltf.meshes[1].primitives) {
      delete pr.attributes.TEXCOORD_0;
      delete pr.attributes.TANGENT;
      delete pr.attributes.WEIGHTS_0;
      delete pr.attributes._VERTICE;
    }
    delete s.gltf.nodes.find((n) => n.name === 'luva_e').extras;
    delete s.gltf.extensionsUsed;
  });
  for (const esperado of ['luva_e: primitiva sem UV', 'luva_e: primitiva sem tangentes', 'luva_e: primitiva sem os pesos',
    'luva_e: primitiva sem o _VERTICE', 'luva_e: sem as correções das dobras', 'sem a compressão Draco']) {
    assert.ok(p.some((m) => m.includes(esperado)), `${esperado} — ${p.join(' | ')}`);
  }
});

test('saída das luvas: texturas com o lado errado, com perdas ou sem alfa, e os arquivos acima de 6 MB', () => {
  let p = problemas((s) => { s.n = webp(1024); s.m = webp(2048, false); });
  assert.ok(p.some((m) => m.includes('luvas_n.webp: 1024×1024 (esperava 2048×2048)')), p.join(' | '));
  assert.ok(p.some((m) => m.includes('luvas_m.webp: sem o canal alfa')), p.join(' | '));
  p = problemas((s) => { s.bin = Buffer.alloc(6.5 * 1024 * 1024); });
  assert.ok(p.some((m) => /^arquivos: 6\.5\d MB \(orçamento 6 MB\)$/.test(m)), p.join(' | '));
});

test('saída das luvas: a marca do rig do relatório diferente da do glb', () => {
  const p = problemas((s) => { s.relatorio = { ...s.relatorio, marca: { d: MARCA.d, e: 'c'.repeat(64) } }; });
  assert.ok(p.some((m) => m.includes('marca do rig e') && m.includes('relatório')), p.join(' | '));
  const q = problemas((s) => { delete s.gltf.nodes[0].extras; });
  assert.ok(q.some((m) => m.includes('o .glb sem a marca do rig')), q.join(' | '));
});
