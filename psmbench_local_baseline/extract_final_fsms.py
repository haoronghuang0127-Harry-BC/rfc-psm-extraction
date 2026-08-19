from pathlib import Path

from config.paths import PSMBENCH_LOCAL_BASELINE_COMBINATION_RESPONSE_DIR, PSMBENCH_LOCAL_BASELINE_FINAL_FSMS_DIR

from utils.files_util import load_json_file, save_json_file
from utils.llm_output_parser import parse_json_from_response

def _get_final_fsm_file_path(response_file_path: Path) -> Path:
    # remove the combination response suffix.
    response_file_suffix: str = "_combination_response"

    # set the final fsm name
    final_fsm_name: str = response_file_path.stem.removesuffix(response_file_suffix)
    final_fsm_file_name: str = (f"{final_fsm_name}_final_fsm.json")

    final_fsm_file_path: Path = PSMBENCH_LOCAL_BASELINE_FINAL_FSMS_DIR / final_fsm_file_name

    return final_fsm_file_path

def extract_final_fsms() -> None:
    # get the combination response file path
    combination_response_files: list[Path] = sorted(PSMBENCH_LOCAL_BASELINE_COMBINATION_RESPONSE_DIR.glob("*_combination_response.json"))

    # get the total number of response files.
    response_files_num: int = len(combination_response_files)

    for index, response_file_path in enumerate(combination_response_files, start=1):
        print(f"Extracting final FSM: {index}/{response_files_num} {response_file_path.name}")

        # load the combination response file
        combination_response: dict[str, object] = load_json_file(file_path=response_file_path, data_type=dict[str, object])

        response_value: object = combination_response.get("response")

        parsed_output: object | None = None
        if isinstance(response_value, str):
            # accept the requested <json>...</json> tag form as well as direct json
            # and Markdown jsob code blocks returned by some local models.
            parsed_output = parse_json_from_response(response=response_value, allow_direct_json=True)

        # save parsed json object and invalid or truncated responses remain null.
        if isinstance(parsed_output, dict):
            final_fsm = parsed_output
        else:
            final_fsm = None

        # get the final FSM output path.
        final_fsm_file_path: Path = _get_final_fsm_file_path(response_file_path=response_file_path)
        

        # save only the clean final FSM object.
        save_json_file(file_path=final_fsm_file_path, data=final_fsm)

        print(f"Saved final FSM: {final_fsm_file_path}")
        
    print("Completed final FSM extraction.")
        

def main() -> None:

    # Parse and save all final FSMs.
    extract_final_fsms()


if __name__ == "__main__":
    main()
