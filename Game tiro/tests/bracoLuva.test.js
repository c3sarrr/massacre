// Um braço de luva (Fase 4.1b; plano, Tarefa 9, Passo 2), sem GPU, montado do luvas.glb de verdade pelo GLTFLoader do
// vendor e com a pega do clipe `empunhadura` do .glb da AK: os dedos no quaternion do clipe e a marca do rig conferida;
// `colocar` com o osso `mao` no pulso e na orientação pedidas, o antebraço do cotovelo ao pulso no comprimento da
// ficha, a torção meio a meio entre a `torcao` e a `mao` (±0,5°), os ângulos do pulso e os avisos dos limites da AAOS;
// em repouso a luva fica onde o Blender a exportou; o antebraço de massinha vai junto com a `torcao` no punho; a facção
// troca os materiais; a braçadeira aparece com a cor do time.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import * as THREE from 'three';
import { LUVAS, OSSOS_DE_DEDO, ZONAS_DAS_LUVAS } from '../src/data/luvas.js';
import { comprimentoDoAntebraco, construirAntebraco } from '../src/characters/hands/antebracoMassa.js';
import { BracoLuva, avisosDoPulso, torcaoDoPulso } from '../src/characters/hands/bracoLuva.js';
import { validarFichaLuvas } from '../src/characters/hands/fichaLuvas.js';
import { moldeDoBraco } from '../src/characters/hands/moldeLuva.js';
import { dedosDoClipe, lerPega } from '../src/characters/hands/pega.js';
import { RNG } from '../src/core/rng.js';
import { RAIZ, carregarGlbNoNode, decodificadorDraco, sdfDeTeste } from './luvasTestUtils.js';

const MM = 25.4;
const X = new THREE.Vector3(1, 0, 0);
const FICHA = validarFichaLuvas(JSON.parse(readFileSync(join(RAIZ, 'tools/blender/refs/luvas.json'), 'utf8')));

let base = null;
async function montagem() {
  if (!base) {
    base = (async () => {
      const draco = await decodificadorDraco();
      const luvas = await carregarGlbNoNode(join(RAIZ, LUVAS.pasta, 'luvas.glb'), draco);
      const ak = await carregarGlbNoNode(join(RAIZ, 'assets/armas/ak47/ak47.glb'), draco);
      const moldes = { d: moldeDoBraco(luvas.scene, 'd', ZONAS_DAS_LUVAS), e: moldeDoBraco(luvas.scene, 'e', ZONAS_DAS_LUVAS) };
      const antebraco = await construirAntebraco(sdfDeTeste(40), FICHA);
      const clipe = ak.animations.find((a) => a.name === 'empunhadura');
      const lida = lerPega(ak.parser.json);
      return { moldes, antebraco, pega: { marca: lida.marca, dedos: dedosDoClipe(clipe) } };
    })();
  }
  return base;
}

const materiaisFalsos = (nome) => Object.fromEntries(ZONAS_DAS_LUVAS.map((z) => [z, new THREE.MeshBasicMaterial({ name: `${nome}:${z}` })]));

async function braco(lado, extra = {}) {
  const m = await montagem();
  return new BracoLuva({
    molde: m.moldes[lado], faccao: 'massaCrua', materiais: materiaisFalsos('massaCrua'),
    materiaisDe: async (f) => materiaisFalsos(f), antebraco: m.antebraco, corDaMassa: '#C8553D', limites: FICHA.limites, ...extra,
  });
}

/** O giro (radianos) em volta de +X contido num quaternion (a torção do swing-twist). */
function torcaoEmX(q) {
  const s = q.w < 0 ? -1 : 1;
  return 2 * Math.atan2(s * q.x, s * q.w);
}

/** O ângulo (radianos) entre dois giros (os quaternions normalizados: o arquivo é float32). */
function angulo(a, b) {
  return 2 * Math.acos(Math.min(1, Math.abs(a.clone().normalize().dot(b.clone().normalize()))));
}

