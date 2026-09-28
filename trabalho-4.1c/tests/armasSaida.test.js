// Leitor e validador da saída do Blender (Fase 4.1a; desenho, seções 4.5, 4.6 e 9.1), com arquivos montados no teste:
// o .glb (cabeçalho, bloco JSON e bloco binário), o resumo por nível (peças, zonas, triângulos, tangentes, UV), os
// soquetes e o cabeçalho do .webp (VP8L sem perdas, VP8 com perdas, VP8X estendido). A AK de verdade é conferida em
// tests/armaAk47.test.js (Tarefa 8).
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { ladoWebp, lerGlb, resumoGlb } from '../tools/blender/saida.mjs';

/** Monta um .glb com o JSON e um binário (os dois alinhados a 4 bytes). */
function montarGlb(json, bin = Buffer.alloc(0)) {
  let j = Buffer.from(JSON.stringify(json), 'utf8');
  if (j.length % 4) j = Buffer.concat([j, Buffer.alloc(4 - (j.length % 4), 0x20)]);
  let b = bin;
  if (b.length % 4) b = Buffer.concat([b, Buffer.alloc(4 - (b.length % 4), 0)]);
  const cab = Buffer.alloc(12);
  cab.writeUInt32LE(0x46546c67, 0);
  cab.writeUInt32LE(2, 4);
  cab.writeUInt32LE(12 + 8 + j.length + (b.length ? 8 + b.length : 0), 8);
  const cj = Buffer.alloc(8);
  cj.writeUInt32LE(j.length, 0);
  cj.writeUInt32LE(0x4e4f534a, 4);
  const partes = [cab, cj, j];
  if (b.length) {
    const cb = Buffer.alloc(8);
    cb.writeUInt32LE(b.length, 0);
    cb.writeUInt32LE(0x004e4942, 4);
    partes.push(cb, b);
  }
  return Buffer.concat(partes);
}

/** Um glTF mínimo com a hierarquia da arma: 3 níveis × (base + ferrolho), soquetes e duas zonas. */
function gltfArma() {
  const accessors = [];
  const acessor = (count) => {
    accessors.push({ count, componentType: 5126, type: 'VEC3' });
    return accessors.length - 1;
  };
  const meshes = [];
  const malha = (tris, comTangente, mats) => {
    meshes.push({
      primitives: mats.map((material) => ({
        attributes: { POSITION: acessor(tris * 3), NORMAL: acessor(tris * 3), TEXCOORD_0: acessor(tris * 3), ...(comTangente ? { TANGENT: acessor(tris * 3) } : {}) },
        indices: acessor(tris * 3),
        material,
      })),
    });
    return meshes.length - 1;
  };
  const nodes = [{ name: 'ak47', children: [] }];
  const no = (def, pai) => {
    nodes.push(def);
    nodes[pai].children = [...(nodes[pai].children ?? []), nodes.length - 1];
    return nodes.length - 1;
  };
  for (const [lod, tris, tangente] of [['perto', 100, true], ['mundo', 20, false], ['longe', 5, false]]) {
    const l = no({ name: lod }, 0);
    no({ name: `${lod}_base`, mesh: malha(tris, tangente, [0, 1]) }, l);
    no({ name: `${lod}_ferrolho`, mesh: malha(tris / 5, tangente, [1]), translation: [1, 2, 3], extras: { eixo: [-1, 0, 0] } }, l);
  }
  const s = no({ name: 'soquetes' }, 0);
  no({ name: 'soquete_boca', translation: [21.69, 0, 0] }, s);
  no({ name: 'soquete_mao_d', translation: [-2, -3, 0.5], rotation: [0, 0, 0.7071068, 0.7071068] }, s);
  return {
    asset: { version: '2.0' }, scene: 0, scenes: [{ nodes: [0] }], nodes, meshes, accessors,
    materials: [{ name: 'corpo' }, { name: 'interno' }], animations: [{ name: 'empunhadura', channels: [], samplers: [] }],
  };
}

test('glb: cabeçalho, bloco JSON e bloco binário', () => {
  const bin = Buffer.from([1, 2, 3, 4, 5]);
  const { json, bin: b } = lerGlb(montarGlb({ asset: { version: '2.0' } }, bin));
  assert.deepEqual(json, { asset: { version: '2.0' } });
  assert.equal(b.length, 8, 'o binário vem com o preenchimento');
  assert.equal(b[4], 5);
  assert.throws(() => lerGlb(Buffer.from('nada disso aqui')), /não é um \.glb/);
});

