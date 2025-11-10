#!/usr/bin/env python3
"""
Log Cleanup Tool
Reduces noise and volume in web log files for better LLM processing
"""

import json
import re
import os
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional

class LogCleanup:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.cleanup_level = config.get('cleanup_level', 'medium')
        self.remove_timestamps = config.get('remove_timestamps', True)
        self.remove_debug_info = config.get('remove_debug_info', True)
        self.compress_repetitive = config.get('compress_repetitive', True)
        self.extract_key_events = config.get('extract_key_events', True)
        
        # Patterns for cleanup
        self.timestamp_patterns = [
            r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}',
            r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}',
            r'timestamp["\']?\s*:\s*["\']?\d+["\']?',
            r'time["\']?\s*:\s*["\']?\d+["\']?',
            r'@timestamp["\']?\s*:\s*["\']?[^"]+["\']?'
        ]
        
        self.debug_patterns = [
            r'debug',
            r'DEBUG',
            r'verbose',
            r'VERBOSE',
            r'trace',
            r'TRACE',
            r'info',
            r'INFO'
        ]
        
        # Key events specific to web session logs
        self.key_events = [
            'login', 'logout', 'register', 'purchase', 'add_to_cart', 
            'checkout', 'payment', 'menu', 'add_menu_item', 'delete',
            'edit', 'update', 'create', 'submit', 'success', 'error',
            'api_call', 'request', 'response', 'redirect', 'navigate'
        ]
        
        # Fields to keep for web session analysis
        self.essential_fields = [
            'event_name', 'endpoint', 'method', 'route', 'status_code',
            'response_size', 'content_type', 'log_type', 'attempt_id',
            'session_id', 'browser_id', 'url'
        ]
        
        # Fields to remove for volume reduction
        self.noise_fields = [
            'ip_address', 'user_agent', 'processing_time', 'content_length',
            'details', 'schema_version', 'id'
        ]

    def clean_json_log(self, content: str) -> str:
        """Clean JSON log content"""
        try:
            data = json.loads(content)
            
            if isinstance(data, list):
                cleaned_entries = []
                for entry in data:
                    cleaned_entry = self.clean_log_entry(entry)
                    if cleaned_entry:
                        cleaned_entries.append(cleaned_entry)
                
                # Compress repetitive entries if configured
                if self.compress_repetitive:
                    cleaned_entries = self.compress_repetitive_entries(cleaned_entries)
                
                return json.dumps(cleaned_entries, indent=2)
            else:
                cleaned_entry = self.clean_log_entry(data)
                return json.dumps(cleaned_entry, indent=2) if cleaned_entry else ""
                
        except json.JSONDecodeError:
            return self.clean_text_log(content)

    def clean_text_log(self, content: str) -> str:
        """Clean text log content"""
        lines = content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            if self.should_keep_line(line):
                cleaned_line = self.clean_line(line)
                if cleaned_line:
                    cleaned_lines.append(cleaned_line)
        
        return '\n'.join(cleaned_lines)

    def clean_log_entry(self, entry: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Clean a single log entry"""
        if not isinstance(entry, dict):
            return entry
            
        cleaned_entry = {}
        
        # Apply cleanup level
        if self.cleanup_level == 'minimal':
            # Keep most fields, only remove timestamps
            for key, value in entry.items():
                if self.remove_timestamps and self.is_timestamp_field(key, value):
                    continue
                cleaned_entry[key] = value
                
        elif self.cleanup_level == 'medium':
            # Keep essential fields, remove noise fields
            for key, value in entry.items():
                if self.remove_timestamps and self.is_timestamp_field(key, value):
                    continue
                if key in self.noise_fields:
                    continue
                if self.remove_debug_info and self.is_debug_field(key, value):
                    continue
                cleaned_entry[key] = value
                
        elif self.cleanup_level == 'aggressive':
            # Keep only essential fields
            for key, value in entry.items():
                if key in self.essential_fields:
                    if self.remove_timestamps and self.is_timestamp_field(key, value):
                        continue
                    cleaned_entry[key] = value
        
        # Extract only key events if configured
        if self.extract_key_events:
            if not self.has_key_events(cleaned_entry):
                return None
                
        return cleaned_entry if cleaned_entry else None

    def clean_string_value(self, value: str) -> str:
        """Clean string values"""
        # Remove timestamps
        if self.remove_timestamps:
            for pattern in self.timestamp_patterns:
                value = re.sub(pattern, '', value)
        
        # Remove debug info
        if self.remove_debug_info:
            for pattern in self.debug_patterns:
                value = re.sub(pattern, '', value, flags=re.IGNORECASE)
        
        # Clean up extra whitespace
        value = re.sub(r'\s+', ' ', value).strip()
        
        return value

    def should_keep_line(self, line: str) -> bool:
        """Determine if a line should be kept"""
        if not line.strip():
            return False
            
        # Skip debug lines
        if self.remove_debug_info:
            for pattern in self.debug_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    return False
        
        # Extract key events if configured
        if self.extract_key_events:
            return any(event in line.lower() for event in self.key_events)
        
        return True

    def clean_line(self, line: str) -> str:
        """Clean a single line"""
        # Remove timestamps
        if self.remove_timestamps:
            for pattern in self.timestamp_patterns:
                line = re.sub(pattern, '', line)
        
        # Clean up extra whitespace
        line = re.sub(r'\s+', ' ', line).strip()
        
        return line

    def is_timestamp_field(self, key: str, value: Any) -> bool:
        """Check if field is a timestamp"""
        timestamp_keys = ['timestamp', 'time', '@timestamp', 'created_at', 'updated_at']
        return key.lower() in timestamp_keys

    def is_debug_field(self, key: str, value: Any) -> bool:
        """Check if field is debug information"""
        debug_keys = ['debug', 'verbose', 'trace', 'info', 'level']
        return key.lower() in debug_keys

    def has_key_events(self, entry: Dict[str, Any]) -> bool:
        """Check if entry contains key events"""
        # Check endpoint field for key events
        endpoint = entry.get('endpoint', '') or ''
        event_name = entry.get('event_name', '') or ''
        route = entry.get('route', '') or ''
        
        # Convert to lowercase safely
        endpoint = endpoint.lower() if isinstance(endpoint, str) else ''
        event_name = event_name.lower() if isinstance(event_name, str) else ''
        route = route.lower() if isinstance(route, str) else ''
        
        # Check for key events in endpoint
        if any(event in endpoint for event in self.key_events):
            return True
            
        # Check for key events in route
        if any(event in route for event in self.key_events):
            return True
            
        # Check for successful responses (status 200-299)
        status_code = entry.get('status_code')
        if isinstance(status_code, int) and 200 <= status_code < 300:
            return True
            
        # Check for error responses (status 400+)
        if isinstance(status_code, int) and status_code >= 400:
            return True
            
        # Check for specific event types
        if event_name in ['http_request', 'http_response']:
            return True
            
        return False

    def compress_repetitive_entries(self, entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Compress repetitive log entries to reduce volume"""
        if not entries:
            return entries
            
        compressed = []
        current_group = []
        current_key = None
        
        for entry in entries:
            # Create a key for grouping similar entries
            group_key = self.create_group_key(entry)
            
            if group_key == current_key:
                # Same group, add to current group
                current_group.append(entry)
            else:
                # Different group, process current group and start new one
                if current_group:
                    compressed.extend(self.process_group(current_group))
                current_group = [entry]
                current_key = group_key
        
        # Process the last group
        if current_group:
            compressed.extend(self.process_group(current_group))
            
        return compressed

    def create_group_key(self, entry: Dict[str, Any]) -> str:
        """Create a key for grouping similar entries"""
        # Group by endpoint, method, and event_name
        endpoint = entry.get('endpoint', '') or ''
        method = entry.get('method', '') or ''
        event_name = entry.get('event_name', '') or ''
        return f"{endpoint}|{method}|{event_name}"

    def process_group(self, group: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process a group of similar entries"""
        if len(group) <= 2:
            # Small group, keep all entries
            return group
        
        # For larger groups, keep first and last entry, add count
        first_entry = group[0].copy()
        last_entry = group[-1].copy()
        
        # Add count information
        first_entry['_group_count'] = len(group)
        first_entry['_group_note'] = f"Grouped {len(group)} similar entries"
        
        return [first_entry, last_entry]

    def process_file(self, input_file: Path, output_file: Path) -> Dict[str, Any]:
        """Process a single log file"""
        print(f"📁 Processing: {input_file.name}")
        
        try:
            # Read input file
            with open(input_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_size = len(content)
            
            # Clean the content
            if input_file.suffix.lower() == '.json':
                cleaned_content = self.clean_json_log(content)
            else:
                cleaned_content = self.clean_text_log(content)
            
            # Create output directory
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Write cleaned content
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(cleaned_content)
            
            cleaned_size = len(cleaned_content)
            reduction_percent = ((original_size - cleaned_size) / original_size) * 100
            
            print(f"   ✅ Reduced by {reduction_percent:.1f}% ({original_size} → {cleaned_size} chars)")
            
            return {
                "status": "success",
                "input_file": str(input_file),
                "output_file": str(output_file),
                "original_size": original_size,
                "cleaned_size": cleaned_size,
                "reduction_percent": reduction_percent
            }
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return {
                "status": "error",
                "input_file": str(input_file),
                "error": str(e)
            }

    def process_directory(self, input_dir: Path, output_dir: Path) -> List[Dict[str, Any]]:
        """Process all log files in a directory"""
        print(f"📂 Processing directory: {input_dir}")
        print(f"📂 Output directory: {output_dir}")
        
        # Find log files
        log_extensions = ['.json', '.log', '.txt']
        files = []
        for ext in log_extensions:
            files.extend(input_dir.glob(f"*{ext}"))
        
        if not files:
            print("❌ No log files found in input directory")
            return []
        
        print(f"📊 Found {len(files)} files to process")
        
        results = []
        total_original = 0
        total_cleaned = 0
        
        for i, file_path in enumerate(files, 1):
            print(f"\n{'='*60}")
            print(f"Processing {i}/{len(files)}: {file_path.name}")
            print(f"{'='*60}")
            
            # Create output filename with _volumeReduced suffix
            output_filename = f"{file_path.stem}_volumeReduced{file_path.suffix}"
            output_file = output_dir / output_filename
            
            result = self.process_file(file_path, output_file)
            results.append(result)
            
            if result["status"] == "success":
                total_original += result["original_size"]
                total_cleaned += result["cleaned_size"]
                print(f"   ✅ {output_filename}")
            else:
                print(f"   ❌ Error: {result['error']}")
        
        # Summary
        if total_original > 0:
            total_reduction = ((total_original - total_cleaned) / total_original) * 100
            print(f"\n📊 SUMMARY:")
            print(f"   Files processed: {len(files)}")
            print(f"   Successful: {len([r for r in results if r['status'] == 'success'])}")
            print(f"   Total reduction: {total_reduction:.1f}%")
            print(f"   Size saved: {total_original - total_cleaned:,} characters")
        
        return results

def read_settings(settings_file: str = "cleanup_settings.txt") -> Optional[Dict[str, Any]]:
    """Read settings from file"""
    try:
        settings = {}
        with open(settings_file, 'r', encoding='utf-8') as f:
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
        print(f"❌ Error: {settings_file} not found!")
        return None
    except Exception as e:
        print(f"❌ Error reading {settings_file}: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description="Log Cleanup Tool")
    parser.add_argument("--input", "-i", help="Input file or directory")
    parser.add_argument("--output", "-o", help="Output file or directory")
    parser.add_argument("--settings", "-s", default="cleanup_settings.txt", help="Settings file")
    parser.add_argument("--level", choices=['minimal', 'medium', 'aggressive'], help="Cleanup level")
    
    args = parser.parse_args()
    
    # Read settings
    settings = read_settings(args.settings)
    if not settings:
        return 1
    
    # Override with command line arguments
    if args.input:
        settings['input_folder'] = args.input
    if args.output:
        settings['output_folder'] = args.output
    if args.level:
        settings['cleanup_level'] = args.level
    
    # Validate settings
    input_folder = settings.get('input_folder')
    output_folder = settings.get('output_folder')
    
    if not input_folder or not output_folder:
        print("❌ Error: INPUT_FOLDER and OUTPUT_FOLDER must be specified")
        return 1
    
    input_path = Path(input_folder)
    output_path = Path(output_folder)
    
    if not input_path.exists():
        print(f"❌ Error: Input path '{input_path}' does not exist")
        return 1
    
    # Create cleanup instance
    cleanup = LogCleanup(settings)
    
    print("🧹 Log Cleanup Tool")
    print("=" * 50)
    print(f"Cleanup Level: {cleanup.cleanup_level}")
    print(f"Remove Timestamps: {cleanup.remove_timestamps}")
    print(f"Remove Debug Info: {cleanup.remove_debug_info}")
    print(f"Compress Repetitive: {cleanup.compress_repetitive}")
    print(f"Extract Key Events: {cleanup.extract_key_events}")
    print("=" * 50)
    
    if input_path.is_file():
        # Single file processing
        output_file = output_path if output_path.suffix else output_path / f"{input_path.stem}_volumeReduced{input_path.suffix}"
        result = cleanup.process_file(input_path, output_file)
        
        if result["status"] == "success":
            print(f"✅ Success: {output_file}")
        else:
            print(f"❌ Error: {result['error']}")
            return 1
    else:
        # Directory processing
        results = cleanup.process_directory(input_path, output_path)
        
        successful = len([r for r in results if r["status"] == "success"])
        if successful == 0:
            print("❌ No files were successfully processed")
            return 1
    
    print("\n🎉 Cleanup completed!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
