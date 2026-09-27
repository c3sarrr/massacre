// Registro das receitas das armas de massinha (Fase 4.1; formato em docs/phases/phase-4.md, seção 4.1, "Receita").
// Cada arquivo desta pasta é gravado pelo exportador do Blender (tools/blender/massacre_armas.py) e lido pelo
// gerador (src/weapons/model/); a ordem aqui é a do comando `armas`.
// Na troca para as armas realistas (docs/superpowers/specs/2026-09-26-armas-realistas-design.md, seção 8.2), cada arma
// refeita no Blender sai daqui e entra em src/data/armasReais.js: a AK-47 na 4.1a; a Glock-18, a M4A4 e a faca na
// 4.1c; a AWP, a Nova e a P90 na 4.1d, quando esta pasta e o gerador de massinha das armas saem de vez.

import glock from './glock.js';
import m4a4 from './m4a4.js';
import awp from './awp.js';
import nova from './nova.js';
import p90 from './p90.js';
import knife from './knife.js';

export const ARMAS = Object.freeze({ glock, m4a4, awp, nova, p90, knife });
