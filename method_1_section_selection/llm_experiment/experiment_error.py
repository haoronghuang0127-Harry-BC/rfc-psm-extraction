from method_1_section_selection.llm_experiment.experiment_types import ModelCallResult, ParseStatus

# build fail result
def build_failed_model_result(error: BaseException) -> ModelCallResult:

    result: ModelCallResult = {
        "ollama_response": {},
        "response_text": "",
        "thinking_text": "",
        "parsed_output": None,
        "parse_status": ParseStatus.REQUEST_FAILED,
        "request_error": f"{type(error).__name__}: {error}"
    }

    return result