# Dicionário de dados do MQTT_UAD

Este documento descreve as 67 colunas comuns a `DoS.csv`, `MitM.csv` e
`Intrusion.csv`. As descrições e os tipos semânticos vêm das Tabelas 1-3 do
artigo *MQTT_UAD: MQTT Under Attack Dataset*; as cinco colunas ausentes dessas
tabelas foram completadas pela referência oficial de filtros do Wireshark.
Tipos, percentuais de ausência, cardinalidades e rótulos foram medidos
diretamente nos CSVs locais, cujos hashes coincidem com os registrados no
projeto.

## Como ler

- **Origem:** `P` = artigo, `W` = referência oficial do Wireshark.
- **Ausentes D/M/I:** percentual de valores ausentes em DoS, MitM e Intrusion.
- **Card. D/M/I:** cardinalidade sem contar ausentes, na mesma ordem.
- **Política preliminar:** `portable` pode ser candidata à matriz principal;
  `derivable` deve originar somente uma derivação generalizável;
  `ablation_only` fica disponível para auditoria de vazamento ou ablação;
  `excluded` não deve entrar como feature.
- `float64` em vários campos inteiros ou booleanos é consequência da presença
  de `NaN`, não uma redefinição do tipo semântico.

## Campos comuns a todos os frames

| Variável | Significado | Tipo semântico | Origem | dtype observado | Ausentes D/M/I | Card. D/M/I | Política preliminar |
|---|---|---|:---:|---|---:|---:|---|
| `frame.time_delta` | Tempo desde o frame capturado imediatamente anterior. | deslocamento de tempo | P | `float64` | 0/0/0% | 9884/23602/22921 | `portable` |
| `frame.time_delta_displayed` | Tempo desde o frame anterior que passou pelo filtro de exibição. | deslocamento de tempo | P | `float64` | 0/0/0% | 9884/23602/22921 | `portable` (avaliar redundância) |
| `frame.time_epoch` | Instante de chegada absoluto, representado em segundos desde o Unix epoch no CSV. | data e hora | W | `float64` | 0/0/0% | 62327/110631/80863 | `ablation_only` (tempo absoluto) |
| `frame.time_invalid` | Sinaliza timestamp de chegada com fração de segundo fora do intervalo válido. | rótulo | P | `float64` | 100/100/100% | 0/0/0 | `excluded` (vazia) |
| `frame.time_relative` | Tempo desde o frame de referência ou primeiro frame da captura. | deslocamento de tempo | P | `float64` | 0/0/0% | 62327/110631/80863 | `ablation_only` (proxy de ordem) |
| `ip.src` | Endereço IPv4 de origem. Ausente em frames sem IPv4. | endereço IPv4 | P | `str` | 1,09/7,44/4,68% | 181/241/440 | `derivable` (direção/escopo; nunca IP cru) |
| `ip.dst` | Endereço IPv4 de destino. Ausente em frames sem IPv4. | endereço IPv4 | P | `str` | 1,09/7,44/4,68% | 191/253/446 | `derivable` (direção/escopo; nunca IP cru) |
| `tcp.srcport` | Porta TCP de origem. Ausente em frames que não usam TCP. | inteiro sem sinal de 16 bits | P | `float64` | 6,52/10,08/11,29% | 1236/857/1809 | `derivable` (papel/porta MQTT; evitar porta efêmera crua) |
| `tcp.dstport` | Porta TCP de destino. Ausente em frames que não usam TCP. | inteiro sem sinal de 16 bits | P | `float64` | 6,52/10,08/11,29% | 1231/808/1719 | `derivable` (papel/porta MQTT; evitar porta efêmera crua) |
| `eth.src` | Endereço MAC de origem. | endereço MAC | P | `str` | 0/0/0% | 9/10/7 | `derivable` (direção/fabricante; nunca MAC cru) |
| `eth.dst` | Endereço MAC de destino. | endereço MAC | P | `str` | 0/0/0% | 36/49/24 | `derivable` (direção/fabricante; nunca MAC cru) |
| `frame.cap_len` | Número de bytes do frame efetivamente capturados. | inteiro sem sinal de 32 bits | P | `int64` | 0/0/0% | 1292/1265/1356 | `portable` |
| `frame.coloring_rule.name` | Nome da regra de coloração aplicada pelo Wireshark. | texto | P | `float64` | 100/100/100% | 0/0/0 | `excluded` (vazia e metadado de análise) |
| `frame.coloring_rule.string` | Expressão da regra de coloração aplicada pelo Wireshark. | texto | P | `float64` | 100/100/100% | 0/0/0 | `excluded` (vazia e metadado de análise) |
| `frame.comment` | Comentário associado ao frame. | texto | P | `float64` | 100/100/100% | 0/0/0 | `excluded` (vazia e metadado de captura) |
| `frame.comment.expert` | Comentário formatado do mecanismo expert do Wireshark. | rótulo | P | `float64` | 100/100/100% | 0/0/0 | `excluded` (vazia e metadado de análise) |
| `frame.encap_type` | Tipo de encapsulamento do arquivo de captura. | inteiro com sinal de 16 bits | P | `int64` | 0/0/0% | 1/1/1 | `excluded` (constante e metadado de captura) |
| `frame.file_off` | Deslocamento em bytes do frame dentro do arquivo de captura. | inteiro com sinal de 64 bits | P | `float64` | 100/100/100% | 0/0/0 | `excluded` (vazia e metadado de arquivo) |
| `frame.ignored` | Indica se o frame foi marcado para ser ignorado no Wireshark. | booleano | P | `int64` | 0/0/0% | 1/1/1 | `excluded` (constante e metadado de análise) |
| `frame.incomplete` | Indica dissecção incompleta do frame. | rótulo | P | `float64` | 100/100/100% | 0/0/0 | `excluded` (vazia) |
| `frame.interface_id` | Identificador da interface de captura. | inteiro sem sinal de 32 bits | P | `float64` | 100/100/100% | 0/0/0 | `excluded` (vazia e metadado de captura) |
| `frame.interface_name` | Nome da interface de captura. | texto | P | `float64` | 100/100/100% | 0/0/0 | `excluded` (vazia e metadado de captura) |
| `frame.len` | Comprimento original do frame no meio físico, em bytes. | inteiro sem sinal de 32 bits | P | `int64` | 0/0/0% | 1292/1265/1356 | `portable` |
| `frame.link_nr` | Número do enlace no arquivo de captura. | inteiro sem sinal de 16 bits | P | `float64` | 100/100/100% | 0/0/0 | `excluded` (vazia e metadado de captura) |
| `frame.marked` | Indica se o frame foi marcado manualmente no Wireshark. | booleano | W | `int64` | 0/0/0% | 1/1/1 | `excluded` (constante e metadado de análise) |
| `frame.md5_hash` | Hash MD5 calculado sobre o frame. | texto | W | `float64` | 100/100/100% | 0/0/0 | `excluded` (vazia; identificador de conteúdo) |
| `frame.number` | Número sequencial do frame na captura. | inteiro sem sinal de 32 bits | W | `int64` | 0/0/0% | 62327/110631/80863 | `ablation_only` (proxy de ordem/cenário) |
| `frame.offset_shift` | Ajuste temporal aplicado ao timestamp do frame. | deslocamento de tempo | W | `float64` | 0/0/0% | 1/1/1 | `excluded` (constante e metadado de captura) |

