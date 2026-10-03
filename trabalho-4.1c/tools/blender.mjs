// Editor de armas no Blender (Fase 4.1; docs/phases/phase-4.md, seção 4.1, "Blender"):
//
//   npm run blender -- abrir <arma>          Blender com janela, a arma montada e o painel "MASSACRE" (tecla N)
//   npm run blender -- conferir <arma|todas> renders sem janela em tools/blender/conferencia/<arma>/
//   npm run blender -- ida-volta <arma|todas> importa e exporta sem janela e compara com a receita (a prova do caminho)
//   npm run blender -- validar <arquivo.js>   a validação do jogo numa receita (o exportador chama antes de gravar)
//   npm run blender -- previa <arquivo.js> <saída>  a malha que o jogo gera de uma receita (o painel do Blender chama)
//
// Armas realistas (Fase 4.1a; as de src/data/armasReais.js, construídas por tools/blender/armas/principal.py):
//   npm run blender -- construir <arma|todas> [--forcar]  modelo, assar, LODs, validar e exportar em assets/armas/<arma>/
//                                                         (pula a arma quando o hash das entradas não mudou)
//   npm run blender -- validar <arma|todas>   refaz a validação na .blend gravada e confere os arquivos exportados
//   npm run blender -- conferir <arma|todas>  renders em tools/blender/conferencia/<arma>/ (as de massinha, como acima)
//   npm run blender -- abrir <arma>           abre a .blend da conferência (as de massinha, como acima)
//
// Luvas (Fase 4.1b; tools/blender/armas/luvas.py, a ficha em tools/blender/refs/luvas.json): o alvo `luvas` nas mesmas
// quatro ações (construir, validar, conferir, abrir); `todas` no construir e no validar começa pelas luvas.
//
// Peças da biblioteca (Fase 4.1c; tools/blender/armas/provas_pecas.py):
//   npm run blender -- provar pecas           constrói cada peça nova sozinha e confere as medidas (reprova com código 1)
//
// Prepara o contexto que o Blender não sabe calcular sozinho — a paleta das massas, o acento da facção, a planta de
// referência, a mão de massinha em cada pose (o próprio rig do jogo, src/characters/hands/) e, para abrir e conferir,
// a prévia do jogo (tools/blender/previa.mjs: a malha que o jogo gera, com as mãos e a câmera do viewmodel) — em
// arquivos temporários.
// O executável vem de BLENDER_PATH, de tools/blender/local.json ({"blender": "caminho"}, fora do git) ou das pastas de
// instalação conhecidas.

