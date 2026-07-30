import json

from config.model_profiles import ModelProfile
from config.models.model_types import ModelConfig
from config.ollama_settings import OllamaConnection
from config.output_formats import OutputFormat, OutputFormatName

from method_1_section_selection.llm_experiment.experiment_error import build_failed_model_result
from method_1_section_selection.llm_experiment.experiment_types import MergeRunResult, ModelCallResult, ParseStatus, SectionRunResult
from method_1_section_selection.llm_experiment.experiment_ollama_request import send_prompt_to_model
from method_1_section_selection.llm_experiment.merge_psm_service import build_merge_profile
from method_1_section_selection.prompt.prompt_types import PromptRecord
from method_1_section_selection.llm_experiment.merge_psm_service import merge_partial_outputs

from util.text_statistics import count_words
     
# send section prompt to ollama
def send_section_prompt(prompt: PromptRecord, prompt_text: str, model_config: ModelConfig, model_profile: ModelProfile, connection: OllamaConnection, output_format: OutputFormat) -> SectionRunResult:
    model_result: ModelCallResult = send_prompt_to_model(prompt_text=prompt_text, model_config=model_config, model_profile=model_profile, 
                                                         connection=connection, request_format=output_format["section_request_format"],
                                                         output_format_name=output_format["name"], is_merge_prompt=False)

    section_result: SectionRunResult = {
        "section_index": prompt["section_index"],
        "section_number": prompt["section_number"],
        "section_name": prompt["section_name"],
        "tag": prompt["tag"],
        "source_file": prompt["source_file"],
        "prompt_word_count": count_words(prompt_text),
        "prompt": prompt_text,
        "ollama_response": model_result["ollama_response"],
        "response_text": model_result["response_text"],
        "thinking_text": model_result["thinking_text"],
        "parsed_output": model_result["parsed_output"],
        "parse_status": model_result["parse_status"],
        "request_error": model_result["request_error"],
    }

    return section_result

def send_merge_prompt(section_results: list[SectionRunResult], model_config: ModelConfig, model_profile: ModelProfile, connection: OllamaConnection, output_format: OutputFormat) -> MergeRunResult:
    partial_outputs: list[str] = []
    merge_profile: ModelProfile = build_merge_profile(model_profile)

    for result in section_results:
        # F0 keeps the original model response.
        # This includes <json>None</json>.
        if output_format["name"] == OutputFormatName.F0:
            if result["parse_status"] in (ParseStatus.VALID_PSM, ParseStatus.NO_PSM_FOUND):
                response_text: str = result["response_text"]
                
                # Some thinking models may place the result in thinking.
                if not response_text.strip():
                    response_text = result["thinking_text"]

                if response_text.strip():
                    partial_outputs.append(response_text)

            # F0 process end here
            continue

        # F1 and F2
        parsed_output: object | None = result["parsed_output"]

        # find the vaild psm and put in the readyly list
        if result["parse_status"] == ParseStatus.VALID_PSM and isinstance(parsed_output, dict):
                    partial_outputs.append(json.dumps(parsed_output, ensure_ascii=False))

    # if parsed_outputs list is empty return the error result (empty)
    if not partial_outputs: 
        merge_result: MergeRunResult = {
            "merge_prompt": "",
            "ollama_response": {},
            "response_text": "",
            "thinking_text": "",
            "parsed_output": None,
            "parse_status": ParseStatus.MERGE_NOT_RUN,
            "merge_options": merge_profile["options"],
            "merge_prompt_token_estimate": 0,
            "merge_call_count": 0,
            "used_batch_merge": False,
            "request_error": "No valid section PSMs were available for the final merge."
        }

        return merge_result

    # set the value for merge_partial_outputs fucntiuon
    model_result: ModelCallResult
    merge_prompt: str
    merge_call_count: int
    used_batch_merge: bool
    merge_prompt_token_prediction: int

    model_result, merge_prompt, merge_call_count, used_batch_merge, merge_prompt_token_prediction = (
         merge_partial_outputs(partial_outputs=partial_outputs, model_config=model_config, merge_profile=merge_profile, connection=connection, output_format=output_format)
    )

    # return the merge result
    merge_result: MergeRunResult = {
        "merge_prompt": merge_prompt,
        "ollama_response": model_result["ollama_response"],
        "response_text": model_result["response_text"],
        "thinking_text": model_result["thinking_text"],
        "parsed_output": model_result["parsed_output"],
        "parse_status": model_result["parse_status"],
        "merge_options": merge_profile["options"],
        "merge_prompt_token_estimate": merge_prompt_token_prediction,
        "merge_call_count": merge_call_count,
        "used_batch_merge": used_batch_merge,
        "request_error": model_result["request_error"],
    }

    return merge_result

# Build the result of a section that could not be processed.
def build_failed_section_result(prompt: PromptRecord, prompt_text: str, error: BaseException) -> SectionRunResult:

    model_result: ModelCallResult = build_failed_model_result(error)

    section_result: SectionRunResult = {
        "section_index": prompt["section_index"],
        "section_number": prompt["section_number"],
        "section_name": prompt["section_name"],
        "tag": prompt["tag"],
        "source_file": prompt["source_file"],
        "prompt_word_count": count_words(prompt_text),
        "prompt": prompt_text,
        "ollama_response": model_result["ollama_response"],
        "response_text": model_result["response_text"],
        "thinking_text": model_result["thinking_text"],
        "parsed_output": model_result["parsed_output"],
        "parse_status": model_result["parse_status"],
        "request_error": model_result["request_error"],
    }

    return section_result

