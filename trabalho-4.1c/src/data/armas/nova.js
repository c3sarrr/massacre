// Receita da Nova de massinha (Fase 4.1): coronha e receptor moldados numa peça só em grafite, cano e tubo do carregador em
// grafite claro, bomba com os sulcos, a massa de mira em bolinha e o gatilho na cor de acento dos dois lados. Referencial:
// +X para a boca, +Y para cima, +Z para a direita, origem no eixo do cano sobre o gatilho (u). Formato em
// docs/phases/phase-4.md, seção 4.1, "Receita"; o corpo é JSON puro.
export default {
  "id": "nova",
  "version": 1,
  "refs": { "planta": "tools/blender/refs/nova.json", "pins": ["QPG3", "QCG1", "QPL5"] },
  "materials": { "corpo": "grafite", "claro": "grafiteClaro", "acento": "acento", "acento2": "acento2" },
  "groups": {
    "corpo": { "pivot": [0, 0, 0] },
    "bomba": { "pivot": [13.3, -1.2, 0], "axis": [-1, 0, 0] },
    "gatilho": { "pivot": [-0.4, -1.7, 0], "axis": [0, 0, 1] }
  },
  "anchors": {
    "maoDireita": { "pos": [-5.84, -0.99, 1.61], "rot": [1.5708, -0.6, 0], "pose": "empunhadura" },
    "maoEsquerda": { "pos": [12.5, -1.93, -2.35], "rot": [-2.608, 1.28, 0], "pose": "bomba" },
    "boca": { "pos": [24.9, 0, 0], "rot": [0, 0, 0] },
    "ejecao": { "pos": [4.3, -0.35, 0.95], "rot": [0, -1.471, 0.244] }
  },
  "parts": [
    { "name": "coronha", "group": "corpo", "mat": "corpo", "shape": "profile", "h": 0.86, "round": 0.45, "corner": 0.5, "points": [[-14.3, -1.647], [-14.123, -5.56], [-14.013, -6.157], [-6.142, -3.438], [-5.921, -3.438], [-5.744, -3.703], [-5.39, -3.814], [-4.55, -3.836], [-4.108, -3.747], [-3.931, -2.974], [-3.621, -2.421], [-3.312, -2.111], [-2.648, -1.736], [-2.361, -1.669], [-1.65, -1.716], [-1.65, 0.298], [-2.98, -0.365], [-4.793, -1.006], [-5.302, -1.006], [-5.567, -0.652], [-5.81, -0.652], [-13.371, -1.382], [-14.057, -1.47]] },
    { "name": "receptor", "group": "corpo", "mat": "corpo", "shape": "profile", "h": 0.74, "round": 0.4, "corner": 0.35, "points": [[-2.1, 0.111], [-2.1, -1.669], [-1.39, -1.8], [1.607, -1.8], [1.973, -1.736], [9.5, -1.8], [9.5, 0.426], [7.036, 0.475], [6.35, 0.542], [6.306, 0.674], [1.973, 0.674], [1.884, 1.072], [1.199, 1.117], [0.668, 1.47], [0.469, 1.47], [0.071, 1.117], [-0.039, 0.652], [-0.703, 0.586], [-1.454, 0.387]] },
    { "name": "guardaMato", "group": "corpo", "mat": "corpo", "shape": "profile", "h": 0.6, "round": 0.26, "corner": 0.24, "points": [[1.8, -1.7], [1.8, -3.1], [1.35, -3.7], [-1.05, -3.7], [-1.65, -3.3], [-1.7, -1.7], [-1.1, -1.7], [-1.1, -3.1], [1.25, -3.1], [1.25, -1.7]] },
    { "name": "guardaVao", "group": "corpo", "mat": "corpo", "shape": "profile", "op": "subtract", "h": 1.6, "round": 0, "corner": 0.26, "points": [[-1.1, -3.1], [1.25, -3.1], [1.25, -1.62], [-1.1, -1.62]] },
    { "name": "janelaEjecao", "group": "corpo", "mat": "corpo", "shape": "roundBox", "op": "subtract", "pos": [4.3, -0.35, 0.92], "size": [1.5, 0.38, 0.3], "r": 0.12 },
    { "name": "cano", "group": "corpo", "mat": "claro", "shape": "lathe", "corner": 0.1, "points": [[2.9, 0], [2.9, 0.62], [24.88, 0.6], [24.88, 0]] },
    { "name": "tuboCarregador", "group": "corpo", "mat": "claro", "shape": "lathe", "pos": [0, -1.1, 0], "corner": 0.3, "points": [[8.9, 0], [8.9, 0.6], [23.3, 0.6], [23.75, 0.5], [23.8, 0]] },
    { "name": "massaMira", "group": "corpo", "mat": "acento", "shape": "sphere", "pos": [23.45, 0.72, 0], "r": 0.62 },
    { "name": "alma", "group": "corpo", "mat": "claro", "shape": "cylinder", "op": "subtract", "pos": [24.7, 0, 0], "rot": [0, 0, 1.5708], "r": 0.3, "h": 0.6, "round": 0.06 },
    { "name": "bomba", "group": "bomba", "mat": "corpo", "shape": "profile", "h": 0.92, "round": 0.52, "corner": 0.45, "points": [[9.45, -1.985], [10.86, -2.156], [14.42, -2.156], [16.476, -2.089], [16.565, -1.957], [16.852, -1.912], [16.874, -2.443], [16.985, -2.576], [17.118, -2.288], [17.15, -0.28], [9.45, -0.28]] },
    { "name": "bombaSulco1D", "group": "bomba", "mat": "corpo", "shape": "capsule", "op": "subtract", "r": 0.13, "a": [10.3, -0.85, 0.96], "b": [16.3, -0.85, 0.96] },
    { "name": "bombaSulco2D", "group": "bomba", "mat": "corpo", "shape": "capsule", "op": "subtract", "r": 0.13, "a": [10.3, -1.3, 0.96], "b": [16.3, -1.3, 0.96] },
    { "name": "bombaSulco3D", "group": "bomba", "mat": "corpo", "shape": "capsule", "op": "subtract", "r": 0.13, "a": [10.3, -1.75, 0.96], "b": [16.3, -1.75, 0.96] },
    { "name": "bombaSulco1E", "group": "bomba", "mat": "corpo", "shape": "capsule", "op": "subtract", "r": 0.13, "a": [10.3, -0.85, -0.96], "b": [16.3, -0.85, -0.96] },
    { "name": "bombaSulco2E", "group": "bomba", "mat": "corpo", "shape": "capsule", "op": "subtract", "r": 0.13, "a": [10.3, -1.3, -0.96], "b": [16.3, -1.3, -0.96] },
    { "name": "bombaSulco3E", "group": "bomba", "mat": "corpo", "shape": "capsule", "op": "subtract", "r": 0.13, "a": [10.3, -1.75, -0.96], "b": [16.3, -1.75, -0.96] },
    { "name": "gatilho", "group": "gatilho", "mat": "acento2", "shape": "profile", "h": 0.6, "round": 0.22, "corner": 0.16, "points": [[-0.2, -1.65], [-0.25, -2.2], [-0.5, -2.6], [-0.85, -2.78], [-0.95, -2.55], [-0.69, -2.3], [-0.55, -1.95], [-0.55, -1.65]] }
  ]
};
