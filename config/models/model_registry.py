from .model_types import ModelConfig, ModelSize
from .model_names import ModelName

from .small.qwen3_5_9b import MODEL_CONFIG as QWEN3_5_9B
from .small.ministral_3_8b import MODEL_CONFIG as MINISTRAL_3_8B
from .small.llama3_1_8b import MODEL_CONFIG as LLAMA3_1_8B
from .small.gemma3_12b import MODEL_CONFIG as GEMMA3_12B
from .small.deepseek_r1_8b import MODEL_CONFIG as DEEPSEEK_R1_8B

from .medium.qwen3_5_27b import MODEL_CONFIG as QWEN3_5_27B
from .medium.qwen3_5_35b import MODEL_CONFIG as QWEN3_5_35B
from .medium.mistral_small3_2_24b import MODEL_CONFIG as MISTRAL_SMALL3_2_24B
from .medium.gemma3_27b import MODEL_CONFIG as GEMMA3_27B
from .medium.deepseek_r1_32b import MODEL_CONFIG as DEEPSEEK_R1_32B
from .medium.gpt_oss_20b import MODEL_CONFIG as GPT_OSS_20B

from .large.llama3_3_70b import MODEL_CONFIG as LLAMA3_3_70B
from .large.deepseek_r1_70b import MODEL_CONFIG as DEEPSEEK_R1_70B
from .large.qwen3_next_80b import MODEL_CONFIG as QWEN3_NEXT_80B

from .extra_large.gpt_oss_120b import MODEL_CONFIG as GPT_OSS_120B
from .extra_large.qwen3_5_122b import MODEL_CONFIG as QWEN3_5_122B


# Store all available model configurations.
ALL_MODEL_CONFIGS: tuple[ModelConfig, ...] = (
    QWEN3_5_9B,
    MINISTRAL_3_8B,
    LLAMA3_1_8B,
    GEMMA3_12B,
    DEEPSEEK_R1_8B,
    QWEN3_5_27B,
    QWEN3_5_35B,
    MISTRAL_SMALL3_2_24B,
    GEMMA3_27B,
    DEEPSEEK_R1_32B,
    GPT_OSS_20B,
    LLAMA3_3_70B,
    DEEPSEEK_R1_70B,
    QWEN3_NEXT_80B,
    GPT_OSS_120B,
    QWEN3_5_122B,
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
