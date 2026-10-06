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

import sys
from pathlib import Path
from typing import Mapping, Protocol


PROJECT_ROOT = Path(__file__).resolve().parent
DECISION_CORE_SRC = PROJECT_ROOT / "src" / "decision-core"
DECISION_PLOTS_SRC = PROJECT_ROOT / "src" / "decision-plots"

for source_path in (DECISION_CORE_SRC, DECISION_PLOTS_SRC):
    source_path_str = str(source_path)
    if source_path_str not in sys.path:
        sys.path.insert(0, source_path_str)

from decision_core import (
    Alternative,
    Criterion,
    DecisionAnalysisResult,
    DecisionProblem,
    FeasibilityRule,
    LinearDecreasingValueFunction,
    LinearIncreasingValueFunction,
    MappingCategoricalValueFunction,
    PiecewiseLinearValueFunction,
    TotalValueModel,
)


class CriterionFeasibilityPredicate(Protocol):
    def __call__(self, raw_value: object) -> bool:
        ...


CRITERIA = [
    Criterion(id="stopping_distance", name="Stopping Distance", kind="continuous", min_value=0.0),
    Criterion(id="airbags", name="Airbags", kind="integer", min_value=0),
    Criterion(id="rollover_rating", name="Rollover Rating", kind="ordinal", allowed_values=(1, 2, 3, 4, 5)),
    Criterion(
        id="apps",
        name="Apps",
        kind="categorical",
        allowed_values=("None", "Subscription", "Wired Car Play", "Wireless Car Play"),
    ),
    Criterion(id="cargo_space", name="Cargo space", kind="continuous", min_value=0.0),
    Criterion(id="traction_control", name="Traction Control", kind="boolean"),
    Criterion(id="rear_legroom", name="Rear Legroom", kind="continuous", min_value=0.0),
    Criterion(id="crash_ratings", name="Crash Ratings", kind="ordinal", allowed_values=(1, 2, 3, 4, 5)),
]


RAW_MATRIX = [
    {
        "Alternative": "Cadillac SRX Luxury 4WD",
        "Stopping Distance": 119.0,
        "Airbags": 6,
        "Rollover Rating": 4,
        "Apps": "Subscription",
        "Cargo space": 29.8,
        "Traction Control": True,
        "Rear Legroom": 36.0,
        "Crash Ratings": 5,
    },
    {
        "Alternative": "Acura RDX SH 4WD",
        "Stopping Distance": 125.0,
        "Airbags": 6,
        "Rollover Rating": 4,
        "Apps": "Wireless Car Play",
        "Cargo space": 28.0,
        "Traction Control": True,
        "Rear Legroom": 37.6,
        "Crash Ratings": 5,
    },
    {
        "Alternative": "Honda CR-V EX-L 4WD",
        "Stopping Distance": 119.0,
        "Airbags": 6,
        "Rollover Rating": 4,
        "Apps": "Wireless Car Play",
        "Cargo space": 35.7,
        "Traction Control": True,
        "Rear Legroom": 38.5,
        "Crash Ratings": 5,
    },
    {
        "Alternative": "Toyota RAV4",
        "Stopping Distance": 130.0,
        "Airbags": 6,
        "Rollover Rating": 4,
        "Apps": "Subscription",
        "Cargo space": 36.4,
        "Traction Control": True,
        "Rear Legroom": 38.3,
        "Crash Ratings": 5,
    },
    {
        "Alternative": "Volvo XC-60",
        "Stopping Distance": 123.0,
        "Airbags": 6,
        "Rollover Rating": 4,
        "Apps": "Wireless Car Play",
        "Cargo space": 30.8,
        "Traction Control": True,
        "Rear Legroom": 36.4,
        "Crash Ratings": 5,
    },
    {
        "Alternative": "Lexus RX 350 AWD",
        "Stopping Distance": 130.0,
        "Airbags": 10,
        "Rollover Rating": 4,
        "Apps": "Wireless Car Play",
        "Cargo space": 40.0,
        "Traction Control": True,
        "Rear Legroom": 36.8,
        "Crash Ratings": 5,
    },
    {
        "Alternative": "Mitsubishi Outlander",
        "Stopping Distance": 141.0,
        "Airbags": 8,
        "Rollover Rating": 4,
        "Apps": "Wireless Car Play",
        "Cargo space": 36.2,
        "Traction Control": True,
        "Rear Legroom": 39.6,
        "Crash Ratings": 5,
    },
    {
        "Alternative": "Lexus RX 350 AWD (2009)",
        "Stopping Distance": 130.0,
        "Airbags": 10,
        "Rollover Rating": 4,
        "Apps": "Wireless Car Play",
        "Cargo space": 40.0,
        "Traction Control": True,
        "Rear Legroom": 36.8,
        "Crash Ratings": 5,
    },
    {
        "Alternative": "Honda CR-V EX-L 4WD (2009)",
        "Stopping Distance": 119.0,
        "Airbags": 6,
        "Rollover Rating": 4,
        "Apps": "Subscription",
        "Cargo space": 35.7,
        "Traction Control": True,
        "Rear Legroom": 38.5,
        "Crash Ratings": 5,
    },
    {
        "Alternative": "Honda Odyssey EX-L",
        "Stopping Distance": 147.0,
        "Airbags": 8,
        "Rollover Rating": 4,
        "Apps": "None",
        "Cargo space": 38.4,
        "Traction Control": True,
        "Rear Legroom": 40.9,
        "Crash Ratings": 5,
    },
]


