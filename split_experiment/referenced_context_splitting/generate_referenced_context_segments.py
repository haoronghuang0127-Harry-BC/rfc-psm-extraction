import re

from collections import Counter
from pathlib import Path
from typing import Final

import tiktoken

from config.paths import REFERENCED_CONTEXT_SPLITTING_MANIFESTS_DIR, REFERENCED_CONTEXT_SPLITTING_SEGMENTS_DIR, RECURSIVE_SECTION_SPLITTING_SEGMENTS_DIR
from config.protocol.protocol_util import get_all_protocol_files, get_protocol_file

from rfc.rfc_io import load_rfc_segments
from rfc.rfc_types import RfcSegment

from split_experiment.command_line import read_command_line_to_value
from split_experiment.types import ReferencedContextSegment, ReferencedContextSplittingManifest, SplitExperimentArguments

from utils.files_util import save_json_file


# fixed tokenizer used by every protocol and model.
TOKENIZER_NAME: Final[str] = "cl100k_base"

# match numbered headings and appendix headings, including top-level sections.
SECTION_HEADING_PATTERN: Final[re.Pattern[str]] = re.compile(r"^([ \t]*)((?:(?i:appendix)[ \t]+)?((?:\d+|[A-Z])(?:\.\d+)*|[IVXLCDM]+)\.?)[ \t]+(\S.*)$")

# match one or more explicitly written section numbers.
SECTION_REFERENCE_PATTERN: Final[re.Pattern[str]] = re.compile(r"\bsections?\s+(\d+(?:\.\d+)*(?:(?:\s*,\s*(?:and\s+)?|\s+(?:and|or)\s+)\d+(?:\.\d+)*)*)", re.IGNORECASE)

# match one explicitly written appendix number.
APPENDIX_REFERENCE_PATTERN: Final[re.Pattern[str]] = re.compile(r"\b(?i:appendix)\s+([A-Z]+(?:\.\d+)*)")

# match a list of explicitly written appendix numbers.
APPENDICES_REFERENCE_PATTERN: Final[re.Pattern[str]] = re.compile(r"\b(?i:appendices)\s+([A-Z]+(?:\.\d+)*(?:(?:\s*,\s*(?:and\s+)?|\s+(?:and|or)\s+)[A-Z]+(?:\.\d+)*)*)")

# match an individual section or appendix number.
REFERENCE_NUMBER_PATTERN: Final[re.Pattern[str]] = re.compile(r"\d+(?:\.\d+)*|[A-Z]+(?:\.\d+)*")


# count tokens with the fixed experiment tokenizer.
def _count_tokens(text: str) -> int:
    token_encoding = tiktoken.get_encoding(TOKENIZER_NAME)

    token_count: int = len(token_encoding.encode(text))

    return token_count


# normalize a section or appendix number.
def _normalize_section_number(section_number: str) -> str:
    normalized_number: str = section_number.strip()

    if normalized_number.lower().startswith("appendix "):
        normalized_number = normalized_number[9:]

    normalized_number = normalized_number.rstrip(".").upper()

    return normalized_number


# return the depth of one section number.
def _get_section_depth(section_number: str) -> int:
    normalized_number: str = _normalize_section_number(section_number=section_number)
    section_depth: int = len(normalized_number.split("."))

    return section_depth


