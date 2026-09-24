#!/usr/bin/env bash
# Cria o cluster local e reproduz o estado de produção antes da publicação
# da versão 1.4.0: gateway 1.3.0 no ar e tráfego sintético rodando.
set -euo pipefail
cd "$(dirname "$0")/.."

CLUSTER="${CLUSTER:-meetkai-sre}"
CTX="kind-${CLUSTER}"
NS=gateway
REPO=registry.interno.meetkai.local/plataforma/gateway

scripts/check-tools.sh

if ! kind get clusters 2>/dev/null | grep -qx "$CLUSTER"; then
  kind create cluster --name "$CLUSTER" --config platform/kind.yaml
fi

# O cluster não alcança o registry interno. As imagens chegam aos nós pelo
# processo de importação, que aqui é simulado com `kind load`.
for version in 1.3.0 1.4.0; do
  echo "Construindo e importando ${REPO}:${version}"
  docker build --quiet --build-arg "APP_VERSION=${version}" -t "${REPO}:${version}" app >/dev/null
  kind load docker-image --name "$CLUSTER" "${REPO}:${version}" >/dev/null
done

kubectl --context "$CTX" apply -f platform/namespace.yaml >/dev/null

# Credenciais entregues pela plataforma. Em produção, este Secret é
# sincronizado a partir do cofre e não é editado à mão.
if ! kubectl --context "$CTX" -n "$NS" get secret gateway-credentials >/dev/null 2>&1; then
  kubectl --context "$CTX" -n "$NS" create secret generic gateway-credentials \
    --from-literal=GATEWAY_API_TOKEN="demo-$(LC_ALL=C tr -dc a-f0-9 </dev/urandom | head -c 24)" >/dev/null
fi

if ! helm status gateway --kube-context "$CTX" -n "$NS" >/dev/null 2>&1; then
  echo "Instalando o gateway 1.3.0 (versão em produção)"
  helm install gateway platform/releases/gateway-1.3.0.tgz \
    --kube-context "$CTX" -n "$NS" --wait --timeout 180s >/dev/null
fi

kubectl --context "$CTX" apply -f platform/trafego.yaml >/dev/null
kubectl --context "$CTX" -n "$NS" rollout status deploy/trafego --timeout 120s >/dev/null

echo
echo "Ambiente pronto. Contexto: ${CTX}, namespace: ${NS}."
helm history gateway --kube-context "$CTX" -n "$NS"
