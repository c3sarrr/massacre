// Os cotovelos de luva de uma categoria do viewmodel (Fase 4.1c; plano da 4.1c, Tarefa 12): a varredura que acha os
// `gloveElbows` de src/data/viewmodel.js com as armas de verdade (o .glb pela biblioteca de armas, com a pega do
// Blender) e as luvas de verdade, no mesmo Viewmodel do jogo (sem GPU, como os testes do Node):
//
//   node tools/cotovelos.mjs <arma|categoria> [--lados direita,esquerda] [--limite 0.93] [--folga 3]
//
// O cotovelo de luva é para onde o antebraço aponta, no referencial da câmera, o mesmo nas três posições prontas do CS
// (viewmodel_presetpos: a Mesa, o Sofá e a Clássica mudam o FOV e os offsets, e o pulso anda com a arma) e em todas as
// armas da categoria (com a pega e o ajuste fino de cada uma: a AK e a M4A4 no `rifle`); com uma arma, só nela. Para cada
// lado da pega (ou só os de `--lados`; os outros ficam nos de hoje), o que a varredura minimiza é o pior ângulo do pulso
// e do antebraço em relação ao limite da AAOS da ficha das luvas (a flexão ou a extensão, o desvio radial ou ulnar e a
// pronação ou a supinação a partir da meia pronação) em todas as posições — o minimax, como o do apoio do `rifle` (a
// soma dos quadrados trocava um ângulo por outro e deixava um deles a 99 % do limite) —, com a soma dos quadrados só
// para desempatar. Restrições, em todas as posições: o cotovelo de
// verdade (o osso `antebraco`, a um antebraço do pulso) abaixo do pulso e fora da tela em 16:9 e 21:9, e o antebraço de
// massinha a pelo menos `folga` mm da arma (a malha do antebraço com o skin na CPU contra a malha do perto). A varredura
// começa numa grade de direções a partir do pulso da Mesa (três distâncias) e refina as melhores por busca de padrão;
// imprime o achado de cada lado, os ângulos e as folgas em cada posição, os cotovelos que a categoria tem hoje avaliados
// do mesmo jeito e a linha para colar em src/data/viewmodel.js. No fim, confere o achado no Viewmodel inteiro (a luva
// deformada, os avisos do braço) e a folga entre os dois antebraços e entre cada antebraço e a outra luva, arma por arma.
// Os carregadores do .glb no Node (o Draco sem Workers) e o SdfMesher da grade grossa vêm dos utilitários dos testes das
// luvas (tests/luvasTestUtils.js): o antebraço sai da mesma árvore SDF do jogo, mais grosso.

import * as THREE from 'three';
import { MeshBVH } from 'three-mesh-bvh';
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';
import { Config } from '../src/core/config.js';
import { EventBus } from '../src/core/events.js';
import { ARMAS_REAIS, armaComPega } from '../src/data/armasReais.js';
import { CONFIG_SCHEMA } from '../src/data/configSchema.js';
import { VIEWMODEL } from '../src/data/viewmodel.js';
import { LuvasSource } from '../src/characters/hands/luvasSource.js';
import { WeaponLibrary } from '../src/weapons/model/weaponLibrary.js';
import {
  GLOVE_SIDE, applyViewmodelPreset, categoryPlacement, gloveTarget, viewCategory, viewmodelVerticalFov,
} from '../src/weapons/viewmodel/placement.js';
import { Viewmodel } from '../src/weapons/viewmodel/viewmodel.js';
import { carregadoresDoDisco, decodificadorDraco, sdfDeTeste } from '../tests/luvasTestUtils.js';

const MM = 25.4;
const CIMA = new THREE.Vector3(0, 1, 0);
const TELAS = [16 / 9, 21 / 9];
// a grade de partida: direções a partir do pulso da Mesa (graus) e as distâncias do cotovelo (u)
const AZIMUTES = Array.from({ length: 36 }, (_, i) => i * 10);
const ELEVACOES = Array.from({ length: 25 }, (_, i) => -85 + i * 5);
const DISTANCIAS = [16, 30, 55];
const PASSOS = [4, 2, 1, 0.5, 0.25, 0.1]; // u, a busca de padrão
const MELHORES = 12; // quantos pontos da grade a busca de padrão refina
const AMOSTRA = 3; // um vértice do antebraço a cada tantos na folga (a malha da grade grossa)
const SINAL = Object.freeze({ direita: 1, esquerda: -1 }); // para que lado do pulso fica o cotovelo
const OUTRO = Object.freeze({ direita: 'esquerda', esquerda: 'direita' });

