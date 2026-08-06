from collections.abc import Mapping
from pathlib import Path
from typing import Final

from config.paths import PSMBENCH_DIR

# Get All (14) the protocols section file in PSMBench Project
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


# Get All (14) the protocols reference PSM file
GROUND_TRUTH_FILES: Final[Mapping[str, Path]] = {
    "BGP": PSMBENCH_DIR / "BGP" / "BGP_state_machine.json",
    "DCCP": PSMBENCH_DIR / "DCCP" / "DCCP_state_machine.json",
    "DHCP": PSMBENCH_DIR / "DHCP" / "DHCP_state_machine.json",
    "FTP": PSMBENCH_DIR / "FTP" / "rfc959_state_machine.json",
    "IMAP": PSMBENCH_DIR / "IMAP" / "rfc9051_state_machine.json",
    "MQTT": PSMBENCH_DIR / "MQTT" / "MQTT_state_machine.json",
    "NNTP": PSMBENCH_DIR / "NNTP" / "rfc3977_state_machine.json",
    "POP3": PSMBENCH_DIR / "POP3" / "rfc1939_state_machine.json",
    "PPP": PSMBENCH_DIR / "PPP" / "PPP_state_machine.json",
    "PPTP": PSMBENCH_DIR / "PPTP" / "PPTP_state_machine.json",
    "RTSP": PSMBENCH_DIR / "RTSP" / "rfc7826_state_machine.json",
    "SIP": PSMBENCH_DIR / "SIP" / "rfc3261_state_machine.json",
    "SMTP": PSMBENCH_DIR / "SMTP" / "rfc5321_state_machine.json",
    "TCP": PSMBENCH_DIR / "TCP" / "rfc9293_state_machine.json"
}