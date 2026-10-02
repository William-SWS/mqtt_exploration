# 03-9. Da evidência à política de features e à modelagem

## Objetivos desta aula

Ao final desta aula você vai entender:

- como transformar as evidências das aulas 03-1 a 03-8 numa **política de features** justificada, e que **derivações mínimas** substituem as identidades cruas;
- por que cada ambiente é, na prática, **um problema de classificação diferente** (e o que mostra o teste de transferência entre eles);
- que consequências a EDA tem para a validação (blocos e *folds*), o desbalanceamento, as duplicatas e as métricas das issues 04 a 15.

E vai ter construído: `derive_portable_candidates`, `candidate_signal_table`, `transfer_matrix` e `block_summary`, e a tabela de política da issue 03. **Nenhum modelo é treinado** nesta aula (a issue 03 proíbe).

**Ganho tangível:** a tabela "coluna → política → evidência", três descobertas operacionais (DoS com 30 s não permite 5 folds; MitM só é visível por camada 2; o que funciona num ambiente não transfere) e o roteiro do que decidir na issue 04.

## Onde estamos

Esta é a última aula da [issue 03](issues/03-data-audit.md). Você já tem o estágio `audit`, três notebooks e as funções de cada análise. O critério final da issue pede "uma política preliminar por coluna com evidência" e a ADR-023 deixou claro que a política **só vira definitiva depois** das análises de vazamento, temporalidade, redundância e portabilidade. Aqui a política deixa de ser preliminar, como **proposta fundamentada**, que você registrará numa ADR sua.

### Relembrando

??? question "1. O que o estágio `audit` registra no manifesto?"

    O hash dos três CSVs de entrada, o contrato de contagens de cada ambiente e o hash de cada tabela e figura gerada. Quem recebe `results/` e o manifesto consegue conferir de que versão dos dados vem cada saída.

??? question "2. Por que `mqtt.topic` no DoS tem F1 zero na divisão temporal e 0,886 na aleatória?"

    Porque os tópicos aleatórios do mqtt-malaria nunca reaparecem no futuro, mas as repetições e rajadas os põem nos dois lados de uma divisão aleatória.

??? question "3. Por que o MAC reaparece em 100% do holdout e ainda assim é perigoso como feature?"

    Porque o laboratório tem poucos aparelhos, todos presentes desde o início: o modelo memoriza a identidade do experimento, e não o comportamento do ataque.

## Antes de começar

As aulas 03-1 a 03-8 concluídas e a suíte verde (`uv run --locked pytest`). Esta aula escreve mais quatro funções em `src/mqtt_ids/audit.py`, mas a parte mais importante é a **decisão** que sai delas.

## Conceitos

### A política de features como hipótese com evidência

O projeto classifica cada coluna em quatro políticas (ADR-006 e dicionário de dados): `portable` (pode entrar na matriz principal), `derivable` (só entra por uma derivação generalizável), `ablation_only` (fica fora da matriz principal e é reintroduzida só em ablações) e `excluded`. Até aqui a política era **preliminar**: baseada em leitura de documentação. As aulas 03-1 a 03-8 trouxeram evidência concreta para cada grupo de colunas. Uma política com evidência permite que um revisor discorde **do argumento**, e não só da conclusão.

### Derivação mínima: comportamento em vez de identidade

Uma **derivação mínima** substitui uma identidade crua por uma propriedade generalizável do mesmo campo. Em vez de "o IP é `192.168.1.196`", "a direção é **privado → privado**". Em vez de "o MAC é `ff:ff:...`", "o frame é **broadcast**". Em vez de "o tópico é `mqtt-malaria/...`", "o frame **tem** tópico". As derivações usadas aqui:

| Derivação | Origem | O que descreve |
|---|---|---|
| `has_ip`, `has_tcp`, `has_mqtt` | presença de `ip.src`, `tcp.srcport`, `mqtt.msgtype` | até que camada o frame chega |
| `msgtype`, `qos` | `mqtt.msgtype`, `mqtt.qos` (ausente = −1) | tipo de pacote e garantia de entrega |
| `mqtt_port` | porta de origem ou destino = 1883 | é tráfego da porta MQTT padrão |
| `broadcast` | `eth.dst` = `ff:ff:ff:ff:ff:ff` | é um broadcast (ARP, no MitM) |
| `direction` | `ip.src`/`ip.dst` privado, público ou ausente | de onde para onde (sem o endereço) |
| `frame_len`, `fields_present` | `frame.len`; quantas colunas `mqtt.*` estão preenchidas | tamanho e riqueza do frame |

O módulo padrão `ipaddress` decide se um IP é privado (`is_private`: não alcançável globalmente, segundo os registros especiais da IANA) e levanta `ValueError` para um texto que não é um IP. A **ausência** não é imputada: vira `-1`, `none` ou uma flag de presença (aula 03-3).

