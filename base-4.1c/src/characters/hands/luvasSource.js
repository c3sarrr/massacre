// Serviço `luvasModels` (Fase 4.1b; desenho em docs/superpowers/specs/2026-09-26-4.1b-luvas-e-empunhadura-design.md,
// seção 7.3; plano, Tarefa 9): as luvas táticas feitas no Blender (assets/maos/; registro em src/data/luvas.js) com o
// antebraço de massinha. Carrega uma vez o luvas.glb (os dois braços com o esqueleto e as correções das dobras), o
// relatório e a ficha; as texturas (_n e _m) quando o primeiro material é pedido; os materiais por facção (as pinturas
// de LUVAS, no material das zonas das armas, com o padrão pela pose de repouso e as duas faces, como o .glb pede); e as
// malhas do antebraço e da braçadeira de massinha, geradas uma vez por sessão no SdfMesher. Tudo marcado
// `userData.shared` (o dispose das cenas não toca) e dividido entre os braços; cada braço (`instanciar`) tem o esqueleto
// e as cópias das malhas da luva dele. Os carregadores são injetados: no navegador, os da origem glb das armas
// (GLTFLoader do vendor com o Draco); no Node, os dos testes.

import * as THREE from 'three';
import { FACCOES_DAS_LUVAS, LUVAS, ZONAS_DAS_LUVAS } from '../../data/luvas.js';
import { ambienteDoMaterial, criarMaterialZona } from '../../weapons/model/materialArma.js';
import { validarPintura } from '../../weapons/skins/skin.js';
import { construirAntebraco } from './antebracoMassa.js';
import { BracoLuva } from './bracoLuva.js';
import { validarFichaLuvas } from './fichaLuvas.js';
import { descartarMolde, moldeDoBraco } from './moldeLuva.js';

const now = () => (globalThis.performance?.now ? globalThis.performance.now() : Date.now());
const RAIZ = new URL('../../../', import.meta.url);
const LADOS = Object.freeze(['d', 'e']);

export class LuvasSource {
  #carregar;
  #sdf;
  #log;
  #anisotropia;
  #pronto = null; // Promise<dados>
  #dados = null; // {moldes: {d, e}, ficha, relatorio, ms}
  #texturas = null; // Promise<{n, m}>
  #texturasProntas = [];
  #materiais = new Map(); // facção → Promise<{zona: material}>
  #prontosMat = new Map(); // facção → {zona: material}
  #antebraco = null; // Promise<{antebraco, bracadeira}>
  #antebracoPronto = null;
  #bracos = new Set();
  #ambiente = null;
  #intensidade = 1;
  #erro = null;
  #descartada = false;

  /**
   * @param {{carregadores:{glb:(url:string)=>Promise<{scene:THREE.Object3D}>, textura:(url:string)=>Promise<THREE.Texture>,
   *   json:(url:string)=>Promise<object>, descartar?:()=>void}, sdf:{build:(tree:object, o:object)=>Promise<THREE.BufferGeometry>},
   *   log?:object|null, anisotropia?:number}} deps
   */
  constructor({ carregadores, sdf, log = null, anisotropia = 8 }) {
    this.#carregar = carregadores;
    this.#sdf = sdf;
    this.#log = log;
    this.#anisotropia = anisotropia;
  }

