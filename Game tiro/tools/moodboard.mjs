// Gera a folha de contato do moodboard (docs/art/moodboard.html) a partir de docs/art/pinterest-boards.json.
// Uso: node tools/moodboard.mjs
// Cada pin vira uma célula com o ID usado em docs/art/moodboard.md (prefixo do board + posição, ex.: FPC7).
// As imagens são exibidas direto do CDN do Pinterest (nada é baixado para o projeto). Na página:
//   ?inteira  → mostra cada foto inteira (object-fit: contain) em vez de recortada — bom para estudar detalhes;
//   ?grande   → 2 colunas (células maiores);  ?colunas=N&altura=PX → grade sob medida (estudo em telas estreitas);
//   #PREFIXO → pula para o board.

import { readFileSync, writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';

const ROOT = fileURLToPath(new URL('..', import.meta.url));
const BOARDS_JSON = `${ROOT}docs/art/pinterest-boards.json`;
const OUT = `${ROOT}docs/art/moodboard.html`;

/** Boards na ordem da folha. `phase` = subfase em que o board entrou no estudo. */
const BOARDS = [
  { id: 'CSD', label: 'Claymation Set Design', url: 'https://www.pinterest.com/ideas/claymation-set-design/893621988359/', phase: '2.1' },
  { id: 'PLA', label: '3D Plasticine', url: 'https://www.pinterest.com/ideas/3d-plasticine/901418997915/', phase: '2.1' },
  { id: 'CIL', label: 'Clay Illustration', url: 'https://www.pinterest.com/ideas/clay-illustration/925869521463/', phase: '2.1' },
  { id: 'P3D', label: 'Plastic 3D Style (cokards)', url: 'https://www.pinterest.com/cokards/plastic-3d-style/', phase: '2.1' },
  { id: 'SSD', label: 'Stop Motion Set Design', url: 'https://www.pinterest.com/ideas/stop-motion-set-design/939142592219/', phase: '2.1' },
  { id: 'SSB', label: 'Stop Motion Set Building', url: 'https://www.pinterest.com/ideas/stop-motion-set-building/913501904960/', phase: '2.1' },
  { id: 'SMD', label: 'Stop Motion Desk', url: 'https://www.pinterest.com/ideas/stop-motion-desk/951357298077/', phase: '2.1' },
  { id: 'TSH', label: 'Tilt Shift', url: 'https://www.pinterest.com/ideas/tilt-shift/942751172933/', phase: '2.5' },
  { id: 'SMA', label: 'Stop Motion Aesthetic', url: 'https://www.pinterest.com/ideas/stop-motion-aesthetic/960919693804/', phase: '2.5' },
  { id: 'SML', label: 'Stop Motion Lighting', url: 'https://www.pinterest.com/mrrufus13/stop-motion-lighting/', phase: '2.5' },
  { id: 'BTS', label: 'Behind the Scenes — Stop Motion', url: 'https://www.pinterest.com/mrrufus13/behind-the-scenes-stop-motion/', phase: '2.5' },
  { id: 'CLT', label: 'Clay Texture', url: 'https://www.pinterest.com/ideas/clay-texture/918258762185/', phase: '2.6' },
  { id: 'FPC', label: 'Fingerprint in Clay', url: 'https://www.pinterest.com/ideas/fingerprint-in-clay/914205465062/', phase: '2.6' },
  { id: 'MPC', label: 'Marbled Polymer Clay', url: 'https://www.pinterest.com/ideas/marbled-polymer-clay/957722805947/', phase: '2.6' },
  { id: 'GPD', label: 'Glitter Playdough', url: 'https://www.pinterest.com/ideas/glitter-playdough/953828611932/', phase: '2.6' },
  { id: 'GDC', label: 'Glow in the Dark Clay', url: 'https://www.pinterest.com/ideas/glow-in-the-dark-clay/902744489574/', phase: '2.6' },
  { id: 'PDH', label: 'Play Doh', url: 'https://www.pinterest.com/ideas/play-doh/922980152283/', phase: '2.6' },
  { id: 'TRL', label: 'Tape Rolls', url: 'https://www.pinterest.com/ideas/tape-rolls/905317052557/', phase: '2.6' },
  { id: 'ARM', label: 'Stop Motion Armature', url: 'https://www.pinterest.com/ideas/stop-motion-armature/922526094853/', phase: '2.6' },
  { id: 'CLF', label: 'Claymation Figures', url: 'https://www.pinterest.com/ideas/claymation-figures/918006513492/', phase: '2.6' },
  { id: 'AAC', label: 'Aardman Characters', url: 'https://www.pinterest.com/ideas/aardman-characters/928944982599/', phase: '2.6' },
  { id: 'MFP', label: 'Miniature Food Photography Props', url: 'https://www.pinterest.com/ideas/miniature-food-photography-props/932796717606/', phase: '2.6' },
  { id: 'PLI', label: 'Plasticine Ideas', url: 'https://www.pinterest.com/ideas/plasticine-ideas/924839357923/', phase: '2.6' },
  { id: 'SMR', label: 'Stop Motion Rig', url: 'https://www.pinterest.com/ideas/stop-motion-rig/923657372951/', phase: '2.6' },
  { id: 'COC', label: 'Cardboard Obstacle Course', url: 'https://www.pinterest.com/ideas/cardboard-obstacle-course/959069167784/', phase: '3.3' },
  { id: 'CBT', label: 'Cardboard Box Tunnel', url: 'https://www.pinterest.com/ideas/cardboard-box-tunnel/958387563144/', phase: '3.3' },
  { id: 'CFO', label: 'Cardboard Fingerboard Obstacles', url: 'https://www.pinterest.com/ideas/cardboard-fingerboard-obstacles/914410744968/', phase: '3.3' },
  { id: 'CFR', label: 'Cardboard Fingerboard Ramps', url: 'https://www.pinterest.com/ideas/cardboard-fingerboard-ramps/948478168138/', phase: '3.3' },
  { id: 'BAS', label: 'Books As Stairs', url: 'https://www.pinterest.com/ideas/books-as-stairs/943259823545/', phase: '3.3' },
  { id: 'AWB', label: 'Architectural Wooden Building Blocks', url: 'https://www.pinterest.com/ideas/architectural-wooden-building-blocks/935841685680/', phase: '3.3' },
  { id: 'WRG', label: 'Wall Ruler Growth Charts', url: 'https://www.pinterest.com/ideas/wall-ruler-growth-charts/907164492834/', phase: '3.3' },
  { id: 'PKG', label: 'Parkour Gym', url: 'https://www.pinterest.com/ideas/parkour-gym/958718375641/', phase: '3.3' },
  { id: 'PKC', label: 'Parkour Course', url: 'https://www.pinterest.com/ideas/parkour-course/915062227603/', phase: '3.3' },
  { id: 'CFP', label: 'Clay Footprints', url: 'https://www.pinterest.com/ideas/clay-footprints/909576168004/', phase: '3.3' },
  { id: 'CIM', label: 'Clay Imprints', url: 'https://www.pinterest.com/ideas/clay-imprints/952443037456/', phase: '3.3' },
  { id: 'DFL', label: 'Desk Flatlay', url: 'https://www.pinterest.com/ideas/desk-flatlay/918272522219/', phase: '3.3' },
  { id: 'BWM', label: 'Balsa Wood Models', url: 'https://www.pinterest.com/ideas/balsa-wood-models/953315394598/', phase: '3.3' },
  { id: 'TMA', label: 'Tape Measure Aesthetic', url: 'https://www.pinterest.com/ideas/tape-measure-aesthetic/939157022954/', phase: '3.3' },
  { id: 'PRU', label: 'Pencil Ruler', url: 'https://www.pinterest.com/ideas/pencil-ruler/922061658246/', phase: '3.3' },
  { id: 'CMR', label: 'Cardboard Marble Run', url: 'https://www.pinterest.com/ideas/cardboard-marble-run/956681619018/', phase: '3.3' },
  { id: 'LDB', label: 'Level Design Grey/Whiteboxes & Blockouts (danejcustance)', url: 'https://www.pinterest.com/danejcustance/level-design-greywhiteboxes-blockouts/', phase: '3.3' },
  { id: 'PFT', label: 'Puppet Feet', url: 'https://www.pinterest.com/ideas/puppet-feet/916422774669/', phase: '3.5' },
  { id: 'SQS', label: 'Animation Squash and Stretch', url: 'https://www.pinterest.com/ideas/animation-squash-and-stretch/951927922051/', phase: '3.5' },
  { id: 'BBR', label: 'Bouncing Ball Animation Reference', url: 'https://www.pinterest.com/ideas/bouncing-ball-animation-reference/910532601340/', phase: '3.5' },
  { id: 'CST', label: 'Clay Stop Motion Techniques', url: 'https://www.pinterest.com/ideas/clay-stop-motion-techniques/939819606233/', phase: '3.5' },
  { id: 'SFP', label: 'Sand Footprint', url: 'https://www.pinterest.com/ideas/sand-footprint/928872792576/', phase: '3.5' },
  { id: 'FIM', label: 'Footprints in Mud', url: 'https://www.pinterest.com/ideas/footprints-in-mud/934366387446/', phase: '3.5' },
  { id: 'SDP', label: 'Salt Dough Footprint', url: 'https://www.pinterest.com/ideas/salt-dough-footprint/939216583789/', phase: '3.5' },
  { id: 'CFS', label: 'Cartoon Feet Soles', url: 'https://www.pinterest.com/ideas/cartoon-feet-soles/929995699012/', phase: '3.5' },
  // Fase 4.1: as buscas (prefixo Q) guardam a primeira página pública de resultados, na ordem servida, sem repetidos.
  { id: 'QPG', label: 'Busca: polymer clay gun miniature', url: 'https://www.pinterest.com/search/pins/?q=polymer%20clay%20gun%20miniature', phase: '4.1' },
  { id: 'QPL', label: 'Busca: plasticine gun', url: 'https://www.pinterest.com/search/pins/?q=plasticine%20gun', phase: '4.1' },
  { id: 'QCG', label: 'Busca: claymation gun stop motion', url: 'https://www.pinterest.com/search/pins/?q=claymation%20gun%20stop%20motion', phase: '4.1' },
  { id: 'QRF', label: 'Busca: clay rifle sculpture', url: 'https://www.pinterest.com/search/pins/?q=clay%20rifle%20sculpture', phase: '4.1' },
  { id: 'QSG', label: 'Busca: stylized gun 3d model cartoon', url: 'https://www.pinterest.com/search/pins/?q=stylized%20gun%203d%20model%20cartoon', phase: '4.1' },
  { id: 'NFS', label: 'Nerf Snipers', url: 'https://www.pinterest.com/ideas/nerf-snipers/918985761206/', phase: '4.1' },
  { id: 'CMH', label: 'Claymation Hands', url: 'https://www.pinterest.com/ideas/claymation-hands/914622142252/', phase: '4.1' },
  { id: 'QHH', label: 'Busca: claymation hands holding', url: 'https://www.pinterest.com/search/pins/?q=claymation%20hands%20holding', phase: '4.1' },
  { id: 'CTL', label: 'Clay Sculpting Tools', url: 'https://www.pinterest.com/ideas/clay-sculpting-tools/953040767088/', phase: '4.1' },
  // Bancada de armas (mapa `arsenal`): bancada de armeiro, quadro de ferramentas, roda de modelar, suporte e planta.
  { id: 'QGW', label: 'Busca: gunsmith workbench', url: 'https://www.pinterest.com/search/pins/?q=gunsmith%20workbench', phase: '4.1' },
  { id: 'QPB', label: 'Busca: pegboard tool wall workshop', url: 'https://www.pinterest.com/search/pins/?q=pegboard%20tool%20wall%20workshop', phase: '4.1' },
  { id: 'QTT', label: 'Busca: miniature figure turntable display', url: 'https://www.pinterest.com/search/pins/?q=miniature%20figure%20turntable%20display', phase: '4.1' },
  { id: 'QWS', label: 'Busca: wire display stand miniature gun', url: 'https://www.pinterest.com/search/pins/?q=wire%20display%20stand%20miniature%20gun', phase: '4.1' },
  { id: 'QBP', label: 'Busca: gun pencil drawing blueprint', url: 'https://www.pinterest.com/search/pins/?q=gun%20pencil%20drawing%20blueprint', phase: '4.1' },
  { id: 'QVM', label: 'Busca: fps viewmodel gun', url: 'https://www.pinterest.com/search/pins/?q=fps%20viewmodel%20gun', phase: '4.1a' },
  { id: 'QCS', label: 'Busca: cs2 ak47 weapon', url: 'https://www.pinterest.com/search/pins/?q=cs2%20ak47%20weapon', phase: '4.1a' },
  { id: 'QHS', label: 'Busca: hard surface weapon 3d model', url: 'https://www.pinterest.com/search/pins/?q=hard%20surface%20weapon%203d%20model', phase: '4.1a' },
  { id: 'QWR', label: 'Busca: weapon render blender', url: 'https://www.pinterest.com/search/pins/?q=weapon%20render%20blender', phase: '4.1a' },
  { id: 'QCD', label: 'Busca: call of duty modern warfare weapon', url: 'https://www.pinterest.com/search/pins/?q=call%20of%20duty%20modern%20warfare%20weapon', phase: '4.1a' },
  { id: 'QTK', label: 'Busca: escape from tarkov weapon', url: 'https://www.pinterest.com/search/pins/?q=escape%20from%20tarkov%20weapon', phase: '4.1a' },
  { id: 'QVS', label: 'Busca: valorant vandal skin', url: 'https://www.pinterest.com/search/pins/?q=valorant%20vandal%20skin', phase: '4.1a' },
  { id: 'QAK', label: 'Busca: akm rifle', url: 'https://www.pinterest.com/search/pins/?q=akm%20rifle', phase: '4.1a' },
  { id: 'QGK', label: 'Busca: glock 17 3d render', url: 'https://www.pinterest.com/search/pins/?q=glock%2017%203d%20render', phase: '4.1a' },
  { id: 'QAW', label: 'Busca: awm sniper rifle 3d', url: 'https://www.pinterest.com/search/pins/?q=awm%20sniper%20rifle%203d', phase: '4.1a' },
  { id: 'QKN', label: 'Busca: tactical knife 3d model', url: 'https://www.pinterest.com/search/pins/?q=tactical%20knife%203d%20model', phase: '4.1a' },
  { id: 'QGL', label: 'Busca: fps hands gloves 3d', url: 'https://www.pinterest.com/search/pins/?q=fps%20hands%20gloves%203d', phase: '4.1a' },
  { id: 'QFH', label: 'Busca: first person hands holding gun', url: 'https://www.pinterest.com/search/pins/?q=first%20person%20hands%20holding%20gun', phase: '4.1a' },
  { id: 'QTG', label: 'Busca: tactical gloves', url: 'https://www.pinterest.com/search/pins/?q=tactical%20gloves', phase: '4.1a' },
  { id: 'QCK', label: 'Busca: cerakote rifle colors', url: 'https://www.pinterest.com/search/pins/?q=cerakote%20rifle%20colors', phase: '4.1a' },
  { id: 'QRL', label: 'Busca: rocket league car paint finish', url: 'https://www.pinterest.com/search/pins/?q=rocket%20league%20car%20paint%20finish', phase: '4.1a' },
  { id: 'QMP', label: 'Busca: fantastic mr fox miniature props', url: 'https://www.pinterest.com/search/pins/?q=fantastic%20mr%20fox%20miniature%20props', phase: '4.1a' },
  { id: 'QMR', label: 'Busca: m4a1 carbine rail carry handle', url: 'https://www.pinterest.com/search/pins/?q=m4a1%20carbine%20rail%20carry%20handle', phase: '4.1c' },
  { id: 'QRS', label: 'Busca: knights armament ras m4', url: 'https://www.pinterest.com/search/pins/?q=knights%20armament%20ras%20m4', phase: '4.1c' },
  { id: 'QTM', label: 'Busca: m4 carbine a2 front sight', url: 'https://www.pinterest.com/search/pins/?q=m4%20carbine%20a2%20front%20sight', phase: '4.1c' },
  { id: 'QRA', label: 'Busca: m4 quad rail ras handguard', url: 'https://www.pinterest.com/search/pins/?q=m4%20quad%20rail%20ras%20handguard', phase: '4.1c' },
  { id: 'QPD', label: 'Busca: first person pistol two hands', url: 'https://www.pinterest.com/search/pins/?q=first%20person%20pistol%20two%20hands', phase: '4.1c' },
  { id: 'QBN', label: 'Busca: m9 bayonet', url: 'https://www.pinterest.com/search/pins/?q=m9%20bayonet', phase: '4.1c' },
  // Correções da P1 da 4.1c (2026-09-28): as buscas das miras, dos acessórios, da tela de armeiro e das skins, para o
  // desenho das miras e das skins (relatório em docs/research/miras-acessorios-skins.md).
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
  { id: 'QAR', label: 'Busca: accuracy international awm', url: 'https://www.pinterest.com/search/pins/?q=accuracy%20international%20awm', phase: '4.1d' },
  { id: 'QSB', label: 'Busca: schmidt bender pm ii scope', url: 'https://www.pinterest.com/search/pins/?q=schmidt%20bender%20pm%20ii%20scope', phase: '4.1d' },
  { id: 'QSH', label: 'Busca: sniper rifle standing support hand', url: 'https://www.pinterest.com/search/pins/?q=sniper%20rifle%20standing%20support%20hand', phase: '4.1d' },
  { id: 'QNA', label: 'Busca: benelli nova shotgun', url: 'https://www.pinterest.com/search/pins/?q=benelli%20nova%20shotgun', phase: '4.1d' },
  { id: 'QNP', label: 'Busca: pump action shotgun grip hands', url: 'https://www.pinterest.com/search/pins/?q=pump%20action%20shotgun%20grip%20hands', phase: '4.1d' },
  { id: 'QP9', label: 'Busca: fn p90', url: 'https://www.pinterest.com/search/pins/?q=fn%20p90', phase: '4.1d' },
  { id: 'QPX', label: 'Busca: p90 magazine', url: 'https://www.pinterest.com/search/pins/?q=p90%20magazine', phase: '4.1d' },
  { id: 'QPH', label: 'Busca: p90 grip hands', url: 'https://www.pinterest.com/search/pins/?q=p90%20grip%20hands', phase: '4.1d' },
];

const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[c]);

