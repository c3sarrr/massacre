// Serviço weaponModels com a origem glb (Fase 4.1a; desenho, seção 5.2), com carregadores falsos (uma cena montada no
// teste no lugar do GLTFLoader, texturas vazias, a ficha real e um relatório): info no formato da 4.1, instância com as
// peças móveis e as âncoras, geometrias e materiais divididos, cada coisa carregada uma vez, skin trocando os materiais
// (evento `skin`), ambiente em todos os materiais, recarga com os eventos e o descarte de tudo; a origem de massinha
// continua respondendo.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import * as THREE from 'three';
import { EV, EventBus } from '../src/core/events.js';
import { ARMAS_REAIS, LODS_REAIS, ZONAS } from '../src/data/armasReais.js';
import { WeaponLibrary } from '../src/weapons/model/weaponLibrary.js';
import { skinPorNome } from '../src/weapons/skins/skin.js';

const FICHA = JSON.parse(readFileSync(new URL('../tools/blender/refs/ak47.json', import.meta.url), 'utf8'));
const ZONA_DA_PECA = { base: 'corpo', ferrolho: 'interno', carregador: 'carregador', gatilho: 'detalhes', cao: 'interno', seletor: 'detalhes' };

function cenaFalsa() {
  const cena = new THREE.Group();
  const raiz = new THREE.Group();
  raiz.name = 'ak47';
  cena.add(raiz);
  for (const lod of LODS_REAIS) {
    const no = new THREE.Group();
    no.name = lod;
    raiz.add(no);
    for (const peca of ['base', ...ARMAS_REAIS.ak47.pecas]) {
      const m = new THREE.Mesh(new THREE.BoxGeometry(peca === 'base' ? 34 : 2, 2, 2), new THREE.MeshStandardMaterial({ name: ZONA_DA_PECA[peca] }));
      m.name = `${lod}_${peca}`;
      if (peca === 'ferrolho') {
        m.position.set(5.9, 0.5, 0);
        m.userData.eixo = [-1, 0, 0];
      }
      no.add(m);
    }
    // A base tem mais zonas: uma segunda malha filha com a guarnição.
    const g = new THREE.Mesh(new THREE.BoxGeometry(8, 3, 1.6), new THREE.MeshStandardMaterial({ name: 'guarnicao' }));
    g.position.set(-10, -1, 0);
    no.getObjectByName(`${lod}_base`).add(g);
  }
  const soq = new THREE.Group();
  soq.name = 'soquetes';
  raiz.add(soq);
  for (const [nome, x] of [['boca', 21.69], ['ejecao', 4.4], ['carregador', 3.7], ['mira_tras', 6.1], ['mira_frente', 20.7], ['mao_d', -2.2], ['mao_e', 10.3]]) {
    const s = new THREE.Object3D();
    s.name = `soquete_${nome}`;
    s.position.set(x, 0, nome === 'ejecao' ? 0.63 : 0);
    soq.add(s);
  }
  return cena;
}

function carregadoresFalsos() {
  const conta = { glb: 0, textura: 0, json: 0, urls: [] };
  return {
    conta,
    carregadores: {
      async glb(url) {
        conta.glb++;
        conta.urls.push(url);
        return { scene: cenaFalsa() };
      },
      async textura(url) {
        conta.textura++;
        conta.urls.push(url);
        const t = new THREE.Texture();
        t.name = url;
        return t;
      },
      async json(url) {
        conta.json++;
        if (url.includes('relatorio')) return { arma: 'ak47', silhueta: { iouTolerancia: 0.991, iouBruto: 0.96 } };
        if (url.includes('refs/ak47.json')) return structuredClone(FICHA);
        throw new Error(`sem ${url}`);
      },
    },
  };
}

const nova = (extra = {}) => {
  const f = carregadoresFalsos();
  const events = new EventBus();
  const lib = new WeaponLibrary({ sdf: null, events, carregadores: f.carregadores, ...extra });
  return { lib, events, conta: f.conta };
};

