# Congelar o experimento e produzir o relatório no holdout

## What to build

Implementar o fechamento experimental: validar o selo de congelamento, ajustar finalistas no desenvolvimento completo, abrir uma única vez o último 30% e produzir métricas por frame e evento, intervalos por bootstrap temporal, figuras, tabelas, model cards e ameaças à validade. Executar as ablações de identificadores e ordem/tempo apenas como diagnóstico dos finalistas.

## What to study

- Avaliação confirmatória, uso único do holdout e prevenção de feedback informal.
- Definição de eventos contíguos, primeiro alerta e falsos alertas normalizados.
- Bootstrap por blocos temporais, autocorrelação e intervalos percentis.
- Model cards, rastreabilidade de artefatos e ameaças à validade externa.

## Recommended tools and libraries

- scikit-learn para métricas, matrizes e persistência Joblib.
- pandas/NumPy para eventos e bootstrap; Matplotlib/Seaborn para figuras.
- PyTorch para recarregar o `state_dict` final.
- pytest para sequências artificiais de eventos, bootstrap, trava e e2e reduzido.

## Acceptance criteria

- [ ] O holdout só abre após validar configuração congelada e gera registro auditável de abertura.
- [ ] São reportadas todas as métricas obrigatórias nos limiares 0,5 e ajustado.
- [ ] Eventos detectados, tempo até primeiro alerta e falsos alertas/10.000 frames normais passam por casos artificiais de borda.
- [ ] Intervalos de 95% usam exatamente 2.000 reamostragens por blocos com seed e regra registradas.
- [ ] Sensibilidades de 10/60 segundos e duas ablações só rodam em finalistas e não alteram a seleção principal.
- [ ] Tabelas, figuras, modelos e model cards referenciam manifests e hashes existentes.
- [ ] Um checkout limpo reproduz o relatório pelo runner e há ameaças à validade explícitas.

## Blocked by

- {{ISSUE_14}}

## User stories covered

29, 35 e 90–104.
