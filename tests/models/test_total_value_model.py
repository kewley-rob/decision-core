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

import pytest

from decision_core import (
    Alternative,
    Criterion,
    DecisionProblem,
    FeasibilityRule,
    LinearDecreasingValueFunction,
    LinearIncreasingValueFunction,
    MappingCategoricalValueFunction,
    PiecewiseLinearValueFunction,
    TotalValueModel,
)


def _sample_problem() -> DecisionProblem:
    criteria = [
        Criterion(id="cost", name="Cost", kind="continuous", min_value=0.0),
        Criterion(id="traction", name="Traction", kind="boolean"),
    ]
    alternatives = [
        Alternative(
            id="a",
            name="A",
            measurements={"cost": 100.0, "traction": True},
        )
    ]
    return DecisionProblem(id="p", name="Problem", criteria=criteria, alternatives=alternatives)


def _sample_problem_with_two_alternatives() -> DecisionProblem:
    criteria = [
        Criterion(id="cost", name="Cost", kind="continuous", min_value=0.0),
        Criterion(id="traction", name="Traction", kind="boolean"),
    ]
    alternatives = [
        Alternative(
            id="a",
            name="A",
            measurements={"cost": 100.0, "traction": True},
        ),
        Alternative(
            id="b",
            name="B",
            measurements={"cost": 80.0, "traction": False},
        ),
    ]
    return DecisionProblem(id="p-2", name="Problem 2", criteria=criteria, alternatives=alternatives)


def _sample_weights() -> dict[str, float]:
    return {"cost": 60.0, "traction": 40.0}


def _sample_problem_with_ordinal_and_categorical() -> DecisionProblem:
    criteria = [
        Criterion(id="rating", name="Rating", kind="ordinal", allowed_values=(1, 2, 3)),
        Criterion(id="segment", name="Segment", kind="categorical", allowed_values=("A", "B")),
    ]
    alternatives = [
        Alternative(
            id="a",
            name="A",
            measurements={"rating": 2, "segment": "A"},
        )
    ]
    return DecisionProblem(id="p-3", name="Problem 3", criteria=criteria, alternatives=alternatives)


def _sample_problem_with_categorical_only() -> DecisionProblem:
    criteria = [Criterion(id="segment", name="Segment", kind="categorical", allowed_values=("A", "B"))]
    alternatives = [Alternative(id="a", name="A", measurements={"segment": "A"})]
    return DecisionProblem(id="p-4", name="Problem 4", criteria=criteria, alternatives=alternatives)


class _NonNumericValueFunction:
    def __call__(self, _raw_value: object) -> str:
        return "high"


class _OutOfRangeValueFunction:
    def __call__(self, _raw_value: object) -> float:
        return 101.0


def test_total_value_model_allows_exact_mapping_for_paired_problem() -> None:
    problem = _sample_problem()
    model = TotalValueModel(
        id="m",
        name="Model",
        decision_problem=problem,
        criterion_value_functions={
            "cost": LinearIncreasingValueFunction(min_raw_value=0.0, max_raw_value=200.0),
            "traction": MappingCategoricalValueFunction(value_mapping={False: 0.0, True: 100.0}),
        },
        criterion_weights=_sample_weights(),
    )

    assert model.evaluate("cost", 100.0) == 50.0
    assert model.evaluate("traction", True) == 100.0


def test_total_value_model_rejects_unknown_criterion_mapping() -> None:
    problem = _sample_problem()

    with pytest.raises(ValueError, match="unknown criterion ids"):
        TotalValueModel(
            id="m",
            name="Model",
            decision_problem=problem,
            criterion_value_functions={
                "cost": LinearIncreasingValueFunction(min_raw_value=0.0, max_raw_value=200.0),
                "traction": MappingCategoricalValueFunction(value_mapping={False: 0.0, True: 100.0}),
                "unknown": LinearIncreasingValueFunction(min_raw_value=0.0, max_raw_value=1.0),
            },
            criterion_weights=_sample_weights(),
        )


def test_total_value_model_rejects_missing_criterion_mapping() -> None:
    problem = _sample_problem()

    with pytest.raises(ValueError, match="missing value functions"):
        TotalValueModel(
            id="m",
            name="Model",
            decision_problem=problem,
            criterion_value_functions={
                "cost": LinearIncreasingValueFunction(min_raw_value=0.0, max_raw_value=200.0),
            },
            criterion_weights=_sample_weights(),
        )


def test_total_value_model_rejects_non_callable_mapping_value() -> None:
    problem = _sample_problem()

    with pytest.raises(ValueError, match="must be callable"):
        TotalValueModel(
            id="m",
            name="Model",
            decision_problem=problem,
            criterion_value_functions={
                "cost": 1.0,
                "traction": MappingCategoricalValueFunction(value_mapping={False: 0.0, True: 100.0}),
            },
            criterion_weights=_sample_weights(),
        )


