// Ficha de fidelidade de uma arma realista (Fase 4.1a; desenho em docs/superpowers/specs/2026-09-26-armas-realistas-
// design.md, seção 3.1): tools/blender/refs/<id>.json no formato 2 — a variante real, as medidas oficiais com a fonte,
// as fotos do Commons (a do lado direito é obrigatória: é o lado do viewmodel), o contorno geral, os buracos, os
// contornos por peça e as linhas abertas em milímetros no referencial da foto (boca do cano em x = 0, eixo do cano em
// y = 0, +X para a boca, +Y para cima), os pontos nomeados e as cores medidas com a correção de exposição. Aqui: a
// validação (o Node confere antes de o Blender construir) e a conversão para a planta da 4.1 (formato 1: pontos em u
// relativos à boca), que a bancada desenha na folha quadriculada e sobrepõe à arma.

export const MM_POR_U = 25.4;
export const MEDIDAS_CHAVE = Object.freeze(['comprimento', 'cano', 'raioDeMira', 'alturaSemCarregador', 'alturaComCarregador']);
const HEX = /^#[0-9A-F]{6}$/;

const anelValido = (anel) => Array.isArray(anel) && anel.length >= 2
  && anel.every((p) => Array.isArray(p) && p.length === 2 && p.every(Number.isFinite));

/**
 * Confere a ficha (formato 2).
 * @param {object} ficha
 * @returns {string[]} os problemas (vazio = válida)
 */
export function problemasDaFicha(ficha) {
  const p = [];
  const exigir = (cond, msg) => {
    if (!cond) p.push(msg);
  };
  exigir(ficha?.formato === 2, 'formato precisa ser 2');
  exigir(typeof ficha?.arma === 'string' && /^[a-z0-9]+$/.test(ficha.arma), 'arma: o id em minúsculas');
  exigir(typeof ficha?.variante === 'string' && ficha.variante.length > 3, 'variante: o nome da variante real');
  exigir(ficha?.unidade === 'mm', 'unidade precisa ser "mm"');
  for (const m of MEDIDAS_CHAVE) {
    const d = ficha?.medidas?.[m];
    exigir(Boolean(d) && Number.isFinite(d.mm) && d.mm > 0, `medidas.${m}.mm: número positivo`);
    exigir(Boolean(d) && typeof d.fonte === 'string' && d.fonte.length > 3, `medidas.${m}.fonte: de onde veio o número`);
  }
  const fotos = Array.isArray(ficha?.fotos) ? ficha.fotos : [];
  exigir(fotos.some((f) => f.lado === 'direito'), 'fotos: a do lado direito é obrigatória');
  fotos.forEach((f, i) => {
    for (const k of ['arquivo', 'pagina', 'autor', 'licenca']) exigir(typeof f[k] === 'string' && f[k].length > 0, `fotos[${i}].${k}`);
    exigir(Number.isFinite(f.mmPorPixel) && f.mmPorPixel > 0, `fotos[${i}].mmPorPixel`);
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
export function validarFicha(ficha) {
  const p = problemasDaFicha(ficha);
  if (p.length) throw new Error(`ficha de ${ficha?.arma ?? '?'} inválida:\n  ${p.join('\n  ')}`);
  return ficha;
}

/**
 * A planta no formato 1 (a da 4.1: pontos em u relativos à boca) tirada da ficha.
 * @returns {{weapon:string, lengthU:number, points:number[][], holes:number[][][], source:object}}
 */
export function fichaParaPlanta(ficha) {
  const u = ([x, y]) => [x / MM_POR_U, y / MM_POR_U];
  const direita = ficha.fotos.find((f) => f.lado === 'direito');
  return {
    weapon: ficha.arma,
    lengthU: ficha.medidas.comprimento.mm / MM_POR_U,
    points: ficha.contorno.map(u),
    holes: (ficha.buracos ?? []).map((b) => b.map(u)),
    source: { file: direita.arquivo, page: direita.pagina, license: direita.licenca, artist: direita.autor },
  };
}

/** A planta de um arquivo de tools/blender/refs/: a ficha (formato 2) vira planta; a planta da 4.1 passa como está. */
export function plantaDoArquivo(json) {
  return json?.formato === 2 ? fichaParaPlanta(validarFicha(json)) : json;
}
