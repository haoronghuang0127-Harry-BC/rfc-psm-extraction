import re
from typing import Final


WORD_PATTERN: Final[re.Pattern[str]] = re.compile(r"[A-Za-z0-9_+-]+")


def count_words(text: str) -> int:

    # find all the words in text
    words: list[str] = WORD_PATTERN.findall(text)

    # return the counter of the words
    return len(words)


def count_keyword(text: str, keyword: str) -> int:
    # find the counter of the keyword in the text
    
    # create the pattern
    pattern:str = rf"\b{re.escape(keyword)}\b"

    # find all the keywords in the text
    found_keyword: list[str] = re.findall(pattern, text, flags=re.IGNORECASE)

    # return the counter of found_keywords
    return len(found_keyword)