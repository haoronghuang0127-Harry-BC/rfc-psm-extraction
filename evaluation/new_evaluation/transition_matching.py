import sys

import numpy as np
from config.paths import PSMBENCH_DIR

from evaluation.new_evaluation.evaluation_types import TransitionRecord

if str(PSMBENCH_DIR) not in sys.path:
    sys.path.insert(0, str(PSMBENCH_DIR))
import eval_fsm_sim as psmbench_evaluator

from scipy.optimize import linear_sum_assignment
from sentence_transformers import util

def _build_similarity_matrix(predicted: list[str], ground_truth: list[str]) -> np.ndarray:
    predicted_embeddings = psmbench_evaluator.model.encode(predicted, normalize_embeddings=True)

    ground_truth_embeddings  = psmbench_evaluator.model.encode(ground_truth, normalize_embeddings=True)

    similarity_matrix: np.ndarray = util.pytorch_cos_sim(predicted_embeddings, ground_truth_embeddings).numpy()

    return similarity_matrix

def _build_transition_match_matrices(predicted_transitions: list[TransitionRecord], ground_truth_transitions: list[TransitionRecord],
                                     threshold: float, partial: bool) -> tuple[np.ndarray, np.ndarray]:

    def get_value_from_transitions(transitions: list[TransitionRecord], key: str) -> list[str]:
        # init the result list
        result: list[str] = []

        for transition in transitions:
            result.append(transition[key])

        return result

    # get the from name from the transitions
    # calculate from similarities
    predicted_from: list[str] = get_value_from_transitions(transitions=predicted_transitions, key="from")
    ground_truth_from: list[str] = get_value_from_transitions(transitions=ground_truth_transitions, key="from")
    from_similarity_matrix = _build_similarity_matrix(predicted=predicted_from, ground_truth=ground_truth_from)

    # get the to name from the transitions
    # calculate to similarities
    predicted_to: list[str] = get_value_from_transitions(transitions=predicted_transitions, key="to")
    ground_truth_to: list[str] = get_value_from_transitions(transitions=ground_truth_transitions, key="to")
    to_similarity_matrix = _build_similarity_matrix(predicted=predicted_to, ground_truth=ground_truth_to)

    # calculate if choose partial
    if partial:
        # partial transition matching

        # get event similarity_matrix
        predicted_events: list[str] = get_value_from_transitions(transitions=predicted_transitions, key="event")
        ground_truth_events: list[str] = get_value_from_transitions(transitions=ground_truth_transitions, key="event")
        event_similarity_matrix = _build_similarity_matrix(predicted=predicted_events, ground_truth=ground_truth_events)

        # get action similarity_matrix
        predicted_actions: list[str] = get_value_from_transitions(transitions=predicted_transitions, key="action")
        ground_truth_actions: list[str] = get_value_from_transitions(transitions=ground_truth_transitions, key="action")
        action_similarity_matrix = _build_similarity_matrix(predicted=predicted_actions, ground_truth=ground_truth_actions)

        # In PSMBench partial matching uses the larger one between "event" and "action"
        event_and_action_similarity_matrix = np.maximum(event_similarity_matrix, action_similarity_matrix)
    else:
        # complete transition matching

        # the function help to get complete transitions match for event + action
        def get_value_from_transitions_complete(transitions: list[TransitionRecord]) -> list[str]:
                # init the result list
                result: list[str] = []
        
                for transition in transitions:
                    event_and_action = transition["event"] + transition["action"]
                    result.append(event_and_action)
        
                return result

        # get event + action similarity_matrix
        predicted_event_and_action: list[str] = get_value_from_transitions_complete(transitions=predicted_transitions)
        ground_truth_event_and_action: list[str] = get_value_from_transitions_complete(transitions=ground_truth_transitions)
        event_and_action_similarity_matrix = _build_similarity_matrix(predicted=predicted_event_and_action, ground_truth=ground_truth_event_and_action)


    # from, to, and (event and action) all reach threshold
    valid_match_matrix: np.ndarray = ((from_similarity_matrix >= threshold) 
                                      & (to_similarity_matrix >= threshold)
                                      & (event_and_action_similarity_matrix >= threshold))

    # when the predicted transitions have the same match of the ground truth choose the higher one
    average_similarity_matrix: np.ndarray = (from_similarity_matrix + to_similarity_matrix + event_and_action_similarity_matrix) / 3.0

    return (valid_match_matrix, average_similarity_matrix)

def match_transitions_one_to_one(predicted_transitions: list[TransitionRecord], ground_truth_transitions: list[TransitionRecord], 
                                 threshold: float = 0.5, partial: bool = False) -> list[tuple[TransitionRecord, TransitionRecord, float]]:

    # can not empty
    if not predicted_transitions or not ground_truth_transitions:
        return []

    valid_match_matrix, average_similarity_matrix = _build_transition_match_matrices(predicted_transitions=predicted_transitions, ground_truth_transitions=ground_truth_transitions,
                                                                                     threshold=threshold, partial=partial)

    # choose the maximum of matching
    predicted_tranistion_num: int = len(predicted_transitions)
    ground_truth_transition_num: int = len(ground_truth_transitions)
    match_count: int = min(predicted_tranistion_num, ground_truth_transition_num)

    # set the bonus, because we should make the maches number first (it important than similiary)
    # the max of the pytorch_cos_sim is 1 so need to add a number bigger than 1
    match_bonus: float = float(match_count + 1)
    matching_scores: np.ndarray = np.where(valid_match_matrix, match_bonus + average_similarity_matrix, 0.0)

    predicted_indexes, ground_truth_indexes = linear_sum_assignment(matching_scores, maximize=True)

    # store the final valid matches.
    # [predict transition, ground truth transition, scores]
    transition_matches: list[tuple[TransitionRecord, TransitionRecord, float]] = []

    for p_index, g_index in zip(predicted_indexes, ground_truth_indexes):
        # check the return index threshold >= 0.5
        if not valid_match_matrix[p_index, g_index]:
            continue

        # put the similarity in the list
        similarity: float = float(average_similarity_matrix[p_index, g_index])
        transition_matches.append((predicted_transitions[p_index], ground_truth_transitions[g_index], similarity))

    return transition_matches
