# PRD — MQTT Intrusion IDS

## Problem Statement

Estudantes e profissionais que desejam construir um sistema de detecção de intrusão para tráfego MQTT encontram um problema maior do que simplesmente treinar um classificador: o dataset é altamente desbalanceado, contém duplicatas, colunas vazias, dependência temporal e identificadores de rede fortemente associados à classe. Uma exploração ingênua pode produzir métricas aparentemente excelentes por vazamento de identidade, ordem ou cenário de captura, sem demonstrar capacidade de generalização.

Também falta um caminho único que conecte aquisição verificável dos dados, auditoria, contrato de schema, limpeza imutável, divisão temporal, validação agrupada, pré-processamento dentro dos folds, comparação ampla de modelos, tuning controlado, calibração, escolha de limiar, ensembles e relato com incerteza. Sem esse caminho, decisões tendem a ficar dispersas em notebooks, resultados falhos desaparecem, o holdout é consultado cedo demais e experimentos não podem ser reproduzidos por outra pessoa.

O produto precisa, portanto, funcionar simultaneamente como pipeline experimental confiável e como trilha educacional. O usuário deve compreender por que cada proteção existe, executar cada etapa de forma reproduzível e produzir evidências auditáveis sem alegar desempenho em Raspberry Pi antes de medi-lo.

## Solution

Construir um projeto Python 3.12 reproduzível e agnóstico de nuvem para estudar e avaliar um MQTT Intrusion IDS. O produto será operado por um runner configurado por YAML, com estágios retomáveis e lógica reutilizável em uma biblioteca. Dados brutos serão obtidos de uma versão Kaggle fixada e validados por SHA-256; nunca serão sobrescritos.

O pipeline aplicará uma política principal de features portáveis, removerá duplicatas antes da divisão e reservará os últimos 30% no tempo como holdout intocado. Os primeiros 70% serão usados em validação agrupada por blocos temporais. Todas as transformações aprendidas, reamostragem e seleção de features ocorrerão dentro dos folds.

O screening comparará oito modelos, oito caminhos de features e três regimes de desbalanceamento, totalizando exatamente 192 registros, inclusive falhas. Em seguida, o sistema otimizará os vencedores por família, treinará e selecionará uma Tiny MLP por regra de não inferioridade, calibrará finalistas, ajustará limiares em previsões out-of-fold e avaliará ensembles fixo e orientado pelos dados. Somente após congelar toda a configuração o holdout será aberto uma vez.

O resultado final incluirá métricas por frame e por evento, intervalos de confiança por bootstrap temporal, manifests, model cards, artefatos versionados e ameaças à validade. A implantação edge permanecerá como protocolo de benchmark futuro até existir hardware representativo e medição real.

## User Stories

