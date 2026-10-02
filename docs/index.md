# Curso MQTT Intrusion IDS

## O que você vai construir

Um sistema de detecção de intrusão em tráfego MQTT: o problema vai além de treinar um classificador, porque o dataset é muito desbalanceado, tem duplicatas e colunas vazias, e identificadores de rede podem inflar as métricas por vazamento. Ao final do projeto você terá um pipeline reproduzível — configuração YAML, dados com proveniência verificada, validação temporal, oito modelos comparados, calibração e relatório no holdout — cujas decisões você consegue defender.

Este curso percorre esse caminho **uma issue por vez**, explicando o código que já existe no repositório e o porquê de cada escolha.

## Para quem é este curso

Para quem já programa em Python e conhece machine learning, mas quer revisar os fundamentos e os tópicos avançados **como se fosse do zero**, para fixar. Nada da stack de engenharia (uv, YAML seguro, manifestos, integridade de dados) é assumido.

O objetivo: projeto de pesquisa que também é portfólio. Cada aula termina com algo que você executa e consegue explicar a quem avaliar o trabalho.

O que você precisa: um computador, tempo e disposição para rodar os comandos e responder às perguntas antes de olhar as respostas.

## Como usar este curso

1. Responda às perguntas de **Relembrando** de memória.
2. Leia a aula.
3. Rode os comandos no seu terminal e compare com a **Saída esperada**.
4. Resolva os **Exercícios** até o teste ficar verde, tentando antes de abrir a solução.
5. Responda ao **Quiz** antes de abrir as respostas.
6. Faça o commit sugerido.
7. Volte e conte como foi (`/mkdocs-project-course progresso`): isso molda a próxima aula.

Por quê: recordar com esforço fixa muito mais do que reler, e rodar o código você mesmo mostra o que a leitura esconde.

!!! note "O código já existe"

    Nas issues 01 e 02 o código está pronto em `src/` e `tests/`. As aulas o mostram, trecho a trecho, e você o executa e o altera em exercícios. Os exercícios usam arquivos próprios — testes em `tests/test_exercicio_*.py` e soluções em `src/mqtt_ids/exercicios.py` — para não mexer no que já foi escrito. Esses arquivos são seus: guarde ou apague quando quiser.

## Como ler os blocos de código

- O **título** do bloco é o caminho do arquivo.
- Os marcadores **(+)** abrem uma anotação que explica a linha e o porquê da escolha.
- Comandos aparecem em blocos `$ Execução no terminal`; a saída vem em outro bloco, `Saída esperada`. Linhas que dependem da máquina (caminhos, versões, tempos) aparecem abreviadas com `...`.
- O botão de copiar fica no canto do bloco.

## Pré-requisitos gerais

Sistema Linux, macOS ou Windows, conexão com a internet e um editor de texto. A instalação das ferramentas é ensinada dentro das aulas.

## Mapa das aulas

| Aula | O que você constrói | Ticket | Status |
|---|---|---|---|
| [01-1 Ambiente e pacote](01-1-ambiente-e-pacote.md) | Ambiente reproduzível com `uv` e o pacote `mqtt_ids` | [01](issues/01-project-runner.md) | escrita |
| [01-2 Cenário YAML](01-2-cenario-yaml.md) | Carregamento seguro e validação de cenário | [01](issues/01-project-runner.md) | escrita |
| [01-3 Runner e manifesto](01-3-runner-e-manifesto.md) | Execução com identidade determinística e manifesto | [01](issues/01-project-runner.md) | escrita |
| [02-1 Handles e SHA-256](02-1-handles-e-sha256.md) | Handles versionados e integridade verificada | [02](issues/02-kaggle-ingestion.md) | escrita |
| [02-2 Aquisição atômica](02-2-aquisicao-atomica.md) | Estágio `acquire` com promoção atômica e reuso | [02](issues/02-kaggle-ingestion.md) | escrita |
| [02-3 Publicar e recuperar](02-3-publicar-e-recuperar.md) | Dataset e Model versionados no Kaggle | [02](issues/02-kaggle-ingestion.md) | escrita |
| [03-1 O MQTT e os três ambientes](03-1-mqtt-e-os-tres-ambientes.md) | Tipos de pacote MQTT por classe nos três ambientes | [03](issues/03-data-audit.md) | escrita |
| [03-2 Carga segura e contrato](03-2-carga-segura-e-contrato.md) | Leitura verificada e contagens do contrato | [03](issues/03-data-audit.md) | escrita |
| [03-3 Missingness e dicionário](03-3-missingness-e-dicionario.md) | Perfil de colunas conferido contra o dicionário | [03](issues/03-data-audit.md) | escrita |
| [03-4 DoS: inundação](03-4-dos-inundacao.md) | Rajadas, taxa de frames e anatomia do DoS | [03](issues/03-data-audit.md) | escrita |
| [03-5 MitM: tráfego alterado](03-5-mitm-trafego-alterado.md) | O ataque que quase não aparece no MQTT | [03](issues/03-data-audit.md) | escrita |
| [03-6 Intrusion: cliente desconhecido](03-6-intrusion-cliente-desconhecido.md) | A sequência de pacotes do intruso | [03](issues/03-data-audit.md) | escrita |
| [03-7 Vazamento](03-7-vazamento-identidade-conteudo-ordem.md) | Identidade, conteúdo e ordem contra o alvo | [03](issues/03-data-audit.md) | escrita |
| [03-8 Estágio `audit`](03-8-estagio-audit.md) | Estágio do runner com manifesto e figuras | [03](issues/03-data-audit.md) | escrita |
| [03-9 Política de features](03-9-politica-de-features-e-modelagem.md) | Da evidência à política e à modelagem | [03](issues/03-data-audit.md) | escrita |
| — | Dados limpos e features portáveis | [04](issues/04-clean-portable-data.md) | em breve |
| — | Holdout temporal e folds agrupados | [05](issues/05-temporal-validation.md) | em breve |
| — | Baseline OOF | [06](issues/06-oof-baseline.md) | em breve |
| — | Regimes de desbalanceamento | [07](issues/07-imbalance-regimes.md) | em breve |
| — | Oito modelos tradicionais | [08](issues/08-model-registry.md) | em breve |
| — | Oito caminhos de features | [09](issues/09-feature-selection.md) | em breve |
| — | Screening de 192 configurações | [10](issues/10-screening.md) | em breve |
| — | Otimização com Optuna | [11](issues/11-optuna.md) | em breve |
| — | Tiny MLP | [12](issues/12-tiny-mlp.md) | em breve |
| — | Calibração e limiares | [13](issues/13-calibration-thresholds.md) | em breve |
| — | Ensembles ponderados | [14](issues/14-ensembles.md) | em breve |
| — | Holdout e relatório final | [15](issues/15-final-report.md) | sem aula (relatório) |
| — | Especificação edge futura | [16](issues/16-edge-spec.md) | sem aula (especificação) |
