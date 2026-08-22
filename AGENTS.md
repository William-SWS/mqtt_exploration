# Repository Guidelines

## Project Structure & Module Organization

This documentation-first MQTT intrusion-detection project keeps the PRD, decisions, and issue drafts in `docs/`. Future reusable Python logic belongs in `src/mqtt_ids/`. Use `scripts/` for thin entrypoints, `configs/` for YAML scenarios, and `notebooks/` for exploration only. Place tests in `tests/`, mirroring package modules where practical. Generated content in `data/`, `artifacts/`, and `results/` is ignored by Git.

## Build, Test, and Development Commands

No executable Python project exists yet: there is no `pyproject.toml`, lockfile, or test suite. The first implementation uses Python 3.12 and `uv`, per [`docs/issues/01-project-runner.md`](docs/issues/01-project-runner.md). Once initialized, use:

```bash
uv sync --locked       # install the exact locked environment
uv run pytest          # run the test suite
uv run ruff check .    # lint
uv run ruff format .   # format
```

Document any additional runner command in `README.md` when it is introduced.

## Coding Style & Naming Conventions

Write documentation and user-facing explanations in PT-BR; use English for Python modules, APIs, configuration keys, functions, and tests. Follow four-space Python indentation. Prefer `snake_case` for files, functions, variables, and YAML keys; `PascalCase` for classes; and clear, domain-specific names such as `temporal_split.py` or `test_data_contract.py`. Use Ruff for formatting and linting once tooling is added. Keep scripts small: they may call library functions but must not launch other scripts with `subprocess`.

## Testing Guidelines

Use `pytest` and name files `test_*.py` and tests `test_<behavior>`. Add focused tests for data contracts, temporal-split isolation, configuration validation, and deterministic manifests. Keep raw data immutable; tests should use fixtures and `tmp_path`, never depend on local datasets, credentials, or generated artifacts. Fit preprocessing, resampling, and supervised selection only inside training folds to prevent leakage.

## Commit & Pull Request Guidelines

Recent history uses short imperative subjects and occasional conventional prefixes, for example `docs: establish MQTT IDS learning path`. Keep commits narrow and use a prefix where useful (`docs:`, `feat:`, `test:`). Pull requests should explain the change, reference the relevant issue draft or issue, list validation commands run, and include screenshots only for visual output. Do not commit datasets, secrets, model files, databases, or result artifacts.

## Decision and Configuration Safety

`docs/DECISIONS.md` need to be updated manually or automaticaly for future report creation or presentations: supersede a decision with a new ADR rather than editing history. Load YAML with `safe_load`, validate it before execution, and keep Kaggle tokens and other credentials outside the repository.
