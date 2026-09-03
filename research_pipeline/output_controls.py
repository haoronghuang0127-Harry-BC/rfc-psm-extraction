from research_pipeline.prompt_schema import FSM_JSON_SCHEMA
from research_pipeline.types import OutputControl



# Store all available output control methods.
OUTPUT_CONTROLS: dict[str, OutputControl] = {
    "tagged_json_output": {
        "request_format": None,
        "prompt_output_style": "tagged_json",
    },
    "ollama_json_output": {
        "request_format": "json",
        "prompt_output_style": "direct_json",
    },
    "ollama_json_schema_output": {
        "request_format": FSM_JSON_SCHEMA,
        "prompt_output_style": "direct_json",
    },
}


# Return all output control names.
def get_output_control_names() -> list[str]:
    output_control_names: list[str] = list(OUTPUT_CONTROLS.keys())

    return output_control_names


# Return one output control configuration.
def get_output_control(output_control_name: str) -> OutputControl:
    if output_control_name not in OUTPUT_CONTROLS:
        raise ValueError(f"Unknown output control: {output_control_name}")

    output_control: OutputControl = OUTPUT_CONTROLS[output_control_name]

    return output_control


# Return the selected output controls.
def get_selected_output_controls(output_control_name: str) -> dict[str, OutputControl]:
    if output_control_name == "all":
        output_controls: dict[str, OutputControl] = OUTPUT_CONTROLS.copy()

        return output_controls

    output_control: OutputControl = get_output_control(output_control_name=output_control_name)

    selected_output_controls: dict[str, OutputControl] = {
        output_control_name: output_control,
    }

    return selected_output_controls


# return the output control name from an experiment name.
# prompt_name name is the full name of the output file
# e.g TCP_qwen3.5_9b_qwen_no_think_tagged_json_output
# it will return the control name like -> tagged_json_output
def get_output_control_name_from_experiment_name(prompt_name: str) -> str:
    # get all the output format name
    output_control_names: list[str] = get_output_control_names()

    for output_control_name in output_control_names:
        required_suffix: str = f"_{output_control_name}"

        if prompt_name.endswith(required_suffix):
            return output_control_name

    raise ValueError(f"Could not find the output control name from: {prompt_name}")