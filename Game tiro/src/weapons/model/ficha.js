// Ficha de fidelidade de uma arma realista (Fase 4.1a; desenho em docs/superpowers/specs/2026-09-26-armas-realistas-
// design.md, seção 3.1): tools/blender/refs/<id>.json no formato 2 — a variante real, as medidas oficiais com a fonte,
// as fotos do Commons, o contorno geral, os buracos, os contornos por peça e as linhas abertas em milímetros no
// referencial da foto (boca do cano — na faca, a ponta — em x = 0, eixo do cano — do cabo — em y = 0, +X para a boca,
// +Y para cima), os pontos nomeados e as cores medidas com a correção de exposição. Aqui: a validação (o Node confere
// antes de o Blender construir) e a conversão para a planta da 4.1 (formato 1: pontos em u relativos à boca — na faca,
// à ponta), que a bancada desenha na folha quadriculada e sobrepõe à arma, posta pela origem da ficha no jogo
// (`origemDaFicha`).
// Desde a 4.1c (plano da 4.1c, D2 e D3): as medidas-chave são as da classe da arma (src/data/armasReais.js); a foto do
// contorno é a marcada com `contorno: true`, de qualquer lado (a do lado esquerdo espelhada na régua, `espelhada: true`,
// para a boca ficar em +X) — sem marca, a do lado direito, como na ficha da AK —, e cada foto diz o que deu (`usos`):
// a primeira pessoa mostra o lado esquerdo da arma, e as peças de um lado só saem da foto daquele lado.
import { ARMAS_REAIS, CLASSES, classeDaArma } from '../../data/armasReais.js';

export const MM_POR_U = 25.4;
export const MEDIDAS_CHAVE = CLASSES.fuzil.medidas;
const HEX = /^#[0-9A-F]{6}$/;
const LADO = /^(direito|esquerdo)\b/;

/** A foto que dá o contorno: a marcada com `contorno: true` ou, sem marca, a do lado direito. */
export function fotoDoContorno(ficha) {
  const fotos = Array.isArray(ficha?.fotos) ? ficha.fotos : [];
  return fotos.find((f) => f.contorno === true) ?? fotos.find((f) => f.lado === 'direito') ?? null;
}

/** A classe pela qual a ficha é conferida: a pedida, a do registro ou, para arma fora dele, a de fuzil. */
function classeDaFicha(ficha, classe) {
  if (classe !== undefined) {
    if (!CLASSES[classe]) throw new Error(`classe desconhecida: ${classe} (tem: ${Object.keys(CLASSES).join(', ')})`);
    return classe;
  }
  return ARMAS_REAIS[ficha?.arma] ? classeDaArma(ficha.arma) : 'fuzil';
}

const anelValido = (anel) => Array.isArray(anel) && anel.length >= 2
  && anel.every((p) => Array.isArray(p) && p.length === 2 && p.every(Number.isFinite));

/**
 * Confere a ficha (formato 2).
 * @param {object} ficha
 * @param {string} [classe] fuzil, pistola ou faca (sem ela, a do registro)
 * @returns {string[]} os problemas (vazio = válida)
 */