test('glb: resumo por nível — peças, zonas, triângulos, tangentes, UV, extras, soquetes, animações e o Draco', () => {
  const r = resumoGlb(lerGlb(montarGlb(gltfArma())).json, 'ak47');
  assert.equal(r.raiz, 'ak47');
  assert.deepEqual(Object.keys(r.lods), ['perto', 'mundo', 'longe']);
  assert.equal(r.lods.perto.triangulos, 100 * 2 + 20);
  assert.equal(r.lods.mundo.triangulos, 20 * 2 + 4);
  assert.equal(r.lods.longe.triangulos, 5 * 2 + 1);
  assert.deepEqual(Object.keys(r.lods.perto.pecas), ['base', 'ferrolho']);
  assert.deepEqual(r.lods.perto.pecas.base.zonas, ['corpo', 'interno']);
  assert.deepEqual(r.lods.perto.pecas.ferrolho.extras, { eixo: [-1, 0, 0] });
  assert.deepEqual(r.lods.perto.pecas.ferrolho.posicao, [1, 2, 3]);
  assert.equal(r.lods.perto.tangentes, true);
  assert.equal(r.lods.mundo.tangentes, false);
  assert.equal(r.lods.perto.uv, true);
  assert.deepEqual(r.zonas, ['corpo', 'interno']);
  assert.deepEqual(Object.keys(r.soquetes), ['boca', 'mao_d']);
  assert.deepEqual(r.soquetes.boca.posicao, [21.69, 0, 0]);
  assert.deepEqual(r.soquetes.mao_d.rotacao, [0, 0, 0.7071068, 0.7071068]);
  assert.deepEqual(r.animacoes, ['empunhadura']);
  assert.equal(r.draco, false);
  assert.equal(resumoGlb({ ...gltfArma(), extensionsUsed: ['KHR_draco_mesh_compression'] }, 'ak47').draco, true);
  const alfabetica = gltfArma();
  alfabetica.nodes[0].children.reverse();
  assert.deepEqual(Object.keys(resumoGlb(alfabetica, 'ak47').lods), ['perto', 'mundo', 'longe'], 'a ordem do registro, não a do arquivo');
  assert.throws(() => resumoGlb(gltfArma(), 'm4a4'), /a raiz do \.glb é ak47, esperava m4a4/);
});

test('webp: VP8L sem perdas, VP8 com perdas e VP8X estendido', () => {
  const riff = (fourcc, dados) => {
    const cab = Buffer.alloc(12);
    cab.write('RIFF', 0, 'ascii');
    cab.writeUInt32LE(4 + 8 + dados.length, 4);
    cab.write('WEBP', 8, 'ascii');
    const ch = Buffer.alloc(8);
    ch.write(fourcc, 0, 'ascii');
    ch.writeUInt32LE(dados.length, 4);
    return Buffer.concat([cab, ch, dados]);
  };
  const l = Buffer.alloc(5);
  l[0] = 0x2f;
  l.writeUInt32LE(((2048 - 1) | ((2048 - 1) << 14) | (1 << 28)) >>> 0, 1);
  assert.deepEqual(ladoWebp(riff('VP8L', l)), { largura: 2048, altura: 2048, semPerdas: true, alfa: true });
  const v = Buffer.alloc(10);
  v[3] = 0x9d;
  v[4] = 0x01;
  v[5] = 0x2a;
  v.writeUInt16LE(512, 6);
  v.writeUInt16LE(256, 8);
  assert.deepEqual(ladoWebp(riff('VP8 ', v)), { largura: 512, altura: 256, semPerdas: false, alfa: false });
  const x = Buffer.alloc(10);
  x[0] = 0x10; // bit do alfa
  x.writeUIntLE(1024 - 1, 4, 3);
  x.writeUIntLE(1024 - 1, 7, 3);
  const estendido = Buffer.concat([riff('VP8X', x), Buffer.from('VP8L'), Buffer.from([5, 0, 0, 0]), l]);
  estendido.writeUInt32LE(estendido.length - 8, 4);
  assert.deepEqual(ladoWebp(estendido), { largura: 1024, altura: 1024, semPerdas: true, alfa: true });
  assert.throws(() => ladoWebp(Buffer.from('RIFF0000WAVEfmt ')), /não é um \.webp/);
});
