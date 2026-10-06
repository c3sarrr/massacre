# 4.1d — Pesquisa da AWP (Accuracy International AWM .338 Lapua Magnum)

Pesquisa de 2026-10-03. Tudo abaixo vem de páginas, APIs e PDFs lidos como texto; nenhuma imagem nem modelo foi
baixado para o disco (as fotos foram só olhadas no navegador; as medidas de pixel foram lidas na própria página, com o
canvas do navegador, sem salvar nada). Três PDFs de documento (a brochura da AI, o manual do usuário do AW e o manual
sueco do Psg 90) foram baixados só para extrair o texto e apagados; os textos extraídos ficaram no scratchpad
(`aw_brochure.txt`, `aw_manual.txt`, `psg90_u.txt`). Cada número tem a fonte; o que não deu para confirmar está marcado
**[NÃO CONFIRMADO]** ou **[ESTIMATIVA]** e repetido na seção 8.

## 0. Resumo (o que decide a 4.1d)

1. **A variante já fixada confere com fonte primária:** a brochura da própria Accuracy International dá para o AWM em
   .338 Lapua Magnum: cano de 27" (686 mm), comprimento de **48,5" (1230 mm)**, peso de 15,1 lb (6,9 kg), carregador de
   5 tiros de fileira única. O 1270 mm da infobox da Wikipedia não tem fonte e não bate com a brochura (seção 2.1).
2. **A AWP do CS2/CS:GO é a família AW com a coronha FIXA verde** (buraco do polegar, soleira preta, capa de bochecha
   preta), cano liso e fino, freio cilíndrico, luneta curta e verde, bipé dobrado para a frente, carregador de aço de
   5 tiros. A luneta do jogo tem 25,8 % do comprimento da arma: é a classe da S&B 3–12×50 (342 mm = 27,8 % de 1230), não
   a 5–25×56 (420 mm = 34 %).
3. **Não achei foto livre de perfil limpo de um AWM de coronha fixa.** A melhor foto de perfil é a da L115A3 do
   Ministério da Defesa (OGL v1.0, 3820×1158, fundo branco, lado esquerdo), que é um AWM .338 de coronha dobrável. A
   coronha fixa sai de uma foto da mesma família (Psg 90 do museu do Exército sueco, CC BY 4.0), registrada pelo
   guarda-mato e pelo buraco do polegar, como a 4.1c já fez na M4A4 (contorno composto de três fotos).
4. **Lado direito (ferrolho, alavanca, trava):** a série de fotos "Medicina Lines Family Day" (L115A3, CC BY-SA 4.0,
   6960×4640) tem um perfil direito quase horizontal e um close da ação com a alavanca e a bola do ferrolho.
5. **Não achei** o curso do ferrolho do AWM, a altura e a largura da arma, o verde exato (RAL/Pantone) nem texto
   nenhum sobre como o viewmodel do CS2 posiciona as mãos (seção 6).

---

## 1. Como a AWP aparece no CS2 e no CS:GO

### 1.1 O que as wikis dizem

