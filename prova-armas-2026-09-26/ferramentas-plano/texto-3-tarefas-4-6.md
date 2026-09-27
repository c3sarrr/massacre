### Tarefa 4: Viewmodel parado — a arma na mão em primeira pessoa

**Files:**
- Create: `src/weapons/viewmodel/placement.js`, `src/weapons/viewmodel/viewmodelLights.js`, `src/weapons/viewmodel/viewmodel.js`, `tests/viewmodel.test.js`
- Modify: `src/render/postPipeline.js`, `src/data/configSchema.js`, `src/ui/settingControls.js`, `src/ui/settingsScreen.js`

O viewmodel é uma camada própria do pipeline de pós (`postPipeline.addLayer`, desenhada depois das passadas da cena e antes do bloom e do tone mapping), com a cena da arma e dos dois braços e uma câmera que copia a do jogador. Convenções do CS (a referência do "sentir" das armas): `viewmodel_fov` é horizontal num quadro 4:3 (o Source mede assim), então o vertical fica fixo e telas mais largas ganham lado (Hor+) — 60 por padrão (46,83° na vertical), de 54 a 68; `viewmodel_offset_x/y/z` (direita, frente, cima; padrão 1, 1, −1) somam por cima da posição da categoria (pistola, rifle, sniper, escopeta, SMG bullpup, faca: a origem da arma na câmera e os ângulos de arfagem, guinada e rolagem) e do ajuste fino da arma (`nudge`, a M4A4 desce por causa da alça); os três `viewmodel_presetpos` (1 Mesa, 2 Sofá, 3 Clássica) e a seção "Arma na mão" das configurações. As contas são puras (`placement.js`): o giro de base leva a boca (+X da arma) para a frente (−Z da câmera), cada âncora de mão vira a pose do pulso na câmera e cada antebraço aponta para um cotovelo fixo fora da tela. A luz da camada (`viewmodelLights.js`) copia as luzes do mapa a cada quadro (mesmas posições, cores e intensidades — o painel da vitrine e o console `luz` valem na hora) e acrescenta o que a cópia sozinha não faz: a sombra própria (cada spot/direcional que faz sombra no mapa projeta na camada com a câmera de sombra apertada numa esfera em volta da arma e dos pulsos, mapa de 512 a 1024) e a oclusão pelo set (raios no mundo de colisão do centro da arma, da boca e dos pulsos até cada luz; a fração livre multiplica a cópia, suavizada em 0,08 s subindo e 0,14 s descendo). As camadas ganham `beforeRender`/`afterRender` (a sombra própria força o mapa de sombra quando as sombras do mapa são estáticas). O `Viewmodel` pede a arma à biblioteca e os braços ao `handModels`, põe as mãos nas âncoras com a pose de cada uma, troca a pose só na troca de pose (12/s, "em dois"), mostra a braçadeira do time e some em terceira pessoa, no noclip, morto, com a luneta, com `r_viewmodel 0` e quando o item na mão não tem receita.

- [ ] **Passo 1: Escrever os testes** — FOV, giro de base, posição e offsets, ângulos, mãos nas âncoras, a arma na tela e os cotovelos fora dela, visibilidade, acento e os presets.

@@arquivo tests/viewmodel.test.js

- [ ] **Passo 2: Rodar e ver falhar**

@@run node --test tests/viewmodel.test.js ::: FAIL — o teste não carrega (`ERR_MODULE_NOT_FOUND`: `src/weapons/viewmodel/placement.js`).

- [ ] **Passo 3: As contas do viewmodel**

@@arquivo src/weapons/viewmodel/placement.js

- [ ] **Passo 4: Rodar os testes do viewmodel**

@@run node --test tests/viewmodel.test.js ::: PASS

- [ ] **Passo 5: `beforeRender`/`afterRender` nas camadas do pipeline**

@@pares src/render/postPipeline.js

- [ ] **Passo 6: A luz da camada**

@@arquivo src/weapons/viewmodel/viewmodelLights.js

- [ ] **Passo 7: O viewmodel**

@@arquivo src/weapons/viewmodel/viewmodel.js

- [ ] **Passo 8: As chaves de configuração e a seção "Arma na mão"**

@@pares src/data/configSchema.js

@@pares src/ui/settingControls.js

@@pares src/ui/settingsScreen.js

- [ ] **Passo 9: A suíte inteira**

@@run npm test ::: PASS — 326 testes passando.

@@commit src/weapons/viewmodel src/render/postPipeline.js src/data/configSchema.js src/ui/settingControls.js src/ui/settingsScreen.js tests/viewmodel.test.js ::: MASSACRE 4.1: viewmodel parado com as mãos nas âncoras, FOV e offsets do CS e a luz do set

---

### Tarefa 5: A bancada `arsenal` e a ligação no jogo

