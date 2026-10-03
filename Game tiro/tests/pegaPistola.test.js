// A pega de pistola (Fase 4.1c; desenho, seção 4.2; plano, Tarefa 11): as duas mãos com os polegares para a frente, os
// dois do lado esquerdo da arma (os `lados` da 4.1b nas duas mãos), a mão de apoio encostada na do gatilho — a luva com a
// luva: nenhuma das duas mais de luvaPenetracaoMM dentro da outra e os quatro dedos de apoio a até contatoMM da luva do
// gatilho (`contatosLuvaMM`) — e os dois polegares a pelo menos folgaFerrolhoMM do ferrolho, que recua no tiro
// (`folgaFerrolhoMM`). O indicador do gatilho fica indexado: reto na lateral da armação, fora do guarda-mato (decisão do
// usuário de 2026-10-02: os polegares retos para a frente; o dedo no gatilho é da animação do tiro).
import { test } from 'node:test';
import assert from 'node:assert/strict';
import {
  CATEGORIAS_COM_PEGA, DEDOS_DA_FRENTE, DUAS_MAOS_DA_CATEGORIA, FRENTE_DA_CATEGORIA, INDEXADO_DA_CATEGORIA,
  LIMITES_DA_PEGA, MAOS_DA_CATEGORIA, OSSOS_DE_DEDO, ossosDoLado,
} from '../src/data/luvas.js';
import { lerPega } from '../src/characters/hands/pega.js';
import { validarPega } from '../tools/blender/saidaPega.mjs';

const MARCA = { d: 'c'.repeat(64), e: 'd'.repeat(64) };
// a palma que cede (4.1c): o afundamento da palma de cada mão no .glb (mm, no referencial do braço com o osso mao em
// repouso) e o resumo dele no relatório — a mão do gatilho com a tenar e o meio da palma no punho e na cauda
const PALMA = {
  d: { vertices: [30, 31, 77], vetores: [[0, 0, 3.4], [0, 0.2, 2.1], [0, 0, 0.8]] },
  e: { vertices: [30, 32], vetores: [[0, 0, 1.6], [0, 0, 0.3]] },
};

/** O glTF da pega das duas mãos (os nós `pega_mao_*` e as trilhas dos 17 ossos de dedo de cada uma). */
function gltfPistola() {
  const luvas = { marca: MARCA, sondas: { d: {}, e: {} }, maos: ['d', 'e'], palma: PALMA };
  const nodes = [{ name: 'glock', children: [1] }, { name: 'pega', extras: { luvas: JSON.stringify(luvas) }, children: [] }];
  for (const lado of ['d', 'e']) {
    nodes.push({ name: `pega_mao_${lado}`, translation: [0, 0, 0], rotation: [0, 0, 0, 1] });
    nodes[1].children.push(nodes.length - 1);
  }
  nodes.push({ name: 'pega_luvas', children: [] });
  const arm = nodes.length - 1;
  nodes[1].children.push(arm);
  const channels = [];
  for (const lado of ['d', 'e']) {
    for (const nome of ossosDoLado(lado)) {
      nodes.push({ name: nome, rotation: [0, 0, 0, 1] });
      nodes[arm].children.push(nodes.length - 1);
      if (OSSOS_DE_DEDO.includes(nome.slice(0, -2))) channels.push({ sampler: 0, target: { node: nodes.length - 1, path: 'rotation' } });
    }
  }
  return { scene: 0, scenes: [{ nodes: [0] }], nodes, animations: [{ name: 'empunhadura', channels, samplers: [{ input: 0, output: 1 }] }] };
}

