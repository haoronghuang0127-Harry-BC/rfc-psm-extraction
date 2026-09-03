from pathlib import Path

from config.paths import RECURSIVE_SECTION_SPLITTING_COMBINATION_RESPONSES_DIR, RECURSIVE_SECTION_SPLITTING_FINAL_FSMS_DIR

from research_pipeline.response_processing import extract_final_fsm_from_response

from utils.files_util import load_json_file, save_json_file


# build the final FSM file path.
def _get_final_fsm_file_path(response_file_path: Path) -> Path:
    response_file_suffix: str = "_combination_response"

    final_fsm_name: str = response_file_path.stem.removesuffix(response_file_suffix)
    final_fsm_file_name: str = f"{final_fsm_name}_final_fsm.json"

    final_fsm_file_path: Path = RECURSIVE_SECTION_SPLITTING_FINAL_FSMS_DIR / final_fsm_file_name

    return final_fsm_file_path


# extract and save all recursive section final FSMs.
def extract_final_fsms() -> list[Path]:
    combination_response_files: list[Path] = sorted(RECURSIVE_SECTION_SPLITTING_COMBINATION_RESPONSES_DIR.glob("*_combination_response.json"))

    final_fsm_files: list[Path] = []

    response_files_num: int = len(combination_response_files)

    for index, response_file_path in enumerate(combination_response_files, start=1):
        print(f"Extracting final FSM: {index}/{response_files_num} {response_file_path.name}")

        combination_response: dict[str, object] = load_json_file(file_path=response_file_path, data_type=dict[str, object])
        final_fsm: dict[str, object] | None = extract_final_fsm_from_response(combination_response=combination_response, allow_direct_json=True)
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