def test_total_value_model_rejects_mapping_value_function_for_continuous_criterion() -> None:
    problem = _sample_problem()

    with pytest.raises(ValueError, match="cannot use a mapping value function"):
        TotalValueModel(
            id="m",
            name="Model",
            decision_problem=problem,
            criterion_value_functions={
                "cost": MappingCategoricalValueFunction(value_mapping={"low": 0.0, "high": 100.0}),
                "traction": MappingCategoricalValueFunction(value_mapping={False: 0.0, True: 100.0}),
            },
            criterion_weights=_sample_weights(),
        )


def test_total_value_model_rejects_non_mapping_value_function_for_categorical_criterion() -> None:
    problem = _sample_problem_with_categorical_only()

    with pytest.raises(ValueError, match="requires a mapping value function"):
        TotalValueModel(
            id="m",
            name="Model",
            decision_problem=problem,
            criterion_value_functions={
                "segment": LinearIncreasingValueFunction(min_raw_value=0.0, max_raw_value=10.0),
            },
            criterion_weights={"segment": 100.0},
        )


def test_total_value_model_rejects_mapping_with_missing_allowed_values_for_ordinal_criterion() -> None:
    problem = _sample_problem_with_ordinal_and_categorical()

    with pytest.raises(ValueError, match="missing allowed_values entries"):
        TotalValueModel(
            id="m",
            name="Model",
            decision_problem=problem,
            criterion_value_functions={
                "rating": MappingCategoricalValueFunction(value_mapping={1: 0.0, 3: 100.0}),
                "segment": MappingCategoricalValueFunction(value_mapping={"A": 0.0, "B": 100.0}),
            },
            criterion_weights={"rating": 50.0, "segment": 50.0},
        )


def test_total_value_model_rejects_mapping_with_unknown_allowed_values_for_categorical_criterion() -> None:
    problem = _sample_problem_with_ordinal_and_categorical()

    with pytest.raises(ValueError, match="not present in allowed_values"):
        TotalValueModel(
            id="m",
            name="Model",
            decision_problem=problem,
            criterion_value_functions={
                "rating": PiecewiseLinearValueFunction(points=((1.0, 0.0), (3.0, 100.0))),
                "segment": MappingCategoricalValueFunction(value_mapping={"A": 0.0, "B": 100.0, "C": 50.0}),
            },
            criterion_weights={"rating": 50.0, "segment": 50.0},
        )


def test_total_value_model_evaluates_raw_feasibility_rules() -> None:
    problem = _sample_problem()
    model = TotalValueModel(
        id="m",
        name="Model",
        decision_problem=problem,
        criterion_value_functions={
            "cost": LinearIncreasingValueFunction(min_raw_value=0.0, max_raw_value=200.0),
            "traction": MappingCategoricalValueFunction(value_mapping={False: 0.0, True: 100.0}),
        },
        criterion_weights=_sample_weights(),
        feasibility_rules=(
            FeasibilityRule(
                id="traction_required",
                name="Traction required",
                criterion_id="traction",
                predicate=lambda raw_value: raw_value is True,
            ),
        ),
    )

    assert model.passes_raw_feasibility({"cost": 100.0, "traction": True}) is True
    assert model.passes_raw_feasibility({"cost": 100.0, "traction": False}) is False


def test_total_value_model_rejects_duplicate_feasibility_rule_ids() -> None:
    problem = _sample_problem()

    with pytest.raises(ValueError, match="duplicate feasibility rule id"):
        TotalValueModel(
            id="m",
            name="Model",
            decision_problem=problem,
            criterion_value_functions={
                "cost": LinearIncreasingValueFunction(min_raw_value=0.0, max_raw_value=200.0),
                "traction": MappingCategoricalValueFunction(value_mapping={False: 0.0, True: 100.0}),
            },
            criterion_weights=_sample_weights(),
            feasibility_rules=(
                FeasibilityRule(
                    id="rule-1",
                    name="Rule 1",
                    criterion_id="traction",
                    predicate=lambda raw_value: raw_value is True,
                ),
                FeasibilityRule(
                    id="rule-1",
                    name="Rule 1 duplicate",
                    criterion_id="cost",
                    predicate=lambda raw_value: raw_value <= 150.0,
                ),
            ),
        )


def test_total_value_model_rejects_feasibility_rule_with_unknown_criterion_id() -> None:
    problem = _sample_problem()

    with pytest.raises(ValueError, match="references unknown criterion id"):
        TotalValueModel(
            id="m",
            name="Model",
            decision_problem=problem,
            criterion_value_functions={
                "cost": LinearIncreasingValueFunction(min_raw_value=0.0, max_raw_value=200.0),
                "traction": MappingCategoricalValueFunction(value_mapping={False: 0.0, True: 100.0}),
            },
            criterion_weights=_sample_weights(),
            feasibility_rules=(
                FeasibilityRule(
                    id="rule-1",
                    name="Rule 1",
                    criterion_id="unknown",
                    predicate=lambda _raw_value: True,
                ),
            ),
        )


