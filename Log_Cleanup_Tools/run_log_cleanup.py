#!/usr/bin/env python3
"""
Log Cleanup Runner
Easy runner for log cleanup tool using settings file
"""

import os
import sys
import subprocess
from pathlib import Path

def read_settings():
    """Read settings from cleanup_settings.txt"""
    settings = {}
    try:
        with open("cleanup_settings.txt", 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # Convert boolean values
                    if value.lower() in ['true', 'false']:
                        settings[key.lower()] = value.lower() == 'true'
                    else:
                        settings[key.lower()] = value
        
        return settings
    except FileNotFoundError:
        print("❌ Error: cleanup_settings.txt not found!")
        print("Please create cleanup_settings.txt with your settings")
        return None
    except Exception as e:
        print(f"❌ Error reading cleanup_settings.txt: {e}")
        return None

def main():
    print("🧹 Log Cleanup Tool - Easy Runner")
    print("=" * 40)
    
    # Read settings
    settings = read_settings()
    if not settings:
        return 1
    
    input_folder = settings.get('input_folder', '')
    output_folder = settings.get('output_folder', '')
    cleanup_level = settings.get('cleanup_level', 'medium')
    remove_timestamps = settings.get('remove_timestamps', True)
    remove_debug_info = settings.get('remove_debug_info', True)
    compress_repetitive = settings.get('compress_repetitive', True)
    extract_key_events = settings.get('extract_key_events', True)
    
    if not input_folder:
        print("❌ Error: INPUT_FOLDER not specified in cleanup_settings.txt")
        return 1
    if not output_folder:
        print("❌ Error: OUTPUT_FOLDER not specified in cleanup_settings.txt")
        return 1
    
    if not os.path.exists(input_folder):
        print(f"❌ Error: Input folder '{input_folder}' does not exist!")
        print("Please check the path in cleanup_settings.txt")
        return 1
    
    os.makedirs(output_folder, exist_ok=True)
    
    print(f"Input Folder: {input_folder}")
    print(f"Output Folder: {output_folder}")
    print(f"Cleanup Level: {cleanup_level}")
    print(f"Remove Timestamps: {remove_timestamps}")
    print(f"Remove Debug Info: {remove_debug_info}")
    print(f"Compress Repetitive: {compress_repetitive}")
    print(f"Extract Key Events: {extract_key_events}")
    print("-" * 40)
    
    try:
        # Run the cleanup tool
        cmd = [
            sys.executable,
            "log_cleanup.py",
            "--input", input_folder,
            "--output", output_folder,
            "--level", cleanup_level
        ]
        
        print("🧹 Starting log cleanup...")
        subprocess.run(cmd, check=True)
        print("✅ Log cleanup completed successfully!")
        print(f"📁 Results saved to: {output_folder}")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running log cleanup: {e}")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
