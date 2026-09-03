from pathlib import Path
from typing import Final


# the Path of path.py
CURRENT_FILE: Final[Path] = Path(__file__).resolve()

# the path of util folder
CONFIG_FOLDER: Final[Path] = CURRENT_FILE.parent

# the root path
PROJECT_FOLDER_DIR: Final[Path] = CONFIG_FOLDER.parent

# PSMBench Project Path
PSMBENCH_DIR: Final[Path] = PROJECT_FOLDER_DIR / "RFC_PSM_Benchmark-main" 
# PSMBech Output data path
PSMBENCH_OUTPUT_DIR: Final[Path] = PROJECT_FOLDER_DIR / "output_data"
# PSMBench original evaluation OutputPath
PSMBENCH_ORIGINAL_EVALUATION_OUTPUT_DIR: Final[Path] = PSMBENCH_OUTPUT_DIR / "PSMBench_original_evaluation_results"
# PSMBench new evaluation OutputPath
PSMBENCH_NEW_EVALUATION_OUTPUT_DIR: Final[Path] = PSMBENCH_OUTPUT_DIR / "PSMBench_new_evaluation_results"
# PSMBench fsm Path
PSMBENCH_FSM_DIR: Final[Path] = PSMBENCH_DIR / "fsm"



# PSMBench loacl baseline path
PSMBENCH_LOCAL_BASELINE_DIR: Final[Path] = PROJECT_FOLDER_DIR / "psmbench_local_baseline"
# PSMBench loacl baseline output path
PSMBENCH_LOCAL_BASELINE_OUTPUT_DIR: Final[Path] = PSMBENCH_LOCAL_BASELINE_DIR / "outputs"
# PSMBench local baseline extraction prompts directory
PSMBENCH_LOCAL_BASELINE_PROMPTS_DIR: Final[Path] = PSMBENCH_LOCAL_BASELINE_OUTPUT_DIR / "prompts"
# PSMBench local baseline extraction prompts file
PSMBENCH_LOCAL_BASELINE_EXTRACTION_PROMPTS: Final[Path] = PSMBENCH_LOCAL_BASELINE_PROMPTS_DIR / "extraction_prompts.json"
# PSMBench local baseline responses directory
PSMBENCH_LOCAL_BASELINE_RESPONSES_DIR: Final[Path] = PSMBENCH_LOCAL_BASELINE_OUTPUT_DIR / "responses"
# PSMBench local baseline original responses directory
PSMBENCH_LOCAL_BASELINE_ORIGINAL_RESPONSES_DIR: Final[Path] = PSMBENCH_LOCAL_BASELINE_RESPONSES_DIR / "original"
# PSMBench local baseline partial FSM responses directory.
PSMBENCH_LOCAL_BASELINE_PARTIAL_FSMS_DIR: Final[Path] = PSMBENCH_LOCAL_BASELINE_RESPONSES_DIR / "partial_fsms"
# PSMBench local baseline combination prompts file.
PSMBENCH_LOCAL_BASELINE_COMBINATION_PROMPTS: Final[Path] = PSMBENCH_LOCAL_BASELINE_PROMPTS_DIR / "combination_prompts.json"
# PSMBench local baseline combination response directory.
PSMBENCH_LOCAL_BASELINE_COMBINATION_RESPONSE_DIR: Final[Path] = PSMBENCH_LOCAL_BASELINE_RESPONSES_DIR / "combination_response"
# PSMBench local baseline final FSM directory.
PSMBENCH_LOCAL_BASELINE_FINAL_FSMS_DIR: Final[Path] = PSMBENCH_LOCAL_BASELINE_OUTPUT_DIR / "final_fsms"
# PSMBench local baseline evaluations directory.
EVALUATION_OUTPUT_DIR: Final[Path] = PSMBENCH_LOCAL_BASELINE_OUTPUT_DIR / "evaluations"






