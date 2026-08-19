from config.models.model_names import ModelName
from config.models.model_types import ModelConfig,ModelSize

from config.models.medium.gemma3_27b import MODEL_CONFIG as GEMMA3_27B
from config.models.medium.mistral_small3_1_24b import MODEL_CONFIG as MISTRAL_SMALL3_1_24B
from config.models.medium.qwen3_5_27b import MODEL_CONFIG as QWEN3_5_27B
from config.models.medium.qwq_32b import MODEL_CONFIG as QWQ_32B

from config.models.small.gemma3_12b import MODEL_CONFIG as GEMMA3_12B
from config.models.small.qwen3_5_9b import MODEL_CONFIG as QWEN3_5_9B

# Store all available model configurations.
ALL_MODEL_CONFIGS: tuple[ModelConfig, ...] = (
    QWEN3_5_9B,
    QWEN3_5_27B,
    GEMMA3_12B,
    GEMMA3_27B,
    MISTRAL_SMALL3_1_24B,
    QWQ_32B,
)

# Store model configurations using model names as keys.
_MODEL_CONFIGS_BY_NAME: dict[ModelName, ModelConfig] = {
    model_config["name"]: model_config for model_config in ALL_MODEL_CONFIGS
}


# return model config
def get_model_config(model_name: ModelName) -> ModelConfig:

    model_config: ModelConfig = _MODEL_CONFIGS_BY_NAME[model_name]

    return model_config

# return all model configs
def get_all_model_configs() -> list[ModelConfig]:

    model_configs: list[ModelConfig] = list(ALL_MODEL_CONFIGS)

    return model_configs

# return model configs by size
def get_model_configs_by_size(size_group: ModelSize) -> list[ModelConfig]:

    configs: list[ModelConfig] = []

    for config in ALL_MODEL_CONFIGS:
        if config["size_group"] == size_group:
            configs.append(config)


    return configs
