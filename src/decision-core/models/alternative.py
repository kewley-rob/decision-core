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


@dataclass(frozen=True)
class Alternative:
    id: str
    name: str
    measurements: dict[str, object]

    def __post_init__(self) -> None:
        if not self.id or not self.id.strip():
            raise ValueError("Alternative id must be a non-empty string.")
        if not self.name or not self.name.strip():
            raise ValueError("Alternative name must be a non-empty string.")
        if not isinstance(self.measurements, dict):
            raise ValueError("Alternative measurements must be a dictionary.")
        for criterion_id, value in self.measurements.items():
            if not isinstance(criterion_id, str) or not criterion_id.strip():
                raise ValueError("Measurement criterion id must be a non-empty string.")
            if value is None:
                raise ValueError(
                    f"Measurement for criterion '{criterion_id}' must not be None."
                )