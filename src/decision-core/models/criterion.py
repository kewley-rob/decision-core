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

from dataclasses import dataclass
from numbers import Number
from typing import Literal


CriterionType = Literal["continuous", "integer", "boolean", "ordinal", "categorical"]


@dataclass(frozen=True)
class Criterion:
    id: str
    name: str
    kind: CriterionType
    min_value: float | int | None = None
    max_value: float | int | None = None
    allowed_values: tuple[int | float | str, ...] | None = None

    def __post_init__(self) -> None:
        if not self.id or not self.id.strip():
            raise ValueError("Criterion id must be a non-empty string.")
        if not self.name or not self.name.strip():
            raise ValueError("Criterion name must be a non-empty string.")

        if self.kind not in {"continuous", "integer", "boolean", "ordinal", "categorical"}:
            raise ValueError(f"Criterion kind '{self.kind}' is not supported.")

        if self.kind in {"continuous", "integer"}:
            self._validate_numeric_bounds()
            if self.allowed_values is not None:
                raise ValueError("allowed_values is not supported for continuous/integer criteria.")
            return

        if self.kind == "boolean":
            if self.min_value is not None or self.max_value is not None:
                raise ValueError("min_value/max_value are not supported for boolean criteria.")
            if self.allowed_values is not None:
                raise ValueError("allowed_values is not supported for boolean criteria.")
            return

        if self.min_value is not None or self.max_value is not None:
            raise ValueError("min_value/max_value are only supported for continuous/integer criteria.")

        if not self.allowed_values:
            raise ValueError("allowed_values must be provided for ordinal/categorical criteria.")

        if self.kind == "categorical":
            self._validate_categorical_values()
        else:
            self._validate_ordinal_values()

    def validate_measurement(self, value: object) -> None:
        if self.kind == "continuous":
            if not isinstance(value, Number) or isinstance(value, bool):
                raise ValueError(f"Criterion '{self.id}' expects a numeric value.")
            numeric_value = float(value)
            if self.min_value is not None and numeric_value < float(self.min_value):
                raise ValueError(f"Criterion '{self.id}' value must be >= {self.min_value}.")
            if self.max_value is not None and numeric_value > float(self.max_value):
                raise ValueError(f"Criterion '{self.id}' value must be <= {self.max_value}.")
            return

        if self.kind == "integer":
            if not isinstance(value, int) or isinstance(value, bool):
                raise ValueError(f"Criterion '{self.id}' expects an integer value.")
            if self.min_value is not None and value < int(self.min_value):
                raise ValueError(f"Criterion '{self.id}' value must be >= {self.min_value}.")
            if self.max_value is not None and value > int(self.max_value):
                raise ValueError(f"Criterion '{self.id}' value must be <= {self.max_value}.")
            return

        if self.kind == "boolean":
            if not isinstance(value, bool):
                raise ValueError(f"Criterion '{self.id}' expects a boolean value.")
            return

        if value not in self.allowed_values:
            raise ValueError(
                f"Criterion '{self.id}' value '{value}' is not in allowed_values {self.allowed_values}."
            )

    def _validate_numeric_bounds(self) -> None:
        if self.min_value is not None:
            self._validate_numeric_bound_value(self.min_value, "min_value")
        if self.max_value is not None:
            self._validate_numeric_bound_value(self.max_value, "max_value")
        if self.min_value is not None and self.max_value is not None and self.min_value > self.max_value:
            raise ValueError("Criterion min_value must be less than or equal to max_value.")

    def _validate_numeric_bound_value(self, value: float | int, field_name: str) -> None:
        if self.kind == "continuous":
            if not isinstance(value, Number) or isinstance(value, bool):
                raise ValueError(f"Criterion {field_name} must be numeric for continuous criteria.")
            return

        if not isinstance(value, int) or isinstance(value, bool):
            raise ValueError(f"Criterion {field_name} must be an integer for integer criteria.")

    def _validate_categorical_values(self) -> None:
        normalized: list[str] = []
        for raw_value in self.allowed_values or ():
            if not isinstance(raw_value, str) or not raw_value.strip():
                raise ValueError("Categorical allowed_values must be non-empty strings.")
            normalized.append(raw_value)

        if len(normalized) != len(set(normalized)):
            raise ValueError("Categorical allowed_values must be unique.")

        object.__setattr__(self, "allowed_values", tuple(normalized))

    def _validate_ordinal_values(self) -> None:
        normalized: list[int | float | str] = []
        for raw_value in self.allowed_values or ():
            if isinstance(raw_value, bool):
                raise ValueError("Ordinal allowed_values cannot contain booleans.")
            if isinstance(raw_value, Number):
                normalized.append(float(raw_value))
                continue
            if isinstance(raw_value, str) and raw_value.strip():
                normalized.append(raw_value)
                continue
            raise ValueError("Ordinal allowed_values must be numbers or non-empty strings.")

        if len(normalized) != len(set(normalized)):
            raise ValueError("Ordinal allowed_values must be unique.")

        object.__setattr__(self, "allowed_values", tuple(normalized))