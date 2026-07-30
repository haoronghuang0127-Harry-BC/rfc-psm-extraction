from config.model_profiles import ModelProfile
from config.models.model_types import ModelConfig
from config.ollama_settings import OllamaConnection

from config.output_formats import OutputFormatName
from method_1_section_selection.llm_experiment.experiment_error import build_failed_model_result
from method_1_section_selection.llm_experiment.experiment_types import ModelCallResult, ParseStatus

from util.llm_output_parser import parse_json_from_response
from util.ollama_client import call_ollama_generate

# check the json if complete
def _is_json_cutoff(ollama_response: dict[str, object]) -> bool:
    # get the reason from the response
    done_reason: object = ollama_response.get("done_reason", "")

    if not isinstance(done_reason, str):
        return False

    # if the ollama reutrn the result because length limit wil return length
    return done_reason.strip().lower() == "length"

# Check the structure of one section result.
def _has_section_psm_structure(parsed_output: dict[str, object], output_format_name: OutputFormatName) -> bool:
    # get the states and transitions from the parsed output
    states: object = parsed_output.get("states")
    transitions: object = parsed_output.get("transitions")

    # check states and transitions are valid
    if not isinstance(states, list):
        return False

    if not isinstance(transitions, list):
        return False

    # F1 and F2 must contain has_psm.
    if output_format_name in (OutputFormatName.F1, OutputFormatName.F2):
        has_psm: object = parsed_output.get("has_psm")

        if not isinstance(has_psm, bool):
            return False

    return True

# Check the structure of the final merged PSM.
def _has_merge_psm_structure(parsed_output: dict[str, object]) -> bool:
    states: object = parsed_output.get("states")
    initial_state: object = parsed_output.get("initial_state")
    final_states: object = parsed_output.get("final_states")
    transitions: object = parsed_output.get("transitions")

    if not isinstance(states, list):
        return False

    if not isinstance(initial_state, str):
        return False

    if not isinstance(final_states, list):
        return False

    if not isinstance(transitions, list):
        return False

    return True

# using to check the F0 method (original PSMBench method)
def _is_no_psm_response(response: str) -> bool:

    response: str = "".join(response.lower().split())

    return response == "<json>none</json>"

def _get_parse_status(response_text: str, parsed_output: object | None, ollama_response: dict[str, object], output_format_name: OutputFormatName, is_merge_prompt: bool) -> ParseStatus:

    # check if the json is complete
    if _is_json_cutoff(ollama_response):
        return ParseStatus.OUTPUT_CUTOFF

    # check if the response is empty
    if not response_text.strip():
        return ParseStatus.EMPTY_RESPONSE

    # Only F0 uses <json>None</json>.
    if output_format_name == OutputFormatName.F0 and _is_no_psm_response(response_text):
        return ParseStatus.NO_PSM_FOUND

    # check if the json is invalid (judge the result is dict)
    if not isinstance(parsed_output, dict):
        return ParseStatus.INVALID_JSON

    # Check the final merged PSM.
    if is_merge_prompt:
        if not _has_merge_psm_structure(parsed_output):
            return ParseStatus.INVALID_JSON

        return ParseStatus.VALID_PSM

    # Check one section result.
    if not _has_section_psm_structure(parsed_output=parsed_output, output_format_name=output_format_name):
        return ParseStatus.INVALID_JSON

    # F1 and F2 use has_psm to represent no PSM.
    if output_format_name in (OutputFormatName.F1, OutputFormatName.F2):
        # check if find psm in the result
        has_psm: object = parsed_output.get("has_psm")
        if has_psm is False:
            return ParseStatus.NO_PSM_FOUND

    return ParseStatus.VALID_PSM


def _get_parameter_from_ollama_response(ollama_response: dict[str, object],parameter: str) -> str:

    res_parameter: object = ollama_response.get(parameter,"")

    if not isinstance(res_parameter, str):
        return ""

    return res_parameter

def send_prompt_to_model(prompt_text: str, model_config: ModelConfig, model_profile: ModelProfile, connection: OllamaConnection, request_format: str | dict[str, object] | None, output_format_name: OutputFormatName, is_merge_prompt: bool) -> ModelCallResult:
    try:
        response: dict[str, object] = call_ollama_generate(ollama_url=connection["ollama_url"],
                                                                model=model_config["name"].value,
                                                                prompt=prompt_text,
                                                                options=model_profile["options"],
                                                                request_timeout_seconds=connection["request_timeout_seconds"],
                                                                think=model_profile["think"],
                                                                output_format=request_format,
                                                                extra_headers=connection["extra_headers"])
    except (RuntimeError, OSError) as error:
            return build_failed_model_result(error)

    # get the model output
    response_str: str = _get_parameter_from_ollama_response(response,"response")

    # get the model thinking output
    thinking_str: str = _get_parameter_from_ollama_response(response,"thinking")

    # I found when uisng P3 + F2, the result will put in the thinking text, the response text is empt, so judge it if the response text is empty
    output_str: str = response_str
    if not output_str.strip():
        output_str = thinking_str


    # F0 requires <json> tags. F1 and F2 use direct JSON.
    allow_direct_json: bool = output_format_name != OutputFormatName.F0
    # convert the json to python opject
    output: object | None = parse_json_from_response(response=output_str, allow_direct_json=allow_direct_json)

    status: ParseStatus = _get_parse_status(response_text=output_str, parsed_output=output, ollama_response=response,
                                            output_format_name=output_format_name, is_merge_prompt=is_merge_prompt)
    
    model_result: ModelCallResult = {
        "ollama_response": response,
        "response_text": response_str,
        "thinking_text": thinking_str,
        "parsed_output": output,
        "parse_status": status,
        "request_error": "",
    }

    return model_result