# find real section headings using the indentation of each heading depth.
def _find_section_headings(section_text: str) -> list[tuple[int, str, str]]:
    heading_candidates: list[tuple[int, int, str, str]] = []
    indentation_by_depth: dict[int, int] = {}
    character_index: int = 0

    for line in section_text.splitlines(keepends=True):
        heading_match: re.Match[str] | None = SECTION_HEADING_PATTERN.match(line.rstrip("\r\n"))

        if heading_match is not None:
            indentation_text, heading_label, section_number, section_name = heading_match.groups()
            normalized_number: str = _normalize_section_number(section_number=section_number)
            indentation: int = len(indentation_text.expandtabs())
            section_depth: int = _get_section_depth(section_number=normalized_number)

            # An ordinary sentence starting with "A" is not an appendix heading.
            is_plain_letter: bool = normalized_number.isalpha() and not heading_label.lower().startswith("appendix ") and not heading_label.endswith(".")
            is_contents_entry: bool = re.search(r"\.{3,}", section_name) is not None

            if not is_plain_letter and not is_contents_entry:
                heading_candidates.append((character_index, indentation, normalized_number, section_name.strip()))
                indentation_by_depth[section_depth] = min(indentation, indentation_by_depth.get(section_depth, indentation))

        character_index += len(line)

    # FTP indents child headings progressively; most other RFCs use column zero.
    child_indentation: int = indentation_by_depth.get(2, 0)
    indentation_step: int = max(0, indentation_by_depth.get(3, child_indentation) - child_indentation)
    indentation_by_depth[1] = max(0, child_indentation - indentation_step)

    section_headings: list[tuple[int, str, str]] = []

    for heading_index, indentation, section_number, section_name in heading_candidates:
        section_depth = _get_section_depth(section_number=section_number)

        if indentation == indentation_by_depth[section_depth]:
            section_headings.append((heading_index, section_number, section_name))

    return section_headings


# build an index containing every available section in one RFC.
def _build_section_index(rfc_segments: list[RfcSegment]) -> dict[str, RfcSegment]:
    source_parts: list[str] = []
    original_headings: list[tuple[int, str, str]] = []
    original_sections: dict[str, RfcSegment] = {}
    character_index: int = 0

    for segment in rfc_segments:
        section_number: str = _normalize_section_number(section_number=segment.get("section_number", ""))
        section_text: str = segment.get("content", "")
        section_name: str = segment.get("section_name", "")

        # Unnumbered metadata still marks a boundary, but is not a reference target.
        if re.fullmatch(r"(?:\d+|[A-Z])(?:\.\d+)*|[IVXLCDM]+", section_number) is None:
            section_number = ""

        original_headings.append((character_index, section_number, section_name))

        if section_number:
            original_sections[section_number] = segment

        source_parts.append(section_text)
        character_index += len(section_text) + 1

    # Scan the whole source, including sections hidden inside another original block.
    source_text: str = "\n".join(source_parts)
    section_headings: list[tuple[int, str, str]] = _find_section_headings(section_text=source_text)

    for original_index, original_number, original_name in original_headings:
        has_written_heading: bool = any(number == original_number and heading_index >= original_index and not source_text[original_index:heading_index].strip() for heading_index, number, _name in section_headings)

        # Original PSMBench blocks often store their title only in metadata.
        if not has_written_heading:
            section_headings.append((original_index, original_number, original_name))

    # A parent without introductory text starts at the same position as its first child.
    section_headings.sort(key=lambda heading: (heading[0], _get_section_depth(section_number=heading[1])))
    heading_counts: Counter[str] = Counter(number for _index, number, _name in section_headings)
    original_boundaries: set[int] = {original_index for original_index, _number, _name in original_headings}
    section_index: dict[str, RfcSegment] = {}

    for index, (heading_index, section_number, section_name) in enumerate(section_headings):
        # Repeated real heading numbers are ambiguous; do not silently choose one.
        if not section_number or heading_counts[section_number] > 1:
            continue

        section_depth: int = _get_section_depth(section_number=section_number)
        end_index: int = len(source_text)

        for next_heading_index, next_number, _next_name in section_headings[index + 1:]:
            if _get_section_depth(section_number=next_number) <= section_depth:
                end_index = next_heading_index
                break

        # Remove only the separator added between original blocks, preserving source whitespace.
        if end_index in original_boundaries:
            end_index -= 1

        indexed_segment: RfcSegment = {
            "section_number": section_number,
            "section_name": section_name,
            "tag": f"Section {section_number} {section_name}",
            "content": source_text[heading_index:end_index],
        }

        if section_number in original_sections:
            indexed_segment["tag"] = original_sections[section_number].get("tag", indexed_segment["tag"])

        section_index[section_number] = indexed_segment

    return section_index


