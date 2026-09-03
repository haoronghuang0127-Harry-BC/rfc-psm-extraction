from pathlib import Path

from config.models.model_names import ModelName
from config.models.model_profiles import ModelProfile, get_model_profile
from config.models.model_types import ModelConfig, ProfileName
from config.ollama_settings import OllamaConnection, get_ollama_connection
from config.paths import FIXED_TOKEN_SPLITTING_COMBINATION_RESPONSES_DIR, FIXED_TOKEN_SPLITTING_PROMPTS_DIR
from config.protocol.protocol_util import get_all_protocol_files

from research_pipeline.output_controls import get_output_control
from research_pipeline.model_selection import get_selected_model_configs
from research_pipeline.types import OutputControl

from split_experiment.command_line import read_command_line_to_value
from split_experiment.types import SplitExperimentArguments

from utils.files_util import load_json_file, save_json_file
from utils.ollama_client import call_ollama_with_model_routing


# load all combination Prompts from the local file.
def _load_combination_prompts() -> dict[str, str]:
    prompts_file: Path = FIXED_TOKEN_SPLITTING_PROMPTS_DIR / "combination_prompts.json"

    if not prompts_file.is_file():
        raise FileNotFoundError(f"Could not find the combination Prompt file: {prompts_file}")

    combination_prompts: dict[str, str] = load_json_file(file_path=prompts_file, data_type=dict[str, str])

    print(f"Loaded combination Prompts: {prompts_file}")

    return combination_prompts


# return the selected protocol names.
def _get_selected_protocol_names(protocol: str) -> list[str]:
    if protocol == "all":
        protocol_files: dict[str, Path] = get_all_protocol_files()
        protocol_names: list[str] = list(protocol_files.keys())

        return protocol_names

    return [protocol]


# build one combination Prompt name.
def _build_combination_prompt_name(protocol: str, model_name: str, profile_name: ProfileName) -> str:
    safe_model_name: str = model_name.replace(":", "_").replace("/", "_")
    safe_profile_name: str = profile_name.value.replace("-", "_")

    prompt_name: str = f"{protocol}_{safe_model_name}_{safe_profile_name}_ollama_json_schema_output"

    return prompt_name


# run one combination Prompt.
def _run_combination_psm(prompt_name: str, prompt: str, connection: OllamaConnection, model_config: ModelConfig, profile_name: ProfileName, model_profile: ModelProfile, output_control: OutputControl) -> Path:
    print(f"Running combination Prompt: {prompt_name}")

    ollama_response: dict[str, object] = call_ollama_with_model_routing(ollama_url=connection["ollama_url"], model=model_config["name"].value, prompt=prompt, options=model_profile["options"], request_timeout_seconds=connection["request_timeout_seconds"], think=model_profile["think"], output_format=output_control["request_format"], extra_headers=connection["extra_headers"])

    response_copy: dict[str, object] = dict(ollama_response)

    # remove the token id array.
    response_copy.pop("context", None)

    # record the Prompt and profile names.
    response_copy["prompt_name"] = prompt_name
    response_copy["profile_name"] = profile_name.value

    output_file: Path = FIXED_TOKEN_SPLITTING_COMBINATION_RESPONSES_DIR / f"{prompt_name}_combination_response.json"

    save_json_file(file_path=output_file, data=response_copy)

    print(f"Saved combination response: {output_file}")

    return output_file


# run fixed token combination for the selected protocols and models.
def combination_psm(combination_prompts: dict[str, str], arguments: SplitExperimentArguments) -> list[Path]:
    connection: OllamaConnection = get_ollama_connection(connection_mode=arguments["connection_mode"])
    model_configs: list[ModelConfig] = get_selected_model_configs(model_name=arguments["model"])
    protocol_names: list[str] = _get_selected_protocol_names(protocol=arguments["protocol"])
    output_control: OutputControl = get_output_control(output_control_name="ollama_json_schema_output")

    response_files: list[Path] = []

    for model_config in model_configs:
        if model_config["name"] == ModelName.QWQ_32B:
            continue

        profile_name: ProfileName = model_config["default_profile"]
        model_profile: ModelProfile = get_model_profile(profile_name=profile_name)

        print(f"Starting model combination: model={model_config['name'].value}, profile={profile_name.value}")

        for protocol in protocol_names:
            prompt_name: str = _build_combination_prompt_name(protocol=protocol, model_name=model_config["name"].value, profile_name=profile_name)
            prompt: str | None = combination_prompts.get(prompt_name)

            if prompt is None:
                print(f"Skipped missing combination Prompt: {prompt_name}")
                continue

            response_file: Path = _run_combination_psm(prompt_name=prompt_name, prompt=prompt, connection=connection, model_config=model_config, profile_name=profile_name, model_profile=model_profile, output_control=output_control)

            response_files.append(response_file)

        print(f"Completed model combination: model={model_config['name'].value}, profile={profile_name.value}")

    return response_files


def main() -> None:
    arguments: SplitExperimentArguments = read_command_line_to_value()

    combination_prompts: dict[str, str] = _load_combination_prompts()

    response_files: list[Path] = combination_psm(combination_prompts=combination_prompts, arguments=arguments)

    print(f"Completed Ollama combination. Saved {len(response_files)} response files.")


if __name__ == "__main__":
    main()
