# Kaggle: salvar e recuperar datasets e modelos

Pesquisa feita em 23-08-2026, exclusivamente nas fontes oficiais mantidas pelo
Kaggle. Esta é a política operacional do projeto para que datasets e modelos
possam ser recuperados em qualquer máquina autorizada. Ela não substitui a
validação de integridade que o projeto deve fazer após cada download.

## Política adotada pelo projeto

Usar dois ativos Kaggle privados, ambos com versões imutáveis na prática:

| Ativo do projeto | Recurso Kaggle | Conteúdo | Handle obrigatório para recuperar |
| --- | --- | --- | --- |
| Dados brutos | Dataset | `Intrusion.csv`, `DoS.csv`, `MitM.csv` e metadata de atribuição | `OWNER/SLUG/versions/N` |
| Modelo treinado | Model, em uma variação por framework | `*.joblib` ou `state_dict`, `metadata.json`, manifesto e SHA-256 | `OWNER/MODEL/FRAMEWORK/VARIATION/N` |

O Dataset espelha a árvore `data/`: os CSVs imutáveis ficam em `raw/` e os
artefatos derivados, quando existirem, ficam separados em `interim/` e
`processed/`. Cada treinamento que produzir um artefato concluído deve montar o
diretório de sua versão de modelo, enviar esse diretório ao Kaggle Model e gravar
o handle retornado/fixado no manifesto local. Para modelos sklearn, a variação
deve usar `sklearn`; para MLPs, `pytorch`. Um artefato que não seja realmente um
modelo pode usar um Dataset privado separado como fallback, mas não substitui o
registro do modelo.

Os recursos começam privados. Acesso em outra máquina requer a mesma conta Kaggle
ou colaboração autorizada; somente depois de revisão humana de conteúdo,
atribuição, licença e hashes alguém pode alterar a visibilidade. Não há publicação
automática como público.

## Acesso de outras pessoas aos ativos

Um handle identifica o ativo, mas **não concede acesso**. Há duas políticas
possíveis, escolhidas por ativo na interface do Kaggle:

| Visibilidade | Quem pode baixar | Como a pessoa configura o projeto |
| --- | --- | --- |
| Privado | Dono e colaboradores convidados. No Dataset: **Settings > Sharing**, com `Can view` para somente baixar ou `Can edit` para alterar. Em Models, o colaborador também precisa de acesso ao Model privado. | Cada pessoa cria seu próprio token/API login e preenche os mesmos handles versionados no seu `.env`. |
| Público | Qualquer pessoa pode visualizar e baixar. | O handle versionado pode ser usado no projeto; autenticação ainda pode ser solicitada pelo Kaggle para alguns ativos/consentimentos. |

Nunca compartilhe `KAGGLE_API_TOKEN`, `access_token` ou `kaggle.json` com outra
pessoa. O token identifica a conta que faz a chamada e dá a ela as permissões
associadas. Para colaborar mantendo os dados fechados, convide a conta Kaggle da
pessoa; para distribuição irrestrita, revise atribuição, licença e hashes e só
então altere o ativo para público manualmente.

