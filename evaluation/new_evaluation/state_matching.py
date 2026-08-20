import sys

import numpy as np
from config.paths import PSMBENCH_DIR

if str(PSMBENCH_DIR) not in sys.path:
    sys.path.insert(0, str(PSMBENCH_DIR))
import eval_fsm_sim as psmbench_evaluator

from scipy.optimize import linear_sum_assignment
from sentence_transformers import util

# build a matrix to match predicted states and ground truth states
def _build_state_similarity_matrix(predicted_states: list[str], ground_truth_states: list[str]) -> np.ndarray:

    # init the normalize predicted list
    normalize_predicted_states: list[str] = []
    for state in predicted_states:
        normalize_predicted_states.append(psmbench_evaluator.preprocess_state_name(state_name=state))

    # init the normalize truth list
    normalize_ground_truth_states: list[str] = []
    for state in ground_truth_states:
        normalize_ground_truth_states.append(psmbench_evaluator.preprocess_state_name(state_name=state))

    # use the original PSMBench SentenceTransformer model ('all-MiniLM-L6-v2').
    predicted_embeddings: np.ndarray = psmbench_evaluator.model.encode(normalize_predicted_states, normalize_embeddings=True)
    ground_truth_embeddings: np.ndarray = psmbench_evaluator.model.encode(normalize_ground_truth_states, normalize_embeddings=True)

    # using cosine similarity calculation.(PSMBench used)
    similarity_matrix: np.ndarray = util.pytorch_cos_sim(predicted_embeddings, ground_truth_embeddings,).numpy()

    return similarity_matrix

    
    

# in original PSMbench evaluation, the old function will match the state many time,
# it will make the answer wrong
# using threshold (PSMBench also using threshold = 0.5, so default 0.5)
# model is using the model SentenceTransformer("all-MiniLM-L6-v2") like PSMbench
def match_state_one_to_one(predicted_states: list[str], ground_truth_states: list[str], threshold: float = 0.5) -> list[tuple[str, str, float]]:

    # if empty return empty list
    if not predicted_states or not ground_truth_states:
        return []

    # get the similarity matrix
    similarity_matrix: np.ndarray = _build_state_similarity_matrix(predicted_states=predicted_states, ground_truth_states=ground_truth_states)

    # mark the matrix which >= threshold
    mark_match_matrix: np.ndarray = similarity_matrix >= threshold

    # calcude the maximum possible number of mathces (one to one)
    # get the maximum match count for matching
    predicted_states_num: int = len(predicted_states)
    ground_truth_states_num: int = len(ground_truth_states)
    match_count: int = min(predicted_states_num, ground_truth_states_num)

    # set the bonus, because we should make the maches number first (it important than similiary)
    # the max of the pytorch_cos_sim is 1 so need to add a number bigger than 1
    match_bonus: float = float(match_count + 1)
    matching_scores: np.ndarray = np.where(mark_match_matrix, match_bonus + similarity_matrix, 0.0)


    predicted_indexes, ground_truth_indexes = linear_sum_assignment(matching_scores, maximize=True)

    # store the final valid matches.
    # [predict states, ground truth state, scores]
    state_matches: list[tuple[str, str, float]] = []

    for p_index, g_index in zip(predicted_indexes, ground_truth_indexes):
        # check the return index threshold >= 0.5
        if not mark_match_matrix[p_index, g_index]:
            continue

        # put the similarity in the list
        similarity: float = float(similarity_matrix[p_index, g_index])
        state_matches.append((predicted_states[p_index], ground_truth_states[g_index], similarity))

    return state_matches

    

