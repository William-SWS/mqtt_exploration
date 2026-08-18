# Validar, limpar e produzir features portáveis

## What to build

Adicionar um estágio de contrato e limpeza que valide schema estrito, aplique coerções auditáveis, ordene segundo regra aprovada, remova duplicatas preservando a primeira ocorrência e produza uma visão portável. O estágio deve criar somente derivações mínimas aprovadas e relatar toda coluna ou linha removida sem sobrescrever o raw.

## What to study

- Schemas de DataFrame, coerção versus validação e erros acumulados.
- Funções puras, idempotência e separação de leitura, validação, transformação e escrita.
- Feature leakage e desenho de features invariantes entre redes MQTT.
- Canonicalização de configuração e contratos de dados versionados.

## Recommended tools and libraries

- Pandera com schema estrito, coerção explícita e validação `lazy` para relatório completo.
- pandas para transformações determinísticas.
- PyYAML para política declarativa e `hashlib` para identidade.
- pytest parametrizado para schemas inválidos, deduplicação e idempotência.

## Acceptance criteria

- [ ] Coluna ausente, extra, fora de ordem ou incoercível produz falha acionável antes da escrita.
- [ ] Deduplicação preserva deterministicamente a primeira ocorrência e é idempotente.
- [ ] Hash e mtime do raw permanecem inalterados.
- [ ] A visão portável não contém alvo, IP/MAC crus, client IDs, payloads, tópicos crus, timestamps absolutos, número do frame ou metadata de captura.
- [ ] Somente derivações aprovadas aparecem e sua origem está documentada.
- [ ] O relatório quantifica linhas/colunas removidas, coerções, ausências e hashes de entrada/saída.
- [ ] Mesma entrada e configuração produzem a mesma saída semântica e identidade.

## Blocked by

- {{ISSUE_02}}
- {{ISSUE_03}}

## User stories covered

22–30 e 103–104.
