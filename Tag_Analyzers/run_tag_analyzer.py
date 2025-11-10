#!/usr/bin/env python3
"""
Simple script to run the Tag Analyzer using tag_settings.txt
"""

import os
import subprocess
import sys
from pathlib import Path

def read_settings():
    """Read settings from tag_settings.txt file"""
    settings = {}
    
    try:
        with open("tag_settings.txt", 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):  # Skip empty lines and comments
                    if '=' in line:
                        key, value = line.split('=', 1)
                        settings[key.strip()] = value.strip()
        
        return settings
    except FileNotFoundError:
        print("Error: tag_settings.txt not found!")
        print("Please create tag_settings.txt with your settings")
        return None
    except Exception as e:
        print(f"Error reading tag_settings.txt: {str(e)}")
        return None

def main():
    print("Tag Analyzer - Easy Runner")
    print("=" * 30)
    
    # Read settings
    settings = read_settings()
    if not settings:
        return
    
    # Get required settings
    input_folder = settings.get('INPUT_FOLDER', '')
    output_file = settings.get('OUTPUT_FILE', 'tag_analysis_results.xlsx')
    tag_pattern = settings.get('TAG_PATTERN', 'Tag: Drop-Off,Conversion')
    
    # Validate settings
    if not input_folder:
        print("Error: INPUT_FOLDER not specified in tag_settings.txt")
        return
    
    # Check if input folder exists
    if not os.path.exists(input_folder):
        print(f"Error: Input folder '{input_folder}' does not exist!")
        print("Please check the path in tag_settings.txt")
        return
    
    print(f"Input Folder: {input_folder}")
    print(f"Output File: {output_file}")
    print(f"Tag Pattern: {tag_pattern}")
    print("-" * 30)
    
    # Run the tag analyzer
    try:
        cmd = [
            sys.executable, 
            "tag_analyzer.py",
            "--directory", input_folder,
            "--output", output_file,
            "--tag", tag_pattern
        ]
        
        print("Starting tag analysis...")
        result = subprocess.run(cmd, check=True)
        print("Tag analysis completed successfully!")
        
    except subprocess.CalledProcessError as e:
        print(f"Error running tag analyzer: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()
