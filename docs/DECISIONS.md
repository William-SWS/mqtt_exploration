# Registro de decisões

Este documento é **append-only**. Cada decisão recebe um ID estável, data, status, decisão, evidência, alternativas e consequências. Para alterar uma decisão, adicione uma nova entrada que substitua explicitamente a anterior; não apague o histórico.

## ADR-001 — Primeira entrega documental

- **Data:** 2026-08-18
- **Status:** aceita
- **Decisão:** entregar apenas documentação, histórico Git local e esqueleto de diretórios.
- **Evidência:** a sequência pedagógica precisa explicitar o protocolo antes de cristalizá-lo em código.
- **Alternativas:** inicializar uv e escrever um pipeline mínimo já nesta entrega.
- **Consequências:** não haverá `pyproject.toml`, `uv.lock`, ambiente, notebook preenchido, código funcional ou modelo treinado.

## ADR-002 — Controle de versão local

- **Data:** 2026-08-18
- **Status:** aceita
- **Decisão:** inicializar Git local e registrar a entrega documental.
- **Evidência:** a trilha deve ensinar mudanças pequenas, auditáveis e reproduzíveis.
- **Alternativas:** adiar Git até o primeiro código.
- **Consequências:** dados, artefatos e segredos precisam estar ignorados antes do primeiro commit.

## ADR-003 — Idioma e nomes técnicos

- **Data:** 2026-08-18
- **Status:** aceita
- **Decisão:** documentação em PT-BR e código futuro em inglês.
- **Evidência:** melhora a acessibilidade da trilha sem divergir das APIs e convenções do ecossistema Python.
- **Alternativas:** todo o projeto em inglês ou todo em português.
- **Consequências:** módulos, funções, campos de configuração e testes usarão nomes ingleses.

## ADR-004 — Plataforma de execução

- **Data:** 2026-08-18
- **Status:** aceita
- **Decisão:** manter o pipeline agnóstico de provedor de nuvem e adiar Raspberry Pi.
- **Evidência:** não há benchmark físico nesta versão e alegações de edge sem medição seriam especulativas.
- **Alternativas:** otimizar desde o início para um provedor ou dispositivo específico.
- **Consequências:** latência de nuvem entra como desempate; edge terá somente uma especificação futura.

## ADR-005 — Publicação e proveniência dos dados

- **Data:** 2026-08-18
- **Status:** aceita
- **Decisão:** espelhar os três CSVs em um dataset Kaggle pessoal, primeiro privado e só depois público, com versão fixada, hashes, autores, DOI e CC BY 4.0.
- **Evidência:** a origem é o DOI `10.6084/m9.figshare.24420958`; a cópia local contém `Intrusion.csv`, `DoS.csv` e `MitM.csv`.
- **Alternativas:** usar somente arquivos locais, publicar imediatamente ou versionar apenas `Intrusion.csv`.
- **Consequências:** tokens ficam fora do Git; cada download será verificado por SHA-256; versões antigas não serão apagadas.

## ADR-006 — Política principal de features

- **Data:** 2026-08-18
- **Status:** aceita
- **Decisão:** usar um conjunto portável sem alvo, IP/MAC crus, client IDs, payloads, tópicos crus, timestamps absolutos, número do frame ou metadados de captura.
- **Evidência:** identificadores e ordem podem codificar o cenário de coleta e inflar artificialmente o desempenho.
- **Alternativas:** usar todas as 66 preditoras ou remover toda feature de rede.
- **Consequências:** derivações mínimas são permitidas; finalistas terão ablações separadas de identificadores e de ordem/tempo, fora da seleção principal.

## ADR-007 — Duplicatas e imutabilidade do raw

- **Data:** 2026-08-18
- **Status:** aceita
- **Decisão:** remover duplicatas exatas antes da divisão, preservando a primeira ocorrência, sem sobrescrever arquivos brutos.
- **Evidência:** a auditoria inicial encontrou 30 duplicatas exatas em `Intrusion.csv`.
- **Alternativas:** manter duplicatas ou removê-las independentemente dentro de cada split.
- **Consequências:** índices removidos e hashes de entrada/saída serão registrados.

## ADR-008 — Holdout temporal e CV agrupada

