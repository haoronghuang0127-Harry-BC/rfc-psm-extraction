
from prompt_experiment.output_format.prompt_schema import FSM_JSON_SCHEMA
from prompt_experiment.types import OutputControl


# Store all available output control methods.
# 保存全部可用的输出控制方式。
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
# 返回全部输出控制方式的名称。
def get_output_control_names() -> list[str]:
    output_control_names: list[str] = list(OUTPUT_CONTROLS.keys())

    return output_control_names


# Return one output control configuration.
# 返回一种输出控制配置。
def get_output_control(output_control_name: str) -> OutputControl:
    if output_control_name not in OUTPUT_CONTROLS:
        raise ValueError(f"Unknown output control: {output_control_name}")

    output_control: OutputControl = OUTPUT_CONTROLS[output_control_name]

    return output_control


# Return the selected output controls.
# 返回用户选择的输出控制配置。
def get_selected_output_controls(output_control_name: str) -> dict[str, OutputControl]:
    if output_control_name == "all":
        output_controls: dict[str, OutputControl] = OUTPUT_CONTROLS.copy()

        return output_controls

    output_control: OutputControl = get_output_control(output_control_name=output_control_name)

    selected_output_controls: dict[str, OutputControl] = {
        output_control_name: output_control,
    }

    return selected_output_controls