NUMERICAL_VALUE_MODELS = {
    "stopping_distance": LinearDecreasingValueFunction(min_raw_value=100.0, max_raw_value=150.0),
    "airbags": PiecewiseLinearValueFunction(
        points=((2.0, 10.0), (4.0, 20.0), (6.0, 80.0), (8.0, 100.0), (10.0, 100.0))
    ),
    "cargo_space": LinearIncreasingValueFunction(min_raw_value=25.0, max_raw_value=50.0),
    "rear_legroom": LinearIncreasingValueFunction(min_raw_value=30.0, max_raw_value=40.0),
}


CATEGORICAL_VALUE_MODELS = {
    "rollover_rating": MappingCategoricalValueFunction(
        value_mapping={1: 0.0, 2: 0.0, 3: 10.0, 4: 50.0, 5: 100.0}
    ),
    "crash_ratings": MappingCategoricalValueFunction(
        value_mapping={1: 0.0, 2: 0.0, 3: 10.0, 4: 50.0, 5: 100.0}
    ),
    "apps": MappingCategoricalValueFunction(
        value_mapping={
            "None": 0.0,
            "Subscription": 30.0,
            "Wired Car Play": 60.0,
            "Wireless Car Play": 100.0,
        }
    ),
    "traction_control": MappingCategoricalValueFunction(value_mapping={False: 0.0, True: 100.0}),
}


CRITERION_RAW_WEIGHTS = {
    "stopping_distance": 100.0,
    "airbags": 100.0,
    "rollover_rating": 75.0,
    "apps": 75.0,
    "cargo_space": 75.0,
    "traction_control": 0.0,
    "rear_legroom": 50.0,
    "crash_ratings": 50.0,
}


def _criterion_measurements_from_raw_row(row: dict[str, object]) -> dict[str, object]:
    return {criterion.id: row[criterion.name] for criterion in CRITERIA}


def _requires_traction_control(raw_value: object) -> bool:
    return raw_value is True


def _apps_must_not_be_none(raw_value: object) -> bool:
    return raw_value != "None"


def _rollover_rating_minimum(raw_value: object) -> bool:
    return float(raw_value) >= 4.0


REQUIRES_TRACTION_CONTROL_PREDICATE: CriterionFeasibilityPredicate = _requires_traction_control
APPS_MUST_NOT_BE_NONE_PREDICATE: CriterionFeasibilityPredicate = _apps_must_not_be_none
ROLLOVER_RATING_MINIMUM_PREDICATE: CriterionFeasibilityPredicate = _rollover_rating_minimum


RAW_FEASIBILITY_RULES = [
    FeasibilityRule(
        id="requires_traction_control",
        name="Requires traction control",
        criterion_id="traction_control",
        predicate=REQUIRES_TRACTION_CONTROL_PREDICATE,
    ),
    FeasibilityRule(
        id="apps_must_not_be_none",
        name="Apps must not be None",
        criterion_id="apps",
        predicate=APPS_MUST_NOT_BE_NONE_PREDICATE,
    ),
    FeasibilityRule(
        id="rollover_rating_minimum",
        name="Rollover rating must be at least 4",
        criterion_id="rollover_rating",
        predicate=ROLLOVER_RATING_MINIMUM_PREDICATE,
    ),
]


