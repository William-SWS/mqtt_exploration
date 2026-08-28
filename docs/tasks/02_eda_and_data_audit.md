# Task 02 — EDA e auditoria dos dados

## Objetivo

Compreender estrutura, qualidade, desbalanceamento, dependência temporal e risco de vazamento de `Intrusion.csv` antes de transformar ou modelar os dados.

## Pré-requisitos

- Concluir as Tasks 00–01 e ler ADR-006 e ADR-007.
- Verificar hash da entrada e carregar somente de `data/raw`.
- Conhecer tipos numéricos/categóricos e estatística descritiva básica.

## Conceitos e APIs para estudar

- `pandas.read_csv`, `DataFrame.info`, `describe`, `nunique`, `isna`, `duplicated`, `value_counts` e `crosstab`.
- Matplotlib/Seaborn para distribuições, missingness, classe ao longo do tempo e associações.
- Cardinalidade, colunas constantes/vazias, duplicatas exatas, classes raras e dependência entre identificadores e alvo.
- Diferença entre exploração descritiva e transformação persistida.

## Exercício a implementar futuramente

Criar `notebooks/00_eda_and_cleaning.ipynb` como narrativa executável. Confirmar 80.893 linhas, 67 colunas, 1.898 intrusões, 30 duplicatas e a lista de colunas totalmente vazias. Produzir um dicionário de dados e classificar cada feature como portável, excluída, derivável ou reservada para ablação. Visualizar a distribuição temporal e cruzar IP, MAC, client ID, tópico, payload e ordem com o alvo.

## Entregáveis

- Notebook reiniciável e executável do início ao fim.
- Dicionário de dados com tipo observado, missingness, cardinalidade e política.
- Relatório de risco de vazamento com evidências, não apenas uma lista de suspeitas.
- Figuras legíveis sem depender do estado interativo do notebook.

## Testes esperados

- Contagem de linhas, colunas, classes e duplicatas coincide com o contrato conhecido.
- Soma das classes coincide com o número de linhas antes da deduplicação.
- Toda coluna aparece exatamente uma vez no dicionário.
- O notebook não grava nem modifica o raw.

## Critérios de aceite

- Números iniciais são confirmados ou divergências são explicadas pelo hash/versão.
- Colunas 100% vazias, constantes e identificadoras são explicitamente marcadas.
- O risco de vazamento temporal e por identidade está sustentado por tabelas ou gráficos.
- Não há treinamento ou escolha de modelo nesta tarefa.

## Perguntas de reflexão

- Uma associação quase perfeita entre IP e classe representa sinal operacional ou cenário de coleta?
- Por que uma coluna completamente vazia ainda importa para o contrato?
- Que visualização evidencia melhor concentração temporal dos ataques?

## Decisões que devem ser registradas

Registrar a taxonomia de colunas, divergências dos números esperados, definição exata do alvo positivo, regra de ordenação e qualquer derivação proposta para a política portável.
