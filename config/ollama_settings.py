"""
Ollama connection setting
"""

import os

from dotenv import load_dotenv

from typing import TypedDict
from enum import StrEnum

from config.paths import PROJECT_FOLDER_DIR

from utils.ollama_client import can_connect_to_ollama

load_dotenv(dotenv_path=PROJECT_FOLDER_DIR / ".env")

# Available Ollama connection modes.
class ConnectionMode(StrEnum):
    LOCAL = "local"
    REMOTE = "remote"
    AUTO = "auto"

# the information about ollama connection 
class OllamaConnection(TypedDict):
    connection_name: ConnectionMode
    ollama_url: str
    request_timeout_seconds: int
    extra_headers: dict[str, str]

# add extra header if need
def _build_extra_headers() -> dict[str, str]:
    extra_headers: dict[str, str] = {}
    

    bearer_token: str = os.getenv("OLLAMA_BEARER_TOKEN","").strip()

    if bearer_token:
        extra_headers["Authorization"] = f"Bearer {bearer_token}"


    return extra_headers



def _build_connection(connection_name: ConnectionMode, ollama_url: str, request_timeout_seconds: int, extra_headers: dict[str, str]) -> OllamaConnection:

    connection: OllamaConnection = {
        "connection_name": connection_name,
        "ollama_url": ollama_url,
        "request_timeout_seconds": request_timeout_seconds,
        "extra_headers": extra_headers
    }

    return connection

def get_ollama_connection(connection_mode: ConnectionMode = ConnectionMode.AUTO) -> OllamaConnection:

    # get local url
    local_url: str = os.getenv("OLLAMA_LOCAL_URL","http://127.0.0.1:11434").strip()

    # get remote url
    remote_url: str = os.getenv("OLLAMA_REMOTE_URL","").strip()

    # get request timeout time(seconds)
    request_timeout_text: str = os.getenv("OLLAMA_REQUEST_TIMEOUT_SECONDS","1800")
    request_timeout_seconds: int = int(request_timeout_text)

    # set check timeout(seconds)
    connection_check_timeout: int = 5

    # get request headers
    extra_headers: dict[str, str] = _build_extra_headers()



    # if using local ollama
    if connection_mode == ConnectionMode.LOCAL:
        if not can_connect_to_ollama(ollama_url=local_url, extra_headers=extra_headers, timeout_seconds=connection_check_timeout):
            raise RuntimeError("The local Ollama server is not available.")

        return _build_connection(connection_name=ConnectionMode.LOCAL, ollama_url=local_url, request_timeout_seconds=request_timeout_seconds, extra_headers=extra_headers)

    # if using remote ollama
    if connection_mode == ConnectionMode.REMOTE:
        if not remote_url:
            raise RuntimeError("OLLAMA_REMOTE_URL is not set.")

        if not can_connect_to_ollama(ollama_url=remote_url, extra_headers=extra_headers, timeout_seconds=connection_check_timeout):
            raise RuntimeError("The remote Ollama server is not available.")

        return _build_connection(connection_name=ConnectionMode.REMOTE, ollama_url=remote_url, request_timeout_seconds=request_timeout_seconds, extra_headers=extra_headers)


    # if using auto mode, make the program to judge using local or remote
    if connection_mode == ConnectionMode.AUTO:
        # uisng local ollama server first
        if can_connect_to_ollama(ollama_url=local_url, extra_headers=extra_headers, timeout_seconds=connection_check_timeout):
            return _build_connection(connection_name=ConnectionMode.LOCAL, ollama_url=local_url, request_timeout_seconds=request_timeout_seconds, extra_headers=extra_headers)


        # if the local ollama server is not available, using remote ollama server
        if remote_url and can_connect_to_ollama(ollama_url=remote_url, extra_headers=extra_headers, timeout_seconds=connection_check_timeout):
            return _build_connection(connection_name=ConnectionMode.REMOTE, ollama_url=remote_url, request_timeout_seconds=request_timeout_seconds, extra_headers=extra_headers)
        


        # if local and remote ollama server both not available raise the error
        raise RuntimeError(
            "No available local or remote Ollama "
            "server was found."
        )

    # if do not choose the connection mode raise the error
    raise ValueError(
        "connection_mode must be "
        "'local', 'remote', or 'auto'."
    )