function opcoes(argv) {
  const [alvo, ...resto] = argv;
  if (!alvo) throw new Error('uso: node tools/cotovelos.mjs <arma|categoria> [--lados direita,esquerda] [--limite 0.93] [--folga 3]');
  const o = { alvo, limite: 0.93, folga: 3, lados: null };
  for (let i = 0; i < resto.length; i += 2) {
    const v = Number(resto[i + 1]);
    if (resto[i] === '--limite' && v > 0) o.limite = v;
    else if (resto[i] === '--folga' && v >= 0) o.folga = v;
    else if (resto[i] === '--lados' && resto[i + 1]?.split(',').every((l) => SINAL[l])) o.lados = resto[i + 1].split(',');
    else throw new Error(`opção desconhecida ou valor inválido: ${resto[i]} ${resto[i + 1] ?? ''}`);
  }
  // a categoria (todas as realistas com pega dela) ou a arma sozinha
  if (VIEWMODEL.categories[alvo]) {
    o.categoria = alvo;
    o.armas = Object.keys(VIEWMODEL.weapons).filter((id) => viewCategory(id) === alvo && ARMAS_REAIS[id] && armaComPega(id));
    if (!o.armas.length) throw new Error(`a categoria ${alvo} não tem arma realista com a pega`);
  } else {
    o.categoria = viewCategory(alvo);
    if (!o.categoria) throw new Error(`${alvo} não é categoria nem arma com categoria de viewmodel (src/data/viewmodel.js)`);
    o.armas = [alvo];
  }
  return o;
}

/** O Viewmodel do jogo com as armas pedidas, com as luvas de verdade (a montagem dos testes, sem GPU). */
async function montar(armas) {
  const carregadores = carregadoresDoDisco(await decodificadorDraco());
  const lib = new WeaponLibrary({ sdf: null, carregadores });
  const weapons = {
    has: (id) => armas.includes(id), source: () => 'glb', describe: (id) => lib.describe(id), info: (id) => lib.info(id),
    instance: (id, o) => lib.instance(id, o),
  };
  const hands = { async createArm(side) { return { side, mesh: new THREE.Object3D(), setPose() {}, setArmband() {}, place() {}, dispose() {} }; } };
  const events = new EventBus();
  const config = new Config(CONFIG_SCHEMA, { events });
  const render = {
    renderer: { compileAsync: async () => {}, shadowMap: { enabled: false, needsUpdate: false } },
    pipeline: { addLayer: () => () => {} }, shadowLevel: 0,
  };
  const luvas = new LuvasSource({ carregadores, sdf: sdfDeTeste(24) });
  const vm = new Viewmodel({ render, weapons, hands, luvas, config, events });
  return { vm, config, camera: new THREE.PerspectiveCamera(74, 16 / 9, 0.5, 400) };
}

/** Quadros até a arma estar na mão, nas luvas (as cargas são promessas). */
async function segurar(vm, camera, arma) {
  for (let i = 0; i < 600; i++) {
    vm.frame(camera, 1 / 60, { item: arma, visible: true });
    if (vm.status().item === arma && vm.layer.visible) {
      if (vm.status().bracos !== 'luvas') throw new Error(`${arma} não está nas luvas (sem a pega no .glb?)`);
      return;
    }
    await new Promise((r) => setTimeout(r, 5));
  }
  throw new Error(`o viewmodel não segurou ${arma}`);
}

/** A malha da arma no referencial da câmera (a raiz do viewmodel), numa BVH. */
function bvhDaArma(vm) {
  vm.root.updateMatrixWorld(true);
  const inv = vm.root.matrixWorld.clone().invert();
  const partes = [];
  vm.weapon.traverse((o) => {
    if (!o.isMesh || !o.visible) return;
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', o.geometry.attributes.position.clone());
    if (o.geometry.index) g.setIndex(o.geometry.index.clone());
    partes.push(g.applyMatrix4(new THREE.Matrix4().multiplyMatrices(inv, o.matrixWorld)));
  });
  return new MeshBVH(mergeGeometries(partes, false));
}

