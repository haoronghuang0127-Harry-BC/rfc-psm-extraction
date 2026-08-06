from pathlib import Path

from config.protocol.protocol_util import get_all_protocol_files

from method_1_section_selection.selection.section_features import RfcSegment, SectionFeatures, extract_section_features
from method_1_section_selection.selection.section_scoring import ScoredSection, score_section
from method_1_section_selection.selection.section_selector import RankedSection, SectionSelectionResult, select_sections
from method_1_section_selection.selection.selection_output import save_selection_result
from method_1_section_selection.selection.selection_rules import ScoringMethod

from rfc.rfc_io import load_rfc_segments



# score the rfc segments
def _score_rfc_segments(segments: list[RfcSegment], scoring_method: ScoringMethod) -> list[ScoredSection]:
    scored_sections: list[ScoredSection] = []

    for index, segment in enumerate(segments, start=1):
        # extract information (keyword and word count)
        features: SectionFeatures = extract_section_features(segment=segment, source_index=index)

        # score the section
        scored_section: ScoredSection = score_section(features, scoring_method)

        scored_sections.append(scored_section)

    return scored_sections

# process protocol
def process_protocol(file_path: Path, scoring_method: ScoringMethod) -> SectionSelectionResult:
    # load the rfc sections
    segments: list[RfcSegment] = load_rfc_segments(file_path)

    # scored section
    scored_section: list[ScoredSection] = _score_rfc_segments(segments, scoring_method)

    # rank the section and divide them into different priority levels
    selection_result: SectionSelectionResult = select_sections(scored_section)

    return selection_result

# Print a summary of the section selection result.
def _print_selection_result(protocol_name: str, selection_result: SectionSelectionResult) -> None:

    ranked_sections: list[RankedSection] = selection_result["ranked_sections"]
    high_sections: list[RankedSection] = selection_result["high_sections"]
    medium_sections: list[RankedSection] = selection_result["medium_sections"]
    low_sections: list[RankedSection] = selection_result["low_sections"]

    print(f"\nProtocol: {protocol_name}")
    print(f"Total sections: {len(ranked_sections)}")
    print(f"High-priority sections: {len(high_sections)}")
    print(f"Medium-priority sections: {len(medium_sections)}")
    print(f"Low-priority sections: {len(low_sections)}")

    def _print_priority_sections(title: str, sections: list[RankedSection]) -> None:
        print(f"\n{title}-priority sections:")

        for section in sections:
            section_number: str = section["section_number"]
            section_name: str = section["section_name"]
            score: float = section["score"]

            print(
                f"  Rank {section['rank']}: "
                f"{section_number} {section_name} "
                f"(score: {score})"
            )

    _print_priority_sections("High",high_sections)
    _print_priority_sections("Medium",medium_sections)
    _print_priority_sections("Low",low_sections)

# Print the main result of one protocol.
def _print_protocol_summary(protocol: str, selection_result: SectionSelectionResult, output_files: dict[str, Path]) -> None:

    total_sections: int = len(selection_result["ranked_sections"])

    high_sections: int = len(selection_result["high_sections"])

    medium_sections: int = len(selection_result["medium_sections"])

    low_sections: int = len(selection_result["low_sections"])

    print(f"\nProtocol: {protocol}")
    print(f"Total sections: {total_sections}")
    print(f"High-priority sections: {high_sections}")
    print(f"Medium-priority sections: {medium_sections}")
    print(f"Low-priority sections: {low_sections}")

    print(f"Ranking CSV: {output_files['ranking_csv']}")
    print(f"Baseline JSON: {output_files['baseline_json']}")
    print(f"High JSON: {output_files['high_json']}")
    print(
        "High and medium JSON: "
        f"{output_files['high_medium_json']}"
    )

def main() -> None:
    protocol_files: dict[str, Path] = get_all_protocol_files()

    for protocol, file_path in protocol_files.items():
        for scoring_method in ScoringMethod:
            selection_result: SectionSelectionResult = process_protocol(file_path, scoring_method)

            #_print_selection_result(protocol, selection_result)

            # save the selection result
            output_files: dict[str, Path] = save_selection_result(protocol, scoring_method, selection_result)

            print(f"Scoring method: {scoring_method.value}")
            _print_protocol_summary(protocol,selection_result,output_files)


if __name__ == "__main__":
    main()
