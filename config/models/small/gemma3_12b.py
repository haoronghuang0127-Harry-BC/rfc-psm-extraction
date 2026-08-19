"""
gemma3:12b model
"""

from config.models.model_names import ModelName
from config.models.model_types import ModelConfig, ModelSize, ProfileName


MODEL_CONFIG: ModelConfig = {
    "name": ModelName.GEMMA3_12B,
    "size_group": ModelSize.SMALL,
    "advertised_context": 131072,
    "default_profile": ProfileName.GEMMA_MISTRAL_NO_THINK,
    "supported_profiles": [
        ProfileName.GEMMA_MISTRAL_NO_THINK
    ],
}
