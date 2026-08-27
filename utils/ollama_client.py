import json
import time
import urllib.error
import urllib.request

from typing import Final

_QWEN_THINK_CHAT_MODELS: Final[list[str]] = [
    "qwen3.5:9b",
    "qwen3.5:27b",
]


def _build_request_headers(extra_headers: dict[str, str] | None = None) -> dict[str, str]:

    # set http headers
    request_headers: dict[str, str] = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "rfc-psm-project",
    }

    # judge if add the extra headers
    if extra_headers is not None:
        request_headers.update(extra_headers)

    return request_headers

# check if can connect the ollama server
def can_connect_to_ollama(ollama_url: str, extra_headers: dict[str, str], timeout_seconds: int) -> bool:

    api_url: str = ollama_url.rstrip("/") + "/api/tags"

    # get request headers
    request_headers: dict[str, str] = _build_request_headers(extra_headers)

    request: urllib.request.Request = urllib.request.Request(url=api_url, headers=request_headers, method="GET")

    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds):
            return True
    except (urllib.error.URLError, TimeoutError):
        return False


# Send a small request used to record the Ollama environment.
def _call_ollama_information_api(ollama_url: str, api_path: str, extra_headers: dict[str, str], timeout_seconds: int) -> dict[str, object]:

    api_url: str = ollama_url.rstrip("/") + api_path
    request_headers: dict[str, str] = _build_request_headers(extra_headers)
    request: urllib.request.Request = urllib.request.Request(url=api_url, headers=request_headers, method="GET")

    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            response_text: str = response.read().decode("utf-8")
    except urllib.error.HTTPError as error:
        error_text: str = error.read().decode("utf-8", errors="replace")

        raise RuntimeError(f"Ollama returned HTTP {error.code}: {error_text}") from error
    except (urllib.error.URLError, TimeoutError) as error:
        raise RuntimeError(f"Could not connect to Ollama at {api_url}: {error}") from error

    try:
        response_value: object = json.loads(response_text)
    except json.JSONDecodeError as error:
        raise RuntimeError("Ollama returned invalid environment information.") from error

    if not isinstance(response_value, dict):
        raise RuntimeError("The Ollama environment response is not a JSON object.")

    return response_value


# Return information about models currently loaded by Ollama.
def get_ollama_running_models(ollama_url: str, extra_headers: dict[str, str], timeout_seconds: int) -> list[dict[str, object]]:

    response: dict[str, object] = _call_ollama_information_api(ollama_url=ollama_url, api_path="/api/ps", extra_headers=extra_headers, timeout_seconds=timeout_seconds)
    models_value: object = response.get("models", [])

    if not isinstance(models_value, list):
        return []

    models: list[dict[str, object]] = []

    for model_value in models_value:
        if isinstance(model_value, dict):
            models.append(model_value)

    return models

def call_ollama_generate(ollama_url: str, model: str, prompt: str, options: dict[str, int | float],
                         request_timeout_seconds: int, think: bool | str | None = None,
                         output_format: str | dict[str, object] | None = None,
                         extra_headers: dict[str, str] | None = None,
                         max_attempts: int = 3,
                         retry_delay_seconds: int = 2) -> dict[str, object]:

    if max_attempts <= 0:
        raise ValueError("max_attempts must be greater than zero.")

    # build the ollama api address
    api_url: str = ollama_url.rstrip("/") + "/api/generate"

    # build the request data
    request_data: dict[str, object] = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": options
    }

    # judge if add the thinking setting
    if think is not None:
        request_data["think"] = think


    # judge if add output format
    if output_format is not None:
        request_data["format"] = output_format


    # convert to json
    request_body: bytes = json.dumps(request_data, ensure_ascii=False).encode("utf-8")

    # get request headers
    request_headers: dict[str, str] = _build_request_headers(extra_headers)

    for attempt in range(1, max_attempts + 1):
        # create http request
        request: urllib.request.Request = urllib.request.Request(url=api_url, data=request_body, headers=request_headers, method="POST")

        try:
            with urllib.request.urlopen(request, timeout=request_timeout_seconds) as response:
                response_text: str = response.read().decode("utf-8")

            # Convert the Ollama response from JSON text into a dictionary.
            response_value: object = json.loads(response_text)

            if not isinstance(response_value, dict):
                raise RuntimeError("The Ollama response is not a JSON object.")

            response_data: dict[str, object] = response_value

            return response_data

        except urllib.error.HTTPError as error:
            error_text: str = error.read().decode("utf-8", errors="replace")

            retryable_status_codes: tuple[int, ...] = (408, 429, 500, 502, 503, 504)

            if error.code not in retryable_status_codes or attempt == max_attempts:
                raise RuntimeError(
                    f"Ollama returned HTTP {error.code}: "
                    f"{error_text}"
                ) from error

        except (urllib.error.URLError, TimeoutError) as error:
            if attempt == max_attempts:
                raise RuntimeError(
                    f"Could not connect to Ollama at {api_url}: "
                    f"{error}"
                ) from error

        except json.JSONDecodeError as error:
            if attempt == max_attempts:
                raise RuntimeError("Ollama returned an invalid JSON response.") from error

        print(
            "Ollama request failed. Retrying: "
            f"attempt {attempt + 1} of {max_attempts}."
        )

        if retry_delay_seconds > 0:
            time.sleep(retry_delay_seconds)

    raise RuntimeError("The Ollama request could not be completed.")



