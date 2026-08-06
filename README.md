# Extraction of Protocol State Machines from RFCs using local LLMs

## Project Description

This project selects useful sections from RFC documents before sending them to a large language model (LLM).

This project uses PSMBench data and runs local LLMs with Ollama.

## Project Structure

- `config/`: protocol, model, profile, output-format, Ollama, and path configuration.
- `rfc/`: rfc types, roadling and related functions.
- `utils/`: shared helper functions.
- `method_1_section_selection/`: section selection, prompt generation, and LLM experiments.
- `method_2_long_section_splitting/`: experimental long-section splitting method; **currently under development.**
- `evaluation/`: PSM validation, PSMBench-based evaluation, and CSV summary generation.
- `PSMBench/`: third-party benchmark data and code.

## Setup

Python 3.11 or a newer version is recommended.

Install the main dependency:

```powershell
pip install -r requirements.txt
```

Copy `.env.example` to `.env`, and then set the local or remote Ollama URL.

## Run the Project

Run all commands from the project root folder.

### Method 1 section_selection

#### 1.Select RFC sections:

```powershell
python -m method_1_section_selection.hybrid_section_selection
```

#### 2.Generate LLM prompts:

```powershell
python -m method_1_section_selection.generate_llm_prompts
```

#### 3.Run LLM extration experiment 

Run a quick test:
```powershell
python -m method_1_section_selection.run_llm_extraction --protocol POP3 --max-sections 1
```

Run a complete experiment:

```powershell
python -m method_1_section_selection.run_llm_extraction --protocol POP3 --scoring-method keyword_density --input-version hybrid_high --model qwen3.5:9b --profile P0 --connection auto --output-format F0 --seed 42 --max-sections all
```

Show the LLM experiment command line options:

```powershell
python -m method_1_section_selection.run_llm_extraction --help
```
The program supports these options:
- `--protocol`: Select a protocol, such as `POP3` or `TCP`.
- `--scoring-method`: Select a method for scoring RFC sections.
- `--input-version`: Select which RFC sections are used.
- `--model`: Select an Ollama model.
- `--profile`: Select the model parameter settings.
- `--connection`: Use a local or remote Ollama server.
- `--output-format`: Select the JSON output method.
- `--seed`: Set the random seed.
- `--max-sections`: Select how many RFC sections are processed.

#### 4.Evaluate completed Method 1 experiments
```powershell
python -m method_1_section_selection.run_evaluation
```


## Experiment Configuration
### Protocol
Available protocols:
`BGP`, `DCCP`, `DHCP`, `FTP`, `IMAP`, `MQTT`, `NNTP`, `POP3`, `PPP`, `PPTP`, `RTSP`, `SIP`, `SMTP`, and `TCP`.

Default: `POP3`

### Scoring Method
- `legacy_count`: Uses the total number of weighted keywords.
- `keyword_density`: Calculates the keyword score for every 1000 words.

Default: `keyword_density`

### Input Versions
- `baseline_all`: Use all RFC sections.
- `hybrid_high`: Use only high priority sections.
- `hybrid_high_medium`: Use high and medium priority sections.

Default: `hybrid_high`

### Model

Available models:
##### Small Models
- `qwen3.5:9b`, `ministral-3:8b`, `llama3.1:8b`, `gemma3:12b`, `deepseek-r1:8b`

##### Medium Models
- `qwen3.5:27b`, `qwen3.5:35b`, `mistral-small3.2:24b`, `gemma3:27b`, `deepseek-r1:32b`, `gpt-oss:20b`

##### Large Models
- `llama3.3:70b`, `deepseek-r1:70b`, `qwen3-next:80b-a3b-instruct-q4_K_M`

##### Extra Large Models
- `qwen3.5:122b`, `gpt-oss:120b`

Default: `qwen3.5:9b`

### Profile
- `default`: Use the default settings of the selected model.
- `P0`: Basic settings.
- `P1`: Use a larger context and output limit.
- `P2`: Use a small amount of randomness to test result stability.
- `P3`: Enable thinking mode.
- `P4-low`: Use low reasoning for GPT-OSS models.
- `P4-medium`: Use medium reasoning for GPT-OSS models.

[View the Model Profile configuration](config/model_profiles.py)

### Connection
- `local`: Use local Ollama.
- `remote`: Use the remote Ollama server defined in `.env`.
- `auto`: Try local Ollama first. If the local connection fails, try the remote Ollama server.

Default: `auto`

### Output Format
- `F0`: Use the original PSMBench prompt and output format.
- `F1`: Ask Ollama to return valid JSON.
- `F2`: Ask Ollama to return JSON with the required structure.

[View the output formats configuration](config/output_formats.py)

### Seed
Using the same seed makes experiments easier to repeat.

Default: `42`

### Max Sections
Use `--max-sections 1` for a quick test.

Use `--max-sections all` to process all selected sections.

Default: `1`



## Data Storage Directory
Generated files are saved in `method_1_section_selection/outputs/`. 

## PSMBench

PSMBench is a third-party project. It is not my original work.

- Project: [RFC_PSM_Benchmark](https://github.com/Zilinlin/RFC_PSM_Benchmark)
- Authors: Zilin Shen, Xinyu Luo, Imtiaz Karim, and Elisa Bertino
- License: Apache License 2.0

The original license is kept in `PSMBench/LICENSE`.
