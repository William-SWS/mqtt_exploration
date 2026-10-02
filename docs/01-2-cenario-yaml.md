# 01-2. Cenário YAML seguro e validado

## Objetivos desta aula

Ao final desta aula você vai entender:

- por que lemos YAML com `safe_load` e por que validamos o contrato **antes** de executar qualquer coisa;
- como uma `dataclass` imutável e uma exceção própria deixam o código honesto sobre o que é um cenário válido;
- como testar muitos casos de erro com um único teste parametrizado.

E vai ter construído: o carregador de cenários (`load_scenario`) e a bateria de testes que o protege.

**Ganho tangível:** um YAML válido vira um `Scenario`, e qualquer erro (chave a mais, seed booleana, sintaxe quebrada) produz uma mensagem clara em vez de uma execução pela metade.

## Onde estamos

Na [aula 01-1](01-1-ambiente-e-pacote.md) você montou o ambiente reproduzível e importou `mqtt_ids`. Agora damos ao runner a sua primeira entrada: o **cenário**, o arquivo YAML que descreve uma execução. Isto cobre o critério "configuração ausente, desconhecida ou inválida falha antes de executar qualquer estágio" da [issue 01](issues/01-project-runner.md). Na próxima aula (01-3) o runner consome o `Scenario` que você constrói aqui.

### Relembrando

Responda de memória antes de seguir:

??? question "1. O que o `uv.lock` guarda que o `pyproject.toml` não guarda?"

    As versões **exatas** de todos os pacotes resolvidos. O `pyproject.toml` só declara versões mínimas e a intenção do projeto.

??? question "2. Por que rodamos `uv run --locked python ...` em vez de `python3 ...`?"

    O `uv run` entra no ambiente do projeto (onde `mqtt_ids` está instalado) e o `--locked` impede que ele resolva versões novas. Com `python3` solto, o pacote não é encontrado.

## Antes de começar

A aula 01-1 precisa estar concluída: ambiente criado e testes verdes.

--8<-- "course/includes/rodar-testes.md"

Você deve ver `22 passed`. Não há ferramenta nova nesta aula: o PyYAML já está nas dependências do `pyproject.toml`.

## Conceitos

### YAML seguro e contrato de configuração

**YAML** é um formato de texto para dados aninhados (mapas, listas, números, textos), muito usado em configuração porque é legível. O arquivo `configs/diagnostics.yaml` é um exemplo mínimo.