- **Data:** 2026-08-18
- **Status:** aceita
- **Decisão:** reservar os últimos 30% no tempo para teste e usar cinco folds de `StratifiedGroupKFold` no desenvolvimento, com blocos primários de 30 s.
- **Evidência:** frames próximos são correlacionados; uma divisão aleatória superestima generalização.
- **Alternativas:** holdout aleatório, CV aleatória ou validação puramente cronológica sem estratificação.
- **Consequências:** 10 s e 60 s serão sensibilidades dos finalistas; o holdout fica inacessível até o congelamento.

## ADR-009 — Ajustes dentro dos folds

- **Data:** 2026-08-18
- **Status:** aceita
- **Decisão:** imputação, encoding, scaling, SMOTENC e seleção de features serão ajustados exclusivamente no treino de cada fold.
- **Evidência:** ajustar transformações globalmente transmite informação da validação.
- **Alternativas:** gerar um CSV selecionado global antes da CV.
- **Consequências:** máscaras, nomes e frequência de seleção serão artefatos por fold; seletores terão CV interna de três folds quando necessário.

## ADR-010 — Modelos, seletores e regimes

- **Data:** 2026-08-18
- **Status:** aceita
- **Decisão:** comparar oito modelos, baseline sem seletor mais sete seletores, e três regimes mutuamente exclusivos: original, cost-sensitive e SMOTENC.
- **Evidência:** isso separa os efeitos de família de modelo, redução de dimensionalidade e desbalanceamento.
- **Alternativas:** uma única receita global ou SMOTE combinado com pesos.
- **Consequências:** haverá 192 configurações; “Lasso” e logística L1 são variantes distintas; o melhor seletor/regime será escolhido por modelo.

## ADR-011 — Objetivo e avaliação

- **Data:** 2026-08-18
- **Status:** aceita
- **Decisão:** otimizar Macro-F1 e avaliar tanto frames quanto eventos.
- **Evidência:** accuracy isolada é inadequada para 2,35% de positivos e o valor operacional depende da detecção de sequências de ataque.
- **Alternativas:** accuracy, ROC-AUC ou recall como objetivo único.
- **Consequências:** desempates usam recall de intrusão, log loss, latência e tamanho; todas as métricas obrigatórias serão reportadas.

## ADR-012 — Orçamento de otimização

- **Data:** 2026-08-18
- **Status:** aceita
- **Decisão:** executar 30 trials Optuna e cinco folds agrupados para o vencedor de cada um dos oito modelos.
- **Evidência:** orçamento moderado equilibra aprendizado, custo e comparação justa.
- **Alternativas:** busca exaustiva, um único estudo global ou orçamento desigual.
- **Consequências:** estudos serão persistentes e determinísticos quando possível; falhas de trials serão preservadas.

## ADR-013 — Tiny MLP e não inferioridade

- **Data:** 2026-08-18
- **Status:** aceita
- **Decisão:** usar PyTorch; a arquitetura 32–16 define a receita, que será congelada ao comparar 64–32, 32–16, 16–8, 8–4 e 4–2.
- **Evidência:** comparar tamanhos exige isolar capacidade de arquitetura de diferenças de treino.
- **Alternativas:** retunar cada tamanho independentemente ou usar outro framework.
- **Consequências:** selecionar a menor arquitetura dentro de um erro-padrão e com perda de recall ≤ 0,01; depois retunar somente ela. A saída é logit, com `BCEWithLogitsLoss` no treino e sigmoid apenas na inferência.

## ADR-014 — Calibração e limiar

- **Data:** 2026-08-18
- **Status:** aceita
- **Decisão:** calibrar apenas finalistas e reportar limiar 0,5 e limiar ajustado por previsões out-of-fold.
- **Evidência:** calibração e escolha de limiar também podem vazar informação do teste.
- **Alternativas:** calibrar todos os 192 candidatos ou ajustar limiar no holdout.
- **Consequências:** sigmoid/isotonic serão comparados no desenvolvimento; log loss e curva de calibração são obrigatórios.

## ADR-015 — Ensembles

- **Data:** 2026-08-18
- **Status:** aceita
- **Decisão:** avaliar um ensemble fixo DT+GB+MLP e um ensemble orientado pelos dados.
- **Evidência:** o fixo testa a hipótese inicial; o orientado a dados permite complementaridade mensurada.
- **Alternativas:** somente melhor modelo individual ou stacking irrestrito.
- **Consequências:** enumerar pares e trios com a melhor MLP e até dois modelos tradicionais; pesos não negativos, normalizados e ajustados apenas em OOF; empates por log loss e número de membros.

## ADR-016 — Configuração, registries e manifests

