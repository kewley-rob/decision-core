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

from decision_core import Alternative, Criterion, DecisionProblem


def test_decision_problem_allows_valid_values() -> None:
    criteria = [
        Criterion(id="stopping_distance", name="Stopping Distance", kind="continuous", min_value=0.0),
        Criterion(id="airbags", name="Airbags", kind="integer", min_value=0),
        Criterion(id="traction_control", name="Traction Control", kind="boolean"),
        Criterion(id="crash_safety", name="Crash Safety", kind="ordinal", allowed_values=(1, 2, 3, 4, 5)),
        Criterion(
            id="stereo",
            name="Stereo",
            kind="categorical",
            allowed_values=("Ultra", "Premium", "Standard", "Poor"),
        ),
    ]
    alternatives = [
        Alternative(
            id="alt-a",
            name="Alternative A",
            measurements={
                "stopping_distance": 130.5,
                "airbags": 6,
                "traction_control": True,
                "crash_safety": 4,
                "stereo": "Premium",
            },
        ),
        Alternative(
            id="alt-b",
            name="Alternative B",
            measurements={
                "stopping_distance": 126.0,
                "airbags": 8,
                "traction_control": False,
                "crash_safety": 5,
                "stereo": "Ultra",
            },
        ),
    ]

    problem = DecisionProblem(
        id="buy-laptop",
        name="Choose laptop",
        criteria=criteria,
        alternatives=alternatives,
    )

    assert problem.id == "buy-laptop"
    assert problem.name == "Choose laptop"
    assert [criterion.id for criterion in problem.criteria] == [
        "stopping_distance",
        "airbags",
        "traction_control",
        "crash_safety",
        "stereo",
    ]
    assert [alternative.id for alternative in problem.alternatives] == ["alt-a", "alt-b"]


def test_decision_problem_rejects_duplicate_criterion_ids() -> None:
    criteria = [
        Criterion(id="cost", name="Cost", kind="continuous"),
        Criterion(id="cost", name="Duplicate Cost", kind="continuous"),
    ]
    alternatives = [
        Alternative(id="alt-a", name="Alternative A", measurements={"cost": 1000})
    ]

    with pytest.raises(ValueError, match="criteria must have unique ids"):
        DecisionProblem(
            id="buy-laptop",
            name="Choose laptop",
            criteria=criteria,
            alternatives=alternatives,
        )


def test_decision_problem_rejects_duplicate_alternative_ids() -> None:
    criteria = [Criterion(id="cost", name="Cost", kind="continuous")]
    alternatives = [
        Alternative(id="alt-a", name="Alternative A", measurements={"cost": 1000}),
        Alternative(id="alt-a", name="Alternative A Duplicate", measurements={"cost": 900}),
    ]

    with pytest.raises(ValueError, match="alternatives must have unique ids"):
        DecisionProblem(
            id="buy-laptop",
            name="Choose laptop",
            criteria=criteria,
            alternatives=alternatives,
        )


def test_decision_problem_rejects_unknown_measurement_criterion() -> None:
    criteria = [Criterion(id="cost", name="Cost", kind="continuous")]
    alternatives = [
        Alternative(
            id="alt-a",
            name="Alternative A",
            measurements={"cost": 1000, "quality": 8.0},
        )
    ]

    with pytest.raises(ValueError, match="unknown criteria"):
        DecisionProblem(
            id="buy-laptop",
            name="Choose laptop",
            criteria=criteria,
            alternatives=alternatives,
        )


def test_decision_problem_rejects_missing_measurement_for_required_criterion() -> None:
    criteria = [
        Criterion(id="cost", name="Cost", kind="continuous"),
        Criterion(id="quality", name="Quality", kind="continuous"),
    ]
    alternatives = [
        Alternative(id="alt-a", name="Alternative A", measurements={"cost": 1000})
    ]

    with pytest.raises(ValueError, match="missing measurements"):
        DecisionProblem(
            id="buy-laptop",
            name="Choose laptop",
            criteria=criteria,
            alternatives=alternatives,
        )


def test_decision_problem_rejects_invalid_typed_measurement_value() -> None:
    criteria = [
        Criterion(id="airbags", name="Airbags", kind="integer", min_value=0),
    ]
    alternatives = [
        Alternative(id="alt-a", name="Alternative A", measurements={"airbags": 4.2})
    ]

    with pytest.raises(ValueError, match="invalid measurement"):
        DecisionProblem(
            id="buy-laptop",
            name="Choose laptop",
            criteria=criteria,
            alternatives=alternatives,
        )