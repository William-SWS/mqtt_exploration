# Treinar e selecionar a Tiny MLP não inferior

## What to build

Adicionar ao runner um estimador PyTorch binário completo, inicialmente 32–16, com treino, validação, early stopping, inferência probabilística e checkpoint. Congelar a receita e comparar 64–32, 32–16, 16–8, 8–4 e 4–2 nos mesmos folds; selecionar a menor arquitetura dentro de um erro-padrão e com perda absoluta de recall limitada a 0,01, retunando apenas a escolhida.

## What to study

- `nn.Module`, logits, minibatches, backpropagation, Adam e early stopping.
- Estabilidade numérica de BCEWithLogitsLoss e significado de `pos_weight`.
- Reprodutibilidade de DataLoader e limites entre versões, plataformas, CPU e GPU.
- Regra de um erro-padrão, não inferioridade e trade-off recall/tamanho.

## Recommended tools and libraries

- PyTorch para modelo, DataLoader, loss, Adam, `inference_mode` e `state_dict`.
- NumPy/pandas para integração OOF e tabela comparativa.
- Optuna somente para a retunagem da arquitetura selecionada.
- pytest para shape/logit, sigmoid única, seeds, checkpoint round-trip e regra de seleção.

## Acceptance criteria

- [ ] Forward retorna um logit finito por amostra e não contém sigmoid.
- [ ] Treino usa BCEWithLogitsLoss; `pos_weight` é calculado somente com o treino do fold.
- [ ] Inferência usa `inference_mode`, aplica sigmoid uma vez e gera probabilidades válidas.
- [ ] Seeds de Python, NumPy, PyTorch e workers são registradas; limites de determinismo são documentados.
- [ ] As cinco arquiteturas usam receita idêntica durante a comparação.
- [ ] A menor não inferior respeita um erro-padrão e perda de recall ≤ 0,01; só ela é retunada.
- [ ] `state_dict` recarregado reproduz outputs dentro da tolerância junto da metadata necessária.

## Blocked by

- {{ISSUE_11}}

## User stories covered

71–78.
