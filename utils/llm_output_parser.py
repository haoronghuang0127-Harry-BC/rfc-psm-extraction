import json
import re

# Extract the content inside <json>...</json>.
def extract_json_content(response: str) -> str | None:

    match: re.Match[str] | None = re.search(r"<json>(.*?)</json>", response,  re.DOTALL | re.IGNORECASE)

    if match is None:
        return None

    json_text: str = match.group(1).strip()

    if not json_text:
        return None

    if json_text.lower() == "none":
        return None

    return json_text


# Extract direct JSON text returned by F1 or F2.
def extract_direct_json_content(response: str) -> str | None:

    json_text: str = response.strip()

    # delete the markdown situation to get the json
    if json_text.startswith("```"):
        first_line_end: int = json_text.find("\n")

        if first_line_end != -1:
            json_text = json_text[first_line_end + 1:]

        if json_text.endswith("```"):
            json_text = json_text[:-3]

        json_text = json_text.strip()

    if not json_text:
        return None

    if json_text.lower() in ("none", "null"):
        return None

    return json_text

# Parse the json returned by the model.
def parse_json_from_response(response: str, allow_direct_json: bool = False) -> object | None:

    json_text: str | None = extract_json_content(response)

    if json_text is None:
        has_json_tags: bool = re.search(r"<json>.*?</json>", response, re.DOTALL | re.IGNORECASE) is not None

        if not allow_direct_json or has_json_tags:
            return None

        json_text = extract_direct_json_content(response)

        if json_text is None:
            return None


    try:
        parsed_output: object = json.loads(json_text)
    except json.JSONDecodeError:
        # return the error json text to analysis
        return json_text

    return parsed_output
    
