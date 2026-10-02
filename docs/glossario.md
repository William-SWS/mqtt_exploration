# Glossário

A linguagem do curso: cada conceito tem uma palavra, usada em todas as aulas. Os termos entram na aula que os explica.

### Ambiente de projeto
A "caixa" com o Python e as bibliotecas de um único projeto, criada e mantida pelo `uv` na pasta `.venv` a partir do lockfile.
_Evite_: venv, virtualenv. Aula: [01-1](01-1-ambiente-e-pacote.md#ambiente-reproduzivel-pyprojecttoml-uvlock-e-venv)

### Lockfile
O arquivo `uv.lock`: registra as versões exatas de todos os pacotes resolvidos, para que duas instalações sejam idênticas. Vai para o Git.
_Evite_: arquivo de travamento. Aula: [01-1](01-1-ambiente-e-pacote.md#ambiente-reproduzivel-pyprojecttoml-uvlock-e-venv)

### Grupo de dependências
Conjunto nomeado de pacotes só de desenvolvimento (`dev`, `notebook`) declarado em `[dependency-groups]` e fora dos requisitos de execução do projeto.
_Evite_: extras, requirements-dev. Aula: [01-1](01-1-ambiente-e-pacote.md#grupos-de-dependencias)

### Layout `src`
Organização em que o código importável fica em `src/<pacote>/`, de modo que só se importa o pacote depois de instalado.
Aula: [01-1](01-1-ambiente-e-pacote.md#layout-src-e-ponto-de-entrada)

### Ponto de entrada
Linha de `[project.scripts]` que transforma uma função (`módulo:função`) em um comando instalado no ambiente, como `mqtt-ids`.
_Evite_: script solto. Aula: [01-1](01-1-ambiente-e-pacote.md#layout-src-e-ponto-de-entrada)

### Cenário
Arquivo YAML que descreve uma execução (`run.name`, `run.seed` e, opcionalmente, `dataset`). Depois de validado vira um objeto `Scenario`.
_Evite_: config, arquivo de configuração. Aula: [01-2](01-2-cenario-yaml.md#yaml-seguro-e-contrato-de-configuracao)

### Falhar cedo
Validar entradas antes de executar qualquer estágio, para que um erro de configuração apareça na hora e não depois de horas de execução.
Aula: [01-2](01-2-cenario-yaml.md#yaml-seguro-e-contrato-de-configuracao)

### Dataclass imutável
Classe gerada por `@dataclass(frozen=True)`: seus campos não podem ser reatribuídos depois da criação (`FrozenInstanceError`). Usada para dados já validados, como `Scenario`.
Aula: [01-2](01-2-cenario-yaml.md#dados-imutaveis-e-erro-com-nome-proprio)

### Teste parametrizado
Uma função de teste executada uma vez por linha de uma tabela de casos, com `@pytest.mark.parametrize`.
Aula: [01-2](01-2-cenario-yaml.md#testes-parametrizados-com-tmp_path)

### Identidade
Nome de 16 caracteres de uma execução: os primeiros caracteres hexadecimais do SHA-256 do JSON canônico da configuração resolvida e dos estágios. Mesmo cenário e mesmos estágios, mesma identidade.
_Evite_: run id, id da execução. Aula: [01-3](01-3-runner-e-manifesto.md#identidade-deterministica)

### JSON canônico
Serialização JSON sempre igual para o mesmo conteúdo: chaves ordenadas (`sort_keys=True`) e separadores compactos (`separators=(",", ":")`).
Aula: [01-3](01-3-runner-e-manifesto.md#identidade-deterministica)

### Manifesto
O `manifest.json` gravado na pasta da identidade: configuração resolvida, estágios, seed, horários, status, erro e ambiente da execução. É gravado mesmo quando a execução falha.
_Evite_: log da execução. Aula: [01-3](01-3-runner-e-manifesto.md#manifesto-autocontido)

### Estágio
Etapa nomeada do runner (`diagnostics`, `acquire`), escolhida com `--stage`. A lista aceita é `SUPPORTED_STAGES`.
_Evite_: passo, step. Aula: [01-3](01-3-runner-e-manifesto.md#interface-de-linha-de-comando-com-estagios-e-retomada)

### Retomada
Com `--resume`, reaproveitar o manifesto `completed` de uma identidade em vez de executá-la de novo.
Aula: [01-3](01-3-runner-e-manifesto.md#interface-de-linha-de-comando-com-estagios-e-retomada)

### Handle
Texto que identifica um recurso no Kaggle: `owner/slug` (Dataset) ou `owner/model/framework/variation` (Model). Para baixar de forma reproduzível, acrescenta-se a versão: `/versions/N` (Dataset) ou `/N` (Model).
_Evite_: URL do dataset, id. Aula: [02-1](02-1-handles-e-sha256.md#handle-versionado)

### Versão fixada
Handle de download com número de versão explícito. Aponta sempre para o mesmo conteúdo; o handle sem versão aponta para o mais recente e, por isso, é mutável.
Aula: [02-1](02-1-handles-e-sha256.md#handle-versionado)

### Integridade verificada
Prova local de que os bytes de um arquivo são os esperados, comparando o SHA-256 calculado com o valor registrado. Diferente de cache (existe um arquivo) e de transporte (o download terminou).
Aula: [02-1](02-1-handles-e-sha256.md#integridade-verificada-com-sha-256-em-streaming)

### SHA-256 em streaming
Cálculo do hash lendo o arquivo em blocos e chamando `update()` a cada um, com memória constante.
Aula: [02-1](02-1-handles-e-sha256.md#integridade-verificada-com-sha-256-em-streaming)

### Aquisição atômica
Baixar para uma pasta temporária vizinha, validar e só então promover o resultado ao destino por troca de nome, de modo que o destino nunca contenha um download parcial ou inválido.
_Evite_: download direto em `data/`. Aula: [02-2](02-2-aquisicao-atomica.md#aquisicao-atomica)

### Promoção
A troca de nome que faz a pasta temporária validada ocupar o lugar do destino (`Path.replace`). É atômica dentro do mesmo sistema de arquivos.
Aula: [02-2](02-2-aquisicao-atomica.md#passo-3-o-estagio-acquire_dataset)

### Proveniência
Registro, em `kaggle-provenance.json`, de onde os dados vieram e quais são: owner, slug, versão, DOI, licença, autores e nome, tamanho e SHA-256 de cada arquivo.
Aula: [02-2](02-2-aquisicao-atomica.md#reuso-por-proveniencia-verificada)

### Reuso verificado
Reaproveitar uma cópia local só quando o manifesto de proveniência coincide com o que se recalcula dos bytes presentes. Resultado marcado com `reused: true`.
Aula: [02-2](02-2-aquisicao-atomica.md#reuso-por-proveniencia-verificada)

### Placeholder
Pasta de dados que só contém subpastas e arquivos `.gitkeep`, usada para o Git versionar a estrutura vazia. A aquisição pode substituí-la; qualquer outro conteúdo ela protege.
Aula: [02-2](02-2-aquisicao-atomica.md#passo-3-o-estagio-acquire_dataset)

### Dublê de teste
Objeto que imita uma dependência externa (aqui, o KaggleHub) com o comportamento mínimo, injetado na costura `_kagglehub()` por `monkeypatch`.
_Evite_: mock genérico, stub. Aula: [02-2](02-2-aquisicao-atomica.md#duble-de-teste-para-a-rede)

### Pacote de modelo
Pasta com o modelo serializado (`.joblib`, `.pt` ou `.pth`), `metadata.json`, `manifest.json` e `sha256sums.txt`. É validado antes de qualquer upload.
Aula: [02-3](02-3-publicar-e-recuperar.md#pacote-de-modelo-verificavel)

### Registro de versão publicada
Gravar em `published_assets` do manifesto local o handle versionado de um ativo enviado ao Kaggle, depois de confirmar o número `N` (o upload não o devolve).
Aula: [02-3](02-3-publicar-e-recuperar.md#versoes-imutaveis-e-registro-do-handle-publicado)

### Subcomando
Comando de uma CLI que agrupa várias ações (`mqtt-kaggle-assets upload-model`, `download-dataset`...), criado com `add_subparsers` do `argparse`.
Aula: [02-3](02-3-publicar-e-recuperar.md#credenciais-fora-do-git-e-recursos-privados)

### MQTT
Protocolo de mensagens publicar/assinar para dispositivos pequenos: clientes publicam em tópicos e assinam tópicos por meio de um broker.
Aula: [03-1](03-1-mqtt-e-os-tres-ambientes.md#mqtt-publicar-assinar-e-pacotes-de-controle)

### Broker
O servidor MQTT que recebe as mensagens publicadas e as encaminha aos clientes cujas assinaturas casam com o tópico.
Aula: [03-1](03-1-mqtt-e-os-tres-ambientes.md#mqtt-publicar-assinar-e-pacotes-de-controle)

### Tópico
Nome hierárquico (`distance/ultrasonic`) em que uma mensagem é publicada e que as assinaturas usam para filtrar. O curinga `#` casa com vários níveis.
Aula: [03-1](03-1-mqtt-e-os-tres-ambientes.md#mqtt-publicar-assinar-e-pacotes-de-controle)

### Pacote de controle
Cada mensagem do protocolo MQTT, identificada por `mqtt.msgtype` de 1 a 14 (CONNECT, PUBLISH, SUBSCRIBE, PINGREQ, DISCONNECT...).
_Evite_: tipo de mensagem. Aula: [03-1](03-1-mqtt-e-os-tres-ambientes.md#mqtt-publicar-assinar-e-pacotes-de-controle)

### QoS
Garantia de entrega de um PUBLISH: 0 (no máximo uma vez), 1 (pelo menos uma) ou 2 (exatamente uma).
Aula: [03-1](03-1-mqtt-e-os-tres-ambientes.md#mqtt-publicar-assinar-e-pacotes-de-controle)

### Frame
Uma linha do CSV: um pacote capturado na rede, com ou sem camada MQTT. A unidade observada do projeto.
_Evite_: registro, amostra. Aula: [03-1](03-1-mqtt-e-os-tres-ambientes.md#camadas-e-missingness-estrutural)

### Ausência estrutural
Campo vazio porque não existe naquele frame (frame sem MQTT, ou campo que o tipo de pacote não tem), e não por falha de coleta. Não se imputa.
_Evite_: valor faltante aleatório. Aula: [03-1](03-1-mqtt-e-os-tres-ambientes.md#camadas-e-missingness-estrutural)

### Ambiente de ataque
Um dos três arquivos: o mesmo laboratório MQTT sob um ataque diferente (`DoS.csv`, `MitM.csv`, `Intrusion.csv`). Cada um é um problema de classificação binária separado.
Aula: [03-1](03-1-mqtt-e-os-tres-ambientes.md#tres-arquivos-tres-ambientes-tres-ataques)

### Leitura verificada
Abrir um CSV só depois de conferir o SHA-256 dos bytes contra o valor esperado (`load_raw`).
Aula: [03-2](03-2-carga-segura-e-contrato.md#leitura-verificada)

### Contrato de contagens
Conjunto de fatos numéricos que identifica uma versão dos dados: linhas, colunas, classes, rótulos e duplicatas. Divergências com a fonte são documentadas, nunca corrigidas no raw.
Aula: [03-2](03-2-carga-segura-e-contrato.md#contrato-de-contagens)

### Duplicata exata
Linha idêntica, em todas as colunas, a uma anterior. Nos três ambientes equivale a um frame repetido (mesmo `frame.number` em mais de uma linha).
Aula: [03-2](03-2-carga-segura-e-contrato.md#duplicata-exata-e-frame-repetido)

### Raw imutável
Regra de que o dado bruto nunca é editado: toda transformação gera cópias derivadas, e a exploração prova que conteúdo e `mtime` não mudaram.
Aula: [03-2](03-2-carga-segura-e-contrato.md#raw-imutavel)

### Fixture
Função de preparação marcada com `@pytest.fixture` que o pytest entrega a um teste pelo nome do parâmetro.
Aula: [03-2](03-2-carga-segura-e-contrato.md#testando)

### Perfil de colunas
Tabela com tipo, percentual de ausência, cardinalidade e alertas (vazia, constante, quase constante, flag de presença) de cada coluna (`column_profile`).
Aula: [03-3](03-3-missingness-e-dicionario.md#passo-1-o-perfil-de-cada-coluna)

### Coluna vazia
Coluna 100% ausente no ambiente. Não carrega informação e entra na política como `excluded`.
Aula: [03-3](03-3-missingness-e-dicionario.md#vazia-constante-quase-constante-e-flag-de-presenca)

### Coluna constante
Coluna com um único estado (sem ausência). Não separa as classes e é excluída (nos três ambientes: `frame.encap_type`, `frame.ignored`, `frame.marked`, `frame.offset_shift`).
Aula: [03-3](03-3-missingness-e-dicionario.md#vazia-constante-quase-constante-e-flag-de-presenca)

### Flag de presença
Coluna com um único valor quando presente e ausente no resto: o que informa é estar ou não presente (por exemplo, ser um CONNECT). Não confundir com constante.
Aula: [03-3](03-3-missingness-e-dicionario.md#vazia-constante-quase-constante-e-flag-de-presenca)

### Quase constante
Coluna em que um único estado cobre 99% ou mais das linhas, sem ser flag de presença. Pede investigação antes de descartar.
Aula: [03-3](03-3-missingness-e-dicionario.md#vazia-constante-quase-constante-e-flag-de-presenca)

### Rajada
Sequência contígua de frames da mesma classe, na ordem de captura. O DoS tem três rajadas de ataque; MitM e Intrusion têm centenas de rajadas curtas.
Aula: [03-4](03-4-dos-inundacao.md#rajadas-a-classe-ao-longo-do-tempo)

### Taxa de frames
Número de frames por segundo de captura (`frames_per_second`), contado só nos segundos com tráfego. Não confundir com o intervalo entre frames (`frame.time_delta`).
Aula: [03-4](03-4-dos-inundacao.md#taxa-de-frames-o-que-a-inundacao-muda)

### Assinatura do ataque
Conjunto de medidas que distinguem um ataque do tráfego normal num ambiente (tipo de pacote, QoS, tamanho, tópicos, taxa). Cada medida é pista e, ao mesmo tempo, risco de identificar o laboratório em vez do comportamento.
Aula: [03-4](03-4-dos-inundacao.md#anatomia-de-um-ataque-de-inundacao)

### Backend Agg
Backend do Matplotlib que só escreve imagens em arquivo, sem janela; permite gerar figuras no terminal, em testes e no runner.
Aula: [03-4](03-4-dos-inundacao.md#passo-4-a-figura-da-linha-do-tempo)

### ARP
Protocolo da rede local que descobre o endereço físico (MAC) de um IP, por broadcast, sem autenticação (RFC 826). Não tem campos próprios nos CSVs: um frame ARP aparece sem IP, TCP e MQTT.
Aula: [03-5](03-5-mitm-trafego-alterado.md#arp-spoofing-o-homem-no-meio-na-rede-local)

### ARP spoofing
Ataque em que o invasor anuncia respostas ARP falsas para ficar entre dois aparelhos (homem no meio), retransmitindo e podendo alterar o tráfego. É o ataque do ambiente MitM.
_Evite_: ARP poisoning (use só como sinônimo, ao citar o MITRE). Aula: [03-5](03-5-mitm-trafego-alterado.md#arp-spoofing-o-homem-no-meio-na-rede-local)

### Broadcast
Frame Ethernet endereçado a todos (`eth.dst` = `ff:ff:ff:ff:ff:ff`). No MitM são 80% dos frames de ataque e 0,07% dos normais.
Aula: [03-5](03-5-mitm-trafego-alterado.md#passo-3-os-enderecos-ethernet-o-que-o-spoofing-mostra)

### MAC compartilhado
Endereço físico que aparece nas duas classes: sob spoofing o MAC do atacante também origina tráfego normal, então não identifica o ataque.
Aula: [03-5](03-5-mitm-trafego-alterado.md#identidade-em-duas-camadas-e-mac-compartilhado)

### Sessão MQTT
Período entre o CONNECT e o DISCONNECT de um cliente. No Intrusion, cada rajada de ataque é uma sessão curta: conecta, publica uma mensagem falsa e desconecta.
Aula: [03-6](03-6-intrusion-cliente-desconhecido.md#sessao-mqtt-e-client-id)

### Client ID
Nome que o cliente envia no CONNECT (`mqtt.clientid`). Se já houver um cliente conectado com o mesmo Client ID, o broker desconecta o existente.
Aula: [03-6](03-6-intrusion-cliente-desconhecido.md#sessao-mqtt-e-client-id)

### Assinatura da sessão
Sequência de tipos de pacote de uma rajada, com repetições consecutivas colapsadas (`burst_signatures`). Mostra o padrão de um ataque que é um evento, não um frame.
Aula: [03-6](03-6-intrusion-cliente-desconhecido.md#o-ataque-como-evento-a-assinatura-da-sessao)

### Mimetismo
Reaproveitamento, pelo ataque, de identidades e conteúdo do tráfego legítimo (Client IDs, tópicos, IPs, valores plausíveis). Reduz o poder de separação desses atributos.
Aula: [03-6](03-6-intrusion-cliente-desconhecido.md#mimetismo-identidades-e-conteudo-copiados-do-legitimo)

### Vazamento
Uso, na construção ou avaliação de um modelo, de informação que não estaria disponível em produção, o que produz métricas otimistas. No projeto vem de identidade, conteúdo e ordem/repetição.
_Evite_: contaminação. Aula: [03-7](03-7-vazamento-identidade-conteudo-ordem.md#vazamento-quando-o-teste-deixa-de-ser-teste)

### Classificador de tabela
Modelo trivial que memoriza, para cada valor de uma coluna, a fração de ataque vista no treino (`lookup_scores`). Serve de termômetro: se uma coluna sozinha dá F1 alto, ela carrega identidade ou conteúdo do cenário.
Aula: [03-7](03-7-vazamento-identidade-conteudo-ordem.md#o-classificador-de-tabela-um-termometro-de-vazamento)

### Divisão temporal
Treino nos primeiros 70% da captura e teste nos últimos 30% (`temporal_split`). Contrasta com a divisão aleatória, otimista quando há rajadas e repetições.
Aula: [03-7](03-7-vazamento-identidade-conteudo-ordem.md#divisao-aleatoria-divisao-temporal)

### Autocorrelação do rótulo
Tendência de um frame ter a mesma classe do vizinho (`neighbor_agreement`: 99,4% a 99,99% nos três ambientes).
Aula: [03-7](03-7-vazamento-identidade-conteudo-ordem.md#passo-3-a-ordem-importa)

### Reaparecimento de identidade
Fração dos valores do holdout que já tinham aparecido no desenvolvimento (`identity_reappearance`): o MAC reaparece em 100% nos três ambientes.
Aula: [03-7](03-7-vazamento-identidade-conteudo-ordem.md#passo-3-a-ordem-importa)

### Estágio audit
Terceiro estágio do runner (`--stage audit`): lê os três CSVs verificados, grava 12 tabelas e 3 figuras em `results/` e registra no manifesto o hash de cada entrada e de cada saída.
Aula: [03-8](03-8-estagio-audit.md#passo-1-o-estagio)

### Artefato ligado à entrada
Tabela ou figura cujo hash, junto com o hash do CSV de origem, consta no manifesto da execução que a gerou.
Aula: [03-8](03-8-estagio-audit.md#artefatos-ligados-a-entrada)

### Derivação mínima
Propriedade generalizável que substitui uma identidade crua: `direction` (privado/público) no lugar do IP, `broadcast` no lugar do MAC, `has_mqtt` no lugar do tópico.
Aula: [03-9](03-9-politica-de-features-e-modelagem.md#derivacao-minima-comportamento-em-vez-de-identidade)

### Política de features
Classificação de cada coluna em `portable`, `derivable`, `ablation_only` ou `excluded`, aqui acompanhada da evidência de cada grupo (aulas 03-1 a 03-9).
Aula: [03-9](03-9-politica-de-features-e-modelagem.md#a-politica-de-features-com-evidencia)

### Matriz de transferência
Tabela de F1 treinando em um ambiente (linha) e testando em outro (coluna) com o classificador de tabela. Fora da diagonal quase tudo cai a zero.
Aula: [03-9](03-9-politica-de-features-e-modelagem.md#passo-3-o-que-transfere-entre-ambientes)

### Bloco de validação
Janela de tempo (10, 30 ou 60 s) usada como grupo na validação cruzada agrupada. O número de blocos com ataque no desenvolvimento limita quantos folds são viáveis.
Aula: [03-9](03-9-politica-de-features-e-modelagem.md#passo-4-blocos-de-validacao)
