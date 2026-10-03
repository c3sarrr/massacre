// Testes das receitas das armas de massinha (Fase 4.1; docs/phases/phase-4.md, seção 4.1, "Testes"): as três que ainda
// são de massinha validam (a AK-47 virou a arma realista do Blender na 4.1a; a Glock-18, a M4A4 e a faca, na 4.1c);
// grupos, âncoras e massas por arma (a tabela do primeiro lote); a espessura mínima (e a receita que a quebra é
// recusada); o acento pela facção; a silhueta lateral × a planta de referência com IoU ≥ 0,8; o comprimento real da
// tabela de escala; árvores determinísticas (a mesma chave de cache); e a categoria de cada uma no viewmodel.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { ARMAS } from '../src/data/armas/index.js';
import { ARMAS_REAIS } from '../src/data/armasReais.js';
import { FACTION_ACCENTS, WEAPON_CLAYS, WEAPON_MODEL } from '../src/data/weaponPalette.js';
import { HAND_POSES } from '../src/data/hands.js';
import { VIEWMODEL } from '../src/data/viewmodel.js';
import { WEAPONS } from '../src/data/weapons.js';
import {
  materialSlots, partThickness, recipeTrees, recipeWholeTree, resolveClay, validateRecipe, weaponFaction,
} from '../src/weapons/model/recipe.js';
import { meshOptions } from '../src/weapons/model/weaponModel.js';
import { silhouetteIoU, silhouetteLength } from '../src/weapons/model/silhouette.js';
import { hashNode } from '../src/clay/sdf/nodes.js';
import { plantaDoArquivo } from '../src/weapons/model/ficha.js';

const IDS = ['awp', 'nova', 'p90'];

// A tabela do primeiro lote (phase-4.md): facção do acento, massas, grupos e o comprimento real (u).
const TABLE = {
  awp: { faction: 'ambos', clays: ['verdeOliva', 'grafite'], groups: ['corpo', 'carregador', 'alavanca', 'gatilho'], length: 48.4 },
  nova: { faction: 'ambos', clays: ['grafite', 'grafiteClaro'], groups: ['corpo', 'bomba', 'gatilho'], length: 39.2 },
  p90: { faction: 'ambos', clays: ['grafite', 'grafiteClaro'], groups: ['corpo', 'carregador', 'gatilho'], length: 19.7 },
};

const plan = (id) => plantaDoArquivo(JSON.parse(readFileSync(new URL(`../tools/blender/refs/${id}.json`, import.meta.url), 'utf8')));
// As de massinha com a planta da 4.1 (formato 1) em tools/blender/refs/ (a ficha no formato 2 é a da arma real, que
// chega com o modelo do Blender e tira a receita daqui).
const COM_PLANTA = IDS.filter((x) => JSON.parse(readFileSync(new URL(`../tools/blender/refs/${x}.json`, import.meta.url), 'utf8')).formato !== 2);

test('receitas: as de massinha estão no registro, validam e são das armas da tabela', () => {
  assert.deepEqual(Object.keys(ARMAS).sort(), [...IDS].sort());
  for (const id of IDS) {
    const r = ARMAS[id];
    assert.equal(r.id, id);
    assert.ok(WEAPONS[id], `${id} existe em src/data/weapons.js`);
    assert.doesNotThrow(() => validateRecipe(r), id);
  }
});

test('receitas: grupos, âncoras e massas por arma (a tabela do primeiro lote)', () => {
  for (const id of IDS) {
    const r = ARMAS[id];
    const t = TABLE[id];
    assert.deepEqual(Object.keys(r.groups).sort(), [...t.groups].sort(), `${id}: grupos`);
    const clays = new Set(Object.values(r.materials));
    for (const c of t.clays) assert.ok(clays.has(c), `${id}: falta a massa ${c}`);
    for (const c of clays) assert.ok(WEAPON_CLAYS[c] || c === 'acento' || c === 'acento2', `${id}: massa ${c}`);
    const melee = WEAPONS[id].slot === 'melee';
    const expected = melee ? ['maoDireita'] : ['boca', 'ejecao', 'maoDireita', 'maoEsquerda'];
    for (const a of expected) assert.ok(r.anchors[a], `${id}: falta a âncora ${a}`);
    if (melee) assert.equal(r.anchors.maoEsquerda, undefined, 'a faca é de uma mão só');
    for (const side of ['maoDireita', 'maoEsquerda']) {
      const a = r.anchors[side];
      if (a) assert.ok(HAND_POSES[a.pose], `${id}.${side}: pose ${a.pose}`);
    }
    // Toda massa declarada é usada por alguma peça de massa (a lista de materiais das malhas sai daí).
    const used = materialSlots(r);
    assert.ok(used.length >= 2, `${id}: massas usadas ${used}`);
    for (const slot of used) assert.ok(r.materials[slot], `${id}: ${slot}`);
  }
});

