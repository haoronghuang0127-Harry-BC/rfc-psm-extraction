from PSMBench.prompt_generation import build_fsm_combination_prompt

from config.output_formats import OutputFormatName

from method_1_section_selection.prompt.generate_f1_and_f2_prompt_template import build_f1_and_f2_merge_prompt_from_template


def _build_f0_merge_prompt(partial_outputs: list[str]) -> str:
    return build_fsm_combination_prompt(partial_fsms=partial_outputs)

def _build_f1_and_f2_merge_prompt(partial_outputs: list[str]) -> str:
    partial_texts: list[str] = []

    for partial_output in partial_outputs:
        partial_text: str = "<partial>\n" + f"{partial_output}\n" + "</partial>"
        partial_texts.append(partial_text)

    total_partial_texts: str = "\n\n".join(partial_texts)


    prompt: str = build_f1_and_f2_merge_prompt_from_template(partial_texts=total_partial_texts)

    return prompt


def build_merge_prompt(partial_outputs: list[str], output_format_name: OutputFormatName) -> str:
    if output_format_name == OutputFormatName.F0:
        return _build_f0_merge_prompt(partial_outputs)

    if output_format_name == OutputFormatName.F1 or output_format_name == OutputFormatName.F2:
        return _build_f1_and_f2_merge_prompt(partial_outputs)