# skip references to another RFC or an external standard.
def _is_external_reference(section_text: str, match: re.Match[str], current_rfc: str) -> bool:
    before_reference: str = re.sub(r"\s+", " ", section_text[max(0, match.start() - 400):match.start()])
    after_reference: str = re.sub(r"\s+", " ", section_text[match.end():match.end() + 200])

    # Include the owner following a range such as Sections 9.3-9.7 of RFC7231.
    after_reference = re.sub(r"^\s*(?:[-–—]|through\b|to\b)\s*\d+(?:\.\d+)*", "", after_reference, flags=re.IGNORECASE)

    if re.match(r"\s*(?:of|in)\s+(?:this|the present)\s+(?:document|specification|RFC)\b", after_reference, re.IGNORECASE):
        return False

    suffix_match: re.Match[str] | None = re.match(r"\s*(?:of|in)\s+(?:(?!\b(?:Section|Appendix|this)\b)[^;()]){0,80}?(?:\bRFC\s*(\d+)|\[([^\]]+)\])", after_reference, re.IGNORECASE)
    prefix_match: re.Match[str] | None = re.search(r"(?:\bRFC\s*(\d+)(?:\s*\[[^\]]+\])?|\[([^\]]+)\])(?:['’]s)?[\s,(]*(?:in\s*)?$", before_reference, re.IGNORECASE)

    # ABNF cites its notation standard; the following section can still be local.
    if suffix_match is None and re.search(r"\bABNF\s+\[RFC\d+\]\s+in\s*$", before_reference, re.IGNORECASE):
        return False

    owner_match: re.Match[str] | None = suffix_match or prefix_match

    if owner_match is not None:
        rfc_number, citation = owner_match.groups()

        if rfc_number is None:
            citation_rfc: re.Match[str] | None = re.fullmatch(r"RFC\s*(\d+)", citation, re.IGNORECASE)

            if citation_rfc is None:
                return citation.lower() != "deprecated"

            rfc_number = citation_rfc.group(1)

        return int(rfc_number) != int(current_rfc)

    citation_match: re.Match[str] | None = re.match(r"\s*\[([^\]]+)\]", after_reference)

    if citation_match is not None:
        citation: str = citation_match.group(1)
        citation_rfc = re.fullmatch(r"RFC\s*(\d+)", citation, re.IGNORECASE)

        if citation_rfc is not None:
            return int(citation_rfc.group(1)) != int(current_rfc)

        return citation.lower() != "deprecated"

    # A named document without an RFC number is still outside the current RFC.
    if re.match(r"\s*(?:of|in)\s+(?:the\s+)?(?:MQTT\b|ISO\b)", after_reference, re.IGNORECASE):
        return True

    # A following clause can refer back to the same external ISO standard.
    if re.search(r"\[ISO\.8601\.2000\][^.;]*following\s*$", before_reference, re.IGNORECASE):
        return True

    # Section numbers inside an explicitly attributed RFC quotation belong to that RFC.
    line_start: int = section_text.rfind("\n", 0, match.start()) + 1

    if section_text[line_start:match.start()].lstrip().startswith("|"):
        quote_prefix: str = section_text[:line_start]
        quote_prefix = re.sub(r"(?:[ \t]*\|[^\n]*\n)+$", "", quote_prefix)
        quote_owner: re.Match[str] | None = re.search(r"\bRFC\s*(\d+)[^\n]*:\s*$", quote_prefix, re.IGNORECASE)

        if quote_owner is not None:
            return int(quote_owner.group(1)) != int(current_rfc)

    return False


