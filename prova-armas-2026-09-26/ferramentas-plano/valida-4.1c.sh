#!/usr/bin/env bash
# Valida o plano executado da 4.1c (docs/phases/phase-4.1c-plan.md) numa cópia limpa da base, tarefa por tarefa, e o
# aplica no projeto pelo mesmo roteiro: em cada tarefa com testes, só os testes gravados têm de falhar; a tarefa inteira
# aplicada, eles passam; a suíte inteira passa no fim de cada tarefa. Depois da Tarefa 4 roda a prova das peças e,
# depois da 11, o `construir todas` do Blender (as luvas e as quatro armas: os testes delas leem a saída). Grava as
# contagens em <raiz>/../contagens-4.1c.json (o gerador do plano as escreve nos "Expected"). No fim, compara com a cópia
# de trabalho (sem a diferença de fim de linha; fora os binários de assets/, o plano executado e o que o git ignora).
# Uso: bash valida-4.1c.sh <plano.md> <raiz da cópia> <cópia de trabalho> [--sem-blender] [primeira] [última]
#   A cópia de trabalho dá a textura CC0 da Tarefa 7 (o plano manda baixar; aqui ela vem de lá, com o mesmo md5) e é
#   a referência da comparação final.
#   --sem-blender: em vez de provar e construir, copia os binários da construção aceita da cópia de trabalho (a
#   aplicação no projeto, depois de a validação ter construído e conferido).
#   primeira/última: só essas tarefas (para refazer um trecho; as contagens saem só delas).
set -u -o pipefail
export PYTHONIOENCODING=utf-8
PLANO="$1"
RAIZ="$2"
TRAB="$3"
SEM_BLENDER="${4:-}"
DE="${5:-1}"
ATE="${6:-16}"
AQUI="$(cd "$(dirname "$0")" && pwd -W)"
CONTAGENS="${CONTAGENS:-$(dirname "$RAIZ")/contagens-4.1c.json}"
# os testes .test.js de uma tarefa: os do "Run" que espera FAIL na seção dela
testes_de() {
  node -e "
    const linhas = require('fs').readFileSync(process.argv[1], 'utf8').split('\n');
    let t = null;
    for (let i = 0; i < linhas.length; i++) {
      const m = /^### Tarefa (\d+):/.exec(linhas[i]);
      if (m) t = Number(m[1]);
      const r = /^Run: \`node --test ([^\"\`]+)\`$/.exec(linhas[i]);
      if (t === $1 && r && linhas[i + 1].startsWith('Expected: FAIL')) { console.log(r[1]); break; }
    }" "$PLANO"
}
conta() { node --test --test-reporter=tap "$@" 2>&1 | grep -E "^# (tests|pass|fail) " | tr '\n' ' '; }
copia_saidas() {
  node -e "import(require('url').pathToFileURL('$AQUI/tarefas-4.1c.mjs').href).then(({SAIDAS})=>console.log((SAIDAS[$1]??[]).join('\n')))" | while read -r d; do
    [ -n "$d" ] || continue
    rm -rf "$d" && mkdir -p "$(dirname "$d")" && cp -r "$TRAB/$d" "$d"
  done
}
TMPD="$(mktemp -d)"
cd "$RAIZ" || exit 1
falhas=0
echo '{' > "$CONTAGENS"
primeira=1
for N in $(seq "$DE" "$ATE"); do
  echo "== Tarefa $N"
  T="$(testes_de "$N")"
  antes=""
  if [ -n "$T" ]; then
    rm -rf "$TMPD/tests" && cp -r tests "$TMPD/tests"
    python3 "$AQUI/aplica-4.1c.py" "$PLANO" . "$N" "$N" tests/ > /dev/null || { echo "   ERRO ao gravar os testes"; falhas=$((falhas + 1)); }
    # shellcheck disable=SC2086
    antes=$(conta $T)
    rm -rf tests && cp -r "$TMPD/tests" tests
    echo "   antes (só os testes): $antes"
    case "$antes" in *"# fail 0 "*) echo "   ERRO: os testes da tarefa não falharam antes"; falhas=$((falhas + 1)) ;; esac
  fi
  python3 "$AQUI/aplica-4.1c.py" "$PLANO" . "$N" "$N" | sed 's/^/   /' || { echo "   ERRO ao aplicar"; falhas=$((falhas + 1)); }
  # a textura CC0 que a tarefa manda baixar (o md5 do registro confere)
  node -e "import(require('url').pathToFileURL('$AQUI/tarefas-4.1c.mjs').href).then(({BINARIOS})=>console.log((BINARIOS[$N]??[]).map(b=>b.arquivo+' '+b.md5).join('\n')))" | while read -r arq md5; do
    [ -n "$arq" ] || continue
    mkdir -p "$(dirname "$arq")" && cp "$TRAB/$arq" "$arq"
    [ "$(md5sum "$arq" | cut -d' ' -f1)" = "$md5" ] && echo "   $arq (md5 conferido)" || echo "   ERRO: md5 de $arq"
  done
  prova=$(node -e "import(require('url').pathToFileURL('$AQUI/tarefas-4.1c.mjs').href).then(({PROVAR})=>console.log((PROVAR[$N]??[]).join(' ')))")
  for alvo in $prova; do
    if [ "$SEM_BLENDER" = "--sem-blender" ]; then
      echo "   provar $alvo: pulado (--sem-blender)"
    else
      npm run blender -- provar "$alvo" 2>&1 | grep -E "^peças:|REPROVAD|problema|Error|Traceback" | sed 's/^/   /'
      [ "${PIPESTATUS[0]}" = 0 ] || { echo "   ERRO: a prova reprovou"; falhas=$((falhas + 1)); }
    fi
  done
  alvos=$(node -e "import(require('url').pathToFileURL('$AQUI/tarefas-4.1c.mjs').href).then(({CONSTRUIR})=>console.log((CONSTRUIR[$N]??[]).join(' ')))")
  if [ -n "$alvos" ]; then
    if [ "$SEM_BLENDER" = "--sem-blender" ]; then
      copia_saidas "$N"
      echo "   binários da construção aceita copiados de $TRAB"
    else
      for alvo in $alvos; do
        npm run blender -- construir "$alvo" 2>&1 | grep -E "^(luvas|ak47|glock|m4a4|knife)|aviso|booleano|REPROVAD|Error|Traceback" | sed 's/^/   /'
        [ "${PIPESTATUS[0]}" = 0 ] || { echo "   ERRO: o construir reprovou"; falhas=$((falhas + 1)); }
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
  case "$suite" in *"# fail 0 "*) ;; *) echo "   ERRO: a suíte falha"; falhas=$((falhas + 1))
    node --test --test-reporter=tap "tests/**/*.test.js" 2>&1 | grep -E "^not ok|^# Subtest" | grep -B1 "^not ok" | head -20 | sed 's/^/      /' ;; esac
  [ "$primeira" = 1 ] || echo ',' >> "$CONTAGENS"
  primeira=0
  printf '"%s": {"antes": "%s", "depois": "%s", "suite": "%s"}' "$N" "$antes" "$depois" "$suite" >> "$CONTAGENS"
done
printf '\n}\n' >> "$CONTAGENS"
if [ "$ATE" = 16 ]; then
  echo "== Comparação com $TRAB"
  diff -rq --strip-trailing-cr . "$TRAB" -x node_modules -x .git -x __pycache__ -x conferencia -x assets \
    -x phase-4.1c-plan.md -x local.json 2>&1 | head -40
fi
echo "== $falhas erro(s)"
exit $((falhas > 0))
