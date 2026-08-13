from psmbench_local_baseline.generate_extraction_prompts import get_extraction_prompts_dict


"""
加载 segments
→ 调用 build_fsm_extraction_prompt()
→ Ollama 逐段抽取
→ 调用 build_fsm_combination_prompt()
→ Ollama 合并
→ parse_json_from_response()
→ 保存 final_fsm
"""


def main() -> None:
    # get the extrantion prompts
    extraction_prompts_dict: dict[str, list[str]] = get_extraction_prompts_dict()
    
if __name__ == "__main__":
    main()