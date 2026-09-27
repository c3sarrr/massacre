// Parâmetros da sala de testes e do modo livre (Fases 1 e 3): sala de papelão andável, volta ao spawn ao cair do set,
// a câmera livre (voo da vitrine e noclip) e o monitor do movimento do aceite da Fase 3 (subfase 3.5).
// Unidades: 1 unidade = 1 cm na escala do boneco (o boneco tem ~72 unidades de altura).

export const TEST_ROOM = Object.freeze({
  width: 1600, // X
  depth: 1600, // Z
  height: 520, // Y
  spawn: Object.freeze({ x: 0, y: 0, z: 560, yawDeg: 0, pitchDeg: -4 }), // pés do jogador (o olho fica 64 u acima)
  // Reflexo das armas realistas (Fase 4.1a, src/render/setReflection.js): o centro da sala, na altura do olho do boneco.
  reflexo: Object.freeze({ x: 0, z: 0 }),
  scaleMarkerHeight: 72, // "boneco" de referência para conferir a escala
  wallCollider: 6.4, // espessura de colisão das paredes: papelão de 4 u + empeno de até 1,1 u em cada face
  floorSlab: 8, // laje de colisão sob o tapete
});

/** Modo livre em mapa andável. */
export const SANDBOX = Object.freeze({
  fallOutDepth: 1500, // caiu mais que isto (u) abaixo do chão do mapa (noclip desligado fora do set): volta ao spawn
});

/** Monitor do movimento (`cl_monitor`, src/debug/moveMonitor.js), o mesmo da varredura do Node. */
export const MONITOR = Object.freeze({
  tolerance: 0.05, // u de folga na checagem "a cápsula cabe aqui?" (a dos testes de varredura da 3.2 à 3.4)
  floorSlack: 0.01, // u abaixo do chão do estúdio que ainda não contam como queda para fora
  memoryEvery: 1, // s entre as amostras de memória (geometrias, texturas, programas e heap)
  window: 5, // s de quadros no FPS "agora" do painel (o do relatório é o da sessão inteira)
  panelHz: 4, // atualizações do texto do painel por segundo
  keepProblems: 20, // problemas guardados com o tick e o lugar (a contagem continua)
});

export const FREE_CAMERA = Object.freeze({
  speed: 420, // u/s voando
  walkFactor: 0.52, // Shift: mesma proporção do andar silencioso do CS
  boostFactor: 2.4, // segurar "mirar" acelera (útil para atravessar mapas grandes em noclip)
  verticalSpeed: 320,
  accelerate: 10, // sv_accelerate
  friction: 8, // sv_friction
  stopSpeed: 60,
  radius: 16, // raio de colisão com as paredes (noclip desligado)
});
