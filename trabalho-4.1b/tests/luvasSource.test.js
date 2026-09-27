// O serviço das luvas (Fase 4.1b; plano, Tarefa 9, Passo 1), com carregadores falsos como os da weaponLibraryGlb.test.js
// — o .glb é o de verdade, lido pelo GLTFLoader do vendor (o Draco sem Workers), as texturas vazias, o relatório e a
// ficha do disco, e o SdfMesher pelo marching cubes numa grade grossa: uma carga só para pedidos ao mesmo tempo; os
// materiais por (facção, zona) em cache e marcados como divididos; cada braço com o esqueleto e as malhas da luva
// dele; o ambiente em todos os materiais; o descarte de tudo e a recusa depois; o erro de carga no log com o arquivo.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import * as THREE from 'three';
import { FACCOES_DAS_LUVAS, LUVAS, ZONAS_DAS_LUVAS } from '../src/data/luvas.js';
import { LuvasSource } from '../src/characters/hands/luvasSource.js';
import { RAIZ, carregarGlbNoNode, decodificadorDraco, sdfDeTeste } from './luvasTestUtils.js';

const RELATORIO = JSON.parse(readFileSync(join(RAIZ, LUVAS.pasta, 'luvas.relatorio.json'), 'utf8'));
const FICHA = JSON.parse(readFileSync(join(RAIZ, 'tools/blender/refs/luvas.json'), 'utf8'));
let draco = null;

function logFalso() {
  const linhas = { debug: [], warn: [], error: [] };
  return { linhas, debug: (m) => linhas.debug.push(m), warn: (m) => linhas.warn.push(m), error: (m) => linhas.error.push(m) };
}

async function nova({ falhaGlb = null } = {}) {
  draco ??= await decodificadorDraco();
  const conta = { glb: 0, textura: 0, json: 0, urls: [], texturas: [] };
  const sdf = sdfDeTeste(32);
  const log = logFalso();
  const carregadores = {
    async glb(url) {
      conta.glb++;
      conta.urls.push(url);
      if (falhaGlb) throw new Error(falhaGlb);
      return carregarGlbNoNode(join(RAIZ, LUVAS.pasta, 'luvas.glb'), draco);
    },
    async textura(url) {
      conta.textura++;
      conta.urls.push(url);
      const t = new THREE.Texture();
      t.name = url;
      conta.texturas.push(t);
      return t;
    },
    async json(url) {
      conta.json++;
      conta.urls.push(url);
      if (url.endsWith('luvas.relatorio.json')) return structuredClone(RELATORIO);
      if (url.endsWith('refs/luvas.json')) return structuredClone(FICHA);
      throw new Error(`sem ${url}`);
    },
    descartar() {
      conta.descartou = true;
    },
  };
  return { fonte: new LuvasSource({ carregadores, sdf, log }), conta, sdf, log };
}

test('luvas: uma carga só para pedidos ao mesmo tempo (o .glb, o relatório, a ficha, as texturas e a massa)', async () => {
  const { fonte, conta, sdf } = await nova();
  const [a, b, d, e] = await Promise.all([fonte.carregar(), fonte.carregar(), fonte.instanciar('d', 'tropa', { corDaMassa: '#C8553D' }),
    fonte.instanciar('e', 'massaCrua', { corDaMassa: '#C8553D' })]);
  assert.equal(a, b);
  assert.equal(conta.glb, 1);
  assert.equal(conta.json, 2);
  assert.equal(conta.textura, 2, 'as texturas _n e _m uma vez para as duas facções');
  assert.ok(conta.urls.some((u) => u.endsWith('assets/maos/luvas_n.webp')) && conta.urls.some((u) => u.endsWith('assets/maos/luvas_m.webp')));
  assert.equal(sdf.pedidos.length, 2, 'o antebraço e a braçadeira gerados uma vez');
  assert.equal(d.lado, 'd');
  assert.equal(e.lado, 'e');
  const r = fonte.relatorio();
  assert.equal(r.estado, 'pronta');
  assert.deepEqual(r.triangulos, { d: RELATORIO.triangulos.luva, e: RELATORIO.triangulos.luva }, 'os triângulos de cada luva, como o Blender contou');
  assert.deepEqual(r.marca, RELATORIO.marca);
  assert.equal(r.bracos, 2);
  assert.ok(r.antebraco > 0);
  fonte.dispose();
});

test('luvas: materiais por facção e zona, em cache, divididos, com o padrão pela pose de repouso e as duas faces', async () => {
  const { fonte } = await nova();
  const tropa = await fonte.materiais('tropa');
  assert.equal(await fonte.materiais('tropa'), tropa);
  const crua = await fonte.materiais('massaCrua');
  assert.deepEqual(Object.keys(tropa).sort(), [...ZONAS_DAS_LUVAS].sort());
  for (const z of ZONAS_DAS_LUVAS) {
    const m = tropa[z];
    assert.equal(m.userData.shared, true);
    assert.equal(m.side, THREE.DoubleSide);
    assert.equal(m.defines.ARMA_REPOUSO, '');
    assert.equal(m.name, `luvas:tropa:${z}`);
    assert.notEqual(crua[z], m);
    assert.equal(m.userData.acabamento, LUVAS.pinturas.tropa.zonas[z].acabamento);
  }
  assert.ok(crua.couro.color.r > tropa.couro.color.r, 'o coiote mais claro que o preto');
  await assert.rejects(fonte.materiais('azul'), /facção das luvas desconhecida/);
  assert.deepEqual([...FACCOES_DAS_LUVAS].sort(), ['massaCrua', 'tropa']);
  fonte.dispose();
});