Fontes: [Datasets: visibilidade e compartilhamento](https://www.kaggle.com/docs/datasets),
[Models: acesso a privados](https://www.kaggle.com/docs/models) e
[autenticação KaggleHub](https://github.com/Kaggle/kagglehub#authenticate).

## Configuração iterativa executada neste repositório

Esta configuração foi implementada em 23-08-2026. Foram adicionadas as
dependências oficiais `kaggle` e `kagglehub`, preservando `uv.lock`, e o comando
`mqtt-kaggle-assets`. O código fica em `src/mqtt_ids/kaggle_assets.py`; ele não
contém handle de conta nem segredo. Antes de cada chamada de rede, ele valida o
formato do handle, a estrutura do pacote e os hashes relevantes.

**Estado da execução:** os três CSVs foram encontrados e validados localmente em
`data/raw/MQTT Under Attack Dataset/`; não há artefato de modelo além do diretório
vazio `artifacts/models/`. Há um token configurado localmente, mas o nome de
usuário/handle Kaggle ainda não foi informado. Portanto, nenhum upload remoto foi
tentado: não é seguro inventar um destino. Os passos 2 e 3 abaixo são o único
trecho ainda necessário para publicar os dados reais.

O comando opera sobre a árvore inteira abaixo. Dessa forma, uma única versão do
Dataset pode preservar os dados hoje existentes em `raw` e as futuras saídas
`interim` e `processed`, mantendo suas categorias distintas:

```text
data/
├── raw/
│   └── MQTT Under Attack Dataset/
│       ├── Intrusion.csv
│       ├── DoS.csv
│       └── MitM.csv
├── interim/
└── processed/
```

O upload gera temporariamente `kaggle-provenance.json` com tamanhos e SHA-256
dos três CSVs; ele não altera os arquivos brutos nem grava esse manifesto em
`data/`. Os hashes conhecidos são verificados **antes** do upload. Um download
de `raw` verifica-os novamente.

### Passo 1 — autenticar uma máquina, sem versionar segredo

Na máquina que enviará ou baixará ativos privados, crie um token em **Kaggle >
Settings > API** e injete-o somente na sessão/gerenciador de segredos. Para uso
local, copie `.env.example` para `.env` e preencha nele o token e seus handles;
o comando `mqtt-kaggle-assets` carrega esse arquivo automaticamente:

```bash
cp .env.example .env
# editar .env localmente; nunca enviar esse arquivo ao Git
```

Alternativamente, sem definir a variável, execute `uv run --locked kaggle auth
login` para concluir o fluxo OAuth. A autenticação é por máquina; repita-a em
cada computador autorizado. Não inclua o export em arquivo rastreado, não chame
`kaggle auth print-access-token` e não copie `kaggle.json` para o projeto. O
`.gitignore` já protege os formatos de credencial conhecidos.

`RAW_HASHES` permanece no código por ser uma âncora pública e versionada de
integridade, não uma credencial. Token e handles privados pertencem ao `.env`;
um hash ou DOI público não deve ser movido para lá, pois impediria revisão e
auditoria reprodutíveis.

### Passo 2 — escolher os handles privados uma única vez

Substitua `OWNER` pelo seu nome de usuário Kaggle e conserve estes nomes em um
local privado de configuração ou no manifesto de cada execução, nunca em um
segredo:

```text
Dataset: OWNER/mqtt-under-attack-data
Model sklearn: OWNER/mqtt-ids/sklearn/baseline
Model PyTorch: OWNER/mqtt-ids/pytorch/tiny-mlp
```

O handle de upload não tem versão. No primeiro upload, o cliente oficial cria o
recurso privado e envia os arquivos; o mesmo handle cria as versões seguintes.
O handle de recuperação **sempre** inclui uma versão:
`OWNER/mqtt-under-attack-data/versions/N` para datasets e
`OWNER/mqtt-ids/sklearn/baseline/N` para modelos.

#### O que é um handle e o que cada variável significa

Um *handle* é o endereço lógico de um ativo no Kaggle; não é token, senha ou
URL. Ele identifica o recurso que receberá upload ou a versão exata que será
baixada. O comando lê as variáveis abaixo do `.env`, mas `--handle` sempre pode
sobrescrevê-las pontualmente.

| Variável | Formato | Serve para | Como preencher |
| --- | --- | --- | --- |
| `KAGGLE_DATASET_HANDLE` | `OWNER/SLUG` | Upload: criar o Dataset privado com arquivos no primeiro envio ou acrescentar versão depois. | `OWNER` é seu identificador no Kaggle; `SLUG` é o nome curto e estável que você escolhe, por exemplo `mqtt-under-attack-data`. |
| `KAGGLE_DATASET_VERSION_HANDLE` | `OWNER/SLUG/versions/N` | Download reprodutível de uma versão de dados. | Após o upload, consulte a página **Versions** do Dataset e substitua `N` pelo número criado, por exemplo `1`. |
| `KAGGLE_MODEL_HANDLE` | `OWNER/MODEL/FRAMEWORK/VARIATION` | Upload: criar Model/Variation privados no primeiro envio ou acrescentar versão depois. | `MODEL` agrupa o modelo; `FRAMEWORK` é `sklearn` ou `pytorch`; `VARIATION` separa receitas, por exemplo `baseline` ou `tiny-mlp`. |
| `KAGGLE_MODEL_VERSION_HANDLE` | `OWNER/MODEL/FRAMEWORK/VARIATION/N` | Download reprodutível de uma versão de modelo. | Após o upload, obtenha `N` na página **Versions** da variação e fixe-o nesta variável. |

Exemplo completo, que pode ser copiado para o `.env` após trocar somente
`seu-usuario` e os números de versão reais:

```dotenv
KAGGLE_DATASET_HANDLE=seu-usuario/mqtt-under-attack-data
KAGGLE_DATASET_VERSION_HANDLE=seu-usuario/mqtt-under-attack-data/versions/1
KAGGLE_MODEL_HANDLE=seu-usuario/mqtt-ids/sklearn/baseline
KAGGLE_MODEL_VERSION_HANDLE=seu-usuario/mqtt-ids/sklearn/baseline/1
```

`OWNER` normalmente é o trecho final da URL do seu perfil Kaggle. Não use o
nome de exibição se ele for diferente do identificador da URL. Para vários
modelos, mantenha no `.env` o handle mais usado e forneça `--handle` nos demais
comandos; um único campo não precisa representar todo o registry.

#### Como o projeto cria e usa esses recursos

1. Escolha os nomes acima e salve os dois handles de **upload** no `.env`.
   Eles não incluem `N`, porque o KaggleHub precisa do recurso/variação, não de
   uma versão já existente, para publicar.
2. Execute `upload-dataset` com `data/`. Um Dataset Kaggle precisa de arquivos,
   portanto esse primeiro envio cria o Dataset privado `OWNER/SLUG` e sobe a
   árvore `data/raw`, `data/interim` e `data/processed` preservando os caminhos.
   Não é preciso criar um Dataset vazio na UI antes disso. Reexecutar o comando
   com o mesmo handle cria uma nova versão.
3. Abra a página do Dataset no Kaggle, localize a nova versão na aba
   **Versions** e registre seu número em `KAGGLE_DATASET_VERSION_HANDLE`.
   Este é o único formato aceito pelo comando de download para evitar que uma
   versão “mais recente” mude silenciosamente o experimento.
4. Quando houver um pacote em `artifacts/models/<run>`, execute
   `upload-model` com o handle escolhido. O primeiro envio cria o Model e a
   Variation privados; cada envio posterior cria nova versão da mesma variação.
   Framework e variação são parte da identidade, portanto nunca mude esses
   segmentos para publicar uma atualização do mesmo modelo.
5. Na aba **Versions** da Variation, copie o número criado para
   `KAGGLE_MODEL_VERSION_HANDLE`. Só então qualquer máquina autorizada poderá
   recuperar exatamente aqueles pesos, metadata e manifesto.

Os handles não são segredos criptográficos, mas ficam no `.env` por serem
configuração particular desta conta e deste ambiente. `KAGGLE_API_TOKEN`, ao
contrário, é segredo e jamais deve aparecer em documentação, log ou manifesto.

Fontes do formato e criação: [KaggleHub: upload/download](https://github.com/Kaggle/kagglehub),
[criação privada de Dataset no cliente oficial](https://github.com/Kaggle/kagglehub/blob/main/src/kagglehub/datasets_helpers.py) e
[criação privada de Model no cliente oficial](https://github.com/Kaggle/kagglehub/blob/main/src/kagglehub/models_helpers.py).

### Passo 3 — publicar os dados atualmente presentes em `data/`

Depois de autenticar e substituir o handle, execute uma única vez:

```bash
uv run --locked mqtt-kaggle-assets upload-dataset \
  --handle OWNER/mqtt-under-attack-data \
  --data-dir data \
  --version-notes 'Espelho inicial: CSVs raw validados por SHA-256'
```

Com os handles preenchidos no `.env`, `--handle` pode ser omitido: upload usa
`KAGGLE_DATASET_HANDLE`, enquanto download usa
`KAGGLE_DATASET_VERSION_HANDLE`. Os equivalentes de modelo são
`KAGGLE_MODEL_HANDLE` e `KAGGLE_MODEL_VERSION_HANDLE`.

O comando envia `raw/`, `interim/` e `processed/`, mas só há CSVs em `raw` neste
momento. Quando uma etapa futura gerar arquivos em `interim/` ou `processed/`,
repita o mesmo comando com uma nota que descreva a alteração; não crie um
Dataset paralelo e não apague versões anteriores. No Kaggle, anote o número
`N` da versão recém-criada e associe `OWNER/mqtt-under-attack-data/versions/N`
ao manifesto da execução que a usou.

### Passo 4 — restaurar os dados em qualquer máquina autorizada

Baixe uma categoria específica para dentro da mesma árvore `data/`:

```bash
# Restaura somente a cópia imutável em data/raw/ e recalcula seus hashes.
uv run --locked mqtt-kaggle-assets download-dataset \
  --handle OWNER/mqtt-under-attack-data/versions/N \
  --data-dir data \
  --category raw

# Restaura somente dados derivados para data/interim/ ou data/processed/.
uv run --locked mqtt-kaggle-assets download-dataset \
  --handle OWNER/mqtt-under-attack-data/versions/N \
  --data-dir data \
  --category interim
```

Troque `interim` por `processed` para a terceira categoria. Sem `--category`, o
comando restaura a árvore toda. Para não misturar uma cópia já existente, use
primeiro outra raiz, por exemplo `--data-dir /tmp/mqtt-restore/data`, examine os
arquivos e só então promova-os para a pasta desejada. O runner rejeita handles
sem versão antes do download.

### Passo 5 — publicar cada modelo treinado

Cada treinamento concluído deve criar um diretório único dentro de
`artifacts/models/`, por exemplo `artifacts/models/run-<identidade>/`, contendo:

```text
model.joblib                 # sklearn; ou model_state_dict.pt para PyTorch
metadata.json                # framework, arquitetura, dependências e parâmetros
manifest.json                # identidade da execução e dataset versionado de entrada
sha256sums.txt               # SHA-256 de todos os arquivos do pacote
```

`sha256sums.txt` segue o formato `SHA256  caminho-relativo`. Depois de gerar o
pacote, publique-o na variação correspondente ao framework:

```bash
uv run --locked mqtt-kaggle-assets upload-model \
  --handle OWNER/mqtt-ids/sklearn/baseline \
  --model-dir artifacts/models/run-IDENTIDADE \
  --version-notes 'run IDENTIDADE; dataset OWNER/mqtt-under-attack-data/versions/N'
```

O comando recusa pacote sem peso (`.joblib`, `.pt` ou `.pth`), metadata,
manifesto ou hashes válidos; portanto, não publica um modelo incompleto. Após o
Kaggle informar a versão `N`, registre no manifesto local
`OWNER/mqtt-ids/sklearn/baseline/N`.

### Passo 6 — restaurar um modelo em qualquer máquina autorizada

```bash
uv run --locked mqtt-kaggle-assets download-model \
  --handle OWNER/mqtt-ids/sklearn/baseline/N \
  --output-dir artifacts/models
```

O download só é aceito para versão explícita e o pacote é verificado contra
`sha256sums.txt` antes que o código de treino/inferência o carregue.

## Autenticação sem vazar segredo

O cliente atual do Kaggle oferece quatro alternativas documentadas:

1. `kaggle auth login` abre o fluxo OAuth;
2. `KAGGLE_API_TOKEN` recebe o token criado em **Kaggle > Settings > API**;
3. o mesmo token pode ficar em `~/.kaggle/access_token`;
4. por compatibilidade, a chave legada gera `~/.kaggle/kaggle.json`.

O `kagglehub` também aceita `kagglehub.login()` (prompt do token) e reutiliza a
autenticação já configurada pela CLI. A referência de autenticação da CLI cita
também as variáveis legadas `KAGGLE_USERNAME` e `KAGGLE_KEY`.

Para automação, preferir um segredo injetado pelo ambiente (`KAGGLE_API_TOKEN`)
ou pelo gerenciador de segredos do CI. Não incluir token, `kaggle.json`,
`access_token`, nem valores de variáveis `KAGGLE_*` em Git, logs, mensagens de
erro ou manifestos. Arquivo local de credenciais deve ter permissões restritas.

Fontes: [CLI: autenticação](https://github.com/Kaggle/kaggle-cli/blob/main/docs/README.md#authentication),
[referência de auth](https://github.com/Kaggle/kaggle-cli/blob/main/skills/references/auth.md),
[KaggleHub: autenticação](https://github.com/Kaggle/kagglehub#authenticate).

## Espelho privado de um dataset

`kaggle datasets create` precisa de uma pasta contendo os arquivos e
`dataset-metadata.json`; `kaggle datasets init -p <pasta>` gera o esqueleto. O
metadata inclui, entre outros, `title`, `id` (`owner/slug`) e exatamente uma
licença. O comportamento padrão de `create` é **privado**: `--public` é a flag
que o torna público.

Exemplo de fluxo, depois de preparar/validar os três CSVs em uma pasta de
publicação:

```bash
kaggle datasets init -p artifacts/kaggle-dataset
# editar dataset-metadata.json: id, título, descrição, licença e atribuição
kaggle datasets create -p artifacts/kaggle-dataset -q -t -r skip
kaggle datasets status OWNER/SLUG --format json
```

Para alterar o conteúdo, reenviar a pasta e registrar uma nota de versão:

```bash
kaggle datasets version -p artifacts/kaggle-dataset \
  -m "Descrição verificável da alteração" -q -t -r skip
kaggle datasets status OWNER/SLUG --format json
```

`datasets version` cria uma nova versão; a nota (`-m`) é obrigatória. **Não usar
`--delete-old-versions`** neste fluxo de proveniência: isso conflita com a
necessidade de recuperar uma versão histórica. Antes de divulgar o espelho, a
revisão manual deve confirmar licença/atribuição de origem, conteúdo e hashes.

Fontes: [referência da CLI de datasets](https://github.com/Kaggle/kaggle-cli/blob/main/docs/datasets.md),
[formato de metadata](https://github.com/Kaggle/kaggle-cli/blob/main/docs/datasets_metadata.md).

### Checklist para salvar uma nova versão de dados

1. Monte uma pasta temporária somente com os três CSVs imutáveis e
   `dataset-metadata.json`; confira os três nomes, tamanhos e SHA-256.
2. Na primeira vez, execute `kaggle datasets create -p <pasta>` sem `--public`.
   Anote o handle `OWNER/SLUG` no cenário do projeto.
3. Em toda alteração posterior, execute `kaggle datasets version -p <pasta> -m
   "<motivo verificável>"`; não use `--delete-old-versions`.
4. Consulte `kaggle datasets status OWNER/SLUG --format json`, identifique a
   versão criada e registre `OWNER/SLUG/versions/N` no manifesto.
5. Faça um download limpo da versão `N` e recalcule os hashes antes de marcar a
   publicação como válida.

## Recuperar uma versão exata

O mecanismo documentado que expressa explicitamente a versão é o KaggleHub:

```python
import kagglehub

directory = kagglehub.dataset_download(
    "OWNER/SLUG/versions/N",
    output_dir=".cache/kaggle/datasets/OWNER-SLUG-N",
)
```

Sem `/versions/N`, o KaggleHub baixa a versão mais recente; portanto, para
reprodutibilidade o runner deve rejeitar esse handle antes de chamar a
biblioteca. Fora de notebooks Kaggle, o destino padrão do KaggleHub é
`~/.cache/kagglehub/`; `output_dir` torna o local explícito. `force_download`
baixa novamente mesmo que haja cache, mas não substitui a verificação local de
SHA-256 feita pelo projeto.

A CLI permite listar arquivos antes de buscar (`kaggle datasets files
OWNER/SLUG`) e baixar todos ou um arquivo (`kaggle datasets download ...`), mas
a referência atual da CLI não documenta um seletor de versão neste comando.
Para esta task, usar o handle versionado do KaggleHub para o download e a CLI
para criação/status é a combinação mais inequívoca.

Fonte: [KaggleHub: download de dataset](https://github.com/Kaggle/kagglehub#download-dataset),
[CLI: files/download/status](https://github.com/Kaggle/kaggle-cli/blob/main/docs/datasets.md).

## Salvar modelos treinados no Kaggle Models

Há duas opções oficiais, com finalidades diferentes:

Kaggle Models é o registro escolhido para modelos reutilizáveis. Crie o modelo e
sua variação na UI ou CLI uma vez; mantenha-a privada. A documentação oficial
confirma que versões privadas podem ser usadas por colaboradores autorizados e
que a mudança para público é uma ação posterior nas configurações do modelo.
Uma versão deve enviar **o diretório inteiro** do artefato, nunca apenas o peso:

```
artifacts/model-package/
├── model.joblib              # ou model_state_dict.pt
├── metadata.json             # arquitetura, framework, versões e parâmetros
├── manifest.json             # identidade da execução e handle do dataset de entrada
└── sha256sums.txt            # hashes de todos os arquivos acima
```

Assim, baixar o modelo em outra máquina restaura tanto os pesos quanto a
informação necessária para carregá-los e auditá-los. Outputs de Notebook são
adequados para uma execução descartável, mas não são o registry principal deste
projeto.

Exemplos para Models:

```python
import kagglehub

handle = "OWNER/MODEL/FRAMEWORK/VARIATION"
kagglehub.model_upload(
    handle,
    "artifacts/model-package",
    version_notes="run RUN_ID; dataset OWNER/SLUG/versions/N",
)
local = kagglehub.model_download(
    "OWNER/MODEL/FRAMEWORK/VARIATION/N",
    output_dir="artifacts/downloaded-model-N",
)
```

Pela CLI, a criação da versão seguinte de uma variação é:

```bash
kaggle models variations versions create OWNER/MODEL/FRAMEWORK/VARIATION \
  -p artifacts/model-package -n "run RUN_ID; dataset OWNER/SLUG/versions/N"
```

Depois do upload, identifique a versão criada e escreva somente o handle com
`/N` no manifesto da execução. Para restaurar, autentique-se, baixe em um
diretório explícito, valide `sha256sums.txt` e só então carregue o modelo.
Nunca use um handle sem a versão no runner, pois ele significa “mais recente” e
deixa de reproduzir a execução original.

Fontes: [Kaggle Models](https://www.kaggle.com/docs/models),
[KaggleHub: modelos](https://github.com/Kaggle/kagglehub#download-model),
[KaggleHub: upload de modelo](https://github.com/Kaggle/kagglehub#upload-model),
[tutorial da CLI: versão de variação](https://github.com/Kaggle/kaggle-cli/blob/main/docs/tutorials.md#tutorial-create-a-model-variation-version),
[CLI: outputs de notebooks](https://github.com/Kaggle/kaggle-cli/blob/main/docs/kernels.md),
[KaggleHub: outputs](https://github.com/Kaggle/kagglehub#download-notebook-outputs),
[tutorial da CLI para modelos](https://github.com/Kaggle/kaggle-cli/blob/main/docs/tutorials.md).

## Implicação para a task 02

Kaggle fornece armazenamento/download e identificação de versão, mas não prova
que os bytes locais são os esperados pelo projeto. O estágio ainda deve: exigir
o handle versionado; verificar os três nomes exatos e SHA-256 streaming; só
promover uma transferência completa para o diretório final; manter cache e
manifesto coerentes; e registrar dados públicos de proveniência (owner/slug,
versão, licença, DOI/autores quando disponíveis, tamanhos e hashes), nunca
credenciais. Para modelos, deve ainda publicar o pacote completo, registrar o
handle versionado no manifesto e verificar os hashes do pacote antes de carregá-lo.
