from collections.abc import Mapping
from pathlib import Path

from config.protocol.protocol_files import GROUND_TRUTH_FILES, PROTOCOL_FILES
from utils.files_util import check_file_exists



def _check_protocol_name(protocol: str, mapping_files: Mapping[str, Path]) -> str:
    # remove the protocol string space and change to uppercase
    protocol = protocol.strip().upper()


    # Check the protocol name is in the PSMBench Project
    if protocol not in mapping_files:
        all_the_protocol: str = ", ".join(mapping_files.keys())

        raise ValueError(f"Unknown protocol: {protocol}  \n Available protocols: {all_the_protocol}")


    return protocol

# this function using to get the file by Mapping parameters
def _get_protocol_file(protocol: str, mapping_files: Mapping[str, Path]) -> Path:
    # check protocol name
    protocol = _check_protocol_name(protocol, mapping_files)

    # get file path
    file_path: Path = mapping_files[protocol]
    # check protocol file
    check_file_exists(file_path, f"File is not found: {file_path}")

    return file_path

# this function using to get the all the file by Mapping parameters
def _get_all_protocol_file(mapping_files: Mapping[str, Path]) -> dict[str, Path]:
    # check all the protocol file
    for file_path in mapping_files.values():
        check_file_exists(file_path, f"File is not found: {file_path}")

    # return the copy of all the protocol files
    return mapping_files.copy()



"""
get the original protocol files
"""
def get_protocol_file(protocol: str) -> Path:
    return _get_protocol_file(protocol=protocol, mapping_files=PROTOCOL_FILES)


def get_all_protocol_files() -> dict[str, Path]:
    return _get_all_protocol_file(PROTOCOL_FILES)



"""
get the ground truth files
"""
def get_ground_truth_file(protocol:str) -> Path:
    return _get_protocol_file(protocol=protocol, mapping_files=GROUND_TRUTH_FILES)

def get_all_ground_truth_files() -> dict[str, Path]:
    return _get_all_protocol_file(GROUND_TRUTH_FILES)
