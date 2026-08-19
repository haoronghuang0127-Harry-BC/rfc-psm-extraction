from enum import StrEnum

class ModelName(StrEnum):
    # small
    QWEN3_5_9B = "qwen3.5:9b"
    GEMMA3_12B = "gemma3:12b"

    # medium
    # qwen3.5:27b have thinking model
    QWEN3_5_27B = "qwen3.5:27b"
    GEMMA3_27B = "gemma3:27b"
    MISTRAL_SMALL3_1_24B = "mistral-small3.1:24b"
    # QWQ_32B automatically enables the thinking model
    QWQ_32B = "qwq:32b"

    # ALL for all the model
    ALL = "all"