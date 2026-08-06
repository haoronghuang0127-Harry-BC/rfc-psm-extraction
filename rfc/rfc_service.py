from rfc.rfc_types import RfcSegment

# get value in RfcSegment
def get_rfc_segment_values(segment: RfcSegment) -> tuple[str, str, str, str]:
    # get RfcSegment values
    section_number: str = segment.get("section_number", "")
    section_name: str = segment.get("section_name", "")
    tag: str = segment.get("tag", "")
    content: str = segment.get("content", "")

    return section_number, section_name, tag, content