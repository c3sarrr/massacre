// Skins das armas realistas (Fase 4.1a; desenho em docs/superpowers/specs/2026-09-26-armas-realistas-design.md, seção
// 6.3): uma skin é, por zona, acabamento + cor (+ segunda cor) + desgaste. Aqui ficam as contas puras — a skin de
// fábrica de cada arma (src/data/armasReais.js), as nomeadas (src/data/skinsArma.js) por cima da de fábrica, a
// validação, a chave estável (o cache dos materiais) e o comando de console `skin` (texto → pedido → skin nova). Formato
// de uma skin resolvida: {chave, nome, zonas: {zona: {acabamento, cor, cor2, desgaste}}}, cores em "#RRGGBB".

import { ACABAMENTOS } from '../../data/acabamentos.js';
import { ARMAS_REAIS, ZONAS } from '../../data/armasReais.js';
import { SKINS_ARMA } from '../../data/skinsArma.js';
import { normalizarNome, resolverAcabamento, resolverCor } from './acabamento.js';

export const FABRICA = 'fabrica';
export const PERSONALIZADA = 'personalizada';

const SKINS = new Map();
for (const [chave, def] of Object.entries(SKINS_ARMA)) {
  SKINS.set(normalizarNome(chave), chave);
  SKINS.set(normalizarNome(def.nome), chave);
}
const ZONA = new Map(ZONAS.map((z) => [normalizarNome(z), z]));
const USO = 'use <zona>=<acabamento>:<cor>[,<cor2>] (zonas: corpo, guarnicao, carregador, detalhes, interno) e desgaste=<0..1>';
const virgula = (v) => String(v).replace('.', ',');

function arma(id) {
  const a = ARMAS_REAIS[id];
  if (!a) throw new Error(`${id} não é uma arma realista (skins de acabamento só nas armas feitas no Blender)`);
  return a;
}

/** Uma zona validada: acabamento pela chave, cores em "#RRGGBB", desgaste de 0 a 1; o `interno` só aceita metal. */
function zonaValida(zona, def) {
  const acabamento = resolverAcabamento(def?.acabamento);
  if (!acabamento) throw new Error(`${zona}: acabamento desconhecido: ${def?.acabamento}`);
  const cor = resolverCor(def.cor);
  if (!cor) throw new Error(`${zona}: cor desconhecida: ${def.cor}`);
  const cor2 = def.cor2 == null ? null : resolverCor(def.cor2);
  if (def.cor2 != null && !cor2) throw new Error(`${zona}: cor desconhecida: ${def.cor2}`);
  const desgaste = Number(def.desgaste ?? 0);
  if (!(desgaste >= 0 && desgaste <= 1)) throw new Error(`${zona}: desgaste entre 0 e 1 (veio ${def.desgaste})`);
  if (zona === 'interno' && ACABAMENTOS[acabamento].metal !== 1) {
    throw new Error(`interno só aceita acabamento de metal (oxidado, fosfatizado, anodizado, escovado, cromado): ${acabamento}`);
  }
  return { acabamento, cor, cor2, desgaste };
}

/**
 * Pintura completa e válida para uma lista de zonas (as de uma arma, as das luvas): acabamento e cores reconhecidos e
 * desgaste de 0 a 1 em cada zona.
 */
export function validarPintura(zonasDaPeca, pintura, rotulo = 'pintura') {
  const zonas = {};
  for (const z of zonasDaPeca) {
    if (!pintura?.zonas?.[z]) throw new Error(`${rotulo} sem a zona ${z}`);
    zonas[z] = zonaValida(z, pintura.zonas[z]);
  }
  return { chave: pintura.chave ?? PERSONALIZADA, nome: pintura.nome ?? 'Personalizada', zonas };
}

/** Skin completa e válida para a arma (todas as zonas dela). */
export function validarSkin(id, skin) {
  return validarPintura(arma(id).zonas, skin, `skin de ${id}`);
}

/** A pintura de fábrica da arma. */
export function skinDeFabrica(id) {
  const a = arma(id);
  return validarSkin(id, { chave: FABRICA, nome: a.fabrica.nome, zonas: a.fabrica.zonas });
}

/** Chave da skin nomeada pela chave ou pelo nome (sem acento nem espaço), ou null. */
export function resolverSkinNomeada(nome) {
  return SKINS.get(normalizarNome(nome)) ?? null;
}

/** Skin por nome: "fabrica" ou uma nomeada, por cima da de fábrica (a zona que a skin não traz fica de fábrica). */
export function skinPorNome(id, nome) {
  const fab = skinDeFabrica(id);
  if (normalizarNome(nome) === FABRICA) return fab;
  const chave = resolverSkinNomeada(nome);
  if (!chave) throw new Error(`skin desconhecida: ${nome} (tem: fabrica, ${Object.values(SKINS_ARMA).map((s) => s.nome).join(', ')})`);
  const def = SKINS_ARMA[chave];
  const zonas = {};
  for (const z of Object.keys(fab.zonas)) zonas[z] = def.zonas[z] ?? fab.zonas[z];
  return validarSkin(id, { chave, nome: def.nome, zonas });
}

