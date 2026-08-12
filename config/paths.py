from pathlib import Path
from typing import Final


# the Path of path.py
CURRENT_FILE: Final[Path] = Path(__file__).resolve()

# the path of util folder
CONFIG_FOLDER: Final[Path] = CURRENT_FILE.parent

# the root path
PROJECT_FOLDER_DIR: Final[Path] = CONFIG_FOLDER.parent

# PSMBench Project Path
PSMBENCH_DIR: Final[Path] = PROJECT_FOLDER_DIR / "RFC_PSM_Benchmark-main" 
# PSMBench Evaluation OutputPath
PSMBENCH_OUTPUT_DIR: Final[Path] = PROJECT_FOLDER_DIR / "PSMBench_evaluation_results"
# PSMBench fsm Path
PSMBENCH_FSM_DIR: Final[Path] = PSMBENCH_DIR / "fsm"

"""
Method1
"""
# The Method 1 root folder
METHOD_1_DIR: Final[Path] = PROJECT_FOLDER_DIR / "method_1_section_selection"

# The output folder of Method 1.
METHOD_1_OUTPUT_DIR: Final[Path] = METHOD_1_DIR / "outputs"




"""
Method2
"""
# The Method 2 root folder.
METHOD_2_DIR: Final[Path] = PROJECT_FOLDER_DIR / "method_2_long_section_splitting"

# The output folder of Method 2.
METHOD_2_OUTPUT_DIR: Final[Path] = METHOD_2_DIR / "outputs"
