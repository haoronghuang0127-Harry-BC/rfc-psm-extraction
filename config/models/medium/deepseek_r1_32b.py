"""
deepseek-r1:32b model
"""

from config.models.model_names import ModelName
from config.models.model_types import ModelConfig, ModelSize, ProfileName


MODEL_CONFIG: ModelConfig = {
    "name": ModelName.DEEPSEEK_R1_32B,
    "size_group": ModelSize.MEDIUM,
    "advertised_context": 131072,
    "default_profile": ProfileName.P0,
    "supported_profiles": [
        ProfileName.P0,
        ProfileName.P3,
    ],
}
