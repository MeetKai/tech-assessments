CLUSTER ?= meetkai-sre
CTX := kind-$(CLUSTER)
NS := gateway
PROMETHEUS_IMAGE ?= prom/prometheus:v3.5.0

.PHONY: check up deploy status smoke traffic alerts-test down

check:
	@scripts/check-tools.sh

up:
	@CLUSTER=$(CLUSTER) scripts/up.sh

# Passo de publicação do pipeline de produção.
deploy:
	helm upgrade gateway chart/gateway --kube-context $(CTX) -n $(NS) \
		-f chart/gateway/values-producao.yaml

status:
	@helm history gateway --kube-context $(CTX) -n $(NS)
	@echo
	@kubectl --context $(CTX) -n $(NS) get deploy,rs,pods -o wide

smoke:
	@CLUSTER=$(CLUSTER) scripts/smoke.sh

traffic:
	kubectl --context $(CTX) -n $(NS) logs deploy/trafego --tail=30 -f

alerts-test:
	docker run --rm -v "$(CURDIR)/alerts:/alerts:ro" --entrypoint promtool \
		$(PROMETHEUS_IMAGE) test rules /alerts/gateway-slo.test.yaml

down:
	kind delete cluster --name $(CLUSTER)
