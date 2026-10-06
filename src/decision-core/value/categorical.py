#  Decision Analysis Core Copyright (C) 2026 Robert Kewley
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from numbers import Number
from typing import Hashable, Mapping, Protocol, runtime_checkable


CategoricalInput = Hashable


def coerce_value_score(raw_score: object) -> float:
    if not isinstance(raw_score, Number) or isinstance(raw_score, bool):
        raise ValueError("Categorical value models require numeric scores (int/float, excluding bool).")

    score = float(raw_score)
    if score < 0.0 or score > 100.0:
        raise ValueError("Categorical value scores must be in the range [0.0, 100.0].")
    return score


@runtime_checkable
class CategoricalValueFunction(Protocol):
    def evaluate(self, raw_value: CategoricalInput) -> float:
        ...

    def __call__(self, raw_value: CategoricalInput) -> float:
        ...


class BaseCategoricalValueFunction(ABC):
    def __call__(self, raw_value: CategoricalInput) -> float:
        return self.evaluate(raw_value)

    @abstractmethod
    def evaluate(self, raw_value: CategoricalInput) -> float:
        raise NotImplementedError


@dataclass(frozen=True)
class MappingCategoricalValueFunction(BaseCategoricalValueFunction):
    value_mapping: Mapping[CategoricalInput, float]

    def __post_init__(self) -> None:
        if not self.value_mapping:
            raise ValueError("Categorical value model requires at least one mapping entry.")

        normalized_mapping: dict[CategoricalInput, float] = {}
        for key, raw_score in self.value_mapping.items():
            if key is None:
                raise ValueError("Categorical value model does not allow None as a category key.")
            normalized_mapping[key] = coerce_value_score(raw_score)

        object.__setattr__(self, "value_mapping", normalized_mapping)

    def evaluate(self, raw_value: CategoricalInput) -> float:
        if raw_value not in self.value_mapping:
            raise ValueError(f"Unknown categorical value '{raw_value}'.")
        return self.value_mapping[raw_value]
