from method_1_section_selection.llm_experiment.experiment_command_line import read_command_line_to_value
from method_1_section_selection.llm_experiment.experiment_runner import run_experiment
from method_1_section_selection.llm_experiment.experiment_types import ExperimentArguments, ExperimentResult


def main() -> None:

    # read the command line
    arguments: ExperimentArguments = read_command_line_to_value()

    
    experiment_result: ExperimentResult = run_experiment(arguments)
    


if __name__ == "__main__":
    main()


    