const pins = JSON.parse(readFileSync(BOARDS_JSON, 'utf8'));
const known = new Set(BOARDS.map((b) => b.id));
const orphan = Object.keys(pins).filter((k) => !known.has(k));
if (orphan.length) throw new Error(`boards sem metadados em tools/moodboard.mjs: ${orphan.join(', ')}`);

const css = [
  'body{margin:0;background:#2A2320;font:14px system-ui,sans-serif;color:#F6F0E4}',
  'header{padding:16px}h1{margin:0 0 4px;font-size:22px}nav{margin-top:8px;display:flex;flex-wrap:wrap;gap:6px}',
  'nav a{color:#2A2320;background:#E8D9A8;border-radius:4px;padding:2px 6px;font-weight:700;text-decoration:none}',
  'h2{margin:18px 8px 6px;font-size:18px}h2 a{color:#FFD23F;font-size:12px;margin-left:8px}h2 small{color:#B98B5E;margin-left:8px;font-size:12px}',
  '.g{display:grid;grid-template-columns:repeat(var(--cols,4),1fr);gap:4px;padding:4px}',
  '.c{position:relative;height:var(--h,330px);background:#000;overflow:hidden}',
  '.c img{width:100%;height:100%;object-fit:cover;display:block}',
  '.inteira .c img{object-fit:contain}.grande{--cols:2}.grande .c{--h:560px}',
  '.c span{position:absolute;left:4px;top:4px;background:#FFD23F;color:#2A2320;font-weight:700;padding:2px 6px;font-size:16px;border-radius:4px}',
  '@media(max-width:700px){:root:not(.sob-medida) .g{grid-template-columns:repeat(2,1fr)}}',
].join('');

