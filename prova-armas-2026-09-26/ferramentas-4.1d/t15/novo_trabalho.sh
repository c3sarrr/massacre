#!/bin/bash
# novo_trabalho.sh <fila (1,2,3...)> <nome> <código python>: põe o trabalho na fila pela renomeação (.tmp -> .py)
S="C:/Users/T-Gamer/AppData/Local/Temp/claude/C--Users-T-Gamer-Desktop-game-tiro/c7a63f39-8955-467e-9908-7a258f968380/scratchpad/t15"
fila="$S/fila$1"; nome="$2"; shift 2
{
  echo "import sys, importlib"
  echo "sys.path.insert(0, r'C:\Users\T-Gamer\Desktop\game tiro\prova-armas-2026-09-26\ferramentas-4.1d\t14')"
  echo "import pega_banco as B"
  echo "import varreduras_p90 as V"
  echo "importlib.reload(V)"
  echo "$*"
} > "$fila/$nome.tmp"
mv "$fila/$nome.tmp" "$fila/$nome.py"
echo "na fila $1: $nome"
