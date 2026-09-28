// Ficha das luvas (Fase 4.1b; desenho em docs/superpowers/specs/2026-09-26-4.1b-luvas-e-empunhadura-design.md, seção 2):
// tools/blender/refs/luvas.json — a mão média (ANSUR II), os ossos entre as juntas (Buryanov & Kotiuk 2010), as larguras
// e circunferências nas juntas e as pontas dos dedos ao pulso (Greiner 1991, médias dos homens, levadas à mão da ficha
// pelas escalas), o antebraço (medianas do ANSUR II), os limites das juntas (AAOS), a pose de repouso, a luva e as
// deduções, cada uma com o porquê. O Node confere antes de o Blender construir; o lançador passa a ficha validada ao
// principal.py, que não inventa medida. O antebraço de massinha do jogo (antebracoMassa.js) lê o mesmo perfil.

const F = Object.freeze;

export const DEDOS = F(['polegar', 'indicador', 'medio', 'anelar', 'minimo']);
export const OSSOS_DO_DEDO = F({
  polegar: F(['metacarpo', 'proximal', 'distal', 'polpa']),
  indicador: F(['metacarpo', 'proximal', 'media', 'distal', 'polpa']),
  medio: F(['metacarpo', 'proximal', 'media', 'distal', 'polpa']),
  anelar: F(['metacarpo', 'proximal', 'media', 'distal', 'polpa']),
  minimo: F(['metacarpo', 'proximal', 'media', 'distal', 'polpa']),
});
const FONTES = F(['ansur2', 'ansur2Explorador', 'buryanov', 'greiner', 'aaos', 'cooney', 'referencias']);
const MEDIDAS_DA_MAO = F(['comprimento', 'largura', 'palma', 'circunferencia', 'pulso']);
const MEDIDAS_DA_LUVA = F(['tecido', 'couro', 'almofada', 'protetor', 'tira', 'punho', 'folgaPunho']);
const REPOUSO = F(['mcp', 'pip', 'dip', 'abertura', 'polegarAbducao', 'polegarMcp', 'polegarIp']);
const DOBRAS = F(['polegarIndicador', 'indicadorMedio', 'medioAnelar', 'anelarMinimo']);

const positivo = (v) => Number.isFinite(v) && v > 0;
const faixa = (v) => Array.isArray(v) && v.length === 2 && v.every(Number.isFinite) && v[0] < v[1];

/**
 * Confere a ficha das luvas (formato 1).
 * @param {object} f
 * @returns {string[]} os problemas (vazio = válida), cada um começando pelo campo
 */
