// Receita da AWP de massinha (Fase 4.1): chassi de coronha verde-oliva com o buraco do polegar, ação redonda, luneta com as
// torres, cano pesado e freio de boca em grafite, a bola da alavanca do ferrolho e a base do carregador na cor de acento dos
// dois lados. Referencial: +X para a boca, +Y para cima, +Z para a direita, origem no eixo do cano sobre o gatilho (u).
// Formato em docs/phases/phase-4.md, seção 4.1, "Receita"; o corpo é JSON puro.
export default {
  "id": "awp",
  "version": 1,
  "refs": { "planta": "tools/blender/refs/awp.json", "pins": ["QPG8", "QRF4", "QCG1", "NFS1"] },
  "materials": { "corpo": "verdeOliva", "metal": "grafite", "claro": "grafiteClaro", "acento": "acento", "acento2": "acento2" },
  "groups": {
    "corpo": { "pivot": [0, 0, 0] },
    "carregador": { "pivot": [11.2, -2.2, 0], "axis": [0, -1, 0] },
    "alavanca": { "pivot": [-1, 0.26, 0], "axis": [1, 0, 0] },
    "gatilho": { "pivot": [-0.5, -2.35, 0], "axis": [0, 0, 1] }
  },
  "anchors": {
    "maoDireita": { "pos": [-3.48, -2.25, 1.61], "rot": [1.5708, -0.3, 0], "pose": "empunhadura" },
    "maoEsquerda": { "pos": [14.51, -2.64, -2.59], "rot": [-2.608, 1.28, 0], "pose": "guardaMao" },
    "boca": { "pos": [34.2, 0, 0], "rot": [0, 0, 0] },
    "ejecao": { "pos": [3, 0.45, 0.8], "rot": [0, -1.67, 0.335] },
    "mira": { "pos": [-2.52, 2.05, 0], "rot": [0, 0, 0] }
  },
  "parts": [
    { "name": "coronha", "group": "corpo", "mat": "corpo", "shape": "profile", "h": 0.86, "round": 0.45, "corner": 0.5, "points": [[-13.9, 0.08], [-13.9, -5.263], [-13.637, -5.226], [-13.557, -5.467], [-10.1, -5.306], [-9.778, -4.181], [-9.456, -4.02], [-7.527, -3.939], [-6.884, -4.261], [-6.401, -4.824], [-5.678, -5.226], [-4.07, -5.467], [-3.185, -5.869], [-2.301, -5.949], [-1.899, -5.628], [-1.819, -4.583], [-1.577, -3.859], [-1.015, -3.377], [0.915, -3.457], [1.317, -2.894], [1.478, -2.894], [1.558, -3.377], [1.799, -3.296], [1.96, -3.618], [2.282, -3.618], [2.523, -3.859], [3.166, -3.859], [4.855, -3.618], [5.096, -3.135], [5.498, -2.814], [9.598, -2.09], [10.45, -2.168], [10.45, 0.2], [-1.216, 0.2], [-1.336, -0.402], [-6.401, -0.482], [-6.562, -0.241], [-7.125, -0.241], [-7.848, 0.08]] },
    { "name": "pocoCarregador", "group": "corpo", "mat": "corpo", "shape": "profile", "h": 0.8, "round": 0.4, "corner": 0.3, "points": [[10.4, -2.163], [12, -2.2], [12, 0.2], [10.4, 0.2]] },
    { "name": "guardaMaoFrente", "group": "corpo", "mat": "corpo", "shape": "profile", "h": 0.8, "round": 0.42, "corner": 0.45, "points": [[11.95, -3.135], [14.181, -3.135], [14.583, -3.055], [14.824, -2.734], [15.306, -2.734], [15.387, -2.894], [15.708, -2.894], [15.789, -2.734], [16.432, -2.734], [16.512, -2.975], [16.754, -2.975], [16.914, -3.216], [17.879, -3.296], [18.764, -3.135], [18.844, -2.653], [18.764, -2.01], [18.442, -1.608], [18.442, -0.804], [17.558, -0.724], [17.558, -0.563], [17.799, -0.482], [18.9, -0.482], [18.9, 0.2], [11.95, 0.2]] },
    { "name": "buracoPolegar", "group": "corpo", "mat": "corpo", "shape": "profile", "op": "subtract", "h": 1.6, "round": 0, "corner": 0.3, "points": [[-3.989, -2.0904], [-3.025, -2.0904], [-2.864, -2.3316], [-2.944, -2.9748], [-3.748, -3.6179], [-4.874, -3.5375], [-5.035, -3.2963], [-4.954, -2.7336], [-4.552, -2.3316]] },
    { "name": "guardaMato", "group": "corpo", "mat": "corpo", "shape": "profile", "h": 0.62, "round": 0.28, "corner": 0.26, "points": [[1.45, -2.5], [1.45, -3.6], [1, -4.1], [-1.1, -4.1], [-1.65, -3.7], [-1.7, -3], [-1.05, -3], [-1.05, -3.5], [0.9, -3.5], [0.9, -2.5]] },
    { "name": "guardaVao", "group": "corpo", "mat": "corpo", "shape": "profile", "op": "subtract", "h": 1.6, "round": 0, "corner": 0.28, "points": [[-1.05, -3.5], [0.9, -3.5], [0.9, -2.25], [-1.05, -2.25]] },
    { "name": "soleira", "group": "corpo", "mat": "metal", "shape": "profile", "h": 0.9, "round": 0.4, "corner": 0.35, "points": [[-14.2, -5.306], [-13.637, -5.226], [-13.557, -5.467], [-13.45, -5.462], [-13.45, 0.08], [-13.959, 0.08]] },
    { "name": "acao", "group": "corpo", "mat": "metal", "shape": "lathe", "pos": [0, 0.26, 0], "corner": 0.16, "points": [[-1.25, 0], [-1.25, 0.62], [11.7, 0.62], [11.7, 0]] },
    { "name": "trilho", "group": "corpo", "mat": "metal", "shape": "roundBox", "pos": [5.3, 0.85, 0], "size": [5, 0.6, 0.6], "r": 0.2 },
    { "name": "anelTras", "group": "corpo", "mat": "metal", "shape": "roundBox", "pos": [0.8, 1.45, 0], "size": [0.62, 0.62, 0.86], "r": 0.3 },
    { "name": "anelFrente", "group": "corpo", "mat": "metal", "shape": "roundBox", "pos": [9.8, 1.45, 0], "size": [0.62, 0.62, 0.86], "r": 0.3 },
    { "name": "luneta", "group": "corpo", "mat": "metal", "shape": "lathe", "pos": [0, 2.05, 0], "corner": 0.16, "points": [[-2.52, 0], [-2.52, 0.8], [-2.3, 0.9], [-1.25, 0.9], [-0.85, 0.76], [8, 0.76], [8.95, 1.12], [11.6, 1.14], [11.6, 0]] },
    { "name": "ocular", "group": "corpo", "mat": "metal", "shape": "cylinder", "op": "subtract", "pos": [-2.7, 2.05, 0], "rot": [0, 0, 1.5708], "r": 0.52, "h": 0.4, "round": 0.08 },
    { "name": "objetiva", "group": "corpo", "mat": "metal", "shape": "cylinder", "op": "subtract", "pos": [11.8, 2.05, 0], "rot": [0, 0, 1.5708], "r": 0.82, "h": 0.4, "round": 0.08 },
    { "name": "torreCima", "group": "corpo", "mat": "metal", "shape": "cylinder", "pos": [4.5, 3.12, 0], "r": 0.66, "h": 0.6, "round": 0.22 },
    { "name": "torreLado", "group": "corpo", "mat": "metal", "shape": "cylinder", "pos": [4.5, 2.05, 1.12], "rot": [1.5708, 0, 0], "r": 0.62, "h": 0.6, "round": 0.22 },
    { "name": "cano", "group": "corpo", "mat": "metal", "shape": "lathe", "corner": 0.1, "points": [[11.6, 0], [11.6, 0.66], [18.2, 0.64], [31.25, 0.6], [31.25, 0]] },
    { "name": "freio", "group": "corpo", "mat": "metal", "shape": "lathe", "corner": 0.16, "points": [[31.25, 0], [31.25, 0.8], [31.95, 0.8], [32.45, 0.68], [34.2, 0.66], [34.2, 0]] },
    { "name": "freioJanelaD", "group": "corpo", "mat": "metal", "shape": "roundBox", "op": "subtract", "pos": [33.2, 0, 0.72], "size": [0.42, 0.34, 0.3], "r": 0.1 },
    { "name": "freioJanelaE", "group": "corpo", "mat": "metal", "shape": "roundBox", "op": "subtract", "pos": [33.2, 0, -0.72], "size": [0.42, 0.34, 0.3], "r": 0.1 },
    { "name": "alma", "group": "corpo", "mat": "metal", "shape": "cylinder", "op": "subtract", "pos": [34, 0, 0], "rot": [0, 0, 1.5708], "r": 0.26, "h": 0.62, "round": 0.06 },
    { "name": "janelaEjecao", "group": "corpo", "mat": "metal", "shape": "roundBox", "op": "subtract", "pos": [3, 0.45, 0.72], "size": [1.3, 0.3, 0.3], "r": 0.1 },
    { "name": "ferrolho", "group": "alavanca", "mat": "claro", "shape": "lathe", "pos": [0, 0.26, 0], "corner": 0.14, "points": [[-1.95, 0], [-1.95, 0.6], [-1, 0.6], [-1, 0]] },
    { "name": "alavancaHaste", "group": "alavanca", "mat": "claro", "shape": "tube", "r": 0.6, "points": [[-1.35, 0.4, 0.4], [-1.55, 0.05, 1.2]] },
    { "name": "alavancaBola", "group": "alavanca", "mat": "acento", "shape": "sphere", "pos": [-1.65, -0.15, 1.55], "r": 0.74 },
    { "name": "gatilho", "group": "gatilho", "mat": "acento2", "shape": "profile", "h": 0.6, "round": 0.22, "corner": 0.16, "points": [[-0.35, -2.3], [-0.4, -2.85], [-0.6, -3.18], [-0.9, -3.36], [-1, -3.15], [-0.78, -2.9], [-0.66, -2.55], [-0.66, -2.3]] },
    { "name": "pente", "group": "carregador", "mat": "metal", "shape": "profile", "h": 0.62, "round": 0.3, "corner": 0.25, "points": [[10.48, -2.171], [10.563, -2.894], [10.684, -3], [11.92, -3], [11.92, -1.6], [10.48, -1.6]] },
    { "name": "penteBase", "group": "carregador", "mat": "acento", "shape": "profile", "h": 0.68, "round": 0.3, "corner": 0.28, "points": [[10.42, -2.95], [10.626, -2.95], [11.206, -3.457], [11.528, -3.457], [11.98, -3.135], [11.98, -2.95]] }
  ]
};
