#!/usr/bin/env python3
"""
Text Concatenator - Reads all text files from a folder and concatenates them into one file
"""

import os
import sys
from pathlib import Path
import argparse

def concatenate_text_files(input_folder, output_filename="concatenated_text.txt"):
    """
    Read all text files from input_folder and concatenate them into one file.
    
    Args:
        input_folder (str): Path to the folder containing text files
        output_filename (str): Name of the output file (will be created in the same folder)
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
    
    Args:
        parent_folder (str): Path to the parent folder containing subfolders with text files
        output_filename (str): Name of the output file for each subfolder
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
    parser = argparse.ArgumentParser(description="Concatenate all text files from a folder into one file")
    parser.add_argument("--folder", "-f", required=True, help="Input folder containing text files")
    parser.add_argument("--output", "-o", default="concatenated_text.txt", help="Output filename (default: concatenated_text.txt)")
    parser.add_argument("--batch", "-b", action="store_true", help="Process all subfolders in the input folder")
    
    args = parser.parse_args()
    
    print("Text Concatenator")
    print("=" * 30)
    print(f"Input Folder: {args.folder}")
    print(f"Output File: {args.output}")
    print(f"Batch Mode: {'Yes' if args.batch else 'No'}")
    print("-" * 30)
    
    if args.batch:
        success = batch_concatenate_folders(args.folder, args.output)
    else:
        success = concatenate_text_files(args.folder, args.output)
    
    if success:
        print("Concatenation completed successfully!")
    else:
        print("Concatenation failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()