const P0 = new URLSearchParams(location.search);
const WIDTH = Number(P0.get('largura') || 4000);
const THRESHOLD = Number(P0.get('limiar') || 48);
const HOLE_MIN = Number(P0.get('buraco') || 0.004);
async function sourceInfo(title) {
  const u = 'https://commons.wikimedia.org/w/api.php?action=query&format=json&origin=*&prop=imageinfo'
    + `&iiprop=url|size|mime|extmetadata&iiurlwidth=${WIDTH}&titles=${encodeURIComponent(title)}`;
  const j = await (await fetch(u)).json();
  const page = Object.values(j.query.pages)[0];
  const ii = page.imageinfo?.[0];
  if (!ii) throw new Error(`arquivo não encontrado no Commons: ${title}`);
  const m = ii.extmetadata || {};
  const strip = (s) => (s || '').replace(/<[^>]+>/g, '').replace(/\s+/g, ' ').trim();
  return {
    file: page.title, page: ii.descriptionurl, url: ii.thumburl || ii.url, width: ii.width, height: ii.height,
    license: strip(m.LicenseShortName?.value), artist: strip(m.Artist?.value), credit: strip(m.Credit?.value).slice(0, 200),
  };
}

function loadImage(url) {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.crossOrigin = 'anonymous';
    img.onload = () => resolve(img);
    img.onerror = () => reject(new Error(`não carregou a imagem: ${url}`));
    img.src = url;
  });
}

// Máscara da arma: 1 = arma. Fundo = transparência, ou pixels parecidos com a cor da borda ligados à borda.
function weaponMask(data, W, H) {
  const n = W * H;
  const px = data.data;
  let transparent = 0;
  for (let i = 0; i < n; i += 97) if (px[i * 4 + 3] < 128) transparent++;
  const mask = new Uint8Array(n);
  if (transparent > (n / 97) * 0.05) {
    for (let i = 0; i < n; i++) mask[i] = px[i * 4 + 3] >= 128 ? 1 : 0;
    return { mask, mode: 'alfa' };
  }
  // Cor do fundo: mediana dos pixels da borda.
  const border = [];
  for (let x = 0; x < W; x++) border.push(x, (H - 1) * W + x);
  for (let y = 0; y < H; y++) border.push(y * W, y * W + W - 1);
  const med = [0, 1, 2].map((c) => {
    const v = border.map((i) => px[i * 4 + c]).sort((a, b) => a - b);
    return v[v.length >> 1];
  });
  const near = (i) => Math.abs(px[i * 4] - med[0]) + Math.abs(px[i * 4 + 1] - med[1]) + Math.abs(px[i * 4 + 2] - med[2]) <= THRESHOLD * 1.5;
  const bg = new Uint8Array(n);
  const stack = [];
  for (const i of border) if (!bg[i] && near(i)) {
    bg[i] = 1;
    stack.push(i);
  }
  while (stack.length) {
    const i = stack.pop();
    const x = i % W;
    const y = (i / W) | 0;
    const nb = [x > 0 ? i - 1 : -1, x < W - 1 ? i + 1 : -1, y > 0 ? i - W : -1, y < H - 1 ? i + W : -1];
    for (const j of nb) if (j >= 0 && !bg[j] && near(j)) {
      bg[j] = 1;
      stack.push(j);
    }
  }
  for (let i = 0; i < n; i++) mask[i] = bg[i] ? 0 : 1;
  // Buracos: regiões com a cor do fundo, fechadas pela arma e grandes (o resto são reflexos na arma).
  const seen = new Uint8Array(n);
  for (let s = 0; s < n; s++) {
    if (seen[s] || !mask[s] || !near(s)) continue;
    const comp = [s];
    seen[s] = 1;
    for (let k = 0; k < comp.length; k++) {
      const i = comp[k];
      const x = i % W;
      const y = (i / W) | 0;
      const nb = [x > 0 ? i - 1 : -1, x < W - 1 ? i + 1 : -1, y > 0 ? i - W : -1, y < H - 1 ? i + W : -1];
      for (const j of nb) if (j >= 0 && !seen[j] && mask[j] && near(j)) {
        seen[j] = 1;
        comp.push(j);
      }
    }
    if (comp.length > n * HOLE_MIN * 0.1) for (const i of comp) mask[i] = 0;
  }
  return { mask, mode: `cor da borda rgb(${med.join(', ')}), limiar ${THRESHOLD}` };
}

