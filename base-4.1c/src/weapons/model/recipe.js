// Receita de arma de massinha (Fase 4.1; formato em docs/phases/phase-4.md, seção 4.1, "Receita"): validação e as
// árvores SDF de cada grupo animável. Puro (sem three.js): o gerador (weaponModel.js), os testes do Node e o
// exportador do Blender (pela mesma validação, via tools/blender.mjs) usam o mesmo código.
// Referencial da arma: +X para a boca do cano, +Y para cima, +Z para o lado direito; origem no eixo do cano sobre o
// gatilho. Unidades: u (polegada na escala do boneco).

import { WEAPONS } from '../../data/weapons.js';
import { ACCENT_CLAY, FACTION_ACCENTS, WEAPON_CLAYS, WEAPON_MODEL } from '../../data/weaponPalette.js';
import { HAND_POSES } from '../../data/hands.js';

export const RECIPE_VERSION = 1;

/** Formas aceitas numa peça (as do SDF, src/clay/sdf/shapes.js) e os parâmetros de cada uma. */
export const RECIPE_SHAPES = Object.freeze({
  roundBox: Object.freeze(['size', 'r']),
  cylinder: Object.freeze(['h', 'r', 'round']),
  capsule: Object.freeze(['a', 'b', 'r']),
  sphere: Object.freeze(['r']),
  ellipsoid: Object.freeze(['radii']),
  roundCone: Object.freeze(['a', 'b', 'ra', 'rb']),
  torus: Object.freeze(['R', 'r']),
  cone: Object.freeze(['h', 'r1', 'r2']),
  profile: Object.freeze(['points', 'h', 'round', 'corner']),
  lathe: Object.freeze(['points', 'corner', 'closed']),
  tube: Object.freeze(['points', 'r', 'radii']),
});

/** Grupos que se mexem (cada um vira malha própria); `corpo` é obrigatório. */
export const RECIPE_GROUPS = Object.freeze(['corpo', 'carregador', 'ferrolho', 'slide', 'gatilho', 'bomba', 'alavanca', 'silenciador']);

/** Âncoras: as de mão levam a pose; `boca` e `ejecao` apontam pelo +X da própria rotação. */
export const RECIPE_ANCHORS = Object.freeze(['maoDireita', 'maoEsquerda', 'boca', 'ejecao', 'mira']);
const HAND_ANCHORS = Object.freeze(['maoDireita', 'maoEsquerda']);

/** Massas especiais resolvidas pela facção. */
export const ACCENT_SLOTS = Object.freeze(['acento', 'acento2']);

const fail = (id, where, msg) => {
  throw new Error(`receita de arma ${id ?? '?'} inválida em ${where}: ${msg}`);
};

const isVec = (v, n) => Array.isArray(v) && v.length === n && v.every((c) => typeof c === 'number' && Number.isFinite(c));

/** Facção do acento de uma arma: 'tr', 'ct' ou 'ambos' (as dos dois lados, a faca). */
export function weaponFaction(id) {
  const team = WEAPONS[id]?.team;
  return team === 'tr' || team === 'ct' ? team : 'ambos';
}

/** Menor espessura de uma peça (u), pela forma. */
export function partThickness(part) {
  switch (part.shape) {
    case 'profile':
      return 2 * part.h;
    case 'lathe':
      return 2 * Math.max(...part.points.map((p) => p[1]));
    case 'tube':
      return 2 * (part.radii ? Math.min(...part.radii) : part.r);
    case 'cylinder':
      return 2 * Math.min(part.r, part.h);
    case 'capsule':
    case 'sphere':
    case 'torus':
      return 2 * part.r;
    case 'ellipsoid':
      return 2 * Math.min(...part.radii);
    case 'roundBox':
      return 2 * Math.min(...part.size);
    case 'roundCone':
      return 2 * Math.min(part.ra, part.rb);
    case 'cone':
      return 2 * Math.max(part.r1, part.r2);
    default:
      return 0;
  }
}

/**
 * Valida uma receita e devolve a mesma receita (congelada em profundidade não; só conferida). Lança Error dizendo
 * a arma, o lugar e o problema.
 */
