import argparse
from inspect import Arguments
from pathlib import Path

from config.models.model_names import ModelName
from config.ollama_settings import ConnectionMode
from config.protocol.protocol_util import get_all_protocol_files



def read_commnad_line_to_value() -> Arguments:

    # get all the protocol names
    protocol_files: dict[str, Path] = get_all_protocol_files()
    protocol_names: list[str] = ["ALL"]
    for name in protocol_files.keys():
        protocol_names.append(name)

    # get all model names
    model_names: list[str] = ["ALL"]
    for name in ModelName:
        model_names.append(name.value)

    # get all ollama connection modes.
    connection_mode_names: list[str] = []
    for name in ConnectionMode:
        connection_mode_names.append(name.value)

    parser: argparse.ArgumentParser = argparse.ArgumentParser(description="Run the PSMBench local Ollama baseline.")


    # set the protocol argument
    parser.add_argument("--protocol", type=str.upper, choices=protocol_names, default="ALL",
                        help="Protocol name or ALL. Default: ALL.")

    # set the model argument
    parser.add_argument("--model", choices=model_names, default="all",
                        help="Ollama model name or all. Default: all.")

    # set the ollama connection mode argument
    parser.add_argument("--connection", choices=connection_mode_names, default=ConnectionMode.AUTO.value,
                        help="Ollama connection mode. Default: auto.")

    parsed_arguments: argparse.Namespace = parser.parse_args()
        