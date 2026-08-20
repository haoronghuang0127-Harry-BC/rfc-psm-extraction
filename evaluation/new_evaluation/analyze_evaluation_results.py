from pathlib import Path
from typing import Final

import pandas as pd

from config.paths import PSMBENCH_NEW_EVALUATION_OUTPUT_DIR, PSMBENCH_ORIGINAL_EVALUATION_OUTPUT_DIR, PSMBENCH_OUTPUT_DIR

# the original state evaluation result
ORIGINAL_STATE_FILE: Final[Path] = PSMBENCH_ORIGINAL_EVALUATION_OUTPUT_DIR / "states_match_results.csv"
# the original exact transition evaluation result
ORIGINAL_EXACT_FILE: Final[Path] = PSMBENCH_ORIGINAL_EVALUATION_OUTPUT_DIR / "transitions_match_results_whole.csv"
# the original partial transition evaluation result
ORIGINAL_PARTIAL_FILE: Final[Path] = PSMBENCH_ORIGINAL_EVALUATION_OUTPUT_DIR / "transitions_match_results_partial.csv"

# the new state evaluation result
NEW_STATE_FILE: Final[Path] = PSMBENCH_NEW_EVALUATION_OUTPUT_DIR / "states_match_results.csv"
# the new exact transition evaluation result
NEW_EXACT_FILE: Final[Path] = PSMBENCH_NEW_EVALUATION_OUTPUT_DIR / "transitions_match_results_whole.csv"
# the new partial transition evaluation result
NEW_PARTIAL_FILE: Final[Path] = PSMBENCH_NEW_EVALUATION_OUTPUT_DIR / "transitions_match_results_partial.csv"

# the final summary CSV file
SUMMARY_OUTPUT_FILE: Final[Path] = PSMBENCH_OUTPUT_DIR / "psmbench_original_vs_new_evaluation_summary.csv"


def build_summary_row(metric_name: str, original_file: Path, new_file: Path) -> dict[str, object]:

    # load original and new csv file
    original_df = pd.read_csv(original_file)
    new_df = pd.read_csv(new_file)

    # calculate original precision, recall, f1 score
    original_mean_precision: float = float(original_df["Precision"].mean())
    original_mean_recall: float = float(original_df["Recall"].mean())
    original_mean_f1: float = float(original_df["F1-Score"].mean())

    # calculate new precision, recall, f1 score
    new_mean_precision: float = float(new_df["Precision"].mean())
    new_mean_recall: float = float(new_df["Recall"].mean())
    new_mean_f1: float = float(new_df["F1-Score"].mean())

    # build the summary row
    summary_row: dict[str, object] = {
        "Metric": metric_name,
        "Total Conditions": len(original_df),
        "Original Mean Precision": round(original_mean_precision, 3),
        "Original Mean Recall": round(original_mean_recall, 3),
        "Original Mean F1": round(original_mean_f1, 3),
        "New Mean Precision": round(new_mean_precision, 3),
        "New Mean Recall": round(new_mean_recall, 3),
        "New Mean F1": round(new_mean_f1, 3),
        "Precision Difference": round(new_mean_precision - original_mean_precision, 3),
        "Recall Difference": round(new_mean_recall - original_mean_recall, 3),
        "F1 Difference": round(new_mean_f1 - original_mean_f1, 3)
    }

    return summary_row

def main() -> None:
    # init the rows list
    summary_rows: list[dict[str, object]] = []

    # calculate state
    state_summary = build_summary_row(metric_name="State", original_file=ORIGINAL_STATE_FILE, new_file=NEW_STATE_FILE)
    summary_rows.append(state_summary)

    # calculate the exact transition 
    exact_summary = build_summary_row(metric_name="Exact Transition", original_file=ORIGINAL_EXACT_FILE, new_file=NEW_EXACT_FILE)
    summary_rows.append(exact_summary)
    
    # calculate the partial transition
    partial_summary = build_summary_row(metric_name="Partial Transition", original_file=ORIGINAL_PARTIAL_FILE, new_file=NEW_PARTIAL_FILE)
    summary_rows.append(partial_summary)

    # change to DataFrame
    summary_df = pd.DataFrame(summary_rows)

    SUMMARY_OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    # save to csv
    summary_df.to_csv(SUMMARY_OUTPUT_FILE, index=False, encoding="utf-8-sig")

    print("PSMBench evaluation summary completed.")
    print(f"Saved to: {SUMMARY_OUTPUT_FILE}")


if __name__ == "__main__":
    main()