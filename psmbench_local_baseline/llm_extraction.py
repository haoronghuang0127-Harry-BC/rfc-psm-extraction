from pathlib import Path

from config.models.model_names import ModelName
from config.models.model_profiles import ModelProfile, get_model_profile
from config.models.model_registry import get_all_model_configs, get_model_config
from config.models.model_types import ModelConfig, ProfileName
from config.ollama_settings import ConnectionMode, OllamaConnection, get_ollama_connection
from config.paths import PSMBENCH_LOCAL_BASELINE_EXTRACTION_PROMPTS, PSMBENCH_LOCAL_BASELINE_RESPONSES_DIR

from psmbench_local_baseline.command_line import read_command_line_to_value
from psmbench_local_baseline.types import Arguments

from utils.files_util import load_json_file, save_json_file
from utils.ollama_client import call_ollama_generate


def _get_extraction_prompts_dict_by_files() ->  dict[str, list[str]]:
    # check if the file exist
    if not PSMBENCH_LOCAL_BASELINE_EXTRACTION_PROMPTS.is_file():
        raise FileNotFoundError(f"Could not find the extraction prompts files: {PSMBENCH_LOCAL_BASELINE_EXTRACTION_PROMPTS}")


    extraction_prompts_dict: dict[str, list[str]] = load_json_file(file_path=PSMBENCH_LOCAL_BASELINE_EXTRACTION_PROMPTS,
                                                                   data_type=dict[str, list[str]])

    return extraction_prompts_dict

def _get_selected_extraction_prompts_dict(protocol: str, extraction_prompts_dict: dict[str, list[str]]) -> dict[str, list[str]]:
    # return all the prompts
    if protocol == "all":
        return extraction_prompts_dict

    if protocol not in extraction_prompts_dict:
        raise KeyError(f"Could not find protocol: {protocol}")

    return {
        protocol: extraction_prompts_dict[protocol]
    }

def _get_selected_model_configs(selected_model: ModelName) -> list[ModelConfig]:
    # if input all return all the model config
    if selected_model == ModelName.ALL:
        return get_all_model_configs()

    # init the result list
    result: list[ModelConfig] = []

    # get the model config
    selected_model_config: ModelConfig = get_model_config(model_name=selected_model)
    # add to the list
    result.append(selected_model_config)

    return result

def _get_extraction_response_file_path(protocol: str, model_name: str, profile_name: ProfileName) -> Path:

    model_name = model_name.replace(":","_").replace("/","_")

    # The suffix is only used for switchable Qwen models.
    thinking: str = ""
    if profile_name == ProfileName.QWEN_NO_THINK:
        thinking = "_no_think"

    if profile_name == ProfileName.QWEN_THINK:
        thinking = "_think"

    file_name: str = f"{protocol}_{model_name}{thinking}_extraction_responses.json"

    file_path: Path = PSMBENCH_LOCAL_BASELINE_RESPONSES_DIR / "original" / file_name

    return file_path

def _get_selected_profile_name(model_config: ModelConfig, thinking: bool) -> ProfileName:
    # if thinking default return the default profile
    if not thinking:
        return model_config["default_profile"]

    if ProfileName.QWEN_THINK in model_config["supported_profiles"]:
        return ProfileName.QWEN_THINK

    raise ValueError("Thinking can only be enabled for qwen3.5:9b and qwen3.5:27b.")

def _get_ollama_response(prompt: str, connection: OllamaConnection, model_config: ModelConfig, model_profile: ModelProfile) -> dict[str, object]:
    # get the ollama url
    url: str = connection["ollama_url"]
    # get the using model
    model: str = model_config["name"].value
    # get the options
    options: dict[str, int | float] = model_profile["options"]
    # get request_timeout_seconds
    request_timeout_seconds: int = connection["request_timeout_seconds"]
    # get if uisng think model
    think: bool | None = model_profile["think"]
    # set the output format
    output_format = None
    # get the header
    headers: dict[str, str] = connection["extra_headers"]

    # get the ollama response
    response: dict[str, object] = call_ollama_generate(ollama_url=url, model=model, prompt=prompt, options=options,
                                                       request_timeout_seconds=request_timeout_seconds, think=think,
                                                       output_format=output_format, extra_headers=headers)

    return response

