# Especificar o benchmark edge futuro

## What to build

Produzir uma especificação executável no futuro para benchmark em Raspberry Pi, fixando previamente hardware, SO, runtime, threads, warm-up, repetições, dataset, equivalência numérica, latência, throughput, RSS, tamanho, temperatura e formato de relato. Esta issue não executará benchmarks nem afirmará adequação ao edge.

## What to study

- Exportação Joblib, TorchScript ou ONNX e equivalência com a referência.
- Warm-up, p50/p95/p99, throughput e distinção entre modelo, pipeline e I/O.
- RSS, inicialização, afinidade, frequência, throttling térmico e concorrência.
- Critérios definidos antes da medição e limitações de generalizar hardware.

## Recommended tools and libraries

- `time.perf_counter_ns` ou pyperf para medições repetíveis futuras.
- psutil para RSS/processo; ferramentas do SO para frequência e temperatura.
- ONNX Runtime somente se houver decisão futura de exportar; não adotá-lo antecipadamente.
- NumPy/pytest para testes futuros de equivalência numérica e schema de resultados.

## Acceptance criteria

- [ ] A especificação identifica todos os campos obrigatórios de hardware e software.
- [ ] Warm-up é separado das medições e o resultado exige distribuição p50/p95/p99, não apenas média.
- [ ] Modelo isolado, pipeline completo e I/O têm medições distinguíveis.
- [ ] Pré-processamento entra no caminho medido quando fizer parte do produto.
- [ ] Equivalência numérica e critérios de sucesso são definidos antes de qualquer resultado.
- [ ] Não existe afirmação de tempo real, memória suficiente ou adequação ao Raspberry Pi.
- [ ] Nenhum benchmark é executado nesta issue.

## Blocked by

- {{ISSUE_15}}

## User stories covered

105–110.
