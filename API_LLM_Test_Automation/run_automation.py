#!/usr/bin/env python3
"""
File LLM Automation Tool - Single Settings File Runner
Reads all settings from settings.txt and runs the automation
"""

import os
import subprocess
import sys
from pathlib import Path

def read_settings():
    """Read settings from settings.txt file with multi-line PROMPT support"""
    settings = {}
    try:
        with open("settings.txt", 'r', encoding='utf-8') as f:
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
        print("Error: settings.txt not found!")
        print("Please create settings.txt with your settings")
        return None
    except Exception as e:
        print(f"Error reading settings.txt: {str(e)}")
        return None

def main():
    print("File LLM Automation Tool - Settings Runner")
    print("=" * 45)
    
    # Read settings
    settings = read_settings()
    if not settings:
        return
    
    # Get required settings
    input_folders_str = settings.get('INPUT_FOLDERS', '')
    output_base_folder = settings.get('OUTPUT_BASE_FOLDER', '')
    prompt = settings.get('PROMPT', '')
    model = settings.get('MODEL', 'gpt-3.5-turbo')
    runs_per_combination = int(settings.get('RUNS_PER_COMBINATION', 1))
    prompt_identifier = settings.get('PROMPT_IDENTIFIER', '19')
    
    # Parse input folders
    input_folders = [folder.strip() for folder in input_folders_str.split(',') if folder.strip()]
    
    # Validate settings
    if not input_folders:
        print("Error: INPUT_FOLDERS not specified in settings.txt")
        return
    
    if not output_base_folder:
        print("Error: OUTPUT_BASE_FOLDER not specified in settings.txt")
        return
    
    if not prompt:
        print("Error: API_PROMPT not specified in settings.txt")
        return
    
    # Check if input folders exist
    for input_folder in input_folders:
        if not os.path.exists(input_folder):
            print(f"Error: Input folder '{input_folder}' does not exist!")
            print("Please check the path in settings.txt")
            return
    
    # Create output base folder if it doesn't exist
    os.makedirs(output_base_folder, exist_ok=True)
    
    print(f"Input Folders: {', '.join(input_folders)}")
    print(f"Output Base Folder: {output_base_folder}")
    print(f"Model: {model}")
    print(f"Runs per combination: {runs_per_combination}")
    print(f"Prompt ID: {prompt_identifier}")
    print(f"Prompt: {prompt[:100]}...")
    print("-" * 45)
    
    # Process each input folder
    for run_num in range(runs_per_combination):
        print(f"\nRun {run_num + 1}/{runs_per_combination}")
        print("=" * 50)
        
        for input_folder in input_folders:
            # Create output folder for this combination matching local LLM pattern
            folder_path = Path(input_folder)
            parent_folder = folder_path.parent.name  # Conversion or Drop_off
            format_type = folder_path.name  # JSON or CSV
            
            # Map parent folder to CO/DO
            if parent_folder.lower() == 'conversion':
                prefix = 'CO'
            elif parent_folder.lower() == 'drop_off':
                prefix = 'DO'
            else:
                prefix = parent_folder.upper()
            
            # Replace colons in model name for Windows compatibility
            model_name = model.replace(':', '-')
            
            # Create proper naming pattern: CO_JSON_ANCHORED_gpt-4o-mini_prompt18_run1
            output_folder = os.path.join(output_base_folder, f"{prefix}_{format_type}_ANCHORED_{model_name}_prompt{prompt_identifier}_run{run_num + 1}")
            
            os.makedirs(output_folder, exist_ok=True)
            
            print(f"\nProcessing: {prefix}_{format_type}")
            print(f"Output: {output_folder}")
            
            # Update config.json with the output folder and model
            try:
                import json
                with open("config.json", 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                config['output_directory'] = output_folder
                config['model'] = model
                
                with open("config.json", 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2)
                
            except Exception as e:
                print(f"Warning: Could not update config.json: {e}")
            
            # Run the automation tool
            try:
                cmd = [
                    sys.executable, 
                    "file_llm_automation.py",
                    "--directory", input_folder,
                    "--prompt", prompt
                ]
                
                print("Starting automation...")
                result = subprocess.run(cmd, check=True)
                print("[OK] Automation completed successfully!")
                print(f"Results saved to: {output_folder}")
                
            except subprocess.CalledProcessError as e:
                print(f"[ERROR] Error running automation: {e}")
            except Exception as e:
                print(f"[ERROR] Unexpected error: {e}")
    
    print(f"\nAll processing completed!")
    print(f"Results saved to: {output_base_folder}")

if __name__ == "__main__":
    main()