def _extraction_psm(extraction_prompts_dict: dict[str, list[str]], arguments: Arguments, model_config_list: list[ModelConfig]) -> None:
    # get the ollama connection
    connection: OllamaConnection = get_ollama_connection(connection_mode=arguments["connection_mode"])

    # loop the choosing model
    for model_config in model_config_list:
        print(f"Starting extraction with model: {model_config['name'].value}")

        # get the model profile
        profile_name: ProfileName = _get_selected_profile_name(model_config=model_config, thinking=arguments["thinking"])
        model_profile: ModelProfile = get_model_profile(profile_name=profile_name)

        # loop the choosing protocol
        for protocol, prompts in extraction_prompts_dict.items():
            # get the ollama response save path
            output_file_path: Path = _get_extraction_response_file_path(protocol=protocol, model_name=model_config["name"].value,
                                                                        profile_name=profile_name)
            
            # init the protocol each prompts' response
            protocol_response: list[dict[str, object]] = []
    
            # get the total prompts
            prompts_num: int = len(prompts)
    
            print(f"Processing protocol:{protocol} Prompt count:{prompts_num}")

            # extracntion through each prompts
            for index, prompt in enumerate(prompts, start=1):
                print(f"{protocol}: {index}/{prompts_num}")
    
                ollama_response: dict[str, object] = _get_ollama_response(prompt=prompt, connection=connection, model_config=model_config,
                                                                            model_profile=model_profile)

                # copy the response
                response_copy: dict[str, object] = dict(ollama_response)

                # remove the token id array
                response_copy.pop("context", None)

                # record the index
                response_copy["prompt_index"] = index

                protocol_response.append(response_copy)

                # save the response
                save_json_file(file_path=output_file_path, data=protocol_response)

            print(f"Save file in {output_file_path}")


def extraction_psm(extraction_prompts_dict: dict[str, list[str]]) -> None:

    all_default_arguments: Arguments = {
        "protocol": "all",
        "model": ModelName.ALL,
        "connection_mode": ConnectionMode.AUTO,
        "thinking": False
    }

    all_model_configs: list[ModelConfig] = get_all_model_configs()

    print("Starting all models with their default profiles.")

    _extraction_psm(extraction_prompts_dict=extraction_prompts_dict, arguments=all_default_arguments, model_config_list=all_model_configs)



    # Qwen 9B with thinking enabled.
    qwen_9b_thinking_arguments: Arguments = {
        "protocol": "all",
        "model": ModelName.QWEN3_5_9B,
        "connection_mode": ConnectionMode.AUTO,
        "thinking": True,
    }

    qwen_9b_model_configs: list[ModelConfig] = [get_model_config(model_name=ModelName.QWEN3_5_9B)]

    print("Starting qwen3.5:9b with thinking enabled.")

    _extraction_psm(extraction_prompts_dict=extraction_prompts_dict, arguments=qwen_9b_thinking_arguments, model_config_list=qwen_9b_model_configs)



    # Qwen 27B with thinking enabled.
    qwen_27b_thinking_arguments: Arguments = {
        "protocol": "all",
        "model": ModelName.QWEN3_5_27B,
        "connection_mode": ConnectionMode.AUTO,
        "thinking": True,
    }

    qwen_27b_model_configs: list[ModelConfig] = [get_model_config(model_name=ModelName.QWEN3_5_27B)]

    print("Starting qwen3.5:27b with thinking enabled.")

    _extraction_psm(extraction_prompts_dict=extraction_prompts_dict, arguments=qwen_27b_thinking_arguments, model_config_list=qwen_27b_model_configs)
    

def main() -> None:
    # first to check if the extraction prompts is exist
    extraction_prompts_dict: dict[str, list[str]] = _get_extraction_prompts_dict_by_files()

    # read the value from the command line
    arguments: Arguments = read_command_line_to_value()

    # select the requested protocols
    selected_extraction_prompts_dict: dict[str, list[str]] = _get_selected_extraction_prompts_dict( protocol=arguments["protocol"], extraction_prompts_dict=extraction_prompts_dict)

    # get the using model
    selected_model_config: list[ModelConfig] = _get_selected_model_configs(selected_model=arguments["model"])

    # extractio psm through ollama
    _extraction_psm(extraction_prompts_dict=selected_extraction_prompts_dict, arguments=arguments,
                    model_config_list=selected_model_config)
    
if __name__ == "__main__":
    main()