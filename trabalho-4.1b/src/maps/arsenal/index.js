// Mapa `arsenal` — bancada de armas da Fase 4.1 (docs/phases/phase-4.md, seção 4.1, "Bancada de armas"): a mesa do
// animador com a luz da vitrine virada em bancada de armeiro, as armas deitadas em fileiras — a realista do Blender
// (Fase 4.1a) e as de massinha das receitas —, a roda de modelar com a arma escolhida e o painel de fita crepe (Tab). É
// também o banco do aceite das armas: forma, acabamento e skins, silhueta × planta, e o caminho do Blender (reler do
// disco). Na 4.1b, o rebatedor de isopor atrás de quem olha a bancada (rebatedor.js), aceso pelo rim: o lado do
// receptor das armas realistas refletia o estúdio escuro.

import * as THREE from 'three';
import { STUDIO_RIGS } from '../../data/studioRigs.js';
import { ARSENAL } from '../../data/arsenal.js';
import { HULL } from '../../data/movement.js';
import { EV } from '../../core/events.js';
import { registerMap } from '../registry.js';
import { StudioRig } from '../../render/studio/studioRig.js';
import { disposeObject3D } from '../../render/dispose.js';
import { ArsenalBench } from './bench.js';
import { createArsenalPanel } from './panel.js';
import { construirRebatedor } from './rebatedor.js';

const DEG = Math.PI / 180;

async function build({ render, config, services }) {
  const scene = new THREE.Scene();
  scene.name = 'arsenal';
  scene.fog = new THREE.FogExp2(0x160f0c, 0.0001);

  // A luz primeiro: as variantes de shader das armas compilam com as luzes da cena, antes de cada arma entrar nela.
  const rigDef = STUDIO_RIGS[ARSENAL.rig];
  const rig = new StudioRig({
    def: rigDef, set: services.set, renderer: render.renderer, tableY: ARSENAL.desk.mat.thickness,
    floorY: ARSENAL.desk.floorY, center: new THREE.Vector3(0, 60, 0),
  }).build(scene);
  rig.setDustDensity(config.get('graphics.particles'));

  const compileCamera = new THREE.PerspectiveCamera();
  const bench = new ArsenalBench({
    set: services.set, weapons: services.weaponModels, anisotropy: render.anisotropy, log: services.log,
    precompile: (obj) => render.renderer.compileAsync(obj, compileCamera, scene),
  });
  try {
    await bench.build(scene);
  } catch (err) {
    // Montagem pela metade: o matchState não recebe o mapa, então a GPU sai aqui.
    bench.dispose();
    rig.dispose();
    disposeObject3D(scene);
    throw err;
  }

  // O rebatedor: a placa de isopor atrás do olho do "Segurar" (o ponto da foto do reflexo), acesa pela luz da montagem
  // que chega pela frente ali, assentada no tampo (y = 0) atrás do tapete; entra na foto do reflexo que o MatchState
  // tira com o mapa pronto.
  const olhoDoReflexo = new THREE.Vector3(ARSENAL.reflexo.x, ARSENAL.desk.mat.thickness + HULL.standEye, ARSENAL.reflexo.z);
  const luzDoRebatedor = rigDef.lights.find((l) => l.id === ARSENAL.rebatedor.luz);
  const rebatedor = construirRebatedor(services.set, ARSENAL.rebatedor, {
    floorY: ARSENAL.desk.floorY, apoioY: 0, olho: olhoDoReflexo, luz: new THREE.Vector3(...luzDoRebatedor.position),
  });
  scene.add(rebatedor.group);

  // "Segurar": o viewmodel com a arma da roda (acento e nível da bancada) e a câmera parada no tapete, na altura do olho
  // do boneco; a troca de arma, de facção ou de nível no painel passa para a mão no quadro seguinte.
  const match = () => services.states.current;
  let holding = null;
  const holdSpec = () => ({ id: bench.state.id, faction: bench.state.faction, lod: bench.state.lod, gloves: bench.state.gloves });
  const toggleHold = () => {
    if (holding) {
      match()?.setHold?.(null);
      holding = null;
      return false;
    }
    if (!bench.state.id) return false;
    const h = ARSENAL.hold;
    const spec = holdSpec();
    const on = match()?.setHold?.({
      ...spec,
      camera: { position: new THREE.Vector3(h.x, ARSENAL.desk.mat.thickness + HULL.standEye, h.z), yaw: h.yawDeg * DEG, pitch: h.pitchDeg * DEG },
    });
    if (!on) return false;
    holding = spec;
    match()?.setCursorMode?.(false);
    return true;
  };
  const panel = createArsenalPanel(services, {
    bench,
    onClose: () => match()?.setCursorMode?.(false),
    onHold: toggleHold,
    isHolding: () => Boolean(holding),
  });

  const offs = [
    services.events.on(EV.POSE, ({ pose }) => rig.onPose(pose)),
    config.watch('graphics.particles', (e) => rig.setDustDensity(e.value)),
    services.events.on(EV.RENDER_CONTEXT, ({ lost }) => {
      if (!lost) rig.bakeEnvironment();
    }),
    // Skin trocada (o painel ou o console `skin`): a arma da roda e a da fileira voltam com os materiais novos.
    services.events.on(EV.WEAPON_MODEL, ({ id, phase }) => {
      if (phase === 'skin') bench.onSkin(id);
    }),
  ];

  const { spawn, bounds } = ARSENAL;
  return {
    id: 'arsenal',
    scene,
    bounds: new THREE.Box3(new THREE.Vector3(...bounds.min), new THREE.Vector3(...bounds.max)),
    rig,
    bench,
    panel,
    move: { speedScale: ARSENAL.speedScale },
    post: { context: 'vitrine', exposure: rigDef.exposure },
    // A roda gira com a arma: a sombra acompanha a cada quadro.
    staticShadows: false,
    reflection: olhoDoReflexo.clone(),
    spawn: {
      position: new THREE.Vector3(spawn.x, spawn.y, spawn.z),
      yaw: spawn.yawDeg * DEG,
      pitch: spawn.pitchDeg * DEG,
    },
    frame(dt, camera) {
      rig.frame(camera, render.drawingHeight);
      bench.frame(dt);
      if (holding) {
        const spec = holdSpec();
        if (!spec.id) {
          match()?.setHold?.(null);
          holding = null;
          panel.refresh();
        } else if (spec.id !== holding.id || spec.faction !== holding.faction || spec.lod !== holding.lod || spec.gloves !== holding.gloves) {
          holding = spec;
          match()?.setHold?.(spec);
        }
      }
    },
    get holding() {
      return Boolean(holding);
    },
    dispose() {
      holding = null;
      for (const off of offs) off();
      panel.dispose();
      rebatedor.dispose();
      rig.dispose();
      bench.dispose();
    },
  };
}

registerMap({
  id: 'arsenal',
  label: 'Bancada de armas',
  description: 'A AK-47 realista do Blender e as armas de massinha das receitas: fileiras no tapete, roda de modelar, plantas a lápis e o painel (Tab).',
  kind: 'teste',
  aliases: ['armas', 'oficina', 'armeiro'],
  build,
});