"""
prompt experiment
"""
# prompt experiment root directory
PROMPT_EXPERIMENT_DIR: Final[Path] = PROJECT_FOLDER_DIR / "prompt_experiment"
# prompt experiment output directory
PROMPT_EXPERIMENT_OUTPUT_DIR: Final[Path] = PROMPT_EXPERIMENT_DIR / "outputs"
# prompt files directory
PROMPT_EXPERIMENT_PROMPTS_DIR: Final[Path] = PROMPT_EXPERIMENT_OUTPUT_DIR / "prompts"
# all response files directory
PROMPT_EXPERIMENT_RESPONSES_DIR: Final[Path] = PROMPT_EXPERIMENT_OUTPUT_DIR / "responses"
# original ollama extraction responses directory
PROMPT_EXPERIMENT_ORIGINAL_RESPONSES_DIR: Final[Path] = PROMPT_EXPERIMENT_RESPONSES_DIR / "original"
# extracted response text directory
PROMPT_EXPERIMENT_PARTIAL_RESPONSES_DIR: Final[Path] = PROMPT_EXPERIMENT_RESPONSES_DIR / "partial_responses"
# parsed partial FSM files directory
PROMPT_EXPERIMENT_PARTIAL_FSMS_DIR: Final[Path] = PROMPT_EXPERIMENT_RESPONSES_DIR / "partial_fsms"
# original ollama combination responses directory
PROMPT_EXPERIMENT_COMBINATION_RESPONSES_DIR: Final[Path] = PROMPT_EXPERIMENT_RESPONSES_DIR / "combination_response"
# final fsm files directory
PROMPT_EXPERIMENT_FINAL_FSMS_DIR: Final[Path] = PROMPT_EXPERIMENT_OUTPUT_DIR / "final_fsms"
# evaluation csv files directory
PROMPT_EXPERIMENT_EVALUATIONS_DIR: Final[Path] = PROMPT_EXPERIMENT_OUTPUT_DIR / "evaluations"
# experiment manifest file
PROMPT_EXPERIMENT_MANIFEST_FILE: Final[Path] = PROMPT_EXPERIMENT_OUTPUT_DIR / "experiment_manifest.json"




"""
split experiment
"""
# split experiment root directory
SPLIT_EXPERIMENT_DIR: Final[Path] = PROJECT_FOLDER_DIR / "split_experiment"
# split experiment output directory
SPLIT_EXPERIMENT_OUTPUT_DIR: Final[Path] = SPLIT_EXPERIMENT_DIR / "outputs"
# whole document reference output directory
WHOLE_DOCUMENT_REFERENCE_OUTPUT_DIR: Final[Path] = SPLIT_EXPERIMENT_OUTPUT_DIR / "whole_document_reference"
# whole RFC document directory
WHOLE_DOCUMENT_REFERENCE_DOCUMENTS_DIR: Final[Path] = WHOLE_DOCUMENT_REFERENCE_OUTPUT_DIR / "documents"
# whole RFC document manifest directory
WHOLE_DOCUMENT_REFERENCE_MANIFESTS_DIR: Final[Path] = WHOLE_DOCUMENT_REFERENCE_OUTPUT_DIR / "manifests"
# whole document reference prompt directory
WHOLE_DOCUMENT_REFERENCE_PROMPTS_DIR: Final[Path] = WHOLE_DOCUMENT_REFERENCE_OUTPUT_DIR / "prompts"
# whole document reference response directory
WHOLE_DOCUMENT_REFERENCE_RESPONSES_DIR: Final[Path] = WHOLE_DOCUMENT_REFERENCE_OUTPUT_DIR / "responses"
# whole document reference original response directory
WHOLE_DOCUMENT_REFERENCE_ORIGINAL_RESPONSES_DIR: Final[Path] = WHOLE_DOCUMENT_REFERENCE_RESPONSES_DIR / "original"
# whole document reference final FSM directory
WHOLE_DOCUMENT_REFERENCE_FINAL_FSMS_DIR: Final[Path] = WHOLE_DOCUMENT_REFERENCE_OUTPUT_DIR / "final_fsms"
# whole document reference evaluation directory
WHOLE_DOCUMENT_REFERENCE_EVALUATIONS_DIR: Final[Path] = WHOLE_DOCUMENT_REFERENCE_OUTPUT_DIR / "evaluations"
# whole document reference context exclusion file
WHOLE_DOCUMENT_REFERENCE_CONTEXT_EXCLUSIONS_FILE: Final[Path] = WHOLE_DOCUMENT_REFERENCE_MANIFESTS_DIR / "context_exclusions.json"

