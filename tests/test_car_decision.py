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

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import pytest


def _load_car_decision_module():
    script_path = Path(__file__).resolve().parents[1] / "CarDecision.py"
    spec = spec_from_file_location("car_decision", script_path)
    assert spec is not None and spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_honda_odyssey_ex_l_is_present_and_infeasible_by_raw_rules() -> None:
    module = _load_car_decision_module()

    odyssey_row = next(row for row in module.RAW_MATRIX if row["Alternative"] == "Honda Odyssey EX-L")
    assert odyssey_row["Apps"] == "None"
    rule_ids = {rule.id for rule in module.TOTAL_VALUE_MODEL.feasibility_rules}
    assert rule_ids == {
        "requires_traction_control",
        "apps_must_not_be_none",
        "rollover_rating_minimum",
    }
    assert module.passes_raw_feasibility_rules(odyssey_row) is False


def test_build_value_score_matrix_includes_feasibility_results() -> None:
    module = _load_car_decision_module()

    criterion_ids = {criterion.id for criterion in module.CAR_DECISION_PROBLEM.criteria}
    model_ids = set(module.TOTAL_VALUE_MODEL.criterion_value_functions.keys())
    weight_ids = set(module.TOTAL_VALUE_MODEL.criterion_weights.keys())
    assert model_ids == criterion_ids
    assert weight_ids == criterion_ids
    assert len(module.TOTAL_VALUE_MODEL.feasibility_rules) == 3

    decision_result = module.TOTAL_VALUE_MODEL.score_decision_problem()
    result_alternative_ids = {row.alternative_id for row in decision_result.rows}
    assert "Honda Odyssey EX-L" in result_alternative_ids
    assert len(decision_result.rows) == 10

    odyssey_result_row = next(
        row for row in decision_result.rows if row.alternative_id == "Honda Odyssey EX-L"
    )
    assert odyssey_result_row.feasibility_rule_results == {
        "requires_traction_control": True,
        "apps_must_not_be_none": False,
        "rollover_rating_minimum": True,
    }

    for result_row in decision_result.rows:
        assert set(result_row.criterion_value_scores.keys()) == criterion_ids
        assert set(result_row.feasibility_rule_results.keys()) == {
            "requires_traction_control",
            "apps_must_not_be_none",
            "rollover_rating_minimum",
        }
        assert 0.0 <= result_row.total_score <= 100.0

    matrix = module.build_value_score_matrix()
    alternatives = {str(row["Alternative"]) for row in matrix}
    feasibility_rule_ids = [rule.id for rule in module.TOTAL_VALUE_MODEL.feasibility_rules]

    assert "Honda Odyssey EX-L" in alternatives
    assert len(matrix) == 10
    for scored_row, result_row in zip(matrix, decision_result.rows):
        assert str(scored_row["Alternative"]) == result_row.alternative_id
        assert "Total Score" in scored_row
        assert float(scored_row["Total Score"]) == result_row.total_score
        for rule_id in feasibility_rule_ids:
            assert rule_id in scored_row
            assert bool(scored_row[rule_id]) == result_row.feasibility_rule_results[rule_id]
        assert 0.0 <= float(scored_row["Total Score"]) <= 100.0


def test_print_value_score_matrix_includes_feasibility_columns(capsys) -> None:
    module = _load_car_decision_module()
    matrix = module.build_value_score_matrix()

    module.print_value_score_matrix(matrix)
    output_lines = capsys.readouterr().out.strip().splitlines()

    header = output_lines[0].split(",")
    assert header[-3:] == [
        "requires_traction_control",
        "apps_must_not_be_none",
        "rollover_rating_minimum",
    ]

    odyssey_line = next(line for line in output_lines if line.startswith("Honda Odyssey EX-L,"))
    assert odyssey_line.endswith(",True,False,True")


def test_build_decision_analysis_figure_returns_weighted_stacked_bars() -> None:
    pytest.importorskip("plotly")
    module = _load_car_decision_module()

    decision_result = module.TOTAL_VALUE_MODEL.score_decision_problem()
    figure = module.build_decision_analysis_figure(decision_result)

    criterion_ids = [criterion.id for criterion in module.CAR_DECISION_PROBLEM.criteria]
    criterion_names = [criterion.name for criterion in module.CAR_DECISION_PROBLEM.criteria]
    normalized_weights = decision_result.total_value_model.normalized_weights()
    infeasible_alternative_ids = {
        row.alternative_id
        for row in decision_result.rows
        if not all(row.feasibility_rule_results.values())
    }

    assert len(figure.data) == len(criterion_ids) + 1
    assert figure.layout.barmode == "stack"
    assert tuple(figure.layout.yaxis.range) == (0, 100)

    alternatives = module.CAR_DECISION_PROBLEM.alternatives
    expected_x = [alternative.name for alternative in alternatives]
    rows_by_alternative_id = {row.alternative_id: row for row in decision_result.rows}

    for trace, criterion_id, criterion_name in zip(
        figure.data[: len(criterion_ids)], criterion_ids, criterion_names
    ):
        assert trace.name == criterion_name
        assert list(trace.x) == expected_x
        for alternative, value in zip(alternatives, trace.y):
            if alternative.id in infeasible_alternative_ids:
                expected_value = 0.0
            else:
                expected_value = (
                    rows_by_alternative_id[alternative.id].criterion_value_scores[criterion_id]
                    * normalized_weights[criterion_id]
                )
            assert 0.0 <= float(value) <= 100.0
            assert float(value) == expected_value

    for alternative_index, alternative in enumerate(alternatives):
        stacked_total = sum(
            float(trace.y[alternative_index]) for trace in figure.data[: len(criterion_ids)]
        )
        if alternative.id in infeasible_alternative_ids:
            expected_total = 0.0
        else:
            expected_total = rows_by_alternative_id[alternative.id].total_score
        assert stacked_total == expected_total

    infeasible_trace = figure.data[-1]
    assert infeasible_trace.name == "Infeasible"
    assert list(infeasible_trace.x) == ["Honda Odyssey EX-L"]
    assert list(infeasible_trace.y) == [0.0]
    assert list(infeasible_trace.text) == ["Infeasible: Apps"]
