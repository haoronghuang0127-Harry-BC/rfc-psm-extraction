import argparse
from pathlib import Path

from config.models.model_names import ModelName
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

    # get the five non-thinking model names.
    model_names: list[str] = ["all"]

    for model_name in ModelName:
        if model_name not in (ModelName.ALL, ModelName.QWQ_32B):
            model_names.append(model_name.value)

    # get all Ollama connection modes.
    connection_names: list[str] = []

    for connection_name in ConnectionMode:
        connection_names.append(connection_name.value)

    parser = argparse.ArgumentParser(description="Run the RFC splitting experiment.")

    # set the protocol argument.
    parser.add_argument("--protocol", choices=protocol_names, default="all", help="Protocol name or all. Default: all.")

    # set the model argument.
    parser.add_argument("--model", choices=model_names, default="all", help="Ollama model name or all. Default: all.")

    # set the Ollama connection mode argument.
    parser.add_argument("--connection", choices=connection_names, default=ConnectionMode.AUTO.value, help="Ollama connection mode. Default: auto.")

    parsed_arguments = parser.parse_args()

    protocol: str = parsed_arguments.protocol
    model: ModelName = ModelName(parsed_arguments.model)
    connection_mode: ConnectionMode = ConnectionMode(parsed_arguments.connection)

    arguments: SplitExperimentArguments = {
        "protocol": protocol,
        "model": model,
        "connection_mode": connection_mode,
    }

    return arguments
