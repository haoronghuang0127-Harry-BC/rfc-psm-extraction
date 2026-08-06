import csv

from pathlib import Path

from evaluation.evaluation_io import get_evaluation_result_file, get_llm_output_fsm_files
from evaluation.evaluation_types import EvaluationResult, MetricResult

from utils.files_util import load_json_file


# Add the common values of one evaluation metric to a CSV row.
def _add_metric_values(row: dict[str, object], prefix: str, metric_result: MetricResult) -> None:

    row[f"{prefix}_matched_count"] = metric_result["matched_count"]
    row[f"{prefix}_missing_count"] = metric_result["missing_count"]
    row[f"{prefix}_extra_count"] = metric_result["extra_count"]
    row[f"{prefix}_precision"] = metric_result["precision"]
    row[f"{prefix}_recall"] = metric_result["recall"]
    row[f"{prefix}_f1"] = metric_result["f1"]

# Build one CSV row for one experiment.
def _build_summary_row(fsm_file: Path) -> dict[str, object]:
    # get the evaluation result file
    evaluation_result_file: Path = get_evaluation_result_file(final_fsm_file=fsm_file)

    # get the experiment result file
    experiment_result_file: Path = fsm_file.parent / "experiment_result.json"

    # load two files
    evaluation_result: EvaluationResult = load_json_file(file_path=evaluation_result_file, data_type=EvaluationResult)
    experiment_result: dict[str, object] = load_json_file(file_path=experiment_result_file, data_type=dict[str, object])

    # Get the three evaluation results.
    state_result: MetricResult = evaluation_result["states"]
    exact_transition_result: MetricResult = evaluation_result["exact_transitions"]
    partial_transition_result: MetricResult = evaluation_result["partial_transitions"]


    # convert structure errors into one CSV value.
    structure_error: str = "; ".join(evaluation_result["structure_errors"])

    # convert max_sections None to "all"
    # in the json file, when the experiment use command line max_sections=all the result will save the max_section=null
    max_sections: object = experiment_result.get("max_sections")
    if max_sections is None:
        max_sections = "all"


    # store the experiment information
    row: dict[str, object] = {
        "protocol": experiment_result.get("protocol", ""),
        "scoring_method": experiment_result.get("scoring_method", ""),
        "input_version": experiment_result.get("input_version", ""),
        "model_name": experiment_result.get("model_name", ""),
        "profile_name": experiment_result.get("profile_name", ""),
        "output_format_name": experiment_result.get("output_format_name", ""),
        "seed": experiment_result.get("seed", ""),
        "max_sections": max_sections,
        "parsed": evaluation_result["parsed"],
        "structure_valid": evaluation_result["structure_valid"],
        "structure_error": structure_error,
    }

    # add the number of predicted and reference states
    row["state_predicted_count"] = state_result["llm_predicted_count"]
    row["state_ground_truth_count"] = state_result["ground_truth_count"]
    # add the remaining state evaluation values
    _add_metric_values(row=row, prefix="state", metric_result=state_result)

    # add the number of predicted and reference transitions
    row["exact_transition_predicted_count"] = exact_transition_result["llm_predicted_count"]
    row["exact_transition_ground_truth_count"] = exact_transition_result["ground_truth_count"]

    # add the remaining exact transition evaluation values
    _add_metric_values(row=row, prefix="exact_transition", metric_result=exact_transition_result)
    # add the partial transition evaluation values
    _add_metric_values(row=row, prefix="partial_transition", metric_result=partial_transition_result)

    return row

        

# Create the evaluation summary CSV file.
def create_evaluation_summary(output_dir: Path) -> Path:
    # get all the psm files
    fsm_files: list[Path] = get_llm_output_fsm_files(output_dir=output_dir)

    if not fsm_files:
        raise ValueError(f"No final PSM files found in {output_dir}")

    summary_rows: list[dict[str, object]] = []

    for fsm_file in fsm_files:
        row: dict[str, object] = _build_summary_row(fsm_file=fsm_file)

        summary_rows.append(row)

    # set the summary.csv file path
    summary_file: Path = output_dir / "evaluation_summary.csv"

    # get the csv file field names
    field_names: list[str] = list(summary_rows[0].keys())

    # write the data in the file
    with summary_file.open("w", encoding="utf-8-sig", newline="") as file:
        writer: csv.DictWriter = csv.DictWriter(file, fieldnames=field_names)

        writer.writeheader()
        writer.writerows(summary_rows)

    return summary_file