from datetime import UTC, datetime

from config.models.model_names import ModelName
from config.ollama_settings import OllamaConnection

from method_1_section_selection.llm_experiment.experiment_types import ExperimentEnvironment, ExperimentSummary, ParseStatus, SectionRunResult

from util.ollama_client import get_ollama_running_models



# Build the main numerical summary of one experiment.
def build_experiment_summary(section_results: list[SectionRunResult], experiment_running_time_seconds: float) -> ExperimentSummary:

    section_parse_status_counts: dict[str, int] = {}

    for section_result in section_results:
        parse_status_value: ParseStatus | str = section_result["parse_status"]

        if isinstance(parse_status_value, ParseStatus):
            parse_status: str = parse_status_value.value
        else:
            parse_status = str(parse_status_value)

        section_parse_status_counts[parse_status] = section_parse_status_counts.get(parse_status, 0) + 1

    summary: ExperimentSummary = {
        "section_parse_status_counts": section_parse_status_counts,
        "experiment_running_time_seconds": round(experiment_running_time_seconds, 3),
    }

    return summary

# Return a string value from an object.
def _get_string(value: object) -> str:

    if isinstance(value, str):
        return value

    return ""


# Return a dictionary value from an object.
def _get_dictionary(value: object) -> dict[str, object]:

    if isinstance(value, dict):
        return value

    return {}


# Find the selected model in the list of running Ollama models.
def _find_running_model(running_models: list[dict[str, object]], model_name: ModelName) -> dict[str, object]:

    for running_model in running_models:
        running_name: str = _get_string(running_model.get("name"))
        running_model_name: str = _get_string(running_model.get("model"))

        if model_name.value in (running_name, running_model_name):
            return running_model

    return {}


# Build the Ollama and model environment record.
def build_experiment_environment(connection: OllamaConnection, model_name: ModelName, requested_context: int) -> ExperimentEnvironment:

    metadata_timeout_seconds: int = 10
    metadata_errors: list[str] = []
    running_model: dict[str, object] = {}

    try:
        running_models: list[dict[str, object]] = get_ollama_running_models(ollama_url=connection["ollama_url"], extra_headers=connection["extra_headers"], timeout_seconds=metadata_timeout_seconds)
        running_model = _find_running_model(running_models=running_models, model_name=model_name)

        if not running_model:
            metadata_errors.append("The selected model was not found in the Ollama running model list.")
    except RuntimeError as error:
        metadata_errors.append(str(error))

    model_details: dict[str, object] = _get_dictionary(running_model.get("details"))

    allocated_context_value: object = running_model.get("context_length")

    if isinstance(allocated_context_value, bool) or not isinstance(allocated_context_value, int):
        allocated_context: int | None = None
    else:
        allocated_context = allocated_context_value

    environment: ExperimentEnvironment = {
        "collected_at": datetime.now(UTC).isoformat(),
        "model_name": model_name,
        "quantization_level": _get_string(model_details.get("quantization_level")),
        "requested_context": requested_context,
        "allocated_context": allocated_context,
        "metadata_error": " | ".join(metadata_errors),
    }

    return environment
