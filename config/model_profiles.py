from typing import TypedDict

from config.models.model_types import ProfileName

# model parameter profile
class ModelProfile(TypedDict):
    description: str
    options: dict[str, int | float]
    think: bool | str | None

_MODEL_PROFILES: dict[ProfileName, ModelProfile] = {
    ProfileName.P0: {
        "description": "Strict baseline",
        "options": {
            "num_ctx": 65536,
            "num_predict": 4096,
            "temperature": 0.0,
            "top_p": 0.9,
            "top_k": 40,
            "repeat_penalty": 1.05,
            "seed": 42,
        },
        "think": False,
    },

    ProfileName.P1: {
        "description": "Long context",
        "options": {
            "num_ctx": 131072,
            "num_predict": 8192,
            "temperature": 0.0,
            "top_p": 0.9,
            "top_k": 40,
            "repeat_penalty": 1.05,
            "seed": 42,
        },
        "think": False,
    },

    ProfileName.P2: {
        "description": "Sampling and stability",
        "options": {
            "num_ctx": 65536,
            "num_predict": 4096,
            "temperature": 0.2,
            "top_p": 0.9,
            "top_k": 40,
            "repeat_penalty": 1.05,
            "seed": 42,
        },
        "think": False,
    },

    ProfileName.P3: {
        "description": "Thinking enabled",
        "options": {
            "num_ctx": 131072,
            "num_predict": 8192,
            "temperature": 0.0,
            "top_p": 0.9,
            "top_k": 40,
            "repeat_penalty": 1.05,
            "seed": 42,
        },
        "think": True,
    },

    ProfileName.P4_LOW: {
        "description": "GPT-OSS low reasoning",
        "options": {
            "num_ctx": 131072,
            "num_predict": 8192,
            "temperature": 0.0,
            "seed": 42,
        },
        "think": "low",
    },

    ProfileName.P4_MEDIUM: {
        "description": "GPT-OSS medium reasoning",
        "options": {
            "num_ctx": 131072,
            "num_predict": 8192,
            "temperature": 0.0,
            "seed": 42,
        },
        "think": "medium",
    },
}

# Return one model parameter profile.
def get_model_profile(profile_name: ProfileName) -> ModelProfile:
    model_profile: ModelProfile = _MODEL_PROFILES[profile_name]

    return model_profile