// Leitor e validador da saída das luvas (Fase 4.1b; desenho em docs/superpowers/specs/2026-09-26-4.1b-luvas-e-
// empunhadura-design.md, seção 7; plano, Tarefa 6). O irmão do saida.mjs das armas, com os mesmos leitores do .glb e
// do .webp. O luvas.glb tem a raiz `luvas` (a marca do rig de cada braço nos extras, D4), as duas armaduras (`rig_d`,
// `rig_e`) e as duas malhas com skin (`luva_d`, `luva_e`), uma primitiva por zona, com o atributo `_VERTICE` (o índice
// do vértice no Blender: as costuras de UV duplicam vértices e o Draco reordena, e o modelo das dobras e as amarras das
// peças são indexados por ele) e as correções das dobras nos extras (o JSON de maos_correcoes.Modelo.parametros).
// `validarSaidaLuvas` confere tudo contra o registro (src/data/luvas.js): os 20 ossos de cada lado, as zonas, os
// atributos, os triângulos dos dois braços, as texturas, o total dos arquivos, o relatório aprovado, os triângulos e a
// marca do relatório iguais aos do .glb.

import { readFileSync, statSync, existsSync } from 'node:fs';
import { join } from 'node:path';
import { LUVAS, ZONAS_DAS_LUVAS, ossosDoLado } from '../../src/data/luvas.js';
import { ladoWebp, lerGlb } from './saida.mjs';

export const ARQUIVOS_DAS_LUVAS = Object.freeze({
  glb: 'luvas.glb', n: 'luvas_n.webp', m: 'luvas_m.webp', relatorio: 'luvas.relatorio.json',
});
const ATRIBUTOS = Object.freeze({ TEXCOORD_0: 'UV', TANGENT: 'tangentes', WEIGHTS_0: 'os pesos', _VERTICE: 'o _VERTICE' });

/**
 * Resumo do glTF das luvas: a raiz, a marca, o Draco e, por malha (`luva_d`, `luva_e`), os triângulos, as zonas, os
 * nomes dos ossos do skin, se todas as primitivas têm UV, tangentes, pesos e o `_VERTICE`, e as correções dos extras.
 */
export function resumoLuvasGlb(json) {
  const cena = json.scenes?.[json.scene ?? 0];
  const raizes = (cena?.nodes ?? []).map((i) => json.nodes[i]);
  if (raizes.length !== 1) throw new Error(`o .glb precisa de uma raiz só (tem ${raizes.length})`);
  const raiz = raizes[0];
  if (raiz.name !== 'luvas') throw new Error(`a raiz do .glb é ${raiz.name}, esperava luvas`);
  const materiais = json.materials ?? [];
  const malhas = {};
  const pilha = [raiz];
  while (pilha.length) {
    const n = pilha.pop();
    pilha.push(...(n.children ?? []).map((i) => json.nodes[i]));
    if (n.mesh === undefined) continue;
    const m = { triangulos: 0, zonas: [], ossos: [], uv: true, tangentes: true, pesos: true, vertice: true, correcoes: null };
    for (const p of json.meshes[n.mesh].primitives) {
      if ((p.mode ?? 4) !== 4) throw new Error(`${n.name}: primitiva que não é de triângulos (mode ${p.mode})`);
      const conta = p.indices !== undefined ? json.accessors[p.indices].count : json.accessors[p.attributes.POSITION].count;
      m.triangulos += conta / 3;
      const zona = materiais[p.material]?.name ?? null;
      if (zona && !m.zonas.includes(zona)) m.zonas.push(zona);
      // pela chave: o acessor 0 é um índice válido
      const tem = (nome) => p.attributes[nome] !== undefined;
      if (!tem('TEXCOORD_0')) m.uv = false;
      if (!tem('TANGENT')) m.tangentes = false;
      if (!tem('JOINTS_0') || !tem('WEIGHTS_0')) m.pesos = false;
      if (!tem('_VERTICE')) m.vertice = false;
    }
    if (n.skin !== undefined) m.ossos = json.skins[n.skin].joints.map((i) => json.nodes[i].name);
    if (typeof n.extras?.correcoes === 'string') {
      const c = JSON.parse(n.extras.correcoes);
      m.correcoes = { juntas: c.juntas?.length ?? 0, pecas: Boolean(c.pecas) };
    }
    malhas[n.name] = m;
  }
  const ordenadas = {};
  for (const nome of Object.keys(malhas).sort()) ordenadas[nome] = malhas[nome];
  return {
    raiz: raiz.name,
    malhas: ordenadas,
    marca: raiz.extras?.marca ?? null,
    draco: (json.extensionsUsed ?? []).includes('KHR_draco_mesh_compression'),
  };
}

