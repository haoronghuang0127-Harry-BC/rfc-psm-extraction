import json
from pathlib import Path
from typing import TypeVar

T = TypeVar("T")  

def check_file_exists(file_path: Path, erros_message: str) -> None:
    # raise the error when the file is not found
    if not file_path.exists():  
        raise FileNotFoundError(erros_message)

def load_json_file(file_path: Path, data_type: type[T]) -> T:
    with file_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    loaded_data: T = data_type(data)

    return loaded_data