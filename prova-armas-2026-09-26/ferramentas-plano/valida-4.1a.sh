#!/usr/bin/env bash
# Valida um plano da 4.1a (o executado, docs/phases/phase-4.1a-plan.md) numa cópia limpa da base, tarefa por tarefa, e
# o aplica no projeto pelo mesmo roteiro: em cada tarefa com testes, só os testes gravados têm de falhar; a tarefa
# inteira aplicada, eles passam; a suíte inteira passa no fim de cada tarefa. Depois da Tarefa 8 roda o `construir` do
# Blender (os testes da AK leem a saída dele) e depois da 9 regenera o vendor. No fim, compara com a cópia de trabalho
# (fora os binários de assets/armas, o vendor regenerado e o que o git ignora).
# Uso: bash valida-4.1a.sh <plano.md> <raiz da cópia> [cópia de trabalho para comparar]
set -u -o pipefail
PLANO="$1"
RAIZ="$2"
TRAB="${3:-}"
AQUI="$(cd "$(dirname "$0")" && pwd)"
declare -A TESTES=(
  [1]="tests/fichaArma.test.js tests/regua.test.js tests/weaponRecipes.test.js"
  [2]="tests/skinsArma.test.js" [3]="tests/skinsArma.test.js" [4]="tests/armasSaida.test.js"
  [8]="tests/armaAk47.test.js" [9]="tests/vendorGltf.test.js" [10]="tests/materialArma.test.js"
  [11]="tests/weaponLibraryGlb.test.js" [12]="tests/setReflection.test.js"
  [13]="tests/viewmodel.test.js tests/armaAk47.test.js" [14]="tests/arsenalStand.test.js"
  [15]="tests/skinCommand.test.js" [16]="tests/weaponRecipes.test.js tests/viewmodel.test.js tests/weaponLibraryGlb.test.js"
)
conta() { node --test --test-reporter=tap "$@" 2>&1 | grep -E "^# (tests|pass|fail) " | tr '\n' ' '; }
TMPD="$(mktemp -d)"  # respeita o TMPDIR
cd "$RAIZ" || exit 1
falhas=0
for N in $(seq 1 19); do
  echo "== Tarefa $N"
  T="${TESTES[$N]:-}"
  if [ -n "$T" ]; then
    rm -rf "$TMPD/tests" && cp -r tests "$TMPD/tests"
    python3 "$AQUI/aplica-testes-4.1a.py" "$PLANO" . "$N" "$N" > /dev/null || { echo "   ERRO ao gravar os testes"; falhas=$((falhas + 1)); }
    # shellcheck disable=SC2086
    antes=$(conta $T)
    rm -rf tests && cp -r "$TMPD/tests" tests
    echo "   antes (só os testes): $antes"
    case "$antes" in *"# fail 0 "*) echo "   ERRO: os testes da tarefa não falharam antes"; falhas=$((falhas + 1)) ;; esac
  fi
  python3 "$AQUI/aplica-4.1a.py" "$PLANO" . "$N" "$N" | sed 's/^/   /' || { echo "   ERRO ao aplicar"; falhas=$((falhas + 1)); }
  if [ "$N" = 8 ]; then
    npm run blender -- construir ak47 2>&1 | grep -E "^ak47|REPROVADO|Error" | sed 's/^/   /'
  fi
  if [ "$N" = 9 ]; then
    npm run vendor > /dev/null 2>&1 && echo "   vendor regenerado"
  fi
  if [ -n "$T" ]; then
    # shellcheck disable=SC2086
    depois=$(conta $T)
    echo "   depois: $depois"
    case "$depois" in *"# fail 0 "*) ;; *) echo "   ERRO: os testes da tarefa falham depois"; falhas=$((falhas + 1)) ;; esac
  fi
  suite=$(conta "tests/**/*.test.js")
  echo "   suíte: $suite"
  case "$suite" in *"# fail 0 "*) ;; *) echo "   ERRO: a suíte falha"; falhas=$((falhas + 1)) ;; esac
done
if [ -n "$TRAB" ]; then
  echo "== Comparação com $TRAB"
  diff -rq . "$TRAB" -x node_modules -x .git -x __pycache__ -x conferencia -x assets -x phase-4.1a-plan.md \
    -x local.json 2>&1 | head -40
fi
echo "== $falhas erro(s)"
exit $((falhas > 0))
