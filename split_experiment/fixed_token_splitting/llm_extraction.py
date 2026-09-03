from pathlib import Path

from config.models.model_names import ModelName
from config.models.model_profiles import ModelProfile, get_model_profile
from config.models.model_types import ModelConfig, ProfileName
from config.ollama_settings import OllamaConnection, get_ollama_connection
from config.paths import FIXED_TOKEN_SPLITTING_ORIGINAL_RESPONSES_DIR, FIXED_TOKEN_SPLITTING_PROMPTS_DIR

from research_pipeline.output_controls import get_output_control
from research_pipeline.types import OutputControl
from research_pipeline.model_selection import get_selected_model_configs

from split_experiment.command_line import read_command_line_to_value
from split_experiment.types import SplitExperimentArguments

from utils.files_util import load_json_file, save_json_file
from utils.ollama_client import call_ollama_with_model_routing


# load extraction Prompts from the local Prompt file.
def _load_extraction_prompts(protocol: str) -> dict[str, list[str]]:
    prompts_file: Path = FIXED_TOKEN_SPLITTING_PROMPTS_DIR / "ollama_json_schema_output_extraction_prompts.json"

    if not prompts_file.is_file():
        raise FileNotFoundError(f"Could not find the extraction Prompt file: {prompts_file}")

    extraction_prompts: dict[str, list[str]] = load_json_file(file_path=prompts_file, data_type=dict[str, list[str]])

    if protocol == "all":
        selected_extraction_prompts: dict[str, list[str]] = extraction_prompts
    else:
        selected_extraction_prompts = {
            protocol: extraction_prompts[protocol],
        }

    print(f"Loaded extraction Prompts: {prompts_file}")

    return selected_extraction_prompts


# build the extraction response file path.
def _build_save_response_path(protocol: str, model_name: str, profile_name: ProfileName) -> Path:
    safe_model_name: str = model_name.replace(":", "_").replace("/", "_")
    safe_profile_name: str = profile_name.value.replace("-", "_")

    file_name: str = f"{protocol}_{safe_model_name}_{safe_profile_name}_ollama_json_schema_output_extraction_responses.json"

    output_file: Path = FIXED_TOKEN_SPLITTING_ORIGINAL_RESPONSES_DIR / file_name

    return output_file


# run all fixed token extraction Prompts for one protocol and model.
def _run_extraction_psm(protocol: str, prompts: list[str], model_config: ModelConfig, profile_name: ProfileName, model_profile: ModelProfile, output_control: OutputControl, connection: OllamaConnection) -> Path:
    response_records: list[dict[str, object]] = []

    prompt_count: int = len(prompts)

    print(f"Starting extraction: protocol={protocol}, model={model_config['name'].value}, profile={profile_name.value}, output=ollama_json_schema_output, prompts={prompt_count}")

    for index, prompt in enumerate(prompts, start=1):
        print(f"{protocol}: extraction Prompt {index}/{prompt_count}")

        ollama_response: dict[str, object] = call_ollama_with_model_routing(ollama_url=connection["ollama_url"], model=model_config["name"].value, prompt=prompt, options=model_profile["options"], request_timeout_seconds=connection["request_timeout_seconds"], think=model_profile["think"], output_format=output_control["request_format"], extra_headers=connection["extra_headers"])

        response_copy: dict[str, object] = dict(ollama_response)

        # remove the token id array.
        response_copy.pop("context", None)

        # record the Prompt index.
        response_copy["prompt_index"] = index

        response_records.append(response_copy)

    output_file: Path = _build_save_response_path(protocol=protocol, model_name=model_config["name"].value, profile_name=profile_name)

    save_json_file(file_path=output_file, data=response_records)

    print(f"Saved extraction responses: {output_file}")

    return output_file


# run fixed token extraction for the selected protocols and models.
def extraction_psm(extraction_prompts: dict[str, list[str]], arguments: SplitExperimentArguments) -> list[Path]:
    connection: OllamaConnection = get_ollama_connection(connection_mode=arguments["connection_mode"])

    model_configs: list[ModelConfig] = get_selected_model_configs(model_name=arguments["model"])
    output_control: OutputControl = get_output_control(output_control_name="ollama_json_schema_output")

    response_files: list[Path] = []

    for model_config in model_configs:
        if model_config["name"] == ModelName.QWQ_32B:
            continue

        profile_name: ProfileName = model_config["default_profile"]
        model_profile: ModelProfile = get_model_profile(profile_name=profile_name)

        for protocol, prompts in extraction_prompts.items():
            response_file: Path = _run_extraction_psm(protocol=protocol, prompts=prompts, model_config=model_config, profile_name=profile_name, model_profile=model_profile, output_control=output_control, connection=connection)

            response_files.append(response_file)

    return response_files


def main() -> None:
    arguments: SplitExperimentArguments = read_command_line_to_value()

    extraction_prompts: dict[str, list[str]] = _load_extraction_prompts(protocol=arguments["protocol"])

    response_files: list[Path] = extraction_psm(extraction_prompts=extraction_prompts, arguments=arguments)

    print(f"Completed Ollama extraction. Saved {len(response_files)} response files.")


if __name__ == "__main__":
    main()
