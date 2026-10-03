# Acabamentos reais de armas e facas e padrões de camuflagem: catálogo de referência para skins procedurais (MASSACRE)

Convenções usadas nestas notas:
- **[MARCA]** marca nome comercial, marca registrada ou padrão proprietário. Serve só como referência e **não deve aparecer no jogo**. No jogo usamos nomes genéricos.
- **"medido por nós"** indica valor hex que extraímos de uma imagem publicada pela fonte citada, pela mediana ou por k-means em CIELAB. Não é um valor publicado pela fonte e é sempre **aproximado**: depende de foto, iluminação, tela, JPEG e desbotamento.
- **"calculado por nós"** indica estimativa física por modelo de filme fino. O método está descrito em Inferences.
- **"via resumo de busca"** indica que o fato veio do resumo do buscador sobre a página listada, sem leitura integral da página (403 ou bloqueio). A confiança é menor.

---

## 1. Revestimentos e tratamentos de metal em armas: aparência, cores e desgaste

### Takeaway
Os acabamentos de arma se dividem em duas famílias com comportamentos visuais bem diferentes:
- **Camadas aplicadas por cima:** Cerakote, Duracoat, hidrografia, pintura, PVD/DLC, niquelagem e cromagem. São opacas, têm cor própria e, no desgaste, lascam nas arestas até mostrar o substrato.
- **Conversões ou filmes finos do próprio metal:** oxidação (bluing), azul de nitrato, têmpera colorida, parkerização, nitrocarbonetação e anodização. Nelas a cor vem da química ou da interferência de filme fino, e o desgaste é um polimento gradual até o metal nu.

Para cores "de catálogo" (Cerakote) só existem fotos oficiais de amostras. Os hex abaixo foram medidos por nós e divergem entre fontes em até ~10–20 L*. Titânio anodizado e cores de revenimento seguem uma sequência física de interferência (bronze → roxo → azul → azul-claro → dourado → rosa → magenta → azul/teal → verde). Essa sequência é reproduzível com `iridescence` do three.js.

### Cited Findings

