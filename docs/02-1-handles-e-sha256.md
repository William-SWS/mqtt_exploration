# 02-1. Handles versionados e integridade com SHA-256

## Objetivos desta aula

Ao final desta aula você vai entender:

- o que é um **handle** do Kaggle, por que o handle de download **precisa** de versão e o de upload **não pode** ter;
- a diferença entre dado "baixado" e dado **verificado**, e como o SHA-256 em streaming prova a integridade;
- como uma expressão regular com `fullmatch` valida o formato antes de qualquer chamada de rede.

E vai ter construído: os quatro validadores de handle e a função `sha256` que sustentam todo o resto da issue 02.

**Ganho tangível:** `validate_dataset_download_handle("owner/data")` falha com uma mensagem clara, e `sha256(arquivo)` devolve o mesmo valor que o comando `sha256sum`.

## Onde estamos

Na [aula 01-3](01-3-runner-e-manifesto.md) você fechou a issue 01: o runner, a identidade e o manifesto. Agora começa a [issue 02](issues/02-kaggle-ingestion.md): trazer os três CSVs do Kaggle com **proveniência verificável**. Esta aula monta os dois alicerces (nomes de recurso e hashes); a 02-2 usa-os para adquirir dados e a 02-3 para publicar e recuperar ativos.

### Relembrando

??? question "1. Por que a identidade de uma execução usa JSON com chaves ordenadas antes do SHA-256?"

    Para o mesmo conteúdo sempre gerar o mesmo texto e, portanto, o mesmo hash, independentemente da ordem das chaves.

??? question "2. O que significa \"falhar cedo\" na validação do cenário?"

    Conferir a entrada antes de executar qualquer estágio, para que o erro apareça na hora e não depois de uma execução longa.

??? question "3. O que o `--locked` garante ao rodar `uv run`?"

    Que o ambiente segue o `uv.lock` sem resolver versões novas, falhando se o lockfile estiver desatualizado em relação ao `pyproject.toml`.

## Antes de começar

As aulas da issue 01 concluídas e a suíte verde:

--8<-- "course/includes/rodar-testes.md"

Nenhuma conta Kaggle é necessária nesta aula: tudo acontece localmente, sem rede.

## Conceitos

### Handle versionado

No Kaggle, cada recurso tem um **handle**: um texto que o identifica, no formato `dono/nome...`. Para um Dataset é `owner/slug`; para um Model é `owner/model/framework/variation`. O KaggleHub permite baixar uma **versão específica** (por exemplo `/versions/1`) ou, sem versão, "a mais recente".

