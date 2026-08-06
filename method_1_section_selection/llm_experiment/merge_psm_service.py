import json
from typing import Final

from config.model_profiles import ModelProfile
from config.models.model_types import ModelConfig
from config.ollama_settings import OllamaConnection
from config.output_formats import OutputFormat

from method_1_section_selection.llm_experiment.experiment_ollama_request import send_prompt_to_model
from method_1_section_selection.llm_experiment.experiment_types import ModelCallResult, ParseStatus
from method_1_section_selection.prompt.generate_merge_prompt import build_merge_prompt

# set the context more bigger
MERGE_NUM_PREDICT: Final[int] = 32768
# set the ratio for the context (80%)
MERGE_CONTEXT_USE_RATIO: Final[float] = 0.80
MERGE_MAX_TIMES: Final[int] = 2
MERGE_MAX_LEVELS: Final[int] = 10

# get the prompt limit
# some model will have the context window limit
def _get_merge_prompt_limit(merge_profile: ModelProfile) -> int:
    # get the context from the profile
    num_ctx: int = int(merge_profile["options"]["num_ctx"]) 
    # set 80% for safe
    prompt_limit: int = int(num_ctx * MERGE_CONTEXT_USE_RATIO)

    return prompt_limit

# calculate the token count
def _calculate_token_count(text: str) -> int:

    length: int = len(text.encode("utf-8"))

    token_count:int = (length + 1) // 2

    return max(1, token_count)

def _send_merge_prompt(merge_prompt: str, model_config: ModelConfig, merge_profile: ModelProfile, connection: OllamaConnection, output_format: OutputFormat) -> tuple[ModelCallResult, int]:
    merge_counter: int = 0

    for time in range(1, MERGE_MAX_TIMES + 1):
        # set the merge prompt to model
        model_result: ModelCallResult = send_prompt_to_model(prompt_text=merge_prompt, model_config=model_config, model_profile=merge_profile, 
                                                             connection=connection, request_format=output_format["merge_request_format"],
                                                             output_format_name=output_format["name"], is_merge_prompt=True)

        # counter + 1
        merge_counter += 1

        # check if the response is not fail return
        if model_result["parse_status"] not in (ParseStatus.EMPTY_RESPONSE, ParseStatus.INVALID_JSON):
            return model_result, merge_counter

        # try again
        if time < MERGE_MAX_TIMES:
            print("Merge output was empty or invalid. Retrying once.")

    return model_result, merge_counter

# Build a merge result that could not be completed safely.
def _build_merge_not_run_result(message: str) -> ModelCallResult:

    model_result: ModelCallResult = {
        "ollama_response": {},
        "response_text": "",
        "thinking_text": "",
        "parsed_output": None,
        "parse_status": ParseStatus.MERGE_NOT_RUN,
        "request_error": message,
    }

    return model_result

# split the partial output in to batches
def _split_partial_outputs(partial_outputs: list[str], prompt_limit: int, output_format: OutputFormat) -> list[list[str]]:

    batches: list[list[str]] = []
    current_batch: list[str] = []


    for partial_output in partial_outputs:
        # add the output in the batch
        temp_batch: list[str] = current_batch + [partial_output]
        # get the merge_prompt
        merge_prompt: str = build_merge_prompt(partial_outputs=temp_batch, output_format_name=output_format["name"])
        # calculate the token count
        predict_token_count: int = _calculate_token_count(merge_prompt)

        if current_batch and predict_token_count > prompt_limit:
            batches.append(current_batch)
            current_batch = [partial_output]
        else:
            current_batch = temp_batch

    # if current_batch is not empty, add the last batch in the batches
    if current_batch:
        batches.append(current_batch)

    return batches
    


