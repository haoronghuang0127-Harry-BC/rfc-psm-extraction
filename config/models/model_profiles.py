from typing import TypedDict

from config.models.model_types import ProfileName


# Store one model parameter profile.
class ModelProfile(TypedDict):
    description: str
    options: dict[str, int | float]
    think: bool | None


# Store all model parameter profiles.
_MODEL_PROFILES: dict[ProfileName, ModelProfile] = {
    ProfileName.QWEN_NO_THINK: {
        "description": "Qwen 256K context without thinking",
        "options": {
            "num_ctx": 262144,
            "num_predict": 32768,
            "temperature": 0.0,
            "top_p": 0.9,
            "top_k": 40,
            "repeat_penalty": 1.0,
            "seed": 42,
        },
        "think": False,
    },

    ProfileName.QWEN_THINK: {
        "description": "Qwen 256K context with thinking",
        "options": {
            "num_ctx": 262144,
            "num_predict": 32768,
            "temperature": 0.0,
            "top_p": 0.9,
            "top_k": 40,
            "repeat_penalty": 1.0,
            "seed": 42,
        },
        "think": True,
    },

    ProfileName.GEMMA_MISTRAL_NO_THINK: {
        "description": "Gemma and Mistral 128K context without Ollama thinking",
        "options": {
            "num_ctx": 131072,
            "num_predict": 32768,
            "temperature": 0.0,
            "top_p": 0.9,
            "top_k": 40,
            "repeat_penalty": 1.0,
            "seed": 42,
        },
        "think": None,
    },

    ProfileName.QWQ_REASONING: {
        "description": "QwQ 40K intrinsic reasoning",
        "options": {
            "num_ctx": 40960,
            "num_predict": 32768,
            "temperature": 0.0,
            "top_p": 0.9,
            "top_k": 40,
            "repeat_penalty": 1.0,
            "seed": 42,
        },
        "think": None,
    },
}


# Return one model parameter profile.
def get_model_profile(profile_name: ProfileName) -> ModelProfile:
    model_profile: ModelProfile = _MODEL_PROFILES[profile_name]

    return model_profile