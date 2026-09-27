// Painel de fita crepe da bancada `arsenal` (Tab solta o mouse; o MatchState chama open/close pelo `map.panel`):
// escolher a arma da roda, a skin — de cor e acabamento na arma realista (a de fábrica e as nomeadas; o console `skin`
// faz as personalizadas por zona), de massa nas de massinha, que também escolhem a facção do acento — e o nível de
// detalhe; explodir as peças, mostrar as âncoras e os soquetes, sobrepor a planta, parar a roda, medir a silhueta contra
// a planta (a realista traz a medida do Blender), reler do disco depois de exportar do Blender e "segurar" a arma (o
// viewmodel com a câmera parada). Linha de informação com a origem, os triângulos e o tempo de carga ou de geração.

import { h } from '../../ui/dom.js';
import { WEAPONS } from '../../data/weapons.js';
import { CLAY_SKINS, CLAY_SKIN_IDS } from '../../data/claySkins.js';
import { SKINS_ARMA } from '../../data/skinsArma.js';
import { FABRICA, PERSONALIZADA } from '../../weapons/skins/skin.js';
import { section, segmented, slider, switchRow } from '../../debug/panelControls.js';

const FACTIONS = [
  { id: 'tr', label: 'Massa Crua' },
  { id: 'ct', label: 'Tropa do Estúdio' },
  { id: 'ambos', label: 'Dos dois lados' },
];
// O `longe` só existe na realista (o LOD2 do .glb); as de massinha têm perto (célula de 0,14 u) e mundo (0,35 u).
const LODS = [{ id: 'perto', label: 'Perto' }, { id: 'mundo', label: 'Mundo' }, { id: 'longe', label: 'Longe' }];
const pct = (v) => `${(v * 100).toFixed(1).replace('.', ',')} %`;

/**
 * @param {object} s serviços do jogo
 * @param {{bench:import('./bench.js').ArsenalBench, onClose:Function, onHold?:Function, isHolding?:()=>boolean}} deps
 *   `onHold` liga/desliga o "segurar" (o mapa cuida da câmera e do viewmodel); `isHolding` diz se está segurando
 */