def merge_partial_outputs(partial_outputs: list[str], model_config: ModelConfig, merge_profile: ModelProfile, connection: OllamaConnection, output_format: OutputFormat) -> tuple[ModelCallResult, str, int, bool, int]:
    # get the prompt limit length
    prompt_limit: int = _get_merge_prompt_limit(merge_profile)
    current_outputs: list[str] = partial_outputs
    merge_call_count: int = 0
    used_batch_merge: bool = False
    merge_level: int = 0


    while merge_level < MERGE_MAX_LEVELS:
        merge_level += 1

        merge_prompt: str = build_merge_prompt(partial_outputs=current_outputs, output_format_name=output_format["name"])
        predict_token_count: int = _calculate_token_count(merge_prompt)

        batches: list[list[str]]

        if predict_token_count <= prompt_limit:
            model_result, send_merge_time = _send_merge_prompt(merge_prompt=merge_prompt, model_config=model_config, merge_profile=merge_profile, connection=connection, output_format=output_format)
            # add the times in the total collection
            merge_call_count += send_merge_time

            # if the result do not cutoff, return
            if model_result["parse_status"] != ParseStatus.OUTPUT_CUTOFF or len(current_outputs) == 1:
                return model_result, merge_prompt, merge_call_count, used_batch_merge, predict_token_count


            # if the result cutoff, the response is to long make batches, send to the model
            middle_index:int = (len(current_outputs) + 1) // 2
            # split to two part
            batches = [current_outputs[:middle_index], current_outputs[middle_index:]]
            used_batch_merge = True

            print("Merge output was cutoff. Using two smaller merge batches.")
        else:
            # if only 1 PSM too long, it could not split (may be try other ways next time)
            if len(current_outputs) == 1:
                # build an not run result return
                model_result = _build_merge_not_run_result("One partial PSM is larger than the safe merge prompt limit.")

                return model_result, merge_prompt, merge_call_count, used_batch_merge, predict_token_count

            batches = _split_partial_outputs(partial_outputs=current_outputs, prompt_limit=prompt_limit, output_format=output_format)
            used_batch_merge = True

            print(f"Merge prompt estimate: {predict_token_count} tokens.")
            print(f"Using {len(batches)} smaller merge batches.")

        
        next_outputs: list[str] = []
        # loop the batches 
        for batch in batches:
            # get the prompt and prompt token 
            prompt: str = build_merge_prompt(partial_outputs=batch,  output_format_name=output_format["name"])
            predict_token_count: int = _calculate_token_count(prompt)

            # if splited batch is bigger than the limition, return the not run result
            if predict_token_count > prompt_limit:
                model_result = _build_merge_not_run_result("One merge batch is larger than the safe merge prompt limit.")
                
                return model_result, prompt, merge_call_count, used_batch_merge, predict_token_count

            # recursion itself for this batch
            batch_result, prompt, batch_call_count, batch_used_batch_merge, predict_token_count = (
                merge_partial_outputs(partial_outputs=batch, model_config=model_config, merge_profile=merge_profile, connection=connection, output_format=output_format)
            )

            merge_call_count += batch_call_count
            used_batch_merge = used_batch_merge or batch_used_batch_merge

            # check if the final status is not PSM, stop the merge
            if batch_result["parse_status"] != ParseStatus.VALID_PSM:
                return batch_result, prompt, merge_call_count, used_batch_merge, predict_token_count

            # check the batch output is dict
            batch_output: object | None = batch_result["parsed_output"]
            if isinstance(batch_output, dict):
                next_outputs.append(json.dumps(batch_output, ensure_ascii=False))

        current_outputs = next_outputs

    # the last time to merge the psm more the than MERGE_MAX_LEVELS, so fail
    merge_prompt = build_merge_prompt(partial_outputs=current_outputs,  output_format_name=output_format["name"])
    predict_token_count = _calculate_token_count(merge_prompt)
    model_result = _build_merge_not_run_result("The merge exceeded the maximum number of batch levels.")

    return model_result, merge_prompt, merge_call_count, used_batch_merge, predict_token_count


            
# build the new profile for merge part, using more bigger context
def build_merge_profile(model_profile: ModelProfile) -> ModelProfile:

    merge_options: dict[str, int | float] = model_profile["options"].copy()
    # put more bigger value in it
    merge_options["num_predict"] = MERGE_NUM_PREDICT

    merge_profile: ModelProfile = {
        "description": model_profile["description"],
        "options": merge_options,
        "think": model_profile["think"],
    }

    return merge_profile