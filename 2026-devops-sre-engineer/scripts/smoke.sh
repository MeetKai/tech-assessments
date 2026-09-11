#!/usr/bin/env bash
# Chama a API de geração pelo Service do gateway.
set -euo pipefail

CTX="kind-${CLUSTER:-meetkai-sre}"
NS=gateway
PORT="${SMOKE_PORT:-18080}"

kubectl --context "$CTX" -n "$NS" port-forward svc/gateway "${PORT}:8080" >/dev/null 2>&1 &
pf=$!
trap 'kill "$pf" 2>/dev/null || true' EXIT

for _ in $(seq 1 20); do
  if curl -fsS "http://127.0.0.1:${PORT}/readyz" >/dev/null 2>&1; then
    break
  fi
  sleep 0.5
done

if body=$(curl -fsS "http://127.0.0.1:${PORT}/v1/generate"); then
  echo "OK  ${body}"
else
  echo "FALHOU  não foi possível chamar /v1/generate pelo Service gateway." >&2
  exit 1
fi
