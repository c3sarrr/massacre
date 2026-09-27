### Tarefa 1: Formas novas do SDF — perfil recortado, torno e tubo

**Files:**
- Create: `src/clay/sdf/polygon.js`, `tests/sdfProfile.test.js`
- Modify: `src/clay/sdf/params.js`, `src/clay/sdf/bounds.js`, `src/clay/sdf/shapes.js`

As peças das armas são massa cortada à mão (QPG2, QPL4): um contorno recortado e extrudado, um sólido torneado e uma cobrinha. `profile` é um polígono em XY (`points`) extrudado com meia-espessura `h` em Z, com `corner` (filete 2D nos cantos convexos e côncavos — a massa preenche os cantos de dentro) e `round` (as arestas da extrusão arredondadas); o filete é feito uma vez na compilação (arcos tangentes aos dois lados, raio limitado pelos lados, 6 segmentos por arco) e o `corner` fica ≥ `round`, o que torna exata a distância do contorno encolhido de `round` usada no "opExtrusion" arredondado de iq. A distância 2D é exata (distância aos segmentos com o sinal pelo número de cruzamentos), então a forma é 1-Lipschitz e entra no intervalo garantido d ± R do marching cubes. `lathe` é o mesmo polígono no semiplano (x, ρ ≥ 0) girado em volta do X (distância exata = a 2D em (x, √(y² + z²))), com `closed` para anéis. `tube` é uma polilinha 3D com raio por ponto (cones arredondados encadeados; a distância é o mínimo entre os trechos). `params.js` lê e limita (polígono de 3 a 256 pontos, sem lado de comprimento zero, raios positivos) e explica o problema quando a forma é inválida; `bounds.js` dá a função suporte de cada uma (o polígono e a revolução do polígono; no tubo, a casca das esferas das pontas).

- [ ] **Passo 1: Escrever os testes** — distância contra a força bruta, o filete, o perfil, o torno contra o cilindro, o tubo contra a cápsula e o cone arredondado, caixa e intervalo, malha fechada e as formas inválidas.

@@arquivo tests/sdfProfile.test.js

- [ ] **Passo 2: Rodar e ver falhar**

@@run node --test tests/sdfProfile.test.js ::: FAIL — o teste não carrega (`ERR_MODULE_NOT_FOUND`: `src/clay/sdf/polygon.js`).

- [ ] **Passo 3: O polígono 2D** — filete dos cantos, distância com sinal e caixa.

@@arquivo src/clay/sdf/polygon.js

- [ ] **Passo 4: Leitores e limites das formas novas**

@@pares src/clay/sdf/params.js

- [ ] **Passo 5: A função suporte de cada uma**

@@pares src/clay/sdf/bounds.js

- [ ] **Passo 6: As distâncias** — `profile`, `lathe` e `tube` no compilador de formas.

@@pares src/clay/sdf/shapes.js

- [ ] **Passo 7: Rodar e ver passar**

@@run node --test tests/sdfProfile.test.js ::: PASS
@@run npm test ::: PASS — 302 testes passando.

@@commit src/clay/sdf tests/sdfProfile.test.js ::: MASSACRE 4.1: formas novas do SDF (perfil recortado, torno e tubo)

---

### Tarefa 2: Mãos de 4 dedos com rig

**Files:**
- Create: `src/data/hands.js`, `src/characters/hands/handShape.js`, `src/characters/hands/handSkin.js`, `src/characters/hands/armband.js`, `src/characters/hands/handRig.js`, `src/characters/hands/handLibrary.js`, `tests/clayHands.test.js`

Decisão do usuário: três dedos grossos e o polegar, como os humanos da Aardman (CMH3, CMH14, CMH16, CMH19; mãos simples CMH15, CMH18). A mão direita é uma árvore SDF (palma de caixa arredondada de 3,0 × 1,4 × 3,2 u, dedos de raio ~0,6 u com três falanges, polegar de 0,68 u saindo perto do pulso, antebraço em cone arredondado de 1,25 u no pulso a 1,65 u no cotovelo e 11 u de comprimento), com o vinco da costura onde cada dedo sai da palma. O rig tem 14 ossos (antebraço, mão, 3 × 3 falanges, polegar em 3) com pesos pela distância de cada vértice ao segmento de cada osso (queda suave, os 4 maiores, normalizados) numa `SkinnedMesh`; o boil do `ClayMaterial` age na pose de repouso (antes do skinning) e as digitais ficam no espaço do objeto em repouso, então a massa dobra com o dedo e as marcas vão junto. As poses (`empunhadura`, `apoio`, `guardaMao`, `bomba`, `faca`, `aberta`) são ângulos em dados, dentro dos limites das juntas. A esquerda é a direita espelhada em Z (malha, ossos e giros). `ClayArm.place` põe o pulso na âncora e aponta o antebraço para o cotovelo. A braçadeira do time é uma faixa torneada a 55% do antebraço; a cor é a primeira do time (primária, secundária, acento) com ΔE ≥ 30 para a massa do braço — no braço terracota do boneco de referência, a do TR vira o laranja. O serviço `handModels` (`HandLibrary`) gera a malha da mão e a da braçadeira uma vez (SDF, cache) e os braços dividem as geometrias de cada lado.

