"""
gpt-oss:120b model
"""

from config.models.model_names import ModelName
from config.models.model_types import ModelConfig, ModelSize, ProfileName


MODEL_CONFIG: ModelConfig = {
    "name": ModelName.GPT_OSS_120B,
    "size_group": ModelSize.EXTRA_LARGE,
    "advertised_context": 131072,
    "default_profile": ProfileName.P4_LOW,
    "supported_profiles": [
        ProfileName.P4_LOW,
        ProfileName.P4_MEDIUM,
    ],
}