# fixed token splitting output directory
FIXED_TOKEN_SPLITTING_OUTPUT_DIR: Final[Path] = SPLIT_EXPERIMENT_OUTPUT_DIR / "fixed_token_splitting"
# fixed token segment directory
FIXED_TOKEN_SPLITTING_SEGMENTS_DIR: Final[Path] = FIXED_TOKEN_SPLITTING_OUTPUT_DIR / "segments"
# fixed token splitting manifest directory
FIXED_TOKEN_SPLITTING_MANIFESTS_DIR: Final[Path] = FIXED_TOKEN_SPLITTING_OUTPUT_DIR / "manifests"
# fixed token splitting prompt directory
FIXED_TOKEN_SPLITTING_PROMPTS_DIR: Final[Path] = FIXED_TOKEN_SPLITTING_OUTPUT_DIR / "prompts"
# fixed token splitting response directory
FIXED_TOKEN_SPLITTING_RESPONSES_DIR: Final[Path] = FIXED_TOKEN_SPLITTING_OUTPUT_DIR / "responses"
# fixed token splitting original response directory
FIXED_TOKEN_SPLITTING_ORIGINAL_RESPONSES_DIR: Final[Path] = FIXED_TOKEN_SPLITTING_RESPONSES_DIR / "original"
# fixed token splitting partial FSM directory
FIXED_TOKEN_SPLITTING_PARTIAL_FSMS_DIR: Final[Path] = FIXED_TOKEN_SPLITTING_RESPONSES_DIR / "partial_fsms"
# fixed token splitting combination response directory
FIXED_TOKEN_SPLITTING_COMBINATION_RESPONSES_DIR: Final[Path] = FIXED_TOKEN_SPLITTING_RESPONSES_DIR / "combination_response"
# fixed token splitting final FSM directory
FIXED_TOKEN_SPLITTING_FINAL_FSMS_DIR: Final[Path] = FIXED_TOKEN_SPLITTING_OUTPUT_DIR / "final_fsms"
# fixed token splitting evaluation directory
FIXED_TOKEN_SPLITTING_EVALUATIONS_DIR: Final[Path] = FIXED_TOKEN_SPLITTING_OUTPUT_DIR / "evaluations"

# recursive section splitting output directory
RECURSIVE_SECTION_SPLITTING_OUTPUT_DIR: Final[Path] = SPLIT_EXPERIMENT_OUTPUT_DIR / "recursive_section_splitting"
# recursive section segment directory
RECURSIVE_SECTION_SPLITTING_SEGMENTS_DIR: Final[Path] = RECURSIVE_SECTION_SPLITTING_OUTPUT_DIR / "segments"
# recursive section splitting manifest directory
RECURSIVE_SECTION_SPLITTING_MANIFESTS_DIR: Final[Path] = RECURSIVE_SECTION_SPLITTING_OUTPUT_DIR / "manifests"
# recursive section splitting prompt directory
RECURSIVE_SECTION_SPLITTING_PROMPTS_DIR: Final[Path] = RECURSIVE_SECTION_SPLITTING_OUTPUT_DIR / "prompts"
# recursive section splitting response directory
RECURSIVE_SECTION_SPLITTING_RESPONSES_DIR: Final[Path] = RECURSIVE_SECTION_SPLITTING_OUTPUT_DIR / "responses"
# recursive section splitting original response directory
RECURSIVE_SECTION_SPLITTING_ORIGINAL_RESPONSES_DIR: Final[Path] = RECURSIVE_SECTION_SPLITTING_RESPONSES_DIR / "original"
# recursive section splitting partial FSM directory
RECURSIVE_SECTION_SPLITTING_PARTIAL_FSMS_DIR: Final[Path] = RECURSIVE_SECTION_SPLITTING_RESPONSES_DIR / "partial_fsms"
# recursive section splitting combination response directory
RECURSIVE_SECTION_SPLITTING_COMBINATION_RESPONSES_DIR: Final[Path] = RECURSIVE_SECTION_SPLITTING_RESPONSES_DIR / "combination_response"
# recursive section splitting final FSM directory
RECURSIVE_SECTION_SPLITTING_FINAL_FSMS_DIR: Final[Path] = RECURSIVE_SECTION_SPLITTING_OUTPUT_DIR / "final_fsms"
# recursive section splitting evaluation directory
RECURSIVE_SECTION_SPLITTING_EVALUATIONS_DIR: Final[Path] = RECURSIVE_SECTION_SPLITTING_OUTPUT_DIR / "evaluations"



