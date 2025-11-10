#!/usr/bin/env python3
"""
File LLM Automation Tool
Automatically processes files through LLM models and saves results.
"""

import os
import json
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
import argparse
from datetime import datetime

# LLM Integration
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

class LLMProcessor:
    """Handles different LLM model integrations"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.openai_client = None
        self.anthropic_client = None
        
        # Initialize clients based on available APIs
        if OPENAI_AVAILABLE and config.get('openai_api_key'):
            self.openai_client = openai.OpenAI(api_key=config['openai_api_key'])
        
        if ANTHROPIC_AVAILABLE and config.get('anthropic_api_key'):
            self.anthropic_client = Anthropic(api_key=config['anthropic_api_key'])
    
    def process_with_llm(self, content: str, prompt: str, model: str) -> str:
        """Process content with specified LLM model"""
        try:
            if model.startswith('gpt') and self.openai_client:
                return self._process_openai(content, prompt, model)
            elif model.startswith('claude') and self.anthropic_client:
                return self._process_anthropic(content, prompt, model)
            elif model.startswith('local:') and REQUESTS_AVAILABLE:
                return self._process_local(content, prompt, model)
            else:
                return f"Error: Model {model} not supported or API key not configured"
        except Exception as e:
            return f"Error processing with {model}: {str(e)}"
    
    def _process_openai(self, content: str, prompt: str, model: str) -> str:
        """Process with OpenAI models"""
        full_prompt = f"{prompt}\n\nContent to process:\n{content}"
        
        response = self.openai_client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": full_prompt}],
            max_tokens=self.config.get('max_tokens', 2000),
            temperature=self.config.get('temperature', 0.7)
        )
        
        return response.choices[0].message.content
    
    def _process_anthropic(self, content: str, prompt: str, model: str) -> str:
        """Process with Anthropic models"""
        full_prompt = f"{prompt}\n\nContent to process:\n{content}"
        
        response = self.anthropic_client.messages.create(
            model=model,
            max_tokens=self.config.get('max_tokens', 2000),
            temperature=self.config.get('temperature', 0.7),
            messages=[{"role": "user", "content": full_prompt}]
        )
        
        return response.content[0].text
    
    def _process_local(self, content: str, prompt: str, model: str) -> str:
        """Process with local LLM (Ollama)"""
        # Extract model name from "local:modelname" format
        local_model = model.replace('local:', '')
        full_prompt = f"{prompt}\n\nContent to process:\n{content}"
        
        # Ollama API endpoint
        url = "http://localhost:11434/api/generate"
        
        payload = {
            "model": local_model,
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "temperature": self.config.get('temperature', 0.7),
                "num_predict": self.config.get('max_tokens', 2000)
            }
        }
        
        try:
            response = requests.post(url, json=payload, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            return result.get('response', 'No response from local model')
            
        except requests.exceptions.ConnectionError:
            return "Error: Cannot connect to local LLM at localhost:11434. Is Ollama running?"
        except requests.exceptions.Timeout:
            return "Error: Local LLM request timed out"
        except Exception as e:
            return f"Error with local LLM: {str(e)}"

class FileProcessor:
    """Handles file iteration and processing"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.llm_processor = LLMProcessor(config)
        self.processed_count = 0
        self.error_count = 0
    
    def get_files_to_process(self, directory: str, extensions: List[str]) -> List[Path]:
        """Get all files matching the specified extensions"""
        files = []
        directory_path = Path(directory)
        
        if not directory_path.exists():
            print(f"Error: Directory {directory} does not exist")
            return files
        
        for ext in extensions:
            pattern = f"**/*{ext}" if not ext.startswith('.') else f"**/*{ext}"
            files.extend(directory_path.glob(pattern))
        
        return sorted(files)
    
    def read_file_content(self, file_path: Path) -> str:
        """Read file content with proper encoding handling"""
        try:
            # Try different encodings
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
                
        except Exception as e:
            return f"Error reading file: {str(e)}"
    
    def save_result(self, file_path: Path, result: str, output_dir: str, naming_pattern: str, prompt: str) -> str:
        """Save LLM result to file"""
        try:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            # Generate output filename based on pattern
            if naming_pattern == "original_name":
                output_filename = f"{file_path.stem}_processed.txt"
            elif naming_pattern == "timestamp":
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_filename = f"processed_{timestamp}_{file_path.stem}.txt"
            elif naming_pattern == "sequential":
                output_filename = f"processed_{self.processed_count:04d}_{file_path.stem}.txt"
            else:
                # Custom pattern - replace placeholders
                output_filename = naming_pattern.replace("{original_name}", file_path.stem)
                output_filename = output_filename.replace("{timestamp}", datetime.now().strftime("%Y%m%d_%H%M%S"))
                output_filename = output_filename.replace("{counter}", str(self.processed_count))
                # Replace colons in model name for Windows compatibility
                model_name = self.config.get('model', 'unknown').replace(':', '-')
                output_filename = output_filename.replace("{model}", model_name)
                if not output_filename.endswith('.txt'):
                    output_filename += '.txt'
            
            output_file = output_path / output_filename
            
            # Save result with metadata
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"Original file: {file_path}\n")
                f.write(f"Processed on: {datetime.now().isoformat()}\n")
                f.write(f"Model used: {self.config.get('model', 'unknown')}\n")
                f.write(f"Prompt: {prompt}\n")
                f.write("=" * 50 + "\n\n")
                f.write(result)
            
            return str(output_file)
            
        except Exception as e:
            print(f"Error saving result for {file_path}: {str(e)}")
            return ""
    
    def process_files(self, directory: str, prompt: str) -> Dict[str, Any]:
        """Main method to process all files"""
        print(f"Starting file processing...")
        print(f"Directory: {directory}")
        print(f"Extensions: {self.config.get('file_extensions', [])}")
        print(f"Model: {self.config.get('model', 'unknown')}")
        print("-" * 50)
        
        files = self.get_files_to_process(directory, self.config.get('file_extensions', []))
        
        if not files:
            print("No files found to process")
            return {"processed": 0, "errors": 0, "files": []}
        
        print(f"Found {len(files)} files to process")
        
        results = []
        
        for i, file_path in enumerate(files, 1):
            print(f"Processing {i}/{len(files)}: {file_path.name}")
            
            try:
                # Read file content
                content = self.read_file_content(file_path)
                
                if content.startswith("Error reading file"):
                    print(f"  [ERROR] {content}")
                    self.error_count += 1
                    continue
                
                # Process with LLM
                result = self.llm_processor.process_with_llm(
                    content, 
                    prompt, 
                    self.config.get('model', 'gpt-3.5-turbo')
                )
                
                if result.startswith("Error"):
                    print(f"  [ERROR] {result}")
                    self.error_count += 1
                    continue
                
                # Save result
                output_file = self.save_result(
                    file_path, 
                    result, 
                    self.config.get('output_directory', './output'),
                    self.config.get('naming_pattern', 'original_name'),
                    prompt
                )
                
                if output_file:
                    print(f"  [OK] Saved to: {output_file}")
                    self.processed_count += 1
                    results.append({
                        "original_file": str(file_path),
                        "output_file": output_file,
                        "status": "success"
                    })
                else:
                    print(f"  [ERROR] Failed to save result")
                    self.error_count += 1
                
                # Add delay between requests to avoid rate limiting
                if i < len(files):
                    time.sleep(self.config.get('delay_between_files', 1))
                
            except Exception as e:
                print(f"  [ERROR] Error processing {file_path.name}: {str(e)}")
                self.error_count += 1
        
        print("-" * 50)
        print(f"Processing complete!")
        print(f"Successfully processed: {self.processed_count}")
        print(f"Errors: {self.error_count}")
        
        return {
            "processed": self.processed_count,
            "errors": self.error_count,
            "files": results
        }

