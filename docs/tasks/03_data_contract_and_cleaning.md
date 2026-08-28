# Task 03 — Contrato de dados e limpeza

## Objetivo

Converter descobertas da EDA em um contrato validado e uma limpeza determinística que produza dados intermediários sem jamais sobrescrever o raw.

## Pré-requisitos

- Concluir a Task 02 e aprovar o dicionário de dados.
- Ler ADR-006, ADR-007 e ADR-016.
- Saber escrever funções puras e testes parametrizados.

## Conceitos e APIs para estudar

- Schema explícito, coerção segura, categorias, valores ausentes e invariantes.
- Funções puras, idempotência e separação entre leitura, validação, transformação e escrita.
- `hashlib.sha256`, `yaml.safe_load` e validação estrita de configuração.
- Canonicalização antes do hash de configuração; erro em campos desconhecidos ou obrigatórios ausentes.

## Exercício a implementar futuramente

Definir schema de entrada e configuração `configs/intrusion.yaml`. Implementar carregamento com verificação de hash, coerção auditável, ordenação definida, deduplicação estável com `keep="first"`, remoção de colunas vazias/constantes segundo política e criação apenas das derivações portáveis aprovadas. Salvar uma nova saída em `data/interim` com relatório de transformações.

## Entregáveis

- Contrato versionado de colunas, tipos, alvo, classe positiva e hashes.
- Funções reutilizáveis em `src/mqtt_ids`, com entrypoint fino em `scripts`.
- Configuração resolvida e relatório de linhas/colunas removidas ou derivadas.
- Identidade de execução baseada em versão, protocolo, políticas e hash da configuração.

## Testes esperados

- Hash, schema, contagem de linhas/classes e nomes obrigatórios são validados.
- Arquivo raw mantém hash e mtime após execução.
- Deduplicação preserva a primeira ocorrência e é idempotente.
- Alvo, identificadores e ordem absoluta não aparecem no conjunto portável.
- Campo ausente, extra, tipo incoercível ou configuração desconhecida falha antes de qualquer escrita.

## Critérios de aceite

- Mesma entrada + mesma configuração produz bytes ou conteúdo semanticamente idêntico.
- Toda perda de informação é quantificada e rastreável.
- Nenhuma função depende de estado escondido de notebook.
- Saída intermediária e relatório referenciam os hashes de entrada e configuração.

## Perguntas de reflexão

- Em que ponto um valor incoercível deve falhar em vez de virar `NaN`?
- Hash do arquivo basta ou também precisamos de invariantes semânticos?
- Como manter estável a identidade de uma configuração YAML equivalente?

## Decisões que devem ser registradas

Registrar schema aprovado, coerções, representação do alvo, regras de deduplicação/ordenação, derivações portáveis, formato de artefatos e política de validação YAML.
