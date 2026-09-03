from typing import TypedDict

from config.models.model_names import ModelName
from config.ollama_settings import ConnectionMode


# store the values selected from the command line.
class PromptExperimentArguments(TypedDict):
    protocol: str
    model: ModelName
    profile: str
    output_control: str
    connection_mode: ConnectionMode



