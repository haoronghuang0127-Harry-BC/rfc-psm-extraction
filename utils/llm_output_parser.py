import json
import re

# remove the model output with Markdown JSON code blocks (```json) or using json tag (<json>)
def _strip_json_wrappers(text: str) -> str:

    json_text: str = text.strip()

    while json_text:
        previous_text: str = json_text

        # remove the started markdown json code blocks
        json_text = re.sub(r"^\s*```(?:json)?\s*", "", json_text, flags=re.IGNORECASE)
        # remove the ended markdown json code blocks
        json_text = re.sub(r"\s*```\s*$", "", json_text)
        # remove started json tag
        json_text = re.sub(r"^\s*<json>\s*", "", json_text, flags=re.IGNORECASE)
        # remove ended json tag
        json_text = re.sub(r"\s*</json>\s*$", "", json_text, flags=re.IGNORECASE)
        json_text = json_text.strip()

        # after change the string if same break the loop
        if json_text == previous_text:
            break

    return json_text

# Extract the content inside <json>...</json>.
def extract_json_content(response: str) -> str | None:

    match: re.Match[str] | None = re.search(r"<json>(.*?)</json>", response,  re.DOTALL | re.IGNORECASE)

    if match is None:
        return None

    # using the new json judge
    json_text: str = _strip_json_wrappers(match.group(1))

    if not json_text:
        return None

    if json_text.lower() == "none":
        return None

    return json_text


# Extract direct JSON text returned by F1 or F2.
def extract_direct_json_content(response: str) -> str | None:

    json_text: str = _strip_json_wrappers(response)

    if not json_text:
        return None

    if json_text.lower() in ("none", "null"):
        return None

    return json_text

# Parse the json returned by the model.
def parse_json_from_response(response: str, allow_direct_json: bool = False) -> object | None:

    # extract content in <json> tag
    json_text: str | None = extract_json_content(response)

    # if can not find <json> tag
    if json_text is None:
        # check the response if have json tages
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


# in gemma 12b model some time will return the json tag in the markdown block
# the content in the markdown block is correct, so I make it valid json to continue emaining experimental procedure
def parse_json_from_responses_include_markdown(response: str, allow_direct_json: bool = False) -> object | None:
    # extract content in <json> tag
    json_text: str | None = extract_json_content(response)

    # if can not find <json> tag
    if json_text is None:
        # check the response if have json tages
        has_json_tags: bool = re.search(r"<json>.*?</json>", response, re.DOTALL | re.IGNORECASE) is not None

        # if do not have the json tag return None
        if has_json_tags:
            return None

        # chekc if response have markdown tag
        markdown_match: re.Match[str] | None = re.fullmatch(r"\s*```json\s*(.*?)\s*```\s*", response, re.DOTALL | re.IGNORECASE)

        # if have markdown tag extraction the json content
        if markdown_match is not None:  
            json_text = markdown_match.group(1).strip()
        elif allow_direct_json:
            # if direct json is allowed, try to extract direct json.
            json_text = extract_direct_json_content(response)
        else:
            return None

        # none, null, empty are not alllow
        if not json_text or json_text.lower() in ("none", "null"):
            return None

    try:
        parsed_output: object = json.loads(json_text)
    except json.JSONDecodeError:
        return json_text

    return parsed_output
