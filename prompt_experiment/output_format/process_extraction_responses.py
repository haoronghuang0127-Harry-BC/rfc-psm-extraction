from pathlib import Path

from config.paths import PROMPT_EXPERIMENT_ORIGINAL_RESPONSES_DIR, PROMPT_EXPERIMENT_PARTIAL_FSMS_DIR

from research_pipeline.response_processing import process_extraction_response_files


# Process all extraction responses from the output format experiment.
def process_extraction_responses() -> list[Path]:
    output_files: list[Path] = process_extraction_response_files(input_directory=PROMPT_EXPERIMENT_ORIGINAL_RESPONSES_DIR, 
                                                                 output_directory=PROMPT_EXPERIMENT_PARTIAL_FSMS_DIR, 
                                                                 input_pattern="*_extraction_responses.json", 
                                                                 input_suffix="_extraction_responses", 
                                                                 output_suffix="_partial_fsms", 
                                                                 allow_direct_json=True)

    return output_files


def main() -> None:
    output_files: list[Path] = process_extraction_responses()

    print(f"Completed extraction response processing. Saved {len(output_files)} partial FSM files.")


if __name__ == "__main__":
    main()