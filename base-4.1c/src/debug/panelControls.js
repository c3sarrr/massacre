// Controles dos painéis de fita crepe dos mapas de teste (vitrine, arsenal): régua deslizante com rótulo e valor,
// cartão com a fita do título, interruptor com rótulo e grupo de botões "segmentado". Classes em styles/showcase.css.

import { h } from '../ui/dom.js';

let uid = 0;

/** Id único para ligar rótulo e controle. */
export const controlId = () => `vt-${++uid}`;

/** Régua deslizante com rótulo e valor. `onInput` a cada movimento; `onCommit` ao soltar (mudanças caras). */
export function slider({ label, min, max, step, value, format, onInput, onCommit = null }) {
  const id = controlId();
  const input = h('input.clay-range', { id, type: 'range', min, max, step });
  const out = h('output.vt-value', { for: id });
  const paint = (v) => {
    input.value = String(v);
    input.style.setProperty('--fill', `${((v - min) / (max - min)) * 100}%`);
    out.textContent = format(v);
  };
  input.addEventListener('input', () => {
    const v = Number(input.value);
    paint(v);
    onInput(v);
  });
  if (onCommit) input.addEventListener('change', () => onCommit(Number(input.value)));
  paint(value);
  const el = h('div.vt-row', null, h('label.vt-label', { for: id }, label), input, out);
  return { el, set: paint };
}

/** Cartão do painel com o título numa tira de fita. */
export function section(title, ...children) {
  return h('section.vt-card', null, h('h3.tape-label.vt-tape', null, title), ...children);
}

/** Interruptor (checkbox com papel de switch) com rótulo. */
export function switchRow(label, { checked = false, onChange }) {
  const id = controlId();
  const input = h('input.clay-switch', { id, type: 'checkbox', role: 'switch' });
  input.checked = checked;
  input.addEventListener('change', () => onChange(input.checked));
  const el = h('div.vt-row.vt-inline', null, input, h('label.vt-label', { for: id }, label));
  return { el, set: (v) => { input.checked = v; } };
}

/**
 * Grupo de botões de escolha única. `items` = [{id, label}]; `onPick(id)` no clique; `set(id)` marca o escolhido.
 */
export function segmented(ariaLabel, items, onPick) {
  const buttons = items.map(({ id, label }) => {
    const b = h('button.seg', { type: 'button', role: 'radio', dataset: { pick: id } }, label);
    b.addEventListener('click', () => onPick(id));
    return b;
  });
  const el = h('div.segmented', { role: 'radiogroup', 'aria-label': ariaLabel }, ...buttons);
  const set = (id) => {
    for (const b of buttons) {
      const on = b.dataset.pick === id;
      b.classList.toggle('is-on', on);
      b.setAttribute('aria-checked', on ? 'true' : 'false');
    }
  };
  return { el, set, buttons };
}