## Campos do protocolo MQTT

Esses campos só são preenchidos quando o frame contém a estrutura MQTT
correspondente. Portanto, a ausência geralmente significa “não aplicável ao
tipo de pacote”, e não necessariamente erro de coleta.

| Variável | Significado | Tipo semântico | Origem | dtype observado | Ausentes D/M/I | Card. D/M/I | Política preliminar |
|---|---|---|:---:|---|---:|---:|---|
| `mqtt.clientid` | Identificador do cliente enviado no CONNECT. | texto | P | `str` | 99,66/100/99,65% | 320/1/33 | `ablation_only` (identidade crua) |
| `mqtt.clientid_len` | Comprimento do identificador do cliente. | inteiro sem sinal de 16 bits | P | `float64` | 99,66/100/99,65% | 6/1/10 | `portable` |
| `mqtt.conack.flags` | Byte de flags do CONNACK, exportado como hexadecimal. | inteiro sem sinal de 8 bits | P | `str` | 99,19/99,99/99,91% | 9/1/1 | `portable` (validar domínio) |
| `mqtt.conack.flags.reserved` | Bits reservados do CONNACK. | booleano | P | `float64` | 99,19/99,99/99,65% | 2/1/1 | `portable` |
| `mqtt.conack.flags.sp` | Flag Session Present do CONNACK. | booleano | P | `float64` | 99,19/99,99/99,91% | 2/1/1 | `portable` |
| `mqtt.conack.val` | Código de retorno do CONNACK. | inteiro sem sinal de 8 bits | P | `float64` | 99,19/99,99/99,65% | 12/1/1 | `portable` (validar valores malformados) |
| `mqtt.conflag.cleansess` | Flag Clean Session do CONNECT. | booleano | P | `float64` | 99,66/100/99,65% | 1/1/1 | `portable` |
| `mqtt.conflag.passwd` | Indica presença de senha no CONNECT. | booleano | P | `float64` | 99,66/100/99,65% | 1/1/1 | `portable` |
| `mqtt.conflag.qos` | Nível de QoS da mensagem Will no CONNECT. | inteiro sem sinal de 8 bits | P | `float64` | 99,66/100/99,65% | 1/1/1 | `portable` |
| `mqtt.conflag.reserved` | Bit reservado das flags do CONNECT. | booleano | P | `float64` | 99,66/100/99,65% | 1/1/1 | `portable` |
| `mqtt.conflag.retain` | Flag Will Retain do CONNECT. | booleano | P | `float64` | 99,66/100/99,65% | 1/1/1 | `portable` |
| `mqtt.conflag.uname` | Indica presença de nome de usuário no CONNECT. | booleano | P | `float64` | 99,66/100/99,65% | 1/1/1 | `portable` |
| `mqtt.conflag.willflag` | Indica presença de mensagem Will no CONNECT. | booleano | P | `float64` | 99,66/100/99,65% | 1/1/1 | `portable` |
| `mqtt.conflags` | Byte agregado de flags do CONNECT, exportado como hexadecimal. | inteiro sem sinal de 8 bits | P | `str` | 99,66/100/99,65% | 1/1/1 | `portable` (avaliar redundância com flags abertas) |
| `mqtt.dupflag` | Flag DUP: mensagem PUBLISH possivelmente retransmitida. | booleano | P | `float64` | 59,35/98,16/97,49% | 2/1/1 | `portable` |
| `mqtt.hdrflags` | Nibble de flags do cabeçalho fixo MQTT, exportado como hexadecimal. | inteiro sem sinal de 8 bits | P | `str` | 58,22/96,73/94,04% | 35/5/8 | `portable` (validar combinações malformadas) |
| `mqtt.kalive` | Intervalo Keep Alive do CONNECT, em segundos. | inteiro sem sinal de 16 bits | P | `float64` | 99,66/100/99,65% | 2/1/2 | `portable` |
| `mqtt.len` | Remaining Length da mensagem MQTT. | inteiro sem sinal de 64 bits | P | `float64` | 58,22/96,73/94,04% | 76/7/16 | `portable` |
| `mqtt.msg` | Conteúdo da mensagem/payload MQTT. | texto | P | `str` ou `float64` | 60,12/98,16/97,50% | 5948/71/77 | `ablation_only` (conteúdo cru e risco de vazamento) |
| `mqtt.msgid` | Identificador de pacote MQTT quando aplicável. | inteiro sem sinal de 16 bits | P | `float64` | 99,16/100/99,94% | 47/0/2 | `portable` (avaliar comportamento sequencial) |
| `mqtt.msgtype` | Tipo de pacote MQTT codificado no cabeçalho (CONNECT, PUBLISH etc.). | inteiro sem sinal de 8 bits | P | `float64` | 58,22/96,73/94,04% | 12/5/8 | `portable` |
| `mqtt.passwd` | Senha transportada no CONNECT. | texto | P | `float64` | 100/100/100% | 0/0/0 | `excluded` (vazia; segredo/conteúdo) |
| `mqtt.passwd_len` | Comprimento da senha do CONNECT. | inteiro sem sinal de 16 bits | P | `float64` | 100/100/100% | 0/0/0 | `excluded` (vazia) |
| `mqtt.proto_len` | Comprimento do nome do protocolo no CONNECT. | inteiro sem sinal de 16 bits | P | `float64` | 99,66/100/99,65% | 1/1/2 | `portable` |
| `mqtt.protoname` | Nome do protocolo no CONNECT (`MQTT` ou legado `MQIsdp`). | texto | P | `str` | 99,66/100/99,65% | 1/1/2 | `portable` |
| `mqtt.qos` | Nível de QoS do PUBLISH. | inteiro sem sinal de 8 bits | P | `float64` | 59,35/98,16/97,49% | 4/1/2 | `portable` (valor 3 é reservado e requer auditoria) |
| `mqtt.retain` | Flag RETAIN do PUBLISH. | booleano | P | `float64` | 59,35/98,16/97,50% | 2/1/1 | `portable` |
| `mqtt.sub.qos` | QoS solicitado em uma assinatura SUBSCRIBE. | inteiro sem sinal de 8 bits | P | `float64` | 100/100/99,97% | 1/0/1 | `portable` |
| `mqtt.suback.qos` | QoS concedido em um SUBACK. | inteiro sem sinal de 8 bits | P | `float64` | 100/100/99,97% | 1/0/1 | `portable` |
| `mqtt.topic` | Nome do tópico MQTT. | texto | P | `str` | 60,12/98,16/97,47% | 5904/3/4 | `ablation_only` (conteúdo/identidade do cenário) |
| `mqtt.topic_len` | Comprimento do tópico MQTT. | inteiro sem sinal de 16 bits | P | `float64` | 59,35/98,16/97,47% | 60/3/4 | `portable` |
| `mqtt.username` | Nome de usuário transportado no CONNECT. | texto | P | `float64` | 100/100/100% | 0/0/0 | `excluded` (vazia; identidade) |
| `mqtt.username_len` | Comprimento do nome de usuário do CONNECT. | inteiro sem sinal de 16 bits | P | `float64` | 100/100/100% | 0/0/0 | `excluded` (vazia) |
| `mqtt.ver` | Nível de versão do protocolo MQTT (`3` ou `4` nos CSVs). | inteiro sem sinal de 8 bits | P | `float64` | 99,66/100/99,65% | 1/1/2 | `portable` |
| `mqtt.willmsg` | Conteúdo da mensagem Will do CONNECT. | texto | P | `float64` | 100/100/100% | 0/0/0 | `excluded` (vazia; conteúdo) |
| `mqtt.willmsg_len` | Comprimento da mensagem Will. | inteiro sem sinal de 16 bits | P | `float64` | 100/100/100% | 0/0/0 | `excluded` (vazia) |
| `mqtt.willtopic` | Tópico da mensagem Will. | texto | P | `float64` | 100/100/100% | 0/0/0 | `excluded` (vazia; conteúdo) |
| `mqtt.willtopic_len` | Comprimento do tópico da mensagem Will. | inteiro sem sinal de 16 bits | P | `float64` | 100/100/100% | 0/0/0 | `excluded` (vazia) |

