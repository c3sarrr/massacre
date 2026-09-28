// Contornos 2D das formas por perfil (Fase 4.1): o filete dos cantos e a distância exata a um polígono.
//  - filletPolygon: troca cada canto por um arco tangente aos dois lados (convexo tira a ponta; côncavo enche o canto,
//    como a massa que o dedo alisa por dentro — QPG2, QPL4), com o raio limitado para os arcos vizinhos não se
//    cruzarem (cada arco usa no máximo metade de cada lado).
//  - polygonDistance: distância assinada exata (negativa dentro) de iq ("sdPolygon", iquilezles.org/articles/
//    distfunctions2d): o mínimo das distâncias aos lados e o sinal pelo número de cruzamentos. 1-Lipschitz.
//  - latheOutline: o meridiano do torno (polilinha de eixo a eixo) espelhado no eixo, fechando o polígono cujo
//    lado sobre o eixo some — a distância ao sólido de revolução é a distância 2D em (x, ρ).
// Tudo em Float64Array e closures sem alocar por amostra (o marching cubes chama milhões de vezes).

/** Segmentos de cada arco de filete. */
export const FILLET_SEGMENTS = 6;

/**
 * Polígono fechado com os cantos arredondados.
 * @param {number[][]} points [[x, y], ...] sem repetir o primeiro no fim (horário ou anti-horário)
 * @param {number} radius raio pedido (cada canto usa o menor entre ele e o que cabe nos dois lados)
 * @param {number} [segments]
 * @returns {number[][]} novo contorno
 */
export function filletPolygon(points, radius, segments = FILLET_SEGMENTS) {
  const n = points.length;
  if (!(radius > 0) || n < 3) return points.map((p) => [p[0], p[1]]);
  const out = [];
  for (let i = 0; i < n; i++) {
    const p0 = points[(i + n - 1) % n];
    const p1 = points[i];
    const p2 = points[(i + 1) % n];
    let ax = p0[0] - p1[0];
    let ay = p0[1] - p1[1];
    const la = Math.hypot(ax, ay);
    let bx = p2[0] - p1[0];
    let by = p2[1] - p1[1];
    const lb = Math.hypot(bx, by);
    ax /= la;
    ay /= la;
    bx /= lb;
    by /= lb;
    const cos = Math.max(-1, Math.min(1, ax * bx + ay * by));
    const theta = Math.acos(cos); // ângulo entre os dois lados, no vértice
    if (theta > Math.PI - 1e-6 || theta < 1e-6) {
      out.push([p1[0], p1[1]]); // alinhado (sem canto) ou ponta degenerada
      continue;
    }
    const tanHalf = Math.tan(theta / 2);
    const r = Math.min(radius, 0.5 * Math.min(la, lb) * tanHalf);
    if (r <= 1e-9) {
      out.push([p1[0], p1[1]]);
      continue;
    }
    const tl = r / tanHalf; // distância do vértice aos pontos de tangência
    const t0x = p1[0] + ax * tl;
    const t0y = p1[1] + ay * tl;
    const t1x = p1[0] + bx * tl;
    const t1y = p1[1] + by * tl;
    // Centro na bissetriz, dentro da cunha entre os dois lados.
    let hx = ax + bx;
    let hy = ay + by;
    const lh = Math.hypot(hx, hy);
    hx /= lh;
    hy /= lh;
    const dc = r / Math.sin(theta / 2);
    const cx = p1[0] + hx * dc;
    const cy = p1[1] + hy * dc;
    const a0 = Math.atan2(t0y - cy, t0x - cx);
    let da = Math.atan2(t1y - cy, t1x - cx) - a0;
    while (da > Math.PI) da -= 2 * Math.PI;
    while (da < -Math.PI) da += 2 * Math.PI;
    for (let k = 0; k <= segments; k++) {
      const a = a0 + (da * k) / segments;
      out.push([cx + r * Math.cos(a), cy + r * Math.sin(a)]);
    }
  }
  return out;
}

/** Área com sinal (positiva = anti-horário). */
export function signedArea(points) {
  let a = 0;
  for (let i = 0, j = points.length - 1; i < points.length; j = i++) {
    a += points[j][0] * points[i][1] - points[i][0] * points[j][1];
  }
  return a / 2;
}

/**
 * Distância assinada exata a um polígono fechado (negativa dentro).
 * @param {number[][]} points [[x, y], ...]
 * @returns {(x:number, y:number) => number}
 */
export function polygonDistance(points) {
  const n = points.length;
  const vx = new Float64Array(n);
  const vy = new Float64Array(n);
  const ex = new Float64Array(n);
  const ey = new Float64Array(n);
  const inv = new Float64Array(n);
  for (let i = 0; i < n; i++) {
    vx[i] = points[i][0];
    vy[i] = points[i][1];
  }
  for (let i = 0, j = n - 1; i < n; j = i++) {
    ex[i] = vx[j] - vx[i];
    ey[i] = vy[j] - vy[i];
    const l2 = ex[i] * ex[i] + ey[i] * ey[i];
    inv[i] = l2 > 0 ? 1 / l2 : 0;
  }
  return (px, py) => {
    let d = Infinity;
    let s = 1;
    for (let i = 0, j = n - 1; i < n; j = i++) {
      const wx = px - vx[i];
      const wy = py - vy[i];
      let h = (wx * ex[i] + wy * ey[i]) * inv[i];
      h = h < 0 ? 0 : h > 1 ? 1 : h;
      const bx = wx - ex[i] * h;
      const by = wy - ey[i] * h;
      const b2 = bx * bx + by * by;
      if (b2 < d) d = b2;
      // Cruzamento da semirreta horizontal pelo ponto (a regra par/ímpar de iq).
      const c1 = py >= vy[i];
      const c2 = py < vy[j];
      const c3 = ex[i] * wy > ey[i] * wx;
      if ((c1 && c2 && c3) || (!c1 && !c2 && !c3)) s = -s;
    }
    return s * Math.sqrt(d);
  };
}

/**
 * Polígono do meridiano de um torno: a polilinha (x, ρ) vai de um ponto no eixo (ρ = 0) a outro e é espelhada em
 * ρ → −ρ (sem repetir os pontos do eixo); com `closed`, é um anel que não toca o eixo e fica como está.
 * @param {number[][]} points [[x, ρ], ...]
 * @param {boolean} closed
 * @returns {number[][]}
 */
export function latheOutline(points, closed) {
  if (closed) return points.map((p) => [p[0], p[1]]);
  const out = points.map((p) => [p[0], p[1]]);
  for (let i = points.length - 2; i >= 1; i--) out.push([points[i][0], -points[i][1]]);
  return out;
}