O PyYAML tem duas portas de leitura. `yaml.load` é tão poderoso quanto `pickle.load`: pode construir objetos Python arbitrários e **executar funções** presentes no arquivo. `yaml.safe_load` aceita só as marcações padrão do YAML (números, textos, listas, mapas) e se recusa a construir classes. Como um cenário pode vir de qualquer lugar (outro colega, um download), usamos sempre `safe_load` ([ADR-016](DECISIONS.md#adr-016-configuracao-registries-e-manifests)).

Ler com segurança não basta: o resultado ainda é um dicionário solto, e o YAML tem armadilhas. Por exemplo, `seed: true` é lido como o booleano `True`, e em Python `True` é um `int`. Por isso o código **valida o contrato** (chaves exatas, tipos certos) e falha cedo, antes de qualquer estágio rodar. "Falhar cedo" evita o pior dos mundos: uma execução de horas que descobre no fim que a configuração estava errada.

Analogia: `safe_load` é o segurança da porta que revista a bagagem; a validação é o recepcionista que confere se o seu nome está na lista.

Fonte: [documentação do PyYAML](https://pyyaml.org/wiki/PyYAMLDocumentation).

### Dados imutáveis e erro com nome próprio

Uma **dataclass** é uma classe que o Python completa para você (`__init__`, `__repr__`, `__eq__`) a partir dos campos declarados. Com `frozen=True`, atribuir a um campo depois de criado gera `FrozenInstanceError`: o objeto vira somente leitura.

Para um cenário isso importa: se a identidade de uma execução é calculada a partir do cenário (aula 01-3), ninguém pode alterá-lo no meio do caminho.

Já `ScenarioError` é uma **exceção própria**, filha de `ValueError`. Dar um nome ao erro permite que a interface de linha de comando capture só os problemas de configuração e trate o resto como bug de verdade.

Fonte: [módulo dataclasses](https://docs.python.org/3/library/dataclasses.html).

### Testes parametrizados com `tmp_path`

Cinco cenários inválidos têm a mesma estrutura de teste: escreva um arquivo, carregue-o, espere um erro com certa mensagem. Em vez de cinco funções iguais, o `@pytest.mark.parametrize` roda **uma função uma vez por linha** de uma tabela de casos. O `tmp_path` entrega, a cada teste, uma pasta temporária própria, de modo que nenhum teste toca o repositório. E `pytest.raises(..., match=...)` confere que o erro aconteceu **e** que a mensagem contém o texto esperado (o `match` usa busca por expressão regular).

Fontes: [tmp_path](https://docs.pytest.org/en/stable/how-to/tmp_path.html), [parametrize](https://docs.pytest.org/en/stable/how-to/parametrize.html) e [pytest.raises](https://docs.pytest.org/en/stable/how-to/assert.html).

## Ponte teoria → projeto

A [issue 01](issues/01-project-runner.md) pede validação antecipada, e a [ADR-016](DECISIONS.md#adr-016-configuracao-registries-e-manifests) fixa: "`yaml.safe_load`; campos desconhecidos/ausentes falham cedo". A [ADR-019](DECISIONS.md#adr-019-cobertura-comportamental-do-runner-minimo) manda cobrir isso com testes de comportamento e `tmp_path`, sem tocar dados reais. Para a sua missão, é o que permite afirmar, num portfólio, que uma execução só começa com configuração conferida.

## Mão na massa

### Passo 1 — Conhecer o contrato do cenário

O cenário mínimo tem uma seção `run` com `name` e `seed`. A seção `dataset` é opcional e será estudada na aula 02-2. Veja o arquivo do projeto:

```yaml title="configs/diagnostics.yaml" linenums="1"
run:
  name: diagnostics  # (1)!
  seed: 20260822  # (2)!
```

1.  Nome humano da execução. Entra na identidade e no manifesto.
2.  Semente de aleatoriedade. Precisa ser um inteiro: guardar a seed no cenário é o que torna o resultado repetível.

Para ver o que o PyYAML entrega antes de qualquer validação, rode:

```bash title="$ Execução no terminal (na pasta do projeto)"
uv run --locked python -c "
import yaml
print(yaml.safe_load(open('configs/diagnostics.yaml')))
print(yaml.safe_load('seed: true'), yaml.safe_load('seed: 7'), yaml.safe_load('seed: \"7\"'))
"
```

```text title="Saída esperada"
{'run': {'name': 'diagnostics', 'seed': 20260822}}
{'seed': True} {'seed': 7} {'seed': '7'}
```

**O que aconteceu:** o YAML virou dicionários Python. Repare que `true` virou o booleano `True`, `7` virou um inteiro e `"7"` (entre aspas) virou texto. Por isso a validação precisa distinguir esses tipos.

??? question "Pare e pense: o que acontece se o arquivo tiver `!!python/object/apply:os.system [\"echo pwned\"]`?"

    Com `safe_load`, nada é executado: ele levanta `ConstructorError` ("could not determine a constructor for the tag ...python/object/apply:os.system"). Com `yaml.load` e um loader inseguro, o comando rodaria.

### Passo 2 — A exceção própria e o `Scenario` imutável

Abra `src/mqtt_ids/config.py`. Comece pelos imports e pela exceção:

```python title="src/mqtt_ids/config.py" linenums="3"
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


class ScenarioError(ValueError):  # (1)!
    """Indica um cenário ausente ou incompatível com o contrato mínimo."""
```

1.  Herdar de `ValueError` diz que o problema é um **valor** inválido, e dá um nome próprio para o `except` da CLI pegar só isto.

Agora o objeto que representa um cenário **já validado**:

```python title="src/mqtt_ids/config.py" linenums="36"
@dataclass(frozen=True)  # (1)!
class Scenario:
    """Configuração já validada do runner."""

    name: str
    seed: int
    dataset: DatasetConfig | None = None  # (2)!

    def as_dict(self) -> dict[str, Any]:  # (3)!
        resolved: dict[str, Any] = {"run": {"name": self.name, "seed": self.seed}}
        if self.dataset is not None:
            resolved["dataset"] = self.dataset.as_dict()
        return resolved
```

1.  `frozen=True` torna o objeto somente leitura: o cenário não muda depois de validado.
2.  O dataset é opcional (`None` por padrão). A classe `DatasetConfig` aparece na aula 02-2.
3.  Devolve a **configuração resolvida** como dicionário simples. É ela que a aula 01-3 transforma em identidade e grava no manifesto.

Confira a imutabilidade na prática:

```bash title="$ Execução no terminal (na pasta do projeto)"
uv run --locked python -c "
from mqtt_ids.config import Scenario
s = Scenario(name='a', seed=1)
try:
    s.seed = 2
except Exception as e:
    print(type(e).__name__, e)
print(s.as_dict())
"
```

```text title="Saída esperada"
FrozenInstanceError cannot assign to field 'seed'
{'run': {'name': 'a', 'seed': 1}}
```

**O que aconteceu:** a atribuição foi barrada; `as_dict()` mostra a forma que será gravada no manifesto.

### Passo 3 — Ler e validar com `load_scenario`

A função em duas partes. Primeiro, **achar e ler** o arquivo:

```python title="src/mqtt_ids/config.py" linenums="51"
def load_scenario(path: Path) -> Scenario:
    """Lê um YAML seguro e falha antes de qualquer estágio ser executado."""
    if not path.is_file():
        raise ScenarioError(f"Cenário não encontrado: {path}")  # (1)!
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))  # (2)!
    except yaml.YAMLError as error:
        raise ScenarioError(f"YAML inválido em {path}: {error}") from error  # (3)!
    if not isinstance(raw, dict):
        raise ScenarioError("O cenário deve ser um mapa YAML.")  # (4)!
```

1.  Arquivo ausente vira um erro claro, não um `FileNotFoundError` solto.
2.  `safe_load`, com a codificação explícita para o texto acentuado funcionar em qualquer sistema.
3.  `from error` mantém a causa original anexada ao erro, útil para depurar.
4.  Um YAML válido pode ser uma lista ou um número; o contrato exige um mapa.

Depois, **conferir o contrato**:

```python title="src/mqtt_ids/config.py" linenums="61"
    if "run" not in raw or not set(raw).issubset({"run", "dataset"}):
        raise ScenarioError(
            "O cenário aceita somente a chave obrigatória 'run' e a opcional 'dataset'."
        )  # (1)!
    run = raw["run"]
    if not isinstance(run, dict) or set(run) != {"name", "seed"}:
        raise ScenarioError("'run' deve conter exatamente 'name' e 'seed'.")  # (2)!
    name, seed = run["name"], run["seed"]
    if not isinstance(name, str) or not name.strip():
        raise ScenarioError("'run.name' deve ser uma string não vazia.")
    if not isinstance(seed, int) or isinstance(seed, bool):  # (3)!
        raise ScenarioError("'run.seed' deve ser um inteiro.")
    return Scenario(
        name=name.strip(), seed=seed, dataset=_load_dataset(raw.get("dataset"))
    )
```

1.  Chave a mais ou `run` ausente falha. Um erro de digitação (`seeed`) não passa em silêncio.
2.  `set(run) != {"name", "seed"}` exige **exatamente** essas chaves: nem falta, nem sobra.
3.  Em Python `True` é um `int` (`isinstance(True, int)` é verdadeiro). Sem a segunda condição, `seed: true` passaria como `1`.

Teste os quatro caminhos com arquivos de verdade. Crie estes dois cenários numa pasta de rascunho (por exemplo, `/tmp/cenarios`):

```yaml title="/tmp/cenarios/extra.yaml"
run:
  name: smoke
  seed: 7
verbose: true
```

```yaml title="/tmp/cenarios/bool.yaml"
run:
  name: smoke
  seed: true
```

```bash title="$ Execução no terminal (na pasta do projeto)"
uv run --locked python -c "
from pathlib import Path
from mqtt_ids.config import load_scenario, ScenarioError
for path in ['configs/diagnostics.yaml', '/tmp/cenarios/extra.yaml', '/tmp/cenarios/bool.yaml']:
    try:
        print(load_scenario(Path(path)))
    except ScenarioError as error:
        print('ScenarioError:', error)
"
```

```text title="Saída esperada"
Scenario(name='diagnostics', seed=20260822, dataset=None)
ScenarioError: O cenário aceita somente a chave obrigatória 'run' e a opcional 'dataset'.
ScenarioError: 'run.seed' deve ser um inteiro.
```

**O que aconteceu:** o primeiro arquivo virou um `Scenario`; os outros dois foram recusados com mensagens que dizem exatamente o que corrigir.

### Passo 4 — Ver a falha chegar à linha de comando

A CLI ainda será explicada na aula 01-3, mas já dá para ver o efeito: um cenário inválido **não cria nada**.

```bash title="$ Execução no terminal (na pasta do projeto)"
uv run --locked mqtt-ids --scenario /tmp/cenarios/extra.yaml --output-dir /tmp/cenarios/runs
ls /tmp/cenarios
```

```text title="Saída esperada"
usage: mqtt-ids [-h] --scenario SCENARIO [--stage {diagnostics,acquire}]
                [--resume] [--output-dir OUTPUT_DIR]
mqtt-ids: error: O cenário aceita somente a chave obrigatória 'run' e a opcional 'dataset'.
bool.yaml
extra.yaml
```

**O que aconteceu:** o comando terminou com código de saída 2 (erro de uso; o shell o mostra em `$?` no bash/zsh e em `$status` no fish) e a pasta `runs` **não existe**: a validação falhou antes de qualquer estágio, que é exatamente o critério de aceite.

## Testando

Os testes que protegem o carregador já existem. Veja-os:

```python title="tests/test_config.py" linenums="32"
@pytest.mark.parametrize(  # (1)!
    ("content", "message"),
    [
        ("unexpected: true\n", "somente a chave obrigatória"),
        (
            "run:\n name: smoke\n",
            "exatamente 'name' e 'seed'",
        ),
        (
            "run:\n  name: ''\n  seed: 7\n",
            "string não vazia",
        ),
        (
            "run:\n  name: smoke\n  seed: true\n",
            "deve ser um inteiro",
        ),
        ("run: [\n", "YAML inválido"),
    ],
)
def test_invalid_scenarios_raise_clear_error(
    tmp_path: Path, content: str, message: str
) -> None:
    scenario_path = tmp_path / "invalid.yaml"
    scenario_path.write_text(content, encoding="utf-8")  # (2)!

    with pytest.raises(ScenarioError, match=message):  # (3)!
        load_scenario(scenario_path)
```

1.  Uma tabela de cinco casos: cada tupla é `(conteúdo do YAML, trecho esperado da mensagem)`. O pytest roda a função uma vez por linha.
2.  `tmp_path` é uma pasta temporária só deste teste: nada do repositório é tocado ([ADR-019](DECISIONS.md#adr-019-cobertura-comportamental-do-runner-minimo)).
3.  Passa se o erro for `ScenarioError` **e** a mensagem contiver o trecho esperado.

O mesmo arquivo ainda tem o teste do cenário válido com `dataset` (aula 02-2) e o do arquivo ausente. Rode só este arquivo, com `-v` para ver cada caso:

```bash title="$ Execução no terminal (na pasta do projeto)"
uv run --locked pytest tests/test_config.py -v
```

```text title="Saída esperada"
collecting ... collected 7 items

tests/test_config.py::test_scenario_loads_versioned_dataset_provenance PASSED [ 14%]
tests/test_config.py::test_invalid_scenarios_raise_clear_error[unexpected: true\n-somente a chave obrigat\xf3ria] PASSED [ 28%]
tests/test_config.py::test_invalid_scenarios_raise_clear_error[run:\n name: smoke\n-exatamente 'name' e 'seed'] PASSED [ 42%]
tests/test_config.py::test_invalid_scenarios_raise_clear_error[run:\n  name: ''\n  seed: 7\n-string n\xe3o vazia] PASSED [ 57%]
tests/test_config.py::test_invalid_scenarios_raise_clear_error[run:\n  name: smoke\n  seed: true\n-deve ser um inteiro] PASSED [ 71%]
tests/test_config.py::test_invalid_scenarios_raise_clear_error[run: [\n-YAML inv\xe1lido] PASSED [ 85%]
tests/test_config.py::test_missing_scenario_raises_clear_error PASSED    [100%]

============================== 7 passed in 0.03s ===============================
```

**Como ler a saída:** com `-v` cada teste ganha uma linha; a parte entre colchetes identifica o caso da tabela (os acentos aparecem escapados, `\xf3`, só no nome do caso). Sete linhas, sete `PASSED`: o teste parametrizado virou cinco testes. Os cenários catalogados estão em [Catálogo de testes](testing/scenarios.md).

## Erros comuns

**1. `seed: "7"` (com aspas).** O YAML lê um texto, e a validação recusa: `'run.seed' deve ser um inteiro.` Correção: tire as aspas.

**2. Recuo errado ou colchete aberto** (`run: [`). O PyYAML não consegue interpretar e a mensagem começa com `YAML inválido em ...: while parsing a flow node`. Correção: confira recuos e fechamento de colchetes/aspas.

**3. Chave com erro de digitação** (`seeed`). A validação exige exatamente `name` e `seed`: `'run' deve conter exatamente 'name' e 'seed'.` O contrato rígido existe para esse caso.

**4. Esquecer que `bool` é `int`.** Se você escrever sua própria validação com só `isinstance(seed, int)`, `seed: true` passa. Foi esse equívoco que motivou o `isinstance(seed, bool)` no código.

## Código completo desta aula

??? example "Arquivo completo: src/mqtt_ids/config.py"

    ```python
    --8<-- "src/mqtt_ids/config.py"
    ```

??? example "Arquivo completo: tests/test_config.py"

    ```python
    --8<-- "tests/test_config.py"
    ```

??? example "Arquivo completo: configs/diagnostics.yaml"

    ```yaml
    --8<-- "configs/diagnostics.yaml"
    ```

## Exercícios

Os dois exercícios continuam no seu módulo de prática, `src/mqtt_ids/exercicios.py`. O segundo mistura a aula 01-1: ele só roda no ambiente do projeto.

1. Escreva `describe_scenario(path)`, que carrega um cenário e devolve um texto como `smoke (seed=7)`. E escreva `reject_unknown_keys(raw, allowed)`, que levanta `ScenarioError("Chaves desconhecidas: a, b")` (nomes em ordem alfabética) quando o mapa tem chaves fora do conjunto permitido. O exercício está pronto quando este teste passar:

    ```python title="tests/test_exercicio_01_2.py"
    from pathlib import Path

    import pytest

    from mqtt_ids.config import ScenarioError
    from mqtt_ids.exercicios import describe_scenario, reject_unknown_keys


    def test_describe_scenario_summarises_name_and_seed(tmp_path: Path) -> None:
        path = tmp_path / "scenario.yaml"
        path.write_text("run:\n  name: smoke\n  seed: 7\n", encoding="utf-8")

        assert describe_scenario(path) == "smoke (seed=7)"


    @pytest.mark.parametrize(
        ("raw", "message"),
        [
            ({"run": {}, "extra": 1}, "extra"),
            ({"run": {}, "b": 1, "a": 2}, "a, b"),
        ],
    )
    def test_reject_unknown_keys_lists_them_sorted(raw: dict, message: str) -> None:
        with pytest.raises(ScenarioError, match=message):
            reject_unknown_keys(raw, {"run", "dataset"})


    def test_reject_unknown_keys_accepts_known_keys() -> None:
        reject_unknown_keys({"run": {}}, {"run", "dataset"})
    ```

    ```bash title="$ Execução no terminal (na pasta do projeto)"
    uv run --locked pytest tests/test_exercicio_01_2.py
    ```

    Antes da solução, a coleta falha:

    ```text title="Saída esperada (antes da solução)"
    E   ImportError: cannot import name 'describe_scenario' from 'mqtt_ids.exercicios' (...)
    ERROR tests/test_exercicio_01_2.py
    ```

??? tip "Solução"

    ```python title="src/mqtt_ids/exercicios.py (acrescente ao arquivo)"
    from mqtt_ids.config import ScenarioError, load_scenario  # junto dos outros imports


    def describe_scenario(path: Path) -> str:
        scenario = load_scenario(path)
        return f"{scenario.name} (seed={scenario.seed})"


    def reject_unknown_keys(raw: dict, allowed: set[str]) -> None:
        unknown = sorted(set(raw) - allowed)
        if unknown:
            raise ScenarioError(f"Chaves desconhecidas: {', '.join(unknown)}")
    ```

    Depois da solução: `4 passed`. O `sorted` garante uma mensagem estável, e a diferença de conjuntos (`set(raw) - allowed`) é o mesmo raciocínio da validação de chaves do `load_scenario`.

## Quiz de fixação

??? question "1. Com suas palavras: por que `seed: true` precisa de um tratamento especial?"

    Porque o YAML lê `true` como booleano e, em Python, `bool` é subclasse de `int`: `isinstance(True, int)` é verdadeiro. Sem checar `bool` explicitamente, a seed `true` passaria como se fosse o inteiro 1.

??? question "2. O que `safe_load` impede que `load` permitiria?"

    Construir objetos Python arbitrários e executar funções descritas no arquivo (como `os.system`). `safe_load` só aceita tipos básicos do YAML.

**3. O que `@pytest.mark.parametrize` faz?**

- a) Roda a mesma função de teste uma vez para cada linha da tabela de casos
- b) Roda todos os testes do arquivo em paralelo em vários processos
- c) Repete cada teste até ele passar um número fixo de vezes

??? question "Resposta da 3"

    **a)**. Cada tupla vira um teste independente, com seu nome. O b) está errado porque paralelismo exige outro plugin; o c) porque não há repetição, e cada caso roda uma vez.

??? question "4. Revisão da aula 01-1: o que acontece se o `pyproject.toml` mudar e o `uv.lock` não, ao rodar `uv run --locked`?"

    Falha com "The lockfile needs to be updated, but --locked was provided": o `--locked` confere o lockfile contra o `pyproject.toml`.

## Commit

```bash title="$ Execução no terminal (na pasta do projeto)"
git add docs/01-2-cenario-yaml.md docs/glossario.md docs/referencia.md docs/recursos.md course/ mkdocs.yml
git commit -m "docs: aula 01-2 sobre cenário YAML seguro e validado"
```

## Resumo

- `safe_load` lê YAML sem executar código; a validação confere o contrato e falha cedo.
- `Scenario` é uma `dataclass(frozen=True)`: dados validados e imutáveis; `ScenarioError` nomeia o problema.
- Um teste parametrizado com `tmp_path` cobre muitos erros sem tocar o repositório.

## Fonte principal

[Documentação do PyYAML](https://pyyaml.org/wiki/PyYAMLDocumentation): leia a diferença entre `load` e `safe_load`.

## Para saber mais

- [Módulo dataclasses](https://docs.python.org/3/library/dataclasses.html)
- [pytest: tmp_path](https://docs.pytest.org/en/stable/how-to/tmp_path.html), [parametrize](https://docs.pytest.org/en/stable/how-to/parametrize.html) e [assert/raises](https://docs.pytest.org/en/stable/how-to/assert.html)

!!! question "Ficou com dúvida?"

    O agente é o seu professor: pergunte o que não ficou claro, colando a mensagem de erro exata e o que você tentou. Para conversar com pessoas, veja as comunidades em [Recursos](recursos.md#comunidades).

**Próxima aula:** [01-3. Runner e manifesto](01-3-runner-e-manifesto.md).
