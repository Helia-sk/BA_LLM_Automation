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

                if key == 'PROMPT':
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
    input_folder = settings.get('INPUT_FOLDER', '')
    output_folder = settings.get('OUTPUT_FOLDER', '')
    prompt = settings.get('PROMPT', '')
    model = settings.get('MODEL', 'gpt-3.5-turbo')
    
    # Validate settings
    if not input_folder:
        print("Error: INPUT_FOLDER not specified in settings.txt")
        return
    
    if not output_folder:
        print("Error: OUTPUT_FOLDER not specified in settings.txt")
        return
    
    if not prompt:
        print("Error: PROMPT not specified in settings.txt")
        return
    
    # Check if input folder exists
    if not os.path.exists(input_folder):
        print(f"Error: Input folder '{input_folder}' does not exist!")
        print("Please check the path in settings.txt")
        return
    
    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    
    print(f"Input Folder: {input_folder}")
    print(f"Output Folder: {output_folder}")
    print(f"Model: {model}")
    print(f"Prompt: {prompt[:100]}...")
    print("-" * 45)
    
    # Update config.json with the output folder and model
    try:
        import json
        with open("config.json", 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        config['output_directory'] = output_folder
        config['model'] = model
        
        with open("config.json", 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
        
        print("Updated config.json with output folder and model")
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
        print("Automation completed successfully!")
        print(f"Results saved to: {output_folder}")
        
    except subprocess.CalledProcessError as e:
        print(f"Error running automation: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()