/** Os vértices do antebraço de massinha com o skin (na CPU), no referencial da câmera (u). */
function pontosDoAntebraco(vm, braco, passo = AMOSTRA) {
  braco.grupo.updateMatrixWorld(true);
  braco.skeleton.update();
  const inv = vm.root.matrixWorld.clone().invert();
  const m = braco.antebraco;
  const n = m.geometry.attributes.position.count;
  const out = [];
  for (let i = 0; i < n; i += passo) {
    const p = m.getVertexPosition(i, new THREE.Vector3()).applyMatrix4(m.matrixWorld).applyMatrix4(inv);
    out.push(p);
  }
  return out;
}

/** A malha do antebraço com o skin (os triângulos dela), no referencial da câmera, numa BVH. */
function bvhDoAntebraco(vm, braco) {
  const g = new THREE.BufferGeometry().setFromPoints(pontosDoAntebraco(vm, braco, 1));
  g.setIndex(braco.antebraco.geometry.index.clone());
  return new MeshBVH(g);
}

/** As malhas da luva deformada, no referencial da câmera, numa BVH. */
function bvhDaLuva(vm, braco) {
  braco.grupo.updateMatrixWorld(true);
  const inv = vm.root.matrixWorld.clone().invert();
  const partes = braco.malhas.map((m) => {
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', m.geometry.attributes.position.clone());
    if (m.geometry.index) g.setIndex(m.geometry.index.clone());
    return g.applyMatrix4(new THREE.Matrix4().multiplyMatrices(inv, m.matrixWorld));
  });
  return new MeshBVH(mergeGeometries(partes, false));
}

/** A menor distância (mm) de pontos a uma BVH. */
function folgaMM(bvh, pontos) {
  let menor = Infinity;
  const alvo = { point: new THREE.Vector3(), distance: 0 };
  for (const p of pontos) {
    bvh.closestPointToPoint(p, alvo);
    menor = Math.min(menor, alvo.distance);
  }
  return menor * MM;
}

/** As razões ângulo/limite do pulso e do antebraço (o lado do limite pelo sinal do ângulo). */
function razoes(a, l) {
  return {
    flexao: a.flexao >= 0 ? a.flexao / l.pulso.flexao : -a.flexao / l.pulso.extensao,
    desvio: a.desvio >= 0 ? a.desvio / l.pulso.radial : -a.desvio / l.pulso.ulnar,
    pronacao: a.pronacao >= 0 ? a.pronacao / l.antebraco.pronacao : -a.pronacao / l.antebraco.supinacao,
  };
}

/** Onde um ponto da câmera cai na tela (−1 a 1 dentro do quadro) e se está à frente do plano de perto. */
function naTela(p, fovV, aspect) {
  const t = Math.tan((fovV * Math.PI) / 360);
  return { x: p.x / (-p.z * t * aspect), y: p.y / (-p.z * t), frente: p.z < -VIEWMODEL.near };
}

/**
 * As três posições prontas da arma na mão: a pose da arma, o alvo de cada mão (o osso `mao` na pega), o FOV vertical, a
 * BVH da arma e a pega (para deformar a luva dela quando o braço fica parado como obstáculo).
 */
function posicoes(vm, config, camera, arma) {
  const out = [];
  for (const id of Object.keys(VIEWMODEL.presets)) {
    applyViewmodelPreset(config, id);
    vm.frame(camera, 1 / 60, { item: arma, visible: true });
    const placement = { position: vm.placement.position.clone(), quaternion: vm.placement.quaternion.clone() };
    const alvos = {};
    for (const lado of ['direita', 'esquerda']) {
      const mao = vm.info.pega.maos[GLOVE_SIDE[lado]];
      if (mao) {
        const a = gloveTarget(placement, mao);
        alvos[lado] = { position: a.position.clone(), quaternion: a.quaternion.clone() };
      }
    }
    out.push({
      id, arma, pega: vm.info.pega, nome: `${arma} ${VIEWMODEL.presets[id].label}`, placement, alvos,
      fovV: viewmodelVerticalFov(VIEWMODEL.presets[id].fov), bvh: bvhDaArma(vm), outros: { direita: [], esquerda: [] },
    });
  }
  return out;
}

/**
 * Avalia um cotovelo `E` (referencial da câmera) num lado, nas três posições: o pior razão, a soma dos quadrados, as
 * violações das restrições (somadas, em unidades comparáveis) e o detalhe de cada posição.
 */