test('weaponModels: as duas origens, os níveis de cada uma e o info da AK no formato da 4.1', async () => {
  const { lib } = nova();
  assert.equal(lib.source('ak47'), 'glb');
  assert.equal(lib.source('awp'), 'massinha');
  assert.equal(lib.source('usps'), null);
  assert.ok(lib.ids.includes('ak47') && lib.ids.includes('awp'));
  assert.equal(lib.ids.filter((id) => id === 'ak47').length, 1, 'a realista vale sobre a receita de massinha do mesmo id');
  assert.deepEqual(lib.lods('ak47'), ['perto', 'mundo', 'longe']);
  assert.deepEqual(lib.lods('awp'), ['perto', 'mundo']);
  assert.equal(lib.info('ak47'), null, 'antes de carregar');
  const info = await lib.describe('ak47');
  assert.equal(info.source, 'glb');
  assert.equal(info.category, 'rifle');
  // a cena falsa não tem a pega das luvas (um .glb de antes da 4.1b): sem braços (a AK de verdade: viewmodelLuvas.test.js)
  assert.equal(info.hands, false);
  assert.equal(info.pega, null);
  assert.deepEqual(info.parts, ['ferrolho', 'carregador', 'gatilho', 'cao', 'seletor']);
  assert.deepEqual(info.anchors.boca.pos, [21.69, 0, 0]);
  assert.equal(info.anchors.maoDireita.pose, null);
  assert.ok(info.anchors.maoEsquerda && info.anchors.ejecao);
  assert.ok(Math.abs(info.plan.lengthU - 870 / 25.4) < 1e-9);
  assert.equal(info.iou, 0.991);
  assert.ok(info.bounds.max[0] > info.bounds.min[0]);
  assert.equal(lib.info('ak47'), info);
  const awp = lib.info('awp');
  assert.equal(awp.source, 'massinha');
  assert.equal(awp.hands, true);
  assert.ok(awp.recipe && awp.anchors.maoDireita);
  // as três da 4.1c são realistas (a Glock, a M4A4 e a faca M9 do Blender)
  for (const id of ['glock', 'm4a4', 'knife']) assert.equal(lib.source(id), 'glb', id);
  await assert.rejects(lib.describe('awp'), /sem .*tools\/blender\/refs\/awp\.json/, 'a planta que a receita aponta, e a falha aparece');
});

test('weaponModels: instância glb com as peças móveis, as âncoras, os materiais de zona e tudo dividido', async () => {
  const { lib, conta } = nova();
  const a = await lib.instance('ak47', { lod: 'perto' });
  const b = await lib.instance('ak47', { lod: 'perto' });
  const w = a.userData.weapon;
  assert.equal(w.id, 'ak47');
  assert.equal(w.source, 'glb');
  assert.deepEqual(Object.keys(w.parts).sort(), ['cao', 'carregador', 'ferrolho', 'gatilho', 'seletor']);
  assert.deepEqual(w.parts.ferrolho.userData.rest, [5.9, 0.5, 0]);
  assert.ok(w.anchors.boca.isObject3D && w.anchors.maoDireita.isObject3D);
  const malhas = (inst) => {
    const out = [];
    inst.traverse((o) => o.isMesh && out.push(o));
    return out;
  };
  const ma = malhas(a);
  const mb = malhas(b);
  assert.equal(ma.length, mb.length);
  ma.forEach((m, i) => {
    assert.ok(m.material.isMeshPhysicalMaterial);
    assert.equal(m.material.userData.zona, m.userData.zona);
    assert.equal(m.geometry, mb[i].geometry, 'geometria dividida');
    assert.equal(m.material, mb[i].material, 'material dividido');
    assert.equal(m.geometry.userData.shared, true);
  });
  assert.equal(conta.glb, 1, 'o .glb carregado uma vez');
  assert.equal(conta.textura, 2, 'o conjunto perto: _n e _m');
  await lib.instance('ak47', { lod: 'mundo' });
  assert.equal(conta.textura, 4, 'o conjunto mundo: _mundo_n e _mundo_m');
  await lib.instance('ak47', { lod: 'longe' });
  assert.equal(conta.textura, 4, 'o longe usa o conjunto do mundo');
  assert.ok(conta.urls.some((u) => u.endsWith('assets/armas/ak47/ak47_mundo_m.webp')));
  await assert.rejects(lib.instance('ak47', { lod: 'medio' }), /nível de detalhe desconhecido/);
});

