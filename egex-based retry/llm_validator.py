#!/usr/bin/env python3
"""
LLM Output Validator with Retry Logic
Validates and corrects LLM output to ensure proper format
"""

import re
import time
import json
import os
import sys
import argparse
from pathlib import Path
from typing import Tuple, Optional, Dict, Any
import requests

# 1) Compile validators once
TAG_LINE_RE = re.compile(r'^Tag:\s*(Conversion|Drop-Off)\s*\[.*?\]\.?\s*$', re.IGNORECASE)
STEP_LINE_RE = re.compile(r'^\d+\)\s+.+$', re.MULTILINE)
DECISION_WORDS_RE = re.compile(r'\b(Conversion|Drop-Off)\b', re.IGNORECASE)

def is_valid_output(text: str) -> bool:
    """Check required structure: first line Tag:..., then at least one numbered step."""
    # Remove code fences if model wrapped output
    cleaned = text.strip().strip('`').strip()
    lines = [ln.strip() for ln in cleaned.splitlines() if ln.strip()]
    if not lines:
        return False
    # First non-empty line must match Tag line
    if not TAG_LINE_RE.match(lines[0]):
        return False
    # There must be at least one step line anywhere below
    steps_block = "\n".join(lines[1:])
    return bool(STEP_LINE_RE.search(steps_block))

def has_decision(text: str) -> bool:
    """Check if text contains a clear Conversion or Drop-Off decision."""
    return bool(DECISION_WORDS_RE.search(text))

def extract_decision(text: str) -> str:
    """Extract the decision (Conversion or Drop-Off) from text."""
    match = DECISION_WORDS_RE.search(text)
    return match.group(1) if match else None

def build_prompt(base_prompt: str, filtered_log: str, endpoint_map: str = "") -> str:
    """Attach the strict rules + format to your base prompt and append the log."""
    endpoint_section = f"Terminal success map:\n{endpoint_map}" if endpoint_map else ""
    
    RULES = f"""
Decide ONLY: Conversion or Drop-Off.
Analyze the following log file. Determine if the session was a drop-off or a conversion. Provide a reason for your classification
Output EXACTLY:
Tag: Conversion || Drop-Off [Short reason].
1) [Step 1]
2) [Step 2]
3) [Step 3]
…
Now analyze the log:
""".strip()
    return f"{RULES}\n{filtered_log}"

def call_local_model(prompt: str, *, model: str = "llama3.3:70b",
                      temperature: float = 0.1, top_p: float = 0.2,
                      max_tokens: int = 2000, base_url: str = "http://localhost:11434",
                      timeout: int = 600) -> str:
    """Call local Ollama model with retry logic."""
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": temperature,
            "top_p": top_p,
            "num_predict": max_tokens
        }
    }
    
    try:
        print(f"  Calling model {model}...")
        print(f"  Prompt preview: {prompt[:200]}...")
        print(f"  Settings: temp={temperature}, top_p={top_p}, max_tokens={max_tokens}")
        print(f"  Timeout: {timeout} seconds")
        print(f"  Sending request to: {base_url}/api/generate")
        
        # Add progress indicators
        print(f"  ⏳ Sending request...")
        response = requests.post(f"{base_url}/api/generate", json=payload, timeout=timeout)
        print(f"  ✅ Request completed, status: {response.status_code}")
        
        response.raise_for_status()
        print(f"  📊 Parsing response...")
        result = response.json()
        response_text = result.get('response', '').strip()
        
        print(f"  Model response length: {len(response_text)} chars")
        print(f"  Raw response: {response_text[:300]}...")
        
        return response_text
    except requests.exceptions.Timeout:
        print(f"  ❌ TIMEOUT: Request took longer than {timeout} seconds")
        raise Exception(f"Model call timed out after {timeout} seconds")
    except requests.exceptions.ConnectionError:
        print(f"  ❌ CONNECTION ERROR: Cannot connect to {base_url}")
        raise Exception(f"Cannot connect to Ollama at {base_url}")
    except Exception as e:
        print(f"  ❌ Model call failed: {e}")
        raise Exception(f"Model call failed: {e}")