import { spawn, spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { existsSync, mkdirSync, readFileSync, readdirSync, rmSync, writeFileSync } from 'node:fs';
import { homedir, platform, tmpdir } from 'node:os';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import * as THREE from 'three';
import { gerarPrevia } from './blender/previa.mjs';
import { validarSaida } from './blender/saida.mjs';
import { validarSaidaLuvas } from './blender/saidaLuvas.mjs';
import { LUVAS } from '../src/data/luvas.js';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const SCRIPT = join(ROOT, 'tools', 'blender', 'massacre_armas.py');
const SCRIPT_REAIS = join(ROOT, 'tools', 'blender', 'armas', 'principal.py');
const SCRIPT_PROVAS = join(ROOT, 'tools', 'blender', 'armas', 'provas_pecas.py');
const TMP = join(tmpdir(), 'massacre-blender');

function blenderExe() {
  const ok = (p) => p && existsSync(p);
  if (process.env.BLENDER_PATH) {
    if (ok(process.env.BLENDER_PATH)) return process.env.BLENDER_PATH;
    throw new Error(`BLENDER_PATH aponta para um arquivo que não existe: ${process.env.BLENDER_PATH}`);
  }
  const local = join(ROOT, 'tools', 'blender', 'local.json');
  if (existsSync(local)) {
    const exe = JSON.parse(readFileSync(local, 'utf8')).blender;
    if (ok(exe)) return exe;
    throw new Error(`tools/blender/local.json aponta para um arquivo que não existe: ${exe}`);
  }
  const candidatos = [];
  if (platform() === 'win32') {
    for (const base of [process.env.ProgramFiles, process.env['ProgramFiles(x86)'], 'C:\\Program Files']) {
      const dir = base && join(base, 'Blender Foundation');
      if (dir && existsSync(dir)) {
        const versoes = readdirSync(dir).filter((n) => /^Blender/i.test(n)).sort((a, b) => b.localeCompare(a, 'en', { numeric: true }));
        for (const v of versoes) candidatos.push(join(dir, v, 'blender.exe'));
      }
    }
    candidatos.push('C:\\Program Files (x86)\\Steam\\steamapps\\common\\Blender\\blender.exe');
  } else if (platform() === 'darwin') {
    candidatos.push('/Applications/Blender.app/Contents/MacOS/Blender', join(homedir(), 'Applications/Blender.app/Contents/MacOS/Blender'));
  } else {
    candidatos.push('/usr/bin/blender', '/usr/local/bin/blender', '/snap/bin/blender', join(homedir(), '.local/bin/blender'));
  }
  const achado = candidatos.find(ok);
  if (achado) return achado;
  const noPath = spawnSync('blender', ['--version'], { encoding: 'utf8' });
  if (noPath.status === 0) return 'blender';
  throw new Error('Blender não encontrado: defina BLENDER_PATH ou crie tools/blender/local.json com {"blender": "caminho do executável"}');
}

/** A mão de massinha em cada pose, no referencial da mão (pulso na origem), pelo rig do jogo. */
async function maosPorPose() {
  const { HAND_POSES } = await import('../src/data/hands.js');
  const { ClayArm, sideBones } = await import('../src/characters/hands/handRig.js');
  const out = {};
  for (const side of ['direita', 'esquerda']) {
    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute('position', new THREE.Float32BufferAttribute([0, 0, 0], 3));
    geometry.setAttribute('skinIndex', new THREE.Uint16BufferAttribute([0, 0, 0, 0], 4));
    geometry.setAttribute('skinWeight', new THREE.Float32BufferAttribute([1, 0, 0, 0], 4));
    const arm = new ClayArm({ geometry, side, color: '#C8553D' });
    const defs = sideBones(side).filter((d) => d.name !== 'antebraco');
    out[side] = {};
    for (const pose of Object.keys(HAND_POSES)) {
      arm.setPose(pose);
      arm.place(new THREE.Vector3(0, 0, 0), new THREE.Quaternion(), new THREE.Vector3(-11, 0, 0));
      arm.mesh.updateMatrixWorld(true);
      out[side][pose] = defs.map((d) => {
        const m = arm.bones[d.name].matrixWorld;
        const len = Math.hypot(d.tail[0] - d.head[0], d.tail[1] - d.head[1], d.tail[2] - d.head[2]);
        const r4 = (v) => Math.round(v * 1e4) / 1e4;
        return {
          name: d.name,
          head: new THREE.Vector3().setFromMatrixPosition(m).toArray().map(r4),
          tail: new THREE.Vector3(len, 0, 0).applyMatrix4(m).toArray().map(r4),
          radius: d.radius,
        };
      });
    }
    arm.dispose();
    geometry.dispose();
  }
  return out;
}

async function contexto(id, { comPrevia = false } = {}) {
  const { ARMAS } = await import('../src/data/armas/index.js');
  if (!ARMAS[id]) throw new Error(`arma sem receita: ${id} (tem: ${Object.keys(ARMAS).join(', ')})`);
  const { WEAPON_CLAYS, FACTION_ACCENTS } = await import('../src/data/weaponPalette.js');
  const { PALETTE } = await import('../src/data/palette.js');
  const { weaponFaction } = await import('../src/weapons/model/recipe.js');
  const refPath = join(ROOT, 'tools', 'blender', 'refs', `${id}.json`);
  const { plantaDoArquivo } = await import('../src/weapons/model/ficha.js');
  const planta = existsSync(refPath) ? plantaDoArquivo(JSON.parse(readFileSync(refPath, 'utf8'))) : null;
  const ctx = {
    id,
    raiz: ROOT,
    receita: join(ROOT, 'src', 'data', 'armas', `${id}.js`),
    faccao: weaponFaction(id),
    massas: WEAPON_CLAYS,
    acentos: FACTION_ACCENTS,
    corMao: PALETTE.terracotta,
    maos: await maosPorPose(),
    planta: planta && { points: planta.points, holes: planta.holes ?? [] },
    pasta: join(ROOT, 'tools', 'blender', 'conferencia', id),
    node: process.execPath,
    ferramenta: fileURLToPath(import.meta.url),
    previa: null,
  };
  mkdirSync(TMP, { recursive: true });
  if (comPrevia) ctx.previa = (await gerarPrevia(ARMAS[id], join(TMP, `${id}-previa`))).json;
  const arquivo = join(TMP, `${id}-contexto.json`);
  writeFileSync(arquivo, JSON.stringify(ctx));
  return arquivo;
}

function rodarSemJanela(args, script = SCRIPT) {
  const res = spawnSync(blenderExe(), ['--background', '--factory-startup', '--python-exit-code', '1', '--python', script, '--', ...args], {
    encoding: 'utf8', maxBuffer: 64 * 1024 * 1024,
  });
  if (res.status !== 0) {
    throw new Error(`o Blender falhou (código ${res.status}):\n${(res.stdout ?? '').split('\n').slice(-25).join('\n')}\n${res.stderr ?? ''}`);
  }
  return res.stdout;
}

/** A receita de um arquivo (sem o cache de módulos: o mesmo caminho pode ter mudado). */
async function lerReceita(arquivo) {
  const url = pathToFileURL(resolve(arquivo));
  url.searchParams.set('v', String(Date.now()));
  return (await import(url.href)).default;
}

async function validar(arquivo) {
  const { validateRecipe } = await import('../src/weapons/model/recipe.js');
  const recipe = validateRecipe(await lerReceita(arquivo));
  return `receita de ${recipe.id} válida (${recipe.parts.length} peças)`;
}

async function previa(arquivo, saida) {
  const { json, triangulos, ms } = await gerarPrevia(await lerReceita(arquivo), resolve(saida));
  return `MASSACRE-PREVIA ${json} (${triangulos} triângulos, ${ms} ms)`;
}

async function idaVolta(id) {
  const ctx = await contexto(id);
  const saida = join(TMP, `${id}-ida-volta.js`);
  rmSync(saida, { force: true });
  rodarSemJanela(['ida-volta', ctx, saida]);
  await validar(saida);
  const original = readFileSync(join(ROOT, 'src', 'data', 'armas', `${id}.js`), 'utf8');
  const volta = readFileSync(saida, 'utf8');
  if (original === volta) return `${id}: ida e volta idêntica (${original.length} bytes)`;
  const a = original.split('\n');
  const b = volta.split('\n');
  const i = a.findIndex((linha, k) => linha !== b[k]);
  throw new Error(`${id}: a volta difere na linha ${i + 1}:\n  receita: ${a[i]?.slice(0, 240)}\n  volta:   ${b[i]?.slice(0, 240)}`);
}

async function conferir(id) {
  const ctx = await contexto(id, { comPrevia: true });
  const out = rodarSemJanela(['conferir', ctx]);
  const linha = out.split('\n').find((l) => l.startsWith('MASSACRE-CONFERIR '));
  const arquivos = linha ? JSON.parse(linha.slice('MASSACRE-CONFERIR '.length)) : [];
  return `${id}: ${arquivos.length} vistas em ${join('tools', 'blender', 'conferencia', id)}`;
}

async function abrir(id) {
  const ctx = await contexto(id, { comPrevia: true });
  const filho = spawn(blenderExe(), ['--python', SCRIPT, '--', 'abrir', ctx], { detached: true, stdio: 'ignore' });
  filho.unref();
  return `Blender aberto com ${id} (painel "MASSACRE" na barra lateral da vista 3D, tecla N)`;
}

/**
 * Como rodarSemJanela, mas mostra as etapas (`MASSACRE-ETAPA`) e os avisos (`MASSACRE-AVISO`) enquanto o Blender
 * trabalha: o construir leva minutos.
 * Devolve a saída inteira; com código diferente de zero lança com as últimas linhas, como o rodarSemJanela.
 */
function rodarComEtapas(args, script, rotulo) {
  return new Promise((aoTerminar, aoFalhar) => {
    const filho = spawn(blenderExe(), ['--background', '--factory-startup', '--python-exit-code', '1', '--python', script, '--', ...args], {
      stdio: ['ignore', 'pipe', 'pipe'],
    });
    let saida = '';
    let erro = '';
    let resto = '';
    filho.stdout.setEncoding('utf8');
    filho.stderr.setEncoding('utf8');
    filho.stdout.on('data', (pedaco) => {
      saida += pedaco;
      const linhas = (resto + pedaco).split('\n');
      resto = linhas.pop();
      for (const linha of linhas) {
        // os avisos (a avaliação ruim do booleano refeita, tools/blender/armas/canonica.py) aparecem como chegam
        if (linha.startsWith('MASSACRE-AVISO ')) console.log(`  ${rotulo} · aviso: ${linha.slice('MASSACRE-AVISO '.length).trim()}`);
        if (!linha.startsWith('MASSACRE-ETAPA ')) continue;
        const { etapa, s } = JSON.parse(linha.slice('MASSACRE-ETAPA '.length));
        console.log(`  ${rotulo} · ${etapa} (${s} s)`);
      }
    });
    filho.stderr.on('data', (pedaco) => {
      erro += pedaco;
    });
    filho.on('error', aoFalhar);
    filho.on('close', (codigo) => {
      if (codigo === 0) aoTerminar(saida);
      else aoFalhar(new Error(`o Blender falhou (código ${codigo}):\n${saida.split('\n').slice(-25).join('\n')}\n${erro}`));
    });
  });
}

/**
 * Hash das entradas de uma arma realista (os .py do pacote, a ficha e o registro da arma; plano da 4.1a, D14) ou das
 * luvas (os .py e a ficha delas, com `def` nulo).
 */
function hashEntradas(id, def, ficha) {
  const h = createHash('sha256');
  const pasta = join(ROOT, 'tools', 'blender', 'armas');
  for (const nome of readdirSync(pasta).filter((n) => n.endsWith('.py')).sort()) {
    h.update(nome);
    h.update(readFileSync(join(pasta, nome), 'utf8').replace(/\r\n/g, '\n'));
  }
  h.update(JSON.stringify(ficha));
  h.update(JSON.stringify({ id, def }));
  return h.digest('hex');
}

/** Contexto de uma arma realista para o principal.py: ficha validada, pintura de fábrica, orçamento, pastas, hash. */
async function contextoReal(id, { forcar = false } = {}) {
  const { ARMAS_REAIS, armaComPega, classeDaArma, medidasDaArma, orcamentoDaArma, soquetesDaArma, zonasDaArma } = await import('../src/data/armasReais.js');
  const { validarFicha } = await import('../src/weapons/model/ficha.js');
  // Os tipos do relevo moldado (correções da P1 da 4.1c): o Blender desenha e assa os mesmos números que o shader usa;
  // e a conta do veio da madeira, a mesma do jogo (o brilho que acompanha o veio é a `varCor` da madeira).
  const { ACABAMENTOS, RELEVOS_MOLDADOS } = await import('../src/data/acabamentos.js');
  const veio = { ...ACABAMENTOS.madeira.veio, brilho: ACABAMENTOS.madeira.varCor };
  // As texturas CC0 do Blender (o registro tem o md5 de cada arquivo): trocar uma refaz as armas.
  const texturas = JSON.parse(readFileSync(join(ROOT, 'tools', 'blender', 'texturas', 'fontes.json'), 'utf8'));
  const def = ARMAS_REAIS[id];
  if (!def) throw new Error(`${id} não é uma arma realista (tem: ${Object.keys(ARMAS_REAIS).join(', ')})`);
  const ficha = validarFicha(JSON.parse(readFileSync(join(ROOT, 'tools', 'blender', 'refs', `${id}.json`), 'utf8')), classeDaArma(id));
  // A pega (Fase 4.1b, D5): o solver refaz o rig das luvas dentro do construir da arma, então a ficha e as pinturas das
  // luvas entram no contexto e no hash — mudar as luvas refaz a pega de todas as armas.
  const { validarFichaLuvas } = await import('../src/characters/hands/fichaLuvas.js');
  const luvas = {
    ficha: validarFichaLuvas(JSON.parse(readFileSync(join(ROOT, 'tools', 'blender', 'refs', 'luvas.json'), 'utf8'))),
    pinturas: LUVAS.pinturas,
  };
  // A primeira pessoa da conferência com a pose do jogo (correções da P1 da 4.1c, P1.4): a câmera no referencial da arma
  // (u) pela posição da categoria, com os offsets padrão do CS e o ajuste fino da arma, e o FOV vertical do padrão. Fica
  // fora do hash: é só a vista da conferência, não muda a saída do construir.
  const { cameraInWeaponFrame, viewCategory, viewPlacement, viewmodelVerticalFov, weaponNudge } = await import('../src/weapons/viewmodel/placement.js');
  const { VIEWMODEL } = await import('../src/data/viewmodel.js');
  const offsetPadrao = { x: VIEWMODEL.offset.x.default, y: VIEWMODEL.offset.y.default, z: VIEWMODEL.offset.z.default };
  const primeiraPessoa = {
    ...cameraInWeaponFrame(viewPlacement(viewCategory(id), { offset: offsetPadrao, nudge: weaponNudge(id) })),
    fovVertical: viewmodelVerticalFov(VIEWMODEL.fov.default),
  };
  const ctx = {
    id, raiz: ROOT, ficha, fabrica: def.fabrica, pecas: def.pecas, zonas: zonasDaArma(id), soquetes: soquetesDaArma(id),
    // As medidas-chave da classe (Fase 4.1c, D3): o validar.py mede cada uma pelo nome.
    classe: classeDaArma(id), medidas: medidasDaArma(id),
    // A pega das luvas só nas categorias que já têm a regra no solver (src/data/luvas.js).
    pega: armaComPega(id),
    orcamento: orcamentoDaArma(id), saida: join(ROOT, def.pasta), conferencia: join(ROOT, 'tools', 'blender', 'conferencia', id),
    relevos: RELEVOS_MOLDADOS, veio,
    categoria: def.categoria, luvas, primeiraPessoa,
    hash: hashEntradas(id, def, { ficha, luvas, pega: armaComPega(id), relevos: RELEVOS_MOLDADOS, veio, texturas }), forcar,
  };
  mkdirSync(TMP, { recursive: true });
  const arquivo = join(TMP, `${id}-real.json`);
  writeFileSync(arquivo, JSON.stringify(ctx));
  return { arquivo, ctx };
}

/** Uma linha com a silhueta, os triângulos e o tamanho; lança com a lista quando a saída tem problema. */
function resumoSaida(id) {
  const { problemas, relatorio, bytes } = validarSaida(id, ROOT);
  if (problemas.length) throw new Error(`${id}: a saída tem problemas:\n  ${problemas.join('\n  ')}`);
  const s = relatorio.silhueta;
  const t = Object.entries(relatorio.lods).map(([l, d]) => `${l} ${d.triangulos.toLocaleString('pt-BR')}`).join(' · ');
  return `silhueta ${(s.iouTolerancia * 100).toFixed(1)} % (bruto ${(s.iouBruto * 100).toFixed(1)} %) · ${t} triângulos · ${(bytes / 1048576).toFixed(2)} MB`
    + resumoPega(relatorio.empunhadura);
}

/** A pega das luvas numa linha: a maior entrada na arma e o contato mais longe de cada mão (Fase 4.1b). */
function resumoPega(e) {
  if (!e) return '';
  // as mãos da regra (Tarefa 8 da 4.1c: a faca só tem a direita; sem o campo, as duas, como as armas da 4.1b) e, na
  // faca, o polegar assentado no dedo
  const maos = (e.maos ?? ['d', 'e']).map((l) => {
    const c = Object.entries(e[l].contatosMM);
    const [nome, mm] = c.reduce((a, b) => (b[1] > a[1] ? b : a));
    const p = e[l].polegar;
    const sobre = p?.sobre ? `, polegar no ${p.sobre.join(', ')} a ${p.polpaEncostaMM} mm` : '';
    return `${l === 'd' ? 'direita' : 'esquerda'} entra ${e[l].penetracaoMM} mm, contato mais longe ${nome} ${mm} mm${sobre}`;
  });
  return ` · pega (${e.segundos} s): ${maos.join('; ')}`;
}

/** Contexto das luvas para o principal.py: a ficha validada, o registro (pinturas e orçamento), as pastas e o hash. */
async function contextoLuvas() {
  const { validarFichaLuvas } = await import('../src/characters/hands/fichaLuvas.js');
  const ficha = validarFichaLuvas(JSON.parse(readFileSync(join(ROOT, 'tools', 'blender', 'refs', 'luvas.json'), 'utf8')));
  const ctx = {
    id: 'luvas', raiz: ROOT, ficha, pinturas: LUVAS.pinturas, orcamento: LUVAS.orcamento, saida: join(ROOT, LUVAS.pasta),
    conferencia: join(ROOT, 'tools', 'blender', 'conferencia', 'luvas'), hash: hashEntradas('luvas', LUVAS, ficha),
  };
  mkdirSync(TMP, { recursive: true });
  const arquivo = join(TMP, 'luvas-real.json');
  writeFileSync(arquivo, JSON.stringify(ctx));
  return { arquivo, ctx };
}

/** A linha `MASSACRE-<nome>` da saída do Blender, lida como JSON. */
function linhaJson(saida, nome) {
  const linha = saida.split('\n').find((l) => l.startsWith(`MASSACRE-${nome} `));
  if (!linha) throw new Error(`o Blender não devolveu a linha MASSACRE-${nome}`);
  return JSON.parse(linha.slice(`MASSACRE-${nome} `.length));
}

/** As contas das luvas numa linha: os triângulos, cada medida com o alvo e o desvio, e o assentamento das peças. */
// As poses de teste do relatório das luvas: a maior penetração da luva nela mesma (e em que pose), a das juntas
// sozinhas no limite, a junta que mais afinou, o pior assentamento das peças e o encosto da polpa do polegar nos dedos.
function resumoPoses(poses) {
  let pen = { mm: 0, pose: '—' };
  let junta = { razao: 1, nome: '—', pose: '—' };
  let assento = 0;
  for (const [nome, p] of Object.entries(poses)) {
    if (typeof p?.atravessaMM !== 'number') continue;
    if (p.atravessaMM > pen.mm) pen = { mm: p.atravessaMM, pose: nome };
    if (p.piorJunta && p.piorJunta[1] < junta.razao) junta = { razao: p.piorJunta[1], nome: p.piorJunta[0], pose: nome };
    assento = Math.max(assento, p.assentamentoMM);
  }
  const limite = Object.values(poses.juntasNoLimite ?? {}).reduce((m, j) => Math.max(m, j.atravessaMM), 0);
  const polegar = Object.entries(poses.contato ?? {})
    .filter(([, c]) => typeof c?.polegar?.polpaEncostaMM === 'number')
    .map(([nome, c]) => `${nome} ${c.polegar.polpaEncostaMM} mm`);
  return `poses: penetração ${pen.mm} mm (${pen.pose}), juntas no limite ${limite} mm, `
    + `pior junta ${junta.razao} (${junta.nome}, ${junta.pose}), assento ${assento} mm, `
    + `polpa do polegar nos dedos (${polegar.join(', ')})`;
}

function resumoLuvas(rel) {
  const medidas = Object.entries(rel.medidas)
    .map(([nome, m]) => `${nome} ${m.mm.toFixed(2)}/${m.alvo.toFixed(2)} mm (${((m.mm / m.alvo - 1) * 100).toFixed(2)} %)`);
  const t = rel.triangulos;
  return `${t.luva.toLocaleString('pt-BR')} triângulos por luva (base ${t.base.toLocaleString('pt-BR')}, detalhes `
    + `${t.detalhes.toLocaleString('pt-BR')}) · ${medidas.join(' · ')} · assentamento ${rel.assentamentoMM} mm · `
    + resumoPoses(rel.poses);
}

/** A saída das luvas em assets/maos/ conferida contra o registro (tools/blender/saidaLuvas.mjs); lança os problemas. */
function saidaLuvas() {
  const { problemas, bytes } = validarSaidaLuvas(ROOT);
  if (problemas.length) throw new Error(`luvas: a saída em ${LUVAS.pasta} tem problemas:\n  - ${problemas.join('\n  - ')}`);
  return `${LUVAS.pasta}luvas.glb e texturas em ${(bytes / 1048576).toFixed(2)} MB`;
}

async function construirLuvas(forcar) {
  const { arquivo, ctx } = await contextoLuvas();
  const rel = join(ctx.saida, 'luvas.relatorio.json');
  if (!forcar && existsSync(rel)) {
    const antigo = JSON.parse(readFileSync(rel, 'utf8'));
    if (antigo.entradas?.hash === ctx.hash && !validarSaidaLuvas(ROOT).problemas.length) {
      return `luvas: sem mudança nas entradas — ${resumoLuvas(antigo)} · ${saidaLuvas()}`;
    }
  }
  const t0 = Date.now();
  const saida = await rodarComEtapas(['construir', arquivo], SCRIPT_REAIS, 'luvas');
  return `luvas: construídas em ${((Date.now() - t0) / 1000).toFixed(0)} s — ${resumoLuvas(linhaJson(saida, 'LUVAS'))} · `
    + saidaLuvas();
}

async function validarLuvas() {
  const { arquivo } = await contextoLuvas();
  const rel = linhaJson(rodarSemJanela(['validar', arquivo], SCRIPT_REAIS), 'VALIDACAO');
  return `luvas: validação aprovada — ${resumoLuvas(rel)} · ${saidaLuvas()}`;
}

async function conferirLuvas() {
  const { arquivo, ctx } = await contextoLuvas();
  const arquivos = linhaJson(rodarSemJanela(['conferir', arquivo], SCRIPT_REAIS), 'CONFERIR');
  return `luvas: ${arquivos.length} vistas em ${ctx.conferencia}`;
}

async function abrirLuvas() {
  const blend = join(ROOT, 'tools', 'blender', 'conferencia', 'luvas', 'luvas.blend');
  if (!existsSync(blend)) throw new Error('luvas: rode antes npm run blender -- construir luvas');
  const filho = spawn(blenderExe(), [blend], { detached: true, stdio: 'ignore' });
  filho.unref();
  return `Blender aberto com ${blend}`;
}

// O booleano exato do Blender 5.2 às vezes sai ruim num processo inteiro: a malha avaliada de uma peça com vértices que
// não são número e arestas soltas, a mesma em todas as reavaliações dentro dele (tools/blender/armas/canonica.py,
// TENTATIVAS: o quebra-chamas da M4A4 em 2 de 3 construções por aqui, nenhuma em 14 do Blender chamado direto), e num
// processo novo a certa, sempre a mesma. O construir que cai nisso (MalhaRuim) é refeito num processo novo, até
// PROCESSOS vezes.
const PROCESSOS = 3;

async function construirReal(id, forcar) {
  const { arquivo, ctx } = await contextoReal(id, { forcar });
  const rel = join(ctx.saida, `${id}.relatorio.json`);
  if (!forcar && existsSync(rel)) {
    const antigo = JSON.parse(readFileSync(rel, 'utf8'));
    if (antigo.entradas?.hash === ctx.hash && !validarSaida(id, ROOT).problemas.length) {
      return `${id}: sem mudança nas entradas — ${resumoSaida(id)}`;
    }
  }
  const t0 = Date.now();
  for (let k = 1; ; k++) {
    try {
      await rodarComEtapas(['construir', arquivo], SCRIPT_REAIS, id);
      break;
    } catch (err) {
      if (k >= PROCESSOS || !/MalhaRuim/.test(err.message)) throw err;
      const linha = err.message.split('\n').find((l) => l.includes('MalhaRuim:')) ?? '';
      console.log(`  ${id} · o booleano saiu ruim neste processo do Blender (${linha.split('MalhaRuim:')[1]?.trim() ?? '?'}); `
        + `construindo de novo num processo novo (${k + 1} de ${PROCESSOS})`);
    }
  }
  return `${id}: construída em ${((Date.now() - t0) / 1000).toFixed(0)} s — ${resumoSaida(id)}`;
}

async function validarReal(id) {
  const { arquivo } = await contextoReal(id);
  rodarSemJanela(['validar', arquivo], SCRIPT_REAIS);
  return `${id}: validação aprovada — ${resumoSaida(id)}`;
}

async function conferirReal(id) {
  const { arquivo, ctx } = await contextoReal(id);
  const out = rodarSemJanela(['conferir', arquivo], SCRIPT_REAIS);
  const linha = out.split('\n').find((l) => l.startsWith('MASSACRE-CONFERIR '));
  const arquivos = linha ? JSON.parse(linha.slice('MASSACRE-CONFERIR '.length)) : [];
  return `${id}: ${arquivos.length} vistas em ${ctx.conferencia}`;
}

async function abrirReal(id) {
  const blend = join(ROOT, 'tools', 'blender', 'conferencia', id, `${id}.blend`);
  if (!existsSync(blend)) throw new Error(`${id}: rode antes npm run blender -- construir ${id}`);
  const filho = spawn(blenderExe(), [blend], { detached: true, stdio: 'ignore' });
  filho.unref();
  return `Blender aberto com ${blend}`;
}

async function principal() {
  const argv = process.argv.slice(2);
  const forcar = argv.includes('--forcar');
  const [acao, alvo, extra] = argv.filter((a) => a !== '--forcar');
  const { ARMAS } = await import('../src/data/armas/index.js');
  const { ARMAS_REAIS } = await import('../src/data/armasReais.js');
  const real = (id) => Boolean(ARMAS_REAIS[id]);
  if (acao === 'provar') {
    if (alvo !== 'pecas') throw new Error('uso: npm run blender -- provar pecas');
    const linha = rodarSemJanela([], SCRIPT_PROVAS).split('\n').find((l) => l.startsWith('MASSACRE-PROVAS '));
    const r = JSON.parse(linha.slice('MASSACRE-PROVAS '.length));
    for (const [peca, d] of Object.entries(r.medidas)) console.log(`${peca}: ${JSON.stringify(d)}`);
    console.log(`peças: ${Object.keys(r.medidas).length} provadas, nenhum problema`);
    return;
  }
  if (acao === 'construir' || (acao === 'validar' && alvo && !alvo.endsWith('.js'))) {
    if (!alvo) throw new Error(`uso: npm run blender -- ${acao} <luvas|${Object.keys(ARMAS_REAIS).join('|')}|todas>`);
    let falhas = 0;
    for (const id of alvo === 'todas' ? ['luvas', ...Object.keys(ARMAS_REAIS)] : [alvo]) {
      try {
        if (id === 'luvas') {
          console.log(acao === 'construir' ? await construirLuvas(forcar) : await validarLuvas());
          continue;
        }
        if (!real(id)) throw new Error(`${id} não é uma arma realista (tem: ${Object.keys(ARMAS_REAIS).join(', ')})`);
        console.log(acao === 'construir' ? await construirReal(id, forcar) : await validarReal(id));
      } catch (err) {
        falhas++;
        console.error(err.message ?? err);
      }
    }
    if (falhas) process.exitCode = 1;
    return;
  }
  // As de massinha que ainda não foram refeitas (a receita da AK fica no disco até a Tarefa 16, mas quem vale é a realista).
  const deMassinha = Object.keys(ARMAS).filter((id) => !real(id));
  const ids = alvo !== 'todas' ? [alvo] : acao === 'conferir' ? ['luvas', ...Object.keys(ARMAS_REAIS), ...deMassinha] : deMassinha;
  const acoes = {
    abrir: (id) => (id === 'luvas' ? abrirLuvas() : real(id) ? abrirReal(id) : abrir(id)),
    conferir: (id) => (id === 'luvas' ? conferirLuvas() : real(id) ? conferirReal(id) : conferir(id)),
    'ida-volta': idaVolta,
  };
  if (acao === 'validar') {
    if (!alvo) throw new Error('uso: npm run blender -- validar <arquivo.js>');
    console.log(await validar(alvo));
    return;
  }
  if (acao === 'previa') {
    if (!alvo || !extra) throw new Error('uso: npm run blender -- previa <arquivo.js> <saída sem extensão>');
    console.log(await previa(alvo, extra));
    return;
  }
  if (!acoes[acao] || !alvo) {
    throw new Error('uso: npm run blender -- <construir|validar|abrir|conferir|ida-volta> <arma|todas> [--forcar], validar <arquivo.js> ou previa <arquivo.js> <saída>');
  }
  if (acao === 'abrir' && ids.length > 1) throw new Error('abrir é uma arma de cada vez');
  let falhas = 0;
  for (const id of ids) {
    try {
      console.log(await acoes[acao](id));
    } catch (err) {
      falhas++;
      console.error(err.message ?? err);
    }
  }
  if (falhas) process.exitCode = 1;
}

principal().catch((err) => {
  console.error(err.message ?? err);
  process.exitCode = 1;
});
