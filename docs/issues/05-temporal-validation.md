# Criar o holdout temporal e os folds agrupados

## What to build

Adicionar um estágio que reserve os últimos 30% como holdout, construa cinco folds de desenvolvimento estratificados e agrupados em blocos temporais de 30 segundos e produza manifests de índices, tempos, grupos, prevalência e cobertura. Implementar uma trava que impeça qualquer estágio experimental de abrir o holdout antes do congelamento final.

## What to study

- Generalização temporal, autocorrelação e diferença entre split aleatório e cronológico.
- `StratifiedGroupKFold`, limitações da estratificação sob restrições de grupos e inspeção de folds.
- Regras determinísticas para timestamps empatados e fronteiras de bloco.
- Controles técnicos contra avaliação repetida no holdout.

## Recommended tools and libraries

- scikit-learn para `StratifiedGroupKFold`.
- pandas/NumPy para ordenação, blocos temporais e invariantes de índices.
- Pandera para validar manifests de split.
- pytest para disjunção, cobertura, ordem e testes negativos da trava.

## Acceptance criteria

- [ ] Desenvolvimento e teste são disjuntos, cobrem todas as linhas válidas e respeitam a regra temporal documentada.
- [ ] O teste contém os últimos 30% sob uma política determinística de empates.
- [ ] Nenhum grupo de 30 segundos atravessa treino e validação dentro de um fold.
- [ ] Cada linha de desenvolvimento aparece exatamente uma vez em validação OOF.
- [ ] Cada fold registra classes, prevalência, grupos e intervalo temporal; impossibilidades de estratificação são explícitas.
- [ ] Tentativas de ler features ou labels do holdout antes do congelamento falham.
- [ ] A definição permite sensibilidades futuras de 10 e 60 segundos sem alterar o screening.

## Blocked by

- {{ISSUE_04}}

## User stories covered

31–37.
