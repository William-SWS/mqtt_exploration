# Inicializar o projeto reproduzível e o runner mínimo

## What to build

Criar o primeiro caminho executável do produto: um projeto Python 3.12 reproduzível que aceite um cenário YAML, valide a estrutura mínima, execute um estágio de diagnóstico e produza um manifesto com identidade, configuração resolvida, versões, seed e status. O comando deve aceitar seleção de estágios e retomada, mesmo que inicialmente exista apenas o estágio de diagnóstico.

## What to study

- Projetos e dependency groups do uv; diferenças entre lock, `--locked` e `--frozen`.
- Layout `src`, imports de pacote e separação entre biblioteca e entrypoint.
- YAML seguro, configuração resolvida, canonicalização e hashing determinístico.
- Testes de CLI por comportamento e commits atômicos.

## Recommended tools and libraries

- uv para Python, ambientes, grupos e lockfile.
- PyYAML para leitura com `safe_load`.
- pytest 9 para fixtures, `tmp_path`, parametrização e captura de logs.
- Ruff para lint e formatação; `importlib.metadata` para versões instaladas.

## Acceptance criteria

- [x] Um checkout limpo sincroniza o ambiente a partir do lockfile sem resolver versões novas.
- [x] O pacote é importável fora da raiz do projeto.
- [x] O runner aceita cenário, estágios e retomada e executa um diagnóstico verificável.
- [x] Configuração ausente, desconhecida ou inválida falha antes de executar qualquer estágio.
- [x] Uma execução concluída ou falha produz manifesto autocontido e identidade determinística.
- [x] O teste end-to-end usa diretório temporário e verifica comportamento externo do comando.
- [x] Dados, credenciais, ambientes, bancos e artefatos grandes permanecem fora do Git.

## Blocked by

None - can start immediately.

## User stories covered

1–9 e fundação de 101–104.