/** A rotação do osso no referencial do braço (o grupo). */
function noBraco(b, osso) {
  b.grupo.updateMatrixWorld(true);
  const g = b.grupo.getWorldQuaternion(new THREE.Quaternion()).invert();
  return g.multiply(b.ossos[osso].getWorldQuaternion(new THREE.Quaternion()));
}

const graus = (r) => (r * 180) / Math.PI;

test('braço: a pega põe cada osso de dedo no quaternion do clipe da AK e recusa outra marca', async () => {
  const { pega } = await montagem();
  for (const lado of ['d', 'e']) {
    const b = await braco(lado);
    b.aplicarPega(pega);
    for (const osso of OSSOS_DE_DEDO) {
      const q = new THREE.Quaternion().fromArray(pega.dedos[lado][osso]).normalize();
      assert.ok(angulo(b.ossos[osso].quaternion, q) < 1e-7, `${lado}: ${osso}`);
    }
    assert.equal(b.pega, pega);
    assert.throws(() => b.aplicarPega({ ...pega, marca: { d: 'f'.repeat(64), e: 'f'.repeat(64) } }), /marca do rig .* não é a das luvas/);
    const semPolegar = structuredClone(pega);
    delete semPolegar.dedos[lado].polegar_2;
    assert.throws(() => b.aplicarPega(semPolegar), new RegExp(`polegar_2_${lado}`));
    b.soltarPega();
    assert.equal(b.pega, null);
    b.dispose();
  }
});

test('braço: colocar põe o osso mao no pulso e na orientação pedidas, e o antebraço do cotovelo ao pulso', async () => {
  const rng = new RNG('colocar-luvas');
  const L = comprimentoDoAntebraco(FICHA) / MM;
  const pai = new THREE.Group();
  pai.position.set(3, -2, 5);
  pai.quaternion.setFromEuler(new THREE.Euler(0.3, -0.7, 0.2));
  for (const lado of ['d', 'e']) {
    const b = await braco(lado);
    pai.add(b.grupo);
    for (let i = 0; i < 12; i++) {
      const pulso = new THREE.Vector3(rng.float(-4, 4), rng.float(-4, 4), rng.float(-8, -2));
      const cotovelo = pulso.clone().add(new THREE.Vector3(rng.float(-1, 1), rng.float(-1.5, -0.5), rng.float(0.5, 1.5)).normalize().multiplyScalar(rng.float(4, 12)));
      const maoQuat = new THREE.Quaternion().setFromEuler(new THREE.Euler(rng.float(-3, 3), rng.float(-3, 3), rng.float(-3, 3))).normalize();
      b.colocar(pulso, maoQuat, cotovelo);
      pai.updateMatrixWorld(true);
      const mao = b.ossos.mao;
      const pm = pai.worldToLocal(mao.getWorldPosition(new THREE.Vector3()));
      assert.ok(pm.distanceTo(pulso) * MM < 1e-4, `${lado}: o pulso a ${pm.distanceTo(pulso) * MM} mm`);
      const qm = pai.getWorldQuaternion(new THREE.Quaternion()).invert().multiply(mao.getWorldQuaternion(new THREE.Quaternion()));
      assert.ok(angulo(qm, maoQuat) < 1e-5, `${lado}: a orientação da mão a ${angulo(qm, maoQuat)} rad`);
      const pc = pai.worldToLocal(b.ossos.antebraco.getWorldPosition(new THREE.Vector3()));
      const esperado = pulso.clone().add(cotovelo.clone().sub(pulso).normalize().multiplyScalar(L));
      assert.ok(pc.distanceTo(esperado) * MM < 0.01, `${lado}: o cotovelo a ${(pc.distanceTo(esperado) * MM).toFixed(4)} mm do alinhamento`);
    }
    b.dispose();
  }
});

