from PSMBench.prompt_generation import build_fsm_extraction_prompt

from config.output_formats import OutputFormatName

from method_1_section_selection.prompt.generate_f1_and_f2_prompt_template import build_f1_and_f2_section_prompt_from_template
from method_1_section_selection.prompt.prompt_types import PromptRecord



def _build_section_prompt_f0(protocol: str, section_title: str, section_text: str) -> str:
    return build_fsm_extraction_prompt(protocol_name=protocol, section_title=section_title, section_text=section_text)

def _build_section_prompt_f1_and_f2(protocol: str, section_title: str, section_text: str) -> str:
    return build_f1_and_f2_section_prompt_from_template(protocol=protocol, section_title=section_title, section_text=section_text)


def build_section_prompt(prompt_record: PromptRecord, output_format_name: OutputFormatName) -> str:
    protocol: str = prompt_record["protocol"]
    section_title: str = prompt_record["tag"]
    section_text: str = prompt_record["section_text"]

    if output_format_name == OutputFormatName.F0:
        return _build_section_prompt_f0(protocol=protocol, section_title=section_title,section_text=section_text)

    if output_format_name == OutputFormatName.F1 or output_format_name == OutputFormatName.F2:
        return _build_section_prompt_f1_and_f2(protocol=protocol, section_title=section_title,section_text=section_text)