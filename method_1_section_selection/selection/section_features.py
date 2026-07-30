from typing import TypedDict

from method_1_section_selection.selection.selection_rules import KEYWORD_WEIGHTS, TITLE_BONUS
from util.text_statistics import count_keyword, count_words

# Structure of RFC segment from PSMBench
class RfcSegment(TypedDict, total=False):
    section_number: str
    section_name: str
    tag: str
    content: str

# The features extracted from a RFC section
class SectionFeatures(TypedDict):
    section_number: str
    section_name: str
    tag: str
    content: str
    word_count: int
    keyword_counts: dict[str, int]
    matched_titles: list[str]
    source_index: int


def _combine_section_name_and_content_to_text(section_name: str, content: str) -> str:
    # combine the section_name and content to text
    text: str = f"{section_name}\n{content}"

    return text


# get the keyword cpunts from thee section text
def _get_keyword_counts(section_text: str) -> dict[str, int]:

    keyword_counts: dict[str, int] = {}

    for keyword in KEYWORD_WEIGHTS:
        # get the number of the keywords
        counter: int = count_keyword(section_text, keyword)

        # save in the result
        if counter > 0:
            keyword_counts[keyword] = counter

    return keyword_counts


# get the matched title(section_name)
def _get_matched_title(section_name: str) -> list[str]:
    # To lower case
    section_name = section_name.lower()

    matched_titles: list[str] = []

    # find matched titles
    for title in TITLE_BONUS:
        if title in section_name:
            matched_titles.append(title)


    return matched_titles

# get value in RfcSegment
def get_rfc_segment_values(segment: RfcSegment) -> tuple[str, str, str, str]:
    # get RfcSegment values
    section_number: str = segment.get("section_number", "")
    section_name: str = segment.get("section_name", "")
    tag: str = segment.get("tag", "")
    content: str = segment.get("content", "")

    return section_number, section_name, tag, content

# extract all features from rfc sections
def extract_section_features(segment: RfcSegment, source_index: int) -> SectionFeatures:
    # get RfcSegment values
    section_number, section_name, tag, content = get_rfc_segment_values(segment)

    # combine the section_name and context -> section_text
    section_text: str = _combine_section_name_and_content_to_text(section_name, content)

    # get keyword counts
    keyword_counts: dict[str, int] = _get_keyword_counts(section_text)

    # get matches titles
    matched_titles: list[str] = _get_matched_title(section_name)

    # get word count
    word_count: int = count_words(content)

    return {
        "section_number": section_number,
        "section_name": section_name,
        "tag": tag,
        "content": content,
        "word_count": word_count,
        "keyword_counts": keyword_counts,
        "matched_titles": matched_titles,
        "source_index": source_index
    }




