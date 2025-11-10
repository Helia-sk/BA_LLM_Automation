API LLM Test Automation

This folder contains tools for automating file processing with various API-based LLM models (OpenAI, Anthropic, etc.).

Files Overview

Core Scripts
- file_llm_automation.py - Main automation script for processing files with API LLMs
- run_automation.py - Simple runner that reads settings from settings.txt
- run_with_files.py - Runner that reads folder path and prompt from text files
- batch_api_automation.py - Batch processor for multiple subfolders and models

Configuration Files
- config.json - Main configuration file with API keys and settings
- settings.txt - Simple settings file for single runs
- batch_api_settings.txt - Settings for batch processing multiple models

Batch Files
- run_api_automation.bat - Windows batch file to run single automation
- run_batch_api_automation.bat - Windows batch file to run batch automation

Quick Start

Single Model Processing
1. Edit settings.txt with your input folder, output folder, model, and prompt
2. Run: python run_automation.py or double-click run_api_automation.bat

Batch Processing (Multiple Models)
1. Edit batch_api_settings.txt with your settings
2. Run: python batch_api_automation.py or double-click run_batch_api_automation.bat

Configuration

API Keys
- Set your OpenAI API key in config.json or batch_api_settings.txt
- Set your Anthropic API key if using Claude models

Models Supported
- OpenAI: gpt-4o, gpt-4, gpt-3.5-turbo, etc.
- Anthropic: claude-3-sonnet-20240229, claude-3-haiku-20240307, etc.

Settings Files (Matching Local LLM Format)

settings.txt
# API LLM Experiment Configuration
RUNS_PER_COMBINATION=1
PROMPT_IDENTIFIER=19
MODEL=gpt-4o-mini
TIMEOUT=300
API_KEY_TYPE=openai

# Input/Output Combinations
INPUT_FOLDERS=path/to/Conversion/JSON,path/to/Conversion/CSV,path/to/Drop_off/JSON,path/to/Drop_off/CSV,path/to/CO/JSON,path/to/CO/CSV,path/to/DO/JSON,path/to/DO/CSV
OUTPUT_BASE_FOLDER=path/to/output/base
API_PROMPT="Your multi-line prompt here..."

batch_api_settings.txt
# Batch API LLM Experiment Configuration
RUNS_PER_COMBINATION=1
PROMPT_IDENTIFIER=19
MODELS=gpt-4o-mini,gpt-3.5-turbo,claude-3-sonnet-20240229
TIMEOUT=300
API_KEY_TYPE=openai
API_KEY=your-api-key-here

# Input/Output Combinations
INPUT_FOLDERS=path/to/Conversion/JSON,path/to/Conversion/CSV,path/to/Drop_off/JSON,path/to/Drop_off/CSV,path/to/CO/JSON,path/to/CO/CSV,path/to/DO/JSON,path/to/DO/CSV
OUTPUT_BASE_FOLDER=path/to/batch/results
API_PROMPT="Your multi-line prompt here..."

Features

Multi-API Support - OpenAI and Anthropic APIs
Batch Processing - Process multiple subfolders with multiple models
Flexible Configuration - JSON and text-based settings
Error Handling - Robust error handling and logging
Rate Limiting - Built-in delays to avoid API rate limits
Progress Tracking - Real-time progress updates

Usage Examples

Process a single folder with GPT-4o
python run_automation.py

Process multiple subfolders with multiple models
python batch_api_automation.py

Use with custom files
1. Create folder_path.txt with your folder path
2. Create prompt.txt with your prompt
3. Run: python run_with_files.py

Output

Results are saved with metadata including:
- Original file path
- Processing timestamp
- Model used
- Prompt used
- LLM response

Requirements

Python 3.7+
openai (for OpenAI models)
anthropic (for Anthropic models)
requests (for API calls)

Install with:
pip install openai anthropic requests