export function problemasDaFichaLuvas(f) {
  const p = [];
  const exigir = (cond, msg) => {
    if (!cond) p.push(msg);
  };
  exigir(f?.formato === 1, 'formato: precisa ser 1');
  exigir(f?.id === 'luvas', 'id: precisa ser "luvas"');
  for (const nome of FONTES) {
    const fo = f?.fontes?.[nome];
    exigir(typeof fo?.titulo === 'string' && fo.titulo.length > 10 && /^https:\/\//.test(fo?.url ?? ''),
      `fontes.${nome}: título e endereço https`);
  }
  const fonteValida = (grupo) => exigir(FONTES.includes(f?.[grupo]?.fonte) && Boolean(f?.fontes?.[f[grupo].fonte]),
    `${grupo}.fonte: uma das fontes da ficha`);
  fonteValida('mao');
  for (const m of MEDIDAS_DA_MAO) exigir(positivo(f?.mao?.[m]?.mm), `mao.${m}.mm: número positivo`);
  fonteValida('ossos');
  for (const d of DEDOS) {
    if (!f?.ossos?.[d]) {
      p.push(`ossos.${d}: falta o dedo`);
      continue;
    }
    for (const o of OSSOS_DO_DEDO[d]) exigir(positivo(f.ossos[d][o]), `ossos.${d}.${o}: número positivo`);
  }
  fonteValida('juntas');
  const j = f?.juntas;
  exigir(positivo(j?.larguraDaMao), 'juntas.larguraDaMao: número positivo');
  for (const d of DEDOS) exigir(positivo(j?.pontaAoPulso?.[d]), `juntas.pontaAoPulso.${d}: número positivo`);
  for (const k of DOBRAS) exigir(positivo(j?.dobras?.[k]), `juntas.dobras.${k}: número positivo`);
  exigir(positivo(j?.cotoveloAoPulso), 'juntas.cotoveloAoPulso: número positivo');
  exigir(positivo(j?.pulso?.largura) && positivo(j?.pulso?.circunferencia), 'juntas.pulso: largura e circunferência');
  exigir(positivo(j?.polegar?.ip?.largura) && positivo(j?.polegar?.ip?.circunferencia), 'juntas.polegar.ip: largura e circunferência');
  for (const d of DEDOS.slice(1)) {
    exigir(positivo(j?.[d]?.pip?.largura) && positivo(j?.[d]?.pip?.circunferencia), `juntas.${d}.pip: largura e circunferência`);
    exigir(positivo(j?.[d]?.dip?.circunferencia), `juntas.${d}.dip.circunferencia: número positivo`);
    exigir(j?.[d]?.dip?.largura === undefined || positivo(j[d].dip.largura), `juntas.${d}.dip.largura: número positivo quando houver`);
  }
  fonteValida('antebraco');
  exigir(positivo(f?.antebraco?.circunferenciaFlexionado?.mm), 'antebraco.circunferenciaFlexionado.mm: número positivo');
  exigir(positivo(f?.antebraco?.pulso?.mm), 'antebraco.pulso.mm: número positivo');
  fonteValida('limites');
  const l = f?.limites;
  for (const k of ['mcp', 'pip', 'dip', 'abertura']) exigir(faixa(l?.[k]), `limites.${k}: [mínimo, máximo]`);
  for (const k of ['cmcAbducao', 'cmcFlexao', 'mcp', 'ip']) exigir(faixa(l?.polegar?.[k]), `limites.polegar.${k}: [mínimo, máximo]`);
  for (const k of ['flexao', 'extensao', 'radial', 'ulnar']) exigir(positivo(l?.pulso?.[k]), `limites.pulso.${k}: graus positivos`);
  for (const k of ['pronacao', 'supinacao']) exigir(positivo(l?.antebraco?.[k]), `limites.antebraco.${k}: graus positivos`);
  fonteValida('rotacaoDoPolegar');
  exigir(faixa(f?.rotacaoDoPolegar?.cmc), 'rotacaoDoPolegar.cmc: [mínimo, máximo]');
  exigir(typeof f?.rotacaoDoPolegar?.nota === 'string' && f.rotacaoDoPolegar.nota.length > 20,
    'rotacaoDoPolegar.nota: de onde veio e para que serve');
  for (const k of REPOUSO) exigir(Number.isFinite(f?.repouso?.[k]), `repouso.${k}: número`);
  for (const k of MEDIDAS_DA_LUVA) exigir(positivo(f?.luva?.[k]), `luva.${k}: número positivo`);
  exigir(typeof f?.luva?.nota === 'string' && f.luva.nota.length > 20, 'luva.nota: de onde vieram as decisões');
  for (const [nome, d] of Object.entries(f?.deducoes ?? {})) {
    exigir(typeof d?.porque === 'string' && d.porque.length > 20, `deducoes.${nome}.porque: como o número foi deduzido`);
  }
  for (const nome of ['polegar', 'espessuraDaMao', 'pulso', 'folgaEntreDedos', 'leque', 'arco', 'convergencia', 'antebraco',
    'perfilDoAntebraco']) {
    exigir(Boolean(f?.deducoes?.[nome]), `deducoes.${nome}: falta`);
  }
  const d = f?.deducoes;
  exigir(positivo(d?.pulso?.espessura) && positivo(d?.pulso?.raio), 'deducoes.pulso.raio: espessura e raio positivos');
  exigir(positivo(d?.espessuraDaMao?.mm) && positivo(d?.espessuraDaMao?.raio), 'deducoes.espessuraDaMao.raio: espessura e raio positivos');
  exigir(positivo(d?.perfilDoAntebraco?.circunferenciaNoCotovelo),
    'deducoes.perfilDoAntebraco.circunferenciaNoCotovelo: número positivo');
  const expoente = d?.perfilDoAntebraco?.expoente;
  exigir(Number.isFinite(expoente) && expoente >= 1 && expoente <= 3, 'deducoes.perfilDoAntebraco.expoente: entre 1 e 3');
  return p;
}

function congelar(o) {
  if (o && typeof o === 'object') {
    for (const v of Object.values(o)) congelar(v);
    Object.freeze(o);
  }
  return o;
}

/** A ficha conferida e congelada (uma cópia); lança com todos os problemas. */
export function validarFichaLuvas(f) {
  const p = problemasDaFichaLuvas(f);
  if (p.length) throw new Error(`ficha das luvas: ${p.join('; ')}`);
  return congelar(structuredClone(f));
}

/** Perímetro do retângulo arredondado (o modelo de seção da ficha para o pulso, a mão nos nós e o antebraço). */
export function perimetroRetanguloArredondado(largura, altura, raio) {
  return 2 * (largura - 2 * raio) + 2 * (altura - 2 * raio) + 2 * Math.PI * raio;
}

/**
 * Escalas das médias dos homens de Greiner para a mão da ficha: os comprimentos pela ponta do médio ao pulso (o mesmo
 * referencial do comprimento da mão), as larguras e circunferências pela largura da mão.
 */
export function escalasDaFicha(f) {
  return {
    comprimento: f.mao.comprimento.mm / f.juntas.pontaAoPulso.medio,
    largura: f.mao.largura.mm / f.juntas.larguraDaMao,
  };
}
