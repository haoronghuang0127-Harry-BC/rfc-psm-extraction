from pathlib import Path
from typing import cast

from config.paths import RECURSIVE_SECTION_SPLITTING_PARTIAL_FSMS_DIR, RECURSIVE_SECTION_SPLITTING_PROMPTS_DIR

from research_pipeline.output_controls import get_output_control
from research_pipeline.prompt_builder import build_fsm_combination_prompt
from research_pipeline.response_processing import parse_partial_fsms
from research_pipeline.types import OutputControl, ResearchStateMachine

from utils.files_util import load_json_file, save_json_file


# get the combination Prompt name from a partial FSM file.
def _get_combination_prompt_name(partial_fsms_file_path: Path) -> str:
    partial_fsms_suffix: str = "_partial_fsms"

    prompt_name: str = partial_fsms_file_path.stem.removesuffix(partial_fsms_suffix).rstrip("_")

    return prompt_name


# generate all recursive section combination Prompts.
def generate_combination_prompts() -> dict[str, str]:
    partial_fsms_files: list[Path] = sorted(RECURSIVE_SECTION_SPLITTING_PARTIAL_FSMS_DIR.glob("*_partial_fsms.json"))

    combination_prompts: dict[str, str] = {}
    output_control: OutputControl = get_output_control(output_control_name="ollama_json_schema_output")
    prompt_output_style: str = output_control["prompt_output_style"]

    for file_path in partial_fsms_files:
        partial_responses: list[str] = load_json_file(file_path=file_path, data_type=list[str])

        if not partial_responses:
            print(f"Skipped empty partial FSM file: {file_path}")
            continue

        partial_fsm_objects: list[dict[str, object]] = parse_partial_fsms(partial_responses=partial_responses, allow_direct_json=True)
        partial_fsms: list[ResearchStateMachine] = cast(list[ResearchStateMachine], partial_fsm_objects)

        if not partial_fsms:
            print(f"Skipped partial FSM file without valid FSM objects: {file_path}")
            continue

        combination_prompt: str = build_fsm_combination_prompt(partial_fsms=partial_fsms, prompt_output_style=prompt_output_style)
        prompt_name: str = _get_combination_prompt_name(partial_fsms_file_path=file_path)

        combination_prompts[prompt_name] = combination_prompt

        print(f"Built combination Prompt: {prompt_name}, partial FSM count: {len(partial_fsms)}")

    output_file: Path = RECURSIVE_SECTION_SPLITTING_PROMPTS_DIR / "combination_prompts.json"

    save_json_file(file_path=output_file, data=combination_prompts)

    print(f"Saved combination Prompts: {output_file}")

    return combination_prompts


def main() -> None:
    combination_prompts: dict[str, str] = generate_combination_prompts()

    print(f"Completed combination Prompt generation. Saved {len(combination_prompts)} Prompts.")


if __name__ == "__main__":
    main()