- [ ] **Passo 1: Escrever os testes** — ossos e cadeias, malha fechada do tamanho do desenho, pesos, limites das poses, espelho, braço na âncora e a cor da braçadeira.

@@arquivo tests/clayHands.test.js

- [ ] **Passo 2: Rodar e ver falhar**

@@run node --test tests/clayHands.test.js ::: FAIL — o teste não carrega (`ERR_MODULE_NOT_FOUND`: `src/data/hands.js`).

- [ ] **Passo 3: Números da mão, da braçadeira e das poses**

@@arquivo src/data/hands.js

- [ ] **Passo 4: Ossos e a árvore SDF da mão**

@@arquivo src/characters/hands/handShape.js

- [ ] **Passo 5: Pesos, giros das poses e espelho**

@@arquivo src/characters/hands/handSkin.js

- [ ] **Passo 6: Cor da braçadeira**

@@arquivo src/characters/hands/armband.js

- [ ] **Passo 7: O braço (`ClayArm`)**

@@arquivo src/characters/hands/handRig.js

- [ ] **Passo 8: O serviço `handModels`**

@@arquivo src/characters/hands/handLibrary.js

- [ ] **Passo 9: Rodar e ver passar**

@@run node --test tests/clayHands.test.js ::: PASS
@@run npm test ::: PASS — 309 testes passando.

@@commit src/data/hands.js src/characters/hands tests/clayHands.test.js ::: MASSACRE 4.1: mãos de massinha de 4 dedos com rig e braçadeira

---

### Tarefa 3: Massas, receitas, gerador, plantas e a biblioteca das armas

**Files:**
- Create: `src/data/weaponPalette.js`, `src/data/viewmodel.js`, `src/weapons/model/recipe.js`, `src/weapons/model/weaponModel.js`, `src/weapons/model/silhouette.js`, `src/weapons/model/weaponLibrary.js`, `src/data/armas/glock.js`, `ak47.js`, `m4a4.js`, `awp.js`, `nova.js`, `p90.js`, `knife.js`, `index.js`, `tools/blender/refs/glock.json`, `ak47.json`, `m4a4.json`, `awp.json`, `nova.json`, `p90.json`, `tools/silhueta.html`, `tests/weaponRecipes.test.js`
- Modify: `src/data/claySkins.js`, `src/clay/glsl/skins.js`, `src/core/events.js`

