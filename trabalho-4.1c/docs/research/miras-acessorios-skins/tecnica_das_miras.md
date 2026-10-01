# Técnica das miras: renderização e câmera de ópticas e acessórios de armas em FPS (three.js/WebGL, 60 fps em GPU integrada e 30 fps em celular intermediário)

> Contexto do projeto, conferido nos arquivos locais em 2026-09-28: three.js **0.186.1 (r186)**. O `src/render/camera.js` já aplica FOV "Hor+" a partir de um FOV horizontal em 16:9 (padrão de 100°, o que dá um FOV vertical de 67,67°) e faz o zoom **multiplicando a tangente** (`zoom = 1/M`; o comentário do código diz "0,4 = luneta 2,5x"). O `src/render/postPipeline.js` já desenha "camadas" (o viewmodel) num alvo próprio com `clearDepth()` e as compõe sobre a cena. Só o alvo da cena tem MSAA, e o pipeline também tem bloom, SMAA e DoF (`src/render/passes/`). A unidade do mundo é o centímetro (`NEAR = 2`, "2 cm na escala do boneco").

---

## 1. Retículos reflex (red dot) e holográficos: ponto no infinito, correção de paralaxe, brilho e antisserrilhado

### Takeaway
O retículo de um red dot ou holográfico **não deve ser uma textura presa na UV do vidro**. O jeito certo é desenhá-lo no fragmento do vidro em função da **direção do raio olho→fragmento em relação ao eixo da mira** (projeção no plano da lente). Assim ele fica "no infinito" e continua no ponto de mira seja qual for a posição da cabeça, sem render-to-texture. Isso custa uma amostra de textura (ou um SDF) por pixel do vidro. O ponto brilha porque recebe um valor emissivo HDR acima do limiar do bloom. No navegador, a dificuldade prática é outra: um ponto realista de 2 MOA ocupa **menos de 1 pixel**, então é preciso impor um tamanho mínimo em pixels e fazer AA com `fwidth`. Como o MASSACRE desenha o viewmodel com FOV próprio, o ponto também precisa ser calculado com a **projeção da câmera do mundo** (ver as Inferences).

