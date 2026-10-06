# Tarefa 12 (a regra lateral): resume as linhas MASSACRE-PROVA-LATERAL de um log da prova do bloco (provas_lateral.py,
# rodada direto no Blender com a saída num arquivo): a pega, quanto a palma andou, as polpas, as falanges médias, o lado
# direito, o dorso, o polegar, os contatos da palma e do polegar, a penetração, a distal do polegar (quando o log traz)
# e os problemas de cada uma.
#   python ler_lateral.py <log>
import json
import sys

for linha in open(sys.argv[1], encoding='utf-8', errors='replace'):
    if not linha.startswith('MASSACRE-PROVA-LATERAL '):
        continue
    r = json.loads(linha[len('MASSACRE-PROVA-LATERAL '):])
    pega = (f"{r['alturaMM']:+.0f} {r.get('inclinacaoGraus', 0):+.0f} {r['giradaGraus']:+.0f} "
            f"{r.get('eixoPolegarGraus', 0):.0f} {r.get('guinadaGraus', 0):+.0f}")
    if 'erro' in r:
        print(f"{pega} ERRO {r['erro'][:220]}")
        continue
    L, c = r['ladosLateral'], r['contatosMM']
    medias = L.get('mediasGraus', {})
    distal = (f" | distal {r['distalAFrenteGraus']}° da frente {r['distalDoPolegar']}"
              if 'distalDoPolegar' in r else '')
    print(f"{pega} andou {r['palmaAndouMM']} polpas {list(L['polpasMM'].values())} medias {list(medias.values())} "
          f"dir {L['direitaMM']} dorso {L['dorsoGraus']} pol {L['polegarGraus']} | palma {c['palma']} polegar "
          f"{c.get('polegar')} | pen {r['penetracaoMM']} | jogador {r.get('dorsoAoJogadorGraus')}°{distal} | "
          f"nprob {len(r['problemas'])} {r['segundos']}s")
    for q in r['problemas']:
        print('    ', q[:170])
