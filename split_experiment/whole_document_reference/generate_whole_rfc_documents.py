from pathlib import Path

from config.paths import WHOLE_DOCUMENT_REFERENCE_DOCUMENTS_DIR, WHOLE_DOCUMENT_REFERENCE_MANIFESTS_DIR
from config.protocol.protocol_util import get_all_protocol_files, get_protocol_file

from rfc.rfc_io import load_rfc_segments
from rfc.rfc_service import get_rfc_segment_values
from rfc.rfc_types import RfcSegment

from split_experiment.command_line import read_command_line_to_value
from split_experiment.types import SplitExperimentArguments, WholeRfcDocumentManifest

from utils.files_util import save_json_file


# build one whole RFC document from the original PSMBench segments.
def _build_whole_rfc_document(rfc_segments: list[RfcSegment]) -> RfcSegment:
    section_texts: list[str] = []

    for segment in rfc_segments:
        _section_number, _section_name, section_title, section_text = get_rfc_segment_values(segment=segment)

        whole_section_text: str = f"{section_title}\n{section_text}"

        section_texts.append(whole_section_text)

    whole_document_text: str = "\n\n".join(section_texts)

    whole_rfc_document: RfcSegment = {
        "section_number": "",
        "section_name": "Whole RFC Document",
        "tag": "Whole RFC Document",
        "content": whole_document_text,
    }

    return whole_rfc_document


# save one whole RFC document.
def _save_whole_rfc_document(protocol: str, whole_rfc_document: RfcSegment) -> Path:
    output_file: Path = WHOLE_DOCUMENT_REFERENCE_DOCUMENTS_DIR / f"{protocol}_whole_rfc_document.json"

    save_json_file(file_path=output_file, data=[whole_rfc_document])

    print(f"Saved whole RFC document: {output_file}")

    return output_file


# save the manifest for one whole RFC document.
def _save_whole_rfc_document_manifest(protocol: str, source_file: Path, source_segment_count: int, whole_document_file: Path) -> Path:
    manifest: WholeRfcDocumentManifest = {
        "condition": "whole_document_reference",
        "protocol": protocol,
        "source_file": str(source_file),
        "source_segment_count": source_segment_count,
        "whole_document_file": str(whole_document_file),
    }

    manifest_file: Path = WHOLE_DOCUMENT_REFERENCE_MANIFESTS_DIR / f"{protocol}_whole_rfc_document_manifest.json"

    save_json_file(file_path=manifest_file, data=manifest)

    print(f"Saved whole RFC document manifest: {manifest_file}")

    return manifest_file


# generate whole RFC documents for the selected protocols.
def generate_whole_rfc_documents(protocol: str) -> dict[str, RfcSegment]:
    protocol_files: dict[str, Path] = {}

    # get the selected protocol files.
    if protocol == "all":
        protocol_files = get_all_protocol_files()
    else:
        protocol_files = {
            protocol: get_protocol_file(protocol=protocol),
        }

    whole_rfc_documents: dict[str, RfcSegment] = {}

    for protocol_name, protocol_file in protocol_files.items():
        rfc_segments: list[RfcSegment] = load_rfc_segments(file_path=protocol_file)

        whole_rfc_document: RfcSegment = _build_whole_rfc_document(rfc_segments=rfc_segments)
        whole_document_file: Path = _save_whole_rfc_document(protocol=protocol_name, whole_rfc_document=whole_rfc_document)

        _save_whole_rfc_document_manifest(protocol=protocol_name, source_file=protocol_file, source_segment_count=len(rfc_segments), whole_document_file=whole_document_file)

        whole_rfc_documents[protocol_name] = whole_rfc_document

        print(f"Built one whole RFC document for {protocol_name} from {len(rfc_segments)} original segments.")

    return whole_rfc_documents


def main() -> None:
    arguments: SplitExperimentArguments = read_command_line_to_value()

    whole_rfc_documents: dict[str, RfcSegment] = generate_whole_rfc_documents(protocol=arguments["protocol"])

    print(f"Completed whole RFC document generation. Saved {len(whole_rfc_documents)} documents.")


if __name__ == "__main__":
    main()
