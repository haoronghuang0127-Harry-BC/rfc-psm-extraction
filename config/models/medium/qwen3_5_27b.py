"""
qwen3.5:27b model
"""

from config.models.model_names import ModelName
from config.models.model_types import ModelConfig, ModelSize, ProfileName


MODEL_CONFIG: ModelConfig = {
    "name": ModelName.QWEN3_5_27B,
    "size_group": ModelSize.MEDIUM,
    "advertised_context": 262144,
    "default_profile": ProfileName.P0,
    "supported_profiles": [
        ProfileName.P0,
        ProfileName.P1,
        ProfileName.P2,
        ProfileName.P3,
    ],
}
