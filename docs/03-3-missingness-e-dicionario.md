# 03-3. Missingness estrutural e o dicionário de dados

## Objetivos desta aula

Ao final desta aula você vai entender:

- como **medir** a ausência dentro de cada tipo de pacote e provar que ela é estrutural;
- a diferença entre coluna **vazia**, **constante**, **quase constante** e **flag de presença**, e por que a contagem de valores distintos engana;
- como conferir o dicionário de dados contra os dados reais, coluna a coluna.

E vai ter construído: `column_profile`, `missing_by_msgtype` e `dictionary_mismatches`, com os testes que protegem o contrato do dicionário.

**Ganho tangível:** um perfil de colunas dos três ambientes que **concorda com o `docs/data_dictionary.md` sem nenhuma divergência**, e a descoberta de que quase todas as colunas "constantes" do MQTT são, na verdade, sinais de presença.

## Onde estamos

Na [aula 03-2](03-2-carga-segura-e-contrato.md) você fixou o contrato de contagens (linhas, classes, duplicatas) com `load_raw`. Agora você olha as **colunas**: a issue 03 pede que "toda coluna apareça exatamente uma vez no dicionário, com tipo, missingness, cardinalidade e política" e que colunas "totalmente vazias, constantes e identificadoras sejam explicitamente sinalizadas". O dicionário já foi escrito à mão ([Dicionário de dados](data_dictionary.md)); esta aula o **audita automaticamente**.

### Relembrando

??? question "1. O que significa `duplicates == repeated_frame_numbers` nos três arquivos?"

    Que toda duplicata exata é o mesmo frame repetido em mais de uma linha. No DoS são 32.298 linhas (34%), quase todas de ataque.

??? question "2. Por que `load_raw` calcula o hash antes de ler o CSV?"

    Para nunca analisar bytes que não sejam a versão fixada: se o arquivo mudou, a carga recusa com `AuditError`.

??? question "3. Por que um frame sem camada MQTT não é \"dado faltante\"?"

    Porque as colunas `mqtt.*` não existem naquele frame (ausência estrutural); imputar destruiria essa informação.

## Antes de começar

A aula 03-2 concluída e a suíte verde (`uv run --locked pytest`). Esta aula acrescenta **uma** configuração ao `pyproject.toml`, explicada no Passo 5. Os rascunhos desta aula importam o carregador do dicionário (`scripts/data_dictionary.py`), que não é um pacote instalado; por isso os comandos usam `env PYTHONPATH=.` (o ponto é a raiz do projeto).

## Conceitos

### Missingness estrutural, medida

A aula 03-1 afirmou que a ausência dos campos `mqtt.*` é estrutural. Agora vamos **provar**. O método é medir a ausência **dentro de cada tipo de pacote**, e não no arquivo inteiro. Se a ausência fosse aleatória (falha de coleta), ela seria parecida em todos os tipos de pacote. Se for estrutural, cada campo terá ausência de **0%** nos tipos que o definem e **100%** nos que não o têm.

Exemplo esperado: `mqtt.topic` deve estar sempre presente em PUBLISH e sempre ausente em PINGREQ; `mqtt.clientid` só em CONNECT. Medir assim transforma uma crença do dicionário ("a ausência geralmente significa não aplicável") em evidência numérica. Uma exceção também é informação: se um campo aparece num tipo onde não deveria, algo especial acontece naquele frame (veremos um caso no DoS).

