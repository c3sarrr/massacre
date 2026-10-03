// Comando `skin` do console (Fase 4.1a; desenho, seção 6.3): lista as armas realistas com a skin atual, as skins, os
// acabamentos e as cores; mostra a skin de uma arma; troca pela de fábrica ou por uma nomeada; pinta por zona por cima
// da atual (com desgaste); recusa a arma de massinha e os erros de digitação com a mensagem certa. E o `armas` com a
// origem de cada arma e o `arma` com a mensagem de quem ainda não tem modelo. Desde a 4.1c (Tarefa 13): as quatro
// realistas (a AK, a Glock, a M4A4 e a M9), cada uma com as zonas da classe dela — a faca sem carregador nem interno, no
// completar, no mostrar e na pintura por zona.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { ARMAS_REAIS } from '../src/data/armasReais.js';
import { registerWeaponCommands } from '../src/debug/weaponCommands.js';
import { skinDeFabrica } from '../src/weapons/skins/skin.js';

const REAIS = Object.keys(ARMAS_REAIS);
// A de massinha do teste: a AWP (a 4.1d a faz realista).
const MASSINHA = 'awp';

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
  const ids = [...REAIS, MASSINHA];
  const weaponModels = {
    ids,
    has: (id) => ids.includes(id),
    source: (id) => (REAIS.includes(id) ? 'glb' : id === MASSINHA ? 'massinha' : null),
    skinOf: (id) => skins.get(id) ?? skinDeFabrica(id),
    setSkin: (id, skin) => {
      skins.set(id, skin);
      trocas.push([id, skin.chave]);
      return skin;
    },
    report: () => [
      { id: 'ak47', lod: 'perto', source: 'glb', state: 'pronta', triangles: 38412, ms: 180, groups: 6 },
      { id: 'knife', lod: 'perto', source: 'glb', state: 'pronta', triangles: 9120, ms: 60, groups: 1 },
      { id: MASSINHA, lod: 'perto', source: 'massinha', state: '—', triangles: 0, ms: 0, groups: 0 },
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
  for (const id of REAIS) assert.match(lista, new RegExp(`^${id}: De fábrica$`, 'm'));
  assert.match(lista, /^skins: fabrica, Anodizado Terracota, Cromo e Carbono, Madeira Clara e Aço Escovado$/m);
  assert.match(lista, /^acabamentos: oxidado, fosfatizado, /m);
  assert.match(lista, /^cores: preto, brancoTitanio, /m);
  assert.doesNotMatch(lista, new RegExp(MASSINHA), 'só as realistas');
  assert.match(skin.run(['ak47']), /^ak47 — De fábrica:\n {2}corpo: Oxidado de fábrica #303135 · desgaste 0,22$/m);
  assert.match(skin.run(['AK-47', 'Cromo', 'e', 'Carbono']), /^ak47 — Cromo e Carbono:/);
  assert.deepEqual(trocas.at(-1), ['ak47', 'cromoECarbono']);
  skin.run(['ak47', 'fabrica']);
  assert.deepEqual(trocas.at(-1), ['ak47', 'fabrica']);
  assert.deepEqual(skin.complete(0, ''), REAIS);
  const daAk = skin.complete(1, '', ['ak47']);
  assert.ok(daAk.includes('cromoECarbono') && daAk.includes('corpo=') && daAk.includes('carregador=') && daAk.includes('interno='));
  // as zonas que o completar oferece são as da arma do primeiro argumento (pelo id ou pelo nome)
  assert.deepEqual(skin.complete(1, '', ['knife']).filter((c) => c.endsWith('=')), ['corpo=', 'guarnicao=', 'detalhes=', 'desgaste=']);
  assert.ok(skin.complete(2, '', ['M4A4', 'corpo=fosco:preto']).includes('carregador='));
  assert.deepEqual(skin.complete(1, '', [MASSINHA]), [], 'nada para a de massinha');
  assert.deepEqual(skin.complete(1, '', []), []);
});

test('skin: a Glock, a M4A4 e a faca, cada uma nas zonas da classe dela (a faca sem carregador nem interno)', () => {
  const { con, s, trocas } = montar();
  const skin = con.commands.get('skin');
  assert.match(skin.run(['glock']), /^glock — De fábrica:\n {2}corpo: Fosfatizado #34353A · desgaste 0,12$/m);
  assert.match(skin.run(['m4a4']), /^ {2}carregador: Acetinado #43463F · desgaste 0,24$/m);
  const faca = skin.run(['knife']);
  assert.equal(faca.split('\n').length, 4, 'o título e as três zonas da faca');
  assert.match(faca, /^ {2}guarnicao: Polímero texturizado #4A4234 · desgaste 0,1$/m);
  assert.doesNotMatch(faca, /carregador|interno/);
  // a nomeada vale na faca nas zonas que ela tem
  assert.match(skin.run(['knife', 'Cromo', 'e', 'Carbono']), /^knife — Cromo e Carbono:\n {2}corpo: Cromado #EDEDE8 · desgaste 0,05$/m);
  assert.deepEqual(trocas.at(-1), ['knife', 'cromoECarbono']);
  assert.deepEqual(Object.keys(s.weaponModels.skinOf('knife').zonas), ['corpo', 'guarnicao', 'detalhes']);
  // pintar por zona na faca: as zonas dela valem; carregador e interno não existem nela
  assert.match(skin.run(['knife', 'guarnicao=madeira:areia,marromSiena']), /guarnicao: Madeira #C2A878,#8C5A3C · desgaste 0,05$/m);
  assert.throws(() => skin.run(['knife', 'carregador=fosco:preto']), /knife não tem a zona carregador \(tem: corpo, guarnicao, detalhes\)/);
  assert.throws(() => skin.run(['knife', 'interno=escovado:preto']), /knife não tem a zona interno/);
  // a Glock pinta o carregador de polímero
  assert.match(skin.run(['glock', 'carregador=polimero:areia']), /carregador: Polímero texturizado #C2A878 · desgaste 0,1$/m);
});

test('skin: pinta por zona por cima da atual, com desgaste; recusa a de massinha e os erros de digitação', () => {
  const { con, s } = montar();
  const skin = con.commands.get('skin');
  const out = skin.run(['ak47', 'corpo=anodizado:terracota', 'desgaste=0,4']);
  assert.match(out, /^ak47 — Personalizada:/);
  assert.match(out, /corpo: Anodizado #C8553D · desgaste 0,4$/m);
  assert.match(out, /guarnicao: Madeira #A4673F,#794224 · desgaste 0,18$/m, 'as outras zonas ficam');
  assert.equal(s.weaponModels.skinOf('ak47').chave, 'personalizada');
  assert.throws(() => skin.run([MASSINHA, 'fabrica']),
    new RegExp(`${MASSINHA} não é uma arma realista \\(skins de acabamento só nas feitas no Blender: ${REAIS.join(', ')}\\)`));
  assert.throws(() => skin.run(['ak47', 'Dourada']), /skin desconhecida: Dourada/);
  assert.throws(() => skin.run(['ak47', 'cano=fosco:preto']), /zona desconhecida: cano/);
  assert.throws(() => skin.run(['ak47', 'interno=fosco:preto']), /interno só aceita acabamento de metal/);
});

test('armas: a origem de cada uma; arma: a mensagem de quem ainda não tem modelo', () => {
  const { con } = montar();
  const armas = con.commands.get('armas').run([]);
  assert.match(armas, /^arma\s+origem\s+nível/);
  assert.match(armas, /^ak47\s+glb\s+perto\s+pronta\s+38\.412/m);
  assert.match(armas, /^knife\s+glb\s+perto\s+pronta\s+9\.120/m);
  assert.match(armas, new RegExp(`^${MASSINHA}\\s+massinha\\s+perto\\s+—`, 'm'));
  assert.throws(() => con.commands.get('arma').run(['usps']), new RegExp(`usps ainda não tem modelo \\(tem: ${[...REAIS, MASSINHA].join(', ')}\\)`));
});