# find direct same-RFC section references in one segment.
def _find_section_references(section_text: str, current_rfc: str) -> list[str]:
    reference_matches: list[tuple[int, re.Match[str]]] = []

    for match in SECTION_REFERENCE_PATTERN.finditer(section_text):
        reference_matches.append((match.start(), match))

    for match in APPENDIX_REFERENCE_PATTERN.finditer(section_text):
        reference_matches.append((match.start(), match))

    for match in APPENDICES_REFERENCE_PATTERN.finditer(section_text):
        reference_matches.append((match.start(), match))

    reference_matches.sort(key=lambda item: item[0])

    section_references: list[str] = []

    for _match_index, match in reference_matches:
        if _is_external_reference(section_text=section_text, match=match, current_rfc=current_rfc):
            continue

        matched_numbers: list[str] = REFERENCE_NUMBER_PATTERN.findall(match.group(1))

        for matched_number in matched_numbers:
            normalized_number: str = _normalize_section_number(section_number=matched_number)

            if normalized_number not in section_references:
                section_references.append(normalized_number)

    return section_references


# build the referenced context text appended to one S2 segment.
def _build_referenced_context_text(referenced_segments: list[RfcSegment]) -> str:
    referenced_section_texts: list[str] = []

    for referenced_segment in referenced_segments:
        section_title: str = referenced_segment.get("tag", "")
        section_text: str = referenced_segment.get("content", "")
        referenced_section_text: str = f"{section_title}\n{section_text}"

        referenced_section_texts.append(referenced_section_text)

    referenced_context_text: str = "\n\n".join(referenced_section_texts)

    return referenced_context_text


# add direct referenced section context to one S2 segment.
def _build_referenced_context_segment(segment: RfcSegment, section_index: dict[str, RfcSegment], current_rfc: str) -> ReferencedContextSegment:
    section_number: str = _normalize_section_number(section_number=segment.get("section_number", ""))
    section_text: str = segment.get("content", "")
    detected_references: list[str] = _find_section_references(section_text=section_text, current_rfc=current_rfc)

    referenced_segments: list[RfcSegment] = []
    referenced_sections: list[str] = []
    unresolved_references: list[str] = []

    for referenced_number in detected_references:
        referenced_segment: RfcSegment | None = section_index.get(referenced_number)

        if referenced_segment is None:
            unresolved_references.append(referenced_number)
            continue

        referenced_text: str = referenced_segment.get("content", "")

        if referenced_number == section_number or referenced_text.strip() in section_text:
            continue

        referenced_segments.append(referenced_segment)
        referenced_sections.append(referenced_number)

    final_section_text: str = section_text

    if referenced_segments:
        referenced_context_text: str = _build_referenced_context_text(referenced_segments=referenced_segments)
        final_section_text = f"{section_text}\n\n<referenced_context>\n{referenced_context_text}\n</referenced_context>"

    referenced_context_segment: ReferencedContextSegment = {
        "section_number": segment.get("section_number", ""),
        "section_name": segment.get("section_name", ""),
        "tag": segment.get("tag", ""),
        "content": final_section_text,
        "referenced_sections": referenced_sections,
        "unresolved_references": unresolved_references,
    }

    return referenced_context_segment


# save the referenced context segments for one protocol.
def _save_referenced_context_segments(protocol: str, referenced_context_segments: list[ReferencedContextSegment]) -> Path:
    output_file: Path = REFERENCED_CONTEXT_SPLITTING_SEGMENTS_DIR / f"{protocol}_referenced_context_segments.json"

    save_json_file(file_path=output_file, data=referenced_context_segments)

    print(f"Saved referenced context segments: {output_file}")

    return output_file


