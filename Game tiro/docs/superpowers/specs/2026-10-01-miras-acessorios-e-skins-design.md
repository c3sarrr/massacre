# Miras, acessórios e skins das armas realistas — desenho

- **Data:** 2026-10-01.
- **Estado:** proposta para o usuário aprovar (o desenho das miras e das skins pedido na resposta à parada P1 da 4.1c,
  em 2026-09-28). Nada daqui é implementado antes da aprovação; as perguntas abertas estão na seção 9.
- **Base:** as decisões do usuário de 2026-09-28 (seção 0), o relatório da pesquisa em
  `docs/research/miras-acessorios-skins.md` (cinco seções, 167 fontes; as notas com os números e os links em
  `docs/research/miras-acessorios-skins/`) e os 29 boards novos do Pinterest (QRD a QCT, 688 pins; moodboard, item 14).
  Os números de jogo abaixo que não vêm de uma fonte são pontos de partida marcados como tais, para medir na pista.

## 0. Decisões do usuário

De 2026-09-28, na resposta à parada P1 da 4.1c:

1. **Miras e acessórios só nos modos casuais** — Mata-mata (FFA), Mata-mata em Times, Gun Game e Ondas. O Competitivo
   continua puro, como o CS2: só as miras de fábrica das armas que já as têm (as lunetas da AWP, da Scout, da SCAR-20 e
   da G3SG1 e as miras da AUG e da SG 553, como a subfase 4.5 já previa).
2. **Os quatro tipos de skin:** artísticas no estilo do CS2, acabamentos reais, temáticas de estúdio e troca de modelo.
3. **A ordem:** terminar a 4.1c (as empunhaduras e as três armas no jogo), depois as miras, depois as skins.

Continuam valendo: armas e acessórios realistas, construídos pelos nossos scripts do Blender a partir de medidas de fotos
de licença livre (nenhum modelo de terceiros), texturas CC0 só no Blender, nomes genéricos sem logotipo nem marca
(regra 9), sem boil nas armas e em tudo o que vai nelas, a progressão sem conta, no IndexedDB (seção 0.15 das regras).

## 1. Onde entra no plano (proposta)

A pesquisa mostra duas metades nas miras: a **visual** (os modelos, a montagem nos trilhos, o retículo no vidro, a
luneta com a sombra do ocular, o brilho) e a **de jogo** (o tempo de mira, a velocidade, a dispersão, como se obtém em
cada modo). A visual depende só do caminho das armas, já provado; a de jogo depende do tiro (4.2), das animações de
mirar (4.3) e dos modos e da loja (fases dos modos). Proposta, na ordem pedida:

| Etapa | O que entra | Depende de |
|---|---|---|
| 4.1c (agora) | o resto da subfase, sem miras | — |
| 4.1d | a AWP com a luneta real (o modelo), a Nova e a P90 | — |
| **Miras A** (a 4.5 adiantada, logo depois da 4.1d) | os modelos do catálogo (seção 3), os trilhos e os soquetes nas armas, a montagem com as alturas de co-witness, o retículo no vidro, a luneta híbrida com a sombra do ocular, o brilho, a lanterna e o laser visuais; as lunetas de fábrica do Competitivo no mesmo caminho; o comando `mira` e a bancada `arsenal` com as miras | o caminho das armas |
| 4.2 e 4.3 | o tiro e as animações (já com o mirar pela mira montada) | Miras A |
| **Miras B** (com os modos) | os efeitos de jogo de cada peça, a obtenção por modo, a tela de armeiro | 4.2, 4.3, os modos e a loja |
| **Skins** (o motor e o catálogo) | as famílias de técnica, as máscaras, as quatro cores, a semente e as faixas de desgaste sobre as cinco zonas; o catálogo dos quatro tipos; as skins também nos acessórios | Miras A (os acessórios têm zonas) |
| Fase 11 | o desbloqueio (nível, conquistas, escadas de maestria) e a tela de escolha | Skins |

## 2. Princípios

