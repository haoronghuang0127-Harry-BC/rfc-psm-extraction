from typing import TypedDict

from config.ollama_settings import ConnectionMode


class Arguments(TypedDict):
    # None means all the protocol
    protocol: str | None

    # None means all the model
    model: str | None

    # Select the local, remote, or automatic connection.
    connection_mode = ConnectionMode
