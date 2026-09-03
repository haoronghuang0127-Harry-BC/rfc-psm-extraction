from pathlib import Path

from utils.files_util import load_json_file, save_json_file
from utils.llm_output_parser import parse_json_from_response, parse_json_from_responses_include_markdown

"""
process extraction responses
"""
# extract valid response strings from Ollama response records.
def _extract_partial_responses(response_records: list[dict[str, object]], allow_direct_json: bool = True) -> list[str]:
    # init the result
    partial_responses: list[str] = []

    for record in response_records:
        response: object = record.get("response")

        # remove the none part of not string 
        if not isinstance(response, str):
            continue

        # parse tagged json(<json>....</json>) or direct json.
        parsed_response: object | None = parse_json_from_response(response=response, allow_direct_json=allow_direct_json)

        # ignore None, invalid JSON text, lists, and other invalid structures.
        if not isinstance(parsed_response, dict):
            continue

        partial_responses.append(response)

    return partial_responses


# build an output file path from an input response file.
def _build_output_file_path(input_file: Path, output_directory: Path, input_suffix: str, output_suffix: str) -> Path:
    if not input_file.stem.endswith(input_suffix):
        raise ValueError(f"Input file does not end with {input_suffix}: {input_file.name}")

    # remove the input suffix from the original file name.
    base_file_name: str = input_file.stem.removesuffix(input_suffix).rstrip("_")

    output_file_name: str = f"{base_file_name}{output_suffix}.json"

    output_file: Path = output_directory / output_file_name

    return output_file


# Process all extraction response files in one experiment directory.
def process_extraction_response_files(input_directory: Path, output_directory: Path, input_pattern: str, input_suffix: str, output_suffix: str, allow_direct_json: bool = True) -> list[Path]:
    input_files: list[Path] = sorted(input_directory.glob(input_pattern))

    if not input_files:
        raise FileNotFoundError(f"Could not find response files in: {input_directory}")

    output_files: list[Path] = []

    for input_file in input_files:
        response_records: list[dict[str, object]] = load_json_file(file_path=input_file, data_type=list[dict[str, object]])

        partial_responses: list[str] = _extract_partial_responses(response_records=response_records, allow_direct_json=allow_direct_json)

        output_file: Path = _build_output_file_path(input_file=input_file, output_directory=output_directory, input_suffix=input_suffix, output_suffix=output_suffix)

        save_json_file(file_path=output_file, data=partial_responses)

        output_files.append(output_file)

        print(f"Saved {len(partial_responses)} valid partial FSM responses: {output_file}")

    return output_files





"""

"""
# parse partial response strings into FSM objects.
def parse_partial_fsms(partial_responses: list[str], allow_direct_json: bool = True) -> list[dict[str, object]]:
    # init the partial FSM list.
    partial_fsms: list[dict[str, object]] = []

    for partial_response in partial_responses:
        parsed_response: object | None = parse_json_from_responses_include_markdown(response=partial_response, allow_direct_json=allow_direct_json)

        # ignore None, invalid JSON text, lists, and other invalid structures.
        if not isinstance(parsed_response, dict):
            continue

        partial_fsms.append(parsed_response)

    return partial_fsms




"""
process combination responses
"""
# extract the final FSM from one Ollama combination response.
def extract_final_fsm_from_response(combination_response: dict[str, object], allow_direct_json: bool = True) -> dict[str, object] | None:
    response_value: object = combination_response.get("response")

    # ignore a missing response or a response that is not a string.
    if not isinstance(response_value, str):
        return None

    parsed_response: object | None = parse_json_from_responses_include_markdown(response=response_value, allow_direct_json=allow_direct_json)

    # invalid JSON, lists, strings, and other structures are not valid FSM objects.
    if not isinstance(parsed_response, dict):
        return None

    return parsed_response