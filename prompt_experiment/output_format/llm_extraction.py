from pathlib import Path

from config.models.model_profiles import ModelProfile, get_model_profile
from config.models.model_types import ModelConfig, ProfileName
from config.ollama_settings import OllamaConnection, get_ollama_connection
from config.paths import PROMPT_EXPERIMENT_ORIGINAL_RESPONSES_DIR, PROMPT_EXPERIMENT_PROMPTS_DIR

from prompt_experiment.output_format.command_line import read_command_line_to_value
from prompt_experiment.types import PromptExperimentArguments

from research_pipeline.model_selection import get_selected_model_configs, get_selected_profile_names
from research_pipeline.output_controls import get_output_control, get_selected_output_controls
from research_pipeline.types import OutputControl

from utils.files_util import save_json_file, load_json_file
from utils.ollama_client import call_ollama_with_model_routing

# load extraction prompts for one output control from a local file.
def _load_extraction_prompts(output_control_name: str) -> dict[str, list[str]]:
    

    prompts_file: Path = PROMPT_EXPERIMENT_PROMPTS_DIR / f"{output_control_name}_extraction_prompts.json"

    if not prompts_file.is_file():
        raise FileNotFoundError(f"Could not find the extraction Prompt file: {prompts_file}")

    extraction_prompts: dict[str, list[str]] = load_json_file(file_path=prompts_file, data_type=dict[str, list[str]])

    print(f"Loaded extraction Prompts: {prompts_file}")

    return extraction_prompts

# load the selected output control and protocol prompts.
def _load_selected_extraction_prompts(protocol: str, output_control_name: str) -> dict[str, dict[str, list[str]]]:
    selected_output_controls: dict[str, OutputControl] = get_selected_output_controls(output_control_name=output_control_name)

    all_extraction_prompts: dict[str, dict[str, list[str]]] = {}

    for selected_output_control_name in selected_output_controls.keys():
        extraction_prompts: dict[str, list[str]] = _load_extraction_prompts(output_control_name=selected_output_control_name)

        if protocol == "all":
            selected_protocol_prompts: dict[str, list[str]] = extraction_prompts
        else:
            selected_protocol_prompts = {
                protocol: extraction_prompts[protocol]
            }

        all_extraction_prompts[selected_output_control_name] = selected_protocol_prompts

    return all_extraction_prompts


def _build_save_response_path(protocol: str, model_name: str, profile_name: ProfileName, output_control_name: str) -> Path:
    # replace characters that are unsuitable for file names.
    safe_model_name: str = model_name.replace(":", "_").replace("/", "_")
    safe_profile_name: str = profile_name.value.replace("-", "_")

    file_name: str = f"{protocol}_{safe_model_name}_{safe_profile_name}_{output_control_name}_extraction_responses.json"

    output_file: Path = PROMPT_EXPERIMENT_ORIGINAL_RESPONSES_DIR / file_name

    return output_file

def _run_extraction_psm(protocol: str, prompts: list[str], model_config: ModelConfig, profile_name: ProfileName, model_profile: ModelProfile, output_control_name: str, output_control: OutputControl, connection: OllamaConnection) -> Path:
    response_records: list[dict[str, object]] = []

    prompt_count: int = len(prompts)

    print(f"Starting extraction: protocol={protocol}, model={model_config['name'].value}, profile={profile_name.value}, output={output_control_name}, prompts={prompt_count}")

    for index, prompt in enumerate(prompts, start=1):
        print(f"{protocol}: extraction Prompt {index}/{prompt_count}")

        ollama_response: dict[str, object] = call_ollama_with_model_routing(ollama_url=connection["ollama_url"], model=model_config["name"].value,
                                                                  prompt=prompt, options=model_profile["options"], request_timeout_seconds=connection["request_timeout_seconds"],
                                                                  think=model_profile["think"], output_format=output_control["request_format"], extra_headers=connection["extra_headers"])

        # copy the response
        response_copy: dict[str, object] = dict(ollama_response)

        # remove the token id array
        response_copy.pop("context", None)

        # record the index
        response_copy["prompt_index"] = index

        response_records.append(response_copy)

    output_file: Path = _build_save_response_path(protocol=protocol, model_name=model_config["name"].value, 
                                                  profile_name=profile_name, output_control_name=output_control_name)

    save_json_file(file_path=output_file, data=response_records)

    print(f"Saved extraction responses: {output_file}")

    return output_file

def extraction_psm(all_extraction_prompts: dict[str, dict[str, list[str]]], arguments: PromptExperimentArguments) -> list[Path]:
    connection: OllamaConnection = get_ollama_connection(connection_mode=arguments["connection_mode"])

    model_configs: list[ModelConfig] = get_selected_model_configs(model_name=arguments["model"])

    response_files: list[Path] = []

    # model for
    for model_config in model_configs:
        profile_names: list[ProfileName] = get_selected_profile_names(model_config=model_config, profile=arguments["profile"])

        # if thinking (just qwen model)
        for profile_name in profile_names:
            model_profile: ModelProfile = get_model_profile(profile_name=profile_name)

            # otuput format
            for output_control_name, extraction_prompts in all_extraction_prompts.items():
                output_control: OutputControl = get_output_control(output_control_name=output_control_name)

                for protocol, prompts in extraction_prompts.items():
                    response_file: Path = _run_extraction_psm(protocol=protocol, prompts=prompts, model_config=model_config,
                                                              profile_name=profile_name, model_profile=model_profile, output_control_name=output_control_name,
                                                              output_control=output_control, connection=connection)

                    response_files.append(response_file)



    return response_files

def main() -> None:
    arguments: PromptExperimentArguments = read_command_line_to_value()

    all_extraction_prompts: dict[str, dict[str, list[str]]] = _load_selected_extraction_prompts(protocol=arguments["protocol"], output_control_name=arguments["output_control"])

    response_files: list[Path] = extraction_psm(all_extraction_prompts=all_extraction_prompts, arguments=arguments)

    print(f"Completed Ollama extraction. Saved {len(response_files)} response files.")


if __name__ == "__main__":
    main()