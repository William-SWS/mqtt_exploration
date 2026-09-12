"""Dicionário de dados do dataset MQTT_UAD.

Permite consultas estruturadas e tipadas sobre o schema, descrições,
políticas de features e métricas observadas dos datasets DoS, MitM e Intrusion.

Uso via linha de comando:
    uv run --locked python scripts/data_dictionary.py

Uso em scripts Python ou Jupyter Notebook:
    from scripts.data_dictionary import load_data_dictionary

    dd = load_data_dictionary()
    col = dd["frame.time_delta"]
    print(col.description, col.policy)
    portable_cols = dd.portable_columns
    df_meta = dd.to_dataframe()
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Literal

import pandas as pd

DatasetName = Literal["dos", "mitm", "intrusion"]


class FeaturePolicy(StrEnum):
    """Políticas de features do projeto (docs/data_dictionary.md e ADR-006)."""

    PORTABLE = "portable"
    DERIVABLE = "derivable"
    ABLATION_ONLY = "ablation_only"
    EXCLUDED = "excluded"


@dataclass(frozen=True)
class DatasetStats:
    """Métricas observadas em um determinado cenário."""

    missing_pct: float
    cardinality: int


@dataclass(frozen=True)
class ColumnMetadata:
    name: str
    description: str
    semantic_type: str
    source: Literal["P", "W"]  # P = paper, W = Wireshark
    observed_dtype: str
    policy: FeaturePolicy
    stats: dict[str, DatasetStats]
    notes: str | None = None

    def stats_for(self, dataset: str) -> DatasetStats | None:
        """Acesso às estatísticas do dataset."""
        return self.stats.get(dataset.lower())

    def is_empty_in(self, dataset: str) -> bool:
        """Verifica se a coluna é 100% ausente no dataset informado."""
        st = self.stats_for(dataset)
        return st.missing_pct == 100.0 if st is not None else False

    @property
    def is_empty_everywhere(self) -> bool:
        """Retorna True se for 100% ausente em todas as bases registradas."""
        if not self.stats:
            return False
        return all(s.missing_pct == 100.0 for s in self.stats.values())

    @property
    def dos(self) -> DatasetStats | None:
        return self.stats_for("dos")

    @property
    def mitm(self) -> DatasetStats | None:
        return self.stats_for("mitm")

    @property
    def intrusion(self) -> DatasetStats | None:
        return self.stats_for("intrusion")


class DataDictionary:
    """Catálogo com métodos de consulta para todas as colunas do projeto."""

    def __init__(self, columns: list[ColumnMetadata]) -> None:
        self._columns: dict[str, ColumnMetadata] = {col.name: col for col in columns}

    def __getitem__(self, name: str) -> ColumnMetadata:
        """Permite consulta com dd['frame.len']."""
        if name not in self._columns:
            raise KeyError(f"Coluna '{name}' não encontrada no dicionário de dados.")
        return self._columns[name]

    def __contains__(self, name: str) -> bool:
        """Permite checar presença com 'ip.src' in dd."""
        return name in self._columns

    def __len__(self) -> int:
        """Permite checar tamanho com len(dd)."""
        return len(self._columns)

    def by_policy(self, policy: FeaturePolicy | str) -> list[str]:
        """Filtra colunas pela política informada."""
        pol_str = str(policy)
        return [
            col.name for col in self._columns.values() if str(col.policy) == pol_str
        ]

    @property
    def portable_columns(self) -> list[str]:
        return self.by_policy(FeaturePolicy.PORTABLE)

    @property
    def derivable_columns(self) -> list[str]:
        return self.by_policy(FeaturePolicy.DERIVABLE)

    @property
    def ablation_only_columns(self) -> list[str]:
        return self.by_policy(FeaturePolicy.ABLATION_ONLY)

    @property
    def excluded_columns(self) -> list[str]:
        return self.by_policy(FeaturePolicy.EXCLUDED)

    def empty_in(self, dataset: str) -> list[str]:
        """Retorna colunas 100% vazias no dataset informado."""
        return [col.name for col in self._columns.values() if col.is_empty_in(dataset)]

    def search(self, term: str) -> list[ColumnMetadata]:
        """Busca colunas pelo nome ou descrição."""
        term_lower = term.lower()
        return [
            col
            for col in self._columns.values()
            if term_lower in col.name.lower() or term_lower in col.description.lower()
        ]

    def to_dataframe(self) -> pd.DataFrame:
        """Exporta o catálogo como tabela pandas."""
        records = []
        for col in self._columns.values():
            rec = {
                "name": col.name,
                "description": col.description,
                "semantic_type": col.semantic_type,
                "source": col.source,
                "observed_dtype": col.observed_dtype,
                "policy": str(col.policy),
                "notes": col.notes,
            }
            for ds_name, ds_stat in col.stats.items():
                rec[f"missing_pct_{ds_name}"] = ds_stat.missing_pct
                rec[f"cardinality_{ds_name}"] = ds_stat.cardinality
            records.append(rec)
        return pd.DataFrame.from_records(records)


def load_data_dictionary(markdown_path: Path | str | None = None) -> DataDictionary:
    """Carrega o dicionário de dados a partir do arquivo docs/data_dictionary.md.

    Args:
        markdown_path: Caminho opcional do arquivo Markdown. Se omitido,
            busca em docs/data_dictionary.md a partir da raiz do repositório.

    Returns:
        Instância de DataDictionary contendo todas as colunas estruturadas.
    """
    if markdown_path is None:
        markdown_path = (
            Path(__file__).resolve().parent.parent / "docs" / "data_dictionary.md"
        )
    else:
        markdown_path = Path(markdown_path)

    if not markdown_path.is_file():
        raise FileNotFoundError(
            f"Arquivo de dicionário não encontrado em: {markdown_path}"
        )

    lines = markdown_path.read_text(encoding="utf-8").splitlines()
    columns: list[ColumnMetadata] = []

    for line in lines:
        if not (line.startswith("| `") and "|" in line[3:]):
            continue

        parts = [p.strip() for p in line.strip().strip("|").split("|")]
        if len(parts) < 8:
            continue

        name = parts[0].replace("`", "").strip()
        description = parts[1]
        semantic_type = parts[2]
        source: Literal["P", "W"] = "W" if parts[3] == "W" else "P"
        observed_dtype = parts[4].replace("`", "").strip()

        # Parse missing percentuais D/M/I (ex: '0/0/0%' ou '1,09/7,44/4,68%')
        raw_pct = parts[5].replace("%", "").strip()
        pct_vals = [float(v.replace(",", ".").strip()) for v in raw_pct.split("/")]

        # Parse cardinalidades D/M/I (ex: '9884/23602/22921')
        raw_card = parts[6].strip()
        card_vals = [int(v.strip()) for v in raw_card.split("/")]

        # Parse política e notas preliminares
        clean_pol = parts[7].replace("`", "").strip()
        pol_token = clean_pol.split()[0].lower()
        policy_map = {
            "portable": FeaturePolicy.PORTABLE,
            "derivable": FeaturePolicy.DERIVABLE,
            "ablation_only": FeaturePolicy.ABLATION_ONLY,
            "excluded": FeaturePolicy.EXCLUDED,
        }
        policy = policy_map.get(pol_token, FeaturePolicy.EXCLUDED)
        notes = clean_pol[len(pol_token) :].strip(" ()") or None

        stats = {
            "dos": DatasetStats(missing_pct=pct_vals[0], cardinality=card_vals[0]),
            "mitm": DatasetStats(missing_pct=pct_vals[1], cardinality=card_vals[1]),
            "intrusion": DatasetStats(
                missing_pct=pct_vals[2], cardinality=card_vals[2]
            ),
        }

        columns.append(
            ColumnMetadata(
                name=name,
                description=description,
                semantic_type=semantic_type,
                source=source,
                observed_dtype=observed_dtype,
                policy=policy,
                stats=stats,
                notes=notes,
            )
        )

    return DataDictionary(columns)


def main() -> None:
    """Execução principal do dicionário via linha de comando."""
    dd = load_data_dictionary()

    print("=" * 70)
    print(f" DICIONÁRIO DE DADOS MQTT_UAD — {len(dd)} COLUNAS CATALOGADAS")
    print("=" * 70)

    policies = [
        (FeaturePolicy.PORTABLE, dd.portable_columns),
        (FeaturePolicy.DERIVABLE, dd.derivable_columns),
        (FeaturePolicy.ABLATION_ONLY, dd.ablation_only_columns),
        (FeaturePolicy.EXCLUDED, dd.excluded_columns),
    ]

    print("\n[1] Distribuição por Política de Features:")
    for pol, col_list in policies:
        print(f"  - {pol.value.upper():<14}: {len(col_list):>2} colunas")

    empty_all = [c.name for c in dd._columns.values() if c.is_empty_everywhere]
    print(f"\n[2] Colunas 100% vazias em todos os datasets: {len(empty_all)}")
    print(f"    {', '.join(empty_all[:6])} ... (+{len(empty_all) - 6} outras)")

    print("\n[3] Exemplos de Consultas Rápidas:")
    example_cols = ["frame.time_delta", "ip.src", "mqtt.clientid", "mqtt.passwd"]
    for col_name in example_cols:
        col = dd[col_name]
        print(f"\n  • Variável: {col.name}")
        print(f"    - Significado   : {col.description}")
        print(f"    - Política      : {col.policy.value}")
        pct_d = col.dos.missing_pct if col.dos else 0.0
        pct_m = col.mitm.missing_pct if col.mitm else 0.0
        pct_i = col.intrusion.missing_pct if col.intrusion else 0.0
        print(f"    - Ausência D/M/I: {pct_d}% / {pct_m}% / {pct_i}%")
        c_d = col.dos.cardinality if col.dos else 0
        c_m = col.mitm.cardinality if col.mitm else 0
        c_i = col.intrusion.cardinality if col.intrusion else 0
        print(f"    - Cardinalidade : DoS={c_d}, MitM={c_m}, Intrusion={c_i}")

    print("\n" + "=" * 70)
    print(" Para consultar interativamente no Jupyter ou scripts:")
    print("   from scripts.data_dictionary import load_data_dictionary")
    print("   dd = load_data_dictionary()")
    print("   display(dd.to_dataframe())")
    print("=" * 70)


if __name__ == "__main__":
    main()
