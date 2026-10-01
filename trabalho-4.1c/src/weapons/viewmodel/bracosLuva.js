// Os braços de luva do viewmodel (Fase 4.1b; desenho em docs/superpowers/specs/2026-09-26-4.1b-luvas-e-empunhadura-
// design.md, seção 7.4; plano, Tarefa 10): os dois braços da LuvasSource (serviço `luvasModels`) na mão das armas
// realistas com pega. A pega do .glb da arma põe os dedos (a marca do rig conferida), cada osso `mao` vai para o
// referencial dele na pega (a pose da arma na câmera), o antebraço aponta para o cotovelo da categoria com o polegar
// para cima na meia pronação, a pintura é a da facção (a do time, ou a do boneco sem time) e a braçadeira só aparece
// com time. As variantes de shader compilam antes de o braço aparecer (sem travada). A pega de uma mão (a faca, 4.1c)
// vai só ao braço direito: o esquerdo volta ao repouso e não aparece.

import * as THREE from 'three';
import { GLOVE_SIDE, gloveTarget } from './placement.js';

const SIDES = Object.freeze(['direita', 'esquerda']);
const CIMA = Object.freeze(new THREE.Vector3(0, 1, 0));
const MM_POR_U = 25.4;

export class BracosDeLuva {
  #luvas;
  #log;
  #corDaMassa;
  #pronto = null;
  #descartado = false;
  #alvo = { position: new THREE.Vector3(), quaternion: new THREE.Quaternion() };

  /**
   * @param {{luvas:import('../../characters/hands/luvasSource.js').LuvasSource, log?:object|null, corDaMassa:string,
   *   faccao:string}} deps
   */
  constructor({ luvas, log = null, corDaMassa, faccao }) {
    this.#luvas = luvas;
    this.#log = log;
    this.#corDaMassa = corDaMassa;
    this.faccao = faccao;
    this.bracadeira = null;
    this.bracos = { direita: null, esquerda: null };
    this.pega = null;
    this.avisos = { direita: [], esquerda: [] };
  }

  get prontos() {
    return Boolean(this.bracos.direita && this.bracos.esquerda);
  }

  /** Alcance da mão de luva a partir do pulso (u): a ponta do médio com o tecido e o couro da ponta. */
  get alcance() {
    const f = this.#luvas.ficha;
    return f ? (f.mao.comprimento.mm + f.luva.tecido + f.luva.couro) / MM_POR_U : 0;
  }

  /**
   * Cria os dois braços uma vez, presos em `pai` e escondidos; `compilar(objeto)` compila as variantes de shader deles
   * antes (o compile do three só percorre o que está visível).
   * @param {THREE.Object3D} pai @param {(o:THREE.Object3D)=>Promise<void>} [compilar]
   */
  garantir(pai, compilar = null) {
    if (!this.#pronto) {
      const p = Promise.all(SIDES.map((s) => this.#luvas.instanciar(GLOVE_SIDE[s], this.faccao, { corDaMassa: this.#corDaMassa })))
        .then(async (bracos) => {
          if (this.#descartado) {
            for (const b of bracos) b.dispose();
            throw new Error('viewmodel descartado');
          }
          SIDES.forEach((s, i) => {
            const b = bracos[i];
            b.setBracadeira(this.bracadeira);
            pai.add(b.grupo);
            this.bracos[s] = b;
          });
          // visíveis (como nasceram) para o compile; escondidos até a arma com pega entrar na mão
          if (compilar) for (const b of bracos) await compilar(b.grupo);
          for (const b of bracos) b.grupo.visible = false;
          // a facção pode ter mudado durante a carga
          await this.setFaccao(this.faccao);
        });
      p.catch((err) => {
        if (this.#pronto === p) this.#pronto = null;
        if (!this.#descartado) this.#log?.error?.('viewmodel: braços de luva', err);
      });
      this.#pronto = p;
    }
    return this.#pronto;
  }

  /** Os dedos na pega da arma nos braços que ela tem (a faca: só o direito; o outro volta ao repouso); false (e o erro
   *  no log) se a pega é de outro rig. */
  aplicarPega(pega) {
    try {
      const lados = pega.lados ?? ['d', 'e'];
      for (const s of SIDES) {
        if (lados.includes(GLOVE_SIDE[s])) this.bracos[s].aplicarPega(pega);
        else if (this.bracos[s].pega) this.bracos[s].soltarPega();
      }
      this.pega = pega;
      return true;
    } catch (err) {
      this.pega = null;
      this.#log?.error?.(`viewmodel: ${err?.message ?? err}`);
      return false;
    }
  }

  /**
   * Põe os braços nos lados pedidos: o osso `mao` na pega (pela pose da arma) e o antebraço para o cotovelo.
   * @param {{position:THREE.Vector3, quaternion:THREE.Quaternion}} placement a pose da arma na câmera
   * @param {(side:string)=>THREE.Vector3} cotovelo o cotovelo de cada lado no referencial da câmera
   * @param {Set<string>} lados
   * @returns {THREE.Vector3[]} os pulsos (para a esfera da sombra própria)
   */
  colocar(placement, cotovelo, lados) {
    const pulsos = [];
    for (const s of SIDES) {
      const b = this.bracos[s];
      if (!b) continue;
      b.grupo.visible = Boolean(this.pega && lados.has(s) && this.pega.maos[GLOVE_SIDE[s]]);
      if (!b.grupo.visible) continue;
      const alvo = gloveTarget(placement, this.pega.maos[GLOVE_SIDE[s]], this.#alvo);
      this.avisos[s] = b.colocar(alvo.position, alvo.quaternion, cotovelo(s), CIMA).avisos;
      pulsos.push(alvo.position.clone());
    }
    return pulsos;
  }

  /** Esconde os dois braços (a arma saiu da mão ou é de massinha). */
  esconder() {
    for (const s of SIDES) if (this.bracos[s]) this.bracos[s].grupo.visible = false;
  }

  /** Lados visíveis agora. */
  visiveis() {
    return SIDES.filter((s) => this.bracos[s]?.grupo.visible);
  }

  /** A pintura das luvas pela facção (os materiais trocam; as malhas ficam). */
  async setFaccao(faccao) {
    this.faccao = faccao;
    await Promise.all(SIDES.map((s) => this.bracos[s]?.setFaccao(faccao)));
  }

  /** Braçadeira do time: cor ou null. */
  setBracadeira(cor) {
    this.bracadeira = cor;
    for (const s of SIDES) this.bracos[s]?.setBracadeira(cor);
  }

  dispose() {
    this.#descartado = true;
    for (const s of SIDES) {
      this.bracos[s]?.dispose();
      this.bracos[s] = null;
    }
    this.pega = null;
  }
}
