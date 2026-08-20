from pathlib import Path
import csv
from typing import Final

# the suffix of every final FSM file.
FINAL_FSM_SUFFIX: Final[str] = "_final_fsm"

# get the file and model from the final fsm file
def get_protocol_and_model(final_fsm_file: Path) -> tuple[str, str]:
    # remove the suffix
    file_name = final_fsm_file.stem.removesuffix(FINAL_FSM_SUFFIX)

    # get the protocol and model name from the file
    protocol, separator, model_name = file_name.partition("_")

    return protocol.upper(), model_name

def calculate_precision_recall_f1(TP: int, TP_FP: int, TP_FN: int) -> tuple[float, float, float]:
    # init precision, recall and f1
    precision: float = 0.0
    recall: float = 0.0
    f1: float = 0.0 

    # calculate precision
    # Precision = TP / (TP + FP)
    if TP_FP > 0:
        precision = TP / TP_FP

    # calculate recall
    # Recall = TP / (TP + FN)
    if TP_FN > 0:
        recall = TP / TP_FN

    # calculate f1
    # f1 = (2 * precision * recall) / (precision + recall)
    total: float = precision + recall
    if total > 0:
        f1 = (2.0 * precision * recall) / total

    return precision, recall, f1
    


def build_state_row(protocol: str, model_name: str, state_result: dict[str, object]) -> dict[str, object]:

    total_extracted = int(state_result["llm_predicted_count"])
    total_ground_truth = int(state_result["ground_truth_count"])
    matched_count = int(state_result["matched_count"])

    # get precision, recall and f1
    precision, recall, f1 = calculate_precision_recall_f1(TP=matched_count,TP_FP=total_extracted,TP_FN=total_ground_truth)

    row: dict[str, object] = {
        "Protocol": protocol,
        "Model": model_name,
        "Total Extracted": total_extracted,
        "Total GT": total_ground_truth,
        "Matched": matched_count,
        "Precision": round(precision, 3),
        "Recall": round(recall, 3),
        "F1-Score": round(f1, 3),
    }

    return row


def build_transition_row(protocol: str, model_name: str, transition_result: dict[str, object]) -> dict[str, object]:

    total_extracted = int(transition_result["llm_predicted_count"])
    total_ground_truth = int(transition_result["ground_truth_count"])
    matched_count = int(transition_result["matched_count"])

    unmatched_ground_truth: int = total_ground_truth - matched_count
    unmatched_extracted: int = total_extracted - matched_count

    # get precision, recall and f1
    precision, recall, f1 = calculate_precision_recall_f1(TP=matched_count,TP_FP=total_extracted,TP_FN=total_ground_truth)

    row: dict[str, object] = {
        "Protocol": protocol,
        "Model": model_name,
        "TotalExtracted": total_extracted,
        "TotalGT": total_ground_truth,
        "Matched": matched_count,
        "UnmatchedGT": unmatched_ground_truth,
        "UnmatchedExtracted": unmatched_extracted,
        "Precision": round(precision, 3),
        "Recall": round(recall, 3),
        "F1-Score": round(f1, 3),
    }

    return row



def save_csv(rows: list[dict[str, object]], output_file: Path) -> None:

    output_file.parent.mkdir(parents=True, exist_ok=True)

    field_names: list[str] = list(rows[0].keys())

    with output_file.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=field_names)

        writer.writeheader()
        writer.writerows(rows)