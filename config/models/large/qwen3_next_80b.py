"""
qwen3-next:80b-a3b-instruct-q4_K_M model
"""

from config.models.model_names import ModelName
from config.models.model_types import ModelConfig, ModelSize, ProfileName


MODEL_CONFIG: ModelConfig = {
    "name": ModelName.QWEN3_NEXT_80B,
    "size_group": ModelSize.LARGE,
    "advertised_context": 262144,
    "default_profile": ProfileName.P0,
    "supported_profiles": [
        ProfileName.P0,
        ProfileName.P1,
        ProfileName.P2,
    ],
}