Fonte: [módulo ipaddress](https://docs.python.org/3/library/ipaddress.html).

### Um problema por ambiente

As aulas 03-4 a 03-6 mostraram três ataques de natureza diferente: volume MQTT (DoS), alteração discreta sob a camada IP (MitM) e sessões curtas e miméticas (Intrusion). Se o sinal que separa as classes **muda de camada** de um ambiente para outro, é de esperar que o que um modelo aprende em um **não transfira** para os outros. Isso é testável sem treinar nenhum modelo, com o classificador de tabela da aula 03-7: treina em todos os frames de um ambiente e testa em outro.

### Consequências para a validação

A validação do projeto (ADR-008) usa blocos de 30 s como grupos e cinco *folds* estratificados e agrupados. A documentação do scikit-learn avisa que, no `StratifiedGroupKFold`, cada grupo aparece uma vez no teste, e o número de grupos deve ser **pelo menos** o número de *folds*. Para que **cada fold de validação contenha ataque**, é preciso também que haja pelo menos tantos blocos **com ataque** no desenvolvimento quantos *folds*. A função `block_summary` conta isso por ambiente.

Fonte: [StratifiedGroupKFold (scikit-learn)](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.StratifiedGroupKFold.html).

## Ponte teoria → projeto

A [issue 03](issues/03-data-audit.md) fecha com "uma política preliminar por coluna" e a [ADR-023](DECISIONS.md#adr-023-fonte-semantica-e-contrato-observado-do-dicionario-mqtt_uad) condiciona a política definitiva às análises que você acabou de fazer. A [ADR-006](DECISIONS.md#adr-006-politica-principal-de-features) fixa o princípio (sem identidades, ordem ou metadados de captura) e a [ADR-008](DECISIONS.md#adr-008-holdout-temporal-e-cv-agrupada), a validação. Esta aula une os dois lados: evidência e decisão. Para a sua missão: no portfólio, a política de features deixa de ser "uma lista" e passa a ser **uma tabela com a evidência de cada linha**.

## Mão na massa

### Passo 1 — As derivações

No topo de `src/mqtt_ids/audit.py` acrescente `import ipaddress` (antes de `from pathlib import Path`) e duas constantes depois de `RAW_DIR`: `MQTT_PORT = 1883` e `BROADCAST_MAC = "ff:ff:ff:ff:ff:ff"`. No fim do arquivo:

```python title="src/mqtt_ids/audit.py" linenums="340"
def _scope(address: object) -> str:
    if pd.isna(address):
        return "none"  # (1)!
    try:
        return "private" if ipaddress.ip_address(str(address)).is_private else "public"
    except ValueError:
        return "none"  # (2)!


def derive_portable_candidates(df: pd.DataFrame, positive: str) -> pd.DataFrame:
    """Derivações mínimas candidatas, sem identidade crua, mais o alvo binário."""
    mqtt_columns = [name for name in df.columns if name.startswith("mqtt.")]
    out = pd.DataFrame(index=df.index)
    out["has_ip"] = df["ip.src"].notna()
    out["has_tcp"] = df["tcp.srcport"].notna()
    out["has_mqtt"] = df["mqtt.msgtype"].notna()
    out["msgtype"] = df["mqtt.msgtype"].fillna(-1)  # (3)!
    out["qos"] = df["mqtt.qos"].fillna(-1)
    out["mqtt_port"] = (df["tcp.srcport"] == MQTT_PORT) | (
        df["tcp.dstport"] == MQTT_PORT
    )
    out["broadcast"] = df["eth.dst"] == BROADCAST_MAC
    out["direction"] = df["ip.src"].map(_scope) + ">" + df["ip.dst"].map(_scope)  # (4)!
    out["frame_len"] = df["frame.len"]
    out["fields_present"] = df[mqtt_columns].notna().sum(axis=1)  # (5)!
    out["type"] = np.where(df["type"] == positive, "attack", "normal")  # (6)!
    return out
```

1.  Sem endereço (frame sem IP, como o ARP), o escopo é `none`: a ausência continua sendo uma categoria, não é imputada.
2.  Um texto que não é um IP válido também vira `none` em vez de derrubar a análise.
3.  `-1` marca "não é um pacote MQTT" e fica fora do domínio 1–14 do `msgtype`: a ausência estrutural continua visível.
4.  Concatena os escopos: `private>public`, `none>none`, etc. Nenhum endereço cru sobra.
5.  Quantas colunas `mqtt.*` o frame preenche: um PINGREQ preenche poucas, um PUBLISH com tópico e payload, muitas.
6.  O alvo binário com **o mesmo nome** em todos os ambientes (`attack` / `normal`): é o que permite comparar e pooling.

### Passo 2 — Quanto sinal cada derivação carrega

```python title="src/mqtt_ids/audit.py" linenums="369"
def candidate_signal_table(frames: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """F1 temporal do classificador de tabela para cada derivação e ambiente."""
    features = [name for name in next(iter(frames.values())).columns if name != "type"]
    return pd.DataFrame(
        {
            env: {
                name: round(
                    lookup_scores(df, name, "attack", temporal_split(df))["f1"], 3  # (1)!
                )
                for name in features
            }
            for env, df in frames.items()
        }
    )
```

1.  Reaproveita `lookup_scores` e `temporal_split` da aula 03-7: o F1 de cada derivação **sozinha**, treinando nos primeiros 70% e testando nos últimos 30%, em cada ambiente.

Rascunho `/tmp/p0309.py`:

```python title="/tmp/p0309.py" linenums="1"
import pandas as pd

from mqtt_ids.audit import (
    DATASETS,
    candidate_signal_table,
    derive_portable_candidates,
    load_raw,
)

pd.set_option("display.width", 200)
frames = {
    key: derive_portable_candidates(load_raw(key), positive)
    for key, (filename, positive) in DATASETS.items()
}
print(frames["intrusion"].head(3).to_string())
print()
print(candidate_signal_table(frames))
```

```bash title="$ Execução no terminal (na pasta do projeto)"
uv run --locked python /tmp/p0309.py
```

```text title="Saída esperada"
   has_ip  has_tcp  has_mqtt  msgtype  qos  mqtt_port  broadcast       direction  frame_len  fields_present    type
0    True     True     False     -1.0 -1.0      False      False  private>public         74               0  normal
1    True     True     False     -1.0 -1.0      False      False  public>private         74               0  normal
2    True     True     False     -1.0 -1.0      False      False  private>public         66               0  normal

                  dos   mitm  intrusion
has_ip          0.000  0.000      0.000
has_tcp         0.638  0.000      0.000
has_mqtt        0.929  0.000      0.000
msgtype         0.931  0.000      0.336
qos             0.928  0.000      0.000
mqtt_port       0.988  0.000      0.000
broadcast       0.000  0.880      0.000
direction       0.963  0.000      0.000
frame_len       0.701  0.776      0.074
fields_present  0.927  0.000      0.192
```

**O que aconteceu e como ler:**

- **Nenhuma identidade crua** sobrou: sem IP, MAC, Client ID, tópico ou payload. A primeira tabela mostra as três primeiras linhas do Intrusion já derivadas.
- **DoS:** quase **toda** derivação funciona, com `mqtt_port` em **0,988** e `direction` em **0,963**. O ataque tem MQTT (`has_mqtt` 0,929) e o normal quase não (aula 03-1): "ser MQTT" separa as classes. É um ambiente **fácil**, mas, por isso mesmo, pouco informativo sobre generalização.
- **MitM:** só **`broadcast` (0,880)** e `frame_len` (0,776) têm sinal. As derivações MQTT dão zero: o ataque não está no MQTT. É o resultado das aulas 03-5 e 03-7 resumido numa coluna.
- **Intrusion:** o melhor é `msgtype` (**0,336**), seguido de `fields_present` (0,192). **Nenhuma** derivação **isolada** passa de 0,34: é o único ambiente em que o sinal precisa vir de **combinações** e de **sequências**.
- **`has_ip`:** F1 zero em todos: ter IP não distingue ataque (no MitM o ataque é, na maioria, sem IP; mas o normal também tem frames sem IP, e a derivação sozinha prevê "normal").

### Passo 3 — O que transfere entre ambientes

```python title="src/mqtt_ids/audit.py" linenums="385"
def transfer_matrix(frames: dict[str, pd.DataFrame], column: str) -> pd.DataFrame:
    """F1 treinando em um ambiente (linha) e testando em outro (coluna)."""
    matrix = pd.DataFrame(index=list(frames), columns=list(frames), dtype=float)
    for source, train_df in frames.items():
        for target, test_df in frames.items():
            if source == target:
                train = temporal_split(train_df)  # (1)!
                both = train_df
            else:
                both = pd.concat([train_df, test_df], ignore_index=True)  # (2)!
                train = pd.Series(np.arange(len(both)) < len(train_df))
            matrix.loc[source, target] = lookup_scores(both, column, "attack", train)[
                "f1"
            ]
    return matrix.round(3)
```

1.  Na diagonal (mesmo ambiente) vale a divisão temporal de sempre: treino nos primeiros 70%, teste nos últimos 30%.
2.  Fora da diagonal, concatena os dois ambientes: **todo** o ambiente de treino é treino e **todo** o ambiente de teste é teste (os rótulos já estão unificados em `attack`/`normal`).

```python title="/tmp/p0309b.py" linenums="1"
from mqtt_ids.audit import DATASETS, derive_portable_candidates, load_raw, transfer_matrix

frames = {
    key: derive_portable_candidates(load_raw(key), positive)
    for key, (filename, positive) in DATASETS.items()
}
for column in ("mqtt_port", "msgtype", "broadcast"):
    print("=====", column, "(linha = treino, coluna = teste)")
    print(transfer_matrix(frames, column))
```

```bash title="$ Execução no terminal (na pasta do projeto)"
uv run --locked python /tmp/p0309b.py
```

```text title="Saída esperada"
===== mqtt_port (linha = treino, coluna = teste)
             dos   mitm  intrusion
dos        0.988  0.048      0.324
mitm       0.000  0.000      0.000
intrusion  0.000  0.000      0.000
===== msgtype (linha = treino, coluna = teste)
             dos   mitm  intrusion
dos        0.931  0.016      0.364
mitm       0.000  0.000      0.000
intrusion  0.037  0.000      0.336
===== broadcast (linha = treino, coluna = teste)
           dos  mitm  intrusion
dos        0.0  0.00        0.0
mitm       0.0  0.88        0.0
intrusion  0.0  0.00        0.0
```

**O que aconteceu e como ler:** a diagonal reproduz os números do passo anterior; **fora da diagonal, o desempenho quase some**. `mqtt_port` treinado no DoS dá 0,988 no próprio DoS, **0,324** no Intrusion e **0,048** no MitM; treinado no MitM ou no Intrusion, **zero** em qualquer outro. `broadcast` só funciona no MitM e **não transfere para lugar nenhum**. O sinal de um ambiente é, em boa parte, **específico daquele ambiente**. Duas leituras: (a) um único modelo "para todos os ataques MQTT", treinado com os três, tenderia a aprender a regra do DoS, que domina; (b) **treinar e avaliar um modelo por ambiente** é a escolha honesta, e a transferência vira uma **análise de generalização** (por exemplo, treinar no DoS e testar no Intrusion) e não uma meta.

!!! warning "Limite desta evidência"

    O classificador de tabela usa **uma** derivação por vez e prevê a classe majoritária para valores nunca vistos; modelos que **combinam** derivações (árvores, gradient boosting) podem transferir mais. Os números provam que **cada derivação isolada** não transfere; não provam que nenhum modelo transfere. Isso é tema das issues 06 a 13.

### Passo 4 — Blocos de validação

```python title="src/mqtt_ids/audit.py" linenums="402"
def block_summary(df: pd.DataFrame, positive: str, seconds: int = 30) -> dict[str, int]:
    """Blocos de tempo (grupos de validação) com ataque, no total e por parte."""
    block = (df["frame.time_relative"] // seconds).astype(int)  # (1)!
    is_attack = df["type"] == positive
    train = temporal_split(df)
    everything = pd.Series(True, index=df.index)

    def with_attack(mask: pd.Series) -> int:  # (2)!
        return int(is_attack[mask].groupby(block[mask]).any().sum())

    return {
        "blocks": int(block.nunique()),
        "attack_blocks": with_attack(everything),
        "dev_attack_blocks": with_attack(train),
        "holdout_attack_blocks": with_attack(~train),
    }
```

1.  Divisão inteira do tempo pelo tamanho do bloco: todos os frames de uma mesma janela de `seconds` segundos ficam no mesmo grupo.
2.  Função auxiliar: quantos blocos têm **pelo menos um** frame de ataque dentro de uma parte dos dados (`any` por grupo, somado).

```python title="/tmp/p0309c.py" linenums="1"
from mqtt_ids.audit import DATASETS, block_summary, load_raw

for key, (filename, positive) in DATASETS.items():
    df = load_raw(key)
    for seconds in (10, 30, 60):
        print(key, f"{seconds:>2d} s", block_summary(df, positive, seconds))
```

```bash title="$ Execução no terminal (na pasta do projeto)"
uv run --locked python /tmp/p0309c.py
```

```text title="Saída esperada"
dos 10 s {'blocks': 95, 'attack_blocks': 11, 'dev_attack_blocks': 6, 'holdout_attack_blocks': 5}
dos 30 s {'blocks': 32, 'attack_blocks': 7, 'dev_attack_blocks': 4, 'holdout_attack_blocks': 3}
dos 60 s {'blocks': 16, 'attack_blocks': 5, 'dev_attack_blocks': 3, 'holdout_attack_blocks': 2}
mitm 10 s {'blocks': 471, 'attack_blocks': 77, 'dev_attack_blocks': 50, 'holdout_attack_blocks': 27}
mitm 30 s {'blocks': 157, 'attack_blocks': 37, 'dev_attack_blocks': 22, 'holdout_attack_blocks': 15}
mitm 60 s {'blocks': 79, 'attack_blocks': 25, 'dev_attack_blocks': 15, 'holdout_attack_blocks': 10}
intrusion 10 s {'blocks': 517, 'attack_blocks': 106, 'dev_attack_blocks': 93, 'holdout_attack_blocks': 13}
intrusion 30 s {'blocks': 173, 'attack_blocks': 60, 'dev_attack_blocks': 52, 'holdout_attack_blocks': 8}
intrusion 60 s {'blocks': 87, 'attack_blocks': 42, 'dev_attack_blocks': 36, 'holdout_attack_blocks': 6}
```

**O que aconteceu e como ler:**

- **DoS com blocos de 30 s: só 4 blocos com ataque no desenvolvimento.** Cinco *folds* estratificados exigiriam pelo menos 5: **a configuração da ADR-008 é inviável no DoS**. Com blocos de 10 s há 6, o que **cabe** em cinco *folds*, mas cada rajada de ataque (de 18 a 44 s) é partida em 2 a 5 blocos que podem cair em *folds* diferentes, e a vizinhança entre treino e validação volta. Agrupar **por rajada** (e não só por janela de tempo) é uma alternativa a avaliar. A escolha do agrupamento **por ambiente** é uma decisão da issue 05.
- **MitM e Intrusion:** com 30 s, 22 e 52 blocos com ataque no desenvolvimento: cabem nos cinco *folds*. No Intrusion, porém, o **holdout** tem só **8** blocos de ataque (254 frames): a incerteza da métrica final será grande (ADR-017, intervalos por blocos).
- **Todo bloco com ataque do MitM e do Intrusion é *misto*** (também tem frames normais): a estratificação por bloco não é um problema, e o ataque nunca "ocupa" um bloco inteiro.

## A política de features, com evidência

Resumo das aulas 03-1 a 03-9, por grupo de colunas. A tabela é a **proposta** que você registrará na ADR (exercício 2):

| Grupo de colunas | Política proposta | Evidência | Aula |
|---|---|---|---|
| Alvo `type` | `excluded` (é o rótulo) | binário por ambiente; rótulos `normal` + `DoS`/`mitm`/`intrusion` | 03-2 |
| 19–22 colunas vazias por ambiente (ex.: `frame.comment`, `mqtt.passwd`) | `excluded` | 100% ausentes; o MitM tem 3 vazias a mais | 03-3 |
| 4 constantes (`frame.encap_type`, `frame.ignored`, `frame.marked`, `frame.offset_shift`) | `excluded` | um único estado nos três ambientes; metadados de captura | 03-3 |
| Tempo absoluto e ordem (`frame.time_epoch`, `frame.time_relative`, `frame.number`) | `ablation_only` | `frame.number` F1 0,897 na divisão aleatória e 0 na temporal; rajadas; repetições | 03-2, 03-7 |
| `frame.time_delta`, `frame.time_delta_displayed` | `portable` (avaliar redundância) | mediana quase igual entre classes no DoS; sem vazamento de ordem | 03-4 |
| IPs e MACs (`ip.*`, `eth.*`) | `derivable`: só `direction`, `broadcast`, `has_ip` | atacante também no normal; MAC reaparece em 100%; MAC sob spoofing; `broadcast` F1 0,880 no MitM | 03-5 a 03-7 |
| Portas TCP | `derivable`: só `mqtt_port`; porta efêmera crua `excluded` | `mqtt_port` F1 0,988 no DoS; `tcp.dstport` cru dá 0,945 | 03-7, 03-9 |
| `mqtt.clientid`, `mqtt.topic`, `mqtt.msg` | `ablation_only` | tópico: 0,886 aleatória e 0 temporal; Client IDs copiados do legítimo; payload do relé idêntico | 03-4, 03-6, 03-7 |
| Campos MQTT de protocolo (`mqtt.msgtype`, `mqtt.qos`, flags, `mqtt.len`, `*_len`) | `portable` (ausência como categoria) | ausência estrutural por tipo de pacote; `msgtype` F1 0,931 / 0,336 | 03-1, 03-3, 03-9 |
| `frame.len`, `frame.cap_len` | `portable` | F1 0,776 no MitM (frames ARP de 42 bytes); 0,701 no DoS | 03-5 |

!!! note "Ausências"

    A política de valores ausentes complementa a de colunas: **não imputar** campos estruturalmente ausentes; usar `-1`, `none` ou uma flag de presença (`has_mqtt`), e ajustar qualquer transformação **só no treino de cada fold** (ADR-009).

## Consequências para as próximas issues

Cada item abaixo sai de um número que você mediu. A decisão final é de cada issue.

1. **Um modelo por ambiente** (issues 05 a 15): o sinal muda de camada de um ambiente para o outro e as derivações isoladas não transferem. A transferência entre ambientes entra como análise extra.
2. **Duplicatas (issue 04):** 32.298 no DoS (ADR-025, proposta), contra 37 e 30. Decidir antes de qualquer divisão.
3. **Blocos e *folds* (issue 05):** o DoS não comporta cinco *folds* com blocos de 30 s (4 blocos de ataque no desenvolvimento); testar 10 s como padrão ali, 30 s no MitM e no Intrusion, e registrar a razão. O Intrusion tem 254 frames de ataque no holdout (8 blocos): intervalos de confiança largos.
4. **Desbalanceamento (issues 07 e 08):** prevalência de 48% (DoS), 3,5% (MitM) e 2,35% (Intrusion). **Macro-F1** e recall do ataque como métricas centrais; `accuracy` seria enganosa (prever sempre "normal" daria 96,5% no MitM). Um aviso: o `SMOTENC` do `imbalanced-learn` "não foi projetado para dados só categóricos", e as derivações desta aula são, em maioria, categóricas ou booleanas: a issue 07 precisa verificar isso.
5. **Avaliação por evento (issue 06 em diante):** no Intrusion e no MitM cada ataque é uma rajada curta (7 e 3 frames); medir tempo até o primeiro alerta e falsos alertas por 10.000 frames normais (ADR-011).
6. **Ablação de identidades (issue 10 em diante):** reintroduzir IP, MAC, Client ID e tópico **só** nas ablações da ADR-006, para quantificar quanto o desempenho vem do cenário.

Fonte: [documentação do imbalanced-learn sobre sobreamostragem](https://imbalanced-learn.org/stable/over_sampling.html).

## O notebook de síntese

Não há um quarto notebook: a síntese é uma **seção final** em cada um dos três (`01_eda_dos`, `02_eda_intrusion`, `03_eda_mtmi`), com as respostas curtas às perguntas da síntese do `notebooks/01_eda.ipynb` original (a seção 10):

1. Unidade observada e confiabilidade de schema, tipos e rótulos (aulas 03-1 a 03-3).
2. Principais problemas de qualidade e dependência (duplicatas, ausência estrutural, rajadas).
3. Como as intrusões se distribuem por classe, tempo e evento.
4. Associações portáveis × indicadores de vazamento.
5. Colunas por política.
6. O que vira contrato automatizado (o estágio `audit`) e o que precisa de ADR.

## Testando

```python title="tests/test_audit_policy.py" linenums="1"
import pandas as pd

from mqtt_ids.audit import (
    block_summary,
    candidate_signal_table,
    derive_portable_candidates,
    transfer_matrix,
)

BROADCAST = "ff:ff:ff:ff:ff:ff"


def make_frames() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "type": ["normal", "normal", "atk", "atk", "normal", "atk"],
            "frame.time_relative": [0.0, 5.0, 12.0, 14.0, 25.0, 31.0],
            "ip.src": ["192.168.1.5", "8.8.8.8", "192.168.1.9", None, "10.0.0.1", None],
            "ip.dst": ["8.8.8.8", "192.168.1.5", "192.168.1.5", None, "10.0.0.2", None],
            "tcp.srcport": [50000.0, 443.0, 1883.0, None, 50001.0, None],
            "tcp.dstport": [443.0, 50000.0, 50002.0, None, 1883.0, None],
            "eth.dst": ["aa", "bb", "cc", BROADCAST, "dd", BROADCAST],
            "frame.len": [60, 70, 80, 42, 90, 42],
            "mqtt.msgtype": [None, None, 3.0, None, 3.0, None],
            "mqtt.qos": [None, None, 0.0, None, 0.0, None],
            "mqtt.topic": [None, None, "t", None, "t", None],
        }
    )
```

```python title="tests/test_audit_policy.py" linenums="30"
def test_derivations_describe_behaviour_not_identity() -> None:
    derived = derive_portable_candidates(make_frames(), "atk")

    assert derived["direction"].tolist() == [
        "private>public",
        "public>private",
        "private>private",
        "none>none",
        "private>private",
        "none>none",
    ]
    assert derived["mqtt_port"].tolist() == [False, False, True, False, True, False]
    assert derived["broadcast"].sum() == 2
    assert "ip.src" not in derived.columns  # (1)!
    assert derived["type"].unique().tolist() == ["normal", "attack"]


def test_signal_table_has_a_row_per_derivation_and_a_column_per_environment() -> None:
    frames = {"a": derive_portable_candidates(make_frames(), "atk")}

    table = candidate_signal_table(frames)

    assert table.columns.tolist() == ["a"]
    assert "broadcast" in table.index and "type" not in table.index


def test_transfer_matrix_trains_on_the_row_and_tests_on_the_column() -> None:
    derived = derive_portable_candidates(make_frames(), "atk")
    frames = {"a": derived, "b": derived.copy()}

    matrix = transfer_matrix(frames, "broadcast")

    assert matrix.index.tolist() == ["a", "b"]
    assert matrix.loc["a", "b"] == matrix.loc["b", "a"]  # (2)!


def test_block_summary_counts_time_blocks_with_attack() -> None:
    summary = block_summary(make_frames(), "atk", seconds=10)

    assert summary == {
        "blocks": 4,
        "attack_blocks": 2,
        "dev_attack_blocks": 1,
        "holdout_attack_blocks": 1,
    }
```

1.  O teste mais importante da política: **nenhuma identidade crua** (`ip.src`) sobra nas derivações.
2.  Com dois ambientes idênticos, treinar em um e testar no outro dá o mesmo resultado nos dois sentidos.

```bash title="$ Execução no terminal (na pasta do projeto)"
uv run --locked pytest tests/test_audit_policy.py -v
```

```text title="Saída esperada"
tests/test_audit_policy.py::test_derivations_describe_behaviour_not_identity PASSED [ 25%]
tests/test_audit_policy.py::test_signal_table_has_a_row_per_derivation_and_a_column_per_environment PASSED [ 50%]
tests/test_audit_policy.py::test_transfer_matrix_trains_on_the_row_and_tests_on_the_column PASSED [ 75%]
tests/test_audit_policy.py::test_block_summary_counts_time_blocks_with_attack PASSED [100%]

============================== 4 passed in 0.22s ==============================
```

**O que aconteceu:** quatro comportamentos com seis frames. Faça um último `lint tests` para fechar o catálogo da issue 03 e confira, um a um, os critérios da issue antes de marcá-los.

## Erros comuns

**1. `KeyError: 'mqtt.qos'`.** O DataFrame não é o CSV completo (as derivações usam `ip.src`, `ip.dst`, `tcp.srcport`, `tcp.dstport`, `eth.dst`, `frame.len` e as colunas `mqtt.*`).

**2. Direções estranhas (`none>none` em quase tudo).** Os IPs foram lidos como outro tipo; confira que `ip.src` e `ip.dst` chegam como texto e que `_scope` recebe `NaN` para ausentes.

**3. Matriz de transferência com todos os valores iguais.** Os rótulos dos ambientes não foram unificados: use `derive_portable_candidates`, que devolve `attack`/`normal`.

**4. Concluir "o ambiente DoS é o melhor para treinar".** Ele é o mais **fácil** (F1 0,99 com uma derivação) e o que **menos generaliza**: o sinal depende da presença de MQTT, que no DoS identifica o laboratório.

## Código completo desta aula

??? example "Trecho acrescentado a src/mqtt_ids/audit.py (a partir da linha 340)"

    ```python
    def _scope(address: object) -> str:
        if pd.isna(address):
            return "none"
        try:
            return "private" if ipaddress.ip_address(str(address)).is_private else "public"
        except ValueError:
            return "none"


    def derive_portable_candidates(df: pd.DataFrame, positive: str) -> pd.DataFrame:
        """Derivações mínimas candidatas, sem identidade crua, mais o alvo binário."""
        mqtt_columns = [name for name in df.columns if name.startswith("mqtt.")]
        out = pd.DataFrame(index=df.index)
        out["has_ip"] = df["ip.src"].notna()
        out["has_tcp"] = df["tcp.srcport"].notna()
        out["has_mqtt"] = df["mqtt.msgtype"].notna()
        out["msgtype"] = df["mqtt.msgtype"].fillna(-1)
        out["qos"] = df["mqtt.qos"].fillna(-1)
        out["mqtt_port"] = (df["tcp.srcport"] == MQTT_PORT) | (
            df["tcp.dstport"] == MQTT_PORT
        )
        out["broadcast"] = df["eth.dst"] == BROADCAST_MAC
        out["direction"] = df["ip.src"].map(_scope) + ">" + df["ip.dst"].map(_scope)
        out["frame_len"] = df["frame.len"]
        out["fields_present"] = df[mqtt_columns].notna().sum(axis=1)
        out["type"] = np.where(df["type"] == positive, "attack", "normal")
        return out


    def candidate_signal_table(frames: dict[str, pd.DataFrame]) -> pd.DataFrame:
        """F1 temporal do classificador de tabela para cada derivação e ambiente."""
        features = [name for name in next(iter(frames.values())).columns if name != "type"]
        return pd.DataFrame(
            {
                env: {
                    name: round(
                        lookup_scores(df, name, "attack", temporal_split(df))["f1"], 3
                    )
                    for name in features
                }
                for env, df in frames.items()
            }
        )


    def transfer_matrix(frames: dict[str, pd.DataFrame], column: str) -> pd.DataFrame:
        """F1 treinando em um ambiente (linha) e testando em outro (coluna)."""
        matrix = pd.DataFrame(index=list(frames), columns=list(frames), dtype=float)
        for source, train_df in frames.items():
            for target, test_df in frames.items():
                if source == target:
                    train = temporal_split(train_df)
                    both = train_df
                else:
                    both = pd.concat([train_df, test_df], ignore_index=True)
                    train = pd.Series(np.arange(len(both)) < len(train_df))
                matrix.loc[source, target] = lookup_scores(both, column, "attack", train)[
                    "f1"
                ]
        return matrix.round(3)


    def block_summary(df: pd.DataFrame, positive: str, seconds: int = 30) -> dict[str, int]:
        """Blocos de tempo (grupos de validação) com ataque, no total e por parte."""
        block = (df["frame.time_relative"] // seconds).astype(int)
        is_attack = df["type"] == positive
        train = temporal_split(df)
        everything = pd.Series(True, index=df.index)

        def with_attack(mask: pd.Series) -> int:
            return int(is_attack[mask].groupby(block[mask]).any().sum())

        return {
            "blocks": int(block.nunique()),
            "attack_blocks": with_attack(everything),
            "dev_attack_blocks": with_attack(train),
            "holdout_attack_blocks": with_attack(~train),
        }
    ```

## Exercícios

Os exercícios continuam em `src/mqtt_ids/exercicios.py`.

1. Escreva `largest_feasible_block(df, positive, folds=5, sizes=(60, 30, 10))`, que devolve o **maior** tamanho de bloco (em segundos) com pelo menos `folds` blocos de ataque no desenvolvimento, ou `None` se nenhum serve; e `assert_no_identity(derived, identities)`, que levanta `ValueError("Identidades cruas nas features: a, b")` (nomes em ordem alfabética) se as features contêm alguma coluna de identidade crua. O exercício está pronto quando este teste passar:

    ```python title="tests/test_exercicio_03_9.py"
    import pandas as pd
    import pytest

    from mqtt_ids.exercicios import assert_no_identity, largest_feasible_block

    RAW_IDENTITIES = {"ip.src", "ip.dst", "eth.src", "eth.dst", "mqtt.clientid"}


    def test_largest_feasible_block_prefers_big_blocks_that_still_fit_the_folds() -> None:
        seconds = list(range(0, 120, 5))
        frames = pd.DataFrame(
            {
                "type": ["atk" if (s // 10) % 2 == 0 else "normal" for s in seconds],
                "frame.time_relative": [float(s) for s in seconds],
            }
        )

        assert largest_feasible_block(frames, "atk", folds=2) == 60
        assert largest_feasible_block(frames, "atk", folds=4) == 10
        assert largest_feasible_block(frames, "atk", folds=99) is None


    def test_assert_no_identity_names_the_offending_columns() -> None:
        clean = pd.DataFrame({"has_mqtt": [True], "broadcast": [False]})
        leaky = clean.assign(**{"ip.src": ["10.0.0.1"], "eth.dst": ["aa"]})

        assert_no_identity(clean, RAW_IDENTITIES)
        with pytest.raises(ValueError, match="eth.dst, ip.src"):
            assert_no_identity(leaky, RAW_IDENTITIES)
    ```

    ```bash title="$ Execução no terminal (na pasta do projeto)"
    uv run --locked pytest tests/test_exercicio_03_9.py
    ```

    Antes da solução:

    ```text title="Saída esperada (antes da solução)"
    E   ImportError: cannot import name 'assert_no_identity' from 'mqtt_ids.exercicios' (...)
    ERROR tests/test_exercicio_03_9.py
    ```

??? tip "Solução"

    ```python title="src/mqtt_ids/exercicios.py (acrescente ao arquivo)"
    from mqtt_ids.audit import block_summary  # junto dos imports de audit


    def largest_feasible_block(
        df: pd.DataFrame,
        positive: str,
        folds: int = 5,
        sizes: tuple[int, ...] = (60, 30, 10),
    ) -> int | None:
        for seconds in sizes:
            summary = block_summary(df, positive, seconds)
            if summary["dev_attack_blocks"] >= folds:
                return seconds
        return None


    def assert_no_identity(derived: pd.DataFrame, identities: set[str]) -> None:
        present = sorted(identities.intersection(derived.columns))
        if present:
            raise ValueError("Identidades cruas nas features: " + ", ".join(present))
    ```

    Depois da solução: `2 passed`. Com os dados reais, `largest_feasible_block` devolve **10** para o DoS, **60** para o MitM e **60** para o Intrusion (com cinco *folds*): confirma que o DoS exige blocos menores.

2. **Sem teste automático.** Escreva a **ADR-027** em `docs/DECISIONS.md` (no fim do arquivo, sem alterar as anteriores), com o formato das demais ADR (data, status, decisão, evidência, alternativas, consequências), registrando a política de features da tabela acima. Use **status `proposta`** até validar com a issue 04. Dica: a evidência são os números das aulas, citados com a aula de origem, e a decisão fica mais curta que a evidência.

## Quiz de fixação

??? question "1. Com suas palavras: por que `direction` (privado/público) é melhor feature que o IP cru?"

    O IP cru identifica máquinas do laboratório (o atacante também gera tráfego normal, e o IP do atacante muda de papel entre os ambientes). A direção descreve de onde para onde o tráfego vai, é generalizável a outras redes e não permite ao modelo memorizar aparelhos.

??? question "2. Por que cinco *folds* com blocos de 30 s são inviáveis no DoS?"

    Porque o desenvolvimento só tem 4 blocos de 30 s com ataque (o ataque ocupa três rajadas): com cinco *folds* estratificados e agrupados, algum fold de validação ficaria sem nenhum frame de ataque. Blocos de 10 s dão 6 blocos de ataque.

**3. O que mostra a matriz de transferência de `mqtt_port`?**

- a) Que a regra aprendida no DoS quase não funciona no MitM e funciona pouco no Intrusion, e que MitM e Intrusion não transferem nada
- b) Que a porta MQTT é a melhor feature em todos os ambientes
- c) Que treinar com os três ambientes juntos sempre melhora o F1

