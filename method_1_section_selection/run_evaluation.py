from config.paths import METHOD_1_OUTPUT_DIR

from evaluation.evaluate_runner import run_all_evaluations, run_summarized_results


def main() -> None:

    run_all_evaluations(output_dir=METHOD_1_OUTPUT_DIR)

    run_summarized_results(output_dir=METHOD_1_OUTPUT_DIR)


if __name__ == "__main__":
    main()