import os
import sys
from pathlib import Path
from typing import Final

from config.paths import PSMBENCH_DIR, PSMBENCH_OUTPUT_DIR

# make sure Python find the PSMBENCH_DIR
sys.path.insert(0, str(PSMBENCH_DIR))

os.chdir(PSMBENCH_DIR)

import eval_fsm_sim as evaluator

# set the output file Path
STATE_OUTPUT_FILE: Final[Path] = PSMBENCH_OUTPUT_DIR / "states_match_results.csv"
WHOLE_OUTPUT_FILE: Final[Path] = PSMBENCH_OUTPUT_DIR / "transitions_match_results_whole.csv"
PARTIAL_OUTPUT_FILE: Final[Path] =  PSMBENCH_OUTPUT_DIR / "transitions_match_results_partial.csv"

def main() -> None:
    #batch_evaluate_fsm_similarity()
    protocols = ["IMAP", "POP3", "MQTT","PPP","PPTP", "BGP",
                    "SIP", "RTSP", "DCCP", "DHCP", "FTP", "NNTP", "SMTP", "TCP"]
    # In Windows system, the fsm filename uses underscores
    # So change "qwen3:32b","gemma3:27b" -> "qwen3_32b", "gemma3_27b"
    models = ["deepseek-reasoner", "gpt-4o-mini", "claude-3-7-sonnet-20250219", 
                "gemini-2.0-flash", "deepseek-chat",
                "qwq", "qwen3_32b", "gemma3_27b" ,"mistral-small3.1"]

    # using the original model name mapping
    model_name_mapping = evaluator.model_name_mapping.copy()

    # chang the filename mapping
    model_name_mapping["qwen3_32b"] = "QWen3"
    model_name_mapping["gemma3_27b"] = "Gemma3"

    # create the output dir
    PSMBENCH_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 1. state evaluation
    all_matches, summary_df = evaluator.match_all_states(models, protocols, fsm_dir="fsm", threshold=0.5)
    summary_df["Model"] = summary_df["Model"].replace(model_name_mapping)
    print("All Matches:\n", all_matches)
    print("summary_df:\n", summary_df)
    summary_df.to_csv(STATE_OUTPUT_FILE, index=False)
    print("State evaluation completed.")
    print(f"Saved to: {STATE_OUTPUT_FILE}")

    # 2. whole transition evaluation
    whole_transition_matches_df = evaluator.batch_evaluate_transitions_combined(protocols=protocols, models=models, fsm_dir="fsm", if_partial=False)
    whole_transition_matches_df["Model"] = whole_transition_matches_df["Model"].replace(model_name_mapping)
    print("whole_transition_matches_df:\n", whole_transition_matches_df)
    whole_transition_matches_df.to_csv(WHOLE_OUTPUT_FILE, index=False)
    print("Whole transition evaluation completed.")
    print(f"Saved to: {WHOLE_OUTPUT_FILE}")

    # 3. partial transition evaluation
    partial_transition_df = evaluator.batch_evaluate_transitions_combined(protocols=protocols, models=models, fsm_dir="fsm", if_partial=True)
    partial_transition_df["Model"] = partial_transition_df["Model"].replace(model_name_mapping)
    print("partial_transition_df:\n", partial_transition_df)
    partial_transition_df.to_csv(PARTIAL_OUTPUT_FILE, index=False)
    print("Partial transition evaluation completed.")
    print(f"Saved to: {PARTIAL_OUTPUT_FILE}")

    print("\nAll evaluations completed.")


if __name__ == "__main__":
    main()