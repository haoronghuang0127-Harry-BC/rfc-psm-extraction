from pathlib import Path
from time import perf_counter

from config.model_profiles import ModelProfile, get_model_profile
from config.models.model_names import ModelName
from config.models.model_registry import get_model_config
from config.models.model_types import ModelConfig, ProfileName
from config.ollama_settings import ConnectionMode, OllamaConnection, get_ollama_connection
from config.output_formats import OutputFormat, OutputFormatName, get_output_format

from method_1_section_selection.llm_experiment.experiment_io import get_output_dir, get_prompt_file, load_prompts, load_section_results, save_json, select_prompt_records
from method_1_section_selection.llm_experiment.experiment_records import build_experiment_environment, build_experiment_summary
from method_1_section_selection.llm_experiment.experiment_types import ExperimentArguments, ExperimentEnvironment, ExperimentResult, ExperimentSummary, MergeRunResult, ParseStatus, SectionRunResult
from method_1_section_selection.llm_experiment.extraction_service import build_failed_section_result, send_merge_prompt, send_section_prompt
from method_1_section_selection.prompt.generate_section_prompt import build_section_prompt
from method_1_section_selection.prompt.prompt_types import InputVersion, PromptRecord
from method_1_section_selection.selection.selection_rules import ScoringMethod


# get selected profile name
def _get_select_profile_name(model_config: ModelConfig, selected_profile_name: ProfileName | None) -> ProfileName:

    if selected_profile_name is None:
        profile_name: ProfileName = model_config["default_profile"]
    else:
        profile_name = selected_profile_name

    if profile_name not in model_config["supported_profiles"]:
        raise ValueError(f"Profile {profile_name} is not supported by model {model_config['name']}.")

    return profile_name

# set the seed from command line
# return the new profile
def _apply_seed(model_profile: ModelProfile, selected_seed: int | None) -> ModelProfile:
    # copy a new options
    options: dict[str, int | float] = model_profile["options"].copy()

    # update the seed 
    if selected_seed is not None:
        options["seed"] = selected_seed

    # create a new model profile (update the seed)
    updated_profile: ModelProfile = {
        "description": model_profile["description"],
        "options": options,
        "think": model_profile["think"],
    }

    return updated_profile

# build a dict using index mapping section result, which can easy to find the section uisng index
def _build_section_result_mapping_index(section_results: list[SectionRunResult]) -> dict[int, SectionRunResult]:
    section_result_mapping_index: dict[int, SectionRunResult] = {}

    for section_result in section_results:
        index: int = section_result["section_index"]
        section_result_mapping_index[index] = section_result

    return section_result_mapping_index

def _check_section_result(prompt: PromptRecord, prompt_text: str, section_result: SectionRunResult) -> bool:
    # if this section result request error, need to process
    if section_result.get("request_error",""):
        return False

    # if this section result do not finish, need to process
    if section_result["parse_status"] not in (ParseStatus.VALID_PSM, ParseStatus.NO_PSM_FOUND):
        return False

    # if change the profile, make the section choice different, need to process
    if section_result["section_number"] != prompt["section_number"]:
        return False

    # if change the file name or not the same file, need to process
    if section_result["source_file"] != prompt["source_file"]:
        return False

    # if chang the prompt or not the same prompt, need to process
    if section_result["prompt"] != prompt_text:
        return False


    return True

# return the section result with correct order
def _get_ordered_section_results(selected_records: list[PromptRecord], section_results_mapping_index: dict[int, SectionRunResult]) -> list[SectionRunResult]:
    ordered_results: list[SectionRunResult] = []

    for prompt in selected_records:
        section_index: int = prompt["section_index"]

        if section_index in section_results_mapping_index:
            ordered_results.append(section_results_mapping_index[section_index])

    return ordered_results

