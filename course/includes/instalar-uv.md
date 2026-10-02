O `uv` instala o Python e as bibliotecas do projeto num ambiente isolado.

=== "Linux / macOS"

    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

=== "Windows"

    ```powershell
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    ```

Depois de instalar, abra um terminal novo e confira com `uv --version`.
