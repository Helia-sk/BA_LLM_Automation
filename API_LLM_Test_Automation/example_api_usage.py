#!/usr/bin/env python3
"""
Example usage of the API LLM Automation Tool
"""

import os
import subprocess
import sys
from pathlib import Path

def example_single_run():
    """Example of running a single automation"""
    print("Example: Single API LLM Run")
    print("=" * 40)
    
    # Example settings (matching Local LLM format)
    settings_content = """# API LLM Experiment Configuration
RUNS_PER_COMBINATION=1
PROMPT_IDENTIFIER=19
MODEL=gpt-4o-mini
TIMEOUT=300
API_KEY_TYPE=openai

# Input/Output Combinations
INPUT_FOLDERS=C:/Users/helia/OneDrive/Uni/6th_Semester/BA/Dataset/Conversion/JSON,C:/Users/helia/OneDrive/Uni/6th_Semester/BA/Dataset/Conversion/CSV,C:/Users/helia/OneDrive/Uni/6th_Semester/BA/Dataset/Drop_off/JSON,C:/Users/helia/OneDrive/Uni/6th_Semester/BA/Dataset/Drop_off/CSV,C:/Users/helia/OneDrive/Uni/6th_Semester/BA/Dataset/CO/JSON,C:/Users/helia/OneDrive/Uni/6th_Semester/BA/Dataset/CO/CSV,C:/Users/helia/OneDrive/Uni/6th_Semester/BA/Dataset/DO/JSON,C:/Users/helia/OneDrive/Uni/6th_Semester/BA/Dataset/DO/CSV
OUTPUT_BASE_FOLDER=C:/Users/helia/OneDrive/Uni/6th_Semester/BA/Dataset/LLM_Results/API_Results
API_PROMPT="Analyze the following user session log and determine whether it represents a Conversion or a Drop-Off. Each core event (Login, Registration, Add to Cart, Place Order, etc.) counts as a Conversion if it was successfully completed at least once. If an event failed initially but was retried and completed successfully, it is still a Conversion. If a user started an event but never completed it successfully or stopped after a failed attempt, it is a Drop-Off. If at least one event was completed successfully and no unrecovered failures remain, classify it as Conversion. Format your response as follows:

Tag: Conversion || Drop-Off [Reason]

[Step 1]

[Step 2]

[Step 3] …" """
    
    # Write example settings
    with open("example_settings.txt", 'w', encoding='utf-8') as f:
        f.write(settings_content)
    
    print("Created example_settings.txt")
    print("To run: python run_automation.py")

def example_batch_run():
    """Example of running batch automation"""
    print("\nExample: Batch API LLM Run")
    print("=" * 40)
    
    # Example batch settings (matching Local LLM format)
    batch_settings_content = """# Batch API LLM Experiment Configuration
RUNS_PER_COMBINATION=1
PROMPT_IDENTIFIER=19
MODELS=gpt-4o-mini,gpt-3.5-turbo,claude-3-sonnet-20240229
TIMEOUT=300
API_KEY_TYPE=openai
API_KEY=your-api-key-here

# Input/Output Combinations
INPUT_FOLDERS=C:/Users/helia/OneDrive/Uni/6th_Semester/BA/Dataset/Conversion/JSON,C:/Users/helia/OneDrive/Uni/6th_Semester/BA/Dataset/Conversion/CSV,C:/Users/helia/OneDrive/Uni/6th_Semester/BA/Dataset/Drop_off/JSON,C:/Users/helia/OneDrive/Uni/6th_Semester/BA/Dataset/Drop_off/CSV,C:/Users/helia/OneDrive/Uni/6th_Semester/BA/Dataset/CO/JSON,C:/Users/helia/OneDrive/Uni/6th_Semester/BA/Dataset/CO/CSV,C:/Users/helia/OneDrive/Uni/6th_Semester/BA/Dataset/DO/JSON,C:/Users/helia/OneDrive/Uni/6th_Semester/BA/Dataset/DO/CSV
OUTPUT_BASE_FOLDER=C:/Users/helia/OneDrive/Uni/6th_Semester/BA/Dataset/LLM_Results/API_Batch_Results
API_PROMPT="Analyze the following user session log and determine whether it represents a Conversion or a Drop-Off. Each core event (Login, Registration, Add to Cart, Place Order, etc.) counts as a Conversion if it was successfully completed at least once. If an event failed initially but was retried and completed successfully, it is still a Conversion. If a user started an event but never completed it successfully or stopped after a failed attempt, it is a Drop-Off. If at least one event was completed successfully and no unrecovered failures remain, classify it as Conversion. Format your response as follows:

Tag: Conversion || Drop-Off [Reason]

[Step 1]

[Step 2]

[Step 3] …" """
    
    # Write example batch settings
    with open("example_batch_settings.txt", 'w', encoding='utf-8') as f:
        f.write(batch_settings_content)
    
    print("Created example_batch_settings.txt")
    print("To run: python batch_api_automation.py")

def main():
    print("API LLM Automation Tool - Examples")
    print("=" * 50)
    
    example_single_run()
    example_batch_run()
    
    print("\n" + "=" * 50)
    print("Examples created!")
    print("Remember to:")
    print("1. Update API keys in the settings files")
    print("2. Update folder paths to your actual directories")
    print("3. Run the appropriate script")

if __name__ == "__main__":
    main()
