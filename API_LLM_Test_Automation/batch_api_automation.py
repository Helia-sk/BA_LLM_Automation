#!/usr/bin/env python3
"""
Batch API LLM Automation Tool
Processes multiple subfolders automatically with different API models
"""

import os
import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime

def read_settings(settings_file="batch_api_settings.txt"):
    """Read batch settings from file with multi-line PROMPT support"""
    settings = {}
    try:
        with open(settings_file, 'r', encoding='utf-8') as f:
            lines = [ln.rstrip('\n') for ln in f]

        i = 0
        while i < len(lines):
            raw = lines[i]
            line = raw.strip()
            i += 1
            if not line or line.startswith('#'):
                continue

            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()

                if key in ['API_PROMPT', 'PROMPT']:
                    prompt_lines = [value]
                    # Collect continuation lines until we hit a line that starts with a key=value pattern
                    while i < len(lines):
                        next_line = lines[i]
                        # Check if this line looks like a new setting (KEY=VALUE at start of line)
                        stripped = next_line.strip()
                        if stripped and '=' in stripped and not stripped.startswith(' ') and not stripped.startswith('\t') and not stripped.startswith('-') and not stripped.startswith('*'):
                            # This looks like a new key=value setting, stop collecting
                            break
                        else:
                            # This is part of the prompt, add it
                            prompt_lines.append(next_line)
                            i += 1
                    settings['PROMPT'] = '\n'.join(prompt_lines).strip()
                else:
                    settings[key] = value

        return settings
    except FileNotFoundError:
        print(f"Error: {settings_file} not found!")
        return None
    except Exception as e:
        print(f"Error reading {settings_file}: {str(e)}")
        return None

def create_config_for_model(model_name, output_base_dir, api_key_type, api_key_value):
    """Create config.json for specific model"""
    config = {
        "file_extensions": [".txt", ".py", ".js", ".md", ".json", ".csv"],
        "output_directory": "",
        "naming_pattern": "{original_name}_{model}",
        "model": model_name,
        "max_tokens": 2000,
        "temperature": 0.7,
        "delay_between_files": 1,
        "openai_api_key": "",
        "anthropic_api_key": ""
    }
    
    # Set the appropriate API key
    if api_key_type == "openai":
        config["openai_api_key"] = api_key_value
    elif api_key_type == "anthropic":
        config["anthropic_api_key"] = api_key_value
    
    return config

def run_single_automation(input_path, model_name, prompt, api_key_type, api_key_value, output_dir):
    """Run automation for a single input folder"""
    print(f"Processing: {input_path.name}")
    print("-" * 50)
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create config for this model
    config = create_config_for_model(model_name, str(output_dir), api_key_type, api_key_value)
    config["output_directory"] = str(output_dir)
    
    # Save config
    config_file = output_dir / "config.json"
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)
    
    # Run the automation
    try:
        cmd = [
            sys.executable,
            "file_llm_automation.py",
            "--directory", str(input_path),
            "--prompt", prompt,
            "--config", str(config_file)
        ]
        
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"[OK] Successfully processed {input_path.name}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Error processing {input_path.name}: {e}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        return False
    except Exception as e:
        print(f"[ERROR] Unexpected error processing {input_path.name}: {e}")
        return False