# 3) Corrective retry messages
RETRY_FORMAT_SUFFIX = """
Your last answer was invalid. Output ONLY in this exact format:

Tag: Conversion || Drop-Off [Short reason].
1) [Step 1]
2) [Step 2]
3) [Step 3]
…
Do not include any other text.
"""

RETRY_DECISION_SUFFIX = """
You must make a clear decision. Your response must include either "Conversion" or "Drop-Off" and follow this exact format:

Tag: Conversion || Drop-Off [Short reason].
1) [Step 1]
2) [Step 2]
3) [Step 3]
…
"""

def classify_with_retries(prompt: str,
                          max_retries: int = 2,
                          retry_delay_s: float = 0.5,
                          timeout: int = 600,
                          attempt_folder: str = None,
                          original_log: str = "",
                          **model_kwargs) -> Tuple[str, bool, int]:
    """
    Returns: (final_output_text, valid, retries_used)
    - valid=True if the final output matches the required format.
    - retries_used = number of corrective attempts taken.
    """
    print(f"   Starting classification with {max_retries} max retries...")
    
    # First attempt
    print(f"   Attempt 1: Initial classification...")
    text = call_local_model(prompt, timeout=timeout, **model_kwargs)
    
    format_valid = is_valid_output(text)
    has_dec = has_decision(text)
    decision = extract_decision(text)
    
    print(f"  Validation results:")
    print(f"     Valid format: {format_valid}")
    print(f"     Has decision: {has_dec}")
    print(f"      Decision: {decision}")
    
    # Save first attempt
    if attempt_folder:
        attempt_file = os.path.join(attempt_folder, "attempt_1_initial.txt")
        with open(attempt_file, 'w', encoding='utf-8') as f:
            f.write(f"PROMPT:\n{prompt}\n\n")
            f.write(f"RESPONSE:\n{text}\n\n")
            f.write(f"VALIDATION:\n")
            f.write(f"  Valid format: {format_valid}\n")
            f.write(f"  Has decision: {has_dec}\n")
            f.write(f"  Decision: {decision}\n")
        print(f"  💾 Saved attempt 1 to: {attempt_file}")
    
    if format_valid and has_dec:
        print(f"   SUCCESS on first attempt!")
        return (text.strip(), True, 0)

    # Retry loop
    retries = 0
    for i in range(max_retries):
        retries += 1
        print(f"  ⏳ Waiting {retry_delay_s}s before retry {retries}...")
        time.sleep(retry_delay_s)
        
        # Choose retry message based on what's missing
        if not has_dec:
            retry_suffix = RETRY_DECISION_SUFFIX
            print(f"   Retry {retries}: No decision found, prompting for decision...")
        else:
            retry_suffix = RETRY_FORMAT_SUFFIX
            print(f"   Retry {retries}: Decision found but wrong format, prompting for format...")
            
        # Include original log in retry prompt
        retry_prompt = f"{retry_suffix}\n\nNow analyze the log:\n{original_log}".strip()
        text = call_local_model(retry_prompt, timeout=timeout, **model_kwargs)
        
        format_valid = is_valid_output(text)
        has_dec = has_decision(text)
        decision = extract_decision(text)
        
        print(f"   Retry {retries} validation results:")
        print(f"     Valid format: {format_valid}")
        print(f"     Has decision: {has_dec}")
        print(f"      Decision: {decision}")
        
        # Save retry attempt
        if attempt_folder:
            attempt_file = os.path.join(attempt_folder, f"attempt_{retries + 1}_retry.txt")
            with open(attempt_file, 'w', encoding='utf-8') as f:
                f.write(f"PROMPT:\n{retry_prompt}\n\n")
                f.write(f"RESPONSE:\n{text}\n\n")
                f.write(f"VALIDATION:\n")
                f.write(f"  Valid format: {format_valid}\n")
                f.write(f"  Has decision: {has_dec}\n")
                f.write(f"  Decision: {decision}\n")
            print(f"  💾 Saved attempt {retries + 1} to: {attempt_file}")
        
        if format_valid and has_dec:
            print(f"   SUCCESS on retry {retries}!")
            return (text.strip(), True, retries)

    # Still invalid after retries
    print(f"   All {max_retries} retries failed, will use fallback")
    return (text.strip(), False, retries)

