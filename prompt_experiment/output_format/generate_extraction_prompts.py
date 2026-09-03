from pathlib import Path

from config.paths import PROMPT_EXPERIMENT_PROMPTS_DIR
from config.protocol.protocol_util import get_all_protocol_files, get_protocol_file

from prompt_experiment.output_format.command_line import read_command_line_to_value
from prompt_experiment.types import PromptExperimentArguments

from research_pipeline.output_controls import get_selected_output_controls
from research_pipeline.prompt_builder import build_fsm_extraction_prompt
from research_pipeline.types import OutputControl

from rfc.rfc_io import load_rfc_segments
from rfc.rfc_service import get_rfc_segment_values
from rfc.rfc_types import RfcSegment

from utils.files_util import save_json_file


def _build_extraction_prompts(protocol_files: dict[str, Path], output_control: OutputControl) -> dict[str, list[str]]:
    extraction_prompts: dict[str, list[str]] = {}

    prompt_output_style: str = output_control["prompt_output_style"]

    for protocol, protocol_file in protocol_files.items():
        rfc_segments: list[RfcSegment] = load_rfc_segments(file_path=protocol_file)

        protocol_prompts: list[str] = []

        for segment in rfc_segments:
            section_number, section_name, section_title, section_text = get_rfc_segment_values(segment=segment)

            prompt: str = build_fsm_extraction_prompt(protocol_name=protocol, section_title=section_title,
                                                      section_text=section_text, prompt_output_style=prompt_output_style)

            protocol_prompts.append(prompt)

        extraction_prompts[protocol] = protocol_prompts

        print(f"Built {len(protocol_prompts)} extraction Prompts for {protocol}.")


    return extraction_prompts


# save extraction Prompts for one output control method.
def _save_extraction_prompts(output_control_name: str, extraction_prompts: dict[str, list[str]]) -> Path:
    output_file: Path = PROMPT_EXPERIMENT_PROMPTS_DIR / f"{output_control_name}_extraction_prompts.json"

    save_json_file(file_path=output_file, data=extraction_prompts)

    print(f"Saved extraction Prompts: {output_file}")

    return output_file

def generate_extraction_prompts(protocol: str, output_control_name: str) -> dict[str, dict[str, list[str]]]:
    protocol_files: dict[str, Path] = {}

    # get the protocol
    if protocol == "all":
        protocol_files = get_all_protocol_files()
    else:
        protocol_files = {
            protocol: get_protocol_file(protocol=protocol)
        }

    
    output_controls: dict[str, OutputControl] = get_selected_output_controls(output_control_name=output_control_name)

    all_extraction_prompts: dict[str, dict[str, list[str]]] = {}


    for selected_output_control_name, output_control in output_controls.items():
        print(f"Building extraction Prompts for output control: {selected_output_control_name}")

        extraction_prompts: dict[str, list[str]] = _build_extraction_prompts(protocol_files=protocol_files, output_control=output_control)

        _save_extraction_prompts(output_control_name=selected_output_control_name, extraction_prompts=extraction_prompts)

        all_extraction_prompts[selected_output_control_name] = extraction_prompts

    return all_extraction_prompts



def main() -> None:
    arguments: PromptExperimentArguments = read_command_line_to_value()

    generate_extraction_prompts(protocol=arguments["protocol"], output_control_name=arguments["output_control"])


if __name__ == "__main__":
    main()