1. Como estudante de machine learning, quero uma sequência de trabalho explícita, para que eu aprenda o processo experimental sem pular diretamente para o treinamento.
2. Como mantenedor, quero um projeto Python 3.12 gerenciado por uv, para que dependências e comandos sejam reproduzíveis.
3. Como colaborador, quero separar dependências de runtime e desenvolvimento, para que o ambiente de produção não carregue ferramentas desnecessárias.
4. Como colaborador, quero um lockfile versionado e sincronização congelada, para que máquinas diferentes resolvam as mesmas versões.
5. Como desenvolvedor, quero o pacote organizado em layout `src`, para que imports acidentais do diretório de trabalho sejam detectados.
6. Como mantenedor, quero entrypoints pequenos chamando funções reutilizáveis, para que a lógica não fique duplicada em scripts.
7. Como pesquisador, quero notebooks restritos à exploração e comunicação, para que o pipeline não dependa de estado interativo.
8. Como mantenedor, quero dados, ambientes, caches, artefatos e credenciais ignorados pelo Git, para que o repositório permaneça seguro e leve.
9. Como colaborador, quero documentação em PT-BR e nomes de código em inglês, para que a trilha seja acessível sem divergir das convenções técnicas.
10. Como responsável pelos dados, quero registrar autores, DOI e licença do dataset, para que a atribuição e o direito de redistribuição sejam claros.
11. Como responsável pelos dados, quero espelhar os três CSVs em um dataset Kaggle pessoal inicialmente privado, para que integridade e metadata sejam revisados antes da publicação.
12. Como responsável pelos dados, quero autenticar no Kaggle sem versionar tokens, para que credenciais não sejam expostas.
13. Como pesquisador, quero fixar uma versão Kaggle no cenário experimental, para que a entrada não mude silenciosamente.
14. Como pesquisador, quero verificar SHA-256 após cada download, para que cache, rede ou atualização remota não alterem os dados usados.
15. Como auditor, quero manter versões Kaggle anteriores, para que resultados históricos continuem reconstruíveis.
16. Como analista, quero confirmar linhas, colunas, classes e duplicatas de `Intrusion.csv`, para que o contrato parta de fatos verificáveis.
17. Como analista, quero quantificar missingness, cardinalidade e colunas constantes ou vazias, para que problemas estruturais sejam tratados conscientemente.
18. Como analista, quero um dicionário cobrindo todas as colunas, para que tipo, significado e política de uso sejam explícitos.
19. Como pesquisador, quero visualizar a classe ao longo do tempo, para que concentração temporal e dependência entre frames sejam compreendidas.
20. Como pesquisador, quero cruzar identificadores, tópicos, payloads e ordem com o alvo, para que riscos de vazamento sejam sustentados por evidência.
21. Como revisor, quero distinguir exploração descritiva de transformação persistida, para que a EDA não modifique os dados de origem.
22. Como engenheiro de dados, quero um schema explícito com tipos e invariantes, para que entradas incompatíveis falhem cedo.
23. Como engenheiro de dados, quero validar campos obrigatórios e rejeitar campos desconhecidos da configuração, para que erros de digitação não alterem experimentos silenciosamente.
24. Como engenheiro de dados, quero coerções auditáveis, para que valores inválidos não desapareçam como ausentes sem registro.
25. Como pesquisador, quero remover duplicatas exatas preservando a primeira ocorrência, para que cópias de frames não atravessem divisões nem inflem métricas.
26. Como auditor, quero provar que o raw manteve hash e conteúdo, para que toda limpeza seja não destrutiva.
27. Como pesquisador, quero uma política principal sem IP/MAC crus, client IDs, payloads, tópicos crus, timestamps absolutos, número do frame e metadata de captura, para que o modelo principal seja mais portável.
28. Como pesquisador, quero permitir somente derivações mínimas aprovadas, para que sinais generalizáveis sejam usados sem reintroduzir identidade disfarçada.
29. Como pesquisador, quero duas ablações separadas para identificadores e ordem/tempo, para que o impacto do vazamento seja medido sem escolher o modelo principal.
30. Como auditor, quero que cada saída intermediária registre hashes e transformações, para que perdas e derivações sejam rastreáveis.
31. Como pesquisador, quero reservar os últimos 30% no tempo como teste, para que a avaliação simule generalização futura.
32. Como pesquisador, quero uma regra determinística para empates na fronteira temporal, para que o split seja reconstruível.
33. Como pesquisador, quero cinco folds estratificados e agrupados no desenvolvimento, para que prevalência e dependência temporal sejam tratadas conjuntamente.
34. Como pesquisador, quero grupos primários de 30 segundos, para que frames próximos não sejam distribuídos entre treino e validação.
35. Como revisor, quero análises de sensibilidade com blocos de 10 e 60 segundos apenas nos finalistas, para que robustez temporal seja avaliada sem ampliar o screening.
36. Como auditor, quero manifestos dos índices e grupos de cada fold, para que disjunção, cobertura e prevalência possam ser verificadas.
37. Como responsável experimental, quero impedir tecnicamente a leitura do holdout antes do congelamento, para que não exista feedback informal do teste.
38. Como engenheiro de ML, quero pré-processar colunas numéricas e categóricas em um pipeline único, para que fit e transform sejam aplicados consistentemente.
39. Como engenheiro de ML, quero ajustar imputação, encoding e scaling apenas no treino do fold, para que estatísticas de validação não vazem.
40. Como engenheiro de ML, quero nomes e ordem estáveis após transformação, para que seleção, manifests e explicação permaneçam alinhados.
41. Como pesquisador, quero comparar regime original, cost-sensitive e SMOTENC, para que estratégias de desbalanceamento sejam avaliadas separadamente.
42. Como pesquisador, quero `class_weight`, `sample_weight`, priors ou `pos_weight` conforme a capacidade de cada modelo, para que o regime cost-sensitive tenha semântica explícita.
43. Como pesquisador, quero SMOTENC somente dentro do treino do fold, para que amostras sintéticas não sejam influenciadas pela validação.
44. Como pesquisador, quero tornar SMOTENC e pesos mutuamente exclusivos, para que os efeitos dos regimes não sejam confundidos.
45. Como revisor, quero validar categorias após SMOTENC, para que a reamostragem não gere valores categóricos impossíveis.
46. Como engenheiro de ML, quero um registry com LDA, QDA, GaussianNB, SVC, Decision Tree, Random Forest, Gradient Boosting e Logistic Regression, para que modelos sejam construídos por nome e não por condicionais dispersos.
47. Como pesquisador, quero factories que produzam instâncias novas e registrem capacidades, para que estado e parâmetros não vazem entre execuções.
48. Como pesquisador, quero baselines sem tuning oportunista, para que melhorias posteriores tenham uma referência honesta.
49. Como auditor, quero preservar warnings e falhas numéricas, para que combinações difíceis não desapareçam dos resultados.
50. Como pesquisador, quero comparar um baseline sem seletor e sete seletores, para que o efeito da redução de features seja isolado.
51. Como pesquisador, quero tratar Lasso e Logistic Regression L1 como seletores distintos, para que hipóteses estatísticas diferentes não sejam fundidas.
52. Como pesquisador, quero seletores por variância, ANOVA F, informação mútua, Lasso, logística L1, LinearSVC e ExtraTrees, para que filtros e métodos embedded sejam comparados.
53. Como pesquisador, quero ajustar seletores supervisionados somente no treino externo, para que labels de validação não influenciem a máscara.
54. Como pesquisador, quero CV interna de três folds para parâmetros de seletores, para que a seleção permaneça aninhada à avaliação externa.
55. Como auditor, quero salvar máscara, nomes e frequência de seleção por fold, para que estabilidade e origem das features sejam inspecionáveis.
56. Como responsável experimental, quero executar o produto cartesiano de oito modelos, oito caminhos de features e três regimes, para que o screening seja completo.
57. Como responsável experimental, quero exatamente 192 registros de screening, para que nenhuma combinação seja omitida.
58. Como responsável experimental, quero status explícito para execuções pendentes, em andamento, concluídas e falhas, para que retomada e cobertura sejam auditáveis.
59. Como pesquisador, quero uma probabilidade OOF por linha de desenvolvimento em execuções concluídas, para que métricas, calibração e ensembles usem previsões honestas.
60. Como pesquisador, quero Macro-F1 como objetivo principal, para que ambas as classes tenham peso apesar do desbalanceamento.
61. Como pesquisador, quero desempatar por recall da intrusão, log loss, latência em nuvem e tamanho do artefato, para que decisões secundárias sejam determinísticas e operacionalmente relevantes.
62. Como analista, quero accuracy, precision da intrusão, weighted F1, F1/recall da intrusão, PR-AUC, ROC-AUC, FPR, log loss e matriz de confusão, para que desempenho não seja resumido por uma única métrica.
63. Como responsável experimental, quero retomar execuções sem duplicar resultados incompatíveis, para que interrupções não comprometam a matriz.
64. Como auditor, quero que cada execução tenha identidade derivada de dataset, protocolo, features, regime, seletor, modelo e configuração, para que colisões sejam evitadas.
65. Como pesquisador, quero escolher o melhor seletor e regime separadamente para cada modelo, para que uma receita global não prejudique famílias distintas.
66. Como pesquisador, quero otimizar os oito vencedores com orçamento igual, para que comparações de tuning sejam justas.
67. Como pesquisador, quero 30 trials Optuna e cinco folds agrupados por modelo, para que o orçamento seja moderado e predefinido.
68. Como responsável experimental, quero estudos persistentes e retomáveis, para que interrupções não descartem trials válidos.
69. Como pesquisador, quero espaços de busca específicos e condicionais, para que apenas hiperparâmetros aplicáveis sejam sugeridos.
70. Como auditor, quero distinguir trials completos, podados e falhos, para que o histórico do estudo não seja sanitizado.
71. Como pesquisador, quero uma Tiny MLP em PyTorch com saída logit, para que a função de perda seja numericamente estável.
72. Como pesquisador, quero usar `BCEWithLogitsLoss` no treino e sigmoid somente na inferência, para que a probabilidade seja calculada exatamente uma vez.
73. Como pesquisador, quero definir a receita de treino na arquitetura 32–16, para que comparação de tamanho isole capacidade arquitetural.
74. Como pesquisador, quero comparar 64–32, 32–16, 16–8, 8–4 e 4–2 com a mesma receita, para que a menor rede adequada seja identificada.
75. Como pesquisador, quero escolher a menor MLP dentro de um erro-padrão e com perda de recall de no máximo 0,01, para que compactação não sacrifique detecção de intrusão.
76. Como pesquisador, quero retunar somente a arquitetura não inferior escolhida, para que os demais tamanhos não recebam orçamento oportunista.
77. Como responsável por reprodutibilidade, quero controlar seeds do framework, NumPy, Python e DataLoader, para que variação estocástica seja conhecida.
78. Como responsável por modelos, quero salvar `state_dict` com metadata suficiente, para que o checkpoint seja recarregável e auditável.
79. Como pesquisador, quero calibrar somente finalistas, para que custo e multiplicidade sejam controlados.
80. Como pesquisador, quero comparar calibração sigmoid e isotonic sem reutilizar a amostra de avaliação, para que a qualidade calibrada não seja superestimada.
81. Como pesquisador, quero escolher limiar usando apenas probabilidades OOF, para que o holdout não determine a regra de decisão.
82. Como analista, quero reportar limiar 0,5 e limiar ajustado, para que o efeito da decisão operacional seja transparente.
83. Como analista, quero log loss e curva de calibração, para que a qualidade probabilística acompanhe a discriminação.
84. Como pesquisador, quero avaliar um ensemble fixo DT+GB+MLP, para que a hipótese inicial de complementaridade seja testada mesmo se não vencer.
85. Como pesquisador, quero enumerar pares e trios contendo a melhor MLP e até dois modelos tradicionais, para que o ensemble orientado pelos dados tenha escopo controlado.
86. Como pesquisador, quero pesos não negativos que somem um, para que soft voting permaneça interpretável.
87. Como pesquisador, quero otimizar pesos e limiar somente sobre OOF, para que membros não sejam retreinados durante a combinação.
88. Como pesquisador, quero desempatar ensembles por log loss e depois por menor número de membros, para que probabilidade e simplicidade decidam empates.
89. Como revisor, quero comparar o ensemble com cada membro no mesmo conjunto OOF, para que o ganho alegado seja justo.
90. Como responsável experimental, quero congelar features, regime, hiperparâmetros, calibrador, limiar e ensemble antes do teste, para que o holdout seja confirmatório.
91. Como auditor, quero registrar a abertura única do holdout, para que qualquer consulta ao teste seja rastreável.
92. Como analista, quero avaliar os últimos 30% por frame, para que o desempenho individual de classificação seja completo.
93. Como operador de segurança, quero agrupar sequências contíguas de intrusão em eventos, para que o resultado represente incidentes e não apenas frames.
94. Como operador de segurança, quero medir eventos detectados e tempo até o primeiro alerta, para que utilidade operacional seja avaliada.
95. Como operador de segurança, quero falsos alertas por 10.000 frames normais, para que o custo de monitoramento seja interpretável.
96. Como pesquisador, quero intervalos de 95% com 2.000 reamostragens por blocos temporais, para que incerteza respeite autocorrelação.
97. Como revisor, quero tabelas, figuras e model cards ligados aos manifests de origem, para que cada alegação seja rastreável.
98. Como colaborador, quero reproduzir o relatório em outra máquina usando lockfile, configuração e versão de dados, para que o resultado não dependa do ambiente original.
99. Como pesquisador, quero documentar ameaças à validade, para que limites de generalização para outras redes MQTT sejam explícitos.
100. Como mantenedor, quero modelos sklearn persistidos com Joblib e MLPs como `state_dict`, para que cada framework use um formato apropriado.
101. Como mantenedor, quero um teste end-to-end com amostra reduzida, para que a integração completa seja verificada com custo baixo.
102. Como usuário do pipeline, quero executar estágios selecionados e usar `--resume`, para que trabalhos longos possam ser retomados sem repetir etapas válidas.
103. Como usuário do pipeline, quero erros claros antes do treinamento para configuração ou dados inválidos, para que recursos não sejam gastos em cenários malformados.
104. Como auditor, quero configuração resolvida, versões, seed, features, parâmetros, métricas e status em cada manifesto, para que a execução seja autocontida.
105. Como operador futuro de edge, quero uma especificação de benchmark antes da medição, para que critérios não sejam escolhidos depois dos resultados.
106. Como operador futuro de edge, quero medir warm-up, p50/p95/p99, throughput, RSS, tamanho e inicialização, para que custo operacional seja caracterizado de forma completa.
107. Como operador futuro de edge, quero identificar hardware, SO, runtime, threads e temperatura, para que resultados de Raspberry Pi sejam interpretáveis.
108. Como revisor, quero equivalência numérica entre artefato exportado e referência, para que otimização de implantação não altere decisões silenciosamente.
109. Como revisor, quero separar latência do modelo, pipeline completo e I/O, para que gargalos sejam localizados.
110. Como leitor, quero que nenhuma alegação de tempo real ou adequação ao Raspberry Pi apareça antes de medições físicas, para que o projeto não apresente conclusões especulativas.

