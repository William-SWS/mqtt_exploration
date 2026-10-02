# 03-2. Carga segura e contrato de contagens

## Objetivos desta aula

Ao final desta aula você vai entender:

- por que o CSV só é lido **depois** de o SHA-256 conferir, e o que isso previne;
- como um **contrato de contagens** (linhas, colunas, classes, duplicatas) transforma "acho que os dados são esses" em fato verificável;
- por que uma duplicata exata aqui é um **frame repetido** e o que isso significa para o DoS;
- como provar que a exploração **não altera** o dado bruto.

E vai ter construído: `load_raw`, `contract_counts`, `paper_divergences`, `duplicates_by_class` e o primeiro arquivo de testes da issue 03.

**Ganho tangível:** os três ambientes confirmados em números (94.625, 110.668 e 80.893 linhas; 67 colunas), as divergências do artigo explicadas, e a descoberta de que **34% das linhas do DoS são cópias exatas** de outra.

## Onde estamos

Na [aula 03-1](03-1-mqtt-e-os-tres-ambientes.md) você aprendeu a ler um frame MQTT e viu os três ambientes pela tabela de tipos de pacote. Agora fixamos os fatos básicos que a [issue 03](issues/03-data-audit.md) pede: "a auditoria confirma ou explica divergências de linhas, colunas, classes e duplicatas" e "nenhuma execução altera conteúdo, hash ou mtime do raw".

### Relembrando

??? question "1. Com suas palavras: o que é uma ausência estrutural?"

    Um campo vazio porque ele não existe naquele frame (o frame nem tem camada MQTT, ou o tipo de pacote não tem esse campo), e não por falha de coleta.

??? question "2. Por que a aula 02-1 calcula o SHA-256 em blocos de 1 MiB?"

    Para usar memória constante: chamadas repetidas de `update()` equivalem a uma chamada com tudo concatenado, então o hash é o mesmo sem carregar o arquivo inteiro.

??? question "3. O que significa \"falhar cedo\" (aula 01-2)?"

    Conferir a entrada antes de executar qualquer estágio, para que o erro apareça na hora e não depois de uma execução longa.

## Antes de começar

A aula 03-1 concluída (você tem `src/mqtt_ids/audit.py` com `DATASETS`, `MSGTYPE_NAMES` e as duas funções) e os CSVs em `data/raw/`. Para o primeiro teste da issue 03:

--8<-- "course/includes/rodar-testes.md"

## Conceitos

### Leitura verificada

Na aula 02-2 a aquisição só promoveu dados cujo SHA-256 conferiu. Aqui o mesmo princípio vale **na hora de ler**: antes de abrir um CSV para análise, calculamos o hash dos bytes e o comparamos com `RAW_HASHES`. Se alguém trocou, truncou ou "arrumou" o arquivo, a análise não começa. O custo é ler o arquivo duas vezes (uma para o hash, em streaming; outra para o pandas), pequeno perto do risco de explorar a versão errada.

Duas decisões de leitura vêm junto: `low_memory=False` (a aula 03-1 mostrou o aviso de tipos mistos) e **não** renomear nem converter colunas na carga: o raw chega ao pandas como está.

### Contrato de contagens

