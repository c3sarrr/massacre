# 4.1d — Pesquisa da Benelli Nova (pump-action) para o MASSACRE

Data da pesquisa: 2026-10-03. Idioma: português.

Legenda de confiança usada em todo o documento:

- **[P]** fonte primária (Benelli: site da Benelli Itália, site da Benelli USA, manuais oficiais do fabricante).
- **[S]** fonte secundária (varejista, review, wiki).
- **[E]** estimativa minha (derivada de foto ou de raciocínio; diz o método).
- **[?]** não consegui confirmar.

Regras que segui: nenhum arquivo de imagem nem modelo foi baixado por mim para o disco. As fotos foram vistas só como captura de tela no painel de navegador, e a análise de pixels (1 foto) foi feita em memória no navegador. Dois efeitos colaterais das ferramentas, fora do projeto, que você deve saber: o `WebFetch` gravou sozinho um PDF de catálogo (Benelli Bélgica, 35 páginas) e o painel de navegador guarda as capturas de tela, ambos em `C:\Users\T-Gamer\.claude\projects\...\tool-results\`. Nenhuma conta foi criada, nenhuma senha usada.

---

## 0. Achados críticos (leia antes do resto)

1. **995 mm não se confirma.** O comprimento total da Nova Tactical de 18,5" é **39,75" = 1010 mm** [S: Botach] e é o valor que o índice de busca devolve da antiga página da Benelli USA [P, hoje 404, ver 2.1]. 995 mm é 1,5 % menor que 1010 mm, ou seja, fora da tolerância de ±1 % do jogo. Não achei nenhuma fonte com 995 mm.
2. **"Nova" e "Nova 3" são armas diferentes.** A Benelli USA hoje vende a *Nova 3* (câmara de 3", curso da bomba 14 % mais curto, 40,25" de comprimento, 5,9 lb, rail Picatinny na alça traseira). O CS imita a Nova **clássica** (2012). Não use fotos nem medidas da Nova 3. A página clássica `benelliusa.com/shotguns/nova-tactical-pump-action-shotguns` agora dá "Page Not Found".
3. **O Commons só tem 2 fotos de Nova de verdade**, as duas da mesma pessoa e as duas da versão **de caça camuflada com cano longo**, em perspectiva. **Nenhuma Nova Tactical.** O único perfil limpo de uma arma da família é da **Supernova Tactical** (coronha de pistola), que tem o mesmo cano, miras, tubo, tampa e bomba, mas coronha e receptor traseiro diferentes.
4. **O curso total da bomba não é publicado** por ninguém que eu tenha achado. O manual só dá os primeiros ~3 cm. Vai como estimativa (seção 4).
5. **A Nova do CS é a Nova Tactical clássica**: coronha fixa inteiriça (sem pega de pistola), cano de 18,5", miras ghost ring, tubo curto de 4 cartuchos, preta fosca. O jogo diz 8 cartuchos, o modelo mostra 4.

---

## 1. Como a Nova aparece no CS:GO / CS2

### 1.1 O que as wikis dizem

| Fato | Fonte |
|---|---|
| "Benelli Nova is an Italian shotgun. In-game, it holds 8 rounds of 12 gauge." Substitui a Leone 12 Gauge Super (a M3 dos CS antigos). Nome de alfa: "Leone Eclipse". Entidade `weapon_nova`. | [S] Fandom CS: https://counterstrike.fandom.com/wiki/Nova (lido pela API `api.php?action=parse&page=Nova&prop=wikitext`) |
| "Although the Nova in-game has an 8-round magazine capacity, the in-game model depicts it with the standard 4-round tube magazine." | [S] mesma página; e IMFDB https://www.imfdb.org/wiki/Counter-Strike:_Global_Offensive ("even though the model has a standard 4-round tube magazine") |
| IMFDB chama o modelo de **"Benelli Nova Tactical"** e diz que o M3 foi o predecessor. | [S] https://www.imfdb.org/wiki/Counter-Strike:_Global_Offensive ; https://www.imfdb.org/wiki/Benelli_Nova |
| Estampa no lado **esquerdo** do receptor: "[!] BENETTI" e na segunda linha "BENETTI ARMS URBINO MADE IN ITALY" (paródia de "Benelli", Urbino é a sede real). | [S] IMFDB CS:GO (link acima); Fandom CS (menciona só "BENETTI") |
| Estatísticas: US$1050, 9 balins por tiro, 68 tiros/min, 8/32 de munição, recarga cartucho a cartucho pela janela de carga, dá para interromper a recarga e atirar. | [S] Fandom CS e Liquipedia https://liquipedia.net/counterstrike/Nova_(Weapon) (lido pela API de wikitext) |
| Animação de recarga compartilhada com a Sawed-Off; som da bomba reaproveitado do Left 4 Dead 2. | [S] Fandom CS |
| Liquipedia dá "based-on = Benelli Nova" e descreve a arma real (receptor e coronha num bloco só de polímero com aço dentro, barras de ação duplas, cabeça rotativa com ressaltos de trava, aceita até 3½"). | [S] Liquipedia (link acima) |

### 1.2 O que eu li nas imagens do próprio CS (só visto, não baixado)

Fonte: ícone de inventário CS2 https://counterstrike.fandom.com/wiki/File:CS2_Nova_Inventory.png, viewmodel `v_nova.png` e capturas "Idle / Reloading #1" da galeria https://counterstrike.fandom.com/wiki/Nova/Gallery (arquivos `Csgo_nova_1.png`, `Csgo_nova_2.png`). Isto é leitura minha, [E]:

- **Coronha**: fixa, inteiriça, comprida, **sem pega de pistola separada** (a "pega" é o pescoço da própria coronha). Não é a tática com pistola da Supernova.
- **Cano**: curto, classe 18,5". Boca com **massa de mira protegida por duas orelhas** (estilo ghost ring/tática). Na visão do viewmodel por trás aparece a **alça traseira em anel (ghost ring) entre duas asas**, em cima do fim do receptor. Não vi trilho Picatinny.
- **Tubo do carregador**: curto (4 cartuchos), termina a uns 3/4 do comprimento do cano, com **tampa com argola/botão** na ponta; cano sobra na frente da tampa.
- **Bomba (guarda-mão)**: longa, com **nervuras horizontais**; chega perto do receptor.
- **Cor**: preta fosca, "Original". Nenhuma versão camuflada de fábrica; as camuflagens são skins.
- **Não vi**: alça de carregamento longa (tubo de 7), coronha de pistola, rail, lanterna, bandoleira.

**Conclusão do item 1:** o CS imita a **Benelli Nova Tactical, 12 ga, cano 18,5", ghost ring, coronha fixa, tubo curto de 4, preta**. O comprimento exato do cano no modelo do jogo não é dado por nenhuma wiki [?]; visualmente é compatível com 18,5".

### 1.3 Mãos no viewmodel (o que consegui ver)

Pelas capturas da galeria Fandom [E, baixa confiança, vale conferir dentro do jogo]:

- **Idle**: arma diagonal, cano para cima e para a esquerda; **mão de apoio (esquerda, luvada) na bomba**, **mão do gatilho (direita) no pescoço/pega da coronha**.
- **Recarga**: a arma gira (janela de carga, que fica embaixo do receptor, vira para o jogador); a mão de apoio solta a bomba e enfia os cartuchos na janela; a direita segura o pescoço da coronha com o dedão por cima.
- **Bomba**: nenhuma wiki descreve a mão na bomba; o IMFDB só diz que a arma é segurada inclinada ao ejetar cartuchos e nivelada ao sacar/recarregar. [?] para o detalhe fino (polegar para que lado).

---

## 2. A arma real

### 2.1 Qual Nova

Duas gerações. A **clássica** (1999–2001 em diante; o Field & Stream diz "debuted in 2001", mas também "mid-1990s... made for law enforcement originally", então a data varia por fonte) é a do CS. A **Nova 3** é de 2025 e é outra arma.

- Nova Tactical clássica [P]: https://benelli.it/en/arma/nova-tactical — câmara "89 mm SuperMagnum"; cano "Cylindrical slug - Adjustable back sight 47/50/61 cm"; receptor, coronha e bomba em tecnopolímero; coronha "360 mm" (medida do gatilho à soleira, sem desvio); carregador "4 rounds 12/76 mm, 4 rounds 12/70 mm and 3 rounds 12/89 mm, 2-round limiter"; peso "approx. 3,400 g with 47 cm barrel". Texto: "The Nova Tactical model comes standard with the rear sight and the Ghost-Ring sight with a rail that serves as a the base for the scope. The fore-end slides freely over the receiver".
- Nova 3 Tactical [P]: https://benelli.it/en/arma/nova-3-tactical (câmara 76 mm, 2700 g, coronha 360 mm) e https://www.benelliusa.com/shotguns/nova-3-tactical-pump-action-shotguns (40,25", 14 1/8", 5,9 lb, "14% shorter cycling stroke compared to the original Nova"). **Descartar.**

### 2.2 Tabela de medidas (Nova Tactical clássica, 12 ga, 18,5")

| Medida | Valor | Fonte e nível |
|---|---|---|
| Comprimento do cano | **18,5" = 470 mm** (47 cm), liso, cilíndrico fixo | [P] Benelli IT (link acima); [S] Botach https://botach.com/benelli-nova-tactical-12ga-18-5-4-1-pump-action-shotgun-w-ghost-ring-sights/ |
| Comprimento total | **39,75" = 1010 mm** | [S] Botach (mesmo link); [S/P-indireto] página clássica da Benelli USA hoje fora do ar, valor devolvido pelo índice de busca. **995 mm: [?] não achei.** |
| Câmara | **3½" = 89 mm** | [P] Benelli IT ("89 mm SuperMagnum"); manual da Nova Tactical: cartuchos de 70, 76 e 89 mm — https://archive.org/details/benelli-nova-tactical-manual (cópia do PDF do site da Benelli USA) |
| Capacidade do tubo | 4 × 70 mm, 4 × 76 mm, 3 × 89 mm; "4+1" | [P] Benelli IT; [S] Botach |
| Tubo longo opcional | 7+1 (ou kit de extensão de tubo) | [S] https://en.wikipedia.org/wiki/Benelli_Nova ; IMFDB "6-shot tube optional". O manual da Nova Tactical tem a seção "Magazine extension tube" (kit) |
| Comprimento de puxada (LOP) | **14¼" = 362 mm** (EUA); **360 mm** (Itália) | [S] Botach; [P] Benelli IT. Review de uma Nova de caça mediu 13,7" (348 mm): [S] https://www.fieldandstream.com/outdoor-gear/guns/shotguns/benelli-nova-shotgun-review |
| Queda da coronha | pente **1⅜" (35 mm)**, talão **2⅛" (54 mm)** | [P] Benelli USA, linha Nova (página 20 ga), https://www.benelliusa.com/shotguns/nova-pump-action-shotguns: LOP 14-1/4", talão 2-1/8", pente 1-3/8". [S] Botach dá 1¼" / 2¼" (32 / 57 mm) para a Tactical 20051. Conflito de ±3 mm |
| Peso | **~3,4 kg** (Itália); **7,2 lb = 3,27 kg** (EUA) | [P] Benelli IT; [S] Botach |
| Altura | **não publicada** [?]. [E] ≈ 195 a 200 mm do ponto mais baixo (ponta da soleira/pega) ao topo da alça traseira, medido na foto da Supernova Tactical (ver 3.3) | método: foto de 1150 px, arma com ~1080 px de ponta da soleira à boca, escala ~0,935 mm/px ancorada no comprimento total de 1010 mm; altura na foto ≈ 211 px |
| Largura | **não publicada** [?] | uma foto de perfil não dá largura; sem fonte |
| Diâmetro do cano | [?] | [E] ≈ 19,6 mm na boca (21 px × 0,935) na foto da Supernova Tactical |
| Curso da bomba | ver seção 4 | [?] total; primeiros ~3 cm [P] |
| Cano de caça (referência) | 26" → 47,5" (1207 mm) na Nova 20 ga; 28" → 49,5" (1257 mm), 24" compacta → 44,2" na 20 ga | [P] Benelli USA (página acima); [S] Wikipedia dá 45,5" a 49,5" para a família; review do F&S mediu 48½" com cano de 28" |

### 2.3 Peças externas (o que existe e onde)

Tudo isto serve de lista de objetos para o Blender. Fontes: manual da Nova Tactical https://archive.org/details/benelli-nova-tactical-manual, manual da Supernova https://archive.org/details/benelli-supernova-manual, Field & Stream (link acima), Truth About Guns https://www.thetruthaboutguns.com/gun-review-benelli-nova-pump-field-shotgun/, e a foto da Supernova Tactical.

1. **Coronha + receptor num bloco só**: "single piece of polymer molded around a steel cage" [S F&S]; "steel skeletal framework overmolded with rugged, state-of-the-art polymer" [P Benelli USA, página Nova]. A cabeça rotativa do ferrolho trava direto no cano, sem extensão de cano nem receptor de aço [S F&S]. Por isso a coronha da Nova **não troca** por outra, ao contrário da Supernova [S Wikipedia, Mesa Tactical].
2. **Guarda-mato** de polímero, integrado ao bloco.
3. **Trava de segurança**: botão **transversal (cross-bolt) na frente do guarda-mato**. Fica com **anel vermelho visível = pronta para atirar**; empurrada para esconder o anel = trava ligada. [P] manual ("Press the safety button on the trigger guard until its red ring, indicating firing position, is no longer visible"). O F&S reclama que o botão é "tiny" [S].
4. **Botão de liberar a bomba (action release / breech bolt latch)**: alavanca logo **à frente da trava, embaixo do receptor, no lado direito**, que "sweeps upward into the receiver" [S American Hunter, Nova 3 https://www.americanhunter.org/content/hardware-review-benelli-nova-3/; Primer Peak https://www.primerpeak.com/benelli-nova-3-tactical-review-2026/]. Na foto da Supernova Tactical (lado direito) vê-se a alavanca pequena à frente do guarda-mato; o lado esquerdo do receptor é liso [E, foto]. O F&S diz que na Nova clássica é uma peça "stamped" de aparência barata [S]. O manual só diz "Press the breech bolt latch" [P].
5. **Botão de parar o carregador (magazine shell stop / "mag cutoff")**: botão quadrado **embaixo da bomba**, no centro [P manual: "magazine shell stop button on the underside of the forend"]. Funciona assim: aperta a alavanca de liberar, recua a bomba uns 3 cm, empurra o botão para dentro, recua tudo: o cartucho da câmara sai e **nenhum novo sai do tubo** [P manual].
6. **Bomba (forend)**: longa, de polímero, com ranhuras moldadas no lugar de quadriculado ("molded grooves... even in wet conditions") [S TTAG]; **chega até a frente do receptor** [S F&S]; "rattles" (balança) [S F&S].
7. **Tampa do tubo (magazine cap)**: rosqueada na ponta do tubo; segura o cano (manual: "barrel retaining cap", desatarraxa para soltar o cano); tem **um pino/"nipple" na ponta que serve de punção** para empurrar os pinos do grupo do gatilho [P manual: "magazine cap (munito sul davanti di un piolo)"; S F&S].
8. **Janela de ejeção** no **lado direito** do receptor; **janela de carga** embaixo, na frente do guarda-mato [P manual].
9. **Alça de mira traseira** (Tactical): anel ghost ring em cima do receptor, ajustável (parafusos), com asas de proteção; **massa de mira** com asas na boca [P Benelli IT: "rear sight and the Ghost-Ring sight"; manual: regulagem da alça "open sight" e regulagem lateral/vertical da "linha de mira"; S Botach: "ghost-ring sights rather than the open rifle sights found on other Nova models"]. Também existe a Tactical com miras abertas (rifle sights) [S Wikipedia].
10. **Coronha**: soleira de borracha; **a placa da soleira sai sem ferramenta e esconde um compartimento de ferramentas** [P manual, seção "Tool compartment"]. Pino de bandoleira moldado na coronha [S F&S]; as Tactical vêm com "quick-release sling attachment swivels" [P Benelli IT].
11. **Marcas**: "Benelli" e "URBINO · MADE IN ITALY" no lado direito do receptor inferior (visível na foto da Supernova; a Nova igual, [E]).

---

## 3. Fotos do Wikimedia Commons (licença livre)

Método: API do Commons (`list=search` nos nomes e descrições, `list=categorymembers` em `Category:Benelli_Nova`, `Category:Benelli_SuperNova`, `Category:Benelli_pump-action_shotguns`, `Category:Benelli_M3`, `prop=imageinfo&iiprop=url|size|extmetadata`) e também `images` dos artigos da Wikipédia (en, ru, pt) sobre Nova e Supernova. Todos usam só as mesmas imagens.

### 3.1 O universo inteiro de fotos de Nova no Commons

`Category:Benelli Nova` tem **apenas 2 arquivos**: `Benelli nova 003.jpg` e `Benelli nova camo.jpg` (esta é um recorte da primeira). Buscas por "Benelli Nova", "Nova Tactical", "Nova ghost ring", "Nova police/military", "Max-4", "Realtree" não retornam mais nenhuma. Não existe Nova Tactical no Commons.

### 3.2 Tabela de candidatos

Todas as páginas: `https://commons.wikimedia.org/wiki/File:<nome com _>`.