function avaliar(vm, braco, lado, pos, E, o) {
  let pior = 0;
  let quadrados = 0;
  let violacao = 0;
  const detalhe = [];
  const inv = vm.root.matrixWorld.clone().invert();
  for (const p of pos) {
    const alvo = p.alvos[lado];
    braco.colocar(alvo.position, alvo.quaternion, E, CIMA);
    const r = razoes(braco.angulos, braco.limites);
    const rs = Object.values(r);
    pior = Math.max(pior, ...rs);
    quadrados += rs.reduce((s, v) => s + v * v, 0);
    braco.grupo.updateMatrixWorld(true);
    const cotovelo = braco.ossos.antebraco.getWorldPosition(new THREE.Vector3()).applyMatrix4(inv);
    const pulso = braco.ossos.mao.getWorldPosition(new THREE.Vector3()).applyMatrix4(inv);
    // o cotovelo abaixo do pulso (u) e fora da tela (o quanto ele entra, nas duas telas)
    violacao += Math.max(0, cotovelo.y - pulso.y + 0.05);
    for (const aspect of TELAS) {
      const c = naTela(cotovelo, p.fovV, aspect);
      if (c.frente) violacao += Math.max(0, 1 - Math.max(Math.abs(c.x), Math.abs(c.y)));
    }
    // com as duas mãos, cada antebraço para o seu lado (o direito à direita do pulso, o esquerdo à esquerda: o
    // triângulo da pega isósceles; sem isso, o achado cruzava o antebraço direito por baixo do esquerdo)
    if (o.duasMaos) violacao += Math.max(0, SINAL[lado] * (pulso.x - cotovelo.x));
    const pontos = pontosDoAntebraco(vm, braco);
    const folga = folgaMM(p.bvh, pontos);
    violacao += Math.max(0, o.folga - folga) / 10;
    // e longe do outro braço (o antebraço e a luva dele, parados na pose achada)
    const outros = p.outros[lado];
    const folgaBraco = outros.length ? Math.min(...outros.map((b) => folgaMM(b, pontos))) : Infinity;
    violacao += Math.max(0, o.folga - folgaBraco) / 10;
    detalhe.push({
      posicao: p.nome, angulos: { ...braco.angulos }, razoes: r, folgaMM: folga, folgaBracoMM: folgaBraco,
      cotovelo: cotovelo.toArray(), pulso: pulso.toArray(),
    });
  }
  return { E: E.clone(), pior, quadrados, violacao, nota: pior + 1e-3 * quadrados + 100 * violacao, detalhe };
}

/** Busca de padrão nas três coordenadas do cotovelo, a partir de um ponto. */
function refinar(vm, braco, lado, pos, inicio, o) {
  let melhor = inicio;
  for (const passo of PASSOS) {
    let mudou = true;
    while (mudou) {
      mudou = false;
      for (let eixo = 0; eixo < 3; eixo++) {
        for (const s of [-1, 1]) {
          const E = melhor.E.clone();
          E.setComponent(eixo, E.getComponent(eixo) + s * passo);
          const c = avaliar(vm, braco, lado, pos, E, o);
          if (c.nota < melhor.nota - 1e-9) {
            melhor = c;
            mudou = true;
          }
        }
      }
    }
  }
  return melhor;
}

/** A varredura de um lado: a grade de direções a partir do pulso da Mesa e a busca de padrão nas melhores. */
function varrer(vm, braco, lado, pos, o) {
  const W = pos[0].alvos[lado].position;
  const grade = [];
  for (const r of DISTANCIAS) {
    for (const el of ELEVACOES) {
      for (const az of AZIMUTES) {
        const e = (el * Math.PI) / 180;
        const a = (az * Math.PI) / 180;
        // azimute no plano da tela: 0° para a direita (+X), 90° para trás (+Z)
        const d = new THREE.Vector3(Math.cos(e) * Math.cos(a), Math.sin(e), Math.cos(e) * Math.sin(a));
        grade.push(avaliar(vm, braco, lado, pos, W.clone().addScaledVector(d, r), o));
      }
    }
  }
  grade.sort((x, y) => x.nota - y.nota);
  const refinados = grade.slice(0, MELHORES).map((c) => refinar(vm, braco, lado, pos, c, o));
  refinados.sort((x, y) => x.nota - y.nota);
  return arredondar(vm, braco, lado, pos, refinados[0].E, o);
}

/**
 * O cotovelo com uma casa decimal (como vai para src/data/viewmodel.js): dos oito vizinhos na grade de 0,1 u, o de
 * melhor nota — o arredondamento simples podia sair das restrições por centésimos (o cotovelo a menos de 0,05 u abaixo
 * do pulso).
 */