def test_total_value_model_rejects_unknown_weight_criterion() -> None:
    problem = _sample_problem()

    with pytest.raises(ValueError, match="unknown weighted criterion ids"):
        TotalValueModel(
            id="m",
            name="Model",
            decision_problem=problem,
            criterion_value_functions={
                "cost": LinearIncreasingValueFunction(min_raw_value=0.0, max_raw_value=200.0),
                "traction": MappingCategoricalValueFunction(value_mapping={False: 0.0, True: 100.0}),
            },
            criterion_weights={"cost": 60.0, "traction": 40.0, "unknown": 10.0},
        )


def test_total_value_model_rejects_missing_weight_criterion() -> None:
    problem = _sample_problem()

    with pytest.raises(ValueError, match="missing criterion weights"):
        TotalValueModel(
            id="m",
            name="Model",
            decision_problem=problem,
            criterion_value_functions={
                "cost": LinearIncreasingValueFunction(min_raw_value=0.0, max_raw_value=200.0),
                "traction": MappingCategoricalValueFunction(value_mapping={False: 0.0, True: 100.0}),
            },
            criterion_weights={"cost": 100.0},
        )


def test_total_value_model_rejects_out_of_range_weight() -> None:
    problem = _sample_problem()

    with pytest.raises(ValueError, match="must be between 0 and 100"):
        TotalValueModel(
            id="m",
            name="Model",
            decision_problem=problem,
            criterion_value_functions={
                "cost": LinearIncreasingValueFunction(min_raw_value=0.0, max_raw_value=200.0),
                "traction": MappingCategoricalValueFunction(value_mapping={False: 0.0, True: 100.0}),
            },
            criterion_weights={"cost": 101.0, "traction": 40.0},
        )


def test_total_value_model_rejects_non_numeric_weight() -> None:
    problem = _sample_problem()

    with pytest.raises(ValueError, match="must be numeric"):
        TotalValueModel(
            id="m",
            name="Model",
            decision_problem=problem,
            criterion_value_functions={
                "cost": LinearIncreasingValueFunction(min_raw_value=0.0, max_raw_value=200.0),
                "traction": MappingCategoricalValueFunction(value_mapping={False: 0.0, True: 100.0}),
            },
            criterion_weights={"cost": "high", "traction": 40.0},
        )


def test_total_value_model_rejects_boolean_weight() -> None:
    problem = _sample_problem()

    with pytest.raises(ValueError, match="must be numeric"):
        TotalValueModel(
            id="m",
            name="Model",
            decision_problem=problem,
            criterion_value_functions={
                "cost": LinearIncreasingValueFunction(min_raw_value=0.0, max_raw_value=200.0),
                "traction": MappingCategoricalValueFunction(value_mapping={False: 0.0, True: 100.0}),
            },
            criterion_weights={"cost": True, "traction": 40.0},
        )


def test_total_value_model_rejects_all_zero_weights() -> None:
    problem = _sample_problem()

    with pytest.raises(ValueError, match="at least one positive weight"):
        TotalValueModel(
            id="m",
            name="Model",
            decision_problem=problem,
            criterion_value_functions={
                "cost": LinearIncreasingValueFunction(min_raw_value=0.0, max_raw_value=200.0),
                "traction": MappingCategoricalValueFunction(value_mapping={False: 0.0, True: 100.0}),
            },
            criterion_weights={"cost": 0.0, "traction": 0.0},
        )


def test_total_value_model_normalized_weights_sum_to_one() -> None:
    problem = _sample_problem()
    model = TotalValueModel(
        id="m",
        name="Model",
        decision_problem=problem,
        criterion_value_functions={
            "cost": LinearIncreasingValueFunction(min_raw_value=0.0, max_raw_value=200.0),
            "traction": MappingCategoricalValueFunction(value_mapping={False: 0.0, True: 100.0}),
        },
        criterion_weights={"cost": 30.0, "traction": 70.0},
    )

    normalized = model.normalized_weights()
    assert sum(normalized.values()) == pytest.approx(1.0)
    assert normalized["cost"] == pytest.approx(0.3)
    assert normalized["traction"] == pytest.approx(0.7)


