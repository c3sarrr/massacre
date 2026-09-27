// Os comandos `luvas` e `luvas_contato` (Fase 4.1b; plano, Tarefa 11): a medida do contato com uma arma e uma luva
// falsas de posição conhecida (um contato a 0,4 mm sai 0,4; um vértice 0,2 mm dentro dá a penetração), o formato em mm
// com duas casas e o veredito, o aviso sem arma com pega, e o `luvas` com o estado, os triângulos, a facção, a marca
// do rig conferida com a da arma na mão e os pulsos.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import * as THREE from 'three';
import { bvhDaArma, contatoDasLuvas } from '../src/characters/hands/luvasContato.js';
import { emMM, formatarContato, registerLuvasCommands, relatorioDasLuvas } from '../src/debug/luvasCommands.js';

const MM = 25.4;
const MARCA = { d: 'a'.repeat(64), e: 'b'.repeat(64) };

/** A arma falsa: uma caixa de 4 × 2 × 2 u girada e deslocada, dentro de um grupo que faz a vez da instância. */
function armaFalsa() {
  const raiz = new THREE.Group();
  raiz.position.set(1, -2, -5);
  raiz.quaternion.setFromEuler(new THREE.Euler(0.2, 0.5, -0.1));
  const caixa = new THREE.Mesh(new THREE.BoxGeometry(4, 2, 2), new THREE.MeshBasicMaterial());
  caixa.position.set(0.5, 0, 0);
  raiz.add(caixa);
  raiz.updateMatrixWorld(true);
  return raiz;
}

/** A luva falsa: três vértices no referencial da arma (0,4 mm fora da face +Y, 0,2 mm dentro, longe), noutro grupo. */
function lucaFalsa(raiz) {
  const grupo = new THREE.Group();
  grupo.position.set(-3, 1, 2);
  grupo.quaternion.setFromEuler(new THREE.Euler(-0.4, 0.3, 0.9));
  grupo.updateMatrixWorld(true);
  const naArma = [new THREE.Vector3(0.7, 1 + 0.4 / MM, 0.1), new THREE.Vector3(-0.8, 1 - 0.2 / MM, -0.3), new THREE.Vector3(0.5, 4, 0)];
  const paraBraco = grupo.matrixWorld.clone().invert().multiply(raiz.matrixWorld);
  const pts = new Float64Array(9);
  naArma.forEach((p, i) => {
    const q = p.clone().applyMatrix4(paraBraco).multiplyScalar(MM);
    pts.set([q.x, q.y, q.z], i * 3);
  });
  return { grupo, posicoesMM: pts };
}

test('luvas_contato: a distância com sinal de cada sonda e a penetração máxima, no referencial da arma', () => {
  const raiz = armaFalsa();
  const braco = lucaFalsa(raiz);
  const bvh = bvhDaArma(raiz);
  const r = contatoDasLuvas({ bvh, raizDaArma: raiz, braco, sondas: { palma: { vertice: 0, mm: 0.38 }, polegar: { vertice: 1, mm: -0.21 } } });
  const [palma, polegar] = r.sondas;
  assert.ok(Math.abs(palma.jogoMM - 0.4) < 1e-4, `um contato a 0,4 mm sai ${palma.jogoMM}`);
  assert.ok(Math.abs(palma.diferencaMM - 0.02) < 1e-4);
  assert.ok(Math.abs(polegar.jogoMM + 0.2) < 1e-4, `dentro sai negativo: ${polegar.jogoMM}`);
  assert.ok(Math.abs(r.penetracaoMM - 0.2) < 1e-4, `penetração ${r.penetracaoMM}`);
  assert.ok(Math.abs(r.piorDiferencaMM - 0.02) < 1e-4);
});

test('luvas_contato: um ponto longe da quina da caixa sai fora (o lado pela pseudonormal, não por uma face só)', () => {
  const raiz = armaFalsa();
  const grupo = new THREE.Group();
  // em volta da quina (+X, +Y, +Z) e das arestas: todos fora, a distância certa
  const casos = [[4, 3, 3], [3, 1.5, 0.2], [0.3, 2, 1.8], [2.6, -1.4, 1.3]];
  for (const c of casos) {
    const pts = new Float64Array(new THREE.Vector3(...c).applyMatrix4(raiz.matrixWorld).multiplyScalar(MM).toArray());
    const r = contatoDasLuvas({ bvh: bvhDaArma(raiz), raizDaArma: raiz, braco: { grupo, posicoesMM: pts }, sondas: { p: { vertice: 0, mm: 0 } } });
    const b = new THREE.Box3(new THREE.Vector3(-1.5, -1, -1), new THREE.Vector3(2.5, 1, 1));
    assert.ok(Math.abs(r.sondas[0].jogoMM - b.distanceToPoint(new THREE.Vector3(...c)) * MM) < 1e-3, `(${c}): ${r.sondas[0].jogoMM}`);
    assert.equal(r.penetracaoMM, 0);
  }
});

