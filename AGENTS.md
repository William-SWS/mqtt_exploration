# Agent Instructions

## Package Manager

- Use `uv`; preserve `uv.lock`.
- Setup: `uv sync --locked --all-groups`.
- Execute project commands with `uv run --locked`.

## File-Scoped Commands

| Task | Command |
| --- | --- |
| Test runner | `uv run --locked pytest tests/test_runner.py` |
| Test config | `uv run --locked pytest tests/test_config.py` |
| Test all | `uv run --locked pytest` |
| Lint a file | `uv run --locked ruff check path/to/file.py` |
| Format a file | `uv run --locked ruff format path/to/file.py` |

## Key Conventions

- PT-BR for documentation and user-facing text; English for code, APIs, YAML keys, and tests.
- Library code: `src/mqtt_ids/`; thin entrypoints: `scripts/`; exploration only: `notebooks/`.
- Tests use `pytest`, `test_*.py`, `test_<behavior>`, fixtures, and `tmp_path`; never use local datasets, credentials, or generated artifacts.
- Load YAML with `safe_load` and validate it before execution.
- Keep raw data immutable. Fit preprocessing, resampling, and supervised selection only in training folds.
- Update `docs/DECISIONS.md` with a new ADR; never rewrite a prior decision.

## Test Documentation

- `docs/testing/scenarios.md` is the canonical catalogue of test scenarios.
- On the command `lint tests`: inventory every `tests/test_*.py` and each `test_*` function; create or update the catalogue for undocumented tests before running validation. Record source test, inputs or setup, expected behavior, and the narrowest execution command.

## Commit Attribution

- Commits created by agents include their own attribution trailer:

```text
Co-Authored-By: <agent model> <noreply@example.com>
```
