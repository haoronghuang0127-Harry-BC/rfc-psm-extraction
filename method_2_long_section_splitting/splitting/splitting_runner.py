from pathlib import Path

from config.protocol.protocol_util import get_all_protocol_files

from method_2_long_section_splitting.splitting.splitting_rfc_service import process_protocol

# split all the rfc documents
def split_all_the_rfc() -> None:
    # get all the protocol files
    protocol_files: dict[str, Path] = get_all_protocol_files()

    # loop to process
    for protocol, source_file in protocol_files.items():
        process_protocol(protocol=protocol, source_file=source_file)