// O modelo das dobras em JS (Fase 4.1b; plano, Tarefa 9) contra o do Blender: montado do luvas.glb de verdade como o
// jogo monta (as primitivas casadas pelo `_VERTICE`, o esqueleto pelas matrizes de ligação inversas, as correções dos
// extras), avaliado nas poses da prova do relatório (os giros no referencial do braço) e comparado com as posições que o
// Blender gravou, nos dois braços — a mesma tolerância do `luvas_contato` (0,05 mm; a posição do glTF vem do Draco em
// 14 bits). E as contas puras: o skin sem giro devolve o repouso, as juntas em repouso não mexem, as peças presas.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import { LIMITES_DA_PEGA, LUVAS } from '../src/data/luvas.js';
import { deBlender, normaisDosVertices } from '../src/characters/hands/modeloDobras.js';
import { lerGlb } from '../tools/blender/saida.mjs';
import { RAIZ, decodificadorDraco, modeloDoGlb, primitivaDraco } from './luvasTestUtils.js';

const PASTA = join(RAIZ, LUVAS.pasta);

async function montar() {
  const { json, bin } = lerGlb(readFileSync(join(PASTA, 'luvas.glb')));
  const relatorio = JSON.parse(readFileSync(join(PASTA, 'luvas.relatorio.json'), 'utf8'));
  const draco = await decodificadorDraco();
  return { json, bin, relatorio, draco };
}

test('modelo das dobras: o JS casa com o Blender nas poses da prova, nos dois braços (≤ 0,05 mm)', async () => {
  const { json, bin, relatorio, draco } = await montar();
  assert.ok(relatorio.provaDoModelo, 'o relatório das luvas sem a prova do modelo: construa as luvas de novo');
  for (const lado of ['d', 'e']) {
    const modelo = modeloDoGlb(draco, json, bin, `luva_${lado}`);
    const prova = relatorio.provaDoModelo[lado];
    assert.equal(modelo.malha.n, relatorio.vertices, `${lado}: vértices`);
    for (const [pose, dados] of Object.entries(prova.poses)) {
      const giros = {};
      for (const [osso, g] of Object.entries(dados.giros)) giros[`${osso}_${lado}`] = [...deBlender(g.slice(0, 3)), g[3]];
      const pts = modelo.avaliar(modelo.deformacoesDosGiros(giros));
      let pior = 0;
      let onde = -1;
      prova.vertices.forEach((v, k) => {
        const esperado = deBlender(dados.mm[k]);
        const d = Math.hypot(pts[v * 3] - esperado[0], pts[v * 3 + 1] - esperado[1], pts[v * 3 + 2] - esperado[2]);
        if (d > pior) {
          pior = d;
          onde = v;
        }
      });
      assert.ok(pior <= LIMITES_DA_PEGA.contatoJogoMM, `${lado}, pose ${pose}: o vértice ${onde} a ${pior.toFixed(4)} mm do Blender`);
    }
  }
});

test('modelo das dobras: sem giro, a malha fica no repouso (as peças a menos de 0,02 mm) e as normais batem com as do Blender', async () => {
  const { json, bin, draco } = await montar();
  const modelo = modeloDoGlb(draco, json, bin, 'luva_d');
  const pts = modelo.avaliar(modelo.deformacoesDosGiros({}));
  let pior = 0;
  for (let i = 0; i < pts.length; i++) pior = Math.max(pior, Math.abs(pts[i] - modelo.malha.repouso[i]));
  // a base fica exata; as peças são sempre reassentadas na base (como no Blender), e a posição do Draco é quantizada
  assert.ok(pior < 0.02, `repouso a ${pior} mm`);
  // as normais do modelo (pela área dos triângulos, por vértice do Blender) contra as que o Blender exportou (o NORMAL
  // do glTF, igual nos vértices duplicados das costuras): o mesmo sentido (o giro dos triângulos certo) e quase a
  // mesma direção
  const vn = normaisDosVertices(pts, modelo.malha.triangulos, modelo.malha.n);
  const no = json.nodes.find((n) => n.name === 'luva_d');
  let soma = 0;
  let conta = 0;
  let contra = 0;
  for (const p of json.meshes[no.mesh].primitives) {
    const d = primitivaDraco(draco, json, bin, p, ['NORMAL', '_VERTICE']);
    for (let k = 0; k < d._VERTICE.length; k++) {
      const v = Math.round(d._VERTICE[k]);
      const c = d.NORMAL[k * 3] * vn[v * 3] + d.NORMAL[k * 3 + 1] * vn[v * 3 + 1] + d.NORMAL[k * 3 + 2] * vn[v * 3 + 2];
      soma += c;
      conta++;
      if (c < 0) contra++;
    }
  }
  assert.ok(soma / conta > 0.95, `as normais do modelo a ${(soma / conta).toFixed(3)} de cosseno médio das do Blender`);
  assert.ok(contra / conta < 0.01, `${contra} normais do modelo contra as do Blender`);
});