def test_total_value_model_scores_solution_with_contributions() -> None:
    problem = _sample_problem()
    model = TotalValueModel(
        id="m",
        name="Model",
        decision_problem=problem,
        criterion_value_functions={
            "cost": LinearIncreasingValueFunction(min_raw_value=0.0, max_raw_value=200.0),
            "traction": MappingCategoricalValueFunction(value_mapping={False: 0.0, True: 100.0}),
        },
        criterion_weights={"cost": 30.0, "traction": 70.0},
    )

    score = model.score_raw_measurements({"cost": 100.0, "traction": True})
    assert score.criterion_value_scores["cost"] == pytest.approx(50.0)
    assert score.criterion_value_scores["traction"] == pytest.approx(100.0)
    assert score.criterion_weighted_contributions["cost"] == pytest.approx(15.0)
    assert score.criterion_weighted_contributions["traction"] == pytest.approx(70.0)
    assert score.total_score == pytest.approx(85.0)
    assert 0.0 <= score.total_score <= 100.0


def test_total_value_model_rejects_missing_measurement_for_scoring() -> None:
    problem = _sample_problem()
    model = TotalValueModel(
        id="m",
        name="Model",
        decision_problem=problem,
        criterion_value_functions={
            "cost": LinearIncreasingValueFunction(min_raw_value=0.0, max_raw_value=200.0),
            "traction": MappingCategoricalValueFunction(value_mapping={False: 0.0, True: 100.0}),
        },
        criterion_weights={"cost": 30.0, "traction": 70.0},
    )

    with pytest.raises(ValueError, match="missing criterion"):
        model.score_raw_measurements({"cost": 100.0})


def test_total_value_model_rejects_non_numeric_value_score() -> None:
    problem = _sample_problem()
    model = TotalValueModel(
        id="m",
        name="Model",
        decision_problem=problem,
        criterion_value_functions={
            "cost": _NonNumericValueFunction(),
            "traction": MappingCategoricalValueFunction(value_mapping={False: 0.0, True: 100.0}),
        },
        criterion_weights={"cost": 30.0, "traction": 70.0},
    )

    with pytest.raises(ValueError, match="must return a numeric score"):
        model.score_raw_measurements({"cost": 100.0, "traction": True})


def test_total_value_model_rejects_out_of_range_value_score() -> None:
    problem = _sample_problem()
    model = TotalValueModel(
        id="m",
        name="Model",
        decision_problem=problem,
        criterion_value_functions={
            "cost": _OutOfRangeValueFunction(),
            "traction": MappingCategoricalValueFunction(value_mapping={False: 0.0, True: 100.0}),
        },
        criterion_weights={"cost": 30.0, "traction": 70.0},
    )

    with pytest.raises(ValueError, match=r"scores must be in \[0, 100\]"):
        model.score_raw_measurements({"cost": 100.0, "traction": True})


def test_total_value_model_scores_decision_problem_with_all_alternatives() -> None:
    problem = _sample_problem_with_two_alternatives()
    model = TotalValueModel(
        id="m",
        name="Model",
        decision_problem=problem,
        criterion_value_functions={
            "cost": LinearIncreasingValueFunction(min_raw_value=0.0, max_raw_value=200.0),
            "traction": MappingCategoricalValueFunction(value_mapping={False: 0.0, True: 100.0}),
        },
        criterion_weights={"cost": 30.0, "traction": 70.0},
    )

    result = model.score_decision_problem()

    assert result.decision_problem is problem
    assert result.total_value_model is model
    assert [row.alternative_id for row in result.rows] == ["a", "b"]
    assert result.rows[0].criterion_value_scores["cost"] == pytest.approx(50.0)
    assert result.rows[0].criterion_value_scores["traction"] == pytest.approx(100.0)
    assert result.rows[0].total_score == pytest.approx(85.0)
    assert result.rows[0].feasibility_rule_results == {}
    assert result.rows[1].criterion_value_scores["cost"] == pytest.approx(40.0)
    assert result.rows[1].criterion_value_scores["traction"] == pytest.approx(0.0)
    assert result.rows[1].total_score == pytest.approx(12.0)
    assert result.rows[1].feasibility_rule_results == {}


def test_total_value_model_scores_decision_problem_with_per_rule_feasibility_results() -> None:
    problem = _sample_problem_with_two_alternatives()
    model = TotalValueModel(
        id="m",
        name="Model",
        decision_problem=problem,
        criterion_value_functions={
            "cost": LinearIncreasingValueFunction(min_raw_value=0.0, max_raw_value=200.0),
            "traction": MappingCategoricalValueFunction(value_mapping={False: 0.0, True: 100.0}),
        },
        criterion_weights={"cost": 30.0, "traction": 70.0},
        feasibility_rules=(
            FeasibilityRule(
                id="traction_required",
                name="Traction required",
                criterion_id="traction",
                predicate=lambda raw_value: raw_value is True,
            ),
        ),
    )

    result = model.score_decision_problem()

    assert [row.alternative_id for row in result.rows] == ["a", "b"]
    assert result.rows[0].feasibility_rule_results == {"traction_required": True}
    assert result.rows[1].feasibility_rule_results == {"traction_required": False}