# save the referenced context splitting manifest for one protocol.
def _save_referenced_context_splitting_manifest(protocol: str, source_file: Path, source_recursive_segments_file: Path, referenced_context_segments: list[ReferencedContextSegment], output_file: Path) -> Path:
    segments_with_referenced_context_count: int = 0
    resolved_reference_count: int = 0
    unresolved_reference_count: int = 0
    maximum_final_segment_token_count: int = 0

    for segment in referenced_context_segments:
        referenced_sections: list[str] = segment.get("referenced_sections", [])
        unresolved_references: list[str] = segment.get("unresolved_references", [])

        if referenced_sections:
            segments_with_referenced_context_count += 1

        resolved_reference_count += len(referenced_sections)
        unresolved_reference_count += len(unresolved_references)

        segment_token_count: int = _count_tokens(text=segment.get("content", ""))
        maximum_final_segment_token_count = max(maximum_final_segment_token_count, segment_token_count)

    manifest: ReferencedContextSplittingManifest = {
        "condition": "referenced_context_splitting",
        "protocol": protocol,
        "tokenizer": TOKENIZER_NAME,
        "base_condition": "recursive_section_splitting",
        "source_file": str(source_file),
        "source_recursive_segments_file": str(source_recursive_segments_file),
        "base_segment_count": len(referenced_context_segments),
        "final_segment_count": len(referenced_context_segments),
        "segments_with_referenced_context_count": segments_with_referenced_context_count,
        "resolved_reference_count": resolved_reference_count,
        "unresolved_reference_count": unresolved_reference_count,
        "maximum_final_segment_token_count": maximum_final_segment_token_count,
        "output_file": str(output_file),
    }

    manifest_file: Path = REFERENCED_CONTEXT_SPLITTING_MANIFESTS_DIR / f"{protocol}_referenced_context_splitting_manifest.json"

    save_json_file(file_path=manifest_file, data=manifest)

    print(f"Saved referenced context splitting manifest: {manifest_file}")

    return manifest_file


# generate referenced context segments for the selected protocols.
def generate_referenced_context_segments(protocol: str) -> dict[str, list[ReferencedContextSegment]]:
    protocol_files: dict[str, Path] = {}

    # get the selected protocol files.
    if protocol == "all":
        protocol_files = get_all_protocol_files()
    else:
        protocol_files = {
            protocol: get_protocol_file(protocol=protocol),
        }

    all_referenced_context_segments: dict[str, list[ReferencedContextSegment]] = {}

    for protocol_name, protocol_file in protocol_files.items():
        recursive_segments_file: Path = RECURSIVE_SECTION_SPLITTING_SEGMENTS_DIR / f"{protocol_name}_recursive_section_segments.json"

        if not recursive_segments_file.is_file():
            raise FileNotFoundError(f"Could not find recursive section segments: {recursive_segments_file}")

        rfc_segments: list[RfcSegment] = load_rfc_segments(file_path=protocol_file)
        recursive_section_segments: list[RfcSegment] = load_rfc_segments(file_path=recursive_segments_file)
        current_rfc: str = protocol_file.stem.removeprefix("rfc").split("_")[0]
        section_index: dict[str, RfcSegment] = _build_section_index(rfc_segments=rfc_segments)
        referenced_context_segments: list[ReferencedContextSegment] = []

        for segment in recursive_section_segments:
            referenced_context_segment: ReferencedContextSegment = _build_referenced_context_segment(segment=segment, section_index=section_index, current_rfc=current_rfc)

            referenced_context_segments.append(referenced_context_segment)

        output_file: Path = _save_referenced_context_segments(protocol=protocol_name, referenced_context_segments=referenced_context_segments)

        _save_referenced_context_splitting_manifest(protocol=protocol_name, source_file=protocol_file, source_recursive_segments_file=recursive_segments_file, referenced_context_segments=referenced_context_segments, output_file=output_file)

        all_referenced_context_segments[protocol_name] = referenced_context_segments

        print(f"Built {len(referenced_context_segments)} referenced context segments for {protocol_name}.")

    return all_referenced_context_segments


def main() -> None:
    arguments: SplitExperimentArguments = read_command_line_to_value()

    all_referenced_context_segments: dict[str, list[ReferencedContextSegment]] = generate_referenced_context_segments(protocol=arguments["protocol"])

    print(f"Completed referenced context splitting. Saved segments for {len(all_referenced_context_segments)} protocols.")


if __name__ == "__main__":
    main()
