# Gerar a auditoria exploratória e o dicionário de dados

## What to build

Adicionar um estágio de auditoria que leia a entrada verificada, produza um dicionário cobrindo todas as colunas e gere tabelas/figuras sobre tipos, missingness, cardinalidade, duplicatas, classes, tempo e associação de identificadores com o alvo. Fornecer também um notebook narrativo que consuma as mesmas funções e não contenha lógica exclusiva.

## What to study

- EDA orientada a riscos: desbalanceamento, colunas vazias/constantes e cardinalidade.
- Vazamento por identidade, tempo, ordem e cenário de captura.
- Associação categórica com classe sem confundir correlação com generalização.
- Boas práticas de notebooks reiniciáveis e figuras reproduzíveis.

## Recommended tools and libraries

- pandas para perfil estrutural, agregações, duplicatas e crosstabs.
- JupyterLab para narrativa; Matplotlib e Seaborn para visualização.
- SciPy apenas quando um teste estatístico acrescentar evidência interpretável.
- pytest para contratos de contagem e imutabilidade do raw.

## Acceptance criteria

- [ ] A auditoria confirma ou explica divergências de 80.893 linhas, 67 colunas, 1.898 intrusões e 30 duplicatas.
- [ ] Toda coluna aparece exatamente uma vez no dicionário com tipo, missingness, cardinalidade e política preliminar.
- [ ] Colunas totalmente vazias, constantes e identificadoras são explicitamente sinalizadas.
- [ ] Há evidência tabular ou visual do risco por IP, MAC, client ID, tópico, payload e ordem.
- [ ] O notebook executa do início ao fim a partir dos artefatos do estágio.
- [ ] Nenhuma execução altera conteúdo, hash ou mtime do raw.
- [ ] O manifesto liga tabelas e figuras ao hash da entrada.

## Blocked by

- {{ISSUE_02}}

## User stories covered

16–21.