// os contatos com a arma (as sondas que o `luvas_contato` mede no jogo) e os com a outra luva: o polegar do gatilho
// deitado sobre o de apoio, e os quatro dedos de apoio por cima dos da mão do gatilho
const GATILHO = {
  penetracaoMM: 0.05, contatosMM: { palma: 0.04, medio: 0.1, anelar: 0.2, minimo: 0.3, indicador: 0.4 },
  juntosMM: { 'medio-anelar': [2.4, 3.1], 'anelar-minimo': [2.6, 3.0] },
  lados: { polegarMM: 16.2, dedosMM: {} }, folgaFerrolhoMM: 3.4, penetracaoLuvaMM: 0.05, contatosLuvaMM: { polegar: 0.3 },
  polegar: { curvaGraus: 9.5, trechosMM: [4.1, 2.6, 1.2, 0.4, 0.1, 0.3], desvioDoEixoGraus: 8.2 },
  // o indicador indexado: a curva da PIP e da DIP, a folga de três trechos de cada falange até a armação (da proximal à
  // distal), a falange mais torta até o eixo da arma, a folga dele ao gatilho e ao ferrolho e a altura da falange média
  // e da distal acima do alto do gatilho
  indicador: {
    curvaGraus: 3.1, trechosMM: [2.2, 1.4, 0.8, 0.5, 0.3, 0.2, 0.4, 0.1, 0.05], desvioDoEixoGraus: 7.5,
    folgaGatilhoMM: 9.8, folgaFerrolhoMM: 3.1, acimaDoGatilhoMM: 5.4,
  },
  palma: { afundaMM: 3.4, vertices: 3, encostam: 2, alemMM: 0.05 },
};
const APOIO = {
  penetracaoMM: 0.05, contatosMM: { palma: 0.2, polegar: 0.5 },
  juntosMM: { 'indicador-medio': [1.2, 2], 'medio-anelar': [1.5, 2.2], 'anelar-minimo': [1.8, 2.4] },
  lados: { polegarMM: 14.1, dedosMM: {} }, folgaFerrolhoMM: 2.6, penetracaoLuvaMM: 0.04,
  contatosLuvaMM: { indicador: 0.3, medio: 0.2, anelar: 0.4, minimo: 0.6 },
  polegar: { curvaGraus: 12.4, trechosMM: [2.9, 2.7, 1.9, 0.9, 0.1, 0.05], desvioDoEixoGraus: 6.4 },
  palma: { afundaMM: 1.6, vertices: 2, encostam: 1, alemMM: 0 },
};

/** O relatório da pega de pistola com as trocas `d` e `e` por cima dos braços que passam. */
function relatorio({ d = {}, e = {} } = {}) {
  return { empunhadura: { maos: ['d', 'e'], d: { ...GATILHO, ...d }, e: { ...APOIO, ...e }, marca: MARCA } };
}

const problemas = (rel) => validarPega(rel, lerPega(gltfPistola()), MARCA, 'pistola');

test('pistola: as duas mãos, a do gatilho e a de apoio, sem mão da frente; e a regra no Blender', () => {
  assert.deepEqual(MAOS_DA_CATEGORIA.pistola, ['d', 'e']);
  assert.deepEqual(DUAS_MAOS_DA_CATEGORIA, { pistola: { gatilho: 'd', apoio: 'e' } });
  assert.equal(FRENTE_DA_CATEGORIA.pistola, undefined);
  assert.equal(LIMITES_DA_PEGA.luvaPenetracaoMM, 0.3);
  assert.equal(LIMITES_DA_PEGA.folgaFerrolhoMM, 2);
  assert.equal(LIMITES_DA_PEGA.polegarEixoGraus, 20);
  assert.equal(LIMITES_DA_PEGA.indexadoGatilhoMM, 5);
  assert.equal(LIMITES_DA_PEGA.indexadoAcimaMM, 0);
  assert.deepEqual(INDEXADO_DA_CATEGORIA, { pistola: 'd' });
  assert.ok(CATEGORIAS_COM_PEGA.includes('pistola'), 'a pistola com a regra no Blender (Tarefa 11)');
});

test('pistola: a pega que passa', () => {
  assert.deepEqual(problemas(relatorio()), []);
});

test('pistola: luva com luva — nenhuma das duas mais de 0,3 mm dentro da outra', () => {
  assert.match(problemas(relatorio({ e: { penetracaoLuvaMM: 0.5 } })).join('\n'), /empunhadura e: a luva entra 0,50 mm na luva d/);
  assert.match(problemas(relatorio({ d: { penetracaoLuvaMM: 0.4 } })).join('\n'), /empunhadura d: a luva entra 0,40 mm na luva e/);
  assert.match(problemas(relatorio({ e: { penetracaoLuvaMM: undefined } })).join('\n'), /e: sem a conta da luva com a luva/);
});

