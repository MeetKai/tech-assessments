# Changelog · chart gateway

## 1.4.0 · 2026-09-18

- Probes configuráveis em `probes.*`, no mesmo formato dos outros serviços da plataforma.
- Nome e chave do Secret de credenciais configuráveis em `credentials.*`, seguindo a convenção de chaves em kebab-case.
- Estratégia de atualização configurável em `strategy.type`. Produção passa a usar `Recreate`, para não haver duas versões atendendo ao mesmo tempo durante a troca.
- Variáveis adicionais em `extraEnv`.
- `values-producao.yaml` concentra os valores de produção.

## 1.3.0 · 2026-09-10

- Duas réplicas por padrão e limites de memória ajustados para produção.

## 1.2.0 · 2026-08-27

- Readiness probe separada da liveness, com aquecimento do serviço.