/**
 * Confere a saída das luvas na raiz do projeto.
 * @returns {{problemas:string[], resumo:object|null, relatorio:object|null, bytes:number}}
 */
export function validarSaidaLuvas(raiz) {
  const problemas = [];
  const orc = LUVAS.orcamento;
  const pasta = join(raiz, LUVAS.pasta);
  const faltando = Object.values(ARQUIVOS_DAS_LUVAS).filter((f) => !existsSync(join(pasta, f)));
  if (faltando.length) {
    return { problemas: [`faltam em ${LUVAS.pasta}: ${faltando.join(', ')}`], resumo: null, relatorio: null, bytes: 0 };
  }
  let bytes = 0;
  for (const f of Object.values(ARQUIVOS_DAS_LUVAS)) bytes += statSync(join(pasta, f)).size;
  if (bytes > orc.arquivosMB * 1024 * 1024) {
    problemas.push(`arquivos: ${(bytes / 1048576).toFixed(2)} MB (orçamento ${orc.arquivosMB} MB)`);
  }

  const resumo = resumoLuvasGlb(lerGlb(readFileSync(join(pasta, ARQUIVOS_DAS_LUVAS.glb))).json);
  let total = 0;
  for (const lado of ['d', 'e']) {
    const nome = `luva_${lado}`;
    const m = resumo.malhas[nome];
    if (!m) {
      problemas.push(`falta a malha ${nome}`);
      continue;
    }
    total += m.triangulos;
    const ossos = ossosDoLado(lado);
    for (const o of ossos) if (!m.ossos.includes(o)) problemas.push(`${nome}: falta o osso ${o}`);
    for (const o of m.ossos) if (!ossos.includes(o)) problemas.push(`${nome}: osso a mais ${o}`);
    for (const z of ZONAS_DAS_LUVAS) if (!m.zonas.includes(z)) problemas.push(`${nome}: falta a zona ${z}`);
    for (const z of m.zonas) if (!ZONAS_DAS_LUVAS.includes(z)) problemas.push(`${nome}: zona desconhecida ${z}`);
    const tem = { TEXCOORD_0: m.uv, TANGENT: m.tangentes, WEIGHTS_0: m.pesos, _VERTICE: m.vertice };
    for (const [atributo, descricao] of Object.entries(ATRIBUTOS)) {
      if (!tem[atributo]) problemas.push(`${nome}: primitiva sem ${descricao}`);
    }
    if (!m.correcoes || !m.correcoes.juntas || !m.correcoes.pecas) {
      problemas.push(`${nome}: sem as correções das dobras nos extras (as juntas e as amarras das peças)`);
    }
  }
  if (total > orc.triangulos) problemas.push(`${total} triângulos nos dois braços (orçamento ${orc.triangulos})`);
  if (!resumo.draco) problemas.push('o .glb sem a compressão Draco (KHR_draco_mesh_compression)');

  for (const arq of [ARQUIVOS_DAS_LUVAS.n, ARQUIVOS_DAS_LUVAS.m]) {
    const w = ladoWebp(readFileSync(join(pasta, arq)));
    if (w.largura !== orc.textura || w.altura !== orc.textura) {
      problemas.push(`${arq}: ${w.largura}×${w.altura} (esperava ${orc.textura}×${orc.textura})`);
    }
    if (!w.semPerdas) problemas.push(`${arq}: WebP com perdas (os canais empacotados precisam do sem perdas)`);
    if (arq === ARQUIVOS_DAS_LUVAS.m && !w.alfa) problemas.push(`${arq}: sem o canal alfa (variação de cor)`);
  }

  const relatorio = JSON.parse(readFileSync(join(pasta, ARQUIVOS_DAS_LUVAS.relatorio), 'utf8'));
  if (!relatorio.aprovado) problemas.push(`o Blender reprovou: ${(relatorio.problemas ?? []).join('; ')}`);
  for (const lado of ['d', 'e']) {
    const m = resumo.malhas[`luva_${lado}`];
    const t = relatorio.triangulos?.luva;
    if (m && t !== m.triangulos) problemas.push(`luva_${lado}: o relatório diz ${t} triângulos e o .glb tem ${m.triangulos}`);
    if (!resumo.marca?.[lado]) {
      problemas.push(`o .glb sem a marca do rig ${lado} (extras da raiz)`);
    } else if (resumo.marca[lado] !== relatorio.marca?.[lado]) {
      problemas.push(`a marca do rig ${lado} do .glb (${resumo.marca[lado].slice(0, 12)}…) não é a do relatório `
        + `(${String(relatorio.marca?.[lado]).slice(0, 12)}…)`);
    }
  }
  return { problemas, resumo, relatorio, bytes };
}