test('pistola: cada dedo de apoio encostado na luva do gatilho, a até 1 mm', () => {
  const longe = { ...APOIO.contatosLuvaMM, medio: LIMITES_DA_PEGA.contatoMM + 0.5 };
  assert.match(problemas(relatorio({ e: { contatosLuvaMM: longe } })).join('\n'), /o medio a 1,50 mm da luva d/);
  for (const d of DEDOS_DA_FRENTE) {
    const sem = { ...APOIO.contatosLuvaMM };
    delete sem[d];
    assert.match(problemas(relatorio({ e: { contatosLuvaMM: sem } })).join('\n'), new RegExp(`sem o contato do ${d}`), d);
  }
});

test('pistola: o polegar do gatilho deitado sobre o de apoio, a até 1 mm da luva', () => {
  assert.match(problemas(relatorio({ d: { contatosLuvaMM: { polegar: 1.4 } } })).join('\n'), /d: o polegar a 1,40 mm da luva e/);
  assert.match(problemas(relatorio({ d: { contatosLuvaMM: {} } })).join('\n'), /d: sem o contato do polegar com a luva e/);
});

test('pistola: os dois polegares retos e deitados (a curva, a distal encostando e a folga ao longo deles)', () => {
  const texto = (rel) => problemas(rel).join('\n');
  assert.match(texto(relatorio({ d: { polegar: { ...GATILHO.polegar, curvaGraus: 27.5 } } })),
    /empunhadura d: o polegar do gatilho com 27,50° de curva/);
  assert.match(texto(relatorio({ e: { polegar: { ...APOIO.polegar, curvaGraus: 23.2 } } })),
    /empunhadura e: o polegar de apoio com 23,20° de curva/);
  assert.match(texto(relatorio({ d: { polegar: { curvaGraus: 4, trechosMM: [9.1, 4.9, 3.3, 6.7, 13.9, 21.9] } } })),
    /d: a falange distal do polegar do gatilho não encosta[^\n]*6,70 mm/);
  assert.match(texto(relatorio({ e: { polegar: { curvaGraus: 4, trechosMM: [12.8, 9.6, 6.8, 4.2, 1.4, 0.5] } } })),
    /e: a falange proximal do polegar de apoio a 12,80 mm da arma no trecho 1/);
  assert.match(texto(relatorio({ e: { polegar: undefined } })), /e: sem a conferência do polegar deitado/);
});

test('pistola: os dois polegares apontando para a frente (a falange mais torta a até 20° do eixo da arma)', () => {
  const texto = (rel) => problemas(rel).join('\n');
  assert.match(texto(relatorio({ d: { polegar: { ...GATILHO.polegar, desvioDoEixoGraus: 38.2 } } })),
    /empunhadura d: o polegar do gatilho a 38,20° da frente da arma \(máximo 20°\): tem de apontar para a frente/);
  assert.match(texto(relatorio({ e: { polegar: { ...APOIO.polegar, desvioDoEixoGraus: 35.9 } } })),
    /empunhadura e: o polegar de apoio a 35,90° da frente da arma/);
  assert.match(texto(relatorio({ e: { polegar: { ...APOIO.polegar, desvioDoEixoGraus: undefined } } })),
    /e: sem a direção do polegar de apoio/);
  assert.deepEqual(problemas(relatorio({ d: { polegar: { ...GATILHO.polegar, desvioDoEixoGraus: 20 } } })), []);
});