test('luvas_contato: o formato em mm com duas casas e o veredito', () => {
  const lado = (dif, entra) => ({ penetracaoMM: entra, piorDiferencaMM: dif, sondas: [{ contato: 'palma', jogoMM: -0.029, blenderMM: -0.044, diferencaMM: dif }] });
  const txt = formatarContato('ak47', { direita: lado(0.016, 0.053), esquerda: lado(0.08, 0.06) }, { d: { penetracaoMM: 0.044 }, e: { penetracaoMM: 0.05 } });
  assert.match(txt, /^luvas_contato ak47 \(a diferença para o Blender até 0,05 mm; entra até 0,30 mm\)/);
  assert.match(txt, /direita: entra 0,05 mm \(Blender 0,04 mm\) · pior diferença 0,02 mm ✓/);
  assert.match(txt, /esquerda: entra 0,06 mm \(Blender 0,05 mm\) · pior diferença 0,08 mm ✗/);
  assert.match(txt, /palma +jogo +−0,03 mm · Blender +−0,04 mm · diferença 0,02 mm/);
  assert.equal(emMM(0.4), '0,40 mm');
});

/** Console mínimo e o viewmodel falso do jeito que os comandos leem. */
function montar({ vm = null, estado = 'pronta' } = {}) {
  const commands = new Map();
  const con = { register: (def) => commands.set(def.name, def) };
  const relatorio = {
    estado, erro: estado === 'erro' ? 'luvas.glb: HTTP 404' : null, triangulos: { d: 6748, e: 6748 }, antebraco: 12500, ms: 1192,
    marca: estado === 'pronta' ? MARCA : null, bracos: vm ? 2 : 0,
  };
  const s = { luvasModels: { relatorio: () => relatorio } };
  registerLuvasCommands(con, s, { matchState: () => (vm ? { viewmodel: vm } : null) });
  return (nome) => commands.get(nome).run([]);
}

function vmFalso({ bracos = 'luvas', marca = MARCA, avisos = { direita: [], esquerda: ['antebraço: supinação de 85,0° (limite 80°)'] } } = {}) {
  const angulos = { flexao: -15.2, desvio: -10.2, pronacao: -2.9 };
  return {
    info: { id: 'ak47', pega: { marca, sondas: {} } },
    status: () => ({ item: 'ak47', bracos, faccao: 'tropa', avisos }),
    gloves: { prontos: bracos === 'luvas', bracos: { direita: { angulos }, esquerda: { angulos: { ...angulos, pronacao: -85 } } } },
  };
}

test('luvas: o estado, os triângulos, a marca do rig e, na mão, a facção, a marca da arma e os pulsos', () => {
  let txt = montar({ vm: vmFalso() })('luvas');
  assert.match(txt, /^luvas: pronta · 6\.748 \+ 6\.748 triângulos · antebraço de massinha 12\.500 · carregadas em 1192 ms · 2 braço\(s\) na cena/);
  assert.match(txt, /marca do rig: d aaaaaaaaaaaa… · e bbbbbbbbbbbb…/);
  assert.match(txt, /na mão: ak47 com as luvas · Tropa do Estúdio \(preta\) · a marca da arma bate com a das luvas ✓/);
  assert.match(txt, /direita: pulso −15,2° de flexão, −10,2° de desvio, antebraço −2,9° de pronação$/m);
  assert.match(txt, /esquerda: .* antebraço −85,0° de pronação — antebraço: supinação de 85,0° \(limite 80°\)/);
  txt = montar({ vm: vmFalso({ marca: { d: 'c'.repeat(64), e: 'b'.repeat(64) } }) })('luvas');
  assert.match(txt, /a marca da arma NÃO bate com a das luvas ✗/);
  txt = montar({ vm: vmFalso({ bracos: null, marca: { d: 'c'.repeat(64), e: 'b'.repeat(64) } }) })('luvas');
  assert.match(txt, /na mão: ak47 com nenhum braço/);
  assert.match(txt, /construa a arma de novo no Blender/);
  assert.match(montar({ estado: 'erro' })('luvas'), /^luvas: erro — luvas\.glb: HTTP 404/);
  assert.match(montar({ estado: 'carregando' })('luvas'), /^luvas: carregando/);
  assert.match(montar({ estado: '—' })('luvas'), /^luvas: não carregadas/);
  assert.match(montar()('luvas'), /na mão: nada/);
});

test('luvas_contato: sem arma com pega na mão, o aviso', () => {
  assert.match(montar()('luvas_contato'), /segure em primeira pessoa uma arma com a pega das luvas \(give ak47\)/);
  assert.match(montar({ vm: vmFalso({ bracos: 'massinha' }) })('luvas_contato'), /segure em primeira pessoa/);
});

test('luvas_contato: o zero arredondado sai sem sinal', () => {
  assert.equal(emMM(-0.001), '0,00 mm');
  assert.equal(emMM(-0.006), '−0,01 mm');
});
