// Registro das receitas das armas de massinha (Fase 4.1; formato em docs/phases/phase-4.md, seção 4.1, "Receita").
// Cada arquivo desta pasta é gravado pelo exportador do Blender (tools/blender/massacre_armas.py) e lido pelo
// gerador (src/weapons/model/); a ordem aqui é a da bancada `arsenal` e do comando `armas`.
// As outras 18 armas de fogo e a faca de ouro entram na 4.4; as granadas na 4.7.

import glock from './glock.js';
import ak47 from './ak47.js';
import m4a4 from './m4a4.js';
import awp from './awp.js';
import nova from './nova.js';
import p90 from './p90.js';
import knife from './knife.js';

export const ARMAS = Object.freeze({ glock, ak47, m4a4, awp, nova, p90, knife });
