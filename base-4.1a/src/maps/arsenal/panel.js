// Painel de fita crepe da bancada `arsenal` (Tab solta o mouse; o MatchState chama open/close pelo `map.panel`):
// escolher a arma da roda, a facção do acento, o nível de detalhe e uma skin; explodir os grupos, mostrar as âncoras,
// sobrepor a planta, parar a roda, medir a silhueta contra a planta, reler a receita depois de exportar do Blender e
// "segurar" a arma (o viewmodel com a câmera parada). Linha de informação com triângulos e tempo de geração.

import { h } from '../../ui/dom.js';
import { WEAPONS } from '../../data/weapons.js';
import { CLAY_SKINS, CLAY_SKIN_IDS } from '../../data/claySkins.js';
import { section, segmented, slider, switchRow } from '../../debug/panelControls.js';

const FACTIONS = [
  { id: 'tr', label: 'Massa Crua' },
  { id: 'ct', label: 'Tropa do Estúdio' },
  { id: 'ambos', label: 'Dos dois lados' },
];
const LODS = [{ id: 'perto', label: 'Perto (0,14 u)' }, { id: 'mundo', label: 'Mundo (0,35 u)' }];

/**
 * @param {object} s serviços do jogo
 * @param {{bench:import('./bench.js').ArsenalBench, onClose:Function, onHold?:Function, isHolding?:()=>boolean}} deps
 *   `onHold` liga/desliga o "segurar" (o mapa cuida da câmera e do viewmodel); `isHolding` diz se está segurando
 */
export function createArsenalPanel(s, { bench, onClose, onHold = null, isHolding = () => false }) {
  const weaponSeg = segmented('Arma na roda', bench.ids.map((id) => ({ id, label: WEAPONS[id]?.name ?? id })), (id) => bench.select(id));
  const factionSeg = segmented('Facção do acento', FACTIONS, (id) => bench.setFaction(id));
  const lodSeg = segmented('Nível de detalhe', LODS, (id) => bench.setLod(id));
  const skinSelect = h('select.clay-select', { 'aria-label': 'Skin' },
    h('option', { value: '' }, 'Sem skin (a massa da receita)'),
    ...CLAY_SKIN_IDS.map((id) => h('option', { value: id }, CLAY_SKINS[id].label)));
  skinSelect.addEventListener('change', () => bench.setSkin(skinSelect.value));
  const explode = slider({
    label: 'Explodir os grupos', min: 0, max: 1, step: 0.01, value: 0, format: (v) => `${Math.round(v * 100)}%`,
    onInput: (v) => bench.setExplode(v),
  });
  const anchors = switchRow('Mostrar as âncoras (mãos, boca, ejeção)', { onChange: (v) => bench.setAnchors(v) });
  const plan = switchRow('Planta por cima da silhueta', { onChange: (v) => bench.setPlanOverlay(v) });
  const spin = switchRow('Girar a roda', { checked: true, onChange: (v) => bench.setSpin(v) });
  const info = h('p.vt-note', { role: 'status' });
  const measureOut = h('p.vt-note', { role: 'status' }, 'IoU da silhueta lateral × planta: aperte "Medir" (trava ~1 s).');
  const measure = h('button.btn-clay.is-small', { type: 'button' }, 'Medir a silhueta');
  measure.addEventListener('click', () => {
    const t0 = performance.now();
    const iou = bench.measure();
    measureOut.textContent = iou === null ? 'Esta arma não tem planta.'
      : `IoU ${iou.toFixed(3)} (aceite: ≥ 0,8) · ${(performance.now() - t0).toFixed(0)} ms`;
  });
  const reload = h('button.btn-clay.is-small', { type: 'button' }, 'Reler a receita do disco');
  const reloadOut = h('p.vt-note', { role: 'status' }, 'Depois de exportar do Blender: a arma da roda e a da fileira voltam com a receita nova.');
  reload.addEventListener('click', async () => {
    reloadOut.textContent = 'Relendo e gerando…';
    try {
      await bench.reload();
      reloadOut.textContent = `Receita de ${bench.state.id} relida.`;
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
      h('p.vt-note', null, 'A arma da roda sai da receita em src/data/armas/. Clique na cena ou Tab/Esc para voltar à câmera.'), close),
    section('Arma', weaponSeg.el, hold, info),
    section('Massa', factionSeg.el, h('div.vt-row', null, h('span.vt-label', null, 'Skin'), skinSelect), lodSeg.el),
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
    weaponSeg.set(st.id);
    factionSeg.set(st.faction);
    lodSeg.set(st.lod);
    skinSelect.value = st.skin ?? '';
    explode.set(st.explode);
    anchors.set(st.anchors);
    plan.set(st.plan);
    spin.set(st.spin);
    hold.textContent = HOLD_LABELS[isHolding() ? 1 : 0];
    const row = s.weaponModels.report().find((r) => r.id === st.id && r.lod === st.lod);
    info.textContent = row
      ? `${WEAPONS[st.id]?.name ?? st.id}: ${row.state} · ${row.triangles.toLocaleString('pt-BR')} triângulos em ${row.groups} grupo(s) · gerada em ${row.ms} ms`
      : 'Nenhuma arma na roda.';
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