**Files:**
- Create: `src/maps/animatorDesk.js`, `src/clay/set/pegboardMaterial.js`, `src/data/arsenal.js`, `src/maps/arsenal/turntable.js`, `src/maps/arsenal/planSheets.js`, `src/maps/arsenal/bench.js`, `src/debug/panelControls.js`, `src/maps/arsenal/panel.js`, `src/maps/arsenal/index.js`, `src/debug/weaponCommands.js`
- Modify: `src/clay/set/index.js`, `src/debug/showcase.js`, `src/debug/showcasePanel.js`, `src/maps/index.js`, `src/render/dispose.js`, `src/player/freeCamera.js`, `src/debug/commands.js`, `src/modes/matchState.js`, `src/main.js`

A mesa do animador da vitrine (a mesma luz de vitrine) vira bancada de armeiro (QGW1, QGW6, QGW8, QGW14): as armas deitadas em fileiras por categoria no tapete de corte, com o lado direito para cima e a etiqueta de fita crepe escrita a caneta; na frente, a roda de modelar de metal (QTT11, com a giratória de produto QTT9) com a arma escolhida deitada num suporte de arame em garfo (QWS9, QWS12, QWS14); atrás, o quadro de hardboard perfurado com as ferramentas de modelar penduradas (QPB8, QPB13, QPB19; material procedural, sem textura) e as plantas a lápis presas com fita (QBP3, QBP13, QBP15: o contorno da planta, a cota e o nome). A mesa sai de `animatorDesk.js`, dividida com a vitrine, e os controles de painel de `panelControls.js`, divididos também. O painel de fita crepe (Tab) escolhe a arma, a facção do acento (nas dos dois lados), o nível, a skin, explode os grupos, mostra as âncoras, sobrepõe a planta à silhueta, para a roda, mede a silhueta contra a planta (IoU), relê a receita do disco (a arma da roda e a da fileira voltam com a receita nova — o caminho do Blender) e "Segurar" (a câmera estacionada e o viewmodel com a arma, para ver a pega). Na partida, o viewmodel entra no `matchState` (criado na entrada, ligado à camada, as mãos aquecidas e as armas do jogador pré-carregadas; atualizado no quadro; descartado na saída) e `main.js` cria os serviços `weaponModels` e `handModels`. O dispose das cenas deixa em paz o que é compartilhado (`userData.shared`: só o dono libera). Console: `viewmodel_fov`, `viewmodel_offset_x/y/z`, `viewmodel_presetpos`, `viewmodel_ajuste` (afina a categoria ou a âncora de uma mão ao vivo e devolve a linha pronta para os dados), `r_viewmodel`, `cl_bracadeira tr|ct|0`, `arsenal` (ou `bancada`), `arma <id>` e `armas`. Esta tarefa é o jogo em volta das contas testadas: a conferência é no navegador (Tarefa 7); no Node, o grafo de módulos do jogo precisa carregar inteiro.

- [ ] **Passo 1: Rodar e ver falhar** — o mapa ainda não existe.

@@run node --input-type=module -e "await import('./src/maps/arsenal/index.js')" ::: FAIL — `ERR_MODULE_NOT_FOUND`: `src/maps/arsenal/index.js`.

- [ ] **Passo 2: A mesa do animador, dividida com a vitrine**

@@arquivo src/maps/animatorDesk.js

@@pares src/debug/showcase.js

- [ ] **Passo 3: O quadro de hardboard perfurado no kit do set**

@@arquivo src/clay/set/pegboardMaterial.js

@@pares src/clay/set/index.js

- [ ] **Passo 4: Números da bancada**

@@arquivo src/data/arsenal.js

- [ ] **Passo 5: Roda de modelar e suporte de arame; plantas a lápis**

@@arquivo src/maps/arsenal/turntable.js

@@arquivo src/maps/arsenal/planSheets.js

- [ ] **Passo 6: A bancada**

@@arquivo src/maps/arsenal/bench.js

- [ ] **Passo 7: Controles de painel divididos, o painel da bancada e o mapa**

@@arquivo src/debug/panelControls.js

@@pares src/debug/showcasePanel.js

@@arquivo src/maps/arsenal/panel.js

@@arquivo src/maps/arsenal/index.js

@@pares src/maps/index.js

- [ ] **Passo 8: Recursos compartilhados fora do dispose das cenas; câmera estacionada**

@@pares src/render/dispose.js

@@pares src/player/freeCamera.js

- [ ] **Passo 9: Os comandos de console**

@@arquivo src/debug/weaponCommands.js

@@pares src/debug/commands.js

- [ ] **Passo 10: O viewmodel na partida e os serviços**

@@pares src/modes/matchState.js

@@pares src/main.js

- [ ] **Passo 11: O grafo de módulos carrega e a suíte passa**

@@run node --input-type=module -e "await import('./src/modes/matchState.js'); await import('./src/maps/arsenal/index.js'); await import('./src/debug/commands.js')" ::: PASS
@@run npm test ::: PASS — 326 testes passando.

@@commit src/maps src/clay/set src/data/arsenal.js src/debug src/render/dispose.js src/player/freeCamera.js src/modes/matchState.js src/main.js ::: MASSACRE 4.1: bancada de armas (mapa arsenal), viewmodel na partida e comandos de console

---

### Tarefa 6: O Blender como editor da receita

