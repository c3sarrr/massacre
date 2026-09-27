// Receita da faca de massinha (Fase 4.1): a espátula de modelar de aço com cabo torneado de madeira (CTL6, CTL7, CTL16),
// lâmina de 0,5 u com a borda arredondada, virola de aço e o anel de acento no pé do cabo. Referencial: +X para a ponta da
// lâmina, +Y para cima (o fio para baixo), +Z para a direita, origem na virola (u). Formato em docs/phases/phase-4.md,
// seção 4.1, "Receita"; o corpo é JSON puro.
export default {
  "id": "knife",
  "version": 1,
  "refs": { "pins": ["CTL6", "CTL7", "CTL16", "CTL12"] },
  "materials": { "aco": "aco", "madeira": "madeira", "acento": "acento" },
  "groups": {
    "corpo": { "pivot": [0, 0, 0] }
  },
  "anchors": {
    "maoDireita": { "pos": [-2.2, -1.3, 3], "rot": [3.1416, -1.5708, 0], "pose": "faca" }
  },
  "parts": [
    { "name": "cabo", "group": "corpo", "mat": "madeira", "shape": "lathe", "corner": 0.12, "points": [[-4.25, 0], [-4.25, 0.44], [-4.05, 0.62], [-3.4, 0.7], [-2, 0.74], [-1, 0.68], [-0.5, 0.6], [-0.3, 0.57], [-0.3, 0]] },
    { "name": "anel", "group": "corpo", "mat": "acento", "shape": "lathe", "corner": 0.06, "closed": true, "points": [[-3.98, 0.6], [-3.66, 0.6], [-3.66, 0.8], [-3.98, 0.8]] },
    { "name": "virola", "group": "corpo", "mat": "aco", "shape": "lathe", "corner": 0.1, "points": [[-0.38, 0], [-0.38, 0.64], [0.1, 0.62], [0.28, 0.46], [0.34, 0]] },
    { "name": "lamina", "group": "corpo", "mat": "aco", "shape": "profile", "thin": true, "h": 0.25, "round": 0.2, "corner": 0.16, "points": [[0.15, -0.2], [0.9, -0.4], [2, -0.5], [3, -0.36], [3.6, -0.06], [3.65, 0], [3.55, 0.12], [2.8, 0.43], [1.8, 0.52], [0.9, 0.38], [0.15, 0.2]] },
    { "name": "laminaFioD", "group": "corpo", "mat": "aco", "shape": "capsule", "op": "subtract", "r": 0.1, "a": [0.9, -0.05, 0.29], "b": [3.1, -0.12, 0.29] },
    { "name": "laminaFioE", "group": "corpo", "mat": "aco", "shape": "capsule", "op": "subtract", "r": 0.1, "a": [0.9, -0.05, -0.29], "b": [3.1, -0.12, -0.29] }
  ]
};