## Implementation Decisions

- O produto será um pacote Python 3.12 gerenciado por uv, com lockfile versionado, layout `src` e dependências de desenvolvimento separadas das dependências de execução.
- Documentação e material educacional serão escritos em PT-BR; módulos, APIs, campos de configuração e identificadores de código serão escritos em inglês.
- A lógica reutilizável residirá na biblioteca. Scripts serão entrypoints finos e não chamarão outros scripts por subprocesso. Notebooks serão usados para exploração e apresentação, não como dependência do pipeline.
- O runner terá a interface conceitual `run_pipeline --config <scenario> --stages <stages> --resume` e executará funções Python por estágio.
- A configuração YAML declarará fonte e versão Kaggle, hashes, alvo, classe positiva, políticas de features, split, seletores, modelos, regimes de desbalanceamento, métricas e seeds.
- O YAML será carregado com modo seguro e validado estritamente. Campos obrigatórios ausentes, campos desconhecidos ou valores incompatíveis causarão erro antes de carregar dados para treinamento.
- Configurações serão resolvidas e canonicalizadas antes do hash. A identidade de execução combinará versão dos dados, protocolo, política de features, regime, seletor, modelo e hash da configuração.
- O dataset Kaggle conterá os três CSVs, será criado como privado e só poderá ser tornado público após revisão manual de atribuição e integridade. O metadata registrará autores, DOI e licença `CC-BY-4.0`.
- Credenciais Kaggle permanecerão externas ao repositório. O pipeline exigirá um handle com versão explícita e verificará SHA-256 depois do download, inclusive quando houver cache.
- Dados raw serão imutáveis. Limpeza produzirá novos artefatos intermediários e registrará hashes, schema, contagens e transformações.
- Duplicatas exatas serão removidas antes da divisão, com preservação determinística da primeira ocorrência. A ordem usada nessa decisão será explicitamente definida.
- A política principal de features excluirá alvo, IP/MAC crus, client IDs, payloads, tópicos crus, timestamps absolutos, número do frame e metadados de captura. Apenas derivações mínimas aprovadas, como direção privado/público, flags de porta MQTT, presença de campos e quantidade de campos preenchidos, serão elegíveis.
- Identificadores e ordem/tempo serão reintroduzidos somente em duas ablações de finalistas. Resultados dessas ablações não poderão alterar a escolha principal.
- O holdout será formado pelos últimos 30% após limpeza e deduplicação. Os primeiros 70% serão desenvolvimento. A regra para timestamps empatados deverá manter ordenação e disjunção determinísticas.
- A validação de desenvolvimento usará cinco folds de `StratifiedGroupKFold` com grupos temporais primários de 30 segundos. Blocos de 10 e 60 segundos serão sensibilidades exclusivas dos finalistas.
- O acesso ao holdout terá uma trava de estado. O desbloqueio exigirá configuração final congelada e produzirá registro auditável.
- Imputação, encoding, scaling, SMOTENC e seleção supervisionada serão componentes de pipeline ajustados somente no treino de cada fold.
- Serão suportados três regimes mutuamente exclusivos: original, cost-sensitive e SMOTENC. SMOTENC jamais será combinado com pesos de classe.
- O regime cost-sensitive usará `class_weight="balanced"` quando disponível, `sample_weight` no Gradient Boosting, priors 0,5/0,5 em LDA/QDA/GNB e `pos_weight` na MLP.
- Um registry de modelos construirá LDA, QDA, GaussianNB, SVC, Decision Tree, Random Forest, Gradient Boosting e Logistic Regression por nome e declarará capacidades como probabilidades, pesos, esparsidade e necessidade de escala.
- Um registry de seletores construirá VarianceThreshold, ANOVA F, informação mútua, Lasso, Logistic Regression L1, LinearSVC L1 e ExtraTrees. O caminho sem seletor será explícito. Lasso e logística L1 permanecerão variantes diferentes.
- Parâmetros de seletores supervisionados serão escolhidos por três folds internos agrupados. Nenhuma matriz global de features selecionadas será persistida.
- O screening gerará o produto cartesiano de oito modelos, oito caminhos de features e três regimes. A tabela terá exatamente 192 registros, incluindo configurações falhas.
- Execuções terão estados `pending`, `running`, `completed` ou `failed`. Falhas preservarão tipo, mensagem e contexto suficiente; retomada será idempotente e não reutilizará artefato de identidade incompatível.
- A previsão OOF será alinhada ao índice original de desenvolvimento e terá exatamente uma predição de validação por linha para cada execução completa.
- Macro-F1 será o objetivo principal. Desempates seguirão recall da intrusão, log loss, latência comparável em nuvem e tamanho do artefato.
- O conjunto obrigatório de métricas conterá accuracy, precision da intrusão, weighted F1, Macro-F1, F1 da intrusão, recall da intrusão, PR-AUC, ROC-AUC, FPR, log loss, matriz de confusão e curva de calibração.
- O melhor caminho de features e regime será selecionado separadamente para cada um dos oito modelos antes do tuning.
- Cada vencedor tradicional receberá um estudo Optuna persistente de 30 trials com TPE seeded e cinco folds agrupados dentro do objetivo. Espaços de busca serão específicos e condicionais. Trials completos, podados e falhos permanecerão no histórico.
- A MLP será implementada em PyTorch e retornará um logit escalar. O treino usará `BCEWithLogitsLoss`; sigmoid será aplicado apenas em inferência.
- A arquitetura 32–16 definirá a receita de treino. Essa receita será congelada ao comparar 64–32, 32–16, 16–8, 8–4 e 4–2.
- A MLP escolhida será a menor dentro de um erro-padrão da melhor e cuja perda absoluta de recall de intrusão não exceda 0,01. Somente essa arquitetura será retunada.
- Reprodutibilidade da MLP abrangerá seeds de Python, NumPy, PyTorch e DataLoader. Checkpoints usarão `state_dict` e metadata separada de arquitetura, pré-processamento e versões.
- Calibração será restrita aos finalistas. Sigmoid e isotonic serão comparados com separação adequada entre ajuste e avaliação. O método e o limiar serão escolhidos apenas em OOF.
- Todas as avaliações preservarão o limiar padrão 0,5 e o limiar ajustado; nenhum substituirá silenciosamente o outro.
- Haverá um ensemble fixo DT+GB+MLP e um ensemble orientado pelos dados. Este enumerará pares e trios contendo a melhor MLP e até dois modelos tradicionais.
- Pesos de ensemble serão não negativos e normalizados para soma um. Pesos e limiar serão otimizados somente sobre probabilidades OOF já produzidas, sem retreinar os membros.
- Empates entre ensembles seguirão a ordem global, depois log loss e menor número de membros quando aplicável.
- Depois de congelar seletor, regime, hiperparâmetros, calibrador, limiar e composição, os modelos serão ajustados no desenvolvimento completo e avaliados uma única vez no holdout temporal.
- A avaliação por evento agrupará sequências contíguas rotuladas como intrusão e reportará eventos detectados, tempo até primeiro alerta e falsos alertas por 10.000 frames normais.
- Intervalos de confiança de 95% usarão 2.000 reamostragens por blocos temporais. Construção/tamanho dos blocos e seed integrarão o manifesto.
- Cada execução salvará manifesto JSON, configuração resolvida, hashes, versões, seed, features selecionadas, parâmetros, métricas, status e referências a artefatos. Modelos sklearn usarão Joblib; MLPs usarão `state_dict`.
- O produto permanecerá agnóstico de nuvem. Latência em nuvem só entrará no desempate quando as medições forem comparáveis.
- Raspberry Pi não faz parte da implementação desta versão. Será produzida apenas uma especificação de benchmark que fixe hardware, software, warm-up, repetições, latência, throughput, RSS, tamanho e equivalência antes da execução futura.
- O registro de decisões continuará append-only. Mudanças criarão novas decisões que substituem explicitamente as anteriores, preservando o histórico.

