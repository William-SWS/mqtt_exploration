Na pasta do projeto, rode a suíte inteira:

```bash title="$ Execução no terminal (na pasta do projeto)"
uv run --locked pytest
```

Para rodar só um arquivo, passe o caminho: `uv run --locked pytest tests/test_config.py`. O `--locked` garante que o ambiente segue o `uv.lock` sem resolver versões novas.
