# Evaluating Local Large Language Models for Protocol State Machine Extraction from RFCs

## Project Description

This project investigates how well local large language models can extract Protocol State Machines (PSMs) from RFC documents. It uses the fourteen protocols provided by PSMBench and runs local models through Ollama.

The project contains four main parts:

1. A local reproduction of the original PSMBench extraction workflow.
2. A comparison of three JSON output control methods.
3. A comparison of different RFC input preparation methods.
4. A comparison of the original PSMBench evaluator and a modified evaluator
   that uses one-to-one matching.

The pipeline prepares RFC inputs, generates extraction prompts, stores raw model responses, parses partial PSMs, combines partial results, extracts final PSMs, and evaluates them against the reference PSMs.


## Project Structure

- `config/`: protocol paths, model settings, profiles, output formats, Ollama connections, and generated-data paths.
- `rfc/`: RFC data types and loading functions.
- `utils/`: shared file, Ollama request, response parsing, and text-statistics functions.
- `research_pipeline/`: shared prompt construction, model selection, JSON Schema, and response-processing functions.
- `evaluation/`: original PSMBench evaluation, modified one-to-one evaluation, and evaluator comparison.
- `psmbench_local_baseline/`: local reproduction of the original PSMBench extraction and combination workflow.
- `prompt_experiment/`: the three output-control experiments.
- `split_experiment/`: fixed-token, recursive-section, referenced-context, and whole-document input experiments.
- `RFC_PSM_Benchmark-main/`: retained PSMBench code, RFC inputs, ground-truth PSMs, and published model outputs required by this project.
- `output_data/`: saved final PSMs, evaluation CSV files, and experiment summaries included with the project.

## Setup

Python 3.11 or a newer version is recommended.

Install the dependencies:

```powershell
pip install -r requirements.txt
```

Copy `.env.example` to `.env`, and then set the local or remote Ollama URL.

For a local Ollama test, pull the model used by the quick examples:

```powershell
ollama pull qwen3.5:9b
```

Make sure Ollama is running before starting an LLM experiment.

## Run the Project

Run all commands from the project root folder.

### Original PSMBench evaluation

These commands evaluate the saved FSM files in `RFC_PSM_Benchmark-main/fsm/`.

Ollama is not required for these commands.

The first evaluation run may download the `all-MiniLM-L6-v2` sentence-transformer model.

#### 1. Run the original PSMBench evaluation

```powershell
python -m evaluation.run_original_psmbench_evaluation
```

The generated CSV files are saved in `output_data/PSMBench_original_evaluation_results/`.

#### 2. Run the new one-to-one PSMBench evaluation

```powershell
python -m evaluation.run_original_psmbench_new_evaluation
```

The generated CSV files are saved in `output_data/PSMBench_new_evaluation_results/`.

#### 3. Compare the two evaluation methods

Run Steps 1 and 2 first.

```powershell
python -m evaluation.analyze_evaluation_results
```

The summary is saved in `output_data/psmbench_original_vs_new_evaluation_summary.csv`.

These evaluation scripts do not have command line options. The protocols, models, and matching threshold are defined in the Python files.


### PSMBench local Ollama baseline

Run the following commands in order.

The quick example uses `PPP` because it contains only 6 RFC segments.

#### 1. Generate the original PSMBench extraction prompts

```powershell
python -m psmbench_local_baseline.generate_extraction_prompts
```

#### 2. Run a quick extraction test

```powershell
python -m psmbench_local_baseline.llm_extraction --protocol PPP --model qwen3.5:9b --connection auto
```

#### 3. Process extraction responses

```powershell
python -m psmbench_local_baseline.process_extraction_responses
```

#### 4. Generate combination prompts

```powershell
python -m psmbench_local_baseline.generate_combination_prompts
```

#### 5. Run LLM combination

```powershell
python -m psmbench_local_baseline.llm_combination
```

#### 6. Extract final FSMs

```powershell
python -m psmbench_local_baseline.extract_final_fsms
```

#### 7. Evaluate the final FSMs

```powershell
python -m psmbench_local_baseline.run_evaluation
```

Show the baseline extraction command line options:

```powershell
python -m psmbench_local_baseline.llm_extraction --help
```

The extraction stage supports these options:

- `--protocol`: Select one protocol or `all`.
- `--model`: Select an Ollama model or `all`.
- `--connection`: Use a local or remote Ollama server.
- `--thinking`: Enable optional thinking for supported Qwen models.

The complete baseline contains eight model settings across 14 protocols: the default profiles of all six models, together with the thinking profiles of `qwen3.5:9b` and `qwen3.5:27b`.

The combination command has no selection options. It scans the saved combination prompts and runs the supported model conditions represented by those prompt names.

Generated files are saved in `psmbench_local_baseline/outputs/`.


### Prompt output control experiment

This experiment compares different methods for controlling the LLM JSON output.

Run the following commands in order.

The quick example uses one protocol, one model, and one output control method.

#### 1. Generate extraction prompts

```powershell
python -m prompt_experiment.output_format.generate_extraction_prompts --protocol PPP --output-control ollama_json_output
```

#### 2. Run LLM extraction

```powershell
python -m prompt_experiment.output_format.llm_extraction --protocol PPP --model qwen3.5:9b --profile default --output-control ollama_json_output --connection auto
```

#### 3. Process extraction responses

```powershell
python -m prompt_experiment.output_format.process_extraction_responses
```

#### 4. Generate combination prompts

```powershell
python -m prompt_experiment.output_format.generate_combination_prompts
```

#### 5. Run LLM combination

```powershell
python -m prompt_experiment.output_format.llm_combination --protocol PPP --model qwen3.5:9b --profile default --output-control ollama_json_output --connection auto
```

#### 6. Extract final FSMs

```powershell
python -m prompt_experiment.output_format.extract_final_fsms
```

#### 7. Evaluate the final FSMs

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

The dissertation comparison uses five non-thinking model settings and excludes QwQ, giving 70 cases for each output method and 210 cases in total.

Generated files are saved in `prompt_experiment/outputs/`.


### RFC input experiments

These experiments add four alternative RFC input methods to the original PSMBench segments. The dissertation's main four-method comparison uses the original PSMBench segments, fixed token splitting, recursive section splitting, and referenced context splitting. Whole document input is an additional analysis. The quick examples use `PPP` and `qwen3.5:9b`.

#### Fixed token splitting

This method joins the available RFC blocks and creates segments of at most 5,000 tokens without overlap.

```powershell
python -m split_experiment.fixed_token_splitting.generate_fixed_token_segments --protocol PPP
python -m split_experiment.fixed_token_splitting.generate_extraction_prompts --protocol PPP
python -m split_experiment.fixed_token_splitting.llm_extraction --protocol PPP --model qwen3.5:9b --profile default --connection auto
python -m split_experiment.fixed_token_splitting.process_extraction_responses
python -m split_experiment.fixed_token_splitting.generate_combination_prompts
python -m split_experiment.fixed_token_splitting.llm_combination --protocol PPP --model qwen3.5:9b --profile default --connection auto
python -m split_experiment.fixed_token_splitting.extract_final_fsms
python -m split_experiment.fixed_token_splitting.run_evaluation
```

#### Recursive section splitting

This method splits long blocks at numbered child-section headings where possible. The 5,000-token value is a splitting threshold, so a block may remain longer when no suitable heading exists.

```powershell
python -m split_experiment.recursive_section_splitting.generate_recursive_section_segments --protocol PPP
python -m split_experiment.recursive_section_splitting.generate_extraction_prompts --protocol PPP
python -m split_experiment.recursive_section_splitting.llm_extraction --protocol PPP --model qwen3.5:9b --profile default --connection auto
python -m split_experiment.recursive_section_splitting.process_extraction_responses
python -m split_experiment.recursive_section_splitting.generate_combination_prompts
python -m split_experiment.recursive_section_splitting.llm_combination --protocol PPP --model qwen3.5:9b --profile default --connection auto
python -m split_experiment.recursive_section_splitting.extract_final_fsms
python -m split_experiment.recursive_section_splitting.run_evaluation
```

#### Referenced context splitting

This method starts with the recursive section segments and adds directly referenced sections from the same RFC. Generate the recursive section segments first.

