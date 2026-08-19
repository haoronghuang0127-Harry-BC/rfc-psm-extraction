import sys

from pathlib import Path

from config.paths import PSMBENCH_DIR, PSMBENCH_LOCAL_BASELINE_COMBINATION_PROMPTS, PSMBENCH_LOCAL_BASELINE_PARTIAL_FSMS_DIR

# Add the original PSMBench directory to Python path.
if str(PSMBENCH_DIR) not in sys.path:
    sys.path.insert(0, str(PSMBENCH_DIR))
from prompt_generation import build_fsm_combination_prompt

from utils.files_util import load_json_file, save_json_file

# get the combination prompt name from the file name.
def _get_combination_prompt_name(partial_fsms_file_path: Path) -> str:
    partial_fsms_suffix: str = "_partial_fsms"

    prompt_name: str = partial_fsms_file_path.stem.removesuffix(partial_fsms_suffix)

    return prompt_name

def get_combination_prompts_dict() -> dict[str, str]:
    # load thr partial fsm files
    partial_fsms_files: list[Path] = sorted(PSMBENCH_LOCAL_BASELINE_PARTIAL_FSMS_DIR.glob("*_partial_fsms.json"))

    # init the combination prompts dict
    combination_prompts_dict: dict[str, str] = {}

    for file_path in partial_fsms_files:
        partial_fsms: list[str] = load_json_file(file_path=file_path, data_type=list[str])

        # if partial fsms is empty skip it
        if not partial_fsms:
            print(f"Skipped empty partial FSM file: {file_path}")
            continue

        # get the combine prompt 
        combination_prompt: str = build_fsm_combination_prompt(partial_fsms=partial_fsms)

        # get the prompt name
        prompt_name: str =  _get_combination_prompt_name(partial_fsms_file_path=file_path)

        # save in the dict
        combination_prompts_dict[prompt_name] = combination_prompt

        print(f"Built combination prompt: {prompt_name}, partial FSM count: {len(partial_fsms)}")

    save_json_file(file_path=PSMBENCH_LOCAL_BASELINE_COMBINATION_PROMPTS, data=combination_prompts_dict)

    print(f"Saved combination prompts: {PSMBENCH_LOCAL_BASELINE_COMBINATION_PROMPTS}")

    return combination_prompts_dict


def main() -> None:
    get_combination_prompts_dict()


if __name__ == "__main__":
    main()