# Extraction of Protocol State Machines from RFCs using local LLMs

## Project Description

This project reproduces the PSMBench extraction workflow using local LLMs and compares different prompt output control and FSM evaluation methods.

This project uses PSMBench data and runs local LLMs with Ollama.

## Project Structure

- `config/`: protocol, model, profile, Ollama, and path configuration.
- `rfc/`: RFC types, loading, and related functions.
- `utils/`: shared helper functions.
- `evaluation/`: original PSMBench evaluation, one-to-one evaluation, and CSV summary generation.
- `psmbench_local_baseline/`: original PSMBench extraction workflow using local Ollama models.
- `prompt_experiment/`: prompt and JSON output control experiments.
- `research_pipeline/`: shared model selection and response processing functions.
- `output_data/`: saved experiment and evaluation results.
- `RFC_PSM_Benchmark-main/`: third-party benchmark data and code.

## Setup

Python 3.11 or a newer version is recommended.

Install the main dependency:

```powershell
pip install -r requirements.txt
```

Copy `.env.example` to `.env`, and then set the local or remote Ollama URL.

For a local Ollama test, pull the model used by the quick examples:

```powershell
ollama pull qwen3.5:9b
```

Make sure Ollama is running before starting an LLM experiment.

On Windows, use `py` instead of `python` if the `python` command is not available.

## Run the Project

Run all commands from the project root folder.

### Original PSMBench evaluation

These commands evaluate the saved FSM files in `RFC_PSM_Benchmark-main/fsm/`.

Ollama is not required for these commands.

The first evaluation run may download the `all-MiniLM-L6-v2` sentence-transformer model.

#### 1.Run the original PSMBench evaluation:

```powershell
python -m evaluation.run_original_psmbench_evaluation
```

The generated CSV files are saved in `output_data/PSMBench_original_evaluation_results/`.

#### 2.Run the new one to one PSMBench evaluation:

```powershell
python -m evaluation.run_original_psmbench_new_evaluation
```

The generated CSV files are saved in `output_data/PSMBench_new_evaluation_results/`.

#### 3.Compare the two evaluation methods:

Run Steps 1 and 2 first.

```powershell
python -m evaluation.analyze_evaluation_results
```

The summary is saved in `output_data/psmbench_original_vs_new_evaluation_summary.csv`.

These evaluation scripts do not have command line options. The protocols, models, and matching threshold are defined in the Python files.


### PSMBench local Ollama baseline

Run the following commands in order.

The quick example uses `PPP` because it contains only 6 RFC segments.

#### 1.Generate the original PSMBench extraction prompts:

```powershell
python -m psmbench_local_baseline.generate_extraction_prompts
```

#### 2.Run a quick extraction test:

```powershell
python -m psmbench_local_baseline.llm_extraction --protocol PPP --model qwen3.5:9b --connection auto
```

#### 3.Process extraction responses:

```powershell
python -m psmbench_local_baseline.process_extraction_responses
```

#### 4.Generate combination prompts:

```powershell
python -m psmbench_local_baseline.generate_combination_prompts
```

#### 5.Run LLM combination:

```powershell
python -m psmbench_local_baseline.llm_combination
```

#### 6.Extract final FSMs:

```powershell
python -m psmbench_local_baseline.extract_final_fsms
```

#### 7.Evaluate the final FSMs:

```powershell
python -m psmbench_local_baseline.run_evaluation
```

Show the baseline extraction command line options:

Run Step 1 before using this help command.

```powershell
python -m psmbench_local_baseline.llm_extraction --help
```

The extraction stage supports these options:

- `--protocol`: Select one protocol or `all`.
- `--model`: Select an Ollama model or `all`.
- `--connection`: Use a local or remote Ollama server.
- `--thinking`: Enable optional thinking for supported Qwen models.

The current complete baseline workflow supports `qwen3.5:9b` and `qwen3.5:27b` without thinking, Gemma, and Mistral.

Qwen thinking and QwQ combination are currently not enabled.

Generated files are saved in `psmbench_local_baseline/outputs/`.


### Prompt output control experiment

This experiment compares different methods for controlling the LLM JSON output.

Run the following commands in order.

The quick example uses one protocol, one model, and one output control method.

#### 1.Generate extraction prompts:

```powershell
python -m prompt_experiment.output_format.generate_extraction_prompts --protocol PPP --output-control ollama_json_output
```

#### 2.Run LLM extraction:

```powershell
python -m prompt_experiment.output_format.llm_extraction --protocol PPP --model qwen3.5:9b --profile default --output-control ollama_json_output --connection auto
```

#### 3.Process extraction responses:

```powershell
python -m prompt_experiment.output_format.process_extraction_responses
```

#### 4.Generate combination prompts:

```powershell
python -m prompt_experiment.output_format.generate_combination_prompts
```

#### 5.Run LLM combination:

```powershell
python -m prompt_experiment.output_format.llm_combination --protocol PPP --model qwen3.5:9b --profile default --output-control ollama_json_output --connection auto
```

#### 6.Extract final FSMs:

```powershell
python -m prompt_experiment.output_format.extract_final_fsms
```

#### 7.Evaluate the final FSMs:

```powershell
python -m prompt_experiment.output_format.run_evaluation
```

Show the shared command line options:

```powershell
python -m prompt_experiment.output_format.llm_extraction --help
```

The LLM experiment commands support these options:

- `--protocol`: Select one protocol or `all`.
- `--model`: Select an Ollama model or `all`.
- `--profile`: Select a model profile, `default`, or `all`.
- `--output-control`: Select a JSON output control method or `all`.
- `--connection`: Use a local or remote Ollama server.

Use `default` to automatically select a profile supported by the selected model.

Do not omit the selection options for a quick test. The default LLM settings select all protocols, models, and output control methods.

Generated files are saved in `prompt_experiment/outputs/`.


### Compare PSMBench and the local Ollama baseline

Run the new PSMBench evaluation and the local baseline evaluation first.

```powershell
python -m psmbench_local_baseline.analyze_psmbench_saved_vs_local_ollama_results
```

The summary is saved in `psmbench_local_baseline/outputs/psmbench_saved_vs_local_ollama_model_summary.csv`.


## Experiment Configuration

### Protocol

Available protocols:

`BGP`, `DCCP`, `DHCP`, `FTP`, `IMAP`, `MQTT`, `NNTP`, `POP3`, `PPP`, `PPTP`, `RTSP`, `SIP`, `SMTP`, and `TCP`.

The local baseline requires `--protocol`.

The prompt output control experiment uses `all` by default.

Quick example: `PPP`


### Model

Available models:

#### Small Models

- `qwen3.5:9b`
- `gemma3:12b`

#### Medium Models

- `qwen3.5:27b`
- `gemma3:27b`
- `mistral-small3.1:24b`
- `qwq:32b`

The local baseline requires `--model`.

The prompt output control experiment uses `all` by default.

Quick example: `qwen3.5:9b`


### Profile

The profile option is used by the prompt output control experiment.

- `default`: Use the default profile supported by the selected model.
- `qwen-no-think`: Run a Qwen model without thinking.
- `qwen-think`: Run a supported Qwen model with thinking.
- `gemma-mistral-no-think`: Run Gemma or Mistral without thinking.
- `qwq-reasoning`: Use the intrinsic QwQ reasoning mode.
- `all`: Run all profiles supported by the selected model.

Default: `default`

[View the Model Profile configuration](config/models/model_profiles.py)


### Output Control

The output control option is used by the prompt output control experiment.

- `tagged_json_output`: Ask the model to return JSON inside tags.
- `ollama_json_output`: Use the Ollama JSON output mode.
- `ollama_json_schema_output`: Use an Ollama JSON schema.
- `all`: Run all output control methods.

Default: `all`


### Connection

- `local`: Use local Ollama.
- `remote`: Use the remote Ollama server defined in `.env`.
- `auto`: Try local Ollama first. If the local connection fails, try the remote Ollama server.

Default: `auto`


## Data Storage Directory

Generated local baseline files are saved in `psmbench_local_baseline/outputs/`.

Generated prompt experiment files are saved in `prompt_experiment/outputs/`.

PSMBench evaluation results and saved experiment results are stored in `output_data/`.


## PSMBench

PSMBench is a third-party project. It is not my original work.

- Project: [RFC_PSM_Benchmark](https://github.com/Zilinlin/RFC_PSM_Benchmark)
- Authors: Zilin Shen, Xinyu Luo, Imtiaz Karim, and Elisa Bertino
- License: Apache License 2.0

The original license is kept in `RFC_PSM_Benchmark-main/LICENSE`.


### PSMBench Evaluation Results

The generated CSV files can be viewed here: [PSMBench Evaluation Results](output_data/)