- **Data:** 2026-08-18
- **Status:** aceita
- **Decisão:** usar YAML validado, registries por nome e um manifesto em arquivos para cada execução.
- **Evidência:** configuração explícita e identidade estável permitem retomar, comparar e auditar execuções.
- **Alternativas:** parâmetros espalhados em notebooks, condicionais em scripts ou banco central obrigatório.
- **Consequências:** `yaml.safe_load`; campos desconhecidos/ausentes falham cedo; identidade inclui dataset, protocolo, features, regime, seletor, modelo e hash da configuração.

## ADR-017 — Incerteza estatística

- **Data:** 2026-08-18
- **Status:** aceita
- **Decisão:** estimar intervalos de 95% com 2.000 reamostragens por blocos temporais.
- **Evidência:** bootstrap de frames independentes ignora autocorrelação temporal.
- **Alternativas:** sem intervalos ou bootstrap IID.
- **Consequências:** tamanho e regra de construção dos blocos devem constar no manifesto e no relatório.

## ADR-018 — Bootstrap automático e ambiente único para scripts e notebooks

- **Data:** 2026-08-22
- **Status:** aceita
- **Decisão:** usar `uv run --locked` como porta de entrada de todo código executável. O projeto declara as dependências de produção, teste, lint e Jupyter no `pyproject.toml`; o `uv.lock` fixa suas versões. Scripts serão iniciados pelo comando de console `mqtt-ids` e notebooks por `uv run --locked --group notebook jupyter lab`, ambos criando ou sincronizando `.venv` automaticamente antes da execução.
- **Evidência:** o mesmo mecanismo elimina a instalação manual, permite iniciar o primeiro script ou notebook em um checkout limpo e mantém a instalação fiel ao lockfile. O runner mínimo valida YAML com `safe_load`, aceita estágios e retomada e grava manifesto com identidade determinística, configuração resolvida, seed, ambiente e status.
- **Alternativas:** exigir `uv sync --locked` manual antes de cada uso; instalar dependências dentro de scripts/notebooks; ou manter ambientes diferentes para CLI e Jupyter.
- **Consequências:** comandos executáveis devem ser documentados e chamados via `uv run --locked`; notebooks não instalam pacotes com `pip` nem contêm lógica de produção. O checkout reproduzível é sincronizado com `uv sync --locked` quando a instalação explícita for desejada; saídas continuam fora do Git.

## ADR-019 — Cobertura comportamental do runner mínimo

- **Data:** 2026-08-22
- **Status:** aceita
- **Decisão:** cobrir o runner por testes de comportamento usando `tmp_path`. A interface de linha de comando é exercitada em subprocesso para verificar cenário inválido, seleção de estágio, manifesto concluído e retomada; o runner é chamado diretamente para verificar identidade determinística e manifesto de falha. A validação de cenários YAML é parametrizada para cobrir arquivo ausente, chaves ausentes ou desconhecidas, valores inválidos e sintaxe YAML incorreta.
- **Evidência:** os critérios da issue 01 exigem falha antecipada da configuração, retomada, identidade determinística, manifesto autocontido e teste end-to-end sem depender de dados locais.
- **Alternativas:** validar somente por execução manual; testar apenas funções internas; ou usar arquivos persistentes dentro do repositório nos testes.
- **Consequências:** novos estágios, campos de cenário e resultados persistidos devem receber testes correspondentes. Testes não acessam dados brutos, credenciais ou artefatos reais e usam diretórios temporários descartáveis.

## ADR-020 — Catálogo de cenários de teste e manutenção orientada por agentes

- **Data:** 2026-08-22
- **Status:** aceita
- **Decisão:** manter `docs/testing/scenarios.md` como catálogo legível dos testes. Cada cenário registra o teste de origem, a entrada ou preparação, o resultado esperado e o comando de execução. O comando de agente `lint tests` inventaria os arquivos e funções em `tests/` e cria ou atualiza a documentação de testes ainda não catalogados antes da validação.
- **Evidência:** a suíte executável é precisa, mas não é suficiente como material de aprendizagem para quem está começando. Associar cada teste ao seu propósito permite conferir a cobertura da issue e localizar rapidamente o comando adequado.
- **Alternativas:** documentar testes somente em comentários no código; manter uma lista manual sem relação com os nomes dos testes; ou depender exclusivamente do relatório do pytest.
- **Consequências:** toda adição, remoção ou renomeação de teste requer atualização do catálogo. A documentação descreve comportamento esperado, mas não substitui a execução da suíte.
