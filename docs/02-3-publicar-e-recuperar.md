# 02-3. Publicar e recuperar ativos versionados

## Objetivos desta aula

Ao final desta aula você vai entender:

- por que um pacote de modelo carrega **hashes** e é validado **antes** de qualquer chamada de rede;
- como o handle versionado publicado é **registrado** no manifesto local, sem deixar o arquivo pela metade;
- como a linha de comando `mqtt-kaggle-assets` e o `.env` mantêm credenciais fora do Git e os recursos **privados** até a revisão manual.

E vai ter construído: `validate_model_package`, `upload_model`, `download_model`, `record_published_version` e a CLI que os expõe.

**Ganho tangível:** uma simulação offline monta um pacote de modelo, o valida (e o vê ser recusado quando adulterado ou incompleto), "envia" o pacote e registra no manifesto o handle `owner/model/framework/variation/N`.

## Onde estamos

Na [aula 02-2](02-2-aquisicao-atomica.md) você fez a aquisição atômica e verificada dos dados. Esta aula fecha a [issue 02](issues/02-kaggle-ingestion.md) com o outro lado: **publicar** novas versões (Dataset e Model) e **recuperá-las** por handle fixado em qualquer máquina. Depois dela, o curso chega à issue 03 (auditoria e dicionário de dados).

### Relembrando

??? question "1. Por que a aquisição baixa para uma pasta temporária e só depois promove?"

    Para que o destino nunca contenha um download parcial ou inválido: a validação acontece fora do lugar e só o resultado verificado entra por uma troca de nome.

??? question "2. Qual a diferença entre o handle de upload e o de download de um Model?"

    Upload: `owner/model/framework/variation` (quatro trechos, sem versão). Download: `owner/model/framework/variation/N` (cinco trechos, com a versão).

??? question "3. Como se grava um arquivo de forma atômica?"

    Escreve-se o conteúdo completo em um arquivo temporário vizinho (`.tmp`) e depois troca-se o nome sobre o destino com `Path.replace`: o arquivo final é sempre a versão antiga inteira ou a nova inteira. Você praticou isso nos exercícios da 02-2.

## Antes de começar

As aulas anteriores concluídas e a suíte verde:

--8<-- "course/includes/rodar-testes.md"

Nenhuma conta ou token é necessário: usaremos um dublê, como na aula 02-2. Para publicar de verdade você precisará de autenticação no Kaggle, explicada na seção de credenciais abaixo.

## Conceitos

### Pacote de modelo verificável

Um modelo treinado vira um **arquivo serializado** (`.joblib` para scikit-learn, `.pt`/`.pth` para o `state_dict` do PyTorch). Esse arquivo não é inofensivo: `joblib.load` se apoia no `pickle` e "pode executar código Python arbitrário", por isso nunca deve ser usado com arquivos de origem não confiável. Verificar a integridade antes de carregar é uma defesa, não um luxo.

O projeto empacota cada modelo concluído numa pasta com quatro itens:

| Arquivo | Para quê |
|---|---|
| `model.joblib` (ou `.pt`/`.pth`) | O modelo serializado |
| `metadata.json` | Framework, parâmetros e dependências |
| `manifest.json` | Identidade da execução e dataset de entrada |
| `sha256sums.txt` | Uma linha `SHA256␣␣caminho` por arquivo |

O código exige o pacote **completo e íntegro antes de tocar na rede**: faltando um item, ou com hash divergente, o upload nem começa. O mesmo vale para o Dataset: antes de enviar, os três CSVs são conferidos contra `RAW_HASHES` (aula 02-1).

