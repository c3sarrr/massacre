// Receita da P90 de massinha (Fase 4.1): corpo bullpup em grafite com o buraco da empunhadura e a janela do gatilho, alojamento
// da mira, carregador por cima em grafite claro, a mira de anel, o seletor, o gatilho e a ponta do carregador na cor de acento
// dos dois lados. Referencial: +X para a boca, +Y para cima, +Z para a direita, origem no eixo do cano sobre o gatilho (u).
// Formato em docs/phases/phase-4.md, seção 4.1, "Receita"; o corpo é JSON puro.
export default {
  "id": "p90",
  "version": 1,
  "refs": { "planta": "tools/blender/refs/p90.json", "pins": ["QSG2", "QCG1", "QPL1"] },
  "materials": { "corpo": "grafite", "claro": "grafiteClaro", "acento": "acento", "acento2": "acento2" },
  "groups": {
    "corpo": { "pivot": [0, 0, 0] },
    "carregador": { "pivot": [-7.9, 1, 0], "axis": [0, 1, 0] },
    "gatilho": { "pivot": [-0.45, -0.8, 0], "axis": [0, 0, 1] }
  },
  "anchors": {
    "maoDireita": { "pos": [-3.41, -1.28, 1.77], "rot": [1.5708, -0.1, 0], "pose": "empunhadura" },
    "maoEsquerda": { "pos": [1.91, -2.98, -2.39], "rot": [-2.608, 1.28, 0], "pose": "guardaMao" },
    "boca": { "pos": [5.6, 0, 0], "rot": [0, 0, 0] },
    "ejecao": { "pos": [-4.2, -3.9, 0], "rot": [0, -0.588, -1.392] },
    "mira": { "pos": [-0.75, 2.72, 0], "rot": [0, 0, 0] }
  },
  "parts": [
    { "name": "corpo", "group": "corpo", "mat": "corpo", "shape": "profile", "h": 1.05, "round": 0.56, "corner": 0.5, "points": [[-14.1, -2.924], [-14.076, -3.078], [-13.78, -3.125], [-9.119, -3.125], [-9.048, -2.959], [-8.668, -2.947], [-6.379, -3.683], [-6.225, -3.92], [-4.719, -3.932], [-3.497, -3.683], [-2.714, -3.256], [-1.991, -2.591], [-1.255, -2.52], [-1.006, -2.615], [-0.888, -2.829], [-1.101, -3.884], [-1.006, -3.955], [0.512, -3.92], [1.093, -3.683], [1.568, -3.267], [1.935, -2.58], [2.018, -1.832], [2.232, -1.607], [3.074, -1.643], [3.24, -1.868], [3.252, -2.402], [3.702, -2.449], [3.85, -0.864], [3.536, -0.421], [3.85, -0.415], [3.814, 1.38], [-14.076, 1.38], [-13.958, -1.251]] },
    { "name": "buracoEmpunhadura", "group": "corpo", "mat": "corpo", "shape": "profile", "op": "subtract", "h": 1.8, "round": 0, "corner": 0.35, "points": [[-5.406, -0.7294], [-4.078, -0.7413], [-3.817, -0.8243], [-3.627, -0.9903], [-3.521, -1.2038], [-3.497, -1.4529], [-3.568, -1.6901], [-3.639, -1.7968], [-3.817, -1.951], [-5.027, -2.4966], [-5.193, -2.5322], [-5.406, -2.5322], [-5.572, -2.4966], [-5.774, -2.4017], [-5.999, -2.212], [-6.154, -1.951], [-6.213, -1.6664], [-6.189, -1.4054], [-6.082, -1.1445], [-5.928, -0.9548], [-5.667, -0.7887]] },
    { "name": "janelaGatilho", "group": "corpo", "mat": "corpo", "shape": "profile", "op": "subtract", "h": 1.8, "round": 0, "corner": 0.42, "points": [[-0.85, -2.45], [1.05, -2.45], [1.05, -0.8], [-0.85, -0.8]] },
    { "name": "manejo", "group": "corpo", "mat": "corpo", "shape": "capsule", "r": 0.6, "a": [2.2, 0.45, -1.55], "b": [2.2, 0.45, 1.55] },
    { "name": "seletor", "group": "corpo", "mat": "acento", "shape": "cylinder", "pos": [0.1, -4.12, 0], "r": 0.72, "h": 0.6, "round": 0.24 },
    { "name": "alojamentoMira", "group": "corpo", "mat": "corpo", "shape": "profile", "h": 0.82, "round": 0.45, "corner": 0.35, "points": [[-2.65, 1.91], [-2.65, 1.3], [3.55, 1.3], [3.55, 3.047], [3.513, 3.113], [2.777, 3.09], [2.754, 3.813], [-0.627, 3.825], [-0.662, 3.398], [-0.84, 3.22], [-2.097, 3.125]] },
    { "name": "alojamentoVao", "group": "corpo", "mat": "corpo", "shape": "profile", "op": "subtract", "h": 1.4, "round": 0, "corner": 0.2, "points": [[-1.125, 2.0222], [-0.745, 1.9866], [0.275, 1.7968], [0.761, 1.7257], [0.939, 1.7257], [1.057, 1.6901], [1.722, 1.5952], [1.817, 1.5596], [1.947, 1.441], [1.71, 1.4292], [1.662, 1.4648], [-1.374, 1.4766], [-1.208, 1.7968], [-1.16, 1.9747]] },
    { "name": "miraAnel", "group": "corpo", "mat": "acento", "shape": "torus", "pos": [-0.75, 2.72, 0], "rot": [0, 0, 1.5708], "r": 0.6, "R": 0.78 },
    { "name": "miraFuro", "group": "corpo", "mat": "acento", "shape": "cylinder", "op": "subtract", "pos": [-0.75, 2.72, 0], "rot": [0, 0, 1.5708], "r": 0.3, "h": 1.2, "round": 0.05 },
    { "name": "cano", "group": "corpo", "mat": "claro", "shape": "lathe", "corner": 0.14, "points": [[3.2, 0], [3.2, 0.62], [5.3, 0.6], [5.6, 0.5], [5.6, 0]] },
    { "name": "quebraChamaD", "group": "corpo", "mat": "claro", "shape": "capsule", "op": "subtract", "r": 0.16, "a": [4.15, 0, 0.62], "b": [5.15, 0, 0.62] },
    { "name": "quebraChamaE", "group": "corpo", "mat": "claro", "shape": "capsule", "op": "subtract", "r": 0.16, "a": [4.15, 0, -0.62], "b": [5.15, 0, -0.62] },
    { "name": "alma", "group": "corpo", "mat": "claro", "shape": "cylinder", "op": "subtract", "pos": [5.4, 0, 0], "rot": [0, 0, 1.5708], "r": 0.24, "h": 0.6, "round": 0.06 },
    { "name": "gatilho", "group": "gatilho", "mat": "acento2", "shape": "profile", "h": 0.6, "round": 0.22, "corner": 0.16, "points": [[-0.3, -0.75], [-0.35, -1.3], [-0.55, -1.75], [-0.82, -2], [-0.9, -1.78], [-0.7, -1.5], [-0.64, -1.1], [-0.64, -0.75]] },
    { "name": "pente", "group": "carregador", "mat": "claro", "shape": "profile", "h": 0.9, "round": 0.42, "corner": 0.35, "points": [[-13.2, 1.548], [-13.2, 0.35], [-2.75, 0.35], [-2.75, 1.62], [-2.856, 1.489]] },
    { "name": "penteBase", "group": "carregador", "mat": "acento", "shape": "profile", "h": 0.96, "round": 0.4, "corner": 0.3, "points": [[-13.8, 1.544], [-13.8, 0.3], [-13.1, 0.3], [-13.1, 1.546]] }
  ]
};
