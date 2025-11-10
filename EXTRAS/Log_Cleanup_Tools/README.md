# Log Cleanup Tools

This folder contains tools for cleaning and reducing web log files by removing noise and unnecessary parts to prepare them for LLM processing.

## 📁 Files Overview

### Core Cleanup Scripts
- **`log_cleanup.py`** - Main log cleanup script that reduces noise and volume
- **`run_log_cleanup.py`** - Easy runner that reads settings and executes cleanup

### Configuration
- **`cleanup_settings.txt`** - Configuration file for input/output folders and cleanup options

### Utilities
- **`run_log_cleanup.bat`** - Windows batch file for easy running

## 🚀 Quick Start

### 1. Configure Settings
Edit `cleanup_settings.txt`:
```
INPUT_FOLDER=path/to/your/input/logs
OUTPUT_FOLDER=path/to/cleaned/logs
CLEANUP_LEVEL=medium
REMOVE_TIMESTAMPS=true
REMOVE_DEBUG_INFO=true
```

### 2. Run Cleanup
```bash
python run_log_cleanup.py
```

Or double-click `run_log_cleanup.bat` on Windows.

## 🔧 Features

- **Noise Reduction** - Remove unnecessary log entries and debug information
- **Volume Reduction** - Compress logs while keeping essential information
- **Format Preservation** - Maintain original log structure for LLM processing
- **Batch Processing** - Clean entire directories of log files
- **Configurable Cleanup** - Adjust cleanup level and options

## 📋 Requirements

- Python 3.7+
- Required packages: `json`, `re`, `pathlib`

## 🎯 Cleanup Options

### Cleanup Levels
- **`minimal`** - Remove only timestamps, keep all other fields
- **`medium`** - Remove timestamps + noise fields (IP, user agent, etc.)
- **`aggressive`** - Keep only essential fields (endpoint, method, status, etc.)

### Cleanup Features
- **Remove timestamps** - Strip time/date information
- **Remove noise fields** - Filter out IP addresses, user agents, processing times
- **Compress repetitive entries** - Group similar HTTP requests/responses
- **Extract key events** - Keep only important user actions and API calls
- **Clean JSON structure** - Remove unnecessary fields while preserving essential data

### Web Session Log Optimization
- **Essential fields kept**: event_name, endpoint, method, route, status_code, response_size
- **Noise fields removed**: ip_address, user_agent, processing_time, content_length, details
- **Smart grouping**: Groups similar API calls to reduce volume
- **Key event detection**: Identifies login, logout, purchases, menu actions, etc.

## 📊 Output Format

Cleaned files are saved with `_volumeReduced` suffix:
- `CO_1.json` → `CO_1_volumeReduced.json`
- `session_2.log` → `session_2_volumeReduced.log`

## 🔍 Troubleshooting

1. **File not found**: Check input folder path in settings
2. **Permission errors**: Ensure output directory is writable
3. **Memory issues**: Use minimal cleanup level for large files
4. **Format errors**: Check if input files are valid JSON/log format
