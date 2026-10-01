# Miras, acessórios e skins de armas: referências do Pinterest para o MASSACRE

## 1. Como foi coletada a primeira página pública de cada busca, e o que deu errado

### Takeaway
As 29 buscas (25 pedidas e 4 com a redação adaptada) foram abertas sem login no Chromium do Playwright e deram de 22 a 25 pins cada, 688 no total. A lista de cada busca é a primeira página da `BaseSearchResource` na ordem servida, sem repetidos e sem os pins de loja que a página pública não exibe. Os pins não trazem título nem descrição quando não há login, então o conteúdo e as marcas foram identificados olhando as imagens.

### Cited Findings
- Método: Playwright (`/opt/node22/lib/node_modules/playwright/index.mjs`) com o Chromium já instalado em `/opt/pw-browsers`, sem login, `locale` en-US, janela de 1366×1600. O script abre `https://www.pinterest.com/search/pins/?q=<busca codificada>`, espera o primeiro `img` do `i.pinimg.com`, lê o DOM, rola a página três vezes e lê o DOM de novo. Enquanto isso, grava a resposta da `/resource/BaseSearchResource/get/` que a própria página pede. Exemplo: [busca QRD](https://www.pinterest.com/search/pins/?q=red%20dot%20sight%20rifle).
- Na primeira tentativa o Chromium recusou o certificado do proxy (`net::ERR_CERT_AUTHORITY_INVALID`), porque o banco NSS do navegador (`/root/.pki/nssdb`) estava vazio. Instalei o `libnss3-tools` e cadastrei a CA do proxy (`/root/.ccr/agent-proxy-ca.crt`) nesse banco com `certutil`. A verificação de TLS continuou ligada. Depois disso todas as páginas responderam com status 200 ([busca QHO](https://www.pinterest.com/search/pins/?q=holographic%20sight%20rifle)).
- O HTML do servidor (`__PWS_INITIAL_PROPS__` e `__PWS_DATA__`) não trouxe nenhum pin. A grade inteira vem da primeira chamada à `BaseSearchResource`, que devolveu de 22 a 28 resultados. Rolar a página não carregou uma segunda página: o DOM ficou igual antes e depois da rolagem em todas as buscas ([busca QAC](https://www.pinterest.com/search/pins/?q=acog%204x%20scope%20rifle)).
- Sem login, cada pin da API só traz `id`, `images`, `dominant_color`, `image_signature`, `node_id` e `tracking_params`. Título, descrição, texto alternativo, domínio e link chegam nulos, e no DOM cada bloco tem `alt="Pin"` e nenhum `href` ([busca QRD](https://www.pinterest.com/search/pins/?q=red%20dot%20sight%20rifle)).
- Nas buscas QNV, QTH e QAT a API mandou pins que a página pública não desenhou. Em QNV foram as posições 1 a 5. Em QAT, as posições 1 a 5. Em QTH, as posições 16, 18, 19 e 20, e também a 17, cuja imagem é a mesma da posição 22, que foi desenhada. Baixei e vi todos. São fotos de produto em fundo branco (miras térmicas e digitais, binóculos noturnos, um deles com a marca FNIRSI "NVS 40", canivetes Spyderco e Benchmade), ou seja, pins de loja. O pin 4608800996756171840 aparece em QNV e em QTH. Eles ficaram fora da lista e vão registrados em cada busca ([busca QNV](https://www.pinterest.com/search/pins/?q=night%20vision%20scope%20view); [busca QTH](https://www.pinterest.com/search/pins/?q=thermal%20scope%20view); [busca QAT](https://www.pinterest.com/search/pins/?q=anodized%20titanium%20knife)).
- Nas outras 26 buscas a ordem da API e a do DOM batem pin a pin. Em QAT, o bloco 21 do DOM veio sem `src` (vídeo ou imagem que ainda não tinha carregado) e corresponde à posição 26 da API, então entrou na lista. Em QTH, a mesma imagem veio em dois pins, nas posições 17 e 22 da API, e a página só desenhou a 22; ficou uma entrada só ([busca QTH](https://www.pinterest.com/search/pins/?q=thermal%20scope%20view)).
- As imagens foram baixadas em 736x só para o scratchpad (`.../scratchpad/pinterest/img/<código>/`). Montei folhas de contato com 8 pins grandes e o resto menor e olhei todos os 688 com o Read, mais ampliações dos diagramas e das telas de UI. Nenhuma imagem foi para dentro do projeto. Dois pins sorteados por busca foram baixados de novo, e o MD5 bateu com o arquivo guardado em todos, o que confirma que cada número aponta para o hash certo.
- Horário da coleta: 2026-09-28 entre 05:38 e 05:42 UTC para as 25 buscas pedidas e entre 05:51 e 05:53 UTC para as 4 adaptadas ([busca QCO](https://www.pinterest.com/search/pins/?q=color%20case%20hardening)).
- Redações adaptadas, porque a busca original veio fora do assunto ou vaga demais:
  - "case hardened receiver" (QCH) trouxe quase só maletas rígidas de arma (a palavra *case*). "color case hardened receiver" (QCC) trouxe sobretudo cerakote de AR. "color case hardening" (QCO) acertou o acabamento ([QCH](https://www.pinterest.com/search/pins/?q=case%20hardened%20receiver); [QCC](https://www.pinterest.com/search/pins/?q=color%20case%20hardened%20receiver); [QCO](https://www.pinterest.com/search/pins/?q=color%20case%20hardening)).
  - "weapon light rifle" (QWL) trouxe fuzis inteiros e concepts de ficção científica. Complementei com "weapon mounted flashlight" (QFL) ([QWL](https://www.pinterest.com/search/pins/?q=weapon%20light%20rifle); [QFL](https://www.pinterest.com/search/pins/?q=weapon%20mounted%20flashlight)).
  - "laser sight beam smoke" (QLS) trouxe sobretudo shows de laser e ponteiros. Complementei com "ir laser night vision rifle" (QIR), que trouxe os módulos de laser e não o feixe visto no noturno ([QLS](https://www.pinterest.com/search/pins/?q=laser%20sight%20beam%20smoke); [QIR](https://www.pinterest.com/search/pins/?q=ir%20laser%20night%20vision%20rifle)).
- Não foi preciso recorrer ao WebSearch com `site:pinterest.com`, nem montar a chamada JSON à mão. Ler a resposta da própria página bastou.

### Inferences
- Um usuário com login, em outra região ou em outro dia, vai receber outra ordem e outros pins. Estas listas são um retrato da busca pública naquele momento. O número de 22 a 25 pins fica perto do que o projeto registrou nas buscas da subfase 4.1a (22 a 29 pins). As seis buscas da 4.1c (QMR a QBN) guardaram 30 cada.
- Como não há texto no pin, as marcas citadas abaixo são só as que aparecem legíveis na imagem. Nomes de modelo que eu reconheci pela forma aparecem como "tipo X" ou "estilo X", e não como fato.

### Gaps
- Não dá para saber a região de saída do proxy, que pesa nos resultados do Pinterest.
- Não sei como as buscas da 4.1c chegaram a 30 pins. Aqui a primeira página sem login deu no máximo 25 desenhados, e rolar não trouxe mais.
- Não há como tirar título ou descrição dos pins sem login, e a página do pin (`/pin/<id>/`) não foi aberta. Por isso a origem e a licença de cada imagem ficam desconhecidas, como nos boards anteriores do projeto.

## 2. Miras e acessórios: o que as 14 buscas de óptica e acessórios mostram e o que o artista 3D tira delas

### Takeaway
Quase tudo nesses boards é foto de produto real com a marca visível (Vortex, EOTech, Holosun, Sig Sauer, Trijicon, Leupold, Aimpoint, Primary Arms, Burris, Inforce, Streamlight, Olight, Steiner) ou foto de atirador. Arte de jogo quase não aparece: só as sobreposições de luneta e algumas cenas noturnas. Os pins mais valiosos são os diagramas com as peças nomeadas e as fichas com medidas (QHO12, QMG16, QMG18, QIR17, QIR18, QRT6). Também valem os modelos sem marca, bons para servir de peça genérica (QRD5, QRD24, QHO16, QAS2 sem a gravação), as vistas pela mira (QRD2, QRD14, QHO13, QHO23, QRT3) e as sobreposições de luneta prontas (QRT1, QRT7, QRT20).

### Cited Findings

#### QRD: "red dot sight rifle"
- Código **QRD** · busca `red dot sight rifle` · https://www.pinterest.com/search/pins/?q=red%20dot%20sight%20rifle · 25 pins na ordem servida · coletada em 2026-09-28 05:38 UTC
- Lista ordenada (código, caminho da imagem depois de `i.pinimg.com/originals/` ou `/736x/`):

```text
QRD1 28/d9/70/28d9704b3cbd59ac481ccd2c98964b5e
QRD2 06/83/b4/0683b4dcda68ee9691b48a620103175c
QRD3 86/1a/f2/861af2196325d408a4a7f4d6392c3f21
QRD4 73/6b/2e/736b2e05d891fa2b1ea7f742b17d6299
QRD5 47/a7/ab/47a7abdaa14fe738139b89b0d2ac747f
QRD6 af/45/8e/af458ed62f5bc081b82f230adb45ff87
QRD7 80/9e/6d/809e6dec10d04fee24a3cb664c2068cf
QRD8 61/da/c7/61dac78fde2145dd1db561434a071b75
QRD9 ba/6c/97/ba6c9764cc358658bc25af9def881e87
QRD10 16/71/56/167156b466e9a8aff3a5ea8ba3d906e1
QRD11 b5/d5/95/b5d595f1c23c2bb9d2e5133bf6949907
QRD12 bc/d4/15/bcd41565d7e614d761d8378d47ee4430
QRD13 94/54/7d/94547d765289e4122988d789ffc1f430
QRD14 21/b8/69/21b869de7b8e1bbad121c92483fbeb98
QRD15 dd/66/2b/dd662b38260b7563ad60adaee82b54f2
QRD16 8e/75/43/8e754394e5f47a4418004d0f543890e2
QRD17 18/e4/09/18e409d04cafa7b23405c8e8da367410
QRD18 c7/ba/5f/c7ba5fda84796f0a31f6c84034a9409f
QRD19 f4/15/0f/f4150fd7192dcb5d6ab84cf730ef97ab
QRD20 85/1d/61/851d619495790a412cdcd24bdd6fb496
QRD21 6c/3e/ba/6c3eba6bca129fca6226509e7efe96c7
QRD22 1a/e1/03/1ae10318b391ab75769fd0a71e549758
QRD23 27/ef/58/27ef58afad3c12d8cb2eb139c274e3f0
QRD24 70/99/27/709927a9ba8d554a2962265babeb9905
QRD25 75/1d/fe/751dfea48f270d059febf07250498b0f
```
Fotos de produtos reais, com marcas visíveis em QRD3, QRD8, QRD9, QRD10, QRD12 e QRD19 a QRD22. Nada de arte de jogo.
- **QRD1**: reflex de janela retangular visto por trás. O retículo círculo-ponto vermelho brilha no vidro, e a borda da janela e o reflexo do vidro aparecem. Sem marca visível.
- **QRD2**: vista pela mira numa pista externa. A caixa da mira fica desfocada, o alvo fica nítido e o ponto é pequeno. É a profundidade de campo da mira apontada.
- **QRD3**: a UH-1 da Vortex ("UH-1" escrito embaixo dos botões) vista por trás num AR, apontada para um campo. Na traseira ficam os botões −, NV e +, e o retículo vermelho aparece na janela retangular.
- **QRD5**: red dot tubular genérico, marcado só "1X30RD", em fundo branco. Mostra os tambores de ajuste com tampa, o botão de brilho na lateral e a base integrada com parafuso de aperto. É a melhor base para um red dot sem marca.
- **QRD8**: óptica Leupold (logo visível) em FDE com uma mini reflex em cima. Mostra miras empilhadas e a cor areia.
- **QRD9**: Holosun (logo visível) de janela grande e aberta. Visto de lado, o vidro tem tom âmbar dourado; tem alavanca de soltura rápida.
- **QRD14**: vista desfocada por dentro de um red dot micro tubular, com a massa de mira de ferro alinhada no meio, o ferro visto junto com o ponto. Serve de referência para mirar com o ferro e o ponto ao mesmo tempo.
- **QRD18**: três miras da mesma linha lado a lado (reflex de pistola, micro tubular num riser e janela fechada). Dá a escala de uma em relação à outra.
- **QRD19**: Holosun "DRS-TH" (texto e logo visíveis), uma reflex térmica. A lente da câmera fica ao lado da janela, e a tampa basculante está aberta.
- **QRD21** e **QRD22**: Sig Sauer ROMEO5 cinza e ROMEO4S (marcas visíveis). A ROMEO4S aparece com a tampa basculante e um riser com alavanca QD. As duas têm vidro âmbar e tambores serrilhados.
- **QRD24**: micro tubular sem marca num riser alto, com três botões na lateral. É o modelo genérico mais limpo do board.
- O resto: QRD4 é um anúncio de loja ("LG02 Infrared Red Laser Tactical Sight") com preço em rúpias paquistanesas, PKR (junk). QRD6 é um brilho de LED com logo de caveira. QRD11, QRD12, QRD16 e QRD25 são combos baratos de luneta 4x com reflex, e QRD12 é Barska. QRD10 é uma Burris vista de cima. QRD7 é uma vista por dentro de um red dot tubular, escura. QRD13 é uma micro tubular diante de um alvo de silhueta. QRD15 é um fuzil tipo M1A com dot à frente. QRD17 é uma ACOG. QRD20 é uma pistola numa caixa de munição. QRD23 é um AR inteiro.

#### QHO: "holographic sight rifle"
- Código **QHO** · busca `holographic sight rifle` · https://www.pinterest.com/search/pins/?q=holographic%20sight%20rifle · 24 pins na ordem servida · coletada em 2026-09-28 05:38 UTC
- Lista ordenada (código, caminho da imagem depois de `i.pinimg.com/originals/` ou `/736x/`):

```text
QHO1 c3/9f/1d/c39f1d411dc1ec7b993629a58ded870a
QHO2 d1/9b/60/d19b601251fe1e22f1b70cfda1a6b508
QHO3 f6/37/8f/f6378f1ae5dd71c0cfbbbf70ecdb1eb2
QHO4 c4/1f/bf/c41fbf54dae3c0229cd4326de1928572
QHO5 27/fb/ac/27fbac65116d6ae0dd87ea3cede2f139
QHO6 9c/67/b9/9c67b9631f96a135e5aecebbb46edee7
QHO7 7b/3b/72/7b3b72ffa10116c40d3489b167bb8f62
QHO8 db/44/b6/db44b663a3d56f6acc1faffbf79e1a2d
QHO9 6d/fd/6c/6dfd6c4aa2ea6ffc369139c71635ae1a
QHO10 fe/9e/89/fe9e891c494113c20d0a8fbdf0566334
QHO11 b3/fc/7a/b3fc7aad0d33d35de59a10f92b42bdd3
QHO12 d4/af/a3/d4afa30e5202710a91b83ff48d734b84
QHO13 d6/a0/3b/d6a03b35e43fb181012378818b84b0f1
QHO14 54/3c/e8/543ce8910c9136fdfad1112f98461a4d
QHO15 c9/7d/ea/c97dea6969c13e39d4c5db8e167d4a09
QHO16 f6/d2/e9/f6d2e90883765554bf418e49aff950be
QHO17 9a/fc/e0/9afce08cfc9c90f70b8299c1817857e6
QHO18 e8/b4/79/e8b479f10ac5e9a33cb300d3f12fd278
QHO19 83/44/d9/8344d9ef724d512a2092e216e60428bb
QHO20 a7/10/39/a71039c1c8ad7248748d0b4952fb5e80
QHO21 0b/d8/e6/0bd8e6383efff68a2f41115bcde4c6bf
QHO22 3a/e0/e2/3ae0e2713f360e37544a78d877c4d8de
QHO23 7c/e3/fc/7ce3fc21c1fc0c455322c08abb0751f2
QHO24 ba/6c/97/ba6c9764cc358658bc25af9def881e87
```
Produtos reais: EOTech, Vortex AMG UH-1, Holosun, Trijicon, e réplicas "PHANTOM" e "THETA OPTICS". Nada de arte de jogo.
- **QHO1**: Vortex Razor AMG UH-1 (marcas visíveis). Os tambores têm "1 CLICK = 0.5 MOA" e as setas UP e RIGHT gravadas, a janela tem reflexo vermelho e o capuz é inclinado.
- **QHO2**, **QHO4** e **QHO6**: EOTech (QHO4 é a réplica "PHANTOM"). Mostram a caixa de pilha transversal, o capuz, a etiqueta amarela de laser e o texto "FOR LAW ENFORCEMENT/MILITARY USE". Dão a proporção da holográfica clássica.
- **QHO3**: holográfica verde com a gravação "Zombie Stopper" e o símbolo de risco biológico, uma edição temática. Mostra que a mira aceita skin (cor mais gravação) sem mudar de forma.
- **QHO5** e **QHO22**: holográfica EOTech com a lupa G33 numa base que bascula para o lado, em FDE e em preto (logos visíveis).
- **QHO12**: diagrama da EOTech com as peças nomeadas. Na holográfica: Reticle, Holographic Window, Battery Compartment, Aluminium Hood, On/Off & Brightness Adjustment Switches e Quick-Detach Lever. Na lupa G33: Vertical Adjustment, Locking Button, Quick-Detach Lever e Adjustable Diopter.
- **QHO13**: vista pela holográfica sobre uma paisagem com água. A caixa fica bem desfocada e o retículo vermelho de círculo e cruz fica nítido.
- **QHO11**: vista por uma UH-1 (logo da Vortex na traseira) numa sala. O retículo de anel com ponto e quatro traços fica nítido e a sala desfocada. Tem a marca d'água da Pew Pew Tactical.
- **QHO17**: EOTech 552 com o detalhe da traseira (botões de seta) e o retículo aceso.
- **QHO21** e **QHO23**: traseira da UH-1 num fuzil, e a foto em primeira pessoa com as duas mãos no AR. É o enquadramento que o jogo usa.
- **QHO9**: Trijicon RMR (marca). A mini reflex tem as "orelhas" de proteção e o vidro âmbar.
- **QHO16**: reflex fechada sem marca, com a caixa em FDE e a base preta, frisos na lateral e parafusos aparentes. É uma boa forma genérica.
- O resto: QHO7 é uma Saiga-12 com holográfica, foto de estilo. QHO10 é um catálogo de réplicas THETA com preços (junk). QHO14 é um atirador com holográfica e lupa. QHO18 é um bullpup FDE (já está no projeto como QVM1). QHO8 é uma reflex em foto escura, com borda acobreada no vidro. QHO19 é uma reflex dobrável com reflexo azul e âmbar. QHO15 e QHO20 são a UH-1 em foto de produto, com "AMG UH-1" e "1 CLICK = 0.5 MOA" gravados, e QHO24 repete QRD9.

#### QAC: "acog 4x scope rifle"
- Código **QAC** · busca `acog 4x scope rifle` · https://www.pinterest.com/search/pins/?q=acog%204x%20scope%20rifle · 25 pins na ordem servida · coletada em 2026-09-28 05:38 UTC
- Lista ordenada (código, caminho da imagem depois de `i.pinimg.com/originals/` ou `/736x/`):

```text
QAC1 58/cc/6e/58cc6e910444c825d6caee1a9d59df58
QAC2 d9/74/74/d974747a730f60df4e374e0e6090e69c
QAC3 ff/8a/81/ff8a819cfeed2c071cc44a3902b1f14c
QAC4 ab/03/99/ab039966ff6715aefcf52d03dd805dfa
QAC5 8f/28/3d/8f283dfee491b46d9c09bfe8a2919460
QAC6 6a/34/f7/6a34f75302aff5bcbad3fbe18cc681be
QAC7 16/71/56/167156b466e9a8aff3a5ea8ba3d906e1
QAC8 57/f3/6c/57f36c533c008214f19b57f08873410d
QAC9 86/aa/64/86aa64f03dd0d6bd788701efb966e825
QAC10 28/8d/ee/288dee8479989faa899a1842a302cb74
QAC11 c0/4c/89/c04c896dd26072e53f9a308a012c1c08
QAC12 67/92/a7/6792a7783088ef9dee24bcd07f22d9bc
QAC13 ec/89/7c/ec897c121b1a8b9b04c93256657edead
QAC14 75/1d/fe/751dfea48f270d059febf07250498b0f
QAC15 f1/63/e8/f163e880ea7f56687eff736f60999c77
QAC16 94/7d/3b/947d3b305e72f6dcca273e864fbce2a9
QAC17 25/bc/f4/25bcf48e9e8380ed5ffdb82f17921f27
QAC18 5f/39/99/5f399919a571e98d47b04fa2afe921db
QAC19 0b/db/51/0bdb5172f059ea09af75561c66f60e7b
QAC20 af/98/33/af98339ea64895929b45f46ae7818edc
QAC21 32/9c/91/329c9158dd47df89f87c09c68206052b
QAC22 38/f0/aa/38f0aa2db99df233f11710edbd3f8cf7
QAC23 fd/b4/43/fdb44347444c7e06cb79ffc4adfbbae6
QAC24 ea/01/c8/ea01c8f41086b4c8c283a7742d2b775e
QAC25 86/6b/45/866b458eec9f076a6f82f7e3ef0e9b30
```
Produtos reais (Trijicon ACOG, Burris, HK) e cópias. Mais ou menos metade do board é fuzil montado com LPVO, não ACOG.
- **QAC1**: colagem de seis ACOGs, em preto e FDE, com fibra óptica vermelha ou verde em cima, killflash em colmeia, tampas e RMR em cima. É a mesma peça com as variações que um sistema de acessórios pode oferecer.
- **QAC4** e **QAC8**: Trijicon ACOG com RMR (marca visível). Mostram o corpo em cunha, o tubo de fibra óptica vermelho em cima e a base com porcas de mão.
- **QAC5**: ACOG com RMR de perfil, com a etiqueta de QR code e número de série no corpo. Serve para a silhueta.
- **QAC16**: ACOG FDE com RMR e o retículo num círculo: chevron vermelho com a linha de queda.
- **QAC25**: ACOG com o desenho do retículo ao lado: uma ferradura vermelha com ponto e a escala de queda (4, 6, 8).
- **QAC17**: ACOG preta com tampas basculantes e killflash de colmeia.
- **QAC12**: ACOG FDE com RMR, a variante de cor.
- **QAC7**: vista de cima de um AR com LPVO Burris e mini dot a 45°. Aparecem os números no anel de ampliação.
- **QAC13**: receptor da HK com as gravações "Heckler & Koch GmbH / Made in Germany" e "Heckler & Koch Defense Inc. / Ashburn VA", uma etiqueta de QR code e uma "Trijicon ACOG" em cima. É referência de gravação de fábrica, que no jogo deve ir sem nome.
- O resto: QAC2, QAC9, QAC15, QAC18 a QAC21 e QAC24 são fuzis montados. QAC11 e QAC14 são combos baratos. QAC10 (uma captura de tela de iPad) e QAC22 são a Burris LRS na base P.E.P.R. com uma mini reflex. QAC3 é um AR com uma Glock, QAC6 é uma EOTech com lupa na base Unity e QAC23 é uma ACOG com base de alavancas. QAC2, QAC3 e QAC19 já estão no projeto (QTM4, QRA1 e QRA2).

#### QLP: "lpvo 1-6x scope ar15"
- Código **QLP** · busca `lpvo 1-6x scope ar15` · https://www.pinterest.com/search/pins/?q=lpvo%201-6x%20scope%20ar15 · 24 pins na ordem servida · coletada em 2026-09-28 05:38 UTC
- Lista ordenada (código, caminho da imagem depois de `i.pinimg.com/originals/` ou `/736x/`):

```text
QLP1 a5/de/3d/a5de3d81ca18349fd033952bf6012308
QLP2 64/d1/43/64d14380041731ced22bf0dea078afb2
QLP3 a7/92/c6/a792c6a81e296adf9a6a3342df01b5e7
QLP4 4d/db/23/4ddb238c6ee757bb560816d7f65d8cb4
QLP5 71/3c/ad/713cad293cc9366c1e6f232018beefae
QLP6 49/23/d3/4923d3e4a1975248e53907778e8652c8
QLP7 28/8d/ee/288dee8479989faa899a1842a302cb74
QLP8 a3/26/80/a32680d6fd65a43fae7b6ea710cbb31e
QLP9 6a/34/f7/6a34f75302aff5bcbad3fbe18cc681be
QLP10 0d/c5/39/0dc539053e741bbd49835503fa44fdce
QLP11 5f/39/99/5f399919a571e98d47b04fa2afe921db
QLP12 bf/f8/af/bff8af86c31193ac869ced05c2ebc247
QLP13 26/a8/58/26a85811e6faa1a2fe77dd5d99c155e7
QLP14 c2/01/46/c201463f11cec89eb53c186a48086c3b
QLP15 c1/ac/1b/c1ac1b4c0a8ecccb028943e415ae86c9
QLP16 39/50/05/395005bdba5aa98a6fc4f4d662f2d77d
QLP17 0b/d7/50/0bd750731fddebbc4a6d320188bcb5a7
QLP18 16/71/56/167156b466e9a8aff3a5ea8ba3d906e1
QLP19 16/08/fe/1608fe252ace3d1c07cc195e258cd6d1
QLP20 b4/b1/b8/b4b1b8443940283eb7c515dd82e426a4
QLP21 17/48/24/174824e58e2da6caf31378d7c4ae11e3
QLP22 9d/0b/15/9d0b153b77eae2c743717872de447ef6
QLP23 4a/d3/a1/4ad3a13c7b002f08e19d937ab03e3941
QLP24 95/d6/ac/95d6ac585a07f63caee59ac71977390a
```
Produtos reais (Primary Arms, Burris, EOTech e Unity) e muitos fuzis montados.
- **QLP1**: Primary Arms (marca visível), um LPVO visto de quatro ângulos. Aparecem o anel de ampliação com a alavanca, os tambores, a ocular com o ajuste de dioptria e a luneta montada. É o melhor pin para modelar um LPVO.
- **QLP24**: LPVO de catálogo em fundo branco. O perfil é limpo, com tambores, anel e ocular, e o logo da torreta não é legível.
- **QLP7**: captura de tela de iPad com a Burris "LRS" e uma mini reflex na montagem cantiléver P.E.P.R. (repete QAC10).
- **QLP10**: close de um LPVO na montagem de uma peça, com a alavanca de zoom.
- **QLP13**: AR com LPVO e caixa de laser tan num tripé.
- **QLP4**: AR com LPVO pintado à mão em camuflagem de spray cinza, verde e areia. Liga este board ao de skins.
- **QLP16** e **QLP17**: fuzis FDE com LPVO, bandoleira e tripé, com a cor areia no conjunto inteiro.
- O resto: QLP3, QLP5, QLP6, QLP8, QLP11, QLP15, QLP19, QLP20, QLP22 e QLP23 são fuzis montados no chão ou no concreto. QLP2 é um MK18 de airsoft com PEQ, QLP9 repete QAC6, QLP12 e QLP14 são builds, QLP18 repete QRD10 e QLP21 é um fuzil camuflado apoiado num mourão. QLP8 e QLP20 já estão no projeto (QTM30 e QTM28).

#### QMG: "magnifier flip red dot"
- Código **QMG** · busca `magnifier flip red dot` · https://www.pinterest.com/search/pins/?q=magnifier%20flip%20red%20dot · 22 pins na ordem servida · coletada em 2026-09-28 05:38 UTC
- Lista ordenada (código, caminho da imagem depois de `i.pinimg.com/originals/` ou `/736x/`):

```text
QMG1 ed/29/dd/ed29dd9092454451bb629bb1a80eec38
QMG2 c4/d4/57/c4d45783235eb376f83c64f25878c442
QMG3 ba/37/bd/ba37bdebf18aeea22f8f9ab613c4635b
QMG4 7b/09/ff/7b09fffe18c13711d7cfd4bdeceac745
QMG5 e2/6f/8b/e26f8bb705a96c685299136a1c8d4185
QMG6 a5/f0/98/a5f09835e62342a79e64a3eda778593a
QMG7 f8/62/8e/f8628e183ae40801c51593e735f1082e
QMG8 2b/55/d7/2b55d7c4be858b6c3c52cc9511c9c4c8
QMG9 83/54/80/835480993ec07a32130897555b4527b4
QMG10 53/37/3d/53373dc7f3471e04be3c157f2f6bc9fb
QMG11 3e/1a/7c/3e1a7c63de10f05b2b70291c62f392bd
QMG12 d3/62/16/d36216251146d781c727cd6caf572498
QMG13 20/09/db/2009db075463088640666c902fad05c0
QMG14 09/26/7b/09267b9f9d993074287a380cc6cd3b61
QMG15 e7/fb/a3/e7fba36ca2755f5bb013d180a30682a8
QMG16 22/6d/11/226d118bda2858c9827037d56b51f4b2
QMG17 c1/bc/d2/c1bcd2eff3b17ce3cad0023075b18fe6
QMG18 97/e5/2a/97e52aa20ed15ee49e585934391e27e5
QMG19 27/d2/86/27d286d31a75b3704cb2ff75dcdcab0a
QMG20 3e/e0/8b/3ee08b98a5d2caceeccf61a8999c201b
QMG21 4f/a5/97/4fa597a1f21cec7fecb882aaccc55629
QMG22 e3/4d/a0/e34da0a62eb53d3c86c50c3e592327a9
```
Produtos reais: Vortex, Holosun, Sig, Aimpoint, CVLIFE, Tacticon, a réplica SOTAC e um upper BCM.
- **QMG18**: diagrama da Vortex VMX-3T com as peças nomeadas: Flip Mount, Objective Lens, Dot-Centering Screw (Elevation), Dot-Centering Screw (Windage), Focus Dial, Ocular Lens, Shim Plate, Mounting Screws ("Tighten to 20 in/lbs") e Release Button. Traz a nota "For a lower 1/3 co-witness height, attach the shim plate between the flip mount and the VMX-3T".
- **QMG16**: ficha da Vortex com as medidas. StrikeFire II: 1x, objetiva de 30 mm, ajuste de 1/2 MOA, 5,6 pol. de comprimento, 7,2 oz. VMX-3T: 3x, alívio de olho de 2,2 pol., campo de 38,2 pés a 100 jardas, tubo de 30 mm, 4,3 pol. (no desenho L1 = 4,2 pol., D1 = 1,36 e D2 = 1,3), 11,9 oz.
- **QMG12**, **QMG13** e **QMG14**: Vortex Micro 3X (logo). A lente da objetiva tem reflexo verde, a base bascula com alavanca e a lateral tem a marca "RIGHT".
- **QMG4** e **QMG5**: Holosun HM3X (logo), com o anel de dioptria e a base QD basculante.
- **QMG8**: anúncio da badassoptic.com, "MODULAR / TUCKS DOWN": uma lupa Aimpoint (logo) que dobra para baixo. Mostra o movimento.
- **QMG15**: red dot tubular com as duas tampas basculantes abertas, com as dobradiças e as abas.
- **QMG22**: AR com upper BCM (logo), red dot e lupa montados. Mostra o espaço real entre as duas peças.
- **QMG2**: combo da CVLIFE (logo), dot com lupa 3x em bases QD.
- **QMG7**: anúncio da SOTAC com bases basculantes FDE, réplicas de G33 e G43. Mostra a dobradiça.
- O resto: QMG1, QMG6, QMG9 a QMG11 e QMG20 são lupas genéricas, e QMG21 é da Tacticon. QMG3 é a capa de um artigo com a Sig JULIET3, e QMG17 e QMG19 são a Vortex StrikeFire II com a VMX-3T.

#### QRT: "sniper scope reticle view"
- Código **QRT** · busca `sniper scope reticle view` · https://www.pinterest.com/search/pins/?q=sniper%20scope%20reticle%20view · 23 pins na ordem servida · coletada em 2026-09-28 05:38 UTC
- Lista ordenada (código, caminho da imagem depois de `i.pinimg.com/originals/` ou `/736x/`):

```text
QRT1 53/f9/84/53f984a6241aec7c4949d8aa8725950d
QRT2 c5/d2/89/c5d289dcae3304fe3701b124a779830a
QRT3 2b/f5/b5/2bf5b59cfd35ad5b486b42bc461b463c
QRT4 c1/63/9b/c1639b8d3d3bc2c9a33e1203df4f6e2a
QRT5 14/a1/3c/14a13c6a472c5810833417cff970d5ef
QRT6 86/7e/ce/867ecefa3c30b85460a12f652c0f3d20
QRT7 93/01/e0/9301e0d810f91cf91acc90c565b589cc
QRT8 9f/71/01/9f710158ecddce402cf09a8482dc8f7d
QRT9 01/13/36/0113367f590124b8b696a38556e3e3ed
QRT10 06/ae/ec/06aeecd105fd67a240d6700b6f0a1285
QRT11 d7/0f/71/d70f711683f05044b8e38055e6f6b578
QRT12 c4/e4/cb/c4e4cb4c16731adaa9ab0fb9dd6412a6
QRT13 a1/07/3f/a1073fac5baddc5b2e58d407f3b30187
QRT14 50/cf/f9/50cff92b0df50e9cd7d9f2a67e5d8148
QRT15 87/f3/92/87f392f423fdece137cb38feb7acde7f
QRT16 43/c6/8d/43c68d1624e2d6a27fc034dbe4f32ee2
QRT17 9a/37/c7/9a37c71ddc71a5608586f9ba639daef7
QRT18 75/4b/45/754b45184afb5c1e3764cdf1d5bd56c2
QRT19 a8/6b/dd/a86bdd4eb41d003d92c021b06705f63a
QRT20 80/d1/b2/80d1b2641cc12f0b694a14a73d134be3
QRT21 15/0b/e7/150be781011bfc570d8c8a77756e61cc
QRT22 2e/d2/04/2ed204cf3c097fd74e1171c3135929d5
QRT23 b4/54/9c/b4549c65a008a61a1fc7d03136d5b464
```
Uma mistura de desenhos de retículo (um da Kahles, com a marca), fotos pela luneta e sobreposições 2D prontas, parecidas com as de jogo.
- **QRT1**, **QRT7**, **QRT20** e **QRT22**: sobreposições de luneta prontas. Têm o disco claro, a vinheta preta de borda macia e a cruz com postes grossos e marcas finas. QRT7 tem fundo transparente (xadrez), e QRT20 e QRT22 têm linhas de queda (BDC). É o tipo de camada 2D que a mira de sniper usa na tela.
- **QRT2**: retículo "árvore de Natal", com a cruz central vermelha e os pontos de queda numerados de 2 a 10.
- **QRT6**: desenho técnico do retículo SKMR4 da Kahles ("kahles.at", 11.03.2020), com as medidas em MIL: 16 MIL de largura total, marcas de 0,25 e 0,5 MIL, traço fino de 0,035 MIL, a "árvore" de pontos de queda em vermelho até 12 MIL embaixo, e cada medida também em cm/100 m e pol./100 jardas. Dá as medidas para desenhar um retículo com proporção de verdade.
- **QRT3**, **QRT5** e **QRT8**: fotos pela luneta. Aparecem o anel escuro da sombra do olho, o corpo da arma desfocado e a paisagem (campo com alvos de aço, pedreira, neve ao entardecer).
- **QRT13**: o retículo da PSO-1, com os chevrons e a curva de distância, num tom esverdeado. É a referência de luneta soviética, para AK ou SVD.
- **QRT16**: luneta vista de trás, com a bolha de nível, os tambores numerados e o retículo em MIL sobre um campo de tiro no deserto.
- **QRT9**: vista por uma luneta com uma térmica clip-on na frente. A cruz da luneta fica por cima da imagem térmica, e o menu do aparelho aparece em volta ("CLIP-IR 4X", "CLIP-ON MODE", "50HZ", "TO CALIBRATE", bateria, "SYSTEM MENU"). Mostra o HUD de uma mira eletrônica.
- **QRT17**, **QRT19** e **QRT21**: diagramas de retículo (cruz verde acesa, duplex com anel e ponto vermelho, ferradura com BDC).
- O resto: QRT4 e QRT12 são vistas de floresta e de um esconderijo com rede camuflada. QRT10 é um ícone de mira. QRT11, QRT14 e QRT15 são fotos de guerra pela luneta (QRT11 mira uma pessoa), e só servem pela composição e pelo tom. QRT18 é uma floresta no inverno. QRT23 é uma sobreposição com céu de pôr do sol.

#### QNV: "night vision scope view"
- Código **QNV** · busca `night vision scope view` · https://www.pinterest.com/search/pins/?q=night%20vision%20scope%20view · 22 pins na ordem servida; a API mandou 27 · coletada em 2026-09-28 05:39 UTC
- Fora da lista (a API mandou, a página pública não desenhou): posição 1: pin 4608800996756171840 (`91/cc/06/91cc068ca53c5b6296575da4c342e1e0`); posição 2: pin 1150388298600916582 (`6b/a2/5f/6ba25fd7c7863eed02f107fdf10c6823`); posição 3: pin 4596275375737768320 (`ed/b6/6c/edb66cb9d831fa790064d6c857d55419`); posição 4: pin 4598386429164913792 (`4c/82/73/4c8273336d9bd993925d0022a6e02310`); posição 5: pin 4600990051054742656 (`9f/be/25/9fbe252f1cbf1da68bb119a4f81fa327`).
- Lista ordenada (código, caminho da imagem depois de `i.pinimg.com/originals/` ou `/736x/`):

```text
QNV1 01/13/36/0113367f590124b8b696a38556e3e3ed
QNV2 05/af/a9/05afa90d22052df8548414b2c771358d
QNV3 3b/11/3b/3b113bf5ff370de7bce32b438599dcae
QNV4 70/1b/84/701b84252529650ef523369fe9e8c54e
QNV5 c9/19/3f/c9193f713f5e1a2e0cce7de333964307
QNV6 46/47/de/4647defbaf246d2babbd7aa32f2f1b3b
QNV7 c4/bc/fd/c4bcfd1cb91c079e79f0e0fd04a011ab
QNV8 76/9e/66/769e663b11d72aee46b4a2cd2b3a4827
QNV9 a1/07/3f/a1073fac5baddc5b2e58d407f3b30187
QNV10 15/19/6f/15196fa828189c5b1a9131843f325783
QNV11 1a/40/42/1a4042d5f1951df84f05e4e9b75906ab
QNV12 ae/41/f0/ae41f0b80e5fddb42852d57146feb897
QNV13 66/65/4b/66654b0c0ed8e1ddf970404a79bba8f4
QNV14 a2/f7/31/a2f73101de45934640a405372221d567
QNV15 27/f4/54/27f4544dff4efc1c3d9045add3d8760d
QNV16 c9/f9/c1/c9f9c1f1001a8ab5d475ca5f2acc010b
QNV17 6b/ad/0a/6bad0a5be81328d4efe28633ba04d34d
QNV18 87/af/96/87af964749a65d0dc283619d367d49da
QNV19 4a/99/d6/4a99d6ab59aff276cf738f0c7f674944
QNV20 9a/37/c7/9a37c71ddc71a5608586f9ba639daef7
QNV21 45/15/59/4515594e372fa092ebe8cec84f3e2863
QNV22 fd/15/69/fd156940118fff835069689d417474ba
```
Fotos pelo visor noturno (reais), gráficos de jogo em verde neon (QNV7, QNV11 e QNV14) e produtos.
- **QNV2**: luneta noturna com a cruz e o ponto vermelho sobre um castelo japonês. Mostra o verde do fósforo, a granulação e a vinheta.
- **QNV3**: monocular noturno numa colina com traçantes e um sinalizador. Aparecem o brilho estourado, as estrelas e o ruído.
- **QNV8**, **QNV13** e **QNV21**: vinheta circular do monocular e dupla do binóculo, com granulação forte.
- **QNV5**: retículo âmbar sobre a imagem verde. Mostra o contraste do retículo com o fósforo.
- **QNV7** e **QNV14**: sobreposições de jogo em verde neon, com círculo, postes e BDC.
- **QNV10**: operador em multicam com óculos de quatro tubos (tipo GPNVG) e a lanterna da arma acesa, tudo em verde.
- **QNV12**: noturno com contorno laranja nas pessoas (fusão com térmica, realce de borda), com a marca d'água do TikTok @spicyboi93.
- **QNV4**, **QNV16** e **QNV11**: noturnos com marcações de HUD por cima.
- O resto: QNV6 e QNV19 são miras noturnas digitais (produto). QNV17, QNV18 e QNV22 são cenas militares. QNV1 repete QRT9, QNV9 repete QRT13, QNV15 é o mesmo monocular térmico de QTH9 e QIR14, e QNV20 repete QRT17.

#### QTH: "thermal scope view"
- Código **QTH** · busca `thermal scope view` · https://www.pinterest.com/search/pins/?q=thermal%20scope%20view · 23 pins na ordem servida; a API mandou 28 · coletada em 2026-09-28 05:39 UTC
- Fora da lista (a API mandou, a página pública não desenhou): posição 16: pin 4608800996756171840 (`91/cc/06/91cc068ca53c5b6296575da4c342e1e0`); posição 17: pin 4590575472448318336 (`f0/12/90/f012908b70be295a41c1a6987789096c`); posição 18: pin 4590645871335905152 (`22/79/ff/2279ffe8cb89055c5c826d9e40023efc`); posição 19: pin 4607886187558004096 (`53/aa/2c/53aa2c12fbf8077a6120528ea37cf9e0`); posição 20: pin 4602397447763666560 (`fa/fc/89/fafc89c5170cbe68665c89ce01b908d4`).
- Lista ordenada (código, caminho da imagem depois de `i.pinimg.com/originals/` ou `/736x/`):

```text
QTH1 22/ab/02/22ab023a21fb3579229152dc48adf038
QTH2 8b/ea/3f/8bea3fa66d99b99f0ac702a258b3ea06
QTH3 00/fe/79/00fe79c1e5dec83c034661f123053cbb
QTH4 04/4d/04/044d04a76f695d2785e3b12ef56bd349
QTH5 f9/4a/a0/f94aa073a032497313d61502623e9fb8
QTH6 89/b1/0d/89b10d3e16f8d1298eab21159cd0b781
QTH7 21/0e/14/210e14d615eb08a007031583325292e4
QTH8 9a/6f/86/9a6f868922968575af8e7f7d500c7392
QTH9 27/f4/54/27f4544dff4efc1c3d9045add3d8760d
QTH10 01/13/36/0113367f590124b8b696a38556e3e3ed
QTH11 6b/16/f0/6b16f03cdab14a4d145e0b0bdefeefab
QTH12 3b/11/3b/3b113bf5ff370de7bce32b438599dcae
QTH13 fc/17/a2/fc17a233e01139249997e4e9010406dd
QTH14 59/8a/06/598a06fa91bf3ade6d8cb69c1c533cf3
QTH15 a1/07/3f/a1073fac5baddc5b2e58d407f3b30187
QTH16 75/af/ae/75afae768c1f8232aa298c78204d8ea9
QTH17 f0/12/90/f012908b70be295a41c1a6987789096c
QTH18 48/26/11/482611214a067052a7e12c95f1c90205
QTH19 d5/70/03/d57003b679db1ecd50d97cd220fdd672
QTH20 9a/37/c7/9a37c71ddc71a5608586f9ba639daef7
QTH21 bc/51/0c/bc510caf079c9db52620a2f9a4675ca9
QTH22 50/cf/f9/50cff92b0df50e9cd7d9f2a67e5d8148
QTH23 50/13/37/501337aad127c74ed2595a856afeca36
```
Imagens térmicas reais (paletas branco-quente, ironbow, arco-íris e red hot), telas de câmera, produtos, e uma imagem que parece de jogo (QTH2).
- **QTH2**: térmica ironbow (laranja e amarelo sobre azul e roxo) de um soldado, com a cruz e cantos verdes de enquadramento. Parece arte de jogo ou render. O rosto e os olhos estão mais quentes.
- **QTH3** e **QTH4**: térmica real em paleta roxa, laranja e amarela, de uma pessoa armada junto a um carro (rodas e frente quentes), e de um grupo de cervos.
- **QTH5**: câmera térmica de helicóptero da polícia (crédito: West Midlands Police, Flickr), em branco-quente. O HUD tem a linha de modos no alto ("HDIR MFOV", "Auto Mod", "Wht", "DDE", "GeoPnt"), a fita de rumo, as escalas de elevação e azimute, a cruz com cantos, e embaixo as coordenadas, a distância, a data e a hora.
- **QTH13**: tela de uma luneta térmica Nocpix (marca visível). A imagem é cinza, com cervos, e em volta ficam os ícones (3x, hora, Wi-Fi), a escala curva verde de inclinação e "100m Profile1". É o melhor HUD térmico moderno do board.
- **QTH18**: câmera "MicroCAM" em branco-quente de um soldado com fuzil, com "x4", "Auto Gain" e cantos.
- **QTH19**: paleta arco-íris: fundo azul, rosto vermelho e amarelo, supressor quente.
- **QTH6**: luneta térmica com o alvo destacado em vermelho sobre o branco-quente (red hot).
- **QTH7**: luneta vista por trás, com a cidade desfocada em volta e a imagem noturna azulada na ocular.
- O resto: QTH1, QTH8, QTH11 e QTH21 são branco-quente (rua, ponte, pessoa, atirador ajoelhado). QTH14, QTH16, QTH17 e QTH23 são miras térmicas de produto. QTH9, QTH10, QTH12, QTH15, QTH20 e QTH22 se repetem em QNV e QRT.

#### QLS: "laser sight beam smoke"
- Código **QLS** · busca `laser sight beam smoke` · https://www.pinterest.com/search/pins/?q=laser%20sight%20beam%20smoke · 24 pins na ordem servida · coletada em 2026-09-28 05:39 UTC
- Lista ordenada (código, caminho da imagem depois de `i.pinimg.com/originals/` ou `/736x/`):

```text
QLS1 e7/66/92/e7669215a16a2e352b5f9f2902aec0c7
QLS2 9a/37/de/9a37decefec709d862e91e52627e6139
QLS3 6b/09/af/6b09afe29bd5ab43b845b1010d7c061e
QLS4 e0/f4/63/e0f4635b1d3b4ee7ad05a34433297859
QLS5 43/72/98/4372980cfac5aa3777b2f4028e965ce2
QLS6 6a/13/5d/6a135de0ad6efada3e83ece785a98ce0
QLS7 81/e1/71/81e1715756eb68364ba350b6d7e171d2
QLS8 bb/26/60/bb266037eace6514a2271525b05237de
QLS9 ef/4f/49/ef4f49d7d713843fe80d6ca98f89cae7
QLS10 fe/d3/ed/fed3ed5250393e2375cf7d0164e9bc4b
QLS11 70/c7/b2/70c7b206c9496efce787dcbaff042bef
QLS12 82/98/c8/8298c888cbd69c654ee49d0cf24d1966
QLS13 91/73/91/9173915f63f9b9cab2ed722b71387336
QLS14 20/09/87/200987367f11d03bf6a9f38566c02a7c
QLS15 0b/57/12/0b5712e77c435e0dcef355f886e0a7a9
QLS16 f9/e1/68/f9e168fad6ec3ef6de6cc4e5fa89d931
QLS17 8a/37/65/8a376537a88eda0f7745321d8356134e
QLS18 ac/3e/c9/ac3ec955938d629c188ca43209b3c9fb
QLS19 62/9b/81/629b8124d40784e87b846d2264128982
QLS20 5c/0f/d7/5c0fd73ffc9d27409b53c6f310437f19
QLS21 ed/f0/81/edf08135dda0ac514ba8c3cc1af47419
QLS22 1e/71/f3/1e71f3277b15c8f2afd6c9ec6cbb1421
QLS23 c1/19/e1/c119e1512d7c652f15472c1980e7e930
QLS24 70/11/ca/7011ca82195f7934bd8671609517114f
```
A maioria é laser de show, de ponteiro ou de banco de imagens. Só três pins têm laser montado em arma: QLS2, QLS15 e QLS18.
- **QLS1**: feixe verde grosso na fumaça, visto de perto da fonte, com turbulência e uma estrela de brilho na saída.
- **QLS2**: pessoa agachada junto a uma fogueira, com um fuzil em pé apontando um laser verde para o céu. O feixe fica fino e reto e some na distância.
- **QLS15**: AR com um módulo de laser vermelho no escuro, com o feixe visível e o ponto de saída brilhando.
- **QLS18**: homem com um AR (mira holográfica) e laser verde de arma, num estúdio escuro.
- **QLS5**, **QLS12** e **QLS20**: sprites de feixe em PNG, com o núcleo claro e o halo, em vermelho e azul. Mostram como se desenha o feixe em 2D.
- **QLS7** e **QLS23**: feixes vermelhos finos na fumaça, com o ponto na ponta.
- **QLS9** e **QLS14**: laser verde num ambiente escuro, com o ponto na parede.
- O resto: QLS3 e QLS4 são shows de laser. QLS6, QLS8, QLS11, QLS13 e QLS16 são ponteiros. QLS10 e QLS22 são lasers apontados para a câmera. QLS17 é de banco de imagens, com marca d'água. QLS19 é uma arma laser militar em teste. QLS21 é uma festa. QLS24 é o disparo de uma espingarda, sem laser.

#### QIR: "ir laser night vision rifle" (redação adaptada, complementa QLS)
- Código **QIR** · busca `ir laser night vision rifle` · https://www.pinterest.com/search/pins/?q=ir%20laser%20night%20vision%20rifle · 23 pins na ordem servida · coletada em 2026-09-28 05:51 UTC · redação adaptada
- Lista ordenada (código, caminho da imagem depois de `i.pinimg.com/originals/` ou `/736x/`):

```text
QIR1 f1/ba/0c/f1ba0cced6ee5f833260f5db948700ee
QIR2 c5/81/33/c58133d2ed4b888ce0b7cd91427f1b1e
QIR3 02/7b/c8/027bc88c048f822c9cd156693f945055
QIR4 c9/09/a2/c909a2370b551c38aa7be345bcba7e99
QIR5 bc/8e/13/bc8e13a4c23772bc94cc54187a4816be
QIR6 89/39/19/893919d1a75d81656b0a8ca2d0d9a8e6
QIR7 b3/a8/66/b3a866377060a51e88fc40f635727cf8
QIR8 54/f8/00/54f800496418ed5f145ab1c11924b832
QIR9 32/32/3e/32323e369efe96fe642f1efedddd39db
QIR10 7c/9c/9d/7c9c9d43e147f0533fbe3436fd8782ea
QIR11 b3/89/ea/b389ea7ae6c0d3a8944792a85b55cef3
QIR12 9b/0c/16/9b0c16dde5b2495430deee3f19f4f2bc
QIR13 af/ce/ee/afceeeb5c1257991dc4d42eadd37f107
QIR14 27/f4/54/27f4544dff4efc1c3d9045add3d8760d
QIR15 9a/89/c3/9a89c396068629e95b09a6b490d9cc06
QIR16 a2/49/4c/a2494c5006e0e4f7a52f0397b11d2381
QIR17 e1/67/b0/e167b02663544ee9175bc6815984523c
QIR18 47/98/48/4798487e1a2d8c3c80d474e696bf9ec0
QIR19 6a/ad/97/6aad9784f925b79326a1a2220b135ef5
QIR20 2b/6a/a7/2b6aa7d7e7d6020c8f0018f4fa3599f8
QIR21 b5/c9/8d/b5c98d0adeca645f9752663ff9af7bd1
QIR22 96/c4/25/96c4257bf08a879ef90ebe5b77aa15fe
QIR23 95/09/06/9509068093bb1f8c9a8ff7ca1796ff68
```
Quase só módulos de laser e iluminador (produtos reais e réplicas: US Night Vision, Steiner, Burris, "TRIAD", "SNIPER", SOTAC e Laserspeed). Não trouxe o feixe infravermelho visto no noturno.
- **QIR2**: caixa de laser tan ("US Night Vision Designate-IR") com a etiqueta "DANGER", o seletor giratório OFF, VIS e IR e a pilha CR-123, ao lado de uma lanterna. É o melhor pin para a etiqueta e o seletor.
- **QIR6**: módulo "TRIAD" visto de cima, com o seletor (OFF, V, IRL, IRH), o botão "FIRE" e a marca da pilha CR123A.
- **QIR1**: o mesmo módulo "TRIAD" num render com dois feixes verdes.
- **QIR17**: mira térmica com as peças nomeadas: Integrated Lens Cap, Optional RMR Sight, Focus Adjustment Knob, Laser Aperture, Zoom Control, Polarity Switch Black Hot/White Hot, Scene Calibration (NUC), Video Output and External Power Connection, Laser Control, Laser Pressure Switch e Rail Mount.
- **QIR18**: ficha do "LS-M6", da Laserspeed, que junta laser visível, laser IR e iluminador IR. Medidas: 106 × 62 × 42 mm, menos de 243 ± 5 g, alumínio 6061-T6 com anodização dura, uma pilha CR123A, IP68. Laser verde de 520 ± 10 nm, vermelho de 635 ± 20 nm e IR de 830 ± 15 nm. Ajuste de 0,16 mil por clique, 20 mil de curso.
- **QIR5**, **QIR7**, **QIR8**, **QIR9**, **QIR15** e **QIR20**: módulos de produto, em preto e tan. QIR8 tem a marca Steiner.
- O resto: QIR10 e QIR11 são réplicas "DBAL-A2" (SOTAC e caixa). QIR16 são óculos de quatro tubos tan. QIR21 é uma coleção de módulos e lanternas (OFFGRIDWEB). QIR3 é um laser Burris com red dot em cima, e QIR4 é o anúncio "SNIPER FL3000+TR20". QIR12 é uma luneta tipo Elcan. QIR13 é uma mira noturna com o iluminador aceso. QIR14 repete QNV15. QIR19 é um laser de pistola. QIR22 é um monocular térmico. QIR23 é uma luneta de caça com lanterna.

#### QWL: "weapon light rifle"
- Código **QWL** · busca `weapon light rifle` · https://www.pinterest.com/search/pins/?q=weapon%20light%20rifle · 23 pins na ordem servida · coletada em 2026-09-28 05:39 UTC
- Lista ordenada (código, caminho da imagem depois de `i.pinimg.com/originals/` ou `/736x/`):

```text
QWL1 03/5d/0a/035d0a371905d7dcd3817aca7645e310
QWL2 7e/48/20/7e48209c3adceae3849851b4419ffc64
QWL3 ec/e8/bc/ece8bc89a35c64f75077716b5ccee71e
QWL4 d0/c1/db/d0c1db1ea1e901cef0b9cd7de39a26e6
QWL5 00/94/2b/00942b521196a6ba263918a1c04337aa
QWL6 80/37/8e/80378e4f9bf9cc764759ddb826b7365b
QWL7 74/b6/be/74b6be2f19cac871e8ee2c1f78b4e29d
QWL8 19/b6/42/19b64201a7b032f6e1f7754c6eb7483c
QWL9 f2/0b/2c/f20b2cecd8ad31fb96f26b46ffa3485e
QWL10 f2/ca/0c/f2ca0cd21d16abe7a24ed7baa17eaae3
QWL11 85/f3/da/85f3dacd27cffa75dd7977135b86546d
QWL12 74/ed/0b/74ed0becde9b987765ca422992fa1a0f
QWL13 b2/15/ce/b215ce938602b04bac90eefe8cbaceb8
QWL14 e8/b4/79/e8b479f10ac5e9a33cb300d3f12fd278
QWL15 d1/48/84/d14884c29049d48dff14466c6119ae9e
QWL16 06/98/a4/0698a4cceca6801435c68a6b3641bffe
QWL17 ec/e8/f3/ece8f39920236da51e10b56c7201e5fe
QWL18 ba/45/22/ba4522c0142c21e1ba0efc9e50e070fe
QWL19 fa/13/57/fa13573031e9baad5baf408729774783
QWL20 86/9b/5e/869b5ed4c1349e68616ef3be88d28a37
QWL21 0b/c5/29/0bc5297deb016ccbb79cee3338f2388b
QWL22 61/70/fc/6170fc5c5f933a667390a3d16ad3745d
QWL23 86/b8/7d/86b87d927ae007652fb96e972d5cad2e
```
Mistura concepts de ficção científica (arte de jogo e portfólio) com fuzis reais montados. Quase não tem close de lanterna, por isso a QFL complementa.
- **QWL3**: folha ortográfica de uma arma longa do jogo SHRAPNEL (logos SHRAPNEL e "Sperasoft, a Keywords Studio"), em quatro vistas sobre cinza. É o exemplo de folha de modelagem.
- **QWL4**: fuzil FDE curto (real) com lanterna, laser tan e supressor. Mostra onde a lanterna vai no trilho.
- **QWL2** e **QWL6**: concepts de ficção científica. QWL2 é um "RAIL GUN" em três variações com a mesma coronha. QWL6 traz "ECLIPSE FORGE TACTICAL" e "LAWSON", com as duas vistas espelhadas sobre fundo escuro com curvas de nível vermelhas. São layouts de apresentação de arma.
- **QWL11** e **QWL22**: a mesma ilustração de equipamento (fuzil com supressor e pistola com red dot sobre cinza) em duas versões. QWL11 traz os nomes reais em texto vertical ("HK416A5 5.56x45mm", "GLOCK 17 Gen5 MOS") e muitas etiquetas de peça. QWL22 troca os nomes por genéricos ("FX97", "F-08"). É o exemplo direto da regra do projeto de nomes genéricos.
- **QWL10**: fuzil de precisão de ficção científica em branco e verde escuro, com cara de skin de jogo.
- **QWL15**: lever-action tática em cerakote OD, com porta-cartuchos na coronha.
- O resto: QWL1, QWL12, QWL13 e QWL19 são renders e concepts. QWL5 é uma SCAR com lança-granadas, QWL7 é uma M249 ou Mk46, QWL8 é uma Tavor X95 OD, QWL14 é uma AUG FDE, e QWL9, QWL16 a QWL18, QWL20, QWL21 e QWL23 são fuzis montados. QWL1, QWL4, QWL9, QWL14 e QWL23 já estão no projeto (QHS6, QRS13, QVM6, QVM1 e QTM19).

#### QFL: "weapon mounted flashlight" (redação adaptada, complementa QWL)
- Código **QFL** · busca `weapon mounted flashlight` · https://www.pinterest.com/search/pins/?q=weapon%20mounted%20flashlight · 22 pins na ordem servida · coletada em 2026-09-28 05:51 UTC · redação adaptada
- Lista ordenada (código, caminho da imagem depois de `i.pinimg.com/originals/` ou `/736x/`):

```text
QFL1 b6/ac/ae/b6acae1986434787343d17c275f6e2f5
QFL2 35/a3/c2/35a3c2e20f739f592eb872fb225b0c48
QFL3 3c/fb/2c/3cfb2c39cfd9c7eb616ae2405aaad49c
QFL4 3d/9e/55/3d9e5519a2d8df9bb58dd14d12027c2e
QFL5 9e/fb/69/9efb693a6d995c2a8358e4e7e79938da
QFL6 d9/c9/7f/d9c97f0b15450009159f79cb2062eee8
QFL7 b1/8c/92/b18c92251a6b8f791ec5fa0b8779543f
QFL8 ce/90/40/ce90400e4f0bd04b91bb3bb958540c46
QFL9 4a/16/b8/4a16b87e6e67730136310bc1a222757b
QFL10 b9/a7/d3/b9a7d3c9d286a157fd563c89f65b3d88
QFL11 02/ed/e5/02ede5c603e541982fc3d9f23c40d74d
QFL12 42/48/e0/4248e0efe7406125556bd1952d7db805
QFL13 6a/6e/d2/6a6ed2eeff750b75a49645c5a8ba43da
QFL14 ff/f3/40/fff3402dff000b8b394cd660a3d2a465
QFL15 10/c0/9b/10c09b03e147c174e547575e5b7ffca1
QFL16 d7/9e/d3/d79ed359837379523906befa3cb9ad99
QFL17 40/20/f2/4020f265e6fee3fb2a11da390dc3fb06
QFL18 b0/0f/a0/b00fa02d96000ae21f805ae914e1788f
QFL19 3e/44/72/3e447272960d5027617577e5e3ccb393
QFL20 c2/0d/b6/c20db651abb87b24309af1234e36d74f
QFL21 2c/57/ee/2c57eedc847bc59ab136e40355e3a1c2
QFL22 28/18/ca/2818cad427c1f8957e46cd1e1133b39a
```
Produtos reais (SureFire, Inforce, Streamlight e Olight) e réplicas.
- **QFL1**: duas lanternas tipo scout, preta e tan, em bases deslocadas, com o interruptor de pressão remoto e o cabo. Tem o texto "Constant the pressure switch" (loja Hunting World Club).
- **QFL4**: guarda-mão SureFire com a lanterna "Scout Light" embaixo (marcas legíveis) e o cabo do interruptor, de lado.
- **QFL3**: lanterna compacta num trilho projetando o facho no chão, com o centro claro e a borda do facho.
- **QFL2** e **QFL16**: lanterna acesa em fuzil tan, com o brilho da lente e o vidro vermelho do red dot.
- **QFL13**: Inforce (marca), uma lanterna compacta de polímero em preto e em tan.
- **QFL17**: Streamlight TLR-7 sub (marca), lanterna de pistola.
- **QFL10** e **QFL21**: Olight (marca), lanterna de pistola com laser verde, em azul, preto e tan.
- **QFL11**: mão segurando uma pistola com red dot e lanterna acesa, em estúdio escuro.
- **QFL12**: fuzil visto de frente, com lanterna e laser. É a silhueta frontal.
- **QFL15**, **QFL19** e **QFL20**: lanterna com caixa de laser, etiquetas, cabo e supressor FDE.
- O resto: QFL5 é uma base giratória. QFL6 é uma cabeça com várias lentes. QFL7 é uma Streamlight tan com braço flexível. QFL8 e QFL14 são fuzis montados. QFL9 é uma lanterna num guarda-mão de trilhos. QFL18 é uma lanterna com interruptor de cauda. QFL22 é uma coleção de lanternas.

#### QPR: "pistol red dot optic"
- Código **QPR** · busca `pistol red dot optic` · https://www.pinterest.com/search/pins/?q=pistol%20red%20dot%20optic · 25 pins na ordem servida · coletada em 2026-09-28 05:39 UTC
- Lista ordenada (código, caminho da imagem depois de `i.pinimg.com/originals/` ou `/736x/`):

```text
QPR1 83/44/d9/8344d9ef724d512a2092e216e60428bb
QPR2 10/aa/d7/10aad7ca73bac602a91e3ba47bfa70cf
QPR3 ed/e9/15/ede915020d756be4b604d25659871ad9
QPR4 80/9e/6d/809e6dec10d04fee24a3cb664c2068cf
QPR5 6e/bb/12/6ebb1265f3964b051863ea6b78b7fced
QPR6 10/6e/3e/106e3e67556401b50b417ce6574e800b
QPR7 5f/06/31/5f06312ea48842f0eeb7c6be0f69d784
QPR8 c7/ba/5f/c7ba5fda84796f0a31f6c84034a9409f
QPR9 19/f3/92/19f392d5c7c76467057024496adf03ae
QPR10 c1/c4/7c/c1c47cdd5a45244be1b475d1ef3007ca
QPR11 11/ad/30/11ad3080515df1b68211afc1d43ce122
QPR12 f4/07/d2/f407d2ee7905373214428bbae3d83129
QPR13 3a/75/ba/3a75ba909ced6782968045bab43648ff
QPR14 84/b7/82/84b78204d6db0e554165262f308d5db9
QPR15 ea/0e/fb/ea0efb26f20c273632a61cdf3321e3a6
QPR16 6a/bd/fc/6abdfc543d26f567874d8725029e994e
QPR17 1f/ed/34/1fed348b5a185faacc5f1d453b836885
QPR18 bf/80/91/bf80911fcac75ae422cffe94a530fbd4
QPR19 1a/b2/2f/1ab22f764e75777ff4885757edd5ba3b
QPR20 a3/47/cd/a347cda8c5ea3a8fded85b6d42dc3d05
QPR21 16/5a/0b/165a0b5bfbf1e22aeac77cae9f6b1ed2
QPR22 fa/95/3e/fa953ee9d89f4da98364a995385ae7be
QPR23 76/e5/29/76e52928ffec4b99f0b5efe504155c15
QPR24 e5/42/4b/e5424bc94e4a96807851fe0af791ea69
QPR25 57/81/06/578106861629202f78fc8715ebd3d107
```
Produtos reais: Trijicon, Leupold, Holosun, Swampfox, Sig, Vortex, CZ e Streamlight. Um terço do board repete miras de fuzil.
- **QPR5**: Trijicon RMR (marca, "RM02", "MADE IN USA", "1 CLICK = 1 MOA", seta "UP" e "R") fresada num ferrolho prateado, com a alça de mira logo atrás. Mostra como a mira entra no ferrolho.
- **QPR3**: Leupold DeltaPoint Pro, com "LEUPOLD", "DP-PRO", "1 MOA", "UP" e "CLICK" gravados e o vidro amarelado.
- **QPR10**: Holosun "EPS CARRY", fechada, com vidro laranja.
- **QPR11**: Swampfox (marca), aberta, com vidro laranja.
- **QPR13**: Sig (logo), fechada, com o vidro em tom verde de arco-íris e três botões.
- **QPR18**: Vortex (marca), reflex com as setas "UP" gravadas e vidro laranja.
- **QPR25**: Sig ROMEO3 (marca), aberta.
- **QPR6**: CZ Shadow 2 com empunhadura de alumínio vermelha de hexágonos, um canivete vermelho e a lanterna Streamlight "TLR-1 HL". A arma e a faca combinam na cor.
- **QPR9**: Glock com o ferrolho gravado com ideogramas chineses pintados de vermelho.
- **QPR22**: CZ Shadow 2 com empunhadura preta com caveira vermelha.
- **QPR17**: foto de produto em fundo vermelho escuro, com pistola e red dot.
- O resto: QPR1 repete QHO19, QPR4 repete QRD7 e QPR8 repete QRD18. QPR7 é a ROMEO4S. QPR2 é a traseira da UH-1. QPR12 são duas fechadas. QPR14, QPR16, QPR19 a QPR21 e QPR23 são miras de fuzil (EOTech FDE, Sig tubular, Vortex SPARC, Holosun 510C, EOTech com G33, ROMEO5 com JULIET). QPR15 e QPR24 são reflex baratas.

#### QAS: "ak side mount optic"
- Código **QAS** · busca `ak side mount optic` · https://www.pinterest.com/search/pins/?q=ak%20side%20mount%20optic · 24 pins na ordem servida · coletada em 2026-09-28 05:39 UTC
- Lista ordenada (código, caminho da imagem depois de `i.pinimg.com/originals/` ou `/736x/`):

```text
QAS1 60/53/24/605324a3728e39ccecc1bffc8cb54108
QAS2 71/07/6a/71076a43fc2089e1fa1ab051d0414e64
QAS3 b7/25/78/b72578aed8e9a123b2401cb51603993f
QAS4 6e/6d/79/6e6d79cf842b3ceb962b97d190c39993
QAS5 97/04/9f/97049f5c403317a355056c50d845e171
QAS6 ef/d8/50/efd850b63e0c519e6bdcd91dab90c950
QAS7 d0/f8/fb/d0f8fbe1143119d06d1dd3aa4dd745ab
QAS8 3c/30/8e/3c308e1bec3285404c3829c2e22a4914
QAS9 f2/fa/e1/f2fae12dc4346d9176a78bf5506278fb
QAS10 fa/93/84/fa93849465b4f27f10657143a80548b5
QAS11 1f/3c/2e/1f3c2e185d8459c6f094a07f42832548
QAS12 e3/6e/a0/e36ea0dac4338baab8c60f44620737de
QAS13 06/4f/16/064f16c39d2d314093cf2c43143b5a0d
QAS14 fd/5c/80/fd5c8032e8fa544a8840b0abf62ba7f8
QAS15 10/8f/c3/108fc3212e1b30e1e2599eeb426e5960
QAS16 39/a3/f8/39a3f816a58a7e92c3d76c213620dd90
QAS17 d4/e7/af/d4e7af3a37f9d9efbae23d6d5388d0db
QAS18 b2/fd/40/b2fd407c7255a7b5e96d279b8cbabd5f
QAS19 bf/07/91/bf0791e75db405d2015a1b15c799248d
QAS20 0e/1b/c0/0e1bc065cddaafec139432b846923ca0
QAS21 ba/b6/be/bab6be900ed8f120e44ee7561a5abb4c
QAS22 33/72/5f/33725fb320c01ac5b9df942ab4b69dcf
QAS23 6a/14/18/6a14185ffab1c3a9a3bac3827c7f9fd8
QAS24 22/66/b0/2266b005b546f1a2599efb39a38222dd
```
AKs reais com a base lateral, uma luneta soviética e um pin de jogo (QAS10, "METRO KYIV").
- **QAS2**: base lateral de AK da Midwest Industries ("MI", "Midwest Industries Inc. Made In U.S.A." gravados). Mostra o braço em "A", o trilho em cima, a trava QD e o botão da cauda de andorinha. Sem a gravação, é o molde de uma base genérica.
- **QAS5**: AK de madeira laminada avermelhada com um micro red dot na base lateral, o braço passando por cima da tampa, em fundo branco.
- **QAS1**, **QAS3**, **QAS6** e **QAS21**: AKs com red dot na base lateral, mostrando a folga sobre a tampa.
- **QAS9**: luneta soviética 4x (tipo POSP ou PSO) com o desenho do retículo, a ocular de borracha e a tampa.
- **QAS11**: foto em primeira pessoa de uma luva segurando uma AK com luneta PSO na neve.
- **QAS10**: peça de jogo (logo "METRO KYIV"): uma mira improvisada de sucata, com anel e lente, trilho, braçadeiras de tubo e fios, vista de dois ângulos.
- **QAS23**: close da base lateral, com a cauda de andorinha e a alavanca.
- **QAS8**: AK com LPVO na base lateral e guarda-mão de madeira.
- O resto: QAS4, QAS7, QAS12, QAS13 e QAS15 a QAS20 são AKs variadas. QAS14 é um Aimpoint tubular. QAS22 é uma AK de madeira gasta com carregadores laranja e marcas d'água de oficinas. QAS24 é um fuzil com EOTech.

### Inferences
- **QRD, QHO e QPR (reflex e holográficas):** o vidro de toda mira real tem um tom visto de fora, âmbar ou dourado (QRD9, QRD21, QPR10), azul ou verde (QHO16, QMG12), e o retículo só aparece de trás (QRD1, QHO13). No Blender, isso pede um vidro com tinta e reflexo, e o retículo como um plano emissivo à parte, visto só pelo lado do olho. As gravações genéricas ("1 CLICK = 0.5 MOA", setas UP e RIGHT, em QHO1, QPR3 e QPR18) dão realismo sem logo e podem ficar. Os nomes, como EOTech, Vortex e Holosun, saem.
- **Mira apontada:** nas fotos pela mira a caixa fica desfocada e o retículo nítido (QRD2, QHO13, QRT3). A luneta tem o anel escuro de sombra do olho (QRT3, QRT5). Com ferro e ponto juntos, a massa de mira aparece dentro do tubo (QRD14).
- **ACOG e LPVO:** a ACOG se define pela cunha, pela fibra óptica em cima e pelo killflash (QAC1, QAC5, QAC17). O LPVO se define pelo anel com alavanca, pelos dois tambores e pela montagem de uma peça (QLP1, QLP24). A RMR ou a mini reflex em cima é o acessório de segundo nível mais comum (QAC4, QLP7).
- **Lupa:** o que caracteriza a peça é a base basculante com o botão de soltura, a dobradiça e o calço de altura (QMG18). As medidas da Vortex (QMG16) dão a escala: a lupa tem 4,3 pol. e o red dot tubular 5,6 pol.
- **Noturno e térmica:** o visual vem da paleta e do HUD. O noturno é fósforo verde com granulação, bloom e vinheta redonda (QNV2, QNV3, QNV8). A térmica vem em branco-quente, ironbow, arco-íris ou red hot (QTH3, QTH19, QTH6), com HUD de ícones, hora, zoom e inclinação (QTH13, QTH5). O retículo em âmbar se destaca do verde (QNV5).
- **Laser e lanterna:** o feixe só aparece no ar com fumaça ou poeira. O sprite tem núcleo claro, halo e o ponto na ponta (QLS1, QLS5, QLS7). Lanterna e laser vêm com o interruptor de pressão e o cabo (QFL1, QFL4, QIR2), que são detalhes baratos de modelar e leem muito bem em primeira pessoa. A ficha do LS-M6 (QIR18) dá a escala de um módulo: uns 106 × 62 × 42 mm.
- **AK:** a base lateral é uma peça própria, com braço, trilho e trava (QAS2). A mira fica deslocada para cima da tampa (QAS5). A luneta soviética com o retículo de chevrons (QRT13, QAS9) é o par natural da AK do jogo.

### Gaps
- Os modelos dos produtos só foram confirmados onde o texto aparece. Os demais são semelhança de forma, como "tipo ACOG" ou "tipo GPNVG".
- Nenhuma busca trouxe o feixe de laser infravermelho visto pelo noturno, o que existe em jogos como o Tarkov. QIR e QLS não resolveram isso.
- Não há referência de sombra do olho nem de paralaxe em red dot com medidas. Só fotos soltas.

## 3. UI de armeiro e menu de acessórios (QGU e QAM)

### Takeaway
As duas buscas trouxeram capturas de jogos comerciais identificáveis pelo nome do jogo ou pelos itens na tela (Battlefield 6, Call of Duty Modern Warfare/Warzone, Metro Exodus, Payday 2, Hunt: Showdown, Escape from Tarkov, Destiny, Call of Duty Mobile e Call of Duty: Black Ops II), concepts de portfólio e folhas de peças. Quatro pins se repetem entre os dois boards (QGU1, QGU2, QGU4 e QGU9 são QAM5, QAM6, QAM4 e QAM15). As referências se dividem em três famílias. A primeira é a bancada física, com a arma sobre a mesa ou na parede de ferramentas, que casa com o mapa `arsenal` e os boards QGW e QPB do projeto. A segunda é a fileira de encaixes com barras de atributo. A terceira é a roda radial.

### Cited Findings

#### QGU: "gunsmith weapon customization ui"
- Código **QGU** · busca `gunsmith weapon customization ui` · https://www.pinterest.com/search/pins/?q=gunsmith%20weapon%20customization%20ui · 23 pins na ordem servida · coletada em 2026-09-28 05:40 UTC
- Lista ordenada (código, caminho da imagem depois de `i.pinimg.com/originals/` ou `/736x/`):

```text
QGU1 4f/5b/03/4f5b03d1eb9c202ea600970896d40565
QGU2 a5/db/95/a5db95bb27a0fba2f2385fb1760ffe43
QGU3 0e/a6/d0/0ea6d087605d3a693f04b72613a8bb57
QGU4 a9/f7/aa/a9f7aa13bc3302edd0e89b074541e56d
QGU5 e5/8f/eb/e58febbcd82286c09b6de362e6a1d215
QGU6 cc/d9/62/ccd962528b3e7de35ccfe80d7377ac39
QGU7 d4/a0/9b/d4a09b6b58865bf7f286ce24e1e02dd9
QGU8 2d/5b/b8/2d5bb8b56af67f8199792b988ba9e356
QGU9 73/c6/a1/73c6a147559d7c62381e27d580f77146
QGU10 fa/e1/50/fae15006691158dc30d791c258c27937
QGU11 d7/69/35/d76935f8f034e1c4eee9792b26f4e1ce
QGU12 08/e5/46/08e546aef27713f0f18252dd46dd00c5
QGU13 e0/b2/68/e0b2684f20d3f46a79091f7a70e961d2
QGU14 1b/a9/58/1ba958e37c5f9f9179a2fa4a3ffaade0
QGU15 5c/ca/26/5cca26e2dbe5ccc1fd4d872a7799dd47
QGU16 bc/1c/46/bc1c460d0a98ab41fcab6f4130aad8d4
QGU17 e8/b4/79/e8b479f10ac5e9a33cb300d3f12fd278
QGU18 4b/d3/30/4bd330627d2514aeefa15e228d03fee6
QGU19 92/d0/f2/92d0f257a10b6163694eb413b974fc25
QGU20 27/76/02/27760281ede1fa48a1f0812add1b950d
QGU21 c5/2d/72/c52d72018ee106e2b388592d0ffc9363
QGU22 5e/fa/20/5efa20679074a06a174d6e74b63d03ce
QGU23 ec/5f/d7/ec5fd7e8ac7b808166236d97b7ec1f5c
```
- **QGU6**: Battlefield 6 (o texto na tela diz "Battlefield™ 6"), tela "SELECT MUZZLE". O acessório em foco é o "LINEAR COMP", com a descrição ("Reduces horizontal recoil in favor of more stable vertical recoil. Soldiers firing will be spotted...") e os botões "EQUIPPED" e "FIRING RANGE". Embaixo fica a fileira de encaixes (FLASH HIDER, BRAKE, CONVERTOR marcado, BRAKE e SUPPRESSOR com cadeado e número de nível). À direita ficam os números (DMG 25, ROF 900, MAG 30) e as barras HIPFIRE, PRECISION, CONTROL e MOBILITY. A arma aparece num estúdio escuro com cortina de listras verde-água.
- **QGU1** (igual a QAM5): inventário de um jogo de tiro com RPG. O revólver "GOOD SAMARITAN" aparece grande, com os selos "ABYSSAL" e "REVOLVER" e "3,497 DPS". Atributos com ícone e barra: DAMAGE 519, RATE OF FIRE, ACCURACY 62 %, RANGE 43 m, CAPACITY 4. Três vantagens com ícone e porcentagem ("BREATH OF SCOVILLE", "HIGHNOON", "HEAVY METAL"), uma coluna de variantes à direita e, no rodapé, "FILTER OPTIONS · GUNSMITH · EQUIP · BACK".
- **QGU18**: Escape from Tarkov em japonês. À esquerda ficam o personagem e os encaixes de equipamento, no meio as grades dos contêineres e à direita o depósito em grade, cheio de armas. As abas de baixo são depósito, ガンスミス (armeiro), comerciantes e mercado.
- **QGU5**: matriz de peças de uma SMG. As linhas são Body, Grip, Magazine, Barrel, Sight, Stock e Accessory, e as colunas vão de 1 a 5, com ícones brancos sobre azul. É o sistema modular inteiro numa tela.
- **QGU19**: seis variantes do mesmo fuzil ("BASE", "BASE SUPP", "BASE GREN", "BASE SUPP GREN", "BASE DMR", "BASE SUPP DMR"). Mostra as combinações de acessório.
- **QGU16**: ilustração de maleta aberta com uma pistola tipo M&P (red dot, detalhes em bronze) e cada item nomeado na espuma: "TORQUE SET", "SPARE MAGAZINES (2 x 17-RD 9mm)", "CUSTOM CHAMBER FLAG", "ARMORER'S PUNCH / MAGAZINE TOOL", "CUSTOM BACKSTRAPS (INTERCHANGEABLE)", "BORE BRUSH", "PRECISION PERFORMANCE LUBRICANT", "BORE SNAKE" e "DEFENSE ROUNDS". É uma organização em estilo knolling, boa para uma bancada.
- **QGU2** (igual a QAM6): tela de loja de jogo mobile. "ASSAULT RIFLE 12K", "375 POWER", barras de atributo, abas por categoria (RIFLE, SHOTGUN, SMG, SNIPER), moedas no alto e o botão vermelho "FIGHT". Exemplo do que evitar se o objetivo é um visual sóbrio.
- **QGU8**: tela "CUSTOMIZE LOADOUT" em holograma azul, com itens do Call of Duty: Black Ops II: PRIMARY M27, "Millimeter Scanner", SECONDARY Titus-6, "Attachments not available", "XM31 Grenade", "EMP Grenade" e "Access Kit". O nome do jogo não aparece na tela.
- **QGU15**: armeiro do Call of Duty Mobile em espanhol ("ASM10 ARMERÍA"). Os encaixes ficam em volta do fuzil, ligados a ele por linhas: Boca de cañón, Cañón ("Ranger OWC"), Mira ("Mira de punto rojo clásica"), Culata, Ventaja, Láser, Acople, Munición ("Cargador ampliado a 33 balas") e Empuñadura trasera. À direita ficam os atributos (DAÑO 34, CADENCIA 55, PRECISIÓN 75, MOVILIDAD 70, ALCANCE 54, Control 50) e os botões PERSONALIZAR, EQUIPAR e GUARDAR. É a referência mais clara de encaixes dispostos em volta da arma.
- **QGU23**: inventário roxo escuro com uma pistola 1911 e uma fileira de encaixes em ícones.
- **QGU4** (igual a QAM4): roda radial com "ROCKET LAUNCHER" no centro e as armas nos gomos com a munição.
- **QGU3**: três variantes de um fuzil de precisão ("GSRS 7.62x51mm", "GSR 7.62x51mm", "GSRM 7.62x67mm") de perfil sobre cinza.
- O resto: QGU7 são ilustrações de Glocks sobre verde-água. QGU9 é uma folha de ícones de arma. QGU10 é uma skin ornamentada de lâmina. QGU11, QGU12, QGU13, QGU14, QGU20 e QGU21 são ilustrações e concepts de armas. QGU17 é uma AUG FDE (já está no projeto como QVM1). QGU22 é uma ficha de RPG de mesa ("BREAK ACTION FAE REVOLVER").

#### QAM: "weapon attachment menu game ui"
- Código **QAM** · busca `weapon attachment menu game ui` · https://www.pinterest.com/search/pins/?q=weapon%20attachment%20menu%20game%20ui · 24 pins na ordem servida · coletada em 2026-09-28 05:40 UTC
- Lista ordenada (código, caminho da imagem depois de `i.pinimg.com/originals/` ou `/736x/`):

```text
QAM1 a2/32/3f/a2323fab9f472c400982f489c0234888
QAM2 62/39/09/623909488428ff1226c7ac574a5769a8
QAM3 4a/13/74/4a1374c829c6fe8581b26b4f3a53faf1
QAM4 a9/f7/aa/a9f7aa13bc3302edd0e89b074541e56d
QAM5 4f/5b/03/4f5b03d1eb9c202ea600970896d40565
QAM6 a5/db/95/a5db95bb27a0fba2f2385fb1760ffe43
QAM7 83/4c/b4/834cb465adcf91271086a72182f751af
QAM8 fa/df/37/fadf377642f20d70affc6f89a094fd5a
QAM9 f0/76/a8/f076a8c5f0777be865196d43b638f3dd
QAM10 96/b9/1f/96b91f16753f341d897eb2f7293ce70b
QAM11 4b/3b/0d/4b3b0d45230e280ec1219c453557f3e3
QAM12 8c/c2/6f/8cc26fe4ba59513d7779c5892abd5012
QAM13 7c/9f/46/7c9f469eea873a28c1045962a5360ab7
QAM14 64/c0/ae/64c0aeb502de42177aeac67375d0def3
QAM15 73/c6/a1/73c6a147559d7c62381e27d580f77146
QAM16 6e/c4/bb/6ec4bb1458575f8584499174ae36002b
QAM17 ce/2d/48/ce2d488880107a76bdbbeab11ef86644
QAM18 0d/ae/e5/0daee541922ced7f637fdfd135670d2f
QAM19 44/4e/ce/444ecedbb46d729ae3483a3240b1b5b5
QAM20 50/ff/e2/50ffe2b2fb08d8d264d3b06196637133
QAM21 ab/86/7b/ab867b3885895fde504b75e939054afc
QAM22 42/4a/cd/424acddd18b4b9c79ca632d588a0d269
QAM23 60/f0/97/60f097d71b840ff8cc2c674eefb745f4
QAM24 29/d7/0c/29d70c3b89581ae81c0cf5ffcf47abeb
```
- **QAM22**: bancada do Metro Exodus ("WEAPONS — TIKHAR"). A arma fica sobre a bancada numa sala de madeira iluminada por lampião, os acessórios ficam numa coluna de ícones à esquerda e os recursos no alto. O painel "WEAPON CLEANING" explica que a sujeira acumulada estraga a arma, e embaixo ficam o custo da limpeza, as barras ACCURACY e RATE OF FIRE e os atalhos "[F] CLEAN" e "[TAB] CLOSE". É a referência mais próxima de uma bancada física, dentro do mundo do jogo.
- **QAM23**: "BLACKMARKET: UAR RIFLE" do Payday 2. A arma fica pendurada diante de uma parede perfurada com ferramentas. Tem as abas de acessório (BARREL EXT, BOOST, CUSTOM, EXTRA, GADGET, LOWER RECEIVER, MAGAZINE, SIGHT), os cartões "MOD PREVIEW" e uma tabela com as colunas TOTAL, EQUIPPED e SELECTED: MAGAZINE 30, RATE OF FIRE 750, DAMAGE 55, ACCURACY 64, STABILITY 44 (+4), CONCEALMENT 19 (−1). Também mostra "Combat Sight — COST: $16,800", o aviso "THIS MOD IS INCOMPATIBLE WITH SOME GADGETS!" e "DETECTION RISK 14".
- **QAM7**: Call of Duty: Modern Warfare, com "WARZONE 2" e "Rank 116" na tela. As armas do equipamento ficam deitadas numa mesa acolchoada com munição, granada e sensor, e à esquerda ficam os cartões (Primary "Beekeeper A", Secondary "Clockwork A", Perks, Lethal "Thermite", Tactical "Heartbeat Sensor").
- **QAM16**: Hunt: Showdown em alemão ("BLUTLINIE", "JÄGER", "LADEN", "BIBLIOTHEK"). A lista de caçadores fica à esquerda, o personagem no centro, os encaixes ("AUSRÜSTUNG": Großer Slot, Kleiner Slot, Werkzeuge, Verbrauchsgüter) e as "UPGRADES" à direita, tudo num visual escuro e pintado.
- **QAM24**: Destiny, "PREACHER MK. 22 — SHOTGUN". Tem uma frase de descrição, "36 ATTACK", barras (Impact, Range, Stability, Reload), "Rate of Fire 65" e "Magazine 5", e a arma grande sobre cinza claro.
- **QAM1**: ficha de item "Atrox Mk II Tactical Axe" ("Rating 189", "Light Attack 71", "Heavy Attack 142"), com as vantagens, o painel "Actions" e o modelo 3D no centro.
- **QAM9**: concept "LOADOUT" com a pistola leve "STINGER-Z1" em laranja e branco. As categorias ficam à esquerda (RIFLES, PISTOLS, ADDITIONAL), a vantagem "HEAT SENSOR" e um texto curto no meio, as barras à direita (ACCURACY, DAMAGE, FIRE RATE, CONTROL) e os contadores embaixo (MAGAZINE 14, DURABILITY 38/42, RARITY GOLD).
- **QAM3** e **QAM20**: rodas radiais, uma em verde e roxo neon e outra com silhuetas brancas, ambas com a munição de cada arma.
- **QAM8**: um bullpup com as variantes em ícones brancos, cada uma em três tamanhos. É um guia de ícones de acessório.
- **QAM21**: concept de tela de celular, "SPEC OPS // GOBLIN", com "WEAPON STATS" (dano, alcance em pés, estabilidade +15 % para 24,3 %, zoom, pente, recarga) e o botão "UPGRADE NOW".
- **QAM19**: Call of Duty Mobile, arma secundária corpo a corpo. A faca base fica no centro, e a fileira de armas brancas embaixo (Base Melee, Knife, Wrench, Axe com cadeado, Shovel). Os atributos ficam à direita (DAMAGE 200, FIRE RATE 10, ACCURACY 70, MOBILITY 90, RANGE 10, CONTROL 70), com os botões GUNSMITH e EQUIPPED. É a referência para a escolha da faca.
- O resto: QAM2 é um HUD vertical de quadrinhos ("MOMENTUM"). QAM10 é uma tela "PRIMARY" com a lista de acessórios. QAM11 é um kit de HUD de sobrevivência. QAM12 é uma lista de armas mobile. QAM13 é um HUD escuro com roda. QAM14 é uma lista de armas em tema claro. QAM17 é um menu de skins em chinês. QAM18 é uma colagem de gameplay mobile. QAM4, QAM5, QAM6 e QAM15 repetem QGU4, QGU1, QGU2 e QGU9.

### Inferences
- **Bancada física:** QAM22 (Metro Exodus), QAM23 (Payday 2) e QAM7 (Warzone) põem a arma num lugar do mundo do jogo: a bancada com lampião, a parede perfurada com ferramentas e a mesa com os itens. É o mesmo caminho do mapa `arsenal`, com a bancada de armeiro e o quadro de ferramentas (QGW e QPB). A UI por cima pode ser curta: nome do acessório, uma frase, as barras e os atalhos.
- **Encaixes e atributos:** o padrão mais claro é o do Battlefield 6 (QGU6). Uma fileira de encaixes por categoria, com os bloqueados em cadeado e nível, o acessório em foco com uma frase sobre o efeito e o custo, e as barras que mudam com um sinal de diferença. O Payday 2 (QAM23) mostra os números TOTAL, EQUIPPED e SELECTED com o delta (+4, −1) e o aviso de incompatibilidade.
- **Sistema de peças:** a matriz de QGU5 (peça × variante) e as variantes de QGU19 e QAM8 mostram como documentar e mostrar os acessórios: silhueta branca da peça, em três tamanhos, dentro de uma grade.
- **O que evitar:** as telas de loja mobile (QGU2, QAM12, QGU15), com moedas, "POWER" e botões berrantes, fogem do tom de um set de stop-motion.

### Gaps
- Nenhum pin mostra uma UI de armeiro com visual de massinha ou de stop-motion. A ponte com o estilo do MASSACRE tem de vir dos boards de bancada (QGW, QPB, QTT) que o projeto já tem.
- Os nomes dos jogos vieram do texto na tela. QGU1 e QAM1 não trazem o nome do jogo.

## 4. Skins de armas e facas (QKS, QCW, QCR, QHD, QAT, QDM, QCH, QCC, QCO, QCP, QSC, QVW, QCT)

### Takeaway
Os boards de skin se dividem em três grupos. O primeiro são os acabamentos de jogo: CS2 e CS:GO, Valorant, Apex, Call of Duty e concepts. Eles aplicam um efeito de material (degradê, marmorizado, damasco, arco-íris) ou uma ilustração sobre a arma de fábrica. O segundo são acabamentos reais: cerakote, hidrografia, titânio anodizado, aço damasco e têmpera colorida. Eles dão paletas e padrões que existem de verdade, e dois gráficos de cores de revenido trazem as temperaturas. O terceiro são temas que casam com um mundo de massinha e estúdio: porcelana azul e branca (QKS14, QCW1, QCW3, QCW7, QHD1), arte de nariz de avião da Segunda Guerra (QCR5, QCR20, QCR25), camuflagem de manchas grandes com borda clara (QCP2), arma de giz de cera e de massinha (QCT2, QCT3), boneco pintado à mão (QCT1), curvas de nível (QCR7, QCR14) e pátina (QCR2, QCC5). O board QCR repete 10 pins do QCK que o projeto já tem.

### Cited Findings

#### QKS: "cs2 knife skins"
- Código **QKS** · busca `cs2 knife skins` · https://www.pinterest.com/search/pins/?q=cs2%20knife%20skins · 24 pins na ordem servida · coletada em 2026-09-28 05:40 UTC
- Lista ordenada (código, caminho da imagem depois de `i.pinimg.com/originals/` ou `/736x/`):

```text
QKS1 b0/cc/46/b0cc466368aed0d97b2a83bcf0272acb
QKS2 df/97/99/df9799de7828a6e8a4b8d1b19162afc5
QKS3 ce/94/16/ce94163869b8b8e6adc936d5f840e54e
QKS4 8e/7b/6e/8e7b6e24eee15e7997c1ea2f2b7f6106
QKS5 79/0b/bc/790bbc7718b8431dc264188a79204a19
QKS6 0f/c3/11/0fc31135a16e3aa73a0cd89606e75595
QKS7 42/7a/7f/427a7f7c10a9a6e6c96f031a5f27d9f6
QKS8 18/cf/c9/18cfc934ac4de46019d32c91915c55d5
QKS9 a4/62/d9/a462d9fdd2ba2815894db5a79e7f0e59
QKS10 e1/f5/96/e1f596ae49ca15b50a5204599862d7e8
QKS11 3d/81/8f/3d818f94912a4847e125fd771d3fb0bd
QKS12 85/c4/f2/85c4f2f492309cc15637598230d3d7d8
QKS13 a4/6c/e7/a46ce777d9da55e0dccd03a65144edd2
QKS14 f2/7b/58/f27b58b4afa554527d039c479cc0f6cf
QKS15 07/b0/af/07b0af6e53329a094d20506fb7083808
QKS16 ff/6d/59/ff6d59c2997d5a695e8b00205eb5c3aa
QKS17 ee/47/c7/ee47c7a6e1857fa24c98ec7d91fa729c
QKS18 51/20/8f/51208fefb8e417207002213076e7522b
QKS19 08/b0/e5/08b0e5eba92d549cb5aa3954dfc8f723
QKS20 0e/57/31/0e57314288b68046f0f536f62dfc647e
QKS21 fb/e3/8e/fbe38e8729b23eb38b1cf04e333b9ed2
QKS22 b5/bb/37/b5bb372d847f212ab14fe3a4a72d7ed8
QKS23 73/17/38/731738c84a59f774eeb6fa68083b6e8e
QKS24 8b/c4/cd/8bc4cde41bfc27b8fc2bf49676e77e83
```
Tudo é arte de jogo (CS:GO e CS2) ou montagem de fã.
- **QKS1**: imagem oficial "Introducing the Chroma Case knife finishes" (logo do CS:GO). Cinco modelos de faca, cada um com seis acabamentos nomeados: Damascus Steel, Doppler, Marble Fade, Tiger Tooth, Rust Coat e Ultraviolet. É o mesmo acabamento aplicado em lâminas diferentes, a lógica de um sistema de skins.
- **QKS6**, **QKS13**, **QKS15** e **QKS20**: degradê rosa, roxo e amarelo tipo Fade em baioneta M9 e canivetes.
- **QKS3**, **QKS5**, **QKS12** e **QKS18**: marmorizado azul e violeta tipo Doppler. QKS3 aparece na tela de inspeção do jogo, com o texto sobre a karambit.
- **QKS4**, **QKS8**, **QKS23** e **QKS24**: marmorizado verde-esmeralda tipo Gamma Doppler.
- **QKS10** e **QKS16**: padrão cinza ondulado de aço damasco (Damascus Steel).
- **QKS19**: marmorizado de três cores (vermelho, amarelo e azul) tipo Marble Fade.
- **QKS9**: canivete borboleta branco perolado com grafismos pretos, e o texto "PRINT STREAM".
- **QKS14**: luvas, AK e baioneta com o mesmo desenho de porcelana chinesa azul e branca, com dragões e nuvens. É um conjunto com tema de cerâmica.
- **QKS22**: baioneta dourada com ornamento gravado.
- **QKS11**: silhuetas pretas de todos os modelos de faca. Serve para a leitura de silhueta.
- **QKS21**: primeira pessoa no jogo, com a mão de luva segurando a karambit violeta num mapa com torre de resfriamento.
- O resto: QKS2 é um estilete vermelho marmorizado. QKS7 e QKS17 são montagens de fã com fundo escuro.

#### QCW: "cs2 weapon skins"
- Código **QCW** · busca `cs2 weapon skins` · https://www.pinterest.com/search/pins/?q=cs2%20weapon%20skins · 25 pins na ordem servida · coletada em 2026-09-28 05:40 UTC
- Lista ordenada (código, caminho da imagem depois de `i.pinimg.com/originals/` ou `/736x/`):

```text
QCW1 fd/2d/36/fd2d360d63f431823f99304793e1ee3c
QCW2 4b/c0/78/4bc078788e8fb98c4b667c2c995bc440
QCW3 37/2c/56/372c56a811fa98146976c64949bb5070
QCW4 8e/7b/6e/8e7b6e24eee15e7997c1ea2f2b7f6106
QCW5 df/97/99/df9799de7828a6e8a4b8d1b19162afc5
QCW6 3a/b4/1c/3ab41ce0690a63e83ff2b174ae9bda61
QCW7 20/3d/2c/203d2c79d23d74e7264449fdb8526bbe
QCW8 d3/c5/0a/d3c50a9303417a014f1478bdb4495801
QCW9 c1/03/ea/c103ea8f075ca1f57f6fec44b6b64364
QCW10 03/a6/24/03a624766cf7a5e55d32696a0fe9f867
QCW11 aa/63/82/aa6382fa64c4328ebbe554cbbde85bb7
QCW12 a9/99/97/a99997f94ded37bfae0b11d09d84fd85
QCW13 f6/0c/00/f60c0061f7d0543dde99c5fd67909600
QCW14 95/2a/24/952a2468d022304ae0e05ed2d1eeb66d
QCW15 8c/90/7d/8c907d2972a02375f73b467585318eeb
QCW16 cb/a5/27/cba52782bbb2332e11109de490534de3
QCW17 d1/3c/dd/d13cddba48caae86c37156eaa9a43df9
QCW18 e1/f5/96/e1f596ae49ca15b50a5204599862d7e8
QCW19 9d/b7/54/9db754b420013ba1401367addccd8b2f
QCW20 bd/7c/bb/bd7cbb1e3931301ff6e6d7ae55d0d6ee
QCW21 9b/9e/d0/9b9ed092db98fafc5a22b0e4ed972323
QCW22 9f/6e/3a/9f6e3adb9b8ea8a0d1fb2a034617cc66
QCW23 2a/77/19/2a7719d16a1e0692a170a9703d7f8f9f
QCW24 4b/76/29/4b7629d627ee927619bf1cbf8dbdc1eb
QCW25 b8/26/e6/b826e6bbe3acef45afe8e11a20180f25
```
Arte de jogo (CS:GO e CS2, oficial e da Oficina) e montagens. QCW14 e QCW24 parecem de outro jogo.
- **QCW1**, **QCW3** e **QCW7**: AK, Vector e Desert Eagle em porcelana azul e branca, com ramos e flores em cobalto. QCW3 e QCW7 estão na ferramenta de prévia, com os botões "Front" e "Back". É um conjunto de tema cerâmico em armas diferentes.
- **QCW13**: arte da caixa ("Spectrum Case") com "AK-47 | Bloodsport — Created by SLIMEface" escrito. **QCW6** é a mesma skin em papel de parede ("VOLTAIC" no carregador).
- **QCW19**: arte da caixa ("The Chroma 2 Case") com "Galil | Eco" escrito.
- **QCW2**: AK branca com uma ave desenhada a traço e a coronha preta com um disco vermelho, de tema japonês.
- **QCW25**: AK cinza (o modelo base) ao lado de uma peça pintada com flores. Mostra a skin como camada por cima da mesma arma.
- **QCW15**: AK em branco, laranja e preto, com grafismo de ficção científica.
- **QCW8**: USP-S branca perolada com grafismo preto.
- **QCW11**, **QCW12**, **QCW21** e **QCW9**: grafite e adesivos (tigre em amarelo e azul, rosa com grafismo, AWP em neon, M4 em preto e rosa de quadrinho).
- **QCW17**: SMG rosa com flores de cerejeira, uma raposa e um chaveiro.
- **QCW20**: sete skins de M4 em displays de acrílico (produto de fã).
- O resto: QCW4, QCW5 e QCW18 repetem QKS4, QKS2 e QKS10. QCW10 é uma AK verde com flores. QCW14 e QCW24 são fuzis com carenagem orgânica em branco e vermelho e em branco e verde, com brilho. QCW16 é uma M4 pastel com personagem. QCW22 é uma M4 dourada e preta. QCW23 é uma AWP roxa. QCW6, QCW10 e QCW15 já estão no QCS do projeto (QCS8, QCS3 e QCS11).

#### QCR: "custom cerakote rifle"
- Código **QCR** · busca `custom cerakote rifle` · https://www.pinterest.com/search/pins/?q=custom%20cerakote%20rifle · 25 pins na ordem servida · coletada em 2026-09-28 05:40 UTC
- Lista ordenada (código, caminho da imagem depois de `i.pinimg.com/originals/` ou `/736x/`):

```text
QCR1 8d/bf/39/8dbf3901f237998b092285055b94e5e7
QCR2 e7/3d/dc/e73ddcb2344a30fcdbcb9405b4cfa122
QCR3 59/4b/1a/594b1aaead1e8633cfee0c401ae3a86b
QCR4 a1/81/e4/a181e4c29f3ce99108c47623c2092d30
QCR5 b9/f8/81/b9f881cf826f448b71c072e02d0842d8
QCR6 de/16/dc/de16dcb43afde3169c9ac84c3ea73e4b
QCR7 ae/19/21/ae19216770c0aa398f71ca03d9bba7c8
QCR8 44/53/7e/44537e2ad7bf3ea802cacdbaeea89733
QCR9 35/62/01/356201857ba2b939a7ce41f8355948d2
QCR10 7d/c6/54/7dc654167ccf4b5b281d049c93089d63
QCR11 38/b4/41/38b4419d19827f6f494443953ba92308
QCR12 3f/4c/51/3f4c510657de4ed809b1844659f900dd
QCR13 3a/b6/0a/3ab60a9cd94cebcc4bd7cd8c673db409
QCR14 de/fb/0a/defb0a5883b01568a2558548576c1128
QCR15 48/83/3f/48833f2c394e7671613b09827a707c35
QCR16 28/80/d4/2880d486970f3c9ae8a81dfd2cc5175b
QCR17 44/76/86/4476864d857e0172e80c30075f12c157
QCR18 26/66/23/266623476ac570e32ca34814926e3bfd
QCR19 80/f1/07/80f1070dcf6692ee7a576f449979651a
QCR20 df/3c/6e/df3c6e8c59456c0ec9c02009fd62e424
QCR21 f1/9e/49/f19e49401f1fb69004044229b09f77f9
QCR22 b1/e2/5a/b1e25ad971e049f7f7b22141650ff31e
QCR23 7e/45/00/7e45005a59c978e022f3b3d516d4a546
QCR24 7d/7c/de/7d7cde053d8302fef604e7374a2c5a60
QCR25 af/15/99/af1599d05559d18fc4d8df25d9b88852
```
Trabalhos reais de cerakote e pintura. Aparecem as marcas d'água de Cerakote, Deadlock Coatings, GunCoat (GCNW), Cerakote Chick e reprif. Dez pins já estão no QCK do projeto (a lista está na seção 5).
- **QCR2**: Deadlock Coatings. AR pistola em turquesa gasto sobre cobre e bronze, com o preto aparecendo. É uma pátina de azinhavre, a melhor referência de desgaste colorido.
- **QCR5**: AR em OD com a boca de tubarão dos caças P-40 no poço do carregador, estrela branca, adesivos de furo de bala e empunhadura de madeira. Tema de arte de nariz de avião.
- **QCR20** e **QCR25**: espingarda cinza e pistola OD com boca de tubarão, xadrez amarelo, a insígnia de estrela da USAAF e a matrícula "A-126". É o mesmo tema.
- **QCR7** e **QCR14**: curvas de nível (mapa topográfico). QCR7 é tan sobre OD, com detalhes em cobre (Cerakote Chick). QCR14 é bronze sobre preto.
- **QCR1** e **QCR6**: padrão de rede ou pele de cobra em areia e oliva com linhas claras, cobrindo até a luneta. QCR6 é da GunCoat.
- **QCR4**, **QCR10** e **QCR22**: multicam preto e multicam árido feitos com máscara, com a camuflagem passando por cima das gravações (Cerakote).
- **QCR9**, **QCR12**, **QCR13**, **QCR19**, **QCR23** e **QCR24**: listras de tigre em várias paletas, de oliva e caqui a preto e vermelho. QCR24 tem uma caveira branca.
- **QCR15**: camuflagem de inverno em branco, marrom e areia, entre plantas secas na neve.
- **QCR21**: fuzil de precisão com chamas em laranja e preto (Cerakote).
- **QCR17**: pistola em rosa, verde-água e preto (Cerakote).
- O resto: QCR3 é um multicam escuro num palete. QCR8 é vermelho gasto sobre preto, com grafismos. QCR11 é cinza urbano com caveira. QCR16 é preto com vermelho. QCR18 é um fuzil de caça camuflado.

#### QHD: "hydro dipped gun"
- Código **QHD** · busca `hydro dipped gun` · https://www.pinterest.com/search/pins/?q=hydro%20dipped%20gun · 24 pins na ordem servida · coletada em 2026-09-28 05:40 UTC
- Lista ordenada (código, caminho da imagem depois de `i.pinimg.com/originals/` ou `/736x/`):

```text
QHD1 7f/28/91/7f28913bd3f0cd3526b46f33799cd36f
QHD2 7c/bb/18/7cbb18627d89e8d570325f576560567c
QHD3 e6/a5/29/e6a52983c4dff928a45a646242d9b6c5
QHD4 44/a9/e2/44a9e2b895d265edc0bfabfb5d1cd13c
QHD5 16/2f/91/162f910d425274d6f768182142b285ce
QHD6 53/b8/d3/53b8d327b9174db89fc9c54dae4bcf6e
QHD7 dc/aa/be/dcaabeed36b07c380f3ac14f52b95781
QHD8 9c/40/31/9c40314d7a431d9bb8d0d586e8df6118
QHD9 1d/54/82/1d5482f03d09c5b67f655520bf131737
QHD10 d4/45/b1/d445b17d3ed0a02375f2431857bcd938
QHD11 71/1f/37/711f37c7bb4218cdf682e762e4eaa9ed
QHD12 db/67/f9/db67f950ce918fa69c3683af5e345e2e
QHD13 00/0f/96/000f966617831e2f194cbf42bfe7a676
QHD14 5a/79/f2/5a79f2c4229b6382df20778875f6bcd8
QHD15 aa/1d/31/aa1d31731444692e35f0a251cf4835e1
QHD16 ba/1b/b2/ba1bb2bf863fb7d15fe83f3486cea0e4
QHD17 cc/f7/b5/ccf7b53f612e57d6dd8dbdf04a5108fb
QHD18 15/94/0f/15940fcb1f5f24257477acf9117d014a
QHD19 fa/e4/15/fae4154b08b30c17bff6b23b44a9df4a
QHD20 bd/2f/1c/bd2f1c59e94b6b9d11ee7d247b9f5083
QHD21 d4/7e/25/d47e25c792e43aec269d45179dd2158d
QHD22 25/69/ba/2569ba8af0d2d2b1735dcd751d886371
QHD23 f7/e2/fd/f7e2fd72fde95ba05f186057da90fa83
QHD24 49/df/ed/49dfed0162e7ce6dbaa51ebdb2b15ce2
```
Trabalhos reais de hidrografia e alguns de cerakote. Aparecem as marcas d'água de Cerakote, MAD Custom Coating, Intermountain Hydrographics e @Bullets_and_Burnouts, e o logo bordado da Ducks Unlimited num pano.
- **QHD1**: Glock em porcelana azul e branca (flores em cobalto sobre branco). É o melhor exemplo do tema cerâmico numa arma real.
- **QHD18**: Glock com estampa de vaca em branco e preto, detalhes rosa, lanterna e red dot.
- **QHD11**: pistola com estampa de onça-das-neves (Intermountain Hydrographics).
- **QHD9**: receptores de AR brancos com efeito de pedra e a boca de tubarão.
- **QHD7**: ferrolho e armação em turquesa com arabescos pretos, desmontados.
- **QHD14**, **QHD15** e **QHD17**: caveiras e ossos em verde neon e em cinza, uma estampa de película.
- **QHD12**: Staccato XL (texto visível) preta com respingos rosa e verde-água.
- **QHD4**: Glock em camuflagem rosa, roxa e ciano (Cerakote).
- **QHD2**, **QHD3**, **QHD8**, **QHD19** a **QHD21**: camuflagens digital, de montanha, de tigre urbano e de mata.
- O resto: QHD5 e QHD13 são padrões roxo e vermelho (MAD Custom Coating). QHD6 e QHD23 são multicam. QHD10 é verde metálico. QHD16 é uma estampa de personagem licenciado, a evitar. QHD20 é um AR em padrão de pele de réptil areia (@Bullets_and_Burnouts). QHD22 é vermelho com respingos. QHD24 é preto com verde-água.

#### QAT: "anodized titanium knife"
- Código **QAT** · busca `anodized titanium knife` · https://www.pinterest.com/search/pins/?q=anodized%20titanium%20knife · 23 pins na ordem servida; a API mandou 28 · coletada em 2026-09-28 05:40 UTC
- Fora da lista (a API mandou, a página pública não desenhou): posição 1: pin 4597471623627966208 (`76/50/07/76500752eba5f4b80b60fd2522f11944`); posição 2: pin 4605704790950213504 (`89/73/dd/8973ddb9e49fd483bdea09e955c65973`); posição 3: pin 4607675091199375232 (`ef/dd/39/efdd39dd70c0cee41f0c894bebc1e00f`); posição 4: pin 4591701426315960576 (`b7/b8/15/b7b815e315a66c4663f20faf487b8dcc`); posição 5: pin 4598949381117657216 (`f2/99/d1/f299d1184da1300d794594e81fadf017`).
- Lista ordenada (código, caminho da imagem depois de `i.pinimg.com/originals/` ou `/736x/`):

```text
QAT1 34/62/9b/34629b8c81bfbafd30860a9c93b4ee72
QAT2 55/30/0a/55300a79460c9aec07f0cd7f0d78fdc5
QAT3 c6/77/d7/c677d7438fe7eba3db6302e9ac041cdb
QAT4 1a/cc/a3/1acca3147104f20d6f3f99275b73c116
QAT5 86/f6/15/86f6152ccce2f3458ecb27754e62bd41
QAT6 42/81/a1/4281a1c43ad9227e484285b18c63313e
QAT7 db/f9/f5/dbf9f5fd62c85061d6a8d21a9a692da1
QAT8 bf/52/ef/bf52efa5edc293be867be8e9eb5c15d4
QAT9 80/7e/06/807e06ae5b0081640c282c6c686d767f
QAT10 21/a6/fc/21a6fcbf658e192dd0f4aa08e287c2d4
QAT11 10/a7/fd/10a7fde4b91dad25eff3dcc101f0053d
QAT12 f9/eb/49/f9eb495b75f3cd5fee3fd4f48501aa4e
QAT13 c1/67/3d/c1673d62d0a0a28eb83d5150de921477
QAT14 70/01/9d/70019df92c6c440252a0eb4842e90ded
QAT15 06/c2/cb/06c2cb54017e490960cc8f9cf803dc6a
QAT16 f4/5f/c4/f45fc443f95db9ad1e91eda71738ce67
QAT17 1d/ce/a2/1dcea25501acbc30e774ff1098382e77
QAT18 05/de/42/05de42a676933fd77a07f587d2bb0159
QAT19 ff/ee/58/ffee58699a638e6e651ab90ecbae7627
QAT20 70/20/94/702094603a4cbac372be336ad69f8b78
QAT21 83/23/3c/83233c811dbfad02cc1bacc6f25ef8ba
QAT22 3a/55/23/3a5523ecdb94da1ddd63d817e768673a
QAT23 fc/5e/40/fc5e40c931bcc7ad8f03bf1998f144c9
```
Facas reais. As cores vão do anodizado de titânio (bronze, roxo, azul) e do titânio queimado a chama a lâminas baratas de arco-íris contínuo, sobretudo QAT4, QAT7, QAT8, QAT9, QAT19, QAT20 e QAT22, com marcas como Timber Wolf e MTech.
- **QAT1**: barra de titânio queimada a chama, com manchas em azul, roxo e dourado.
- **QAT2**: talas de cabo em titânio azul e roxo com textura de "casca rachada" e toque bronze.
- **QAT3**: canivete fino com cabo de titânio damasco em azul e bronze e lâmina bronzeada.
- **QAT6** e **QAT15**: cabos de titânio damasco com manchas de arco-íris. QAT15 é um Spyderco, com a marca visível.
- **QAT10** e **QAT11**: facas de luxo com anodização azul e gravação à mão (créditos na imagem: Bali Ballistic / Jerry Hom e Hawk Knives; gravador Wilfred Valtakis II; foto SharpByCoop).
- **QAT12**: flipper de titânio cinza lavado com um único detalhe azul anodizado no pino.
- **QAT14**, **QAT17** e **QAT23**: cabos de titânio esculpidos em ondas, anodizados em rosa e em violeta.
- **QAT18**: miniatura "ANODIZE AT HOME", com pilha e béquer. A cor depende do banho elétrico.
- **QAT16**: cabo de titânio queimado a chama em listras de bronze, verde e roxo, com furos (Strider, marca na lâmina).
- **QAT13**: três canivetes borboleta de treino em arco-íris, roxo e preto.
- **QAT21**: canivete com anel, tipo karambit, em titânio roxo e cinza.
- O resto: QAT4 é a Timber Wolf de arco-íris. QAT5 são facas de arremesso com "HOW TO ANODIZE" escrito. QAT7, QAT8, QAT9, QAT19, QAT20 e QAT22 são canivetes de fantasia com dragões e chamas.

#### QDM: "damascus steel knife"
- Código **QDM** · busca `damascus steel knife` · https://www.pinterest.com/search/pins/?q=damascus%20steel%20knife · 24 pins na ordem servida · coletada em 2026-09-28 05:41 UTC
- Lista ordenada (código, caminho da imagem depois de `i.pinimg.com/originals/` ou `/736x/`):

```text
QDM1 60/5b/cb/605bcb3f01521042d2134d61d62ec433
QDM2 af/1d/4c/af1d4ca664edb439eed7c1856ee595c5
QDM3 c5/5d/4e/c55d4e4b10a33462fb67d119d617be73
QDM4 91/ff/3d/91ff3d6bd33e27fe96bb6acc81430bbf
QDM5 35/d6/08/35d608df07322fdfca3240b3a19d68d9
QDM6 62/d6/34/62d63484eb22d19121af533ddd4d4420
QDM7 c7/fb/db/c7fbdbc1e481e94a959f0b4ed705831d
QDM8 a4/6a/8e/a46a8e2dd2a42f0a560f63b968a64707
QDM9 ec/4e/ec/ec4eec8f23323105974a17fc644419b9
QDM10 a7/bd/9e/a7bd9e15378bcd763c5ce6422b67a87e
QDM11 30/73/73/3073730a0b9d37a27d176e48787e7b12
QDM12 ca/e7/91/cae79177422e28524eb5c5bca1920e58
QDM13 6e/7f/21/6e7f211b16215e1e408eb1590cadfab0
QDM14 fa/8d/ea/fa8dea9b0f0b868d2e4c49e1fc439076
QDM15 6b/a0/7d/6ba07d8f4ca13ca0021da6e3418f56b1
QDM16 6f/e8/81/6fe881f89b92fbdf138d8d8c915ca597
QDM17 e1/c0/f0/e1c0f02d38d700d5ff96eec2589ff388
QDM18 f9/52/14/f952147744536667e79e8e8fd0f1ac37
QDM19 a0/12/7e/a0127ec0d6243813e41d0b2dc03d316b
QDM20 32/bd/87/32bd8791ad8b9aebd367da0ab7e94906
QDM21 5f/f7/22/5ff722953a82bfae712e540826358325
QDM22 1d/cd/58/1dcd58052e941945ae81e0a6a9eb4b89
QDM23 08/ab/b2/08abb23b63dcbe8687ff0938d7d1006d
QDM24 5a/11/d2/5a11d2297773c0a010a477ad5065307c
```
Facas reais de lojas e ferreiros. Aparecem as marcas d'água de YouCraftsStore (Etsy), Knifeindex, santokuknives.co.uk e AIKO.
- **QDM6**: dez lâminas de damasco cruas lado a lado, cada uma num padrão: escada, gota, "W", mosaico, pena. É um catálogo de padrões numa foto só.
- **QDM18**: macro de uma lâmina de damasco, com as ondas aleatórias em close. É a textura.
- **QDM3**: faca de chef com damasco em zigue-zague de alto contraste, a lombada preta martelada e cabo de bordo listrado sobre ardósia.
- **QDM15**: faca de chef com damasco mosaico de "folha" em padrão grande.
- **QDM9**: nakiri com camadas de cobre, damasco quente e dourado.
- **QDM24**: lâmina com casca de forja preta e padrão gravado a ácido, cabo G10 laranja e preto.
- **QDM22**: quatro facas com martelado tsuchime por cima do damasco.
- **QDM16**: karambit de damasco com cabo de raiz de madeira sobre carvão.
- **QDM23**: bowies de damasco com cabo de madeira estabilizada azul e guarda em níquel sobre couro laranja.
- **QDM14**: faca de caça de damasco entre ferramentas de forja (bigorna, tenazes, lampião).
- O resto: QDM1, QDM2, QDM5, QDM8, QDM11, QDM13, QDM17 e QDM20 são bowies e facas de caça com bainha. QDM7, QDM10, QDM12 e QDM21 são jogos de cozinha. QDM4 é uma faca de pescoço. QDM19 é a capa de um artigo ("Is Damascus steel actually good?").

#### QCH: "case hardened receiver" (fora do assunto; ver QCC e QCO)
- Código **QCH** · busca `case hardened receiver` · https://www.pinterest.com/search/pins/?q=case%20hardened%20receiver · 23 pins na ordem servida · coletada em 2026-09-28 05:41 UTC
- Lista ordenada (código, caminho da imagem depois de `i.pinimg.com/originals/` ou `/736x/`):

```text
QCH1 22/e8/87/22e887a78ba240737c67d4b8d61a58d5
QCH2 3c/af/28/3caf28cf285f0724cba9987d32b1e2f1
QCH3 c0/aa/06/c0aa069c9e9b2fb2693e33efe5719ea2
QCH4 32/bc/99/32bc9926fd50eb75dfa266ed0aa3b6c8
QCH5 8d/0a/19/8d0a193511347ca9342c75a12d518554
QCH6 55/97/9e/55979ef0cffdbf1d7a57ca5ae022af2a
QCH7 f5/70/9f/f5709fa60f8d3912a63584406fef6bd9
QCH8 2d/30/10/2d301030d656ce3b8e652596aae0497c
QCH9 39/4d/21/394d21336c7d3c3ba50b951603edaa4c
QCH10 f7/e7/5f/f7e75f5d36b43f0c7ca7473d140d5e08
QCH11 ee/07/29/ee07298aefa0023611566a41d0d49739
QCH12 b5/ff/8a/b5ff8a8c5809b1dad44b33d5f75891c9
QCH13 67/94/52/6794521ef5690f2e1a1faddd09f34bba
QCH14 23/7c/08/237c082e81f4a6cd3bac8c7a60741b29
QCH15 2f/ef/5f/2fef5f0713a9c799b12aec58369760e3
QCH16 59/0e/82/590e8226168f8dbccb5e948b8f217038
QCH17 bb/3f/55/bb3f55b5c44ab1be9d2f099e6ed80a99
QCH18 86/ac/4a/86ac4a32abb58d1061c84a5b36d29bb9
QCH19 c0/76/eb/c076ebc1440ce3790e5ec9d23f14db9d
QCH20 52/d1/cf/52d1cf3b4c5407044c5e7b6c0e4c8425
QCH21 c5/60/eb/c560eb55eae762c9e236ef78a8e5fc75
QCH22 14/5e/47/145e47c53098d1dedc916da385dde26f
QCH23 52/c9/3f/52c93fd363b3bef34453174ccd8ee549
```
A busca entendeu *case* como maleta: quase tudo é fuzil em maleta rígida com espuma, com marcas Pelican e Condition 1 visíveis.
- **QCH4**: armações de revólver de ação simples e um receptor com têmpera colorida de verdade, manchas azuis, roxas, cor de palha e cinza. É o único pin no assunto.
- **QCH9**: revólver de percussão antigo (tipo Colt Walker ou Dragoon) numa caixa de madeira com feltro verde, polvorinho e molde de bala. A armação tem as cores de têmpera desbotadas.
- **QCH22**: receptor de AR antigo com a anodização gasta puxando para o roxo.
- **QCH17**: carregador PMAG com um marcador de combustível pintado ("E" e "F", com balas no lugar das marcas). É uma ideia de grafismo.
- **QCH1**: maleta laranja com o logo "GROZA" e um touro em pixels, adesivo gasto.
- **QCH2**: desenho técnico isométrico de um receptor inferior de AR, a traço.
- **QCH14**: marcas do seletor gravadas por encomenda ("SAFE" e "GET OFF MY LAWN!").
- O resto: QCH3, QCH5 a QCH8, QCH10, QCH11, QCH13, QCH15, QCH16 e QCH18 a QCH21 são fuzis em maletas. QCH12 são fios, junk. QCH23 é uma peça de aço inox.

#### QCC: "color case hardened receiver" (primeira adaptação)
- Código **QCC** · busca `color case hardened receiver` · https://www.pinterest.com/search/pins/?q=color%20case%20hardened%20receiver · 25 pins na ordem servida · coletada em 2026-09-28 05:51 UTC · redação adaptada
- Lista ordenada (código, caminho da imagem depois de `i.pinimg.com/originals/` ou `/736x/`):

```text
QCC1 5a/f4/26/5af426acff0851614ba879247316adf8
QCC2 3d/62/46/3d6246445462ff80a6e211beeb54b0ec
QCC3 8f/2d/83/8f2d83009ac4afe6658069f3d6852d11
QCC4 22/e8/87/22e887a78ba240737c67d4b8d61a58d5
QCC5 d0/c2/49/d0c249bd50fc4fca1e7f3629574045c3
QCC6 59/0c/ff/590cff5891b97544ad80896bc5a30914
QCC7 ae/19/21/ae19216770c0aa398f71ca03d9bba7c8
QCC8 45/b8/dd/45b8dd4bf089bc97437862a1cfc648d9
QCC9 05/16/8b/05168b6fb57b32dabb3036a562c9ad40
QCC10 ca/c4/81/cac481214477bfa396c79ed7bf0dac4b
QCC11 06/de/bc/06debc5c028d18538cca144cdc31fa41
QCC12 57/33/86/573386bf5eb263285a914c6caafec01a
QCC13 f3/71/52/f3715254c2a1ecfa57bc9958bf0327d3
QCC14 7d/c6/54/7dc654167ccf4b5b281d049c93089d63
QCC15 f1/89/bd/f189bd31bb4970b6e6d2efe7e79ef283
QCC16 82/dd/34/82dd34803153ff16919b8f6f0d813365
QCC17 e8/98/c1/e898c1354e1a19569a6ae202280fb04e
QCC18 d8/88/d2/d888d2eb89ced15a4c8f161f6a1670fa
QCC19 1b/06/6f/1b066f259a9a425955a506304142396b
QCC20 a0/ca/c1/a0cac15ad88ae36030ff9482a7ee7a81
QCC21 3a/b6/0a/3ab60a9cd94cebcc4bd7cd8c673db409
QCC22 a0/3b/4e/a03b4eb9f80776cbc09f4d1fb415a2e9
QCC23 14/5e/47/145e47c53098d1dedc916da385dde26f
QCC24 ff/84/70/ff8470e15c4290192d97f1aa363df662
QCC25 2a/cd/e1/2acde1be3fffaeb68f4cbd7710a7093b
```
Ainda dominado por cerakote colorido de AR. Só QCC18 mostra a têmpera colorida de verdade.
- **QCC18**: AR clássico com os receptores superior e inferior em têmpera colorida, com coronha, guarda-mão e empunhadura de nogueira. É a têmpera numa arma moderna.
- **QCC1**: AR em tinta camaleão, que muda do roxo para o azul, sobre lenha.
- **QCC2**: Falkor Defense (marca, "300 WINMAG"). Aurora boreal e silhueta de pinheiros pintadas no receptor.
- **QCC5** e **QCC13**: pátina de azinhavre sobre cobre e peças em cobre enferrujado.
- **QCC10**: receptor rosa e roxo "doce", com o logo da Radical Firearms.
- **QCC20**: 1911 com um falso revenido colorido (azul, dourado, roxo, arabescos ciano). Parece película ou pintura, não têmpera de verdade.
- O resto: QCC3, QCC6, QCC8, QCC9, QCC11, QCC12, QCC15 a QCC17, QCC19, QCC22, QCC24 e QCC25 são outras pinturas de AR. Dos repetidos, QCC4 é QCH1, QCC23 é QCH22, e QCC1, QCC2, QCC7, QCC10, QCC14 e QCC21 já estão no QCK do projeto.

#### QCO: "color case hardening" (segunda adaptação, a que acertou)
- Código **QCO** · busca `color case hardening` · https://www.pinterest.com/search/pins/?q=color%20case%20hardening · 25 pins na ordem servida · coletada em 2026-09-28 05:52 UTC · redação adaptada
- Lista ordenada (código, caminho da imagem depois de `i.pinimg.com/originals/` ou `/736x/`):

```text
QCO1 49/52/f9/4952f9bdd6237b060b34511824ca7cd1
QCO2 c7/5a/c5/c75ac551417b502e091d530fab7739f3
QCO3 00/51/c5/0051c554042c3413f9f7694d2ea0ac2e
QCO4 cd/36/4d/cd364dcb98b9cd297c9910b9bb23ab2b
QCO5 b1/08/fc/b108fc34912794f99d8f8806fe17f438
QCO6 23/8f/c4/238fc4e48234ae4f78ce2722ca0f4f35
QCO7 88/bc/19/88bc199ca9ff5fad8458280a640fc05d
QCO8 32/bc/99/32bc9926fd50eb75dfa266ed0aa3b6c8
QCO9 48/81/e5/4881e540637d3e9cbd122bc3e1a4f3d8
QCO10 43/fc/7f/43fc7feecb4a853abf3867a067c343fb
QCO11 9a/ef/fb/9aeffb870d3c5b613729dd423e33baf9
QCO12 a7/33/db/a733db42d3cf53459654430a4d885058
QCO13 8c/3b/17/8c3b17fc0cb3f24fdf69a99ab6427dc6
QCO14 c6/90/b4/c690b477b0b8fa7451eb7957df8492d3
QCO15 40/24/8a/40248a8549248b80c4e6987a3e6b642f
QCO16 5a/f2/49/5af249578f8d341f365a12db36e26222
QCO17 ef/99/bd/ef99bd295700231f685f25cc0d8f05dc
QCO18 e0/43/c5/e043c517bdee7edeb084de780ba9634f
QCO19 ba/70/cf/ba70cf50771c142ebda39c7ebc2d7c98
QCO20 b4/80/10/b48010035a75370d1974c945820de424
QCO21 03/d2/89/03d289fa0293890d219f3a3001f635e5
QCO22 15/6b/40/156b4048967a6dc01ac1de3f277dee28
QCO23 ca/c4/81/cac481214477bfa396c79ed7bf0dac4b
QCO24 32/b3/e4/32b3e4c514e03a2ace73f09f8e26553a
QCO25 9e/ec/01/9eec01a0930ca8909d1cead3604b591f
```
Armas reais, peças soltas e gráficos técnicos. Marcas visíveis: 903 Tactical Arms (QCO17) e Steel F/X (QCO20 e QCO24).
- **QCO2**: armação de revólver de ação simples, tipo Colt Single Action Army, com têmpera colorida viva em manchas azuis, roxas e âmbar, o tambor oxidado e a empunhadura clara.
- **QCO3**: bloco de aço de teste com as cores de têmpera, na ponta dos dedos. Serve de amostra de material.
- **QCO5**: espingarda de dois canos lado a lado com a ação em azul, roxo e dourado fortes e coronha de nogueira quadriculada sobre feltro verde.
- **QCO6** e **QCO7**: lever-actions tipo Winchester com o receptor em têmpera colorida, nogueira e cartuchos de latão. QCO7 está numa caixa de madeira.
- **QCO4**: fuzil de tiro único (bloco cadente) com a ação colorida e nogueira, em três fotos.
- **QCO14**: réplica de revólver de percussão com a armação colorida, guarda-mato de latão e cabo de madeira vermelha.
- **QCO18**, **QCO21** e **QCO22**: pistolas 1911 com a armação em têmpera colorida.
- **QCO9**: gráfico de cores de revenido do aço: Light Straw 410 °F / 210 °C, Orange-Red 500 °F / 260 °C, Purple 520 °F / 270 °C, Dark Blue 550 °F / 290 °C, Light Blue 590 °F / 310 °C, Green 630 °F / 330 °C, e depois "Pastels" e "Dark Green".
- **QCO25**: tabela de cores do aço aquecido, do brilho ao revenido: Bright yellow 2000 °F / 1093 °C, Orange 1700 °F / 927 °C, Bright red 1500 °F / 816 °C, Dull red 1200 °F / 649 °C, Dark grey 800 °F / 427 °C, Blue 575 °F / 302 °C, Dark Purple 540 °F / 282 °C, Purple 520 °F / 271 °C, Brown/Purple 500 °F / 260 °C, Brown 480 °F / 249 °C, Dark Straw 465 °F / 241 °C, Light Straw 445 °F / 229 °C, Faint Straw 390 °F / 199 °C. Os dois gráficos não batem nos detalhes: a 500 °F, QCO9 diz laranja-avermelhado e QCO25 diz marrom e roxo.
- **QCO11**: gráfico "Tempering colors of steel" com as amostras de 350 °F a 730 °F e uma tabela de tratamento térmico.
- **QCO15**: carvão de osso, o composto da têmpera, num cadinho.
- **QCO16**: receptor recém-saído do banho, com as cores foscas, na mão de luva.
- O resto: QCO1 é a miniatura "How to colour steel with HEAT". QCO8 repete QCH4. QCO10 é um fuzil de ferrolho com a ação gravada. QCO12 são peças pequenas coloridas. QCO13 é uma 1911 oxidada. QCO17 é uma Glock com o ferrolho gravado (903 Tactical Arms). QCO19 é uma 1911 com pátina verde. QCO20 é uma amostra de pátina colorida em aço inox 304 ("Stainless F/X Patina", Steel F/X, 2016). QCO24 é um receptor de espingarda com pátina que imita a têmpera colorida ("Matching or restoring color case-hardened patina on shotgun", Steel F/X, 2015). QCO23 repete QCC10.

#### QCP: "camouflage pattern swatches"
- Código **QCP** · busca `camouflage pattern swatches` · https://www.pinterest.com/search/pins/?q=camouflage%20pattern%20swatches · 24 pins na ordem servida · coletada em 2026-09-28 05:41 UTC
- Lista ordenada (código, caminho da imagem depois de `i.pinimg.com/originals/` ou `/736x/`):

```text
QCP1 d8/12/68/d81268e747458a54d5251651dceb1fdb
QCP2 53/ee/06/53ee06a978a7a2836c670c47c9cfb513
QCP3 42/98/61/4298615525fb9247104935d5450046c8
QCP4 84/29/68/84296872c5ed502ba042c8c9edb41efe
QCP5 d8/56/1d/d8561d22719ae3999ef5a701d9ccce07
QCP6 1c/3d/19/1c3d19e1ad33e45a4a040469b896847d
QCP7 61/e0/5b/61e05b5dd23a7e301898b5da26beb5e0
QCP8 ce/50/f5/ce50f557f1f7141bcbd72b27f7ec68fc
QCP9 33/39/fb/3339fb7c1de08b96330c462d68b56c51
QCP10 91/af/c7/91afc716ec11fdb5a5b48df9b199d73d
QCP11 dd/c2/0c/ddc20c892d45dc13f1fec21b083f2dd5
QCP12 29/c2/88/29c28866a15ecaade110f4b74755747c
QCP13 01/a0/fb/01a0fb7a1bcb9d9e29d31ec8f1f022a2
QCP14 d6/14/9d/d6149dd7dda41bdfdfe4063b2367f76d
QCP15 4c/b6/dd/4cb6dd675a84b6e324139f8da6cae129
QCP16 19/1a/4e/191a4ece017268b0f28ea2078c86a6ca
QCP17 a1/a9/1d/a1a91df6bfc86d64abc0e30848773d81
QCP18 d3/ad/6b/d3ad6b2657d998ebe1488729de9e5509
QCP19 23/cd/3d/23cd3d6a7509dc13530548aee81c56ec
QCP20 c9/a1/82/c9a182dcef54aa838a5c6cee5562f897
QCP21 4b/7e/4c/4b7e4cd5a728d45200e94a84a8bf9822
QCP22 ff/18/22/ff182237087dd578f2ee1cafdc76d982
QCP23 89/b5/b1/89b5b179d47b6d99ad465249a3512e70
QCP24 6c/5d/16/6c5d16bdb0a7acd42b4b5c9103e8bb27
```
Padrões vetoriais e tecidos. QCP17 nomeia padrões reais, alguns registrados (MultiCam®, A-TACS).
- **QCP17**: mostruário de tecidos com os nomes: MARPAT DESERT, MARPAT WOODLAND, ACU, MULTICAM®, NWU, AOR, ABU, MULTICAM® ARID, BLACK RIPSTOP, ATACS FG FOREST GREEN, ATACS AU ARID URBAN, MULTICAM® BLACK, COYOTE BROWN, DESERT SAND, OLIVE DRAB e FOLIAGE GREEN. É a taxonomia e o nome de cada cor.
- **QCP2**: manchas grandes arredondadas em marrom, verde e oliva, separadas por um fundo creme (tipo "frog skin" ou "duck hunter"). Lê bem de longe.
- **QCP3**: retalhos de camuflagens reais (flecktarn, multicam, woodland) costurados com ponto zigue-zague. Tecido com a costura aparente.
- **QCP5** e **QCP20**: coleções de padrões ("400+ Free Camouflage Patterns"; "seamless camouflage eps 10 vector"), com versões rosa, azul, roxa, ártica e digital.
- **QCP15**: listras de tigre em azul-marinho e azul-claro.
- **QCP24**: camuflagem de pinceladas verdes e manchas de tinta.
- **QCP14**: camuflagem misturada com estampa de onça, envelhecida.
- **QCP1** e **QCP7**: digitais em pixel, uma de deserto e outra verde.
- O resto: QCP4, QCP6, QCP8, QCP11, QCP16, QCP18 e QCP22 são woodland em várias escalas e contrastes. QCP9, QCP21 e QCP23 são de neve ou urbanas claras. QCP10 é woodland com rosa-choque. QCP12 é de mata miúda. QCP13 é preta. QCP19 é urbana cinza.

#### QSC: "gun skin concept art"
- Código **QSC** · busca `gun skin concept art` · https://www.pinterest.com/search/pins/?q=gun%20skin%20concept%20art · 25 pins na ordem servida · coletada em 2026-09-28 05:41 UTC
- Lista ordenada (código, caminho da imagem depois de `i.pinimg.com/originals/` ou `/736x/`):

```text
QSC1 20/3d/2c/203d2c79d23d74e7264449fdb8526bbe
QSC2 d1/3c/dd/d13cddba48caae86c37156eaa9a43df9
QSC3 5d/76/09/5d7609d79a3704b65b6a8a2699abf1f6
QSC4 d9/d8/33/d9d833a521d82e8bf1f2e67eab59d717
QSC5 1f/6d/e1/1f6de1dcdee4857cad1dd7a359384eca
QSC6 75/7d/95/757d9528cf77466e94f94c76226c66c5
QSC7 4d/1f/f6/4d1ff678f7bb0bda0f6fa31d43f026d0
QSC8 45/99/2a/45992ae70c12c0e71f02934b054cbd01
QSC9 95/2a/24/952a2468d022304ae0e05ed2d1eeb66d
QSC10 bf/b8/8a/bfb88a19d24eb43df5886f15ef9b83c6
QSC11 f7/46/15/f746154a77ca3970fe273fb6ac3ea6ba
QSC12 89/7c/53/897c536901e28069c337f3655e43347d
QSC13 43/f2/73/43f27362b5f19d3540c26efd71e5c6df
QSC14 50/03/77/500377276c21511bdfb4a886e13e24c9
QSC15 37/2c/56/372c56a811fa98146976c64949bb5070
QSC16 65/00/a1/6500a1c4e5201036882c2b7d8dec7c01
QSC17 02/2d/31/022d3138f08c0a1248535617fd8a7510
QSC18 e8/0a/db/e80adb37254577049f19f569e9ccf3fb
QSC19 c7/8c/96/c78c962afe0ce2fe7502b7b94e282593
QSC20 5d/54/e1/5d54e197483153986b1ed206c7ac0f81
QSC21 3d/b0/da/3db0daa2bfc05a7549bdfa17383e1c0a
QSC22 a1/d5/08/a1d5080a8c71561d5a5966f16c25898f
QSC23 fa/e1/50/fae15006691158dc30d791c258c27937
QSC24 3e/08/4c/3e084c733da1150e66b6e639aaf4494c
QSC25 9b/ae/33/9bae33bde6ce87a43a15dada21f618ab
```
Concepts de fã, da Oficina e oficiais (Apex Legends, com a marca Respawn/EA; Call of Duty, com Activision, Beenox e Raven), e uma pistola pintada de verdade (QSC6).
- **QSC4**: folha de um conjunto em branco, azul-marinho e dourado, com asas e mármore (fuzil de precisão, fuzil, pistola). No canto ficam os quadrados das amostras de material: azul-marinho, mármore e dourado. É a apresentação de uma skin com a paleta de materiais.
- **QSC22**: arte oficial de Call of Duty (logos de Call of Duty, Beenox, Raven, Treyarch e Activision). Duas versões de um fuzil tipo AK decorado com uma serpente roxa, uma carpa e flores de cerejeira, com os decalques soltos ao lado (a serpente, a carpa, as flores) e, embaixo, um detalhe de elmo samurai em bronze. É a skin decomposta em decalques.
- **QSC7**: Apex Legends, "R-99 REACTIVE — BUZZ KILL", temporada 20, com três estágios da mesma skin reativa em laranja e preto com efeito de falha.
- **QSC17**: "AKS-74U SAMURAI SKIN" em três vistas: laca preta e vermelha, dourado e os chifres do elmo samurai.
- **QSC16**: SMG com listras de bala em rosa, amarelo e verde-água em quatro vistas, com o logo do Substance. Mostra como o padrão contorna as peças.
- **QSC5**: "USP-S DRACO" (assinatura CLEGFX): grafismo tribal roxo e azul em duas vistas.
- **QSC6**: Glock pintada com a máscara de oni, ondas e o ideograma 鬼 em vermelho e preto.
- **QSC10**: ilustração de pistola de tema japonês em rosa pastel (grande onda, cerejeira, máscara, pagode, torii).
- **QSC12**: pistola retrofuturista branca e laranja ("TONY BOY", "MI.COM").
- **QSC19**: fuzil de estilo mecha em rosa e verde, com "THUNDER", os ideogramas 和諧富強 e a etiqueta "DANGER".
- **QSC13**: fuzil de precisão todo dourado e ornamentado.
- O resto: QSC1, QSC2, QSC9 e QSC15 repetem QCW7, QCW17, QCW14 e QCW3. QSC3, QSC8 e QSC14 são fuzis de ficção científica com brilho. QSC11 é um concept do ArtStation. QSC18 é um revólver ornamentado branco e dourado. QSC20 é uma Glock com grafite. QSC21 é uma Vector rosa. QSC23 repete QGU10. QSC24 é "USP-S CUT". QSC25 é uma SMG amarela e preta.

#### QVW: "valorant weapon skin"
- Código **QVW** · busca `valorant weapon skin` · https://www.pinterest.com/search/pins/?q=valorant%20weapon%20skin · 22 pins na ordem servida · coletada em 2026-09-28 05:41 UTC
- Lista ordenada (código, caminho da imagem depois de `i.pinimg.com/originals/` ou `/736x/`):

```text
QVW1 00/40/d4/0040d4dded7dff4592c0e9eabeb2bb7d
QVW2 bb/d1/6f/bbd16fa597767beb4f0af7ecd718e4a7
QVW3 c2/b9/55/c2b9559bf524fac9d399f5167d6df61a
QVW4 c7/59/26/c75926209001eac288223c2b9b151a17
QVW5 d0/34/21/d03421822fb9be240e55a1b869d0abf9
QVW6 1e/9f/6c/1e9f6c0ca5793637d1dc268eec610955
QVW7 6e/9d/d6/6e9dd6962299660c88782b5365e357fa
QVW8 7b/dc/20/7bdc208961b1965984ea4d6436b36e3b
QVW9 95/2a/24/952a2468d022304ae0e05ed2d1eeb66d
QVW10 c5/10/4e/c5104e77b759798ce520e743212b3403
QVW11 e6/43/82/e643824214255d1ac411c7dff42389e5
QVW12 8a/34/cd/8a34cd98477c89a6e6c204f86661e053
QVW13 41/04/45/4104451019dcab155d7ea97eecb1b959
QVW14 3a/39/14/3a391415d1aeedb0de6c4479c91d3559
QVW15 00/d9/db/00d9db80dfc6e8c25cb1953eca63a1ac
QVW16 72/2d/4d/722d4dccf627d720eee3f1d45a6acfe3
QVW17 26/a3/75/26a3750ff921fbd6a52ca81ba89029f9
QVW18 80/f8/d4/80f8d4582bafc1a2189a17e57e33c084
QVW19 13/b0/52/13b0526fd231d5740fc3b6e71706d662
QVW20 5c/28/f9/5c28f9282c8258548e2d2d7ee9de787c
QVW21 87/7d/2d/877d2d7c9fb9e49c4ae56483e2437564
QVW22 4e/ea/e8/4eeae869cf7f0f9510b1398efec23a0d
```
Tudo é arte de jogo (Valorant, com os logos da Riot e do jogo) ou captura da tela de coleção.
- **QVW1**: pistola do Valorant em cromo, preto e branco esculpidos, com crédito de artista ("Michael Altuna // 3D Artist II") e o logo da Riot. É o nível de acabamento de uma skin premium.
- **QVW13**: quatro iterações de concept de uma skin de fuzil em branco e azul, com o crédito "Concept Designer". Mostra a ideia evoluindo.
- **QVW4**: "SINGULARITY SHERIFF" na tela de coleção: preto com painéis violeta emissivos.
- **QVW8**: "REAVER PHANTOM" na tela de coleção, em preto e carmim, com as variantes e o botão "EQUIP SKIN".
- **QVW7**: coleção 光明哨兵 (Sentinelas da Luz) em rosa, branco e prata, com o leque como arma branca (captura do rednote).
- **QVW10**, **QVW15**, **QVW18**, **QVW20** e **QVW21**: pôsteres de coleção com a fila de armas, a arma branca e o logo. É o layout de apresentação de um pacote.
- **QVW19**: karambit preta e roxa em fundo branco.
- O resto: QVW2, QVW3, QVW5, QVW6, QVW11, QVW12, QVW14, QVW16, QVW17 e QVW22 são outras skins. QVW3 e QVW5 já estão no QVS do projeto. QVW9 repete QCW14.

#### QCT: "claymation weapon toy"
- Código **QCT** · busca `claymation weapon toy` · https://www.pinterest.com/search/pins/?q=claymation%20weapon%20toy · 23 pins na ordem servida · coletada em 2026-09-28 05:41 UTC
- Lista ordenada (código, caminho da imagem depois de `i.pinimg.com/originals/` ou `/736x/`):

```text
QCT1 71/2b/b2/712bb21f912d4dc1f91846cab587ba84
QCT2 17/24/3b/17243b5ab6c651e16e9775a92e50c76a
QCT3 55/3e/ff/553eff220cef92ee2ddf2fd07024c3a1
QCT4 dc/c0/7c/dcc07c45d85709cb304a64c60240e62a
QCT5 62/3d/e8/623de86fade139ce2168ba1a1b901447
QCT6 7e/0b/55/7e0b55032730153d3085c6d3a4170619
QCT7 7b/8a/62/7b8a62dfba196a93521c94691b51c483
QCT8 7f/4d/68/7f4d681a536bc3ef2dec9dc38d2a51f2
QCT9 59/25/4f/59254f63d56ad34d4c24a86788b84cb7
QCT10 25/a7/43/25a743e9b75eb7c3dcfb5d112ff8511f
QCT11 a2/e6/0d/a2e60d487c3b3646a4f41dc4be661849
QCT12 c1/b6/77/c1b677a483ca21fec272014d3358a12f
QCT13 46/7d/d3/467dd3bef2b1086c0b84462683615a3b
QCT14 6f/4c/a2/6f4ca2b41741b6d61c8ba7ed092eccbc
QCT15 f9/04/9f/f9049f155b9cd9e08620c6d330a6f44e
QCT16 d9/66/06/d966063f13b8dc957f410bfec382c39a
QCT17 77/f5/31/77f5317123f565a501d1c3ad2ecf50d7
QCT18 1c/4e/74/1c4e74c7b338b144e1d6c77b64b9b98b
QCT19 2b/0e/d4/2b0ed487b1dd9a8dda191f7639a3f614
QCT20 20/48/62/20486247ff5c76240ae6517f50ceec61
QCT21 ba/5b/06/ba5b06678d6e1a7070a5f762ca05f089
QCT22 1d/94/23/1d9423c580790c4af14d3ddab7e3f621
QCT23 09/98/55/099855c47de9a948b5d8cb9e51ce1411
```
Brinquedos, miniaturas, props e renders estilizados. Arma de massinha propriamente dita só em QCT2 e QCT9.
- **QCT2**: arma ou martelo de massinha colorida (listras de Play-Doh, um número "2", uma estrela), feita por criança. É o visual de massinha de verdade, com emendas, dedadas e cores que se misturam.
- **QCT3**: ilustração de arma feita de gizes de cera, com hachura de lápis de cor e os gizes como munição. É um tema de material escolar.
- **QCT1**: boneco articulado (marca d'água FigureBoy) com duas submetralhadoras pintadas à mão em tons pastel, com letras de grafite ("BYE BYE") e fita. Arma de brinquedo pintada à mão.
- **QCT9**: duas facas com cabo de cabeça de peixe vermelha de desenho animado, olhos arregalados e fita. É um render com cara de massinha.
- **QCT5**: fuzil de precisão em escala 1/6 com luneta e fita, entre dois dedos (Snow Corporation, 1-6th.co.uk). É o desgaste de uma miniatura. Já está no projeto como QRF4.
- **QCT6**: réplica da Ray Gun do Call of Duty Zombies, pintada em vermelho com mostrador colorido, sobre uma base de corte.
- **QCT14**: armas esculpidas como madeira de tronco, com cogumelos e folhas.
- **QCT15**: cartela antiga "SHARP SHOOTER COLLECTOR'S SET" (Imperial Toy Corporation, 1977, No. 781, feita em Hong Kong) com armas de metal em miniatura sobre rosa.
- **QCT22**: lança-granadas estilizado em laranja e marrom, com chamas e o símbolo nuclear, pintado à mão.
- O resto: QCT4 e QCT20 são martelos de apito. QCT7 é uma arma de desentupidor. QCT8 são espadas impressas em 3D. QCT10 é um bowcaster. QCT11 é uma pistola steampunk. QCT12 e QCT17 são miniaturas de boneco. QCT13 é uma motosserra de desenho. QCT16 é uma faca de brinquedo verde. QCT18 é uma bazuca de desenho. QCT19 é um manequim articulado. QCT21 são armas de fantasia em 2D. QCT23 é um lançador de espuma com serra.

### Inferences
- **Acabamento como material:** o CS aplica o mesmo acabamento em todas as lâminas (QKS1). No MASSACRE, cada skin pode ser um material com parâmetros próprios (degradê, marmorizado, damasco, arco-íris), aplicado por zona sobre a arma de fábrica. Isso segue o que o projeto já decidiu com o QCK e o QCS (`src/data/acabamentos.js`).
- **Temas que servem ao set de massinha:** a porcelana azul e branca aparece em cinco pins de fontes diferentes (QKS14, QCW1, QCW3, QCW7, QHD1). Esmalte de cerâmica é um material de ateliê e combina com um mundo de massinha e estúdio. Os outros temas que servem são a arte de nariz de avião (QCR5, QCR20, QCR25), a manchada de borda clara (QCP2), o giz de cera (QCT3), a massinha de criança (QCT2), a pintura de brinquedo (QCT1), as curvas de nível (QCR7) e a pátina de cobre (QCR2).
- **Cores com base física:** a têmpera colorida (QCO2, QCO5, QCO3) é feita de manchas grandes de azul, roxo, âmbar e palha que seguem o fluxo de calor. Os gráficos (QCO9, QCO25) dão a ordem das cores do revenido: palha, marrom, roxo, azul, verde. É uma paleta pronta para um acabamento "aço queimado" ou para a boca do cano esquentada. O titânio anodizado de verdade vem em faixas de cor limpas (QAT2, QAT14, QAT17), enquanto as lâminas baratas têm o arco-íris contínuo (QAT4, QAT7), que tem cara de película, não de anodização.
- **Damasco:** um padrão só não basta. QDM6 mostra sete ou oito famílias (escada, gota, "W", mosaico, pena), e QDM18 e QDM3 dão a escala do veio em relação à lâmina.
- **Apresentação:** as folhas com a paleta de materiais (QSC4), a decomposição em decalques (QSC22), os estágios de uma skin (QSC7) e as várias vistas (QSC16, QSC17) servem de modelo para documentar cada skin nova.
- **Logos e nomes:** muitos pins trazem marcas registradas (MultiCam®, A-TACS, Cerakote, as marcas de faca) ou personagens licenciados (QHD16). No jogo ficam os nomes genéricos das cores ("areia", "oliva", "coiote", como em QCP17) e nenhum logo.

### Gaps
- Nenhum pin mostra uma skin de arma feita de massinha, argila ou material de stop-motion com acabamento profissional. QCT2 é de criança e QCT9 é render. As buscas antigas do projeto (QPG, QPL, QCG) cobrem a arma de massinha.
- Os nomes dos acabamentos do CS fora de QKS1 ("tipo Fade", "tipo Doppler") foram dados pela aparência e não foram conferidos no jogo.
- A anodização de titânio por tensão (QAT18) não traz a tabela de volts por cor. Seria preciso outra fonte.

## 5. Códigos novos, listas prontas para o projeto e repetições

### Takeaway
Os 29 códigos propostos começam com Q, não colidem com nenhuma das 86 chaves de `docs/art/pinterest-boards.json` nem com os códigos citados nos textos do repositório, e terminam em letra, então "QRD1" não se confunde com nada. Abaixo vão o JSON pronto para juntar ao arquivo (minificado, no mesmo formato), as linhas de `BOARDS` para o `tools/moodboard.mjs` e a lista de imagens repetidas. Nenhum arquivo do projeto foi editado.

### Cited Findings
- As chaves Q que já existem no JSON são QAK, QAW, QBN, QBP, QCD, QCG, QCK, QCS, QFH, QGK, QGL, QGW, QHH, QHS, QKN, QMP, QMR, QPB, QPD, QPG, QPL, QRA, QRF, QRL, QRS, QSG, QTG, QTK, QTM, QTT, QVM, QVS, QWR e QWS. A seção 16 do `docs/art/moodboard.md` ainda cita "QM9" (QM95, QM915), que no JSON virou QBN; por isso QM9 também fica reservado. Fonte: `docs/art/pinterest-boards.json` e `docs/art/moodboard.md` do repositório.
- Os códigos novos são QRD, QHO, QAC, QLP, QMG, QRT, QNV, QTH, QLS, QIR, QWL, QFL, QPR, QAS, QGU, QAM, QKS, QCW, QCR, QHD, QAT, QDM, QCH, QCC, QCO, QCP, QSC, QVW e QCT. Procurei cada um nos `.md`, `.json`, `.mjs`, `.js`, `.py` e `.html` do repositório e não achei nenhum. As únicas ocorrências estão dentro de binários (`.blend`, `.webp`, `.png`), por acaso.
- O `tools/moodboard.mjs` lança um erro ("boards sem metadados em tools/moodboard.mjs") se uma chave do JSON não tiver a sua linha em `BOARDS`. Por isso as duas coisas precisam entrar juntas. Fonte: `tools/moodboard.mjs`, logo depois da lista `BOARDS`.
- JSON para juntar a `docs/art/pinterest-boards.json` (uma linha por board, na ordem servida; a posição n na lista é o pin CÓDIGOn):

```json
"QRD":["28/d9/70/28d9704b3cbd59ac481ccd2c98964b5e","06/83/b4/0683b4dcda68ee9691b48a620103175c","86/1a/f2/861af2196325d408a4a7f4d6392c3f21","73/6b/2e/736b2e05d891fa2b1ea7f742b17d6299","47/a7/ab/47a7abdaa14fe738139b89b0d2ac747f","af/45/8e/af458ed62f5bc081b82f230adb45ff87","80/9e/6d/809e6dec10d04fee24a3cb664c2068cf","61/da/c7/61dac78fde2145dd1db561434a071b75","ba/6c/97/ba6c9764cc358658bc25af9def881e87","16/71/56/167156b466e9a8aff3a5ea8ba3d906e1","b5/d5/95/b5d595f1c23c2bb9d2e5133bf6949907","bc/d4/15/bcd41565d7e614d761d8378d47ee4430","94/54/7d/94547d765289e4122988d789ffc1f430","21/b8/69/21b869de7b8e1bbad121c92483fbeb98","dd/66/2b/dd662b38260b7563ad60adaee82b54f2","8e/75/43/8e754394e5f47a4418004d0f543890e2","18/e4/09/18e409d04cafa7b23405c8e8da367410","c7/ba/5f/c7ba5fda84796f0a31f6c84034a9409f","f4/15/0f/f4150fd7192dcb5d6ab84cf730ef97ab","85/1d/61/851d619495790a412cdcd24bdd6fb496","6c/3e/ba/6c3eba6bca129fca6226509e7efe96c7","1a/e1/03/1ae10318b391ab75769fd0a71e549758","27/ef/58/27ef58afad3c12d8cb2eb139c274e3f0","70/99/27/709927a9ba8d554a2962265babeb9905","75/1d/fe/751dfea48f270d059febf07250498b0f"],
"QHO":["c3/9f/1d/c39f1d411dc1ec7b993629a58ded870a","d1/9b/60/d19b601251fe1e22f1b70cfda1a6b508","f6/37/8f/f6378f1ae5dd71c0cfbbbf70ecdb1eb2","c4/1f/bf/c41fbf54dae3c0229cd4326de1928572","27/fb/ac/27fbac65116d6ae0dd87ea3cede2f139","9c/67/b9/9c67b9631f96a135e5aecebbb46edee7","7b/3b/72/7b3b72ffa10116c40d3489b167bb8f62","db/44/b6/db44b663a3d56f6acc1faffbf79e1a2d","6d/fd/6c/6dfd6c4aa2ea6ffc369139c71635ae1a","fe/9e/89/fe9e891c494113c20d0a8fbdf0566334","b3/fc/7a/b3fc7aad0d33d35de59a10f92b42bdd3","d4/af/a3/d4afa30e5202710a91b83ff48d734b84","d6/a0/3b/d6a03b35e43fb181012378818b84b0f1","54/3c/e8/543ce8910c9136fdfad1112f98461a4d","c9/7d/ea/c97dea6969c13e39d4c5db8e167d4a09","f6/d2/e9/f6d2e90883765554bf418e49aff950be","9a/fc/e0/9afce08cfc9c90f70b8299c1817857e6","e8/b4/79/e8b479f10ac5e9a33cb300d3f12fd278","83/44/d9/8344d9ef724d512a2092e216e60428bb","a7/10/39/a71039c1c8ad7248748d0b4952fb5e80","0b/d8/e6/0bd8e6383efff68a2f41115bcde4c6bf","3a/e0/e2/3ae0e2713f360e37544a78d877c4d8de","7c/e3/fc/7ce3fc21c1fc0c455322c08abb0751f2","ba/6c/97/ba6c9764cc358658bc25af9def881e87"],
"QAC":["58/cc/6e/58cc6e910444c825d6caee1a9d59df58","d9/74/74/d974747a730f60df4e374e0e6090e69c","ff/8a/81/ff8a819cfeed2c071cc44a3902b1f14c","ab/03/99/ab039966ff6715aefcf52d03dd805dfa","8f/28/3d/8f283dfee491b46d9c09bfe8a2919460","6a/34/f7/6a34f75302aff5bcbad3fbe18cc681be","16/71/56/167156b466e9a8aff3a5ea8ba3d906e1","57/f3/6c/57f36c533c008214f19b57f08873410d","86/aa/64/86aa64f03dd0d6bd788701efb966e825","28/8d/ee/288dee8479989faa899a1842a302cb74","c0/4c/89/c04c896dd26072e53f9a308a012c1c08","67/92/a7/6792a7783088ef9dee24bcd07f22d9bc","ec/89/7c/ec897c121b1a8b9b04c93256657edead","75/1d/fe/751dfea48f270d059febf07250498b0f","f1/63/e8/f163e880ea7f56687eff736f60999c77","94/7d/3b/947d3b305e72f6dcca273e864fbce2a9","25/bc/f4/25bcf48e9e8380ed5ffdb82f17921f27","5f/39/99/5f399919a571e98d47b04fa2afe921db","0b/db/51/0bdb5172f059ea09af75561c66f60e7b","af/98/33/af98339ea64895929b45f46ae7818edc","32/9c/91/329c9158dd47df89f87c09c68206052b","38/f0/aa/38f0aa2db99df233f11710edbd3f8cf7","fd/b4/43/fdb44347444c7e06cb79ffc4adfbbae6","ea/01/c8/ea01c8f41086b4c8c283a7742d2b775e","86/6b/45/866b458eec9f076a6f82f7e3ef0e9b30"],
"QLP":["a5/de/3d/a5de3d81ca18349fd033952bf6012308","64/d1/43/64d14380041731ced22bf0dea078afb2","a7/92/c6/a792c6a81e296adf9a6a3342df01b5e7","4d/db/23/4ddb238c6ee757bb560816d7f65d8cb4","71/3c/ad/713cad293cc9366c1e6f232018beefae","49/23/d3/4923d3e4a1975248e53907778e8652c8","28/8d/ee/288dee8479989faa899a1842a302cb74","a3/26/80/a32680d6fd65a43fae7b6ea710cbb31e","6a/34/f7/6a34f75302aff5bcbad3fbe18cc681be","0d/c5/39/0dc539053e741bbd49835503fa44fdce","5f/39/99/5f399919a571e98d47b04fa2afe921db","bf/f8/af/bff8af86c31193ac869ced05c2ebc247","26/a8/58/26a85811e6faa1a2fe77dd5d99c155e7","c2/01/46/c201463f11cec89eb53c186a48086c3b","c1/ac/1b/c1ac1b4c0a8ecccb028943e415ae86c9","39/50/05/395005bdba5aa98a6fc4f4d662f2d77d","0b/d7/50/0bd750731fddebbc4a6d320188bcb5a7","16/71/56/167156b466e9a8aff3a5ea8ba3d906e1","16/08/fe/1608fe252ace3d1c07cc195e258cd6d1","b4/b1/b8/b4b1b8443940283eb7c515dd82e426a4","17/48/24/174824e58e2da6caf31378d7c4ae11e3","9d/0b/15/9d0b153b77eae2c743717872de447ef6","4a/d3/a1/4ad3a13c7b002f08e19d937ab03e3941","95/d6/ac/95d6ac585a07f63caee59ac71977390a"],
"QMG":["ed/29/dd/ed29dd9092454451bb629bb1a80eec38","c4/d4/57/c4d45783235eb376f83c64f25878c442","ba/37/bd/ba37bdebf18aeea22f8f9ab613c4635b","7b/09/ff/7b09fffe18c13711d7cfd4bdeceac745","e2/6f/8b/e26f8bb705a96c685299136a1c8d4185","a5/f0/98/a5f09835e62342a79e64a3eda778593a","f8/62/8e/f8628e183ae40801c51593e735f1082e","2b/55/d7/2b55d7c4be858b6c3c52cc9511c9c4c8","83/54/80/835480993ec07a32130897555b4527b4","53/37/3d/53373dc7f3471e04be3c157f2f6bc9fb","3e/1a/7c/3e1a7c63de10f05b2b70291c62f392bd","d3/62/16/d36216251146d781c727cd6caf572498","20/09/db/2009db075463088640666c902fad05c0","09/26/7b/09267b9f9d993074287a380cc6cd3b61","e7/fb/a3/e7fba36ca2755f5bb013d180a30682a8","22/6d/11/226d118bda2858c9827037d56b51f4b2","c1/bc/d2/c1bcd2eff3b17ce3cad0023075b18fe6","97/e5/2a/97e52aa20ed15ee49e585934391e27e5","27/d2/86/27d286d31a75b3704cb2ff75dcdcab0a","3e/e0/8b/3ee08b98a5d2caceeccf61a8999c201b","4f/a5/97/4fa597a1f21cec7fecb882aaccc55629","e3/4d/a0/e34da0a62eb53d3c86c50c3e592327a9"],
"QRT":["53/f9/84/53f984a6241aec7c4949d8aa8725950d","c5/d2/89/c5d289dcae3304fe3701b124a779830a","2b/f5/b5/2bf5b59cfd35ad5b486b42bc461b463c","c1/63/9b/c1639b8d3d3bc2c9a33e1203df4f6e2a","14/a1/3c/14a13c6a472c5810833417cff970d5ef","86/7e/ce/867ecefa3c30b85460a12f652c0f3d20","93/01/e0/9301e0d810f91cf91acc90c565b589cc","9f/71/01/9f710158ecddce402cf09a8482dc8f7d","01/13/36/0113367f590124b8b696a38556e3e3ed","06/ae/ec/06aeecd105fd67a240d6700b6f0a1285","d7/0f/71/d70f711683f05044b8e38055e6f6b578","c4/e4/cb/c4e4cb4c16731adaa9ab0fb9dd6412a6","a1/07/3f/a1073fac5baddc5b2e58d407f3b30187","50/cf/f9/50cff92b0df50e9cd7d9f2a67e5d8148","87/f3/92/87f392f423fdece137cb38feb7acde7f","43/c6/8d/43c68d1624e2d6a27fc034dbe4f32ee2","9a/37/c7/9a37c71ddc71a5608586f9ba639daef7","75/4b/45/754b45184afb5c1e3764cdf1d5bd56c2","a8/6b/dd/a86bdd4eb41d003d92c021b06705f63a","80/d1/b2/80d1b2641cc12f0b694a14a73d134be3","15/0b/e7/150be781011bfc570d8c8a77756e61cc","2e/d2/04/2ed204cf3c097fd74e1171c3135929d5","b4/54/9c/b4549c65a008a61a1fc7d03136d5b464"],
"QNV":["01/13/36/0113367f590124b8b696a38556e3e3ed","05/af/a9/05afa90d22052df8548414b2c771358d","3b/11/3b/3b113bf5ff370de7bce32b438599dcae","70/1b/84/701b84252529650ef523369fe9e8c54e","c9/19/3f/c9193f713f5e1a2e0cce7de333964307","46/47/de/4647defbaf246d2babbd7aa32f2f1b3b","c4/bc/fd/c4bcfd1cb91c079e79f0e0fd04a011ab","76/9e/66/769e663b11d72aee46b4a2cd2b3a4827","a1/07/3f/a1073fac5baddc5b2e58d407f3b30187","15/19/6f/15196fa828189c5b1a9131843f325783","1a/40/42/1a4042d5f1951df84f05e4e9b75906ab","ae/41/f0/ae41f0b80e5fddb42852d57146feb897","66/65/4b/66654b0c0ed8e1ddf970404a79bba8f4","a2/f7/31/a2f73101de45934640a405372221d567","27/f4/54/27f4544dff4efc1c3d9045add3d8760d","c9/f9/c1/c9f9c1f1001a8ab5d475ca5f2acc010b","6b/ad/0a/6bad0a5be81328d4efe28633ba04d34d","87/af/96/87af964749a65d0dc283619d367d49da","4a/99/d6/4a99d6ab59aff276cf738f0c7f674944","9a/37/c7/9a37c71ddc71a5608586f9ba639daef7","45/15/59/4515594e372fa092ebe8cec84f3e2863","fd/15/69/fd156940118fff835069689d417474ba"],
"QTH":["22/ab/02/22ab023a21fb3579229152dc48adf038","8b/ea/3f/8bea3fa66d99b99f0ac702a258b3ea06","00/fe/79/00fe79c1e5dec83c034661f123053cbb","04/4d/04/044d04a76f695d2785e3b12ef56bd349","f9/4a/a0/f94aa073a032497313d61502623e9fb8","89/b1/0d/89b10d3e16f8d1298eab21159cd0b781","21/0e/14/210e14d615eb08a007031583325292e4","9a/6f/86/9a6f868922968575af8e7f7d500c7392","27/f4/54/27f4544dff4efc1c3d9045add3d8760d","01/13/36/0113367f590124b8b696a38556e3e3ed","6b/16/f0/6b16f03cdab14a4d145e0b0bdefeefab","3b/11/3b/3b113bf5ff370de7bce32b438599dcae","fc/17/a2/fc17a233e01139249997e4e9010406dd","59/8a/06/598a06fa91bf3ade6d8cb69c1c533cf3","a1/07/3f/a1073fac5baddc5b2e58d407f3b30187","75/af/ae/75afae768c1f8232aa298c78204d8ea9","f0/12/90/f012908b70be295a41c1a6987789096c","48/26/11/482611214a067052a7e12c95f1c90205","d5/70/03/d57003b679db1ecd50d97cd220fdd672","9a/37/c7/9a37c71ddc71a5608586f9ba639daef7","bc/51/0c/bc510caf079c9db52620a2f9a4675ca9","50/cf/f9/50cff92b0df50e9cd7d9f2a67e5d8148","50/13/37/501337aad127c74ed2595a856afeca36"],
"QLS":["e7/66/92/e7669215a16a2e352b5f9f2902aec0c7","9a/37/de/9a37decefec709d862e91e52627e6139","6b/09/af/6b09afe29bd5ab43b845b1010d7c061e","e0/f4/63/e0f4635b1d3b4ee7ad05a34433297859","43/72/98/4372980cfac5aa3777b2f4028e965ce2","6a/13/5d/6a135de0ad6efada3e83ece785a98ce0","81/e1/71/81e1715756eb68364ba350b6d7e171d2","bb/26/60/bb266037eace6514a2271525b05237de","ef/4f/49/ef4f49d7d713843fe80d6ca98f89cae7","fe/d3/ed/fed3ed5250393e2375cf7d0164e9bc4b","70/c7/b2/70c7b206c9496efce787dcbaff042bef","82/98/c8/8298c888cbd69c654ee49d0cf24d1966","91/73/91/9173915f63f9b9cab2ed722b71387336","20/09/87/200987367f11d03bf6a9f38566c02a7c","0b/57/12/0b5712e77c435e0dcef355f886e0a7a9","f9/e1/68/f9e168fad6ec3ef6de6cc4e5fa89d931","8a/37/65/8a376537a88eda0f7745321d8356134e","ac/3e/c9/ac3ec955938d629c188ca43209b3c9fb","62/9b/81/629b8124d40784e87b846d2264128982","5c/0f/d7/5c0fd73ffc9d27409b53c6f310437f19","ed/f0/81/edf08135dda0ac514ba8c3cc1af47419","1e/71/f3/1e71f3277b15c8f2afd6c9ec6cbb1421","c1/19/e1/c119e1512d7c652f15472c1980e7e930","70/11/ca/7011ca82195f7934bd8671609517114f"],
"QIR":["f1/ba/0c/f1ba0cced6ee5f833260f5db948700ee","c5/81/33/c58133d2ed4b888ce0b7cd91427f1b1e","02/7b/c8/027bc88c048f822c9cd156693f945055","c9/09/a2/c909a2370b551c38aa7be345bcba7e99","bc/8e/13/bc8e13a4c23772bc94cc54187a4816be","89/39/19/893919d1a75d81656b0a8ca2d0d9a8e6","b3/a8/66/b3a866377060a51e88fc40f635727cf8","54/f8/00/54f800496418ed5f145ab1c11924b832","32/32/3e/32323e369efe96fe642f1efedddd39db","7c/9c/9d/7c9c9d43e147f0533fbe3436fd8782ea","b3/89/ea/b389ea7ae6c0d3a8944792a85b55cef3","9b/0c/16/9b0c16dde5b2495430deee3f19f4f2bc","af/ce/ee/afceeeb5c1257991dc4d42eadd37f107","27/f4/54/27f4544dff4efc1c3d9045add3d8760d","9a/89/c3/9a89c396068629e95b09a6b490d9cc06","a2/49/4c/a2494c5006e0e4f7a52f0397b11d2381","e1/67/b0/e167b02663544ee9175bc6815984523c","47/98/48/4798487e1a2d8c3c80d474e696bf9ec0","6a/ad/97/6aad9784f925b79326a1a2220b135ef5","2b/6a/a7/2b6aa7d7e7d6020c8f0018f4fa3599f8","b5/c9/8d/b5c98d0adeca645f9752663ff9af7bd1","96/c4/25/96c4257bf08a879ef90ebe5b77aa15fe","95/09/06/9509068093bb1f8c9a8ff7ca1796ff68"],
"QWL":["03/5d/0a/035d0a371905d7dcd3817aca7645e310","7e/48/20/7e48209c3adceae3849851b4419ffc64","ec/e8/bc/ece8bc89a35c64f75077716b5ccee71e","d0/c1/db/d0c1db1ea1e901cef0b9cd7de39a26e6","00/94/2b/00942b521196a6ba263918a1c04337aa","80/37/8e/80378e4f9bf9cc764759ddb826b7365b","74/b6/be/74b6be2f19cac871e8ee2c1f78b4e29d","19/b6/42/19b64201a7b032f6e1f7754c6eb7483c","f2/0b/2c/f20b2cecd8ad31fb96f26b46ffa3485e","f2/ca/0c/f2ca0cd21d16abe7a24ed7baa17eaae3","85/f3/da/85f3dacd27cffa75dd7977135b86546d","74/ed/0b/74ed0becde9b987765ca422992fa1a0f","b2/15/ce/b215ce938602b04bac90eefe8cbaceb8","e8/b4/79/e8b479f10ac5e9a33cb300d3f12fd278","d1/48/84/d14884c29049d48dff14466c6119ae9e","06/98/a4/0698a4cceca6801435c68a6b3641bffe","ec/e8/f3/ece8f39920236da51e10b56c7201e5fe","ba/45/22/ba4522c0142c21e1ba0efc9e50e070fe","fa/13/57/fa13573031e9baad5baf408729774783","86/9b/5e/869b5ed4c1349e68616ef3be88d28a37","0b/c5/29/0bc5297deb016ccbb79cee3338f2388b","61/70/fc/6170fc5c5f933a667390a3d16ad3745d","86/b8/7d/86b87d927ae007652fb96e972d5cad2e"],
"QFL":["b6/ac/ae/b6acae1986434787343d17c275f6e2f5","35/a3/c2/35a3c2e20f739f592eb872fb225b0c48","3c/fb/2c/3cfb2c39cfd9c7eb616ae2405aaad49c","3d/9e/55/3d9e5519a2d8df9bb58dd14d12027c2e","9e/fb/69/9efb693a6d995c2a8358e4e7e79938da","d9/c9/7f/d9c97f0b15450009159f79cb2062eee8","b1/8c/92/b18c92251a6b8f791ec5fa0b8779543f","ce/90/40/ce90400e4f0bd04b91bb3bb958540c46","4a/16/b8/4a16b87e6e67730136310bc1a222757b","b9/a7/d3/b9a7d3c9d286a157fd563c89f65b3d88","02/ed/e5/02ede5c603e541982fc3d9f23c40d74d","42/48/e0/4248e0efe7406125556bd1952d7db805","6a/6e/d2/6a6ed2eeff750b75a49645c5a8ba43da","ff/f3/40/fff3402dff000b8b394cd660a3d2a465","10/c0/9b/10c09b03e147c174e547575e5b7ffca1","d7/9e/d3/d79ed359837379523906befa3cb9ad99","40/20/f2/4020f265e6fee3fb2a11da390dc3fb06","b0/0f/a0/b00fa02d96000ae21f805ae914e1788f","3e/44/72/3e447272960d5027617577e5e3ccb393","c2/0d/b6/c20db651abb87b24309af1234e36d74f","2c/57/ee/2c57eedc847bc59ab136e40355e3a1c2","28/18/ca/2818cad427c1f8957e46cd1e1133b39a"],
"QPR":["83/44/d9/8344d9ef724d512a2092e216e60428bb","10/aa/d7/10aad7ca73bac602a91e3ba47bfa70cf","ed/e9/15/ede915020d756be4b604d25659871ad9","80/9e/6d/809e6dec10d04fee24a3cb664c2068cf","6e/bb/12/6ebb1265f3964b051863ea6b78b7fced","10/6e/3e/106e3e67556401b50b417ce6574e800b","5f/06/31/5f06312ea48842f0eeb7c6be0f69d784","c7/ba/5f/c7ba5fda84796f0a31f6c84034a9409f","19/f3/92/19f392d5c7c76467057024496adf03ae","c1/c4/7c/c1c47cdd5a45244be1b475d1ef3007ca","11/ad/30/11ad3080515df1b68211afc1d43ce122","f4/07/d2/f407d2ee7905373214428bbae3d83129","3a/75/ba/3a75ba909ced6782968045bab43648ff","84/b7/82/84b78204d6db0e554165262f308d5db9","ea/0e/fb/ea0efb26f20c273632a61cdf3321e3a6","6a/bd/fc/6abdfc543d26f567874d8725029e994e","1f/ed/34/1fed348b5a185faacc5f1d453b836885","bf/80/91/bf80911fcac75ae422cffe94a530fbd4","1a/b2/2f/1ab22f764e75777ff4885757edd5ba3b","a3/47/cd/a347cda8c5ea3a8fded85b6d42dc3d05","16/5a/0b/165a0b5bfbf1e22aeac77cae9f6b1ed2","fa/95/3e/fa953ee9d89f4da98364a995385ae7be","76/e5/29/76e52928ffec4b99f0b5efe504155c15","e5/42/4b/e5424bc94e4a96807851fe0af791ea69","57/81/06/578106861629202f78fc8715ebd3d107"],
"QAS":["60/53/24/605324a3728e39ccecc1bffc8cb54108","71/07/6a/71076a43fc2089e1fa1ab051d0414e64","b7/25/78/b72578aed8e9a123b2401cb51603993f","6e/6d/79/6e6d79cf842b3ceb962b97d190c39993","97/04/9f/97049f5c403317a355056c50d845e171","ef/d8/50/efd850b63e0c519e6bdcd91dab90c950","d0/f8/fb/d0f8fbe1143119d06d1dd3aa4dd745ab","3c/30/8e/3c308e1bec3285404c3829c2e22a4914","f2/fa/e1/f2fae12dc4346d9176a78bf5506278fb","fa/93/84/fa93849465b4f27f10657143a80548b5","1f/3c/2e/1f3c2e185d8459c6f094a07f42832548","e3/6e/a0/e36ea0dac4338baab8c60f44620737de","06/4f/16/064f16c39d2d314093cf2c43143b5a0d","fd/5c/80/fd5c8032e8fa544a8840b0abf62ba7f8","10/8f/c3/108fc3212e1b30e1e2599eeb426e5960","39/a3/f8/39a3f816a58a7e92c3d76c213620dd90","d4/e7/af/d4e7af3a37f9d9efbae23d6d5388d0db","b2/fd/40/b2fd407c7255a7b5e96d279b8cbabd5f","bf/07/91/bf0791e75db405d2015a1b15c799248d","0e/1b/c0/0e1bc065cddaafec139432b846923ca0","ba/b6/be/bab6be900ed8f120e44ee7561a5abb4c","33/72/5f/33725fb320c01ac5b9df942ab4b69dcf","6a/14/18/6a14185ffab1c3a9a3bac3827c7f9fd8","22/66/b0/2266b005b546f1a2599efb39a38222dd"],
"QGU":["4f/5b/03/4f5b03d1eb9c202ea600970896d40565","a5/db/95/a5db95bb27a0fba2f2385fb1760ffe43","0e/a6/d0/0ea6d087605d3a693f04b72613a8bb57","a9/f7/aa/a9f7aa13bc3302edd0e89b074541e56d","e5/8f/eb/e58febbcd82286c09b6de362e6a1d215","cc/d9/62/ccd962528b3e7de35ccfe80d7377ac39","d4/a0/9b/d4a09b6b58865bf7f286ce24e1e02dd9","2d/5b/b8/2d5bb8b56af67f8199792b988ba9e356","73/c6/a1/73c6a147559d7c62381e27d580f77146","fa/e1/50/fae15006691158dc30d791c258c27937","d7/69/35/d76935f8f034e1c4eee9792b26f4e1ce","08/e5/46/08e546aef27713f0f18252dd46dd00c5","e0/b2/68/e0b2684f20d3f46a79091f7a70e961d2","1b/a9/58/1ba958e37c5f9f9179a2fa4a3ffaade0","5c/ca/26/5cca26e2dbe5ccc1fd4d872a7799dd47","bc/1c/46/bc1c460d0a98ab41fcab6f4130aad8d4","e8/b4/79/e8b479f10ac5e9a33cb300d3f12fd278","4b/d3/30/4bd330627d2514aeefa15e228d03fee6","92/d0/f2/92d0f257a10b6163694eb413b974fc25","27/76/02/27760281ede1fa48a1f0812add1b950d","c5/2d/72/c52d72018ee106e2b388592d0ffc9363","5e/fa/20/5efa20679074a06a174d6e74b63d03ce","ec/5f/d7/ec5fd7e8ac7b808166236d97b7ec1f5c"],
"QAM":["a2/32/3f/a2323fab9f472c400982f489c0234888","62/39/09/623909488428ff1226c7ac574a5769a8","4a/13/74/4a1374c829c6fe8581b26b4f3a53faf1","a9/f7/aa/a9f7aa13bc3302edd0e89b074541e56d","4f/5b/03/4f5b03d1eb9c202ea600970896d40565","a5/db/95/a5db95bb27a0fba2f2385fb1760ffe43","83/4c/b4/834cb465adcf91271086a72182f751af","fa/df/37/fadf377642f20d70affc6f89a094fd5a","f0/76/a8/f076a8c5f0777be865196d43b638f3dd","96/b9/1f/96b91f16753f341d897eb2f7293ce70b","4b/3b/0d/4b3b0d45230e280ec1219c453557f3e3","8c/c2/6f/8cc26fe4ba59513d7779c5892abd5012","7c/9f/46/7c9f469eea873a28c1045962a5360ab7","64/c0/ae/64c0aeb502de42177aeac67375d0def3","73/c6/a1/73c6a147559d7c62381e27d580f77146","6e/c4/bb/6ec4bb1458575f8584499174ae36002b","ce/2d/48/ce2d488880107a76bdbbeab11ef86644","0d/ae/e5/0daee541922ced7f637fdfd135670d2f","44/4e/ce/444ecedbb46d729ae3483a3240b1b5b5","50/ff/e2/50ffe2b2fb08d8d264d3b06196637133","ab/86/7b/ab867b3885895fde504b75e939054afc","42/4a/cd/424acddd18b4b9c79ca632d588a0d269","60/f0/97/60f097d71b840ff8cc2c674eefb745f4","29/d7/0c/29d70c3b89581ae81c0cf5ffcf47abeb"],
"QKS":["b0/cc/46/b0cc466368aed0d97b2a83bcf0272acb","df/97/99/df9799de7828a6e8a4b8d1b19162afc5","ce/94/16/ce94163869b8b8e6adc936d5f840e54e","8e/7b/6e/8e7b6e24eee15e7997c1ea2f2b7f6106","79/0b/bc/790bbc7718b8431dc264188a79204a19","0f/c3/11/0fc31135a16e3aa73a0cd89606e75595","42/7a/7f/427a7f7c10a9a6e6c96f031a5f27d9f6","18/cf/c9/18cfc934ac4de46019d32c91915c55d5","a4/62/d9/a462d9fdd2ba2815894db5a79e7f0e59","e1/f5/96/e1f596ae49ca15b50a5204599862d7e8","3d/81/8f/3d818f94912a4847e125fd771d3fb0bd","85/c4/f2/85c4f2f492309cc15637598230d3d7d8","a4/6c/e7/a46ce777d9da55e0dccd03a65144edd2","f2/7b/58/f27b58b4afa554527d039c479cc0f6cf","07/b0/af/07b0af6e53329a094d20506fb7083808","ff/6d/59/ff6d59c2997d5a695e8b00205eb5c3aa","ee/47/c7/ee47c7a6e1857fa24c98ec7d91fa729c","51/20/8f/51208fefb8e417207002213076e7522b","08/b0/e5/08b0e5eba92d549cb5aa3954dfc8f723","0e/57/31/0e57314288b68046f0f536f62dfc647e","fb/e3/8e/fbe38e8729b23eb38b1cf04e333b9ed2","b5/bb/37/b5bb372d847f212ab14fe3a4a72d7ed8","73/17/38/731738c84a59f774eeb6fa68083b6e8e","8b/c4/cd/8bc4cde41bfc27b8fc2bf49676e77e83"],
"QCW":["fd/2d/36/fd2d360d63f431823f99304793e1ee3c","4b/c0/78/4bc078788e8fb98c4b667c2c995bc440","37/2c/56/372c56a811fa98146976c64949bb5070","8e/7b/6e/8e7b6e24eee15e7997c1ea2f2b7f6106","df/97/99/df9799de7828a6e8a4b8d1b19162afc5","3a/b4/1c/3ab41ce0690a63e83ff2b174ae9bda61","20/3d/2c/203d2c79d23d74e7264449fdb8526bbe","d3/c5/0a/d3c50a9303417a014f1478bdb4495801","c1/03/ea/c103ea8f075ca1f57f6fec44b6b64364","03/a6/24/03a624766cf7a5e55d32696a0fe9f867","aa/63/82/aa6382fa64c4328ebbe554cbbde85bb7","a9/99/97/a99997f94ded37bfae0b11d09d84fd85","f6/0c/00/f60c0061f7d0543dde99c5fd67909600","95/2a/24/952a2468d022304ae0e05ed2d1eeb66d","8c/90/7d/8c907d2972a02375f73b467585318eeb","cb/a5/27/cba52782bbb2332e11109de490534de3","d1/3c/dd/d13cddba48caae86c37156eaa9a43df9","e1/f5/96/e1f596ae49ca15b50a5204599862d7e8","9d/b7/54/9db754b420013ba1401367addccd8b2f","bd/7c/bb/bd7cbb1e3931301ff6e6d7ae55d0d6ee","9b/9e/d0/9b9ed092db98fafc5a22b0e4ed972323","9f/6e/3a/9f6e3adb9b8ea8a0d1fb2a034617cc66","2a/77/19/2a7719d16a1e0692a170a9703d7f8f9f","4b/76/29/4b7629d627ee927619bf1cbf8dbdc1eb","b8/26/e6/b826e6bbe3acef45afe8e11a20180f25"],
"QCR":["8d/bf/39/8dbf3901f237998b092285055b94e5e7","e7/3d/dc/e73ddcb2344a30fcdbcb9405b4cfa122","59/4b/1a/594b1aaead1e8633cfee0c401ae3a86b","a1/81/e4/a181e4c29f3ce99108c47623c2092d30","b9/f8/81/b9f881cf826f448b71c072e02d0842d8","de/16/dc/de16dcb43afde3169c9ac84c3ea73e4b","ae/19/21/ae19216770c0aa398f71ca03d9bba7c8","44/53/7e/44537e2ad7bf3ea802cacdbaeea89733","35/62/01/356201857ba2b939a7ce41f8355948d2","7d/c6/54/7dc654167ccf4b5b281d049c93089d63","38/b4/41/38b4419d19827f6f494443953ba92308","3f/4c/51/3f4c510657de4ed809b1844659f900dd","3a/b6/0a/3ab60a9cd94cebcc4bd7cd8c673db409","de/fb/0a/defb0a5883b01568a2558548576c1128","48/83/3f/48833f2c394e7671613b09827a707c35","28/80/d4/2880d486970f3c9ae8a81dfd2cc5175b","44/76/86/4476864d857e0172e80c30075f12c157","26/66/23/266623476ac570e32ca34814926e3bfd","80/f1/07/80f1070dcf6692ee7a576f449979651a","df/3c/6e/df3c6e8c59456c0ec9c02009fd62e424","f1/9e/49/f19e49401f1fb69004044229b09f77f9","b1/e2/5a/b1e25ad971e049f7f7b22141650ff31e","7e/45/00/7e45005a59c978e022f3b3d516d4a546","7d/7c/de/7d7cde053d8302fef604e7374a2c5a60","af/15/99/af1599d05559d18fc4d8df25d9b88852"],
"QHD":["7f/28/91/7f28913bd3f0cd3526b46f33799cd36f","7c/bb/18/7cbb18627d89e8d570325f576560567c","e6/a5/29/e6a52983c4dff928a45a646242d9b6c5","44/a9/e2/44a9e2b895d265edc0bfabfb5d1cd13c","16/2f/91/162f910d425274d6f768182142b285ce","53/b8/d3/53b8d327b9174db89fc9c54dae4bcf6e","dc/aa/be/dcaabeed36b07c380f3ac14f52b95781","9c/40/31/9c40314d7a431d9bb8d0d586e8df6118","1d/54/82/1d5482f03d09c5b67f655520bf131737","d4/45/b1/d445b17d3ed0a02375f2431857bcd938","71/1f/37/711f37c7bb4218cdf682e762e4eaa9ed","db/67/f9/db67f950ce918fa69c3683af5e345e2e","00/0f/96/000f966617831e2f194cbf42bfe7a676","5a/79/f2/5a79f2c4229b6382df20778875f6bcd8","aa/1d/31/aa1d31731444692e35f0a251cf4835e1","ba/1b/b2/ba1bb2bf863fb7d15fe83f3486cea0e4","cc/f7/b5/ccf7b53f612e57d6dd8dbdf04a5108fb","15/94/0f/15940fcb1f5f24257477acf9117d014a","fa/e4/15/fae4154b08b30c17bff6b23b44a9df4a","bd/2f/1c/bd2f1c59e94b6b9d11ee7d247b9f5083","d4/7e/25/d47e25c792e43aec269d45179dd2158d","25/69/ba/2569ba8af0d2d2b1735dcd751d886371","f7/e2/fd/f7e2fd72fde95ba05f186057da90fa83","49/df/ed/49dfed0162e7ce6dbaa51ebdb2b15ce2"],
"QAT":["34/62/9b/34629b8c81bfbafd30860a9c93b4ee72","55/30/0a/55300a79460c9aec07f0cd7f0d78fdc5","c6/77/d7/c677d7438fe7eba3db6302e9ac041cdb","1a/cc/a3/1acca3147104f20d6f3f99275b73c116","86/f6/15/86f6152ccce2f3458ecb27754e62bd41","42/81/a1/4281a1c43ad9227e484285b18c63313e","db/f9/f5/dbf9f5fd62c85061d6a8d21a9a692da1","bf/52/ef/bf52efa5edc293be867be8e9eb5c15d4","80/7e/06/807e06ae5b0081640c282c6c686d767f","21/a6/fc/21a6fcbf658e192dd0f4aa08e287c2d4","10/a7/fd/10a7fde4b91dad25eff3dcc101f0053d","f9/eb/49/f9eb495b75f3cd5fee3fd4f48501aa4e","c1/67/3d/c1673d62d0a0a28eb83d5150de921477","70/01/9d/70019df92c6c440252a0eb4842e90ded","06/c2/cb/06c2cb54017e490960cc8f9cf803dc6a","f4/5f/c4/f45fc443f95db9ad1e91eda71738ce67","1d/ce/a2/1dcea25501acbc30e774ff1098382e77","05/de/42/05de42a676933fd77a07f587d2bb0159","ff/ee/58/ffee58699a638e6e651ab90ecbae7627","70/20/94/702094603a4cbac372be336ad69f8b78","83/23/3c/83233c811dbfad02cc1bacc6f25ef8ba","3a/55/23/3a5523ecdb94da1ddd63d817e768673a","fc/5e/40/fc5e40c931bcc7ad8f03bf1998f144c9"],
"QDM":["60/5b/cb/605bcb3f01521042d2134d61d62ec433","af/1d/4c/af1d4ca664edb439eed7c1856ee595c5","c5/5d/4e/c55d4e4b10a33462fb67d119d617be73","91/ff/3d/91ff3d6bd33e27fe96bb6acc81430bbf","35/d6/08/35d608df07322fdfca3240b3a19d68d9","62/d6/34/62d63484eb22d19121af533ddd4d4420","c7/fb/db/c7fbdbc1e481e94a959f0b4ed705831d","a4/6a/8e/a46a8e2dd2a42f0a560f63b968a64707","ec/4e/ec/ec4eec8f23323105974a17fc644419b9","a7/bd/9e/a7bd9e15378bcd763c5ce6422b67a87e","30/73/73/3073730a0b9d37a27d176e48787e7b12","ca/e7/91/cae79177422e28524eb5c5bca1920e58","6e/7f/21/6e7f211b16215e1e408eb1590cadfab0","fa/8d/ea/fa8dea9b0f0b868d2e4c49e1fc439076","6b/a0/7d/6ba07d8f4ca13ca0021da6e3418f56b1","6f/e8/81/6fe881f89b92fbdf138d8d8c915ca597","e1/c0/f0/e1c0f02d38d700d5ff96eec2589ff388","f9/52/14/f952147744536667e79e8e8fd0f1ac37","a0/12/7e/a0127ec0d6243813e41d0b2dc03d316b","32/bd/87/32bd8791ad8b9aebd367da0ab7e94906","5f/f7/22/5ff722953a82bfae712e540826358325","1d/cd/58/1dcd58052e941945ae81e0a6a9eb4b89","08/ab/b2/08abb23b63dcbe8687ff0938d7d1006d","5a/11/d2/5a11d2297773c0a010a477ad5065307c"],
"QCH":["22/e8/87/22e887a78ba240737c67d4b8d61a58d5","3c/af/28/3caf28cf285f0724cba9987d32b1e2f1","c0/aa/06/c0aa069c9e9b2fb2693e33efe5719ea2","32/bc/99/32bc9926fd50eb75dfa266ed0aa3b6c8","8d/0a/19/8d0a193511347ca9342c75a12d518554","55/97/9e/55979ef0cffdbf1d7a57ca5ae022af2a","f5/70/9f/f5709fa60f8d3912a63584406fef6bd9","2d/30/10/2d301030d656ce3b8e652596aae0497c","39/4d/21/394d21336c7d3c3ba50b951603edaa4c","f7/e7/5f/f7e75f5d36b43f0c7ca7473d140d5e08","ee/07/29/ee07298aefa0023611566a41d0d49739","b5/ff/8a/b5ff8a8c5809b1dad44b33d5f75891c9","67/94/52/6794521ef5690f2e1a1faddd09f34bba","23/7c/08/237c082e81f4a6cd3bac8c7a60741b29","2f/ef/5f/2fef5f0713a9c799b12aec58369760e3","59/0e/82/590e8226168f8dbccb5e948b8f217038","bb/3f/55/bb3f55b5c44ab1be9d2f099e6ed80a99","86/ac/4a/86ac4a32abb58d1061c84a5b36d29bb9","c0/76/eb/c076ebc1440ce3790e5ec9d23f14db9d","52/d1/cf/52d1cf3b4c5407044c5e7b6c0e4c8425","c5/60/eb/c560eb55eae762c9e236ef78a8e5fc75","14/5e/47/145e47c53098d1dedc916da385dde26f","52/c9/3f/52c93fd363b3bef34453174ccd8ee549"],
"QCC":["5a/f4/26/5af426acff0851614ba879247316adf8","3d/62/46/3d6246445462ff80a6e211beeb54b0ec","8f/2d/83/8f2d83009ac4afe6658069f3d6852d11","22/e8/87/22e887a78ba240737c67d4b8d61a58d5","d0/c2/49/d0c249bd50fc4fca1e7f3629574045c3","59/0c/ff/590cff5891b97544ad80896bc5a30914","ae/19/21/ae19216770c0aa398f71ca03d9bba7c8","45/b8/dd/45b8dd4bf089bc97437862a1cfc648d9","05/16/8b/05168b6fb57b32dabb3036a562c9ad40","ca/c4/81/cac481214477bfa396c79ed7bf0dac4b","06/de/bc/06debc5c028d18538cca144cdc31fa41","57/33/86/573386bf5eb263285a914c6caafec01a","f3/71/52/f3715254c2a1ecfa57bc9958bf0327d3","7d/c6/54/7dc654167ccf4b5b281d049c93089d63","f1/89/bd/f189bd31bb4970b6e6d2efe7e79ef283","82/dd/34/82dd34803153ff16919b8f6f0d813365","e8/98/c1/e898c1354e1a19569a6ae202280fb04e","d8/88/d2/d888d2eb89ced15a4c8f161f6a1670fa","1b/06/6f/1b066f259a9a425955a506304142396b","a0/ca/c1/a0cac15ad88ae36030ff9482a7ee7a81","3a/b6/0a/3ab60a9cd94cebcc4bd7cd8c673db409","a0/3b/4e/a03b4eb9f80776cbc09f4d1fb415a2e9","14/5e/47/145e47c53098d1dedc916da385dde26f","ff/84/70/ff8470e15c4290192d97f1aa363df662","2a/cd/e1/2acde1be3fffaeb68f4cbd7710a7093b"],
"QCO":["49/52/f9/4952f9bdd6237b060b34511824ca7cd1","c7/5a/c5/c75ac551417b502e091d530fab7739f3","00/51/c5/0051c554042c3413f9f7694d2ea0ac2e","cd/36/4d/cd364dcb98b9cd297c9910b9bb23ab2b","b1/08/fc/b108fc34912794f99d8f8806fe17f438","23/8f/c4/238fc4e48234ae4f78ce2722ca0f4f35","88/bc/19/88bc199ca9ff5fad8458280a640fc05d","32/bc/99/32bc9926fd50eb75dfa266ed0aa3b6c8","48/81/e5/4881e540637d3e9cbd122bc3e1a4f3d8","43/fc/7f/43fc7feecb4a853abf3867a067c343fb","9a/ef/fb/9aeffb870d3c5b613729dd423e33baf9","a7/33/db/a733db42d3cf53459654430a4d885058","8c/3b/17/8c3b17fc0cb3f24fdf69a99ab6427dc6","c6/90/b4/c690b477b0b8fa7451eb7957df8492d3","40/24/8a/40248a8549248b80c4e6987a3e6b642f","5a/f2/49/5af249578f8d341f365a12db36e26222","ef/99/bd/ef99bd295700231f685f25cc0d8f05dc","e0/43/c5/e043c517bdee7edeb084de780ba9634f","ba/70/cf/ba70cf50771c142ebda39c7ebc2d7c98","b4/80/10/b48010035a75370d1974c945820de424","03/d2/89/03d289fa0293890d219f3a3001f635e5","15/6b/40/156b4048967a6dc01ac1de3f277dee28","ca/c4/81/cac481214477bfa396c79ed7bf0dac4b","32/b3/e4/32b3e4c514e03a2ace73f09f8e26553a","9e/ec/01/9eec01a0930ca8909d1cead3604b591f"],
"QCP":["d8/12/68/d81268e747458a54d5251651dceb1fdb","53/ee/06/53ee06a978a7a2836c670c47c9cfb513","42/98/61/4298615525fb9247104935d5450046c8","84/29/68/84296872c5ed502ba042c8c9edb41efe","d8/56/1d/d8561d22719ae3999ef5a701d9ccce07","1c/3d/19/1c3d19e1ad33e45a4a040469b896847d","61/e0/5b/61e05b5dd23a7e301898b5da26beb5e0","ce/50/f5/ce50f557f1f7141bcbd72b27f7ec68fc","33/39/fb/3339fb7c1de08b96330c462d68b56c51","91/af/c7/91afc716ec11fdb5a5b48df9b199d73d","dd/c2/0c/ddc20c892d45dc13f1fec21b083f2dd5","29/c2/88/29c28866a15ecaade110f4b74755747c","01/a0/fb/01a0fb7a1bcb9d9e29d31ec8f1f022a2","d6/14/9d/d6149dd7dda41bdfdfe4063b2367f76d","4c/b6/dd/4cb6dd675a84b6e324139f8da6cae129","19/1a/4e/191a4ece017268b0f28ea2078c86a6ca","a1/a9/1d/a1a91df6bfc86d64abc0e30848773d81","d3/ad/6b/d3ad6b2657d998ebe1488729de9e5509","23/cd/3d/23cd3d6a7509dc13530548aee81c56ec","c9/a1/82/c9a182dcef54aa838a5c6cee5562f897","4b/7e/4c/4b7e4cd5a728d45200e94a84a8bf9822","ff/18/22/ff182237087dd578f2ee1cafdc76d982","89/b5/b1/89b5b179d47b6d99ad465249a3512e70","6c/5d/16/6c5d16bdb0a7acd42b4b5c9103e8bb27"],
"QSC":["20/3d/2c/203d2c79d23d74e7264449fdb8526bbe","d1/3c/dd/d13cddba48caae86c37156eaa9a43df9","5d/76/09/5d7609d79a3704b65b6a8a2699abf1f6","d9/d8/33/d9d833a521d82e8bf1f2e67eab59d717","1f/6d/e1/1f6de1dcdee4857cad1dd7a359384eca","75/7d/95/757d9528cf77466e94f94c76226c66c5","4d/1f/f6/4d1ff678f7bb0bda0f6fa31d43f026d0","45/99/2a/45992ae70c12c0e71f02934b054cbd01","95/2a/24/952a2468d022304ae0e05ed2d1eeb66d","bf/b8/8a/bfb88a19d24eb43df5886f15ef9b83c6","f7/46/15/f746154a77ca3970fe273fb6ac3ea6ba","89/7c/53/897c536901e28069c337f3655e43347d","43/f2/73/43f27362b5f19d3540c26efd71e5c6df","50/03/77/500377276c21511bdfb4a886e13e24c9","37/2c/56/372c56a811fa98146976c64949bb5070","65/00/a1/6500a1c4e5201036882c2b7d8dec7c01","02/2d/31/022d3138f08c0a1248535617fd8a7510","e8/0a/db/e80adb37254577049f19f569e9ccf3fb","c7/8c/96/c78c962afe0ce2fe7502b7b94e282593","5d/54/e1/5d54e197483153986b1ed206c7ac0f81","3d/b0/da/3db0daa2bfc05a7549bdfa17383e1c0a","a1/d5/08/a1d5080a8c71561d5a5966f16c25898f","fa/e1/50/fae15006691158dc30d791c258c27937","3e/08/4c/3e084c733da1150e66b6e639aaf4494c","9b/ae/33/9bae33bde6ce87a43a15dada21f618ab"],
"QVW":["00/40/d4/0040d4dded7dff4592c0e9eabeb2bb7d","bb/d1/6f/bbd16fa597767beb4f0af7ecd718e4a7","c2/b9/55/c2b9559bf524fac9d399f5167d6df61a","c7/59/26/c75926209001eac288223c2b9b151a17","d0/34/21/d03421822fb9be240e55a1b869d0abf9","1e/9f/6c/1e9f6c0ca5793637d1dc268eec610955","6e/9d/d6/6e9dd6962299660c88782b5365e357fa","7b/dc/20/7bdc208961b1965984ea4d6436b36e3b","95/2a/24/952a2468d022304ae0e05ed2d1eeb66d","c5/10/4e/c5104e77b759798ce520e743212b3403","e6/43/82/e643824214255d1ac411c7dff42389e5","8a/34/cd/8a34cd98477c89a6e6c204f86661e053","41/04/45/4104451019dcab155d7ea97eecb1b959","3a/39/14/3a391415d1aeedb0de6c4479c91d3559","00/d9/db/00d9db80dfc6e8c25cb1953eca63a1ac","72/2d/4d/722d4dccf627d720eee3f1d45a6acfe3","26/a3/75/26a3750ff921fbd6a52ca81ba89029f9","80/f8/d4/80f8d4582bafc1a2189a17e57e33c084","13/b0/52/13b0526fd231d5740fc3b6e71706d662","5c/28/f9/5c28f9282c8258548e2d2d7ee9de787c","87/7d/2d/877d2d7c9fb9e49c4ae56483e2437564","4e/ea/e8/4eeae869cf7f0f9510b1398efec23a0d"],
"QCT":["71/2b/b2/712bb21f912d4dc1f91846cab587ba84","17/24/3b/17243b5ab6c651e16e9775a92e50c76a","55/3e/ff/553eff220cef92ee2ddf2fd07024c3a1","dc/c0/7c/dcc07c45d85709cb304a64c60240e62a","62/3d/e8/623de86fade139ce2168ba1a1b901447","7e/0b/55/7e0b55032730153d3085c6d3a4170619","7b/8a/62/7b8a62dfba196a93521c94691b51c483","7f/4d/68/7f4d681a536bc3ef2dec9dc38d2a51f2","59/25/4f/59254f63d56ad34d4c24a86788b84cb7","25/a7/43/25a743e9b75eb7c3dcfb5d112ff8511f","a2/e6/0d/a2e60d487c3b3646a4f41dc4be661849","c1/b6/77/c1b677a483ca21fec272014d3358a12f","46/7d/d3/467dd3bef2b1086c0b84462683615a3b","6f/4c/a2/6f4ca2b41741b6d61c8ba7ed092eccbc","f9/04/9f/f9049f155b9cd9e08620c6d330a6f44e","d9/66/06/d966063f13b8dc957f410bfec382c39a","77/f5/31/77f5317123f565a501d1c3ad2ecf50d7","1c/4e/74/1c4e74c7b338b144e1d6c77b64b9b98b","2b/0e/d4/2b0ed487b1dd9a8dda191f7639a3f614","20/48/62/20486247ff5c76240ae6517f50ceec61","ba/5b/06/ba5b06678d6e1a7070a5f762ca05f089","1d/94/23/1d9423c580790c4af14d3ddab7e3f621","09/98/55/099855c47de9a948b5d8cb9e51ce1411"]
```
- Linhas para o `BOARDS` do `tools/moodboard.mjs`. A subfase sugerida é '4.1c', a que está em trabalho; ajuste se as buscas entrarem em outra:

```js
  { id: 'QRD', label: 'Busca: red dot sight rifle', url: 'https://www.pinterest.com/search/pins/?q=red%20dot%20sight%20rifle', phase: '4.1c' },
  { id: 'QHO', label: 'Busca: holographic sight rifle', url: 'https://www.pinterest.com/search/pins/?q=holographic%20sight%20rifle', phase: '4.1c' },
  { id: 'QAC', label: 'Busca: acog 4x scope rifle', url: 'https://www.pinterest.com/search/pins/?q=acog%204x%20scope%20rifle', phase: '4.1c' },
  { id: 'QLP', label: 'Busca: lpvo 1-6x scope ar15', url: 'https://www.pinterest.com/search/pins/?q=lpvo%201-6x%20scope%20ar15', phase: '4.1c' },
  { id: 'QMG', label: 'Busca: magnifier flip red dot', url: 'https://www.pinterest.com/search/pins/?q=magnifier%20flip%20red%20dot', phase: '4.1c' },
  { id: 'QRT', label: 'Busca: sniper scope reticle view', url: 'https://www.pinterest.com/search/pins/?q=sniper%20scope%20reticle%20view', phase: '4.1c' },
  { id: 'QNV', label: 'Busca: night vision scope view', url: 'https://www.pinterest.com/search/pins/?q=night%20vision%20scope%20view', phase: '4.1c' },
  { id: 'QTH', label: 'Busca: thermal scope view', url: 'https://www.pinterest.com/search/pins/?q=thermal%20scope%20view', phase: '4.1c' },
  { id: 'QLS', label: 'Busca: laser sight beam smoke', url: 'https://www.pinterest.com/search/pins/?q=laser%20sight%20beam%20smoke', phase: '4.1c' },
  { id: 'QIR', label: 'Busca: ir laser night vision rifle', url: 'https://www.pinterest.com/search/pins/?q=ir%20laser%20night%20vision%20rifle', phase: '4.1c' },
  { id: 'QWL', label: 'Busca: weapon light rifle', url: 'https://www.pinterest.com/search/pins/?q=weapon%20light%20rifle', phase: '4.1c' },
  { id: 'QFL', label: 'Busca: weapon mounted flashlight', url: 'https://www.pinterest.com/search/pins/?q=weapon%20mounted%20flashlight', phase: '4.1c' },
  { id: 'QPR', label: 'Busca: pistol red dot optic', url: 'https://www.pinterest.com/search/pins/?q=pistol%20red%20dot%20optic', phase: '4.1c' },
  { id: 'QAS', label: 'Busca: ak side mount optic', url: 'https://www.pinterest.com/search/pins/?q=ak%20side%20mount%20optic', phase: '4.1c' },
  { id: 'QGU', label: 'Busca: gunsmith weapon customization ui', url: 'https://www.pinterest.com/search/pins/?q=gunsmith%20weapon%20customization%20ui', phase: '4.1c' },
  { id: 'QAM', label: 'Busca: weapon attachment menu game ui', url: 'https://www.pinterest.com/search/pins/?q=weapon%20attachment%20menu%20game%20ui', phase: '4.1c' },
  { id: 'QKS', label: 'Busca: cs2 knife skins', url: 'https://www.pinterest.com/search/pins/?q=cs2%20knife%20skins', phase: '4.1c' },
  { id: 'QCW', label: 'Busca: cs2 weapon skins', url: 'https://www.pinterest.com/search/pins/?q=cs2%20weapon%20skins', phase: '4.1c' },
  { id: 'QCR', label: 'Busca: custom cerakote rifle', url: 'https://www.pinterest.com/search/pins/?q=custom%20cerakote%20rifle', phase: '4.1c' },
  { id: 'QHD', label: 'Busca: hydro dipped gun', url: 'https://www.pinterest.com/search/pins/?q=hydro%20dipped%20gun', phase: '4.1c' },
  { id: 'QAT', label: 'Busca: anodized titanium knife', url: 'https://www.pinterest.com/search/pins/?q=anodized%20titanium%20knife', phase: '4.1c' },
  { id: 'QDM', label: 'Busca: damascus steel knife', url: 'https://www.pinterest.com/search/pins/?q=damascus%20steel%20knife', phase: '4.1c' },
  { id: 'QCH', label: 'Busca: case hardened receiver', url: 'https://www.pinterest.com/search/pins/?q=case%20hardened%20receiver', phase: '4.1c' },
  { id: 'QCC', label: 'Busca: color case hardened receiver', url: 'https://www.pinterest.com/search/pins/?q=color%20case%20hardened%20receiver', phase: '4.1c' },
  { id: 'QCO', label: 'Busca: color case hardening', url: 'https://www.pinterest.com/search/pins/?q=color%20case%20hardening', phase: '4.1c' },
  { id: 'QCP', label: 'Busca: camouflage pattern swatches', url: 'https://www.pinterest.com/search/pins/?q=camouflage%20pattern%20swatches', phase: '4.1c' },
  { id: 'QSC', label: 'Busca: gun skin concept art', url: 'https://www.pinterest.com/search/pins/?q=gun%20skin%20concept%20art', phase: '4.1c' },
  { id: 'QVW', label: 'Busca: valorant weapon skin', url: 'https://www.pinterest.com/search/pins/?q=valorant%20weapon%20skin', phase: '4.1c' },
  { id: 'QCT', label: 'Busca: claymation weapon toy', url: 'https://www.pinterest.com/search/pins/?q=claymation%20weapon%20toy', phase: '4.1c' },
```
- Imagens repetidas. O asterisco marca um pin que já está num board antigo do projeto:

```text
QRD10 = QAC7 = QLP18
QRD18 = QPR8
QRD25 = QAC14
QRD7 = QPR4
QRD9 = QHO24
QHO19 = QPR1
QVM1* = QHO18 = QWL14 = QGU17
QAC10 = QLP7
QAC18 = QLP11
QAC6 = QLP9
QRA2* = QAC19
QRS8* = QTM9* = QRA1* = QAC3
QTM4* = QAC2
QTM28* = QLP20
QTM30* = QLP8
QRT13 = QNV9 = QTH15
QRT14 = QTH22
QRT17 = QNV20 = QTH20
QRT9 = QNV1 = QTH10
QNV15 = QTH9 = QIR14
QNV3 = QTH12
QHS6* = QWL1
QRS13* = QWL4
QTM19* = QWL23
QVM6* = QRS10* = QWL9
QGU1 = QAM5
QGU10 = QSC23
QGU2 = QAM6
QGU4 = QAM4
QGU9 = QAM15
QKS10 = QCW18
QKS2 = QCW5
QKS4 = QCW4
QCS11* = QCW15
QCS3* = QCW10
QCS8* = QCW6
QCW14 = QSC9 = QVW9
QCW17 = QSC2
QCW3 = QSC15
QCW7 = QSC1
QCK1* = QCR9
QCK10* = QCR17
QCK15* = QCR5
QCK16* = QCR21
QCK17* = QCR22
QCK2* = QCR10 = QCC14
QCK22* = QRS27* = QCR13 = QCC21
QCK3* = QCR1
QCK4* = QCR2
QCK5* = QCR7 = QCC7
QCH1 = QCC4
QCH22 = QCC23
QCH4 = QCO8
QCK13* = QCC10 = QCO23
QCK24* = QCC2
QCK6* = QCC1
QVS13* = QVW5
QVS5* = QVW3
QRF4* = QCT5
```
  Total: 59 imagens repetidas.

### Inferences
- Se o dono quiser um board menor para as skins, dá para deixar de fora QCH e QCC e ficar com QCO, e dispensar QCR, que repete 10 pins do QCK. Mas a convenção do projeto é guardar a primeira página inteira de cada busca, então as listas acima estão completas.

### Gaps
- A subfase dos boards (`phase`) e a seção do `moodboard.md` onde as observações entrariam ficam para o dono decidir.
