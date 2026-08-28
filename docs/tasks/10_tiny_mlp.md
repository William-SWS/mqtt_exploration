# Task 10 — Tiny MLP em PyTorch

## Objetivo

Treinar uma MLP binária pequena e reproduzível, separar corretamente logits de probabilidades e escolher tamanho por não inferioridade, não apenas pelo melhor ponto estimado.

## Pré-requisitos

- Concluir a Task 09 e ler ADR-013.
- Ter pré-processamento leakage-safe e arrays OOF rastreáveis.
- Entender forward pass, minibatch, backpropagation e early stopping.

## Conceitos e APIs para estudar

- `torch.nn.Module`, camadas lineares/ativação e uma saída escalar sem sigmoid.
- `DataLoader`, shuffling apenas no treino, `Generator` e `worker_init_fn`.
- `BCEWithLogitsLoss(pos_weight=...)`, `torch.optim.Adam` e validação por época.
- `torch.inference_mode`, `torch.sigmoid`, `state_dict` e carregamento estrito.
- `torch.manual_seed`, seeds de Python/NumPy/workers e limites de determinismo.

## Exercício a implementar futuramente

Usar a arquitetura 32–16 para definir otimização, batch size, regularização e early stopping. Congelar a receita e comparar 64–32, 32–16, 16–8, 8–4 e 4–2 nos mesmos folds. Selecionar a menor arquitetura dentro de um erro-padrão da melhor e que não perca mais de 0,01 de recall absoluto da intrusão. Depois, retunar somente a arquitetura escolhida.

## Entregáveis

- Módulo MLP e loop de treino/validação testáveis fora de notebook.
- Receita congelada, curvas por fold/seed e checkpoints `state_dict`.
- Tabela de tamanhos, parâmetros, Macro-F1, recall, variabilidade e duração.
- Justificativa formal da regra de um erro-padrão e do limite de recall.

## Testes esperados

- Forward retorna shape correto e logits finitos, sem sigmoid embutido.
- `BCEWithLogitsLoss` recebe targets float em `[0,1]`; `pos_weight` vem só do treino.
- Inferência aplica sigmoid uma vez e produz probabilidades em `[0,1]`.
- Checkpoint recarregado reproduz outputs dentro da tolerância.
- Seeds e DataLoader reproduzem treino dentro das limitações registradas.
- A receita permanece idêntica na comparação de tamanhos.

## Critérios de aceite

- A menor arquitetura não inferior é escolhida pela regra predefinida.
- Nenhum tamanho, exceto o escolhido, é retunado após a comparação.
- Resultados distinguem variabilidade entre folds/seeds de diferença real.
- Holdout continua fechado.

## Perguntas de reflexão

- Por que sigmoid antes de `BCEWithLogitsLoss` é incorreto?
- “Menor dentro de um erro-padrão” favorece qual tipo de erro decisório?
- O que deve acompanhar um `state_dict` para ele ser reutilizável?

## Decisões que devem ser registradas

Registrar arquitetura/base recipe, inicialização, ativação, batch size, otimizador, early stopping, seeds, tolerâncias, cálculo do erro-padrão e arquitetura selecionada.
