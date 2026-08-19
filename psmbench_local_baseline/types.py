from typing import TypedDict

from config.models.model_names import ModelName
from config.ollama_settings import ConnectionMode


class Arguments(TypedDict):
    # None means all the protocol
    protocol: str

    # None means all the model
    model: ModelName

    # Select the local, remote, or automatic connection.
    connection_mode: ConnectionMode

    # Whether optional thinking is enabled.
    thinking: bool