# this function is for the qwen3.5 9b and 27b 
# when use the thinking model
# if use the api, /api/generate and set the parameter think = true and set the output format using json
# it will put the final result in the thinking value not in the response
# so create a new function to fix this problem
# ollama using the api /api/chat can fix this problem
def call_ollama_chat(ollama_url: str, model: str, prompt: str, options: dict[str, int | float],
                     request_timeout_seconds: int, think: bool | str | None = None,
                     output_format: str | dict[str, object] | None = None,
                     extra_headers: dict[str, str] | None = None,
                     max_attempts: int = 3,
                     retry_delay_seconds: int = 2) -> dict[str, object]:

    if max_attempts <= 0:
            raise ValueError("max_attempts must be greater than zero.")
    
    # build the ollama api address
    api_url: str = ollama_url.rstrip("/") + "/api/chat"

    # build the request data
    # the /api/chat request data is different to /api/generate
    request_data: dict[str, object] = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "stream": False,
        "options": options
    }

    # judge if add the thinking setting
    if think is not None:
        request_data["think"] = think

    # judge if add output format
    if output_format is not None:
        request_data["format"] = output_format

    # convert to json
    request_body: bytes = json.dumps(request_data, ensure_ascii=False).encode("utf-8")

    # get request headers
    request_headers: dict[str, str] = _build_request_headers(extra_headers)

    for attempt in range(1, max_attempts + 1):
        # create http request
        request: urllib.request.Request = urllib.request.Request(url=api_url, data=request_body, headers=request_headers, method="POST")

        try:
            with urllib.request.urlopen(request, timeout=request_timeout_seconds) as response:
                response_text: str = response.read().decode("utf-8")

            # convert the Ollama response from JSON text into a dictionary
            response_value: object = json.loads(response_text)

            if not isinstance(response_value, dict):
                raise RuntimeError("The Ollama response is not a JSON object.")

            # get the message object returned by /api/chat
            message_value: object = response_value.get("message")

            if not isinstance(message_value, dict):
                raise RuntimeError("The Ollama chat response does not contain a message object.")

            # get final response and thinking response
            content_value: object = message_value.get("content", "")
            thinking_value: object = message_value.get("thinking", "")

            # the final answer must be a non-empty string
            if not isinstance(content_value, str) or not content_value.strip():
                raise RuntimeError("Ollama chat returned an empty final response.")

            # thinking is optional
            if not isinstance(thinking_value, str):
                thinking_value = ""

            # reject an output truncated by the token limit
            if response_value.get("done_reason") == "length":
                raise RuntimeError("Ollama chat stopped because the output length limit was reached.")

            # check structured output returned by Ollama
            if output_format is not None:
                try:
                    json.loads(content_value)
                except json.JSONDecodeError as error:
                    raise RuntimeError("Ollama chat returned invalid structured JSON content.") from error

            # copy the original chat response
            response_data: dict[str, object] = dict(response_value)

            # remove the nested message object
            response_data.pop("message", None)

            # convert chat fields into the same fields used by /api/generate
            response_data["response"] = content_value
            response_data["thinking"] = thinking_value

            return response_data

        except urllib.error.HTTPError as error:
            error_text: str = error.read().decode("utf-8", errors="replace")

            retryable_status_codes: tuple[int, ...] = (408, 429, 500, 502, 503, 504)

            if error.code not in retryable_status_codes or attempt == max_attempts:
                raise RuntimeError(f"Ollama returned HTTP {error.code}: {error_text}") from error

        except (urllib.error.URLError, TimeoutError) as error:
            if attempt == max_attempts:
                raise RuntimeError(f"Could not connect to Ollama at {api_url}: {error}") from error

        except json.JSONDecodeError as error:
            if attempt == max_attempts:
                raise RuntimeError("Ollama returned an invalid JSON response.") from error

        print(f"Ollama request failed. Retrying: attempt {attempt + 1} of {max_attempts}.")

        if retry_delay_seconds > 0:
            time.sleep(retry_delay_seconds)

    raise RuntimeError("The Ollama request could not be completed.")



def call_ollama_with_model_routing(ollama_url: str, model: str, prompt: str, options: dict[str, int | float],
                                   request_timeout_seconds: int, think: bool | str | None = None, output_format: str | dict[str, object] | None = None, 
                                   extra_headers: dict[str, str] | None = None, max_attempts: int = 3, retry_delay_seconds: int = 2) -> dict[str, object]:

    # Only Qwen 3.5 9B/27B thinking mode uses /api/chat.
    use_chat: bool = model in _QWEN_THINK_CHAT_MODELS and think is True

    # if using Qwen 3.5 9B/27B need to change the api to request the ollama 
    ollama_call = call_ollama_chat if use_chat else call_ollama_generate
    

    return ollama_call(
        ollama_url=ollama_url,
        model=model,
        prompt=prompt,
        options=options,
        request_timeout_seconds=request_timeout_seconds,
        think=think,
        output_format=output_format,
        extra_headers=extra_headers,
        max_attempts=max_attempts,
        retry_delay_seconds=retry_delay_seconds
    )