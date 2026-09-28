// Leitor e validador da saída do Blender (Fase 4.1a; desenho em docs/superpowers/specs/2026-09-26-armas-realistas-
// design.md, seções 4.5, 4.6 e 9.1). Sem o three: o Node só precisa do bloco JSON do .glb (nomes, hierarquia,
// primitivas, materiais e acessores), do cabeçalho de cada .webp (lado e se é sem perdas) e do relatório que o Blender
// gravou. `validarSaida` confere tudo contra o registro das armas realistas (src/data/armasReais.js): os três níveis com
// as peças da arma, as zonas, os soquetes da categoria, os triângulos e as texturas do orçamento, as tangentes e as UV
// do nível de perto, o total dos arquivos e os números do relatório (medidas ±1 %, silhueta ≥ 98 % com tolerância); desde
// a 4.1b, a pega das luvas nas categorias com regra (saidaPega.mjs e src/characters/hands/pega.js).

import { readFileSync, statSync, existsSync } from 'node:fs';
import { join } from 'node:path';
import { ARMAS_REAIS, LODS_REAIS, armaComPega, medidasDaArma, orcamentoDaArma, soquetesDaArma } from '../../src/data/armasReais.js';
import { LUVAS } from '../../src/data/luvas.js';
import { lerPega } from '../../src/characters/hands/pega.js';
import { validarPega } from './saidaPega.mjs';

const GLTF = 0x46546c67;
const JSON_CHUNK = 0x4e4f534a;
const BIN_CHUNK = 0x004e4942;

/** Blocos de um .glb (versão 2). @returns {{json:object, bin:Buffer|null}} */
export function lerGlb(buf) {
  if (buf.length < 20 || buf.readUInt32LE(0) !== GLTF) throw new Error('não é um .glb (falta o "glTF" no começo)');
  if (buf.readUInt32LE(4) !== 2) throw new Error(`glTF versão ${buf.readUInt32LE(4)} (esperava 2)`);
  const total = Math.min(buf.readUInt32LE(8), buf.length);
  let pos = 12;
  let json = null;
  let bin = null;
  while (pos + 8 <= total) {
    const len = buf.readUInt32LE(pos);
    const tipo = buf.readUInt32LE(pos + 4);
    const dados = buf.subarray(pos + 8, pos + 8 + len);
    if (tipo === JSON_CHUNK) json = JSON.parse(dados.toString('utf8'));
    else if (tipo === BIN_CHUNK) bin = dados;
    pos += 8 + len;
  }
  if (!json) throw new Error('o .glb não tem o bloco JSON');
  return { json, bin };
}

/**
 * Resumo do glTF de uma arma: a raiz (tem de ser o id), os níveis (peças `<nivel>_<peca>` com as zonas, os triângulos,
 * a posição e os extras), se o nível tem tangentes e UV em todas as primitivas, as zonas usadas, os soquetes e as
 * animações.
 */
export function resumoGlb(json, id) {
  const cena = json.scenes?.[json.scene ?? 0];
  const raizes = (cena?.nodes ?? []).map((i) => json.nodes[i]);
  if (raizes.length !== 1) throw new Error(`o .glb precisa de uma raiz só (tem ${raizes.length})`);
  const raiz = raizes[0];
  if (raiz.name !== id) throw new Error(`a raiz do .glb é ${raiz.name}, esperava ${id}`);
  const filhos = (n) => (n.children ?? []).map((i) => json.nodes[i]);
  const materiais = json.materials ?? [];
  const contaPrimitiva = (p) => {
    const mode = p.mode ?? 4;
    if (mode !== 4) throw new Error(`primitiva que não é de triângulos (mode ${mode})`);
    const n = p.indices !== undefined ? json.accessors[p.indices].count : json.accessors[p.attributes.POSITION].count;
    return n / 3;
  };
  const lods = {};
  const zonasUsadas = new Set();
  // Na ordem do registro (perto, mundo, longe): o exportador do Blender grava os nós em ordem alfabética.
  for (const nome of LODS_REAIS) {
    const no = filhos(raiz).find((n) => n.name === nome);
    if (!no) continue;
    const lod = { pecas: {}, triangulos: 0, tangentes: true, uv: true };
    for (const peca of filhos(no)) {
      const prefixo = `${no.name}_`;
      if (!peca.name?.startsWith(prefixo)) throw new Error(`peça ${peca.name} fora do padrão ${prefixo}<peça>`);
      const nome = peca.name.slice(prefixo.length);
      const zonas = [];
      let triangulos = 0;
      const pilha = [peca];
      while (pilha.length) {
        const n = pilha.pop();
        if (n.mesh !== undefined) {
          for (const p of json.meshes[n.mesh].primitives) {
            triangulos += contaPrimitiva(p);
            const zona = materiais[p.material]?.name ?? null;
            if (zona && !zonas.includes(zona)) zonas.push(zona);
            if (zona) zonasUsadas.add(zona);
            if (p.attributes.TANGENT === undefined) lod.tangentes = false; // pela chave: o acessor 0 é válido
            if (p.attributes.TEXCOORD_0 === undefined) lod.uv = false;
          }
        }
        pilha.push(...filhos(n));
      }
      lod.pecas[nome] = { zonas, triangulos, posicao: peca.translation ?? [0, 0, 0], extras: peca.extras ?? null };
      lod.triangulos += triangulos;
    }
    lods[no.name] = lod;
  }
  const soquetes = {};
  const pasta = filhos(raiz).find((n) => n.name === 'soquetes');
  for (const s of pasta ? filhos(pasta) : []) {
    if (!s.name?.startsWith('soquete_')) throw new Error(`nó ${s.name} dentro de "soquetes" fora do padrão soquete_<nome>`);
    soquetes[s.name.slice('soquete_'.length)] = { posicao: s.translation ?? [0, 0, 0], rotacao: s.rotation ?? [0, 0, 0, 1] };
  }
  return {
    raiz: raiz.name,
    lods,
    zonas: [...zonasUsadas],
    soquetes,
    animacoes: (json.animations ?? []).map((a) => a.name),
    draco: (json.extensionsUsed ?? []).includes('KHR_draco_mesh_compression'),
  };
}