Fontes: [joblib.load](https://joblib.readthedocs.io/en/latest/generated/joblib.load.html) (aviso de segurança) e [PyTorch: salvar e carregar modelos](https://docs.pytorch.org/tutorials/beginner/saving_loading_models.html) (`state_dict`, extensões `.pt`/`.pth`).

### Versões imutáveis e registro do handle publicado

Cada upload cria uma **nova versão** sem remover as anteriores; o handle com `/N` recupera exatamente aquela. O detalhe incômodo é que a função de upload do KaggleHub **não devolve o número `N`** criado ([ADR-022](DECISIONS.md#adr-022-aquisicao-kaggle-versionada-validada-e-promovida-atomicamente)). Então o fluxo tem duas etapas: (1) publicar; (2) depois de confirmar `N` no Kaggle, **registrar** o handle versionado em `published_assets` do manifesto local. Assim nenhum artefato publicado fica sem o "endereço imutável" necessário para recuperá-lo em outra máquina.

Registrar edita um arquivo que já existe; para não corrompê-lo se o programa for interrompido, a escrita é atômica: grava em `manifest.json.tmp` e só então troca o nome (a ideia da aula 02-2).

Fontes: [README do KaggleHub](https://github.com/Kaggle/kagglehub) (nova versão ao reenviar com o mesmo handle) e [Kaggle CLI: datasets](https://github.com/Kaggle/kaggle-cli/blob/main/docs/datasets.md) (cada versão exige uma nota).

### Credenciais fora do Git e recursos privados

O KaggleHub autentica por variável de ambiente `KAGGLE_API_TOKEN`, por arquivo de token ou pelo fluxo interativo. O projeto guarda o que é **local** em um `.env`, lido por `load_dotenv()`: ele coloca as variáveis em `os.environ` **sem** sobrescrever as já definidas, e a própria documentação recomenda pôr o `.env` no `.gitignore`. O repositório traz só o modelo `.env.example`, sem valores. Datasets e Models nascem **privados** e só se tornam públicos depois de uma revisão manual de atribuição e integridade.

Uma CLI com vários comandos usa **subcomandos** do `argparse`, como `git commit` e `git push`: `mqtt-kaggle-assets upload-model ...`, `download-dataset ...` etc.

Fontes: [python-dotenv](https://github.com/theskumar/python-dotenv), [argparse: subcomandos](https://docs.python.org/3/library/argparse.html#sub-commands) e [README do KaggleHub](https://github.com/Kaggle/kagglehub) (formas de autenticação).

## Ponte teoria → projeto

A [issue 02](issues/02-kaggle-ingestion.md) pede que todo modelo concluído seja empacotado com formato serializado, metadata e hashes, enviado a um Kaggle Model privado e que seu handle versionado seja registrado no manifesto; que um modelo possa ser baixado por `owner/model/framework/variation/N` (handle sem `/N` rejeitado); que o upload crie nova versão sem apagar as anteriores; e que nenhum token apareça em log, manifesto ou Git. A [ADR-022](DECISIONS.md#adr-022-aquisicao-kaggle-versionada-validada-e-promovida-atomicamente) fixa a segunda etapa de registro. Para a sua missão: cada modelo do portfólio poderá ser baixado, conferido por hash e atribuído a uma execução e a uma versão de dados.

## Mão na massa

### Passo 1 — Validar o pacote de modelo

```python title="src/mqtt_ids/kaggle_assets.py" linenums="184"
def validate_model_package(model_dir: Path) -> None:
    """Garante que o modelo inclua pesos, metadata, manifesto e hashes."""
    required = ("metadata.json", "manifest.json", "sha256sums.txt")
    missing = [name for name in required if not (model_dir / name).is_file()]  # (1)!
    model_files = (
        [
            path
            for path in model_dir.iterdir()
            if path.is_file() and path.suffix in {".joblib", ".pt", ".pth"}  # (2)!
        ]
        if model_dir.is_dir()
        else []
    )
    if missing or not model_files:
        details = []
        if missing:
            details.append("faltam " + ", ".join(missing))
        if not model_files:
            details.append("falta um .joblib, .pt ou .pth")
        raise KaggleAssetError("Pacote de modelo inválido: " + "; ".join(details) + ".")  # (3)!
```

1.  Lista **todos** os itens que faltam, não só o primeiro: uma única mensagem diz o que corrigir.
2.  O modelo pode ser sklearn (`.joblib`) ou PyTorch (`.pt`/`.pth`); pelo menos um é obrigatório.
3.  Junta as queixas em uma frase só, como `faltam metadata.json; falta um .joblib, .pt ou .pth.`

A segunda metade compara cada arquivo com o `sha256sums.txt`:

```python title="src/mqtt_ids/kaggle_assets.py" linenums="204"
    expected = _parse_sha256sums(model_dir / "sha256sums.txt")  # (1)!
    for relative_path, expected_hash in expected.items():
        path = model_dir / relative_path
        if not path.is_file() or sha256(path) != expected_hash:  # (2)!
            raise KaggleAssetError(
                f"Hash divergente ou arquivo ausente: {relative_path}."
            )
```

1.  Lê o arquivo de hashes (o formato é `SHA256␣␣caminho`; o auxiliar `_parse_sha256sums`, linhas 344–353, recusa linhas malformadas e arquivo vazio).
2.  Arquivo ausente e arquivo adulterado são o **mesmo erro**: não dá para confiar no pacote.

E o upload só acontece depois disso:

```python title="src/mqtt_ids/kaggle_assets.py" linenums="213"
def upload_model(model_dir: Path, handle: str, version_notes: str) -> None:
    """Publica o pacote de um modelo em sua variação privada no Kaggle."""
    validate_model_upload_handle(handle)  # (1)!
    if not version_notes.strip():
        raise KaggleAssetError("A versão do Model exige uma nota não vazia.")  # (2)!
    validate_model_package(model_dir)  # (3)!
    _kagglehub().model_upload(
        handle, str(model_dir), version_notes=version_notes.strip()  # (4)!
    )
```

1.  Handle de upload (sem versão), da aula 02-1.
2.  Nota de versão obrigatória: cada versão no Kaggle precisa de uma explicação verificável.
3.  O pacote é validado **antes** de qualquer rede.
4.  Só depois a rede, pela mesma costura `_kagglehub()` da aula 02-2.

O upload de Dataset segue o mesmo princípio (`prepare_dataset_package` confere os três hashes, copia os dados para uma pasta temporária **sem** os `.gitkeep` e grava um manifesto de hashes antes do envio). Veja o código completo no fim da aula.

### Passo 2 — Registrar a versão publicada

```python title="src/mqtt_ids/kaggle_assets.py" linenums="232"
def record_published_version(manifest_path: Path, kind: str, handle: str) -> None:
    """Registra atomicamente o handle imutável confirmado após um upload."""
    if kind == "dataset":
        validate_dataset_download_handle(handle)  # (1)!
    elif kind == "model":
        validate_model_download_handle(handle)
    else:
        raise KaggleAssetError("Ativo publicado deve ser dataset ou model.")
    if not manifest_path.is_file():
        raise KaggleAssetError(f"Manifesto não encontrado: {manifest_path}")
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise KaggleAssetError(f"Manifesto inválido: {manifest_path}") from error
    if not isinstance(manifest, dict):
        raise KaggleAssetError(f"Manifesto deve ser um objeto JSON: {manifest_path}")
```

1.  O que se registra é o handle **versionado** (de download). Um handle sem versão seria um registro inútil.

```python title="src/mqtt_ids/kaggle_assets.py" linenums="248"
    published = manifest.setdefault("published_assets", {})  # (1)!
    if not isinstance(published, dict):
        raise KaggleAssetError("'published_assets' deve ser um objeto JSON.")
    published[kind] = handle
    temporary = manifest_path.with_suffix(manifest_path.suffix + ".tmp")  # (2)!
    temporary.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    temporary.replace(manifest_path)  # (3)!
```

1.  `setdefault` devolve a seção se já existe e a cria vazia se não: registrar um modelo **não apaga** o dataset registrado antes.
2.  Escreve em `manifest.json.tmp`, ao lado.
3.  Troca o nome: o manifesto é sempre a versão antiga completa ou a nova completa, nunca metade.

### Passo 3 — Simular o ciclo, sem rede

Crie `/tmp/montar_modelo.py`. Ele monta o pacote, tenta quebrá-lo de duas formas, "envia" e registra:

```python title="/tmp/montar_modelo.py" linenums="1"
import json
from pathlib import Path

from mqtt_ids import kaggle_assets
from mqtt_ids.kaggle_assets import (
    KaggleAssetError,
    record_published_version,
    sha256,
    upload_model,
    validate_model_package,
)

package = Path("/tmp/m/modelo")
package.mkdir(parents=True)
(package / "model.joblib").write_bytes(b"pesos-simulados")  # (1)!
(package / "metadata.json").write_text('{"framework": "sklearn"}\n', encoding="utf-8")
(package / "manifest.json").write_text('{"status": "completed"}\n', encoding="utf-8")
names = ["model.joblib", "metadata.json", "manifest.json"]
(package / "sha256sums.txt").write_text(
    "".join(f"{sha256(package / name)}  {name}\n" for name in names), encoding="utf-8"  # (2)!
)

validate_model_package(package)
print("1. pacote válido")

(package / "model.joblib").write_bytes(b"adulterado")  # (3)!
try:
    validate_model_package(package)
except KaggleAssetError as error:
    print("2. ERRO:", error)
(package / "model.joblib").write_bytes(b"pesos-simulados")

(package / "metadata.json").unlink()  # (4)!
try:
    validate_model_package(package)
except KaggleAssetError as error:
    print("3. ERRO:", error)
(package / "metadata.json").write_text('{"framework": "sklearn"}\n', encoding="utf-8")


class FakeKaggleHub:  # (5)!
    def model_upload(self, handle, directory, version_notes):
        print("4. [rede simulada] enviando", handle, "|", version_notes)


kaggle_assets._kagglehub = lambda: FakeKaggleHub()
upload_model(package, "owner/mqtt-ids/sklearn/baseline", "run abc; dataset owner/data/versions/3")

manifest = Path("/tmp/m/manifest.json")
manifest.write_text('{"status": "completed"}\n', encoding="utf-8")
try:
    record_published_version(manifest, "model", "owner/mqtt-ids/sklearn/baseline")  # (6)!
except KaggleAssetError as error:
    print("5. ERRO:", error)
record_published_version(manifest, "model", "owner/mqtt-ids/sklearn/baseline/2")
print("6.", json.loads(manifest.read_text()))
print("7.", sorted(path.name for path in Path("/tmp/m").glob("*.tmp")))
```

1.  Conteúdo falso no lugar de um modelo de verdade: para a validação só importa que seja um arquivo com hash.
2.  O formato do `sha256sums.txt`: hash, **dois espaços**, nome do arquivo. O mesmo formato do comando `sha256sum`.
3.  Adulterar um byte do modelo: o hash deixa de bater.
4.  Remover o `metadata.json`: o pacote fica incompleto.
5.  Dublê de upload, como na aula 02-2: só imprime o que receberia.
6.  Handle **sem versão** no registro: deve ser recusado.

```bash title="$ Execução no terminal (na pasta do projeto)"
rm -rf /tmp/m
uv run --locked python /tmp/montar_modelo.py
```

```text title="Saída esperada"
1. pacote válido
2. ERRO: Hash divergente ou arquivo ausente: model.joblib.
3. ERRO: Pacote de modelo inválido: faltam metadata.json.
4. [rede simulada] enviando owner/mqtt-ids/sklearn/baseline | run abc; dataset owner/data/versions/3
5. ERRO: Handle de download de Model deve ser 'owner/model/framework/variation/N'.
6. {'published_assets': {'model': 'owner/mqtt-ids/sklearn/baseline/2'}, 'status': 'completed'}
7. []
```

**O que aconteceu:** (1) o pacote íntegro passou; (2) adulterar `model.joblib` foi detectado pelo hash; (3) remover `metadata.json` foi detectado como item faltando; (4) o upload só chegou ao dublê depois de validar; (5) o registro sem versão foi recusado; (6) com o handle versionado, `published_assets` foi criado **preservando** `status`; (7) não sobrou nenhum `.tmp`.

??? question "Pare e pense: se você registrar um `dataset` logo depois do `model`, o que o manifesto terá em `published_assets`?"

    Os dois: `{'dataset': ..., 'model': ...}`. O `setdefault` reutiliza a seção existente e a atribuição `published[kind] = handle` só acrescenta (ou troca) a chave de `kind`.

### Passo 4 — A linha de comando `mqtt-kaggle-assets`

O ponto de entrada fino da aula 01-1 (`[project.scripts]`) tem seis subcomandos:

```python title="src/mqtt_ids/kaggle_assets_cli.py" linenums="21"
def main() -> None:
    """Processa comandos explícitos de upload e download Kaggle."""
    load_dotenv()  # (1)!
    parser = argparse.ArgumentParser(
        description="Sincroniza ativos privados no Kaggle."
    )
    commands = parser.add_subparsers(dest="command", required=True)  # (2)!

    upload_data = commands.add_parser("upload-dataset")
    upload_data.add_argument("--handle", default=os.getenv("KAGGLE_DATASET_HANDLE"))  # (3)!
    upload_data.add_argument("--data-dir", type=Path, default=Path("data"))
    upload_data.add_argument("--version-notes", required=True)
```

1.  Lê o `.env` local para `os.environ` (sem sobrescrever variáveis já definidas).
2.  `add_subparsers(required=True)`: o comando precisa ser dado; `dest="command"` guarda qual foi.
3.  O handle pode vir da linha de comando **ou** do `.env`. O repositório só tem `.env.example`, sem valores.

Os outros cinco subcomandos (`download-dataset`, `upload-model`, `download-model`, `record-dataset-version`, `record-model-version`) seguem a mesma forma. Depois de ler os argumentos, a CLI cobra o handle e traduz erros de contrato em mensagem de uso:

```python title="src/mqtt_ids/kaggle_assets_cli.py" linenums="66"
    arguments = parser.parse_args()
    if not arguments.handle:
        required_variable = {
            "upload-dataset": "KAGGLE_DATASET_HANDLE",
            "download-dataset": "KAGGLE_DATASET_VERSION_HANDLE",
            "upload-model": "KAGGLE_MODEL_HANDLE",
            "download-model": "KAGGLE_MODEL_VERSION_HANDLE",
            "record-dataset-version": "KAGGLE_DATASET_VERSION_HANDLE",
            "record-model-version": "KAGGLE_MODEL_VERSION_HANDLE",
        }[arguments.command]  # (1)!
        parser.error(f"Informe --handle ou defina {required_variable} no .env.")
```

1.  Um dicionário comando → variável de ambiente produz uma mensagem que diz exatamente qual variável definir.

Experimente a CLI sem credenciais, só os caminhos de erro (nenhum chega à rede):

```bash title="$ Execução no terminal (na pasta do projeto)"
uv run --locked mqtt-kaggle-assets download-model
uv run --locked mqtt-kaggle-assets download-model --handle owner/mqtt-ids/sklearn/baseline --output-dir /tmp/m/out
uv run --locked mqtt-kaggle-assets upload-dataset --handle owner/data/versions/3 --version-notes x
echo '{"status": "completed"}' > /tmp/m/m2.json
uv run --locked mqtt-kaggle-assets record-model-version --handle owner/mqtt-ids/sklearn/baseline/2 --manifest /tmp/m/m2.json
cat /tmp/m/m2.json
```

Os três primeiros comandos terminam com a última linha de uma mensagem de uso do `argparse`; a saída abaixo mostra só essa linha de erro de cada um:

```text title="Saída esperada"
mqtt-kaggle-assets: error: Informe --handle ou defina KAGGLE_MODEL_VERSION_HANDLE no .env.
mqtt-kaggle-assets: error: Handle de download de Model deve ser 'owner/model/framework/variation/N'.
mqtt-kaggle-assets: error: Handle de upload de Dataset deve ser 'owner/slug', sem versão.
/tmp/m/m2.json
{
  "published_assets": {
    "model": "owner/mqtt-ids/sklearn/baseline/2"
  },
  "status": "completed"
}
```

**O que aconteceu:** sem handle (e sem `.env`), o comando diz qual variável definir; handles no formato errado são recusados antes de qualquer rede; e `record-model-version` imprimiu o caminho do manifesto e gravou `published_assets`. (Se você tiver um `.env` com `KAGGLE_MODEL_VERSION_HANDLE`, o primeiro comando usará esse valor e a saída será outra.)

!!! warning "Credenciais nunca vão para o Git"

    O `.gitignore` do projeto ignora `.env`, `kaggle.json` e `access_token`, e a pasta `data/`. Confira com `git check-ignore -v .env kaggle.json access_token`: cada nome deve aparecer, com a linha do `.gitignore` que o cobre. Só o `.env.example` (sem valores) é versionado.

### Passo 5 — Checklist antes de tornar qualquer coisa pública

A [issue 02](issues/02-kaggle-ingestion.md) pede uma checklist operacional que mantenha Dataset e Model **privados** até uma revisão manual. Em resumo (o roteiro completo, com os comandos, está na [pesquisa sobre armazenamento no Kaggle](research/kaggle-armazenamento-e-recuperacao.md)):

1. Os três CSVs conferem em nome, tamanho e SHA-256 (`prepare_dataset_package` já exige isso).
2. O recurso foi criado **sem** `--public` (privado por padrão).
3. Cada nova versão tem uma nota verificável; **não** se usa `--delete-old-versions`, para poder recuperar versões históricas.
4. A versão `N` criada foi confirmada no Kaggle e o handle versionado foi registrado no manifesto (`record-*-version`).
5. Um download limpo da versão `N` foi feito e os hashes foram recalculados.
6. Atribuição (autores, DOI, licença CC BY 4.0) revisada à mão antes de qualquer publicação.
7. Nenhum token, `kaggle.json` ou valor de `KAGGLE_*` aparece em Git, logs, mensagens ou manifestos.

## Testando

Os testes de publicação não usam rede: o dublê recebe a chamada e o teste a inspeciona.

```python title="tests/test_kaggle_assets.py" linenums="120"
def test_model_upload_validates_package_before_network(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    package = tmp_path / "model"
    package.mkdir()
    (package / "model.joblib").write_bytes(b"model")
    (package / "metadata.json").write_text("{}\n", encoding="utf-8")
    (package / "manifest.json").write_text("{}\n", encoding="utf-8")
    entries = ["model.joblib", "metadata.json", "manifest.json"]
    (package / "sha256sums.txt").write_text(
        "".join(f"{sha256(package / name)}  {name}\n" for name in entries),
        encoding="utf-8",
    )

    calls: list[tuple[str, str, str]] = []

    class FakeKaggleHub:
        def model_upload(self, handle: str, directory: str, version_notes: str) -> None:
            calls.append((handle, directory, version_notes))  # (1)!

    monkeypatch.setattr(kaggle_assets, "_kagglehub", lambda: FakeKaggleHub())

    upload_model(
        package,
        "owner/mqtt-ids/sklearn/baseline",
        "run abc; dataset owner/data/versions/1",
    )

    assert calls == [  # (2)!
        (
            "owner/mqtt-ids/sklearn/baseline",
            str(package),
            "run abc; dataset owner/data/versions/1",
        )
    ]
```

1.  O dublê guarda os argumentos recebidos em vez de enviar algo.
2.  O teste afirma exatamente o que a "rede" receberia: handle, pasta e nota (já sem espaços sobrando).

O teste de recusa é o inverso: um pacote com hash errado não pode chegar à rede (e nem há dublê para recebê-lo):

```python title="tests/test_kaggle_assets.py" linenums="157"
def test_model_upload_rejects_a_corrupted_package_before_network(
    tmp_path: Path,
) -> None:
    package = tmp_path / "model"
    package.mkdir()
    (package / "model.joblib").write_bytes(b"model")
    (package / "metadata.json").write_text("{}\n", encoding="utf-8")
    (package / "manifest.json").write_text("{}\n", encoding="utf-8")
    (package / "sha256sums.txt").write_text(
        "0" * 64 + "  model.joblib\n", encoding="utf-8"  # (1)!
    )

    with pytest.raises(KaggleAssetError, match="Hash divergente"):
        upload_model(package, "owner/mqtt-ids/sklearn/baseline", "run abc")  # (2)!
```

1.  `"0" * 64` é um hash plausível, mas errado.
2.  Como não há dublê instalado, se o código tentasse a rede o teste falharia por outro motivo (e não por `KaggleAssetError`): a ausência de dublê é parte da prova.

```bash title="$ Execução no terminal (na pasta do projeto)"
uv run --locked pytest tests/test_kaggle_assets.py -v -k "model or versioned"
```

```text title="Saída esperada"
collecting ... collected 9 items / 4 deselected / 5 selected

tests/test_kaggle_assets.py::test_versioned_asset_is_recorded_in_local_manifest PASSED [ 20%]
tests/test_kaggle_assets.py::test_handles_reject_the_wrong_version_form[validate_model_upload_handle-owner/model/sklearn/main/1] PASSED [ 40%]
tests/test_kaggle_assets.py::test_handles_reject_the_wrong_version_form[validate_model_download_handle-owner/model/sklearn/main] PASSED [ 60%]
tests/test_kaggle_assets.py::test_model_upload_validates_package_before_network PASSED [ 80%]
tests/test_kaggle_assets.py::test_model_upload_rejects_a_corrupted_package_before_network PASSED [100%]

======================= 5 passed, 4 deselected in 0.01s ========================
```

**O que aconteceu:** cobrimos o registro local (`test_versioned_asset_is_recorded_in_local_manifest`), o formato dos handles (aula 02-1) e os dois caminhos de upload. Com isso, **todos** os testes da issue 02 e da 01 já foram estudados: rode a suíte completa e confira `38 passed` (os 22 originais mais os seus exercícios). Descrição dos cenários em [Catálogo de testes](testing/scenarios.md).

## Erros comuns

**1. `Pacote de modelo inválido: faltam metadata.json, sha256sums.txt; falta um .joblib, .pt ou .pth.`** Você apontou `--model-dir` para uma pasta que não é um pacote completo. Correção: gere os quatro itens e aponte para a pasta do pacote.

**2. `Hash divergente ou arquivo ausente: model.joblib.`** O `sha256sums.txt` foi gerado **antes** de o arquivo ser alterado, ou um arquivo foi trocado. Correção: regere o `sha256sums.txt` a partir dos arquivos finais, nunca à mão.

**3. `A versão do Model exige uma nota não vazia.`** `--version-notes ""` ou só espaços. Correção: escreva uma nota que ligue o modelo à execução e à versão dos dados (`run abc; dataset owner/data/versions/3`).

**4. Registrar o handle de upload (sem versão).** O registro recusa: o que vale é o handle com `/N`. Correção: confirme o número na aba de versões do recurso no Kaggle.

**5. Subir um `.env` por engano.** O `.gitignore` já o cobre, mas confira `git status` antes de cada commit. Se um token vazar, revogue-o no Kaggle imediatamente.

## Código completo desta aula

??? example "Arquivo completo: src/mqtt_ids/kaggle_assets.py"

    ```python
    --8<-- "src/mqtt_ids/kaggle_assets.py"
    ```

??? example "Arquivo completo: src/mqtt_ids/kaggle_assets_cli.py"

    ```python
    --8<-- "src/mqtt_ids/kaggle_assets_cli.py"
    ```

??? example "Arquivo completo: tests/test_kaggle_assets.py"

    ```python
    --8<-- "tests/test_kaggle_assets.py"
    ```

## Exercícios

Os exercícios continuam em `src/mqtt_ids/exercicios.py`. Eles automatizam um passo que o teste da aula fez à mão e leem o que o registro grava.

1. Escreva `write_sha256sums(directory, names)`, que grava `sha256sums.txt` na pasta, uma linha `hash␣␣nome` por arquivo (na ordem dada) usando o `sha256` do projeto. E escreva `published_handles(manifest_path)`, que devolve o dicionário `published_assets` do manifesto (ou `{}` se ainda não houver). O exercício está pronto quando este teste passar:

    ```python title="tests/test_exercicio_02_3.py"
    from pathlib import Path

    from mqtt_ids.exercicios import published_handles, write_sha256sums
    from mqtt_ids.kaggle_assets import (
        record_published_version,
        sha256,
        validate_model_package,
    )


    def test_write_sha256sums_makes_a_valid_model_package(tmp_path: Path) -> None:
        names = ["model.joblib", "metadata.json", "manifest.json"]
        for name in names:
            (tmp_path / name).write_text(name, encoding="utf-8")

        write_sha256sums(tmp_path, names)

        first_line = (tmp_path / "sha256sums.txt").read_text().splitlines()[0]
        assert first_line == f"{sha256(tmp_path / 'model.joblib')}  model.joblib"
        validate_model_package(tmp_path)


    def test_published_handles_reads_what_was_recorded(tmp_path: Path) -> None:
        manifest = tmp_path / "manifest.json"
        manifest.write_text('{"status": "completed"}\n', encoding="utf-8")

        assert published_handles(manifest) == {}

        record_published_version(manifest, "model", "owner/model/sklearn/base/2")
        record_published_version(manifest, "dataset", "owner/data/versions/3")

        assert published_handles(manifest) == {
            "model": "owner/model/sklearn/base/2",
            "dataset": "owner/data/versions/3",
        }
    ```

    ```bash title="$ Execução no terminal (na pasta do projeto)"
    uv run --locked pytest tests/test_exercicio_02_3.py
    ```

    Antes da solução:

    ```text title="Saída esperada (antes da solução)"
    E   ImportError: cannot import name 'published_handles' from 'mqtt_ids.exercicios' (...)
    ERROR tests/test_exercicio_02_3.py
    ```

??? tip "Solução"

    ```python title="src/mqtt_ids/exercicios.py (acrescente ao arquivo)"
    def write_sha256sums(directory: Path, names: list[str]) -> None:
        lines = [f"{sha256(directory / name)}  {name}\n" for name in names]
        (directory / "sha256sums.txt").write_text("".join(lines), encoding="utf-8")


    def published_handles(manifest_path: Path) -> dict[str, str]:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        return manifest.get("published_assets", {})
    ```

    Depois da solução: `2 passed`. O `sha256` já existe no projeto (aula 02-1) e o formato com **dois espaços** é o que `validate_model_package` espera; o `.get("published_assets", {})` cobre o manifesto que ainda não registrou nada.

## Quiz de fixação

??? question "1. Com suas palavras: por que o pacote de modelo é validado antes do upload e não depois?"

    Porque um modelo incompleto ou adulterado publicado já é um problema: ele fica no Kaggle com versão e handle. Validar antes impede que algo inválido saia da máquina, e a validação não depende de rede.

??? question "2. Por que o handle versionado é registrado em uma segunda etapa, depois do upload?"

    Porque a função de upload do KaggleHub não devolve o número `N` da versão criada. O operador confirma `N` no Kaggle e executa o comando de registro, que valida o handle versionado e o grava em `published_assets`.

**3. O que `manifest.setdefault("published_assets", {})` garante?**

- a) Que registrar um novo ativo não apaga os já registrados
- b) Que o manifesto é gravado em um arquivo temporário
- c) Que o handle registrado deixa de precisar de versão

??? question "Resposta da 3"

    **a)**. `setdefault` devolve a seção existente (ou cria uma vazia), então só a chave do ativo novo é acrescentada. O b) é papel do `.tmp` + `replace`; o c) é o oposto: o registro exige handle versionado.

