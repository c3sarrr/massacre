// Paleta das skins das armas (Fase 4.1a; desenho em docs/superpowers/specs/2026-09-26-armas-realistas-design.md, seção
// 6.2): cores nomeadas como as pinturas do Rocket League, várias vindas dos tokens das facções e da UI (terracota e
// azul da tropa, amarelo-massinha, laranja). A chave é o que o console aceita (também pelo nome, sem acento).

const F = Object.freeze;

export const CORES_SKIN = F({
  preto: F({ nome: 'Preto', hex: '#1B1B1D' }),
  brancoTitanio: F({ nome: 'Branco Titânio', hex: '#EDEDE8' }),
  cinzaGrafite: F({ nome: 'Cinza Grafite', hex: '#4A4E54' }),
  carmesim: F({ nome: 'Carmesim', hex: '#9E1B32' }),
  vermelho: F({ nome: 'Vermelho', hex: '#D1362F' }),
  laranja: F({ nome: 'Laranja', hex: '#F28F3B' }),
  acafrao: F({ nome: 'Açafrão', hex: '#E9A13B' }),
  amarelo: F({ nome: 'Amarelo', hex: '#FFD23F' }),
  lima: F({ nome: 'Lima', hex: '#9BD13B' }),
  verdeFloresta: F({ nome: 'Verde Floresta', hex: '#2F5D3A' }),
  verdeAgua: F({ nome: 'Verde-água', hex: '#3FB8AF' }),
  azulCobalto: F({ nome: 'Azul Cobalto', hex: '#2F4FB5' }),
  azulCeleste: F({ nome: 'Azul Celeste', hex: '#5DADE2' }),
  roxo: F({ nome: 'Roxo', hex: '#6C3FB5' }),
  rosa: F({ nome: 'Rosa', hex: '#E86FA3' }),
  marromSiena: F({ nome: 'Marrom Siena', hex: '#8C5A3C' }),
  areia: F({ nome: 'Areia', hex: '#C2A878' }),
  verdeOliva: F({ nome: 'Verde-oliva', hex: '#5B5F3A' }),
  terracota: F({ nome: 'Terracota', hex: '#C8553D' }),
  azulTropa: F({ nome: 'Azul Tropa', hex: '#2F6DB5' }),
});
