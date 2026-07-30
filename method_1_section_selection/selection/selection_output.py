import csv
import json
from pathlib import Path

from config.paths import METHOD_1_OUTPUT_DIR

from method_1_section_selection.selection.section_features import RfcSegment
from method_1_section_selection.selection.section_selector import RankedSection, SectionSelectionResult
from method_1_section_selection.selection.selection_rules import ScoringMethod


# RankedSection -> RfcSegment
def _convert_ranked_section_to_rfc_segment(section: RankedSection) -> RfcSegment:

    segment: RfcSegment = {
        "section_number": section["section_number"],
        "section_name": section["section_name"],
        "tag": section["tag"],
        "content": section["content"],
    }

    return segment

# RankedSection[] -> RfcSegment[]
def _convert_ranked_section_list_to_rfc_segment_list(sections: list[RankedSection]) -> list[RfcSegment]:
    segments: list[RfcSegment] = []

    for section in sections:
        segment: RfcSegment = _convert_ranked_section_to_rfc_segment(section)

        segments.append(segment)


    return segments


# save selected sections as a json file
def _save_segments_json(file_path: Path, sections: list[RankedSection]) -> None:

    segments: list[RfcSegment] = _convert_ranked_section_list_to_rfc_segment_list(sections)

    with file_path.open("w", encoding="utf-8") as file:
        json.dump(segments, file, ensure_ascii=False, indent=2)

# Save the main ranking information as a CSV file.
def _save_ranking_csv(file_path: Path, protocol: str, sections: list[RankedSection]) -> None:
    # csv column name
    fieldnames: list[str] = [
        "protocol", "source_index", "rank", "priority_level", "section_number", "section_name", "tag", "scoring_method", "score", "keyword_score", "keyword_density_score", "title_bonus", "word_count",
    ]

    with file_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        writer.writeheader()

        for section in sections:
            writer.writerow({
                "protocol": protocol,
                "source_index": section["source_index"],
                "rank": section["rank"],
                "priority_level": section["priority_level"],
                "section_number": section["section_number"],
                "section_name": section["section_name"],
                "tag": section["tag"],
                "scoring_method": section["scoring_method"],
                "score": section["score"],
                "keyword_score": section["keyword_score"],
                "keyword_density_score": section["keyword_density_score"],
                "title_bonus": section["title_bonus"],
                "word_count": section["word_count"]
            })


def _sorted_sections(sections: list[RankedSection]) -> list[RankedSection]:
    return sorted(sections, key=lambda section: section["source_index"])

# save the selection result
def save_selection_result(protocol: str, scoring_method: ScoringMethod, selection_result: SectionSelectionResult) -> dict[str, Path]:
    # Create the output folder when it does not exist.
    protocol_output_dir: Path = METHOD_1_OUTPUT_DIR / protocol / scoring_method.value
    protocol_output_dir.mkdir(parents=True,exist_ok=True)

    ranked_sections: list[RankedSection] = selection_result["ranked_sections"]
    original_order_all_sections: list[RankedSection] = _sorted_sections(ranked_sections)

    high_sections: list[RankedSection] = selection_result["high_sections"]
    original_order_high_section: list[RankedSection] = _sorted_sections(high_sections)

    medium_sections: list[RankedSection] = selection_result["medium_sections"]

    # high + medium
    original_order_high_medium_sections: list[RankedSection] = _sorted_sections(high_sections + medium_sections)


    # save file path
    ranking_csv: Path = (protocol_output_dir / f"{protocol}_hybrid_section_routing.csv")

    baseline_json: Path = (protocol_output_dir / f"{protocol}_baseline_all_segments.json")

    high_json: Path = (protocol_output_dir / f"{protocol}_high_priority_segments.json")

    high_medium_json: Path = (protocol_output_dir / f"{protocol}_high_medium_segments.json")


    # save the file
    _save_ranking_csv(ranking_csv, protocol, ranked_sections)

    _save_segments_json(baseline_json, original_order_all_sections)

    _save_segments_json(high_json, original_order_high_section)

    _save_segments_json(high_medium_json, original_order_high_medium_sections)

    output_files: dict[str, Path] = {
        "ranking_csv": ranking_csv,
        "baseline_json": baseline_json,
        "high_json": high_json,
        "high_medium_json": high_medium_json
    }

    return output_files