## Alvo

| Variável | Significado | Tipo semântico | Origem | dtype observado | Ausentes D/M/I | Card. D/M/I | Política preliminar |
|---|---|---|:---:|---|---:|---:|---|
| `type` | Classe atribuída ao frame: tráfego normal ou ataque do cenário do arquivo. | categórico | P | `str` | 0/0/0% | 2/2/2 | `excluded` da matriz; é o alvo |

Valores efetivamente observados:

| Arquivo | Classes e contagens observadas |
|---|---|
| `DoS.csv` | `normal`: 49.111; `DoS`: 45.514 |
| `MitM.csv` | `normal`: 106.813; `mitm`: 3.855 |
| `Intrusion.csv` | `normal`: 78.995; `intrusion`: 1.898 |

## Inconsistências e cuidados de interpretação

1. O artigo afirma que todos os arquivos têm 67 campos, mas suas Tabelas 1-3
   enumeram apenas 62. Os cinco campos faltantes são `frame.time_epoch`,
   `frame.marked`, `frame.md5_hash`, `frame.number` e `frame.offset_shift`.
2. A Tabela 3 escreve o rótulo como `MitM`; o valor real em `MitM.csv` é
   `mitm`. O contrato deve respeitar a capitalização observada ou normalizá-la
   explicitamente em etapa posterior.
3. O artigo informa 45.513 frames `DoS` e 49.112 `normal`; o CSV verificado tem
   45.514 e 49.111, respectivamente. O total permanece 94.625.
4. Valores semanticamente inválidos ou reservados aparecem sobretudo no
   cenário DoS, por exemplo QoS 3 e combinações incomuns de flags. Eles podem
   representar tráfego malformado do ataque e não devem ser corrigidos sem uma
   regra de contrato sustentada por evidência.
5. Missingness em campos MQTT frequentemente é estrutural: o campo não existe
   naquele tipo de pacote ou o frame não contém MQTT. Imputar esses valores como
   se fossem falhas aleatórias destruiria informação protocolar.

## Fontes

- J. Aveleira-Mata et al., *MQTT_UAD: MQTT Under Attack Dataset. A public
  dataset for the detection of attacks in IoT networks using MQTT protocol*,
  Data in Brief 63 (2025), 112167, DOI: 10.1016/j.dib.2025.112167. Cópia local:
  `data/mqtt_under_atack_paper.pdf`.
- [Wireshark Display Filter Reference: Frame](https://www.wireshark.org/docs/dfref/f/frame.html),
  usada para os cinco campos presentes nos CSVs e ausentes da Tabela 1.

