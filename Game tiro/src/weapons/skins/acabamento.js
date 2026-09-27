// Acabamento + cor + desgaste → parâmetros do material físico das armas realistas (Fase 4.1a; desenho em
// docs/superpowers/specs/2026-09-26-armas-realistas-design.md, seções 5.3 e 6). Função pura, testada no Node: o
// material de cada zona (src/weapons/model/materialArma.js) só copia estes números; nada aqui depende do three.
// Também os nomes digitados no console: sem acento, sem espaço, pela chave ou pelo nome da tabela.

import { ACABAMENTOS, PADROES } from '../../data/acabamentos.js';
import { CORES_SKIN } from '../../data/coresSkin.js';

const HEX = /^#?([0-9a-f]{6})$/i;

/** Nome digitado → chave de busca ("Branco Titânio" → "brancotitanio", "verde-água" → "verdeagua"). */
export function normalizarNome(texto) {
  return String(texto).normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase().replace(/[\s_-]+/g, '');
}

function indice(tabela) {
  const mapa = new Map();
  for (const [chave, def] of Object.entries(tabela)) {
    mapa.set(normalizarNome(chave), chave);
    mapa.set(normalizarNome(def.nome), chave);
  }
  return mapa;
}

const CORES = indice(CORES_SKIN);
const ACABS = indice(ACABAMENTOS);

/** Chave do acabamento pela chave ou pelo nome da tabela (null se não existe). */
export function resolverAcabamento(nome) {
  return nome == null ? null : ACABS.get(normalizarNome(nome)) ?? null;
}

/** Cor da paleta (chave ou nome) ou hex ("#RRGGBB" ou "RRGGBB") → "#RRGGBB" maiúsculo (null se não reconhece). */
export function resolverCor(valor) {
  if (valor == null) return null;
  const m = HEX.exec(String(valor).trim());
  if (m) return `#${m[1].toUpperCase()}`;
  const chave = CORES.get(normalizarNome(valor));
  return chave ? CORES_SKIN[chave].hex.toUpperCase() : null;
}

/** Componente sRGB (0–1) → linear. */
export function srgbParaLinear(c) {
  return c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4;
}

/** "#RRGGBB" → [r, g, b] linear. */
export function hexParaLinear(hex) {
  const m = HEX.exec(hex);
  if (!m) throw new Error(`cor inválida: ${hex}`);
  const n = parseInt(m[1], 16);
  return [(n >> 16) & 255, (n >> 8) & 255, n & 255].map((v) => srgbParaLinear(v / 255));
}

const limitar = (v, a, b) => Math.min(b, Math.max(a, v));

/**
 * Parâmetros do material de uma zona.
 * @param {{acabamento:string, cor:string, cor2?:string|null, desgaste?:number}} zona chave ou nome do acabamento; cor da
 *   paleta ou hex; segunda cor (madeira e carbono — sem ela, sai da primeira pelo `cor2Fator`); desgaste de 0 a 1
 * @returns {{acabamento:string, metalness:number, roughness:number, color:number[], color2:number[]|null,
 *   clearcoat:number, clearcoatRoughness:number, iridescence:number, iridescenceIOR:number,
 *   iridescenceThicknessRange:number[], anisotropy:number, padrao:string, padraoId:number, varAspereza:number,
 *   varCor:number, desgaste:number, gasto:{color:number[], metalness:number, roughness:number}, recursos:string[]}}
 *   cores em linear; `recursos` = os do material físico que o acabamento liga (verniz, iridescência, anisotropia)
 */
export function acabamentoParaMaterial({ acabamento, cor, cor2 = null, desgaste = 0 }) {
  const chave = resolverAcabamento(acabamento);
  if (!chave) throw new Error(`acabamento desconhecido: ${acabamento} (use ${Object.keys(ACABAMENTOS).join(', ')})`);
  const a = ACABAMENTOS[chave];
  const hex = resolverCor(cor);
  if (!hex) throw new Error(`cor desconhecida: ${cor}`);
  const color = hexParaLinear(hex);
  let color2 = null;
  if (a.duasCores) {
    const hex2 = resolverCor(cor2);
    if (cor2 != null && !hex2) throw new Error(`cor desconhecida: ${cor2}`);
    color2 = hex2 ? hexParaLinear(hex2) : color.map((c) => limitar(c * a.cor2Fator, 0, 1));
  }
  const clearcoat = a.verniz ?? 0;
  const iridescence = a.iridescencia ?? 0;
  const anisotropy = a.anisotropia ?? 0;
  const recursos = [];
  if (clearcoat > 0) recursos.push('verniz');
  if (iridescence > 0) recursos.push('iridescencia');
  if (anisotropy > 0) recursos.push('anisotropia');
  return {
    acabamento: chave,
    metalness: a.metal,
    roughness: a.aspereza,
    color,
    color2,
    clearcoat,
    clearcoatRoughness: a.asperezaVerniz ?? 0,
    iridescence,
    iridescenceIOR: a.iorIridescencia ?? 1.3,
    iridescenceThicknessRange: [...(a.filme ?? [250, 600])],
    anisotropy,
    padrao: a.padrao,
    padraoId: PADROES.indexOf(a.padrao),
    varAspereza: a.varAspereza,
    varCor: a.varCor,
    desgaste: limitar(Number(desgaste) || 0, 0, 1),
    gasto: { color: hexParaLinear(a.gasto.cor), metalness: a.gasto.metal, roughness: a.gasto.aspereza },
    recursos,
  };
}