// Maior componente de 4-vizinhança.
function largestComponent(mask, W, H) {
  const n = W * H;
  const label = new Int32Array(n);
  let best = 0;
  let bestSize = 0;
  let next = 1;
  for (let s = 0; s < n; s++) {
    if (!mask[s] || label[s]) continue;
    const comp = [s];
    label[s] = next;
    for (let k = 0; k < comp.length; k++) {
      const i = comp[k];
      const x = i % W;
      const y = (i / W) | 0;
      const nb = [x > 0 ? i - 1 : -1, x < W - 1 ? i + 1 : -1, y > 0 ? i - W : -1, y < H - 1 ? i + W : -1];
      for (const j of nb) if (j >= 0 && mask[j] && !label[j]) {
        label[j] = next;
        comp.push(j);
      }
    }
    if (comp.length > bestSize) {
      bestSize = comp.length;
      best = next;
    }
    next++;
  }
  const out = new Uint8Array(n);
  for (let i = 0; i < n; i++) out[i] = label[i] === best ? 1 : 0;
  return out;
}

// Laços do contorno pelas arestas dos pixels (arma à esquerda de cada aresta), com a regra de virar à direita nos
// cantos em sela (dois pixels só na diagonal ficam separados).
function traceLoops(mask, W, H) {
  const at = (x, y) => (x >= 0 && y >= 0 && x < W && y < H ? mask[y * W + x] : 0);
  const key = (x, y) => y * (W + 1) + x;
  const out = new Map();
  const add = (x0, y0, x1, y1) => {
    const k = key(x0, y0);
    if (!out.has(k)) out.set(k, []);
    out.get(k).push([x1, y1]);
  };
  for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
    if (!mask[y * W + x]) continue;
    if (!at(x, y - 1)) add(x + 1, y, x, y);
    if (!at(x - 1, y)) add(x, y, x, y + 1);
    if (!at(x, y + 1)) add(x, y + 1, x + 1, y + 1);
    if (!at(x + 1, y)) add(x + 1, y + 1, x + 1, y);
  }
  const loops = [];
  for (const [k0, list0] of out) {
    while (list0.length) {
      const sx = k0 % (W + 1);
      const sy = (k0 / (W + 1)) | 0;
      const loop = [[sx, sy]];
      let [cx, cy] = list0.shift();
      let dx = cx - sx;
      let dy = cy - sy;
      for (let guard = 0; guard < 4 * W * H; guard++) {
        if (cx === sx && cy === sy) break;
        loop.push([cx, cy]);
        const list = out.get(key(cx, cy));
        let pick = 0;
        if (list.length > 1) {
          // Sela: vira à direita (em coordenadas da imagem, y para baixo).
          const right = [-dy, dx];
          const i = list.findIndex(([nx, ny]) => nx - cx === right[0] && ny - cy === right[1]);
          pick = i >= 0 ? i : 0;
        }
        const [nx, ny] = list.splice(pick, 1)[0];
        dx = nx - cx;
        dy = ny - cy;
        cx = nx;
        cy = ny;
      }
      loops.push(loop);
    }
  }
  return loops;
}

function area(poly) {
  let a = 0;
  for (let i = 0, j = poly.length - 1; i < poly.length; j = i++) a += poly[j][0] * poly[i][1] - poly[i][0] * poly[j][1];
  return a / 2;
}

// Douglas-Peucker num laço fechado (divide no ponto mais longe do primeiro).
function simplify(loop, eps) {
  const dp = (pts) => {
    if (pts.length < 3) return pts;
    const [ax, ay] = pts[0];
    const [bx, by] = pts[pts.length - 1];
    const ex = bx - ax;
    const ey = by - ay;
    const l = Math.hypot(ex, ey) || 1;
    let far = 0;
    let fi = 0;
    for (let i = 1; i < pts.length - 1; i++) {
      const d = Math.abs((pts[i][0] - ax) * ey - (pts[i][1] - ay) * ex) / l;
      if (d > far) {
        far = d;
        fi = i;
      }
    }
    if (far <= eps) return [pts[0], pts[pts.length - 1]];
    const a = dp(pts.slice(0, fi + 1));
    const b = dp(pts.slice(fi));
    return [...a.slice(0, -1), ...b];
  };
  let fi = 0;
  let far = 0;
  for (let i = 1; i < loop.length; i++) {
    const d = Math.hypot(loop[i][0] - loop[0][0], loop[i][1] - loop[0][1]);
    if (d > far) {
      far = d;
      fi = i;
    }
  }
  const a = dp(loop.slice(0, fi + 1));
  const b = dp([...loop.slice(fi), loop[0]]);
  return [...a.slice(0, -1), ...b.slice(0, -1)];
}

export { sourceInfo, loadImage, weaponMask, largestComponent, traceLoops, area, simplify };