def build_car_decision_problem() -> DecisionProblem:
    alternatives = [
        Alternative(
            id=str(row["Alternative"]),
            name=str(row["Alternative"]),
            measurements=_criterion_measurements_from_raw_row(row),
        )
        for row in RAW_MATRIX
    ]
    return DecisionProblem(
        id="car-decision",
        name="Car Decision",
        criteria=list(CRITERIA),
        alternatives=alternatives,
    )


CAR_DECISION_PROBLEM = build_car_decision_problem()


TOTAL_VALUE_MODEL = TotalValueModel(
    id="car-total-value-model",
    name="Car Total Value Model",
    decision_problem=CAR_DECISION_PROBLEM,
    criterion_value_functions={**NUMERICAL_VALUE_MODELS, **CATEGORICAL_VALUE_MODELS},
    criterion_weights=CRITERION_RAW_WEIGHTS,
    feasibility_rules=RAW_FEASIBILITY_RULES,
)


def passes_raw_feasibility_rules(row: dict[str, object]) -> bool:
    return TOTAL_VALUE_MODEL.passes_raw_feasibility(_criterion_measurements_from_raw_row(row))


def feasible_raw_rows() -> list[dict[str, object]]:
    return [row for row in RAW_MATRIX if passes_raw_feasibility_rules(row)]


def score_cell(criterion_id: str, raw_value: object) -> float:
    return TOTAL_VALUE_MODEL.evaluate(criterion_id, raw_value)


def build_value_score_matrix(
    decision_result: DecisionAnalysisResult | None = None,
) -> list[dict[str, float | str | bool]]:
    if decision_result is None:
        decision_result = TOTAL_VALUE_MODEL.score_decision_problem()
    alternative_names_by_id = {
        alternative.id: alternative.name for alternative in decision_result.decision_problem.alternatives
    }

    matrix: list[dict[str, float | str | bool]] = []
    for scored_result_row in decision_result.rows:
        scored_row: dict[str, float | str | bool] = {
            "Alternative": alternative_names_by_id[scored_result_row.alternative_id]
        }
        for criterion in CAR_DECISION_PROBLEM.criteria:
            scored_row[criterion.name] = scored_result_row.criterion_value_scores[criterion.id]
        scored_row["Total Score"] = scored_result_row.total_score
        for rule in TOTAL_VALUE_MODEL.feasibility_rules:
            scored_row[rule.id] = scored_result_row.feasibility_rule_results[rule.id]
        matrix.append(scored_row)
    return matrix


def build_decision_analysis_figure(decision_result: DecisionAnalysisResult | None = None):
    from decision_plots import DecisionAnalysisStackedBarPlotter

    if decision_result is None:
        decision_result = TOTAL_VALUE_MODEL.score_decision_problem()
    return DecisionAnalysisStackedBarPlotter().build_figure(decision_result)


def print_value_score_matrix(matrix: list[dict[str, float | str | bool]]) -> None:
    criterion_names = [criterion.name for criterion in CAR_DECISION_PROBLEM.criteria]
    feasibility_rule_ids = [rule.id for rule in TOTAL_VALUE_MODEL.feasibility_rules]
    header = ["Alternative", *criterion_names, "Total Score", *feasibility_rule_ids]
    print(",".join(header))
    for row in matrix:
        cells = [str(row["Alternative"])]
        for criterion in criterion_names:
            cells.append(f"{float(row[criterion]):.2f}")
        cells.append(f"{float(row['Total Score']):.2f}")
        for rule_id in feasibility_rule_ids:
            cells.append(str(bool(row[rule_id])))
        print(",".join(cells))


if __name__ == "__main__":
    scored_decision_result = TOTAL_VALUE_MODEL.score_decision_problem()
    value_score_matrix = build_value_score_matrix(scored_decision_result)
    decision_analysis_figure = build_decision_analysis_figure(scored_decision_result)
    print_value_score_matrix(value_score_matrix)
    decision_analysis_figure.show()
