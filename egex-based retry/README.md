# Regex Validator - LLM Output Validation with Retry Logic

This folder contains all files related to the LLM output validator that uses regex validation and retry logic.

## 📁 Files in this folder:

### **Core Files:**
- **`llm_validator.py`** - Main validator script with regex validation and retry logic
- **`run_validator.py`** - Easy runner that reads settings and launches the validator
- **`validator_settings.txt`** - Configuration file for input/output paths and model settings
- **`test_ollama.py`** - Test script to check if Ollama is running and models are available

## 🚀 How to use:

### **1. Configure settings:**
Edit `validator_settings.txt`:
```
INPUT_PATH=C:/path/to/your/input/files
OUTPUT_PATH=C:/path/to/output/directory
MODEL=llama3.3:70b
TEMPERATURE=0.1
TOP_P=0.2
MAX_TOKENS=400
MAX_RETRIES=2
TEST_MODE=true
TIMEOUT=300
```

### **2. Run the validator:**
```cmd
cd regex
python run_validator.py
```

### **3. Test Ollama connection:**
```cmd
cd regex
python test_ollama.py
```

## 🎯 What it does:

- **Validates LLM output** using regex patterns for exact format
- **Checks for decisions** - ensures "Conversion" or "Drop-Off" is present
- **Retry logic** - automatically retries with corrective prompts if format is wrong
- **Sequential processing** - processes files one by one with progress tracking
- **Timeout handling** - configurable timeout for LLM requests
- **Test mode** - process only first 3 files for quick testing

## 📊 Output format expected:
```
Tag: Conversion || Drop-Off [Reason].
1) [Step 1]
2) [Step 2]
3) [Step 3]
...
```

## ⚙️ Features:
- ✅ Regex validation for exact format
- ✅ Decision detection (Conversion/Drop-Off)
- ✅ Smart retry with different prompts
- ✅ Progress tracking with time estimates
- ✅ Test mode for quick validation
- ✅ Detailed logging of all operations
- ✅ Fallback classification if LLM fails
