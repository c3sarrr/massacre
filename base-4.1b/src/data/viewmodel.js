// Viewmodel parado (Fase 4.1; desenho em docs/phases/phase-4.md, seção 4.1, "Viewmodel parado"): a arma na mão em
// primeira pessoa, numa camada própria do pipeline, com os dois braços de massinha presos às âncoras da arma. Na 4.1
// não anima (a 4.3 traz as poses-chave do Blender): segura parado, com o boil "em dois".
// Referencial da câmera (o do three): +X direita, +Y cima, −Z frente. Unidades: u (polegada na escala do boneco).
// FOV e offsets como no CS:GO: `viewmodel_fov` é horizontal em 4:3 (o Source mede assim; o vertical fica fixo e telas
// mais largas ganham lado, Hor+), 60 por padrão, 54–68; `viewmodel_offset_x/y/z` (direita, frente, cima) somam por
// cima da posição da categoria, com o padrão do CS (1, 1, −1 — o "Desktop" do viewmodel_presetpos).

const F = Object.freeze;

export const VIEWMODEL = F({
  fov: F({ default: 60, min: 54, max: 68, aspect: 4 / 3 }),
  offset: F({
    x: F({ default: 1, min: -2, max: 2.5 }), // direita (+) / esquerda (−)
    y: F({ default: 1, min: -2, max: 2 }), // frente (+) / trás (−)
    z: F({ default: -1, min: -2, max: 2 }), // cima (+) / baixo (−)
  }),
  // viewmodel_presetpos do CS:GO: 1 Mesa ("Desktop"), 2 Sofá ("Couch"), 3 Clássica ("Classic").
  presets: F({
    1: F({ label: 'Mesa', fov: 60, x: 1, y: 1, z: -1 }),
    2: F({ label: 'Sofá', fov: 54, x: 0, y: 0, z: 0 }),
    3: F({ label: 'Clássica', fov: 68, x: 2.5, y: 0, z: -1.5 }),
  }),
  // Câmera própria da camada: o antebraço passa rente ao olho, então o plano de perto é bem mais curto que o do mundo.
  near: 0.5,
  far: 400,
  /**
   * Posição por categoria: `pos` = a origem da arma (o eixo do cano acima do gatilho) no referencial da câmera, antes
   * dos offsets; `angles` = [arfagem, guinada, rolagem] em graus (guinada + vira a boca para o centro da tela, arfagem +
   * levanta a boca, rolagem + tomba o topo para a esquerda); `elbows` = para onde cada antebraço aponta, fora da tela
   * (o cotovelo real fica no alinhamento, a um antebraço do pulso).
   */
  categories: F({
    pistola: F({ pos: F([1.8, -0.9, -13.5]), angles: F([3, 4, -2]), elbows: F({ direita: F([12, -20, 2]), esquerda: F([-10, -20, 0]) }) }),
    rifle: F({ pos: F([4.5, -3.1, -9]), angles: F([4, 1, -2]), elbows: F({ direita: F([15, -18, 6]), esquerda: F([-18, -16, -4]) }) }),
    sniper: F({ pos: F([5, -4.1, -9.6]), angles: F([3.5, 1, -1.5]), elbows: F({ direita: F([15, -18, 6]), esquerda: F([-18, -17, -8]) }) }),
    escopeta: F({ pos: F([4.5, -3.2, -9.2]), angles: F([4, 1, -2]), elbows: F({ direita: F([15, -18, 6]), esquerda: F([-18, -17, -6]) }) }),
    smgBullpup: F({ pos: F([4.9, -4, -14.5]), angles: F([4, 2, -2]), elbows: F({ direita: F([14, -19, 4]), esquerda: F([-14, -19, -2]) }) }),
    faca: F({ pos: F([3.4, -2.4, -10.5]), angles: F([10, 18, -30]), elbows: F({ direita: F([16, -16, 4]), esquerda: F([-9, -20, 4]) }) }),
  }),
  // Categoria de cada arma com modelo — a receita de massinha ou o .glb do Blender (as da 4.4 entram aqui junto com o
  // modelo) — e, quando a silhueta pede, um ajuste fino somado à posição da categoria (`nudge`, u no referencial da
  // câmera): a alça de transporte da M4A4 fica mais alta que a tampa da AK, então a M4 desce um pouco para não tapar o
  // lado direito da tela.
  weapons: F({
    glock: F({ category: 'pistola' }),
    ak47: F({ category: 'rifle' }),
    m4a4: F({ category: 'rifle', nudge: F([0.3, -0.6, -0.4]) }),
    awp: F({ category: 'sniper' }),
    nova: F({ category: 'escopeta' }),
    p90: F({ category: 'smgBullpup' }),
    knife: F({ category: 'faca' }),
  }),
  // Luz da camada: cópias das luzes do mapa (mesmas posições, cores e intensidades, lidas a cada quadro), a hemisférica
  // e o ambiente assado.
  light: F({
    // Sombra própria (a mão na arma, a arma nos dedos): cada luz que faz sombra no mapa ganha, na cópia, uma câmera de
    // sombra apertada numa esfera em volta da arma e dos pulsos (+ `padding` u). Lado do mapa = o do nível de sombra ×
    // `mapScale`, entre `minSize` e `maxSize`; some com as sombras desligadas. `softness` multiplica o raio do filtro.
    selfShadow: F({ mapScale: 0.5, minSize: 512, maxSize: 1024, padding: 2, bias: -0.0006, normalBias: 0.04, softness: 1.2 }),
    // O set tapa a luz: do centro da arma, da boca e dos pulsos, um raio até cada luz que faz sombra no mapa (no mundo
    // de colisão); a fração livre multiplica a cópia. Suaviza (constantes de tempo em s, subindo e descendo) para não
    // piscar ao passar rente a uma quina.
    occlusion: F({ points: F(['centro', 'boca', 'maoDireita', 'maoEsquerda']), rise: 0.08, fall: 0.14 }),
    // s entre as varreduras da cena do mapa atrás de luzes que entraram (uma que saiu aparece na hora).
    rescan: 1,
  }),
});
