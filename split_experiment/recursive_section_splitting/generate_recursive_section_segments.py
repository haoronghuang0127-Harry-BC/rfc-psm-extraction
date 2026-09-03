import re

from pathlib import Path
from typing import Final

import tiktoken

from config.paths import RECURSIVE_SECTION_SPLITTING_MANIFESTS_DIR, RECURSIVE_SECTION_SPLITTING_SEGMENTS_DIR
from config.protocol.protocol_util import get_all_protocol_files, get_protocol_file

from rfc.rfc_io import load_rfc_segments
from rfc.rfc_service import get_rfc_segment_values
from rfc.rfc_types import RfcSegment

from split_experiment.command_line import read_command_line_to_value
from split_experiment.types import RecursiveSectionSplittingManifest, SplitExperimentArguments

from utils.files_util import save_json_file


# fixed tokenizer used by every protocol and model.
TOKENIZER_NAME: Final[str] = "cl100k_base"

# maximum number of tokens in one segment.
MAXIMUM_TOKENS_PER_SEGMENT: Final[int] = 5000

# no overlap is used between adjacent segments.
OVERLAP_TOKENS: Final[int] = 0

# match a numbered RFC subsection heading.
SECTION_HEADING_PATTERN: Final[re.Pattern[str]] = re.compile(r"^(\s*)((?:\d+|[A-Z])(?:\.\d+)+)\.?\s+(\S.*)$")


# count tokens with the fixed experiment tokenizer.
def _count_tokens(text: str) -> int:
    token_encoding = tiktoken.get_encoding(TOKENIZER_NAME)

    token_count: int = len(token_encoding.encode(text))

    return token_count


# normalize a top-level or appendix section number.
def _normalize_section_number(section_number: str) -> str:
    normalized_number: str = section_number.strip()

    if normalized_number.lower().startswith("appendix "):
        normalized_number = normalized_number[9:]

    normalized_number = normalized_number.rstrip(".")

    return normalized_number


# return the depth of one section number.
def _get_section_depth(section_number: str) -> int:
    normalized_number: str = _normalize_section_number(section_number=section_number)
    section_depth: int = len(normalized_number.split("."))

    return section_depth


# select the longest increasing sequence of child section numbers.
def _select_ordered_child_headings(heading_candidates: list[tuple[int, int, str, str]]) -> list[tuple[int, str, str]]:
    if not heading_candidates:
        return []

    sequence_lengths: list[int] = [1] * len(heading_candidates)
    previous_indexes: list[int] = [-1] * len(heading_candidates)

    for current_index, current_candidate in enumerate(heading_candidates):
        current_child_number: int = int(current_candidate[2].split(".")[-1])

        for previous_index in range(current_index):
            previous_candidate = heading_candidates[previous_index]
            previous_child_number: int = int(previous_candidate[2].split(".")[-1])

            if previous_child_number < current_child_number and sequence_lengths[previous_index] + 1 > sequence_lengths[current_index]:
                sequence_lengths[current_index] = sequence_lengths[previous_index] + 1
                previous_indexes[current_index] = previous_index

    final_index: int = max(range(len(heading_candidates)), key=lambda index: sequence_lengths[index])
    selected_candidates: list[tuple[int, str, str]] = []

    while final_index >= 0:
        heading_index, _indentation, child_number, child_name = heading_candidates[final_index]

        selected_candidates.append((heading_index, child_number, child_name))
        final_index = previous_indexes[final_index]

    selected_candidates.reverse()

    return selected_candidates


# find immediate child section headings in one segment.
def _find_child_section_headings(section_number: str, section_text: str) -> list[tuple[int, str, str]]:
    parent_number: str = _normalize_section_number(section_number=section_number)
    child_depth: int = _get_section_depth(section_number=parent_number) + 1

    heading_candidates: list[tuple[int, int, str, str]] = []
    character_index: int = 0

    for line in section_text.splitlines(keepends=True):
        heading_match = SECTION_HEADING_PATTERN.match(line.rstrip("\r\n"))

        if heading_match is not None:
            indentation_text, child_number, child_name = heading_match.groups()

            if child_number.startswith(f"{parent_number}.") and _get_section_depth(section_number=child_number) == child_depth:
                heading_candidates.append((character_index, len(indentation_text), child_number, child_name.strip()))

        character_index += len(line)

    if not heading_candidates:
        return []

    minimum_indentation: int = min(candidate[1] for candidate in heading_candidates)
    minimum_indentation_candidates: list[tuple[int, int, str, str]] = []

    for heading_index, indentation, child_number, child_name in heading_candidates:
        if indentation != minimum_indentation:
            continue

        minimum_indentation_candidates.append((heading_index, indentation, child_number, child_name))

    child_headings: list[tuple[int, str, str]] = _select_ordered_child_headings(heading_candidates=minimum_indentation_candidates)

    return child_headings


# build one child segment with its complete section path.
def _build_child_segment(parent_segment: RfcSegment, child_number: str, child_name: str, child_text: str) -> RfcSegment:
    parent_tag: str = parent_segment.get("tag", "")
    child_tag: str = f"{parent_tag} > Section {child_number} {child_name}"

    child_segment: RfcSegment = {
        "section_number": child_number,
        "section_name": child_name,
        "tag": child_tag,
        "content": child_text,
    }

    return child_segment


