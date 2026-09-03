from typing import TypedDict

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