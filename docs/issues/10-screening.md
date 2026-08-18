# Executar e retomar o screening de 192 configurações

## What to build

Adicionar um estágio de screening que materialize e execute o produto cartesiano de oito modelos, oito caminhos de features e três regimes. O estágio deve produzir exatamente 192 identidades, prever OOF para sucessos, preservar falhas, permitir retomada idempotente e selecionar o melhor seletor/regime separadamente para cada modelo pela regra predefinida.

## What to study

- Orquestração de experimentos, produto cartesiano e máquinas de estado.
- Predições OOF, agregação de folds e comparações sob múltiplas configurações.
- Idempotência, checkpoints, atomicidade de manifests e tratamento explícito de falhas.
- Ranking por Macro-F1 com desempates determinísticos.

## Recommended tools and libraries

- scikit-learn para execução dos pipelines e métricas.
- pandas para tabela longa de 192 registros e ranking.
- JSON/PyYAML e hashing da biblioteca padrão para manifests e identidade.
- Joblib apenas para paralelização controlada e persistência compatível; pytest para testes de interrupção/retomada.

## Acceptance criteria

- [ ] O planejador cria exatamente 192 IDs únicos antes de treinar.
- [ ] A tabela final continua com 192 linhas quando algumas configurações falham.
- [ ] Cada sucesso possui uma probabilidade OOF alinhada por linha de desenvolvimento.
- [ ] Cada falha registra estágio, tipo, mensagem resumida e contexto reproduzível.
- [ ] Retomada não duplica sucesso, não confunde configuração e segue política para parciais.
- [ ] Oito vencedores são escolhidos por Macro-F1, recall da intrusão e log loss, nessa ordem aplicável.
- [ ] Nenhuma leitura de holdout ocorre e a trava é exercitada pelo teste end-to-end reduzido.

## Blocked by

- {{ISSUE_08}}
- {{ISSUE_09}}

## User stories covered

56–65.
