"""
ministral-3:8b model
"""

from config.models.model_names import ModelName
from config.models.model_types import ModelConfig, ModelSize, ProfileName

MODEL_CONFIG: ModelConfig = {
    "name": ModelName.MINISTRAL_3_8B,
    "size_group": ModelSize.SMALL,
    "advertised_context": 262144,
    "default_profile": ProfileName.P0,
    "supported_profiles": [
        ProfileName.P0,
        ProfileName.P1,
        ProfileName.P2,
    ],
}
