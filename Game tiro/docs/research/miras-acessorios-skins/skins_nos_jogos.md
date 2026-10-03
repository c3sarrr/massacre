# Sistemas de skins de armas e facas em jogos de tiro (e pintura de carros) — taxonomia de referência para o MASSACRE

> Pesquisa feita em 28/09/2026. Todos os nomes de skins, acabamentos, camuflagens, moedas e sistemas citados abaixo (ex.: "Doppler", "Case Hardened", "Dark Matter", "StatTrak™", "Radianite") pertencem aos respectivos jogos/empresas e aparecem **apenas como referência**. O MASSACRE deve usar nomes 100% originais.
> Método: além de fontes web, foram lidos diretamente os arquivos de dados do CS2 espelhados pelo SteamDatabase (`items_game.txt` e `csgo_english.txt`, versão atual do repositório GameTracking-CS2). Os números marcados "schema" vêm dessa leitura.

---

## 1. Counter-Strike (CS:GO/CS2): como os acabamentos são construídos, desgaste (float), semente de padrão, raridade, extras e acabamentos de faca

### Takeaway
No CS, uma skin é **arma + "paint kit"** (definição de acabamento em texto): um de 9 estilos documentados (mais um estilo 10 não documentado no schema), até 4 cores, uma textura de padrão cujos canais RGB guardam 3 máscaras, o alfa guardando durabilidade ou rugosidade, faixas de escala/offset/rotação e uma faixa de desgaste. Cada item individual recebe 3 números aleatórios: índice do paint kit, semente de padrão e float de desgaste. É dessa aleatoriedade (fases, "gemas", % de degradê, teias centralizadas, floats extremos) que vem a maior parte do valor percebido.

### Cited Findings

