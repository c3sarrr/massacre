#!/bin/bash
# esperar.sh <arquivo .out> [segundos máximos]: espera o trabalho terminar e imprime a saída
alvo="$1"; max="${2:-3000}"; t=0
while [ ! -f "$alvo" ]; do sleep 2; t=$((t+2)); if [ $t -ge $max ]; then echo "TEMPO ESGOTADO $alvo"; exit 1; fi; done
cat "$alvo"
