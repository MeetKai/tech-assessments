# DevOps / SRE · MeetKai Brasil

Bem-vinda! Neste exercício, você está de plantão quando uma publicação derruba a API de geração da plataforma. Queremos entender como você mitiga, investiga, corrige e registra o que aprendeu.

Reserve **2 a 3 horas**, dentro do prazo de **uma semana** após o recebimento. Não precisa resolver tudo. O raciocínio escrito vale tanto quanto o código: registre o que conseguiu verificar, o que ficou pendente e seu próximo passo. Pare ao chegar ao limite de tempo e informe quanto tempo usou.

O cenário, os tokens e os endereços são fictícios. A menção ao Serpro serve apenas para contextualizar a simulação. O histórico Git deste diretório faz parte do cenário.

## Comece por aqui

1. Leia [o incidente INC-2026-0918](incidente/INC-2026-0918.md).
2. Rode `make up`. Na primeira vez, leva de 3 a 10 minutos, porque baixa a imagem do kind e a base Python.
3. Rode `make smoke` e confirme que a versão 1.3.0 responde.
4. Rode `make deploy`. Ele reproduz a publicação das 18:05. A partir daqui, você está no incidente.

## Pré-requisitos

- Docker em execução (Docker Desktop, OrbStack, Colima ou equivalente), com cerca de 4 GB de memória livre.
- [kind](https://kind.sigs.k8s.io/docs/user/quick-start/#installation) 0.20 ou superior.
- [kubectl](https://kubernetes.io/docs/tasks/tools/) e [Helm](https://helm.sh/docs/intro/install/) 3 ou 4.
- `make` e `curl`.
- Internet na primeira execução, para baixar a imagem do nó do kind, `python:3.12-slim` e `prom/prometheus`.

`make check` confere as ferramentas.

## Comandos

| Comando | O que faz |
| --- | --- |
| `make up` | Cria o cluster `meetkai-sre`, importa as imagens e instala o gateway 1.3.0 |
| `make deploy` | Publica o chart de `chart/gateway` com `values-producao.yaml`, como o pipeline |
| `make status` | Mostra o histórico do Helm e os recursos do namespace `gateway` |
| `make smoke` | Chama `/v1/generate` pelo Service do gateway |
| `make traffic` | Acompanha os logs do gerador de tráfego |
| `make alerts-test` | Roda os testes das regras de alerta com `promtool` |
| `make down` | Apaga o cluster |

O contexto do kubectl é `kind-meetkai-sre` e o namespace é `gateway`.

## O que entregar

Crie os arquivos abaixo dentro de `2026-devops-sre-engineer/`.

1. **Mitigação.** Restaure o serviço antes de investigar a fundo. Registre no `INVESTIGACAO.md` o que fez e por quê.
2. **`INVESTIGACAO.md`**: para cada problema encontrado, o sintoma, a evidência (evento, log, diff), a causa e a correção. Inclua os comandos que usou.
3. **Chart corrigido.** Publique a versão 1.4.1 do chart, com `Chart.yaml` e `CHANGELOG.md` atualizados, de modo que `make deploy` e `make smoke` funcionem. Uma publicação saudável não deve derrubar o serviço: acompanhe `make traffic` durante o deploy. Não edite o Secret da plataforma nem o código em `app/`.
4. **Alertas de SLO.** Escreva as regras em `alerts/gateway-slo.rules.yaml` conforme a seção abaixo e acrescente testes em `alerts/gateway-slo.test.yaml` que cubram pelo menos uma queima rápida, uma queima lenta e a recuperação. `make alerts-test` deve passar.
5. **`POSTMORTEM.md`, em inglês.** Resumo, impacto (duração, requisições afetadas e error budget consumido, mesmo que estimados), linha do tempo, causas, o que funcionou, o que não funcionou e ações com responsável e prioridade. Sem culpados.
6. **`NOTAS.md`**, em português ou inglês, com respostas curtas:
   1. Quantos minutos de indisponibilidade o SLO de 99,9% em 30 dias permite? Quanto restava antes do incidente e o que você recomendaria sobre publicações até o fim do mês?
   2. Revise a versão 1.4.0 como se fosse um pull request. Que riscos você apontaria além dos que quebraram o deploy?
   3. Como você garantiria que só imagens construídas e assinadas pelo nosso pipeline rodem neste cluster?
   4. Como você entregaria este chart com ArgoCD num cluster sem acesso à internet?
   5. Onde o `GATEWAY_API_TOKEN` deveria ficar e como você o rotacionaria sem indisponibilidade?
7. **`USO_DE_IA.md`**: quais ferramentas de IA você usou, para quê e como conferiu as sugestões. IA é permitida e esperada; avaliamos a validação. Se não usou, registre isso.

Informe também seu tempo total e as limitações da entrega.

## Alertas de SLO

- **SLO:** 99,9% das requisições a `/v1/generate` respondidas sem erro 5xx, em janela de 30 dias.
- **Métrica:** o contador `http_requests_total{job="gateway", route="/v1/generate", code="..."}`.
- **Política do time:**

| Alerta | Dispara quando | Deve parar de disparar | `for` | `severity` |
| --- | --- | --- | --- | --- |
| `GatewayErrorBudgetFastBurn` | no ritmo atual, 2% do error budget de 30 dias seriam consumidos em 1 hora | em até 5 minutos depois que os erros param | `2m` | `page` |
| `GatewayErrorBudgetSlowBurn` | no ritmo atual, 5% do error budget de 30 dias seriam consumidos em 6 horas | em até 30 minutos depois que os erros param | `15m` | `ticket` |

- Os dois alertas levam o label `slo: gateway-availability`, além de `severity`. Agregue com `sum(...)` sem `by`, para que o alerta saia só com esses dois labels.
- As annotations são livres. Recomendamos `summary` e `runbook_url`.
- O teste que já existe passa com as regras vazias. Ele serve de exemplo do formato do `promtool`.

## Extras opcionais

Nenhum extra é necessário para passar. Priorize o incidente.

- NetworkPolicy que bloqueie o egress do gateway, já que o cluster de produção não sai para a internet.
- Imagem fixada por digest.
- PodDisruptionBudget para o gateway.
- Validação do chart em CI, por exemplo um workflow do GitHub Actions com `helm lint` e `helm template` validado por `kubeconform`.
- Um `Application` do ArgoCD para o chart.

## Entrega

Envie à pessoa que mandou o exercício o link de um repositório **privado** seu, com acesso para ela, ou um arquivo com o histórico Git (`git bundle`). Preserve o histórico inicial. Não abra pull request neste repositório público e não publique a solução.

Se travar na instalação, responda por e-mail com o comando executado, a mensagem de erro e seu sistema operacional. Pedir ajuda não prejudica a avaliação.

Ao terminar, `make down` apaga o cluster.

## Como vamos avaliar

Kubernetes e diagnóstico (30%), resposta a incidente e prática de SRE (25%), IaC, segredos e supply chain (20%), comunicação escrita, incluindo o postmortem em inglês (15%), e organização e uso de IA (10%). Esperamos uma abordagem de nível pleno: estabilizar primeiro, investigar com evidência, corrigir com o menor risco e deixar o sistema mais seguro do que estava.
