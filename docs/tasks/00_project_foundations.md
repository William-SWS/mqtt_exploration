# Task 00 — Fundamentos do projeto

## Objetivo

Transformar, em uma etapa futura, este esqueleto documental em um pacote Python 3.12 reproduzível, gerenciado por uv e organizado no layout `src`, sem misturar lógica reutilizável com scripts ou notebooks.

## Pré-requisitos

- Ler o README e as ADR-001, ADR-002, ADR-003 e ADR-016.
- Ter Git e uv instalados; não executar esta tarefa durante a entrega documental inicial.
- Entender a diferença entre dependência de execução, desenvolvimento e ambiente local.

## Conceitos e APIs para estudar

- `uv init --package --python 3.12`, `uv add`, grupos de dependências, `uv lock`, `uv sync --frozen` e `uv run`.
- Arquivos `pyproject.toml`, `uv.lock` e `.python-version`; lockfile versus ambiente `.venv`.
- Layout `src`, imports de pacote, entrypoints pequenos e testes fora do pacote.
- Commits atômicos, status/diff do Git e padrões de `.gitignore`.

> Nota atual de API: `uv add` atualiza projeto, lock e ambiente; `uv lock` resolve o lockfile; `uv sync --frozen` deve consumir o lock existente sem atualizá-lo. Confirmar novamente na documentação oficial ao executar.

## Exercício a implementar futuramente

Inicializar o projeto na raiz existente, adaptar o pacote gerado para `src/mqtt_ids`, declarar Python 3.12 e separar dependências de runtime das ferramentas de notebook, qualidade e teste. Criar comandos mínimos para verificar importação e testes, sem implementar o IDS.

## Entregáveis

- `pyproject.toml`, `.python-version` e `uv.lock` revisados.
- Pacote importável `mqtt_ids` e configuração de testes/qualidade.
- README atualizado com comandos exatos e política de atualização do lockfile.

## Testes esperados

- `uv sync --frozen` funciona a partir de clone limpo.
- `uv run python -c "import mqtt_ids"` termina com sucesso.
- `uv run pytest` encontra a suíte sem depender do diretório de execução.
- `.venv`, caches, dados e credenciais permanecem não rastreados.

## Critérios de aceite

- Python 3.12 está explicitamente restringido.
- O lockfile é versionado e o ambiente não é.
- Nenhum notebook contém lógica necessária à execução do pipeline.
- Uma máquina limpa reproduz o ambiente usando apenas os arquivos versionados.

## Perguntas de reflexão

- Que garantia `--frozen` oferece em CI que um `uv sync` comum não oferece?
- Por que o layout `src` revela imports acidentais com mais facilidade?
- Quais dependências pertencem ao runtime e quais só servem ao desenvolvimento?

## Decisões que devem ser registradas

Registrar versão mínima/máxima do Python, versão do uv adotada, grupos de dependências, ferramentas de qualidade e qualquer desvio do layout ou dos comandos propostos.