export function validateRecipe(recipe) {
  const id = recipe?.id;
  if (!recipe || typeof recipe !== 'object') fail(id, 'raiz', 'a receita precisa ser um objeto');
  if (typeof id !== 'string' || !WEAPONS[id]) fail(id, 'id', `arma desconhecida ${JSON.stringify(id)}`);
  if (recipe.version !== RECIPE_VERSION) fail(id, 'version', `formato ${recipe.version} (esperado ${RECIPE_VERSION})`);
  const mats = recipe.materials;
  if (!mats || typeof mats !== 'object') fail(id, 'materials', 'faltam as massas');
  for (const [slot, clay] of Object.entries(mats)) {
    if (!(ACCENT_SLOTS.includes(clay) || WEAPON_CLAYS[clay])) fail(id, `materials.${slot}`, `massa desconhecida ${JSON.stringify(clay)}`);
  }
  const groups = recipe.groups;
  if (!groups || typeof groups !== 'object' || !groups.corpo) fail(id, 'groups', "falta o grupo 'corpo'");
  for (const [g, def] of Object.entries(groups)) {
    if (!RECIPE_GROUPS.includes(g)) fail(id, `groups.${g}`, `grupo desconhecido (use ${RECIPE_GROUPS.join(', ')})`);
    if (def.pivot !== undefined && !isVec(def.pivot, 3)) fail(id, `groups.${g}.pivot`, 'precisa ser [x, y, z]');
    if (def.axis !== undefined && !isVec(def.axis, 3)) fail(id, `groups.${g}.axis`, 'precisa ser [x, y, z]');
  }
  const anchors = recipe.anchors ?? {};
  for (const [a, def] of Object.entries(anchors)) {
    if (!RECIPE_ANCHORS.includes(a)) fail(id, `anchors.${a}`, `âncora desconhecida (use ${RECIPE_ANCHORS.join(', ')})`);
    if (!isVec(def.pos, 3)) fail(id, `anchors.${a}.pos`, 'precisa ser [x, y, z]');
    if (def.rot !== undefined && !isVec(def.rot, 3)) fail(id, `anchors.${a}.rot`, 'precisa ser [x, y, z] (Euler XYZ, rad)');
    if (HAND_ANCHORS.includes(a) && !HAND_POSES[def.pose]) fail(id, `anchors.${a}.pose`, `pose de mão desconhecida ${JSON.stringify(def.pose)}`);
  }
  if (!anchors.maoDireita) fail(id, 'anchors', "falta a âncora 'maoDireita'");
  const melee = WEAPONS[id].slot === 'melee';
  if (!melee) for (const a of ['boca', 'ejecao', 'maoEsquerda']) if (!anchors[a]) fail(id, 'anchors', `falta a âncora '${a}'`);
  const parts = recipe.parts;
  if (!Array.isArray(parts) || parts.length === 0) fail(id, 'parts', 'a arma não tem peças');
  const names = new Set();
  const minimum = recipe.minThickness ?? WEAPON_MODEL.minThickness;
  for (let i = 0; i < parts.length; i++) {
    const p = parts[i];
    const where = `parts[${i}] (${p?.name ?? 'sem nome'})`;
    if (typeof p?.name !== 'string' || !p.name) fail(id, where, 'peça sem nome');
    if (names.has(p.name)) fail(id, where, 'nome repetido');
    names.add(p.name);
    if (!groups[p.group]) fail(id, where, `grupo ${JSON.stringify(p.group)} não existe em 'groups'`);
    if (!mats[p.mat]) fail(id, where, `massa ${JSON.stringify(p.mat)} não existe em 'materials'`);
    if (!RECIPE_SHAPES[p.shape]) fail(id, where, `forma desconhecida ${JSON.stringify(p.shape)}`);
    if (p.pos !== undefined && !isVec(p.pos, 3)) fail(id, where, "'pos' precisa ser [x, y, z]");
    if (p.rot !== undefined && !isVec(p.rot, 3)) fail(id, where, "'rot' precisa ser [x, y, z]");
    if (p.op !== undefined && p.op !== 'subtract') fail(id, where, `op ${JSON.stringify(p.op)} (só 'subtract')`);
    if (p.k !== undefined && !(p.k >= 0)) fail(id, where, "'k' precisa ser ≥ 0");
    if (p.op !== 'subtract') {
      const min = p.thin ? WEAPON_MODEL.minBlade : minimum;
      const t = partThickness(p);
      if (!(t >= min - 1e-9)) fail(id, where, `mais fina que a massa mínima (${t.toFixed(3)} u < ${min} u)`);
    }
  }
  for (const g of Object.keys(groups)) {
    if (!parts.some((p) => p.group === g && p.op !== 'subtract')) fail(id, `groups.${g}`, 'grupo sem nenhuma peça de massa');
  }
  return recipe;
}

/** Massas usadas pelas peças, na ordem em que aparecem: o índice é o `mat` da árvore e do array de materiais. */
export function materialSlots(recipe) {
  const out = [];
  for (const p of recipe.parts) if (p.op !== 'subtract' && !out.includes(p.mat)) out.push(p.mat);
  return out;
}

