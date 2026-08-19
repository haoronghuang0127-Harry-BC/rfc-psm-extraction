"""
qwq:32b model
"""

from config.models.model_names import ModelName
from config.models.model_types import ModelConfig, ModelSize, ProfileName


MODEL_CONFIG: ModelConfig = {
    "name": ModelName.QWQ_32B,
    "size_group": ModelSize.MEDIUM,
    "advertised_context": 40960,
    "default_profile": ProfileName.QWQ_REASONING,
    "supported_profiles": [
        ProfileName.QWQ_REASONING,
    ],
}