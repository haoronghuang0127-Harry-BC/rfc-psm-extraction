from enum import StrEnum
from typing import TypedDict

from method_1_section_selection.selection.selection_rules import ScoringMethod


# Input versions 
class InputVersion(StrEnum):
    BASELINE_ALL = "baseline_all"
    HIGH_PRIORITY = "hybrid_high"
    HIGH_MEDIUM_PRIORITY = "hybrid_high_medium"

class PromptRecord(TypedDict):
    protocol: str
    scoring_method: ScoringMethod
    input_version: InputVersion
    section_index: int
    section_number: str
    section_name: str
    tag: str
    source_file: str
    section_text: str
    prompt_word_count: int
    prompt: str


class PromptSummary(TypedDict):
    protocol: str
    scoring_method: ScoringMethod
    input_version: InputVersion
    source_file: str
    prompt_count: int
    total_prompt_words: int
    baseline_prompt_words: int
    reduced_prompt_words: int
    word_reduction_percentage: float
    output_file: str
