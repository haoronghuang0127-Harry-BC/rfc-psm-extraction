import csv
import json
from pathlib import Path

from config.output_formats import OutputFormatName
from config.paths import METHOD_1_OUTPUT_DIR
from config.protocol_files import get_all_protocol_files

from method_1_section_selection.prompt.generate_section_prompt import build_section_prompt
from method_1_section_selection.prompt.prompt_types import InputVersion, PromptRecord, PromptSummary
from method_1_section_selection.selection.rfc_segment_io import load_rfc_segments
from method_1_section_selection.selection.section_features import RfcSegment, get_rfc_segment_values
from method_1_section_selection.selection.selection_rules import ScoringMethod

from util.text_statistics import count_words


# save the prompt as a json file
def _save_prompt_records(file_path: Path, prompt_records: list[PromptRecord]) -> None:

    with file_path.open("w", encoding="utf-8") as file:
        json.dump(prompt_records, file, ensure_ascii=False, indent=2)

# get input files
def _get_input_files(protocol: str, scoring_method: ScoringMethod) -> dict[InputVersion, Path]:
    protocol_output_dir: Path = METHOD_1_OUTPUT_DIR / protocol / scoring_method.value

    input_files: dict[InputVersion, Path] = {
        InputVersion.BASELINE_ALL: protocol_output_dir / f"{protocol}_baseline_all_segments.json",
        InputVersion.HIGH_PRIORITY: protocol_output_dir / f"{protocol}_high_priority_segments.json",
        InputVersion.HIGH_MEDIUM_PRIORITY: protocol_output_dir / f"{protocol}_high_medium_segments.json"
    }

    return input_files


def _build_prompt_records(protocol: str, scoring_method: ScoringMethod, input_version: InputVersion, segments_file: Path) -> list[PromptRecord]:

    segments: list[RfcSegment] = load_rfc_segments(segments_file)

    prompt_records: list[PromptRecord] = []

    for index, segment in enumerate(segments, start=1):
        # get RfcSegment values
        section_number, section_name, tag, content = get_rfc_segment_values(segment)

        # Create the basic prompt record.
        prompt_record: PromptRecord = {
            "protocol": protocol,
            "scoring_method": scoring_method,
            "input_version": input_version,
            "section_index": index,
            "section_number": section_number,
            "section_name": section_name,
            "tag": tag,
            "source_file": segments_file.name,
            "section_text": content,
            "prompt_word_count": 0,
            "prompt": "",
        }

        # get the common prompt used by F0, F1, and F2
        prompt: str = build_section_prompt(prompt_record=prompt_record, output_format_name=OutputFormatName.F0)

        # add prompt and its word count.
        prompt_record["prompt"] = prompt
        prompt_record["prompt_word_count"] = count_words(prompt)
        
        prompt_records.append(prompt_record)

    return prompt_records

# save prompt summary in csf file
def _save_prompt_summary(file_path: Path, summaries: list[PromptSummary]) -> None:

    fieldnames: list[str] = ["protocol","scoring_method","input_version","source_file","prompt_count","total_prompt_words","baseline_prompt_words","reduced_prompt_words","word_reduction_percentage","output_file"]

    with file_path.open("w", encoding="utf-8", newline="") as file:

        writer = csv.DictWriter(file,fieldnames=fieldnames)

        writer.writeheader()
        
        for summary in summaries:
            writer.writerow(summary)

# Calculate prompt word count
def _calculate_prompt_word_count(prompt_records: list[PromptRecord]) -> int:
    total_prompt_words: int = 0

    for record in prompt_records:
        total_prompt_words += record["prompt_word_count"]

    return total_prompt_words


# Calculate word reduction compared with the baseline input.
def _add_word_reduction(summaries: list[PromptSummary]) -> None:

    baseline_prompt_words: int = 0

    for summary in summaries:
        if summary["input_version"] == InputVersion.BASELINE_ALL:
            baseline_prompt_words = summary["total_prompt_words"]
            break

    for summary in summaries:
        total_prompt_words: int = summary["total_prompt_words"]
        reduced_prompt_words: int = baseline_prompt_words - total_prompt_words

        if baseline_prompt_words > 0:
            word_reduction_percentage: float = reduced_prompt_words / baseline_prompt_words * 100
        else:
            word_reduction_percentage = 0.0

        summary["baseline_prompt_words"] = baseline_prompt_words
        summary["reduced_prompt_words"] = reduced_prompt_words
        summary["word_reduction_percentage"] = round(word_reduction_percentage, 2)

def _process_input_version(protocol: str, scoring_method: ScoringMethod, input_version: InputVersion, segments_file: Path, prompt_output_dir: Path) -> PromptSummary:

    prompt_records: list[PromptRecord] = _build_prompt_records(protocol, scoring_method, input_version, segments_file)

    output_file: Path = prompt_output_dir / f"{input_version}_prompts.json"

    _save_prompt_records(output_file, prompt_records)

    # get total_prompt_words
    total_prompt_words: int = _calculate_prompt_word_count(prompt_records)

    summary: PromptSummary = {
        "protocol": protocol,
        "scoring_method": scoring_method,
        "input_version": input_version,
        "source_file": segments_file.name,
        "prompt_count": len(prompt_records),
        "total_prompt_words": total_prompt_words,
        "baseline_prompt_words": 0,
        "reduced_prompt_words": 0,
        "word_reduction_percentage": 0.0,
        "output_file": output_file.name,
    }

    return summary


def process_protocol_prompts(protocol: str, scoring_method: ScoringMethod) -> list[PromptSummary]:

    prompt_output_dir: Path = METHOD_1_OUTPUT_DIR / protocol / scoring_method.value / "prompts"

    prompt_output_dir.mkdir(parents=True,exist_ok=True)

    input_files: dict[InputVersion, Path] = _get_input_files(protocol, scoring_method)

    summaries: list[PromptSummary] = []

    for input_version, segments_file in input_files.items():
        summary: PromptSummary = _process_input_version(protocol, scoring_method, input_version, segments_file, prompt_output_dir)

        summaries.append(summary)

    _add_word_reduction(summaries)

    summary_files: Path = prompt_output_dir / "prompt_summary.csv"

    _save_prompt_summary(summary_files, summaries)

    return summaries

# generate prompt for protocols
def main() -> None:
    protocol_files: dict[str, Path] = get_all_protocol_files()

    for protocol in protocol_files:
        for scoring_method in ScoringMethod:
            summaries: list[PromptSummary] = process_protocol_prompts(protocol, scoring_method)

            print(f"\nProtocol: {protocol}")
            print(f"Scoring method: {scoring_method.value}")

            for summary in summaries:
                print(
                    f"{summary['input_version']}: "
                    f"{summary['prompt_count']} prompts, "
                    f"{summary['total_prompt_words']} words"
                )

if __name__ == "__main__":
    main()



