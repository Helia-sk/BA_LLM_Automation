#!/usr/bin/env python3
"""
Batch Tag Analyzer - Processes all subfolders in a parent directory
Analyzes DO/CO files in each subfolder and creates individual Excel reports
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
        # Look for Tag: that's not in the prompt instructions
        # Put patterns without line start anchor FIRST to avoid matching prompt instructions
        tag_patterns = [
            # Fallback patterns without line start anchor (these work better)
            re.compile(r'Tag:\s*([a-zA-Z\s\-*:]+)(?:\s*\[.*?\])?(?=\n|$)', re.IGNORECASE),
            re.compile(r'Tag\s*:\s*([a-zA-Z\s\-*:]+)(?:\s*\[.*?\])?(?=\n|$)', re.IGNORECASE),
            re.compile(r'tag:\s*([a-zA-Z\s\-*:]+)(?:\s*\[.*?\])?(?=\n|$)', re.IGNORECASE),
            re.compile(r'TAG:\s*([a-zA-Z\s\-*:]+)(?:\s*\[.*?\])?(?=\n|$)', re.IGNORECASE),
            # Fallback patterns for **Tag: format
            re.compile(r'\*\*Tag:\s*([a-zA-Z\s\-*:]+)(?:\s*\[.*?\])?(?:\*\*|$)', re.IGNORECASE),
            re.compile(r'\*\*Tag\s*:\s*([a-zA-Z\s\-*:]+)(?:\s*\[.*?\])?(?:\*\*|$)', re.IGNORECASE),
            re.compile(r'\*\*tag:\s*([a-zA-Z\s\-*:]+)(?:\s*\[.*?\])?(?:\*\*|$)', re.IGNORECASE),
            re.compile(r'\*\*TAG:\s*([a-zA-Z\s\-*:]+)(?:\s*\[.*?\])?(?:\*\*|$)', re.IGNORECASE),
            # Fallback patterns for **Tag**: format (with colon after Tag)
            re.compile(r'\*\*Tag\*\*:\s*([a-zA-Z\s\-*:]+)(?:\s*\[.*?\])?(?=\n|$)', re.IGNORECASE),
            re.compile(r'\*\*tag\*\*:\s*([a-zA-Z\s\-*:]+)(?:\s*\[.*?\])?(?=\n|$)', re.IGNORECASE),
            re.compile(r'\*\*TAG\*\*:\s*([a-zA-Z\s\-*:]+)(?:\s*\[.*?\])?(?=\n|$)', re.IGNORECASE),
            # Patterns with line start anchor (these might match prompt instructions)
            re.compile(r'^Tag:\s*([a-zA-Z\s\-*:]+)(?:\s*\[.*?\])?', re.IGNORECASE | re.MULTILINE),
            re.compile(r'^Tag\s*:\s*([a-zA-Z\s\-*:]+)(?:\s*\[.*?\])?', re.IGNORECASE | re.MULTILINE),
            re.compile(r'^tag:\s*([a-zA-Z\s\-*:]+)(?:\s*\[.*?\])?', re.IGNORECASE | re.MULTILINE),
            re.compile(r'^TAG:\s*([a-zA-Z\s\-*:]+)(?:\s*\[.*?\])?', re.IGNORECASE | re.MULTILINE),
            # Patterns for **Tag: format
            re.compile(r'^\*\*Tag:\s*([a-zA-Z\s\-*:]+)(?:\s*\[.*?\])?(?:\*\*|$)', re.IGNORECASE | re.MULTILINE),
            re.compile(r'^\*\*Tag\s*:\s*([a-zA-Z\s\-*:]+)(?:\s*\[.*?\])?(?:\*\*|$)', re.IGNORECASE | re.MULTILINE),
            re.compile(r'^\*\*tag:\s*([a-zA-Z\s\-*:]+)(?:\s*\[.*?\])?(?:\*\*|$)', re.IGNORECASE | re.MULTILINE),
            re.compile(r'^\*\*TAG:\s*([a-zA-Z\s\-*:]+)(?:\s*\[.*?\])?(?:\*\*|$)', re.IGNORECASE | re.MULTILINE),
            # Patterns for **Tag**: format (with colon after Tag)
            re.compile(r'^\*\*Tag\*\*:\s*([a-zA-Z\s\-*:]+)(?:\s*\[.*?\])?', re.IGNORECASE | re.MULTILINE),
            re.compile(r'^\*\*tag\*\*:\s*([a-zA-Z\s\-*:]+)(?:\s*\[.*?\])?', re.IGNORECASE | re.MULTILINE),
            re.compile(r'^\*\*TAG\*\*:\s*([a-zA-Z\s\-*:]+)(?:\s*\[.*?\])?', re.IGNORECASE | re.MULTILINE)
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
            conversion_patterns = ['conversion', 'Conversion', '**Tag**: Conversion', 'convert', 'converted', 'success', 'completed']
            is_conversion = any(pattern in tag_lower for pattern in conversion_patterns)
            
            # Check for drop-off patterns  
            dropoff_patterns = ['drop-off', 'dropoff', 'drop off', 'drop_off', 'Drop-Off', '**Tag**: Drop-Off', 'abandon', 'abandoned', 'exit', 'left']
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
    Process all DO/CO files in a directory and create Excel results with detailed analysis
    """
    directory = Path(directory_path)
    
    if not directory.exists():
        print(f"Error: Directory '{directory_path}' does not exist!")
        return False
    
    # Get all text files in the directory that start with DO or CO
    files = [f for f in directory.iterdir() if f.is_file() and f.suffix.lower() in ['.txt', '.text'] and (f.name.startswith('DO') or f.name.startswith('CO'))]
    
    if not files:
        print(f"No DO/CO files found in '{directory_path}'")
        return False
    
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
        
        return True
        
    except Exception as e:
        print(f"Error saving Excel file: {str(e)}")
        print("Saving as CSV instead...")
        csv_file = output_file.replace('.xlsx', '.csv')
        csv_path = Path(csv_file)
        csv_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(csv_file, index=False, sep=',', encoding='utf-8')
        print(f"Results saved to: {csv_file}")
        print("Note: Open the CSV file in Excel or a text editor to see the columns properly separated.")
        return False

