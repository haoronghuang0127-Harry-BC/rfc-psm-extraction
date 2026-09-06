from typing import TypedDict

from config.models.model_names import ModelName
from config.ollama_settings import ConnectionMode
from rfc.rfc_types import RfcSegment


# store the values selected from the command line.
class SplitExperimentArguments(TypedDict):
    protocol: str
    model: ModelName
    profile: str
    connection_mode: ConnectionMode


# store the whole RFC document manifest.
class WholeRfcDocumentManifest(TypedDict):
    condition: str
    protocol: str
    source_file: str
    source_segment_count: int
    whole_document_file: str


# store one whole document context exclusion.
class WholeDocumentContextExclusion(TypedDict):
    protocol: str
    model: str
    profile: str
    tokenizer: str
    prompt_token_count: int
    num_ctx: int
    num_predict: int
    maximum_input_tokens: int
    reason: str


# store one fixed token splitting manifest.
class FixedTokenSplittingManifest(TypedDict):
    condition: str
    protocol: str
    tokenizer: str
    maximum_tokens_per_segment: int
    overlap_tokens: int
    source_file: str
    original_segment_count: int
    source_token_count: int
    fixed_segment_count: int
    output_file: str


# store one recursive section splitting manifest.
class RecursiveSectionSplittingManifest(TypedDict):
    condition: str
    protocol: str
    tokenizer: str
    maximum_tokens_per_segment: int
    overlap_tokens: int
    source_file: str
    original_segment_count: int
    original_over_limit_count: int
    split_segment_count: int
    final_segment_count: int
    remaining_over_limit_count: int
    remaining_over_limit_sections: list[str]
    output_file: str


# store one segment with referenced RFC section context.
class ReferencedContextSegment(RfcSegment, total=False):
    referenced_sections: list[str]
    unresolved_references: list[str]


# store one referenced context splitting manifest.
class ReferencedContextSplittingManifest(TypedDict):
    condition: str
    protocol: str
    tokenizer: str
    base_condition: str
    source_file: str
    source_recursive_segments_file: str
    base_segment_count: int
    final_segment_count: int
    segments_with_referenced_context_count: int
    resolved_reference_count: int
    unresolved_reference_count: int
    maximum_final_segment_token_count: int
    output_file: str
