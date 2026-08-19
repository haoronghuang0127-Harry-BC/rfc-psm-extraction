"""
mistral-small3.1:24b model
"""

from config.models.model_names import ModelName
from config.models.model_types import ModelConfig, ModelSize, ProfileName


MODEL_CONFIG: ModelConfig = {
    "name": ModelName.MISTRAL_SMALL3_1_24B,
    "size_group": ModelSize.MEDIUM,
    "advertised_context": 131072,
    "default_profile": ProfileName.GEMMA_MISTRAL_NO_THINK,
    "supported_profiles": [
        ProfileName.GEMMA_MISTRAL_NO_THINK,
    ],
}