Fonte: [guia de dados ausentes do pandas](https://pandas.pydata.org/docs/user_guide/missing_data.html) (`isna()`/`notna()` detectam `NaN`; reduções como a média pulam os ausentes).

### Vazia, constante, quase constante e flag de presença

Quatro situações parecem a mesma coisa (poucos valores distintos) e **não são**:

| Tipo | Definição | Exemplo | O que fazer |
|---|---|---|---|
| **Vazia** | 100% ausente | `frame.comment`, `mqtt.passwd` | Excluir; é só contrato |
| **Constante** | um único valor, sem ausência | `frame.encap_type` | Excluir; não separa nada |
| **Quase constante** | um valor domina (≥ 99% das linhas) | `mqtt.clientid` no DoS | Investigar; pode ser só raridade |
| **Flag de presença** | um único valor **quando presente** + ausência no resto | `mqtt.conflag.cleansess` | **Não excluir às cegas**: presente = "é um CONNECT" |

A armadilha: `df.nunique()` **ignora** os ausentes por padrão (`dropna=True`). Uma coluna com 99,66% de ausência e um único valor entre os restantes tem "cardinalidade 1", e parece constante. Mas ela tem **dois estados**: presente ou ausente, e esse estado é informação (o frame é um CONNECT?). Contando também a ausência (`dropna=False`) a diferença aparece: constante verdadeira tem **um** estado; flag de presença tem **dois**.

Fonte: [DataFrame.nunique](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.nunique.html) e [Series.value_counts](https://pandas.pydata.org/docs/reference/api/pandas.Series.value_counts.html) (`dropna`, `normalize`).

### O dicionário como contrato verificável

O dicionário tem, por coluna, o percentual de ausência e a cardinalidade **de cada ambiente**. Esses números foram medidos uma vez, à mão. Um **contrato** só vale se for conferido automaticamente: o perfil observado precisa concordar com o documento. Se um dia o arquivo mudar (outra versão do dataset), ou alguém editar o dicionário errado, o teste falha.

O ponto de ligação é o carregador `scripts/data_dictionary.py` que você já tem (`load_data_dictionary`, que lê o próprio `docs/data_dictionary.md`). Para não criar uma dependência da biblioteca (`src/`) para os scripts, a comparação é feita por uma função que **recebe** o dicionário como argumento.

## Ponte teoria → projeto

As histórias 17 e 18 do [PRD](PRD.md) pedem quantificar missingness, cardinalidade e colunas constantes ou vazias, e um dicionário cobrindo todas as colunas. A [ADR-023](DECISIONS.md#adr-023-fonte-semantica-e-contrato-observado-do-dicionario-mqtt_uad) estabelece que o missingness MQTT é tratado inicialmente como ausência estrutural e que a política de features só vira definitiva depois da análise. Esta aula entrega a evidência: números por tipo de pacote e a conferência automática do dicionário. Para a sua missão: no portfólio, a afirmação "não imputei porque a ausência é estrutural" passa a vir com a tabela que a sustenta.

## Mão na massa

### Passo 1 — O perfil de cada coluna

Acrescente ao fim de `src/mqtt_ids/audit.py`:

```python title="src/mqtt_ids/audit.py" linenums="100"
def column_profile(df: pd.DataFrame) -> pd.DataFrame:
    """Perfil estrutural de cada coluna: tipo, ausência, cardinalidade e alertas."""
    profile = pd.DataFrame(
        {
            "dtype": df.dtypes.astype(str),  # (1)!
            "missing_pct": df.isna().mean() * 100,  # (2)!
            "cardinality": df.nunique(dropna=True),  # (3)!
        }
    )
    states = df.nunique(dropna=False)  # (4)!
    profile["is_empty"] = profile["missing_pct"] == 100
    profile["is_constant"] = (states == 1) & ~profile["is_empty"]  # (5)!
    profile["is_presence_flag"] = (profile["cardinality"] == 1) & (states == 2)  # (6)!
    top_share = df.apply(
        lambda column: column.value_counts(normalize=True, dropna=False).max()  # (7)!
    )
    profile["top_value_share"] = top_share
    profile["is_near_constant"] = (
        (top_share >= 0.99) & (states > 1) & ~profile["is_presence_flag"]  # (8)!
    )
    return profile
```

1.  O tipo de cada coluna como texto. Os índices do perfil são os **nomes das colunas**.
2.  `isna()` marca os ausentes; a média de verdadeiros/falsos é a fração ausente; vezes 100, percentual.
3.  Valores distintos **sem contar** a ausência: é a mesma "cardinalidade" do dicionário.
4.  Estados distintos **contando** a ausência (`dropna=False`): é a chave para separar constante de flag.
5.  Constante verdadeira: um único estado e não vazia. Um coluna vazia também tem um estado (`NaN`), por isso `~is_empty`.
6.  Flag de presença: um único valor quando presente (`cardinality == 1`) **e** dois estados no total (presente/ausente).
7.  `value_counts(normalize=True, dropna=False)` dá a fração de cada estado; `.max()` é a do estado dominante. `df.apply` repete isso por coluna.
8.  Quase constante: o estado dominante cobre 99% ou mais, a coluna tem mais de um estado e não é uma flag de presença (essas ganham a sua própria etiqueta).

### Passo 2 — Ausência dentro de cada tipo de pacote

```python title="src/mqtt_ids/audit.py" linenums="123"
def missing_by_msgtype(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """Percentual de ausência de cada coluna dentro de cada tipo de pacote."""
    codes = df["mqtt.msgtype"]
    names = codes.map(MSGTYPE_NAMES)
    names = names.mask(codes.notna() & names.isna(), RESERVED).fillna(NO_MQTT)  # (1)!
    return df[columns].isna().groupby(names).mean().mul(100).round(1)  # (2)!
```

1.  Os mesmos nomes da aula 03-1. (Se você quiser evitar a repetição, extraia estas três linhas para uma função `packet_names(df)` e use-a nas duas funções; o curso mantém a repetição para cada passo ficar completo.)
2.  `isna()` vira verdadeiro/falso, `groupby(names)` agrupa por tipo de pacote, `mean()` dá a fração ausente em cada grupo; `.mul(100).round(1)` põe em percentual com uma casa.

Rascunho `/tmp/p0303b.py`:

```python title="/tmp/p0303b.py" linenums="1"
import pandas as pd

from mqtt_ids.audit import load_raw, missing_by_msgtype

pd.set_option("display.width", 200)
pd.set_option("display.max_columns", None)
columns = ["mqtt.topic", "mqtt.msg", "mqtt.qos", "mqtt.msgid", "mqtt.clientid", "mqtt.kalive"]
for key in ("dos", "intrusion"):
    print("=====", key)
    print(missing_by_msgtype(load_raw(key), columns))
```

```bash title="$ Execução no terminal (na pasta do projeto)"
uv run --locked python /tmp/p0303b.py
```

```text title="Saída esperada"
===== dos
                       mqtt.topic  mqtt.msg  mqtt.qos  mqtt.msgid  mqtt.clientid  mqtt.kalive
mqtt.msgtype
(sem MQTT)                  100.0     100.0     100.0       100.0          100.0        100.0
(tipo fora da tabela)        36.4      36.4       9.1        36.4          100.0        100.0
CONNACK                      96.8      96.8      85.7        85.7          100.0        100.0
CONNECT                     100.0     100.0     100.0       100.0            0.0          0.0
DISCONNECT                  100.0     100.0     100.0       100.0          100.0        100.0
PINGREQ                     100.0     100.0     100.0       100.0          100.0        100.0
PINGRESP                    100.0     100.0     100.0       100.0          100.0        100.0
PUBACK                       92.0      92.0       0.0         0.0          100.0        100.0
PUBCOMP                     100.0     100.0       0.0         0.0          100.0        100.0
PUBLISH                       0.5       0.5       0.0        99.5          100.0        100.0
PUBREL                       95.3      95.3       2.7         0.0          100.0        100.0
SUBACK                      100.0     100.0     100.0         0.0          100.0        100.0
SUBSCRIBE                     0.0     100.0     100.0         0.0          100.0        100.0
===== intrusion
              mqtt.topic  mqtt.msg  mqtt.qos  mqtt.msgid  mqtt.clientid  mqtt.kalive
mqtt.msgtype
(sem MQTT)         100.0     100.0     100.0       100.0          100.0        100.0
CONNACK            100.0     100.0     100.0       100.0          100.0        100.0
CONNECT            100.0     100.0     100.0       100.0            0.0          0.0
DISCONNECT         100.0     100.0     100.0       100.0          100.0        100.0
PINGREQ            100.0     100.0     100.0       100.0          100.0        100.0
PINGRESP           100.0     100.0     100.0       100.0          100.0        100.0
PUBLISH              0.0       0.0       0.0       100.0          100.0        100.0
SUBACK             100.0     100.0     100.0         0.0          100.0        100.0
SUBSCRIBE            0.0     100.0      76.9         0.0          100.0        100.0
```

**O que aconteceu e como ler:**

- **A ausência é estrutural.** `mqtt.clientid` e `mqtt.kalive` (campos do CONNECT) têm 0% de ausência em CONNECT e 100% em **todos** os outros tipos. `mqtt.topic` tem 0% em PUBLISH e 0% em SUBSCRIBE (a assinatura nomeia o tópico), e 100% em PINGREQ, PINGRESP, DISCONNECT.
- **No Intrusion o quadro é limpo**: cada campo está presente exatamente onde o protocolo manda.
- **No DoS há exceções.** Em PUBACK, PUBREL e CONNACK o tópico é ausente em ~92–97% (não em 100%): ~8% dos PUBACK **têm** `mqtt.topic`. Um PUBACK não leva tópico. A leitura mais natural é um frame com **mais de uma mensagem MQTT** (um PUBLISH e um PUBACK no mesmo segmento TCP), com o tipo do pacote registrado de uma delas. É consistente com a hipótese de frame repetido da aula 03-2, mas continua sendo hipótese. Repare também que `mqtt.msgid` (identificador de pacote) é **ausente em 99,5% dos PUBLISH** do DoS: PUBLISH de QoS 0 não leva identificador. Isso encaixa com o QoS 0 que dominou o ataque.
- A linha `(tipo fora da tabela)` do DoS (frames com `msgtype` 0) tem ausências **parciais**: o frame é malformado e as colunas ficam preenchidas ao acaso.

??? question "Pare e pense: se você imputasse `mqtt.topic` com a moda (o tópico mais frequente), o que perderia?"

    A informação de que o frame **não tem** tópico (PINGREQ, DISCONNECT, frames sem MQTT) viraria "tem o tópico mais frequente", e o modelo passaria a ver tópicos onde não existem. É o que o dicionário chama de destruir informação protocolar.

### Passo 3 — Colunas vazias, constantes, quase constantes e flags

Rascunho `/tmp/p0303.py` (ele também usa a função do Passo 4, escrita a seguir; **escreva primeiro o Passo 4**):

```python title="/tmp/p0303.py" linenums="1"
from mqtt_ids.audit import DATASETS, column_profile, dictionary_mismatches, load_raw
from scripts.data_dictionary import load_data_dictionary

dictionary = load_data_dictionary()
for key in DATASETS:
    profile = column_profile(load_raw(key))
    print("=====", key)
    print("  vazias:", int(profile["is_empty"].sum()))
    print("  constantes:", profile.index[profile["is_constant"]].tolist())
    print("  flags de presença:", int(profile["is_presence_flag"].sum()))
    print("  quase constantes:", profile.index[profile["is_near_constant"]].tolist())
    print("  divergências com o dicionário:", dictionary_mismatches(profile, dictionary, key))
```

### Passo 4 — Conferir o dicionário

```python title="src/mqtt_ids/audit.py" linenums="131"
def dictionary_mismatches(
    profile: pd.DataFrame, dictionary: object, key: str
) -> list[str]:
    """Colunas cuja ausência ou cardinalidade observada difere do dicionário."""
    problems = []
    if set(profile.index) != set(dictionary.to_dataframe()["name"]):  # (1)!
        problems.append("conjunto de colunas diferente do dicionário")
    for name, row in profile.iterrows():
        if name not in dictionary:
            continue
        stats = dictionary[name].stats_for(key)  # (2)!
        if round(row["missing_pct"], 2) != stats.missing_pct:  # (3)!
            problems.append(f"{name}: ausência {row['missing_pct']:.2f}")
        if row["cardinality"] != stats.cardinality:
            problems.append(f"{name}: cardinalidade {row['cardinality']}")
    return problems
```

1.  O dicionário deve ter **as mesmas colunas** dos dados, nem mais, nem menos. O parâmetro `dictionary` recebe o objeto de `load_data_dictionary()`; a função **não importa** o módulo de scripts (a biblioteca não depende dele).
2.  `stats_for("dos")` (e `mitm`, `intrusion`) devolve a ausência e a cardinalidade documentadas.
3.  O dicionário guarda o percentual com duas casas; compara-se com o valor observado arredondado igual.

```bash title="$ Execução no terminal (na pasta do projeto)"
env PYTHONPATH=. uv run --locked python /tmp/p0303.py
```

```text title="Saída esperada"
===== dos
  vazias: 19
  constantes: ['frame.encap_type', 'frame.ignored', 'frame.marked', 'frame.offset_shift']
  flags de presença: 13
  quase constantes: ['mqtt.clientid', 'mqtt.clientid_len', 'mqtt.conack.flags', 'mqtt.conack.flags.reserved', 'mqtt.conack.flags.sp', 'mqtt.conack.val', 'mqtt.kalive', 'mqtt.msgid']
  divergências com o dicionário: []
===== mitm
  vazias: 22
  constantes: ['frame.encap_type', 'frame.ignored', 'frame.marked', 'frame.offset_shift']
  flags de presença: 21
  quase constantes: []
  divergências com o dicionário: []
===== intrusion
  vazias: 19
  constantes: ['frame.encap_type', 'frame.ignored', 'frame.marked', 'frame.offset_shift']
  flags de presença: 16
  quase constantes: ['mqtt.clientid', 'mqtt.clientid_len', 'mqtt.kalive', 'mqtt.msgid', 'mqtt.proto_len', 'mqtt.protoname', 'mqtt.ver']
  divergências com o dicionário: []
```

**O que aconteceu e como ler:**

- **O dicionário concorda com os dados nos três ambientes**: nenhuma divergência de ausência ou cardinalidade, e as mesmas 67 colunas.
- **Vazias:** 19 no DoS e no Intrusion, 22 no MitM (três campos do MQTT que não aparecem nunca nesse ambiente: `mqtt.msgid`, `mqtt.sub.qos`, `mqtt.suback.qos`). Um campo vazio **num** ambiente não é, necessariamente, vazio em outro: a política deve ser decidida **por ambiente** ou pelo conjunto de campos sempre vazios.
- **Constantes:** as mesmas **quatro** nos três ambientes, todas metadados de captura (`frame.encap_type`, `frame.ignored`, `frame.marked`, `frame.offset_shift`).
- **Flags de presença:** são muito mais numerosas que as constantes (13, 21 e 16). Se alguém aplicasse o filtro "remover colunas com um valor só" usando `nunique()`, **jogaria fora campos que identificam o tipo de pacote**. O dicionário já aponta isso ao classificar vários como `portable`.
- **Quase constantes:** no DoS e no Intrusion, `mqtt.clientid` (≥99% ausente, mas com muitas identidades quando presente) é quase constante por raridade do CONNECT; no MitM nenhum campo passa de 99%.

Veja a aparência de colunas "de verdade" (rascunho `/tmp/p0303c.py`):

```python title="/tmp/p0303c.py" linenums="1"
from mqtt_ids.audit import column_profile, load_raw

profile = column_profile(load_raw("intrusion"))
columns = ["dtype", "missing_pct", "cardinality", "top_value_share"]
print(profile.loc[["frame.len", "ip.src", "tcp.dstport", "mqtt.msg", "mqtt.clientid"], columns].round(3))
print(profile["dtype"].value_counts().to_dict())
```

```bash title="$ Execução no terminal (na pasta do projeto)"
uv run --locked python /tmp/p0303c.py
```

```text title="Saída esperada"
                 dtype  missing_pct  cardinality  top_value_share
frame.len        int64        0.000         1356            0.190
ip.src             str        4.681          440            0.195
tcp.dstport    float64       11.294         1719            0.284
mqtt.msg       float64       97.502           77            0.975
mqtt.clientid      str       99.653           33            0.997
{'float64': 50, 'str': 11, 'int64': 6}
```

**O que aconteceu:** `tcp.dstport` é `float64` apesar de ser uma porta (inteiro): é a consequência de ter `NaN` (frames sem TCP), como o dicionário avisa. `mqtt.msg` também é `float64` no Intrusion: os valores publicados são numéricos (leituras de sensor). `ip.src` tem `str` (o pandas 3 usa o tipo `str`). **Tipo observado não é tipo semântico**: porta é inteiro sem sinal de 16 bits; o dicionário guarda os dois.

### Passo 5 — Fazer o pytest enxergar `scripts/`

O teste do dicionário importa `scripts.data_dictionary`, e o pytest não põe a raiz do projeto no caminho de importação por padrão. Acrescente **uma linha** à seção do pytest no `pyproject.toml`:

```toml title="pyproject.toml" linenums="36" hl_lines="3"
[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["."]  # (1)!
```

1.  `pythonpath` acrescenta pastas ao caminho de importação dos testes; o `.` é a raiz do projeto, onde mora `scripts/`. (O `uv.lock` não muda: não é dependência.)

??? question "Pare e pense: por que não bastava rodar `uv run python /tmp/p0303.py`, como nos rascunhos anteriores?"

    Quando o Python executa um arquivo, ele põe **a pasta desse arquivo** (`/tmp`) no começo do caminho de importação, e não a pasta atual. Como `scripts/` está na raiz do projeto, o `import` falha. O `env PYTHONPATH=.` acrescenta a raiz explicitamente.

## Testando

```python title="tests/test_audit_profile.py" linenums="1"
from pathlib import Path

import pandas as pd

from mqtt_ids.audit import column_profile, dictionary_mismatches, missing_by_msgtype


def make_frames() -> pd.DataFrame:  # (1)!
    return pd.DataFrame(
        {
            "mqtt.msgtype": [3.0, 3.0, 1.0, None],
            "mqtt.topic": ["a/b", "a/b", None, None],
            "mqtt.clientid": [None, None, "c1", None],
            "frame.encap_type": [1, 1, 1, 1],
            "frame.comment": [None, None, None, None],
            "frame.len": [60, 70, 80, 90],
        }
    )


def test_profile_flags_empty_constant_and_presence_columns() -> None:
    profile = column_profile(make_frames())

    assert profile.loc["frame.comment", "is_empty"]
    assert profile.loc["frame.encap_type", "is_constant"]
    assert profile.loc["mqtt.clientid", "is_presence_flag"]
    assert not profile.loc["frame.len", ["is_empty", "is_constant"]].any()  # (2)!


def test_missing_is_measured_inside_each_packet_type() -> None:
    table = missing_by_msgtype(make_frames(), ["mqtt.topic", "mqtt.clientid"])

    assert table.loc["PUBLISH", "mqtt.topic"] == 0.0  # (3)!
    assert table.loc["CONNECT", "mqtt.topic"] == 100.0
    assert table.loc["CONNECT", "mqtt.clientid"] == 0.0
```

1.  Quatro frames à mão: dois PUBLISH com tópico, um CONNECT com `clientid` e um frame sem MQTT. Cada tipo de coluna do perfil está representado: vazia, constante, presença, comum.
2.  `.loc[linha, [coluna1, coluna2]]` devolve os dois alertas; `.any()` é verdadeiro se algum for verdadeiro; o `not` afirma que **nenhum** é.
3.  Dentro de PUBLISH o tópico nunca falta; dentro de CONNECT, sempre falta: a assinatura de uma ausência estrutural.

```python title="tests/test_audit_profile.py" linenums="38"
def test_dictionary_documents_all_67_columns_once() -> None:
    text = Path("docs/data_dictionary.md").read_text(encoding="utf-8")
    rows = [
        line.split("|")[1].strip(" `")  # (1)!
        for line in text.splitlines()
        if line.startswith("| `") and line.count("|") > 8  # (2)!
    ]

    assert len(rows) == len(set(rows)) == 67  # (3)!


def test_mismatch_is_reported_when_the_data_disagree() -> None:
    from scripts.data_dictionary import load_data_dictionary

    profile = column_profile(make_frames())

    assert "conjunto de colunas diferente do dicionário" in dictionary_mismatches(
        profile, load_data_dictionary(), "dos"
    )
```

1.  O nome da coluna é a primeira célula da linha da tabela, sem a crase de código.
2.  Só linhas de tabela de colunas: começam com `` | ` `` e têm 8 células (a tabela de classes, de 2 células, fica de fora).
3.  Conta as linhas e as linhas **únicas**: se uma coluna aparecer duas vezes, ou faltar uma, falha. É o critério "toda coluna aparece exatamente uma vez no dicionário". (Um `dict` do carregador esconderia a duplicata, por isso o teste lê o texto.)

```bash title="$ Execução no terminal (na pasta do projeto)"
uv run --locked pytest tests/test_audit_profile.py -v
```

```text title="Saída esperada"
tests/test_audit_profile.py::test_profile_flags_empty_constant_and_presence_columns PASSED [ 25%]
tests/test_audit_profile.py::test_missing_is_measured_inside_each_packet_type PASSED [ 50%]
tests/test_audit_profile.py::test_dictionary_documents_all_67_columns_once PASSED [ 75%]
tests/test_audit_profile.py::test_mismatch_is_reported_when_the_data_disagree PASSED [100%]
```

**O que aconteceu:** os quatro testes usam só dados mínimos e o próprio documento do dicionário; nenhum lê os CSVs reais. A conferência contra os dados reais (as divergências vazias que você viu no Passo 4) é uma **evidência da EDA**, e na aula 03-8 ela vira parte do estágio `audit`. Depois, rode `lint tests` para catalogar estes cenários.

## Erros comuns

**1. `ModuleNotFoundError: No module named 'scripts'`.** Nos rascunhos de `/tmp`: falta o `env PYTHONPATH=.`. No pytest: falta `pythonpath = ["."]` no `pyproject.toml`.

**2. Usar `df.nunique() == 1` para achar colunas constantes.** Pega as flags de presença junto (cardinalidade 1 com ausência). Use `dropna=False` para contar a ausência como estado.

**3. `KeyError` em `dictionary[name].stats_for(key)`.** `key` precisa ser `dos`, `mitm` ou `intrusion` (minúsculas, como nas chaves de `DATASETS`).

**4. O dicionário e os dados "não batem" por arredondamento.** O dicionário usa duas casas decimais; compare o valor observado arredondado igual (`round(valor, 2)`). Comparar o valor bruto com o arredondado falha por centésimos.

## Código completo desta aula

??? example "Trecho acrescentado a src/mqtt_ids/audit.py (a partir da linha 100)"

    ```python
    def column_profile(df: pd.DataFrame) -> pd.DataFrame:
        """Perfil estrutural de cada coluna: tipo, ausência, cardinalidade e alertas."""
        profile = pd.DataFrame(
            {
                "dtype": df.dtypes.astype(str),
                "missing_pct": df.isna().mean() * 100,
                "cardinality": df.nunique(dropna=True),
            }
        )
        states = df.nunique(dropna=False)
        profile["is_empty"] = profile["missing_pct"] == 100
        profile["is_constant"] = (states == 1) & ~profile["is_empty"]
        profile["is_presence_flag"] = (profile["cardinality"] == 1) & (states == 2)
        top_share = df.apply(
            lambda column: column.value_counts(normalize=True, dropna=False).max()
        )
        profile["top_value_share"] = top_share
        profile["is_near_constant"] = (
            (top_share >= 0.99) & (states > 1) & ~profile["is_presence_flag"]
        )
        return profile


    def missing_by_msgtype(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
        """Percentual de ausência de cada coluna dentro de cada tipo de pacote."""
        codes = df["mqtt.msgtype"]
        names = codes.map(MSGTYPE_NAMES)
        names = names.mask(codes.notna() & names.isna(), RESERVED).fillna(NO_MQTT)
        return df[columns].isna().groupby(names).mean().mul(100).round(1)


    def dictionary_mismatches(
        profile: pd.DataFrame, dictionary: object, key: str
    ) -> list[str]:
        """Colunas cuja ausência ou cardinalidade observada difere do dicionário."""
        problems = []
        if set(profile.index) != set(dictionary.to_dataframe()["name"]):
            problems.append("conjunto de colunas diferente do dicionário")
        for name, row in profile.iterrows():
            if name not in dictionary:
                continue
            stats = dictionary[name].stats_for(key)
            if round(row["missing_pct"], 2) != stats.missing_pct:
                problems.append(f"{name}: ausência {row['missing_pct']:.2f}")
            if row["cardinality"] != stats.cardinality:
                problems.append(f"{name}: cardinalidade {row['cardinality']}")
        return problems
    ```

??? example "Arquivo completo: tests/test_audit_profile.py"

    ```python
    from pathlib import Path

    import pandas as pd

    from mqtt_ids.audit import column_profile, dictionary_mismatches, missing_by_msgtype


    def make_frames() -> pd.DataFrame:
        return pd.DataFrame(
            {
                "mqtt.msgtype": [3.0, 3.0, 1.0, None],
                "mqtt.topic": ["a/b", "a/b", None, None],
                "mqtt.clientid": [None, None, "c1", None],
                "frame.encap_type": [1, 1, 1, 1],
                "frame.comment": [None, None, None, None],
                "frame.len": [60, 70, 80, 90],
            }
        )


    def test_profile_flags_empty_constant_and_presence_columns() -> None:
        profile = column_profile(make_frames())

        assert profile.loc["frame.comment", "is_empty"]
        assert profile.loc["frame.encap_type", "is_constant"]
        assert profile.loc["mqtt.clientid", "is_presence_flag"]
        assert not profile.loc["frame.len", ["is_empty", "is_constant"]].any()


    def test_missing_is_measured_inside_each_packet_type() -> None:
        table = missing_by_msgtype(make_frames(), ["mqtt.topic", "mqtt.clientid"])

        assert table.loc["PUBLISH", "mqtt.topic"] == 0.0
        assert table.loc["CONNECT", "mqtt.topic"] == 100.0
        assert table.loc["CONNECT", "mqtt.clientid"] == 0.0


    def test_dictionary_documents_all_67_columns_once() -> None:
        text = Path("docs/data_dictionary.md").read_text(encoding="utf-8")
        rows = [
            line.split("|")[1].strip(" `")
            for line in text.splitlines()
            if line.startswith("| `") and line.count("|") > 8
        ]

        assert len(rows) == len(set(rows)) == 67


    def test_mismatch_is_reported_when_the_data_disagree() -> None:
        from scripts.data_dictionary import load_data_dictionary

        profile = column_profile(make_frames())

        assert "conjunto de colunas diferente do dicionário" in dictionary_mismatches(
            profile, load_data_dictionary(), "dos"
        )
    ```

## Exercícios

Os exercícios continuam em `src/mqtt_ids/exercicios.py`.

1. Escreva `columns_with_flag(profile, flag)`, que devolve, em ordem alfabética, os nomes das colunas do perfil em que a etiqueta (`is_empty`, `is_constant`, `is_presence_flag`...) é verdadeira, e `present_only_in(df, column)`, que devolve os tipos de pacote em que a coluna **nunca** falta (ausência 0%). O exercício está pronto quando este teste passar. Atenção ao que o teste espera de `mqtt.topic`:

    ```python title="tests/test_exercicio_03_3.py"
    import pandas as pd

    from mqtt_ids.audit import column_profile
    from mqtt_ids.exercicios import columns_with_flag, present_only_in


    def make_frames() -> pd.DataFrame:
        return pd.DataFrame(
            {
                "mqtt.msgtype": [3.0, 3.0, 1.0, None],
                "mqtt.topic": ["a/b", "a/b", None, None],
                "mqtt.clientid": [None, None, "c1", None],
                "frame.comment": [None, None, None, None],
            }
        )


    def test_columns_with_flag_lists_names_in_alphabetical_order() -> None:
        profile = column_profile(make_frames())

        assert columns_with_flag(profile, "is_empty") == ["frame.comment"]
        assert columns_with_flag(profile, "is_presence_flag") == [
            "mqtt.clientid",
            "mqtt.topic",
        ]


    def test_present_only_in_names_the_packet_types_that_carry_the_field() -> None:
        frames = make_frames()

        assert present_only_in(frames, "mqtt.topic") == ["PUBLISH"]
        assert present_only_in(frames, "mqtt.clientid") == ["CONNECT"]
    ```

    ```bash title="$ Execução no terminal (na pasta do projeto)"
    uv run --locked pytest tests/test_exercicio_03_3.py
    ```

    Antes da solução:

    ```text title="Saída esperada (antes da solução)"
    E   ImportError: cannot import name 'columns_with_flag' from 'mqtt_ids.exercicios' (...)
    ERROR tests/test_exercicio_03_3.py
    ```

??? tip "Solução"

    ```python title="src/mqtt_ids/exercicios.py (acrescente ao arquivo)"
    from mqtt_ids.audit import missing_by_msgtype  # junto dos imports de audit


    def columns_with_flag(profile: pd.DataFrame, flag: str) -> list[str]:
        return sorted(profile.index[profile[flag]])


    def present_only_in(df: pd.DataFrame, column: str) -> list[str]:
        missing = missing_by_msgtype(df, [column])[column]
        return sorted(missing.index[missing == 0.0])
    ```

    Depois da solução: `2 passed`. `profile[flag]` é um filtro booleano sobre o índice (os nomes das colunas). O `mqtt.topic` **também é** flag de presença aqui: os dois valores presentes são o mesmo (`a/b`) e há ausência, exatamente o caso de "um único valor quando presente". A segunda função **reaproveita** `missing_by_msgtype`.

## Quiz de fixação

??? question "1. Com suas palavras: como você prova que a ausência de `mqtt.topic` é estrutural e não aleatória?"

    Medindo a ausência **dentro de cada tipo de pacote**: 0% em PUBLISH e SUBSCRIBE (os pacotes que têm tópico) e 100% nos demais (PINGREQ, DISCONNECT, frames sem MQTT). Se fosse falha de coleta, a ausência seria parecida entre os tipos.

??? question "2. Por que remover \"colunas com um valor só\" usando `df.nunique() == 1` pode ser um erro aqui?"

    Porque `nunique()` ignora os ausentes por padrão: um campo do CONNECT com um único valor possível (e ausente em todos os outros pacotes) parece constante, mas a **presença** dele identifica o tipo de pacote. Com `dropna=False` ele tem dois estados e é uma flag de presença.

**3. O que `dictionary_mismatches` devolve quando os dados e o dicionário concordam?**

- a) Uma lista vazia
- b) Uma lista com uma entrada por coluna conferida
- c) `None`, sinalizando que não há o que comparar

??? question "Resposta da 3"

    **a)**. Só acrescenta ao resultado as colunas que divergem; lista vazia = nenhuma divergência (foi o que você viu nos três ambientes). O b) listaria tudo, e o c) não é um retorno da função.

??? question "4. Revisão da aula 03-2: o que a leitura verificada (`load_raw`) garante antes de qualquer perfil de colunas?"

    Que os bytes são os da versão fixada: o perfil descreve exatamente os dados citados no contrato, e uma troca do arquivo falharia antes de qualquer análise.

## Commit

```bash title="$ Execução no terminal (na pasta do projeto)"
git add src/mqtt_ids/audit.py tests/test_audit_profile.py pyproject.toml
git commit -m "feat(audit): perfil de colunas e conferência do dicionário de dados"
```

## Resumo

- Ausência estrutural prova-se medindo a ausência **por tipo de pacote** (0% onde o campo existe, 100% onde não existe).
- Vazia, constante, quase constante e **flag de presença** são coisas diferentes; `nunique(dropna=False)` as separa.
- O dicionário é um contrato: o perfil observado concorda com ele nos três ambientes, e um teste lê o próprio documento para garantir 67 colunas únicas.

## Fonte principal

[Guia de dados ausentes do pandas](https://pandas.pydata.org/docs/user_guide/missing_data.html): leia como `isna()`/`notna()` detectam ausentes e como as reduções os tratam.

## Para saber mais

- [DataFrame.nunique](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.nunique.html) e [Series.value_counts](https://pandas.pydata.org/docs/reference/api/pandas.Series.value_counts.html)
- [Dicionário de dados do projeto](data_dictionary.md), [Wireshark: campos MQTT](https://www.wireshark.org/docs/dfref/m/mqtt.html)

!!! question "Ficou com dúvida?"

    O agente é o seu professor: pergunte o que não ficou claro, colando a mensagem de erro exata e o que você tentou. Para conversar com pessoas, veja as comunidades em [Recursos](recursos.md#comunidades).

**Próxima aula:** [03-4. DoS: o ambiente da inundação](03-4-dos-inundacao.md).
