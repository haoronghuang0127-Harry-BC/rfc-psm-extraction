from method_1_section_selection.selection.section_features import SectionFeatures
from method_1_section_selection.selection.selection_rules import KEYWORD_DENSITY_SCALE, KEYWORD_WEIGHTS, MINIMUM_SECTION_WORDS, TITLE_BONUS, ScoringMethod


class ScoredSection(SectionFeatures):
    scoring_method: ScoringMethod
    keyword_score: int
    keyword_density_score: float
    title_bonus: int
    score: float

# Calculate the keyword score of one section.
def _calculate_keyword_score(keyword_counts: dict[str, int]) -> int:
    res: int = 0

    # calculate the score of each matched keyword.
    for keyword, count in keyword_counts.items():
        weight: int = KEYWORD_WEIGHTS[keyword]

        res += count * weight

    return res

# Calculate the weighted keyword score for every 1,000 words.
def _calculate_keyword_density_score(keyword_score: int, word_count: int) -> float:
    adjusted_word_count: int = max(word_count, MINIMUM_SECTION_WORDS)

    density_score: float = keyword_score / adjusted_word_count * KEYWORD_DENSITY_SCALE

    return round(density_score, 3)


# Calculate the extra score from the section title.
def _calculate_title_bonus(matched_titles: list[str]) -> int:
    res = 0

    for title in matched_titles:
        bonus: int = TITLE_BONUS[title]

        res += bonus

    return res

# Calculate all scores for one RFC section.
def score_section(features: SectionFeatures, scoring_method: ScoringMethod) -> ScoredSection:

    # get the keyword score
    keyword_counts: dict[str, int] = features["keyword_counts"]
    keyword_score: int = _calculate_keyword_score(keyword_counts)

    # get the keyword density score
    word_count: int = features["word_count"]
    keyword_density_score: float = _calculate_keyword_density_score(keyword_score, word_count)

    # get title bonus
    matched_titles: list[str] = features["matched_titles"]
    title_bonus: int = _calculate_title_bonus(matched_titles)

    # get total score
    if scoring_method == ScoringMethod.LEGACY_COUNT:
        total_score: float = keyword_score + title_bonus
    else:
        total_score = keyword_density_score + title_bonus

    scored_section: ScoredSection = {
        "section_number": features["section_number"],
        "section_name": features["section_name"],
        "tag": features["tag"],
        "content": features["content"],
        "word_count": features["word_count"],
        "keyword_counts": features["keyword_counts"],
        "matched_titles": features["matched_titles"],
        "source_index": features["source_index"],
        "scoring_method": scoring_method,
        "keyword_score": keyword_score,
        "keyword_density_score": keyword_density_score,
        "title_bonus": title_bonus,
        "score": total_score
    }

    return scored_section
