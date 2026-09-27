// Skins nomeadas das armas realistas (Fase 4.1a; desenho em docs/superpowers/specs/2026-09-26-armas-realistas-design.md,
// seção 6.3): por zona, acabamento + cor (+ segunda cor no veio e na trama) + desgaste. São genéricas — valem para
// qualquer arma realista; a zona que a arma não tem é ignorada e a que a skin não traz fica de fábrica. As três abaixo
// são as do aceite da 4.1a; o catálogo, o desbloqueio e a tela de escolha são da Fase 11.

const F = Object.freeze;

export const SKINS_ARMA = F({
  anodizadoTerracota: F({
    nome: 'Anodizado Terracota',
    zonas: F({
      corpo: F({ acabamento: 'anodizado', cor: 'terracota', desgaste: 0.12 }),
      guarnicao: F({ acabamento: 'polimero', cor: 'preto', desgaste: 0.1 }),
      carregador: F({ acabamento: 'anodizado', cor: 'cinzaGrafite', desgaste: 0.15 }),
      detalhes: F({ acabamento: 'anodizado', cor: 'preto', desgaste: 0.2 }),
      interno: F({ acabamento: 'escovado', cor: 'brancoTitanio', desgaste: 0 }),
    }),
  }),
  cromoECarbono: F({
    nome: 'Cromo e Carbono',
    zonas: F({
      corpo: F({ acabamento: 'cromado', cor: 'brancoTitanio', desgaste: 0.05 }),
      guarnicao: F({ acabamento: 'carbono', cor: 'preto', cor2: 'cinzaGrafite', desgaste: 0.05 }),
      carregador: F({ acabamento: 'carbono', cor: 'preto', cor2: 'cinzaGrafite', desgaste: 0.1 }),
      detalhes: F({ acabamento: 'cromado', cor: 'brancoTitanio', desgaste: 0.1 }),
      interno: F({ acabamento: 'cromado', cor: 'brancoTitanio', desgaste: 0 }),
    }),
  }),
  madeiraClaraEAcoEscovado: F({
    nome: 'Madeira Clara e Aço Escovado',
    zonas: F({
      corpo: F({ acabamento: 'escovado', cor: 'brancoTitanio', desgaste: 0.08 }),
      guarnicao: F({ acabamento: 'madeira', cor: 'areia', cor2: 'marromSiena', desgaste: 0.15 }),
      carregador: F({ acabamento: 'escovado', cor: 'cinzaGrafite', desgaste: 0.12 }),
      detalhes: F({ acabamento: 'escovado', cor: 'cinzaGrafite', desgaste: 0.15 }),
      interno: F({ acabamento: 'escovado', cor: 'brancoTitanio', desgaste: 0 }),
    }),
  }),
});
