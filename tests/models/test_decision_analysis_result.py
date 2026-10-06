import pytest

from decision_core import (
    Alternative,
    Criterion,
    DecisionAnalysisResult,
    DecisionAnalysisRow,
    DecisionProblem,
    FeasibilityRule,
    LinearIncreasingValueFunction,
    MappingCategoricalValueFunction,
    TotalValueModel,
)


def _sample_problem() -> DecisionProblem:
    criteria = [
        Criterion(id="cost", name="Cost", kind="continuous", min_value=0.0),
        Criterion(id="traction", name="Traction", kind="boolean"),
    ]
    alternatives = [
        Alternative(id="a", name="A", measurements={"cost": 100.0, "traction": True}),
        Alternative(id="b", name="B", measurements={"cost": 80.0, "traction": False}),
    ]
    return DecisionProblem(id="p", name="Problem", criteria=criteria, alternatives=alternatives)


def _sample_model(problem: DecisionProblem) -> TotalValueModel:
    return TotalValueModel(
        id="m",
        name="Model",
        decision_problem=problem,
        criterion_value_functions={
            "cost": LinearIncreasingValueFunction(min_raw_value=0.0, max_raw_value=200.0),
            "traction": MappingCategoricalValueFunction(value_mapping={False: 0.0, True: 100.0}),
        },
        criterion_weights={"cost": 60.0, "traction": 40.0},
    )


def _sample_model_with_rules(problem: DecisionProblem) -> TotalValueModel:
    return TotalValueModel(
        id="m-rules",
        name="Model With Rules",
        decision_problem=problem,
        criterion_value_functions={
            "cost": LinearIncreasingValueFunction(min_raw_value=0.0, max_raw_value=200.0),
            "traction": MappingCategoricalValueFunction(value_mapping={False: 0.0, True: 100.0}),
        },
        criterion_weights={"cost": 60.0, "traction": 40.0},
        feasibility_rules=(
            FeasibilityRule(
                id="traction_required",
                name="Traction required",
                criterion_id="traction",
                predicate=lambda raw_value: raw_value is True,
            ),
        ),
    )


def test_decision_analysis_result_accepts_valid_rows_and_keeps_traceability() -> None:
    problem = _sample_problem()
    model = _sample_model(problem)
    rows = [
        DecisionAnalysisRow(
            alternative_id="a",
            criterion_value_scores={"cost": 50.0, "traction": 100.0},
            total_score=70.0,
            feasibility_rule_results={},
        ),
        DecisionAnalysisRow(
            alternative_id="b",
            criterion_value_scores={"cost": 40.0, "traction": 0.0},
            total_score=24.0,
            feasibility_rule_results={},
        ),
    ]

    result = DecisionAnalysisResult(decision_problem=problem, total_value_model=model, rows=rows)

    assert result.decision_problem is problem
    assert result.total_value_model is model
    assert len(result.rows) == 2


def test_decision_analysis_result_rejects_duplicate_alternative_rows() -> None:
    problem = _sample_problem()
    model = _sample_model(problem)

    with pytest.raises(ValueError, match="duplicate alternative row"):
        DecisionAnalysisResult(
            decision_problem=problem,
            total_value_model=model,
            rows=(
                DecisionAnalysisRow(
                    alternative_id="a",
                    criterion_value_scores={"cost": 50.0, "traction": 100.0},
                    total_score=70.0,
                    feasibility_rule_results={},
                ),
                DecisionAnalysisRow(
                    alternative_id="a",
                    criterion_value_scores={"cost": 40.0, "traction": 0.0},
                    total_score=24.0,
                    feasibility_rule_results={},
                ),
            ),
        )


def test_decision_analysis_result_rejects_unknown_alternative_id() -> None:
    problem = _sample_problem()
    model = _sample_model(problem)

    with pytest.raises(ValueError, match="is not part of the linked DecisionProblem"):
        DecisionAnalysisResult(
            decision_problem=problem,
            total_value_model=model,
            rows=(
                DecisionAnalysisRow(
                    alternative_id="unknown",
                    criterion_value_scores={"cost": 50.0, "traction": 100.0},
                    total_score=70.0,
                    feasibility_rule_results={},
                ),
            ),
        )


def test_decision_analysis_result_rejects_missing_or_unknown_criterion_ids() -> None:
    problem = _sample_problem()
    model = _sample_model(problem)

    with pytest.raises(ValueError, match="missing criterion ids"):
        DecisionAnalysisResult(
            decision_problem=problem,
            total_value_model=model,
            rows=(
                DecisionAnalysisRow(
                    alternative_id="a",
                    criterion_value_scores={"cost": 50.0},
                    total_score=70.0,
                    feasibility_rule_results={},
                ),
            ),
        )

    with pytest.raises(ValueError, match="unknown criterion ids"):
        DecisionAnalysisResult(
            decision_problem=problem,
            total_value_model=model,
            rows=(
                DecisionAnalysisRow(
                    alternative_id="a",
                    criterion_value_scores={"cost": 50.0, "traction": 100.0, "unknown": 12.0},
                    total_score=70.0,
                    feasibility_rule_results={},
                ),
            ),
        )


def test_decision_analysis_result_rejects_missing_or_unknown_feasibility_rule_ids() -> None:
    problem = _sample_problem()
    model = _sample_model_with_rules(problem)

    with pytest.raises(ValueError, match="missing feasibility rule ids"):
        DecisionAnalysisResult(
            decision_problem=problem,
            total_value_model=model,
            rows=(
                DecisionAnalysisRow(
                    alternative_id="a",
                    criterion_value_scores={"cost": 50.0, "traction": 100.0},
                    total_score=70.0,
                    feasibility_rule_results={},
                ),
            ),
        )

    with pytest.raises(ValueError, match="unknown feasibility rule ids"):
        DecisionAnalysisResult(
            decision_problem=problem,
            total_value_model=model,
            rows=(
                DecisionAnalysisRow(
                    alternative_id="a",
                    criterion_value_scores={"cost": 50.0, "traction": 100.0},
                    total_score=70.0,
                    feasibility_rule_results={"traction_required": True, "unknown": False},
                ),
            ),
        )


def test_decision_analysis_result_rejects_empty_rows() -> None:
    problem = _sample_problem()
    model = _sample_model(problem)

    with pytest.raises(ValueError, match="at least one row"):
        DecisionAnalysisResult(decision_problem=problem, total_value_model=model, rows=())


def test_decision_analysis_row_rejects_non_numeric_or_out_of_range_scores() -> None:
    with pytest.raises(ValueError, match="must be numeric"):
        DecisionAnalysisRow(
            alternative_id="a",
            criterion_value_scores={"cost": "high"},
            total_score=50.0,
            feasibility_rule_results={},
        )

    with pytest.raises(ValueError, match="must be between 0 and 100"):
        DecisionAnalysisRow(
            alternative_id="a",
            criterion_value_scores={"cost": 101.0},
            total_score=50.0,
            feasibility_rule_results={},
        )

    with pytest.raises(ValueError, match="total_score must be between 0 and 100"):
        DecisionAnalysisRow(
            alternative_id="a",
            criterion_value_scores={"cost": 50.0},
            total_score=120.0,
            feasibility_rule_results={},
        )


def test_decision_analysis_row_rejects_non_boolean_feasibility_results() -> None:
    with pytest.raises(ValueError, match="must be a boolean"):
        DecisionAnalysisRow(
            alternative_id="a",
            criterion_value_scores={"cost": 50.0},
            total_score=40.0,
            feasibility_rule_results={"traction_required": 1},
        )