- **Cada mira paga um preço visível.** A lição do Valorant: sem custo claro, os jogadores elegem uma peça "melhor em tudo"
  e nunca mais trocam, e a Riot tirou os acessórios livres por isso ([PlayValorant](https://playvalorant.com/en-us/news/dev/how-the-valorant-arsenal-was-built/)).
  O preço é pago em tempo de mira, velocidade com a mira, brilho da luneta, exposição (o ponto e o feixe do laser, o
  facho da lanterna) ou campo de visão; o entregável da Miras B é uma tabela de custos medida na pista contra a mira de
  ferro.
- **O padrão de spray fica intocado.** Como a luneta da AUG no CS2, uma mira muda só grandezas escalares (o FOV, a
  velocidade, a imprecisão parada, o tempo de zoom), nunca o desenho do recuo (`weapons.vdata` do CS2, no relatório).
  Por isso, na proposta, **ficam fora** as peças que mudam o recuo (quebra-chamas, empunhadura frontal, coronha) e as
  que mudam a economia (carregador estendido) — seção 9, pergunta 4.
- **A ampliação no nome**, como o Battlefield 6 ("1,00x", "4,00x"): o menu de compra lê rápido e nenhuma marca entra.
- **Acessórios são adereços de metal como as armas:** o mesmo pipeline (script Python no Blender, ficha com as medidas
  de foto livre, modelo alto assado no de jogo, níveis de detalhe), as mesmas zonas (`corpo`, `detalhes`, `interno` e a
  nova `vidro`), as skins valendo neles — exceto no retículo, que nenhuma skin toca.
- **O Competitivo não muda.** As lunetas de fábrica são as mesmas em todos os modos, e o que a Miras A constrói para
  elas (o vidro, o retículo gravado, a sombra do ocular) é a base técnica de todas as outras.

## 3. Catálogo (os modos casuais)

Medidas pelas peças reais de referência (as marcas só no relatório, nunca no jogo); ganhos e preços como ponto de
partida, extrapolados do PUBG e do CS2.

| Peça (nome no jogo) | Ampliação | Referência de medida (C × L × A, peso) | Armas | Ganha | Paga |
|---|---|---|---|---|---|
| Ponto 1x (reflex compacta) | 1x, ponto de 2 MOA | 46 × 30 × 25 mm, 33 g (pistola); micro de fuzil 79 × 56 × 69 mm com o espaçador de 39 mm | pistolas, SMGs, fuzis, espingardas | a mira limpa; o mirar ~10–20 % mais rápido que as lunetas | só 1x; a janela pequena |
| Anel 1x (holográfica) | 1x, anel de 68 MOA + ponto de 1 MOA | 96,5 × 58,4 × 73,7 mm, 318 g | SMGs, fuzis, espingardas | o anel fácil de achar em movimento; aceita o magnificador | a carcaça tapa a periferia |
| Lupa 3x (magnificador basculante) | 1x ↔ 3x | 102 × 55,9 × 73,7 mm, 300 g | atrás do Ponto 1x ou do Anel 1x | a média distância quando quiser | a troca anima e impede mirar |
| Luneta 2x | 2x | — (a família compacta) | fuzis, SMGs | o meio-termo de alcance | perde o 1x |
| Luneta 4x (de combate, chevron) | 4x | 151,9 × 50,8 × 58,4 mm, 422 g; alívio de olho de 38 mm | fuzis | o alcance; um Ponto 1x opcional em cima | o mirar ~10–20 % mais lento |
| Luneta 1–6x (LPVO) | 1x / 3x / 6x numa tecla | 222 mm, tubo de 30 mm, 490 g (a 1–8x de referência) | fuzis | a versatilidade | a mais pesada de fuzil, com o mirar de luneta mesmo em 1x |
| Luneta 8x (de precisão) | 8x | 420 mm, objetiva de 62 mm, 1.065 g (a 5–25x56 de referência) | só snipers, no lugar da de fábrica | o mirar mais rápido que a de fábrica | menos ampliação que o 2º zoom da AWP; o brilho |
| Laser | — | módulo de 117 × 71 × 41 mm, 213 g | trilho ou sob o cano | ~20–30 % menos dispersão do quadril | o ponto e o feixe visíveis aos outros |
| Lanterna | — | 141 mm, aro de 28,6 mm, 146 g (fuzil); 86 × 37 × 37 mm, 123 g (pistola) | trilho lateral | ilumina e ofusca | denuncia a posição |
| Noturna e térmica | 1x a 4x | — | **só nas Ondas e em mapas escuros** | ver no escuro e através da fumaça (a térmica) | a imagem lenta e granulada, o vidro opaco, o mirar lento |

A térmica é a peça mais corrigida do gênero (o Warzone baixou o alcance em 2020, proibiu seis no ranqueado em 2023 e
todas no Resurgence ranqueado em 2024; o PUBG a prendeu nos pacotes aéreos; o Tarkov limita a ~230 m e a cinco por
incursão — fontes no relatório, seção 1). Nas Ondas, contra os inimigos de massinha do host, o problema de justiça some.

## 4. Montagem nas armas

- **Trilho Picatinny (MIL-STD-1913):** 21,2 mm de topo, fendas de 5,23 mm a cada 10,01 mm, 3,00 mm de fundo, flancos a
  45°; o soquete de cada peça encaixa numa fenda (a peça de jogo não escorrega entre fendas).
- **Alturas no AR:** o centro óptico a 35,8 mm do trilho (co-witness absoluto) ou 39,0 mm (1/3 de baixo); as LPVOs na
  base em balanço de 1,93 pol. A mira de ferro aparece dentro do Ponto 1x no co-witness, como na foto de QRD14.
- **M4A4 (a M4A1 da 4.1c):** o receptor já é plano com o trilho embaixo da alça de transporte. Com uma mira, a alça
  sai e entra uma mira traseira rebatível (a configuração real das M4A1 com óptica) — seção 9, pergunta 3. O laser às
  12 h do guarda-mão de trilhos (onde o módulo real foi feito para não tapar a mira) e a lanterna às 3 ou às 9 h.
- **AK-47 tipo 3:** não tem trilho nenhum. O trilho lateral em cauda de andorinha só existe nas variantes "N" e na série
  100; a alternativa moderna é o tubo de gás com trilho (174,6 mm, 16 fendas, a montagem mais baixa do AK) — seção 9,
  pergunta 1.
- **Glock-18 de 3ª geração:** o trilho de uma fenda embaixo da armação recebe a lanterna ou o laser de pistola; o
  ferrolho não tem o corte para o ponto (só certas de 4ª e 5ª geração têm): a Ponto 1x pede uma placa no encaixe da mira
  traseira ou o ferrolho fresado — seção 9, pergunta 2.
- **Baioneta M9:** nenhum acessório.
- **Soquetes novos** (no registro das classes, como os de hoje): `trilho_cima`, `trilho_direito`, `trilho_esquerdo`,
  `trilho_baixo` (a origem na primeira fenda, +X para a boca, o passo das fendas no `extras`), e o `olho` da mira (o
  ponto do alívio de olho, que o viewmodel alinha com a câmera ao mirar).

## 5. No jogo — a técnica

- **O retículo no vidro**, calculado no fragmento a partir da direção olho → fragmento em relação ao eixo da mira
  (projeção gnomônica: u = d·T / d·N, v = d·B / d·N), sem textura presa na UV e sem render-to-texture. Um ponto real de
  2 MOA dá 0,47 px em 1080p na câmera do projeto: o shader garante 1,5–2 px de raio mínimo, antisserrilhado por
  `fwidth` e a intensidade acima do limiar do bloom. O vidro é desenhado pela câmera do viewmodel e o alvo pela do mundo
  (FOVs diferentes): o ponto é calculado no espaço de tela com a projeção da câmera do mundo e o vidro serve de máscara.
  O vidro tingido (azul nas reflex, âmbar nas de gama alta) e o reflexo fraco do estúdio.
- **As lunetas, no modo híbrido** (o do Call of Duty): o zoom em tela cheia com a luneta 3D, a máscara do ocular e o
  borrão fora da lente; o **picture-in-picture** como "alta qualidade" só no desktop (no Sandstorm e no Tarkov ele custa
  20 a 40 FPS; a meta é 60 FPS em GPU integrada e 30 no celular). A sombra do ocular encolhe quando o olho sai do alívio
  e escorrega com o desalinhamento: os crescentes pretos no balanço da arma. Retículo de primeiro plano focal cresce com
  o zoom na LPVO.
- **A ampliação sobre um FOV de referência fixo** (como os FOVs fixos do CS): uma 4x mostra o mesmo cone de mundo para
  todos, qualquer que seja o FOV escolhido; a sensibilidade com zoom no casamento de 0 % como padrão (a memória muscular
  perto da mira), com o coeficiente escolhível e um multiplicador por peça, iguais no mouse, no analógico e no toque —
  seção 9, pergunta 5. Na tabela do relatório (FOV de 100° em 16:9): 2x → 37,06° de FOV vertical, 4x → 19,03°, 8x → 9,58°.
- **O brilho da luneta:** um sprite aditivo na objetiva, do tamanho em pixels (visível de longe), que acende num cone de
  10° da linha de tiro, só mirando e só acima de 4x (a regra do Battlefield 4); a direção e o estado de mira já vão na
  rede para a animação, então custa zero de rede; a oclusão por um raycast BVH a cada poucos quadros.
- **A noturna:** um passe de tela cheia (a luminância baixa multiplicada, o ruído animado, o verde de fósforo ou o branco,
  a máscara do tubo) com o bloom de limiar baixo para os halos das luzes.
- **A térmica não é um filtro de cor:** cada material do set ganha um valor de calor — a massinha dos bonecos e dos
  inimigos quente, o metal das ferramentas frio, o papelão morno sob a luminária — e a cena sem luz passa por uma paleta
  (branco-quente, preto-quente, ferro em brasa); o vidro sai opaco (o infravermelho longo não o atravessa). No three.js
  r186, `scene.overrideMaterial` com `material.allowOverride = false` dá o material térmico com as exceções.
- **O laser:** o feixe (um quad aditivo voltado para a câmera, mais forte perto do emissor) só aparece onde houver
  poeira ou fumaça — a poeira nos feixes de luz do estúdio e a nuvem de algodão da smoke —, e o ponto vem de um raycast
  da boca; no jogador local o feixe nasce no cano do viewmodel e segue no mundo.
- **A lanterna:** uma `SpotLight` com o cookie desenhado em canvas, num pool fixo apagado com `intensity = 0` — ligar e
  desligar com `visible` muda a contagem de luzes na chave dos programas e recompila os shaders.
- **Por plataforma** (a medir com o `gpuTimer.js`): o retículo no vidro em todas; a luneta híbrida no celular e na GPU
  integrada (PiP opcional até 512 px), PiP até 1024 px com MSAA no desktop dedicado; a noturna e a térmica em meia
  resolução no preset Leve; a lanterna com o cookie sem sombra, e a sombra só na lanterna local no desktop.

## 6. Como se obtém em cada modo casual

- **Mata-mata (FFA) e em Times, com a compra livre (o padrão):** um orçamento por arma, como os 100 pontos do Battlefield
  6 e os 15 do Insurgency: cada peça custa pontos (as de maior impacto, mais), e a arma sai montada da loja.
- **Com a "Economia" ligada pelo host:** as peças entram no menu B com preço e se perdem na morte, como as armas
  (inferência pelos preços do CS2: um Ponto 1x por $100–200, uma Luneta 4x por $400–600).
- **Gun Game:** cada degrau da lista vem com um pacote fixo (como os pacotes de fábrica do Battlefield 6).
- **Ondas:** pontos por onda repelida, como o Outpost do Insurgency (+2 por onda), gastos entre as ondas.
- **Competitivo:** nada; só as miras de fábrica.

## 7. Skins — um motor só para os quatro tipos

O projeto já tem a primeira camada: por zona (corpo, guarnição, carregador, detalhes, interno), um acabamento, uma cor
da paleta nomeada e o desgaste, com três skins de exemplo (`src/data/skinsArma.js`). O motor proposto acrescenta, por
zona, uma **família de técnica**, uma **máscara de padrão** (três máscaras nos canais R, G e B, como as do CS2), **até
quatro cores**, uma **semente** (a escala, o deslocamento e a rotação do padrão sorteados em faixas) e a **faixa de
desgaste** de cada skin (a direção de arte do CS: o degradê sobre cromo só de 0,00 a 0,08, a ferrugem de faca só de
0,40 a 1,00).

| Tipo | O que muda | Como se constrói | Custo por skin |
|---|---|---|---|
| Acabamento real | o material de cada zona | os parâmetros físicos (metal, aspereza, anisotropia, iridescência, verniz) e o substrato que o desgaste mostra | quase nenhum |
| Artística estilo CS2 | o padrão e as cores | a família, a máscara, as quatro cores, a semente e a faixa de desgaste | baixo nas procedurais; alto nas ilustradas (uma arte por arma) |
| Temática de estúdio | o tema, com os materiais do ateliê | as mesmas famílias, com os padrões e os materiais do set | médio |
| Troca de modelo | a malha inteira | um modelo novo no mesmo pipeline do Blender, com os mesmos soquetes, zonas e peças móveis | alto, por arma |

- **Acabamentos reais novos** (os do relatório, seção 4): o **titânio anodizado** por interferência (filme de 20 a
  230 nm com IOR ≈ 2,3: palha, roxo, azul profundo, dourado de 2ª ordem, magenta, verde-azulado — a sequência física),
  o **verniz colorido sobre cromo**, o **azul de nitrato**, a **têmpera colorida** (as manchas pretas, azuis e roxas que
  desbotam primeiro nas arestas), o **parkerizado** (cinza-carvão, não oliva), o **damasco** na faca (faixas senoidais
  deformadas por ruído: escada, torção, gota, pena), o **stonewash** e o **jateado** da lâmina. O "anodizado" de hoje
  ficou o alumínio jateado tingido, sem a iridescência (correções da P1 da 4.1c), e o titânio entra como acabamento à
  parte. Três recursos do `MeshPhysicalMaterial` cobrem o catálogo: a anisotropia, a iridescência (IOR até 2,333) e o
  verniz.
- **Artísticas**, com nomes de técnica em português: película d'água (hidrografia), estêncil (spray em projeção
  triplanar), verniz sobre cromo, aerógrafo sobre cromo, têmpera, ilustrada e oficina (pintura livre). As camuflagens
  como famílias de forma, de receita própria: manchas orgânicas (ruído com domínio torcido), pontilhado (Worley),
  estilhaço (Voronoi em métrica de Manhattan), listras e digital (o domínio quantizado), com nomes genéricos ("Floresta 4
  tons", "Pontilhado 5 tons", "Estilhaço", "Lagarto vertical"). Nada copiado de padrões protegidos (MultiCam, A-TACS,
  MARPAT, M90) nem da "rajada" do Exército Brasileiro (o Estatuto dos Militares trata de uniformes, mas a cópia não vale
  o risco): o lagarto vertical é desenho nosso.
- **Temáticas de estúdio** — onde o MASSACRE se diferencia: a porcelana azul e branca (cinco pins de fontes diferentes:
  QKS14, QCW1, QCW3, QCW7, QHD1), a arte de nariz de avião (QCR5, QCR20, QCR25), o giz de cera (QCT3), a massinha de
  criança (QCT2) — o ClayMaterial do projeto como uma camada de "massa por cima do metal", sem modelo novo —, as curvas
  de nível (QCR7, QCR14), a pátina de azinhavre (QCR2) e os materiais do próprio set: o tapete de corte verde com a
  grade, a fita crepe, o papelão ondulado, a folha de exposição (X-sheet) e a película de 35 mm.
- **Troca de modelo** (caneta, lápis, skate, arma de água e as ideias de massinha da 4.1): mantém os soquetes, as zonas e
  as peças móveis da arma base, e também a linha de mira, a posição da boca e o ícone do killfeed — a skin nunca esconde
  que arma o adversário tem na mão.
- **Nomes:** originais, em português. Ficam de fora os do CS (Fade, Doppler, Case Hardened, Crimson Web, Tiger Tooth,
  Marble Fade, Howl, Asiimov e os outros), "StatTrak", "Souvenir" e os das camuflagens de maestria do Call of Duty.
- **Leitura** (o guia de estilo da Valve): as comuns discretas, difíceis de ler à distância; as do topo gritantes,
  reconhecíveis de longe; preto puro e saturação extrema parecem fonte de luz; o albedo de 180 a 250 nos metálicos e de
  55 a 220 nos não metálicos; o desenho importante nunca gasta até o substrato; a skin tem de ficar boa na mão, não só
  de lado na inspeção.
- **Obtenção, sem caixas pagas:** o art. 20 da Lei 15.211/2025 (em vigor desde 17/03/2026) veda caixas de recompensa em
  jogos de acesso provável por crianças e adolescentes; sem conta e com a progressão no IndexedDB, o caminho é o das
  regras do projeto — o desbloqueio por nível e conquista, as escadas de maestria com nomes próprios e as combinações
  livres de acabamento e cor. A semente rara vem com a skin ganha (a assinatura de cada exemplar), nunca vendida como
  chance.
- **Faca:** as famílias metálicas procedurais (o degradê sobre cromo, o marmorizado com fases, a têmpera, o azulamento,
  a pátina forçada, o damasco) servem a qualquer faca futura sem arte nova; as ilustradas ficam para o topo.

## 8. Testes e aceite (resumo; o plano de cada etapa detalha)

- **Miras A:** as fichas das peças (medidas e fotos livres, como as armas); o `construir` de cada peça com a silhueta e
  as medidas-chave; os soquetes de trilho nas armas (posição nas fendas, alturas de co-witness); o retículo no vidro com
  o raio mínimo e o alinhamento com a câmera do mundo (teste da conta do ponto na tela, no Node); a luneta híbrida com a
  sombra do ocular; nenhuma recompilação de shader ao ligar e desligar a lanterna (`renderer.info.programs`); FPS no
  preset Leve.
- **Miras B:** a tabela de custos medida na pista contra a mira de ferro (nenhuma peça melhor em tudo); o spray idêntico
  com e sem cada mira; o Competitivo sem nenhuma peça.
- **Skins:** a função pura skin → parâmetros de material (no Node), a semente reproduzível, as faixas de desgaste, a
  leitura de longe na pista, os nomes fora da lista proibida.

## 9. Perguntas para o usuário (antes da Miras A)

1. **AK-47 com mira:** a placa lateral em cauda de andorinha (de época, deslocada para a esquerda do eixo, mas o tipo 3
   não a tem — seria outra variante) ou o tubo de gás com trilho (moderno, a montagem mais baixa)? Ou a AK fica só com a
   mira de ferro e o laser e a lanterna?
2. **Glock-18 com o Ponto 1x:** a placa no encaixe da mira traseira, o ferrolho fresado, ou a Glock fica só com a
   lanterna e o laser?
3. **M4A4 com mira:** a alça de transporte sai e entra a mira traseira rebatível (a configuração real; recomendado), ou
   a alça fica e só entram as peças de base de alça?
4. **Peças que mudam o recuo ou o carregador** (quebra-chamas, empunhadura frontal, coronha, carregador estendido): fora,
   para manter o spray fixo do CS (recomendado), ou dentro dos casuais?
5. **A ampliação sobre o FOV de referência fixo** (uma 4x igual para todos) e a sensibilidade com zoom no casamento de 0 %
   como padrão (recomendado)?
6. **A noturna e a térmica** só nas Ondas e nos mapas escuros (recomendado), ou também no FFA?
7. **A ordem da seção 1** (a Miras A logo depois da 4.1d, antes da 4.2; a Miras B com os modos; as skins depois da Miras
   A) — ou as miras inteiras só na 4.5, depois do arsenal?

## 10. Riscos e respostas

- **Uma peça dominante nos casuais** → a tabela de custos medida na pista é o entregável da Miras B, e cada peça perde em
  algum eixo; a pior delas sai do catálogo antes de entrar.
- **O PiP pesado** → o híbrido é o padrão em todas as plataformas; o PiP é opção do desktop, medida pelo `gpuTimer.js`.
- **O ponto do retículo sumindo em 720p** → o raio mínimo em pixels e o bloom; o teste da conta no Node.
- **A AK e a Glock sem trilho** → as perguntas 1 e 2 decidem a variante antes de modelar; nada é modelado "no chute".
- **Skins que escondem a arma** → a troca de modelo mantém a silhueta de leitura (a linha de mira, a boca, o ícone), e
  nenhuma skin toca o retículo.
- **Caixas de recompensa** → fora, por lei e pelas regras do projeto; o valor vem da conquista e da expressão.
