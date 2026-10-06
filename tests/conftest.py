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