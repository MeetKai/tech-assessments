#!/usr/bin/env bash
# Confere as ferramentas necessárias para o exercício.
set -euo pipefail

missing=0
for tool in docker kind kubectl helm; do
  if ! command -v "$tool" >/dev/null 2>&1; then
    echo "Não encontrei '$tool' no PATH." >&2
    missing=1
  fi
done
if [ "$missing" -ne 0 ]; then
  echo "Veja a seção \"Pré-requisitos\" do README." >&2
  exit 1
fi

if ! docker info >/dev/null 2>&1; then
  echo "O Docker está instalado, mas o daemon não respondeu. Inicie o Docker e tente de novo." >&2
  exit 1
fi

echo "docker  $(docker version --format '{{.Server.Version}}')"
echo "kind    $(kind version | awk '{print $2}')"
echo "kubectl $(kubectl version --client -o json | sed -n 's/.*"gitVersion": "\(v[^"]*\)".*/\1/p' | head -1)"
echo "helm    $(helm version --short)"