def load_config(config_file: str) -> Dict[str, Any]:
    """Load configuration from JSON file"""
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Config file {config_file} not found. Using default configuration.")
        return get_default_config()
    except Exception as e:
        print(f"Error loading config: {str(e)}. Using default configuration.")
        return get_default_config()

def get_default_config() -> Dict[str, Any]:
    """Get default configuration"""
    return {
        "file_extensions": [".txt", ".py", ".js", ".md"],
        "output_directory": "./output",
        "naming_pattern": "original_name",
        "model": "gpt-3.5-turbo",
        "max_tokens": 2000,
        "temperature": 0.7,
        "delay_between_files": 1,
        "openai_api_key": "",
        "anthropic_api_key": ""
    }

def create_sample_config():
    """Create a sample configuration file"""
    config = get_default_config()
    config["openai_api_key"] = "your-openai-api-key-here"
    config["anthropic_api_key"] = "your-anthropic-api-key-here"
    
    with open("config.json", 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)
    
    print("Created sample config.json file. Please edit it with your API keys and preferences.")

def main():
    parser = argparse.ArgumentParser(description="Automate file processing with LLM")
    parser.add_argument("--directory", "-d", help="Directory containing files to process")
    parser.add_argument("--prompt", "-p", help="Prompt to send to LLM")
    parser.add_argument("--config", "-c", default="config.json", help="Configuration file path")
    parser.add_argument("--create-config", action="store_true", help="Create sample configuration file")
    
    args = parser.parse_args()
    
    if args.create_config:
        create_sample_config()
        return
    
    # Check if required arguments are provided when not creating config
    if not args.directory or not args.prompt:
        print("Error: --directory and --prompt are required when not using --create-config")
        parser.print_help()
        return
    
    # Load configuration
    config = load_config(args.config)
    
    # Validate required settings
    model = config.get('model', '')
    is_local_model = model.startswith('local:')
    
    if not is_local_model and not config.get('openai_api_key') and not config.get('anthropic_api_key'):
        print("Error: No API keys configured. Please set openai_api_key or anthropic_api_key in config.json")
        print("Or use a local model by setting model to 'local:MODEL_NAME'")
        print("Run with --create-config to create a sample configuration file.")
        return
    
    # Create processor and run
    processor = FileProcessor(config)
    results = processor.process_files(args.directory, args.prompt)
    
    # Save processing summary
    summary_file = Path(config.get('output_directory', './output')) / "processing_summary.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    
    print(f"Processing summary saved to: {summary_file}")

if __name__ == "__main__":
    main()
