from pathlib import Path
from typing import Final

from config.protocol.protocol_util import get_ground_truth_file

from evaluation.evaluate_psm_service import build_failed_evaluation_result, evaluate_complete_transitions, evaluate_partial_transitions, evaluate_states
from evaluation.evaluation_io import get_evaluation_result_file, get_llm_output_fsm_files, save_evaluation_result
from evaluation.evaluation_summary import create_evaluation_summary
from evaluation.evaluation_types import EvaluationResult, MetricResult, StateMachine
from evaluation.psm_reader import load_and_build_state_machine

# The similarity threshold used by PSMBench.
DEFAULT_SIMILARITY_THRESHOLD: Final[float] = 0.5

def _evaluate_psm(llm_output_psm: StateMachine, ground_truth_psm: StateMachine, threshold: float = DEFAULT_SIMILARITY_THRESHOLD) -> EvaluationResult:
    # evaluate states
    states_result: MetricResult = evaluate_states(llm_output_psm=llm_output_psm, ground_truth_psm=ground_truth_psm, threshold=threshold)

    # evaluate complete transitions
    complete_transitions_result: MetricResult = evaluate_complete_transitions(llm_output_psm=llm_output_psm, ground_truth_psm=ground_truth_psm, threshold=threshold)

    # evaluate partial transitions
    partial_transitions_result: MetricResult = evaluate_partial_transitions(llm_output_psm=llm_output_psm, ground_truth_psm=ground_truth_psm, threshold=threshold)

    # combine the result
    evaluation_result: EvaluationResult = {
        "parsed": True,
        "structure_valid": True,
        "structure_errors": [],
        "states": states_result,
        "exact_transitions": complete_transitions_result,
        "partial_transitions": partial_transitions_result,
    }

    return evaluation_result

def _get_protocol_name_from_path(fsm_file: Path, output_dir: Path) -> str:
    # get the relative path in the project
    # because my output files is "../outputs/‘protocol_name’/.........."
    relative_file_path: Path = fsm_file.relative_to(output_dir)

    # get the protocol name (in the path the first item is protocol name)
    protocol_name: str = relative_file_path.parts[0].upper()

    return protocol_name 

def _evaluate_fsm_file(fsm_file: Path, output_dir: Path) -> Path:
    # get the protocol name
    protocol_name: str = _get_protocol_name_from_path(fsm_file=fsm_file, output_dir=output_dir)

    # get the path of ground truth files
    ground_truth_file_path: Path = get_ground_truth_file(protocol=protocol_name)
    # get ground truth psm
    ground_truth_psm: StateMachine = load_and_build_state_machine(file_path=ground_truth_file_path)

    try:
        # get llm output psm
        llm_output_psm: StateMachine = load_and_build_state_machine(file_path=fsm_file)
    except ValueError as error:
        evaluation_result = build_failed_evaluation_result(error_message=str(error), ground_truth_psm=ground_truth_psm)
    else:
        evaluation_result: EvaluationResult = _evaluate_psm(llm_output_psm=llm_output_psm, ground_truth_psm=ground_truth_psm)

    # get the evaluation result file path.
    evaluation_result_file: Path = get_evaluation_result_file(final_fsm_file=fsm_file)

    # save the evaluation result
    save_evaluation_result(file_path=evaluation_result_file, evaluation_result=evaluation_result)

    return evaluation_result_file

# Evaluate all final PSM files in one output directory.
def run_all_evaluations(output_dir: Path) -> None:

    # get the final psm files in dir
    fsm_files: list[Path] = get_llm_output_fsm_files(output_dir=output_dir)

    # get len of the final psm files
    fsm_files_count: int = len(fsm_files)
    # evaluate each final psm files
    for index, fsm_file in enumerate(fsm_files, start=1):
        print(f"[{index}/{fsm_files_count}]  evaluating: {fsm_file}")

        evaluation_result_file: Path = _evaluate_fsm_file(fsm_file=fsm_file, output_dir=output_dir)

        print(f"Result saved: {evaluation_result_file}")


def run_summarized_results(output_dir: Path) -> None:
    summary_file: Path = create_evaluation_summary(output_dir=output_dir) 

    print(f"Evaluation summary saved: {summary_file}")
