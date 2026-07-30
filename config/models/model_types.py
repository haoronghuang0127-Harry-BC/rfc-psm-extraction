from typing import TypedDict
from enum import StrEnum

from .model_names import ModelName

# the size of the model
class ModelSize(StrEnum):
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    EXTRA_LARGE = "extra_large"

# Parameter profile names
class ProfileName(StrEnum):
    P0 = "P0"
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"
    P4_LOW = "P4-low"
    P4_MEDIUM = "P4-medium"

# Store the configuration of one Ollama model.
class ModelConfig(TypedDict):
    name: ModelName
    size_group: ModelSize
    advertised_context: int
    default_profile: ProfileName
    supported_profiles: list[ProfileName]
