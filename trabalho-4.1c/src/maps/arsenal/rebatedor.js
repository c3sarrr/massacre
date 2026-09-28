// O rebatedor da bancada `arsenal` (Fase 4.1b; desenho da 4.1b, seção 7.6; plano, Tarefa 12): uma placa de isopor
// branco num C-stand, atrás de quem olha a bancada e virada para ela, como os rebatedores dos sets de estúdio (seção
// 0.9; item 3 do moodboard: o C-stand e as formas de luz das bordas, SSD14 e SMD7). O lado do receptor das armas
// realistas refletia o estúdio escuro atrás do olho e saía quase preto: a placa entra na foto do reflexo (a cena
// inteira, fotografada do olho do "Segurar", src/render/setReflection.js) e na vista da bancada.
//  - a placa: caixa de largura × altura × espessura (u = mm) com o isopor do set (`set.foam`), a frente (+Z local)
//    virada para a bissetriz, no plano horizontal, entre a luz que a acende (o `luz` da montagem, o rim) e o olho do
//    reflexo, deitada `inclinacao` graus para trás em volta do eixo de baixo dela — o cartão rebatedor de mesa, que
//    devolve a contraluz para a frente (os dados explicam a posição) — e com a borda de baixo assentada no apoio (o
//    tampo, atrás do tapete): a altura do centro sai da inclinação;
//  - o tripé: o C-stand do equipamento de luz (src/render/studio/fixtures.js), com o encaixe no meio das costas da placa
//    e a coluna `braco` para trás dela, no chão do estúdio (desce fora da mesa);
//  - fora da colisão (a bancada não tem); as geometrias saem com o mapa, os materiais são da biblioteca do set.

import * as THREE from 'three';
import { buildCStand } from '../../render/studio/fixtures.js';

/**
 * A direção da frente da placa em pé: a bissetriz entre a direção da luz e a do olho, a partir do centro dela, no plano
 * horizontal.
 * @param {THREE.Vector3} centro
 * @param {THREE.Vector3} olho
 * @param {THREE.Vector3} luz
 * @returns {THREE.Vector3} unitária
 */
export function frenteDoRebatedor(centro, olho, luz) {
  const paraOlho = olho.clone().sub(centro).normalize();
  const paraLuz = luz.clone().sub(centro).normalize();
  return paraOlho.add(paraLuz).setY(0).normalize();
}

/**
 * A altura do centro da placa acima do apoio com a borda de baixo encostada nele: só o giro em volta de Y (a frente no
 * plano horizontal) e a inclinação em volta do eixo de baixo; o giro em Y não muda a altura, e o ponto mais baixo é a
 * aresta de baixo de trás — deitada para trás, a placa se apoia nela — (a metade da altura pelo cosseno, a metade da
 * espessura pelo seno); a de baixo da frente fica a espessura pelo seno acima do apoio.
 * @param {{altura:number, espessura:number, inclinacao?:number}} def
 * @returns {number}
 */
export function alturaDoCentro(def) {
  const t = THREE.MathUtils.degToRad(def.inclinacao ?? 0);
  return (def.altura / 2) * Math.cos(t) + (def.espessura / 2) * Math.sin(t);
}

/**
 * @param {object} set a biblioteca de materiais do set (foam, blackMetal, chrome)
 * @param {object} def ARSENAL.rebatedor
 * @param {{floorY:number, apoioY:number, olho:THREE.Vector3, luz:THREE.Vector3}} ctx o chão do estúdio, a altura da
 *   superfície em que a placa assenta (o tampo), o olho do reflexo e a posição da luz que acende a placa (mundo)
 * @returns {{group:THREE.Group, painel:THREE.Mesh, dispose:()=>void}}
 */
export function construirRebatedor(set, def, { floorY, apoioY, olho, luz }) {
  const [x, z] = def.centro;
  const centro = new THREE.Vector3(x, apoioY + alturaDoCentro(def), z);
  const frente = frenteDoRebatedor(centro, olho, luz);
  const group = new THREE.Group();
  group.name = 'rebatedor';

  const painel = new THREE.Mesh(
    new THREE.BoxGeometry(def.largura, def.altura, def.espessura),
    set.foam({ color: def.cor, conta: def.conta }),
  );
  painel.name = 'rebatedor-painel';
  painel.position.copy(centro);
  painel.lookAt(centro.clone().add(frente)); // o +Z da placa na frente; o `up` do mundo deixa o lado de cima em pé
  painel.rotateX(-THREE.MathUtils.degToRad(def.inclinacao ?? 0)); // o topo deita para trás, a frente sobe
  painel.castShadow = true;
  painel.receiveShadow = true;
  group.add(painel);

  painel.updateMatrixWorld(true);
  const face = new THREE.Vector3(0, 0, 1).applyQuaternion(painel.quaternion);
  const encaixe = centro.clone().addScaledVector(face, -def.espessura / 2);
  const tripe = buildCStand(set, { mountWorld: encaixe, awayDir: face.clone().negate(), floorY, reach: def.braco });
  group.add(tripe.group);

  return {
    group,
    painel,
    dispose() {
      group.traverse((o) => {
        if (o.isMesh) o.geometry.dispose();
      });
      group.removeFromParent();
    },
  };
}
