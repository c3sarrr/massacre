// Origem `glb` do serviço weaponModels (Fase 4.1a; desenho em docs/superpowers/specs/2026-09-26-armas-realistas-design.md,
// seção 5.2): as armas realistas feitas no Blender (assets/armas/<id>/; registro em src/data/armasReais.js). Carrega o
// .glb uma vez por arma (os três níveis, os soquetes, as peças móveis), o relatório e a ficha (a planta da bancada); as
// texturas por conjunto (`perto`: 2048/1024; `mundo`: 512/256, que também serve o `longe`) quando o primeiro material do
// conjunto é pedido; os materiais por (arma, conjunto, skin), guardando a de fábrica e as duas últimas usadas. Tudo
// marcado `userData.shared` (o dispose das cenas não toca); sai no `forget` (recarga) e no `dispose`. Os carregadores
// são injetados: no navegador, o GLTFLoader do vendor e o TextureLoader; no Node, falsos.
// Fase 4.1b: nas categorias com regra de pega (CATEGORIAS_COM_PEGA), o `info.pega` (pegaDoGltf: a marca do rig, os dedos
// do clipe `empunhadura` e o referencial do osso `mao` de cada lado) e `hands: true` — o viewmodel segura com as luvas.
// Sem a pega no .glb (construído antes das luvas) a arma aparece sem braços, com o erro no log.

import * as THREE from 'three';
import { ARMAS_REAIS, LODS_REAIS, TEXTURAS_DO_LOD } from '../../data/armasReais.js';
import { CATEGORIAS_COM_PEGA } from '../../data/luvas.js';
import { VIEWMODEL } from '../../data/viewmodel.js';
import { pegaDoGltf } from '../../characters/hands/pega.js';
import { FABRICA, chaveDaSkin, skinDeFabrica } from '../skins/skin.js';
import { fichaParaPlanta, MM_POR_U, validarFicha } from './ficha.js';
import { ancorasDosSoquetes, montarInstanciaGlb, resumirGlb } from './glbWeapon.js';
import { ambienteDoMaterial, criarMaterialZona } from './materialArma.js';

const now = () => (globalThis.performance?.now ? globalThis.performance.now() : Date.now());
const RAIZ = new URL('../../../', import.meta.url);
const DECODIFICADOR_DRACO = new URL('vendor/three/examples/jsm/libs/draco/gltf/', RAIZ).href;
const SKINS_GUARDADAS = 2; // além da de fábrica, por (arma, conjunto)

/**
 * Carregadores do navegador: GLTFLoader do vendor com o DRACOLoader (a geometria vem comprimida), TextureLoader com as
 * texturas no padrão do glTF, fetch do JSON. `descartar` encerra os workers do decodificador.
 */
export function carregadoresDoNavegador() {
  let gltf = null; // Promise<GLTFLoader>: um carregador só, mesmo com pedidos ao mesmo tempo
  let draco = null;
  const texturas = new THREE.TextureLoader();
  const carregador = () => (gltf ??= Promise.all([
    import('three/addons/loaders/GLTFLoader.js'),
    import('three/addons/loaders/DRACOLoader.js'),
  ]).then(([{ GLTFLoader }, { DRACOLoader }]) => {
    draco = new DRACOLoader().setDecoderPath(DECODIFICADOR_DRACO);
    return new GLTFLoader().setDRACOLoader(draco);
  }));
  return {
    async glb(url) {
      return (await carregador()).loadAsync(url);
    },
    async textura(url) {
      const t = await texturas.loadAsync(url);
      t.flipY = false;
      t.colorSpace = THREE.NoColorSpace;
      return t;
    },
    async json(url) {
      const r = await fetch(url);
      if (!r.ok) throw new Error(`${url}: HTTP ${r.status}`);
      return r.json();
    },
    descartar() {
      draco?.dispose();
      draco = null;
      gltf = null;
    },
  };
}

