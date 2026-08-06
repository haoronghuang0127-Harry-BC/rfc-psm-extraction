"""
command line setting
"""

import argparse
from pathlib import Path

from config.models.model_names import ModelName
from config.models.model_types import ProfileName
from config.ollama_settings import ConnectionMode
from config.output_formats import OutputFormatName
from config.protocol.protocol_util import get_all_protocol_files

from ..prompt.prompt_types import InputVersion
from ..selection.selection_rules import ScoringMethod
from .experiment_types import ExperimentArguments

# convert max_section to number
def _max_sections_to_int(value: str) -> int | None:
    value: str = value.strip().lower()

    # all means select all sections
    if value == "all":
        return None

    try:
        max_sections: int = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("max-sections must be a positive number or 'all'.") from error

    if max_sections <= 0:
        raise argparse.ArgumentTypeError("max-sections must be greater than zero.")

    return max_sections


# Read the experiment settings from the command line.
def read_command_line_to_value() -> ExperimentArguments:
    # get all the protocl files
    protocol_files: dict[str, Path] = get_all_protocol_files()

    # get all the protocol name
    protocol_names: list[str] = list(protocol_files.keys())

    # get the name of scoring methods
    # choose the scoring mehtods, which is using different way to score the section
    scoring_method_names: list[str] = [scoring_method.value for scoring_method in ScoringMethod]

    # get the input version
    # the input version is have high, high + medium, all, to get different number of part sections to llm
    input_version_names: list[str] = [input_version.value for input_version in InputVersion]

    # get the llm model name
    model_names: list[str] = [model_name.value for model_name in ModelName]

    # set the profile name default
    # set the different parameter for the ollama
    profile_names: list[str] = ["default"]
    # all the profile name
    for profile_name in ProfileName:
        profile_names.append(profile_name.value)

    # get the connection mode names
    # set the connection mode for ollama, include local and remote
    connection_mode_names: list[str] = [connection_mode.value for connection_mode in ConnectionMode]

    # get output format names
    # using different output format for the llm output, also setting different prompt for different output format
    output_format_names: list[str] = [output_format.value for output_format in OutputFormatName]

    # set the parser to get the command line argument
    parser: argparse.ArgumentParser = argparse.ArgumentParser(description="Run the Method 1 LLM extraction experiment.")

    # Select the protocol
    parser.add_argument("--protocol", type=str.upper, choices=protocol_names, default="POP3",
                        help="Protocol name. Default: POP3.")

    # Select the section scoring method
    parser.add_argument("--scoring-method", choices=scoring_method_names, default=ScoringMethod.KEYWORD_DENSITY.value,
                        help="Section scoring method. Default: keyword_density.")

    # Select the prepared RFC input version
    parser.add_argument("--input-version", choices=input_version_names, default=InputVersion.HIGH_PRIORITY.value,
                        help="RFC input version. Default: hybrid_high.")

    # Select the Ollama model
    parser.add_argument("--model", choices=model_names, default=ModelName.QWEN3_5_9B.value,
                        help="Ollama model name. Default: qwen3.5:9b.")
    

    # Select the model parameter profile
    parser.add_argument("--profile", choices=profile_names, default="default",
                        help="Model parameter profile. Use 'default' for the model's default profile.")
    

    # Select the Ollama connection mode
    parser.add_argument("--connection", choices=connection_mode_names, default=ConnectionMode.AUTO.value,
                        help="Ollama connection mode. Default: auto." )

    # Select the model output format.
    parser.add_argument("--output-format", type=str.upper, choices=output_format_names, default=OutputFormatName.F0.value,
                        help="Output format: F0, F1, or F2. Default: F0.")

    # Select the random seed
    parser.add_argument("--seed", type=int, default=42,
                        help="Random seed. Uses the profile seed when omitted.")

    # Select how many sections will be processed
    parser.add_argument("--max-sections", type=_max_sections_to_int, default=1,
                        help="Number of sections to process. Use 'all' to process every section. Default: 1.")

    parsed_arguments: argparse.Namespace = parser.parse_args()

    profile_name_text: str = parsed_arguments.profile

    # setting the profile name
    if profile_name_text == "default":
        selected_profile_name: ProfileName | None = None
    else:
        selected_profile_name = ProfileName(profile_name_text)

    # set the experiment arguments from command line
    experiment_arguments: ExperimentArguments = {
        "protocol": parsed_arguments.protocol,
        "scoring_method": ScoringMethod(parsed_arguments.scoring_method),
        "input_version": InputVersion(parsed_arguments.input_version),
        "model_name": ModelName(parsed_arguments.model),
        "profile_name": selected_profile_name,
        "connection_mode": ConnectionMode(parsed_arguments.connection),
        "output_format_name": OutputFormatName(parsed_arguments.output_format),
        "seed": parsed_arguments.seed,
        "max_sections": (parsed_arguments.max_sections)
    }

    return experiment_arguments