## Testing Decisions

- A principal seam de teste será o runner completo, executado com uma configuração reduzida e dados sintéticos/recortados conhecidos. Esse teste verificará do carregamento validado ao manifesto final sem depender de resultados previamente gerados.
- Testes observarão comportamento externo, arquivos produzidos, erros, métricas e invariantes. Não deverão acoplar-se à ordem interna de chamadas ou a detalhes privados de implementação.
- Uma seam complementar de contrato cobrirá configuração e dados, pois falhas precisam ocorrer antes do treinamento. Casos incluirão campo obrigatório ausente, campo desconhecido, hash divergente, coluna ausente/extra, tipo incoercível e versão Kaggle não fixada.
- O projeto ainda não possui código ou testes anteriores. Os critérios definidos nas tarefas educacionais e as ADRs são a fonte de prior art até que os primeiros testes criem padrões reutilizáveis.
- A reprodutibilidade do ambiente será testada com sincronização congelada e importação do pacote em um checkout limpo.
- Segurança do repositório será testada verificando que dados, modelos, bancos, ambientes e padrões de credenciais não são rastreados.
- Proveniência será testada contra nomes, tamanhos e hashes conhecidos dos três CSVs. Falta de autenticação ou corrupção deverá interromper a aquisição com mensagem acionável.
- A EDA será validada por contratos de contagem, classes, duplicatas e cobertura do dicionário; ela não poderá alterar hash ou mtime do raw.
- Limpeza será testada por idempotência, preservação da primeira duplicata, imutabilidade do raw, coerção explícita e ausência das features proibidas no conjunto portável.
- Splits serão testados por cobertura e disjunção de índices, ordem cronológica do holdout, ausência de grupo compartilhado e exatamente uma validação OOF por linha de desenvolvimento.
- A trava do holdout terá testes negativos demonstrando que labels e features não podem ser lidos antes do congelamento, inclusive por estágios de screening, tuning, calibração e ensemble.
- Pipelines de pré-processamento terão spies ou estimadores sentinela no nível público de `fit/transform` para provar que validação não chega a `fit`, sem testar detalhes das bibliotecas subjacentes.
- SMOTENC será testado quanto ao uso apenas no treino, categorias válidas, prevalência configurada e exclusão mútua com pesos.
- Registries serão testados por conjunto exato de nomes, construção de instâncias independentes, parâmetros efetivos e declaração consistente de capacidades.
- Seletores serão testados por oito caminhos totais, distinção entre Lasso e logística L1, alinhamento de máscara/nome e falha explícita ao selecionar zero features.
- O screening será testado por cardinalidade de 192 identidades únicas. Casos falhos continuarão presentes com status e motivo.
- Métricas serão testadas em pequenos vetores com resultados calculáveis manualmente, incluindo matriz de confusão, FPR, PR-AUC, ROC-AUC e log loss.
- Toda probabilidade será validada como finita e pertencente a `[0,1]`; todo vetor OOF será testado por índice e classe verdadeira correspondentes.
- Retomada será testada interrompendo uma execução e verificando que artefatos completos são reutilizados, parciais são tratados pela política e identidades divergentes não colidem.
- Estudos Optuna serão testados com orçamento reduzido para persistência, retomada, ramos condicionais, seed e contabilização de estados, reservando os 30 trials para execução experimental real.
- A MLP será testada quanto a shape/logit, targets, aplicação única de sigmoid, cálculo de `pos_weight` no treino, checkpoint round-trip e determinismo dentro da tolerância documentada.
- A regra de não inferioridade será testada com tabelas artificiais que exercitem empate, um erro-padrão, limite exato de 0,01 de recall e rejeição por perda superior.
- Calibração será testada por separação de amostras, preservação de 0,5, determinismo do limiar e comparação transparente mesmo quando piorar a métrica principal.
- Ensembles serão testados por pesos finitos/não negativos, soma unitária, reprodução por peso unitário, enumeração válida de pares/trios e alinhamento das matrizes OOF.
- Métricas por evento serão testadas com sequências artificiais cobrindo início/fim de captura, eventos adjacentes, evento não detectado, múltiplos alertas e cálculo do primeiro alerta.
- Bootstrap será testado por exatamente 2.000 reamostragens, unidade de bloco correta, seed registrada e limites de intervalo coerentes em exemplos controlados.
- Manifests serão validados por schema e completude; cada tabela, figura, modelo e estudo deverá apontar para uma identidade de execução existente.
- Artefatos Joblib e `state_dict` terão testes de ida e volta que comparam predições com a referência dentro de tolerâncias explícitas.
- As duas ablações serão testadas para garantir que só rodam em finalistas, permanecem rotuladas como diagnóstico e não alteram a configuração principal congelada.
- A especificação edge terá revisão estática: nenhuma métrica real ou afirmação de adequação poderá existir antes de uma execução identificada em hardware físico.