#### 1.1 Filosofia e os estilos oficiais (Workshop)
- A Valve declara que "Counter-Strike is a game set in reality, so we researched real-world finishing techniques. We reproduced spray-painted camouflaging, hydro-dipping, patinas, and more" e que "every finish is available in a variety of states of wear". Cada estilo "represents a real-world gunsmithing or finishing technique"; "the recipe for a finished weapon is simple: an existing weapon and a finish definition", e o mesmo acabamento pode ser aplicado a armas diferentes — [CS2 Workshop Finishes (oficial)](https://www.counter-strike.net/workshop/workshopfinishes)
- Tabela dos estilos (texto e parâmetros da doc oficial; número do estilo conferido no schema pelo prefixo interno dos paint kits: `so_`=1, `hy_`=2, `sp_`=3, `an_`=4, `am_`=5, `aa_`=6, `cu_`=7, `aq_`=8, `gs_`=9) — [Workshop Finishes](https://www.counter-strike.net/workshop/workshopfinishes); [items_game.txt (schema CS2)](https://github.com/SteamDatabase/GameTracking-CS2/blob/master/game/csgo/pak01_dir/scripts/items/items_game.txt)

| Estilo (nome Valve, referência) | Nº no schema | Entradas | Mapeamento | Como desgasta | Técnica real simulada |
|---|---|---|---|---|---|
| Solid Color | 1 | até 4 cores, aplicadas por "paint by number" (regiões predefinidas por arma) | regiões da arma | "wears directly to the substrate" | peças pintadas separadamente antes da remontagem |
| Hydrographic | 2 | 4 cores + 1 textura de padrão; áreas sólidas usam "Green Channel" e "Blue Channel"; alfa = durabilidade/máscara | UVs originais da arma; escala relativa a folha de 36" | direto ao substrato | peças mergulhadas em película flutuante num tanque d'água (hydro-dip) |
| Spray-Paint | 3 | 4 cores + 1 padrão (estêncil) | **triplanar** ("spray painting through a stencil onto the sides, top, bottom, back and front"); escala relativa a 18" | "each layer of paint wears successively to the layer below it before revealing the substrate" | várias demãos de spray por estênceis |
| Anodized | 4 | 1 cor | regiões "anodizáveis" | "wears first to the chrome base coat before revealing the substrate" | "colored candy coat over a chrome base" (verniz colorido translúcido sobre cromo) |
| Anodized Multicolored | 5 | 4 cores + 1 padrão; alfa = rugosidade (0–127) + máscara | UVs originais; 36" | direto ao substrato | verniz translúcido aplicado em padrão (serigrafia/estêncil) |
| Anodized Airbrushed | 6 | 4 cores + 1 padrão | triplanar; 18" | primeiro ao cromo, depois ao substrato | verniz translúcido aplicado à mão com aerógrafo |
| Custom Paint Job | 7 | 1 imagem colorida completa; alfa = durabilidade/máscara; aceita normal map | UVs originais; 36" | direto ao substrato | pintura ilustrada livre |
| Patina | 8 | 4 cores com papéis fixos (Base Metal, Patina Tint, Patina Wear, Grime) + imagem colorida; aceita normal map | UVs originais; 36" | arranhões revelam o metal base; a pátina "envelhece" da cor Tint para a cor Wear | reação química que forma casca endurecida: "case hardening, cold bluing, and acid forced patinas" |
| Gunsmith | 9 | Patina + Custom Paint combinados por paint-by-number; alfa = rugosidade nas partes com pátina, máscara nas partes pintadas; normal map | UVs originais; 36" | híbrido | "combination of patina and custom paint styles" |

- Ainda na tabela: o papel das 4 cores do estilo Patina é "Base Metal: the metal before patina, revealed through scratches; Patina Tint: tint of the newly applied patina; Patina Wear: tint of the aged patina; Grime: color of the grime, oil accretion, or oxide that accumulates in cavities" — [Workshop Finishes](https://www.counter-strike.net/workshop/workshopfinishes)
- O Gunsmith foi criado a partir de feedback dos autores do Workshop e combina recursos do Custom Paint Job, Patina e Anodized Multicolored — [resultado de busca sobre a doc/anúncio "New Paint Style: Gunsmith"](https://steamcommunity.com/games/CSGO/announcements/detail/47636923019498014) (a página do anúncio não carregou; a data não foi confirmada)
- Dos 1.481 paint kits do schema atual, 1.387 têm estilo definido (os demais, como os de luvas, usam material próprio). A distribuição por estilo é: Custom Paint (7) 388; Gunsmith (9) 304; Hydrographic (2) 220; Anodized Multicolored (5) 150; Spray-Paint (3) 146; Solid Color (1) 71; Patina (8) 63; Anodized Airbrushed (6) 29; Anodized (4) 10; estilo 10: 4 — [schema](https://github.com/SteamDatabase/GameTracking-CS2/blob/master/game/csgo/pak01_dir/scripts/items/items_game.txt)
- **Estilo 10 (não documentado publicamente):** é usado por acabamentos novos de "tratamento térmico": "Heat Treated" (Five-SeveN e Desert Eagle), "Rainbow Spoon" ("achieved by heating the painted weapon to very high temperatures. By using this method the number of unique finishes is almost infinite") e "Runoff" ("lightly color case-hardened") — [schema](https://github.com/SteamDatabase/GameTracking-CS2/blob/master/game/csgo/pak01_dir/scripts/items/items_game.txt) + [localização csgo_english.txt](https://github.com/SteamDatabase/GameTracking-CS2/blob/master/game/csgo/pak01_dir/resource/csgo_english.txt). O Desert Eagle "Heat Treated" foi item de tempo limitado da The Armory (out/2024) — [BLAST.tv](https://blast.tv/cs/news/cs2-the-amory-update)
- Exemplos do estilo Anodized (4) no schema: "Anodized Navy", "Silver", "Hot Rod" (vermelho), "Emerald", "Anodized Gunmetal" e "Blue Titanium" ("oxide layer achieved via controlled anodization at 30 volts", float travado em 0,00–0,04) — [schema](https://github.com/SteamDatabase/GameTracking-CS2/blob/master/game/csgo/pak01_dir/scripts/items/items_game.txt)

#### 1.2 O "paint kit" em texto: parâmetros
- Os acabamentos "are defined by a set of parameters that are stored in a plain text files", gerados pelo Workbench/Item Editor do Workshop. Exemplo oficial de Spray-Paint: `"style" "3"`, `"pattern" "tiger"`, `"pattern_scale" "0.9"`, `"color0".."color3"` (RGB), `"phongintensity" "5"`, `"phongexponent" "32"`, `"pattern_offset_x_start" "0"`, `"pattern_offset_x_end" "1"`, `"pattern_offset_y_start/end"`, `"pattern_rotate_start" "-10"`, `"pattern_rotate_end" "7"`, `"wear_remap_min" "0.06"`, `"wear_remap_max" "0.8"` — [Workshop Finishes](https://www.counter-strike.net/workshop/workshopfinishes)
- Outros parâmetros que aparecem nos exemplos oficiais: `phongalbedoboost`, `ignore_weapon_size_scale`, `only_first_material`, `view_model_exponent_override_size` ("should only be used in conjunction with an exponent map in the alpha channel... The exponent texture is a 256 square texture by default to conserve memory"); exemplo Patina com rotação `0`→`360`; exemplo Gunsmith com padrão `mother_of_pearl_elite` e cores brancas/cinza — [Workshop Finishes](https://www.counter-strike.net/workshop/workshopfinishes)
- **Randomização:** "All paints specify ranges for offsets and rotations. On application, random values are chosen within those ranges so that each application is unique. Paints also specify a range for wear. On application, a random value is chosen within that range" — [Workshop Finishes](https://www.counter-strike.net/workshop/workshopfinishes)
- **Escala por arma:** "For most styles the scale of the pattern is relative to a pattern sheet size of 36 inches. For styles that use triplanar mapping, 18 inches". A escala é corrigida automaticamente por arma para o tamanho ser consistente; `"ignore_weapon_size_scale" "1"` desliga isso (usado quando a arte precisa casar exatamente com as UVs) — [Workshop Finishes](https://www.counter-strike.net/workshop/workshopfinishes)
- **Textura de padrão com 3 imagens:** "we take advantage of this configuration to store three separate images" nos canais R, G e B — [Workshop Finishes](https://www.counter-strike.net/workshop/workshopfinishes)
- **Regra de autoria:** "Don't include grime, scratches, ambient occlusion, or details from the weapon in your finish. The composite system will do it for you" — [Workshop Finishes](https://www.counter-strike.net/workshop/workshopfinishes)
- **Normal map** "can be applied to Patina, Custom Paint, and Gunsmith finish styles" (ex.: veio de madeira) — [Workshop Finishes](https://www.counter-strike.net/workshop/workshopfinishes)
- **Paint by number:** "All finishable weapons are divided into regions that define how the finish styles apply their colors and patterns", e há áreas que nunca recebem acabamento ("shell casings, the inside of barrels, firing rods, etc.") — [Workshop Finishes](https://www.counter-strike.net/workshop/workshopfinishes)
- Observação de consistência: nos exemplos da própria doc, o bloco Hydrographic usa `"style" "3"` (igual ao Spray-Paint) e o bloco Anodized usa `"style" "1"`, enquanto o schema usa 2 e 4 para esses estilos. Isso parece erro de cópia na doc — [Workshop Finishes](https://www.counter-strike.net/workshop/workshopfinishes) vs [schema](https://github.com/SteamDatabase/GameTracking-CS2/blob/master/game/csgo/pak01_dir/scripts/items/items_game.txt)

#### 1.3 Durabilidade, rugosidade e PBR
- **Máscara de durabilidade no alfa** (Hydrographic, Custom Paint e as partes pintadas do Gunsmith): "Values around 196 in the alpha channel subtract from the refinishable areas... Both 128 and 255 have no effect... Values below 128 in the alpha channel increase the durability of the finish. The darker the value, the more durable the paint". No exemplo oficial, os olhos de um monstro ficavam num canto que arranha fácil, então a área foi marcada como mais durável "so that it is readable even when the finish is well worn" — [Workshop Finishes](https://www.counter-strike.net/workshop/workshopfinishes)
- **Rugosidade no alfa** (Anodized Multicolored e as partes com pátina do Gunsmith): permite "finishes that look as though they are comprised of several different types and reflectivities of paint". Fica só na faixa 0–127 e é invertida ("higher values represent smoother surfaces") por retrocompatibilidade — [Workshop Finishes](https://www.counter-strike.net/workshop/workshopfinishes)
- **PBR:** "CS2 uses physically based rendering... artists will now use an albedo texture". Para acabamentos metálicos, "effective RGB range is most likely between 180-250. Values as low as 90 may be acceptable"; para não metálicos, "55-220". Fora disso "will not respond appropriately to in-game lighting", e esses acabamentos "are unlikely to be selected from the workshop" — [Workshop Finishes](https://www.counter-strike.net/workshop/workshopfinishes)

#### 1.4 Desgaste (float / "wear rating")
- O float é sorteado ao dropar, abrir caixa ou sair de um trade-up. A distribuição segue "a bell curve for most weapons, with low float Factory New items and high float Battle-Scarred items being the rarest"; "A weapon float will not degrade over time and can never be changed" — [Counter-Strike Wiki – Skins](https://counterstrike.fandom.com/wiki/Skins)
- **Faixas — há conflito entre fontes:**
  - Doc oficial do Workshop e wiki: Factory New 0,00–0,07; Minimal Wear 0,07–0,15; Field-Tested 0,15–**0,37**; Well-Worn 0,37–**0,44**; Battle-Scarred 0,44–1,00 — [Workshop Finishes](https://www.counter-strike.net/workshop/workshopfinishes); [CS Wiki – Skins](https://counterstrike.fandom.com/wiki/Skins)
  - Guias de mercado usam FT 0,15–**0,38**, WW 0,38–**0,45**, BS 0,45–1,00 — [ProSettings](https://prosettings.net/blog/cs2-skin-conditions-explained/); [DMarket](https://dmarket.com/blog/csgo-skin-float-guide/)
- **Limites de float por skin (float cap):** a doc diz que as faixas de desgaste não precisam cobrir 0–1 e que "many weapon finishes ship with wear values from Factory New (0.0) to Battle Scarred (0.6)". O paint kit "default" do schema usa 0,06–0,80, herdado por kits sem faixa própria — [Workshop Finishes](https://www.counter-strike.net/workshop/workshopfinishes); [schema](https://github.com/SteamDatabase/GameTracking-CS2/blob/master/game/csgo/pak01_dir/scripts/items/items_game.txt)
- Exemplos de float cap no schema: Fade 0,00–0,08 (só FN/MW); Rust Coat de faca 0,40–1,00 (só WW/BS); Slaughter 0,01–0,26; Blue Titanium 0,00–0,04. Fade tem kits diferentes por arma com tetos diferentes (revólver 0,00–0,40; MP7 0,00–0,25) — [schema](https://github.com/SteamDatabase/GameTracking-CS2/blob/master/game/csgo/pak01_dir/scripts/items/items_game.txt)
- "As the wear increases, more scratches appear" — [Workshop Finishes](https://www.counter-strike.net/workshop/workshopfinishes). A wiki acrescenta: "some weapon finishes even have easter eggs built into the scratch pattern for higher floats" — [CS Wiki – Skins](https://counterstrike.fandom.com/wiki/Skins)

#### 1.5 Semente de padrão (pattern index/"paint seed") e fenômenos de padrão
- **Implementação (schema):** cada item tem os atributos `set item texture prefab` (id 6 = índice do paint kit), `set item texture seed` (id 7 = semente) e `set item texture wear` (id 8 = float) — [schema](https://github.com/SteamDatabase/GameTracking-CS2/blob/master/game/csgo/pak01_dir/scripts/items/items_game.txt)
- **Faixa da semente — conflito:** a wiki fala em "a visible pattern index seed between 1 & 1000" ([CS Wiki – Skins](https://counterstrike.fandom.com/wiki/Skins)), e o CS2 Float Checker também diz "1 to 1000" ([cs2floatchecker](https://cs2floatchecker.com/blog/pattern-guide)). Guias de Case Hardened dizem 0–999 ([csdb.gg](https://csdb.gg/guides/case-hardened-guide/); [SteamAnalyst](https://www.steamanalyst.com/guides/blue-gem)).
- A semente é determinística: "pattern 661 on an AK-47 will always be the Blue Top", e o float não altera a distribuição de cores — [SteamAnalyst – Blue Gem](https://www.steamanalyst.com/guides/blue-gem); [csdb.gg](https://csdb.gg/guides/case-hardened-guide/)
- **Case Hardened ("blue gem"):** a semente define a distribuição azul/dourado/roxo. Azul é o mais valioso e dourado o mais comum. AK-47 #661 é o padrão mais famoso ("Scar Pattern"/"Blue Top"), e Karambit #387 é citado como top — [SteamAnalyst](https://www.steamanalyst.com/guides/blue-gem); [cs2floatchecker](https://cs2floatchecker.com/blog/pattern-guide) (os valores em US$ desses guias variam e são de agregadores)
- **Doppler / Gamma Doppler:** no schema, **cada "fase" é um paint kit diferente** (índice de pintura, não semente): Ruby 415, Sapphire 416, Black Pearl 417, Phase 1–4 = 418–421 (mais variantes 617–619 e 852–855). Todos são agrupados sob o mesmo nome de mercado pelo campo `same_name_family_aggregate`. No Gamma Doppler, Emerald = 568 e Phase 1–4 = 569–572; a Glock tem bloco próprio (1119–1123, float 0,00–0,50) — [schema](https://github.com/SteamDatabase/GameTracking-CS2/blob/master/game/csgo/pak01_dir/scripts/items/items_game.txt); os mesmos números aparecem em [csdb.gg](https://csdb.gg/doppler-phases/) e [SteamAnalyst](https://www.steamanalyst.com/guides/doppler-phases). **Conflito:** alguns guias dizem que a fase é determinada pelo "pattern index (paint seed)", mas o schema mostra que ela vem do índice do paint kit.
- Cores descritas pelos guias: Ruby = vermelho integral; Sapphire = azul intenso com tons de roxo; Black Pearl = roxo profundo e preto; Emerald = verdes claro e escuro; Phases 1–4 = misturas azul/roxo/preto — [csdb.gg](https://csdb.gg/doppler-phases/); [vskin.gg](https://vskin.gg/guides/cs2-doppler-patterns)
- **Fade:** o "% de fade" varia com a semente (posição do degradê). Os guias classificam faixas como "100%/Max", "95%" e "90%", com prêmio sobre fades baixos — [cs2floatchecker](https://cs2floatchecker.com/blog/pattern-guide)
- **Marble Fade:** mistura de três cores (vermelho, azul e amarelo) cuja proporção varia com a semente. "Fire & Ice" é o padrão sem amarelo (só vermelho e azul), e é o mais valorizado — [csgoskins.gg](https://csgoskins.gg/blog/karambit-marble-fade-fire-and-ice-seed-patterns); [SteamAnalyst – Fire & Ice](https://www.steamanalyst.com/guides/fire-ice)
- **Crimson Web:** a semente define onde ficam as teias. Teias grandes e centralizadas no lado visível ("playside") são raras e caras; guias classificam por número de teias centralizadas (1, 2, 3+) — [SteamAnalyst – Crimson Web](https://www.steamanalyst.com/guides/crimson-web-pattern); [cs2floatchecker](https://cs2floatchecker.com/blog/pattern-guide)
- A seed/float de um item pode ser consultada com o "inspect link" em ferramentas como o CSFloat — [SteamAnalyst – Blue Gem](https://www.steamanalyst.com/guides/blue-gem)
- A doc oficial incentiva "Easter eggs" escondidos em certas rotações/offsets — [CS2 Workshop Styleguide](https://www.counter-strike.net/workshop/workshopstyleguide)

#### 1.6 Raridade: tiers, cores e probabilidades
- Tiers (chave interna → nome de arma → cor hex no schema): common → Consumer Grade `#b0c3d9`; uncommon → Industrial Grade `#5e98d9`; rare → Mil-Spec Grade `#4b69ff`; mythical → Restricted `#8847ff`; legendary → Classified `#d32ce6`; ancient → Covert `#eb4b4b`; immortal → Contraband `#e4ae39`; unusual ("★", facas/luvas) `#ffd700`. A cor "strange" (StatTrak) é `#CF6A32` — [schema](https://github.com/SteamDatabase/GameTracking-CS2/blob/master/game/csgo/pak01_dir/scripts/items/items_game.txt) + [csgo_english.txt](https://github.com/SteamDatabase/GameTracking-CS2/blob/master/game/csgo/pak01_dir/resource/csgo_english.txt)
- A wiki descreve as mesmas faixas por cor (branco, azul-bebê, azul-marinho, roxo, rosa, vermelho, dourado "Exceedingly Rare" para ★ facas/luvas e "Contraband" descontinuado). Bordas especiais: amarelo = Souvenir, laranja = StatTrak™, roxo = ★ — [CS Wiki – Skins](https://counterstrike.fandom.com/wiki/Skins)
- **Probabilidades de caixa:** Mil-Spec 79,92%; Restricted 15,98%; Classified 3,20%; Covert 0,64%; faca/luva 0,26% (≈1 em 385). Os números foram divulgados pela Valve depois que a China passou a exigir, em 2017, a publicação de odds de loot boxes (via a Perfect World) — [csgoskins.gg](https://csgoskins.gg/blog/csgo-case-odds-the-official-numbers-published-by-valve); [SteamAnalyst](https://www.steamanalyst.com/guides/case-odds)
- **Contraband:** o M4A4 "Howl" foi alterado e tornado Contraband em 11/06/2014 por violação de direitos autorais (arte plagiada). Ele deixou de sair de caixas e de trade-ups, e cinco outras skins ligadas ao mesmo autor foram removidas — [CS Wiki – Huntsman Weapon Case](https://counterstrike.fandom.com/wiki/Huntsman_Weapon_Case); [CS Wiki – M4A4](https://counterstrike.fandom.com/wiki/M4A4)

#### 1.7 StatTrak™, Souvenir, adesivos, name tags, charms (e seus atributos técnicos)
- **StatTrak™:** conta as abates do dono; o contador não vai junto quando a arma é trocada entre jogadores (pode ser movido com o "StatTrak Swap Tool"). Sai de caixas ou de trade-up só com itens StatTrak; coleções de mapa não têm StatTrak — [CS Wiki – Skins](https://counterstrike.fandom.com/wiki/Skins). No schema, são os atributos `kill eater` / `kill eater score type` (ids 80–83, 88–89) e `stattrak model` (147) — [schema](https://github.com/SteamDatabase/GameTracking-CS2/blob/master/game/csgo/pak01_dir/scripts/items/items_game.txt)
- **Souvenir:** só sai de pacotes de Majors, de coleções de mapa, com adesivos do evento. Desde a StarLadder Berlin 2019, os pacotes vêm de "Souvenir tokens" comprados na loja — [CS Wiki – Souvenir](https://counterstrike.fandom.com/wiki/Souvenir)
- **Name Tag:** lançada em 29/08/2013 por US$ 1,99. Renomeia a arma (até 20 caracteres), o nome aparece entre aspas no killcam/menu/inventário e acompanha a arma em trocas — [CS Wiki – Name Tag](https://counterstrike.fandom.com/wiki/Name_Tag). Atributo `custom name attr` (111) — [schema](https://github.com/SteamDatabase/GameTracking-CS2/blob/master/game/csgo/pak01_dir/scripts/items/items_game.txt)
- **Adesivos:** lançados em 05/02/2014; máximo de 5 por arma; raridades High Grade (azul), Remarkable (roxo), Exotic (rosa), Extraordinary (vermelho) e Contraband (dourado). Não têm desgaste fixo, mas podem ser "raspados" (scrape) — [CS Wiki – Sticker](https://counterstrike.fandom.com/wiki/Sticker). No schema: `max_num_stickers "5"` e atributos por slot `sticker slot N id/wear/scale/rotation/offset x/offset y` (a posição livre fica em offset x/y) — [schema](https://github.com/SteamDatabase/GameTracking-CS2/blob/master/game/csgo/pak01_dir/scripts/items/items_game.txt)
- **Charms (chaveiros) — The Armory, 03/10/2024:** o Armory Pass custa US$ 15,99, dá 40 créditos e até 5 podem progredir juntos. Os charms podem ser posicionados em qualquer lugar da arma. As primeiras coleções foram "Small Arms" (miniaturas de armas) e "Missing Link" (personagens). A mesma atualização trouxe um slider de nível de raspagem de adesivos com pré-visualização — [BLAST.tv](https://blast.tv/cs/news/cs2-the-amory-update). "All charms have paint seeds, so your charm may have a unique color pattern", e eles balançam com o movimento — [GamerPay Blog](https://www.blog.gamerpay.gg/skins-stickers-items/cs2-weapon-charms-guide). No schema há 143 definições de chaveiro e os atributos `keychain slot 0 offset x/y/z`, `keychain slot 0 seed` e `keychain slot 0 highlight` — [schema](https://github.com/SteamDatabase/GameTracking-CS2/blob/master/game/csgo/pak01_dir/scripts/items/items_game.txt)

#### 1.8 Obtenção no CS
- Formas de obter: drops aleatórios jogando; abrir contêineres (caixas de armas, pacotes souvenir); **Trade Up Contract** (10 skins da mesma raridade → 1 de raridade acima); Steam Market; troca entre jogadores — [CS Wiki – Skins](https://counterstrike.fandom.com/wiki/Skins). A chave para abrir caixa custa US$ 2,49 — [GeekWire](https://www.geekwire.com/2026/valve-software-sued-by-new-york-ag-accused-of-promoting-illegal-gambling-via-video-game-loot-boxes/)
- Fora das facas, as skins são organizadas em **coleções**: cada caixa é uma coleção, e há coleções temáticas ou de mapa. Jogar num mapa não garante skin da coleção daquele mapa — [CS Wiki – Skins](https://counterstrike.fandom.com/wiki/Skins)
- **Atualização de 23/10/2025:** o Trade Up passou a aceitar 5 itens Covert → 1 faca ou luva da coleção de um dos itens. Covert "combustível" disparou de preço e facas/luvas despencaram (até −70%). Uma estimativa aponta queda da capitalização de US$ 609 mi para US$ 337 mi (−45% em horas); outra fala em US$ 2 bi de valor apagado. Os números **conflitam** entre fontes — [esports.net](https://www.esports.net/wiki/guides/cs2-knives-skin-market-crash/); [SIH blog](https://blog.sih.app/en/news/shocking-cs2-update-valve-adds-trade-contracts-for-knives-and-gloves-causing-panic-in-the-skins-market-is-everything-really-that-bad); [Esports Legal News](https://esportslegal.news/2025/11/18/cs2-collapse-no-one-saw-coming/)

#### 1.9 Acabamentos de faca: estilo técnico, faixa de float e descrição oficial de "como foi feito"
(estilo e faixa: [schema](https://github.com/SteamDatabase/GameTracking-CS2/blob/master/game/csgo/pak01_dir/scripts/items/items_game.txt); descrições entre aspas: [csgo_english.txt](https://github.com/SteamDatabase/GameTracking-CS2/blob/master/game/csgo/pak01_dir/resource/csgo_english.txt); "padrão 0,06–0,80" = sem faixa própria, herda o kit default)

| Acabamento (referência) | Estilo | Float | Descrição oficial (resumo/citação) | Variação individual |
|---|---|---|---|---|
| Fade | Anodized Airbrushed (6) | 0,00–0,08 | "painted by airbrushing transparent paints that fade together over a chrome base coat" | % de fade por semente |
| Doppler | Anodized Multicolored (5) | 0,00–0,08 | "black and silver metallic paints using a marbleizing medium, then candy coated" | fases = kits 415–421 (+617–619, 852–855) |
| Gamma Doppler | 5 | 0,00–0,08 | mesma técnica de marmorização + verniz | Emerald 568, Phases 569–572 |
| Marble Fade | 5 | 0,00–0,08 | marmorizado "then candy coated in three colors" | proporção de 3 cores; "Fire & Ice" |
| Tiger Tooth | 5 | 0,00–0,08 | "anodized orange and hand-etched in a tiger stripe pattern" | — |
| Case Hardened | Patina (8) | 0,00–1,00 | "color case-hardened through the application of wood charcoal at high temperatures" | % azul ("blue gem") por semente |
| Crimson Web | Hydrographic (2) | padrão 0,06–0,80 | "spider web-patterned hydrographic over a red base coat and finished with a semi-gloss topcoat" | nº e centralização das teias |
| Slaughter | 5 | 0,01–0,26 | "zebra-stripe pattern with aluminum and chrome paints with various reflectivities... tomato red candy coat" | (não verificado) |
| Damascus Steel | Patina (8) | 0,00–0,50 (faca) | "It has some damascus steel parts." (há kits `_90` e por modelo) | — |
| Ultraviolet | Solid Color (1); Huntsman = Custom Paint (7) | 0,06–0,80 | "individual parts spray-painted solid colors in a black and purple color scheme" | — |
| Night | Solid Color (1) | padrão 0,06–0,80 | "solid colors in a night ops color scheme" | — |
| Blue Steel | Patina (8) | 0,00–1,00 | "It has been cold blued." | — |
| Stained | Patina (8) | 0,00–1,00 | "forced patina using lemon and mustard dripped onto the surface" | — |
| Rust Coat | Patina (8) | faca 0,40–1,00 (só WW/BS) | "the exterior surfaces have rusted" | — |
| Safari Mesh | Spray-Paint (3) | padrão 0,06–0,80 | "spray-painted using mesh fencing and cardboard cutouts as stencils" | — |
| Boreal Forest | Hydrographic (2) | padrão 0,06–0,80 | "forest camouflage hydrographic" | — |
| Scorched | Spray-Paint (3) | padrão 0,06–0,80 | "spray-painted in a sun-dappled pattern" | — |
| Urban Masked | Spray-Paint (3) | padrão 0,06–0,80 | "spray-painted using a tangle of masking tape as a stencil" | — |
| Bright Water | Hydrographic (2) | faca 0,00–0,50 | "painted using a blue camo hydrographic" | — |
| Freehand | 5 | 0,00–0,48 | "painted black and purple, then decorated with a metallic marker" | — |
| Lore | Custom Paint (7) | 0,00–0,65 (alguns modelos até 1,00) | "custom painted with knotwork" — **um kit por modelo de faca** (ex.: `cu_m9_bay_lore`) | — |
| Autotronic | Gunsmith (9) | 0,00–0,85 | "anodized red and uses steel mesh to lighten the weight" — um kit por modelo (ex.: `gs_m9_bay_autotronic`) | — |
| Black Laminate | Gunsmith (9) | 0,00–1,00 | "given a laminate stock" — um kit por modelo (ex.: `cu_m9_bay_stonewash`) | — |

### Inferences
- A "receita" do CS separa **o que é da arma** (regiões paint-by-number, áreas que não recebem acabamento, escala normalizada por tamanho) do **que é do acabamento** (estilo, cores, textura de padrão, faixas) e do **que é do item individual** (índice, semente, float). O MASSACRE já tem a primeira camada (zonas corpo/guarnições/carregador/detalhes/internos). Falta formalizar a segunda (famílias de técnica + textura de padrão + faixas) e a terceira (semente + desgaste por exemplar).
- Os estilos procedurais (degradê sobre cromo, marmorizado, pátina, hidro, spray triplanar, cor sólida) usam **um único kit para todas as facas**. Os estilos ilustrados (Custom/Gunsmith: Lore, Autotronic, Black Laminate) exigem **um kit e uma arte por modelo**. Para uma equipe pequena, famílias procedurais rendem muito mais skins por hora de arte.
- As faixas de float por acabamento funcionam como **ferramenta de direção de arte**. Acabamentos que "estragam feio" (verniz sobre cromo) ficam travados no novo; acabamentos que ficam bonitos gastos (ferrugem) só existem gastos.
- Agrupar vários kits sob um nome, como as "fases", cria **variantes ocultas raras** sem nomes novos. É um mecanismo poderoso de valor, e também de apelo a jogo de azar (ver seção 3).
- Guardar 3 máscaras num único RGB e manter o mapa de rugosidade em 256² ("to conserve memory") são práticas diretamente úteis num jogo de navegador.

### Gaps
- O algoritmo exato que converte semente → offset/rotação (e o intervalo exato: 0–999, 1–1000 ou 0–1000) não é documentado oficialmente; as fontes divergem.
- O estilo 10 (Heat Treated/Rainbow Spoon/Runoff) não consta da doc pública do Workshop; seus parâmetros não foram encontrados.
- Não encontrei parâmetro "pearlescent" no schema do CS2 (busca por "pearl" retornou só nomes de padrão). A doc só mostra o padrão `mother_of_pearl_elite` no exemplo Gunsmith. Se existe um controle de perolização no Item Editor atual, não foi confirmado.
- No CS2, cores e texturas de muitos kits migraram para materiais compostos (`.vcompmat`); o espelho legado do CS:GO com os parâmetros completos (cores de cada fase Doppler etc.) não estava acessível.
- Não confirmei a data de lançamento do estilo Gunsmith (a página do anúncio na Steam não carregou), nem nomes/regras dos padrões de Slaughter.
- O significado dos campos `seed` e `use_legacy_model` dos paint kits não é documentado.

---

## 2. Outros jogos: Valorant, Call of Duty, Rainbow Six Siege, Apex, PUBG, Free Fire, Fortnite, Warframe e a pintura do Rocket League

### Takeaway
Fora do CS, o "valor" de uma skin vem menos de aleatoriedade e mais de **camadas de conteúdo** e **conquista**:
- **Valorant:** tier com preço fixo, níveis pagos com VFX/animação/finalizador e variantes de cor.
- **Call of Duty:** escadas de camuflagens de maestria ganhas por desafios, com o topo animado.
- **PUBG e Free Fire:** skins que evoluem por níveis.
- **Apex e Fortnite:** skins reativas.
- **Warframe e Rocket League:** o jogador escolhe cores por canal, e o acabamento é um atributo separado da cor.

### Cited Findings

#### Valorant (Riot)
- Tiers: Select (SE) 875 VP, Deluxe (DE) 1.275 VP, Premium (PE) 1.775 VP, Ultra (UE) e Exclusive (XE) com preço variável. O ícone de cor do tier indica o preço ("as soon as you see a blue circle you know that a skin will cost 875 VP") — [Riot Support](https://support.riotgames.com/en-us/valorant/store/price-tiers-for-skins-in-valorant)
- Preços arma/corpo a corpo: Select 875/1.750; Deluxe 1.275/2.550; Premium 1.775/3.550; Exclusive 2.175–2.675/4.350–5.350; Ultra 2.475–2.975/4.950–5.950 VP. Melee costuma custar o dobro e todos os melees são classificados como Exclusive — [Valorant Wiki – Weapon Skins](https://valorant.fandom.com/wiki/Weapon_Skins)
- Obtenção: ofertas diárias da loja, bundle em destaque, Night.Market, Battle Pass (13 armas por ato, 3 coleções; no tier 50, sidearm na trilha grátis e melee na premium) e Agent Gear (skins Select no tier 10, com Kingdom Credits) — [Valorant Wiki – Weapon Skins](https://valorant.fandom.com/wiki/Weapon_Skins)
- **Upgrades com Radianite Points (RP):** dão "new VFX, audio, animations, finishers and variants". Custam 10 RP por nível e 15 RP por variante depois do upgrade completo. RP é comprável (1.600 VP → 20 RP; 2.800 → 40; 4.800 → 80) ou ganho no passe — [Valorant Wiki – Radianite Points](https://valorant.fandom.com/wiki/Radianite_Points)
- Estrutura típica de níveis segundo guias (fonte secundária): nível 2 = VFX e sons; nível 3 = animações (recarga, inspeção, disparo); nível 4 = kill banner/áudio e finalizador (animação de abate final). Algumas Premium têm só 2 níveis e outras até 5; skins de tier alto costumam ter 3–4 variantes de cor — [ProSettings](https://www.prosettings.com/valorant-level-up-skins/); [Valobuff](https://valobuff.com/guides/level-up-skins-valorant/)
- **Integridade competitiva:** o patch 12.07 (14/04/2026) padronizou retículos de luneta de skins (Kuronami Marshal, EX.O Marshal, Nocturnum Marshal, Araxys Outlaw, Operator) "to make them more consistent in the center range of view with the base scope reticle" — [Patch Notes 12.07 (oficial)](https://playvalorant.com/en-us/news/game-updates/valorant-patch-notes-12-07/)

#### Call of Duty (Activision) — camuflagens de maestria
- **Black Ops 7 (2025):** 16 camos de maestria, 4 por modo:
  - Multiplayer: Shattered Gold → Arclight → Tempest → Singularity
  - Zombies: Golden Dragon (escamas de dragão douradas) → Bloodstone (gema com brilho vermelho/rosa) → Doomsteel → Infestation
  - Warzone: Golden Damascus → Starglass → Absolute Zero → Apocalypse
  - mais a "Ultra Mastery" Nexus Horizon, que exige completar a maestria de cada modo

  — [esports.gg](https://esports.gg/guides/call-of-duty/all-mastery-camos-in-black-ops-7-multiplayer-zombies-and-campaign/); [Windows Central](https://www.windowscentral.com/gaming/here-are-all-of-the-call-of-duty-black-ops-7-mastery-camos)
- **Black Ops 6 (2024), MP:** Gold → Diamond → Dark Spine → Dark Matter.
  - Gold exige 9 camos militares + 2 especiais e um desafio de "double kills".
  - Diamond exige Gold em N armas da classe e "3 kills without dying 10 times".
  - Dark Spine exige Diamond em várias classes e triple kills.
  - Dark Matter exige Dark Spine nas 33 armas de lançamento e "5 kills without dying, 3 times" em cada.

  — [PC Gamer](https://www.pcgamer.com/games/fps/call-of-duty/black-ops-6-mastery-camo-unlock/); [timesaver.gg](https://timesaver.gg/blog/bo6-dark-matter-camo-unlock-guide). A Dark Matter do BO6 é animada: roxo brilhante com detalhes que lembram galáxias — [Game Rant](https://gamerant.com/call-of-duty-all-mastery-camos/)
- **BO6, outros modos:** Zombies = Mystic Gold → Opal → Afterlife (animada) → Nebula (animada e dinâmica); Warzone = Gold Tiger → King's Ransom → Catalyst → Abyss — [TheGamer](https://www.thegamer.com/cod-bo6-zombies-weapon-camo-challenges-tips/); [PCGamesN](https://www.pcgamesn.com/call-of-duty-black-ops-6/camos)
- **Modern Warfare III (2023):**
  - MP: Gilded → Forged → Priceless (animada; exige 36 Forged) → Interstellar (36 Priceless). Só podem ser aplicadas a armas do MWIII.
  - Zombies: Golden Enigma → Zircon Scale → Serpentinite → Borealis (37 Serpentinite).

  — [PC Gamer](https://www.pcgamer.com/call-of-duty-modern-warfare-3-mastery-camo-challenges/); [Call of Duty blog (oficial, lançamento MWIII)](https://www.callofduty.com/blog/2023/11/call-of-duty-modern-warfare-III-launch-comms-challenges-weapon-camos)
- **Modern Warfare II (2022):** Gold → Platinum → Polyatomic (exige Platinum em 51 armas) → Orion — [GamesRadar](https://www.gamesradar.com/modern-warfare-2-mastery-camos-challenges-unlock-gold-platinum-polyatomic-orion/); [ONE Esports](https://www.oneesports.gg/call-of-duty/unlock-gold-camos-modern-warfare-2/)
- **Histórico:**
  - Modern Warfare (2019): Gold, Platinum, Damascus (aparência de "oil-slick"; exige Platinum em todas as armas) e Obsidian, adicionada em abr/2020 — [GamesRadar](https://www.gamesradar.com/modern-warfare-camos/); [blog Activision](https://blog.activision.com/call-of-duty/2020-04/Become-a-True-Weapon-Master-with-Obsidian-Camo-Now-in-Call-of-Duty-Modern-Warfare)
  - Black Ops Cold War (2020): Gold, Diamond e Dark Matter Ultra — [Dot Esports](https://dotesports.com/call-of-duty/news/how-to-unlock-gold-diamond-and-dark-matter-camos-in-call-of-duty-black-ops-cold-war)
  - Black Ops 4: Dark Matter "evolutiva" — [Game Rant](https://gamerant.com/call-of-duty-all-mastery-camos/)
  - **Conflito:** o mesmo texto do Game Rant atribui Obsidian/Platinum ao MW 2022 e Atomic/Orion ao Vanguard, o que contradiz GamesRadar/ONE Esports (Orion = MWII 2022). Tratar o Game Rant como menos confiável.
- **Retículo e blueprints:** a personalização de retículo e de cor do retículo voltou no BO6 — [esports.gg](https://esports.gg/guides/call-of-duty/how-to-change-your-reticle-and-reticle-color-in-black-ops-6/). Blueprints (armas pré-montadas vendidas em bundles) podem trazer tracers coloridos, efeitos de desmembramento/morte e sons. Os "Mastercraft" têm animações próprias (ex.: tracer de raio e "Lightning Strike Death FX"). Trocar acessórios de um blueprint pode remover detalhes visuais exclusivos — [GamesAtlas](https://www.gamesatlas.com/cod-warzone-2-blueprints/black-ops-6/); [Game8](https://game8.co/games/Call-of-Duty-Black-Ops-6/archives/470935)

#### Rainbow Six Siege (Ubisoft)
- 5 raridades (Common, Uncommon, Rare, Epic, Legendary). As skins podem ser **Universal** ("applied to all current and future weapons"), **Seasonal** ("applied to all weapons available at the release of the skin") ou **exclusivas de uma arma**. Compra com Renown (moeda do jogo) ou Credits (moeda paga), com rotação na loja; o resto sai de Alpha Packs ou ofertas. Exemplos: universais "Cold War-BEL" etc. por 12.500 Renown/300 Credits, "Black" por 25.000 Renown, e a sazonal "Black Ice" (Operation Black Ice) por 720 Credits — [Rainbow Six Wiki – Weapon Skins](https://rainbowsix.fandom.com/wiki/Weapon_Skins_(Siege))
- Charms são universais (servem em qualquer arma), segundo resultados de busca que agregavam [siege.gg](https://siege.gg/news/3198-how-to-get-skins-in-rainbow-six-siege) e o [Rainbow Six Wiki](https://rainbowsix.fandom.com/wiki/Alpha_Packs); a página exata de origem não foi confirmada. Alpha Packs são loot boxes com uniformes, capacetes, charms e skins, obtidas com Renown ou por sorteio após vitória — [Rainbow Six Wiki – Alpha Packs](https://rainbowsix.fandom.com/wiki/Alpha_Packs)
- **Siege X (10/06/2025):** acesso gratuito; o novo sistema de níveis dá Renown, Alpha Packs e operadores — [Business Wire (Ubisoft)](https://www.businesswire.com/news/home/20250605216543/en); [Dexerto](https://www.dexerto.com/rainbow-six/how-to-get-free-alpha-packs-in-rainbow-six-siege-x-3212944/). Houve críticas: Renown ficou mais difícil de acumular, e o bundle "Valkyrie Paragon Elite" custa 5.000 Credits — [Notebookcheck](https://www.notebookcheck.net/Rainbow-Six-Siege-X-is-now-a-free-game-but-introduces-a-50-skin-and-controversial-currency-changes.1039189.0.html)

#### Apex Legends (EA/Respawn)
- Raridades: Common, Rare, Epic, Legendary. Skins mais raras mudam mais a aparência — [Apex Wiki (fandom) – Cosmetic](https://apexlegends.fandom.com/wiki/Cosmetic); [The Spike](https://www.thespike.gg/apex-legends/skins)
- **Skins reativas:** Legendary que mudam durante a partida conforme o desempenho. Até a temporada 21 ficavam nos níveis 100/110 do passe premium; da 22 em diante há ao menos uma por split — [Apex Wiki (wiki.gg) – Reactive Weapon Skin](https://apexlegends.wiki.gg/wiki/Reactive_Weapon_Skin)
- **Apex Packs:** 3 itens por pack. Odds do Rare Pack: 100% Rare ou melhor, 24,8% Epic ou melhor, 7,4% Legendary, 0,045% Heirloom Shards. Garantias: Legendary no pack seguinte após 29 sem Legendary; Heirloom Shards após 499 packs. Duplicatas viram crafting metals (15/30/200/600). Pack a 100 Apex Coins; até 544 packs grátis por nível — [Apex Wiki – Apex Pack](https://apexlegends.wiki.gg/wiki/Apex_Pack)

#### PUBG: Battlegrounds (Krafton) — skins progressivas
- Skins "Progressive/Upgradeable" têm 10 níveis. Os upgrades usam Polymers (obtidos desmontando skins no Workshop; raridade maior rende mais) e Schematics/Blueprints (de "Contraband Crates" e eventos). Cada nível acrescenta elementos (textura de carregador, animações, desenhos de kill-feed, mensagens e efeitos de abate, contadores BATTLESTAT, "forma final"), e os upgrades são irreversíveis. Fontes secundárias — [Game Rant](https://gamerant.com/pubg-what-to-do-with-polymers/); [PlasticRanger](https://plasticranger.com/what-are-polymers-used-for-in-pubg/)

#### Free Fire (Garena) — "Evo Guns"
- Skins evolutivas com Evo Tokens. As antigas vão até o nível 7 (1.450 tokens) e as novas até o 8 (2.150 tokens). Trazem animações, efeitos e anúncios de eliminação e emotes. **Alteram atributos da arma e dão habilidade passiva no nível 6** (ex.: AK47 "Blue Flame Draco" causa dano extra a Gloo Walls). Tokens vêm do "Evo Vault", de eventos e de duplicatas. Fontes secundárias — [BlueStacks](https://www.bluestacks.com/blog/game-guides/garena-free-fire-max/ffm-evo-guns-guide-en.html); [Zonapk](https://www.zonapk.org/evolutionary-weapons/free-fire-evo-gun-guide/)

#### Fortnite (Epic) — Wraps
- Wraps foram introduzidos na Season 7 e mudam a aparência de armas e veículos. Havia 1.168 wraps na atualização v41.30 (08/08/2026). Existem wraps **animados** (o primeiro foi "Magma") e **reativos** (o primeiro foi "Ripe"). Vêm de Battle Pass, Item Shop, packs, Fortnite Crew, desafios, torneios, promoções etc. — [Fortnite Wiki – Wraps](https://fortnite.fandom.com/wiki/Wraps)
- O wrap é escolhido no armário por slot e aplicado à arma ou veículo em uso. Ao largar a arma, o wrap sai e outro jogador aplica o dele — resultado de busca agregando [Fortnite Wiki – Wraps](https://fortnite.fandom.com/wiki/Wraps) e [PCGamesN](https://www.pcgamesn.com/fortnite/wraps-weapon-skins-list). Exemplo de reativo: o "Clucking Mad" muda de rosa pastel para um padrão emplumado amarelo ao atirar — [Sportskeeda](https://www.sportskeeda.com/fortnite/news-fortnite-season-6-how-activate-clucking-mad-wrap-reactive-cammo-in-game)

#### Warframe (Digital Extremes) — cor escolhida pelo jogador por canal
- "Each equipment has six color parts: Primary, Secondary, Tertiary, Accents, and Emissive (affects glowing color on equipment), and Energy (affects glowing colors on Warframe abilities)". Emissive e Energy têm também cor secundária (a Energy secundária exige Forma no item). Paletas "can be purchased in the Market". Armas, companheiros e até a nave são personalizáveis — [WARFRAME Wiki – Warframe Cosmetics](https://wiki.warframe.com/w/Warframe_Cosmetics)
- Com as duas cores de energia/emissivo, a primária cobre a área emissiva mais clara e a secundária a mais escura — [WARFRAME Wiki (resultado de busca)](https://wiki.warframe.com/w/Emissive_Color)

#### Rocket League (Psyonix/Epic) — "painted" (cor) × "paint finish" (acabamento)
- **Painted items** existem desde 20/06/2016. Um item pintado mantém a raridade do item base (com exceções). Há **14 cores**: Black, Burnt Sienna, Cobalt, Crimson, Forest Green, Gold (introduzida na Season 7), Grey, Lime, Orange, Pink, Purple, Saffron, Sky Blue e Titanium White. Nem todo item existe em todas as cores ("some colours may look too similar to the unpainted versions"). Existem 4 cores inobteníveis (Onyx, Platinum, Rose Gold, White Gold). A chance normal de um drop vir pintado é 25% (50% nos fins de semana "Double Painted") — [Rocket League Wiki – Painted Item](https://rocketleague.fandom.com/wiki/Painted_Item)
- **Paint finishes** "add a texture or pattern to paint when equipped" e se organizam por raridade/origem — [Rocket League Wiki – Paint Finish](https://rocketleague.fandom.com/wiki/Paint_Finish):
  - Common (Glossy é o padrão; outros por desafios e DLC): Canvas, Corroded Metal, Glossy, Matte, Metallic, Metallic (Rough), Semigloss, Stainless Steel… — [/Common](https://rocketleague.fandom.com/wiki/Paint_Finish/Common)
  - Uncommon (Item Shop, 100 créditos): Feathered, Grassy — [/Uncommon](https://rocketleague.fandom.com/wiki/Paint_Finish/Uncommon)
  - Rare (Blueprints/Drops): Brushed Metal, Burlap, Camo, Carbon Fiber, Circuit Board, Cookie Dough, Dino, Glossy Block, Knitted Yarn, Moon Rock, Pearlescent (Matte), Stiletto, Sun-Damaged, Toon Glossy, Toon Matte, Toon Sketch, Toon Wood, Wood — [/Rare](https://rocketleague.fandom.com/wiki/Paint_Finish/Rare)
  - Very Rare: Anodized, Anodized Pearl, Metallic (Smooth), Metallic Pearl, Metallic Pearl (Smooth), Pearlescent, Pigskin, Polygrid, Straight-Line — [/Very Rare](https://rocketleague.fandom.com/wiki/Paint_Finish/Very_Rare)
  - Legacy (liberados a quem jogava antes do free-to-play): Brushed Metal, Camo, Canvas, Carbon Fiber, Corroded Metal, Matte, Metallic, Metallic (Rough), Metallic Pearl, Pearlescent, Semigloss, Sun-Damaged, Toon Glossy, Toon Matte, Toon Wood, Wood — [/Legacy](https://rocketleague.fandom.com/wiki/Paint_Finish/Legacy)
  - Import: Furry. Rocket Pass: Metallic Flake, Medallion, Glitter, Obsidian, Stamped Metal, Metallograph, Mako Marks, Dragon Scale, Sludge, Basket, Marble, Hieroglyph, Exo, Sequin… Evento: Zebra — [Paint Finish](https://rocketleague.fandom.com/wiki/Paint_Finish)

### Inferences
- Existem quatro "motores de valor" distintos:
  1. **aleatoriedade/escassez** (CS: float, semente, fases; RL: 25% pintado);
  2. **conteúdo em camadas pago** (Valorant: níveis e variantes; PUBG/Free Fire: evolução);
  3. **conquista visível** (CoD: escadas de maestria, com o topo animado e restrito);
  4. **expressão pessoal** (Warframe: canais de cor; RL: cor × acabamento; CS: adesivos/charms/nome).

  O MASSACRE pode combinar 3 e 4 sem depender de 1 pago (ver seção 3).
- O modelo Rocket League (cor como atributo e acabamento como item separado) é o mais próximo do sistema atual do MASSACRE. A diferença é que o RL não tem **padrões/estampas** por zona, e é isso que o dono do jogo pede agora.
- O modelo Universal/Seasonal do R6 resolve a escala: uma skin procedural "universal" vale para armas futuras sem arte nova, algo natural com mapeamento triplanar ou normalização de escala como no CS.
- Free Fire mostra o risco de skins que mudam atributos (pay-to-win). Riot e Valve tratam cosmético como sem efeito de jogo, e a Riot chega a corrigir retículos de skins.

### Gaps
- A Riot não publica matriz oficial de recursos por tier; a estrutura de níveis veio de guias secundários.
- Não li as páginas oficiais da Activision para BO6/BO7 (usei imprensa). Os detalhes de Vanguard/BO4 são pouco confiáveis e há conflito sobre Orion/Obsidian.
- Não encontrei odds oficiais atuais de Alpha Packs (R6), nem confirmação oficial de mudanças nas Alpha Packs no Siege X além das notícias citadas. Skins de acessórios do R6 não foram verificadas.
- PUBG e Free Fire foram cobertos só com guias secundários; não verifiquei as notas oficiais.
- Não encontrei o preço atual das paletas do Warframe nem o número de cores por paleta.
- Rocket League: não verifiquei se a lista de acabamentos da wiki está completa em 2026 (há páginas de Rocket Pass de temporadas mais novas não lidas).

---

## 3. Personalização × skins fixas, como são mostradas, como são obtidas e a crítica/regulação de loot boxes (inclusive Brasil)

### Takeaway
Os jogos vão da **curadoria total** (CS e Valorant: design fixo; o jogador só escolhe variante, adesivo, charm ou nome) à **personalização por canal** (Warframe; Rocket League com cor + acabamento). A obtenção mistura drops, caixas pagas, passe, desafios de maestria, crafting e compra direta. Loot boxes pagas sofrem pressão crescente:
- estudo associando gasto em caixas a jogo problemático;
- proibição na Bélgica (com fiscalização ineficaz);
- classificação M na Austrália (2024);
- **proibição para jogos acessíveis a crianças/adolescentes no Brasil (Lei 15.211/2025, em vigor desde março de 2026)**;
- processo de Nova York contra a Valve (fev/2026).

### Cited Findings

#### 3.1 Espectro personalização ↔ curadoria
- CS: o design da skin é fixo (paint kit). A personalização vem por adesivos (até 5, com posição livre e raspagem), name tag e charms (posição livre, com semente) — [CS Wiki – Sticker](https://counterstrike.fandom.com/wiki/Sticker); [BLAST.tv](https://blast.tv/cs/news/cs2-the-amory-update); [schema](https://github.com/SteamDatabase/GameTracking-CS2/blob/master/game/csgo/pak01_dir/scripts/items/items_game.txt)
- Valorant: design fixo, mas o jogador escolhe entre variantes (cores) desbloqueadas e níveis — [Valorant Wiki – Radianite Points](https://valorant.fandom.com/wiki/Radianite_Points)
- CoD: camos de design fixo, escolhidas por arma; retículo e cor do retículo configuráveis — [esports.gg](https://esports.gg/guides/call-of-duty/how-to-change-your-reticle-and-reticle-color-in-black-ops-6/)
- Warframe: 6 canais de cor escolhidos pelo jogador a partir de paletas — [WARFRAME Wiki](https://wiki.warframe.com/w/Warframe_Cosmetics)
- Rocket League: cor ("painted") como atributo do item e acabamento escolhido à parte — [RL Wiki – Painted Item](https://rocketleague.fandom.com/wiki/Painted_Item); [RL Wiki – Paint Finish](https://rocketleague.fandom.com/wiki/Paint_Finish)

#### 3.2 Como as skins são mostradas (preview/inspeção)
- No Workshop do CS2, o Item Editor tem botões "Inspect" (mostra o item na interface de inspeção do inventário) e "Preview" ("load into preview map and equip selected econitem") — [Workshop Finishes](https://www.counter-strike.net/workshop/workshopfinishes)
- A Valve pede nas submissões "screenshots of the weapon inspect, in hand, and side view without any post-processing" e valoriza "a finish that is pleasing when held in hand and not just from the side while inspecting" — [CS2 Workshop Styleguide](https://www.counter-strike.net/workshop/workshopstyleguide)
- Float e semente de um item específico são verificados por "inspect links" (ex.: CSFloat) — [SteamAnalyst – Blue Gem](https://www.steamanalyst.com/guides/blue-gem)
- A abertura de caixa do CS é descrita pela Procuradoria de NY como semelhante a "a slot machine, with an animated spinning wheel that eventually rests on a selected item" — [NY AG (press release)](https://ag.ny.gov/press-release/2026/attorney-general-james-sues-game-developer-promoting-illegal-gambling-through)

#### 3.3 Como são obtidas
- **CS:** drops, caixas + chave (US$ 2,49), trade-up (10→1; desde 23/10/2025 também 5 Covert → faca/luva), Steam Market, trocas, Armory Pass (US$ 15,99 = 40 créditos) e tokens souvenir — [CS Wiki – Skins](https://counterstrike.fandom.com/wiki/Skins); [GeekWire](https://www.geekwire.com/2026/valve-software-sued-by-new-york-ag-accused-of-promoting-illegal-gambling-via-video-game-loot-boxes/); [esports.net](https://www.esports.net/wiki/guides/cs2-knives-skin-market-crash/); [BLAST.tv](https://blast.tv/cs/news/cs2-the-amory-update); [CS Wiki – Souvenir](https://counterstrike.fandom.com/wiki/Souvenir)
- **CS, fim das cápsulas de Major (22/05/2026):** a Valve deixou de vender cápsulas aleatórias de adesivos de Major e passou a vender tokens para comprar adesivos específicos (100 tokens = R$ 4,99). A Dust2 relaciona a mudança, sem justificativa oficial da Valve, às pressões regulatórias contra loot boxes — [Dust2 Brasil](https://www.dust2.com.br/noticias/74053/entenda-por-que-valve-nao-vai-vender-mais-capsulas-do-major)
- **Valorant:** compra direta com preço fixo por tier, Night.Market, Battle Pass, Agent Gear — [Valorant Wiki – Weapon Skins](https://valorant.fandom.com/wiki/Weapon_Skins)
- **CoD:** desafios e maestria (grátis) mais blueprints e bundles pagos — [esports.gg](https://esports.gg/guides/call-of-duty/all-mastery-camos-in-black-ops-7-multiplayer-zombies-and-campaign/); [GamesAtlas](https://www.gamesatlas.com/cod-warzone-2-blueprints/black-ops-6/)
- **R6:** loja (Renown ou Credits) e Alpha Packs — [R6 Wiki](https://rainbowsix.fandom.com/wiki/Weapon_Skins_(Siege))
- **Apex:** packs com odds publicadas, pity e crafting de duplicatas — [Apex Wiki – Apex Pack](https://apexlegends.wiki.gg/wiki/Apex_Pack)
- **PUBG:** crates, desmonte → polímeros → upgrades — [Game Rant](https://gamerant.com/pubg-what-to-do-with-polymers/)
- **Fortnite:** passe, loja, desafios — [Fortnite Wiki – Wraps](https://fortnite.fandom.com/wiki/Wraps)
- **Rocket League:** drops/blueprints, loja, Rocket Pass — [RL Wiki – Paint Finish](https://rocketleague.fandom.com/wiki/Paint_Finish)

#### 3.4 Crítica e regulação de loot boxes
- **Evidência empírica:** Zendle & Cairns (2018, PLOS ONE, n = 7.422) encontraram ligação entre o gasto em loot boxes e a gravidade de problemas com jogo de azar. A ligação é mais forte que a encontrada para outras compras dentro do jogo — [PLOS ONE](https://journals.plos.org/plosone/article?id=10.1371%2Fjournal.pone.0206767)
- **China (2017):** passou a exigir a divulgação de probabilidades, e a Valve publicou as odds via Perfect World — [csgoskins.gg](https://csgoskins.gg/blog/csgo-case-odds-the-official-numbers-published-by-valve)
- **Bélgica:** desde 2018 a Comissão de Jogos considera ilegais as loot boxes pagas, mas mais de três anos depois vários jogos de alta receita ainda as tinham ("ineffective" enforcement) — [Xiao, Collabra: Psychology (2023)](https://online.ucpress.edu/collabra/article/9/1/57641/195100/Breaking-Ban-Belgium-s-Ineffective-Gambling-Law). Visão global: [Xiao, "Loot Box State of Play 2023", Gaming Law Review (2024)](https://journals.sagepub.com/doi/10.1089/glr2.2024.0006)
- **Austrália (22/09/2024):** jogos com "in-game purchases with an element of chance" recebem classificação mínima M; jogos com jogo de azar simulado recebem R18+ — [Game Developer](https://www.gamedeveloper.com/business/games-featuring-paid-loot-boxes-will-soon-receive-a-mandatory-m-rating-in-australia); [PCWorld](https://www.pcworld.com/article/2464538/all-games-with-loot-boxes-will-be-rated-m-or-higher-in-australia.html)
- **Brasil — Lei 15.211/2025 ("ECA Digital"/"Lei Felca"):**
  - Sancionada em 17/09/2025, em vigor desde 17/03/2026 — [juridico.ai](https://juridico.ai/blog/juridico/eca-digital-lei-15-211-2025/); [texto no Planalto](https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2025/lei/l15211.htm) (a página deu erro 503 na consulta).
  - O **art. 20** diz: "São vedadas as caixas de recompensa (loot boxes) oferecidas em jogos eletrônicos direcionados a crianças e a adolescentes ou de acesso provável por eles" — [Dust2 Brasil](https://www.dust2.com.br/noticias/71770/lei-felca-comeca-com-indefinicao-sobre-counter-strike); ver também [ConJur](https://www.conjur.com.br/2025-out-15/adultizacao-lei-no-15-211-proibe-caixa-de-recompensas-em-games/) e [Rádio Senado](https://www12.senado.leg.br/radio/1/noticia/2026/03/27/eca-digital-proibe-rolagem-infinita-e-caixa-de-recompensa-em-games-infantojuvenis).
  - A lei também exige mecanismos eficazes de verificação de idade — [juridico.ai](https://juridico.ai/blog/juridico/eca-digital-lei-15-211-2025/)
- **CS2 no Brasil (mar/2026):** o CS2 tem classificação 16+ no Brasil. A Dust2 conseguiu comprar e abrir uma caixa com a conta Steam de um menor, sem nenhuma diferença na transação, e a Valve não respondeu nem anunciou medidas — [Dust2 Brasil](https://www.dust2.com.br/noticias/71770/lei-felca-comeca-com-indefinicao-sobre-counter-strike). A Dust2 cita ainda que Bélgica, Holanda e França têm mecanismos específicos de conformidade — [Dust2 Brasil](https://www.dust2.com.br/noticias/74053/entenda-por-que-valve-nao-vai-vender-mais-capsulas-do-major)
- **Nova York (25/02/2026):** a Procuradoria-Geral processou a Valve por promover jogo de azar ilegal via loot boxes (CS2, TF2, Dota 2). A ação aponta a revenda (cash-out) no Steam Market e em sites de terceiros, um mercado de skins de CS acima de US$ 4,3 bi (mar/2025), uma skin vendida por mais de US$ 1 mi (jun/2024) e o dano a menores. Pede fim das práticas, devolução de lucros e multas — [NY AG](https://ag.ny.gov/press-release/2026/attorney-general-james-sues-game-developer-promoting-illegal-gambling-through). A ação cita a Penal Law §§ 225.05/225.10 e pede multa de "três vezes" o ganho — [Jones Walker](https://www.joneswalker.com/en/insights/blogs/perspectives/new-york-targets-valves-loot-boxes-as-illegal-gambling.html); [GeekWire](https://www.geekwire.com/2026/valve-software-sued-by-new-york-ag-accused-of-promoting-illegal-gambling-via-video-game-loot-boxes/). A Valve compara as caixas a cartas colecionáveis (beisebol/Pokémon) — [GeekWire](https://www.geekwire.com/2026/valve-software-sued-by-new-york-ag-accused-of-promoting-illegal-gambling-via-video-game-loot-boxes/); [Dust2 Brasil (título)](https://www.dust2.com.br/noticias/74009/valve-compara-caixas-de-cs-com-cartas-de-pokemon-em-processo)

### Inferences
- Para um FPS de navegador com público brasileiro (e provavelmente jovem), **caixas pagas com conteúdo aleatório são um risco jurídico direto** pelo art. 20 da Lei 15.211/2025. O caminho mais seguro é: compra direta com preço fixo, desafios/maestria, passe, crafting determinístico e drops grátis sem cash-out.
- Se houver algum sorteio (mesmo grátis): publicar as odds (como a China exigiu), usar pity/garantias (modelo Apex), converter duplicatas em moeda de crafting e **não criar mercado com saída para dinheiro real**, que é o ponto central da ação de NY.
- O movimento da própria Valve (tokens de compra direta no lugar de cápsulas de Major) indica a tendência do setor: manter o colecionismo e trocar o "sorteio pago" por "escolha paga".

### Gaps
- Não consegui ler o texto integral da Lei 15.211/2025 no Planalto (erro 503). A definição legal exata de "caixa de recompensa" e os detalhes do decreto regulamentador (mencionado por veículos em mar/2026) não foram verificados.
- Não verifiquei a situação atual (após mai/2026) da conformidade da Valve no Brasil nem o andamento do processo de NY.
- Holanda, Reino Unido, Espanha e os rótulos PEGI/ESRB não foram pesquisados em profundidade.
- Não encontrei fonte primária sobre como Valorant e Fortnite apresentam o preview na loja (vídeos, "inspect"). Não incluí.

---

## 4. Lições para um sistema original no MASSACRE: o que dá valor, o que se lê bem em 1ª pessoa e à distância, riscos de propriedade intelectual

### Takeaway
Os sinais mais fortes de valor são raridade legível (cor de tier), variação individual (desgaste e semente), conteúdo extra no topo (animação, reatividade, contador de abates) e conquista visível. Para legibilidade, a Valve gradua o **"quanto a skin grita"** conforme a raridade, exige valores de albedo dentro de faixas PBR, protege partes importantes da arte contra desgaste e pede que o desenho "converse" com a geometria da arma. A Riot mantém a mira/retículo neutros. Tudo deve ser original: o caso Howl (Contraband em 2014) mostra o custo de usar arte de terceiros.

### Cited Findings
- **Saliência por raridade (Valve):** Mil-Spec "muted, harder to read at a distance"; Restricted "distinct but not flashy"; Classified "distinct noticeable patterns"; Covert "distinct 'loud' patterns, are recognizable at a distance" — [CS2 Workshop Styleguide](https://www.counter-strike.net/workshop/workshopstyleguide)
- **Primeira pessoa:** é valorizado "creating a finish that is pleasing when held in hand and not just from the side while inspecting" — [Styleguide](https://www.counter-strike.net/workshop/workshopstyleguide)
- **Valores e cor:** evitar cores "either too bright or too dark"; preto puro fica "darker than most of the shadows in game", e cores supersaturadas parecem "a light source" — [Styleguide](https://www.counter-strike.net/workshop/workshopstyleguide). Faixas de albedo: metálicos 180–250 (até ~90), não metálicos 55–220 — [Workshop Finishes](https://www.counter-strike.net/workshop/workshopfinishes)
- **Padrões:** "All patterns should be seamless. Using offset and/or rotation values allow the finish to have more variety"; ilustrações "designed for the weapon, not just slapped on" — [Styleguide](https://www.counter-strike.net/workshop/workshopstyleguide)
- **Desgaste a serviço da leitura:** "Important features of your design should never wear to the substrate"; a máscara de durabilidade no alfa mantém legível o elemento central — [Workshop Finishes](https://www.counter-strike.net/workshop/workshopfinishes)
- **Originalidade e versões:** "All elements of the submission need to be original work (including patterns and textures)"; não incluir versão "low violence" dificulta a seleção — [Styleguide](https://www.counter-strike.net/workshop/workshopstyleguide)
- **Custo de PI:** o M4A4 Howl virou Contraband em 2014 por arte sem permissão, e outras skins do mesmo autor foram removidas — [CS Wiki – Huntsman Weapon Case](https://counterstrike.fandom.com/wiki/Huntsman_Weapon_Case)
- **Clareza competitiva:** a Riot padronizou retículos de skins de luneta (patch 12.07, 2026) — [Valorant Patch Notes 12.07](https://playvalorant.com/en-us/news/game-updates/valorant-patch-notes-12-07/)
- **Raridade de desgaste e padrão gera prêmio:** floats extremos são os mais raros (curva em sino) — [CS Wiki – Skins](https://counterstrike.fandom.com/wiki/Skins). Padrões específicos (fração de azul, % de fade, "Fire & Ice", teias centralizadas) têm prêmios grandes em relação ao mesmo item comum — [cs2floatchecker](https://cs2floatchecker.com/blog/pattern-guide); [SteamAnalyst](https://www.steamanalyst.com/guides/blue-gem)
- **Topo animado/reativo:** Dark Matter e Nebula (BO6) e Priceless (MWIII) são camos animadas — [Game Rant](https://gamerant.com/call-of-duty-all-mastery-camos/); [TheGamer](https://www.thegamer.com/cod-bo6-zombies-weapon-camo-challenges-tips/); [PC Gamer](https://www.pcgamer.com/call-of-duty-modern-warfare-3-mastery-camo-challenges/). Skins/wraps reativos mudam com o desempenho — [Apex Wiki](https://apexlegends.wiki.gg/wiki/Reactive_Weapon_Skin); [Fortnite Wiki](https://fortnite.fandom.com/wiki/Wraps). Valorant cobra por VFX, animações, finalizador e variantes — [Valorant Wiki](https://valorant.fandom.com/wiki/Radianite_Points)
- **Economia é frágil:** mudar a escassez de itens de topo (trade-up de facas, out/2025) derrubou preços em horas — [esports.net](https://www.esports.net/wiki/guides/cs2-knives-skin-market-crash/)
- **Custo de memória:** a Valve mantém o mapa de rugosidade/expoente em 256² por padrão "to conserve memory" — [Workshop Finishes](https://www.counter-strike.net/workshop/workshopfinishes)

### Inferences
Proposta de taxonomia para o MASSACRE, com **nomes originais provisórios em português**. Os nomes são sugestões; convém revisão jurídica antes de fixá-los.

1. **Zonas (já existem):** corpo, guarnições, carregador, detalhes, internos. Equivalem às regiões "paint by number" do CS e aos canais do Warframe. Sugestão: manter "internos" sempre em acabamento de fábrica, como as áreas não pintáveis do CS.
2. **Família de técnica (camada nova, inspirada nas técnicas reais, não nos nomes dos jogos):**
   - "Pintura por peça" (cor sólida por zona);
   - "Película d'água" (hidroimpressão; estampa nas UVs);
   - "Estêncil" (spray triplanar em camadas que se revelam com o desgaste);
   - "Verniz translúcido sobre cromo" (cor única);
   - "Verniz estampado" (padrão + rugosidade variável);
   - "Aerógrafo sobre cromo" (degradê);
   - "Têmpera colorida" / "Oxidação química" (pátina com 4 papéis: metal, tinta nova, tinta envelhecida, sujeira);
   - "Ilustrada" (arte por modelo);
   - "Oficina" (pátina + ilustração).

   Os acabamentos atuais (fosfato, cerakote, fibra de carbono, madeira, polímero texturizado, borracha etc.) viram "materiais-base/substratos" que aparecem quando a pintura gasta.
3. **Padrão:** uma textura RGB = 3 máscaras (ex.: camuflagens, listras, malha, marmorizado, gotas, teia, circuitos, escamas, "fita adesiva"), com escala normalizada por tamanho de arma e faixas de offset/rotação.
4. **Paleta:** 4 cores nomeadas por skin, reaproveitando a paleta nomeada atual. Com N padrões × M paletas × K técnicas, o catálogo cresce combinatoriamente, que é o pedido de "muitas skins com muitas cores e desenhos".
5. **Desgaste:** float 0–1 com 5 faixas de nomes originais e teto/piso por skin (verniz sobre cromo só "novo"; ferrugem só "gasto"). Máscara de durabilidade para proteger logotipos e elementos centrais.
6. **Semente (0–999):** define offset/rotação/"fase". Para a faca estilo M9, "fases" de um marmorizado ou % de degradê dão exemplares únicos sem arte nova. **Não vender a chance de semente rara**: dar a semente ao ganhar o item.
7. **Extras:** contador de abates (nome próprio, não "StatTrak"), gravação de nome, adesivos com raspagem, pingente com semente e física de balanço.
8. **Tiers de raridade** com cores próprias (evitar a sequência exata de cores e nomes do CS) e regra de saliência por tier. No topo, efeitos animados/reativos que não alterem silhueta, mira ou atributos.
9. **Obtenção sem loot box paga** (Lei 15.211/2025): compra direta, "escadas de maestria" por desafios (com nomes próprios, não "Gold/Diamond/Dark Matter"), passe e crafting determinístico com duplicatas → moeda.
10. **Faca (M9-style):** priorizar famílias procedurais metálicas (degradê sobre cromo, marmorizado com fases, têmpera colorida, azulamento a frio, oxidação forçada, aço em camadas) que servem a qualquer modelo futuro. Usar "Ilustrada/Oficina" só para peças de topo com arte dedicada.
11. **Leitura em 1ª pessoa:** desenhar para o que a câmera do viewmodel mostra (lado esquerdo/topo do corpo, guarda-mão, face da lâmina). Manter valores dentro das faixas PBR, sem preto puro nem saturação que "vira luz". Não pintar retículos nem alças de mira.

- Nomes a evitar como nomes de skin (lista não exaustiva): Fade, Doppler, Gamma Doppler, Marble Fade, Tiger Tooth, Case Hardened, Crimson Web, Slaughter, Damascus Steel, Ultraviolet, Blue Steel, Rust Coat, Safari Mesh, Boreal Forest, Scorched, Urban Masked, Bright Water, Freehand, Lore, Autotronic, Black Laminate, Howl, StatTrak, Souvenir, Gold/Diamond/Dark Matter/Dark Spine/Platinum/Damascus/Obsidian/Polyatomic/Orion/Priceless/Interstellar/Borealis/Nebula/Opal/Afterlife/Singularity etc. Termos técnicos genéricos ("anodizado", "cerakote", "hidroimpressão") parecem descrições de técnica, não marcas. Ainda assim, recomenda-se usá-los só como categoria e não como nome do produto.

### Gaps
- Não encontrei estudo acadêmico que meça quais características visuais (animação, reatividade, cor, padrão) mais aumentam a disposição a pagar ou o uso de skins. As conclusões acima vêm de práticas da indústria e de preços de mercado de agregadores.
- Não achei guia oficial da Riot ou da Activision equivalente ao Styleguide da Valve sobre legibilidade de skins em 1ª pessoa.
- Não foi feita análise jurídica de marcas (INPI/USPTO). A lista de nomes a evitar é prudencial, não parecer jurídico.
