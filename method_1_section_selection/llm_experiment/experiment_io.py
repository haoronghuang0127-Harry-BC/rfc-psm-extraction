import json
from pathlib import Path

from config.models.model_names import ModelName
from config.models.model_types import ProfileName
from config.paths import METHOD_1_OUTPUT_DIR
from config.output_formats import OutputFormatName

from method_1_section_selection.llm_experiment.experiment_types import SectionRunResult
from method_1_section_selection.prompt.prompt_types import InputVersion, PromptRecord
from method_1_section_selection.selection.selection_rules import ScoringMethod


# Load generated prompts from a JSON file.
def load_prompts(file_path: Path) -> list[PromptRecord]:

    with file_path.open("r", encoding="utf-8") as file:
        prompts: list[PromptRecord] = json.load(file)


    return prompts

# Load the section results saved by an earlier run.
def load_section_results(file_path: Path) -> list[SectionRunResult]:

    if not file_path.exists():
        return []

    with file_path.open("r", encoding="utf-8") as file:
        section_results: list[SectionRunResult] = json.load(file)

    return section_results


# Load one JSON object when the file exists.
def load_json_object(file_path: Path) -> dict[str, object]:

    if not file_path.exists():
        return {}

    with file_path.open("r", encoding="utf-8") as file:
        data: object = json.load(file)

    if not isinstance(data, dict):
        return {}

    return data

def save_json(file_path: Path, data: object) -> None:

    file_path.parent.mkdir(parents=True, exist_ok=True)

    temporary_file_path: Path = file_path.with_suffix(file_path.suffix + ".tmp")

    with temporary_file_path.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)

    temporary_file_path.replace(file_path)

def get_prompt_file(protocol: str, scoring_method: ScoringMethod, input_version: InputVersion) -> Path:

    prompt_file: Path = METHOD_1_OUTPUT_DIR / protocol / scoring_method.value / "prompts" / f"{input_version.value}_prompts.json"

    if not prompt_file.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_file}")

    return prompt_file


# Return the output directory for the experiment.
def get_output_dir(protocol: str, scoring_method: ScoringMethod, input_version: InputVersion, model_name: ModelName, profile_name: ProfileName, output_format_name: OutputFormatName, seed: int, max_sections: int | None) -> Path:

    safe_model_name: str = (model_name.value.replace(":","_").replace("/","_"))

    if max_sections is None:
        run_size: str = "all_sections"
    else:
        run_size = f"first_{max_sections}_sections"

    output_dir: Path = METHOD_1_OUTPUT_DIR / protocol / scoring_method.value / "llm_runs" / input_version.value / safe_model_name / profile_name.value / output_format_name.value / f"seed_{seed}" / run_size

    return output_dir

# Select how many prompt records will be processed.
def select_prompt_records(prompt_records: list[PromptRecord], max_sections: int | None) -> list[PromptRecord]:

    if max_sections is None:
        return prompt_records

    selected_records: list[PromptRecord] = prompt_records[:max_sections]

    return selected_records
