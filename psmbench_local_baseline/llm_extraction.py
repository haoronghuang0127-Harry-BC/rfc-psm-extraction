from config.ollama_settings import OllamaConnection, get_ollama_connection
from config.paths import PSMBENCH_LOCAL_BASELINE_EXTRACTION_PROMPTS

from utils.files_util import load_json_file
from utils.ollama_client import call_ollama_generate


def _get_extraction_prompts_dict_by_files() ->  dict[str, list[str]]:
    extraction_prompts_dict: dict[str, list[str]] = load_json_file(file_path=PSMBENCH_LOCAL_BASELINE_EXTRACTION_PROMPTS,
                                                                   data_type=dict[str, list[str]])

    return extraction_prompts_dict


def extraction_psm(extraction_prompts_dict: dict[str, list[str]]) -> None:

    for protocol, prompts in extraction_prompts_dict.items():
        # init the protocol each prompts' response
        protocol_response: list[str] = []

        # get the total prompts
        prompts_num: int = len(prompts)

        print(f"Processing protocol:{protocol} Prompt count:{prompts_num}")

        for index, prompt in enumerate(prompts, start=1):
            print(f"{protocol}: {index}/{prompts_num}")
            connection: OllamaConnection

            ollama_response: dict[str, object] = _get_ollama_response()

    return 


def main() -> None:
    extraction_prompts_dict: dict[str, list[str]] = _get_extraction_prompts_dict_by_files()
    extraction_psm(extraction_prompts_dict)
    return 
    
if __name__ == "__main__":
    main()