#### 1.1 Cerakote, Duracoat e revestimentos cerâmico-poliméricos
- Cerakote se define como "Polymer-Ceramic coating" aplicável a metais, plásticos, polímeros e madeira. As séries mais populares são a **H-Series** (cura em forno, bicomponente, "the most durable of the standard Cerakote products") e a **C-Series** (cura ao ar, "High Temp Firearm") — [Unique-ARs](https://unique-ars.com/how-to-choose-the-right-gun-coating/)
- A **E/Elite Series** é descrita como versão aprimorada da H: cerâmica bicomponente de cura em forno, para peças de tolerância apertada e baixo atrito. A C é a opção flexível de cura ao ar — [10xem](https://10xem.com/library/cerakote-series/)
- Os dados de teste da Elite usam 0,75 mil (~19 µm) de filme seco, com cura recomendada de 300 °F por 2 h (via resumo de busca) — [Cerakote Elite TDS](https://images.nicindustries.com/cerakote/documents/119/cerakote-elite-tds-dt20200115005709041.pdf?1579049830=)
- A própria Cerakote avisa que suas amostras são "aluminum panels sprayed with Cerakote for DEMONSTRATION AND COLOR REPRESENTATION PURPOSES ONLY", ou seja, não servem como especificação colorimétrica — [Cerakote KB](https://www.cerakote.com/resources/knowledge-base/233/application-guide-pattern-splinter-camo)
- **Duracoat [MARCA]:** bicomponente, aplicável em metal, plástico e madeira, "over 300 colors", cura ao ar, espessura ótima 0,001″–0,008″ — [Unique-ARs](https://unique-ars.com/how-to-choose-the-right-gun-coating/)
- **GunKote (KG) [MARCA]:** série 2400 de cura em forno, monocomponente, que "will flex up to a 180 degree bend"; série 1200 de cura ao ar — [Unique-ARs](https://unique-ars.com/how-to-choose-the-right-gun-coating/)

#### 1.2 Cores Cerakote: hex medido por nós nas imagens oficiais de amostra
Duas fontes trazem as fotos oficiais do painel curvo ("S-curve") com reflexos:
- **A:** imagens da tabela de cores do aplicador [acoating.com](https://acoating.com/cerakote-colors/cerakote-color-charts.html) (renderização antiga).
- **B:** PDF "Cerakote Color Chart – Updated April 2023" de revendedor ([taylorfreelancestore.com](https://taylorfreelancestore.com/content/Cerakote%20Color%20Chart%20-%202021.pdf)).

Método: média linear dos pixels do painel entre os percentis 35–65 de luminância, excluindo fundo e reflexos extremos. A coluna "Sugestão" é a média linear A/B. Todos os valores são **aproximados**. Os nomes são da Cerakote **[MARCA]** e vários contêm marcas de terceiros (Magpul, Sig, Savage, NRA, Vortex, "Stormtrooper").

| Código | Nome de referência (não usar no jogo) | A (acoating) | B (PDF 2023) | Sugestão | Observação |
|---|---|---|---|---|---|
| H-146 | Graphite Black | #484546 | #46413B | **#474341** | fontes consistentes |
| H-190 | Armor Black (arquivo rotulado "Military Black") | #434040 | — | #434040 | |
| H-234 | Sniper Grey | #626569 | #746F6C | **#6B6A6B** | |
| H-237 | Tungsten | #6B6B6B | #938A83 | #817C78 | divergência grande; aspecto metálico |
| H-262 | Stone Grey | #515459 | #777571 | #666666 | |
| H-227 | Tactical Grey | #70767F | — | #70767F | |
| H-219 | Gun Metal Grey | #9B9C98 | — | #9B9C98 | metálico |
| H-210 | "Sig Dark Grey" [marca de terceiro] | #393836 | — | #393836 | |
| H-188 | "Magpul Stealth Grey" [marca de terceiro] | — | #4A4749 | #4A4749 | |
| H-148 | Burnt Bronze | #7B6951 | #866E56 | **#816C54** | metálico (flocos) |
| H-293 | "Vortex Bronze" [marca de terceiro] | — | #695445 | #695445 | metálico |
| H-294 | Midnight Bronze | — | #6E5848 | #6E5848 | metálico |
| H-149 | Copper Brown | #81685A | — | #81685A | metálico |
| H-226 | Patriot Brown | #332C25 | #846E57 | **não usar média** | fontes muito divergentes |
| H-265 | Flat Dark Earth (arquivo antigo "Troy Coyote Tan") | #8A6A48 | #A58E78 | **#987E63** | |
| H-267 | "Magpul FDE" [marca de terceiro] | #9D8D75 | #A88C6B | #A38C70 | |
| H-235 | Coyote Tan | #97846F | #B39A80 | #A59078 | |
| H-199 | Desert Sand | #BAA891 | — | #BAA891 | |
| H-236 | O.D. Green | #565243 | #6A604B | **#605947** | |
| H-232 | "Magpul O.D. Green" [marca de terceiro] | #51504B | #5A503D | #555045 | |
| H-231 | "Magpul Foliage Green" [marca de terceiro] | #5A564A | — | #5A564A | |
| H-240 | Mil Spec O.D. Green | #59584E | — | #59584E | |
| H-200 | Highland Green | #53604A | #6B705B | #606953 | |
| H-170 | Titanium | #9B9995 | — | #9B9995 | metálico |
| H-185 | Blue Titanium | #4F5155 | #6D777C | #5F666B | metálico |
| H-151 | Satin Aluminum | #CACED3 | #BAADA2 | #C3BFBC | metálico |
| H-150 | "Savage Stainless" [marca de terceiro] | #B0B1AE | — | #B0B1AE | metálico |
| H-122 | Gold | #E1AA3C | #CE9E64 | #D7A453 | metálico |
| H-238 | Midnight Blue | #101012 | #2A2B2A | — | as duas fotos saem quase pretas; o azul não aparece |
| H-220 | Ridgeway Blue | #2B4B88 | #5785A4 | #456D97 | divergente |
| H-171 | "NRA Blue" [marca de terceiro] | — | #3F88B3 | #3F88B3 | |
| H-221 | Crimson | #7B171A | #B94231 | — | divergente |
| H-216 | Firehouse Red | — | #CA3E2E | #CA3E2E | |
| H-297 | "Stormtrooper White" [nome evoca marca de terceiro] | — | #E9E7E5 | #E9E7E5 | |
| H-140 | Bright White | #D2D7D9 | — | #D2D7D9 | |
| H-242 | Hidden White | #CDD1D2 | — | #CDD1D2 | |
| H-168 | Zombie Green | #70BB20 | #A1C052 | #8BBD3F | |
| H-141 | Prison Pink | #FC8AAE | #F86C95 | #FA7CA2 | |
| H-217 | Bright Purple | #77558E | #A67AAE | #91699F | |
| H-346 | HiVis Orange | — | #FD7837 | #FD7837 | |
| H-243 | Safety Orange | #E85C1D | — | #E85C1D | |
| (FS) | arquivo "H-30188_FS_Field_Drab" | #766550 | — | #766550 | cores Federal Standard 595 em Cerakote; rótulos conforme o arquivo |
| (FS) | arquivo "H-33446_FS_Brown_Sand" | #C7AF94 | — | #C7AF94 | |
| (FS) | arquivo "H-36357_FS_Grey" | #C7C7BB | — | #C7C7BB | |

Fontes: medições nossas sobre [acoating.com](https://acoating.com/cerakote-colors/cerakote-color-charts.html) e o [PDF de revendedor](https://taylorfreelancestore.com/content/Cerakote%20Color%20Chart%20-%202021.pdf).

#### 1.3 Padrões aplicados por pintores (stencil e técnica)
- Aplicadores oferecem estes padrões:
  - variações de MultiCam [MARCA];
  - "tiger stripe" (urbano, verde, dourado);
  - "dazzle stripe";
  - padrões "alpine";
  - acabamentos **battleworn** (bronze, tungsten, Multicam Black, zombie green).

  "Every camo and multi-color pattern is applied using a combination of vinyl stencils, freehand spraying, and layered coating techniques" — [Weapon Works](https://weaponworksllc.com/cerakote-patterns/)
- Outro aplicador organiza os padrões em duas famílias:
  - **Texture/Graphic:** Kryptek (licenciado), "Hex/Dragon Scale", "Damascus", "Reptile" e "Triangle".
  - **Técnica:** "Battleworn (worn/distressed look), Fades, Torn, and Patina".

  "Battleworn: Often applied to Bronze or Tungsten, creating a rustic look". "Torn Pattern: Often uses a top layer color 'torn' away to reveal a bottom layer or metallic base" — [Aegis Cerakote](https://www.aegiscerakote.com/services/custom-cerakote/patterns/)
- O guia oficial de splinter usa vinil de alta aderência, estênceis de splinter, pinças antiestáticas e lâminas plásticas (via resumo de busca) — [Cerakote – Splinter Camo](https://www.cerakote.com/resources/knowledge-base/233/application-guide-pattern-splinter-camo)

#### 1.4 Hidrografia (hydro dipping / water transfer printing)
- A peça passa antes por todo o processo de pintura: preparo, primer, **cor de base**, e depois **verniz**.
- Um filme de PVA impresso com a imagem desejada (tintas látex ou pigmentadas) flutua na água por 60–75 s antes da imersão.
- Serve para metal, plástico, fibra de vidro, madeira e cerâmica.

Fonte: [Wikipedia – Water transfer printing](https://en.wikipedia.org/wiki/Water_transfer_printing)

#### 1.5 Anodização de alumínio (Tipo II e Tipo III)
- A MIL-A-8625 define três tipos:
  - Tipo I: ácido crômico;
  - Tipo II: sulfúrico, espessura moderada até ~25 µm;
  - Tipo III: "hard-coat", acima de 25 µm. A anodização dura pode ir de 13 a 150 µm.

  Os poros do óxido absorvem o corante e depois precisam de selagem (tipicamente acetato de níquel). "Because the dye is only superficial … minor wear and scratches break through the dyed layer". Selar o Tipo III melhora a corrosão, mas reduz a resistência à abrasão — [Wikipedia – Anodizing](https://en.wikipedia.org/wiki/Anodizing)
- Na **anodização de cor integral** (sem corante), "Shades of color are restricted to a range which includes pale yellow, gold, deep bronze, brown, grey, and black" — [Wikipedia – Anodizing](https://en.wikipedia.org/wiki/Anodizing)
- Tipo III em peças de AR-15 (via resumo de busca; a atribuição exata entre as páginas não foi verificada):
  - ligas 6xxx ficam cinza-preto profundo; 7xxx e 2xxx ficam cinza-bronzeado;
  - upper (7075) e guarda-mão (6061) podem não combinar;
  - há variação entre lotes e lados, "light mottling", e o grão do alumínio pode aparecer através da camada.

  Fontes: [CAT Outdoors](https://catoutdoors.com/type-iii-hardcoat-anodize-ar-15/); [Applied Weapons Tech](https://appliedweaponstech.com/p/type-iii-hard-coat-info)

#### 1.6 Anodização de titânio: tensão → cor
- A cor vem de uma camada transparente de TiO₂ por **interferência de filme fino** (como bolha de sabão). A camada vai de ~15 nm (dourado pálido) a >160 nm. A cor **muda com o ângulo de visão**. Não existe vermelho dominante. Cresce "roughly 1.5–2 nm per volt", com variação de ±2–3 V conforme eletrólito, liga, temperatura e acabamento — [PartMFG](https://www.partmfg.com/titanium-anodizing-color-chart/)
- "Browns require the least voltage (about 10 to 15 volts) and greens the most (85 to 90 volts)". A cor percebida depende da espessura **e do acabamento da superfície** (via resumo de busca) — [Rio Grande](https://www.riogrande.com/knowledge-hub/articles/reactive-metals-anodizing-niobium-and-titanium-for-colorful-results/)
- Faixa alta da tabela (via resumo de busca): dourado/rosa ≈ 50–60 V; rosa ≈ 62,5 V; roxos ≈ 65–75 V; azul/teal ≈ 77,5–85 V; verde → verde-amarelado ≈ 87,5–100 V — [Monster Bolts](https://monsterbolts.com/pages/anodized-titanium-color-chart)
- **Conflito entre fontes:**
  - A PartMFG dá uma tabela contínua sem o "segundo dourado": dourado 13–18 V, bronze 19–25, rosa 26–30, roxo 31–40, roxo escuro 41–50, azul 51–60, azul-teal 61–70, teal 71–80, verde 81–90 — [PartMFG](https://www.partmfg.com/titanium-anodizing-color-chart/)
  - A Fastenere (via resumo de busca) dá dourado 15–18, azul 30–35, roxo 40–45, teal 60–65, verde 80–110 — [Fastenere](https://www.fastenere.com/blog/titanium-basics)

  Essas duas tabelas contradizem a sequência de interferência (ver Inferences).
- Cabos de titânio recebem anodização colorida com frequência em facas custom — [KnifeInformer](https://knifeinformer.com/the-ultimate-guide-to-knife-handle-materials/)

#### 1.7 PVD, TiN e DLC
- O TiN é marrom em volume e "appears gold when applied as a coating". É usado em joias, acabamento automotivo e "on the moving parts of many rifles and semi-automatic firearms". As variantes TiCN e TiAlN/AlTiN dão cores "from light gray to nearly black, to a dark, iridescent, bluish-purple" — [Wikipedia – Titanium nitride](https://en.wikipedia.org/wiki/Titanium_nitride)
- PVD sobre inox produz uma gama de cores e pode imitar latão e bronze (ex.: acabamentos Space Gray e Gold) — [Wikipedia – PVD](https://en.wikipedia.org/wiki/Physical_vapor_deposition)
- O DLC tem dureza extrema e baixo atrito; o ta-C é a forma mais dura e "slickest" — [Wikipedia – DLC](https://en.wikipedia.org/wiki/Diamond-like_carbon)
- Em lâminas, o DLC é um tipo de PVD aplicado em câmara de vácuo — [Artisan Cutlery](https://artisancutlery.net/blogs/ai/knife-finish-guide-stonewash-vs-satin-vs-bead-blast-vs-pvd-dlc-coating). Ele resiste a riscos, mas marcas no revestimento escuro uniforme continuam visíveis (via resumo de busca) — [Noblie](https://nobliecustomknives.com/knife-blade-finishes/); [South Summit](https://www.southsummit.com/blog/gear-guide/knife-blade-finishes-explained)

#### 1.8 Têmpera colorida (colour case hardening)
- Processo tradicional:
  - a peça é embalada em caixa selada com osso moído e carvão, ou com couro, cascos, sal e urina;
  - o aço escurece e "shows a mottled pattern of black, blue, and purple caused by the various compounds formed from impurities in the bone and charcoal".

  Fonte: [Wikipedia – Case-hardening](https://en.wikipedia.org/wiki/Case-hardening)
- Aquecimento em cadinho a ~730 °C por até 6 h, seguido de têmpera, gera padrões coloridos — [Wikipedia – Bluing](https://en.wikipedia.org/wiki/Bluing_(steel))
- Preferências estéticas citadas: "brilliant cobalt, others the fade of old blue jeans, gold or khaki". Defeitos citados: "closely mottled" e "flashing" (áreas cinza-foscas).

  Peças típicas: action bodies, lockplates, trigger plates, hammers e side plates. As cores desbotam com sol e uso, "occurring first along edges" — [Shooting Sportsman](https://shootingsportsman.com/color-case-hardening/)
- Descrições de restauradores e fóruns (via resumo de busca): manchas azul/verde/marrom em receivers de espingardas e rifles duplos, receivers Winchester e armações Colt SAA; às vezes "straw and grey, with some blue" — [Hallowell](https://www.hallowellco.com/casehardening.htm); [Turnbull](https://www.turnbullrestoration.com/restoration-services/color-case-hardening/)

#### 1.9 Oxidação (bluing), azul de nitrato/fogo e cores de revenimento
- Tipos e resultados:
  - **Hot caustic** a 135–154 °C dá preto e é o padrão atual.
  - **Rust bluing** dá "deep blue-black" e resiste mais à ferrugem.
  - **Fume bluing** usa vapores ácidos por ~12 h.
  - **Cold bluing** dá preto ou "very dark grey" e serve só para retoque.
  - **Nitre bluing** usa sal fundido a 310–321 °C, com a sequência "straw, gold, brown, purple, blue, teal, then black". É usado em pinos, parafusos e miras e dá "peacock blue, a rich iridescent blue".
  - **Browning** é ferrugem vermelha controlada.

  A camada tem "typically no thicker than 2.5 micrometres" e por isso sofre com o desgaste de coldre (holster wear) — [Wikipedia – Bluing (steel)](https://en.wikipedia.org/wiki/Bluing_(steel))
- No revenimento, o óxido engrossa com a temperatura e a cor vai de "very light yellow, to brown, to purple, and then to blue". Depois do cinza-azulado o óxido deixa de ser transparente. Inox dá uma gama maior ("golds, teals, and magentas"). Um aço mantido a 205 °C por muito tempo também chega a marrom, roxo ou azul — [Wikipedia – Tempering](https://en.wikipedia.org/wiki/Tempering_(metallurgy))

#### 1.10 Parkerização (fosfato de zinco / manganês)
- "The color, fresh from the Parkerizing Tank, is best described as a dark, charcoal gray; not olive drab as many believe". O tom verde-marrom das armas militares antigas vem de óleos e preservativos (Cosmoline, óleo de linhaça, suor, sujeira).

  A camada tem capilares e microcavidades que retêm óleo. Recomenda-se jateamento antes, porque superfície polida dá camada mais fina. Ligas e tratamentos térmicos diferentes dão tons diferentes de cinza "even on the same gun".

  O manganês tem "very heavy crystal structure that gives a coarser and more porous finish" e a melhor resistência ao desgaste como acabamento final. O zinco pesado é a melhor base para pinturas de forno.

  Acabamentos originais observados em M1 Garand: "charcoal black, gloss black, black with a noticeable green tint, dark olive green, a light, almost translucent gray, and translucent gray with a green cast" — [Brownells (PDF)](https://feeds.brownells.com/userdocs/learn/076-200-482_Manganese_and_Zinc_Parkerizing.pdf)
- Em fóruns, o zinco é descrito como "a little lighter… gray/charcoal" e o manganês como mais escuro, "dark charcoal tint" (via resumo de busca; nível fórum) — [1911Forum](https://www.1911forum.com/threads/diffrence-in-manganese-phosphate-and-parkerizing.134603/)
- A Glock aplica parkerização preta sobre Tenifer; "the slide is protected even if the Parkerized finish were to wear off" — [Wikipedia – Phosphate conversion coating](https://en.wikipedia.org/wiki/Phosphate_conversion_coating)

#### 1.11 Nitrocarbonetação ferrítica (Tenifer, Tufftride, Melonite, Arcor [MARCAS])
- Difunde N e C no aço em banho de sal. A pós-oxidação cria Fe₃O₄ preto, "aesthetically attractive black color".
- A Glock usou Tenifer até 2010 e depois passou ao processo gasoso. O acabamento é "matte, non-glare".

Fonte: [Wikipedia – Ferritic nitrocarburizing](https://en.wikipedia.org/wiki/Ferritic_nitrocarburizing)

#### 1.12 Níquel, cromo e NP3
- Níquel químico (electroless) pode ser "matte, semi-bright, or bright". Existe compósito Ni-P-PTFE desde 1981 — [Wikipedia – Electroless nickel](https://en.wikipedia.org/wiki/Electroless_nickel-phosphorus_plating)
- O cromo pode ser decorativo ou duro. O banho decorativo trabalha a 35–45 °C e o duro a 50–65 °C — [Wikipedia – Chrome plating](https://en.wikipedia.org/wiki/Chrome_plating)
- **NP3 [MARCA Robar]:** níquel químico com PTFE submicrométrico. "satin gray, non-reflective… so lubricious (slick) it appears wet, yet remains dry to the touch" (via resumo de busca) — [Robar](https://robarguns.com/custom-firearm-finishes/np3/)

#### 1.13 Gravação
- Gravura manual é usada em armas de fogo e facas. Em trabalho de alto nível chega a "up to 40 lines per mm … creating game scenes and scrollwork". O estilo **bulino** ("hand push") é "highly detailed and delicate, fine work" — [Wikipedia – Engraving](https://en.wikipedia.org/wiki/Engraving)

### Inferences

**Cores Cerakote**
- Use a coluna "Sugestão" como ponto de partida e ajuste no próprio renderer.
- As cores "metálicas" (Burnt Bronze, Tungsten, Titanium, Blue Titanium, Gold, Satin Aluminum) precisam de flocos. Uma forma é metalness ~0,4–0,7 com ruído de normal de alta frequência. A cor sozinha não dá a aparência.
- No jogo, dê nomes genéricos. Exemplos: "Grafite fosco", "Cinza atirador", "Bronze tostado", "Terra escura", "Verde oliva", "Areia do deserto", "Titânio acetinado".

**Titânio anodizado: sequência física**
Calculado por nós:
- Modelo de reflexão de filme fino (ar / TiO₂ com n ≈ 2,3 / titânio com n ≈ 2,0–3,1 e k ≈ 2,7–3,9).
- Funções CIE 1931 pelo ajuste analítico de Wyman, Sloan e Shirley (2013), iluminante ~D65 (corpo negro de 6504 K).
- Saída em sRGB.

O modelo reproduz a ordem da tabela "clássica" (Rio Grande + Monster Bolts) e mostra que a tabela da PartMFG, sem o dourado de 2ª ordem, é fisicamente inconsistente.

| Espessura do filme | Cor calculada (aprox.) | Nome usual |
|---|---|---|
| 0 nm | #CCC4C2 | titânio nu |
| 20–25 nm | #B19C78 → #A58852 | palha / bronze claro |
| 30–35 nm | #966E31 → #81503E | bronze / marrom-arroxeado |
| 40–45 nm | #683965 → #4C3F87 | roxo → índigo |
| 50–55 nm | #375AA1 → #3E77B3 | azul profundo |
| 60–70 nm | #588EBF → #8AAFCC | azul-claro |
| 80–100 nm | #ACC1CF → #CBCDB9 | azul-prateado / "branco" |
| 110–130 nm | #D1CC97 → #D5C45F → #D9AF40 | dourado pálido → dourado |
| 140 nm | #DA8A77 | rosa / salmão |
| 150 nm | #CB5AA8 | magenta |
| 160 nm | #A447C4 | roxo |
| 170 nm | #5E6DD0 | azul-violeta |
| 180–195 nm | #0098D0 → #00B5C5 → #43BFBC | azul / teal |
| 200–210 nm | #67C6AE → #96CE8A | verde |
| 220–230 nm | #B7CF67 → #CEC666 | verde-amarelado → amarelo |

- Para o dourado cair em ~50 V, o rosa em ~60 V, o roxo em ~65–70 V, o teal em ~80 V e o verde em ~85–90 V (tabela clássica), o crescimento efetivo precisa ser de ~2,2–2,4 nm/V. Isso é um pouco acima do "1.5–2 nm/V" citado pela PartMFG. Os hex acima são estimativas: cores reais variam com liga, eletrólito, acabamento (fosco reduz a saturação) e ângulo.

**Aço: cores de revenimento e azul de nitrato**
Calculado por nós, com filme de óxido de ferro fracamente absorvente (n ≈ 2,5 + 0,35i) sobre ferro:

| Espessura | Cor |
|---|---|
| 0 nm | #C7C1C5 |
| 20 nm (palha) | #A18C69 |
| 30 nm (marrom/bronze) | #7A551D |
| 40 nm (roxo) | #43204F |
| 45–50 nm (azul profundo, "azul de nitrato/pavão") | #262D6B → #1B467F |
| 55–65 nm (azul) | #2D5C8F → #5A7EA0 |
| 70–80 nm (cinza-azulado) | #6C89A4 → #8698A3 |

A ordem bate com a Wikipedia (amarelo-claro → marrom → roxo → azul → cinza-azulado). Os valores são aproximados.

**Oxidação a quente (hot bluing)**
É um óxido preto espesso (até 2,5 µm), então fica fora do regime de interferência visível. Ponto de partida estimado (sem fonte): base preta-azulada ~#1E2229–#2B3038, metalness ~0,6–0,9, rugosidade:
- 0,15–0,3 em peça polida ("high polish blue");
- 0,45–0,6 em peça jateada.

**Têmpera colorida**
Pode ser modelada como filme fino de espessura variável:
- mapa de espessura por ruído com "domain warping", com manchas grandes e pequenas;
- espessura 20–70 nm (palha → marrom → roxo → azul);
- manchas cinza-escuras ("flashing");
- base de aço acinzentado;
- desbotamento nas arestas a partir da máscara de desgaste, conforme a Shooting Sportsman.

**Parkerização**
- Cinza-carvão médio a escuro. Estimativa sem fonte: #3A3B3A–#4A4B48 no zinco e #2E302E–#3A3A37 no manganês.
- Superfície cristalina e rugosa (rugosidade 0,75–0,95, quase dielétrica).
- Variante "arsenal envelhecido": tinte esverdeado/marrom de óleo com pouca opacidade, mais forte nos recessos.

**Nitreto/Tenifer**
Preto fosco não-refletivo (rugosidade 0,6–0,8). Com o desgaste, o óxido preto sai e aparece um cinza-aço opaco, não metal brilhante, porque a camada nitretada fica.

**Anodizado de alumínio (Tipo III preto)**
- Tratar como dielétrico escuro (metalness 0), rugosidade 0,5–0,7.
- Leve variação de tom ("mottling") e leve tinte bronze/cinza em peças de liga diferente (upper × lower). É um bom detalhe de realismo por zona de material.
- Desgaste: alumínio claro e brilhante nas arestas.

**Hidrografia**
Três camadas: cor de base, gráfico do filme (qualquer imagem) e verniz. No three.js: `clearcoat` 0,6–1,0 com `clearcoatRoughness` 0,05–0,2 sobre a arte. O desgaste corta o verniz e a arte até a base ou o metal.

### Gaps
- Não achei hex publicados oficialmente pela Cerakote. Os valores são medições de fotos com renderizações diferentes (A vs B divergem até ~20 L*).
- Não medi **Robin's Egg Blue** (H-175), **Cobalt** nem os "Tiffany-like". Nenhuma das duas fontes trazia a amostra.
- O status de marca de "Tiffany Blue" e "Stormtrooper" é provável, mas não foi verificado.
- Não verifiquei o nome atual exato de H-190 (Armor Black × "Military Black") nem de H-265 (FDE × "Troy Coyote Tan"). Os rótulos seguem as fontes.
- Não houve fonte primária acessível para a série C "até 1700 °F". Monster Bolts e Rio Grande foram lidos só por resumo de busca (403 ou falha).
- Não encontrei fonte com paleta hex para têmpera colorida, oxidação a quente, parkerização ou nitreto. Os valores dados são estimativas nossas.
- Não pesquisei a fundo filmes típicos de hidrografia (fibra de carbono, madeira, caveiras, chamas), embutimento de ouro (gold inlay) nem NP3 em cores.
- A Commons/Wikipedia bloqueou (rate limit) a busca de imagens de receiver com têmpera colorida para extrair paleta.

---

## 2. Acabamentos específicos de facas (damasco, lâmina e cabo)

### Takeaway
O damasco moderno é um "padrão por construção". O aço carbono (ex.: 1084) escurece no ataque ácido e o aço com níquel (ex.: 15N20) fica claro. O padrão vem de como o tarugo é cortado, torcido, furado ou espelhado, o que o torna ideal para shaders baseados em faixas deformadas.

Os acabamentos de lâmina variam principalmente em rugosidade e direcionalidade:
- satin é anisotrópico ao longo da lâmina;
- mirror é quase espelhado;
- stonewash tem riscos aleatórios e esconde desgaste;
- bead blast é fosco e isotrópico;
- acid/black wash é escuro e manchado;
- DLC/PVD é escuro e duro.

Os cabos são laminados fibrosos: G10 em camadas coloridas, Micarta de tecido fenólico, fibra de carbono com trama e FRN moldado.

### Cited Findings

#### 2.1 Padrões de damasco
Red Label Abrasives:
- **Ladder:** sulcos esmerilhados antes de forjar plano, com "repeating horizontal lines … like the rungs of a ladder".
- **Twist:** tarugo torcido, "swirling, corkscrew-like grain".
- **Raindrop:** covinhas furadas ou prensadas, com "circular shapes … scattered".
- **Feather:** tarugo dividido e espelhado em torno de um eixo central, com "strong central line … branching lines fanning out".
- **Mosaic:** peças pré-arranjadas, com "stars, skulls, logos, flowers, or repeating geometric motifs".
- **Random:** "organic, non-uniform flow of lines".
- **W/Turkish twist:** "sharp, zigzagging lines".
- **Herringbone:** "V-shaped lines … alternating directions".
- **Tile/Explosion:** tarugo cortado em ladrilhos e reorganizado.
- **Snakeskin:** matrizes prensam uma textura de escamas.

No ataque, "The bright and silvery nickel-rich steel resists acid etching, while the high-carbon version etches darker", com cloreto férrico. A profundidade, a concentração e o tempo alteram o visual — [Red Label Abrasives](https://www.redlabelabrasives.com/blogs/news/types-of-damascus-patterns)

Ataque e contraste (via resumo de busca):
- o cloreto férrico corrói as camadas de 1084 mais rápido que as de 15N20, que ficam brilhantes enquanto o 1084 "recedes dark";
- um banho de café solúvel forte depois do ataque escurece ainda mais as camadas de carbono, com tom mais quente;
- um tempo citado para o cloreto férrico é de 4–5 min.

Fontes: [Damascus Steel Buy – 1084/15N20](https://damascussteelbuy.com/1084-15n20-damascus-combination-modern-standard/); [Torus CNC](https://toruscnc.com/forge-brain/damascus/etching-damascus/); [Noblie – coffee etching](https://nobliecustomknives.com/coffee-etching-damascus-steel/)

História do padrão:
- No pattern welding as faixas são realçadas "by proper polishing or acid etching", e os vikings torciam barras entre si — [Wikipedia – Pattern welding](https://en.wikipedia.org/wiki/Pattern_welding)
- O damasco histórico (wootz) tem "banding and mottling reminiscent of flowing water, sometimes in a 'ladder' or 'rose' pattern" ("watered steel") — [Wikipedia – Damascus steel](https://en.wikipedia.org/wiki/Damascus_steel)

#### 2.2 Acabamentos de lâmina
- Artisan Cutlery:
  - **Stonewash:** "tumbling blades with ceramic or stone media in a rotating drum", superfície levemente encruada com aspecto gasto.
  - **Bead blast:** "uniform, matte, pebbled surface texture".
  - **Satin:** lixas progressivamente mais finas, "producing parallel lines along the length of the blade".
  - **PVD/DLC:** câmara de vácuo.

  Fonte: [Artisan Cutlery](https://artisancutlery.net/blogs/ai/knife-finish-guide-stonewash-vs-satin-vs-bead-blast-vs-pvd-dlc-coating)
- Via resumo de busca:
  - "acabamento" é textura do próprio aço (satin, mirror, stonewash, bead blast, acid wash) e "revestimento" é camada adicionada (DLC, PVD, Cerakote, TiN, TiCN, cromo duro, powder coat);
  - stonewash e blackwash são os que melhor escondem riscos;
  - "acid stonewashed/black stonewash" é ácido para escurecer, seguido de stonewash;
  - "BlackWash" é termo genérico;
  - o satin mostra riscos com mais facilidade e o mirror "reveals every scratch".

  Fontes: [Noblie](https://nobliecustomknives.com/knife-blade-finishes/); [South Summit](https://www.southsummit.com/blog/gear-guide/knife-blade-finishes-explained); [Urban EDC](https://urbanedc.com/blogs/analog-field-guide/blade-finishes-explained)
- Ácidos usados: cloreto férrico, ácido muriático e até vinagre. "Vinegar creates a surface color change without significant depth. Ferric chloride etches patterns and provides more dramatic darkening". Lâminas mirror e stonewash podem ter corte idêntico — [Urban EDC](https://urbanedc.com/blogs/analog-field-guide/blade-finishes-explained)

#### 2.3 Materiais de cabo
- **G-10:** laminado de fibra de vidro, "the toughest of all the fiberglass resin laminates", mais forte porém mais frágil que Micarta. "The production process can utilize many layers of the same color, or varying different colors to achieve a unique cosmetic look".
- **Micarta [MARCA]:** linho em resina fenólica, "somewhat dressier than G-10", "has absolutely no surface texture … requires … hand labor … to carve some sort of texture".
- **Fibra de carbono:** "the way in which the carbon 'weave' reflects light".
- **Zytel [MARCA DuPont]:** FRN (nylon reforçado com fibra de vidro), com fibras "arranged haphazardly".
- Titânio e alumínio riscam com mais facilidade que o inox.

Fonte: [KnifeInformer](https://knifeinformer.com/the-ultimate-guide-to-knife-handle-materials/)
- Laminados tipo Micarta podem usar linho, lona (canvas), papel, fibra de vidro ou fibra de carbono em resinas fenólica, epóxi, silicone ou melamina. O Micarta surgiu na Westinghouse (~1910) — [Wikipedia – Micarta](https://en.wikipedia.org/wiki/Micarta)
- Tecido de carbono comum: sarja (twill) 2/2 — [Wikipedia – CFRP](https://en.wikipedia.org/wiki/Carbon_fiber_reinforced_polymer)
- "Timascus™" (titânio em camadas) aparece como material de cabo com marca — [Alpha Knife Supply](https://www.alphaknifesupply.com/shop/handle-materials)

### Inferences

**Damasco procedural**
Base: faixas `b = 0.5+0.5*sin(2π·f·(u + warp(u,v)))`, onde `u` é a coordenada ao longo da espessura do tarugo, projetada na lâmina. A partir dela:
- **Random:** domain warp FBM de amplitude média.
- **Ladder:** somar uma onda periódica perpendicular ao comprimento da lâmina (`+A·sawtooth(v·k)`).
- **Raindrop:** somar à fase anéis radiais em torno de pontos Worley (`+A·smoothstep(r0,0,d_F1)`).
- **Twist:** fase dependente de `atan` em uma coordenada rotacionada, gerando elipses concêntricas alongadas.
- **Feather:** espelhar `|v - centro|` e somar deslocamento em "V".
- **W / herringbone:** fase dente-de-serra alternada.

A camada clara (15N20) é metal quase polido: metalness 1, base ≈ níquel/inox (#D9D1C6 / #D6D1CB), rugosidade 0,2–0,35.

A camada escura (1084 atacado, com ou sem café) tem base escurecida (~#2A2826–#3A3632, estimativa), metalness 0,6–0,9 e rugosidade 0,45–0,65. Ela fica levemente **rebaixada**: dar à normal um relevo de ~0,02–0,05 mm, porque o ácido remove mais o aço carbono.

**Lâminas no three.js**
- **Satin:** `anisotropy` 0,6–0,9, direção ao longo do comprimento, rugosidade 0,25–0,4.
- **Mirror:** rugosidade 0,02–0,08 e anisotropia 0.
- **Stonewash:** rugosidade 0,35–0,55 com mapa de normal de micro-riscos multidirecionais (ruído de linhas curtas em ângulos aleatórios).
- **Bead blast:** rugosidade 0,55–0,75 e ruído isotrópico fino.
- **Acid/blackwash:** base metálica multiplicada por 0,3–0,5 com manchas FBM e rugosidade 0,45–0,65.
- **Pátina forçada:** manchas azul-acinzentadas e marrons (filme fino de baixa intensidade com espessura por ruído).
- **DLC:** preto-grafite (~#1C1C1E, estimativa), metalness 0,2–0,5, rugosidade 0,25–0,45. Os riscos aparecem como linhas finas mais claras.

**Cabos**
- **G10:** dielétrico com textura em relevo (pirâmides ou escamas), rugosidade 0,5–0,8. Nas arestas chanfradas, a máscara de aresta pode revelar as faixas coloridas das camadas, como em G10 multicolor.
- **Micarta:** tecido fino (linho) ou grosso (canvas) no mapa de normal, rugosidade 0,6–0,9.
- **Fibra de carbono:** sarja 2/2 com direção de anisotropia alternando entre tows, `clearcoat` 1 e `clearcoatRoughness` 0,03–0,1.
- **FRN:** textura moldada, rugosidade 0,6–0,85.
- **Titânio anodizado:** mesma receita de `iridescence` da seção 1.

**"Tiger stripe" de faca**
Pode ser tratado como máscara de listras sobre dois acabamentos, por exemplo stonewash + blackwash, ou DLC + inox. É inferência; ver Gaps.

### Gaps
- Não achei fonte técnica sobre o acabamento "tiger stripe" em lâminas (mascaramento + ácido/DLC).
- Não achei valores medidos de rugosidade dos acabamentos. Todos os valores numéricos são estimativas de partida.
- Não encontrei paletas hex de G10, Micarta ou FRN comerciais, nem das cores de PVD "rainbow" e bronze em lâminas.
- Não confirmei a contagem de camadas típica por padrão de damasco. A cifra de "300+ camadas" vista em resumo não teve fonte clara.

---

## 3. Camuflagens militares/civis: paletas, escala e status de propriedade

### Takeaway
Os padrões se agrupam em famílias de forma, cada uma com receita procedural própria:
- manchas orgânicas: Woodland/ERDL, DPM, Vegetato;
- pontos: Flecktarn;
- polígonos duros: Splittertarn, M90;
- listras: tiger stripe horizontal; lagarto e rajada verticais; pinceladas rodesianas;
- digitais/pixelados: MARPAT, CADPAT, UCP, EMR, Type 07;
- multiterreno em gradiente: MultiCam [MARCA].

Status de propriedade:
- **Restritos ou proprietários:** MARPAT (patenteado pelo governo dos EUA e restrito pelo USMC), CADPAT (marca registrada), MultiCam (Crye Precision), OCP/Scorpion W2 (direitos de licença do Exército dos EUA), A-TACS® (processo patenteado), Kryptek™, M90 (protegido desde 2020), variantes comerciais "Tiger Stripe™".
- **Brasil:** o uso por civis de uniformes que possam ser confundidos com os das Forças Armadas é vedado por lei.

Só uma fonte publica hex "oficiais": MultiCam, na Wikipedia. Para o resto, medimos paletas aproximadas por k-means em fotos de tecido do Camopedia.

### Cited Findings

#### 3.1 EUA
- **Woodland M81:** quatro cores (verde-claro, verde-escuro, marrom, preto) em grandes manchas orgânicas (via resumo de busca) — [Soldier Systems](https://soldiersystems.net/2025/02/15/a-brief-history-of-m81-woodland-camouflage/)

  É parecido com o ERDL de dominante marrom, "enlarged by 60 percent and the shades adjusted for contrast", e foi impresso um pouco mais escuro que o ERDL — [Wikipedia – U.S. Woodland](https://en.wikipedia.org/wiki/U.S._Woodland)
- **ERDL:** quatro cores entrelaçadas. A versão de dominante verde tem formas orgânicas verde-oliva e marrom, "black 'branches'" e "light green 'leaf highlights'". Na versão de dominante marrom, o verde-claro vira bege-claro — [Wikipedia – ERDL](https://en.wikipedia.org/wiki/ERDL_pattern)
- **DBDU "chocolate chip" (6 cores):** "base pattern of light tan overlaid with broad swathes of pale green and wide two-tone bands of brown. Clusters of black and white spots … to mimic … pebbles and their shadows" — [Wikipedia – DBDU](https://en.wikipedia.org/wiki/Desert_Battle_Dress_Uniform)
- **DCU (3 cores, "coffee stain"):** marrom-escuro, verde-oliva pálido (que fica "mint-colored" nos DCU de 1989/90) e bege. As paletas foram inicialmente reaproveitadas do 6 cores — [Wikipedia – DCU](https://en.wikipedia.org/wiki/Desert_Camouflage_Uniform)
- **MARPAT:** "multi-scale", "formed of small rectangular pixels of color". "The United States government has patented MARPAT, including specifics of its manufacture". O USMC restringe seu uso. A patente do padrão foi depositada em 19/06/2001. Os equipamentos usam Coyote Brown — [Wikipedia – MARPAT](https://en.wikipedia.org/wiki/MARPAT)
- **UCP:** "tan, gray, and sage green (officially named Desert Sand 500, Urban Gray 501, and Foliage Green 502)". Não tem preto. É essencialmente uma recoloração das formas do MARPAT — [Wikipedia – UCP](https://en.wikipedia.org/wiki/Universal_Camouflage_Pattern)
- **MultiCam [MARCA Crye Precision]:**
  - sete cores, desenvolvido com o U.S. Army Soldier Systems Center;
  - fundo em gradiente marrom → bege-claro, sobreimpresso com gradiente verde-escuro, oliva e lima, e camada superior de formas opacas marrom-escuro e creme;
  - hex publicados: **Cream 524 #B8A78B; Dark Brown 530 #48352F; Tan 525 #967860; Brown 529 #6F573F; Dark Green 528 #5A613F; Olive 527 #8C7D50; Pale Green 526 #85755C**;
  - variantes Arid, Tropic, Alpine e Black desde 2013; "Variants of it, some unlicensed".

  Fonte: [Wikipedia – MultiCam](https://en.wikipedia.org/wiki/MultiCam)
- **OCP (Scorpion W2):** "The Army owns the licensing rights for Scorpion W2 … allows the Army the option to restrict the pattern to service members only". Camiseta e cinto na cor Tan 499 — [Wikipedia – OCP](https://en.wikipedia.org/wiki/Operational_Camouflage_Pattern)
- **A-TACS® [MARCA, Digital Concealment Systems, 2007]:** substitui pixels quadrados por "organically-shaped pixels, utilizing a patented process" — [Camopedia – A-TACS](https://www.camopedia.org/index.php/A-TACS)

  O AU agrupa pixels orgânicos em macroformas; o FG (verde) é de 2011 (via resumo de busca) — [A-TACS](https://www.a-tacs.com/our-patterns); [UF PRO](https://ufpro.com/us/blog/different-types-tacs-camo)

  Um licenciado russo alega exclusividade de copyright do A-TACS FG (apenas o título foi lido) — [5.45 Design](http://www.en.545design.ru/news/exclusive-rights-for-a-tacs-fg-camo-pattern)
- **Kryptek™ [MARCA]:** "bi-level layering design that incorporates background transitional shading and sharp random geometrical foregrounds". A geometria padrão tem nove colorways — [Camopedia – Kryptek](https://www.camopedia.org/index.php/Kryptek)

  Padrões: Highlander (transição), Mandrake (floresta), Typhon (noturno/urbano) e Nomad (deserto), submetidos ao Camouflage Improvement Effort de 2012 (via resumo de busca) — [Kryptek](https://kryptek.com/pages/kryptek-camo-patterns)
- **Tiger stripe:**
  - o primeiro foi uma cópia local do "lizard" francês para os Fuzileiros vietnamitas (1957);
  - há dezenas de variantes (JWS, JWD ~1964, Tadpole Sparse "silver", Tadpole Dense ~1970, ADD "purple", ADS "gold tiger", entre outras);
  - existem versões comerciais com marca: "The original Vietnam Tiger Stripe Pattern™ design is copied from the 'John Wayne Dense'…" e "Desert Tiger™" (1991).

  Fonte: [Camopedia – Tiger stripe](https://camopedia.org/index.php?title=Tiger_stripe)

#### 3.2 Europa, Rússia, China, Canadá, África e Brasil
- **Flecktarn:**
  - nasceu do Truppenversuch 76 (variante "Flecktarnmuster B") e foi confirmado em 1989;
  - nome oficial: "Fünf Farben Tarndruck der Bundeswehr" (camuflagem de **cinco cores**);
  - foi copiado por Dinamarca, Japão, Polônia, China e Bélgica;
  - a versão de deserto começou com "sparse dark olive & reddish-brown spots on a sandy background";
  - o "Multitarndruck" (a partir de ~2015) usa verde-claro, verde-escuro, marrom, bege, cinza e off-white.

  Fonte: [Camopedia – Germany](https://camopedia.org/index.php?title=Germany)
- **Splittertarn:** quatro cores, 1931, "disruptive pattern of hard-edged polygons", polígonos marrom-madeira e verde-médio sobre cinza-campo ou bege claro, com tracejados verdes aleatórios ("raindrops") — [Wikipedia – Splittertarnmuster](https://en.wikipedia.org/wiki/Splittertarnmuster)
- **DPM (Reino Unido):**
  - woodland de quatro cores: preto, marrom-escuro, verde-médio e areia-escuro;
  - existem versões urbanas, azuis e roxas;
  - as cores mudaram ao longo das décadas (o marrom de 1985 é bem mais escuro; o de 1994 é alaranjado);
  - o tecido do Soldier 95 é tecido já na cor areia e sobreimpresso com só três cores, o que "leads to a loss in contrast … after washing".

  Fonte: [Wikipedia – DPM](https://en.wikipedia.org/wiki/Disruptive_Pattern_Material)
- **M90 (Suécia):**
  - derivado de um padrão de veículos da FOA, reduzido na proporção 1:66;
  - campos de cor "unusually large and 'clean'";
  - só teve proteção de direitos em 2020: em outubro de 2020 o escritório sueco de patentes registrou uma versão protegida em três iterações (floresta, deserto, inverno);
  - antes disso ele se espalhou em produtos comerciais.

  Fonte: [Wikipedia – M90](https://en.wikipedia.org/wiki/M90_(camouflage))

  Cores descritas: "Blue, khaki, and light green patches … on a dark green background" — [Wikipedia – Splittertarnmuster](https://en.wikipedia.org/wiki/Splittertarnmuster). Eficaz a distâncias de até ~1 km — [Camopedia – Sweden](https://camopedia.org/index.php?title=Sweden)
- **Vegetato (Itália):** adotado pelo Exército em 2004, "mottled pattern of chocolate brown, russet & olive gre[en]…" (trecho truncado). A versão deserto (2004) é "chocolate brown, ochre & light tan shapes on a sandy-beige base". O Exército anunciou um novo padrão em dezembro de 2025 — [Camopedia – Italy](https://camopedia.org/index.php?title=Italy)
- **Rússia:**
  - **Berezka:** o KLMK soviético "solnechnye zaychiki (sunshine rays)" hoje é chamado "berezka (birch)" ou "silver leaf"; versões mais douradas são "golden yellow leaf".
  - **Flora (~1998, "Arbuz"/melancia):** derivado do VSR-93 "dubok", com desenhos ampliados e alinhados na horizontal.
  - **EMR ("Tsifra", "digital flora", 2008):** a variante de verão tem "tiny pixels of black, reddish-brown and foliage green on a pale green background".
  - A partir de 2023 os kits VKBO passaram a usar cópias locais de MultiCam.

  Fonte: [Camopedia – Russia](https://camopedia.org/index.php?title=Russia)

  A Flora tem versão verde e versão "Mountain Flora" (amarelo-escuro, areia ou cáqui), e as cores variam muito por fabricante — [Wikipedia – Flora](https://en.wikipedia.org/wiki/Flora_camouflage)
- **China Type 07 (junho de 2007):** seis paletas (Universal, Deserto, Floresta, Oceânico, Operações Especiais, Urbano). A Universal é "mid-brown, grey-green and small elements of very dark green on a neutral grey background". Em 2021 foi anunciada a família Type 21 "Xingkong"/"Starry Sky" — [Camopedia – China](https://camopedia.org/index.php?title=China)
- **CADPAT (Canadá):**
  - adotado em 1997, com testes concluídos em 2001 "once the pattern was trademarked";
  - TW: verde-claro, verde-escuro, marrom e preto; AR: três tons de marrom.

  Fonte: [Wikipedia – CADPAT](https://en.wikipedia.org/wiki/CADPAT)

  O CADPAT-MT (fevereiro de 2024) tem cinco cores: verde-oliva escuro, cáqui, areia, marrom-claro e traços de preto — [Camopedia – Canada](https://camopedia.org/index.php?title=Canada)
- **Rhodesian Brushstroke:** três cores, "green and brown strokes on a sandy background", com variantes de estação seca (base cáqui claro) e de chuva (base verde) — [Wikipedia – Rhodesian Brushstroke](https://en.wikipedia.org/wiki/Rhodesian_Brushstroke)

  O primeiro padrão foi de 1965–69 e o padrão tardio de 1970 ao fim da guerra: "brown & dark green brush strokes on a khaki…" — [Camopedia – Rhodesia](https://camopedia.org/index.php?title=Rhodesia)
- **Lagarto francês (TAP 47):** padrões listrados ou de pincelada a partir de ~1951, associados à Guerra da Argélia. O "A1" aparece no TAP Mle 47; o "A2" tem marrom-avermelhado e verde-oliva ou musgo sobre verde-pálido — [Camopedia – France](https://camopedia.org/index.php?title=France)
- **Brasil:**
  - O primeiro padrão do EB (1967) tinha manchas marrons e verde-lima sobre verde-pálido.
  - O lagarto do EB foi criado em 1977 na COSAC (Cap. Luiz Guilherme Terra Amaral e Cap. Jeannot Jansen da Silva Filho). Uma versão inicial com preto foi descartada "because it was easy to detect in a jungle environment".
  - O padrão atual do Exército, chamado **"rajada"**, "is characterized by dark green and purplish-brown vertical stripes on light or pale green background", em uso "from 1986 into the present", com várias versões de tecido.
  - **Marinha:** verde-escuro e verde-oliva sobre verde-claro. **FAB:** verde-escuro, castanho-avermelhado e azul sobre cáqui.
  - Há variantes históricas de Caatinga e de Montanha.
  - Os Fuzileiros Navais adotaram em 2019 um padrão para combate urbano (BMMCU) sem substituir o lagarto.

  Fonte: [Camopedia – Brazil](https://camopedia.org/index.php?title=Brazil)
- **Base legal brasileira:**
  - Lei 6.880/1980 (Estatuto dos Militares), Art. 76: "Os uniformes das Forças Armadas, com seus distintivos, insígnias e emblemas, são privativos dos militares".
  - Art. 79: "É vedado às Forças Auxiliares e a qualquer elemento civil ou organizações civis usar uniformes ou ostentar distintivos, insígnias ou emblemas que possam ser confundidos com os adotados nas Forças Armadas".

    Fonte: [Planalto – Lei 6.880](https://www.planalto.gov.br/ccivil_03/leis/l6880.htm)
  - Código Penal Militar, Art. 172: "Usar, indevidamente, uniforme, distintivo ou insígnia militar a que não tenha direito: Pena – detenção, até seis meses" — [Planalto – CPM](https://www.planalto.gov.br/ccivil_03/decreto-lei/del1001.htm)
  - Um blog de airsoft interpreta que os três padrões (Marinha, Exército, FAB) não podem ser usados por civis (opinião, via resumo de busca) — [VentureShop](https://blog.ventureshop.com.br/fardamento-militar-e-permitido-airsoft/)
- **Uniforme novo do EB (COBRA 2020):** adoção facultativa a partir de 2022, tecido poliéster/algodão ou poliamida/algodão com estampa de alta solidez e propriedades anti-infravermelho (via resumo de busca). Não encontrei afirmação de que o **desenho** do padrão mudou — [Defesa Aérea & Naval](https://www.defesaaereanaval.com.br/exercito/exercito-brasileiro-vai-comecar-a-adotar-novo-uniforme-de-forma-facultativa-a-partir-de-2022)

  No projeto COBRA, os coturnos avaliados vinham em marrom (paraquedistas), verde (Amazônia/Pantanal) e "Coyote" bege (tropas convencionais) — [Tecnodefesa](https://tecnodefesa.com.br/projeto-cobra-a-evolucao-dos-uniformes-e-equipamentos-do-exercito/)

#### 3.3 Paletas medidas por nós (k-means em CIELAB sobre fotos de tecido do Camopedia)
Método:
- imagem de 400 px reduzida à metade;
- faixa central com a marca d'água "camopedia.org" excluída;
- k = número de cores documentado;
- % = fração de área de cada cluster.

Limitações: são fotos de tecido real com desbotamento, sombra e balanço de branco variáveis, e clusters vizinhos podem se fundir. Use como ponto de partida e reequilibre pela descrição documentada.

| Padrão (referência) | Imagem / fonte | Paleta medida (hex, % da área) | Confiança / nota |
|---|---|---|---|
| EB "rajada" (lagarto BR) | Brazil39 – [Camopedia BR](https://camopedia.org/index.php?title=Brazil) | #7B6956 (50,6) · #829177 (21,6) · #837D68 (14,4) · #B1B29D (13,5) | média: tecido lavado; o marrom-arroxeado sai dessaturado |
| EB "rajada", amostra 2 | Brazil18 – idem | #756F5F (33,5) · #8A8677 (30,7) · #8D7067 (21,7, marrom-arroxeado) · #C7BEAD (14,1) | média |
| Marinha do Brasil (lagarto) | Brazil8 – idem | #646042 (58,4) · #3E5C43 (26,3) · #8A8E75 (15,2) | média |
| FAB (lagarto) | Brazil35 – idem | #8E8967 (50,3) · #4C5C82 (22,5, azul) · #ACAF94 (17,5) · #727880 (9,6) | boa |
| Flecktarn | Germany10 – [Camopedia DE](https://camopedia.org/index.php?title=Germany) | #88897E (33,5) · #B08776 (25,8) · #A1A290 (25,6) · #C7C68E (12,2) · #6E6972 (3,0) | baixa: foto clara e desbotada, preto sub-representado |
| Flecktarn deserto (3 cores) | Germany12 – idem | #C5AB99 (52,4) · #7F4D3A (36,1) · #403F31 (11,6) | boa |
| EMR verão (RU) | Russia38 – [Camopedia RU](https://camopedia.org/index.php?title=Russia) | #464D39 (35,7) · #707847 (21,8) · #585838 (21,6) · #63693E (20,8) | média: pixels pequenos se misturam |
| Flora (RU) | Russia10 – idem | #A9B077 (46,8) · #6B7A6B (32,1) · #917C6A (21,1) | média |
| Berezka (RU) | Russia34 – idem | #5B5239 (41,7) · #7A7055 (35,0) · #A5A359 (23,3) | média |
| Type 07 Universal (CN) | China3 – [Camopedia CN](https://camopedia.org/index.php?title=China) | #A0A1A0 (31,5) · #374F43 (30,7) · #424034 (30,4) · #6F736E (7,4) | média |
| Type 07 Floresta (CN) | China4 – idem | #466C62 (41,8) · #514A47 (24,6) · #A3A392 (18,5) · #37544B (15,1) | média |
| Vegetato (IT) | Italy12 – [Camopedia IT](https://camopedia.org/index.php?title=Italy) | #CE8762 (37,0) · #F2CE8E (21,7) · #C1A473 (21,6) · #A66752 (19,7) | baixa: foto com dominante quente, oliva não separado |
| Vegetato deserto (IT) | Italy13 – idem | #EEC79C (37,2) · #F0E4D8 (30,4) · #EBD3BD (19,9) · #C08E80 (12,5) | baixa: superexposta |
| M90 (SE) | Sweden4 – [Camopedia SE](https://camopedia.org/index.php?title=Sweden) | #8D947B (57,7) · #7B6D81 (21,6, "azul"/lilás) · #ECE1C7 (10,4) · #AAB665 (10,2) | média |
| DPM Soldier 95 (UK) | Uk24 – [Camopedia UK](https://camopedia.org/index.php?title=United_Kingdom) | #805756 (37,8) · #8C9863 (32,1) · #E0C69F (16,0) · #555355 (14,2) | boa |
| DPM P68 (UK) | Uk17 – idem | #A36C65 (34,1) · #8CB980 (31,7) · #6C6769 (20,3) · #E1D8AC (14,0) | boa (cores vivas) |
| Rhodesian Brushstroke tardio | Rhodesia1 – [Camopedia Rhodesia](https://camopedia.org/index.php?title=Rhodesia) | #606E53 (41,3) · #844F46 (37,4) · #C8B895 (21,2) | boa |
| idem, amostra 2 | Rhodesia4 – idem | #5E704D (49,1) · #CEBA98 (30,0) · #84564F (20,9) | boa |
| Lagarto francês A1 | France4 – [Camopedia FR](https://camopedia.org/index.php?title=France) | #A5896D (42,2) · #BBB593 (29,3) · #8F9269 (28,5) | média |
| CADPAT TW (CA) | Canada10 – [Camopedia CA](https://camopedia.org/index.php?title=Canada) | #8B925B (43,1) · #5B5662 (28,1) · #B6C687 (14,5) · #817F6B (14,2) | média |
| Woodland M81 (US) | Usa7 – [Camopedia USA](https://camopedia.org/index.php?title=USA) | #7D8D7A (35,2) · #776258 (28,0) · #B4AD99 (20,3) · #3D3948 (16,5) | boa |
| Woodland M81, amostra 2 | Usa34 – idem | #7B8C75 (32,2) · #73594E (30,6) · #393441 (18,8) · #B4A791 (18,4) | boa |
| 6 cores "chocolate chip" | Usa5 – idem (k=8) | #A69079 (31,6) · #AC9B86 (23,2) · #AF9387 (17,1) · #7A4F41 (13,2) · #968279 (4,9) · #BAA7A4 (4,1, "pedra branca") · #3F3338 (3,3, "pedra preta") · #675858 (2,6) | média: tons claros se sobrepõem |
| 3 cores deserto (DCU) | Usa8 – idem | #BAAB7D (51,9) · #D9C5A3 (38,9) · #814E18 (9,2) | boa |
| MARPAT floresta | Usa10 – idem | #BD9F80 (41,6) · #808A73 (29,3) · #7F6D5B (14,9) · #493D48 (14,2) | média |
| MARPAT deserto | Usa11 – idem | #C9B3A5 (44,8) · #B3957F (37,8) · #977255 (17,3) | média |
| UCP | Usa12 – idem | #7F8282 (37,3) · #A9A6A3 (31,5) · #626869 (31,1) | baixa: verde-sálvia não separado |
| ERDL verde | Usa2 – idem | #978972 (47,1) · #7F9478 (26,7) · #BAC68E (15,3) · #6B6965 (11,0) | média |
| Tiger stripe JWD | Arvn14 – [Camopedia Tiger](https://camopedia.org/index.php?title=Tiger_stripe) | #2E2A31 (37,1) · #57554A (36,9) · #736B5E (15,5) · #9C9484 (10,4) | média |
| Tiger stripe Tadpole Sparse | Arvn32 – idem | #75705C (33,7) · #4C4D4D (27,5) · #98927D (21,2) · #2A2C2E (17,6) | média |

### Inferences

**Classificação para o jogo** (usar sempre só nomes genéricos):
- **Evitar reproduzir** (proprietários ou restritos): MultiCam e derivados próximos, OCP/Scorpion, A-TACS, Kryptek, MARPAT, CADPAT, M90 atual e versões comerciais "Tiger Stripe™".
- **Padrões brasileiros:** a lei trata de uniformes e "confusão" com os das Forças Armadas, não de estampa em objeto virtual. Mesmo assim, por prudência institucional, recomendo **não copiar o desenho da "rajada"**. Faça um "lagarto vertical" original com paleta inspirada (verde-claro base, verde-escuro e marrom-arroxeado).
- **Históricos governamentais** (M81/ERDL, DCU, 6 cores, Flecktarn, DPM, Splittertarn, lagarto francês, tiger stripe histórico, Rhodesian): circulam amplamente em produtos comerciais. O caminho mais seguro continua sendo recriar a **família de forma** com desenhos e paletas próprios, em vez de copiar a arte.
- **Nomes genéricos sugeridos:** "Floresta 4 tons", "Deserto 3 tons", "Deserto pedregoso", "Pontilhado 5 tons", "Estilhaço", "Blocos nórdicos", "Listras de tigre", "Lagarto vertical", "Pinceladas", "Digital floresta", "Digital árido", "Folhas de bétula", "Multiterreno 7 tons".

**Escala na arma**
Os padrões de tecido foram desenhados para corpo humano e para distâncias de dezenas de metros até ~1 km (M90; M81 ampliado 60% sobre o ERDL). Na arma, reduza a escala para que o corpo de um fuzil mostre ~3–6 manchas principais, ou ~1,5–3 repetições de listra no comprimento do receiver. Em pistola e faca, suba um pouco a frequência. Isso é inferência de legibilidade, não dado de fonte.

**Proporções de área para thresholds**
As % do k-means podem virar os thresholds de camadas empilhadas. Exemplo Floresta 4 tons ≈ 33–35% verde, 28–31% marrom, 18–20% cáqui, 16–19% preto.

**Paleta brasileira-inspirada**
Base derivada das medições e da descrição do Camopedia (usar em padrão original):
- verde-claro ~#B1B29D–#C7BEAD;
- verde-médio ~#829177;
- marrom-arroxeado ~#8D7067 (saturar levemente para compensar o tecido lavado);
- evitar preto, coerente com a história do padrão.

### Gaps
- Não confirmei os números de sombra de tecido do M81 (Light Green 354, Field Drab 355, Brown 356, Black 357). A Wikipedia não os traz e a busca não os confirmou.
- Não encontrei padrão oficial de cor (CIELAB/hex) do Flecktarn, DPM, M90, EMR, Type 07, Vegetato ou do padrão do EB.
- Não localizei norma pública do EB com as cores do camuflado nem registro no INPI (desenho industrial) do padrão.
- Não confirmei o cronograma de obrigatoriedade 2022/2024/2026 visto em resumo de busca (Portaria C Ex nº 2.259/2024 inacessível).
- Não encontrei jurisprudência citável sobre uso parcial (calça/gandola) por civis. Um resumo de busca sugeriu que não configura crime sem características de engano, mas não foi verificado.
- O status legal (domínio público × restrito) de M81, UCP, DCU, Flecktarn, DPM, EMR e Type 07 não foi confirmado por fonte jurídica.
- Não verifiquei os registros de marca USPTO de Kryptek, A-TACS e MultiCam.
- Não achei medidas de repetição (repeat) dos tecidos.
- Não consegui extrair a descrição completa do Vegetato (truncada) nem o nome do novo padrão italiano de 2025.

---

## 4. Parâmetros físicos de renderização (MeshPhysicalMaterial), desgaste e receitas procedurais

### Takeaway
Três recursos do `MeshPhysicalMaterial` cobrem quase todo o catálogo:
- **metalness/roughness** com cores F0 de metais medidas;
- **`anisotropy`** para satin e escovado;
- **`iridescence`** (filme fino) para titânio anodizado, cores de revenimento, azul de nitrato, têmpera colorida e PVD iridescente.

A isso se somam **`clearcoat`** (verniz, hidrografia, fibra de carbono) e uma máscara de aresta ou desgaste que troca o acabamento pelo substrato. As formas dos padrões saem de ruído com threshold, domain warping, Voronoi/Worley (F1, F2, distância à borda), ondas deformadas e quantização em pixels.

### Cited Findings
- Cores base F0 de metais (lineares; o sRGB foi convertido por nós) — [Physically Based API](https://api.physicallybased.info/materials) ([site](https://physicallybased.info)):

  | Metal | Linear | sRGB |
  |---|---|---|
  | Alumínio | 0,916/0,923/0,924 | #F5F6F6 |
  | Cromo | 0,654/0,685/0,701 | #D3D8DA |
  | Níquel | 0,697/0,641/0,563 | #D9D1C6 |
  | Ferro | 0,530/0,513/0,494 | #C0BEBB |
  | Inox | 0,669/0,639/0,598 | #D6D1CB |
  | Titânio | 0,441/0,400/0,361 | #B1AAA2 |
  | Ouro | 1,059/0,773/0,307 | #FFE496 |
  | Cobre | — | #F7CFBF |
  | Latão | — | #F5E4AE |
  | Prata | — | #FEFDFC |
  | Zinco | — | #E8EDEF |
  | Tungstênio | — | #C2C1BF |
  | Cobalto | — | #DADAD6 |

  A mesma base descreve "Car Paint" como poliuretano acrílico com basecoat pigmentado e "clear topcoat" (roughness 0).
- three.js `MeshPhysicalMaterial` — [three.js docs](https://threejs.org/docs/pages/MeshPhysicalMaterial.html):
  - `anisotropy` 0–1 (padrão 0), com `anisotropyMap` (RG = direção em espaço tangente, B = força) e `anisotropyRotation`;
  - `clearcoat` e `clearcoatRoughness` 0–1, com mapas próprios;
  - `iridescence` 0–1;
  - `iridescenceIOR` entre 1,0 e 2,333 (padrão 1,3);
  - `iridescenceThicknessRange` padrão [100, 400];
  - `iridescenceThicknessMap`, que usa o canal G para interpolar entre mín. e máx.;
  - `ior` 1,0–2,333 (padrão 1,5);
  - `sheen` (tecidos).
- Iridescência real em dielétrico: a mesma base lista "Soap Bubble" (thinFilmIor 1,4, espessura 500 nm) e "Pearl" (2, 420 nm) — [Physically Based API](https://api.physicallybased.info/materials)
- Técnicas procedurais de referência:
  - Blender Wave: "adds procedural bands or rings with noise distortion". A distorção é somada às coordenadas, proporcional a Distortion/Scale — [Blender Manual – Wave](https://docs.blender.org/manual/en/latest/render/shader_nodes/textures/wave.html)
  - Blender Voronoi: F1, F2, "smooth F1", "distance to edge", "n-sphere radius", Randomness e métricas (Euclidiana, Manhattan, Chebychev) — [Blender Manual – Voronoi](https://docs.blender.org/manual/en/latest/render/shader_nodes/textures/voronoi.html)
  - Domain warping: "Warping simply means we distort the domain with another function g(p) before we evaluate f". Técnica usada desde o mármore de Perlin (1984) — [Inigo Quilez – warp](https://iquilezles.org/articles/warp/)
  - Ruído celular (Worley, 1996) é "based on distance fields, the distance to the closest one of a set of feature points" — [The Book of Shaders – Cellular noise](https://thebookofshaders.com/12/)
  - Há exemplos de damasco procedural no Blender que combinam ondas e ruído e imitam forja, esmerilhamento, ataque ácido e polimento (via resumo de busca) — [The Rookies](https://www.therookies.co/projects/7523); [ArtStation](https://www.artstation.com/artwork/LR59Nl)
  - Usuários do Blender tentaram reproduzir o M90 com Voronoi + color ramp (via resumo de busca) — [BlenderArtists](https://blenderartists.org/t/give-voronoi-texture-colors/621222)
- Fatos de desgaste por acabamento:
  - **Bluing:** fino (≤2,5 µm), sofre holster wear — [Wikipedia – Bluing](https://en.wikipedia.org/wiki/Bluing_(steel))
  - **Têmpera colorida:** desbota com sol e uso, "first along edges" — [Shooting Sportsman](https://shootingsportsman.com/color-case-hardening/)
  - **Anodizado tingido:** o corante é superficial e riscos atravessam a camada tingida — [Wikipedia – Anodizing](https://en.wikipedia.org/wiki/Anodizing)
  - **Parkerização:** o excesso de camada sai "in the very early stages of use"; a cor evolui com óleos e sujeira — [Brownells](https://feeds.brownells.com/userdocs/learn/076-200-482_Manganese_and_Zinc_Parkerizing.pdf)
  - **Nitreto:** a proteção permanece mesmo sem a camada preta — [Wikipedia – FNC](https://en.wikipedia.org/wiki/Ferritic_nitrocarburizing)
  - **Cerakote "Torn":** revela a camada inferior ou o metal — [Aegis](https://www.aegiscerakote.com/services/custom-cerakote/patterns/)
  - **Lâminas:** stonewash esconde riscos; mirror e satin os mostram; DLC mostra marcas (via resumo de busca) — [Noblie](https://nobliecustomknives.com/knife-blade-finishes/)
- A cor do Ti anodizado muda com o ângulo, por interferência — [PartMFG](https://www.partmfg.com/titanium-anodizing-color-chart/)

### Inferences

**Tabela de partida por acabamento**
Todos os valores são estimativas nossas, não medições. Cores base vêm das seções 1–3 ou da tabela de metais acima.

| Acabamento | metalness | roughness | clearcoat | anisotropy | iridescence (IOR / espessura) | Desgaste (máscara de aresta → substrato) |
|---|---|---|---|---|---|---|
| Cerakote/Duracoat fosco-satin | 0 (metálicos: 0,4–0,7 + ruído de normal "flake") | 0,55–0,8 | 0 | 0 | — | lasca nítida → base (alumínio anodizado ou aço fosfatizado); borda levemente clara |
| Pintura/hidrografia com verniz | 0 | 0,4–0,6 | 0,6–1,0 (cc-rough 0,05–0,2) | 0 | — | verniz fosqueia → arte → base → metal |
| Anodizado Al Tipo III preto | 0 | 0,5–0,7 | 0 | 0 | — | alumínio claro (#F5F6F6, rough 0,3–0,5) em arestas e cantos vivos |
| Titânio anodizado | 1 (base #B1AAA2) | 0,2–0,45 | 0 | 0–0,3 (se escovado) | 1 / IOR 2,3 (teto 2,333) / 20–230 nm | metal cinza nas arestas (filme removido) |
| Revenimento, azul de nitrato | 1 (base #C0BEBB escurecida) | 0,15–0,35 | 0 | 0 | 1 / IOR ~2,3 / 20–80 nm | aço polido claro |
| Têmpera colorida | 1 | 0,2–0,4 | 0 (armas finas às vezes envernizadas: 0,3) | 0 | 0,7–1 / espessura por ruído 20–70 nm + manchas cinza | desbota para cinza-prata nas arestas |
| Oxidação a quente (blue-black) | 0,6–0,9 | 0,15–0,3 polido; 0,45–0,6 jateado | 0 | 0 | opcional 0,1–0,2 | aço brilhante nas arestas (holster wear) |
| Parkerização | 0–0,2 | 0,75–0,95 | 0 | 0 | — | cinza-aço fosco lentamente; tinte de óleo nos recessos |
| Nitreto/Tenifer | 0,3–0,6 | 0,6–0,8 | 0 | 0 | — | cinza-aço opaco (não brilhante) |
| DLC/PVD preto | 0,2–0,5 | 0,25–0,45 | 0 | 0 | — | riscos finos claros |
| TiN dourado | 1 (base dourada, ~#D9B86A, estimativa) | 0,15–0,35 | 0 | 0 | — | aço claro |
| Níquel acetinado / NP3 | 1 (#D9D1C6) | 0,3–0,5 | 0 | 0 | — | quase não muda (fosqueia levemente) |
| Cromo brilhante | 1 (#D3D8DA) | 0,03–0,12 | 0 | 0 | — | micro-riscos |
| Ouro (gatilho, detalhes) | 1 (#FFE496) | 0,1–0,3 | 0 | 0 | — | latão ou aço por baixo |
| Inox satin (faca) | 1 (#D6D1CB) | 0,25–0,4 | 0 | 0,6–0,9 ao longo da lâmina | — | riscos direcionais |
| Fibra de carbono | 0 (base ~#101010) | 0,3–0,5 | 1 (cc-rough 0,03–0,1) | 0,5–0,8, direção alternando por tow | — | verniz fosqueia |

**Receitas procedurais por família**
Trabalhar em coordenada de objeto triplanar, com o eixo X ao longo do cano ou da lâmina:
1. **Manchas orgânicas (Floresta 4 tons, ERDL-like, DPM-like):**
   - `n = fbm(p*s + warp(p))`, com 3–5 oitavas de simplex e domain warp de amplitude 0,3–0,6;
   - camadas empilhadas com thresholds diferentes e sementes diferentes por cor (ordem: base clara → verde → marrom → "galhos" pretos);
   - para os "galhos", usar threshold de banda estreita (`abs(n2-0.5)<w`).
2. **Pontilhado (Flecktarn-like):** várias camadas de Worley F1 com células pequenas e raio modulado por ruído, cada camada com densidade e cor próprias. Bordas com ruído de alta frequência para irregularidade.
3. **Estilhaço / polígonos (Splittertarn / M90-like):**
   - Voronoi com cor por hash do ID da célula;
   - estirar o domínio (anisotropia 1,5–3×) e usar métrica Manhattan ou Chebychev para ângulos duros;
   - no estilo Splittertarn, somar tracejados finos ("chuva": linhas curtas em `fract(v*k)` mascaradas por ruído).
4. **Listras (tiger / lagarto / pincelada):**
   - ruído anisotrópico: estirar 6–12× na direção da listra (tiger = ao longo do cano; lagarto = perpendicular);
   - `ridged` + threshold, com as listras escuras por cima;
   - para "pincelada", adicionar estrias de cerdas (ruído 1D de alta frequência ao longo do traço) na borda.
5. **Digital (MARPAT-/CADPAT-/EMR-like):** gerar o padrão orgânico e **quantizar o domínio** antes de amostrar (`p = floor(p*N)/N`), em duas escalas (macro + micro) para o efeito "multi-scale". Opcionalmente, dithering nas bordas. Não usar "pixels orgânicos" agrupados em macroformas, estilo associado ao A-TACS (patenteado).
6. **Multiterreno em gradiente:**
   - gradiente de baixa frequência (marrom → bege);
   - manchas médias de verde com blending suave;
   - formas pequenas opacas escuras e creme por cima (Worley com threshold).

   Criar paleta própria, não os hex do MultiCam.
7. **Pedregoso (6 cores-like):** base + faixas largas + "pedras" Worley pequenas em aglomerados, cada pedra preta com cópia branca deslocada (sombra).
8. **Folhas de bétula (Berezka-like):** Voronoi F2−F1 recortado em formas serrilhadas, em duas cores sobre fundo.
9. **Padrões de pintor:**
   - topográfico: isolinhas `abs(fract(n*k)-0.5)<w`;
   - favo de mel: SDF hexagonal;
   - "mármore/damasco cerakote": seno com domain warp;
   - "battleworn": máscara de desgaste amplificada + ruído, revelando uma cor de base metálica;
   - "fade": gradiente por eixo com dithering de spray (ruído fino).
10. **Iridescência controlada:** mapear a espessura desejada em nm para `iridescenceThicknessRange` com mín. = máx. (cor sólida), ou com um `iridescenceThicknessMap` de ruído (têmpera colorida, pátina, "rainbow"). Usar `iridescenceIOR` ≈ 2,3. Conferir visualmente contra as tabelas calculadas (seção 1), já que o three.js modela filme não absorvente.

**Mapeamento para as zonas de material do jogo**
Combinações realistas:
- **corpo (receiver/slide):** acabamento principal (Cerakote, anodizado, nitreto, oxidado, têmpera colorida);
- **guarda-mão e coronha (furniture):** mesmo padrão com leve variação de tom ou polímero liso, já que ligas e materiais diferentes "não combinam", como no Tipo III;
- **carregador:** polímero ou alumínio anodizado com desgaste forte na boca e nos lábios;
- **detalhes (pinos, parafusos, miras):** azul de nitrato, ouro ou TiN em skins premium; aço oxidado nas comuns;
- **internos (ferrolho, cano):** fosfato de manganês, nitreto, TiN ou níquel/NP3.

A máscara de aresta baked deve escolher um "substrato" por acabamento, conforme a tabela acima.

### Gaps
- Não achei medições publicadas de rugosidade ou anisotropia por acabamento real (Cerakote, parkerização, nitreto, bluing). Todos os números da tabela são estimativas para ajuste artístico.
- Não verifiquei constantes ópticas de TiO₂ anódico nem de óxidos de ferro. Os valores dos modelos de filme fino são aproximados.
- O modelo de iridescência do three.js não representa filme absorvente, o que pode limitar a fidelidade das cores de revenimento.
- Não li integralmente nenhum tutorial específico de camuflagem procedural. Os exemplos de damasco procedural e o tópico do M90 foram vistos só por resumo de busca.
