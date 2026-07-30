from enum import StrEnum
from typing import TypedDict


# Output formats used in the experiments.
class OutputFormatName(StrEnum):
    F0 = "F0"
    F1 = "F1"
    F2 = "F2"


# Store one output format configuration.
class OutputFormat(TypedDict):
    name: OutputFormatName
    description: str
    section_request_format: str | dict[str, object] | None
    merge_request_format: str | dict[str, object] | None


# JSON Schema used when one RFC section is processed.
SECTION_PSM_SCHEMA: dict[str, object] = {
    "type": "object",
    "properties": {
        "has_psm": {
            "type": "boolean",
        },
        "states": {
            "type": "array",
            "items": {
                "type": "string",
            },
        },
        "transitions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "from": {"type": "string"},
                    "event": {"type": "string"},
                    "action": {"type": "string"},
                    "to": {"type": "string"},
                },
                "required": [
                    "from",
                    "event",
                    "action",
                    "to",
                ],
                "additionalProperties": False,
            },
        },
    },
    "required": [
        "has_psm",
        "states",
        "transitions",
    ],
    "additionalProperties": False,
}


# JSON Schema used when the partial PSMs are combined.
MERGED_PSM_SCHEMA: dict[str, object] = {
    "type": "object",
    "properties": {
        "states": {
            "type": "array",
            "items": {
                "type": "string",
            },
        },
        "initial_state": {
            "type": "string",
        },
        "final_states": {
            "type": "array",
            "items": {
                "type": "string",
            },
        },
        "transitions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "from": {"type": "string"},
                    "event": {"type": "string"},
                    "action": {"type": "string"},
                    "to": {"type": "string"},
                },
                "required": [
                    "from",
                    "event",
                    "action",
                    "to",
                ],
                "additionalProperties": False,
            },
        },
    },
    "required": [
        "states",
        "initial_state",
        "final_states",
        "transitions",
    ],
    "additionalProperties": False,
}


# Store all output format configurations.
OUTPUT_FORMATS: dict[OutputFormatName, OutputFormat] = {
    OutputFormatName.F0: {
        "name": OutputFormatName.F0,
        "description": "Prompt-only direct JSON",
        "section_request_format": None,
        "merge_request_format": None,
    },
    OutputFormatName.F1: {
        "name": OutputFormatName.F1,
        "description": "Ollama JSON mode",
        "section_request_format": "json",
        "merge_request_format": "json",
    },
    OutputFormatName.F2: {
        "name": OutputFormatName.F2,
        "description": "Ollama JSON Schema mode",
        "section_request_format": SECTION_PSM_SCHEMA,
        "merge_request_format": MERGED_PSM_SCHEMA,
    },
}


# Return one output format configuration.
def get_output_format(output_format_name: OutputFormatName) -> OutputFormat:

    return OUTPUT_FORMATS[output_format_name]
