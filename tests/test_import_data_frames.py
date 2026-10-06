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

import pandas as pd
import pytest

from import_data_frames import (
    build_alternatives_from_data_frame,
    build_criteria_from_data_frame,
    build_criterion_weights_from_data_frame,
    build_default_feasibility_predicate_registry,
    build_decision_problem,
    build_feasibility_rules_from_data_frame,
    build_value_functions_from_specs,
    validate_input_shapes,
)


def _criteria_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "id": "stopping_distance",
                "name": "Stopping Distance",
                "kind": "continuous",
                "min_value": 0.0,
                "max_value": None,
                "allowed_values": None,
            },
            {
                "id": "airbags",
                "name": "Airbags",
                "kind": "integer",
                "min_value": 0,
                "max_value": None,
                "allowed_values": None,
            },
            {
                "id": "rollover_rating",
                "name": "Rollover Rating",
                "kind": "ordinal",
                "min_value": None,
                "max_value": None,
                "allowed_values": [1, 2, 3, 4, 5],
            },
            {
                "id": "apps",
                "name": "Apps",
                "kind": "categorical",
                "min_value": None,
                "max_value": None,
                "allowed_values": ["None", "Subscription", "Wired Car Play", "Wireless Car Play"],
            },
            {
                "id": "cargo_space",
                "name": "Cargo space",
                "kind": "continuous",
                "min_value": 0.0,
                "max_value": None,
                "allowed_values": None,
            },
            {
                "id": "traction_control",
                "name": "Traction Control",
                "kind": "boolean",
                "min_value": None,
                "max_value": None,
                "allowed_values": None,
            },
            {
                "id": "rear_legroom",
                "name": "Rear Legroom",
                "kind": "continuous",
                "min_value": 0.0,
                "max_value": None,
                "allowed_values": None,
            },
            {
                "id": "crash_ratings",
                "name": "Crash Ratings",
                "kind": "ordinal",
                "min_value": None,
                "max_value": None,
                "allowed_values": [1, 2, 3, 4, 5],
            },
        ]
    )


def _raw_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "id": "cadillac_srx",
                "name": "Cadillac SRX Luxury 4WD",
                "stopping_distance": 119.0,
                "airbags": 6,
                "rollover_rating": 4,
                "apps": "Subscription",
                "cargo_space": 29.8,
                "traction_control": True,
                "rear_legroom": 36.0,
                "crash_ratings": 5,
            },
            {
                "id": "acura_rdx",
                "name": "Acura RDX SH 4WD",
                "stopping_distance": 125.0,
                "airbags": 6,
                "rollover_rating": 4,
                "apps": "Wireless Car Play",
                "cargo_space": 28.0,
                "traction_control": True,
                "rear_legroom": 37.6,
                "crash_ratings": 5,
            },
            {
                "id": "honda_crv",
                "name": "Honda CR-V EX-L 4WD",
                "stopping_distance": 119.0,
                "airbags": 6,
                "rollover_rating": 4,
                "apps": "Wireless Car Play",
                "cargo_space": 35.7,
                "traction_control": True,
                "rear_legroom": 38.5,
                "crash_ratings": 5,
            },
            {
                "id": "toyota_rav4",
                "name": "Toyota RAV4",
                "stopping_distance": 130.0,
                "airbags": 6,
                "rollover_rating": 4,
                "apps": "Subscription",
                "cargo_space": 36.4,
                "traction_control": True,
                "rear_legroom": 38.3,
                "crash_ratings": 5,
            },
            {
                "id": "volvo_xc60",
                "name": "Volvo XC-60",
                "stopping_distance": 123.0,
                "airbags": 6,
                "rollover_rating": 4,
                "apps": "Wireless Car Play",
                "cargo_space": 30.8,
                "traction_control": True,
                "rear_legroom": 36.4,
                "crash_ratings": 5,
            },
            {
                "id": "lexus_rx_350",
                "name": "Lexus RX 350 AWD",
                "stopping_distance": 130.0,
                "airbags": 10,
                "rollover_rating": 4,
                "apps": "Wireless Car Play",
                "cargo_space": 40.0,
                "traction_control": True,
                "rear_legroom": 36.8,
                "crash_ratings": 5,
            },
            {
                "id": "mitsubishi_outlander",
                "name": "Mitsubishi Outlander",
                "stopping_distance": 141.0,
                "airbags": 8,
                "rollover_rating": 4,
                "apps": "Wireless Car Play",
                "cargo_space": 36.2,
                "traction_control": True,
                "rear_legroom": 39.6,
                "crash_ratings": 5,
            },
            {
                "id": "lexus_rx_350_2009",
                "name": "Lexus RX 350 AWD (2009)",
                "stopping_distance": 130.0,
                "airbags": 10,
                "rollover_rating": 4,
                "apps": "Wireless Car Play",
                "cargo_space": 40.0,
                "traction_control": True,
                "rear_legroom": 36.8,
                "crash_ratings": 5,
            },
            {
                "id": "honda_crv_2009",
                "name": "Honda CR-V EX-L 4WD (2009)",
                "stopping_distance": 119.0,
                "airbags": 6,
                "rollover_rating": 4,
                "apps": "Subscription",
                "cargo_space": 35.7,
                "traction_control": True,
                "rear_legroom": 38.5,
                "crash_ratings": 5,
            },
            {
                "id": "honda_odyssey",
                "name": "Honda Odyssey EX-L",
                "stopping_distance": 147.0,
                "airbags": 8,
                "rollover_rating": 4,
                "apps": "None",
                "cargo_space": 38.4,
                "traction_control": True,
                "rear_legroom": 40.9,
                "crash_ratings": 5,
            },
        ]
    )


