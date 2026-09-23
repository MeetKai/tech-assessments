# Engenharia de Suporte · MeetKai Brasil

Bem-vinda! Neste exercício, você assume um chamado de suporte de uma plataforma de busca de documentos. Queremos entender como você investiga, organiza evidências e se comunica com o cliente.

Reserve **4 a 6 horas**, dentro do prazo de **uma semana** após o recebimento. Não precisa resolver tudo. O raciocínio escrito vale tanto quanto o código: registre o que conseguiu verificar, o que ficou pendente e seu próximo passo. Pare ao chegar ao limite de tempo e informe quanto tempo usou.

O cenário, as contas, o acervo e os registros são fictícios. A menção ao Serpro serve apenas para contextualizar a simulação. Não use dados reais de clientes. O histórico do repositório faz parte do cenário.

## Comece por aqui

1. Leia [o chamado TICKET-0142](chamado/TICKET-0142.md). A primeira mensagem chegou às 09:12, com SLA de primeira resposta de uma hora.
2. Escreva sua primeira resposta **antes de investigar a causa**. Você pode fazer perguntas e combinar o próximo retorno.
3. Suba o portal, reproduza os relatos e consulte [o registro de operação](chamado/logs/app-2026-09-21.log), além do código e do histórico Git.
4. Faça as correções que conseguir, acrescente testes e documente suas conclusões.

Se travar na instalação, responda por e-mail à pessoa que enviou o exercício. Inclua o comando executado, a mensagem de erro e seu sistema operacional. Pedir ajuda não prejudica a avaliação.

## Execute o portal

Você precisa de Git, Make, [uv](https://docs.astral.sh/uv/getting-started/installation/), Python 3.12 e Node.js 20 ou superior, com npm. O uv pode instalar o Python 3.12 quando necessário. A primeira execução precisa de internet para baixar as dependências. Não é necessário Docker nem banco externo.

```sh
git clone git@github.com:MeetKai/tech-assessments.git
cd tech-assessments/2026-l2-support-engineer
make dev
```

Se você não usa chave SSH, clone por HTTPS:

```sh
git clone https://github.com/MeetKai/tech-assessments.git
```

Espere a mensagem **Portal: http://127.0.0.1:5173** e abra esse endereço. Ela aparece depois que a API e a interface iniciam. O comando prepara as dependências e reutiliza a instalação do frontend enquanto os arquivos de dependências não mudarem. Você também pode executar `make dev` na raiz do repositório.

O `make dev` instala as dependências Python e JavaScript em uma pasta temporária local do sistema, separada para cada cópia do repositório. O frontend usa uma cópia local dos arquivos da interface e atualiza essa cópia quando você edita o projeto. Isso evita atrasos de leitura quando `Documents` está sincronizada. A primeira execução após uma limpeza de arquivos temporários reinstala as dependências automaticamente.

Para iniciar só a interface, execute `npm run dev` dentro de `frontend/`. Esse comando usa a mesma cópia local e espera que a API esteja rodando em `127.0.0.1:8000` para consultas e login.

As portas 5173 e 8000 precisam estar livres. Use Ctrl+C uma vez e aguarde o encerramento dos dois serviços, que pode levar até três segundos. Após editar o backend, reinicie `make dev`; o frontend atualiza automaticamente. Se uma porta estiver ocupada, use `lsof -nP -iTCP:5173 -sTCP:LISTEN` ou o mesmo comando com `8000` para identificar o processo antes de encerrá-lo.

| Campo | Valor de demonstração |
| --- | --- |
| Usuário | `servidor` |
| Senha | `acesso-demo-2026` |
| Segunda conta | `colega`, com a mesma senha |

As contas têm o mesmo perfil de acesso. O acervo contém 200 documentos. Dados, sessões e contadores ficam em memória e são reiniciados junto com a API. O token dura 600 segundos por padrão.

Para experimentar uma duração diferente, encerre o portal e use:

```sh
TOKEN_TTL_SECONDS=20 make dev
```

## Comandos e estrutura

```sh
make test     # testes de backend e frontend
make build    # verificação TypeScript e build da interface
```

Os testes existentes verificam alguns fluxos, mas não garantem o funcionamento de cada situação do chamado. Você pode acrescentar testes com pytest e Vitest; não é necessário trocar as ferramentas.

```text
backend/app/           API, sessões e acervo em memória
backend/tests/         testes com pytest
frontend/src/          interface Lit e TypeScript
chamado/               conversa e evidências do atendimento
scripts/dev.py         inicialização local
```

A interface usa o proxy do Vite para enviar `/api` à API em `127.0.0.1:8000`. Os logs aparecem no terminal de `make dev`. O código de atendimento exibido na tela corresponde ao `request_id` dos logs. A documentação da API está em **http://127.0.0.1:8000/docs**.

## O que entregar

Crie os arquivos abaixo dentro de `2026-l2-support-engineer/`, em português. Use exemplos e evidências que você realmente verificou.

1. **`RESPOSTA_INICIAL.md`**: sua primeira resposta ao cliente, dentro do SLA, ainda sem conhecer a causa.
2. **`INVESTIGACAO.md`**: para cada problema, registre hipótese, verificações, evidência e causa raiz. A evidência pode ser um trecho de log, um commit ou uma reprodução. Inclua a nota de escalonamento que enviaria ao time técnico se precisasse de ajuda.
3. **Código e testes**: corrija os três comportamentos relatados no chamado, com pelo menos um teste automatizado para cada. Explique como executar os testes.
4. **Disponibilidade**: implemente `/api/health` como uma verificação leve, sem consultar a busca, retornando HTTP 200 ou 204. Faça o selo do cabeçalho refletir o estado do serviço.
5. **`RESPOSTA_FINAL.md`**: explique ao cliente o que aconteceu e o que foi resolvido, sem jargão desnecessário. Se algo estiver pendente, diga o próximo passo.
6. **`RUNBOOK.md`**: uma página com o título “Busca indisponível ou com erro: como diagnosticar”, para a próxima pessoa do suporte. Inclua ações que ela consiga seguir e quando escalar.
7. **`USO_DE_IA.md`**: quais ferramentas de IA você usou, para quê e como conferiu as sugestões. IA é permitida e esperada; avaliamos a validação. Se não usou, registre isso.

Informe também seu tempo total, as limitações da entrega e como a pessoa avaliadora pode repetir suas verificações. Envie o link do seu repositório ou um arquivo com o histórico Git à pessoa que enviou o exercício. Preserve o histórico inicial e não abra um pull request neste repositório público.

## Extras opcionais

Nenhum extra é necessário para passar. Priorize o atendimento e a investigação.

- Logging estruturado em JSON, com `request_id` propagado da interface à API.
- Métricas simples, como contadores de status por rota, e uma visão de status na interface.
- Mensagens mais úteis para HTTP 401, 403, 404, 429, 500 e 503.
- Uma pequena funcionalidade à sua escolha, como destacar o termo buscado nos resultados.

## Como vamos avaliar

Raciocínio de diagnóstico (30%), comunicação escrita (25%), base técnica (20%), organização e testes (15%) e extras (10%). Esperamos uma abordagem de nível júnior: observar, testar hipóteses, explicar limites e pedir ajuda com contexto. Não é necessário reescrever a aplicação nem adicionar infraestrutura.
