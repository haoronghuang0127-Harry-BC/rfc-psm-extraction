# Extraction of Protocol State Machines from RFCs using local LLMs

## Project Description

This project selects useful sections from RFC documents before sending them to a large language model (LLM).

This project uses PSMBench data and runs local LLMs with Ollama.

## Main Folders

- `method_1_section_selection/`: section selection, prompt generation, and LLM experiments.
- `config/`: protocol paths, model names, and experiment settings.
- `util/`: shared helper functions.
- `PSMBench/`: third-party benchmark data and code.

## Setup

Python 3.11 or a newer version is recommended.

Install the main dependency:

```powershell
pip install python-dotenv
```

Copy `.env.example` to `.env`, and then set the local or remote Ollama URL.

## Run the Project

Run all commands from the project root folder.

Select RFC sections:

```powershell
python -m method_1_section_selection.hybrid_section_selection
```

Generate LLM prompts:

```powershell
python -m method_1_section_selection.generate_llm_prompts
```

Show the LLM experiment options:

```powershell
python -m method_1_section_selection.run_llm_extraction --help
```

Generated files are saved in `method_1_section_selection/outputs/`. 

## PSMBench

PSMBench is a third-party project. It is not my original work.

- Project: [RFC_PSM_Benchmark](https://github.com/Zilinlin/RFC_PSM_Benchmark)
- Authors: Zilin Shen, Xinyu Luo, Imtiaz Karim, and Elisa Bertino
- License: Apache License 2.0

The original license is kept in `PSMBench/LICENSE`.
