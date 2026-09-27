// Contas puras da régua (Fase 4.1a; desenho em docs/superpowers/specs/2026-09-26-armas-realistas-design.md, seção 3.3):
// suavização de contorno lido de foto de baixa resolução (Chaikin), área e caixa de polígono, rasterização de contorno
// com buracos numa grade, dilatação por disco, perfis de cima e de baixo por coluna e a coincidência (IoU) entre duas
// máscaras com a tolerância de raio r (a diferença a até r pixels da outra silhueta não conta: é o ruído do próprio
// contorno). A página tools/regua.html usa no navegador e os testes no Node; tools/blender/armas/validar.py faz as
// mesmas contas em numpy.

/** Chaikin em polígono fechado: cada lado vira dois pontos, a 1/4 e a 3/4. */
export function chaikin(pontos, iteracoes = 1) {
  let pts = pontos;
  for (let k = 0; k < iteracoes; k++) {
    const novo = [];
    for (let i = 0; i < pts.length; i++) {
      const [ax, ay] = pts[i];
      const [bx, by] = pts[(i + 1) % pts.length];
      novo.push([0.75 * ax + 0.25 * bx, 0.75 * ay + 0.25 * by], [0.25 * ax + 0.75 * bx, 0.25 * ay + 0.75 * by]);
    }
    pts = novo;
  }
  return pts;
}

/** Área com sinal (positiva no sentido anti-horário, com +Y para cima). */
export function areaPoligono(pontos) {
  let s = 0;
  for (let i = 0; i < pontos.length; i++) {
    const [ax, ay] = pontos[i];
    const [bx, by] = pontos[(i + 1) % pontos.length];
    s += ax * by - bx * ay;
  }
  return s / 2;
}

export function caixaDoPoligono(pontos) {
  let x0 = Infinity;
  let y0 = Infinity;
  let x1 = -Infinity;
  let y1 = -Infinity;
  for (const [x, y] of pontos) {
    x0 = Math.min(x0, x);
    y0 = Math.min(y0, y);
    x1 = Math.max(x1, x);
    y1 = Math.max(y1, y);
  }
  return { x0, y0, x1, y1 };
}

/**
 * Máscara (1 = dentro) de um contorno com buracos numa grade: a célula (i, j) cobre x ∈ [x0 + i·passo, x0 + (i+1)·passo)
 * e y ∈ [y1 − (j+1)·passo, y1 − j·passo) — a linha 0 fica em cima, como numa imagem. O centro da célula decide, pela
 * paridade dos cruzamentos com todos os anéis.
 * @param {number[][][]} aneis [contorno, ...buracos]
 * @param {{x0:number, y1:number, passo:number, largura:number, altura:number}} grade
 * @returns {Uint8Array}
 */
export function rasterizar(aneis, { x0, y1, passo, largura, altura }) {
  const mascara = new Uint8Array(largura * altura);
  const cruz = [];
  for (let j = 0; j < altura; j++) {
    const y = y1 - (j + 0.5) * passo;
    cruz.length = 0;
    for (const anel of aneis) {
      for (let k = 0; k < anel.length; k++) {
        const [ax, ay] = anel[k];
        const [bx, by] = anel[(k + 1) % anel.length];
        if ((ay > y) !== (by > y)) cruz.push(ax + ((y - ay) / (by - ay)) * (bx - ax));
      }
    }
    cruz.sort((a, b) => a - b);
    for (let k = 0; k + 1 < cruz.length; k += 2) {
      const i0 = Math.max(0, Math.ceil((cruz[k] - x0) / passo - 0.5));
      const i1 = Math.min(largura - 1, Math.floor((cruz[k + 1] - x0) / passo - 0.5));
      for (let i = i0; i <= i1; i++) mascara[j * largura + i] = 1;
    }
  }
  return mascara;
}

/** Dilatação da máscara por um disco de raio r pixels (r = 0 devolve uma cópia). */
export function dilatar(mascara, largura, altura, r) {
  if (r <= 0) return mascara.slice();
  const out = new Uint8Array(mascara.length);
  const offs = [];
  for (let dy = -r; dy <= r; dy++) for (let dx = -r; dx <= r; dx++) if (dx * dx + dy * dy <= r * r) offs.push([dx, dy]);
  for (let j = 0; j < altura; j++) {
    for (let i = 0; i < largura; i++) {
      if (!mascara[j * largura + i]) continue;
      for (const [dx, dy] of offs) {
        const x = i + dx;
        const y = j + dy;
        if (x >= 0 && y >= 0 && x < largura && y < altura) out[y * largura + x] = 1;
      }
    }
  }
  return out;
}

/**
 * Coincidência entre duas máscaras do mesmo tamanho. Bruta: |A∩B| / |A∪B|. Com tolerância r: o pixel de A fora de B que
 * está a até r pixels de B não conta (e o de B fora de A a até r de A): |A∩B| / (|A∩B| + a diferença que conta).
 * @returns {{bruto:number, tolerancia:number, inter:number, soA:number, soB:number}}
 */
export function iou(a, b, largura, altura, r = 0) {
  const da = r > 0 ? dilatar(a, largura, altura, r) : a;
  const db = r > 0 ? dilatar(b, largura, altura, r) : b;
  let inter = 0;
  let soA = 0;
  let soB = 0;
  let contaA = 0;
  let contaB = 0;
  for (let k = 0; k < a.length; k++) {
    if (a[k] && b[k]) inter++;
    else if (a[k]) {
      soA++;
      if (!db[k]) contaA++;
    } else if (b[k]) {
      soB++;
      if (!da[k]) contaB++;
    }
  }
  return {
    bruto: inter / (inter + soA + soB || 1),
    tolerancia: inter / (inter + contaA + contaB || 1),
    inter, soA, soB,
  };
}

/** Primeira (cima) e última (baixo) linha com 1 em cada coluna; −1 na coluna vazia. */
export function perfis(mascara, largura, altura) {
  const cima = new Array(largura).fill(-1);
  const baixo = new Array(largura).fill(-1);
  for (let i = 0; i < largura; i++) {
    for (let j = 0; j < altura; j++) {
      if (!mascara[j * largura + i]) continue;
      if (cima[i] < 0) cima[i] = j;
      baixo[i] = j;
    }
  }
  return { cima, baixo };
}
