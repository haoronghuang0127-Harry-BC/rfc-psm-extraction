from config.models.model_profiles import ModelProfile
from config.models.model_types import ModelConfig
from config.ollama_settings import OllamaConnection

from utils.ollama_client import call_ollama_generate


def get_ollama_response(prompt: str, connection: OllamaConnection, model_config: ModelConfig, model_profile: ModelProfile) -> dict[str, object]:
    # get the ollama url
    url: str = connection["ollama_url"]
    # get the using model
    model: str = model_config["name"].value
    # get the options
    options: dict[str, int | float] = model_profile["options"]
    # get request_timeout_seconds
    request_timeout_seconds: int = connection["request_timeout_seconds"]
    # get if uisng think model
    think: bool | None = model_profile["think"]
    # set the output format
    output_format = None
    # get the header
    headers: dict[str, str] = connection["extra_headers"]

    # get the ollama response
    response: dict[str, object] = call_ollama_generate(ollama_url=url, model=model, prompt=prompt, options=options,
                                                       request_timeout_seconds=request_timeout_seconds, think=think,
                                                       output_format=output_format, extra_headers=headers)

    return response