/**
 * Massa de um slot já com a facção: {color, roughness, wetness, skin?, colorB?, colorC?}.
 * @param {object} recipe
 * @param {string} slot
 * @param {'tr'|'ct'|'ambos'} [faction] padrão: a facção da arma
 */
export function resolveClay(recipe, slot, faction = weaponFaction(recipe.id)) {
  const clay = recipe.materials[slot];
  if (ACCENT_SLOTS.includes(clay)) {
    const accents = FACTION_ACCENTS[faction] ?? FACTION_ACCENTS.ambos;
    return { color: accents[clay], roughness: ACCENT_CLAY.roughness, wetness: ACCENT_CLAY.wetness };
  }
  return { ...WEAPON_CLAYS[clay] };
}

// Nó SDF de uma peça no referencial da arma (os parâmetros da forma passam direto).
function partNode(p, matIndex) {
  const node = { type: p.shape, mat: matIndex };
  for (const key of RECIPE_SHAPES[p.shape]) if (p[key] !== undefined) node[key] = p[key];
  if (p.pos) node.pos = p.pos;
  if (p.rot) node.rot = p.rot;
  return node;
}

/**
 * Árvore SDF de cada grupo, no referencial do pivô do grupo (a malha gira em volta dele).
 * Peças somadas numa união suave com vinco por suavidade (peças com `k`/`crease` próprios num grupo à parte),
 * calombos por cima, e os cortes numa subtração suave.
 * @returns {{materials:string[], groups:Object<string, {tree:object, pivot:number[], axis:number[]|null}>}}
 */
export function recipeTrees(recipe) {
  // `soft` opcional na receita: {k, crease: {depth, width}, lumps: {amp, freq, octaves}} por cima do padrão.
  const k0 = recipe.soft?.k ?? WEAPON_MODEL.soft;
  const crease = { ...WEAPON_MODEL.crease, ...(recipe.soft?.crease ?? {}) };
  const lumps = { ...WEAPON_MODEL.lumps, ...(recipe.soft?.lumps ?? {}) };
  const seamWidth = WEAPON_MODEL.seamWidth;
  const slots = materialSlots(recipe);
  const groups = {};
  for (const [name, def] of Object.entries(recipe.groups)) {
    const pivot = def.pivot ?? [0, 0, 0];
    const mine = recipe.parts.filter((p) => p.group === name);
    // Baldes por suavidade: n-ário (raso) em vez de uma cadeia binária de dezenas de níveis.
    const buckets = new Map();
    for (const p of mine) {
      if (p.op === 'subtract') continue;
      const k = p.k ?? k0;
      const c = { ...crease, ...(p.crease ?? {}) };
      const key = `${k}|${c.depth}|${c.width}`;
      if (!buckets.has(key)) buckets.set(key, { k, crease: c, nodes: [] });
      buckets.get(key).nodes.push(partNode(p, slots.indexOf(p.mat)));
    }
    const unions = [...buckets.values()].map((b) => ({
      type: 'smoothUnionCrease', k: b.k, depth: b.crease.depth, width: b.crease.width, seamWidth, children: b.nodes,
    }));
    let tree = unions.length === 1 ? unions[0] : {
      type: 'smoothUnionCrease', k: k0, depth: crease.depth, width: crease.width, seamWidth, children: unions,
    };
    if (lumps.amp > 0) {
      tree = { type: 'displace', amp: lumps.amp, freq: lumps.freq, octaves: lumps.octaves, seed: `${recipe.id}:${name}`, child: tree };
    }
    const cuts = mine.filter((p) => p.op === 'subtract').map((p) => partNode(p, 0));
    if (cuts.length) {
      tree = { type: 'smoothSubtract', k: WEAPON_MODEL.cutSoft, a: tree, b: cuts.length === 1 ? cuts[0] : { type: 'union', children: cuts } };
    }
    if (pivot.some((c) => c !== 0)) tree = { type: 'transform', pos: pivot.map((c) => -c), child: tree };
    groups[name] = { tree, pivot, axis: def.axis ?? null };
  }
  return { materials: slots, groups };
}

/** Árvore da arma inteira no referencial da arma (todos os grupos na posição de repouso): silhueta e testes. */
export function recipeWholeTree(recipe) {
  const { groups } = recipeTrees(recipe);
  const children = Object.values(groups).map((g) => (g.pivot.some((c) => c !== 0) ? { type: 'transform', pos: g.pivot, child: g.tree } : g.tree));
  return children.length === 1 ? children[0] : { type: 'union', children };
}
