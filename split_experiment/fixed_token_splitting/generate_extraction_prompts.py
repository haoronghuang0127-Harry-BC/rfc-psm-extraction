from pathlib import Path

from config.paths import FIXED_TOKEN_SPLITTING_PROMPTS_DIR, FIXED_TOKEN_SPLITTING_SEGMENTS_DIR
from config.protocol.protocol_util import get_all_protocol_files, get_protocol_file

from research_pipeline.output_controls import get_output_control
from research_pipeline.prompt_builder import build_fsm_extraction_prompt
from research_pipeline.types import OutputControl

from rfc.rfc_io import load_rfc_segments
from rfc.rfc_service import get_rfc_segment_values
from rfc.rfc_types import RfcSegment

from split_experiment.command_line import read_command_line_to_value
from split_experiment.types import SplitExperimentArguments

from utils.files_util import save_json_file


# build extraction Prompts from the fixed token segments.
def _build_extraction_prompts(protocol_names: list[str], output_control: OutputControl) -> dict[str, list[str]]:
    extraction_prompts: dict[str, list[str]] = {}

    prompt_output_style: str = output_control["prompt_output_style"]

    for protocol in protocol_names:
        fixed_segments_file: Path = FIXED_TOKEN_SPLITTING_SEGMENTS_DIR / f"{protocol}_fixed_token_segments.json"
        fixed_token_segments: list[RfcSegment] = load_rfc_segments(file_path=fixed_segments_file)

        protocol_prompts: list[str] = []

        for segment in fixed_token_segments:
            _section_number, _section_name, section_title, section_text = get_rfc_segment_values(segment=segment)

            prompt: str = build_fsm_extraction_prompt(protocol_name=protocol, section_title=section_title, section_text=section_text, prompt_output_style=prompt_output_style)

            protocol_prompts.append(prompt)

        extraction_prompts[protocol] = protocol_prompts

        print(f"Built {len(protocol_prompts)} extraction Prompts for {protocol}.")

    return extraction_prompts


# save all fixed token extraction Prompts.
def _save_extraction_prompts(extraction_prompts: dict[str, list[str]]) -> Path:
    output_file: Path = FIXED_TOKEN_SPLITTING_PROMPTS_DIR / "ollama_json_schema_output_extraction_prompts.json"

    save_json_file(file_path=output_file, data=extraction_prompts)

    print(f"Saved extraction Prompts: {output_file}")

    return output_file


# generate extraction Prompts for the selected protocols.
def generate_extraction_prompts(protocol: str) -> dict[str, list[str]]:
    protocol_names: list[str] = []

    # get the selected protocol names.
    if protocol == "all":
        protocol_files: dict[str, Path] = get_all_protocol_files()
        protocol_names = list(protocol_files.keys())
    else:
        get_protocol_file(protocol=protocol)
        protocol_names = [protocol]

    output_control: OutputControl = get_output_control(output_control_name="ollama_json_schema_output")

    extraction_prompts: dict[str, list[str]] = _build_extraction_prompts(protocol_names=protocol_names, output_control=output_control)

    _save_extraction_prompts(extraction_prompts=extraction_prompts)

    return extraction_prompts


def main() -> None:
    arguments: SplitExperimentArguments = read_command_line_to_value()

    extraction_prompts: dict[str, list[str]] = generate_extraction_prompts(protocol=arguments["protocol"])

    print(f"Completed extraction Prompt generation. Saved {len(extraction_prompts)} protocol Prompts.")


if __name__ == "__main__":
    main()
