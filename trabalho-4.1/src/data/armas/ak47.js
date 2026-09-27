// Receita da AK-47 de massinha (Fase 4.1): receptor e tampa em grafite, coronha e guarda-mãos de madeira riscada a palito,
// empunhadura de baquelite, carregador curvo com a base na cor da facção. Referencial: +X para a boca, +Y para cima,
// +Z para a direita, origem no eixo do cano sobre o gatilho (u). Formato em docs/phases/phase-4.md, seção 4.1, "Receita";
// o corpo é JSON puro (o exportador do Blender, tools/blender/massacre_armas.py, grava; o importador lê).
export default {
  "id": "ak47",
  "version": 1,
  "refs": { "planta": "tools/blender/refs/ak47.json", "pins": ["QPG2", "QPL4", "QRF1", "QCG1"] },
  "materials": { "corpo": "grafite", "madeira": "madeira", "empunhadura": "madeiraEscura", "ferrolho": "grafiteClaro", "acento": "acento", "acento2": "acento2" },
  "groups": {
    "corpo": { "pivot": [0, 0, 0] },
    "carregador": { "pivot": [4.65, -1.3, 0], "axis": [0, 0, 1] },
    "ferrolho": { "pivot": [4.7, 0.3, 0.78], "axis": [-1, 0, 0] },
    "gatilho": { "pivot": [-0.28, -1.42, 0], "axis": [0, 0, 1] }
  },
  "anchors": {
    "maoDireita": { "pos": [-4.2, -2.95, 1.4], "rot": [1.5708, -0.18, 0], "pose": "empunhadura" },
    "maoEsquerda": { "pos": [8.81, -0.88, -2.22], "rot": [-2.608, 1.28, 0], "pose": "guardaMao" },
    "boca": { "pos": [21.2, 0, 0], "rot": [0, 0, 0] },
    "ejecao": { "pos": [2.65, 0.3, 1], "rot": [0, -1.816, 0.327] }
  },
  "parts": [
    { "name": "coronha", "group": "corpo", "mat": "madeira", "shape": "profile", "h": 0.8, "round": 0.42, "corner": 0.6, "points": [[-13.4, -1.296], [-12.732, -5.184], [-12.615, -5.361], [-12.281, -5.4], [-6.586, -2.69], [-4.269, -1.767], [-3.387, -1.571], [-3.1, -0.637], [-3.1, 0.853], [-3.621, 0.511], [-3.503, 0.393], [-3.66, 0.216], [-3.68, 0], [-4.406, -0.02], [-6.724, -0.452], [-7.057, -0.432], [-7.627, -0.177], [-7.961, -0.196], [-13.282, -1.119]] },
    { "name": "soleira", "group": "corpo", "mat": "corpo", "shape": "profile", "h": 0.86, "round": 0.4, "corner": 0.4, "points": [[-13.4, -1.296], [-12.929, -3.633], [-12.732, -5.184], [-12.615, -5.361], [-12.281, -5.4], [-12.25, -0.94], [-13.282, -1.119]] },
    { "name": "empunhadura", "group": "corpo", "mat": "empunhadura", "shape": "profile", "h": 0.64, "round": 0.45, "corner": 0.55, "points": [[-3.935, -4.772], [-3.778, -5.263], [-3.562, -5.498], [-3.228, -5.655], [-2.403, -5.636], [-2.246, -5.498], [-1.932, -4.34], [-1.323, -2.945], [-1.1, -2.643], [-1.1, -1.2], [-3.273, -1.2], [-3.385, -1.61], [-3.307, -1.649], [-3.13, -2.612]] },
    { "name": "receptor", "group": "corpo", "mat": "corpo", "shape": "profile", "h": 0.78, "round": 0.3, "corner": 0.3, "points": [[-3.25, -1.52], [4.599, -1.52], [4.646, -1.237], [5.5, -1.206], [5.5, 0.62], [-3.25, 0.62]] },
    { "name": "tampa", "group": "corpo", "mat": "corpo", "shape": "profile", "h": 0.72, "round": 0.55, "corner": 0.45, "points": [[-3, 1], [-3, 0.3], [5.4, 0.3], [5.4, 1.393], [-2.462, 1.355], [-2.698, 1.296]] },
    { "name": "alcaMira", "group": "corpo", "mat": "corpo", "shape": "profile", "h": 0.68, "round": 0.3, "corner": 0.22, "points": [[5.05, 1.391], [5.05, 0.35], [6.35, 0.35], [6.35, 1.767], [6.237, 1.866], [5.746, 1.728], [5.55, 1.905], [5.589, 1.63], [5.981, 1.551], [5.648, 1.512], [5.608, 1.394]] },
    { "name": "guardaMaoCima", "group": "corpo", "mat": "madeira", "shape": "profile", "h": 0.62, "round": 0.5, "corner": 0.45, "points": [[6.25, 1.843], [6.25, 0.42], [12.85, 0.42], [12.85, 1.375], [12.737, 1.532], [8.475, 1.63], [8.318, 1.434], [8.161, 1.767], [7.847, 1.728], [7.572, 1.846], [6.296, 1.767]] },
    { "name": "guardaMaoBaixo", "group": "corpo", "mat": "madeira", "shape": "profile", "h": 0.84, "round": 0.5, "corner": 0.5, "points": [[5.45, 0.46], [5.45, -1.208], [6.61, -1.1], [6.845, -1.139], [6.983, -1.375], [7.336, -1.394], [8.161, -1.139], [9.654, -1.1], [12.85, -0.785], [12.85, 0.46]] },
    { "name": "anelFrente", "group": "corpo", "mat": "corpo", "shape": "roundBox", "pos": [13, -0.2, 0], "size": [0.6, 0.74, 0.9], "r": 0.34 },
    { "name": "blocoGas", "group": "corpo", "mat": "corpo", "shape": "profile", "h": 0.66, "round": 0.36, "corner": 0.35, "points": [[12.8, 1.468], [12.8, 0.18], [17, 0.18], [17, 0.358], [16.605, 0.511], [15.996, 1.316], [13.385, 1.316], [12.835, 1.375]] },
    { "name": "cano", "group": "corpo", "mat": "corpo", "shape": "lathe", "corner": 0.1, "points": [[5.6, 0], [5.6, 0.62], [16.7, 0.62], [20.58, 0.6], [20.58, 0]] },
    { "name": "baseMira", "group": "corpo", "mat": "corpo", "shape": "profile", "h": 0.64, "round": 0.34, "corner": 0.3, "points": [[19.35, 0.288], [19.35, -0.643], [20.473, -0.648], [20.62, -0.318], [20.611, 1.25], [19.806, 1.25], [19.433, 0.53], [19.433, 0.295]] },
    { "name": "massaMira", "group": "corpo", "mat": "acento", "shape": "capsule", "r": 0.6, "a": [20.08, 1.15, 0], "b": [20.08, 1.42, 0] },
    { "name": "freio", "group": "corpo", "mat": "corpo", "shape": "lathe", "corner": 0.14, "points": [[20.3, 0], [20.3, 0.63], [21.2, 0.61], [21.2, 0]] },
    { "name": "freioInclinado", "group": "corpo", "mat": "corpo", "shape": "roundBox", "op": "subtract", "pos": [21.48, 0.62, 0], "rot": [0, 0, -0.62], "size": [0.45, 0.62, 1.2], "r": 0.08 },
    { "name": "alma", "group": "corpo", "mat": "corpo", "shape": "cylinder", "op": "subtract", "pos": [21, 0, 0], "rot": [0, 0, 1.5708], "r": 0.25, "h": 0.62, "round": 0.06 },
    { "name": "guardaMato", "group": "corpo", "mat": "corpo", "shape": "profile", "h": 0.6, "round": 0.28, "corner": 0.26, "points": [[2, -1.3], [1.95, -3.05], [1.5, -3.5], [-1.15, -3.5], [-1.85, -3.05], [-1.9, -2.35], [-1.2, -2.5], [-1.1, -2.88], [1.1, -2.88], [1.38, -2.6], [1.4, -1.3]] },
    { "name": "seletor", "group": "corpo", "mat": "acento2", "shape": "profile", "pos": [0, 0, 0.7], "h": 0.6, "round": 0.26, "corner": 0.2, "points": [[-3.15, 0.35], [-3, 0.74], [-2.6, 0.82], [0.2, 0.52], [0.65, 0.3], [0.7, -0.45], [0.25, -0.52], [0.1, 0], [-2.4, -0.06], [-3, 0]] },
    { "name": "janelaEjecao", "group": "corpo", "mat": "corpo", "shape": "roundBox", "op": "subtract", "pos": [2.65, 0.3, 0.98], "size": [1.75, 0.34, 0.38], "r": 0.1 },
    { "name": "ferrolhoCorpo", "group": "ferrolho", "mat": "ferrolho", "shape": "roundBox", "pos": [2.65, 0.3, 0.1], "size": [1.6, 0.6, 0.6], "r": 0.24 },
    { "name": "alavanca", "group": "ferrolho", "mat": "ferrolho", "shape": "tube", "r": 0.6, "points": [[4.65, 0.3, 0.55], [4.75, 0.36, 1.2]] },
    { "name": "alavancaBola", "group": "ferrolho", "mat": "ferrolho", "shape": "sphere", "pos": [4.78, 0.38, 1.45], "r": 0.66 },
    { "name": "gatilho", "group": "gatilho", "mat": "acento2", "shape": "profile", "h": 0.6, "round": 0.22, "corner": 0.16, "points": [[-0.05, -1.3], [-0.1, -1.95], [-0.4, -2.4], [-0.85, -2.62], [-1, -2.35], [-0.7, -2.05], [-0.52, -1.6], [-0.52, -1.3]] },
    { "name": "pente", "group": "carregador", "mat": "corpo", "shape": "profile", "h": 0.62, "round": 0.3, "corner": 0.35, "points": [[2.18, -1.28], [2.18, -1.887], [2.879, -3.829], [3.272, -4.615], [4.47, -6.303], [5.412, -7.226], [6.217, -7.8], [7.443, -5.81], [6.315, -4.831], [5.333, -3.495], [4.803, -2.317], [4.587, -1.394], [4.646, -1.28], [6.888, -1.28], [7.336, -1.394], [7.705, -1.28]] },
    { "name": "penteBase", "group": "carregador", "mat": "acento", "shape": "profile", "h": 0.68, "round": 0.3, "corner": 0.3, "points": [[6.028, -7.686], [6.492, -8.031], [6.649, -8.051], [7.592, -6.676], [7.572, -6.559], [7.867, -6.068], [7.279, -5.657]] },
    { "name": "penteFriso1D", "group": "carregador", "mat": "corpo", "shape": "tube", "op": "subtract", "r": 0.18, "points": [[2.95, -2.4, 0.66], [3.85, -4.4, 0.66], [5.35, -6.35, 0.66]] },
    { "name": "penteFriso2D", "group": "carregador", "mat": "corpo", "shape": "tube", "op": "subtract", "r": 0.18, "points": [[4.05, -2.2, 0.66], [4.9, -4.05, 0.66], [6.3, -5.9, 0.66]] },
    { "name": "penteFriso1E", "group": "carregador", "mat": "corpo", "shape": "tube", "op": "subtract", "r": 0.18, "points": [[2.95, -2.4, -0.66], [3.85, -4.4, -0.66], [5.35, -6.35, -0.66]] },
    { "name": "penteFriso2E", "group": "carregador", "mat": "corpo", "shape": "tube", "op": "subtract", "r": 0.18, "points": [[4.05, -2.2, -0.66], [4.9, -4.05, -0.66], [6.3, -5.9, -0.66]] }
  ]
};
