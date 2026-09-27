// Comandos do console da Fase 4.1 (docs/phases/phase-4.md, seção 4.1, "Console e dados"): o viewmodel como no CS
// (viewmodel_fov, viewmodel_offset_x/y/z, viewmodel_presetpos, r_viewmodel), a braçadeira de teste (cl_bracadeira), a
// bancada de armas (arsenal, arma <id>), a lista das armas com a origem (armas: o .glb do Blender ou a receita de
// massinha), o ajuste ao vivo da posição de cada categoria na mão (viewmodel_ajuste, para afinar src/data/viewmodel.js)
// e, na 4.1a, as skins de cor e acabamento das armas realistas (skin). Falam com a mesma config, a mesma biblioteca de
// armas e o mesmo viewmodel que o jogo usa.

import { EV } from '../core/events.js';
import { ACABAMENTOS } from '../data/acabamentos.js';
import { ZONAS } from '../data/armasReais.js';
import { CORES_SKIN } from '../data/coresSkin.js';
import { SKINS_ARMA } from '../data/skinsArma.js';
import { VIEWMODEL } from '../data/viewmodel.js';
import { WEAPONS, resolveWeaponId } from '../data/weapons.js';
import { FABRICA, aplicarZonas, descreverSkin, lerArgumentosSkin, skinPorNome } from '../weapons/skins/skin.js';
import { SELECT } from '../player/moveCmd.js';
import { applyViewmodelPreset, currentViewmodelPreset } from '../weapons/viewmodel/placement.js';
import { onOff } from './consoleArgs.js';

const SLOT_SELECT = Object.freeze({ primary: SELECT.SLOT1, secondary: SELECT.SLOT2, melee: SELECT.SLOT3 });
const ARMBAND_ARGS = Object.freeze({ tr: 'tr', ct: 'ct', 0: 'off', off: 'off', nenhum: 'off' });

const num = (v, what) => {
  const n = Number(String(v).replace(',', '.'));
  if (!Number.isFinite(n)) throw new Error(`${what} precisa ser um número`);
  return n;
};

