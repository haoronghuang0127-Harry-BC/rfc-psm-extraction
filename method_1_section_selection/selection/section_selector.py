import math

from typing import TypedDict
from enum import StrEnum

from method_1_section_selection.selection.section_scoring import ScoredSection
from method_1_section_selection.selection.selection_rules import HIGH_PRIORITY_RATIO, MEDIUM_PRIORITY_RATIO


# define the priority level of rfc section
class PriorityLevel(StrEnum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


# scored section after sort
class RankedSection(ScoredSection):
    rank: int
    priority_level: PriorityLevel


# the result after selection
class SectionSelectionResult(TypedDict):
    ranked_sections: list[RankedSection]
    high_sections: list[RankedSection]
    medium_sections: list[RankedSection]
    low_sections: list[RankedSection]


# Classify one section according to its rank.
def _classify_by_rank(rank: int, total_section: int) -> PriorityLevel:

    # get the high priority part
    high_part_sections: int = math.ceil(total_section * HIGH_PRIORITY_RATIO)
    high_part: int = max(1,high_part_sections)

    # get the medium priority part
    medium_part_sections: int = math.ceil(total_section * MEDIUM_PRIORITY_RATIO)
    medium_part: int = max(high_part, medium_part_sections)


    # return the priority level
    if rank <= high_part:
        return PriorityLevel.HIGH
    if rank <= medium_part:
        return PriorityLevel.MEDIUM

    return PriorityLevel.LOW

def _build_ranked_section(section: ScoredSection, rank: int, priority_level: PriorityLevel) -> RankedSection:
    ranked_section: RankedSection = {
        "section_number": section["section_number"],
        "section_name": section["section_name"],
        "tag": section["tag"],
        "content": section["content"],
        "word_count": section["word_count"],
        "keyword_counts": section["keyword_counts"],
        "matched_titles": section["matched_titles"],
        "scoring_method": section["scoring_method"],
        "keyword_score": section["keyword_score"],
        "keyword_density_score": section["keyword_density_score"],
        "title_bonus": section["title_bonus"],
        "score": section["score"],
        "source_index": section["source_index"],
        "rank": rank,
        "priority_level": priority_level,
    }

    return ranked_section

# get the different priority section
def _build_priority_section(ranked_sections: list[RankedSection], priority_level: PriorityLevel) -> list[RankedSection]:
    sections: list[RankedSection] = []

    for section in ranked_sections:
        if section["priority_level"] == priority_level:
            sections.append(section)

    return sections

# Rank scored sections and divide them into priority groups.
def select_sections(scored_sections: list[ScoredSection]) -> SectionSelectionResult:

    # Sort by score and keep the RFC order when scores are equal.
    sorted_sections: list[ScoredSection] = sorted(scored_sections,
                                                  key=lambda section: (-section["score"], section["source_index"]))

    total_section: int = len(sorted_sections)
    ranked_sections: list[RankedSection] = []

    # add rank and priority information to each section
    for rank, section in enumerate(sorted_sections, start=1):
        priority_level: PriorityLevel = _classify_by_rank(rank, total_section)

        ranked_section: RankedSection = _build_ranked_section(section, rank, priority_level)

        ranked_sections.append(ranked_section)


    # get high priority sections
    high_sections: list[RankedSection] = _build_priority_section(ranked_sections, PriorityLevel.HIGH)

    # get medium priority sections
    medium_sections: list[RankedSection] = _build_priority_section(ranked_sections, PriorityLevel.MEDIUM)

    # get low priority sections
    low_sections: list[RankedSection] = _build_priority_section(ranked_sections, PriorityLevel.LOW)

    return {
        "ranked_sections": ranked_sections,
        "high_sections": high_sections,
        "medium_sections": medium_sections,
        "low_sections": low_sections,
    }
