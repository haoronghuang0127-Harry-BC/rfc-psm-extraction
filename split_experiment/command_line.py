import argparse
from pathlib import Path

from config.models.model_names import ModelName
from config.models.model_registry import get_model_config
from config.models.model_types import ProfileName
from config.ollama_settings import ConnectionMode
from config.protocol.protocol_util import get_all_protocol_files

from split_experiment.types import SplitExperimentArguments


# read the command line arguments.
def read_command_line_to_value() -> SplitExperimentArguments:
    # get all protocol names.
    protocol_files: dict[str, Path] = get_all_protocol_files()
    protocol_names: list[str] = ["all"]

    for name in protocol_files.keys():
        protocol_names.append(name)

    # get all model names.
    model_names: list[str] = ["all"]

    for model_name in ModelName:
        if model_name != ModelName.ALL:
            model_names.append(model_name.value)

    # get all model profile names.
    profile_names: list[str] = ["all", "default"]

    for profile_name in ProfileName:
        profile_names.append(profile_name.value)

    # get all Ollama connection modes.
    connection_names: list[str] = []

    for connection_name in ConnectionMode:
        connection_names.append(connection_name.value)

    parser = argparse.ArgumentParser(description="Run the RFC splitting experiment.")

    # set the protocol argument.
    parser.add_argument("--protocol", choices=protocol_names, default="all", help="Protocol name or all. Default: all.")

    # set the model argument.
    parser.add_argument("--model", choices=model_names, default="all", help="Ollama model name or all. Default: all.")

    # set the model profile argument.
    parser.add_argument("--profile", choices=profile_names, default="default", help="Model profile, default, or all. Default: default.")

    # set the Ollama connection mode argument.
    parser.add_argument("--connection", choices=connection_names, default=ConnectionMode.AUTO.value, help="Ollama connection mode. Default: auto.")

    parsed_arguments = parser.parse_args()

    protocol: str = parsed_arguments.protocol
    model: ModelName = ModelName(parsed_arguments.model)
    profile: str = parsed_arguments.profile
    connection_mode: ConnectionMode = ConnectionMode(parsed_arguments.connection)

    # check whether a specific profile is supported by a specific model.
    if model != ModelName.ALL and profile not in ("all", "default"):
        model_config = get_model_config(model_name=model)
        selected_profile: ProfileName = ProfileName(profile)

        if selected_profile not in model_config["supported_profiles"]:
            supported_profile_names: list[str] = []

            for supported_profile in model_config["supported_profiles"]:
                supported_profile_names.append(supported_profile.value)

            supported_profile_text: str = ", ".join(supported_profile_names)
            parser.error(f"Model {model.value} does not support profile {profile}. Supported profiles: {supported_profile_text}.")

    arguments: SplitExperimentArguments = {
        "protocol": protocol,
        "model": model,
        "profile": profile,
        "connection_mode": connection_mode,
    }

    return arguments
