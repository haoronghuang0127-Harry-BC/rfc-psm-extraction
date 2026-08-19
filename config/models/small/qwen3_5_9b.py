"""
Qwen3.5:9b model
"""

from config.models.model_names import ModelName
from config.models.model_types import ModelConfig, ModelSize, ProfileName


MODEL_CONFIG: ModelConfig = {
    "name": ModelName.QWEN3_5_9B,
    "size_group": ModelSize.SMALL,
    "advertised_context": 262144,
    "default_profile": ProfileName.QWEN_NO_THINK,
    "supported_profiles": [
        ProfileName.QWEN_NO_THINK,
        ProfileName.QWEN_THINK
    ]
}
