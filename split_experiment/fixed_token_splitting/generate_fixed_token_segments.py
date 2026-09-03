from pathlib import Path
from typing import Final

import tiktoken

from config.paths import FIXED_TOKEN_SPLITTING_MANIFESTS_DIR, FIXED_TOKEN_SPLITTING_SEGMENTS_DIR
from config.protocol.protocol_util import get_all_protocol_files, get_protocol_file

from rfc.rfc_io import load_rfc_segments
from rfc.rfc_service import get_rfc_segment_values
from rfc.rfc_types import RfcSegment

from split_experiment.command_line import read_command_line_to_value
from split_experiment.types import FixedTokenSplittingManifest, SplitExperimentArguments

from utils.files_util import save_json_file


# fixed tokenizer used by every protocol and model.
TOKENIZER_NAME: Final[str] = "cl100k_base"

# maximum number of tokens in one segment.
MAXIMUM_TOKENS_PER_SEGMENT: Final[int] = 5000

# no overlap is used between adjacent segments.
OVERLAP_TOKENS: Final[int] = 0


# build the complete RFC text from the original PSMBench segments.
def _build_whole_rfc_text(rfc_segments: list[RfcSegment]) -> str:
    section_texts: list[str] = []

    for segment in rfc_segments:
        _section_number, _section_name, section_title, section_text = get_rfc_segment_values(segment=segment)

        whole_section_text: str = f"{section_title}\n{section_text}"

        section_texts.append(whole_section_text)

    whole_rfc_text: str = "\n\n".join(section_texts)

    return whole_rfc_text


# split one complete RFC into fixed 5000-token segments.
def _build_fixed_token_segments(whole_rfc_text: str) -> tuple[list[RfcSegment], int]:
    token_encoding = tiktoken.get_encoding(TOKENIZER_NAME)
    token_ids: list[int] = token_encoding.encode(whole_rfc_text)

    fixed_token_segments: list[RfcSegment] = []

    for start_index in range(0, len(token_ids), MAXIMUM_TOKENS_PER_SEGMENT):
        end_index: int = start_index + MAXIMUM_TOKENS_PER_SEGMENT
        segment_token_ids: list[int] = token_ids[start_index:end_index]
        segment_text: str = token_encoding.decode(segment_token_ids)
        segment_index: int = len(fixed_token_segments) + 1
        segment_title: str = f"Fixed Token Segment {segment_index}"

        fixed_token_segment: RfcSegment = {
            "section_number": str(segment_index),
            "section_name": segment_title,
            "tag": segment_title,
            "content": segment_text,
        }

        fixed_token_segments.append(fixed_token_segment)

    return fixed_token_segments, len(token_ids)


# save the fixed token segments for one protocol.
def _save_fixed_token_segments(protocol: str, fixed_token_segments: list[RfcSegment]) -> Path:
    output_file: Path = FIXED_TOKEN_SPLITTING_SEGMENTS_DIR / f"{protocol}_fixed_token_segments.json"

    save_json_file(file_path=output_file, data=fixed_token_segments)

    print(f"Saved fixed token segments: {output_file}")

    return output_file


# save the fixed token splitting manifest for one protocol.
def _save_fixed_token_splitting_manifest(protocol: str, source_file: Path, original_segment_count: int, source_token_count: int, fixed_segment_count: int, output_file: Path) -> Path:
    manifest: FixedTokenSplittingManifest = {
        "condition": "fixed_token_splitting",
        "protocol": protocol,
        "tokenizer": TOKENIZER_NAME,
        "maximum_tokens_per_segment": MAXIMUM_TOKENS_PER_SEGMENT,
        "overlap_tokens": OVERLAP_TOKENS,
        "source_file": str(source_file),
        "original_segment_count": original_segment_count,
        "source_token_count": source_token_count,
        "fixed_segment_count": fixed_segment_count,
        "output_file": str(output_file),
    }

    manifest_file: Path = FIXED_TOKEN_SPLITTING_MANIFESTS_DIR / f"{protocol}_fixed_token_splitting_manifest.json"

    save_json_file(file_path=manifest_file, data=manifest)

    print(f"Saved fixed token splitting manifest: {manifest_file}")

    return manifest_file


# generate fixed token segments for the selected protocols.
def generate_fixed_token_segments(protocol: str) -> dict[str, list[RfcSegment]]:
    protocol_files: dict[str, Path] = {}

    # get the selected protocol files.
    if protocol == "all":
        protocol_files = get_all_protocol_files()
    else:
        protocol_files = {
            protocol: get_protocol_file(protocol=protocol),
        }

    all_fixed_token_segments: dict[str, list[RfcSegment]] = {}

    for protocol_name, protocol_file in protocol_files.items():
        rfc_segments: list[RfcSegment] = load_rfc_segments(file_path=protocol_file)
        whole_rfc_text: str = _build_whole_rfc_text(rfc_segments=rfc_segments)
        fixed_token_segments, source_token_count = _build_fixed_token_segments(whole_rfc_text=whole_rfc_text)
        output_file: Path = _save_fixed_token_segments(protocol=protocol_name, fixed_token_segments=fixed_token_segments)

        _save_fixed_token_splitting_manifest(protocol=protocol_name, source_file=protocol_file, original_segment_count=len(rfc_segments), source_token_count=source_token_count, fixed_segment_count=len(fixed_token_segments), output_file=output_file)

        all_fixed_token_segments[protocol_name] = fixed_token_segments

        print(f"Built {len(fixed_token_segments)} fixed token segments for {protocol_name}.")

    return all_fixed_token_segments


def main() -> None:
    arguments: SplitExperimentArguments = read_command_line_to_value()

    all_fixed_token_segments: dict[str, list[RfcSegment]] = generate_fixed_token_segments(protocol=arguments["protocol"])

    print(f"Completed fixed token splitting. Saved segments for {len(all_fixed_token_segments)} protocols.")


if __name__ == "__main__":
    main()