Decisões do usuário: estilo "fiel e gordinha" (a silhueta da arma real com massa mínima de 1,2 u; a lâmina da espátula, 0,5 u — o revólver do pinguim de *The Wrong Trousers*, QCG1) e a cor real traduzida em massinha com o acento da facção nos detalhes pequenos (massa de mira, base do carregador, gatilho, seletor). A paleta: `grafite` (o "preto" das armas vira grafite fosco; massinha nunca é preta), `grafiteClaro`, `madeira` com a skin de base nova `veio` (riscada a palito ao longo da peça, fora das skins de jogador), `madeiraEscura`, `verdeOliva`, `areia`, `prata` e `aco` (a lâmina da espátula, massa prata úmida); o acento TR é terracota/laranja, o CT azul/verde-água e o das armas dos dois lados amarelo-massinha/branco-massa. A receita (um módulo por arma, `export default` + JSON puro) tem `id`, `version`, `refs`, `materials` (slot → massa), `soft` opcional, `groups` (as partes que se mexem, com pivô e eixo), `anchors` (mãos com a pose, boca, ejeção, mira) e `parts` (forma, parâmetros, `pos`/`rot` em Euler XYZ, `op: 'subtract'` nos cortes). `recipe.js` valida e monta uma árvore SDF por grupo — as peças numa união suave com vinco (k 0,25 u, faixa de costura de 0,25 u entre massas), os cortes numa subtração suave (k 0,12 u) e os calombos —; `weaponModel.js` gera uma malha por grupo no pivô, em dois níveis (`perto` 0,14 u, viewmodel e bancada; `mundo` 0,35 u, Fases 5, 8 e 9), e os materiais com o acento e o boil na medida da arma; `silhouette.js` tira a silhueta lateral do SDF (máximo em Z) para o IoU contra a planta e para o comprimento. As plantas vêm de fotos laterais do Wikimedia Commons (Glock 17, AK-47 tipo II, carabina M4A1 com a alça de transporte, AI Arctic Warfare PSG 90, Benelli M3 Super 90, FN P90): a página `tools/silhueta.html` (servida pelo servidor de desenvolvimento) carrega a imagem pelo CORS num canvas, separa a arma do fundo, segue o contorno, simplifica e escala pelo comprimento real — nenhuma imagem vai para o disco, só o contorno e a ficha da fonte. As âncoras das mãos saem da geometria da empunhadura (a mão direita com os dedos perpendiculares ao eixo inclinado da empunhadura e os nós logo à frente da borda; a esquerda por baixo do guarda-mão) e os guarda-matos ficam alargados em relação à planta, para o dedo de massa caber. `src/data/viewmodel.js` entra aqui porque o teste das receitas confere a categoria de cada uma no viewmodel (a Tarefa 4 usa o resto). O serviço `weaponModels` guarda as malhas por (arma, nível) e os materiais por (arma, facção) — o boil de cada material segue o tamanho da arma —, marca tudo como compartilhado (`userData.shared`), pré-carrega e relê a receita do disco em duas fases (`EV.WEAPON_MODEL` com `relendo` antes do descarte e `pronta` depois).

- [ ] **Passo 1: Escrever os testes** — registro e validação, a tabela do primeiro lote, espessura mínima, acento pela facção, IoU ≥ 0,8, comprimento, árvores determinísticas e categoria no viewmodel.

@@arquivo tests/weaponRecipes.test.js

- [ ] **Passo 2: Rodar e ver falhar**

@@run node --test tests/weaponRecipes.test.js ::: FAIL — o teste não carrega (`ERR_MODULE_NOT_FOUND`: `src/data/armas/index.js`).

- [ ] **Passo 3: As massas das armas e a skin de base `veio`**

@@arquivo src/data/weaponPalette.js

@@pares src/data/claySkins.js

@@pares src/clay/glsl/skins.js

- [ ] **Passo 4: Números do viewmodel** (a categoria de cada arma; FOV, offsets, presets, cotovelos e luz da camada para a Tarefa 4)

@@arquivo src/data/viewmodel.js

- [ ] **Passo 5: A receita — validação e árvores por grupo**

@@arquivo src/weapons/model/recipe.js

- [ ] **Passo 6: Malhas, materiais e a instância**

@@arquivo src/weapons/model/weaponModel.js

- [ ] **Passo 7: Silhueta lateral e comprimento**

@@arquivo src/weapons/model/silhouette.js

- [ ] **Passo 8: As plantas de referência e a página que tira o contorno**

@@arquivo tools/blender/refs/glock.json

@@arquivo tools/blender/refs/ak47.json

@@arquivo tools/blender/refs/m4a4.json

@@arquivo tools/blender/refs/awp.json

@@arquivo tools/blender/refs/nova.json

@@arquivo tools/blender/refs/p90.json

@@arquivo tools/silhueta.html

- [ ] **Passo 9: As sete receitas e o registro**

@@arquivo src/data/armas/glock.js

@@arquivo src/data/armas/ak47.js

@@arquivo src/data/armas/m4a4.js

@@arquivo src/data/armas/awp.js

@@arquivo src/data/armas/nova.js

@@arquivo src/data/armas/p90.js

@@arquivo src/data/armas/knife.js

@@arquivo src/data/armas/index.js

- [ ] **Passo 10: O evento da recarga e o serviço `weaponModels`**

@@pares src/core/events.js

@@arquivo src/weapons/model/weaponLibrary.js

- [ ] **Passo 11: Rodar e ver passar**

@@run node --test tests/weaponRecipes.test.js ::: PASS
@@run npm test ::: PASS — 317 testes passando.

@@commit src/data/weaponPalette.js src/data/claySkins.js src/clay/glsl/skins.js src/data/viewmodel.js src/weapons/model src/data/armas tools/blender/refs tools/silhueta.html src/core/events.js tests/weaponRecipes.test.js ::: MASSACRE 4.1: receitas das sete primeiras armas, gerador, plantas e a biblioteca de malhas

---