| Afirmação | Fonte |
|---|---|
| A "Magnum Sniper Rifle" dos CS antigos é baseada na **Arctic Warfare Magnum, calibre .338 Lapua Magnum**; a AWP do **Global Offensive** é "baseada na Arctic Warfare original" (a wiki afirma isso sem citar fonte). | https://counterstrike.fandom.com/wiki/AWP (seção Overview; wikitexto lido por `api.php`) |
| Calibre listado: **.338 Lapua Magnum**; país: Reino Unido; ação de ferrolho. | https://liquipedia.net/counterstrike/AWP (wikitexto lido por `api.php?action=parse`) e a mesma página do Fandom |
| Carregador: **5 tiros** no CS2 e no GO (era 10 nos CS antigos; o patch do GO de **18/11/2022** reduziu de 10 para 5). Reserva: 10 no CS2, 30 no GO. Recarga 3,7 s. | https://counterstrike.fandom.com/wiki/AWP (infobox e Updates) |
| Em 14/08/2025 o CS2 recebeu "animações de saque melhoradas" para AWP, M4A4 e M4A1-S. | mesma página, Updates |
| A AWP do GO "devia ter acabamento todo preto" (trailer de lançamento), mas mudou; com skin danificada o quadro aparece preto, ou seja, o **verde é uma camada de acabamento** sobre quadro preto. | mesma página, Trivia |
| Gravação no cano do GO: "ACUMEN MULTINATIONAL ENGLAND AKA OAKRIDGE TN" (paródia do fabricante). | Fandom (Trivia) e Liquipedia (Trivia) |
| Nos GoldSrc a mira de ferro do cano só existe na AWP alemã (G22); no Source ela some na primeira pessoa e fica na terceira. | Fandom (Trivia) |
| Em todos os jogos o jogador nunca puxa o ferrolho antes de colocar um carregador novo. No CS:S o viewmodel mostra o ferrolho do lado **esquerdo**, enquanto a animação de terceira pessoa o opera do lado direito (as imagens do GO que olhei mostram a bola à direita). | Fandom (Trivia) |
| O nome AWP vem de "Arctic Warfare **Police**", a versão policial do AW (7,62 NATO ou .243, **coronha preta, cano de 24"**). A AWP real **não** é o rifle do jogo: o jogo mistura o nome da AWP com o desenho do AWM. | https://en.wikipedia.org/wiki/Accuracy_International_Arctic_Warfare (seção AWP) |
| "AWP" aparece em muitos jogos de tiro, entre eles CS e Call of Duty. | mesma Wikipedia, "In popular culture" |

### 1.2 O que o modelo mostra (observação direta das imagens da wiki, só olhadas no navegador)

Imagens consultadas (não baixadas): `W_awp_csgo.png` (modelo de mundo, lado esquerdo, 1276×255),
`V_awp_stat_csgo.png` (viewmodel com StatTrak, lado esquerdo, 1338×389), `V_awp_csgo.png` (viewmodel, 769×403),
`V_awp_uid_csgo.png` (popa da coronha), `W_awp_mag_csgo.png` (carregador) e `CS2_AWP_Inventory.png` (ícone do CS2),
todas em https://counterstrike.fandom.com/wiki/AWP/Gallery (URLs pelo `api.php`, `prop=imageinfo`).

| Peça | No jogo (CS:GO; o ícone do CS2 tem o mesmo desenho) | Real mais próximo |
|---|---|---|
| **Coronha** | **Fixa**, uma peça só, sem dobradiça; buraco do polegar redondo e grande; verde-oliva escuro; **soleira preta** alta e curva; **capa de bochecha preta** plana sobre a parte de trás; parafusos e uma etiqueta rebaixada na lateral | AICS fixa do AW/AWM (laterais de polímero verde, capa de bochecha padrão, soleira de borracha) |
| **Cor** | Laterais ≈ `#3c4136` a `#4a4f44` (amostra de pixel no `W_awp_csgo.png`); cano ≈ `#2a2724`; luneta **verde-oliva** nas imagens do mundo e do viewmodel (a amostra de um ponto deu `#454545`, que cai num anel preto) | Laterais "verde" (brochura da AI) / "olive drab" (AICS); ver seção 5 |
| **Cano** | **Liso (sem canelura)**, fino: diâmetro ≈ 1,6 % do comprimento da arma (≈ 20 mm se a arma tem 1230 mm) | Canelado, de aço inox, ≈ 28 mm na saída do guarda-mão (estimativa de foto, seção 2.2) |
| **Cano exposto** | Da frente do guarda-mão à boca (com o freio): ≈ **25,5 %** do comprimento total | Na L115A3 (fotos): ≈ **36–38 %**. O guarda-mão do jogo é mais longo e o cano exposto mais curto que o real (≈ 12 pontos percentuais, uns 150 mm em 1230) |
| **Freio de boca** | Cilindro com fendas, mais grosso que o cano, com um anel/porca atrás | AI "standard" ou "tactical" (a brochura lista os dois); o freio das fotos do AWM é um cilindro com furos e colar |
| **Luneta** | Curta: **25,8 %** do comprimento (324 px de 1255 no `W_awp_csgo.png`); tubo fino com campânula pequena; torre de elevação alta no topo, bloco quadrado na esquerda (paralaxe), torre de deriva na direita; anéis altos de uma base só; **sem tampas** | S&B PM II 3–12×50 (342 mm = 27,8 % de 1230) ou 10×42; **não** a 5–25×56 (420 mm = 34 %) |
| **Trilho** | Placa com trilho no topo da ação sob a base da luneta | Trilho de cauda de andorinha integral de 11 mm (Picatinny opcional) |
| **Bipé** | **Dobrado para a frente** sob o guarda-mão, preso perto da frente do guarda-mão; visível no modelo de mundo e no ícone do CS2 (no viewmodel **não confirmei**; a wiki diz que ele aparece em primeira pessoa nos CS antigos) | Bipé da AI: espigão que entra num soquete sob o guarda-mão, botão de soltar embaixo; as pernas dobram para a frente ou para trás |
| **Monopé / espigão de soleira** | Não aparece | Opcional na AI (espigão rosqueado que sai até 80 mm) |
| **Carregador** | Caixa de aço escuro, quase quadrada, com **duas fendas verticais compridas** (`W_awp_mag_csgo.png`); sai na recarga (o GO faz o carregador cair desde 27/07/2016) | Carregador de aço, fileira única, 5 tiros, peça 2468 |
| **Ferrolho** | Alavanca fina com **bola** do lado **direito** da arma (viewmodel do GO); qual mão a opera na animação **não confirmei** | Alavanca dobrada para trás com bola grande, do lado direito, operada pela mão do gatilho |
| **Proporção** | Comprimento : altura ≈ 5,34 : 1 (1255×235 px no `W_awp_csgo.png`, com a soleira) | — |

Medidas de pixel do `W_awp_csgo.png`: caixa 1255×235 px; luneta de x = 659 a 982 (324 px); diâmetro do cano 20 px; frente do
guarda-mão a 25,5 % da boca. Conferência feita no navegador (canvas), nada gravado.

### 1.3 Onde o jogo se afasta da arma real (o projeto manda seguir a arma real; isto é só para saber o que o jogador reconhece)

- Guarda-mão mais longo e cano exposto mais curto e mais fino (±12 pontos percentuais no comprimento exposto).
- Cano liso, sem canelura; luneta verde; sem tampas, sem torre de paralaxe real legível.
- Soleira e capa de bochecha pretas bem destacadas (no real a soleira é de borracha preta e a capa também é preta; confere).
- O que o jogador reconhece como "a AWP": coronha verde com buraco do polegar redondo, cano longo e fino com freio grosso,
  luneta curta e escura sobre uma base alta, bipé dobrado embaixo, carregador de aço, bola do ferrolho à direita.

---

## 2. A arma real escolhida: Accuracy International AWM em .338 Lapua Magnum

### 2.1 Especificações (fonte primária sempre que existe)

Fonte primária principal: **brochura "AW rifle system" da Accuracy International**, tabela "Choose your weapon" (arquivada
no Wayback em 2012-09-04):
http://web.archive.org/web/20120904141921/http://www.accuracyinternational.com/assets/assets/aw_brochure.pdf
(lida como texto; a brochura é da família AW e inclui as duas linhas magnum).

| Item | AWM .338 Lapua Mag | AWM .300 Win Mag (para contraste) | Fonte |
|---|---|---|---|
| Cano | **27" = 686 mm**, passo 1:11, **6 raias**, **canelado**, com freio de boca | 26" = 660 mm, 1:11, 4 raias, canelado, com freio | brochura da AI |
| Comprimento total | **48,5" = 1230 mm** (a coluna não diz a coronha; pelos 1178 mm do manual do AW com dois espaçadores, é a **coronha fixa com os dois espaçadores**) | 47" = 1200 mm | brochura da AI |
| Peso | **15,1 lb = 6,9 kg** (nota da brochura: "aproximado, com coronha fixa, bipé e carregador vazio"; a nota não fala da luneta) | 14,3 lb = 6,5 kg | brochura da AI |
| Carregador | **5 tiros, fileira única**, peça nº 2468, de aço | 5 tiros, fileira única, peça 0479 | brochura da AI |
| Alcance eficaz | 1600 jardas = 1500 m | 1300 jardas = 1200 m | brochura da AI |
| Rosca do cano na ação | **1,5" = 38 mm** de rosca (o cano é atarraxado na ação; "rigid mount", segundo a brochura) | idem | brochura da AI |
| Ferrolho | Corpo de **0,75" = 20 mm** de diâmetro, aço, com furos de alívio de gás e proteção; **abertura de 60°** (curta); alavanca integral "com bola grande" que fica rente ao lado da coronha, **logo acima do gatilho** | idem | brochura da AI |
| Soleira e espaçadores | Soleira de borracha parafusada + espaçadores de **10 mm (0,4")** e **20 mm (0,8")** | idem | brochura da AI |
| Espigão de soleira | Rosqueado, sai até **80 mm (3,2")** e recolhe rente | idem | brochura da AI |
| Coronha dobrável | Reduz o comprimento em **210 mm (8")** e soma 0,2 kg (0,4 lb); trava dobrada e é solta puxando a soleira; dobradiça com compensação de desgaste | idem | brochura da AI |
| Gatilho | Dois estágios, regulável de **1,5 a 2,0 kg (3,3–4,4 lb)** | idem | brochura da AI |
| Cor das laterais | **Preto, verde ou dark earth** (cano e ação **pretos**) | idem | brochura da AI (configurador) |
| Trilho de luneta | **Cauda de andorinha integral de 11 mm**; Picatinny colado e pinado opcional; trilho(s) de guarda-mão opcional(is) | idem | https://en.wikipedia.org/wiki/Accuracy_International_Arctic_Warfare (Design details) e o configurador da brochura |
| Bochecha | Regulável para a esquerda/direita e em altura; versão de ajuste rápido com mola | idem | brochura da AI |

Divergências que encontrei (não use esses números):

- Wikipedia (infobox do AWM): **1270 mm**, 6,9 kg, 686 mm — o comprimento não bate com a brochura (1230 mm).
  https://en.wikipedia.org/wiki/Accuracy_International_AWM
- Militaryfactory: 1200 mm, 660 mm, 6,5 kg — são os números do .300 Win Mag.
  https://www.militaryfactory.com/smallarms/detail.php?smallarms_id=1034

Britânico, também primário (Exército Britânico, página arquivada de 2013-01-06):
https://web.archive.org/web/20130106203357/http://www.army.mod.uk/equipment/support-weapons/1459.aspx

| L115A3 (AWM .338 com coronha dobrável) | Valor |
|---|---|
| Calibre | 8,59 mm (.338) |
| Peso | 6,8 kg |
| Comprimento | **1300 mm** (coronha dobrável aberta, com soleira; a página não diz se inclui o silenciador; as fotos mostram que **não** inclui) |
| Velocidade de boca | 936 m/s |
| Alimentação | caixa de 5 tiros |
| Luneta | S&B 5–25×56; coronha dobrável; bochecha regulável; silenciador; bipé regulável (diferente do original da AI) |

Outros números de apoio:

- **AW 7,62 (curto), manual do usuário da AI:** "AW 1178 mm (46,4") **com dois espaçadores de soleira**"; "AWP 1120 mm
  (44") com dois espaçadores"; abertura do ferrolho 60°, queda do percussor 6 mm; gatilho regulado em 1,8 kg; cano de
  26" (AW) ou 24" (AWP). http://www.indaginibalistiche.it/utlities/manuali/accuracy_international_aw_sniper_EN.pdf
  Como o AW 26" da brochura dá 1180 mm, **o comprimento da brochura é o da coronha com os dois espaçadores** (30 mm).
- **Psg 90 (AW 7,62 sueco), manual do Exército sueco:** 6,0 kg sem carregador, 6,4 kg com carregador cheio,
  **1190 mm com 30 mm de extensor**, cano de 657 mm. https://web.archive.org/web/20210709184741/https://hemvarnet.se/UserFiles/Utbildningsgrupper/Sodertornsgruppen/filer/SoldR_Psg_90.pdf
- **Cartucho .338 Lapua Magnum** (infobox da Wikipedia): comprimento do estojo **69,20 mm**; comprimento total máximo
  (C.I.P.) **93,50 mm**; diâmetro da base 14,91 mm; da borda 14,93 mm; espessura da borda 1,52 mm; ombro 13,82 mm;
  pescoço 9,46 mm. https://en.wikipedia.org/wiki/.338_Lapua_Magnum
  O carregador do AWM tem **91,5 mm** de comprimento interno, por isso só cabem cartuchos de até 91,44 mm (a carga
  militar de 250 gr); o de 93,5 mm não entra. https://en.wikipedia.org/wiki/Accuracy_International_AWM
- **Produção:** o AWM .338 foi produzido de 1996 a 2013 e substituído pelo AXMC (anúncio de 09/09/2012).
  https://en.wikipedia.org/wiki/Accuracy_International_AWM

### 2.2 Altura, largura, altura da luneta, gatilho (sem fonte primária: estimativas de foto)

Não achei altura nem largura do AWM em fonte da AI nem do Exército. As estimativas abaixo saem da foto da L115A3 do MoD
(escala 0,79 mm/px na versão de 1920 px, ver seção 3) e valem ±5 %:

| Medida | Valor | Como saiu |
|---|---|---|
| Eixo da luneta acima do eixo do cano | **≈ 55 mm** (±4) | eixo do cano a 179,5 px; eixo da luneta (campânula de 62 mm) a ≈ 110 px; diferença de 69,5 px × 0,79 |
| Diâmetro do cano na saída do guarda-mão | **≈ 28 mm** | 35 px × 0,79 |
| Diâmetro do cano perto da boca (antes do silenciador) | **≈ 21 mm** | 26 px × 0,79 |
| Altura da soleira (extremos) | **≈ 130 mm** | 167 px × 0,79 |
| Gatilho ao plano da soleira | **≈ 370–390 mm** (com os dois espaçadores) | MoD ≈ 387 mm; Psg 90 do museu ≈ 370 mm |
| Folga entre a frente do poço do carregador e o espigão do bipé | **≈ 250 mm** (±15 %: lida a olho numa captura reduzida) | 135 px na captura × 2,4 × 0,79 (espaço para a mão de apoio) |
| Largura da arma | **[NÃO CONFIRMADO]** | sem foto de frente ou de cima de qualidade; o manual do AW não dá |

O manual do AW avisa que "a carcaça da objetiva da luneta não pode encostar na ação nem no cano" (mesmo alívio que a
conta acima dá: raio da campânula 31 mm contra eixo a 55 mm e cano de ≈ 14 mm de raio, sobra ≈ 10 mm).

### 2.3 A luneta (Schmidt & Bender PM II)

Fontes de dados: páginas oficiais da Schmidt & Bender.
- 3–12×50 PM II LP: https://www.schmidtundbender.de/en/3-12x50-PM-II-LP-P3L-1cm-cw-DT-ST/644-911-882-96-94A38
- 5–25×56 PM II LP: https://www.schmidtundbender.de/en/5-25x56-PM-II/689-xxx-xxx-xx-xx

| | **3–12×50 PM II LP** | **5–25×56 PM II LP** |
|---|---|---|
| Comprimento (0 dpt) | **342 mm** | **420 mm** |
| Tubo principal | **34 mm** | **34 mm** |
| Diâmetro externo da objetiva | **57 mm** (interno 50) | **62 mm** (interno 56) |
| Diâmetro externo da ocular | **43,1 mm** | **45,8 mm** |
| Peso | 860 g | 1065 g |
| Distância da pupila (eye relief) | 90 mm | 90 mm |
| Paralaxe | 50 m a ∞ | 10 m a ∞ |
| Torres (cada página) | elevação DT/ST (0,1 mrad / 1 cm), giro horário; faixa de elevação 23 mrad | DT27 MTC LT/ST ZC CT (0,1 mrad), giro horário; faixa de elevação 27 mrad |

Que luneta vai com que arma (com fonte):

- **AW 7,62 original (manual da AI):** S&B **6×42, 10×42 e 3–12×50**, com reticle Mil Dot da AI; a luneta de 3–12×50 vai
  no furo de recuo mais traseiro; a luneta e a base são presas por **8** parafusos (figura 10 do manual); tambores de
  elevação e deriva de uma volta; **a paralaxe fica numa terceira torre no lado esquerdo** (50–1000 m e infinito).
  http://www.indaginibalistiche.it/utlities/manuali/accuracy_international_aw_sniper_EN.pdf
- **AWM (Wikipedia, citando a AI):** configuração padrão **5–25×56 FFP MK II**, com variantes 3–12×50 e 4–16×50.
  https://en.wikipedia.org/wiki/Accuracy_International_AWM
- **L115A1 (britânico) e AWM-F dos Países Baixos:** **3–12×50**. L115A3: **5–25×56**
  (Wikipedia AWM; página do Exército Britânico acima).
- **Observação:** os dados da S&B acima são das versões **LP atuais**; as peças dos anos 90 podem diferir em milímetros.
  Não achei a ficha técnica da PM II 3–12×50 original.

Tampas das lentes: o manual da AI manda "conferir que as tampas das lentes estão no lugar, se fornecidas" antes de
desmontar; nas fotos da L115A3 e do AWM não há tampa; capas basculantes são acessório de terceiros. O jogo também não
tem tampas. **[Recomendo não modelar tampa.]**

---

## 3. Fotos de licença livre (Wikimedia Commons)

Todas conferidas pela API do Commons (`prop=imageinfo&iiprop=url|size|extmetadata`). Categorias usadas:
`Category:Accuracy International AWM`, `Category:Accuracy International Arctic Warfare` (e suas subcategorias),
`Category:L115A3 rifle`, `Category:L115 rifle`, `Category:G22 rifle`, `Category:Accuracy International rifles`.
**Lado** = lado da arma que a foto mostra; "boca à esquerda" = a foto mostra o lado **esquerdo** (o da primeira pessoa
no jogo), "boca à direita" = o lado **direito** (o do ferrolho). `mm/px` = comprimento real ÷ pixels da arma, **na
resolução original** do arquivo, e **é estimativa**: confirme com a régua do projeto (`tools/regua.html`).

### 3.1 Para o contorno e a escala

| # | Arquivo e página | Autor / licença | Pixels | Lado | Perfil / fundo | Configuração | mm/px |
|---|---|---|---|---|---|---|---|
| **A** | `File:L115A3 sniper rifle.jpg` https://commons.wikimedia.org/wiki/File:L115A3_sniper_rifle.jpg | Andrew Linnett (MoD), **OGL v1.0**, 2007-11-09 | **3820×1158** | **esquerdo** (boca à esquerda) | **perfil quase ortogonal, fundo branco limpo**; a mais limpa de todas | L115A3: coronha dobrável aberta (dark earth), bochecha regulável, espigão de soleira, S&B 5–25×56, bipé aberto, carregador, **silenciador na boca** (cobre o freio) | **≈ 0,39–0,40** (escala por duas vias: o comprimento de 1300 mm a ≈ 0,397 e o comprimento de 420 mm da luneta a ≈ 0,391); o conjunto com o silenciador mede ≈ 1460 mm |
| **B** | `File:Medicina Lines Family Day 18 October 2024 13.jpg` https://commons.wikimedia.org/wiki/File:Medicina_Lines_Family_Day_18_October_2024_13.jpg | Pangalau, **CC BY-SA 4.0**, 2024-10-18 | **6960×4640** | **direito** (boca à direita) | quase horizontal, mas a coronha está mais perto da câmera que a boca (guinada); fundo de asfalto e grama, com equipamento de visão noturna escondendo o carregador e as pernas do bipé | L115A3 **sem silenciador, com freio**, coronha aberta, dark earth, S&B 5–25×56 | **≈ 0,20** com 1300 mm (a luneta dá ≈ 0,186: 8 % de diferença, então a guinada tira a precisão; serve para detalhes e para registrar, **não** para as medidas-chave) |
| **C** | `File:Psg 90 AM.068399 (1).jpg` https://commons.wikimedia.org/wiki/File:Psg_90_AM.068399_(1).jpg | Armémuseum (Museu do Exército Sueco), **CC BY 4.0** | **1200×455** | **esquerdo** (boca à esquerda) | perfil quase ortogonal, fundo cinza claro neutro, com acessórios embaixo | **Psg 90 (AW 7,62): coronha FIXA** verde, laterais sem dobradiça, sem silenciador, com freio, luneta 10×42, cano de 657 mm, correia e carregadores soltos | **≈ 1,05** (1190 mm ÷ ≈ 1125 px); só serve para a coronha fixa e a cor, não para o comprimento do AWM |

### 3.2 Lado direito e peças de um lado só

| # | Arquivo | Autor / licença | Pixels | O que mostra |
|---|---|---|---|---|
| D | `File:Medicina Lines Family Day 18 October 2024 17.jpg` (mesma pasta de B) | Pangalau, CC BY-SA 4.0 | 6960×4640 | **Close do lado direito da ação**: alavanca do ferrolho com a bola, trilho, base e anéis da S&B, torres da luneta (elevação com tampa, deriva à direita), poço do carregador |
| E | `File:Medicina Lines Family Day 18 October 2024 16.jpg` | idem | 6960×4640 | **Close da coronha, lado direito** (L115A3): dobradiça, bochecha regulável, espigão de soleira, buraco do polegar, soleira |
| F | `File:USMC-19580.jpg` https://commons.wikimedia.org/wiki/File:USMC-19580.jpg | Cpl. R. Logan Kyle, USMC, **domínio público**, 2009-09-22 | 3504×2336 | **Macro da alavanca e da bola do ferrolho** (AWM .338 dos fuzileiros navais holandeses, legenda "Accuracy International .338 Lapua"), torre de elevação lida de trás |
| G | `File:USMC-19560.jpg` | idem, domínio público | 3504×2336 | **Macro do ferrolho aberto** ejetando um estojo .338 (janela de ejeção, corpo do ferrolho, base da luneta) |
| H | `File:USMC-19456.jpg` | idem, domínio público | 3504×2336 | AWM de fuzileiro holandês deitado com bipé, lado direito, mão do gatilho no punho |
| I | `File:AW G22 Arctic 7.62mm Sniper Rifle.jpg` https://commons.wikimedia.org/wiki/File:AW_G22_Arctic_7.62mm_Sniper_Rifle.jpg | Luhai Wong, **CC BY-SA 2.0** | 3888×2592 | Close traseiro-direito de um AW/G22 de coronha dobrável em exposição (o título diz "G22 Arctic 7.62mm"): **bola do ferrolho**, bochecha, buraco do polegar, soleira |
| J | `File:Arctic Warfare Police Model.jpg` https://commons.wikimedia.org/wiki/File:Arctic_Warfare_Police_Model.jpg | MaXwell (de.wikipedia), **CC BY-SA 3.0** | 800×600 | AWP real de **coronha fixa verde** vista de trás-direita: soleira quadriculada, bola do ferrolho |
| K | `File:G22 ohne Schalldaempfer noBG.png` https://commons.wikimedia.org/wiki/File:G22_ohne_Schalldaempfer_noBG.png | Sonaz, **CC BY-SA 4.0** | 1171×498 | **Lado direito, quase perfil**, fundo transparente (G22 = AWM-F .300 Win Mag, luneta Zeiss, coronha estendida, **carregador fora e ferrolho recuado ou ausente**; o carregador solto aparece de lado) |
| L | `File:Bundeswehr-Technik 01 (RaBoe).jpg` | Ra Boe, CC BY-SA 3.0 | 800×260 | G22 de lado direito com silenciador, baixa resolução |

### 3.3 Para o aspecto geral e a cor

| # | Arquivo | Autor / licença | Pixels | Uso |
|---|---|---|---|---|
| M | `File:AWM-338-white.jpg` https://commons.wikimedia.org/wiki/File:AWM-338-white.jpg | Vitaly V. Kuzmin / MathKnight, **CC BY-SA 4.0** | 1998×810 | **A imagem da infobox do AWM na Wikipedia**: AWM-F verde, trilho de guarda-mão, freio grande de furos com colar, S&B de campânula longa, bipé aberto, fundo branco. **Visão 3/4 com perspectiva, não serve para medir**; serve de reconhecimento e da cor das laterais |
| N | `File:Accuracy International AW .338 LM 4thNovSniperCompetition21.jpg` | Vitaly V. Kuzmin, CC BY-SA 4.0 | 2248×1451 | Original de M: duas AWM-F num campeonato russo, lado direito oblíquo |
| O | `File:AI AWSM .338 Lap. Mag. Dutch ISAF sniper team.jpg` | Francis Flinch, **domínio público** | 959×682 | AWM .338 camuflado (pouco útil) |

### 3.4 Poses e pega (Ministério da Defesa britânico, OGL v1.0, e domínio público)

| Arquivo | Autor / licença | Pixels | O que mostra |
|---|---|---|---|
| `File:Sniper with L115 A3 Rifle MOD 45150348.jpg` | Cpl Rupert Frere RLC, **OGL v1.0**, 2009-06-12 | 4998×3132 | **Silhueta de franco-atirador sentado**: mão do gatilho no punho, **mão de apoio embaixo do guarda-mão, perto do espigão do bipé**; AWM .338 L115A3 |
| `File:Sniper with L115A3 Rifle MOD 45150232.jpg` | Cpl Russ Nolan RLC, OGL v1.0, 2009-04-02 | 3312×1722 | Mão do gatilho no punho (dedo no guarda-mato), rifle num tripé |
| `File:Sniper Aims L115A3 Rifle MOD 45151384.jpg` | Maj Paul Smyth, OGL v1.0, 2010-01-11 | 3460×2077 | Deitado com bipé: mão de apoio sob a soleira, mão do gatilho no punho |
| `File:British Army Sniper with L115A3 Rifle Deploys on a Mission in Afghanistan MOD 45153555.jpg` | Sgt Martin Downs RAF, OGL v1.0, 2010-12-13 | 2848×4288 | Arma vertical presa pela correia (carregada) |
| `File:USMC-19456.jpg`, `File:USMC-19560.jpg`, `File:USMC-19580.jpg` | Cpl. R. Logan Kyle, domínio público | 3504×2336 | Fuzileiros holandeses com AWM .338: tiro deitado, ejeção, posição da bochecha |

### 3.5 Outras que olhei e descartei (e por quê)

- `Accuracy International Arctic Warfare - Psg 90 G24.png` (CC BY-SA 4.0, **650×180**): a foto que o `refs/awp.json` atual usa;
  a resolução é de ≈ 1,9 mm/px, grossa demais para ±1 %.
- `Accuracy AW Ejército Español.JPG` (CC BY-SA 3.0, 3448×1692): arma sobre rede camuflada, fundo sujo, folhagem.
- `Hanse Sail 2009 - Scharfschützengewehr G22.jpg` (CC BY-SA 2.0, 3456×2304): G22 sobre mesa, lado direito inclinado, gente em volta.
- `G22 mit NSV80.jpg` (CC BY-SA 2.0 de, 1278×467): escura, visor noturno encobrindo a luneta.
- `BWEHR Scharfschützengewehr 3.jpg` (CC BY-SA 4.0, 2080×4160): vista de cima da boca de um G22; útil só para o **freio de boca**.
- `Wehrtechnische Sammlung der Bundeswehr (25765829448).jpg` (CC BY 2.0): vitrine com reflexo.
- Pangalau 12, 15 e 26 (lado esquerdo da mesma L115A3, em tripé ou sobre mesa): têm o **silenciador** ou são oblíquas; 14 é
  3/4 direita; 18 só tem visores noturnos e um carregador solto.

### 3.6 Cuidados com a escala

1. Em A, a conta pela luneta e a conta pelo comprimento diferem só 1,5 %; as duas dependem de **1300 mm** (MoD) serem
   de fato a distância entre a soleira e a boca do freio na pose da foto, que tem as bochechas e espaçadores dela.
2. Em B a diferença entre as duas contas é de 8 %, o que mostra guinada da arma: use B para registrar detalhes sobre A,
   não para tirar medidas.
3. O projeto já aceita contorno composto e foto espelhada (`refs/m4a4.json`: "composto de três fotos pela régua" e
   `espelhada`), então A (esquerdo) pode ser espelhada para o lado direito e C emendada na coronha.
4. **Não escale a foto A para 1230 mm.** A é uma L115A3 de 1300 mm (coronha dobrável aberta, com a soleira); a escala
   vem do mm/px, e é a emenda com a coronha fixa (C) que tem de fechar os 1230 mm do AWM. A diferença de 70 mm entre a
   L115A3 e o AWM de brochura (coronha fixa com dois espaçadores) não está explicada em nenhuma fonte que achei: pode ser
   a dobradiça, o comprimento da coronha, o freio ou os espaçadores. Confira com a régua antes de cortar.
5. A parte da arma que **muda de uma coronha para outra** é só a de trás da dobradiça; o resto (ação, poço do carregador,
   guarda-mão, buraco do polegar, guarda-mato, punho) é o mesmo chassi AICS.

---

## 4. Peças móveis e o movimento real

| Peça | Como é e como se move | Fonte |
|---|---|---|
| **Ferrolho** | Giro de **60°** para abrir (a alavanca sobe para o alto), depois recuo em linha reta até encostar no batente; arma o percussor ao abrir ("cocks on opening"); percussor sai da parte de trás do suporte quando está armado (indicador de armado). Corpo de **20 mm**. **Fecha** empurrando para a frente e baixando a alavanca; só alimenta se o ferrolho recuar até o fim. O manual manda sempre cumprir o ciclo completo. Quedas do percussor: **6 mm**. | brochura da AI; manual do AW (seções 2C, 2D, Safe Handling); https://en.wikipedia.org/wiki/Accuracy_International_Arctic_Warfare |
| **Trancamento** | Manual do AW e manual sueco: **3 ressaltos** na frente e 1 ressalto de emergência atrás. A Wikipedia fala em 6 ressaltos (duas fileiras de três) sem citar fonte primária. Para o AWM **[NÃO CONFIRMADO]** | manual do AW; manual do Psg 90 ("tre låsklackar"); Wikipedia |
| **Curso do ferrolho (recuo)** | **[NÃO CONFIRMADO]**: a AI não publica. **[ESTIMATIVA]**: **≈ 125–135 mm** para o AWM .338 (o AT-X de ação curta tem 110 mm e o cartucho do AWM é ≈ 20 mm mais longo que o 7,62 NATO) | AT-X: https://www.gunmart.net/gun-reviews/firearms/rifles/accuracy-international-at-x ("Bolt travel is 110mm"); cartucho: Wikipedia |
| **Alavanca do ferrolho** | Dobrada **para trás**, com bola grande, "rente ao lado da coronha, acima do gatilho"; do lado **direito**; larga para facilitar com luvas grossas. (A bola do AT-X mede 24 mm; a do AWM **[NÃO CONFIRMADO]**; nas fotos F e D parece parecida) | brochura da AI; Wikipedia AW ("thumb-hole, bolt handle, magazine release and trigger guard enlarged"); gunmart (AT-X) |
| **Retém do ferrolho** | Botão/lingueta no **lado esquerdo** da ação; aperta com o polegar esquerdo para tirar o ferrolho | manual do AW (A3 e J5) |
| **Trava de segurança** | **3 posições**, alavanca no escudo (shroud) do ferrolho, atrás da ação (o lado é o direito nas fotos que vi; texto que o diga **[NÃO CONFIRMADO]**): **frente = FOGO**; **meio = "primeira trava"** (percussor travado, ferrolho **livre** para descarregar); **trás = "segunda trava"** (percussor travado e ferrolho **travado fechado**). O manual inglês dá a trava toda aplicada a "cerca de 110° da posição de fogo". Só trabalha com a arma **armada**. A trava tem marca branca/vermelha visível. | manual do AW (Safety features); manual do Psg 90 (posição 1 aponta para a frente, 2 "rakt ut", 3 para trás); Wikipedia AW (Safety) |
| **Gatilho** | Dois estágios, 1,5–2,0 kg, aro do guarda-mato **largo** (luvas de Ártico); o conjunto sai desparafusando 2 parafusos | brochura da AI; Wikipedia AW |
| **Carregador (como sai)** | Aperta o **retém na frente do guarda-mato com o polegar direito** e puxa com os dedos da mão direita; **entra por baixo**, empurrando até o retém travar no ressalto (estalo audível); aço, fileira única, 5 tiros; a placa de fundo tem abas salientes para pegar com luva grossa | manual do AW (A4, 2E); Wikipedia AW |
| **Coronha dobrável (AWM-F)** | Dobra para o lado da ação; trava dobrada; solta puxando a soleira; **−210 mm**, **+0,2 kg**. Lado da dobra **[NÃO CONFIRMADO]**. Não se aplica à AWP do jogo (coronha fixa) | brochura da AI |
| **Bipé** | Espigão no soquete sob o guarda-mão, **botão de soltar embaixo do guarda-mão**; pernas dobram para a frente ou para trás; pés telescópicos; **10° de inclinação** para cada lado; a AI aceita adaptador de bipé Harris no ponto de correia da frente | manual do AW (seção 4); brochura da AI |
| **Bochecha / soleira** | Bochecha regulável para os lados e em altura; soleira com espaçadores de 10 e 20 mm; espigão de soleira até 80 mm | brochura da AI |
| **Luneta (torres)** | Elevação no topo (tambor de uma volta, escala de alcance acima da escala de cliques), deriva na direita, paralaxe numa terceira torre na **esquerda**; 8 parafusos nas braçadeiras | manual do AW (seção 3); S&B |
| **Cápsula** | Sai pela janela do **lado direito/alto** e cai à direita; no jogo o carregador cai na recarga (patch do GO de 27/07/2016) | USMC-19560 (macro); Fandom |

---

## 5. Acabamentos de fábrica

| Peça | Real | No jogo (observado) | Recomendação |
|---|---|---|---|
| **Laterais da coronha** | Polímero (náilon reforçado) **verde**, dark earth ou preto; a AICS chama de "olive drab". **Nenhum RAL/Pantone encontrado [NÃO CONFIRMADO]** (brochura da AI; Wikipedia AICS; EuroOptic) | verde-oliva escuro `#3c4136`–`#4a4f44` | amostras de foto: museu do Psg 90 `#646042` a `#7d7a61` (luz de estúdio, verde-oliva amarelado); AWM-338-white `#4b504e`–`#676b6e` (verde-acinzentado). Sugiro albedo sRGB ≈ `#585a3f` (±), mais claro que o jogo e mais escuro que o museu; decide na ficha do material |
| **Chassi de alumínio** (espinha da ação e do guarda-mão) | Alumínio, preto nas fotos (o acabamento exato, anodizado ou pintado, **[NÃO CONFIRMADO]**); visível em cima e embaixo do guarda-mão | preto sob o verde (visível nas skins gastas) | preto fosco |
| **Ação** | Aço carbono forjado, **preto** ("barris e ações são pretos", brochura) | cinza-escuro `#4a4f44` na amostra do receptor | preto fosfatizado/oxidado |
| **Cano** | Aço inox canelado, acabamento **preto** | liso, `#2a2724` | preto fosco/oxidado, com as caneluras |
| **Freio de boca** | Aço preto; uma das duas versões (standard ou tactical) | cilindro grosso com colar | preto, fosfatizado |
| **Luneta** | Alumínio anodizado **preto fosco** (S&B padrão; a S&B também faz variações de cor, por exemplo RAL 8000 areia: fonte secundária de revenda) | verde-oliva nas imagens do viewmodel | preto fosco (real); a decisão é sua (seção 7) |
| **Soleira e capa de bochecha** | Borracha/polímero preto; soleira quadriculada | preto, curva | preto, com o quadriculado (foto J) |
| **Bola do ferrolho** | Aço preto ou polimérico escuro | metálica | preto fosco |
| **Carregador** | Aço (corrosão resistida/escurecido) | aço escuro com 2 fendas | aço escurecido |
| **Bipé** | Alumínio e aço pretos | preto | preto fosco |

---

## 6. A pega real e a do jogo

### 6.1 Pega real (fontes)

- **Mão do gatilho (direita):** na região estreita do **punho** atrás do guarda-mato (o "pescoço" entre o guarda-mato e o
  buraco). O buraco do polegar da AICS atravessa a coronha de um lado a outro; segundo resultados de busca (fóruns
  SnipersHide e Long Range Hunting e a revisão da TTAG; **as páginas não foram abertas**), muita gente passa o polegar por
  ele e outros apoiam a mão ao lado dele, sem entrar, principalmente deitados; o punho foi desenhado para o pulso reto,
  com o gatilho em linha com o antebraço. Primário: o buraco do polegar, o guarda-mato e o ferrolho do AW foram
  aumentados para luvas de Ártico (Wikipedia AW, "Design evolution").
- **Mão do gatilho no ciclo:** o manual do AW manda **ficar na posição de mira durante o ciclo**, com o polegar direito
  sobre a ação ou o escudo do ferrolho e os dedos da direita segurando a alavanca; os dedos vêm em direção ao polegar para
  soltar o estojo, depois puxam o ferrolho até o fim e o empurram de volta. A mão **larga o punho** para isso; a arma
  continua na espádua. (manual do AW, seção 2D, "Firing and operating the bolt"; Fr. Frog's, https://www.frfrogspad.com/bolt.htm:
  "a mão direita larga o punho e pega a alavanca com o polegar por cima".)
- **Mão de apoio (esquerda):**
  - **Deitado (doutrina do manual da AI):** a mão esquerda segura a **abertura da coronha, na frente da soleira e embaixo
    da bochecha**, com a mão apoiada no chão ou num saco de areia (manual do AW, seção 2H, passo H1).
  - **Sentado, de joelhos ou de pé:** nas fotos do Exército Britânico (`MOD 45150348`) a mão esquerda **sustenta o
    guarda-mão por baixo, perto do espigão do bipé**, o antebraço sob a arma. Para posição em pé sem apoio, a técnica geral é
    "embalar" o guarda-mão na palma, com os dedos relaxados (Art of the Rifle, resultado de busca; o site tem certificado
    inválido e não foi aberto).
  - Nada na doutrina da AI coloca a mão esquerda "em volta" da coronha de trás; a coronha de trás é do ombro, e o apoio
    de trás é a mão do deitado.
- **Espaço para a mão de apoio:** na L115A3 há ≈ 250 mm de guarda-mão liso entre a frente do poço do carregador e o
  espigão do bipé (seção 2.2); o fundo do guarda-mão é plano e estreito.

### 6.2 Como o CS mostra as mãos (o que deu para confirmar)

- **[NÃO CONFIRMADO]** Nenhuma fonte de texto descreve a posição das mãos no viewmodel da AWP do CS2. Tentei Fandom,
  Liquipedia, Steam e o YouTube; os vídeos que achei eram de baixa resolução, com anúncio antes, e não consegui
  extrair um quadro limpo.
- O que as imagens do viewmodel do GO na wiki (`V_awp_stat_csgo.png`, lado esquerdo) deixam ver: a **mão de apoio
  está embaixo e na frente da ação, junto do poço do carregador**, com a manga azul entrando por baixo do lado esquerdo; a
  **mão do gatilho está no punho**, com a luva ocupando a região do buraco do polegar (não deu para saber se o polegar
  passa pelo buraco ou se a mão fica ao lado). O ferrolho (haste fina com bola) está do lado **direito**.
- O desenho do projeto já diz "a mão de apoio **fica sob o guarda-mão na AWP**"
  (`docs/superpowers/specs/2026-09-26-armas-realistas-design.md`, seção 7.3) e a regra da mão da frente do CLAUDE.md
  (polegar reto e deitado no lado esquerdo, quatro dedos abraçando por baixo até o lado direito) cabe nesse apoio: o
  guarda-mão do AW é estreito e plano embaixo.

---

## 7. Recomendação final

### 7.1 Configuração a modelar

**AWM (Accuracy International) em .338 Lapua Magnum, coronha fixa, laterais verdes, 1230 mm:**

- **Comprimento total 1230 mm**, com a soleira e os **dois espaçadores (10 + 20 mm)**, como na brochura e no manual.
- **Cano de aço inox canelado, 686 mm, passo 1:11, 6 raias**, pintado de preto, com a rosca de 38 mm na ação e o **freio
  de boca** cilíndrico de furos com colar (o das fotos B e M, que é o que o jogo lembra); **sem silenciador**.
- **Ação preta de aço**, **trilho integral de cauda de andorinha de 11 mm** (e uma base de luneta de uma peça, como na AI).
- **Coronha AICS fixa**, sem dobradiça: laterais verde-oliva, buraco do polegar, **capa de bochecha preta**, **soleira
  preta quadriculada**, pontos de correia de cada lado, sem espigão de soleira (o jogo não tem).
- **Luneta S&B PM II 3–12×50** (342 mm, tubo de 34 mm, objetiva de 57 mm, ocular de 43,1 mm), **preta fosca**, torre de
  elevação no topo, deriva à direita, paralaxe à esquerda, sem tampas. Motivo: é a classe da luneta do jogo (25,8 % do
  comprimento contra 27,8 % da 3–12×50), é a da L115A1 e da AW original, e **deixa a 5–25×56 (420 mm, objetiva de 62 mm)
  para o acessório "Luneta 8x de precisão"** do desenho de miras, sem duplicar o visual.
- **Bipé da AI dobrado para a frente** sob o guarda-mão, como peça móvel com o pivô no espigão (aberto só se quiser em
  inspeção ou killfeed).
- **Carregador de aço de 5 tiros, fileira única**, que sai por baixo na recarga, com o retém na frente do guarda-mato.
- **Ferrolho** com alavanca dobrada para trás, bola grande, do lado direito; abertura de 60° e recuo (ver 4); **trava de
  três posições** na parte de trás do suporte, também do lado direito; **retém do ferrolho** do lado esquerdo.

Isso é o AWM original de 1996 (o AWM-F é a mesma arma com coronha dobrável) e é o que o jogador reconhece: o chassi verde
com buraco do polegar, o cano longo com freio, a luneta curta e escura, o bipé dobrado.

### 7.2 Fotos para o contorno e as peças

1. **Contorno (lado esquerdo, o da primeira pessoa):** **A — `File:L115A3 sniper rifle.jpg`** (OGL v1.0, 3820×1158, ≈ 0,39–0,40
   mm/px). Corte o silenciador na rosca do freio e a coronha dobrável na dobradiça; o resto (ação, poço do carregador,
   guarda-mão, buraco do polegar, punho, guarda-mato, luneta, bipé) é do AWM .338 de verdade.
2. **Coronha fixa e cor:** **C — `File:Psg 90 AM.068399 (1).jpg`** (CC BY 4.0, 1200×455, ≈ 1,05 mm/px). Registre pelo
   guarda-mato e pelo buraco do polegar (a mesma lógica da M4A4 em `refs/m4a4.json`). Cuidado: o Psg 90 é o AW curto
   (7,62); a coronha e o punho são os do chassi AICS, mas o AWM com o mesmo cano de 26" é 20 mm mais longo que o AW
   (1200 mm contra 1180 mm na brochura, por causa da ação magnum; **onde** está esse acréscimo, no poço do carregador ou
   na ação, eu não confirmei). Por isso o contorno de trás vem do Psg 90 e o da frente vem de A.
3. **Lado direito e peças de um lado só:** **B — `File:Medicina Lines Family Day 18 October 2024 13.jpg`** (CC BY-SA 4.0,
   6960×4640; perfil direito, freio sem silenciador) **junto com D (nº 17, close da ação)**, mais **F (`USMC-19580.jpg`,
   domínio público, macro da bola do ferrolho)** para a haste e a bola. Use B para posição do ferrolho, da trava e do
   freio, não para medir.

Os créditos exigidos (OGL v1.0 para A; CC BY-SA 4.0 para B e D; CC BY 4.0 para C; domínio público para F) entram no
`refs/awp.json`, como a 4.1c já faz.

### 7.3 Decisões que são suas

- **Luneta preta (real) ou verde (como no jogo)?** Recomendei preta; a verde é só um retoque de acabamento do jogo.
- **Freio:** "standard" ou "tactical" da AI? Fotos B e M mostram o de furos com colar; a brochura não diz qual é qual.
- **Bipé:** dobrado no viewmodel (como o jogo) e aberto no inspect/killfeed, ou sempre dobrado?
- **Cano:** o jogo tem cano liso e fino; a arma real é canelada e mais grossa. Recomendei a real (regra do projeto).
- **Proporção do guarda-mão:** o jogo tem o guarda-mão mais longo; segui a arma real.

---

## 8. O que não consegui confirmar

1. **Curso do ferrolho** do AWM (estimativa ≈ 125–135 mm; AT-X de ação curta = 110 mm).
2. **Altura e largura** da arma, em fonte primária (só estimativas de foto, seção 2.2).
3. **Número de ressaltos do ferrolho do AWM** (3 + 1 de emergência no AW; "6" só na Wikipedia).
4. **Lado para o qual a coronha dobrável dobra** (irrelevante para a AWP de coronha fixa).
5. **Verde exato** (RAL/Pantone) das laterais; só tem "olive drab" e "green".
6. **Qual freio** (standard ou tactical) é o das fotos B, M e L115A3.
7. **Posição das mãos no viewmodel do CS2**: nenhum texto; só os quadros da wiki do GO.
8. **Ficha técnica da S&B PM II 3–12×50 original** (os dados acima são das LP atuais).
9. **Largura da bola do ferrolho do AWM** (só o AT-X, 24 mm, e as fotos).
10. **Reddit** e outros sites bloqueados pelas ferramentas não foram lidos; **Counter-Strike Fandom** foi lido pela API
    (`api.php`) porque a página renderizada devolve erro 402 no WebFetch e abre banner de cookies no navegador (não aceitei).

## 9. Fontes (URLs)

- Brochura da AI (AW): http://web.archive.org/web/20120904141921/http://www.accuracyinternational.com/assets/assets/aw_brochure.pdf
- Manual do usuário do AW (AI): http://www.indaginibalistiche.it/utlities/manuali/accuracy_international_aw_sniper_EN.pdf
- Manual do Psg 90 (Exército sueco): https://web.archive.org/web/20210709184741/https://hemvarnet.se/UserFiles/Utbildningsgrupper/Sodertornsgruppen/filer/SoldR_Psg_90.pdf
- L115A3 (Exército Britânico, arquivado): https://web.archive.org/web/20130106203357/http://www.army.mod.uk/equipment/support-weapons/1459.aspx
- Schmidt & Bender 3–12×50 PM II LP: https://www.schmidtundbender.de/en/3-12x50-PM-II-LP-P3L-1cm-cw-DT-ST/644-911-882-96-94A38
- Schmidt & Bender 5–25×56 PM II LP: https://www.schmidtundbender.de/en/5-25x56-PM-II/689-xxx-xxx-xx-xx
- Wikipedia AWM: https://en.wikipedia.org/wiki/Accuracy_International_AWM
- Wikipedia Arctic Warfare: https://en.wikipedia.org/wiki/Accuracy_International_Arctic_Warfare
- Wikipedia .338 Lapua Magnum: https://en.wikipedia.org/wiki/.338_Lapua_Magnum
- CS Wiki AWP e galeria: https://counterstrike.fandom.com/wiki/AWP e https://counterstrike.fandom.com/wiki/AWP/Gallery
- Liquipedia AWP: https://liquipedia.net/counterstrike/AWP
- AT-X (curso do ferrolho 110 mm, bola de 24 mm): https://www.gunmart.net/gun-reviews/firearms/rifles/accuracy-international-at-x
- Militaryfactory AWM (números do .300): https://www.militaryfactory.com/smallarms/detail.php?smallarms_id=1034
- Fr. Frog's (como o atirador opera o ferrolho): https://www.frfrogspad.com/bolt.htm
- API do Commons (as fotos e licenças): https://commons.wikimedia.org/w/api.php (`list=categorymembers`, `list=search`, `prop=imageinfo`)
