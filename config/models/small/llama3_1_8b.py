"""
llama3.1:8b model
"""

from config.models.model_names import ModelName
from config.models.model_types import ModelConfig, ModelSize, ProfileName


MODEL_CONFIG: ModelConfig = {
    "name": ModelName.LLAMA3_1_8B,
    "size_group": ModelSize.SMALL,
    "advertised_context": 131072,
    "default_profile": ProfileName.P0,
    "supported_profiles": [
        ProfileName.P0,
        ProfileName.P1,
        ProfileName.P2,
    ],
}