export function createArsenalPanel(s, { bench, onClose, onHold = null, isHolding = () => false }) {
  const weaponSeg = segmented('Arma na roda', bench.ids.map((id) => ({ id, label: WEAPONS[id]?.name ?? id })), (id) => bench.select(id));
  const factionSeg = segmented('Facção do acento', FACTIONS, (id) => bench.setFaction(id));
  const lodSeg = segmented('Nível de detalhe', LODS, (id) => bench.setLod(id));
  const skinSelect = h('select.clay-select', { 'aria-label': 'Skin' });
  let skinKind = null; // 'glb' ou 'massinha': o jogo de opções que o seletor tem agora
  const fillSkins = (kind) => {
    if (kind === skinKind) return;
    skinKind = kind;
    skinSelect.replaceChildren(...(kind === 'glb'
      ? [
        h('option', { value: FABRICA }, 'De fábrica'),
        ...Object.entries(SKINS_ARMA).map(([key, def]) => h('option', { value: key }, def.nome)),
        h('option', { value: PERSONALIZADA, disabled: true }, 'Personalizada (pelo console: skin)'),
      ]
      : [
        h('option', { value: '' }, 'Sem skin (a massa da receita)'),
        ...CLAY_SKIN_IDS.map((id) => h('option', { value: id }, CLAY_SKINS[id].label)),
      ]));
  };
  skinSelect.addEventListener('change', () => bench.setSkin(skinSelect.value));
  const explode = slider({
    label: 'Explodir as peças', min: 0, max: 1, step: 0.01, value: 0, format: (v) => `${Math.round(v * 100)}%`,
    onInput: (v) => bench.setExplode(v),
  });
  const anchors = switchRow('Mostrar as âncoras e os soquetes (mãos, boca, ejeção, miras)', { onChange: (v) => bench.setAnchors(v) });
  const plan = switchRow('Planta por cima da silhueta', { onChange: (v) => bench.setPlanOverlay(v) });
  const spin = switchRow('Girar a roda', { checked: true, onChange: (v) => bench.setSpin(v) });
  const info = h('p.vt-note', { role: 'status' });
  const measureOut = h('p.vt-note', { role: 'status' }, 'Silhueta lateral × planta: aperte "Medir" (na de massinha trava ~1 s).');
  const measure = h('button.btn-clay.is-small', { type: 'button' }, 'Medir a silhueta');
  measure.addEventListener('click', () => {
    const t0 = performance.now();
    const m = bench.measure();
    if (!m) measureOut.textContent = 'Esta arma não tem planta.';
    else if (m.origem === 'glb') {
      measureOut.textContent = `Medida no Blender: ${pct(m.iou)} com a tolerância de 1 px da foto (bruto ${pct(m.bruto)}; aceite: ≥ 98 %).`;
    } else {
      measureOut.textContent = `IoU ${m.iou.toFixed(3)} (aceite: ≥ 0,8) · ${(performance.now() - t0).toFixed(0)} ms`;
    }
  });
  const reload = h('button.btn-clay.is-small', { type: 'button' }, 'Reler do disco');
  const reloadOut = h('p.vt-note', { role: 'status' }, 'Depois de exportar do Blender: a arma da roda e a da fileira voltam com o modelo novo.');
  reload.addEventListener('click', async () => {
    reloadOut.textContent = 'Relendo…';
    try {
      await bench.reload();
      reloadOut.textContent = `${WEAPONS[bench.state.id]?.name ?? bench.state.id} relida do disco.`;
    } catch (err) {
      reloadOut.textContent = `Falhou: ${err?.message ?? err}`;
    }
  });
  const HOLD_LABELS = ['Segurar (primeira pessoa)', 'Soltar a arma'];
  const hold = h('button.btn-clay.is-primary.is-small', { type: 'button', hidden: !onHold }, HOLD_LABELS[0]);
  hold.addEventListener('click', () => {
    onHold?.();
    sync();
  });

  const close = h('button.btn-clay.is-small', { type: 'button' }, 'Voltar à câmera (Tab)');
  close.addEventListener('click', () => onClose());
  const root = h('aside.vt-panel', { hidden: true, 'aria-label': 'Painel da bancada de armas' },
    h('header.vt-head', null, h('h2.vt-title', null, 'Bancada de armas'),
      h('p.vt-note', null, 'As armas realistas saem do Blender (assets/armas/); as de massinha, das receitas em src/data/armas/. Clique na cena ou Tab/Esc para voltar à câmera.'), close),
    section('Arma', weaponSeg.el, hold, info),
    section('Aparência', h('div.vt-row', null, h('span.vt-label', null, 'Skin'), skinSelect), factionSeg.el, lodSeg.el),
    section('Oficina', explode.el, anchors.el, plan.el, spin.el, measure, measureOut, reload, reloadOut),
  );
  root.addEventListener('keydown', (e) => {
    if (e.code === 'Tab') {
      e.preventDefault();
      onClose();
    }
  });
  s.uiRoot.append(root);

  function sync() {
    const st = bench.state;
    const glb = Boolean(st.id) && s.weaponModels.source(st.id) === 'glb';
    weaponSeg.set(st.id);
    factionSeg.el.hidden = glb;
    factionSeg.set(st.faction);
    for (const b of lodSeg.buttons) b.hidden = b.dataset.pick === 'longe' && !glb;
    lodSeg.set(st.lod);
    fillSkins(glb ? 'glb' : 'massinha');
    skinSelect.value = glb ? s.weaponModels.skinOf(st.id).chave : st.skin ?? '';
    explode.set(st.explode);
    anchors.set(st.anchors);
    plan.set(st.plan);
    spin.set(st.spin);
    hold.textContent = HOLD_LABELS[isHolding() ? 1 : 0];
    const name = WEAPONS[st.id]?.name ?? st.id;
    const row = s.weaponModels.report().find((r) => r.id === st.id && r.lod === st.lod);
    if (!row) info.textContent = 'Nenhuma arma na roda.';
    else if (glb) {
      info.textContent = `${name} (Blender): ${row.state} · ${row.triangles.toLocaleString('pt-BR')} triângulos em ${row.groups} peça(s) · carregada em ${row.ms} ms · skin ${s.weaponModels.skinOf(st.id).nome}`;
    } else {
      info.textContent = `${name} (massinha): ${row.state} · ${row.triangles.toLocaleString('pt-BR')} triângulos em ${row.groups} grupo(s) · gerada em ${row.ms} ms`;
    }
  }
  bench.onChange = sync;

  return {
    root,
    open() {
      sync();
      root.hidden = false;
    },
    close() {
      root.hidden = true;
    },
    refresh: sync,
    dispose() {
      bench.onChange = null;
      root.remove();
    },
  };
}
