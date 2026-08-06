from pathlib import Path

from rfc.rfc_io import load_rfc_segments
from rfc.rfc_types import RfcSegment


def process_protocol(protocol: str, source_file: Path) -> None:
    print(f"\nProcessing protocol: {protocol}")

    # load the original rfc sections
    source_segments: list[RfcSegment] = load_rfc_segments()


    
    