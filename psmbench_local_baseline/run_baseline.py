from psmbench_local_baseline.generate_extraction_prompts import get_extraction_prompts_dict
from psmbench_local_baseline.llm_extraction import extraction_psm


def main() -> None:
    # get the extrantion prompts
    extraction_prompts_dict: dict[str, list[str]] = get_extraction_prompts_dict()

    extraction_psm(extraction_prompts_dict)
    
if __name__ == "__main__":
    main()