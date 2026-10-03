// Os braços de luva do viewmodel com a pega de uma mão (Fase 4.1c; desenho, seção 4.3: "o viewmodel monta só o braço
// direito" na faca): a pega vai só aos braços que ela tem — o outro volta ao repouso — e o braço sem a mão na pega nunca
// aparece, mesmo que o lado esteja pedido. Com braços falsos (sem GPU nem luvas de verdade).
import { test } from 'node:test';
import assert from 'node:assert/strict';
import * as THREE from 'three';
import { BracosDeLuva } from '../src/weapons/viewmodel/bracosLuva.js';

/** Um braço falso com o que o BracosDeLuva usa dele. */
function bracoFalso(lado) {
  return {
    lado,
    grupo: new THREE.Group(),
    pega: null,
    aplicadas: 0,
    soltas: 0,
    aplicarPega(p) {
      if (!p.dedos?.[lado]) throw new Error(`pega: sem a rotação de indicador_1_${lado}`);
      this.pega = p;
      this.aplicadas++;
    },
    soltarPega() {
      this.pega = null;
      this.soltas++;
    },
    colocar() {
      return { avisos: [] };
    },
    setBracadeira() {},
    async setFaccao() {},
    dispose() {},
  };
}

async function montar() {
  const luvas = { ficha: null, instanciar: async (lado) => bracoFalso(lado) };
  const bl = new BracosDeLuva({ luvas, corDaMassa: '#C8553D', faccao: 'massaCrua' });
  await bl.garantir(new THREE.Group());
  return bl;
}

const MAO = { posicao: new THREE.Vector3(1, 2, 3), quaternion: new THREE.Quaternion() };
const POSE = { position: new THREE.Vector3(), quaternion: new THREE.Quaternion() };
const cotovelo = () => new THREE.Vector3(0, -10, 5);

test('a pega de uma mão (a faca): só o braço direito recebe os dedos e aparece', async () => {
  const bl = await montar();
  const faca = { lados: ['d'], marca: { d: 'a'.repeat(64) }, dedos: { d: {} }, maos: { d: MAO } };
  assert.equal(bl.aplicarPega(faca), true);
  assert.equal(bl.bracos.direita.aplicadas, 1);
  assert.equal(bl.bracos.esquerda.aplicadas, 0);
  const pulsos = bl.colocar(POSE, cotovelo, new Set(['direita', 'esquerda']));
  assert.equal(pulsos.length, 1);
  assert.deepEqual(bl.visiveis(), ['direita']);
});

test('da pega de duas mãos para a de uma: o braço esquerdo solta a pega e some', async () => {
  const bl = await montar();
  const ak = { lados: ['d', 'e'], marca: {}, dedos: { d: {}, e: {} }, maos: { d: MAO, e: MAO } };
  bl.aplicarPega(ak);
  bl.colocar(POSE, cotovelo, new Set(['direita', 'esquerda']));
  assert.deepEqual(bl.visiveis(), ['direita', 'esquerda']);
  bl.aplicarPega({ lados: ['d'], marca: {}, dedos: { d: {} }, maos: { d: MAO } });
  assert.equal(bl.bracos.esquerda.soltas, 1, 'os dedos da esquerda voltam ao repouso');
  bl.colocar(POSE, cotovelo, new Set(['direita', 'esquerda']));
  assert.deepEqual(bl.visiveis(), ['direita']);
});

test('o braço que some não guarda os avisos do pulso da arma anterior (o luvas_contato e o status)', async () => {
  const bl = await montar();
  bl.bracos.esquerda.colocar = () => ({ avisos: ['pulso: 80° de flexão (limite 70°)'] });
  bl.aplicarPega({ lados: ['d', 'e'], marca: {}, dedos: { d: {}, e: {} }, maos: { d: MAO, e: MAO } });
  bl.colocar(POSE, cotovelo, new Set(['direita', 'esquerda']));
  assert.deepEqual(bl.avisos.esquerda, ['pulso: 80° de flexão (limite 70°)']);
  // a faca: o braço esquerdo some e os avisos dele também
  bl.aplicarPega({ lados: ['d'], marca: {}, dedos: { d: {} }, maos: { d: MAO } });
  bl.colocar(POSE, cotovelo, new Set(['direita', 'esquerda']));
  assert.deepEqual(bl.avisos, { direita: [], esquerda: [] });
  // e a arma que sai da mão (esconder) leva os avisos junto
  bl.aplicarPega({ lados: ['d', 'e'], marca: {}, dedos: { d: {}, e: {} }, maos: { d: MAO, e: MAO } });
  bl.colocar(POSE, cotovelo, new Set(['direita', 'esquerda']));
  bl.esconder();
  assert.deepEqual(bl.avisos, { direita: [], esquerda: [] });
});

test('a pega sem o campo `lados` (as armas da 4.1b): as duas mãos', async () => {
  const bl = await montar();
  bl.aplicarPega({ marca: {}, dedos: { d: {}, e: {} }, maos: { d: MAO, e: MAO } });
  assert.equal(bl.bracos.esquerda.aplicadas, 1);
});