export class GlbSource {
  #carregar;
  #log;
  #glb = new Map(); // id → Promise<pronto>
  #prontos = new Map(); // id → {resumo, info, ms, neutro}
  #texturas = new Map(); // `${id}:${conjunto}` → Promise<{n, m}>
  #materiais = new Map(); // `${id}:${conjunto}:${skin}` → Promise<{zona: material}>
  #prontosMat = new Map(); // mesma chave → {zona: material}
  #usadas = new Map(); // `${id}:${conjunto}` → chaves de skin na ordem de uso (a de fábrica fica sempre)
  #skins = new Map(); // id → skin atual
  #versoes = new Map(); // id → número da recarga (?v=)
  #texturasProntas = new Set(); // as carregadas (a anisotropia segue a config)
  #anisotropia;
  #ambiente = null;
  #intensidade = 1;
  #descartada = false;

  /**
   * @param {{carregadores:{glb:(url:string)=>Promise<{scene:THREE.Object3D}>, textura:(url:string)=>Promise<THREE.Texture>,
   *   json:(url:string)=>Promise<object>}, log?:object|null, anisotropia?:number}} deps
   */
  constructor({ carregadores, log = null, anisotropia = 8 }) {
    this.#carregar = carregadores;
    this.#log = log;
    this.#anisotropia = anisotropia;
  }

  get ids() {
    return Object.keys(ARMAS_REAIS);
  }

  has(id) {
    return Boolean(ARMAS_REAIS[id]);
  }

  lods() {
    return LODS_REAIS;
  }