test('luvas: cada braço tem o esqueleto e as malhas da luva dele; dividem os materiais e a massa', async () => {
  const { fonte } = await nova();
  const opts = { corDaMassa: '#C8553D' };
  const [a, b, c] = await Promise.all([fonte.instanciar('d', 'tropa', opts), fonte.instanciar('d', 'tropa', opts), fonte.instanciar('e', 'tropa', opts)]);
  assert.notEqual(a.ossos.mao, b.ossos.mao);
  assert.notEqual(a.ossos.indicador_2, b.ossos.indicador_2);
  const geoA = new Set(a.malhas.map((m) => m.geometry));
  for (const m of b.malhas) assert.ok(!geoA.has(m.geometry), 'as malhas da luva são do braço');
  assert.deepEqual(a.malhas.map((m) => m.material), b.malhas.map((m) => m.material));
  assert.equal(a.antebraco.geometry, b.antebraco.geometry);
  assert.notEqual(a.materialMassa, b.materialMassa);
  assert.notEqual(a.marca, c.marca, 'a marca de cada braço');
  assert.equal(a.marca, RELATORIO.marca.d);
  // posar um não mexe no outro
  a.colocar(new THREE.Vector3(), new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(1, 0, 0), 1), new THREE.Vector3(-8, 0, 0));
  assert.notDeepEqual(a.malhas[0].geometry.attributes.position.array.slice(0, 30), b.malhas[0].geometry.attributes.position.array.slice(0, 30));
  await assert.rejects(fonte.instanciar('x', 'tropa', opts), /'d' ou 'e'/);
  fonte.dispose();
});

test('luvas: o ambiente chega a todos os materiais das duas facções', async () => {
  const { fonte } = await nova();
  await fonte.materiais('tropa');
  const ambiente = new THREE.Texture();
  fonte.setAmbiente(ambiente, 0.7);
  await fonte.materiais('massaCrua');
  for (const f of FACCOES_DAS_LUVAS) {
    for (const m of Object.values(await fonte.materiais(f))) {
      assert.equal(m.envMap, ambiente, `${f}: ${m.name}`);
      assert.equal(m.envMapIntensity, 0.7);
    }
  }
  fonte.setAmbiente(null);
  for (const m of Object.values(await fonte.materiais('tropa'))) assert.equal(m.envMap, null);
  fonte.dispose();
});

test('luvas: o descarte leva geometrias, materiais, texturas e braços, e recusa carga depois', async () => {
  const { fonte, conta } = await nova();
  const braco = await fonte.instanciar('d', 'massaCrua', { corDaMassa: '#C8553D' });
  const mats = Object.values(await fonte.materiais('massaCrua'));
  const eventos = [];
  const ouvir = (o, nome) => o.addEventListener('dispose', () => eventos.push(nome));
  for (const m of mats) ouvir(m, m.name);
  for (const t of conta.texturas) ouvir(t, t.name);
  ouvir(braco.antebraco.geometry, 'antebraco');
  ouvir(braco.bracadeira.geometry, 'bracadeira');
  for (const m of braco.malhas) ouvir(m.geometry, m.geometry.name);
  const pai = new THREE.Group();
  pai.add(braco.grupo);
  fonte.dispose();
  for (const m of mats) assert.ok(eventos.includes(m.name), m.name);
  for (const t of conta.texturas) assert.ok(eventos.includes(t.name), t.name);
  assert.ok(eventos.includes('antebraco') && eventos.includes('bracadeira'));
  assert.ok(braco.malhas.length === 0 || eventos.filter((x) => x.startsWith('luva_d')).length === ZONAS_DAS_LUVAS.length);
  assert.equal(braco.grupo.parent, null, 'o braço saiu da cena');
  assert.equal(conta.descartou, true);
  await assert.rejects(fonte.carregar(), /descartada/);
  await assert.rejects(fonte.instanciar('d', 'tropa', { corDaMassa: '#C8553D' }), /descartada/);
});

test('luvas: o erro de carga chega ao log com o arquivo, e a próxima carga tenta de novo', async () => {
  const { fonte, conta, log } = await nova({ falhaGlb: 'HTTP 404' });
  await assert.rejects(fonte.carregar(), /luvas\.glb: HTTP 404/);
  assert.equal(log.linhas.error.length, 1);
  assert.match(log.linhas.error[0], /luvas: não carregaram — luvas\.glb: HTTP 404/);
  assert.equal(fonte.relatorio().estado, 'erro');
  await assert.rejects(fonte.carregar(), /HTTP 404/);
  assert.equal(conta.glb, 2, 'tentou de novo');
  fonte.dispose();
});
