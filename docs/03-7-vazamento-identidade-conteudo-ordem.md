# 03-7. Vazamento por identidade, conteúdo e ordem

## Objetivos desta aula

Ao final desta aula você vai entender:

- o que é **vazamento** (*leakage*) e por que ele infla métricas sem que o modelo aprenda nada útil;
- como **medir** o risco de cada coluna com um **classificador de tabela**, um modelo trivial que só memoriza o que vê em cada valor;
- por que a **ordem** de captura e as **repetições** fazem uma divisão aleatória enganar, e o que muda com um holdout temporal.

E vai ter construído: `temporal_split`, `random_split`, `lookup_scores`, `identity_leak_table`, `neighbor_agreement`, `order_prevalence` e `identity_reappearance`.

**Ganho tangível:** uma tabela dos três ambientes mostrando, por coluna, o F1 de um classificador de uma coluna só com divisão temporal e com divisão aleatória, e a prova numérica de que a divisão aleatória é otimista.

## Onde estamos

As aulas 03-4 a 03-6 descreveram cada ambiente separadamente e deixaram várias pistas: tópicos aleatórios no DoS, MAC compartilhado no MitM, Client IDs copiados no Intrusion. Agora **medimos** o risco de forma comparável, atendendo ao critério da [issue 03](issues/03-data-audit.md): "evidência tabular ou visual do risco por IP, MAC, client ID, tópico, payload e ordem" (histórias 19 e 20 do [PRD](PRD.md)).

### Relembrando

??? question "1. Por que o Intrusion deve ser avaliado também por evento?"

    Porque cada ataque é uma sessão de cerca de 7 frames em menos de um segundo (`CONNECT > CONNACK > PUBLISH > DISCONNECT`): a sequência caracteriza a intrusão, e contar cada frame como independente superestima o ataque.

??? question "2. O que significa `shared_values(...)[\"only_attack\"] == []` para `ip.src` no Intrusion?"

    Que nenhum IP é exclusivo do ataque: os 10 IPs de origem que ele usa também aparecem no normal.

??? question "3. Qual a diferença entre uma assinatura de ataque que **generaliza** e uma que identifica o **laboratório**?"

    A que generaliza descreve comportamento de rede (PUBLISH QoS 0 contra a porta 1883, sessões curtas); a do laboratório descreve identidades do experimento (IP do atacante, tópicos `mqtt-malaria/...`).

## Antes de começar

As aulas 03-1 a 03-6 concluídas e a suíte verde:

--8<-- "course/includes/rodar-testes.md"

## Conceitos

### Vazamento: quando o teste deixa de ser teste

**Vazamento** (*data leakage*) é usar, ao construir ou avaliar um modelo, informação que **não estaria disponível** quando ele estivesse em produção. O resultado são estimativas de desempenho otimistas demais, e um modelo que decepciona no mundo real. A regra geral da documentação do scikit-learn é "nunca chamar `fit` nos dados de teste", e o vazamento de que tratamos aqui é a **versão do dado**: quando o conjunto de teste contém coisas que o de treino já viu.

Há três fontes de vazamento neste projeto:

| Fonte | Como acontece | Exemplo |
|---|---|---|
| **Identidade** | O modelo memoriza *quem* (IP, MAC, Client ID) em vez de *o quê* | A máquina do atacante |
| **Conteúdo** | O modelo memoriza *texto* (tópico, payload) que nomeia o ataque | `mqtt-malaria/...` |
| **Ordem/repetição** | Frames vizinhos ou repetidos caem dos dois lados da divisão | `frame.number`, rajadas |

