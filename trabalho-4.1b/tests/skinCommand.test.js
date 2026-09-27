// Comando `skin` do console (Fase 4.1a; desenho, seção 6.3): lista as armas realistas com a skin atual, as skins, os
// acabamentos e as cores; mostra a skin de uma arma; troca pela de fábrica ou por uma nomeada; pinta por zona por cima
// da atual (com desgaste); recusa a arma de massinha e os erros de digitação com a mensagem certa. E o `armas` com a
// origem de cada arma e o `arma` com a mensagem de quem ainda não tem modelo.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { registerWeaponCommands } from '../src/debug/weaponCommands.js';
import { skinDeFabrica } from '../src/weapons/skins/skin.js';

/** Console mínimo com o mesmo registro do console do jogo (nome e apelidos apontam para a definição). */
function fakeConsole() {
  const commands = new Map();
  return {
    commands,
    register(def) {
      commands.set(def.name, def);
      for (const a of def.aliases ?? []) commands.set(a, def);
    },
  };
}

/** Serviços falsos: a biblioteca de armas só com o que os comandos usam (a real é testada em weaponLibraryGlb). */
function montar() {
  const skins = new Map();
  const trocas = [];
  const weaponModels = {
    ids: ['ak47', 'glock'],
    has: (id) => id === 'ak47' || id === 'glock',
    source: (id) => (id === 'ak47' ? 'glb' : id === 'glock' ? 'massinha' : null),
    skinOf: (id) => skins.get(id) ?? skinDeFabrica(id),
    setSkin: (id, skin) => {
      skins.set(id, skin);
      trocas.push([id, skin.chave]);
      return skin;
    },
    report: () => [
      { id: 'ak47', lod: 'perto', source: 'glb', state: 'pronta', triangles: 38412, ms: 180, groups: 6 },
      { id: 'glock', lod: 'perto', source: 'massinha', state: '—', triangles: 0, ms: 0, groups: 0 },
    ],
  };
  const s = {
    config: { spec: () => ({ min: 0, max: 1 }), get: () => 0, set: () => {} },
    weaponModels,
    handModels: { report: () => ({ state: 'pronta', triangles: 5200, ms: 90 }) },
    events: { emit() {} },
    localLoadout: {},
  };
  const con = fakeConsole();
  registerWeaponCommands(con, s, { goState() {}, matchState: () => null });
  return { con, s, trocas };
}

test('skin: lista as realistas, mostra, troca por nome e volta à de fábrica', () => {
  const { con, trocas } = montar();
  const skin = con.commands.get('skin');
  const lista = skin.run([]);
  assert.match(lista, /^ak47: De fábrica$/m);
  assert.match(lista, /^skins: fabrica, Anodizado Terracota, Cromo e Carbono, Madeira Clara e Aço Escovado$/m);
  assert.match(lista, /^acabamentos: oxidado, fosfatizado, /m);
  assert.match(lista, /^cores: preto, brancoTitanio, /m);
  assert.doesNotMatch(lista, /glock/, 'só as realistas');
  assert.match(skin.run(['ak47']), /^ak47 — De fábrica:\n {2}corpo: Oxidado de fábrica #303135 · desgaste 0,22$/m);
  assert.match(skin.run(['AK-47', 'Cromo', 'e', 'Carbono']), /^ak47 — Cromo e Carbono:/);
  assert.deepEqual(trocas.at(-1), ['ak47', 'cromoECarbono']);
  skin.run(['ak47', 'fabrica']);
  assert.deepEqual(trocas.at(-1), ['ak47', 'fabrica']);
  assert.deepEqual(skin.complete(0, ''), ['ak47']);
  assert.ok(skin.complete(1, '').includes('cromoECarbono') && skin.complete(1, '').includes('corpo='));
});

test('skin: pinta por zona por cima da atual, com desgaste; recusa a de massinha e os erros de digitação', () => {
  const { con, s } = montar();
  const skin = con.commands.get('skin');
  const out = skin.run(['ak47', 'corpo=anodizado:terracota', 'desgaste=0,4']);
  assert.match(out, /^ak47 — Personalizada:/);
  assert.match(out, /corpo: Anodizado #C8553D · desgaste 0,4$/m);
  assert.match(out, /guarnicao: Madeira #A4673F,#794224 · desgaste 0,18$/m, 'as outras zonas ficam');
  assert.equal(s.weaponModels.skinOf('ak47').chave, 'personalizada');
  assert.throws(() => skin.run(['glock', 'fabrica']), /glock não é uma arma realista \(skins de acabamento só nas feitas no Blender: ak47\)/);
  assert.throws(() => skin.run(['ak47', 'Dourada']), /skin desconhecida: Dourada/);
  assert.throws(() => skin.run(['ak47', 'cano=fosco:preto']), /zona desconhecida: cano/);
  assert.throws(() => skin.run(['ak47', 'interno=fosco:preto']), /interno só aceita acabamento de metal/);
});

test('armas: a origem de cada uma; arma: a mensagem de quem ainda não tem modelo', () => {
  const { con } = montar();
  const armas = con.commands.get('armas').run([]);
  assert.match(armas, /^arma\s+origem\s+nível/);
  assert.match(armas, /^ak47\s+glb\s+perto\s+pronta\s+38\.412/m);
  assert.match(armas, /^glock\s+massinha\s+perto\s+—/m);
  assert.throws(() => con.commands.get('arma').run(['usps']), /usps ainda não tem modelo \(tem: ak47, glock\)/);
});
