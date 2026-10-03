// Relevo moldado das armas realistas (correções da P1 da 4.1c; plano da 4.1c, P1.1 e P1.2): as texturas do molde
// (o pontilhado do punho da Glock, o quadriculado dos straps, o losango do punho A2 da M4, o recartilhado do cabo da M9)
// saem do alfa do `_n` — o tipo que o Blender assou — e o shader desenha o relevo, em qualquer acabamento. Aqui: a
// tabela dos tipos, a codificação do alfa (255 = liso, 255 − 32·id), o material de zona com o trecho do relevo depois
// da normal assada e o polímero acetinado com o padrão `molde`.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import * as THREE from 'three';
import { ACABAMENTOS, PADROES, RELEVOS_MOLDADOS } from '../src/data/acabamentos.js';
import { acabamentoParaMaterial } from '../src/weapons/skins/acabamento.js';
import { criarMaterialZona } from '../src/weapons/model/materialArma.js';
import { ARMA_RELEVO_PARS } from '../src/weapons/model/glsl/acabamentos.js';
import { RELEVO_DEGRAU, alfaDoRelevo, relevoDoAlfa, relevoPorId } from '../src/weapons/model/relevoMoldado.js';

test('relevos moldados: os quatro tipos com id, passo, altura e projeção', () => {
  assert.deepEqual(Object.keys(RELEVOS_MOLDADOS), ['pontilhado', 'quadriculado', 'losango', 'recartilhado']);
  assert.deepEqual(Object.values(RELEVOS_MOLDADOS).map((r) => r.id), [1, 2, 3, 4]);
  for (const [nome, r] of Object.entries(RELEVOS_MOLDADOS)) {
    assert.ok(r.nome.length > 3, nome);
    assert.ok(r.passo >= 0.5 && r.passo <= 3, `${nome}: passo ${r.passo} mm`);
    assert.ok(r.altura > 0 && r.altura < r.passo / 2, `${nome}: altura ${r.altura} mm`);
    assert.ok(['plano', 'cilindrica'].includes(r.projecao), `${nome}: projeção ${r.projecao}`);
  }
  assert.equal(RELEVOS_MOLDADOS.pontilhado.forma, 'graos');
  // os grãos se encostam (raio maior que meia célula), sem passar da célula vizinha (a vizinhança de 3 × 3 do shader)
  assert.ok(RELEVOS_MOLDADOS.pontilhado.raio > RELEVOS_MOLDADOS.pontilhado.passo / 2);
  assert.ok(RELEVOS_MOLDADOS.pontilhado.raio * 1.2 < RELEVOS_MOLDADOS.pontilhado.passo * 1.25);
  for (const nome of ['quadriculado', 'losango', 'recartilhado']) {
    const r = RELEVOS_MOLDADOS[nome];
    assert.equal(r.forma, 'piramides', nome);
    assert.ok(r.plato >= 0 && r.plato < 1, `${nome}: platô`);
  }
  assert.equal(RELEVOS_MOLDADOS.quadriculado.angulo, 0);
  assert.equal(RELEVOS_MOLDADOS.losango.angulo, 45);
  assert.equal(RELEVOS_MOLDADOS.recartilhado.projecao, 'cilindrica');
  assert.equal(relevoPorId(3), RELEVOS_MOLDADOS.losango);
  assert.equal(relevoPorId(0), null);
});