function arredondar(vm, braco, lado, pos, E, o) {
  let melhor = null;
  for (let k = 0; k < 8; k++) {
    const c = E.toArray().map((v, i) => ((k >> i) & 1 ? Math.ceil(v * 10) : Math.floor(v * 10)) / 10);
    const a = avaliar(vm, braco, lado, pos, new THREE.Vector3(...c), o);
    if (!melhor || a.nota < melhor.nota) melhor = a;
  }
  return melhor;
}

const f1 = (v) => v.toFixed(1);
const pct = (v) => `${(100 * v).toFixed(0)} %`;

function imprimir(titulo, c, o) {
  const ok = c.pior <= o.limite && c.violacao === 0;
  console.log(`  ${titulo}: [${c.E.toArray().map(f1).join(', ')}] — pior ${pct(c.pior)}${c.violacao ? `, restrições violadas (${c.violacao.toFixed(3)})` : ''}${ok ? '' : ' ✗'}`);
  for (const d of c.detalhe) {
    const a = d.angulos;
    const r = d.razoes;
    console.log(`    ${d.posicao.padEnd(16)} flexão ${f1(a.flexao)}° (${pct(r.flexao)}), desvio ${f1(a.desvio)}° (${pct(r.desvio)}), `
      + `pronação ${f1(a.pronacao)}° (${pct(r.pronacao)}); antebraço a ${f1(d.folgaMM)} mm da arma`
      + `${Number.isFinite(d.folgaBracoMM) ? ` e ${f1(d.folgaBracoMM)} mm do outro braço` : ''}; `
      + `cotovelo [${d.cotovelo.map(f1).join(', ')}], pulso [${d.pulso.map(f1).join(', ')}]`);
  }
}

/**
 * Para o braço de um lado no cotovelo `E` (com a luva deformada de verdade) e guarda, em cada posição, o antebraço e a
 * luva dele (só a luva com `soLuva`) como obstáculo do outro lado.
 */
function fixar(vm, braco, lado, pos, E, atualizar, soLuva = false) {
  for (const p of pos) {
    if (vm.gloves.pega !== p.pega) vm.gloves.aplicarPega(p.pega); // os dedos e a palma da arma desta posição
    const alvo = p.alvos[lado];
    braco.colocar(alvo.position, alvo.quaternion, E, CIMA);
    atualizar.call(braco);
    p.outros[OUTRO[lado]] = soLuva ? [bvhDaLuva(vm, braco)] : [bvhDoAntebraco(vm, braco), bvhDaLuva(vm, braco)];
  }
}

/** O achado no Viewmodel inteiro, arma por arma: a luva deformada, os avisos e as folgas entre os braços. */
async function conferir(vm, config, camera, armas, categoria, cotovelos) {
  vm.setTune(categoria, { gloveElbows: cotovelos });
  const lados = Object.keys(cotovelos);
  for (const arma of armas) {
    await segurar(vm, camera, arma);
    for (const id of Object.keys(VIEWMODEL.presets)) {
      applyViewmodelPreset(config, id);
      vm.frame(camera, 1 / 60, { item: arma, visible: true });
      conferirPosicao(vm, `${arma} ${VIEWMODEL.presets[id].label}`, lados);
    }
  }
}

/** Os avisos e as folgas entre os braços na posição de agora. */
function conferirPosicao(vm, nome, lados) {
  const linhas = [`    ${nome}: avisos ${JSON.stringify(vm.status().avisos)}`];
  if (lados.length === 2) {
    const [a, b] = lados.map((l) => vm.gloves.bracos[l]);
    // os antebraços entre si e cada antebraço contra a outra luva (a malha deformada)
    linhas.push(`antebraço com antebraço ${f1(folgaMM(bvhDoAntebraco(vm, b), pontosDoAntebraco(vm, a, 1)))} mm, `
      + `antebraço ${lados[0]} com a luva ${lados[1]} ${f1(folgaMM(bvhDaLuva(vm, b), pontosDoAntebraco(vm, a, 1)))} mm, `
      + `antebraço ${lados[1]} com a luva ${lados[0]} ${f1(folgaMM(bvhDaLuva(vm, a), pontosDoAntebraco(vm, b, 1)))} mm`);
  }
  console.log(linhas.join('; '));
}

