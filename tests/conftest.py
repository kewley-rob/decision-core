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

from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DECISION_CORE_SRC = PROJECT_ROOT / "src" / "decision-core"
DECISION_PLOTS_SRC = PROJECT_ROOT / "src" / "decision-plots"
IMPORT_DATA_FRAMES_SRC = PROJECT_ROOT / "src" / "import-data-frames"

for source_path in (DECISION_CORE_SRC, DECISION_PLOTS_SRC, IMPORT_DATA_FRAMES_SRC):
    source_path_str = str(source_path)
    if source_path_str not in sys.path:
        sys.path.insert(0, source_path_str)