def batch_process_folders(input_folders, models, prompt, api_key_type, api_key_value, output_base_dir, runs_per_combination, prompt_identifier):
    """Process all input folders with multiple models"""
    # Create output base directory
    output_base_path = Path(output_base_dir)
    output_base_path.mkdir(parents=True, exist_ok=True)
    
    # Check if input folders exist
    for input_folder in input_folders:
        if not Path(input_folder).exists():
            print(f"Error: Input folder '{input_folder}' does not exist!")
            return
    
    print(f"Found {len(input_folders)} input folders to process")
    print(f"Models to test: {', '.join(models)}")
    print(f"Runs per combination: {runs_per_combination}")
    print("=" * 60)
    
    # Process each input folder with each model
    total_combinations = len(input_folders) * len(models) * runs_per_combination
    current_combination = 0
    successful_runs = 0
    failed_runs = 0
    
    for run_num in range(runs_per_combination):
        print(f"\nRun {run_num + 1}/{runs_per_combination}")
        print("=" * 60)
        
        for input_folder in input_folders:
            input_path = Path(input_folder)
            parent_folder = input_path.parent.name  # Conversion or Drop_off
            format_type = input_path.name  # JSON or CSV
            
            # Map parent folder to CO/DO
            if parent_folder.lower() == 'conversion':
                prefix = 'CO'
            elif parent_folder.lower() == 'drop_off':
                prefix = 'DO'
            else:
                prefix = parent_folder.upper()
            
            print(f"\nProcessing folder: {prefix}_{format_type}")
            print("-" * 40)
            
            for model in models:
                current_combination += 1
                print(f"\nModel {current_combination}/{total_combinations}: {model}")
                print("-" * 30)
                
                # Create output folder for this combination matching local LLM pattern
                model_name = model.replace(':', '-')
                # Create proper naming pattern: CO_JSON_ANCHORED_gpt-4o-mini_prompt18_run1
                output_folder = output_base_path / f"{prefix}_{format_type}_ANCHORED_{model_name}_prompt{prompt_identifier}_run{run_num + 1}"
                
                success = run_single_automation(
                    input_path, 
                    model, 
                    prompt, 
                    api_key_type, 
                    api_key_value, 
                    output_folder
                )
                
                if success:
                    successful_runs += 1
                else:
                    failed_runs += 1
    
    # Summary
    print("\n" + "=" * 60)
    print("BATCH PROCESSING SUMMARY")
    print("=" * 60)
    print(f"Total input folders: {len(input_folders)}")
    print(f"Total models: {len(models)}")
    print(f"Runs per combination: {runs_per_combination}")
    print(f"Total combinations: {total_combinations}")
    print(f"Successful runs: {successful_runs}")
    print(f"Failed runs: {failed_runs}")
    print(f"Success rate: {(successful_runs/total_combinations)*100:.1f}%")
    print(f"Results saved to: {output_base_path}")

def main():
    print("Batch API LLM Automation Tool")
    print("=" * 40)
    
    # Read settings
    settings = read_settings()
    if not settings:
        return
    
    # Get settings
    input_folders_str = settings.get('INPUT_FOLDERS', '')
    models_str = settings.get('MODELS', '')
    prompt = settings.get('PROMPT', '')
    api_key_type = settings.get('API_KEY_TYPE', 'openai')
    api_key_value = settings.get('API_KEY', '')
    output_base_dir = settings.get('OUTPUT_BASE_FOLDER', './batch_results')
    runs_per_combination = int(settings.get('RUNS_PER_COMBINATION', 1))
    prompt_identifier = settings.get('PROMPT_IDENTIFIER', '19')
    
    # Parse input folders and models
    input_folders = [folder.strip() for folder in input_folders_str.split(',') if folder.strip()]
    models = [model.strip() for model in models_str.split(',') if model.strip()]
    
    # Validate settings
    if not input_folders:
        print("Error: INPUT_FOLDERS not specified in batch_api_settings.txt")
        return
    
    if not models:
        print("Error: MODELS not specified in batch_api_settings.txt")
        return
    
    if not prompt:
        print("Error: API_PROMPT not specified in batch_api_settings.txt")
        return
    
    if not api_key_value:
        print("Error: API_KEY not specified in batch_api_settings.txt")
        return
    
    print(f"Input Folders: {', '.join(input_folders)}")
    print(f"Models: {', '.join(models)}")
    print(f"API Key Type: {api_key_type}")
    print(f"Output Base Directory: {output_base_dir}")
    print(f"Runs per combination: {runs_per_combination}")
    print(f"Prompt ID: {prompt_identifier}")
    print(f"Prompt: {prompt[:100]}...")
    print("-" * 40)
    
    # Confirm before starting
    response = input("Do you want to start batch processing? (y/N): ").strip().lower()
    if response != 'y':
        print("Batch processing cancelled.")
        return
    
    # Start batch processing
    batch_process_folders(input_folders, models, prompt, api_key_type, api_key_value, output_base_dir, runs_per_combination, prompt_identifier)

if __name__ == "__main__":
    main()