test('braço: a torção vai meio a meio para a torcao e para a mao, com a pronação no sentido da anatomia', async () => {
  const { moldes } = await montagem();
  const pulso = new THREE.Vector3(0, 0, 0);
  const cotovelo = new THREE.Vector3(-8, -3, 4);
  for (const lado of ['d', 'e']) {
    const b = await braco(lado);
    const m = moldes[lado];
    const repM = m.quatRepouso[m.ossos.indexOf(`mao_${lado}`)];
    const repT = m.quatRepouso[m.ossos.indexOf(`torcao_${lado}`)];
    b.colocar(pulso, new THREE.Quaternion(), cotovelo);
    const Q = b.grupo.quaternion.clone();
    for (const tau of [-150, -80, -35, 0, 20, 60, 120]) {
      // a mão girada τ em volta do antebraço (+X do braço) e com um balanço de pulso por cima
      const delta = new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0, 0.6, 0.8), 0.3)
        .multiply(new THREE.Quaternion().setFromAxisAngle(X, (tau * Math.PI) / 180));
      const { angulos } = b.colocar(pulso, Q.clone().multiply(delta).multiply(repM), cotovelo);
      const rt = noBraco(b, 'torcao').multiply(repT.clone().invert());
      const rm = noBraco(b, 'mao').multiply(repM.clone().invert());
      const rolT = graus(torcaoEmX(rt));
      const rolM = graus(torcaoEmX(rt.clone().invert().multiply(rm)));
      const total = graus(torcaoEmX(rm));
      assert.ok(Math.abs(rolT - total / 2) < 0.5 && Math.abs(rolM - total / 2) < 0.5, `${lado}, τ ${tau}: torcao ${rolT.toFixed(2)}°, mao ${rolM.toFixed(2)}° de ${total.toFixed(2)}°`);
      assert.ok(Math.abs(total - tau) < 1e-4, `${lado}: a torção total ${total}`);
      // pronação: a palma para baixo com o polegar para cima de partida — na direita é o giro negativo em +X
      assert.ok(Math.abs(angulos.pronacao - (lado === 'd' ? -tau : tau)) < 1e-4, `${lado}: pronação ${angulos.pronacao} para τ ${tau}`);
    }
    b.dispose();
  }
});

test('braço: os ângulos do pulso e os avisos dos limites da AAOS da ficha', async () => {
  const { moldes } = await montagem();
  const pulso = new THREE.Vector3(0, 0, 0);
  const cotovelo = new THREE.Vector3(-10, 0, 0);
  for (const lado of ['d', 'e']) {
    const b = await braco(lado);
    const m = moldes[lado];
    const repM = m.quatRepouso[m.ossos.indexOf(`mao_${lado}`)];
    const r0 = b.colocar(pulso, new THREE.Quaternion(), cotovelo);
    assert.ok(Array.isArray(r0.avisos));
    const Q = b.grupo.quaternion.clone();
    const pose = (eixo, g) => Q.clone().multiply(new THREE.Quaternion().setFromAxisAngle(eixo, (g * Math.PI) / 180)).multiply(repM);
    const neutro = b.colocar(pulso, pose(X, 0), cotovelo);
    assert.deepEqual(neutro.avisos, []);
    assert.ok(Math.abs(neutro.angulos.flexao) < 1e-4 && Math.abs(neutro.angulos.desvio) < 1e-4 && Math.abs(neutro.angulos.pronacao) < 1e-4);
    // flexão: as pontas para a palma (−Y do braço), em volta de +Z; desvio radial: para o polegar (σ·Z)
    const Z = new THREE.Vector3(0, 0, 1);
    const Y = new THREE.Vector3(0, 1, 0);
    const s = m.polegar;
    const casos = [
      [pose(Z, -60), 'flexao', 60, []],
      [pose(Z, -85), 'flexao', 85, [/pulso: flexão de 85\.0° \(limite 80°\)/]],
      [pose(Z, 75), 'flexao', -75, [/pulso: extensão de 75\.0° \(limite 70°\)/]],
      [pose(Y, -25 * s), 'desvio', 25, [/pulso: desvio radial de 25\.0° \(limite 20°\)/]],
      [pose(Y, 35 * s), 'desvio', -35, [/pulso: desvio ulnar de 35\.0° \(limite 30°\)/]],
      [pose(X, 90 * s), 'pronacao', 90, [/antebraço: pronação de 90\.0° \(limite 80°\)/]],
      [pose(X, -85 * s), 'pronacao', -85, [/antebraço: supinação de 85\.0° \(limite 80°\)/]],
    ];
    for (const [q, campo, valor, avisos] of casos) {
      const r = b.colocar(pulso, q, cotovelo);
      assert.ok(Math.abs(r.angulos[campo] - valor) < 1e-4, `${lado}: ${campo} ${r.angulos[campo]} (esperado ${valor})`);
      assert.equal(r.avisos.length, avisos.length, `${lado}: ${r.avisos.join('; ')}`);
      avisos.forEach((re, i) => assert.match(r.avisos[i], re));
    }
    b.dispose();
  }
  // a conta pura: o pulso flexionado 60° no rádio girado 90° continua flexão (a torção inteira sai antes de medir), e o
  // mesmo giro de 60° em volta do Z fixo depois da supinação é desvio ulnar — a mão já está de lado
  const Zf = new THREE.Vector3(0, 0, 1);
  const t = torcaoDoPulso(new THREE.Quaternion().setFromAxisAngle(X, Math.PI / 2).multiply(new THREE.Quaternion().setFromAxisAngle(Zf, -Math.PI / 3)), -1);
  assert.ok(Math.abs(t.flexao - 60) < 1e-9 && Math.abs(t.desvio) < 1e-9 && Math.abs(t.pronacao + 90) < 1e-9, JSON.stringify(t));
  const u = torcaoDoPulso(new THREE.Quaternion().setFromAxisAngle(Zf, -Math.PI / 3).multiply(new THREE.Quaternion().setFromAxisAngle(X, Math.PI / 2)), -1);
  assert.ok(Math.abs(u.flexao) < 1e-9 && Math.abs(u.desvio + 60) < 1e-9 && Math.abs(u.pronacao + 90) < 1e-9, JSON.stringify(u));
  assert.deepEqual(avisosDoPulso({ flexao: 80, desvio: -30, pronacao: 80 }, FICHA.limites), [], 'nos limites não avisa');
});