test('weaponModels: skin e ambiente', async () => {
  const { lib, events } = nova();
  const fab = await lib.instance('ak47');
  const matFab = fab.getObjectByName('perto_base').material;
  assert.equal(lib.skinOf('ak47').chave, 'fabrica');
  const ouvidos = [];
  events.on(EV.WEAPON_MODEL, (e) => ouvidos.push(e));
  lib.setSkin('ak47', skinPorNome('ak47', 'Cromo e Carbono'));
  assert.deepEqual(ouvidos, [{ id: 'ak47', phase: 'skin' }]);
  const cc = await lib.instance('ak47');
  const matCc = cc.getObjectByName('perto_base').material;
  assert.notEqual(matCc, matFab);
  assert.equal(matCc.userData.acabamento, 'cromado');
  assert.throws(() => lib.setSkin('awp', skinPorNome('ak47', 'fabrica')), /skins de acabamento só nas armas realistas/);
  const env = new THREE.Texture();
  lib.setEnvironment(env, 0.9);
  assert.equal(matFab.envMap, env);
  assert.equal(matCc.envMap, env);
  assert.equal(matCc.envMapIntensity, 0.9);
  const depois = await lib.instance('ak47', { lod: 'mundo' });
  const matMundo = depois.getObjectByName('mundo_base').material;
  assert.equal(matMundo.envMap, env, 'material novo já nasce com o ambiente');
  assert.equal(matMundo.envMapIntensity, 0.9);
  assert.equal(matFab.normalMap.anisotropy, 8, 'a anisotropia de partida');
  const versao = matFab.normalMap.version;
  lib.setAnisotropy(4);
  assert.equal(matFab.normalMap.anisotropy, 4);
  assert.equal(matMundo.aoMap.anisotropy, 4);
  assert.ok(matFab.normalMap.version > versao, 'a textura sobe de novo com a anisotropia nova');
});

test('weaponModels: recarga (relendo → pronta, ?v= novo, o velho descartado) e o descarte de tudo', async () => {
  const { lib, events, conta } = nova();
  const velha = await lib.instance('ak47');
  const geo = velha.getObjectByName('perto_base').geometry;
  let geoDescartada = false;
  geo.addEventListener('dispose', () => {
    geoDescartada = true;
  });
  const fases = [];
  events.on(EV.WEAPON_MODEL, (e) => fases.push(e.phase));
  await lib.reload('ak47', 'perto');
  assert.deepEqual(fases, ['relendo', 'pronta']);
  assert.ok(geoDescartada, 'a geometria velha saiu');
  assert.equal(conta.glb, 2);
  assert.match(conta.urls.filter((u) => u.includes('ak47.glb')).at(-1), /\?v=\d+/);
  const nova_ = await lib.instance('ak47');
  const mats = new Set();
  nova_.traverse((o) => o.isMesh && mats.add(o.material));
  let descartados = 0;
  for (const m of mats) m.addEventListener('dispose', () => descartados++);
  lib.dispose();
  assert.equal(descartados, mats.size, 'os materiais de zona saíram no dispose');
  await assert.rejects(lib.instance('ak47'), /descartada/);
});

test('weaponModels: o relatório do console tem as duas origens', async () => {
  const { lib } = nova();
  await lib.describe('ak47');
  const linhas = lib.report();
  const ak = linhas.filter((r) => r.id === 'ak47');
  assert.deepEqual(ak.map((r) => r.lod), ['perto', 'mundo', 'longe']);
  assert.ok(ak.every((r) => r.source === 'glb' && r.state === 'pronta' && r.triangles > 0));
  assert.ok(linhas.some((r) => r.id === 'awp' && r.source === 'massinha'));
  assert.equal(ZONAS.length, 5);
});

test('weaponModels: o .glb de rifle sem a pega das luvas aparece sem braços, com o erro no log pedindo a reconstrução', async () => {
  const erros = [];
  const { lib } = nova({ log: { error: (m) => erros.push(m), debug() {}, warn() {} } });
  const info = await lib.describe('ak47');
  assert.equal(info.hands, false);
  assert.equal(info.pega, null);
  assert.equal(erros.length, 1);
  assert.match(erros[0], /arma ak47: sem a pega das luvas \(construa a arma de novo no Blender\)/);
});
