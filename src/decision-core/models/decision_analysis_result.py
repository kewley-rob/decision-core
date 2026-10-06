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
from typing import TYPE_CHECKING, Mapping, Sequence

from .decision_problem import DecisionProblem

if TYPE_CHECKING:
    from .total_value_model import TotalValueModel


@dataclass(frozen=True)
class DecisionAnalysisRow:
    alternative_id: str
    criterion_value_scores: Mapping[str, float]
    total_score: float
    feasibility_rule_results: Mapping[str, bool]

    def __post_init__(self) -> None:
        if not self.alternative_id or not self.alternative_id.strip():
            raise ValueError("DecisionAnalysisRow alternative_id must be a non-empty string.")
        if not self.criterion_value_scores:
            raise ValueError("DecisionAnalysisRow requires at least one criterion value score.")

        normalized_scores: dict[str, float] = {}
        for criterion_id, raw_score in self.criterion_value_scores.items():
            if not isinstance(criterion_id, str) or not criterion_id.strip():
                raise ValueError("DecisionAnalysisRow criterion ids must be non-empty strings.")
            if isinstance(raw_score, bool) or not isinstance(raw_score, (int, float)):
                raise ValueError(
                    f"DecisionAnalysisRow value score for criterion '{criterion_id}' must be numeric (int/float, excluding bool)."
                )

            score = float(raw_score)
            if score < 0.0 or score > 100.0:
                raise ValueError(
                    f"DecisionAnalysisRow value score for criterion '{criterion_id}' must be between 0 and 100."
                )
            normalized_scores[criterion_id] = score

        if isinstance(self.total_score, bool) or not isinstance(self.total_score, (int, float)):
            raise ValueError("DecisionAnalysisRow total_score must be numeric (int/float, excluding bool).")

        normalized_total_score = float(self.total_score)
        if normalized_total_score < 0.0 or normalized_total_score > 100.0:
            raise ValueError("DecisionAnalysisRow total_score must be between 0 and 100.")

        normalized_feasibility_results: dict[str, bool] = {}
        for rule_id, passed in self.feasibility_rule_results.items():
            if not isinstance(rule_id, str) or not rule_id.strip():
                raise ValueError("DecisionAnalysisRow feasibility rule ids must be non-empty strings.")
            if not isinstance(passed, bool):
                raise ValueError(
                    f"DecisionAnalysisRow feasibility result for rule '{rule_id}' must be a boolean."
                )
            normalized_feasibility_results[rule_id] = passed

        object.__setattr__(self, "criterion_value_scores", normalized_scores)
        object.__setattr__(self, "total_score", normalized_total_score)
        object.__setattr__(self, "feasibility_rule_results", normalized_feasibility_results)


@dataclass(frozen=True)
class DecisionAnalysisResult:
    decision_problem: DecisionProblem
    total_value_model: TotalValueModel
    rows: Sequence[DecisionAnalysisRow]

    def __post_init__(self) -> None:
        if not self.rows:
            raise ValueError("DecisionAnalysisResult requires at least one row.")

        expected_criterion_ids = {criterion.id for criterion in self.decision_problem.criteria}
        expected_alternative_ids = {alternative.id for alternative in self.decision_problem.alternatives}
        expected_feasibility_rule_ids = {
            feasibility_rule.id for feasibility_rule in self.total_value_model.feasibility_rules
        }

        seen_alternative_ids: set[str] = set()
        normalized_rows: list[DecisionAnalysisRow] = []

        for row in self.rows:
            if not isinstance(row, DecisionAnalysisRow):
                raise ValueError("DecisionAnalysisResult rows must be DecisionAnalysisRow instances.")

            if row.alternative_id in seen_alternative_ids:
                raise ValueError(
                    f"DecisionAnalysisResult includes duplicate alternative row '{row.alternative_id}'."
                )
            seen_alternative_ids.add(row.alternative_id)

            if row.alternative_id not in expected_alternative_ids:
                raise ValueError(
                    f"DecisionAnalysisResult row alternative '{row.alternative_id}' is not part of the linked DecisionProblem."
                )

            score_ids = set(row.criterion_value_scores.keys())
            unknown_criteria = score_ids - expected_criterion_ids
            if unknown_criteria:
                unknown = ", ".join(sorted(unknown_criteria))
                raise ValueError(
                    f"DecisionAnalysisResult row '{row.alternative_id}' includes unknown criterion ids: {unknown}."
                )

            missing_criteria = expected_criterion_ids - score_ids
            if missing_criteria:
                missing = ", ".join(sorted(missing_criteria))
                raise ValueError(
                    f"DecisionAnalysisResult row '{row.alternative_id}' is missing criterion ids: {missing}."
                )

            feasibility_rule_ids = set(row.feasibility_rule_results.keys())
            unknown_rule_ids = feasibility_rule_ids - expected_feasibility_rule_ids
            if unknown_rule_ids:
                unknown = ", ".join(sorted(unknown_rule_ids))
                raise ValueError(
                    f"DecisionAnalysisResult row '{row.alternative_id}' includes unknown feasibility rule ids: {unknown}."
                )

            missing_rule_ids = expected_feasibility_rule_ids - feasibility_rule_ids
            if missing_rule_ids:
                missing = ", ".join(sorted(missing_rule_ids))
                raise ValueError(
                    f"DecisionAnalysisResult row '{row.alternative_id}' is missing feasibility rule ids: {missing}."
                )

            normalized_rows.append(row)

        object.__setattr__(self, "rows", tuple(normalized_rows))