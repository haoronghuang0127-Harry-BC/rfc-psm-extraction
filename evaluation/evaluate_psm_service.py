import sys

from config.paths import PSMBENCH_DIR


if str(PSMBENCH_DIR) not in sys.path:
    sys.path.insert(0, str(PSMBENCH_DIR))
from eval_fsm_sim import compute_match_metrics, match_states, match_transitions_combined_event_action

from evaluation.evaluation_types import EvaluationResult, MetricResult, StateMachine, TransitionRecord

# Build an empty metric result for a failed PSM.
def _build_failed_metric_result(ground_truth_count: int) -> MetricResult:

    metric_result: MetricResult = {
        "llm_predicted_count": 0,
        "ground_truth_count": ground_truth_count,
        "matched_count": 0,
        "missing_count": ground_truth_count,
        "extra_count": 0,
        "precision": 0.0,
        "recall": 0.0,
        "f1": 0.0,
    }

    return metric_result

# Build an evaluation result for an invalid PSM.
def build_failed_evaluation_result(error_message: str, ground_truth_psm: StateMachine) -> EvaluationResult:

    # Invalid JSON means that the file could not be parsed.
    parsed: bool = "invalid JSON" not in error_message

    # get states and transitions count
    states_count: int = len(ground_truth_psm["states"])
    transitions_count: int = len(ground_truth_psm["transitions"])

    evaluation_result: EvaluationResult = {
        "parsed": parsed,
        "structure_valid": False,
        "structure_errors": [
            error_message,
        ],
        "states": _build_failed_metric_result(ground_truth_count=states_count),
        "exact_transitions": _build_failed_metric_result(ground_truth_count=transitions_count),
        "partial_transitions": _build_failed_metric_result(ground_truth_count=transitions_count)
    }

    return evaluation_result

"""
states part
"""
def _build_metric_result(state_matches_count: int, llm_output_count: int, ground_truth_count: int) -> MetricResult:
    # init precision, recall and f1
    precision: float = 0.0
    recall: float = 0.0
    f1: float = 0.0

    # calculate precision
    # Precision = TP / (TP + FP)
    if llm_output_count > 0:
        precision = state_matches_count / llm_output_count

    # calculate recall
    # Recall = TP / (TP + FN)
    if ground_truth_count > 0:
        recall = state_matches_count / ground_truth_count

    # calculate f1
    # F1 = 2TP / (2TP + FP + FN)
    total: float = precision + recall
    if total > 0:
        f1 = (2.0 * precision * recall) / total

    # calculate missing count and extra count
    miss_count: int = ground_truth_count - state_matches_count
    extra_count: int = llm_output_count - state_matches_count

    metric_result: MetricResult = {
        "llm_predicted_count": llm_output_count,
        "ground_truth_count": ground_truth_count,
        "matched_count": state_matches_count,
        "missing_count": miss_count,
        "extra_count": extra_count,
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }

    return metric_result
    

def evaluate_states(llm_output_psm: StateMachine, ground_truth_psm: StateMachine, threshold: float) -> MetricResult:
    # get the states from llm output psm and ground truth psm
    llm_output_states: list[str] = llm_output_psm["states"]
    ground_truth_states: list[str] = ground_truth_psm["states"]

    # get the count of states
    llm_states_count: int = len(llm_output_states)
    ground_truth_states_count: int = len(ground_truth_states)

    # PSMBench match_states function need not empty in source and target states
    if llm_states_count == 0 or ground_truth_states_count == 0:
        return _build_metric_result(state_matches_count=0, llm_output_count=llm_states_count, ground_truth_count=ground_truth_states_count)


    state_matches, _unmatched_states = match_states(source_states=ground_truth_states, target_states=llm_output_states, threshold=threshold)

    # calculate the state matches count
    state_matches_count: int = 0
    for src, best_match, score  in state_matches:
        if best_match is not None:
            state_matches_count += 1

    metric_result: MetricResult = _build_metric_result(state_matches_count=state_matches_count, llm_output_count=llm_states_count, ground_truth_count=ground_truth_states_count)

    return metric_result

"""
transitions part
"""
def _evaluate_transitions(llm_output_psm: StateMachine, ground_truth_psm: StateMachine, threshold: float, partial: bool) -> MetricResult:
    # get the transitions from llm output psm and ground truth psm
    llm_output_transitions: list[TransitionRecord] = llm_output_psm["transitions"]
    ground_truth_transitions: list[TransitionRecord] = ground_truth_psm["transitions"]
    

    # using the PSMBench matching function
    # get the match related value
    matched_transitions, _unmatched_transitions, matched_count = match_transitions_combined_event_action(trans1=llm_output_transitions, trans2=ground_truth_transitions, 
                                                                                                         threshold=threshold, if_partial=partial)

    # Use the PSMBench metric function to get the precision, recall, f1
    precision, recall, f1 = compute_match_metrics(matched=matched_transitions, gt_trans=ground_truth_transitions, ex_trans=llm_output_transitions)

    # get the count of the transitions
    llm_transitions_count: int = len(llm_output_transitions)
    ground_truth_transitions_count: int = len(ground_truth_transitions)
    # calculate the missing count and extracted transitions count
    missing_count: int = ground_truth_transitions_count - matched_count
    extra_count: int = llm_transitions_count - matched_count

    metric_result: MetricResult = {
        "llm_predicted_count": llm_transitions_count,
        "ground_truth_count": ground_truth_transitions_count,
        "matched_count": matched_count,
        "missing_count": missing_count,
        "extra_count": extra_count,
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }

    return metric_result

# evaluate complete transitions
def evaluate_complete_transitions(llm_output_psm: StateMachine, ground_truth_psm: StateMachine, threshold: float) -> MetricResult:
    return _evaluate_transitions(llm_output_psm=llm_output_psm, ground_truth_psm=ground_truth_psm, threshold=threshold, partial=False)

# evaluate partial transitions
def evaluate_partial_transitions(llm_output_psm: StateMachine, ground_truth_psm: StateMachine, threshold: float) -> MetricResult:
    return _evaluate_transitions(llm_output_psm=llm_output_psm, ground_truth_psm=ground_truth_psm, threshold=threshold, partial=True)







