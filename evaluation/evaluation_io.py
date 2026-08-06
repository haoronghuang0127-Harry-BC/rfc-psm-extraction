import json

from pathlib import Path

from evaluation.evaluation_types import EvaluationResult


def get_llm_output_fsm_files(output_dir: Path) -> list[Path]:

    # check if the output dir exists
    if not output_dir.exists():
        raise FileNotFoundError(f"{output_dir} is not found.")

    # check the path is dir
    if not output_dir.is_dir():
        raise NotADirectoryError(f"{output_dir} is not a directory.")

    # find all the "final_fsm.json" in this path
    fsm_files: list[Path] = list(output_dir.rglob("final_fsm.json"))

    fsm_files.sort()

    return fsm_files

# Return the evaluation result file for one final PSM
def get_evaluation_result_file(final_fsm_file: Path) -> Path:
    evaluation_result_file: Path = final_fsm_file.parent / "evaluation_result.json"

    return evaluation_result_file

# Save evaluation result 
def save_evaluation_result(file_path: Path, evaluation_result: EvaluationResult) -> None:
    # create parent dir if not exists
    file_path.parent.mkdir(parents=True, exist_ok=True)

    # write the json file
    with file_path.open("w", encoding="utf-8") as file:
        json.dump(evaluation_result, file, ensure_ascii=False, indent=2)

    