??? question "4. Revisão da aula 02-1: por que `fullmatch` e não `match` nos validadores de handle?"

    `fullmatch` exige que o handle **inteiro** case com o padrão; `match` olha só o começo e o `$` aceita uma quebra de linha final. Com `fullmatch`, um handle copiado com `\n` sobrando é recusado.

## Commit

```bash title="$ Execução no terminal (na pasta do projeto)"
git add docs/02-3-publicar-e-recuperar.md docs/glossario.md docs/referencia.md docs/recursos.md course/ mkdocs.yml docs/issues/02-kaggle-ingestion.md
git commit -m "docs: aula 02-3 sobre publicação e recuperação de ativos versionados"
```

## Resumo

- Pacote de modelo = arquivo serializado + `metadata.json` + `manifest.json` + `sha256sums.txt`; validado **antes** da rede.
- Cada upload cria uma versão; o handle `…/N` é registrado em `published_assets` por escrita atômica.
- Credenciais ficam em `.env` (ignorado pelo Git); recursos nascem privados até a revisão manual.

## Fonte principal

[README do KaggleHub](https://github.com/Kaggle/kagglehub): leia upload e download de datasets e modelos, versões e autenticação.

## Para saber mais

- [joblib.load](https://joblib.readthedocs.io/en/latest/generated/joblib.load.html) e [PyTorch: salvar e carregar modelos](https://docs.pytorch.org/tutorials/beginner/saving_loading_models.html)
- [python-dotenv](https://github.com/theskumar/python-dotenv) e [argparse: subcomandos](https://docs.python.org/3/library/argparse.html#sub-commands)
- [Pesquisa sobre armazenamento e recuperação no Kaggle](research/kaggle-armazenamento-e-recuperacao.md)

!!! question "Ficou com dúvida?"

    O agente é o seu professor: pergunte o que não ficou claro, colando a mensagem de erro exata e o que você tentou. Para conversar com pessoas, veja as comunidades em [Recursos](recursos.md#comunidades).

**Próxima aula:** [03-1. O MQTT e os três ambientes de ataque](03-1-mqtt-e-os-tres-ambientes.md).
