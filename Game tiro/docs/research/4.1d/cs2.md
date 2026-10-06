# 4.1d — como o CS2 mostra a AWP, a Nova e a P90 (pesquisa de 2026-10-03)

Pedido do usuário (2026-10-03): "é só se basear nas armas do CS2, tipo a AWP de lá, e como fica a pegada da mão em cada
arma no CS2". Quadros vistos no Chrome, nos vídeos abaixo (as armas padrão, sem skin, na posição pronta e na inspeção).
Só para olhar: nenhuma imagem do jogo entra no projeto (regra dos direitos, `CLAUDE.md` 0.7); copiamos a configuração, as
cores e as pegas, nunca a malha nem as proporções inventadas do modelo da Valve.

## Fontes

| Vídeo | Canal | Trechos |
|---|---|---|
| [CS2 - ALL WEAPONS (New Animations Summer 2025)](https://www.youtube.com/watch?v=boSwnyDyezU) | Tigerfield | a Nova em 2:51–3:00 (pronta, 2:54), a P90 em 5:20–5:30 (pronta, 5:26), a AWP em 8:25–8:45 (pronta, 8:27–8:32) |
| [Counter-Strike 2 - All Inspect Animations](https://www.youtube.com/watch?v=y1NSHUq7WOI) | PC Gaming Videos | a P90 em 1:45–1:48, a AWP em 2:56–2:59, a Nova em 3:12–3:14 |
| [COUNTER-STRIKE 2 : ALL WEAPON IN 2026 [UPDATE] 4K](https://www.youtube.com/watch?v=2B1Ty_ah9n0) | EXILAS | a AWP em 14:38–14:48 (com skin; a inspeção mostra as duas mãos) |

As posições prontas dos vídeos são as do `viewmodel` padrão do CS2 (a arma entra pela direita e aponta para o centro).

**Vistas de lado do modelo do jogo** (wiki do Counter-Strike no Fandom, URLs pelo `api.php`, `prop=imageinfo`; o CS2
reaproveita os modelos do CS:GO nas três): `W_awp_csgo.png` (1276×255, lado esquerdo), `W_nova.png` (1247×290, lado
direito), `W_p90_csgo.png` (968×415, lado direito, perspectiva leve), e os ícones do CS2 em três quartos
(`CS2_AWP_Inventory.png`, `CS2_Nova_Inventory.png`, `CS2_P90_Inventory.png`, 512×384). No ícone do CS2 a AWP mostra o
freio de fendas grosso com a porca, o cano liso, a luneta verde com as bordas pretas e o bipé dobrado para a frente; na
vista de lado a Nova é a Tactical de coronha inteiriça, e a P90 tem a ponte do trilho com as miras e o carregador
castanho-ferrugem com uma textura de pontos.

## AWP

- **Cores:** a coronha inteira verde-oliva (as laterais e o guarda-mão), a ação, o cano e o trilho pretos-azulados, o
  bipé dobrado preto sob a ponta do guarda-mão, a bola do ferrolho preta à direita. **A luneta é verde-oliva** (o tubo, a
  campânula da objetiva e o corpo da ocular), com os anéis, as torres e as bordas das campânulas pretas.
- **Forma:** o guarda-mão do CS2 é mais longo e o cano é liso e fino (diferente da AWM real, que tem o cano canelado e o
  freio de furos); a coronha de buraco do polegar, a capa de bochecha e a soleira são as da AICS.
- **Mão de apoio (pronta):** a única mão que aparece. Fica na face **esquerda** do guarda-mão, logo atrás do bipé, com o
  **dorso virado para o jogador** (o protetor dos nós à vista), o punho embaixo e os dedos subindo pela face esquerda até
  a borda de cima; o polegar fica por baixo, escondido. É o contrário da regra da frente (polegar à esquerda, dedos à
  direita).
- **Mão do gatilho (inspeção):** a pega de buraco do polegar — os quatro dedos em volta da frente do punho, o indicador
  no gatilho, o polegar passando por cima do punho, pelo buraco, até o lado esquerdo. Fora da tela na posição pronta.

## Nova

- **Cores:** toda preta fosca (o bloco de polímero, a bomba, o cano e o tubo).
- **Forma:** a Nova de coronha inteiriça (sem punho de pistola), a bomba longa nervurada, o ghost ring traseiro com as
  asas e a massa de mira com as orelhas — a Nova Tactical clássica, como a ficha.
- **Mão de apoio (pronta):** na face **esquerda** da bomba, como a da AWP: o dorso para o jogador, os dedos subindo pela
  face esquerda; um dedo (o polegar) deitado ao longo da borda de cima da bomba, apontando para a boca.
- **Mão do gatilho (pronta):** no pescoço da coronha, o **polegar deitado por cima do pescoço, apontando para a frente**
  (não enrolado para o lado esquerdo), os dedos por baixo.

## P90

- **Cores:** o quadro cinza-chumbo fosco; o carregador de cima escuro, castanho-fumê, quase opaco no jogo.
- **Forma:** a **TR** — o trilho de cima com a ponte e as **miras de ferro rebatíveis levantadas** (a de trás com as
  orelhas, a da frente com o poste), os trilhos laterais; o quebra-chama curto.
- **Mão de apoio (pronta):** na face **esquerda** do lóbulo da frente, o dorso para o jogador, os dedos subindo pela face
  esquerda.
- **Mão do gatilho (pronta e inspeção):** os dedos em volta do pescoço pelo oval de trás, o indicador no gatilho, o
  **polegar atravessando para o lado esquerdo e deitado ao longo do quadro, apontando para a frente**.
- As duas luvas ficam juntas embaixo, à esquerda da arma, quase encostadas.

## O que muda no desenho da 4.1d

A decisão 6 do desenho aprovado (a mão de apoio da AWP pela regra da frente) e a 7 (o polegar de apoio da P90 dentro da
abertura da frente) não batiam com o CS2: nas três, o CS2 põe a mão de apoio pela **face esquerda, com o dorso para o
jogador**. A luneta do CS2 é verde, não preta, e o desenho da AWP do jogo foge da AWM real (o guarda-mão longo, o cano
liso e fino).

**Decisões do usuário (2026-10-03):** "Pega do CS2 nas três" e "Forma do CS2 também" — com o aviso de que imitar as
proporções do modelo da Valve vai contra a regra de vender sem problema de direitos (conferir com um advogado antes de
vender). O desenho (`docs/superpowers/specs/2026-10-03-4.1d-awp-nova-p90-design.md`, item 9) passa a tirar o contorno da
régua das vistas de lado do jogo, na escala da arma real, e a mão de apoio das três pela regra nova `lateral`; a regra da
frente fica na AK e na M4A4.
