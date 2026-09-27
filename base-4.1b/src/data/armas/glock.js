// Receita da Glock-18 de massinha (Fase 4.1): armação e empunhadura com as ondas dos dedos em grafite, ferrolho em grafite
// claro com as serrilhas em cortes de estilete e o cano marcado na boca, a massa de mira da frente, o seletor de rajada, o
// gatilho e a base do carregador na cor da facção. Referencial: +X para a boca, +Y para cima, +Z para a direita, origem no
// eixo do cano sobre o gatilho (u). Formato em docs/phases/phase-4.md, seção 4.1, "Receita"; o corpo é JSON puro.
export default {
  "id": "glock",
  "version": 1,
  "refs": { "planta": "tools/blender/refs/glock.json", "pins": ["QPG1", "QPG5", "QPL6", "QCG1"] },
  "materials": { "corpo": "grafite", "claro": "grafiteClaro", "acento": "acento", "acento2": "acento2" },
  "groups": {
    "corpo": { "pivot": [0, 0, 0] },
    "slide": { "pivot": [0.65, 0.08, 0], "axis": [-1, 0, 0] },
    "carregador": { "pivot": [-2.2, -4.15, 0], "axis": [-0.252, -0.968, 0] },
    "gatilho": { "pivot": [-0.05, -0.95, 0], "axis": [0, 0, 1] }
  },
  "anchors": {
    "maoDireita": { "pos": [-3.21, -1.64, 1.45], "rot": [1.5708, -0.32, 0], "pose": "empunhadura" },
    "maoEsquerda": { "pos": [-2.64, -2.14, -1.45], "rot": [-1.5708, 0.32, 0], "pose": "apoio" },
    "boca": { "pos": [4.05, 0, 0], "rot": [0, 0, 0] },
    "ejecao": { "pos": [1.1, 0.6, 0.45], "rot": [0, -1.768, 0.532] }
  },
  "parts": [
    { "name": "armacao", "group": "corpo", "mat": "corpo", "shape": "profile", "h": 0.62, "round": 0.26, "corner": 0.2, "points": [[-2.81, -0.414], [-2.744, -0.58], [-2.354, -0.688], [-2.195, -1], [1.537, -1], [1.702, -0.92], [3.818, -0.862], [4.025, -0.613], [4.009, -0.3], [-2.761, -0.3]] },
    { "name": "empunhadura", "group": "corpo", "mat": "corpo", "shape": "profile", "h": 0.7, "round": 0.34, "corner": 0.3, "points": [[-3.25, -3.741], [-3.25, -3.865], [-3.134, -4.014], [-2.852, -4.122], [-2.951, -4.214], [-2.962, -4.36], [-1.531, -4.36], [-1.417, -4.238], [-1.417, -4.081], [-1.184, -3.873], [-1.201, -3.616], [-1.077, -3.301], [-0.911, -3.152], [-0.911, -2.812], [-0.795, -2.621], [-0.662, -2.538], [-0.645, -2.214], [-0.562, -2.015], [-0.4, -1.868], [-0.4, -0.3], [-2.794, -0.34], [-2.744, -0.58], [-2.354, -0.688], [-2.238, -0.837], [-2.188, -1.103], [-2.562, -2.198], [-3.084, -3.102]] },
    { "name": "guardaMato", "group": "corpo", "mat": "corpo", "shape": "profile", "h": 0.6, "round": 0.24, "corner": 0.22, "points": [[1.7, -0.85], [1.7, -2.25], [1.3, -2.65], [-0.4, -2.65], [-0.8, -2.2], [-0.75, -1.9], [-0.35, -1.9], [-0.35, -2.1], [1.3, -2.1], [1.3, -0.85]] },
    { "name": "guardaVao", "group": "corpo", "mat": "corpo", "shape": "profile", "op": "subtract", "h": 1.4, "round": 0, "corner": 0.24, "points": [[-0.35, -2.1], [1.3, -2.1], [1.3, -0.95], [-0.35, -0.95]] },
    { "name": "ferrolho", "group": "slide", "mat": "claro", "shape": "profile", "h": 0.62, "round": 0.28, "corner": 0.2, "points": [[-2.798, -0.36], [4.016, -0.36], [4.04, 0.349], [3.967, 0.449], [3.767, 0.52], [3.596, 0.52], [3.577, 0.473], [-2.653, 0.498], [-2.761, 0.324]] },
    { "name": "serrilhaDireita", "group": "slide", "mat": "claro", "shape": "profile", "op": "subtract", "pos": [0, 0, 0.66], "h": 0.14, "round": 0, "corner": 0.03, "points": [[-1.15, 1.15], [-2.15, 1.15], [-2.095, 0.95], [-2.095, -0.22], [-2.005, -0.22], [-2.005, 0.95], [-1.895, 0.95], [-1.895, -0.22], [-1.805, -0.22], [-1.805, 0.95], [-1.695, 0.95], [-1.695, -0.22], [-1.605, -0.22], [-1.605, 0.95], [-1.495, 0.95], [-1.495, -0.22], [-1.405, -0.22], [-1.405, 0.95], [-1.295, 0.95], [-1.295, -0.22], [-1.205, -0.22], [-1.205, 0.95]] },
    { "name": "serrilhaEsquerda", "group": "slide", "mat": "claro", "shape": "profile", "op": "subtract", "pos": [0, 0, -0.66], "h": 0.14, "round": 0, "corner": 0.03, "points": [[-1.15, 1.15], [-2.15, 1.15], [-2.095, 0.95], [-2.095, -0.22], [-2.005, -0.22], [-2.005, 0.95], [-1.895, 0.95], [-1.895, -0.22], [-1.805, -0.22], [-1.805, 0.95], [-1.695, 0.95], [-1.695, -0.22], [-1.605, -0.22], [-1.605, 0.95], [-1.495, 0.95], [-1.495, -0.22], [-1.405, -0.22], [-1.405, 0.95], [-1.295, 0.95], [-1.295, -0.22], [-1.205, -0.22], [-1.205, 0.95]] },
    { "name": "janelaEjecao", "group": "slide", "mat": "claro", "shape": "roundBox", "op": "subtract", "pos": [1.1, 0.55, 0.36], "size": [0.75, 0.2, 0.3], "r": 0.08 },
    { "name": "alma", "group": "slide", "mat": "claro", "shape": "cylinder", "op": "subtract", "pos": [3.95, 0, 0], "rot": [0, 0, 1.5708], "r": 0.22, "h": 0.3, "round": 0.04 },
    { "name": "bordaCano", "group": "slide", "mat": "claro", "shape": "torus", "op": "subtract", "pos": [4.07, 0, 0], "rot": [0, 0, 1.5708], "r": 0.05, "R": 0.38 },
    { "name": "miraTras", "group": "slide", "mat": "claro", "shape": "profile", "h": 0.6, "round": 0.12, "corner": 0.08, "points": [[-2.5, 0.42], [-2.05, 0.42], [-2.07, 0.7], [-2.47, 0.72]] },
    { "name": "miraTrasEntalhe", "group": "slide", "mat": "claro", "shape": "roundBox", "op": "subtract", "pos": [-2.28, 0.78, 0], "size": [0.4, 0.14, 0.12], "r": 0.04 },
    { "name": "miraFrente", "group": "slide", "mat": "acento", "shape": "profile", "h": 0.6, "round": 0.12, "corner": 0.08, "points": [[3.59, 0.42], [3.85, 0.42], [3.83, 0.66], [3.61, 0.67]] },
    { "name": "seletor", "group": "slide", "mat": "acento2", "shape": "profile", "pos": [0, 0, -0.5], "h": 0.6, "round": 0.2, "corner": 0.14, "points": [[-2.35, 0.08], [-1.57, 0.1], [-1.5, 0.3], [-2.3, 0.36]] },
    { "name": "gatilho", "group": "gatilho", "mat": "acento2", "shape": "profile", "h": 0.6, "round": 0.2, "corner": 0.14, "points": [[0.1, -0.95], [0.05, -1.4], [-0.1, -1.75], [-0.3, -1.9], [-0.37, -1.7], [-0.23, -1.5], [-0.2, -1.15], [-0.2, -0.95]] },
    { "name": "pente", "group": "carregador", "mat": "corpo", "shape": "profile", "h": 0.6, "round": 0.26, "corner": 0.2, "points": [[-2.9, -4.15], [-1.55, -4.15], [-0.85, -1.35], [-2.1, -1.2]] },
    { "name": "penteBase", "group": "carregador", "mat": "acento", "shape": "profile", "h": 0.74, "round": 0.24, "corner": 0.2, "points": [[-3.1, -4.021], [-2.852, -4.122], [-2.951, -4.214], [-2.96, -4.388], [-1.707, -4.413], [-1.558, -4.388], [-1.417, -4.238], [-1.417, -4.081], [-1.35, -4.02]] }
  ]
};
