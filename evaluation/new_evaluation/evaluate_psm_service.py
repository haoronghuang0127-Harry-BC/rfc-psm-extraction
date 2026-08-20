from evaluation.new_evaluation.evaluation_types import MetricResult, StateMachine, TransitionRecord
from evaluation.new_evaluation.state_matching import match_state_one_to_one
from evaluation.new_evaluation.transition_matching import match_transitions_one_to_one
from evaluation.new_evaluation.evaluation_csv_io import calculate_precision_recall_f1

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

def build_failed_evaluation_result(ground_truth_fsm: StateMachine) -> dict[str, object]:
    state_result = _build_failed_metric_result(ground_truth_count=len(ground_truth_fsm["states"]))
    

    transition_result = _build_failed_metric_result(ground_truth_count=len(ground_truth_fsm["transitions"]))
    

    evaluation_result: dict[str, object] = {
        "states": state_result,
        "exact_transitions": transition_result,
        "partial_transitions": transition_result,
    }

    return evaluation_result


def _build_metric_result(matches_count: int, llm_output_count: int, ground_truth_count: int) -> MetricResult:
    # get precision, recall and f1
    precision, recall, f1 = calculate_precision_recall_f1(TP=matches_count,TP_FP=llm_output_count,TP_FN=ground_truth_count)

    # calculate missing count and extra count
    miss_count: int = ground_truth_count - matches_count
    extra_count: int = llm_output_count - matches_count

    metric_result: MetricResult = {
        "llm_predicted_count": llm_output_count,
        "ground_truth_count": ground_truth_count,
        "matched_count": matches_count,
        "missing_count": miss_count,
        "extra_count": extra_count,
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }

    return metric_result

def evaluate_states(predicted_fsm: StateMachine, ground_truth_fsm: StateMachine, threshold: float = 0.5) -> dict[str, object]:

    # get predicted and ground truth states from fsm
    predicted_states = predicted_fsm["states"]
    ground_truth_states = ground_truth_fsm["states"]

    # get the states matches
    states_matches = match_state_one_to_one(predicted_states=predicted_states, ground_truth_states=ground_truth_states, threshold=threshold)

    # calculate the evaluation metrics
    state_matches_count:int = len(states_matches)
    llm_output_count:int = len(predicted_states)
    ground_truth_count:int = len(ground_truth_states)
    metric_result = _build_metric_result(matches_count=state_matches_count, llm_output_count=llm_output_count, ground_truth_count=ground_truth_count)

    # return the result and the match group
    match_details: list[dict[str, object]] = []
    for predicted_state, ground_truth_state, similarity in states_matches:
        match_details.append({
            "predicted_state": predicted_state,
            "ground_truth_state": ground_truth_state,
            "similarity": similarity
        })

    metric_result["matches"] = match_details

    return metric_result


def _evaluate_transitions(predicted_fsm: StateMachine, ground_truth_fsm: StateMachine, threshold: float, partial: bool) -> dict[str, object]:
    # get the transitions from predicted and ground_truth fsm
    predicted_transitions: list[TransitionRecord] = predicted_fsm["transitions"]
    ground_truth_transitions: list[TransitionRecord] = ground_truth_fsm["transitions"]

    # get transition matches
    transition_matches = match_transitions_one_to_one(predicted_transitions=predicted_transitions, ground_truth_transitions=ground_truth_transitions,
                                                      threshold=threshold, partial=partial)

    # get metric result
    matches_count: int = len(transition_matches)
    llm_output_count:int = len(predicted_transitions)
    ground_truth_count:int = len(ground_truth_transitions)
    metric_result = _build_metric_result(matches_count=matches_count, llm_output_count=llm_output_count, ground_truth_count=ground_truth_count)

    match_details: list[dict[str, object]] = []

    for predicted_transition, ground_truth_transition, similarity in transition_matches:
        match_details.append({
            "predicted_transition":predicted_transition,
            "ground_truth_transition":ground_truth_transition,
            "similarity": similarity
        })

    evaluation_result: dict[str, object] = dict(metric_result)
    evaluation_result["matches"] = match_details

    return evaluation_result

def evaluate_complete_transitions(predicted_fsm: StateMachine, ground_truth_fsm: StateMachine, threshold: float = 0.5) -> dict[str, object]:
    return _evaluate_transitions(predicted_fsm=predicted_fsm, ground_truth_fsm=ground_truth_fsm, threshold=threshold, partial=False)


def evaluate_partial_transitions(predicted_fsm: StateMachine, ground_truth_fsm: StateMachine, threshold: float = 0.5) -> dict[str, object]:
    return _evaluate_transitions(predicted_fsm=predicted_fsm, ground_truth_fsm=ground_truth_fsm, threshold=threshold, partial=True)





def evaluate_psm(predicted_fsm: StateMachine, ground_truth_fsm: StateMachine, threshold: float = 0.5) -> dict[str, object]:
    # evaluate state
    states_result = evaluate_states(predicted_fsm=predicted_fsm, ground_truth_fsm=ground_truth_fsm, threshold=threshold)

    # evaluate transition
    # complete
    complete_transitions_result = evaluate_complete_transitions(predicted_fsm=predicted_fsm, ground_truth_fsm=ground_truth_fsm, threshold=threshold)
    # partial
    partial_transitions_result = evaluate_partial_transitions(predicted_fsm=predicted_fsm, ground_truth_fsm=ground_truth_fsm, threshold=threshold)

    # build the complete evaluation result.
    evaluation_result: dict[str, object] = {
        "states": states_result,
        "exact_transitions": complete_transitions_result,
        "partial_transitions":partial_transitions_result
    }

    return evaluation_result