// O recartilhado em volta do cabo (correções da P1 da 4.1c): o número de losangos numa volta é fixo no tipo. Tirado do
// raio de cada ponto, ele pulava de 58 para 59 entre o meio e a quina das facetas do torno (o raio de 13,8 a 13,9 mm do
// cabo da M9) e o padrão rasgava em linhas ao longo do cabo.
test('projeção cilíndrica: as voltas inteiras e fixas do tipo, no shader e no período do padrão', () => {
  const cilindricos = Object.values(RELEVOS_MOLDADOS).filter((r) => r.projecao === 'cilindrica');
  assert.ok(cilindricos.length > 0);
  for (const r of cilindricos) {
    assert.ok(Number.isInteger(r.voltas) && r.voltas >= 8, `${r.nome}: voltas ${r.voltas}`);
    assert.ok(r.raioNominal > 0, `${r.nome}: raio nominal`);
    // no raio nominal, a volta tem o período do padrão a menos de 3 % (o losango sai quadrado)
    const periodo = r.passo / Math.max(Math.abs(Math.cos((r.angulo * Math.PI) / 180)), Math.abs(Math.sin((r.angulo * Math.PI) / 180)));
    const naVolta = (2 * Math.PI * r.raioNominal) / r.voltas;
    assert.ok(Math.abs(naVolta / periodo - 1) < 0.03, `${r.nome}: ${naVolta.toFixed(3)} × ${periodo.toFixed(3)} mm`);
    assert.ok(ARMA_RELEVO_PARS.includes(`if ( id == ${r.id}.0 ) return ${r.voltas.toFixed(1)};`), `voltas do tipo ${r.id} no shader`);
  }
  for (const r of Object.values(RELEVOS_MOLDADOS).filter((t) => t.projecao !== 'cilindrica')) assert.equal(r.voltas, undefined, r.nome);
  // nenhuma conta das voltas pelo raio do fragmento
  assert.doesNotMatch(ARMA_RELEVO_PARS, /floor\( 6\.2831853 \* r/);
  assert.equal(RELEVOS_MOLDADOS.recartilhado.raioNominal, 13.9);
});

test('o alfa do _n: 255 no liso e 255 − 32·id nos relevos, lido de volta com o peso da borda', () => {
  assert.equal(RELEVO_DEGRAU, 32);
  assert.equal(alfaDoRelevo(0), 1);
  for (const { id } of Object.values(RELEVOS_MOLDADOS)) {
    assert.equal(Math.round(alfaDoRelevo(id) * 255), 255 - 32 * id);
    assert.deepEqual(relevoDoAlfa(alfaDoRelevo(id)), { id, peso: 1 });
    // o valor de 8 bits da textura
    assert.deepEqual(relevoDoAlfa(Math.round(alfaDoRelevo(id) * 255) / 255), { id, peso: 1 });
  }
  assert.deepEqual(relevoDoAlfa(1), { id: 0, peso: 0 });
  assert.deepEqual(relevoDoAlfa(0.995), { id: 0, peso: 0 });
  // na borda de uma região (o filtro da textura mistura o liso com o tipo 3): o peso cai até sumir no meio
  const meio = relevoDoAlfa((alfaDoRelevo(0) + alfaDoRelevo(3)) / 2);
  assert.ok(meio.peso < 0.05, `peso no meio da mistura ${meio.peso}`);
  const perto = relevoDoAlfa(alfaDoRelevo(3) + 4 / 255);
  assert.equal(perto.id, 3);
  assert.ok(perto.peso > 0.5 && perto.peso < 1);
  assert.throws(() => alfaDoRelevo(9), /relevo/);
});

test('polímero acetinado: aspereza de molde e o padrão `molde` (o grão fino só na aspereza)', () => {
  assert.equal(PADROES.at(-1), 'molde');
  assert.deepEqual(PADROES.slice(0, 10), ['nenhum', 'fino', 'granulado', 'flocos', 'carbono', 'veio', 'pontilhado', 'ceramica', 'grao', 'trama']);
  assert.equal(ACABAMENTOS.polimero.padrao, 'molde');
  assert.equal(ACABAMENTOS.polimero.aspereza, 0.45);
  const p = acabamentoParaMaterial({ acabamento: 'polimero', cor: '#1F1F22' });
  assert.equal(p.padraoId, PADROES.indexOf('molde'));
  assert.equal(p.metalness, 0);
  // gasto: o polímero gasto pela mão fica mais liso (o brilho do uso), não mais áspero
  assert.ok(p.gasto.roughness < p.roughness, `gasto ${p.gasto.roughness} × ${p.roughness}`);
});

test('material de zona: o relevo moldado depois da normal assada, com os eixos da arma na vista', () => {
  const texturas = { n: new THREE.Texture(), m: new THREE.Texture() };
  const m = criarMaterialZona({ zona: 'guarnicao', def: { acabamento: 'polimero', cor: '#1F1F22', desgaste: 0.08 }, texturas });
  assert.equal(m.defines.ARMA_RELEVO, '');
  const shader = { uniforms: {}, vertexShader: THREE.ShaderLib.physical.vertexShader, fragmentShader: THREE.ShaderLib.physical.fragmentShader };
  m.onBeforeCompile(shader);
  assert.match(shader.vertexShader, /vEixoYVista = normalize\(/);
  assert.match(shader.vertexShader, /vEixoZVista = normalize\(/);
  const f = shader.fragmentShader;
  const iNormal = f.indexOf('#include <normal_fragment_maps>');
  const iRelevo = f.indexOf('normal = armaAplicarRelevo( normal );');
  assert.ok(iNormal > 0 && iRelevo > iNormal, 'o relevo entra depois da normal assada');
  const iLer = f.indexOf('armaLerRelevo();');
  assert.ok(iLer > f.indexOf('#include <color_fragment>') && iLer < f.indexOf('#include <roughnessmap_fragment>'),
    'o tipo é lido antes da cor e da aspereza');
  assert.ok(f.indexOf('vec4 armaParRelevo(') > f.indexOf('#include <normalmap_pars_fragment>'), 'as contas depois do normalMap');
  // as constantes do shader saem da tabela (passo e altura de cada tipo, em mm)
  for (const r of Object.values(RELEVOS_MOLDADOS)) {
    assert.ok(ARMA_RELEVO_PARS.includes(`${r.passo.toFixed(4)}`), `passo do tipo ${r.id}`);
    assert.ok(ARMA_RELEVO_PARS.includes(`${r.altura.toFixed(4)}`), `altura do tipo ${r.id}`);
  }
  // as luvas (a malha que se deforma na CPU) não têm molde: sem o relevo
  const luva = criarMaterialZona({ zona: 'couro', def: { acabamento: 'couro', cor: '#8B6B4A' }, texturas, repouso: true });
  assert.equal(luva.defines.ARMA_RELEVO, undefined);
});