test('receitas: nenhuma peça de massa fica mais fina que o mínimo (a peça de lâmina é a exceção)', () => {
  for (const id of IDS) {
    for (const p of ARMAS[id].parts) {
      if (p.op === 'subtract') continue;
      const min = p.thin ? WEAPON_MODEL.minBlade : WEAPON_MODEL.minThickness;
      assert.ok(partThickness(p) >= min - 1e-9, `${id}.${p.name}: ${partThickness(p)} < ${min}`);
    }
  }
  // A peça de lâmina (`thin`, a da faca de massinha da 4.1) vale até o mínimo dela, 0,5 u; uma peça fina demais é
  // recusada, com o nome dela no erro.
  const fina = structuredClone(ARMAS.awp);
  const lamina = fina.parts.find((p) => p.shape === 'profile' && p.op !== 'subtract');
  lamina.thin = true;
  lamina.h = WEAPON_MODEL.minBlade / 2;
  assert.ok(Math.abs(partThickness(lamina) - WEAPON_MODEL.minBlade) < 1e-9);
  assert.doesNotThrow(() => validateRecipe(fina));
  const bad = structuredClone(ARMAS.awp);
  const part = bad.parts.find((p) => p.shape === 'profile' && p.op !== 'subtract');
  part.h = 0.4;
  assert.throws(() => validateRecipe(bad), new RegExp(part.name));
});

test('receitas: acento pela facção (as de um lado ficam com o seu; as dos dois lados trocam)', () => {
  for (const id of IDS) {
    assert.equal(weaponFaction(id), TABLE[id].faction, id);
    const r = ARMAS[id];
    const accentSlot = Object.keys(r.materials).find((k) => r.materials[k] === 'acento');
    for (const f of ['tr', 'ct', 'ambos']) {
      assert.equal(resolveClay(r, accentSlot, f).color, FACTION_ACCENTS[f].acento, `${id}/${f}`);
    }
    // Sem facção pedida, o acento é o da própria arma.
    assert.equal(resolveClay(r, accentSlot).color, FACTION_ACCENTS[TABLE[id].faction].acento, `${id}: padrão`);
  }
});

test('receitas: silhueta lateral × planta de referência com IoU ≥ 0,8 (as de massinha com planta da 4.1)', () => {
  for (const id of COM_PLANTA) {
    const { iou, sdfArea, refArea } = silhouetteIoU(ARMAS[id], plan(id), { cell: 0.1 });
    assert.ok(iou >= WEAPON_MODEL.silhouetteIoU, `${id}: IoU ${iou.toFixed(3)} (massa ${sdfArea.toFixed(1)} u², planta ${refArea.toFixed(1)} u²)`);
  }
});

test('receitas: o comprimento real é o da tabela de escala (e o da planta)', () => {
  for (const id of IDS) {
    const len = silhouetteLength(ARMAS[id], { cell: 0.05 });
    assert.ok(Math.abs(len - TABLE[id].length) <= 0.15, `${id}: ${len.toFixed(2)} u (tabela ${TABLE[id].length})`);
    if (COM_PLANTA.includes(id)) assert.equal(plan(id).lengthU, TABLE[id].length, `${id}: planta`);
  }
});

test('receitas: árvores determinísticas (a mesma chave de cache do SdfMesher)', () => {
  for (const id of IDS) {
    const a = recipeTrees(ARMAS[id]);
    const b = recipeTrees(structuredClone(ARMAS[id]));
    assert.deepEqual(a.materials, b.materials, id);
    for (const g of Object.keys(a.groups)) {
      for (const lod of Object.keys(WEAPON_MODEL.lods)) {
        const oa = meshOptions(a.groups[g].tree, lod);
        const ob = meshOptions(b.groups[g].tree, lod);
        assert.deepEqual(oa, ob);
        assert.equal(hashNode(a.groups[g].tree, oa), hashNode(b.groups[g].tree, ob), `${id}.${g}.${lod}`);
      }
    }
    assert.equal(hashNode(recipeWholeTree(ARMAS[id])), hashNode(recipeWholeTree(structuredClone(ARMAS[id]))));
  }
});

test('receitas: cada uma tem categoria no viewmodel', () => {
  for (const id of IDS) {
    const w = VIEWMODEL.weapons[id];
    assert.ok(w && VIEWMODEL.categories[w.category], `${id}: categoria ${w?.category}`);
  }
  for (const id of Object.keys(VIEWMODEL.weapons)) assert.ok(ARMAS[id] || ARMAS_REAIS[id], `${id}: categoria sem modelo`);
});