Fonte: [armadilhas comuns do scikit-learn](https://scikit-learn.org/stable/common_pitfalls.html) (definição de vazamento e a regra de nunca ajustar com o teste).

### O classificador de tabela: um termômetro de vazamento

Como medir o quanto **uma coluna sozinha** permite acertar o ataque? Construímos o modelo mais simples possível, o **classificador de tabela** (*lookup*): para cada valor da coluna, ele guarda a fração de frames de ataque que viu no treino, e prevê "ataque" se essa fração for maior que 50%. Valores **nunca vistos** recebem a previsão da classe majoritária do treino. Não há aprendizado de padrões: é só memória.

Se esse modelo de memória, usando **uma coluna**, tem F1 alto no teste, a coluna carrega identidade ou conteúdo do cenário, e um modelo mais complexo faria o mesmo (e esconderia isso). Se o F1 é zero, a coluna, **sozinha**, não separa as classes.

### Divisão aleatória × divisão temporal

A **divisão aleatória** sorteia 70% dos frames para treino e deixa 30% para teste. Como frames vizinhos são quase cópias (nas rajadas) e há frames repetidos (as duplicatas da aula 03-2), os mesmos valores aparecem nos dois lados. A **divisão temporal** (holdout, ADR-008) usa os **primeiros 70%** da captura para treino e os **últimos 30%** para teste: o teste só contém o que veio **depois**. Se um valor só existia no começo, o modelo não o encontra no teste.

A diferença entre as duas notas é uma estimativa direta do quanto a divisão aleatória **mente**. O scikit-learn explica por quê: a hipótese de amostras independentes e identicamente distribuídas se quebra quando há grupos de amostras dependentes, e a autocorrelação entre observações próximas no tempo faz o `KFold` comum gerar "correlação irrazoável entre treino e teste".

Fonte: [validação cruzada (scikit-learn)](https://scikit-learn.org/stable/modules/cross_validation.html) (hipótese i.i.d., `GroupKFold`/`StratifiedGroupKFold`, `TimeSeriesSplit`).

## Ponte teoria → projeto

A [ADR-006](DECISIONS.md#adr-006-politica-principal-de-features) exclui identidade e ordem da política principal, e a [ADR-008](DECISIONS.md#adr-008-holdout-temporal-e-cv-agrupada) adota holdout temporal e CV agrupada porque "frames próximos são correlacionados; uma divisão aleatória superestima a generalização". Esta aula transforma as duas afirmações em **números**, para os três ambientes. Para a sua missão: no portfólio, a pergunta "como você sabe que não há vazamento?" passa a ter uma resposta experimental.

## Mão na massa

### Passo 1 — Divisões e o classificador de tabela

Acrescente ao fim de `src/mqtt_ids/audit.py` e, no topo, `import numpy as np` (junto de `import pandas as pd`):

```python title="src/mqtt_ids/audit.py" linenums="272"
def temporal_split(df: pd.DataFrame, fraction: float = 0.7) -> pd.Series:
    """Verdadeiro nos primeiros `fraction` frames da captura (desenvolvimento)."""
    return pd.Series(np.arange(len(df)) < int(len(df) * fraction), index=df.index)  # (1)!


def random_split(df: pd.DataFrame, fraction: float = 0.7, seed: int = 0) -> pd.Series:
    """Divisão aleatória, só para mostrar o que ela esconde."""
    rng = np.random.default_rng(seed)  # (2)!
    return pd.Series(rng.random(len(df)) < fraction, index=df.index)
```

1.  Uma série verdadeiro/falso, uma posição por frame: `True` nos primeiros 70% **em ordem de captura**. Como o CSV está em ordem, as posições já são o tempo.
2.  Gerador de números aleatórios com semente fixa (`seed=0`): o resultado é reproduzível (a mesma divisão sempre).

```python title="src/mqtt_ids/audit.py" linenums="283"
def lookup_scores(
    df: pd.DataFrame, column: str, positive: str, train: pd.Series
) -> dict[str, float]:
    """Classificador de tabela: aprende a taxa de ataque de cada valor da coluna."""
    is_attack = df["type"] == positive
    key = df[column].astype(str).where(df[column].notna(), "(ausente)")  # (1)!
    rate = is_attack[train].groupby(key[train]).mean()  # (2)!
    unseen = float(is_attack[train].mean() > 0.5)  # (3)!
    predicted = key[~train].map(rate).fillna(unseen) > 0.5  # (4)!
    actual = is_attack[~train]
    tp = int((predicted & actual).sum())
    precision = tp / max(int(predicted.sum()), 1)  # (5)!
    recall = tp / max(int(actual.sum()), 1)
    f1 = 2 * precision * recall / max(precision + recall, 1e-12)
    return {"precision": precision, "recall": recall, "f1": f1}
```

1.  O valor da coluna como texto, com a ausência virando o valor `(ausente)`: a ausência também é um estado que o modelo pode memorizar (lembre da flag de presença, aula 03-3).
2.  **Treino:** para cada valor, a fração de frames de ataque. `is_attack[train]` seleciona só o treino e agrupa pelo valor.
3.  O que prever para valores nunca vistos: a classe majoritária do treino (1 se a maioria for ataque, 0 caso contrário).
4.  **Teste:** troca cada valor pela taxa aprendida (`map`), usa o `unseen` onde não havia valor (`fillna`) e prevê ataque se a taxa for maior que 0,5.
5.  Precisão e recall com `max(..., 1)` no denominador para não dividir por zero; F1 é a média harmônica.

```python title="src/mqtt_ids/audit.py" linenums="300"
def identity_leak_table(
    df: pd.DataFrame, positive: str, columns: list[str]
) -> pd.DataFrame:
    """F1 do classificador de tabela com divisão temporal e com divisão aleatória."""
    splits = {"temporal": temporal_split(df), "random": random_split(df)}
    rows = {
        column: {
            name: round(lookup_scores(df, column, positive, train)["f1"], 3)  # (1)!
            for name, train in splits.items()
        }
        for column in columns
    }
    return pd.DataFrame(rows).T  # (2)!
```

1.  Para cada coluna e cada divisão, o F1 do ataque.
2.  `DataFrame(rows)` põe as colunas do CSV como colunas da tabela; `.T` as transpõe para que cada linha seja uma coluna do CSV.

### Passo 2 — A tabela de vazamento dos três ambientes

Rascunho `/tmp/p0307b.py`:

```python title="/tmp/p0307b.py" linenums="1"
import pandas as pd

from mqtt_ids.audit import DATASETS, identity_leak_table, load_raw

pd.set_option("display.width", 200)
columns = ["ip.src", "eth.src", "mqtt.clientid", "mqtt.topic", "tcp.dstport", "frame.len", "frame.number"]
for key, (filename, positive) in DATASETS.items():
    print("=====", key, "(F1 do ataque)")
    print(identity_leak_table(load_raw(key), positive, columns))
```

```bash title="$ Execução no terminal (na pasta do projeto)"
uv run --locked python /tmp/p0307b.py
```

```text title="Saída esperada"
===== dos (F1 do ataque)
               temporal  random
ip.src            0.855   0.890
eth.src           0.853   0.887
mqtt.clientid     0.000   0.000
mqtt.topic        0.000   0.886
tcp.dstport       0.945   0.990
frame.len         0.701   0.776
frame.number      0.000   0.897
===== mitm (F1 do ataque)
               temporal  random
ip.src            0.000   0.000
eth.src           0.740   0.834
mqtt.clientid     0.000   0.000
mqtt.topic        0.000   0.000
tcp.dstport       0.000   0.031
frame.len         0.776   0.799
frame.number      0.000   0.000
===== intrusion (F1 do ataque)
               temporal  random
ip.src            0.000   0.000
eth.src           0.000   0.000
mqtt.clientid     0.070   0.057
mqtt.topic        0.182   0.107
tcp.dstport       0.000   0.171
frame.len         0.074   0.115
frame.number      0.000   0.000
```

**O que aconteceu e como ler (um ambiente por vez):**

- **DoS:** uma coluna **só**, a porta de destino (`tcp.dstport`), dá F1 de **0,945** com divisão temporal: quase um detector pronto, porque o ataque vai todo para a porta 1883. O IP e o MAC dão ~0,85 (identidade da máquina atacante, que também gera tráfego normal, por isso não chega a 1). **O contraste mais revelador está em `mqtt.topic` e `frame.number`:** F1 **0,000** na divisão temporal e **0,886 / 0,897** na aleatória. Os tópicos do mqtt-malaria e os números de frame repetidos **nunca reaparecem** no futuro, mas aparecem nos dois lados de uma divisão aleatória (os mesmos frames repetidos, as mesmas rajadas). É vazamento puro: o modelo "decora" o teste.
- **MitM:** `eth.src` (0,740) e `frame.len` (0,776) são os únicos que funcionam, ambos de **camada 2**: o ataque vive abaixo do IP. IP, tópico e Client ID **não** separam nada (0,000).
- **Intrusion:** **nenhuma coluna isolada funciona** (o melhor, o tópico, tem F1 de 0,182). É o ambiente que realmente exige combinar atributos e olhar sequências.
- **A diferença aleatória − temporal** é pequena onde as colunas generalizam (ex.: `frame.len` no MitM: 0,776 contra 0,799) e **enorme** onde há vazamento (tópico e `frame.number` no DoS: +0,89).

??? question "Pare e pense: se um colega apresentasse F1 = 0,99 no DoS usando só `tcp.dstport` e divisão aleatória, você confiaria?"

    Não sem antes ver a divisão temporal (0,945) e entender **por quê**: o ataque usa a porta 1883, que também é a porta do tráfego MQTT normal do laboratório. O número alto é real neste ambiente, mas descreve *este* laboratório, e a divisão aleatória o superestima (0,990 contra 0,945).

### Passo 3 — A ordem importa

Escreva as funções de ordem:

```python title="src/mqtt_ids/audit.py" linenums="315"
def neighbor_agreement(df: pd.DataFrame, positive: str) -> float:
    """Fração dos frames cuja classe é igual à do frame anterior."""
    is_attack = df["type"] == positive
    return float((is_attack == is_attack.shift()).iloc[1:].mean())  # (1)!


def order_prevalence(df: pd.DataFrame, positive: str, bins: int = 10) -> list[float]:
    """Prevalência do ataque em cada décimo da captura, em ordem."""
    position = pd.qcut(np.arange(len(df)), bins, labels=False)  # (2)!
    return (df["type"] == positive).groupby(position).mean().round(3).tolist()
```

1.  Compara cada frame com o anterior (`shift`); `iloc[1:]` descarta o primeiro, que não tem anterior. A média é a fração de frames com a mesma classe do vizinho.
2.  `qcut` divide as posições em 10 faixas de **mesmo tamanho**; agrupar por faixa e tirar a média do ataque dá a prevalência em cada décimo da captura.

```python title="src/mqtt_ids/audit.py" linenums="327"
def identity_reappearance(
    df: pd.DataFrame, column: str, fraction: float = 0.7
) -> float:
    """Fração dos valores do holdout que já tinham aparecido no desenvolvimento."""
    train = temporal_split(df, fraction)
    seen = set(df.loc[train, column].dropna())  # (1)!
    holdout = df.loc[~train, column].dropna()
    return float(holdout.isin(seen).mean())  # (2)!
```

1.  Os valores presentes no desenvolvimento (os primeiros 70%).
2.  A fração dos valores do holdout (os últimos 30%) que já estavam nesse conjunto: quanto do "futuro" já é conhecido.

Rascunhos `/tmp/p0307.py` e `/tmp/p0307c.py`:

```python title="/tmp/p0307.py" linenums="1"
from mqtt_ids.audit import (
    DATASETS,
    load_raw,
    neighbor_agreement,
    order_prevalence,
    temporal_split,
)

for key, (filename, positive) in DATASETS.items():
    df = load_raw(key)
    train = temporal_split(df)
    holdout_positives = int((df.loc[~train, "type"] == positive).sum())
    print("=====", key)
    print("  classe igual à do frame anterior:", round(neighbor_agreement(df, positive), 4))
    print("  prevalência por décimo:", order_prevalence(df, positive))
    print("  ataques nos últimos 30%:", holdout_positives, "de", int((~train).sum()), "frames")
```

```bash title="$ Execução no terminal (na pasta do projeto)"
uv run --locked python /tmp/p0307.py
```

```text title="Saída esperada"
===== dos
  classe igual à do frame anterior: 0.9999
  prevalência por décimo: [0.0, 0.628, 1.0, 0.183, 0.0, 0.889, 0.715, 0.209, 1.0, 0.185]
  ataques nos últimos 30%: 13191 de 28388 frames
===== mitm
  classe igual à do frame anterior: 0.9971
  prevalência por décimo: [0.049, 0.002, 0.0, 0.05, 0.018, 0.007, 0.104, 0.05, 0.055, 0.015]
  ataques nos últimos 30%: 1325 de 33201 frames
===== intrusion
  classe igual à do frame anterior: 0.9939
  prevalência por décimo: [0.075, 0.047, 0.03, 0.017, 0.004, 0.012, 0.018, 0.018, 0.0, 0.014]
  ataques nos últimos 30%: 254 de 24268 frames
```

**O que aconteceu e como ler:**

- **Frames vizinhos têm a mesma classe em 99,4% a 99,99% das vezes.** Um "classificador" que prevê, para cada frame, a classe do anterior, acerta quase tudo nos três ambientes: o rótulo é fortemente **autocorrelacionado**. Numa divisão aleatória, o vizinho de cada frame de teste está no treino com a classe correta.
- **Prevalência por décimo:** no DoS a prevalência vai de 0 a 1 de um décimo para o outro (blocos de ataque, depois blocos normais). No Intrusion ela **cai ao longo da captura** (de 7,5% no primeiro décimo para 1,4% no último): o começo tem mais intrusões que o fim.
- **O holdout temporal tem ataques** nos três ambientes, mas **muito poucos no Intrusion**: 254 frames em 24.268 (1%), distribuídos em **33 rajadas** curtas; é o resultado que a avaliação por evento vai precisar tratar com intervalos de confiança (ADR-017).

```python title="/tmp/p0307c.py" linenums="1"
from mqtt_ids.audit import DATASETS, identity_reappearance, load_raw

columns = ["ip.src", "eth.src", "mqtt.clientid", "mqtt.topic", "tcp.dstport"]
for key in DATASETS:
    df = load_raw(key)
    shares = {column: round(identity_reappearance(df, column), 3) for column in columns}
    print(key, shares)
```

```bash title="$ Execução no terminal (na pasta do projeto)"
uv run --locked python /tmp/p0307c.py
```

```text title="Saída esperada"
dos {'ip.src': 0.991, 'eth.src': 1.0, 'mqtt.clientid': 0.25, 'mqtt.topic': 0.006, 'tcp.dstport': 0.593}
mitm {'ip.src': 0.66, 'eth.src': 1.0, 'mqtt.clientid': 1.0, 'mqtt.topic': 1.0, 'tcp.dstport': 0.518}
intrusion {'ip.src': 0.719, 'eth.src': 1.0, 'mqtt.clientid': 0.875, 'mqtt.topic': 1.0, 'tcp.dstport': 0.57}
```

**O que aconteceu e como ler:** a fração do holdout cujos valores já apareceram. **MAC (`eth.src`)** reaparece em 100% nos três ambientes: o laboratório tem poucos aparelhos, todos presentes desde o começo, então um modelo que memoriza MAC "funciona" no holdout, mas apenas porque os mesmos aparelhos continuam lá. **Tópico no DoS** reaparece em **0,6%**: os tópicos aleatórios do ataque nunca voltam (a razão de o F1 temporal ser zero). **IP** reaparece em 66% a 99%: há IPs novos (servidores da internet) no futuro, o que é saudável.

!!! note "O que a divisão temporal **não** resolve"

    O holdout temporal elimina o vazamento por vizinhança e por repetição, mas **não** o por identidade: o MAC reaparece em 100% do holdout. Por isso a ADR-006 exclui MAC e IP crus da **política principal**, e não só da validação. A ablação (aula 03-9) mede o efeito de reincluí-los.

## Testando

```python title="tests/test_audit_leakage.py" linenums="1"
import pandas as pd

from mqtt_ids.audit import (
    identity_reappearance,
    lookup_scores,
    neighbor_agreement,
    order_prevalence,
    random_split,
    temporal_split,
)


def make_frames() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "type": ["normal"] * 4 + ["atk"] * 2 + ["normal"] * 2 + ["atk"] * 2,
            "ip.src": ["a", "a", "b", "b", "x", "x", "a", "c", "x", "d"],  # (1)!
        }
    )


def test_temporal_split_takes_the_first_frames_in_order() -> None:
    train = temporal_split(make_frames(), 0.7)

    assert train.tolist() == [True] * 7 + [False] * 3


def test_random_split_is_reproducible_with_the_same_seed() -> None:
    frames = make_frames()

    assert random_split(frames, seed=1).equals(random_split(frames, seed=1))


def test_lookup_learns_known_identities_and_misses_new_ones() -> None:
    frames = make_frames()
    scores = lookup_scores(frames, "ip.src", "atk", temporal_split(frames, 0.7))

    assert scores == {"precision": 1.0, "recall": 0.5, "f1": 2 / 3}  # (2)!


def test_neighbor_agreement_and_order_prevalence_show_the_bursts() -> None:
    frames = make_frames()

    assert neighbor_agreement(frames, "atk") == 6 / 9  # (3)!
    assert order_prevalence(frames, "atk", bins=2) == [0.2, 0.6]


def test_reappearance_counts_holdout_values_already_seen() -> None:
    assert identity_reappearance(make_frames(), "ip.src", 0.7) == 1 / 3  # (4)!
```

1.  Dez frames: no treino (7 primeiros) `x` é sempre ataque e `a`/`b` sempre normal; no holdout (3 últimos) aparecem `c` (novo), `x` (conhecido) e `d` (novo).
2.  O modelo acerta o `x` (ataque) e **perde** o `d`, que nunca viu: precisão 1, recall 0,5, F1 = 2/3. É o vazamento medido: só acerta o que já conhecia.
3.  Das 9 comparações entre vizinhos, 6 mantêm a classe.
4.  Dos três valores do holdout, só `x` já tinha aparecido: 1/3.

```bash title="$ Execução no terminal (na pasta do projeto)"
uv run --locked pytest tests/test_audit_leakage.py -v
```

```text title="Saída esperada"
tests/test_audit_leakage.py::test_temporal_split_takes_the_first_frames_in_order PASSED [ 20%]
tests/test_audit_leakage.py::test_random_split_is_reproducible_with_the_same_seed PASSED [ 40%]
tests/test_audit_leakage.py::test_lookup_learns_known_identities_and_misses_new_ones PASSED [ 60%]
tests/test_audit_leakage.py::test_neighbor_agreement_and_order_prevalence_show_the_bursts PASSED [ 80%]
tests/test_audit_leakage.py::test_reappearance_counts_holdout_values_already_seen PASSED [100%]

============================== 5 passed in 0.19s ==============================
```

**O que aconteceu:** cinco comportamentos em dez linhas. Esses cenários, e os de todas as aulas, entram no catálogo com o comando `lint tests`.

## Erros comuns

**1. `ValueError: Bin edges must be unique` em `order_prevalence`.** Poucos frames para o número de faixas (`bins`); use menos faixas.

**2. F1 sempre zero.** Confira que o rótulo positivo é o certo para o ambiente (`DoS`, `mitm`, `intrusion`) e que a divisão não deixou o holdout sem nenhum ataque.

**3. Resultado diferente do da aula na divisão aleatória.** A semente muda a divisão: use `seed=0` (padrão) e a mesma versão do NumPy; a divisão **temporal** não depende de semente.

**4. Concluir "o MAC é a melhor feature porque reaparece 100%".** Reaparecer é condição para o modelo **memorizar**; é justamente o que o torna identidade do laboratório, e não comportamento.

**5. Treinar o modelo de verdade com a divisão aleatória "só para ver".** Qualquer número obtido assim em dados com rajadas e repetições é otimista. Use sempre o holdout temporal (aula 05).

## Código completo desta aula

??? example "Trecho acrescentado a src/mqtt_ids/audit.py (a partir da linha 272)"

    ```python
    def temporal_split(df: pd.DataFrame, fraction: float = 0.7) -> pd.Series:
        """Verdadeiro nos primeiros `fraction` frames da captura (desenvolvimento)."""
        return pd.Series(np.arange(len(df)) < int(len(df) * fraction), index=df.index)


    def random_split(df: pd.DataFrame, fraction: float = 0.7, seed: int = 0) -> pd.Series:
        """Divisão aleatória, só para mostrar o que ela esconde."""
        rng = np.random.default_rng(seed)
        return pd.Series(rng.random(len(df)) < fraction, index=df.index)


    def lookup_scores(
        df: pd.DataFrame, column: str, positive: str, train: pd.Series
    ) -> dict[str, float]:
        """Classificador de tabela: aprende a taxa de ataque de cada valor da coluna."""
        is_attack = df["type"] == positive
        key = df[column].astype(str).where(df[column].notna(), "(ausente)")
        rate = is_attack[train].groupby(key[train]).mean()
        unseen = float(is_attack[train].mean() > 0.5)
        predicted = key[~train].map(rate).fillna(unseen) > 0.5
        actual = is_attack[~train]
        tp = int((predicted & actual).sum())
        precision = tp / max(int(predicted.sum()), 1)
        recall = tp / max(int(actual.sum()), 1)
        f1 = 2 * precision * recall / max(precision + recall, 1e-12)
        return {"precision": precision, "recall": recall, "f1": f1}


    def identity_leak_table(
        df: pd.DataFrame, positive: str, columns: list[str]
    ) -> pd.DataFrame:
        """F1 do classificador de tabela com divisão temporal e com divisão aleatória."""
        splits = {"temporal": temporal_split(df), "random": random_split(df)}
        rows = {
            column: {
                name: round(lookup_scores(df, column, positive, train)["f1"], 3)
                for name, train in splits.items()
            }
            for column in columns
        }
        return pd.DataFrame(rows).T


    def neighbor_agreement(df: pd.DataFrame, positive: str) -> float:
        """Fração dos frames cuja classe é igual à do frame anterior."""
        is_attack = df["type"] == positive
        return float((is_attack == is_attack.shift()).iloc[1:].mean())


    def order_prevalence(df: pd.DataFrame, positive: str, bins: int = 10) -> list[float]:
        """Prevalência do ataque em cada décimo da captura, em ordem."""
        position = pd.qcut(np.arange(len(df)), bins, labels=False)
        return (df["type"] == positive).groupby(position).mean().round(3).tolist()


    def identity_reappearance(
        df: pd.DataFrame, column: str, fraction: float = 0.7
    ) -> float:
        """Fração dos valores do holdout que já tinham aparecido no desenvolvimento."""
        train = temporal_split(df, fraction)
        seen = set(df.loc[train, column].dropna())
        holdout = df.loc[~train, column].dropna()
        return float(holdout.isin(seen).mean())
    ```

??? example "Arquivo completo: tests/test_audit_leakage.py"

    ```python
    import pandas as pd

    from mqtt_ids.audit import (
        identity_reappearance,
        lookup_scores,
        neighbor_agreement,
        order_prevalence,
        random_split,
        temporal_split,
    )


    def make_frames() -> pd.DataFrame:
        return pd.DataFrame(
            {
                "type": ["normal"] * 4 + ["atk"] * 2 + ["normal"] * 2 + ["atk"] * 2,
                "ip.src": ["a", "a", "b", "b", "x", "x", "a", "c", "x", "d"],
            }
        )


    def test_temporal_split_takes_the_first_frames_in_order() -> None:
        train = temporal_split(make_frames(), 0.7)

        assert train.tolist() == [True] * 7 + [False] * 3


    def test_random_split_is_reproducible_with_the_same_seed() -> None:
        frames = make_frames()

        assert random_split(frames, seed=1).equals(random_split(frames, seed=1))


    def test_lookup_learns_known_identities_and_misses_new_ones() -> None:
        frames = make_frames()
        scores = lookup_scores(frames, "ip.src", "atk", temporal_split(frames, 0.7))

        assert scores == {"precision": 1.0, "recall": 0.5, "f1": 2 / 3}


    def test_neighbor_agreement_and_order_prevalence_show_the_bursts() -> None:
        frames = make_frames()

        assert neighbor_agreement(frames, "atk") == 6 / 9
        assert order_prevalence(frames, "atk", bins=2) == [0.2, 0.6]


    def test_reappearance_counts_holdout_values_already_seen() -> None:
        assert identity_reappearance(make_frames(), "ip.src", 0.7) == 1 / 3
    ```

## Exercícios

Os exercícios continuam em `src/mqtt_ids/exercicios.py`.

1. Escreva `holdout_attack_share(df, positive, fraction=0.7)`, a fração de frames de ataque no holdout temporal, e `leak_gap(df, positive, column)`, a diferença entre o F1 do classificador de tabela com divisão aleatória e com divisão temporal para uma coluna (o "excesso de otimismo" da divisão aleatória). O exercício está pronto quando este teste passar:

    ```python title="tests/test_exercicio_03_7.py"
    import pandas as pd

    from mqtt_ids.exercicios import holdout_attack_share, leak_gap


    def make_frames() -> pd.DataFrame:
        return pd.DataFrame(
            {
                "type": ["normal"] * 6 + ["atk"] * 4,
                "frame.number": list(range(10)),
            }
        )


    def test_holdout_attack_share_is_measured_on_the_last_frames() -> None:
        assert holdout_attack_share(make_frames(), "atk", 0.7) == 1.0


    def test_leak_gap_is_zero_for_a_column_without_any_signal() -> None:
        frames = make_frames().assign(constant="x")

        assert leak_gap(frames, "atk", "constant") == 0.0
    ```

    ```bash title="$ Execução no terminal (na pasta do projeto)"
    uv run --locked pytest tests/test_exercicio_03_7.py
    ```

    Antes da solução:

    ```text title="Saída esperada (antes da solução)"
    E   ImportError: cannot import name 'holdout_attack_share' from 'mqtt_ids.exercicios' (...)
    ERROR tests/test_exercicio_03_7.py
    ```

??? tip "Solução"

    ```python title="src/mqtt_ids/exercicios.py (acrescente ao arquivo)"
    from mqtt_ids.audit import lookup_scores, random_split, temporal_split  # junto dos imports


    def holdout_attack_share(
        df: pd.DataFrame, positive: str, fraction: float = 0.7
    ) -> float:
        holdout = df.loc[~temporal_split(df, fraction), "type"]
        return float((holdout == positive).mean())


    def leak_gap(df: pd.DataFrame, positive: str, column: str) -> float:
        temporal = lookup_scores(df, column, positive, temporal_split(df))["f1"]
        shuffled = lookup_scores(df, column, positive, random_split(df))["f1"]
        return shuffled - temporal
    ```

    Depois da solução: `2 passed`. Nos dados reais, `holdout_attack_share` dá **0,4647** (DoS), **0,0399** (MitM) e **0,0105** (Intrusion), e `leak_gap` para `mqtt.topic` dá **0,886** no DoS (e −0,075 no Intrusion, onde a divisão aleatória por acaso foi pior que a temporal: o ruído aparece quando há poucos ataques).

## Quiz de fixação

??? question "1. Com suas palavras: por que `mqtt.topic` no DoS tem F1 0,000 na divisão temporal e 0,886 na aleatória?"

    Porque os tópicos do mqtt-malaria são aleatórios e **nunca reaparecem** no futuro (só 0,6% dos valores do holdout já tinham aparecido), mas as repetições e as rajadas põem os mesmos tópicos nos dois lados de uma divisão aleatória: o modelo "decora" o teste. É vazamento por conteúdo e por ordem/repetição.

??? question "2. O que significa que a classe do frame anterior prevê a classe atual em 99,4% a 99,99% dos casos?"

    Que o rótulo é fortemente autocorrelacionado: os ataques formam rajadas, e frames vizinhos são quase cópias. Por isso a divisão aleatória é otimista e a validação precisa respeitar a ordem (holdout temporal) e agrupar frames dependentes (blocos de 30 s, ADR-008).

**3. O MAC (`eth.src`) reaparece em 100% do holdout nos três ambientes. O que isso implica?**

- a) Que o holdout temporal não protege contra memorização de identidade, então MAC e IP crus devem ficar fora da política principal
- b) Que o MAC é a melhor feature, pois nunca aparece algo novo no futuro
- c) Que a divisão temporal está errada e deveria ser refeita aleatoriamente