### Cited Findings
- **Ótica real.** A imagem colimada do red dot só é livre de paralaxe no infinito. Para alvos a distância finita, sobra um "círculo de erro" do diâmetro da óptica colimadora. Como a imagem do retículo está no infinito, ela continua alinhada à arma seja qual for a posição do olho. — [Wikipedia: Red dot sight](https://en.wikipedia.org/wiki/Red_dot_sight); [Wikipedia: Reflector sight](https://en.wikipedia.org/wiki/Reflector_sight)
- **Técnica de Vazgriz (Unity).** A técnica compara a direção câmera→fragmento com a normal da lente: `offset = cameraDir + normal`, com a normal virada para a câmera. Esse offset vai para o espaço tangente com a matriz TBN (`float3x3(tangent, cross(normal, tangent), normal)`), o componente z é descartado e a UV sai de `uv = offset.xy / _TexScale + 0.5`. Com `_TexScale = 1`, a imagem cobre "cerca de 60° do FOV da câmera". O autor aponta duas limitações: o retículo não muda de escala quando a câmera se afasta da mira, e a precisão piora quando a câmera sai do alinhamento com a normal da lente. Reflex e holográfico "só diferem no retículo usado". — [Vazgriz: Reflex Sight Shader in Unity3D](https://vazgriz.com/158/reflex-sight-shader-in-unity3d/)
- **Shader "Reflector Sight (Red Dot)" do Godot.** No vértice, calcula `view_dir = CAMERA_POSITION_WORLD - world_position` e leva essa direção para o espaço do modelo (`lens_dir = (inverse(MODEL_MATRIX) * vec4(view_dir, 0.0)).xz`). No fragmento, faz `offset_uv -= lens_dir * depth; offset_uv /= (retical_size * depth); offset_uv += 0.5`. O brilho vem de `EMISSION = retical_color.rgb * retical_a * emission_strength` (faixa de 0 a 16). Há um "flicker" opcional por onda quadrada (`max(0.1, sign(sin(TIME*rate*2π)))`), e o vidro tem tinta própria (`lens_color` com alfa 0,2). O shader não faz antisserrilhado. — [Godot Shaders: Reflector Sight](https://godotshaders.com/shader/reflector-sight-red-dot/)
- **Shader "Holographic Sight Reticle" do Godot.** A conta é feita em espaço de tela: `slope = -1/PROJECTION_MATRIX[1][1]` (que é −tan(FOV/2)), a normal em espaço de visão é normalizada por z (`NORMAL / NORMAL.z`, ou seja, as tangentes dos ângulos) e somada à posição do pixel em clip space. O resultado é corrigido pelo aspecto e dividido pelo tamanho do retículo. O material é `unshaded` e a UV é limitada com `clamp`. A normal da malha precisa estar paralela ao cano. — [Godot Shaders: Holographic Sight Reticle](https://godotshaders.com/shader/holographic-sight-reticle/)
- Há um red dot "Parallax Reticle" feito só com shader no Shader Graph do URP, **sem render textures**, que mantém o ponto travado do ponto de vista do jogador enquanto arma e câmera se movem. — [ArtStation: Youssef Alioua, FPS Red Dot Shader](https://www.artstation.com/artwork/V2Qqab) (fonte: trecho do resultado de busca)
- Existe um addon distribuído para S.T.A.L.K.E.R. Anomaly só com miras reflex com paralaxe ("Parallax Reflex Sights"), o que mostra que a técnica já foi usada num mod lançado. — [ModDB: Parallax Reflex Sights](https://www.moddb.com/mods/stalker-anomaly/addons/parallax-reflex-sights)

### Inferences
- **Fórmula exata do "retículo no infinito" (projeção gnomônica).** Considere o referencial da lente (T, B, N), com N sendo o **eixo de visada** (do olho para o alvo, já com a zeragem). Seja E a posição do olho e P a do fragmento no vidro. O retículo é função apenas da direção `d = P − E`:
  `u = dot(d,T)/dot(d,N)`, `v = dot(d,B)/dot(d,N)` (as tangentes dos ângulos em relação ao eixo), e `uvRet = 0.5 + (u,v) / (2·tanθs)`, onde θs é a meia-abertura angular coberta pela textura do retículo.
  Não precisa normalizar `d`: a divisão por `dot(d,N)` cancela o comprimento. Como `P − E` é linear no triângulo, basta calculá-lo no vértice e interpolar. O resultado é exato para qualquer posição do olho. A versão de Vazgriz (`cameraDir + normal`) aproxima isso com senos, o que funciona bem para ângulos pequenos.
- **Esboço para three.js** (ShaderMaterial no vidro, dentro da camada do viewmodel, com blending aditivo, `depthWrite:false` e `toneMapped` ligado para o bloom pegar):
  ```glsl
  // vertex: uEyeLocal = lente.worldToLocal(posição da câmera do viewmodel), calculado na CPU a cada quadro
  varying vec3 vRay;  void main(){ vRay = position - uEyeLocal; gl_Position = projectionMatrix*modelViewMatrix*vec4(position,1.); }
  // fragment: eixo de visada = -Z local da lente
  vec2 t = vRay.xy / -vRay.z;                 // tangentes (ângulos) em relação ao eixo
  float r = length(t);                         // distância angular ao centro do ponto
  float w = fwidth(r);                         // 1 pixel expresso em "unidades de tangente"
  float rad = max(uDotTan, 0.75*w);            // raio mínimo de ~0,75 px (evita cintilação)
  float a = 1. - smoothstep(rad - w, rad + w, r);
  gl_FragColor = vec4(uColor * uIntensity * a, a); // uIntensity > limiar do bloom (HDR)
  ```
  Um holográfico usa o mesmo shader, trocando o SDF do ponto por anel + ponto (ou por uma textura com mipmaps). O vidro é a própria máscara: quando o olho sai muito do eixo, o ponto "escorrega" para a borda e some, exatamente como na mira real.
- **Tamanho em pixels.** Nas contas feitas para a câmera do MASSACRE (vFOV de 67,67°), o centro da tela tem 0,234 px/MOA em 1080p, 0,156 px/MOA em 720p e 0,312 px/MOA em 1440p. Um ponto de 2 MOA dá **0,47 px em 1080p e 0,31 px em 720p**, então seria invisível ou cintilaria sem um raio mínimo. Um anel de 68 MOA (valor usado aqui só como exemplo) dá 15,9 px em 1080p e 10,6 px em 720p. Conclusão: o ponto precisa de um diâmetro mínimo de ~1,5 a 2 px e de um brilho HDR que o bloom espalhe. Se o objetivo for conservar energia, dá para escalar a intensidade por `(uDotTan/rad)²`. Para jogabilidade, porém, costuma ser melhor não escurecer o ponto.
- **Armadilha do MASSACRE: FOV do viewmodel ≠ FOV do mundo.** O vidro é projetado pela câmera do viewmodel (FOV_vm), e o alvo pela câmera do mundo (FOV_w). Uma direção θ fora do centro cai em `x_vm = tanθ/tan(FOV_vm/2)` numa tela e em `x_w = tanθ/tan(FOV_w/2)` na outra. As duas só coincidem no centro da tela. Durante o balanço da arma (sway), ou com qualquer zoom de ADS no mundo, o ponto desenhado pela fórmula acima **deixa de marcar o alvo**. Há duas saídas:
  (a) Na pose de ADS, manter o eixo de visada no centro da tela e limitar o sway angular. O erro fica em `tanθ·|1/tan(FOV_vm/2) − 1/tan(FOV_w/2)|` em NDC.
  (b) **Recomendado.** Fazer a conta em espaço de tela, como o shader holográfico do Godot, mas com a **projeção da câmera do mundo**: `ndcPonto = (P_w · V · vec4(N_mundo, 0)).xy / w`. O retículo é desenhado a partir de `gl_FragCoord` em relação a `ndcPonto`, com tamanho `tanθ_ret / tan(FOV_w/2)` em NDC. O vidro vira só a máscara. Essa saída já resolve o zoom de ADS, o FOV separado do viewmodel e o magnificador.
- **Magnificador atrás do holo (3x flip).** Um retículo no infinito é ampliado pelo magnificador. Com a abordagem (b), basta multiplicar o tamanho angular do retículo por M enquanto o magnificador estiver abaixado.
- **Brilho.** Um uniform `uIntensity` com uns 10 níveis, como nas miras reais, e um modo "NV" com intensidade baixa para não estourar o bloom com visão noturna. Um ajuste automático opcional que siga a exposição média da cena (o pipeline já tem HDR e bloom) pode ser bom, mas é uma hipótese a testar.
- **Custo.** Desprezível: poucos fragmentos (só o vidro), sem passe extra. Funciona igual em celular (mas use `highp` no cálculo de `t`, porque os ângulos são muito pequenos).

### Gaps
- Não achei nenhuma fonte primária (GDC ou blog de estúdio AAA) que descreva o shader de red dot de um jogo comercial. As fontes são shaders da comunidade (Godot, Unity, ArtStation) e mods.
- Não pesquisei as diferenças ópticas entre holográfico e reflex que afetariam o jogo (por exemplo, o retículo com a janela parcialmente obstruída), nem o tamanho oficial do anel e do ponto de cada modelo.
- Não achei como jogos comerciais fazem o ajuste automático de brilho do ponto.

---

## 2. Ópticas com ampliação: zoom de FOV em tela cheia com máscara × picture-in-picture (render-to-texture) × híbridos

### Takeaway
Existem quatro famílias usadas em jogos lançados:
- **(A) Zoom de FOV em tela cheia com overlay 2D** (CS, os "2D scopes" do Arma e o modo "Normal" do Sandstorm). Custo extra praticamente zero.
- **(B) Híbrido.** Zoom em tela cheia, luneta 3D no FOV do viewmodel e borrão/escurecimento fora da lente (CoD a partir de Advanced Warfare). Uma única renderização da cena, mais um blur.
- **(C) PiP de verdade.** Uma segunda renderização da cena, no FOV da luneta, num render target mostrado na lente (Tarkov, modo PiP do Sandstorm, PiP do Arma Reforger, "dual render" do CoD Ghosts). É a mais cara: jogadores relatam quedas de 10 a 40 fps mesmo em GPUs dedicadas.
- **(D) Lupa em espaço de tela.** Amplia o quadro já renderizado (o addon "Shader 3D Scopes" do S.T.A.L.K.E.R. Anomaly). É quase grátis, mas perde resolução na razão M.

Todos os jogos que oferecem PiP também oferecem a opção 2D/Normal por causa do custo. Para o MASSACRE, o caminho sugerido é **(B) como padrão em todas as plataformas e (C) como "alta qualidade" no desktop**. No modo (C), o RT deve ter o tamanho da lente em pixels e só ser renderizado durante o ADS.

### Cited Findings
- **Insurgency: Sandstorm.** O modo PiP mostra a imagem ampliada dentro da luneta e mantém a visão periférica. O modo "Normal" amplia a tela inteira e elimina a periferia. Relatos de custo do PiP: cerca de −20 fps numa GTX 1060 Max-Q; de 120 e poucos para uns 85 fps numa GTX 1080 Ti em 1440p; de 60 para 50 fps numa Vega 56 em 1440p; impacto mínimo com trava em 60 fps numa GTX 1070 e numa RTX 2070. O tópico não tem declaração de desenvolvedor. — [Steam: Sandstorm, Picture in Picture vs Normal](https://steamcommunity.com/app/581320/discussions/0/1741106440018198500/)
- **Escape from Tarkov.** Jogadores relatam quedas de 30 a 40 fps ao mirar em lunetas de longa distância (de 70–90 para 40–50 fps). — [Fórum EFT: Scope FPS drop](https://forum.escapefromtarkov.com/topic/118297-scope-fps-drop/) (fonte: trecho do resultado de busca)
- **Call of Duty.** O Ghosts tinha lunetas "dual render", que ampliavam só dentro da luneta e deixavam ver fora dela. O Advanced Warfare trocou isso por lunetas com borrão em volta. Um jogador observou que "a parte borrada também estava ampliada; é só profundidade de campo exagerada simulando o efeito", e outros citaram quedas de desempenho do dual render. Tudo isso vem de jogadores, não de desenvolvedores. — [Steam: CoD AW, Dual render scopes are gone](https://steamcommunity.com/app/209650/discussions/0/34095051769519953/)
- **Arma Reforger.** O componente `SCR_2DPIPSightsComponent` liga o modo 2D ou o PiP na luneta conforme a preferência do jogador nas configurações de Gameplay. — [Bohemia Wiki: Arma Reforger, Weapon Optic Creation](https://community.bistudio.com/wiki/Arma_Reforger:Weapon_Optic_Creation) (fonte: trecho do resultado de busca; a página devolveu 403)
- **Arma Reforger (jogadores).** O PiP pesa bem mais na GPU e a recomendação é usar 2D em máquinas fracas. — [Steam: Reforger, PIP scope performance](https://steamcommunity.com/app/1874880/discussions/0/594018749968850009/). Com PiP, alvos distantes aparecem com qualidade inconsistente, e partes do corpo deixam de ser renderizadas a longa distância. — [Steam: Reforger, qualidade de alvos distantes com PiP](https://steamcommunity.com/app/1874880/discussions/6/4351113819078335524/) (ambos: trechos do resultado de busca)
- **Squad.** Jogadores argumentam que a escala do jogo (muitos jogadores, veículos, vegetação e efeitos) faria o PiP pesar demais. — [Steam: Squad, Picture in picture scope](https://steamcommunity.com/app/393380/discussions/0/1646544348827204120/) (fonte: trecho do resultado de busca; é opinião da comunidade)
- **S.T.A.L.K.E.R. Anomaly, "Shader 3D Scopes".** Usa uma técnica de lupa e mascara a arma dentro da lente, "tentando chegar o mais perto possível do PiP sem impacto de desempenho". Algumas miras têm primeiro plano focal (o retículo cresce junto com o zoom). — [ModDB: Shader 3D Scopes](https://www.moddb.com/mods/stalker-anomaly/addons/shader-3d-scopes) (fonte: trecho do resultado de busca; a página devolveu 403)
- **Shader de lente de luneta para Unity (PiP com render texture).** Distorção de borda: `distortedUV = uv + normalize(0.5−uv) · pow(|0.5−uv|, _EdgeDistortion)`. Vinheta: `vignetteWeight = clamp((1−_Vignette)/dist(uv, 0.5), 0, 1)`. O retículo entra por cima quando o alfa passa de 0,85, e o vidro usa PBR com metalicidade e suavidade. — [GitHub Gist: kameronbrooks, A Unity Shader for a sniper scope lens](https://gist.github.com/kameronbrooks/0e17fa98c9429100981eb723615e02b0)
- **Shader de luneta de Cedric Kuppens (Unity e Unreal, para VR).** Usa câmera separada com render texture. Os parâmetros de profundidade, escala e gradiente da máscara criam o círculo que limita a visão, e uma vinheta escurece as bordas. A diferença entre a direção da câmera e a normal da lente vira um offset 2D na textura. — [ArtStation: Scope shader, Cedric Kuppens](https://www.artstation.com/artwork/LeKnzP) (fonte: trecho do resultado de busca)
- **Primeiro e segundo plano focal.** Em FFP, o retículo fica antes do mecanismo de zoom e cresce ou encolhe com a ampliação, então as marcações valem em qualquer zoom. Em SFP, o retículo fica depois do zoom e mantém o mesmo tamanho aparente. — [Swampfox Optics](https://www.swampfoxoptics.com/first-focal-plane-vs-second-focal-plane-reticles); [ATN](https://www.atncorp.com/blog/rifle-scope-reticles-first-focal-plane-vs-second-focal-plane)
- **Zoom variável no Tarkov.** O jogo ganhou zoom suave em 14 ópticas variáveis (por exemplo, de 1x até 4, 6 ou 8x) no patch 0.15 (novembro de 2024). — [Vocal Media: Tarkov Fixed All These Scopes](https://vocal.media/gamers/tarkov-fixed-all-these-scopes) (agregador; não conferi nas notas oficiais)

### Inferences
- **FOV da câmera PiP a partir do tamanho da lente na tela.** Seja `r_ndc` o raio vertical da lente em NDC (raio em pixels dividido por H/2), medido projetando a malha da lente com a câmera do viewmodel. Para que a imagem da lente fique **M vezes maior do que a mesma região vista a olho nu no mundo**:
  `tan(FOV_pip/2) = r_ndc · tan(FOV_w/2) / M`, com aspecto 1 (RT quadrado).
  Com a lente ocupando a altura inteira da tela (`r_ndc = 1`), a fórmula vira o zoom de tela cheia, o que confirma a coerência. Exemplo: se a lente equivale a 20° do mundo, uma luneta 8x tem FOV_pip de 2,53° e uma 4x tem 5,05°.
- **Amostrar o RT pela direção de visada**, não pela UV plana: `uvImg = 0.5 + (tanθ_olho · k / M) / (2·tan(FOV_pip/2))`, onde `tanθ_olho` são as tangentes da direção do olho em relação ao eixo da luneta (a mesma conta do red dot) e `k = tan(FOV_w/2)/tan(FOV_vm/2)` corrige a diferença de FOV do viewmodel. Assim a imagem fica "no infinito", como numa luneta real: ela não desliza junto com o aro quando o olho se move. Somada à sombra do ocular, isso reproduz o efeito do Tarkov e do Sandstorm.
- **Sombra do ocular (eye relief / eye box) que acompanha o sway.** Seja C o centro do ocular, N o eixo da luneta e `e = E − C`.
  - Distância axial: `z = −dot(e,N)`. Deslocamento lateral: `l = (dot(e,T), dot(e,B))`.
  - Raio visível: `r = r0 · (1 − (1 − r_min/r0) · saturate(|z − z0| / Δz))`, onde z0 é o eye relief ideal (em cm, na escala do jogo).
  - Centro da máscara: `s = −l / R_eyebox + g · tanθ_eixo`. O segundo termo é o desalinhamento angular entre a câmera e o eixo; é ele que cria as "luas crescentes" pretas quando a arma balança.
  - Máscara: `mask = 1 − smoothstep(r − f, r, |uvLente − 0.5 − s|)`, e a cor final é multiplicada por `mask`.
  Isso funciona tanto no modo (C) quanto no (B) e é o ponto de partida natural para a "sombra do ocular" já prevista para a AWP.
- **Distorção e aberração cromática na lente.** Distorção radial: `uv' = c + (uv − c)(1 + k1·r² + k2·r⁴)`, com k1 < 0 para barril. Aberração cromática: amostrar R, G e B com k ligeiramente diferente (por exemplo, `k·(1 ± ca)`) ou deslocar só nas bordas (`ca·r²`). Tudo isso roda apenas nos pixels da lente, com 3 amostras, e custa pouco até em celular.
- **FFP × SFP na implementação.**
  - SFP: o retículo fica fixo na UV do ocular (`uvRet = uvLente`), então seu tamanho angular no mundo é proporcional a 1/M.
  - FFP: o retículo fica fixo em ângulo de mundo, então cresce com o zoom: `uvRet = 0.5 + (uvLente − 0.5) · (M_ref / M)`.
  - O zoom variável só anima M. Atualizar `pipCamera.fov` e chamar `updateProjectionMatrix()` a cada quadro é barato.
- **Como baratear o PiP** (os jogos não publicam isso; são técnicas padrão que precisam ser medidas):
  1. Renderizar o RT **só com ADS acima de ~30–50%** de progresso. Antes disso, a lente está pequena ou oblíqua.
  2. Tamanho do RT = diâmetro da lente em px × qualidade (0,5 a 1), limitado entre 256 e 1024 e **sem MSAA** no celular (ver seção 7).
  3. **Reaproveitar as shadow maps** do passe principal: `renderer.shadowMap.autoUpdate = false` durante o `render()` do PiP. O `WebGLShadowMap` do r186 sai cedo se `autoUpdate` e `needsUpdate` forem falsos.
  4. Usar **as mesmas luzes e camadas de luz** do passe principal, para não gerar outra variante de programa (ver seção 6).
  5. Excluir por `layers` o corpo do próprio jogador, o viewmodel, as partículas pequenas e os decals.
  6. Calcular a **LOD com o FOV da luneta**. O problema do Reforger (partes do corpo sumindo a distância) sugere LOD ou culling calculados com a câmera principal.
  7. O **frustum estreito** (por exemplo, 17° de hFOV em 8x) já descarta por frustum culling a maior parte dos objetos. Mas isso só funciona se o cenário estiver dividido em pedaços: um mapa numa malha única custa o mesmo número de vértices.
  8. No celular, uma opção a testar é renderizar o PiP a 30 Hz e compensar o giro da câmera deslocando a UV (`ΔuvImg = Δângulo / FOV_pip`), no estilo do timewarp de VR.
- **Plano para a "luneta real" da AWP no MASSACRE.**
  - Padrão, modo (B): no ADS, a câmera do mundo recebe `setCameraFov(cam, hfov, 1/M)`. O viewmodel mantém o FOV próprio e a pose de ADS encosta o ocular no olho, de modo que ele ocupe ~80–90% da altura da tela. O vidro fica transparente (tinta, reflexo fraco e retículo gravado na UV, em SFP). A sombra do ocular usa a máscara acima. Fora da lente, a tela fica preta (como no CS) ou borrada e escurecida (como no CoD), aproveitando o `dofPass` com uma máscara circular.
  - "Alta qualidade", modo (C): o mesmo modelo 3D, mas a lente amostra um RT de PiP, o que mantém a periferia nítida e sem zoom.
  - Com o ocular cobrindo quase a tela toda, (B) e (C) ficam visualmente próximos, porque só a periferia muda.
- **Lupa em espaço de tela (D).** Serve para magnificadores de 1,5 a 3x ou miras baratas, mas com M = 4 a imagem da lente tem 1/16 dos pixels únicos e fica borrada. Não serve para 8x.

### Gaps
- Não achei fonte primária (GDC, blog de estúdio) sobre como Tarkov, Sandstorm, Squad, Hunt ou Battlefield **barateiam o PiP** (resolução do RT, viés de LOD, sombras, taxa de atualização). Só existem relatos de jogadores.
- Não achei a implementação exata das lunetas do CoD MW (2019 em diante), Hunt: Showdown e Battlefield.
- Não achei números oficiais do custo de cada modo. As quedas citadas são relatos de jogadores em hardware variado.

---

## 3. Matemática de FOV e sensibilidade: ampliação → FOV, ADS, FOV do viewmodel, sensibilidade com zoom (mouse, controle e toque)

### Takeaway
Ampliação e FOV se relacionam pela tangente: `tan(F_z/2) = tan(F_0/2) / M`. A regra geral de sensibilidade é o **casamento por distância no monitor** (monitor distance match), com coeficiente c:
`s = atan(c·tan(F_z/2)) / atan(c·tan(F_0/2))`.
Com c → 0, s = 1/M: é o "0%", ou "zoom ratio", que casa o movimento em volta da mira. Com c = 1, s = F_z/F_0: é o "100%", razão linear de FOV. É isso que o motor Source faz com `zoom_sensitivity_ratio 1` usando FOVs de 4:3, o que equivale a 75% da largura em 16:9. O Uniform Soldier Aiming do Battlefield com coeficiente padrão de 133% (vertical) dá o mesmo resultado em 16:9. Para o MASSACRE: **0% como padrão**, coeficiente escolhível, multiplicador por óptica e a mesma lei aplicada ao controle (velocidade angular) e ao toque (pixel → ângulo).

### Cited Findings
- **Motor Source (CS e TF2).** O `zoom_sensitivity_ratio` "correto" para casar pela tangente é `(FOV_sem_zoom / FOV_com_zoom) · tan(FOV_com_zoom/2) · cot(FOV_sem_zoom/2)`. Os valores são 0,793471 no TF2 (fov 90, luneta de 20°) e 0,818933027 no CS:GO. O valor 0,919455 casa o eixo vertical. Com ratio 1, o CS:GO exige a mesma distância de mouse para levar a mira do centro até a borda de uma tela 4:3, com ou sem luneta. O ratio "independe do aspecto". As FOVs da AWP no CS:GO são 40° e 10°. — [TeamFortress.tv: On the "correct" value of zoom_sensitivity_ratio](https://www.teamfortress.tv/35467/on-the-correct-value-of-zoom-sensitivity-ratio)
- O CS:GO usa casamento de **100% na horizontal em 4:3**, o que equivale a 75% na horizontal em 16:9. O 0% seria o melhor matematicamente porque a memória muscular está na mira: microajustes e controle de recuo ficam iguais em todos os FOVs. Para converter entre eixos: 100% vertical × 9/16 = 56,25% horizontal em 16:9. — [Tom's Blog: Sensitivity Conversion between 3D Games](https://tomhepz.com/post/sensitivity/)
- **Battlefield, Uniform Soldier Aiming.** Define uma "distância de controle" na tela e iguala o movimento de mouse para alvos a essa distância em qualquer FOV de luneta. O coeficiente padrão é 1,33. A comunidade publica fórmulas no formato `atan((1080/1920)·1,33·tan(hFOV/2))` para cada FOV. — [Mouse Sensitivity Forum: Battlefield's USA formula](https://www.mouse-sensitivity.com/forums/topic/3346-battlefields-uniform-soldier-aiming-formula/); [tópico 2747](https://www.mouse-sensitivity.com/forums/topic/2747-battlefield-uniform-soldier-aiming-formula/) (ambos: trechos do resultado de busca; o site devolveu 403)
- **Valorant: fontes em conflito.** Uma calculadora diz que o multiplicador 1,0 é o casamento de 100% na horizontal ("mesma distância até a borda da tela") e que o 0% na ADS de 1,25x (Vandal, Phantom, Bulldog) seria 0,870. Outro trecho diz que 1,0 "já equivale a 0% em todas as lunetas". — [eDPI Calculator: Valorant Scoped Sensitivity](https://edpi-calculator.org/tools/valorant-scoped-sensitivity) (fonte comercial de baixa confiabilidade)
- **PUBG Mobile.** Cada óptica (sem mira, red dot, 2x, 3x, 4x, 6x, 8x) tem **o próprio controle deslizante** de sensibilidade de ADS e de giroscópio. As recomendações da comunidade descem com a ampliação (por exemplo, giroscópio de 30–40% em 2x e de 10–20% em 8x). — [Rivals: PUBG Mobile Sensitivity Guide](https://getrivals.com/guides/pubgm-sensitivity-guide/) (fonte: trecho do resultado de busca)
- **Viewmodel.** Costuma ser desenhado num passe separado para ficar sempre na frente do mundo. Ele é modelado e animado para um FOV específico, por isso esse FOV em geral é fixo. Uma alternativa para a arma ocultar o mundo é desenhá-la com depth range `0..0,0000001`. — [Bevy issue #12658](https://github.com/bevyengine/bevy/issues/12658); [GameDev.net: first-person weapon with different FOV](https://gamedev.net/forums/topic/605666-first-person-weapon-with-different-fov-in-deferred-engine/4831984/) (trechos do resultado de busca). Um "Weapon FOV" separado corrige o estiramento com FOV alto e a arma atravessando paredes, pode ser feito por vértice no material sem render target extra e é usado em Shadow Warrior, HL2, Battlefield e Dying Light. — [Imaginary Blend: Weapon FOV](https://imaginaryblend.com/2018/10/16/weapon-fov/) (fonte: trecho do resultado de busca)
- **Duas câmeras no three.js.** A receita é `renderer.autoClear = false`, limpar uma vez, depois `setViewport`/`setScissor`/`setScissorTest(true)` por câmera e limpar a área antes de desenhar a segunda. — [Fórum three.js: Rendering two cameras on top of each other](https://discourse.threejs.org/t/rendering-two-cameras-on-top-of-each-other/66739)

### Inferences
- **Tabela para o MASSACRE** (hFOV de 100° em 16:9, vFOV de 67,67°). As colunas `s` são o multiplicador de sensibilidade de cada regra; "75% H" equivale ao padrão do CS e ao 133% vertical do Battlefield em 16:9.

  | M | vFOV | hFOV 16:9 | s 0% | s 75% H | s 100% H | s 100% V |
  |---|---|---|---|---|---|---|
  | 1,25 | 56,41° | 87,27° | 0,800 | 0,851 | 0,873 | 0,834 |
  | 1,5 | 48,16° | 76,93° | 0,667 | 0,737 | 0,769 | 0,712 |
  | 2 | 37,06° | 61,58° | 0,500 | 0,576 | 0,616 | 0,548 |
  | 3 | 25,19° | 43,33° | 0,333 | 0,397 | 0,433 | 0,372 |
  | 4 | 19,03° | 33,18° | 0,250 | 0,301 | 0,332 | 0,281 |
  | 6 | 12,75° | 22,47° | 0,167 | 0,203 | 0,225 | 0,188 |
  | 8 | 9,58° | 16,95° | 0,125 | 0,153 | 0,170 | 0,142 |

  No código atual basta chamar `setCameraFov(camera, hfov, 1/M)`, porque o `camera.js` já multiplica a tangente.
- **Conferências.**
  - A AWP do CS (FOV de 4:3 indo de 90° para 40° e 10°) equivale a **M = 2,747x e 11,43x** no centro da tela.
  - O ratio de 0% dá 0,818933 no zoom 1 e 0,787398 no zoom 2. Os 4% de diferença explicam por que um único ratio não casa os dois níveis de zoom.
  - `1,333·tan(v/2) = 0,75·tan(h/2) = 0,8938` em 16:9, o que confirma que o 133% vertical do Battlefield é igual ao 75% horizontal (o padrão do CS).
  - No Valorant, se a ADS de 1,25x usar FOV linear (103° / 1,25 = 82,4°), o 0% dá exatamente 0,870. Isso bate com a hipótese de "1,0 = 100% horizontal" e contradiz "1,0 = 0%". Nesse caso, a ampliação real no centro seria de 1,436x. Isto é uma dedução, não uma confirmação.
- **Justiça competitiva.** Definir M em relação a um **FOV de referência fixo**, não ao FOV que o jogador escolheu, para que uma 4x mostre o mesmo cone de mundo para todos. É assim que o CS faz, com FOVs de zoom fixos.
- **Transição de ADS.** Interpolar em espaço log-tangente: `tan(F(t)/2) = tan(F_0/2) · M^(−t)`, com t suavizado entre 0 e 1. Assim a velocidade percebida do zoom fica constante. A sensibilidade deve seguir o FOV **corrente**, `s(F(t))`, sem salto quando o estado vira ADS. A máscara preta ou o borrão (modo B) entram no fim, com t > 0,8.
- **Controle.** O analógico gera velocidade angular `ω = ω_max · curva(x)`. Com zoom, usar `ω · s_0% = ω/M`, que mantém constante a velocidade em pixels perto da mira (`px/s ≈ ω·(H/2)/tan(F/2)`), e somar o multiplicador por óptica. Os raios de aim assist devem ser definidos **em pixels** e convertidos para ângulo com o FOV corrente, para não encolherem M vezes.
- **Toque.** `Δθ = k · Δpx · 2·tan(vFOV_atual/2) / H_px`. Usar o FOV corrente já produz o 0%, porque o ponto sob o dedo acompanha o dedo. Somar controles por óptica como no PUBG Mobile. **Giroscópio:** `Δθ_câmera = k_gyro · Δθ_aparelho · s(c)`.
- **FOV do viewmodel.** O MASSACRE já tem as camadas separadas no `postPipeline`. O ideal é manter o FOV do viewmodel fixo e, no máximo, estreitá-lo um pouco no ADS para o ocular crescer na tela. Isso também muda o tamanho do RT do PiP e exige a correção `k` e a abordagem (b) do red dot.

### Gaps
- O mouse-sensitivity.com, a referência da comunidade, devolveu 403. As fórmulas acima foram deduzidas e conferidas com os números do TF.tv e do Tom's Blog, não citadas do site.
- A fórmula interna exata do Valorant não foi confirmada: as fontes se contradizem.
- Não achei uma fonte oficial sobre como os jogos escalam o aim assist com o zoom.

---

## 4. Brilho de luneta visível aos inimigos (scope glint), reflexos na lente e sujeira

### Takeaway
No Battlefield 4, o brilho só aparece com a luneta em ADS, para lunetas **acima de 4x**, e para quem estiver **dentro de um cone de 10°** da direção em que o atirador mira. Ele é mais forte na linha de tiro direta. A implementação natural é um sprite aditivo virado para a câmera na objetiva, com intensidade dependente do ângulo. Reflexos e sujeira na lente são efeitos de shader no vidro (Fresnel com mapa de ambiente e textura de sujeira modulada por luz forte) que custam pouco.

### Cited Findings
- **BF4.** O brilho só é visível para quem está num ângulo de até 10° da direção do atirador, e só com a mira em ADS. "Luneta de alta potência" é a que passa de 4x. O brilho é mais forte na linha de tiro direta e menos visível em ângulos oblíquos. As formas de evitá-lo são mirar para longe do inimigo, trocar de arma ou usar ampliação menor ou mira mecânica. — [Battlefield Wiki: Scope Glint](https://battlefield.fandom.com/wiki/Scope_Glint) (fonte: trecho do resultado de busca; a página devolveu 402)
- O shader de lente de exemplo trata o vidro como superfície PBR (`Standard`, com mapas de metalicidade e suavidade). Os reflexos vêm do sistema de iluminação do motor. — [GitHub Gist: kameronbrooks](https://gist.github.com/kameronbrooks/0e17fa98c9429100981eb723615e02b0)

### Inferences
- **Brilho em three.js.** Um `THREE.Sprite` (ou um quad) aditivo na objetiva, com `sizeAttenuation:false` e tamanho em pixels limitado, para continuar visível a longa distância. A intensidade seria:
  `I = I0 · pow(saturate((dot(mira_atirador, dir_para_observador) − cos10°) / (1 − cos10°)), p) · ADS · [M > 4]`,
  opcionalmente multiplicada por um termo de sol, `saturate(dot(mira, dir_sol))`, se o brilho for tratado como reflexo solar. O estado de ADS e a direção da mira já precisam trafegar na rede para a animação, então o custo de rede é zero. A oclusão pode ser um raycast a cada N quadros com o `three-mesh-bvh`, que o projeto já tem. Para não piscar, usar `depthTest:true` com um pequeno deslocamento em direção à câmera.
- **Reflexo no vidro.** Somar `F · env(reflect(−V, N))` com Fresnel de Schlick, `F = F0 + (1 − F0)(1 − cosθ)^5`. F0 ≈ 0,04 é o valor convencional de vidro em PBR, e um vidro com tratamento antirreflexo teria menos. Isso é uma suposição a calibrar. Pode vir do `scene.environment` (PMREM) ou de um cubemap falso gerado proceduralmente.
- **Sujeira na lente.** Uma textura de sujeira em tons de cinza (gerada por canvas, mantendo a regra "100% procedural") multiplicada pela luminância do bloom na área da lente, para ela aparecer contra o sol ou a luz de uma lanterna. O custo é uma amostra a mais, só nos pixels do vidro.

### Gaps
- Não conferi as regras de brilho de Hunt: Showdown, PUBG, Tarkov nem dos outros Battlefields (a página da wiki não abriu).
- Não achei implementações publicadas de reflexo e sujeira em lentes de lunetas de jogos comerciais.

---

## 5. Visão noturna (NVG) e térmica: pós-processamento, calor por material e paletas

### Takeaway
A **NVG** é um passe de tela cheia barato com luminância amplificada, halo nas luzes (o bloom que o projeto já tem, com limiar mais baixo), cintilação (ruído animado), tinta de fósforo (P43 verde ou P45 branco) e a máscara circular do tubo. A **térmica** não é um filtro de cor: cada material e entidade precisa de um **valor de calor** (o Arma usa texturas "_TI" de 4 canais), renderizado sem iluminação e mapeado por uma paleta 1D (white hot, black hot, ironbow). O vidro deve ser **opaco** porque o LWIR não atravessa vidro. Numa luneta térmica em PiP, o próprio passe do PiP usa os materiais térmicos, então não há passe extra.

### Cited Findings
- **Shader de NVG da Geeks3D (GLSL).**
  - Luminância por `dot(c, vec3(0.30, 0.59, 0.11))`. Se `lum < luminanceThreshold` (0,2), `c *= colorAmplification` (4,0).
  - Ruído de uma textura, com UV animada por `0.4·sin(t·50)` e `0.4·cos(t·50)`, que também desloca a amostragem da cena (`n.xy · 0.005`).
  - Cor final `(c + n·0.2) · vec3(0.1, 0.95, 0.2) · máscara`, com máscara binocular.
  — [Geeks3D: Night Vision Post Processing Filter (GLSL)](https://www.geeks3d.com/20091009/shader-library-night-vision-post-processing-filter-glsl/)
- A NVG é verde porque a maioria dos tubos usa fósforo **P43**, que brilha em verde. Tubos mais novos usam **P45**, que brilha em branco. O olho humano é mais sensível ao verde. — [ATN: Why is night vision green](https://www.atncorp.com/blog/why-is-night-vision-green) (fonte: trecho do resultado de busca). O verde leva vantagem em percepção de contraste, conforto e custo, e o branco em fidelidade e reconhecimento. — [LUMOPT: Green vs White Phosphor](https://www.lumopt.com/news/night-vision-green-phosphor-vs-white-phosphor/) (fonte: trecho do resultado de busca)
- O **halo** é o brilho em volta de fontes pontuais fortes e pesa especialmente em lugares com iluminação artificial. A **cintilação** (granulado) vem da própria amplificação: a placa de microcanais multiplica poucos elétrons em milhares, um processo estatístico que não é liso. Tubos melhores precisam de menos ganho e mostram menos grão. — [Vantax: Night vision tube specs explained](https://www.vantaxnv.com/blogs/blog/night-vision-intensifier-tube-specs-explained) (fonte: trecho do resultado de busca)
- **Arma, textura térmica "_TI" (4 canais, desde o Arrowhead).**
  - R: quanto o objeto aquece com o sol.
  - G: base de ruído e lightmap, mais as fontes de calor que esquentam só com o veículo ligado.
  - B: preto, com branco nas partes móveis (pneus).
  - A: calor metabólico (pessoas) e calor do cano (tanques e armas).
  — [Bohemia Wiki: Thermal Imaging Maps](https://community.bistudio.com/wiki/Thermal_Imaging_Maps) (fonte: trecho do resultado de busca; a página devolveu 403)
- **Paletas.** White hot mostra o quente em branco e o frio em preto. Black hot é o inverso e ajuda a identificar forma e postura através da vegetação. Ironbow vai do preto ao azul no frio e passa por magenta, laranja e amarelo até o branco no quente, destacando anomalias e calor corporal. Trocar a paleta não muda os dados de temperatura. — [ATN: Thermal Color Palettes 101](https://www.atncorp.com/journal/thermal-color-palettes-guide); [FLIR: Picking a thermal color palette](https://www.flir.com/discover/industrial/picking-a-thermal-color-palette/) (trechos do resultado de busca)
- **Vidro.** O vidro comum é opaco ao infravermelho de onda longa (7 a 14 µm), a faixa da maioria das câmeras térmicas. A câmera vê a temperatura e os reflexos da superfície do vidro, não a pessoa atrás da janela. — [FLIR: Can thermal imaging see through walls?](https://www.flir.com/discover/home-outdoor/can-thermal-imaging-see-through-walls/) (fonte: trecho do resultado de busca)

### Inferences
- **Pipeline de NVG no MASSACRE** (um passe no pós-processamento, antes do tonemapping, em HDR):
  1. `L = luma(hdr) · ganho`, com ganho automático `alvo / (lumMédia + ε)` limitado a um teto (o tubo satura). Depois, compressão tipo `L/(1+L)`.
  2. Halo: o bloom existente com limiar menor e raio maior enquanto a NVG estiver ligada.
  3. Ruído por hash a cada quadro, com amplitude proporcional a `sqrt(ganho)`. É uma analogia com o ruído de fótons: mais ganho, mais grão.
  4. Leve desfoque, porque a resolução do tubo é limitada.
  5. Tinta de fósforo: P43 ≈ `(0.1, 0.95, 0.2)` (valor da Geeks3D). Para o P45, um branco levemente azulado é uma suposição a calibrar.
  6. Máscara do tubo, circular ou binocular, com borda suave.
  O custo é um passe de tela cheia mais o bloom que já existe, viável até em celular (dá para rodar em meia resolução). Um **iluminador IR** seria uma SpotLight visível só com NVG, e **lasers IR** ficariam numa layer que só entra no render quando a NVG está ligada.
- **Pipeline térmico.**
  - Cada material ou entidade recebe `heat` entre 0 e 1: jogador vivo alto, arma com calor que sobe a cada tiro e decai exponencialmente, cenário com "aquecimento solar" à moda do canal R do Arma, e cadáver que esfria.
  - Renderizar **sem iluminação** (barato) num RT, ou no próprio RT do PiP no caso da luneta térmica.
  - Depois, um passe de "sensor": `t = saturate((T − nível)/faixa + 0.5)` com ganho e nível automáticos (AGC), uma amostra numa LUT 256×1 da paleta (black hot é `1 − t`), borrão leve, ruído e a máscara.
  - No three.js r186 existe `scene.overrideMaterial`, e cada material pode recusar a substituição com `material.allowOverride = false`. Com isso dá para fazer um material térmico único mais exceções. O calor por objeto pode vir de um atributo, de `userData` lido em `onBeforeRender` com `uniformsNeedUpdate`, ou de materiais "gêmeos" trocados por layer. Os três caminhos precisam ser testados.
  - **Vidro**: renderizar opaco com a temperatura do ambiente, para que ninguém seja visto através dele, como no mundo real.
- **Custo da térmica.** Em tela cheia, o passe térmico sem iluminação **substitui** o passe iluminado e pode até ficar mais barato. Numa luneta térmica em PiP, o passe PiP vira o passe térmico, sem custo além do próprio PiP.

### Gaps
- Não achei notas oficiais de implementação ou desempenho de NVG e térmica em jogos comerciais (Tarkov, CoD MW, Ready or Not, Ground Branch).
- Não achei valores de cor medidos para o fósforo P45 nem parâmetros de halo em pixels.

---

## 6. Mira laser e lanterna de arma (feixe, ponto, visibilidade, SpotLight com cookie, sombra, ofuscamento)

### Takeaway
O laser tem duas partes: um **feixe** aditivo fino, mais forte perto do emissor e visível pela poeira no ar, e um **ponto** colocado por raycast, testado contra a profundidade e com bloom. Como o viewmodel usa outro FOV, a ponta do feixe precisa **partir do cano desenhado**. A lanterna é uma `SpotLight` com cookie (`.map`). No r186, o cookie **funciona sem sombra**, apesar do aviso na documentação. Sombra de spot custa um passe extra de profundidade e deve ficar só com a lanterna do jogador local no desktop. **Não ligue e desligue luzes com `visible`**: isso muda a contagem de luzes e força a troca ou recompilação de shaders.

### Cited Findings
- **Laser do TartarusEngine.**
  - Um feixe fino saindo do cano, "mais brilhante perto do emissor, com poeira à deriva", e um ponto quente "sobre a superfície atingida, com teste de profundidade e bloom".
  - A ponta próxima do feixe segue a projeção do viewmodel, para sair do cano desenhado ao longo da linha dele.
  - Um passe novo, `WorldOverlay`, desenha os efeitos de mundo "depois do mundo e antes do passe do viewmodel".
  - Zeragem: o cano tem 1,68° acima da linha de visada, e os tiros e o laser cruzam a linha de visada a 25 m.
  - Furos de bala feitos por raycast a partir do cano, no máximo 512 decals.
  — [GitHub: TartarusEngine PR #399](https://github.com/JCamberos27/TartarusEngine/pull/399)
- Um feixe de laser só aparece se houver partículas no ar (poeira, névoa, fumaça, umidade, chuva, neve). Em ar limpo, não aparece. — [ILDA: Haze and fog for laser shows](https://www.ilda.com/hazefoglasers.htm) (fonte: trecho do resultado de busca)
- **`SpotLight` no three.js (documentação).** `.map` é uma textura que modula a cor da luz, e o efeito de "cookie" vem dos pixels `(0,0,0,1−cookie)`. **Aviso da doc:** a propriedade é desativada se `castShadow` for `false`. Os outros parâmetros: `angle` até π/2 (padrão π/3), `penumbra` entre 0 e 1, `decay` 2 (fisicamente correto), `distance` (0 = sem limite) e `power` em lúmens. — [three.js docs: SpotLight](https://threejs.org/docs/pages/SpotLight.html)
- **Código do r186, que contradiz o aviso da documentação.**
  - As spot lights são ordenadas como "[sombra com mapa, sombra sem mapa, **mapa sem sombra**, nenhum]".
  - `NUM_SPOT_LIGHT_COORDS = sombras + mapas − sombrasComMapa`.
  - O cookie multiplica `directLight.color` por `spotColor.rgb` só dentro do frustum projetado da luz.
  — [three.js r186: lights_fragment_begin.glsl.js](https://github.com/mrdoob/three.js/blob/r186/src/renderers/shaders/ShaderChunk/lights_fragment_begin.glsl.js); [WebGLProgram.js](https://github.com/mrdoob/three.js/blob/r186/src/renderers/webgl/WebGLProgram.js); [WebGLLights.js](https://github.com/mrdoob/three.js/blob/r186/src/renderers/webgl/WebGLLights.js) (conferido no pacote local three 0.186.1)
- **Contagem de luzes no r186.** O `WebGLRenderer` só registra uma luz se `object.visible` for verdadeiro e se ela passar em `object.layers.test(camera.layers)`. `numSpotLights` e a contagem de mapas e sombras entram na chave de cache do programa. — [three.js r186: WebGLRenderer.js](https://github.com/mrdoob/three.js/blob/r186/src/renderers/WebGLRenderer.js); [WebGLPrograms.js](https://github.com/mrdoob/three.js/blob/r186/src/renderers/webgl/WebGLPrograms.js) (conferido localmente)

### Inferences
- **Feixe.** Um quad com billboard axial no vertex shader, mais barato e sem as facetas de um cilindro:
  `p = mix(A, B, along)`, `right = normalize(cross(normalize(B − A), normalize(camPos − p)))`, `p += right · side · largura/2`.
  O material é aditivo, com `depthWrite:false`, `depthTest:true` e cor HDR. Alfa ao longo do feixe: `a(s) = exp(−s/L) · poeira(s, t)`, com a poeira vinda de ruído 1D rolando. Uma **largura mínima em pixels** (`w ≥ k_px · dist · 2·tan(vFOV/2)/H`) evita cintilação. A visibilidade do feixe depende de um parâmetro de "névoa ou poeira" do mapa (seguindo o princípio da ILDA) e cresce quando o observador olha ao longo do feixe. Isso último é uma aproximação de espalhamento para frente, ainda a validar.
- **Ponto.** A cada quadro, um raycast com o `three-mesh-bvh` partindo do cano **pelo eixo do laser** (não pelo raio da câmera). No ponto atingido, um sprite ou quad afastado ε ao longo da normal, com tamanho `d0 + dist·divergência` e piso de 1 a 2 px, aditivo e em HDR para o bloom. Para o jogador local, o feixe nasce na posição do cano projetada pelo viewmodel: pegar o NDC do cano na câmera do viewmodel, desprojetar na câmera do mundo a uns 30–50 cm e desenhar o feixe no mundo a partir dali (a solução do TartarusEngine).
- **Regras de jogo.** Lasers visíveis (vermelho e verde) aparecem para todos. Lasers IR só com NVG, por layer. O ponto some além de um alcance máximo. O estado "laser ligado" vai pela rede.
- **Lanterna.**
  - Um **pool fixo** de SpotLights, por exemplo a lanterna local mais as 2–3 lanternas remotas mais próximas. Para "desligar", usar `intensity = 0` em vez de `visible = false`, o que mantém a contagem de luzes e o programa.
  - As mesmas layers de luz no passe principal e no PiP.
  - Cookie gerado por canvas (anéis e hotspot), `angle` de 15–25°, `penumbra` de 0,3–0,5 e `distance` definido para limitar o alcance.
  - Sombra (`castShadow`) só na lanterna local no desktop, com shadow map de 512 ou 1024. Cada spot com sombra é mais uma renderização de profundidade da cena por quadro. No celular, sem sombra: o cookie continua funcionando no r186.
- **Ofuscamento.** `I = saturate((dot(dirLuz, −dirObs) − cos(ângulo)) / (1 − cos(ângulo))) · 1/(1 + d²/d0²) · visível(raycast)`. Com isso, desenhar um sprite de glare na posição da luz na tela, aplicar um aumento curto de exposição (clarão branco) e, com NVG, um ganho muito maior (o tubo "estoura").

### Gaps
- Não achei fontes sobre as regras de visibilidade de laser e lanterna em Tarkov, Ready or Not ou Ground Branch, nem sobre o alcance usado nesses jogos.
- Não achei medições do custo de sombras de SpotLight no three.js em GPU integrada ou celular. É preciso medir com o `gpuTimer.js` do projeto.

---

## 7. Especificidades do three.js: render targets, layers, scissor/viewport, stencil na lente, custo de MSAA, resolução dinâmica, WebGL2 × WebGPU e limites de GPU móvel

### Takeaway
Tudo o que é preciso já existe no three.js r186: `WebGLRenderTarget` (com `samples`, `stencilBuffer` e `resolve*Buffer`), `Layers` (32 bits), `setScissor`/`setViewport`, as propriedades de stencil nos materiais e o `shadowMap.autoUpdate`. O custo em celular vem do tiling. Cada troca de framebuffer descarrega a memória do tile. MSAA em render target sem resolução no próprio tile grava um buffer 4x na memória e lê de volta. E o r186 **só chama `invalidateFramebuffer` no navegador do Oculus**. Então: PiP sem MSAA e em meia resolução no celular, com o mínimo de alvos, e o modo 2D/híbrido como padrão móvel. O WebGPURenderer tem fallback para WebGL2, mas mudar para ele exigiria portar os passes GLSL do projeto.

### Cited Findings
- **`RenderTarget`.** `samples` (0 = sem MSAA), `depthBuffer` (padrão true), `stencilBuffer` (padrão **false**), `resolveDepthBuffer` e `resolveStencilBuffer` ("quando false, economiza banda"; só importa em alvos multiamostrados no WebGL), `depthTexture`, `generateMipmaps` (padrão false), `count` (MRT), e `scissor`/`viewport` próprios. — [three.js docs: RenderTarget](https://threejs.org/docs/pages/RenderTarget.html)
- **Stencil no material.** `stencilWrite` precisa ser true para gravar ou comparar. Os outros campos são `stencilRef`, `stencilFunc` (padrão Always), `stencilFuncMask`, `stencilWriteMask` e `stencilFail`/`stencilZFail`/`stencilZPass`. `colorWrite:false` junto com `renderOrder` cria oclusores invisíveis. — [three.js docs: Material](https://threejs.org/docs/pages/Material.html)
- **`Layers`.** São 32 camadas (0 a 31). Um objeto só aparece se tiver uma layer em comum com a câmera. — [three.js docs: Layers](https://threejs.org/docs/pages/Layers.html)
- **MSAA em render target no r186.**
  - Se a extensão `WEBGL_multisampled_render_to_texture` existir, o three.js a usa.
  - Senão, cria renderbuffers com `renderbufferStorageMultisample` e resolve com `blitFramebuffer`.
  - Depois do blit, só chama `invalidateFramebuffer` quando `supportsInvalidateFramebuffer` é verdadeiro, e isso é definido por `/OculusBrowser/.test(navigator.userAgent)`.
  — [three.js r186: WebGLTextures.js](https://github.com/mrdoob/three.js/blob/r186/src/renderers/webgl/WebGLTextures.js) (conferido no pacote local)
- **Sombras e override.** O `WebGLShadowMap.render` retorna cedo se `autoUpdate === false && needsUpdate === false`. — [three.js r186: WebGLShadowMap.js](https://github.com/mrdoob/three.js/blob/r186/src/renderers/webgl/WebGLShadowMap.js). `Material.allowOverride` (padrão true) define se o material pode ser substituído por `Scene.overrideMaterial`. — [three.js r186: Material.js](https://github.com/mrdoob/three.js/blob/r186/src/materials/Material.js)
- **MDN.**
  - "Guardar dados que você não vai usar de novo pode custar caro, sobretudo nas GPUs com tiling comuns em celulares." Use `invalidateFramebuffer` (WebGL 2), principalmente em anexos de profundidade, stencil e multiamostrados.
  - Configure os framebuffers "quentes" antes, porque mudar os anexos invalida o FBO.
  - Estime um orçamento de VRAM por pixel.
  - Profundidade e stencil costumam ser inseparáveis, com arredondamento para 4 bytes.
  - Reduza `canvas.width/height` mantendo o tamanho CSS: é a base da resolução dinâmica.
  - `mediump` pode corromper a renderização por falta de precisão.
  - Agrupe draw calls.
  — [MDN: WebGL best practices](https://developer.mozilla.org/en-US/docs/Web/API/WebGL_API/WebGL_best_practices)
- **Arm (Mali).** Com resolução no próprio tile, o MSAA 4x sai "praticamente de graça (tipicamente 1–2%)". O caminho de resolução explícita é "altamente ineficiente" porque grava na memória um buffer 4x maior e lê de volta, e é "altamente recomendado evitá-lo no Mali". — [Arm Vulkan SDK: Multisampling](https://arm-software.github.io/vulkan-sdk/multisampling.html). Religar framebuffers (`glBindFramebuffer`) descarrega os pixels do tile para a memória, e `glInvalidateFramebuffer` evita gravar profundidade e stencil. — [Arm: Deferred shading on mobile](https://developer.arm.com/community/arm-community-blogs/b/mobile-graphics-and-gaming-blog/posts/deferred-shading-on-mobile); [Arm: The Mali GPU, An Abstract Machine, Part 2](https://developer.arm.com/community/arm-community-blogs/b/mobile-graphics-and-gaming-blog/posts/the-mali-gpu-an-abstract-machine-part-2---tile-based-rendering) (trechos do resultado de busca)
- **WebGPURenderer.** Tenta o WebGPU e, se o navegador não suportar, volta para um backend WebGL2. A opção `forceWebGL` força o WebGL2. `antialias` usa 4 amostras por padrão, e `samples` sobrescreve esse valor. O renderer usa uma biblioteca de materiais de nós (`StandardNodeLibrary`). — [three.js docs: WebGPURenderer](https://threejs.org/docs/pages/WebGPURenderer.html)

### Inferences
- **Ordem do quadro no MASSACRE com PiP ligado.** O `postPipeline.render` desenha a cena no `sceneTarget` e só depois as camadas, chamando `layer.beforeRender?.(r)` antes de cada uma. Isso permite:
  1. O passe principal da cena, que atualiza as shadow maps.
  2. No `beforeRender` da camada do viewmodel, com ADS acima de ~0,3 e luneta PiP: guardar o alvo atual, `renderer.setRenderTarget(pipRT)`, limpar, ligar `shadowMap.autoUpdate = false` para reaproveitar as sombras **do mesmo quadro**, chamar `render(scene, pipCam)` (com `pipCam.layers` sem o corpo local nem o viewmodel e com as mesmas luzes), e depois restaurar o `autoUpdate`, o alvo da camada e a cor de limpeza.
  3. O viewmodel, cujo material de lente amostra `pipRT.texture`.
  Outra opção é renderizar o PiP **antes** do pipeline, com as sombras do quadro anterior (um quadro de atraso quase invisível). Em celular, cada troca de alvo no meio do passe de camadas custa mais uma descarga de tile.
- **Alternativa sem RT: stencil com scissor.** A lente escreve `stencilRef = 1` com `colorWrite:false`, e o mundo ampliado é desenhado com `stencilFunc = Equal` e `setScissor` no retângulo da lente, o que limita o custo de fragmentos. Isso exige `stencilBuffer:true` no `sceneTarget` (e `resolveStencilBuffer:false` se houver MSAA) e mistura o mundo ampliado com o pós-processamento do quadro, o que complica o DoF e o bloom. Para o pipeline atual do MASSACRE, o RT separado é mais simples.
- **Memória.** Um RT de 512² em RGBA8 com profundidade de 24/8 ocupa ~2 MB. Com 4x MSAA via renderbuffer, somam-se ~8 MB. No celular, `samples: 0` no PiP. No desktop, 4x é aceitável se a medição com o `gpuTimer.js` permitir.
- **Celular.** Como o r186 não invalida os anexos multiamostrados fora do Oculus Browser, **o MSAA do `sceneTarget` pode sair caro no Android**: é melhor desligá-lo lá e ficar só com o SMAA, que já existe. Também vale evitar trocas de alvo desnecessárias (cada passe de pós é uma troca). Os níveis sugeridos, a medir:
  - **Celular:** red dot barato; lunetas no modo (B) ou 2D; NVG e térmica em meia resolução; laser e lanterna sem sombras.
  - **GPU integrada:** (B) por padrão, PiP opcional com RT ≤ 512.
  - **Desktop dedicado:** PiP com RT de até 1024 e MSAA.
- **Resolução dinâmica.** O pipeline e o `gpuTimer.js` já existem. Durante o ADS com um ocular grande (AWP), a tela fora da lente fica quase toda preta ou borrada, então dá para **baixar a resolução do passe principal** enquanto o PiP roda e segurar os 60/30 fps.
- **Custo de CPU do PiP.** O PiP repete a submissão de draw calls, e esse é o gargalo típico do WebGL. É preciso medir com `renderer.info.render.calls` e dividir o mapa em pedaços para o frustum estreito cortar objetos.
- **WebGPU.** Hoje não compensa migrar: os passes de pós, o red dot e a lente estão em GLSL/ShaderMaterial e teriam de ser portados para nós/TSL. Reavaliar quando o custo de CPU das draw calls (duas cenas por quadro no PiP) virar o gargalo.

### Gaps
- Não sei qual fração dos celulares Android com Chrome expõe `WEBGL_multisampled_render_to_texture` (sem fonte).
- Não achei benchmarks de PiP em three.js em GPU integrada ou celular, nem o custo real de uma troca de render target em GPUs Adreno e Mali via WebGL. É preciso medir no projeto.
- A página da documentação do WebGPURenderer não diz explicitamente se `ShaderMaterial` ou `onBeforeCompile` são suportados. A necessidade de portar para TSL é uma inferência a confirmar.
