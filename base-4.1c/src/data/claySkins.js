// Skins procedurais de massinha (seção 0.15), aplicadas pelo mesmo ClayMaterial com parâmetros.
// `id` numérico vira define CLAY_SKIN no shader. Cores extras e parâmetros ficam aqui (balanceamento visual).
// O desbloqueio por nível/conquista entra na Fase 11 (src/progression).

export const CLAY_SKINS = Object.freeze({
  liso: Object.freeze({ id: 0, label: 'Massa lisa', params: [1, 1, 0, 0] }),
  marmorizado: Object.freeze({
    id: 1, label: 'Marmorizado', colorB: '#F4EDE1', colorC: '#2A2320',
    // escala (0,55 → 5–8 faixas largas numa bola de 40 u, MPC3/MPC11), distorção das camadas (2,6: faixas que
    // fluem sem virar manchas), veio escuro, —
    params: [0.55, 2.6, 0.22, 0],
  }),
  glitter: Object.freeze({
    id: 2, label: 'Glitter', colorB: '#FFE8A3', colorC: '#9FD8FF',
    // densidade (fino ~0,5 u por célula, grosso ~2,3 u), fração sem floco fino, tinta do floco grosso, —
    params: [1.25, 0.45, 0.85, 0],
  }),
  escolar: Object.freeze({ id: 3, label: 'Massa de escola desbotada', params: [0.45, 0.22, 0.12, 0] }), // saturação, clareamento, pó
  // emissão (fraca: só vence na sombra, como pigmento fosforescente), variação
  neon: Object.freeze({ id: 4, label: 'Neon', params: [1.1, 0.35, 0, 0] }),
  misturada: Object.freeze({
    id: 5, label: 'Massa misturada', colorB: '#3FB8AF', colorC: '#FFD23F',
    params: [0.75, 4.0, 0, 0], // escala, torção (4 → uma volta a cada ~12 u, duas espessuras da corda)
  }),
  madeira: Object.freeze({
    id: 6, label: 'Madeira falsa', colorB: '#5E3A22', colorC: '#A87A4F',
    params: [0.7, 9.0, 0.35, 0], // escala dos anéis, frequência, veio
  }),
  camuflagem: Object.freeze({
    id: 7, label: 'Camuflagem de massinha', colorB: '#5B6B3A', colorC: '#3B3526',
    params: [0.55, 0.0, 0, 0], // escala das manchas
  }),
  ouro: Object.freeze({ id: 8, label: 'Ouro (Gun Game)', params: [1, 0.32, 0, 0], metalness: 1, roughness: 0.34, color: '#E2B53E' }),
  // Base (não é skin de jogador): a madeira das armas (Fase 4.1), riscada a palito ao longo do comprimento da peça
  // (QPG2, QPL4, QPG8). Cores B (risco) e C (faixa clara) vêm da massa em src/data/weaponPalette.js.
  veio: Object.freeze({
    id: 9, label: 'Madeira riscada a palito', base: true, colorB: '#4A2C19', colorC: '#A5764D',
    params: [1, 0.16, 0.85, 0], // escala (1 → ~0,45 u entre riscos), largura do risco, força do risco, —
  }),
});

/** Skins de jogador (a Fase 11 desbloqueia): todas menos as de base das peças. */
export const CLAY_SKIN_IDS = Object.freeze(Object.keys(CLAY_SKINS).filter((id) => !CLAY_SKINS[id].base));
