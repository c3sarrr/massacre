// Acabamentos das skins das armas realistas (Fase 4.1a; desenho em docs/superpowers/specs/2026-09-26-armas-realistas-
// design.md, seção 6.1; referências QCK2/5/7/10/13 e QRL2/5/8/11 no item 14 do moodboard): cada um com os parâmetros do
// material físico (MeshPhysicalMaterial) e o padrão procedural que o trecho de shader das armas desenha por cima
// (src/weapons/model/glsl/acabamentos.js). `gasto` é o que o desgaste mostra por baixo, pelo canal de borda (_m.b): o
// metal nu nas pinturas, o aço claro nos metais, a madeira lixada, o plástico raspado. `varAspereza` e `varCor` dosam o
// quanto a variação assada (_m.g e _m.a, em torno de 0,5) mexe na aspereza e na cor. `verniz` liga a camada de verniz
// (clearcoat), `iridescencia` o filme fino, `anisotropia` o escovado ao longo do X da arma — só quando o acabamento
// pede, para limitar as variantes de shader. `cor2Fator` faz a segunda cor (veio, trama) quando a skin não traz uma.

const F = Object.freeze;

// Padrões procedurais do shader, na ordem do define ARMA_PADRAO.
export const PADROES = F(['nenhum', 'fino', 'granulado', 'flocos', 'carbono', 'veio', 'pontilhado', 'ceramica']);

const NU = F({ cor: '#8F959C', metal: 1, aspereza: 0.32 }); // aço nu debaixo da tinta

export const ACABAMENTOS = F({
  oxidado: F({ nome: 'Oxidado de fábrica', metal: 1, aspereza: 0.34, padrao: 'fino', varAspereza: 0.16, varCor: 0.06, gasto: F({ cor: '#A7ABB0', metal: 1, aspereza: 0.2 }) }),
  fosfatizado: F({ nome: 'Fosfatizado', metal: 1, aspereza: 0.55, padrao: 'granulado', varAspereza: 0.14, varCor: 0.05, gasto: F({ cor: '#9CA0A6', metal: 1, aspereza: 0.26 }) }),
  fosco: F({ nome: 'Fosco', metal: 0, aspereza: 0.85, padrao: 'nenhum', varAspereza: 0.06, varCor: 0.04, gasto: NU }),
  acetinado: F({ nome: 'Acetinado', metal: 0, aspereza: 0.5, padrao: 'nenhum', varAspereza: 0.06, varCor: 0.04, gasto: NU }),
  brilhante: F({ nome: 'Brilhante', metal: 0, aspereza: 0.25, verniz: 1, asperezaVerniz: 0.05, padrao: 'nenhum', varAspereza: 0.04, varCor: 0.03, gasto: NU }),
  metalico: F({ nome: 'Metálico', metal: 0.6, aspereza: 0.35, verniz: 0.8, asperezaVerniz: 0.08, padrao: 'flocos', varAspereza: 0.05, varCor: 0.03, gasto: NU }),
  perolado: F({
    nome: 'Perolado', metal: 0.2, aspereza: 0.3, verniz: 1, asperezaVerniz: 0.06, iridescencia: 0.8, iorIridescencia: 1.3,
    filme: F([250, 600]), padrao: 'nenhum', varAspereza: 0.04, varCor: 0.03, gasto: NU,
  }),
  anodizado: F({
    nome: 'Anodizado', metal: 1, aspereza: 0.25, iridescencia: 0.2, iorIridescencia: 1.3, filme: F([250, 600]), padrao: 'fino',
    varAspereza: 0.08, varCor: 0.04, gasto: F({ cor: '#C9CCD0', metal: 1, aspereza: 0.2 }),
  }),
  escovado: F({ nome: 'Aço escovado', metal: 1, aspereza: 0.3, anisotropia: 0.8, padrao: 'nenhum', varAspereza: 0.06, varCor: 0.03, gasto: F({ cor: '#B8BBBF', metal: 1, aspereza: 0.18 }) }),
  cromado: F({ nome: 'Cromado', metal: 1, aspereza: 0.05, padrao: 'nenhum', varAspereza: 0.03, varCor: 0.02, gasto: NU }),
  cerakote: F({ nome: 'Cerakote', metal: 0, aspereza: 0.7, padrao: 'ceramica', varAspereza: 0.08, varCor: 0.04, gasto: NU }),
  carbono: F({
    nome: 'Fibra de carbono', metal: 0, aspereza: 0.35, verniz: 1, asperezaVerniz: 0.05, padrao: 'carbono', duasCores: true, cor2Fator: 2.2,
    varAspereza: 0.04, varCor: 0.03, gasto: F({ cor: '#3A3C40', metal: 0, aspereza: 0.6 }),
  }),
  madeira: F({
    nome: 'Madeira', metal: 0, aspereza: 0.45, verniz: 0.6, asperezaVerniz: 0.18, padrao: 'veio', duasCores: true, cor2Fator: 0.45,
    varAspereza: 0.1, varCor: 0.3, gasto: F({ cor: '#C49A6C', metal: 0, aspereza: 0.62 }),
  }),
  polimero: F({ nome: 'Polímero texturizado', metal: 0, aspereza: 0.65, padrao: 'pontilhado', varAspereza: 0.08, varCor: 0.05, gasto: F({ cor: '#6E7074', metal: 0, aspereza: 0.8 }) }),
  borracha: F({ nome: 'Borracha', metal: 0, aspereza: 0.9, padrao: 'nenhum', varAspereza: 0.05, varCor: 0.04, gasto: F({ cor: '#55575B', metal: 0, aspereza: 0.95 }) }),
});