## Out of Scope

- Implementar um broker MQTT, coletor de pacotes, firewall, IPS ativo ou resposta automatizada a incidentes.
- Tratar `DoS.csv` e `MitM.csv` como alvos adicionais na primeira análise modelada; eles integram proveniência e espelho, mas a experiência principal inicial usa `Intrusion.csv`.
- Modificar, normalizar ou substituir os arquivos brutos de origem.
- Usar identificadores, payloads, tópicos crus ou ordem absoluta no modelo principal.
- Usar as ablações de vazamento para escolher modelo, seletor, regime, hiperparâmetros, calibrador, limiar ou ensemble.
- Criar datasets globais já imputados, reamostrados ou selecionados antes da validação.
- Combinar SMOTENC com pesos de classe no mesmo regime.
- Consultar o holdout durante EDA orientada a modelos, screening, tuning, escolha da MLP, calibração, limiar ou ensemble.
- Otimizar todos os 192 candidatos; somente o vencedor por família recebe o estudo de 30 trials.
- Retunar individualmente todas as arquiteturas MLP depois da comparação congelada.
- Adotar stacking irrestrito ou ensembles que não contenham a melhor MLP na busca orientada pelos dados.
- Vincular a solução a um provedor de nuvem específico.
- Criar dashboard, serviço web, API online, monitoramento de produção ou integração SIEM nesta versão.
- Publicar automaticamente o dataset Kaggle como público; a mudança de visibilidade exige revisão e ação manual.
- Executar benchmark Raspberry Pi, exportar para edge ou afirmar tempo real, consumo, memória ou adequação de hardware nesta versão.