def deterministic_fallback_from_log(filtered_log: str) -> str:
    """
    Very conservative fallback that always makes a clear decision:
    - If we see any terminal 2xx on key endpoints AND no obvious started-but-unfinished goal,
      we call Conversion; else Drop-Off.
    """
    # Simple signals (tweak for your app)
    success_signals = re.findall(r'status_code["\']?\s*:\s*2\d\d|→\s*200', filtered_log)
    started_add_item = re.search(r'Add Item|/api/items|items', filtered_log, re.IGNORECASE)
    terminal_add_item = re.search(r'POST\s+/api/items.*?(200|201)', filtered_log, re.IGNORECASE)

    if started_add_item and not terminal_add_item:
        tag = "Drop-Off"
        reason = '"Add Item" started without terminal success.'
    elif success_signals:
        tag = "Conversion"
        reason = 'Observed terminal backend success on a goal endpoint.'
    else:
        tag = "Drop-Off"
        reason = 'No business goal reached terminal success.'

    # Ensure we always have a clear decision
    if tag not in ["Conversion", "Drop-Off"]:
        tag = "Drop-Off"
        reason = 'Unable to determine outcome - defaulting to Drop-Off.'

    # Minimal steps (best-effort)
    return f"""Tag: {tag} [{reason}]
1) Parsed backend/frontend events
2) Applied deterministic rules
3) Emitted conservative label
""".strip()

def classify_session(filtered_log: str,
                     endpoint_map: str = "",
                     model_kwargs: Optional[dict] = None,
                     timeout: int = 600) -> str:
    """End-to-end classification for one log with validation and retry."""
    print(f"   Starting session classification...")
    print(f"   Log length: {len(filtered_log)} chars")
    
    model_kwargs = model_kwargs or {}
    base = ""
    prompt = build_prompt(base, filtered_log, endpoint_map)
    print(f"   Built prompt length: {len(prompt)} chars")
    
    attempt_folder = model_kwargs.pop('attempt_folder', None)
    out, valid, retries = classify_with_retries(prompt, timeout=timeout, attempt_folder=attempt_folder, original_log=filtered_log, **model_kwargs)

    if valid:
        print(f"   LLM SUCCESS after {retries} retries!")
        print(f"   Final output: {out[:200]}...")
        
        # Save final successful result
        if attempt_folder:
            final_file = os.path.join(attempt_folder, "final_success.txt")
            with open(final_file, 'w', encoding='utf-8') as f:
                f.write(f"FINAL SUCCESSFUL RESULT:\n")
                f.write(f"Retries used: {retries}\n")
                f.write(f"Valid: {valid}\n\n")
                f.write(f"RESPONSE:\n{out}\n")
            print(f"  💾 Saved final success to: {final_file}")
        
        return out

    # Fallback if still invalid
    print(f"    LLM FAILED after {retries} retries, using deterministic fallback...")
    fallback_result = deterministic_fallback_from_log(filtered_log)
    print(f"   Fallback result: {fallback_result[:200]}...")
    
    # Save fallback result
    if attempt_folder:
        fallback_file = os.path.join(attempt_folder, "final_fallback.txt")
        with open(fallback_file, 'w', encoding='utf-8') as f:
            f.write(f"FALLBACK RESULT:\n")
            f.write(f"Retries used: {retries}\n")
            f.write(f"Valid: {valid}\n\n")
            f.write(f"FALLBACK RESPONSE:\n{fallback_result}\n")
        print(f"  💾 Saved fallback to: {fallback_file}")
    
    return fallback_result

