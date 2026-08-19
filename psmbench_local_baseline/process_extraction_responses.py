from pathlib import Path
from config.paths import PSMBENCH_LOCAL_BASELINE_ORIGINAL_RESPONSES_DIR, PSMBENCH_LOCAL_BASELINE_PARTIAL_FSMS_DIR

from utils.llm_output_parser import parse_json_from_response
from utils.files_util import load_json_file, save_json_file

# load the ortiginal response files
def _get_original_response_files() -> list[Path]:
    response_files: list[Path] = PSMBENCH_LOCAL_BASELINE_ORIGINAL_RESPONSES_DIR.glob("*_extraction_responses.json")

    return sorted(response_files)

def _extract_partial_responses(response_records: list[dict[str, object]]) -> list[str]:
    # init the result
    partial_responses: list[str] = []

    for record in response_records:
        response: object = record.get("response")

        # remove the none part of not string 
        if not isinstance(response, str):
            continue

        # parse <json>...</json>
        parsed_response: object | None = parse_json_from_response(response=response, allow_direct_json=True)

        if parsed_response is None:
            continue

        partial_responses.append(response)

    return partial_responses

def _get_partial_fsms_file_path(original_file_path: Path) -> Path:
    original_suffix: str = "_extraction_responses"

    # remove the original response suffix.
    base_file_name: str = original_file_path.stem.removesuffix(original_suffix)

    output_file_name: str = f"{base_file_name}_partial_fsms.json"

    output_file_path: Path = PSMBENCH_LOCAL_BASELINE_PARTIAL_FSMS_DIR / output_file_name

    return output_file_path

def process_extraction_responses():
    original_response_files: list[Path] = _get_original_response_files()

    for file_path in original_response_files:
        response: list[dict[str, object]] = load_json_file(file_path=file_path, data_type=list[dict[str, object]])

        partial_responses: list[str] = _extract_partial_responses(response_records=response)

        output_file_path: Path = _get_partial_fsms_file_path(original_file_path=file_path)

        save_json_file(file_path=output_file_path, data=partial_responses)

        print(f"Saved {len(partial_responses)} valid partial FSM responses: {output_file_path}")
        

    return 

def main() -> None:

    process_extraction_responses()


if __name__ == "__main__":
    main()