??? question "Resposta da 3"

    **a)**. 0,988 no DoS, 0,324 no Intrusion, 0,048 no MitM e zero nas outras linhas. O b) é contrariado pela coluna do MitM e do Intrusion; o c) não foi testado e a matriz sugere o contrário (o DoS domina).

??? question "4. Revisão da aula 03-7: o que a divisão temporal elimina e o que ela **não** elimina?"

    Elimina o vazamento por vizinhança e por repetição (os frames repetidos e as rajadas ficam todos no mesmo lado). Não elimina o vazamento por identidade: o MAC reaparece em 100% do holdout, por isso identidades ficam fora da política principal.

## Commit

```bash title="$ Execução no terminal (na pasta do projeto)"
git add src/mqtt_ids/audit.py tests/test_audit_policy.py docs/DECISIONS.md
git commit -m "feat(audit): derivações candidatas, transferência e blocos; política de features (ADR-027)"
```

Quando todos os critérios da [issue 03](issues/03-data-audit.md) estiverem verificados, marque-os no arquivo da issue e abra a issue 04 (contrato, limpeza e features portáveis).

## Resumo

- A política de features proposta tem evidência por grupo de colunas; identidades cruas viram derivações mínimas (`direction`, `broadcast`, `mqtt_port`, `has_*`).
- Cada ambiente pede um modelo: o sinal muda de camada (DoS: MQTT; MitM: broadcast/camada 2; Intrusion: combinações e sequências) e as derivações isoladas não transferem.
- Consequências: decidir as duplicatas do DoS, blocos de 10 s no DoS, atenção ao holdout do Intrusion (8 blocos), métricas por evento e cuidado com `SMOTENC` em features categóricas.

## Fonte principal

[StratifiedGroupKFold (scikit-learn)](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.StratifiedGroupKFold.html): leia a restrição de que o número de grupos deve ser pelo menos o número de *folds*.

## Para saber mais

- [Módulo ipaddress](https://docs.python.org/3/library/ipaddress.html)
- [imbalanced-learn: sobreamostragem (SMOTE, SMOTENC)](https://imbalanced-learn.org/stable/over_sampling.html)
- [Armadilhas comuns do scikit-learn](https://scikit-learn.org/stable/common_pitfalls.html)

!!! question "Ficou com dúvida?"

    O agente é o seu professor: pergunte o que não ficou claro, colando a mensagem de erro exata e o que você tentou. Para conversar com pessoas, veja as comunidades em [Recursos](recursos.md#comunidades).

**Próxima aula:** a issue 04 (contrato, limpeza e features portáveis) ainda não tem aula.