def read_file_content(file_path: Path) -> str:
    """Read file with multiple encoding attempts."""
    encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']
    
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    
    # If all encodings fail, read as binary and decode with errors='replace'
    with open(file_path, 'rb') as f:
        return f.read().decode('utf-8', errors='replace')

def process_file(input_file: Path, output_file: Path, model: str, 
                 temperature: float = 0.1, top_p: float = 0.2, 
                 max_tokens: int = 2000, max_retries: int = 2, 
                 timeout: int = 600) -> Dict[str, Any]:
    """Process a single file with validation and retry logic."""
    print(f"📁 Processing file: {input_file.name}")
    
    try:
        # Read input file
        print(f"   Reading input file...")
        content = read_file_content(input_file)
        print(f"   File content length: {len(content)} chars")
        
        # Create attempt folder for this file
        model_name_clean = model.replace(':', '-')
        attempt_folder = output_file.parent / f"{input_file.stem}_{model_name_clean}_attempts"
        attempt_folder.mkdir(parents=True, exist_ok=True)
        print(f"   📁 Created attempt folder: {attempt_folder.name}")
        
        # Classify with validation
        model_kwargs = {
            'model': model,
            'temperature': temperature,
            'top_p': top_p,
            'max_tokens': max_tokens,
            'attempt_folder': str(attempt_folder)
        }
        
        print(f"   Starting classification...")
        result = classify_session(content, model_kwargs=model_kwargs, timeout=timeout)
        
        # Validate final result
        final_format_valid = is_valid_output(result)
        final_has_decision = has_decision(result)
        final_decision = extract_decision(result)
        
        print(f"   Final validation:")
        print(f"     Valid format: {final_format_valid}")
        print(f"     Has decision: {final_has_decision}")
        print(f"      Decision: {final_decision}")
        
        # Write output file
        print(f"   Writing output file: {output_file.name}")
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"Original file: {input_file}\n")
            f.write(f"Processed on: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Model used: {model}\n")
            f.write("=" * 50 + "\n\n")
            f.write(result)
        
        print(f"   File processing completed successfully!")
        
        return {
            "status": "success",
            "input_file": str(input_file),
            "output_file": str(output_file),
            "valid_format": final_format_valid,
            "has_decision": final_has_decision,
            "decision": final_decision
        }
        
    except Exception as e:
        print(f"   Error processing file: {e}")
        return {
            "status": "error",
            "input_file": str(input_file),
            "error": str(e)
        }