async function main() {
  const o = opcoes(process.argv.slice(2));
  const t0 = performance.now();
  const { vm, config, camera } = await montar(o.armas);
  const pos = [];
  let lados = null;
  for (const arma of o.armas) {
    await segurar(vm, camera, arma);
    const destas = ['direita', 'esquerda'].filter((l) => vm.info.pega.maos[GLOVE_SIDE[l]]);
    if (lados && destas.join() !== lados.join()) throw new Error(`${arma}: mãos ${destas.join(', ')}, as outras ${lados.join(', ')}`);
    lados = destas;
    pos.push(...posicoes(vm, config, camera, arma));
  }
  const otimizar = (o.lados ?? lados).filter((l) => lados.includes(l));
  // a luva não precisa ser deformada na varredura (os ângulos e o antebraço só dependem dos ossos do braço)
  const atualizar = {};
  for (const l of lados) {
    const b = vm.gloves.bracos[l];
    atualizar[l] = b.atualizar;
    b.atualizar = () => false;
  }
  o.duasMaos = lados.length === 2;
  console.log(`${o.categoria}: ${o.armas.join(', ')}; ${lados.join(' e ')} (achando ${otimizar.join(' e ')}), limite `
    + `${pct(o.limite)}, folga ${o.folga} mm`);
  // os de hoje: os da categoria, com os da arma por cima quando é uma arma só
  const atuais = categoryPlacement(o.categoria, null, o.armas.length === 1 ? o.armas[0] : null).gloveElbows;
  const achados = {};
  const bracos = Object.fromEntries(lados.map((l) => [l, vm.gloves.bracos[l]]));
  // os lados que ficam nos de hoje são obstáculo inteiro (o antebraço e a luva); com os dois achados, a mão do gatilho
  // primeiro, longe da luva de apoio (a mão parada pela pega; o punho dela muda pouco com o cotovelo), a de apoio depois,
  // longe do braço do gatilho já achado, e a do gatilho refinada de novo, longe do braço de apoio
  for (const l of lados.filter((x) => !otimizar.includes(x))) {
    fixar(vm, bracos[l], l, pos, new THREE.Vector3(...atuais[l]), atualizar[l]);
  }
  if (o.duasMaos && otimizar.length === 2) {
    fixar(vm, bracos.esquerda, 'esquerda', pos, new THREE.Vector3(...atuais.esquerda), atualizar.esquerda, true);
  }
  for (const l of otimizar) {
    console.log(`${l}:`);
    imprimir('hoje', avaliar(vm, bracos[l], l, pos, new THREE.Vector3(...atuais[l]), o), o);
    achados[l] = varrer(vm, bracos[l], l, pos, o);
    if (o.duasMaos) fixar(vm, bracos[l], l, pos, achados[l].E, atualizar[l]);
  }
  if (o.duasMaos && otimizar.length === 2) {
    const d = refinar(vm, bracos.direita, 'direita', pos, avaliar(vm, bracos.direita, 'direita', pos, achados.direita.E, o), o);
    achados.direita = arredondar(vm, bracos.direita, 'direita', pos, d.E, o);
  }
  for (const l of otimizar) {
    console.log(`${l}:`);
    imprimir('achado', achados[l], o);
  }
  for (const l of lados) vm.gloves.bracos[l].atualizar = atualizar[l];
  const cotovelos = Object.fromEntries(lados.map((l) => [l, (achados[l]?.E ?? new THREE.Vector3(...atuais[l])).toArray()
    .map((v) => Number(v.toFixed(1)))]));
  console.log('conferência no Viewmodel inteiro:');
  await conferir(vm, config, camera, o.armas, o.categoria, cotovelos);
  const linha = (l) => `F([${(cotovelos[l] ?? atuais[l]).join(', ')}])`;
  // na categoria `categories`; numa arma só, os lados achados vão para a arma em `weapons` quando a categoria tem outras
  console.log(`gloveElbows: F({ direita: ${linha('direita')}, esquerda: ${linha('esquerda')} }),`);
  if (o.armas.length === 1) {
    console.log(`  (só da arma, em VIEWMODEL.weapons.${o.armas[0]}: gloveElbows: F({ ${otimizar.map((l) => `${l}: ${linha(l)}`).join(', ')} }))`);
  }
  console.log(`(${((performance.now() - t0) / 1000).toFixed(1)} s)`);
  vm.dispose();
}

main().catch((err) => {
  console.error(err?.stack ?? err);
  process.exit(1);
});