/** Lado e tipo de um .webp pelo cabeçalho (VP8, VP8L ou VP8X + o bloco da imagem). */
export function ladoWebp(buf) {
  if (buf.length < 20 || buf.toString('ascii', 0, 4) !== 'RIFF' || buf.toString('ascii', 8, 12) !== 'WEBP') {
    throw new Error('não é um .webp');
  }
  let pos = 12;
  let largura = 0;
  let altura = 0;
  let alfa = false;
  while (pos + 8 <= buf.length) {
    const tipo = buf.toString('ascii', pos, pos + 4);
    const len = buf.readUInt32LE(pos + 4);
    const d = pos + 8;
    if (tipo === 'VP8X') {
      alfa = (buf[d] & 0x10) !== 0;
      largura = buf.readUIntLE(d + 4, 3) + 1;
      altura = buf.readUIntLE(d + 7, 3) + 1;
    } else if (tipo === 'VP8L') {
      const b = buf.readUInt32LE(d + 1);
      return { largura: largura || (b & 0x3fff) + 1, altura: altura || ((b >>> 14) & 0x3fff) + 1, semPerdas: true, alfa: alfa || ((b >>> 28) & 1) === 1 };
    } else if (tipo === 'VP8 ') {
      return { largura: largura || buf.readUInt16LE(d + 6) & 0x3fff, altura: altura || buf.readUInt16LE(d + 8) & 0x3fff, semPerdas: false, alfa };
    }
    pos = d + len + (len % 2);
  }
  throw new Error('.webp sem o bloco da imagem');
}

/**
 * As medidas-chave do relatório contra as da classe da arma (Fase 4.1c; plano da 4.1c, D3): cada uma presente e a ±1 %
 * do alvo da ficha, e nenhuma fora da lista.
 * @returns {string[]}
 */
export function problemasDasMedidas(relatorio, medidas) {
  const p = [];
  const tem = relatorio?.medidas ?? {};
  for (const m of medidas) if (!tem[m]) p.push(`o relatório não tem a medida ${m}`);
  for (const [m, d] of Object.entries(tem)) {
    if (!medidas.includes(m)) p.push(`medida ${m} fora das da classe`);
    if (!(Math.abs(d.erro) <= 0.01)) p.push(`medida ${m}: ${d.mm} mm contra ${d.alvo} mm (erro ${d.erro >= 0 ? '+' : ''}${(d.erro * 100).toFixed(2)} %)`);
  }
  return p;
}

/** Arquivos que a construção grava para uma arma (pasta do registro). */
export function arquivosDaArma(id) {
  return {
    glb: `${id}.glb`,
    n: `${id}_n.webp`,
    m: `${id}_m.webp`,
    mundoN: `${id}_mundo_n.webp`,
    mundoM: `${id}_mundo_m.webp`,
    relatorio: `${id}.relatorio.json`,
  };
}

/**
 * Confere a saída de uma arma na raiz do projeto.
 * @returns {{problemas:string[], resumo:object|null, relatorio:object|null, bytes:number}}
 */