def main():
    parser = argparse.ArgumentParser(description="LLM Output Validator with Retry Logic")
    parser.add_argument("--input", "-i", required=True, help="Input file or directory")
    parser.add_argument("--output", "-o", required=True, help="Output file or directory")
    parser.add_argument("--model", "-m", default="llama3.3:70b", help="Model name")
    parser.add_argument("--temperature", type=float, default=0.1, help="Temperature")
    parser.add_argument("--top-p", type=float, default=0.2, help="Top-p")
    parser.add_argument("--max-tokens", type=int, default=2000, help="Max tokens")
    parser.add_argument("--max-retries", type=int, default=2, help="Max retries for invalid output")
    parser.add_argument("--base-url", default="http://localhost:11434", help="Ollama base URL")
    parser.add_argument("--test-mode", action="store_true", help="Process only first 3 files for testing")
    parser.add_argument("--timeout", type=int, default=600, help="Timeout for LLM requests in seconds")
    
    args = parser.parse_args()
    
    input_path = Path(args.input)
    output_path = Path(args.output)
    
    if input_path.is_file():
        # Single file processing
        print(f" SINGLE FILE MODE")
        print(f" Input: {input_path}")
        print(f" Output: {output_path}")
        
        if output_path.suffix:
            # Output is a file
            output_file = output_path
        else:
            # Output is a directory, create filename
            output_file = output_path / f"{input_path.stem}_validated.txt"
        
        print(f" Processing single file: {input_path.name}")
        result = process_file(input_path, output_file, args.model, 
                            args.temperature, args.top_p, args.max_tokens, args.max_retries, args.timeout)
        
        if result["status"] == "success":
            print(f" SUCCESS: {output_file}")
            print(f"    Valid format: {result['valid_format']}")
            print(f"    Has decision: {result['has_decision']}")
            print(f"     Decision: {result['decision']}")
        else:
            print(f" ERROR: {result['error']}")
    
    elif input_path.is_dir():
        # Directory processing
        print(f" DIRECTORY MODE")
        print(f" Input directory: {input_path}")
        print(f" Output directory: {output_path}")
        
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Find all supported files
        print(f" Scanning for supported files...")
        supported_extensions = ['.txt', '.json', '.log']
        files = []
        for ext in supported_extensions:
            files.extend(input_path.glob(f"*{ext}"))
        
        if not files:
            print(" No supported files found in input directory")
            return
        
        # Test mode: limit files
        if args.test_mode:
            files = files[:3]
            print(f" 🧪 TEST MODE: Processing only first 3 files")
        
        print(f" Found {len(files)} files to process")
        print(f" File types: {[f.suffix for f in files[:5]]}{'...' if len(files) > 5 else ''}")
        
        results = []
        start_time = time.time()
        
        for i, file_path in enumerate(files, 1):
            print(f"\n{'='*60}")
            print(f" Processing {i}/{len(files)}: {file_path.name}")
            print(f"{'='*60}")
            
            # Show estimated time remaining
            if i > 1:
                elapsed = time.time() - start_time
                avg_time_per_file = elapsed / (i - 1)
                remaining_files = len(files) - i + 1
                estimated_remaining = avg_time_per_file * remaining_files
                print(f" ⏱️  Elapsed: {elapsed:.1f}s | Est. remaining: {estimated_remaining:.1f}s")
            
            output_file = output_path / f"{file_path.stem}_validated.txt"
            
            # Process file sequentially (one at a time)
            print(f" 🔄 Processing file {i} of {len(files)}...")
            result = process_file(file_path, output_file, args.model,
                                args.temperature, args.top_p, args.max_tokens, args.max_retries, args.timeout)
            results.append(result)
            
            # Wait for this file to complete before moving to next
            print(f" ✅ File {i} processing completed")
            
            if result["status"] == "success":
                decision_info = f"decision: {result.get('decision', 'None')}" if result.get('has_decision') else "no decision"
                print(f"   ✅ {output_file.name} (valid: {result['valid_format']}, {decision_info})")
            else:
                print(f"   ❌ Error: {result['error']}")
            
            # Show progress summary
            successful = len([r for r in results if r["status"] == "success"])
            print(f" 📊 Progress: {successful}/{i} successful ({successful/i*100:.1f}%)")
            
            # Add small delay between files to ensure proper sequencing
            if i < len(files):
                print(f" ⏳ Waiting 2 seconds before next file...")
                time.sleep(2)
        
        # Save summary
        summary_file = output_path / "validation_summary.json"
        successful_results = [r for r in results if r["status"] == "success"]
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump({
                "total_files": len(files),
                "successful": len(successful_results),
                "errors": len([r for r in results if r["status"] == "error"]),
                "valid_formats": len([r for r in successful_results if r.get("valid_format", False)]),
                "has_decisions": len([r for r in successful_results if r.get("has_decision", False)]),
                "conversions": len([r for r in successful_results if r.get("decision") == "Conversion"]),
                "drop_offs": len([r for r in successful_results if r.get("decision") == "Drop-Off"]),
                "results": results
            }, f, indent=2)
        
        print(f"\nSummary saved to: {summary_file}")
    
    else:
        print(f"Error: Input path '{input_path}' does not exist")
        return 1

if __name__ == "__main__":
    sys.exit(main())
