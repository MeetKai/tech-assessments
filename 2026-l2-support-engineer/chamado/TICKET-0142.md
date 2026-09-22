# TICKET-0142 · Consulta de documentos

**Cliente:** Serpro (cenário fictício)

**Abertura:** 22/09/2026, 09:12, horário de Brasília (UTC−03:00)

**SLA de primeira resposta:** 1 hora, até 10:12

**Canal:** atendimento por e-mail

**Situação:** aguardando a primeira resposta do suporte

## 09:12 · Pessoa solicitante

Bom dia. A busca da plataforma parou de funcionar. Precisamos consultar os documentos para continuar os atendimentos. Conseguem verificar?

## 09:18 · Relato A, área de contratações

Pesquiso “licitação” e dá erro, mas “contrato” funciona. Apareceu HTTP 500 e código de atendimento `req-0142-a1`. Ontem no fim do expediente consegui pesquisar normalmente. Hoje aconteceu logo que cheguei. Outra pessoa da equipe conseguiu fazer uma consulta diferente.

## 09:23 · Relato B, atendimento

Aparece “muitas requisições” enquanto eu digito. Nem cheguei a apertar Buscar. Copiei o código `req-0142-b1`, HTTP 429. Estou digitando o assunto e apagando para tentar outra palavra. Há várias pessoas usando a plataforma no mesmo prédio. A equipe de rede confirmou que saímos pelo mesmo endereço de internet.

## 09:29 · Relato C, orçamento

Diz que não tenho permissão, mas ontem eu tinha. Hoje cedo consegui entrar e depois deixei a aba aberta enquanto estava em uma reunião. Quando voltei, às 09:27, tentei consultar de novo. HTTP 403, código `req-0142-c1`. Não pedi nenhuma mudança de acesso.

## Anexo recebido às 09:32

O arquivo [app-2026-09-21.log](logs/app-2026-09-21.log) contém o registro de operação iniciado em 21/09, incluindo a manhã de 22/09. Os horários estão em UTC−03:00. A equipe informou que houve uma publicação na noite anterior. Os endereços de rede e identificadores do arquivo são fictícios.

O selo do cabeçalho aparece como “Status desconhecido”. Ainda não sabemos se isso está relacionado aos relatos.

---

Escreva sua primeira resposta considerando apenas o que era conhecido na abertura, às 09:12. Use as atualizações para investigar depois. Não trate o SLA da primeira resposta como prazo para resolver o incidente.
