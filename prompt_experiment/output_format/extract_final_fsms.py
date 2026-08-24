from pathlib import Path

from config.paths import PROMPT_EXPERIMENT_COMBINATION_RESPONSES_DIR, PROMPT_EXPERIMENT_FINAL_FSMS_DIR

from prompt_experiment.output_format.output_controls import get_output_control, get_output_control_name_from_experiment_name
from prompt_experiment.types import OutputControl

from research_pipeline.response_processing import extract_final_fsm_from_response

from utils.files_util import load_json_file, save_json_file


def _get_output_control_name(response_file_path: Path) -> str:
    response_file_suffix: str = "_combination_response"

    prompt_name: str = response_file_path.stem.removesuffix(response_file_suffix)

    output_control_name: str = get_output_control_name_from_experiment_name(prompt_name=prompt_name)

    return output_control_name



# build the final FSM file path.
def _get_final_fsm_file_path(response_file_path: Path) -> Path:
    response_file_suffix: str = "_combination_response"

    final_fsm_name: str = response_file_path.stem.removesuffix(response_file_suffix)
    final_fsm_file_name: str = f"{final_fsm_name}_final_fsm.json"

    final_fsm_file_path: Path = PROMPT_EXPERIMENT_FINAL_FSMS_DIR / final_fsm_file_name

    return final_fsm_file_path


# extract and save all final FSMs.
def extract_final_fsms() -> list[Path]:
    # get the combination response file path
    combination_response_files: list[Path] = sorted(PROMPT_EXPERIMENT_COMBINATION_RESPONSES_DIR.glob("*_combination_response.json"))

    final_fsm_files: list[Path] = []

    # get the total number of response files.
    response_files_num: int = len(combination_response_files)

    for index, response_file_path in enumerate(combination_response_files, start=1):
        print(f"Extracting final FSM: {index}/{response_files_num} {response_file_path.name}")

        # load the original combination response
        combination_response: dict[str, object] = load_json_file(file_path=response_file_path, data_type=dict[str, object])

        # get the output control used to produce this response.
        output_control_name: str = _get_output_control_name(response_file_path=response_file_path)
        output_control: OutputControl = get_output_control(output_control_name=output_control_name)
        prompt_output_style: str = output_control["prompt_output_style"]

        # choose json output  type
        allow_direct_json: bool = prompt_output_style == "direct_json"

        final_fsm: dict[str, object] | None = extract_final_fsm_from_response(combination_response=combination_response, allow_direct_json=allow_direct_json)

        final_fsm_file_path: Path = _get_final_fsm_file_path(response_file_path=response_file_path)

        # invalid or truncated responses are saved as null.
        save_json_file(file_path=final_fsm_file_path, data=final_fsm)

        final_fsm_files.append(final_fsm_file_path)

        if final_fsm is None:
            print(f"Saved invalid final FSM as null: {final_fsm_file_path}")
        else:
            print(f"Saved final FSM: {final_fsm_file_path}")

    print("Completed final FSM extraction.")

    return final_fsm_files

def main() -> None:
    final_fsm_files: list[Path] = extract_final_fsms()

    print(f"Completed final FSM processing. Saved {len(final_fsm_files)} final FSM files.")


if __name__ == "__main__":
    main()