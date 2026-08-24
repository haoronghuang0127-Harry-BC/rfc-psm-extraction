from config.models.model_names import ModelName
from config.models.model_registry import get_all_model_configs, get_model_config
from config.models.model_types import ModelConfig, ProfileName



# return the selected profiles supported by one model.
def get_selected_profile_names(model_config: ModelConfig, profile: str) -> list[ProfileName]:
    if profile == "all":
        profile_names: list[ProfileName] = list(model_config["supported_profiles"])

        return profile_names

    if profile == "default":
        default_profile: ProfileName = model_config["default_profile"]

        return [default_profile]

    selected_profile: ProfileName = ProfileName(profile)

    if selected_profile not in model_config["supported_profiles"]:
        return []

    return [selected_profile]

# return the selected model configurations.
def get_selected_model_configs(model_name: ModelName) -> list[ModelConfig]:
    if model_name == ModelName.ALL:
        model_configs: list[ModelConfig] = get_all_model_configs()

        return model_configs

    model_config: ModelConfig = get_model_config(model_name=model_name)

    selected_model_configs: list[ModelConfig] = [model_config]

    return selected_model_configs