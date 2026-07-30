# Get the PSMBench Project Path
from config.paths import PSMBENCH_DIR
from pathlib import Path
from typing import Final
from collections.abc import Mapping

#Get All (14) the protocols section file in PSMBench Project
PROTOCOL_FILES: Final[Mapping[str, Path]] = {
    "BGP": PSMBENCH_DIR / "BGP" / "rfc4271_segments.json",
    "DCCP": PSMBENCH_DIR / "DCCP" / "rfc4340_segments.json",
    "DHCP": PSMBENCH_DIR / "DHCP" / "rfc2131_segments.json",
    "FTP": PSMBENCH_DIR / "FTP" / "rfc959_segments.json",
    "IMAP": PSMBENCH_DIR / "IMAP" / "rfc9051_segments.json",
    "MQTT": PSMBENCH_DIR / "MQTT" / "rfc9431_segments.json",
    "NNTP": PSMBENCH_DIR / "NNTP" / "rfc3977_segments.json",
    "POP3": PSMBENCH_DIR / "POP3" / "rfc1939_segments.json",
    "PPP": PSMBENCH_DIR / "PPP" / "rfc1661_segments.json",
    "PPTP": PSMBENCH_DIR / "PPTP" / "rfc2637_segments.json",
    "RTSP": PSMBENCH_DIR / "RTSP" / "rfc7826_segments.json",
    "SIP": PSMBENCH_DIR / "SIP" / "rfc3261_segments.json",
    "SMTP": PSMBENCH_DIR / "SMTP" / "rfc5321_segments.json",
    "TCP": PSMBENCH_DIR / "TCP" / "rfc9293_segments.json",
}

# check whether the protocol name is validated and in the PSMBench project
def _check_protocol_name(protocol: str) -> str:
    # remove the protocol string space and change to uppercase
    protocol = protocol.strip().upper()


    # Check the protocol name is in the PSMBench Project
    if protocol not in PROTOCOL_FILES:
        all_the_protocol: str = ", ".join(PROTOCOL_FILES.keys())

        raise ValueError(f"Unknown protocol: {protocol}  \n Available protocols: {all_the_protocol}")


    return protocol


def _check_file_exists(file_path: Path) -> None:
    # raise the error when the protocol is not found
    if not file_path.exists():  
        raise FileNotFoundError(f"Protocol file not found {file_path}")


def get_protocol_file(protocol: str) -> Path:

    # check protocol name
    protocol = _check_protocol_name(protocol)

    # get file path
    file_path: Path = PROTOCOL_FILES[protocol]
    # check protocol file
    _check_file_exists(file_path)

    return file_path


def get_all_protocol_files() -> dict[str, Path]:

    # check all the protocol file
    for file_path in PROTOCOL_FILES.values():
        _check_file_exists(file_path)

    # return the copy of all the protocol files
    return PROTOCOL_FILES.copy()


    

    
