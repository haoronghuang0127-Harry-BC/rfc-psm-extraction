from typing import TypedDict
from enum import StrEnum

from .model_names import ModelName

# the size of the model
class ModelSize(StrEnum):
    SMALL = "small"
    MEDIUM = "medium"

# Parameter profile names
class ProfileName(StrEnum):
    QWEN_NO_THINK = "qwen-no-think"
    QWEN_THINK = "qwen-think"
    GEMMA_MISTRAL_NO_THINK = "gemma-mistral-no-think"
    QWQ_REASONING  = "qwq-reasoning"

# Store the configuration of one Ollama model.
class ModelConfig(TypedDict):
    name: ModelName
    size_group: ModelSize
    advertised_context: int
    default_profile: ProfileName
    supported_profiles: list[ProfileName]
