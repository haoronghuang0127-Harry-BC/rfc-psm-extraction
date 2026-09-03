from typing import TypedDict

from config.models.model_names import ModelName
from config.ollama_settings import ConnectionMode


# store the values selected from the command line.
class SplitExperimentArguments(TypedDict):
    protocol: str
    model: ModelName
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
