"""Generate only the three standard split-experiment CSV summaries.

Run from the project root:
    python -m split_experiment.analyze_split_experiment_results

The evaluation table uses separate Non-Thinking and Thinking metric rows.
Non-Thinking compares common conditions across all five methods. Thinking
compares the three methods with saved Thinking results; Original Segments and
Referenced Context Splitting scores remain blank.
Common Condition refers to the common set for that row's model mode.
The model table describes ALL saved protocols per model, like the reference;
use the evaluation table, not unmatched model means, to rank methods.

Only saved JSON Schema results are used. Scores are macro means computed
from evaluation counts and rounded to three decimals on the 0-1 scale.
Saved failures remain included; absent conditions are not assigned zero.
No manifest or PSMBench Local Baseline is read. No source
result is changed. No additional report, diagnostic CSV or README is written.
This recomputes arithmetic, not semantic matching or inference settings.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from statistics import mean
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_CONTROL = "ollama_json_schema_output"
ORIGINAL = "PSMBench Original Segments"
REFERENCED_CONTEXT = "Referenced Context Splitting"
SPLIT_METHODS = {
    "Whole Document": "whole_document_reference",
    "Fixed Token Splitting": "fixed_token_splitting",
    "Recursive Section Splitting": "recursive_section_splitting",
    REFERENCED_CONTEXT: "referenced_context_splitting",
}
METRICS = {
    "State": "states_match_results.csv",
    "Exact Transition": "transitions_match_results_whole.csv",
    "Partial Transition": "transitions_match_results_partial.csv",
}
PROFILES = {
    "gemma_mistral_no_think": "Non-Thinking",
    "qwen_no_think": "Non-Thinking",
    "qwen_think": "Thinking",
    "qwq_reasoning": "Thinking",
}
SCORES = ("Precision", "Recall", "F1")
SCORE_FIELDS = [f"{metric} {score}" for metric in METRICS for score in SCORES]
CONDITION_FIELDS = ["Split Method", "Protocol", "Model", "Common Condition", *SCORE_FIELDS]
MODEL_FIELDS = ["Data Source", "Split Method", "Model", "Total Protocols", *SCORE_FIELDS]
CaseKey = tuple[str, str]


def model_info(model: str) -> tuple[str, str, str]:
    suffix = "_" + OUTPUT_CONTROL
    if not model.endswith(suffix):
        raise ValueError(f"Not a JSON Schema condition: {model}")
    stem = model.removesuffix(suffix)
    for profile, mode in PROFILES.items():
        if stem.endswith("_" + profile):
            return stem.removesuffix("_" + profile), profile, mode
    raise ValueError(f"Unknown profile; update PROFILES explicitly: {model}")


def readable_model_name(model: str) -> str:
    name, _, mode = model_info(model)
    return f"{name}_{'no_think' if mode == 'Non-Thinking' else 'think'}"


def scores_from_counts(row: dict[str, str]) -> dict[str, float | int]:
    def count(*names: str) -> int:
        value = next((row[name] for name in names if name in row), None)
        if value is None:
            raise ValueError(f"Missing count column: {names}")
        number = float(value)
        if not math.isfinite(number) or number < 0 or not number.is_integer():
            raise ValueError(f"Invalid count {names}: {value}")
        return int(number)

    extracted = count("Total Extracted", "TotalExtracted")
    ground_truth = count("Total GT", "TotalGT")
    matched = count("Matched")
    if matched > min(extracted, ground_truth):
        raise ValueError("Matched exceeds the extracted or ground-truth count.")
    precision = matched / extracted if extracted else 0.0
    recall = matched / ground_truth if ground_truth else 0.0
    # Preserve the reference summaries' arithmetic and rounding sequence.
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {
        "Total Extracted": extracted,
        "Total GT": ground_truth,
        "Matched": matched,
        "Precision": precision,
        "Recall": recall,
        "F1": f1,
    }


def read_evaluations(root: Path) -> dict[CaseKey, dict[str, Any]]:
    indexes: dict[str, dict[CaseKey, dict[str, Any]]] = {}
    for metric, filename in METRICS.items():
        path = root / "evaluations" / filename
        indexes[metric] = {}
        with path.open(encoding="utf-8-sig", newline="") as handle:
            for line, row in enumerate(csv.DictReader(handle), 2):
                if not row["Model"].endswith("_" + OUTPUT_CONTROL):
                    continue
                model_info(row["Model"])
                key = (row["Protocol"], row["Model"])
                if key in indexes[metric]:
                    raise ValueError(f"Duplicate condition at {path}:{line}: {key}")
                try:
                    scores = scores_from_counts(row)
                except ValueError as error:
                    raise ValueError(f"{path}:{line}: {error}") from error
                for name, stored_column in (
                    ("Precision", "Precision"), ("Recall", "Recall"), ("F1", "F1-Score")
                ):
                    stored = float(row[stored_column])
                    if not math.isfinite(stored) or abs(stored - scores[name]) > 0.000501:
                        raise ValueError(f"Count/score mismatch at {path}:{line}: {name}")
                indexes[metric][key] = scores
    keys = set(indexes["State"])
    if not keys:
        raise ValueError(f"No JSON Schema evaluation rows in {root}")
    if any(set(index) != keys for index in indexes.values()):
        raise ValueError(f"The three evaluation CSVs have different conditions: {root}")
    return {key: {metric: index[key] for metric, index in indexes.items()} for key in sorted(keys)}


def validate_final_files(root: Path, evaluations: dict[CaseKey, dict[str, Any]]) -> None:
    """Check saved finals without exporting paths or diagnostic attributes."""
    for (protocol, model), metrics in evaluations.items():
        path = root / "final_fsms" / f"{protocol}_{model}_final_fsm.json"
        with path.open(encoding="utf-8-sig") as handle:
            data = json.load(handle)
        if data is not None and (not isinstance(data, dict)
                                or not isinstance(data.get("states"), list)
                                or not isinstance(data.get("transitions"), list)):
            raise ValueError(f"Invalid saved final FSM structure: {path}")
        empty = data is None or (not data["states"] and not data["transitions"])
        if empty and any(metric["Matched"] for metric in metrics.values()):
            raise ValueError(f"Null/empty final FSM has a nonzero saved match count: {path}")


def build_cohorts(methods: dict[str, Any]) -> list[dict[str, Any]]:
    cohorts = []
    for mode, labels in (
        ("Non-Thinking", list(methods)),
        ("Thinking", [label for label in methods
                      if label not in (ORIGINAL, REFERENCED_CONTEXT)]),
    ):
        keys = set.intersection(*[
            {key for key in methods[label]["evaluations"] if model_info(key[1])[2] == mode}
            for label in labels
        ])
        cohorts.append({"mode": mode, "labels": labels, "keys": keys})
    return cohorts


def validate_common_ground_truth(methods: dict[str, Any]) -> None:
    seen = {}
    for method in methods.values():
        for key, metrics in method["evaluations"].items():
            for metric, values in metrics.items():
                index = (key, metric)
                count = values["Total GT"]
                if index in seen and seen[index] != count:
                    raise ValueError(f"Ground-truth count differs between methods: {index}")
                seen[index] = count


def mean_score(method: dict[str, Any], keys: set[CaseKey], metric: str, score: str) -> float | None:
    return mean(method["evaluations"][key][metric][score] for key in sorted(keys)) if keys else None


def evaluation_rows(methods: dict[str, Any], cohorts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for cohort in cohorts:
        for metric in METRICS:
            row = {"Metric": f"{metric} ({cohort['mode']})", "Total Conditions": len(cohort["keys"])}
            for label, method in methods.items():
                for score in SCORES:
                    row[f"{label} Mean {score}"] = (
                        mean_score(method, cohort["keys"], metric, score)
                        if label in cohort["labels"] else None
                    )
            rows.append(row)
    return rows


def model_rows(methods: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for label, item in methods.items():
        for model in sorted({key[1] for key in item["evaluations"]}):
            keys = {key for key in item["evaluations"] if key[1] == model}
            row = {
                "Data Source": "Prompt Experiment Results 1" if label == ORIGINAL else "Split Experiment Results",
                "Split Method": label,
                "Model": readable_model_name(model),
                "Total Protocols": len(keys),
            }
            for metric in METRICS:
                for score in SCORES:
                    row[f"{metric} {score}"] = mean_score(item, keys, metric, score)
            rows.append(row)
    return rows


def condition_rows(methods: dict[str, Any], cohorts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    common = {cohort["mode"]: cohort for cohort in cohorts}
    for label, item in methods.items():
        for key, metrics in item["evaluations"].items():
            cohort = common[model_info(key[1])[2]]
            row = {
                "Split Method": label,
                "Protocol": key[0],
                "Model": key[1],
                "Common Condition": "Yes" if label in cohort["labels"] and key in cohort["keys"] else "No",
            }
            for metric, values in metrics.items():
                for score in SCORES:
                    row[f"{metric} {score}"] = values[score]
            rows.append(row)
    return rows


def save_csv(path: Path, rows: list[dict[str, Any]], headers: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: round(value, 3) if isinstance(value, float) else value
                             for key, value in row.items()})


def generate_summary(original_results: Path, split_outputs: Path, output_dir: Path) -> dict[str, int]:
    roots = {ORIGINAL: original_results.resolve(), **{
        label: (split_outputs / folder).resolve() for label, folder in SPLIT_METHODS.items()
    }}
    methods = {}
    for label, root in roots.items():
        evaluations = read_evaluations(root)
        validate_final_files(root, evaluations)
        methods[label] = {"evaluations": evaluations}
    validate_common_ground_truth(methods)
    cohorts = build_cohorts(methods)
    if not cohorts[0]["keys"]:
        raise ValueError("No common Non-Thinking conditions across the five methods.")

    evaluation_fields = ["Metric", "Total Conditions", *[
        f"{label} Mean {score}" for label in methods for score in SCORES
    ]]
    tables = {
        "split_experiment_condition_results.csv": (condition_rows(methods, cohorts), CONDITION_FIELDS),
        "split_experiment_evaluation_summary.csv": (evaluation_rows(methods, cohorts), evaluation_fields),
        "split_experiment_model_output_summary.csv": (model_rows(methods), MODEL_FIELDS),
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    for name, (rows, headers) in tables.items():
        save_csv(output_dir / name, rows, headers)
        print(f"CSV: {name} ({len(rows)} rows)")
    print(f"Non-Thinking common conditions: {len(cohorts[0]['keys'])}")
    print(f"Thinking common conditions: {len(cohorts[1]['keys'])}")
    return {name: len(rows) for name, (rows, _) in tables.items()}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--original-results", type=Path,
                        default=PROJECT_ROOT / "output_data" / "Prompt_experiment_results_repaired")
    parser.add_argument("--split-outputs", type=Path, default=PROJECT_ROOT / "split_experiment" / "outputs")
    parser.add_argument("--output-dir", type=Path, default=PROJECT_ROOT / "output_data")
    args = parser.parse_args()
    generate_summary(args.original_results, args.split_outputs, args.output_dir.resolve())


if __name__ == "__main__":
    main()