Um **contrato de contagens** é a lista de fatos numéricos que dizem "estes são os dados": número de linhas, de colunas, de cada classe, se os rótulos são exatamente `normal` e o rótulo do ataque, e quantas linhas são duplicatas exatas. Ele serve a dois propósitos: (1) detectar mudança sem olhar linha a linha e (2) documentar diferenças com a fonte. O artigo descreve 45.513 frames `DoS` e 49.112 `normal`; o arquivo verificado tem 45.514 e 49.111. A soma (94.625) é igual, mas uma linha mudou de classe. O dicionário de dados já registrou isso ([ADR-023](DECISIONS.md#adr-023-fonte-semantica-e-contrato-observado-do-dicionario-mqtt_uad)); aqui o código passa a **mostrar** a diferença sempre que rodar. A regra: o contrato segue o arquivo verificado, e a divergência com o artigo é documentada, nunca "corrigida".

Fonte: [DataFrame.duplicated](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.duplicated.html) (por padrão considera todas as colunas e marca como duplicata tudo, exceto a primeira ocorrência).

### Duplicata exata é frame repetido

A [ADR-007](DECISIONS.md#adr-007-duplicatas-e-imutabilidade-do-raw) manda remover duplicatas exatas antes da divisão, preservando a primeira ocorrência. Ela foi escrita com base nas **30 duplicatas** do `Intrusion.csv`. Os outros dois arquivos contam outra história: 37 no MitM e **32.298 no DoS** (34% das linhas). Antes de decidir o que fazer, é preciso entender **o que** elas são.

Pista: `frame.number` deveria ser único (o número do frame na captura). Em cada arquivo, `linhas − frames distintos` é **exatamente** igual ao número de duplicatas. Ou seja, duplicata exata aqui significa "o mesmo frame aparece em mais de uma linha". Uma hipótese razoável: um frame TCP que carrega várias mensagens MQTT foi exportado em várias linhas idênticas. É uma hipótese (não temos o PCAP), mas os dados a sustentam e o impacto é grande: dedup mudaria o tamanho do ataque do DoS de 45.514 para 13.245.

### Raw imutável

Dado bruto não se edita: toda correção acontece em cópias derivadas. Para provar que a exploração respeita isso, comparamos o **conteúdo** (hash) e o **horário da última modificação** (`st_mtime_ns`, o instante da modificação mais recente do conteúdo, em nanossegundos inteiros) antes e depois de ler. Se os dois forem iguais, nada foi gravado no arquivo.

Fonte: [os.stat_result.st_mtime_ns](https://docs.python.org/3/library/os.html#os.stat_result.st_mtime_ns).

## Ponte teoria → projeto

As histórias 16 e 17 do [PRD](PRD.md) pedem confirmar linhas, colunas, classes e duplicatas; a 21, distinguir exploração descritiva de transformação persistida (EDA que não modifica a origem). A [ADR-007](DECISIONS.md#adr-007-duplicatas-e-imutabilidade-do-raw) define duplicatas e imutabilidade e a [ADR-023](DECISIONS.md#adr-023-fonte-semantica-e-contrato-observado-do-dicionario-mqtt_uad) as divergências do artigo. O achado do DoS não estava previsto: ele vira a ADR-025 (proposta) e será decidido na issue 04. Para a sua missão: números de portfólio precisam sair de uma versão verificada, e um rótulo "34% duplicado" muda como se lê qualquer métrica do DoS.

## Mão na massa

### Passo 1 — Preparar o módulo e ler só depois de conferir

No topo de `src/mqtt_ids/audit.py`, acrescente os imports e a pasta padrão dos dados. Linhas novas em destaque:

```python title="src/mqtt_ids/audit.py" linenums="3" hl_lines="3 7 9"
from __future__ import annotations

from pathlib import Path

import pandas as pd

from mqtt_ids.kaggle_assets import RAW_HASHES, sha256  # (1)!

RAW_DIR = Path("data/raw")  # (2)!

DATASETS = {
    "dos": ("DoS.csv", "DoS"),
    "mitm": ("MitM.csv", "mitm"),
    "intrusion": ("Intrusion.csv", "intrusion"),
}
```

1.  Reaproveita o hash esperado e o cálculo da aula 02-1. Nada de reescrever `sha256`.
2.  Valor padrão; o parâmetro `raw_dir` das funções permite apontar outra pasta (os testes usam isso).

Agora a exceção e a carga:

```python title="src/mqtt_ids/audit.py" linenums="60"
class AuditError(ValueError):
    """Indica uma entrada que não é a versão verificada dos dados."""


def load_raw(key: str, raw_dir: Path = RAW_DIR) -> pd.DataFrame:
    """Lê um CSV bruto somente depois de conferir o SHA-256."""
    filename, _ = DATASETS[key]  # (1)!
    path = raw_dir / filename
    if sha256(path) != RAW_HASHES[filename]:  # (2)!
        raise AuditError(f"SHA-256 divergente para {filename}.")
    return pd.read_csv(path, low_memory=False)  # (3)!
```

1.  `key` é `dos`, `mitm` ou `intrusion`; o dicionário `DATASETS` (aula 03-1) dá o nome do arquivo.
2.  Primeiro o hash, depois a leitura. Em Python, `AuditError` herda de `ValueError` como o `ScenarioError` e o `KaggleAssetError`: mesmo padrão, mesmo tratamento.
3.  A leitura sem renomeações nem conversões: o raw chega como está.

Teste o caso de falha com uma cópia adulterada (acrescentamos **uma quebra de linha** ao final):

```python title="/tmp/p0302c.py" linenums="1"
from pathlib import Path

from mqtt_ids.audit import AuditError, load_raw

try:
    load_raw("dos", Path("/tmp/raw_adulterado"))
except AuditError as error:
    print("AuditError:", error)
```

```bash title="$ Execução no terminal (na pasta do projeto)"
mkdir -p /tmp/raw_adulterado
cp data/raw/DoS.csv /tmp/raw_adulterado/DoS.csv
printf '\n' >> /tmp/raw_adulterado/DoS.csv
uv run --locked python /tmp/p0302c.py
rm -rf /tmp/raw_adulterado
```

```text title="Saída esperada"
AuditError: SHA-256 divergente para DoS.csv.
```

**O que aconteceu:** um único byte a mais (o `\n`) mudou o hash e a carga recusou o arquivo. Repare que o original em `data/raw` **não** foi tocado: trabalhamos numa cópia em `/tmp`.

### Passo 2 — O contrato de contagens

Primeiro, as contagens do artigo, para podermos comparar:

```python title="src/mqtt_ids/audit.py" linenums="36"
PAPER_COUNTS = {  # (1)!
    "dos": {"DoS": 45513, "normal": 49112},
    "mitm": {"mitm": 3855, "normal": 106813},
    "intrusion": {"intrusion": 1898, "normal": 78995},
}

NO_MQTT = "(sem MQTT)"
RESERVED = "(tipo fora da tabela)"
```

1.  Os números que o artigo publica. São uma **referência para comparar**, não o contrato: o contrato é o que o arquivo verificado contém.

As funções que reúnem as contagens:

```python title="src/mqtt_ids/audit.py" linenums="73"
def contract_counts(df: pd.DataFrame, positive: str) -> dict[str, object]:
    """Reúne as contagens que formam o contrato de um ambiente."""
    classes = df["type"].value_counts().to_dict()
    return {
        "rows": len(df),
        "columns": df.shape[1],  # (1)!
        "classes": classes,
        "labels_ok": set(classes) == {"normal", positive},  # (2)!
        "duplicates": int(df.duplicated().sum()),  # (3)!
        "repeated_frame_numbers": len(df) - df["frame.number"].nunique(),  # (4)!
    }
```

1.  `df.shape` é `(linhas, colunas)`; o índice 1 é o número de colunas (67 em todos os ambientes).
2.  Os rótulos precisam ser **exatamente** `normal` e o rótulo do ataque, com a capitalização observada (`mitm`, e não `MitM` como no artigo).
3.  `duplicated()` marca todas as repetições exceto a primeira; somar os `True` dá quantas linhas são cópias. O `int(...)` converte o inteiro do NumPy em `int` do Python.
4.  Quantas linhas "sobram" além dos frames distintos. Se for igual a `duplicates`, a duplicata exata **é** o frame repetido.

```python title="src/mqtt_ids/audit.py" linenums="86"
def paper_divergences(key: str, classes: dict[str, int]) -> dict[str, int]:
    """Diferença (observado - artigo) por classe, só onde houver."""
    return {
        label: classes[label] - expected
        for label, expected in PAPER_COUNTS[key].items()
        if classes[label] != expected  # (1)!
    }


def duplicates_by_class(df: pd.DataFrame) -> pd.Series:
    """Linhas duplicadas (a partir da segunda ocorrência) por classe."""
    return df[df.duplicated()]["type"].value_counts()  # (2)!
```

1.  Só aparecem as classes que **divergem**; um dicionário vazio quer dizer que o arquivo coincide com o artigo.
2.  Filtra as linhas duplicadas e conta por classe: quem repete mais, ataque ou normal?

Rode o contrato nos três ambientes:

```python title="/tmp/p0302.py" linenums="1"
from mqtt_ids.audit import (
    DATASETS,
    contract_counts,
    duplicates_by_class,
    load_raw,
    paper_divergences,
)

for key, (filename, positive) in DATASETS.items():
    df = load_raw(key)
    counts = contract_counts(df, positive)
    print("=====", key)
    for name, value in counts.items():
        print(f"  {name:24s} {value}")
    print("  divergência do artigo   ", paper_divergences(key, counts["classes"]))
    print("  duplicatas por classe   ", duplicates_by_class(df).to_dict())
```

```bash title="$ Execução no terminal (na pasta do projeto)"
uv run --locked python /tmp/p0302.py
```

```text title="Saída esperada"
===== dos
  rows                     94625
  columns                  67
  classes                  {'normal': 49111, 'DoS': 45514}
  labels_ok                True
  duplicates               32298
  repeated_frame_numbers   32298
  divergência do artigo    {'DoS': 1, 'normal': -1}
  duplicatas por classe    {'DoS': 32269, 'normal': 29}
===== mitm
  rows                     110668
  columns                  67
  classes                  {'normal': 106813, 'mitm': 3855}
  labels_ok                True
  duplicates               37
  repeated_frame_numbers   37
  divergência do artigo    {}
  duplicatas por classe    {'normal': 37}
===== intrusion
  rows                     80893
  columns                  67
  classes                  {'normal': 78995, 'intrusion': 1898}
  labels_ok                True
  duplicates               30
  repeated_frame_numbers   30
  divergência do artigo    {}
  duplicatas por classe    {'normal': 30}
```

**O que aconteceu e como ler:**

- Os três arquivos têm 67 colunas e rótulos corretos. **Só o DoS diverge do artigo**: um frame a mais de `DoS` e um a menos de `normal`.
- Em **todos** os arquivos `duplicates` é igual a `repeated_frame_numbers`: duplicata exata = frame repetido.
- No MitM e no Intrusion as duplicatas são poucas (37 e 30) e todas `normal`. No DoS são **32.298, e 32.269 delas são ataque**.

??? question "Pare e pense: se removêssemos as duplicatas do DoS, o que mudaria na proporção entre as classes?"

    O ataque cairia de 45.514 para 13.245 frames e o normal quase não mudaria (49.111 → 49.082): o DoS passaria de ~48% de ataque para ~21%. Qualquer métrica seria lida de outro jeito. Confira no próximo passo.

### Passo 3 — Olhar de perto as repetições do DoS

```python title="/tmp/p0302b.py" linenums="1"
from mqtt_ids.audit import load_raw

df = load_raw("dos")
sizes = df.groupby("frame.number").size()  # (1)!
print("frames distintos (frame.number):", sizes.shape[0])
print("linhas por frame:", sizes.value_counts().sort_index().to_dict())

unique_rows = df[~df.duplicated()]  # (2)!
print("classes depois de remover duplicatas:", unique_rows["type"].value_counts().to_dict())

crowded = sizes[sizes == sizes.max()].index[0]  # (3)!
columns = ["frame.number", "frame.len", "ip.src", "tcp.dstport", "mqtt.msgtype", "type"]
print(df.loc[df["frame.number"] == crowded, columns].head(3).to_string())
```

1.  Agrupa por `frame.number` e conta quantas linhas cada frame ocupa.
2.  `~` inverte o booleano: linhas que **não** são duplicata (mantém a primeira ocorrência, como a ADR-007).
3.  O frame que ocupa mais linhas, para olhar um exemplo.

```bash title="$ Execução no terminal (na pasta do projeto)"
uv run --locked python /tmp/p0302b.py
```

```text title="Saída esperada"
frames distintos (frame.number): 62327
linhas por frame: {1: 57593, 2: 203, 3: 167, 4: 165, 5: 162, 6: 173, 7: 191, 8: 1111, 9: 2522, 11: 1, 12: 3, 13: 2, 14: 2, 16: 4, 17: 2, 18: 9, 19: 11, 20: 3, 21: 2, 22: 1}
classes depois de remover duplicatas: {'normal': 49082, 'DoS': 13245}
       frame.number  frame.len         ip.src  tcp.dstport  mqtt.msgtype type
26946         17249       1514  192.168.1.196       1883.0           2.0  DoS
26947         17249       1514  192.168.1.196       1883.0           2.0  DoS
26948         17249       1514  192.168.1.196       1883.0           2.0  DoS
```

**O que aconteceu:** os 94.625 itens são, na verdade, **62.327 frames**, muitos repetidos até 22 vezes. O exemplo é um frame de 1.514 bytes (perto do tamanho máximo usual de um frame Ethernet) para a porta 1883 do broker, com `mqtt.msgtype` 2 (CONNACK), repetido em linhas idênticas. É coerente com um segmento TCP que carrega várias mensagens MQTT, exportado uma linha por mensagem com os campos do primeiro. Mas lembre: é uma **hipótese**. Se ela vale ou não muda o que significa "um frame de ataque" e é uma decisão para a issue 04 (veja a ADR-025, proposta).

!!! note "Duas leituras possíveis, duas consequências"

    **Se removermos as duplicatas:** uma unidade = um frame capturado, mas perdemos o volume de mensagens (uma inundação de 22 CONNACK vira uma linha). **Se mantivermos:** cada linha é uma mensagem MQTT, mas as métricas ficam dominadas por cópias e a validação cruzada pode ter a mesma linha em treino e validação. Sem decidir agora, o curso registra os dois lados.

### Passo 4 — Provar que o raw não foi tocado

```python title="/tmp/p0302d.py" linenums="1"
from pathlib import Path

from mqtt_ids.audit import DATASETS, load_raw

for key, (filename, _) in DATASETS.items():
    path = Path("data/raw") / filename
    before = path.stat().st_mtime_ns  # (1)!
    load_raw(key)
    print(filename, "mtime inalterado:", path.stat().st_mtime_ns == before)
```

1.  `Path.stat()` devolve metadados do arquivo; `st_mtime_ns` é o instante da última modificação, em nanossegundos inteiros.

```bash title="$ Execução no terminal (na pasta do projeto)"
uv run --locked python /tmp/p0302d.py
```

```text title="Saída esperada"
DoS.csv mtime inalterado: True
MitM.csv mtime inalterado: True
Intrusion.csv mtime inalterado: True
```

**O que aconteceu:** a carga leu três arquivos de dezenas de MB e nenhum foi modificado. (A ordem das linhas segue `DATASETS`.) O conteúdo também não mudou: o hash continuaria conferindo.

## Testando

O primeiro arquivo de testes da issue 03 usa um CSV de **três linhas** em `tmp_path`, nunca os dados reais (regra do projeto). Ele precisa de uma **fixture**: uma função de preparação que o pytest entrega ao teste pelo nome do parâmetro.

```python title="tests/test_audit_contract.py" linenums="1"
import hashlib
from pathlib import Path

import pandas as pd
import pytest

from mqtt_ids import audit
from mqtt_ids.audit import AuditError, contract_counts, load_raw

CSV = "frame.number,type\n1,normal\n2,DoS\n2,DoS\n"  # (1)!


@pytest.fixture  # (2)!
def raw_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:  # (3)!
    raw = tmp_path / "raw"
    raw.mkdir()
    (raw / "DoS.csv").write_text(CSV, encoding="utf-8")
    digest = hashlib.sha256(CSV.encode("utf-8")).hexdigest()
    monkeypatch.setattr(audit, "RAW_HASHES", {"DoS.csv": digest})  # (4)!
    return raw
```

1.  Um mini DoS: três frames com o número `2` repetido (uma duplicata).
2.  `@pytest.fixture` marca a função como preparação reutilizável.
3.  A fixture pede outras fixtures (`tmp_path`, `monkeypatch`) do mesmo jeito que um teste faz.
4.  Troca, só durante o teste, o hash esperado de `DoS.csv` pelo hash do mini arquivo. Sem isso, o `load_raw` recusaria o CSV de teste.

```python title="tests/test_audit_contract.py" linenums="23"
def test_load_raw_returns_the_verified_file(raw_dir: Path) -> None:
    assert load_raw("dos", raw_dir).shape == (3, 2)


def test_load_raw_rejects_a_changed_file(raw_dir: Path) -> None:
    (raw_dir / "DoS.csv").write_text(CSV + "3,normal\n", encoding="utf-8")  # (1)!

    with pytest.raises(AuditError, match="SHA-256 divergente"):
        load_raw("dos", raw_dir)


def test_loading_never_changes_the_raw_file(raw_dir: Path) -> None:
    path = raw_dir / "DoS.csv"
    before = (path.read_bytes(), path.stat().st_mtime_ns)  # (2)!

    load_raw("dos", raw_dir)

    assert (path.read_bytes(), path.stat().st_mtime_ns) == before


def test_duplicates_match_repeated_frame_numbers() -> None:
    df = pd.DataFrame({"frame.number": [1, 2, 2], "type": ["normal", "DoS", "DoS"]})

    counts = contract_counts(df, "DoS")

    assert counts["duplicates"] == counts["repeated_frame_numbers"] == 1  # (3)!
    assert counts["labels_ok"] is True
```

1.  Altera o arquivo **depois** de a fixture registrar o hash: o hash deixa de bater.
2.  Guarda o conteúdo e o horário de modificação antes e compara depois: é o critério "nenhuma execução altera conteúdo, hash ou mtime do raw".
3.  Em um DataFrame construído à mão, duplicata e número de frame repetido coincidem: o contrato que vimos nos dados reais.

```bash title="$ Execução no terminal (na pasta do projeto)"
uv run --locked pytest tests/test_audit_contract.py -v
```

```text title="Saída esperada"
tests/test_audit_contract.py::test_load_raw_returns_the_verified_file PASSED [ 25%]
tests/test_audit_contract.py::test_load_raw_rejects_a_changed_file PASSED [ 50%]
tests/test_audit_contract.py::test_loading_never_changes_the_raw_file PASSED [ 75%]
tests/test_audit_contract.py::test_duplicates_match_repeated_frame_numbers PASSED [100%]

============================== 4 passed in 0.19s ==============================
```

**O que aconteceu:** quatro comportamentos verificados sem tocar nos dados reais. Fixtures foram o único conceito novo de teste; as duas primeiras fixtures (`tmp_path`, `monkeypatch`) você já usa desde a aula 01-2. Depois de escrever os testes, rode o comando de agente `lint tests` (veja o `AGENTS.md`) para que o [Catálogo de testes](testing/scenarios.md) registre estes cenários.

## Erros comuns

**1. `AuditError: SHA-256 divergente para DoS.csv.`** O arquivo em `data/raw/` não é a versão fixada (alguém o editou, ou o download foi incompleto). Correção: refaça a aquisição da aula 02-2; nunca ajuste o hash esperado para "fazer passar".

**2. `FileNotFoundError` ao chamar `load_raw` no teste.** A fixture não criou o arquivo com o nome certo: `DoS.csv`, não `dos.csv`. O nome vem de `DATASETS`.

**3. O teste passa com `RAW_HASHES` real e falha com o fictício (ou o contrário).** O `monkeypatch.setattr(audit, "RAW_HASHES", ...)` precisa trocar o nome **no módulo onde ele é usado** (`audit`), não em `kaggle_assets`. Como o `audit.py` fez `from ... import RAW_HASHES`, ele tem a sua própria referência.

**4. Chamar a coluna pelo rótulo do artigo (`MitM`).** O arquivo usa `mitm`. O contrato usa a capitalização observada: `labels_ok` seria `False` com o rótulo errado.

## Código completo desta aula

??? example "Arquivo completo: src/mqtt_ids/audit.py"

    ```python
    """Auditoria exploratória dos três ambientes MQTT_UAD."""

    from __future__ import annotations

    from pathlib import Path

    import pandas as pd

    from mqtt_ids.kaggle_assets import RAW_HASHES, sha256

    RAW_DIR = Path("data/raw")

    DATASETS = {
        "dos": ("DoS.csv", "DoS"),
        "mitm": ("MitM.csv", "mitm"),
        "intrusion": ("Intrusion.csv", "intrusion"),
    }

    MSGTYPE_NAMES = {
        1: "CONNECT",
        2: "CONNACK",
        3: "PUBLISH",
        4: "PUBACK",
        5: "PUBREC",
        6: "PUBREL",
        7: "PUBCOMP",
        8: "SUBSCRIBE",
        9: "SUBACK",
        10: "UNSUBSCRIBE",
        11: "UNSUBACK",
        12: "PINGREQ",
        13: "PINGRESP",
        14: "DISCONNECT",
    }

    PAPER_COUNTS = {
        "dos": {"DoS": 45513, "normal": 49112},
        "mitm": {"mitm": 3855, "normal": 106813},
        "intrusion": {"intrusion": 1898, "normal": 78995},
    }

    NO_MQTT = "(sem MQTT)"
    RESERVED = "(tipo fora da tabela)"


    def msgtype_by_class(df: pd.DataFrame) -> pd.DataFrame:
        """Conta frames por tipo de pacote MQTT e por classe."""
        codes = df["mqtt.msgtype"]
        names = codes.map(MSGTYPE_NAMES)
        names = names.mask(codes.notna() & names.isna(), RESERVED).fillna(NO_MQTT)
        table = pd.crosstab(names, df["type"])
        return table.loc[table.sum(axis=1).sort_values(ascending=False).index]


    def mqtt_share_by_class(df: pd.DataFrame) -> pd.Series:
        """Fração de frames com camada MQTT em cada classe."""
        return df["mqtt.msgtype"].notna().groupby(df["type"]).mean()


    class AuditError(ValueError):
        """Indica uma entrada que não é a versão verificada dos dados."""


    def load_raw(key: str, raw_dir: Path = RAW_DIR) -> pd.DataFrame:
        """Lê um CSV bruto somente depois de conferir o SHA-256."""
        filename, _ = DATASETS[key]
        path = raw_dir / filename
        if sha256(path) != RAW_HASHES[filename]:
            raise AuditError(f"SHA-256 divergente para {filename}.")
        return pd.read_csv(path, low_memory=False)


    def contract_counts(df: pd.DataFrame, positive: str) -> dict[str, object]:
        """Reúne as contagens que formam o contrato de um ambiente."""
        classes = df["type"].value_counts().to_dict()
        return {
            "rows": len(df),
            "columns": df.shape[1],
            "classes": classes,
            "labels_ok": set(classes) == {"normal", positive},
            "duplicates": int(df.duplicated().sum()),
            "repeated_frame_numbers": len(df) - df["frame.number"].nunique(),
        }


    def paper_divergences(key: str, classes: dict[str, int]) -> dict[str, int]:
        """Diferença (observado - artigo) por classe, só onde houver."""
        return {
            label: classes[label] - expected
            for label, expected in PAPER_COUNTS[key].items()
            if classes[label] != expected
        }


    def duplicates_by_class(df: pd.DataFrame) -> pd.Series:
        """Linhas duplicadas (a partir da segunda ocorrência) por classe."""
        return df[df.duplicated()]["type"].value_counts()
    ```

## Exercícios

Os exercícios continuam em `src/mqtt_ids/exercicios.py`.

1. Escreva `positive_rate(df, positive)`, a fração de linhas da classe positiva, e `drop_exact_duplicates(df)`, que devolve o DataFrame **sem** as duplicatas exatas, mantendo a primeira ocorrência (como a ADR-007). O exercício está pronto quando este teste passar:

    ```python title="tests/test_exercicio_03_2.py"
    import pandas as pd

    from mqtt_ids.exercicios import drop_exact_duplicates, positive_rate


    def make_frames() -> pd.DataFrame:
        return pd.DataFrame(
            {
                "frame.number": [1, 2, 2, 3],
                "type": ["normal", "DoS", "DoS", "normal"],
            }
        )


    def test_positive_rate_is_the_share_of_the_positive_class() -> None:
        assert positive_rate(make_frames(), "DoS") == 0.5


    def test_drop_exact_duplicates_keeps_the_first_occurrence() -> None:
        result = drop_exact_duplicates(make_frames())

        assert result["frame.number"].tolist() == [1, 2, 3]
        assert positive_rate(result, "DoS") == 1 / 3
    ```

    ```bash title="$ Execução no terminal (na pasta do projeto)"
    uv run --locked pytest tests/test_exercicio_03_2.py
    ```

    Antes da solução:

    ```text title="Saída esperada (antes da solução)"
    E   ImportError: cannot import name 'drop_exact_duplicates' from 'mqtt_ids.exercicios' (...)
    ERROR tests/test_exercicio_03_2.py
    ```

??? tip "Solução"

    ```python title="src/mqtt_ids/exercicios.py (acrescente ao arquivo)"
    def positive_rate(df: pd.DataFrame, positive: str) -> float:
        return float((df["type"] == positive).mean())


    def drop_exact_duplicates(df: pd.DataFrame) -> pd.DataFrame:
        return df[~df.duplicated(keep="first")]
    ```

    Depois da solução: `2 passed`. A média de um booleano é a fração de `True`; `keep="first"` é o padrão do `duplicated`, escrito para deixar a regra da ADR-007 explícita. Aplique `positive_rate` ao DoS antes e depois da remoção: a fração de ataque cai de cerca de 48% para cerca de 21%.

## Quiz de fixação

??? question "1. Com suas palavras: por que `load_raw` calcula o hash antes de chamar `read_csv`?"

    Para não analisar bytes que não sejam a versão fixada: se o arquivo foi trocado, truncado ou editado, a análise nem começa e o erro aponta o arquivo. Explorar dados de versão desconhecida torna os números irreprodutíveis.

??? question "2. O que significa `duplicates == repeated_frame_numbers` nos três arquivos?"

    Que cada duplicata exata é o mesmo frame repetido em mais de uma linha (o número do frame deveria ser único). No DoS isso afeta 32.298 linhas, quase todas de ataque.

**3. O que o contrato faz com a diferença entre o artigo (45.513 `DoS`) e o arquivo (45.514)?**

- a) Documenta a divergência e segue o arquivo verificado
- b) Corrige o arquivo para que fique igual ao artigo
- c) Ignora o número do artigo e não registra a diferença

??? question "Resposta da 3"

    **a)**. O contrato segue os bytes verificados e a divergência com o artigo fica registrada (ADR-023 e `paper_divergences`). O b) alteraria o raw, que é imutável; o c) esconderia uma diferença que o leitor do portfólio deve conhecer.

