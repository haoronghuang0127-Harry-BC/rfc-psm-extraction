from typing import TypedDict

from config.models.model_names import ModelName
from config.ollama_settings import ConnectionMode


# store one FSM transition.
TransitionRecord = TypedDict(
    "TransitionRecord",
    {
        "from": str,
        "event": str,
        "action": str,
        "to": str,
    }
)


# store the research FSM structure.
class ResearchStateMachine(TypedDict):
    states: list[str]
    transitions: list[TransitionRecord]


# store one output control configuration.
class OutputControl(TypedDict):
    request_format: str | dict[str, object] | None
    prompt_output_style: str


# store the values selected from the command line.
class PromptExperimentArguments(TypedDict):
    protocol: str
    model: ModelName
    profile: str
    output_control: str
    connection_mode: ConnectionMode



