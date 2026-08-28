# Task 14 — Especificação de benchmark edge futuro

## Objetivo

Especificar um protocolo para medir implantação em Raspberry Pi no futuro, sem produzir nesta versão números, promessas ou escolhas baseadas em hardware não testado.

## Pré-requisitos

- Concluir a Task 13 e ler ADR-004.
- Ter modelo final, pré-processador e contrato de entrada congelados.
- Antes da execução futura, definir modelo exato do Raspberry Pi, SO, runtime e alimentação.

## Conceitos e APIs para estudar

- Exportação adequada ao modelo (Joblib, TorchScript/ONNX quando justificado) e equivalência numérica.
- Warm-up, latência por frame e por lote, throughput, percentis p50/p95/p99.
- Resident Set Size (RSS), tamanho em disco, tempo de inicialização e consumo energético opcional.
- Afinidade de CPU, frequência, temperatura/throttling, concorrência e protocolo de repetição.

## Exercício a implementar futuramente

Escrever e revisar um protocolo antes de possuir resultados: ambiente fixado; conjunto de benchmark sem labels no caminho de inferência; warm-up separado; repetições suficientes; sincronização; medição de RSS; artefato e pré-processamento incluídos; baseline de hardware; relatório de falhas. Só executar quando houver dispositivo físico representativo.

## Entregáveis

- Especificação de hardware/software e checklist de preparação.
- Formato de dados do benchmark e script futuro descrito, mas não implementado nesta entrega.
- Schema de resultados para latência, throughput, RSS, tamanho e equivalência.
- Critérios prévios de sucesso/insucesso, sem números inventados.

## Testes esperados

- Predições exportadas equivalem à referência dentro de tolerância definida.
- Medição exclui warm-up do sumário e reporta distribuição, não só média.
- Cada resultado identifica hardware, SO, runtime, threads, temperatura e artefato.
- Pré-processamento faz parte do caminho medido quando fizer parte do produto.

## Critérios de aceite

- Nesta versão existe apenas a especificação.
- Nenhuma frase afirma que o sistema roda em tempo real, cabe em memória ou é adequado ao Raspberry Pi.
- O protocolo pode ser executado sem decisões metodológicas pós-hoc.
- Resultados futuros distinguem tempo de modelo, pipeline completo e I/O.

## Perguntas de reflexão

- Qual unidade operacional define “tempo real” para o tráfego MQTT alvo?
- Medir batches grandes representa o fluxo online real?
- Como throttling térmico e processos concorrentes mudam p99?

## Decisões que devem ser registradas

Quando a tarefa for executada, registrar hardware/revisão, SO/runtime, formato exportado, tolerância, warm-up, repetições, threads, método de RSS/energia e critérios de sucesso definidos antes da medição.
