from pathlib import Path
from typing import Final

from config.paths import PSMBENCH_LOCAL_BASELINE_FINAL_FSMS_DIR, EVALUATION_OUTPUT_DIR

from config.protocol.protocol_util import get_ground_truth_file

from evaluation.new_evaluation.evaluate_psm_service import evaluate_psm, build_failed_evaluation_result
from evaluation.new_evaluation.evaluation_types import StateMachine
from evaluation.new_evaluation.evaluation_csv_io import build_state_row, build_transition_row, save_csv, get_protocol_and_model, FINAL_FSM_SUFFIX
from evaluation.psm_reader import load_and_build_state_machine

STATE_OUTPUT_FILE: Final[Path] = EVALUATION_OUTPUT_DIR / "states_match_results.csv"

EXACT_TRANSITION_OUTPUT_FILE: Final[Path] = EVALUATION_OUTPUT_DIR / "transitions_match_results_whole.csv"

PARTIAL_TRANSITION_OUTPUT_FILE: Final[Path] = EVALUATION_OUTPUT_DIR / "transitions_match_results_partial.csv"


def run_evaluation() -> tuple[Path, Path, Path]:
    # load the fsm file
    final_fsm_files: list[Path] = sorted(PSMBENCH_LOCAL_BASELINE_FINAL_FSMS_DIR.glob(f"*{FINAL_FSM_SUFFIX}.json"))

    # init each csv file rows
    state_rows: list[dict[str, object]] = []
    exact_transition_rows: list[dict[str, object]] = []
    partial_transition_rows: list[dict[str, object]] = []

    # get the number of the final fsm files
    total_files: int = len(final_fsm_files)
    for index, final_fsm_file in enumerate(final_fsm_files, start=1):
        protocol, model_name = get_protocol_and_model(final_fsm_file=final_fsm_file)

        print(f"[{index}/{total_files}] Evaluating: {protocol} {model_name}")

        # load ground truth fsm
        ground_truth_file = get_ground_truth_file(protocol=protocol)
        ground_truth_fsm: StateMachine = load_and_build_state_machine(file_path=ground_truth_file)

        # load predicted fsm
        try:   
            # if the fsm is null catch the error
            predicted_fsm: StateMachine = load_and_build_state_machine(file_path=final_fsm_file)
        except ValueError as error:
            print(f"Invalid PSM: {final_fsm_file.name}")
            print(f"Reason:{error}")

            evaluation_result = build_failed_evaluation_result(ground_truth_fsm=ground_truth_fsm)
        else:
            evaluation_result = evaluate_psm(predicted_fsm=predicted_fsm, ground_truth_fsm=ground_truth_fsm, threshold=0.5)

        state_result: dict[str, object] = evaluation_result.get("states")
        exact_transition_result: dict[str, object] = evaluation_result.get("exact_transitions")
        partial_transition_result: dict[str, object] = evaluation_result.get("partial_transitions")

        # add the row in csv rows
        state_rows.append(build_state_row(protocol=protocol, model_name=model_name, state_result=state_result))
        exact_transition_rows.append(build_transition_row(protocol=protocol, model_name=model_name, transition_result=exact_transition_result))
        partial_transition_rows.append(build_transition_row(protocol=protocol, model_name=model_name, transition_result=partial_transition_result))

    save_csv(rows=state_rows, output_file=STATE_OUTPUT_FILE)
    save_csv(rows=exact_transition_rows, output_file=EXACT_TRANSITION_OUTPUT_FILE)
    save_csv(rows=partial_transition_rows, output_file=PARTIAL_TRANSITION_OUTPUT_FILE)


    return (STATE_OUTPUT_FILE, EXACT_TRANSITION_OUTPUT_FILE, PARTIAL_TRANSITION_OUTPUT_FILE)

def main() -> None:
    evaluation_csv_file = run_evaluation()

    print("All evaluations completed.")
    print(f"Saved to: {evaluation_csv_file}")


if __name__ == "__main__":
    main()