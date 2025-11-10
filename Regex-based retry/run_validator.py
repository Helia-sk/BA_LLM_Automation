#!/usr/bin/env python3
"""
LLM Validator Runner - Reads settings and runs validation
"""

import os
import subprocess
import sys
from pathlib import Path

def read_settings():
    """Read settings from validator_settings.txt"""
    settings = {}
    try:
        with open("validator_settings.txt", 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    if '=' in line:
                        key, value = line.split('=', 1)
                        settings[key.strip()] = value.strip()
        return settings
    except FileNotFoundError:
        print("Error: validator_settings.txt not found!")
        return None
    except Exception as e:
        print(f"Error reading validator_settings.txt: {str(e)}")
        return None

def main():
    print("LLM Output Validator - Settings Runner")
    print("=" * 40)
    
    # Read settings
    settings = read_settings()
    if not settings:
        return
    
    # Get settings
    input_path = settings.get('INPUT_PATH', '')
    output_path = settings.get('OUTPUT_PATH', '')
    model = settings.get('MODEL', 'llama3.3:70b')
    temperature = float(settings.get('TEMPERATURE', '0.1'))
    top_p = float(settings.get('TOP_P', '0.2'))
    max_tokens = int(settings.get('MAX_TOKENS', '400'))
    max_retries = int(settings.get('MAX_RETRIES', '2'))
    test_mode = settings.get('TEST_MODE', 'false').lower() == 'true'
    timeout = int(settings.get('TIMEOUT', '300'))
    
    # Validate settings
    if not input_path:
        print("Error: INPUT_PATH not specified in validator_settings.txt")
        return
    
    if not output_path:
        print("Error: OUTPUT_PATH not specified in validator_settings.txt")
        return
    
    # Check if input exists
    if not os.path.exists(input_path):
        print(f"Error: Input path '{input_path}' does not exist!")
        return
    
    print(f"Input Path: {input_path}")
    print(f"Output Path: {output_path}")
    print(f"Model: {model}")
    print(f"Temperature: {temperature}")
    print(f"Top-p: {top_p}")
    print(f"Max Tokens: {max_tokens}")
    print(f"Max Retries: {max_retries}")
    print(f"Test Mode: {test_mode}")
    print(f"Timeout: {timeout}s")
    print("-" * 40)
    
    # Run validator
    try:
        cmd = [
            sys.executable,
            "llm_validator.py",
            "--input", input_path,
            "--output", output_path,
            "--model", model,
            "--temperature", str(temperature),
            "--top-p", str(top_p),
            "--max-tokens", str(max_tokens),
            "--max-retries", str(max_retries),
            "--timeout", str(timeout)
        ]
        
        if test_mode:
            cmd.append("--test-mode")
        
        print("Starting validation...")
        result = subprocess.run(cmd, check=True)
        print("Validation completed successfully!")
        
    except subprocess.CalledProcessError as e:
        print(f"Error running validator: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()
