#!/usr/bin/env python3
"""
Optimized Tag Analyzer - Reads files and analyzes "Tag:" patterns
Detects conversions vs drop-offs and calculates percentages
Creates an Excel file with detailed analysis results
"""

import os
import pandas as pd
from pathlib import Path
import argparse
import re

def analyze_file_for_tag(file_path):
    """
    Analyze a file for Tag: patterns and classify as Conversion or Drop-Off.
    Looks for the actual analysis result after </think> tag, not in the prompt.
    Returns a dictionary with classification and details.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split content by </think> to get the actual analysis result
        parts = content.split('</think>')
        if len(parts) > 1:
            # Look for Tag: pattern in the analysis result (after </think>)
            analysis_content = parts[1]
        else:
            # Fallback: look in the entire content for files without </think> separator
            analysis_content = content
        
        # Look for Tag: pattern (case insensitive) in the analysis content
        # Enhanced pattern to catch various formats including reasons in brackets
        tag_patterns = [
            re.compile(r'Tag:\s*([^.\n]+?)(?:\s*\[.*?\])?', re.IGNORECASE),
            re.compile(r'Tag\s*:\s*([^.\n]+?)(?:\s*\[.*?\])?', re.IGNORECASE),
            re.compile(r'tag:\s*([^.\n]+?)(?:\s*\[.*?\])?', re.IGNORECASE),
            re.compile(r'TAG:\s*([^.\n]+?)(?:\s*\[.*?\])?', re.IGNORECASE)
        ]
        
        match = None
        for pattern in tag_patterns:
            match = pattern.search(analysis_content)
            if match:
                break
        
        if match:
            tag_value = match.group(1).strip()
            
            # Enhanced classification with more variations
            tag_lower = tag_value.lower()
            
            # Check for conversion patterns
            conversion_patterns = ['conversion', 'Conversion', 'convert', 'converted', 'success', 'completed']
            is_conversion = any(pattern in tag_lower for pattern in conversion_patterns)
            
            # Check for drop-off patterns  
            dropoff_patterns = ['drop-off', 'dropoff', 'drop off', 'drop_off', 'Drop-Off', 'abandon', 'abandoned', 'exit', 'left']
            is_dropoff = any(pattern in tag_lower for pattern in dropoff_patterns)
            
            if is_conversion and not is_dropoff:
                return {
                    'has_tag': True,
                    'tag_type': 'Conversion',
                    'tag_value': tag_value,
                    'is_conversion': True,
                    'is_dropoff': False
                }
            elif is_dropoff and not is_conversion:
                return {
                    'has_tag': True,
                    'tag_type': 'Drop-Off',
                    'tag_value': tag_value,
                    'is_conversion': False,
                    'is_dropoff': True
                }
            elif is_conversion and is_dropoff:
                # If both patterns match, prioritize based on order or context
                return {
                    'has_tag': True,
                    'tag_type': 'Mixed',
                    'tag_value': tag_value,
                    'is_conversion': True,
                    'is_dropoff': True
                }
            else:
                # Unknown tag type
                return {
                    'has_tag': True,
                    'tag_type': 'Unknown',
                    'tag_value': tag_value,
                    'is_conversion': False,
                    'is_dropoff': False
                }
        else:
            return {
                'has_tag': False,
                'tag_type': 'None',
                'tag_value': '',
                'is_conversion': False,
                'is_dropoff': False
            }
            
    except Exception as e:
        print(f"Error reading {file_path}: {str(e)}")
        return {
            'has_tag': False,
            'tag_type': 'Error',
            'tag_value': f'Error: {str(e)}',
            'is_conversion': False,
            'is_dropoff': False
        }

def process_directory(directory_path, output_file="tag_analysis_results.xlsx"):
    """
    Process all files in a directory and create Excel results with detailed analysis
    """
    directory = Path(directory_path)
    
    if not directory.exists():
        print(f"Error: Directory '{directory_path}' does not exist!")
        return
    
    # Get all text files in the directory that start with DO or CO
    files = [f for f in directory.iterdir() if f.is_file() and f.suffix.lower() in ['.txt', '.text'] and (f.name.startswith('DO') or f.name.startswith('CO'))]
    
    if not files:
        print(f"No DO/CO files found in '{directory_path}'")
        return
    
    print(f"Analyzing {len(files)} files (DO/CO files only) in '{directory_path}'")
    print("Looking for Tag: patterns (Conversion/Drop-Off)")
    print("-" * 60)
    
    results = []
    conversion_count = 0
    dropoff_count = 0
    mixed_count = 0
    unknown_count = 0
    no_tag_count = 0
    error_count = 0
    
    for file_path in files:
        filename = file_path.name
        analysis = analyze_file_for_tag(file_path)
        
        # Count different types
        if analysis['tag_type'] == 'Mixed':
            mixed_count += 1
        elif analysis['is_conversion']:
            conversion_count += 1
        elif analysis['is_dropoff']:
            dropoff_count += 1
        elif analysis['tag_type'] == 'Unknown':
            unknown_count += 1
        elif analysis['tag_type'] == 'Error':
            error_count += 1
        else:
            no_tag_count += 1
        
        results.append({
            'Filename': filename,
            'Tag_Type': analysis['tag_type']
        })
        
        # Display status
        status_icon = "[OK]" if analysis['has_tag'] else "[NO]"
        tag_display = analysis['tag_type'] if analysis['has_tag'] else "No Tag"
        print(f"{status_icon} {filename}: {tag_display}")
    
    # Calculate percentages
    total_files = len(files)
    conversion_percentage = (conversion_count / total_files) * 100 if total_files > 0 else 0
    dropoff_percentage = (dropoff_count / total_files) * 100 if total_files > 0 else 0
    mixed_percentage = (mixed_count / total_files) * 100 if total_files > 0 else 0
    unknown_percentage = (unknown_count / total_files) * 100 if total_files > 0 else 0
    no_tag_percentage = (no_tag_count / total_files) * 100 if total_files > 0 else 0
    error_percentage = (error_count / total_files) * 100 if total_files > 0 else 0
    
    
    # Create DataFrame
    df = pd.DataFrame(results)
    
    # Create summary data
    summary_data = {
        'Metric': [
            'Total Files',
            'Conversions',
            'Drop-Offs',
            'Mixed (Both)',
            'Unknown Tags',
            'No Tags',
            'Errors',
            'Conversion Rate (%)',
            'Drop-Off Rate (%)',
            'Mixed Rate (%)',
            'Unknown Rate (%)',
            'No Tag Rate (%)',
            'Error Rate (%)'
        ],
        'Count': [
            total_files,
            conversion_count,
            dropoff_count,
            mixed_count,
            unknown_count,
            no_tag_count,
            error_count,
            f"{conversion_percentage:.2f}%",
            f"{dropoff_percentage:.2f}%",
            f"{mixed_percentage:.2f}%",
            f"{unknown_percentage:.2f}%",
            f"{no_tag_percentage:.2f}%",
            f"{error_percentage:.2f}%"
        ]
    }
    
    summary_df = pd.DataFrame(summary_data)
    
    # Save to Excel with multiple sheets
    try:
        # Create output directory if it doesn't exist
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # Write detailed results
            df.to_excel(writer, sheet_name='Detailed_Results', index=False)
            # Write summary statistics
            summary_df.to_excel(writer, sheet_name='Summary_Statistics', index=False)
        
        print("-" * 60)
        print("ANALYSIS COMPLETE")
        print("-" * 60)
        print(f"Results saved to: {output_file}")
        print(f"Total files analyzed: {total_files}")
        print(f"Conversions: {conversion_count} ({conversion_percentage:.2f}%)")
        print(f"Drop-Offs: {dropoff_count} ({dropoff_percentage:.2f}%)")
        print(f"Mixed (Both): {mixed_count} ({mixed_percentage:.2f}%)")
        print(f"Unknown tags: {unknown_count} ({unknown_percentage:.2f}%)")
        print(f"No tags found: {no_tag_count} ({no_tag_percentage:.2f}%)")
        print(f"Errors: {error_count} ({error_percentage:.2f}%)")
        print("-" * 60)
        print("Excel file contains two sheets:")
        print("- 'Detailed_Results': Individual file analysis")
        print("- 'Summary_Statistics': Overall percentages and counts")
        
    except Exception as e:
        print(f"Error saving Excel file: {str(e)}")
        print("Saving as CSV instead...")
        csv_file = output_file.replace('.xlsx', '.csv')
        csv_path = Path(csv_file)
        csv_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(csv_file, index=False, sep=',', encoding='utf-8')
        print(f"Results saved to: {csv_file}")
        print("Note: Open the CSV file in Excel or a text editor to see the columns properly separated.")

def main():
    parser = argparse.ArgumentParser(description='Optimized Tag Analyzer - Conversion/Drop-Off Analysis')
    parser.add_argument('--directory', '-d', help='Directory to analyze')
    parser.add_argument('--output', '-o', default='tag_analysis_results.xlsx', help='Output Excel file')
    parser.add_argument('--tag', '-t', default='Tag: Drop-Off,Conversion', help='Tag pattern to search for')
    
    args = parser.parse_args()
    
    # If no directory specified via command line, try to read from settings file
    if not args.directory:
        settings = {}
        try:
            with open("tag_settings.txt", 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if '=' in line:
                            key, value = line.split('=', 1)
                            settings[key.strip()] = value.strip()
        except FileNotFoundError:
            print("Error: No directory specified and tag_settings.txt not found!")
            print("Please specify --directory or create tag_settings.txt")
            return
        
        input_folder = settings.get('INPUT_FOLDER', '')
        output_file = settings.get('OUTPUT_FILE', 'tag_analysis_results.xlsx')
        
        if not input_folder:
            print("Error: INPUT_FOLDER not specified in tag_settings.txt")
            return
    else:
        input_folder = args.directory
        output_file = args.output
    
    print("Optimized Tag Analyzer - Conversion/Drop-Off Analysis")
    print("=" * 60)
    print(f"Input Folder: {input_folder}")
    print(f"Output File: {output_file}")
    print("-" * 60)
    
    process_directory(input_folder, output_file)

if __name__ == "__main__":
    main()