| Arquivo | Autor | Licença | Resolução | Lado | Perfil / fundo | Configuração | mm/px (estim.) | Uso |
|---|---|---|---|---|---|---|---|---|
| `Benelli nova 003.jpg` | Chuckeieio | Domínio público (PD-self) | 1280×960 (2007, Sony DSC-P73) | **Direito** (janela de ejeção visível) | **Não é perfil**: câmera alta e de 3/4, arma deitada num banco, grama e vasos ao fundo | **Nova de caça** 12 ga em camuflagem Realtree Advantage, cano longo 24–28" com massa simples, **sem miras táticas**; coronha fixa original | ~1,1 mm/px, **não confiável** (perspectiva; comprimento total entre 1155 e 1257 mm) | **Única** foto livre da **coronha fixa da Nova** (pente, pescoço, talão, guarda-mato integrado, soleira) |
| `Benelli nova camo.jpg` | recorte de mAyo (mesma foto) | PD | 1024×133 | Direito | Tira recortada, perspectiva | idem | ~1,27 mm/px | redundante |
| **`Benelli-SuperNova-Tactical.jpg`** | Picanox | **CC BY-SA 4.0** | 1150×289 (2020-09-19) | **Direito** (janela de ejeção, alavanca de liberar, botão da trava, anel ghost ring) | **Melhor perfil**: arma deitada no chão de madeira, câmera quase ortogonal, fundo de madeira claro (contraste alto com a arma preta) | **Supernova Tactical 18,5"**, **coronha com pega de pistola**, ghost ring traseiro, massa com asas, tubo curto (4), tampa, bomba longa | **~0,935 mm/px** (±1,5 %; ~1080 px de ponta da soleira à boca; ver 3.3) | Contorno do **cano, mira, tubo, tampa, bomba e receptor dianteiro**. O contorno traseiro (coronha + pega) é de outra arma |
| `ARMS & Hunting 2010 exhibition (331-09) (supernova crop).jpg` (e o original `(331-09).jpg`, 2250×1420, com a MR1) | Vitaly V. Kuzmin | **CC BY-SA 4.0** (VRTS confirmado) | 2243×452 | **Direito** | Perfil limpo de vitrine, fundo de madeira/vermelho, cadeado no guarda-mato | **Supernova** de caça (coronha comfort, cano ~20–24" com massa), **não Tactical** | ~0,5 mm/px [E] | Detalhe de **receptor, janela de ejeção, painel inferior, bomba, tampa** em alta resolução |
| `ARMS & Hunting 2010 exhibition (331-11).jpg` | Vitaly V. Kuzmin | CC BY-SA 4.0 | 2250×1412 | Direito | Parede com 4 Benelli (MR1, Supernova, M3, M4) | Supernova de caça | — | comparação de proporções |
| `Shooting Benelli Super Nova Shotgun.jpg` | Brian Omura (Flickr) | **CC BY 2.0** | 2592×1944 | **Esquerdo** | Atirador em campo, céu limpo, ângulo de 3/4 | Supernova de caça 28" com nervura de ventilação | ~0,6 mm/px (perspectiva) | **Único lado esquerdo** do receptor da família (liso, sem janela, sem alavanca); e referência de **mãos** |
| `Shotgun French Army.jpg` | 2nd Hussar Regiment / French Army | **Licence Ouverte 2.0** (não está na sua lista; é livre com atribuição, estilo CC BY) | 1440×1079 | misto | Grupo atirando em campo | Supernova Tactical (pega de pistola) | — | **Referência de mãos** (mão de apoio na bomba) |
| `US and NATO Allies conduct weapons familiarization (7426987).jpg` | US Army (PFC D. Rodriguez) | Domínio público | 6732×4492 | — | Arma cortada em primeiro plano | Supernova FDE, parcial | — | **sem uso** |

Descartados: `French Army shotgun.jpg` (a descrição diz M4 Super 90); `Shotgun in training US military.jpg` (M4); `Remington 870 Police model` (870); fotos de Flickr achadas pelo Openverse (`Benelli Nova Shotguns` de ILMO JOE, CC BY-NC-SA 2.0; `Cable lock` de btmspox, CC BY-NC 2.0): **licença NC**, fora da sua lista.

### 3.3 Diagnóstico e caminho

- **Não há perfil reto de Nova Tactical livre.** A Nova de perfil existe só na versão de caça, em perspectiva (`003`).
- Por isso, **a meta de "silhueta de lado ≥ 98 %" só é verificável contra foto na metade dianteira** (boca → receptor), usando a Supernova Tactical (Picanox). A metade traseira (coronha fixa, guarda-mato, pescoço) só tem a `003`, com distorção.
- **Caminho proposto (composição):**
  1. Escalar a foto Picanox pela medida oficial: comprimento total **1010 mm** (ponta da soleira à boca, ~1080 px na foto), e conferir com as outras duas cotas oficiais. O teste de consistência que fiz (ver tabela abaixo) fecha nos três: com ~0,935 mm/px, gatilho→boca dá ~642 mm (esperado para a Nova: 1010 − 362 = 648 mm, diferença de 1 %), ponta da soleira→gatilho dá ~367 mm (LOP oficial 362 mm, +1,5 %) e a parte visível do cano à frente do receptor dá ~452 mm (cano oficial 470 mm menos ~18 mm que ficam dentro do receptor). Ou seja, **a metade dianteira da Supernova Tactical tem as mesmas proporções da Nova Tactical**, o que sustenta usar a foto para o cano, miras, tubo, tampa e bomba. [E]
  2. Desenhar a coronha da Nova a partir de cotas **oficiais**: LOP 362 mm, queda no pente 35 mm, no talão 54 mm (seção 2.2), e do contorno da `003` corrigido por homografia usando duas âncoras conhecidas (comprimento gatilho→soleira = 362 mm; cano). Aceitar tolerância maior (±3 a 4 %) nessa região, e dizer isso no relatório de fidelidade.
  3. Usar a foto Kuzmin para a janela de ejeção, painéis e bomba (alta resolução).
  4. Conferir o conjunto contra o ícone do CS2 (só olhar, sem copiar) para garantir que o resultado "parece" a Nova do jogo.
- **Marcos medidos na foto Picanox** (leitura minha com grade sobreposta no navegador; x em pixels da imagem original 1150×289, mm medidos da ponta da soleira com 0,935 mm/px; tolerância ±2 %, [E]; vale para a Supernova Tactical da foto, mas a metade dianteira é a mesma da Nova Tactical):

  | Marco | x (px) | mm da soleira |
  |---|---|---|
  | Ponta da soleira | 24 | 0 |
  | Gatilho (dentro do guarda-mato) | ~417 | ~367 |
  | Alça traseira (bloco do ghost ring, topo do receptor) | ~417–473 | ~367–420 |
  | Janela de ejeção (abertura visível, lado direito) | ~521–607 | ~465–545 (80 mm de comprimento) |
  | Frente do receptor / início da bomba | ~620 | ~557 |
  | Fim da bomba | ~905 | ~824 (bomba com ~265 mm) |
  | Tampa do tubo | ~905–970 | ~824–885 (~61 mm) |
  | Massa de mira com asas | ~1045–1085 | ~955–992 |
  | Boca do cano | ~1104 | ~1010 |
  | Cano que sobra à frente da tampa | ~134 px | ~125 mm |
  | Tubo (frente do receptor até o fim da tampa) | ~350 px | ~327 mm |
  | Diâmetro do cano na boca | 21 px | ~19,6 mm |

- Alternativas se você quiser ≥98 % em toda a arma: (a) uma foto própria ou de conhecido de uma Nova Tactical, de perfil, sobre fundo liso; (b) pedir ao Commons/uma pessoa uma foto livre dedicada; (c) o catálogo da Benelli Bélgica (PDF de 35 páginas) https://www.benelli-guns.be/images/pdf/nova-supernova.pdf tem tabelas técnicas em imagem (não consegui ler sem OCR) — vale abrir à mão para ver se traz o comprimento total em mm e um desenho cotado.
- Nota de licença: as fotos CC BY-SA 4.0 (Picanox, Kuzmin) pedem **atribuição** e **mesma licença** para obras derivadas; um modelo traçado a partir do contorno é discutível como derivado, então **credite os autores nos créditos do jogo**. Fotos PD (Chuckeieio) não pedem nada.

---

## 4. Peças móveis e o movimento real

Fontes: manuais da Nova Tactical e da Supernova no Internet Archive (links na seção 2.3), Field & Stream, Truth About Guns.

**Cadeia da bomba:** a bomba (forend) desliza sobre o tubo do carregador e leva **duas barras de ação ("action bars", "bretelle")** que se encaixam na **guia do ferrolho**. O ferrolho tem a **cabeça rotativa com ressaltos de trava** que gira e trava direto no cano. As "hastes-guia da bomba" correm em trilhos do receptor [P manual de desmontagem].

**Ciclo (para animar):**

1. **Pronta**: bomba toda à frente, ferrolho travado no cano, anel vermelho da trava visível = pode atirar.
2. **Tiro**. Para abrir a bomba numa arma carregada e ainda não disparada é preciso apertar a alavanca de liberar [P manual: "Press the breech bolt latch" ao descarregar]. Que a bomba destrave sozinha depois do disparo é o comportamento geral das pumps, mas o manual não descreve [?]; confirmar em vídeo.
3. **Recuar a bomba**: as barras puxam o ferrolho para trás, a cabeça gira e destrava, o ferrolho **aparece e recua pela janela de ejeção (lado direito)**, o cartucho gasto sai pela janela. O próximo cartucho **cai do tubo para o elevador** ("allowing the first cartridge to drop on the carrier support" [P manual]).
4. **Avançar a bomba**: o elevador sobe (por baixo do ferrolho, dentro do receptor, acima da janela de carga), o ferrolho empurra o cartucho do elevador para a câmara, a cabeça gira e trava.

**Curso:**

- **Primeiros ~3 cm** (para destravar a bomba e permitir apertar o botão de parar o carregador): manual diz "circa 3 cm" (IT), "environ 3 cm" (FR), "etwa 3 cm" (DE), mas a versão em inglês diz "about 2 inches" (5 cm). O mesmo manual se contradiz. [P, conflito]
- **Curso total**: **não publicado** [?]. Sinais: a câmara de 3½" exige "almost an inch more travel" que uma de 2¾" (comentário de review, [S]); a Nova 3 de 3" tem curso **14 % menor** [P Benelli USA]. [E] Para a Nova clássica: **~120–135 mm** (cartucho de 89 mm + folga do elevador e da cabeça). Isto é só ordem de grandeza. Confira no vídeo/animação do CS.
- Comprimento da bomba (peça): [E] ~265 mm medido na foto da Supernova Tactical (tabela da seção 3.3); o F&S diz que a da Nova clássica chega até a frente do receptor.

**Outras peças móveis:**

- **Elevador de cartuchos** (carrier): fica por baixo do ferrolho; sobe e desce a cada ciclo. Aparece na janela de ejeção só como sombra.
- **Trinco/alavanca de fixar cartucho** (cartridge/carrier latch, "leva di fermo cartuccia"): na janela de carga, segura o cartucho empurrado para o tubo [P manual].
- **Gatilho**: gira para trás dentro do guarda-mato.
- **Trava (botão transversal)**: desliza de lado alguns mm; mostra/esconde o anel vermelho [P manual].
- **Botão de liberar a bomba**: alavanca que se move para cima/entrar no receptor.
- **Botão de parar o carregador**: entra na bomba ao ser apertado (embaixo da bomba).
- **Tampa do tubo**: **não se move no tiro**; rosqueia/desrosqueia (solta o cano, que desliza para a frente).

---

## 5. Acabamentos de fábrica

| Item | Acabamento | Fonte |
|---|---|---|
| Coronha, receptor, bomba (Tactical) | **Tecnopolímero preto fosco** ("Black Synthetic") | [P] https://benelli.it/en/arma/nova-tactical ("Technopolymer"); [P] Benelli USA, linha Nova ("Black Synthetic") |
| Cano (Tactical) | **Fosco / oxidado preto** ("Matte, Blued"; Benelli IT escreve "matte burnished" para a Nova 3) | [P] https://www.benelliusa.com/shotguns/nova-pump-action-shotguns ; https://benelli.it/en/arma/nova-3-tactical |
| Textura da coronha | "Black synthetic stock with grooved surface" (pescoço com ranhuras, não quadriculado) | [S] Botach |
| Textura da bomba | ranhuras moldadas, "aggressive ribbing" | [S] TTAG; no CS: nervuras horizontais |
| Soleira | borracha preta, placa removível | [P] manual |
| Camuflagens da Nova de caça | **Realtree Advantage** (foto PD do Commons), **Realtree MAX-4** (Impact Guns, item 20076 "Nova Pump 12g 26 MAX-4 Camo"), **APG HD** (Able Ammo, item 20048), **Mossy Oak Bottomland** (Benelli USA, hoje) | [S] https://www.impactguns.com/Pump-Shotguns/Benelli-Nova-Pump-12g-26-MAX-4-Camo-650350200768-20076/ ; https://www.ableammo.com/catalog/benelli-nova-pump-shotgun-20048-gauge-chmbr-youth-synthetic-stock-apg-finish-p-101527.html ; https://www.benelliusa.com/shotguns/nova-pump-action-shotguns |
| Tactical alternativas | **Nova Tactical H2O** (níquel eletrolítico) | [S] https://en.wikipedia.org/wiki/Benelli_Nova ; "Nova Tactical Nickel 20090" em varejistas |
| Nova 3 (não usar) | MultiCam Black, anodizado preto | [P] Benelli USA Nova 3 |
| **A que o CS imita** | **Preta fosca, Nova Tactical** (a camuflagem e as demais são skins do jogo) | seção 1 |

"Nova Max-4" existe apenas em versão de **caça** (cano longo); não achei uma "Max-4 Tactical" [?].

---

## 6. A pega real

**Como o atirador segura uma pump (técnica geral, não específica da Nova)**

- **Mão de apoio (esquerda para destro)** na **bomba**, "pushes forward against the dominant hand's rearward pull" (empurra para frente contra a puxada da mão do gatilho) [S Mossberg https://resources.mossberg.com/journal/reduce-recoil-when-shooting-a-tactical-shotgun]. A técnica "push-pull" para bombear. Os dedos abraçam a bomba por baixo e pelo lado; o dedão fica **ao longo do lado/por cima** da bomba [S, resultado de busca de técnica tática; não achei uma fonte única e textual que fixe o dedão]. Na foto livre `Shotgun French Army.jpg` (Supernova Tactical) a mão de apoio está na metade dianteira da bomba, dedos por baixo/lado.
- **Mão do gatilho (direita)** no **pescoço da coronha**, o indicador fora do guarda-mato até o momento de atirar; o **polegar bem enrolado em volta da pega**, **sem "montar" a trava** de segurança [S http://www.positiveshooting.com/GripMain.html ("it must not 'ride' the safety catch")].

**Na Nova**

- **A pega da Nova é o pescoço da própria coronha**, não uma pistola separada. Na versão clássica o pescoço tem uma inclinação moderada e um inchaço de palma bem visível na foto livre `003` [E, leitura minha da foto]; a Supernova Tactical é que tem pega de pistola (a Nova não aceita troca de coronha) [S Wikipedia/Mesa Tactical]. Na Nova 3 o pescoço fica mais vertical com textura "mildly aggressive" [S Primer Peak].
- A trava e a alavanca de liberar ficam **à frente do guarda-mato**, ao alcance do indicador sem soltar a pega [S Primer Peak].
- A bomba **longa** permite pegar curto com a mão de apoio, o que o F&S aponta como vantagem [S F&S].

**Como o CS mostra** (da seção 1.3): mão de apoio na bomba, mão do gatilho no pescoço da coronha; na recarga, a arma gira e a mão de apoio carrega pela janela de baixo. Detalhe fino (polegar, dedos) [?]; conferir dentro do jogo.

---

## 7. Recomendação

### 7.1 Configuração exata a modelar

**Benelli Nova Tactical (geração clássica), 12 ga, câmara 3½" (89 mm), cano liso de 18,5" (470 mm) cilíndrico fixo, miras ghost ring (anel traseiro com asas + massa com asas), coronha fixa inteiriça preta de tecnopolímero (sem pega de pistola, sem rail, sem lanterna), tubo curto de 4 cartuchos com tampa de punção, bomba longa com nervuras, tudo preto fosco.** É o que o CS imita.

Ficha de cotas (para a regra "medidas-chave a ±1 %"):

| Cota | Valor | Nível |
|---|---|---|
| Comprimento total | **1010 mm** (não 995) | [S] — conferir; se tiver prova de 995 mm, avise |
| Comprimento do cano | **470 mm** | [P] |
| Câmara | 89 mm | [P] |
| Comprimento de puxada | 362 mm (Itália 360) | [S]/[P] |
| Queda pente / talão | 35 mm / 54 mm (alternativa 32 / 57) | [P]/[S] |
| Peso | 3,27 a 3,4 kg | [S]/[P] |
| Tubo | 4 cartuchos (3 de 89 mm) | [P] |
| Curso da bomba | 120–135 mm | [E] |
| Altura, largura, diâmetros | medir na foto | [?] |

Atenção: **não há fonte primária para o comprimento total**; o 1010 mm vem de varejista e do índice de busca de uma página fora do ar. Se a fidelidade a ±1 % no comprimento importa, abra o catálogo da Benelli Bélgica (link na seção 3.3) à mão, ou use o cano de 470 mm (primário) como âncora principal.

### 7.2 As 2–3 fotos

1. **`Benelli-SuperNova-Tactical.jpg`** (Picanox, CC BY-SA 4.0, 1150×289, lado direito, ~0,92 mm/px): contorno de cano, miras, tubo, tampa, bomba e receptor dianteiro; janela de ejeção, alavanca de liberar e botão da trava aparecem. A pega de pistola **não** vale para a Nova.
2. **`Benelli nova 003.jpg`** (Chuckeieio, domínio público, 1280×960, lado direito): a **única coronha fixa de Nova**; corrigir a perspectiva com as âncoras LOP 362 mm e o cano. Tolerância dessa região maior que ±1 %.
3. **`ARMS & Hunting 2010 exhibition (331-09) (supernova crop).jpg`** (Kuzmin, CC BY-SA 4.0, 2243×452, lado direito): detalhe de alta resolução do receptor, janela, painel inferior e bomba.
   - Opcional para o lado esquerdo e as mãos: `Shooting Benelli Super Nova Shotgun.jpg` (Brian Omura, CC BY 2.0).

### 7.3 Pendências e riscos

- A meta de silhueta ≥98 % **não é alcançável contra uma Nova Tactical real** só com o Commons; só a metade dianteira tem um bom perfil. Decida: relaxar a meta na coronha, ou conseguir uma foto.
- 995 mm: **provavelmente é outro número** (talvez de outra variante ou medida até a base da massa). Use 1010 mm até prova em contrário.
- Curso da bomba, altura e largura: **estimativas**, sem fonte.
- A posição do polegar na bomba e as mãos do viewmodel: confirmar dentro do jogo.
- Lado esquerdo: só há foto de uma Supernova; a Nova clássica deve ser idêntica no receptor, com a estampa no lado esquerdo (no CS: "BENETTI") [E].

---

## Anexo — o que não consegui acessar

- Fandom, IMFDB (via ferramenta), Benelli USA (via ferramenta), Midwest Gun Works (Cloudflare), Lucky Gunner, Pew Pew Tactical, Gunbuyer, Sportsman's, Bass Pro, Hyatt, Wayback Machine: 403/429/desafio. Contornei com a API de MediaWiki do Fandom, o site da Benelli Itália, a Benelli USA pelo navegador (páginas Nova 3 e Nova 20 ga), Botach, e os PDFs oficiais copiados no Internet Archive.
- A página clássica da Benelli USA (Nova Tactical 12 ga) está fora do ar; valores dela (39,75", 14¼", 7,2 lb, câmara 2¾/3/3½") vêm do índice de busca.
- O catálogo da Benelli Bélgica (nova-supernova.pdf) é imagem; não li.

## Fontes principais (resumo)

- Benelli Itália, Nova Tactical: https://benelli.it/en/arma/nova-tactical
- Benelli Itália, Nova Black: https://benelli.it/en/arma/nova
- Benelli Itália, Nova 3 Tactical: https://benelli.it/en/arma/nova-3-tactical
- Benelli USA, Nova (20 ga): https://www.benelliusa.com/shotguns/nova-pump-action-shotguns
- Benelli USA, Nova 3 Tactical: https://www.benelliusa.com/shotguns/nova-3-tactical-pump-action-shotguns
- Manual Nova Tactical (cópia do PDF oficial): https://archive.org/details/benelli-nova-tactical-manual
- Manual Nova (cópia do PDF oficial): https://archive.org/details/benelli-nova-manual
- Manual Supernova (cópia do PDF oficial): https://archive.org/details/benelli-supernova-manual
- Fandom CS Nova: https://counterstrike.fandom.com/wiki/Nova ; galeria: https://counterstrike.fandom.com/wiki/Nova/Gallery
- Liquipedia: https://liquipedia.net/counterstrike/Nova_(Weapon)
- IMFDB: https://www.imfdb.org/wiki/Counter-Strike:_Global_Offensive ; https://www.imfdb.org/wiki/Benelli_Nova
- Wikipedia: https://en.wikipedia.org/wiki/Benelli_Nova ; https://en.wikipedia.org/wiki/Benelli_Supernova
- Field & Stream: https://www.fieldandstream.com/outdoor-gear/guns/shotguns/benelli-nova-shotgun-review
- Botach (Nova Tactical 20051): https://botach.com/benelli-nova-tactical-12ga-18-5-4-1-pump-action-shotgun-w-ghost-ring-sights/
- Truth About Guns: https://www.thetruthaboutguns.com/gun-review-benelli-nova-pump-field-shotgun/
- Primer Peak (Nova 3): https://www.primerpeak.com/benelli-nova-3-tactical-review-2026/
- American Hunter (Nova 3): https://www.americanhunter.org/content/hardware-review-benelli-nova-3/
- Mossberg (técnica): https://resources.mossberg.com/journal/reduce-recoil-when-shooting-a-tactical-shotgun
- Positive Shooting (pega): http://www.positiveshooting.com/GripMain.html
- Catálogo Benelli Bélgica: https://www.benelli-guns.be/images/pdf/nova-supernova.pdf
- Commons: https://commons.wikimedia.org/wiki/Category:Benelli_Nova ; https://commons.wikimedia.org/wiki/Category:Benelli_SuperNova ; arquivos citados na seção 3