def _value_function_specs() -> dict[str, dict[str, object]]:
    return {
        "stopping_distance": {"type": "linear_decreasing", "min_raw_value": 100.0, "max_raw_value": 150.0},
        "airbags": {
            "type": "piecewise_linear",
            "points": [(2.0, 10.0), (4.0, 20.0), (6.0, 80.0), (8.0, 100.0), (10.0, 100.0)],
        },
        "rollover_rating": {"type": "mapping", "value_mapping": {1: 0.0, 2: 0.0, 3: 10.0, 4: 50.0, 5: 100.0}},
        "apps": {
            "type": "mapping",
            "value_mapping": {
                "None": 0.0,
                "Subscription": 30.0,
                "Wired Car Play": 60.0,
                "Wireless Car Play": 100.0,
            },
        },
        "cargo_space": {"type": "linear_increasing", "min_raw_value": 25.0, "max_raw_value": 50.0},
        "traction_control": {"type": "mapping", "value_mapping": {False: 0.0, True: 100.0}},
        "rear_legroom": {"type": "linear_increasing", "min_raw_value": 30.0, "max_raw_value": 40.0},
        "crash_ratings": {"type": "mapping", "value_mapping": {1: 0.0, 2: 0.0, 3: 10.0, 4: 50.0, 5: 100.0}},
    }


def _weights_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"criterion_id": "stopping_distance", "weight": 100.0},
            {"criterion_id": "airbags", "weight": 100.0},
            {"criterion_id": "rollover_rating", "weight": 75.0},
            {"criterion_id": "apps", "weight": 75.0},
            {"criterion_id": "cargo_space", "weight": 75.0},
            {"criterion_id": "traction_control", "weight": 0.0},
            {"criterion_id": "rear_legroom", "weight": 50.0},
            {"criterion_id": "crash_ratings", "weight": 50.0},
        ]
    )


def _feasibility_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "id": "requires_traction_control",
                "name": "Requires traction control",
                "criterion_id": "traction_control",
                "predicate_kind": "requires_true",
                "predicate_param": None,
            },
            {
                "id": "apps_must_not_be_none",
                "name": "Apps must not be None",
                "criterion_id": "apps",
                "predicate_kind": "not_equal",
                "predicate_param": "None",
            },
            {
                "id": "rollover_rating_minimum",
                "name": "Rollover rating must be at least 4",
                "criterion_id": "rollover_rating",
                "predicate_kind": "gte",
                "predicate_param": 4.0,
            },
        ]
    )


def test_validate_input_shapes_accepts_notebook_input_frames() -> None:
    errors = validate_input_shapes(_criteria_df(), _raw_df(), _weights_df(), _value_function_specs())

    assert errors == []


def test_validate_input_shapes_reports_missing_raw_column() -> None:
    raw_df = _raw_df().drop(columns=["apps"])

    errors = validate_input_shapes(_criteria_df(), raw_df, _weights_df(), _value_function_specs())

    assert errors == [
        {
            "stage": "raw",
            "row_or_key": "table",
            "field": "criteria columns",
            "message": "Missing measurement columns: apps",
        }
    ]


def test_builders_construct_decision_problem_value_functions_and_weights_from_data_frames() -> None:
    criteria = build_criteria_from_data_frame(_criteria_df())
    alternatives = build_alternatives_from_data_frame(criteria, _raw_df())
    problem = build_decision_problem(criteria, alternatives)
    value_functions = build_value_functions_from_specs(_value_function_specs())
    weights = build_criterion_weights_from_data_frame(_weights_df())

    assert len(criteria) == 8
    assert len(alternatives) == 10
    assert len(problem.criteria) == 8
    assert len(problem.alternatives) == 10
    assert set(value_functions.keys()) == {criterion.id for criterion in criteria}
    assert set(weights.keys()) == {criterion.id for criterion in criteria}
    assert weights["traction_control"] == 0.0


