// Material de zona das armas realistas (Fase 4.1a; desenho, seção 5.3): os números do acabamento viram o
// MeshPhysicalMaterial; os recursos só ligam quando o acabamento pede; a chave do programa e os defines separam as
// variantes; as texturas e o ambiente entram; o trecho de shader entra nos pontos certos do shader do three r186.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import * as THREE from 'three';
import { ambienteDoMaterial, criarMaterialZona } from '../src/weapons/model/materialArma.js';

const tex = () => ({ n: new THREE.Texture(), m: new THREE.Texture() });

test('material de zona: oxidado de fábrica', () => {
  const t = tex();
  const m = criarMaterialZona({ zona: 'corpo', def: { acabamento: 'oxidado', cor: '#303135', desgaste: 0.22 }, texturas: t });
  assert.ok(m.isMeshPhysicalMaterial);
  assert.equal(m.metalness, 1);
  assert.equal(m.roughness, 0.34);
  assert.equal(m.clearcoat, 0);
  assert.equal(m.iridescence, 0);
  assert.equal(m.anisotropy, 0);
  assert.equal(m.normalMap, t.n);
  assert.equal(m.aoMap, t.m);
  assert.deepEqual(m.normalScale.toArray(), [1, 1]);
  assert.equal(m.defines.ARMA_PADRAO, 1);
  assert.equal(m.defines.ARMA_ESCOVADO, undefined);
  assert.equal(m.userData.uniforms.desgaste.value, 0.22);
  assert.equal(m.userData.uniforms.mapaM.value, t.m);
  assert.equal(m.customProgramCacheKey(), 'arma:fino:');
  assert.equal(m.userData.zona, 'corpo');
  assert.equal(m.userData.shared, true);
  assert.ok(Math.abs(m.color.r - 0.02956) < 0.0005, 'a cor em linear');
});

test('material de zona: recursos do material físico só quando o acabamento pede', () => {
  const pe = criarMaterialZona({ zona: 'corpo', def: { acabamento: 'perolado', cor: 'rosa' }, texturas: tex() });
  assert.equal(pe.clearcoat, 1);
  assert.equal(pe.iridescence, 0.8);
  assert.deepEqual(pe.iridescenceThicknessRange, [250, 600]);
  assert.equal(pe.customProgramCacheKey(), 'arma:nenhum:verniz+iridescencia');
  const es = criarMaterialZona({ zona: 'interno', def: { acabamento: 'escovado', cor: '#ADADAF' }, texturas: tex() });
  assert.equal(es.anisotropy, 0.8);
  assert.equal(es.defines.ARMA_ESCOVADO, '');
  const md = criarMaterialZona({ zona: 'guarnicao', def: { acabamento: 'madeira', cor: '#A4673F', cor2: '#794224' }, texturas: tex() });
  assert.equal(md.defines.ARMA_PADRAO, 5);
  assert.ok(md.userData.uniforms.corDois.value.r < md.color.r, 'o veio mais escuro que a madeira');
});

test('material de zona: o trecho de shader entra nos pontos do shader do three', () => {
  const m = criarMaterialZona({ zona: 'corpo', def: { acabamento: 'escovado', cor: '#ADADAF', desgaste: 0.3 }, texturas: tex() });
  const shader = { uniforms: {}, vertexShader: THREE.ShaderLib.physical.vertexShader, fragmentShader: THREE.ShaderLib.physical.fragmentShader };
  m.onBeforeCompile(shader);
  for (const k of ['mapaM', 'corDois', 'corGasto', 'metalGasto', 'asperezaGasto', 'desgaste', 'varAspereza', 'varCor']) {
    assert.ok(shader.uniforms[k], `uniform ${k}`);
  }
  assert.match(shader.vertexShader, /#else\nvPosArma = position;\nvNormalArma = normal;/);
  assert.match(shader.fragmentShader, /vec4 armaM = texture2D\( mapaM, vAoMapUv \);/);
  assert.match(shader.fragmentShader, /roughnessFactor = mix\( roughnessFactor, asperezaGasto, armaGasto \);/);
  assert.match(shader.fragmentShader, /metalnessFactor = mix\( metalnessFactor, metalGasto, armaGasto \);/);
  assert.match(shader.fragmentShader, /material\.anisotropyT = /);
  const ambiente = new THREE.Texture();
  const versao = m.version;
  ambienteDoMaterial(m, ambiente, 0.8);
  assert.equal(m.envMap, ambiente);
  assert.equal(m.envMapIntensity, 0.8);
  assert.ok(m.version > versao, 'a variante com o ambiente compila de novo');
});
