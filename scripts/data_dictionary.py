from dataclasses import dataclass, asdict
from enum import StrEnum
from typing import Literal

DatasetName = Literal["dos", "mitm", "intrusion"]

class FeaturePolicy(StrEnum):
    """Feature policy for a feature in the data dictionary."""

    PORTABLE = 'portable'
    REQUIRED = "required"
    OPTIONAL = "optional"
    DEPRECATED = "deprecated"

@dataclass(frozen=True)

class ColumnMetadata:
    name: str
    description: str
    semantic_type: str
    source: Literal["P", "W"]  # P = paper, W = Wireshark
    observed_dtype: str
    missing_pct_intrusion: float
    cardinality_intrusion: int
    dos: DatasetStats
    mitm: DatasetStats
    intrusion: DatasetStats
    policy: FeaturePolicy
    notes: str | None = None

    def stats_for(self, dataset: DatasetName) -> "DatasetStats":  ##Acesso as estatísticas do dataset.
        return getattr(self, dataset)

    def is_empty_in(self, dataset: DatasetName) -> bool:        
        return self.stats_for(dataset),self.missing_pct == 100.0

    @property
    def is_empty_everywhere(self) -> bool:
        return (
            self.dos.missing_pct == 100.0
            self.mitm.missing_pct = 100.0
            self.intrusion.missing_pct ==100.0
        )