def test_build_criteria_parses_allowed_values_from_string_literal() -> None:
    criteria_df = _criteria_df()
    criteria_df.loc[criteria_df["id"] == "apps", "allowed_values"] = "['None', 'Subscription']"

    criteria = build_criteria_from_data_frame(criteria_df)
    apps = next(criterion for criterion in criteria if criterion.id == "apps")

    assert apps.allowed_values == ("None", "Subscription")


def test_build_value_functions_rejects_unknown_type() -> None:
    specs = _value_function_specs()
    specs["apps"] = {"type": "unknown"}

    with pytest.raises(ValueError, match="Unsupported value-function type"):
        build_value_functions_from_specs(specs)


def test_build_criterion_weights_rejects_non_numeric_weight() -> None:
    weights_df = _weights_df().astype({"weight": object})
    weights_df.loc[weights_df["criterion_id"] == "airbags", "weight"] = "heavy"

    with pytest.raises(ValueError, match="weight must be numeric"):
        build_criterion_weights_from_data_frame(weights_df)


def test_validate_input_shapes_accepts_feasibility_input_frames() -> None:
    errors = validate_input_shapes(
        _criteria_df(),
        _raw_df(),
        _weights_df(),
        _value_function_specs(),
        _feasibility_df(),
        build_default_feasibility_predicate_registry(),
    )

    assert errors == []


def test_validate_input_shapes_reports_missing_feasibility_column() -> None:
    feasibility_df = _feasibility_df().drop(columns=["predicate_kind"])

    errors = validate_input_shapes(
        _criteria_df(),
        _raw_df(),
        _weights_df(),
        _value_function_specs(),
        feasibility_df,
        build_default_feasibility_predicate_registry(),
    )

    assert errors == [
        {
            "stage": "feasibility",
            "row_or_key": "table",
            "field": "predicate_kind",
            "message": "Missing required column.",
        }
    ]


def test_validate_input_shapes_reports_feasibility_unknown_criterion_id() -> None:
    feasibility_df = _feasibility_df().copy()
    feasibility_df.loc[feasibility_df["id"] == "apps_must_not_be_none", "criterion_id"] = "missing_criterion"

    errors = validate_input_shapes(
        _criteria_df(),
        _raw_df(),
        _weights_df(),
        _value_function_specs(),
        feasibility_df,
        build_default_feasibility_predicate_registry(),
    )

    assert errors == [
        {
            "stage": "feasibility",
            "row_or_key": "apps_must_not_be_none",
            "field": "criterion_id",
            "message": "Unknown criterion id: missing_criterion",
        }
    ]


def test_validate_input_shapes_reports_unsupported_feasibility_predicate_kind() -> None:
    feasibility_df = _feasibility_df().copy()
    feasibility_df.loc[feasibility_df["id"] == "rollover_rating_minimum", "predicate_kind"] = "lt"

    errors = validate_input_shapes(
        _criteria_df(),
        _raw_df(),
        _weights_df(),
        _value_function_specs(),
        feasibility_df,
        build_default_feasibility_predicate_registry(),
    )

    assert errors == [
        {
            "stage": "feasibility",
            "row_or_key": "rollover_rating_minimum",
            "field": "predicate_kind",
            "message": "Unsupported predicate kind: lt",
        }
    ]


def test_validate_input_shapes_reports_malformed_feasibility_predicate_parameter() -> None:
    feasibility_df = _feasibility_df().copy()
    feasibility_df.loc[feasibility_df["id"] == "rollover_rating_minimum", "predicate_param"] = "not-a-number"

    errors = validate_input_shapes(
        _criteria_df(),
        _raw_df(),
        _weights_df(),
        _value_function_specs(),
        feasibility_df,
        build_default_feasibility_predicate_registry(),
    )

    assert len(errors) == 1
    assert errors[0]["stage"] == "feasibility"
    assert errors[0]["row_or_key"] == "rollover_rating_minimum"
    assert errors[0]["field"] == "predicate_param"
    assert "Invalid predicate parameter for kind 'gte'" in errors[0]["message"]


def test_build_feasibility_rules_constructs_car_decision_predicates() -> None:
    rules = build_feasibility_rules_from_data_frame(
        _feasibility_df(),
        build_default_feasibility_predicate_registry(),
    )

    assert [rule.id for rule in rules] == [
        "requires_traction_control",
        "apps_must_not_be_none",
        "rollover_rating_minimum",
    ]

    by_rule_id = {rule.id: rule for rule in rules}
    assert by_rule_id["requires_traction_control"].evaluate({"traction_control": True}) is True
    assert by_rule_id["requires_traction_control"].evaluate({"traction_control": False}) is False
    assert by_rule_id["apps_must_not_be_none"].evaluate({"apps": "Wireless Car Play"}) is True
    assert by_rule_id["apps_must_not_be_none"].evaluate({"apps": "None"}) is False
    assert by_rule_id["rollover_rating_minimum"].evaluate({"rollover_rating": 4}) is True
    assert by_rule_id["rollover_rating_minimum"].evaluate({"rollover_rating": 3.5}) is False
