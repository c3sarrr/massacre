// O antebraço de massinha das luvas e a braçadeira do time (Fase 4.1b; desenho em docs/superpowers/specs/2026-09-26-
// 4.1b-luvas-e-empunhadura-design.md, seção 5; plano, Tarefa 9, Passo 4): a massa do boneco que entra no punho da luva
// e passa do cotovelo, fora da tela. A seção é a mesma que o Blender usou para vestir o punho (tools/blender/armas/
// maos.py, `secao_antebraco`): o retângulo arredondado do pulso da ficha (largura em Z, espessura em Y — o referencial
// das luvas no glTF: +X pontas, +Y costas) na escala da circunferência, que cresce do pulso ao cotovelo como t^expoente
// (`perfilDoAntebraco`). A árvore SDF (a forma `tronco`, src/clay/sdf/tronco.js, com a irregularidade de massa moldada)
// sai em u no referencial do braço (o pulso na origem, o cotovelo em −X) e vira malha uma vez por sessão no SdfMesher
// (Workers e cache); a seção é simétrica em Z, então uma malha serve aos dois braços. O skin tem dois ossos
// (`antebraco` e `torcao`), na rampa da torção de BRACO_DE_MASSA; a braçadeira é uma faixa de massa em volta do
// antebraço, com os mesmos pesos, que torce junto.
// Puro nas contas (os testes do Node conferem com o relatório das luvas e com a malha delas); construirAntebraco usa o
// SdfMesher.

import * as THREE from 'three';
import { BRACO_DE_MASSA } from '../../data/luvas.js';
import { escalasDaFicha, perimetroRetanguloArredondado } from './fichaLuvas.js';

const MM_POR_U = 25.4;
const B = BRACO_DE_MASSA;

/** Os dois ossos do skin do antebraço (sem o sufixo do lado), na ordem dos índices do skin. */
export const OSSOS_DO_ANTEBRACO = Object.freeze(['antebraco', 'torcao']);

/** Comprimento do antebraço (mm): do cotovelo ao pulso de Greiner, na escala do comprimento da mão da ficha. */
export function comprimentoDoAntebraco(f) {
  return f.juntas.cotoveloAoPulso * escalasDaFicha(f).comprimento;
}

/** Circunferência (mm) do antebraço a x ≤ 0 do pulso (mm): a do pulso crescendo até a do cotovelo como t^expoente. */
export function circunferenciaDoAntebraco(f, x) {
  const perfil = f.deducoes.perfilDoAntebraco;
  const pulso = f.mao.pulso.mm;
  const t = Math.min(1, Math.max(0, -x / comprimentoDoAntebraco(f)));
  return pulso + (perfil.circunferenciaNoCotovelo - pulso) * t ** perfil.expoente;
}

/** Seção (mm) do antebraço a x ≤ 0: o retângulo arredondado do pulso na escala da circunferência. */
export function secaoDoAntebraco(f, x) {
  const largura = f.juntas.pulso.largura * escalasDaFicha(f).largura;
  const { espessura, raio } = f.deducoes.pulso;
  const s = circunferenciaDoAntebraco(f, x) / perimetroRetanguloArredondado(largura, espessura, raio);
  return { largura: largura * s, espessura: espessura * s, raio: raio * s };
}

/** As seções [x, largura, espessura, raio] em u, com `ganho` mm a mais em cada lado (negativo encolhe). */
function secoesEmU(f, xs, ganho = 0) {
  return xs.map((x) => {
    const s = secaoDoAntebraco(f, x);
    return [x, s.largura + 2 * ganho, s.espessura + 2 * ganho, Math.max(0, s.raio + ganho)].map((v) => v / MM_POR_U);
  });
}

/** Onde o tronco começa e acaba (mm): da ponta dentro do punho até depois do cotovelo. */
export function extensaoDoAntebraco(f) {
  return { pulso: -B.dentroDoPunhoMM, cotovelo: -(comprimentoDoAntebraco(f) + B.alemDoCotoveloMM) };
}

/** A árvore SDF do antebraço (u, referencial do braço): o tronco das seções com a irregularidade de massa. */
export function arvoreDoAntebraco(f) {
  const L = comprimentoDoAntebraco(f);
  const { pulso, cotovelo } = extensaoDoAntebraco(f);
  const n = B.secoes;
  // do cotovelo (t = 1, a seção para de crescer) até a ponta do pulso, e a ponta depois do cotovelo com a do cotovelo
  const xs = [cotovelo];
  for (let k = n - 1; k >= 0; k--) xs.push(pulso + ((-L - pulso) * k) / (n - 1));
  const secoes = secoesEmU(f, xs);
  const menor = Math.min(...secoes.map((s) => Math.min(s[1], s[2]) / 2));
  const I = B.irregularidade;
  return {
    type: 'displace', amp: I.ampMM / MM_POR_U, freq: I.freqPorU, octaves: I.oitavas, seed: 'antebraco-de-massinha',
    child: { type: 'tronco', mat: 0, round: Math.min(menor, 10 / MM_POR_U), secoes },
  };
}