export function registerWeaponCommands(con, s, { goState, matchState }) {
  const reg = (def) => con.register(def);
  const cfg = s.config;

  /** Variável numérica da config no formato do CS: sem argumento mostra, com argumento ajusta (no limite do esquema). */
  const cvar = (name, key, help) => reg({
    name,
    usage: `[${cfg.spec(key).min} a ${cfg.spec(key).max}]`,
    help,
    run: ([v]) => {
      if (v !== undefined) cfg.set(key, num(v, name));
      return `${name} ${cfg.get(key)}`;
    },
  });
  cvar('viewmodel_fov', 'viewmodel.fov', 'campo de visão da arma na mão (horizontal em 4:3, como no CS; padrão 60)');
  cvar('viewmodel_offset_x', 'viewmodel.offsetX', 'arma na mão para a direita (+) ou a esquerda (−)');
  cvar('viewmodel_offset_y', 'viewmodel.offsetY', 'arma na mão para a frente (+) ou para trás (−)');
  cvar('viewmodel_offset_z', 'viewmodel.offsetZ', 'arma na mão para cima (+) ou para baixo (−)');
  reg({
    name: 'viewmodel_presetpos', usage: '[1|2|3]', help: 'posições prontas do CS: 1 Mesa, 2 Sofá, 3 Clássica',
    complete: () => Object.keys(VIEWMODEL.presets),
    run: ([id]) => {
      if (id === undefined) {
        const cur = currentViewmodelPreset(cfg);
        return cur ? `viewmodel_presetpos ${cur} (${VIEWMODEL.presets[cur].label})` : 'viewmodel_presetpos: ajustada à mão';
      }
      const p = applyViewmodelPreset(cfg, id);
      return `viewmodel_presetpos ${id} (${p.label}): fov ${p.fov}, offset ${p.x} ${p.y} ${p.z}`;
    },
  });
  reg({
    name: 'r_viewmodel', usage: '[0|1]', help: 'mostra ou esconde a arma na mão em primeira pessoa',
    run: ([v]) => `r_viewmodel ${cfg.set('debug.viewmodel', onOff(v, cfg.get('debug.viewmodel'))) ? 1 : 0}`,
  });
  reg({
    name: 'cl_bracadeira', usage: '[tr|ct|0]', help: 'braçadeira de teste do time no antebraço (e o acento das armas dos dois lados)',
    complete: () => ['tr', 'ct', '0'],
    run: ([v]) => {
      if (v !== undefined) {
        const value = ARMBAND_ARGS[String(v).toLowerCase()];
        if (!value) throw new Error('uso: cl_bracadeira tr|ct|0');
        cfg.set('debug.armband', value);
      }
      const cur = cfg.get('debug.armband');
      return `cl_bracadeira ${cur === 'off' ? '0 (sem time)' : cur}`;
    },
  });

  reg({
    name: 'arsenal', aliases: ['bancada'], help: 'abre a bancada de armas (a AK realista e as de massinha; Tab para o painel)',
    run: () => {
      goState('match', { map: 'arsenal', mode: 'livre' });
      return 'montando a bancada de armas…';
    },
  });

  reg({
    name: 'arma', usage: '<id>', help: 'na bancada, põe a arma na roda; nos mapas de andar, dá a arma e põe na mão',
    complete: () => s.weaponModels.ids,
    run: ([name]) => {
      const ids = s.weaponModels.ids;
      if (!name) throw new Error(`qual arma? (${ids.join(', ')})`);
      const id = resolveWeaponId(name) ?? name;
      if (!s.weaponModels.has(id)) throw new Error(`${name} ainda não tem modelo (tem: ${ids.join(', ')})`);
      const m = matchState();
      if (m?.map?.bench) {
        m.map.bench.select(id);
        return `na roda: ${WEAPONS[id]?.name ?? id}`;
      }
      const p = m?.player;
      if (!p?.hands) throw new Error('abra a bancada (arsenal) ou um mapa de andar (sala de testes, pista)');
      const loadout = s.localLoadout;
      const slot = WEAPONS[id].slot;
      if (loadout[slot] !== id) {
        const res = loadout.give(id, { ignoreTeam: true });
        if (!res.ok) throw new Error(res.reason);
        s.events.emit(EV.LOADOUT, { owner: 'local', loadout: loadout.toJSON(), received: { kind: 'weapon', id, slot: res.slot } });
      }
      p.pendingSelect = SLOT_SELECT[slot];
      return `na mão: ${WEAPONS[id].name}`;
    },
  });

  reg({
    name: 'armas', help: 'armas com modelo: a origem (glb do Blender ou massinha), o estado, os triângulos e o tempo por nível; e as mãos',
    run: () => {
      const head = `${'arma'.padEnd(8)}${'origem'.padEnd(10)}${'nível'.padEnd(7)}${'estado'.padEnd(12)}${'triângulos'.padStart(11)}${'ms'.padStart(7)}${'peças'.padStart(7)}`;
      const rows = s.weaponModels.report().map((r) =>
        `${r.id.padEnd(8)}${r.source.padEnd(10)}${r.lod.padEnd(7)}${r.state.padEnd(12)}${r.triangles.toLocaleString('pt-BR').padStart(11)}${String(r.ms).padStart(7)}${String(r.groups).padStart(7)}`);
      const hands = s.handModels.report();
      return [head, ...rows, `mãos: ${hands.state} · ${hands.triangles.toLocaleString('pt-BR')} triângulos por braço · ${hands.ms} ms`].join('\n');
    },
  });

  // Skins de cor e acabamento das armas realistas (Fase 4.1a; desenho, seção 6.3). A troca vai para o serviço de armas
  // (weaponModels.setSkin), que avisa a roda da bancada, a fileira e a mão (EV.WEAPON_MODEL, phase 'skin').
  const realistas = () => s.weaponModels.ids.filter((id) => s.weaponModels.source(id) === 'glb');
  const linhasDaSkin = (id, skin) => [`${id} — ${skin.nome}:`, ...descreverSkin(skin).map((l) => `  ${l}`)].join('\n');
  reg({
    name: 'skin',
    usage: '[<arma> [fabrica | <nome da skin> | <zona>=<acabamento>:<cor>[,<cor2>] … desgaste=<0..1>]]',
    help: 'skin de cor e acabamento das armas realistas: mostra, troca pela de fábrica ou por uma nomeada, ou pinta por zona',
    complete: (index) => (index === 0
      ? realistas()
      : [FABRICA, ...Object.keys(SKINS_ARMA), ...ZONAS.map((z) => `${z}=`), 'desgaste=']),
    run: ([nome, ...args]) => {
      const reais = realistas();
      if (!nome) {
        return [
          ...reais.map((id) => `${id}: ${s.weaponModels.skinOf(id).nome}`),
          `skins: fabrica, ${Object.values(SKINS_ARMA).map((k) => k.nome).join(', ')}`,
          `acabamentos: ${Object.keys(ACABAMENTOS).join(', ')}`,
          `cores: ${Object.keys(CORES_SKIN).join(', ')} (ou #RRGGBB)`,
          'uso: skin <arma> [fabrica | <nome> | <zona>=<acabamento>:<cor>[,<cor2>] … desgaste=<0..1>]',
        ].join('\n');
      }
      const id = resolveWeaponId(nome) ?? nome;
      if (!reais.includes(id)) throw new Error(`${nome} não é uma arma realista (skins de acabamento só nas feitas no Blender: ${reais.join(', ')})`);
      const pedido = lerArgumentosSkin(args);
      if (pedido.tipo === 'mostrar') return linhasDaSkin(id, s.weaponModels.skinOf(id));
      const skin = pedido.tipo === 'nome' ? skinPorNome(id, pedido.nome) : aplicarZonas(id, s.weaponModels.skinOf(id), pedido);
      s.weaponModels.setSkin(id, skin);
      return linhasDaSkin(id, skin);
    },
  });

  reg({
    name: 'viewmodel_ajuste',
    usage: '[pos x y z | ang arfagem guinada rolagem | cotovelo direita|esquerda x y z | mao direita|esquerda x y z rx ry rz | zerar]',
    help: 'afina ao vivo a posição da categoria (linha para src/data/viewmodel.js) ou a âncora de uma mão (linha para a receita)',
    complete: () => ['pos', 'ang', 'cotovelo', 'mao', 'zerar'],
    run: ([what, ...args]) => {
      const vm = matchState()?.viewmodel;
      const cat = vm?.category;
      if (!cat) throw new Error('segure uma arma em primeira pessoa primeiro');
      if (what === 'mao') {
        const [side, ...v] = args;
        if ((side !== 'direita' && side !== 'esquerda') || (v.length !== 3 && v.length !== 6)) {
          throw new Error('uso: viewmodel_ajuste mao direita|esquerda x y z [rx ry rz] (rad, Euler XYZ da receita)');
        }
        const n = v.map((a) => num(a, 'mao'));
        return vm.setAnchorTune(side, n.length === 6 ? { pos: n.slice(0, 3), rot: n.slice(3) } : { pos: n });
      }
      if (what === 'zerar') vm.clearTune(cat);
      else if (what === 'pos' || what === 'ang') {
        if (args.length !== 3) throw new Error(`uso: viewmodel_ajuste ${what} <3 números>`);
        const v = args.map((a) => num(a, what));
        vm.setTune(cat, what === 'pos' ? { pos: v } : { angles: v });
      } else if (what === 'cotovelo') {
        const [side, ...xyz] = args;
        if (side !== 'direita' && side !== 'esquerda') throw new Error('uso: viewmodel_ajuste cotovelo direita|esquerda x y z');
        if (xyz.length !== 3) throw new Error('uso: viewmodel_ajuste cotovelo direita|esquerda x y z');
        vm.setTune(cat, { elbows: { [side]: xyz.map((a) => num(a, 'cotovelo')) } });
      } else if (what !== undefined) {
        throw new Error('uso: viewmodel_ajuste [pos x y z | ang arfagem guinada rolagem | cotovelo direita|esquerda x y z | mao direita|esquerda x y z rx ry rz | zerar]');
      }
      return vm.tuneLine(cat);
    },
  });
}