??? question "4. Revisão da aula 03-1: por que um frame sem camada MQTT não é \"dado faltante\"?"

    Porque as colunas `mqtt.*` não existem naquele frame (ausência estrutural). Imputar valores destruiria a informação de que o frame nem é MQTT.

## Commit

```bash title="$ Execução no terminal (na pasta do projeto)"
git add src/mqtt_ids/audit.py tests/test_audit_contract.py
git commit -m "feat(audit): carga verificada e contrato de contagens dos três ambientes"
```

## Resumo

- `load_raw` confere o SHA-256 antes de ler; o raw nunca é alterado (conteúdo e mtime).
- O contrato fixa linhas, colunas, classes, rótulos e duplicatas; divergências do artigo ficam documentadas.
- Duplicata exata = frame repetido; no DoS são 32.298 linhas (34%), quase todas de ataque: decisão adiada para a issue 04 (ADR-025, proposta).

## Fonte principal

[DataFrame.duplicated (pandas)](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.duplicated.html): leia `subset` e `keep`, que definem o que é duplicata.

## Para saber mais

- [pytest: fixtures](https://docs.pytest.org/en/stable/how-to/fixtures.html)
- [os.stat_result.st_mtime_ns](https://docs.python.org/3/library/os.html#os.stat_result.st_mtime_ns)
- [pandas.read_csv](https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html)

!!! question "Ficou com dúvida?"

    O agente é o seu professor: pergunte o que não ficou claro, colando a mensagem de erro exata e o que você tentou. Para conversar com pessoas, veja as comunidades em [Recursos](recursos.md#comunidades).

**Próxima aula:** [03-3. Missingness estrutural e o dicionário de dados](03-3-missingness-e-dicionario.md).
