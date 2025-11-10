#!/usr/bin/env python3
"""
Simple script to run the Text Concatenator using concatenator_settings.txt
"""

import os
import subprocess
import sys
from pathlib import Path

def read_settings():
    """Read settings from concatenator_settings.txt file"""
    settings = {}
    
    try:
        with open("concatenator_settings.txt", 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):  # Skip empty lines and comments
                    if '=' in line:
                        key, value = line.split('=', 1)
                        settings[key.strip()] = value.strip()
        
        return settings
    except FileNotFoundError:
        print("Error: concatenator_settings.txt not found!")
        print("Please create concatenator_settings.txt with your settings")
        return None
    except Exception as e:
        print(f"Error reading concatenator_settings.txt: {str(e)}")
        return None

def main():
    print("Text Concatenator - Easy Runner")
    print("=" * 35)
    
    # Read settings
    settings = read_settings()
    if not settings:
        return
    
    # Get required settings
    input_folder = settings.get('INPUT_FOLDER', '')
    output_filename = settings.get('OUTPUT_FILENAME', 'concatenated_text.txt')
    
    # Validate settings
    if not input_folder:
        print("Error: INPUT_FOLDER not specified in concatenator_settings.txt")
        return
    
    # Check if input folder exists
    if not os.path.exists(input_folder):
        print(f"Error: Input folder '{input_folder}' does not exist!")
        print("Please check the path in concatenator_settings.txt")
        return
    
    print(f"Input Folder: {input_folder}")
    print(f"Output Filename: {output_filename}")
    print("-" * 35)
    
    # Run the text concatenator
    try:
        cmd = [
            sys.executable, 
            "text_concatenator.py",
            "--folder", input_folder,
            "--output", output_filename
        ]
        
        print("Starting text concatenation...")
        result = subprocess.run(cmd, check=True)
        print("Text concatenation completed successfully!")
        
    except subprocess.CalledProcessError as e:
        print(f"Error running text concatenator: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()
