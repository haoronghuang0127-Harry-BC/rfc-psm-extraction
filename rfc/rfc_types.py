from typing import TypedDict

# Structure of RFC segment from PSMBench
class RfcSegment(TypedDict, total=False):
    section_number: str
    section_name: str
    tag: str
    content: str