def run_experiment(arguments: ExperimentArguments) -> ExperimentResult:

    #start time
    start_time: float = perf_counter()

    # get the value from command line arguments
    protocol: str = arguments["protocol"]
    scoring_method: ScoringMethod = arguments["scoring_method"]
    input_version: InputVersion = arguments["input_version"]
    model_name: ModelName = arguments["model_name"]
    selected_profile_name: ProfileName | None = arguments["profile_name"]
    connection_mode: ConnectionMode = arguments["connection_mode"]
    output_format_name: OutputFormatName = arguments["output_format_name"]
    selected_seed: int | None = arguments["seed"]
    max_sections: int | None = arguments["max_sections"]


    # get the model config
    model_config: ModelConfig = get_model_config(model_name=model_name)

    # get the model name
    profile_name: ProfileName = _get_select_profile_name(model_config=model_config, selected_profile_name=selected_profile_name)

    # get the model profile
    model_profile: ModelProfile = get_model_profile(profile_name=profile_name)
    # set the seed from command line, because the each profiles have their default seed
    model_profile = _apply_seed(model_profile, selected_seed)
    # get the actual seed used by the experiment
    seed: int = int(model_profile["options"]["seed"])

    # Get the selected output format.
    output_format: OutputFormat = get_output_format(output_format_name=output_format_name)
    
    # connect to the ollama server
    connection: OllamaConnection = get_ollama_connection(connection_mode=connection_mode)

    # get prompt file
    prompt_file: Path = get_prompt_file(protocol=protocol, scoring_method=scoring_method, input_version=input_version)
    # get prompt
    prompts: list[PromptRecord] = load_prompts(file_path=prompt_file)

    # sometime do a small test not using all the section, so this can choose one or more section to do a small test (also can choose all the sections)
    selected_records: list[PromptRecord] = select_prompt_records(prompt_records=prompts, max_sections=max_sections)




    # create the experiment output directory
    output_dir: Path = get_output_dir(protocol=protocol, scoring_method=scoring_method, input_version=input_version, model_name=model_name, 
                                      profile_name=profile_name, output_format_name=output_format_name, seed=seed, max_sections=max_sections)
    output_dir.mkdir(parents=True,exist_ok=True)

    # print the experiment information
    print(f"Protocol: {protocol}")
    print(f"Scoring method: {scoring_method.value}")
    print(f"Input version: {input_version.value}")
    print(f"Model: {model_name.value}")
    print(f"Profile: {profile_name.value}")
    print(f"Output format: {output_format_name.value}")
    print(f"Seed: {seed}")
    print(f"Connection: {connection['connection_name'].value}")
    print(f"Sections: {len(selected_records)}")


    # set the section result file
    section_results_file: Path = output_dir / "section_results.json"

    # read the section results saved before (some time the program will stop cause Internet or other error, read the finished result to continue)
    section_results: list[SectionRunResult] = load_section_results(section_results_file)

    section_results_mapping_index: dict[int, SectionRunResult] = _build_section_result_mapping_index(section_results)




    # process each selected sections
    for prompt in selected_records:
        # get the section index
        section_index: int = prompt["section_index"]

        # build the section prompt
        prompt_text: str = build_section_prompt(prompt_record=prompt, output_format_name=output_format_name)

        # if some results are saved in the file, we can skip them
        previous_result: SectionRunResult | None = section_results_mapping_index.get(section_index)

        # check the previous can skip
        if previous_result is not None and _check_section_result(prompt=prompt, prompt_text=prompt_text, section_result=previous_result):
            print(f"\nSkipping completed section: {prompt['section_number']} {prompt['section_name']}")
            continue

        print(f"\nProcessing section: {prompt['section_number']} {prompt['section_name']}")

        try:
            section_result: SectionRunResult = send_section_prompt(prompt=prompt, prompt_text=prompt_text, model_config=model_config, 
                                                                  model_profile=model_profile, connection=connection, output_format=output_format)
        except Exception as error:
            section_result = build_failed_section_result(prompt=prompt, prompt_text=prompt_text, error=error)

        # add the result in mapping
        section_results_mapping_index[section_index] = section_result

        # sorted the section results
        section_results = _get_ordered_section_results(selected_records=selected_records, section_results_mapping_index=section_results_mapping_index)

        # save the result
        save_json(file_path=section_results_file, data=section_results)

        if section_result["request_error"]:
            print(f"Request failed: {section_result['request_error']}")
        else:
            print(f"Parse status: {section_result['parse_status']}")


    section_results = _get_ordered_section_results(selected_records=selected_records, section_results_mapping_index=section_results_mapping_index)
    

    # calculate the success and fail result
    successful_section_results: list[SectionRunResult] = []
    failed_section_results: list[SectionRunResult] = []

    for result in section_results:
        if result["parse_status"] in (ParseStatus.VALID_PSM, ParseStatus.NO_PSM_FOUND):
            successful_section_results.append(result)
        else:
            failed_section_results.append(result)

    print(f"Completed sections: {len(successful_section_results)}")
    print(f"Failed sections: {len(failed_section_results)}")
    print("\nCombining partial PSM outputs.")

    # Combine the partial section results.
    merge_result: MergeRunResult = send_merge_prompt(section_results=successful_section_results, model_config=model_config, model_profile=model_profile, 
                                                            connection=connection, output_format=output_format)


    # end time
    end_time: float = perf_counter()
    # spend time
    experiment_spend_time: float = end_time - start_time

    # build the summary of the experiment
    summary: ExperimentSummary = build_experiment_summary(section_results=section_results, experiment_running_time_seconds=experiment_spend_time)

    # get the context
    requested_context: int = int(model_profile["options"]["num_ctx"])
    environment: ExperimentEnvironment = build_experiment_environment(connection=connection, model_name=model_name, requested_context=requested_context)

    experiment_result: ExperimentResult = {
            "protocol": protocol,
            "scoring_method": scoring_method,
            "input_version": input_version,
            "model_name": model_name,
            "profile_name": profile_name,
            "profile_description": model_profile["description"],
            "options": model_profile["options"],
            "think": model_profile["think"],
            "requested_connection_mode": connection_mode,
            "actual_connection_mode": connection["connection_name"],
            "output_format_name": output_format_name,
            "output_format_description": output_format["description"],
            "seed": seed,
            "max_sections": max_sections,
            "prompt_file": str(prompt_file),
            "section_count": len(section_results),
            "successful_section_count": len(successful_section_results),
            "failed_section_count": len(failed_section_results),
            "summary": summary,
            "environment": environment,
            "sections": section_results,
            "merge": merge_result,
        }
        
    # Save the complete experiment information.
    save_json(file_path=(output_dir / "experiment_result.json"), data=experiment_result)

    # Save the main experiment numbers separately.
    save_json(file_path=(output_dir / "run_summary.json"), data=summary)

    # Save the Ollama and model environment separately.
    save_json(file_path=(output_dir / "experiment_environment.json"), data=environment)

    # Save the final parsed PSM separately.
    save_json(file_path=(output_dir / "final_fsm.json"), data=merge_result["parsed_output"])

    print(f"Final parse status: {merge_result['parse_status']}")

    print(f"Results saved in: {output_dir}")


    return experiment_result
        


    