  #url(arquivo) {
    return new URL(`${LUVAS.pasta}${arquivo}`, RAIZ).href;
  }

  /** Um arquivo pelo carregador, com o nome dele no erro. */
  #buscar(tipo, url) {
    const arquivo = url.slice(url.lastIndexOf('/') + 1);
    return this.#carregar[tipo](url).catch((e) => {
      throw new Error(`${arquivo}: ${e?.message ?? e}`);
    });
  }

  /** Carrega o .glb, o relatório e a ficha (uma vez; pedidos ao mesmo tempo dividem a promessa). */
  carregar() {
    if (this.#descartada) return Promise.reject(new Error('LuvasSource: já foi descartada'));
    if (!this.#pronto) {
      const t0 = now();
      const p = Promise.all([
        this.#buscar('glb', this.#url('luvas.glb')),
        this.#buscar('json', this.#url('luvas.relatorio.json')),
        this.#buscar('json', new URL('tools/blender/refs/luvas.json', RAIZ).href),
      ]).then(([gltf, relatorio, ficha]) => {
        const f = validarFichaLuvas(ficha);
        const moldes = {};
        try {
          for (const lado of LADOS) moldes[lado] = moldeDoBraco(gltf.scene, lado, ZONAS_DAS_LUVAS);
        } finally {
          // os materiais do arquivo não entram: cada zona recebe os da facção
          gltf.scene.traverse((o) => {
            if (o.isMesh) for (const m of [o.material].flat()) m?.dispose();
          });
        }
        if (this.#descartada || this.#pronto !== p) {
          for (const lado of LADOS) descartarMolde(moldes[lado]);
          throw new Error('luvas descartadas durante a carga');
        }
        for (const lado of LADOS) {
          if (relatorio?.marca?.[lado] && relatorio.marca[lado] !== moldes[lado].marca) {
            this.#log?.warn?.(`luvas: a marca do rig ${lado} do relatório não é a do .glb (arquivos de construções diferentes)`);
          }
        }
        if (relatorio?.aprovado === false) this.#log?.warn?.(`luvas: o relatório do Blender não aprovou as luvas (${(relatorio.problemas ?? []).join('; ')})`);
        const dados = { moldes, ficha: f, relatorio, ms: now() - t0 };
        this.#dados = dados;
        this.#erro = null;
        this.#log?.debug?.(`luvas: ${moldes.d.triangulos} + ${moldes.e.triangulos} triângulos em ${dados.ms.toFixed(0)} ms`);
        return dados;
      });
      p.catch((err) => {
        if (this.#pronto === p) this.#pronto = null;
        if (this.#descartada) return;
        this.#erro = err?.message ?? String(err);
        this.#log?.error?.(`luvas: não carregaram — ${this.#erro}`);
      });
      this.#pronto = p;
    }
    return this.#pronto;
  }

  #texturasDasLuvas() {
    if (!this.#texturas) {
      const p = Promise.all([this.#buscar('textura', this.#url('luvas_n.webp')), this.#buscar('textura', this.#url('luvas_m.webp'))])
        .then(([n, m]) => {
          for (const t of [n, m]) {
            t.userData.shared = true;
            t.anisotropy = this.#anisotropia;
            this.#texturasProntas.push(t);
          }
          return { n, m };
        });
      p.catch(() => {
        if (this.#texturas === p) this.#texturas = null;
      });
      this.#texturas = p;
    }
    return this.#texturas;
  }

  /** Os materiais (um por zona) da pintura de uma facção; divididos entre os braços. */
  materiais(faccao) {
    if (this.#descartada) return Promise.reject(new Error('LuvasSource: já foi descartada'));
    if (!FACCOES_DAS_LUVAS.includes(faccao)) return Promise.reject(new Error(`facção das luvas desconhecida: ${faccao} (use ${FACCOES_DAS_LUVAS.join(', ')})`));
    let p = this.#materiais.get(faccao);
    if (!p) {
      p = this.#texturasDasLuvas().then((texturas) => {
        const pintura = validarPintura(ZONAS_DAS_LUVAS, LUVAS.pinturas[faccao], `luvas ${faccao}`);
        const mats = {};
        for (const zona of ZONAS_DAS_LUVAS) {
          const m = criarMaterialZona({
            zona, def: pintura.zonas[zona], texturas, ambiente: this.#ambiente, intensidade: this.#intensidade,
            nome: `luvas:${faccao}:${zona}`, repouso: true,
          });
          m.side = THREE.DoubleSide; // o punho mostra o forro por dentro da boca, como no .glb
          mats[zona] = m;
        }
        if (this.#descartada || this.#materiais.get(faccao) !== p) {
          for (const m of Object.values(mats)) m.dispose();
          throw new Error('luvas descartadas durante a carga');
        }
        this.#prontosMat.set(faccao, mats);
        return mats;
      });
      p.catch(() => {
        if (this.#materiais.get(faccao) === p) this.#materiais.delete(faccao);
      });
      this.#materiais.set(faccao, p);
    }
    return p;
  }

  /** As malhas do antebraço e da braçadeira de massinha (uma vez por sessão). */
  #antebracoDe(ficha) {
    if (!this.#antebraco) {
      const p = construirAntebraco(this.#sdf, ficha).then((g) => {
        if (this.#descartada || this.#antebraco !== p) {
          g.antebraco.dispose();
          g.bracadeira.dispose();
          throw new Error('luvas descartadas durante a geração do antebraço');
        }
        this.#antebracoPronto = g;
        return g;
      });
      p.catch((err) => {
        if (this.#antebraco === p) this.#antebraco = null;
        if (!this.#descartada) this.#log?.error?.(`luvas: o antebraço de massinha não foi gerado — ${err?.message ?? err}`);
      });
      this.#antebraco = p;
    }
    return this.#antebraco;
  }

  /**
   * Um braço novo (esqueleto e malhas da luva próprios) na pintura da facção, com a massa do antebraço na cor dada.
   * @param {'d'|'e'} lado @param {string} faccao @param {{corDaMassa:string}} o
   */
  async instanciar(lado, faccao, { corDaMassa }) {
    if (!LADOS.includes(lado)) throw new Error(`lado das luvas: 'd' ou 'e' (veio ${lado})`);
    const dados = await this.carregar();
    const [materiais, antebraco] = await Promise.all([this.materiais(faccao), this.#antebracoDe(dados.ficha)]);
    if (this.#descartada) throw new Error('LuvasSource: já foi descartada');
    const braco = new BracoLuva({
      molde: dados.moldes[lado], faccao, materiais, materiaisDe: (f) => this.materiais(f), antebraco, corDaMassa,
      limites: dados.ficha.limites, log: this.#log,
    });
    this.#bracos.add(braco);
    const descartar = braco.dispose.bind(braco);
    braco.dispose = () => {
      this.#bracos.delete(braco);
      descartar();
    };
    return braco;
  }

  /** A ficha validada (null antes de carregar). */
  get ficha() {
    return this.#dados?.ficha ?? null;
  }

  /** A marca do rig de cada braço (null antes de carregar). */
  get marca() {
    const d = this.#dados;
    return d ? { d: d.moldes.d.marca, e: d.moldes.e.marca } : null;
  }

  /** Reflexo do set nos materiais das luvas (null volta ao ambiente da cena). */
  setAmbiente(textura, intensidade = 1) {
    this.#ambiente = textura;
    this.#intensidade = intensidade;
    for (const mats of this.#prontosMat.values()) for (const m of Object.values(mats)) ambienteDoMaterial(m, textura, intensidade);
  }

  /** Anisotropia das texturas das luvas (graphics.anisotropy). */
  setAnisotropia(n) {
    this.#anisotropia = n;
    for (const t of this.#texturasProntas) {
      t.anisotropy = n;
      t.needsUpdate = true;
    }
  }

  /** O estado do console `luvas`: carga, triângulos por braço, o antebraço de massinha, a marca e os braços vivos. */
  relatorio() {
    const d = this.#dados;
    return {
      estado: d ? 'pronta' : this.#pronto ? 'carregando' : this.#erro ? 'erro' : '—',
      erro: this.#erro,
      triangulos: d ? { d: d.moldes.d.triangulos, e: d.moldes.e.triangulos } : { d: 0, e: 0 },
      antebraco: this.#antebracoPronto ? this.#antebracoPronto.antebraco.index.count / 3 : 0,
      ms: d ? Math.round(d.ms) : 0,
      marca: this.marca,
      bracos: this.#bracos.size,
    };
  }

  dispose() {
    this.#descartada = true;
    for (const b of [...this.#bracos]) b.dispose();
    for (const mats of this.#prontosMat.values()) for (const m of Object.values(mats)) m.dispose();
    this.#prontosMat.clear();
    this.#materiais.clear();
    for (const t of this.#texturasProntas) t.dispose();
    this.#texturasProntas = [];
    this.#texturas = null;
    if (this.#antebracoPronto) {
      this.#antebracoPronto.antebraco.dispose();
      this.#antebracoPronto.bracadeira.dispose();
    }
    this.#antebracoPronto = null;
    this.#antebraco = null;
    if (this.#dados) for (const lado of LADOS) descartarMolde(this.#dados.moldes[lado]);
    this.#dados = null;
    this.#pronto = null;
    this.#carregar.descartar?.();
  }
}
