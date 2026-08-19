import argparse

from pathlib import Path

from config.models.model_names import ModelName
from config.ollama_settings import ConnectionMode
from config.protocol.protocol_util import get_all_protocol_files

from psmbench_local_baseline.types import Arguments



def read_command_line_to_value() -> Arguments:

    # get all the protocol names
    protocol_files: dict[str, Path] = get_all_protocol_files()
    protocol_names: list[str] = ["all"]
    for name in protocol_files.keys():
        protocol_names.append(name)

    # get all model names
    model_names: list[str] = []
    for name in ModelName:
        model_names.append(name.value)

    # get all ollama connection modes.
    connection_mode_names: list[str] = []
    for name in ConnectionMode:
        connection_mode_names.append(name.value)

    parser: argparse.ArgumentParser = argparse.ArgumentParser(description="Run the PSMBench local Ollama baseline.")


    # set the protocol argument
    parser.add_argument("--protocol", choices=protocol_names, required=True,
                        help="Protocol name or all.")

    # set the model argument
    parser.add_argument("--model", choices=model_names, required=True,
                        help="Ollama model name or all.")

    # set the model if thinking
    parser.add_argument("--thinking", action="store_true", default=False,
                        help="Enable optional thinking mode. Supported models: qwen3.5:9b and qwen3.5:27b. "
                              "QwQ uses intrinsic reasoning and is not controlled by this option. Default: disabled.")

    # set the ollama connection mode argument
    parser.add_argument("--connection", choices=connection_mode_names, default=ConnectionMode.AUTO.value,
                        help="Ollama connection mode. Default: auto.")

    parsed_arguments: argparse.Namespace = parser.parse_args()


    # get the value from the command line
    protocol: str = parsed_arguments.protocol
    model: ModelName = ModelName(parsed_arguments.model)
    connection_mode: ConnectionMode = ConnectionMode(parsed_arguments.connection)
    thinking: bool = parsed_arguments.thinking

    thinking_model_names: tuple[ModelName, ...] = (
        ModelName.QWEN3_5_9B,
        ModelName.QWEN3_5_27B,
    )

    if thinking and model not in thinking_model_names:
        parser.error("--thinking is supported only by qwen3.5:9b and qwen3.5:27b. "
        "Do not use --thinking with gemma3, mistral, qwq, or all. QwQ uses intrinsic reasoning automatically.")


    # create the arguments for return
    arguments: Arguments = {
        "protocol": protocol,
        "model": model,
        "connection_mode": connection_mode,
        "thinking": thinking
    }


    return arguments


        