test('braço: em repouso a luva fica onde o Blender a exportou, e sem giro nenhum osso mexe', async () => {
  const { moldes } = await montagem();
  for (const lado of ['d', 'e']) {
    const b = await braco(lado);
    const m = moldes[lado];
    const repM = m.quatRepouso[m.ossos.indexOf(`mao_${lado}`)];
    b.colocar(new THREE.Vector3(1, 2, 3), new THREE.Quaternion(), new THREE.Vector3(-5, 2, 3));
    b.colocar(new THREE.Vector3(1, 2, 3), b.grupo.quaternion.clone().multiply(repM), new THREE.Vector3(-5, 2, 3));
    let pior = 0;
    for (const malha of b.malhas) {
      const zona = malha.geometry.name.split(':')[1];
      const original = m.primitivas.find((p) => p.zona === zona).geometria.attributes.position.array;
      const agora = malha.geometry.attributes.position.array;
      for (let i = 0; i < agora.length; i++) pior = Math.max(pior, Math.abs(agora[i] - original[i]) * MM);
      assert.ok(malha.geometry.attributes.repouso, 'o padrão lê a posição de repouso');
    }
    assert.ok(pior < 0.02, `${lado}: a luva a ${pior.toFixed(4)} mm do repouso`);
    b.dispose();
  }
});

test('braço: com a pega da AK a luva dobra e as normais acompanham', async () => {
  const { pega } = await montagem();
  const b = await braco('d');
  const antes = b.malhas.map((mm) => mm.geometry.attributes.position.array.slice());
  const normais = b.malhas.map((mm) => mm.geometry.attributes.normal.array.slice());
  b.aplicarPega(pega);
  let andou = 0;
  let viradas = 0;
  let total = 0;
  b.malhas.forEach((mm, k) => {
    const p = mm.geometry.attributes.position.array;
    const n = mm.geometry.attributes.normal.array;
    for (let i = 0; i < p.length; i++) andou = Math.max(andou, Math.abs(p[i] - antes[k][i]) * MM);
    for (let i = 0; i < n.length; i += 3) {
      total++;
      if (Math.abs(Math.hypot(n[i], n[i + 1], n[i + 2]) - 1) > 1e-3) viradas++;
    }
    assert.ok(normais[k].some((v, i) => Math.abs(v - n[i]) > 1e-3), 'as normais giram com a malha');
  });
  assert.ok(andou > 20, `as pontas dos dedos andaram ${andou.toFixed(1)} mm`);
  assert.equal(viradas, 0, `${viradas} de ${total} normais fora do comprimento 1`);
  assert.equal(b.atualizar(), false, 'sem mudança, não recalcula');
  b.dispose();
});

