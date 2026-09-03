from pathlib import Path
from typing import cast

from config.paths import PROMPT_EXPERIMENT_PARTIAL_FSMS_DIR, PROMPT_EXPERIMENT_PROMPTS_DIR

from research_pipeline.output_controls import get_output_control, get_output_control_name_from_experiment_name
from research_pipeline.prompt_builder import build_fsm_combination_prompt
from research_pipeline.response_processing import parse_partial_fsms
from research_pipeline.types import OutputControl, ResearchStateMachine

from utils.files_util import load_json_file, save_json_file


def _get_combination_prompt_name(partial_fsms_file_path: Path) -> str:
    partial_fsms_suffix: str = "_partial_fsms"

    # remove the .json and remove ""_partial_fsms""
    prompt_name: str = partial_fsms_file_path.stem.removesuffix(partial_fsms_suffix).rstrip("_")

    return prompt_name

# generate all combination prompts.
def generate_combination_prompts() -> dict[str, str]:
    partial_fsms_files: list[Path] = sorted(PROMPT_EXPERIMENT_PARTIAL_FSMS_DIR.glob("*_partial_fsms.json"))

    combination_prompts: dict[str, str] = {}

    for file_path in partial_fsms_files:
        # load the partial response strings.
        partial_responses: list[str] = load_json_file(file_path=file_path, data_type=list[str])

        if not partial_responses:
            print(f"Skipped empty partial FSM file: {file_path}")
            continue

        # get the prompt name and output control.
        prompt_name: str = _get_combination_prompt_name(partial_fsms_file_path=file_path)
        output_control_name: str = get_output_control_name_from_experiment_name(prompt_name=prompt_name)
        # get the output format to choose the prompt output style
        output_control: OutputControl = get_output_control(output_control_name=output_control_name)
        prompt_output_style: str = output_control["prompt_output_style"]

        allow_direct_json: bool = prompt_output_style == "direct_json"

        partial_fsm_objects: list[dict[str, object]] = parse_partial_fsms(partial_responses=partial_responses, allow_direct_json=allow_direct_json)

        partial_fsms: list[ResearchStateMachine] = cast(list[ResearchStateMachine], partial_fsm_objects)

        if not partial_fsms:
            print(f"Skipped partial FSM file without valid FSM objects: {file_path}")
            continue

        # build the combination prompt.
        combination_prompt: str = build_fsm_combination_prompt(partial_fsms=partial_fsms, prompt_output_style=prompt_output_style)

        combination_prompts[prompt_name] = combination_prompt

        print(f"Built combination prompt: {prompt_name}, partial FSM count: {len(partial_fsms)}")


    # save the combination prompts
    output_file: Path = PROMPT_EXPERIMENT_PROMPTS_DIR / "combination_prompts.json"

    save_json_file(file_path=output_file, data=combination_prompts)

    print(f"Saved combination prompts: {output_file}")

    return combination_prompts


def main() -> None:
    combination_prompts: dict[str, str] = generate_combination_prompts()

    print(f"Completed combination prompt generation. Saved {len(combination_prompts)} prompts.")


if __name__ == "__main__":
    main()