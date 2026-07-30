from enum import StrEnum

class ModelName(StrEnum):
    # small
    QWEN3_5_9B = "qwen3.5:9b"
    MINISTRAL_3_8B = "ministral-3:8b"
    LLAMA3_1_8B = "llama3.1:8b"
    GEMMA3_12B = "gemma3:12b"
    DEEPSEEK_R1_8B = "deepseek-r1:8b"

    # medium
    QWEN3_5_27B = "qwen3.5:27b"
    QWEN3_5_35B = "qwen3.5:35b"
    MISTRAL_SMALL3_2_24B = "mistral-small3.2:24b"
    GEMMA3_27B = "gemma3:27b"
    DEEPSEEK_R1_32B = "deepseek-r1:32b"
    GPT_OSS_20B = "gpt-oss:20b"

    # large
    LLAMA3_3_70B = "llama3.3:70b"
    DEEPSEEK_R1_70B = "deepseek-r1:70b"
    QWEN3_NEXT_80B = "qwen3-next:80b-a3b-instruct-q4_K_M"

    # extra large
    GPT_OSS_120B = "gpt-oss:120b"
    QWEN3_5_122B = "qwen3.5:122b"