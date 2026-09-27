#!/usr/bin/env bash
# Valida o plano executado da 4.1b (docs/phases/phase-4.1b-plan.md) numa cópia limpa da base, tarefa por tarefa, e o
# aplica no projeto pelo mesmo roteiro: em cada tarefa com testes, só os testes gravados têm de falhar; a tarefa inteira
# aplicada, eles passam; a suíte inteira passa no fim de cada tarefa. Depois da Tarefa 6 roda o `construir` do Blender
# (as luvas e a AK com a pega: os testes delas leem a saída). Grava as contagens em <raiz>/../contagens-4.1b.json (o
# gerador do plano as escreve nos "Expected"). No fim, compara com a cópia de trabalho (fora os binários de assets/, o
# plano executado e o que o git ignora).
# Uso: bash valida-4.1b.sh <plano.md> <raiz da cópia> [cópia de trabalho para comparar] [--sem-blender]
#   --sem-blender: em vez de construir, copia os binários da construção aceita da cópia de trabalho (a aplicação no
#   projeto, depois de a validação ter construído e conferido).
set -u -o pipefail
PLANO="$1"
RAIZ="$2"
TRAB="${3:-}"
SEM_BLENDER="${4:-}"
AQUI="$(cd "$(dirname "$0")" && pwd)"
CONTAGENS="$(dirname "$RAIZ")/contagens-4.1b.json"
testes_de() { node -e "import('$AQUI/tarefas-4.1b.mjs').then(({TAREFAS})=>console.log((TAREFAS[$1]?.testes??[]).filter(f=>f.endsWith('.test.js')).join(' ')))"; }
conta() { node --test --test-reporter=tap "$@" 2>&1 | grep -E "^# (tests|pass|fail) " | tr '\n' ' '; }
TMPD="$(mktemp -d)"
cd "$RAIZ" || exit 1
falhas=0
echo '{' > "$CONTAGENS"
for N in $(seq 2 15); do
  echo "== Tarefa $N"
  T="$(testes_de "$N")"
  antes=""
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
  if [ "$N" = 6 ]; then
    if [ "$SEM_BLENDER" = "--sem-blender" ]; then
      rm -rf assets/maos && cp -r "$TRAB/assets/maos" assets/maos && cp "$TRAB"/assets/armas/ak47/* assets/armas/ak47/
      echo "   binários da construção aceita copiados de $TRAB"
    else
      for alvo in luvas "ak47 --forcar"; do
        # shellcheck disable=SC2086
        npm run blender -- construir $alvo 2>&1 | grep -E "^(luvas|ak47)|REPROVAD|Error|Traceback" | sed 's/^/   /'
      done
    fi
  fi
  depois=""
  if [ -n "$T" ]; then
    # shellcheck disable=SC2086
    depois=$(conta $T)
    echo "   depois: $depois"
    case "$depois" in *"# fail 0 "*) ;; *) echo "   ERRO: os testes da tarefa falham depois"; falhas=$((falhas + 1)) ;; esac
  fi
  suite=$(conta "tests/**/*.test.js")
  echo "   suíte: $suite"
  case "$suite" in *"# fail 0 "*) ;; *) echo "   ERRO: a suíte falha"; falhas=$((falhas + 1)) ;; esac
  [ "$N" = 2 ] || echo ',' >> "$CONTAGENS"
  printf '"%s": {"antes": "%s", "depois": "%s", "suite": "%s"}' "$N" "$antes" "$depois" "$suite" >> "$CONTAGENS"
done
printf '\n}\n' >> "$CONTAGENS"
if [ -n "$TRAB" ]; then
  echo "== Comparação com $TRAB"
  diff -rq . "$TRAB" -x node_modules -x .git -x __pycache__ -x conferencia -x assets -x phase-4.1b-plan.md \
    -x local.json 2>&1 | head -40
fi
echo "== $falhas erro(s)"
exit $((falhas > 0))
