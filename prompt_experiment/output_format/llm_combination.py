from pathlib import Path

from config.models.model_profiles import ModelProfile, get_model_profile
from config.models.model_types import ModelConfig, ProfileName
from config.ollama_settings import OllamaConnection, get_ollama_connection
from config.paths import PROMPT_EXPERIMENT_COMBINATION_RESPONSES_DIR, PROMPT_EXPERIMENT_PROMPTS_DIR
from config.protocol.protocol_util import get_all_protocol_files

from prompt_experiment.output_format.command_line import read_command_line_to_value
from prompt_experiment.output_format.output_controls import get_selected_output_controls
from prompt_experiment.types import OutputControl, PromptExperimentArguments

from research_pipeline.model_selection import get_selected_model_configs, get_selected_profile_names

from utils.files_util import load_json_file, save_json_file
from utils.ollama_client import call_ollama_generate

# load all combination prompts from the local file.
def _load_combination_prompts() -> dict[str, str]:
    prompts_file: Path = PROMPT_EXPERIMENT_PROMPTS_DIR / "combination_prompts.json"

    if not prompts_file.is_file():
        raise FileNotFoundError(f"Could not find the combination prompt file: {prompts_file}")

    combination_prompts: dict[str, str] = load_json_file(file_path=prompts_file, data_type=dict[str, str])

    print(f"Loaded combination prompts: {prompts_file}")

    return combination_prompts


def _get_selected_protocol_names(protocol: str) -> list[str]:
    # if all return all the protocol list
    if protocol == "all":
        protocol_files: dict[str, Path] = get_all_protocol_files()
        protocol_names: list[str] = list(protocol_files.keys())

        return protocol_names

    # return the only one protocol
    return [protocol]

# build the combination prompt name.
def _build_combination_prompt_name(protocol: str, model_name: str, profile_name: ProfileName, output_control_name: str) -> str:
    safe_model_name: str = model_name.replace(":", "_").replace("/", "_")
    safe_profile_name: str = profile_name.value.replace("-", "_")

    prompt_name: str = f"{protocol}_{safe_model_name}_{safe_profile_name}_{output_control_name}"

    return prompt_name

# run all selected protocol prompts for one model condition
def _run_model_combination(combination_prompts: dict[str, str], protocol_names: list[str], output_controls: dict[str, OutputControl], 
                           connection: OllamaConnection, model_config: ModelConfig, profile_name: ProfileName, model_profile: ModelProfile) -> list[Path]:

    # init the respones files list
    response_files: list[Path] = []

    print(f"Starting model combination: model={model_config['name'].value}, profile={profile_name.value}")

    # loop the output format
    for output_control_name, output_control in output_controls.items():
        for protocol in protocol_names:
            prompt_name: str = _build_combination_prompt_name(protocol=protocol, model_name=model_config["name"].value, profile_name=profile_name, output_control_name=output_control_name)

            prompt: str | None = combination_prompts.get(prompt_name)

            if prompt is None:
                print(f"Skipped missing combination prompt: {prompt_name}")
                continue

            print(f"Running combination prompt: {prompt_name}")

            ollama_response: dict[str, object] = call_ollama_generate(ollama_url=connection["ollama_url"], model=model_config["name"].value, prompt=prompt, 
                                                                      options=model_profile["options"], request_timeout_seconds=connection["request_timeout_seconds"], 
                                                                      think=model_profile["think"], output_format=output_control["request_format"], extra_headers=connection["extra_headers"])

            # copy the response
            response_copy: dict[str, object] = dict(ollama_response)

            # remove the contenxt
            response_copy.pop("context", None)

            # record the prompt and profile names.
            response_copy["prompt_name"] = prompt_name
            response_copy["profile_name"] = profile_name.value

            output_file: Path = PROMPT_EXPERIMENT_COMBINATION_RESPONSES_DIR / f"{prompt_name}_combination_response.json"

            save_json_file(file_path=output_file, data=response_copy)

            response_files.append(output_file)

            print(f"Saved combination response: {output_file}")

    print(f"Completed model combination: model={model_config['name'].value}, profile={profile_name.value}")

    return response_files

def combination_psm(combination_prompts: dict[str, str], arguments: PromptExperimentArguments) -> list[Path]:
    connection: OllamaConnection = get_ollama_connection(connection_mode=arguments["connection_mode"])

    model_configs: list[ModelConfig] = get_selected_model_configs(model_name=arguments["model"])
    protocol_names: list[str] = _get_selected_protocol_names(protocol=arguments["protocol"])
    output_controls: dict[str, OutputControl] = get_selected_output_controls(output_control_name=arguments["output_control"])

    response_files: list[Path] = []

    # loop the model to run 
    for model_config in model_configs:
        profile_names: list[ProfileName] = get_selected_profile_names(model_config=model_config, profile=arguments["profile"])

        # loop for think (only qwen9b, qwen27b, qwq)
        for profile_name in profile_names:
            model_profile: ModelProfile = get_model_profile(profile_name=profile_name)

            model_response_files: list[Path] = _run_model_combination(combination_prompts=combination_prompts, protocol_names=protocol_names, output_controls=output_controls, 
                                                                      connection=connection, model_config=model_config, profile_name=profile_name, model_profile=model_profile)

            response_files.extend(model_response_files)

    return response_files

def main() -> None:
    arguments: PromptExperimentArguments = read_command_line_to_value()

    combination_prompts: dict[str, str] = _load_combination_prompts()

    response_files: list[Path] = combination_psm(combination_prompts=combination_prompts, arguments=arguments)

    print(f"Completed Ollama combination. Saved {len(response_files)} response files.")


if __name__ == "__main__":
    main()