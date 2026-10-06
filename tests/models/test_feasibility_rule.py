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

from decision_core import FeasibilityRule


def test_feasibility_rule_evaluates_raw_measurements() -> None:
    rule = FeasibilityRule(
        id="traction_required",
        name="Traction required",
        criterion_id="traction_control",
        predicate=lambda raw_value: raw_value is True,
    )

    assert rule.evaluate({"traction_control": True}) is True
    assert rule.evaluate({"traction_control": False}) is False


def test_feasibility_rule_rejects_non_callable_predicate() -> None:
    with pytest.raises(ValueError, match="predicate must be callable"):
        FeasibilityRule(id="r", name="Rule", criterion_id="traction_control", predicate=True)


def test_feasibility_rule_rejects_missing_criterion_id() -> None:
    with pytest.raises(ValueError, match="criterion_id must be a non-empty string"):
        FeasibilityRule(id="r", name="Rule", criterion_id="", predicate=lambda _raw_value: True)


def test_feasibility_rule_rejects_missing_measurement_for_linked_criterion() -> None:
    rule = FeasibilityRule(
        id="traction_required",
        name="Traction required",
        criterion_id="traction_control",
        predicate=lambda raw_value: raw_value is True,
    )

    with pytest.raises(ValueError, match="is missing from measurements"):
        rule.evaluate({})


def test_feasibility_rule_rejects_non_boolean_predicate_result() -> None:
    rule = FeasibilityRule(
        id="bad_result",
        name="Bad result",
        criterion_id="traction_control",
        predicate=lambda _raw_value: 1,
    )

    with pytest.raises(ValueError, match="must return a boolean"):
        rule.evaluate({"traction_control": True})
