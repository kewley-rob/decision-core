from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Protocol


class CriterionFeasibilityPredicate(Protocol):
    def __call__(self, raw_value: object) -> bool:
        ...


@dataclass(frozen=True)
class FeasibilityRule:
    id: str
    name: str
    criterion_id: str
    predicate: CriterionFeasibilityPredicate

    def __post_init__(self) -> None:
        if not self.id or not self.id.strip():
            raise ValueError("FeasibilityRule id must be a non-empty string.")
        if not self.name or not self.name.strip():
            raise ValueError("FeasibilityRule name must be a non-empty string.")
        if not self.criterion_id or not self.criterion_id.strip():
            raise ValueError("FeasibilityRule criterion_id must be a non-empty string.")
        if not callable(self.predicate):
            raise ValueError("FeasibilityRule predicate must be callable.")

    def evaluate(self, raw_measurements: Mapping[str, object]) -> bool:
        if self.criterion_id not in raw_measurements:
            raise ValueError(
                f"FeasibilityRule '{self.id}' criterion '{self.criterion_id}' is missing from measurements."
            )

        raw_value = raw_measurements[self.criterion_id]
        result = self.predicate(raw_value)
        if not isinstance(result, bool):
            raise ValueError(f"FeasibilityRule '{self.id}' predicate must return a boolean.")
        return result