  #url(id, arquivo) {
    const url = new URL(`${ARMAS_REAIS[id].pasta}${arquivo}`, RAIZ);
    const v = this.#versoes.get(id);
    if (v) url.searchParams.set('v', String(v));
    return url.href;
  }

  /** Carrega o .glb, o relatório e a ficha de uma arma (uma vez; pedidos iguais dividem a promessa). */
  carregar(id) {
    if (this.#descartada) return Promise.reject(new Error('WeaponLibrary: já foi descartada'));
    if (!this.has(id)) return Promise.reject(new Error(`${id} não é uma arma realista`));
    let p = this.#glb.get(id);
    if (!p) {
      const t0 = now();
      p = Promise.all([
        this.#carregar.glb(this.#url(id, `${id}.glb`)),
        this.#carregar.json(this.#url(id, `${id}.relatorio.json`)),
        this.#carregar.json(new URL(`tools/blender/refs/${id}.json`, RAIZ).href),
      ]).then(([gltf, relatorio, ficha]) => {
        const resumo = resumirGlb(gltf.scene, id);
        const pega = this.#pega(id, gltf);
        // O modelo carregado é o molde das instâncias e nunca vai à cena: as malhas dele guardam só a geometria, com um
        // material neutro no lugar dos do arquivo; cada instância recebe os materiais das zonas (montarInstanciaGlb).
        const neutro = new THREE.MeshBasicMaterial({ name: `molde:${id}` });
        resumo.raiz.traverse((o) => {
          if (!o.isMesh) return;
          for (const m of Array.isArray(o.material) ? o.material : [o.material]) m?.dispose();
          o.material = neutro;
        });
        if (this.#descartada || this.#glb.get(id) !== p) {
          resumo.raiz.traverse((o) => o.isMesh && o.geometry.dispose());
          neutro.dispose();
          throw new Error(`arma ${id} descartada durante a carga`);
        }
        const pronto = { resumo, info: this.#info(id, resumo, relatorio, validarFicha(ficha), pega), ms: now() - t0, neutro };
        this.#prontos.set(id, pronto);
        this.#log?.debug?.(`arma ${id} (glb): ${LODS_REAIS.map((l) => `${l} ${resumo.lods[l].triangulos}`).join(' · ')} triângulos em ${pronto.ms.toFixed(0)} ms`);
        return pronto;
      });
      p.catch((err) => {
        if (this.#glb.get(id) === p) this.#glb.delete(id);
        if (!this.#descartada) this.#log?.error?.(`arma ${id}: não carregou — ${err?.message ?? err}`);
      });
      this.#glb.set(id, p);
    }
    return p;
  }

  /** A pega das luvas da arma (null na categoria sem regra de pega, ou com o erro no log se o .glb não a tem). */
  #pega(id, gltf) {
    if (!CATEGORIAS_COM_PEGA.includes(this.#categoria(id))) return null;
    try {
      return pegaDoGltf(gltf, id);
    } catch (e) {
      this.#log?.error?.(`arma ${id}: sem a pega das luvas (construa a arma de novo no Blender) — ${e?.message ?? e}`);
      return null;
    }
  }

  #categoria(id) {
    return VIEWMODEL.weapons[id]?.category ?? ARMAS_REAIS[id].categoria;
  }

  #info(id, resumo, relatorio, ficha, pega) {
    const a = ARMAS_REAIS[id];
    const min = new THREE.Vector3().fromArray(resumo.caixa.min);
    const max = new THREE.Vector3().fromArray(resumo.caixa.max);
    return {
      id, source: 'glb', category: this.#categoria(id),
      bounds: resumo.caixa, radius: max.distanceTo(min) / 2,
      anchors: ancorasDosSoquetes(resumo.soquetes), sockets: resumo.soquetes,
      hands: Boolean(pega), pega,
      plan: fichaParaPlanta(ficha), lengthU: ficha.medidas.comprimento.mm / MM_POR_U,
      parts: [...a.pecas], zones: [...a.zonas], lods: [...LODS_REAIS],
      report: relatorio, ficha, iou: relatorio?.silhueta?.iouTolerancia ?? null, recipe: null,
    };
  }

  /** Info da arma (null antes de carregar). */
  info(id) {
    return this.#prontos.get(id)?.info ?? null;
  }

  /** Skin atual da arma (a de fábrica até alguém trocar). */
  skinOf(id) {
    if (!this.#skins.has(id)) this.#skins.set(id, skinDeFabrica(id));
    return this.#skins.get(id);
  }

  setSkin(id, skin) {
    this.#skins.set(id, skin);
  }

  #texturasDe(id, conjunto) {
    const chave = `${id}:${conjunto}`;
    let p = this.#texturas.get(chave);
    if (!p) {
      const pre = conjunto === 'perto' ? id : `${id}_mundo`;
      p = Promise.all([this.#carregar.textura(this.#url(id, `${pre}_n.webp`)), this.#carregar.textura(this.#url(id, `${pre}_m.webp`))])
        .then(([n, m]) => {
          for (const t of [n, m]) {
            t.userData.shared = true;
            t.anisotropy = this.#anisotropia;
            this.#texturasProntas.add(t);
          }
          return { n, m };
        });
      p.catch(() => {
        if (this.#texturas.get(chave) === p) this.#texturas.delete(chave);
      });
      this.#texturas.set(chave, p);
    }
    return p;
  }

  /** Materiais (um por zona) de uma arma num conjunto de texturas com uma skin. */
  materiais(id, conjunto, skin = this.skinOf(id)) {
    const sk = chaveDaSkin(skin);
    const chave = `${id}:${conjunto}:${sk}`;
    this.#usar(`${id}:${conjunto}`, sk);
    let p = this.#materiais.get(chave);
    if (!p) {
      p = this.#texturasDe(id, conjunto).then((texturas) => {
        const mats = {};
        for (const zona of ARMAS_REAIS[id].zonas) {
          mats[zona] = criarMaterialZona({
            zona, def: skin.zonas[zona], texturas, ambiente: this.#ambiente, intensidade: this.#intensidade,
            nome: `arma:${id}:${zona}:${sk}:${conjunto}`,
          });
        }
        if (this.#materiais.get(chave) !== p) {
          for (const m of Object.values(mats)) m.dispose();
          throw new Error(`arma ${id} descartada durante a carga`);
        }
        this.#prontosMat.set(chave, mats);
        return mats;
      });
      p.catch(() => {
        if (this.#materiais.get(chave) === p) this.#materiais.delete(chave);
      });
      this.#materiais.set(chave, p);
    }
    return p;
  }

  /** Guarda a de fábrica e as últimas skins usadas por (arma, conjunto); descarta os materiais da mais antiga. */
  #usar(grupo, sk) {
    const lista = (this.#usadas.get(grupo) ?? []).filter((k) => k !== sk);
    if (sk !== FABRICA) lista.push(sk);
    while (lista.length > SKINS_GUARDADAS) {
      const velha = `${grupo}:${lista.shift()}`;
      for (const m of Object.values(this.#prontosMat.get(velha) ?? {})) m.dispose();
      this.#prontosMat.delete(velha);
      this.#materiais.delete(velha);
    }
    this.#usadas.set(grupo, lista);
  }

  /** Instância nova da arma num nível, com a skin atual. */
  async instancia(id, { lod = 'perto' } = {}) {
    if (!LODS_REAIS.includes(lod)) throw new Error(`nível de detalhe desconhecido: ${lod} (use ${LODS_REAIS.join(', ')})`);
    const pronto = await this.carregar(id);
    const mats = await this.materiais(id, TEXTURAS_DO_LOD[lod]);
    return montarInstanciaGlb(pronto.resumo, id, lod, mats, pronto.info.anchors, pronto.info.radius);
  }

  /** Reflexo do set nos materiais de todas as armas (null volta ao ambiente da cena). */
  setAmbiente(textura, intensidade = 1) {
    this.#ambiente = textura;
    this.#intensidade = intensidade;
    for (const mats of this.#prontosMat.values()) for (const m of Object.values(mats)) ambienteDoMaterial(m, textura, intensidade);
  }

  /** Anisotropia das texturas das armas (graphics.anisotropy); as já carregadas sobem de novo para a GPU. */
  setAnisotropia(n) {
    this.#anisotropia = n;
    for (const t of this.#texturasProntas) {
      t.anisotropy = n;
      t.needsUpdate = true;
    }
  }

  /** Linhas do console `armas`: uma por (arma, nível). */
  relatorio() {
    const rows = [];
    for (const id of this.ids) {
      const pronto = this.#prontos.get(id);
      for (const lod of LODS_REAIS) {
        rows.push({
          id, lod, source: 'glb',
          state: pronto ? 'pronta' : this.#glb.has(id) ? 'carregando' : '—',
          triangles: pronto ? Math.round(pronto.resumo.lods[lod].triangulos) : 0,
          ms: pronto ? Math.round(pronto.ms) : 0,
          groups: pronto ? Object.keys(pronto.resumo.lods[lod].pecas).length : 0,
        });
      }
    }
    return rows;
  }

  /** Esquece a arma: descarta materiais, texturas e geometrias; a próxima carga busca de novo. */
  forget(id) {
    for (const [k, mats] of [...this.#prontosMat]) {
      if (!k.startsWith(`${id}:`)) continue;
      for (const m of Object.values(mats)) m.dispose();
      this.#prontosMat.delete(k);
    }
    for (const k of [...this.#materiais.keys()]) if (k.startsWith(`${id}:`)) this.#materiais.delete(k);
    for (const k of [...this.#usadas.keys()]) if (k.startsWith(`${id}:`)) this.#usadas.delete(k);
    for (const [k, p] of [...this.#texturas]) {
      if (!k.startsWith(`${id}:`)) continue;
      p.then(({ n, m }) => {
        for (const t of [n, m]) {
          this.#texturasProntas.delete(t);
          t.dispose();
        }
      }, () => {});
      this.#texturas.delete(k);
    }
    const pronto = this.#prontos.get(id);
    if (pronto) {
      pronto.resumo.raiz.traverse((o) => o.isMesh && o.geometry.dispose());
      pronto.neutro.dispose();
    }
    this.#prontos.delete(id);
    this.#glb.delete(id);
  }

  /** Recarga depois de exportar do Blender: esquece e busca de novo com ?v= novo (sem o cache do navegador). */
  async recarregar(id) {
    this.forget(id);
    this.#versoes.set(id, Date.now());
    return this.carregar(id);
  }

  dispose() {
    for (const id of this.ids) this.forget(id);
    this.#carregar.descartar?.();
    this.#descartada = true;
  }
}
