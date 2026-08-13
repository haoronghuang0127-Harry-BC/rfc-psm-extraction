from collections.abc import Mapping
from pathlib import Path

from config.protocol.protocol_files import GROUND_TRUTH_FILES, PROTOCOL_FILES

from rfc.rfc_io import load_rfc_segments
from rfc.rfc_types import RfcSegment

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


def get_all_protocol() -> dict[str, list[RfcSegment]]:

    # get all the protocol files path
    protocol_files_path: dict[str, Path] = get_all_protocol_files()

    # init the dict result
    rfc_segments_dict: dict[str, list[RfcSegment]] = {}

    for protocol, file_path in protocol_files_path.items():
        segments: list[RfcSegment] = load_rfc_segments(file_path=file_path)
        rfc_segments_dict[protocol] = segments

    return rfc_segments_dict




"""
get the ground truth files
"""
def get_ground_truth_file(protocol:str) -> Path:
    return _get_protocol_file(protocol=protocol, mapping_files=GROUND_TRUTH_FILES)

def get_all_ground_truth_files() -> dict[str, Path]:
    return _get_all_protocol_file(GROUND_TRUTH_FILES)