test('pistola: o indicador do gatilho indexado — reto na armação, acima do guarda-mato, apontando para a frente', () => {
  const texto = (rel) => problemas(rel).join('\n');
  const ind = (troca) => relatorio({ d: { indicador: { ...GATILHO.indicador, ...troca } } });
  assert.match(texto(ind({ curvaGraus: 25 })), /empunhadura d: o indicador indexado com 25,00° de curva \(a PIP mais a DIP; máximo 20°\)/);
  assert.match(texto(ind({ trechosMM: [9.2, 1.4, 0.8, 0.5, 0.3, 0.2, 0.4, 0.1, 0.05] })),
    /d: a falange proximal do indicador indexado a 9,20 mm da armação no trecho 1/);
  assert.match(texto(ind({ trechosMM: [2.2, 1.4, 0.8, 0.5, 0.3, 0.2, 2.4, 1.9, 1.5] })),
    /d: a falange distal do indicador indexado não encosta na armação \(o trecho mais perto a 1,50 mm/);
  assert.match(texto(ind({ desvioDoEixoGraus: 31 })), /d: o indicador indexado a 31,00° da frente da arma \(máximo 20°\)/);
  assert.match(texto(ind({ folgaGatilhoMM: 3.5 })), /d: o indicador indexado a 3,50 mm do gatilho \(mínimo 5 mm: fora do guarda-mato\)/);
  assert.match(texto(ind({ folgaFerrolhoMM: 1.2 })), /d: o indicador indexado a 1,20 mm do ferrolho \(mínimo 2 mm/);
  // deitado na lateral do guarda-mato, com as folgas passando: a falange média e a distal abaixo do alto do gatilho
  assert.match(texto(ind({ acimaDoGatilhoMM: -22.9 })),
    /d: o indicador indexado a -22,90 mm do alto do gatilho \(mínimo 0 mm: acima do guarda-mato, na lateral da armação\)/);
  assert.match(texto(ind({ acimaDoGatilhoMM: undefined })), /d: sem a conferência do indicador indexado/);
  assert.match(texto(relatorio({ d: { indicador: undefined } })), /d: sem a conferência do indicador indexado/);
  // só na mão do gatilho: a de apoio não tem
  assert.doesNotMatch(texto(relatorio()), /indexado/);
});

test('pistola: os dois polegares a pelo menos 2 mm do ferrolho', () => {
  assert.match(problemas(relatorio({ d: { folgaFerrolhoMM: 1.5 } })).join('\n'), /empunhadura d: o polegar a 1,50 mm do ferrolho/);
  assert.match(problemas(relatorio({ e: { folgaFerrolhoMM: -0.2 } })).join('\n'), /empunhadura e: o polegar a -0,20 mm do ferrolho/);
  assert.match(problemas(relatorio({ e: { folgaFerrolhoMM: undefined } })).join('\n'), /e: sem a folga do polegar ao ferrolho/);
});

test('pistola: os dois polegares do lado esquerdo da arma (os lados nas duas mãos)', () => {
  assert.match(problemas(relatorio({ d: { lados: { polegarMM: 2, dedosMM: {} } } })).join('\n'), /empunhadura d: o polegar a 2,00 mm do meio/);
  assert.match(problemas(relatorio({ e: { lados: { polegarMM: -8, dedosMM: {} } } })).join('\n'), /empunhadura e: o polegar a -8,00 mm/);
  assert.match(problemas(relatorio({ d: { lados: undefined } })).join('\n'), /d: sem a conferência dos lados/);
});

test('pistola: a penetração na arma, os contatos e os dedos lado a lado continuam valendo', () => {
  assert.match(problemas(relatorio({ e: { penetracaoMM: 0.6 } })).join('\n'), /e: a luva entra 0,60 mm na arma/);
  assert.match(problemas(relatorio({ d: { contatosMM: { ...GATILHO.contatosMM, polegar: 1.8 } } })).join('\n'), /contato polegar a 1,80 mm/);
  assert.match(problemas(relatorio({ e: { juntosMM: { ...APOIO.juntosMM, 'medio-anelar': [9, 9] } } })).join('\n'), /leque/);
});

test('fuzil e faca não pedem as contas da pistola', () => {
  // o braço da mão do gatilho do fuzil, sem os campos da pistola, continua passando como antes
  const rifle = { empunhadura: { ...relatorio().empunhadura } };
  delete rifle.empunhadura.d.folgaFerrolhoMM;
  delete rifle.empunhadura.d.penetracaoLuvaMM;
  const sem = validarPega(rifle, lerPega(gltfPistola()), MARCA, 'rifle');
  assert.ok(!sem.some((p) => /ferrolho|luva com a luva/.test(p)), sem.join('\n'));
});
