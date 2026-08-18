# Task 13 — Relatório, holdout e reprodutibilidade

## Objetivo

Abrir o holdout uma única vez após o congelamento, produzir avaliação por frame e evento com incerteza temporal e empacotar evidências reproduzíveis.

## Pré-requisitos

- Concluir a Task 12; todas as escolhas e hashes precisam estar congelados.
- Ler ADR-011, ADR-016 e ADR-017.
- Definir evento, alerta e bloco de bootstrap antes de observar o teste.

## Conceitos e APIs para estudar

- Accuracy, precision da intrusão, Macro/weighted/intrusion F1, recall, PR-AUC, ROC-AUC, FPR e log loss.
- Matriz de confusão, curva de calibração e comparação nos limiares 0,5/ajustado.
- Sequências contíguas de intrusão, tempo até primeiro alerta e falsos alertas por 10.000 frames normais.
- Bootstrap temporal com 2.000 reamostragens em blocos e intervalos percentis de 95%.
- Model cards, threat-to-validity, manifests JSON, configuração resolvida, Joblib e `state_dict`.

## Exercício a implementar futuramente

Validar o selo de congelamento, treinar finalistas nos 70% de desenvolvimento conforme receita congelada e avaliar uma vez nos últimos 30%. Calcular todas as métricas por frame e evento, intervalos em blocos, figuras e tabelas. Executar ablações de identificadores e de ordem/timestamps somente para finalistas e rotulá-las como diagnóstico, sem reescolher o modelo principal.

## Entregáveis

- Relatório reproduzível com tabela principal, intervalos, matrizes e calibração.
- Métricas por evento: detectados, atraso até primeiro alerta e falsos alertas/10.000 frames normais.
- Manifests/configuração/hashes/versões/seeds/features/parâmetros/status por execução.
- Model cards, ameaças à validade e artefatos Joblib/`state_dict` com metadata.
- Teste end-to-end sobre amostra pequena sem acessar resultados pré-computados.

## Testes esperados

- Abertura do holdout requer configuração congelada e gera registro irreversível/auditável.
- Métricas conferem com exemplos pequenos conhecidos e matrizes de confusão.
- Eventos contíguos e atraso são corretos em sequências artificiais de borda.
- Bootstrap faz exatamente 2.000 reamostragens por blocos com seed registrada.
- Toda tabela/figura aponta para execução e configuração de origem.
- Ablations não alteram ranking/configuração principal.

## Critérios de aceite

- Todas as métricas obrigatórias e os dois limiares são reportados.
- Intervalos de 95% respeitam dependência temporal.
- Nenhuma alegação de edge é feita.
- Outra máquina consegue refazer o relatório com lockfile, config, dados versionados e comandos documentados.

## Perguntas de reflexão

- O teste foi realmente usado uma vez ou houve feedback informal por gráficos/logs?
- Um evento detectado no último frame foi operacionalmente útil?
- Que ameaça à validade impede generalizar deste capture para outra rede MQTT?

## Decisões que devem ser registradas

Registrar data de abertura, configuração congelada, definição de evento/alerta, blocos de bootstrap, resultados finais, ablações e todas as ameaças à validade identificadas.
