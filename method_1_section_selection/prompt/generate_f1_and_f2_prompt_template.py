import json

from typing import Final


# this is the example for section result 
SECTION_RESULT_EXAMPLE: Final[dict[str, object]] = {
    "has_psm": True,
    "states": [
        "state1",
        "state2",
    ],
    "transitions": [
        {
            "from": "state1",
            "event": "receive COMMAND",
            "action": "reply CODE",
            "to": "state2",
        },
    ],
}

# this is the example for section result when no PSM
NO_PSM_RESULT_EXAMPLE: Final[dict[str, object]] = {
    "has_psm": False,
    "states": [],
    "transitions": [],
}

# the f1 and f2 method using the same section prompt
def build_f1_and_f2_section_prompt_from_template(protocol:str, section_title: str, section_text: str) -> str:
    prompt_template: str = f"""
        You will be given the section "{section_title}" of an RFC document for protocol "{protocol}".

        RESPONSE FORMAT:

        - Return only one valid JSON object.
        - Do not use <json> tags.
        - Do not include explanations, Markdown, or comments.

        <section>
        {section_text}
        </section>

        Steps:

        1. Check whether the section contains information about protocol states or transitions.
        2. If the section does not contain this information, return:

        {json.dumps(NO_PSM_RESULT_EXAMPLE, ensure_ascii=False, indent=2)}

        3. If the section contains PSM information, return a JSON object like this:

        {json.dumps(SECTION_RESULT_EXAMPLE, ensure_ascii=False, indent=2)}

        Field rules:

        - "states" contains all states used in "from" and "to".
        - Use short and consistent state names.
        - "event" describes what causes the transition.
        - "action" describes what the protocol does.
        - If there is no action, use an empty string.
        - Every transition must contain "from", "event", "action", and "to".
        - Do not invent states or transitions that are not supported by the RFC text.
        - Do not include additional JSON fields.
        - Return only the JSON object.
    """

    return prompt_template.strip()



# this is the example for merge result 
RESULT_EXAMPLE: Final[dict[str, object]] = {
    "states": [
        "state1",
        "state2",
    ],
    "initial_state": "state1",
    "final_states": [
        "state2",
    ],
    "transitions": [
        {
            "from": "state1",
            "event": "receive COMMAND",
            "action": "reply CODE",
            "to": "state2",
        }
    ],
}

# the f1 and f2 method using the same merge prompt
def build_f1_and_f2_merge_prompt_from_template(partial_texts: str) -> str:
    prompt_template: str = f"""
        You will be provided with multiple partial protocol state machines
        extracted from different sections of one RFC document.

        Each partial PSM is wrapped in <partial> and </partial>.

        A partial PSM may contain:

        - "has_psm"
        - "states"
        - "transitions"

        Each transition contains:

        - "from"
        - "event"
        - "action"
        - "to"

        Ignore a partial PSM when "has_psm" is false.

        Your task is to combine all valid partial PSMs into one global PSM.

        Return only one valid JSON object using this structure:

        {json.dumps(RESULT_EXAMPLE, ensure_ascii=False, indent=2)}

        FSM construction constraints:

        "states", "from", and "to":

        - Use short, meaningful, and consistent state names.
        - Use CamelCase or snake_case.
        - Do not use long free-text descriptions.

        "event":

        - Describe the trigger that causes the transition.
        - It may begin with "receive", "send", "timeout", or "cond".

        "action":

        - Describe the response or operation caused by the event.
        - Use a short action phrase.
        - If no action is available, use an empty string.

        FSM merging rules:

        1. Standardise state names that clearly describe the same state.
        2. Remove duplicate states and transitions.
        3. Keep similar states separate when they describe different
        protocol phases.
        4. Preserve the meaning of events and actions.
        5. Do not invent new states or transitions.
        6. Include every "from" and "to" state in "states".
        7. Use the state with no incoming transitions as "initial_state".
        8. Use states with no outgoing transitions as "final_states".
        9. Do not include additional JSON fields.
        10. Do not include <json> tags.
        11. Return only the JSON object.

        Here are the partial PSMs:

        {partial_texts}
    """

    return prompt_template.strip()