from typing import Final
from collections.abc import Mapping
from enum import StrEnum

# Scoring methods used to rank RFC sections.
class ScoringMethod(StrEnum):
    LEGACY_COUNT = "legacy_count"
    KEYWORD_DENSITY = "keyword_density"

# Calculate the weighted keyword score for every 1,000 words.
KEYWORD_DENSITY_SCALE: Final[int] = 1000
MINIMUM_SECTION_WORDS: Final[int] = 100

# the ratio of the different level priority
HIGH_PRIORITY_RATIO: Final[float] = 0.25
MEDIUM_PRIORITY_RATIO: Final[float] = 0.70

# Keyword weights used to calculate the keyword score of a section.
KEYWORD_WEIGHTS: Final[Mapping[str, int]] = {
    "state": 8,
    "states": 8,
    "transition": 8,
    "transitions": 8,
    "command": 5,
    "commands": 5,
    "response": 4,
    "responses": 4,
    "event": 6,
    "events": 6,
    "receive": 5,
    "received": 5,
    "send": 5,
    "sent": 5,
    "connection": 3,
    "connections": 3,
    "open": 3,
    "opened": 3,
    "close": 3,
    "closed": 3,
    "timeout": 4,
    "timer": 4,
    "syn": 5,
    "ack": 4,
    "fin": 5,
    "rst": 5,
    "must": 1,
    "should": 1,
    "may": 1,
}

# The extra scores, when these keywords appears in a section title.
TITLE_BONUS: Final[Mapping[str, int]] = {
    "state": 40,
    "operation": 25,
    "functional specification": 40,
    "command": 25,
    "connection": 20,
}
