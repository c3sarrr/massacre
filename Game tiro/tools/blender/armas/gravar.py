# Gravar um arquivo de saída do construir (Fase 4.1c; plano da 4.1c, Tarefa 11): o Windows às vezes segura por um instante
# o arquivo de antes de uma textura ou de um .glb (o antivírus ou o indexador lendo o que acabou de mudar) e a gravação
# falha no meio de uma construção de minutos — a ak47_mundo_m.webp ("Could not open file") e o knife.glb ("[Errno 22]
# Invalid argument") em duas construções seguidas. A gravação espera um pouco e tenta de novo.
import time

TENTATIVAS = 6
ESPERA_S = 0.5  # cresce a cada tentativa: 0,5 + 1 + 1,5 + 2 + 2,5 s no pior caso


def com_novas_tentativas(gravar, caminho):
    """Chama `gravar()` até dar certo; entre as tentativas, avisa (a linha MASSACRE-AVISO que o lançador mostra) e espera.
    Na última, o erro sobe com o caminho do arquivo."""
    for k in range(TENTATIVAS):
        try:
            return gravar()
        except (OSError, RuntimeError) as erro:
            if k == TENTATIVAS - 1:
                raise RuntimeError(f'{caminho}: {TENTATIVAS} tentativas de gravar, o arquivo continua preso') from erro
            print(f'MASSACRE-AVISO {caminho} preso ({str(erro).splitlines()[0]}); gravando de novo')
            time.sleep(ESPERA_S * (k + 1))
