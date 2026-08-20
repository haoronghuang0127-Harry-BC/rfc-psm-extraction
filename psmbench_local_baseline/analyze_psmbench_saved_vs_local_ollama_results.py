"""
analyze the new evaluation PSMBench result and the new evaluation local LLM result
"""

from pathlib import Path
from typing import Final

import pandas as pd

from config.paths import EVALUATION_OUTPUT_DIR, PSMBENCH_LOCAL_BASELINE_OUTPUT_DIR, PSMBENCH_NEW_EVALUATION_OUTPUT_DIR

# the new state evaluation result
NEW_STATE_FILE: Final[Path] = PSMBENCH_NEW_EVALUATION_OUTPUT_DIR / "states_match_results.csv"
# the new exact transition evaluation result
NEW_EXACT_FILE: Final[Path] = PSMBENCH_NEW_EVALUATION_OUTPUT_DIR / "transitions_match_results_whole.csv"
# the new partial transition evaluation result
NEW_PARTIAL_FILE: Final[Path] = PSMBENCH_NEW_EVALUATION_OUTPUT_DIR / "transitions_match_results_partial.csv"

# the local llm state evaluation result
STATE_OUTPUT_FILE: Final[Path] = EVALUATION_OUTPUT_DIR / "states_match_results.csv"
# the local llm exact transitione evaluation result
EXACT_TRANSITION_OUTPUT_FILE: Final[Path] = EVALUATION_OUTPUT_DIR / "transitions_match_results_whole.csv"
# the local llm partial transition evaluation result
PARTIAL_TRANSITION_OUTPUT_FILE: Final[Path] = EVALUATION_OUTPUT_DIR / "transitions_match_results_partial.csv"


# the final all-model summary CSV file
SUMMARY_OUTPUT_FILE: Final[Path] = PSMBENCH_LOCAL_BASELINE_OUTPUT_DIR / "psmbench_saved_vs_local_ollama_model_summary.csv"


def build_model_summary_rows(data_source: str, state_file: Path, exact_file: Path, partial_file: Path) -> list[dict[str, object]]:
    # load the state, exact transition, and partial transition csv files
    state_df = pd.read_csv(state_file)
    exact_df = pd.read_csv(exact_file)
    partial_df = pd.read_csv(partial_file)

    # get all model names
    model_names: list[str] = sorted(state_df["Model"].unique().tolist())

    # init the model summary rows
    summary_rows: list[dict[str, object]] = []

    for model_name in model_names:
        # get the state results of the selected model
        model_state_df = state_df[state_df["Model"] == model_name]
        # calculate state precision, recall, f1 score
        state_mean_precision: float = float(model_state_df["Precision"].mean())
        state_mean_recall: float = float(model_state_df["Recall"].mean())
        state_mean_f1: float = float(model_state_df["F1-Score"].mean())


        # get the exact transition results of the selected model
        model_exact_df = exact_df[exact_df["Model"] == model_name]
        # calculate exact transition precision, recall, f1 score
        exact_mean_precision: float = float(model_exact_df["Precision"].mean())
        exact_mean_recall: float = float(model_exact_df["Recall"].mean())
        exact_mean_f1: float = float(model_exact_df["F1-Score"].mean())


        # get the partial transition results of the selected model
        model_partial_df = partial_df[partial_df["Model"] == model_name]
        # calculate partial transition precision, recall, f1 score
        partial_mean_precision: float = float(model_partial_df["Precision"].mean())
        partial_mean_recall: float = float(model_partial_df["Recall"].mean())
        partial_mean_f1: float = float(model_partial_df["F1-Score"].mean())

        # build one model summary row
        summary_row: dict[str, object] = {
            "Data Source": data_source,
            "Model": model_name,
            "Total Protocols": len(model_state_df),
            "State Precision": round(state_mean_precision, 3),
            "State Recall": round(state_mean_recall, 3),
            "State F1": round(state_mean_f1, 3),
            "Exact Transition Precision": round(exact_mean_precision, 3),
            "Exact Transition Recall": round(exact_mean_recall, 3),
            "Exact Transition F1": round(exact_mean_f1, 3),
            "Partial Transition Precision": round(partial_mean_precision, 3),
            "Partial Transition Recall": round(partial_mean_recall, 3),
            "Partial Transition F1": round(partial_mean_f1, 3)
        }

        summary_rows.append(summary_row)

    return summary_rows

def main() -> None:
    # init the final summary rows
    summary_rows: list[dict[str, object]] = []

    # calculate all PSMBench saved FSM model results
    psmbench_summary_rows: list[dict[str, object]] = build_model_summary_rows(data_source="PSMBench Saved FSMs", state_file=NEW_STATE_FILE,
                                                                              exact_file=NEW_EXACT_FILE, partial_file=NEW_PARTIAL_FILE)

    summary_rows.extend(psmbench_summary_rows)

    # calculate all local Ollama model results
    local_summary_rows: list[dict[str, object]] = build_model_summary_rows(data_source="Local Ollama", state_file=STATE_OUTPUT_FILE,
                                                                           exact_file=EXACT_TRANSITION_OUTPUT_FILE, partial_file=PARTIAL_TRANSITION_OUTPUT_FILE)

    summary_rows.extend(local_summary_rows)

    # change all summary rows to DataFrame
    summary_df = pd.DataFrame(summary_rows)

    # create the output directory
    SUMMARY_OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    # save the final summary CSV
    summary_df.to_csv(SUMMARY_OUTPUT_FILE, index=False, encoding="utf-8-sig")

    # print the final summary table
    print(summary_df.to_string(index=False))

    print("PSMBench saved FSMs and local Ollama model summary completed.")
    print(f"Saved to: {SUMMARY_OUTPUT_FILE}")


if __name__ == "__main__":
    main()