# recursively split one segment only when it exceeds 5000 tokens.
def _split_segment_recursively(segment: RfcSegment) -> tuple[list[RfcSegment], int]:
    section_text: str = segment.get("content", "")

    if _count_tokens(text=section_text) <= MAXIMUM_TOKENS_PER_SEGMENT:
        return [segment], 0

    section_number: str = segment.get("section_number", "")
    child_headings: list[tuple[int, str, str]] = _find_child_section_headings(section_number=section_number, section_text=section_text)

    if not child_headings:
        return [segment], 0

    direct_segments: list[RfcSegment] = []
    first_child_index: int = child_headings[0][0]
    parent_text: str = section_text[:first_child_index]

    for index, (child_index, child_number, child_name) in enumerate(child_headings):
        if index + 1 < len(child_headings):
            next_child_index: int = child_headings[index + 1][0]
        else:
            next_child_index = len(section_text)

        child_text: str = section_text[child_index:next_child_index]

        if index == 0 and parent_text.strip() and _count_tokens(text=parent_text + child_text) <= MAXIMUM_TOKENS_PER_SEGMENT:
            child_text = parent_text + child_text

        child_segment: RfcSegment = _build_child_segment(parent_segment=segment, child_number=child_number, child_name=child_name, child_text=child_text)

        direct_segments.append(child_segment)

    first_child_text: str = direct_segments[0].get("content", "")

    if parent_text.strip() and not first_child_text.startswith(parent_text):
        parent_segment: RfcSegment = dict(segment)
        parent_segment["content"] = parent_text
        direct_segments.insert(0, parent_segment)

    final_segments: list[RfcSegment] = []
    split_segment_count: int = 1

    for direct_segment in direct_segments:
        if direct_segment.get("section_number", "") == segment.get("section_number", ""):
            final_segments.append(direct_segment)
            continue

        recursive_segments, recursive_split_count = _split_segment_recursively(segment=direct_segment)

        final_segments.extend(recursive_segments)
        split_segment_count += recursive_split_count

    return final_segments, split_segment_count


# save the recursive section segments for one protocol.
def _save_recursive_section_segments(protocol: str, recursive_section_segments: list[RfcSegment]) -> Path:
    output_file: Path = RECURSIVE_SECTION_SPLITTING_SEGMENTS_DIR / f"{protocol}_recursive_section_segments.json"

    save_json_file(file_path=output_file, data=recursive_section_segments)

    print(f"Saved recursive section segments: {output_file}")

    return output_file


# save the recursive section splitting manifest for one protocol.
def _save_recursive_section_splitting_manifest(protocol: str, source_file: Path, original_segment_count: int, original_over_limit_count: int, split_segment_count: int, recursive_section_segments: list[RfcSegment], output_file: Path) -> Path:
    remaining_over_limit_sections: list[str] = []

    for segment in recursive_section_segments:
        section_text: str = segment.get("content", "")

        if _count_tokens(text=section_text) > MAXIMUM_TOKENS_PER_SEGMENT:
            remaining_over_limit_sections.append(segment.get("tag", ""))

    manifest: RecursiveSectionSplittingManifest = {
        "condition": "recursive_section_splitting",
        "protocol": protocol,
        "tokenizer": TOKENIZER_NAME,
        "maximum_tokens_per_segment": MAXIMUM_TOKENS_PER_SEGMENT,
        "overlap_tokens": OVERLAP_TOKENS,
        "source_file": str(source_file),
        "original_segment_count": original_segment_count,
        "original_over_limit_count": original_over_limit_count,
        "split_segment_count": split_segment_count,
        "final_segment_count": len(recursive_section_segments),
        "remaining_over_limit_count": len(remaining_over_limit_sections),
        "remaining_over_limit_sections": remaining_over_limit_sections,
        "output_file": str(output_file),
    }

    manifest_file: Path = RECURSIVE_SECTION_SPLITTING_MANIFESTS_DIR / f"{protocol}_recursive_section_splitting_manifest.json"

    save_json_file(file_path=manifest_file, data=manifest)

    print(f"Saved recursive section splitting manifest: {manifest_file}")

    return manifest_file


# generate recursive section segments for the selected protocols.
def generate_recursive_section_segments(protocol: str) -> dict[str, list[RfcSegment]]:
    protocol_files: dict[str, Path] = {}

    # get the selected protocol files.
    if protocol == "all":
        protocol_files = get_all_protocol_files()
    else:
        protocol_files = {
            protocol: get_protocol_file(protocol=protocol),
        }

    all_recursive_section_segments: dict[str, list[RfcSegment]] = {}

    for protocol_name, protocol_file in protocol_files.items():
        rfc_segments: list[RfcSegment] = load_rfc_segments(file_path=protocol_file)
        recursive_section_segments: list[RfcSegment] = []
        original_over_limit_count: int = 0
        split_segment_count: int = 0

        for segment in rfc_segments:
            section_text: str = segment.get("content", "")

            if _count_tokens(text=section_text) > MAXIMUM_TOKENS_PER_SEGMENT:
                original_over_limit_count += 1

            final_segments, segment_split_count = _split_segment_recursively(segment=segment)

            recursive_section_segments.extend(final_segments)
            split_segment_count += segment_split_count

        output_file: Path = _save_recursive_section_segments(protocol=protocol_name, recursive_section_segments=recursive_section_segments)

        _save_recursive_section_splitting_manifest(protocol=protocol_name, source_file=protocol_file, original_segment_count=len(rfc_segments), original_over_limit_count=original_over_limit_count, split_segment_count=split_segment_count, recursive_section_segments=recursive_section_segments, output_file=output_file)

        all_recursive_section_segments[protocol_name] = recursive_section_segments

        print(f"Built {len(recursive_section_segments)} recursive section segments for {protocol_name} from {len(rfc_segments)} original segments.")

    return all_recursive_section_segments


def main() -> None:
    arguments: SplitExperimentArguments = read_command_line_to_value()

    all_recursive_section_segments: dict[str, list[RfcSegment]] = generate_recursive_section_segments(protocol=arguments["protocol"])

    print(f"Completed recursive section splitting. Saved segments for {len(all_recursive_section_segments)} protocols.")


if __name__ == "__main__":
    main()
