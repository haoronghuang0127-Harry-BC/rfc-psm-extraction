from pathlib import Path

from config.paths import WHOLE_DOCUMENT_REFERENCE_FINAL_FSMS_DIR, WHOLE_DOCUMENT_REFERENCE_ORIGINAL_RESPONSES_DIR

from research_pipeline.response_processing import extract_final_fsm_from_response

from utils.files_util import load_json_file, save_json_file


# build the final FSM file path.
def _get_final_fsm_file_path(response_file_path: Path) -> Path:
    response_file_suffix: str = "_extraction_responses"

    final_fsm_name: str = response_file_path.stem.removesuffix(response_file_suffix)
    final_fsm_file_name: str = f"{final_fsm_name}_final_fsm.json"

    final_fsm_file_path: Path = WHOLE_DOCUMENT_REFERENCE_FINAL_FSMS_DIR / final_fsm_file_name

    return final_fsm_file_path


# extract and save all whole document final FSMs.
def extract_final_fsms() -> list[Path]:
    extraction_response_files: list[Path] = sorted(WHOLE_DOCUMENT_REFERENCE_ORIGINAL_RESPONSES_DIR.glob("*_extraction_responses.json"))

    final_fsm_files: list[Path] = []

    response_files_num: int = len(extraction_response_files)

    for index, response_file_path in enumerate(extraction_response_files, start=1):
        print(f"Extracting final FSM: {index}/{response_files_num} {response_file_path.name}")

        response_records: list[dict[str, object]] = load_json_file(file_path=response_file_path, data_type=list[dict[str, object]])

        if len(response_records) == 1:
            final_fsm: dict[str, object] | None = extract_final_fsm_from_response(combination_response=response_records[0], allow_direct_json=True)
        else:
            final_fsm = None

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
