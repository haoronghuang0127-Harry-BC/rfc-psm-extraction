import sys
from pathlib import Path
from typing import Final, cast

from config.paths import PSMBENCH_DIR, PSMBENCH_FSM_DIR, PSMBENCH_NEW_EVALUATION_OUTPUT_DIR

from config.protocol.protocol_util import get_ground_truth_file

from evaluation.new_evaluation.evaluate_psm_service import build_failed_evaluation_result, evaluate_psm
from evaluation.new_evaluation.evaluation_csv_io import FINAL_FSM_SUFFIX, build_state_row, build_transition_row, save_csv, get_protocol_and_model
from evaluation.new_evaluation.evaluation_types import StateMachine

from evaluation.psm_reader import load_and_build_state_machine

# make sure Python finds the PSMBench directory
if str(PSMBENCH_DIR) not in sys.path:
    sys.path.insert(0, str(PSMBENCH_DIR))

import eval_fsm_sim as evaluator


# state evaluation CSV file.
STATE_OUTPUT_FILE: Final[Path] = PSMBENCH_NEW_EVALUATION_OUTPUT_DIR / "states_match_results.csv"
# exact transition evaluation CSV file.
EXACT_TRANSITION_OUTPUT_FILE: Final[Path] = PSMBENCH_NEW_EVALUATION_OUTPUT_DIR / "transitions_match_results_whole.csv"
# partial transition evaluation CSV file.
PARTIAL_TRANSITION_OUTPUT_FILE: Final[Path] = PSMBENCH_NEW_EVALUATION_OUTPUT_DIR / "transitions_match_results_partial.csv"



def run_evaluation() -> tuple[Path, Path, Path]:

    # load the psmbench fsm file
    final_fsm_files: list[Path] = sorted(PSMBENCH_FSM_DIR.glob(f"*{FINAL_FSM_SUFFIX}.json"))

    # using the original model name mapping
    model_name_mapping = evaluator.model_name_mapping.copy()
    # chang the filename mapping
    model_name_mapping["qwen3_32b"] = "QWen3"
    model_name_mapping["gemma3_27b"] = "Gemma3"

    # init each csv file rows
    state_rows: list[dict[str, object]] = []
    exact_transition_rows: list[dict[str, object]] = []
    partial_transition_rows: list[dict[str, object]] = []

    # get the total number of FSM files
    total_files: int = len(final_fsm_files)

    for index, predicted_fsm_file in enumerate(final_fsm_files, start=1):
        protocol, model_name = get_protocol_and_model(final_fsm_file=predicted_fsm_file)

        # change to cvs display name like PSMBench
        display_model_name: str = model_name_mapping.get(model_name, model_name)

        print(f"[{index}/{total_files}] Evaluating: {protocol} {display_model_name}")

        # load ground truth fsm
        ground_truth_file = get_ground_truth_file(protocol=protocol)
        ground_truth_fsm: StateMachine = load_and_build_state_machine(file_path=ground_truth_file)

        # load predict fsm
        try:
            predicted_fsm: StateMachine = load_and_build_state_machine(file_path=predicted_fsm_file)
        except ValueError as error:
            print(f"Invalid PSM: {predicted_fsm_file.name}")
            print(f"Reason:{error}")

            evaluation_result = build_failed_evaluation_result(ground_truth_fsm=ground_truth_fsm)
        else:
            evaluation_result = evaluate_psm(predicted_fsm=predicted_fsm, ground_truth_fsm=ground_truth_fsm, threshold=0.5)

        state_result: dict[str, object] = cast(dict[str, object], evaluation_result["states"])
        exact_transition_result: dict[str, object] = cast(dict[str, object], evaluation_result["exact_transitions"])
        partial_transition_result: dict[str, object] = cast(dict[str, object], evaluation_result["partial_transitions"])

        # add the row in csv rows
        state_rows.append(build_state_row(protocol=protocol, model_name=display_model_name, state_result=state_result))
        exact_transition_rows.append(build_transition_row(protocol=protocol, model_name=display_model_name, transition_result=exact_transition_result))
        partial_transition_rows.append(build_transition_row(protocol=protocol, model_name=display_model_name, transition_result=partial_transition_result))

    save_csv(rows=state_rows, output_file=STATE_OUTPUT_FILE)
    save_csv(rows=exact_transition_rows, output_file=EXACT_TRANSITION_OUTPUT_FILE)
    save_csv(rows=partial_transition_rows, output_file=PARTIAL_TRANSITION_OUTPUT_FILE)

    return (STATE_OUTPUT_FILE, EXACT_TRANSITION_OUTPUT_FILE, PARTIAL_TRANSITION_OUTPUT_FILE) 

def main() -> None:
    state_file, exact_file, partial_file = run_evaluation()

    print("All evaluations completed.")
    print(f"State results: {state_file}")
    print(f"Exact transition results: {exact_file}")
    print(f"Partial transition results: {partial_file}")


if __name__ == "__main__":
    main()