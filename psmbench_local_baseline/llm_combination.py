from pathlib import Path

from config.models.model_names import ModelName
from config.models.model_profiles import ModelProfile, get_model_profile
from config.models.model_registry import get_model_config
from config.models.model_types import ModelConfig, ProfileName
from config.ollama_settings import ConnectionMode, OllamaConnection, get_ollama_connection
from config.paths import PSMBENCH_LOCAL_BASELINE_COMBINATION_PROMPTS, PSMBENCH_LOCAL_BASELINE_COMBINATION_RESPONSE_DIR

from psmbench_local_baseline.util import get_ollama_response

from utils.files_util import load_json_file, save_json_file

def _get_selected_combination_prompts_dict(combination_prompts_dict: dict[str, str], prompt_suffix: str) -> dict[str, str]:
    required_suffix: str = f"_{prompt_suffix}"

    # init dict
    selected_prompts_dict: dict[str, str] = {}

    for prompt_name, prompt in combination_prompts_dict.items():
        if prompt_name.endswith(required_suffix):
            selected_prompts_dict[prompt_name] = prompt

    return selected_prompts_dict

# run all protocol prompts for one model condition.
# this can reduce the time in the model swap
def _run_model_combination(combination_prompts_dict: dict[str, str], connection: OllamaConnection, model_name: ModelName, profile_name: ProfileName, prompt_suffix: str) -> None:
    selected_prompts_dict: dict[str, str] = _get_selected_combination_prompts_dict(combination_prompts_dict=combination_prompts_dict,
                                                                                   prompt_suffix=prompt_suffix)

    if not selected_prompts_dict:
        print(f"No found {prompt_suffix}, skip.")
        return

    # get the config and profile
    model_config: ModelConfig = get_model_config(model_name=model_name)
    model_profile: ModelProfile = get_model_profile(profile_name=profile_name)

    # get the num of the prompts
    prompts_num: int = len(selected_prompts_dict)
    print(f"Starting model combination: {model_name.value}, profile: {profile_name.value}, prompt count: {prompts_num}")

    for index, (prompt_name, prompt) in enumerate(selected_prompts_dict.items(), start=1):
        # get the ollama response
        ollama_response: dict[str, object] = get_ollama_response(prompt=prompt, connection=connection, model_config=model_config, model_profile=model_profile)

        # copy the response
        response_copy: dict[str, object] = dict(ollama_response)

        # remove the contenxt
        response_copy.pop("context", None)

        # set the prompt name and profile name to record
        response_copy["prompt_name"] = prompt_name
        response_copy["profile_name"] = profile_name.value

        # set the output path
        output_file_path: Path = PSMBENCH_LOCAL_BASELINE_COMBINATION_RESPONSE_DIR / f"{prompt_name}_combination_response.json"

        # save the file
        save_json_file(file_path=output_file_path, data=response_copy)

        print(f"Saved combination response: {output_file_path}")

    print(f"Completed model combination: {model_name.value}, profile: {profile_name.value}")
     


def combination_psm(combination_prompts_dict: dict[str, str]) -> None:

    # get the ollama connection
    connection: OllamaConnection = get_ollama_connection(connection_mode=ConnectionMode.AUTO)

    # qwen3.5_9b_no_think
    _run_model_combination(combination_prompts_dict=combination_prompts_dict,
                           connection=connection,
                           model_name=ModelName.QWEN3_5_9B,
                           profile_name=ProfileName.QWEN_NO_THINK,
                           prompt_suffix="qwen3.5_9b_no_think")

    # gemma3_12b
    _run_model_combination(combination_prompts_dict=combination_prompts_dict,
                                connection=connection,
                                model_name=ModelName.GEMMA3_12B,
                                profile_name=ProfileName.GEMMA_MISTRAL_NO_THINK,
                                prompt_suffix="gemma3_12b")

    # gemma3_27b
    _run_model_combination(combination_prompts_dict=combination_prompts_dict,
                                connection=connection,
                                model_name=ModelName.GEMMA3_27B,
                                profile_name=ProfileName.GEMMA_MISTRAL_NO_THINK,
                                prompt_suffix="gemma3_27b")

    # mistral-small3.1_24b
    _run_model_combination(combination_prompts_dict=combination_prompts_dict,
                                connection=connection,
                                model_name=ModelName.MISTRAL_SMALL3_1_24B,
                                profile_name=ProfileName.GEMMA_MISTRAL_NO_THINK,
                                prompt_suffix="mistral-small3.1_24b")

    # qwen3.5_27b_no_think
    _run_model_combination(combination_prompts_dict=combination_prompts_dict,
                                connection=connection,
                                model_name=ModelName.QWEN3_5_27B,
                                profile_name=ProfileName.QWEN_NO_THINK,
                                prompt_suffix="qwen3.5_27b_no_think")

    # qwen3.5_9b_think
    _run_model_combination(combination_prompts_dict=combination_prompts_dict,
                                connection=connection,
                                model_name=ModelName.QWEN3_5_9B,
                                profile_name=ProfileName.QWEN_THINK,
                                prompt_suffix="qwen3.5_9b_think")

    # qwen3.5_27b_think
    _run_model_combination(combination_prompts_dict=combination_prompts_dict,
                                    connection=connection,
                                    model_name=ModelName.QWEN3_5_27B,
                                    profile_name=ProfileName.QWEN_THINK,
                                    prompt_suffix="qwen3.5_27b_think")


    # qwq_32b
    _run_model_combination(combination_prompts_dict=combination_prompts_dict,
                                connection=connection,
                                model_name=ModelName.QWQ_32B,
                                profile_name=ProfileName.QWQ_REASONING,
                                prompt_suffix="qwq_32b")
    return


def main() -> None:

    # Load all combination prompts.
    combination_prompts_dict: dict[str, str] = load_json_file(file_path=PSMBENCH_LOCAL_BASELINE_COMBINATION_PROMPTS, data_type=dict[str, str])


    # Run the Ollama combination process.
    combination_psm(combination_prompts_dict=combination_prompts_dict)


if __name__ == "__main__":
    main()