export function validarSaida(id, raiz) {
  const problemas = [];
  const a = ARMAS_REAIS[id];
  if (!a) return { problemas: [`${id} não está em src/data/armasReais.js`], resumo: null, relatorio: null, bytes: 0 };
  const orc = orcamentoDaArma(id);
  const pasta = join(raiz, a.pasta);
  const arqs = arquivosDaArma(id);
  const faltando = Object.values(arqs).filter((f) => !existsSync(join(pasta, f)));
  if (faltando.length) return { problemas: [`faltam em ${a.pasta}: ${faltando.join(', ')}`], resumo: null, relatorio: null, bytes: 0 };
  let bytes = 0;
  for (const f of Object.values(arqs)) bytes += statSync(join(pasta, f)).size;
  if (bytes > orc.arquivosMB * 1024 * 1024) problemas.push(`arquivos: ${(bytes / 1048576).toFixed(2)} MB (orçamento ${orc.arquivosMB} MB)`);

  const json = lerGlb(readFileSync(join(pasta, arqs.glb))).json;
  const resumo = resumoGlb(json, id);
  const pecas = ['base', ...a.pecas];
  for (const lod of LODS_REAIS) {
    const l = resumo.lods[lod];
    if (!l) {
      problemas.push(`falta o nível ${lod}`);
      continue;
    }
    const nomes = Object.keys(l.pecas);
    for (const p of pecas) if (!nomes.includes(p)) problemas.push(`${lod}: falta a peça ${p}`);
    for (const p of nomes) if (!pecas.includes(p)) problemas.push(`${lod}: peça a mais ${p}`);
    if (l.triangulos > orc.triangulos[lod]) problemas.push(`${lod}: ${l.triangulos} triângulos (orçamento ${orc.triangulos[lod]})`);
    if (!l.uv) problemas.push(`${lod}: primitiva sem UV`);
  }
  if (resumo.lods.perto && !resumo.lods.perto.tangentes) problemas.push('perto: primitiva sem tangentes (o relevo assado precisa delas)');
  if (!resumo.draco) problemas.push('o .glb sem a compressão Draco (KHR_draco_mesh_compression; desenho, seção 4.5)');
  for (const z of resumo.zonas) if (!a.zonas.includes(z)) problemas.push(`zona desconhecida no .glb: ${z}`);
  for (const z of a.zonas) if (!resumo.zonas.includes(z)) problemas.push(`falta a zona ${z}`);
  for (const s of soquetesDaArma(id)) if (!resumo.soquetes[s]) problemas.push(`falta o soquete ${s}`);

  const texturas = { [arqs.n]: orc.textura, [arqs.m]: orc.textura, [arqs.mundoN]: orc.texturaMundo, [arqs.mundoM]: orc.texturaMundo };
  for (const [arq, lado] of Object.entries(texturas)) {
    const w = ladoWebp(readFileSync(join(pasta, arq)));
    if (w.largura !== lado || w.altura !== lado) problemas.push(`${arq}: ${w.largura}×${w.altura} (esperava ${lado}×${lado})`);
    if (!w.semPerdas) problemas.push(`${arq}: WebP com perdas (os canais empacotados precisam do sem perdas)`);
    if (arq.endsWith('_m.webp') && !w.alfa) problemas.push(`${arq}: sem o canal alfa (variação de cor)`);
  }

  const relatorio = JSON.parse(readFileSync(join(pasta, arqs.relatorio), 'utf8'));
  if (relatorio.arma !== id) problemas.push(`relatório de ${relatorio.arma}, esperava ${id}`);
  if (!relatorio.aprovado) problemas.push(`o Blender reprovou: ${(relatorio.problemas ?? []).join('; ')}`);
  problemas.push(...problemasDasMedidas(relatorio, medidasDaArma(id)));
  if (!(relatorio.silhueta?.iouTolerancia >= 0.98)) problemas.push(`silhueta: ${relatorio.silhueta?.iouTolerancia} com tolerância (mínimo 0,98)`);
  for (const lod of LODS_REAIS) {
    const t = relatorio.lods?.[lod]?.triangulos;
    if (resumo.lods[lod] && t !== resumo.lods[lod].triangulos) problemas.push(`${lod}: o relatório diz ${t} triângulos e o .glb tem ${resumo.lods[lod].triangulos}`);
  }
  // A pega das luvas (Fase 4.1b): nas armas com a regra (armaComPega), os nós e o clipe no .glb, a seção do relatório e
  // a marca igual à do luvas.glb (se as luvas já foram construídas).
  if (armaComPega(id)) {
    try {
      const glbLuvas = join(raiz, LUVAS.pasta, 'luvas.glb');
      const marcaLuvas = existsSync(glbLuvas)
        ? lerGlb(readFileSync(glbLuvas)).json.nodes?.find((n) => n.name === 'luvas')?.extras?.marca ?? null
        : null;
      problemas.push(...validarPega(relatorio, lerPega(json), marcaLuvas));
    } catch (e) {
      problemas.push(e.message);
    }
  }
  return { problemas, resumo, relatorio, bytes };
}