??? question "Resposta da 3"

    **a)**. A divisão temporal remove vizinhança e repetição, mas o laboratório tem poucos aparelhos, todos presentes desde o início: memorizar o MAC funcionaria no holdout sem generalizar. O b) confunde reaparecer com informar comportamento; o c) está errado: a divisão aleatória só pioraria o otimismo.

??? question "4. Revisão da aula 03-2: que relação há entre as duplicatas do DoS e o resultado de `frame.number` (0,897 na divisão aleatória)?"

    O mesmo frame aparece em até 22 linhas idênticas. Numa divisão aleatória, cópias do mesmo frame caem em treino e teste, e o número do frame as liga. Na divisão temporal esses números nunca reaparecem. É um vazamento causado pela repetição, e um argumento a favor da ADR-025.

## Commit

```bash title="$ Execução no terminal (na pasta do projeto)"
git add src/mqtt_ids/audit.py tests/test_audit_leakage.py
git commit -m "feat(audit): medidas de vazamento por identidade, conteúdo e ordem"
```

## Resumo

- Vazamento é usar no treino/avaliação o que não existiria em produção; mede-se com um classificador de tabela e duas divisões (temporal e aleatória).
- No DoS, tópico e `frame.number` valem F1 ≈ 0,9 na divisão aleatória e 0 na temporal; a porta de destino sozinha dá 0,945; no Intrusion nenhuma coluna isolada funciona.
- Frames vizinhos têm a mesma classe em 99,4–99,99% dos casos; o MAC reaparece em 100% do holdout: o holdout temporal ajuda, mas não elimina o vazamento por identidade.

## Fonte principal

[Armadilhas comuns do scikit-learn](https://scikit-learn.org/stable/common_pitfalls.html): leia a definição de vazamento de dados e o exemplo de seleção de atributos antes da divisão.

## Para saber mais

- [Validação cruzada: grupos e séries temporais](https://scikit-learn.org/stable/modules/cross_validation.html)
- [pandas.qcut](https://pandas.pydata.org/docs/reference/api/pandas.qcut.html) e [numpy.random.default_rng](https://numpy.org/doc/stable/reference/random/generator.html)

!!! question "Ficou com dúvida?"

    O agente é o seu professor: pergunte o que não ficou claro, colando a mensagem de erro exata e o que você tentou. Para conversar com pessoas, veja as comunidades em [Recursos](recursos.md#comunidades).

**Próxima aula:** [03-8. O estágio `audit` e o manifesto com hashes](03-8-estagio-audit.md).
