#!/usr/bin/env bash
# Prepara a cópia limpa para o valida-4.1c.sh: a base (`base-4.1c`, o Game tiro depois da 4.1b) copiada, os fins de
# linha em LF (a base veio do git com o autocrlf: o teste do vendor compara o GLTFLoader com o do node_modules byte a
# byte), o node_modules e o tools/blender/local.json (o caminho do Blender, fora do git) da cópia de trabalho.
# Uso: bash prepara-4.1c.sh <base> <cópia de trabalho> <raiz da cópia limpa>
set -eu -o pipefail
BASE="$1"
TRAB="$2"
RAIZ="$3"
AQUI="$(cd "$(dirname "$0")" && pwd)"
rm -rf "$RAIZ"
mkdir -p "$(dirname "$RAIZ")"
cp -r "$BASE" "$RAIZ"
rm -rf "$RAIZ/node_modules" "$RAIZ/tools/blender/conferencia"
find "$RAIZ" -name __pycache__ -type d -prune -exec rm -rf {} +
node "$AQUI/lf.mjs" "$RAIZ"
cp -r "$TRAB/node_modules" "$RAIZ/node_modules"
cp "$TRAB/tools/blender/local.json" "$RAIZ/tools/blender/local.json"
echo "cópia limpa em $RAIZ"
