# Recursos

Fontes de alta confiança em que o curso se apoia, cada uma lida durante a escrita das aulas.

## Conhecimento

- [uv — sincronização e bloqueio de projetos](https://docs.astral.sh/uv/concepts/projects/sync/)
  Documentação oficial de `uv sync`, `uv run`, `--locked` e `--frozen`. Use para: entender quando o lockfile é validado ou atualizado.
- [uv — layout de projetos](https://docs.astral.sh/uv/concepts/projects/layout/)
  Papel de `pyproject.toml`, `uv.lock` e `.venv`. Use para: saber o que vai para o Git.
- [uv — grupos de dependências](https://docs.astral.sh/uv/concepts/projects/dependencies/)
  `[dependency-groups]`, `--group`, `--all-groups`, `--no-dev`. Use para: separar dev, notebook e produção.
- [uv — configuração e pontos de entrada](https://docs.astral.sh/uv/concepts/projects/config/)
  `[project.scripts]` e a exigência de um build system. Use para: criar comandos do projeto.
- [uv — projetos empacotados](https://docs.astral.sh/uv/concepts/projects/init/)
  Aplicações, bibliotecas e layout `src`. Use para: entender por que o pacote é instalável.
- [uv — instalação](https://docs.astral.sh/uv/getting-started/installation/)
  Instaladores para Linux/macOS e Windows. Use para: instalar o `uv`.
- [PyPA — src layout vs flat layout](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/)
  Por que separar o código em `src/`. Use para: justificar o layout do pacote.
- [PyYAML — documentação](https://pyyaml.org/wiki/PyYAMLDocumentation)
  Referência da biblioteca; explica `load` versus `safe_load`. Use para: ler YAML de configuração com segurança.
- [Python — módulo `dataclasses`](https://docs.python.org/3/library/dataclasses.html)
  Referência de `@dataclass` e `frozen=True`. Use para: modelar dados validados e imutáveis.
- [pytest — parametrize](https://docs.pytest.org/en/stable/how-to/parametrize.html)
  Como rodar um teste para vários casos. Use para: tabelas de entradas e saídas esperadas.
- [pytest — asserts e `pytest.raises`](https://docs.pytest.org/en/stable/how-to/assert.html)
  Verificação de exceções com `match`. Use para: testar mensagens de erro.
- [Python — módulo `tempfile`](https://docs.python.org/3/library/tempfile.html)
  `TemporaryDirectory` e limpeza ao sair do contexto. Use para: áreas de preparação descartáveis.
- [Python — módulo `pathlib`](https://docs.python.org/3/library/pathlib.html)
  `Path.replace`, `rglob`, `with_name`, `relative_to`. Use para: manipular caminhos e trocas de nome.
- [Python — módulo `shutil`](https://docs.python.org/3/library/shutil.html)
  `rmtree`, `copytree` e `ignore_patterns`. Use para: copiar e apagar árvores de pastas.
- [pytest — fixture `tmp_path`](https://docs.pytest.org/en/stable/how-to/tmp_path.html)
  Guia oficial do diretório temporário por teste. Use para: testes que escrevem arquivos sem sujar o repositório.
- [Python — módulo `json`](https://docs.python.org/3/library/json.html)
  Parâmetros `sort_keys`, `separators`, `indent`. Use para: serialização canônica e arquivos legíveis.
- [Python — módulo `argparse`](https://docs.python.org/3/library/argparse.html)
  Opções de linha de comando, `action`, `choices`, `error`. Use para: construir CLIs.
- [Python — `importlib.metadata`](https://docs.python.org/3/library/importlib.metadata.html)
  Versão de pacotes instalados. Use para: registrar o ambiente de uma execução.
- [pytest — monkeypatch](https://docs.pytest.org/en/stable/how-to/monkeypatch.html)
  Substituir atributos durante um teste. Use para: simular falhas sem alterar o código.
- [Python — módulo `hashlib`](https://docs.python.org/3/library/hashlib.html)
  Referência de `sha256`, `update`, `hexdigest` e `file_digest`. Use para: calcular hashes de arquivos.
- [KaggleHub](https://github.com/Kaggle/kagglehub)
  README oficial: download e upload de datasets e modelos, formato de handle, versões e autenticação. Use para: acessar ativos do Kaggle por código.
- [python-dotenv](https://github.com/theskumar/python-dotenv)
  `load_dotenv()` e o `.env` fora do Git. Use para: configuração local e segredos.
- [argparse — subcomandos](https://docs.python.org/3/library/argparse.html#sub-commands)
  `add_subparsers` e `add_parser`. Use para: CLIs com vários comandos.
- [joblib.load](https://joblib.readthedocs.io/en/latest/generated/joblib.load.html)
  Aviso de segurança: depende de `pickle` e pode executar código. Use para: entender por que verificar hash antes de carregar.
- [PyTorch — salvar e carregar modelos](https://docs.pytorch.org/tutorials/beginner/saving_loading_models.html)
  `state_dict` e extensões `.pt`/`.pth`. Use para: serializar modelos PyTorch.
- [Especificação MQTT 3.1.1 (OASIS)](https://docs.oasis-open.org/mqtt/mqtt/v3.1.1/os/mqtt-v3.1.1-os.html)
  Tabela de pacotes de controle, QoS, papéis de cliente e broker, curinga `#`, Client ID duplicado, Clean Session e Keep Alive. Use para: ler `mqtt.msgtype` e o comportamento do protocolo.
- [Wireshark — campos MQTT](https://www.wireshark.org/docs/dfref/m/mqtt.html)
  Nome e tipo de cada campo `mqtt.*`. Use para: relacionar colunas do CSV ao protocolo.
- [Artigo MQTT_UAD (Data in Brief, 2025)](https://doi.org/10.1016/j.dib.2025.112167)
  Descreve o laboratório, os três ataques e o esquema de 67 campos. Use para: entender o que cada arquivo simula.
- [mqtt-malaria](https://github.com/etactica/mqtt-malaria)
  Ferramenta de teste de carga de brokers MQTT usada no ambiente DoS do artigo. Use para: entender a origem do tráfego de inundação.
- [MITRE ATT&CK — ARP Cache Poisoning (T1557.002)](https://attack.mitre.org/techniques/T1557/002/)
  Descrição da técnica de homem no meio por ARP spoofing e mitigações. Use para: entender o ambiente MitM.
- [mosquitto_sub](https://mosquitto.org/man/mosquitto_sub-1.html)
  Cliente MQTT de linha de comando usado na intrusão do artigo. Use para: entender assinaturas e o curinga `#`.
- [pandas — read_csv](https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html)
  `low_memory`, `dtype` e tipos mistos. Use para: leitura confiável dos CSVs.
- [pandas — DataFrame.duplicated](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.duplicated.html)
  `subset` e `keep`: o que conta como duplicata. Use para: contar e remover linhas repetidas.
- [pytest — fixtures](https://docs.pytest.org/en/stable/how-to/fixtures.html)
  Fixtures pedidas pelo nome do parâmetro e compostas entre si. Use para: preparar dados de teste reutilizáveis.
- [Python — os.stat_result.st_mtime_ns](https://docs.python.org/3/library/os.html#os.stat_result.st_mtime_ns)
  Horário da última modificação em nanossegundos inteiros. Use para: provar que um arquivo não foi alterado.
- [pandas — guia de dados ausentes](https://pandas.pydata.org/docs/user_guide/missing_data.html)
  `NaN`, `isna()`/`notna()` e o efeito dos ausentes nas contas. Use para: detectar e tratar ausências.
- [pandas — DataFrame.nunique](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.nunique.html)
  Valores distintos, com `dropna`. Use para: cardinalidade e estados de uma coluna.
- [pandas — Series.value_counts](https://pandas.pydata.org/docs/reference/api/pandas.Series.value_counts.html)
  Contagens e frequências relativas. Use para: o estado dominante de uma coluna.
- [pandas — guia de groupby](https://pandas.pydata.org/docs/user_guide/groupby.html)
  Dividir-aplicar-combinar, agrupar por série de rótulos e agregação nomeada. Use para: resumir dados por grupo ou por rajada.
- [pandas — Series.shift](https://pandas.pydata.org/docs/reference/api/pandas.Series.shift.html)
  Deslocar uma série; o primeiro elemento vira ausente. Use para: comparar cada linha com a anterior.
- [Matplotlib — backends](https://matplotlib.org/stable/users/explain/figure/backends.html)
  Backends interativos e de arquivo; `Agg`. Use para: gerar figuras sem interface gráfica.
- [RFC 826 — ARP](https://www.rfc-editor.org/rfc/rfc826.html)
  Especificação do Address Resolution Protocol: mapeia endereços de protocolo em endereços Ethernet por broadcast. Use para: entender os frames do MitM.
- [pandas — to_numeric](https://pandas.pydata.org/docs/reference/api/pandas.to_numeric.html)
  Conversão para número com `errors="coerce"`. Use para: payloads que podem ou não ser numéricos.
- [scikit-learn — armadilhas comuns](https://scikit-learn.org/stable/common_pitfalls.html)
  Vazamento de dados, pré-processamento antes da divisão e uso de `Pipeline`. Use para: evitar métricas otimistas.
- [scikit-learn — validação cruzada](https://scikit-learn.org/stable/modules/cross_validation.html)
  Hipótese i.i.d., `GroupKFold`, `StratifiedGroupKFold` e `TimeSeriesSplit`. Use para: escolher a divisão certa para dados dependentes.
- [pandas — DataFrame.to_csv](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_csv.html)
  Gravar tabelas em CSV, com ou sem índice. Use para: salvar os artefatos de um estágio.
- [Python — módulo ipaddress](https://docs.python.org/3/library/ipaddress.html)
  `ip_address`, `is_private`, `ValueError`. Use para: derivar o escopo de um IP sem guardar o endereço.
- [scikit-learn — StratifiedGroupKFold](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.StratifiedGroupKFold.html)
  Folds estratificados com grupos que não se dividem; o número de grupos deve ser ao menos o de folds. Use para: planejar a validação agrupada.
- [imbalanced-learn — sobreamostragem](https://imbalanced-learn.org/stable/over_sampling.html)
  SMOTE e SMOTENC (este último não foi projetado para dados só categóricos). Use para: planejar os regimes de desbalanceamento.
- [pandas — crosstab](https://pandas.pydata.org/docs/reference/api/pandas.crosstab.html)
  Tabelas cruzadas. Use para: contar combinações de duas colunas.
- [pandas — Series.map](https://pandas.pydata.org/docs/reference/api/pandas.Series.map.html)
  Troca de valores por dicionário. Use para: nomear códigos.
- [Kaggle CLI — datasets](https://github.com/Kaggle/kaggle-cli/blob/main/docs/datasets.md)
  Comandos `datasets version` (nota de versão obrigatória) e download; datasets nascem privados. Use para: criar versões pela linha de comando.
- [Python — módulo `re`](https://docs.python.org/3/library/re.html)
  `match`, `search`, `fullmatch` e as âncoras `^` e `$`. Use para: validar formatos de texto.
- [Python — funções embutidas](https://docs.python.org/3/library/functions.html)
  Inclui `iter(callable, sentinel)`. Use para: ler arquivos em blocos.
- [Kaggle CLI](https://github.com/Kaggle/kaggle-cli/blob/main/docs/README.md)
  Documentação oficial da linha de comando: datasets, modelos e métodos de autenticação. Use para: criar e versionar recursos pela linha de comando.
- [Material for MkDocs — blocos de código](https://squidfunk.github.io/mkdocs-material/reference/code-blocks/)
  Sintaxe de título, números de linha, destaque e anotações. Use para: ler e escrever as aulas deste curso.

## Comunidades

- [Python Brasil](https://python.org.br/)
  Comunidade brasileira de Python, com lista de discussão, Telegram e grupos regionais. Use para: tirar dúvidas em português.
- [Discussions on Python.org](https://discuss.python.org/)
  Fórum oficial; a categoria Python Help recebe perguntas de qualquer nível. Use para: dúvidas sobre a linguagem.
- [Discussões do Kaggle](https://www.kaggle.com/discussions)
  Fóruns da plataforma Kaggle. Use para: dúvidas sobre datasets, modelos e a plataforma.

## Lacunas

- Documentação oficial do Kaggle sobre versões de Models (`kaggle.com/docs/models`): a página não carregou por busca automática; o curso usa os READMEs do KaggleHub e do Kaggle CLI.
- Fonte sobre convenções de hash canônico (JSON ordenado) para identidade de experimentos: ainda não encontrada em fonte oficial.