/** Chave estável da skin: a da tabela, ou "p:" + o hash do conteúdo para a personalizada (o cache dos materiais). */
export function chaveDaSkin(skin) {
  if (skin.chave !== PERSONALIZADA) return skin.chave;
  const texto = JSON.stringify(Object.keys(skin.zonas).sort().map((z) => [z, skin.zonas[z]]));
  let h = 0x811c9dc5;
  for (let i = 0; i < texto.length; i++) h = Math.imul(h ^ texto.charCodeAt(i), 0x01000193) >>> 0;
  return `p:${h.toString(16).padStart(8, '0')}`;
}

/**
 * Argumentos do comando `skin` depois do id da arma:
 *   []                                        → {tipo: 'mostrar'}
 *   ['fabrica'] ou ['Anodizado', 'Terracota'] → {tipo: 'nome', nome} (a chave; o nome pode ter espaços)
 *   ['corpo=anodizado:terracota', 'guarnicao=madeira:areia,marromSiena', 'desgaste=0.3']
 *                                             → {tipo: 'zonas', zonas: {zona: {acabamento, cor, cor2}}, desgaste}
 */
export function lerArgumentosSkin(args) {
  if (!args.length) return { tipo: 'mostrar' };
  if (!args.some((a) => a.includes('='))) {
    const nome = args.join(' ');
    if (normalizarNome(nome) === FABRICA) return { tipo: 'nome', nome: FABRICA };
    const chave = resolverSkinNomeada(nome);
    if (!chave) throw new Error(`skin desconhecida: ${nome} (tem: fabrica, ${Object.values(SKINS_ARMA).map((s) => s.nome).join(', ')})`);
    return { tipo: 'nome', nome: chave };
  }
  const zonas = {};
  let desgaste = null;
  for (const arg of args) {
    const [k, v] = arg.split('=');
    if (v === undefined || !k) throw new Error(`argumento sem "=": ${arg} (${USO})`);
    if (normalizarNome(k) === 'desgaste') {
      desgaste = Number(v.replace(',', '.'));
      if (!(desgaste >= 0 && desgaste <= 1)) throw new Error(`desgaste entre 0 e 1 (veio ${v})`);
      continue;
    }
    const zona = ZONA.get(normalizarNome(k));
    if (!zona) throw new Error(`zona desconhecida: ${k} (${USO})`);
    const [acab, cores] = v.split(':');
    if (!acab || !cores) throw new Error(`${arg}: ${USO}`);
    const acabamento = resolverAcabamento(acab);
    if (!acabamento) throw new Error(`acabamento desconhecido: ${acab} (use ${Object.keys(ACABAMENTOS).join(', ')})`);
    const [c1, c2] = cores.split(',');
    const cor = resolverCor(c1);
    if (!cor) throw new Error(`cor desconhecida: ${c1}`);
    const cor2 = c2 === undefined ? null : resolverCor(c2);
    if (c2 !== undefined && !cor2) throw new Error(`cor desconhecida: ${c2}`);
    zonas[zona] = { acabamento, cor, cor2 };
  }
  return { tipo: 'zonas', zonas, desgaste };
}

/**
 * Aplica um pedido de zonas numa skin: troca as zonas citadas (com o desgaste pedido, ou o que a zona tinha) e, sem
 * zona citada, põe o desgaste em todas. O resultado é a skin personalizada.
 */
export function aplicarZonas(id, atual, pedido) {
  const a = arma(id);
  const zonas = {};
  const citadas = Object.keys(pedido.zonas ?? {});
  for (const z of citadas) if (!a.zonas.includes(z)) throw new Error(`${id} não tem a zona ${z}`);
  for (const z of a.zonas) {
    const velha = atual.zonas[z];
    const nova = pedido.zonas?.[z];
    if (nova) zonas[z] = { ...nova, desgaste: pedido.desgaste ?? velha.desgaste };
    else if (!citadas.length && pedido.desgaste != null) zonas[z] = { ...velha, desgaste: pedido.desgaste };
    else zonas[z] = velha;
  }
  return validarSkin(id, { chave: PERSONALIZADA, nome: 'Personalizada', zonas });
}

/** Uma linha por zona, para o console: "corpo: Oxidado de fábrica #303135 · desgaste 0,22". */
export function descreverSkin(skin) {
  return Object.entries(skin.zonas).map(([z, d]) =>
    `${z}: ${ACABAMENTOS[d.acabamento].nome} ${d.cor}${d.cor2 ? `,${d.cor2}` : ''} · desgaste ${virgula(d.desgaste)}`);
}