const parts = [];
parts.push('<!doctype html><html lang="pt-BR"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">');
parts.push(`<title>MASSACRE — Moodboard</title><style>${css}</style>`);
parts.push('<script>{const q=new URLSearchParams(location.search),r=document.documentElement;' +
  'for(const k of ["inteira","grande"])if(q.has(k))r.classList.add(k);' +
  'const n=Number(q.get("colunas")),h=Number(q.get("altura"));' +
  'if(n>0){r.style.setProperty("--cols",String(Math.min(8,Math.round(n))));r.classList.add("sob-medida")}' +
  'if(h>0)r.style.setProperty("--h",`${Math.min(1200,Math.round(h))}px`)}</script>');
parts.push('<header><h1>MASSACRE — Moodboard de referências (Pinterest)</h1>');
parts.push('<div>IDs usados em docs/art/moodboard.md. Imagens exibidas direto do CDN do Pinterest (nada é baixado para o projeto). ');
parts.push('Gerado por tools/moodboard.mjs · <code>?inteira</code> mostra as fotos sem recorte · <code>?grande</code> usa células maiores.</div>');
parts.push(`<nav>${BOARDS.filter((b) => pins[b.id]).map((b) => `<a href="#${b.id}">${b.id}</a>`).join('')}</nav></header>`);
let total = 0;
for (const b of BOARDS) {
  const list = pins[b.id];
  if (!list?.length) continue;
  parts.push(`<h2 id="${b.id}">${b.id} — ${esc(b.label)}<a href="${esc(b.url)}" target="_blank" rel="noopener">abrir board</a><small>subfase ${b.phase} · ${list.length} pins</small></h2><div class="g">`);
  list.forEach((hash, i) => {
    const id = `${b.id}${i + 1}`;
    parts.push(`<div class="c"><img loading="lazy" referrerpolicy="no-referrer" src="https://i.pinimg.com/736x/${hash}.jpg" alt="${id}"><span>${id}</span></div>`);
  });
  parts.push('</div>');
  total += list.length;
}
parts.push('</html>');
writeFileSync(OUT, parts.join(''));
console.log(`moodboard.html: ${BOARDS.filter((b) => pins[b.id]).length} boards, ${total} pins`);
