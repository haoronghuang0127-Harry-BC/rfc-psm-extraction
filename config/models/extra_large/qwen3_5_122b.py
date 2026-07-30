"""
qwen3.5:122b model
"""

from config.models.model_names import ModelName
from config.models.model_types import ModelConfig, ModelSize, ProfileName


MODEL_CONFIG: ModelConfig = {
    "name": ModelName.QWEN3_5_122B,
    "size_group": ModelSize.EXTRA_LARGE,
    "advertised_context": 262144,
    "default_profile": ProfileName.P0,
    "supported_profiles": [
        ProfileName.P0,
        ProfileName.P1,
        ProfileName.P2,
        ProfileName.P3,
    ],
}
