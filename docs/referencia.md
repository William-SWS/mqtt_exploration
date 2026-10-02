# Referência rápida

Comandos, padrões de código e receitas curtas, agrupados por ferramenta. Cada aula acrescenta o que ensinou, com o link para a aula de origem.

## uv

| Quando usar | Comando | Aula |
|---|---|---|
| Criar o ambiente a partir do lockfile (checkout limpo) | `uv sync --locked` | [01-1](01-1-ambiente-e-pacote.md#passo-1-sincronizar-o-ambiente-a-partir-do-lockfile) |
| Executar qualquer coisa no ambiente, sem resolver versões novas | `uv run --locked <comando>` | [01-1](01-1-ambiente-e-pacote.md#passo-3-importar-o-pacote-de-qualquer-pasta) |
| Usar o ambiente de outra pasta | `uv run --locked --project <pasta> <comando>` | [01-1](01-1-ambiente-e-pacote.md#passo-3-importar-o-pacote-de-qualquer-pasta) |
| Tirar/pôr grupos de dependências | `uv sync --locked --no-dev` / `--all-groups` / `--group notebook` | [01-1](01-1-ambiente-e-pacote.md#passo-5-ver-os-grupos-em-acao) |
| Adicionar dependência atualizando `pyproject.toml` e `uv.lock` | `uv add <pacote>` (`--dev` para o grupo dev) | [01-1](01-1-ambiente-e-pacote.md#erros-comuns) |
| Chamar o comando do projeto | `uv run --locked mqtt-ids --help` | [01-1](01-1-ambiente-e-pacote.md#passo-4-chamar-o-comando-mqtt-ids) |

## pytest

| Quando usar | Comando | Aula |
|---|---|---|
| Rodar toda a suíte | `uv run --locked pytest` | [01-1](01-1-ambiente-e-pacote.md#testando) |
| Rodar um arquivo | `uv run --locked pytest tests/test_config.py` | [01-1](01-1-ambiente-e-pacote.md#testando) |

## YAML e validação

| Quando usar | Padrão | Aula |
|---|---|---|
| Ler configuração sem executar código | `yaml.safe_load(path.read_text(encoding="utf-8"))` | [01-2](01-2-cenario-yaml.md#passo-3-ler-e-validar-com-load_scenario) |
| Impedir que `seed: true` passe como inteiro | `isinstance(seed, int) and not isinstance(seed, bool)` | [01-2](01-2-cenario-yaml.md#passo-3-ler-e-validar-com-load_scenario) |
| Dado validado e somente leitura | `@dataclass(frozen=True)` | [01-2](01-2-cenario-yaml.md#passo-2-a-excecao-propria-e-o-scenario-imutavel) |

## pytest (padrões)

| Quando usar | Padrão | Aula |
|---|---|---|
| Vários casos com a mesma estrutura | `@pytest.mark.parametrize(("entrada", "esperado"), [...])` | [01-2](01-2-cenario-yaml.md#testando) |
| Pasta temporária por teste | parâmetro `tmp_path: Path` | [01-2](01-2-cenario-yaml.md#testando) |
| Erro esperado com mensagem | `with pytest.raises(Erro, match="trecho"):` | [01-2](01-2-cenario-yaml.md#testando) |
| Ver cada teste | `uv run --locked pytest -v` | [01-2](01-2-cenario-yaml.md#testando) |

## Runner (`mqtt-ids`)

| Quando usar | Comando ou padrão | Aula |
|---|---|---|
| Executar o diagnóstico | `uv run --locked mqtt-ids --scenario configs/diagnostics.yaml` | [01-3](01-3-runner-e-manifesto.md#passo-4-a-linha-de-comando) |
| Escolher a pasta de saída | `--output-dir <pasta>` (padrão `artifacts/runs`) | [01-3](01-3-runner-e-manifesto.md#passo-4-a-linha-de-comando) |
| Reaproveitar execução concluída | `--resume` | [01-3](01-3-runner-e-manifesto.md#passo-5-retomar-falhar-e-mudar-de-identidade) |
| Escolher estágio (repetível) | `--stage diagnostics` / `--stage acquire` | [01-3](01-3-runner-e-manifesto.md#passo-5-retomar-falhar-e-mudar-de-identidade) |
| Hash canônico de um dicionário | `hashlib.sha256(json.dumps(d, sort_keys=True, separators=(",", ":")).encode()).hexdigest()` | [01-3](01-3-runner-e-manifesto.md#passo-2-a-identidade-deterministica) |
| Gravar resultado mesmo em falha | `try: ... except: ...; raise ... finally: gravar` | [01-3](01-3-runner-e-manifesto.md#passo-3-o-manifesto-gravado-sempre) |
| Simular falha num teste | `monkeypatch.setattr(modulo, "funcao", falha)` | [01-3](01-3-runner-e-manifesto.md#testando) |

## Kaggle: handles e hashes

| Quando usar | Padrão | Aula |
|---|---|---|
| Handle de download de Dataset | `owner/slug/versions/N` | [02-1](02-1-handles-e-sha256.md#handle-versionado) |
| Handle de upload de Dataset | `owner/slug` | [02-1](02-1-handles-e-sha256.md#handle-versionado) |
| Handle de download de Model | `owner/model/framework/variation/N` | [02-1](02-1-handles-e-sha256.md#handle-versionado) |
| Handle de upload de Model | `owner/model/framework/variation` | [02-1](02-1-handles-e-sha256.md#handle-versionado) |
| Validar o formato inteiro de um texto | `padrao.fullmatch(texto)` (não `match`) | [02-1](02-1-handles-e-sha256.md#validacao-antecipada-com-expressao-regular) |
| Hash de arquivo sem ler tudo na memória | `iter(lambda: f.read(1024 * 1024), b"")` + `digest.update(bloco)` | [02-1](02-1-handles-e-sha256.md#passo-3-sha-256-em-streaming) |
| Conferir um arquivo no terminal | `sha256sum arquivo` (macOS: `shasum -a 256`) | [02-1](02-1-handles-e-sha256.md#passo-3-sha-256-em-streaming) |

## Aquisição de dados (`acquire`)

| Quando usar | Comando ou padrão | Aula |
|---|---|---|
| Executar a aquisição pelo runner | `uv run --locked mqtt-ids --scenario configs/kaggle-acquisition.local.yaml --stage acquire` | [02-2](02-2-aquisicao-atomica.md#passo-1-a-secao-dataset-do-cenario) |
| Pasta temporária que some sozinha, ao lado do destino | `with tempfile.TemporaryDirectory(prefix=".x-", dir=destino.parent) as tmp:` | [02-2](02-2-aquisicao-atomica.md#passo-3-o-estagio-acquire_dataset) |
| Trocar o nome de forma atômica | `origem.replace(destino)` | [02-2](02-2-aquisicao-atomica.md#passo-3-o-estagio-acquire_dataset) |
| Gravar arquivo sem deixá-lo pela metade | escrever em `x.tmp` e `x.tmp.replace(x)` | [02-2](02-2-aquisicao-atomica.md#exercicios) |
| Trocar a rede por um dublê em teste | `monkeypatch.setattr(modulo, "_kagglehub", lambda: Fake())` | [02-2](02-2-aquisicao-atomica.md#testando) |
| Rodar só testes de um tema | `uv run --locked pytest -v -k "acquisition"` | [02-2](02-2-aquisicao-atomica.md#testando) |

## Publicar e recuperar (`mqtt-kaggle-assets`)

| Quando usar | Comando | Aula |
|---|---|---|
| Enviar nova versão de Dataset | `uv run --locked mqtt-kaggle-assets upload-dataset --handle OWNER/SLUG --version-notes "<motivo>"` | [02-3](02-3-publicar-e-recuperar.md#passo-4-a-linha-de-comando-mqtt-kaggle-assets) |
| Baixar versão fixada de Dataset | `... download-dataset --handle OWNER/SLUG/versions/N [--category raw]` | [02-3](02-3-publicar-e-recuperar.md#passo-4-a-linha-de-comando-mqtt-kaggle-assets) |
| Enviar um pacote de modelo | `... upload-model --handle OWNER/MODEL/FRAMEWORK/VARIATION --model-dir <pasta> --version-notes "<motivo>"` | [02-3](02-3-publicar-e-recuperar.md#passo-1-validar-o-pacote-de-modelo) |
| Baixar um modelo fixado | `... download-model --handle OWNER/MODEL/FRAMEWORK/VARIATION/N --output-dir <pasta>` | [02-3](02-3-publicar-e-recuperar.md#passo-4-a-linha-de-comando-mqtt-kaggle-assets) |
| Registrar a versão publicada no manifesto | `... record-dataset-version` / `record-model-version --handle <com versão> --manifest <arquivo>` | [02-3](02-3-publicar-e-recuperar.md#passo-2-registrar-a-versao-publicada) |
| Formato do `sha256sums.txt` | `<sha256>␣␣<caminho-relativo>` (como `sha256sum`) | [02-3](02-3-publicar-e-recuperar.md#passo-3-simular-o-ciclo-sem-rede) |
| Confirmar que segredos são ignorados | `git check-ignore -v .env kaggle.json access_token` | [02-3](02-3-publicar-e-recuperar.md#passo-4-a-linha-de-comando-mqtt-kaggle-assets) |

## Auditoria dos dados (pandas)

| Quando usar | Padrão | Aula |
|---|---|---|
| Ler CSV sem tipos misturados | `pd.read_csv(caminho, low_memory=False)` | [03-1](03-1-mqtt-e-os-tres-ambientes.md#passo-2-abrir-um-csv-sem-enganar-o-pandas) |
| Contar combinações de duas colunas | `pd.crosstab(a, b)` | [03-1](03-1-mqtt-e-os-tres-ambientes.md#passo-3-nomear-os-tipos-de-pacote) |
| Trocar códigos por nomes | `serie.map(dicionario)` (o que falta vira `NaN`) | [03-1](03-1-mqtt-e-os-tres-ambientes.md#passo-3-nomear-os-tipos-de-pacote) |
| Fração de verdadeiros por grupo | `cond.groupby(grupo).mean()` | [03-1](03-1-mqtt-e-os-tres-ambientes.md#passo-3-nomear-os-tipos-de-pacote) |
| Tipos de pacote MQTT | 1 CONNECT, 2 CONNACK, 3 PUBLISH, 4 PUBACK, 5 PUBREC, 6 PUBREL, 7 PUBCOMP, 8 SUBSCRIBE, 9 SUBACK, 10 UNSUBSCRIBE, 11 UNSUBACK, 12 PINGREQ, 13 PINGRESP, 14 DISCONNECT | [03-1](03-1-mqtt-e-os-tres-ambientes.md#mqtt-publicar-assinar-e-pacotes-de-controle) |

## Carga e contrato (pandas)

| Quando usar | Padrão | Aula |
|---|---|---|
| Ler só depois de verificar o hash | `if sha256(path) != RAW_HASHES[nome]: raise AuditError(...)` | [03-2](03-2-carga-segura-e-contrato.md#passo-1-preparar-o-modulo-e-ler-so-depois-de-conferir) |
| Contar linhas duplicadas | `int(df.duplicated().sum())` (marca todas, exceto a primeira) | [03-2](03-2-carga-segura-e-contrato.md#passo-2-o-contrato-de-contagens) |
| Frames repetidos | `len(df) - df["frame.number"].nunique()` | [03-2](03-2-carga-segura-e-contrato.md#passo-2-o-contrato-de-contagens) |
| Remover duplicatas mantendo a primeira | `df[~df.duplicated(keep="first")]` | [03-2](03-2-carga-segura-e-contrato.md#exercicios) |
| Provar que o arquivo não mudou | comparar `path.read_bytes()` e `path.stat().st_mtime_ns` antes e depois | [03-2](03-2-carga-segura-e-contrato.md#testando) |
| Fixture que cria um CSV de teste | `@pytest.fixture` pedindo `tmp_path` e `monkeypatch` | [03-2](03-2-carga-segura-e-contrato.md#testando) |

## Perfil de colunas (pandas)

| Quando usar | Padrão | Aula |
|---|---|---|
| Percentual de ausência por coluna | `df.isna().mean() * 100` | [03-3](03-3-missingness-e-dicionario.md#passo-1-o-perfil-de-cada-coluna) |
| Valores distintos sem / com a ausência | `df.nunique(dropna=True)` / `df.nunique(dropna=False)` | [03-3](03-3-missingness-e-dicionario.md#passo-1-o-perfil-de-cada-coluna) |
| Fração do estado dominante | `col.value_counts(normalize=True, dropna=False).max()` | [03-3](03-3-missingness-e-dicionario.md#passo-1-o-perfil-de-cada-coluna) |
| Ausência dentro de cada grupo | `df[cols].isna().groupby(grupo).mean().mul(100)` | [03-3](03-3-missingness-e-dicionario.md#passo-2-ausencia-dentro-de-cada-tipo-de-pacote) |
| Rascunho que importa `scripts/` | `env PYTHONPATH=. uv run --locked python /tmp/arquivo.py` | [03-3](03-3-missingness-e-dicionario.md#passo-5-fazer-o-pytest-enxergar-scripts) |
| Pytest enxergar `scripts/` | `pythonpath = ["."]` em `[tool.pytest.ini_options]` | [03-3](03-3-missingness-e-dicionario.md#passo-5-fazer-o-pytest-enxergar-scripts) |

## Rajadas, taxa e figuras

| Quando usar | Padrão | Aula |
|---|---|---|
| Numerar rajadas de uma classe | `(is_pos != is_pos.shift()).cumsum()` | [03-4](03-4-dos-inundacao.md#passo-1-numerar-as-rajadas) |
| Resumir cada grupo com nomes | `df.groupby(ids).agg(nome=("coluna", "função"))` | [03-4](03-4-dos-inundacao.md#passo-1-numerar-as-rajadas) |
| Frames por segundo | `s = tempo.astype(int); s.groupby(s).size()` | [03-4](03-4-dos-inundacao.md#passo-2-taxa-de-frames-por-classe) |
| Figura sem janela | `matplotlib.use("Agg")` antes de importar `pyplot`; `fig.savefig(caminho)`; `plt.close(fig)` | [03-4](03-4-dos-inundacao.md#passo-4-a-figura-da-linha-do-tempo) |
| Eixo em escala log | `ax.set_yscale("log")` (diga a escala no rótulo) | [03-4](03-4-dos-inundacao.md#passo-4-a-figura-da-linha-do-tempo) |
| Abrir o Jupyter no ambiente do projeto | `uv run --locked --group notebook jupyter lab` | [03-4](03-4-dos-inundacao.md#o-notebook-do-dos) |

## Camadas e endereços (MitM)

| Quando usar | Padrão | Aula |
|---|---|---|
| Fração de frames com IP/TCP/MQTT por classe | `pd.DataFrame({"ip": df["ip.src"].notna(), ...}).groupby(df["type"]).mean()` | [03-5](03-5-mitm-trafego-alterado.md#passo-1-quantas-camadas-cada-classe-tem) |
| Valores mais usados pelo ataque e seu uso no normal | `pd.crosstab(col, df["type"])` + `counts[positivo].nlargest(n)` | [03-5](03-5-mitm-trafego-alterado.md#passo-1-quantas-camadas-cada-classe-tem) |
| Converter payload em número ignorando erros | `pd.to_numeric(serie, errors="coerce")` | [03-5](03-5-mitm-trafego-alterado.md#passo-4-o-dado-alterado) |
| Estatísticas por grupo | `valores.groupby(classe).describe()` | [03-5](03-5-mitm-trafego-alterado.md#passo-4-o-dado-alterado) |
| Frame é broadcast? | `df["eth.dst"] == "ff:ff:ff:ff:ff:ff"` | [03-5](03-5-mitm-trafego-alterado.md#exercicios) |

## Sessões e identidades

| Quando usar | Padrão | Aula |
|---|---|---|
| Sequência de pacotes de cada rajada | `nomes.groupby(ids_rajada).agg(juntar_sem_repeticao)` | [03-6](03-6-intrusion-cliente-desconhecido.md#passo-2-nomes-de-pacote-e-assinaturas) |
| Valores só do ataque / só do normal / dos dois | `set(a) - set(n)`, `set(a) & set(n)`, `set(n) - set(a)` | [03-6](03-6-intrusion-cliente-desconhecido.md#passo-3-que-parte-da-sessao-e-so-do-atacante) |
| Contar rajadas por assinatura | `sequencias.value_counts()` | [03-6](03-6-intrusion-cliente-desconhecido.md#passo-2-nomes-de-pacote-e-assinaturas) |

## Vazamento e divisões

| Quando usar | Padrão | Aula |
|---|---|---|
| Primeiros 70% como treino (ordem de captura) | `np.arange(len(df)) < int(len(df) * 0.7)` | [03-7](03-7-vazamento-identidade-conteudo-ordem.md#passo-1-divisoes-e-o-classificador-de-tabela) |
| Divisão aleatória reproduzível | `np.random.default_rng(seed).random(len(df)) < 0.7` | [03-7](03-7-vazamento-identidade-conteudo-ordem.md#passo-1-divisoes-e-o-classificador-de-tabela) |
| Memorizar taxa por valor | `y[treino].groupby(valor[treino]).mean()` e `valor[teste].map(taxa)` | [03-7](03-7-vazamento-identidade-conteudo-ordem.md#passo-1-divisoes-e-o-classificador-de-tabela) |
| Prevalência por décimo da captura | `y.groupby(pd.qcut(np.arange(n), 10, labels=False)).mean()` | [03-7](03-7-vazamento-identidade-conteudo-ordem.md#passo-3-a-ordem-importa) |
| Classe igual à do vizinho | `(y == y.shift()).iloc[1:].mean()` | [03-7](03-7-vazamento-identidade-conteudo-ordem.md#passo-3-a-ordem-importa) |

## Estágio `audit`

| Quando usar | Comando ou padrão | Aula |
|---|---|---|
| Gerar tabelas, figuras e manifesto | `uv run --locked mqtt-ids --scenario configs/audit.yaml --stage audit` | [03-8](03-8-estagio-audit.md#passo-3-executar-o-estagio) |
| Escolher onde gravar tabelas e figuras | `--results-dir <pasta>` (padrão `results`) | [03-8](03-8-estagio-audit.md#passo-2-ligar-o-estagio-ao-runner-e-a-cli) |
| Gravar um DataFrame em CSV com os nomes | `tabela.to_csv(caminho)` (o índice vai junto) | [03-8](03-8-estagio-audit.md#passo-1-o-estagio) |
| Conferir saídas contra o manifesto | comparar `sha256(results/<caminho>)` com `manifest["audit"]["outputs"]` | [03-8](03-8-estagio-audit.md#exercicios) |
| Testar um estágio sem dados reais | fixture com CSVs sintéticos e `monkeypatch.setattr(audit, "RAW_HASHES", ...)` | [03-8](03-8-estagio-audit.md#testando) |

## Derivações e validação

| Quando usar | Padrão | Aula |
|---|---|---|
| IP privado ou público | `ipaddress.ip_address(texto).is_private` (levanta `ValueError` se não for IP) | [03-9](03-9-politica-de-features-e-modelagem.md#passo-1-as-derivacoes) |
| Ausência como categoria | `col.fillna(-1)`, escopo `none`, flag `col.notna()` | [03-9](03-9-politica-de-features-e-modelagem.md#passo-1-as-derivacoes) |
| Blocos de tempo como grupos | `(tempo // segundos).astype(int)` | [03-9](03-9-politica-de-features-e-modelagem.md#passo-4-blocos-de-validacao) |
| Folds viáveis | blocos com ataque no desenvolvimento ≥ número de folds | [03-9](03-9-politica-de-features-e-modelagem.md#passo-4-blocos-de-validacao) |
| Bloquear identidades cruas nas features | `assert_no_identity(derivadas, {"ip.src", ...})` | [03-9](03-9-politica-de-features-e-modelagem.md#exercicios) |