```powershell
python -m split_experiment.recursive_section_splitting.generate_recursive_section_segments --protocol PPP
python -m split_experiment.referenced_context_splitting.generate_referenced_context_segments --protocol PPP
python -m split_experiment.referenced_context_splitting.generate_extraction_prompts --protocol PPP
python -m split_experiment.referenced_context_splitting.llm_extraction --protocol PPP --model qwen3.5:9b --profile default --connection auto
python -m split_experiment.referenced_context_splitting.process_extraction_responses
python -m split_experiment.referenced_context_splitting.generate_combination_prompts
python -m split_experiment.referenced_context_splitting.llm_combination --protocol PPP --model qwen3.5:9b --profile default --connection auto
python -m split_experiment.referenced_context_splitting.extract_final_fsms
python -m split_experiment.referenced_context_splitting.run_evaluation
```

#### Whole document input

This method joins all available PSMBench RFC blocks into one input. It uses one extraction request and does not use a combination stage. Inputs that exceed the model input budget are skipped and recorded in `manifests/context_exclusions.json`.

```powershell
python -m split_experiment.whole_document_reference.generate_whole_rfc_documents --protocol PPP
python -m split_experiment.whole_document_reference.generate_extraction_prompts --protocol PPP
python -m split_experiment.whole_document_reference.llm_extraction --protocol PPP --model qwen3.5:9b --profile default --connection auto
python -m split_experiment.whole_document_reference.extract_final_fsms
python -m split_experiment.whole_document_reference.run_evaluation
```

Generated files are saved under `split_experiment/outputs/`.


### Compare PSMBench and the local Ollama baseline

Run the new PSMBench evaluation and the local baseline evaluation first.

```powershell
python -m psmbench_local_baseline.analyze_psmbench_saved_vs_local_ollama_results
```

The summary is saved in `psmbench_local_baseline/outputs/psmbench_saved_vs_local_ollama_model_summary.csv`.


### Summarize the RFC input experiments

Run this command after the required experiment outputs are available:

```powershell
python -m split_experiment.analyze_split_experiment_results
```

It saves `split_experiment_condition_results.csv`, `split_experiment_evaluation_summary.csv`, and `split_experiment_model_output_summary.csv` in `output_data/`.

The non-thinking summary uses the 64 conditions shared by the original blocks, fixed token, recursive section, referenced context, and whole document methods. The thinking rows compare fixed token, recursive section, and whole document results. Referenced context does not have matching thinking results.


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

The profile option is used by the prompt output control and RFC input experiments.

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

The RFC input experiments use `ollama_json_schema_output`.


### Connection

- `local`: Use local Ollama.
- `remote`: Use the remote Ollama server defined in `.env`.
- `auto`: Try local Ollama first. If the local connection fails, try the remote Ollama server.

Default: `auto`


## Data Storage Directory

Generated local baseline files are saved in `psmbench_local_baseline/outputs/`.

Generated prompt experiment files are saved in `prompt_experiment/outputs/`.

Generated RFC input experiment files are saved in `split_experiment/outputs/`.

PSMBench evaluation results and saved experiment results are stored in `output_data/`.

The saved dissertation results contain 112 local baseline FSMs, 210 repaired output control FSMs, 112 fixed token FSMs, 112 recursive section FSMs, 70 referenced context FSMs, and 92 whole document FSMs. The original 210 output control FSMs are retained separately for comparison.

The generated `outputs/` directories are excluded by `.gitignore`. The `output_data/` directory contains the final FSMs and evaluation CSV files included with the project, but not every raw Ollama response.


## PSMBench

PSMBench is a third-party project. It is not my original work.

- Project: [RFC_PSM_Benchmark](https://github.com/Zilinlin/RFC_PSM_Benchmark)
- Authors: Zilin Shen, Xinyu Luo, Imtiaz Karim, and Elisa Bertino
- Revision: `df0bce6dcf769f976ff02b0743c96e5a1e84720b`
- License: Apache License 2.0

Only the PSMBench files required by this project are included in `RFC_PSM_Benchmark-main/`. These include the evaluation and prompt-generation code, the fourteen protocol segment files, the ground-truth state machines, and the published FSM results. Unused upstream API scripts, preprocessing scripts, raw RFC files, and generated figures are not included.

The retained upstream source files have not been modified. For Windows compatibility, 28 FSM filenames containing `:` were renamed to use `_`. Their JSON contents were not changed.

The original Apache License 2.0 is retained in `RFC_PSM_Benchmark-main/LICENSE`.


### PSMBench Evaluation Results

The generated CSV files can be viewed here: [PSMBench Evaluation Results](output_data/)
