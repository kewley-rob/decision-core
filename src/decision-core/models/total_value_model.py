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
from typing import Mapping, Protocol, Sequence

from value.categorical import MappingCategoricalValueFunction

from .decision_analysis_result import DecisionAnalysisResult, DecisionAnalysisRow
from .decision_problem import DecisionProblem
from .feasibility_rule import FeasibilityRule


class ValueFunction(Protocol):
    def __call__(self, raw_value: object) -> float:
        ...


@dataclass(frozen=True)
class SolutionScore:
    criterion_value_scores: Mapping[str, float]
    criterion_weighted_contributions: Mapping[str, float]
    total_score: float


@dataclass(frozen=True)
class TotalValueModel:
    id: str
    name: str
    decision_problem: DecisionProblem
    criterion_value_functions: Mapping[str, ValueFunction]
    criterion_weights: Mapping[str, float]
    feasibility_rules: Sequence[FeasibilityRule] = ()

    def __post_init__(self) -> None:
        if not self.id or not self.id.strip():
            raise ValueError("TotalValueModel id must be a non-empty string.")
        if not self.name or not self.name.strip():
            raise ValueError("TotalValueModel name must be a non-empty string.")
        if not self.criterion_value_functions:
            raise ValueError("TotalValueModel requires at least one criterion value function.")
        if not self.criterion_weights:
            raise ValueError("TotalValueModel requires at least one criterion weight.")

        normalized_functions: dict[str, ValueFunction] = {}
        for criterion_id, value_function in self.criterion_value_functions.items():
            if not isinstance(criterion_id, str) or not criterion_id.strip():
                raise ValueError("TotalValueModel criterion ids must be non-empty strings.")
            if not callable(value_function):
                raise ValueError(
                    f"TotalValueModel value function for criterion '{criterion_id}' must be callable."
                )
            normalized_functions[criterion_id] = value_function

        criteria_by_id = {criterion.id: criterion for criterion in self.decision_problem.criteria}
        criterion_ids = set(criteria_by_id.keys())
        mapped_ids = set(normalized_functions.keys())

        unknown_criteria = mapped_ids - criterion_ids
        if unknown_criteria:
            unknown = ", ".join(sorted(unknown_criteria))
            raise ValueError(
                f"TotalValueModel includes unknown criterion ids for the paired DecisionProblem: {unknown}."
            )

        missing_criteria = criterion_ids - mapped_ids
        if missing_criteria:
            missing = ", ".join(sorted(missing_criteria))
            raise ValueError(
                f"TotalValueModel is missing value functions for DecisionProblem criteria: {missing}."
            )

        for criterion_id, criterion in criteria_by_id.items():
            self._validate_criterion_value_function_compatibility(
                criterion_id=criterion_id,
                criterion_kind=criterion.kind,
                value_function=normalized_functions[criterion_id],
            )

            self._validate_criterion_mapping_coverage(
                criterion_id=criterion_id,
                criterion_kind=criterion.kind,
                criterion_allowed_values=criterion.allowed_values,
                value_function=normalized_functions[criterion_id],
            )

        normalized_weights: dict[str, float] = {}
        total_raw_weight = 0.0
        for criterion_id, raw_weight in self.criterion_weights.items():
            if not isinstance(criterion_id, str) or not criterion_id.strip():
                raise ValueError("TotalValueModel weight criterion ids must be non-empty strings.")
            if isinstance(raw_weight, bool) or not isinstance(raw_weight, (int, float)):
                raise ValueError(
                    f"TotalValueModel weight for criterion '{criterion_id}' must be numeric (int/float, excluding bool)."
                )

            normalized_weight = float(raw_weight)
            if normalized_weight < 0.0 or normalized_weight > 100.0:
                raise ValueError(
                    f"TotalValueModel weight for criterion '{criterion_id}' must be between 0 and 100."
                )

            normalized_weights[criterion_id] = normalized_weight
            total_raw_weight += normalized_weight

        if total_raw_weight <= 0.0:
            raise ValueError("TotalValueModel criterion weights must include at least one positive weight.")

        weighted_ids = set(normalized_weights.keys())

        unknown_weight_criteria = weighted_ids - criterion_ids
        if unknown_weight_criteria:
            unknown = ", ".join(sorted(unknown_weight_criteria))
            raise ValueError(
                f"TotalValueModel includes unknown weighted criterion ids for the paired DecisionProblem: {unknown}."
            )

        missing_weight_criteria = criterion_ids - weighted_ids
        if missing_weight_criteria:
            missing = ", ".join(sorted(missing_weight_criteria))
            raise ValueError(
                f"TotalValueModel is missing criterion weights for DecisionProblem criteria: {missing}."
            )

        normalized_rules: list[FeasibilityRule] = []
        seen_rule_ids: set[str] = set()
        for feasibility_rule in self.feasibility_rules:
            if not isinstance(feasibility_rule, FeasibilityRule):
                raise ValueError("TotalValueModel feasibility rules must be FeasibilityRule instances.")
            if feasibility_rule.id in seen_rule_ids:
                raise ValueError(
                    f"TotalValueModel includes duplicate feasibility rule id '{feasibility_rule.id}'."
                )
            if feasibility_rule.criterion_id not in criterion_ids:
                raise ValueError(
                    f"TotalValueModel feasibility rule '{feasibility_rule.id}' references unknown criterion id "
                    f"'{feasibility_rule.criterion_id}' for the paired DecisionProblem."
                )
            seen_rule_ids.add(feasibility_rule.id)
            normalized_rules.append(feasibility_rule)

        object.__setattr__(self, "criterion_value_functions", normalized_functions)
        object.__setattr__(self, "criterion_weights", normalized_weights)
        object.__setattr__(self, "feasibility_rules", normalized_rules)

    def evaluate(self, criterion_id: str, raw_value: object) -> float:
        if criterion_id not in self.criterion_value_functions:
            raise ValueError(f"Criterion '{criterion_id}' is not configured in this TotalValueModel.")

        value_function = self.criterion_value_functions[criterion_id]
        raw_value_score = value_function(raw_value)
        if not isinstance(raw_value_score, Number) or isinstance(raw_value_score, bool):
            raise ValueError(
                f"Value function for criterion '{criterion_id}' must return a numeric score in [0, 100]."
            )

        value_score = float(raw_value_score)
        if value_score < 0.0 or value_score > 100.0:
            raise ValueError(
                f"Value function for criterion '{criterion_id}' returned {value_score}, "
                "but scores must be in [0, 100]."
            )

        return value_score

    def _validate_criterion_value_function_compatibility(
        self,
        criterion_id: str,
        criterion_kind: str,
        value_function: ValueFunction,
    ) -> None:
        is_mapping_value_function = isinstance(value_function, MappingCategoricalValueFunction)

        if criterion_kind in {"boolean", "categorical"} and not is_mapping_value_function:
            raise ValueError(
                f"Criterion '{criterion_id}' with kind '{criterion_kind}' requires a mapping value function."
            )

        if criterion_kind in {"continuous", "integer"} and is_mapping_value_function:
            raise ValueError(
                f"Criterion '{criterion_id}' with kind '{criterion_kind}' cannot use a mapping value function."
            )

    def _validate_criterion_mapping_coverage(
        self,
        criterion_id: str,
        criterion_kind: str,
        criterion_allowed_values: tuple[int | float | str, ...] | None,
        value_function: ValueFunction,
    ) -> None:
        if criterion_kind not in {"ordinal", "categorical"}:
            return

        if not isinstance(value_function, MappingCategoricalValueFunction):
            return

        if criterion_allowed_values is None:
            return

        allowed_values = set(criterion_allowed_values)
        mapping_keys = set(value_function.value_mapping.keys())

        missing_values = sorted(allowed_values - mapping_keys, key=str)
        if missing_values:
            raise ValueError(
                f"Mapping value function for criterion '{criterion_id}' is missing allowed_values entries: "
                f"{missing_values}."
            )

        unknown_values = sorted(mapping_keys - allowed_values, key=str)
        if unknown_values:
            raise ValueError(
                f"Mapping value function for criterion '{criterion_id}' contains keys not present in "
                f"allowed_values: {unknown_values}."
            )

    def normalized_weights(self) -> dict[str, float]:
        total_raw_weight = sum(self.criterion_weights.values())
        return {
            criterion_id: raw_weight / total_raw_weight
            for criterion_id, raw_weight in self.criterion_weights.items()
        }

    def score_raw_measurements(self, raw_measurements: Mapping[str, object]) -> SolutionScore:
        normalized_weights = self.normalized_weights()
        criterion_value_scores: dict[str, float] = {}
        criterion_weighted_contributions: dict[str, float] = {}

        for criterion in self.decision_problem.criteria:
            criterion_id = criterion.id
            if criterion_id not in raw_measurements:
                raise ValueError(
                    f"Raw measurements are missing criterion '{criterion_id}' required for scoring."
                )

            value_score = self.evaluate(criterion_id, raw_measurements[criterion_id])
            contribution = value_score * normalized_weights[criterion_id]
            criterion_value_scores[criterion_id] = value_score
            criterion_weighted_contributions[criterion_id] = contribution

        total_score = float(sum(criterion_weighted_contributions.values()))
        return SolutionScore(
            criterion_value_scores=criterion_value_scores,
            criterion_weighted_contributions=criterion_weighted_contributions,
            total_score=total_score,
        )

    def score_decision_problem(self, enforce_raw_feasibility: bool = True) -> DecisionAnalysisResult:
        rows: list[DecisionAnalysisRow] = []
        for alternative in self.decision_problem.alternatives:
            raw_measurements = alternative.measurements
            solution_score = self.score_raw_measurements(raw_measurements)
            feasibility_rule_results = {
                rule.id: rule.evaluate(raw_measurements) for rule in self.feasibility_rules
            }
            rows.append(
                DecisionAnalysisRow(
                    alternative_id=alternative.id,
                    criterion_value_scores=solution_score.criterion_value_scores,
                    total_score=solution_score.total_score,
                    feasibility_rule_results=feasibility_rule_results,
                )
            )

        return DecisionAnalysisResult(
            decision_problem=self.decision_problem,
            total_value_model=self,
            rows=rows,
        )

    def passes_raw_feasibility(self, raw_measurements: Mapping[str, object]) -> bool:
        return all(rule.evaluate(raw_measurements) for rule in self.feasibility_rules)