Aí está o risco para a pesquisa: um handle sem versão aponta para um conteúdo que **muda** quando alguém publica uma nova versão. Dois colegas baixando "o mesmo dataset" em dias diferentes podem receber dados diferentes. Por isso a [ADR-022](DECISIONS.md#adr-022-aquisicao-kaggle-versionada-validada-e-promovida-atomicamente) estabelece: *download* exige versão explícita; *upload* usa o handle **sem** versão, porque é o Kaggle que cria o número da nova versão.

| Operação | Dataset | Model |
|---|---|---|
| Upload (cria nova versão) | `owner/slug` | `owner/model/framework/variation` |
| Download (versão fixa) | `owner/slug/versions/N` | `owner/model/framework/variation/N` |

Analogia: o handle sem versão é "a edição mais recente do livro"; o handle com versão é "o ISBN da 3ª edição". Para citar um resultado, só o segundo serve.

Fontes: [README do KaggleHub](https://github.com/Kaggle/kagglehub) (formato de handle e versões) e [Kaggle CLI: datasets](https://github.com/Kaggle/kaggle-cli/blob/main/docs/datasets.md) (cada nova versão exige uma nota, `-m`).

### Integridade verificada com SHA-256 em streaming

Há três níveis de confiança em um arquivo baixado: (1) o **cache** diz "já tenho um arquivo com esse nome"; (2) a **transferência** diz "o download terminou sem erro de rede"; (3) a **verificação local** compara o **hash** do conteúdo com o valor esperado. Só o terceiro prova que os bytes são os certos: um arquivo parcial, corrompido ou trocado pode estar no cache e passar na transferência.

O **SHA-256** transforma qualquer arquivo em 64 caracteres hexadecimais; um único byte diferente muda tudo. O projeto guarda os hashes esperados dos três CSVs em `RAW_HASHES` ([ADR-005](DECISIONS.md#adr-005-publicacao-e-proveniencia-dos-dados)).

Os CSVs podem ser grandes. Ler tudo na memória para calcular o hash seria desperdício. Por isso o hash é calculado em **streaming**: lemos blocos de 1 MiB e alimentamos o objeto de hash com `update()`. Chamadas repetidas equivalem a uma chamada com tudo concatenado, então o resultado é o mesmo. A construção `iter(função, sentinela)` chama a função repetidamente e para quando ela devolve a sentinela, aqui `b""` (fim do arquivo).

Fontes: [hashlib](https://docs.python.org/3/library/hashlib.html) (`sha256`, `update`, `hexdigest`) e [funções embutidas: `iter`](https://docs.python.org/3/library/functions.html).

### Validação antecipada com expressão regular

Uma **expressão regular** descreve um formato de texto. Para um handle de download de Dataset:

```text
^[^/]+/[^/]+/versions/[1-9][0-9]*$
```

Leia assim: um trecho sem `/`, uma barra, outro trecho sem `/`, `/versions/`, e um número que começa em 1–9 (sem zero à esquerda, e a versão 0 não existe).

O ponto sutil é `fullmatch`: ele exige que a **string inteira** case com o padrão. Já `match` só olha o começo, e o `$` aceita uma quebra de linha no final. Com `fullmatch`, um handle copiado com `\n` sobrando é recusado em vez de passar e quebrar mais adiante. Validar antes da chamada remota é o "falhar cedo" da aula 01-2, agora aplicado a recursos remotos.

Fonte: [módulo re](https://docs.python.org/3/library/re.html) (`fullmatch`, `match` e as âncoras `^` e `$`).

## Ponte teoria → projeto

A [issue 02](issues/02-kaggle-ingestion.md) pede: "handles sem `/versions/N` são rejeitados antes do download", "hash divergente interrompe o estágio" e "`Intrusion.csv`, `DoS.csv` e `MitM.csv` são exigidos". A [ADR-022](DECISIONS.md#adr-022-aquisicao-kaggle-versionada-validada-e-promovida-atomicamente) decide validar nomes e SHA-256 e usar só versões fixadas; a [ADR-005](DECISIONS.md#adr-005-publicacao-e-proveniencia-dos-dados) registra a origem (DOI) e os hashes. Para a sua missão: qualquer número do portfólio poderá apontar para uma versão e hashes exatos dos dados.

## Mão na massa

### Passo 1 — Os hashes esperados e os formatos de handle

Abra `src/mqtt_ids/kaggle_assets.py`. O começo do arquivo guarda os hashes dos CSVs e os padrões dos quatro tipos de handle:

```python title="src/mqtt_ids/kaggle_assets.py" linenums="14"
RAW_HASHES = {  # (1)!
    "Intrusion.csv": "730f65a2bd388b973f7088a28b8a37a3a0a56062ad059d90e95da9fffed93518",
    "DoS.csv": "e935c819f8bc08898135180029bde0a685e9c5676d5277cacf66d917bb98d4e1",
    "MitM.csv": "bfee47413bcf82f3b1433d51db63629a1b61d1a40fc704f545f23c7350daa5d0",
}

_DATASET_UPLOAD = re.compile(r"^[^/]+/[^/]+$")  # (2)!
_DATASET_DOWNLOAD = re.compile(r"^[^/]+/[^/]+/versions/[1-9][0-9]*$")  # (3)!
_MODEL_UPLOAD = re.compile(r"^[^/]+/[^/]+/[^/]+/[^/]+$")
_MODEL_DOWNLOAD = re.compile(r"^[^/]+/[^/]+/[^/]+/[^/]+/[1-9][0-9]*$")
_CATEGORIES = frozenset({"raw", "interim", "processed"})
PROVENANCE_FILE = "kaggle-provenance.json"
```

1.  Nome do arquivo → SHA-256 esperado. Os nomes são exigidos exatamente assim, sem renomeação silenciosa.
2.  Upload de Dataset: dois trechos, `owner/slug`, sem versão.
3.  Download de Dataset: `owner/slug/versions/N`, com `N` inteiro positivo.

As duas últimas linhas serão usadas na aula 02-2 (categorias de dados e o arquivo de proveniência).

### Passo 2 — Os validadores e o erro próprio

Primeiro a exceção, no mesmo estilo do `ScenarioError`:

```python title="src/mqtt_ids/kaggle_assets.py" linenums="28"
class KaggleAssetError(ValueError):
    """Indica que um ativo não atende ao contrato antes da chamada remota."""
```

Depois os validadores de Dataset (os de Model, nas linhas 81–94, têm a mesma forma):

```python title="src/mqtt_ids/kaggle_assets.py" linenums="65"
def validate_dataset_upload_handle(handle: str) -> None:
    """Exige handle sem versão para criar ou publicar uma nova versão."""
    if not _DATASET_UPLOAD.fullmatch(handle):  # (1)!
        raise KaggleAssetError(
            "Handle de upload de Dataset deve ser 'owner/slug', sem versão."  # (2)!
        )


def validate_dataset_download_handle(handle: str) -> None:
    """Exige versão explícita para restaurar dados reproduzíveis."""
    if not _DATASET_DOWNLOAD.fullmatch(handle):
        raise KaggleAssetError(
            "Handle de download de Dataset deve ser 'owner/slug/versions/N'."
        )
```

1.  `fullmatch` exige que o handle inteiro case com o padrão.
2.  A mensagem diz o formato correto: quem erra sabe como corrigir. A função devolve `None` quando está tudo certo; só falha com exceção.

Rode os quatro validadores com casos certos e errados:

```bash title="$ Execução no terminal (na pasta do projeto)"
uv run --locked python -c "
from mqtt_ids.kaggle_assets import *
casos = [
    (validate_dataset_download_handle, 'owner/data/versions/3'),
    (validate_dataset_download_handle, 'owner/data'),
    (validate_dataset_download_handle, 'owner/data/versions/0'),
    (validate_dataset_upload_handle, 'owner/data/versions/3'),
    (validate_model_download_handle, 'owner/model/sklearn/baseline/2'),
    (validate_model_upload_handle, 'owner/model/sklearn/baseline'),
]
for funcao, handle in casos:
    try:
        funcao(handle)
        print('OK  ', handle)
    except KaggleAssetError as erro:
        print('ERRO', handle, '->', erro)
"
```

```text title="Saída esperada"
OK   owner/data/versions/3
ERRO owner/data -> Handle de download de Dataset deve ser 'owner/slug/versions/N'.
ERRO owner/data/versions/0 -> Handle de download de Dataset deve ser 'owner/slug/versions/N'.
ERRO owner/data/versions/3 -> Handle de upload de Dataset deve ser 'owner/slug', sem versão.
OK   owner/model/sklearn/baseline/2
OK   owner/model/sklearn/baseline
```

**O que aconteceu:** cada validador aceita só o seu formato. Repare nos dois erros de download: faltou a versão em `owner/data`, e a versão `0` é recusada pelo `[1-9]`. E o handle **com** versão é recusado no upload, porque quem cria o número é o Kaggle.

??? question "Pare e pense: o que `fullmatch` faz com `'owner/data/versions/3\\n'` (com uma quebra de linha no fim)?"

    Recusa. Com o padrão `^...$`, o `match` aceitaria (o `$` vale também antes da quebra final), mas `fullmatch` exige que a string inteira case: `False` para o `\n` sobrando. Foi o que verificamos no replay: `fullmatch` devolve `False` e `match` devolve um resultado.

### Passo 3 — SHA-256 em streaming

```python title="src/mqtt_ids/kaggle_assets.py" linenums="56"
def sha256(path: Path) -> str:
    """Calcula SHA-256 em streaming, sem carregar o arquivo integralmente."""
    digest = hashlib.sha256()  # (1)!
    with path.open("rb") as source:  # (2)!
        for block in iter(lambda: source.read(1024 * 1024), b""):  # (3)!
            digest.update(block)  # (4)!
    return digest.hexdigest()
```

1.  Cria o objeto de hash vazio.
2.  Abre em modo binário (`"rb"`): hash é sobre **bytes**, não sobre texto decodificado; e o `with` fecha o arquivo no fim.
3.  `iter(f, b"")` chama `f()` (lê 1 MiB) até vir `b""`, o fim do arquivo. Cada bloco é uma passagem do `for`.
4.  Atualiza o hash com o bloco; no fim o resultado é o mesmo de hashear o arquivo inteiro de uma vez.

Compare com o `sha256sum` do sistema, em um arquivo de verdade:

```bash title="$ Execução no terminal (na pasta do projeto)"
printf 'hello' > /tmp/a.txt
uv run --locked python -c "
from pathlib import Path
from mqtt_ids.kaggle_assets import sha256
print(sha256(Path('/tmp/a.txt')))
"
sha256sum /tmp/a.txt
printf 'hellp' > /tmp/b.txt
sha256sum /tmp/b.txt
```

```text title="Saída esperada"
2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824
2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824  /tmp/a.txt
fdd7585e08c4e2afd71dcabdb4636c89d557a3f42db9e2040c8bbd1708aa4ce7  /tmp/b.txt
```

**O que aconteceu:** nossa função e o `sha256sum` concordam. E trocar **uma** letra (`hello` → `hellp`) mudou o hash inteiro: é isso que torna o SHA-256 um detector de corrupção. (No macOS use `shasum -a 256`.)

??? question "Pare e pense: quanta memória o streaming economiza em um arquivo de 300 MB?"

    Muita. No replay, com um arquivo de 300 MB, o pico de memória do processo ficou em torno de 45 MiB usando `sha256` (streaming), contra cerca de 301 MiB ao ler tudo com `Path.read_bytes()`. Os valores variam, mas a proporção é a ideia: o streaming usa memória constante.

Limpe os rascunhos: `rm /tmp/a.txt /tmp/b.txt`.

## Testando

O teste dos validadores é parametrizado (como na aula 01-2): cada linha da tabela é um par validador/handle **errado** e o teste espera `KaggleAssetError`.

```python title="tests/test_kaggle_assets.py" linenums="106"
@pytest.mark.parametrize(  # (1)!
    ("validator", "handle"),
    [
        (kaggle_assets.validate_dataset_upload_handle, "owner/data/versions/1"),
        (kaggle_assets.validate_dataset_download_handle, "owner/data"),
        (kaggle_assets.validate_model_upload_handle, "owner/model/sklearn/main/1"),
        (kaggle_assets.validate_model_download_handle, "owner/model/sklearn/main"),
    ],
)
def test_handles_reject_the_wrong_version_form(validator: object, handle: str) -> None:
    with pytest.raises(KaggleAssetError):
        validator(handle)  # type: ignore[operator]
```

1.  O primeiro elemento de cada tupla é a **própria função**: em Python funções são objetos e podem ir numa tabela de casos. Os quatro casos cobrem os quatro erros: upload com versão, download sem versão e o mesmo para Model.

```bash title="$ Execução no terminal (na pasta do projeto)"
uv run --locked pytest tests/test_kaggle_assets.py -v -k "handles or corrupted"
```

```text title="Saída esperada"
collecting ... collected 9 items / 4 deselected / 5 selected

tests/test_kaggle_assets.py::test_handles_reject_the_wrong_version_form[validate_dataset_upload_handle-owner/data/versions/1] PASSED [ 20%]
tests/test_kaggle_assets.py::test_handles_reject_the_wrong_version_form[validate_dataset_download_handle-owner/data] PASSED [ 40%]
tests/test_kaggle_assets.py::test_handles_reject_the_wrong_version_form[validate_model_upload_handle-owner/model/sklearn/main/1] PASSED [ 60%]
tests/test_kaggle_assets.py::test_handles_reject_the_wrong_version_form[validate_model_download_handle-owner/model/sklearn/main] PASSED [ 80%]
tests/test_kaggle_assets.py::test_model_upload_rejects_a_corrupted_package_before_network PASSED [100%]

======================= 5 passed, 4 deselected in 0.01s ========================
```

**Como ler a saída:** `-k "handles or corrupted"` seleciona só os testes cujo nome contém essas palavras; os outros quatro aparecem como `deselected`. O teste de pacote corrompido usa o `sha256` desta aula e será estudado na 02-3. O catálogo completo está em [Catálogo de testes](testing/scenarios.md).

## Erros comuns

**1. Usar handle sem versão no download.**

```text title="Saída"
Handle de download de Dataset deve ser 'owner/slug/versions/N'.
```

Correção: acrescente `/versions/N` com a versão que você confirmou no Kaggle.

**2. Usar `versions/0`.** A mesma mensagem: as versões começam em 1, e o padrão `[1-9][0-9]*` recusa o zero.

**3. Handle com quebra de linha ou espaço no fim** (comum ao copiar de um arquivo `.env`). `fullmatch` recusa. Correção: remova o espaço ou o `\n` sobrando.

**4. Confundir os dois handles de Model.** O de download tem **cinco** trechos (`owner/model/framework/variation/N`) e o de upload tem **quatro**; trocar um pelo outro dá a mensagem do formato correto.

## Código completo desta aula

??? example "Arquivo completo: src/mqtt_ids/kaggle_assets.py"

    ```python
    --8<-- "src/mqtt_ids/kaggle_assets.py"
    ```

??? example "Arquivo completo: tests/test_kaggle_assets.py"

    ```python
    --8<-- "tests/test_kaggle_assets.py"
    ```

## Exercícios

Os dois exercícios continuam em `src/mqtt_ids/exercicios.py`. Eles **reaproveitam** as funções já existentes em `kaggle_assets.py`: antes de reescrever, procure o que o projeto já tem.

1. Escreva `parse_dataset_handle(handle)`, que valida um handle de download de Dataset e devolve `(owner, slug, versão_inteira)`. E escreva `tampered_files(directory, expected)`, que recebe um mapa nome→hash esperado e devolve, em ordem alfabética, os nomes dos arquivos cujo hash difere **ou** que não existem. O exercício está pronto quando este teste passar:

    ```python title="tests/test_exercicio_02_1.py"
    from pathlib import Path

    import pytest

    from mqtt_ids.exercicios import parse_dataset_handle, tampered_files
    from mqtt_ids.kaggle_assets import KaggleAssetError, sha256


    def test_parse_dataset_handle_returns_owner_slug_and_version() -> None:
        assert parse_dataset_handle("owner/data/versions/3") == ("owner", "data", 3)


    @pytest.mark.parametrize("handle", ["owner/data", "owner/data/versions/0"])
    def test_parse_dataset_handle_rejects_implicit_versions(handle: str) -> None:
        with pytest.raises(KaggleAssetError):
            parse_dataset_handle(handle)


    def test_tampered_files_reports_changed_and_missing_files(tmp_path: Path) -> None:
        good = tmp_path / "good.csv"
        good.write_bytes(b"ok")
        bad = tmp_path / "bad.csv"
        bad.write_bytes(b"changed")
        expected = {
            "good.csv": sha256(good),
            "bad.csv": "0" * 64,
            "missing.csv": "1" * 64,
        }

        assert tampered_files(tmp_path, expected) == ["bad.csv", "missing.csv"]
    ```

    ```bash title="$ Execução no terminal (na pasta do projeto)"
    uv run --locked pytest tests/test_exercicio_02_1.py
    ```

    Antes da solução:

    ```text title="Saída esperada (antes da solução)"
    E   ImportError: cannot import name 'parse_dataset_handle' from 'mqtt_ids.exercicios' (...)
    ERROR tests/test_exercicio_02_1.py
    ```

??? tip "Solução"

    ```python title="src/mqtt_ids/exercicios.py (acrescente ao arquivo)"
    from mqtt_ids.kaggle_assets import sha256, validate_dataset_download_handle  # junto dos imports


    def parse_dataset_handle(handle: str) -> tuple[str, str, int]:
        validate_dataset_download_handle(handle)
        owner, slug, _, version = handle.split("/")
        return owner, slug, int(version)


    def tampered_files(directory: Path, expected: dict[str, str]) -> list[str]:
        tampered = []
        for name, expected_hash in sorted(expected.items()):
            path = directory / name
            if not path.is_file() or sha256(path) != expected_hash:
                tampered.append(name)
        return tampered
    ```

    Depois da solução: `4 passed`. Primeiro valida (falhar cedo), depois divide: só chega ao `split` um handle que já tem o formato certo. Em `tampered_files`, o `is_file()` antes do hash evita um `FileNotFoundError` e conta o arquivo ausente como adulterado.

## Quiz de fixação

??? question "1. Com suas palavras: por que o handle de download exige versão e o de upload não pode ter?"

    Sem versão o handle aponta para a versão mais recente, que muda quando alguém publica: o resultado deixa de ser reproduzível. No upload, quem atribui o número da nova versão é o Kaggle, então o handle sem versão identifica o recurso ao qual a nova versão será acrescentada.

??? question "2. Por que o cache do KaggleHub não prova a integridade dos dados?"

    O cache só garante que existe um arquivo com aquele nome. Só a comparação do SHA-256 calculado com o esperado prova que os bytes são os certos; um arquivo parcial ou corrompido também pode estar no cache.

**3. Por que a função `sha256` lê o arquivo em blocos de 1 MiB?**

- a) Para usar memória constante, sem carregar o arquivo inteiro de uma vez
- b) Para que o hash de cada bloco seja diferente do hash do arquivo todo
- c) Para o hash ficar mais curto quando o arquivo for muito grande

??? question "Resposta da 3"

    **a)**. Chamadas repetidas de `update` equivalem a uma só com tudo concatenado, então o resultado é o mesmo com memória constante. O b) está errado porque o hash final é igual ao do arquivo inteiro; o c) porque o SHA-256 sempre tem 64 caracteres.

??? question "4. Revisão da aula 01-2: qual a vantagem de uma exceção própria, como `KaggleAssetError`?"

    Dá um nome ao problema, de modo que a interface de linha de comando capture só erros de contrato (e mostre a mensagem) e deixe os bugs de verdade subirem como exceções comuns.

## Commit

```bash title="$ Execução no terminal (na pasta do projeto)"
git add docs/02-1-handles-e-sha256.md docs/glossario.md docs/referencia.md docs/recursos.md course/ mkdocs.yml
git commit -m "docs: aula 02-1 sobre handles versionados e SHA-256"
```

## Resumo

- Download usa `owner/slug/versions/N`; upload usa `owner/slug` (o Kaggle cria o `N`).
- Integridade se prova comparando SHA-256 calculado em streaming com o valor esperado.
- `fullmatch` valida o formato inteiro antes de qualquer rede.

## Fonte principal

[README do KaggleHub](https://github.com/Kaggle/kagglehub): leia as seções de download e upload, com o formato dos handles e as versões.

## Para saber mais

- [Kaggle CLI: datasets](https://github.com/Kaggle/kaggle-cli/blob/main/docs/datasets.md)
- [hashlib](https://docs.python.org/3/library/hashlib.html), [re](https://docs.python.org/3/library/re.html) e [funções embutidas](https://docs.python.org/3/library/functions.html)

!!! question "Ficou com dúvida?"

    O agente é o seu professor: pergunte o que não ficou claro, colando a mensagem de erro exata e o que você tentou. Para conversar com pessoas, veja as comunidades em [Recursos](recursos.md#comunidades).

**Próxima aula:** [02-2. Aquisição atômica](02-2-aquisicao-atomica.md).