def batch_analyze_folders(parent_folder):
    """
    Process all subfolders in parent_folder and analyze DO/CO files in each subfolder.
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
    all_results = []
    
    for i, subfolder in enumerate(subfolders):
        print(f"\nProcessing subfolder {i+1}/{len(subfolders)}: {subfolder.name}")
        print("-" * 40)
        
        # Create output file path for this subfolder
        output_file = subfolder / "Tag_analysis_results.xlsx"
        
        success = process_directory(str(subfolder), str(output_file))
        
        if success:
            success_count += 1
            print(f"[OK] Successfully processed '{subfolder.name}'")
            
            # Collect summary data for overall report
            try:
                summary_df = pd.read_excel(output_file, sheet_name='Summary_Statistics')
                total_files = summary_df[summary_df['Metric'] == 'Total Files']['Count'].iloc[0]
                conversions = summary_df[summary_df['Metric'] == 'Conversions']['Count'].iloc[0]
                dropoffs = summary_df[summary_df['Metric'] == 'Drop-Offs']['Count'].iloc[0]
                mixed = summary_df[summary_df['Metric'] == 'Mixed (Both)']['Count'].iloc[0]
                conversion_rate = summary_df[summary_df['Metric'] == 'Conversion Rate (%)']['Count'].iloc[0]
                dropoff_rate = summary_df[summary_df['Metric'] == 'Drop-Off Rate (%)']['Count'].iloc[0]
                mixed_rate = summary_df[summary_df['Metric'] == 'Mixed Rate (%)']['Count'].iloc[0]
                
                all_results.append({
                    'Subfolder': subfolder.name,
                    'Total_Files': total_files,
                    'Conversions': conversions,
                    'Drop_Offs': dropoffs,
                    'Mixed': mixed,
                    'Conversion_Rate': conversion_rate,
                    'DropOff_Rate': dropoff_rate,
                    'Mixed_Rate': mixed_rate
                })
            except Exception as e:
                print(f"Warning: Could not read summary from {subfolder.name}: {e}")
        else:
            failed_folders.append(subfolder.name)
            print(f"[FAIL] Failed to process '{subfolder.name}'")
    
    # Create overall summary report
    if all_results:
        overall_df = pd.DataFrame(all_results)
        overall_output = parent_path / "Overall_Tag_Analysis_Summary.xlsx"
        
        # Create CO vs DO analysis
        co_analysis = []
        do_analysis = []
        
        for result in all_results:
            subfolder_name = result['Subfolder']
            if subfolder_name.startswith('CO_'):
                co_analysis.append({
                    'Subfolder': subfolder_name,
                    'Total_Files': result['Total_Files'],
                    'Conversions': result['Conversions'],
                    'Conversion_Rate': result['Conversion_Rate'],
                    'Drop_Offs': result['Drop_Offs'],
                    'DropOff_Rate': result['DropOff_Rate'],
                    'Mixed': result['Mixed'],
                    'Mixed_Rate': result['Mixed_Rate']
                })
            elif subfolder_name.startswith('DO_'):
                do_analysis.append({
                    'Subfolder': subfolder_name,
                    'Total_Files': result['Total_Files'],
                    'Conversions': result['Conversions'],
                    'Conversion_Rate': result['Conversion_Rate'],
                    'Drop_Offs': result['Drop_Offs'],
                    'DropOff_Rate': result['DropOff_Rate'],
                    'Mixed': result['Mixed'],
                    'Mixed_Rate': result['Mixed_Rate']
                })
        
        co_df = pd.DataFrame(co_analysis)
        do_df = pd.DataFrame(do_analysis)
        
        # Calculate overall CO and DO statistics
        co_stats = []
        do_stats = []
        
        if not co_df.empty:
            co_total_files = co_df['Total_Files'].sum()
            co_total_conversions = co_df['Conversions'].sum()
            co_total_dropoffs = co_df['Drop_Offs'].sum()
            co_total_mixed = co_df['Mixed'].sum()
            co_avg_conversion_rate = (co_total_conversions / co_total_files * 100) if co_total_files > 0 else 0
            co_avg_dropoff_rate = (co_total_dropoffs / co_total_files * 100) if co_total_files > 0 else 0
            co_avg_mixed_rate = (co_total_mixed / co_total_files * 100) if co_total_files > 0 else 0
            
            co_stats = [
                {'Metric': 'Total CO Files', 'Count': co_total_files},
                {'Metric': 'Total CO Conversions', 'Count': co_total_conversions},
                {'Metric': 'Total CO Drop-Offs', 'Count': co_total_dropoffs},
                {'Metric': 'Total CO Mixed', 'Count': co_total_mixed},
                {'Metric': 'Average CO Conversion Rate (%)', 'Count': f"{co_avg_conversion_rate:.2f}%"},
                {'Metric': 'Average CO Drop-Off Rate (%)', 'Count': f"{co_avg_dropoff_rate:.2f}%"},
                {'Metric': 'Average CO Mixed Rate (%)', 'Count': f"{co_avg_mixed_rate:.2f}%"}
            ]
        
        if not do_df.empty:
            do_total_files = do_df['Total_Files'].sum()
            do_total_conversions = do_df['Conversions'].sum()
            do_total_dropoffs = do_df['Drop_Offs'].sum()
            do_total_mixed = do_df['Mixed'].sum()
            do_avg_conversion_rate = (do_total_conversions / do_total_files * 100) if do_total_files > 0 else 0
            do_avg_dropoff_rate = (do_total_dropoffs / do_total_files * 100) if do_total_files > 0 else 0
            do_avg_mixed_rate = (do_total_mixed / do_total_files * 100) if do_total_files > 0 else 0
            
            do_stats = [
                {'Metric': 'Total DO Files', 'Count': do_total_files},
                {'Metric': 'Total DO Conversions', 'Count': do_total_conversions},
                {'Metric': 'Total DO Drop-Offs', 'Count': do_total_dropoffs},
                {'Metric': 'Total DO Mixed', 'Count': do_total_mixed},
                {'Metric': 'Average DO Conversion Rate (%)', 'Count': f"{do_avg_conversion_rate:.2f}%"},
                {'Metric': 'Average DO Drop-Off Rate (%)', 'Count': f"{do_avg_dropoff_rate:.2f}%"},
                {'Metric': 'Average DO Mixed Rate (%)', 'Count': f"{do_avg_mixed_rate:.2f}%"}
            ]
        
        try:
            with pd.ExcelWriter(overall_output, engine='openpyxl') as writer:
                # Overall summary sheet
                overall_df.to_excel(writer, sheet_name='Overall_Summary', index=False)
                
                # CO statistics sheet
                if not co_df.empty and co_stats:
                    co_stats_df = pd.DataFrame(co_stats)
                    co_stats_df.to_excel(writer, sheet_name='CO_Statistics', index=False)
                
                # DO statistics sheet
                if not do_df.empty and do_stats:
                    do_stats_df = pd.DataFrame(do_stats)
                    do_stats_df.to_excel(writer, sheet_name='DO_Statistics', index=False)
            
            print(f"\n[OK] Overall summary saved to: {overall_output}")
            print("Excel file contains multiple sheets:")
            print("- 'Overall_Summary': All subfolders summary")
            if not co_df.empty and co_stats:
                print("- 'CO_Statistics': CO overall statistics")
            if not do_df.empty and do_stats:
                print("- 'DO_Statistics': DO overall statistics")
        except Exception as e:
            print(f"Warning: Could not create overall summary: {e}")
    
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
    parser = argparse.ArgumentParser(description='Batch Tag Analyzer - Process All Subfolders')
    parser.add_argument('--directory', '-d', help='Directory to analyze (single directory mode)')
    parser.add_argument('--parent', '-p', help='Parent directory to analyze all subfolders')
    
    args = parser.parse_args()
    
    # If single directory specified, process it directly
    if args.directory:
        print("Batch Tag Analyzer - Single Directory Mode")
        print("=" * 60)
        print(f"Directory: {args.directory}")
        print("-" * 60)
        
        success = process_directory(args.directory, f"{args.directory}/Tag_analysis_results.xlsx")
        
        if success:
            print("\n" + "=" * 60)
            print("[OK] ANALYSIS COMPLETED SUCCESSFULLY!")
            print("=" * 60)
        else:
            print("\n" + "=" * 60)
            print("[FAIL] ANALYSIS FAILED!")
            print("=" * 60)
        return
    
    # If parent directory specified, process all subfolders
    if args.parent:
        parent_folder = args.parent
    else:
        # Read settings from batch_tag_settings.txt
        settings = {}
        
        try:
            with open("batch_tag_settings.txt", 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if '=' in line:
                            key, value = line.split('=', 1)
                            settings[key.strip()] = value.strip()
        except FileNotFoundError:
            print("Error: No directory specified and batch_tag_settings.txt not found!")
            print("Please specify --directory or --parent, or create batch_tag_settings.txt")
            return
        
        # Get settings
        parent_folder = settings.get('PARENT_FOLDER', '')
        
        if not parent_folder:
            print("Error: PARENT_FOLDER not specified in batch_tag_settings.txt")
            return
    
    print("Batch Tag Analyzer - Process All Subfolders")
    print("=" * 60)
    print(f"Parent Folder: {parent_folder}")
    print("-" * 60)
    
    # Process all subfolders
    success = batch_analyze_folders(parent_folder)
    
    if success:
        print("\n" + "=" * 60)
        print("[OK] BATCH PROCESSING COMPLETED SUCCESSFULLY!")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("[FAIL] BATCH PROCESSING FAILED!")
        print("=" * 60)

if __name__ == "__main__":
    main()
