# Fontes de texturas e modelos para o Blender

Referência permanente do MASSACRE para achar texturas e modelos prontos de qualidade: os sites, a licença de cada
um conferida na própria página, o que já está baixado na biblioteca local e os candidatos de modelo por arma.
Regras do projeto: `CLAUDE.md`, seção 0.7 ("Texturas CC0 no Blender" e "Modelos CC0 prontos de armas").

- **Levantamento:** 2026-10-03 (subfase 4.1d). Licenças lidas nas páginas de licença dos sites nessa data; reabrir a
  página antes de usar um site novo ou depois de muito tempo, porque licença muda.
- **Decisões do usuário de 2026-10-03:** só **CC0** entra no projeto, tanto textura quanto modelo (o repositório é
  público no GitHub e o navegador entrega qualquer textura do jogo a quem abrir); o modelo pronto passa pela mesma
  régua das armas já feitas (ficha medida, silhueta de lado ≥ 98 %, medidas-chave ±1 %, peças móveis, zonas, LODs) —
  se não passar, a arma é modelada do zero; as texturas ficam numa **biblioteca local fora do git**
  (`S:\biblioteca-texturas\`, o caminho em `tools/blender/local.json` → `bibliotecaTexturas`) e só o que uma arma usar
  é copiado para `tools/blender/texturas/` e registrado no `fontes.json`; os downloads que pedem conta (Blend Swap,
  Sketchfab) são feitos pelo Chrome do usuário, já logado, com a autorização dele arquivo por arquivo.
- **Regra dos direitos (decisão do usuário de 2026-10-03): só ficam as fontes que deixam fazer e vender o jogo sem
  problema de direitos.** Na prática: o arquivo só pode vir da **faixa 1** (seção 2.1) — CC0 conferido em site que
  publica obra própria e assina a licença. Tudo o mais (as faixas 2, 3 e 4) é **só para olhar** como referência
  visual, nunca o arquivo: licenças que proíbem redistribuir (ShareTextures, Textures.com, Poliigon, Fab…) e "CC0" de
  site novo ou de envio livre de usuários, onde alguém pode ter subido obra alheia. Os modelos baixados para estudo
  (a 4.1d é toda modelada do zero) não entram no jogo e nada é copiado da malha deles.
- **Atenção à parte, para vender:** a licença da textura e do modelo não cobre **marca registrada**. A regra 9 já tira
  os logotipos e os nomes de fabricante das peças; os **nomes** de algumas armas são marcas (Glock, Desert Eagle,
  Benelli Nova, FN P90…) — conferir antes do lançamento se o jogo usa o nome genérico (o que o CS faz em parte) ou o
  nome do modelo.
- **Reddit:** pedido pelo usuário, mas **não foi lido** — o domínio está bloqueado em todas as ferramentas do
  assistente (WebFetch, busca e os dois navegadores: "not allowed due to safety restrictions"). A reputação abaixo
  vem de Blender Artists, Polycount, GameDev.tv, fóruns da Epic e artigos, com a fonte marcada. Para trazer o Reddit:
  colar no chat os links ou o texto dos tópicos, e eles entram na seção 7.

## 1. Como usar (o fluxo de uma textura)

1. **Procurar primeiro na biblioteca local** (`S:\biblioteca-texturas\biblioteca.json`, seção 4): já tem metal,
   polímero, borracha, couro, tecido, madeira, imperfeições e HDRI de estúdio em 4K.
2. Se não tiver, **procurar nos sites da faixa 1** (seção 2.1) — o atalho é o **3dassets.one** com o filtro "Public
   Domain Only", que busca em ambientCG, Poly Haven, cgbookcase, TextureCan e outros de uma vez (o resultado só vale se
   o site de origem estiver na faixa 1: o filtro também mostra PBRPX e outros da faixa 2).
3. **Conferir a licença na página da textura** (não só a do site) e baixar para a biblioteca local, com o
   `LICENCA.json` ao lado (site, página, nome, autor, licença com a URL e a data em que foi conferida, resolução, md5 e
   sha256 de cada arquivo) — o roteiro `S:\biblioteca-texturas\baixar_biblioteca.py` (APIs da ambientCG e do Poly
   Haven) faz isso; o TextureCan recusa script e vai pelo navegador.
4. Quando uma arma usar a textura: copiar os mapas usados para `tools/blender/texturas/<id>/`, registrar em
   `tools/blender/texturas/fontes.json` (o `texturas.py` recusa textura fora do registro, sem CC0 ou com o md5
   diferente) e dizer na ficha do material qual usou e por quê.
5. **Nunca** commitar arquivo de site das faixas 3 e 4 (seção 2): servem só para comparar e achar a referência.

## 2. Sites de texturas

### 2.1 Faixa 1 — PODE USAR: CC0 conferido, em site que publica obra própria (pode ir para o jogo vendido e para o repositório)

| Site | Endereço | Licença (página onde foi conferida) | Conteúdo | Grátis até | Conta | Reputação (fonte) |
|---|---|---|---|---|---|---|
| **Poly Haven** | https://polyhaven.com/textures | CC0 1.0 — https://polyhaven.com/license (proíbe só raspar o site sem permissão; a API é liberada) | 864 texturas PBR escaneadas e procedurais, 997 HDRIs (96 de estúdio), modelos; metal fraco (25, quase tudo ferrugem) | 8K–16K, JPG/PNG/EXR | não | "Padrão ouro" (craftpbr); "meu favorito" (Blender Artists); tópico do GameDev.tv |
| **ambientCG** | https://ambientcg.com | CC0 1.0 — https://docs.ambientcg.com/license/ ("pode incluir os arquivos crus no projeto, por exemplo um jogo") | ~2,9 mil: Metal 101, Couro 50, Tecido 87, Plástico 25, Borracha 4, Fingerprints 9, Scratches 5, Surface Imperfections 20, HDRIs 429 (céu) | 8K (alguns antigos 4K) | não | "Maior biblioteca", "reserva do Poly Haven" (Blender Artists); mantido por uma pessoa (Lennart Demes) |
| **cgbookcase** | https://www.cgbookcase.com/textures | CC0 na página de cada textura (não há página de licença separada; `/license` dá 404) | 566 texturas: metal, couro, tecido, imperfeições; mapas metal/rough e "channel-packed" | 1K–4K (alguns 6K/8K) | não | Favorito em lista do Blender Artists; um artista (Dorian Zgraggen) |
| **TextureCan** | https://www.texturecan.com | CC0 1.0 — https://www.texturecan.com/terms/ ("pode ser redistribuída junto dos seus projetos") | 650+ PBR, com **grip de arma** (Plastic 0016, 0020), alumínio escovado/arranhado, couro; ZIP + SBSAR | 4K | não | "Mínimo 4K, estilizadas" (Blender Artists); recusa download por script (usar o navegador) |
| **3D Textures** | https://3dtextures.me | CC0 — https://3dtextures.me/about/ (só não pode se declarar autor) | 1.300+ PBR; série de nylon/malha, scratches, sci-fi | **1K grátis**; 4K e SBSAR no Patreon | não | "Forte em sci-fi" (craftpbr) |
| **OpenHDRI** | https://openhdri.org | CC0 — https://openhdri.org/license | 60+ HDRIs EXR 32 bits, **12 de estúdio** (Big Studio 01–04, Fly Studio 01–05, Studio 2nd Floor) | até 29K | não | Novo (out/2025), noticiado por CGChannel e DigitalProduction |
| **Free Stock Textures** | https://freestocktextures.com | CC0 — https://freestocktextures.com/license/ | Fotos (grunge, metal, madeira), sem mapas PBR | alta | não | Base 2D para máscaras |
### 2.2 Faixa 2 — NÃO usar o arquivo: "CC0" declarado por site novo, de envio livre ou não conferido na fonte

Pela regra dos direitos (topo), só para olhar: a licença pode estar certa, mas não há como garantir que quem publicou
era dono da obra.

| Site | Endereço | O que diz | Cuidado |
|---|---|---|---|
| **Texture Ninja** | https://texture.ninja | CC0 — conferido só por CGChannel (2018) e BlenderNation; o site não renderizou | 5.000+ fotos de referência, sem PBR; licença não lida na fonte |
| **PolyScan** | https://polyscann.com (dois "n") | CC0 — `/about`; 182 texturas de fotogrametria própria em 8K/4K, com **decals**; 32 modelos | Site novo (tópico no Blender Artists sem consenso ainda) |
| **LazyTextures** | https://www.lazytextures.com | CC0 — `/CC0`; PBR, HDRIs, modelos até 4K | Novo, sem reputação |
| **3DTexel** | https://3dtexel.com | CC0 só na biblioteca "handmade" (`/about`, `/decals`); 286 decals com alfa (impactos de bala, rachaduras, manchas) | 141 dos decals são de IA da comunidade, licença pouco clara: só os 145 feitos à mão |
| **PBRPX** | https://pbrpx.com | CC0 declarado; texturas, HDRI, modelos | Equipe pequena, sem reputação |
| **AMD GPUOpen MaterialX** | https://matlib.gpuopen.com | Apache 2.0 (materiais da AMD) e CC0/MIT (contribuições), por CGChannel 2021 | Não é CC0 puro: manter o aviso Apache; o site é JS e não abriu |
| **Kenney** | https://kenney.nl | CC0 — `/support` (o logo do estúdio é reservado) | Estilizado/protótipo, não fotorrealista |
| **Pixar One Twenty Eight** | https://renderman.pixar.com/pixar-one-twenty-eight | **CC BY 4.0** (crédito a Dylan Sisson e Leif Pedersen) | **Fora** pela regra "só CC0" |

### 2.3 Faixa 3 — NÃO usar o arquivo: licença por item, de envio livre

| Site | Endereço | Regra |
|---|---|---|
| **Blendkit** (antigo BlenderKit; blenderkit.com redireciona) | https://www.blendkit.com | Dois tipos por asset (`/docs/licenses/`): **CC0** e **Royalty Free** (proíbe redistribuir o asset na mesma forma). Os CC0 são de envio livre de usuários, então ficam fora pela regra dos direitos. Ex.: "Anodised Aluminium" é Royalty Free |

### 2.4 Faixa 4 — NÃO usar o arquivo: a licença proíbe redistribuir (só olhar como referência)

| Site | Endereço | O que proíbe |
|---|---|---|
| **ShareTextures** | https://www.sharetextures.com | Licença "tipo CC0": redistribuir em sites/plugins/coleções sem permissão escrita, download automatizado e hotlink |
| **Textures.com** | https://www.textures.com | Distribuir o conteúdo sozinho ou em pacote, juntar a engines/plugins, liberar sob licença open source (Termos rev. 3-8, dez/2020; a versão atual não abriu); créditos grátis acabaram (GameDev.tv, dez/2023) |
| **Poliigon (grátis)** | https://www.poliigon.com/free | Compartilhar, revender, redistribuir ou reempacotar — embutir/assar conta como redistribuição |
| **Fab / Quixel Megascans** | https://www.fab.com | Standard License: redistribuir isolado (o grátis ilimitado do Megascans acabou no fim de 2024) |
| **Adobe Substance 3D Assets** | https://substance3d.adobe.com/assets | Distribuir cópia sem modificação (resumo por busca; o PDF não abriu) |
| **CGAxis (free)** | https://cgaxis.com/free/ | Compartilhar o PBR na forma baixada; usar como biblioteca dentro de app |
| **Texturelabs** | https://texturelabs.org | Redistribuir, mesmo de graça — mas é o **melhor grunge para máscaras**: usar local e pintar a nossa versão |
| **Texturelib** | https://www.texturelib.com | Distribuir as imagens sozinhas ou em pacote |
| **AiTextured** | https://aitextured.com | Redistribuir, espelhar, baixar em massa, treinar IA |
| **FreePBR** | https://freepbr.com | Comercial só no pacote pago (grátis = uso pessoal, por artigos) |
| **Architextures** | https://architextures.org | Comercial exige Pro (trecho de busca) |
| **GameTextures**, **Raw Catalog**, **HDRMaps**, **Pixel Furnace**, **Texture Box** | — | Licença paga, "All Rights Reserved" ou sem texto formal. O Raw Catalog tem o único "Steel Parkerized" e "Nylon Strap Webbing" achados — só referência |
| **NoEmotion HDRs** | https://noemotionhdrs.net | CC BY-ND 4.0 (sem modificação, com crédito): fora |

### 2.5 Alertas

- **Blendermada** (blendermada.com): era banco CC0 de materiais; em 2026-10-03 responde com spam de jogos de azar —
  domínio sequestrado. **Não visitar.** Listas antigas (awesome-blender) ainda o citam.
- **cc0-textures.com**: rotula como CC0 texturas do ShareTextures (que proíbe isso). Não confiar na etiqueta.
- **Mixos** (mixos.io): espelho de ambientCG + Poly Haven + IA. Usar a fonte original.
- **3dprintermarket.co.uk**: diz "CC0, 4K" sem dizer a origem.
- **JSplacement** está fora do ar (o substituto é o add-on **BPYplacement**); o **Quixel Mixer** foi descontinuado em
  fev/2026; o add-on oficial do **Poly Haven é pago** (a API é grátis).

## 3. Recorte para armas e luvas (IDs CC0)

Notação: `ACG:Metal027` = https://ambientcg.com/view?id=Metal027 · `PH:x` = https://polyhaven.com/a/x ·
`CGB:x` = https://www.cgbookcase.com/textures/x · `TC:n` = https://www.texturecan.com/details/n/.
**Negrito** = já está na biblioteca local (seção 4).

**Lacuna:** nenhuma biblioteca CC0 tem acabamento de arma de verdade — a API da ambientCG deu zero para anodized,
parkerized, phosphate, cerakote, gunmetal, blued, knurled e stipple. Fosfatizado, parkerizado e cerakote saem dos
nossos nós procedurais sobre um preto em pó (Metal027–029), com a variação de rugosidade, os arranhões e as digitais
por cima; cromo espelhado é metallic 1 com rugosidade baixa, sem textura.

| Uso | Texturas CC0 |
|---|---|
| Preto fosco / pintura em pó (base do fosfatizado e do cerakote) | **ACG:Metal027, 028, 029**, **ACG:Metal046A** (preto limpo), ACG:Metal046B (sujo), CGB:scratched-painted-metal-01, CGB:painted-metal-01, PH:blue_metal_plate, TC:508 |
| Aço escovado | **ACG:Metal009, Metal012**, ACG:Metal010, Metal011, ACG:MetalPlates001–003, CGB:brushed-iron-02, CGB:brushed-metal-tiles-01 |
| Alumínio / base do anodizado | **ACG:Metal050B** (arranhado), **ACG:Metal051A** (escovado circular), ACG:Metal050A/050C, 051B/051C, TC:76, TC:475, TC:539, TC:502 |
| Aço escuro polido (perto do oxidado) | **ACG:Metal063** (2026-03-30, 8K) |
| Aço riscado | **ACG:Metal038**, ACG:Metal037, Metal039 |
| Prata limpo | **ACG:Metal049A**, ACG:Metal032 |
| Oxidado / envelhecido | PH:rust_coarse_01, PH:metal_plate_02, PH:rusty_metal_03–05, ACG:Metal053C, Metal056A–C, CGB:battered-metal-01 |
| Grip de polímero (losangos, antiderrapante) | **TC:387 (Plastic 0016)**, **TC:460 (Plastic 0020)** |
| Polímero liso / riscado | **ACG:Plastic006** (preto brilhante), **Plastic012A**, **Plastic012B** (riscado), **Plastic018B** (cinza sujo); 3dtextures "plastic-001 w/ speckles and fingerprints" (1K) |
| Borracha (soleira, almofada) | **ACG:Rubber004**, ACG:Rubber001–003, TC:381 |
| Couro preto (luvas) | **ACG:Leather026, Leather032**, ACG:Leather027, 031, 034C, CGB:black-leather-01/02, TC:501, TC:455, TC:404, **PH:fabric_leather_02**, PH:fabric_leather_01, PH:brown_leather |
| Neoprene / tecido sintético (luvas) | **PH:scuba_suede**, **PH:bi_stretch**, PH:terlenka; 3dtextures nylon-weave-001, fabric-nylon-001/002, fabric-mesh-003, nylon-ribbon-001 (1K) |
| Fibra de carbono | **ACG:Fabric004** |
| Madeira de coronha | **PH:walnut_veneer**, **PH:black_walnut_veneer_01**, PH:walnut_veneer_02, black_walnut_veneer_02/03, smoked_walnut_veneer, dark_wood, lacquered_cherry_wood, PH:cherry_veneer (já no projeto) |
| Arranhões | **ACG:Scratches001, 003, 005**, ACG:Scratches002/004; 3dtextures surface-imperfections-scratches-001, metal-scratched-009 (1K) |
| Impressões digitais | **ACG:Fingerprints002, 005, 008**, ACG:Fingerprints001–009, CGB:fingerprints-01/06/07 |
| Manchas, poeira, sujeira | **ACG:SurfaceImperfections003, 013, 016, 018**, ACG:SurfaceImperfections001–020; 3dtextures dust-fibers-001 |
| Decals | Nenhum da faixa 1 serve (a ambientCG só tem marcação de rua; 3DTexel e PolyScan são faixa 2: só olhar); marcas de arma (número de série, gravação) se geram no Blender (regra 9: sem logotipo) |

**Lacuna sem CC0:** cordura/ripstop/nylon balístico em boa resolução (só os 1K do 3dtextures) e parkerizado de verdade.

## 4. A biblioteca local (`S:\biblioteca-texturas\`)

Fora do git, no S: (o C: estava com 99 % ocupado). Baixada em 2026-10-03 com a autorização do usuário: **38
conjuntos, 3,05 GB, 4K**, cada pasta com o seu `LICENCA.json` (md5 e sha256 conferidos depois do download, nenhum
erro). Índice: `biblioteca.json`. Estrutura: `ambientcg/<id>/`, `polyhaven/<id>/`, `texturecan/<id>/`.

| Grupo | Conjuntos (site) |
|---|---|
| Metal (ambientCG, 4K-JPG) | Metal027, Metal028, Metal029, Metal046A, Metal009, Metal012, Metal050B, Metal051A, Metal063, Metal038, Metal049A |
| Polímero e borracha | ambientCG Plastic006, Plastic012A, Plastic012B, Plastic018B, Rubber004 (4K-JPG); TextureCan plastic_0016 e plastic_0020 (4K; os 6 arquivos-lixo `._*` do macOS do ZIP da 0016 foram apagados) |
| Imperfeições (ambientCG, 4K-JPG) | Scratches001, 003, 005; Fingerprints002, 005, 008; SurfaceImperfections003, 013, 016, 018 |
| Luvas e madeira | ambientCG Leather026, Leather032, Fabric004 (4K-JPG); Poly Haven fabric_leather_02 (Rob Tuytel), scuba_suede e bi_stretch (colormass, Rico Cilliers), walnut_veneer e black_walnut_veneer_01 (Jenelle van Heerden) — 4K JPG, sem o `nor_dx` |
| HDRI de estúdio (Poly Haven) | studio_small_08, studio_small_09 (Sergej Majboroda), 4K `.hdr` |

Para baixar mais: `S:\biblioteca-texturas\baixar_biblioteca.py` — acrescentar os IDs nas listas `AMBIENTCG`,
`POLYHAVEN` ou `POLYHAVEN_HDRI` e rodar `python -u baixar_biblioteca.py` (Python 3.7+; ambientCG pela API v2 `full_json` → `fullDownloadPath` do `4K-JPG`; Poly
Haven por `api.polyhaven.com/files/<id>` com User-Agent próprio; sequencial, com pausa, porque a ambientCG é de uma
pessoa só). Pula o que já tem `LICENCA.json`.

## 5. Ferramentas e catálogos

| Ferramenta | Licença / preço | Uso |
|---|---|---|
| **3dassets.one** (criado pela ambientCG; textures.one redireciona) | grátis | Busca em 8+ fontes com filtro "Public Domain Only" — o melhor ponto de partida |
| **CC0 Asset Index** — https://github.com/xiaoqianran/Blender-cc0-asset-index | grátis | ~2.500 assets CC0 com a CLI `cc0a` e o `LICENSE.json`; hoje só Poly Haven, Kenney e Quaternius |
| API do **Poly Haven** — `api.polyhaven.com` | grátis | `/files/<id>`, `/info/<id>`; arquivos em `dl.polyhaven.org/file/ph-assets/Textures/<fmt>/<res>/<id>/…`; User-Agent próprio |
| API v2 da **ambientCG** — `ambientcg.com/api/v2/full_json` | grátis | `type` (Material, HDRI, Decal…), `include=downloadData`, ZIP em `ambientcg.com/get?file=<id>_<res>-<fmt>.zip` |
| **AmbientCG Material Importer** | GPL-3+, grátis (Blender 4.2+) | Importa no Blender com cache local |
| **Poly Haven Asset Browser** | pago (US$ 5/mês ou US$ 49) | Desnecessário: a API faz o mesmo |
| **Material Maker** | MIT | Gerador procedural (exporta para o Blender) — o caminho para fosfatizado/cerakote próprios |
| **BPYplacement** | grátis (Gumroad) | Painéis/greebles com normal map dentro do Blender (substitui o JSplacement) |
| **Materialize** | GPL-3.0 | Gera normal/height/AO a partir de foto (parado) |
| **ArmorPaint** | fonte aberta, binário pago | Pintura 3D PBR (compilar do fonte) |
| Listas: **awesome-cc0** (github.com/madjin/awesome-cc0), **awesome-blender** (cuidado: ainda lista o Blendermada) | — | Descobrir sites novos |

## 6. Modelos prontos de armas (CC0)

Regra (CLAUDE.md 0.7, decisões de 2026-10-01 e 2026-10-03): só **CC0 conferido na página do modelo**; o modelo é ponto
de partida e passa pela mesma ficha e validação; pela regra dos direitos (topo), quase todo modelo CC0 é de **envio
livre de usuários** — usado como **base** (malha que vai para o jogo), ele precisa de uma conferência a mais da origem
(o autor modelou? outros envios dele, a data, a busca reversa da imagem, a contagem de faces contra os modelos de jogo
conhecidos); usado só como **referência** de estudo, não há direito em jogo; **nada extraído de jogo** (CS2/CS:GO, CoD, Battlefield, PUBG,
Insurgency, Valorant…), mesmo que a página diga CC; o `.blend`/`.glb` vai para `tools/blender/modelos/<arma>/` com o
registro em `tools/blender/modelos/fontes.json` (página, autor, licença, data, versão do Blender, md5).

### 6.1 Onde procurar

| Site | Endereço | Como achar CC0 | Observação |
|---|---|---|---|
| **Blend Swap** | https://blendswap.com/3d/weapons | Filtro do próprio site: **https://blendswap.com/3d/weapons?license=CC-0** (páginas `/3d/weapons/<n>?license=CC-0`); o cartão mostra a licença, a versão do Blender, curtidas e downloads | Varredura completa de 2026-10-03: **2.020 armas, 556 CC-0** (24 páginas). Download pede conta; a maioria é de 2010–2018. Os CC0 de qualidade recente são poucos — os do **LonesomeDucky** (Blender 3.0: Weathered AKM rifle /blend/31806, Detective Special Revolver /31805, Weathered Rifle Scope /31807) e do **Britdawgmasterfunk** (Remington 870 /30712, M2 .50cal /30289, Firearms_kit /28872). Na primeira página da listagem geral, os bons Mauser C96 (/31788), Beretta M9 (/31031), SIG-MPX (/31428) e "shotgun" do amaryase (/30594) são **CC-BY** (fora) |
| **Sketchfab** | https://sketchfab.com | API `api.sketchfab.com/v3/search?type=models&downloadable=true&q=…` e o campo `license` | CC0 de arma é só peça de museu (fotogrametria histórica); títulos com "(CC0)" às vezes estão com a etiqueta **CC-BY** — vale a etiqueta, não o título. Download pede conta |
| **OpenGameArt** | https://opengameart.org (coleção "CC0 – 3D Weapons") | Licença por página | Baixa sem conta |
| **Poly Pizza** | https://poly.pizza | CC0 por modelo (Quaternius, Pichuliru, CreativeTrio) | Estilizado low-poly |
| **itch.io** | ex.: https://stein-indie.itch.io/classic-weapons-pack | Licença na página do pack | **Stein Games**: realista, PBR 2K, CC0 (dez/2025) |
| **Poly Haven** | https://polyhaven.com/models | CC0 | PBR de verdade, mas só rifle bolt-action, pistola de serviço e granada de cabo |
| **Blendkit** | https://www.blendkit.com | Só os marcados CC0 | Royalty Free fica fora |
| **Kenney** | https://kenney.nl | CC0 | Estilizado |
| Fora: **CGTrader**, **TurboSquid**, **Free3D**, **Fab** | — | "Royalty Free"/"Standard"/uso pessoal | Proíbem redistribuir o arquivo |
| Fora: **open3dmodel** | https://open3dmodel.com/pt/3d-models/blender-gun | Licença na página de cada modelo | Conferido em 2026-10-03: **os 32 modelos da categoria são "Uso pessoal ou educacional"** (a AWM /accuracy-awm-rifle-gun_361349 também); agregador de "conteúdo contribuído pelo usuário", com descrições automáticas e "9.900 triângulos" em todos (metadado falso). Só consulta |

Peças úteis CC0 que não são armas inteiras: **Bullet Library with 360 different rounds** (WayneC2e, https://blendswap.com/blend/31675, 49 MB) — 95 projéteis e os estojos do calibre .17 ao .460 Weatherby, medidos no manual Hornady de 1973 (escala 1 bu = 1 polegada): serve às cápsulas da AK (7,62×39), da M4 (.223) e da Glock (9 mm), mas **não** tem o .338 Lapua (1989) da AWP, o 5,7×28 (1990) da P90 nem cartucho de espingarda; **12 Gauge Shells Cycles** (CopperStache, /blend/5142); **Weathered Rifle Scope** (LonesomeDucky, /blend/31807) — luneta curta de caça, não a Schmidt & Bender 5–25×56 da AWM.

### 6.2 AWP, Nova e P90 (subfase 4.1d)

Pesquisa dedicada de 2026-10-03 (Sketchfab pela API com `license=cc0`, Blend Swap, OpenGameArt, Poly Haven,
Blendkit, Poly Pizza, Quaternius, itch.io). Licença CC0 conferida na página de cada um. As três prévias marcadas com
"vista" foram olhadas no navegador; as outras notas vêm de metadados.

**AWP** (a do CS é a Accuracy International AWM; a L96A1 é a antecessora):

| Modelo | Endereço | Autor | Blender / tamanho | Nota | Avaliação |
|---|---|---|---|---|---|
| Marui L96 AWS Sniper Rifle | https://blendswap.com/blend/8803 | nokkaew | 2.6x Cycles, 612 KB | 3 | **Vista:** detalhe médio de 2012, coronha verde e luneta; é a réplica airsoft da **L96A1**, não da AWM (ferrolho, coronha e carregador diferentes). Referência de proporção |
| L96AW | https://blendswap.com/blend/2980 | willool | 2.4x, 491 KB | 3 | A versão 2.6x do mesmo autor é CC-BY (fora) |
| AWP Magnum Sniper Rifle | https://blendswap.com/blend/5793 | riddif999 | 357 KB | 2 | Silhueta AI AW reconhecível, mas simples; o nome do CS pede cuidado com a origem |
| Aw50f | https://blendswap.com/blend/2984 | willool | 136 KB | 2 | Variante AW50 |
| Bolt Action Rifle 7.62 | https://polyhaven.com/a/bolt_action_rifle_7_62 | Mateusz Sadek | 19.985 tris, PBR 8K | 2 | Qualidade AAA, mas é um fuzil antigo de madeira: só referência de ferrolho e material |
| Firearms_kit_1.0 | https://blendswap.com/blend/28872 | Britdawgmasterfunk | kit modular | 2 | Miras e carregadores para kitbash |
| L96A1 | https://blendswap.com/blend/2668 | ColbyHep55 | <7.000 faces | — | **Evitar:** o autor diz "from Call Of Duty Black Ops" |

**Nova** (Benelli Nova: receptor e coronha num bloco só de polímero) — **não existe Nova CC0**:

| Modelo | Endereço | Autor | Blender / tamanho | Nota | Avaliação |
|---|---|---|---|---|---|
| Remington 870 shotgun | https://blendswap.com/blend/30712 | Britdawgmasterfunk | 3.0x Cycles, 65,8 MB | 4 como modelo, 2 como Nova | **Vista:** o único hard surface sério das três (2022, duas configurações com punho de pistola, desgaste); é **outra espingarda** — referência do mecanismo de bomba, do cano, do tubo do carregador e da cápsula. No Sketchfab o mesmo modelo está com a etiqueta CC-BY: vale o CC0 do Blend Swap |
| Benelli M1 | https://opengameart.org/content/benelli-m1 | Jean PFP | 716 KB, sem textura | 3 | Estética Benelli, mas semiautomática |
| Lightning Pump Action Rifle | https://opengameart.org/content/lightning-pump-action-rifle | LonesomeDucky | 3.058 tris, PBR 2K, bomba animada | 3 | Arma errada (Colt de faroeste): só o mecanismo |
| Shotgun (Remington 870) / Remington 870 | https://opengameart.org/content/shotgun-1 ; https://blendswap.com/blend/13928 | MikeMoon, Mateus77 | <300 KB | 2 | Simples |

**P90** (FN P90):

| Modelo | Endereço | Autor | Blender / tamanho | Nota | Avaliação |
|---|---|---|---|---|---|
| FN P90 | https://blendswap.com/blend/3380 | LeCube | 2.5x Blender Internal, 245 KB (Staff Pick) | 3 | **Vista:** silhueta certa, superfície mole e "derretida", com mira, lanterna, trilho e supressor pregados; muito abaixo da AK/M4A4. Vale a **forma 3D** do corpo curvo (vistas de cima e de frente), a parte difícil de medir em foto de lado |
| Fn-P90 Low Poly Model | https://blendswap.com/blend/7099 | arshith007 | 2.680 faces, sem UV | 2 | Só silhueta |
| P90 Retextured | https://blendswap.com/blend/8569 | izuzf | 5 MB | — | **Evitar:** derivado do P90 do Fluppy393, de licença desconhecida |
| P90 gerados por IA (meshy.ai) | — | — | — | — | **Evitar:** todos de IA, um chamado "MW2_P90" |

**Extraídos de jogo (fora):** 20 AWPs no Sketchfab com a mesma contagem de faces do CS:GO (21.916) ou do CS2 (39.769);
P90 do CS:GO com 15.907 faces; AWM do PUBG e do Free Fire; o "Shotgun - NOVA" do beerusu798 (o mesmo autor tem um
"AWP_CS2").

**Fora só pela licença (CC-BY, para saber que existe):** AWM — L115A3 do Mortavex (195 mil faces, 2026, o mais
detalhado achado), AWM do Rafael_Oliveira; Nova — Low Poly Benelli Nova (yeepotato10), Benelli M3 Tactical (Amapsis);
P90 — Modular P90 Tactical (doomsentinel), FN PS90 (viktor_colpaert). MKoegler3D é CC-BY-NC; os do Blendkit são
Royalty Free.

**Conclusão e decisão do usuário (2026-10-03):** nenhuma das três tem base CC0 que passe na régua (silhueta ≥ 98 % da
arma certa, detalhe da AK), mesmo depois da varredura das 2.020 armas do Blend Swap e do open3dmodel — **as três são
modeladas do zero pelos nossos scripts**, como as da 4.1c. Para estudo, fora do git, em `S:\biblioteca-modelos\`: a
P90 do LeCube (/blend/3380, a forma 3D do corpo), a L96 AWS do nokkaew (/blend/8803, proporção), a Remington 870 do
Britdawgmasterfunk (/blend/30712, o mecanismo de bomba) e o Low Quality Weapon Pack do Knife (/blend/19742: 24 armas de
baixa qualidade, com imagens de fundo em vez de textura, para proporções e silhuetas — escolhido pelo usuário no lugar
da Weathered Rifle Scope do LonesomeDucky, /blend/31807, que ficou de fora) — **baixadas em 2026-10-03** pelo Chrome do
usuário, logado no Blend Swap (o site dá 5 downloads por dia; a página de download tem uma contagem de 1 s antes do
botão e, às vezes, uma verificação da Cloudflare que passa sozinha), com a licença CC0 conferida na página e no arquivo
de licença de cada download. Ficam em `S:\biblioteca-modelos\blendswap\<id>\` com o zip original, os arquivos e o
`LICENCA.json` (página, autor, licença, data, md5 e sha256), e o índice em `S:\biblioteca-modelos\biblioteca.json`;
nada da malha delas vai para o jogo.

### 6.3 As outras armas do arsenal

Notas de 1 a 5 pelos metadados (o modelo não foi aberto): 4 = boa base com ajustes; 3 = referência de forma e
proporção; 2 = só silhueta. Endereços do Blend Swap no formato `https://blendswap.com/blend/<id>`.

| Arma | Melhor CC0 achado | Site / endereço | Autor | Nota |
|---|---|---|---|---|
| USP-S | "USP" do Low Quality Weapon Pack + silenciador "Suppressor" (Pichuliru, https://poly.pizza/m/VLiLj3j1tS) | Blend Swap /blend/19742 | Knife | 2 |
| P250 | Sig Sauer P-220 (não é a P250) | Blend Swap /blend/8988 | et1337 | 2 |
| Five-SeveN | **nenhum** | — | — | — |
| Desert Eagle | Desert Eagle (textured + rigged; conferir se é obra original) | https://opengameart.org/content/desert-eagle-0 | SirDraco65 | 3 |
| MAC-10 | Free Classic Weapons Pack (também AK, MP5, M700, 1911, Tec-9, M14) | https://stein-indie.itch.io/classic-weapons-pack | Stein Games | 4 (provisório) |
| MP9 | **nenhum** | — | — | — |
| UMP-45 | UMP 45. (topologia ruim, admitida) / UMP45 (parece G36C) | Blend Swap /blend/2691, /blend/6426 | ColbyHep55, mattface | 2 |
| XM1014 | Benelli M1 (antecessor do M4) | https://opengameart.org/content/benelli-m1 | Jean PFP | 3 |
| Galil AR | galil ace (é ACE, não ARM) | Blend Swap /blend/22148 | DanielB247 | 2 |
| FAMAS | GIAT FAMAS | Blend Swap /blend/3731 | Knife | 2 |
| M4A1-S | Cycles-Ready M4 Carbine / M4A1 | Blend Swap /blend/5331, /blend/11042 | karkan010, willool | 3 |
| AUG | AUG A3 | Blend Swap /blend/21376 | robertotulalan | 3 |
| SG 553 | **nenhum** | — | — | — |
| SSG 08 | só substitutos: Bolt Action Rifle 7.62 (PH, 8K) e M700 (Stein Games) | https://polyhaven.com/a/bolt_action_rifle_7_62 | Mateusz Sadek | 3 |
| SCAR-20 | Scar-h remastered (peças separadas) / Scar-H 2.0 | Blend Swap /blend/21634, /blend/2665 | —, ColbyHep55 | 3 |
| G3SG1 | G3A3 do pack Various Small Arms (CC0 desde 15/12/2023) / H&K PSG1 | https://opengameart.org/content/various-small-arms-assault-rifles-sniper-pistol ; Blend Swap /blend/5012 | Tabasco, Daniel74 | 3 / 2 |
| Negev | **nenhum** | — | — | — |
| M249 | **nenhum** (o "Machine Gun" CC0 do OpenGameArt o próprio autor diz que é ruim) | — | — | — |
| Granada HE | High Poly Grenades (frag + flash + fumaça) / Grenade Pack (texturizado) | https://opengameart.org/content/high-poly-grenades-flashbang-frag-grenade-smoke-grenade-no-textures ; Blend Swap /blend/3224 | locarem, willool | 3 |
| Flashbang | Flash Grenade Texture Game Ready | Blend Swap /blend/7929 | arshith007 | 3 |
| Fumaça, incendiária | Smoke / Incendiary Grenade West/East (pack CC0 Flat Grenades) | https://poly.pizza/m/GbhfKcTiF9 , https://poly.pizza/m/B7hY93Zqqk | Pichuliru | 3 |
| Molotov | Molotov / Gasoline Bomb | https://poly.pizza/m/jsmWZYqVlM | CreativeTrio | 3 |
| C4, kit de desarme | **nenhum** verificado | — | — | — |

Packs com várias armas (CC0): Stein Games "Free Classic Weapons Pack" (o melhor: realista, PBR 2K); Pichuliru "CC0
Flat" (Guns West/East, Grenades, Attachments, Ammo — estilizado, riggado); Quaternius "Ultimate Guns Pack" (25,
estilizado); chilly_durango "Low Poly Gun Models" (16, blockout); Knife "Low Quality Weapon Pack" (24, Blend Swap);
Britdawgmasterfunk "Firearms_kit_1.0" (CC-0 no Blend Swap, CC-BY no Sketchfab: vale o Blend Swap; kit de montar
AK/AR/G36/SCAR/sniper, 1,32 milhão de faces); Tabasco "Various Small Arms" (7, CC0 desde 12/2023); GGBotNet
"Untextured 3D Weapons"; Kenney "Weapon Pack" (30, página deu 403).

**As fotos de dentro do Low Quality Weapon Pack (baixado em 2026-10-03; o usuário: "podemos usar essas imagens de baixa
qualidade para fazer as armas"):** cada uma das 24 malhas (215 a 956 faces) é pintada com uma foto de lado da arma
real, empacotada no `.blend`. Extraídas em `S:\biblioteca-modelos\blendswap\low-quality-weapon-pack-knife\imagens\`
(com o `IMAGENS.json`: a arma, o tamanho em pixels e o md5). **Não são CC0:** o CC0 do pack cobre o trabalho do Knife,
não as fotos, que são de catálogo de fabricante (HK, FN, SIG, Colt), de loja de airsoft e de wiki — só para olhar e
medir a arma real na régua, nunca o arquivo no projeto (o mesmo estado das vistas do CS2 da 4.1d). São fotos limpas,
de lado, em fundo branco, de 400 a 1500 px: a USP (600×444, ≈ 0,33 mm/px) serve de contorno; a SCAR-H (600×186) e a
PSG-1 (800×183) só da proporção (≈ 1,5 mm/px). **Nenhuma é AWP, Nova ou P90.** Para o arsenal: a **USP** para a
USP-S, a **SCAR-H** para a SCAR-20 (a do CS2 é a SCAR-H de cano longo), a **PSG-1** ao lado da G3SG1 (parente da
G3SG/1), a LE6920 para conferir a M4A4 já feita; as outras (MX4, Skorpion, R870, Model 629, M1911, MP5A4, MP5SD6, G36C,
Galil SR, Glock 27, HK53, M14, MP7, P226, QBB-95, QBZ-97B, Model 7, SPAS-12, SVDs, Mini Uzi) não estão na tabela do
`CLAUDE.md` 0.7 — a MP5-SD e a MP7 do CS2 entram se o arsenal crescer.

**Alertas de origem:** o pack "Free CC0 Guns & Explosives" do 3dmodelscc0 (o único CC0 que cobre C4, flash, frag,
fumaça e molotov com PBR) não tem origem verificável — o site morreu, o domínio redireciona para outro, e no espelho do
Blendkit os mesmos modelos têm as etiquetas `cs`/`csgo`: **não usar** sem comparar com os modelos do CS. Os uploads
"Counter Strike 2"/"csgo" do Sketchfab (gettan, blazitt, AvnisT, Frostoise) são extraídos de jogo e CC-BY: fora. No Blend
Swap há "CC-0" que são cópias de jogos (TF2, Halo, MW3); o UMP 45 e o Scar-H do ColbyHep55 têm etiquetas de CoD, mas
o autor diz que modelou.

**Conclusão honesta:** com a regra "só CC0", quase nenhuma arma do arsenal tem base pronta à altura da AK, da M4A4 e
da Glock já feitas; o CC0 serve na maior parte como **referência de forma e proporção** (o lado de dentro, peças que a
foto não mostra), e a arma continua sendo modelada pelos nossos scripts.

## 7. Comunidade (fontes da reputação)

O Reddit não foi lido (ver o topo). Lidos:

| Endereço | Resumo |
|---|---|
| https://blenderartists.org/t/best-free-pbr-texturse-website-guide/1447607 | Poly Haven, ambientCG, cgbookcase e Archive CG recomendados |
| https://blenderartists.org/t/useful-websites-with-free-textures/1289311 | Poly Haven "meu favorito", 3D Textures, ambientCG, TextureCan (4K), Texturelib (grunge, não PBR) |
| https://blenderartists.org/t/free-pbr-texture-websites/1207080 | Textures.com "qualidade alta, resolução baixa sem pagar"; Texture Box; Pixel Furnace |
| https://blenderartists.org/t/free-cc0-pbr-textures-and-3d-assets-library-polyscann/1638879 | Lançamento do PolyScan |
| https://blenderartists.org/t/bpyplacement-scifi-texture-generation-inside-blender/1592861 | BPYplacement no lugar do JSplacement |
| https://community.gamedev.tv/t/textures-com-no-longer-offers-free-credits/219803 | Textures.com sem créditos grátis; sugerem Poly Haven |
| https://forums.unrealengine.com/t/all-free-assets-including-ue-ones-are-now-standard-license-on-fab-meaning-no-commercial-use/2080626 | Standard License do Fab: comercial sim, redistribuir isolado não |
| https://gist.github.com/mauricesvay/1330cc530f6ab2ef33eb6a5ea56ef5bd | Lista comentada (em parte desatualizada) |
| https://craftpbr.com/guides/free-pbr-textures e https://app.cinevva.com/guides/free-textures-hdris-materials | Guias de 2026: Poly Haven e ambientCG como base |
| https://artisticrender.com/top-32-free-texture-libraries-for-blender-and-3d-artists/ | 32 bibliotecas |
| https://www.xda-developers.com/best-places-blender-3d-textures/ | 7 sites; FreePBR é comercial pago |

Os blogs de comparação (artivoxa, webyurt etc.) têm erros de licença: usar só para descobrir nomes.
