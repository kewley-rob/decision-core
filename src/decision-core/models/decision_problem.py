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

from dataclasses import dataclass

from .alternative import Alternative
from .criterion import Criterion


@dataclass(frozen=True)
class DecisionProblem:
    id: str
    name: str
    criteria: list[Criterion]
    alternatives: list[Alternative]

    def __post_init__(self) -> None:
        if not self.id or not self.id.strip():
            raise ValueError("DecisionProblem id must be a non-empty string.")
        if not self.name or not self.name.strip():
            raise ValueError("DecisionProblem name must be a non-empty string.")

        criterion_ids = [criterion.id for criterion in self.criteria]
        if len(criterion_ids) != len(set(criterion_ids)):
            raise ValueError("DecisionProblem criteria must have unique ids.")

        alternative_ids = [alternative.id for alternative in self.alternatives]
        if len(alternative_ids) != len(set(alternative_ids)):
            raise ValueError("DecisionProblem alternatives must have unique ids.")

        required_criterion_ids = set(criterion_ids)
        criteria_by_id = {criterion.id: criterion for criterion in self.criteria}
        for alternative in self.alternatives:
            measured_criterion_ids = set(alternative.measurements.keys())
            unknown_criteria = measured_criterion_ids - required_criterion_ids
            missing_criteria = required_criterion_ids - measured_criterion_ids

            if unknown_criteria:
                unknown = ", ".join(sorted(unknown_criteria))
                raise ValueError(
                    f"Alternative '{alternative.id}' includes unknown criteria: {unknown}."
                )
            if missing_criteria:
                missing = ", ".join(sorted(missing_criteria))
                raise ValueError(
                    f"Alternative '{alternative.id}' is missing measurements for criteria: {missing}."
                )

            for criterion_id, raw_value in alternative.measurements.items():
                criterion = criteria_by_id[criterion_id]
                try:
                    criterion.validate_measurement(raw_value)
                except ValueError as error:
                    raise ValueError(
                        f"Alternative '{alternative.id}' has invalid measurement for criterion '{criterion_id}': {error}"
                    ) from error