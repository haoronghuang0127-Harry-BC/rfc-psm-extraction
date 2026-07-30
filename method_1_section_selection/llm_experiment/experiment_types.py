from enum import StrEnum
from typing import TypedDict

from config.models.model_names import ModelName
from config.models.model_types import ProfileName
from config.ollama_settings import ConnectionMode
from config.output_formats import OutputFormatName

from method_1_section_selection.prompt.prompt_types import InputVersion
from method_1_section_selection.selection.selection_rules import ScoringMethod



# Store the possible results of one model call.
class ParseStatus(StrEnum):
    VALID_PSM = "valid_psm"
    NO_PSM_FOUND = "no_psm_found"
    EMPTY_RESPONSE = "empty_response"
    INVALID_JSON = "invalid_json"
    OUTPUT_CUTOFF = "output_cutoff"
    REQUEST_FAILED = "request_failed"
    MERGE_NOT_RUN = "merge_not_run"


# Store the settings selected from the command line.
class ExperimentArguments(TypedDict):
    protocol: str
    scoring_method: ScoringMethod
    input_version: InputVersion
    model_name: ModelName
    profile_name: ProfileName | None
    connection_mode: ConnectionMode
    output_format_name: OutputFormatName
    seed: int | None
    max_sections: int | None

# Store the common result of one model call.
class ModelCallResult(TypedDict):
    ollama_response: dict[str, object]
    response_text: str
    thinking_text: str
    parsed_output: object | None
    parse_status: ParseStatus
     # Empty when the request succeeded, and the error message when it failed.
    request_error: str


# Store the result of one section prompt.
class SectionRunResult(ModelCallResult):
    section_index: int
    section_number: str
    section_name: str
    tag: str
    source_file: str
    prompt_word_count: int
    prompt: str

# Store the result of the final merge prompt.
class MergeRunResult(ModelCallResult):
    merge_prompt: str
    merge_options: dict[str, int | float]
    merge_prompt_token_estimate: int
    merge_call_count: int
    used_batch_merge: bool


# Store the main numbers used to analyse one experiment.
class ExperimentSummary(TypedDict):
    section_parse_status_counts: dict[str, int]
    experiment_running_time_seconds: float


# Store the Ollama and model environment used by one experiment.
class ExperimentEnvironment(TypedDict):
    collected_at: str
    model_name: ModelName
    quantization_level: str
    requested_context: int
    allocated_context: int | None
    metadata_error: str

# Store the complete result of one experiment.
class ExperimentResult(TypedDict):
    protocol: str
    scoring_method: ScoringMethod
    input_version: InputVersion
    model_name: ModelName
    profile_name: ProfileName
    profile_description: str
    options: dict[str, int | float]
    think: bool | str | None
    requested_connection_mode: ConnectionMode
    actual_connection_mode: ConnectionMode
    output_format_name: OutputFormatName
    output_format_description: str
    seed: int
    max_sections: int | None
    prompt_file: str
    section_count: int
    successful_section_count: int
    failed_section_count: int
    summary: ExperimentSummary
    environment: ExperimentEnvironment
    sections: list[SectionRunResult]
    merge: MergeRunResult
