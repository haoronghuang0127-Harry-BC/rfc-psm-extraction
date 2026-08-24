import json

from pathlib import Path

from evaluation.evaluation_types import StateMachine, TransitionRecord

from utils.files_util import check_file_exists


# check the value if string and not empty
# some rfc may have empty in the "action" and the "event" value
def _check_string(item: object, name: str, allow_empty: bool = False) -> str:
    if not isinstance(item, str):
        raise ValueError(f"{name} must be a string.")

    item = item.strip()

    if not item and not allow_empty:
        raise ValueError(f"{name} can not empty.")

    return item


def _get_string_list(_object: object, name: str) -> list[str]:

    # check the _object must be a list
    if not isinstance(_object, list):
        raise ValueError(f"{name} must be a list.")

    str_list: list[str] = []

    # loop the object to list
    for item in _object:
        # check if string
        item = _check_string(item=item, name=name)

        str_list.append(item)

    return str_list

# get one tranistion from the lsit
def _get_transition(transition: object, index: int) -> TransitionRecord:

    # check if the transition is a oject
    if not isinstance(transition, dict):
        raise ValueError(f"Transition {index} must be an object.\n  Transition:{transition}")

    # get the transition value
    from_value: object = transition.get("from")
    event_value: object = transition.get("event")
    action_value: object = transition.get("action")
    to_value: object = transition.get("to")

    # check if each value is a string
    from_str: str = _check_string(from_value, f"Transition {index} from")
    event_str: str = _check_string(event_value, f"Transition {index} event", allow_empty=True)
    action_str: str = _check_string(action_value, f"Transition {index} action", allow_empty=True)
    to_str: str = _check_string(to_value, f"Transition {index} to")

    transition: TransitionRecord = {
        "from": from_str,
        "event": event_str,
        "action": action_str,
        "to": to_str,
    }

    return transition

def _get_transitions(transitions_object: object) -> list[TransitionRecord]:

    if not isinstance(transitions_object, list):
        raise ValueError(f"Transitions must be a list.")

    transitions: list[TransitionRecord] = []

    for index, transition in enumerate(transitions_object, start=1):
        # check the transition if valid
        transition = _get_transition(transition=transition, index=index)
        transitions.append(transition)

    return transitions




def _build_state_machine(state_machine_object: object) -> StateMachine:

    # check if the PSM is a json object
    if not isinstance(state_machine_object, dict):
        raise ValueError("The PSM must be a JSON object")

    # get the states
    states_object: object = state_machine_object.get("states")
    states: list[str] = _get_string_list(_object=states_object, name="states")

    # get the initial_state
    initial_state_object: object = state_machine_object.get("initial_state")
    initial_state: str = _check_string(item=initial_state_object, name="initial_state")

    # get the final_states
    final_states_object: object = state_machine_object.get("final_states")
    final_states: list[str] = _get_string_list(_object=final_states_object, name="final_states")

    # get transitions
    transitions_object: object = state_machine_object.get("transitions")
    transitions: list[TransitionRecord] = _get_transitions(transitions_object=transitions_object)

    state_machine: StateMachine = {
        "states": states,
        "initial_state": initial_state,
        "final_states": final_states,
        "transitions": transitions,
    }

    return state_machine


# load the reference psm and load the model outputs
# need to check if the model outputs psm is valid
# some time the mode will output "null" or empty in the json file so need check it
def load_and_build_state_machine(file_path: Path) -> StateMachine:

    # check the file is exists
    check_file_exists(file_path=file_path, erros_message=f"PSM file is not found: {file_path}")

    # load the json state machine file
    try:
        with file_path.open("r", encoding="utf-8") as file:
            state_machine_object: object = json.load(file)
    except json.JSONDecodeError as error:
        raise ValueError(f"The PSM file contains invalid JSON: {file_path}") from error


    # build the state machine
    state_machine: StateMachine = _build_state_machine(state_machine_object)


    return state_machine


# load a research fsm containing states and transitions.
def load_and_build_research_state_machine(file_path: Path) -> StateMachine:
    # check the file is exists
    check_file_exists(file_path=file_path, erros_message=f"PSM file is not found: {file_path}")

    # load the json state machine file
    try:
        with file_path.open("r", encoding="utf-8") as file:
            state_machine_object: object = json.load(file)
    except json.JSONDecodeError as error:
        raise ValueError(f"The PSM file contains invalid JSON: {file_path}") from error

    # the research fsm must be a json object.
    if not isinstance(state_machine_object, dict):
        raise ValueError("The PSM must be a JSON object")

    # get the states.
    states_object: object = state_machine_object.get("states")
    states: list[str] = _get_string_list(_object=states_object, name="states")

    # get the transitions.
    transitions_object: object = state_machine_object.get("transitions")
    transitions: list[TransitionRecord] = _get_transitions(transitions_object=transitions_object)

    # initial and final states are not generated or evaluated in Research mode.
    # because in some protocol do not have the real initial_state and final_states
    state_machine: StateMachine = {
        "states": states,
        "initial_state": "",
        "final_states": [],
        "transitions": transitions,
    }

    return state_machine