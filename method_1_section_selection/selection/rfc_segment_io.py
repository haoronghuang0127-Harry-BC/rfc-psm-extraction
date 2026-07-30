import json
from pathlib import Path

from method_1_section_selection.selection.section_features import RfcSegment

# Load all RFC sections from one PSMBench JSON file.
def load_rfc_segments(file_path: Path) -> list[RfcSegment]:
    with file_path.open("r", encoding="utf-8") as file:
        segments: list[RfcSegment] = json.load(file)

    return segments