**Files:**
- Create: `tools/blender/previa.mjs`, `tools/blender.mjs`, `tools/blender/massacre/__init__.py`, `tools/blender/massacre/receita.py`, `tools/blender/massacre/eixos.py`, `tools/blender/massacre/importar.py`, `tools/blender/massacre/exportar.py`, `tools/blender/massacre/previa.py`, `tools/blender/massacre/conferir.py`, `tools/blender/massacre_armas.py`, `tests/blenderPrevia.test.js`
- Modify: `package.json`, `.gitignore`

Decisão do usuário: o Blender gera a receita. `npm run blender -- <ação>` (`tools/blender.mjs`) acha o executável (`BLENDER_PATH`, `tools/blender/local.json` fora do git ou as pastas de instalação conhecidas), prepara no Node o contexto que o Blender não sabe calcular — a paleta, o acento da facção, a planta, a mão de massinha em cada pose (o rig do jogo) e, para `abrir` e `conferir`, a prévia do jogo — e roda o `tools/blender/massacre_armas.py`: `abrir` (com janela: a arma montada, vista lateral ortográfica, o painel "MASSACRE" na barra lateral com Exportar, Prévia do jogo, Conferir e Recarregar), `conferir` (sem janela: seis PNGs em `tools/blender/conferencia/<id>/`), `ida-volta` (sem janela: importa, exporta e compara byte a byte com a receita — a prova do caminho), `validar <arquivo>` (a validação do jogo; o exportador chama antes de gravar por cima da receita) e `previa <arquivo> <saída>`. No Blender: `receita.py` lê a receita e grava no formato canônico (o mesmo do formatador do jogo); `eixos.py` converte os eixos (o ponto (x, y, z) do jogo fica em (x, −z, y) no Blender; o Euler XYZ do three é a ordem 'ZYX' do mathutils; o exportador tira o Euler pelo atan2, porque as matrizes do Blender são float32); `importar.py` monta a cena (uma coleção por grupo com o pivô; `profile` em curva 2D com extrusão e bisel, `lathe` no modificador Parafuso, `tube` em curva 3D com raio por ponto, o resto em malhas; a origem das peças por pontos no centro delas, então escalar e girar acontecem no lugar; cortes em arame vermelho; âncoras com a mão desenhada na pose; a planta numa coleção que não exporta; propriedades `massacre_*` guardando a peça original); `exportar.py` faz o caminho de volta (dobra a escala nos parâmetros, devolve aos pontos a translação e a escala das peças por pontos, usa o valor guardado quando o novo é o mesmo a 5·10⁻⁵ u — sem edição, a receita volta idêntica —, cópia com Shift+D vira peça nova depois da original e objeto sem receita recusa a exportação); `previa.py` lê a prévia do jogo; `conferir.py` renderiza no Workbench a lateral com a planta, cima, frente, 3/4, as mãos e a primeira pessoa. `tools/blender/previa.mjs` gera no Node a malha que o jogo faz da receita (o mesmo SDF, nível `perto`), os braços de massinha nas âncoras (o rig do jogo com o skinning na CPU, como no viewmodel) e a câmera do viewmodel, num binário que o Python lê.

- [ ] **Passo 1: Escrever o teste da prévia** — o formato que o Python lê, sem o Blender.

@@arquivo tests/blenderPrevia.test.js

- [ ] **Passo 2: Rodar e ver falhar**

@@run node --test tests/blenderPrevia.test.js ::: FAIL — o teste não carrega (`ERR_MODULE_NOT_FOUND`: `tools/blender/previa.mjs`).

- [ ] **Passo 3: A prévia do jogo para o Blender**

@@arquivo tools/blender/previa.mjs

@@run node --test tests/blenderPrevia.test.js ::: PASS

- [ ] **Passo 4: O lançador, o script do npm e o que fica fora do git**

@@arquivo tools/blender.mjs

@@pares package.json

@@pares .gitignore

- [ ] **Passo 5: O pacote do Blender**

@@arquivo tools/blender/massacre/__init__.py

@@arquivo tools/blender/massacre/receita.py

@@arquivo tools/blender/massacre/eixos.py

@@arquivo tools/blender/massacre/importar.py

@@arquivo tools/blender/massacre/exportar.py

@@arquivo tools/blender/massacre/previa.py

@@arquivo tools/blender/massacre/conferir.py

@@arquivo tools/blender/massacre_armas.py

- [ ] **Passo 6: O caminho no Blender** — com o Blender 5.2 instalado: o caminho do executável em `BLENDER_PATH` ou em `tools/blender/local.json` (`{ "blender": "<caminho do blender.exe>" }`, fora do git).

@@run npm run blender -- ida-volta todas ::: PASS (as sete linhas "ida e volta idêntica").
@@run npm run blender -- conferir ak47 ::: PASS (seis vistas em `tools/blender/conferencia/ak47/`).

- [ ] **Passo 7: A suíte inteira**

@@run npm test ::: PASS — 328 testes passando.

@@commit tools/blender.mjs tools/blender package.json .gitignore tests/blenderPrevia.test.js ::: MASSACRE 4.1: o Blender como editor das receitas (importar, exportar, conferir, prévia do jogo)

---