/** A árvore SDF da braçadeira: a faixa por fora do antebraço menos o antebraço encolhido (um anel, sem massa dentro). */
export function arvoreDaBracadeira(f) {
  const b = B.bracadeira;
  const x0 = -(b.doPulsoMM + b.larguraMM / 2);
  const x1 = -(b.doPulsoMM - b.larguraMM / 2);
  const fora = Array.from({ length: 5 }, (_, k) => x0 + ((x1 - x0) * k) / 4);
  const dentro = [x0 - 4, (x0 + x1) / 2, x1 + 4];
  const I = b.irregularidade;
  return {
    type: 'displace', amp: I.ampMM / MM_POR_U, freq: I.freqPorU, octaves: I.oitavas, seed: 'bracadeira-de-massinha',
    child: {
      type: 'subtract',
      a: { type: 'tronco', mat: 0, round: b.arredondaMM / MM_POR_U, secoes: secoesEmU(f, fora, b.espessuraMM) },
      b: { type: 'tronco', mat: 0, secoes: secoesEmU(f, dentro, -b.dentroMM) },
    },
  };
}

/**
 * Pesos dos dois ossos por vértice (posições em u, referencial do braço): a `torcao` sobe em rampa linear do cotovelo
 * (0) à boca do punho (1), como o punho da luva, que é todo dela.
 * @returns {{skinIndex:Uint16Array, skinWeight:Float32Array}} 4 por vértice (índices 0 = antebraco, 1 = torcao)
 */
export function pesosDoAntebraco(posicoes, f) {
  const L = comprimentoDoAntebraco(f);
  const boca = f.luva.punho;
  const n = posicoes.length / 3;
  const skinIndex = new Uint16Array(n * 4);
  const skinWeight = new Float32Array(n * 4);
  for (let v = 0; v < n; v++) {
    const x = posicoes[v * 3] * MM_POR_U;
    const w = Math.min(1, Math.max(0, (x + L) / (L - boca)));
    skinIndex[v * 4] = 0;
    skinIndex[v * 4 + 1] = 1;
    skinWeight[v * 4] = 1 - w;
    skinWeight[v * 4 + 1] = w;
  }
  return { skinIndex, skinWeight };
}

function comPesos(g, f, nome) {
  const { skinIndex, skinWeight } = pesosDoAntebraco(g.attributes.position.array, f);
  g.setAttribute('skinIndex', new THREE.Uint16BufferAttribute(skinIndex, 4));
  g.setAttribute('skinWeight', new THREE.Float32BufferAttribute(skinWeight, 4));
  g.name = nome;
  g.userData.shared = true;
  return g;
}

/**
 * As malhas do antebraço e da braçadeira (Workers e cache do SdfMesher), com os pesos. Quem recebe é dono (a
 * LuvasSource divide entre os braços e descarta no fim).
 * @param {import('../../clay/sdf/sdfMesher.js').SdfMesher} sdf
 * @returns {Promise<{antebraco:THREE.BufferGeometry, bracadeira:THREE.BufferGeometry}>}
 */
export async function construirAntebraco(sdf, f) {
  const { pulso, cotovelo } = extensaoDoAntebraco(f);
  const extensao = (pulso - cotovelo) / MM_POR_U;
  const b = B.bracadeira;
  const extBracadeira = Math.max(b.larguraMM, secaoDoAntebraco(f, -b.doPulsoMM).largura + 2 * b.espessuraMM) / MM_POR_U;
  const [antebraco, bracadeira] = await Promise.all([
    sdf.build(arvoreDoAntebraco(f), {
      resolution: Math.min(1024, Math.ceil(extensao / B.malha.celulaU)), maxCells: B.malha.maxCells, touchRadius: B.malha.touchRadius,
    }),
    sdf.build(arvoreDaBracadeira(f), {
      resolution: Math.min(1024, Math.ceil(extBracadeira / b.malha.celulaU)), maxCells: b.malha.maxCells, touchRadius: b.malha.touchRadius,
    }),
  ]);
  return { antebraco: comPesos(antebraco, f, 'antebraco-de-massinha'), bracadeira: comPesos(bracadeira, f, 'bracadeira-de-massinha') };
}