## Further Notes

- A fonte é o *MQTT Under Attack Dataset*, DOI `10.6084/m9.figshare.24420958`, sob CC BY 4.0.
- A cópia local conhecida de `Intrusion.csv` tem 80.893 frames, 67 colunas incluindo o alvo, 1.898 intrusões (2,35%) e 30 duplicatas exatas. Esses valores são contratos a confirmar, não resultados de modelo.
- Hashes observados: `Intrusion.csv` — `730f65a2bd388b973f7088a28b8a37a3a0a56062ad059d90e95da9fffed93518`; `DoS.csv` — `e935c819f8bc08898135180029bde0a685e9c5676d5277cacf66d917bb98d4e1`; `MitM.csv` — `bfee47413bcf82f3b1433d51db63629a1b61d1a40fc704f545f23c7350daa5d0`.
- A implementação deve seguir a ordem educacional dos fundamentos até o relatório; a especificação edge vem por último e não bloqueia a entrega científica em nuvem.
- O critério de produto não é apenas obter Macro-F1 alto. O resultado precisa demonstrar ausência de vazamento conhecido, rastreabilidade, incerteza, comportamento por evento e capacidade de reprodução.
- Decisões futuras encontradas durante a implementação devem ser acrescentadas ao registro append-only antes de alterar o contrato experimental.
