import json
import time
import urllib.error
import urllib.request

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
