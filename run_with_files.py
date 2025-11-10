#!/usr/bin/env python3
"""
Simple script to run the File LLM Automation Tool using folder_path.txt and prompt.txt
"""

import os
import subprocess
import sys
from pathlib import Path

def read_file_content(filename):
    """Read content from a text file"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except FileNotFoundError:
        print(f"Error: {filename} not found!")
        return None
    except Exception as e:
        print(f"Error reading {filename}: {str(e)}")
        return None

def main():
    print("File LLM Automation Tool - Easy Runner")
    print("=" * 40)
    
    # Read folder path
    folder_path = read_file_content("folder_path.txt")
    if not folder_path:
        print("Please create folder_path.txt with your folder path")
        return
    
    # Read prompt
    prompt = read_file_content("prompt.txt")
    if not prompt:
        print("Please create prompt.txt with your prompt")
        return
    
    # Check if folder exists
    if not os.path.exists(folder_path):
        print(f"Error: Folder '{folder_path}' does not exist!")
        print("Please check the path in folder_path.txt")
        return
    
    print(f"Folder: {folder_path}")
    print(f"Prompt: {prompt}")
    print("-" * 40)
    
    # Run the automation tool
    try:
        cmd = [
            sys.executable, 
            "file_llm_automation.py",
            "--directory", folder_path,
            "--prompt", prompt
        ]
        
        print("Starting automation...")
        result = subprocess.run(cmd, check=True)
        print("Automation completed successfully!")
        
    except subprocess.CalledProcessError as e:
        print(f"Error running automation: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()