export function problemasDaFicha(ficha, classe) {
  const medidas = CLASSES[classeDaFicha(ficha, classe)].medidas;
  const p = [];
  const exigir = (cond, msg) => {
    if (!cond) p.push(msg);
  };
  exigir(ficha?.formato === 2, 'formato precisa ser 2');
  exigir(typeof ficha?.arma === 'string' && /^[a-z0-9]+$/.test(ficha.arma), 'arma: o id em minúsculas');
  exigir(typeof ficha?.variante === 'string' && ficha.variante.length > 3, 'variante: o nome da variante real');
  exigir(ficha?.unidade === 'mm', 'unidade precisa ser "mm"');
  for (const m of medidas) {
    const d = ficha?.medidas?.[m];
    exigir(Boolean(d) && Number.isFinite(d.mm) && d.mm > 0, `medidas.${m}.mm: número positivo`);
    exigir(Boolean(d) && typeof d.fonte === 'string' && d.fonte.length > 3, `medidas.${m}.fonte: de onde veio o número`);
  }
  const fotos = Array.isArray(ficha?.fotos) ? ficha.fotos : [];
  exigir(fotos.filter((f) => f.contorno === true).length <= 1, 'fotos: uma foto só com contorno: true');
  exigir(fotoDoContorno(ficha) !== null, 'fotos: falta a foto do contorno (marcada com contorno: true, ou a do lado direito)');
  fotos.forEach((f, i) => {
    for (const k of ['arquivo', 'pagina', 'autor', 'licenca']) exigir(typeof f[k] === 'string' && f[k].length > 0, `fotos[${i}].${k}`);
    exigir(Number.isFinite(f.mmPorPixel) && f.mmPorPixel > 0, `fotos[${i}].mmPorPixel`);
    exigir(typeof f.lado === 'string' && LADO.test(f.lado), `fotos[${i}].lado: "direito" ou "esquerdo"`);
    exigir(f.espelhada === undefined || typeof f.espelhada === 'boolean', `fotos[${i}].espelhada: true ou false`);
    exigir(f.contorno === undefined || typeof f.contorno === 'boolean', `fotos[${i}].contorno: true ou false`);
    exigir(f.usos === undefined || (Array.isArray(f.usos) && f.usos.every((u) => typeof u === 'string' && u.length > 0)),
      `fotos[${i}].usos: lista do que a foto deu`);
  });
  exigir(anelValido(ficha?.contorno) && ficha.contorno.length >= 3, 'contorno: polígono com 3 pontos ou mais');
  (ficha?.buracos ?? []).forEach((b, i) => exigir(anelValido(b) && b.length >= 3, `buracos[${i}]: polígono`));
  for (const [nome, anel] of Object.entries(ficha?.pecas ?? {})) exigir(anelValido(anel) && anel.length >= 3, `pecas.${nome}: polígono`);
  for (const [nome, linha] of Object.entries(ficha?.linhas ?? {})) exigir(anelValido(linha), `linhas.${nome}: polilinha`);
  for (const [nome, c] of Object.entries(ficha?.cores ?? {})) {
    exigir(HEX.test(c?.fabrica ?? ''), `cores.${nome}.fabrica: "#RRGGBB" maiúsculo`);
    exigir(c?.foto === null || HEX.test(c?.foto?.srgb ?? ''), `cores.${nome}.foto: null ou {srgb, linear}`);
    exigir(typeof c?.correcao === 'string' && c.correcao.length > 3, `cores.${nome}.correcao: como a cor da foto virou a de fábrica`);
  }
  if (anelValido(ficha?.contorno) && ficha.contorno.length >= 3) {
    const xs = ficha.contorno.map((q) => q[0]);
    const x1 = Math.max(...xs);
    exigir(Math.abs(x1) <= 0.5, `contorno: a boca (x máximo, ${x1}) precisa estar em x = 0`);
    const alvo = ficha?.medidas?.comprimento?.mm;
    const comprimento = x1 - Math.min(...xs);
    exigir(!alvo || Math.abs(comprimento - alvo) / alvo <= 0.005,
      `contorno: comprimento ${comprimento.toFixed(1)} mm longe do oficial (${alvo} mm)`);
  }
  return p;
}

/** Lança com a lista de problemas; devolve a ficha quando está boa. */
export function validarFicha(ficha, classe) {
  const p = problemasDaFicha(ficha, classe);
  if (p.length) throw new Error(`ficha de ${ficha?.arma ?? '?'} inválida:\n  ${p.join('\n  ')}`);
  return ficha;
}

/**
 * A planta no formato 1 (a da 4.1: pontos em u relativos à boca) tirada da ficha.
 * @returns {{weapon:string, lengthU:number, points:number[][], holes:number[][][], source:object}}
 */
export function fichaParaPlanta(ficha) {
  const u = ([x, y]) => [x / MM_POR_U, y / MM_POR_U];
  const foto = fotoDoContorno(ficha);
  return {
    weapon: ficha.arma,
    lengthU: ficha.medidas.comprimento.mm / MM_POR_U,
    points: ficha.contorno.map(u),
    holes: (ficha.buracos ?? []).map((b) => b.map(u)),
    source: { file: foto.arquivo, page: foto.pagina, license: foto.licenca, artist: foto.autor },
  };
}

/**
 * Onde o (0, 0) da ficha (a boca do cano; na faca, a ponta) fica no referencial da arma no jogo, em u: a origem do jogo
 * é o `ORIGEM_MM` do script do Blender (o pino do gatilho nas armas de fogo, a frente da guarda na faca), que o relatório
 * do `construir` traz como `origemMM` — o ponto (x, y) da ficha vai para ((x, y) − origemMM) / 25,4.
 * @param {number[]} origemMM o `origemMM` do relatório
 * @returns {number[]} [x, y] em u
 */
export function origemDaFicha(origemMM, arma = '?') {
  if (!Array.isArray(origemMM) || origemMM.length !== 2 || !origemMM.every(Number.isFinite)) {
    throw new Error(`${arma}: o relatório sem a origemMM (construa a arma de novo no Blender)`);
  }
  // 0 − o (e não −o): sem o −0 da origem no eixo
  return [(0 - origemMM[0]) / MM_POR_U, (0 - origemMM[1]) / MM_POR_U];
}

/** A planta de um arquivo de tools/blender/refs/: a ficha (formato 2) vira planta; a planta da 4.1 passa como está. */
export function plantaDoArquivo(json) {
  return json?.formato === 2 ? fichaParaPlanta(validarFicha(json)) : json;
}
