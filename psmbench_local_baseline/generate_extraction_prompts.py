from pathlib import Path
import sys

from config.paths import PSMBENCH_DIR, PSMBENCH_LOCAL_BASELINE_EXTRACTION_PROMPTS, PSMBENCH_LOCAL_BASELINE_OUTPUT_DIR
from config.protocol.protocol_util import get_all_protocol

from rfc.rfc_types import RfcSegment
from utils.files_util import save_json_file

if str(PSMBENCH_DIR) not in sys.path:
    sys.path.insert(0, str(PSMBENCH_DIR))
from prompt_generation import build_fsm_extraction_prompt


def _print_the_rfc_segments_info(rfc_segments_dict: dict[str, list[RfcSegment]]) -> None:
    print(f"Loaded {len(rfc_segments_dict)} PSMBench protocols.")

    for protocol, segments in rfc_segments_dict.items():
        print(f"{protocol}: {len(segments)} segments")

def _print_the_extraction_prompts_info(extraction_prompts_dict: dict[str, list[str]]) -> None:

    total_prompts: int = 0
    for protocol_prompts in extraction_prompts_dict.values():
        total_prompts += len(protocol_prompts)

    print(f"Built {total_prompts} extraction prompts for {len(extraction_prompts_dict)} protocols.")

    for protocol, protocol_prompts in extraction_prompts_dict.items():
        print(f"{protocol}: {len(protocol_prompts)} extraction prompts")

def _build_original_psmbench_extraction_prompts(rfc_segments_dict: dict[str, list[RfcSegment]]) -> dict[str, list[str]]:
    # init extraction prompts dict
    extraction_prompts_dict: dict[str, list[str]] = {}

    for protocol, rfc_segments in rfc_segments_dict.items():
        # init segments prompts
        prompt_list: list[str] = []

        for index, segment in enumerate(rfc_segments, start=1):
            # get the rfc tag as section title
            section_title: str = segment["tag"]
            # get the content as section text
            section_text: str = segment["content"]

            # get the extraction prompt
            prompt: str = build_fsm_extraction_prompt(protocol_name=protocol, section_title=section_title ,section_text=section_text)

            prompt_list.append(prompt)

        extraction_prompts_dict[protocol] = prompt_list

    return extraction_prompts_dict

def _save_extraction_prompts(extraction_prompts_dict: dict[str, list[str]]) -> None:
    PSMBENCH_LOCAL_BASELINE_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    output_file_path: Path = PSMBENCH_LOCAL_BASELINE_EXTRACTION_PROMPTS

    save_json_file(file_path=output_file_path,data=extraction_prompts_dict)

    print(f"Saved extraction prompts: {output_file_path}.")

def get_extraction_prompts_dict() -> dict[str, list[str]]:
    # load the original PSMBench segemnts.
    rfc_segments_dict: dict[str, list[RfcSegment]] = get_all_protocol()
    _print_the_rfc_segments_info(rfc_segments_dict)

    # get the extrantion prompts using PSMBench original function
    extraction_prompts_dict: dict[str, list[str]] = _build_original_psmbench_extraction_prompts(rfc_segments_dict)
    _print_the_extraction_prompts_info(extraction_prompts_dict)
    # save the prompts
    _save_extraction_prompts(extraction_prompts_dict)

    return extraction_prompts_dict

def main() -> None:
    get_extraction_prompts_dict()

if __name__ == "__main__":
    main()