test('braço: o antebraço de massinha no punho vai junto com a torcao', async () => {
  const b = await braco('e');
  const { moldes } = await montagem();
  const m = moldes.e;
  const repM = m.quatRepouso[m.ossos.indexOf('mao_e')];
  b.colocar(new THREE.Vector3(), new THREE.Quaternion(), new THREE.Vector3(-9, 0, 0));
  b.colocar(new THREE.Vector3(), b.grupo.quaternion.clone().multiply(new THREE.Quaternion().setFromAxisAngle(X, 1.2)).multiply(repM), new THREE.Vector3(-9, 0, 0));
  b.grupo.updateMatrixWorld(true);
  b.skeleton.update();
  const g = b.antebraco.geometry;
  const pos = g.attributes.position;
  const torcao = b.ossos.torcao;
  const it = m.ossos.indexOf('torcao_e');
  const Mt = b.grupo.matrixWorld.clone().invert().multiply(torcao.matrixWorld).multiply(m.relRepousoInv[it]);
  let conta = 0;
  for (let i = 0; i < pos.count; i++) {
    if (g.attributes.skinWeight.getY(i) < 1) continue;
    const v = new THREE.Vector3().fromBufferAttribute(pos, i);
    const esperado = v.clone().applyMatrix4(Mt);
    const pele = b.antebraco.applyBoneTransform(i, v.clone());
    assert.ok(pele.distanceTo(esperado) * MM < 1e-3, 'o pedaço do punho é todo da torcao');
    conta++;
  }
  assert.ok(conta > 20, 'amostrou o pedaço do punho');
  b.dispose();
});

test('braço: a facção troca os materiais da luva; a braçadeira aparece com a cor do time; o descarte', async () => {
  const b = await braco('d');
  const antes = b.malhas.map((mm) => mm.material);
  assert.deepEqual(antes.map((x) => x.name).sort(), ZONAS_DAS_LUVAS.map((z) => `massaCrua:${z}`).sort());
  const p1 = b.setFaccao('massaCrua');
  const p2 = b.setFaccao('tropa');
  assert.equal(await p1, false, 'o pedido velho não troca');
  assert.equal(await p2, true);
  assert.equal(b.faccao, 'tropa');
  for (const mm of b.malhas) assert.equal(mm.material.name, `tropa:${mm.geometry.name.split(':')[1]}`);
  assert.equal(b.bracadeira.visible, false);
  b.setBracadeira('#2F6DB5');
  assert.equal(b.bracadeira.visible, true);
  assert.equal(b.materialBracadeira.color.getHexString(), '2f6db5');
  b.setBracadeira(null);
  assert.equal(b.bracadeira.visible, false);
  assert.equal(b.materialMassa.clay.boil, 0, 'sem boil');
  const pai = new THREE.Group();
  pai.add(b.grupo);
  const descartadas = [];
  for (const mm of b.malhas) mm.geometry.addEventListener('dispose', () => descartadas.push(mm.geometry.name));
  const antebraco = b.antebraco.geometry;
  let dividida = false;
  antebraco.addEventListener('dispose', () => {
    dividida = true;
  });
  b.dispose();
  assert.equal(b.grupo.parent, null);
  assert.equal(descartadas.length, ZONAS_DAS_LUVAS.length);
  assert.equal(dividida, false, 'a malha de massinha é da fonte, dividida entre os braços');
});
