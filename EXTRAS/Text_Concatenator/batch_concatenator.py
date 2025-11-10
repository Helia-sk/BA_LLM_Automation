#!/usr/bin/env python3
"""
Simple batch concatenator - processes all subfolders in a parent folder
"""

import os
import sys
from pathlib import Path

def concatenate_text_files(input_folder, output_filename="concatenated_text.txt"):
    """
    Read all text files from input_folder and concatenate them into one file.
    """
    folder_path = Path(input_folder)
    
    if not folder_path.exists():
        print(f"Error: Folder '{input_folder}' does not exist!")
        return False
    
    if not folder_path.is_dir():
        print(f"Error: '{input_folder}' is not a directory!")
        return False
    
    # Get all text files in the folder
    text_files = []
    for file_path in folder_path.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in ['.txt', '.text']:
            text_files.append(file_path)
    
    if not text_files:
        print(f"No text files found in '{input_folder}'")
        return False
    
    # Sort files for consistent ordering
    text_files.sort(key=lambda x: x.name)
    
    print(f"Found {len(text_files)} text files in '{input_folder}'")
    print("Files to concatenate:")
    for file_path in text_files:
        print(f"  - {file_path.name}")
    
    # Create output file path
    output_path = folder_path / output_filename
    
    try:
        with open(output_path, 'w', encoding='utf-8') as output_file:
            for i, file_path in enumerate(text_files):
                print(f"Processing {file_path.name}...")
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as input_file:
                        content = input_file.read()
                    
                    # Add file separator and filename header
                    if i > 0:
                        output_file.write("\n" + "="*80 + "\n")
                    
                    output_file.write(f"FILE: {file_path.name}\n")
                    output_file.write("="*80 + "\n")
                    output_file.write(content)
                    
                    # Add newline at the end if content doesn't end with one
                    if content and not content.endswith('\n'):
                        output_file.write('\n')
                        
                except Exception as e:
                    print(f"Warning: Could not read '{file_path.name}': {e}")
                    # Add error message to output
                    output_file.write(f"\n" + "="*80 + "\n")
                    output_file.write(f"FILE: {file_path.name} (ERROR: {e})\n")
                    output_file.write("="*80 + "\n")
                    output_file.write(f"Error reading file: {e}\n")
        
        print(f"\nSuccessfully concatenated {len(text_files)} files into '{output_path}'")
        return True
        
    except Exception as e:
        print(f"Error writing output file: {e}")
        return False

def batch_concatenate_folders(parent_folder, output_filename="concatenated_text.txt"):
    """
    Process all subfolders in parent_folder and concatenate text files in each subfolder.
    """
    parent_path = Path(parent_folder)
    
    if not parent_path.exists():
        print(f"Error: Parent folder '{parent_folder}' does not exist!")
        return False
    
    if not parent_path.is_dir():
        print(f"Error: '{parent_folder}' is not a directory!")
        return False
    
    # Get all subdirectories
    subfolders = []
    for item in parent_path.iterdir():
        if item.is_dir():
            subfolders.append(item)
    
    if not subfolders:
        print(f"No subfolders found in '{parent_folder}'")
        return False
    
    # Sort subfolders for consistent ordering
    subfolders.sort(key=lambda x: x.name)
    
    print(f"Found {len(subfolders)} subfolders in '{parent_folder}'")
    print("Subfolders to process:")
    for subfolder in subfolders:
        print(f"  - {subfolder.name}")
    
    print("\n" + "="*60)
    
    success_count = 0
    failed_folders = []
    
    for i, subfolder in enumerate(subfolders):
        print(f"\nProcessing subfolder {i+1}/{len(subfolders)}: {subfolder.name}")
        print("-" * 40)
        
        success = concatenate_text_files(str(subfolder), output_filename)
        
        if success:
            success_count += 1
            print(f"✓ Successfully processed '{subfolder.name}'")
        else:
            failed_folders.append(subfolder.name)
            print(f"✗ Failed to process '{subfolder.name}'")
    
    print("\n" + "="*60)
    print("BATCH PROCESSING SUMMARY")
    print("="*60)
    print(f"Total subfolders processed: {len(subfolders)}")
    print(f"Successfully processed: {success_count}")
    print(f"Failed: {len(failed_folders)}")
    
    if failed_folders:
        print("\nFailed folders:")
        for folder_name in failed_folders:
            print(f"  - {folder_name}")
    
    return success_count > 0

def main():
    # Read settings from concatenator_settings.txt
    settings = {}
    
    try:
        with open("concatenator_settings.txt", 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    if '=' in line:
                        key, value = line.split('=', 1)
                        settings[key.strip()] = value.strip()
    except FileNotFoundError:
        print("Error: concatenator_settings.txt not found!")
        return
    
    # Get settings
    input_folder = settings.get('INPUT_FOLDER', '')
    output_filename = settings.get('OUTPUT_FILENAME', 'concatenated_text.txt')
    
    if not input_folder:
        print("Error: INPUT_FOLDER not specified in concatenator_settings.txt")
        return
    
    print("Batch Text Concatenator")
    print("=" * 30)
    print(f"Input Folder: {input_folder}")
    print(f"Output Filename: {output_filename}")
    print("-" * 30)
    
    # Process all subfolders
    success = batch_concatenate_folders(input_folder, output_filename)
    
    if success:
        print("Batch concatenation completed successfully!")
    else:
        print("Batch concatenation failed!")

if __name__ == "__main__":
    main()





