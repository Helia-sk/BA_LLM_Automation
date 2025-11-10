# Text Concatenator

A simple tool to concatenate all text files from a folder into one combined file.

## Features

- Reads all `.txt` and `.text` files from a specified folder
- Concatenates them in alphabetical order
- Adds file separators and headers for each file
- Creates one output file in the same folder
- Handles encoding errors gracefully

## Usage

### Method 1: Using Settings File (Recommended)

1. Edit `concatenator_settings.txt`:
   ```
   INPUT_FOLDER=C:\path\to\your\folder
   OUTPUT_FILENAME=all_text_combined.txt
   ```

2. Run:
   ```bash
   python run_concatenator.py
   ```

### Method 2: Direct Command Line

```bash
python text_concatenator.py --folder "C:\path\to\your\folder" --output "combined.txt"
```

## Output Format

The concatenated file will have this format:
```
FILE: file1.txt
================================================================================
[content of file1.txt]

================================================================================
FILE: file2.txt
================================================================================
[content of file2.txt]
```

## Files

- `text_concatenator.py` - Main script
- `run_concatenator.py` - Easy runner using settings file
- `concatenator_settings.txt` - Configuration file
- `README.md` - This documentation
